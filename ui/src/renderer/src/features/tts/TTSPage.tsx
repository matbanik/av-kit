import { useQueryClient } from '@tanstack/react-query'
import { useEffect, useMemo, useRef, useState } from 'react'

import { Button } from '../../components/ui/Button'
import { Disclosure } from '../../components/ui/Disclosure'
import { PathRow } from '../../components/ui/PathRow'
import { HelpCard } from '../../components/help/HelpCard'
import { ProgressBar } from '../../components/ui/ProgressBar'
import { SegmentedControl } from '../../components/ui/SegmentedControl'
import { SelectInput } from '../../components/ui/SelectInput'
import { StatusChip } from '../../components/ui/StatusChip'
import { ApiError } from '../../lib/api'
import { usePublishCommandState } from '../../registry/command-state'
import { ariaKeyshortcuts } from '../../registry/shortcuts'
import {
  browseOutputDir,
  cancelJob,
  loadTextFile,
  openOutput,
  openOutputFolder,
  pasteClipboard,
  postDownload,
  postDownloadAsset,
  postGenerate,
  postLoad,
  postPrepare,
  postUnload,
  putSettings,
} from './tts-commands'
import {
  assetChip,
  assetGetVisible,
  presentAssetRows,
  QUERY_HEALTH_DEPENDENCIES,
  TTS_ASSET_LABELS,
} from './tts-assets'
import {
  cancelEnabled,
  defaultModelSelection,
  generateEnabled,
  modelStateSuffix,
  openOutputEnabled,
  resolveModelAction,
  SPEED_PRESETS,
  STATUS_COLORS,
  type ModelAction,
} from './tts-controls'
import { DEVICE_FLOOR } from './tts-devices'
import { TTS_HELP_SECTIONS } from './tts-help-content'
import { CLEANUP_LABELS, PREPARE_DEFAULT_ON, PREPARE_STEPS } from './tts-prepare'
import { resolveRunBarSlot, runBarError } from './tts-run-bar'
import { textStats } from './tts-stats'
import { type VoiceOut } from './tts-voices'
import {
  QUERY_MODELS_AVAILABLE,
  useDownloadRuntime,
  useModelsAvailable,
  useModelStatus,
  useTtsDependencies,
  useTtsJob,
  useTtsSettings,
  useVoices,
} from './useTtsJob'
import { VoiceCombobox } from './VoiceCombobox'

const TTS_ERROR_EVENT = 'av-kit:tts:error'
const OUTPUT_DEFAULT = '~/Documents'
const INPUT_DEBOUNCE_MS = 300

/** The model button's `data-testid` follows `MODEL_ACTION` (registered ids, D-15). */
const MODEL_ACTION_TEST_IDS: Record<ModelAction, string> = {
  get: 'model-get-btn',
  load: 'model-load-btn',
  unload: 'unload-btn',
}

/** Button label per `MODEL_ACTION`; Get reads "Getting…" while the selection downloads. */
const MODEL_ACTION_LABELS: Record<ModelAction, (downloading: boolean) => string> = {
  get: (downloading) => (downloading ? 'Getting…' : 'Get'),
  load: () => 'Load',
  unload: () => 'Unload',
}

/** Settings leaves a user can change before hydration lands (Session 24 RULE-2). */
type HydratedLeaf = 'input_text' | 'voice' | 'speed' | 'output_format' | 'output_path' | 'device'

/** Radio id/test id for a speed preset, e.g. `speed-preset-1-1`. */
function presetId(preset: number): string {
  return `speed-preset-${preset.toFixed(1).replace('.', '-')}`
}

export function TTSPage() {
  const settingsQuery = useTtsSettings()
  const voicesQuery = useVoices()
  const modelsQuery = useModelsAvailable()
  const statusQuery = useModelStatus()
  const runtimeQuery = useDownloadRuntime()
  const depsQuery = useTtsDependencies()
  const queryClient = useQueryClient()
  const lastRuntimeState = useRef<string | undefined>(undefined)
  const textRef = useRef<HTMLTextAreaElement | null>(null)
  const debounceTimer = useRef<number | undefined>(undefined)
  const touched = useRef(new Set<HydratedLeaf>())
  const [text, setText] = useState('')
  const [hydrated, setHydrated] = useState(false)
  const [enabledSteps, setEnabledSteps] = useState<string[]>([...PREPARE_DEFAULT_ON])
  // The cleaned preview exists only after a successful Preview of the current text (AC-64.2).
  const [previewCleaned, setPreviewCleaned] = useState<string | null>(null)
  const [sourceKind, setSourceKind] = useState<'inline' | 'file'>('inline')
  const [sourcePath, setSourcePath] = useState<string | null>(null)
  const [voice, setVoice] = useState('af_heart')
  const [speed, setSpeed] = useState(1)
  const [format, setFormat] = useState<'MP3' | 'WAV'>('MP3')
  const [device, setDevice] = useState('auto')
  const [outputPath, setOutputPath] = useState(OUTPUT_DEFAULT)
  const [chunkMaxChars, setChunkMaxChars] = useState<number | undefined>(undefined)
  const [jobId, setJobId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [cleanupOpen, setCleanupOpen] = useState(false)
  const [manageOpen, setManageOpen] = useState(false)
  const [chosenModel, setChosenModel] = useState<string | null>(null)

  const jobQuery = useTtsJob(jobId)
  const job = jobQuery.data
  const status = job?.status ?? 'Idle'
  const isLoaded = statusQuery.data?.is_loaded === true
  const stats = useMemo(() => textStats(text, speed), [text, speed])
  // PAGE_STATE: the Preview and Generate buttons' own enabled expressions.
  usePublishCommandState('/tts', {
    'tts:prepare': !(busy || text.trim().length < 1),
    'tts:generate': generateEnabled({ isLoaded, text, status }) && !busy,
  })

  const voices = useMemo(() => (voicesQuery.data?.items ?? []) as VoiceOut[], [voicesQuery.data?.items])

  useEffect(() => {
    const onError = (event: Event) => {
      setError((event as CustomEvent<string>).detail)
    }
    window.addEventListener(TTS_ERROR_EVENT, onError)
    return () => {
      window.removeEventListener(TTS_ERROR_EVENT, onError)
    }
  }, [])

  /*
    Hydration applies once, and only to leaves the user has not already changed
    (Session 24 RULE-2): a settings response that lands after the user typed or
    chose something must not overwrite that choice.
  */
  useEffect(() => {
    if (hydrated || settingsQuery.data === undefined) {
      return
    }
    const data = settingsQuery.data
    const fresh = (leaf: HydratedLeaf): boolean => !touched.current.has(leaf)
    if (typeof data.input_text === 'string' && fresh('input_text')) {
      setText(data.input_text)
    }
    if (typeof data.voice === 'string' && fresh('voice')) {
      setVoice(data.voice)
    }
    if (typeof data.speed === 'number' && fresh('speed')) {
      setSpeed(data.speed)
    }
    if ((data.output_format === 'MP3' || data.output_format === 'WAV') && fresh('output_format')) {
      setFormat(data.output_format)
    }
    if (fresh('output_path')) {
      setOutputPath(
        typeof data.output_path === 'string' && data.output_path.length > 0
          ? data.output_path
          : OUTPUT_DEFAULT,
      )
    }
    if (typeof data.device === 'string' && fresh('device')) {
      setDevice(data.device)
    }
    if (typeof data.chunk_max_chars === 'number' && data.chunk_max_chars > 0) {
      setChunkMaxChars(data.chunk_max_chars)
    }
    setHydrated(true)
  }, [hydrated, settingsQuery.data])

  /* A finished (or failed) download changes the catalog and the readiness rows. */
  const currentRuntimeState = runtimeQuery.data?.state
  useEffect(() => {
    const previous = lastRuntimeState.current
    lastRuntimeState.current = currentRuntimeState
    if (previous === 'Downloading' && currentRuntimeState !== 'Downloading') {
      void queryClient.invalidateQueries({ queryKey: QUERY_MODELS_AVAILABLE })
      void queryClient.invalidateQueries({ queryKey: QUERY_HEALTH_DEPENDENCIES })
    }
  }, [currentRuntimeState, queryClient])

  useEffect(() => {
    return () => {
      if (debounceTimer.current !== undefined) {
        window.clearTimeout(debounceTimer.current)
      }
    }
  }, [])

  async function run(work: () => Promise<void>): Promise<void> {
    setBusy(true)
    setError(null)
    try {
      await work()
    } catch (caught) {
      const message = caught instanceof ApiError || caught instanceof Error ? caught.message : String(caught)
      setError(message)
    } finally {
      setBusy(false)
    }
  }

  function persistLeaf(patch: Parameters<typeof putSettings>[0]): void {
    void putSettings(patch).catch((caught: unknown) => {
      const message = caught instanceof ApiError || caught instanceof Error ? caught.message : String(caught)
      setError(message)
    })
  }

  function scheduleInputText(next: string): void {
    touched.current.add('input_text')
    if (debounceTimer.current !== undefined) {
      window.clearTimeout(debounceTimer.current)
    }
    debounceTimer.current = window.setTimeout(() => {
      persistLeaf({ input_text: next })
    }, INPUT_DEBOUNCE_MS)
  }

  /** Replace the text from any source; the cleaned preview no longer describes it. */
  function replaceText(next: string, kind: 'inline' | 'file', path: string | null): void {
    setText(next)
    setSourceKind(kind)
    setSourcePath(path)
    setPreviewCleaned(null)
    scheduleInputText(next)
  }

  function chooseVoice(voiceId: string): void {
    touched.current.add('voice')
    setVoice(voiceId)
    persistLeaf({ voice: voiceId })
  }

  function chooseSpeed(next: number): void {
    touched.current.add('speed')
    setSpeed(next)
    persistLeaf({ speed: next })
  }

  const openTarget = job?.output_path ?? (outputPath !== OUTPUT_DEFAULT ? outputPath : null)
  const outputActionable = openOutputEnabled(openTarget)
  const loadedVariantId = statusQuery.data?.variant_id ?? null
  const runtimeState = runtimeQuery.data?.state ?? 'Idle'
  const catalog = modelsQuery.data?.items ?? []
  const loadedName = catalog.find((item) => item.id === loadedVariantId)?.name
  const loadedChipText = isLoaded
    ? `${loadedName ?? loadedVariantId ?? 'model'} · ${statusQuery.data?.device ?? device}`
    : 'No model loaded'
  const loadedDetails = isLoaded
    ? `Loaded: ${statusQuery.data?.variant_id ?? 'model'} (${statusQuery.data?.device ?? device})${
        typeof statusQuery.data?.memory_bytes === 'number' ? ` · ${statusQuery.data.memory_bytes} B` : ''
      }`
    : 'No model loaded'
  const activeVariantId = isLoaded ? loadedVariantId : null
  const selectedModelId = defaultModelSelection({ chosen: chosenModel, loadedVariantId: activeVariantId, catalog })
  const selectedModel = catalog.find((item) => item.id === selectedModelId)
  // The select lists the selected row's devices. A stored device the row cannot use shows and
  // loads as `auto`; the setting itself is kept for rows that offer it (D-13).
  const deviceOptions = selectedModel?.devices ?? DEVICE_FLOOR
  const effectiveDevice = deviceOptions.includes(device) ? device : 'auto'
  const modelAction =
    selectedModel === undefined
      ? null
      : resolveModelAction({
          isDownloaded: selectedModel.is_downloaded,
          loadedVariantId: activeVariantId,
          rowId: selectedModel.id,
          runtimeState,
        })
  const selectedDownloading =
    runtimeState === 'Downloading' && selectedModel !== undefined && runtimeQuery.data?.variant_id === selectedModel.id
  const downloadFraction = runtimeQuery.data?.fraction ?? 0
  const downloadTarget =
    catalog.find((item) => item.id === runtimeQuery.data?.variant_id)?.name ??
    (runtimeQuery.data?.asset && runtimeQuery.data.asset in TTS_ASSET_LABELS
      ? TTS_ASSET_LABELS[runtimeQuery.data.asset as keyof typeof TTS_ASSET_LABELS]
      : 'model')
  const assetRows = presentAssetRows(depsQuery.data)
  const runBarText = runBarError({ error, status, jobError: job?.error_message })
  const slot = resolveRunBarSlot({ error, status, jobError: job?.error_message })
  const segmentsDone = job?.segments_done ?? 0
  const segmentsTotal = job?.segments_total ?? 0
  const presetValue = SPEED_PRESETS.find((preset) => preset === speed)

  return (
    <div className="flex flex-col gap-4 p-4" data-testid="tts-page">
      <HelpCard feature="tts" tabKey="main" sections={TTS_HELP_SECTIONS} />

      <div className="grid w-full max-w-[var(--layout-page-max-width)] grid-cols-1 gap-3.5 min-[880px]:grid-cols-[minmax(0,1.45fr)_minmax(300px,1fr)]">
        <section aria-labelledby="tts-text-title" className="flex min-w-0 flex-col gap-2 rounded-[var(--radius-lg)] border border-border p-3">
          <div className="flex flex-wrap items-center gap-2">
            <h2 id="tts-text-title" className="mr-auto text-sm font-semibold text-fg">
              Text
            </h2>
            <Button
              data-testid="load-file-btn"
              variant="ghost"
              size="sm"
              disabled={busy}
              onClick={() => {
                void run(async () => {
                  const loaded = await loadTextFile()
                  if (loaded === null) {
                    return
                  }
                  replaceText(loaded.text, 'file', loaded.basename)
                })
              }}
            >
              Load file
            </Button>
            <Button
              data-testid="paste-btn"
              variant="ghost"
              size="sm"
              disabled={busy}
              onClick={() => {
                void run(async () => {
                  const clip = await pasteClipboard()
                  if (clip.length === 0) {
                    return
                  }
                  const el = textRef.current
                  const start = el?.selectionStart ?? text.length
                  const end = el?.selectionEnd ?? text.length
                  const next = `${text.slice(0, start)}${clip}${text.slice(end)}`
                  replaceText(next, 'inline', null)
                  window.requestAnimationFrame(() => {
                    const field = textRef.current
                    if (field) {
                      const caret = start + clip.length
                      field.focus()
                      field.setSelectionRange(caret, caret)
                    }
                  })
                })
              }}
            >
              Paste
            </Button>
          </div>
          <textarea
            ref={textRef}
            data-testid="text-input"
            aria-labelledby="tts-text-title"
            rows={11}
            className="resize-y rounded-[var(--radius-control)] border border-border bg-bg-elevated p-3"
            value={text}
            onChange={(event) => {
              replaceText(event.target.value, 'inline', null)
            }}
          />
          <div className="flex flex-wrap items-center gap-4 text-sm tabular-nums text-fg-muted">
            <span data-testid="word-count">{stats.words} words</span>
            <span data-testid="sentence-count">{stats.sentences} sentences</span>
            <span data-testid="duration-estimate">
              {stats.words === 0 ? '—' : `~${Math.round(stats.durationSeconds)}s @ ${speed}x`}
            </span>
          </div>
          <Disclosure
            id="tts-cleanup"
            testId="cleanup-toggle"
            title={`Cleanup · ${enabledSteps.length} of ${PREPARE_STEPS.length} steps`}
            open={cleanupOpen}
            onOpenChange={setCleanupOpen}
          >
            <div className="flex flex-col gap-2 pt-2">
              <div className="flex items-center gap-2">
                <span className="mr-auto text-sm font-medium">Cleanup pipeline</span>
                <Button
                  data-testid="preview-cleanup-btn"
                  variant="secondary"
                  size="sm"
                  disabled={busy || text.trim().length < 1}
                  onClick={() => {
                    void run(async () => {
                      const result = await postPrepare(text, enabledSteps, chunkMaxChars)
                      if (result) {
                        setPreviewCleaned(result.cleaned_text)
                      }
                    })
                  }}
                >
                  Preview cleanup
                </Button>
                <Button
                  data-testid="apply-cleanup-btn"
                  variant="secondary"
                  size="sm"
                  disabled={busy || text.trim().length < 1}
                  onClick={() => {
                    void run(async () => {
                      // On failure run() shows the error and the text stays as it was.
                      const result = await postPrepare(text, enabledSteps, chunkMaxChars)
                      if (result) {
                        replaceText(result.cleaned_text, 'inline', null)
                      }
                    })
                  }}
                >
                  Apply cleanup
                </Button>
              </div>
              <fieldset data-testid="cleanup-pipeline" className="grid grid-cols-3 gap-2">
                <legend className="sr-only">Cleanup pipeline</legend>
                {PREPARE_STEPS.map((step) => (
                  <label key={step} className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      value={step}
                      checked={enabledSteps.includes(step)}
                      onChange={(event) => {
                        setEnabledSteps((prev) =>
                          event.target.checked ? [...prev, step] : prev.filter((s) => s !== step),
                        )
                      }}
                    />
                    {CLEANUP_LABELS[step]}
                  </label>
                ))}
              </fieldset>
              {previewCleaned !== null ? (
                <pre
                  data-testid="preview-cleaned"
                  className="max-h-40 min-h-20 overflow-auto rounded border border-border p-2 text-xs whitespace-pre-wrap"
                >
                  {previewCleaned}
                </pre>
              ) : null}
            </div>
          </Disclosure>
        </section>

        <section aria-labelledby="tts-voice-title" className="flex min-w-0 flex-col gap-3 rounded-[var(--radius-lg)] border border-border p-3">
          <div className="flex flex-wrap items-center gap-2">
            <h2 id="tts-voice-title" className="mr-auto text-sm font-semibold text-fg">
              Voice
            </h2>
            <StatusChip testId="loaded-model" label={loadedChipText} tone={isLoaded ? 'success' : 'warning'} />
          </div>
          {/* MEU-63: the picker, its one action and the readiness chips stay visible; only the
              details sit behind "Model details". The panel is a direct child of this block
              (not the Disclosure primitive, which wraps its panel in its own section). */}
          <div className="flex flex-col gap-2">
            <div data-testid="model-row" className="grid grid-cols-[minmax(0,1fr)_7rem_auto] items-end gap-2">
              <SelectInput
                data-testid="model-select"
                label="Model"
                options={catalog.map((item) => ({
                  value: item.id,
                  // MODEL_FIELDS: a row this build can't run is disabled, its reason in place of its state.
                  label: `${item.name} — ${
                    item.available === false && item.reason
                      ? item.reason
                      : modelStateSuffix({
                          rowId: item.id,
                          isDownloaded: item.is_downloaded,
                          loadedVariantId: activeVariantId,
                          runtime: runtimeQuery.data,
                        })
                  }`,
                  disabled: item.available === false,
                }))}
                value={selectedModelId ?? ''}
                onChange={(event) => {
                  setChosenModel(event.target.value)
                }}
              />
              <SelectInput
                data-testid="device-select"
                label="Device"
                options={deviceOptions.map((option) => ({ value: option, label: option }))}
                value={effectiveDevice}
                onChange={(event) => {
                  touched.current.add('device')
                  setDevice(event.target.value)
                  persistLeaf({ device: event.target.value as 'auto' | 'cuda' | 'cpu' | 'mps' })
                }}
              />
              {selectedModel !== undefined && modelAction !== null ? (
                <Button
                  data-testid={MODEL_ACTION_TEST_IDS[modelAction.action]}
                  variant="primary"
                  size="md"
                  disabled={busy || !modelAction.enabled}
                  onClick={() => {
                    const variantId = selectedModel.id
                    void run(async () => {
                      if (modelAction.action === 'get') {
                        await postDownload(variantId)
                      } else if (modelAction.action === 'load') {
                        await postLoad(variantId, effectiveDevice)
                      } else {
                        await postUnload()
                      }
                    })
                  }}
                >
                  {MODEL_ACTION_LABELS[modelAction.action](selectedDownloading)}
                </Button>
              ) : null}
            </div>
            {runtimeState === 'Downloading' ? (
              <div data-testid="download-progress" className="flex items-center gap-2 text-sm tabular-nums text-fg-muted">
                <span className="w-32">
                  <ProgressBar
                    testId="download-progress-bar"
                    value={downloadFraction}
                    ariaLabel={`Download progress for ${downloadTarget}`}
                  />
                </span>
                {`${downloadTarget} · ${Math.round(downloadFraction * 100)}%`}
              </div>
            ) : null}
            {assetRows.length > 0 ? (
              <div className="flex flex-wrap items-center gap-2">
                {assetRows.map(([wire, row]) => {
                  const chip = assetChip(row.state)
                  return (
                    <span key={wire} className="flex items-center gap-1">
                      <StatusChip
                        testId={`tts-asset-chip-${wire}`}
                        label={`${TTS_ASSET_LABELS[wire]}: ${chip.label}`}
                        tone={chip.tone}
                      />
                      {assetGetVisible(row.state) ? (
                        <Button
                          data-testid={`tts-asset-get-btn-${wire}`}
                          variant="secondary"
                          size="sm"
                          disabled={busy || row.state === 'downloading' || runtimeState === 'Downloading'}
                          onClick={() => {
                            void run(async () => {
                              await postDownloadAsset(wire)
                            })
                          }}
                        >
                          Get
                        </Button>
                      ) : null}
                    </span>
                  )
                })}
              </div>
            ) : null}
            <Button
              aria-controls="tts-model-details-panel"
              aria-expanded={manageOpen}
              data-testid="model-manage-toggle"
              variant="ghost"
              className="self-start"
              onClick={() => {
                setManageOpen(!manageOpen)
              }}
            >
              Model details
            </Button>
            <section
              id="tts-model-details-panel"
              data-testid="model-manager"
              hidden={!manageOpen}
              className="flex flex-col gap-2"
            >
              <h3 className="sr-only">Model details</h3>
              <div data-testid="loaded-model-details" className="text-xs text-fg-muted">
                {loadedDetails}
              </div>
            </section>
          </div>
          <VoiceCombobox
            voices={voices}
            value={voice}
            onSelect={chooseVoice}
            testIds={{
              input: 'voice-combobox',
              chip: 'voice-selected-chip',
              list: 'voice-grid',
              option: 'voice-card',
              language: 'language-select',
            }}
          />
          <div className="grid grid-cols-[minmax(0,1fr)_auto] items-end gap-2">
            <label className="flex min-w-0 flex-col gap-1">
              <span className="text-sm font-medium text-fg-muted">{`Speed ${speed.toFixed(1)}×`}</span>
              <input
                data-testid="speed-slider"
                type="range"
                className="h-9 w-full"
                min={0.5}
                max={2.0}
                step={0.1}
                value={speed}
                onChange={(event) => {
                  chooseSpeed(Number(event.target.value))
                }}
              />
            </label>
            <SegmentedControl
              name="Speed preset"
              size="md"
              value={presetValue === undefined ? '' : String(presetValue)}
              options={SPEED_PRESETS.map((preset) => ({
                id: presetId(preset),
                testId: presetId(preset),
                value: String(preset),
                label: preset.toFixed(1),
              }))}
              onValueChange={(next) => {
                chooseSpeed(Number(next))
              }}
            />
          </div>
          <div className="w-28">
            <SelectInput
              data-testid="format-select"
              label="Format"
              options={[
                { value: 'MP3', label: 'MP3' },
                { value: 'WAV', label: 'WAV' },
              ]}
              value={format}
              onChange={(event) => {
                const next = event.target.value as 'MP3' | 'WAV'
                touched.current.add('output_format')
                setFormat(next)
                persistLeaf({ output_format: next })
              }}
            />
          </div>
        </section>
      </div>

      {/* TT7: the run bar sits statically below both columns; it is never sticky. */}
      <div
        data-run-bar=""
        className="flex w-full max-w-[var(--layout-page-max-width)] flex-wrap items-center gap-2 rounded-[var(--radius-lg)] border border-border p-3"
      >
        <PathRow
          id="tts-output-path"
          label="Output path"
          inputTestId="output-path"
          browseTestId="browse-output-btn"
          value={outputPath}
          onChange={() => {}}
          readOnly
          browseDisabled={busy}
          onBrowse={() => {
            void run(async () => {
              const chosen = await browseOutputDir()
              if (chosen === undefined) {
                return
              }
              touched.current.add('output_path')
              setOutputPath(chosen)
              await putSettings({ output_path: chosen })
            })
          }}
          className="min-w-[20rem] flex-1"
        />
        <Button
          data-testid="generate-btn"
          variant="primary"
          size="md"
          title="Generate (Ctrl+Enter)"
          aria-keyshortcuts={ariaKeyshortcuts('Ctrl+Enter')}
          disabled={!generateEnabled({ isLoaded, text, status }) || busy}
          onClick={() => {
            void run(async () => {
              const created = await postGenerate(
                {
                  text,
                  voice,
                  speed,
                  format,
                  enabled_steps: enabledSteps,
                  source_kind: sourceKind,
                  source_path: sourcePath,
                },
                { isLoaded, status },
              )
              if (created) {
                setJobId(created.id)
              }
            })
          }}
        >
          Generate
        </Button>
        <Button
          data-testid="cancel-btn"
          variant="secondary"
          size="md"
          disabled={!cancelEnabled({ status }) || jobId === null || busy}
          onClick={() => {
            if (jobId === null) {
              return
            }
            void run(async () => {
              await cancelJob(jobId, status)
            })
          }}
        >
          Cancel
        </Button>
        <span className={`rounded px-2 py-1 text-xs text-fg ${STATUS_COLORS[status as keyof typeof STATUS_COLORS] ?? 'bg-neutral'}`}>
          {status}
        </span>
        <div className="flex min-w-0 flex-1 flex-wrap items-center gap-2 text-sm">
          {slot === 'error' ? (
            <p data-testid="error-banner" role="alert" className="text-error">
              {runBarText}
            </p>
          ) : null}
          {slot === 'progress' ? (
            <div data-testid="segment-progress" className="flex min-w-0 flex-1 items-center gap-2">
              <span className="w-32 shrink-0">
                <ProgressBar
                  testId="segment-progress-bar"
                  value={segmentsTotal > 0 ? segmentsDone / segmentsTotal : 0}
                  ariaLabel="Segment progress"
                />
              </span>
              <span className="min-w-0 truncate tabular-nums text-fg-muted">
                Segments {job?.segments_done ?? 0}/{job?.segments_total ?? 0}
                {job?.text_preview ? ` · ${job.text_preview}` : ''}
                {job?.text_hash ? ` · ${job.text_hash.slice(0, 8)}` : ''}
              </span>
            </div>
          ) : null}
          {slot === 'output' ? (
            <>
              <span
                data-testid="last-output"
                className={`min-w-0 truncate ${job?.output_path ? 'text-fg' : 'text-fg-muted'}`}
              >
                {job?.output_path ?? 'No output yet'}
              </span>
              {outputActionable ? (
                <>
                  <Button
                    data-testid="open-output-btn"
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      if (!openTarget) {
                        return
                      }
                      void run(async () => {
                        await openOutput(openTarget)
                      })
                    }}
                  >
                    Open file
                  </Button>
                  <Button
                    data-testid="open-output-folder-btn"
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      if (!openTarget) {
                        return
                      }
                      void run(async () => {
                        await openOutputFolder(openTarget)
                      })
                    }}
                  >
                    Open folder
                  </Button>
                </>
              ) : null}
            </>
          ) : null}
        </div>
      </div>
    </div>
  )
}
