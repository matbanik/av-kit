import { useCallback, useEffect, useId, useLayoutEffect, useRef, useState, type ReactNode } from 'react'

import { Button } from '../../components/ui/Button'
import { SegmentedControl } from '../../components/ui/SegmentedControl'
import type { Annotation, RedactMode } from './capture-annotate'
import type { CropBox } from './capture-crop'
import { arrowHeadPoints, arrowShaftSpan } from './capture-arrow-head'
import { contrastText, displayHex, hexForNamedColor, NAMED_COLOR_HEX, normalizeHex } from './capture-color'
import { shapeOption, type ArrowHead, type BoxShape } from './capture-shapes'
import { stepBadgeLayout, stepTextColor } from './capture-step'
import {
  clampImagePoint,
  mapImageToPointerWithView,
  mapPointerWithView,
  mapPointerWithViewUnclamped,
  viewTransform,
  type ImagePoint,
  type ViewTransform,
} from './capture-fit-map'
import { useG30Styles } from '../../components/ui/SelectInput'
import {
  applyRegionPass,
  isRegionMark,
  PIXELATE_BLOCK_DEFAULT,
  PIXELATE_BLOCK_MAX,
  PIXELATE_BLOCK_MIN,
  regionClip,
  type RegionBox,
} from './capture-region-pass'
import { HANDLE_RADIUS_CSS, bodyHandleImagePoint, markLabel } from './capture-hit-test'
import {
  boxHandlePoints,
  cursorForHandle,
  isBoxMark,
  RESIZE_HANDLE_CSS,
  textPlateHandlePoints,
  type HandleId,
} from './capture-transform'
import { ACTION_BUTTONS, optionGroups, TOOL_LETTERS, TOOLBAR_BUTTONS } from './capture-toolbar'
import {
  WHEEL_IDLE,
  wheelSteps,
  zoomAbout,
  zoomKeyAction,
  ZOOM_PAN_HINT,
  zoomStep,
  type ZoomDirection,
  type ZoomState,
} from './capture-zoom'
import {
  SVG_DOMINANT_BASELINE,
  SVG_TEXT_ANCHOR,
  SVG_TEXT_FONT_FAMILY,
  segoeLinePitchPx,
  svgTextBaselineY,
  textBackgroundBox,
  textLines,
} from './capture-text-metrics'
import { ToolbarIconButton } from './ToolbarIconButton'
import { CaptureCropOverlay } from './CaptureCropOverlay'
import { CaptureScrubField } from './CaptureScrubField'
import { FONT_SCRUB_MAX, parsePositiveInt, STROKE_SCRUB_MAX } from './capture-scrub'
import { SCROLL_BAR_THICKNESS, scrollBars, thumbDragToPan, type ScrollBarAxis } from './capture-scroll-bars'
import { isRegistryChord } from '../../registry/commandRegistry'

/** HOVER_CURSOR: literal class names, so Tailwind emits each one. */
const RESIZE_CURSOR_CLASS: Record<ReturnType<typeof cursorForHandle>, string> = {
  'nwse-resize': ' cursor-nwse-resize',
  'nesw-resize': ' cursor-nesw-resize',
  'ns-resize': ' cursor-ns-resize',
  'ew-resize': ' cursor-ew-resize',
}

/** CROP_POINTER (MEU-131): what a press under the pointer would do while the crop is open. */
export type CropCursor = HandleId | 'move' | 'draw'

/** CROP_LOOK: the surface cursor for the crop's hover; a handle shows its resize cursor. */
function cropCursorClass(cursor: CropCursor | null): string {
  if (cursor === 'move') {
    return ' cursor-move'
  }
  if (cursor === null || cursor === 'draw') {
    return ' cursor-crosshair'
  }
  return RESIZE_CURSOR_CLASS[cursorForHandle(cursor)]
}

export type CaptureTool =
  | 'select'
  | 'arrow'
  | 'box'
  | 'highlight'
  | 'text'
  | 'step'
  | 'redact'
  | 'eraser'
  | 'crop'
export type CaptureViewVariant = 'original' | 'annotated'

export type TextDraft = {
  x: number
  y: number
  value: string
  /** TEXT_REEDIT (MEU-101): the committed text mark this draft edits; it is not painted while the draft is open. */
  editIndex?: number
}

export type SurfacePointer = {
  phase: 'down' | 'move' | 'up' | 'cancel' | 'dblclick'
  pointerId: number
  cssX: number
  cssY: number
  scale: number
  ox: number
  oy: number
  image: ImagePoint | null
  imageClamped: ImagePoint | null
  /** CROP_POINTER (MEU-131): Shift keeps the box's ratio under Free. */
  shiftKey: boolean
  /** MODIFIERS (MEU-143): Alt draws a bounded mark from its centre. */
  altKey: boolean
}

type CaptureViewportProps = {
  empty: boolean
  /** The selected shot; ZOOM_STATE returns to Fit whenever it changes (ZOOM_RESET). */
  shotId?: string | null
  /** A shot is selected; tools are disabled without one (Phase 11 CP5). Defaults to true. */
  hasSelection?: boolean
  /** Existing `overlayReady && imageEpoch > 0` state, exposed as CAPTURE_READY_SIGNAL. */
  overlayReady?: boolean
  /** Per-shot actions the page owns (Save overlay, Open file/folder, Delete). */
  actions?: ReactNode
  /** Inline confirmation strip rendered above the surface. */
  confirmStrip?: ReactNode
  /** Empty-state block that replaces the surface when there are no shots. */
  emptyState?: ReactNode
  /** Status/shot-info lines rendered under the surface. */
  statusLine?: ReactNode
  imageUrl: string | null
  imageWidth?: number
  imageHeight?: number
  hasAnnotated?: boolean
  viewVariant?: CaptureViewVariant
  tool: CaptureTool
  color: string
  stroke: string
  fontSize?: string
  textBg?: string
  /** BLOCK_CONTROL: the Block size field's text. */
  blockSize?: string
  /** REDACT_MODE (D-680): the checked Redact mode, the selected redaction's own when one is selected. */
  redactMode?: RedactMode
  annotations: Annotation[]
  preview?: Annotation | null
  selectedIndex?: number | null
  /** HOVER_CURSOR: the resize handle under the pointer or being dragged; the pan cursors win over it. */
  resizeCursor?: HandleId | null
  canUndo: boolean
  canRedo: boolean
  textDraft: TextDraft | null
  onTool: (tool: CaptureTool) => void
  /** COLOR_HEX, COLOR_WELL (MEU-105): one colour commit, from the hex field or the well's `change`. */
  onColor: (color: string) => void
  /** COLOR_WELL: one native `input` event of the well; it paints with no undo step and no save. */
  onColorPreview?: (color: string) => void
  /** COLOR_NAMED: one named pick, which commits. */
  onNamedColor?: (name: string) => void
  onStroke: (stroke: string) => void
  onFontSize?: (size: string) => void
  /** SIZE_BURST (MEU-85): one scrub step on the Stroke or Size field, then its commit or cancel. */
  onStrokePreview?: (value: number) => void
  onStrokeCommit?: () => void
  onStrokeCancel?: () => void
  onFontSizePreview?: (value: number) => void
  onFontSizeCommit?: () => void
  onFontSizeCancel?: () => void
  /** SCRUB_BASE: bumped by the page each time it closes that field's burst. */
  strokeEpoch?: number
  fontSizeEpoch?: number
  /** TOOL_LOCK (MEU-87): keep the current tool after each mark. LOCK_STORE (MEU-143): the page persists it. */
  toolLocked?: boolean
  onToggleToolLock?: () => void
  /** ALT_NO_MENU (MEU-143): true while a box, highlight, redact or eraser draw is live. */
  boundedDrawLive?: () => boolean
  /** TEXT_BG_WELL (MEU-105): one background commit, from the well's `change` or Clear (''). */
  onTextBg?: (color: string) => void
  onTextBgPreview?: (color: string) => void
  onBlockSize?: (size: string) => void
  /** BLOCK_SCRUB (MEU-105): one scrub step on the Block size field, then its commit or cancel. */
  onBlockSizePreview?: (value: number) => void
  onBlockSizeCommit?: () => void
  onBlockSizeCancel?: () => void
  blockSizeEpoch?: number
  /** SHAPE_OPTIONS (MEU-106): the checked Head and Shape, a selected mark's own when one is selected. */
  arrowHead?: ArrowHead
  boxShape?: BoxShape
  onArrowHead?: (head: ArrowHead) => void
  onBoxShape?: (shape: BoxShape) => void
  /** STEP_STYLE (MEU-107): the Step size field's text, its scrub steps and its commit or cancel. */
  stepSize?: string
  onStepSize?: (size: string) => void
  onStepSizePreview?: (value: number) => void
  onStepSizeCommit?: () => void
  onStepSizeCancel?: () => void
  stepSizeEpoch?: number
  onRedactMode?: (mode: RedactMode) => void
  onViewVariant?: (variant: CaptureViewVariant) => void
  onUndo: () => void
  onRedo: () => void
  onPointer: (x: number, y: number, phase: 'down' | 'up') => void
  onSurfacePointer?: (event: SurfacePointer) => void
  onSelectIndex?: (index: number) => void
  onRemoveMark?: () => void
  /** NUDGE_TARGET: an arrow handle took focus, so the arrow keys move that end. */
  onHandleFocus?: (end: 'from' | 'to') => void
  /** NUDGE_TARGET: focus landed on the draw surface itself, so the arrow keys move the whole mark. */
  onSurfaceFocus?: () => void
  onEditorKey?: (event: KeyboardEvent) => void
  onTextDraftChange: (value: string) => void
  onTextCommit: () => void
  onTextCancel: () => void
  /** CROP_LOOK (MEU-131): the open crop's box, whether a drag is live and the hover cursor; null when closed. */
  crop?: { box: CropBox; dragging: boolean; cursor: CropCursor | null } | null
  /** CROP_BAR: replaces the option groups while the crop is open. */
  cropBar?: ReactNode
  /** CROP_MODAL (D-518): set while the crop is open; every other tool, history, the lock and Annotated wait. */
  cropReason?: string
  /** CROP_UNSAVED_GATE (D-509): why Crop can't open now, or undefined. */
  cropDisabledReason?: string
  onToggleCrop?: () => void
}

function toolVariant(active: boolean): 'primary' | 'outline' {
  return active ? 'primary' : 'outline'
}

/** REDACT_MODE (D-680): the Redact tool's two modes, Solid first. */
const REDACT_MODE_OPTIONS = [
  { id: 'capture-redact-solid', testId: 'capture-redact-solid', value: 'solid', label: 'Solid' },
  { id: 'capture-redact-pixelate', testId: 'capture-redact-pixelate', value: 'pixelate', label: 'Pixelate' },
] as const

/** SHAPE_OPTIONS (MEU-106, D-771): the Arrow tool's heads, End first. */
const ARROW_HEAD_OPTIONS = [
  { id: 'capture-arrow-head-end', testId: 'capture-arrow-head-end', value: 'end', label: 'End' },
  { id: 'capture-arrow-head-none', testId: 'capture-arrow-head-none', value: 'none', label: 'None' },
  { id: 'capture-arrow-head-both', testId: 'capture-arrow-head-both', value: 'both', label: 'Both' },
] as const

/** SHAPE_OPTIONS (MEU-106, D-771): the Box tool's outlines, Rectangle first. */
const BOX_SHAPE_OPTIONS = [
  { id: 'capture-box-shape-rect', testId: 'capture-box-shape-rect', value: 'rect', label: 'Rectangle' },
  { id: 'capture-box-shape-ellipse', testId: 'capture-box-shape-ellipse', value: 'ellipse', label: 'Ellipse' },
] as const

/** STEP_STYLE: the Step size field's range and the default an invalid field scrubs from. */
const STEP_SIZE_MIN = 12
const STEP_SIZE_MAX = 200
const STEP_SIZE_DEFAULT = 32

function AnnotationMark({ ann }: { ann: Annotation }) {
  if (ann.type === 'arrow') {
    // HEAD_PREVIEW (MEU-106, D-767): the line over arrowShaftSpan and one polygon per head.
    const length = Math.hypot(ann.to[0] - ann.from[0], ann.to[1] - ann.from[1])
    const head = ann.head ?? 'end'
    const span = arrowShaftSpan(ann.from, ann.to, ann.stroke_width, head)
    return (
      <g
        data-testid="capture-annotation"
        data-annotation-type="arrow"
        data-head={head}
        x1={ann.from[0]}
        y1={ann.from[1]}
        x2={ann.to[0]}
        y2={ann.to[1]}
        stroke={ann.color}
      >
        {span !== null ? (
          <line
            x1={span[0][0]}
            y1={span[0][1]}
            x2={span[1][0]}
            y2={span[1][1]}
            stroke={ann.color}
            strokeWidth={ann.stroke_width}
          />
        ) : null}
        {length > 0 && head !== 'none' ? (
          <polygon
            points={arrowHeadPoints(ann.from, ann.to, ann.stroke_width)}
            fill={ann.color}
            stroke="none"
          />
        ) : null}
        {length > 0 && head === 'both' ? (
          <polygon
            points={arrowHeadPoints(ann.to, ann.from, ann.stroke_width)}
            fill={ann.color}
            stroke="none"
          />
        ) : null}
      </g>
    )
  }
  if (ann.type === 'rect' && ann.shape === 'ellipse') {
    // ELLIPSE_PREVIEW (MEU-106, D-769): the ellipse inscribed in the box the <rect> draws.
    return (
      <ellipse
        data-testid="capture-annotation"
        data-annotation-type="rect"
        data-shape="ellipse"
        cx={ann.x + ann.width / 2}
        cy={ann.y + ann.height / 2}
        rx={ann.width / 2}
        ry={ann.height / 2}
        fill="none"
        stroke={ann.color}
        strokeWidth={ann.stroke_width}
      />
    )
  }
  if (ann.type === 'rect') {
    return (
      <rect
        data-testid="capture-annotation"
        data-annotation-type="rect"
        x={ann.x}
        y={ann.y}
        width={ann.width}
        height={ann.height}
        fill="none"
        stroke={ann.color}
        strokeWidth={ann.stroke_width}
      />
    )
  }
  if (ann.type === 'highlight') {
    return (
      <rect
        data-testid="capture-annotation"
        data-annotation-type="highlight"
        x={ann.x}
        y={ann.y}
        width={ann.width}
        height={ann.height}
        fill={ann.color}
        opacity={ann.opacity}
      />
    )
  }
  if (ann.type === 'eraser') {
    // REGION_MARK_SVG: a transparent rect for selection and counting; REGION_PREVIEW draws the pixels.
    return (
      <rect
        data-testid="capture-annotation"
        data-annotation-type={ann.type}
        x={ann.x}
        y={ann.y}
        width={ann.width}
        height={ann.height}
        fill="none"
        stroke="none"
      />
    )
  }
  if (ann.type === 'pixelate' || ann.type === 'redact') {
    // REDACT_OUTLINE (D-684): a redaction draws a 1 px dashed outline here, in the Original view only; no bake
    // and no Annotated view draws it. REGION_PREVIEW draws the pixels under it.
    return (
      <rect
        data-testid="capture-annotation"
        data-annotation-type={ann.type}
        x={ann.x}
        y={ann.y}
        width={ann.width}
        height={ann.height}
        fill="none"
        stroke="var(--color-fg)"
        strokeOpacity={0.7}
        strokeWidth={1}
        strokeDasharray="4 3"
        vectorEffect="non-scaling-stroke"
      />
    )
  }
  if (ann.type === 'step') {
    // STEP_PREVIEW (MEU-107, D-773): the bake's layout, a disc and the number centred on x.
    const layout = stepBadgeLayout(ann.x, ann.y, ann.number, ann.size)
    return (
      <g data-testid="capture-annotation" data-annotation-type="step">
        <circle cx={ann.x} cy={ann.y} r={layout.radius} fill={displayHex(ann.color)} stroke="none" />
        <text
          x={ann.x}
          y={layout.baseline}
          fill={stepTextColor(ann.color)}
          fontSize={layout.fontPx}
          fontFamily={SVG_TEXT_FONT_FAMILY}
          textAnchor="middle"
        >
          {ann.number}
        </text>
      </g>
    )
  }
  const plate = ann.bg_color
    ? textBackgroundBox({ x: ann.x, y: ann.y, text: ann.text, font_size: ann.font_size })
    : null
  return (
    <g>
      {plate !== null ? (
        <rect
          data-testid="capture-text-bg-plate"
          x={plate.x}
          y={plate.y}
          width={plate.width}
          height={plate.height}
          fill={ann.bg_color ?? 'none'}
        />
      ) : null}
      <text
        data-testid="capture-annotation"
        data-annotation-type="text"
        x={ann.x}
        y={svgTextBaselineY(ann)}
        fill={ann.color}
        fontSize={ann.font_size}
        fontFamily={SVG_TEXT_FONT_FAMILY}
        textAnchor={SVG_TEXT_ANCHOR}
        dominantBaseline={SVG_DOMINANT_BASELINE}
      >
        {ann.text.includes('\n')
          ? textLines(ann.text).map((line, index) => (
              <tspan
                key={index}
                x={ann.x}
                y={svgTextBaselineY(ann) + index * segoeLinePitchPx(ann.font_size)}
              >
                {line}
              </tspan>
            ))
          : ann.text}
      </text>
    </g>
  )
}

const FIT_STATE: ZoomState = { kind: 'fit' }

/** REGION_SOURCE: the Original image's pixels, read once per load, keyed by the URL they came from. */
type RegionSource = { url: string; width: number; height: number; data: Uint8ClampedArray }

function readRegionSource(image: HTMLImageElement, url: string): RegionSource | null {
  const width = image.naturalWidth
  const height = image.naturalHeight
  if (width < 1 || height < 1) {
    return null
  }
  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height
  const context = canvas.getContext('2d', { willReadFrequently: true })
  if (context === null) {
    return null
  }
  context.drawImage(image, 0, 0)
  try {
    return { url, width, height, data: context.getImageData(0, 0, width, height).data }
  } catch {
    // A tainted canvas (not a same-origin blob URL) has no readable pixels: no preview, no throw.
    return null
  }
}

/**
 * REGION_PREVIEW: clear the layer, run `applyRegionPass` over a copy of the source inside the bounding box
 * of the region rectangles grown by 1 px, and write back only those rectangles; the rest stays transparent.
 */
function paintRegionLayer(canvas: HTMLCanvasElement, source: RegionSource, marks: readonly Annotation[]): void {
  const context = canvas.getContext('2d')
  if (context === null) {
    return
  }
  context.clearRect(0, 0, canvas.width, canvas.height)
  const boxes = marks
    .map((mark) => regionClip(mark, source.width, source.height))
    .filter((box): box is RegionBox => box !== null)
  if (boxes.length === 0) {
    return
  }
  const x0 = Math.max(0, Math.min(...boxes.map((box) => box.x0)) - 1)
  const y0 = Math.max(0, Math.min(...boxes.map((box) => box.y0)) - 1)
  const x1 = Math.min(source.width, Math.max(...boxes.map((box) => box.x1)) + 1)
  const y1 = Math.min(source.height, Math.max(...boxes.map((box) => box.y1)) + 1)
  const work = context.createImageData(x1 - x0, y1 - y0)
  for (let y = y0; y < y1; y += 1) {
    const from = (y * source.width + x0) * 4
    work.data.set(source.data.subarray(from, from + work.width * 4), (y - y0) * work.width * 4)
  }
  // The marks move into the work box's frame; it contains every clipped rectangle, so clipping agrees.
  const shifted = marks.map((mark) => (isRegionMark(mark) ? { ...mark, x: mark.x - x0, y: mark.y - y0 } : mark))
  applyRegionPass(work.data, work.width, work.height, shifted)
  for (const box of boxes) {
    context.putImageData(work, x0, y0, box.x0 - x0, box.y0 - y0, box.x1 - box.x0, box.y1 - box.y0)
  }
}

/** The surface's live box and its VIEW_TRANSFORM; the surface is overflow-hidden, never a scroll container. */
function liveView(
  target: HTMLElement,
  imageWidth: number,
  imageHeight: number,
  zoom: ZoomState,
): { box: DOMRect; view: ViewTransform | null } {
  const box = target.getBoundingClientRect()
  return { box, view: viewTransform({ w: box.width, h: box.height }, { w: imageWidth, h: imageHeight }, zoom) }
}

function mapEvent(
  event: { currentTarget: HTMLElement; clientX: number; clientY: number },
  imageWidth: number,
  imageHeight: number,
  zoom: ZoomState,
): ImagePoint | null {
  const { box, view } = liveView(event.currentTarget, imageWidth, imageHeight, zoom)
  return view === null
    ? null
    : mapPointerWithView(event.clientX, event.clientY, box.left, box.top, view, imageWidth, imageHeight)
}

function mapEventClamped(
  event: { currentTarget: HTMLElement; clientX: number; clientY: number },
  imageWidth: number,
  imageHeight: number,
  zoom: ZoomState,
): ImagePoint | null {
  const { box, view } = liveView(event.currentTarget, imageWidth, imageHeight, zoom)
  const loose = view === null ? null : mapPointerWithViewUnclamped(event.clientX, event.clientY, box.left, box.top, view)
  return loose === null ? null : clampImagePoint(loose, imageWidth, imageHeight)
}

/** SURFACE_POINTER: every surface event carries the VIEW_TRANSFORM it was mapped with. */
function surfaceFromDom(
  event: { currentTarget: EventTarget | null; clientX: number; clientY: number; shiftKey?: boolean; altKey?: boolean },
  phase: SurfacePointer['phase'],
  pointerId: number,
  imageWidth: number,
  imageHeight: number,
  zoom: ZoomState,
): SurfacePointer | null {
  const target = event.currentTarget
  if (!(target instanceof HTMLElement)) {
    return null
  }
  const { box, view } = liveView(target, imageWidth, imageHeight, zoom)
  const loose = view === null ? null : mapPointerWithViewUnclamped(event.clientX, event.clientY, box.left, box.top, view)
  return {
    phase,
    pointerId,
    cssX: event.clientX - box.left,
    cssY: event.clientY - box.top,
    scale: view?.s ?? 0,
    ox: view?.ox ?? 0,
    oy: view?.oy ?? 0,
    image: view === null ? null : mapPointerWithView(event.clientX, event.clientY, box.left, box.top, view, imageWidth, imageHeight),
    imageClamped: loose === null ? null : clampImagePoint(loose, imageWidth, imageHeight),
    shiftKey: event.shiftKey === true,
    altKey: event.altKey === true,
  }
}

function capturePointer(target: HTMLElement, pointerId: number): void {
  if (typeof target.setPointerCapture === 'function') {
    try {
      target.setPointerCapture(pointerId)
    } catch {
      /* jsdom */
    }
  }
}

function releasePointer(target: HTMLElement, pointerId: number): void {
  if (typeof target.releasePointerCapture === 'function') {
    try {
      target.releasePointerCapture(pointerId)
    } catch {
      /* jsdom */
    }
  }
}

/**
 * SCROLL_BAR_OVERLAY (MEU-167): one bar drawn over the frame's edge from the view transform; the frame stays
 * overflow-hidden. SCROLL_BAR_DRAG: only the thumb takes pointer input, and it stops every pointer and mouse
 * event, so the draw surface never sees a thumb drag. SCROLL_BAR_LOOK: theme tokens only and no transition.
 */
function ViewportScrollBar({
  axis,
  bar,
  controls,
  onDrag,
}: {
  axis: 'x' | 'y'
  bar: ScrollBarAxis
  controls: string
  onDrag: (pixels: number) => void
}) {
  const dragRef = useRef<{ pointerId: number; at: number } | null>(null)
  const horizontal = axis === 'x'
  const place = horizontal
    ? { left: 0, bottom: 0, width: bar.track, height: SCROLL_BAR_THICKNESS }
    : { top: 0, right: 0, width: SCROLL_BAR_THICKNESS, height: bar.track }
  const thumb = horizontal
    ? { left: bar.offset, top: 0, width: bar.thumb, height: '100%' }
    : { top: bar.offset, left: 0, width: '100%', height: bar.thumb }
  const stop = (event: React.SyntheticEvent): void => {
    event.stopPropagation()
  }
  const end = (event: React.PointerEvent<HTMLDivElement>): void => {
    event.stopPropagation()
    if (dragRef.current?.pointerId === event.pointerId) {
      dragRef.current = null
      releasePointer(event.currentTarget, event.pointerId)
    }
  }
  return (
    <div
      data-testid={`capture-scrollbar-${axis}`}
      role="scrollbar"
      aria-orientation={horizontal ? 'horizontal' : 'vertical'}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={bar.value}
      aria-controls={controls}
      aria-label={horizontal ? 'Horizontal scroll' : 'Vertical scroll'}
      className="absolute pointer-events-none bg-transparent"
      style={place}
    >
      <div
        data-testid={`capture-scrollbar-${axis}-thumb`}
        className="absolute pointer-events-auto rounded-full border border-bg bg-fg-muted"
        style={thumb}
        onPointerDown={(event) => {
          event.stopPropagation()
          if (event.button !== 0) {
            return
          }
          // No compatibility mouse events, no text selection and no focus move from a thumb press.
          event.preventDefault()
          dragRef.current = { pointerId: event.pointerId, at: horizontal ? event.clientX : event.clientY }
          capturePointer(event.currentTarget, event.pointerId)
        }}
        onPointerMove={(event) => {
          event.stopPropagation()
          const drag = dragRef.current
          if (drag === null || drag.pointerId !== event.pointerId) {
            return
          }
          const at = horizontal ? event.clientX : event.clientY
          dragRef.current = { ...drag, at }
          onDrag(at - drag.at)
        }}
        onPointerUp={end}
        onPointerCancel={end}
        onLostPointerCapture={(event) => {
          event.stopPropagation()
          dragRef.current = null
        }}
        onMouseDown={stop}
        onMouseMove={stop}
        onMouseUp={stop}
        onClick={stop}
        onDoubleClick={stop}
      />
    </div>
  )
}

const NO_SHOT_HINT = 'Select a shot first'

/** SWATCH_OPTIONS (MEU-86): each Named option shows its own colour with contrast-picked text. */
const SWATCH_OPTIONS = Object.entries(NAMED_COLOR_HEX).map(([name, hex]) => ({
  name,
  style: { backgroundColor: hex, color: contrastText(hex) },
}))

/** Native events already acted on by `handleViewKey` (the window and surface paths can both see one). */
const handledViewKeys = new WeakSet<Event>()

export function CaptureViewport({
  empty,
  shotId = null,
  hasSelection = true,
  overlayReady,
  actions,
  confirmStrip,
  emptyState,
  statusLine,
  imageUrl,
  imageWidth = 0,
  imageHeight = 0,
  hasAnnotated = false,
  viewVariant = 'original',
  tool,
  color,
  stroke,
  fontSize = '16',
  textBg = '',
  blockSize = '10',
  redactMode = 'solid',
  annotations,
  preview = null,
  selectedIndex = null,
  resizeCursor = null,
  canUndo,
  canRedo,
  textDraft,
  onTool,
  onColor,
  onColorPreview = () => undefined,
  onNamedColor = () => undefined,
  onStroke,
  onFontSize = () => undefined,
  onStrokePreview = () => undefined,
  onStrokeCommit = () => undefined,
  onStrokeCancel = () => undefined,
  onFontSizePreview = () => undefined,
  onFontSizeCommit = () => undefined,
  onFontSizeCancel = () => undefined,
  strokeEpoch = 0,
  fontSizeEpoch = 0,
  toolLocked = false,
  onToggleToolLock = () => undefined,
  boundedDrawLive = () => false,
  onTextBg = () => undefined,
  onTextBgPreview = () => undefined,
  onBlockSize = () => undefined,
  onBlockSizePreview = () => undefined,
  onBlockSizeCommit = () => undefined,
  onBlockSizeCancel = () => undefined,
  blockSizeEpoch = 0,
  arrowHead = 'end',
  boxShape = 'rect',
  onArrowHead = () => undefined,
  onBoxShape = () => undefined,
  stepSize = String(STEP_SIZE_DEFAULT),
  onStepSize = () => undefined,
  onStepSizePreview = () => undefined,
  onStepSizeCommit = () => undefined,
  onStepSizeCancel = () => undefined,
  stepSizeEpoch = 0,
  onRedactMode = () => undefined,
  onViewVariant = () => undefined,
  onUndo,
  onRedo,
  onPointer,
  onSurfacePointer,
  onSelectIndex = () => undefined,
  onRemoveMark = () => undefined,
  onHandleFocus = () => undefined,
  onSurfaceFocus = () => undefined,
  onEditorKey = () => undefined,
  onTextDraftChange,
  onTextCommit,
  onTextCancel,
  crop = null,
  cropBar,
  cropReason,
  cropDisabledReason,
  onToggleCrop = () => undefined,
}: CaptureViewportProps) {
  const pointerSession = useRef(false)
  // ALT_NO_MENU: an Alt draw ended with Alt still held, so its keyup must not open the menu bar.
  const altPendingRef = useRef(false)
  const surfaceRef = useRef<HTMLDivElement>(null)
  // SCROLL_BAR_LOOK: the bars' aria-controls names the surface by this id.
  const surfaceId = useId()
  // The measured surface box; VIEW_TRANSFORM reads it for the observables, handles and content box.
  const [frame, setFrame] = useState({ w: 0, h: 0 })
  const [zoom, setZoom] = useState<ZoomState>(FIT_STATE)
  const [zoomShot, setZoomShot] = useState(shotId)
  if (zoomShot !== shotId) {
    // ZOOM_RESET: a different shot (thumb switch, delete, first selection) starts at Fit.
    setZoomShot(shotId)
    setZoom(FIT_STATE)
  }
  const zoomRef = useRef<ZoomState>(zoom)
  zoomRef.current = zoom
  const panRef = useRef<{ pointerId: number; x: number; y: number } | null>(null)
  const spaceRef = useRef(false)
  const [spaceHeld, setSpaceHeld] = useState(false)
  const [panning, setPanning] = useState(false)
  const wheelAccRef = useRef(WHEEL_IDLE)
  const useSurface = onSurfacePointer !== undefined
  const showVectors = viewVariant === 'original'
  const selected = selectedIndex !== null ? (annotations[selectedIndex] ?? null) : null
  const showArrowHandles = showVectors && selected?.type === 'arrow'
  // TEXT_REEDIT: the mark under an edit draft has no handles.
  const showBodyHandle =
    showVectors && selected !== null && selected.type !== 'arrow' && textDraft?.editIndex !== selectedIndex
  const options = optionGroups(tool, selected, redactMode)
  const shapeControl = shapeOption(tool, selected)
  // CROP_ENTRY: why the Crop button is disabled, if it is.
  const cropOff = hasSelection ? cropDisabledReason : NO_SHOT_HINT
  // SCRUB_BASE: an invalid field scrubs from the applicable selected mark, else the default.
  const strokeBase = selected !== null && (selected.type === 'arrow' || selected.type === 'rect') ? selected.stroke_width : 3
  const fontSizeBase = selected?.type === 'text' ? selected.font_size : 16
  const blockBase = selected?.type === 'pixelate' ? selected.block_size : PIXELATE_BLOCK_DEFAULT
  const stepSizeBase = selected?.type === 'step' ? selected.size : STEP_SIZE_DEFAULT
  const scrubTarget = selectedIndex ?? '-'
  const imageBox = { w: imageWidth, h: imageHeight }
  const view = viewTransform(frame, imageBox, zoom)
  // SCROLL_BAR_GEOMETRY (MEU-167): a bar on each axis where the zoomed image is longer than the frame.
  const bars = scrollBars(frame, imageBox, zoom)
  const fitView = viewTransform(frame, imageBox, FIT_STATE)
  const handleRadius = view !== null ? HANDLE_RADIUS_CSS / view.s : HANDLE_RADIUS_CSS
  // RESIZE_HANDLES: `selected` is the painted list's mark, so the squares follow the live preview.
  const resizeSide = view !== null ? RESIZE_HANDLE_CSS / view.s : RESIZE_HANDLE_CSS
  const resizePoints =
    showBodyHandle && textDraft === null && selected !== null
      ? isBoxMark(selected)
        ? (Object.entries(boxHandlePoints(selected)) as Array<[HandleId, ImagePoint]>)
        : selected.type === 'text'
          ? (Object.entries(textPlateHandlePoints(selected)) as Array<[HandleId, ImagePoint]>)
          : []
      : []
  const surfaceMounted = !empty && hasSelection
  const canZoomIn = hasSelection && fitView !== null && zoomStep(zoom, 'in', fitView.s) !== null
  const canZoomOut = hasSelection && fitView !== null && zoomStep(zoom, 'out', fitView.s) !== null
  const canFit = hasSelection && zoom.kind !== 'fit'
  const zoomReadout = zoom.kind === 'fit' ? 'Fit' : `${Math.round(zoom.scale * 100)}%`
  const bodyHandle = selected !== null && selected.type !== 'arrow' ? bodyHandleImagePoint(selected) : null
  const wellHold = useRef('#000000')
  if (/^#[0-9A-Fa-f]{6}$/.test(color)) {
    wellHold.current = color.toLowerCase()
  }
  const textBgHold = useRef('#ffffff')
  const textBgHex = normalizeHex(textBg) ?? hexForNamedColor(textBg)
  if (textBgHex !== null) {
    textBgHold.current = textBgHex.toLowerCase()
  }
  // COLOR_HEX (MEU-105): the hex field's own text while it is edited; null shows the current colour.
  const [hexDraft, setHexDraft] = useState<string | null>(null)
  function commitHexDraft(): void {
    const text = hexDraft
    setHexDraft(null)
    if (text === null) {
      return
    }
    const hex = normalizeHex(text)
    if (hex !== null) {
      onColor(hex)
    }
  }
  // COLOR_WELL, TEXT_BG_WELL: the native `change` commits once; React's onChange also fires on `input`.
  const wellCommits = useRef({ onColor, onTextBg })
  wellCommits.current = { onColor, onTextBg }
  const colorWellRef = useCallback((node: HTMLInputElement | null) => {
    if (node === null) {
      return undefined
    }
    const onNativeChange = (): void => {
      wellCommits.current.onColor(node.value)
    }
    node.addEventListener('change', onNativeChange)
    return () => {
      node.removeEventListener('change', onNativeChange)
    }
  }, [])
  const textBgWellRef = useCallback((node: HTMLInputElement | null) => {
    if (node === null) {
      return undefined
    }
    const onNativeChange = (): void => {
      wellCommits.current.onTextBg(node.value)
    }
    node.addEventListener('change', onNativeChange)
    return () => {
      node.removeEventListener('change', onNativeChange)
    }
  }, [])
  const namedMenuStyle = useG30Styles()
  const regionLayerRef = useRef<HTMLCanvasElement>(null)
  const [regionSource, setRegionSource] = useState<RegionSource | null>(null)
  const liveSource =
    regionSource !== null &&
    regionSource.url === imageUrl &&
    regionSource.width === imageWidth &&
    regionSource.height === imageHeight
      ? regionSource
      : null
  // REGION_PREVIEW input: the region marks of [...annotations, preview], in list order.
  const regionMarks = (preview !== null ? [...annotations, preview] : annotations).filter(isRegionMark)
  const regionKey = JSON.stringify(regionMarks)
  const showRegionLayer = showVectors && imageWidth > 0 && imageHeight > 0
  useEffect(() => {
    const canvas = regionLayerRef.current
    if (canvas === null || liveSource === null) {
      return
    }
    paintRegionLayer(canvas, liveSource, JSON.parse(regionKey) as Annotation[])
  }, [liveSource, regionKey, showRegionLayer])
  useLayoutEffect(() => {
    const host = surfaceRef.current
    if (host === null || imageWidth < 1 || imageHeight < 1) {
      return
    }
    const measure = (): void => {
      const box = host.getBoundingClientRect()
      if (box.width > 0 && box.height > 0 && Number.isFinite(box.width) && Number.isFinite(box.height)) {
        setFrame((prev) => (prev.w === box.width && prev.h === box.height ? prev : { w: box.width, h: box.height }))
      }
    }
    measure()
    if (typeof ResizeObserver !== 'function') {
      return
    }
    const observer = new ResizeObserver(measure)
    observer.observe(host)
    return () => {
      observer.disconnect()
    }
  }, [imageHeight, imageWidth, selectedIndex, showArrowHandles, showBodyHandle, shotId, surfaceMounted])

  /** The live container box and image box for a zoom or pan, or null when nothing can be mapped. */
  function liveFrame(): { container: { w: number; h: number }; box: DOMRect } | null {
    const host = surfaceRef.current
    if (host === null || !hasSelection) {
      return null
    }
    const box = host.getBoundingClientRect()
    return { container: { w: box.width, h: box.height }, box }
  }

  function commitZoom(next: ZoomState): void {
    zoomRef.current = next
    setZoom(next)
  }

  /** ZOOM_STEP about `anchor` (container CSS px), or about the container centre for buttons and keys. */
  function stepZoom(dir: ZoomDirection, anchor: { x: number; y: number } | null, count = 1): void {
    const live = liveFrame()
    const fit = live === null ? null : viewTransform(live.container, imageBox, FIT_STATE)
    if (live === null || fit === null) {
      return
    }
    const point = anchor ?? { x: live.container.w / 2, y: live.container.h / 2 }
    let next = zoomRef.current
    for (let i = 0; i < count; i += 1) {
      const scale = zoomStep(next, dir, fit.s)
      if (scale === null) {
        break
      }
      next = zoomAbout(next, point, scale, live.container, imageBox)
    }
    commitZoom(next)
  }

  /** PAN_GESTURES: move a scale view's offset through VIEW_TRANSFORM's clamp; a no-op at Fit. */
  function panBy(dx: number, dy: number): void {
    const live = liveFrame()
    const current = zoomRef.current
    if (live === null || current.kind !== 'scale') {
      return
    }
    const now = viewTransform(live.container, imageBox, current)
    const placed =
      now === null
        ? null
        : viewTransform(live.container, imageBox, { kind: 'scale', scale: now.s, ox: now.ox + dx, oy: now.oy + dy })
    if (placed !== null) {
      commitZoom({ kind: 'scale', scale: placed.s, ox: placed.ox, oy: placed.oy })
    }
  }

  /** SCROLL_BAR_DRAG: a thumb drag of `pixels` on `axis` pans through `panBy`, so the clamp is the pan's own. */
  function dragScrollThumb(axis: 'x' | 'y', pixels: number): void {
    const live = liveFrame()
    if (live === null) {
      return
    }
    const bar = scrollBars(live.container, imageBox, zoomRef.current)[axis]
    if (bar === null) {
      return
    }
    const change = thumbDragToPan(pixels, bar)
    if (axis === 'x') {
      panBy(change, 0)
    } else {
      panBy(0, change)
    }
  }

  function startPan(event: React.PointerEvent<HTMLDivElement>): boolean {
    if (!(event.button === 1 || (event.button === 0 && spaceRef.current))) {
      return false
    }
    // Middle-button down would otherwise start Chromium's autoscroll on the page's scroll container.
    event.preventDefault()
    panRef.current = { pointerId: event.pointerId, x: event.clientX, y: event.clientY }
    setPanning(true)
    capturePointer(event.currentTarget, event.pointerId)
    return true
  }

  function endPan(target: HTMLElement | null): void {
    const pan = panRef.current
    if (pan === null) {
      return
    }
    panRef.current = null
    setPanning(false)
    if (target !== null) {
      releasePointer(target, pan.pointerId)
    }
  }

  /** ZOOM_KEY_SCOPE: a shot is selected, focus is not in text entry and no confirm strip is open. */
  function zoomKeysInScope(): boolean {
    if (!hasSelection) {
      return false
    }
    const active = document.activeElement
    if (active instanceof HTMLElement && (active.matches('input, textarea, select') || active.isContentEditable)) {
      return false
    }
    return document.querySelector('[data-testid="capture-confirm-strip"]') === null
  }

  /** Space arms pan only from the surface, the body or a non-control element inside the viewport. */
  function spaceArmable(): boolean {
    const active = document.activeElement
    if (active === null || active === document.body || active === surfaceRef.current) {
      return true
    }
    // HANDLE_LAYER: a focused arrow handle is a control (role="button"), so Space never arms pan from it.
    return (
      active.closest('[data-testid="capture-viewport"]') !== null &&
      !active.matches('button, input, select, textarea, [role="button"]')
    )
  }

  /** The single owner of the zoom keys and the Space pan arm; one native event acts at most once. */
  function handleViewKey(event: KeyboardEvent): void {
    if (handledViewKeys.has(event)) {
      return
    }
    if (event.type === 'keyup') {
      if (event.key === ' ' && spaceRef.current) {
        handledViewKeys.add(event)
        spaceRef.current = false
        setSpaceHeld(false)
      }
      return
    }
    if (event.type !== 'keydown' || event.isComposing || !zoomKeysInScope()) {
      return
    }
    const action = zoomKeyAction(event)
    if (action !== null) {
      handledViewKeys.add(event)
      event.preventDefault()
      if (action === 'fit') {
        commitZoom(FIT_STATE)
      } else {
        stepZoom(action, null)
      }
      return
    }
    if (event.key === ' ' && !event.ctrlKey && !event.metaKey && !event.altKey && spaceArmable()) {
      handledViewKeys.add(event)
      event.preventDefault()
      if (!spaceRef.current) {
        spaceRef.current = true
        setSpaceHeld(true)
      }
    }
  }

  function handleWheel(event: WheelEvent): void {
    event.preventDefault()
    const { steps, acc } = wheelSteps(wheelAccRef.current, event)
    wheelAccRef.current = acc
    const live = liveFrame()
    if (steps === 0 || live === null) {
      return
    }
    stepZoom(steps > 0 ? 'in' : 'out', { x: event.clientX - live.box.left, y: event.clientY - live.box.top }, Math.abs(steps))
  }

  const viewKeyRef = useRef(handleViewKey)
  viewKeyRef.current = handleViewKey
  const wheelRef = useRef(handleWheel)
  wheelRef.current = handleWheel
  useEffect(() => {
    const onKey = (event: KeyboardEvent): void => {
      viewKeyRef.current(event)
    }
    const onBlur = (): void => {
      spaceRef.current = false
      setSpaceHeld(false)
    }
    window.addEventListener('keydown', onKey)
    window.addEventListener('keyup', onKey)
    window.addEventListener('blur', onBlur)
    return () => {
      window.removeEventListener('keydown', onKey)
      window.removeEventListener('keyup', onKey)
      window.removeEventListener('blur', onBlur)
    }
  }, [])
  useEffect(() => {
    const host = surfaceRef.current
    if (!surfaceMounted || host === null) {
      return
    }
    // React's onWheel is passive, so it cannot prevent the page scroll or zoom; register natively.
    const onWheel = (event: WheelEvent): void => {
      wheelRef.current(event)
    }
    host.addEventListener('wheel', onWheel, { passive: false })
    return () => {
      host.removeEventListener('wheel', onWheel)
    }
  }, [surfaceMounted])
  const draftStyle = (() => {
    if (textDraft === null) {
      return undefined
    }
    const host = surfaceRef.current
    const box = host !== null ? host.getBoundingClientRect() : { width: 0, height: 0 }
    const live = viewTransform({ w: box.width, h: box.height }, imageBox, zoom)
    const mapped = live === null ? { x: 0, y: 0 } : mapImageToPointerWithView(textDraft, 0, 0, live)
    return { left: mapped.x, top: mapped.y }
  })()
  // TEXT_DRAFT_STYLE (MEU-105): the draft shows the colour, size and background its mark will take.
  const draftColor = normalizeHex(color) ?? undefined
  const draftBg = textBgHex ?? undefined
  const draftFontPx = (parsePositiveInt(fontSize) ?? fontSizeBase) * (view?.s ?? 1)
  const draftTextStyle =
    draftStyle === undefined
      ? undefined
      : { ...draftStyle, color: draftColor, fontSize: `${draftFontPx}px`, backgroundColor: draftBg }
  const contentStyle =
    view !== null
      ? { left: view.ox, top: view.oy, width: imageWidth * view.s, height: imageHeight * view.s }
      : { left: 0, top: 0, width: '100%', height: '100%' }
  const surfaceCursor = panning
    ? ' cursor-grabbing'
    : spaceHeld
      ? ' cursor-grab'
      : crop !== null
        ? cropCursorClass(crop.cursor)
        : showVectors && resizeCursor !== null && resizePoints.length > 0
          ? RESIZE_CURSOR_CLASS[cursorForHandle(resizeCursor)]
          : ''
  const painted = (() => {
    const rows = annotations
      .map((ann, index) => ({ ann, index }))
      .filter((row) => row.index !== textDraft?.editIndex)
    if (selectedIndex === null) {
      return rows
    }
    return [
      ...rows.filter((row) => row.index === selectedIndex),
      ...rows.filter((row) => row.index !== selectedIndex),
    ]
  })()
  const visibleMarks = preview !== null ? [...painted, { ann: preview, index: -1 }] : painted

  function emitSurface(
    event: { currentTarget: EventTarget | null; clientX: number; clientY: number; shiftKey?: boolean; altKey?: boolean },
    phase: SurfacePointer['phase'],
    pointerId: number,
  ): void {
    const payload = surfaceFromDom(event, phase, pointerId, imageWidth, imageHeight, zoomRef.current)
    if (payload !== null) {
      onSurfacePointer?.(payload)
    }
  }

  return (
    <div className="flex min-w-0 flex-col gap-1 flex-1 min-h-[16rem]" data-testid="capture-viewport">
      <div className="flex flex-col gap-1 shrink-0" data-testid="capture-chrome">
        <div
          className="flex flex-nowrap items-center gap-1 overflow-x-auto min-h-9"
          data-testid="capture-chrome-tools"
          onClick={(event) => {
            // A-4: a mouse click (detail > 0) on a toolbar button hands focus to the surface, so Space can
            // arm pan next. Keyboard activation (detail 0) keeps focus on the button for keyboard users.
            if (event.detail > 0 && event.target instanceof Element && event.target.closest('button') !== null) {
              surfaceRef.current?.focus({ preventScroll: true })
            }
          }}
        >
          <div role="group" aria-label="Annotation tool" className="flex shrink-0 items-center gap-0.5 rounded-[var(--radius-control)] border border-border p-0.5">
            <ToolbarIconButton
              spec={TOOLBAR_BUTTONS['capture-tool-select']}
              id="capture-tool-select"
              variant={toolVariant(tool === 'select')}
              pressed={tool === 'select'}
              disabled={!hasSelection || cropReason !== undefined}
              reason={cropReason ?? (hasSelection ? undefined : NO_SHOT_HINT)}
              shortcut={TOOL_LETTERS.select}
              onClick={() => onTool('select')}
            />
            <ToolbarIconButton
              spec={TOOLBAR_BUTTONS['capture-tool-arrow']}
              id="capture-tool-arrow"
              variant={toolVariant(tool === 'arrow')}
              pressed={tool === 'arrow'}
              disabled={!hasSelection || cropReason !== undefined}
              reason={cropReason ?? (hasSelection ? undefined : NO_SHOT_HINT)}
              shortcut={TOOL_LETTERS.arrow}
              onClick={() => onTool('arrow')}
            />
            <ToolbarIconButton
              spec={TOOLBAR_BUTTONS['capture-tool-box']}
              id="capture-tool-box"
              variant={toolVariant(tool === 'box')}
              pressed={tool === 'box'}
              disabled={!hasSelection || cropReason !== undefined}
              reason={cropReason ?? (hasSelection ? undefined : NO_SHOT_HINT)}
              shortcut={TOOL_LETTERS.box}
              onClick={() => onTool('box')}
            />
            <ToolbarIconButton
              spec={TOOLBAR_BUTTONS['capture-tool-highlight']}
              id="capture-tool-highlight"
              variant={toolVariant(tool === 'highlight')}
              pressed={tool === 'highlight'}
              disabled={!hasSelection || cropReason !== undefined}
              reason={cropReason ?? (hasSelection ? undefined : NO_SHOT_HINT)}
              shortcut={TOOL_LETTERS.highlight}
              onClick={() => onTool('highlight')}
            />
            <ToolbarIconButton
              spec={TOOLBAR_BUTTONS['capture-tool-text']}
              id="capture-tool-text"
              variant={toolVariant(tool === 'text')}
              pressed={tool === 'text'}
              disabled={!hasSelection || cropReason !== undefined}
              reason={cropReason ?? (hasSelection ? undefined : NO_SHOT_HINT)}
              shortcut={TOOL_LETTERS.text}
              onClick={() => onTool('text')}
            />
            <ToolbarIconButton
              spec={TOOLBAR_BUTTONS['capture-tool-step']}
              id="capture-tool-step"
              variant={toolVariant(tool === 'step')}
              pressed={tool === 'step'}
              disabled={!hasSelection || cropReason !== undefined}
              reason={cropReason ?? (hasSelection ? undefined : NO_SHOT_HINT)}
              onClick={() => onTool('step')}
            />
            <ToolbarIconButton
              spec={TOOLBAR_BUTTONS['capture-tool-redact']}
              id="capture-tool-redact"
              variant={toolVariant(tool === 'redact')}
              pressed={tool === 'redact'}
              disabled={!hasSelection || cropReason !== undefined}
              reason={cropReason ?? (hasSelection ? undefined : NO_SHOT_HINT)}
              shortcut={TOOL_LETTERS.redact}
              onClick={() => onTool('redact')}
            />
            <ToolbarIconButton
              spec={TOOLBAR_BUTTONS['capture-tool-eraser']}
              id="capture-tool-eraser"
              variant={toolVariant(tool === 'eraser')}
              pressed={tool === 'eraser'}
              disabled={!hasSelection || cropReason !== undefined}
              reason={cropReason ?? (hasSelection ? undefined : NO_SHOT_HINT)}
              shortcut={TOOL_LETTERS.eraser}
              onClick={() => onTool('eraser')}
            />
          </div>
          {/* TOOL_LOCK: enabled with or without a shot; it changes no mark, tool or selection. */}
          <ToolbarIconButton
            spec={TOOLBAR_BUTTONS['capture-tool-lock']}
            id="capture-tool-lock"
            variant={toolVariant(toolLocked)}
            pressed={toolLocked}
            disabled={cropReason !== undefined}
            reason={cropReason}
            onClick={onToggleToolLock}
          />
          {/* CROP_ENTRY (MEU-131, D-508): after the lock, outside the tool group; the page opens and closes it. */}
          <ToolbarIconButton
            spec={TOOLBAR_BUTTONS['capture-tool-crop']}
            id="capture-tool-crop"
            variant={toolVariant(tool === 'crop')}
            pressed={tool === 'crop'}
            disabled={cropOff !== undefined}
            reason={cropOff}
            shortcut={TOOL_LETTERS.crop}
            onClick={onToggleCrop}
          />
          <div role="group" aria-label="History" className="flex shrink-0 items-center gap-0.5">
            <ToolbarIconButton
              spec={TOOLBAR_BUTTONS['capture-undo']}
              id="capture-undo"
              variant="ghost"
              disabled={!canUndo || cropReason !== undefined}
              reason={cropReason}
              shortcut="Ctrl+Z"
              onClick={onUndo}
            />
            <ToolbarIconButton
              spec={TOOLBAR_BUTTONS['capture-redo']}
              id="capture-redo"
              variant="ghost"
              disabled={!canRedo || cropReason !== undefined}
              reason={cropReason}
              shortcut="Ctrl+Y"
              onClick={onRedo}
            />
          </div>
          <div role="group" aria-label="View" className="flex shrink-0 items-center gap-0.5">
            <ToolbarIconButton
              spec={TOOLBAR_BUTTONS['capture-view-original']}
              id="capture-view-original"
              variant={toolVariant(viewVariant === 'original')}
              pressed={viewVariant === 'original'}
              onClick={() => onViewVariant('original')}
            />
            <ToolbarIconButton
              spec={TOOLBAR_BUTTONS['capture-view-annotated']}
              id="capture-view-annotated"
              variant={toolVariant(viewVariant === 'annotated')}
              pressed={viewVariant === 'annotated'}
              disabled={!hasAnnotated || cropReason !== undefined}
              reason={cropReason}
              onClick={() => onViewVariant('annotated')}
            />
          </div>
          <div role="group" aria-label="Zoom" className="flex shrink-0 items-center gap-0.5">
            <ToolbarIconButton
              spec={TOOLBAR_BUTTONS['capture-zoom-out']}
              id="capture-zoom-out"
              variant="ghost"
              disabled={!canZoomOut}
              reason={hasSelection ? undefined : NO_SHOT_HINT}
              onClick={() => stepZoom('out', null)}
            />
            <span
              data-testid="capture-zoom-level"
              aria-live="polite"
              title={ZOOM_PAN_HINT}
              className="min-w-[3.5rem] text-center text-xs tabular-nums text-fg-muted"
            >
              {zoomReadout}
            </span>
            <ToolbarIconButton
              spec={TOOLBAR_BUTTONS['capture-zoom-in']}
              id="capture-zoom-in"
              variant="ghost"
              disabled={!canZoomIn}
              reason={hasSelection ? undefined : NO_SHOT_HINT}
              onClick={() => stepZoom('in', null)}
            />
            <ToolbarIconButton
              spec={TOOLBAR_BUTTONS['capture-zoom-fit']}
              id="capture-zoom-fit"
              variant="ghost"
              disabled={!canFit}
              reason={hasSelection ? undefined : NO_SHOT_HINT}
              onClick={() => commitZoom(FIT_STATE)}
            />
          </div>
        </div>
        {/* OPTIONS_ROW: only the controls the active tool or selected mark consumes (OPTIONS_BY_TOOL). */}
        <div className="flex flex-nowrap items-center gap-1 overflow-x-auto min-h-9" data-testid="capture-chrome-options">
          {cropBar}
          {options.includes('color') ? (
            <span role="group" aria-label="Color" className="flex shrink-0 items-center gap-1">
              <span className="text-xs text-fg-muted">Color</span>
              <input
                ref={colorWellRef}
                data-testid="capture-color-well"
                type="color"
                value={wellHold.current}
                onInput={(event) => {
                  onColorPreview(event.currentTarget.value)
                }}
                onChange={() => undefined}
              />
              <input
                data-testid="capture-color"
                className="w-24 font-mono"
                value={hexDraft ?? color}
                onChange={(event) => {
                  setHexDraft(event.target.value)
                }}
                onKeyDown={(event) => {
                  if (event.key === 'Enter') {
                    event.preventDefault()
                    commitHexDraft()
                  } else if (event.key === 'Escape') {
                    setHexDraft(null)
                  }
                }}
                onBlur={commitHexDraft}
              />
              <select
                data-testid="capture-named-color"
                value=""
                style={namedMenuStyle}
                onChange={(event) => {
                  const name = event.target.value
                  event.currentTarget.value = ''
                  onNamedColor(name)
                }}
              >
                <option value="" style={namedMenuStyle}>
                  Named
                </option>
                {SWATCH_OPTIONS.map(({ name, style }) => (
                  <option key={name} value={name} style={style}>
                    {name}
                  </option>
                ))}
              </select>
            </span>
          ) : null}
          {options.includes('text') ? (
            <span className="flex shrink-0 items-center gap-1">
              <CaptureScrubField
                key="capture-font-size"
                id="capture-font-size"
                label="Size"
                ariaLabel="Font size"
                inputClassName="w-14 shrink-0"
                value={fontSize}
                fallback={fontSizeBase}
                max={FONT_SCRUB_MAX}
                onChange={onFontSize}
                onPreview={onFontSizePreview}
                onCommit={onFontSizeCommit}
                onCancel={onFontSizeCancel}
                resetKey={`${fontSizeEpoch}:${scrubTarget}`}
              />
              <label className="flex shrink-0 items-center gap-1 text-sm" title="Text background">
                Bg
                <input
                  key="capture-text-bg"
                  ref={textBgWellRef}
                  data-testid="capture-text-bg"
                  type="color"
                  aria-label="Text background"
                  title="Text background"
                  className="h-7 w-8 cursor-pointer bg-transparent p-0"
                  value={textBgHold.current}
                  onInput={(event) => {
                    onTextBgPreview(event.currentTarget.value)
                  }}
                  onChange={() => undefined}
                />
              </label>
              <Button
                size="sm"
                variant="ghost"
                data-testid="capture-text-bg-clear"
                aria-label="Clear text background"
                title="Clear text background"
                disabled={textBg.trim().length === 0}
                onClick={() => onTextBg('')}
              >
                Clear
              </Button>
            </span>
          ) : null}
          {options.includes('stroke') ? (
            <CaptureScrubField
              key="capture-stroke"
              id="capture-stroke"
              label="Stroke"
              ariaLabel="Stroke width"
              inputClassName="w-14 shrink-0 text-sm text-fg"
              value={stroke}
              fallback={strokeBase}
              max={STROKE_SCRUB_MAX}
              onChange={onStroke}
              onPreview={onStrokePreview}
              onCommit={onStrokeCommit}
              onCancel={onStrokeCancel}
              resetKey={`${strokeEpoch}:${scrubTarget}`}
            />
          ) : null}
          {options.includes('size') ? (
            <CaptureScrubField
              key="capture-step-size"
              id="capture-step-size"
              label="Size"
              ariaLabel="Step size"
              inputClassName="w-14 shrink-0 text-sm text-fg"
              value={stepSize}
              fallback={stepSizeBase}
              min={STEP_SIZE_MIN}
              max={STEP_SIZE_MAX}
              onChange={onStepSize}
              onPreview={onStepSizePreview}
              onCommit={onStepSizeCommit}
              onCancel={onStepSizeCancel}
              resetKey={`${stepSizeEpoch}:${scrubTarget}`}
            />
          ) : null}
          {shapeControl === 'head' ? (
            <SegmentedControl
              key="capture-arrow-head"
              name="capture-arrow-head"
              label="Head"
              testId="capture-arrow-head"
              className="shrink-0"
              size="sm"
              value={arrowHead}
              options={ARROW_HEAD_OPTIONS}
              onValueChange={(value) => {
                onArrowHead(value === 'none' ? 'none' : value === 'both' ? 'both' : 'end')
              }}
            />
          ) : null}
          {shapeControl === 'shape' ? (
            <SegmentedControl
              key="capture-box-shape"
              name="capture-box-shape"
              label="Shape"
              testId="capture-box-shape"
              className="shrink-0"
              size="sm"
              value={boxShape}
              options={BOX_SHAPE_OPTIONS}
              onValueChange={(value) => {
                onBoxShape(value === 'ellipse' ? 'ellipse' : 'rect')
              }}
            />
          ) : null}
          {options.includes('mode') ? (
            <SegmentedControl
              key="capture-redact-mode"
              name="capture-redact-mode"
              label="Redact mode"
              testId="capture-redact-mode"
              className="shrink-0"
              size="sm"
              value={redactMode}
              options={REDACT_MODE_OPTIONS}
              onValueChange={(value) => {
                onRedactMode(value === 'pixelate' ? 'pixelate' : 'solid')
              }}
            />
          ) : null}
          {options.includes('block') ? (
            <span key="capture-block-size" role="group" aria-label="Block size" className="flex shrink-0 items-center">
              <CaptureScrubField
                id="capture-block-size"
                label="Block size"
                ariaLabel="Block size"
                inputClassName="w-16 shrink-0 text-sm text-fg"
                value={blockSize}
                fallback={blockBase}
                min={PIXELATE_BLOCK_MIN}
                max={PIXELATE_BLOCK_MAX}
                onChange={onBlockSize}
                onPreview={onBlockSizePreview}
                onCommit={onBlockSizeCommit}
                onCancel={onBlockSizeCancel}
                resetKey={`${blockSizeEpoch}:${scrubTarget}`}
              />
            </span>
          ) : null}
        </div>
      {/* MARKS_ROW_LAYOUT: only the chip list scrolls; the row and the action slot never do. */}
      <div className="flex flex-nowrap items-center gap-1 shrink-0 min-h-9" data-testid="capture-chrome-marks">
        <div data-testid="capture-mark-list" className="flex min-w-0 flex-1 items-center gap-1 overflow-x-auto">
          {annotations.map((ann, index) => (
            <Button
              key={`${ann.type}-${index}`}
              size="sm"
              variant={toolVariant(index === selectedIndex)}
              aria-pressed={index === selectedIndex}
              onClick={() => onSelectIndex(index)}
            >
              {markLabel(ann, index, annotations)}
            </Button>
          ))}
        </div>
        {/* ACTION_ORDER: Remove mark (while a mark is selected), then the per-shot actions the page owns. */}
        <div className="ml-auto flex shrink-0 items-center gap-1 pl-2">
          {selectedIndex !== null ? (
            <ToolbarIconButton
              spec={ACTION_BUTTONS['capture-remove-mark']}
              id="capture-remove-mark"
              variant="ghost"
              onClick={onRemoveMark}
            />
          ) : null}
          {actions}
        </div>
      </div>
      </div>
      {confirmStrip}
      {empty ? (
        emptyState ?? <p className="text-fg-muted">Select a shot from the filmstrip.</p>
      ) : !hasSelection ? (
        <p className="flex min-h-[200px] flex-1 items-center justify-center text-fg-muted">Select a shot from the filmstrip.</p>
      ) : (
        <div
          ref={surfaceRef}
          id={surfaceId}
          className={`flex-1 min-h-[200px] relative overflow-hidden bg-bg-elevated${surfaceCursor}`}
          data-testid="capture-draw-surface"
          data-overlay-ready={overlayReady === undefined ? undefined : overlayReady ? 'true' : 'false'}
          data-zoom-kind={zoom.kind}
          data-zoom-scale={view?.s.toFixed(4)}
          data-zoom-ox={view?.ox.toFixed(4)}
          data-zoom-oy={view?.oy.toFixed(4)}
          tabIndex={0}
          onFocus={(event) => {
            // Focus moving onto a handle bubbles here too; only the surface itself resets the nudge target.
            if (event.target === event.currentTarget) {
              onSurfaceFocus()
            }
          }}
          onKeyDown={(event) => {
            if (event.key === 'Alt' && (boundedDrawLive() || altPendingRef.current)) {
              event.preventDefault()
            }
            // The view keys run before stopPropagation, which keeps the event from the window listener.
            handleViewKey(event.nativeEvent)
            onEditorKey(event.nativeEvent)
            // CAPTURE_CHORD_BUBBLE: a registry chord still reaches the shell's window handler.
            if (!isRegistryChord(event.nativeEvent)) {
              event.stopPropagation()
            }
          }}
          onKeyUp={(event) => {
            if (event.key === 'Alt') {
              if (boundedDrawLive() || altPendingRef.current) {
                event.preventDefault()
              }
              altPendingRef.current = false
            }
            handleViewKey(event.nativeEvent)
          }}
          onPointerDown={(event) => {
            if (startPan(event)) {
              return
            }
            if (viewVariant !== 'original') {
              return
            }
            pointerSession.current = true
            capturePointer(event.currentTarget, event.pointerId)
            if (useSurface) {
              emitSurface(event, 'down', event.pointerId)
              return
            }
            const mapped = mapEvent(event, imageWidth, imageHeight, zoomRef.current)
            if (mapped !== null) {
              onPointer(mapped.x, mapped.y, 'down')
            }
          }}
          onPointerMove={(event) => {
            const pan = panRef.current
            if (pan !== null) {
              panBy(event.clientX - pan.x, event.clientY - pan.y)
              panRef.current = { ...pan, x: event.clientX, y: event.clientY }
              return
            }
            if (viewVariant !== 'original' || !useSurface) {
              return
            }
            emitSurface(event, 'move', event.pointerId)
          }}
          onPointerUp={(event) => {
            if (panRef.current !== null) {
              endPan(event.currentTarget)
              return
            }
            if (viewVariant !== 'original') {
              return
            }
            if (useSurface) {
              const altDraw = boundedDrawLive() && event.altKey
              emitSurface(event, 'up', event.pointerId)
              if (altDraw) {
                altPendingRef.current = true
              }
            } else {
              const clamped = mapEventClamped(event, imageWidth, imageHeight, zoomRef.current)
              if (clamped !== null) {
                onPointer(clamped.x, clamped.y, 'up')
              }
            }
            releasePointer(event.currentTarget, event.pointerId)
            pointerSession.current = false
          }}
          onPointerCancel={(event) => {
            if (panRef.current !== null) {
              endPan(event.currentTarget)
              return
            }
            if (useSurface) {
              const altDraw = boundedDrawLive() && event.altKey
              emitSurface(event, 'cancel', event.pointerId)
              if (altDraw) {
                altPendingRef.current = true
              }
            }
            pointerSession.current = false
          }}
          onLostPointerCapture={() => {
            if (panRef.current !== null) {
              endPan(null)
              return
            }
            if (useSurface) {
              emitSurface(
                { currentTarget: document.querySelector('[data-testid="capture-draw-surface"]'), clientX: 0, clientY: 0 },
                'cancel',
                0,
              )
            }
            pointerSession.current = false
          }}
          onDoubleClick={(event) => {
            // TEXT_REEDIT: the page decides whether the double-click lands on a text mark.
            if (viewVariant !== 'original' || !useSurface || panRef.current !== null || spaceRef.current) {
              return
            }
            emitSurface(event, 'dblclick', 1)
          }}
          onMouseDown={(event) => {
            if (event.button === 1) {
              // No middle-click autoscroll on the page's scroll container (PAN_GESTURES).
              event.preventDefault()
              return
            }
            if (viewVariant !== 'original' || pointerSession.current || panRef.current !== null || spaceRef.current) {
              return
            }
            if (event.nativeEvent.type.startsWith('pointer')) {
              return
            }
            if (useSurface) {
              emitSurface(event, 'down', 1)
              return
            }
            const mapped = mapEvent(event, imageWidth, imageHeight, zoomRef.current)
            if (mapped !== null) {
              onPointer(mapped.x, mapped.y, 'down')
            }
          }}
          onMouseMove={(event) => {
            if (viewVariant !== 'original' || pointerSession.current || !useSurface || panRef.current !== null || spaceRef.current) {
              return
            }
            if (event.nativeEvent.type.startsWith('pointer')) {
              return
            }
            emitSurface(event, 'move', 1)
          }}
          onMouseUp={(event) => {
            if (viewVariant !== 'original' || pointerSession.current || event.button === 1 || panRef.current !== null || spaceRef.current) {
              return
            }
            if (event.nativeEvent.type.startsWith('pointer')) {
              return
            }
            if (useSurface) {
              emitSurface(event, 'up', 1)
              return
            }
            const clamped = mapEventClamped(event, imageWidth, imageHeight, zoomRef.current)
            if (clamped !== null) {
              onPointer(clamped.x, clamped.y, 'up')
            }
          }}
        >
          <div data-testid="capture-zoom-content" className="absolute pointer-events-none" style={contentStyle}>
          {imageUrl !== null ? (
            <img
              data-testid="capture-viewport-image"
              src={imageUrl}
              alt=""
              draggable={false}
              onLoad={(event) => {
                // REGION_SOURCE: only the Original image feeds the region layer.
                if (viewVariant === 'original' && imageUrl !== null) {
                  setRegionSource(readRegionSource(event.currentTarget, imageUrl))
                }
              }}
              onDragStart={(event) => {
                event.preventDefault()
              }}
              className="absolute inset-0 w-full h-full object-contain select-none pointer-events-none"
            />
          ) : null}
          {showRegionLayer ? (
            <canvas
              ref={regionLayerRef}
              data-testid="capture-region-layer"
              aria-hidden="true"
              width={imageWidth}
              height={imageHeight}
              className="absolute inset-0 w-full h-full pointer-events-none"
            />
          ) : null}
          <svg
            className="absolute inset-0 w-full h-full pointer-events-none"
            aria-hidden="true"
            viewBox={`0 0 ${Math.max(1, imageWidth)} ${Math.max(1, imageHeight)}`}
            preserveAspectRatio="xMidYMid meet"
          >
            {showVectors
              ? visibleMarks.map((row) => (
                  <AnnotationMark key={row.index === -1 ? 'preview' : row.index} ann={row.ann} />
                ))
              : null}
            {showBodyHandle && bodyHandle !== null ? (
              <circle
                data-testid="capture-handle-body"
                cx={bodyHandle.x}
                cy={bodyHandle.y}
                r={handleRadius}
                fill="var(--color-accent)"
                stroke="var(--color-bg)"
                strokeWidth={1}
                vectorEffect="non-scaling-stroke"
              />
            ) : null}
            {resizePoints.map(([id, point]) => (
              <rect
                key={id}
                data-testid={`capture-handle-resize-${id}`}
                data-handle={id}
                x={point.x - resizeSide / 2}
                y={point.y - resizeSide / 2}
                width={resizeSide}
                height={resizeSide}
                fill="var(--color-bg)"
                stroke="var(--color-accent)"
                strokeWidth={1}
                vectorEffect="non-scaling-stroke"
              />
            ))}
          </svg>
          {/* HANDLE_LAYER: the arrow ends as focusable controls, outside the aria-hidden marks svg but in the same
              zoom box. A grab still goes through the surface's hit test; keydown bubbles to the surface's handler. */}
          {showArrowHandles && selected?.type === 'arrow' ? (
            <svg
              data-testid="capture-handle-layer"
              className="absolute inset-0 w-full h-full pointer-events-none"
              viewBox={`0 0 ${Math.max(1, imageWidth)} ${Math.max(1, imageHeight)}`}
              preserveAspectRatio="xMidYMid meet"
            >
              {(
                [
                  ['from', 'capture-handle-from', 'Arrow tail', selected.from],
                  ['to', 'capture-handle-to', 'Arrow head', selected.to],
                ] as const
              ).map(([end, id, label, point]) => (
                <circle
                  key={id}
                  data-testid={id}
                  role="button"
                  tabIndex={0}
                  aria-label={label}
                  className="pointer-events-none outline-none focus-visible:stroke-[var(--color-fg)] focus-visible:[stroke-width:2]"
                  cx={point[0]}
                  cy={point[1]}
                  r={handleRadius}
                  fill="var(--color-accent)"
                  stroke="var(--color-bg)"
                  strokeWidth={1}
                  vectorEffect="non-scaling-stroke"
                  onFocus={() => {
                    onHandleFocus(end)
                  }}
                />
              ))}
            </svg>
          ) : null}
          {crop !== null && showVectors ? (
            <CaptureCropOverlay
              box={crop.box}
              dragging={crop.dragging}
              imageWidth={imageWidth}
              imageHeight={imageHeight}
              scale={view?.s ?? 1}
            />
          ) : null}
          </div>
          {textDraft !== null && showVectors ? (
            <div
              id="capture-text-draft-hint"
              data-testid="capture-text-draft-hint"
              className="absolute z-10 pointer-events-none whitespace-nowrap rounded bg-bg px-1 text-xs text-fg-muted"
              style={draftStyle === undefined ? undefined : { ...draftStyle, transform: 'translateY(calc(-100% - 2px))' }}
            >
              Enter to finish, Shift+Enter for a new line, Esc to cancel
            </div>
          ) : null}
          {textDraft !== null && showVectors ? (
            <textarea
              data-testid="capture-text-draft"
              className="absolute z-10 bg-bg border border-border px-1 resize-none"
              style={draftTextStyle}
              value={textDraft.value}
              rows={Math.max(1, textLines(textDraft.value).length)}
              wrap="off"
              spellCheck={false}
              aria-describedby="capture-text-draft-hint"
              autoFocus
              onPointerDown={(event) => {
                event.stopPropagation()
              }}
              onMouseDown={(event) => {
                event.stopPropagation()
              }}
              onChange={(event) => {
                onTextDraftChange(event.target.value)
              }}
              onKeyDown={(event) => {
                if (event.nativeEvent.isComposing) {
                  return
                }
                if (event.key === 'Enter' && !event.shiftKey) {
                  event.preventDefault()
                  onTextCommit()
                }
                if (event.key === 'Escape') {
                  event.preventDefault()
                  onTextCancel()
                }
              }}
            />
          ) : null}
          {bars.x !== null ? (
            <ViewportScrollBar
              axis="x"
              bar={bars.x}
              controls={surfaceId}
              onDrag={(pixels) => {
                dragScrollThumb('x', pixels)
              }}
            />
          ) : null}
          {bars.y !== null ? (
            <ViewportScrollBar
              axis="y"
              bar={bars.y}
              controls={surfaceId}
              onDrag={(pixels) => {
                dragScrollThumb('y', pixels)
              }}
            />
          ) : null}
        </div>
      )}
      {statusLine}
    </div>
  )
}
