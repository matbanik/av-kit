import type { Annotation } from './capture-annotate'
import { displayHex } from './capture-color'

/** STEP_PREVIEW (MEU-107, D-773): a badge's radius, its number's font size and the text baseline. */
export type StepLayout = { radius: number; fontPx: number; baseline: number }

/** The largest step number (STEP_TYPE, D-772); STEP_PLACE and DUPLICATE stop past it. */
export const STEP_NUMBER_MAX = 999

/**
 * STEP_PREVIEW (MEU-107, D-773): the TS mirror of the adapter's `step_badge_layout`. One or two
 * digits use half the badge as the font and three use four tenths; the baseline sits 0.355 font
 * px below the centre, in integer arithmetic so the preview and the bake agree exactly.
 */
export function stepBadgeLayout(_x: number, y: number, n: number, size: number): StepLayout {
  const fontPx = n < 100 ? Math.floor((size + 1) / 2) : Math.floor((size * 4 + 5) / 10)
  return { radius: size / 2, fontPx, baseline: y + Math.floor((fontPx * 355 + 500) / 1000) }
}

function linearChannel(value: number): number {
  const channel = value / 255
  return channel <= 0.04045 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4
}

/**
 * STEP_PREVIEW (MEU-107, D-773): the TS mirror of `step_text_color`, black when the colour's WCAG
 * relative luminance is above 0.179, else white.
 */
export function stepTextColor(color: string): '#000000' | '#FFFFFF' {
  const hex = displayHex(color)
  const channel = (offset: number): number => linearChannel(Number.parseInt(hex.slice(offset, offset + 2), 16))
  const luminance = 0.2126 * channel(1) + 0.7152 * channel(3) + 0.0722 * channel(5)
  return luminance > 0.179 ? '#000000' : '#FFFFFF'
}

/** STEP_PLACE (MEU-107, D-774): one more than the largest step number in the list, or 1. */
export function nextStepNumber(marks: readonly Annotation[]): number {
  let largest = 0
  for (const mark of marks) {
    if (mark.type === 'step' && mark.number > largest) {
      largest = mark.number
    }
  }
  return largest + 1
}
