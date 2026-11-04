import type { Annotation } from './capture-annotate'

/** PIXELATE_BLOCK (Session 39, MEU-90): the pixelate mark's block edge in pixels; parity with the API. */
export const PIXELATE_BLOCK_MIN = 2
export const PIXELATE_BLOCK_MAX = 100
export const PIXELATE_BLOCK_DEFAULT = 10

/** A mark that changes the pixels under its rectangle (REGION_PASS step 1) instead of painting over them. */
export type RegionMark = Extract<Annotation, { type: 'pixelate' | 'eraser' }>

/** A clipped rectangle, half-open: `[x0, x1) x [y0, y1)`. */
export type RegionBox = { x0: number; y0: number; x1: number; y1: number }

export function isRegionMark(mark: Annotation): mark is RegionMark {
  return mark.type === 'pixelate' || mark.type === 'eraser'
}

/** REGION_RECT: `[x, x + width) x [y, y + height)` within the image, or null when nothing is left (or a drawn mark). */
export function regionClip(mark: Annotation, width: number, height: number): RegionBox | null {
  if (!isRegionMark(mark)) {
    return null
  }
  const x0 = Math.max(0, mark.x)
  const y0 = Math.max(0, mark.y)
  const x1 = Math.min(width, mark.x + mark.width)
  const y1 = Math.min(height, mark.y + mark.height)
  return x0 >= x1 || y0 >= y1 ? null : { x0, y0, x1, y1 }
}

/** PIXELATE_QUANT: Pillow's integer box reduce for `n` pixels summing to `sum`, in doubles (no 32-bit `>>`). */
function quantize(sum: number, n: number): number {
  return Math.floor(((sum + Math.floor(n / 2)) * Math.floor(16777216 / n)) / 16777216)
}

/** Blocks anchored at the clipped top-left; a partial right or bottom block averages only its own pixels. */
function pixelate(rgba: Uint8ClampedArray, width: number, box: RegionBox, block: number): void {
  const sums = [0, 0, 0, 0]
  for (let by = box.y0; by < box.y1; by += block) {
    const ey = Math.min(by + block, box.y1)
    for (let bx = box.x0; bx < box.x1; bx += block) {
      const ex = Math.min(bx + block, box.x1)
      const n = (ex - bx) * (ey - by)
      sums.fill(0)
      for (let y = by; y < ey; y += 1) {
        for (let x = bx; x < ex; x += 1) {
          const i = (y * width + x) * 4
          for (let band = 0; band < 4; band += 1) {
            sums[band] = (sums[band] as number) + (rgba[i + band] as number)
          }
        }
      }
      const value = sums.map((sum) => quantize(sum, n))
      for (let y = by; y < ey; y += 1) {
        for (let x = bx; x < ex; x += 1) {
          const i = (y * width + x) * 4
          for (let band = 0; band < 4; band += 1) {
            rgba[i + band] = value[band] as number
          }
        }
      }
    }
  }
}

/**
 * ERASER_SAMPLE: the most frequent RGB in the ring 1 px outside `box` (corners included, clipped to the image), or
 * in the box's own edge pixels when that ring is empty. A tie goes to the smallest `(r << 16) | (g << 8) | b`.
 */
export function eraserFill(rgba: Uint8ClampedArray, width: number, height: number, box: RegionBox): [number, number, number] {
  const counts = new Map<number, number>()
  const add = (x: number, y: number): void => {
    if (x < 0 || x >= width || y < 0 || y >= height) {
      return
    }
    const i = (y * width + x) * 4
    const packed = ((rgba[i] as number) << 16) | ((rgba[i + 1] as number) << 8) | (rgba[i + 2] as number)
    counts.set(packed, (counts.get(packed) ?? 0) + 1)
  }
  for (let x = box.x0 - 1; x <= box.x1; x += 1) {
    add(x, box.y0 - 1)
    add(x, box.y1)
  }
  for (let y = box.y0; y < box.y1; y += 1) {
    add(box.x0 - 1, y)
    add(box.x1, y)
  }
  if (counts.size === 0) {
    for (let y = box.y0; y < box.y1; y += 1) {
      for (let x = box.x0; x < box.x1; x += 1) {
        if (x === box.x0 || x === box.x1 - 1 || y === box.y0 || y === box.y1 - 1) {
          add(x, y)
        }
      }
    }
  }
  let best = 0
  let bestCount = 0
  for (const [packed, count] of counts) {
    if (count > bestCount || (count === bestCount && packed < best)) {
      best = packed
      bestCount = count
    }
  }
  return [(best >> 16) & 255, (best >> 8) & 255, best & 255]
}

/** The eraser fill: the clipped rectangle becomes one opaque colour. */
function erase(rgba: Uint8ClampedArray, width: number, box: RegionBox, fill: [number, number, number]): void {
  for (let y = box.y0; y < box.y1; y += 1) {
    for (let x = box.x0; x < box.x1; x += 1) {
      const i = (y * width + x) * 4
      rgba[i] = fill[0]
      rgba[i + 1] = fill[1]
      rgba[i + 2] = fill[2]
      rgba[i + 3] = 255
    }
  }
}

/**
 * REGION_PASS step 1 over RGBA pixels, in place: every region mark in list order, so an eraser samples the canvas
 * as the earlier region marks left it; drawn marks are skipped.
 */
export function applyRegionPass(rgba: Uint8ClampedArray, width: number, height: number, marks: readonly Annotation[]): void {
  for (const mark of marks) {
    if (!isRegionMark(mark)) {
      continue
    }
    const box = regionClip(mark, width, height)
    if (box === null) {
      continue
    }
    if (mark.type === 'pixelate') {
      pixelate(rgba, width, box, mark.block_size)
    } else {
      erase(rgba, width, box, eraserFill(rgba, width, height, box))
    }
  }
}
