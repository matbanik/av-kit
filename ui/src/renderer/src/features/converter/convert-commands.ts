import { ApiError, apiFetch } from '../../lib/api'
import { queryClient } from '../../lib/query-client'
import { navigateShell } from '../../lib/shell-nav'
import {
  createConversionBody,
  type ConversionKindWire,
  type CopyModeWire,
  type StreamModeWire,
} from './convert-body'
import {
  buildReorderBody,
  buildReorderBodyToIndex,
  controlEnabled,
  isSameOrder,
  type ProcessorState,
  type QueueItemLike,
} from './convert-controls'
import {
  PRESET_DEFAULT,
  presetAdvanced,
  type AudioModeWire,
  type GpuPrefWire,
  type PresetWire,
  type ScaleHeight,
} from './convert-presets'
import { parseConvertTime } from './convert-time'
import { QUERY_KEY, parseListEnvelope } from './useConversionQueue'

export const CONVERT_EVENTS = {
  add: 'av-kit:convert:add',
  start: 'av-kit:convert:start',
  pause: 'av-kit:convert:pause',
  resume: 'av-kit:convert:resume',
  cancel: 'av-kit:convert:cancel',
  clear: 'av-kit:convert:clear',
} as const

/** The palette asks the Convert page to confirm a destructive command (CONFIRM_ROUTE). */
export const CONVERT_CONFIRM_EVENT = 'av-kit:convert:confirm'

export type ConvertConfirmRequest = { kind: 'clear' | 'cancel' }

/** The palette asks the Convert page to open its file browser (CONVERT_BROWSE). */
export const CONVERT_BROWSE_EVENT = 'av-kit:convert:browse'

export const CONVERT_PALETTE_IDS = [
  'convert:add',
  'convert:start',
  'convert:pause',
  'convert:resume',
  'convert:cancel',
  'convert:clear',
] as const

export type ConvertFormSnapshot = {
  kind: ConversionKindWire
  paths: string[]
  preset: PresetWire
  cq: number
  scale_height: ScaleHeight
  audio_mode: AudioModeWire
  gpu_choice: GpuPrefWire | null
  saved_gpu_preference: GpuPrefWire | null
  cutIn: string
  cutOut: string
  copy_mode: CopyModeWire
  stream_mode: StreamModeWire
  ffmpegAvailable: boolean
}

const DEFAULT_SNAPSHOT: ConvertFormSnapshot = {
  kind: 'compress',
  paths: [],
  preset: PRESET_DEFAULT,
  cq: 25,
  scale_height: 0,
  audio_mode: 'aac_128',
  gpu_choice: null,
  saved_gpu_preference: null,
  cutIn: '00:00:00.000',
  cutOut: '00:00:00.000',
  copy_mode: 'fast_copy',
  stream_mode: 'first',
  ffmpegAvailable: true,
}

let formSnapshot: ConvertFormSnapshot = { ...DEFAULT_SNAPSHOT }

export function getStagingPaths(): string[] {
  return [...formSnapshot.paths]
}

export function setConvertFormSnapshot(next: ConvertFormSnapshot): void {
  formSnapshot = { ...next, paths: next.paths.filter((path) => path.length > 0) }
}

export function isConvertHome(): boolean {
  const hash = window.location.hash.replace(/^#/, '')
  return hash === '/convert'
}

export function navigateAndDeliver(run: () => void): void {
  if (!isConvertHome()) {
    navigateShell('/convert')
  }
  window.requestAnimationFrame(() => {
    window.requestAnimationFrame(run)
  })
}

export function focusDropzone(): void {
  const tryFocus = (left: number): void => {
    const el = document.querySelector('[data-testid="convert-dropzone"]')
    if (el instanceof HTMLElement) {
      el.focus()
      return
    }
    if (left > 0) {
      window.requestAnimationFrame(() => {
        tryFocus(left - 1)
      })
    }
  }
  tryFocus(16)
}

async function queueContext(): Promise<{
  items: QueueItemLike[]
  processorState: ProcessorState
  selectedId: string | null
  ffmpegAvailable: boolean
}> {
  const cached = queryClient.getQueryData(QUERY_KEY)
  const envelope = cached
    ? parseListEnvelope(cached)
    : parseListEnvelope(await apiFetch<unknown>('/conversions'))
  if (!cached) {
    queryClient.setQueryData(QUERY_KEY, envelope)
  }
  return {
    items: envelope.items,
    processorState: envelope.processor.state,
    selectedId: envelope.items[0]?.id ?? null,
    ffmpegAvailable: formSnapshot.ffmpegAvailable,
  }
}

async function invalidateConversions(): Promise<void> {
  await queryClient.invalidateQueries({ queryKey: QUERY_KEY })
}

export async function postConversionCreate(
  input: unknown,
): Promise<{ items: { id: string }[] }> {
  const body = createConversionBody(input)
  if (body === null) {
    return { items: [] }
  }
  const created = await apiFetch<{ items: { id: string }[] }>('/conversions', {
    method: 'POST',
    body: JSON.stringify(body),
  })
  await invalidateConversions()
  return created
}

/** What a Compress job sends as its encoder. `choice` is what the user picked in this form, null until
 *  they pick. `saved` is the saved setting, null until it has loaded. A job with no value reads the
 *  setting when it runs. */
export function perJobGpuPreference(
  choice: GpuPrefWire | null,
  saved: GpuPrefWire | null,
): GpuPrefWire | undefined {
  if (choice === null || choice === saved) {
    return undefined
  }
  return choice
}

export function snapshotCreateInput(): unknown {
  const snap = formSnapshot
  if (snap.kind === 'compress') {
    const catalog = presetAdvanced(snap.preset)
    const body: Record<string, unknown> = {
      paths: snap.paths,
      kind: 'compress',
      preset: snap.preset,
    }
    if (snap.cq !== catalog.cq) {
      body.cq = snap.cq
    }
    if (snap.scale_height !== catalog.scale_height) {
      body.scale_height = snap.scale_height
    }
    if (snap.audio_mode !== catalog.audio_mode) {
      body.audio_mode = snap.audio_mode
    }
    const encoder = perJobGpuPreference(snap.gpu_choice, snap.saved_gpu_preference)
    if (encoder !== undefined) {
      body.gpu_preference = encoder
    }
    return body
  }
  if (snap.kind === 'cut') {
    const inMs = parseConvertTime(snap.cutIn)
    const outMs = parseConvertTime(snap.cutOut)
    return {
      paths: snap.paths,
      kind: 'cut',
      in_ms: inMs,
      out_ms: outMs,
      copy_mode: snap.copy_mode,
    }
  }
  return {
    paths: snap.paths,
    kind: 'extract',
    stream_mode: snap.stream_mode,
  }
}

export async function startConversion(): Promise<void> {
  const ctx = await queueContext()
  if (!controlEnabled('start', ctx)) {
    return
  }
  await apiFetch('/conversions/start', { method: 'POST' })
  await invalidateConversions()
}

export async function pauseConversion(): Promise<void> {
  const ctx = await queueContext()
  if (!controlEnabled('pause', ctx)) {
    return
  }
  await apiFetch('/conversions/pause', { method: 'POST' })
  await invalidateConversions()
}

export async function resumeConversion(): Promise<void> {
  const ctx = await queueContext()
  if (!controlEnabled('resume', ctx)) {
    return
  }
  await apiFetch('/conversions/resume', { method: 'POST' })
  await invalidateConversions()
}

export async function cancelConversion(): Promise<void> {
  const ctx = await queueContext()
  if (!controlEnabled('cancel', ctx)) {
    return
  }
  await apiFetch('/conversions/cancel', { method: 'POST' })
  await invalidateConversions()
}

export async function clearConversions(): Promise<void> {
  const ctx = await queueContext()
  if (!controlEnabled('clear-all', ctx)) {
    return
  }
  await apiFetch('/conversions', { method: 'DELETE' })
  await invalidateConversions()
}

export function deliverPaletteAdd(): void {
  navigateAndDeliver(() => {
    if (getStagingPaths().length < 1) {
      focusDropzone()
      return
    }
    void postConversionCreate(snapshotCreateInput()).catch(rethrow)
  })
}

export function deliverPaletteStart(): void {
  navigateAndDeliver(() => {
    void startConversion().catch(rethrow)
  })
}

export function deliverPalettePause(): void {
  navigateAndDeliver(() => {
    void pauseConversion().catch(rethrow)
  })
}

export function deliverPaletteResume(): void {
  navigateAndDeliver(() => {
    void resumeConversion().catch(rethrow)
  })
}

function requestConfirm(kind: ConvertConfirmRequest['kind']): void {
  navigateAndDeliver(() => {
    window.dispatchEvent(new CustomEvent<ConvertConfirmRequest>(CONVERT_CONFIRM_EVENT, { detail: { kind } }))
  })
}

/** The page's confirm runs the cancel; the palette never calls the API itself. */
export function deliverPaletteCancel(): void {
  requestConfirm('cancel')
}

/** The page's confirm runs the clear-all; the palette never calls the API itself. */
export function deliverPaletteClear(): void {
  requestConfirm('clear')
}

export function deliverPaletteBrowse(): void {
  navigateAndDeliver(() => {
    window.dispatchEvent(new CustomEvent(CONVERT_BROWSE_EVENT))
  })
}

function rethrow(error: unknown): void {
  const message = error instanceof ApiError || error instanceof Error ? error.message : String(error)
  window.dispatchEvent(new CustomEvent('av-kit:convert:error', { detail: message }))
}

/** Direction accepted by {@link reorderConversion}; mirrors `buildReorderBody`. */
export type ReorderDirection = 'up' | 'down' | 'top' | 'bottom'

/**
 * Normalize a caught API failure into an `Error` whose message always
 * carries the HTTP status alongside the server's own reason, and whose
 * `.status` property carries it structurally too (ERROR_SURFACE / G15). The
 * kebab, the primary action and the bulk bar all render this message
 * verbatim to the user, so a bare "Conflict" would hide which conversion
 * failed and why a retry, a remove or a reorder was rejected.
 *
 * @param error - The value caught from a rejected `apiFetch` call.
 * @returns An `Error` safe to re-throw to the caller.
 */
function toCommandError(error: unknown): Error & { status?: number } {
  if (error instanceof ApiError) {
    const wrapped = new Error(
      `Request failed with status ${error.status}: ${error.message}`,
    ) as Error & { status: number }
    wrapped.name = 'CommandError'
    wrapped.status = error.status
    return wrapped
  }
  if (error instanceof Error) {
    return error
  }
  return new Error(String(error))
}

/**
 * Re-queue a single failed or cancelled conversion (AC-45.4). Callers gate
 * this command's visibility via `controlEnabled('reset', ctx)` — per
 * KEBAB_MENU_ORDER an unavailable action is absent, never disabled — so this
 * function performs the mutation unconditionally once invoked.
 *
 * @param id - The conversion job id to reset.
 * @throws {Error} With `.status` set to the HTTP status when the API
 *   rejects the request — this command never resolves silently on failure.
 */
/**
 * Issue the re-queue request for one conversion and nothing else — no cache
 * reconcile.
 *
 * This is the primitive a bulk fan-out is handed. `runBulk` owns
 * CLEAR_FINISHED_SEMANTICS clause 6 — exactly ONE list refetch, after the whole
 * run settles — so a per-row invalidation here would be N redundant refetches
 * interleaved between the requests, each one re-rendering the queue mid-run.
 *
 * @param id - The conversion job id.
 * @throws {Error} With `.status` set to the HTTP status on failure.
 */
export async function resetConversionOnly(id: string): Promise<void> {
  try {
    await apiFetch(`/conversions/${id}/reset`, { method: 'POST' })
  } catch (error) {
    throw toCommandError(error)
  }
}

/**
 * Re-queue a single conversion (AC-45.4).
 *
 * Reconciles the list on its own, so it is the right call for a SINGLE-row
 * gesture. A bulk fan-out uses `resetConversionOnly` instead and reconciles once at
 * the end.
 *
 * @param id - The conversion job id.
 * @throws {Error} With `.status` set to the HTTP status on failure.
 */
export async function resetConversion(id: string): Promise<void> {
  await resetConversionOnly(id)
  await invalidateConversions()
}

/**
 * Remove a single conversion's queue record (AC-45.4). Per
 * CLEAR_FINISHED_SEMANTICS clause 5 this deletes the queue entry only — the
 * media file on disk is untouched — so the request carries no body.
 *
 * @param id - The conversion job id to remove.
 * @throws {Error} With `.status` set to the HTTP status on failure.
 */
/**
 * Issue the remove request for one conversion and nothing else — no cache
 * reconcile.
 *
 * This is the primitive a bulk fan-out is handed. `runBulk` owns
 * CLEAR_FINISHED_SEMANTICS clause 6 — exactly ONE list refetch, after the whole
 * run settles — so a per-row invalidation here would be N redundant refetches
 * interleaved between the requests, each one re-rendering the queue mid-run.
 *
 * @param id - The conversion job id.
 * @throws {Error} With `.status` set to the HTTP status on failure.
 */
export async function removeConversionOnly(id: string): Promise<void> {
  try {
    await apiFetch(`/conversions/${id}`, { method: 'DELETE' })
  } catch (error) {
    throw toCommandError(error)
  }
}

/**
 * Remove a single conversion's queue record (AC-45.4). Per
 * CLEAR_FINISHED_SEMANTICS clause 5 this deletes the queue entry only — the
 * media file on disk is untouched.
 *
 * Reconciles the list on its own, so it is the right call for a SINGLE-row
 * gesture. A bulk fan-out uses `removeConversionOnly` instead and reconciles once at
 * the end.
 *
 * @param id - The conversion job id.
 * @throws {Error} With `.status` set to the HTTP status on failure.
 */
export async function removeConversion(id: string): Promise<void> {
  await removeConversionOnly(id)
  await invalidateConversions()
}

/**
 * Issue one conversion reorder WITHOUT reconciling the list (AC-45.4). Sends the
 * complete permutation required by REORDER_WIRE_CONTRACT — never
 * `{ id, direction }` — built by the existing `buildReorderBody`, reused
 * unchanged.
 *
 * This is the variant `bulkReorder` folds over. Its steps are dependent — each
 * request is built from the order the previous one produced — so a per-step
 * invalidation would refetch the list N times inside one gesture and re-render
 * the queue between the steps of a single absolute permutation, against
 * CLEAR_FINISHED_SEMANTICS clause 6.
 *
 * @param ids - The full ordered list of job ids currently in the queue.
 * @param selectedId - The id being moved.
 * @param direction - Which way to move it.
 * @throws {Error} With `.status` set to the HTTP status on failure (e.g. a
 *   422 when `ids` is not a complete permutation of the queue).
 */
export async function reorderConversionOnly(
  ids: string[],
  selectedId: string,
  direction: ReorderDirection,
): Promise<void> {
  const body = buildReorderBody(ids, selectedId, direction)
  try {
    await apiFetch('/conversions/reorder', { method: 'PUT', body: JSON.stringify(body) })
  } catch (error) {
    throw toCommandError(error)
  }
}

/**
 * Move one conversion within the queue order and reconcile (AC-45.4).
 *
 * Reconciles on its own, so it is the right call for a SINGLE-row gesture — the
 * card kebab and the keyboard path. A bulk fold uses `reorderConversionOnly`
 * and reconciles once at the end.
 *
 * @param ids - The full ordered list of job ids currently in the queue.
 * @param selectedId - The id being moved.
 * @param direction - Which way to move it.
 * @throws {Error} With `.status` set to the HTTP status on failure.
 */
export async function reorderConversion(
  ids: string[],
  selectedId: string,
  direction: ReorderDirection,
): Promise<void> {
  await reorderConversionOnly(ids, selectedId, direction)
  await invalidateConversions()
}

/**
 * Move one conversion to an absolute final index and reconcile (AC-49.21).
 *
 * The drag counterpart of {@link reorderConversion}, mirroring
 * `reorderDownloadToIndex` exactly — the two queues differ only in their
 * endpoint. See that function for why an identity permutation is dropped
 * rather than sent.
 *
 * @param ids - The full ordered list of job ids currently in the queue.
 * @param movedId - The id being dropped.
 * @param targetIndex - The FINAL index the row must occupy, pre-move.
 * @throws {Error} With `.status` set to the HTTP status on failure.
 */
export async function reorderConversionToIndex(
  ids: string[],
  movedId: string,
  targetIndex: number,
): Promise<void> {
  const body = buildReorderBodyToIndex(ids, movedId, targetIndex)
  if (isSameOrder(ids, body.job_ids)) {
    return
  }
  try {
    await apiFetch('/conversions/reorder', { method: 'PUT', body: JSON.stringify(body) })
  } catch (error) {
    throw toCommandError(error)
  }
  await invalidateConversions()
}

export const CONVERT_COMMANDS = {
  add: deliverPaletteAdd,
  start: deliverPaletteStart,
  pause: deliverPalettePause,
  resume: deliverPaletteResume,
  cancel: deliverPaletteCancel,
  clear: deliverPaletteClear,
  postConversionCreate,
  // Palette-id aliases (CONVERT_PALETTE_IDS) onto the same handlers above —
  // AppShell.tsx dispatches by short key (`.add()`), the command palette
  // dispatches by full id (`convert:add`); both must resolve to one handler.
  'convert:add': deliverPaletteAdd,
  'convert:start': deliverPaletteStart,
  'convert:pause': deliverPalettePause,
  'convert:resume': deliverPaletteResume,
  'convert:cancel': deliverPaletteCancel,
  'convert:clear': deliverPaletteClear,
}
