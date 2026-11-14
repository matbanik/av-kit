/** MODIFIERS (MEU-143, D-753): Shift and Alt while drawing, dragging an arrow end and resizing a box. Pure. */
import { drivingFromHeight, drivingFromWidth, largestDriving, ratioBox } from './capture-crop'
import { clampImagePoint, type ImagePoint } from './capture-fit-map'
import { resizeBox, type BoxMark, type HandleId } from './capture-transform'

/**
 * A bounded tool's draw. `square` gives the box the longer side, cut to what fits inside the image in the
 * drag's direction. `centre` makes the anchor the centre, with the half-extents cut so the box stays inside
 * the image. Both can apply together; with neither the points come back as they are.
 */
export function drawBounds(
  anchor: ImagePoint,
  point: ImagePoint,
  mods: { square: boolean; centre: boolean },
  imageW: number,
  imageH: number,
): { start: ImagePoint; end: ImagePoint } {
  if (!mods.square && !mods.centre) {
    return { start: anchor, end: point }
  }
  const maxX = Math.max(0, imageW - 1)
  const maxY = Math.max(0, imageH - 1)
  const dx = point.x - anchor.x
  const dy = point.y - anchor.y
  const sx = dx < 0 ? -1 : 1
  const sy = dy < 0 ? -1 : 1
  let ex = Math.abs(dx)
  let ey = Math.abs(dy)
  if (mods.square) {
    ex = Math.max(ex, ey)
    ey = ex
  }
  if (mods.centre) {
    ex = Math.min(ex, anchor.x, maxX - anchor.x)
    ey = Math.min(ey, anchor.y, maxY - anchor.y)
  } else {
    ex = Math.min(ex, sx > 0 ? maxX - anchor.x : anchor.x)
    ey = Math.min(ey, sy > 0 ? maxY - anchor.y : anchor.y)
  }
  if (mods.square) {
    ex = Math.min(ex, ey)
    ey = ex
  }
  ex = Math.max(0, ex)
  ey = Math.max(0, ey)
  const end = { x: anchor.x + sx * ex, y: anchor.y + sy * ey }
  const start = mods.centre ? { x: anchor.x - sx * ex, y: anchor.y - sy * ey } : anchor
  return { start, end }
}

function inside(p: ImagePoint, maxX: number, maxY: number): boolean {
  return p.x >= 0 && p.x <= maxX && p.y >= 0 && p.y <= maxY
}

/**
 * An arrow end snapped about `fixed`: the length stays, the angle rounds to the nearest 45 degrees, the end
 * rounds to whole pixels, and the arrow is shortened along that angle until the end lies inside the image.
 */
export function snapArrowEnd(fixed: ImagePoint, moving: ImagePoint, imageW: number, imageH: number): ImagePoint {
  const maxX = Math.max(0, imageW - 1)
  const maxY = Math.max(0, imageH - 1)
  const length = Math.hypot(moving.x - fixed.x, moving.y - fixed.y)
  if (length === 0) {
    return clampImagePoint({ x: Math.round(moving.x), y: Math.round(moving.y) }, imageW, imageH)
  }
  const step = Math.PI / 4
  const angle = Math.round(Math.atan2(moving.y - fixed.y, moving.x - fixed.x) / step) * step
  let ux = Math.cos(angle)
  let uy = Math.sin(angle)
  if (Math.abs(ux) < 1e-9) ux = 0
  if (Math.abs(uy) < 1e-9) uy = 0
  let reach = length
  if (ux > 0) reach = Math.min(reach, (maxX - fixed.x) / ux)
  if (ux < 0) reach = Math.min(reach, fixed.x / -ux)
  if (uy > 0) reach = Math.min(reach, (maxY - fixed.y) / uy)
  if (uy < 0) reach = Math.min(reach, fixed.y / -uy)
  reach = Math.max(0, reach)
  const at = (l: number): ImagePoint => ({ x: Math.round(fixed.x + l * ux) + 0, y: Math.round(fixed.y + l * uy) + 0 })
  let end = at(reach)
  while (!inside(end, maxX, maxY) && reach > 0) {
    reach = Math.max(0, reach - 0.5)
    end = at(reach)
  }
  return inside(end, maxX, maxY) ? end : clampImagePoint(end, imageW, imageH)
}

/**
 * A corner-handle resize that keeps the start box's ratio as the crop's corner does (CROP_RATIO): the larger
 * relative change of width or height drives, `ratioBox` builds the box, the opposite corner stays, and the
 * box is cut to the image. An edge handle resizes as it does without Shift.
 */
export function keepRatioResize<T extends BoxMark>(start: T, handle: HandleId, point: ImagePoint, imageW: number, imageH: number): T {
  const corner = handle === 'nw' || handle === 'ne' || handle === 'se' || handle === 'sw'
  if (!corner || start.width <= 0 || start.height <= 0) {
    return resizeBox(start, handle, point, imageW, imageH)
  }
  const p = clampImagePoint({ x: Math.round(point.x), y: Math.round(point.y) }, imageW, imageH)
  const maxX = Math.max(0, imageW - 1)
  const maxY = Math.max(0, imageH - 1)
  const ratio = start.width / start.height
  const west = handle.includes('w')
  const north = handle.includes('n')
  const right = start.x + start.width
  const bottom = start.y + start.height
  const proposedW = Math.max(1, west ? right - p.x : p.x - start.x)
  const proposedH = Math.max(1, north ? bottom - p.y : p.y - start.y)
  const relX = Math.abs(proposedW - start.width) / start.width
  const relY = Math.abs(proposedH - start.height) / start.height
  const driving = relX >= relY ? drivingFromWidth(proposedW, ratio) : drivingFromHeight(proposedH, ratio)
  const sMax = largestDriving(ratio, west ? right : maxX - start.x, north ? bottom : maxY - start.y)
  if (sMax < 1) {
    return { ...start }
  }
  const size = ratioBox(Math.min(Math.max(driving, 1), sMax), ratio)
  return {
    ...start,
    x: west ? right - size.width : start.x,
    y: north ? bottom - size.height : start.y,
    width: size.width,
    height: size.height,
  }
}
