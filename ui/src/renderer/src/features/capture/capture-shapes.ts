import type { Annotation } from './capture-annotate'
import type { CaptureTool } from './CaptureViewport'

/** HEAD_FIELD (MEU-106, D-767): where an arrow draws its heads. */
export const ARROW_HEADS = ['end', 'none', 'both'] as const
export type ArrowHead = (typeof ARROW_HEADS)[number]

/** SHAPE_FIELD (MEU-106, D-769): the outline a box draws. */
export const BOX_SHAPES = ['rect', 'ellipse'] as const
export type BoxShape = (typeof BOX_SHAPES)[number]

/**
 * SHAPE_OPTIONS (MEU-106, D-770): the shape control the options row shows. A selected mark decides by its
 * type, an arrow giving the Head control and a rect the Shape control; with nothing selected the Arrow tool
 * gives Head and the Box tool gives Shape. Anything else shows neither.
 */
export function shapeOption(tool: CaptureTool, selected: Annotation | null): 'head' | 'shape' | null {
  if (selected !== null) {
    return selected.type === 'arrow' ? 'head' : selected.type === 'rect' ? 'shape' : null
  }
  return tool === 'arrow' ? 'head' : tool === 'box' ? 'shape' : null
}

/** DUPLICATE: how far a copy moves on one axis, never back and never past the room it has. */
function step(shift: number, room: number): number {
  return Math.max(0, Math.min(shift, room))
}

/**
 * DUPLICATE (MEU-106, MEU-107, D-777): a copy of `mark` moved right and down by `shift`, or by less where the
 * image edge leaves less room. An arrow's room is its larger endpoint coordinate against `W - 1` (`H - 1`
 * down); a text or step mark's is its anchor against the same; a rect of either shape covers the closed box,
 * so `x + width` against `W - 1`; a highlight, redact, pixelate or eraser covers the half-open box, so
 * `x + width` against `W`. The copy is never resized. A step keeps its number; the page renumbers it.
 */
export function duplicateMark(mark: Annotation, shift: number, imageW: number, imageH: number): Annotation {
  switch (mark.type) {
    case 'arrow': {
      const dx = step(shift, imageW - 1 - Math.max(mark.from[0], mark.to[0]))
      const dy = step(shift, imageH - 1 - Math.max(mark.from[1], mark.to[1]))
      return { ...mark, from: [mark.from[0] + dx, mark.from[1] + dy], to: [mark.to[0] + dx, mark.to[1] + dy] }
    }
    case 'text':
    case 'step': {
      const dx = step(shift, imageW - 1 - mark.x)
      const dy = step(shift, imageH - 1 - mark.y)
      return { ...mark, x: mark.x + dx, y: mark.y + dy }
    }
    case 'rect': {
      const dx = step(shift, imageW - 1 - (mark.x + mark.width))
      const dy = step(shift, imageH - 1 - (mark.y + mark.height))
      return { ...mark, x: mark.x + dx, y: mark.y + dy }
    }
    case 'highlight':
    case 'redact':
    case 'pixelate':
    case 'eraser': {
      const dx = step(shift, imageW - (mark.x + mark.width))
      const dy = step(shift, imageH - (mark.y + mark.height))
      return { ...mark, x: mark.x + dx, y: mark.y + dy }
    }
    default: {
      const unhandled: never = mark
      throw new Error(`Unhandled mark: ${String(unhandled)}`)
    }
  }
}
