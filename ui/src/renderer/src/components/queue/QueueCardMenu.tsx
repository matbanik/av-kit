/**
 * Kebab overflow menu for a queue card.
 *
 * Two rules shape this component:
 *
 * 1. **Structurally unavailable actions are absent, never disabled.** A
 *    greyed-out "Move up" on the first row is a control the user can reach,
 *    focus and click for no result; omitting it keeps the menu's length an
 *    honest signal of what is possible right now. *Temporarily* unavailable is
 *    the other case and takes the other rendering: an action that exists on this
 *    row but cannot run *right now* — a reorder while another reorder is still
 *    on the wire — renders `disabled`, because it is coming back and its absence
 *    would make the menu's length flicker. Absent means "not for this row";
 *    disabled means "not this moment".
 * 2. **The visible label names what the action actually does.** `copy-location`
 *    is one action id in one order slot, but it copies the output path only once
 *    one exists — before that it copies the source URL, so the label follows the
 *    payload rather than the id.
 *
 * Keyboard behaviour follows the WAI-ARIA menu-button pattern: Enter, Space and
 * Down Arrow open the menu and move focus to the first item, Up/Down Arrow roam,
 * Escape closes and returns focus to the trigger.
 */
import { MoreVertical } from 'lucide-react'
import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type KeyboardEvent,
  type ReactElement,
} from 'react'

import { Tooltip } from '../ui/Tooltip'

/** Canonical action ids, in the order the menu renders them. */
export const KEBAB_MENU_ORDER = [
  'open-file',
  'open-folder',
  'copy-location',
  'move-up',
  'move-down',
  'move-top',
  'move-bottom',
  'remove',
] as const

export type QueueMenuActionId = (typeof KEBAB_MENU_ORDER)[number]

/** Optional per-action callbacks. An absent callback removes its menu item. */
export type QueueCardMenuHandlers = {
  /** Reveal the finished file in its default application. */
  onOpenFile?: (id: string) => void
  /** Reveal the finished file's containing folder. */
  onOpenFolder?: (id: string) => void
  /** Put the output path — or, before one exists, the source URL — on the clipboard. */
  onCopyLocation?: (value: string) => void
  /** Move the job one slot towards the front of the queue. */
  onMoveUp?: (id: string) => void
  /** Move the job one slot towards the back of the queue. */
  onMoveDown?: (id: string) => void
  /** Move the job to the front of the queue. */
  onMoveTop?: (id: string) => void
  /** Move the job to the back of the queue. */
  onMoveBottom?: (id: string) => void
  /** Remove the job from the queue. */
  onRemove?: (id: string) => void
}

/** Everything {@link resolveQueueMenuItems} needs to decide availability and labels. */
export type QueueMenuContext = {
  /** Job id passed back to every callback except `onCopyLocation`. */
  id: string
  /** Status name as the API reported it. */
  status: string
  /** Absolute output path, once the job has produced a file. */
  outputPath?: string | null
  /** Source URL the job was queued from. */
  sourceUrl?: string | null
  /** Whether the job is the first row of the rendered queue. */
  isFirst: boolean
  /** Whether the job is the last row of the rendered queue. */
  isLast: boolean
  /**
   * Whether this queue's reorder gate is currently held
   * (`REORDER_SINGLE_FLIGHT_RULE`). Every reorder item that IS present renders
   * `disabled` while it is — leaving them live would show four controls that
   * silently do nothing, which is exactly what `NO_DEAD_CONTROL_RULE` forbids.
   */
  reorderLocked?: boolean
  /** Callbacks the host page supplied. */
  handlers: QueueCardMenuHandlers
}

/**
 * One rendered menu row.
 *
 * Generic over its id (`MENU_ITEM_EXTENSION`): the download and convert queues
 * use the canonical {@link QueueMenuActionId} set, while a page with its own
 * closed action set (the transcript channel menu) supplies that union instead.
 */
export type QueueMenuItem<Id extends string = QueueMenuActionId> = {
  /** Action id: canonical by default, or the caller's own closed set. */
  id: Id
  /** Visible label, which is also the item's accessible name. */
  label: string
  /** Whether the item is a destructive verb and must be styled as one. */
  destructive: boolean
  /** Whether the action is temporarily unavailable and must render inert. */
  disabled?: boolean
  /** Invoke the host callback for this action. */
  run: () => void
  /** `data-testid` for the item, when a page keeps an existing action id on it. */
  testId?: string
}

/**
 * Non-empty check that also rejects a whitespace-only value.
 *
 * @param value - Candidate path or URL.
 * @returns Whether the value carries usable content.
 */
function present(value: string | null | undefined): value is string {
  return typeof value === 'string' && value.trim() !== ''
}

/**
 * Decide which menu items a card shows, in canonical order.
 *
 * Availability is the conjunction of two things: the host supplied a callback,
 * and the job's own state makes the action meaningful (a `Done` job with an
 * output path can be opened; a first row cannot move up).
 *
 * @param context - See {@link QueueMenuContext}.
 * @returns The items to render, ordered by {@link KEBAB_MENU_ORDER}.
 */
export function resolveQueueMenuItems(context: QueueMenuContext): QueueMenuItem[] {
  const { id, status, outputPath, sourceUrl, isFirst, isLast, reorderLocked, handlers } = context
  const hasOutput = present(outputPath)
  const finished = status === 'Done' && hasOutput
  const copyValue = hasOutput ? outputPath : present(sourceUrl) ? sourceUrl : null
  const items: QueueMenuItem[] = []

  for (const action of KEBAB_MENU_ORDER) {
    switch (action) {
      case 'open-file': {
        const handler = handlers.onOpenFile
        if (finished && handler !== undefined) {
          items.push({
            id: action,
            label: 'Open file',
            destructive: false,
            run: () => {
              handler(id)
            },
          })
        }
        break
      }
      case 'open-folder': {
        const handler = handlers.onOpenFolder
        if (finished && handler !== undefined) {
          items.push({
            id: action,
            label: 'Open folder',
            destructive: false,
            run: () => {
              handler(id)
            },
          })
        }
        break
      }
      case 'copy-location': {
        const handler = handlers.onCopyLocation
        if (handler !== undefined && copyValue !== null) {
          const value = copyValue
          items.push({
            id: action,
            label: hasOutput ? 'Copy path' : 'Copy URL',
            destructive: false,
            run: () => {
              handler(value)
            },
          })
        }
        break
      }
      case 'move-up': {
        const handler = handlers.onMoveUp
        if (!isFirst && handler !== undefined) {
          items.push({
            id: action,
            label: 'Move up',
            destructive: false,
            disabled: reorderLocked === true,
            run: () => {
              handler(id)
            },
          })
        }
        break
      }
      case 'move-down': {
        const handler = handlers.onMoveDown
        if (!isLast && handler !== undefined) {
          items.push({
            id: action,
            label: 'Move down',
            destructive: false,
            disabled: reorderLocked === true,
            run: () => {
              handler(id)
            },
          })
        }
        break
      }
      case 'move-top': {
        const handler = handlers.onMoveTop
        if (!isFirst && handler !== undefined) {
          items.push({
            id: action,
            label: 'Move to top',
            destructive: false,
            disabled: reorderLocked === true,
            run: () => {
              handler(id)
            },
          })
        }
        break
      }
      case 'move-bottom': {
        const handler = handlers.onMoveBottom
        if (!isLast && handler !== undefined) {
          items.push({
            id: action,
            label: 'Move to bottom',
            destructive: false,
            disabled: reorderLocked === true,
            run: () => {
              handler(id)
            },
          })
        }
        break
      }
      case 'remove': {
        const handler = handlers.onRemove
        if (handler !== undefined) {
          items.push({
            id: action,
            label: 'Remove',
            destructive: true,
            run: () => {
              handler(id)
            },
          })
        }
        break
      }
      default:
        break
    }
  }

  return items
}

export type QueueCardMenuProps = {
  /** Items to render: resolved by {@link resolveQueueMenuItems}, or a page's own. */
  items: readonly QueueMenuItem<string>[]
  /** Accessible name for the trigger, e.g. `Actions for Example video`. */
  triggerLabel?: string
  /** Override the trigger's `data-testid`. */
  triggerTestId?: string
  /** Override the popup's `data-testid`. */
  menuTestId?: string
  /** Called whenever the menu opens or closes. */
  onOpenChange?: (open: boolean) => void
}

const triggerClasses = [
  'inline-flex h-7 w-7 shrink-0 items-center justify-center',
  'rounded-[var(--radius-control)] text-fg-muted',
  'transition-[background-color,color] duration-[var(--duration-fast)] ease-[var(--ease-out)]',
  'hover:bg-neutral/30 hover:text-fg',
  'focus-visible:outline-none focus-visible:shadow-[0_0_0_3px_var(--color-accent-ring)]',
].join(' ')

const menuClasses = [
  'absolute right-0 top-full z-10 mt-1 min-w-44 py-1',
  'rounded-[var(--radius-md)] border border-border bg-bg-elevated',
].join(' ')

const itemClasses = [
  'flex w-full items-center px-3 py-1.5 text-left text-sm',
  'transition-[background-color,color] duration-[var(--duration-fast)] ease-[var(--ease-out)]',
  'hover:bg-neutral/30 focus-visible:outline-none focus-visible:bg-neutral/30',
].join(' ')

/**
 * Render the kebab trigger and, while open, its menu.
 *
 * @param props - See {@link QueueCardMenuProps}.
 * @returns The trigger button plus the popup menu when open.
 */
export function QueueCardMenu({
  items,
  triggerLabel = 'More actions',
  triggerTestId = 'queue-card-kebab',
  menuTestId = 'queue-card-menu',
  onOpenChange,
}: QueueCardMenuProps): ReactElement {
  const [open, setOpen] = useState(false)
  const onOpenChangeRef = useRef(onOpenChange)
  onOpenChangeRef.current = onOpenChange
  const reportedOpen = useRef(false)

  // Report transitions only, never the initial closed state, so a host that
  // selects its row on open is not told about menus nobody opened.
  useEffect(() => {
    if (reportedOpen.current === open) {
      return
    }
    reportedOpen.current = open
    onOpenChangeRef.current?.(open)
  }, [open])
  const triggerRef = useRef<HTMLButtonElement | null>(null)
  const menuRef = useRef<HTMLDivElement | null>(null)
  const containerRef = useRef<HTMLDivElement | null>(null)

  const close = useCallback((restoreFocus: boolean): void => {
    setOpen(false)
    if (restoreFocus) {
      triggerRef.current?.focus()
    }
  }, [])

  // Roving focus: the menu owns focus while it is open, so the first item takes
  // it as soon as the popup mounts.
  useEffect(() => {
    if (!open) {
      return
    }
    const first = menuRef.current?.querySelector<HTMLButtonElement>('[role="menuitem"]')
    first?.focus()
  }, [open])

  // A pointer press anywhere outside dismisses the menu without running an
  // action, and Escape dismisses from anywhere at all. The menu div carries its
  // own Escape handler for the common case where focus is inside the popup, but
  // focus can legitimately sit elsewhere — the trigger after a click that did
  // not move it, or the page body — and the WAI-ARIA menu-button pattern still
  // requires Escape to close. A document listener is the only placement that
  // covers every one of those, and it is idempotent with the menu-level handler
  // because both simply close an already-open menu.
  useEffect(() => {
    if (!open) {
      return undefined
    }
    const onPointerDown = (event: MouseEvent): void => {
      const container = containerRef.current
      if (container !== null && event.target instanceof Node && !container.contains(event.target)) {
        setOpen(false)
      }
    }
    const onDocumentKeyDown = (event: globalThis.KeyboardEvent): void => {
      if (event.key === 'Escape') {
        event.preventDefault()
        close(true)
      }
    }
    document.addEventListener('mousedown', onPointerDown)
    document.addEventListener('keydown', onDocumentKeyDown)
    return () => {
      document.removeEventListener('mousedown', onPointerDown)
      document.removeEventListener('keydown', onDocumentKeyDown)
    }
  }, [open, close])

  const onTriggerKeyDown = (event: KeyboardEvent<HTMLButtonElement>): void => {
    if (event.key === 'Enter' || event.key === ' ' || event.key === 'ArrowDown') {
      // Also suppresses the browser's implicit click activation, which would
      // otherwise toggle the menu straight back shut.
      event.preventDefault()
      setOpen(true)
    }
  }

  const moveFocus = (step: number): void => {
    const nodes = Array.from(
      menuRef.current?.querySelectorAll<HTMLButtonElement>('[role="menuitem"]') ?? [],
    )
    if (nodes.length === 0) {
      return
    }
    const active = document.activeElement
    const current = active instanceof HTMLButtonElement ? nodes.indexOf(active) : -1
    const next = (current + step + nodes.length) % nodes.length
    nodes[next].focus()
  }

  const onMenuKeyDown = (event: KeyboardEvent<HTMLDivElement>): void => {
    if (event.key === 'Escape') {
      event.preventDefault()
      close(true)
      return
    }
    if (event.key === 'Tab') {
      close(false)
      return
    }
    if (event.key === 'ArrowDown') {
      event.preventDefault()
      moveFocus(1)
      return
    }
    if (event.key === 'ArrowUp') {
      event.preventDefault()
      moveFocus(-1)
    }
  }

  return (
    <div className="relative shrink-0" ref={containerRef}>
      <Tooltip id={triggerTestId} label={triggerLabel} suppressed={open}>
        <button
          ref={triggerRef}
          type="button"
          className={triggerClasses}
          data-testid={triggerTestId}
          aria-haspopup="menu"
          aria-expanded={open}
          aria-label={triggerLabel}
          onClick={() => {
            setOpen((previous) => !previous)
          }}
          onKeyDown={onTriggerKeyDown}
        >
          <MoreVertical className="h-4 w-4" aria-hidden="true" />
        </button>
      </Tooltip>
      {open ? (
        <div
          ref={menuRef}
          className={menuClasses}
          data-testid={menuTestId}
          role="menu"
          aria-label={triggerLabel}
          onKeyDown={onMenuKeyDown}
        >
          {items.map((item) => (
            <button
              key={item.id}
              type="button"
              role="menuitem"
              tabIndex={-1}
              data-menu-action={item.id}
              data-testid={item.testId}
              disabled={item.disabled === true}
              className={[
                itemClasses,
                'disabled:opacity-50 disabled:pointer-events-none',
                item.destructive ? 'text-error' : 'text-fg',
              ].join(' ')}
              onClick={() => {
                item.run()
                close(true)
              }}
            >
              {item.label}
            </button>
          ))}
        </div>
      ) : null}
    </div>
  )
}
