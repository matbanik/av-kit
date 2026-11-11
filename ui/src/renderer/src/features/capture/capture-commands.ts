import { ApiError, apiFetch } from '../../lib/api'
import { queryClient } from '../../lib/query-client'
import { navigateShell } from '../../lib/shell-nav'
import { ANNOTATE_PATH, parseAnnotateBody, type Annotation } from './capture-annotate'
import type { CropBox } from './capture-crop'
import { QUERY_KEY, type CaptureListItem } from './useCaptureCatalog'

export const IPC_CAPTURE_REGION = 'capture-region'

export const CAPTURE_EVENTS = {
  region: 'av-kit:capture:region',
  save: 'av-kit:capture:save',
  open_folder: 'av-kit:capture:open_folder',
} as const

export const CAPTURE_PALETTE_IDS = [
  'nav:capture',
  'capture:region',
  'capture:save',
  'capture:open_folder',
] as const

let selectedId: string | null = null
let annotations: Annotation[] = []
let inboxDir = '~/Pictures/av-kit'
// VIEWED_FILE (MEU-84): the file the viewport shows, which Open file and Open folder use.
let viewedPath: string | null = null

export function setCaptureSelection(next: {
  id: string | null
  annotations?: Annotation[]
  viewedPath?: string | null
}): void {
  selectedId = next.id
  if (next.annotations !== undefined) {
    annotations = next.annotations
  }
  if (next.viewedPath !== undefined) {
    viewedPath = next.viewedPath
  }
}

export function setCaptureInboxDir(dir: string): void {
  inboxDir = dir
}

export function isCaptureHome(): boolean {
  const hash = window.location.hash.replace(/^#/, '')
  return hash === '/capture'
}

export function navigateAndDeliver(run: () => void): void {
  if (!isCaptureHome()) {
    navigateShell('/capture')
  }
  window.requestAnimationFrame(() => {
    window.requestAnimationFrame(run)
  })
}

function rethrow(error: unknown): void {
  const message = error instanceof ApiError || error instanceof Error ? error.message : String(error)
  window.dispatchEvent(new CustomEvent('av-kit:capture:error', { detail: message }))
}

export async function invokeCaptureRegion(): Promise<void> {
  void IPC_CAPTURE_REGION
  await window.api.captureRegion()
}

let saveAllowed: () => boolean = () => selectedId !== null

export function setCaptureSaveAllowed(gate: () => boolean): void {
  saveAllowed = gate
}

export async function saveAnnotations(): Promise<boolean> {
  if (!saveAllowed()) {
    return false
  }
  if (selectedId === null) {
    return false
  }
  const body = parseAnnotateBody({ annotations })
  if (body === null) {
    window.dispatchEvent(new CustomEvent('av-kit:capture:error', { detail: 'Invalid overlay marks' }))
    return false
  }
  await apiFetch(ANNOTATE_PATH.replace('{id}', selectedId), {
    method: 'POST',
    body: JSON.stringify(body),
  })
  await queryClient.invalidateQueries({ queryKey: QUERY_KEY })
  return true
}

export async function deleteCapture(id: string): Promise<void> {
  await apiFetch(`/captures/${id}`, { method: 'DELETE' })
  await queryClient.invalidateQueries({ queryKey: QUERY_KEY })
}

/** One `DELETE /captures/{id}` with the id percent-encoded (RULE-2); no catalog refresh. */
export async function removeCapture(id: string): Promise<void> {
  await apiFetch(`/captures/${encodeURIComponent(id)}`, { method: 'DELETE' })
}

export type BatchDeleteResult = { deleted: string[]; failed: { id: string; message: string }[] }

/**
 * BATCH_DELETE (MEU-89): awaits `remove` for each id in the given order, so a request starts
 * only after the previous one settles. A failure is recorded and the loop goes on; the
 * catalog is refreshed once at the end, and not at all for an empty list.
 */
export async function deleteCaptures(
  ids: readonly string[],
  remove: (id: string) => Promise<unknown>,
): Promise<BatchDeleteResult> {
  const result: BatchDeleteResult = { deleted: [], failed: [] }
  if (ids.length === 0) {
    return result
  }
  for (const id of ids) {
    try {
      await remove(id)
      result.deleted.push(id)
    } catch (caught) {
      result.failed.push({ id, message: caught instanceof Error ? caught.message : String(caught) })
    }
  }
  await queryClient.invalidateQueries({ queryKey: QUERY_KEY })
  return result
}

/** Shot detail as flatten/revert return it (CaptureShotDetailOut). */
export type CaptureShotDetail = CaptureListItem & { annotations: unknown[]; backup_path: string | null }

/** MEU-67 Apply to image: POST {} and refresh the catalog (IMAGE_REVISION). */
export async function flattenCapture(id: string): Promise<CaptureShotDetail> {
  const detail = await apiFetch<CaptureShotDetail>(`/captures/${id}/flatten`, { method: 'POST', body: '{}' })
  await queryClient.invalidateQueries({ queryKey: QUERY_KEY })
  return detail
}

/** MEU-67 Revert: POST {} and refresh the catalog (IMAGE_REVISION). */
export async function revertCapture(id: string): Promise<CaptureShotDetail> {
  const detail = await apiFetch<CaptureShotDetail>(`/captures/${id}/revert`, { method: 'POST', body: '{}' })
  await queryClient.invalidateQueries({ queryKey: QUERY_KEY })
  return detail
}

/** MEU-131 CROP_COMMIT: Session 59's `CaptureCropOut`; the renderer reads `item` only. */
export type CaptureCropResult = { item: CaptureListItem; source_id: string; clamped: boolean }

/**
 * MEU-131 CROP_COMMIT (D-516): POST the integer box to the source's crop route and refresh the catalog, so
 * the new shot is listed before the page selects it. The source is untouched.
 */
export async function cropCapture(id: string, box: CropBox): Promise<CaptureCropResult> {
  const result = await apiFetch<CaptureCropResult>(`/captures/${encodeURIComponent(id)}/crop`, {
    method: 'POST',
    body: JSON.stringify({ x: box.x, y: box.y, width: box.width, height: box.height }),
  })
  await queryClient.invalidateQueries({ queryKey: QUERY_KEY })
  return result
}

export type CaptureImportResult = { item: CaptureListItem }

/** MEU-132 IMPORT_CALL: one file into the inbox through MEU-129's import route; IMPORT_RUN refetches once. */
export async function importCapture(path: string): Promise<CaptureImportResult> {
  return apiFetch<CaptureImportResult>('/captures', {
    method: 'POST',
    body: JSON.stringify({ mode: 'import', path }),
  })
}

export async function openCaptureFile(): Promise<void> {
  const target = viewedPath
  if (target === null || target.length < 1) {
    return
  }
  await window.api.openPath(target)
}

export async function openCaptureFolder(): Promise<void> {
  const target = viewedPath ?? inboxDir
  if (target.length < 1) {
    return
  }
  await window.api.showItemInFolder(target)
}

export const CAPTURE_COMMANDS = {
  region: () => {
    navigateAndDeliver(() => {
      void invokeCaptureRegion().catch(rethrow)
    })
  },
  save: () => {
    // CAPTURE_SAVE_ROUTE: press the page's Save so the shot ends clean as after a click.
    navigateAndDeliver(() => {
      const button = document.querySelector('[data-testid="capture-save"]')
      if (button instanceof HTMLButtonElement && !button.disabled) {
        button.click()
      }
    })
  },
  open_folder: () => {
    navigateAndDeliver(() => {
      void openCaptureFolder().catch(rethrow)
    })
  },
}
