/**
 * Inputs for the pre-MEU-55 markup baseline (`queue-slot-baseline.json`).
 *
 * The JSON was captured from the unchanged `QueueCard` / `QueueHeaderRow` before
 * any CARD_SLOTS or HEADER_FRAME edit (task row 2). AC-55.1/AC-55.2 re-render
 * these exact inputs and require identical markup, which is what "a consumer
 * that passes no slot is byte-for-byte unchanged" means in a test.
 */
import type { ComponentProps } from 'react'

import type { QueueCard } from '../../../src/renderer/src/components/queue/QueueCard'
import type { QueueHeaderRow } from '../../../src/renderer/src/components/queue/QueueHeaderRow'

type CardProps = ComponentProps<typeof QueueCard>
type HeaderProps = ComponentProps<typeof QueueHeaderRow>

const noop = (): void => undefined

export const SLOTLESS_CARD_CASES: Record<string, CardProps> = {
  pending: {
    job: { id: 'j1', position: 1, status: 'Pending', title: 'Pending job' },
    isFirst: true,
  },
  doneWithMenu: {
    job: { id: 'j2', position: 2, status: 'Done', title: 'Done job', fileSize: 1024, outputPath: 'C:/out/a.mp4' },
    isLast: true,
    selectable: true,
    selected: true,
    onSelectChange: noop,
    onOpen: noop,
    onOpenFile: noop,
    onOpenFolder: noop,
    onMoveUp: noop,
    onRemove: noop,
  },
  inFlight: {
    job: { id: 'j3', position: 3, status: 'Downloading', title: 'Running job', progress: 0.42 },
    isInFlight: true,
    onCancelQueue: noop,
  },
}

export const HEADER_ROW_CASE: HeaderProps = {
  total: 3,
  selectedCount: 1,
  onToggleAll: noop,
  selectionAriaLabel: 'Select all downloads',
  statuses: ['Pending', 'Downloading', 'Done'],
  counts: { Pending: 2, Downloading: 1, Done: 0 },
  summaryTestId: 'queue-summary',
  processorTestId: 'processor-indicator',
  processorLabel: 'Processing…',
  toolbar: {
    processorState: 'Processing',
    label: 'Download queue actions',
    onStart: noop,
    onPauseResume: noop,
    onClearFinished: noop,
    onClearAll: noop,
  },
}
