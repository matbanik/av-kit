/**
 * The always-mounted select-all header (`SELECTION_HEADER_CONTRACT`).
 *
 * This is a separate component from `BulkActionBar` because the two have
 * opposite lifetimes, and the difference is normative: the bar exists only while
 * a selection does, whereas this checkbox is the control that *starts* one — a
 * header that appeared once a row was ticked could never be used to tick the
 * first row.
 *
 * The counts it is given are the FILTERED list's, the same list `QueueList`
 * renders, so toggling it can never reach a row the user cannot see.
 */
import { type ReactElement } from 'react'

import { SelectionCheckbox } from '../ui/SelectionCheckbox'

export type QueueSelectionHeaderProps = {
  /** How many rows the filtered list holds. */
  total: number
  /** How many of those rows are selected. */
  selectedCount: number
  /** Select (`true`) or clear (`false`) the whole filtered list. */
  onToggleAll: (checked: boolean) => void
  /** Accessible name for the checkbox, e.g. `Select all conversions`. */
  ariaLabel?: string
}

const headerClasses = 'flex items-center gap-2 px-1 py-1.5 text-sm text-fg-muted'

/**
 * Render the select-all checkbox and the list's item count.
 *
 * @param props - See {@link QueueSelectionHeaderProps}.
 * @returns The header row. Always rendered, whatever the selection.
 */
export function QueueSelectionHeader({
  total,
  selectedCount,
  onToggleAll,
  ariaLabel = 'Select all rows',
}: QueueSelectionHeaderProps): ReactElement {
  // An empty queue is UNCHECKED, never "all selected" by vacuous truth: a
  // checked box over nothing invites a bulk action against no rows.
  const allSelected = total > 0 && selectedCount >= total
  const someSelected = selectedCount > 0 && selectedCount < total

  return (
    <div className={headerClasses} data-testid="queue-selection-header">
      <SelectionCheckbox
        checked={allSelected}
        indeterminate={someSelected}
        ariaLabel={ariaLabel}
        testId="queue-select-all"
        onChange={(checked) => {
          onToggleAll(checked)
        }}
      />
      <span>{`${String(total)} items`}</span>
    </div>
  )
}
