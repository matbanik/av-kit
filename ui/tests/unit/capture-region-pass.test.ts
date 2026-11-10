/** @vitest-environment node */
/** MEU-90 FIC: AC-90.7 from the approved Session 39 plan (2026-10-16-capture-new-marks). */
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

import type { Annotation } from '../../src/renderer/src/features/capture/capture-annotate'
import {
  applyRegionPass,
  eraserFill,
  isRegionMark,
  PIXELATE_BLOCK_DEFAULT,
  PIXELATE_BLOCK_MAX,
  PIXELATE_BLOCK_MIN,
  regionClip,
  type RegionBox,
} from '../../src/renderer/src/features/capture/capture-region-pass'

const fixturePath = resolve(dirname(fileURLToPath(import.meta.url)), '../e2e/fixtures/capture-region-pass.json')

/** One REGION_FIXTURE case: RGB `pixels` in, the real bake's RGB `expected` out (row-major). */
type RegionCase = {
  name: string
  width: number
  height: number
  pixels: number[]
  marks: Annotation[]
  expected: number[]
}

/** The pixelate rows of REGION_CASES, by name, so cases added for later marks stay out of this AC. */
const PIXELATE_CASES = [
  'pixelate-interior',
  'pixelate-clipped',
  'pixelate-negative-origin',
  'pixelate-big-block',
  'pixelate-empty',
  'pixelate-repeat-overlap',
  // MEU-130 (Session 59, D-493): crops of a pixelate mark, clipped by CROP_PIXELS.
  'crop-pixelate-sliver',
  'crop-pixelate-corner',
]

const DRAWN: Annotation[] = [
  { type: 'rect', x: 1, y: 1, width: 6, height: 5, color: '#12AB34', stroke_width: 2 },
  { type: 'arrow', color: '#FF0000', stroke_width: 3, from: [0, 0], to: [9, 7] },
  { type: 'highlight', x: 2, y: 2, width: 5, height: 4, color: '#FFFF00', opacity: 0.4 },
  { type: 'text', x: 3, y: 3, text: 'Hi', color: '#000000', font_size: 12 },
]

function loadCases(): RegionCase[] {
  return (JSON.parse(readFileSync(fixturePath, 'utf8')) as { cases: RegionCase[] }).cases
}

/** RGB → opaque RGBA, the layout `applyRegionPass` works on (canvas `ImageData`). */
function rgba(pixels: number[]): Uint8ClampedArray {
  const out = new Uint8ClampedArray((pixels.length / 3) * 4)
  for (let i = 0, j = 0; i < pixels.length; i += 3, j += 4) {
    out[j] = pixels[i] as number
    out[j + 1] = pixels[i + 1] as number
    out[j + 2] = pixels[i + 2] as number
    out[j + 3] = 255
  }
  return out
}

/** The first RGB mismatch as `name@(x,y) band b: got vs want`, or null when every channel is equal. */
function firstDiff(name: string, width: number, got: Uint8ClampedArray, want: number[]): string | null {
  if (got.length / 4 !== want.length / 3) {
    return `${name}: ${got.length / 4} px vs ${want.length / 3} px`
  }
  for (let p = 0; p < want.length / 3; p += 1) {
    for (let band = 0; band < 3; band += 1) {
      const g = got[p * 4 + band]
      const w = want[p * 3 + band]
      if (g !== w) {
        return `${name}@(${p % width},${Math.floor(p / width)}) band ${band}: ${g} vs ${w}`
      }
    }
  }
  return null
}

function opaque(canvas: Uint8ClampedArray): boolean {
  for (let i = 3; i < canvas.length; i += 4) {
    if (canvas[i] !== 255) {
      return false
    }
  }
  return true
}

const pixelate = (x: number, y: number, width: number, height: number, block_size = 4): Annotation => ({
  type: 'pixelate',
  x,
  y,
  width,
  height,
  block_size,
})

describe('MEU-90 renderer region pass', () => {
  it('AC-90.7 applyRegionPass equals the bake on every channel for every pixelate REGION_CASE', () => {
    expect([PIXELATE_BLOCK_MIN, PIXELATE_BLOCK_MAX, PIXELATE_BLOCK_DEFAULT]).toEqual([2, 100, 10])
    const cases = loadCases().filter((c) => PIXELATE_CASES.includes(c.name))
    expect(cases.map((c) => c.name)).toEqual(PIXELATE_CASES)
    for (const c of cases) {
      const canvas = rgba(c.pixels)
      applyRegionPass(canvas, c.width, c.height, c.marks)
      expect(firstDiff(c.name, c.width, canvas, c.expected)).toBeNull()
      expect(opaque(canvas), `${c.name} alpha`).toBe(true)
    }
    // Self-check: the comparator sees a change of 1 at one pixel.
    const first = cases[0] as RegionCase
    const nudged = [...first.expected]
    nudged[0] = ((nudged[0] as number) + 1) % 256
    const canvas = rgba(first.pixels)
    applyRegionPass(canvas, first.width, first.height, first.marks)
    expect(firstDiff(first.name, first.width, canvas, nudged)).not.toBeNull()
  })

  it('AC-90.7 regionClip follows REGION_RECT for the clipped, negative-origin and empty cases', () => {
    expect(regionClip(pixelate(2, 1, 11, 8), 16, 12)).toEqual({ x0: 2, y0: 1, x1: 13, y1: 9 })
    expect(regionClip(pixelate(9, 6, 12, 10), 16, 12)).toEqual({ x0: 9, y0: 6, x1: 16, y1: 12 })
    expect(regionClip(pixelate(-3, 2, 9, 7), 16, 12)).toEqual({ x0: 0, y0: 2, x1: 6, y1: 9 })
    expect(regionClip(pixelate(5, 5, 0, 6), 16, 12)).toBeNull()
    expect(regionClip(pixelate(5, 5, 6, 0), 16, 12)).toBeNull()
    expect(regionClip(pixelate(20, 2, 4, 4), 16, 12)).toBeNull()
    expect(regionClip(pixelate(-9, 2, 4, 4), 16, 12)).toBeNull()
  })

  it('AC-90.7 drawn marks in the list are ignored: only region marks change pixels', () => {
    const interior = loadCases().find((c) => c.name === 'pixelate-interior') as RegionCase
    expect(interior).toBeDefined()
    expect(DRAWN.map((mark) => isRegionMark(mark))).toEqual([false, false, false, false])
    expect(interior.marks.map((mark) => isRegionMark(mark))).toEqual([true])
    const mixed: Annotation[] = [DRAWN[0] as Annotation, ...interior.marks, ...DRAWN.slice(1)]
    const canvas = rgba(interior.pixels)
    applyRegionPass(canvas, interior.width, interior.height, mixed)
    expect(firstDiff(interior.name, interior.width, canvas, interior.expected)).toBeNull()
    // Negative: a list of drawn marks only leaves every pixel as it was.
    const untouched = rgba(interior.pixels)
    applyRegionPass(untouched, interior.width, interior.height, DRAWN)
    expect(firstDiff(interior.name, interior.width, untouched, interior.pixels)).toBeNull()
  })

  // MEU-130 (Session 59, D-493): the crop cases are the crop's own pixels and the marks clip_mark returns.
  it('AC-130.29 the region fixture holds the four crop cases', () => {
    const crop = ['crop-pixelate-sliver', 'crop-pixelate-corner', 'crop-eraser-edge', 'crop-eraser-ring']
    expect(crop.filter((name) => PIXELATE_CASES.includes(name) || ERASER_CASES.includes(name))).toEqual(crop)
    const cases = loadCases().filter((c) => c.name.startsWith('crop-'))
    expect(cases.map((c) => c.name)).toEqual(crop)
    for (const c of cases) {
      expect(c.marks.length, c.name).toBeGreaterThan(0)
      expect(c.marks.map((mark) => isRegionMark(mark)), c.name).toEqual(c.marks.map(() => true))
      expect(c.expected, `${c.name} changes pixels`).not.toEqual(c.pixels)
      const canvas = rgba(c.pixels)
      applyRegionPass(canvas, c.width, c.height, c.marks)
      expect(firstDiff(c.name, c.width, canvas, c.expected)).toBeNull()
      expect(opaque(canvas), `${c.name} alpha`).toBe(true)
    }
  })
})

/** The eraser rows of REGION_CASES in fixture order; `pixelate-then-eraser` is a composed pass (R-1 `composed`). */
// MEU-130 (Session 59, D-493): + the crop eraser cases, after the composed pass.
const ERASER_CASES = [
  'eraser-stems',
  'eraser-tie',
  'eraser-clipped',
  'eraser-cover',
  'pixelate-then-eraser',
  'crop-eraser-edge',
  'crop-eraser-ring',
]

describe('MEU-91 renderer eraser', () => {
  it('AC-91.7 applyRegionPass equals the bake on every channel for every eraser REGION_CASE', () => {
    expect(typeof eraserFill).toBe('function')
    const cases = loadCases().filter((c) => ERASER_CASES.includes(c.name))
    expect(cases.map((c) => c.name)).toEqual(ERASER_CASES)
    for (const c of cases) {
      expect(c.marks.map((mark) => isRegionMark(mark)), c.name).toEqual(c.marks.map(() => true))
      const canvas = rgba(c.pixels)
      applyRegionPass(canvas, c.width, c.height, c.marks)
      expect(firstDiff(c.name, c.width, canvas, c.expected)).toBeNull()
      expect(opaque(canvas), `${c.name} alpha`).toBe(true)
    }
    // Self-check: the comparator sees a change of 1 at one eraser pixel.
    const stems = cases[0] as RegionCase
    const box = regionClip(stems.marks[0] as Annotation, stems.width, stems.height) as RegionBox
    const at = (box.y0 * stems.width + box.x0) * 3
    const nudged = [...stems.expected]
    nudged[at] = ((nudged[at] as number) + 1) % 256
    const canvas = rgba(stems.pixels)
    applyRegionPass(canvas, stems.width, stems.height, stems.marks)
    expect(firstDiff(stems.name, stems.width, canvas, nudged)).not.toBeNull()
  })

  it('AC-91.7 eraserFill takes the ring mode, breaks a tie on the smaller packed value and falls back to the inner ring', () => {
    expect(typeof eraserFill).toBe('function')
    const fill = (name: string): number[] => {
      const c = loadCases().find((item) => item.name === name) as RegionCase
      expect(c, name).toBeDefined()
      const box = regionClip(c.marks[c.marks.length - 1] as Annotation, c.width, c.height) as RegionBox
      return [...eraserFill(rgba(c.pixels), c.width, c.height, box)]
    }
    expect(fill('eraser-stems')).toEqual([240, 240, 240])
    expect(fill('eraser-tie')).toEqual([0, 0, 0])
    expect(fill('eraser-cover')).toEqual([1, 2, 3])
  })
})
