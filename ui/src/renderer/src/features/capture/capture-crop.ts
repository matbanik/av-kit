/**
 * MEU-131 crop geometry (plan 2026-11-10-gui-capture-crop-tool §Crop geometry, D-511 to D-514). Pure: no
 * React, no DOM. Every box it returns is in whole original px, inside the image, each side at least
 * CROP_MIN_PX, so `resolve_region` accepts it unclamped (`capture.py:159-194`).
 */
import type { HandleId } from './capture-transform'

/** A crop box in whole original px. */
export type CropBox = { x: number; y: number; width: number; height: number }
/** A size in whole px: a ratio box before it is placed. */
export type CropSize = { width: number; height: number }
/** The shot's size in original px. */
export type CropImage = { width: number; height: number }
export type CropField = 'x' | 'y' | 'width' | 'height'
export type AspectPresetId = 'free' | 'original' | 'square' | '16:9' | '4:3' | '3:2'

/** CROP_PRESETS: the Aspect options, in order. */
export const ASPECT_PRESETS: readonly { readonly id: AspectPresetId; readonly label: string }[] = [
  { id: 'free', label: 'Free' },
  { id: 'original', label: 'Original' },
  { id: 'square', label: 'Square' },
  { id: '16:9', label: '16:9' },
  { id: '4:3', label: '4:3' },
  { id: '3:2', label: '3:2' },
]

/** CROP_MIN: equal to CAPTURE_MIN_EDGE_PX (`capture.py:27`). */
export const CROP_MIN_PX = 8

/** CROP_ROUND: the one rounding of the tool, half up each way (2.5 → 3, −2.5 → −2). */
export function roundHalfUp(v: number): number {
  return Math.floor(v + 0.5)
}

function clamp(v: number, lo: number, hi: number): number {
  return Math.min(Math.max(v, lo), hi)
}

/** CROP_MIN: an image each of whose sides is at least the minimum. */
export function cropEligible(imageW: number, imageH: number): boolean {
  return imageW >= CROP_MIN_PX && imageH >= CROP_MIN_PX
}

/** The whole image as a crop box. */
export function wholeImage(image: CropImage): CropBox {
  return { x: 0, y: 0, width: image.width, height: image.height }
}

/** CROP_MIN: round, cut the size to the image, raise it to the minimum, then shift the origin inside. */
export function clampCrop(box: CropBox, imageW: number, imageH: number): CropBox {
  const width = Math.max(CROP_MIN_PX, Math.min(roundHalfUp(box.width), imageW))
  const height = Math.max(CROP_MIN_PX, Math.min(roundHalfUp(box.height), imageH))
  const x = clamp(roundHalfUp(box.x), 0, imageW - width)
  const y = clamp(roundHalfUp(box.y), 0, imageH - height)
  return { x, y, width, height }
}

/** CROP_RATIO: the box of ratio `r` built from the whole driving side `s` (the height when r ≥ 1, else the width). */
export function ratioBox(s: number, r: number): CropSize {
  return r >= 1 ? { width: roundHalfUp(s * r), height: s } : { width: s, height: roundHalfUp(s / r) }
}

/** CROP_RATIO: exact; true exactly when the box is the `ratioBox` of its driving side. */
export function fitsRatio(box: CropSize, r: number): boolean {
  return r >= 1 ? box.width === roundHalfUp(box.height * r) : box.height === roundHalfUp(box.width / r)
}

/** The largest whole driving side whose `ratioBox` fits within `maxW × maxH`; 0 when none does. */
function largestDriving(r: number, maxW: number, maxH: number): number {
  const limit = Math.floor(r >= 1 ? maxH : maxW)
  const otherMax = r >= 1 ? maxW : maxH
  const other = (s: number): number => (r >= 1 ? ratioBox(s, r).width : ratioBox(s, r).height)
  let s = Math.max(0, Math.min(limit, Math.floor(r >= 1 ? (otherMax + 0.5) / r : (otherMax + 0.5) * r)))
  while (s > 0 && other(s) > otherMax) {
    s -= 1
  }
  while (s + 1 <= limit && other(s + 1) <= otherMax) {
    s += 1
  }
  return s
}

/** CROP_RATIO: the smallest box of ratio `r` with both sides at least the minimum. */
export function ratioMinBox(r: number): CropSize {
  return ratioBox(CROP_MIN_PX, r)
}

/** CROP_RATIO: the largest box of ratio `r` inside a `imageW × imageH` image. */
export function ratioLargestBox(r: number, imageW: number, imageH: number): CropSize {
  return ratioBox(largestDriving(r, imageW, imageH), r)
}

/** CROP_RATIO: the ratio has a box inside the image with both sides at least the minimum. */
export function ratioFeasible(r: number, imageW: number, imageH: number): boolean {
  return largestDriving(r, imageW, imageH) >= CROP_MIN_PX
}

/** The driving side a width of `v` gives under ratio `r`. */
function drivingFromWidth(v: number, r: number): number {
  return r >= 1 ? roundHalfUp(v / r) : v
}

/** The driving side a height of `v` gives under ratio `r`. */
function drivingFromHeight(v: number, r: number): number {
  return r >= 1 ? v : roundHalfUp(v * r)
}

/** CROP_MOVE: keep the size and clamp the origin inside the image. */
export function moveCrop(start: CropBox, dx: number, dy: number, image: CropImage): CropBox {
  return clampCrop({ ...start, x: start.x + roundHalfUp(dx), y: start.y + roundHalfUp(dy) }, image.width, image.height)
}

/** CROP_NUDGE: a move by whole pixels. */
export function nudgeCrop(box: CropBox, dx: number, dy: number, image: CropImage): CropBox {
  return moveCrop(box, dx, dy, image)
}

/**
 * CROP_HANDLES and CROP_RATIO: the box `start` with `handle` dragged by `(dx, dy)` image px. The opposite edges stay;
 * an edge stops at the minimum and at the image edge, and the box never flips. With a ratio the box is a `ratioBox`.
 */
export function resizeCrop(
  start: CropBox,
  handle: HandleId,
  dx: number,
  dy: number,
  image: CropImage,
  ratio: number | null,
): CropBox {
  const W = image.width
  const H = image.height
  const rdx = roundHalfUp(dx)
  const rdy = roundHalfUp(dy)
  const right = start.x + start.width
  const bottom = start.y + start.height
  const horizontal = handle.includes('e') || handle.includes('w')
  const vertical = handle.includes('n') || handle.includes('s')
  const west = handle.includes('w')
  const north = handle.includes('n')
  if (ratio === null) {
    let x = start.x
    let y = start.y
    let r = right
    let b = bottom
    if (handle.includes('e')) {
      r = clamp(right + rdx, start.x + CROP_MIN_PX, W)
    }
    if (west) {
      x = clamp(start.x + rdx, 0, right - CROP_MIN_PX)
    }
    if (handle.includes('s')) {
      b = clamp(bottom + rdy, start.y + CROP_MIN_PX, H)
    }
    if (north) {
      y = clamp(start.y + rdy, 0, bottom - CROP_MIN_PX)
    }
    return { x, y, width: r - x, height: b - y }
  }
  const proposedW = start.width + (west ? -rdx : rdx)
  const proposedH = start.height + (north ? -rdy : rdy)
  if (horizontal && vertical) {
    const availW = west ? right : W - start.x
    const availH = north ? bottom : H - start.y
    const sMax = largestDriving(ratio, availW, availH)
    if (sMax < CROP_MIN_PX) {
      return clampCrop(start, W, H)
    }
    const relX = Math.abs(proposedW - start.width) / start.width
    const relY = Math.abs(proposedH - start.height) / start.height
    const s0 = relX >= relY ? drivingFromWidth(proposedW, ratio) : drivingFromHeight(proposedH, ratio)
    const size = ratioBox(clamp(s0, CROP_MIN_PX, sMax), ratio)
    return {
      x: west ? right - size.width : start.x,
      y: north ? bottom - size.height : start.y,
      width: size.width,
      height: size.height,
    }
  }
  if (horizontal) {
    const sMax = largestDriving(ratio, west ? right : W - start.x, H)
    if (sMax < CROP_MIN_PX) {
      return clampCrop(start, W, H)
    }
    const size = ratioBox(clamp(drivingFromWidth(proposedW, ratio), CROP_MIN_PX, sMax), ratio)
    const centreY = start.y + start.height / 2
    return {
      x: west ? right - size.width : start.x,
      y: clamp(roundHalfUp(centreY - size.height / 2), 0, H - size.height),
      width: size.width,
      height: size.height,
    }
  }
  const sMax = largestDriving(ratio, W, north ? bottom : H - start.y)
  if (sMax < CROP_MIN_PX) {
    return clampCrop(start, W, H)
  }
  const size = ratioBox(clamp(drivingFromHeight(proposedH, ratio), CROP_MIN_PX, sMax), ratio)
  const centreX = start.x + start.width / 2
  return {
    x: clamp(roundHalfUp(centreX - size.width / 2), 0, W - size.width),
    y: north ? bottom - size.height : start.y,
    width: size.width,
    height: size.height,
  }
}

/**
 * CROP_DRAW: the box between two image points in any direction, normalised and clamped. A drag under the minimum
 * on an axis grows to it from the anchor in the drag's direction; a down and up at the same point is `null`.
 */
export function drawCrop(
  anchor: { x: number; y: number },
  point: { x: number; y: number },
  image: CropImage,
  ratio: number | null,
): CropBox | null {
  const ax = roundHalfUp(anchor.x)
  const ay = roundHalfUp(anchor.y)
  const px = roundHalfUp(point.x)
  const py = roundHalfUp(point.y)
  if (ax === px && ay === py) {
    return null
  }
  const dirX = px >= ax ? 1 : -1
  const dirY = py >= ay ? 1 : -1
  const dx = Math.abs(px - ax)
  const dy = Math.abs(py - ay)
  let size: CropSize
  if (ratio === null) {
    size = { width: Math.max(dx, CROP_MIN_PX), height: Math.max(dy, CROP_MIN_PX) }
  } else {
    const availW = dirX > 0 ? image.width - ax : ax
    const availH = dirY > 0 ? image.height - ay : ay
    const sMax = largestDriving(ratio, availW, availH)
    const s0 = dx >= dy * ratio ? drivingFromWidth(dx, ratio) : drivingFromHeight(dy, ratio)
    size = ratioBox(sMax >= CROP_MIN_PX ? clamp(s0, CROP_MIN_PX, sMax) : CROP_MIN_PX, ratio)
  }
  const box = {
    x: dirX > 0 ? ax : ax - size.width,
    y: dirY > 0 ? ay : ay - size.height,
    width: size.width,
    height: size.height,
  }
  return clampCrop(box, image.width, image.height)
}

/** CROP_PRESETS: the preset's ratio on this image, flipped when swapped; `null` for Free. */
export function presetRatio(preset: AspectPresetId, image: CropImage, swapped: boolean): number | null {
  let r: number
  switch (preset) {
    case 'free':
      return null
    case 'original':
      r = image.width / image.height
      break
    case 'square':
      r = 1
      break
    case '16:9':
      r = 16 / 9
      break
    case '4:3':
      r = 4 / 3
      break
    case '3:2':
      r = 3 / 2
      break
  }
  return swapped ? 1 / r : r
}

/** CROP_PRESETS: Free always; otherwise the preset's ratio is feasible on this image. */
export function presetFeasible(preset: AspectPresetId, image: CropImage, swapped: boolean): boolean {
  const r = presetRatio(preset, image, swapped)
  return r === null || ratioFeasible(r, image.width, image.height)
}

/**
 * CROP_PRESETS: Free keeps the box; an infeasible preset is `null`; otherwise the largest box of the ratio, centred
 * on the current box's centre and shifted inside.
 */
export function applyPreset(box: CropBox, preset: AspectPresetId, image: CropImage, swapped: boolean): CropBox | null {
  const r = presetRatio(preset, image, swapped)
  if (r === null) {
    return box
  }
  if (!ratioFeasible(r, image.width, image.height)) {
    return null
  }
  const size = ratioLargestBox(r, image.width, image.height)
  const centreX = box.x + box.width / 2
  const centreY = box.y + box.height / 2
  return {
    x: clamp(roundHalfUp(centreX - size.width / 2), 0, image.width - size.width),
    y: clamp(roundHalfUp(centreY - size.height / 2), 0, image.height - size.height),
    width: size.width,
    height: size.height,
  }
}

/**
 * CROP_SWAP: the box after the swap. Under Free, width and height trade about the centre, then clamp; Square is
 * unchanged; another preset is refitted with the flipped ratio, and is `null` when that isn't feasible.
 */
export function swapCrop(box: CropBox, preset: AspectPresetId, image: CropImage, swapped: boolean): CropBox | null {
  if (preset === 'free') {
    const centreX = box.x + box.width / 2
    const centreY = box.y + box.height / 2
    return clampCrop(
      { x: centreX - box.height / 2, y: centreY - box.width / 2, width: box.height, height: box.width },
      image.width,
      image.height,
    )
  }
  if (!presetFeasible(preset, image, !swapped)) {
    return null
  }
  if (preset === 'square') {
    return box
  }
  return applyPreset(box, preset, image, !swapped)
}

const DECIMAL = /^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$/

/**
 * CROP_FIELDS: the box with one field typed. Empty, non-numeric or infinite text is `null`. X or Y keeps the size;
 * W or H keeps the origin, is cut to the image and raised to the minimum; with a ratio the box is a `ratioBox`.
 */
export function applyField(
  box: CropBox,
  field: CropField,
  text: string,
  image: CropImage,
  ratio: number | null,
): CropBox | null {
  const trimmed = text.trim()
  if (!DECIMAL.test(trimmed)) {
    return null
  }
  const parsed = Number(trimmed)
  if (!Number.isFinite(parsed)) {
    return null
  }
  const value = Math.max(0, roundHalfUp(parsed))
  const W = image.width
  const H = image.height
  if (field === 'x' || field === 'y') {
    return clampCrop({ ...box, [field]: value }, W, H)
  }
  if (ratio === null) {
    const next =
      field === 'width'
        ? { ...box, width: Math.max(CROP_MIN_PX, Math.min(value, W - box.x)) }
        : { ...box, height: Math.max(CROP_MIN_PX, Math.min(value, H - box.y)) }
    return clampCrop(next, W, H)
  }
  const s0 = field === 'width' ? drivingFromWidth(value, ratio) : drivingFromHeight(value, ratio)
  const sMax = largestDriving(ratio, W - box.x, H - box.y)
  const size = ratioBox(sMax >= CROP_MIN_PX ? clamp(s0, CROP_MIN_PX, sMax) : CROP_MIN_PX, ratio)
  return clampCrop({ x: box.x, y: box.y, width: size.width, height: size.height }, W, H)
}
