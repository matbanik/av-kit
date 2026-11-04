import type { Annotation } from './capture-annotate'
import { clampImagePoint, type ImagePoint } from './capture-fit-map'
import { arrowheadVertices } from './capture-arrow-head'
import { textBackgroundBox } from './capture-text-metrics'
import { boxHandlePoints, hitResizeHandle, isBoxMark, textPlateHandlePoints, type HandleId } from './capture-transform'

export const HANDLE_RADIUS_CSS = 5
export const HIT_RADIUS_CSS = 10
export const HIT_PADDING_CSS = 6

export type HitResult =
  | { kind: 'handle'; end: 'from' | 'to'; index: number }
  | { kind: 'body'; index: number }
  | { kind: 'resize'; handle: HandleId; index: number }

export type HitTestInput = {
  cssX: number
  cssY: number
  scale: number
  ox: number
  oy: number
  imageW: number
  imageH: number
  annotations: Annotation[]
  selectedIndex: number | null
}

function imageToCss(x: number, y: number, scale: number, ox: number, oy: number): { x: number; y: number } {
  return { x: ox + x * scale, y: oy + y * scale }
}

function inImageCss(input: HitTestInput): boolean {
  if (input.scale <= 0) {
    return false
  }
  return (
    input.cssX >= input.ox &&
    input.cssY >= input.oy &&
    input.cssX < input.ox + input.imageW * input.scale &&
    input.cssY < input.oy + input.imageH * input.scale
  )
}

function dist(ax: number, ay: number, bx: number, by: number): number {
  return Math.hypot(ax - bx, ay - by)
}

function distToSegment(px: number, py: number, x1: number, y1: number, x2: number, y2: number): number {
  const dx = x2 - x1
  const dy = y2 - y1
  const len2 = dx * dx + dy * dy
  if (len2 === 0) {
    return dist(px, py, x1, y1)
  }
  const t = Math.max(0, Math.min(1, ((px - x1) * dx + (py - y1) * dy) / len2))
  return dist(px, py, x1 + t * dx, y1 + t * dy)
}

function pointInTriangle(
  px: number,
  py: number,
  ax: number,
  ay: number,
  bx: number,
  by: number,
  cx: number,
  cy: number,
): boolean {
  const area = (bx - ax) * (cy - ay) - (cx - ax) * (by - ay)
  if (area === 0) {
    return false
  }
  const s = ((px - ax) * (cy - ay) - (py - ay) * (cx - ax)) / area
  const t = ((ax - px) * (by - ay) - (ay - py) * (bx - ax)) / area
  return s >= 0 && t >= 0 && s + t <= 1
}

function distToRectOutline(px: number, py: number, x: number, y: number, w: number, h: number): number {
  const x1 = x + w
  const y1 = y + h
  if (w <= 0 || h <= 0) {
    return dist(px, py, x, y)
  }
  const inside = px >= x && px <= x1 && py >= y && py <= y1
  if (inside) {
    return Math.min(px - x, x1 - px, py - y, y1 - py)
  }
  const clampedX = Math.max(x, Math.min(x1, px))
  const clampedY = Math.max(y, Math.min(y1, py))
  return dist(px, py, clampedX, clampedY)
}

function inPaddedRect(
  px: number,
  py: number,
  x: number,
  y: number,
  w: number,
  h: number,
  pad: number,
): boolean {
  return px >= x - pad && py >= y - pad && px <= x + w + pad && py <= y + h + pad
}

function hitArrowBody(mark: Extract<Annotation, { type: 'arrow' }>, input: HitTestInput): boolean {
  const from = imageToCss(mark.from[0], mark.from[1], input.scale, input.ox, input.oy)
  const to = imageToCss(mark.to[0], mark.to[1], input.scale, input.ox, input.oy)
  if (distToSegment(input.cssX, input.cssY, from.x, from.y, to.x, to.y) <= HIT_RADIUS_CSS) {
    return true
  }
  const verts = arrowheadVertices(mark.from, mark.to, mark.stroke_width)
  const a = imageToCss(verts.tip[0], verts.tip[1], input.scale, input.ox, input.oy)
  const b = imageToCss(verts.left[0], verts.left[1], input.scale, input.ox, input.oy)
  const c = imageToCss(verts.right[0], verts.right[1], input.scale, input.ox, input.oy)
  return pointInTriangle(input.cssX, input.cssY, a.x, a.y, b.x, b.y, c.x, c.y)
}

export function bodyHandleImagePoint(mark: Annotation): ImagePoint {
  if (mark.type === 'arrow') {
    return {
      x: (mark.from[0] + mark.to[0]) / 2,
      y: (mark.from[1] + mark.to[1]) / 2,
    }
  }
  if (mark.type === 'text') {
    const plate = textBackgroundBox({ x: mark.x, y: mark.y, text: mark.text, font_size: mark.font_size })
    return { x: plate.x + plate.width / 2, y: plate.y + plate.height / 2 }
  }
  return { x: mark.x + mark.width / 2, y: mark.y + mark.height / 2 }
}

function textHitBoxCss(mark: Extract<Annotation, { type: 'text' }>, input: HitTestInput): {
  x: number
  y: number
  w: number
  h: number
} {
  const plate = textBackgroundBox({ x: mark.x, y: mark.y, text: mark.text, font_size: mark.font_size })
  const origin = imageToCss(plate.x, plate.y, input.scale, input.ox, input.oy)
  let x = origin.x
  let y = origin.y
  let w = Math.max(1, plate.width * input.scale)
  let h = Math.max(1, plate.height * input.scale)
  const min = 2 * HIT_RADIUS_CSS
  if (w < min) {
    x -= (min - w) / 2
    w = min
  }
  if (h < min) {
    y -= (min - h) / 2
    h = min
  }
  return { x, y, w, h }
}

function hitBody(mark: Annotation, input: HitTestInput): boolean {
  if (mark.type === 'arrow') {
    return hitArrowBody(mark, input)
  }
  if (mark.type === 'text') {
    const anchor = imageToCss(mark.x, mark.y, input.scale, input.ox, input.oy)
    if (dist(input.cssX, input.cssY, anchor.x, anchor.y) <= HIT_RADIUS_CSS) {
      return true
    }
    const box = textHitBoxCss(mark, input)
    return inPaddedRect(input.cssX, input.cssY, box.x, box.y, box.w, box.h, HIT_PADDING_CSS)
  }
  const origin = imageToCss(mark.x, mark.y, input.scale, input.ox, input.oy)
  const w = mark.width * input.scale
  const h = mark.height * input.scale
  // REGION_EDIT: a region mark is a filled body, like a highlight.
  if (mark.type === 'highlight' || mark.type === 'pixelate' || mark.type === 'eraser') {
    return inPaddedRect(input.cssX, input.cssY, origin.x, origin.y, w, h, HIT_PADDING_CSS)
  }
  return distToRectOutline(input.cssX, input.cssY, origin.x, origin.y, w, h) <= Math.max(HIT_RADIUS_CSS, HIT_PADDING_CSS)
}

function selectedHandle(input: HitTestInput): HitResult | null {
  if (input.selectedIndex === null || input.selectedIndex < 0) {
    return null
  }
  const mark = input.annotations[input.selectedIndex]
  if (mark === undefined) {
    return null
  }
  if (mark.type === 'arrow') {
    const from = imageToCss(mark.from[0], mark.from[1], input.scale, input.ox, input.oy)
    const to = imageToCss(mark.to[0], mark.to[1], input.scale, input.ox, input.oy)
    const dFrom = dist(input.cssX, input.cssY, from.x, from.y)
    const dTo = dist(input.cssX, input.cssY, to.x, to.y)
    const fromHit = dFrom <= HANDLE_RADIUS_CSS
    const toHit = dTo <= HANDLE_RADIUS_CSS
    if (!fromHit && !toHit) {
      return null
    }
    if (toHit && (!fromHit || dTo <= dFrom)) {
      return { kind: 'handle', end: 'to', index: input.selectedIndex }
    }
    return { kind: 'handle', end: 'from', index: input.selectedIndex }
  }
  const body = bodyHandleImagePoint(mark)
  const handle = imageToCss(body.x, body.y, input.scale, input.ox, input.oy)
  if (dist(input.cssX, input.cssY, handle.x, handle.y) <= HANDLE_RADIUS_CSS) {
    return { kind: 'body', index: input.selectedIndex }
  }
  return null
}

function selectedResizeHandle(input: HitTestInput): HitResult | null {
  if (input.selectedIndex === null || input.selectedIndex < 0) {
    return null
  }
  const mark = input.annotations[input.selectedIndex]
  if (mark === undefined) {
    return null
  }
  // TEXT_SCALE: a text mark has the four plate corners only.
  const points = isBoxMark(mark) ? boxHandlePoints(mark) : mark.type === 'text' ? textPlateHandlePoints(mark) : null
  if (points === null) {
    return null
  }
  const handle = hitResizeHandle(points, input)
  return handle === null ? null : { kind: 'resize', handle, index: input.selectedIndex }
}

export function hitTestMarks(input: HitTestInput): HitResult | null {
  if (!inImageCss(input)) {
    return null
  }
  const handle = selectedHandle(input)
  if (handle !== null) {
    return handle
  }
  // HIT_ORDER: the selected box or text mark's resize handles beat every body, the topmost included.
  const resize = selectedResizeHandle(input)
  if (resize !== null) {
    return resize
  }
  for (let i = input.annotations.length - 1; i >= 0; i -= 1) {
    const mark = input.annotations[i]
    if (mark !== undefined && hitBody(mark, input)) {
      return { kind: 'body', index: i }
    }
  }
  return null
}

function clampDelta(
  minX: number,
  maxX: number,
  minY: number,
  maxY: number,
  dx: number,
  dy: number,
  imageW: number,
  imageH: number,
): { dx: number; dy: number } {
  const maxBoundX = Math.max(0, imageW - 1)
  const maxBoundY = Math.max(0, imageH - 1)
  return {
    dx: Math.min(maxBoundX - maxX, Math.max(-minX, dx)),
    dy: Math.min(maxBoundY - maxY, Math.max(-minY, dy)),
  }
}

export function translateBody<T extends Annotation>(
  mark: T,
  dx: number,
  dy: number,
  imageW: number,
  imageH: number,
): T {
  if (mark.type === 'arrow') {
    const minX = Math.min(mark.from[0], mark.to[0])
    const maxX = Math.max(mark.from[0], mark.to[0])
    const minY = Math.min(mark.from[1], mark.to[1])
    const maxY = Math.max(mark.from[1], mark.to[1])
    const adj = clampDelta(minX, maxX, minY, maxY, dx, dy, imageW, imageH)
    return {
      ...mark,
      from: [mark.from[0] + adj.dx, mark.from[1] + adj.dy],
      to: [mark.to[0] + adj.dx, mark.to[1] + adj.dy],
    }
  }
  if (mark.type === 'text') {
    const next = clampImagePoint({ x: mark.x + dx, y: mark.y + dy }, imageW, imageH)
    return { ...mark, x: next.x, y: next.y }
  }
  const origin = clampImagePoint({ x: mark.x + dx, y: mark.y + dy }, imageW, imageH)
  return { ...mark, x: origin.x, y: origin.y }
}

export function moveEndpoint(
  mark: Annotation,
  end: 'from' | 'to',
  point: ImagePoint,
  imageW: number,
  imageH: number,
): Annotation | null {
  if (mark.type !== 'arrow') {
    return mark
  }
  const clamped = clampImagePoint(point, imageW, imageH)
  const from: [number, number] = end === 'from' ? [clamped.x, clamped.y] : [mark.from[0], mark.from[1]]
  const to: [number, number] = end === 'to' ? [clamped.x, clamped.y] : [mark.to[0], mark.to[1]]
  const originalLen = Math.hypot(mark.to[0] - mark.from[0], mark.to[1] - mark.from[1])
  const nextLen = Math.hypot(to[0] - from[0], to[1] - from[1])
  if (originalLen > 0 && nextLen === 0) {
    return null
  }
  return { ...mark, from, to }
}

export function markLabel(mark: Annotation, index: number): string {
  if (mark.type === 'arrow') {
    return `Arrow ${index + 1}`
  }
  if (mark.type === 'rect') {
    return `Box ${index + 1}`
  }
  if (mark.type === 'highlight') {
    return `Highlight ${index + 1}`
  }
  if (mark.type === 'pixelate') {
    return `Pixelate ${index + 1}`
  }
  if (mark.type === 'eraser') {
    return `Eraser ${index + 1}`
  }
  return `Text ${index + 1}`
}
