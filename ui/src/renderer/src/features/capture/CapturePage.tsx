import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { ImagePlus, SlidersHorizontal } from 'lucide-react'
import { useQueryClient } from '@tanstack/react-query'

import { HelpCard } from '../../components/help/HelpCard'
import { BulkResultToast } from '../../components/queue/BulkResultToast'
import { Button } from '../../components/ui/Button'
import { Disclosure } from '../../components/ui/Disclosure'
import { PathRow } from '../../components/ui/PathRow'
import { StatusChip } from '../../components/ui/StatusChip'
import { ApiError, apiFetch } from '../../lib/api'
import type { BulkResult } from '../../lib/queue/run-bulk'
import { logRenderer } from '../../lib/renderer-log'
import { usePublishCommandState } from '../../registry/command-state'
import { ariaKeyshortcuts } from '../../registry/shortcuts'
import {
  cropCapture,
  deleteCapture,
  deleteCaptures,
  flattenCapture,
  importCapture,
  invokeCaptureRegion,
  openCaptureFile,
  openCaptureFolder,
  removeCapture,
  revertCapture,
  saveAnnotations,
  setCaptureInboxDir,
  setCaptureSaveAllowed,
  setCaptureSelection,
} from './capture-commands'
import { displayHex, hexForNamedColor, normalizeHex } from './capture-color'
import { viewedFilePath } from './capture-viewed-file'
import {
  applyState,
  assertNever,
  flattenConfirmText,
  flattenStatus,
  revertConfirmText,
  revertState,
} from './capture-flatten'
import { CAPTURE_HELP_SECTIONS } from './capture-help-content'
import { parsePositiveInt } from './capture-scrub'
import type { Annotation } from './capture-annotate'
import { parseAnnotateBody } from './capture-annotate'
import { CaptureFilmstrip, type FilmstripShotActions } from './CaptureFilmstrip'
import { rangeBetween, toggleSelection } from './capture-filmstrip-select'
import { COPY_IMAGE_UNAVAILABLE, copyErrorMessage, loadClipboardPng } from './capture-clipboard'
import { CaptureCropBar } from './CaptureCropBar'
import {
  applyPreset,
  CROP_MIN_PX,
  cropEligible,
  drawCrop,
  moveCrop,
  nudgeCrop,
  presetFeasible,
  presetRatio,
  resizeCrop,
  swapCrop,
  wholeImage,
  type AspectPresetId,
  type CropBox,
} from './capture-crop'
import {
  CaptureViewport,
  type CaptureTool,
  type CaptureViewVariant,
  type CropCursor,
  type SurfacePointer,
  type TextDraft,
} from './CaptureViewport'
import { fetchCaptureImageObjectUrl } from './capture-image'
import {
  IMPORT_EXTENSIONS,
  importFiles,
  isEditableTarget,
  pasteToastResult,
  type ImportEntry,
  type PasteOutcome,
} from './capture-import'
import { hitTestMarks, moveEndpoint, translateBody } from './capture-hit-test'
import {
  boxHandlePoints,
  hitResizeHandle,
  isBoxMark,
  resizeBox,
  scaleTextMark,
  type HandleId,
  type TextCorner,
} from './capture-transform'
import { PIXELATE_BLOCK_DEFAULT, PIXELATE_BLOCK_MAX, PIXELATE_BLOCK_MIN } from './capture-region-pass'
import { ACTION_BUTTONS } from './capture-toolbar'
import { ToolbarIconButton } from './ToolbarIconButton'
import { useCaptureCatalog, type CaptureListItem, sortFilmstrip } from './useCaptureCatalog'
import { useCaptureSettings } from './useCaptureSettings'

const HOTKEY_IN_USE_TEMPLATE = '{accelerator} is in use — quit ShareX or pick another key'
const EMPTY_STATE = 'Press F2 or Capture region'
const DRAG_THRESHOLD_CSS = 3
const KEYBOARD_NUDGE_PX = 1
const COLOR_GATE_MESSAGE = 'Apply or Cancel color'
const TEXT_GATE_MESSAGE = 'Finish or cancel the text label'
// CROP_MODAL, CROP_UNSAVED_GATE, CROP_ERRORS (MEU-131): the crop's reasons and its pending status.
const CROP_REASON = 'Finish or cancel the crop first'
const CROP_NO_SHOT = 'Select a shot first'
const CROP_DIRTY_REASON = 'Save or discard your marks first'
const CROP_SMALL_REASON = `Too small to crop: each side needs ${CROP_MIN_PX} px`
const CROP_SWAP_REASON = 'Too small to swap this ratio'
const CROP_BUSY_MESSAGE = 'Cropping…'
const CROP_NUDGE_SHIFT_PX = 10
// IMPORT_BUTTON (MEU-132): the button's title while nothing blocks it.
const IMPORT_TITLE = 'Import image files. You can also drop them here or paste with Ctrl+V.'

/** IMPORT_DROP (D-551): a drag carries files when its types name `Files`. */
function dragHasFiles(transfer: DataTransfer | null): boolean {
  return transfer !== null && Array.from(transfer.types ?? []).includes('Files')
}

/** NUDGE_TARGET: what the arrow keys move, the whole selected mark or one end of a selected arrow. */
type NudgeTarget = 'body' | 'from' | 'to'

/** CROP_POINTER (D-515): a live crop drag, from the box it started on. */
type CropDrag =
  | { kind: 'resize'; handle: HandleId; startCssX: number; startCssY: number; start: CropBox }
  | { kind: 'move'; startCssX: number; startCssY: number; start: CropBox }
  | { kind: 'draw'; anchor: { x: number; y: number }; start: CropBox }

/** CROP_STATE (D-510): the open crop on one shot; `prior` is the tool it returns to when it closes. */
type CropState = {
  shotId: string
  box: CropBox
  aspect: AspectPresetId
  swapped: boolean
  prior: CaptureTool
  drag: CropDrag | null
  hover: CropCursor | null
  busy: boolean
}

function insideBox(box: CropBox, point: { x: number; y: number }): boolean {
  return point.x >= box.x && point.x <= box.x + box.width && point.y >= box.y && point.y <= box.y + box.height
}

/** SIZE_BURST (MEU-85): the field text and marks before one Stroke or Size scrub; `index` is the live mark, if any. */
type SizeBurst = {
  field: 'stroke' | 'font'
  startText: string
  origin: Annotation[] | null
  index: number | null
}

/** PIXELATE_BLOCK: an int in range, else null (the field holds the text and applies nothing). */
function parseBlockSize(raw: string): number | null {
  const parsed = parsePositiveInt(raw)
  return parsed !== null && parsed >= PIXELATE_BLOCK_MIN && parsed <= PIXELATE_BLOCK_MAX ? parsed : null
}

const COLOR_FOCUS_IDS = new Set([
  'capture-color',
  'capture-color-well',
  'capture-text-draft',
  'capture-font-size',
  'capture-text-bg',
  'capture-text-bg-clear',
  'capture-stroke',
  'capture-block-size',
  'capture-named-color',
])

function annotationOwnsFocus(): boolean {
  const active = document.activeElement
  const viewport = document.querySelector('[data-testid="capture-viewport"]')
  // Any Element: a focused arrow handle is an SVG circle (HANDLE_LAYER), not an HTMLElement.
  if (!(active instanceof Element) || viewport === null || !viewport.contains(active)) {
    return false
  }
  // The inline confirm strip sits inside the viewport (AC-57.7) but keeps the old portal's
  // key scope: editor keys never act on marks while its buttons hold focus.
  if (active.closest('[data-testid="capture-confirm-strip"]') !== null) {
    return false
  }
  const id = active.getAttribute('data-testid')
  if (id !== null && COLOR_FOCUS_IDS.has(id)) {
    return false
  }
  return true
}

/**
 * HISTORY_FOCUS (D-164): the history chords act from the page body or the Capture image and its controls,
 * never from a text field, a COLOR_FOCUS_IDS control or the confirm strip, and never under a modal dialog.
 */
function historyOwnsFocus(): boolean {
  const active = document.activeElement
  if (active instanceof Element && active.matches('input, textarea, select, [contenteditable]')) {
    return false
  }
  if (document.querySelector('[aria-modal="true"]') !== null) {
    return false
  }
  return active === null || active === document.body || annotationOwnsFocus()
}

/** HISTORY_CHORDS (D-163): Ctrl/Meta+Z undoes; Ctrl/Meta+Y and Ctrl/Meta+Shift+Z redo; Alt opts out. */
function historyChord(event: KeyboardEvent): 'undo' | 'redo' | null {
  if (!(event.ctrlKey || event.metaKey) || event.altKey) {
    return null
  }
  const key = event.key.toLowerCase()
  if (key === 'z') {
    return event.shiftKey ? 'redo' : 'undo'
  }
  if (key === 'y' && !event.shiftKey) {
    return 'redo'
  }
  return null
}

type Gesture = {
  kind: 'drawing' | 'moving' | 'endpoint' | 'resizing'
  startCssX: number
  startCssY: number
  startImageX: number
  startImageY: number
  origin: Annotation[]
  index: number
  end?: 'from' | 'to'
  handle?: HandleId
  pointerId: number
  epoch: number
  shotId: string
}

const TEXT_CORNERS: ReadonlySet<HandleId> = new Set(['nw', 'ne', 'se', 'sw'])

/**
 * RESIZE_GESTURE: the mark resized by `handle` to `point`, or null when there is no handle or the mark has none.
 * TEXT_SCALE: a text mark scales from a plate corner.
 */
function resizeMark(
  mark: Annotation,
  handle: HandleId | undefined,
  point: { x: number; y: number },
  imageW: number,
  imageH: number,
): Annotation | null {
  if (handle === undefined) {
    return null
  }
  if (isBoxMark(mark)) {
    return resizeBox(mark, handle, point, imageW, imageH)
  }
  if (mark.type === 'text' && TEXT_CORNERS.has(handle)) {
    return scaleTextMark(mark, handle as TextCorner, point, imageW, imageH)
  }
  return null
}

/** A text draft is unsaved work when Enter would commit it: not empty, and for a re-edit, not the mark's own text. */
function draftCommits(draft: TextDraft | null, list: Annotation[]): boolean {
  if (draft === null || draft.value.trim().length === 0) {
    return false
  }
  if (draft.editIndex === undefined) {
    return true
  }
  const mark = list[draft.editIndex]
  return mark?.type === 'text' && mark.text !== draft.value
}

function createDrawnMark(
  tool: CaptureTool,
  start: { x: number; y: number },
  end: { x: number; y: number },
  color: string,
  stroke: string,
  blockSize: string,
): Annotation | null {
  if (tool === 'select' || tool === 'text' || tool === 'crop') {
    return null
  }
  const strokeWidth = Number.parseInt(stroke, 10) || 3
  if (tool === 'arrow') {
    if (Math.hypot(end.x - start.x, end.y - start.y) === 0) {
      return null
    }
    return {
      type: 'arrow',
      color,
      stroke_width: strokeWidth,
      from: [start.x, start.y],
      to: [end.x, end.y],
    }
  }
  const x = Math.min(start.x, end.x)
  const y = Math.min(start.y, end.y)
  const width = Math.abs(end.x - start.x)
  const height = Math.abs(end.y - start.y)
  if (width === 0 && height === 0) {
    return null
  }
  if (tool === 'box') {
    return {
      type: 'rect',
      x,
      y,
      width,
      height,
      color,
      stroke_width: strokeWidth,
    }
  }
  if (tool === 'pixelate') {
    // BLOCK_CONTROL: the field's value when it is a valid block, else the default.
    return { type: 'pixelate', x, y, width, height, block_size: parseBlockSize(blockSize) ?? PIXELATE_BLOCK_DEFAULT }
  }
  if (tool === 'eraser') {
    // REGION_DTO: a rectangle only; the fill is sampled at preview and bake time.
    return { type: 'eraser', x, y, width, height }
  }
  return {
    type: 'highlight',
    x,
    y,
    width,
    height,
    color,
    opacity: 0.35,
  }
}

function replaceAt(list: Annotation[], index: number, next: Annotation): Annotation[] {
  return list.map((item, i) => (i === index ? next : item))
}

type ConfirmKind = 'dirty' | 'delete' | 'flatten' | 'revert'

type ConfirmSpec = { message: string; cancelId: string; acceptId: string; acceptLabel: string }

/** Per-shot success notice (FLATTEN_STATUS); shown only while its shot stays selected. `null` is the empty selection (BATCH_RESULT after the last shot goes). */
type ShotNotice = { shotId: string | null; text: string }

/** RANGE (MEU-89): the Shift-click anchor and the range it spans, in filmstrip order. */
type FilmstripRange = { anchorId: string | null; rangeIds: string[] }

export function CapturePage() {
  const catalog = useCaptureCatalog()
  const settings = useCaptureSettings()
  const items = useMemo(() => catalog.data?.items ?? [], [catalog.data?.items])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [tool, setTool] = useState<CaptureTool>('arrow')
  // LOCK_PERSISTS (MEU-87): only the lock button changes this; choosing a tool keeps it.
  const [toolLocked, setToolLocked] = useState(false)
  const [color, setColor] = useState('#E0AF68')
  const [candidate, setCandidate] = useState('#E0AF68')
  const [stroke, setStroke] = useState('3')
  const [fontSize, setFontSize] = useState('16')
  const [textBg, setTextBg] = useState('')
  const [blockSize, setBlockSize] = useState(String(PIXELATE_BLOCK_DEFAULT))
  const [viewVariant, setViewVariant] = useState<CaptureViewVariant>('original')
  const [annotations, setAnnotations] = useState<Annotation[]>([])
  const [past, setPast] = useState<Annotation[][]>([])
  const [future, setFuture] = useState<Annotation[][]>([])
  const [saved, setSaved] = useState<Annotation[]>([])
  const [error, setError] = useState<string | null>(null)
  // CONFIRM_KINDS (MEU-67): every kind is handled by the exhaustive switch in confirmSpec.
  const [confirm, setConfirm] = useState<ConfirmKind | null>(null)
  // DELETE_TARGETS: the shots the 'delete' confirm acts on (the toolbar's selection or a menu target).
  const [deleteTargets, setDeleteTargets] = useState<string[]>([])
  const [pendingSelect, setPendingSelect] = useState<string | null>(null)
  const [anchorId, setAnchorId] = useState<string | null>(null)
  const [rangeIds, setRangeIds] = useState<string[]>([])
  // RANGE_DIRTY: the range a choice would apply, held until the discard confirm is answered.
  const [pendingRange, setPendingRange] = useState<FilmstripRange | null>(null)
  const [hotkeyInUse, setHotkeyInUse] = useState(false)
  // CP2: the key cap shows only for a hotkey the main process actually registered.
  const [hotkeyCap, setHotkeyCap] = useState<string | null>(null)
  // CP3/OQ-3: the Settings disclosure starts closed; later toggles are local presentation state.
  const [settingsOpen, setSettingsOpen] = useState(false)
  const confirmCancelRef = useRef<HTMLButtonElement>(null)
  const [recording, setRecording] = useState(false)
  const overlayEditGen = useRef(0)
  const [textDraft, setTextDraft] = useState<TextDraft | null>(null)
  const [viewportSrc, setViewportSrc] = useState<string | null>(null)
  const [overlayReady, setOverlayReady] = useState(false)
  const [imageEpoch, setImageEpoch] = useState(0)
  const [baked, setBaked] = useState(false)
  // MEU-67: the selected detail's newest backup (REVERT_VISIBLE) and the reload key after a
  // flatten or revert (IMAGE_REVISION).
  const [backupPath, setBackupPath] = useState<string | null>(null)
  const [detailRevision, setDetailRevision] = useState(0)
  const [notice, setNotice] = useState<ShotNotice | null>(null)
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null)
  const [preview, setPreview] = useState<Annotation | null>(null)
  // Read by the window key handler, so a ref: a focus and a keydown in one task see the new end.
  const nudgeTargetRef = useRef<NudgeTarget>('body')
  const [namedPreview, setNamedPreview] = useState(false)
  const [txOpen, setTxOpen] = useState(false)
  const gestureRef = useRef<Gesture | null>(null)
  // HOVER_CURSOR: the resize handle under an idle pointer, or the handle a resize gesture grabbed.
  const [hoverHandle, setHoverHandle] = useState<HandleId | null>(null)
  // A new selection drops the old hover; the next pointer move names a handle of the new mark.
  useEffect(() => {
    setHoverHandle(null)
  }, [selectedIndex])
  const annotationsRef = useRef(annotations)
  annotationsRef.current = annotations
  const canSaveRef = useRef(false)
  const nudgeBurstRef = useRef<Annotation[] | null>(null)
  const sizeBurstRef = useRef<SizeBurst | null>(null)
  // SCRUB_BASE: tells the Stroke or Size field that the page closed its burst.
  const [sizeEpoch, setSizeEpoch] = useState({ stroke: 0, font: 0 })
  // CROP_STATE (D-510): pointer and key events read the ref in the same task; updateCrop sets both.
  const [crop, setCrop] = useState<CropState | null>(null)
  const cropRef = useRef<CropState | null>(null)
  const cropBusyRef = useRef(false)
  /** CROP_COMMIT (D-515): the copy a crop just selected; its detail load keeps the tool the crop restored. */
  const cropCopyRef = useRef<string | null>(null)
  // IMPORT_GATE (D-555): the crop, an open confirm or a running import or paste blocks a new one; `dirty`
  // doesn't. The handlers read refs, so a drop or a paste in the same task as a state change sees it. Only an
  // import run shows on the button (aria-busy): a paste holds the gate through its ref alone.
  const [importBusy, setImportBusy] = useState(false)
  const importBusyRef = useRef(false)
  const pasteBusyRef = useRef(false)
  const confirmOpenRef = useRef(false)
  confirmOpenRef.current = confirm !== null
  // IMPORT_TOAST (D-554): one note for all three entries; a new run replaces it and only Dismiss clears it.
  const [importNote, setImportNote] = useState<BulkResult | null>(null)
  const queryClient = useQueryClient()
  const importBlocked = useCallback(
    () => cropRef.current !== null || confirmOpenRef.current || importBusyRef.current || pasteBusyRef.current,
    [],
  )

  const selected = useMemo(
    () => items.find((item) => item.id === selectedId) ?? null,
    [items, selectedId],
  )
  const selectedMark = selectedIndex !== null ? annotations[selectedIndex] : undefined
  // A region mark has no color, so its baseline is the tool color (the color group is hidden for it).
  const colorBaseline =
    selectedMark !== undefined && 'color' in selectedMark ? displayHex(selectedMark.color) : displayHex(color)
  const colorDirty = !namedPreview && displayHex(candidate) !== colorBaseline
  const gestureOpen = gestureRef.current !== null || preview !== null
  const dirty = JSON.stringify(annotations) !== JSON.stringify(saved) || draftCommits(textDraft, annotations)
  // TEXT_REEDIT: an edit draft holds an index into the marks, so nothing may reorder them while it is open.
  const editingText = textDraft?.editIndex !== undefined
  const canSave =
    selectedId !== null &&
    overlayReady &&
    imageEpoch > 0 &&
    viewVariant === 'original' &&
    textDraft === null &&
    !colorDirty &&
    !gestureOpen &&
    !txOpen
  canSaveRef.current = canSave
  // PAGE_STATE: capture-save is mounted while dirty and enabled while canSave.
  usePublishCommandState('/capture', { 'capture:save': dirty && canSave })
  const cropImage = { width: selected?.width ?? 0, height: selected?.height ?? 0 }
  const cropLive = crop !== null && crop.shotId === selectedId ? crop : null
  const cropReason = cropLive !== null ? CROP_REASON : undefined
  // CROP_UNSAVED_GATE (D-509): no crop over unsaved marks or on a shot too small to cut.
  const cropDisabledReason =
    cropLive !== null
      ? undefined
      : selected === null
        ? CROP_NO_SHOT
        : !cropEligible(cropImage.width, cropImage.height)
          ? CROP_SMALL_REASON
          : dirty
            ? CROP_DIRTY_REASON
            : undefined

  // CROP_CANCEL (D-509): another shot, a shot that left the catalog or a view other than Original closes it.
  useEffect(() => {
    if (crop === null) {
      return
    }
    if (crop.shotId !== selectedId || viewVariant !== 'original' || !items.some((item) => item.id === crop.shotId)) {
      cropRef.current = null
      setCrop(null)
      setTool(crop.prior)
    }
  }, [crop, items, selectedId, viewVariant])

  useEffect(() => {
    setCaptureSaveAllowed(() => canSaveRef.current)
    return () => {
      setCaptureSaveAllowed(() => false)
    }
  }, [])

  useEffect(() => {
    if (selectedId !== null) {
      return
    }
    const newest = sortFilmstrip(items)[0]
    if (newest !== undefined) {
      setSelectedId(newest.id)
    }
  }, [items, selectedId])

  // RANGE: shots that left the catalog leave the range, and a removed anchor is dropped.
  useEffect(() => {
    const present = new Set(items.map((item) => item.id))
    setRangeIds((ids) => (ids.every((id) => present.has(id)) ? ids : ids.filter((id) => present.has(id))))
    setAnchorId((id) => (id !== null && !present.has(id) ? null : id))
  }, [items])

  useEffect(() => {
    setCaptureInboxDir(settings.form.inbox_dir)
  }, [settings.form.inbox_dir])

  // PASTE_KEY (D-550): Ctrl+V outside a text field saves a clipboard image to the inbox. It adds no
  // commandRegistry entry; a text field, a textarea or an editable element keeps its native paste.
  useEffect(() => {
    const onPaste = (event: ClipboardEvent): void => {
      if (isEditableTarget(event.target) || importBlocked()) {
        return
      }
      event.preventDefault()
      pasteBusyRef.current = true
      void (async () => {
        let outcome: PasteOutcome
        try {
          outcome = (await window.api.pasteCaptureImage?.()) ?? { kind: 'failed' }
        } catch {
          outcome = { kind: 'failed' }
        }
        // PASTE_MESSAGES: `busy` shows nothing; only a saved image changes the list.
        const note = pasteToastResult(outcome)
        if (note !== null) {
          setImportNote(note)
        }
        if (outcome.kind === 'saved') {
          void queryClient.invalidateQueries({ queryKey: ['captures'] })
        }
      })().finally(() => {
        pasteBusyRef.current = false
      })
    }
    window.addEventListener('paste', onPaste)
    return () => {
      window.removeEventListener('paste', onPaste)
    }
  }, [importBlocked, queryClient])

  /** IMPORT_RUN for the button and a drop: one run at a time, then its note. An empty pick shows nothing. */
  async function runImport(collect: () => Promise<ImportEntry[]>): Promise<void> {
    importBusyRef.current = true
    setImportBusy(true)
    try {
      const entries = await collect()
      if (entries.length > 0) {
        setImportNote(await importFiles(entries, { importOne: importCapture, refetch: () => catalog.refetch() }))
      }
    } finally {
      importBusyRef.current = false
      setImportBusy(false)
    }
  }

  useEffect(() => {
    setCaptureSelection({
      id: selectedId,
      annotations,
      viewedPath: viewedFilePath(viewVariant, selected),
    })
  }, [annotations, selected, selectedId, viewVariant])

  useEffect(() => {
    let cancelled = false
    let created: string | null = null
    if (selectedId === null) {
      setViewportSrc(null)
      setImageEpoch(0)
      return
    }
    setImageEpoch(0)
    void fetchCaptureImageObjectUrl(selectedId, viewVariant)
      .then((url) => {
        if (cancelled) {
          if (url !== null) {
            URL.revokeObjectURL(url)
          }
          return
        }
        created = url
        setViewportSrc(url)
        setImageEpoch((value) => value + 1)
      })
      .catch(() => {
        if (!cancelled) {
          setViewportSrc(null)
          setImageEpoch(0)
        }
      })
    return () => {
      cancelled = true
      if (created !== null) {
        URL.revokeObjectURL(created)
      }
    }
    // IMAGE_REVISION: a flatten or revert bumps updated_at, so the viewport image refetches.
  }, [selectedId, viewVariant, selected?.updated_at])

  useEffect(() => {
    nudgeTargetRef.current = 'body'
    if (selectedId === null) {
      setOverlayReady(false)
      setAnnotations([])
      setSaved([])
      setPast([])
      setFuture([])
      setTextDraft(null)
      setSelectedIndex(null)
      setPreview(null)
      setBaked(false)
      setBackupPath(null)
      setNamedPreview(false)
      setTxOpen(false)
      gestureRef.current = null
      sizeBurstRef.current = null
      return
    }
    let cancelled = false
    setOverlayReady(false)
    setAnnotations([])
    setSaved([])
    setPast([])
    setFuture([])
    setTextDraft(null)
    setSelectedIndex(null)
    setPreview(null)
    setBaked(false)
    setBackupPath(null)
    setNamedPreview(false)
    setTxOpen(false)
    gestureRef.current = null
    sizeBurstRef.current = null
    overlayEditGen.current = 0
    const loadGen = overlayEditGen.current
    const loadId = selectedId
    const keepTool = cropCopyRef.current === loadId
    if (!keepTool) {
      cropCopyRef.current = null
    }
    void apiFetch<{ annotations?: unknown; backup_path?: string | null }>(`/captures/${loadId}`)
      .then((detail) => {
        if (cancelled || overlayEditGen.current !== loadGen) {
          return
        }
        if (keepTool) {
          cropCopyRef.current = null
        }
        setBackupPath(typeof detail.backup_path === 'string' ? detail.backup_path : null)
        const parsed = parseAnnotateBody({ annotations: detail.annotations ?? [] })
        if (parsed === null) {
          window.dispatchEvent(
            new CustomEvent('av-kit:capture:error', { detail: 'Invalid overlay marks' }),
          )
          return
        }
        setAnnotations(parsed.annotations)
        setSaved(parsed.annotations)
        setOverlayReady(true)
        // A crop's copy keeps the tool the crop opened from, even when it carries marks.
        if (parsed.annotations.length > 0 && !keepTool) {
          setTool('select')
        }
      })
      .catch((caught: unknown) => {
        if (cancelled) {
          return
        }
        const message =
          caught instanceof ApiError || caught instanceof Error ? caught.message : String(caught)
        window.dispatchEvent(new CustomEvent('av-kit:capture:error', { detail: message }))
      })
    return () => {
      cancelled = true
    }
  }, [selectedId, detailRevision])

  useEffect(() => {
    void window.api.getHotkeyStatus().then((status) => {
      setHotkeyInUse(status.inUse)
      setHotkeyCap(status.registered && status.accelerator.length > 0 ? status.accelerator : null)
    })
  }, [settings.form.hotkey])

  useEffect(() => {
    // APG alert-dialog guidance: an opening confirmation focuses its least destructive action.
    if (confirm !== null) {
      confirmCancelRef.current?.focus()
    }
  }, [confirm])

  useEffect(() => {
    const onError = (event: Event) => {
      const detail = (event as CustomEvent<string>).detail
      setError(detail)
      logRenderer('ERROR', detail)
    }
    window.addEventListener('av-kit:capture:error', onError)
    return () => {
      window.removeEventListener('av-kit:capture:error', onError)
    }
  }, [])

  function applyHistory(next: Annotation[]): void {
    finishSize()
    const previous = annotationsRef.current
    setNotice(null)
    overlayEditGen.current += 1
    setPast((stack) => [...stack, previous])
    setFuture([])
    setAnnotations(next)
    annotationsRef.current = next
  }

  function updateCrop(next: CropState | null): void {
    cropRef.current = next
    setCrop(next)
  }

  /** CROP_CANCEL: close the crop and return to the tool it opened from. */
  function closeCrop(): void {
    const open = cropRef.current
    if (open === null) {
      return
    }
    updateCrop(null)
    setTool(open.prior)
  }

  /** CROP_ENTRY (D-508): opens on the whole image, Free, in Original; a second click closes it. */
  function toggleCrop(): void {
    const open = cropRef.current
    if (open !== null) {
      if (!open.busy) {
        closeCrop()
      }
      return
    }
    if (
      selectedId === null ||
      cropDisabledReason !== undefined ||
      textDraft !== null ||
      colorDirty ||
      txOpen ||
      gestureRef.current !== null
    ) {
      return
    }
    finishSize()
    setPreview(null)
    setSelectedIndex(null)
    nudgeTargetRef.current = 'body'
    setViewVariant('original')
    updateCrop({
      shotId: selectedId,
      box: wholeImage(cropImage),
      aspect: 'free',
      swapped: false,
      prior: tool,
      drag: null,
      hover: null,
      busy: false,
    })
    setTool('crop')
  }

  /** CROP_BAR aspect: a preset that can't fit is ignored. */
  function chooseCropAspect(aspect: AspectPresetId): void {
    const open = cropRef.current
    if (open === null || open.drag !== null || open.busy) {
      return
    }
    const box = applyPreset(open.box, aspect, cropImage, open.swapped)
    if (box !== null) {
      updateCrop({ ...open, box, aspect })
    }
  }

  /** CROP_BAR swap (button or X): exchange the orientation when the swapped ratio fits. */
  function swapCropBox(): void {
    const open = cropRef.current
    if (open === null || open.drag !== null || open.busy) {
      return
    }
    const box = swapCrop(open.box, open.aspect, cropImage, open.swapped)
    if (box !== null) {
      updateCrop({ ...open, box, swapped: !open.swapped })
    }
  }

  function setCropBox(box: CropBox): void {
    const open = cropRef.current
    if (open === null || open.drag !== null || open.busy) {
      return
    }
    updateCrop({ ...open, box })
  }

  function resetCrop(): void {
    const open = cropRef.current
    if (open === null || open.busy) {
      return
    }
    updateCrop({ ...open, box: wholeImage(cropImage), aspect: 'free', swapped: false, drag: null })
  }

  /** CROP_COMMIT, CROP_ERRORS (D-516, D-517): one POST; the copy is selected and named, the source stays. */
  function commitCrop(): void {
    const open = cropRef.current
    if (open === null || open.drag !== null || cropBusyRef.current) {
      return
    }
    cropBusyRef.current = true
    const { shotId, box, prior } = open
    updateCrop({ ...open, busy: true })
    setError(null)
    void run(async () => {
      try {
        const result = await cropCapture(shotId, box)
        if (cropRef.current?.shotId === shotId) {
          updateCrop(null)
          setTool(prior)
        }
        applyRange({ anchorId: result.item.id, rangeIds: [] })
        cropCopyRef.current = result.item.id
        setSelectedId(result.item.id)
        setNotice({ shotId: result.item.id, text: `Saved crop as ${result.item.display_name}.` })
        setViewVariant('original')
        setTextDraft(null)
        setPast([])
        setFuture([])
      } finally {
        cropBusyRef.current = false
        const live = cropRef.current
        if (live?.busy === true) {
          updateCrop({ ...live, busy: false })
        }
      }
    })
  }

  /** CROP_POINTER (D-515): a handle resizes, inside moves, outside draws; Shift keeps the ratio under Free. */
  function handleCropPointer(event: SurfacePointer): void {
    const open = cropRef.current
    if (open === null || open.busy) {
      return
    }
    const loose = event.scale > 0 ? { x: (event.cssX - event.ox) / event.scale, y: (event.cssY - event.oy) / event.scale } : null
    const view = { cssX: event.cssX, cssY: event.cssY, scale: event.scale, ox: event.ox, oy: event.oy }
    if (event.phase === 'dblclick') {
      if (open.drag === null && loose !== null && insideBox(open.box, loose)) {
        commitCrop()
      }
      return
    }
    if (event.phase === 'cancel') {
      if (open.drag !== null) {
        updateCrop({ ...open, box: open.drag.start, drag: null })
      }
      return
    }
    if (event.phase === 'down') {
      if (loose === null || event.imageClamped === null) {
        return
      }
      const handle = hitResizeHandle(boxHandlePoints(open.box), view)
      const drag: CropDrag =
        handle !== null
          ? { kind: 'resize', handle, startCssX: event.cssX, startCssY: event.cssY, start: open.box }
          : insideBox(open.box, loose)
            ? { kind: 'move', startCssX: event.cssX, startCssY: event.cssY, start: open.box }
            : { kind: 'draw', anchor: event.imageClamped, start: open.box }
      updateCrop({ ...open, drag, hover: handle ?? (drag.kind === 'move' ? 'move' : 'draw') })
      return
    }
    const drag = open.drag
    if (drag === null) {
      if (event.phase === 'move' && loose !== null) {
        const hover = hitResizeHandle(boxHandlePoints(open.box), view) ?? (insideBox(open.box, loose) ? 'move' : 'draw')
        if (hover !== open.hover) {
          updateCrop({ ...open, hover })
        }
      }
      return
    }
    const ratio =
      presetRatio(open.aspect, cropImage, open.swapped) ??
      (event.shiftKey ? drag.start.width / drag.start.height : null)
    let box = open.box
    if (drag.kind === 'draw') {
      if (event.imageClamped !== null) {
        box = drawCrop(drag.anchor, event.imageClamped, cropImage, ratio) ?? drag.start
      }
    } else if (event.scale > 0) {
      const dx = (event.cssX - drag.startCssX) / event.scale
      const dy = (event.cssY - drag.startCssY) / event.scale
      box =
        drag.kind === 'resize'
          ? resizeCrop(drag.start, drag.handle, dx, dy, cropImage, ratio)
          : moveCrop(drag.start, dx, dy, cropImage)
    }
    updateCrop({ ...open, box, drag: event.phase === 'up' ? null : drag })
  }

  /** CROP_MODAL (D-518): while the crop is open only its keys act; the marks, history and tools wait. */
  function handleCropKey(event: KeyboardEvent): void {
    const open = cropRef.current
    if (open === null || event.type !== 'keydown') {
      return
    }
    const target = event.target
    if (
      target instanceof HTMLInputElement ||
      target instanceof HTMLSelectElement ||
      target instanceof HTMLTextAreaElement
    ) {
      return
    }
    if (historyChord(event) !== null) {
      event.preventDefault()
      return
    }
    const plain = !event.ctrlKey && !event.metaKey && !event.altKey
    if (event.key === 'Escape') {
      event.preventDefault()
      if (!open.busy) {
        closeCrop()
      }
      return
    }
    if (event.key === 'Enter') {
      // Enter on another button stays that button's. On the Crop toggle it commits: keyboard entry
      // keeps focus there (A-4), so its own activation would otherwise close the crop.
      const toggle = target instanceof HTMLElement && target.dataset.testid === 'capture-tool-crop'
      if (!plain || (target instanceof HTMLButtonElement && !toggle)) {
        return
      }
      event.preventDefault()
      commitCrop()
      return
    }
    const step = event.shiftKey ? CROP_NUDGE_SHIFT_PX : KEYBOARD_NUDGE_PX
    const delta =
      event.key === 'ArrowRight'
        ? [step, 0]
        : event.key === 'ArrowLeft'
          ? [-step, 0]
          : event.key === 'ArrowDown'
            ? [0, step]
            : event.key === 'ArrowUp'
              ? [0, -step]
              : null
    if (delta !== null) {
      event.preventDefault()
      if (plain && open.drag === null && !open.busy) {
        updateCrop({ ...open, box: nudgeCrop(open.box, delta[0] ?? 0, delta[1] ?? 0, cropImage) })
      }
      return
    }
    if ((event.key === 'x' || event.key === 'X') && plain) {
      event.preventDefault()
      swapCropBox()
    }
  }

  function chooseTool(next: CaptureTool): void {
    if (cropRef.current !== null || textDraft !== null || colorDirty || txOpen || gestureRef.current !== null) {
      return
    }
    finishSize()
    setTool(next)
    nudgeTargetRef.current = 'body'
    if (next !== 'select') {
      setSelectedIndex(null)
      setNamedPreview(false)
      setCandidate(displayHex(color))
    }
  }

  function applyRange(range: FilmstripRange): void {
    setAnchorId(range.anchorId)
    setRangeIds(range.rangeIds)
  }

  /** RANGE: a plain choice re-anchors; Shift extends from the anchor, or from the editor's shot. */
  function filmstripChoice(item: CaptureListItem, extend: boolean): void {
    const anchor = extend ? (anchorId ?? selectedId) : null
    chooseItem(
      item,
      anchor === null
        ? { anchorId: item.id, rangeIds: [] }
        : { anchorId: anchor, rangeIds: rangeBetween(sortFilmstrip(items).map((row) => row.id), anchor, item.id) },
    )
  }

  /**
   * CHECK_TOGGLE (D-25): a checkbox toggles its shot in the set, and Shift ticks the range from the
   * anchor. The editor's shot is untouched, so there is nothing to discard and no confirm.
   */
  function checkChoice(id: string, extend: boolean): void {
    const order = sortFilmstrip(items).map((row) => row.id)
    const anchor = extend ? (anchorId ?? selectedId) : null
    applyRange(
      anchor === null
        ? { anchorId: id, rangeIds: toggleSelection(order, rangeIds, id) }
        : { anchorId: anchor, rangeIds: rangeBetween(order, anchor, id) },
    )
    setNotice(null)
  }

  function chooseItem(item: CaptureListItem, range: FilmstripRange): void {
    if (dirty) {
      setPendingSelect(item.id)
      setPendingRange(range)
      setConfirm('dirty')
      return
    }
    applyRange(range)
    setSelectedId(item.id)
    setNotice(null)
    setViewVariant('original')
    setTextDraft(null)
    setPast([])
    setFuture([])
  }

  /** TEXT_REEDIT: reopen text mark `index` in the draft field; the mark is hidden until Enter or Escape. */
  function openTextEdit(index: number): void {
    const mark = annotationsRef.current[index]
    if (mark?.type !== 'text') {
      return
    }
    finishSize()
    setSelectedIndex(index)
    nudgeTargetRef.current = 'body'
    inspectMark(index)
    setTextDraft({ x: mark.x, y: mark.y, value: mark.text, editIndex: index })
  }

  function commitSelection(index: number, list: Annotation[], nextTool: CaptureTool = 'select'): void {
    finishSize()
    setSelectedIndex(index)
    setTool(nextTool)
    nudgeTargetRef.current = 'body'
    inspectMark(index)
  }

  function inspectMark(index: number): void {
    const mark = annotationsRef.current[index]
    setNamedPreview(false)
    if (mark === undefined) {
      return
    }
    if (mark.type === 'pixelate') {
      setCandidate(displayHex(color))
      setBlockSize(String(mark.block_size))
      return
    }
    if (mark.type === 'eraser') {
      setCandidate(displayHex(color))
      return
    }
    setCandidate(displayHex(mark.color))
    if (mark.type === 'text') {
      setFontSize(String(mark.font_size))
      setTextBg(mark.bg_color ? displayHex(mark.bg_color) : '')
      return
    }
    if (mark.type === 'arrow' || mark.type === 'rect') {
      setStroke(String(mark.stroke_width))
    }
  }

  function handleSurfacePointer(event: SurfacePointer): void {
    if (viewVariant !== 'original' || !overlayReady || imageEpoch < 1) {
      return
    }
    if (cropRef.current !== null) {
      handleCropPointer(event)
      return
    }
    if (event.phase === 'down') {
      finishSize()
    }
    if (event.phase === 'cancel') {
      gestureRef.current = null
      setPreview(null)
      setTxOpen(false)
      return
    }
    if (event.phase === 'up') {
      setTxOpen(false)
    }
    if (textDraft !== null) {
      return
    }
    const imageW = selected?.width ?? 0
    const imageH = selected?.height ?? 0
    if (event.phase === 'dblclick') {
      // TEXT_REEDIT: a select-tool double-click on a text mark's body reopens its text.
      if (tool !== 'select' || event.image === null) {
        return
      }
      const hit = hitTestMarks({
        cssX: event.cssX,
        cssY: event.cssY,
        scale: event.scale,
        ox: event.ox,
        oy: event.oy,
        imageW,
        imageH,
        annotations: annotationsRef.current,
        selectedIndex,
      })
      if (hit?.kind === 'body') {
        openTextEdit(hit.index)
      }
      return
    }
    if (event.phase === 'down') {
      if (event.image === null) {
        return
      }
      if (tool === 'text') {
        setTextDraft({ x: event.image.x, y: event.image.y, value: '' })
        return
      }
      if (tool === 'select') {
        const hit = hitTestMarks({
          cssX: event.cssX,
          cssY: event.cssY,
          scale: event.scale,
          ox: event.ox,
          oy: event.oy,
          imageW,
          imageH,
          annotations: annotationsRef.current,
          selectedIndex,
        })
        if (hit === null) {
          setSelectedIndex(null)
          nudgeTargetRef.current = 'body'
          setNamedPreview(false)
          setCandidate(displayHex(color))
          return
        }
        setSelectedIndex(hit.index)
        // NUDGE_TARGET: grabbing an arrow end makes the arrow keys move that end.
        nudgeTargetRef.current = hit.kind === 'handle' ? hit.end : 'body'
        inspectMark(hit.index)
        setTxOpen(true)
        if (hit.kind === 'resize') {
          setHoverHandle(hit.handle)
        }
        gestureRef.current = {
          kind: hit.kind === 'handle' ? 'endpoint' : hit.kind === 'resize' ? 'resizing' : 'moving',
          startCssX: event.cssX,
          startCssY: event.cssY,
          startImageX: event.image.x,
          startImageY: event.image.y,
          origin: annotationsRef.current,
          index: hit.index,
          end: hit.kind === 'handle' ? hit.end : undefined,
          handle: hit.kind === 'resize' ? hit.handle : undefined,
          pointerId: event.pointerId,
          epoch: imageEpoch,
          shotId: selectedId ?? '',
        }
        return
      }
      setTxOpen(true)
      gestureRef.current = {
        kind: 'drawing',
        startCssX: event.cssX,
        startCssY: event.cssY,
        startImageX: event.image.x,
        startImageY: event.image.y,
        origin: annotationsRef.current,
        index: -1,
        pointerId: event.pointerId,
        epoch: imageEpoch,
        shotId: selectedId ?? '',
      }
      return
    }
    const gesture = gestureRef.current
    if (event.phase === 'up') {
      gestureRef.current = null
      setPreview(null)
      if (gesture === null || gesture.epoch !== imageEpoch || gesture.shotId !== (selectedId ?? '')) {
        return
      }
      const current = event.imageClamped
      if (current === null) {
        return
      }
      if (gesture.kind === 'drawing') {
        const next = createDrawnMark(
          tool,
          { x: gesture.startImageX, y: gesture.startImageY },
          current,
          color,
          stroke,
          blockSize,
        )
        if (next === null) {
          return
        }
        const list = [...annotationsRef.current, next]
        applyHistory(list)
        // LOCK_KEEPS_TOOL: with the lock on, the tool stays and nothing is selected.
        if (!toolLocked) {
          commitSelection(list.length - 1, list)
        }
        return
      }
      const originMark = gesture.origin[gesture.index]
      if (originMark === undefined) {
        return
      }
      const moved = Math.hypot(event.cssX - gesture.startCssX, event.cssY - gesture.startCssY)
      if (moved < DRAG_THRESHOLD_CSS) {
        return
      }
      let nextMark: Annotation | null = originMark
      if (gesture.kind === 'moving') {
        nextMark = translateBody(
          originMark,
          current.x - gesture.startImageX,
          current.y - gesture.startImageY,
          imageW,
          imageH,
        )
      } else if (gesture.kind === 'resizing') {
        nextMark = resizeMark(originMark, gesture.handle, current, imageW, imageH)
      } else if (gesture.end !== undefined) {
        nextMark = moveEndpoint(originMark, gesture.end, current, imageW, imageH)
      }
      if (nextMark === null || JSON.stringify(nextMark) === JSON.stringify(originMark)) {
        return
      }
      applyHistory(replaceAt(gesture.origin, gesture.index, nextMark))
      setSelectedIndex(gesture.index)
      // A text corner scale changes font_size, so the inspector re-reads the committed mark.
      inspectMark(gesture.index)
      return
    }
    if (event.phase === 'move' && gesture === null) {
      // HOVER_CURSOR: an idle pointer over a resize handle of the selected mark names that handle.
      const hover =
        tool === 'select'
          ? hitTestMarks({
              cssX: event.cssX,
              cssY: event.cssY,
              scale: event.scale,
              ox: event.ox,
              oy: event.oy,
              imageW,
              imageH,
              annotations: annotationsRef.current,
              selectedIndex,
            })
          : null
      setHoverHandle(hover?.kind === 'resize' ? hover.handle : null)
    }
    if (gesture === null || gesture.epoch !== imageEpoch || gesture.shotId !== (selectedId ?? '')) {
      return
    }
    const current = event.imageClamped
    if (current === null) {
      return
    }
    if (event.phase === 'move') {
      if (gesture.kind === 'drawing') {
        const draft = createDrawnMark(
          tool,
          { x: gesture.startImageX, y: gesture.startImageY },
          current,
          color,
          stroke,
          blockSize,
        )
        setPreview(draft)
        return
      }
      const moved = Math.hypot(event.cssX - gesture.startCssX, event.cssY - gesture.startCssY)
      if (moved < DRAG_THRESHOLD_CSS) {
        return
      }
      const originMark = gesture.origin[gesture.index]
      if (originMark === undefined) {
        return
      }
      if (gesture.kind === 'moving') {
        const next = translateBody(
          originMark,
          current.x - gesture.startImageX,
          current.y - gesture.startImageY,
          imageW,
          imageH,
        )
        setPreview(next)
        return
      }
      if (gesture.kind === 'resizing') {
        setPreview(resizeMark(originMark, gesture.handle, current, imageW, imageH))
        return
      }
      if (gesture.end === undefined) {
        return
      }
      setPreview(moveEndpoint(originMark, gesture.end, current, imageW, imageH))
      return
    }
  }

  function changeStroke(value: string): void {
    finishSize()
    setStroke(value)
    const parsed = parsePositiveInt(value)
    if (parsed === null || selectedIndex === null) {
      return
    }
    const mark = annotationsRef.current[selectedIndex]
    if (mark === undefined || (mark.type !== 'arrow' && mark.type !== 'rect')) {
      return
    }
    if (mark.stroke_width === parsed) {
      return
    }
    applyHistory(replaceAt(annotationsRef.current, selectedIndex, { ...mark, stroke_width: parsed }))
  }

  /** BLOCK_CONTROL: as changeStroke; a valid block applied to a selected pixelate is one undo step. */
  function changeBlockSize(value: string): void {
    setBlockSize(value)
    const parsed = parseBlockSize(value)
    if (parsed === null || selectedIndex === null) {
      return
    }
    const mark = annotationsRef.current[selectedIndex]
    if (mark === undefined || mark.type !== 'pixelate' || mark.block_size === parsed) {
      return
    }
    applyHistory(replaceAt(annotationsRef.current, selectedIndex, { ...mark, block_size: parsed }))
  }

  function changeFontSize(value: string): void {
    finishSize()
    setFontSize(value)
    const parsed = parsePositiveInt(value)
    if (parsed === null || selectedIndex === null) {
      return
    }
    const mark = annotationsRef.current[selectedIndex]
    if (mark === undefined || mark.type !== 'text' || mark.font_size === parsed) {
      return
    }
    applyHistory(replaceAt(annotationsRef.current, selectedIndex, { ...mark, font_size: parsed }))
  }

  function changeTextBg(value: string): void {
    const trimmed = value.trim()
    const nextValue =
      trimmed.length === 0 ? '' : (normalizeHex(trimmed) ?? hexForNamedColor(trimmed) ?? trimmed)
    setTextBg(nextValue)
    if (selectedIndex === null) {
      return
    }
    const mark = annotationsRef.current[selectedIndex]
    if (mark === undefined || mark.type !== 'text') {
      return
    }
    const nextBg = nextValue.length > 0 ? nextValue : null
    if (mark.bg_color === nextBg) {
      return
    }
    applyHistory(replaceAt(annotationsRef.current, selectedIndex, { ...mark, bg_color: nextBg }))
  }

  function applyColor(): void {
    const hex = normalizeHex(candidate)
    if (hex === null) {
      return
    }
    setNamedPreview(false)
    setColor(hex)
    setCandidate(hex)
    if (selectedIndex === null) {
      return
    }
    const mark = annotationsRef.current[selectedIndex]
    if (mark === undefined || !('color' in mark) || displayHex(mark.color) === hex) {
      return
    }
    applyHistory(replaceAt(annotationsRef.current, selectedIndex, { ...mark, color: hex }))
  }

  function cancelColor(): void {
    setNamedPreview(false)
    setCandidate(colorBaseline)
  }

  function removeSelectedMark(): void {
    if (selectedIndex === null || editingText) {
      return
    }
    const next = annotationsRef.current.filter((_, index) => index !== selectedIndex)
    applyHistory(next)
    setSelectedIndex(null)
    nudgeTargetRef.current = 'body'
    // As an empty-click deselect: the removed mark's color must not linger as an unapplied candidate.
    setNamedPreview(false)
    setCandidate(displayHex(color))
  }

  function nudgeSelected(dx: number, dy: number): void {
    finishSize()
    if (selectedIndex === null) {
      return
    }
    const imageW = selected?.width ?? 0
    const imageH = selected?.height ?? 0
    const mark = annotationsRef.current[selectedIndex]
    if (mark === undefined) {
      return
    }
    if (nudgeBurstRef.current === null) {
      nudgeBurstRef.current = annotationsRef.current
      setTxOpen(true)
    }
    let next: Annotation | null = mark
    const nudgeTarget = nudgeTargetRef.current
    if (nudgeTarget === 'body' || mark.type !== 'arrow') {
      next = translateBody(mark, dx, dy, imageW, imageH)
    } else {
      const end = nudgeTarget === 'from' ? mark.from : mark.to
      next = moveEndpoint(mark, nudgeTarget, { x: end[0] + dx, y: end[1] + dy }, imageW, imageH)
    }
    if (next === null) {
      return
    }
    const list = replaceAt(annotationsRef.current, selectedIndex, next)
    setAnnotations(list)
    annotationsRef.current = list
  }

  function finishNudge(): void {
    const origin = nudgeBurstRef.current
    if (origin === null) {
      return
    }
    nudgeBurstRef.current = null
    setTxOpen(false)
    if (JSON.stringify(origin) === JSON.stringify(annotationsRef.current)) {
      return
    }
    overlayEditGen.current += 1
    setPast((stack) => [...stack, origin])
    setFuture([])
  }

  /** SIZE_BURST: one scrub step. The first step of a gesture records the start; the selected mark follows live. */
  function previewSize(field: SizeBurst['field'], value: number): void {
    if (gestureRef.current !== null) {
      return
    }
    finishNudge()
    if (sizeBurstRef.current !== null && sizeBurstRef.current.field !== field) {
      finishSize()
    }
    let burst = sizeBurstRef.current
    if (burst === null) {
      const mark = selectedIndex !== null ? annotationsRef.current[selectedIndex] : undefined
      const applies =
        mark !== undefined &&
        (field === 'stroke' ? mark.type === 'arrow' || mark.type === 'rect' : mark.type === 'text')
      burst = {
        field,
        startText: field === 'stroke' ? stroke : fontSize,
        origin: applies ? annotationsRef.current : null,
        index: applies ? selectedIndex : null,
      }
      sizeBurstRef.current = burst
      if (applies) {
        setTxOpen(true)
      }
    }
    if (field === 'stroke') {
      setStroke(String(value))
    } else {
      setFontSize(String(value))
    }
    if (burst.index === null) {
      return
    }
    const mark = annotationsRef.current[burst.index]
    let next: Annotation | null = null
    if (field === 'stroke' && mark !== undefined && (mark.type === 'arrow' || mark.type === 'rect')) {
      next = { ...mark, stroke_width: value }
    } else if (field === 'font' && mark !== undefined && mark.type === 'text') {
      next = { ...mark, font_size: value }
    }
    if (next === null) {
      return
    }
    const list = replaceAt(annotationsRef.current, burst.index, next)
    setAnnotations(list)
    annotationsRef.current = list
  }

  /** SIZE_BURST: end the open scrub as one undo step. Idempotent; runs first in every handler that writes the marks. */
  function finishSize(): void {
    const burst = sizeBurstRef.current
    if (burst === null) {
      return
    }
    sizeBurstRef.current = null
    setSizeEpoch((epoch) => ({ ...epoch, [burst.field]: epoch[burst.field] + 1 }))
    const origin = burst.origin
    if (origin === null) {
      return
    }
    setTxOpen(false)
    if (JSON.stringify(origin) === JSON.stringify(annotationsRef.current)) {
      return
    }
    overlayEditGen.current += 1
    setPast((stack) => [...stack, origin])
    setFuture([])
  }

  /** SIZE_BURST: drop the open scrub, restoring the field text and the marks. Idempotent. */
  function cancelSize(): void {
    const burst = sizeBurstRef.current
    if (burst === null) {
      return
    }
    sizeBurstRef.current = null
    setSizeEpoch((epoch) => ({ ...epoch, [burst.field]: epoch[burst.field] + 1 }))
    if (burst.field === 'stroke') {
      setStroke(burst.startText)
    } else {
      setFontSize(burst.startText)
    }
    if (burst.origin === null) {
      return
    }
    setTxOpen(false)
    setAnnotations(burst.origin)
    annotationsRef.current = burst.origin
  }

  // HISTORY_ACTIONS: the Undo and Redo buttons and the history chords share these steps.
  function undo(): void {
    if (txOpen || editingText) {
      return
    }
    const prev = past[past.length - 1]
    if (prev === undefined) {
      return
    }
    setPast(past.slice(0, -1))
    setFuture([annotations, ...future])
    setAnnotations(prev)
    annotationsRef.current = prev
    setSelectedIndex(null)
    nudgeTargetRef.current = 'body'
    setPreview(null)
  }

  function redo(): void {
    if (txOpen || editingText) {
      return
    }
    const next = future[0]
    if (next === undefined) {
      return
    }
    setFuture(future.slice(1))
    setPast([...past, annotations])
    setAnnotations(next)
    annotationsRef.current = next
    setSelectedIndex(null)
    nudgeTargetRef.current = 'body'
    setPreview(null)
  }

  function handleEditorKey(event: KeyboardEvent): void {
    if (recording || textDraft !== null) {
      return
    }
    if (event.isComposing) {
      return
    }
    if (cropRef.current !== null) {
      handleCropKey(event)
      return
    }
    const history = historyChord(event)
    if (history !== null) {
      // Outside HISTORY_FOCUS the key stays the field's or the menu's: no preventDefault.
      if (confirm !== null || !historyOwnsFocus()) {
        return
      }
      event.preventDefault()
      // A size transaction or a live pointer gesture owns the marks until it ends.
      if (txOpen || gestureRef.current !== null) {
        return
      }
      if (history === 'undo') {
        undo()
      } else {
        redo()
      }
      return
    }
    if (event.key === 'Escape') {
      event.preventDefault()
      gestureRef.current = null
      setPreview(null)
      setTxOpen(false)
      if (colorDirty) {
        cancelColor()
      }
      if (nudgeBurstRef.current !== null) {
        setAnnotations(nudgeBurstRef.current)
        annotationsRef.current = nudgeBurstRef.current
        nudgeBurstRef.current = null
      }
      cancelSize()
      return
    }
    if (event.key === 'Delete' && annotationOwnsFocus() && selectedIndex !== null && textDraft === null) {
      event.preventDefault()
      removeSelectedMark()
      return
    }
    if (selectedIndex === null || !annotationOwnsFocus() || textDraft !== null) {
      return
    }
    if (event.key === 'Enter') {
      // TEXT_REEDIT: plain Enter on a selected text mark reopens its text; on any other mark it stays inert.
      const plain = !event.ctrlKey && !event.metaKey && !event.altKey && !event.shiftKey && !event.repeat
      if (
        plain &&
        event.type === 'keydown' &&
        annotationsRef.current[selectedIndex]?.type === 'text' &&
        confirm === null &&
        !txOpen &&
        gestureRef.current === null
      ) {
        event.preventDefault()
        openTextEdit(selectedIndex)
      }
      return
    }
    let dx = 0
    let dy = 0
    if (event.key === 'ArrowRight') {
      dx = KEYBOARD_NUDGE_PX
    } else if (event.key === 'ArrowLeft') {
      dx = -KEYBOARD_NUDGE_PX
    } else if (event.key === 'ArrowDown') {
      dy = KEYBOARD_NUDGE_PX
    } else if (event.key === 'ArrowUp') {
      dy = -KEYBOARD_NUDGE_PX
    } else {
      return
    }
    event.preventDefault()
    // A live pointer gesture owns the mark until pointerup; a nudge now would fork its origin.
    if (gestureRef.current !== null) {
      return
    }
    if (event.type === 'keydown') {
      nudgeSelected(dx, dy)
    }
  }

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      handleEditorKey(event)
    }
    const onKeyUp = (event: KeyboardEvent) => {
      if (event.key.startsWith('Arrow')) {
        finishNudge()
      }
    }
    window.addEventListener('keydown', onKeyDown)
    window.addEventListener('keyup', onKeyUp)
    return () => {
      window.removeEventListener('keydown', onKeyDown)
      window.removeEventListener('keyup', onKeyUp)
    }
  })

  async function run(work: () => Promise<void>): Promise<void> {
    try {
      await work()
      setError(null)
    } catch (caught) {
      const message =
        caught instanceof ApiError || caught instanceof Error ? caught.message : String(caught)
      setError(message)
      logRenderer('ERROR', message)
    }
  }

  const banner = HOTKEY_IN_USE_TEMPLATE.replace('{accelerator}', settings.form.hotkey)
  const pendingHex = normalizeHex(candidate)
  const applyEnabled = pendingHex !== null && pendingHex !== colorBaseline

  function cancelConfirm(): void {
    setConfirm(null)
    setPendingSelect(null)
    setPendingRange(null)
    setDeleteTargets([])
  }

  /** COPY_STATUS: the notice is keyed to the editor's shot, because the menu never changes the selection. */
  function reportCopy(target: CaptureListItem, work: () => Promise<string>): void {
    const shotId = selectedId
    void (async () => {
      try {
        const text = await work()
        setError(null)
        if (shotId !== null) {
          setNotice({ shotId, text })
        }
      } catch (caught) {
        const message = `Could not copy ${target.display_name}: ${copyErrorMessage(caught)}`
        setError(message)
        logRenderer('ERROR', message)
      }
    })()
  }

  const filmstripActions: FilmstripShotActions = {
    onCopyPath: (target) => {
      reportCopy(target, async () => {
        await window.api.writeClipboardText(target.original_path)
        return `Copied the path of ${target.display_name}.`
      })
    },
    onCopyImage: (target) => {
      reportCopy(target, async () => {
        const writeImage = window.api.writeClipboardImage
        if (writeImage === undefined) {
          throw new Error(COPY_IMAGE_UNAVAILABLE)
        }
        await writeImage(await loadClipboardPng(target.id))
        return `Copied ${target.display_name} as an image.`
      })
    },
    onDelete: (target) => {
      setDeleteTargets([target.id])
      setConfirm('delete')
    },
    onDeleteRange: () => {
      setDeleteTargets(rangeIds)
      setConfirm('delete')
    },
  }

  /** BATCH_DELETE then BATCH_RESULT: report every failure; NEXT_SELECTION if the editor's shot went. */
  async function deleteRange(targets: string[]): Promise<void> {
    const order = sortFilmstrip(items).map((item) => item.id)
    const nameOf = (id: string): string => items.find((item) => item.id === id)?.display_name ?? id
    const result = await deleteCaptures(targets, removeCapture)
    applyRange({ anchorId: null, rangeIds: [] })
    const gone = new Set(result.deleted)
    let shown = selectedId
    if (shown !== null && gone.has(shown)) {
      shown = order.find((id) => !gone.has(id)) ?? null
      setSelectedId(shown)
      setViewVariant('original')
      setTextDraft(null)
      setPast([])
      setFuture([])
    }
    if (result.failed.length > 0) {
      const failures = result.failed.map((failure) => `${nameOf(failure.id)}: ${failure.message}`).join('; ')
      throw new Error(`Deleted ${result.deleted.length} of ${targets.length} shots. Could not delete ${failures}`)
    }
    setNotice({ shotId: shown, text: `Deleted ${targets.length} shots.` })
  }

  function acceptConfirm(): void {
    finishSize()
    const kind = confirm
    const nextId = pendingSelect
    const targets = deleteTargets
    const nextRange = pendingRange
    setConfirm(null)
    setPendingSelect(null)
    setPendingRange(null)
    setDeleteTargets([])
    if (kind === 'dirty' && nextId !== null) {
      if (nextRange !== null) {
        applyRange(nextRange)
      }
      setSelectedId(nextId)
      setNotice(null)
      setViewVariant('original')
      setPast([])
      setFuture([])
      setTextDraft(null)
    }
    if (kind === 'delete' && targets.length === 1) {
      // SINGLE_DELETE: only deleting the editor's own shot clears the selection.
      const id = targets[0] as string
      const wasSelected = id === selectedId
      void run(async () => {
        await deleteCapture(id)
        if (wasSelected) {
          setSelectedId(null)
        }
      })
    }
    if (kind === 'delete' && targets.length > 1) {
      void run(() => deleteRange(targets))
    }
    if (kind === 'flatten' && selectedId !== null) {
      const id = selectedId
      const before = backupPath
      void run(async () => {
        const detail = await flattenCapture(id)
        setViewVariant('original')
        if (detail.id !== id) {
          // CONVERT_ON_APPLY: the new PNG copy becomes the selection; the original stays.
          setSelectedId(detail.id)
          setNotice({ shotId: detail.id, text: flattenStatus({ kind: 'convert', displayName: detail.display_name }) })
          return
        }
        setNotice({
          shotId: id,
          text: flattenStatus({ kind: 'flatten', backupBefore: before, backupAfter: detail.backup_path }),
        })
        setDetailRevision((value) => value + 1)
      })
    }
    if (kind === 'revert' && selectedId !== null && backupPath !== null) {
      const id = selectedId
      const used = backupPath
      void run(async () => {
        await revertCapture(id)
        setViewVariant('original')
        setNotice({ shotId: id, text: flattenStatus({ kind: 'revert', backupPath: used }) })
        setDetailRevision((value) => value + 1)
      })
    }
  }

  /** DELETE_CONFIRM_TEXT: a menu target other than the editor's shot is named; a batch is counted. */
  function deleteConfirmText(): string {
    if (deleteTargets.length > 1) {
      return `Delete ${deleteTargets.length} captures and their files from disk?`
    }
    const only = deleteTargets.length === 1 ? deleteTargets[0] : undefined
    const named = only !== undefined && only !== selectedId ? items.find((item) => item.id === only) : undefined
    if (named !== undefined) {
      return `Delete "${named.display_name}" and its files from disk?`
    }
    return 'Delete this capture and its files from disk?'
  }

  function confirmSpec(kind: ConfirmKind): ConfirmSpec {
    switch (kind) {
      case 'dirty':
        return {
          message: 'Discard unsaved overlay marks on this shot?',
          cancelId: 'capture-dirty-confirm-cancel',
          acceptId: 'capture-dirty-confirm',
          acceptLabel: 'Confirm',
        }
      case 'delete':
        return {
          message: deleteConfirmText(),
          cancelId: 'capture-delete-confirm-cancel',
          acceptId: 'capture-delete-confirm',
          acceptLabel: deleteTargets.length > 1 ? `Delete ${deleteTargets.length} captures` : 'Delete capture',
        }
      case 'flatten':
        return {
          message: flattenConfirmText({
            displayName: selected?.display_name ?? '',
            originalPath: selected?.original_path ?? '',
            backupEnabled: settings.form.flatten_backup,
            backupDir: settings.form.backup_dir,
          }),
          cancelId: 'capture-flatten-confirm-cancel',
          acceptId: 'capture-flatten-confirm',
          acceptLabel: 'Apply to image',
        }
      case 'revert':
        return {
          message: revertConfirmText(selected?.display_name ?? '', backupPath ?? ''),
          cancelId: 'capture-revert-confirm-cancel',
          acceptId: 'capture-revert-confirm',
          acceptLabel: 'Revert image',
        }
      default:
        return assertNever(kind)
    }
  }

  // Inline confirmation strip (Phase 11 §05 CP 23–24): same text, same IDs, same handlers as the
  // former portal. CONFIRM_EXCLUSIVITY keeps the filmstrip, Delete, Apply and Revert disabled while open.
  const spec = confirm !== null ? confirmSpec(confirm) : null
  const confirmStrip =
    spec !== null ? (
      <div
        data-testid="capture-confirm-strip"
        role="group"
        aria-labelledby="capture-confirm-message"
        className="flex shrink-0 flex-wrap items-center gap-2 rounded-[var(--radius-control)] border border-border bg-bg-elevated px-3 py-2"
      >
        <p id="capture-confirm-message" className="flex-1 text-sm">
          {spec.message}
        </p>
        <Button
          ref={confirmCancelRef}
          data-testid={spec.cancelId}
          variant="outline"
          size="sm"
          onClick={cancelConfirm}
        >
          Cancel
        </Button>
        <Button data-testid={spec.acceptId} variant="destructive" size="sm" onClick={acceptConfirm}>
          {spec.acceptLabel}
        </Button>
      </div>
    ) : null

  const paintedAnnotations = (() => {
    if (preview === null || gestureRef.current === null || gestureRef.current.kind === 'drawing') {
      return annotations
    }
    return replaceAt(annotations, gestureRef.current.index, preview)
  })()
  const drawingPreview = preview !== null && gestureRef.current?.kind === 'drawing' ? preview : null
  const cropStatus = cropLive?.busy === true ? CROP_BUSY_MESSAGE : null
  const editorStatus =
    error ??
    cropStatus ??
    (textDraft !== null
      ? TEXT_GATE_MESSAGE
      : applyEnabled || colorDirty
        ? COLOR_GATE_MESSAGE
        : notice !== null && notice.shotId === selectedId
          ? notice.text
          : rangeIds.length > 1
            ? `${rangeIds.length} shots selected`
            : '')

  const settingsSaveLabel = settings.isDirty ? 'Save settings •' : 'Save settings'
  const shotCount = `${items.length} ${items.length === 1 ? 'shot' : 'shots'}`
  const shotInfo = selected !== null ? `${selected.display_name} · ${selected.width}×${selected.height}` : ''

  const apply = applyState({
    selected: selected !== null,
    savedCount: saved.length,
    dirty,
    confirmOpen: confirm !== null,
    originalPath: selected?.original_path ?? '',
  })
  const revert = revertState({ dirty, confirmOpen: confirm !== null })

  function saveOverlay(): void {
    void (async () => {
      try {
        if (!canSaveRef.current) {
          return
        }
        const savedOk = await saveAnnotations()
        if (savedOk) {
          setSaved(annotationsRef.current)
          setBaked(true)
          setError(null)
        }
      } catch (caught: unknown) {
        const message =
          caught instanceof ApiError || caught instanceof Error ? caught.message : String(caught)
        setError(message)
        logRenderer('ERROR', message)
      }
    })()
  }

  // Per-shot actions (CAPTURE_SOURCE_LOCATION, ACTION_ORDER): rendered here, placed at the end of the marks row.
  // Each icon button's Tooltip wrapper takes the pointer while it is disabled and renders the reason (A-6/A-10).
  const shotActions = (
    <>
      {dirty ? (
        <ToolbarIconButton
          spec={ACTION_BUTTONS['capture-save']}
          id="capture-save"
          variant="primary"
          shortcut="Ctrl+S"
          disabled={!canSave}
          onClick={saveOverlay}
        />
      ) : null}
      <ToolbarIconButton
        spec={ACTION_BUTTONS['capture-apply-image']}
        id="capture-apply-image"
        variant="secondary"
        reason={apply.title}
        disabled={!apply.enabled}
        onClick={() => {
          setConfirm('flatten')
        }}
      />
      {backupPath !== null ? (
        <ToolbarIconButton
          spec={ACTION_BUTTONS['capture-revert-image']}
          id="capture-revert-image"
          variant="secondary"
          reason={revert.title}
          disabled={!revert.enabled}
          onClick={() => {
            setConfirm('revert')
          }}
        />
      ) : null}
      <ToolbarIconButton
        spec={ACTION_BUTTONS['capture-open-file']}
        id="capture-open-file"
        variant="ghost"
        disabled={selected === null}
        onClick={() => {
          void run(async () => {
            await openCaptureFile()
          })
        }}
      />
      <ToolbarIconButton
        spec={ACTION_BUTTONS['capture-open-folder']}
        id="capture-open-folder"
        variant="ghost"
        disabled={selected === null && settings.form.inbox_dir.length < 1}
        onClick={() => {
          void run(async () => {
            await openCaptureFolder()
          })
        }}
      />
      <span
        role="separator"
        aria-orientation="vertical"
        data-testid="capture-actions-separator"
        className="mx-1 h-5 w-px shrink-0 bg-border"
      />
      <ToolbarIconButton
        spec={ACTION_BUTTONS['capture-delete']}
        id="capture-delete"
        variant="destructive"
        disabled={selectedId === null || confirm !== null}
        onClick={() => {
          setDeleteTargets(selectedId !== null ? [selectedId] : [])
          setConfirm('delete')
        }}
      />
    </>
  )

  return (
    <section
      data-testid="capture-page"
      className="flex min-h-full w-full max-w-[var(--layout-page-max-width)] flex-col gap-4 p-4"
      onDragOver={(event) => {
        // IMPORT_DROP: a file drag is always taken, so a dropped file never navigates the window.
        if (!dragHasFiles(event.dataTransfer)) {
          return
        }
        event.preventDefault()
        event.dataTransfer.dropEffect = importBlocked() ? 'none' : 'copy'
      }}
      onDrop={(event) => {
        if (!dragHasFiles(event.dataTransfer)) {
          return
        }
        event.preventDefault()
        if (importBlocked()) {
          return
        }
        const entries = Array.from(event.dataTransfer.files).map((file) => ({
          path: window.api.getPathForFile(file),
          name: file.name,
        }))
        // A failed run leaves its note unset; importFiles itself never rejects.
        void runImport(async () => entries).catch(() => undefined)
      }}
    >
      <HelpCard feature="capture" tabKey="main" sections={CAPTURE_HELP_SECTIONS} />
      <div data-testid="capture-header" className="flex flex-nowrap items-center gap-3">
        <Button
          data-testid="capture-region"
          variant="primary"
          size="md"
          aria-keyshortcuts={ariaKeyshortcuts('Ctrl+Enter')}
          title="Capture region (Ctrl+Enter)"
          onClick={() => {
            void run(async () => {
              await invokeCaptureRegion()
            })
          }}
        >
          Capture region
          {hotkeyCap !== null ? (
            <kbd
              data-testid="capture-hotkey-keycap"
              className="ml-2 rounded border border-accent-fg/40 px-1 font-mono text-xs leading-[1.125rem]"
            >
              {hotkeyCap}
            </kbd>
          ) : null}
        </Button>
        <Button
          data-testid="capture-import"
          variant="secondary"
          size="md"
          title={crop !== null ? CROP_REASON : IMPORT_TITLE}
          disabled={crop !== null || confirm !== null}
          loading={importBusy}
          onClick={() => {
            if (importBlocked()) {
              return
            }
            // IMPORT_BUTTON (D-552): the existing multi-select dialog, filtered to IMPORT_TYPES.
            void runImport(async () => {
              const paths = await window.api.showFilesDialog([{ name: 'Images', extensions: [...IMPORT_EXTENSIONS] }])
              return paths.map((path) => ({ path, name: path }))
            }).catch(() => undefined)
          }}
        >
          <ImagePlus size={16} aria-hidden="true" />
          Import image…
        </Button>
        <p className="min-w-0 truncate text-sm text-fg-muted">
          {shotCount} · inbox {settings.form.inbox_dir}
        </p>
        {/* HEADER_STATUS: the in-use banner sits in the header row and is mounted only while it has text. */}
        {hotkeyInUse ? (
          <p data-testid="capture-hotkey-banner" role="status" className="flex shrink-0 items-center gap-2 text-sm">
            <StatusChip label="Hotkey" tone="warning" />
            <span>{banner}</span>
          </p>
        ) : null}
        <Disclosure
          id="capture-settings"
          title="Options"
          variant="secondary"
          icon={<SlidersHorizontal size={16} aria-hidden="true" />}
          chevron
          open={settingsOpen}
          onOpenChange={setSettingsOpen}
          testId="capture-settings-toggle"
          className="flex min-w-0 flex-1 flex-col items-end gap-2"
        >
          <div className="flex flex-wrap items-end gap-3">
            <PathRow
              id="capture-inbox-path-field"
              label="Inbox"
              value={settings.form.inbox_dir}
              onChange={(value) => {
                settings.patchForm({ inbox_dir: value })
              }}
              onBrowse={() => {
                void (async () => {
                  const chosen = await window.api.showDirectoryDialog()
                  if (chosen === undefined) {
                    return
                  }
                  settings.patchForm({ inbox_dir: chosen })
                })()
              }}
              inputTestId="capture-inbox-path"
              browseTestId="capture-inbox-browse"
              className="w-[24rem] sm:grid-cols-[3.25rem_minmax(0,1fr)]! sm:items-center!"
            />
            <label className="flex items-center gap-2 text-sm">
              <span>Hotkey</span>
              <input
                data-testid="capture-hotkey"
                className="w-20 rounded border border-border bg-bg px-2 py-1 font-mono"
                value={settings.form.hotkey}
                readOnly={!recording}
                onKeyDown={(event) => {
                  if (!recording) {
                    return
                  }
                  event.preventDefault()
                  const accel = event.key.length === 1 ? event.key.toUpperCase() : event.key
                  settings.patchForm({ hotkey: accel })
                  setRecording(false)
                }}
              />
            </label>
            <Button
              data-testid="capture-hotkey-change"
              size="sm"
              onClick={() => {
                setRecording(true)
              }}
            >
              Change
            </Button>
            <Button
              data-testid="capture-page-save"
              variant="primary"
              size="sm"
              className={settings.saveClass}
              disabled={!settings.isDirty}
              onClick={() => {
                void run(async () => {
                  await settings.save()
                })
              }}
            >
              {settingsSaveLabel}
            </Button>
          </div>
        </Disclosure>
      </div>
      <BulkResultToast
        result={importNote}
        onDismiss={() => {
          setImportNote(null)
        }}
      />
      <div className="flex flex-1 gap-3 min-h-[16rem]">
        <aside className="w-[12.5rem] shrink-0">
          <CaptureFilmstrip
            items={items}
            selectedId={selectedId}
            selectedDirty={dirty}
            locked={confirm !== null}
            rangeIds={rangeIds}
            actions={filmstripActions}
            onSelect={(id, { extend }) => {
              const item = items.find((row) => row.id === id)
              if (item !== undefined) {
                filmstripChoice(item, extend)
              }
            }}
            onCheck={(id, { extend }) => {
              checkChoice(id, extend)
            }}
          />
        </aside>
        <CaptureViewport
          empty={items.length === 0}
          hasSelection={selectedId !== null}
          shotId={selectedId}
          overlayReady={overlayReady && imageEpoch > 0}
          actions={shotActions}
          confirmStrip={confirmStrip}
          emptyState={
            <p
              data-testid="capture-empty"
              className="flex min-h-[200px] flex-1 items-center justify-center rounded-[var(--radius-control)] border border-dashed border-border text-fg-muted"
            >
              {EMPTY_STATE}
            </p>
          }
          statusLine={
            <div className="flex shrink-0 items-center gap-3">
              <p data-testid="capture-status" className="h-5 min-w-0 flex-1 leading-5 truncate">{editorStatus}</p>
              <p data-testid="capture-shot-info" className="h-5 shrink-0 leading-5 text-xs text-fg-muted">{shotInfo}</p>
            </div>
          }
          imageUrl={viewportSrc}
          imageWidth={selected?.width ?? 0}
          imageHeight={selected?.height ?? 0}
          hasAnnotated={Boolean(selected?.annotated_path) || baked}
          viewVariant={viewVariant}
          tool={tool}
          color={candidate}
          stroke={stroke}
          fontSize={fontSize}
          textBg={textBg}
          blockSize={blockSize}
          annotations={paintedAnnotations}
          preview={drawingPreview}
          selectedIndex={selectedIndex}
          resizeCursor={selectedIndex !== null ? hoverHandle : null}
          canUndo={past.length > 0 && !txOpen && !editingText}
          canRedo={future.length > 0 && !txOpen && !editingText}
          textDraft={textDraft}
          colorApplyEnabled={applyEnabled}
          colorCancelEnabled={applyEnabled}
          onTool={chooseTool}
          toolLocked={toolLocked}
          onToggleToolLock={() => {
            setToolLocked((locked) => !locked)
          }}
          onColor={(value) => {
            setNamedPreview(false)
            setCandidate(value)
          }}
          onColorApply={applyColor}
          onColorCancel={cancelColor}
          onNamedColor={(name) => {
            const hex = hexForNamedColor(name)
            if (hex !== null) {
              setNamedPreview(true)
              setCandidate(hex)
            }
          }}
          onStroke={changeStroke}
          onFontSize={changeFontSize}
          onStrokePreview={(value) => {
            previewSize('stroke', value)
          }}
          onStrokeCommit={finishSize}
          onStrokeCancel={cancelSize}
          onFontSizePreview={(value) => {
            previewSize('font', value)
          }}
          onFontSizeCommit={finishSize}
          onFontSizeCancel={cancelSize}
          strokeEpoch={sizeEpoch.stroke}
          fontSizeEpoch={sizeEpoch.font}
          onTextBg={changeTextBg}
          onBlockSize={changeBlockSize}
          onViewVariant={setViewVariant}
          onUndo={undo}
          onRedo={redo}
          onTextDraftChange={(value) => {
            setTextDraft((current) => (current === null ? current : { ...current, value }))
          }}
          onTextCommit={() => {
            finishSize()
            if (textDraft === null || !draftCommits(textDraft, annotationsRef.current)) {
              // An empty or unchanged draft closes without a step.
              setTextDraft(null)
              return
            }
            const editIndex = textDraft.editIndex
            if (editIndex !== undefined) {
              // TEXT_REEDIT: the new text replaces the mark's in place as one step; every other field stays.
              const mark = annotationsRef.current[editIndex]
              setTextDraft(null)
              if (mark?.type === 'text') {
                const list = replaceAt(annotationsRef.current, editIndex, { ...mark, text: textDraft.value })
                applyHistory(list)
                commitSelection(editIndex, list)
              }
              return
            }
            const list: Annotation[] = [
              ...annotationsRef.current,
              {
                type: 'text',
                x: textDraft.x,
                y: textDraft.y,
                text: textDraft.value,
                color,
                font_size: Number.parseInt(fontSize, 10) || 16,
                bg_color: textBg.trim().length > 0 ? textBg : null,
              },
            ]
            applyHistory(list)
            setTextDraft(null)
            if (!toolLocked) {
              commitSelection(list.length - 1, list)
            }
          }}
          onTextCancel={() => {
            setTextDraft(null)
          }}
          onPointer={() => undefined}
          onSurfacePointer={handleSurfacePointer}
          onSelectIndex={(index) => {
            if (cropRef.current !== null) {
              return
            }
            finishSize()
            setSelectedIndex(index)
            setTool('select')
            nudgeTargetRef.current = 'body'
            inspectMark(index)
          }}
          onRemoveMark={removeSelectedMark}
          onHandleFocus={(end) => {
            nudgeTargetRef.current = end
          }}
          onSurfaceFocus={() => {
            // A pointerdown on a handle runs before the surface takes focus; keep the grabbed end.
            if (gestureRef.current === null) {
              nudgeTargetRef.current = 'body'
            }
          }}
          onEditorKey={handleEditorKey}
          crop={cropLive === null ? null : { box: cropLive.box, dragging: cropLive.drag !== null, cursor: cropLive.hover }}
          cropBar={
            cropLive === null ? undefined : (
              <CaptureCropBar
                box={cropLive.box}
                image={cropImage}
                aspect={cropLive.aspect}
                swapped={cropLive.swapped}
                busy={cropLive.busy}
                ratio={presetRatio(cropLive.aspect, cropImage, cropLive.swapped)}
                swapReason={
                  cropLive.aspect !== 'free' && !presetFeasible(cropLive.aspect, cropImage, !cropLive.swapped)
                    ? CROP_SWAP_REASON
                    : undefined
                }
                onAspect={chooseCropAspect}
                onSwap={swapCropBox}
                onBox={setCropBox}
                onReset={resetCrop}
                onCancel={closeCrop}
                onSave={commitCrop}
              />
            )
          }
          cropReason={cropReason}
          cropDisabledReason={cropDisabledReason}
          onToggleCrop={toggleCrop}
        />
      </div>
    </section>
  )
}
