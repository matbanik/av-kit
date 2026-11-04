import { useQuery } from '@tanstack/react-query'
import { ChevronDown, ChevronUp } from 'lucide-react'
import { useEffect, useMemo, useRef, useState, type ReactElement } from 'react'
import { createPortal } from 'react-dom'

import { QueueHeaderFrame } from '../../components/queue/QueueHeaderRow'
import type { QueueCardSlots } from '../../components/queue/QueueCard'
import type { QueueMenuItem } from '../../components/queue/QueueCardMenu'
import { QueueList } from '../../components/queue/QueueList'
import { Button } from '../../components/ui/Button'
import { ProgressBar } from '../../components/ui/ProgressBar'
import { StatusChip } from '../../components/ui/StatusChip'
import { Tooltip } from '../../components/ui/Tooltip'
import { HelpCard } from '../../components/help/HelpCard'
import { ApiError, apiFetch } from '../../lib/api'
import { queryClient } from '../../lib/query-client'
import { usePublishCommandState } from '../../registry/command-state'
import { ariaKeyshortcuts } from '../../registry/shortcuts'
import { outputTreeLabels } from './output-tree'
import { formatRateEta } from './rate-eta'
import {
  asJobStatus,
  CARD_ACTION_TESTIDS,
  CARD_LINK_TESTIDS,
  cardActionAvailable,
  cardLinkActions,
  cardMenuActions,
  channelRatio,
  statusCounts,
  toQueueCardJob,
  type TranscriptCardAction,
} from './transcript-card'
import {
  buildReorderBody,
  controlEnabled,
  JOB_STATUSES,
  processorLabel,
  type ProcessorState,
} from './transcript-controls'
import {
  compileTranscript,
  openCompiled,
  openFolder,
  openZip,
  pauseTranscripts,
  postTranscriptCreate,
  removeTranscript,
  requeueTranscript,
  resumeTranscripts,
  retryTranscript,
  startTranscripts,
  stopTranscripts,
} from './transcript-commands'
import { TRANSCRIPT_HELP_SECTIONS } from './transcript-help-content'
import { TranscriptToolbar } from './TranscriptToolbar'
import { QUERY_KEY, useTranscriptQueue, type TranscriptListItem } from './useTranscriptQueue'

export const TRANSCRIPT_TEST_IDS = [
  'transcript-page',
  'channel-input',
  'channel-card',
  'compile-btn',
  'channel-progress',
  'add-btn',
  'start-btn',
  'pause-btn',
  'resume-btn',
  'stop-btn',
  'up-btn',
  'down-btn',
  'remove-btn',
  'requeue-btn',
  'retry-btn',
  'view-compiled-btn',
  'open-zip-btn',
  'open-folder-btn',
  'processor-indicator',
  'output-tree',
  'rate-display',
  'eta-display',
  'last-title',
  'channel-url-hint',
  'remove-confirm-btn',
  'remove-confirm-cancel',
  'error-banner',
] as const

const TRANSCRIPT_ERROR_EVENT = 'av-kit:transcript:error'

/** Visible and accessible labels for each per-card action. */
const ACTION_LABELS: Readonly<Record<TranscriptCardAction, string>> = {
  requeue: 'Requeue',
  retry: 'Retry',
  compile: 'Compile',
  'view-compiled': 'View compiled',
  'open-zip': 'Open ZIP',
  'open-folder': 'Open folder',
  remove: 'Remove…',
}

type Direction = 'up' | 'down'

function asProcessor(state: string | undefined): ProcessorState {
  if (state === 'Processing' || state === 'Paused') {
    return state
  }
  return 'Idle'
}

function errorMessage(caught: unknown): string {
  return caught instanceof ApiError || caught instanceof Error ? caught.message : String(caught)
}

/**
 * Line 3 of a card (TR5): the last title on the Processing card, otherwise the
 * output root with both full raw/compiled paths kept in accessible text.
 */
function CardDetail({ item }: { item: TranscriptListItem }): ReactElement {
  if (asJobStatus(item.status) === 'Processing' && item.last_title) {
    return (
      <span data-testid="last-title">
        {[`Last: ${item.last_title}`, item.last_item_status].filter((part) => part).join(' ')}
      </span>
    )
  }
  const tree = outputTreeLabels(item.output_dir)
  const root = item.output_dir.replace(/[\\/]+$/, '')
  return (
    <span data-testid="output-tree" title={`raw: ${tree.raw}\ncompiled: ${tree.compiled}`}>
      {`${root} · raw · compiled`}
      <span className="sr-only">{` (raw: ${tree.raw}; compiled: ${tree.compiled})`}</span>
    </span>
  )
}

export function TranscriptPage() {
  const queue = useTranscriptQueue()
  const settingsQuery = useQuery({
    queryKey: ['settings', 'transcript'],
    queryFn: async () => apiFetch<{ delay_between_requests?: number }>('/settings/transcript'),
  })
  const [channelUrl, setChannelUrl] = useState('')
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [adding, setAdding] = useState(false)
  const [busy, setBusy] = useState(false)
  const [confirmOpen, setConfirmOpen] = useState(false)
  const [compiledById, setCompiledById] = useState<Record<string, string>>({})
  const inputRef = useRef<HTMLInputElement | null>(null)
  const scrollerRef = useRef<HTMLDivElement | null>(null)
  const pendingFocus = useRef<{ id: string; dir: Direction } | null>(null)

  const items = useMemo(
    () =>
      (queue.data?.items ?? []).map((item) => ({
        ...item,
        compiled_path: item.compiled_path ?? compiledById[item.id] ?? null,
      })),
    [compiledById, queue.data?.items],
  )
  const processorState = asProcessor(queue.data?.processor.state)
  const delay = settingsQuery.data?.delay_between_requests
  const label = processorLabel(processorState)
  const ctx = { items, selectedId, processorState }
  const cardCtx = { items, processorState }
  // PAGE_STATE: the same expressions the transcript toolbar uses.
  usePublishCommandState('/transcript', {
    'transcript:start': controlEnabled('start', ctx) && !busy,
    'transcript:pause': controlEnabled('pause', ctx) && !busy,
    'transcript:resume': controlEnabled('resume', ctx) && !busy,
    'transcript:stop': controlEnabled('stop', ctx) && !busy,
  })
  const counts = useMemo(() => statusCounts(items), [items])
  const rateFor = (item: TranscriptListItem) =>
    formatRateEta({
      delay: delay ?? Number.NaN,
      videoCount: item.video_count,
      transcriptsDone: item.transcripts_done,
    })
  const processingItem = items.find((item) => asJobStatus(item.status) === 'Processing')
  const headerRate = processorState === 'Processing' && processingItem ? rateFor(processingItem) : null

  useEffect(() => {
    const onError = (event: Event) => {
      const detail = (event as CustomEvent<string>).detail
      setError(detail)
    }
    window.addEventListener(TRANSCRIPT_ERROR_EVENT, onError)
    return () => {
      window.removeEventListener(TRANSCRIPT_ERROR_EVENT, onError)
    }
  }, [])

  useEffect(() => {
    if (selectedId !== null && !items.some((item) => item.id === selectedId)) {
      setSelectedId(items[0]?.id ?? null)
    }
  }, [items, selectedId])

  useEffect(() => {
    if (!confirmOpen) {
      return
    }
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault()
        setConfirmOpen(false)
      }
    }
    window.addEventListener('keydown', onKey)
    return () => {
      window.removeEventListener('keydown', onKey)
    }
  }, [confirmOpen])

  /*
    After a ▲ ▼ reorder settles — whether it landed or was rejected — focus
    returns to that card. While the command is in flight every per-card control
    is disabled, so the browser drops focus; the order may or may not have
    changed afterwards, but focus is lost either way, which is why there is no
    early return on an unchanged order (the Session 24 shared fallback in
    QueueList restores on success and rejection alike). The row is found by its
    data-job-id inside this page's own list root (Session 24 RULE-1). When the
    same-direction button is now disabled (the card reached an end), focus falls
    back to the other one.
  */
  useEffect(() => {
    const pending = pendingFocus.current
    if (pending === null || busy) {
      return
    }
    pendingFocus.current = null
    const card = Array.from(scrollerRef.current?.querySelectorAll<HTMLElement>('[data-job-id]') ?? []).find(
      (node) => node.getAttribute('data-job-id') === pending.id,
    )
    const button = (dir: Direction): HTMLButtonElement | null =>
      card?.querySelector<HTMLButtonElement>(`[data-testid="${dir}-btn"]`) ?? null
    const same = button(pending.dir)
    const other = button(pending.dir === 'up' ? 'down' : 'up')
    const target = same !== null && !same.disabled ? same : other !== null && !other.disabled ? other : null
    target?.focus()
  }, [items, busy])

  async function run(work: () => Promise<void>): Promise<void> {
    setBusy(true)
    setError(null)
    try {
      await work()
    } catch (caught) {
      setError(errorMessage(caught))
    } finally {
      setBusy(false)
    }
  }

  function addFromForm(): void {
    const field = document.querySelector('[data-testid="channel-input"]')
    const submitted = field instanceof HTMLInputElement ? field.value : channelUrl
    if (submitted.trim().length < 1) {
      return
    }
    setAdding(true)
    setError(null)
    void postTranscriptCreate(submitted)
      .then(() => {
        setChannelUrl('')
      })
      .catch((caught: unknown) => {
        setError(errorMessage(caught))
      })
      .finally(() => {
        setAdding(false)
      })
  }

  function reorder(item: TranscriptListItem, dir: Direction): void {
    setSelectedId(item.id)
    pendingFocus.current = { id: item.id, dir }
    void run(async () => {
      await apiFetch('/transcripts/reorder', {
        method: 'PUT',
        body: JSON.stringify(buildReorderBody(items.map((row) => row.id), item.id, dir)),
      })
      await queryClient.invalidateQueries({ queryKey: QUERY_KEY })
    })
  }

  /** `CARD_TARGET_RULE`: every per-card action selects its card and acts on it. */
  function runCardAction(item: TranscriptListItem, action: TranscriptCardAction): void {
    setSelectedId(item.id)
    switch (action) {
      case 'compile':
        void run(async () => {
          const compiled = await compileTranscript(item.id)
          const first = compiled.compiled_paths[0]
          if (first) {
            setCompiledById((current) => ({ ...current, [item.id]: first }))
          }
        })
        return
      case 'view-compiled': {
        const path = item.compiled_path
        if (path) {
          void run(async () => {
            await openCompiled(path)
          })
        }
        return
      }
      case 'open-zip': {
        const path = item.zip_path
        if (path) {
          void run(async () => {
            await openZip(path)
          })
        }
        return
      }
      case 'open-folder':
        void run(async () => {
          await openFolder(item.output_dir)
        })
        return
      case 'requeue':
        void run(async () => {
          await requeueTranscript(item.id)
        })
        return
      case 'retry':
        void run(async () => {
          await retryTranscript(item.id)
        })
        return
      case 'remove':
        setConfirmOpen(true)
        return
      default: {
        const unreachable: never = action
        throw new Error(`unhandled transcript card action ${String(unreachable)}`)
      }
    }
  }

  function cardSlots(job: { id: string }): QueueCardSlots {
    const item = items.find((row) => row.id === job.id)
    if (item === undefined) {
      return {}
    }
    const status = asJobStatus(item.status)
    const ratio = channelRatio(item)
    const rate = status === 'Processing' ? rateFor(item) : null
    const menuItems: QueueMenuItem<TranscriptCardAction>[] = cardMenuActions(item, cardCtx).map((action) => ({
      id: action,
      label: action === 'compile' ? `Compile (${String(item.transcripts_done)} done)` : ACTION_LABELS[action],
      destructive: action === 'remove',
      disabled: busy,
      testId: CARD_ACTION_TESTIDS[action],
      run: () => {
        runCardAction(item, action)
      },
    }))
    return {
      regionLabel: `Select channel ${item.channel_name}`,
      metaContent: (
        <>
          <span>{`${String(item.transcripts_done)} / ${String(item.video_count)} transcripts · ${String(item.word_count)} words`}</span>
          {ratio !== null && status !== 'Failed' ? (
            <span className="w-28 shrink-0">
              <ProgressBar
                testId="channel-progress"
                value={ratio}
                tone={status === 'Done' ? 'success' : 'accent'}
                ariaLabel={`Transcript progress for ${item.channel_name}`}
              />
            </span>
          ) : null}
          {rate ? (
            <>
              <span data-testid="rate-display">{rate.rate}</span>
              <span data-testid="eta-display">{`ETA ${String(rate.etaSeconds)}s`}</span>
            </>
          ) : null}
        </>
      ),
      detailContent: <CardDetail item={item} />,
      trailingControls: (
        <>
          {cardLinkActions(item, cardCtx).map((action) => (
            <Button
              key={action}
              data-testid={CARD_LINK_TESTIDS[action]}
              variant="ghost"
              size="sm"
              disabled={busy}
              onClick={() => {
                runCardAction(item, action)
              }}
            >
              {ACTION_LABELS[action]}
            </Button>
          ))}
          <Tooltip
            id="up-btn"
            label={`Move ${item.channel_name} up`}
            disabled={busy || !cardActionAvailable('up', item, cardCtx)}
          >
            <Button
              data-testid="up-btn"
              variant="ghost"
              size="sm"
              icon
              aria-label={`Move ${item.channel_name} up`}
              disabled={busy || !cardActionAvailable('up', item, cardCtx)}
              onClick={() => {
                reorder(item, 'up')
              }}
            >
              <ChevronUp className="h-4 w-4" aria-hidden="true" />
            </Button>
          </Tooltip>
          <Tooltip
            id="down-btn"
            label={`Move ${item.channel_name} down`}
            disabled={busy || !cardActionAvailable('down', item, cardCtx)}
          >
            <Button
              data-testid="down-btn"
              variant="ghost"
              size="sm"
              icon
              aria-label={`Move ${item.channel_name} down`}
              disabled={busy || !cardActionAvailable('down', item, cardCtx)}
              onClick={() => {
                reorder(item, 'down')
              }}
            >
              <ChevronDown className="h-4 w-4" aria-hidden="true" />
            </Button>
          </Tooltip>
        </>
      ),
      menuItems,
      onMenuOpen: () => {
        setSelectedId(item.id)
      },
    }
  }

  return (
    <section className="flex h-full min-h-0 flex-col gap-4 p-4" data-testid="transcript-page">
      {/*
        QUEUE_SCROLL_CONTAINER_RULE: this controls pane yields the column's height
        deficit, so the queue region below keeps at least 20rem.
      */}
      <div className="flex min-h-0 flex-col gap-4 overflow-auto">
        <HelpCard feature="transcript" tabKey="main" sections={TRANSCRIPT_HELP_SECTIONS} />
        <div className="flex w-full max-w-[var(--layout-page-max-width)] flex-col gap-2">
          <div className="flex flex-wrap items-center gap-2">
            <input
              ref={inputRef}
              data-testid="channel-input"
              aria-label="Channel URL"
              title="Channel URL (Ctrl+L)"
              aria-keyshortcuts={ariaKeyshortcuts('Ctrl+L')}
              placeholder="Channel URL"
              className="h-9 min-w-64 flex-1 rounded-[var(--radius-control)] border border-border bg-bg px-3"
              value={channelUrl}
              onChange={(event) => {
                setChannelUrl(event.target.value)
              }}
            />
            <Button
              data-testid="add-btn"
              variant="primary"
              size="md"
              title="Add (Ctrl+Enter)"
              aria-keyshortcuts={ariaKeyshortcuts('Ctrl+Enter')}
              loading={adding}
              disabled={channelUrl.trim().length < 1 || adding}
              onClick={() => {
                addFromForm()
              }}
            >
              Add
            </Button>
          </div>
          <div className="min-h-6 text-sm">
            <p data-testid="channel-url-hint" className="text-fg-muted" hidden={error !== null}>
              Accepts: /@handle, /c/name, /channel/UCxxx, /user/name
            </p>
            {error ? (
              <p data-testid="error-banner" className="text-error" role="alert">
                {error}
              </p>
            ) : (
              <p data-testid="error-banner" hidden className="text-error" />
            )}
          </div>
        </div>
      </div>

      <div className="flex min-h-[20rem] w-full max-w-[var(--layout-page-max-width)] flex-1 flex-col gap-2">
        <QueueHeaderFrame
          title="Channels"
          statuses={JOB_STATUSES}
          counts={counts}
          summaryTestId="transcript-queue-summary"
          processorTestId="processor-indicator"
          processorLabel={label}
          extraChips={
            headerRate ? (
              <StatusChip
                testId="transcript-rate-chip"
                tone="info"
                label={`${headerRate.rate} · ETA ${String(headerRate.etaSeconds)}s`}
              />
            ) : null
          }
          actions={
            <TranscriptToolbar
              processorState={processorState}
              canStart={controlEnabled('start', ctx) && !busy}
              canPause={controlEnabled('pause', ctx) && !busy}
              canResume={controlEnabled('resume', ctx) && !busy}
              canStop={controlEnabled('stop', ctx) && !busy}
              onStart={() => void run(startTranscripts)}
              onPause={() => void run(pauseTranscripts)}
              onResume={() => void run(resumeTranscripts)}
              onStop={() => void run(stopTranscripts)}
            />
          }
        />
        {/*
          QUEUE_SCROLL_CONTAINER_RULE: overflow lives on this wrapper, never on the
          shared list, whose node is the containing block for its overlays.
        */}
        <div ref={scrollerRef} className="min-h-0 flex-1 overflow-auto">
          <QueueList
            items={items.map(toQueueCardJob)}
            rowTestId="channel-card"
            selectedIds={selectedId === null ? [] : [selectedId]}
            onOpen={(id) => {
              setSelectedId(id)
            }}
            cardSlots={cardSlots}
            emptyState={
              <div
                data-testid="transcript-empty-invite"
                className="flex flex-col items-start gap-2 rounded-[var(--radius-lg)] border border-dashed border-border p-4 text-sm text-fg-muted"
              >
                <p>Paste a channel link above to queue transcript extraction.</p>
                <Button
                  data-testid="transcript-empty-invite-action"
                  variant="secondary"
                  size="sm"
                  onClick={() => {
                    inputRef.current?.focus()
                  }}
                >
                  Paste a link
                </Button>
              </div>
            }
          />
        </div>
      </div>

      {confirmOpen
        ? createPortal(
            <div
              style={{
                position: 'fixed',
                inset: 0,
                zIndex: 9999,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: 'rgba(0,0,0,0.6)',
              }}
              onClick={() => {
                setConfirmOpen(false)
              }}
            >
              <div
                style={{
                  backgroundColor: 'var(--color-bg-elevated)',
                  border: '1px solid var(--color-border)',
                  borderRadius: '12px',
                  padding: '24px',
                  color: 'var(--color-fg)',
                }}
                onClick={(event) => {
                  event.stopPropagation()
                }}
              >
                <p>Remove this channel from the queue? Files stay on disk.</p>
                <div className="mt-4 flex gap-2">
                  <Button
                    data-testid="remove-confirm-btn"
                    variant="destructive"
                    size="sm"
                    onClick={() => {
                      if (selectedId === null) {
                        setConfirmOpen(false)
                        return
                      }
                      const id = selectedId
                      setConfirmOpen(false)
                      void run(async () => {
                        await removeTranscript(id)
                      })
                    }}
                  >
                    Confirm
                  </Button>
                  <Button
                    data-testid="remove-confirm-cancel"
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setConfirmOpen(false)
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            </div>,
            document.body,
          )
        : null}
    </section>
  )
}
