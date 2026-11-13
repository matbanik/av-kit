/** @vitest-environment node */

import { describe, expect, it } from 'vitest'

import type { Annotation } from '../../src/renderer/src/features/capture/capture-annotate'

const arrow = (
  from: [number, number],
  to: [number, number],
): Extract<Annotation, { type: 'arrow' }> => ({
  type: 'arrow',
  color: '#FF0000',
  stroke_width: 3,
  from,
  to,
})

const box = (x: number, y: number, width: number, height: number): Annotation => ({
  type: 'rect',
  x,
  y,
  width,
  height,
  color: '#00FF00',
  stroke_width: 2,
})

const highlight = (x: number, y: number, width: number, height: number): Annotation => ({
  type: 'highlight',
  x,
  y,
  width,
  height,
  color: '#FFFF00',
  opacity: 0.4,
})

const label = (x: number, y: number, text: string, bg: string | null = null): Annotation => ({
  type: 'text',
  x,
  y,
  text,
  color: '#FFFFFF',
  font_size: 16,
  bg_color: bg,
})

describe('MEU-60 hit-test', () => {
  it('AC-60.1 CSS hit radii stay constant across fit scales; letterbox misses; selected-arrow handles beat bodies; coincident from/to selects to', async () => {
    const mod = await import('../../src/renderer/src/features/capture/capture-hit-test')
    expect(mod.HANDLE_RADIUS_CSS).toBe(5)
    expect(mod.HIT_RADIUS_CSS).toBe(10)
    expect(mod.HIT_PADDING_CSS).toBe(6)
    const marks = [arrow([20, 20], [80, 20])]
    const nearHandle = (scale: number) =>
      mod.hitTestMarks({
        cssX: 20 * scale + 4,
        cssY: 20 * scale,
        scale,
        ox: 0,
        oy: 0,
        imageW: 100,
        imageH: 100,
        annotations: marks,
        selectedIndex: 0,
      })
    expect(nearHandle(1)).toEqual({ kind: 'handle', end: 'from', index: 0 })
    expect(nearHandle(0.5)).toEqual({ kind: 'handle', end: 'from', index: 0 })
    const farHandle = (scale: number) =>
      mod.hitTestMarks({
        cssX: 20 * scale + 8,
        cssY: 20 * scale,
        scale,
        ox: 0,
        oy: 0,
        imageW: 100,
        imageH: 100,
        annotations: marks,
        selectedIndex: 0,
      })
    expect(farHandle(1)).not.toEqual({ kind: 'handle', end: 'from', index: 0 })
    expect(farHandle(0.5)).not.toEqual({ kind: 'handle', end: 'from', index: 0 })
    expect(
      mod.hitTestMarks({
        cssX: 10,
        cssY: 50,
        scale: 0.5,
        ox: 40,
        oy: 0,
        imageW: 100,
        imageH: 100,
        annotations: marks,
        selectedIndex: 0,
      }),
    ).toBeNull()
    const covered: Annotation[] = [highlight(0, 0, 100, 100), arrow([10, 10], [90, 90])]
    expect(
      mod.hitTestMarks({
        cssX: 10,
        cssY: 10,
        scale: 1,
        ox: 0,
        oy: 0,
        imageW: 100,
        imageH: 100,
        annotations: covered,
        selectedIndex: 1,
      }),
    ).toEqual({ kind: 'handle', end: 'from', index: 1 })
    expect(
      mod.hitTestMarks({
        cssX: 40,
        cssY: 40,
        scale: 1,
        ox: 0,
        oy: 0,
        imageW: 100,
        imageH: 100,
        annotations: [arrow([40, 40], [40, 40])],
        selectedIndex: 0,
      }),
    ).toEqual({ kind: 'handle', end: 'to', index: 0 })
  })

  it('AC-60.2 body translate keeps arrow delta; endpoint edit keeps the other end; box size unchanged; collapsing nonzero arrow cancels', async () => {
    const mod = await import('../../src/renderer/src/features/capture/capture-hit-test')
    const shaft = arrow([10, 10], [30, 18])
    const moved = mod.translateBody(shaft, 4, -2, 100, 80)
    expect(moved).toMatchObject({ type: 'arrow', from: [14, 8], to: [34, 16] })
    expect(moved.to[0] - moved.from[0]).toBe(20)
    expect(moved.to[1] - moved.from[1]).toBe(8)
    const head = mod.moveEndpoint(shaft, 'to', { x: 50, y: 12 }, 100, 80)
    expect(head).toMatchObject({ type: 'arrow', from: [10, 10], to: [50, 12] })
    const boxed = box(5, 5, 20, 10)
    const shifted = mod.translateBody(boxed, 3, 4, 100, 80)
    expect(shifted).toMatchObject({ type: 'rect', x: 8, y: 9, width: 20, height: 10 })
    expect(mod.moveEndpoint(shaft, 'to', { x: 10, y: 10 }, 100, 80)).toBeNull()
  })

  it('AC-60.3 textBackgroundBox plate is hittable when bg_color is empty', async () => {
    const hit = await import('../../src/renderer/src/features/capture/capture-hit-test')
    const metrics = await import('../../src/renderer/src/features/capture/capture-text-metrics')
    const mark = label(10, 20, 'Hi', null)
    const plate = metrics.textBackgroundBox({ x: 10, y: 20, text: 'Hi', font_size: 16 })
    const target = hit.hitTestMarks({
      cssX: plate.x + plate.width / 2,
      cssY: plate.y + plate.height / 2,
      scale: 1,
      ox: 0,
      oy: 0,
      imageW: 200,
      imageH: 200,
      annotations: [mark],
      selectedIndex: 0,
    })
    expect(target).toEqual({ kind: 'body', index: 0 })
  })

  it('AC-60.3 fitted 0.2 scale still hits the label away from the image-space origin', async () => {
    const hit = await import('../../src/renderer/src/features/capture/capture-hit-test')
    const mark = label(100, 80, 'i', null)
    const scale = 0.2
    const origin = { x: 100 * scale, y: 80 * scale }
    const away = hit.hitTestMarks({
      cssX: origin.x + 12,
      cssY: origin.y + 2,
      scale,
      ox: 0,
      oy: 0,
      imageW: 1920,
      imageH: 1080,
      annotations: [mark],
      selectedIndex: 0,
    })
    expect(away).toEqual({ kind: 'body', index: 0 })
  })
})

describe('MEU-66 hit-test at zoom (Session 29 plan AC-66.5, regression lock)', () => {
  it('AC-66.5 handle and body radii stay CSS-sized at s = 4 with a panned origin', async () => {
    const mod = await import('../../src/renderer/src/features/capture/capture-hit-test')
    const s = 4
    const ox = -300
    const oy = -120
    const marks = [arrow([100, 60], [160, 60])]
    const at = (cssX: number, cssY: number, selectedIndex: number | null) =>
      mod.hitTestMarks({ cssX, cssY, scale: s, ox, oy, imageW: 400, imageH: 300, annotations: marks, selectedIndex })
    const fromCss = { x: ox + 100 * s, y: oy + 60 * s }
    expect(at(fromCss.x + 4, fromCss.y, 0)).toEqual({ kind: 'handle', end: 'from', index: 0 })
    const midCss = { x: ox + 130 * s, y: oy + 60 * s }
    expect(at(midCss.x, midCss.y + 9, null)).toEqual({ kind: 'body', index: 0 })
    expect(at(midCss.x, midCss.y + 11, null)).toBeNull()
  })

  it('AC-66.5 negative: a letterbox point in a centred zoomed-out frame hits nothing', async () => {
    const mod = await import('../../src/renderer/src/features/capture/capture-hit-test')
    const marks = [box(0, 0, 1600, 900)]
    // 1600×900 at s = 0.25 in 800×600: the image spans x 200–600, y 187.5–412.5.
    const hit = mod.hitTestMarks({
      cssX: 100,
      cssY: 300,
      scale: 0.25,
      ox: 200,
      oy: 187.5,
      imageW: 1600,
      imageH: 900,
      annotations: marks,
      selectedIndex: null,
    })
    expect(hit).toBeNull()
  })
})

describe('MEU-90 pixelate hit-test (REGION_EDIT)', () => {
  it('AC-90.10 markLabel names a pixelate; a click inside its rectangle hits the body; translateBody keeps size and block', async () => {
    const mod = await import('../../src/renderer/src/features/capture/capture-hit-test')
    const pix: Annotation = { type: 'pixelate', x: 10, y: 10, width: 60, height: 40, block_size: 7 }
    expect(mod.markLabel(pix, 0)).toBe('Pixelate 1')
    expect(mod.markLabel(pix, 2)).toBe('Pixelate 3')
    const at = (cssX: number, cssY: number, annotations: Annotation[]) =>
      mod.hitTestMarks({
        cssX,
        cssY,
        scale: 1,
        ox: 0,
        oy: 0,
        imageW: 100,
        imageH: 100,
        annotations,
        selectedIndex: null,
      })
    // The centre is 20 px from every edge, beyond HIT_RADIUS_CSS: only a filled body hits it.
    expect(at(40, 30, [pix])).toEqual({ kind: 'body', index: 0 })
    expect(at(40, 30, [box(10, 10, 60, 40)])).toBeNull()
    expect(at(90, 80, [pix])).toBeNull()
    expect(mod.translateBody(pix, 5, -3, 100, 100)).toEqual({ ...pix, x: 15, y: 7 })
    expect(mod.translateBody(pix, 80, 0, 100, 100)).toMatchObject({ x: 90, width: 60, height: 40, block_size: 7 })
  })
})

describe('MEU-91 eraser hit-test (REGION_EDIT)', () => {
  it('AC-91.9 markLabel names an eraser; a click inside its rectangle hits the body; translateBody keeps size', async () => {
    const mod = await import('../../src/renderer/src/features/capture/capture-hit-test')
    const eraser: Annotation = { type: 'eraser', x: 10, y: 10, width: 60, height: 40 }
    // Session 68 SMART_ERASER (D-683): the chip names the Smart eraser; the JSON type stays eraser.
    expect(mod.markLabel(eraser, 0)).toBe('Smart eraser 1')
    const at = (cssX: number, cssY: number, annotations: Annotation[]) =>
      mod.hitTestMarks({
        cssX,
        cssY,
        scale: 1,
        ox: 0,
        oy: 0,
        imageW: 100,
        imageH: 100,
        annotations,
        selectedIndex: null,
      })
    // The centre is 20 px from every edge, beyond HIT_RADIUS_CSS: only a filled body hits it.
    expect(at(40, 30, [eraser])).toEqual({ kind: 'body', index: 0 })
    expect(at(90, 80, [eraser])).toBeNull()
    expect(mod.translateBody(eraser, 5, -3, 100, 100)).toEqual({ ...eraser, x: 15, y: 7 })
  })
})

describe('MEU-100 resize hit order (HIT_ORDER)', () => {
  const at = (cssX: number, cssY: number, annotations: Annotation[], selectedIndex: number | null) => ({
    cssX,
    cssY,
    scale: 1,
    ox: 0,
    oy: 0,
    imageW: 100,
    imageH: 100,
    annotations,
    selectedIndex,
  })

  it('AC-100.5 a selected box mark returns its resize handle before any body; an unselected mark and an arrow never do', async () => {
    const mod = await import('../../src/renderer/src/features/capture/capture-hit-test')
    const marks = [box(10, 20, 30, 40)]
    expect(mod.hitTestMarks(at(40, 60, marks, 0))).toEqual({ kind: 'resize', handle: 'se', index: 0 })
    expect(mod.hitTestMarks(at(40, 60, marks, null))).toEqual({ kind: 'body', index: 0 })
    const stacked = [box(10, 20, 30, 40), box(35, 55, 20, 20)]
    expect(mod.hitTestMarks(at(40, 60, stacked, 0))).toEqual({ kind: 'resize', handle: 'se', index: 0 })
    expect(mod.hitTestMarks(at(25, 40, marks, 0))).toEqual({ kind: 'body', index: 0 })
    const arrows = [arrow([20, 20], [80, 60])]
    const kinds = new Set<string>()
    for (let x = 0; x < 100; x += 2) {
      for (let y = 0; y < 100; y += 2) {
        const hit = mod.hitTestMarks(at(x, y, arrows, 0))
        if (hit !== null) {
          kinds.add(hit.kind)
        }
      }
    }
    expect(kinds.has('resize')).toBe(false)
  })
})
