import { useEffect, useRef, type KeyboardEvent as ReactKeyboardEvent, type PointerEvent as ReactPointerEvent } from 'react'

import {
  clampScrub,
  parsePositiveInt,
  SCRUB_COARSE_FACTOR,
  SCRUB_MIN,
  scrubSteps,
} from './capture-scrub'
import { WHEEL_IDLE, WHEEL_RESET_MS, wheelSteps, type WheelAccumulator } from './capture-zoom'

export type CaptureScrubFieldProps = {
  id: string
  label: string
  ariaLabel: string
  value: string
  /** Where a gesture starts when the field text is not a positive whole number. */
  fallback: number
  max: number
  inputClassName?: string
  onChange: (value: string) => void
  /** One call per applied step, with the gesture's new value. */
  onPreview: (value: number) => void
  /** Once per gesture that applied a step. */
  onCommit: () => void
  /** Escape, pointercancel or a lost capture mid-gesture. */
  onCancel: () => void
  /**
   * SCRUB_BASE: a new value ends the field's own wheel or key burst without a callback, so the next
   * step starts from `value` again. The parent changes it when it closes the burst or the selection.
   */
  resetKey?: string
}

type Drag = { pointerId: number; lastX: number; carry: number }
/** The fields of a pointer event the drag reads; React and DOM pointer events both have them. */
type DragPointer = Pick<PointerEvent, 'pointerId' | 'clientX' | 'altKey' | 'shiftKey'>

/**
 * SCRUB_FIELD (MEU-85): a visible label that scrubs the number, then the input. The label is
 * aria-hidden and has no tab stop; the input keeps its test id, accessible name and title.
 * SCRUB_GESTURES: label drag, wheel over the field and Up/Down in the input each open one burst,
 * which previews every step and commits once. The burst keeps its own value, not the `value` prop.
 */
export function CaptureScrubField({
  id,
  label,
  ariaLabel,
  value,
  fallback,
  max,
  inputClassName,
  onChange,
  onPreview,
  onCommit,
  onCancel,
  resetKey,
}: CaptureScrubFieldProps) {
  const wrapRef = useRef<HTMLSpanElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const dragRef = useRef<Drag | null>(null)
  const detachRef = useRef<(() => void) | null>(null)
  const burstRef = useRef<number | null>(null)
  const keyRef = useRef<string | null>(null)
  const wheelAccRef = useRef<WheelAccumulator>(WHEEL_IDLE)
  const wheelTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  // The listeners below are bound once; these refs give them the current render's values.
  const latest = useRef({ value, fallback, max, onPreview, onCommit, onCancel })
  latest.current = { value, fallback, max, onPreview, onCommit, onCancel }

  function clearWheelTimer(): void {
    if (wheelTimerRef.current !== null) {
      clearTimeout(wheelTimerRef.current)
      wheelTimerRef.current = null
    }
    wheelAccRef.current = WHEEL_IDLE
  }

  function step(delta: number): void {
    const { value: text, fallback: base, max: top, onPreview: preview } = latest.current
    const from = burstRef.current ?? parsePositiveInt(text) ?? base
    const next = clampScrub(from, delta, SCRUB_MIN, top)
    burstRef.current = next
    if (next !== from) {
      preview(next)
    }
  }

  function endDrag(): void {
    const drag = dragRef.current
    dragRef.current = null
    detachRef.current?.()
    detachRef.current = null
    const handle = wrapRef.current?.querySelector<HTMLElement>(`[data-testid="${id}-scrub"]`)
    if (drag !== null && handle && typeof handle.releasePointerCapture === 'function') {
      try {
        handle.releasePointerCapture(drag.pointerId)
      } catch {
        /* jsdom, or capture already gone */
      }
    }
  }

  function commit(): void {
    clearWheelTimer()
    keyRef.current = null
    if (burstRef.current === null) {
      return
    }
    burstRef.current = null
    latest.current.onCommit()
  }

  function cancel(): void {
    const open = burstRef.current !== null || dragRef.current !== null
    clearWheelTimer()
    keyRef.current = null
    endDrag()
    burstRef.current = null
    if (open) {
      latest.current.onCancel()
    }
  }

  // Kept in a ref so the once-bound listeners call this render's closures.
  const actions = useRef({ step, commit, cancel, move: onDragMove, up: onDragUp, lost: onHandleLost })
  actions.current = { step, commit, cancel, move: onDragMove, up: onDragUp, lost: onHandleLost }

  useEffect(() => {
    // SCRUB_BASE: the parent closed the burst or changed the selection; forget it without a callback.
    if (wheelTimerRef.current !== null) {
      clearTimeout(wheelTimerRef.current)
      wheelTimerRef.current = null
    }
    wheelAccRef.current = WHEEL_IDLE
    keyRef.current = null
    burstRef.current = null
  }, [resetKey])

  useEffect(() => {
    const wrap = wrapRef.current
    if (wrap === null) {
      return
    }
    const onWheel = (event: WheelEvent): void => {
      // Ctrl+wheel stays with the page (zoom); everything else over the field is ours.
      if (event.ctrlKey || dragRef.current !== null) {
        return
      }
      event.preventDefault()
      const delta = event.deltaY !== 0 ? event.deltaY : event.deltaX
      const result = wheelSteps(wheelAccRef.current, { deltaMode: event.deltaMode, deltaY: delta, timeStamp: event.timeStamp })
      wheelAccRef.current = result.acc
      if (result.steps === 0) {
        return
      }
      actions.current.step(result.steps * (event.shiftKey ? SCRUB_COARSE_FACTOR : 1))
      if (wheelTimerRef.current !== null) {
        clearTimeout(wheelTimerRef.current)
      }
      wheelTimerRef.current = setTimeout(() => {
        wheelTimerRef.current = null
        actions.current.commit()
      }, WHEEL_RESET_MS)
    }
    wrap.addEventListener('wheel', onWheel, { passive: false })
    return () => {
      wrap.removeEventListener('wheel', onWheel)
    }
  }, [])

  useEffect(() => {
    // SCRUB_ALT_GUARD: Alt toggles fine steps mid-drag, so it must not open the window menu.
    const onKey = (event: KeyboardEvent): void => {
      if (event.key === 'Alt' && dragRef.current !== null) {
        event.preventDefault()
        return
      }
      if (event.type === 'keydown' && event.key === 'Escape') {
        actions.current.cancel()
      }
    }
    window.addEventListener('keydown', onKey)
    window.addEventListener('keyup', onKey)
    return () => {
      window.removeEventListener('keydown', onKey)
      window.removeEventListener('keyup', onKey)
      detachRef.current?.()
      detachRef.current = null
      if (wheelTimerRef.current !== null) {
        clearTimeout(wheelTimerRef.current)
      }
    }
  }, [])

  function onHandleDown(event: ReactPointerEvent<HTMLSpanElement>): void {
    if (event.button !== 0) {
      return
    }
    event.preventDefault()
    commit()
    inputRef.current?.focus()
    dragRef.current = { pointerId: event.pointerId, lastX: event.clientX, carry: 0 }
    // SCRUB_DRAG_WINDOW (S6 A-3): the drag follows the window, so it keeps scrubbing past the
    // label even if pointer capture never takes effect. Capture is still asked for, and a lost
    // capture still cancels.
    detachRef.current?.()
    const onMove = (moved: PointerEvent): void => actions.current.move(moved)
    const onUp = (released: PointerEvent): void => actions.current.up(released)
    const onCancelled = (cancelled: PointerEvent): void => actions.current.lost(cancelled)
    window.addEventListener('pointermove', onMove, true)
    window.addEventListener('pointerup', onUp, true)
    window.addEventListener('pointercancel', onCancelled, true)
    detachRef.current = () => {
      window.removeEventListener('pointermove', onMove, true)
      window.removeEventListener('pointerup', onUp, true)
      window.removeEventListener('pointercancel', onCancelled, true)
    }
    const handle = event.currentTarget
    if (typeof handle.setPointerCapture === 'function') {
      try {
        handle.setPointerCapture(event.pointerId)
      } catch {
        /* jsdom */
      }
    }
  }

  function onDragMove(event: DragPointer): void {
    const drag = dragRef.current
    if (drag === null || drag.pointerId !== event.pointerId) {
      return
    }
    const result = scrubSteps(drag.carry, event.clientX - drag.lastX, event.altKey)
    drag.lastX = event.clientX
    drag.carry = result.carry
    if (result.steps !== 0) {
      step(result.steps * (event.shiftKey ? SCRUB_COARSE_FACTOR : 1))
    }
  }

  function onDragUp(event: DragPointer): void {
    const drag = dragRef.current
    if (drag === null || drag.pointerId !== event.pointerId) {
      return
    }
    endDrag()
    if (burstRef.current !== null) {
      commit()
      return
    }
    inputRef.current?.select()
  }

  function onHandleLost(event: Pick<PointerEvent, 'pointerId'>): void {
    if (dragRef.current !== null && dragRef.current.pointerId === event.pointerId) {
      cancel()
    }
  }

  function onInputKeyDown(event: ReactKeyboardEvent<HTMLInputElement>): void {
    if (event.key !== 'ArrowUp' && event.key !== 'ArrowDown') {
      return
    }
    event.preventDefault()
    keyRef.current = event.key
    const unit = event.shiftKey ? SCRUB_COARSE_FACTOR : 1
    step(event.key === 'ArrowUp' ? unit : -unit)
  }

  function onInputKeyUp(event: ReactKeyboardEvent<HTMLInputElement>): void {
    if (keyRef.current !== null && event.key === keyRef.current) {
      commit()
    }
  }

  return (
    <span
      ref={wrapRef}
      className="flex shrink-0 items-center gap-1 text-xs text-fg-muted"
      onPointerLeave={() => {
        if (dragRef.current === null && wheelTimerRef.current !== null) {
          commit()
        }
      }}
    >
      <span
        data-testid={`${id}-scrub`}
        aria-hidden="true"
        className="cursor-ew-resize select-none"
        onPointerDown={onHandleDown}
        onLostPointerCapture={onHandleLost}
      >
        {label}
      </span>
      <input
        ref={inputRef}
        data-testid={id}
        aria-label={ariaLabel}
        title={ariaLabel}
        className={inputClassName}
        value={value}
        onChange={(event) => {
          // A typed value ends any open wheel or key burst; the page finishes its own burst first.
          clearWheelTimer()
          keyRef.current = null
          burstRef.current = null
          onChange(event.target.value)
        }}
        onKeyDown={onInputKeyDown}
        onKeyUp={onInputKeyUp}
        onBlur={() => {
          if (dragRef.current === null) {
            commit()
          }
        }}
      />
    </span>
  )
}
