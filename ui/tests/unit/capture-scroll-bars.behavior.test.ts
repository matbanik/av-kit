/** @vitest-environment jsdom */

// MEU-167 (Session 103) viewport scroll bars on the Capture page: AC-167.4 to AC-167.6.
// The harness is copied from capture-crop-tool.behavior.test.ts (PointerEvent polyfill, hrefOf,
// jsonResponse, mockApi, the stubbed fetch) with one 1600×900 shot and the draw surface stubbed to
// 800×600 from before the first render, as capture-page.behavior.test.ts's withSurfaceRect does. Ten
// Zoom in clicks reach scale 2 (3200×1800 in 800×600), so both bars show. The expected geometry is
// computed here from the plan's SCROLL_BAR_GEOMETRY formulas, not from the module. Every bar element is
// asserted present before use, so a Red run fails by assertion (red-check.py).

import { createHash } from 'node:crypto'
import { existsSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { QueryClientProvider } from '@tanstack/react-query'
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { CapturePage } from '../../src/renderer/src/features/capture/CapturePage'
import { queryClient as appQueryClient } from '../../src/renderer/src/lib/query-client'

const RENDERER = resolve(dirname(fileURLToPath(import.meta.url)), '../../src/renderer/src')
const VIEWPORT_FILE = resolve(RENDERER, 'features/capture/CaptureViewport.tsx')
const MODULE_FILE = resolve(RENDERER, 'features/capture/capture-scroll-bars.ts')
const FIT_MAP_FILE = resolve(RENDERER, 'features/capture/capture-fit-map.ts')
/** sha256 of capture-fit-map.ts at baseline e5028a3, line endings as LF (4994 bytes). */
const FIT_MAP_BASELINE_SHA256 = '7e8ca978ef95ce305cd2a1aba3de5d23a7a8830ba65b511a264c7399d49ebb6e'

/** SCROLL_BAR_GEOMETRY constants from the plan (§MEU-167 Geometry). */
const THICKNESS = 10
const THUMB_MIN = 24
const FRAME = { w: 800, h: 600 }
const IMAGE = { w: 1600, h: 900 }

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

const SHOT = {
  id: 'wide-1',
  original_path: 'C:/shots/wide.png',
  annotated_path: null,
  sidecar_path: null,
  display_name: 'wide.png',
  width: IMAGE.w,
  height: IMAGE.h,
  file_size: 32,
  source: 'gui',
  created_at: '2026-11-26T12:00:00Z',
  updated_at: '2026-11-26T12:00:00Z',
}

/** Every bar element is asserted present before use, so a missing one fails by assertion. */
function present<T extends HTMLElement = HTMLElement>(id: string): T {
  const node = screen.queryByTestId(id)
  expect(node, `${id} rendered`).not.toBeNull()
  return node as T
}

function view(): { kind: string | null; scale: number; ox: number; oy: number } {
  const surface = screen.getByTestId('capture-draw-surface')
  return {
    kind: surface.getAttribute('data-zoom-kind'),
    scale: Number(surface.getAttribute('data-zoom-scale')),
    ox: Number(surface.getAttribute('data-zoom-ox')),
    oy: Number(surface.getAttribute('data-zoom-oy')),
  }
}

/** The plan's geometry for one axis when both bars show. */
function expected(frame: number, content: number, offset: number): { track: number; thumb: number; at: number; value: number } {
  const track = frame - THICKNESS
  const thumb = Math.min(track, Math.max(THUMB_MIN, (track * frame) / content))
  return {
    track,
    thumb,
    at: ((track - thumb) * -offset) / (content - frame),
    value: Math.round((100 * -offset) / (content - frame)),
  }
}

const BAR_IDS = ['capture-scrollbar-x', 'capture-scrollbar-y', 'capture-scrollbar-x-thumb', 'capture-scrollbar-y-thumb']

describe('MEU-167 viewport scroll bars', () => {
  let user: ReturnType<typeof userEvent.setup>
  const proto = HTMLElement.prototype.getBoundingClientRect

  beforeEach(() => {
    user = userEvent.setup()
    HTMLElement.prototype.getBoundingClientRect = function (this: HTMLElement): DOMRect {
      if (this.getAttribute('data-testid') === 'capture-draw-surface') {
        return {
          x: 0,
          y: 0,
          left: 0,
          top: 0,
          right: FRAME.w,
          bottom: FRAME.h,
          width: FRAME.w,
          height: FRAME.h,
          toJSON: () => ({}),
        } as DOMRect
      }
      return proto.call(this)
    }
    appQueryClient.setQueryData(['settings', 'capture'], {
      inbox_dir: 'C:/shots',
      hotkey: 'F2',
      copy_to_clipboard: false,
      close_to_tray: true,
      tool_lock: false,
    })
    mockApi()
    URL.createObjectURL = vi.fn(() => 'blob:capture-shot')
    URL.revokeObjectURL = vi.fn()
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const path = hrefOf(input).split('?')[0] ?? ''
      if (path.includes('/settings/capture')) {
        return jsonResponse(appQueryClient.getQueryData(['settings', 'capture']))
      }
      if (path.includes('/captures/requests')) {
        return jsonResponse({ items: [] })
      }
      if (path.endsWith('/image')) {
        return new Response(new Uint8Array([1, 2, 3]), { status: 200, headers: { 'Content-Type': 'image/png' } })
      }
      if (/\/captures\/[^/]+$/.test(path)) {
        return jsonResponse({ ...SHOT, annotations: [], backup_path: null })
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
    localStorage.clear()
    appQueryClient.clear()
    vi.unstubAllGlobals()
    HTMLElement.prototype.getBoundingClientRect = proto
  })

  /** Renders the page, selects the shot and zooms in ten times to scale 2. */
  async function openZoomed(): Promise<HTMLElement> {
    appQueryClient.setQueryData(['captures'], { items: [SHOT], pendingInteractive: false })
    render(createElement(QueryClientProvider, { client: appQueryClient }, createElement(CapturePage)))
    await vi.waitFor(() => {
      expect(screen.getAllByTestId('capture-filmstrip-item').length).toBe(1)
    })
    await user.click(screen.getAllByTestId('capture-filmstrip-item')[0] as HTMLElement)
    await vi.waitFor(() => {
      expect(screen.getByTestId('capture-draw-surface').getAttribute('data-overlay-ready')).toBe('true')
    })
    for (let i = 0; i < 10; i += 1) {
      await user.click(screen.getByTestId('capture-zoom-in'))
    }
    expect(view().kind).toBe('scale')
    expect(view().scale).toBeCloseTo(2, 4)
    return screen.getByTestId('capture-draw-surface')
  }

  it('AC-167.4 zoomed past the frame: both bars carry the scrollbar role, values, controls and names', async () => {
    const surface = await openZoomed()
    const now = view()
    for (const [axis, orientation, name, frame, content, offset] of [
      ['x', 'horizontal', 'Horizontal scroll', FRAME.w, IMAGE.w * 2, now.ox],
      ['y', 'vertical', 'Vertical scroll', FRAME.h, IMAGE.h * 2, now.oy],
    ] as const) {
      const bar = present(`capture-scrollbar-${axis}`)
      const thumb = present(`capture-scrollbar-${axis}-thumb`)
      expect(bar.contains(thumb), `${axis} thumb inside its bar`).toBe(true)
      expect(bar.getAttribute('role')).toBe('scrollbar')
      expect(bar.getAttribute('aria-orientation')).toBe(orientation)
      expect(bar.getAttribute('aria-valuemin')).toBe('0')
      expect(bar.getAttribute('aria-valuemax')).toBe('100')
      const want = expected(frame, content, offset)
      expect(bar.getAttribute('aria-valuenow')).toMatch(/^\d+$/)
      expect(Number(bar.getAttribute('aria-valuenow'))).toBe(want.value)
      const controls = bar.getAttribute('aria-controls')
      expect(controls, `${axis} aria-controls`).toBeTruthy()
      expect(document.getElementById(controls as string)).toBe(surface)
      expect(screen.getByRole('scrollbar', { name })).toBe(bar)
      const length = axis === 'x' ? thumb.style.width : thumb.style.height
      const start = axis === 'x' ? thumb.style.left : thumb.style.top
      expect(Number.parseFloat(length)).toBeCloseTo(want.thumb, 3)
      expect(Number.parseFloat(start)).toBeCloseTo(want.at, 3)
      for (const node of [bar, thumb]) {
        expect(node.tabIndex, `${axis} not a tab stop`).toBeLessThan(0)
        expect(node.getAttribute('tabindex')).toBeNull()
      }
    }
  })

  it('AC-167.4 negative: at Fit no bar is in the document', async () => {
    await openZoomed()
    for (const id of BAR_IDS) {
      present(id)
    }
    await user.click(screen.getByTestId('capture-zoom-fit'))
    expect(view().kind).toBe('fit')
    for (const id of BAR_IDS) {
      expect(screen.queryByTestId(id), `${id} at Fit`).toBeNull()
    }
  })

  it('AC-167.5 a 30 px drag of the vertical thumb pans that axis by the geometry and draws nothing', async () => {
    await openZoomed()
    const before = view()
    const thumb = present('capture-scrollbar-y-thumb')
    const undo = screen.getByTestId('capture-undo') as HTMLButtonElement
    const color = (screen.getByTestId('capture-color') as HTMLInputElement).value
    const marks = document.querySelectorAll('[data-testid="capture-annotation"]').length
    expect(undo.disabled).toBe(true)
    await user.pointer([
      { keys: '[MouseLeft>]', target: thumb, coords: { clientX: 795, clientY: 300 } },
      { target: thumb, coords: { clientX: 795, clientY: 330 } },
      { keys: '[/MouseLeft]', target: thumb, coords: { clientX: 795, clientY: 330 } },
    ])
    const want = expected(FRAME.h, IMAGE.h * 2, before.oy)
    const after = view()
    expect(after.oy).toBeCloseTo(before.oy + (-30 * (IMAGE.h * 2 - FRAME.h)) / (want.track - want.thumb), 3)
    expect(after.ox).toBe(before.ox)
    expect(after.scale).toBe(before.scale)
    // SCROLL_BAR_DRAG: the arrow tool is active, so a pointer event that reached the surface would draw.
    expect(document.querySelectorAll('[data-testid="capture-annotation"]').length).toBe(marks)
    expect(undo.disabled).toBe(true)
    expect((screen.getByTestId('capture-color') as HTMLInputElement).value).toBe(color)
  })

  it('AC-167.6 source scan: theme tokens only, no transition, a click-through track, the frame and fit map kept', () => {
    expect(existsSync(MODULE_FILE), 'capture-scroll-bars.ts exists').toBe(true)
    const viewport = readFileSync(VIEWPORT_FILE, 'utf8').replace(/\r\n/g, '\n')
    const start = viewport.indexOf('\nfunction ViewportScrollBar(')
    expect(start, 'the bars markup (function ViewportScrollBar) exists').toBeGreaterThanOrEqual(0)
    const end = viewport.indexOf('\n}\n', start)
    const markup = viewport.slice(start, end)
    expect(markup).toContain('capture-scrollbar-')
    const geometry = readFileSync(MODULE_FILE, 'utf8')
    for (const [label, text] of [
      ['markup', markup],
      ['capture-scroll-bars.ts', geometry],
    ] as const) {
      expect(text, `${label}: no hex colour`).not.toMatch(/#[0-9a-fA-F]{3,8}\b/)
      expect(text, `${label}: no rgb( colour`).not.toMatch(/\brgba?\(/)
      expect(text, `${label}: no transition`).not.toMatch(/\btransition/)
    }
    expect(markup).toContain('pointer-events-none')
    expect(markup).toContain('pointer-events-auto')
    expect(markup).toContain('bg-fg-muted')
    expect(markup).toContain('border-bg')
    expect(viewport).toContain('className={`flex-1 min-h-[200px] relative overflow-hidden bg-bg-elevated${surfaceCursor}`}')
    const fitMap = readFileSync(FIT_MAP_FILE).toString('utf8').replace(/\r\n/g, '\n')
    expect(createHash('sha256').update(fitMap, 'utf8').digest('hex')).toBe(FIT_MAP_BASELINE_SHA256)
  })
})
