import { PRESET_LABELS, type PresetWire } from './convert-presets'

export const JOB_STATUSES = [
  'Pending',
  'Processing',
  'Done',
  'Failed',
  'Cancelled',
  'Skipped',
] as const

export type JobStatus = (typeof JOB_STATUSES)[number]
export type ProcessorState = 'Idle' | 'Processing' | 'Paused'
export type ConversionKindWire = 'compress' | 'cut' | 'extract'

export type QueueControl =
  | 'add'
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
  output_path: string | null
  input_path: string
}

export type ControlContext = {
  items: QueueItemLike[]
  selectedId: string | null
  processorState: ProcessorState
  ffmpegAvailable: boolean
}

/**
 * Conversion statuses a `reset` (Retry) may act on (AC-45.5). Narrower than
 * `DOWNLOAD_REQUEUEABLE_STATUSES`: the conversion status enum has no
 * `QualityBlocked`/`AgeRestricted`, and `Skipped` stays locked out per
 * USER_LOCKS lock 4.
 */
export const CONVERT_REQUEUEABLE_STATUSES: readonly JobStatus[] = ['Failed', 'Cancelled'] as const

function selectedIndex(ctx: ControlContext): number {
  if (ctx.selectedId === null) {
    return -1
  }
  return ctx.items.findIndex((item) => item.id === ctx.selectedId)
}

export function applyTaskKind<T extends { kind: ConversionKindWire; staging: string[]; items: unknown[] }>(
  prev: T,
  nextKind: ConversionKindWire,
): T {
  return { ...prev, kind: nextKind }
}

export function controlEnabled(control: QueueControl, ctx: ControlContext): boolean {
  const selected = selectedIndex(ctx)
  const current = selected >= 0 ? ctx.items[selected] : undefined
  const hasPending = ctx.items.some((item) => item.status === 'Pending')
  switch (control) {
    case 'add':
      return ctx.ffmpegAvailable
    case 'start':
      return (
        hasPending &&
        (ctx.processorState === 'Idle' || ctx.processorState === 'Paused') &&
        ctx.ffmpegAvailable
      )
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
        (CONVERT_REQUEUEABLE_STATUSES as readonly string[]).includes(current.status)
      )
    case 'remove':
      return selected >= 0
    case 'clear-all':
      return ctx.items.length > 0
    case 'open-file':
    case 'open-folder':
      return current?.output_path != null && current.output_path.length > 0
    default: {
      const _never: never = control
      return _never
    }
  }
}

/**
 * `buildReorderBody` and `buildReorderBodyToIndex` have exactly one owner —
 * `REORDER_BODY_MODULE` — so this file re-exports the shared builders rather
 * than declaring its own copy. `download-controls.ts` re-exports the same
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

export function openTarget(item: QueueItemLike | undefined): string | null {
  if (item === undefined) {
    return null
  }
  if (item.output_path != null && item.output_path.length > 0) {
    return item.output_path
  }
  if (item.input_path.length > 0) {
    return item.input_path
  }
  return null
}

/** Kind label rendered as the first {@link convertMetaSegments} segment. */
const CONVERT_KIND_LABELS: Record<string, string> = {
  compress: 'Compress',
  cut: 'Cut',
  extract: 'Extract',
}

/**
 * Fields of a conversion list row that {@link convertMetaSegments} reads.
 * Deliberately narrower than the full `ConversionListItem` wire shape — the
 * function is pure and feature-agnostic (META_SEGMENTS_CONTRACT), so it only
 * asks for what it renders.
 */
export type ConvertMetaRow = {
  kind: string
  preset_id: string | null
  gpu_encoder?: string | null
  in_ms: number | null
  out_ms: number | null
  stream_index: number | null
  speed: string | null
  eta: string | null
}

/**
 * The mode segment for a single conversion row, or `null` when the row's
 * kind-specific mode has not resolved yet. `extract` is the one exception:
 * it always yields a segment, falling back to the literal `'audio'` because
 * that states something true about the job — an empty dash would not
 * (AC-45.17).
 */
function convertModeSegment(row: ConvertMetaRow): string | null {
  if (row.kind === 'compress') {
    if (
      row.preset_id !== null &&
      Object.prototype.hasOwnProperty.call(PRESET_LABELS, row.preset_id)
    ) {
      return PRESET_LABELS[row.preset_id as PresetWire]
    }
    return null
  }
  if (row.kind === 'cut') {
    if (row.in_ms !== null && row.out_ms !== null) {
      return `${row.in_ms}–${row.out_ms}`
    }
    return null
  }
  if (row.kind === 'extract') {
    return row.stream_index !== null ? `a:${row.stream_index}` : 'audio'
  }
  return null
}

/**
 * Build the QueueCard meta-line segments for a conversion row (AC-45.17),
 * matching `CONVERT_META_SEGMENTS`: kind label, mode label, speed, ETA. Null
 * fields are dropped entirely rather than rendered as an empty string or a
 * placeholder dash. Speed and ETA are included whenever present regardless
 * of status — the backend never clears them once a job finishes — so a
 * `Done` row keeps showing its final speed and ETA.
 *
 * @param row - The conversion fields this segment set depends on.
 * @returns The ordered, gap-free list of meta segments for this row.
 */
export function convertMetaSegments(row: ConvertMetaRow): string[] {
  const segments: (string | null)[] = [
    CONVERT_KIND_LABELS[row.kind] ?? row.kind,
    convertModeSegment(row),
    row.gpu_encoder ?? null,
    row.speed,
    row.eta,
  ]
  return segments.filter(
    (segment): segment is string => segment !== null && segment.length > 0,
  )
}
