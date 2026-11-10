/** @vitest-environment jsdom */

// MEU-131 (Session 60) Crop tool on the Capture page: AC-131.11 to AC-131.22.
// The harness is copied from capture-page.behavior.test.ts:1-190 (PointerEvent polyfill, hrefOf,
// jsonResponse, mockApi, the surface binding and the hint reader) with a 400×200 shot and a stubbed
// fetch that records each request. No image leaves the test: /image answers three bytes.
// Every crop element is looked up with queryByTestId and asserted present before use, so a Red
// run fails by assertion (red-check.py).

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ArrowLeftRight, Crop } from 'lucide-react'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import type { Annotation } from '../../src/renderer/src/features/capture/capture-annotate'
import {
  ACTION_BUTTONS,
  CROP_BUTTONS,
  TOOLBAR_BUTTONS,
  TOOL_BUTTON_IDS,
  optionGroups,
} from '../../src/renderer/src/features/capture/capture-toolbar'
import { CapturePage } from '../../src/renderer/src/features/capture/CapturePage'
import type { CaptureTool } from '../../src/renderer/src/features/capture/CaptureViewport'
import { queryClient as appQueryClient } from '../../src/renderer/src/lib/query-client'

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
  return new Response(JSON.stringify(payload), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
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
    getSetupReadiness: async () => ({
      descriptorPresent: true,
      portOk: true,
      modelsDirWritable: true,
    }),
    getMcpAccessStatus: async () => ({ tokenPresent: true }),
    captureRegion: async () => undefined,
    getHotkeyStatus: async () => ({ accelerator: 'F2', registered: true, inUse: false }),
    loginItemGet: async () => ({
      supported: false,
      reason: 'not-packaged',
      enabled: false,
      minimized: false,
    }),
    loginItemSet: async () => ({
      supported: false,
      reason: 'not-packaged',
      enabled: false,
      minimized: false,
    }),
    onInboxChanged: () => () => undefined,
  }
}

/**
 * The surface's client rect. 400×200 maps the 400×200 shot at view scale 1 with no offset; 200×200 maps it
 * at 0.5 with a 50 px top offset (xMidYMid meet).
 */
function bindSurface(surface: HTMLElement, width: number, height: number): void {
  surface.getBoundingClientRect = () =>
    ({
      x: 0,
      y: 0,
      left: 0,
      top: 0,
      right: width,
      bottom: height,
      width,
      height,
      toJSON: () => ({}),
    }) as DOMRect
}

/** MEU-80 HINT_TIMING: focus shows the hint at once; reads `hintId`'s text, then blurs. */
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
function toolbarFocusTarget(id: string): HTMLElement {
  const button = present<HTMLButtonElement>(id)
  return button.disabled ? present(`${id}-tip`) : button
}

function hintOf(id: string): string | null {
  return focusedHint(toolbarFocusTarget(id), `${id}-hint`)
}

/** Every crop element is asserted present before use, so a missing one fails by assertion. */
function present<T extends HTMLElement = HTMLElement>(id: string): T {
  const node = screen.queryByTestId(id)
  expect(node, `${id} rendered`).not.toBeNull()
  return node as T
}

function dispatchPointer(target: HTMLElement, type: string, clientX: number, clientY: number, shiftKey = false): void {
  target.dispatchEvent(
    new PointerEvent(type, {
      bubbles: true,
      cancelable: true,
      clientX,
      clientY,
      shiftKey,
      pointerId: 1,
      pointerType: 'mouse',
      isPrimary: true,
    }),
  )
}

/** A down, each move in turn and an up, in client px. */
async function drag(surface: HTMLElement, points: Array<[number, number]>, shiftKey = false): Promise<void> {
  const [first, ...rest] = points as [[number, number], ...Array<[number, number]>]
  const last = rest[rest.length - 1] ?? first
  await act(async () => {
    dispatchPointer(surface, 'pointerdown', first[0], first[1], shiftKey)
    for (const [x, y] of rest) {
      dispatchPointer(surface, 'pointermove', x, y, shiftKey)
    }
    dispatchPointer(surface, 'pointerup', last[0], last[1], shiftKey)
  })
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

function shot(id: string, name: string, width: number, height: number, hour: number): Shot {
  const stamp = `2026-11-10T${String(hour).padStart(2, '0')}:00:00Z`
  return {
    id,
    original_path: `C:/shots/${name}`,
    annotated_path: null,
    sidecar_path: null,
    display_name: name,
    width,
    height,
    file_size: 32,
    source: 'gui',
    created_at: stamp,
    updated_at: stamp,
  }
}

const LAND = shot('land-1', 'land.png', 400, 200, 12)
const SPACED = shot('shot one', 'spaced.png', 400, 200, 11)
const OTHER = shot('other-1', 'other.png', 400, 200, 10)
const NARROW = shot('narrow-1', 'narrow.png', 5, 300, 9)
const TINY = shot('tiny-1', 'tiny.png', 8, 8, 8)
const STRIP = shot('strip-1', 'strip.png', 400, 10, 7)
const BAKED = { ...shot('baked-1', 'baked.png', 400, 200, 6), annotated_path: 'C:/shots/baked.annotated.png' }

const SAVED_RECT = { type: 'rect', x: 10, y: 10, width: 40, height: 40, color: '#ff0000', stroke_width: 2 }

const CROP_REASON = 'Finish or cancel the crop first'

describe('MEU-131 capture crop tool', () => {
  let user: ReturnType<typeof userEvent.setup>
  let queryClient: QueryClient
  let items: Shot[] = []
  let marks: Record<string, unknown[]> = {}
  let cropError: { status: number; message: string } | null = null
  let cropHold = false
  let cropRelease: Array<() => void> = []
  /** The marks the server carries onto a crop's copy (Session 59 keeps those that fit); none by default. */
  let copyMarks: unknown[] | null = null
  const calls: Array<{ url: string; method: string; body?: unknown }> = []

  function cropPosts(): Array<{ url: string; method: string; body?: unknown }> {
    return calls.filter((call) => call.method === 'POST' && /\/crop$/.test(call.url.split('?')[0] ?? call.url))
  }

  beforeEach(() => {
    user = userEvent.setup()
    calls.length = 0
    items = [LAND, SPACED, OTHER]
    marks = {}
    cropError = null
    cropHold = false
    cropRelease = []
    copyMarks = null
    // capture-commands refreshes the app's QUERY_KEY client, so the page renders with that client.
    queryClient = appQueryClient
    queryClient.setQueryData(['settings', 'capture'], {
      inbox_dir: 'C:/shots',
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
      calls.push({ url, method, body })
      const path = url.split('?')[0] ?? url
      if (path.includes('/settings/capture')) {
        return jsonResponse(queryClient.getQueryData(['settings', 'capture']))
      }
      if (path.includes('/captures/requests')) {
        return jsonResponse({ items: [] })
      }
      if (path.endsWith('/image')) {
        return new Response(new Uint8Array([1, 2, 3]), { status: 200, headers: { 'Content-Type': 'image/png' } })
      }
      const crop = path.match(/\/captures\/([^/]+)\/crop$/)
      if (crop && method === 'POST') {
        if (cropHold) {
          await new Promise<void>((resolve) => {
            cropRelease.push(resolve)
          })
        }
        if (cropError !== null) {
          return jsonResponse(
            { error: { code: 'capture_crop_failed', message: cropError.message, details: null } },
            cropError.status,
          )
        }
        const sourceId = decodeURIComponent(crop[1] as string)
        const source = items.find((row) => row.id === sourceId) as Shot
        const box = body as { width: number; height: number }
        const stem = source.display_name.replace(/\.[^.]+$/, '')
        const made: Shot = {
          ...source,
          id: `${source.id}-crop`,
          original_path: `C:/shots/${stem}-crop.png`,
          annotated_path: null,
          display_name: `${stem}-crop.png`,
          width: box.width,
          height: box.height,
          created_at: '2026-11-10T13:00:00Z',
          updated_at: '2026-11-10T13:00:00Z',
        }
        items = [made, ...items]
        if (copyMarks !== null) {
          marks[made.id] = copyMarks
        }
        return jsonResponse({ item: made, source_id: source.id, clamped: false }, 201)
      }
      const annotate = path.match(/\/captures\/([^/]+)\/annotate$/)
      if (annotate && method === 'POST') {
        marks[decodeURIComponent(annotate[1] as string)] = (body as { annotations?: unknown[] }).annotations ?? []
        return jsonResponse({ ok: true })
      }
      const detail = path.match(/\/captures\/([^/]+)$/)
      if (detail && method === 'GET') {
        const id = decodeURIComponent(detail[1] as string)
        const row = items.find((item) => item.id === id)
        return jsonResponse({ ...row, annotations: marks[id] ?? [], backup_path: null })
      }
      if (/\/captures\/?$/.test(path)) {
        return jsonResponse({ items })
      }
      return jsonResponse({})
    })
    vi.stubGlobal('fetch', fetchMock)
    window.fetch = fetchMock as typeof window.fetch
  })

  afterEach(() => {
    for (const release of cropRelease) {
      release()
    }
    cleanup()
    queryClient.clear()
    vi.unstubAllGlobals()
  })

  /** Renders the page on `items`, selects the shot named `name` and binds the surface. */
  async function open(name: string, rect: [number, number] = [400, 200]): Promise<HTMLElement> {
    queryClient.setQueryData(['captures'], { items: [...items], pendingInteractive: false })
    render(createElement(QueryClientProvider, { client: queryClient }, createElement(CapturePage)))
    await vi.waitFor(() => {
      expect(screen.getAllByTestId('capture-filmstrip-item').length).toBe(items.length)
    })
    await select(name)
    const surface = screen.getByTestId('capture-draw-surface')
    bindSurface(surface, rect[0], rect[1])
    return surface
  }

  async function select(name: string): Promise<void> {
    const thumb = screen
      .getAllByTestId('capture-filmstrip-item')
      .find((node) => node.textContent?.includes(name))
    expect(thumb, `thumb ${name}`).toBeDefined()
    await user.click(thumb as HTMLElement)
    await vi.waitFor(() => {
      expect(screen.getByTestId('capture-shot-info').textContent).toContain(name)
      expect(screen.getByTestId('capture-draw-surface').getAttribute('data-overlay-ready')).toBe('true')
    })
  }

  /** Clicks Crop and asserts the bar shows. */
  async function openCrop(): Promise<void> {
    await user.click(present('capture-tool-crop'))
    expect(screen.queryByTestId('capture-crop-bar'), 'the crop bar opens').not.toBeNull()
  }

  function fields(): number[] {
    return (['x', 'y', 'w', 'h'] as const).map((key) => Number(present<HTMLInputElement>(`capture-crop-${key}`).value))
  }

  function aspect(): HTMLSelectElement {
    return present<HTMLSelectElement>('capture-crop-aspect')
  }

  function pressed(id: string): string | null {
    return present(id).getAttribute('aria-pressed')
  }

  function focusSurface(): void {
    act(() => {
      screen.getByTestId('capture-draw-surface').focus()
    })
  }

  function blurAll(): void {
    act(() => {
      ;(document.activeElement as HTMLElement | null)?.blur()
    })
  }

  function rects(): string[] {
    return Array.from(document.querySelectorAll('[data-testid="capture-annotation"]')).map((node) =>
      ['x', 'y', 'width', 'height'].map((key) => node.getAttribute(key)).join(','),
    )
  }

  async function drawBox(surface: HTMLElement): Promise<void> {
    await user.click(screen.getByTestId('capture-tool-box'))
    await drag(surface, [
      [60, 60],
      [120, 120],
    ])
  }

  async function save(): Promise<void> {
    await user.click(screen.getByTestId('capture-save'))
    await vi.waitFor(() => {
      expect(screen.queryByTestId('capture-save')).toBeNull()
    })
  }

  it('AC-131.11 CROP_ENTRY: after the lock, outside the tool group; opens on the whole image, Free, Original', async () => {
    items = [BAKED, LAND]
    await open('baked.png')
    const tools = screen.getByTestId('capture-chrome-tools')
    const lockTip = present('capture-tool-lock-tip')
    const cropTip = present('capture-tool-crop-tip')
    expect(lockTip.nextElementSibling, 'Crop sits straight after the lock').toBe(cropTip)
    expect(cropTip.nextElementSibling?.getAttribute('aria-label'), 'then the History group').toBe('History')
    expect(tools.querySelector('[role="group"][aria-label="Annotation tool"] [data-testid="capture-tool-crop"]')).toBeNull()
    expect(hintOf('capture-tool-crop')).toBe('Crop')
    expect(present('capture-tool-crop').hasAttribute('aria-keyshortcuts')).toBe(false)
    await user.click(present('capture-view-annotated'))
    expect(pressed('capture-view-annotated')).toBe('true')
    await user.click(present('capture-tool-crop'))
    expect(pressed('capture-tool-crop')).toBe('true')
    const bar = present('capture-crop-bar')
    expect(bar.getAttribute('role')).toBe('group')
    expect(bar.getAttribute('aria-label')).toBe('Crop')
    expect(present('capture-chrome-options').contains(bar), 'the bar replaces the options').toBe(true)
    expect(screen.queryByTestId('capture-color')).toBeNull()
    expect(fields()).toEqual([0, 0, 400, 200])
    expect(aspect().value).toBe('free')
    expect(pressed('capture-view-original')).toBe('true')
  })

  it('AC-131.11 CROP_ENTRY: with no shot Crop is disabled with Select a shot first', async () => {
    items = []
    queryClient.setQueryData(['captures'], { items: [], pendingInteractive: false })
    render(createElement(QueryClientProvider, { client: queryClient }, createElement(CapturePage)))
    await vi.waitFor(() => {
      expect(screen.getByTestId('capture-page')).toBeTruthy()
    })
    expect(present<HTMLButtonElement>('capture-tool-crop').disabled).toBe(true)
    expect(hintOf('capture-tool-crop')).toBe('Crop — Select a shot first')
  })

  it('AC-131.12 CROP_UNSAVED_GATE: unsaved marks and a too-small shot disable Crop; Save and Undo free it', async () => {
    items = [LAND, NARROW]
    const surface = await open('land.png')
    await drawBox(surface)
    expect(present<HTMLButtonElement>('capture-tool-crop').disabled, 'dirty disables Crop').toBe(true)
    expect(hintOf('capture-tool-crop')).toBe('Crop — Save or discard your marks first')
    fireEvent.click(present('capture-tool-crop'))
    expect(screen.queryByTestId('capture-crop-bar')).toBeNull()
    await save()
    expect(present<HTMLButtonElement>('capture-tool-crop').disabled).toBe(false)
    await openCrop()
    await user.click(present('capture-crop-cancel'))
    expect(screen.queryByTestId('capture-crop-bar')).toBeNull()
    await drawBox(surface)
    expect(present<HTMLButtonElement>('capture-tool-crop').disabled).toBe(true)
    await user.click(screen.getByTestId('capture-undo'))
    expect(screen.queryByTestId('capture-save')).toBeNull()
    expect(present<HTMLButtonElement>('capture-tool-crop').disabled, 'back to the saved marks').toBe(false)
    await openCrop()
    await user.click(present('capture-crop-cancel'))
    await select('narrow.png')
    expect(present<HTMLButtonElement>('capture-tool-crop').disabled).toBe(true)
    expect(hintOf('capture-tool-crop')).toBe('Crop — Too small to crop: each side needs 8 px')
    fireEvent.click(present('capture-tool-crop'))
    expect(screen.queryByTestId('capture-crop-bar')).toBeNull()
  })

  it('AC-131.13 CROP_POINTER at view scale 1: handle, inside, outside and Shift drags reach the crop, never a mark', async () => {
    marks[LAND.id] = [SAVED_RECT]
    const surface = await open('land.png')
    const before = rects()
    expect(before).toHaveLength(1)
    await user.click(present('capture-tool-crop'))
    await drag(surface, [
      [400, 200],
      [350, 170],
      [300, 150],
    ])
    expect(fields(), 'se handle').toEqual([0, 0, 300, 150])
    await drag(surface, [
      [100, 50],
      [130, 60],
      [150, 80],
    ])
    expect(fields(), 'inside moves').toEqual([50, 30, 300, 150])
    await drag(surface, [
      [380, 190],
      [370, 100],
      [360, 5],
    ])
    expect(fields(), 'outside draws').toEqual([360, 5, 20, 185])
    expect(rects(), 'no mark added or moved').toEqual(before)
    expect(screen.queryByTestId('capture-remove-mark'), 'no mark selected').toBeNull()
    expect(screen.queryByTestId('capture-save'), 'the overlay stays clean').toBeNull()
  })

  it('AC-131.13 CROP_POINTER: a Shift se drag keeps the start ratio', async () => {
    const surface = await open('land.png')
    await openCrop()
    await drag(
      surface,
      [
        [400, 200],
        [300, 190],
      ],
      true,
    )
    expect(fields(), 'Shift keeps 2:1').toEqual([0, 0, 300, 150])
    expect(rects()).toEqual([])
  })

  it('AC-131.13 CROP_POINTER at view scale 0.5: the same drags give the same image-px boxes', async () => {
    marks[LAND.id] = [SAVED_RECT]
    const surface = await open('land.png', [200, 200])
    const before = rects()
    await openCrop()
    // image (x, y) sits at client (x / 2, 50 + y / 2)
    await drag(surface, [
      [200, 150],
      [175, 135],
      [150, 125],
    ])
    expect(fields(), 'se handle').toEqual([0, 0, 300, 150])
    await drag(surface, [
      [50, 75],
      [75, 90],
    ])
    expect(fields(), 'inside moves').toEqual([50, 30, 300, 150])
    await drag(surface, [
      [190, 145],
      [180, 53],
    ])
    expect(fields(), 'outside draws').toEqual([360, 6, 20, 184])
    expect(rects()).toEqual(before)
    expect(screen.queryByTestId('capture-remove-mark')).toBeNull()
  })

  it('AC-131.14 CROP_LOOK: the dim holds the box, thirds only while dragging, the readout holds through zoom', async () => {
    const surface = await open('land.png')
    await openCrop()
    const overlay = present('capture-crop-overlay')
    expect(overlay.getAttribute('class') ?? '').toContain('pointer-events-none')
    const dim = present('capture-crop-dim')
    expect(dim.getAttribute('fill-rule')).toBe('evenodd')
    expect(dim.getAttribute('d')).toBe('M0 0H400V200H0Z M0 0H400V200H0Z')
    expect(document.querySelectorAll('[data-testid="capture-crop-handle"]')).toHaveLength(8)
    expect(screen.queryByTestId('capture-crop-thirds'), 'no thirds at rest').toBeNull()
    await act(async () => {
      dispatchPointer(surface, 'pointerdown', 400, 200)
      dispatchPointer(surface, 'pointermove', 300, 150)
    })
    expect(screen.queryByTestId('capture-crop-thirds'), 'thirds while dragging').not.toBeNull()
    await act(async () => {
      dispatchPointer(surface, 'pointerup', 300, 150)
    })
    expect(screen.queryByTestId('capture-crop-thirds'), 'no thirds after up').toBeNull()
    expect(present('capture-crop-dim').getAttribute('d')).toBe('M0 0H400V200H0Z M0 0H300V150H0Z')
    const outline = present('capture-crop-outline')
    expect(['x', 'y', 'width', 'height'].map((key) => outline.getAttribute(key))).toEqual(['0', '0', '300', '150'])
    expect(present('capture-crop-size').textContent).toBe('300 × 150 px')
    await user.click(present('capture-crop-reset'))
    expect(present('capture-crop-size').textContent).toBe('400 × 200 px')
    await user.click(present('capture-zoom-in'))
    expect(present('capture-crop-size').textContent).toBe('400 × 200 px')
    await user.click(present('capture-zoom-out'))
    expect(present('capture-crop-size').textContent).toBe('400 × 200 px')
  })

  it('AC-131.15 CROP_BAR aspect: presets in order, Square, 16:9 and its swap, X, the hint', async () => {
    await open('land.png')
    await openCrop()
    const select = aspect()
    expect(Array.from(select.options).map((option) => option.textContent)).toEqual([
      'Free',
      'Original',
      'Square',
      '16:9',
      '4:3',
      '3:2',
    ])
    await user.selectOptions(select, 'square')
    expect(fields(), 'Square').toEqual([100, 0, 200, 200])
    await user.selectOptions(aspect(), '16:9')
    expect(fields(), '16:9').toEqual([22, 0, 356, 200])
    expect(hintOf('capture-crop-swap')).toBe('Swap portrait and landscape (X)')
    expect(present('capture-crop-swap').getAttribute('aria-keyshortcuts')).not.toBeNull()
    await user.click(present('capture-crop-swap'))
    expect(fields(), '9:16').toEqual([144, 1, 112, 199])
    focusSurface()
    await user.keyboard('x')
    expect(fields(), 'X swaps back').toEqual([22, 0, 356, 200])
    expect(screen.queryByTestId('capture-crop-bar')).not.toBeNull()
  })

  it('AC-131.15 CROP_BAR aspect: an 8×8 shot disables the wide presets; a 400×10 shot cannot swap 16:9', async () => {
    items = [TINY, STRIP]
    await open('tiny.png')
    await openCrop()
    const disabled = Array.from(aspect().options)
      .filter((option) => option.disabled)
      .map((option) => option.value)
    expect(disabled).toEqual(['16:9', '4:3', '3:2'])
    await user.click(present('capture-crop-cancel'))
    await select('strip.png')
    bindSurface(screen.getByTestId('capture-draw-surface'), 400, 10)
    await openCrop()
    await user.selectOptions(aspect(), '16:9')
    expect(fields()).toEqual([191, 0, 18, 10])
    expect(present<HTMLButtonElement>('capture-crop-swap').disabled).toBe(true)
    expect(hintOf('capture-crop-swap')).toBe('Swap portrait and landscape (X) — Too small to swap this ratio')
    focusSurface()
    await user.keyboard('x')
    expect(fields(), 'X does nothing').toEqual([191, 0, 18, 10])
  })

  it('AC-131.16 CROP_BAR fields: Enter applies, bad text and Esc revert, arrows step; surface arrows nudge', async () => {
    await open('land.png')
    await openCrop()
    const width = present<HTMLInputElement>('capture-crop-w')
    expect(width.getAttribute('inputmode')).toBe('numeric')
    await user.clear(width)
    await user.type(width, '150{Enter}')
    expect(fields(), 'W 150').toEqual([0, 0, 150, 200])
    await user.clear(present('capture-crop-w'))
    await user.type(present('capture-crop-w'), 'abc{Enter}')
    expect(present<HTMLInputElement>('capture-crop-w').value, 'abc reverts').toBe('150')
    await user.clear(present('capture-crop-w'))
    await user.type(present('capture-crop-w'), '99{Escape}')
    expect(present<HTMLInputElement>('capture-crop-w').value, 'Esc reverts the field').toBe('150')
    expect(screen.queryByTestId('capture-crop-bar'), 'Esc in a field keeps the crop open').not.toBeNull()
    await user.keyboard('{ArrowUp}')
    expect(fields(), 'ArrowUp adds 1').toEqual([0, 0, 151, 200])
    await user.keyboard('{Shift>}{ArrowUp}{/Shift}')
    expect(fields(), 'Shift+ArrowUp adds 10').toEqual([0, 0, 161, 200])
    focusSurface()
    await user.keyboard('{ArrowRight}')
    expect(fields(), 'surface arrow').toEqual([1, 0, 161, 200])
    await user.keyboard('{Shift>}{ArrowRight}{/Shift}')
    expect(fields(), 'surface Shift+arrow').toEqual([11, 0, 161, 200])
    expect(cropPosts()).toHaveLength(0)
  })

  it('AC-131.17 CROP_COMMIT by Save as copy: one encoded POST with the integer box; the copy is selected and named', async () => {
    const surface = await open('spaced.png')
    expect(pressed('capture-tool-arrow')).toBe('true')
    await openCrop()
    await drag(surface, [
      [400, 200],
      [300, 150],
    ])
    await user.click(present('capture-crop-save'))
    await vi.waitFor(() => {
      expect(screen.queryByTestId('capture-crop-bar'), 'the crop closes').toBeNull()
    })
    const posts = cropPosts()
    expect(posts).toHaveLength(1)
    expect(new URL((posts[0] as { url: string }).url).pathname).toBe('/api/v1/captures/shot%20one/crop')
    const body = (posts[0] as { body: Record<string, number> }).body
    expect(body).toEqual({ x: 0, y: 0, width: 300, height: 150 })
    expect(Object.values(body).every((value) => Number.isInteger(value))).toBe(true)
    await vi.waitFor(() => {
      const current = document.querySelector('[data-testid="capture-filmstrip-item"][aria-current="true"]')
      expect(current?.textContent ?? '').toContain('spaced-crop.png')
      expect(screen.getByTestId('capture-status').textContent).toBe('Saved crop as spaced-crop.png.')
    })
    const names = screen.getAllByTestId('capture-filmstrip-item').map((node) => node.textContent ?? '')
    expect(names.some((name) => name.includes('spaced.png')), 'the source stays').toBe(true)
    expect(pressed('capture-tool-arrow'), 'the prior tool returns').toBe('true')
    expect(pressed('capture-tool-crop')).toBe('false')
  })

  it('AC-131.18 CROP_COMMIT by double-click inside the box and by Enter; outside sends none; Enter twice sends one', async () => {
    const surface = await open('land.png')
    await openCrop()
    await drag(surface, [
      [400, 200],
      [300, 150],
    ])
    act(() => {
      fireEvent.doubleClick(surface, { clientX: 350, clientY: 180 })
    })
    expect(cropPosts(), 'a double-click outside the box sends none').toHaveLength(0)
    expect(screen.queryByTestId('capture-crop-bar')).not.toBeNull()
    await act(async () => {
      fireEvent.doubleClick(surface, { clientX: 100, clientY: 50 })
    })
    await vi.waitFor(() => {
      expect(screen.queryByTestId('capture-crop-bar')).toBeNull()
    })
    expect(cropPosts(), 'a double-click inside the box').toHaveLength(1)
    await select('other.png')
    bindSurface(screen.getByTestId('capture-draw-surface'), 400, 200)
    await openCrop()
    focusSurface()
    await user.keyboard('{Enter}')
    await vi.waitFor(() => {
      expect(screen.queryByTestId('capture-crop-bar')).toBeNull()
    })
    expect(cropPosts(), 'Enter commits').toHaveLength(2)
    await select('land.png')
    bindSurface(screen.getByTestId('capture-draw-surface'), 400, 200)
    await openCrop()
    cropHold = true
    focusSurface()
    await user.keyboard('{Enter}')
    await user.keyboard('{Enter}')
    await vi.waitFor(() => {
      expect(cropPosts()).toHaveLength(3)
    })
    await act(async () => {
      for (const release of cropRelease.splice(0)) {
        release()
      }
    })
    await vi.waitFor(() => {
      expect(screen.queryByTestId('capture-crop-bar')).toBeNull()
    })
    expect(cropPosts(), 'Enter twice while pending sends one').toHaveLength(3)
  })

  it('AC-131.18 CROP_COMMIT by Enter straight after opening Crop, by mouse or by keyboard: one POST each', async () => {
    await open('land.png')
    await openCrop()
    await user.keyboard('{Enter}')
    await vi.waitFor(() => {
      expect(screen.queryByTestId('capture-crop-bar')).toBeNull()
    })
    expect(cropPosts(), 'Enter after a mouse click on Crop commits').toHaveLength(1)
    await select('other.png')
    bindSurface(screen.getByTestId('capture-draw-surface'), 400, 200)
    act(() => {
      present('capture-tool-crop').focus()
    })
    await user.keyboard('{Enter}')
    expect(screen.queryByTestId('capture-crop-bar'), 'Enter on Crop opens it').not.toBeNull()
    await user.keyboard('{Enter}')
    await vi.waitFor(() => {
      expect(screen.queryByTestId('capture-crop-bar')).toBeNull()
    })
    expect(cropPosts(), 'a second Enter after keyboard entry commits').toHaveLength(2)
    expect(new URL((cropPosts()[1] as { url: string }).url).pathname).toBe('/api/v1/captures/other-1/crop')
  })

  it('AC-131.17 CROP_COMMIT: a copy that carries marks keeps the tool the crop opened from', async () => {
    copyMarks = [SAVED_RECT]
    await open('land.png')
    expect(pressed('capture-tool-arrow')).toBe('true')
    await openCrop()
    await user.click(present('capture-crop-save'))
    await vi.waitFor(() => {
      expect(screen.getByTestId('capture-status').textContent).toBe('Saved crop as land-crop.png.')
      expect(screen.getByTestId('capture-draw-surface').getAttribute('data-overlay-ready')).toBe('true')
      expect(rects(), 'the carried rect shows on the copy').toEqual(['10,10,40,40'])
    })
    expect(cropPosts()).toHaveLength(1)
    expect(pressed('capture-tool-arrow'), 'the prior tool survives the copy load').toBe('true')
    expect(pressed('capture-tool-select')).toBe('false')
    expect(pressed('capture-tool-crop')).toBe('false')
  })

  it('AC-131.19 CROP_ERRORS: Cropping… while pending; a 409 and a 422 keep the crop open with their messages', async () => {
    const surface = await open('land.png')
    await openCrop()
    await drag(surface, [
      [400, 200],
      [300, 150],
    ])
    cropError = { status: 409, message: 'A file named land-crop.png already exists.' }
    cropHold = true
    await user.click(present('capture-crop-save'))
    await vi.waitFor(() => {
      expect(present('capture-crop-save').getAttribute('aria-busy')).toBe('true')
    })
    expect(present<HTMLButtonElement>('capture-crop-save').disabled).toBe(true)
    expect(screen.getByTestId('capture-status').textContent).toBe('Cropping…')
    await act(async () => {
      for (const release of cropRelease.splice(0)) {
        release()
      }
    })
    await vi.waitFor(() => {
      expect(screen.getByTestId('capture-status').textContent).toContain('A file named land-crop.png already exists.')
    })
    expect(screen.queryByTestId('capture-crop-bar'), '409 keeps the crop open').not.toBeNull()
    expect(fields()).toEqual([0, 0, 300, 150])
    expect(present<HTMLButtonElement>('capture-crop-save').disabled).toBe(false)
    expect(present('capture-crop-save').getAttribute('aria-busy')).not.toBe('true')
    cropHold = false
    cropError = { status: 422, message: 'The crop box is outside the image.' }
    await user.click(present('capture-crop-save'))
    await vi.waitFor(() => {
      expect(screen.getByTestId('capture-status').textContent).toContain('The crop box is outside the image.')
    })
    expect(screen.queryByTestId('capture-crop-bar'), '422 keeps the crop open').not.toBeNull()
    expect(fields()).toEqual([0, 0, 300, 150])
    expect(present<HTMLButtonElement>('capture-crop-save').disabled).toBe(false)
    expect(cropPosts()).toHaveLength(2)
  })

  it('AC-131.20 CROP_CANCEL: Esc, Cancel and a second Crop click close with no request and restore the tool', async () => {
    await open('land.png')
    await user.click(screen.getByTestId('capture-tool-box'))
    await openCrop()
    focusSurface()
    await user.keyboard('{Escape}')
    expect(screen.queryByTestId('capture-crop-bar'), 'Esc closes').toBeNull()
    expect(pressed('capture-tool-box')).toBe('true')
    await openCrop()
    await user.click(present('capture-crop-cancel'))
    expect(screen.queryByTestId('capture-crop-bar'), 'Cancel closes').toBeNull()
    expect(pressed('capture-tool-box')).toBe('true')
    await openCrop()
    await user.click(present('capture-tool-crop'))
    expect(screen.queryByTestId('capture-crop-bar'), 'a second Crop click closes').toBeNull()
    expect(pressed('capture-tool-box')).toBe('true')
    expect(cropPosts()).toHaveLength(0)
  })

  it('AC-131.20 CROP_CANCEL: Reset keeps the crop open; another shot cancels; Annotated cannot be chosen', async () => {
    items = [BAKED, LAND]
    const surface = await open('baked.png')
    await openCrop()
    await user.selectOptions(aspect(), 'square')
    await drag(surface, [
      [150, 100],
      [170, 100],
    ])
    expect(fields()).toEqual([120, 0, 200, 200])
    await user.click(present('capture-crop-reset'))
    expect(fields(), 'Reset').toEqual([0, 0, 400, 200])
    expect(aspect().value).toBe('free')
    expect(screen.queryByTestId('capture-crop-bar')).not.toBeNull()
    // CROP_MODAL disables Annotated while the crop is open, so the view cannot leave Original.
    expect(present<HTMLButtonElement>('capture-view-annotated').disabled).toBe(true)
    fireEvent.click(present('capture-view-annotated'))
    expect(pressed('capture-view-original')).toBe('true')
    await select('land.png')
    expect(screen.queryByTestId('capture-crop-bar'), 'another shot cancels').toBeNull()
    expect(pressed('capture-tool-crop')).toBe('false')
    expect(cropPosts()).toHaveLength(0)
  })

  it('AC-131.21 CROP_MODAL: keys change neither the marks nor the box; tools, history, lock and Annotated wait', async () => {
    items = [BAKED, LAND]
    const surface = await open('baked.png')
    await drawBox(surface)
    await save()
    const before = rects()
    expect(before).toHaveLength(1)
    await user.click(present('capture-tool-crop'))
    for (const focus of [focusSurface, blurAll]) {
      focus()
      await user.keyboard('a')
      await user.keyboard('b')
      await user.keyboard('{Delete}')
      await user.keyboard('{Backspace}')
      await user.keyboard('{Control>}z{/Control}')
      await user.keyboard('{Control>}y{/Control}')
    }
    expect(rects(), 'the marks stay').toEqual(before)
    expect(screen.queryByTestId('capture-save'), 'nothing to save').toBeNull()
    expect(screen.queryByTestId('capture-crop-bar')).not.toBeNull()
    expect(fields(), 'the box stays').toEqual([0, 0, 400, 200])
    expect(pressed('capture-tool-crop')).toBe('true')
    const waiting = [
      ...Object.values(TOOL_BUTTON_IDS).filter((id) => id !== 'capture-tool-crop'),
      'capture-undo',
      'capture-redo',
      'capture-tool-lock',
      'capture-view-annotated',
    ]
    for (const id of waiting) {
      expect(present<HTMLButtonElement>(id).disabled, `${id} disabled`).toBe(true)
      expect(hintOf(id), `${id} hint`).toMatch(new RegExp(` — ${CROP_REASON}$`))
    }
  })

  it('AC-131.22 the registries: the crop tool, its empty options and CROP_BUTTONS beside the others', () => {
    expect(TOOL_BUTTON_IDS.crop).toBe('capture-tool-crop')
    const cropSpec = TOOLBAR_BUTTONS['capture-tool-crop']
    expect(cropSpec?.icon).toBe(Crop)
    expect(cropSpec?.name).toBe('Crop')
    const selections: Array<Annotation | null> = [
      null,
      { type: 'arrow', color: '#FF0000', stroke_width: 3, from: [1, 1], to: [6, 6] },
      { type: 'rect', x: 1, y: 1, width: 4, height: 4, color: '#FF0000', stroke_width: 3 },
      { type: 'highlight', x: 1, y: 1, width: 4, height: 4, color: '#FFFF00', opacity: 0.4 },
      { type: 'text', x: 1, y: 1, text: 'Hi', color: '#FF0000', font_size: 16 },
      { type: 'pixelate', x: 1, y: 1, width: 4, height: 4, block_size: 10 },
      { type: 'eraser', x: 1, y: 1, width: 4, height: 4 },
    ]
    const tool: CaptureTool = 'crop'
    for (const selected of selections) {
      expect(optionGroups(tool, selected), `crop × ${selected?.type ?? 'none'}`).toEqual([])
    }
    const swap = CROP_BUTTONS['capture-crop-swap']
    expect(swap?.icon).toBe(ArrowLeftRight)
    expect(swap?.name).toBe('Swap portrait and landscape')
    expect(Object.keys(CROP_BUTTONS).filter((id) => id in TOOLBAR_BUTTONS || id in ACTION_BUTTONS)).toEqual([])
  })
})
