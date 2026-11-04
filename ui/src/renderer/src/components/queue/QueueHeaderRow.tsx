import { useState, type ReactElement, type ReactNode } from 'react'

import { StatusChip, type StatusChipTone } from '../ui/StatusChip'
import { QueueSelectionHeader } from './QueueSelectionHeader'
import { QueueToolbar, type QueueToolbarProps } from './QueueToolbar'

export type QueueHeaderRowProps = {
  total: number
  selectedCount: number
  onToggleAll: (checked: boolean) => void
  selectionAriaLabel: string
  statuses: readonly string[]
  counts: Readonly<Record<string, number>>
  summaryTestId: string
  processorTestId: string
  processorLabel: string | null
  toolbar: QueueToolbarProps
}

/**
 * `HEADER_FRAME` — the queue header anatomy without any page's controls.
 *
 * It owns the row layout, the optional title, the nonzero status chips with
 * their read-only More summary, the live processor chip, and an optional slot
 * for extra chips. The page supplies `leading` (the select-all header, when the
 * queue is multi-select) and `actions` (its toolbar). Transcript mounts it with
 * no `leading` because that queue is single-select (TR6), and with its own
 * three-action toolbar because it has no Clear finished mutation (TR1).
 */
export type QueueHeaderFrameProps = {
  title?: string
  leading?: ReactNode
  statuses: readonly string[]
  counts: Readonly<Record<string, number>>
  summaryTestId: string
  processorTestId: string
  processorLabel: string | null
  extraChips?: ReactNode
  actions: ReactNode
}

function toneFor(status: string): StatusChipTone {
  if (status === 'Done') return 'success'
  if (status === 'Failed' || status === 'AgeRestricted') return 'danger'
  if (status === 'Downloading' || status === 'Processing') return 'info'
  if (status === 'Pending' || status === 'QualityBlocked') return 'warning'
  return 'neutral'
}

/** One queue chrome row; see {@link QueueHeaderFrameProps}. */
export function QueueHeaderFrame({
  title,
  leading,
  statuses,
  counts,
  summaryTestId,
  processorTestId,
  processorLabel,
  extraChips,
  actions,
}: QueueHeaderFrameProps): ReactElement {
  const [moreOpen, setMoreOpen] = useState(false)

  return (
    <div data-testid="queue-header-row" className="flex flex-wrap items-center gap-x-4 gap-y-2">
      {title !== undefined ? <h2 className="text-sm font-semibold text-fg">{title}</h2> : null}
      {leading}
      <div className="flex flex-wrap items-center gap-2" data-testid={summaryTestId}>
        {statuses.filter((status) => (counts[status] ?? 0) > 0).map((status) => (
          <StatusChip key={status} label={status} count={counts[status]} tone={toneFor(status)} />
        ))}
        <div className="relative">
          <button
            type="button"
            data-testid="queue-status-more"
            aria-expanded={moreOpen}
            aria-label="Show all queue status counts"
            className="rounded-[var(--radius-control)] px-2 py-1 text-xs text-fg-muted hover:bg-neutral/30 focus-visible:outline-none focus-visible:shadow-[0_0_0_3px_var(--color-accent-ring)]"
            onClick={() => setMoreOpen((open) => !open)}
          >
            More
          </button>
          {moreOpen ? (
            <div
              data-testid="queue-status-details"
              className="absolute left-0 top-full z-10 mt-1 min-w-44 rounded-[var(--radius-md)] border border-border bg-bg-elevated p-2 text-xs text-fg shadow-lg"
            >
              {statuses.map((status) => (
                <div key={status}>{`${status}: ${String(counts[status] ?? 0)}`}</div>
              ))}
            </div>
          ) : null}
        </div>
      </div>
      {processorLabel === null ? (
        <span data-testid={processorTestId} hidden />
      ) : (
        <StatusChip label={processorLabel} tone="info" testId={processorTestId} />
      )}
      {extraChips}
      {actions}
    </div>
  )
}

/** One queue chrome row shared by downloader and converter. */
export function QueueHeaderRow({
  total,
  selectedCount,
  onToggleAll,
  selectionAriaLabel,
  statuses,
  counts,
  summaryTestId,
  processorTestId,
  processorLabel,
  toolbar,
}: QueueHeaderRowProps): ReactElement {
  return (
    <QueueHeaderFrame
      leading={
        <QueueSelectionHeader
          total={total}
          selectedCount={selectedCount}
          onToggleAll={onToggleAll}
          ariaLabel={selectionAriaLabel}
        />
      }
      statuses={statuses}
      counts={counts}
      summaryTestId={summaryTestId}
      processorTestId={processorTestId}
      processorLabel={processorLabel}
      actions={<QueueToolbar {...toolbar} />}
    />
  )
}
