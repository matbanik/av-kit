// MEU-167 (Session 103) viewport scroll bar geometry: AC-167.1 to AC-167.3 on the pure functions of
// capture-scroll-bars.ts (SCROLL_BAR_GEOMETRY). The module is loaded through import.meta.glob and
// every test asserts the loader first, so a Red run fails by assertion (red-check.py).

import { describe, expect, it } from 'vitest'

import { viewTransform, type ViewState } from '../../src/renderer/src/features/capture/capture-fit-map'

type Box = { w: number; h: number }
type Axis = { frame: number; content: number; track: number; thumb: number; offset: number; value: number }
type Geometry = { x: Axis | null; y: Axis | null }
type ScrollBarsModule = {
  SCROLL_BAR_THICKNESS: number
  SCROLL_THUMB_MIN: number
  scrollBars: (frame: Box, image: Box, state: ViewState) => Geometry
  thumbDragToPan: (drag: number, bar: Axis) => number
}

const loaders = import.meta.glob<ScrollBarsModule>('../../src/renderer/src/features/capture/capture-scroll-bars.ts')
const MODULE_PATH = '../../src/renderer/src/features/capture/capture-scroll-bars.ts'

async function load(): Promise<ScrollBarsModule> {
  const loader = loaders[MODULE_PATH]
  expect(loader, 'capture-scroll-bars.ts exists').toBeTypeOf('function')
  return (loader as () => Promise<ScrollBarsModule>)()
}

const at = (ox: number, oy: number, scale = 1): ViewState => ({ kind: 'scale', scale, ox, oy })

/** The horizontal bar for frame 400×400 and an image `w` wide (100 tall, so only x shows) at scale 1. */
function xBar(mod: ScrollBarsModule, w: number, ox: number): Axis {
  const bars = mod.scrollBars({ w: 400, h: 400 }, { w, h: 100 }, at(ox, 0))
  expect(bars.y).toBeNull()
  expect(bars.x).not.toBeNull()
  return bars.x as Axis
}

describe('MEU-167 scroll bar geometry (AC-167.1)', () => {
  it('AC-167.1 C 400, K 1600, T 400: a 100 px thumb at 0, at T - thumb and in the middle; value 0 to 100', async () => {
    const mod = await load()
    const start = xBar(mod, 1600, 0)
    expect(start).toMatchObject({ frame: 400, content: 1600, track: 400, thumb: 100, offset: 0, value: 0 })
    const end = xBar(mod, 1600, 400 - 1600)
    expect(end.offset).toBe(end.track - end.thumb)
    expect(end.value).toBe(100)
    const middle = xBar(mod, 1600, (400 - 1600) / 2)
    expect(middle.offset).toBe(150)
    expect(middle.value).toBe(50)
  })

  it('AC-167.1 a very long image gives the shortest thumb, SCROLL_THUMB_MIN', async () => {
    const mod = await load()
    expect(mod.SCROLL_THUMB_MIN).toBe(24)
    expect(mod.SCROLL_BAR_THICKNESS).toBe(10)
    expect(xBar(mod, 40000, 0).thumb).toBe(mod.SCROLL_THUMB_MIN)
  })

  it('AC-167.1 negative: the thumb is never longer than the track', async () => {
    const mod = await load()
    // C 20, K 30: the minimum (24) is longer than the track (20), so the track caps it.
    const short = mod.scrollBars({ w: 20, h: 20 }, { w: 30, h: 10 }, at(0, 0)).x
    expect(short).not.toBeNull()
    expect((short as Axis).thumb).toBe(20)
    for (const [frame, image, scale] of [
      [{ w: 400, h: 300 }, { w: 1600, h: 900 }, 1],
      [{ w: 30, h: 30 }, { w: 31, h: 900 }, 1],
      [{ w: 800, h: 600 }, { w: 1600, h: 900 }, 5],
      [{ w: 25, h: 25 }, { w: 100, h: 100 }, 0.3],
    ] as const) {
      const bars = mod.scrollBars(frame, image, at(0, 0, scale))
      for (const bar of [bars.x, bars.y]) {
        if (bar !== null) {
          expect(bar.thumb).toBeLessThanOrEqual(bar.track)
          expect(bar.thumb).toBeGreaterThan(0)
        }
      }
    }
  })
})

describe('MEU-167 which bars show (AC-167.2)', () => {
  const frame = { w: 400, h: 300 }

  it('AC-167.2 at Fit neither bar shows; in scale with the image inside the frame neither shows', async () => {
    const mod = await load()
    expect(mod.scrollBars(frame, { w: 1600, h: 900 }, { kind: 'fit' })).toEqual({ x: null, y: null })
    expect(mod.scrollBars(frame, { w: 200, h: 100 }, at(0, 0))).toEqual({ x: null, y: null })
  })

  it('AC-167.2 one larger axis shows only its bar on the full frame; two larger shorten each by the thickness', async () => {
    const mod = await load()
    const wide = mod.scrollBars(frame, { w: 1600, h: 300 }, at(0, 0))
    expect(wide.y).toBeNull()
    expect(wide.x?.track).toBe(400)
    const tall = mod.scrollBars(frame, { w: 300, h: 900 }, at(0, 0))
    expect(tall.x).toBeNull()
    expect(tall.y?.track).toBe(300)
    const both = mod.scrollBars(frame, { w: 1600, h: 900 }, at(0, 0))
    expect(both.x?.track).toBe(400 - mod.SCROLL_BAR_THICKNESS)
    expect(both.y?.track).toBe(300 - mod.SCROLL_BAR_THICKNESS)
  })

  it('AC-167.2 negative: equal lengths show no bar', async () => {
    const mod = await load()
    expect(mod.scrollBars(frame, { w: 400, h: 300 }, at(0, 0))).toEqual({ x: null, y: null })
    expect(mod.scrollBars(frame, { w: 200, h: 150 }, at(0, 0, 2))).toEqual({ x: null, y: null })
  })
})

describe('MEU-167 thumb drag to pan (AC-167.3)', () => {
  it('AC-167.3 a drag of d px pans by -d * (K - C) / (T - thumb); the whole free track reaches the end', async () => {
    const mod = await load()
    const bar = xBar(mod, 1600, 0)
    expect(mod.thumbDragToPan(30, bar)).toBeCloseTo((-30 * (1600 - 400)) / (400 - 100), 9)
    expect(mod.thumbDragToPan(-30, bar)).toBeCloseTo((30 * (1600 - 400)) / (400 - 100), 9)
    const whole = mod.thumbDragToPan(bar.track - bar.thumb, bar)
    expect(0 + whole).toBe(400 - 1600)
    const placed = viewTransform({ w: 400, h: 400 }, { w: 1600, h: 100 }, at(0 + whole, 0))
    expect(placed?.ox).toBe(400 - 1600)
    expect(xBar(mod, 1600, placed?.ox ?? 0).offset).toBe(bar.track - bar.thumb)
  })

  it('AC-167.3 after the pan clamp the offset stays within C - K to 0 over a table of cases', async () => {
    const mod = await load()
    const cases: Array<{ frame: Box; image: Box; scale: number; ox: number; oy: number; dx: number; dy: number }> = [
      { frame: { w: 800, h: 600 }, image: { w: 1600, h: 900 }, scale: 2, ox: -1200, oy: -600, dx: 30, dy: -30 },
      { frame: { w: 800, h: 600 }, image: { w: 1600, h: 900 }, scale: 2, ox: 0, oy: 0, dx: -500, dy: -500 },
      { frame: { w: 800, h: 600 }, image: { w: 1600, h: 900 }, scale: 2, ox: -2400, oy: -1200, dx: 900, dy: 900 },
      { frame: { w: 400, h: 300 }, image: { w: 40000, h: 301 }, scale: 1, ox: -100, oy: 0, dx: 5, dy: 1 },
      { frame: { w: 640, h: 480 }, image: { w: 1920, h: 1080 }, scale: 1.25, ox: -777, oy: -333, dx: -1, dy: 2.5 },
    ]
    for (const c of cases) {
      const bars = mod.scrollBars(c.frame, c.image, at(c.ox, c.oy, c.scale))
      expect(bars.x).not.toBeNull()
      expect(bars.y).not.toBeNull()
      const now = viewTransform(c.frame, c.image, at(c.ox, c.oy, c.scale))
      const next = viewTransform(
        c.frame,
        c.image,
        at(
          (now?.ox ?? 0) + mod.thumbDragToPan(c.dx, bars.x as Axis),
          (now?.oy ?? 0) + mod.thumbDragToPan(c.dy, bars.y as Axis),
          c.scale,
        ),
      )
      expect(next).not.toBeNull()
      const t = next as { s: number; ox: number; oy: number }
      expect(t.ox).toBeGreaterThanOrEqual(c.frame.w - c.image.w * c.scale)
      expect(t.ox).toBeLessThanOrEqual(0)
      expect(t.oy).toBeGreaterThanOrEqual(c.frame.h - c.image.h * c.scale)
      expect(t.oy).toBeLessThanOrEqual(0)
      const after = mod.scrollBars(c.frame, c.image, at(t.ox, t.oy, c.scale))
      for (const bar of [after.x, after.y] as Axis[]) {
        expect(bar.offset).toBeGreaterThanOrEqual(0)
        expect(bar.offset).toBeLessThanOrEqual(bar.track - bar.thumb + 1e-9)
        expect(Number.isInteger(bar.value)).toBe(true)
        expect(bar.value).toBeGreaterThanOrEqual(0)
        expect(bar.value).toBeLessThanOrEqual(100)
      }
    }
  })

  it('AC-167.3 negative: with the thumb as long as the track the change is 0, not a division by zero', async () => {
    const mod = await load()
    const bar = mod.scrollBars({ w: 20, h: 20 }, { w: 30, h: 10 }, at(0, 0)).x
    expect(bar).not.toBeNull()
    expect((bar as Axis).thumb).toBe((bar as Axis).track)
    expect(mod.thumbDragToPan(15, bar as Axis)).toBe(0)
    expect(mod.thumbDragToPan(-15, bar as Axis)).toBe(0)
  })
})
