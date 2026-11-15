/** @vitest-environment jsdom */

import { describe, expect, it } from 'vitest'

import type { Annotation, RedactMode } from '../../src/renderer/src/features/capture/capture-annotate'
import { CAPTURE_HELP_SECTIONS } from '../../src/renderer/src/features/capture/capture-help-content'
import * as store from '../../src/renderer/src/features/capture/capture-style-store'
import { optionGroups } from '../../src/renderer/src/features/capture/capture-toolbar'
import * as style from '../../src/renderer/src/features/capture/capture-tool-style'
import type { StyleTool, ToolStyle, ToolStyles } from '../../src/renderer/src/features/capture/capture-tool-style'
import type { CaptureScrubFieldProps } from '../../src/renderer/src/features/capture/CaptureScrubField'
import type { CaptureTool } from '../../src/renderer/src/features/capture/CaptureViewport'
import * as hook from '../../src/renderer/src/features/capture/useCaptureToolStyles'
import type { CapturePut } from '../../src/renderer/src/features/settings/settings-schemas'
import * as ids from '../e2e/test-ids'

// Session 71 (MEU-105): the style model, the read-back, SELECT_NO_STYLE's table half and STYLE_HELP.

const STYLE_TOOLS: StyleTool[] = ['arrow', 'box', 'highlight', 'text', 'pixelate', 'step']
const TOOLS: CaptureTool[] = ['select', 'arrow', 'box', 'highlight', 'text', 'step', 'redact', 'eraser', 'crop']
const MODES: RedactMode[] = ['solid', 'pixelate']

const DEFAULTS: ToolStyles = {
  arrow: { color: '#E0AF68', stroke: 3 },
  box: { color: '#E0AF68', stroke: 3 },
  highlight: { color: '#E0AF68' },
  text: { color: '#E0AF68', fontSize: 16, textBg: '' },
  pixelate: { blockSize: 10 },
  step: { color: '#E0AF68', stepSize: 32 },
}

const LEAVES = {
  arrow: { color: 'arrow_color', stroke: 'arrow_stroke' },
  box: { color: 'box_color', stroke: 'box_stroke' },
  highlight: { color: 'highlight_color' },
  text: { color: 'text_color', fontSize: 'text_font_size', textBg: 'text_bg_color' },
  pixelate: { blockSize: 'pixelate_block_size' },
  step: { color: 'step_color', stepSize: 'step_size' },
}

/** The STYLE_MODEL table for armed tools: [tool, mode, style tool]. */
const FOR_TOOL: Array<[CaptureTool, RedactMode, StyleTool | null]> = TOOLS.flatMap((tool) =>
  MODES.map((mode): [CaptureTool, RedactMode, StyleTool | null] => {
    // Session 72 row 3 (STEP_STYLE, D-775): step styles itself.
    if (tool === 'arrow' || tool === 'box' || tool === 'highlight' || tool === 'text' || tool === 'step') {
      return [tool, mode, tool]
    }
    if (tool === 'redact') {
      return [tool, mode, mode === 'pixelate' ? 'pixelate' : null]
    }
    return [tool, mode, null]
  }),
)

const MARKS: Record<Annotation['type'], Annotation> = {
  arrow: { type: 'arrow', color: '#E0AF68', stroke_width: 3, from: [1, 1], to: [5, 5] },
  rect: { type: 'rect', x: 1, y: 1, width: 4, height: 4, color: '#E0AF68', stroke_width: 3 },
  highlight: { type: 'highlight', x: 1, y: 1, width: 4, height: 4, color: '#E0AF68', opacity: 0.35 },
  text: { type: 'text', x: 1, y: 1, text: 'Hi', color: '#E0AF68', font_size: 16, bg_color: null },
  pixelate: { type: 'pixelate', x: 1, y: 1, width: 4, height: 4, block_size: 10 },
  eraser: { type: 'eraser', x: 1, y: 1, width: 4, height: 4 },
  redact: { type: 'redact', x: 1, y: 1, width: 4, height: 4, color: '#000000' },
  step: { type: 'step', x: 1, y: 1, number: 1, color: '#E0AF68', size: 32 },
}

const OF_MARK: Record<Annotation['type'], StyleTool | null> = {
  arrow: 'arrow',
  rect: 'box',
  highlight: 'highlight',
  text: 'text',
  pixelate: 'pixelate',
  eraser: null,
  redact: null,
  step: 'step',
}

/** Every leaf valid and none at its default, so a fallback shows as exactly one changed field. */
const FULL: Record<string, unknown> = {
  inbox_dir: 'C:/Pictures/av-kit',
  hotkey: 'F2',
  copy_to_clipboard: false,
  close_to_tray: true,
  flatten_backup: true,
  backup_dir: '',
  annotated_format: 'png',
  arrow_color: '#123456',
  arrow_stroke: 7,
  box_color: '#234567',
  box_stroke: 9,
  highlight_color: '#345678',
  text_color: '#456789',
  text_font_size: 24,
  text_bg_color: '#56789A',
  pixelate_block_size: 20,
  step_color: '#6789AB',
  step_size: 48,
}

const FULL_STYLES: ToolStyles = {
  arrow: { color: '#123456', stroke: 7 },
  box: { color: '#234567', stroke: 9 },
  highlight: { color: '#345678' },
  text: { color: '#456789', fontSize: 24, textBg: '#56789A' },
  pixelate: { blockSize: 20 },
  step: { color: '#6789AB', stepSize: 48 },
}

/** FULL_STYLES with one field replaced. */
function withField(tool: StyleTool, field: keyof ToolStyle, value: string | number): ToolStyles {
  return { ...FULL_STYLES, [tool]: { ...FULL_STYLES[tool], [field]: value } }
}

const STYLE_HELP_SENTENCE =
  "A swatch applies when you pick it, and a typed hex colour applies on Enter. With a mark selected, a style control changes only that mark; with none selected, it sets the current tool's own colour and size, which Capture remembers."

describe('MEU-105 capture tool style model', () => {
  it('AC-105.1 the TS names: the style types, maps and functions, the store, the hook, the scrub min and the scrub id', () => {
    const forTool: (tool: CaptureTool, mode: RedactMode) => StyleTool | null = style.styleToolFor
    const ofMark: (mark: Annotation) => StyleTool | null = style.styleToolOfMark
    const read: (data: unknown) => ToolStyles = style.readToolStyles
    const fetchSettings: () => Promise<CapturePut> = store.fetchCaptureSettings
    const reset: () => void = store.resetCaptureStyleStore
    const useStyles: () => {
      styles: ToolStyles
      saveToolStyle: (tool: StyleTool, patch: ToolStyle) => void
    } = hook.useCaptureToolStyles
    for (const [name, fn, arity] of [
      ['styleToolFor', forTool, 2],
      ['styleToolOfMark', ofMark, 1],
      ['readToolStyles', read, 1],
      ['fetchCaptureSettings', fetchSettings, 0],
      ['resetCaptureStyleStore', reset, 0],
      ['useCaptureToolStyles', useStyles, 0],
    ] as const) {
      expect(typeof fn, name).toBe('function')
      expect(fn.length, name).toBe(arity)
    }
    const min: CaptureScrubFieldProps['min'] = 2
    const absent: CaptureScrubFieldProps['min'] = undefined
    expect(min).toBe(2)
    expect(absent).toBeUndefined()
    expect(ids.CAPTURE_BLOCK_SIZE_SCRUB).toBe('capture-block-size-scrub')
    const tool: StyleTool = 'pixelate'
    const fields: Required<ToolStyle> = {
      color: '#E0AF68',
      stroke: 3,
      fontSize: 16,
      textBg: '',
      blockSize: 10,
      stepSize: 32,
    }
    expect(tool).toBe('pixelate')
    expect(Object.keys(fields).sort()).toEqual(['blockSize', 'color', 'fontSize', 'stepSize', 'stroke', 'textBg'])
    expect(Object.keys(style.TOOL_STYLE_DEFAULTS).sort()).toEqual([...STYLE_TOOLS].sort())
    expect(Object.keys(style.TOOL_STYLE_LEAVES).sort()).toEqual([...STYLE_TOOLS].sort())
    expect(style.TOOL_STYLE_DEFAULTS).toEqual(DEFAULTS)
    expect(style.TOOL_STYLE_LEAVES).toEqual(LEAVES)
  })

  it('AC-105.6 styleToolFor and styleToolOfMark give the STYLE_MODEL table for every tool, mode and mark type', () => {
    expect(typeof style.styleToolFor).toBe('function')
    expect(typeof style.styleToolOfMark).toBe('function')
    expect(FOR_TOOL).toHaveLength(TOOLS.length * MODES.length)
    for (const [tool, mode, want] of FOR_TOOL) {
      expect(style.styleToolFor(tool, mode), `${tool} × ${mode}`).toBe(want)
    }
    expect(Object.keys(MARKS).sort()).toEqual(Object.keys(OF_MARK).sort())
    for (const [type, mark] of Object.entries(MARKS)) {
      expect(style.styleToolOfMark(mark), type).toBe(OF_MARK[type as Annotation['type']])
    }
    for (const tool of STYLE_TOOLS) {
      expect(style.TOOL_STYLE_DEFAULTS[tool], `default ${tool}`).toBeDefined()
      expect(style.TOOL_STYLE_LEAVES[tool], `leaves ${tool}`).toBeDefined()
    }
  })

  it('AC-105.6 negative: Redact Solid has no style tool, and neither does a redact or eraser mark', () => {
    expect(typeof style.styleToolFor).toBe('function')
    expect(style.styleToolFor('redact', 'pixelate')).toBe('pixelate')
    expect(style.styleToolFor('redact', 'solid')).toBeNull()
    expect(style.styleToolOfMark(MARKS.redact)).toBeNull()
    expect(style.styleToolOfMark(MARKS.eraser)).toBeNull()
  })

  it('AC-105.7 readToolStyles keeps each valid leaf and replaces only the bad one with its default', () => {
    expect(typeof style.readToolStyles).toBe('function')
    expect(style.readToolStyles(FULL)).toEqual(FULL_STYLES)
    const cases: Array<[string, Record<string, unknown>, ToolStyles]> = [
      ['a missing leaf', { box_color: undefined }, withField('box', 'color', '#E0AF68')],
      ['a number for a colour', { arrow_color: 5 }, withField('arrow', 'color', '#E0AF68')],
      ['five hex digits', { arrow_color: '#12ABC' }, withField('arrow', 'color', '#E0AF68')],
      ['an empty arrow_color', { arrow_color: '' }, withField('arrow', 'color', '#E0AF68')],
      ['a lone surrogate', { arrow_color: '#12AB\uD800' }, withField('arrow', 'color', '#E0AF68')],
      ['a control character', { arrow_color: '#12AB\u0007D' }, withField('arrow', 'color', '#E0AF68')],
      ['a float stroke', { arrow_stroke: 2.5 }, withField('arrow', 'stroke', 3)],
      ['a zero stroke', { arrow_stroke: 0 }, withField('arrow', 'stroke', 3)],
      ['a stroke of 101', { arrow_stroke: 101 }, withField('arrow', 'stroke', 3)],
      ['a string stroke', { arrow_stroke: '7' }, withField('arrow', 'stroke', 3)],
      ['a block size of 1', { pixelate_block_size: 1 }, withField('pixelate', 'blockSize', 10)],
      ['a font size of 401', { text_font_size: 401 }, withField('text', 'fontSize', 16)],
      ['a bad text_bg_color', { text_bg_color: 'red' }, withField('text', 'textBg', '')],
      ['an empty text_bg_color is kept', { text_bg_color: '' }, withField('text', 'textBg', '')],
      ['a lowercase colour is kept as read', { highlight_color: '#abcdef' }, withField('highlight', 'color', '#abcdef')],
    ]
    for (const [label, patch, want] of cases) {
      const data: Record<string, unknown> = { ...FULL, ...patch }
      for (const [key, value] of Object.entries(patch)) {
        if (value === undefined) {
          delete data[key]
        }
      }
      expect(style.readToolStyles(data), label).toEqual(want)
    }
    expect(style.readToolStyles(undefined)).toEqual(DEFAULTS)
    expect(style.readToolStyles(null)).toEqual(DEFAULTS)
  })

  it('AC-105.7 negative: a lone surrogate in one colour keeps every other leaf', () => {
    expect(typeof style.readToolStyles).toBe('function')
    const got = style.readToolStyles({ ...FULL, text_color: '#45\uD8006789' })
    expect(got.text.color).toBe('#E0AF68')
    expect(got.text.fontSize).toBe(24)
    expect(got.arrow).toEqual(FULL_STYLES.arrow)
    expect(got.box).toEqual(FULL_STYLES.box)
    expect(got.pixelate).toEqual(FULL_STYLES.pixelate)
  })

  it('AC-105.19 optionGroups gives no group for Select with nothing selected, in both modes', () => {
    expect(typeof optionGroups).toBe('function')
    for (const mode of MODES) {
      expect([...optionGroups('select', null, mode)], mode).toEqual([])
    }
  })

  it('AC-105.19 negative: a selected arrow under Select still shows Color and Stroke', () => {
    expect([...optionGroups('select', MARKS.arrow)]).toEqual(['color', 'stroke'])
  })

  it('AC-105.24 the Annotation tools body names the commit rules and Block size, and drops Apply', () => {
    const section = CAPTURE_HELP_SECTIONS.find((row) => row.id === 'four-tools')
    expect(section).toBeDefined()
    const body = section?.body ?? ''
    expect(body).toContain(STYLE_HELP_SENTENCE)
    expect(body).toContain('Drag the Stroke, Size or Block size label')
    expect(body).not.toContain('Apply commits color')
  })
})
