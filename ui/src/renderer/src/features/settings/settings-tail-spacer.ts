import { useEffect, useRef, useState, type RefObject } from 'react'

/**
 * Settings tail spacer (MEU-70, Session 31 plan D-9 / D-16). A bottom spacer that lets the last
 * section scroll up to the same position a rail click scrolls it to, so every section can reach
 * the rail's top band and become current while scrolling.
 */

/** The `scroll-mt-4` on every section frame, which `revealSection` honours (block 'start'). */
export const SECTION_SCROLL_MARGIN = 16

type SpacerInput = {
  /** The scroller's clientHeight. */
  clientHeight: number
  /** Content height from the last section's top to the end of the scroll content, spacer excluded. */
  belowLastTop: number
  /** SECTION_SCROLL_MARGIN. */
  margin: number
}

function usable(value: number): boolean {
  return Number.isFinite(value) && value >= 0
}

/**
 * The smallest spacer that lets the last section's top reach `margin` below the scroller's top.
 * Any non-finite or negative input fails closed to 0 (no spacer, today's layout).
 */
export function tailSpacerHeight({ clientHeight, belowLastTop, margin }: SpacerInput): number {
  if (!usable(clientHeight) || !usable(belowLastTop) || !usable(margin)) {
    return 0
  }
  return Math.max(0, Math.ceil(clientHeight - margin - belowLastTop))
}

type BelowInput = {
  scrollHeight: number
  /** The spacer's current height; subtracting it makes the measurement a fixpoint. */
  spacerHeight: number
  /** The last section's getBoundingClientRect().top. */
  lastTopInViewport: number
  /** The scroller's getBoundingClientRect().top. */
  scrollerTop: number
  scrollTop: number
}

/** Content height below the last section's top, excluding the spacer itself. */
export function belowLastTop({ scrollHeight, spacerHeight, lastTopInViewport, scrollerTop, scrollTop }: BelowInput): number {
  return scrollHeight - spacerHeight - (lastTopInViewport - scrollerTop + scrollTop)
}

/** The nearest scrolling ancestor (the AppShell `<main>`); null when the page does not scroll. */
function scroller(node: HTMLElement | null): HTMLElement | null {
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

/**
 * Measure the spacer for the settings page rooted at `rootRef`. It observes the scroller and the
 * section frames, never the spacer or its column, and applies each height in an animation frame,
 * so a height change cannot re-trigger its own observer. Without ResizeObserver the height stays 0.
 */
export function useTailSpacer(rootRef: RefObject<HTMLElement | null>, sectionKeys: string): number {
  const [height, setHeight] = useState(0)
  // The height last handed to the spacer. It outlives effect restarts (a section-list change keeps
  // the rendered spacer), so every measurement subtracts the spacer that is actually there.
  const applied = useRef(0)

  useEffect(() => {
    const root = rootRef.current
    if (root === null || typeof ResizeObserver !== 'function') {
      return
    }
    const main = scroller(root)
    if (main === null) {
      return
    }
    const scrollerElement: HTMLElement = main
    let frame = 0

    function measure(): void {
      const sections = root?.querySelectorAll<HTMLElement>('[data-settings-section]') ?? []
      const last = sections.length > 0 ? sections[sections.length - 1] : undefined
      if (last === undefined) {
        return
      }
      const next = tailSpacerHeight({
        clientHeight: scrollerElement.clientHeight,
        belowLastTop: belowLastTop({
          scrollHeight: scrollerElement.scrollHeight,
          spacerHeight: applied.current,
          lastTopInViewport: last.getBoundingClientRect().top,
          scrollerTop: scrollerElement.getBoundingClientRect().top,
          scrollTop: scrollerElement.scrollTop,
        }),
        margin: SECTION_SCROLL_MARGIN,
      })
      if (next !== applied.current) {
        applied.current = next
        setHeight(next)
      }
    }

    function schedule(): void {
      window.cancelAnimationFrame(frame)
      frame = window.requestAnimationFrame(measure)
    }

    const observer = new ResizeObserver(schedule)
    observer.observe(scrollerElement)
    for (const section of root.querySelectorAll<HTMLElement>('[data-settings-section]')) {
      observer.observe(section)
    }
    window.addEventListener('resize', schedule)
    schedule()
    return () => {
      window.cancelAnimationFrame(frame)
      observer.disconnect()
      window.removeEventListener('resize', schedule)
    }
  }, [rootRef, sectionKeys])

  return height
}
