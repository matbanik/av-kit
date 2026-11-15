import type { ArrowHead } from './capture-shapes'

// ARROW_HEAD (MEU-83, D-12): head = max(ARROWHEAD_MIN_PX, ARROWHEAD_LENGTH_FACTOR * stroke).
export const ARROWHEAD_MIN_PX = 10
export const ARROWHEAD_LENGTH_FACTOR = 5
export const ARROWHEAD_ANGLE_RAD = 0.45
// ARROW_SHAFT_OVERLAP_PX (MEU-83, D-13): the shaft runs this far past the head base.
export const ARROW_SHAFT_OVERLAP_PX = 1

export type ArrowheadVertices = {
  tip: [number, number]
  left: [number, number]
  right: [number, number]
}

export function arrowheadVertices(
  from: [number, number],
  to: [number, number],
  strokeWidth: number,
): ArrowheadVertices {
  const dx = to[0] - from[0]
  const dy = to[1] - from[1]
  const angle = Math.atan2(dy, dx)
  const head = Math.max(ARROWHEAD_MIN_PX, ARROWHEAD_LENGTH_FACTOR * strokeWidth)
  return {
    tip: [to[0], to[1]],
    left: [to[0] - head * Math.cos(angle - ARROWHEAD_ANGLE_RAD), to[1] - head * Math.sin(angle - ARROWHEAD_ANGLE_RAD)],
    right: [to[0] - head * Math.cos(angle + ARROWHEAD_ANGLE_RAD), to[1] - head * Math.sin(angle + ARROWHEAD_ANGLE_RAD)],
  }
}

/** SHAFT_END: where the shaft stops, or null when only the head is drawn. Zero length keeps from -> to. */
export function arrowShaftEnd(
  from: [number, number],
  to: [number, number],
  strokeWidth: number,
): [number, number] | null {
  const dx = to[0] - from[0]
  const dy = to[1] - from[1]
  const length = Math.hypot(dx, dy)
  if (length === 0) return [to[0], to[1]]
  const head = Math.max(ARROWHEAD_MIN_PX, ARROWHEAD_LENGTH_FACTOR * strokeWidth)
  const back = head * Math.cos(ARROWHEAD_ANGLE_RAD) - ARROW_SHAFT_OVERLAP_PX
  if (length <= back) return null
  return [to[0] - (dx / length) * back, to[1] - (dy / length) * back]
}

/**
 * HEAD_PREVIEW (MEU-106, D-767): the TS mirror of the adapter's `arrow_shaft_span`.
 * `none` gives `[from, to]`; `end` gives `[from, arrowShaftEnd(...)]`, today's span; `both` pulls
 * each end back by the head's back-off, or gives null when the arrow is no longer than two.
 */
export function arrowShaftSpan(
  from: [number, number],
  to: [number, number],
  strokeWidth: number,
  head: ArrowHead,
): [[number, number], [number, number]] | null {
  const start: [number, number] = [from[0], from[1]]
  if (head === 'none') return [start, [to[0], to[1]]]
  if (head === 'end') {
    const end = arrowShaftEnd(from, to, strokeWidth)
    return end === null ? null : [start, end]
  }
  const dx = to[0] - from[0]
  const dy = to[1] - from[1]
  const length = Math.hypot(dx, dy)
  if (length === 0) return [start, [from[0], from[1]]]
  const back =
    Math.max(ARROWHEAD_MIN_PX, ARROWHEAD_LENGTH_FACTOR * strokeWidth) * Math.cos(ARROWHEAD_ANGLE_RAD) -
    ARROW_SHAFT_OVERLAP_PX
  if (length <= 2 * back) return null
  const ux = dx / length
  const uy = dy / length
  return [
    [from[0] + ux * back, from[1] + uy * back],
    [to[0] - ux * back, to[1] - uy * back],
  ]
}

export function arrowHeadPoints(from: [number, number], to: [number, number], strokeWidth: number): string {
  const verts = arrowheadVertices(from, to, strokeWidth)
  return `${verts.tip[0]},${verts.tip[1]} ${verts.left[0]},${verts.left[1]} ${verts.right[0]},${verts.right[1]}`
}
