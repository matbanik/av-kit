/** @vitest-environment jsdom */

/**
 * MEU-80 Tooltip primitive (AC-80.1–AC-80.7, AC-80.13): `TOOLTIP`, `HINT_TEXT`, `HINT_TIMING`,
 * `TOOLTIP_PLACEMENT`, `HINT_SINGLETON` and `DESCRIBEDBY_COMPOSE`.
 *
 * The module is imported statically, so before it exists this file fails to load on exactly that import
 * (`AC_CASES` class red-import). Timing runs on fake timers and events go through `fireEvent`, which fires the
 * pointer-over/out pair React needs for its enter/leave emulation.
 */
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, onTestFinished, vi } from 'vitest'

import { HINT_DELAY_MS, HINT_GRACE_MS, Tooltip } from '../../src/renderer/src/components/ui/Tooltip'

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

const here = dirname(fileURLToPath(import.meta.url))
const TOOLTIP_SRC = resolve(here, '../../src/renderer/src/components/ui/Tooltip.tsx')

function tip(id: string): HTMLElement {
  return screen.getByTestId(`${id}-tip`)
}

function hint(id: string): HTMLElement | null {
  return screen.queryByTestId(`${id}-hint`)
}

function describedBy(el: Element): string[] {
  return (el.getAttribute('aria-describedby') ?? '').split(/\s+/).filter(Boolean)
}

function advance(ms: number): void {
  act(() => {
    vi.advanceTimersByTime(ms)
  })
}

function focus(el: HTMLElement): void {
  act(() => {
    el.focus()
  })
}

function blur(el: HTMLElement): void {
  act(() => {
    el.blur()
  })
}

function hover(el: HTMLElement): void {
  fireEvent.pointerEnter(el)
}

function unhover(el: HTMLElement): void {
  fireEvent.pointerLeave(el)
}

beforeEach(() => {
  vi.useFakeTimers()
})

afterEach(() => {
  cleanup()
  vi.useRealTimers()
  vi.restoreAllMocks()
})

describe('MEU-80 Tooltip primitive', () => {
  it('AC-80.1: hover shows one portaled role=tooltip hint after HINT_DELAY_MS and links it by aria-describedby', () => {
    expect(HINT_DELAY_MS).toBe(400)
    render(
      <Tooltip id="t1" label="Arrow">
        <button type="button" aria-label="Arrow" data-testid="t1" />
      </Tooltip>,
    )
    const wrapper = tip('t1')
    const button = screen.getByTestId('t1')
    hover(wrapper)
    advance(HINT_DELAY_MS - 1)
    expect(hint('t1'), 'no hint before HINT_DELAY_MS').toBeNull()
    expect(wrapper.querySelector('[role="tooltip"]')).toBeNull()
    advance(1)
    const shown = hint('t1')
    expect(shown, 'hint after HINT_DELAY_MS').not.toBeNull()
    expect(screen.getAllByRole('tooltip')).toHaveLength(1)
    expect(shown?.getAttribute('role')).toBe('tooltip')
    expect(shown?.parentElement, 'portaled to document.body').toBe(document.body)
    expect(wrapper.contains(shown as HTMLElement)).toBe(false)
    expect(shown?.textContent).toBe('Arrow')
    expect(shown?.id).toBeTruthy()
    expect(describedBy(button)).toContain(shown?.id)
  })

  it('AC-80.2: focus shows the hint at once, blur hides it and removes the hint id', () => {
    render(
      <>
        <Tooltip id="t2" label="Undo">
          <button type="button" aria-label="Undo" data-testid="t2" />
        </Tooltip>
        <button type="button" data-testid="other">
          Other
        </button>
      </>,
    )
    const button = screen.getByTestId('t2')
    const other = screen.getByTestId('other')
    focus(other)
    advance(HINT_DELAY_MS * 2)
    expect(hint('t2'), 'an unrelated focus shows nothing').toBeNull()
    focus(button)
    const shown = hint('t2')
    expect(shown, 'shown at once on focus').not.toBeNull()
    expect(shown?.textContent).toBe('Undo')
    expect(describedBy(button)).toContain(shown?.id)
    const hintId = shown?.id as string
    blur(button)
    expect(hint('t2')).toBeNull()
    expect(describedBy(button)).not.toContain(hintId)
    expect(button.getAttribute('aria-describedby'), 'absent when the child had none').toBeNull()
  })

  it('AC-80.3: Escape, pointerdown and the grace period dismiss; the hint itself is hoverable', () => {
    expect(HINT_GRACE_MS).toBe(120)
    render(
      <Tooltip id="t3" label="Box">
        <button type="button" aria-label="Box" data-testid="t3" />
      </Tooltip>,
    )
    const wrapper = tip('t3')
    // Escape hides, and a later document listener still gets the event, not prevented.
    hover(wrapper)
    advance(HINT_DELAY_MS)
    expect(hint('t3')).not.toBeNull()
    const later = vi.fn((event: KeyboardEvent) => event.defaultPrevented)
    document.addEventListener('keydown', later)
    fireEvent.keyDown(document, { key: 'Escape' })
    document.removeEventListener('keydown', later)
    expect(hint('t3'), 'Escape hides').toBeNull()
    expect(later).toHaveBeenCalledTimes(1)
    expect(later.mock.results[0]?.value, 'Escape is not prevented').toBe(false)
    unhover(wrapper)
    advance(HINT_GRACE_MS * 2)
    // pointerdown cancels a pending show.
    hover(wrapper)
    advance(HINT_DELAY_MS - 100)
    fireEvent.pointerDown(wrapper)
    advance(HINT_DELAY_MS * 2)
    expect(hint('t3'), 'pointerdown cancels the pending show').toBeNull()
    unhover(wrapper)
    advance(HINT_GRACE_MS * 2)
    // pointerdown hides a shown hint.
    hover(wrapper)
    advance(HINT_DELAY_MS)
    expect(hint('t3')).not.toBeNull()
    fireEvent.pointerDown(wrapper)
    expect(hint('t3'), 'pointerdown hides').toBeNull()
    unhover(wrapper)
    advance(HINT_GRACE_MS * 2)
    // pointerleave hides after the grace.
    hover(wrapper)
    advance(HINT_DELAY_MS)
    unhover(wrapper)
    advance(HINT_GRACE_MS - 1)
    expect(hint('t3'), 'still shown inside the grace').not.toBeNull()
    advance(1)
    expect(hint('t3'), 'hidden after the grace').toBeNull()
    // Entering the hint within the grace keeps it; leaving the hint hides it after the grace.
    hover(wrapper)
    advance(HINT_DELAY_MS)
    unhover(wrapper)
    advance(HINT_GRACE_MS / 2)
    hover(hint('t3') as HTMLElement)
    advance(HINT_GRACE_MS + 50)
    expect(hint('t3'), 'a hint entered from the trigger stays').not.toBeNull()
    unhover(hint('t3') as HTMLElement)
    advance(HINT_GRACE_MS)
    expect(hint('t3'), 'leaving the hint hides it').toBeNull()
  })

  it('execution R1 F1: Escape hides the hint while focus sits in an editor that stops keydown propagation', () => {
    // Execution review R1 F1: the Capture surface stops keydown at React's root, so a bubbling document
    // listener never saw Escape. The editor still gets the key and decides about preventDefault itself.
    const editorKey = vi.fn((event: { stopPropagation: () => void; defaultPrevented: boolean }) => {
      event.stopPropagation()
      return event.defaultPrevented
    })
    render(
      <>
        <div tabIndex={0} data-testid="editor" onKeyDown={editorKey} />
        <Tooltip id="t3e" label="Box">
          <button type="button" aria-label="Box" data-testid="t3e" />
        </Tooltip>
      </>,
    )
    const editor = screen.getByTestId('editor')
    focus(editor)
    hover(tip('t3e'))
    advance(HINT_DELAY_MS)
    expect(hint('t3e')).not.toBeNull()
    fireEvent.keyDown(editor, { key: 'Escape' })
    expect(hint('t3e'), 'Escape hides although the editor stops propagation').toBeNull()
    expect(editorKey, 'the editor still handles its Escape').toHaveBeenCalledTimes(1)
    expect(editorKey.mock.results[0]?.value, 'the hint does not prevent Escape').toBe(false)
    expect(document.activeElement, 'focus stays in the editor').toBe(editor)
  })

  it('AC-80.4: a disabled child gets a focusable wrapper; an enabled one does not; no title anywhere', () => {
    const spread = { title: 'x' }
    const { rerender } = render(
      <Tooltip id="t4" label="Undo" reason="Nothing to undo" disabled>
        <button type="button" aria-label="Undo" data-testid="t4" disabled title="Undo" />
      </Tooltip>,
    )
    let wrapper = tip('t4')
    let button = screen.getByTestId('t4')
    expect(wrapper.getAttribute('tabindex'), 'the disabled wrapper is the tab stop').toBe('0')
    expect(wrapper.getAttribute('title')).toBeNull()
    expect(button.getAttribute('title'), 'a JSX title is not rendered').toBeNull()
    expect(wrapper.querySelector('[title]')).toBeNull()
    focus(wrapper)
    const shown = hint('t4')
    expect(shown, 'focusing the wrapper shows the hint').not.toBeNull()
    expect(describedBy(wrapper)).toContain(shown?.id)
    blur(wrapper)
    rerender(
      <Tooltip id="t4" label="Undo">
        <button type="button" aria-label="Undo" data-testid="t4" {...spread} />
      </Tooltip>,
    )
    wrapper = tip('t4')
    button = screen.getByTestId('t4')
    expect(wrapper.getAttribute('tabindex'), 'an enabled wrapper is not a tab stop').toBeNull()
    expect(wrapper.getAttribute('title')).toBeNull()
    expect(button.getAttribute('title'), 'a spread title is not rendered').toBeNull()
    focus(button)
    const enabledHint = hint('t4')
    expect(enabledHint).not.toBeNull()
    expect(describedBy(button)).toContain(enabledHint?.id)
    expect(describedBy(wrapper)).not.toContain(enabledHint?.id)
  })

  it('AC-80.5: HINT_TEXT, HINT_SINGLETON and suppressed', () => {
    const { rerender } = render(
      <>
        <Tooltip id="a" label="Apply to image" reason="Save the overlay first">
          <button type="button" aria-label="Apply to image" data-testid="a" />
        </Tooltip>
        <Tooltip id="b" label="Revert image" reason="Save or discard overlay marks first" disabled>
          <button type="button" aria-label="Revert image" data-testid="b" disabled />
        </Tooltip>
        <Tooltip id="c" label="Redo" reason="" disabled>
          <button type="button" aria-label="Redo" data-testid="c" disabled />
        </Tooltip>
      </>,
    )
    focus(screen.getByTestId('a'))
    expect(hint('a')?.textContent, 'enabled: the label only').toBe('Apply to image')
    blur(screen.getByTestId('a'))
    focus(tip('b'))
    expect(hint('b')?.textContent, 'disabled with a reason').toBe('Revert image — Save or discard overlay marks first')
    blur(tip('b'))
    focus(tip('c'))
    expect(hint('c')?.textContent, 'disabled without a reason').toBe('Redo')
    blur(tip('c'))
    // Singleton: showing B hides A.
    hover(tip('a'))
    advance(HINT_DELAY_MS)
    expect(hint('a')).not.toBeNull()
    hover(tip('b'))
    advance(HINT_DELAY_MS)
    expect(hint('b')).not.toBeNull()
    expect(hint('a'), 'showing B hides A').toBeNull()
    expect(screen.getAllByRole('tooltip')).toHaveLength(1)
    unhover(tip('a'))
    unhover(tip('b'))
    advance(HINT_GRACE_MS * 2)
    // suppressed hides a shown hint and blocks show on hover and focus.
    hover(tip('a'))
    advance(HINT_DELAY_MS)
    expect(hint('a')).not.toBeNull()
    rerender(
      <>
        <Tooltip id="a" label="Apply to image" reason="Save the overlay first" suppressed>
          <button type="button" aria-label="Apply to image" data-testid="a" />
        </Tooltip>
      </>,
    )
    expect(hint('a'), 'suppressed hides the shown hint').toBeNull()
    unhover(tip('a'))
    advance(HINT_GRACE_MS * 2)
    hover(tip('a'))
    advance(HINT_DELAY_MS * 2)
    expect(hint('a'), 'suppressed blocks hover').toBeNull()
    focus(screen.getByTestId('a'))
    expect(hint('a'), 'suppressed blocks focus').toBeNull()
  })

  it('AC-80.6: TOOLTIP_PLACEMENT centres below, clamps to 8 px and flips above near the bottom', () => {
    const HINT_W = 100
    const HINT_H = 20
    let trigger = { left: 450, top: 100, width: 100, height: 30 }
    const rect = (r: { left: number; top: number; width: number; height: number }): DOMRect =>
      ({
        x: r.left,
        y: r.top,
        left: r.left,
        top: r.top,
        right: r.left + r.width,
        bottom: r.top + r.height,
        width: r.width,
        height: r.height,
        toJSON: () => ({}),
      }) as DOMRect
    const isHint = (el: Element): boolean => (el.getAttribute('data-testid') ?? '').endsWith('-hint')
    vi.spyOn(HTMLElement.prototype, 'getBoundingClientRect').mockImplementation(function (this: HTMLElement) {
      return isHint(this) ? rect({ left: 0, top: 0, width: HINT_W, height: HINT_H }) : rect(trigger)
    })
    vi.spyOn(HTMLElement.prototype, 'offsetWidth', 'get').mockImplementation(function (this: HTMLElement) {
      return isHint(this) ? HINT_W : trigger.width
    })
    vi.spyOn(HTMLElement.prototype, 'offsetHeight', 'get').mockImplementation(function (this: HTMLElement) {
      return isHint(this) ? HINT_H : trigger.height
    })
    const viewport = { innerWidth: window.innerWidth, innerHeight: window.innerHeight }
    Object.defineProperty(window, 'innerWidth', { configurable: true, writable: true, value: 1000 })
    Object.defineProperty(window, 'innerHeight', { configurable: true, writable: true, value: 600 })
    onTestFinished(() => {
      Object.defineProperty(window, 'innerWidth', { configurable: true, writable: true, value: viewport.innerWidth })
      Object.defineProperty(window, 'innerHeight', { configurable: true, writable: true, value: viewport.innerHeight })
    })
    render(
      <Tooltip id="t6" label="Zoom in">
        <button type="button" aria-label="Zoom in" data-testid="t6" />
      </Tooltip>,
    )
    const button = screen.getByTestId('t6')
    const place = (): { left: number; top: number; el: HTMLElement } => {
      focus(button)
      const el = hint('t6') as HTMLElement
      expect(el, 'hint shown').not.toBeNull()
      const out = { left: parseFloat(el.style.left), top: parseFloat(el.style.top), el }
      blur(button)
      return out
    }
    const centred = place()
    expect(centred.el.style.position === 'fixed' || /\bfixed\b/.test(centred.el.className), 'position fixed').toBe(true)
    expect(centred.el.className).toMatch(/\bz-50\b/)
    expect(centred.left, 'centred').toBe(450)
    expect(centred.top, 'below by 6').toBe(136)
    trigger = { left: 2, top: 100, width: 20, height: 30 }
    const leftEdge = place()
    expect(leftEdge.left, 'clamped at 8 on the left').toBe(8)
    expect(leftEdge.left).toBeGreaterThanOrEqual(0)
    trigger = { left: 980, top: 100, width: 20, height: 30 }
    expect(place().left, 'clamped at innerWidth - 8 - width on the right').toBe(892)
    trigger = { left: 450, top: 580, width: 100, height: 20 }
    expect(place().top, 'flipped above near the bottom').toBe(554)
  })

  it('AC-80.7: Tooltip.tsx source guard (no features import, hex, transition-all or title; portal; tokens)', () => {
    const violations = (src: string): string[] => {
      const out: string[] = []
      if (/from\s+['"][^'"]*features\//.test(src)) out.push('features import')
      if (/#[0-9a-fA-F]{3,8}\b/.test(src)) out.push('hex colour')
      if (src.includes('transition-all')) out.push('transition-all')
      if (/\btitle=/.test(src)) out.push('title=')
      if (!/createPortal\([\s\S]*?document\.body/.test(src)) out.push('no createPortal(…, document.body)')
      for (const token of ['bg-bg-elevated', 'text-fg', 'border-border']) {
        if (!src.includes(token)) out.push(`no ${token}`)
      }
      return out
    }
    const src = readFileSync(TOOLTIP_SRC, 'utf8')
    expect(violations(src)).toEqual([])
    expect(violations(`${src}\nimport { x } from '../../features/capture/x'\n`)).toContain('features import')
    expect(violations(`${src}\nconst c = '#ff0000'\n`)).toContain('hex colour')
    expect(violations(`${src}\nconst m = 'transition-all'\n`)).toContain('transition-all')
    expect(violations(`${src}\nconst t = <span title="x" />\n`)).toContain('title=')
  })

  it('AC-80.13: DESCRIBEDBY_COMPOSE keeps the child aria-describedby, ref and handlers, enabled and disabled', () => {
    const refs: Array<HTMLButtonElement | null> = []
    const onKeyDown = vi.fn()
    const { rerender } = render(
      <Tooltip id="t13" label="Reorder">
        <button
          type="button"
          aria-label="Reorder"
          aria-describedby="pre-1"
          data-testid="t13"
          ref={(node) => {
            refs.push(node)
          }}
          onKeyDown={onKeyDown}
        />
      </Tooltip>,
    )
    let button = screen.getByTestId('t13')
    expect(refs).toContain(button)
    expect(button.getAttribute('aria-describedby'), 'hidden: own tokens only').toBe('pre-1')
    focus(button)
    const hintId = hint('t13')?.id as string
    expect(hintId).toBeTruthy()
    expect(button.getAttribute('aria-describedby'), 'shown: own tokens then the hint id').toBe(`pre-1 ${hintId}`)
    fireEvent.keyDown(button, { key: 'ArrowDown' })
    expect(onKeyDown, 'the child handler still fires').toHaveBeenCalledTimes(1)
    blur(button)
    expect(button.getAttribute('aria-describedby'), 'after hide: own tokens only').toBe('pre-1')
    rerender(
      <Tooltip id="t13" label="Reorder" disabled>
        <button
          type="button"
          aria-label="Reorder"
          aria-describedby="pre-1"
          data-testid="t13"
          disabled
          ref={(node) => {
            refs.push(node)
          }}
          onKeyDown={onKeyDown}
        />
      </Tooltip>,
    )
    button = screen.getByTestId('t13')
    const wrapper = tip('t13')
    expect(refs).toContain(button)
    expect(wrapper.getAttribute('aria-describedby')).toBeNull()
    focus(wrapper)
    const disabledHintId = hint('t13')?.id as string
    expect(disabledHintId).toBeTruthy()
    expect(wrapper.getAttribute('aria-describedby'), 'the wrapper carries only the hint id').toBe(disabledHintId)
    expect(button.getAttribute('aria-describedby'), 'the child keeps its own token').toBe('pre-1')
    fireEvent.keyDown(button, { key: 'ArrowDown' })
    expect(onKeyDown).toHaveBeenCalledTimes(2)
    blur(wrapper)
    expect(wrapper.getAttribute('aria-describedby'), 'no hint id left behind').toBeNull()
    expect(button.getAttribute('aria-describedby')).toBe('pre-1')
  })
})
