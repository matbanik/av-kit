import type { Annotation, RedactMode } from './capture-annotate'
import type { CaptureTool } from './CaptureViewport'

/** STYLE_MODEL (MEU-105, D-715): the tools that keep their own persisted style. */
export type StyleTool = 'arrow' | 'box' | 'highlight' | 'text' | 'pixelate' | 'step'

/** One tool's style; a field the tool has no control for is absent. */
export type ToolStyle = {
  color?: string
  stroke?: number
  fontSize?: number
  textBg?: string
  blockSize?: number
  stepSize?: number
}

export type ToolStyles = Readonly<Record<StyleTool, ToolStyle>>

/** The defaults, which match the `capture` rows of SETTINGS_KEY_TABLE. */
export const TOOL_STYLE_DEFAULTS: ToolStyles = {
  arrow: { color: '#E0AF68', stroke: 3 },
  box: { color: '#E0AF68', stroke: 3 },
  highlight: { color: '#E0AF68' },
  text: { color: '#E0AF68', fontSize: 16, textBg: '' },
  pixelate: { blockSize: 10 },
  step: { color: '#E0AF68', stepSize: 32 },
}

/** The `capture` settings leaf that stores each field of each tool's style. */
export const TOOL_STYLE_LEAVES: Readonly<Record<StyleTool, Readonly<Partial<Record<keyof ToolStyle, string>>>>> = {
  arrow: { color: 'arrow_color', stroke: 'arrow_stroke' },
  box: { color: 'box_color', stroke: 'box_stroke' },
  highlight: { color: 'highlight_color' },
  text: { color: 'text_color', fontSize: 'text_font_size', textBg: 'text_bg_color' },
  pixelate: { blockSize: 'pixelate_block_size' },
  step: { color: 'step_color', stepSize: 'step_size' },
}

/** A colour leaf as stored: `#` and six hex digits, nothing more. */
const COLOR_LEAF = /^#[0-9A-Fa-f]{6}$/

/** The integer range of each number field, as the `capture` rows of SETTINGS_KEY_TABLE hold it. */
const NUMBER_RANGE: Readonly<Record<'stroke' | 'fontSize' | 'blockSize' | 'stepSize', readonly [number, number]>> = {
  stroke: [1, 100],
  fontSize: [1, 400],
  blockSize: [2, 100],
  stepSize: [12, 200],
}

function unreachable(value: never): never {
  throw new Error(`Unhandled value: ${String(value)}`)
}

/** The style tool an armed tool draws with, or null when it has none (STYLE_MODEL). */
export function styleToolFor(tool: CaptureTool, mode: RedactMode): StyleTool | null {
  switch (tool) {
    case 'arrow':
    case 'box':
    case 'highlight':
    case 'text':
    case 'step':
      return tool
    case 'redact':
      return mode === 'pixelate' ? 'pixelate' : null
    case 'select':
    case 'eraser':
    case 'crop':
      return null
    default:
      return unreachable(tool)
  }
}

/** The style tool a mark belongs to, or null when it has none (STYLE_MODEL). */
export function styleToolOfMark(mark: Annotation): StyleTool | null {
  switch (mark.type) {
    case 'arrow':
      return 'arrow'
    case 'rect':
      return 'box'
    case 'highlight':
    case 'text':
    case 'pixelate':
      return mark.type
    case 'redact':
    case 'eraser':
      return null
    case 'step':
      // STEP_STYLE (MEU-107, D-775): a step keeps its own colour and size.
      return 'step'
    default:
      return unreachable(mark)
  }
}

function readField(field: keyof ToolStyle, raw: unknown, fallback: string | number): string | number {
  if (field === 'color' || field === 'textBg') {
    if (typeof raw !== 'string') {
      return fallback
    }
    if (field === 'textBg' && raw === '') {
      return raw
    }
    return COLOR_LEAF.test(raw) ? raw : fallback
  }
  const [min, max] = NUMBER_RANGE[field]
  return typeof raw === 'number' && Number.isInteger(raw) && raw >= min && raw <= max ? raw : fallback
}

/** Each tool's style from the `capture` settings data, leaf by leaf; a bad leaf gives its default alone. */
export function readToolStyles(data: unknown): ToolStyles {
  const source = typeof data === 'object' && data !== null ? (data as Record<string, unknown>) : {}
  const read = (tool: StyleTool): ToolStyle => {
    const defaults = TOOL_STYLE_DEFAULTS[tool]
    const leaves = TOOL_STYLE_LEAVES[tool]
    const out: Record<string, string | number> = {}
    for (const field of Object.keys(defaults) as Array<keyof ToolStyle>) {
      const fallback = defaults[field]
      const leaf = leaves[field]
      if (fallback === undefined || leaf === undefined) {
        continue
      }
      out[field] = readField(field, source[leaf], fallback)
    }
    return out as ToolStyle
  }
  return {
    arrow: read('arrow'),
    box: read('box'),
    highlight: read('highlight'),
    text: read('text'),
    pixelate: read('pixelate'),
    step: read('step'),
  }
}
