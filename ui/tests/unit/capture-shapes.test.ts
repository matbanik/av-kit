import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

import { describe, expect, expectTypeOf, it } from 'vitest'

import { arrowShaftSpan } from '../../src/renderer/src/features/capture/capture-arrow-head'
import type { Annotation, StepAnnotation } from '../../src/renderer/src/features/capture/capture-annotate'
import { annotateInSchema, stepSchema } from '../../src/renderer/src/features/capture/capture-annotate'
import { CAPTURE_EVENTS } from '../../src/renderer/src/features/capture/capture-commands'
import * as shapes from '../../src/renderer/src/features/capture/capture-shapes'
import type { ArrowHead, BoxShape } from '../../src/renderer/src/features/capture/capture-shapes'
import * as step from '../../src/renderer/src/features/capture/capture-step'
import type { StepLayout } from '../../src/renderer/src/features/capture/capture-step'
import type { LetterTool } from '../../src/renderer/src/features/capture/capture-toolbar'
import { readToolStyles, TOOL_STYLE_DEFAULTS } from '../../src/renderer/src/features/capture/capture-tool-style'
import type { StyleTool, ToolStyle } from '../../src/renderer/src/features/capture/capture-tool-style'
import type { CaptureTool } from '../../src/renderer/src/features/capture/CaptureViewport'
import { hitTestMarks, markLabel } from '../../src/renderer/src/features/capture/capture-hit-test'
import type { HitTestInput } from '../../src/renderer/src/features/capture/capture-hit-test'
import { CAPTURE_EDIT_IDS, listCommands } from '../../src/renderer/src/registry/commandRegistry'
import { buildShortcutMap, normalizeChord, paletteCommands, RESERVED_CHORDS } from '../../src/renderer/src/registry/shortcuts'

// Session 72 (MEU-106, MEU-107): the names, the schemas and the read-back that row 2 makes pass.

const ARROW = { type: 'arrow', from: [4, 6], to: [40, 30], color: 'red', stroke_width: 3 }
const RECT = { type: 'rect', x: 4, y: 6, width: 20, height: 10, color: 'red', stroke_width: 2 }
const STEP = { type: 'step', x: 12, y: 9, number: 3, color: '#E0AF68', size: 24 }

const parses = (mark: Record<string, unknown>): boolean => annotateInSchema.safeParse({ annotations: [mark] }).success

describe('MEU-106 names', () => {
  it('AC-106.1 the head and shape literals, the helpers and the duplicate command exist', () => {
    expect(shapes.ARROW_HEADS).toEqual(['end', 'none', 'both'])
    expect(shapes.BOX_SHAPES).toEqual(['rect', 'ellipse'])
    expectTypeOf<ArrowHead>().toEqualTypeOf<'end' | 'none' | 'both'>()
    expectTypeOf<BoxShape>().toEqualTypeOf<'rect' | 'ellipse'>()
    expect(typeof shapes.shapeOption).toBe('function')
    expect(typeof shapes.duplicateMark).toBe('function')
    expect(typeof arrowShaftSpan).toBe('function')
    expect(CAPTURE_EDIT_IDS).toEqual(['capture:duplicate'])
    expect(CAPTURE_EVENTS.duplicate).toBe('av-kit:capture:duplicate')
    expectTypeOf<LetterTool>().toEqualTypeOf<Exclude<CaptureTool, 'step'>>()
    expectTypeOf<Extract<Annotation, { type: 'arrow' }>['head']>().toEqualTypeOf<ArrowHead | undefined>()
    expectTypeOf<Extract<Annotation, { type: 'rect' }>['shape']>().toEqualTypeOf<BoxShape | undefined>()
  })
})

describe('MEU-106 schema', () => {
  it('AC-106.7 annotateInSchema accepts head and shape and refuses values outside the Literal', () => {
    for (const head of ['end', 'none', 'both']) {
      expect(parses({ ...ARROW, head }), head).toBe(true)
    }
    expect(parses({ ...RECT, shape: 'rect' })).toBe(true)
    expect(parses({ ...RECT, shape: 'ellipse' })).toBe(true)
    expect(parses(ARROW)).toBe(true)
    expect(parses(RECT)).toBe(true)
    const bad = [
      { ...ARROW, head: 'End' },
      { ...ARROW, head: null },
      { ...ARROW, head: '\uD800' },
      { ...RECT, shape: 'circle' },
      { ...RECT, shape: 1 },
    ]
    for (const mark of bad) {
      expect(parses(mark), JSON.stringify(mark)).toBe(false)
    }
  })
})

describe('MEU-107 names', () => {
  it('AC-107.1 the step layout, colour and numbering helpers and the step types exist', () => {
    expect(typeof step.stepBadgeLayout).toBe('function')
    expect(typeof step.stepTextColor).toBe('function')
    expect(typeof step.nextStepNumber).toBe('function')
    expect(step.stepBadgeLayout.length).toBe(4)
    expectTypeOf<StepLayout>().toEqualTypeOf<{ radius: number; fontPx: number; baseline: number }>()
    expect(stepSchema.safeParse(STEP).success).toBe(true)
    expectTypeOf<StepAnnotation>().toEqualTypeOf<{
      type: 'step'
      x: number
      y: number
      number: number
      color: string
      size: number
    }>()
    expectTypeOf<'step'>().toMatchTypeOf<CaptureTool>()
    expectTypeOf<'step'>().toMatchTypeOf<StyleTool>()
    expectTypeOf<ToolStyle['stepSize']>().toEqualTypeOf<number | undefined>()
    expect(TOOL_STYLE_DEFAULTS.step).toEqual({ color: '#E0AF68', stepSize: 32 })
  })
})

describe('MEU-107 schema', () => {
  it('AC-107.8 annotateInSchema accepts a step and refuses each value of the input matrix', () => {
    expect(parses(STEP)).toBe(true)
    expect(parses({ ...STEP, number: 1, size: 12 })).toBe(true)
    expect(parses({ ...STEP, number: 999, size: 200, color: 'blue' })).toBe(true)
    const { size: _size, ...missing } = STEP
    const bad: Record<string, Record<string, unknown>> = {
      'x -1': { ...STEP, x: -1 },
      'x true': { ...STEP, x: true },
      'x 1.5': { ...STEP, x: 1.5 },
      'number 0': { ...STEP, number: 0 },
      'number 1000': { ...STEP, number: 1000 },
      'size 11': { ...STEP, size: 11 },
      'size 201': { ...STEP, size: 201 },
      'color empty': { ...STEP, color: '' },
      'color bell': { ...STEP, color: '\u0007' },
      'color surrogate': { ...STEP, color: '\uD800' },
      'extra label': { ...STEP, label: 'one' },
      'missing size': missing,
    }
    for (const [name, mark] of Object.entries(bad)) {
      expect(parses(mark), name).toBe(false)
    }
  })
})

describe('MEU-107 read-back', () => {
  const DEFAULT_STEP = { color: '#E0AF68', stepSize: 32 }
  const SIZES: Array<[string, unknown]> = [
    ['11', 11],
    ['201', 201],
    ['48.5', 48.5],
    ['"48"', '48'],
    ['true', true],
  ]
  const COLORS: Array<[string, unknown]> = [
    ['empty', ''],
    ['bell', '\u0007'],
    ['lone surrogate', '\uD800'],
    ['red', 'red'],
  ]

  it('AC-107.17 a good stored step leaf reads back as stored', () => {
    expect(readToolStyles({ step_color: '#123456', step_size: 48 }).step).toEqual({ color: '#123456', stepSize: 48 })
  })

  for (const [name, value] of SIZES) {
    it(`AC-107.17 step_size ${name} reads as the default`, () => {
      expect(readToolStyles({ step_color: '#E0AF68', step_size: value }).step).toEqual(DEFAULT_STEP)
    })
  }

  for (const [name, value] of COLORS) {
    it(`AC-107.17 step_color ${name} reads as the default`, () => {
      expect(readToolStyles({ step_color: value, step_size: 32 }).step).toEqual(DEFAULT_STEP)
    })
  }
})

// ------------------------------------------------------------ row 3 (Red)

type Pt = [number, number]
type ArrowFixture = { from: Pt; to: Pt; stroke: number; shaft_end: Pt | null }
type BothFixture = { from: Pt; to: Pt; stroke: number; shaft: [Pt, Pt] | null }
type StepFixture = { x: number; y: number; number: number; size: number; radius: number; font_px: number; baseline: number }
const GEOMETRY = JSON.parse(readFileSync(resolve(__dirname, '../e2e/fixtures/capture-geometry.json'), 'utf8')) as {
  arrows: ArrowFixture[]
  arrow_both: BothFixture[]
  steps: StepFixture[]
}

function nearSpan(got: [Pt, Pt] | null, want: [Pt, Pt] | null, where: string): void {
  if (want === null) {
    expect(got, where).toBeNull()
    return
  }
  expect(got, where).not.toBeNull()
  const flat = (got ?? []).flat()
  want.flat().forEach((value, i) => {
    expect(Math.abs((flat[i] ?? Number.NaN) - value), `${where} [${i}]`).toBeLessThanOrEqual(1e-9)
  })
}

describe('MEU-106 HEAD_PREVIEW span', () => {
  it('AC-106.9 arrowShaftSpan equals the fixture for "both", "end" and "none"', () => {
    for (const [i, entry] of GEOMETRY.arrow_both.entries()) {
      nearSpan(arrowShaftSpan(entry.from, entry.to, entry.stroke, 'both'), entry.shaft, `both ${i}`)
    }
    for (const [i, entry] of GEOMETRY.arrows.entries()) {
      const end = entry.shaft_end === null ? null : ([entry.from, entry.shaft_end] as [Pt, Pt])
      nearSpan(arrowShaftSpan(entry.from, entry.to, entry.stroke, 'end'), end, `end ${i}`)
      nearSpan(arrowShaftSpan(entry.from, entry.to, entry.stroke, 'none'), [entry.from, entry.to], `none ${i}`)
    }
  })
})

/** One press at 1:1 on a 400×300 image (ox = oy = 0). */
function press(annotations: Annotation[], at: Pt, selectedIndex: number | null = null, scale = 1): ReturnType<typeof hitTestMarks> {
  const input: HitTestInput = {
    cssX: at[0],
    cssY: at[1],
    scale,
    ox: 0,
    oy: 0,
    imageW: 400,
    imageH: 300,
    annotations,
    selectedIndex,
  }
  return hitTestMarks(input)
}

describe('MEU-106 HEAD_HIT', () => {
  const arrow = (head: ArrowHead): Annotation => ({
    type: 'arrow',
    from: [100, 100],
    to: [300, 100],
    color: '#FF0000',
    stroke_width: 20,
    ...(head === 'end' ? {} : { head }),
  })
  const CASES: Array<[string, ArrowHead, Pt, boolean]> = [
    ['end hits inside the end head', 'end', [240, 125], true],
    ['end misses where a start head would be', 'end', [160, 125], false],
    ['none misses beside the end', 'none', [240, 125], false],
    ['none hits the last 5 px of the shaft', 'none', [297, 100], true],
    ['both hits inside the start head', 'both', [160, 125], true],
    ['both hits inside the end head', 'both', [240, 125], true],
    ['end misses between the heads', 'end', [200, 125], false],
    ['none misses between the heads', 'none', [200, 125], false],
    ['both misses between the heads', 'both', [200, 125], false],
  ]
  it.each(CASES)('AC-106.10 %s', (_name, head, at, hits) => {
    const got = press([arrow(head)], at)
    expect(got).toEqual(hits ? { kind: 'body', index: 0 } : null)
  })

  it.each(['end', 'none', 'both'] as const)('AC-106.10 a selected %s arrow keeps its endpoint handles', (head) => {
    expect(press([arrow(head)], [100, 100], 0)).toEqual({ kind: 'handle', end: 'from', index: 0 })
    expect(press([arrow(head)], [300, 100], 0)).toEqual({ kind: 'handle', end: 'to', index: 0 })
  })
})

describe('MEU-106 ELLIPSE_HIT', () => {
  const ellipse = (x: number, y: number, width: number, height: number): Annotation => ({
    type: 'rect',
    x,
    y,
    width,
    height,
    color: '#FF0000',
    stroke_width: 3,
    shape: 'ellipse',
  })
  const BIG = ellipse(10, 10, 200, 120)
  const WIDE = ellipse(10, 10, 200, 20)
  const TALL = ellipse(10, 10, 20, 200)
  const SMALL = ellipse(10, 10, 60, 40)
  const DOT = ellipse(50, 50, 1, 1)
  const CASES: Array<[string, Annotation, Pt, number, boolean]> = [
    ['the outline at (110, 10) hits', BIG, [110, 10], 1, true],
    ['the box corner (11, 11) misses', BIG, [11, 11], 1, false],
    ['the centre misses', BIG, [110, 70], 1, false],
    ['5 px past a wide tip hits', WIDE, [215, 20], 1, true],
    ['12 px past a wide tip misses', WIDE, [222, 20], 1, false],
    ['50 px past a wide tip misses', WIDE, [260, 20], 1, false],
    ['5 px past a tall tip hits', TALL, [20, 215], 1, true],
    ['12 px past a tall tip misses', TALL, [20, 222], 1, false],
    ['50 px past a tall tip misses', TALL, [20, 260], 1, false],
    ['at scale 2 the outline hits', SMALL, [80, 20], 2, true],
    ['at scale 2 12 CSS px inside misses', SMALL, [80, 32], 2, false],
    ['at scale 0.5 8 CSS px inside hits', BIG, [55, 13], 0.5, true],
    ['at scale 0.5 12 CSS px inside misses', BIG, [55, 17], 0.5, false],
    ['a 1x1 ellipse is hit as its box', DOT, [50, 50], 1, true],
    ['a 1x1 ellipse misses beyond its box', DOT, [70, 70], 1, false],
  ]
  it.each(CASES)('AC-106.13 %s', (_name, mark, at, scale, hits) => {
    expect(press([mark], at, null, scale)).toEqual(hits ? { kind: 'body', index: 0 } : null)
  })
})

describe('MEU-106 DUPLICATE entry', () => {
  it('AC-106.22 the registry holds capture:duplicate after capture:tool_crop, chord-only, outside the palette', () => {
    const commands = listCommands()
    const ids = commands.map((command) => command.id)
    const crop = ids.indexOf('capture:tool_crop')
    expect(crop).toBeGreaterThanOrEqual(0)
    expect(ids[crop + 1]).toBe('capture:duplicate')
    const entry = commands.find((command) => command.id === 'capture:duplicate')
    expect(entry).toMatchObject({
      label: 'Duplicate mark',
      shortcut: 'Ctrl+D',
      category: 'capture',
      page: '/capture',
      stateful: true,
      palette: false,
    })
    expect(RESERVED_CHORDS.has(normalizeChord('Ctrl+D') ?? 'Ctrl+D')).toBe(false)
    expect(() => buildShortcutMap(commands)).not.toThrow()
    const allOn = Object.fromEntries(ids.map((id) => [id, true]))
    expect(paletteCommands(commands, '/capture', allOn).map((command) => command.id)).not.toContain('capture:duplicate')
  })
})

/** MARK_LABELS: Green counts each kind through the list (Session 72 departure: a third argument). */
const labelOf = markLabel as unknown as (mark: Annotation, index: number, marks: readonly Annotation[]) => string

describe('MEU-106 MARK_LABELS', () => {
  it('AC-106.26 an arrow, a line, a box and an ellipse read Arrow 1, Line 1, Box 1 and Ellipse 1', () => {
    const marks: Annotation[] = [
      { type: 'arrow', from: [1, 1], to: [20, 20], color: '#FF0000', stroke_width: 3 },
      { type: 'arrow', from: [1, 30], to: [20, 40], color: '#FF0000', stroke_width: 3, head: 'none' },
      { type: 'rect', x: 30, y: 1, width: 10, height: 10, color: '#FF0000', stroke_width: 3 },
      { type: 'rect', x: 30, y: 30, width: 10, height: 10, color: '#FF0000', stroke_width: 3, shape: 'ellipse' },
    ]
    expect(marks.map((mark, index) => labelOf(mark, index, marks))).toEqual(['Arrow 1', 'Line 1', 'Box 1', 'Ellipse 1'])
  })
})

describe('MEU-107 STEP_PREVIEW layout', () => {
  it('AC-107.11 the layout gives radius size / 2 and the text colour follows luminance', () => {
    expect(step.stepBadgeLayout(40, 50, 1, 32).radius).toBe(16)
    expect(step.stepBadgeLayout(40, 50, 7, 13).radius).toBe(6.5)
    const colours: Record<string, string> = {
      '#E0AF68': '#000000',
      '#FFFFFF': '#000000',
      '#FFFF00': '#000000',
      '#00FF00': '#000000',
      '#FF0000': '#000000',
      '#000000': '#FFFFFF',
      '#1A1B26': '#FFFFFF',
      '#0000FF': '#FFFFFF',
    }
    for (const [colour, text] of Object.entries(colours)) {
      expect(step.stepTextColor(colour), colour).toBe(text)
    }
  })
})

describe('MEU-107 parity', () => {
  it('AC-107.12 stepBadgeLayout equals the fixture steps for the 12 pairs', () => {
    expect(GEOMETRY.steps).toHaveLength(12)
    for (const entry of GEOMETRY.steps) {
      const where = `${entry.size}/${entry.number}`
      expect(step.stepBadgeLayout(entry.x, entry.y, entry.number, entry.size), where).toEqual({
        radius: entry.radius,
        fontPx: entry.font_px,
        baseline: entry.baseline,
      })
    }
  })
})

describe('MEU-107 MARK_LABELS', () => {
  it('AC-107.19 steps numbered 1 and 4 read Step 1 and Step 4', () => {
    const marks: Annotation[] = [
      { type: 'step', x: 10, y: 10, number: 1, color: '#E0AF68', size: 32 },
      { type: 'step', x: 60, y: 10, number: 4, color: '#E0AF68', size: 32 },
    ]
    expect(marks.map((mark, index) => labelOf(mark, index, marks))).toEqual(['Step 1', 'Step 4'])
  })
})
