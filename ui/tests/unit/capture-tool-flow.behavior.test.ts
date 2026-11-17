/** @vitest-environment jsdom */

import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { act, cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClientProvider } from '@tanstack/react-query'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { CommandPalette } from '../../src/renderer/src/components/CommandPalette'
import type { Annotation } from '../../src/renderer/src/features/capture/capture-annotate'
import { bodyHandleImagePoint } from '../../src/renderer/src/features/capture/capture-hit-test'
import * as store from '../../src/renderer/src/features/capture/capture-style-store'
import { CAPTURE_EVENTS } from '../../src/renderer/src/features/capture/capture-commands'
import { CapturePage } from '../../src/renderer/src/features/capture/CapturePage'
import { CAPTURE_SETTINGS_KEY } from '../../src/renderer/src/features/capture/useCaptureSettings'
import { HELP_EVENTS } from '../../src/renderer/src/features/settings/settings-commands'
import { captureLockPutSchema } from '../../src/renderer/src/features/settings/settings-schemas'
import { queryClient } from '../../src/renderer/src/lib/query-client'
import { clearCommandState, getCommandState, type CommandState } from '../../src/renderer/src/registry/command-state'
import { listCommands } from '../../src/renderer/src/registry/commandRegistry'
import { createShortcutHandler } from '../../src/renderer/src/registry/shortcuts'

// Session 71b (MEU-143): the tool lock, the tool letters and the draw modifiers on the real CapturePage
// with the app's query client. A recording fake server answers GET and PUT /settings/capture (a GET can
// be held or fail, a PUT can be held or fail) and the save POST. The registry handler is mounted on the
// window through createShortcutHandler with the real listCommands(), as AppShell mounts it, with a
// recording getState. The harness is modelled on capture-style-flow.behavior.test.ts. The default shot is
// 100x80 on a 100x80 surface, so one screen px is one image px. Every element that appears only after
// Green is looked up with queryBy and asserted present, so a Red fails by assertion.

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

const UI = resolve(dirname(fileURLToPath(import.meta.url)), '../..')

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
const SQUARE = makeShot('square', 200, 200)
const LAND = makeShot('land', 400, 200)

const PNG_BYTES = Uint8Array.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0, 0, 0, 13, 0x49, 0x48, 0x44, 0x52])

/** The Capture card's Save body after an inbox-only edit: only the changed leaf (CAPTURE_SAVE_CHANGED_ONLY, D-966; D-1066). */
const CARD_KEYS = ['inbox_dir']

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

/** Each style tool's saved colour set to a different value (AC-143.16). */
const STYLE_COLOURS: Record<string, unknown> = {
  arrow_color: '#111111',
  box_color: '#222222',
  highlight_color: '#333333',
  text_color: '#444444',
}

const STYLE_FIELD_IDS = [
  'capture-color',
  'capture-color-well',
  'capture-named-color',
  'capture-stroke',
  'capture-font-size',
  'capture-text-bg',
  'capture-block-size',
]

/** What the options row and the crop show; a letter must give what a click gives (AC-143.16). */
const OPTION_IDS = [...STYLE_FIELD_IDS, 'capture-redact-solid', 'capture-redact-pixelate', 'capture-crop-bar']

const TOOLS = ['select', 'arrow', 'box', 'highlight', 'text', 'redact', 'eraser'] as const
type Tool = (typeof TOOLS)[number]

const LETTER_CASES: Array<{ letter: string; tool: Tool | 'crop'; colour?: string; mark?: 'arrow' | 'rect' | 'highlight' }> = [
  { letter: 'v', tool: 'select' },
  { letter: 'a', tool: 'arrow', colour: '#111111', mark: 'arrow' },
  { letter: 'r', tool: 'box', colour: '#222222', mark: 'rect' },
  { letter: 'h', tool: 'highlight', colour: '#333333', mark: 'highlight' },
  { letter: 't', tool: 'text', colour: '#444444' },
  { letter: 'x', tool: 'redact' },
  { letter: 'e', tool: 'eraser' },
  { letter: 'c', tool: 'crop' },
]

/** The hint each tool button shows, its letter and its bare accessible name (AC-143.17). */
const HINT_CASES: Array<{ id: string; letter: string; name: string; hint: string }> = [
  { id: 'capture-tool-select', letter: 'V', name: 'Select', hint: 'Select (V)' },
  { id: 'capture-tool-arrow', letter: 'A', name: 'Arrow', hint: 'Arrow (A)' },
  { id: 'capture-tool-box', letter: 'R', name: 'Box', hint: 'Box (R)' },
  { id: 'capture-tool-highlight', letter: 'H', name: 'Highlight', hint: 'Highlight (H)' },
  { id: 'capture-tool-text', letter: 'T', name: 'Text', hint: 'Text (T)' },
  { id: 'capture-tool-redact', letter: 'X', name: 'Redact', hint: 'Redact (X)' },
  {
    id: 'capture-tool-eraser',
    letter: 'E',
    name: 'Smart eraser',
    hint: 'Smart eraser (E): Covers an area with the surrounding colour',
  },
  { id: 'capture-tool-crop', letter: 'C', name: 'Crop', hint: 'Crop (C)' },
]

/** The bounded tools, one parametrize id each (AC-143.23, AC-143.26). */
const BOUNDED: Array<{ name: string; tool: Tool; mode?: 'solid' | 'pixelate'; type: string }> = [
  { name: 'Box', tool: 'box', type: 'rect' },
  { name: 'Highlight', tool: 'highlight', type: 'highlight' },
  { name: 'Redact Solid', tool: 'redact', mode: 'solid', type: 'redact' },
  { name: 'Redact Pixelate', tool: 'redact', mode: 'pixelate', type: 'pixelate' },
  { name: 'Smart eraser', tool: 'eraser', type: 'eraser' },
]

const TYPED = 'varhtxecVARHTXEC'

const RECT_A: Annotation = { type: 'rect', x: 10, y: 10, width: 40, height: 20, color: '#FF0000', stroke_width: 2 }
const RECT_C: Annotation = { type: 'rect', x: 60, y: 40, width: 30, height: 30, color: '#FF0000', stroke_width: 2 }
const RECT_N: Annotation = { type: 'rect', x: 20, y: 20, width: 40, height: 20, color: '#FF0000', stroke_width: 2 }
const RECT_G: Annotation = { type: 'rect', x: 40, y: 40, width: 40, height: 20, color: '#FF0000', stroke_width: 2 }
const ARROW_E: Annotation = { type: 'arrow', color: '#E0AF68', stroke_width: 3, from: [20, 60], to: [60, 60] }
const TEXT_G: Annotation = { type: 'text', x: 20, y: 150, text: 'Hi', color: '#FFFFFF', font_size: 16, bg_color: null }

type FetchCall = { url: string; method: string; body: unknown; response?: Record<string, unknown> }
type Outcome = 'ok' | 'fail'
type Held = { method: 'GET' | 'PUT'; release: (outcome: Outcome) => void }
type Box4 = [number, number, number, number]

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

function pressedOf(id: string): string | null {
  return present(id).getAttribute('aria-pressed')
}

function armed(tool: Tool): boolean {
  return pressedOf(`capture-tool-${tool}`) === 'true'
}

/** The tool whose button is pressed, or null. */
function armedTool(): Tool | null {
  return TOOLS.find((tool) => screen.queryByTestId(`capture-tool-${tool}`)?.getAttribute('aria-pressed') === 'true') ?? null
}

function options(): string[] {
  return OPTION_IDS.filter((id) => screen.queryByTestId(id) !== null)
}

/** The index of the selected mark in the mark list, or null. */
function selectedMark(): number | null {
  const buttons = Array.from(present('capture-mark-list').querySelectorAll('button[aria-pressed]'))
  const index = buttons.findIndex((button) => button.getAttribute('aria-pressed') === 'true')
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

function boxOf(el: Element | undefined): Box4 | null {
  if (el === undefined) {
    return null
  }
  return ['x', 'y', 'width', 'height'].map((name) => Number(el.getAttribute(name))) as Box4
}

function lastBox(type: string): Box4 | null {
  return boxOf(painted(type).at(-1))
}

function lastArrow(): { from: [number, number]; to: [number, number]; color: string } | null {
  const el = painted('arrow').at(-1)
  if (el === undefined) {
    return null
  }
  const n = (name: string): number => Number(el.getAttribute(name))
  return { from: [n('x1'), n('y1')], to: [n('x2'), n('y2')], color: (el.getAttribute('stroke') ?? '').toUpperCase() }
}

function textX(): number[] {
  return painted('text').map((el) => Number(el.getAttribute('x')))
}

function hexValue(): string {
  return present('capture-color').value.toUpperCase()
}

function lockState(): string | null {
  return pressedOf('capture-tool-lock')
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

function focusOn(el: HTMLElement): void {
  act(() => {
    el.focus()
  })
}

function cropFields(): number[] {
  return ['x', 'y', 'w', 'h'].map((part) => Number(present(`capture-crop-${part}`).value))
}

describe('MEU-143 capture tool flow', () => {
  let user: ReturnType<typeof userEvent.setup>
  const calls: FetchCall[] = []
  const held: Held[] = []
  const keyLog: Array<{ event: KeyboardEvent; handled: boolean }> = []
  const stateLog: CommandState[] = []
  let savedMarks: unknown[]
  let stored: Record<string, unknown>
  let shot: Shot
  // D-765: true serves an empty catalog, the only way to have no shot selected.
  let noShots = false
  let getPlan: Array<'ok' | 'hold'>
  let getFails: boolean
  let putPlan: Array<'ok' | 'hold' | 'fail'>
  let helpToggles: number
  let saveEvents: number
  let shortcutListener: (event: KeyboardEvent) => void
  let helpListener: () => void
  let saveListener: () => void

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
    keyLog.length = 0
    stateLog.length = 0
    savedMarks = []
    stored = { ...BASE_SETTINGS }
    shot = SMALL
    noShots = false
    getPlan = []
    getFails = false
    putPlan = []
    helpToggles = 0
    saveEvents = 0
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
    // SHELL_WIRING as AppShell binds it, with a getState that records what the page published.
    const handler = createShortcutHandler({
      commands: listCommands(),
      getPage: () => '/capture',
      getState: (page) => {
        const state = getCommandState(page)
        stateLog.push({ ...state })
        return state
      },
      isPaletteOpen: () => false,
      closePalette: () => undefined,
    })
    shortcutListener = (event) => {
      keyLog.push({ event, handled: handler(event) })
    }
    window.addEventListener('keydown', shortcutListener)
    helpListener = () => {
      helpToggles += 1
    }
    window.addEventListener(HELP_EVENTS.toggle, helpListener)
    // AppShell owns the save bridge; the page's Ctrl+S is the registry's capture:save event.
    saveListener = () => {
      saveEvents += 1
    }
    window.addEventListener(CAPTURE_EVENTS.save, saveListener)
  })

  afterEach(async () => {
    // Settle every held request, then any PUT the style queue sends after it.
    for (let round = 0; round < 10 && held.length > 0; round += 1) {
      for (const entry of held.splice(0, held.length)) {
        entry.release('ok')
      }
      await settle()
    }
    window.removeEventListener('keydown', shortcutListener)
    window.removeEventListener(HELP_EVENTS.toggle, helpListener)
    window.removeEventListener(CAPTURE_EVENTS.save, saveListener)
    for (const modal of Array.from(document.querySelectorAll('[data-test-modal="transform"]'))) {
      modal.remove()
    }
    cleanup()
    clearCommandState('/capture')
    queryClient.clear()
    queryClient.setQueryDefaults(CAPTURE_SETTINGS_KEY, {})
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
    if (typeof store.resetCaptureStyleStore === 'function') {
      store.resetCaptureStyleStore()
    }
  })

  function gets(): number {
    return calls.filter((call) => call.method === 'GET' && call.url.includes('/settings/capture')).length
  }

  function puts(): Array<Record<string, unknown>> {
    return calls
      .filter((call) => call.method === 'PUT' && call.url.includes('/settings/capture'))
      .map((call) => (call.body ?? {}) as Record<string, unknown>)
  }

  function annotatePosts(): Array<{ annotations: Array<Record<string, unknown>> }> {
    return calls
      .filter((call) => call.method === 'POST' && call.url.endsWith('/annotate'))
      .map((call) => call.body as { annotations: Array<Record<string, unknown>> })
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
  async function openShot(marks: unknown[] = [], settings?: Record<string, unknown>, which: Shot = SMALL): Promise<HTMLElement> {
    savedMarks = marks
    shot = which
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
    bindRect(surface, { left: 0, top: 0, width: which.width, height: which.height })
    return surface
  }

  /** Unmount, clear the cache and the style store, and open the shot again on `stored`. */
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

  async function drag(el: HTMLElement, from: [number, number], to: [number, number], mods: Mods = {}): Promise<void> {
    await act(async () => {
      pointer(el, 'pointerdown', from[0], from[1], mods)
      pointer(el, 'pointermove', to[0], to[1], mods)
      pointer(el, 'pointerup', to[0], to[1], mods)
    })
  }

  async function chooseTool(tool: Tool): Promise<void> {
    await user.click(present(`capture-tool-${tool}`))
  }

  async function arm(spec: { tool: Tool; mode?: 'solid' | 'pixelate' }): Promise<void> {
    await chooseTool(spec.tool)
    if (spec.mode !== undefined) {
      await user.click(present(`capture-redact-${spec.mode}`))
    }
  }

  /** Select the mark whose content is `mark` with the Select tool, at its body point. */
  async function selectMark(surface: HTMLElement, mark: Annotation): Promise<void> {
    await chooseTool('select')
    const point = bodyHandleImagePoint(mark)
    await click(surface, Math.round(point.x), Math.round(point.y))
    expect(selectedMark(), 'one mark is selected').not.toBeNull()
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

  async function openCrop(): Promise<void> {
    await user.click(present('capture-tool-crop'))
    present('capture-crop-bar')
  }

  async function release(method: 'GET' | 'PUT', outcome: Outcome = 'ok'): Promise<void> {
    const index = held.findIndex((entry) => entry.method === method)
    expect(index, `a held ${method}`).toBeGreaterThanOrEqual(0)
    const [entry] = held.splice(index, 1)
    entry?.release(outcome)
    await settle()
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

  /** The keydowns the registry saw since `from`: none ran a command and none was prevented. */
  function quietSince(from: number): void {
    const seen = keyLog.slice(from)
    expect(seen.length, 'the registry saw the keys').toBeGreaterThan(0)
    expect(seen.filter((entry) => entry.handled).map((entry) => entry.event.key), 'no letter ran').toEqual([])
    expect(seen.filter((entry) => entry.event.defaultPrevented).map((entry) => entry.event.key), 'none prevented').toEqual([])
  }

  async function typeInField(el: HTMLElement, expected: Tool): Promise<void> {
    focusOn(el)
    const from = keyLog.length
    await user.keyboard(TYPED)
    quietSince(from)
    expect(armedTool(), 'the tool is unchanged').toBe(expected)
    expect(screen.queryByTestId('capture-crop-bar'), 'no crop opened').toBeNull()
  }

  // ---------------------------------------------------------------- LOCK_DEFAULT, ONE_SHOT, LOCK_STORE

  it('AC-143.7 the lock is on without tool_lock, off on false, on on a lone surrogate; a locked Box drag keeps Box with the box selected', async () => {
    const surface = await openShot([], { box_color: '#224466' })
    expect(lockState(), 'no tool_lock: on').toBe('true')
    await chooseTool('box')
    await drag(surface, [20, 20], [60, 50])
    expect(armed('box'), 'Box stays armed').toBe(true)
    expect(lastBox('rect')).toEqual([20, 20, 40, 30])
    expect(selectedMark(), 'the new box is selected').toBe(0)
    expect(hexValue(), "the options row shows the box's colour").toBe('#224466')
    await remount([], { tool_lock: false })
    expect(lockState(), 'tool_lock false: off').toBe('false')
    await remount([], { tool_lock: '\uD800' })
    expect(lockState(), 'a lone surrogate: on').toBe('true')
  })

  it('AC-143.8 a Lock click sends one PUT of exactly tool_lock false and shows off before it settles; the remount and one-shot', async () => {
    await openShot([])
    putPlan = ['hold']
    await user.click(present('capture-tool-lock'))
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(1)
    })
    const raw = calls.find((call) => call.method === 'PUT' && call.url.includes('/settings/capture'))
    expect(JSON.stringify(raw?.body)).toBe('{"tool_lock":false}')
    expect(lockState(), 'off before the PUT settles').toBe('false')
    await release('PUT')
    expect(stored.tool_lock).toBe(false)
    const surface = await remount([])
    expect(lockState(), 'the remount reads the stored value').toBe('false')
    await chooseTool('box')
    await drag(surface, [20, 20], [60, 50])
    expect(armed('select'), 'one-shot returns to Select').toBe(true)
    expect(selectedMark(), 'with the box selected').toBe(0)
    await user.click(present('capture-tool-lock'))
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(2)
    })
    expect(puts()[1]).toEqual({ tool_lock: true })
    expect(lockState()).toBe('true')
  })

  it('AC-143.9 held GET: a Lock click shows off at once, and the held GET answering true leaves it off', async () => {
    getPlan = ['hold']
    await openShot([], { tool_lock: true })
    expect(held.some((entry) => entry.method === 'GET'), 'the GET is held').toBe(true)
    await user.click(present('capture-tool-lock'))
    expect(lockState(), 'off at once').toBe('false')
    await vi.waitFor(() => {
      expect(puts()).toEqual([{ tool_lock: false }])
    })
    await release('GET')
    const answered = calls.filter((call) => call.method === 'GET' && call.url.includes('/settings/capture'))[0]
    expect(answered?.response?.tool_lock, 'the held GET answered true').toBe(true)
    expect(lockState(), 'the stale GET leaves it off').toBe('false')
  })

  it('AC-143.9 failed GET: the lock shows on with nothing committed; after a saved click a failing refetch still shows off', async () => {
    getFails = true
    await openShot([])
    await settle()
    expect(lockState(), 'nothing committed: on').toBe('true')
    await user.click(present('capture-tool-lock'))
    await vi.waitFor(() => {
      expect(puts()).toEqual([{ tool_lock: false }])
    })
    await settle()
    const before = gets()
    await act(async () => {
      await queryClient.refetchQueries({ queryKey: CAPTURE_SETTINGS_KEY })
    })
    await settle()
    expect(gets(), 'the refetch ran').toBeGreaterThan(before)
    expect(lockState(), 'a failing refetch still shows off').toBe('false')
  })

  it('AC-143.9 order: two clicks while the first PUT is held send the second after it settles, false then true', async () => {
    await openShot([])
    putPlan = ['hold']
    await user.click(present('capture-tool-lock'))
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(1)
    })
    await user.click(present('capture-tool-lock'))
    await settle()
    expect(puts(), 'the second PUT waits for the first').toHaveLength(1)
    expect(lockState()).toBe('true')
    await release('PUT')
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(2)
    })
    await settle()
    expect(puts()).toEqual([{ tool_lock: false }, { tool_lock: true }])
    expect(stored.tool_lock).toBe(true)
  })

  it('AC-143.9 shared queue: an arrow_color commit and a Lock click go out one after the other, in commit order', async () => {
    await openShot([])
    await chooseTool('arrow')
    putPlan = ['hold']
    await commitHex('#121212')
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(1)
    })
    await user.click(present('capture-tool-lock'))
    await settle()
    expect(puts(), 'the Lock PUT waits for the style PUT').toHaveLength(1)
    await release('PUT')
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(2)
    })
    expect(puts()).toEqual([{ arrow_color: '#121212' }, { tool_lock: false }])
  })

  it("AC-143.10 a failed Lock PUT shows Couldn't save the tool lock, names no value, refetches once and shows the stored value", async () => {
    const logged = (['error', 'warn', 'log', 'info', 'debug'] as const).map((level) =>
      vi.spyOn(console, level).mockImplementation(() => undefined),
    )
    await openShot([])
    putPlan = ['fail']
    const getsBefore = gets()
    await user.click(present('capture-tool-lock'))
    await vi.waitFor(() => {
      expect(present('capture-status').textContent ?? '').toContain("Couldn't save the tool lock")
    })
    expect(present('capture-status').textContent ?? '', 'the status names no value').not.toMatch(/\b(true|false)\b/i)
    await vi.waitFor(() => {
      expect(gets()).toBe(getsBefore + 1)
    })
    await settle()
    expect(lockState(), 'the stored value again').toBe('true')
    const consoleText = logged
      .flatMap((spy) => spy.mock.calls)
      .map((args) => args.map((arg) => (typeof arg === 'string' ? arg : String(arg))).join(' '))
      .join('\n')
    expect(consoleText).not.toMatch(/tool_lock\W*(true|false)/i)
    await chooseTool('arrow')
    putPlan = ['fail']
    await commitHex('#12abcd')
    await vi.waitFor(() => {
      expect(present('capture-status').textContent ?? '').toContain("Couldn't save the tool style")
    })
    expect(present('capture-status').textContent ?? '').not.toContain('tool lock')
  })

  // ---------------------------------------------------------------- LOCK_SELECTS, ARMED_EDIT, ARMED_RECHOOSE

  it('AC-143.11 under Lock a drag on the just-drawn box moves or resizes it; an arrow end and a text mark edit too', async () => {
    const surface = await openShot([])
    await chooseTool('box')
    await drag(surface, [20, 20], [60, 40])
    expect(armed('box'), 'Box stays armed').toBe(true)
    expect(selectedMark()).toBe(0)
    await drag(surface, [40, 30], [50, 35])
    expect(painted('rect'), 'the body drag adds no mark').toHaveLength(1)
    expect(lastBox('rect'), 'A moved').toEqual([30, 25, 40, 20])
    expect(armed('box')).toBe(true)
    await drag(surface, [70, 45], [80, 50])
    expect(painted('rect')).toHaveLength(1)
    expect(lastBox('rect'), 'A resized from its corner').toEqual([30, 25, 50, 25])
    expect(armed('box')).toBe(true)
    await undo()
    expect(lastBox('rect'), 'the resize is one step').toEqual([30, 25, 40, 20])
    await undo()
    expect(lastBox('rect'), 'the move is one step').toEqual([20, 20, 40, 20])

    await chooseTool('arrow')
    await drag(surface, [10, 70], [50, 70])
    expect(armed('arrow')).toBe(true)
    await drag(surface, [50, 70], [60, 60])
    expect(painted('arrow'), 'the end drag adds no arrow').toHaveLength(1)
    expect(lastArrow()?.to, 'the end moved').toEqual([60, 60])
    expect(armed('arrow')).toBe(true)

    await chooseTool('text')
    await click(surface, 60, 10)
    const draft = screen.queryByTestId('capture-text-draft') as HTMLTextAreaElement | null
    expect(draft, 'the draft opened').not.toBeNull()
    await user.type(draft as HTMLTextAreaElement, 'Hi')
    await user.keyboard('{Enter}')
    expect(armed('text'), 'Text stays armed').toBe(true)
    expect(textX()).toEqual([60])
    const body = bodyHandleImagePoint({ type: 'text', x: 60, y: 10, text: 'Hi', color: '#E0AF68', font_size: 16, bg_color: null })
    await drag(surface, [Math.round(body.x), Math.round(body.y)], [Math.round(body.x) + 5, Math.round(body.y) + 5])
    expect(screen.queryByTestId('capture-text-draft'), 'no draft opens').toBeNull()
    expect(textX(), 'the text moved').toEqual([65])
    expect(armed('text')).toBe(true)
  })

  it('AC-143.12 under Lock a drag elsewhere draws and selects a new box; a drag on an unselected mark draws over it', async () => {
    const surface = await openShot([RECT_C])
    await chooseTool('box')
    await drag(surface, [10, 10], [30, 30])
    expect(armed('box')).toBe(true)
    expect(selectedMark(), 'A is selected').toBe(1)
    await drag(surface, [10, 50], [30, 70])
    expect(painted('rect'), 'B was drawn').toHaveLength(3)
    expect(selectedMark(), 'B is selected').toBe(2)
    expect(boxOf(painted('rect')[1]), 'A is unchanged').toEqual([10, 10, 20, 20])
    await drag(surface, [70, 50], [80, 60])
    expect(painted('rect'), 'a new box over C').toHaveLength(4)
    expect(selectedMark(), 'C is not selected').toBe(3)
    expect(boxOf(painted('rect')[0]), 'C is unchanged').toEqual([60, 40, 30, 30])
  })

  it('AC-143.13 under Lock a hex commit restyles the just-drawn arrow; re-choosing Arrow sets its own style; Escape keeps the selection', async () => {
    const surface = await openShot([])
    await chooseTool('arrow')
    await drag(surface, [10, 10], [50, 10])
    expect(armed('arrow'), 'Arrow stays armed').toBe(true)
    expect(selectedMark()).toBe(0)
    await commitHex('#12abcd')
    await settle()
    expect(lastArrow()?.color, 'the arrow is restyled').toBe('#12ABCD')
    expect(puts(), 'no PUT for a mark restyle').toHaveLength(0)
    await undo()
    expect(lastArrow()?.color, 'one undo step').toBe('#E0AF68')
    await chooseTool('arrow')
    expect(selectedMark(), 'the button clears the selection').toBeNull()
    await commitHex('#345678')
    await vi.waitFor(() => {
      expect(puts()).toEqual([{ arrow_color: '#345678' }])
    })
    await drag(surface, [10, 40], [50, 40])
    expect(lastArrow()?.color, 'the next arrow has that colour').toBe('#345678')
    expect(selectedMark()).toBe(1)
    focusOn(surface)
    keyOn(surface, 'a')
    expect(selectedMark(), 'the letter A clears the selection').toBeNull()
    await drag(surface, [10, 60], [50, 60])
    expect(selectedMark()).toBe(2)
    focusOn(surface)
    keyOn(surface, 'Escape')
    expect(selectedMark(), 'Escape leaves the selection').toBe(2)
  })

  it('AC-143.14 under Lock a text commit keeps Text with the text selected; a click away opens a draft; one-shot returns to Select', async () => {
    const surface = await openShot([])
    await chooseTool('text')
    await click(surface, 20, 10)
    const first = screen.queryByTestId('capture-text-draft') as HTMLTextAreaElement | null
    expect(first).not.toBeNull()
    await user.type(first as HTMLTextAreaElement, 'Hi')
    await user.keyboard('{Enter}')
    expect(armed('text'), 'Text stays armed').toBe(true)
    expect(selectedMark(), 'the text is selected').toBe(0)
    await click(surface, 60, 60)
    expect(screen.queryByTestId('capture-text-draft'), 'a click away opens a draft').not.toBeNull()
    await user.keyboard('{Escape}')
    await user.click(present('capture-tool-lock'))
    expect(lockState()).toBe('false')
    await chooseTool('text')
    await click(surface, 60, 40)
    const second = screen.queryByTestId('capture-text-draft') as HTMLTextAreaElement | null
    expect(second).not.toBeNull()
    await user.type(second as HTMLTextAreaElement, 'Yo')
    await user.keyboard('{Enter}')
    expect(armed('select'), 'one-shot returns to Select').toBe(true)
    expect(selectedMark(), 'with the text selected').toBe(1)
  })

  // ---------------------------------------------------------------- LETTERS, LETTER_HINTS, FIELD_GUARD

  it.each(LETTER_CASES)('AC-143.16 the letter $letter arms $tool as its button does', async ({ letter, tool, colour, mark }) => {
    const surface = await openShot([], STYLE_COLOURS)
    let reference: string[]
    if (tool === 'crop') {
      await openCrop()
      reference = options()
      await user.click(present('capture-crop-cancel'))
      expect(screen.queryByTestId('capture-crop-bar')).toBeNull()
    } else {
      await chooseTool(tool)
      reference = options()
      await chooseTool(tool === 'select' ? 'box' : 'select')
    }
    focusOn(surface)
    const event = keyOn(surface, letter)
    expect(event.defaultPrevented, `${letter} is prevented`).toBe(true)
    if (tool === 'crop') {
      expect(screen.queryByTestId('capture-crop-bar'), 'C opens the crop').not.toBeNull()
    } else {
      expect(armed(tool), `${letter} arms ${tool}`).toBe(true)
    }
    expect(options(), 'the options row a click gives').toEqual(reference)
    if (tool === 'select') {
      expect(screen.queryByTestId('capture-color'), 'SELECT_NO_STYLE').toBeNull()
    }
    if (colour !== undefined) {
      expect(hexValue(), "the tool's own colour").toBe(colour)
    }
    if (mark !== undefined) {
      await drag(surface, [20, 20], [60, 50])
      const drawn = painted(mark).at(-1)
      const paint = mark === 'highlight' ? drawn?.getAttribute('fill') : drawn?.getAttribute('stroke')
      expect((paint ?? '').toUpperCase(), "the mark carries the tool's style").toBe(colour)
    }
  })

  it('AC-143.17 each tool hint names its letter, carries aria-keyshortcuts and keeps the bare name; no shot, no letter', async () => {
    await openShot([])
    for (const { id, letter, name, hint } of HINT_CASES) {
      expect(hintOf(id), id).toBe(hint)
      expect(present(id).getAttribute('aria-keyshortcuts'), id).toBe(letter)
      expect(present(id).getAttribute('aria-label'), id).toBe(name)
    }
    cleanup()
    clearCommandState('/capture')
    queryClient.clear()
    noShots = true
    renderPage()
    await vi.waitFor(() => {
      expect(present<HTMLButtonElement>('capture-tool-select').disabled).toBe(true)
    })
    await settle()
    expect(screen.queryAllByTestId('capture-filmstrip-item')).toHaveLength(0)
    for (const { id, letter, name } of HINT_CASES) {
      expect(hintOf(id), `${id} with no shot`).toBe(`${name} (${letter}) — Select a shot first`)
    }
    const event = keyOn(document.body, 'r')
    expect(event.defaultPrevented, 'the no-shot letter is not prevented').toBe(false)
    expect(armed('box')).toBe(false)
  })

  it('AC-143.18 letters type in the draft, the hex, number fields, the named menu and the palette; Ctrl+S and F1 still work', async () => {
    const surface = await openShot([])
    focusOn(surface)
    const control = keyOn(surface, 'r')
    expect(control.defaultPrevented && armed('box'), 'R on the surface arms Box').toBe(true)

    await chooseTool('arrow')
    await drag(surface, [10, 10], [50, 10])
    const hex = present('capture-color')
    focusOn(hex)
    await user.keyboard('{F1}')
    expect(helpToggles, 'F1 toggles help from the hex field').toBe(1)
    focusOn(present('capture-color'))
    await user.keyboard('{Control>}s{/Control}')
    expect(saveEvents, 'Ctrl+S saves from the hex field').toBe(1)

    await chooseTool('text')
    await click(surface, 20, 40)
    const draft = screen.queryByTestId('capture-text-draft') as HTMLTextAreaElement | null
    expect(draft, 'the draft opened').not.toBeNull()
    await typeInField(draft as HTMLTextAreaElement, 'text')
    expect((draft as HTMLTextAreaElement).value, 'the draft holds the typed text').toBe(TYPED)
    await user.keyboard('{Escape}')

    await chooseTool('arrow')
    await typeInField(present('capture-color'), 'arrow')
    await typeInField(present('capture-stroke'), 'arrow')
    await typeInField(present('capture-named-color'), 'arrow')
    await chooseTool('text')
    await typeInField(present('capture-font-size'), 'text')
    await arm({ tool: 'redact', mode: 'pixelate' })
    await typeInField(present('capture-block-size'), 'redact')

    render(createElement(CommandPalette, { open: true, onClose: () => undefined }))
    await typeInField(present('command-palette-input'), 'redact')
  })

  it('AC-143.19 with the crop open on 16:9 one x swaps once; with the crop closed X arms Redact', async () => {
    const surface = await openShot([], undefined, LAND)
    await openCrop()
    await user.selectOptions(present<HTMLSelectElement>('capture-crop-aspect'), '16:9')
    expect(cropFields(), '16:9').toEqual([22, 0, 356, 200])
    focusOn(surface)
    keyOn(surface, 'x')
    expect(cropFields(), 'swapped exactly once').toEqual([144, 1, 112, 199])
    expect(armed('redact'), 'Redact stays unarmed').toBe(false)
    expect(screen.queryByTestId('capture-crop-bar'), 'the crop stays').not.toBeNull()
    await user.click(present('capture-crop-cancel'))
    focusOn(surface)
    const event = keyOn(surface, 'x')
    expect(armed('redact'), 'X arms Redact').toBe(true)
    expect(event.defaultPrevented).toBe(true)
    expect(screen.queryByTestId('capture-crop-bar'), 'no crop').toBeNull()
  })

  it('AC-143.20 letters do nothing with the crop open, a confirm open, a modal dialog open, or held', async () => {
    const surface = await openShot([])
    focusOn(surface)
    expect(keyOn(surface, 'r').defaultPrevented && armed('box'), 'R arms Box with nothing open').toBe(true)
    await chooseTool('select')

    await openCrop()
    for (const letter of ['v', 'a', 'r', 'h', 't', 'e', 'c']) {
      focusOn(surface)
      const event = keyOn(surface, letter)
      expect(event.defaultPrevented, `${letter} with the crop open`).toBe(false)
      expect(screen.queryByTestId('capture-crop-bar'), `${letter} leaves the crop open`).not.toBeNull()
    }
    await user.click(present('capture-crop-cancel'))
    expect(armed('select')).toBe(true)

    await user.click(present('capture-delete'))
    present('capture-confirm-strip')
    for (const letter of ['v', 'a', 'r', 'h', 't', 'x', 'e', 'c']) {
      const event = keyOn(document.activeElement ?? document.body, letter)
      expect(event.defaultPrevented, `${letter} with the confirm open`).toBe(false)
    }
    expect(armed('select'), 'the confirm keeps the tool').toBe(true)
    expect(screen.queryByTestId('capture-crop-bar')).toBeNull()
    await user.click(present('capture-delete-confirm-cancel'))

    // There is no transform dialog in today's page; an aria-modal element stands in for it (MODAL_GUARD).
    const modal = document.createElement('div')
    modal.setAttribute('aria-modal', 'true')
    modal.setAttribute('data-test-modal', 'transform')
    document.body.appendChild(modal)
    for (const letter of ['v', 'a', 'r', 'h', 't', 'x', 'e', 'c']) {
      focusOn(surface)
      expect(keyOn(surface, letter).defaultPrevented, `${letter} with a modal open`).toBe(false)
    }
    expect(armed('select'), 'the modal keeps the tool').toBe(true)
    modal.remove()

    focusOn(surface)
    expect(keyOn(surface, 'r', { repeat: true }).defaultPrevented, 'a held letter').toBe(false)
    expect(armed('select')).toBe(true)
  })

  it('AC-143.21 trace: one A keydown through createShortcutHandler, the capture:tool_arrow action and one button click', async () => {
    const surface = await openShot([], { arrow_color: '#123456' })
    await chooseTool('box')
    const button = present<HTMLButtonElement>('capture-tool-arrow')
    let clicks = 0
    button.addEventListener('click', () => {
      clicks += 1
    })
    focusOn(surface)
    const from = keyLog.length
    stateLog.length = 0
    const event = keyOn(surface, 'a')
    const entry = keyLog.slice(from).find((logged) => logged.event === event)
    expect(entry?.handled, 'the registry ran the letter').toBe(true)
    expect(stateLog.some((state) => state['capture:tool_arrow'] === true), 'getState saw capture:tool_arrow true').toBe(true)
    expect(clicks, 'the button was clicked exactly once').toBe(1)
    expect(armed('arrow')).toBe(true)
    expect(hexValue(), "the arrow tool's saved colour").toBe('#123456')
  })

  it('AC-143.22 trace: one Lock click through saveCaptureToolLock and captureLockPutSchema to the recorded PUT body', async () => {
    await openShot([])
    await user.click(present('capture-tool-lock'))
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(1)
    })
    const raw = calls.find((call) => call.method === 'PUT' && call.url.includes('/settings/capture'))
    expect(raw?.body).toEqual(captureLockPutSchema.parse({ tool_lock: false }))
    expect(JSON.stringify(raw?.body)).toBe('{"tool_lock":false}')
    expect(captureLockPutSchema.safeParse({ tool_lock: false, arrow_color: '#123456' }).success, 'strict').toBe(false)
    await settle()
    act(() => {
      store.saveCaptureToolLock(queryClient, true)
    })
    expect(lockState(), 'merged into the cache at once').toBe('true')
    await vi.waitFor(() => {
      expect(puts()).toEqual([{ tool_lock: false }, { tool_lock: true }])
    })
  })

  // ---------------------------------------------------------------- MODIFIERS, SHIFT_NUDGE, ALT_NO_MENU

  it.each(BOUNDED)('AC-143.23 Shift draws a square with $name, cut to the image; without Shift the plain box', async (spec) => {
    const surface = await openShot([])
    await arm(spec)
    await drag(surface, [10, 10], [50, 30], { shiftKey: true })
    expect(painted(spec.type)).toHaveLength(1)
    expect(lastBox(spec.type), 'a 40x40 square').toEqual([10, 10, 40, 40])
    await arm(spec)
    await drag(surface, [90, 70], [30, 60], { shiftKey: true })
    expect(painted(spec.type)).toHaveLength(2)
    expect(lastBox(spec.type), 'a 60x60 square up and left').toEqual([30, 10, 60, 60])
    await arm(spec)
    await drag(surface, [10, 10], [50, 30])
    expect(painted(spec.type)).toHaveLength(3)
    expect(lastBox(spec.type), 'the plain drag').toEqual([10, 10, 40, 20])
  })

  it('AC-143.24 Shift on a corner handle keeps 2:1; without Shift the plain resize; an edge handle ignores Shift', async () => {
    const surface = await openShot([RECT_A])
    await selectMark(surface, RECT_A)
    await drag(surface, [50, 30], [70, 34], { shiftKey: true })
    expect(lastBox('rect'), 'the width drives').toEqual([10, 10, 60, 30])
    await undo()
    await selectMark(surface, RECT_A)
    await drag(surface, [50, 30], [70, 34])
    expect(lastBox('rect'), 'the plain resize').toEqual([10, 10, 60, 24])
    await undo()
    await selectMark(surface, RECT_A)
    await drag(surface, [50, 20], [70, 24])
    const plainEdge = lastBox('rect')
    expect(plainEdge).toEqual([10, 10, 60, 20])
    await undo()
    await selectMark(surface, RECT_A)
    await drag(surface, [50, 20], [70, 24], { shiftKey: true })
    expect(lastBox('rect'), 'the edge handle ignores Shift').toEqual(plainEdge)
  })

  it('AC-143.25 Shift snaps an arrow to 45 degrees as it is drawn and as its end is dragged', async () => {
    const surface = await openShot([ARROW_E])
    await chooseTool('arrow')
    await drag(surface, [10, 10], [50, 22], { shiftKey: true })
    expect(lastArrow()?.to, 'on the horizontal, 41.76 px rounded').toEqual([52, 10])
    await chooseTool('arrow')
    await drag(surface, [10, 10], [40, 38], { shiftKey: true })
    expect(lastArrow()?.to, 'on the 45 degree line').toEqual([39, 39])
    await selectMark(surface, ARROW_E)
    await drag(surface, [60, 60], [50, 72], { shiftKey: true })
    const arrow = painted('arrow')[0]
    expect([Number(arrow?.getAttribute('x2')), Number(arrow?.getAttribute('y2'))], 'snapped about the fixed end').toEqual([52, 60])
    expect([Number(arrow?.getAttribute('x1')), Number(arrow?.getAttribute('y1'))], 'the fixed end').toEqual([20, 60])
  })

  it.each(BOUNDED)('AC-143.26 Alt draws $name from its centre, cut to the image; Shift+Alt a square', async (spec) => {
    const surface = await openShot([])
    await arm(spec)
    await drag(surface, [30, 30], [40, 35], { altKey: true })
    expect(lastBox(spec.type), 'from the centre').toEqual([20, 25, 20, 10])
    await arm(spec)
    await drag(surface, [30, 30], [40, 35], { altKey: true, shiftKey: true })
    expect(lastBox(spec.type), 'a square from the centre').toEqual([20, 20, 20, 20])
    await arm(spec)
    await drag(surface, [5, 5], [20, 10], { altKey: true })
    expect(lastBox(spec.type), 'the centre stays at (5, 5)').toEqual([0, 0, 10, 10])
  })

  it('AC-143.26 Alt leaves an arrow draw, a text click and a move as they are; Shift leaves a move as it is', async () => {
    const surface = await openShot([RECT_N])
    await chooseTool('arrow')
    await drag(surface, [10, 70], [50, 74], { altKey: true })
    expect(lastArrow()?.from).toEqual([10, 70])
    expect(lastArrow()?.to).toEqual([50, 74])
    await chooseTool('text')
    await click(surface, 70, 5, { altKey: true })
    expect(screen.queryByTestId('capture-text-draft'), 'an Alt click opens a draft').not.toBeNull()
    await user.keyboard('{Escape}')
    await selectMark(surface, RECT_N)
    await drag(surface, [40, 30], [45, 32], { altKey: true })
    expect(lastBox('rect'), 'an Alt move').toEqual([25, 22, 40, 20])
    await drag(surface, [45, 32], [50, 34], { shiftKey: true })
    expect(lastBox('rect'), 'a Shift move').toEqual([30, 24, 40, 20])
  })

  it('AC-143.27 Shift+arrow nudges 10 px and plain 1 px; a burst is one undo step; the edge clamps; FIELD_STEP_SHIFT', async () => {
    const surface = await openShot([RECT_N])
    await selectMark(surface, RECT_N)
    focusOn(surface)
    keyOn(surface, 'ArrowRight', { shiftKey: true })
    keyOn(surface, 'ArrowRight', { shiftKey: true }, 'keyup')
    expect(lastBox('rect')?.[0], 'Shift+ArrowRight moves 10').toBe(30)
    keyOn(surface, 'ArrowRight')
    keyOn(surface, 'ArrowRight', {}, 'keyup')
    expect(lastBox('rect')?.[0], 'ArrowRight moves 1').toBe(31)
    keyOn(surface, 'ArrowRight', { shiftKey: true })
    keyOn(surface, 'ArrowRight', { shiftKey: true })
    keyOn(surface, 'ArrowRight', { shiftKey: true }, 'keyup')
    expect(lastBox('rect')?.[0]).toBe(51)
    await undo()
    expect(lastBox('rect')?.[0], 'the burst is one step').toBe(31)
    await selectMark(surface, { ...RECT_N, x: 31 })
    focusOn(surface)
    for (let i = 0; i < 80; i += 1) {
      keyOn(surface, 'ArrowRight')
    }
    keyOn(surface, 'ArrowRight', {}, 'keyup')
    const edge = lastBox('rect')?.[0]
    expect(edge, 'the plain nudge reached the edge').toBeGreaterThan(51)
    await undo()
    expect(lastBox('rect')?.[0], 'the plain burst is one step').toBe(31)
    await selectMark(surface, { ...RECT_N, x: 31 })
    focusOn(surface)
    for (let i = 0; i < 8; i += 1) {
      keyOn(surface, 'ArrowRight', { shiftKey: true })
    }
    keyOn(surface, 'ArrowRight', { shiftKey: true }, 'keyup')
    expect(lastBox('rect')?.[0], 'the Shift nudge clamps where the plain nudge does').toBe(edge)
    const page = readFileSync(resolve(UI, 'src/renderer/src/features/capture/CapturePage.tsx'), 'utf8')
    expect(page, 'the page imports FIELD_STEP_SHIFT').toMatch(/\bFIELD_STEP_SHIFT\b/)
  })

  it('AC-143.27 with the crop open Shift+ArrowRight moves the crop by CROP_NUDGE_SHIFT_PX, as today', async () => {
    const surface = await openShot([], undefined, LAND)
    await openCrop()
    await user.selectOptions(present<HTMLSelectElement>('capture-crop-aspect'), 'square')
    expect(cropFields()).toEqual([100, 0, 200, 200])
    focusOn(surface)
    keyOn(surface, 'ArrowRight', { shiftKey: true })
    expect(cropFields()[0]).toBe(110)
    keyOn(surface, 'ArrowRight')
    expect(cropFields()[0]).toBe(111)
  })

  it('AC-143.28 Alt is prevented during a bounded drag and on the first keyup after one; a plain Alt is not', async () => {
    const surface = await openShot([])
    await chooseTool('box')
    focusOn(surface)
    await act(async () => {
      pointer(surface, 'pointerdown', 10, 10)
      pointer(surface, 'pointermove', 30, 30)
    })
    const down = keyOn(surface, 'Alt', { altKey: true })
    const up = keyOn(surface, 'Alt', {}, 'keyup')
    await act(async () => {
      pointer(surface, 'pointerup', 30, 30)
    })
    expect(down.defaultPrevented, 'the Alt keydown during the drag').toBe(true)
    expect(up.defaultPrevented, 'the Alt keyup during the drag').toBe(true)
    await chooseTool('box')
    focusOn(surface)
    await drag(surface, [40, 40], [60, 60], { altKey: true })
    expect(keyOn(surface, 'Alt', {}, 'keyup').defaultPrevented, 'the first Alt keyup after an Alt drag').toBe(true)
    expect(keyOn(surface, 'Alt', { altKey: true }).defaultPrevented, 'a plain Alt keydown').toBe(false)
    expect(keyOn(surface, 'Alt', {}, 'keyup').defaultPrevented, 'a plain Alt keyup').toBe(false)
  })

  // ---------------------------------------------------------------- Guards

  it("AC-143.30 after a Lock click the Capture card's unsaved edit stays, its Save sends only inbox_dir, and the GET keeps tool_lock", async () => {
    await openShot([], { tool_lock: true })
    await user.click(present('capture-settings-toggle'))
    const inbox = present('capture-inbox-path')
    await user.clear(inbox)
    await user.type(inbox, 'C:/Pictures/inbox-9')
    await user.click(present('capture-tool-lock'))
    await settle()
    expect(present('capture-inbox-path').value, 'the unsaved edit stays').toBe('C:/Pictures/inbox-9')
    const getsBefore = gets()
    await user.click(present('capture-page-save'))
    await vi.waitFor(() => {
      expect(puts().some((body) => 'inbox_dir' in body)).toBe(true)
    })
    const card = puts().find((body) => 'inbox_dir' in body) ?? {}
    expect(Object.keys(card).sort(), 'the card body has no tool_lock').toEqual(CARD_KEYS)
    expect(card.inbox_dir).toBe('C:/Pictures/inbox-9')
    await vi.waitFor(() => {
      expect(gets()).toBeGreaterThan(getsBefore)
    })
    const after = calls.filter((call) => call.method === 'GET' && call.url.includes('/settings/capture')).at(-1)
    expect(after?.response !== undefined && 'tool_lock' in after.response, 'the GET still returns tool_lock').toBe(true)
  })

  it('AC-143.33 Ctrl+Z and Ctrl+Y, Escape, Delete, F1, Ctrl+S and Enter re-edit behave as today', async () => {
    shot = SQUARE
    const surface = await openShot([RECT_G, TEXT_G], undefined, SQUARE)
    await selectMark(surface, RECT_G)
    focusOn(surface)
    keyOn(surface, 'ArrowRight')
    keyOn(surface, 'ArrowRight', {}, 'keyup')
    expect(boxOf(painted('rect')[0])?.[0]).toBe(41)
    keyOn(surface, 'z', { ctrlKey: true })
    expect(boxOf(painted('rect')[0])?.[0], 'Ctrl+Z').toBe(40)
    keyOn(surface, 'y', { ctrlKey: true })
    expect(boxOf(painted('rect')[0])?.[0], 'Ctrl+Y').toBe(41)
    await selectMark(surface, { ...RECT_G, x: 41 })
    expect(selectedMark()).toBe(0)
    focusOn(surface)
    keyOn(surface, 'Escape')
    expect(selectedMark(), 'Escape keeps the selection').toBe(0)
    keyOn(surface, 'Delete')
    expect(painted('rect'), 'Delete removes the mark').toHaveLength(0)
    keyOn(surface, 'F1')
    expect(helpToggles, 'F1 toggles help').toBe(1)
    const save = keyOn(surface, 's', { ctrlKey: true })
    expect(saveEvents, 'Ctrl+S saves').toBe(1)
    expect(save.defaultPrevented).toBe(true)
    await selectMark(surface, TEXT_G)
    focusOn(surface)
    keyOn(surface, 'Enter')
    const draft = screen.queryByTestId('capture-text-draft') as HTMLTextAreaElement | null
    expect(draft, 'Enter re-edits the text').not.toBeNull()
    expect(draft?.value).toBe('Hi')
  })

  it("AC-143.33 the crop's arrows, Shift+arrow and Escape behave as today", async () => {
    const surface = await openShot([], undefined, LAND)
    await openCrop()
    await user.selectOptions(present<HTMLSelectElement>('capture-crop-aspect'), 'square')
    expect(cropFields()).toEqual([100, 0, 200, 200])
    focusOn(surface)
    keyOn(surface, 'ArrowLeft')
    expect(cropFields()[0]).toBe(99)
    keyOn(surface, 'ArrowRight', { shiftKey: true })
    expect(cropFields()[0]).toBe(109)
    keyOn(surface, 'Escape')
    expect(screen.queryByTestId('capture-crop-bar'), 'Escape closes the crop').toBeNull()
  })

  it('AC-143.34 no letter, modifier or Lock value enters mark JSON', async () => {
    const surface = await openShot([])
    await chooseTool('box')
    await drag(surface, [10, 10], [40, 30])
    await chooseTool('box')
    await drag(surface, [50, 40], [80, 50], { shiftKey: true, altKey: true })
    const marks = await saveMarks()
    expect(marks).toHaveLength(2)
    for (const mark of marks) {
      expect(Object.keys(mark).sort()).toEqual(RECT_KEYS)
    }
  })
})
