export type MapPointerInput = {
  clientX: number
  clientY: number
  left: number
  top: number
  containerW: number
  containerH: number
  imageW: number
  imageH: number
}

export type ImagePoint = {
  x: number
  y: number
}

export function fitScaleOrigin(input: Pick<MapPointerInput, 'containerW' | 'containerH' | 'imageW' | 'imageH'>): {
  s: number
  ox: number
  oy: number
} {
  const s = Math.min(input.containerW / input.imageW, input.containerH / input.imageH)
  return {
    s,
    ox: (input.containerW - input.imageW * s) / 2,
    oy: (input.containerH - input.imageH * s) / 2,
  }
}

export function mapPointerToImage(input: MapPointerInput): ImagePoint | null {
  const mapped = mapPointerToImageUnclamped(input)
  if (mapped === null) {
    return null
  }
  if (mapped.x < 0 || mapped.y < 0 || mapped.x >= input.imageW || mapped.y >= input.imageH) {
    return null
  }
  return mapped
}

export function mapPointerToImageUnclamped(input: MapPointerInput): ImagePoint | null {
  if (input.imageW <= 0 || input.imageH <= 0 || input.containerW <= 0 || input.containerH <= 0) {
    return null
  }
  const { s, ox, oy } = fitScaleOrigin(input)
  if (!Number.isFinite(s) || s <= 0) {
    return null
  }
  return {
    x: Math.round((input.clientX - input.left - ox) / s),
    y: Math.round((input.clientY - input.top - oy) / s),
  }
}

export function clampImagePoint(point: ImagePoint, imageW: number, imageH: number): ImagePoint {
  const maxX = Math.max(0, imageW - 1)
  const maxY = Math.max(0, imageH - 1)
  return {
    x: Math.min(maxX, Math.max(0, point.x)),
    y: Math.min(maxY, Math.max(0, point.y)),
  }
}

export function mapImageToPointer(
  point: ImagePoint,
  box: { left: number; top: number; containerW: number; containerH: number; imageW: number; imageH: number },
): { x: number; y: number } {
  const { s, ox, oy } = fitScaleOrigin(box)
  return {
    x: box.left + ox + point.x * s,
    y: box.top + oy + point.y * s,
  }
}

/** ZOOM_STATE: Fit, or a ladder scale with the content offset inside the container (CSS px). */
export type ViewState = { kind: 'fit' } | { kind: 'scale'; scale: number; ox: number; oy: number }

/** The transform actually applied: image px × `s` + (`ox`, `oy`) = container CSS px. */
export type ViewTransform = { s: number; ox: number; oy: number }

function positiveFinite(value: number): boolean {
  return Number.isFinite(value) && value > 0
}

/** Centres an axis whose content fits; otherwise clamps the offset so no blank margin shows. */
function placeAxis(container: number, content: number, offset: number): number {
  if (content <= container) {
    return (container - content) / 2
  }
  return Math.min(0, Math.max(container - content, offset))
}

/**
 * VIEW_TRANSFORM: the single geometry source for pointer mapping, handle radii, the text draft and the
 * content box. Fit returns exactly `fitScaleOrigin`, so the MEU-59 mapping is unchanged. Any invalid size,
 * scale or offset returns null, and the caller then maps nothing.
 */
export function viewTransform(
  container: { w: number; h: number },
  image: { w: number; h: number },
  state: ViewState,
): ViewTransform | null {
  if (![container.w, container.h, image.w, image.h].every(positiveFinite)) {
    return null
  }
  if (state.kind === 'fit') {
    const fit = fitScaleOrigin({ containerW: container.w, containerH: container.h, imageW: image.w, imageH: image.h })
    return positiveFinite(fit.s) ? fit : null
  }
  if (!positiveFinite(state.scale) || !Number.isFinite(state.ox) || !Number.isFinite(state.oy)) {
    return null
  }
  return {
    s: state.scale,
    ox: placeAxis(container.w, image.w * state.scale, state.ox),
    oy: placeAxis(container.h, image.h * state.scale, state.oy),
  }
}

/** VIEW_MAP pointer → image, before the in-image check (same rounding as `mapPointerToImageUnclamped`). */
export function mapPointerWithViewUnclamped(
  clientX: number,
  clientY: number,
  left: number,
  top: number,
  t: ViewTransform,
): ImagePoint | null {
  if (!positiveFinite(t.s)) {
    return null
  }
  return {
    x: Math.round((clientX - left - t.ox) / t.s),
    y: Math.round((clientY - top - t.oy) / t.s),
  }
}

/** VIEW_MAP pointer → image; a point outside the zoomed image returns null, as `mapPointerToImage` does. */
export function mapPointerWithView(
  clientX: number,
  clientY: number,
  left: number,
  top: number,
  t: ViewTransform,
  imageW: number,
  imageH: number,
): ImagePoint | null {
  const mapped = mapPointerWithViewUnclamped(clientX, clientY, left, top, t)
  if (mapped === null || mapped.x < 0 || mapped.y < 0 || mapped.x >= imageW || mapped.y >= imageH) {
    return null
  }
  return mapped
}

/** VIEW_MAP image → pointer (container CSS px offset by `left`/`top`). */
export function mapImageToPointerWithView(
  point: ImagePoint,
  left: number,
  top: number,
  t: ViewTransform,
): { x: number; y: number } {
  return { x: left + t.ox + point.x * t.s, y: top + t.oy + point.y * t.s }
}
