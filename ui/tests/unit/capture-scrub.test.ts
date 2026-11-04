/** @vitest-environment jsdom */

import { act, cleanup, render, screen } from '@testing-library/react'
import { createElement } from 'react'
import { afterEach, describe, expect, it, type Mock, vi } from 'vitest'

import { CaptureScrubField } from '../../src/renderer/src/features/capture/CaptureScrubField'
import {
  FONT_SCRUB_MAX,
  SCRUB_COARSE_FACTOR,
  SCRUB_FINE_PX_PER_STEP,
  SCRUB_MIN,
  SCRUB_PX_PER_STEP,
  STROKE_SCRUB_MAX,
  clampScrub,
  parsePositiveInt,
  scrubSteps,
} from '../../src/renderer/src/features/capture/capture-scrub'
import { WHEEL_RESET_MS } from '../../src/renderer/src/features/capture/capture-zoom'

if (typeof PointerEvent === 'undefined') {
  class PointerEventPolyfill extends MouseEvent {
    pointerId: number
    pointerType: string
    isPrimary: boolean
    constructor(
      type: string,
      init: MouseEventInit & { pointerId?: number; pointerType?: string; isPrimary?: boolean } = {},
    ) {
      super(type, init)
      this.pointerId = init.pointerId ?? 1
      this.pointerType = init.pointerType ?? 'mouse'
      this.isPrimary = init.isPrimary ?? true
    }
  }
  globalThis.PointerEvent = PointerEventPolyfill as unknown as typeof PointerEvent
}

afterEach(() => {
  cleanup()
  vi.useRealTimers()
})

describe('MEU-85 scrub math (SCRUB_MATH)', () => {
  it('AC-85.1 scrubSteps truncates toward zero and keeps the remainder in pixels; the constants have their values', () => {
    expect(SCRUB_MIN).toBe(1)
    expect(STROKE_SCRUB_MAX).toBe(100)
    expect(FONT_SCRUB_MAX).toBe(400)
    expect(SCRUB_PX_PER_STEP).toBe(2)
    expect(SCRUB_FINE_PX_PER_STEP).toBe(8)
    expect(SCRUB_COARSE_FACTOR).toBe(10)
    expect(scrubSteps(0, 5, false)).toEqual({ steps: 2, carry: 1 })
    expect(scrubSteps(1, 1, false)).toEqual({ steps: 1, carry: 0 })
    expect(scrubSteps(0, -5, false)).toEqual({ steps: -2, carry: -1 })
    expect(scrubSteps(0, 15, true)).toEqual({ steps: 1, carry: 7 })
  })

  it('AC-85.1 negative: 1 px coarse gives no step and carries the pixel', () => {
    expect(scrubSteps(0, 1, false)).toEqual({ steps: 0, carry: 1 })
  })

  it('AC-85.2 clampScrub clamps to [min, max] and never moves a value against the gesture; parsePositiveInt keeps its behaviour', () => {
    expect(clampScrub(99, 10, 1, 100)).toBe(100)
    expect(clampScrub(1, -1, 1, 100)).toBe(1)
    expect(clampScrub(500, 1, 1, 100)).toBe(500)
    expect(clampScrub(500, -1, 1, 100)).toBe(499)
    expect(parsePositiveInt('12')).toBe(12)
    expect(parsePositiveInt(' 7 ')).toBe(7)
  })

  it('AC-85.2 negative: parsePositiveInt refuses zero, negatives, decimals, words and empty text', () => {
    for (const raw of ['0', '-3', '2.5', 'abc', '']) {
      expect(parsePositiveInt(raw), raw).toBeNull()
    }
  })
})

type Spies = {
  onChange: Mock<(...args: unknown[]) => void>
  onPreview: Mock<(...args: unknown[]) => void>
  onCommit: Mock<(...args: unknown[]) => void>
  onCancel: Mock<(...args: unknown[]) => void>
}

function renderField(value = '3', fallback = 3): Spies {
  const spies: Spies = { onChange: vi.fn(), onPreview: vi.fn(), onCommit: vi.fn(), onCancel: vi.fn() }
  render(
    createElement(CaptureScrubField, {
      id: 'capture-stroke',
      label: 'Stroke',
      ariaLabel: 'Stroke width',
      value,
      fallback,
      max: STROKE_SCRUB_MAX,
      ...spies,
    }),
  )
  return spies
}

function pointer(target: Element, type: string, clientX: number, init: PointerEventInit = {}): void {
  act(() => {
    target.dispatchEvent(
      new PointerEvent(type, {
        bubbles: true,
        cancelable: true,
        clientX,
        clientY: 10,
        pointerId: 1,
        pointerType: 'mouse',
        isPrimary: true,
        button: 0,
        ...init,
      }),
    )
  })
}

function key(target: EventTarget, type: 'keydown' | 'keyup', name: string, init: KeyboardEventInit = {}): KeyboardEvent {
  const event = new KeyboardEvent(type, { key: name, bubbles: true, cancelable: true, ...init })
  act(() => {
    target.dispatchEvent(event)
  })
  return event
}

function wheel(target: Element, init: WheelEventInit): WheelEvent {
  const event = new WheelEvent('wheel', { bubbles: true, cancelable: true, deltaMode: 0, ...init })
  act(() => {
    target.dispatchEvent(event)
  })
  return event
}

describe('MEU-85 CaptureScrubField drag (SCRUB_GESTURES, SCRUB_BASE)', () => {
  it('AC-85.3 a handle drag previews from the field text, Shift is coarse, Alt is fine, pointerup commits once', () => {
    const plain = renderField('3')
    const handle = screen.getByTestId('capture-stroke-scrub')
    pointer(handle, 'pointerdown', 100)
    pointer(handle, 'pointermove', 110)
    pointer(handle, 'pointermove', 120)
    expect(plain.onPreview).toHaveBeenLastCalledWith(13)
    expect(plain.onCommit).not.toHaveBeenCalled()
    pointer(handle, 'pointerup', 120)
    expect(plain.onCommit).toHaveBeenCalledTimes(1)
    cleanup()

    const coarse = renderField('3')
    const coarseHandle = screen.getByTestId('capture-stroke-scrub')
    pointer(coarseHandle, 'pointerdown', 100)
    pointer(coarseHandle, 'pointermove', 104, { shiftKey: true })
    pointer(coarseHandle, 'pointerup', 104, { shiftKey: true })
    expect(coarse.onPreview).toHaveBeenLastCalledWith(23)
    expect(coarse.onCommit).toHaveBeenCalledTimes(1)
    cleanup()

    const fine = renderField('3')
    const fineHandle = screen.getByTestId('capture-stroke-scrub')
    pointer(fineHandle, 'pointerdown', 100)
    pointer(fineHandle, 'pointermove', 116, { altKey: true })
    pointer(fineHandle, 'pointerup', 116, { altKey: true })
    expect(fine.onPreview).toHaveBeenLastCalledWith(5)
    expect(fine.onCommit).toHaveBeenCalledTimes(1)
  })

  it('AC-85.3 a press with no move selects the input text and calls neither onPreview nor onCommit', () => {
    const spies = renderField('12')
    const handle = screen.getByTestId('capture-stroke-scrub')
    const input = screen.getByTestId('capture-stroke') as HTMLInputElement
    pointer(handle, 'pointerdown', 100)
    pointer(handle, 'pointerup', 100)
    expect(document.activeElement).toBe(input)
    expect([input.selectionStart, input.selectionEnd]).toEqual([0, 2])
    expect(spies.onPreview).not.toHaveBeenCalled()
    expect(spies.onCommit).not.toHaveBeenCalled()
  })

  it('AC-85.3 negative: Escape mid-drag cancels without a commit; a secondary-button press does nothing', () => {
    const spies = renderField('3')
    const handle = screen.getByTestId('capture-stroke-scrub')
    const input = screen.getByTestId('capture-stroke')
    pointer(handle, 'pointerdown', 100)
    pointer(handle, 'pointermove', 110)
    key(input, 'keydown', 'Escape')
    pointer(handle, 'pointerup', 110)
    expect(spies.onCancel).toHaveBeenCalledTimes(1)
    expect(spies.onCommit).not.toHaveBeenCalled()
    cleanup()

    const secondary = renderField('3')
    const secondaryHandle = screen.getByTestId('capture-stroke-scrub')
    pointer(secondaryHandle, 'pointerdown', 100, { button: 2 })
    pointer(secondaryHandle, 'pointermove', 140, { button: 2 })
    pointer(secondaryHandle, 'pointerup', 140, { button: 2 })
    expect(secondary.onPreview).not.toHaveBeenCalled()
    expect(secondary.onCommit).not.toHaveBeenCalled()
    expect(secondary.onCancel).not.toHaveBeenCalled()
  })
})

describe('MEU-85 CaptureScrubField wheel and keys (SCRUB_GESTURES)', () => {
  it('AC-85.4 wheel notches preview one step each and commit once after WHEEL_RESET_MS; Shift+horizontal wheel is coarse', () => {
    vi.useFakeTimers({ toFake: ['setTimeout', 'clearTimeout'] })
    const spies = renderField('3')
    const input = screen.getByTestId('capture-stroke')
    expect(wheel(input, { deltaY: -100 }).defaultPrevented).toBe(true)
    wheel(input, { deltaY: -100 })
    wheel(input, { deltaY: -100 })
    expect(spies.onPreview.mock.calls.map((call) => call[0])).toEqual([4, 5, 6])
    expect(spies.onCommit).not.toHaveBeenCalled()
    act(() => {
      vi.advanceTimersByTime(WHEEL_RESET_MS + 1)
    })
    expect(spies.onCommit).toHaveBeenCalledTimes(1)
    cleanup()

    const coarse = renderField('3')
    wheel(screen.getByTestId('capture-stroke'), { deltaY: 0, deltaX: -100, shiftKey: true })
    expect(coarse.onPreview).toHaveBeenLastCalledWith(13)
  })

  it('AC-85.4 Up/Down step the value, Shift is coarse, keyup commits, and unparsable text starts from the fallback', () => {
    const up = renderField('3')
    const input = screen.getByTestId('capture-stroke')
    expect(key(input, 'keydown', 'ArrowUp').defaultPrevented).toBe(true)
    expect(up.onPreview).toHaveBeenLastCalledWith(4)
    key(input, 'keyup', 'ArrowUp')
    expect(up.onCommit).toHaveBeenCalledTimes(1)
    cleanup()

    const down = renderField('30')
    const downInput = screen.getByTestId('capture-stroke')
    key(downInput, 'keydown', 'ArrowDown', { shiftKey: true })
    expect(down.onPreview).toHaveBeenLastCalledWith(20)
    key(downInput, 'keyup', 'ArrowDown', { shiftKey: true })
    expect(down.onCommit).toHaveBeenCalledTimes(1)
    cleanup()

    const fallback = renderField('abc', 16)
    key(screen.getByTestId('capture-stroke'), 'keydown', 'ArrowUp')
    expect(fallback.onPreview).toHaveBeenLastCalledWith(17)
  })

  it('AC-85.4 negative: Ctrl+wheel and ArrowLeft neither preview nor prevent the default', () => {
    const spies = renderField('3')
    const input = screen.getByTestId('capture-stroke')
    expect(wheel(input, { deltaY: -100, ctrlKey: true }).defaultPrevented).toBe(false)
    expect(key(input, 'keydown', 'ArrowLeft').defaultPrevented).toBe(false)
    expect(spies.onPreview).not.toHaveBeenCalled()
  })
})

describe('MEU-85 Alt guard (SCRUB_ALT_GUARD)', () => {
  it('AC-85.5 during a drag a window Alt keydown and keyup are both prevented', () => {
    renderField('3')
    const handle = screen.getByTestId('capture-stroke-scrub')
    pointer(handle, 'pointerdown', 100)
    expect(key(window, 'keydown', 'Alt', { altKey: true }).defaultPrevented).toBe(true)
    expect(key(window, 'keyup', 'Alt').defaultPrevented).toBe(true)
    pointer(handle, 'pointerup', 100)
  })

  it('AC-85.5 negative: after pointerup neither Alt event is prevented', () => {
    renderField('3')
    const handle = screen.getByTestId('capture-stroke-scrub')
    pointer(handle, 'pointerdown', 100)
    pointer(handle, 'pointermove', 110)
    pointer(handle, 'pointerup', 110)
    expect(key(window, 'keydown', 'Alt', { altKey: true }).defaultPrevented).toBe(false)
    expect(key(window, 'keyup', 'Alt').defaultPrevented).toBe(false)
  })
})
