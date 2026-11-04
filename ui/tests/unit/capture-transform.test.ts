/** @vitest-environment node */

import { existsSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

import type { Annotation } from '../../src/renderer/src/features/capture/capture-annotate'
import { textBackgroundBox } from '../../src/renderer/src/features/capture/capture-text-metrics'

type Transform = typeof import('../../src/renderer/src/features/capture/capture-transform')
type BoxGeometry = { x: number; y: number; width: number; height: number }

const TRANSFORM_FILE = fileURLToPath(new URL('../../src/renderer/src/features/capture/capture-transform.ts', import.meta.url))

/** The module is new in Session 43: assert it exists, then load it as a namespace and check the export first. */
async function loadTransform(): Promise<Transform> {
  expect(existsSync(TRANSFORM_FILE), 'capture-transform.ts exists').toBe(true)
  const tx = await import('../../src/renderer/src/features/capture/capture-transform')
  expect(typeof tx.resizeBox).toBe('function')
  return tx
}

const RECT: Extract<Annotation, { type: 'rect' }> = {
  type: 'rect',
  x: 10,
  y: 20,
  width: 30,
  height: 40,
  color: '#FF0000',
  stroke_width: 3,
}

const at = (x: number, y: number) => ({ x, y })
const geometry = (mark: BoxGeometry): BoxGeometry => ({ x: mark.x, y: mark.y, width: mark.width, height: mark.height })
const HANDLES = ['nw', 'n', 'ne', 'e', 'se', 's', 'sw', 'w'] as const

describe('MEU-100 capture transform', () => {
  it('AC-100.1 TRANSFORM handle sizes and the eight box handle points', async () => {
    const tx = await loadTransform()
    expect(tx.RESIZE_HANDLE_CSS).toBe(8)
    expect(tx.RESIZE_HIT_CSS).toBe(12)
    expect(tx.boxHandlePoints({ x: 10, y: 20, width: 30, height: 40 })).toEqual({
      nw: at(10, 20),
      n: at(25, 20),
      ne: at(40, 20),
      e: at(40, 40),
      se: at(40, 60),
      s: at(25, 60),
      sw: at(10, 60),
      w: at(10, 40),
    })
  })

  it('AC-100.2 resizeBox moves only the edges the handle names', async () => {
    const tx = await loadTransform()
    const cases: Array<[(typeof HANDLES)[number], number, number, BoxGeometry]> = [
      ['se', 50, 70, { x: 10, y: 20, width: 40, height: 50 }],
      ['nw', 5, 5, { x: 5, y: 5, width: 35, height: 55 }],
      ['ne', 45, 15, { x: 10, y: 15, width: 35, height: 45 }],
      ['sw', 0, 65, { x: 0, y: 20, width: 40, height: 45 }],
      ['n', 99, 10, { x: 10, y: 10, width: 30, height: 50 }],
      ['e', 60, 0, { x: 10, y: 20, width: 50, height: 40 }],
      ['s', 0, 80, { x: 10, y: 20, width: 30, height: 60 }],
      ['w', 20, 99, { x: 20, y: 20, width: 20, height: 40 }],
    ]
    for (const [handle, px, py, expected] of cases) {
      expect(tx.resizeBox(RECT, handle, at(px, py), 100, 100), handle).toEqual({ ...RECT, ...expected })
    }
  })

  it('AC-100.3 resizeBox normalizes a crossed drag, keeps the stationary edge on a collapse and clamps to the image', async () => {
    const tx = await loadTransform()
    const box = (x: number, y: number, width: number, height: number) => ({ ...RECT, x, y, width, height })
    const cases: Array<[string, BoxGeometry, (typeof HANDLES)[number], number, number, BoxGeometry]> = [
      ['se crossed', RECT, 'se', 5, 5, { x: 5, y: 5, width: 5, height: 15 }],
      ['se onto the opposite corner', RECT, 'se', 10, 20, { x: 10, y: 20, width: 1, height: 1 }],
      ['w collapse at the east edge', box(98, 20, 1, 40), 'w', 99, 30, { x: 98, y: 20, width: 1, height: 40 }],
      ['n collapse at the south edge', box(10, 98, 30, 1), 'n', 20, 99, { x: 10, y: 98, width: 30, height: 1 }],
      ['e collapse at the west edge', box(0, 20, 5, 40), 'e', 0, 30, { x: 0, y: 20, width: 1, height: 40 }],
      ['s collapse at the north edge', box(10, 0, 30, 5), 's', 20, 0, { x: 10, y: 0, width: 30, height: 1 }],
    ]
    for (const [label, start, handle, px, py, expected] of cases) {
      const out = tx.resizeBox({ ...RECT, ...start }, handle, at(px, py), 100, 100)
      expect(geometry(out), label).toEqual(expected)
      expect(out.x + out.width, `${label} right edge`).toBeLessThanOrEqual(99)
      expect(out.y + out.height, `${label} bottom edge`).toBeLessThanOrEqual(99)
    }
    const far = tx.resizeBox(RECT, 'se', at(500, 500), 100, 100)
    expect(far.x + far.width, 'far right edge').toBe(99)
    expect(far.y + far.height, 'far bottom edge').toBe(99)
    const fractional = tx.resizeBox(RECT, 'se', at(40.6, 60.4), 100, 100)
    for (const value of [fractional.x, fractional.y, fractional.width, fractional.height]) {
      expect(Number.isInteger(value), `fractional ${value}`).toBe(true)
    }
    const pixelate: Annotation = { type: 'pixelate', x: 10, y: 20, width: 30, height: 40, block_size: 12 }
    expect(tx.resizeBox(pixelate, 'se', at(50, 70), 100, 100)).toEqual({ ...pixelate, width: 40, height: 50 })
    const highlight: Annotation = { type: 'highlight', x: 10, y: 20, width: 30, height: 40, color: '#FFFF00', opacity: 0.35 }
    expect(tx.resizeBox(highlight, 'se', at(50, 70), 100, 100)).toEqual({ ...highlight, width: 40, height: 50 })
    const eraser: Annotation = { type: 'eraser', x: 10, y: 20, width: 30, height: 40 }
    const erased = tx.resizeBox(eraser, 'se', at(50, 70), 100, 100)
    expect(erased).toEqual({ type: 'eraser', x: 10, y: 20, width: 40, height: 50 })
    expect(Object.keys(erased).sort()).toEqual(['height', 'type', 'width', 'x', 'y'])
  })

  it('AC-100.4 hitResizeHandle keeps a constant CSS hit square at every scale; cursorForHandle names each resize cursor', async () => {
    const tx = await loadTransform()
    const points = tx.boxHandlePoints({ x: 10, y: 20, width: 30, height: 40 })
    const ox = 7
    const oy = 11
    for (const scale of [0.5, 1, 1.5, 2]) {
      for (const id of HANDLES) {
        const point = points[id]
        const hit = tx.hitResizeHandle(points, { cssX: ox + point.x * scale, cssY: oy + point.y * scale, scale, ox, oy })
        expect(hit, `${id} at scale ${scale}`).toBe(id)
      }
    }
    const se = points.se
    expect(tx.hitResizeHandle(points, { cssX: ox + se.x + 5, cssY: oy + se.y, scale: 1, ox, oy }), '5 px off').toBe('se')
    expect(tx.hitResizeHandle(points, { cssX: ox + se.x + 7, cssY: oy + se.y, scale: 1, ox, oy }), '7 px off').toBeNull()
    // A 4-image-px-wide box at scale 1 puts nw (10,20) and n (12,20) both inside the hit square.
    const narrow = tx.boxHandlePoints({ x: 10, y: 20, width: 4, height: 40 })
    const near = (x: number) => tx.hitResizeHandle(narrow, { cssX: ox + x, cssY: oy + 20, scale: 1, ox, oy })
    expect(near(10.5), 'nearer nw').toBe('nw')
    expect(near(11.5), 'nearer n').toBe('n')
    expect(near(11), 'exact tie').toBe('nw')
    expect(Object.fromEntries(HANDLES.map((id) => [id, tx.cursorForHandle(id)]))).toEqual({
      nw: 'nwse-resize',
      se: 'nwse-resize',
      ne: 'nesw-resize',
      sw: 'nesw-resize',
      n: 'ns-resize',
      s: 'ns-resize',
      e: 'ew-resize',
      w: 'ew-resize',
    })
  })
})

type TextMark = Extract<Annotation, { type: 'text' }>
type Corner = 'nw' | 'ne' | 'se' | 'sw'

/** MEU-101 adds the text exports to the same module: check them before any call. */
async function loadTextScale(): Promise<Transform> {
  const tx = await loadTransform()
  expect(typeof tx.textPlateHandlePoints).toBe('function')
  expect(typeof tx.scaleTextMark).toBe('function')
  return tx
}

const TEXT: TextMark = { type: 'text', x: 10, y: 10, text: 'Hi', font_size: 16, color: '#FF0000', bg_color: null }
const OPPOSITE: Record<Corner, Corner> = { nw: 'se', ne: 'sw', se: 'nw', sw: 'ne' }

function plateCorners(mark: TextMark): Record<Corner, { x: number; y: number }> {
  const p = textBackgroundBox(mark)
  return {
    nw: at(p.x, p.y),
    ne: at(p.x + p.width, p.y),
    se: at(p.x + p.width, p.y + p.height),
    sw: at(p.x, p.y + p.height),
  }
}

function expectNear(actual: { x: number; y: number }, expected: { x: number; y: number }, label: string): void {
  expect(Math.abs(actual.x - expected.x), `${label} x`).toBeLessThanOrEqual(1)
  expect(Math.abs(actual.y - expected.y), `${label} y`).toBeLessThanOrEqual(1)
}

describe('MEU-101 text scale', () => {
  it('AC-101.1 TEXT_SCALE: four plate corners; a corner drag scales font_size about the opposite corner, 1..400, unclamped x/y', async () => {
    const tx = await loadTextScale()
    const plate = textBackgroundBox(TEXT)
    const corners = plateCorners(TEXT)
    const points = tx.textPlateHandlePoints(TEXT)
    expect(Object.keys(points).sort(), 'corners only').toEqual(['ne', 'nw', 'se', 'sw'])
    expect(points).toEqual(corners)
    const anchor = corners.nw
    const doubled = tx.scaleTextMark(TEXT, 'se', at(anchor.x + 2 * plate.width, anchor.y + 2 * plate.height), 1000, 1000)
    expect(doubled.font_size, 'se at twice the plate').toBe(32)
    expectNear(plateCorners(doubled).nw, anchor, 'se keeps nw')
    expect({ ...doubled, x: TEXT.x, y: TEXT.y, font_size: TEXT.font_size }, 'only x, y and font_size change').toEqual(TEXT)
    expect(tx.scaleTextMark(TEXT, 'se', anchor, 1000, 1000).font_size, 'onto the anchor').toBe(1)
    expect(tx.scaleTextMark(TEXT, 'se', at(999, 999), 1000, 1000).font_size, 'far').toBe(400)
    const fromNw = tx.scaleTextMark(TEXT, 'nw', at(corners.se.x - 2 * plate.width, corners.se.y - 2 * plate.height), 1000, 1000)
    expect(fromNw.font_size, 'nw dragged out').toBeGreaterThan(16)
    expectNear(plateCorners(fromNw).se, corners.se, 'nw keeps se')
    // Image edge (review round 1 F2): the glyph bearing puts the plate 6 px below y, so a grown mark needs y < 0.
    const edge: TextMark = { ...TEXT, y: 0 }
    expect(textBackgroundBox(edge)).toEqual({ x: 10, y: 6, width: 15, height: 12 })
    const grown = tx.scaleTextMark(edge, 'se', at(40, 30), 100, 100)
    expect({ x: grown.x, y: grown.y, font_size: grown.font_size }).toEqual({ x: 10, y: -6, font_size: 32 })
    expect(textBackgroundBox(grown)).toEqual({ x: 10, y: 6, width: 30, height: 24 })
    // Each anchor plate corner sits 5 px from an image corner of a 100×100 image; the handle goes to the far edge.
    const cases: Array<[Corner, TextMark, { x: number; y: number }]> = [
      ['se', { ...TEXT, x: 5, y: -1 }, at(99, 99)],
      ['nw', { ...TEXT, x: 80, y: 77 }, at(0, 0)],
      ['ne', { ...TEXT, x: 5, y: 77 }, at(99, 0)],
      ['sw', { ...TEXT, x: 80, y: -1 }, at(0, 99)],
    ]
    for (const [handle, mark, point] of cases) {
      const anchorCorner = plateCorners(mark)[OPPOSITE[handle]]
      expect(Math.min(anchorCorner.x, 100 - anchorCorner.x), `${handle} anchor x near an image corner`).toBeLessThanOrEqual(10)
      expect(Math.min(anchorCorner.y, 100 - anchorCorner.y), `${handle} anchor y near an image corner`).toBeLessThanOrEqual(10)
      const scaled = tx.scaleTextMark(mark, handle, point, 100, 100)
      expect(scaled.font_size, `${handle} grows`).toBeGreaterThan(16)
      expectNear(plateCorners(scaled)[OPPOSITE[handle]], anchorCorner, `${handle} keeps its anchor`)
    }
  })
})
