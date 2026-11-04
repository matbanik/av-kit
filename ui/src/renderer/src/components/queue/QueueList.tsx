/**
 * Vertical list of {@link QueueCard} rows.
 *
 * The list renders `items` in the order it received them and never re-sorts:
 * queue order *is* execution order, and the backend owns it. Sorting here would
 * make the row a user drags to position 3 land somewhere else on the next poll.
 *
 * A populated list stays a drop target. Dragging files over it shows an overlay
 * *above* the rows rather than replacing them, so the user keeps the context of
 * what is already queued while deciding whether to add more.
 *
 * An empty queue is an invitation rather than a blank slate — but *which*
 * invitation is the host's decision, because the two queues have different
 * intake contracts (`EMPTY_STATE_CONTRACT`). A file-intake queue gets the dashed
 * `EmptyDropZone` and, once populated, the compact drop strip. A URL-intake
 * queue supplies its own `emptyState` and gets no file-drop invitation at all,
 * since offering one there could only be a no-op.
 *
 * Row reordering by drag is opt-in per consumer (`DND_OPT_IN_RULE`): it exists
 * only for a host that passes both `onMoveToIndex` and `queueKey`. The
 * transcript and TTS queues mount this same component with neither and get the
 * markup they have today, down to the absence of a drag handle.
 */
import { closestCenter, DndContext, KeyboardSensor, PointerSensor, useSensor, useSensors } from '@dnd-kit/core'
import {
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import {
  type CSSProperties,
  type ReactElement,
  type ReactNode,
  type Ref,
  useEffect,
  useRef,
} from 'react'

import { type ReorderQueueKey } from '../../lib/queue/reorder-single-flight'
import { useQueueReorderHeld } from '../../lib/queue/use-queue-reorder-held'
import { QueueCard, type QueueCardJob, type QueueCardProps, type QueueCardSlots } from './QueueCard'
import { EmptyDropZone, useDropZone, type DropCandidate } from './EmptyDropZone'
import { createQueueAnnouncements, queueScreenReaderInstructions } from './queue-dnd'

export type QueueListProps = Omit<
  QueueCardProps,
  | 'job'
  | 'testId'
  | 'isFirst'
  | 'isLast'
  | 'isInFlight'
  | 'selected'
  | 'detailOpen'
  | 'metaSegments'
  | 'drag'
  | keyof QueueCardSlots
> & {
  /** Jobs in the order the backend returned them. */
  items: readonly QueueCardJob[]
  /**
   * Page-owned meta columns appended to each card's shared meta line.
   *
   * Widened from the card's fixed array to *either* a fixed array or a
   * resolver, because the segments a page contributes differ row by row: the
   * converter's Kind/Mode/Speed/ETA come from each job's own fields, so one
   * array cannot serve the whole list. The resolver must be pure — it runs on
   * every render, once per row.
   */
  metaSegments?: readonly string[] | ((job: QueueCardJob) => readonly string[])
  /** Override the list's `data-testid`. */
  testId?: string
  /** `data-testid` for each row — the converter queue uses its own id. */
  rowTestId?: string
  /** Ids currently in the bulk selection. */
  selectedIds?: readonly string[]
  /** Id of the job the processor is working on, if any. */
  inFlightId?: string | null
  /** Id of the job whose detail panel is open, if any. */
  detailOpenId?: string | null
  /** Decide whether a dragged payload may be dropped onto the list. */
  accept?: (items: readonly DropCandidate[]) => boolean
  /** Called with the dropped files once an accepted payload is released. */
  onDropFiles?: (files: readonly File[]) => void
  /** Whether a drag is in progress anywhere over the window. */
  windowDragActive?: boolean
  /** Overlay copy shown while an accepted payload hovers the list. */
  dropOverlayLabel?: string
  /** Overlay copy shown while a rejected payload hovers the list. */
  dropRejectionLabel?: string
  /**
   * What an empty queue says, when the host owns that copy.
   *
   * Supplying this replaces the file-drop invitation entirely — it is how the
   * downloader renders `queue-empty-invite` instead of a drop zone it has no
   * intake for.
   */
  emptyState?: ReactNode
  /** Open the host's file picker. Renders the empty zone's Browse path. */
  onBrowse?: () => void
  /**
   * Move a row to an absolute final index (`MOVE_TO_INDEX_CONTRACT`).
   *
   * Supplying it — together with `queueKey` — is what turns drag reordering on.
   * The index is resolved against the array as it is currently rendered, and is
   * the position the row ends up in, not a post-removal offset.
   */
  onMoveToIndex?: (id: string, targetIndex: number) => void
  /**
   * Which single-flight gate this queue's reorders share
   * (`REORDER_SINGLE_FLIGHT_RULE`). Required alongside `onMoveToIndex`: without
   * it the handles could not tell that a reorder from some other affordance is
   * already on the wire.
   */
  queueKey?: ReorderQueueKey
  /**
   * Per-row `CARD_SLOTS` (`LIST_SLOT_RESOLVER`). Like the `metaSegments`
   * resolver, it must be pure: it runs on every render, once per row. Absent
   * means every card renders its default anatomy.
   */
  cardSlots?: (job: QueueCardJob) => QueueCardSlots
}

/** Spec microcopy for the converter's empty queue. */
const EMPTY_TITLE = 'Drop video or audio files here — or'
const EMPTY_HINT = 'Nothing is queued yet.'
/** Spec microcopy for the compact strip a populated queue keeps. */
const DROP_STRIP_LABEL = 'Drop files to add'

const listClasses = 'relative flex flex-col gap-2'

const stripClasses = [
  'rounded-[var(--radius-md)] border border-dashed border-border',
  'px-3 py-1.5 text-center text-xs text-fg-muted',
].join(' ')

const overlayClasses = [
  'pointer-events-none absolute inset-0 z-10 flex items-center justify-center',
  'rounded-[var(--radius-lg)] border-2 border-dashed bg-bg/80 text-sm',
].join(' ')

/** How the shell asks its host to turn one job's resolved props into a row. */
type RowRenderer = (job: QueueCardJob, cardProps: QueueCardProps) => ReactElement

type QueueListShellProps = Omit<QueueListProps, 'onMoveToIndex' | 'queueKey'> & {
  renderRow: RowRenderer
  listRef?: Ref<HTMLDivElement>
}

/**
 * Everything the list renders that is independent of whether rows can drag:
 * the drop-zone container, the empty state, the drop strip and the overlay.
 *
 * It is factored out so the draggable and static lists share one DOM shape
 * rather than two that have to be kept in sync by hand, and so the hooks a
 * draggable list needs live in a component that only exists when drag is on.
 */
function QueueListShell({
  items,
  testId = 'queue-list',
  rowTestId = 'queue-card',
  selectedIds,
  inFlightId,
  detailOpenId,
  accept,
  onDropFiles,
  windowDragActive,
  dropOverlayLabel = 'Drop files to add them to the queue',
  dropRejectionLabel = 'These files cannot be added to this queue',
  emptyState,
  onBrowse,
  metaSegments,
  cardSlots,
  renderRow,
  listRef,
  ...cardProps
}: QueueListShellProps): ReactElement {
  const { state, handlers } = useDropZone({ accept, onDropFiles, windowDragActive })
  const hovering = state === 'direct-hover' || state === 'invalid'
  const selection = selectedIds ?? []
  const lastIndex = items.length - 1
  // A file-drop affordance is only honest when the host actually accepts files.
  const acceptsFiles = onDropFiles !== undefined || onBrowse !== undefined
  const resolveSegments = (job: QueueCardJob): readonly string[] | undefined =>
    typeof metaSegments === 'function' ? metaSegments(job) : metaSegments

  return (
    <div ref={listRef} className={listClasses} data-testid={testId} data-drag-state={state} {...handlers}>
      {items.length === 0 && emptyState !== undefined ? emptyState : null}
      {items.length === 0 && emptyState === undefined && acceptsFiles ? (
        // The zone tracks its own drag state for styling, but the drop itself is
        // handled once, by the list container this zone sits inside.
        <EmptyDropZone
          testId="queue-empty-dropzone"
          browseTestId="queue-empty-browse"
          title={EMPTY_TITLE}
          hint={EMPTY_HINT}
          accept={accept}
          rejectionReason={dropRejectionLabel}
          onBrowse={() => {
            onBrowse?.()
          }}
        />
      ) : null}
      {items.map((job, index) =>
        renderRow(job, {
          ...cardProps,
          ...cardSlots?.(job),
          job,
          testId: rowTestId,
          metaSegments: resolveSegments(job),
          isFirst: index === 0,
          isLast: index === lastIndex,
          isInFlight: inFlightId === job.id,
          selected: selection.includes(job.id),
          detailOpen: detailOpenId === job.id,
        }),
      )}
      {items.length > 0 && acceptsFiles ? (
        <p className={stripClasses} data-testid="queue-drop-strip">
          {DROP_STRIP_LABEL}
        </p>
      ) : null}
      {hovering ? (
        <div
          className={[
            overlayClasses,
            state === 'invalid' ? 'border-error text-error' : 'border-accent text-fg',
          ].join(' ')}
          data-testid="queue-drop-overlay"
          role="status"
        >
          {state === 'invalid' ? dropRejectionLabel : dropOverlayLabel}
        </div>
      ) : null}
    </div>
  )
}

/**
 * One sortable row: the dnd-kit wrapper that carries the displacement, plus the
 * card it hands the activator surface to.
 *
 * `G33_RULE` — displacement is `transform` and `transition` and nothing else.
 * Animating geometry (`top`, `margin`, `height`) would reflow the whole list on
 * every frame of a drag, and on a long queue that is visible as jitter.
 *
 * @param props.cardProps - The row's resolved card props from the shell.
 * @param props.handleDisabled - Whether the queue's reorder gate is held.
 * @returns The wrapper element containing one {@link QueueCard}.
 */
function SortableQueueRow({
  cardProps,
  handleDisabled,
}: {
  cardProps: QueueCardProps
  handleDisabled: boolean
}): ReactElement {
  const { attributes, listeners, setNodeRef, setActivatorNodeRef, transform, transition, isDragging } =
    useSortable({ id: cardProps.job.id })

  /*
    `CSS.Transform.toString` is dnd-kit's own helper rather than a hand-rolled
    `translate3d`: the library changes what it emits (it drops scale for
    sortable rows, for one), and a local copy would drift from it silently.
  */
  const style: CSSProperties = {
    transform: CSS.Transform.toString(transform) ?? undefined,
    transition,
  }

  return (
    <div ref={setNodeRef} style={style}>
      <QueueCard
        {...cardProps}
        drag={{
          attributes,
          listeners,
          setActivatorNodeRef,
          isDragging,
          disabled: handleDisabled,
        }}
      />
    </div>
  )
}

/**
 * The list with row dragging on.
 *
 * `DRAG_STATE_ISOLATION_RULE`: `DndContext` **wraps** the drop-zone container
 * rather than merging into it. dnd-kit is pointer-events only and never fires
 * the native HTML5 drag events the drop zone listens for, so keeping them on
 * separate elements is what makes a row drag leave `data-drag-state` at `idle`
 * while a file drag still lights the list up.
 *
 * @param props - The list props, with drag guaranteed present.
 * @returns The list wrapped in its dnd-kit providers.
 */
function SortableQueueList(
  props: QueueListProps & {
    onMoveToIndex: (id: string, targetIndex: number) => void
    queueKey: ReorderQueueKey
  },
): ReactElement {
  const { items, onMoveToIndex, queueKey, ...shellProps } = props
  /*
    One subscription for the whole list rather than one per row: the gate is
    module-level state shared by every reorder affordance on the page, and every
    handle answers the same question about it.
  */
  const held = useQueueReorderHeld(queueKey)
  const ids = items.map((job) => job.id)
  const restoreFocusId = useRef<string | null>(null)
  const listRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    const id = restoreFocusId.current
    if (held || id === null) {
      return
    }
    restoreFocusId.current = null
    window.requestAnimationFrame(() => {
      const card = Array.from(listRef.current?.querySelectorAll<HTMLElement>('[data-job-id]') ?? []).find(
        (candidate) => candidate.dataset.jobId === id,
      )
      card?.querySelector<HTMLElement>('[data-testid="queue-card-drag-handle"]')?.focus()
    })
  }, [held, items])

  const sensors = useSensors(
    /*
      DND_SENSOR_CONFIG. The distance constraint is what keeps a click on a
      control inside the row from being stolen by drag activation; without it
      the kebab button becomes unreliable on the rows that can also drag.
    */
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  )

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      /*
        DND_AUTOSCROLL_CONFIG. dnd-kit's auto-scroller is on by default with
        `threshold: {x: 0.2, y: 0.2}` and `acceleration: 10` — a band covering
        the outer FIFTH of the nearest scrollable ancestor, scrolling up to
        10px every 5ms. The queue is not its own scroll container: the nearest
        one is the page shell's `<main>`, and the list sits near its bottom, so
        the default band swallows the rows themselves — grabbing a row and
        nudging it 20px down drives the shell to its maximum scroll before the
        pointer has reached the next row, and the drop lands on whatever row
        the scroll pulled underneath. Measured, not inferred: `scrollTop` went
        0 -> 100 -> 149 (its maximum) within two 10px pointer steps.

        `y: 0.05` keeps edge auto-scroll — it is what makes a drag past the
        visible list reachable — but confines it to a band the pointer has to
        be deliberately steered into, and `acceleration: 5` makes the scroll
        that follows steerable rather than a jump. `x: 0` switches the
        horizontal axis off outright: a vertical list has nowhere to go
        sideways, so any horizontal scroll here is a bug by definition.
      */
      autoScroll={{ threshold: { x: 0, y: 0.05 }, acceleration: 5 }}
      accessibility={{
        announcements: createQueueAnnouncements(
          items.map((job) => ({ id: job.id, title: job.title })),
        ),
        screenReaderInstructions: queueScreenReaderInstructions,
      }}
      onDragEnd={({ active, over }) => {
        /*
          A drop onto nothing, or onto the row's own position, is the identity
          permutation. Issuing it anyway would put a PUT on the wire that can
          only lose a race with whatever reorder comes next.
        */
        if (over === null || over === undefined || active.id === over.id) {
          return
        }
        const targetIndex = ids.indexOf(String(over.id))
        if (targetIndex === -1) {
          return
        }
        restoreFocusId.current = String(active.id)
        onMoveToIndex(String(active.id), targetIndex)
      }}
    >
      <SortableContext items={ids} strategy={verticalListSortingStrategy}>
        <QueueListShell
          {...shellProps}
          items={items}
          listRef={listRef}
          renderRow={(job, cardProps) => (
            <SortableQueueRow key={job.id} cardProps={cardProps} handleDisabled={held} />
          )}
        />
      </SortableContext>
    </DndContext>
  )
}

/**
 * Render the queue as a list of cards.
 *
 * @param props - See {@link QueueListProps}.
 * @returns The list element, with a drop overlay while a drag hovers it.
 */
export function QueueList(props: QueueListProps): ReactElement {
  const { onMoveToIndex, queueKey } = props
  if (onMoveToIndex !== undefined && queueKey !== undefined) {
    return <SortableQueueList {...props} onMoveToIndex={onMoveToIndex} queueKey={queueKey} />
  }

  /*
    DND_OPT_IN_RULE. No dnd-kit provider, no sortable wrapper element and no
    handle: a consumer that does not reorder keeps exactly the markup it had
    before this feature existed.
  */
  const { onMoveToIndex: _move, queueKey: _key, ...shellProps } = props
  return (
    <QueueListShell
      {...shellProps}
      renderRow={(job, cardProps) => <QueueCard key={job.id} {...cardProps} />}
    />
  )
}
