/**
 * The bulk action bar (`BULK_BAR_ACTIONS`, AC-47.4 / AC-47.5).
 *
 * `USER_LOCKS` places it STICKY ABOVE THE LIST inside the queue panel — never a
 * floating bar pinned to the viewport bottom, never inline per row. Sticking is
 * only meaningful because of where the page mounts it: it scrolls with the panel
 * until it reaches the top, so it is present without ever covering the last row.
 *
 * With no selection the bar is REMOVED from the tree rather than hidden. A bar
 * hidden by a class keeps its buttons focusable and its handlers reachable, so
 * Tab could still land on a Remove that acts on nothing.
 *
 * The action list is normative and complete: count, Retry, Move to top, Move to
 * bottom, Remove (destructive), spacer, Clear selection. There is deliberately
 * no bulk move-up/move-down — single-step reorder stays on the card kebab and
 * the keyboard path — and no bar-level select-all, which lives in
 * `QueueSelectionHeader` (`SELECTION_HEADER_CONTRACT`).
 */
import { ArrowDownToLine, ArrowUpToLine, RotateCcw, Trash2, X } from 'lucide-react'
import { type ReactElement } from 'react'

import { Button } from '../ui/Button'

export type BulkActionBarProps = {
  /** The statuses of the selected rows; its length is the selection count. */
  selectedStatuses: readonly string[]
  /**
   * The statuses this page allows a retry from — `CONVERT_REQUEUEABLE_STATUSES`
   * or `DOWNLOAD_REQUEUEABLE_STATUSES`. Passed in rather than hard-coded,
   * because the two queues genuinely differ and `USER_LOCKS` forbids `Skipped`
   * in either.
   */
  requeueableStatuses: readonly string[]
  /** Re-queue every selected row that the requeueable set admits. */
  onRetry: () => void
  /** Move the selection to the head of the queue. */
  onMoveTop: () => void
  /** Move the selection to the tail of the queue. */
  onMoveBottom: () => void
  /** Remove the selection, behind the confirm the page owns. */
  onRemove: () => void
  /** Drop the selection without touching the queue. */
  onClearSelection: () => void
  /**
   * Whether the page already has a mutation in flight.
   *
   * Every acting verb is disabled while it is set. A bulk fan-out is N requests
   * and a reorder fold is N DEPENDENT requests built from the order the last one
   * produced, so a second gesture launched mid-run would either duplicate the
   * per-id mutations or send an absolute permutation derived from an order the
   * server has already replaced — the two runs would then clobber each other.
   * `Clear selection` stays live: it touches no endpoint, and taking the escape
   * hatch away during a slow run is precisely when the user reaches for it.
   */
  busy?: boolean
}

const barClasses = [
  // `sticky top-0` inside the scrolling queue panel: it rides with the list and
  // parks at the panel's top edge.
  'sticky top-0 z-10 flex items-center gap-2 px-2 py-2',
  'rounded-[var(--radius-md)] border border-border bg-bg-elevated',
].join(' ')

const countClasses = 'px-1 text-sm font-medium text-accent'

const iconClasses = 'h-4 w-4'

/**
 * Render the bulk action bar for the current selection.
 *
 * @param props - See {@link BulkActionBarProps}.
 * @returns The bar, or `null` when nothing is selected.
 */
export function BulkActionBar({
  selectedStatuses,
  requeueableStatuses,
  onRetry,
  onMoveTop,
  onMoveBottom,
  onRemove,
  onClearSelection,
  busy = false,
}: BulkActionBarProps): ReactElement | null {
  if (selectedStatuses.length === 0) {
    return null
  }

  // Retry is live when AT LEAST ONE selected row can be re-queued: the run skips
  // the rest. Requiring every row to qualify would disable the control for the
  // common mixed selection.
  const canRetry =
    !busy && selectedStatuses.some((status) => requeueableStatuses.includes(status))

  return (
    <div
      className={barClasses}
      data-testid="bulk-action-bar"
      role="toolbar"
      aria-label="Bulk actions"
    >
      <span className={countClasses} data-testid="bulk-selection-count">
        {`${String(selectedStatuses.length)} selected`}
      </span>
      <Button
        size="sm"
        variant="ghost"
        data-testid="bulk-retry"
        disabled={!canRetry}
        onClick={onRetry}
      >
        <RotateCcw className={iconClasses} aria-hidden="true" />
        Retry
      </Button>
      <Button
        size="sm"
        variant="ghost"
        data-testid="bulk-move-top"
        disabled={busy}
        onClick={onMoveTop}
      >
        <ArrowUpToLine className={iconClasses} aria-hidden="true" />
        Move to top
      </Button>
      <Button
        size="sm"
        variant="ghost"
        data-testid="bulk-move-bottom"
        disabled={busy}
        onClick={onMoveBottom}
      >
        <ArrowDownToLine className={iconClasses} aria-hidden="true" />
        Move to bottom
      </Button>
      <Button
        size="sm"
        variant="destructive"
        data-testid="bulk-remove"
        disabled={busy}
        onClick={onRemove}
      >
        <Trash2 className={iconClasses} aria-hidden="true" />
        Remove
      </Button>
      {/* The spec's spacer: Clear selection is not one of the acting verbs. */}
      <span className="flex-1" aria-hidden="true" />
      <Button
        size="sm"
        variant="ghost"
        data-testid="bulk-clear-selection"
        onClick={onClearSelection}
      >
        <X className={iconClasses} aria-hidden="true" />
        Clear selection
      </Button>
    </div>
  )
}
