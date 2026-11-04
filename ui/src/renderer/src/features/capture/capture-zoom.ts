import { viewTransform, type ViewState } from './capture-fit-map'

/** ZOOM_STATE (Session 29 plan): view-only state owned by the viewport, never persisted. */
export type ZoomState = ViewState

export type ZoomDirection = 'in' | 'out'

/** ZOOM_PAN_HINT: the zoom readout's tooltip (plan D-21). */
export const ZOOM_PAN_HINT = 'Wheel or Ctrl+= / Ctrl+- to zoom · Ctrl+0 to fit · Space+drag or middle-drag to pan'

/**
 * ZOOM_LADDER: Chromium's preset browser zoom factors (kPresetBrowserZoomFactorsArray,
 * third_party/blink/common/page/page_zoom.cc), 25 % to 500 %. Fit is a separate level (plan D-14).
 */
export const ZOOM_LADDER: readonly number[] = [
  0.25, 1 / 3, 0.5, 2 / 3, 0.75, 0.8, 0.9, 1, 1.1, 1.25, 1.5, 1.75, 2, 2.5, 3, 4, 5,
]

const LADDER_EPSILON = 1e-9

/**
 * ZOOM_STEP: the next ladder level above or below the current scale (the fit scale while at Fit).
 * Returns null past either end, or when the fit scale is not a positive finite number (fail closed).
 */
export function zoomStep(state: ZoomState, dir: ZoomDirection, fitScale: number): number | null {
  if (!Number.isFinite(fitScale) || fitScale <= 0) {
    return null
  }
  const current = state.kind === 'fit' ? fitScale : state.scale
  if (!Number.isFinite(current) || current <= 0) {
    return null
  }
  if (dir === 'in') {
    return ZOOM_LADDER.find((level) => level > current + LADDER_EPSILON) ?? null
  }
  for (let i = ZOOM_LADDER.length - 1; i >= 0; i -= 1) {
    const level = ZOOM_LADDER[i] as number
    if (level < current - LADDER_EPSILON) {
      return level
    }
  }
  return null
}

/**
 * ZOOM_ABOUT: zoom to `nextScale` keeping the image point under `cursor` (container CSS px) fixed, then
 * centre or clamp each axis through VIEW_TRANSFORM. An invalid geometry leaves the state unchanged.
 */
export function zoomAbout(
  state: ZoomState,
  cursor: { x: number; y: number },
  nextScale: number,
  container: { w: number; h: number },
  image: { w: number; h: number },
): ZoomState {
  const current = viewTransform(container, image, state)
  if (current === null || !Number.isFinite(cursor.x) || !Number.isFinite(cursor.y)) {
    return state
  }
  const ix = (cursor.x - current.ox) / current.s
  const iy = (cursor.y - current.oy) / current.s
  const placed = viewTransform(container, image, {
    kind: 'scale',
    scale: nextScale,
    ox: cursor.x - ix * nextScale,
    oy: cursor.y - iy * nextScale,
  })
  if (placed === null) {
    return state
  }
  return { kind: 'scale', scale: placed.s, ox: placed.ox, oy: placed.oy }
}

/** Pixel-mode wheel distance for one zoom step (plan D-18). */
export const WHEEL_STEP_PX = 100
/** Idle gap that resets the pixel-mode accumulator. */
export const WHEEL_RESET_MS = 250

export type WheelAccumulator = { readonly sum: number; readonly lastAt: number | null }

/** An empty accumulator. */
export const WHEEL_IDLE: WheelAccumulator = { sum: 0, lastAt: null }

/**
 * WHEEL_STEP: zoom steps for one wheel event (positive = in). Line and page deltas give one step per
 * event; pixel deltas accumulate to WHEEL_STEP_PX, resetting on a sign change or after WHEEL_RESET_MS idle.
 * A zero, non-finite or unknown-mode delta gives no step.
 */
export function wheelSteps(
  acc: WheelAccumulator,
  event: { deltaMode: number; deltaY: number; timeStamp: number },
): { steps: number; acc: WheelAccumulator } {
  if (!Number.isFinite(event.deltaY) || event.deltaY === 0) {
    return { steps: 0, acc }
  }
  if (event.deltaMode === 1 || event.deltaMode === 2) {
    return { steps: event.deltaY < 0 ? 1 : -1, acc: WHEEL_IDLE }
  }
  if (event.deltaMode !== 0) {
    return { steps: 0, acc }
  }
  const stale = acc.lastAt === null || event.timeStamp - acc.lastAt > WHEEL_RESET_MS
  const flipped = acc.sum !== 0 && Math.sign(acc.sum) !== Math.sign(event.deltaY)
  let sum = (stale || flipped ? 0 : acc.sum) + event.deltaY
  let steps = 0
  while (Math.abs(sum) >= WHEEL_STEP_PX) {
    const unit = Math.sign(sum)
    steps -= unit
    sum -= unit * WHEEL_STEP_PX
  }
  return { steps, acc: { sum, lastAt: event.timeStamp } }
}

export type ZoomKeyAction = 'in' | 'out' | 'fit'

/**
 * ZOOM_INPUTS (c): Ctrl (Meta on macOS) with = / + / NumpadAdd → in, - / NumpadSubtract → out,
 * 0 / Numpad0 → fit. Alt, or Shift on anything but '+', is not a zoom key.
 */
export function zoomKeyAction(event: {
  key: string
  code: string
  ctrlKey: boolean
  metaKey: boolean
  shiftKey: boolean
  altKey: boolean
}): ZoomKeyAction | null {
  if (!(event.ctrlKey || event.metaKey) || event.altKey) {
    return null
  }
  if (event.key === '+' || event.code === 'NumpadAdd') {
    return 'in'
  }
  if (event.shiftKey) {
    return null
  }
  if (event.key === '=') {
    return 'in'
  }
  if (event.key === '-' || event.code === 'NumpadSubtract') {
    return 'out'
  }
  if (event.key === '0' || event.code === 'Numpad0') {
    return 'fit'
  }
  return null
}
