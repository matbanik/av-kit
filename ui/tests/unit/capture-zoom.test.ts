/** MEU-66 FIC: AC-66.1, AC-66.4 and AC-66.6 from the approved Session 29 plan. */
import { describe, expect, it } from 'vitest'

import * as fitMap from '../../src/renderer/src/features/capture/capture-fit-map'
import * as zoom from '../../src/renderer/src/features/capture/capture-zoom'

/** Chromium kPresetBrowserZoomFactorsArray (third_party/blink/common/page/page_zoom.cc:13-15; plan D-14). */
const CHROMIUM_PRESETS = [0.25, 1 / 3, 0.5, 2 / 3, 0.75, 0.8, 0.9, 1, 1.1, 1.25, 1.5, 1.75, 2, 2.5, 3, 4, 5]
const FIT = { kind: 'fit' } as const
const CONTAINER = { w: 800, h: 600 }
const IMAGE = { w: 1600, h: 900 }

function imageUnder(state: zoom.ZoomState, cursor: { x: number; y: number }): { x: number; y: number } {
  const t = fitMap.viewTransform(CONTAINER, IMAGE, state)
  if (t === null) {
    throw new Error('viewTransform returned null')
  }
  return { x: (cursor.x - t.ox) / t.s, y: (cursor.y - t.oy) / t.s }
}

describe('MEU-66 zoom ladder and step (AC-66.1)', () => {
  it('AC-66.1 ZOOM_LADDER equals the Chromium presets, ascending, unique, and contains 1', () => {
    expect(typeof zoom.zoomStep).toBe('function')
    expect([...zoom.ZOOM_LADDER]).toEqual(CHROMIUM_PRESETS)
    for (let i = 1; i < zoom.ZOOM_LADDER.length; i += 1) {
      expect(zoom.ZOOM_LADDER[i]).toBeGreaterThan(zoom.ZOOM_LADDER[i - 1] as number)
    }
    expect(new Set(zoom.ZOOM_LADDER).size).toBe(zoom.ZOOM_LADDER.length)
    expect(zoom.ZOOM_LADDER).toContain(1)
  })

  it('AC-66.1 zoomStep steps the ladder from fit and from a scale, and returns null past the ends', () => {
    expect(typeof zoom.zoomStep).toBe('function')
    expect(zoom.zoomStep(FIT, 'in', 0.5)).toBe(2 / 3)
    expect(zoom.zoomStep(FIT, 'out', 0.5)).toBe(1 / 3)
    const at = (scale: number): zoom.ZoomState => ({ kind: 'scale', scale, ox: 0, oy: 0 })
    expect(zoom.zoomStep(at(1), 'in', 0.5)).toBe(1.1)
    expect(zoom.zoomStep(at(1), 'out', 0.5)).toBe(0.9)
    expect(zoom.zoomStep(at(5), 'in', 0.5)).toBeNull()
    expect(zoom.zoomStep(at(0.25), 'out', 0.5)).toBeNull()
    expect(zoom.zoomStep(FIT, 'in', 20)).toBeNull()
    expect(zoom.zoomStep(FIT, 'out', 0.1)).toBeNull()
  })

  it('AC-66.1 negative: a non-finite or non-positive fit scale fails closed', () => {
    expect(typeof zoom.zoomStep).toBe('function')
    expect(zoom.zoomStep(FIT, 'in', Number.NaN)).toBeNull()
    expect(zoom.zoomStep(FIT, 'in', 0)).toBeNull()
    expect(zoom.zoomStep(FIT, 'out', -1)).toBeNull()
    expect(zoom.zoomStep(FIT, 'in', Number.POSITIVE_INFINITY)).toBeNull()
  })
})

describe('MEU-66 zoom about the cursor (AC-66.4)', () => {
  it('AC-66.4 zoomAbout keeps the cursor image point on ZOOM_ABOUT_EXAMPLE', () => {
    expect(typeof zoom.zoomAbout).toBe('function')
    const next = zoom.zoomAbout(FIT, { x: 400, y: 300 }, 2 / 3, CONTAINER, IMAGE)
    expect(next.kind).toBe('scale')
    if (next.kind !== 'scale') {
      return
    }
    expect(next.scale).toBe(2 / 3)
    expect(next.ox).toBeCloseTo(400 - (800 * 2) / 3, 6)
    expect(next.oy).toBeCloseTo(0, 6)
    const under = imageUnder(next, { x: 400, y: 300 })
    expect(under.x).toBeCloseTo(800, 6)
    expect(under.y).toBeCloseTo(450, 6)
  })

  it('AC-66.4 the image point under the cursor moves at most 1 image px wherever no clamp applies', () => {
    expect(typeof zoom.zoomAbout).toBe('function')
    let checked = 0
    for (const cursor of [
      { x: 400, y: 300 },
      { x: 300, y: 250 },
      { x: 520, y: 340 },
    ]) {
      let state: zoom.ZoomState = { kind: 'scale', scale: 2, ox: -1000, oy: -450 }
      for (const dir of ['in', 'in', 'out', 'out', 'out'] as const) {
        const fitScale = 0.5
        const nextScale = zoom.zoomStep(state, dir, fitScale)
        if (nextScale === null) {
          continue
        }
        const before = imageUnder(state, cursor)
        const unclampedOx = cursor.x - before.x * nextScale
        const unclampedOy = cursor.y - before.y * nextScale
        const fitsX = IMAGE.w * nextScale <= CONTAINER.w
        const fitsY = IMAGE.h * nextScale <= CONTAINER.h
        const clampX = !fitsX && (unclampedOx > 0 || unclampedOx < CONTAINER.w - IMAGE.w * nextScale)
        const clampY = !fitsY && (unclampedOy > 0 || unclampedOy < CONTAINER.h - IMAGE.h * nextScale)
        const next = zoom.zoomAbout(state, cursor, nextScale, CONTAINER, IMAGE)
        if (!fitsX && !fitsY && !clampX && !clampY) {
          const after = imageUnder(next, cursor)
          expect(Math.abs(after.x - before.x)).toBeLessThanOrEqual(1)
          expect(Math.abs(after.y - before.y)).toBeLessThanOrEqual(1)
          checked += 1
        }
        state = next
      }
    }
    expect(checked).toBeGreaterThan(3)
  })

  it('AC-66.4 negative: at the image edge a zoom-out stays inside the clamp range and leaves no blank margin', () => {
    expect(typeof zoom.zoomAbout).toBe('function')
    const state: zoom.ZoomState = { kind: 'scale', scale: 2, ox: 0, oy: 0 }
    const next = zoom.zoomAbout(state, { x: 0, y: 0 }, 1.75, CONTAINER, IMAGE)
    expect(next.kind).toBe('scale')
    if (next.kind !== 'scale') {
      return
    }
    expect(next.ox).toBeLessThanOrEqual(0)
    expect(next.ox).toBeGreaterThanOrEqual(CONTAINER.w - IMAGE.w * 1.75)
    expect(next.oy).toBeLessThanOrEqual(0)
    expect(next.oy).toBeGreaterThanOrEqual(CONTAINER.h - IMAGE.h * 1.75)
    const far = zoom.zoomAbout({ kind: 'scale', scale: 2, ox: -2400, oy: -1200 }, { x: 800, y: 600 }, 1.1, CONTAINER, IMAGE)
    if (far.kind !== 'scale') {
      throw new Error('expected a scale state')
    }
    expect(far.ox).toBeGreaterThanOrEqual(CONTAINER.w - IMAGE.w * 1.1)
    expect(far.oy).toBeGreaterThanOrEqual(CONTAINER.h - IMAGE.h * 1.1)
  })
})

describe('MEU-66 wheel and key normalization (AC-66.6)', () => {
  const pixel = (deltaY: number, timeStamp: number) => ({ deltaMode: 0, deltaY, timeStamp })

  it('AC-66.6 line and page deltas give one step per event; up zooms in', () => {
    expect(typeof zoom.wheelSteps).toBe('function')
    expect(zoom.wheelSteps(zoom.WHEEL_IDLE, { deltaMode: 1, deltaY: -3, timeStamp: 0 }).steps).toBe(1)
    expect(zoom.wheelSteps(zoom.WHEEL_IDLE, { deltaMode: 1, deltaY: 3, timeStamp: 0 }).steps).toBe(-1)
    expect(zoom.wheelSteps(zoom.WHEEL_IDLE, { deltaMode: 2, deltaY: -1, timeStamp: 0 }).steps).toBe(1)
  })

  it('AC-66.6 pixel deltas accumulate to WHEEL_STEP_PX, reset on a sign change and after 250 ms idle', () => {
    expect(typeof zoom.wheelSteps).toBe('function')
    expect(zoom.WHEEL_STEP_PX).toBe(100)
    let acc = zoom.WHEEL_IDLE
    const steps: number[] = []
    for (const [i, delta] of [-40, -40, -40].entries()) {
      const out = zoom.wheelSteps(acc, pixel(delta, i * 10))
      steps.push(out.steps)
      acc = out.acc
    }
    expect(steps).toEqual([0, 0, 1])
    expect(zoom.wheelSteps(zoom.WHEEL_IDLE, pixel(-100, 0)).steps).toBe(1)
    let flip = zoom.wheelSteps(zoom.WHEEL_IDLE, pixel(-80, 0)).acc
    const reversed = zoom.wheelSteps(flip, pixel(40, 10))
    expect(reversed.steps).toBe(0)
    flip = reversed.acc
    expect(zoom.wheelSteps(flip, pixel(70, 20)).steps).toBe(-1)
    const idle = zoom.wheelSteps(zoom.WHEEL_IDLE, pixel(-80, 0)).acc
    expect(zoom.wheelSteps(idle, pixel(-40, 300)).steps).toBe(0)
    expect(zoom.wheelSteps(idle, pixel(-40, 100)).steps).toBe(1)
  })

  it('AC-66.6 negative: a zero, non-finite or unknown-mode delta gives no step', () => {
    expect(typeof zoom.wheelSteps).toBe('function')
    expect(zoom.wheelSteps(zoom.WHEEL_IDLE, pixel(0, 0)).steps).toBe(0)
    expect(zoom.wheelSteps(zoom.WHEEL_IDLE, { deltaMode: 1, deltaY: 0, timeStamp: 0 }).steps).toBe(0)
    expect(zoom.wheelSteps(zoom.WHEEL_IDLE, { deltaMode: 7, deltaY: -100, timeStamp: 0 }).steps).toBe(0)
    expect(zoom.wheelSteps(zoom.WHEEL_IDLE, pixel(Number.NaN, 0)).steps).toBe(0)
  })

  it('AC-66.6 zoomKeyAction maps the Ctrl/Meta key table and nothing else', () => {
    expect(typeof zoom.zoomKeyAction).toBe('function')
    const key = (k: string, code: string, mods: Partial<Record<'ctrlKey' | 'metaKey' | 'shiftKey' | 'altKey', boolean>> = {}) => ({
      key: k,
      code,
      ctrlKey: false,
      metaKey: false,
      shiftKey: false,
      altKey: false,
      ...mods,
    })
    expect(zoom.zoomKeyAction(key('=', 'Equal', { ctrlKey: true }))).toBe('in')
    expect(zoom.zoomKeyAction(key('+', 'Equal', { ctrlKey: true, shiftKey: true }))).toBe('in')
    expect(zoom.zoomKeyAction(key('+', 'NumpadAdd', { ctrlKey: true }))).toBe('in')
    expect(zoom.zoomKeyAction(key('-', 'Minus', { ctrlKey: true }))).toBe('out')
    expect(zoom.zoomKeyAction(key('-', 'NumpadSubtract', { ctrlKey: true }))).toBe('out')
    expect(zoom.zoomKeyAction(key('0', 'Digit0', { ctrlKey: true }))).toBe('fit')
    expect(zoom.zoomKeyAction(key('0', 'Numpad0', { ctrlKey: true }))).toBe('fit')
    expect(zoom.zoomKeyAction(key('=', 'Equal', { metaKey: true }))).toBe('in')
    expect(zoom.zoomKeyAction(key('=', 'Equal'))).toBeNull()
    expect(zoom.zoomKeyAction(key('-', 'Minus'))).toBeNull()
    expect(zoom.zoomKeyAction(key('0', 'Digit0'))).toBeNull()
    expect(zoom.zoomKeyAction(key('0', 'Digit0', { ctrlKey: true, shiftKey: true }))).toBeNull()
    expect(zoom.zoomKeyAction(key('=', 'Equal', { ctrlKey: true, altKey: true }))).toBeNull()
    expect(zoom.zoomKeyAction(key('a', 'KeyA', { ctrlKey: true }))).toBeNull()
  })
})
