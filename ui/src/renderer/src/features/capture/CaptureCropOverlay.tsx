import type { CropBox } from './capture-crop'
import type { ImagePoint } from './capture-fit-map'
import { boxHandlePoints, RESIZE_HANDLE_CSS, type HandleId } from './capture-transform'

type CaptureCropOverlayProps = {
  box: CropBox
  /** A drag is live: the rule-of-thirds lines show. */
  dragging: boolean
  imageWidth: number
  imageHeight: number
  /** The view scale, so the handle squares keep their CSS size at every zoom. */
  scale: number
}

/**
 * CROP_LOOK (MEU-131, D-523): the dim outside the box, its outline, the thirds while a drag is live and the eight
 * handle squares, in image pixels in the zoom box. It takes no pointer events; the surface routes every gesture.
 */
export function CaptureCropOverlay({ box, dragging, imageWidth, imageHeight, scale }: CaptureCropOverlayProps) {
  const W = Math.max(1, imageWidth)
  const H = Math.max(1, imageHeight)
  const { x, y, width, height } = box
  const side = RESIZE_HANDLE_CSS / (scale > 0 ? scale : 1)
  const handles = Object.entries(boxHandlePoints(box)) as Array<[HandleId, ImagePoint]>
  const thirdsX = [x + width / 3, x + (2 * width) / 3]
  const thirdsY = [y + height / 3, y + (2 * height) / 3]
  return (
    <svg
      data-testid="capture-crop-overlay"
      className="absolute inset-0 w-full h-full pointer-events-none"
      viewBox={`0 0 ${W} ${H}`}
      preserveAspectRatio="xMidYMid meet"
      aria-hidden="true"
    >
      <path
        data-testid="capture-crop-dim"
        d={`M0 0H${W}V${H}H0Z M${x} ${y}H${x + width}V${y + height}H${x}Z`}
        fillRule="evenodd"
        fill="var(--color-bg)"
        opacity={0.6}
      />
      <rect
        data-testid="capture-crop-outline"
        x={x}
        y={y}
        width={width}
        height={height}
        fill="none"
        stroke="var(--color-accent)"
        strokeWidth={1}
        vectorEffect="non-scaling-stroke"
      />
      {dragging ? (
        <g data-testid="capture-crop-thirds" stroke="var(--color-accent)" strokeOpacity={0.5} strokeWidth={1}>
          {thirdsX.map((lineX) => (
            <line key={`x${lineX}`} x1={lineX} y1={y} x2={lineX} y2={y + height} vectorEffect="non-scaling-stroke" />
          ))}
          {thirdsY.map((lineY) => (
            <line key={`y${lineY}`} x1={x} y1={lineY} x2={x + width} y2={lineY} vectorEffect="non-scaling-stroke" />
          ))}
        </g>
      ) : null}
      {handles.map(([handle, point]) => (
        <rect
          key={handle}
          data-testid="capture-crop-handle"
          data-handle={handle}
          x={point.x - side / 2}
          y={point.y - side / 2}
          width={side}
          height={side}
          fill="var(--color-bg)"
          stroke="var(--color-accent)"
          strokeWidth={1}
          vectorEffect="non-scaling-stroke"
        />
      ))}
    </svg>
  )
}
