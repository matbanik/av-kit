import { useQuery } from '@tanstack/react-query'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'

import { HelpCard } from '../../components/help/HelpCard'
import { BulkActionBar } from '../../components/queue/BulkActionBar'
import { BulkResultToast } from '../../components/queue/BulkResultToast'
import { QueueHeaderRow } from '../../components/queue/QueueHeaderRow'
import { QueueList } from '../../components/queue/QueueList'
import { recordShellIpc } from '../../lib/queue/shell-ipc-ledger'
import type { QueueCardJob } from '../../components/queue/QueueCard'
import { Button } from '../../components/ui/Button'
import { ConfirmModal } from '../../components/ui/ConfirmModal'
import { Disclosure } from '../../components/ui/Disclosure'
import { PathRow } from '../../components/ui/PathRow'
import { SegmentedControl } from '../../components/ui/SegmentedControl'
import { SelectInput } from '../../components/ui/SelectInput'
import { StatusChip } from '../../components/ui/StatusChip'
import { Tooltip } from '../../components/ui/Tooltip'
import { ApiError, apiFetch } from '../../lib/api'
import {
  acquireQueueReorder,
  type ReorderQueueKey,
} from '../../lib/queue/reorder-single-flight'
import { CLEAR_FINISHED_STATUSES } from '../../lib/queue/run-bulk'
import { useQueueBulk } from '../../lib/queue/use-queue-bulk'
import { logRenderer } from '../../lib/renderer-log'
import { queryClient } from '../../lib/query-client'
import { usePublishCommandState } from '../../registry/command-state'
import { ariaKeyshortcuts } from '../../registry/shortcuts'
import { createConversionBody } from './convert-body'
import {
  CONVERT_REQUEUEABLE_STATUSES,
  buildReorderBody,
  controlEnabled,
  convertMetaSegments,
  JOB_STATUSES,
  openTarget,
  processorLabel,
  queueSummary,
  type ConversionKindWire,
  type ProcessorState,
} from './convert-controls'
import {
  cancelConversion,
  clearConversions,
  CONVERT_BROWSE_EVENT,
  CONVERT_CONFIRM_EVENT,
  pauseConversion,
  postConversionCreate,
  removeConversion,
  removeConversionOnly,
  reorderConversion,
  reorderConversionOnly,
  reorderConversionToIndex,
  resetConversion,
  resetConversionOnly,
  resumeConversion,
  setConvertFormSnapshot,
  startConversion,
  type ConvertConfirmRequest,
  type ReorderDirection,
} from './convert-commands'
import { CONVERT_DIALOG_FILTERS } from './convert-filters'
import { CONVERT_HELP_SECTIONS } from './convert-help-content'
import { gpuChipLabel } from './convert-gpu'
import {
  AUDIO_MODE_WIRES,
  CQ_MAX,
  CQ_MIN,
  CQ_STEP,
  GPU_PREF_WIRES,
  PRESET_DEFAULT,
  PRESET_LABELS,
  PRESET_WIRES,
  SCALE_HEIGHTS,
  presetAdvanced,
  type AudioModeWire,
  type GpuPrefWire,
  type PresetWire,
  type ScaleHeight,
} from './convert-presets'
import { parseConvertTime } from './convert-time'
import { useConverterSettings } from './useConverterSettings'
import { QUERY_KEY, useConversionQueue } from './useConversionQueue'

const CONVERT_ERROR_EVENT = 'av-kit:convert:error'


const PRESET_TESTIDS: Record<PresetWire, string> = {
  archival: 'convert-preset-archival',
  high_quality: 'convert-preset-high_quality',
  balanced: 'convert-preset-balanced',
  sharing: 'convert-preset-sharing',
  mobile: 'convert-preset-mobile',
}

type GpuOut = {
  nvidia_nvenc: boolean
  amd_amf: boolean
  intel_qsv: boolean
}

type DepsOut = {
  ffmpeg: { available: boolean }
}

function asProcessor(state: string | undefined): ProcessorState {
  if (state === 'Processing' || state === 'Paused') {
    return state
  }
  return 'Idle'
}

type ConvertConfirm =
  | { kind: 'remove'; id: string }
  | { kind: 'clear' }
  | { kind: 'cancel' }
  | { kind: 'bulk-remove' }
  | null

/*
  One place decides what the confirm dialog says, so the three kinds cannot drift
  apart in the JSX. The bulk copy reuses the hook's already-pluralised label
  (USER_LOCKS lock 2: the button names the verb AND the count, never a bare
  "Confirm") instead of re-deriving the noun here.
*/
function confirmCopy(
  confirm: ConvertConfirm,
  bulkRemoveLabel: string,
): { title: string; description: string; confirmLabel: string } {
  if (confirm?.kind === 'clear') {
    return {
      title: 'Clear the whole queue?',
      description: 'Every queued conversion is dropped. Files stay on disk.',
      confirmLabel: 'Clear all',
    }
  }
  if (confirm?.kind === 'cancel') {
    return {
      title: 'Cancel active conversions?',
      description: 'Work in progress stops. Files already on disk stay there.',
      confirmLabel: 'Cancel conversions',
    }
  }
  if (confirm?.kind === 'bulk-remove') {
    return {
      title: `${bulkRemoveLabel}?`,
      description: 'The queue records are deleted. Files stay on disk.',
      confirmLabel: bulkRemoveLabel,
    }
  }
  return {
    title: 'Remove from queue?',
    description: 'The queue record is deleted. Files stay on disk.',
    confirmLabel: 'Remove',
  }
}

function asScale(value: number): ScaleHeight {
  if (value === 1080 || value === 720 || value === 480) {
    return value
  }
  return 0
}

/**
 * The single-flight key every reorder path on this page shares
 * (`REORDER_SINGLE_FLIGHT_RULE`). One constant, so the kebab, Alt+Arrow, the
 * drag handle, the bulk fold and the gate the handle reads back cannot drift
 * onto two different keys and stop excluding each other.
 */
const CONVERT_QUEUE_KEY: ReorderQueueKey = 'convert'

export function ConvertPage() {
  const queue = useConversionQueue()
  const converter = useConverterSettings()
  const gpuQuery = useQuery({
    queryKey: ['conversions', 'gpu'],
    queryFn: async () => apiFetch<GpuOut>('/conversions/gpu'),
  })
  const depsQuery = useQuery({
    queryKey: ['health', 'dependencies'],
    queryFn: async () => apiFetch<DepsOut>('/health/dependencies'),
  })
  const [kind, setKind] = useState<ConversionKindWire>('compress')
  const [staging, setStaging] = useState<string[]>([])
  const [preset, setPreset] = useState<PresetWire>(PRESET_DEFAULT)
  const [advancedOpen, setAdvancedOpen] = useState(false)
  const presetTouched = useRef(false)
  const defaults = presetAdvanced(PRESET_DEFAULT)
  const [cq, setCq] = useState(defaults.cq)
  const [scaleHeight, setScaleHeight] = useState<ScaleHeight>(defaults.scale_height)
  const [audioMode, setAudioMode] = useState<AudioModeWire>(defaults.audio_mode)
  const [gpuPreference, setGpuPreference] = useState<GpuPrefWire>('auto')
  const [cutIn, setCutIn] = useState('00:00:00.000')
  const [cutOut, setCutOut] = useState('00:00:00.000')
  const [copyMode, setCopyMode] = useState<'fast_copy' | 'reencode'>('fast_copy')
  const [streamMode, setStreamMode] = useState<'first' | 'all'>('first')
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [adding, setAdding] = useState(false)
  const [busy, setBusy] = useState(false)
  // The confirm the queue is currently asking for. `remove` carries the id it
  // will delete: the card kebab acts on the row the user opened it from, which
  // is not necessarily the selected row, so the id cannot be read back off
  // `selectedId` at confirm time (USER_LOCKS lock 2).
  const [confirm, setConfirm] = useState<ConvertConfirm>(null)

  const items = useMemo(() => queue.data?.items ?? [], [queue.data?.items])
  const processorState = asProcessor(queue.data?.processor.state)
  const summary = useMemo(() => queueSummary(items), [items])

  /*
    Every bulk control on this page — the header checkbox, the five
    BULK_BAR_ACTIONS and `Clear finished` — is driven from this one hook, which
    the downloader shares. The endpoints differ per page; the model does not,
    and BULK_CONTROL_E2E_OBLIGATION requires both pages to behave identically.
  */
  const bulk = useQueueBulk({
    items,
    queueKey: CONVERT_QUEUE_KEY,
    requeueableStatuses: CONVERT_REQUEUEABLE_STATUSES,
    run: (action) => {
      void run(action)
    },
    retry: resetConversionOnly,
    remove: removeConversionOnly,
    reorder: reorderConversionOnly,
    buildBody: buildReorderBody,
    refetch: async () => queue.refetch(),
  })
  const label = processorLabel(processorState)
  const ffmpegAvailable = depsQuery.data?.ffmpeg?.available === true
  const ctx = { items, selectedId, processorState, ffmpegAvailable }
  const chip = gpuChipLabel({
    ffmpegAvailable: depsQuery.data?.ffmpeg?.available,
    gpu: gpuQuery.data,
  })

  useEffect(() => {
    const onError = (event: Event) => {
      const detail = (event as CustomEvent<string>).detail
      setError(detail)
    }
    window.addEventListener(CONVERT_ERROR_EVENT, onError)
    return () => {
      window.removeEventListener(CONVERT_ERROR_EVENT, onError)
    }
  }, [])

  // CONFIRM_ROUTE: the palette's clear and cancel open this page's confirm.
  useEffect(() => {
    const onConfirmRequest = (event: Event) => {
      setConfirm({ kind: (event as CustomEvent<ConvertConfirmRequest>).detail.kind })
    }
    window.addEventListener(CONVERT_CONFIRM_EVENT, onConfirmRequest)
    return () => {
      window.removeEventListener(CONVERT_CONFIRM_EVENT, onConfirmRequest)
    }
  }, [])

  useEffect(() => {
    if (kind !== 'compress') {
      setAdvancedOpen(false)
    }
  }, [kind])

  useEffect(() => {
    if (presetTouched.current || !converter.ready) {
      return
    }
    const next = converter.form.default_preset
    setPreset(next)
    const advanced = presetAdvanced(next)
    setCq(advanced.cq)
    setScaleHeight(advanced.scale_height)
    setAudioMode(advanced.audio_mode)
    setGpuPreference(converter.form.gpu_preference)
  }, [converter.ready, converter.form.default_preset, converter.form.gpu_preference])

  useEffect(() => {
    if (selectedId !== null && !items.some((item) => item.id === selectedId)) {
      setSelectedId(items[0]?.id ?? null)
    }
  }, [items, selectedId])

  useEffect(() => {
    setConvertFormSnapshot({
      kind,
      paths: staging,
      preset,
      cq,
      scale_height: scaleHeight,
      audio_mode: audioMode,
      gpu_preference: gpuPreference,
      cutIn,
      cutOut,
      copy_mode: copyMode,
      stream_mode: streamMode,
      ffmpegAvailable,
    })
  }, [
    kind,
    staging,
    preset,
    cq,
    scaleHeight,
    audioMode,
    gpuPreference,
    cutIn,
    cutOut,
    copyMode,
    streamMode,
    ffmpegAvailable,
  ])

  function selectPreset(next: PresetWire): void {
    presetTouched.current = true
    setPreset(next)
    const advanced = presetAdvanced(next)
    setCq(advanced.cq)
    setScaleHeight(advanced.scale_height)
    setAudioMode(advanced.audio_mode)
  }

  function buildCreateInput(): unknown {
    if (kind === 'compress') {
      const catalog = presetAdvanced(preset)
      const body: Record<string, unknown> = { paths: staging, kind: 'compress', preset }
      if (cq !== catalog.cq) {
        body.cq = cq
      }
      if (scaleHeight !== catalog.scale_height) {
        body.scale_height = scaleHeight
      }
      if (audioMode !== catalog.audio_mode) {
        body.audio_mode = audioMode
      }
      if (gpuPreference !== 'auto') {
        body.gpu_preference = gpuPreference
      }
      return body
    }
    if (kind === 'cut') {
      return {
        paths: staging,
        kind: 'cut',
        in_ms: parseConvertTime(cutIn),
        out_ms: parseConvertTime(cutOut),
        copy_mode: copyMode,
      }
    }
    return { paths: staging, kind: 'extract', stream_mode: streamMode }
  }

  function addFromForm(): void {
    if (staging.length < 1) {
      setError('Add at least one file')
      return
    }
    if (kind === 'cut') {
      const inMs = parseConvertTime(cutIn)
      const outMs = parseConvertTime(cutOut)
      if (inMs === null || outMs === null || outMs <= inMs) {
        setError('Cut Out must be after In (HH:MM:SS.mmm or seconds)')
        return
      }
    }
    const input = buildCreateInput()
    if (createConversionBody(input) === null) {
      setError('Invalid conversion options')
      return
    }
    setError(null)
    setAdding(true)
    logRenderer('INFO', `convert add: posting ${staging.length} path(s)`)
    void postConversionCreate(input)
      .then((out) => {
        if (out.items.length > 0) {
          setStaging([])
          logRenderer('INFO', `convert add: queued ${out.items.length} job(s)`)
        }
      })
      .catch((caught: unknown) => {
        const message =
          caught instanceof ApiError ? caught.message : caught instanceof Error ? caught.message : String(caught)
        setError(message)
        logRenderer('ERROR', `convert add: ${message}`)
        void queryClient.invalidateQueries({ queryKey: QUERY_KEY })
      })
      .finally(() => {
        setAdding(false)
      })
  }

  async function run(action: () => Promise<unknown>): Promise<void> {
    setBusy(true)
    setError(null)
    try {
      await action()
    } catch (caught) {
      const message =
        caught instanceof ApiError ? caught.message : caught instanceof Error ? caught.message : String(caught)
      setError(message)
    } finally {
      setBusy(false)
    }
  }

  /*
    Reorder acts on the id the control belongs to. The retired toolbar moved
    "the selected row"; a card's kebab and its Alt+Arrow shortcut move THAT
    card, so the id travels with the call. The wire body stays the complete
    permutation `reorderConversion` builds (REORDER_WIRE_CONTRACT) — the API
    422s a `{ id, direction }` body.
  */
  /*
    Every permutation mutation on this page — kebab, Alt+Arrow, drag, bulk fold
    — goes through this one gate (`REORDER_SINGLE_FLIGHT_RULE`). Each of them
    computes its new order from `items`, the order react-query currently holds,
    so two of them in flight at once would both build a body from the SAME
    pre-move array and the second PUT would silently undo the first. The acquire
    is synchronous and happens before `items` is read; the release is in a
    `finally`, so a rejected PUT cannot strand the gate and leave every reorder
    control disabled for the rest of the session.
  */
  function withReorderGate(action: () => Promise<unknown>): void {
    const release = acquireQueueReorder(CONVERT_QUEUE_KEY)
    if (release === null) {
      return
    }
    void run(async () => {
      try {
        await action()
      } finally {
        release()
      }
    })
  }

  function reorder(id: string, direction: ReorderDirection): void {
    if (items.length < 1) {
      return
    }
    withReorderGate(async () => {
      await reorderConversion(
        items.map((item) => item.id),
        id,
        direction,
      )
    })
  }

  /*
    The drag path differs from the kebab path only in how the target is named:
    dnd-kit resolves a FINAL index, not a direction (`MOVE_TO_INDEX_CONTRACT`).
    It deliberately does NOT reorder the list optimistically — the rendered
    order stays the server's until the reconcile lands, so a rejected PUT leaves
    the row exactly where it was and surfaces through the page's existing error
    banner rather than needing a rollback (AC-49.22).
  */
  function reorderToIndex(id: string, targetIndex: number): void {
    if (items.length < 1) {
      return
    }
    withReorderGate(async () => {
      await reorderConversionToIndex(
        items.map((item) => item.id),
        id,
        targetIndex,
      )
    })
  }

  /** Open the host's file picker and stage whatever it returns. */
  const browseForFiles = useCallback((): void => {
    void window.api
      .showFilesDialog(
        CONVERT_DIALOG_FILTERS.map((row) => ({
          name: row.name,
          extensions: [...row.extensions],
        })),
      )
      .then((picked) => {
        if (picked.length > 0) {
          setStaging((current) => [...current, ...picked])
        }
      })
  }, [])

  // CONVERT_BROWSE: the palette's Browse files opens the same picker.
  useEffect(() => {
    window.addEventListener(CONVERT_BROWSE_EVENT, browseForFiles)
    return () => {
      window.removeEventListener(CONVERT_BROWSE_EVENT, browseForFiles)
    }
  }, [browseForFiles])

  /** Stage files released onto the queue itself, via the same path as a browse. */
  function stageDroppedFiles(files: readonly File[]): void {
    const paths = files
      .map((file) => window.api.getPathForFile(file))
      .filter((path) => path.length > 0)
    if (paths.length > 0) {
      setStaging((current) => [...current, ...paths])
    }
  }

  /** Resolve the on-disk target for a row's open-file / open-folder actions. */
  function targetFor(id: string): string | null {
    return openTarget(items.find((item) => item.id === id))
  }

  /*
    QueueCard's own shape, built from the conversion wire row. `sourceUrl` is
    the input path: before an output exists, "copy location" copies where the
    job came FROM, which is the only location the row has.
  */
  const cards: QueueCardJob[] = items.map((item) => ({
    id: item.id,
    position: item.queue_position,
    status: item.status,
    title: item.display_name,
    progress: item.progress,
    fileSize: item.file_size,
    outputPath: item.output_path,
    sourceUrl: item.input_path,
  }))

  /*
    Per-row meta for the shared card. `QueueCardJob` deliberately does not carry
    the converter's kind/preset/cut/stream fields — they are this page's, not
    the queue package's — so the resolver goes back to the wire row by id.
  */
  const metaSegmentsFor = (job: QueueCardJob): readonly string[] => {
    const row = items.find((item) => item.id === job.id)
    if (row === undefined) {
      return []
    }
    return convertMetaSegments({
      kind: row.kind,
      preset_id: row.preset_id,
      gpu_encoder: row.gpu_encoder,
      in_ms: row.in_ms,
      out_ms: row.out_ms,
      stream_index: row.stream_index,
      speed: row.speed,
      eta: row.eta,
    })
  }

  const paused = processorState === 'Paused'
  const hasFinished = items.some((item) => CLEAR_FINISHED_STATUSES.includes(item.status))

  // PAGE_STATE: the same expressions the queue toolbar and cancel control use.
  usePublishCommandState('/convert', {
    'convert:start': controlEnabled('start', ctx) && !busy,
    'convert:pause': !paused && controlEnabled('pause', ctx) && !busy,
    'convert:resume': paused && controlEnabled('resume', ctx) && !busy,
    'convert:cancel': controlEnabled('cancel', ctx) && !busy,
    'convert:clear': controlEnabled('clear-all', ctx) && !busy,
  })

  return (
    <section data-testid="convert-page" className="flex h-full min-h-0 flex-col gap-4 p-4">
      {/*
        QUEUE_SCROLL_CONTAINER_RULE. This column is oversubscribed at the app's
        own 1280x800 default window, so one pane has to yield the deficit. It is
        this one, not the queue: a queue shorter than two rows puts every
        keyboard target in the bottom half of its own scroller, and there
        KeyboardSensor scrolls instead of moving the row.
      */}
      <div className="flex min-h-0 flex-col gap-4 overflow-auto">
      <HelpCard feature="converter" tabKey="main" sections={CONVERT_HELP_SECTIONS} />

      <div data-testid="convert-add-panel" className="flex w-full max-w-[var(--layout-page-max-width)] flex-col gap-3">

      <div className="flex flex-wrap items-center gap-3">
        <SegmentedControl
          name="Task"
          value={kind}
          options={([
            ['compress', 'Compress'], ['cut', 'Cut'], ['extract', 'Extract'],
          ] as const).map(([value, label]) => ({
            id: `convert-task-${value}`,
            testId: `convert-task-${value}`,
            value,
            label,
          }))}
          onValueChange={(value) => {
            if (value === 'compress' || value === 'cut' || value === 'extract') setKind(value)
          }}
        />
        <StatusChip label={chip} tone="info" testId="convert-gpu-chip" />
        <Button
          data-testid="convert-gpu-refresh"
          variant="secondary"
          size="sm"
          onClick={() => {
            void run(async () => {
              await apiFetch('/conversions/gpu/refresh', { method: 'POST' })
              await queryClient.invalidateQueries({ queryKey: ['conversions', 'gpu'] })
            })
          }}
        >
          Refresh GPU
        </Button>
      </div>

      <div className="flex flex-wrap items-center gap-2">
      <div
        data-testid="convert-dropzone"
        tabIndex={0}
        className="flex min-w-64 flex-1 flex-wrap items-center gap-3 rounded-md border border-dashed border-border p-3"
        onDragOver={(event) => {
          event.preventDefault()
        }}
        onDrop={(event) => {
          event.preventDefault()
          stageDroppedFiles(Array.from(event.dataTransfer.files))
        }}
      >
        <p>Drop video or audio files here</p>
        <Button
          data-testid="convert-browse"
          variant="secondary"
          size="md"
          title="Browse (Ctrl+O)"
          aria-keyshortcuts={ariaKeyshortcuts('Ctrl+O')}
          onClick={browseForFiles}
        >
          Browse…
        </Button>
      </div>
      <Button
        data-testid="convert-add"
        variant="primary"
        size="md"
        type="button"
        title="Add (Ctrl+Enter)"
        aria-keyshortcuts={ariaKeyshortcuts('Ctrl+Enter')}
        loading={adding}
        disabled={!controlEnabled('add', ctx) || busy}
        onClick={addFromForm}
      >
        {staging.length > 0 ? `Add (${staging.length})` : 'Add'}
      </Button>
      </div>
      {staging.length > 0 ? (
        <ul className="flex flex-wrap gap-2" aria-label="Staged files">
          {staging.map((path, index) => (
            <li key={`${path}-${index}`} className="inline-flex items-center gap-1 rounded-[var(--radius-full)] border border-border px-2 py-1 text-xs">
              <span>{path}</span>
              <Tooltip id="convert-staged-remove" label={`Remove staged file ${path}`}>
                <button
                  type="button"
                  data-testid="convert-staged-remove"
                  aria-label={`Remove staged file ${path}`}
                  className="rounded-[var(--radius-full)] px-1 text-fg-muted hover:text-fg"
                  onClick={() => setStaging((current) => current.filter((_, position) => position !== index))}
                >
                  ×
                </button>
              </Tooltip>
            </li>
          ))}
        </ul>
      ) : null}

      <div className="flex flex-col gap-2">
        {kind === 'compress' ? (
          <>
            <SegmentedControl
              name="Preset"
              value={preset}
              options={PRESET_WIRES.map((value) => ({
                id: `convert-preset-${value}`,
                testId: PRESET_TESTIDS[value],
                value,
                label: PRESET_LABELS[value],
              }))}
              onValueChange={(value) => {
                const next = PRESET_WIRES.find((wire) => wire === value)
                if (next !== undefined) selectPreset(next)
              }}
            />
            <Disclosure
              id="convert-overrides"
              title="Advanced"
              testId="convert-advanced"
              open={advancedOpen}
              onOpenChange={setAdvancedOpen}
            >
              <div className="flex flex-wrap gap-3 rounded-md border border-border p-3">
                <label className="flex flex-col gap-1 text-sm">
                  <span>CQ</span>
                  <input
                    type="range"
                    min={CQ_MIN}
                    max={CQ_MAX}
                    step={CQ_STEP}
                    value={cq}
                    onChange={(event) => setCq(Number(event.target.value))}
                  />
                </label>
                <SelectInput
                  label="Scale"
                  value={String(scaleHeight)}
                  options={SCALE_HEIGHTS.map((height) => ({
                    value: String(height),
                    label: height === 0 ? 'Source' : `${height}p`,
                  }))}
                  onChange={(event) => setScaleHeight(asScale(Number(event.target.value)))}
                />
                <SelectInput
                  label="Audio"
                  value={audioMode}
                  options={AUDIO_MODE_WIRES.map((mode) => ({ value: mode, label: mode }))}
                  onChange={(event) => setAudioMode(event.target.value as AudioModeWire)}
                />
                <SelectInput
                  label="Encoder override"
                  value={gpuPreference}
                  options={GPU_PREF_WIRES.map((pref) => ({ value: pref, label: pref }))}
                  onChange={(event) => setGpuPreference(event.target.value as GpuPrefWire)}
                />
              </div>
            </Disclosure>
          </>
        ) : null}
      </div>

      {kind === 'cut' ? (
        <div className="flex flex-wrap gap-3">
          <label className="flex flex-col gap-1 text-sm">
            In
            <input
              data-testid="convert-cut-in"
              className="rounded border border-border bg-bg px-2 py-1"
              value={cutIn}
              onChange={(event) => {
                setCutIn(event.target.value)
              }}
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            Out
            <input
              data-testid="convert-cut-out"
              className="rounded border border-border bg-bg px-2 py-1"
              value={cutOut}
              onChange={(event) => {
                setCutOut(event.target.value)
              }}
            />
          </label>
          <SegmentedControl
            name="Cut mode"
            value={copyMode}
            options={[
              { id: 'convert-copy-fast', testId: 'convert-copy-fast', value: 'fast_copy', label: 'Fast (copy)' },
              { id: 'convert-copy-reencode', testId: 'convert-copy-reencode', value: 'reencode', label: 'Accurate (re-encode)' },
            ]}
            onValueChange={(value) => {
              if (value === 'fast_copy' || value === 'reencode') setCopyMode(value)
            }}
          />
        </div>
      ) : (
        <>
          <input data-testid="convert-cut-in" hidden readOnly value={cutIn} />
          <input data-testid="convert-cut-out" hidden readOnly value={cutOut} />
        </>
      )}

      {kind === 'extract' ? (
        <SegmentedControl
          name="Extract streams"
          value={streamMode}
          options={[
            { id: 'convert-extract-first', testId: 'convert-extract-first', value: 'first', label: 'First audio stream' },
            { id: 'convert-extract-all', testId: 'convert-extract-all', value: 'all', label: 'All audio streams' },
          ]}
          onValueChange={(value) => {
            if (value === 'first' || value === 'all') setStreamMode(value)
          }}
        />
      ) : (
        <>
          <input type="radio" data-testid="convert-extract-first" hidden readOnly />
          <input type="radio" data-testid="convert-extract-all" hidden readOnly />
        </>
      )}

      <div className="flex flex-wrap items-center gap-3">
        <PathRow
          id="convert-output-dir"
          label="Output folder"
          inputTestId="convert-output-dir"
          browseTestId="convert-output-dir-browse"
          value={converter.form.output_dir}
          onChange={(value) => {
            converter.patchForm({ output_dir: value })
          }}
          onBrowse={() => {
            void (async () => {
              const chosen = await window.api.showDirectoryDialog()
              if (chosen === undefined) {
                return
              }
              converter.patchForm({ output_dir: chosen })
            })()
          }}
          className="min-w-[24rem] flex-1"
        />
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            data-testid="convert-skip-existing"
            checked={converter.form.skip_existing}
            onChange={(event) => {
              converter.patchForm({ skip_existing: event.target.checked })
            }}
          />
          Skip files that already exist
        </label>
        <Button
          data-testid="convert-page-save"
          variant={converter.isDirty ? 'primary' : 'ghost'}
          size="sm"
          className={converter.isDirty ? 'btn-save-dirty' : undefined}
          onClick={() => {
            void run(async () => {
              await converter.save()
            })
          }}
        >
          {converter.isDirty ? 'Save Changes •' : 'Save'}
        </Button>
      </div>

      {error ? (
        <p data-testid="error-banner" className="text-error" role="alert">
          {error}
        </p>
      ) : (
        <p data-testid="error-banner" hidden className="text-error" />
      )}
      </div>
      </div>

      {/*
        USER_LOCKS lock 1: the bar is STICKY ABOVE THE LIST, inside this queue
        region — never a floating viewport-bottom bar. The region also owns the
        Ctrl/Cmd+A chord, so select-all works from a focused card without taking
        the shortcut away from the form fields above.
      */}
      <div className="flex min-h-[20rem] flex-1 flex-col gap-2" data-testid="convert-queue-region" onKeyDown={bulk.onKeyDown}>
        <QueueHeaderRow
          total={cards.length}
          selectedCount={bulk.selection.count}
          onToggleAll={bulk.onToggleAll}
          selectionAriaLabel="Select all conversions"
          statuses={JOB_STATUSES}
          counts={summary}
          summaryTestId="convert-queue-summary"
          processorTestId="convert-processor"
          processorLabel={label}
          toolbar={{
            label: 'Conversion queue actions',
            processorState,
            canStart: controlEnabled('start', ctx) && !busy,
            canPauseResume: (paused ? controlEnabled('resume', ctx) : controlEnabled('pause', ctx)) && !busy,
            canClearFinished: hasFinished && !busy,
            canClearAll: controlEnabled('clear-all', ctx) && !busy,
            onStart: () => { void run(startConversion) },
            onPauseResume: () => { void run(paused ? resumeConversion : pauseConversion) },
            onClearFinished: bulk.clearFinishedNow,
            onClearAll: () => { setConfirm({ kind: 'clear' }) },
          }}
        />
        <BulkActionBar
          selectedStatuses={bulk.selectedStatuses}
          requeueableStatuses={CONVERT_REQUEUEABLE_STATUSES}
          busy={busy}
          onRetry={bulk.retrySelected}
          onMoveTop={() => {
            bulk.moveSelected('top')
          }}
          onMoveBottom={() => {
            bulk.moveSelected('bottom')
          }}
          onRemove={() => {
            setConfirm({ kind: 'bulk-remove' })
          }}
          onClearSelection={bulk.selection.clear}
        />
        <BulkResultToast result={bulk.note} onDismiss={bulk.dismissNote} />
        {/*
          QUEUE_SCROLL_CONTAINER_RULE. overflow-auto lives on this wrapper, not
          on QueueList's listClasses: that node is `relative` and is the containing
          block for the file-drop overlay (absolute inset-0). Scrolling it would
          park the overlay in the overflow, and would also change the non-drag
          DOM DND_OPT_IN_RULE promises byte-for-byte.
        */}
        <div className="min-h-0 flex-1 overflow-auto">
        <QueueList
        testId="convert-queue"
        rowTestId="convert-queue-row"
        items={cards}
        queueKey={CONVERT_QUEUE_KEY}
        onMoveToIndex={reorderToIndex}
        inFlightId={queue.data?.processor.current_job_id ?? null}
        requeueableStatuses={CONVERT_REQUEUEABLE_STATUSES}
        metaSegments={metaSegmentsFor}
        selectable
        selectedIds={bulk.selection.selectedIds}
        onSelectChange={bulk.onSelectChange}
        onOpen={setSelectedId}
        onRetry={(id) => {
          void run(async () => {
            await resetConversion(id)
          })
        }}
        onCancelQueue={() => {
          void run(cancelConversion)
        }}
        onOpenFile={(id) => {
          const target = targetFor(id)
          if (target !== null) {
            recordShellIpc('openPath', target)
            void window.api.openPath(target)
          }
        }}
        onOpenFolder={(id) => {
          const target = targetFor(id)
          if (target !== null) {
            recordShellIpc('showItemInFolder', target)
            void window.api.showItemInFolder(target)
          }
        }}
        onCopyLocation={(value) => {
          void navigator.clipboard?.writeText(value)
        }}
        onMoveUp={(id) => {
          reorder(id, 'up')
        }}
        onMoveDown={(id) => {
          reorder(id, 'down')
        }}
        onMoveTop={(id) => {
          reorder(id, 'top')
        }}
        onMoveBottom={(id) => {
          reorder(id, 'bottom')
        }}
        onRemove={(id) => {
          setConfirm({ kind: 'remove', id })
        }}
        onBrowse={browseForFiles}
        onDropFiles={stageDroppedFiles}
        />
        </div>
      </div>

      <ConfirmModal
        open={confirm !== null}
        title={confirmCopy(confirm, bulk.removeConfirmLabel).title}
        description={confirmCopy(confirm, bulk.removeConfirmLabel).description}
        confirmLabel={confirmCopy(confirm, bulk.removeConfirmLabel).confirmLabel}
        cancelLabel={confirm?.kind === 'cancel' ? 'Keep running' : undefined}
        destructive
        onConfirm={() => {
          const pending = confirm
          setConfirm(null)
          if (pending === null) {
            return
          }
          if (pending.kind === 'bulk-remove') {
            bulk.removeSelected()
            return
          }
          void run(async () => {
            if (pending.kind === 'remove') {
              await removeConversion(pending.id)
              return
            }
            if (pending.kind === 'cancel') {
              await cancelConversion()
              return
            }
            await clearConversions()
          })
        }}
        onCancel={() => {
          setConfirm(null)
        }}
      />
    </section>
  )
}
