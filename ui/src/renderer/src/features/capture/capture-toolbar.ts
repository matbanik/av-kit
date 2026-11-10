import {
  ArchiveRestore,
  ArrowLeftRight,
  Crop,
  Delete,
  Eraser,
  ExternalLink,
  FolderOpen,
  Grid3x3,
  Highlighter,
  Image as ImageIcon,
  Layers,
  Lock,
  Maximize,
  MousePointer2,
  MoveUpRight,
  Redo2,
  Save,
  Square,
  Stamp,
  Trash2,
  Type,
  Undo2,
  ZoomIn,
  ZoomOut,
  type LucideIcon,
} from 'lucide-react'

import type { Annotation } from './capture-annotate'
import type { CaptureTool } from './CaptureViewport'

/** One icon button of the Capture tools row: its lucide icon and accessible name (TOOLBAR_BUTTONS). */
export type ToolbarButtonSpec = {
  readonly icon: LucideIcon
  readonly name: string
}

/**
 * TOOLBAR_BUTTONS (Session 29 plan, spec 09 §Viewport toolbar icons and Options). Keyed by test id so
 * `CaptureViewport.tsx` renders each button with its literal id (AC-39.8 reads those literals).
 */
export const TOOLBAR_BUTTONS = {
  'capture-tool-select': { icon: MousePointer2, name: 'Select' },
  'capture-tool-arrow': { icon: MoveUpRight, name: 'Arrow' },
  'capture-tool-box': { icon: Square, name: 'Box' },
  'capture-tool-highlight': { icon: Highlighter, name: 'Highlight' },
  'capture-tool-text': { icon: Type, name: 'Text' },
  'capture-tool-pixelate': { icon: Grid3x3, name: 'Pixelate' },
  'capture-tool-eraser': { icon: Eraser, name: 'Eraser' },
  // TOOL_LOCK (MEU-87): a toggle, not a tool, so it is not in TOOL_BUTTON_IDS.
  'capture-tool-lock': { icon: Lock, name: 'Keep tool after drawing' },
  // CROP_ENTRY (MEU-131): a tool, after the lock in the row.
  'capture-tool-crop': { icon: Crop, name: 'Crop' },
  'capture-undo': { icon: Undo2, name: 'Undo' },
  'capture-redo': { icon: Redo2, name: 'Redo' },
  'capture-view-original': { icon: ImageIcon, name: 'Original' },
  'capture-view-annotated': { icon: Layers, name: 'Annotated' },
  'capture-zoom-out': { icon: ZoomOut, name: 'Zoom out' },
  'capture-zoom-in': { icon: ZoomIn, name: 'Zoom in' },
  'capture-zoom-fit': { icon: Maximize, name: 'Fit to view' },
} as const satisfies Record<string, ToolbarButtonSpec>

export type ToolbarButtonId = keyof typeof TOOLBAR_BUTTONS

/**
 * ACTION_BUTTONS (Session 34 plan, triage D-49): the icon actions of the marks row, keyed by test id, in
 * ACTION_ORDER. Disjoint from TOOLBAR_BUTTONS.
 */
export const ACTION_BUTTONS = {
  'capture-remove-mark': { icon: Delete, name: 'Remove mark' },
  'capture-save': { icon: Save, name: 'Save overlay' },
  'capture-apply-image': { icon: Stamp, name: 'Apply to image' },
  'capture-revert-image': { icon: ArchiveRestore, name: 'Revert image' },
  'capture-open-file': { icon: ExternalLink, name: 'Open file' },
  'capture-open-folder': { icon: FolderOpen, name: 'Open folder' },
  'capture-delete': { icon: Trash2, name: 'Delete shot' },
} as const satisfies Record<string, ToolbarButtonSpec>

export type ActionButtonId = keyof typeof ACTION_BUTTONS

/**
 * CROP_BUTTONS (MEU-131 CROP_BAR): the crop bar's icon buttons, keyed by test id. A record apart from
 * TOOLBAR_BUTTONS, which AC-80.8 expects on the page, and from ACTION_BUTTONS.
 */
export const CROP_BUTTONS: Record<string, ToolbarButtonSpec> = {
  'capture-crop-swap': { icon: ArrowLeftRight, name: 'Swap portrait and landscape' },
}

/** Every `CaptureTool` maps to exactly one toolbar button; a new tool fails the type check here. */
export const TOOL_BUTTON_IDS: Readonly<Record<CaptureTool, ToolbarButtonId>> = {
  select: 'capture-tool-select',
  arrow: 'capture-tool-arrow',
  box: 'capture-tool-box',
  highlight: 'capture-tool-highlight',
  text: 'capture-tool-text',
  pixelate: 'capture-tool-pixelate',
  eraser: 'capture-tool-eraser',
  crop: 'capture-tool-crop',
}

/** The option groups the contextual options row can show (OPTIONS_BY_TOOL, OPTIONS_BY_TOOL_V2). */
export type OptionGroup = 'color' | 'stroke' | 'text' | 'block'

function assertNever(value: never): never {
  throw new Error(`Unhandled capture tool: ${String(value)}`)
}

/** True when this tool, with this selection, edits a stroke width (only arrows and rects have one). */
function strokeApplies(tool: CaptureTool, selected: Annotation | null): boolean {
  switch (tool) {
    case 'arrow':
    case 'box':
      return true
    case 'select':
      return selected === null || selected.type === 'arrow' || selected.type === 'rect'
    case 'highlight':
    case 'text':
    case 'pixelate':
    case 'eraser':
    case 'crop':
      return false
    default:
      return assertNever(tool)
  }
}

/**
 * OPTIONS_BY_TOOL_V2: the option groups for the active tool and the selected mark, first rule that
 * matches. The crop has no option group (MEU-131 CROP_ENTRY); a pixelate (tool or selected mark) has
 * only its block size; an eraser has no option at all;
 * otherwise color is present and text options win over stroke, so the two are never shown together.
 */
export function optionGroups(tool: CaptureTool, selected: Annotation | null): readonly OptionGroup[] {
  if (tool === 'crop') {
    return []
  }
  if (tool === 'pixelate' || selected?.type === 'pixelate') {
    return ['block']
  }
  if (tool === 'eraser' || selected?.type === 'eraser') {
    return []
  }
  if (tool === 'text' || selected?.type === 'text') {
    return ['color', 'text']
  }
  return strokeApplies(tool, selected) ? ['color', 'stroke'] : ['color']
}
