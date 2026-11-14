export const SVG_TEXT_ANCHOR = 'start'
export const SVG_DOMINANT_BASELINE = 'alphabetic'
export const SVG_TEXT_FONT_FAMILY = '"Segoe UI", Arial, sans-serif'

import { SEGOE_LA_BASE_SIZE, SEGOE_LA_GLYPHS, SEGOE_UI_ASCENDER, SEGOE_UI_UNITS_PER_EM } from './capture-segoe-metrics'

/**
 * SEGOE_ASCENT (MEU-82, D-10): FreeType's 26.6 ascent, which Pillow's `la` anchor uses.
 * FT_MulFix of the ascender by the y scale `size*64*65536/UNITS_PER_EM`, then ceil to whole px.
 * Integer math stays exact here: 2210 * 500 * 2048 is far below 2^53.
 */
export function segoeAscentPx(fontSize: number): number {
  const size = Math.max(1, fontSize)
  const yScale = (size * 64 * 0x10000) / SEGOE_UI_UNITS_PER_EM
  const ascent26_6 = Math.floor((SEGOE_UI_ASCENDER * yScale + 0x8000) / 0x10000)
  return Math.ceil(ascent26_6 / 64)
}

/** TEXT_ANCHOR: the alphabetic baseline sits `ascent` below the mark's `la` top-left `y`. */
export function svgTextBaselineY(input: { y: number; font_size: number }): number {
  return input.y + segoeAscentPx(input.font_size)
}

/** TEXT_LINE_GAP_PX (MEU-102): px between lines, the bake's `TEXT_LINE_GAP`. */
export const TEXT_LINE_GAP_PX = 4

/** TEXT_LINE_PITCH (MEU-102): one line's top to the next, Pillow's multiline pitch. */
export function segoeLinePitchPx(fontSize: number): number {
  return segoeAscentPx(fontSize) + TEXT_LINE_GAP_PX
}

/** TEXT_LINE_PITCH: the lines of a text mark; a stored text holds LF only, and lines never wrap. */
export function textLines(text: string): string[] {
  return text.split('\n')
}

export type TextMetricsInput = {
  x: number
  y: number
  text: string
  font_size: number
}

export type TextBackgroundBox = {
  x: number
  y: number
  width: number
  height: number
}

const FALLBACK_GLYPH = { l: 0, t: 7, r: 8, b: 18, adv: 8 }

/**
 * TEXT_PLATE_LINES (MEU-102): the union of each line's unrounded glyph extents, line `i` at
 * `y + i * pitch`; an empty line counts as the point `(x, y_i)`. The union is rounded and clamped
 * once. A text with no `\n` keeps the one-line box (an empty text measures one space).
 */
export function textBackgroundBox(input: TextMetricsInput): TextBackgroundBox {
  const size = Math.max(1, input.font_size)
  const scale = size / SEGOE_LA_BASE_SIZE
  const multiline = input.text.includes('\n')
  const lines = multiline ? textLines(input.text) : [input.text.length > 0 ? input.text : ' ']
  const pitch = segoeLinePitchPx(size)
  let left = Number.POSITIVE_INFINITY
  let top = Number.POSITIVE_INFINITY
  let right = Number.NEGATIVE_INFINITY
  let bottom = Number.NEGATIVE_INFINITY
  lines.forEach((line, index) => {
    const lineTop = input.y + index * pitch
    if (line.length === 0) {
      left = Math.min(left, input.x)
      top = Math.min(top, lineTop)
      right = Math.max(right, input.x)
      bottom = Math.max(bottom, lineTop)
      return
    }
    let cursor = input.x
    for (const ch of line) {
      const glyph = SEGOE_LA_GLYPHS[ch] ?? FALLBACK_GLYPH
      left = Math.min(left, cursor + glyph.l * scale)
      top = Math.min(top, lineTop + glyph.t * scale)
      right = Math.max(right, cursor + glyph.r * scale)
      bottom = Math.max(bottom, lineTop + glyph.b * scale)
      cursor += glyph.adv * scale
    }
  })
  return {
    x: Math.round(left),
    y: Math.round(top),
    width: Math.max(1, Math.round(right) - Math.round(left)),
    height: Math.max(1, Math.round(bottom) - Math.round(top)),
  }
}
