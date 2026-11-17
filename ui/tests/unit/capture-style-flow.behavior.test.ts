/** @vitest-environment jsdom */

import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClientProvider } from '@tanstack/react-query'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import type { Annotation } from '../../src/renderer/src/features/capture/capture-annotate'
import { bodyHandleImagePoint } from '../../src/renderer/src/features/capture/capture-hit-test'
import * as store from '../../src/renderer/src/features/capture/capture-style-store'
import { CapturePage } from '../../src/renderer/src/features/capture/CapturePage'
import { CAPTURE_SETTINGS_KEY } from '../../src/renderer/src/features/capture/useCaptureSettings'
import { queryClient } from '../../src/renderer/src/lib/query-client'

// Session 71 (MEU-105): the style controls on the real CapturePage with the app's query client. A
// recording fake server answers GET and PUT /settings/capture (a PUT can be held or fail) and the save
// POST. The harness is modelled on capture-text-lines.behavior.test.ts; the shot is 200x200 on a
// 200x200 surface, so one screen px is one image px. Marks are found by their content.

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

const SHOT: Shot = {
  id: 'shot-a',
  original_path: 'C:/shots/a.png',
  annotated_path: null,
  sidecar_path: null,
  display_name: 'a.png',
  width: 200,
  height: 200,
  file_size: 32,
  source: 'gui',
  created_at: '2026-11-13T12:00:00Z',
  updated_at: '2026-11-13T12:00:00Z',
}

const PNG_BYTES = Uint8Array.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0, 0, 0, 13, 0x49, 0x48, 0x44, 0x52])

/** The Capture card's Save body after an inbox-only edit: only the changed leaf (CAPTURE_SAVE_CHANGED_ONLY, D-966; D-1066). */
const CARD_KEYS = ['inbox_dir']

const BASE_SETTINGS: Record<string, unknown> = {
  inbox_dir: 'C:/Pictures/av-kit',
  hotkey: 'F2',
  copy_to_clipboard: false,
  close_to_tray: true,
  flatten_backup: true,
  backup_dir: '',
  annotated_format: 'png',
  // MEU-143 (D-744): the lock is off, so a draw returns to Select and a style commit sets the tool's style.
  tool_lock: false,
}

const ARROW_A: Annotation = { type: 'arrow', color: '#E0AF68', stroke_width: 3, from: [20, 20], to: [80, 20] }
const ARROW_B: Annotation = { type: 'arrow', color: '#E0AF68', stroke_width: 3, from: [20, 120], to: [80, 120] }
const TEXT_M: Annotation = { type: 'text', x: 20, y: 150, text: 'Hi', color: '#FFFFFF', font_size: 16, bg_color: null }
const PIXELATE_M: Annotation = { type: 'pixelate', x: 120, y: 120, width: 40, height: 40, block_size: 10 }

/** The style fields; with Select armed and nothing selected none of them shows (SELECT_NO_STYLE). */
const STYLE_FIELD_IDS = [
  'capture-color',
  'capture-color-well',
  'capture-named-color',
  'capture-stroke',
  'capture-font-size',
  'capture-text-bg',
  'capture-block-size',
]

type FetchCall = { url: string; method: string; body: unknown; response?: Record<string, unknown> }
type Outcome = 'ok' | 'fail'
type Held = { method: 'GET' | 'PUT'; release: (outcome: Outcome) => void }

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

/** jsdom gives an inline colour back as `rgb(r, g, b)`; this reads it as `#RRGGBB`. */
function cssHex(value: string): string {
  const match = /^rgb\((\d+), (\d+), (\d+)\)$/.exec(value)
  if (match === null) {
    return value.toUpperCase()
  }
  return `#${[match[1], match[2], match[3]].map((part) => Number(part).toString(16).padStart(2, '0')).join('')}`.toUpperCase()
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

describe('MEU-105 capture style and tool flow', () => {
  let user: ReturnType<typeof userEvent.setup>
  const calls: FetchCall[] = []
  const held: Held[] = []
  let savedMarks: unknown[]
  let stored: Record<string, unknown>
  let getPlan: Array<'ok' | 'hold'>
  let putPlan: Array<'ok' | 'hold' | 'fail'>

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
      const apply = (): Response => {
        stored = { ...stored, ...patch }
        return jsonResponse(stored)
      }
      const plan = putPlan.shift() ?? 'ok'
      if (plan === 'fail') {
        return serverError()
      }
      if (plan === 'hold') {
        return new Promise<Response>((resolve) => {
          held.push({ method: 'PUT', release: (outcome) => resolve(outcome === 'ok' ? apply() : serverError()) })
        })
      }
      return apply()
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
    getPlan = []
    putPlan = []
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
        return jsonResponse({ ...SHOT, annotations: savedMarks, backup_path: null })
      }
      if (/\/captures\/([^/]+)$/.test(path) && method === 'GET') {
        return jsonResponse({ ...SHOT, annotations: savedMarks, backup_path: null })
      }
      if (/\/captures\/?$/.test(path)) {
        return jsonResponse({ items: [SHOT] })
      }
      return jsonResponse({})
    })
    vi.stubGlobal('fetch', fetchMock)
    window.fetch = fetchMock as typeof window.fetch
  })

  afterEach(async () => {
    // Settle every held request, then any PUT the style queue sends after it.
    for (let round = 0; round < 10 && held.length > 0; round += 1) {
      for (const entry of held.splice(0, held.length)) {
        entry.release('ok')
      }
      await settle()
    }
    cleanup()
    queryClient.clear()
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
    if (typeof store.resetCaptureStyleStore === 'function') {
      store.resetCaptureStyleStore()
    }
  })

  /**
   * Render with `marks` saved on the shot and the settings GET answering `stored` (with `settings`
   * merged in, when given), select the shot, and wait until its overlay is ready.
   */
  async function openShot(marks: unknown[] = [], settings?: Record<string, unknown>): Promise<HTMLElement> {
    savedMarks = marks
    if (settings !== undefined) {
      stored = { ...BASE_SETTINGS, ...settings }
    }
    queryClient.setQueryData(['captures'], { items: [SHOT], pendingInteractive: false })
    mockApi()
    render(createElement(QueryClientProvider, { client: queryClient }, createElement(CapturePage)))
    await vi.waitFor(() => {
      expect(screen.queryAllByTestId('capture-filmstrip-item')).toHaveLength(1)
    })
    await user.click(screen.getAllByTestId('capture-filmstrip-item')[0] as HTMLElement)
    await vi.waitFor(() => {
      expect(screen.queryByTestId('capture-draw-surface')?.getAttribute('data-overlay-ready')).toBe('true')
    })
    await vi.waitFor(() => {
      expect(gets()).toBeGreaterThanOrEqual(1)
    })
    await settle()
    const surface = screen.getByTestId('capture-draw-surface')
    bindRect(surface, { left: 0, top: 0, width: 200, height: 200 })
    return surface
  }

  function pointer(el: HTMLElement, type: string, x: number, y: number): void {
    el.dispatchEvent(
      new PointerEvent(type, { bubbles: true, cancelable: true, clientX: x, clientY: y, pointerId: 1, pointerType: 'mouse', isPrimary: true }),
    )
  }

  async function click(el: HTMLElement, x: number, y: number): Promise<void> {
    await act(async () => {
      pointer(el, 'pointerdown', x, y)
      pointer(el, 'pointerup', x, y)
    })
  }

  async function drag(el: HTMLElement, fromX: number, fromY: number, toX: number, toY: number): Promise<void> {
    await act(async () => {
      pointer(el, 'pointerdown', fromX, fromY)
      pointer(el, 'pointermove', toX, toY)
      pointer(el, 'pointerup', toX, toY)
    })
  }

  function present(id: string): HTMLInputElement {
    const el = screen.queryByTestId(id)
    expect(el, id).not.toBeNull()
    return el as HTMLInputElement
  }

  async function chooseTool(tool: string): Promise<void> {
    await user.click(present(`capture-tool-${tool}`))
  }

  /** Select the mark whose content is `mark` with the Select tool, at its body point. */
  async function selectMark(surface: HTMLElement, mark: Annotation): Promise<void> {
    await chooseTool('select')
    const point = bodyHandleImagePoint(mark)
    await click(surface, Math.round(point.x), Math.round(point.y))
    const pressed = present('capture-mark-list').querySelectorAll('button[aria-pressed="true"]')
    expect(pressed.length, 'one mark is selected').toBe(1)
  }

  function arrowAt(x: number, y: number): Element | null {
    return document.querySelector(`[data-annotation-type="arrow"][x1="${x}"][y1="${y}"]`)
  }

  function arrowColor(x: number, y: number): string | undefined {
    return arrowAt(x, y)?.getAttribute('stroke')?.toUpperCase()
  }

  function arrowWidth(x: number, y: number): string | null | undefined {
    return arrowAt(x, y)?.querySelector('line')?.getAttribute('stroke-width')
  }

  function textMark(text: string): Element | undefined {
    return Array.from(document.querySelectorAll('[data-annotation-type="text"]')).find((el) => el.textContent === text)
  }

  function plate(): Element | null {
    return document.querySelector('[data-testid="capture-text-bg-plate"]')
  }

  function hexValue(): string {
    return present('capture-color').value.toUpperCase()
  }

  function undoOn(): boolean {
    return !present('capture-undo').disabled
  }

  async function undo(): Promise<void> {
    await user.click(present('capture-undo'))
  }

  /** Type `text` into the hex field and press Enter. */
  async function commitHex(text: string): Promise<void> {
    const hex = present('capture-color')
    await user.clear(hex)
    await user.type(hex, text)
    await user.keyboard('{Enter}')
  }

  /** Put `text` in the hex field as one change, the field focused (for text user-event can't type). */
  function setHexText(text: string): HTMLInputElement {
    const hex = present('capture-color')
    act(() => {
      hex.focus()
    })
    fireEvent.change(hex, { target: { value: text } })
    return hex
  }

  function wellInput(id: string, value: string): void {
    fireEvent.input(present(id), { target: { value } })
  }

  function wellChange(id: string, value: string): void {
    fireEvent.change(present(id), { target: { value } })
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

  /** One scrub gesture: a 2 px move is one step. */
  function scrub(id: string, fromX: number, toX: number): void {
    const handle = present(`${id}-scrub`)
    scrubPointer(handle, 'pointerdown', fromX)
    scrubPointer(handle, 'pointermove', toX)
    scrubPointer(handle, 'pointerup', toX)
  }

  function escapeNow(): void {
    act(() => {
      ;(document.activeElement ?? document.body).dispatchEvent(
        new KeyboardEvent('keydown', { key: 'Escape', bubbles: true, cancelable: true }),
      )
    })
  }

  async function historyKey(surface: HTMLElement, key: 'z' | 'y'): Promise<void> {
    await act(async () => {
      surface.focus()
    })
    await act(async () => {
      surface.dispatchEvent(new KeyboardEvent('keydown', { key, ctrlKey: true, bubbles: true, cancelable: true }))
    })
  }

  function puts(): Array<Record<string, unknown>> {
    return calls
      .filter((call) => call.method === 'PUT' && call.url.includes('/settings/capture'))
      .map((call) => (call.body ?? {}) as Record<string, unknown>)
  }

  function gets(): number {
    return calls.filter((call) => call.method === 'GET' && call.url.includes('/settings/capture')).length
  }

  function annotatePosts(): Array<{ annotations: Array<Record<string, unknown>> }> {
    return calls
      .filter((call) => call.method === 'POST' && call.url.endsWith('/annotate'))
      .map((call) => call.body as { annotations: Array<Record<string, unknown>> })
  }

  /** Save, and return the marks of the one save POST. */
  async function saveMarks(): Promise<Array<Record<string, unknown>>> {
    const before = annotatePosts().length
    const save = present('capture-save')
    expect(save.disabled, 'Save is on').toBe(false)
    await user.click(save)
    await vi.waitFor(() => {
      expect(annotatePosts()).toHaveLength(before + 1)
    })
    return annotatePosts()[before]?.annotations ?? []
  }

  async function release(method: 'GET' | 'PUT', outcome: Outcome = 'ok'): Promise<void> {
    const index = held.findIndex((entry) => entry.method === method)
    expect(index, `a held ${method}`).toBeGreaterThanOrEqual(0)
    const [entry] = held.splice(index, 1)
    entry?.release(outcome)
    await settle()
  }

  it('AC-105.8 a named pick paints the selected arrow at once as one undo step; the menu shows Named again', async () => {
    const surface = await openShot([ARROW_A])
    await selectMark(surface, ARROW_A)
    present('capture-color-well')
    expect(screen.queryByTestId('capture-color-apply')).toBeNull()
    expect(screen.queryByTestId('capture-color-cancel')).toBeNull()
    await user.selectOptions(present('capture-named-color'), 'orange')
    expect(arrowColor(20, 20)).toBe('#FFA500')
    expect((present('capture-named-color') as unknown as HTMLSelectElement).value).toBe('')
    expect(undoOn()).toBe(true)
    await historyKey(surface, 'z')
    expect(arrowColor(20, 20)).toBe('#E0AF68')
    expect(undoOn(), 'one step').toBe(false)
  })

  it('AC-105.9 the hex field paints the selected arrow on Enter or blur, one step each; refused text paints nothing', async () => {
    const surface = await openShot([ARROW_A])
    await selectMark(surface, ARROW_A)
    const hex = present('capture-color')
    await user.clear(hex)
    await user.type(hex, '#12abcd')
    expect(arrowColor(20, 20)).toBe('#E0AF68')
    await user.keyboard('{Enter}')
    expect(arrowColor(20, 20)).toBe('#12ABCD')
    expect(undoOn()).toBe(true)
    await undo()
    expect(arrowColor(20, 20)).toBe('#E0AF68')
    expect(undoOn(), 'Enter is one step').toBe(false)
    await selectMark(surface, ARROW_A)
    const again = present('capture-color')
    await user.clear(again)
    await user.type(again, '#00ff00')
    expect(arrowColor(20, 20)).toBe('#E0AF68')
    await user.tab()
    expect(arrowColor(20, 20)).toBe('#00FF00')
    await selectMark(surface, ARROW_A)
    for (const text of ['#12abc', '', '#12AB\uD800', '#12AB\u0007D']) {
      const label = JSON.stringify(text)
      setHexText(text)
      await user.keyboard('{Enter}')
      expect(arrowColor(20, 20), label).toBe('#00FF00')
      expect(present('capture-save').disabled, `${label} Save`).toBe(false)
      setHexText(text)
      await user.tab()
      expect(arrowColor(20, 20), label).toBe('#00FF00')
      expect(hexValue(), `${label} blur`).toBe('#00FF00')
      setHexText(text)
      escapeNow()
      expect(hexValue(), `${label} Escape`).toBe('#00FF00')
    }
    await chooseTool('box')
    expect(present('capture-tool-box').getAttribute('aria-pressed')).toBe('true')
  })

  it('AC-105.10 the colour well previews on input with no step, and its change is exactly one step', async () => {
    const surface = await openShot([ARROW_A])
    await selectMark(surface, ARROW_A)
    wellInput('capture-color-well', '#111111')
    expect(arrowColor(20, 20)).toBe('#111111')
    wellInput('capture-color-well', '#222222')
    expect(arrowColor(20, 20)).toBe('#222222')
    wellInput('capture-color-well', '#333333')
    expect(arrowColor(20, 20)).toBe('#333333')
    expect(undoOn(), 'previews add no step').toBe(false)
    wellChange('capture-color-well', '#333333')
    expect(arrowColor(20, 20)).toBe('#333333')
    expect(undoOn()).toBe(true)
    await undo()
    expect(arrowColor(20, 20)).toBe('#E0AF68')
    expect(undoOn(), 'one step').toBe(false)
  })

  it("AC-105.10 negative: a well change equal to the mark's colour adds no step", async () => {
    const surface = await openShot([ARROW_A])
    await selectMark(surface, ARROW_A)
    wellChange('capture-color-well', '#e0af68')
    expect(arrowColor(20, 20)).toBe('#E0AF68')
    expect(undoOn()).toBe(false)
  })

  it('AC-105.11 the text Bg well is one step for three inputs and a change, and Clear is one more', async () => {
    const surface = await openShot([TEXT_M])
    await selectMark(surface, TEXT_M)
    wellInput('capture-text-bg', '#111111')
    wellInput('capture-text-bg', '#222222')
    wellInput('capture-text-bg', '#333333')
    wellChange('capture-text-bg', '#333333')
    expect(plate()?.getAttribute('fill')?.toUpperCase()).toBe('#333333')
    expect(undoOn()).toBe(true)
    await undo()
    expect(plate(), 'one undo removes the background').toBeNull()
    expect(undoOn(), 'one step').toBe(false)
    await selectMark(surface, TEXT_M)
    wellChange('capture-text-bg', '#444444')
    expect(plate()?.getAttribute('fill')?.toUpperCase()).toBe('#444444')
    await user.click(present('capture-text-bg-clear'))
    expect(plate()).toBeNull()
    await undo()
    expect(plate()?.getAttribute('fill')?.toUpperCase()).toBe('#444444')
    await undo()
    expect(plate()).toBeNull()
    expect(undoOn(), 'Clear is one step').toBe(false)
  })

  it('AC-105.12 with one of two arrows selected, a colour and a stroke commit restyle only it and send no PUT', async () => {
    const surface = await openShot([ARROW_A, ARROW_B])
    await selectMark(surface, ARROW_A)
    await commitHex('#12abcd')
    expect(arrowColor(20, 20)).toBe('#12ABCD')
    expect(arrowColor(20, 120), 'the other arrow').toBe('#E0AF68')
    scrub('capture-stroke', 100, 110)
    expect(arrowWidth(20, 20)).toBe('8')
    expect(arrowWidth(20, 120), 'the other arrow').toBe('3')
    await settle()
    expect(puts()).toHaveLength(0)
    await chooseTool('arrow')
    await drag(surface, 30, 60, 90, 60)
    expect(arrowColor(30, 60), 'the arrow tool keeps its style').toBe('#E0AF68')
    expect(arrowWidth(30, 60)).toBe('3')
  })

  it('AC-105.13 with Arrow armed and nothing selected, a hex commit and a Stroke drag each send one PUT and no step', async () => {
    await openShot([ARROW_A])
    await chooseTool('arrow')
    await commitHex('#12abcd')
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(1)
    })
    expect(puts()[0]).toEqual({ arrow_color: '#12ABCD' })
    expect(hexValue()).toBe('#12ABCD')
    expect(arrowColor(20, 20), 'no mark changes').toBe('#E0AF68')
    expect(undoOn()).toBe(false)
    const handle = present('capture-stroke-scrub')
    scrubPointer(handle, 'pointerdown', 100)
    scrubPointer(handle, 'pointermove', 110)
    scrubPointer(handle, 'pointermove', 120)
    await settle()
    expect(puts(), 'the previews send no PUT').toHaveLength(1)
    scrubPointer(handle, 'pointerup', 120)
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(2)
    })
    expect(puts()[1]).toEqual({ arrow_stroke: 13 })
    expect(present('capture-stroke').value).toBe('13')
    expect(undoOn()).toBe(false)
    await chooseTool('box')
    expect(hexValue()).toBe('#E0AF68')
    expect(present('capture-stroke').value).toBe('3')
    await chooseTool('highlight')
    expect(hexValue()).toBe('#E0AF68')
    await chooseTool('text')
    expect(hexValue()).toBe('#E0AF68')
    expect(present('capture-font-size').value).toBe('16')
    await chooseTool('redact')
    await user.click(present('capture-redact-pixelate'))
    expect(present('capture-block-size').value).toBe('10')
    expect(puts()).toHaveLength(2)
  })

  it('AC-105.14 each of Arrow, Box, Highlight, Text and Pixelate draws with its own style and none of the others', async () => {
    const surface = await openShot([])
    await chooseTool('arrow')
    await commitHex('#111111')
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(1)
    })
    await chooseTool('box')
    await commitHex('#222222')
    await chooseTool('highlight')
    await commitHex('#333333')
    await chooseTool('text')
    await commitHex('#444444')
    await chooseTool('redact')
    await user.click(present('capture-redact-pixelate'))
    scrub('capture-block-size', 100, 110)
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(5)
    })
    await chooseTool('arrow')
    await drag(surface, 20, 20, 80, 20)
    expect(arrowColor(20, 20)).toBe('#111111')
    await chooseTool('box')
    await drag(surface, 30, 100, 80, 130)
    expect(document.querySelector('[data-annotation-type="rect"][x="30"][y="100"]')?.getAttribute('stroke')?.toUpperCase()).toBe(
      '#222222',
    )
    await chooseTool('highlight')
    await drag(surface, 100, 20, 150, 50)
    expect(
      document.querySelector('[data-annotation-type="highlight"][x="100"][y="20"]')?.getAttribute('fill')?.toUpperCase(),
    ).toBe('#333333')
    await chooseTool('text')
    await click(surface, 20, 170)
    await user.type(present('capture-text-draft'), 'Hi{Enter}')
    expect(textMark('Hi')?.getAttribute('fill')?.toUpperCase()).toBe('#444444')
    await chooseTool('redact')
    await drag(surface, 120, 120, 160, 160)
    const marks = await saveMarks()
    expect(marks).toHaveLength(5)
    const byType = (type: string) => marks.filter((mark) => mark.type === type)
    expect(byType('arrow').map((mark) => String(mark.color).toUpperCase())).toEqual(['#111111'])
    expect(byType('rect').map((mark) => String(mark.color).toUpperCase())).toEqual(['#222222'])
    expect(byType('highlight').map((mark) => String(mark.color).toUpperCase())).toEqual(['#333333'])
    expect(byType('text').map((mark) => String(mark.color).toUpperCase())).toEqual(['#444444'])
    expect(byType('pixelate').map((mark) => mark.block_size)).toEqual([15])
  })

  it("AC-105.15 the fields show each armed tool's style, a selected mark's values, then the tool's again", async () => {
    const surface = await openShot([ARROW_A], {
      arrow_color: '#111111',
      arrow_stroke: 4,
      box_color: '#222222',
      box_stroke: 6,
      text_color: '#333333',
      text_font_size: 20,
    })
    await chooseTool('arrow')
    expect(hexValue()).toBe('#111111')
    expect(present('capture-stroke').value).toBe('4')
    await chooseTool('box')
    expect(hexValue()).toBe('#222222')
    expect(present('capture-stroke').value).toBe('6')
    await chooseTool('text')
    expect(hexValue()).toBe('#333333')
    expect(present('capture-font-size').value).toBe('20')
    await selectMark(surface, ARROW_A)
    expect(hexValue()).toBe('#E0AF68')
    expect(present('capture-stroke').value).toBe('3')
    await chooseTool('box')
    expect(hexValue()).toBe('#222222')
    expect(present('capture-stroke').value).toBe('6')
  })

  it('AC-105.16 a page mounted on a stored arrow style shows it and draws an arrow with it', async () => {
    const surface = await openShot([], { arrow_color: '#123456', arrow_stroke: 7 })
    await chooseTool('arrow')
    expect(hexValue()).toBe('#123456')
    expect(present('capture-stroke').value).toBe('7')
    await drag(surface, 30, 60, 90, 60)
    expect(arrowColor(30, 60)).toBe('#123456')
    expect(arrowWidth(30, 60)).toBe('7')
    const marks = await saveMarks()
    expect(marks).toHaveLength(1)
    expect(marks[0]).toMatchObject({ type: 'arrow', stroke_width: 7 })
    expect(String(marks[0]?.color).toUpperCase()).toBe('#123456')
  })

  it("AC-105.16 negative: a stored arrow_color of 'nope' shows the default, and the valid stroke is kept", async () => {
    await openShot([], { arrow_color: 'nope', arrow_stroke: 7 })
    await chooseTool('arrow')
    expect(hexValue()).toBe('#E0AF68')
    expect(present('capture-stroke').value).toBe('7')
  })

  it('AC-105.17 a colour commit in a new draft sets the text style; in a re-edit it restyles that mark with no PUT', async () => {
    const surface = await openShot([TEXT_M])
    await chooseTool('text')
    await click(surface, 30, 40)
    present('capture-text-draft')
    await commitHex('#12abcd')
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(1)
    })
    expect(puts()[0]).toEqual({ text_color: '#12ABCD' })
    const draft = present('capture-text-draft')
    expect(cssHex(draft.style.color), 'the draft shows the colour').toBe('#12ABCD')
    await user.type(draft, 'Yo{Enter}')
    expect(textMark('Yo')?.getAttribute('fill')?.toUpperCase()).toBe('#12ABCD')
    expect(screen.queryByTestId('capture-text-draft')).toBeNull()
    await chooseTool('select')
    const point = bodyHandleImagePoint(TEXT_M)
    await act(async () => {
      surface.dispatchEvent(
        new MouseEvent('dblclick', { bubbles: true, cancelable: true, clientX: point.x, clientY: point.y, detail: 2 }),
      )
    })
    present('capture-text-draft')
    await commitHex('#00ff00')
    await user.type(present('capture-text-draft'), '{Enter}')
    expect(textMark('Hi')?.getAttribute('fill')?.toUpperCase()).toBe('#00FF00')
    await settle()
    expect(puts(), 'the re-edit sends no PUT').toHaveLength(1)
    await undo()
    expect(textMark('Hi')?.getAttribute('fill')?.toUpperCase(), 'one step').toBe('#FFFFFF')
    expect(textMark('Yo')).toBeDefined()
  })

  it('AC-105.17 a Bg commit and Clear show on a new draft and on a re-edit draft', async () => {
    const surface = await openShot([TEXT_M])
    await chooseTool('text')
    await click(surface, 30, 40)
    present('capture-text-draft')
    wellChange('capture-text-bg', '#112233')
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(1)
    })
    expect(puts()[0]).toEqual({ text_bg_color: '#112233' })
    expect(cssHex(present('capture-text-draft').style.backgroundColor), 'the new draft shows the Bg').toBe('#112233')
    await user.click(present('capture-text-bg-clear'))
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(2)
    })
    expect(puts()[1]).toEqual({ text_bg_color: '' })
    expect(present('capture-text-draft').style.backgroundColor, 'Clear shows no Bg on the new draft').toBe('')
    await user.type(present('capture-text-draft'), 'Yo{Enter}')
    expect(textMark('Yo')).toBeDefined()
    await chooseTool('select')
    const point = bodyHandleImagePoint(TEXT_M)
    await act(async () => {
      surface.dispatchEvent(
        new MouseEvent('dblclick', { bubbles: true, cancelable: true, clientX: point.x, clientY: point.y, detail: 2 }),
      )
    })
    expect(present('capture-text-draft').style.backgroundColor, 'the re-edit starts with no Bg').toBe('')
    wellChange('capture-text-bg', '#445566')
    expect(cssHex(present('capture-text-draft').style.backgroundColor), 'the re-edit draft shows the Bg').toBe('#445566')
    await user.click(present('capture-text-bg-clear'))
    expect(present('capture-text-draft').style.backgroundColor, 'Clear shows no Bg on the re-edit').toBe('')
    await settle()
    expect(puts(), 'the re-edit sends no PUT').toHaveLength(2)
  })

  it('AC-105.18 the Block size scrub is one step on a selected pixelate, clamps to 2 and 100, and Escape restores', async () => {
    const surface = await openShot([PIXELATE_M])
    await selectMark(surface, PIXELATE_M)
    const handle = present('capture-block-size-scrub')
    expect(handle.closest('[role="group"]')?.contains(present('capture-block-size'))).toBe(true)
    scrubPointer(handle, 'pointerdown', 100)
    scrubPointer(handle, 'pointermove', 120)
    expect(present('capture-block-size').value).toBe('20')
    escapeNow()
    scrubPointer(handle, 'pointerup', 120)
    expect(present('capture-block-size').value).toBe('10')
    expect(undoOn(), 'Escape adds no step').toBe(false)
    scrub('capture-block-size', 100, 0)
    expect(present('capture-block-size').value, 'the clamp at 2').toBe('2')
    expect(undoOn()).toBe(true)
    await undo()
    expect(undoOn(), 'one step').toBe(false)
    await selectMark(surface, PIXELATE_M)
    expect(present('capture-block-size').value).toBe('10')
    scrub('capture-block-size', 100, 400)
    expect(present('capture-block-size').value, 'the clamp at 100').toBe('100')
    const marks = await saveMarks()
    expect(marks).toHaveLength(1)
    expect(marks[0]?.block_size).toBe(100)
    await settle()
    expect(puts(), 'a mark scrub sends no PUT').toHaveLength(0)
  })

  it('AC-105.18 with Redact in Pixelate mode and nothing selected, one Block size drag sends one PUT', async () => {
    await openShot([])
    await chooseTool('redact')
    await user.click(present('capture-redact-pixelate'))
    scrub('capture-block-size', 100, 110)
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(1)
    })
    expect(puts()[0]).toEqual({ pixelate_block_size: 15 })
    expect(present('capture-block-size').value).toBe('15')
  })

  it('AC-105.19 with Select armed and nothing selected the page shows no style field; a selected arrow shows them', async () => {
    const surface = await openShot([ARROW_A])
    await chooseTool('select')
    for (const id of STYLE_FIELD_IDS) {
      expect(screen.queryByTestId(id), id).toBeNull()
    }
    await selectMark(surface, ARROW_A)
    present('capture-color')
    present('capture-stroke')
  })

  it('AC-105.20 a named pick reaches the save POST body: the arrow is #FFA500 and appears once', async () => {
    const surface = await openShot([ARROW_A])
    await selectMark(surface, ARROW_A)
    await user.selectOptions(present('capture-named-color'), 'orange')
    expect(arrowColor(20, 20)).toBe('#FFA500')
    const marks = await saveMarks()
    const arrows = marks.filter((mark) => mark.type === 'arrow')
    expect(arrows).toHaveLength(1)
    expect(marks).toHaveLength(1)
    expect(String(arrows[0]?.color).toUpperCase()).toBe('#FFA500')
    expect(arrows[0]).toMatchObject({ from: [20, 20], to: [80, 20], stroke_width: 3 })
  })

  it('AC-105.21 a hex commit with Arrow armed sends the PUT body {"arrow_color":"#12ABCD"} once, and the next arrow has it', async () => {
    const surface = await openShot([])
    await chooseTool('arrow')
    await commitHex('#12abcd')
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(1)
    })
    const raw = calls.find((call) => call.method === 'PUT' && call.url.includes('/settings/capture'))
    expect(JSON.stringify(raw?.body)).toBe('{"arrow_color":"#12ABCD"}')
    await drag(surface, 30, 60, 90, 60)
    expect(arrowColor(30, 60)).toBe('#12ABCD')
    const marks = await saveMarks()
    expect(marks).toHaveLength(1)
    expect(String(marks[0]?.color).toUpperCase()).toBe('#12ABCD')
    expect(puts(), 'exactly one PUT').toHaveLength(1)
  })

  it("AC-105.23 a style PUT keeps the Capture card's unsaved edit, whose Save sends only inbox_dir", async () => {
    await openShot([])
    await user.click(present('capture-settings-toggle'))
    const inbox = present('capture-inbox-path')
    await user.clear(inbox)
    await user.type(inbox, 'C:/Pictures/inbox-9')
    await chooseTool('arrow')
    await commitHex('#12abcd')
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(1)
    })
    await settle()
    expect(present('capture-inbox-path').value, 'the unsaved edit stays').toBe('C:/Pictures/inbox-9')
    const getsBefore = gets()
    await user.click(present('capture-page-save'))
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(2)
    })
    const card = puts()[1] ?? {}
    expect(Object.keys(card).sort()).toEqual(CARD_KEYS)
    expect(card.inbox_dir).toBe('C:/Pictures/inbox-9')
    await vi.waitFor(() => {
      expect(gets()).toBeGreaterThan(getsBefore)
    })
    const after = calls.filter((call) => call.method === 'GET' && call.url.includes('/settings/capture')).at(-1)
    expect(after?.response?.arrow_color).toBe('#12ABCD')
    await settle()
    expect(hexValue()).toBe('#12ABCD')
  })

  it("AC-105.31 a failed style PUT shows Couldn't save the tool style, names no value, and refetches the stored style", async () => {
    const logged = (['error', 'warn', 'log', 'info', 'debug'] as const).map((level) =>
      vi.spyOn(console, level).mockImplementation(() => undefined),
    )
    await openShot([])
    await chooseTool('arrow')
    putPlan = ['fail']
    const getsBefore = gets()
    await commitHex('#12abcd')
    await vi.waitFor(() => {
      expect(present('capture-status').textContent ?? '').toContain("Couldn't save the tool style")
    })
    expect((present('capture-status').textContent ?? '').toUpperCase()).not.toContain('12ABCD')
    await vi.waitFor(() => {
      expect(gets()).toBe(getsBefore + 1)
    })
    await settle()
    expect(hexValue(), 'the fields show the stored style again').toBe('#E0AF68')
    const consoleText = logged
      .flatMap((spy) => spy.mock.calls)
      .map((args) => args.map((arg) => (typeof arg === 'string' ? arg : String(arg))).join(' '))
      .join('\n')
      .toUpperCase()
    expect(consoleText).not.toContain('12ABCD')
  })

  it('AC-105.32 two commits while the first PUT is held: the second PUT waits, the bodies keep order, the second colour stays', async () => {
    await openShot([])
    await chooseTool('arrow')
    putPlan = ['hold']
    await commitHex('#111111')
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(1)
    })
    await commitHex('#222222')
    await settle()
    expect(puts(), 'the second PUT waits for the first').toHaveLength(1)
    expect(hexValue()).toBe('#222222')
    await release('PUT')
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(2)
    })
    await settle()
    expect(puts()).toEqual([{ arrow_color: '#111111' }, { arrow_color: '#222222' }])
    expect(hexValue()).toBe('#222222')
    expect(stored.arrow_color).toBe('#222222')
    cleanup()
    queryClient.clear()
    expect(typeof store.resetCaptureStyleStore).toBe('function')
    store.resetCaptureStyleStore()
    await openShot([])
    await chooseTool('arrow')
    expect(hexValue(), 'a remounted page').toBe('#222222')
  })

  it('AC-105.32 the first PUT fails while the second is held: no GET until the second settles, then exactly one', async () => {
    await openShot([])
    await chooseTool('arrow')
    putPlan = ['hold', 'hold']
    await commitHex('#111111')
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(1)
    })
    await commitHex('#222222')
    const getsBefore = gets()
    await release('PUT', 'fail')
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(2)
    })
    await settle()
    expect(gets(), 'no GET while a PUT is queued').toBe(getsBefore)
    expect(hexValue()).toBe('#222222')
    await release('PUT', 'ok')
    await vi.waitFor(() => {
      expect(gets()).toBe(getsBefore + 1)
    })
    await settle()
    expect(gets(), 'exactly one GET').toBe(getsBefore + 1)
    expect(hexValue()).toBe('#222222')
  })

  it('AC-105.32 a failed PUT, a held GET, a second commit: the old GET answer leaves the second colour', async () => {
    const surface = await openShot([])
    await chooseTool('arrow')
    putPlan = ['fail', 'hold']
    getPlan = ['hold']
    const getsBefore = gets()
    await commitHex('#111111')
    await vi.waitFor(() => {
      expect(gets()).toBe(getsBefore + 1)
    })
    await commitHex('#222222')
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(2)
    })
    await release('GET')
    expect(hexValue(), 'the old GET answer').toBe('#222222')
    await release('PUT', 'ok')
    expect(hexValue()).toBe('#222222')
    await drag(surface, 30, 60, 90, 60)
    expect(arrowColor(30, 60)).toBe('#222222')
    await act(async () => {
      await queryClient.invalidateQueries({ queryKey: CAPTURE_SETTINGS_KEY })
    })
    await settle()
    expect(stored.arrow_color).toBe('#222222')
    await chooseTool('arrow')
    expect(hexValue(), 'a later GET').toBe('#222222')
  })

  it('AC-105.32 a refetch started while a PUT is held answers the old colour and leaves the new one', async () => {
    await openShot([])
    await chooseTool('arrow')
    putPlan = ['hold']
    await commitHex('#111111')
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(1)
    })
    const getsBefore = gets()
    await act(async () => {
      await queryClient.invalidateQueries({ queryKey: CAPTURE_SETTINGS_KEY })
    })
    await vi.waitFor(() => {
      expect(gets()).toBe(getsBefore + 1)
    })
    await settle()
    expect(hexValue(), 'before the PUT succeeds').toBe('#111111')
    await release('PUT', 'ok')
    expect(hexValue(), 'after the PUT succeeds').toBe('#111111')
  })

  it('AC-105.32 a commit while the first settings GET is held draws the next arrow with it', async () => {
    getPlan = ['hold']
    const surface = await openShot([])
    await chooseTool('arrow')
    await commitHex('#12abcd')
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(1)
    })
    expect(puts()[0]).toEqual({ arrow_color: '#12ABCD' })
    await settle()
    expect(hexValue(), 'the field keeps the committed colour').toBe('#12ABCD')
    await drag(surface, 30, 60, 90, 60)
    expect(arrowColor(30, 60), 'before the GET answers').toBe('#12ABCD')
    await release('GET')
    await chooseTool('arrow')
    expect(hexValue(), 'the old GET answer').toBe('#12ABCD')
    await drag(surface, 30, 100, 90, 100)
    expect(arrowColor(30, 100), 'after the GET answers').toBe('#12ABCD')
    expect(puts(), 'exactly one PUT').toHaveLength(1)
  })

  it('AC-105.32 a commit after the first settings GET fails draws the next arrow with it', async () => {
    getPlan = ['hold']
    const surface = await openShot([])
    await release('GET', 'fail')
    await chooseTool('arrow')
    await commitHex('#12abcd')
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(1)
    })
    await settle()
    expect(hexValue()).toBe('#12ABCD')
    await drag(surface, 30, 60, 90, 60)
    expect(arrowColor(30, 60), 'with no settings loaded').toBe('#12ABCD')
  })

  it('AC-105.27 the Redact mode is not saved; a solid redact and an eraser draw as today; the crop shows no style group', async () => {
    const surface = await openShot([])
    await chooseTool('redact')
    await user.click(present('capture-redact-pixelate'))
    await user.click(present('capture-redact-solid'))
    await drag(surface, 30, 30, 70, 70)
    await chooseTool('eraser')
    await drag(surface, 100, 100, 140, 140)
    const marks = await saveMarks()
    expect(marks).toEqual([
      { type: 'redact', x: 30, y: 30, width: 40, height: 40, color: '#000000' },
      { type: 'eraser', x: 100, y: 100, width: 40, height: 40 },
    ])
    await chooseTool('crop')
    for (const id of [...STYLE_FIELD_IDS, 'capture-redact-mode']) {
      expect(screen.queryByTestId(id), `crop ${id}`).toBeNull()
    }
    await settle()
    expect(puts()).toHaveLength(0)
  })

  it('AC-105.28 the Stroke and Size scrubs stay one step per gesture, Escape restores, and Ctrl+Z / Ctrl+Y work', async () => {
    const surface = await openShot([ARROW_A, TEXT_M])
    await selectMark(surface, ARROW_A)
    scrub('capture-stroke', 100, 110)
    expect(arrowWidth(20, 20)).toBe('8')
    await historyKey(surface, 'z')
    expect(arrowWidth(20, 20)).toBe('3')
    expect(undoOn(), 'one step').toBe(false)
    await historyKey(surface, 'y')
    expect(arrowWidth(20, 20)).toBe('8')
    await selectMark(surface, ARROW_A)
    const handle = present('capture-stroke-scrub')
    scrubPointer(handle, 'pointerdown', 100)
    scrubPointer(handle, 'pointermove', 120)
    expect(present('capture-stroke').value).toBe('18')
    escapeNow()
    scrubPointer(handle, 'pointerup', 120)
    expect(arrowWidth(20, 20)).toBe('8')
    expect(present('capture-stroke').value).toBe('8')
    await selectMark(surface, TEXT_M)
    scrub('capture-font-size', 100, 110)
    expect(textMark('Hi')?.getAttribute('font-size')).toBe('21')
    await undo()
    expect(textMark('Hi')?.getAttribute('font-size')).toBe('16')
  })

  it("AC-105.30 after a style commit on a selected arrow the save POST holds exactly today's arrow keys", async () => {
    const surface = await openShot([ARROW_A])
    await selectMark(surface, ARROW_A)
    scrub('capture-stroke', 100, 110)
    const marks = await saveMarks()
    expect(marks).toHaveLength(1)
    expect(Object.keys(marks[0] ?? {}).sort()).toEqual(['color', 'from', 'stroke_width', 'to', 'type'])
    expect(marks[0]).toMatchObject({ stroke_width: 8 })
  })
})
