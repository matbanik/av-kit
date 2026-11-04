import { z } from 'zod'

import { ApiError, apiFetch } from '../../lib/api'
import { queryClient } from '../../lib/query-client'
import { navigateShell } from '../../lib/shell-nav'
import {
  buildReorderBody,
  buildReorderBodyToIndex,
  controlEnabled,
  isSameOrder,
  type ProcessorState,
  type QueueItemLike,
} from './download-controls'
import { AUDIO_WIRE, QUALITY_WIRE, type AudioWire, type QualityWire } from './quality-options'
import { QUERY_KEY, parseListEnvelope } from './useDownloadQueue'

export const DOWNLOAD_EVENTS = {
  add: 'av-kit:download:add',
  start: 'av-kit:download:start',
  pause: 'av-kit:download:pause',
  resume: 'av-kit:download:resume',
  cancel: 'av-kit:download:cancel',
  clear: 'av-kit:download:clear',
  sabrCheck: 'av-kit:download:sabr-check',
} as const

/** The palette asks the Downloader page to confirm a destructive command (CONFIRM_ROUTE). */
export const DOWNLOAD_CONFIRM_EVENT = 'av-kit:download:confirm'

export type DownloadConfirmRequest = { kind: 'clear' | 'cancel' }

export const DOWNLOAD_PALETTE_IDS = [
  'download:add',
  'download:start',
  'download:pause',
  'download:resume',
  'download:cancel',
  'download:clear',
  'download:sabr_check',
] as const

const createSchema = z
  .object({
    url: z.string().min(1),
    quality: z.enum(QUALITY_WIRE),
    audio_only: z.boolean(),
    audio_format: z.enum(AUDIO_WIRE),
  })
  .strict()

export type CreateDownloadInput = {
  url: string
  quality: QualityWire
  audio_only: boolean
  audio_format: AudioWire
}

export function createDownloadBody(input: CreateDownloadInput): CreateDownloadInput | null {
  if (input.url.trim().length < 1) {
    return null
  }
  return createSchema.parse({ ...input, url: input.url.trim() })
}

export function applyCreateItems<T extends { id: string }>(out: { items: T[] }): T[] {
  return out.items
}

export function isDownloaderHome(): boolean {
  const hash = window.location.hash.replace(/^#/, '')
  return hash === '/' || hash === ''
}

export function navigateAndDeliver(run: () => void): void {
  if (!isDownloaderHome()) {
    navigateShell('/')
  }
  window.requestAnimationFrame(() => {
    window.requestAnimationFrame(run)
  })
}

export function focusUrlInput(): void {
  const tryFocus = (left: number): void => {
    const el = document.querySelector('[data-testid="url-input"]')
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
}> {
  const cached = queryClient.getQueryData(QUERY_KEY)
  const envelope = cached
    ? parseListEnvelope(cached)
    : parseListEnvelope(await apiFetch<unknown>('/downloads'))
  if (!cached) {
    queryClient.setQueryData(QUERY_KEY, envelope)
  }
  return {
    items: envelope.items,
    processorState: envelope.processor.state,
    selectedId: envelope.items[0]?.id ?? null,
  }
}

async function invalidateDownloads(): Promise<void> {
  await queryClient.invalidateQueries({ queryKey: QUERY_KEY })
}

async function invalidateDownloadsAndSabr(): Promise<void> {
  await queryClient.invalidateQueries({ queryKey: QUERY_KEY })
  await queryClient.invalidateQueries({ queryKey: ['downloads', 'sabr'] })
}

async function replaceQueueFromList(): Promise<void> {
  const envelope = parseListEnvelope(await apiFetch<unknown>('/downloads'))
  queryClient.setQueryData(QUERY_KEY, envelope)
}

export async function postDownloadCreate(input: CreateDownloadInput): Promise<{ items: { id: string }[] }> {
  const body = createDownloadBody(input)
  if (body === null) {
    return { items: [] }
  }
  const created = await apiFetch<{ items: { id: string }[] }>('/downloads', {
    method: 'POST',
    body: JSON.stringify(body),
  })
  applyCreateItems(created)
  await replaceQueueFromList()
  await invalidateDownloads()
  return created
}

export async function startDownload(): Promise<void> {
  const ctx = await queueContext()
  if (!controlEnabled('start', ctx)) {
    return
  }
  await apiFetch('/downloads/start', { method: 'POST' })
  await invalidateDownloads()
}

export async function pauseDownload(): Promise<void> {
  const ctx = await queueContext()
  if (!controlEnabled('pause', ctx)) {
    return
  }
  await apiFetch('/downloads/pause', { method: 'POST' })
  await invalidateDownloads()
}

export async function resumeDownload(): Promise<void> {
  const ctx = await queueContext()
  if (!controlEnabled('resume', ctx)) {
    return
  }
  await apiFetch('/downloads/resume', { method: 'POST' })
  await invalidateDownloads()
}

export async function cancelDownload(): Promise<void> {
  const ctx = await queueContext()
  if (!controlEnabled('cancel', ctx)) {
    return
  }
  await apiFetch('/downloads/cancel', { method: 'POST' })
  await invalidateDownloads()
}

export async function clearDownloads(): Promise<void> {
  const ctx = await queueContext()
  if (!controlEnabled('clear-all', ctx)) {
    return
  }
  await apiFetch('/downloads', { method: 'DELETE' })
  await invalidateDownloads()
}

export async function checkSabr(): Promise<void> {
  await apiFetch('/downloads/sabr/check', { method: 'POST', body: JSON.stringify({}) })
  await invalidateDownloadsAndSabr()
}

export async function forceSabr(): Promise<void> {
  await apiFetch('/downloads/sabr/force', { method: 'POST', body: JSON.stringify({}) })
  await invalidateDownloadsAndSabr()
}

export async function clearSabr(): Promise<void> {
  await apiFetch('/downloads/sabr/clear', { method: 'POST', body: JSON.stringify({}) })
  await invalidateDownloadsAndSabr()
}

export function deliverPaletteAdd(): void {
  navigateAndDeliver(() => {
    focusUrlInput()
  })
}

export function deliverPaletteStart(): void {
  navigateAndDeliver(() => {
    void startDownload().catch(rethrow)
  })
}

export function deliverPalettePause(): void {
  navigateAndDeliver(() => {
    void pauseDownload().catch(rethrow)
  })
}

export function deliverPaletteResume(): void {
  navigateAndDeliver(() => {
    void resumeDownload().catch(rethrow)
  })
}

function requestConfirm(kind: DownloadConfirmRequest['kind']): void {
  navigateAndDeliver(() => {
    window.dispatchEvent(new CustomEvent<DownloadConfirmRequest>(DOWNLOAD_CONFIRM_EVENT, { detail: { kind } }))
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

export function deliverPaletteSabrCheck(): void {
  navigateAndDeliver(() => {
    void checkSabr().catch(rethrow)
  })
}

function rethrow(error: unknown): void {
  const message = error instanceof ApiError || error instanceof Error ? error.message : String(error)
  window.dispatchEvent(new CustomEvent('av-kit:download:error', { detail: message }))
}

/** Direction accepted by {@link reorderDownload}; mirrors `buildReorderBody`. */
export type ReorderDirection = 'up' | 'down' | 'top' | 'bottom'

/**
 * Normalize a caught API failure into an `Error` whose message always carries
 * the HTTP status alongside the server's own reason, and whose `.status`
 * property carries it structurally too (ERROR_SURFACE / G15). The kebab and the
 * card's primary action render this message verbatim, so a bare "Conflict"
 * would hide which download failed and why the retry, remove or reorder was
 * rejected.
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
 * Re-queue a single download (AC-46.1). Callers gate this command's visibility
 * via `controlEnabled('reset', ctx)` — per KEBAB_MENU_ORDER an unavailable
 * action is absent, never disabled — so this function performs the mutation
 * unconditionally once invoked.
 *
 * @param id - The download job id to reset.
 * @throws {Error} With `.status` set to the HTTP status when the API rejects
 *   the request — this command never resolves silently on failure.
 */
/**
 * Issue the re-queue request for one download and nothing else — no cache
 * reconcile.
 *
 * This is the primitive a bulk fan-out is handed. `runBulk` owns
 * CLEAR_FINISHED_SEMANTICS clause 6 — exactly ONE list refetch, after the whole
 * run settles — so a per-row invalidation here would be N redundant refetches
 * interleaved between the requests, each one re-rendering the queue mid-run.
 *
 * @param id - The download job id.
 * @throws {Error} With `.status` set to the HTTP status on failure.
 */
export async function resetDownloadOnly(id: string): Promise<void> {
  try {
    await apiFetch(`/downloads/${id}/reset`, { method: 'POST' })
  } catch (error) {
    throw toCommandError(error)
  }
}

/**
 * Re-queue a single download (AC-46.1).
 *
 * Reconciles the list on its own, so it is the right call for a SINGLE-row
 * gesture. A bulk fan-out uses `resetDownloadOnly` instead and reconciles once at
 * the end.
 *
 * @param id - The download job id.
 * @throws {Error} With `.status` set to the HTTP status on failure.
 */
export async function resetDownload(id: string): Promise<void> {
  await resetDownloadOnly(id)
  await invalidateDownloads()
}

/**
 * Remove a single download's queue record (AC-46.1). Per
 * CLEAR_FINISHED_SEMANTICS clause 5 this deletes the queue entry only — the
 * media file on disk is untouched — so the request carries no body.
 *
 * @param id - The download job id to remove.
 * @throws {Error} With `.status` set to the HTTP status on failure.
 */
/**
 * Issue the remove request for one download and nothing else — no cache
 * reconcile.
 *
 * This is the primitive a bulk fan-out is handed. `runBulk` owns
 * CLEAR_FINISHED_SEMANTICS clause 6 — exactly ONE list refetch, after the whole
 * run settles — so a per-row invalidation here would be N redundant refetches
 * interleaved between the requests, each one re-rendering the queue mid-run.
 *
 * @param id - The download job id.
 * @throws {Error} With `.status` set to the HTTP status on failure.
 */
export async function removeDownloadOnly(id: string): Promise<void> {
  try {
    await apiFetch(`/downloads/${id}`, { method: 'DELETE' })
  } catch (error) {
    throw toCommandError(error)
  }
}

/**
 * Remove a single download's queue record (AC-46.1). Per
 * CLEAR_FINISHED_SEMANTICS clause 5 this deletes the queue entry only — the
 * media file on disk is untouched.
 *
 * Reconciles the list on its own, so it is the right call for a SINGLE-row
 * gesture. A bulk fan-out uses `removeDownloadOnly` instead and reconciles once at
 * the end.
 *
 * @param id - The download job id.
 * @throws {Error} With `.status` set to the HTTP status on failure.
 */
export async function removeDownload(id: string): Promise<void> {
  await removeDownloadOnly(id)
  await invalidateDownloads()
}

/**
 * Issue one download reorder WITHOUT reconciling the list (AC-46.1). Sends the
 * complete permutation required by REORDER_WIRE_CONTRACT — never
 * `{ id, direction }`, which `routes/downloads.py:210-217` answers with a 422 —
 * built by the existing `buildReorderBody`, reused unchanged.
 *
 * This is the variant `bulkReorder` folds over: its steps are dependent, so a
 * per-step invalidation would refetch the list N times inside one gesture,
 * against CLEAR_FINISHED_SEMANTICS clause 6.
 *
 * @param ids - The full ordered list of job ids currently in the queue.
 * @param selectedId - The id being moved.
 * @param direction - Which way to move it.
 * @throws {Error} With `.status` set to the HTTP status on failure.
 */
export async function reorderDownloadOnly(
  ids: string[],
  selectedId: string,
  direction: ReorderDirection,
): Promise<void> {
  const body = buildReorderBody(ids, selectedId, direction)
  try {
    await apiFetch('/downloads/reorder', { method: 'PUT', body: JSON.stringify(body) })
  } catch (error) {
    throw toCommandError(error)
  }
}

/**
 * Move one download within the queue order and reconcile (AC-46.1).
 *
 * Reconciles on its own, so it is the right call for a SINGLE-row gesture. A
 * bulk fold uses `reorderDownloadOnly` and reconciles once at the end.
 *
 * @param ids - The full ordered list of job ids currently in the queue.
 * @param selectedId - The id being moved.
 * @param direction - Which way to move it.
 * @throws {Error} With `.status` set to the HTTP status on failure.
 */
export async function reorderDownload(
  ids: string[],
  selectedId: string,
  direction: ReorderDirection,
): Promise<void> {
  await reorderDownloadOnly(ids, selectedId, direction)
  await invalidateDownloads()
}

/**
 * Move one download to an absolute final index and reconcile (AC-49.21).
 *
 * The drag counterpart of {@link reorderDownload}: a drop names a POSITION,
 * not a direction, and `MOVE_TO_INDEX_CONTRACT` resolves that index against the
 * order as it is currently rendered. `COMMAND_MODULE_RULE` puts it here rather
 * than in a page `onDrop` so the drag and the kebab reach the wire through the
 * same module, and cannot drift apart.
 *
 * A drop that lands the row back where it already is produces the identity
 * permutation, and that never reaches the wire: it is a PUT that can change
 * nothing and can only lose a race with the next real reorder.
 *
 * @param ids - The full ordered list of job ids currently in the queue.
 * @param movedId - The id being dropped.
 * @param targetIndex - The FINAL index the row must occupy, pre-move.
 * @throws {Error} With `.status` set to the HTTP status on failure.
 */
export async function reorderDownloadToIndex(
  ids: string[],
  movedId: string,
  targetIndex: number,
): Promise<void> {
  const body = buildReorderBodyToIndex(ids, movedId, targetIndex)
  if (isSameOrder(ids, body.job_ids)) {
    return
  }
  try {
    await apiFetch('/downloads/reorder', { method: 'PUT', body: JSON.stringify(body) })
  } catch (error) {
    throw toCommandError(error)
  }
  await invalidateDownloads()
}

export const DOWNLOAD_COMMANDS = {
  add: deliverPaletteAdd,
  start: deliverPaletteStart,
  pause: deliverPalettePause,
  resume: deliverPaletteResume,
  cancel: deliverPaletteCancel,
  clear: deliverPaletteClear,
  sabrCheck: deliverPaletteSabrCheck,
  postDownloadCreate,
  forceSabr,
  clearSabr,
  // Palette-id aliases (DOWNLOAD_PALETTE_IDS) onto the same handlers above —
  // AppShell.tsx dispatches by short key (`.add()`), the command palette
  // dispatches by full id (`download:add`); both must resolve to one handler.
  'download:add': deliverPaletteAdd,
  'download:start': deliverPaletteStart,
  'download:pause': deliverPalettePause,
  'download:resume': deliverPaletteResume,
  'download:cancel': deliverPaletteCancel,
  'download:clear': deliverPaletteClear,
  'download:sabr_check': deliverPaletteSabrCheck,
}
