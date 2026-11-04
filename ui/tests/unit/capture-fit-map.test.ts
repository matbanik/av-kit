/** @vitest-environment node */

import { describe, expect, it } from 'vitest'

describe('MEU-59 FIT_MAP', () => {
  it('AC-59.1 maps the letterboxed example and rejects the letterbox', async () => {
    const mod = await import('../../src/renderer/src/features/capture/capture-fit-map')
    const mapped = mod.mapPointerToImage({
      clientX: 400,
      clientY: 300,
      left: 0,
      top: 0,
      containerW: 800,
      containerH: 600,
      imageW: 1600,
      imageH: 900,
    })
    expect(mapped).toEqual({ x: 800, y: 450 })
    const letterbox = mod.mapPointerToImage({
      clientX: 400,
      clientY: 10,
      left: 0,
      top: 0,
      containerW: 800,
      containerH: 600,
      imageW: 1600,
      imageH: 900,
    })
    expect(letterbox).toBeNull()
  })

  it('AC-59.18 stored image points do not change when the container resizes', async () => {
    const mod = await import('../../src/renderer/src/features/capture/capture-fit-map')
    const a = mod.mapPointerToImage({
      clientX: 400,
      clientY: 300,
      left: 0,
      top: 0,
      containerW: 800,
      containerH: 600,
      imageW: 1600,
      imageH: 900,
    })
    const b = mod.mapPointerToImage({
      clientX: 800,
      clientY: 600,
      left: 0,
      top: 0,
      containerW: 1600,
      containerH: 1200,
      imageW: 1600,
      imageH: 900,
    })
    expect(a).toEqual(b)
    expect(a).toEqual({ x: 800, y: 450 })
  })
})

describe('MEU-66 VIEW_TRANSFORM and VIEW_MAP (Session 29 plan AC-66.2, AC-66.3)', () => {
  const container = { w: 800, h: 600 }
  const image = { w: 1600, h: 900 }

  it('AC-66.2 viewTransform at fit equals fitScaleOrigin on the MEU-59 worked example', async () => {
    const mod = await import('../../src/renderer/src/features/capture/capture-fit-map')
    expect(typeof mod.viewTransform).toBe('function')
    const fit = mod.fitScaleOrigin({ containerW: 800, containerH: 600, imageW: 1600, imageH: 900 })
    expect(fit).toEqual({ s: 0.5, ox: 0, oy: 75 })
    expect(mod.viewTransform(container, image, { kind: 'fit' })).toEqual(fit)
  })

  it('AC-66.2 viewTransform at a scale centres an axis that fits and clamps an axis that overflows', async () => {
    const mod = await import('../../src/renderer/src/features/capture/capture-fit-map')
    expect(typeof mod.viewTransform).toBe('function')
    expect(mod.viewTransform(container, image, { kind: 'scale', scale: 2, ox: -1000, oy: -450 })).toEqual({
      s: 2,
      ox: -1000,
      oy: -450,
    })
    // 1600×0.5 = 800 fits the width exactly and 900×0.5 = 450 fits the height: both axes centre.
    expect(mod.viewTransform(container, image, { kind: 'scale', scale: 0.5, ox: -300, oy: -300 })).toEqual({
      s: 0.5,
      ox: 0,
      oy: 75,
    })
    // At 0.6 the width overflows (960 > 800) and clamps; the height (540) centres.
    const mixed = mod.viewTransform(container, image, { kind: 'scale', scale: 0.6, ox: 50, oy: -999 })
    expect(mixed?.ox).toBe(0)
    expect(mixed?.oy).toBeCloseTo(30, 9)
  })

  it('AC-66.2 negative: offsets beyond the range clamp; invalid sizes or scales return null', async () => {
    const mod = await import('../../src/renderer/src/features/capture/capture-fit-map')
    expect(typeof mod.viewTransform).toBe('function')
    expect(mod.viewTransform(container, image, { kind: 'scale', scale: 2, ox: 500, oy: 500 })).toEqual({
      s: 2,
      ox: 0,
      oy: 0,
    })
    expect(mod.viewTransform(container, image, { kind: 'scale', scale: 2, ox: -9999, oy: -9999 })).toEqual({
      s: 2,
      ox: 800 - 3200,
      oy: 600 - 1800,
    })
    expect(mod.viewTransform({ w: 0, h: 600 }, image, { kind: 'fit' })).toBeNull()
    expect(mod.viewTransform(container, { w: -1, h: 900 }, { kind: 'fit' })).toBeNull()
    expect(mod.viewTransform(container, image, { kind: 'scale', scale: Number.NaN, ox: 0, oy: 0 })).toBeNull()
    expect(mod.viewTransform(container, image, { kind: 'scale', scale: 0, ox: 0, oy: 0 })).toBeNull()
    expect(mod.viewTransform(container, image, { kind: 'scale', scale: 2, ox: Number.POSITIVE_INFINITY, oy: 0 })).toBeNull()
  })

  it('AC-66.3 VIEW_MAP maps ZOOM_EXAMPLE both ways, and the fit-only mapping differs', async () => {
    const mod = await import('../../src/renderer/src/features/capture/capture-fit-map')
    expect(typeof mod.mapPointerWithView).toBe('function')
    const t = { s: 2, ox: -1000, oy: -450 }
    expect(mod.mapPointerWithView(400, 300, 0, 0, t, 1600, 900)).toEqual({ x: 700, y: 375 })
    expect(mod.mapImageToPointerWithView({ x: 700, y: 375 }, 0, 0, t)).toEqual({ x: 400, y: 300 })
    expect(mod.mapPointerWithView(410, 320, 10, 20, t, 1600, 900)).toEqual({ x: 700, y: 375 })
    const fitOnly = mod.mapPointerToImage({
      clientX: 400,
      clientY: 300,
      left: 0,
      top: 0,
      containerW: 800,
      containerH: 600,
      imageW: 1600,
      imageH: 900,
    })
    expect(fitOnly).toEqual({ x: 800, y: 450 })
  })

  it('AC-66.3 a 7×7 grid round-trips within 0.5 px before rounding at a non-fit zoom', async () => {
    const mod = await import('../../src/renderer/src/features/capture/capture-fit-map')
    expect(typeof mod.mapPointerWithView).toBe('function')
    const t = { s: 2, ox: -1000, oy: -450 }
    for (let row = 0; row < 7; row += 1) {
      for (let col = 0; col < 7; col += 1) {
        const point = { x: 520 + col * 40, y: 240 + row * 40 }
        const css = mod.mapImageToPointerWithView(point, 0, 0, t)
        const back = mod.mapPointerWithView(css.x, css.y, 0, 0, t, 1600, 900)
        expect(back, `${point.x},${point.y}`).not.toBeNull()
        expect(Math.abs((css.x - t.ox) / t.s - point.x)).toBeLessThanOrEqual(0.5)
        expect(Math.abs((back?.x ?? -1) - point.x)).toBeLessThanOrEqual(0.5)
        expect(Math.abs((back?.y ?? -1) - point.y)).toBeLessThanOrEqual(0.5)
      }
    }
  })

  it('AC-66.3 negative: a point outside the zoomed image maps to null (letterbox of a centred axis)', async () => {
    const mod = await import('../../src/renderer/src/features/capture/capture-fit-map')
    expect(typeof mod.mapPointerWithView).toBe('function')
    // 0.25 zoom: 400×225 image centred at (200, 187.5) in the 800×600 frame.
    const t = mod.viewTransform(container, image, { kind: 'scale', scale: 0.25, ox: 0, oy: 0 })
    expect(t).toEqual({ s: 0.25, ox: 200, oy: 187.5 })
    expect(mod.mapPointerWithView(100, 300, 0, 0, t as { s: number; ox: number; oy: number }, 1600, 900)).toBeNull()
    expect(mod.mapPointerWithView(400, 50, 0, 0, t as { s: number; ox: number; oy: number }, 1600, 900)).toBeNull()
    expect(mod.mapPointerWithView(400, 300, 0, 0, t as { s: number; ox: number; oy: number }, 1600, 900)).toEqual({
      x: 800,
      y: 450,
    })
  })
})
