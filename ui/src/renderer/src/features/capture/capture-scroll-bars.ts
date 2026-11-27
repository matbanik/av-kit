import { viewTransform, type ViewState } from './capture-fit-map'

/** SCROLL_BAR_GEOMETRY (MEU-167): the bar's thickness in CSS px. */
export const SCROLL_BAR_THICKNESS = 10
/** SCROLL_BAR_GEOMETRY: the shortest thumb in CSS px, so a very long image keeps a thumb to grab. */
export const SCROLL_THUMB_MIN = 24

/** One axis of a shown bar, in CSS px: the frame, the content, the track, the thumb and its offset, and 0 to 100. */
export type ScrollBarAxis = {
  frame: number
  content: number
  track: number
  thumb: number
  offset: number
  value: number
}

/** The bars a view shows; null on an axis where the image fits the frame, and on both at Fit. */
export type ScrollBars = { x: ScrollBarAxis | null; y: ScrollBarAxis | null }

function axis(frame: number, content: number, pan: number, track: number): ScrollBarAxis {
  const thumb = Math.min(track, Math.max(SCROLL_THUMB_MIN, (track * frame) / content))
  // The share of the free content scrolled past, 0 to 1; Math.max also turns a -0 pan into +0.
  const share = Math.min(1, Math.max(0, -pan / (content - frame)))
  return {
    frame,
    content,
    track,
    thumb,
    offset: (track - thumb) * share,
    value: Math.round(100 * share),
  }
}

/**
 * SCROLL_BAR_GEOMETRY: an axis shows its bar when the view is `scale` and the content (image length times
 * scale) is longer than the frame. The track is the frame, less the thickness when both bars show. The
 * offsets are the view transform's, so the pan clamp is already applied.
 */
export function scrollBars(frame: { w: number; h: number }, image: { w: number; h: number }, state: ViewState): ScrollBars {
  if (state.kind !== 'scale') {
    return { x: null, y: null }
  }
  const placed = viewTransform(frame, image, state)
  if (placed === null) {
    return { x: null, y: null }
  }
  const contentW = image.w * placed.s
  const contentH = image.h * placed.s
  const showX = contentW > frame.w
  const showY = contentH > frame.h
  const both = showX && showY
  return {
    x: showX ? axis(frame.w, contentW, placed.ox, both ? frame.w - SCROLL_BAR_THICKNESS : frame.w) : null,
    y: showY ? axis(frame.h, contentH, placed.oy, both ? frame.h - SCROLL_BAR_THICKNESS : frame.h) : null,
  }
}

/** SCROLL_BAR_DRAG: the pan change for a thumb drag of `drag` px; 0 when the thumb fills the track. */
export function thumbDragToPan(drag: number, bar: ScrollBarAxis): number {
  const free = bar.track - bar.thumb
  if (!(free > 0) || !Number.isFinite(drag) || drag === 0) {
    return 0
  }
  return (-drag * (bar.content - bar.frame)) / free
}
