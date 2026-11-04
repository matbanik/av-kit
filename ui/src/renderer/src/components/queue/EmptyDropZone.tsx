/**
 * Empty-queue drop target, plus the drag-state hook the populated list shares.
 *
 * Rejection is explained *during* the drag, not after the drop. A user who is
 * still holding the pointer can retarget; one who has already released has to
 * undo something. The zone therefore evaluates the payload on `dragenter` and
 * shows the reason inline while the pointer is over it.
 *
 * `dragenter`/`dragleave` fire for every descendant the pointer crosses, so a
 * depth counter — not a boolean — decides when the pointer has really left.
 * Without it the zone flickers each time the cursor passes over the Browse
 * button inside it.
 */
import { useCallback, useRef, useState, type DragEvent, type ReactElement } from 'react'

import { Button } from '../ui/Button'

/** The four states a queue drop target can be in. */
export const DRAG_STATES = ['idle', 'window-drag', 'direct-hover', 'invalid'] as const

export type DragState = (typeof DRAG_STATES)[number]

/** The parts of a `DataTransferItem` an accept predicate needs. */
export type DropCandidate = {
  /** `'file'` or `'string'`, as the platform reports it. */
  kind: string
  /** MIME type of the dragged item. */
  type: string
}

export type UseDropZoneOptions = {
  /** Decide whether the dragged payload may be dropped here. Defaults to accepting everything. */
  accept?: (items: readonly DropCandidate[]) => boolean
  /** Called with the dropped files once an accepted payload is released. */
  onDropFiles?: (files: readonly File[]) => void
  /** Whether a drag is in progress anywhere over the window. */
  windowDragActive?: boolean
}

/** Drag state plus the handlers to spread onto the drop target element. */
export type DropZoneBinding = {
  /** Current state, drawn from {@link DRAG_STATES}. */
  state: DragState
  /** Handlers to spread onto the element that acts as the drop target. */
  handlers: {
    onDragEnter: (event: DragEvent<HTMLElement>) => void
    onDragOver: (event: DragEvent<HTMLElement>) => void
    onDragLeave: (event: DragEvent<HTMLElement>) => void
    onDrop: (event: DragEvent<HTMLElement>) => void
  }
}

/**
 * Read the dragged items off an event without assuming a real `DataTransfer`.
 *
 * @param event - The drag event React handed us.
 * @returns The dragged items, or an empty list when the platform reported none.
 */
function readCandidates(event: DragEvent<HTMLElement>): DropCandidate[] {
  const transfer = event.dataTransfer as unknown as
    | { items?: ArrayLike<DropCandidate> }
    | null
    | undefined
  if (transfer === null || transfer === undefined || transfer.items === undefined) {
    return []
  }
  return Array.from(transfer.items)
}

/**
 * Read the dropped files off an event without assuming a real `DataTransfer`.
 *
 * @param event - The drop event React handed us.
 * @returns The dropped files, or an empty list.
 */
function readFiles(event: DragEvent<HTMLElement>): File[] {
  const transfer = event.dataTransfer as unknown as
    | { files?: ArrayLike<File> }
    | null
    | undefined
  if (transfer === null || transfer === undefined || transfer.files === undefined) {
    return []
  }
  return Array.from(transfer.files)
}

/**
 * Track drag state for one drop target.
 *
 * @param options - See {@link UseDropZoneOptions}.
 * @returns The current {@link DragState} and the handlers that maintain it.
 */
export function useDropZone(options: UseDropZoneOptions = {}): DropZoneBinding {
  const { accept, onDropFiles, windowDragActive = false } = options
  const depth = useRef(0)
  const [hovering, setHovering] = useState(false)
  const [accepted, setAccepted] = useState(true)

  const onDragEnter = useCallback(
    (event: DragEvent<HTMLElement>): void => {
      event.preventDefault()
      depth.current += 1
      if (depth.current === 1) {
        setAccepted(accept === undefined ? true : accept(readCandidates(event)))
        setHovering(true)
      }
    },
    [accept],
  )

  const onDragOver = useCallback((event: DragEvent<HTMLElement>): void => {
    // Without this the browser treats the element as a non-target and never
    // fires `drop`.
    event.preventDefault()
  }, [])

  const onDragLeave = useCallback((event: DragEvent<HTMLElement>): void => {
    event.preventDefault()
    depth.current = Math.max(0, depth.current - 1)
    if (depth.current === 0) {
      setHovering(false)
      setAccepted(true)
    }
  }, [])

  const onDrop = useCallback(
    (event: DragEvent<HTMLElement>): void => {
      event.preventDefault()
      depth.current = 0
      setHovering(false)
      const allowed = accept === undefined ? true : accept(readCandidates(event))
      setAccepted(true)
      if (allowed && onDropFiles !== undefined) {
        onDropFiles(readFiles(event))
      }
    },
    [accept, onDropFiles],
  )

  const state: DragState = hovering
    ? accepted
      ? 'direct-hover'
      : 'invalid'
    : windowDragActive
      ? 'window-drag'
      : 'idle'

  return { state, handlers: { onDragEnter, onDragOver, onDragLeave, onDrop } }
}

export type EmptyDropZoneProps = UseDropZoneOptions & {
  /** Open the host's file picker. */
  onBrowse: () => void
  /** Why the current payload cannot be dropped, shown while the drag is invalid. */
  rejectionReason?: string
  /** Headline microcopy. */
  title?: string
  /** Supporting microcopy under the headline. */
  hint?: string
  /** Override the default `data-testid`. */
  testId?: string
  /** Override the Browse button's `data-testid`. */
  browseTestId?: string
}

const zoneStateClasses: Record<DragState, string> = {
  idle: 'border-border text-fg-muted',
  'window-drag': 'border-accent/50 text-fg-muted',
  'direct-hover': 'border-accent bg-accent/5 text-fg',
  invalid: 'border-error text-error',
}

const zoneBaseClasses = [
  'flex flex-col items-center justify-center gap-2 px-6 py-10 text-center',
  'rounded-[var(--radius-lg)] border-2 border-dashed',
  'transition-[background-color,border-color,color] duration-[var(--duration-fast)] ease-[var(--ease-out)]',
].join(' ')

/**
 * Render the empty-queue drop target.
 *
 * Drag-and-drop is never the only route in: the Browse button is a real button
 * in the tab order, so the zone is operable by keyboard alone (WCAG 2.2 SC
 * 2.1.1).
 *
 * @param props - See {@link EmptyDropZoneProps}.
 * @returns The dashed drop zone with its microcopy and Browse affordance.
 */
export function EmptyDropZone({
  onBrowse,
  rejectionReason,
  title = 'Drop video files here',
  hint = 'Nothing is queued yet.',
  testId = 'empty-drop-zone',
  browseTestId = 'empty-drop-zone-browse',
  ...dropOptions
}: EmptyDropZoneProps): ReactElement {
  const { state, handlers } = useDropZone(dropOptions)
  const showRejection = state === 'invalid' && rejectionReason !== undefined

  return (
    <div
      className={[zoneBaseClasses, zoneStateClasses[state]].join(' ')}
      data-testid={testId}
      data-drag-state={state}
      {...handlers}
    >
      <p className="text-sm font-medium">{title}</p>
      <p className="text-xs">{hint}</p>
      <Button variant="secondary" size="sm" data-testid={browseTestId} onClick={onBrowse}>
        Browse files
      </Button>
      {showRejection ? (
        <p className="text-xs" data-drop-rejection="" role="status">
          {rejectionReason}
        </p>
      ) : null}
    </div>
  )
}
