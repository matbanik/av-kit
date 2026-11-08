export const JOB_STATUSES = [
  'Pending',
  'Downloading',
  'Done',
  'Failed',
  'Skipped',
  'QualityBlocked',
  'AgeRestricted',
  'Cancelled',
] as const

export type JobStatus = (typeof JOB_STATUSES)[number]
export type ProcessorState = 'Idle' | 'Processing' | 'Paused'

export type QueueControl =
  | 'start'
  | 'pause'
  | 'resume'
  | 'cancel'
  | 'up'
  | 'down'
  | 'top'
  | 'bottom'
  | 'reset'
  | 'remove'
  | 'clear-all'
  | 'open-file'
  | 'open-folder'

export type QueueItemLike = {
  id: string
  status: string
  file_path: string | null
}

export type ControlContext = {
  items: QueueItemLike[]
  selectedId: string | null
  processorState: ProcessorState
}

/**
 * The download statuses a job can be re-queued from (AC-46.2,
 * DOWNLOAD_REQUEUEABLE_STATUSES). `POST /downloads/{id}/reset` answers 200 for
 * every one of them; before MEU-46 the GUI offered Retry on `Failed` alone, so
 * a quality-blocked or age-restricted job was a dead end.
 *
 * `Skipped` is deliberately absent (USER_LOCKS lock 4): a download is skipped
 * because the file already exists, and offering Retry there would silently
 * re-download over it.
 */
export const DOWNLOAD_REQUEUEABLE_STATUSES = [
  'Failed',
  'Cancelled',
  'QualityBlocked',
  'AgeRestricted',
] as const satisfies readonly JobStatus[]

function selectedIndex(ctx: ControlContext): number {
  if (ctx.selectedId === null) {
    return -1
  }
  return ctx.items.findIndex((item) => item.id === ctx.selectedId)
}

export function controlEnabled(control: QueueControl, ctx: ControlContext): boolean {
  const selected = selectedIndex(ctx)
  const current = selected >= 0 ? ctx.items[selected] : undefined
  const hasPending = ctx.items.some((item) => item.status === 'Pending')
  switch (control) {
    case 'start':
      return hasPending && ctx.processorState !== 'Processing'
    case 'pause':
      return ctx.processorState === 'Processing'
    case 'resume':
      return ctx.processorState === 'Paused'
    case 'cancel':
      return ctx.processorState === 'Processing' || ctx.processorState === 'Paused'
    case 'up':
    case 'top':
      return selected > 0
    case 'down':
    case 'bottom':
      return selected >= 0 && selected < ctx.items.length - 1
    case 'reset':
      return (
        current !== undefined &&
        (DOWNLOAD_REQUEUEABLE_STATUSES as readonly string[]).includes(current.status)
      )
    case 'remove':
      return selected >= 0
    case 'clear-all':
      return ctx.items.length > 0
    case 'open-file':
    case 'open-folder':
      return current?.file_path != null && current.file_path.length > 0
    default: {
      const _never: never = control
      return _never
    }
  }
}

/**
 * `buildReorderBody` and `buildReorderBodyToIndex` have exactly one owner —
 * `REORDER_BODY_MODULE` — so this file re-exports the shared builders rather
 * than declaring its own copy. `convert-controls.ts` re-exports the same
 * binding, and `AC-49.3` asserts reference identity across both sites: a
 * second copy that merely behaved alike would fail that test.
 */
export {
  buildReorderBody,
  buildReorderBodyToIndex,
  isSameOrder,
} from '../../lib/queue/reorder-body'

export function queueSummary(items: { status: string }[]): Record<JobStatus, number> {
  const summary = Object.fromEntries(JOB_STATUSES.map((status) => [status, 0])) as Record<
    JobStatus,
    number
  >
  for (const item of items) {
    if ((JOB_STATUSES as readonly string[]).includes(item.status)) {
      summary[item.status as JobStatus] += 1
    }
  }
  return summary
}

export function processorLabel(state: ProcessorState): string | null {
  if (state === 'Idle') {
    return null
  }
  if (state === 'Processing') {
    return 'Processing…'
  }
  return 'Queue Paused'
}

/**
 * Fields of a download list row that {@link downloadMetaSegments} reads.
 * Deliberately narrower than the full wire shape — the function is pure and
 * feature-agnostic (META_SEGMENTS_CONTRACT), so it asks only for what it
 * renders.
 */
export type DownloadMetaRow = {
  quality: string
  speed: string | null
  eta: string | null
  status: string
  received_height: number | null
}

/**
 * The card meta line for one download row (AC-46.3, DOWNLOAD_META_SEGMENTS).
 *
 * Carries the Quality / Speed / ETA columns of the deleted react-table queue
 * onto the card. Speed and ETA are emitted whenever the field is non-null
 * *regardless of status* — the backend never clears them
 * (`services/download.py:561-571`), so a finished row keeps the speed and ETA it
 * completed at. A null or empty field yields no segment at all rather than a
 * stray em dash, because the card joins the segments with META_SEPARATOR and an
 * empty segment would render as a floating separator.
 *
 * SHOWN_WHEN_DIFFERENT (D-385): when the row's received height differs from its
 * requested quality, the Quality segment reads `360p (asked 1080p)`; a matching
 * or missing height leaves the request alone, as before MEU-124.
 *
 * @param row - One download list row; only the fields above are read.
 * @returns The segments in Quality, Speed, ETA order, with blanks dropped.
 */
export function downloadMetaSegments(row: DownloadMetaRow): string[] {
  const height = row.received_height
  const received = typeof height === 'number' && height > 0 ? `${height}p` : null
  const quality =
    received === null || received === row.quality
      ? row.quality
      : `${received} (asked ${row.quality})`
  const segments: (string | null)[] = [quality, row.speed, row.eta]
  return segments.filter(
    (segment): segment is string => segment !== null && segment.length > 0,
  )
}
