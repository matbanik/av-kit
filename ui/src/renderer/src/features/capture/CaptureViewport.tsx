import { useEffect, useLayoutEffect, useRef, useState, type ReactNode } from 'react'

import { Button } from '../../components/ui/Button'
import type { Annotation } from './capture-annotate'
import type { CropBox } from './capture-crop'
import { arrowHeadPoints, arrowShaftEnd } from './capture-arrow-head'
import { contrastText, hexForNamedColor, NAMED_COLOR_HEX, normalizeHex } from './capture-color'
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
import { ACTION_BUTTONS, optionGroups, TOOLBAR_BUTTONS } from './capture-toolbar'
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
  svgTextBaselineY,
  textBackgroundBox,
} from './capture-text-metrics'
import { ToolbarIconButton } from './ToolbarIconButton'
import { CaptureCropOverlay } from './CaptureCropOverlay'
import { CaptureScrubField } from './CaptureScrubField'
import { FONT_SCRUB_MAX, STROKE_SCRUB_MAX } from './capture-scrub'
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

export type CaptureTool = 'select' | 'arrow' | 'box' | 'highlight' | 'text' | 'pixelate' | 'eraser' | 'crop'
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
  annotations: Annotation[]
  preview?: Annotation | null
  selectedIndex?: number | null
  /** HOVER_CURSOR: the resize handle under the pointer or being dragged; the pan cursors win over it. */
  resizeCursor?: HandleId | null
  canUndo: boolean
  canRedo: boolean
  textDraft: TextDraft | null
  colorApplyEnabled?: boolean
  colorCancelEnabled?: boolean
  onTool: (tool: CaptureTool) => void
  onColor: (color: string) => void
  onColorApply?: () => void
  onColorCancel?: () => void
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
  /** TOOL_LOCK (MEU-87): keep the current tool after each mark. Page view state, never persisted. */
  toolLocked?: boolean
  onToggleToolLock?: () => void
  onTextBg?: (color: string) => void
  onBlockSize?: (size: string) => void
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

function AnnotationMark({ ann }: { ann: Annotation }) {
  if (ann.type === 'arrow') {
    const length = Math.hypot(ann.to[0] - ann.from[0], ann.to[1] - ann.from[1])
    const end = arrowShaftEnd(ann.from, ann.to, ann.stroke_width)
    return (
      <g
        data-testid="capture-annotation"
        data-annotation-type="arrow"
        x1={ann.from[0]}
        y1={ann.from[1]}
        x2={ann.to[0]}
        y2={ann.to[1]}
        stroke={ann.color}
      >
        {end !== null ? (
          <line
            x1={ann.from[0]}
            y1={ann.from[1]}
            x2={end[0]}
            y2={end[1]}
            stroke={ann.color}
            strokeWidth={ann.stroke_width}
          />
        ) : null}
        {length > 0 ? (
          <polygon
            points={arrowHeadPoints(ann.from, ann.to, ann.stroke_width)}
            fill={ann.color}
            stroke="none"
          />
        ) : null}
      </g>
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
  if (ann.type === 'pixelate' || ann.type === 'eraser') {
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
        {ann.text}
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
  event: { currentTarget: EventTarget | null; clientX: number; clientY: number; shiftKey?: boolean },
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
  annotations,
  preview = null,
  selectedIndex = null,
  resizeCursor = null,
  canUndo,
  canRedo,
  textDraft,
  colorApplyEnabled = true,
  colorCancelEnabled = true,
  onTool,
  onColor,
  onColorApply = () => undefined,
  onColorCancel = () => undefined,
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
  onTextBg = () => undefined,
  onBlockSize = () => undefined,
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
  const surfaceRef = useRef<HTMLDivElement>(null)
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
  const options = optionGroups(tool, selected)
  // CROP_ENTRY: why the Crop button is disabled, if it is.
  const cropOff = hasSelection ? cropDisabledReason : NO_SHOT_HINT
  // SCRUB_BASE: an invalid field scrubs from the applicable selected mark, else the default.
  const strokeBase = selected !== null && (selected.type === 'arrow' || selected.type === 'rect') ? selected.stroke_width : 3
  const fontSizeBase = selected?.type === 'text' ? selected.font_size : 16
  const scrubTarget = selectedIndex ?? '-'
  const imageBox = { w: imageWidth, h: imageHeight }
  const view = viewTransform(frame, imageBox, zoom)
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
    event: { currentTarget: EventTarget | null; clientX: number; clientY: number; shiftKey?: boolean },
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
              onClick={() => onTool('select')}
            />
            <ToolbarIconButton
              spec={TOOLBAR_BUTTONS['capture-tool-arrow']}
              id="capture-tool-arrow"
              variant={toolVariant(tool === 'arrow')}
              pressed={tool === 'arrow'}
              disabled={!hasSelection || cropReason !== undefined}
              reason={cropReason ?? (hasSelection ? undefined : NO_SHOT_HINT)}
              onClick={() => onTool('arrow')}
            />
            <ToolbarIconButton
              spec={TOOLBAR_BUTTONS['capture-tool-box']}
              id="capture-tool-box"
              variant={toolVariant(tool === 'box')}
              pressed={tool === 'box'}
              disabled={!hasSelection || cropReason !== undefined}
              reason={cropReason ?? (hasSelection ? undefined : NO_SHOT_HINT)}
              onClick={() => onTool('box')}
            />
            <ToolbarIconButton
              spec={TOOLBAR_BUTTONS['capture-tool-highlight']}
              id="capture-tool-highlight"
              variant={toolVariant(tool === 'highlight')}
              pressed={tool === 'highlight'}
              disabled={!hasSelection || cropReason !== undefined}
              reason={cropReason ?? (hasSelection ? undefined : NO_SHOT_HINT)}
              onClick={() => onTool('highlight')}
            />
            <ToolbarIconButton
              spec={TOOLBAR_BUTTONS['capture-tool-text']}
              id="capture-tool-text"
              variant={toolVariant(tool === 'text')}
              pressed={tool === 'text'}
              disabled={!hasSelection || cropReason !== undefined}
              reason={cropReason ?? (hasSelection ? undefined : NO_SHOT_HINT)}
              onClick={() => onTool('text')}
            />
            <ToolbarIconButton
              spec={TOOLBAR_BUTTONS['capture-tool-pixelate']}
              id="capture-tool-pixelate"
              variant={toolVariant(tool === 'pixelate')}
              pressed={tool === 'pixelate'}
              disabled={!hasSelection || cropReason !== undefined}
              reason={cropReason ?? (hasSelection ? undefined : NO_SHOT_HINT)}
              onClick={() => onTool('pixelate')}
            />
            <ToolbarIconButton
              spec={TOOLBAR_BUTTONS['capture-tool-eraser']}
              id="capture-tool-eraser"
              variant={toolVariant(tool === 'eraser')}
              pressed={tool === 'eraser'}
              disabled={!hasSelection || cropReason !== undefined}
              reason={cropReason ?? (hasSelection ? undefined : NO_SHOT_HINT)}
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
                data-testid="capture-color-well"
                type="color"
                value={wellHold.current}
                onInput={(event) => {
                  onColor(event.currentTarget.value)
                }}
                onChange={(event) => {
                  onColor(event.target.value)
                }}
              />
              <input
                data-testid="capture-color"
                className="w-24 font-mono"
                value={color}
                onChange={(event) => {
                  onColor(event.target.value)
                }}
              />
              <Button size="sm" variant="primary" data-testid="capture-color-apply" disabled={!colorApplyEnabled} onClick={onColorApply}>
                Apply
              </Button>
              <Button size="sm" variant="ghost" data-testid="capture-color-cancel" disabled={!colorCancelEnabled} onClick={onColorCancel}>
                Cancel
              </Button>
              <select
                data-testid="capture-named-color"
                defaultValue=""
                style={namedMenuStyle}
                onChange={(event) => {
                  onNamedColor(event.target.value)
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
                  data-testid="capture-text-bg"
                  type="color"
                  aria-label="Text background"
                  title="Text background"
                  className="h-7 w-8 cursor-pointer bg-transparent p-0"
                  value={textBgHold.current}
                  onInput={(event) => {
                    onTextBg(event.currentTarget.value)
                  }}
                  onChange={(event) => {
                    onTextBg(event.target.value)
                  }}
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
          {options.includes('block') ? (
            <label key="capture-block-size" className="flex shrink-0 items-center gap-1 text-xs text-fg-muted">
              Block size
              <input
                data-testid="capture-block-size"
                type="number"
                min={PIXELATE_BLOCK_MIN}
                max={PIXELATE_BLOCK_MAX}
                step={1}
                aria-label="Block size"
                title="Block size"
                className="w-16 shrink-0 text-sm text-fg"
                value={blockSize}
                onChange={(event) => {
                  onBlockSize(event.target.value)
                }}
              />
            </label>
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
              {markLabel(ann, index)}
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
            // The view keys run before stopPropagation, which keeps the event from the window listener.
            handleViewKey(event.nativeEvent)
            onEditorKey(event.nativeEvent)
            // CAPTURE_CHORD_BUBBLE: a registry chord still reaches the shell's window handler.
            if (!isRegistryChord(event.nativeEvent)) {
              event.stopPropagation()
            }
          }}
          onKeyUp={(event) => {
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
              emitSurface(event, 'up', event.pointerId)
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
              emitSurface(event, 'cancel', event.pointerId)
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
            <input
              data-testid="capture-text-draft"
              className="absolute z-10 bg-bg border border-border px-1"
              style={draftStyle}
              value={textDraft.value}
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
                if (event.key === 'Enter') {
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
        </div>
      )}
      {statusLine}
    </div>
  )
}
