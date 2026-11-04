import { useEffect, useRef, useState, type KeyboardEvent, type MouseEvent } from 'react'

import type { CaptureListItem } from './useCaptureCatalog'
import { sortFilmstrip } from './useCaptureCatalog'
import { fetchAuthorizedBlob } from './capture-image'
import { filmstripLabel } from './capture-filmstrip-label'
import { CaptureFilmstripMenu, type FilmstripMenuItem } from './CaptureFilmstripMenu'

/** What the "Shot actions" menu can do to the shot it was opened on (MENU_TARGET). */
export type FilmstripShotActions = {
  onCopyPath: (item: CaptureListItem) => void
  onCopyImage: (item: CaptureListItem) => void
  onDelete: (item: CaptureListItem) => void
  /** MENU_ITEMS_BATCH: delete every shot in the range (MEU-89). */
  onDeleteRange: () => void
}

type CaptureFilmstripProps = {
  items: CaptureListItem[]
  selectedId: string | null
  /** The selected shot has unsaved overlay marks (CAPTURE_OVERLAY_DIRTY). */
  selectedDirty?: boolean
  /** A pending confirmation owns the selection (CONFIRM_EXCLUSIVITY). */
  locked?: boolean
  /** RANGE: the selection set in filmstrip order; it counts as a range only with more than one shot. */
  rangeIds?: string[]
  /** `extend` is true for a Shift-click, which selects a range from the anchor (MEU-89). */
  onSelect: (id: string, options: { extend: boolean }) => void
  /** CHECK_TOGGLE (D-25): a row's checkbox was clicked; `extend` is true with Shift held. */
  onCheck: (id: string, options: { extend: boolean }) => void
  actions: FilmstripShotActions
}

type MenuState = { id: string; left: number; top: number; opener: HTMLElement }

export function CaptureFilmstrip({
  items,
  selectedId,
  selectedDirty = false,
  locked = false,
  rangeIds = [],
  onSelect,
  onCheck,
  actions,
}: CaptureFilmstripProps) {
  const ordered = sortFilmstrip(items)
  const ticked = new Set(rangeIds)
  const range = new Set(rangeIds.length > 1 ? rangeIds : [])
  const listRef = useRef<HTMLDivElement | null>(null)
  const [menu, setMenu] = useState<MenuState | null>(null)
  const menuOpen = menu !== null

  // MENU_LOCK: a confirm strip that opens while the menu is up closes it.
  useEffect(() => {
    if (locked) {
      setMenu(null)
    }
  }, [locked])

  // Scrolling the filmstrip moves the thumb away from a fixed menu, so it closes.
  useEffect(() => {
    const list = listRef.current
    if (!menuOpen || list === null) {
      return undefined
    }
    const onScroll = (): void => {
      setMenu(null)
    }
    list.addEventListener('scroll', onScroll)
    return () => {
      list.removeEventListener('scroll', onScroll)
    }
  }, [menuOpen])

  // MENU_OPEN / MENU_ANCHOR: `point` is null for a keyboard open, which anchors to the thumb.
  function openMenu(id: string, opener: HTMLElement, point: { x: number; y: number } | null): void {
    if (locked) {
      return
    }
    let anchor = point
    if (anchor === null) {
      const rect = opener.getBoundingClientRect()
      anchor = { x: rect.left, y: rect.bottom }
    }
    const next = { id, left: anchor.x, top: anchor.y, opener }
    // Chromium follows the ContextMenu key with a contextmenu event; the second signal is a no-op.
    setMenu((current) => (current !== null && current.id === id ? current : next))
  }

  function closeMenu(restoreFocus: boolean): void {
    const opener = menu?.opener
    setMenu(null)
    if (restoreFocus) {
      opener?.focus()
    }
  }

  const target = menu !== null ? ordered.find((item) => item.id === menu.id) : undefined
  const menuItems: FilmstripMenuItem[] =
    target === undefined
      ? []
      : range.has(target.id)
        ? [
            {
              id: 'delete-batch',
              label: `Delete ${range.size} shots`,
              testId: 'capture-filmstrip-menu-delete-batch',
              destructive: true,
              run: () => {
                actions.onDeleteRange()
              },
            },
          ]
        : [
            {
              id: 'copy-path',
              label: 'Copy full path',
              testId: 'capture-filmstrip-menu-copy-path',
              run: () => {
                actions.onCopyPath(target)
              },
            },
            {
              id: 'copy-image',
              label: 'Copy image',
              testId: 'capture-filmstrip-menu-copy-image',
              run: () => {
                actions.onCopyImage(target)
              },
            },
            {
              id: 'delete',
              label: 'Delete',
              testId: 'capture-filmstrip-menu-delete',
              destructive: true,
              run: () => {
                actions.onDelete(target)
              },
            },
          ]

  return (
    <div
      ref={listRef}
      className="flex max-h-[26rem] min-h-[8rem] flex-col gap-1 overflow-auto"
      data-testid="capture-filmstrip"
      aria-label="Captures"
    >
      {ordered.map((item) => (
        // CHECK: a button cannot hold a checkbox, so the box is the thumb's sibling, to its left.
        <div key={item.id} className="flex shrink-0 items-center gap-1">
          <input
            type="checkbox"
            data-testid="capture-filmstrip-check"
            aria-label={`Select ${item.display_name}`}
            checked={ticked.has(item.id)}
            disabled={locked}
            className="h-3.5 w-3.5 shrink-0 accent-accent disabled:cursor-not-allowed"
            onChange={(event) => {
              onCheck(item.id, { extend: (event.nativeEvent as globalThis.MouseEvent).shiftKey === true })
            }}
          />
          <FilmstripThumb
            item={item}
            selected={item.id === selectedId}
            inRange={range.has(item.id)}
            dirty={item.id === selectedId && selectedDirty}
            locked={locked}
            onSelect={(extend) => {
              onSelect(item.id, { extend })
            }}
            onOpenMenu={(opener, point) => {
              openMenu(item.id, opener, point)
            }}
          />
        </div>
      ))}
      {menu !== null && target !== undefined && !locked ? (
        <CaptureFilmstripMenu left={menu.left} top={menu.top} items={menuItems} onClose={closeMenu} />
      ) : null}
    </div>
  )
}

function FilmstripThumb({
  item,
  selected,
  inRange,
  dirty,
  locked,
  onSelect,
  onOpenMenu,
}: {
  item: CaptureListItem
  selected: boolean
  inRange: boolean
  dirty: boolean
  locked: boolean
  onSelect: (extend: boolean) => void
  onOpenMenu: (opener: HTMLElement, point: { x: number; y: number } | null) => void
}) {
  const label = filmstripLabel(item.display_name, item.created_at)
  const [src, setSrc] = useState<string | null>(null)

  useEffect(() => {
    let revoked = false
    let objectUrl: string | null = null
    void fetchAuthorizedBlob(`/captures/${item.id}/image`).then((blob) => {
      if (blob === null) {
        return
      }
      objectUrl = URL.createObjectURL(blob)
      if (!revoked) {
        setSrc(objectUrl)
      } else {
        URL.revokeObjectURL(objectUrl)
      }
    })
    return () => {
      revoked = true
      if (objectUrl !== null) {
        URL.revokeObjectURL(objectUrl)
      }
    }
    // IMAGE_REVISION: a flatten or revert bumps updated_at, so the thumbnail refetches.
  }, [item.id, item.updated_at])

  const onContextMenu = (event: MouseEvent<HTMLButtonElement>): void => {
    event.preventDefault()
    // A contextmenu at 0,0 comes from the keyboard on some hosts: anchor it to the thumb.
    const fromKeyboard = event.clientX === 0 && event.clientY === 0
    onOpenMenu(event.currentTarget, fromKeyboard ? null : { x: event.clientX, y: event.clientY })
  }

  const onKeyDown = (event: KeyboardEvent<HTMLButtonElement>): void => {
    if (event.key === 'ContextMenu' || (event.key === 'F10' && event.shiftKey)) {
      event.preventDefault()
      onOpenMenu(event.currentTarget, null)
    }
  }

  return (
    <button
      type="button"
      data-testid="capture-filmstrip-item"
      aria-current={selected ? 'true' : undefined}
      aria-haspopup="menu"
      data-in-range={inRange ? 'true' : undefined}
      data-dirty={dirty ? 'true' : undefined}
      disabled={locked}
      className={`flex h-[2.875rem] min-w-0 flex-1 items-center gap-2 rounded-[var(--radius-control)] border px-1 text-left disabled:cursor-not-allowed ${
        selected ? 'border-accent/50 bg-accent/10' : 'border-transparent hover:bg-bg-elevated'
      }${inRange ? ' ring-1 ring-accent/40' : ''}`}
      onClick={(event) => {
        onSelect(event.shiftKey)
      }}
      onContextMenu={onContextMenu}
      onKeyDown={onKeyDown}
    >
      <span className="h-9 w-14 shrink-0 overflow-hidden rounded bg-bg-elevated">
        {src !== null ? <img src={src} alt={label.full} className="h-full w-full object-cover" /> : null}
      </span>
      {/* Screenshots of the same app look alike as thumbnails, so the name is what distinguishes
          them. The full name stays in the DOM (sr-only) whether or not the thumbnail loaded. */}
      <span className="flex min-w-0 flex-1 flex-col">
        <span className="truncate text-xs" data-testid="capture-filmstrip-name" aria-hidden="true">{label.name}</span>
        <span className="text-xs text-fg-muted" data-testid="capture-filmstrip-time" aria-hidden="true">{label.time}</span>
        {/* RANGE_MARK: the accessible name says the shot is part of the range. */}
        <span className="sr-only">{inRange ? `${label.full}, selected` : label.full}</span>
      </span>
      {dirty ? <span className="h-2 w-2 shrink-0 rounded-full bg-accent-orange" aria-label="Unsaved marks" /> : null}
    </button>
  )
}
