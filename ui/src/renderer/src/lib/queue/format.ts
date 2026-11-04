/**
 * Shared queue formatting helpers.
 *
 * Single owner of `formatFileSize` (AC-43.1): the downloader and converter queue
 * tables each carried a byte-identical private copy before MEU-43. Both now
 * import from here, so a change to the size rendering lands in one place.
 */

/**
 * Render a byte count the way the queue surfaces show it.
 *
 * @param bytes - Size in bytes, or `null` when the backend has not reported one.
 * @returns `'—'` for an unknown or non-numeric size, otherwise a decimal-unit
 *          string (`MB` at 1e6, `KB` at 1e3, `B` below that).
 */
export function formatFileSize(bytes: number | null): string {
  if (bytes === null || Number.isNaN(bytes)) {
    return '—'
  }
  if (bytes >= 1_000_000) {
    return `${Math.round(bytes / 1_000_000)} MB`
  }
  if (bytes >= 1_000) {
    return `${Math.round(bytes / 1_000)} KB`
  }
  return `${bytes} B`
}
