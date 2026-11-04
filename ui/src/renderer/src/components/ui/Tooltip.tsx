import {
  cloneElement,
  useEffect,
  useId,
  useLayoutEffect,
  useRef,
  useState,
  type FocusEvent,
  type ReactElement,
} from 'react'
import { createPortal } from 'react-dom'

/** HINT_TIMING: a hover shows the hint after this delay; focus shows it at once. */
export const HINT_DELAY_MS = 400
/** HINT_TIMING: leaving the trigger (or the hint) hides it after this grace, so the pointer can cross the gap. */
export const HINT_GRACE_MS = 120

const GAP_PX = 6
const EDGE_PX = 8

const HINT_CLASSES = [
  'fixed z-50 px-2 py-0.5 text-xs',
  'bg-bg-elevated text-fg border border-border',
  'rounded-[var(--radius-control)] shadow-[var(--shadow-elevated)]',
].join(' ')

// The disabled wrapper is the tab stop, so it carries the Button focus ring.
const DISABLED_WRAPPER_FOCUS =
  'rounded-[var(--radius-control)] focus-visible:outline-none focus-visible:shadow-[0_0_0_3px_var(--color-accent-ring)]'

/** HINT_SINGLETON: hides whichever hint is shown, so showing one hides any other. */
let hideActive: (() => void) | null = null

/** HINT_TEXT: the name alone when enabled or without a reason; otherwise the name, an em dash and the reason. */
export function hintText(label: string, disabled: boolean, reason: string | undefined): string {
  return disabled && reason !== undefined && reason !== '' ? `${label} — ${reason}` : label
}

/** TOOLTIP_PLACEMENT: centred below the trigger, flipped above near the bottom, clamped 8 px inside the window. */
export function placeHint(
  trigger: Pick<DOMRect, 'left' | 'top' | 'bottom' | 'width'>,
  hint: { width: number; height: number },
  viewport: { width: number; height: number },
): { left: number; top: number } {
  let top = trigger.bottom + GAP_PX
  if (top + hint.height > viewport.height - EDGE_PX) {
    top = trigger.top - GAP_PX - hint.height
  }
  const centred = trigger.left + trigger.width / 2 - hint.width / 2
  const left = Math.max(EDGE_PX, Math.min(centred, viewport.width - EDGE_PX - hint.width))
  return { left, top }
}

type ChildProps = {
  'aria-describedby'?: string
  title?: string
}

export type TooltipProps = {
  /** The wrapped control's test id: the wrapper is `{id}-tip`, the hint `{id}-hint`. */
  id: string
  /** The control's accessible name. */
  label: string
  /** Why the control is disabled; shown after the name only while `disabled`. */
  reason?: string
  /** The child is disabled: the wrapper becomes the focus target. */
  disabled?: boolean
  /** Hides the hint and blocks showing it (for example while the control's menu is open). */
  suppressed?: boolean
  children: ReactElement<ChildProps>
}

/**
 * TOOLTIP: a rendered hint for an icon-only control. The wrapper span takes the pointer and focus events, because
 * a disabled Button ignores the pointer; the hint is portaled to `document.body` so no overflow clips it.
 */
export function Tooltip({ id, label, reason, disabled = false, suppressed = false, children }: TooltipProps) {
  const hintId = useId()
  const [shown, setShown] = useState(false)
  const [position, setPosition] = useState<{ left: number; top: number } | null>(null)
  const wrapperRef = useRef<HTMLSpanElement>(null)
  const hintRef = useRef<HTMLDivElement>(null)
  const showTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const graceTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  // The hint was shown (or kept) by focus, so it stays until blur or Escape, not until the pointer leaves.
  const heldByFocus = useRef(false)
  // A mouse press is in progress: the focus its default action causes is not a request for the hint.
  const pressRef = useRef(false)
  const suppressedRef = useRef(suppressed)
  suppressedRef.current = suppressed

  const visible = shown && !suppressed
  const text = hintText(label, disabled, reason)

  const hideRef = useRef<() => void>(() => undefined)
  hideRef.current = () => {
    clearTimers()
    heldByFocus.current = false
    setShown(false)
    setPosition(null)
    if (hideActive === hideSelf.current) {
      hideActive = null
    }
  }
  // A stable identity for the singleton store; it always calls the latest hide.
  const hideSelf = useRef(() => {
    hideRef.current()
  })

  function clearTimers(): void {
    if (showTimer.current !== null) {
      clearTimeout(showTimer.current)
      showTimer.current = null
    }
    if (graceTimer.current !== null) {
      clearTimeout(graceTimer.current)
      graceTimer.current = null
    }
  }

  function show(): void {
    clearTimers()
    if (suppressedRef.current) {
      return
    }
    if (hideActive !== null && hideActive !== hideSelf.current) {
      hideActive()
    }
    hideActive = hideSelf.current
    setShown(true)
  }

  function hideAfterGrace(): void {
    if (heldByFocus.current) {
      return
    }
    if (graceTimer.current !== null) {
      clearTimeout(graceTimer.current)
    }
    graceTimer.current = setTimeout(() => {
      graceTimer.current = null
      hideRef.current()
    }, HINT_GRACE_MS)
  }

  useEffect(() => {
    if (suppressed) {
      hideRef.current()
    }
  }, [suppressed])

  useEffect(
    () => () => {
      hideRef.current()
    },
    [],
  )

  useEffect(() => {
    if (!visible) {
      return undefined
    }
    // Escape dismisses; the event is neither prevented nor stopped, so page handlers still see it. The capture
    // phase runs before any target-side stopPropagation, such as the Capture surface's editor keys.
    const onKeyDown = (event: KeyboardEvent): void => {
      if (event.key === 'Escape') {
        hideRef.current()
      }
    }
    document.addEventListener('keydown', onKeyDown, true)
    return () => {
      document.removeEventListener('keydown', onKeyDown, true)
    }
  }, [visible])

  useLayoutEffect(() => {
    if (!visible) {
      return undefined
    }
    const measure = (): void => {
      const wrapper = wrapperRef.current
      const hint = hintRef.current
      if (wrapper === null || hint === null) {
        return
      }
      setPosition(
        placeHint(
          wrapper.getBoundingClientRect(),
          { width: hint.offsetWidth, height: hint.offsetHeight },
          { width: window.innerWidth, height: window.innerHeight },
        ),
      )
    }
    measure()
    window.addEventListener('resize', measure)
    window.addEventListener('scroll', measure, true)
    return () => {
      window.removeEventListener('resize', measure)
      window.removeEventListener('scroll', measure, true)
    }
  }, [visible, text])

  const ownDescribedBy = children.props['aria-describedby']
  const composed = [ownDescribedBy, visible && !disabled ? hintId : undefined].filter(Boolean).join(' ')
  const child = cloneElement(children, {
    title: undefined,
    'aria-describedby': disabled ? ownDescribedBy : composed === '' ? undefined : composed,
  })

  return (
    <span
      ref={wrapperRef}
      data-testid={`${id}-tip`}
      className={disabled ? `inline-flex ${DISABLED_WRAPPER_FOCUS}` : 'inline-flex'}
      tabIndex={disabled ? 0 : undefined}
      aria-describedby={disabled && visible ? hintId : undefined}
      onPointerEnter={() => {
        if (graceTimer.current !== null) {
          clearTimeout(graceTimer.current)
          graceTimer.current = null
        }
        if (shown || showTimer.current !== null || suppressedRef.current) {
          return
        }
        showTimer.current = setTimeout(() => {
          showTimer.current = null
          show()
        }, HINT_DELAY_MS)
      }}
      onPointerLeave={() => {
        if (showTimer.current !== null) {
          clearTimeout(showTimer.current)
          showTimer.current = null
        }
        if (shown) {
          hideAfterGrace()
        }
      }}
      onPointerDown={() => {
        // A click is not a request for the hint.
        hideRef.current()
      }}
      onMouseDown={() => {
        // Skip the focus this press's default action causes; it is consumed there or cleared on release.
        pressRef.current = true
        document.addEventListener(
          'mouseup',
          () => {
            pressRef.current = false
          },
          { once: true },
        )
      }}
      onFocus={() => {
        if (pressRef.current) {
          pressRef.current = false
          return
        }
        show()
        heldByFocus.current = !suppressedRef.current
      }}
      onBlur={(event: FocusEvent<HTMLSpanElement>) => {
        if (event.relatedTarget instanceof Node && event.currentTarget.contains(event.relatedTarget)) {
          return
        }
        hideRef.current()
      }}
    >
      {child}
      {visible
        ? createPortal(
            <div
              ref={hintRef}
              role="tooltip"
              id={hintId}
              data-testid={`${id}-hint`}
              className={HINT_CLASSES}
              style={{
                maxWidth: 'min(32rem, calc(100vw - 16px))',
                left: position?.left ?? 0,
                top: position?.top ?? 0,
                visibility: position === null ? 'hidden' : undefined,
              }}
              onPointerEnter={() => {
                if (graceTimer.current !== null) {
                  clearTimeout(graceTimer.current)
                  graceTimer.current = null
                }
              }}
              onPointerLeave={hideAfterGrace}
            >
              {text}
            </div>,
            document.body,
          )
        : null}
    </span>
  )
}
