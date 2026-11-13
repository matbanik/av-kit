/** @vitest-environment jsdom */
/**
 * MEU-103 capture-redact-mark (Session 68): AC-103.14 to AC-103.22 from the approved plan
 * (docs/execution/plans/2026-11-13-capture-redact). Each test asserts that the name it drives exists before
 * it drives it, so a Red run fails on an assertion, never on a thrown error (Session 62 RULE-3).
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Eraser, EyeOff } from 'lucide-react'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import * as help from '../../src/renderer/src/features/capture/capture-help-content'
import * as hitTest from '../../src/renderer/src/features/capture/capture-hit-test'
import * as toolbar from '../../src/renderer/src/features/capture/capture-toolbar'
import * as transform from '../../src/renderer/src/features/capture/capture-transform'
import { CapturePage } from '../../src/renderer/src/features/capture/CapturePage'

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

type Mark = Record<string, unknown> & { type: string }
type FetchCall = { url: string; method: string; body?: unknown }
type Groups = readonly string[]

const SMART_HINT = 'Smart eraser: Covers an area with the surrounding colour'
const REDACT_ID = 'capture-tool-redact'
const SOLID_ID = 'capture-redact-solid'
const PIXELATE_ID = 'capture-redact-pixelate'
const MODE_ID = 'capture-redact-mode'
const REDACT_BOX = { type: 'redact', x: 1, y: 1, width: 4, height: 3, color: '#000000' }

const SHOT = {
  id: 'shot-1',
  original_path: 'C:/shots/a.png',
  annotated_path: null as string | null,
  sidecar_path: null,
  display_name: 'a.png',
  width: 8,
  height: 8,
  file_size: 32,
  source: 'gui',
  created_at: '2026-08-27T12:00:00Z',
  updated_at: '2026-08-27T12:00:00Z',
}

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
    loginItemGet: async () => ({ supported: false, reason: 'not-packaged', enabled: false, minimized: false }),
    loginItemSet: async () => ({ supported: false, reason: 'not-packaged', enabled: false, minimized: false }),
    onInboxChanged: () => () => undefined,
  }
}

function bindSurface(surface: HTMLElement): void {
  surface.getBoundingClientRect = () =>
    ({ x: 0, y: 0, left: 0, top: 0, right: 200, bottom: 200, width: 200, height: 200, toJSON: () => ({}) }) as DOMRect
}

function dispatchPointer(target: HTMLElement, type: string, clientX: number, clientY: number): void {
  target.dispatchEvent(
    new PointerEvent(type, { bubbles: true, cancelable: true, clientX, clientY, pointerId: 1, pointerType: 'mouse', isPrimary: true }),
  )
}

/** MEU-80 HINT_TIMING: focus shows the hint at once; read `${id}-hint`, then blur. */
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

const rectGeometry = (element: Element | null | undefined) =>
  ['x', 'y', 'width', 'height'].map((name) => Number(element?.getAttribute(name)))
const marksOf = (type: string) => document.querySelectorAll(`[data-annotation-type="${type}"]`)
const isAnnotatePost = (row: FetchCall) => row.method === 'POST' && row.url.includes('/annotate')

describe('MEU-103 capture redact mark', () => {
  let user: ReturnType<typeof userEvent.setup>
  let queryClient: QueryClient
  const fetches: FetchCall[] = []
  let detail: Mark[] = []
  let shotItem = { ...SHOT }

  beforeEach(() => {
    user = userEvent.setup()
    fetches.length = 0
    detail = []
    shotItem = { ...SHOT }
    queryClient = new QueryClient({ defaultOptions: { queries: { retry: false, staleTime: Infinity, gcTime: 0 } } })
    queryClient.setQueryData(['settings', 'capture'], {
      inbox_dir: 'C:/Pictures/av-kit',
      hotkey: 'F2',
      copy_to_clipboard: false,
      close_to_tray: true,
    })
    mockApi()
    URL.createObjectURL = vi.fn(() => 'blob:capture-shot')
    URL.revokeObjectURL = vi.fn()
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = hrefOf(input)
      const method = (init?.method ?? 'GET').toUpperCase()
      const body = typeof init?.body === 'string' && init.body.length > 0 ? JSON.parse(init.body) : undefined
      fetches.push({ url, method, body })
      if (url.includes('/settings/capture')) {
        return jsonResponse(queryClient.getQueryData(['settings', 'capture']))
      }
      if (url.includes('/captures/requests')) {
        return jsonResponse({ items: [] })
      }
      if (url.includes('/image')) {
        return new Response(new Uint8Array([1, 2, 3]), { status: 200, headers: { 'Content-Type': 'image/png' } })
      }
      if (url.includes('/annotate')) {
        return jsonResponse({ ok: true })
      }
      const pathOnly = url.split('?')[0] ?? url
      if (/\/captures\/[^/]+$/.test(pathOnly) && method === 'GET') {
        return jsonResponse({ ...shotItem, annotations: detail })
      }
      if (url.includes('/captures')) {
        return jsonResponse({ items: [shotItem] })
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
    vi.restoreAllMocks()
  })

  async function openSurface(): Promise<HTMLElement> {
    queryClient.setQueryData(['captures'], { items: [shotItem], pendingInteractive: false })
    render(createElement(QueryClientProvider, { client: queryClient }, createElement(CapturePage)))
    await vi.waitFor(() => {
      expect(screen.getAllByTestId('capture-filmstrip-item').length).toBeGreaterThan(0)
    })
    await user.click(screen.getAllByTestId('capture-filmstrip-item')[0] as HTMLElement)
    await vi.waitFor(() => {
      expect(screen.getByTestId('capture-draw-surface').getAttribute('data-overlay-ready')).toBe('true')
    })
    const surface = screen.getByTestId('capture-draw-surface')
    bindSurface(surface)
    return surface
  }

  async function drag(surface: HTMLElement, fromX: number, fromY: number, toX: number, toY: number): Promise<void> {
    await act(async () => {
      dispatchPointer(surface, 'pointerdown', fromX, fromY)
      dispatchPointer(surface, 'pointermove', toX, toY)
      dispatchPointer(surface, 'pointerup', toX, toY)
    })
  }

  async function click(surface: HTMLElement, x: number, y: number): Promise<void> {
    await act(async () => {
      dispatchPointer(surface, 'pointerdown', x, y)
      dispatchPointer(surface, 'pointerup', x, y)
    })
  }

  async function saveBody(): Promise<unknown> {
    const before = fetches.filter(isAnnotatePost).length
    expect(screen.queryByTestId('capture-save'), 'Save is shown for a dirty overlay').not.toBeNull()
    await user.click(screen.getByTestId('capture-save'))
    await vi.waitFor(() => {
      expect(fetches.filter(isAnnotatePost).length).toBe(before + 1)
    })
    const posted = fetches.filter(isAnnotatePost)
    return posted[posted.length - 1]?.body
  }

  /** The Redact button exists and is pressed after a click; the mode control is then on screen. */
  async function pickRedact(): Promise<void> {
    expect(screen.queryByTestId(REDACT_ID), `${REDACT_ID} is in the tools row`).not.toBeNull()
    await user.click(screen.getByTestId(REDACT_ID))
    expect(screen.getByTestId(REDACT_ID).getAttribute('aria-pressed')).toBe('true')
  }

  const radio = (id: string) => screen.getByTestId(id) as HTMLInputElement
  const chip = (name: string) => within(screen.getByTestId('capture-mark-list')).queryByRole('button', { name })

  // ── AC-103.14 REDACT_TOOL ─────────────────────────────────────────────────────────────────────────
  it('AC-103.14 the tool row holds Redact in the Pixelate slot, between Text and Smart eraser; 8 tools', async () => {
    const buttons = toolbar.TOOLBAR_BUTTONS as Record<string, { icon: unknown; name: string }>
    expect(Object.keys(buttons)).toContain(REDACT_ID)
    expect(Object.keys(buttons)).not.toContain('capture-tool-pixelate')
    expect(buttons[REDACT_ID]?.name).toBe('Redact')
    expect(buttons[REDACT_ID]?.icon).toBe(EyeOff)
    const keys = Object.keys(buttons).filter((key) => key.startsWith('capture-tool-'))
    expect(keys.slice(4, 7)).toEqual(['capture-tool-text', REDACT_ID, 'capture-tool-eraser'])
    const ids = toolbar.TOOL_BUTTON_IDS as Record<string, string>
    expect(ids.redact).toBe(REDACT_ID)
    expect(Object.keys(ids)).toEqual(['select', 'arrow', 'box', 'highlight', 'text', 'redact', 'eraser', 'crop'])
    await openSurface()
    const row = screen.getByTestId('capture-chrome-tools')
    const order = Array.from(row.querySelectorAll('button[data-testid^="capture-tool-"]')).map((button) =>
      button.getAttribute('data-testid'),
    )
    const at = order.indexOf(REDACT_ID)
    expect(at, 'the Redact button is rendered').toBeGreaterThan(0)
    expect(order.slice(at - 1, at + 2)).toEqual(['capture-tool-text', REDACT_ID, 'capture-tool-eraser'])
    expect(order).not.toContain('capture-tool-pixelate')
    expect(within(row).getAllByRole('button', { name: 'Redact' })).toHaveLength(1)
  })

  // ── AC-103.15 SMART_ERASER ────────────────────────────────────────────────────────────────────────
  it('AC-103.15 the eraser is named Smart eraser with its hint; its chip and JSON type', async () => {
    const buttons = toolbar.TOOLBAR_BUTTONS as Record<string, { icon: unknown; name: string; hint?: string }>
    expect(buttons['capture-tool-eraser']).toEqual({
      icon: Eraser,
      name: 'Smart eraser',
      hint: 'Covers an area with the surrounding colour',
    })
    const surface = await openSurface()
    const row = screen.getByTestId('capture-chrome-tools')
    const eraser = screen.getByTestId('capture-tool-eraser')
    expect(eraser.getAttribute('aria-label')).toBe('Smart eraser')
    expect(focusedHint(eraser, 'capture-tool-eraser-hint')).toBe(SMART_HINT)
    // Negative: `Eraser` alone names no button in the row.
    expect(within(row).queryAllByRole('button', { name: 'Eraser' })).toHaveLength(0)
    await user.click(eraser)
    await drag(surface, 25, 25, 150, 125)
    expect(marksOf('eraser')).toHaveLength(1)
    expect(chip('Smart eraser 1')).not.toBeNull()
    expect(chip('Eraser 1')).toBeNull()
    expect(await saveBody()).toEqual({ annotations: [{ type: 'eraser', x: 1, y: 1, width: 5, height: 4 }] })
  })

  // ── AC-103.16 drawing under each mode ─────────────────────────────────────────────────────────────
  it('AC-103.16 Redact draws a #000000 redact under Solid (checked on mount) and a pixelate under Pixelate', async () => {
    const surface = await openSurface()
    await pickRedact()
    expect(screen.queryByTestId(MODE_ID), 'the mode control shows for the Redact tool').not.toBeNull()
    expect(radio(SOLID_ID).checked).toBe(true)
    expect(radio(PIXELATE_ID).checked).toBe(false)
    expect(screen.getByTestId(MODE_ID).getAttribute('aria-label')).toBe('Redact mode')
    await drag(surface, 25, 25, 150, 125)
    expect(marksOf('redact')).toHaveLength(1)
    expect(marksOf('pixelate')).toHaveLength(0)
    expect(await saveBody()).toEqual({
      annotations: [{ type: 'redact', x: 1, y: 1, width: 5, height: 4, color: '#000000' }],
    })
    await pickRedact()
    await user.click(radio(PIXELATE_ID))
    expect(radio(PIXELATE_ID).checked).toBe(true)
    expect((screen.getByTestId('capture-block-size') as HTMLInputElement).value).toBe('10')
    await drag(surface, 25, 150, 100, 175)
    expect(marksOf('pixelate')).toHaveLength(1)
    expect(await saveBody()).toEqual({
      annotations: [
        { type: 'redact', x: 1, y: 1, width: 5, height: 4, color: '#000000' },
        { type: 'pixelate', x: 1, y: 6, width: 3, height: 1, block_size: 10 },
      ],
    })
  })

  // ── AC-103.17 MODE_GROUPS ─────────────────────────────────────────────────────────────────────────
  it('AC-103.17 optionGroups follows MODE_GROUPS for the redact tool, selected marks, eraser and crop', () => {
    expect(Object.keys(toolbar.TOOL_BUTTON_IDS)).toContain('redact')
    const groups = toolbar.optionGroups as unknown as (tool: string, selected: unknown, mode?: string) => Groups
    expect(groups.length).toBeGreaterThanOrEqual(2)
    const redact = { ...REDACT_BOX }
    const pixelate = { type: 'pixelate', x: 1, y: 1, width: 4, height: 3, block_size: 10 }
    const eraser = { type: 'eraser', x: 1, y: 1, width: 4, height: 3 }
    const rows: Array<[string, unknown, string | undefined, Groups]> = [
      ['redact', null, 'solid', ['mode']],
      ['redact', null, undefined, ['mode']],
      ['redact', null, 'pixelate', ['mode', 'block']],
      ['select', redact, 'solid', ['mode']],
      ['select', redact, 'pixelate', ['mode']],
      ['select', pixelate, 'solid', ['mode', 'block']],
      ['redact', pixelate, 'solid', ['mode', 'block']],
      ['eraser', null, 'solid', []],
      ['select', eraser, 'pixelate', []],
      ['crop', redact, 'solid', []],
      ['crop', null, 'pixelate', []],
      ['box', null, 'solid', ['color', 'stroke']],
      ['text', null, 'pixelate', ['color', 'text']],
      ['highlight', null, 'solid', ['color']],
    ]
    for (const [tool, selected, mode, want] of rows) {
      const got = mode === undefined ? groups(tool, selected) : groups(tool, selected, mode)
      expect(got, `${tool} / ${String((selected as Mark | null)?.type)} / ${String(mode)}`).toEqual(want)
    }
    // Negative: a selected redact shows no color group.
    expect(groups('select', redact, 'solid')).not.toContain('color')
  })

  // ── AC-103.18 MODE_SWAP ───────────────────────────────────────────────────────────────────────────
  it('AC-103.18 a mode pick swaps the selected mark in place as one undo step; a checked pick is a no-op', async () => {
    const surface = await openSurface()
    await pickRedact()
    await drag(surface, 25, 25, 150, 125)
    expect(marksOf('redact')).toHaveLength(1)
    expect(chip('Redact 1')?.getAttribute('aria-pressed')).toBe('true')
    expect(radio(SOLID_ID).checked).toBe(true)
    // Redact to Pixelate: the same box with the page's block size.
    await user.click(radio(PIXELATE_ID))
    expect(marksOf('redact')).toHaveLength(0)
    expect(marksOf('pixelate')).toHaveLength(1)
    expect(rectGeometry(marksOf('pixelate')[0])).toEqual([1, 1, 5, 4])
    expect(await saveBody()).toEqual({
      annotations: [{ type: 'pixelate', x: 1, y: 1, width: 5, height: 4, block_size: 10 }],
    })
    // Picking the checked mode changes nothing and adds no undo step.
    await user.click(radio(PIXELATE_ID))
    expect(marksOf('pixelate')).toHaveLength(1)
    // One Undo restores the redact; a second Undo removes the drawn mark (the swap was one step).
    await user.click(screen.getByTestId('capture-undo'))
    expect(marksOf('redact')).toHaveLength(1)
    expect(marksOf('pixelate')).toHaveLength(0)
    await user.click(screen.getByTestId('capture-undo'))
    expect(marksOf('redact')).toHaveLength(0)
    await user.click(screen.getByTestId('capture-redo'))
    await user.click(screen.getByTestId('capture-redo'))
    expect(marksOf('pixelate')).toHaveLength(1)
    // Pixelate to Solid gives #000000 on the same box.
    await click(surface, 75, 75)
    expect(chip('Pixelate 1')?.getAttribute('aria-pressed')).toBe('true')
    await user.click(radio(SOLID_ID))
    expect(marksOf('redact')).toHaveLength(1)
    expect(await saveBody()).toEqual({
      annotations: [{ type: 'redact', x: 1, y: 1, width: 5, height: 4, color: '#000000' }],
    })
    // With nothing selected, a pick only sets the mode for the next drawn box. 185 css px maps to pixel 7 of 8
    // (190 rounds to 8, off the image, and is ignored).
    await click(surface, 185, 30)
    await pickRedact()
    expect(chip('Redact 1')?.getAttribute('aria-pressed')).toBe('false')
    await user.click(radio(PIXELATE_ID))
    expect(marksOf('redact')).toHaveLength(1)
    expect(marksOf('pixelate')).toHaveLength(0)
    await drag(surface, 25, 150, 100, 175)
    expect(marksOf('pixelate')).toHaveLength(1)
  })

  // ── AC-103.19 REDACT_HIT ──────────────────────────────────────────────────────────────────────────
  it('AC-103.19 a redact is a box mark: a click inside selects it, its se handle resizes it, chip Redact 1', async () => {
    const label = hitTest.markLabel as unknown as (mark: unknown, index: number) => string
    expect(label(REDACT_BOX, 0)).toBe('Redact 1')
    expect(label({ type: 'eraser', x: 0, y: 0, width: 1, height: 1 }, 1)).toBe('Smart eraser 2')
    const isBox = transform.isBoxMark as unknown as (mark: unknown) => boolean
    expect(isBox(REDACT_BOX)).toBe(true)
    const surface = await openSurface()
    await pickRedact()
    // At the 25 px/px fit, 25,25 → 100,100 covers image (1,1)-(4,4); its se handle sits at CSS (100,100).
    await drag(surface, 25, 25, 100, 100)
    expect(rectGeometry(marksOf('redact')[0])).toEqual([1, 1, 3, 3])
    expect(chip('Redact 1')?.getAttribute('aria-pressed')).toBe('true')
    await drag(surface, 100, 100, 150, 175)
    expect(rectGeometry(marksOf('redact')[0])).toEqual([1, 1, 5, 6])
    // Negative: a click on empty image outside the box (185,30 maps to pixel 7,1) deselects it; a click
    // inside selects it again.
    await click(surface, 185, 30)
    expect(chip('Redact 1')?.getAttribute('aria-pressed')).toBe('false')
    await click(surface, 75, 75)
    expect(chip('Redact 1')?.getAttribute('aria-pressed')).toBe('true')
  })

  // ── AC-103.20 REDACT_OUTLINE ──────────────────────────────────────────────────────────────────────
  it('AC-103.20 redact and pixelate marks have a dashed outline in Original and none in Annotated', async () => {
    // The Pillow half (no outline pixel in a bake) is test_ac_103_8_region_pass_fills_the_redact_box.
    detail = [
      { ...REDACT_BOX },
      { type: 'pixelate', x: 5, y: 1, width: 2, height: 2, block_size: 2 },
      { type: 'eraser', x: 1, y: 5, width: 2, height: 2 },
    ]
    shotItem = { ...SHOT, annotated_path: 'C:/shots/a.annotated.png' }
    await openSurface()
    expect(marksOf('redact'), 'the loaded redact is drawn').toHaveLength(1)
    for (const type of ['redact', 'pixelate']) {
      const mark = marksOf(type)[0] as Element
      expect(mark.getAttribute('fill'), type).toBe('none')
      expect(mark.getAttribute('stroke-dasharray'), `${type} dashed`).not.toBeNull()
      expect(mark.getAttribute('stroke'), `${type} stroke`).not.toBe('none')
    }
    // Negative: the eraser's element has no dashed outline.
    expect(marksOf('eraser')[0]?.getAttribute('stroke-dasharray')).toBeNull()
    await user.click(screen.getByTestId('capture-view-annotated'))
    expect(document.querySelectorAll('[data-testid="capture-annotation"][stroke-dasharray]')).toHaveLength(0)
  })

  // ── AC-103.21 REDACT_PREVIEW in the editor ────────────────────────────────────────────────────────
  it('AC-103.21 the region layer shows the redact colour inside its box during and after a drag', async () => {
    // A fake 2D context: the layer is an 8 by 8 RGBA buffer; the source image is opaque grey.
    const layer = new Uint8ClampedArray(8 * 8 * 4)
    const context = {
      drawImage: () => undefined,
      getImageData: (_x: number, _y: number, w: number, h: number) => ({
        width: w,
        height: h,
        data: new Uint8ClampedArray(w * h * 4).fill(200),
      }),
      clearRect: () => {
        layer.fill(0)
      },
      createImageData: (w: number, h: number) => ({ width: w, height: h, data: new Uint8ClampedArray(w * h * 4) }),
      putImageData: (
        work: { width: number; data: Uint8ClampedArray },
        dx: number,
        dy: number,
        sx: number,
        sy: number,
        sw: number,
        sh: number,
      ) => {
        for (let y = sy; y < sy + sh; y += 1) {
          for (let x = sx; x < sx + sw; x += 1) {
            const from = (y * work.width + x) * 4
            const to = ((dy + y) * 8 + dx + x) * 4
            layer.set(work.data.subarray(from, from + 4), to)
          }
        }
      },
    }
    vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockImplementation(
      () => context as unknown as CanvasRenderingContext2D,
    )
    const surface = await openSurface()
    const image = screen.getByTestId('capture-viewport-image')
    Object.defineProperty(image, 'naturalWidth', { value: 8 })
    Object.defineProperty(image, 'naturalHeight', { value: 8 })
    fireEvent.load(image)
    const pixel = (x: number, y: number) => Array.from(layer.subarray((y * 8 + x) * 4, (y * 8 + x) * 4 + 4))
    await pickRedact()
    await act(async () => {
      dispatchPointer(surface, 'pointerdown', 25, 25)
      dispatchPointer(surface, 'pointermove', 150, 125)
    })
    expect(pixel(2, 2), 'during the drag').toEqual([0, 0, 0, 255])
    await act(async () => {
      dispatchPointer(surface, 'pointerup', 150, 125)
    })
    expect(marksOf('redact')).toHaveLength(1)
    for (const [x, y] of [
      [1, 1],
      [5, 4],
      [3, 2],
    ] as const) {
      expect(pixel(x, y), `inside (${x},${y})`).toEqual([0, 0, 0, 255])
    }
    // Outside the box the layer stays transparent.
    expect(pixel(0, 0)[3]).toBe(0)
    expect(pixel(6, 5)[3]).toBe(0)
  })

  // ── AC-103.22 REDACT_HELP ─────────────────────────────────────────────────────────────────────────
  it('AC-103.22 the help body names Redact with its Solid default and Pixelate mode, and Smart eraser', () => {
    const sections = help.CAPTURE_HELP_SECTIONS
    const tools = sections.find((item) => item.id === 'four-tools')
    expect(tools).toBeDefined()
    const body = tools?.body ?? ''
    expect(body).toMatch(/\bRedact\b/)
    expect(body).toMatch(/Redact[^.]*\bSolid\b[^.]*\bdefault\b/)
    expect(body).toMatch(/Redact[^.]*\bPixelate\b/)
    expect(body).toContain('Smart eraser')
    expect(body).toMatch(/Drag a square handle on a selected [^.]*\bredact\b[^.]* mark to resize it\./)
    // Negative: the old sentence is gone.
    expect(body).not.toContain('Pixelate and Eraser change the pixels under them')
  })
})
