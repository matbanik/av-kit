export const SVG_TEXT_ANCHOR = 'start'
export const SVG_DOMINANT_BASELINE = 'alphabetic'
export const SVG_TEXT_FONT_FAMILY = '"Segoe UI", Arial, sans-serif'

import { SEGOE_UI_ASCENDER, SEGOE_UI_GLYPH_UNITS, SEGOE_UI_KERN_UNITS, SEGOE_UI_UNITS_PER_EM } from './capture-segoe-metrics'

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

/** The unknown-glyph box in font units: the old 16 px fallback (l 0, t 7, r 8, b 18, adv 8 at `la`) at 128 units a px. */
const FALLBACK_GLYPH_UNITS = { l: 0, t: -1408, r: 1024, b: 0, adv: 1024 }

/** FreeType's FT_MulFix: (a * b + 0x8000) / 0x10000, rounded half away from zero; exact below 2^53. */
function mulFix(a: number, b: number): number {
  const magnitude = Math.floor((Math.abs(a) * Math.abs(b) + 0x8000) / 0x10000)
  return a < 0 !== b < 0 ? -magnitude : magnitude
}

/** FreeType's FT_PIX_ROUND of a 26.6 value, in whole px: (v + 32) >> 6, written without a 32-bit shift. */
function pixRound(value26: number): number {
  return Math.floor((value26 + 32) / 64)
}

/** The bake's kerning step for a pair (Pillow's basic layout over FT_Get_Kerning): the pair's font units by FT_MulFix, shrunk below 25 px as FreeType's default kerning does, rounded to whole px. */
function kernStep(pair: string, size: number, scale: number): number {
  const units = SEGOE_UI_KERN_UNITS[pair]
  if (!units) return 0
  let kern26 = mulFix(units, scale)
  if (size < 25) {
    const magnitude = Math.floor((Math.abs(kern26) * size + 12) / 25)
    kern26 = kern26 < 0 ? -magnitude : magnitude
  }
  return pixRound(kern26)
}

/** TEXT_PLATE_UNITS (MEU-161, D-1243) and PREVIEW_FOLLOWS_BAKE (D-1242): the plate the bake paints, from each glyph's font units scaled by FT_MulFix and rounded per extent and advance as FreeType does, the pen moved by each pair's kerning step, line `i` at `y + i * pitch` with its baseline the ascent below, an empty line the point `(x, y_i)`; Pillow's textbbox is inclusive, so the box is `r - l + 1` by `b - t + 1`. */
export function textBackgroundBox(input: TextMetricsInput): TextBackgroundBox {
  const size = Math.max(1, input.font_size)
  const scale = (size * 64 * 0x10000) / SEGOE_UI_UNITS_PER_EM
  const ascent = segoeAscentPx(size)
  const pitch = segoeLinePitchPx(size)
  const multiline = input.text.includes('\n')
  const lines = multiline ? textLines(input.text) : [input.text.length > 0 ? input.text : ' ']
  // left, top, right, bottom: the inclusive pixel extents, as Pillow's textbbox reports them
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
    const baseline = lineTop + ascent
    let pen26 = 0
    let previous = ''
    for (const ch of line) {
      const known = SEGOE_UI_GLYPH_UNITS[ch]
      if (previous && known) pen26 += kernStep(previous + ch, size, scale)
      const glyph = known ?? FALLBACK_GLYPH_UNITS
      const origin = input.x + pixRound(pen26)
      left = Math.min(left, origin + pixRound(mulFix(glyph.l, scale)))
      top = Math.min(top, baseline + pixRound(mulFix(glyph.t, scale)))
      right = Math.max(right, origin + pixRound(mulFix(glyph.r, scale)))
      bottom = Math.max(bottom, baseline + pixRound(mulFix(glyph.b, scale)))
      pen26 += pixRound(mulFix(glyph.adv, scale)) * 64
      previous = known ? ch : ''
    }
  })
  return { x: left, y: top, width: Math.max(1, right - left + 1), height: Math.max(1, bottom - top + 1) }
}
