/**
 * MEU-162 (Session 99, PRIVACY_GUARD, D-1292) the screenshot generator's privacy guard.
 *
 * `findPrivatePath(text, roots)` flags, with case ignored, each root in either slash form, any
 * `<drive>:\Users\<name>` or `<drive>:/Users/<name>` segment except `Users\Public`, and
 * `/Users/<name>/` or `/home/<name>/`. It never matches a bare user name.
 *
 * `clipText(items, clip)` is pure: it keeps the text items (from `gatherShotText` in the page)
 * that are not masked and have a rect with a non-zero area that meets the clip, joined by
 * newlines. So the guard reads only the text that the image can show.
 */

export type Rect = { x: number; y: number; width: number; height: number }
export type TextItem = { text: string; rects: Rect[]; masked: boolean }

const DRIVE_USERS = /\b[a-z]:[\\/]+users[\\/]+([^\\/\s"'<>|]+)/gi
const POSIX_HOME = /(?:^|[^\w.:-])(\/(?:users|home)\/[^/\s"'<>|]+\/)/gi

function slashes(text: string): string {
  return text.replace(/\\/g, '/').toLowerCase()
}

/** The first private path in `text`, or null. */
export function findPrivatePath(text: string, roots: readonly string[]): string | null {
  const flat = slashes(text)
  for (const root of roots) {
    const needle = slashes(root).replace(/\/+$/, '')
    if (needle.length === 0) {
      continue
    }
    const at = flat.indexOf(needle)
    if (at >= 0) {
      return text.slice(at, at + needle.length)
    }
  }
  for (const match of text.matchAll(DRIVE_USERS)) {
    if (match[1].toLowerCase() !== 'public') {
      return match[0]
    }
  }
  for (const match of text.matchAll(POSIX_HOME)) {
    return match[1]
  }
  return null
}

function meets(rect: Rect, clip: Rect): boolean {
  if (rect.width <= 0 || rect.height <= 0) {
    return false
  }
  return (
    rect.x < clip.x + clip.width &&
    rect.x + rect.width > clip.x &&
    rect.y < clip.y + clip.height &&
    rect.y + rect.height > clip.y
  )
}

/** The text of the unmasked items with a visible rect that meets the clip, one per line. */
export function clipText(items: readonly TextItem[], clip: Rect): string {
  return items
    .filter((item) => !item.masked && item.rects.some((rect) => meets(rect, clip)))
    .map((item) => item.text)
    .join('\n')
}
