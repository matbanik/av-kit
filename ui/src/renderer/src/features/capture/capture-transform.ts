import type { Annotation } from './capture-annotate'
import { clampImagePoint, type ImagePoint } from './capture-fit-map'
import { FONT_SCRUB_MAX } from './capture-scrub'
import { textBackgroundBox } from './capture-text-metrics'

/** TRANSFORM (MEU-100): resize handles for the box marks; pure, no React. */
export type HandleId = 'nw' | 'n' | 'ne' | 'e' | 'se' | 's' | 'sw' | 'w'

/** Visible handle square side, in CSS px at every zoom. */
export const RESIZE_HANDLE_CSS = 8
/** Hit square side, in CSS px at every zoom. */
export const RESIZE_HIT_CSS = 12

export type BoxMark = Extract<Annotation, { type: 'rect' | 'highlight' | 'pixelate' | 'eraser' }>
export type TextMark = Extract<Annotation, { type: 'text' }>

/** A text plate corner: TEXT_SCALE has no edge handles. */
export type TextCorner = 'nw' | 'ne' | 'se' | 'sw'

type Box = { x: number; y: number; width: number; height: number }

const CORNERS: ReadonlySet<HandleId> = new Set(['nw', 'ne', 'se', 'sw'])

export function isBoxMark(mark: Annotation): mark is BoxMark {
  return mark.type === 'rect' || mark.type === 'highlight' || mark.type === 'pixelate' || mark.type === 'eraser'
}

export function boxHandlePoints({ x, y, width, height }: Box): Record<HandleId, ImagePoint> {
  const right = x + width
  const bottom = y + height
  const midX = x + width / 2
  const midY = y + height / 2
  return {
    nw: { x, y },
    n: { x: midX, y },
    ne: { x: right, y },
    e: { x: right, y: midY },
    se: { x: right, y: bottom },
    s: { x: midX, y: bottom },
    sw: { x, y: bottom },
    w: { x, y: midY },
  }
}

/**
 * One axis of a resize: the handle moves edge `moving` to `to` while `stationary` stays. A collapse steps the
 * moving edge one pixel off (`step` is +1 for e/s, -1 for w/n), or to the other side when that leaves `0..max`.
 */
function resizeAxis(stationary: number, to: number, step: 1 | -1, max: number): { start: number; size: number } {
  let moving = to
  if (moving === stationary) {
    moving = stationary + step
    if (moving < 0 || moving > max) {
      moving = stationary - step
    }
  }
  return { start: Math.min(stationary, moving), size: Math.abs(moving - stationary) }
}

/** A copy of `mark` with the edges `handle` names moved to `point`; the opposite edges never move. */
export function resizeBox<T extends BoxMark>(mark: T, handle: HandleId, point: ImagePoint, imageW: number, imageH: number): T {
  const p = clampImagePoint({ x: Math.round(point.x), y: Math.round(point.y) }, imageW, imageH)
  const next = { ...mark }
  const maxX = Math.max(0, imageW - 1)
  const maxY = Math.max(0, imageH - 1)
  if (handle.includes('w') || handle.includes('e')) {
    const west = handle.includes('w')
    const axis = resizeAxis(west ? mark.x + mark.width : mark.x, p.x, west ? -1 : 1, maxX)
    next.x = axis.start
    next.width = axis.size
  }
  if (handle.includes('n') || handle.includes('s')) {
    const north = handle.includes('n')
    const axis = resizeAxis(north ? mark.y + mark.height : mark.y, p.y, north ? -1 : 1, maxY)
    next.y = axis.start
    next.height = axis.size
  }
  return next
}

/** The handle whose CSS hit square holds the pointer, nearest first; a corner wins an exact tie with an edge. */
export function hitResizeHandle(
  points: Partial<Record<HandleId, ImagePoint>>,
  view: { cssX: number; cssY: number; scale: number; ox: number; oy: number },
): HandleId | null {
  const half = RESIZE_HIT_CSS / 2
  let best: { id: HandleId; d: number } | null = null
  for (const [id, point] of Object.entries(points) as Array<[HandleId, ImagePoint | undefined]>) {
    if (point === undefined) {
      continue
    }
    const dx = view.cssX - (view.ox + point.x * view.scale)
    const dy = view.cssY - (view.oy + point.y * view.scale)
    if (Math.abs(dx) > half || Math.abs(dy) > half) {
      continue
    }
    const d = Math.hypot(dx, dy)
    if (best === null || d < best.d || (d === best.d && CORNERS.has(id) && !CORNERS.has(best.id))) {
      best = { id, d }
    }
  }
  return best?.id ?? null
}

export function cursorForHandle(handle: HandleId): 'nwse-resize' | 'nesw-resize' | 'ns-resize' | 'ew-resize' {
  if (handle === 'nw' || handle === 'se') {
    return 'nwse-resize'
  }
  if (handle === 'ne' || handle === 'sw') {
    return 'nesw-resize'
  }
  return handle === 'n' || handle === 's' ? 'ns-resize' : 'ew-resize'
}

const OPPOSITE_CORNER: Record<TextCorner, TextCorner> = { nw: 'se', ne: 'sw', se: 'nw', sw: 'ne' }

/** TEXT_SCALE (MEU-101): the four corners of the text plate, in image px. */
export function textPlateHandlePoints(mark: TextMark): Record<TextCorner, ImagePoint> {
  const { x, y, width, height } = textBackgroundBox(mark)
  return {
    nw: { x, y },
    ne: { x: x + width, y },
    se: { x: x + width, y: y + height },
    sw: { x, y: y + height },
  }
}

/**
 * A copy of `mark` scaled by dragging plate corner `handle` to `point`: `font_size` follows the larger of the
 * two axis ratios about the opposite corner, `1..FONT_SCRUB_MAX`, and `x`/`y` shift so that corner stays. The
 * plate never flips, and `x`/`y` are not clamped: a grown plate at the image edge needs the anchor off-image.
 */
export function scaleTextMark(mark: TextMark, handle: TextCorner, point: ImagePoint, imageW: number, imageH: number): TextMark {
  const p = clampImagePoint({ x: Math.round(point.x), y: Math.round(point.y) }, imageW, imageH)
  const plate = textBackgroundBox(mark)
  const corner = OPPOSITE_CORNER[handle]
  const anchor = textPlateHandlePoints(mark)[corner]
  const ratio = Math.max(Math.abs(p.x - anchor.x) / plate.width, Math.abs(p.y - anchor.y) / plate.height)
  const fontSize = Math.min(FONT_SCRUB_MAX, Math.max(1, Math.round(mark.font_size * ratio)))
  const moved = textPlateHandlePoints({ ...mark, font_size: fontSize })[corner]
  return {
    ...mark,
    x: Math.round(mark.x + anchor.x - moved.x),
    y: Math.round(mark.y + anchor.y - moved.y),
    font_size: fontSize,
  }
}
