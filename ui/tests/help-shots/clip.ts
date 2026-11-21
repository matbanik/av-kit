/**
 * MEU-162 (Session 99, HELP_SHOTS_GEN, D-1292) the clip of one help screenshot.
 *
 * `shotClip(boxes, viewport)` returns the union of the target boxes plus a 24 px margin. It never
 * clamps a target away: a target box that is not fully inside the viewport is an error that
 * names the target, and so is a clip wider than 1280 or taller than 900 CSS px. Only the margin
 * is clamped to the viewport. The caller writes no file on an error (S9).
 */

export type Rect = { x: number; y: number; width: number; height: number }
export type TargetBox = Rect & { target: string }
export type ClipResult = { ok: true; clip: Rect } | { ok: false; error: string }

export const CLIP_MARGIN = 24
export const CLIP_MAX_WIDTH = 1280
export const CLIP_MAX_HEIGHT = 900

export function shotClip(
  boxes: readonly TargetBox[],
  viewport: { width: number; height: number },
): ClipResult {
  if (boxes.length === 0) {
    return { ok: false, error: 'no target boxes' }
  }
  for (const box of boxes) {
    const inside =
      box.width > 0 &&
      box.height > 0 &&
      box.x >= 0 &&
      box.y >= 0 &&
      box.x + box.width <= viewport.width &&
      box.y + box.height <= viewport.height
    if (!inside) {
      return {
        ok: false,
        error: `target ${box.target} at ${box.x},${box.y} ${box.width} x ${box.height} is not fully inside the ${viewport.width} x ${viewport.height} viewport`,
      }
    }
  }
  const left = Math.min(...boxes.map((b) => b.x))
  const top = Math.min(...boxes.map((b) => b.y))
  const right = Math.max(...boxes.map((b) => b.x + b.width))
  const bottom = Math.max(...boxes.map((b) => b.y + b.height))
  const x = Math.max(0, Math.floor(left - CLIP_MARGIN))
  const y = Math.max(0, Math.floor(top - CLIP_MARGIN))
  const width = Math.min(viewport.width, Math.ceil(right + CLIP_MARGIN)) - x
  const height = Math.min(viewport.height, Math.ceil(bottom + CLIP_MARGIN)) - y
  if (width > CLIP_MAX_WIDTH || height > CLIP_MAX_HEIGHT) {
    return {
      ok: false,
      error: `the clip is ${width} x ${height}, over ${CLIP_MAX_WIDTH} x ${CLIP_MAX_HEIGHT}`,
    }
  }
  return { ok: true, clip: { x, y, width, height } }
}
