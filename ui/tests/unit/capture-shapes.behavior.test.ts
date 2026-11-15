/** @vitest-environment jsdom */

import { act, cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClientProvider } from '@tanstack/react-query'
import { ListOrdered } from 'lucide-react'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import type { Annotation } from '../../src/renderer/src/features/capture/capture-annotate'
import { arrowShaftSpan } from '../../src/renderer/src/features/capture/capture-arrow-head'
import * as store from '../../src/renderer/src/features/capture/capture-style-store'
import { stepBadgeLayout } from '../../src/renderer/src/features/capture/capture-step'
import { TOOL_BUTTON_IDS, TOOL_LETTERS, TOOLBAR_BUTTONS } from '../../src/renderer/src/features/capture/capture-toolbar'
import { CapturePage } from '../../src/renderer/src/features/capture/CapturePage'
import { CAPTURE_SETTINGS_KEY } from '../../src/renderer/src/features/capture/useCaptureSettings'
import { queryClient } from '../../src/renderer/src/lib/query-client'
import { clearCommandState, getCommandState } from '../../src/renderer/src/registry/command-state'
import { listCommands } from '../../src/renderer/src/registry/commandRegistry'
import { createShortcutHandler } from '../../src/renderer/src/registry/shortcuts'

// Session 72 row 3 (MEU-106, MEU-107): line and ellipse shapes, Ctrl+D and the step mark on the real
// CapturePage with the app's query client. The harness is capture-tool-flow.behavior.test.ts's: a
// recording fake server answers GET and PUT /settings/capture (a GET can be held or fail) and the save
// POST, and the registry handler is mounted on the window through createShortcutHandler with the real
// listCommands(), as AppShell mounts it. The default shot is 100x80 on a 100x80 surface, so one screen px
// is one image px. Every element that appears only after Green is looked up with queryBy and asserted
// present, so a Red fails by assertion. The guards AC-106.14, AC-106.31, AC-107.27 and AC-107.29 and the
// STEP_TOOL test AC-107.13 pass on today's tree.

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

type Shot = {
  id: string
  original_path: string
  annotated_path: string | null
  sidecar_path: string | null
  display_name: string
  width: number
  height: number
  file_size: number
  source: string
  created_at: string
  updated_at: string
}

function makeShot(id: string, width: number, height: number): Shot {
  return {
    id,
    original_path: `C:/shots/${id}.png`,
    annotated_path: null,
    sidecar_path: null,
    display_name: `${id}.png`,
    width,
    height,
    file_size: 32,
    source: 'gui',
    created_at: '2026-11-14T12:00:00Z',
    updated_at: '2026-11-14T12:00:00Z',
  }
}

const SMALL = makeShot('small', 100, 80)

const PNG_BYTES = Uint8Array.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0, 0, 0, 13, 0x49, 0x48, 0x44, 0x52])

/** Today's seven Capture card keys (AC-105.23, D-745). */
const CARD_KEYS = [
  'annotated_format',
  'backup_dir',
  'close_to_tray',
  'copy_to_clipboard',
  'flatten_backup',
  'hotkey',
  'inbox_dir',
]

/** A rect mark's keys in the save POST (AC-143.34). */
const RECT_KEYS = ['color', 'height', 'stroke_width', 'type', 'width', 'x', 'y']

/** No `tool_lock`: the lock is on by default (LOCK_DECODE). */
const BASE_SETTINGS: Record<string, unknown> = {
  inbox_dir: 'C:/Pictures/av-kit',
  hotkey: 'F2',
  copy_to_clipboard: false,
  close_to_tray: true,
  flatten_backup: true,
  backup_dir: '',
  annotated_format: 'png',
}

type Tool = 'select' | 'arrow' | 'box' | 'highlight' | 'text' | 'step' | 'redact' | 'eraser'

const STOP_STATUS = 'Step numbers stop at 999'
const STEP_DEFAULT_COLOR = '#E0AF68'

const RED = '#FF0000'
const ARROW_A: Annotation = { type: 'arrow', from: [20, 20], to: [60, 20], color: RED, stroke_width: 3 }
const RECT_A: Annotation = { type: 'rect', x: 10, y: 10, width: 40, height: 20, color: RED, stroke_width: 2 }
const ELLIPSE_A: Annotation = { ...RECT_A, shape: 'ellipse' } as Annotation
const TEXT_B: Annotation = { type: 'text', x: 60, y: 50, text: 'Hi', color: '#FFFFFF', font_size: 16, bg_color: null }

function step(x: number, y: number, number: number, color = STEP_DEFAULT_COLOR, size = 32): Annotation {
  return { type: 'step', x, y, number, color, size }
}

type FetchCall = { url: string; method: string; body: unknown; response?: Record<string, unknown> }
type Outcome = 'ok' | 'fail'
type Held = { method: 'GET' | 'PUT'; release: (outcome: Outcome) => void }
type Box4 = [number, number, number, number]
type Pt = [number, number]
type Mark = Record<string, unknown>

function hrefOf(input: RequestInfo | URL): string {
  if (typeof input === 'string') {
    return input
  }
  if (input instanceof URL) {
    return input.href
  }
  return input.url
}

function jsonResponse(payload: unknown, status = 200): Response {
  return new Response(JSON.stringify(payload), { status, headers: { 'Content-Type': 'application/json' } })
}

function serverError(): Response {
  return jsonResponse({ error: { code: 'INTERNAL', message: 'Internal error', details: null } }, 500)
}

function bindRect(el: HTMLElement, rect: { left: number; top: number; width: number; height: number }): void {
  el.getBoundingClientRect = () =>
    ({
      x: rect.left,
      y: rect.top,
      left: rect.left,
      top: rect.top,
      right: rect.left + rect.width,
      bottom: rect.top + rect.height,
      width: rect.width,
      height: rect.height,
      toJSON: () => ({}),
    }) as DOMRect
}

async function settle(): Promise<void> {
  await act(async () => {
    for (let i = 0; i < 5; i += 1) {
      await new Promise<void>((resolve) => {
        setTimeout(resolve, 0)
      })
    }
  })
}

function present<T extends HTMLElement = HTMLInputElement>(id: string): T {
  const el = screen.queryByTestId(id)
  expect(el, id).not.toBeNull()
  return el as T
}

function armed(tool: Tool): boolean {
  return present(`capture-tool-${tool}`).getAttribute('aria-pressed') === 'true'
}

/** The mark-list chips, one per mark. */
function chips(): HTMLButtonElement[] {
  return Array.from(present('capture-mark-list').querySelectorAll<HTMLButtonElement>('button[aria-pressed]'))
}

/** The index of the selected mark in the mark list, or null. */
function selectedMark(): number | null {
  const index = chips().findIndex((button) => button.getAttribute('aria-pressed') === 'true')
  return index < 0 ? null : index
}

/**
 * The painted marks of `type` in mark-list order. The viewport paints the selected mark first, under the
 * rest, so the DOM order is put back into list order with the selected index.
 */
function painted(type: string): Element[] {
  const dom = Array.from(document.querySelectorAll('[data-testid="capture-annotation"]'))
  const selected = screen.queryByTestId('capture-mark-list') === null ? null : selectedMark()
  const ordered = selected === null || dom.length === 0 ? dom : [...dom.slice(1, selected + 1), dom[0] as Element, ...dom.slice(selected + 1)]
  return ordered.filter((el) => el.getAttribute('data-annotation-type') === type)
}

/** A box mark's (x, y, width, height), read from a `<rect>` or, for an ellipse, from cx, cy, rx and ry. */
function shapeBox(el: Element | undefined): Box4 | null {
  if (el === undefined) {
    return null
  }
  const n = (name: string): number => Number(el.getAttribute(name))
  if (el.tagName.toLowerCase() === 'ellipse') {
    return [n('cx') - n('rx'), n('cy') - n('ry'), 2 * n('rx'), 2 * n('ry')]
  }
  return [n('x'), n('y'), n('width'), n('height')]
}

function lastShape(): { tag: string; box: Box4 | null } {
  const el = painted('rect').at(-1)
  return { tag: el?.tagName.toLowerCase() ?? '', box: shapeBox(el) }
}

function lastArrow(): { from: Pt; to: Pt; head: string | null } | null {
  const el = painted('arrow').at(-1)
  if (el === undefined) {
    return null
  }
  const n = (name: string): number => Number(el.getAttribute(name))
  return { from: [n('x1'), n('y1')], to: [n('x2'), n('y2')], head: el.getAttribute('data-head') }
}

/** The centre of a painted step's circle, in list order. */
function stepCentre(index: number): Pt | null {
  const circle = painted('step')[index]?.querySelector('circle')
  if (circle === null || circle === undefined) {
    return null
  }
  return [Number(circle.getAttribute('cx')), Number(circle.getAttribute('cy'))]
}

function hexValue(): string {
  return present('capture-color').value.toUpperCase()
}

function radio(id: string): HTMLInputElement {
  return present<HTMLInputElement>(id)
}

function statusText(): string {
  return present('capture-status').textContent ?? ''
}

function resizeHandles(): number {
  return document.querySelectorAll('[data-testid^="capture-handle-resize-"]').length
}

function focusedHint(target: HTMLElement, hintId: string): string | null {
  act(() => {
    target.focus()
  })
  const text = screen.queryByTestId(hintId)?.textContent ?? null
  act(() => {
    target.blur()
  })
  return text
}

/** MEU-80 TA-11: the focus target is the `${id}-tip` wrapper when the button is disabled, else the button. */
function hintOf(id: string): string | null {
  const button = present<HTMLButtonElement>(id)
  return focusedHint(button.disabled ? present(`${id}-tip`) : button, `${id}-hint`)
}

function keyOn(target: Element, key: string, init: KeyboardEventInit = {}, type: 'keydown' | 'keyup' = 'keydown'): KeyboardEvent {
  const event = new KeyboardEvent(type, { key, bubbles: true, cancelable: true, ...init })
  act(() => {
    target.dispatchEvent(event)
  })
  return event
}

function ctrlD(target: Element): KeyboardEvent {
  return keyOn(target, 'd', { ctrlKey: true, code: 'KeyD' })
}

function focusOn(el: HTMLElement): void {
  act(() => {
    el.focus()
  })
}

/** A mark moved by (dx, dy), every other field kept. */
function moved(mark: Mark, dx: number, dy: number): Mark {
  if (mark.type === 'arrow') {
    const from = mark.from as Pt
    const to = mark.to as Pt
    return { ...mark, from: [from[0] + dx, from[1] + dy], to: [to[0] + dx, to[1] + dy] }
  }
  return { ...mark, x: (mark.x as number) + dx, y: (mark.y as number) + dy }
}

describe('MEU-106 and MEU-107 capture shapes and steps', () => {
  let user: ReturnType<typeof userEvent.setup>
  const calls: FetchCall[] = []
  const held: Held[] = []
  let savedMarks: unknown[]
  let stored: Record<string, unknown>
  let shot: Shot
  // D-765: true serves an empty catalog, the only way to have no shot selected.
  let noShots = false
  let getPlan: Array<'ok' | 'hold'>
  let getFails: boolean
  let shortcutListener: (event: KeyboardEvent) => void

  function mockApi(): void {
    window.api = {
      getBackendUrl: async () => 'http://127.0.0.1:51234/api/v1',
      getToken: async () => 'gui-nonce',
      logStartupMetric: () => undefined,
      showDirectoryDialog: async () => 'C:/Pictures/av-kit',
      showFileDialog: async () => 'C:/e2e/sample.txt',
      showFilesDialog: async () => [],
      getPathForFile: () => 'C:/e2e/sample.mp4',
      openPath: async () => undefined,
      showItemInFolder: async () => undefined,
      readClipboardText: async () => '',
      writeClipboardText: async () => undefined,
      readTextFile: async () => ({ text: '', basename: 'x.txt' }),
      copyMcpConfig: async () => ({ ok: true as const }),
      subscribeLogs: () => () => undefined,
      getLogSnapshot: async () => [],
      getSetupReadiness: async () => ({ descriptorPresent: true, portOk: true, modelsDirWritable: true }),
      getMcpAccessStatus: async () => ({ tokenPresent: true }),
      captureRegion: async () => undefined,
      getHotkeyStatus: async () => ({ accelerator: 'F2', registered: true, inUse: false }),
      onInboxChanged: () => () => undefined,
    }
  }

  function settingsRoute(method: string, body: unknown, call: FetchCall): Promise<Response> | Response {
    if (method === 'PUT') {
      const patch = (body ?? {}) as Record<string, unknown>
      stored = { ...stored, ...patch }
      return jsonResponse(stored)
    }
    if (getFails) {
      return serverError()
    }
    // The answer is the store as it was when the GET arrived, even when the GET is held.
    const snapshot = { ...stored }
    call.response = snapshot
    const plan = getPlan.shift() ?? 'ok'
    if (plan === 'hold') {
      return new Promise<Response>((resolve) => {
        held.push({ method: 'GET', release: (outcome) => resolve(outcome === 'ok' ? jsonResponse(snapshot) : serverError()) })
      })
    }
    return jsonResponse(snapshot)
  }

  beforeEach(() => {
    user = userEvent.setup()
    calls.length = 0
    held.length = 0
    savedMarks = []
    stored = { ...BASE_SETTINGS }
    shot = SMALL
    noShots = false
    getPlan = []
    getFails = false
    // A failing settings GET fails at once instead of after the default retries.
    queryClient.setQueryDefaults(CAPTURE_SETTINGS_KEY, { retry: false })
    URL.createObjectURL = vi.fn(() => 'blob:capture-shot')
    URL.revokeObjectURL = vi.fn()
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = hrefOf(input)
      const method = (init?.method ?? 'GET').toUpperCase()
      const raw = typeof init?.body === 'string' ? init.body : null
      const call: FetchCall = { url, method, body: raw === null || raw.length === 0 ? null : (JSON.parse(raw) as unknown) }
      calls.push(call)
      const path = url.split('?')[0] ?? url
      if (path.includes('/settings/capture')) {
        return settingsRoute(method, call.body, call)
      }
      if (path.includes('/captures/requests')) {
        return jsonResponse({ items: [] })
      }
      if (/\/captures\/.+\/image$/.test(path)) {
        return new Response(PNG_BYTES, { status: 200, headers: { 'Content-Type': 'image/png' } })
      }
      if (path.endsWith('/annotate')) {
        savedMarks = (call.body as { annotations: unknown[] }).annotations
        return jsonResponse({ ...shot, annotations: savedMarks, backup_path: null })
      }
      if (/\/captures\/([^/]+)$/.test(path) && method === 'GET') {
        return jsonResponse({ ...shot, annotations: savedMarks, backup_path: null })
      }
      if (/\/captures\/?$/.test(path)) {
        return jsonResponse({ items: noShots ? [] : [shot] })
      }
      return jsonResponse({})
    })
    vi.stubGlobal('fetch', fetchMock)
    window.fetch = fetchMock as typeof window.fetch
    // SHELL_WIRING as AppShell binds it.
    const handler = createShortcutHandler({
      commands: listCommands(),
      getPage: () => '/capture',
      getState: (page) => getCommandState(page),
      isPaletteOpen: () => false,
      closePalette: () => undefined,
    })
    shortcutListener = (event) => {
      handler(event)
    }
    window.addEventListener('keydown', shortcutListener)
  })

  afterEach(async () => {
    for (let round = 0; round < 10 && held.length > 0; round += 1) {
      for (const entry of held.splice(0, held.length)) {
        entry.release('ok')
      }
      await settle()
    }
    window.removeEventListener('keydown', shortcutListener)
    for (const modal of Array.from(document.querySelectorAll('[data-test-modal="transform"]'))) {
      modal.remove()
    }
    cleanup()
    clearCommandState('/capture')
    queryClient.clear()
    queryClient.setQueryDefaults(CAPTURE_SETTINGS_KEY, {})
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
    store.resetCaptureStyleStore()
  })

  function gets(): number {
    return calls.filter((call) => call.method === 'GET' && call.url.includes('/settings/capture')).length
  }

  function puts(): Array<Record<string, unknown>> {
    return calls
      .filter((call) => call.method === 'PUT' && call.url.includes('/settings/capture'))
      .map((call) => (call.body ?? {}) as Record<string, unknown>)
  }

  function annotatePosts(): Array<{ annotations: Mark[] }> {
    return calls
      .filter((call) => call.method === 'POST' && call.url.endsWith('/annotate'))
      .map((call) => call.body as { annotations: Mark[] })
  }

  function renderPage(): void {
    queryClient.setQueryData(['captures'], { items: noShots ? [] : [shot], pendingInteractive: false })
    mockApi()
    render(createElement(QueryClientProvider, { client: queryClient }, createElement(CapturePage)))
  }

  /**
   * Render with `marks` saved on the shot and the settings GET answering `stored` (BASE_SETTINGS with
   * `settings` merged in, when given), select the shot, and wait until its overlay is ready.
   */
  async function openShot(marks: unknown[] = [], settings?: Record<string, unknown>): Promise<HTMLElement> {
    savedMarks = marks
    shot = SMALL
    if (settings !== undefined) {
      stored = { ...BASE_SETTINGS, ...settings }
    }
    const before = gets()
    renderPage()
    await vi.waitFor(() => {
      expect(screen.queryAllByTestId('capture-filmstrip-item')).toHaveLength(1)
    })
    await user.click(screen.getAllByTestId('capture-filmstrip-item')[0] as HTMLElement)
    await vi.waitFor(() => {
      expect(screen.queryByTestId('capture-draw-surface')?.getAttribute('data-overlay-ready')).toBe('true')
    })
    await vi.waitFor(() => {
      expect(gets()).toBeGreaterThan(before)
    })
    await settle()
    const surface = screen.getByTestId('capture-draw-surface')
    bindRect(surface, { left: 0, top: 0, width: SMALL.width, height: SMALL.height })
    return surface
  }

  /** Unmount, clear the cache and the style store, and open the shot again. */
  async function remount(marks: unknown[] = [], settings?: Record<string, unknown>): Promise<HTMLElement> {
    for (const entry of held.splice(0, held.length)) {
      entry.release('ok')
    }
    await settle()
    cleanup()
    clearCommandState('/capture')
    queryClient.clear()
    store.resetCaptureStyleStore()
    return openShot(marks, settings)
  }

  type Mods = { shiftKey?: boolean; altKey?: boolean }

  function pointer(el: HTMLElement, type: string, x: number, y: number, mods: Mods = {}): void {
    el.dispatchEvent(
      new PointerEvent(type, {
        bubbles: true,
        cancelable: true,
        clientX: x,
        clientY: y,
        shiftKey: mods.shiftKey ?? false,
        altKey: mods.altKey ?? false,
        pointerId: 1,
        pointerType: 'mouse',
        isPrimary: true,
      }),
    )
  }

  async function click(el: HTMLElement, x: number, y: number, mods: Mods = {}): Promise<void> {
    await act(async () => {
      pointer(el, 'pointerdown', x, y, mods)
      pointer(el, 'pointerup', x, y, mods)
    })
  }

  async function drag(el: HTMLElement, from: Pt, to: Pt, mods: Mods = {}): Promise<void> {
    await act(async () => {
      pointer(el, 'pointerdown', from[0], from[1], mods)
      pointer(el, 'pointermove', to[0], to[1], mods)
      pointer(el, 'pointerup', to[0], to[1], mods)
    })
  }

  async function chooseTool(tool: Tool): Promise<void> {
    await user.click(present(`capture-tool-${tool}`))
  }

  /** Select mark `index` through its mark-list chip. */
  async function selectChip(index: number): Promise<void> {
    const chip = chips()[index]
    expect(chip, `chip ${index}`).toBeDefined()
    await user.click(chip as HTMLButtonElement)
    expect(selectedMark(), `mark ${index} is selected`).toBe(index)
  }

  async function pick(id: string): Promise<void> {
    await user.click(radio(id))
  }

  async function undo(): Promise<void> {
    await user.click(present('capture-undo'))
  }

  async function redo(): Promise<void> {
    await user.click(present('capture-redo'))
  }

  /** Type `text` into the hex field and press Enter. */
  async function commitHex(text: string): Promise<void> {
    const hex = present('capture-color')
    await user.clear(hex)
    await user.type(hex, text)
    await user.keyboard('{Enter}')
  }

  async function release(method: 'GET' | 'PUT', outcome: Outcome = 'ok'): Promise<void> {
    const index = held.findIndex((entry) => entry.method === method)
    expect(index, `a held ${method}`).toBeGreaterThanOrEqual(0)
    const [entry] = held.splice(index, 1)
    entry?.release(outcome)
    await settle()
  }

  /** Save, and return the marks of the one save POST. */
  async function saveMarks(): Promise<Mark[]> {
    const before = annotatePosts().length
    const save = present<HTMLButtonElement>('capture-save')
    expect(save.disabled, 'Save is on').toBe(false)
    await user.click(save)
    await vi.waitFor(() => {
      expect(annotatePosts()).toHaveLength(before + 1)
    })
    return annotatePosts()[before]?.annotations ?? []
  }

  function scrubPointer(handle: HTMLElement, type: string, clientX: number): void {
    act(() => {
      handle.dispatchEvent(
        new PointerEvent(type, {
          bubbles: true,
          cancelable: true,
          clientX,
          clientY: 10,
          pointerId: 7,
          pointerType: 'mouse',
          isPrimary: true,
          button: 0,
        }),
      )
    })
  }

  /** One scrub gesture on `${id}-scrub`: a 2 px move is one step. */
  function scrub(id: string, fromX: number, toX: number): void {
    const handle = present(`${id}-scrub`)
    scrubPointer(handle, 'pointerdown', fromX)
    scrubPointer(handle, 'pointermove', toX)
    scrubPointer(handle, 'pointerup', toX)
  }

  function stepSize(): string {
    return present('capture-step-size').value
  }

  // ---------------------------------------------------------------- HEAD_PREVIEW, ELLIPSE_PREVIEW, STEP_PREVIEW

  it('AC-106.9 the viewport draws data-head, one polygon per head and a line over the shaft span', async () => {
    const marks: Annotation[] = [
      { type: 'arrow', from: [10, 20], to: [90, 20], color: RED, stroke_width: 3 },
      { type: 'arrow', from: [10, 40], to: [90, 40], color: RED, stroke_width: 3, head: 'none' },
      { type: 'arrow', from: [10, 60], to: [90, 60], color: RED, stroke_width: 3, head: 'both' },
    ]
    await openShot(marks)
    const groups = painted('arrow')
    expect(groups).toHaveLength(3)
    const heads = ['end', 'none', 'both'] as const
    heads.forEach((head, i) => {
      const g = groups[i]
      const mark = marks[i] as Extract<Annotation, { type: 'arrow' }>
      expect(g?.getAttribute('data-head'), `${head}: data-head`).toBe(head)
      expect(g?.querySelectorAll('polygon').length, `${head}: polygons`).toBe(head === 'none' ? 0 : head === 'end' ? 1 : 2)
      const span = arrowShaftSpan(mark.from, mark.to, mark.stroke_width, head)
      const line = g?.querySelector('line')
      expect(line, `${head}: a line`).not.toBeNull()
      const got = ['x1', 'y1', 'x2', 'y2'].map((name) => Number(line?.getAttribute(name)))
      const want = (span ?? []).flat()
      want.forEach((value, k) => {
        expect(Math.abs((got[k] ?? Number.NaN) - value), `${head}: line [${k}]`).toBeLessThanOrEqual(1e-6)
      })
    })
  })

  it('AC-106.12 an ellipse renders one <ellipse data-shape="ellipse"> from its box and no <rect>; a rect renders a <rect>', async () => {
    await openShot([ELLIPSE_A, { type: 'rect', x: 50, y: 40, width: 30, height: 20, color: RED, stroke_width: 2 }])
    const boxes = painted('rect')
    expect(boxes).toHaveLength(2)
    const ellipse = boxes[0]
    expect(ellipse?.tagName.toLowerCase(), 'the ellipse is an <ellipse>').toBe('ellipse')
    expect(ellipse?.getAttribute('data-shape')).toBe('ellipse')
    expect(['cx', 'cy', 'rx', 'ry'].map((name) => Number(ellipse?.getAttribute(name)))).toEqual([30, 20, 20, 10])
    const rects = Array.from(document.querySelectorAll('rect[data-testid="capture-annotation"]'))
    expect(rects, 'only the rect mark is a <rect>').toHaveLength(1)
    expect(rects[0]?.hasAttribute('data-shape'), 'a rect has no data-shape').toBe(false)
    expect(shapeBox(rects[0])).toEqual([50, 40, 30, 20])
  })

  it('AC-107.11 a step renders a <g> with a circle of radius size / 2 and the number in the contrast colour', async () => {
    await openShot([step(40, 40, 7)])
    const groups = painted('step')
    expect(groups, 'one step group').toHaveLength(1)
    const circle = groups[0]?.querySelector('circle')
    expect(circle, 'a circle').not.toBeNull()
    expect(['cx', 'cy', 'r'].map((name) => Number(circle?.getAttribute(name)))).toEqual([40, 40, 16])
    expect(circle?.getAttribute('fill')?.toUpperCase()).toBe(STEP_DEFAULT_COLOR)
    const text = groups[0]?.querySelector('text')
    expect(text, 'a text').not.toBeNull()
    expect(text?.getAttribute('text-anchor')).toBe('middle')
    expect(Number(text?.getAttribute('x')), "the text's x is the mark's x").toBe(40)
    expect(Number(text?.getAttribute('y'))).toBe(stepBadgeLayout(40, 40, 7, 32).baseline)
    expect(text?.getAttribute('fill')?.toUpperCase(), 'black on the default colour').toBe('#000000')
    expect(text?.textContent).toBe('7')
  })

  // ---------------------------------------------------------------- ELLIPSE handles (guard)

  it('AC-106.14 a selected ellipse shows eight handles; a corner drag keeps shape ellipse; a body drag is one undo step', async () => {
    const surface = await openShot([ELLIPSE_A])
    await chooseTool('select')
    await click(surface, 30, 10)
    expect(selectedMark(), 'a press on the outline selects it').toBe(0)
    expect(resizeHandles(), "the box's eight handles").toBe(8)
    await drag(surface, [50, 30], [70, 34])
    expect(lastShape().box, 'the corner resize').toEqual([10, 10, 60, 24])
    await drag(surface, [40, 22], [45, 27])
    expect(painted('rect'), 'the body drag adds no mark').toHaveLength(1)
    expect(lastShape().box, 'the body drag').toEqual([15, 15, 60, 24])
    await undo()
    expect(lastShape().box, 'the move is one undo step').toEqual([10, 10, 60, 24])
    const marks = await saveMarks()
    expect(marks).toEqual([{ ...ELLIPSE_A, width: 60, height: 24 }])
  })

  // ---------------------------------------------------------------- SHAPE_OPTIONS

  it('AC-106.18 Head and Shape show for Arrow and Box after the stroke control, for no other tool, and show a selected mark', async () => {
    const surface = await openShot([])
    await chooseTool('arrow')
    const head = screen.queryByTestId('capture-arrow-head')
    expect(head, 'the Head control').not.toBeNull()
    expect(radio('capture-arrow-head-end').checked, 'End').toBe(true)
    expect(radio('capture-arrow-head-none').checked).toBe(false)
    expect(radio('capture-arrow-head-both').checked).toBe(false)
    const stroke = present('capture-stroke')
    expect(stroke.compareDocumentPosition(head as HTMLElement) & Node.DOCUMENT_POSITION_FOLLOWING, 'after the stroke').toBeTruthy()
    expect(screen.queryByTestId('capture-box-shape')).toBeNull()
    await chooseTool('box')
    const shape = screen.queryByTestId('capture-box-shape')
    expect(shape, 'the Shape control').not.toBeNull()
    expect(radio('capture-box-shape-rect').checked, 'Rectangle').toBe(true)
    expect(radio('capture-box-shape-ellipse').checked).toBe(false)
    expect(present('capture-stroke').compareDocumentPosition(shape as HTMLElement) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(screen.queryByTestId('capture-arrow-head')).toBeNull()
    for (const tool of ['highlight', 'text', 'redact', 'eraser', 'step', 'select'] as const) {
      await chooseTool(tool)
      expect(screen.queryByTestId('capture-arrow-head'), `${tool}: no Head`).toBeNull()
      expect(screen.queryByTestId('capture-box-shape'), `${tool}: no Shape`).toBeNull()
    }
    void surface
    await remount([{ ...ARROW_A, head: 'both' }, ELLIPSE_A])
    await chooseTool('select')
    await selectChip(0)
    expect(radio('capture-arrow-head-both').checked, 'the selected arrow shows Both').toBe(true)
    await selectChip(1)
    expect(radio('capture-box-shape-ellipse').checked, 'the selected ellipse shows Ellipse').toBe(true)
  })

  it('AC-106.19 a None pick draws a line and an Ellipse pick an ellipse; the defaults add no key; a remount starts at the defaults', async () => {
    const surface = await openShot([])
    await chooseTool('arrow')
    await pick('capture-arrow-head-none')
    await drag(surface, [10, 10], [50, 10])
    await chooseTool('box')
    await pick('capture-box-shape-ellipse')
    await drag(surface, [10, 30], [50, 60])
    const picked = await saveMarks()
    expect(picked).toHaveLength(2)
    expect(picked[0]).toMatchObject({ type: 'arrow', from: [10, 10], to: [50, 10], head: 'none' })
    expect(picked[1]).toMatchObject({ type: 'rect', x: 10, y: 30, width: 40, height: 30, shape: 'ellipse' })

    const again = await remount([])
    await chooseTool('arrow')
    expect(radio('capture-arrow-head-end').checked, 'a remount starts at End').toBe(true)
    await drag(again, [10, 10], [50, 10])
    await chooseTool('box')
    expect(radio('capture-box-shape-rect').checked, 'a remount starts at Rectangle').toBe(true)
    await drag(again, [10, 30], [50, 60])
    const plain = await saveMarks()
    expect(plain).toHaveLength(2)
    expect('head' in (plain[0] ?? {}), 'the default arrow has no head key').toBe(false)
    expect('shape' in (plain[1] ?? {}), 'the default box has no shape key').toBe(false)
  })

  it('AC-106.20 a pick with a mark selected changes it as one undo step and sends no PUT; under Lock it changes the drawn box', async () => {
    await openShot([ARROW_A])
    await chooseTool('select')
    await selectChip(0)
    await pick('capture-arrow-head-both')
    expect(lastArrow()?.head, 'the arrow is Both').toBe('both')
    await undo()
    expect(lastArrow()?.head, 'one undo step back to End').toBe('end')

    await remount([RECT_A])
    await chooseTool('select')
    await selectChip(0)
    await pick('capture-box-shape-ellipse')
    expect(lastShape().tag, 'the rect is an ellipse').toBe('ellipse')
    await undo()
    expect(lastShape().tag, 'one undo step back to a rect').toBe('rect')

    const surface = await remount([])
    await chooseTool('box')
    await drag(surface, [20, 20], [60, 50])
    expect(selectedMark(), 'the drawn box is selected').toBe(0)
    await pick('capture-box-shape-ellipse')
    expect(painted('rect'), 'no second mark').toHaveLength(1)
    expect(lastShape().tag, 'the drawn box is an ellipse').toBe('ellipse')
    expect(puts(), 'no PUT').toEqual([])
  })

  // ---------------------------------------------------------------- MODIFIERS on Line and Ellipse

  const MODIFIER_CASES: Array<[string, (surface: HTMLElement) => Promise<void>]> = [
    [
      'Shift on a Line draw snaps to 45 degrees and keeps head none',
      async (surface) => {
        await chooseTool('arrow')
        await pick('capture-arrow-head-none')
        await drag(surface, [10, 10], [50, 22], { shiftKey: true })
        expect(lastArrow()).toEqual({ from: [10, 10], to: [52, 10], head: 'none' })
      },
    ],
    [
      'Shift on a Line end drag snaps about the fixed end',
      async (surface) => {
        await remount([{ type: 'arrow', from: [20, 60], to: [60, 60], color: RED, stroke_width: 3, head: 'none' }])
        await chooseTool('select')
        await selectChip(0)
        const fresh = screen.getByTestId('capture-draw-surface')
        void surface
        await drag(fresh, [60, 60], [50, 72], { shiftKey: true })
        expect(lastArrow()).toEqual({ from: [20, 60], to: [52, 60], head: 'none' })
      },
    ],
    [
      'Alt on a Line draw does nothing',
      async (surface) => {
        await chooseTool('arrow')
        await pick('capture-arrow-head-none')
        await drag(surface, [10, 70], [50, 74], { altKey: true })
        expect(lastArrow()).toEqual({ from: [10, 70], to: [50, 74], head: 'none' })
      },
    ],
    [
      'Shift on an Ellipse draw draws a circle',
      async (surface) => {
        await chooseTool('box')
        await pick('capture-box-shape-ellipse')
        await drag(surface, [10, 10], [50, 30], { shiftKey: true })
        expect(lastShape()).toEqual({ tag: 'ellipse', box: [10, 10, 40, 40] })
      },
    ],
    [
      'Alt on an Ellipse draw draws from the centre',
      async (surface) => {
        await chooseTool('box')
        await pick('capture-box-shape-ellipse')
        await drag(surface, [30, 30], [40, 35], { altKey: true })
        expect(lastShape()).toEqual({ tag: 'ellipse', box: [20, 25, 20, 10] })
      },
    ],
    [
      'Shift+Alt on an Ellipse draw draws a circle from the centre',
      async (surface) => {
        await chooseTool('box')
        await pick('capture-box-shape-ellipse')
        await drag(surface, [30, 30], [40, 35], { altKey: true, shiftKey: true })
        expect(lastShape()).toEqual({ tag: 'ellipse', box: [20, 20, 20, 20] })
      },
    ],
    [
      'Shift on an Ellipse corner resize keeps 2:1',
      async () => {
        const surface = await remount([ELLIPSE_A])
        await chooseTool('select')
        await selectChip(0)
        await drag(surface, [50, 30], [70, 34], { shiftKey: true })
        expect(lastShape()).toEqual({ tag: 'ellipse', box: [10, 10, 60, 30] })
      },
    ],
    [
      'Shift on an Ellipse edge resize is ignored',
      async () => {
        const surface = await remount([ELLIPSE_A])
        await chooseTool('select')
        await selectChip(0)
        await drag(surface, [50, 20], [70, 24], { shiftKey: true })
        expect(lastShape()).toEqual({ tag: 'ellipse', box: [10, 10, 60, 20] })
      },
    ],
  ]

  it.each(MODIFIER_CASES)('AC-106.21 %s', async (_name, run) => {
    const surface = await openShot([])
    await run(surface)
  })

  // ---------------------------------------------------------------- DUPLICATE

  const DUP_CASES: Array<[string, Annotation]> = [
    ['arrow', { type: 'arrow', from: [20, 20], to: [50, 40], color: RED, stroke_width: 3 }],
    ['line', { type: 'arrow', from: [20, 20], to: [50, 40], color: RED, stroke_width: 3, head: 'none' }],
    ['rect', { type: 'rect', x: 10, y: 10, width: 20, height: 20, color: RED, stroke_width: 3 }],
    ['ellipse', { type: 'rect', x: 10, y: 10, width: 20, height: 20, color: RED, stroke_width: 3, shape: 'ellipse' }],
    ['highlight', { type: 'highlight', x: 10, y: 10, width: 20, height: 20, color: '#FFFF00', opacity: 0.4 }],
    ['text', { type: 'text', x: 20, y: 20, text: 'Hi', color: '#FFFFFF', font_size: 16, bg_color: null }],
    ['redact', { type: 'redact', x: 10, y: 10, width: 20, height: 20, color: '#000000' }],
    ['pixelate', { type: 'pixelate', x: 10, y: 10, width: 20, height: 20, block_size: 10 }],
    ['eraser', { type: 'eraser', x: 10, y: 10, width: 20, height: 20 }],
    ['step', step(20, 20, 1)],
  ]

  it.each(DUP_CASES)('AC-106.23 Ctrl+D copies a selected %s 10 px down and right as one undo step', async (_name, mark) => {
    const surface = await openShot([mark])
    await selectChip(0)
    focusOn(surface)
    const event = ctrlD(surface)
    expect(event.defaultPrevented, 'Ctrl+D is prevented').toBe(true)
    expect(chips(), 'a copy is appended').toHaveLength(2)
    expect(selectedMark(), 'the copy is selected').toBe(1)
    await undo()
    expect(chips(), 'Undo removes the copy').toHaveLength(1)
    expect(selectedMark(), 'and selects nothing').toBeNull()
    await redo()
    const marks = await saveMarks()
    expect(marks).toHaveLength(2)
    const original = marks[0] as Mark
    const copy = moved(original, 10, 10)
    expect(marks[1]).toEqual(mark.type === 'step' ? { ...copy, number: 2 } : copy)
    expect(puts(), 'no PUT').toEqual([])
  })

  const box = (type: string, x: number, y: number, width: number, height: number, extra: Mark = {}): Mark => {
    const fields: Record<string, Mark> = {
      rect: { color: RED, stroke_width: 3 },
      highlight: { color: '#FFFF00', opacity: 0.4 },
      redact: { color: '#000000' },
      pixelate: { block_size: 10 },
      eraser: {},
    }
    return { type, x, y, width, height, ...fields[type], ...extra }
  }
  const ELLIPSE: Mark = { shape: 'ellipse' }
  const EDGE_CASES: Array<[string, Mark, Mark]> = [
    ['rect at the left and top edges', box('rect', 0, 0, 20, 20), box('rect', 10, 10, 20, 20)],
    ['rect with 4 px of room across', box('rect', 85, 20, 10, 10), box('rect', 89, 30, 10, 10)],
    ['rect at the right edge', box('rect', 89, 20, 10, 10), box('rect', 89, 30, 10, 10)],
    ['rect at the bottom edge', box('rect', 20, 69, 10, 10), box('rect', 30, 69, 10, 10)],
    ['rect filling the image', box('rect', 0, 0, 99, 79), box('rect', 0, 0, 99, 79)],
    ['ellipse with 4 px of room across', box('rect', 85, 20, 10, 10, ELLIPSE), box('rect', 89, 30, 10, 10, ELLIPSE)],
    ['ellipse at the right edge', box('rect', 89, 20, 10, 10, ELLIPSE), box('rect', 89, 30, 10, 10, ELLIPSE)],
    ['ellipse at the bottom edge', box('rect', 20, 69, 10, 10, ELLIPSE), box('rect', 30, 69, 10, 10, ELLIPSE)],
    ['ellipse filling the image', box('rect', 0, 0, 99, 79, ELLIPSE), box('rect', 0, 0, 99, 79, ELLIPSE)],
    ...(['highlight', 'redact', 'pixelate', 'eraser'] as const).flatMap((type): Array<[string, Mark, Mark]> => [
      [`${type} at the right edge`, box(type, 90, 20, 10, 10), box(type, 90, 30, 10, 10)],
      [`${type} at the bottom edge`, box(type, 20, 70, 10, 10), box(type, 30, 70, 10, 10)],
      [`${type} filling the image`, box(type, 0, 0, 100, 80), box(type, 0, 0, 100, 80)],
    ]),
    [
      'arrow with 4 px of room across',
      { type: 'arrow', from: [80, 10], to: [95, 20], color: RED, stroke_width: 3 },
      { type: 'arrow', from: [84, 20], to: [99, 30], color: RED, stroke_width: 3 },
    ],
    [
      'text at the right edge',
      { type: 'text', x: 99, y: 40, text: 'Hi', color: '#FFFFFF', font_size: 16, bg_color: null },
      { type: 'text', x: 99, y: 50, text: 'Hi', color: '#FFFFFF', font_size: 16, bg_color: null },
    ],
    ['step at the bottom edge', step(50, 79, 1) as Mark, step(60, 79, 2) as Mark],
  ]

  it.each(EDGE_CASES)('AC-106.24 Ctrl+D on a %s appends exactly the matrix copy', async (_name, mark, copy) => {
    const surface = await openShot([mark])
    await selectChip(0)
    focusOn(surface)
    expect(ctrlD(surface).defaultPrevented, 'Ctrl+D is prevented').toBe(true)
    expect(chips(), 'a copy is appended').toHaveLength(2)
    const marks = await saveMarks()
    expect(marks).toHaveLength(2)
    const original = marks[0] as Mark
    // Every field but the position (and a step's number) equals the original's as the POST carries it.
    const want: Mark = { ...original }
    for (const key of ['x', 'y', 'from', 'to', 'number']) {
      if (key in copy) {
        want[key] = copy[key]
      }
    }
    expect(marks[1]).toEqual(want)
  })

  it('AC-106.25 Ctrl+D copies nothing with no selection, the crop, a draft, a modal, a live drag or no shot; the hex field prevents it', async () => {
    const surface = await openShot([RECT_A, TEXT_B])
    focusOn(surface)
    expect(ctrlD(surface).defaultPrevented, 'nothing selected: not prevented').toBe(false)
    expect(chips(), 'nothing selected: no copy').toHaveLength(2)

    await selectChip(0)
    await user.click(present('capture-tool-crop'))
    present('capture-crop-bar')
    focusOn(surface)
    ctrlD(surface)
    expect(chips(), 'the crop open: no copy').toHaveLength(2)
    await user.click(present('capture-crop-cancel'))

    await chooseTool('select')
    await selectChip(1)
    focusOn(surface)
    keyOn(surface, 'Enter')
    const draft = screen.queryByTestId('capture-text-draft') as HTMLTextAreaElement | null
    expect(draft, 'the draft opened').not.toBeNull()
    ctrlD(draft as HTMLTextAreaElement)
    expect(chips(), 'a draft open: no copy').toHaveLength(2)
    await user.keyboard('{Escape}')

    await selectChip(0)
    const modal = document.createElement('div')
    modal.setAttribute('aria-modal', 'true')
    modal.setAttribute('data-test-modal', 'transform')
    modal.tabIndex = -1
    document.body.appendChild(modal)
    focusOn(modal)
    ctrlD(modal)
    expect(chips(), 'a modal focused: no copy').toHaveLength(2)
    modal.remove()

    await selectChip(0)
    await act(async () => {
      pointer(surface, 'pointerdown', 30, 20)
      pointer(surface, 'pointermove', 35, 25)
    })
    focusOn(surface)
    ctrlD(surface)
    await act(async () => {
      pointer(surface, 'pointerup', 35, 25)
    })
    expect(chips(), 'a live drag: no copy').toHaveLength(2)

    await selectChip(0)
    const hex = present('capture-color')
    focusOn(hex)
    const fromField = ctrlD(hex)
    expect(fromField.defaultPrevented, 'the hex field: prevented').toBe(true)
    expect(chips(), 'the hex field: no copy').toHaveLength(2)

    cleanup()
    clearCommandState('/capture')
    queryClient.clear()
    noShots = true
    renderPage()
    await vi.waitFor(() => {
      expect(present<HTMLButtonElement>('capture-tool-select').disabled).toBe(true)
    })
    await settle()
    ctrlD(document.body)
    expect(document.querySelectorAll('[data-testid="capture-annotation"]'), 'no shot: nothing').toHaveLength(0)
  })

  // ---------------------------------------------------------------- Guards

  it('AC-106.31 no pick, head or shape value reaches the capture settings', async () => {
    const surface = await openShot([])
    await chooseTool('arrow')
    const none = screen.queryByTestId('capture-arrow-head-none')
    if (none !== null) {
      await user.click(none)
    }
    await drag(surface, [10, 10], [50, 10])
    await chooseTool('box')
    const ellipse = screen.queryByTestId('capture-box-shape-ellipse')
    if (ellipse !== null) {
      await user.click(ellipse)
    }
    await drag(surface, [10, 30], [50, 60])
    await settle()
    expect(puts(), 'no PUT').toEqual([])
  })

  it("AC-107.27 after a step style commit the Capture card's unsaved edit stays and its Save sends the seven keys", async () => {
    await openShot([])
    await user.click(present('capture-settings-toggle'))
    const inbox = present('capture-inbox-path')
    await user.clear(inbox)
    await user.type(inbox, 'C:/Pictures/inbox-9')
    await chooseTool('step')
    if (screen.queryByTestId('capture-color') !== null) {
      await commitHex('#123456')
    }
    await settle()
    expect(present('capture-inbox-path').value, 'the unsaved edit stays').toBe('C:/Pictures/inbox-9')
    await user.click(present('capture-page-save'))
    await vi.waitFor(() => {
      expect(puts().some((body) => 'inbox_dir' in body)).toBe(true)
    })
    const card = puts().find((body) => 'inbox_dir' in body) ?? {}
    expect(Object.keys(card).sort(), 'the card body has no step leaf').toEqual(CARD_KEYS)
    expect(card.inbox_dir).toBe('C:/Pictures/inbox-9')
  })

  it('AC-107.29 a step colour commit with nothing selected adds no key to the saved marks', async () => {
    const surface = await openShot([])
    await chooseTool('box')
    await drag(surface, [10, 10], [40, 30])
    await chooseTool('step')
    expect(selectedMark(), 'nothing is selected').toBeNull()
    if (screen.queryByTestId('capture-color') !== null) {
      await commitHex('#123456')
    }
    await settle()
    const marks = await saveMarks()
    expect(marks).toHaveLength(1)
    expect(Object.keys(marks[0] ?? {}).sort()).toEqual(RECT_KEYS)
  })

  // ---------------------------------------------------------------- STEP_TOOL

  it('AC-107.13 Step follows Text in the tool group, with ListOrdered, its hint, no keyshortcut and no letter; no shot disables it', async () => {
    const surface = await openShot([])
    const order = [
      'capture-tool-select',
      'capture-tool-arrow',
      'capture-tool-box',
      'capture-tool-highlight',
      'capture-tool-text',
      'capture-tool-step',
      'capture-tool-redact',
      'capture-tool-eraser',
      'capture-tool-lock',
      'capture-tool-crop',
      'capture-undo',
    ]
    const ids = Array.from(document.querySelectorAll('button[data-testid]'))
      .map((el) => el.getAttribute('data-testid') ?? '')
      .filter((id) => order.includes(id))
    expect(ids).toEqual(order)
    const group = present('capture-tool-step').closest('[role="group"]')
    expect(group?.getAttribute('aria-label')).toBe('Annotation tool')
    expect(TOOLBAR_BUTTONS['capture-tool-step'].icon).toBe(ListOrdered)
    expect(TOOL_BUTTON_IDS.step).toBe('capture-tool-step')
    expect(hintOf('capture-tool-step')).toBe('Step: Places the next number')
    expect(present('capture-tool-step').getAttribute('aria-keyshortcuts')).toBeNull()
    expect(present('capture-tool-step').getAttribute('aria-label')).toBe('Step')
    expect('step' in TOOL_LETTERS, 'no letter').toBe(false)
    const letters = new Set(Object.values(TOOL_LETTERS).map((letter) => letter.toLowerCase()))
    for (const letter of 'abcdefghijklmnopqrstuvwxyz') {
      if (letters.has(letter)) {
        continue
      }
      focusOn(surface)
      keyOn(surface, letter)
      expect(armed('step'), `${letter} does not arm Step`).toBe(false)
    }
    cleanup()
    clearCommandState('/capture')
    queryClient.clear()
    noShots = true
    renderPage()
    await vi.waitFor(() => {
      expect(present<HTMLButtonElement>('capture-tool-step').disabled).toBe(true)
    })
    await settle()
    expect(hintOf('capture-tool-step')).toBe('Step — Select a shot first')
  })

  // ---------------------------------------------------------------- STEP_PLACE

  it('AC-107.14 a press places the next number, one undo step each; one-shot returns to Select; a step 999 stops it', async () => {
    let surface = await openShot([])
    await chooseTool('step')
    await click(surface, 20.4, 30.6)
    expect(painted('step'), 'step 1').toHaveLength(1)
    expect(armed('step'), 'under Lock Step stays armed').toBe(true)
    expect(selectedMark(), 'the step is selected').toBe(0)
    await chooseTool('step')
    await click(surface, 60, 40)
    expect(painted('step'), 'step 2').toHaveLength(2)
    expect(selectedMark()).toBe(1)
    const two = await saveMarks()
    expect(two).toEqual([step(20, 31, 1), step(60, 40, 2)])
    await undo()
    expect(painted('step'), 'one undo step').toHaveLength(1)
    await undo()
    expect(painted('step'), 'one undo step each').toHaveLength(0)

    surface = await remount([step(10, 10, 1), step(30, 10, 2), step(50, 10, 3)])
    await selectChip(1)
    focusOn(surface)
    keyOn(surface, 'Delete')
    expect(chips(), 'step 2 is deleted').toHaveLength(2)
    await chooseTool('step')
    await click(surface, 70, 60)
    const gap = await saveMarks()
    expect(gap.at(-1), 'the largest plus one').toEqual(step(70, 60, 4))

    surface = await remount([])
    await chooseTool('step')
    await drag(surface, [20, 20], [60, 60])
    expect(painted('step'), 'a press and drag places one').toHaveLength(1)
    expect(await saveMarks()).toEqual([step(20, 20, 1)])

    surface = await remount([], { tool_lock: false })
    await chooseTool('step')
    await click(surface, 30, 30)
    expect(painted('step')).toHaveLength(1)
    expect(armed('select'), 'one-shot returns to Select').toBe(true)
    expect(selectedMark(), 'with the step selected').toBe(0)

    surface = await remount([step(50, 50, 999)], {})
    await chooseTool('step')
    await click(surface, 20, 20)
    expect(painted('step'), 'nothing is placed').toHaveLength(1)
    expect(statusText()).toBe(STOP_STATUS)
  })

  // ---------------------------------------------------------------- STEP_STYLE

  it('AC-107.16 Step shows its saved colour and size; a hex commit and a scrub PUT one leaf; a selected step restyles with no PUT', async () => {
    const surface = await openShot([], { step_color: '#112233', step_size: 48 })
    await chooseTool('step')
    expect(hexValue(), 'the saved step colour').toBe('#112233')
    expect(screen.queryByTestId('capture-step-size'), 'the Size field').not.toBeNull()
    expect(stepSize(), 'the saved step size').toBe('48')
    expect(screen.queryByTestId('capture-stroke'), 'no stroke control').toBeNull()
    await commitHex('#123456')
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(1)
    })
    const raw = calls.find((call) => call.method === 'PUT' && call.url.includes('/settings/capture'))
    expect(JSON.stringify(raw?.body), 'the trace').toBe('{"step_color":"#123456"}')
    await click(surface, 30, 30)
    await chooseTool('step')
    scrub('capture-step-size', 100, 120)
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(2)
    })
    expect(Object.keys(puts()[1] ?? {})).toEqual(['step_size'])
    expect(puts()[1]?.step_size, 'the PUT carries the field').toBe(Number(stepSize()))
    expect(Number(stepSize()), 'the scrub grew the size').toBeGreaterThan(48)
    const marks = await saveMarks()
    expect(marks[0], 'the step has the committed colour').toMatchObject({ type: 'step', color: '#123456', size: 48 })

    await chooseTool('select')
    await selectChip(0)
    await commitHex('#abcdef')
    await settle()
    expect(painted('step')[0]?.querySelector('circle')?.getAttribute('fill')?.toUpperCase(), 'restyled').toBe('#ABCDEF')
    expect(puts(), 'no PUT for a mark restyle').toHaveLength(2)
    await undo()
    expect(painted('step')[0]?.querySelector('circle')?.getAttribute('fill')?.toUpperCase(), 'one undo step').toBe('#123456')
  })

  it('AC-107.16 held GET: a size commit shows at once, and the old GET answer leaves the new size', async () => {
    getPlan = ['hold']
    await openShot([])
    await chooseTool('step')
    scrub('capture-step-size', 100, 120)
    const shown = stepSize()
    expect(Number(shown), 'the new size at once').toBeGreaterThan(32)
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(1)
    })
    await release('GET')
    await chooseTool('step')
    expect(stepSize(), 'the old GET answer leaves it').toBe(shown)
  })

  it('AC-107.16 failed GET: the field shows 32; after a commit a failing refetch still shows the committed size', async () => {
    getFails = true
    await openShot([])
    await chooseTool('step')
    expect(stepSize(), 'the default').toBe('32')
    scrub('capture-step-size', 100, 120)
    const shown = stepSize()
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(1)
    })
    await settle()
    await chooseTool('step')
    expect(stepSize(), 'the failing refetch leaves it').toBe(shown)
    expect(Number(shown)).toBeGreaterThan(32)
  })

  // ---------------------------------------------------------------- STEP_HIT

  it('AC-107.18 a press inside the badge selects it; outside misses; a locked drag moves it; arrows nudge; no resize handle', async () => {
    let surface = await openShot([step(40, 40, 1)])
    await chooseTool('select')
    await click(surface, 55, 40)
    expect(selectedMark(), 'inside the badge').toBe(0)
    expect(resizeHandles(), 'no resize handle').toBe(0)
    await click(surface, 90, 75)
    expect(selectedMark()).toBeNull()
    await click(surface, 40 + 16 + 6 + 2, 40)
    expect(selectedMark(), '2 px past the radius and padding').toBeNull()

    surface = await remount([])
    await chooseTool('step')
    await click(surface, 40, 40)
    expect(selectedMark()).toBe(0)
    await drag(surface, [40, 40], [50, 45])
    expect(painted('step'), 'the drag places nothing').toHaveLength(1)
    expect(stepCentre(0), 'the step moved').toEqual([50, 45])
    expect(armed('step')).toBe(true)
    await undo()
    expect(stepCentre(0), 'one undo step').toEqual([40, 40])
    await selectChip(0)
    focusOn(surface)
    keyOn(surface, 'ArrowRight')
    keyOn(surface, 'ArrowRight', {}, 'keyup')
    expect(stepCentre(0), 'the nudge').toEqual([41, 40])
  })

  // ---------------------------------------------------------------- DUPLICATE on a step

  it('AC-107.21 Ctrl+D on a step takes the next number; at 999 nothing is appended and the status shows the stop', async () => {
    let surface = await openShot([step(20, 20, 1), step(60, 20, 2)])
    await selectChip(0)
    focusOn(surface)
    expect(ctrlD(surface).defaultPrevented).toBe(true)
    expect(chips(), 'step 3 is appended').toHaveLength(3)
    expect(selectedMark(), 'and selected').toBe(2)
    expect(stepCentre(2)).toEqual([30, 30])
    expect(painted('step')[2]?.querySelector('text')?.textContent).toBe('3')
    await undo()
    expect(chips()).toHaveLength(2)
    expect(selectedMark()).toBeNull()
    await chooseTool('step')
    await click(surface, 50, 60)
    expect((await saveMarks()).at(-1), 'the next press places 3').toEqual(step(50, 60, 3))

    for (const selected of [1, 0]) {
      surface = await remount([step(50, 50, 999), step(20, 20, 5)])
      await selectChip(selected)
      const undoOff = present<HTMLButtonElement>('capture-undo').disabled
      focusOn(surface)
      expect(ctrlD(surface).defaultPrevented, `step ${selected === 1 ? 5 : 999}: prevented`).toBe(true)
      expect(chips(), 'nothing appended').toHaveLength(2)
      expect(selectedMark(), 'the selection stays').toBe(selected)
      expect(present<HTMLButtonElement>('capture-undo').disabled, 'Undo as it was').toBe(undoOff)
      expect(statusText()).toBe(STOP_STATUS)
    }

    surface = await remount([step(50, 50, 999), { type: 'rect', x: 10, y: 10, width: 20, height: 20, color: RED, stroke_width: 3 }])
    await selectChip(1)
    focusOn(surface)
    ctrlD(surface)
    expect(chips(), 'the rect copies beside a step 999').toHaveLength(3)
    expect(selectedMark()).toBe(2)
  })
})
