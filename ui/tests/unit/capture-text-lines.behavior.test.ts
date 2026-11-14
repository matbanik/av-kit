/** @vitest-environment jsdom */

import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { act, cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClientProvider } from '@tanstack/react-query'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { CapturePage } from '../../src/renderer/src/features/capture/CapturePage'
import { SEGOE_LA_BASE_SIZE, SEGOE_LA_GLYPHS } from '../../src/renderer/src/features/capture/capture-segoe-metrics'
import * as tm from '../../src/renderer/src/features/capture/capture-text-metrics'
import { queryClient } from '../../src/renderer/src/lib/query-client'
import * as ids from '../e2e/test-ids'

// Session 70 (MEU-102): multi-line text marks. The metrics, the SVG lines, the draft keys and
// hint, re-edit, hit-testing and the save body, on the real CapturePage with the app's query
// client. The harness is modelled on capture-copy-image.behavior.test.ts; the shot is 200x200
// on a 200x200 surface, so one screen px is one image px.

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

type Geometry = {
  segoe_ascent: Record<string, number>
  segoe_line_pitch: Record<string, number>
  text_plates: { x: number; y: number; text: string; font_size: number; box: [number, number, number, number] }[]
}

const GEOMETRY = JSON.parse(
  readFileSync(resolve(dirname(fileURLToPath(import.meta.url)), '../e2e/fixtures/capture-geometry.json'), 'utf8'),
) as Geometry

const HINT = 'Enter to finish, Shift+Enter for a new line, Esc to cancel'
const MATRIX_TEXTS = ['Hi\nHi', 'Hi\n\nHi', 'Hi\n', '\nHi', '\n', 'Hello\nW\ngy', 'Hi\n\nHello\n', 'i\nWWWW', '  \n  ']
const FALLBACK = { l: 0, t: 7, r: 8, b: 18, adv: 8 }

/** The TEXT_PLATE_LINES oracle: the union of each line's unrounded extents, rounded and clamped once. */
function unionOracle(x: number, y: number, text: string, fontSize: number): { x: number; y: number; width: number; height: number } {
  const size = Math.max(1, fontSize)
  const scale = size / SEGOE_LA_BASE_SIZE
  const pitch = GEOMETRY.segoe_line_pitch[String(size)] as number
  let l = Number.POSITIVE_INFINITY
  let t = Number.POSITIVE_INFINITY
  let r = Number.NEGATIVE_INFINITY
  let b = Number.NEGATIVE_INFINITY
  text.split('\n').forEach((line, i) => {
    const top = y + i * pitch
    if (line.length === 0) {
      l = Math.min(l, x)
      t = Math.min(t, top)
      r = Math.max(r, x)
      b = Math.max(b, top)
      return
    }
    let cursor = x
    for (const ch of line) {
      const g = SEGOE_LA_GLYPHS[ch] ?? FALLBACK
      l = Math.min(l, cursor + g.l * scale)
      t = Math.min(t, top + g.t * scale)
      r = Math.max(r, cursor + g.r * scale)
      b = Math.max(b, top + g.b * scale)
      cursor += g.adv * scale
    }
  })
  const left = Math.round(l)
  const tp = Math.round(t)
  return { x: left, y: tp, width: Math.max(1, Math.round(r) - left), height: Math.max(1, Math.round(b) - tp) }
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

function textMark(text: string, x = 10, y = 20, fontSize = 16): Record<string, unknown> {
  return { type: 'text', x, y, text, color: '#000000', font_size: fontSize, bg_color: '#FFD400' }
}

type FetchCall = { url: string; method: string; body: string | null }

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

describe('MEU-102 multi-line text marks', () => {
  let user: ReturnType<typeof userEvent.setup>
  const calls: FetchCall[] = []
  let savedMarks: unknown[]

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

  beforeEach(() => {
    user = userEvent.setup()
    calls.length = 0
    savedMarks = []
    const captureSettings = {
      inbox_dir: 'C:/Pictures/av-kit',
      hotkey: 'F2',
      copy_to_clipboard: false,
      close_to_tray: true,
      flatten_backup: true,
      backup_dir: '',
      annotated_format: 'png',
    }
    queryClient.setQueryData(['settings', 'capture'], captureSettings)
    URL.createObjectURL = vi.fn(() => 'blob:capture-shot')
    URL.revokeObjectURL = vi.fn()
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = hrefOf(input)
      const method = (init?.method ?? 'GET').toUpperCase()
      calls.push({ url, method, body: typeof init?.body === 'string' ? init.body : null })
      const path = url.split('?')[0] ?? url
      if (path.includes('/settings/capture')) {
        return jsonResponse(captureSettings)
      }
      if (path.includes('/captures/requests')) {
        return jsonResponse({ items: [] })
      }
      if (/\/captures\/.+\/image$/.test(path)) {
        return new Response(PNG_BYTES, { status: 200, headers: { 'Content-Type': 'image/png' } })
      }
      if (path.endsWith('/annotate')) {
        savedMarks = (JSON.parse(String(init?.body ?? '{}')) as { annotations: unknown[] }).annotations
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

  afterEach(() => {
    cleanup()
    queryClient.clear()
    vi.unstubAllGlobals()
  })

  /** Render with `marks` saved on the shot, select it, and wait until its overlay is ready. */
  async function openShot(marks: unknown[] = []): Promise<HTMLElement> {
    savedMarks = marks
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

  /** Text tool, then a click at (30, 40): a new, empty draft. */
  async function newDraft(surface: HTMLElement): Promise<HTMLTextAreaElement> {
    await user.click(screen.getByTestId('capture-tool-text'))
    await click(surface, 30, 40)
    return draftField() as HTMLTextAreaElement
  }

  function draftField(): HTMLTextAreaElement | HTMLInputElement | null {
    return screen.queryByTestId('capture-text-draft') as HTMLTextAreaElement | HTMLInputElement | null
  }

  function textMarks(): SVGTextElement[] {
    return Array.from(document.querySelectorAll('[data-annotation-type="text"]')) as SVGTextElement[]
  }

  /** The lines a painted text mark shows: its `<tspan>` children, or its own text with none. */
  function linesOf(el: Element): string[] {
    const spans = Array.from(el.querySelectorAll('tspan'))
    return spans.length > 0 ? spans.map((span) => span.textContent ?? '') : [el.textContent ?? '']
  }

  function annotatePosts(): FetchCall[] {
    return calls.filter((call) => call.method === 'POST' && call.url.endsWith('/annotate'))
  }

  it('AC-102.1 the TS names: TEXT_LINE_GAP_PX, segoeLinePitchPx, textLines and CAPTURE_TEXT_DRAFT_HINT', () => {
    expect(tm.TEXT_LINE_GAP_PX).toBe(4)
    const pitch: (fontSize: number) => number = tm.segoeLinePitchPx
    const lines: (text: string) => string[] = tm.textLines
    expect(typeof pitch).toBe('function')
    expect(pitch.length).toBe(1)
    expect(typeof lines).toBe('function')
    expect(lines.length).toBe(1)
    expect(ids.CAPTURE_TEXT_DRAFT_HINT).toBe('capture-text-draft-hint')
  })

  it('AC-102.9 segoeLinePitchPx equals segoe_line_pitch at every size; textLines splits on \\n', () => {
    const sizes = Object.keys(GEOMETRY.segoe_line_pitch).map(Number)
    expect(sizes).toEqual(Object.keys(GEOMETRY.segoe_ascent).map(Number))
    for (const size of sizes) {
      expect(tm.segoeLinePitchPx(size), `size ${size}`).toBe(GEOMETRY.segoe_line_pitch[String(size)])
      expect(tm.segoeLinePitchPx(size), `ascent + gap at ${size}`).toBe(tm.segoeAscentPx(size) + tm.TEXT_LINE_GAP_PX)
    }
    expect(tm.textLines('Hi\n\nHi\n')).toEqual(['Hi', '', 'Hi', ''])
    expect(tm.textLines('Hi')).toEqual(['Hi'])
  })

  it('AC-102.10 textBackgroundBox equals each text_plates box and the line-union oracle; a trailing \\n reaches the empty line', () => {
    expect(GEOMETRY.text_plates).toHaveLength(16)
    for (const plate of GEOMETRY.text_plates) {
      const [l, t, r, b] = plate.box
      const label = `${JSON.stringify(plate.text)}@${plate.font_size}`
      expect(tm.textBackgroundBox(plate), label).toEqual({ x: l, y: t, width: r - l, height: b - t })
    }
    for (const text of MATRIX_TEXTS) {
      for (const size of [8, 16, 32, 64]) {
        const input = { x: 10, y: 20, text, font_size: size }
        expect(tm.textBackgroundBox(input), `${JSON.stringify(text)}@${size}`).toEqual(unionOracle(10, 20, text, size))
      }
    }
    for (const size of [8, 16, 32, 64]) {
      expect(tm.textBackgroundBox({ x: 10, y: 20, text: 'Hello', font_size: size })).toEqual(
        unionOracle(10, 20, 'Hello', size),
      )
    }
    const one = tm.textBackgroundBox({ x: 10, y: 20, text: 'Hi', font_size: 16 })
    const trailing = tm.textBackgroundBox({ x: 10, y: 20, text: 'Hi\n', font_size: 16 })
    expect(one.y + one.height, 'Hi ends at 38').toBe(38)
    expect(trailing.y + trailing.height, 'Hi\\n ends at the empty line top, 42').toBe(42)
  })

  it('AC-102.11 a multi-line mark paints one <text> with a <tspan> per line; a one-line mark has none', async () => {
    await openShot([textMark('Hi\n\nHi'), textMark('Hi', 10, 120)])
    const marks = textMarks()
    expect(marks).toHaveLength(2)
    const spans = Array.from(marks[0]?.querySelectorAll('tspan') ?? [])
    expect(spans).toHaveLength(3)
    expect(spans.map((span) => span.getAttribute('x'))).toEqual(['10', '10', '10'])
    expect(spans.map((span) => span.getAttribute('y'))).toEqual(['38', '60', '82'])
    expect(spans.map((span) => span.textContent)).toEqual(['Hi', '', 'Hi'])
    expect(marks[1]?.querySelectorAll('tspan')).toHaveLength(0)
    expect(marks[1]?.textContent).toBe('Hi')
  })

  it('AC-102.12 Shift+Enter adds a line and Enter commits Hi\\nHi; Enter alone after Hi commits Hi', async () => {
    const surface = await openShot()
    const draft = await newDraft(surface)
    await user.type(draft, 'Hi{Shift>}{Enter}{/Shift}')
    expect(draftField(), 'Shift+Enter keeps the draft open').not.toBeNull()
    await user.type(draftField() as HTMLTextAreaElement, 'Hi{Enter}')
    expect(draftField(), 'Enter closes the draft').toBeNull()
    expect(textMarks()).toHaveLength(1)
    expect(linesOf(textMarks()[0] as Element)).toEqual(['Hi', 'Hi'])
    const second = await newDraft(surface)
    await user.type(second, 'Hi{Enter}')
    expect(draftField()).toBeNull()
    expect(textMarks()).toHaveLength(2)
    // Both marks sit at one point and the DOM order is not the commit order: match by content.
    expect(textMarks().map((el) => linesOf(el)).sort()).toEqual([['Hi'], ['Hi', 'Hi']])
  })

  it('AC-102.13 the draft is a textarea with wrap off and one row per line, at least 1', async () => {
    const surface = await openShot()
    const draft = await newDraft(surface)
    expect(draft.tagName).toBe('TEXTAREA')
    expect(draft.getAttribute('wrap')).toBe('off')
    expect(draft.getAttribute('rows'), 'an empty draft has 1 row').toBe('1')
    await user.type(draft, 'Hi{Shift>}{Enter}{/Shift}Hi{Shift>}{Enter}{/Shift}')
    expect(draftField()?.getAttribute('rows')).toBe('3')
  })

  it('AC-102.14 composing Enter neither commits nor closes; Escape closes with no mark', async () => {
    const surface = await openShot()
    const draft = await newDraft(surface)
    await user.type(draft, 'Hi')
    await act(async () => {
      draft.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true, cancelable: true, isComposing: true }))
    })
    expect(draftField(), 'composing Enter keeps the draft').not.toBeNull()
    expect(textMarks()).toHaveLength(0)
    await user.type(draftField() as HTMLElement, '{Escape}')
    expect(draftField()).toBeNull()
    expect(textMarks()).toHaveLength(0)
  })

  it('AC-102.15 the hint reads the keys while the draft is open and the draft names it; with no draft it is absent', async () => {
    const surface = await openShot()
    expect(screen.queryByTestId('capture-text-draft-hint'), 'no draft, no hint').toBeNull()
    const draft = await newDraft(surface)
    const hint = screen.queryByTestId('capture-text-draft-hint')
    expect(hint).not.toBeNull()
    expect(hint?.textContent).toBe(HINT)
    expect(hint?.id).toBe('capture-text-draft-hint')
    expect(draft.getAttribute('aria-describedby')).toBe('capture-text-draft-hint')
    await user.type(draft, '{Escape}')
    expect(screen.queryByTestId('capture-text-draft-hint')).toBeNull()
  })

  it('AC-102.16 one two-line mark traced from the keydowns to the save POST body', async () => {
    const surface = await openShot()
    const draft = await newDraft(surface)
    await user.type(draft, 'Hi{Shift>}{Enter}{/Shift}Hi')
    expect(draftField()?.value, 'onTextDraftChange holds both lines').toBe('Hi\nHi')
    await user.type(draftField() as HTMLElement, '{Enter}')
    expect(draftField(), 'onTextCommit closes the draft').toBeNull()
    expect(textMarks().map((el) => linesOf(el)), 'annotationsRef paints one two-line mark').toEqual([['Hi', 'Hi']])
    await user.click(screen.getByTestId('capture-save'))
    await vi.waitFor(() => {
      expect(annotatePosts()).toHaveLength(1)
    })
    const body = JSON.parse(annotatePosts()[0]?.body ?? '{}') as { annotations: { type: string; text?: string }[] }
    const texts = body.annotations.filter((mark) => mark.type === 'text')
    expect(texts, 'the body holds the mark exactly once').toHaveLength(1)
    expect(texts[0]).toMatchObject({ type: 'text', x: 30, y: 40, text: 'Hi\nHi' })
  })

  it('AC-102.18 a double-click on a saved Hi\\nHi reopens the draft with both lines', async () => {
    const surface = await openShot([textMark('Hi\nHi')])
    await user.click(screen.getByTestId('capture-tool-select'))
    await act(async () => {
      for (let i = 0; i < 2; i += 1) {
        pointer(surface, 'pointerdown', 15, 32)
        pointer(surface, 'pointerup', 15, 32)
      }
      surface.dispatchEvent(new MouseEvent('dblclick', { bubbles: true, cancelable: true, clientX: 15, clientY: 32, detail: 2 }))
    })
    const draft = draftField()
    expect(draft, 'the draft opens').not.toBeNull()
    expect(draft?.tagName).toBe('TEXTAREA')
    expect(draft?.value).toBe('Hi\nHi')
  })

  it('AC-102.24 a click on the second line selects the mark; a click below the last line selects nothing', async () => {
    const surface = await openShot([textMark('Hi\nHi')])
    await user.click(screen.getByTestId('capture-tool-select'))
    const selected = () => document.querySelector('[data-testid="capture-handle-body"]') !== null
    await click(surface, 15, 90)
    expect(selected(), 'below the last line').toBe(false)
    await click(surface, 15, 54)
    expect(selected(), 'inside the second line, outside the first').toBe(true)
  })
})
