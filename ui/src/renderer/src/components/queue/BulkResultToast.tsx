/**
 * The partial-result report a bulk fan-out raises (G35, `ERROR_SURFACE`).
 *
 * `BULK_ENDPOINT_POLICY` makes every bulk action N independent requests, so a
 * run that half-succeeds is the normal case, not an edge case — and a run that
 * reported nothing would leave the user staring at a queue that changed for
 * reasons they cannot see. The note is a polite live region, so the outcome
 * reaches a screen reader without stealing focus, and it is DISMISSIBLE rather
 * than a flash: a message that disappears on a timer is unreadable exactly when
 * it matters most, which is when it lists several failures.
 */
import { X } from 'lucide-react'
import { type ReactElement } from 'react'

import { type BulkResult } from '../../lib/queue/run-bulk'
import { Tooltip } from '../ui/Tooltip'

export type BulkResultToastProps = {
  /** The run to report, or `null` when there is nothing to say. */
  result: BulkResult | null
  /** Clear the note. */
  onDismiss: () => void
}

const toastClasses = [
  'flex items-start gap-2 rounded-[var(--radius-md)] px-3 py-2 text-sm',
  'border border-border bg-bg-elevated text-fg',
].join(' ')

const dismissClasses = [
  'ml-auto shrink-0 rounded-[var(--radius-control)] p-1 text-fg-muted',
  'hover:bg-neutral/30 hover:text-fg',
  'focus-visible:outline-none focus-visible:shadow-[0_0_0_3px_var(--color-accent-ring)]',
].join(' ')

/**
 * Render the bulk result note.
 *
 * @param props - See {@link BulkResultToastProps}.
 * @returns The note, or `null` when there is no result to report.
 */
export function BulkResultToast({ result, onDismiss }: BulkResultToastProps): ReactElement | null {
  if (result === null) {
    return null
  }

  return (
    <div className={toastClasses} data-testid="bulk-toast" role="status" aria-live="polite">
      <span>{result.message}</span>
      <Tooltip id="bulk-toast-dismiss" label="Dismiss">
        <button
          type="button"
          className={dismissClasses}
          data-testid="bulk-toast-dismiss"
          aria-label="Dismiss"
          onClick={onDismiss}
        >
          <X className="h-4 w-4" aria-hidden="true" />
        </button>
      </Tooltip>
    </div>
  )
}
