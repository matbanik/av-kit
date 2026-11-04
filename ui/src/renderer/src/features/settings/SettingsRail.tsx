import { useEffect, useRef, useState, type RefObject } from 'react'

import { RAIL_GROUPS, type SettingsSection, type SettingsSectionKey } from './settings-sections'

type SettingsRailProps = {
  /** Visible sections in DOM order (the unsupported startup section is omitted by the caller). */
  sections: readonly SettingsSection[]
  /** The settings page root; sections are resolved inside it by `data-settings-section`. */
  rootRef: RefObject<HTMLElement | null>
  /** Sections that need attention (unsaved draft, readiness not all ok). */
  dots: Partial<Record<SettingsSectionKey, boolean>>
  /** ACTIVE_SOURCE (MEU-70): called with the active entry after every change, including the first. */
  onActiveChange?: (key: SettingsSectionKey | null) => void
}

function sectionElement(root: HTMLElement | null, key: SettingsSectionKey): HTMLElement | null {
  return root?.querySelector<HTMLElement>(`[data-settings-section="${key}"]`) ?? null
}

/** The nearest scrolling ancestor is the observer root (the AppShell `<main>`); null means viewport. */
function scrollParent(node: HTMLElement | null): HTMLElement | null {
  let current = node?.parentElement ?? null
  while (current !== null) {
    const overflowY = window.getComputedStyle(current).overflowY
    if (overflowY === 'auto' || overflowY === 'scroll') {
      return current
    }
    current = current.parentElement
  }
  return null
}

function prefersReducedMotion(): boolean {
  return typeof window.matchMedia === 'function' && window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

/** Delay after which a smooth scroll that never started is completed as a jump. */
const SMOOTH_SCROLL_FALLBACK_MS = 450

/**
 * Focus a settings section and bring it to the top of its scroller. Smooth scrolling is used
 * unless reduced motion is preferred; a background/throttled Chromium window can drop a smooth
 * scroll entirely, so a scroller that never emitted a `scroll` event is completed with an instant
 * scroll. Any scroll event means the smooth scroll started (or the user took over), so the
 * fallback stays out of the way even if the scroller is back at its start (Session 31 D-22).
 * Returns a cancel.
 */
export function revealSection(target: HTMLElement): () => void {
  // Focus first: a focus call after a smooth scrollIntoView cancels the scroll in Chromium.
  target.focus({ preventScroll: true })
  if (typeof target.scrollIntoView !== 'function') {
    return () => undefined
  }
  const smooth = !prefersReducedMotion()
  target.scrollIntoView({ behavior: smooth ? 'smooth' : 'auto', block: 'start' })
  if (!smooth) {
    return () => undefined
  }
  const scroller = scrollParent(target)
  const source: HTMLElement | Window = scroller ?? window
  let scrolled = false
  function onScroll(): void {
    scrolled = true
  }
  source.addEventListener('scroll', onScroll, { passive: true })
  const timer = window.setTimeout(() => {
    source.removeEventListener('scroll', onScroll)
    if (!scrolled && target.isConnected) {
      target.scrollIntoView({ behavior: 'auto', block: 'start' })
    }
  }, SMOOTH_SCROLL_FALLBACK_MS)
  return () => {
    window.clearTimeout(timer)
    source.removeEventListener('scroll', onScroll)
  }
}

const CLICK_LOCK_MS = 800
/** A click's scroll has settled once its scroller has emitted no `scroll` event for this long. */
const SCROLL_SETTLE_MS = 150
/** Upper bound on how long a click owns the active entry, whatever the scroll does. */
const CLICK_LOCK_MAX_MS = 3000

/**
 * Call `release` once a click's scroll has settled (Session 27 A-6). A smooth scroll emits a
 * `scroll` event per frame, so the hold ends `SCROLL_SETTLE_MS` after the last one; its duration is
 * platform-dependent (Chromium on Windows outlasts 800 ms on a long page), so a fixed lock let the
 * observer reclaim the entry mid-scroll. Without any scroll the original `CLICK_LOCK_MS` applies;
 * `CLICK_LOCK_MAX_MS` caps it. Returns a cancel.
 */
function holdUntilScrollSettles(scroller: HTMLElement | null, release: () => void): () => void {
  const source: HTMLElement | Window = scroller ?? window
  let settle = window.setTimeout(finish, CLICK_LOCK_MS)
  const cap = window.setTimeout(finish, CLICK_LOCK_MAX_MS)
  function onScroll(): void {
    window.clearTimeout(settle)
    settle = window.setTimeout(finish, SCROLL_SETTLE_MS)
  }
  function cancel(): void {
    window.clearTimeout(settle)
    window.clearTimeout(cap)
    source.removeEventListener('scroll', onScroll)
  }
  function finish(): void {
    cancel()
    release()
  }
  source.addEventListener('scroll', onScroll, { passive: true })
  return cancel
}

/**
 * Sticky section rail (Phase 11 ST3). The active entry follows scroll through an
 * IntersectionObserver; without one (jsdom, older runtimes) activation alone sets it.
 */
export function SettingsRail({ sections, rootRef, dots, onActiveChange }: SettingsRailProps): React.JSX.Element {
  const [active, setActive] = useState<SettingsSectionKey | null>(sections[0]?.key ?? null)
  // A click owns the active entry while its smooth scroll settles, so passing sections cannot
  // steal it (RULE-2: explicit user ownership beats asynchronous updates).
  const clickLockUntil = useRef(0)
  const cancelHold = useRef<() => void>(() => undefined)
  // Set by the observer effect: once the lock expires, re-derive the current entry from the
  // latest crossings unless the clicked section is still on screen.
  const reconcile = useRef<(clicked: SettingsSectionKey) => void>(() => undefined)
  const cancelReveal = useRef<() => void>(() => undefined)
  const keys = sections.map((section) => section.key).join('|')

  useEffect(() => {
    const root = rootRef.current
    if (root === null || typeof IntersectionObserver !== 'function') {
      return
    }
    const ordered = keys.split('|') as SettingsSectionKey[]
    const visible = new Map<Element, boolean>()
    const scroller = scrollParent(root)
    const targets = ordered
      .map((key) => ({ key, element: sectionElement(root, key) }))
      .filter((row): row is { key: SettingsSectionKey; element: HTMLElement } => row.element !== null)
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          visible.set(entry.target, entry.isIntersecting)
        }
        if (Date.now() < clickLockUntil.current) {
          return
        }
        const key = current()
        if (key !== undefined) {
          setActive(key)
        }
      },
      { root: scroller, rootMargin: '0px 0px -60% 0px', threshold: 0 },
    )
    function current(): SettingsSectionKey | undefined {
      // At the bottom of the scroller the last sections can never reach the top band, so the
      // last one whose top is on screen wins there; elsewhere the first section in the band
      // is current.
      const atBottom =
        scroller !== null && scroller.scrollHeight - scroller.scrollTop - scroller.clientHeight < 2
      const bottomEdge = scroller?.getBoundingClientRect().bottom ?? 0
      const chosen = atBottom
        ? targets.filter((row) => row.element.getBoundingClientRect().top < bottomEdge).at(-1)
        : targets.find((row) => visible.get(row.element) === true)
      return chosen?.key
    }
    reconcile.current = (clicked) => {
      const clickedElement = targets.find((row) => row.key === clicked)?.element
      const box = scroller?.getBoundingClientRect()
      if (clickedElement !== undefined && box !== undefined) {
        const top = clickedElement.getBoundingClientRect().top
        if (top >= box.top && top < box.bottom) {
          return
        }
      }
      const key = current()
      if (key !== undefined) {
        setActive(key)
      }
    }
    for (const row of targets) {
      observer.observe(row.element)
    }
    // SCROLL_RECHECK (MEU-70, plan D-17): no crossing fires at the bottom of the scroller, so the
    // at-bottom rule in current() also runs on scroll, once per frame, and never during a click lock.
    const scrollSource: HTMLElement | Window = scroller ?? window
    let frame = 0
    function onScroll(): void {
      if (frame !== 0) {
        return
      }
      frame = window.requestAnimationFrame(() => {
        frame = 0
        if (Date.now() < clickLockUntil.current) {
          return
        }
        const key = current()
        if (key !== undefined) {
          setActive(key)
        }
      })
    }
    scrollSource.addEventListener('scroll', onScroll, { passive: true })
    return () => {
      observer.disconnect()
      scrollSource.removeEventListener('scroll', onScroll)
      window.cancelAnimationFrame(frame)
      reconcile.current = () => undefined
    }
  }, [keys, rootRef])

  useEffect(() => () => {
    cancelReveal.current()
    cancelHold.current()
  }, [])

  // The rail's active entry is the only source of "current" for the section emphasis.
  useEffect(() => {
    onActiveChange?.(active)
  }, [active, onActiveChange])

  function activate(key: SettingsSectionKey): void {
    clickLockUntil.current = Date.now() + CLICK_LOCK_MAX_MS
    cancelHold.current()
    setActive(key)
    const target = sectionElement(rootRef.current, key)
    cancelHold.current = holdUntilScrollSettles(target === null ? null : scrollParent(target), () => {
      clickLockUntil.current = 0
      reconcile.current(key)
    })
    if (target === null) {
      return
    }
    cancelReveal.current()
    cancelReveal.current = revealSection(target)
  }

  return (
    <nav
      data-testid="settings-rail"
      aria-label="Settings sections"
      className="flex gap-4 overflow-x-auto min-[1000px]:sticky min-[1000px]:top-4 min-[1000px]:flex-col min-[1000px]:self-start min-[1000px]:overflow-visible"
    >
      {RAIL_GROUPS.map((group) => {
        const entries = sections.filter((section) => section.group === group)
        if (entries.length === 0) {
          return null
        }
        const headingId = `settings-rail-group-${group.toLowerCase()}`
        return (
          <div key={group} role="group" aria-labelledby={headingId} className="flex shrink-0 gap-1 min-[1000px]:flex-col">
            <p
              id={headingId}
              className="cursor-default select-none self-center rounded-[var(--radius-control)] bg-bg-subtle/20 px-2 py-1 text-xs font-semibold uppercase tracking-wider text-fg-muted min-[1000px]:self-stretch"
            >
              {group}
            </p>
            {entries.map((section) => {
              const current = active === section.key
              return (
                <button
                  key={section.key}
                  type="button"
                  data-testid={`settings-rail-${section.key}`}
                  aria-current={current ? 'location' : undefined}
                  onClick={() => activate(section.key)}
                  className={[
                    'flex shrink-0 items-center justify-between gap-2 whitespace-nowrap rounded-[var(--radius-control)] px-2 py-1 text-left text-sm',
                    'transition-[background-color,color] duration-[var(--duration-fast)] ease-[var(--ease-out)]',
                    'focus-visible:outline-none focus-visible:shadow-[0_0_0_3px_var(--color-accent-ring)]',
                    current ? 'bg-accent/10 text-fg' : 'text-fg-muted hover:bg-bg-elevated',
                  ].join(' ')}
                >
                  <span>{section.label}</span>
                  {dots[section.key] === true ? (
                    <span
                      data-testid={`settings-rail-dot-${section.key}`}
                      className="h-2 w-2 rounded-full bg-accent-orange"
                      aria-label="Needs attention"
                    />
                  ) : null}
                </button>
              )
            })}
          </div>
        )
      })}
    </nav>
  )
}
