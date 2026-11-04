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

export function textBackgroundBox(input: TextMetricsInput): TextBackgroundBox {
  const size = Math.max(1, input.font_size)
  const scale = size / SEGOE_LA_BASE_SIZE
  const glyphs = input.text.length > 0 ? [...input.text] : [' ']
  let left = Number.POSITIVE_INFINITY
  let top = Number.POSITIVE_INFINITY
  let right = Number.NEGATIVE_INFINITY
  let bottom = Number.NEGATIVE_INFINITY
  let cursor = input.x
  for (const ch of glyphs) {
    const glyph = SEGOE_LA_GLYPHS[ch] ?? FALLBACK_GLYPH
    left = Math.min(left, cursor + glyph.l * scale)
    top = Math.min(top, input.y + glyph.t * scale)
    right = Math.max(right, cursor + glyph.r * scale)
    bottom = Math.max(bottom, input.y + glyph.b * scale)
    cursor += glyph.adv * scale
  }
  return {
    x: Math.round(left),
    y: Math.round(top),
    width: Math.max(1, Math.round(right) - Math.round(left)),
    height: Math.max(1, Math.round(bottom) - Math.round(top)),
  }
}
