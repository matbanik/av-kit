/**
 * One queue row, rendered as a card.
 *
 * The single structural rule worth stating up front: the checkbox, the primary
 * action and the kebab are **siblings** of the activatable card body, never
 * descendants of it. Nesting a control inside an element that is itself
 * `role="button"` produces one tab stop that does two things and an
 * accessibility tree that lies about both, so the body owns a bounded region and
 * every other control sits beside it (WCAG 2.2 SC 4.1.2).
 *
 * The card also never invents copy about *why* a job stopped: the reason comes
 * from the job's own `errorMessage`, and the remediation from the shared
 * `BLOCKER_REMEDIATION` map.
 */
import type { DraggableAttributes, DraggableSyntheticListeners } from '@dnd-kit/core'
import { GripVertical } from 'lucide-react'
import { type KeyboardEvent, type ReactElement, type ReactNode } from 'react'

import { resolveBlockerRemediation } from '../../lib/queue/blockers'
import { formatFileSize } from '../../lib/queue/format'
import { Button, type ButtonVariant } from '../ui/Button'
import { ProgressBar } from '../ui/ProgressBar'
import { SelectionCheckbox, type SelectionCheckboxModifiers } from '../ui/SelectionCheckbox'
import { StatusBadge, StatusIcon } from '../ui/StatusBadge'
import { Tooltip } from '../ui/Tooltip'
import {
  QueueCardMenu,
  resolveQueueMenuItems,
  type QueueCardMenuHandlers,
  type QueueMenuItem,
} from './QueueCardMenu'

/**
 * Separator between the shared meta line and a page's own meta segments.
 *
 * Stated once here because the card writes it and both pages' tests read it
 * (`META_SEPARATOR` in the migration plan's named sets).
 */
export const META_SEPARATOR = ' · '

/**
 * The meta line's placeholder, used when a state has nothing to report.
 *
 * Stated once because `resolveMeta` writes it and `composeMeta` FILTERS it: a
 * placeholder standing next to real facts is worse than no placeholder, so the
 * sentinel survives only when it is the entire line.
 */
export const META_PLACEHOLDER = '—'

/** Statuses a download job may be put back on the queue from. */
export const REQUEUEABLE_DOWNLOAD_STATUSES: readonly string[] = [
  'Failed',
  'Cancelled',
  'QualityBlocked',
  'AgeRestricted',
]

/**
 * Visual state of the card, in precedence order.
 *
 * An open detail panel outranks selection: the card the user is *reading* has to
 * stay findable even when a bulk selection is also in play.
 */
export const CARD_STATE_CLASSES = {
  'detail-open': 'border-accent bg-accent/10',
  'checkbox-selected': 'border-accent/50 bg-accent/5',
  default: 'border-border bg-bg hover:bg-bg-elevated',
} as const

/** The subset of a queue job a card renders. */
export type QueueCardJob = {
  /** Stable job id, passed back to every callback. */
  id: string
  /** 1-based position in the queue, as the API reported it. */
  position: number
  /** Status name as the API reported it. */
  status: string
  /** Human-readable job title. */
  title: string
  /** Progress in the 0..1 range while the job is running. */
  progress?: number | null
  /** Output size in bytes, once the job has finished. */
  fileSize?: number | null
  /** Failure or blocker reason the backend reported. */
  errorMessage?: string | null
  /** Absolute output path, once the job has produced a file. */
  outputPath?: string | null
  /** Source URL the job was queued from. */
  sourceUrl?: string | null
}

/**
 * The dnd-kit sortable surface for one row, as `QueueList` forwards it.
 *
 * It arrives as a PROP rather than being read from a `DndContext` here, and
 * that is deliberate: jsdom reports every rect as all-zero (`JSDOM_RECT_RULE`),
 * so no unit test can complete a real drag. What a unit test *can* prove is
 * that every piece dnd-kit supplies actually lands on the activator element,
 * and a prop is what makes that provable without a context.
 *
 * `attributes` is `Partial` because a test supplies only the members it is
 * asserting; the real `useSortable` return satisfies it in full.
 */
export type QueueCardDrag = {
  /** ARIA surface dnd-kit computes for the activator. */
  attributes?: Partial<DraggableAttributes>
  /** Sensor listeners; spread onto the activator verbatim. */
  listeners?: DraggableSyntheticListeners
  /**
   * Registers the activator element with dnd-kit. This ref — not `setNodeRef` —
   * is what restores focus to the handle after a keyboard drag.
   */
  setActivatorNodeRef?: (element: HTMLElement | null) => void
  /** Whether this row is the one currently being dragged. */
  isDragging?: boolean
  /**
   * Whether a reorder is already in flight for this queue
   * (`REORDER_SINGLE_FLIGHT_RULE`). `NO_DEAD_CONTROL_RULE`: a gated handle
   * renders `disabled` so it reads as unavailable, rather than staying live and
   * silently no-opping.
   */
  disabled?: boolean
}

export type QueueCardProps = QueueCardMenuHandlers & {
  /** The job this card renders. */
  job: QueueCardJob
  /** Override the card's `data-testid` — the converter queue uses its own id. */
  testId?: string
  /**
   * Page-owned meta columns appended to the shared meta line.
   *
   * The converter passes its Kind/Mode/Speed/ETA here so neither page has to
   * own the other's copy. Empty and whitespace-only segments are dropped, so a
   * page that cannot resolve a column never renders a dangling separator.
   */
  metaSegments?: readonly string[]
  /** Whether the job is the first row of the rendered queue. */
  isFirst?: boolean
  /** Whether the job is the last row of the rendered queue. */
  isLast?: boolean
  /** Whether this job is the one the processor is currently working on. */
  isInFlight?: boolean
  /** Whether the row is part of the current bulk selection. */
  selected?: boolean
  /** Whether the row's detail panel is open. */
  detailOpen?: boolean
  /** Whether to render the selection checkbox at all. */
  selectable?: boolean
  /**
   * Drag surface for this row. `DND_OPT_IN_RULE`: when it is undefined the card
   * renders no handle and no dnd attributes at all, which is what keeps the
   * transcript and TTS queues byte-for-byte unchanged.
   */
  drag?: QueueCardDrag
  /** Statuses this queue allows a retry from. */
  requeueableStatuses?: readonly string[]
  /** Open the row's detail panel. */
  onOpen?: (id: string) => void
  /**
   * Toggle the row's membership in the bulk selection.
   *
   * The modifier state — `{ shiftKey }` — is forwarded verbatim rather than
   * narrowed away (`SELECTION_PRIMITIVE_EXTENSION`): it is the only path by
   * which `SELECTION_MODEL`'s Shift+click range select reaches the page, so a
   * card that dropped it would leave the range working in tests and dead in the
   * running app.
   */
  onSelectChange?: (id: string, checked: boolean, modifiers: SelectionCheckboxModifiers) => void
  /** Put the job back on the queue. */
  onRetry?: (id: string) => void
  /**
   * Stop the whole queue. The backend exposes cancellation at queue scope only,
   * so this takes no id and the control that calls it says so.
   */
  onCancelQueue?: () => void
} & QueueCardSlots

/**
 * `CARD_SLOTS` — optional page-owned content for a card whose anatomy differs
 * from the download row (the transcript channel card).
 *
 * Every slot is additive: a card that passes none renders exactly the markup it
 * rendered before the slots existed. Interactive slot content goes in
 * `trailingControls`, which renders as a SIBLING of the activatable region —
 * never inside it — for the same WCAG 2.2 SC 4.1.2 reason stated at the top of
 * this file. `metaContent` and `detailContent` are inside the region and must
 * therefore be non-interactive.
 */
export type QueueCardSlots = {
  /** Accessible name of the activatable region. Defaults to `Open details for {title}`. */
  regionLabel?: string
  /** Replaces the shared text meta line (line 2). Non-interactive content only. */
  metaContent?: ReactNode
  /** A third line inside the region. Non-interactive content only. */
  detailContent?: ReactNode
  /** Controls rendered beside the region, before the kebab. */
  trailingControls?: ReactNode
  /** Replaces the resolved download kebab items with the page's own closed set. */
  menuItems?: readonly QueueMenuItem<string>[]
  /** Called when this card's kebab opens. */
  onMenuOpen?: () => void
}

/** Accessible name and tooltip for the in-flight stop control. */
const CANCEL_CONTROL_LABEL = 'Cancel queue'
const CANCEL_CONTROL_TITLE = 'Cancel queue - this is the in-flight item'

/**
 * The handle's own classes.
 *
 * `DND_HOVER_REVEAL_RULE` — the reveal is OPACITY ONLY. The handle is always
 * mounted, always focusable and always in the accessibility tree; it merely
 * fades in when the row is engaged. `hidden`, `display:none` and `aria-hidden`
 * would each take the keyboard drag away from the users most likely to need it,
 * and animating width would move every other zone while it did so (`G33_RULE`).
 *
 * `touch-none` is `DND_TOUCH_ACTION_RULE`: under Pointer Events, without
 * `touch-action: none` the browser's native scroll gesture claims a touch drag
 * and the row never moves.
 */
const dragHandleClasses = [
  'h-7 w-7 shrink-0 cursor-grab text-fg-muted',
  'touch-none',
  'opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 focus-visible:opacity-100',
].join(' ')

const containerClasses = [
  'flex items-center gap-3 px-3 py-2',
  'rounded-[var(--radius-lg)] border',
  'transition-[background-color,border-color] duration-[var(--duration-fast)] ease-[var(--ease-out)]',
].join(' ')

const inertRegionClasses = [
  'flex min-w-0 flex-1 items-center gap-3 text-left',
  'rounded-[var(--radius-md)]',
].join(' ')

const regionClasses = [
  inertRegionClasses,
  'cursor-pointer',
  'focus-visible:outline-none focus-visible:shadow-[0_0_0_3px_var(--color-accent-ring)]',
].join(' ')

/**
 * Pick the card's visual state class by precedence.
 *
 * @param detailOpen - Whether the row's detail panel is open.
 * @param selected - Whether the row is in the bulk selection.
 * @returns The token classes for the winning state.
 */
function resolveStateClasses(detailOpen: boolean, selected: boolean): string {
  if (detailOpen) {
    return CARD_STATE_CLASSES['detail-open']
  }
  if (selected) {
    return CARD_STATE_CLASSES['checkbox-selected']
  }
  return CARD_STATE_CLASSES.default
}

/**
 * Compose the meta line, which says something different in every state.
 *
 * @param job - The job being rendered.
 * @param isInFlight - Whether the processor is working on this job now.
 * @param blocked - Whether the status carries remediation copy.
 * @returns The meta text; never an empty string, so the row keeps its height.
 */
function resolveMeta(job: QueueCardJob, isInFlight: boolean, blocked: boolean): string {
  if (isInFlight) {
    const ratio = job.progress ?? 0
    const clamped = Number.isFinite(ratio) ? Math.min(Math.max(ratio, 0), 1) : 0
    return `${String(Math.round(clamped * 100))}% complete`
  }
  if (blocked || job.status === 'Failed' || job.status === 'Cancelled') {
    const reason = job.errorMessage
    return reason !== null && reason !== undefined && reason !== '' ? reason : META_PLACEHOLDER
  }
  if (job.status === 'Done') {
    return formatFileSize(job.fileSize ?? null)
  }
  if (job.status === 'Pending') {
    return `Waiting - position ${String(job.position)} in queue`
  }
  return META_PLACEHOLDER
}

/**
 * Append a page's own meta segments to the shared meta line.
 *
 * The filter runs over the COMPLETE sequence — `resolveMeta`'s output included —
 * and drops both the blank segment and the `META_PLACEHOLDER` sentinel
 * (`META_SEGMENTS_CONTRACT`, AC-45.1). Filtering only the page-owned tail would
 * leave the sentinel in the lead position whenever the shared half had nothing
 * to say: a Skipped row, a failed row with no reason, or a Done row with no
 * size would then read `— · 1080p · 12.4 MB`, which is a placeholder standing
 * in front of the very facts it exists to substitute for.
 *
 * The placeholder survives only when it is all that is left, because the row
 * must keep its height whatever the state.
 *
 * @param base - The meta text `resolveMeta` produced.
 * @param segments - Page-owned columns, possibly containing blanks or sentinels.
 * @returns The joined line; blanks and sentinels are dropped rather than separated.
 */
function composeMeta(base: string, segments: readonly string[] | undefined): string {
  const kept = [base, ...(segments ?? [])].filter((segment) => {
    const trimmed = segment.trim()
    return trimmed !== '' && trimmed !== META_PLACEHOLDER
  })
  return kept.length === 0 ? META_PLACEHOLDER : kept.join(META_SEPARATOR)
}

/** The one action promoted out of the kebab onto the card itself. */
type PrimaryAction = {
  label: string
  title: string
  variant: ButtonVariant
  run: () => void
}

/**
 * Pick at most one primary action for the card.
 *
 * The order is deliberate: an in-flight row's most urgent affordance is stopping
 * it, a re-queueable row's is trying again, and a finished row's is opening the
 * result. Everything else lives in the kebab.
 *
 * @param props - The card's resolved props.
 * @param isInFlight - Whether the processor is working on this job now.
 * @param requeueable - Statuses this queue allows a retry from.
 * @returns The single action to render, or `null` when the state affords none.
 */
function resolvePrimaryAction(
  props: QueueCardProps,
  isInFlight: boolean,
  requeueable: readonly string[],
): PrimaryAction | null {
  const { job, onRetry, onOpenFile, onCancelQueue } = props

  if (isInFlight && onCancelQueue !== undefined) {
    return {
      label: CANCEL_CONTROL_LABEL,
      title: CANCEL_CONTROL_TITLE,
      variant: 'destructive',
      run: () => {
        onCancelQueue()
      },
    }
  }
  if (requeueable.includes(job.status) && onRetry !== undefined) {
    return {
      label: 'Retry',
      title: 'Put this job back on the queue',
      variant: 'secondary',
      run: () => {
        onRetry(job.id)
      },
    }
  }
  const outputPath = job.outputPath
  if (
    job.status === 'Done' &&
    onOpenFile !== undefined &&
    outputPath !== null &&
    outputPath !== undefined &&
    outputPath.trim() !== ''
  ) {
    return {
      label: 'Open file',
      title: outputPath,
      variant: 'secondary',
      run: () => {
        onOpenFile(job.id)
      },
    }
  }
  return null
}

/**
 * Render one queue row as a card.
 *
 * @param props - See {@link QueueCardProps}.
 * @returns The card element.
 */
export function QueueCard(props: QueueCardProps): ReactElement {
  const {
    job,
    testId = 'queue-card',
    isFirst = false,
    isLast = false,
    isInFlight = false,
    selected = false,
    detailOpen = false,
    selectable = false,
    requeueableStatuses = REQUEUEABLE_DOWNLOAD_STATUSES,
    metaSegments,
    drag,
    onOpen,
    onSelectChange,
    regionLabel,
    metaContent,
    detailContent,
    trailingControls,
    onMenuOpen,
  } = props

  const remediation = resolveBlockerRemediation(job.status)
  const meta = composeMeta(resolveMeta(job, isInFlight, remediation !== null), metaSegments)
  const primary = resolvePrimaryAction(props, isInFlight, requeueableStatuses)
  const menuItems = props.menuItems ?? resolveQueueMenuItems({
    id: job.id,
    status: job.status,
    outputPath: job.outputPath,
    sourceUrl: job.sourceUrl,
    isFirst,
    isLast,
    /*
      The gate the drag handle reads is the same gate the kebab's four reorder
      items read — one queue, one in-flight reorder, so every entry point into it
      has to report unavailable together (`REORDER_FEEDBACK_TIER`). Reading it off
      `drag` rather than taking a second prop is what keeps them from drifting.
    */
    reorderLocked: drag?.disabled === true,
    handlers: props,
  })

  const activatable = onOpen !== undefined

  const activate = (): void => {
    onOpen?.(job.id)
  }

  const onRegionKeyDown = (event: KeyboardEvent<HTMLDivElement>): void => {
    if (event.key === 'Enter' || event.key === ' ') {
      // Space would otherwise scroll the queue out from under the user.
      event.preventDefault()
      activate()
    }
  }

  /*
    Alt+Up / Alt+Down reorder the row. The handler sits on the card container,
    not on the activatable region, for two reasons: the shortcut has to work
    wherever focus is inside the card (region, primary action, kebab trigger),
    and a *bare* arrow must stay navigation — the kebab trigger's own ArrowDown
    opens the menu, so claiming unmodified arrows here would break it. Moving is
    gated by the same availability rule the menu uses: the first row has no
    up, the last row no down.
  */
  const onCardKeyDown = (event: KeyboardEvent<HTMLDivElement>): void => {
    if (!event.altKey || (event.key !== 'ArrowUp' && event.key !== 'ArrowDown')) {
      return
    }
    /*
      ALT_ARROW_SUPPRESSION_RULE. Two keyboard paths can move the same row, and
      only one of them may be live at a time. While dnd-kit owns the drag it is
      already interpreting arrow keys as drag movement, so letting Alt+Arrow fire
      too would commit a second, index-based move on top of the drag dnd-kit is
      about to commit. The same holds while the single-flight gate is held: the
      reorder in flight has not yet returned the authoritative order, so a move
      computed from the stale one would race it.
    */
    if (drag?.isDragging === true || drag?.disabled === true) {
      return
    }
    const up = event.key === 'ArrowUp'
    if (up ? isFirst : isLast) {
      return
    }
    const move = up ? props.onMoveUp : props.onMoveDown
    if (move === undefined) {
      return
    }
    event.preventDefault()
    move(job.id)
  }

  return (
    <div
      className={[
        containerClasses,
        /*
          `group` is what `DND_HOVER_REVEAL_RULE` hangs the handle's
          `group-hover:` / `group-focus-within:` reveal off. DND_OPT_IN_RULE: it
          is added only when the row can actually drag, so a consumer that
          passes no `drag` keeps its markup byte-for-byte unchanged.
        */
        drag !== undefined ? 'group' : '',
        resolveStateClasses(detailOpen, selected),
      ]
        .filter((entry) => entry !== '')
        .join(' ')}
      data-testid={testId}
      data-job-id={job.id}
      data-status={job.status}
      onKeyDown={onCardKeyDown}
    >
      {/*
        DND_HANDLE_CONTRACT. The handle is the FIRST child and a SIBLING of every
        other zone, never nested inside the activatable region: nesting it would
        put a button inside a `role="button"` and make one gesture ambiguous
        between opening the row and dragging it.
      */}
      {drag !== undefined ? (
        <Tooltip id="queue-card-drag-handle" label={`Reorder ${job.title}`} disabled={drag.disabled === true}>
          <Button
            ref={drag.setActivatorNodeRef}
            variant="ghost"
            size="sm"
            icon
            className={dragHandleClasses}
            data-testid="queue-card-drag-handle"
            aria-label={`Reorder ${job.title}`}
            disabled={drag.disabled === true}
            {...drag.attributes}
            {...drag.listeners}
          >
            <GripVertical className="h-4 w-4" aria-hidden="true" />
          </Button>
        </Tooltip>
      ) : null}

      {selectable && onSelectChange !== undefined ? (
        <SelectionCheckbox
          checked={selected}
          ariaLabel={`Select ${job.title}`}
          onChange={(checked, modifiers) => {
            onSelectChange(job.id, checked, modifiers)
          }}
        />
      ) : null}

      {/*
        DEAD_REGION_RULE — without `onOpen` there is nothing to activate, so the
        region advertises no role, no tab stop and no accessible name. Telling a
        screen-reader user to press a button that does nothing is worse than
        rendering plain text.
      */}
      <div
        className={activatable ? regionClasses : inertRegionClasses}
        {...(activatable
          ? {
              role: 'button',
              tabIndex: 0,
              'aria-label': regionLabel ?? `Open details for ${job.title}`,
              onClick: activate,
              onKeyDown: onRegionKeyDown,
            }
          : {})}
      >
        <span
          className="w-7 shrink-0 text-right text-xs tabular-nums text-fg-muted"
          data-testid="queue-card-position"
        >
          {job.position}
        </span>
        <StatusIcon status={job.status} />
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm text-fg" data-testid="queue-card-title" title={job.title}>
            {job.title}
          </p>
          {metaContent !== undefined ? (
            <div
              className="flex min-w-0 flex-wrap items-center gap-x-2 gap-y-1 text-xs text-fg-muted"
              data-testid="queue-card-meta"
            >
              {metaContent}
            </div>
          ) : (
            <p
              className="truncate text-xs text-fg-muted"
              data-testid="queue-card-meta"
              title={meta}
            >
              {meta}
            </p>
          )}
          {remediation !== null ? (
            <p
              className="truncate text-xs text-fg-muted"
              data-blocker-remediation=""
              title={remediation}
            >
              {remediation}
            </p>
          ) : null}
          {detailContent !== undefined ? (
            <div className="truncate text-xs text-fg-muted" data-testid="queue-card-detail">
              {detailContent}
            </div>
          ) : null}
        </div>
        {isInFlight ? (
          <div className="w-28 shrink-0">
            <ProgressBar value={job.progress ?? 0} ariaLabel={`Progress for ${job.title}`} />
          </div>
        ) : null}
        <StatusBadge status={job.status} />
      </div>

      {primary !== null ? (
        <Button
          variant={primary.variant}
          size="sm"
          data-testid="queue-card-primary-action"
          aria-label={primary.label}
          title={primary.title}
          onClick={primary.run}
        >
          {primary.label}
        </Button>
      ) : null}

      {trailingControls !== undefined ? trailingControls : null}

      {menuItems.length > 0 ? (
        <QueueCardMenu
          items={menuItems}
          triggerLabel={`Actions for ${job.title}`}
          onOpenChange={
            onMenuOpen === undefined
              ? undefined
              : (open) => {
                  if (open) {
                    onMenuOpen()
                  }
                }
          }
        />
      ) : null}
    </div>
  )
}
