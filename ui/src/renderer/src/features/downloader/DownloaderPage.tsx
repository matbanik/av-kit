import { useQuery } from '@tanstack/react-query'
import { useEffect, useMemo, useRef, useState } from 'react'

import { Button } from '../../components/ui/Button'
import { ConfirmModal } from '../../components/ui/ConfirmModal'
import { Disclosure } from '../../components/ui/Disclosure'
import { HelpCard } from '../../components/help/HelpCard'
import { SegmentedControl } from '../../components/ui/SegmentedControl'
import { StatusChip } from '../../components/ui/StatusChip'
import { BulkActionBar } from '../../components/queue/BulkActionBar'
import { BulkResultToast } from '../../components/queue/BulkResultToast'
import { QueueHeaderRow } from '../../components/queue/QueueHeaderRow'
import { QueueList } from '../../components/queue/QueueList'
import { type QueueCardJob } from '../../components/queue/QueueCard'
import { ApiError, apiFetch } from '../../lib/api'
import {
  acquireQueueReorder,
  type ReorderQueueKey,
} from '../../lib/queue/reorder-single-flight'
import { CLEAR_FINISHED_STATUSES } from '../../lib/queue/run-bulk'
import { useQueueBulk } from '../../lib/queue/use-queue-bulk'
import { recordShellIpc } from '../../lib/queue/shell-ipc-ledger'
import { logRenderer } from '../../lib/renderer-log'
import { queryClient } from '../../lib/query-client'
import { usePublishCommandState } from '../../registry/command-state'
import { ariaKeyshortcuts } from '../../registry/shortcuts'
import {
  audioFormatVisible,
  cookieBrowserVisible,
  cookieFileVisible,
  cookieSettingsPutBody,
  cookieTestBody,
  COOKIE_BROWSERS,
  COOKIE_MODES,
  type CookieMode,
} from './cookie-bar'
import {
  buildReorderBody,
  controlEnabled,
  DOWNLOAD_REQUEUEABLE_STATUSES,
  downloadMetaSegments,
  JOB_STATUSES,
  processorLabel,
  queueSummary,
  type ProcessorState,
} from './download-controls'
import {
  cancelDownload,
  checkSabr,
  clearDownloads,
  clearSabr,
  DOWNLOAD_CONFIRM_EVENT,
  forceSabr,
  pauseDownload,
  postDownloadCreate,
  removeDownload,
  removeDownloadOnly,
  reorderDownload,
  reorderDownloadOnly,
  reorderDownloadToIndex,
  resetDownload,
  resetDownloadOnly,
  resumeDownload,
  startDownload,
  type DownloadConfirmRequest,
  type ReorderDirection,
} from './download-commands'
import {
  AUDIO_DEFAULT,
  audioOptions,
  QUALITY_DEFAULT,
  qualityOptions,
  SELECT_THEME_STYLE,
  type AudioWire,
  type QualityWire,
} from './quality-options'
import { fetchSabr, sabrResultText } from './sabr-panel'
import { DOWNLOADER_HELP_SECTIONS } from './downloader-help-content'
import { QUERY_KEY, useDownloadQueue } from './useDownloadQueue'

/*
  The ids this page is responsible for rendering, after the MEU-46 migration
  (AC-46.4/.6). The thirteen retired row/toolbar buttons are not dropped from
  the surface -- each one's capability moved onto a shared queue id listed here,
  per RETIRED_TOOLBAR_CONTROLS.downloader:

    queue-table/queue-row -> queue-list / queue-card
    start/pause/resume    -> queue-toolbar-start / -pause / -resume
    cancel/reset/open-file (Done row) -> queue-card-primary-action
    up/down/top/bottom/remove/open-file/open-folder -> queue-card-kebab menu
    clear-all             -> queue-toolbar-overflow > queue-toolbar-clear-all
*/
export const DOWNLOADER_TEST_IDS = [
  'downloader-page',
  'url-input',
  'add-btn',
  'queue-list',
  'queue-card',
  'queue-card-primary-action',
  'queue-card-kebab',
  'queue-card-menu',
  'queue-toolbar',
  'queue-toolbar-start',
  'queue-toolbar-pause',
  'queue-toolbar-resume',
  'queue-toolbar-clear-finished',
  'queue-toolbar-overflow',
  'queue-toolbar-clear-all',
  'queue-empty-invite',
  'queue-empty-invite-action',
  'confirm-modal',
  'sabr-status',
  'sabr-check-btn',
  'quality-select',
  'audio-only',
  'audio-format',
  'cookie-mode-none',
  'cookie-mode-browser',
  'cookie-mode-file',
  'cookie-browser',
  'cookie-profile',
  'cookie-file',
  'cookie-test-btn',
  'sabr-force-btn',
  'sabr-clear-btn',
  'sabr-quality-chip',
  'add-advanced-toggle',
  'queue-summary',
  'processor-indicator',
  'error-banner',
] as const

const DOWNLOAD_ERROR_EVENT = 'av-kit:download:error'

type DownloadConfirm =
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
  confirm: DownloadConfirm,
  bulkRemoveLabel: string,
): { title: string; description: string; confirmLabel: string } {
  if (confirm?.kind === 'clear') {
    return {
      title: 'Clear the whole queue?',
      description: 'Every queued download is dropped. Files already on disk stay there.',
      confirmLabel: 'Clear all',
    }
  }
  if (confirm?.kind === 'cancel') {
    return {
      title: 'Cancel active downloads?',
      description: 'Work in progress stops. Files already on disk stay there.',
      confirmLabel: 'Cancel downloads',
    }
  }
  if (confirm?.kind === 'bulk-remove') {
    return {
      title: `${bulkRemoveLabel}?`,
      description: 'The queue records are deleted. Files already on disk stay there.',
      confirmLabel: bulkRemoveLabel,
    }
  }
  return {
    title: 'Remove from queue?',
    description: 'The queue record is deleted. Files already on disk stay there.',
    confirmLabel: 'Remove',
  }
}

function asProcessor(state: string | undefined): ProcessorState {
  if (state === 'Processing' || state === 'Paused') {
    return state
  }
  return 'Idle'
}

/**
 * The single-flight key every reorder path on this page shares
 * (`REORDER_SINGLE_FLIGHT_RULE`). One constant, so the kebab, Alt+Arrow, the
 * drag handle, the bulk fold and the gate the handle reads back cannot drift
 * onto two different keys and stop excluding each other.
 */
const DOWNLOAD_QUEUE_KEY: ReorderQueueKey = 'download'
const DOWNLOADER_SETTINGS_KEY = ['settings', 'downloader'] as const

type DownloaderSettings = {
  cookie_mode?: string | null
  cookie_browser?: string | null
  cookie_browser_profile?: string | null
  cookie_file_path?: string | null
}

export function DownloaderPage() {
  const queue = useDownloadQueue()
  const sabrQuery = useQuery({
    queryKey: ['downloads', 'sabr'],
    queryFn: fetchSabr,
  })
  const cookieSettings = useQuery({
    queryKey: DOWNLOADER_SETTINGS_KEY,
    queryFn: () => apiFetch<DownloaderSettings>('/settings/downloader'),
  })
  const [url, setUrl] = useState('')
  const [quality, setQuality] = useState<QualityWire>(QUALITY_DEFAULT)
  const [audioOnly, setAudioOnly] = useState(false)
  const [audioFormat, setAudioFormat] = useState<AudioWire>(AUDIO_DEFAULT)
  const [cookieMode, setCookieMode] = useState<CookieMode>('none')
  const [cookieBrowser, setCookieBrowser] = useState<(typeof COOKIE_BROWSERS)[number]>('chrome')
  const [cookieProfile, setCookieProfile] = useState('')
  const [cookieFile, setCookieFile] = useState('')
  const [advancedOpen, setAdvancedOpen] = useState(false)
  const advancedInitialized = useRef(false)
  const advancedTouched = useRef(false)
  const cookieSettingsTouched = useRef(false)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [addStatus, setAddStatus] = useState<string | null>(null)
  const [adding, setAdding] = useState(false)
  const [busy, setBusy] = useState(false)
  const [confirm, setConfirm] = useState<DownloadConfirm>(null)

  const items = useMemo(() => queue.data?.items ?? [], [queue.data?.items])
  const processorState = asProcessor(queue.data?.processor.state)
  const sabrActive = sabrQuery.data?.mode === 'active'
  const qualities = qualityOptions(sabrActive)
  const audios = audioOptions(sabrActive)
  const summary = useMemo(() => queueSummary(items), [items])
  /*
    The same hook the converter uses. BULK_CONTROL_E2E_OBLIGATION requires both
    pages to behave identically under every bulk control, and a second copy of
    this logic is exactly where they would quietly diverge -- only the endpoints
    and the requeueable set differ per page.
  */
  const bulk = useQueueBulk({
    items,
    queueKey: DOWNLOAD_QUEUE_KEY,
    requeueableStatuses: DOWNLOAD_REQUEUEABLE_STATUSES,
    run: (action) => {
      void run(action)
    },
    retry: resetDownloadOnly,
    remove: removeDownloadOnly,
    reorder: reorderDownloadOnly,
    buildBody: buildReorderBody,
    refetch: async () => queue.refetch(),
  })
  const label = processorLabel(processorState)
  const ctx = { items, selectedId, processorState }

  useEffect(() => {
    if (
      advancedInitialized.current ||
      cookieSettings.isPending ||
      cookieSettings.isFetching ||
      sabrQuery.isPending ||
      sabrQuery.isFetching
    ) return
    advancedInitialized.current = true
    const settings = cookieSettings.data
    const configuredMode = COOKIE_MODES.find((mode) => mode === settings?.cookie_mode) ?? 'none'
    const configuredBrowser = COOKIE_BROWSERS.find((browser) => browser === settings?.cookie_browser) ?? 'chrome'
    if (!cookieSettingsTouched.current) {
      setCookieMode(configuredMode)
      setCookieBrowser(configuredBrowser)
      setCookieProfile(typeof settings?.cookie_browser_profile === 'string' ? settings.cookie_browser_profile : '')
      setCookieFile(typeof settings?.cookie_file_path === 'string' ? settings.cookie_file_path : '')
    }
    if (!advancedTouched.current) {
      setAdvancedOpen(configuredMode !== 'none' || sabrQuery.data?.mode === 'active')
    }
  }, [
    cookieSettings.data,
    cookieSettings.isFetching,
    cookieSettings.isPending,
    sabrQuery.data,
    sabrQuery.isFetching,
    sabrQuery.isPending,
  ])

  useEffect(() => {
    const onError = (event: Event) => {
      const detail = (event as CustomEvent<string>).detail
      setError(detail)
    }
    window.addEventListener(DOWNLOAD_ERROR_EVENT, onError)
    return () => {
      window.removeEventListener(DOWNLOAD_ERROR_EVENT, onError)
    }
  }, [])

  // CONFIRM_ROUTE: the palette's clear and cancel open this page's confirm.
  useEffect(() => {
    const onConfirmRequest = (event: Event) => {
      setConfirm({ kind: (event as CustomEvent<DownloadConfirmRequest>).detail.kind })
    }
    window.addEventListener(DOWNLOAD_CONFIRM_EVENT, onConfirmRequest)
    return () => {
      window.removeEventListener(DOWNLOAD_CONFIRM_EVENT, onConfirmRequest)
    }
  }, [])

  useEffect(() => {
    if (!qualities.includes(quality)) {
      setQuality(qualities[0] ?? QUALITY_DEFAULT)
    }
  }, [qualities, quality])

  useEffect(() => {
    if (!audios.includes(audioFormat)) {
      setAudioFormat(audios[0] ?? AUDIO_DEFAULT)
    }
  }, [audios, audioFormat])

  useEffect(() => {
    if (selectedId !== null && !items.some((item) => item.id === selectedId)) {
      setSelectedId(items[0]?.id ?? null)
    }
  }, [items, selectedId])

  function addFromForm(): void {
    const field = document.querySelector('[data-testid="url-input"]')
    const submittedUrl = field instanceof HTMLInputElement ? field.value : url
    const body = {
      url: submittedUrl,
      quality,
      audio_only: audioOnly,
      audio_format: audioFormat,
    }
    if (submittedUrl.trim().length < 1) {
      setError('URL is required')
      setAddStatus(null)
      return
    }
    setError(null)
    setAdding(true)
    setAddStatus('Adding — waiting for backend, then yt-dlp extract…')
    logRenderer('INFO', `add: posting ${submittedUrl.trim()}`)
    void postDownloadCreate(body)
      .then((out) => {
        if (out.items.length > 0) {
          setUrl('')
          setAddStatus(`Queued ${out.items.length} job(s). Click Start to download.`)
          logRenderer('INFO', `add: queued ${out.items.length} job(s)`)
          return
        }
        setAddStatus('Add returned no new jobs (duplicate or empty extract).')
        logRenderer('WARNING', 'add: no new jobs')
      })
      .catch((caught: unknown) => {
        const message = caught instanceof ApiError ? caught.message : caught instanceof Error ? caught.message : String(caught)
        setError(message)
        setAddStatus(null)
        logRenderer('ERROR', `add: ${message}`)
        void queryClient.invalidateQueries({ queryKey: QUERY_KEY })
      })
      .finally(() => {
        setAdding(false)
      })
  }

  async function persistCookies(next: {
    cookie_mode: CookieMode
    cookie_browser: (typeof COOKIE_BROWSERS)[number]
    cookie_browser_profile: string
    cookie_file_path: string
  }): Promise<void> {
    const body = cookieSettingsPutBody(next)
    await apiFetch('/settings/downloader', { method: 'PUT', body: JSON.stringify(body) })
    queryClient.setQueryData<DownloaderSettings>(DOWNLOADER_SETTINGS_KEY, (current) => ({
      ...current,
      ...body,
    }))
    await queryClient.invalidateQueries({ queryKey: DOWNLOADER_SETTINGS_KEY })
  }

  async function run(action: () => Promise<unknown>): Promise<void> {
    setBusy(true)
    setError(null)
    try {
      await action()
    } catch (caught) {
      const message = caught instanceof ApiError ? caught.message : caught instanceof Error ? caught.message : String(caught)
      setError(message)
    } finally {
      setBusy(false)
    }
  }

  /*
    Reorder acts on the id the control belongs to. The retired Up/Down/Top/
    Bottom buttons moved "the selected row"; a card's kebab and its Alt+Arrow
    shortcut move THAT card, so the id travels with the call. The wire body
    stays the complete permutation `reorderDownload` builds
    (REORDER_WIRE_CONTRACT) -- `routes/downloads.py` 422s a `{ id, direction }`.
  */
  /*
    Every permutation mutation on this page -- kebab, Alt+Arrow, drag, bulk fold
    -- goes through this one gate (`REORDER_SINGLE_FLIGHT_RULE`). Each of them
    computes its new order from `items`, the order react-query currently holds,
    so two of them in flight at once would both build a body from the SAME
    pre-move array and the second PUT would silently undo the first. The acquire
    is synchronous and happens before `items` is read; the release is in a
    `finally`, so a rejected PUT cannot strand the gate and leave every reorder
    control disabled for the rest of the session.
  */
  function withReorderGate(action: () => Promise<unknown>): void {
    const release = acquireQueueReorder(DOWNLOAD_QUEUE_KEY)
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
      await reorderDownload(
        items.map((item) => item.id),
        id,
        direction,
      )
    })
  }

  /*
    The drag path differs from the kebab path only in how the target is named:
    dnd-kit resolves a FINAL index, not a direction (`MOVE_TO_INDEX_CONTRACT`).
    It deliberately does NOT reorder the list optimistically -- the rendered
    order stays the server's until the reconcile lands, so a rejected PUT leaves
    the row exactly where it was and surfaces through the page's existing error
    banner rather than needing a rollback (AC-49.22).
  */
  function reorderToIndex(id: string, targetIndex: number): void {
    if (items.length < 1) {
      return
    }
    withReorderGate(async () => {
      await reorderDownloadToIndex(
        items.map((item) => item.id),
        id,
        targetIndex,
      )
    })
  }

  /** Resolve the on-disk target for a row's open-file / open-folder actions. */
  function targetFor(id: string): string | null {
    const path = items.find((item) => item.id === id)?.file_path
    return path !== null && path !== undefined && path.trim() !== '' ? path : null
  }

  /*
    QueueCard's own shape, built from the download wire row. `sourceUrl` is the
    video URL the job was queued from: before a file exists on disk, "copy
    location" copies where the job came FROM, which is the only location the
    row has (KEBAB_ACTION_LABELS makes the label follow that state).
  */
  const cards: QueueCardJob[] = items.map((item) => ({
    id: item.id,
    position: item.queue_position,
    status: item.status,
    title: item.title,
    progress: item.progress,
    fileSize: item.file_size,
    outputPath: item.file_path,
    sourceUrl: item.url,
    errorMessage: item.error_message ?? null,
  }))

  /*
    Per-row meta for the shared card (DOWNLOAD_META_SEGMENTS). `QueueCardJob`
    does not carry quality/speed/eta -- they are this page's columns, inherited
    from the retired table -- so the resolver goes back to the wire row by id.
  */
  const metaSegmentsFor = (job: QueueCardJob): readonly string[] => {
    const row = items.find((item) => item.id === job.id)
    if (row === undefined) {
      return []
    }
    return downloadMetaSegments({
      quality: row.quality,
      speed: row.speed,
      eta: row.eta,
      status: row.status,
      received_height: row.received_height,
    })
  }

  /*
    EMPTY_STATE_CONTRACT, downloader half. This queue's only intake is the URL
    field above, so it supplies its own invitation instead of `EmptyDropZone`:
    a file-drop target here could only be a no-op. The action focuses the real
    field rather than opening anything, which is why it is wired to the DOM node
    the form already renders.
  */
  const emptyInvite = (
    <div
      data-testid="queue-empty-invite"
      className="flex flex-col items-center gap-2 rounded-[var(--radius-lg)] border border-dashed border-border px-4 py-8 text-center text-sm text-fg-muted"
    >
      <p>Paste a video link above to queue a download</p>
      <Button
        data-testid="queue-empty-invite-action"
        variant="secondary"
        size="sm"
        type="button"
        onClick={() => {
          const field = document.querySelector('[data-testid="url-input"]')
          if (field instanceof HTMLElement) {
            field.focus()
          }
        }}
      >
        Paste a link
      </Button>
    </div>
  )

  const paused = processorState === 'Paused'
  const hasFinished = items.some((item) => CLEAR_FINISHED_STATUSES.includes(item.status))

  // PAGE_STATE: the same expressions the queue toolbar and cancel control use.
  usePublishCommandState('/', {
    'download:start': controlEnabled('start', ctx) && !busy,
    'download:pause': !paused && controlEnabled('pause', ctx) && !busy,
    'download:resume': paused && controlEnabled('resume', ctx) && !busy,
    'download:cancel': controlEnabled('cancel', ctx) && !busy,
    'download:clear': controlEnabled('clear-all', ctx) && !busy,
  })

  return (
    <section data-testid="downloader-page" className="flex h-full min-h-0 flex-col gap-4 p-4">
      {/*
        QUEUE_SCROLL_CONTAINER_RULE. This column is oversubscribed at the app's
        own 1280x800 default window, so one pane has to yield the deficit. It is
        this one, not the queue: a queue shorter than two rows puts every
        keyboard target in the bottom half of its own scroller, and there
        KeyboardSensor scrolls instead of moving the row.
      */}
      <div className="flex min-h-0 flex-col gap-4 overflow-auto">
      <HelpCard feature="downloader" tabKey="main" sections={DOWNLOADER_HELP_SECTIONS} />
      <form
        className="flex w-full max-w-[var(--layout-page-max-width)] flex-col gap-3"
        onSubmit={(event) => {
          event.preventDefault()
          addFromForm()
        }}
      >
        <div className="flex flex-wrap items-end gap-2">
        <label className="flex min-w-64 flex-1 flex-col gap-1">
          URL
          <input
            data-testid="url-input"
            title="URL (Ctrl+L)"
            aria-keyshortcuts={ariaKeyshortcuts('Ctrl+L')}
            className="h-9 rounded-md border border-border bg-bg-elevated px-2 py-1"
            value={url}
            onChange={(event) => {
              setUrl(event.target.value)
            }}
          />
        </label>
        <Button
          data-testid="add-btn"
          variant="primary"
          size="md"
          type="submit"
          title="Add (Ctrl+Enter)"
          aria-keyshortcuts={ariaKeyshortcuts('Ctrl+Enter')}
          loading={adding}
        >
          Add
        </Button>
        </div>
        <div className="flex flex-wrap items-end gap-4">
        <label className="flex flex-col gap-1">
          Quality
          <select
            data-testid="quality-select"
            style={{ ...SELECT_THEME_STYLE }}
            value={quality}
            onChange={(event) => {
              setQuality(event.target.value as QualityWire)
            }}
          >
            {qualities.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>
        {sabrActive ? (
          <StatusChip label="SABR active — quality limited to 360p" tone="warning" testId="sabr-quality-chip" />
        ) : null}
        <label className="flex items-center gap-2">
          <input
            data-testid="audio-only"
            type="checkbox"
            checked={audioOnly}
            onChange={(event) => {
              setAudioOnly(event.target.checked)
            }}
          />
          Audio Only
        </label>
        {audioFormatVisible(audioOnly) ? (
          <label className="flex flex-col gap-1">
            Audio format
            <select
              data-testid="audio-format"
              style={{ ...SELECT_THEME_STYLE }}
              value={audioFormat}
              onChange={(event) => {
                setAudioFormat(event.target.value as AudioWire)
              }}
            >
              {audios.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
        ) : (
          <select data-testid="audio-format" hidden style={{ ...SELECT_THEME_STYLE }} value={audioFormat} disabled aria-hidden>
            {audios.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        )}
        </div>
        <Disclosure
          id="downloader-add-advanced"
          title="Advanced"
          testId="add-advanced-toggle"
          open={advancedOpen}
          onOpenChange={(open) => {
            advancedTouched.current = true
            setAdvancedOpen(open)
          }}
          className="border-t border-border pt-2"
        >
        <div className="flex flex-col gap-3 pt-2">
        {/* SABR_SHOWN (D-635): the last result is always shown; no separate Checking line. */}
        <div data-testid="sabr-status" className="text-sm text-fg-muted">
          {sabrResultText(sabrQuery.data)}
        </div>
        <div className="flex flex-wrap gap-2">
          <Button data-testid="sabr-check-btn" variant="secondary" size="sm" loading={busy} onClick={() => void run(checkSabr)}>
            Check SABR
          </Button>
          <Button data-testid="sabr-force-btn" variant="secondary" size="sm" loading={busy} onClick={() => void run(forceSabr)}>
            Force SABR
          </Button>
          <Button data-testid="sabr-clear-btn" variant="secondary" size="sm" loading={busy} onClick={() => void run(clearSabr)}>
            Clear SABR
          </Button>
        </div>
        <SegmentedControl
          name="Cookie Authentication"
          value={cookieMode}
          options={COOKIE_MODES.map((mode) => ({
            id: `download-cookie-${mode}`,
            testId: `cookie-mode-${mode}`,
            value: mode,
            label: mode === 'none' ? 'None' : mode === 'browser' ? 'Browser' : 'File',
          }))}
          onValueChange={(value) => {
            const mode = COOKIE_MODES.find((entry) => entry === value)
            if (mode === undefined) return
            cookieSettingsTouched.current = true
            setCookieMode(mode)
            void run(async () => {
              await persistCookies({
                cookie_mode: mode,
                cookie_browser: cookieBrowser,
                cookie_browser_profile: cookieProfile,
                cookie_file_path: cookieFile,
              })
            })
          }}
        />
        <label className="flex flex-col gap-1" hidden={!cookieBrowserVisible(cookieMode)}>
          Browser
          <select
            data-testid="cookie-browser"
            style={{ ...SELECT_THEME_STYLE }}
            value={cookieBrowser}
            onChange={(event) => {
              const next = event.target.value as (typeof COOKIE_BROWSERS)[number]
              cookieSettingsTouched.current = true
              setCookieBrowser(next)
              void run(async () => {
                await persistCookies({
                  cookie_mode: cookieMode,
                  cookie_browser: next,
                  cookie_browser_profile: cookieProfile,
                  cookie_file_path: cookieFile,
                })
              })
            }}
          >
            {COOKIE_BROWSERS.map((browser) => (
              <option key={browser} value={browser}>
                {browser}
              </option>
            ))}
          </select>
        </label>
        <input
          data-testid="cookie-profile"
          hidden={!cookieBrowserVisible(cookieMode)}
          className="rounded-md border border-border bg-bg-elevated px-2 py-1"
          value={cookieProfile}
          onChange={(event) => {
            cookieSettingsTouched.current = true
            setCookieProfile(event.target.value)
          }}
          onBlur={() => {
            void run(async () => {
              await persistCookies({
                cookie_mode: cookieMode,
                cookie_browser: cookieBrowser,
                cookie_browser_profile: cookieProfile,
                cookie_file_path: cookieFile,
              })
            })
          }}
        />
        <div hidden={!cookieFileVisible(cookieMode)} className="flex gap-2">
          <input
            data-testid="cookie-file"
            className="flex-1 rounded-md border border-border bg-bg-elevated px-2 py-1"
            value={cookieFile}
            readOnly
          />
          <Button
            variant="secondary"
            size="sm"
            onClick={() => {
              void run(async () => {
                const picked = await window.api.showFileDialog([{ name: 'Cookies', extensions: ['txt'] }])
                if (!picked) {
                  return
                }
                cookieSettingsTouched.current = true
                setCookieFile(picked)
                await persistCookies({
                  cookie_mode: cookieMode,
                  cookie_browser: cookieBrowser,
                  cookie_browser_profile: cookieProfile,
                  cookie_file_path: picked,
                })
              })
            }}
          >
            Browse
          </Button>
        </div>
        <Button
          data-testid="cookie-test-btn"
          variant="secondary"
          size="sm"
          onClick={() => {
            void run(async () => {
              const body =
                cookieMode === 'browser'
                  ? cookieTestBody({ mode: cookieMode, browser: cookieBrowser, profile: cookieProfile })
                  : cookieMode === 'file'
                    ? cookieTestBody({ mode: cookieMode, cookie_file: cookieFile })
                    : cookieTestBody({ mode: cookieMode })
              await apiFetch('/downloads/cookies/test', { method: 'POST', body: JSON.stringify(body) })
            })
          }}
        >
          Test Cookies
        </Button>
        </div>
        </Disclosure>
      </form>

      <div className="min-h-6 max-w-[var(--layout-page-max-width)]">
      {addStatus ? (
        <p data-testid="add-status" className="text-fg-muted">
          {addStatus}
        </p>
      ) : (
        <p data-testid="add-status" hidden />
      )}
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
        region -- never a floating viewport-bottom bar. The region also owns the
        Ctrl/Cmd+A chord, so select-all works from a focused card without taking
        the shortcut away from the URL field above.
      */}
      <div
        className="flex min-h-[20rem] flex-1 flex-col gap-2"
        data-testid="download-queue-region"
        onKeyDown={bulk.onKeyDown}
      >
        <QueueHeaderRow
          total={cards.length}
          selectedCount={bulk.selection.count}
          onToggleAll={bulk.onToggleAll}
          selectionAriaLabel="Select all downloads"
          statuses={JOB_STATUSES}
          counts={summary}
          summaryTestId="queue-summary"
          processorTestId="processor-indicator"
          processorLabel={label}
          toolbar={{
            label: 'Download queue actions',
            processorState,
            canStart: controlEnabled('start', ctx) && !busy,
            canPauseResume: (paused ? controlEnabled('resume', ctx) : controlEnabled('pause', ctx)) && !busy,
            canClearFinished: hasFinished && !busy,
            canClearAll: controlEnabled('clear-all', ctx) && !busy,
            onStart: () => { void run(startDownload) },
            onPauseResume: () => { void run(paused ? resumeDownload : pauseDownload) },
            onClearFinished: bulk.clearFinishedNow,
            onClearAll: () => { setConfirm({ kind: 'clear' }) },
          }}
        />
        <BulkActionBar
          selectedStatuses={bulk.selectedStatuses}
          requeueableStatuses={DOWNLOAD_REQUEUEABLE_STATUSES}
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
        items={cards}
        queueKey={DOWNLOAD_QUEUE_KEY}
        onMoveToIndex={reorderToIndex}
        inFlightId={queue.data?.processor.current_job_id ?? null}
        requeueableStatuses={DOWNLOAD_REQUEUEABLE_STATUSES}
        metaSegments={metaSegmentsFor}
        selectable
        selectedIds={bulk.selection.selectedIds}
        onSelectChange={bulk.onSelectChange}
        emptyState={emptyInvite}
        onOpen={setSelectedId}
        onRetry={(id) => {
          void run(async () => {
            await resetDownload(id)
          })
        }}
        onCancelQueue={() => {
          void run(cancelDownload)
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
              await removeDownload(pending.id)
              return
            }
            if (pending.kind === 'cancel') {
              await cancelDownload()
              return
            }
            await clearDownloads()
          })
        }}
        onCancel={() => {
          setConfirm(null)
        }}
      />
    </section>
  )
}
