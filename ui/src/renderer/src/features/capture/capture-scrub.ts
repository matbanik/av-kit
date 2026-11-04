/**
 * SCRUB_MATH (MEU-85): the Stroke and Size fields change by label drag, mouse wheel and Up/Down.
 * A drag gives one step per SCRUB_PX_PER_STEP pixels (SCRUB_FINE_PX_PER_STEP with Alt); Shift
 * multiplies each step by SCRUB_COARSE_FACTOR.
 */
export const SCRUB_MIN = 1
export const STROKE_SCRUB_MAX = 100
export const FONT_SCRUB_MAX = 400
export const SCRUB_PX_PER_STEP = 2
export const SCRUB_FINE_PX_PER_STEP = 8
export const SCRUB_COARSE_FACTOR = 10

/** Whole steps in `carry + dx` pixels, truncated toward zero; the remainder carries to the next move. */
export function scrubSteps(carry: number, dx: number, fine: boolean): { steps: number; carry: number } {
  const perStep = fine ? SCRUB_FINE_PX_PER_STEP : SCRUB_PX_PER_STEP
  const total = carry + dx
  const steps = Math.trunc(total / perStep)
  // `+ 0` turns a -0 into 0.
  return { steps: steps + 0, carry: total - steps * perStep + 0 }
}

/** `value + delta` clamped to [min, max]; a value already past a bound never moves further against the gesture. */
export function clampScrub(value: number, delta: number, min: number, max: number): number {
  if (delta > 0) {
    return value >= max ? value : Math.min(value + delta, max)
  }
  if (delta < 0) {
    return value <= min ? value : Math.max(value + delta, min)
  }
  return value
}

/** A whole number above zero, or null for anything else (moved from CapturePage, behaviour unchanged). */
export function parsePositiveInt(raw: string): number | null {
  const trimmed = raw.trim()
  if (!/^\d+$/.test(trimmed)) {
    return null
  }
  const parsed = Number.parseInt(trimmed, 10)
  return parsed > 0 ? parsed : null
}
