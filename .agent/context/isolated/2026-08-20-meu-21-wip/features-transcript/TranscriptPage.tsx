import { useQuery } from '@tanstack/react-query'
import { useEffect, useMemo, useState } from 'react'
import { createPortal } from 'react-dom'

import { Button } from '../../components/ui/Button'
import { ApiError, apiFetch } from '../../lib/api'
import { queryClient } from '../../lib/query-client'
import { outputTreeLabels } from './output-tree'
import { formatRateEta } from './rate-eta'
import {
  actionVisible,
  buildReorderBody,
  controlEnabled,
  JOB_STATUSES,
  processorLabel,
  STATUS_COLORS,
  type JobStatus,
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

function asProcessor(state: string | undefined): ProcessorState {
  if (state === 'Processing' || state === 'Paused') {
    return state
  }
  return 'Idle'
}

function asJobStatus(status: string): JobStatus {
  if ((JOB_STATUSES as readonly string[]).includes(status)) {
    return status as JobStatus
  }
  return 'Pending'
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
  const selected = items.find((item) => item.id === selectedId)

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
        const message = caught instanceof ApiError || caught instanceof Error ? caught.message : String(caught)
        setError(message)
      })
      .finally(() => {
        setAdding(false)
      })
  }

  return (
    <div className="flex flex-col gap-4 p-4" data-testid="transcript-page">
      <label className="flex flex-col gap-1">
        <span>Channel URL</span>
        <input
          data-testid="channel-input"
          className="h-9 rounded-[var(--radius-control)] border border-border bg-bg px-3"
          value={channelUrl}
          onChange={(event) => {
            setChannelUrl(event.target.value)
          }}
        />
      </label>
      <p data-testid="channel-url-hint" className="text-sm text-fg-muted">
        Accepts: /@handle, /c/name, /channel/UCxxx, /user/name
      </p>
      <Button
        data-testid="add-btn"
        variant="primary"
        size="md"
        loading={adding}
        disabled={channelUrl.trim().length < 1 || adding}
        onClick={() => {
          addFromForm()
        }}
      >
        Add
      </Button>

      {error ? (
        <p data-testid="error-banner" className="text-error" role="alert">
          {error}
        </p>
      ) : (
        <p data-testid="error-banner" hidden className="text-error" />
      )}

      <div className="flex flex-col gap-3">
        {items.map((item) => (
          <ChannelCard
            key={item.id}
            item={item}
            selected={item.id === selectedId}
            delay={delay}
            onSelect={() => {
              setSelectedId(item.id)
            }}
          />
        ))}
      </div>

      <div data-testid="processor-indicator" hidden={label === null}>
        {label}
      </div>

      <div className="flex flex-wrap gap-2">
        <Button
          data-testid="start-btn"
          variant="primary"
          disabled={!controlEnabled('start', ctx) || busy}
          onClick={() => void run(startTranscripts)}
        >
          Start
        </Button>
        <Button
          data-testid="pause-btn"
          variant="secondary"
          disabled={!controlEnabled('pause', ctx) || busy}
          onClick={() => void run(pauseTranscripts)}
        >
          Pause
        </Button>
        <Button
          data-testid="resume-btn"
          variant="secondary"
          disabled={!controlEnabled('resume', ctx) || busy}
          onClick={() => void run(resumeTranscripts)}
        >
          Resume
        </Button>
        <Button
          data-testid="stop-btn"
          variant="secondary"
          disabled={!controlEnabled('stop', ctx) || busy}
          onClick={() => void run(stopTranscripts)}
        >
          Stop
        </Button>
        <Button
          data-testid="up-btn"
          variant="secondary"
          size="sm"
          disabled={!controlEnabled('up', ctx) || busy}
          onClick={() => {
            if (selectedId === null) {
              return
            }
            void run(async () => {
              await apiFetch('/transcripts/reorder', {
                method: 'PUT',
                body: JSON.stringify(buildReorderBody(items.map((item) => item.id), selectedId, 'up')),
              })
              await queryClient.invalidateQueries({ queryKey: QUERY_KEY })
            })
          }}
        >
          Up
        </Button>
        <Button
          data-testid="down-btn"
          variant="secondary"
          size="sm"
          disabled={!controlEnabled('down', ctx) || busy}
          onClick={() => {
            if (selectedId === null) {
              return
            }
            void run(async () => {
              await apiFetch('/transcripts/reorder', {
                method: 'PUT',
                body: JSON.stringify(buildReorderBody(items.map((item) => item.id), selectedId, 'down')),
              })
              await queryClient.invalidateQueries({ queryKey: QUERY_KEY })
            })
          }}
        >
          Down
        </Button>
        <Button
          data-testid="compile-btn"
          variant="secondary"
          size="sm"
          disabled={!controlEnabled('compile', ctx) || busy}
          onClick={() => {
            if (selectedId === null) {
              return
            }
            void run(async () => {
              const compiled = await compileTranscript(selectedId)
              const first = compiled.compiled_paths[0]
              if (first) {
                setCompiledById((current) => ({ ...current, [selectedId]: first }))
              }
            })
          }}
        >
          Compile
        </Button>
        <Button
          data-testid="view-compiled-btn"
          variant="ghost"
          size="sm"
          disabled={!controlEnabled('view-compiled', ctx) || busy}
          onClick={() => {
            const path = selected?.compiled_path
            if (!path) {
              return
            }
            void run(async () => {
              await openCompiled(path)
            })
          }}
        >
          View Compiled
        </Button>
        <Button
          data-testid="open-zip-btn"
          variant="ghost"
          size="sm"
          disabled={!controlEnabled('open-zip', ctx) || busy}
          onClick={() => {
            const path = selected?.zip_path
            if (!path) {
              return
            }
            void run(async () => {
              await openZip(path)
            })
          }}
        >
          Open ZIP
        </Button>
        <Button
          data-testid="open-folder-btn"
          variant="ghost"
          size="sm"
          disabled={!controlEnabled('open-folder', ctx) || busy}
          onClick={() => {
            const path = selected?.output_dir
            if (!path) {
              return
            }
            void run(async () => {
              await openFolder(path)
            })
          }}
        >
          Open Folder
        </Button>
        {selected && actionVisible('requeue', selected.status) ? (
          <Button
            data-testid="requeue-btn"
            variant="secondary"
            size="sm"
            disabled={busy}
            onClick={() => {
              void run(async () => {
                await requeueTranscript(selected.id)
              })
            }}
          >
            Requeue
          </Button>
        ) : null}
        {selected && actionVisible('retry', selected.status) ? (
          <Button
            data-testid="retry-btn"
            variant="secondary"
            size="sm"
            disabled={busy}
            onClick={() => {
              void run(async () => {
                await retryTranscript(selected.id)
              })
            }}
          >
            Retry
          </Button>
        ) : null}
        <Button
          data-testid="remove-btn"
          variant="destructive"
          size="sm"
          disabled={!controlEnabled('remove', ctx) || busy}
          onClick={() => {
            if (selectedId === null) {
              return
            }
            setConfirmOpen(true)
          }}
        >
          Remove
        </Button>
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
    </div>
  )
}

function ChannelCard({
  item,
  selected,
  delay,
  onSelect,
}: {
  item: TranscriptListItem
  selected: boolean
  delay: number | undefined
  onSelect: () => void
}) {
  const tree = outputTreeLabels(item.output_dir)
  const rate = formatRateEta({
    delay: delay ?? Number.NaN,
    videoCount: item.video_count,
    transcriptsDone: item.transcripts_done,
  })
  const status = asJobStatus(item.status)
  const percent =
    item.video_count > 0 ? Math.round((item.transcripts_done / item.video_count) * 1000) / 10 : 0
  return (
    <button
      type="button"
      data-testid="channel-card"
      className={`rounded-lg border p-3 text-left ${selected ? 'border-accent' : 'border-border'}`}
      onClick={onSelect}
    >
      <div className="flex items-center gap-2">
        <span className={`inline-block h-2 w-2 rounded-full ${STATUS_COLORS[status]}`} />
        <strong>{item.channel_name}</strong>
        <span>{item.status}</span>
      </div>
      <p>
        {item.video_count} videos · {item.transcripts_done}/{item.video_count} transcripts · {item.word_count} words
      </p>
      <p>Output: {item.output_dir}</p>
      {item.video_count > 0 ? (
        <div data-testid="channel-progress">
          <div className="h-2 bg-neutral/30">
            <div className="h-2 bg-accent" style={{ width: `${percent}%` }} />
          </div>
        </div>
      ) : null}
      {rate ? (
        <>
          <p data-testid="rate-display">{rate.rate}</p>
          <p data-testid="eta-display">ETA {rate.etaSeconds}s</p>
        </>
      ) : null}
      {item.last_title ? (
        <p data-testid="last-title">
          Last: {item.last_title} {item.last_item_status ?? ''}
        </p>
      ) : null}
      <div data-testid="output-tree">
        <div>{tree.raw}</div>
        <div>{tree.compiled}</div>
      </div>
    </button>
  )
}
