import { useEffect, useLayoutEffect, useRef, useState, type KeyboardEvent, type ReactElement } from 'react'
import { createPortal } from 'react-dom'

export type FilmstripMenuItem = {
  id: string
  label: string
  testId: string
  destructive?: boolean
  run: () => void
}

type CaptureFilmstripMenuProps = {
  /** Viewport coordinates of the menu's top-left corner before clamping (MENU_ANCHOR). */
  left: number
  top: number
  items: FilmstripMenuItem[]
  /** `restoreFocus` returns focus to the thumb that opened the menu. */
  onClose: (restoreFocus: boolean) => void
}

const menuClasses = [
  'z-20 min-w-44 py-1',
  'rounded-[var(--radius-md)] border border-border bg-bg-elevated',
].join(' ')

const itemClasses = [
  'flex w-full items-center px-3 py-1.5 text-left text-sm',
  'transition-[background-color,color] duration-[var(--duration-fast)] ease-[var(--ease-out)]',
  'hover:bg-neutral/30 focus-visible:outline-none focus-visible:bg-neutral/30',
].join(' ')

/**
 * MENU_PATTERN: the filmstrip's "Shot actions" menu (WAI-ARIA APG menu, `QueueCardMenu`
 * precedent). It renders fixed in a portal so the filmstrip's scroll box cannot clip it.
 */
export function CaptureFilmstripMenu({ left, top, items, onClose }: CaptureFilmstripMenuProps): ReactElement {
  const menuRef = useRef<HTMLDivElement | null>(null)
  const [position, setPosition] = useState({ left, top })
  const onCloseRef = useRef(onClose)
  onCloseRef.current = onClose

  // Keep the whole menu inside the viewport once its size is known.
  useLayoutEffect(() => {
    const rect = menuRef.current?.getBoundingClientRect()
    const width = rect?.width ?? 0
    const height = rect?.height ?? 0
    setPosition({
      left: Math.max(0, Math.min(left, window.innerWidth - width)),
      top: Math.max(0, Math.min(top, window.innerHeight - height)),
    })
  }, [left, top])

  useEffect(() => {
    menuRef.current?.querySelector<HTMLButtonElement>('[role="menuitem"]')?.focus()
  }, [])

  // A pointer press outside, or the window losing focus, dismisses without moving focus.
  useEffect(() => {
    const onPointerDown = (event: PointerEvent): void => {
      const menu = menuRef.current
      if (menu !== null && event.target instanceof Node && !menu.contains(event.target)) {
        onCloseRef.current(false)
      }
    }
    const onBlur = (): void => {
      onCloseRef.current(false)
    }
    document.addEventListener('pointerdown', onPointerDown, true)
    window.addEventListener('blur', onBlur)
    return () => {
      document.removeEventListener('pointerdown', onPointerDown, true)
      window.removeEventListener('blur', onBlur)
    }
  }, [])

  const focusAt = (pick: (current: number, count: number) => number): void => {
    const nodes = Array.from(menuRef.current?.querySelectorAll<HTMLButtonElement>('[role="menuitem"]') ?? [])
    if (nodes.length === 0) {
      return
    }
    const active = document.activeElement
    const current = active instanceof HTMLButtonElement ? nodes.indexOf(active) : -1
    nodes[pick(current, nodes.length)]?.focus()
  }

  const onKeyDown = (event: KeyboardEvent<HTMLDivElement>): void => {
    switch (event.key) {
      case 'Escape':
        // The editor's window-level Escape handler must not also cancel a colour edit.
        event.preventDefault()
        event.stopPropagation()
        onClose(true)
        return
      case 'Tab':
        onClose(false)
        return
      case 'ArrowDown':
        event.preventDefault()
        focusAt((current, count) => (current + 1) % count)
        return
      case 'ArrowUp':
        event.preventDefault()
        focusAt((current, count) => (current - 1 + count) % count)
        return
      case 'Home':
        event.preventDefault()
        focusAt(() => 0)
        return
      case 'End':
        event.preventDefault()
        focusAt((_current, count) => count - 1)
        return
      default:
    }
  }

  return createPortal(
    <div
      ref={menuRef}
      role="menu"
      aria-label="Shot actions"
      data-testid="capture-filmstrip-menu"
      className={menuClasses}
      style={{ position: 'fixed', left: position.left, top: position.top }}
      onKeyDown={onKeyDown}
      onContextMenu={(event) => {
        event.preventDefault()
      }}
    >
      {items.map((item) => (
        <button
          key={item.id}
          type="button"
          role="menuitem"
          tabIndex={-1}
          data-testid={item.testId}
          className={[itemClasses, item.destructive === true ? 'text-error' : 'text-fg'].join(' ')}
          onClick={() => {
            onClose(true)
            item.run()
          }}
        >
          {item.label}
        </button>
      ))}
    </div>,
    document.body,
  )
}
