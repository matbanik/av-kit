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

export const STATUS_COLORS: Record<JobStatus, string> = {
  Idle: 'bg-neutral',
  Pending: 'bg-status-pending',
  Generating: 'bg-accent',
  Done: 'bg-accent-green',
  Failed: 'bg-error',
  Cancelled: 'bg-neutral',
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
