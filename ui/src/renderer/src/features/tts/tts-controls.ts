import type { StatusChipTone } from '../../components/ui/StatusChip'

export const JOB_STATUSES = [
  'Idle',
  'Pending',
  'Generating',
  'Done',
  'Failed',
  'Cancelled',
] as const

export type JobStatus = (typeof JOB_STATUSES)[number]

export const SPEED_PRESETS = [0.8, 1.0, 1.1] as const

/**
 * The share of a job done, as a whole percentage floored into 0 to 100.
 *
 * A job's `segments_done` and `segments_total` are a progress scale
 * (`TTS_PROGRESS_RESOLUTION` steps in the service), not a segment count, so the run bar
 * shows this percentage and never `done/total`. The floor never shows 100% while the job
 * still runs. A total of 0 or less, or a value that is not finite, gives 0.
 */
function progressPercent(done: number, total: number): number {
  if (!Number.isFinite(done) || !Number.isFinite(total) || total <= 0) {
    return 0
  }
  return Math.min(100, Math.max(0, Math.floor((100 * done) / total)))
}

/**
 * `PROGRESS_PERCENT`: the run bar's progress label.
 *
 * @param done - The job's `segments_done`, a step on the progress scale.
 * @param total - The job's `segments_total`, the scale's length.
 * @returns The floored percentage with a `%` sign, such as `25%`.
 */
export function progressLabel(done: number, total: number): string {
  return `${String(progressPercent(done, total))}%`
}

/**
 * `PROGRESS_ARIA`: the run bar's value, the label's percentage over 100.
 *
 * `ProgressBar` rounds its value times 100 for `aria-valuenow`; a floored value rounds to
 * itself, so a screen reader hears the number the label shows (D-963).
 *
 * @param done - The job's `segments_done`.
 * @param total - The job's `segments_total`.
 * @returns A fraction from 0 to 1.
 */
export function progressFraction(done: number, total: number): number {
  return progressPercent(done, total) / 100
}

/**
 * `PILL_CHIP_TONES`: the run bar's status pill tone for each job status.
 *
 * The pill is a `StatusChip`, a 10% status-hue fill with `text-fg` that reads at 4.5:1 in
 * both themes. The tones follow the queue header's `toneFor`: done is success, failed
 * danger, running info, waiting warning, anything else neutral.
 */
export const TTS_STATUS_TONE: Record<JobStatus, StatusChipTone> = {
  Idle: 'neutral',
  Pending: 'warning',
  Generating: 'info',
  Done: 'success',
  Failed: 'danger',
  Cancelled: 'neutral',
}

const BLOCKED_GENERATE = new Set(['Generating', 'Pending'])
const CANCELABLE = new Set(['Generating', 'Pending'])

export function generateEnabled(input: {
  isLoaded: boolean
  text: string
  status: string
}): boolean {
  return input.isLoaded && input.text.trim().length > 0 && !BLOCKED_GENERATE.has(input.status)
}

export function cancelEnabled(input: { status: string }): boolean {
  return CANCELABLE.has(input.status)
}

export function getEnabled(input: {
  isDownloaded: boolean
  runtimeState: string
}): boolean {
  return !input.isDownloaded && input.runtimeState !== 'Downloading'
}

export function loadEnabled(input: {
  isDownloaded: boolean
  loadedVariantId: string | null | undefined
  rowId: string
}): boolean {
  return input.isDownloaded && input.loadedVariantId !== input.rowId
}

export function openOutputEnabled(outputPath: string | null | undefined): boolean {
  return typeof outputPath === 'string' && outputPath.length > 0
}

/** `MODEL_ACTION`: the one model button's action for the selected variant. */
export type ModelAction = 'get' | 'load' | 'unload'

/**
 * Resolve `MODEL_ACTION` for the selected variant from the Get/Load predicates.
 *
 * @param input - The selection, the loaded variant (null when none is loaded) and the
 *   download runtime state.
 * @returns The action, and whether it is enabled. Every action is disabled while any
 *   download runs.
 */
export function resolveModelAction(input: {
  isDownloaded: boolean
  loadedVariantId: string | null
  rowId: string
  runtimeState: string
}): { action: ModelAction; enabled: boolean } {
  const idle = input.runtimeState !== 'Downloading'
  if (input.loadedVariantId !== null && input.loadedVariantId === input.rowId) {
    return { action: 'unload', enabled: idle }
  }
  if (loadEnabled(input)) {
    return { action: 'load', enabled: idle }
  }
  return { action: 'get', enabled: getEnabled(input) }
}

/**
 * The picker's state suffix for one variant: `downloading N%`, `loaded`, `downloaded`
 * or `not downloaded`. `loaded` is only ever the loaded variant.
 */
export function modelStateSuffix(input: {
  rowId: string
  isDownloaded: boolean
  loadedVariantId: string | null
  runtime: { state: string; variant_id?: string | null; fraction?: number | null } | undefined
}): string {
  const download = input.runtime
  if (download?.state === 'Downloading' && download.variant_id === input.rowId) {
    return `downloading ${Math.round((download.fraction ?? 0) * 100)}%`
  }
  if (input.loadedVariantId !== null && input.loadedVariantId === input.rowId) {
    return 'loaded'
  }
  return input.isDownloaded ? 'downloaded' : 'not downloaded'
}

/**
 * The fallback's preference among runnable rows (D-239, D-330): ONNX INT8, then FP32. FP16
 * is still offered, and is picked only when it is the one downloaded row.
 */
export const PRESELECT_ORDER = ['kokoro-onnx-int8', 'kokoro-onnx-fp32'] as const

/**
 * Default picker selection: the user's choice while it is still in the catalog, else the
 * loaded variant, else the first downloaded one, else the first row. For the last two the
 * runnable rows are ranked by `PRESELECT_ORDER`, with every other row after them in catalog
 * order. The chosen, first-downloaded and first-row rules skip a row this build can't run
 * (`available: false`), and with no runnable row the result is `null`. The loaded row is
 * kept: a load of an unavailable variant is refused, so a loaded row could run when it loaded.
 */
export function defaultModelSelection(input: {
  chosen: string | null
  loadedVariantId: string | null
  catalog: ReadonlyArray<{ id: string; is_downloaded: boolean; available?: boolean }>
}): string | null {
  const ids = input.catalog.map((row) => row.id)
  // A row without `available` counts as available.
  const runnable = input.catalog.filter((row) => row.available !== false)
  if (input.chosen !== null && runnable.some((row) => row.id === input.chosen)) {
    return input.chosen
  }
  if (input.loadedVariantId !== null && ids.includes(input.loadedVariantId)) {
    return input.loadedVariantId
  }
  const order: ReadonlyArray<string> = PRESELECT_ORDER
  const rank = (id: string): number => {
    const index = order.indexOf(id)
    return index === -1 ? order.length : index
  }
  // The sort is stable, so rows outside PRESELECT_ORDER keep their catalog order.
  const ranked = [...runnable].sort((a, b) => rank(a.id) - rank(b.id))
  return ranked.find((row) => row.is_downloaded)?.id ?? ranked[0]?.id ?? null
}
