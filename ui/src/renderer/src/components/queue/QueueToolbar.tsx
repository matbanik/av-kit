/**
 * The reduced global queue toolbar (MEU-45, AC-45.3).
 *
 * The converter and downloader pages each used to carry their own row of up to
 * thirteen buttons. Both now mount this one component, which renders exactly
 * `TOOLBAR_CONTROLS` — Start, one Pause/Resume toggle, Clear finished, and an
 * overflow kebab holding `QUEUE_OVERFLOW_MENU`. Three rules shape it:
 *
 * 1. **Exactly four interactive elements** live inside `[data-testid="queue-toolbar"]`,
 *    in every state. The overflow popup is therefore a *sibling* of that group,
 *    never a fifth child of it, so opening the menu cannot inflate the census.
 * 2. **`pause-resume` is ONE button.** Its label and testid suffix follow
 *    `PAUSE_SCOPE` — the queue processor's state, never a per-job state — and
 *    the other half of the toggle is absent from the DOM, not merely hidden.
 * 3. **Icon *plus* persistent text label** (`TOOLBAR_LABEL_RULE`). A control
 *    named only by `title` or `aria-label` fails: the label is real text.
 *
 * The wrapper carrying `relative` is the box the overflow popup's `right-0`
 * resolves against, so it must shrink-wrap the control group. `self-start` is
 * load-bearing, not cosmetic: both queue pages mount this component as a direct
 * child of a `flex flex-col` section, and a column flex container stretches its
 * items across the cross axis. `inline-flex` alone does not survive that — a
 * flex item's display is blockified — so without `self-start` the wrapper takes
 * the page's full width and the menu opens against the window edge.
 *
 * Unusable controls are *disabled rather than removed* — the opposite of the
 * card kebab's rule (`QueueCardMenu`), and deliberately so: the toolbar's census
 * is fixed, so a vanishing Start button would break the contract above and make
 * the toolbar's shape jitter as the queue drains. The card menu has no such
 * census, so there an unavailable action is simply omitted.
 */
import { ListChecks, MoreHorizontal, Pause, Play } from 'lucide-react'
import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type KeyboardEvent,
  type ReactElement,
} from 'react'

/**
 * Visible copy for every toolbar control, keyed by control id.
 *
 * The tests read their expected strings from this table rather than repeating
 * them, so the copy has exactly one home. `clear-all` keeps its ellipsis because
 * it opens a confirm rather than acting immediately.
 */
export const TOOLBAR_CONTROL_LABELS = {
  start: 'Start',
  pause: 'Pause',
  resume: 'Resume',
  'clear-finished': 'Clear finished',
  'queue-overflow': 'More',
  'clear-all': 'Clear all…',
} as const

/** The processor state name the toggle reflects, as the API reported it. */
export type ProcessorStateName = string

export type QueueToolbarProps = {
  /** Queue processor state (`Idle` | `Processing` | `Running` | `Paused`). */
  processorState: ProcessorStateName
  /** Start (or restart) the queue processor. */
  onStart: () => void
  /** Toggle the processor between running and paused. */
  onPauseResume: () => void
  /** Sweep every finished job out of the queue. */
  onClearFinished: () => void
  /** Clear the whole queue, behind a confirm the host owns. */
  onClearAll: () => void
  /** Whether Start is usable right now. Defaults to enabled. */
  canStart?: boolean
  /** Whether the Pause/Resume toggle is usable right now. Defaults to enabled. */
  canPauseResume?: boolean
  /** Whether Clear finished is usable right now. Defaults to enabled. */
  canClearFinished?: boolean
  /** Whether Clear all is usable right now. Defaults to enabled. */
  canClearAll?: boolean
  /** Accessible name for the control group, e.g. `Conversion queue actions`. */
  label?: string
}

/** The only processor state that flips the toggle to Resume (`PAUSE_SCOPE`). */
const PAUSED_STATE = 'Paused'

const groupClasses = 'flex items-center gap-1.5'

const controlClasses = [
  'inline-flex items-center gap-1.5 px-2.5 py-1.5',
  'rounded-[var(--radius-control)] text-sm text-fg',
  'transition-[background-color,color] duration-[var(--duration-fast)] ease-[var(--ease-out)]',
  'hover:bg-neutral/30',
  'focus-visible:outline-none focus-visible:shadow-[0_0_0_3px_var(--color-accent-ring)]',
  'disabled:cursor-not-allowed disabled:text-fg-muted disabled:opacity-60 disabled:hover:bg-transparent',
].join(' ')

const menuClasses = [
  'absolute right-0 top-full z-10 mt-1 min-w-44 py-1',
  'rounded-[var(--radius-md)] border border-border bg-bg-elevated',
].join(' ')

const menuItemClasses = [
  'flex w-full items-center px-3 py-1.5 text-left text-sm text-error',
  'transition-[background-color,color] duration-[var(--duration-fast)] ease-[var(--ease-out)]',
  'hover:bg-neutral/30 focus-visible:outline-none focus-visible:bg-neutral/30',
  'disabled:cursor-not-allowed disabled:text-fg-muted disabled:opacity-60 disabled:hover:bg-transparent',
].join(' ')

const iconClasses = 'h-4 w-4'

/**
 * Render the four-control queue toolbar and its overflow menu.
 *
 * @param props - See {@link QueueToolbarProps}.
 * @returns The control group plus, while open, the sibling overflow menu.
 */
export function QueueToolbar({
  processorState,
  onStart,
  onPauseResume,
  onClearFinished,
  onClearAll,
  canStart = true,
  canPauseResume = true,
  canClearFinished = true,
  canClearAll = true,
  label = 'Queue actions',
}: QueueToolbarProps): ReactElement {
  const [open, setOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement | null>(null)
  const triggerRef = useRef<HTMLButtonElement | null>(null)
  const menuRef = useRef<HTMLDivElement | null>(null)

  const paused = processorState === PAUSED_STATE

  const close = useCallback((restoreFocus: boolean): void => {
    setOpen(false)
    if (restoreFocus) {
      triggerRef.current?.focus()
    }
  }, [])

  // The first *enabled* item takes focus when the popup mounts; when every item
  // is disabled focus stays on the trigger, which is where Escape is handled.
  useEffect(() => {
    if (!open) {
      return
    }
    const first = menuRef.current?.querySelector<HTMLButtonElement>(
      '[role="menuitem"]:not([disabled])',
    )
    first?.focus()
  }, [open])

  // Escape dismisses from anywhere: with a disabled-only menu the focused node
  // is the trigger, and after an outside click it may be neither.
  useEffect(() => {
    if (!open) {
      return undefined
    }
    const onKeyDown = (event: globalThis.KeyboardEvent): void => {
      if (event.key === 'Escape') {
        event.preventDefault()
        close(true)
      }
    }
    const onPointerDown = (event: MouseEvent): void => {
      const container = containerRef.current
      if (container !== null && event.target instanceof Node && !container.contains(event.target)) {
        setOpen(false)
      }
    }
    document.addEventListener('keydown', onKeyDown)
    document.addEventListener('mousedown', onPointerDown)
    return () => {
      document.removeEventListener('keydown', onKeyDown)
      document.removeEventListener('mousedown', onPointerDown)
    }
  }, [open, close])

  const onTriggerKeyDown = (event: KeyboardEvent<HTMLButtonElement>): void => {
    if (event.key === 'Enter' || event.key === ' ' || event.key === 'ArrowDown') {
      // Also suppresses the implicit click activation, which would toggle the
      // menu straight back shut.
      event.preventDefault()
      setOpen(true)
    }
  }

  return (
    <div className="relative inline-flex self-start" ref={containerRef}>
      <div className={groupClasses} data-testid="queue-toolbar" role="toolbar" aria-label={label}>
        <button
          type="button"
          className={controlClasses}
          data-testid="queue-toolbar-start"
          disabled={!canStart}
          onClick={onStart}
        >
          <Play className={iconClasses} aria-hidden="true" />
          {TOOLBAR_CONTROL_LABELS.start}
        </button>
        <button
          type="button"
          className={controlClasses}
          data-testid={paused ? 'queue-toolbar-resume' : 'queue-toolbar-pause'}
          disabled={!canPauseResume}
          onClick={onPauseResume}
        >
          {paused ? (
            <Play className={iconClasses} aria-hidden="true" />
          ) : (
            <Pause className={iconClasses} aria-hidden="true" />
          )}
          {paused ? TOOLBAR_CONTROL_LABELS.resume : TOOLBAR_CONTROL_LABELS.pause}
        </button>
        <button
          type="button"
          className={controlClasses}
          data-testid="queue-toolbar-clear-finished"
          disabled={!canClearFinished}
          onClick={onClearFinished}
        >
          <ListChecks className={iconClasses} aria-hidden="true" />
          {TOOLBAR_CONTROL_LABELS['clear-finished']}
        </button>
        <button
          ref={triggerRef}
          type="button"
          className={controlClasses}
          data-testid="queue-toolbar-overflow"
          aria-haspopup="menu"
          aria-expanded={open}
          onClick={() => {
            setOpen((previous) => !previous)
          }}
          onKeyDown={onTriggerKeyDown}
        >
          <MoreHorizontal className={iconClasses} aria-hidden="true" />
          {TOOLBAR_CONTROL_LABELS['queue-overflow']}
        </button>
      </div>
      {open ? (
        <div ref={menuRef} className={menuClasses} role="menu" aria-label={label}>
          <button
            type="button"
            role="menuitem"
            tabIndex={-1}
            className={menuItemClasses}
            data-testid="queue-toolbar-clear-all"
            data-menu-action="clear-all"
            disabled={!canClearAll}
            onClick={() => {
              onClearAll()
              close(true)
            }}
          >
            {TOOLBAR_CONTROL_LABELS['clear-all']}
          </button>
        </div>
      ) : null}
    </div>
  )
}
