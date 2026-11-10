/** MEU-131 crop geometry: AC-131.1 to AC-131.10 (plan 2026-11-10-gui-capture-crop-tool, D-511 to D-514). */
import { describe, expect, it } from 'vitest'

import {
  applyField,
  applyPreset,
  ASPECT_PRESETS,
  clampCrop,
  cropEligible,
  drawCrop,
  fitsRatio,
  moveCrop,
  nudgeCrop,
  presetFeasible,
  presetRatio,
  ratioBox,
  ratioFeasible,
  ratioLargestBox,
  ratioMinBox,
  resizeCrop,
  roundHalfUp,
  swapCrop,
  wholeImage,
  type AspectPresetId,
  type CropBox,
  type CropField,
  type CropImage,
} from '../../src/renderer/src/features/capture/capture-crop'
import type { HandleId } from '../../src/renderer/src/features/capture/capture-transform'

const IMAGE: CropImage = { width: 400, height: 200 }
const HANDLES: HandleId[] = ['nw', 'n', 'ne', 'e', 'se', 's', 'sw', 'w']
const PRESET_IDS: AspectPresetId[] = ['original', 'square', '16:9', '4:3', '3:2']
const SWEEP_SHOTS: Array<[number, number]> = [
  [8, 8],
  [9, 17],
  [17, 9],
  [400, 200],
  [400, 10],
  [600, 1000],
  [1201, 799],
  [380, 608],
  [3840, 8],
]

/** `resolve_region`'s px rules (`capture.py:159-194`), restated: the endpoint accepts the box unclamped. */
function endpointAccepts(box: CropBox | null, W: number, H: number): boolean {
  if (box === null) {
    return false
  }
  const { x, y, width, height } = box
  if (![x, y, width, height].every((v) => Number.isInteger(v))) {
    return false
  }
  if (x < 0 || y < 0 || width <= 0 || height <= 0) {
    return false
  }
  if (x >= W || y >= H) {
    return false
  }
  const right = Math.min(x + width, W)
  const bottom = Math.min(y + height, H)
  const clamped = x + width > W || y + height > H
  return !clamped && right - x >= 8 && bottom - y >= 8
}

type SweepBox = { label: string; box: CropBox | null; ratio: number | null; W: number; H: number }

/** Every box the sweep asks of the module on one shot (AC-131.2), with the ratio it was asked under. */
function sweepShot(W: number, H: number): SweepBox[] {
  const image = { width: W, height: H }
  const out: SweepBox[] = []
  const add = (label: string, box: CropBox | null, ratio: number | null): void => {
    out.push({ label: `${W}x${H} ${label}`, box, ratio, W, H })
  }
  const whole = wholeImage(image)
  add('clamp whole', clampCrop(whole, W, H), null)
  add('clamp off', clampCrop({ x: -50, y: -50, width: W * 3, height: 2 }, W, H), null)
  add('clamp corner', clampCrop({ x: W - 1, y: H - 1, width: 3, height: 3 }, W, H), null)
  const middle = clampCrop({ x: W / 4, y: H / 4, width: W / 2, height: H / 2 }, W, H)
  const drags: Array<[number, number]> = [
    [-10000, -10000],
    [10000, 10000],
    [10000, -10000],
    [-3, 7],
    [25, -40],
    [0, 0],
  ]
  const ratios: Array<{ name: string; ratio: number | null; start: CropBox }> = [{ name: 'free', ratio: null, start: middle }]
  for (const preset of PRESET_IDS) {
    for (const swapped of [false, true]) {
      if (!presetFeasible(preset, image, swapped)) {
        continue
      }
      const start = applyPreset(whole, preset, image, swapped)
      const ratio = presetRatio(preset, image, swapped)
      if (start !== null) {
        ratios.push({ name: `${preset}${swapped ? ' swapped' : ''}`, ratio, start })
      }
      add(`preset ${preset} swapped=${swapped}`, start, ratio)
      if (start !== null) {
        const flipped = swapCrop(start, preset, image, swapped)
        if (presetFeasible(preset, image, !swapped)) {
          add(`swap ${preset} swapped=${swapped}`, flipped, preset === 'square' ? 1 : presetRatio(preset, image, !swapped))
        }
      }
    }
  }
  add('swap free', swapCrop(middle, 'free', image, false), null)
  for (const { name, ratio, start } of ratios) {
    for (const handle of HANDLES) {
      for (const [dx, dy] of drags) {
        add(`resize ${name} ${handle} ${dx},${dy}`, resizeCrop(start, handle, dx, dy, image, ratio), ratio)
      }
    }
    const anchors = [
      { x: 0, y: 0 },
      { x: W, y: H },
      { x: W / 2, y: H / 2 },
      { x: W - 1, y: 1 },
    ]
    for (const anchor of anchors) {
      for (const point of [
        { x: 0, y: H },
        { x: W, y: 0 },
        { x: anchor.x + 3, y: anchor.y + 2 },
        { x: anchor.x - 2, y: anchor.y - 3 },
      ]) {
        const drawn = drawCrop(anchor, point, image, ratio)
        if (drawn !== null) {
          add(`draw ${name} ${anchor.x},${anchor.y}->${point.x},${point.y}`, drawn, ratio)
        }
      }
    }
    const fields: CropField[] = ['x', 'y', 'width', 'height']
    for (const field of fields) {
      for (const text of ['0', '3', '150', '99999', '-5', '2.5']) {
        add(`field ${name} ${field} ${text}`, applyField(start, field, text, image, ratio), ratio)
      }
    }
  }
  for (const [dx, dy] of drags) {
    add(`move ${dx},${dy}`, moveCrop(middle, dx, dy, image), null)
  }
  return out
}

describe('MEU-131 crop geometry (capture-crop.ts)', () => {
  it('AC-131.1 roundHalfUp rounds a half up each way', () => {
    expect([2.5, 3.5, -2.5, -3.5, 2.4999, 2.5001].map(roundHalfUp)).toEqual([3, 4, -2, -3, 2, 3])
    const box = clampCrop({ x: 10.4, y: 20.6, width: 100.5, height: 50.49 }, 400, 200)
    expect(box).toEqual({ x: 10, y: 21, width: 101, height: 50 })
    for (const value of Object.values(box)) {
      expect(Number.isInteger(value), `${value} is whole`).toBe(true)
    }
  })

  it('AC-131.2 the box clamps inside the image and to the minimum', () => {
    expect(cropEligible(5, 300)).toBe(false)
    expect(cropEligible(300, 5)).toBe(false)
    expect(cropEligible(7, 7)).toBe(false)
    expect(cropEligible(8, 8)).toBe(true)
    expect(clampCrop({ x: -20, y: 10, width: 100, height: 50 }, 400, 200)).toEqual({ x: 0, y: 10, width: 100, height: 50 })
    expect(clampCrop({ x: 350, y: 10, width: 100, height: 50 }, 400, 200)).toEqual({ x: 300, y: 10, width: 100, height: 50 })
    expect(clampCrop({ x: 10, y: -5, width: 100, height: 50 }, 400, 200)).toEqual({ x: 10, y: 0, width: 100, height: 50 })
    expect(clampCrop({ x: 10, y: 180, width: 100, height: 50 }, 400, 200)).toEqual({ x: 10, y: 150, width: 100, height: 50 })
    expect(clampCrop({ x: 399, y: 199, width: 3, height: 3 }, 400, 200)).toEqual({ x: 392, y: 192, width: 8, height: 8 })
    let checked = 0
    for (const [W, H] of SWEEP_SHOTS) {
      for (const item of sweepShot(W, H)) {
        expect(endpointAccepts(item.box, item.W, item.H), `${item.label}: ${JSON.stringify(item.box)}`).toBe(true)
        checked += 1
      }
    }
    expect(checked).toBeGreaterThan(1000)
  })

  it('AC-131.3 a handle moves only its edges and never flips', () => {
    const start = { x: 50, y: 40, width: 100, height: 80 }
    for (const handle of HANDLES) {
      const want = { ...start }
      if (handle.includes('w')) {
        want.x += 10
        want.width -= 10
      }
      if (handle.includes('e')) {
        want.width += 10
      }
      if (handle.includes('n')) {
        want.y += 6
        want.height -= 6
      }
      if (handle.includes('s')) {
        want.height += 6
      }
      expect(resizeCrop(start, handle, 10, 6, IMAGE, null), handle).toEqual(want)
    }
    expect(resizeCrop(start, 'e', -200, 0, IMAGE, null)).toEqual({ x: 50, y: 40, width: 8, height: 80 })
    expect(resizeCrop(start, 'nw', -1000, -1000, IMAGE, null)).toEqual({ x: 0, y: 0, width: 150, height: 120 })
    expect(resizeCrop(start, 'w', 1000, 0, IMAGE, null)).toEqual({ x: 142, y: 40, width: 8, height: 80 })
    for (const handle of HANDLES) {
      for (const [dx, dy] of [
        [1000, 1000],
        [-1000, -1000],
        [1000, -1000],
        [-1000, 1000],
      ]) {
        const box = resizeCrop(start, handle, dx, dy, IMAGE, null)
        const label = `${handle} ${dx},${dy}`
        expect(box.width, label).toBeGreaterThanOrEqual(8)
        expect(box.height, label).toBeGreaterThanOrEqual(8)
        if (!handle.includes('w')) {
          expect(box.x, `${label} west edge stays`).toBe(start.x)
        }
        if (!handle.includes('e')) {
          expect(box.x + box.width, `${label} east edge stays`).toBe(start.x + start.width)
        }
        if (!handle.includes('n')) {
          expect(box.y, `${label} north edge stays`).toBe(start.y)
        }
        if (!handle.includes('s')) {
          expect(box.y + box.height, `${label} south edge stays`).toBe(start.y + start.height)
        }
        expect(endpointAccepts(box, 400, 200), label).toBe(true)
      }
    }
  })

  it('AC-131.4 a move keeps the size inside the image', () => {
    const start = { x: 50, y: 40, width: 100, height: 80 }
    expect(moveCrop(start, 30, -20, IMAGE)).toEqual({ x: 80, y: 20, width: 100, height: 80 })
    expect(moveCrop(start, -1000, 0, IMAGE)).toEqual({ x: 0, y: 40, width: 100, height: 80 })
    expect(moveCrop(start, 1000, 0, IMAGE)).toEqual({ x: 300, y: 40, width: 100, height: 80 })
    expect(moveCrop(start, 0, -1000, IMAGE)).toEqual({ x: 50, y: 0, width: 100, height: 80 })
    expect(moveCrop(start, 0, 1000, IMAGE)).toEqual({ x: 50, y: 120, width: 100, height: 80 })
  })

  it('AC-131.5 a drawn box normalises and a click keeps the old box', () => {
    const want = { x: 100, y: 50, width: 100, height: 70 }
    expect(drawCrop({ x: 100, y: 50 }, { x: 200, y: 120 }, IMAGE, null), 'right-down').toEqual(want)
    expect(drawCrop({ x: 200, y: 120 }, { x: 100, y: 50 }, IMAGE, null), 'left-up').toEqual(want)
    expect(drawCrop({ x: 100, y: 120 }, { x: 200, y: 50 }, IMAGE, null), 'right-up').toEqual(want)
    expect(drawCrop({ x: 200, y: 50 }, { x: 100, y: 120 }, IMAGE, null), 'left-down').toEqual(want)
    expect(drawCrop({ x: 100, y: 50 }, { x: 103, y: 53 }, IMAGE, null), '3 px right-down').toEqual({ x: 100, y: 50, width: 8, height: 8 })
    expect(drawCrop({ x: 100, y: 50 }, { x: 97, y: 47 }, IMAGE, null), '3 px left-up').toEqual({ x: 92, y: 42, width: 8, height: 8 })
    expect(drawCrop({ x: 100, y: 50 }, { x: 100, y: 50 }, IMAGE, null), 'same point').toBeNull()
  })

  it('AC-131.6 a ratio and Shift hold through a drag', () => {
    const r169 = 16 / 9
    expect(fitsRatio({ width: 16, height: 9 }, r169), '16x9 fits 16:9').toBe(true)
    expect(fitsRatio({ width: 17, height: 9 }, r169), '17x9 does not fit 16:9').toBe(false)
    expect(ratioBox(9, r169)).toEqual({ width: 16, height: 9 })
    const start = { x: 50, y: 40, width: 160, height: 90 }
    expect(fitsRatio(start, r169), 'start box').toBe(true)
    const right = resizeCrop(start, 'se', 42, 5, IMAGE, r169)
    expect(right, 'se mostly right').toEqual({ x: 50, y: 40, width: 203, height: 114 })
    const down = resizeCrop(start, 'se', 5, 30, IMAGE, r169)
    expect(down, 'se mostly down').toEqual({ x: 50, y: 40, width: 213, height: 120 })
    const east = resizeCrop(start, 'e', 36, 0, IMAGE, r169)
    expect(east, 'e drag, centred').toEqual({ x: 50, y: 30, width: 196, height: 110 })
    expect(Math.abs(east.y + east.height / 2 - (start.y + start.height / 2))).toBeLessThanOrEqual(0.5)
    const north = resizeCrop(start, 'n', 0, -20, IMAGE, r169)
    expect(north, 'n drag, centred').toEqual({ x: 32, y: 20, width: 196, height: 110 })
    expect(Math.abs(north.x + north.width / 2 - (start.x + start.width / 2))).toBeLessThanOrEqual(0.5)
    for (const box of [right, down, east, north]) {
      expect(fitsRatio(box, r169), JSON.stringify(box)).toBe(true)
      expect(endpointAccepts(box, 400, 200), JSON.stringify(box)).toBe(true)
    }
    const free = { x: 50, y: 40, width: 120, height: 60 }
    const shift = resizeCrop(free, 'se', 30, 2, IMAGE, free.width / free.height)
    expect(shift, 'Shift keeps the start ratio').toEqual({ x: 50, y: 40, width: 150, height: 75 })
    expect(fitsRatio(shift, 2)).toBe(true)
    const edge = resizeCrop(start, 'se', 1000, 1000, IMAGE, r169)
    expect(edge, 'stops at the image edge').toEqual({ x: 50, y: 40, width: 284, height: 160 })
    expect(fitsRatio(edge, r169)).toBe(true)
    const thin = { width: 400, height: 10 }
    const thinStart = applyPreset(wholeImage(thin), '16:9', thin, false)
    expect(thinStart).toEqual({ x: 191, y: 0, width: 18, height: 10 })
    if (thinStart !== null) {
      const min = resizeCrop(thinStart, 'n', 0, 50, thin, r169)
      expect(min).toEqual({ x: 193, y: 2, width: 14, height: 8 })
      expect({ width: min.width, height: min.height }).toEqual(ratioMinBox(r169))
    }
    const tall = { width: 380, height: 608 }
    const swappedOriginal = presetRatio('original', tall, true)
    expect(swappedOriginal).toBeCloseTo(1.6, 9)
    const largest = ratioLargestBox(swappedOriginal ?? 0, 380, 608)
    expect(largest).toEqual({ width: 379, height: 237 })
    expect(fitsRatio(largest, swappedOriginal ?? 0)).toBe(true)
    let checked = 0
    for (const [W, H] of SWEEP_SHOTS) {
      for (const item of sweepShot(W, H)) {
        const kind = item.label.split(' ')[1]
        if (item.ratio === null || item.box === null || !['resize', 'draw', 'field'].includes(kind ?? '')) {
          continue
        }
        expect(fitsRatio(item.box, item.ratio), `${item.label}: ${JSON.stringify(item.box)}`).toBe(true)
        checked += 1
      }
    }
    expect(checked).toBeGreaterThan(500)
  })

  it('AC-131.7 the presets fit the largest box', () => {
    expect(ASPECT_PRESETS.map((preset) => preset.id)).toEqual(['free', 'original', 'square', '16:9', '4:3', '3:2'])
    expect(ASPECT_PRESETS.map((preset) => preset.label)).toEqual(['Free', 'Original', 'Square', '16:9', '4:3', '3:2'])
    expect(presetRatio('original', IMAGE, false)).toBe(2)
    expect(applyPreset(wholeImage(IMAGE), 'square', IMAGE, false)).toEqual({ x: 100, y: 0, width: 200, height: 200 })
    expect(applyPreset({ x: 380, y: 90, width: 16, height: 16 }, '16:9', IMAGE, false)).toEqual({ x: 44, y: 0, width: 356, height: 200 })
    const box = { x: 30, y: 20, width: 50, height: 70 }
    expect(applyPreset(box, 'free', IMAGE, false)).toEqual(box)
    const tiny = { width: 8, height: 8 }
    for (const preset of ['16:9', '4:3', '3:2'] as const) {
      for (const swapped of [false, true]) {
        expect(presetFeasible(preset, tiny, swapped), `8x8 ${preset} swapped=${swapped}`).toBe(false)
        expect(applyPreset(wholeImage(tiny), preset, tiny, swapped), `8x8 ${preset} swapped=${swapped}`).toBeNull()
      }
    }
    for (const preset of ['free', 'original', 'square'] as const) {
      expect(presetFeasible(preset, tiny, false), `8x8 ${preset}`).toBe(true)
    }
    const thin = { width: 400, height: 10 }
    expect(ratioMinBox(3 / 4)).toEqual({ width: 8, height: 11 })
    expect(ratioLargestBox(3 / 4, 400, 10)).toEqual({ width: 7, height: 9 })
    expect(presetFeasible('4:3', thin, true)).toBe(false)
    for (const [W, H] of SWEEP_SHOTS) {
      const image = { width: W, height: H }
      for (const preset of PRESET_IDS) {
        for (const swapped of [false, true]) {
          const label = `${W}x${H} ${preset} swapped=${swapped}`
          const r = presetRatio(preset, image, swapped)
          expect(r, label).not.toBeNull()
          if (r === null) {
            continue
          }
          const feasible = ratioFeasible(r, W, H)
          const min = ratioMinBox(r)
          const largest = ratioLargestBox(r, W, H)
          expect(feasible, `${label} min fits`).toBe(min.width <= W && min.height <= H)
          expect(feasible, `${label} largest at least 8`).toBe(largest.width >= 8 && largest.height >= 8)
          expect(presetFeasible(preset, image, swapped), label).toBe(feasible)
          expect(largest.width <= W && largest.height <= H, `${label} largest inside`).toBe(true)
          expect(fitsRatio(largest, r), `${label} largest fits`).toBe(true)
          if (feasible) {
            const applied = applyPreset(wholeImage(image), preset, image, swapped)
            expect(applied !== null && fitsRatio(applied, r), `${label} applied fits`).toBe(true)
            expect(applied !== null && applied.width >= 8 && applied.height >= 8, `${label} applied at least 8`).toBe(true)
          }
        }
      }
    }
  })

  it('AC-131.8 the swap flips the ratio', () => {
    expect(swapCrop({ x: 100, y: 80, width: 120, height: 40 }, 'free', IMAGE, false)).toEqual({ x: 140, y: 40, width: 40, height: 120 })
    const wide = applyPreset(wholeImage(IMAGE), '16:9', IMAGE, false)
    expect(wide).toEqual({ x: 22, y: 0, width: 356, height: 200 })
    if (wide !== null) {
      const flipped = swapCrop(wide, '16:9', IMAGE, false)
      expect(flipped).toEqual({ x: 144, y: 1, width: 112, height: 199 })
      expect(flipped !== null && fitsRatio(flipped, 9 / 16)).toBe(true)
    }
    const square = { x: 100, y: 0, width: 200, height: 200 }
    expect(swapCrop(square, 'square', IMAGE, false)).toEqual(square)
    const thin = { width: 400, height: 10 }
    expect(swapCrop({ x: 191, y: 0, width: 18, height: 10 }, '16:9', thin, false)).toBeNull()
    const strip = { width: 3840, height: 8 }
    expect(swapCrop(wholeImage(strip), 'original', strip, false)).toBeNull()
  })

  it('AC-131.9 a field applies or reverts', () => {
    const box = { x: 100, y: 50, width: 100, height: 60 }
    expect(applyField(box, 'x', '350', IMAGE, null)).toEqual({ ...box, x: 300 })
    expect(applyField(box, 'width', '500', IMAGE, null)).toEqual({ ...box, width: 300 })
    expect(applyField(box, 'width', '3', IMAGE, null)).toEqual({ ...box, width: 8 })
    expect(applyField(box, 'x', '2.5', IMAGE, null)).toEqual({ ...box, x: 3 })
    expect(applyField(box, 'x', '2.4', IMAGE, null)).toEqual({ ...box, x: 2 })
    expect(applyField(box, 'width', '2.5', IMAGE, null)).toEqual({ ...box, width: 8 })
    expect(applyField(box, 'x', '-5', IMAGE, null)).toEqual({ ...box, x: 0 })
    for (const text of ['', '   ', 'abc', 'NaN', '1e999']) {
      expect(applyField(box, 'width', text, IMAGE, null), JSON.stringify(text)).toBeNull()
    }
    const square = { x: 100, y: 0, width: 200, height: 200 }
    expect(applyField(square, 'width', '150', IMAGE, 1)).toEqual({ x: 100, y: 0, width: 150, height: 150 })
    expect(applyField({ x: 100, y: 50, width: 100, height: 100 }, 'width', '180', IMAGE, 1)).toEqual({
      x: 100,
      y: 50,
      width: 150,
      height: 150,
    })
  })

  it('AC-131.10 a nudge moves by whole pixels', () => {
    const box = { x: 100, y: 50, width: 100, height: 60 }
    expect(nudgeCrop(box, 1, 0, IMAGE)).toEqual({ ...box, x: 101 })
    expect(nudgeCrop(box, -1, 0, IMAGE)).toEqual({ ...box, x: 99 })
    expect(nudgeCrop(box, 10, 0, IMAGE)).toEqual({ ...box, x: 110 })
    expect(nudgeCrop(box, -10, 0, IMAGE)).toEqual({ ...box, x: 90 })
    expect(nudgeCrop(box, 0, 1, IMAGE)).toEqual({ ...box, y: 51 })
    expect(nudgeCrop(box, 0, -10, IMAGE)).toEqual({ ...box, y: 40 })
    const corner = { x: 300, y: 140, width: 100, height: 60 }
    expect(nudgeCrop(corner, 1, 0, IMAGE)).toEqual(corner)
    expect(nudgeCrop(corner, 0, 10, IMAGE)).toEqual(corner)
    const origin = { x: 0, y: 0, width: 100, height: 60 }
    expect(nudgeCrop(origin, -1, -10, IMAGE)).toEqual(origin)
  })
})
