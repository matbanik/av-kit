/** @vitest-environment jsdom */

import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import type { Annotation } from '../../src/renderer/src/features/capture/capture-annotate'
import { arrowHeadPoints } from '../../src/renderer/src/features/capture/capture-arrow-head'
import { contrastText, NAMED_COLOR_HEX } from '../../src/renderer/src/features/capture/capture-color'
import { queryClient as appQueryClient } from '../../src/renderer/src/lib/query-client'
import { CAPTURE_COMMANDS, setCaptureSelection } from '../../src/renderer/src/features/capture/capture-commands'
import { CapturePage } from '../../src/renderer/src/features/capture/CapturePage'
import { getCommandState } from '../../src/renderer/src/registry/command-state'
import { CaptureViewport } from '../../src/renderer/src/features/capture/CaptureViewport'
import { fitScaleOrigin } from '../../src/renderer/src/features/capture/capture-fit-map'
import { HANDLE_RADIUS_CSS } from '../../src/renderer/src/features/capture/capture-hit-test'
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

function hrefOf(input: RequestInfo | URL): string {
  if (typeof input === 'string') {
    return input
  }
  if (input instanceof URL) {
    return input.href
  }
  return input.url
}

function makeClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false, staleTime: Infinity, gcTime: 0 },
    },
  })
}

type FetchCall = { url: string; method: string; body?: unknown }

type ArrowCase = {
  from: [number, number]
  to: [number, number]
  stroke: number
  head: number | null
  left: [number, number] | null
  right: [number, number] | null
  shaft_end: [number, number] | null
}

const ARROW_CASES = (
  JSON.parse(
    readFileSync(resolve(dirname(fileURLToPath(import.meta.url)), '../e2e/fixtures/capture-geometry.json'), 'utf8'),
  ) as { arrows: ArrowCase[] }
).arrows

function expectNear(actual: number, expected: number, label: string): void {
  expect(Math.abs(actual - expected), label).toBeLessThanOrEqual(1e-9)
}

const SHOT = {
  id: 'shot-1',
  original_path: 'C:/shots/a.png',
  annotated_path: null,
  sidecar_path: null,
  display_name: 'a.png',
  width: 8,
  height: 8,
  file_size: 32,
  source: 'gui',
  created_at: '2026-08-27T12:00:00Z',
  updated_at: '2026-08-27T12:00:00Z',
}

const SHOT_B = {
  ...SHOT,
  id: 'shot-2',
  original_path: 'C:/shots/b.png',
  display_name: 'b.png',
  created_at: '2026-08-27T11:00:00Z',
  updated_at: '2026-08-27T11:00:00Z',
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

function bindSurface(surface: HTMLElement): void {
  surface.getBoundingClientRect = () =>
    ({
      x: 0,
      y: 0,
      left: 0,
      top: 0,
      right: 200,
      bottom: 200,
      width: 200,
      height: 200,
      toJSON: () => ({}),
    }) as DOMRect
}

/**
 * MEU-80 (HINT_TIMING): focus shows a hint at once, so a focused control's `{id}-hint` text reads back
 * synchronously. Focuses `target`, reads `hintId`'s text (null when no hint shows), then blurs.
 */
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
  const button = screen.getByTestId(id) as HTMLButtonElement
  return button.disabled ? screen.getByTestId(`${id}-tip`) : button
}

describe('MEU-39 capture GUI runtime (exec r1 F1 F2 F5)', () => {
  let user: ReturnType<typeof userEvent.setup>
  let queryClient: QueryClient
  const fetches: FetchCall[] = []
  const detailAnnotations: Record<string, unknown[]> = {}
  const detailStatus: Record<string, number> = {}
  const detailHold = new Set<string>()
  const detailWaiters: Record<string, Array<(response: Response) => void>> = {}
  // Fixture seam (MEU-57): the catalog the fetch mock serves, so a test can render zero shots.
  let catalogItems: Array<typeof SHOT> = [SHOT, SHOT_B]
  let captureSettings = {
    inbox_dir: 'C:/Pictures/av-kit',
    hotkey: 'F2',
    copy_to_clipboard: false,
    close_to_tray: true,
  }

  beforeEach(() => {
    user = userEvent.setup()
    fetches.length = 0
    for (const key of Object.keys(detailAnnotations)) {
      delete detailAnnotations[key]
    }
    for (const key of Object.keys(detailStatus)) {
      delete detailStatus[key]
    }
    detailHold.clear()
    for (const key of Object.keys(detailWaiters)) {
      delete detailWaiters[key]
    }
    captureSettings = {
      inbox_dir: 'C:/Pictures/av-kit',
      hotkey: 'F2',
      copy_to_clipboard: false,
      close_to_tray: true,
    }
    catalogItems = [SHOT, SHOT_B]
    queryClient = makeClient()
    queryClient.setQueryData(['captures'], { items: [SHOT, SHOT_B], pendingInteractive: false })
    queryClient.setQueryData(['settings', 'capture'], captureSettings)
    mockApi()
    URL.createObjectURL = vi.fn(() => 'blob:capture-shot')
    URL.revokeObjectURL = vi.fn()
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = hrefOf(input)
      const method = (init?.method ?? 'GET').toUpperCase()
      let body: unknown
      if (typeof init?.body === 'string' && init.body.length > 0) {
        body = JSON.parse(init.body)
      }
      fetches.push({ url, method, body })
      if (url.includes('/settings/capture')) {
        if (method === 'PUT') {
          captureSettings = { ...captureSettings, ...(body as typeof captureSettings) }
          return jsonResponse(captureSettings)
        }
        return jsonResponse(captureSettings)
      }
      if (url.includes('/captures/requests')) {
        return jsonResponse({ items: [] })
      }
      if (url.includes('/image')) {
        return new Response(new Uint8Array([1, 2, 3]), {
          status: 200,
          headers: { 'Content-Type': 'image/png' },
        })
      }
      if (url.includes('/annotate')) {
        return jsonResponse({ ok: true })
      }
      const pathOnly = url.split('?')[0] ?? url
      const shotMatch = pathOnly.match(/\/captures\/([^/]+)$/)
      if (shotMatch && method === 'GET') {
        const shotId = shotMatch[1] as string
        const status = detailStatus[shotId] ?? 200
        const payload = jsonResponse(
          {
            ...SHOT,
            id: shotId,
            annotations: detailAnnotations[shotId] ?? [],
          },
          status,
        )
        if (detailHold.has(shotId)) {
          return await new Promise<Response>((resolve) => {
            const queued = detailWaiters[shotId] ?? []
            queued.push(resolve)
            detailWaiters[shotId] = queued
          }).then(() => payload)
        }
        return payload
      }
      if (url.includes('/captures')) {
        return jsonResponse({ items: catalogItems })
      }
      return jsonResponse({})
    })
    vi.stubGlobal('fetch', fetchMock)
    window.fetch = fetchMock as typeof window.fetch
  })

  afterEach(() => {
    queryClient.clear()
    vi.unstubAllGlobals()
  })

  async function renderPage(): Promise<void> {
    render(createElement(QueryClientProvider, { client: queryClient }, createElement(CapturePage)))
    await vi.waitFor(() => {
      expect(screen.getByTestId('capture-page')).toBeTruthy()
    })
  }

  async function flush(): Promise<void> {
    await act(async () => {
      await Promise.resolve()
      await Promise.resolve()
    })
  }

  async function openSelectedSurface(): Promise<HTMLElement> {
    await renderPage()
    await vi.waitFor(() => {
      expect(screen.getAllByTestId('capture-filmstrip-item').length).toBeGreaterThan(0)
    })
    await user.click(screen.getAllByTestId('capture-filmstrip-item')[0] as HTMLElement)
    await vi.waitFor(() => {
      expect(screen.getByTestId('capture-draw-surface')).toBeTruthy()
    })
    const surface = screen.getByTestId('capture-draw-surface')
    bindSurface(surface)
    // TM-5 (CP1): Save mounts only when the overlay is dirty, so readiness is CAPTURE_READY_SIGNAL
    // on a clean shot with Save absent.
    await vi.waitFor(() => {
      expect(screen.getByTestId('capture-draw-surface').getAttribute('data-overlay-ready')).toBe('true')
    })
    expect(screen.queryByTestId('capture-save')).toBeNull()
    return surface
  }

  function releaseHeldDetail(shotId: string): void {
    detailHold.delete(shotId)
    const queued = detailWaiters[shotId] ?? []
    detailWaiters[shotId] = []
    for (const resolve of queued) {
      resolve(jsonResponse({}))
    }
  }

  it('AC-39.7 AC-39.8 selected capture renders in the viewport with visible vector marks', async () => {
    const surface = await openSelectedSurface()
    const image = screen.getByTestId('capture-viewport-image') as HTMLImageElement
    expect(image.src).toContain('blob:')
    expect(image.src).not.toContain('file://')
    await act(async () => {
      surface.dispatchEvent(new MouseEvent('mousedown', { clientX: 10, clientY: 10, bubbles: true }))
      surface.dispatchEvent(new MouseEvent('mouseup', { clientX: 40, clientY: 50, bubbles: true }))
    })
    const mark = document.querySelector('[data-testid="capture-annotation"]')
    expect(mark).toBeTruthy()
    expect(mark?.getAttribute('data-annotation-type')).toBe('arrow')
  })

  it('AC-39.8 text tool commits on Enter and cancels on Escape', async () => {
    const surface = await openSelectedSurface()
    await user.click(screen.getByTestId('capture-tool-text'))
    await act(async () => {
      surface.dispatchEvent(new MouseEvent('mousedown', { clientX: 20, clientY: 30, bubbles: true }))
    })
    const draft = screen.getByTestId('capture-text-draft') as HTMLInputElement
    await user.type(draft, 'Hello{Enter}')
    const committed = document.querySelector('[data-annotation-type="text"]')
    expect(committed?.textContent).toBe('Hello')
    await user.click(screen.getByTestId('capture-tool-text'))
    await act(async () => {
      surface.dispatchEvent(new MouseEvent('mousedown', { clientX: 80, clientY: 90, bubbles: true }))
    })
    const draft2 = screen.getByTestId('capture-text-draft')
    await user.type(draft2, '{Escape}')
    expect(screen.queryByTestId('capture-text-draft')).toBeNull()
    expect(document.querySelectorAll('[data-annotation-type="text"]')).toHaveLength(1)
  })

  it('AC-39.4 AC-39.15 Capture page Save PUTs capture settings only when dirty', async () => {
    await renderPage()
    await vi.waitFor(() => {
      expect((screen.getByTestId('capture-inbox-path') as HTMLInputElement).value).toBe('C:/Pictures/av-kit')
    })
    const putsBefore = fetches.filter((row) => row.method === 'PUT' && row.url.includes('/settings/capture'))
    expect(putsBefore).toHaveLength(0)
    const inbox = screen.getByTestId('capture-inbox-path')
    await user.clear(inbox)
    await user.type(inbox, 'C:/Pictures/inbox-2')
    const save = screen.getByTestId('capture-page-save')
    expect(save.className).toContain('btn-save-dirty')
    await user.click(save)
    await flush()
    const puts = fetches.filter((row) => row.method === 'PUT' && row.url.includes('/settings/capture'))
    expect(puts).toHaveLength(1)
    expect(puts[0]?.body).toMatchObject({ inbox_dir: 'C:/Pictures/inbox-2', hotkey: 'F2' })
  })

  it('AC-39.28 Capture region is primary md and tools are outline until active primary', async () => {
    await renderPage()
    const region = screen.getByTestId('capture-region')
    expect(region.className).toMatch(/h-9/)
    expect(region.className).toMatch(/bg-accent/)
    const arrow = screen.getByTestId('capture-tool-arrow')
    const box = screen.getByTestId('capture-tool-box')
    // TM-10 (§05 CP 17): the tool segment is sm.
    expect(arrow.className).toMatch(/h-7/)
    expect(arrow.getAttribute('aria-pressed')).toBe('true')
    expect(box.getAttribute('aria-pressed')).toBe('false')
    await user.click(box)
    expect(screen.getByTestId('capture-tool-box').getAttribute('aria-pressed')).toBe('true')
    expect(screen.getByTestId('capture-tool-arrow').getAttribute('aria-pressed')).toBe('false')
  })

  it('AC-59.4 draw SVG uses image-space viewBox and xMidYMid meet', async () => {
    await openSelectedSurface()
    const svg = document.querySelector('[data-testid="capture-draw-surface"] svg')
    expect(svg?.getAttribute('viewBox')).toBe('0 0 8 8')
    expect(svg?.getAttribute('preserveAspectRatio') ?? '').toContain('xMidYMid')
    expect(svg?.getAttribute('preserveAspectRatio') ?? '').toContain('meet')
  })

  it('AC-59.5 zero-length arrow gesture creates no mark', async () => {
    const surface = await openSelectedSurface()
    await act(async () => {
      surface.dispatchEvent(new MouseEvent('mousedown', { clientX: 20, clientY: 20, bubbles: true }))
      surface.dispatchEvent(new MouseEvent('mouseup', { clientX: 20, clientY: 20, bubbles: true }))
    })
    expect(document.querySelector('[data-annotation-type="arrow"]')).toBeNull()
  })

  it('AC-59.6 nonempty text draft is dirty and composing Enter does not commit', async () => {
    const surface = await openSelectedSurface()
    await user.click(screen.getByTestId('capture-tool-text'))
    await act(async () => {
      surface.dispatchEvent(new MouseEvent('mousedown', { clientX: 20, clientY: 30, bubbles: true }))
    })
    const draft = screen.getByTestId('capture-text-draft') as HTMLInputElement
    await user.type(draft, 'Hello')
    const thumbs = screen.getAllByTestId('capture-filmstrip-item')
    expect(thumbs.length).toBeGreaterThan(1)
    await user.click(thumbs[1] as HTMLElement)
    expect(screen.getByTestId('capture-dirty-confirm')).toBeTruthy()
    await user.click(screen.getByTestId('capture-dirty-confirm-cancel'))
    await act(async () => {
      draft.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true, isComposing: true }))
    })
    expect(screen.queryByTestId('capture-text-draft')).not.toBeNull()
  })

  it('AC-59.7 invalid annotate body does not POST and surfaces capture-status', async () => {
    const surface = await openSelectedSurface()
    // TM-11 (CP1): draw one mark so Save mounts before the malformed seam selection is injected.
    await drag(surface, 25, 25, 150, 150)
    const errors: string[] = []
    window.addEventListener('av-kit:capture:error', (event) => {
      errors.push(String((event as CustomEvent<string>).detail ?? ''))
    })
    setCaptureSelection({
      id: 'shot-1',
      annotations: [
        {
          type: 'arrow',
          from: [0, 0],
          to: [8, 8],
          color: 'red',
          stroke_width: 2,
          extra: true,
        } as never,
      ],
    })
    await user.click(screen.getByTestId('capture-save'))
    await flush()
    const annotatePosts = fetches.filter((row) => row.method === 'POST' && row.url.includes('/annotate'))
    expect(annotatePosts).toHaveLength(0)
    const status = screen.getByTestId('capture-status').textContent ?? ''
    expect(status.trim().length).toBeGreaterThan(0)
    expect(errors.length).toBeGreaterThan(0)
  })

  it('AC-59.8 selecting a shot loads GET detail annotations and a 422 does not wipe them', async () => {
    detailAnnotations['shot-1'] = [
      {
        type: 'arrow',
        from: [0, 0],
        to: [8, 8],
        color: 'red',
        stroke_width: 2,
      },
    ]
    await openSelectedSurface()
    await vi.waitFor(() => {
      expect(document.querySelector('[data-annotation-type="arrow"]')).not.toBeNull()
    })
    detailHold.add('shot-2')
    await user.click(screen.getAllByTestId('capture-filmstrip-item')[1] as HTMLElement)
    await flush()
    // TM-8 (CP1): the held clean shot has no mounted Save.
    expect(screen.queryByTestId('capture-save')).toBeNull()
    expect(fetches.filter((row) => row.method === 'POST' && row.url.includes('/annotate'))).toHaveLength(0)
    releaseHeldDetail('shot-2')
    await vi.waitFor(() => {
      expect(screen.getByTestId('capture-draw-surface').getAttribute('data-overlay-ready')).toBe('true')
    })
    expect(screen.queryByTestId('capture-save')).toBeNull()
    expect(fetches.filter((row) => row.method === 'POST' && row.url.includes('/annotate'))).toHaveLength(0)
  })

  it('AC-59.8 a 422 detail GET does not enable Save or POST empty marks', async () => {
    detailAnnotations['shot-1'] = [
      {
        type: 'arrow',
        from: [0, 0],
        to: [8, 8],
        color: 'red',
        stroke_width: 2,
      },
    ]
    await openSelectedSurface()
    detailStatus['shot-2'] = 422
    await user.click(screen.getAllByTestId('capture-filmstrip-item')[1] as HTMLElement)
    await flush()
    // TM-6 (CP1): a clean shot whose detail failed has no mounted Save.
    expect(screen.queryByTestId('capture-save')).toBeNull()
    const status = screen.getByTestId('capture-status').textContent ?? ''
    expect(status.trim().length).toBeGreaterThan(0)
    expect(fetches.filter((row) => row.method === 'POST' && row.url.includes('/annotate'))).toHaveLength(0)
  })

  it('AC-59.9 annotated view hides vector marks', async () => {
    queryClient.setQueryData(['captures'], {
      items: [{ ...SHOT, annotated_path: 'C:/shots/a.annotated.png' }, SHOT_B],
      pendingInteractive: false,
    })
    const surface = await openSelectedSurface()
    await act(async () => {
      surface.dispatchEvent(new MouseEvent('mousedown', { clientX: 10, clientY: 10, bubbles: true }))
      surface.dispatchEvent(new MouseEvent('mouseup', { clientX: 40, clientY: 50, bubbles: true }))
    })
    expect(document.querySelector('[data-testid="capture-annotation"]')).not.toBeNull()
    await user.click(screen.getByTestId('capture-view-annotated'))
    expect(document.querySelectorAll('[data-testid="capture-annotation"]')).toHaveLength(0)
  })

  it('AC-59.13 text tool shows font and bg controls', async () => {
    await openSelectedSurface()
    expect(screen.getByTestId('capture-stroke')).toBeTruthy()
    expect(screen.queryByTestId('capture-font-size')).toBeNull()
    await user.click(screen.getByTestId('capture-tool-text'))
    expect(screen.getByTestId('capture-font-size')).toBeTruthy()
    expect(screen.getByTestId('capture-text-bg')).toBeTruthy()
  })

  it('text background is a color well; a pick paints the plate and clear removes it', async () => {
    const surface = await openSelectedSurface()
    await user.click(screen.getByTestId('capture-tool-text'))
    const bg = screen.getByTestId('capture-text-bg') as HTMLInputElement
    expect(bg.type).toBe('color')
    await act(async () => {
      bg.value = '#112233'
      bg.dispatchEvent(new Event('input', { bubbles: true }))
      bg.dispatchEvent(new Event('change', { bubbles: true }))
    })
    await act(async () => {
      surface.dispatchEvent(new MouseEvent('mousedown', { clientX: 20, clientY: 30, bubbles: true }))
    })
    await user.type(screen.getByTestId('capture-text-draft'), 'Hi{Enter}')
    expect(screen.getByTestId('capture-text-bg-plate').getAttribute('fill')?.toUpperCase()).toBe('#112233')
    await user.click(screen.getByTestId('capture-text-bg-clear'))
    expect(screen.queryByTestId('capture-text-bg-plate')).toBeNull()
  })

  it('AC-59.17 committed text font_size matches the font control', async () => {
    const surface = await openSelectedSurface()
    await user.click(screen.getByTestId('capture-tool-text'))
    const font = screen.getByTestId('capture-font-size')
    await user.clear(font)
    await user.type(font, '24')
    await act(async () => {
      surface.dispatchEvent(new MouseEvent('mousedown', { clientX: 20, clientY: 30, bubbles: true }))
    })
    const draft = screen.getByTestId('capture-text-draft')
    await user.type(draft, 'Sized{Enter}')
    const committed = document.querySelector('[data-annotation-type="text"]')
    expect(committed?.getAttribute('font-size') ?? committed?.getAttribute('fontSize')).toBe('24')
  })

  function dispatchPointer(target: HTMLElement, type: string, clientX: number, clientY: number): void {
    target.dispatchEvent(
      new PointerEvent(type, {
        bubbles: true,
        cancelable: true,
        clientX,
        clientY,
        pointerId: 1,
        pointerType: 'mouse',
        isPrimary: true,
      }),
    )
  }

  async function drag(surface: HTMLElement, fromX: number, fromY: number, toX: number, toY: number): Promise<void> {
    await act(async () => {
      dispatchPointer(surface, 'pointerdown', fromX, fromY)
      dispatchPointer(surface, 'pointermove', toX, toY)
      dispatchPointer(surface, 'pointerup', toX, toY)
    })
  }

  // navigateAndDeliver runs a capture command two animation frames after the call, so a test
  // waits out both frames: the assertions then see the delivery, and none fires in a later test.
  async function deliverSave(): Promise<void> {
    await act(async () => {
      CAPTURE_COMMANDS.save()
      await new Promise<void>((resolve) => {
        window.requestAnimationFrame(() => {
          window.requestAnimationFrame(() => {
            resolve()
          })
        })
      })
    })
  }

  it('AC-60.4 Arrow tool drag over an existing mark creates a new arrow then auto-Select; Select mode moves the targeted mark', async () => {
    const surface = await openSelectedSurface()
    await drag(surface, 25, 25, 150, 150)
    expect(document.querySelectorAll('[data-annotation-type="arrow"]')).toHaveLength(1)
    expect(screen.getByTestId('capture-tool-select').getAttribute('aria-pressed')).toBe('true')
    await user.click(screen.getByTestId('capture-tool-arrow'))
    await drag(surface, 30, 30, 100, 40)
    expect(document.querySelectorAll('[data-annotation-type="arrow"]')).toHaveLength(2)
    await user.click(screen.getByTestId('capture-tool-select'))
    const first = document.querySelector('[data-annotation-type="arrow"]') as SVGLineElement
    const x1 = first.getAttribute('x1')
    await drag(surface, 25, 25, 75, 25)
    const moved = document.querySelector('[data-annotation-type="arrow"]') as SVGLineElement
    expect(moved.getAttribute('x1')).not.toBe(x1)
  })

  it('AC-60.5 Enter commits text; later drag moves x,y; draft pointer does not start a second draft', async () => {
    const surface = await openSelectedSurface()
    await user.click(screen.getByTestId('capture-tool-text'))
    await act(async () => {
      dispatchPointer(surface, 'pointerdown', 50, 50)
      dispatchPointer(surface, 'pointerup', 50, 50)
    })
    const draft = screen.getByTestId('capture-text-draft') as HTMLInputElement
    await user.type(draft, 'Parked{Enter}')
    expect(screen.getByTestId('capture-tool-select').getAttribute('aria-pressed')).toBe('true')
    const before = document.querySelector('[data-annotation-type="text"]')
    const x = before?.getAttribute('x')
    await drag(surface, 50, 50, 100, 75)
    const after = document.querySelector('[data-annotation-type="text"]')
    expect(after?.getAttribute('x')).not.toBe(x)
    expect(screen.queryAllByTestId('capture-text-draft')).toHaveLength(0)
  })

  it('AC-60.6 many move events coalesce to one undo restoring the start; Esc does not push history', async () => {
    const surface = await openSelectedSurface()
    await drag(surface, 25, 25, 150, 150)
    await user.click(screen.getByTestId('capture-tool-select'))
    await act(async () => {
      dispatchPointer(surface, 'pointerdown', 25, 25)
      dispatchPointer(surface, 'pointermove', 40, 25)
      dispatchPointer(surface, 'pointermove', 55, 25)
      dispatchPointer(surface, 'pointermove', 70, 25)
      dispatchPointer(surface, 'pointerup', 70, 25)
    })
    const undo = screen.getByTestId('capture-undo') as HTMLButtonElement
    expect(undo.disabled).toBe(false)
    await user.click(undo)
    await user.click(undo)
    expect(document.querySelectorAll('[data-annotation-type="arrow"]')).toHaveLength(0)
  })

  it('AC-60.7 mark list shows all four types; click selects a covered mark; Remove mark drops that annotation only', async () => {
    const surface = await openSelectedSurface()
    await drag(surface, 25, 25, 150, 150)
    await user.click(screen.getByTestId('capture-tool-box'))
    await drag(surface, 50, 50, 120, 120)
    await user.click(screen.getByTestId('capture-tool-highlight'))
    await drag(surface, 60, 60, 130, 130)
    await user.click(screen.getByTestId('capture-tool-text'))
    await act(async () => {
      dispatchPointer(surface, 'pointerdown', 75, 75)
      dispatchPointer(surface, 'pointerup', 75, 75)
    })
    await user.type(screen.getByTestId('capture-text-draft'), 'L{Enter}')
    const list = screen.getByTestId('capture-mark-list')
    expect(list.querySelectorAll('button').length).toBeGreaterThanOrEqual(4)
    await user.click(screen.getByTestId('capture-remove-mark'))
    expect(document.querySelectorAll('[data-testid="capture-annotation"]').length).toBe(3)
    expect(screen.getByTestId('capture-delete')).toBeTruthy()
  })

  it('AC-60.8 well/hex update a candidate only; Apply writes #RRGGBB; Cancel writes nothing; named green is not dirty', async () => {
    const surface = await openSelectedSurface()
    await drag(surface, 25, 25, 150, 150)
    const hex = screen.getByTestId('capture-color') as HTMLInputElement
    const well = screen.getByTestId('capture-color-well') as HTMLInputElement
    await user.clear(hex)
    await user.type(hex, '#12abcd')
    expect(document.querySelector('[data-annotation-type="arrow"]')?.getAttribute('stroke')).not.toBe('#12ABCD')
    await user.click(screen.getByTestId('capture-color-apply'))
    expect(document.querySelector('[data-annotation-type="arrow"]')?.getAttribute('stroke')?.toUpperCase()).toBe(
      '#12ABCD',
    )
    well.value = '#00ff00'
    well.dispatchEvent(new Event('input', { bubbles: true }))
    await user.click(screen.getByTestId('capture-color-cancel'))
    expect(document.querySelector('[data-annotation-type="arrow"]')?.getAttribute('stroke')?.toUpperCase()).toBe(
      '#12ABCD',
    )
    await user.selectOptions(screen.getByTestId('capture-named-color'), 'green')
    expect((screen.getByTestId('capture-color') as HTMLInputElement).value.toUpperCase()).toBe('#008000')
    expect(document.querySelector('[data-annotation-type="arrow"]')?.getAttribute('stroke')?.toUpperCase()).toBe(
      '#12ABCD',
    )
    expect((screen.getByTestId('capture-save') as HTMLButtonElement).disabled).toBe(false)
  })

  it('AC-60.8 selecting a named-color mark loads the well without rewriting the DTO or dirtying Save', async () => {
    detailAnnotations['shot-1'] = [
      { type: 'arrow', color: 'green', stroke_width: 3, from: [1, 1], to: [6, 6] },
    ]
    await openSelectedSurface()
    const hexBefore = (screen.getByTestId('capture-color') as HTMLInputElement).value
    await user.click(screen.getByTestId('capture-mark-list').querySelector('button') as HTMLElement)
    expect((screen.getByTestId('capture-color') as HTMLInputElement).value.toUpperCase()).toBe(
      NAMED_COLOR_HEX.green,
    )
    expect(document.querySelector('[data-annotation-type="arrow"]')?.getAttribute('stroke')).toBe('green')
    // TM-9 (CP1): re-selecting a saved mark leaves the shot clean, so Save stays unmounted.
    expect(screen.getByTestId('capture-draw-surface').getAttribute('data-overlay-ready')).toBe('true')
    expect(screen.queryByTestId('capture-save')).toBeNull()
    expect(hexBefore.toUpperCase()).not.toBe(NAMED_COLOR_HEX.green)
  })

  it('AC-60.10 button and palette capture:save refuse when a transaction is open', async () => {
    window.location.hash = '#/capture'
    const surface = await openSelectedSurface()
    await user.click(screen.getByTestId('capture-tool-text'))
    await act(async () => {
      dispatchPointer(surface, 'pointerdown', 50, 50)
      dispatchPointer(surface, 'pointerup', 50, 50)
    })
    expect(screen.getByTestId('capture-text-draft')).toBeTruthy()
    // TM-6 (CP1): an empty text draft is not dirty, so Save is not mounted.
    expect(screen.queryByTestId('capture-save')).toBeNull()
    const posts = fetches.filter((row) => row.method === 'POST' && row.url.includes('/annotate')).length
    await deliverSave()
    const postsAfter = fetches.filter((row) => row.method === 'POST' && row.url.includes('/annotate')).length
    expect(postsAfter).toBe(posts)
  })

  it('AC-60.10 Save refuses during pointer-down-before-move and during an open nudge burst [TA-1]', async () => {
    window.location.hash = '#/capture'
    const surface = await openSelectedSurface()
    await act(async () => {
      dispatchPointer(surface, 'pointerdown', 25, 25)
    })
    // TM-6 (CP1): no mark is committed mid-gesture, so Save is not mounted.
    expect(screen.queryByTestId('capture-save')).toBeNull()
    const postsDown = fetches.filter((row) => row.method === 'POST' && row.url.includes('/annotate')).length
    await deliverSave()
    expect(fetches.filter((row) => row.method === 'POST' && row.url.includes('/annotate')).length).toBe(postsDown)
    await act(async () => {
      dispatchPointer(surface, 'pointermove', 150, 150)
      dispatchPointer(surface, 'pointerup', 150, 150)
    })
    await act(async () => {
      surface.focus()
      surface.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true }))
    })
    expect((screen.getByTestId('capture-save') as HTMLButtonElement).disabled).toBe(true)
    const postsNudge = fetches.filter((row) => row.method === 'POST' && row.url.includes('/annotate')).length
    await deliverSave()
    expect(fetches.filter((row) => row.method === 'POST' && row.url.includes('/annotate')).length).toBe(postsNudge)
    await act(async () => {
      window.dispatchEvent(new KeyboardEvent('keyup', { key: 'ArrowRight', bubbles: true }))
    })
  })

  it('AC-97.11 CAPTURE_SAVE_ROUTE capture:save posts once, then the clean shot has no Save to run', async () => {
    window.location.hash = '#/capture'
    const surface = await openSelectedSurface()
    await drag(surface, 25, 25, 150, 150)
    expect(screen.queryByTestId('capture-save')).not.toBeNull()
    const annotatePosts = () => fetches.filter((row) => row.method === 'POST' && row.url.includes('/annotate')).length
    const before = annotatePosts()
    await deliverSave()
    await vi.waitFor(() => {
      expect(annotatePosts(), 'the first save posts once').toBe(before + 1)
    })
    await vi.waitFor(() => {
      expect(screen.queryByTestId('capture-save'), 'the saved shot is clean').toBeNull()
      expect(getCommandState('/capture')['capture:save']).not.toBe(true)
    })
    await deliverSave()
    expect(annotatePosts(), 'the second save posts nothing').toBe(before + 1)
  })

  it('AC-60.11 Save POSTs the committed list without preview geometry; annotated view has no SVG marks', async () => {
    const surface = await openSelectedSurface()
    await drag(surface, 25, 25, 150, 150)
    await user.click(screen.getByTestId('capture-save'))
    await vi.waitFor(() => {
      const posted = fetches.filter((row) => row.method === 'POST' && row.url.includes('/annotate'))
      expect(posted.length).toBeGreaterThan(0)
      const body = posted[posted.length - 1]?.body as { annotations: unknown[] }
      expect(Array.isArray(body.annotations)).toBe(true)
      expect(body.annotations).toHaveLength(1)
    })
    await user.click(screen.getByTestId('capture-view-annotated'))
    expect(document.querySelector('[data-testid="capture-annotation"]')).toBeNull()
    expect(screen.queryByTestId('capture-handle-from')).toBeNull()
  })

  it('AC-60.13 Select uses outline/primary; color well/Apply/Cancel are visible; handles only for the selected arrow on original [TA-2]', async () => {
    const surface = await openSelectedSurface()
    const select = screen.getByTestId('capture-tool-select')
    expect(select.className).toMatch(/btn-(outline|primary)/)
    expect(screen.getByTestId('capture-color-well')).toBeTruthy()
    expect(screen.getByTestId('capture-color-apply')).toBeTruthy()
    expect(screen.getByTestId('capture-color-cancel')).toBeTruthy()
    await drag(surface, 25, 25, 150, 150)
    expect(screen.getByTestId('capture-handle-from')).toBeTruthy()
    expect(screen.getByTestId('capture-handle-to')).toBeTruthy()
    const box = surface.getBoundingClientRect()
    const { s } = fitScaleOrigin({
      containerW: box.width,
      containerH: box.height,
      imageW: SHOT.width,
      imageH: SHOT.height,
    })
    expect(Number(screen.getByTestId('capture-handle-from').getAttribute('r')) * s).toBeCloseTo(
      HANDLE_RADIUS_CSS,
    )
  })

  it('AC-60.16 Arrow down+move before up draws a preview with no extra undo step; valid up appends once', async () => {
    const surface = await openSelectedSurface()
    await act(async () => {
      dispatchPointer(surface, 'pointerdown', 25, 25)
      dispatchPointer(surface, 'pointermove', 80, 90)
    })
    expect((screen.getByTestId('capture-undo') as HTMLButtonElement).disabled).toBe(true)
    expect(document.querySelector('[data-annotation-type="arrow"]')).toBeTruthy()
    await act(async () => {
      dispatchPointer(surface, 'pointerup', 80, 90)
    })
    expect(document.querySelectorAll('[data-annotation-type="arrow"]')).toHaveLength(1)
    expect((screen.getByTestId('capture-undo') as HTMLButtonElement).disabled).toBe(false)
  })

  it('AC-60.19 a focused arrow handle chooses the nudged end; Delete removes only with annotation focus; Esc cancels without history [TA-3]', async () => {
    const surface = await openSelectedSurface()
    await drag(surface, 25, 25, 150, 150)
    const arrowAttr = (name: string) => document.querySelector('[data-annotation-type="arrow"]')?.getAttribute(name)
    const x1 = arrowAttr('x1')
    const x2 = arrowAttr('x2')
    const nudgeFrom = async (handle: HTMLElement): Promise<void> => {
      await act(async () => {
        handle.focus()
        handle.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true }))
        handle.dispatchEvent(new KeyboardEvent('keyup', { key: 'ArrowRight', bubbles: true }))
      })
    }
    // NUDGE_TARGET: the focused head moves only `to`; the focused tail moves only `from`.
    await nudgeFrom(screen.getByTestId('capture-handle-to'))
    expect(arrowAttr('x2')).not.toBe(x2)
    expect(arrowAttr('x1')).toBe(x1)
    const x2Moved = arrowAttr('x2')
    await nudgeFrom(screen.getByTestId('capture-handle-from'))
    expect(arrowAttr('x1')).not.toBe(x1)
    expect(arrowAttr('x2')).toBe(x2Moved)
    await user.click(screen.getByTestId('capture-color'))
    await act(async () => {
      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Delete', bubbles: true }))
    })
    expect(document.querySelectorAll('[data-annotation-type="arrow"]')).toHaveLength(1)
    expect(screen.queryByTestId('capture-delete-confirm')).toBeNull()
    await user.click(screen.getByTestId('capture-inbox-path'))
    await act(async () => {
      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Delete', bubbles: true }))
    })
    expect(document.querySelectorAll('[data-annotation-type="arrow"]')).toHaveLength(1)
    await act(async () => {
      surface.focus()
    })
    await act(async () => {
      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Backspace', bubbles: true }))
    })
    expect(document.querySelectorAll('[data-annotation-type="arrow"]')).toHaveLength(1)
    await act(async () => {
      const composing = new KeyboardEvent('keydown', { key: 'Delete', bubbles: true })
      Object.defineProperty(composing, 'isComposing', { get: () => true })
      window.dispatchEvent(composing)
    })
    expect(document.querySelectorAll('[data-annotation-type="arrow"]')).toHaveLength(1)
    await act(async () => {
      surface.focus()
    })
    await act(async () => {
      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Delete', bubbles: true }))
    })
    expect(document.querySelectorAll('[data-annotation-type="arrow"]')).toHaveLength(0)
  })

  it('AC-60.3 loaded text auto-Selects, shows a body handle, keeps font-size, and dragging the handle moves the label', async () => {
    detailAnnotations['shot-1'] = [
      {
        type: 'text',
        x: 1,
        y: 1,
        text: 'HelloWorld',
        color: '#FFFFFF',
        font_size: 16,
        bg_color: null,
      },
    ]
    const surface = await openSelectedSurface()
    expect(screen.getByTestId('capture-tool-select').getAttribute('aria-pressed')).toBe('true')
    await user.click(screen.getByTestId('capture-mark-list').querySelector('button') as HTMLElement)
    expect(screen.getByTestId('capture-handle-body')).toBeTruthy()
    expect(screen.getByTestId('capture-font-size')).toBeTruthy()
    const before = document.querySelector('[data-annotation-type="text"]')?.getAttribute('x')
    await drag(surface, 25, 25, 120, 40)
    expect(document.querySelector('[data-annotation-type="text"]')?.getAttribute('x')).not.toBe(before)
  })

  it('AC-82.4 a loaded plate text renders on the alphabetic baseline at y + ascent and a click in the plate selects it', async () => {
    const big = { ...SHOT, width: 40, height: 40 }
    catalogItems = [big, SHOT_B]
    queryClient.setQueryData(['captures'], { items: [big, SHOT_B], pendingInteractive: false })
    detailAnnotations['shot-1'] = [
      {
        type: 'text',
        x: 10,
        y: 20,
        text: 'Hi',
        color: '#FFFFFF',
        font_size: 16,
        bg_color: '#000000',
      },
    ]
    const surface = await openSelectedSurface()
    await vi.waitFor(() => {
      expect(document.querySelector('[data-annotation-type="text"]')).toBeTruthy()
    })
    const text = document.querySelector('[data-annotation-type="text"]') as SVGTextElement
    expect(text.getAttribute('x')).toBe('10')
    expect(text.getAttribute('y')).toBe('38')
    expect(text.getAttribute('dominant-baseline')).toBe('alphabetic')
    const plate = screen.getByTestId('capture-text-bg-plate')
    expect([plate.getAttribute('x'), plate.getAttribute('y'), plate.getAttribute('width'), plate.getAttribute('height')]).toEqual([
      '10',
      '26',
      '15',
      '12',
    ])
    // Fit scale 5 on the 200 px surface: the plate covers CSS x 50..125, y 130..190.
    await act(async () => {
      dispatchPointer(surface, 'pointerdown', 180, 20)
      dispatchPointer(surface, 'pointerup', 180, 20)
    })
    expect(screen.queryByTestId('capture-handle-body')).toBeNull()
    await act(async () => {
      dispatchPointer(surface, 'pointerdown', 85, 160)
      dispatchPointer(surface, 'pointerup', 85, 160)
    })
    expect(screen.getByTestId('capture-handle-body')).toBeTruthy()
  })

  it('AC-83.4 loaded arrows keep from/to on the <g>, end the <line> at SHAFT_END and draw the ARROW_HEAD polygon', async () => {
    const big = { ...SHOT, width: 800, height: 450 }
    catalogItems = [big, SHOT_B]
    queryClient.setQueryData(['captures'], { items: [big, SHOT_B], pendingInteractive: false })
    detailAnnotations['shot-1'] = ARROW_CASES.map((c) => ({
      type: 'arrow',
      color: '#FF0000',
      stroke_width: c.stroke,
      from: c.from,
      to: c.to,
    }))
    await openSelectedSurface()
    await vi.waitFor(() => {
      expect(document.querySelectorAll('[data-annotation-type="arrow"]')).toHaveLength(ARROW_CASES.length)
    })
    const marks = [...document.querySelectorAll('[data-annotation-type="arrow"]')]
    ARROW_CASES.forEach((c, i) => {
      const label = `${c.from} -> ${c.to} s${c.stroke}`
      const mark = marks[i] as SVGGElement
      expect(['x1', 'y1', 'x2', 'y2'].map((k) => mark.getAttribute(k)), label).toEqual(
        [c.from[0], c.from[1], c.to[0], c.to[1]].map(String),
      )
      const line = mark.querySelector('line')
      if (c.shaft_end === null) {
        expect(line, `${label} line`).toBeNull()
      } else {
        expect(line, `${label} line`).not.toBeNull()
        expect([line?.getAttribute('x1'), line?.getAttribute('y1')], label).toEqual(c.from.map(String))
        expectNear(Number(line?.getAttribute('x2')), c.shaft_end[0], `${label} line x2`)
        expectNear(Number(line?.getAttribute('y2')), c.shaft_end[1], `${label} line y2`)
      }
      const polygon = mark.querySelector('polygon')
      if (c.head === null) {
        expect(polygon, `${label} polygon`).toBeNull()
        return
      }
      expect(polygon?.getAttribute('points'), label).toBe(arrowHeadPoints(c.from, c.to, c.stroke))
      const points = (polygon?.getAttribute('points') ?? '').split(' ').map((pair) => pair.split(',').map(Number))
      expect(points, label).toHaveLength(3)
      ;[c.to, c.left as [number, number], c.right as [number, number]].forEach((expected, k) => {
        expectNear(points[k][0], expected[0], `${label} vertex ${k} x`)
        expectNear(points[k][1], expected[1], `${label} vertex ${k} y`)
      })
    })
  })

  it('AC-83.9 the head polygon has stroke="none" and the arrow <g> keeps its stroke colour', async () => {
    detailAnnotations['shot-1'] = [{ type: 'arrow', color: '#FF0000', stroke_width: 3, from: [1, 1], to: [7, 7] }]
    await openSelectedSurface()
    await vi.waitFor(() => {
      expect(document.querySelector('[data-annotation-type="arrow"] polygon')).toBeTruthy()
    })
    const mark = document.querySelector('[data-annotation-type="arrow"]') as SVGGElement
    expect(mark.getAttribute('stroke')).toBe('#FF0000')
    expect(mark.querySelector('polygon')?.getAttribute('stroke')).toBe('none')
  })

  it('AC-84.4 Open file and Open folder follow the viewed variant and fall back to the original', async () => {
    const annotated = 'C:/shots/a.annotated.png'
    const viewed = { ...SHOT, annotated_path: annotated, sidecar_path: 'C:/shots/a.ann.json' } as unknown as typeof SHOT
    catalogItems = [viewed, SHOT_B]
    queryClient.setQueryData(['captures'], { items: [viewed, SHOT_B], pendingInteractive: false })
    const openPath = vi.fn(async (_target: string) => undefined)
    const showItemInFolder = vi.fn(async (_target: string) => undefined)
    window.api = { ...window.api, openPath, showItemInFolder }
    const hash = window.location.hash
    const frame = vi.spyOn(window, 'requestAnimationFrame').mockImplementation((run) => {
      run(0)
      return 0
    })
    async function openBoth(): Promise<void> {
      openPath.mockClear()
      showItemInFolder.mockClear()
      await user.click(screen.getByTestId('capture-open-file'))
      await user.click(screen.getByTestId('capture-open-folder'))
      await vi.waitFor(() => {
        expect(openPath).toHaveBeenCalledTimes(1)
        expect(showItemInFolder).toHaveBeenCalledTimes(1)
      })
    }
    async function paletteOpenFolder(): Promise<void> {
      showItemInFolder.mockClear()
      CAPTURE_COMMANDS.open_folder()
      await vi.waitFor(() => {
        expect(showItemInFolder).toHaveBeenCalledTimes(1)
      })
    }
    try {
      window.location.hash = '#/capture'
      await openSelectedSurface()
      await openBoth()
      expect(openPath).toHaveBeenLastCalledWith(SHOT.original_path)
      expect(showItemInFolder).toHaveBeenLastCalledWith(SHOT.original_path)
      await user.click(screen.getByTestId('capture-view-annotated'))
      await openBoth()
      expect(openPath).toHaveBeenLastCalledWith(annotated)
      expect(showItemInFolder).toHaveBeenLastCalledWith(annotated)
      await paletteOpenFolder()
      expect(showItemInFolder).toHaveBeenLastCalledWith(annotated)
      // The list refetches without the annotated copy while the Annotated view is still the last choice.
      const stale = { ...viewed, annotated_path: null }
      catalogItems = [stale, SHOT_B]
      await act(async () => {
        queryClient.setQueryData(['captures'], { items: [stale, SHOT_B], pendingInteractive: false })
      })
      await openBoth()
      expect(openPath).toHaveBeenLastCalledWith(SHOT.original_path)
      expect(showItemInFolder).toHaveBeenLastCalledWith(SHOT.original_path)
      await paletteOpenFolder()
      expect(showItemInFolder).toHaveBeenLastCalledWith(SHOT.original_path)
    } finally {
      frame.mockRestore()
      window.location.hash = hash
    }
  })

  it('AC-60.8 Save status names the color Apply/Cancel gate instead of looking inert', async () => {
    const surface = await openSelectedSurface()
    await drag(surface, 25, 25, 150, 150)
    const hex = screen.getByTestId('capture-color') as HTMLInputElement
    await user.clear(hex)
    await user.type(hex, '#12ABCD')
    expect((screen.getByTestId('capture-save') as HTMLButtonElement).disabled).toBe(true)
    expect(screen.getByTestId('capture-status').textContent).toMatch(/Apply or Cancel color/i)
  })

  it('AC-60.19 the arrow handles are labeled, focusable nudge targets [TA-5]', async () => {
    const surface = await openSelectedSurface()
    await drag(surface, 25, 25, 150, 150)
    for (const [id, label] of [
      ['capture-handle-from', 'Arrow tail'],
      ['capture-handle-to', 'Arrow head'],
    ] as const) {
      const handle = screen.getByTestId(id)
      expect(handle.getAttribute('aria-label'), id).toBe(label)
      expect(handle.getAttribute('tabindex'), id).toBe('0')
    }
  })

  it('tail and head stay off non-arrow marks; arrow keys move the selected box [TA-6]', async () => {
    detailAnnotations['shot-1'] = [
      { type: 'rect', x: 1, y: 1, width: 3, height: 3, color: '#E0AF68', stroke_width: 2 },
      { type: 'arrow', color: '#E0AF68', stroke_width: 3, from: [1, 1], to: [6, 6] },
    ]
    const surface = await openSelectedSurface()
    const list = screen.getByTestId('capture-mark-list').querySelectorAll('button')
    await user.click(list[0] as HTMLElement)
    expect(screen.queryByTestId('capture-handle-from')).toBeNull()
    expect(screen.queryByTestId('capture-handle-to')).toBeNull()
    const before = document.querySelector('[data-annotation-type="rect"]')?.getAttribute('x')
    await act(async () => {
      surface.focus()
      surface.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true }))
      surface.dispatchEvent(new KeyboardEvent('keyup', { key: 'ArrowRight', bubbles: true }))
    })
    expect(document.querySelector('[data-annotation-type="rect"]')?.getAttribute('x')).not.toBe(before)
    await user.click(list[1] as HTMLElement)
    expect(screen.getByTestId('capture-handle-from')).toBeTruthy()
    expect(screen.getByTestId('capture-handle-to')).toBeTruthy()
  })

  it('AC-60.8 Apply stays off until the candidate differs; named orange then Apply paints the selected mark', async () => {
    const surface = await openSelectedSurface()
    await drag(surface, 25, 25, 150, 150)
    expect((screen.getByTestId('capture-color-apply') as HTMLButtonElement).disabled).toBe(true)
    await user.selectOptions(screen.getByTestId('capture-named-color'), 'orange')
    expect((screen.getByTestId('capture-color') as HTMLInputElement).value.toUpperCase()).toBe('#FFA500')
    expect(document.querySelector('[data-annotation-type="arrow"]')?.getAttribute('stroke')?.toUpperCase()).not.toBe(
      '#FFA500',
    )
    expect((screen.getByTestId('capture-color-apply') as HTMLButtonElement).disabled).toBe(false)
    await user.click(screen.getByTestId('capture-color-apply'))
    expect(document.querySelector('[data-annotation-type="arrow"]')?.getAttribute('stroke')?.toUpperCase()).toBe(
      '#FFA500',
    )
    await user.selectOptions(screen.getByTestId('capture-named-color'), 'blue')
    await user.click(screen.getByTestId('capture-color-cancel'))
    expect((screen.getByTestId('capture-color') as HTMLInputElement).value.toUpperCase()).toBe('#FFA500')
    expect(document.querySelector('[data-annotation-type="arrow"]')?.getAttribute('stroke')?.toUpperCase()).toBe(
      '#FFA500',
    )
  })

  /** jsdom may keep an inline colour as hex or turn it into rgb(); accept either spelling of the same colour. */
  function colorSpellings(hex: string): string[] {
    const [r, g, b] = [1, 3, 5].map((offset) => Number.parseInt(hex.slice(offset, offset + 2), 16))
    return [hex, hex.toLowerCase(), `rgb(${r}, ${g}, ${b})`]
  }

  it('AC-86.2 each named option is painted with its own colour and contrast-picked text; the closed select keeps the menu style', async () => {
    await openSelectedSurface()
    const select = screen.getByTestId('capture-named-color') as HTMLSelectElement
    for (const [name, hex] of Object.entries(NAMED_COLOR_HEX)) {
      const option = select.querySelector(`option[value="${name}"]`) as HTMLOptionElement
      expect(colorSpellings(hex), name).toContain(option.style.backgroundColor)
      expect(colorSpellings(contrastText(hex)), name).toContain(option.style.color)
      expect(option.textContent).toBe(name)
    }
    expect(['#ffffff', 'rgb(255, 255, 255)']).toContain(select.style.backgroundColor)
    expect(['#1e293b', 'rgb(30, 41, 59)']).toContain(select.style.color)
  })

  it('AC-86.2 negative: the Named placeholder is not painted with a named colour', async () => {
    await openSelectedSurface()
    const placeholder = screen.getByTestId('capture-named-color').querySelector('option[value=""]') as HTMLOptionElement
    expect(placeholder.textContent).toBe('Named')
    expect(['#1e293b', 'rgb(30, 41, 59)']).toContain(placeholder.style.color)
    expect(['#ffffff', 'rgb(255, 255, 255)']).toContain(placeholder.style.backgroundColor)
  })

  it('chrome rows do not wrap and a drag does not grow a status line that shoves the image', async () => {
    const surface = await openSelectedSurface()
    const chrome = screen.getByTestId('capture-chrome')
    expect(chrome.className).toMatch(/shrink-0/)
    expect(screen.getByTestId('capture-chrome-tools').className).toMatch(/flex-nowrap/)
    expect(screen.getByTestId('capture-chrome-marks').className).toMatch(/flex-nowrap/)
    expect(screen.getByTestId('capture-status').className).toMatch(/\bh-5\b/)
    await act(async () => {
      dispatchPointer(surface, 'pointerdown', 25, 25)
    })
    expect(screen.getByTestId('capture-status').textContent).not.toMatch(/Finish the current edit/i)
  })

  // ── MEU-57 Capture page layout (Phase 11 §Capture, CP1–CP6) ─────────────────────────────
  function putCount(): number {
    return fetches.filter((row) => row.method === 'PUT' && row.url.includes('/settings/capture')).length
  }

  it('AC-57.1 header row: capped page, Capture region first, closed Settings disclosure owns inbox/hotkey/Save', async () => {
    await renderPage()
    const page = screen.getByTestId('capture-page')
    expect(page.className).toContain('max-w-[var(--layout-page-max-width)]')
    const region = screen.getByTestId('capture-region')
    const toggle = screen.getByTestId('capture-settings-toggle')
    expect(region.compareDocumentPosition(toggle) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(toggle.getAttribute('aria-expanded')).toBe('false')
    const inbox = screen.getByTestId('capture-inbox-path')
    expect(inbox.closest('[hidden]')).not.toBeNull()
    expect(screen.getByTestId('capture-hotkey').closest('[hidden]')).not.toBeNull()
    const summary = page.textContent ?? ''
    expect(summary).toMatch(/2 shots/)
    expect(summary).toContain('C:/Pictures/av-kit')
    await user.click(toggle)
    expect(toggle.getAttribute('aria-expanded')).toBe('true')
    expect(inbox.closest('[hidden]')).toBeNull()
    expect(putCount()).toBe(0)
    const save = screen.getByTestId('capture-page-save')
    expect(save.textContent).toMatch(/Save settings/)
    expect(save.className).toMatch(/h-7/)
    await user.clear(inbox)
    await user.type(inbox, 'C:/Pictures/inbox-3')
    expect(putCount()).toBe(0)
    expect(save.className).toContain('btn-save-dirty')
    await user.click(save)
    await flush()
    expect(putCount()).toBe(1)
    const put = fetches.find((row) => row.method === 'PUT' && row.url.includes('/settings/capture'))
    expect(put?.body).toMatchObject({ inbox_dir: 'C:/Pictures/inbox-3', hotkey: 'F2' })
  })

  it('AC-57.2 hotkey key cap renders inside Capture region only when the hotkey is registered', async () => {
    const status = vi.fn(async () => ({ accelerator: 'F2', registered: true, inUse: false }))
    window.api.getHotkeyStatus = status
    await renderPage()
    await vi.waitFor(() => {
      expect(screen.getByTestId('capture-hotkey-keycap').textContent).toBe('F2')
    })
    const region = screen.getByTestId('capture-region')
    expect(region.contains(screen.getByTestId('capture-hotkey-keycap'))).toBe(true)
    expect(region.textContent?.startsWith('Capture region')).toBe(true)
    expect(status).toHaveBeenCalledTimes(1)
  })

  it('AC-57.2 AC-57.3 an in-use hotkey shows no key cap and a warning banner with the Hotkey chip inside the header [TA-7]', async () => {
    window.api.getHotkeyStatus = vi.fn(async () => ({ accelerator: 'F2', registered: false, inUse: true }))
    await renderPage()
    await vi.waitFor(() => {
      expect(screen.queryByTestId('capture-hotkey-banner')?.textContent).toContain(
        'F2 is in use — quit ShareX or pick another key',
      )
    })
    const banner = screen.getByTestId('capture-hotkey-banner')
    expect(screen.queryByTestId('capture-hotkey-keycap')).toBeNull()
    expect(banner.parentElement).toBe(screen.queryByTestId('capture-header'))
    const chip = banner.querySelector('[data-tone="warning"]')
    expect(chip?.textContent).toBe('Hotkey')
  })

  it('AC-57.3 a free hotkey mounts no banner [TA-7]', async () => {
    await renderPage()
    await flush()
    expect(screen.queryByTestId('capture-hotkey-banner')).toBeNull()
  })

  it('AC-57.4 filmstrip rows: 200px aside, stripped name, time line, full name kept, aria-current, dirty dot', async () => {
    const dated = { ...SHOT, display_name: '2026-09-03 14-22-08 settings-dialog.png' }
    catalogItems = [dated, SHOT_B]
    queryClient.setQueryData(['captures'], { items: [dated, SHOT_B], pendingInteractive: false })
    const surface = await openSelectedSurface()
    const film = screen.getByTestId('capture-filmstrip')
    expect(film.getAttribute('aria-label')).toBe('Captures')
    expect(film.closest('aside')?.className).toMatch(/w-\[12\.5rem\]/)
    const [first, second] = screen.getAllByTestId('capture-filmstrip-item')
    expect(first?.getAttribute('aria-current')).toBe('true')
    expect(second?.getAttribute('aria-current')).toBeNull()
    const names = screen.getAllByTestId('capture-filmstrip-name')
    expect(names[0]?.textContent).toBe('14-22-08 settings-dialog.png')
    expect(screen.getAllByTestId('capture-filmstrip-time')[0]?.textContent).toMatch(/^\d{2}:\d{2}:\d{2}$/)
    expect(first?.textContent).toContain('2026-09-03 14-22-08 settings-dialog.png')
    expect(first?.getAttribute('data-dirty')).toBeNull()
    await drag(surface, 25, 25, 150, 150)
    expect(first?.getAttribute('data-dirty')).toBe('true')
    expect(second?.getAttribute('data-dirty')).toBeNull()
  })

  it('AC-57.5 toolbar: sm tool segment, labelled Color/Stroke, per-shot actions inside the chrome', async () => {
    await openSelectedSurface()
    const chrome = screen.getByTestId('capture-chrome')
    for (const id of ['capture-tool-select', 'capture-tool-arrow', 'capture-tool-box', 'capture-tool-highlight', 'capture-tool-text']) {
      const tool = screen.getByTestId(id)
      expect(tool.className, id).toMatch(/h-7/)
      expect((tool as HTMLButtonElement).disabled, id).toBe(false)
    }
    await user.click(screen.getByTestId('capture-tool-box'))
    expect(screen.getByTestId('capture-tool-box').getAttribute('aria-pressed')).toBe('true')
    expect(screen.getByTestId('capture-tool-arrow').getAttribute('aria-pressed')).toBe('false')
    expect(screen.getByTestId('capture-color').closest('[role="group"]')?.textContent).toMatch(/Color/)
    expect(screen.getByTestId('capture-stroke-scrub').textContent).toBe('Stroke')
    expect(screen.getByTestId('capture-stroke').getAttribute('aria-label')).toBe('Stroke width')
    for (const id of ['capture-open-file', 'capture-open-folder', 'capture-delete']) {
      expect(chrome.contains(screen.getByTestId(id)), id).toBe(true)
    }
    expect(screen.getByTestId('capture-delete').className).toMatch(/h-7/)
    expect(chrome.contains(screen.getByTestId('capture-region'))).toBe(false)
  })

  it('AC-57.5 with no shot the tools are disabled with a hint and a click cannot change the pressed tool [TA-8]', async () => {
    catalogItems = []
    queryClient.setQueryData(['captures'], { items: [], pendingInteractive: false })
    await renderPage()
    const box = screen.getByTestId('capture-tool-box') as HTMLButtonElement
    expect(box.disabled).toBe(true)
    expect(box.getAttribute('title')).toBeNull()
    expect(focusedHint(screen.getByTestId('capture-tool-box-tip'), 'capture-tool-box-hint')).toMatch(/shot/i)
    await user.click(box)
    expect(box.getAttribute('aria-pressed')).toBe('false')
    expect((screen.getByTestId('capture-delete') as HTMLButtonElement).disabled).toBe(true)
    expect((screen.getByTestId('capture-open-file') as HTMLButtonElement).disabled).toBe(true)
    expect((screen.getByTestId('capture-open-folder') as HTMLButtonElement).disabled).toBe(false)
  })

  it('AC-57.6 Save overlay mounts only when dirty and posts once [TA-9]', async () => {
    const surface = await openSelectedSurface()
    expect(screen.queryByTestId('capture-save')).toBeNull()
    await drag(surface, 25, 25, 150, 150)
    const save = screen.getByTestId('capture-save') as HTMLButtonElement
    expect(save.getAttribute('aria-label')).toBe('Save overlay')
    expect(save.textContent?.trim()).toBe('')
    expect(save.disabled).toBe(false)
    expect(save.className).toMatch(/h-7/)
    expect(screen.getByTestId('capture-chrome').contains(save)).toBe(true)
    await user.click(save)
    await flush()
    expect(fetches.filter((row) => row.method === 'POST' && row.url.includes('/annotate'))).toHaveLength(1)
    await vi.waitFor(() => {
      expect(screen.queryByTestId('capture-save')).toBeNull()
    })
  })

  it('AC-57.6 a non-empty text draft mounts Save but keeps it disabled', async () => {
    const surface = await openSelectedSurface()
    await user.click(screen.getByTestId('capture-tool-text'))
    await act(async () => {
      dispatchPointer(surface, 'pointerdown', 50, 50)
      dispatchPointer(surface, 'pointerup', 50, 50)
    })
    expect(screen.queryByTestId('capture-save')).toBeNull()
    await user.type(screen.getByTestId('capture-text-draft'), 'Note')
    expect((screen.getByTestId('capture-save') as HTMLButtonElement).disabled).toBe(true)
  })

  it('AC-57.7 delete confirm is an inline strip above the surface; Cancel focuses first and sends no DELETE', async () => {
    await openSelectedSurface()
    await user.click(screen.getByTestId('capture-delete'))
    const strip = screen.getByTestId('capture-confirm-strip')
    expect(screen.getByTestId('capture-viewport').contains(strip)).toBe(true)
    expect(strip.compareDocumentPosition(screen.getByTestId('capture-draw-surface')) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(strip.textContent).toContain('Delete this capture and its files from disk?')
    expect(screen.getByTestId('capture-delete-confirm').textContent).toBe('Delete capture')
    await vi.waitFor(() => {
      expect(document.activeElement).toBe(screen.getByTestId('capture-delete-confirm-cancel'))
    })
    await user.click(screen.getByTestId('capture-delete-confirm-cancel'))
    expect(screen.queryByTestId('capture-confirm-strip')).toBeNull()
    expect(fetches.filter((row) => row.method === 'DELETE')).toHaveLength(0)
  })

  it('AC-57.7 while a dirty confirm is open the filmstrip and Delete cannot replace it', async () => {
    const surface = await openSelectedSurface()
    await drag(surface, 25, 25, 150, 150)
    const items = screen.getAllByTestId('capture-filmstrip-item')
    await user.click(items[1] as HTMLElement)
    expect(screen.getByTestId('capture-confirm-strip').textContent).toContain('Discard unsaved overlay marks on this shot?')
    expect((items[0] as HTMLButtonElement).disabled).toBe(true)
    expect((items[1] as HTMLButtonElement).disabled).toBe(true)
    expect((screen.getByTestId('capture-delete') as HTMLButtonElement).disabled).toBe(true)
    await user.click(items[1] as HTMLElement)
    expect(screen.getAllByTestId('capture-filmstrip-item')[0]?.getAttribute('aria-current')).toBe('true')
    await user.click(screen.getByTestId('capture-dirty-confirm'))
    await vi.waitFor(() => {
      expect(screen.getAllByTestId('capture-filmstrip-item')[1]?.getAttribute('aria-current')).toBe('true')
    })
    expect(document.body.querySelector(':scope > [style*="position: fixed"]')).toBeNull()
  })

  it.each([
    ['dirty', 'capture-dirty-confirm-cancel'],
    ['delete', 'capture-delete-confirm-cancel'],
  ])('AC-57.7 while the %s confirm strip owns focus, Delete and arrows leave the selected mark alone', async (kind, cancelId) => {
    const surface = await openSelectedSurface()
    await drag(surface, 25, 25, 150, 150)
    const x1 = document.querySelector('[data-annotation-type="arrow"]')?.getAttribute('x1')
    if (kind === 'dirty') {
      await user.click(screen.getAllByTestId('capture-filmstrip-item')[1] as HTMLElement)
    } else {
      await user.click(screen.getByTestId('capture-delete'))
    }
    await vi.waitFor(() => {
      expect(document.activeElement).toBe(screen.getByTestId(cancelId))
    })
    await act(async () => {
      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true }))
      window.dispatchEvent(new KeyboardEvent('keyup', { key: 'ArrowRight', bubbles: true }))
      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Delete', bubbles: true }))
    })
    expect(document.querySelectorAll('[data-annotation-type="arrow"]')).toHaveLength(1)
    expect(document.querySelector('[data-annotation-type="arrow"]')?.getAttribute('x1')).toBe(x1)
    expect(screen.getByTestId('capture-confirm-strip')).toBeTruthy()
    expect(fetches.filter((row) => row.method === 'DELETE')).toHaveLength(0)
  })

  it('AC-57.8 capture-status stays the error channel under the surface; shot info is separate', async () => {
    await openSelectedSurface()
    const info = screen.getByTestId('capture-shot-info')
    expect(info.textContent).toBe('a.png · 8×8')
    const status = screen.getByTestId('capture-status')
    expect(screen.getByTestId('capture-draw-surface').compareDocumentPosition(status) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    await act(async () => {
      window.dispatchEvent(new CustomEvent('av-kit:capture:error', { detail: 'boom failure' }))
    })
    expect(status.textContent).toBe('boom failure')
    expect(info.textContent).not.toContain('boom')
  })

  it('AC-57.9 empty catalog shows capture-empty inside the viewport instead of the draw surface', async () => {
    catalogItems = []
    queryClient.setQueryData(['captures'], { items: [], pendingInteractive: false })
    await renderPage()
    const empty = screen.getByTestId('capture-empty')
    expect(screen.getByTestId('capture-viewport').contains(empty)).toBe(true)
    expect(empty.textContent).toContain('Press F2 or Capture region')
    expect(screen.queryByTestId('capture-draw-surface')).toBeNull()
    expect(screen.getByTestId('capture-shot-info').textContent).toBe('')
  })

  it('AC-57.9 with shots present capture-empty is absent', async () => {
    await openSelectedSurface()
    expect(screen.queryByTestId('capture-empty')).toBeNull()
  })
  // ── MEU-65 Capture toolbar icons and Options (Session 29 plan AC-65.2, AC-65.3, AC-65.5) ──────────
  const MEU65_TOOLBAR: Array<[string, string]> = [
    ['capture-tool-select', 'Select'],
    ['capture-tool-arrow', 'Arrow'],
    ['capture-tool-box', 'Box'],
    ['capture-tool-highlight', 'Highlight'],
    ['capture-tool-text', 'Text'],
    ['capture-tool-redact', 'Redact'],
    ['capture-tool-eraser', 'Smart eraser'],
    ['capture-undo', 'Undo'],
    ['capture-redo', 'Redo'],
    ['capture-view-original', 'Original'],
    ['capture-view-annotated', 'Annotated'],
  ]
  // TA-2 (Session 43): Undo and Redo hints name their chord (HISTORY_HINTS); the aria-label stays the name.
  // Session 68 SMART_ERASER (D-683): the eraser's tooltip reads the name, a colon and the hint.
  const HINT_OVERRIDE: Record<string, string> = {
    'capture-undo': 'Undo (Ctrl+Z)',
    'capture-redo': 'Redo (Ctrl+Y)',
    'capture-tool-eraser': 'Smart eraser: Covers an area with the surrounding colour',
  }
  const MEU65_TOGGLES = [
    'capture-tool-select',
    'capture-tool-arrow',
    'capture-tool-box',
    'capture-tool-highlight',
    'capture-tool-text',
    'capture-tool-redact',
    'capture-tool-eraser',
    'capture-view-original',
    'capture-view-annotated',
  ]
  const MEU65_OPTION_IDS: Record<'color' | 'stroke' | 'text' | 'block' | 'mode', string[]> = {
    color: [
      'capture-color-well',
      'capture-color',
      'capture-color-apply',
      'capture-color-cancel',
      'capture-named-color',
    ],
    stroke: ['capture-stroke'],
    text: ['capture-font-size', 'capture-text-bg', 'capture-text-bg-clear'],
    block: ['capture-block-size'],
    // Session 68 MODE_GROUPS (D-680): the Redact mode control.
    mode: ['capture-redact-mode'],
  }

  function expectOptionGroups(groups: Array<'color' | 'stroke' | 'text' | 'block' | 'mode'>, label: string): void {
    const tools = screen.getByTestId('capture-chrome-tools')
    const options = screen.getByTestId('capture-chrome-options')
    for (const [group, ids] of Object.entries(MEU65_OPTION_IDS) as Array<['color' | 'stroke' | 'text' | 'block' | 'mode', string[]]>) {
      for (const id of ids) {
        const element = screen.queryByTestId(id)
        if (groups.includes(group)) {
          expect(element, `${label}: ${id} present`).not.toBeNull()
          expect(options.contains(element), `${label}: ${id} in the options row`).toBe(true)
        } else {
          expect(element, `${label}: ${id} absent`).toBeNull()
        }
        expect(tools.querySelector(`[data-testid="${id}"]`), `${label}: ${id} not in the tools row`).toBeNull()
      }
    }
    for (const [id] of MEU65_TOOLBAR) {
      expect(options.querySelector(`[data-testid="${id}"]`), `${label}: ${id} not in the options row`).toBeNull()
    }
  }

  it('AC-65.2 toolbar buttons are icon-only with the table accessible name, a hidden svg, h-7 and aria-pressed [TA-11]', async () => {
    await openSelectedSurface()
    const row = screen.getByTestId('capture-chrome-tools')
    for (const [id, name] of MEU65_TOOLBAR) {
      const matches = within(row).getAllByRole('button', { name })
      expect(matches, `${id} resolves once by name`).toHaveLength(1)
      const button = matches[0] as HTMLButtonElement
      expect(button.getAttribute('data-testid'), name).toBe(id)
      expect(button.getAttribute('aria-label'), id).toBe(name)
      expect(button.getAttribute('title'), id).toBeNull()
      expect(screen.getByTestId(`${id}-tip`).getAttribute('title'), `${id}-tip`).toBeNull()
      expect(focusedHint(toolbarFocusTarget(id), `${id}-hint`), `${id} hint`).toBe(HINT_OVERRIDE[id] ?? name)
      expect((button.textContent ?? '').trim(), `${id} has no text node`).toBe('')
      const svg = button.querySelector('svg')
      expect(svg, `${id} svg`).not.toBeNull()
      expect(svg?.getAttribute('aria-hidden'), `${id} svg aria-hidden`).toBe('true')
      expect(button.className, id).toMatch(/\bh-7\b/)
    }
    for (const id of MEU65_TOGGLES) {
      expect(screen.getByTestId(id).hasAttribute('aria-pressed'), `${id} aria-pressed`).toBe(true)
    }
  })

  it('AC-65.2 icon buttons keep their handlers: tool change, undo and redo', async () => {
    const surface = await openSelectedSurface()
    const row = screen.getByTestId('capture-chrome-tools')
    await user.click(within(row).getByRole('button', { name: 'Box' }))
    expect(screen.getByTestId('capture-tool-box').getAttribute('aria-pressed')).toBe('true')
    await user.click(within(row).getByRole('button', { name: 'Arrow' }))
    expect(screen.getByTestId('capture-tool-arrow').getAttribute('aria-pressed')).toBe('true')
    await drag(surface, 25, 25, 150, 150)
    expect(document.querySelectorAll('[data-annotation-type="arrow"]')).toHaveLength(1)
    await user.click(within(row).getByRole('button', { name: 'Undo' }))
    expect(document.querySelectorAll('[data-annotation-type="arrow"]')).toHaveLength(0)
    await user.click(within(row).getByRole('button', { name: 'Redo' }))
    expect(document.querySelectorAll('[data-annotation-type="arrow"]')).toHaveLength(1)
  })

  it('AC-65.2 negative: with no shot the icon tools are disabled with NO_SHOT_HINT and Undo adds no history [TA-11]', async () => {
    catalogItems = []
    queryClient.setQueryData(['captures'], { items: [], pendingInteractive: false })
    await renderPage()
    for (const id of ['capture-tool-select', 'capture-tool-arrow', 'capture-tool-box', 'capture-tool-highlight', 'capture-tool-text']) {
      const tool = screen.getByTestId(id) as HTMLButtonElement
      expect(tool.disabled, id).toBe(true)
      expect(tool.getAttribute('title'), id).toBeNull()
      expect(screen.getByTestId(`${id}-tip`).getAttribute('title'), `${id}-tip`).toBeNull()
      expect(focusedHint(screen.getByTestId(`${id}-tip`), `${id}-hint`), `${id} hint`).toBe(
        `${new Map(MEU65_TOOLBAR).get(id)} — Select a shot first`,
      )
      expect((tool.textContent ?? '').trim(), id).toBe('')
    }
    const undo = screen.getByTestId('capture-undo') as HTMLButtonElement
    expect(undo.disabled).toBe(true)
    await user.click(undo)
    expect((screen.getByTestId('capture-redo') as HTMLButtonElement).disabled).toBe(true)
  })

  it('AC-65.3 the options row renders exactly OPTIONS_BY_TOOL and the tools row holds no option control [TA-10]', async () => {
    await openSelectedSurface()
    const cases: Array<[string, Array<'color' | 'stroke' | 'text' | 'block' | 'mode'>]> = [
      ['capture-tool-select', ['color', 'stroke']],
      ['capture-tool-arrow', ['color', 'stroke']],
      ['capture-tool-box', ['color', 'stroke']],
      ['capture-tool-highlight', ['color']],
      ['capture-tool-redact', ['mode']],
      ['capture-tool-eraser', []],
      ['capture-tool-text', ['color', 'text']],
    ]
    for (const [toolId, groups] of cases) {
      await user.click(screen.getByTestId(toolId))
      expectOptionGroups(groups, toolId)
    }
    const colorGroup = within(screen.getByTestId('capture-chrome-options')).getByRole('group', { name: 'Color' })
    expect(colorGroup.textContent).toMatch(/Color/)
  })

  it('AC-65.3 options keep their behavior: stroke edits a selected arrow, font size edits a selected text mark [TA-10]', async () => {
    const surface = await openSelectedSurface()
    await drag(surface, 25, 25, 150, 150)
    expect(screen.getByTestId('capture-tool-select').getAttribute('aria-pressed')).toBe('true')
    expectOptionGroups(['color', 'stroke'], 'selected arrow')
    const stroke = screen.getByTestId('capture-stroke')
    await user.clear(stroke)
    await user.type(stroke, '7')
    const head = (document.querySelector('[data-annotation-type="arrow"] polygon')?.getAttribute('points') ?? '')
      .split(' ')
      .map((pair) => pair.split(',').map(Number))
    expect(Math.hypot(head[1][0] - head[0][0], head[1][1] - head[0][1])).toBeCloseTo(35, 9)
    await user.click(screen.getByTestId('capture-tool-text'))
    await act(async () => {
      dispatchPointer(surface, 'pointerdown', 60, 60)
      dispatchPointer(surface, 'pointerup', 60, 60)
    })
    await user.type(screen.getByTestId('capture-text-draft'), 'Hi{Enter}')
    expect(screen.getByTestId('capture-tool-select').getAttribute('aria-pressed')).toBe('true')
    expectOptionGroups(['color', 'text'], 'selected text')
    const font = screen.getByTestId('capture-font-size')
    await user.clear(font)
    await user.type(font, '22')
    expect(document.querySelector('[data-annotation-type="text"]')?.getAttribute('font-size')).toBe('22')
  })

  it('AC-65.3 negative: Highlight shows no Stroke; Text shows font size and no Stroke', async () => {
    await openSelectedSurface()
    await user.click(screen.getByTestId('capture-tool-highlight'))
    expect(screen.queryByTestId('capture-stroke')).toBeNull()
    await user.click(screen.getByTestId('capture-tool-text'))
    expect(screen.queryByTestId('capture-stroke')).toBeNull()
    expect(screen.getByTestId('capture-font-size')).toBeTruthy()
  })

  // ── MEU-90 Pixelate (Session 39 plan AC-90.10, AC-90.11) ──────────────────────────────────────────
  const pixelateRects = () => document.querySelectorAll('[data-annotation-type="pixelate"]')
  const rectGeometry = (element: Element | undefined) =>
    ['x', 'y', 'width', 'height'].map((name) => Number(element?.getAttribute(name)))
  const isAnnotatePost = (row: FetchCall) => row.method === 'POST' && row.url.includes('/annotate')

  async function saveBody(): Promise<unknown> {
    const before = fetches.filter(isAnnotatePost).length
    await user.click(screen.getByTestId('capture-save'))
    await vi.waitFor(() => {
      expect(fetches.filter(isAnnotatePost).length).toBe(before + 1)
    })
    const posted = fetches.filter(isAnnotatePost)
    return posted[posted.length - 1]?.body
  }

  it('AC-90.10 a Pixelate drag makes one block-10 mark; Block size applies valid values as one undo step; select, move, Delete guard and Save REGION_DTO', async () => {
    const surface = await openSelectedSurface()
    // Session 68 (D-679, D-680): Pixelate is the Redact tool's second mode.
    expect(screen.queryByTestId('capture-tool-redact')).not.toBeNull()
    await user.click(screen.getByTestId('capture-tool-redact'))
    expect(screen.getByTestId('capture-tool-redact').getAttribute('aria-pressed')).toBe('true')
    expect(screen.queryByTestId('capture-redact-pixelate')).not.toBeNull()
    await user.click(screen.getByTestId('capture-redact-pixelate'))
    const blockField = () => screen.getByTestId('capture-block-size') as HTMLInputElement
    expect(blockField().value).toBe('10')
    expect(blockField().getAttribute('aria-label')).toBe('Block size')
    // Negative: a zero-size drag creates no mark.
    await drag(surface, 60, 60, 60, 60)
    expect(pixelateRects()).toHaveLength(0)
    await drag(surface, 25, 25, 150, 125)
    expect(pixelateRects()).toHaveLength(1)
    expect(rectGeometry(pixelateRects()[0])).toEqual([1, 1, 5, 4])
    const chip = () => within(screen.getByTestId('capture-mark-list')).getByRole('button', { name: 'Pixelate 1' })
    expect(chip().getAttribute('aria-pressed')).toBe('true')
    fireEvent.change(blockField(), { target: { value: '24' } })
    expect(blockField().value).toBe('24')
    for (const held of ['1', '101']) {
      fireEvent.change(blockField(), { target: { value: held } })
      expect(blockField().value).toBe(held)
    }
    const dto = (x: number, y: number, block_size: number) => ({
      annotations: [{ type: 'pixelate', x, y, width: 5, height: 4, block_size }],
    })
    expect(await saveBody()).toEqual(dto(1, 1, 24))
    await user.click(screen.getByTestId('capture-undo'))
    expect(await saveBody()).toEqual(dto(1, 1, 10))
    // A click on empty image deselects; a click inside the body (50 css px from every edge) selects.
    await act(async () => {
      dispatchPointer(surface, 'pointerdown', 190, 190)
      dispatchPointer(surface, 'pointerup', 190, 190)
    })
    expect(chip().getAttribute('aria-pressed')).toBe('false')
    await act(async () => {
      dispatchPointer(surface, 'pointerdown', 75, 75)
      dispatchPointer(surface, 'pointerup', 75, 75)
    })
    expect(chip().getAttribute('aria-pressed')).toBe('true')
    expect(blockField().value).toBe('10')
    await drag(surface, 75, 75, 100, 100)
    expect(rectGeometry(pixelateRects()[0])).toEqual([2, 2, 5, 4])
    await user.click(blockField())
    await act(async () => {
      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Delete', bubbles: true }))
    })
    expect(pixelateRects()).toHaveLength(1)
    await act(async () => {
      surface.focus()
    })
    await act(async () => {
      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Delete', bubbles: true }))
    })
    expect(pixelateRects()).toHaveLength(0)
  })

  it('AC-90.11 a loaded pixelate is one transparent rect over capture-region-layer in Original; Annotated shows neither', async () => {
    detailAnnotations['shot-1'] = [{ type: 'pixelate', x: 1, y: 1, width: 4, height: 3, block_size: 2 }]
    queryClient.setQueryData(['captures'], {
      items: [{ ...SHOT, annotated_path: 'C:/shots/a.annotated.png' }, SHOT_B],
      pendingInteractive: false,
    })
    await openSelectedSurface()
    expect(pixelateRects()).toHaveLength(1)
    const mark = pixelateRects()[0] as Element
    expect(mark.tagName.toLowerCase()).toBe('rect')
    expect(mark.getAttribute('fill')).toBe('none')
    // Session 68 REDACT_OUTLINE (D-684, DEP-2): a pixelate is a redaction, so it draws a 1 px dashed outline.
    expect(mark.getAttribute('stroke')).not.toBe('none')
    expect(mark.getAttribute('stroke-dasharray')).not.toBeNull()
    expect(rectGeometry(mark)).toEqual([1, 1, 4, 3])
    // Negative: the mark is not drawn by the text branch.
    expect(document.querySelectorAll('[data-annotation-type="text"]')).toHaveLength(0)
    expect(document.querySelectorAll('[data-testid="capture-annotation"] text')).toHaveLength(0)
    const layer = screen.queryByTestId('capture-region-layer')
    expect(layer).not.toBeNull()
    expect(layer?.tagName.toLowerCase()).toBe('canvas')
    await user.click(screen.getByTestId('capture-view-annotated'))
    expect(screen.queryByTestId('capture-region-layer')).toBeNull()
    expect(pixelateRects()).toHaveLength(0)
  })

  // ── MEU-91 Eraser (Session 39 plan AC-91.9) ────────────────────────────────────────────────────────
  const eraserRects = () => document.querySelectorAll('[data-annotation-type="eraser"]')

  it('AC-91.9 an Eraser drag makes one eraser mark with no options; select, move, Delete and Save REGION_DTO', async () => {
    const surface = await openSelectedSurface()
    expect(screen.queryByTestId('capture-tool-eraser')).not.toBeNull()
    await user.click(screen.getByTestId('capture-tool-eraser'))
    expect(screen.getByTestId('capture-tool-eraser').getAttribute('aria-pressed')).toBe('true')
    expectOptionGroups([], 'eraser tool')
    // Negative: a zero-size drag creates no mark.
    await drag(surface, 60, 60, 60, 60)
    expect(eraserRects()).toHaveLength(0)
    await drag(surface, 25, 25, 150, 125)
    expect(eraserRects()).toHaveLength(1)
    expect(rectGeometry(eraserRects()[0])).toEqual([1, 1, 5, 4])
    const chip = () => within(screen.getByTestId('capture-mark-list')).getByRole('button', { name: 'Smart eraser 1' })
    expect(chip().getAttribute('aria-pressed')).toBe('true')
    expectOptionGroups([], 'new eraser')
    expect(await saveBody()).toEqual({ annotations: [{ type: 'eraser', x: 1, y: 1, width: 5, height: 4 }] })
    // A click on empty image (175 css px maps to pixel 7 of 8) deselects; a click inside the body (50 css px
    // from every edge) selects.
    await act(async () => {
      dispatchPointer(surface, 'pointerdown', 175, 175)
      dispatchPointer(surface, 'pointerup', 175, 175)
    })
    expect(chip().getAttribute('aria-pressed')).toBe('false')
    await act(async () => {
      dispatchPointer(surface, 'pointerdown', 75, 75)
      dispatchPointer(surface, 'pointerup', 75, 75)
    })
    expect(chip().getAttribute('aria-pressed')).toBe('true')
    expectOptionGroups([], 'selected eraser')
    await drag(surface, 75, 75, 100, 100)
    expect(rectGeometry(eraserRects()[0])).toEqual([2, 2, 5, 4])
    await act(async () => {
      surface.focus()
    })
    await act(async () => {
      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Delete', bubbles: true }))
    })
    expect(eraserRects()).toHaveLength(0)
  })

  it('AC-65.5 the header toggle is an Options button with an icon and a chevron that follows aria-expanded', async () => {
    await renderPage()
    const toggle = screen.getByTestId('capture-settings-toggle')
    expect(screen.getByRole('button', { name: 'Options' })).toBe(toggle)
    expect(toggle.textContent ?? '').not.toMatch(/Settings/)
    expect(toggle.className).toContain('btn-secondary')
    const first = toggle.firstElementChild
    expect(first?.tagName.toLowerCase()).toBe('svg')
    expect(first?.getAttribute('aria-hidden')).toBe('true')
    const chevron = screen.getByTestId('capture-settings-chevron')
    expect(toggle.contains(chevron)).toBe(true)
    expect(chevron.querySelector('svg')).not.toBeNull()
    const panel = document.getElementById('capture-settings-panel') as HTMLElement
    expect(toggle.getAttribute('aria-controls')).toBe('capture-settings-panel')
    expect(toggle.getAttribute('aria-expanded')).toBe('false')
    expect(chevron.getAttribute('data-state')).toBe('closed')
    expect(panel.hidden).toBe(true)
    expect(screen.getByTestId('capture-inbox-path').closest('[hidden]')).not.toBeNull()
    await user.click(toggle)
    expect(toggle.getAttribute('aria-expanded')).toBe('true')
    expect(screen.getByTestId('capture-settings-chevron').getAttribute('data-state')).toBe('open')
    expect(panel.hidden).toBe(false)
    await user.click(toggle)
    expect(toggle.getAttribute('aria-expanded')).toBe('false')
    expect(screen.getByTestId('capture-settings-chevron').getAttribute('data-state')).toBe('closed')
    expect(panel.hidden).toBe(true)
  })

  // ── MEU-66 Capture viewport zoom (Session 29 plan AC-66.7 – AC-66.11; ZOOM_SEAM_SHOT) ─────────────
  // ZOOM_SEAM_SHOT: 1600×900 in an 800×600 surface stub, so Fit is 0.5 and every ladder step is reachable.
  const ZOOM_SEAM_SHOT = {
    ...SHOT,
    id: 'shot-zoom',
    original_path: 'C:/shots/zoom.png',
    annotated_path: 'C:/shots/zoom.annotated.png' as string | null,
    display_name: 'zoom.png',
    width: 1600,
    height: 900,
  }
  const ZOOM_SEAM_SHOT_B = {
    ...ZOOM_SEAM_SHOT,
    id: 'shot-zoom-b',
    original_path: 'C:/shots/zoom-b.png',
    annotated_path: null,
    display_name: 'zoom-b.png',
    created_at: '2026-08-27T11:00:00Z',
    updated_at: '2026-08-27T11:00:00Z',
  }

  type ZoomFixture = Omit<typeof SHOT, 'annotated_path'> & { annotated_path: string | null }

  async function openZoomSurface(items: ZoomFixture[] = [ZOOM_SEAM_SHOT, ZOOM_SEAM_SHOT_B]): Promise<HTMLElement> {
    // The catalog seam is typed by SHOT (annotated_path: null); the zoom shot carries a baked path.
    catalogItems = items as unknown as Array<typeof SHOT>
    queryClient.setQueryData(['captures'], { items, pendingInteractive: false })
    await renderPage()
    await vi.waitFor(() => {
      expect(screen.getAllByTestId('capture-filmstrip-item').length).toBe(items.length)
    })
    await user.click(screen.getAllByTestId('capture-filmstrip-item')[0] as HTMLElement)
    await vi.waitFor(() => {
      expect(screen.getByTestId('capture-draw-surface').getAttribute('data-overlay-ready')).toBe('true')
    })
    return screen.getByTestId('capture-draw-surface')
  }

  function zoomView(): { kind: string | null; scale: number; ox: number; oy: number; readout: string } {
    const surface = screen.getByTestId('capture-draw-surface')
    return {
      kind: surface.getAttribute('data-zoom-kind'),
      scale: Number(surface.getAttribute('data-zoom-scale')),
      ox: Number(surface.getAttribute('data-zoom-ox')),
      oy: Number(surface.getAttribute('data-zoom-oy')),
      readout: screen.getByTestId('capture-zoom-level').textContent ?? '',
    }
  }

  function buttonPointer(target: HTMLElement, type: string, x: number, y: number, button: number): void {
    target.dispatchEvent(
      new PointerEvent(type, {
        bubbles: true,
        cancelable: true,
        clientX: x,
        clientY: y,
        button,
        buttons: button === 1 ? 4 : 1,
        pointerId: 2,
        pointerType: 'mouse',
        isPrimary: true,
      }),
    )
  }

  async function middleDrag(surface: HTMLElement, fromX: number, fromY: number, toX: number, toY: number): Promise<void> {
    await act(async () => {
      buttonPointer(surface, 'pointerdown', fromX, fromY, 1)
      buttonPointer(surface, 'pointermove', toX, toY, 1)
      buttonPointer(surface, 'pointerup', toX, toY, 1)
    })
  }

  async function zoomInTimes(count: number): Promise<void> {
    for (let i = 0; i < count; i += 1) {
      await user.click(screen.getByTestId('capture-zoom-in'))
    }
  }

  function annotationCount(): number {
    return document.querySelectorAll('[data-testid="capture-annotation"]').length
  }

  it('AC-66.7 the zoom group steps ZOOM_STATE about the centre and never touches annotations', async () => {
    await withSurfaceRect({ width: 800, height: 600 }, async () => {
      await openZoomSurface()
      const row = screen.getByTestId('capture-chrome-tools')
      for (const [id, name] of [
        ['capture-zoom-out', 'Zoom out'],
        ['capture-zoom-in', 'Zoom in'],
        ['capture-zoom-fit', 'Fit to view'],
      ]) {
        const button = within(row).getByRole('button', { name })
        expect(button.getAttribute('data-testid')).toBe(id)
        expect((button.textContent ?? '').trim(), id).toBe('')
        expect(button.querySelector('svg')?.getAttribute('aria-hidden'), id).toBe('true')
        expect(button.className, id).toMatch(/\bh-7\b/)
      }
      expect(row.contains(screen.getByTestId('capture-zoom-level'))).toBe(true)
      expect(zoomView()).toMatchObject({ kind: 'fit', readout: 'Fit' })
      expect(zoomView().scale).toBeCloseTo(0.5, 4)
      expect((screen.getByTestId('capture-zoom-fit') as HTMLButtonElement).disabled).toBe(true)
      await user.click(screen.getByTestId('capture-zoom-in'))
      expect(zoomView()).toMatchObject({ kind: 'scale', readout: '67%' })
      expect(zoomView().scale).toBeCloseTo(2 / 3, 4)
      expect(zoomView().ox).toBeCloseTo(400 - (800 * 2) / 3, 3)
      expect(zoomView().oy).toBeCloseTo(0, 3)
      await user.click(screen.getByTestId('capture-zoom-out'))
      expect(zoomView()).toMatchObject({ kind: 'scale', readout: '50%' })
      await user.click(screen.getByTestId('capture-zoom-fit'))
      expect(zoomView()).toMatchObject({ kind: 'fit', readout: 'Fit' })
      expect(annotationCount()).toBe(0)
      expect((screen.getByTestId('capture-undo') as HTMLButtonElement).disabled).toBe(true)
      expect(screen.queryByTestId('capture-save')).toBeNull()
    })
  })

  it('AC-66.7 negative: zoom-in disables at the top of the ladder; no shot disables every zoom button [TA-11]', async () => {
    await withSurfaceRect({ width: 800, height: 600 }, async () => {
      await openZoomSurface()
      for (let i = 0; i < 20 && !(screen.getByTestId('capture-zoom-in') as HTMLButtonElement).disabled; i += 1) {
        await user.click(screen.getByTestId('capture-zoom-in'))
      }
      expect(zoomView().readout).toBe('500%')
      expect((screen.getByTestId('capture-zoom-in') as HTMLButtonElement).disabled).toBe(true)
      expect(screen.queryByTestId('capture-save')).toBeNull()
    })
    cleanup()
    catalogItems = []
    queryClient.setQueryData(['captures'], { items: [], pendingInteractive: false })
    await renderPage()
    const zoomNames: Record<string, string> = {
      'capture-zoom-in': 'Zoom in',
      'capture-zoom-out': 'Zoom out',
      'capture-zoom-fit': 'Fit to view',
    }
    for (const id of ['capture-zoom-in', 'capture-zoom-out', 'capture-zoom-fit']) {
      const button = screen.getByTestId(id) as HTMLButtonElement
      expect(button.disabled, id).toBe(true)
      expect(button.getAttribute('title'), id).toBeNull()
      expect(screen.getByTestId(`${id}-tip`).getAttribute('title'), `${id}-tip`).toBeNull()
      expect(focusedHint(screen.getByTestId(`${id}-tip`), `${id}-hint`), `${id} hint`).toBe(
        `${zoomNames[id]} — Select a shot first`,
      )
    }
  })

  it('AC-66.8 ZOOM_RESET: a shot change returns to Fit; Original/Annotated keeps the scale', async () => {
    await withSurfaceRect({ width: 800, height: 600 }, async () => {
      await openZoomSurface()
      await zoomInTimes(3)
      expect(zoomView().readout).toBe('80%')
      await user.click(screen.getByTestId('capture-view-annotated'))
      expect(zoomView().readout).toBe('80%')
      await user.click(screen.getByTestId('capture-view-original'))
      expect(zoomView().readout).toBe('80%')
      await user.click(screen.getAllByTestId('capture-filmstrip-item')[1] as HTMLElement)
      await vi.waitFor(() => {
        expect(screen.getByTestId('capture-zoom-level').textContent).toBe('Fit')
      })
      expect(screen.getByTestId('capture-draw-surface').getAttribute('data-zoom-kind')).toBe('fit')
    })
  })

  it('AC-66.8 ZOOM_RESET after the dirty confirm, and the offsets re-clamp on a resize', async () => {
    const observers: Array<{ callback: () => void }> = []
    class FakeResizeObserver {
      callback: () => void
      constructor(callback: () => void) {
        this.callback = callback
        observers.push(this)
      }
      observe(): void {}
      unobserve(): void {}
      disconnect(): void {}
    }
    vi.stubGlobal('ResizeObserver', FakeResizeObserver)
    const rect = { width: 800, height: 600 }
    await withSurfaceRect(rect, async () => {
      const surface = await openZoomSurface()
      await zoomInTimes(10)
      expect(zoomView().scale).toBeCloseTo(2, 4)
      await middleDrag(surface, 400, 300, -4600, 300)
      expect(zoomView().ox).toBeCloseTo(800 - 3200, 3)
      rect.width = 1000
      await act(async () => {
        for (const observer of observers) {
          observer.callback()
        }
      })
      expect(zoomView().scale).toBeCloseTo(2, 4)
      expect(zoomView().ox).toBeCloseTo(1000 - 3200, 3)
      await user.click(screen.getByTestId('capture-tool-arrow'))
      await drag(surface, 400, 300, 450, 330)
      expect(annotationCount()).toBe(1)
      await user.click(screen.getAllByTestId('capture-filmstrip-item')[1] as HTMLElement)
      await user.click(screen.getByTestId('capture-dirty-confirm'))
      await vi.waitFor(() => {
        expect(screen.getByTestId('capture-zoom-level').textContent).toBe('Fit')
      })
    })
  })

  it('AC-66.9 Ctrl+= / Ctrl+- / Ctrl+0 zoom from body and from the focused surface, one step per press, prevented', async () => {
    await withSurfaceRect({ width: 800, height: 600 }, async () => {
      const surface = await openZoomSurface()
      const seen: KeyboardEvent[] = []
      const record = (event: KeyboardEvent): void => {
        seen.push(event)
      }
      document.addEventListener('keydown', record)
      try {
        ;(document.activeElement as HTMLElement | null)?.blur()
        await user.keyboard('{Control>}={/Control}')
        expect(zoomView().readout).toBe('67%')
        expect(seen.at(-1)?.defaultPrevented).toBe(true)
        await user.keyboard('{Control>}-{/Control}')
        expect(zoomView().readout).toBe('50%')
        expect(seen.at(-1)?.defaultPrevented).toBe(true)
        await user.keyboard('{Control>}0{/Control}')
        expect(zoomView().readout).toBe('Fit')
        expect(seen.at(-1)?.defaultPrevented).toBe(true)
        surface.focus()
        expect(document.activeElement).toBe(surface)
        await user.keyboard('{Control>}={/Control}')
        expect(zoomView().readout).toBe('67%')
        await user.keyboard('{Control>}{Shift>}+{/Shift}{/Control}')
        expect(zoomView().readout).toBe('75%')
        await user.keyboard('{Control>}-{/Control}')
        expect(zoomView().readout).toBe('67%')
        expect(seen.at(-1)?.defaultPrevented).toBe(true)
        await user.keyboard('{Control>}0{/Control}')
        expect(zoomView().readout).toBe('Fit')
      } finally {
        document.removeEventListener('keydown', record)
      }
    })
  })

  it('AC-66.9 negative: text-entry focus, the confirm strip, no shot and plain keys change nothing', async () => {
    await withSurfaceRect({ width: 800, height: 600 }, async () => {
      const surface = await openZoomSurface()
      const seen: KeyboardEvent[] = []
      const record = (event: KeyboardEvent): void => {
        seen.push(event)
      }
      document.addEventListener('keydown', record)
      try {
        await user.click(screen.getByTestId('capture-zoom-in'))
        expect(zoomView().readout).toBe('67%')
        screen.getByTestId('capture-color').focus()
        await user.keyboard('{Control>}-{/Control}')
        expect(zoomView().readout).toBe('67%')
        expect(seen.at(-1)?.defaultPrevented).toBe(false)
        await user.click(screen.getByTestId('capture-tool-text'))
        screen.getByTestId('capture-font-size').focus()
        await user.keyboard('{Control>}0{/Control}')
        expect(zoomView().readout).toBe('67%')
        await act(async () => {
          dispatchPointer(surface, 'pointerdown', 400, 300)
          dispatchPointer(surface, 'pointerup', 400, 300)
        })
        screen.getByTestId('capture-text-draft').focus()
        await user.keyboard('{Control>}-{/Control}')
        expect(zoomView().readout).toBe('67%')
        await user.keyboard('{Escape}')
        await user.click(screen.getByTestId('capture-settings-toggle'))
        screen.getByTestId('capture-inbox-path').focus()
        await user.keyboard('{Control>}-{/Control}')
        expect(zoomView().readout).toBe('67%')
        ;(document.activeElement as HTMLElement | null)?.blur()
        await user.keyboard('=-0')
        expect(zoomView().readout).toBe('67%')
        await user.click(screen.getByTestId('capture-delete'))
        expect(screen.getByTestId('capture-confirm-strip')).toBeTruthy()
        expect(document.activeElement).toBe(screen.getByTestId('capture-delete-confirm-cancel'))
        await user.keyboard('{Control>}0{/Control}')
        expect(zoomView().readout).toBe('67%')
        expect(seen.at(-1)?.defaultPrevented).toBe(false)
      } finally {
        document.removeEventListener('keydown', record)
      }
    })
    cleanup()
    catalogItems = []
    queryClient.setQueryData(['captures'], { items: [], pendingInteractive: false })
    await renderPage()
    const seenNoShot: KeyboardEvent[] = []
    const recordNoShot = (event: KeyboardEvent): void => {
      seenNoShot.push(event)
    }
    document.addEventListener('keydown', recordNoShot)
    try {
      await user.keyboard('{Control>}={/Control}')
      expect(screen.getByTestId('capture-zoom-level').textContent).toBe('Fit')
      expect(seenNoShot.at(-1)?.defaultPrevented).toBe(false)
    } finally {
      document.removeEventListener('keydown', recordNoShot)
    }
  })

  it('AC-66.10 middle-drag and Space+drag pan the clamped offset without creating a mark', async () => {
    await withSurfaceRect({ width: 800, height: 600 }, async () => {
      const surface = await openZoomSurface()
      await zoomInTimes(10)
      expect(zoomView()).toMatchObject({ kind: 'scale', readout: '200%' })
      expect(zoomView().ox).toBeCloseTo(-1200, 3)
      expect(zoomView().oy).toBeCloseTo(-600, 3)
      await middleDrag(surface, 400, 300, 350, 270)
      expect(zoomView().ox).toBeCloseTo(-1250, 3)
      expect(zoomView().oy).toBeCloseTo(-630, 3)
      surface.focus()
      await user.keyboard('{ >}')
      await act(async () => {
        dispatchPointer(surface, 'pointerdown', 300, 300)
        dispatchPointer(surface, 'pointermove', 350, 330)
        dispatchPointer(surface, 'pointerup', 350, 330)
      })
      await user.keyboard('{/ }')
      expect(zoomView().ox).toBeCloseTo(-1200, 3)
      expect(zoomView().oy).toBeCloseTo(-600, 3)
      expect(annotationCount()).toBe(0)
      expect((screen.getByTestId('capture-undo') as HTMLButtonElement).disabled).toBe(true)
      expect(screen.queryByTestId('capture-save')).toBeNull()
      await drag(surface, 300, 300, 360, 340)
      expect(document.querySelectorAll('[data-annotation-type="arrow"]')).toHaveLength(1)
    })
  })

  it('AC-66.10 negative: no pan at Fit; Space on a toolbar button does not arm pan; a letterbox press creates nothing', async () => {
    await withSurfaceRect({ width: 800, height: 600 }, async () => {
      const surface = await openZoomSurface()
      const before = zoomView()
      await middleDrag(surface, 400, 300, 300, 250)
      expect(zoomView()).toEqual(before)
      await drag(surface, 400, 10, 450, 40)
      expect(annotationCount()).toBe(0)
      const box = screen.getByTestId('capture-tool-box')
      box.focus()
      await user.keyboard(' ')
      expect(box.getAttribute('aria-pressed')).toBe('true')
      await drag(surface, 300, 200, 360, 260)
      expect(document.querySelectorAll('[data-annotation-type="rect"]')).toHaveLength(1)
    })
  })

  it('AC-66.11 ZOOM_EXAMPLE through the real inputs: keys and a middle-drag, then an arrow lands on the zoomed pixel', async () => {
    await withSurfaceRect({ width: 800, height: 600 }, async () => {
      const surface = await openZoomSurface()
      expect(zoomView().scale).toBeCloseTo(0.5, 4)
      ;(document.activeElement as HTMLElement | null)?.blur()
      for (let i = 0; i < 10; i += 1) {
        await user.keyboard('{Control>}={/Control}')
      }
      expect(zoomView().scale).toBeCloseTo(2, 4)
      expect(zoomView().ox).toBeCloseTo(-1200, 3)
      expect(zoomView().oy).toBeCloseTo(-600, 3)
      await middleDrag(surface, 300, 200, 500, 350)
      expect(zoomView().ox).toBeCloseTo(-1000, 3)
      expect(zoomView().oy).toBeCloseTo(-450, 3)
      const content = screen.getByTestId('capture-zoom-content')
      expect(content.style.left).toBe('-1000px')
      expect(content.style.top).toBe('-450px')
      expect(content.style.width).toBe('3200px')
      expect(content.style.height).toBe('1800px')
      await user.click(screen.getByTestId('capture-tool-arrow'))
      await drag(surface, 400, 300, 500, 350)
      const line = document.querySelector('[data-annotation-type="arrow"] line') as SVGLineElement
      expect([line.getAttribute('x1'), line.getAttribute('y1')]).toEqual(['700', '375'])
      const mark = document.querySelector('[data-annotation-type="arrow"]') as SVGGElement
      expect([mark.getAttribute('x2'), mark.getAttribute('y2')]).toEqual(['750', '400'])
      // ZOOM_EXAMPLE negative oracle: the fit-only mapping of (400, 300) is (800, 450).
      expect(line.getAttribute('x1')).not.toBe('800')
      const radius = Number(screen.getByTestId('capture-handle-from').getAttribute('r'))
      expect(radius * 2).toBeCloseTo(HANDLE_RADIUS_CSS, 6)
      await user.click(screen.getByTestId('capture-tool-text'))
      await act(async () => {
        dispatchPointer(surface, 'pointerdown', 400, 300)
        dispatchPointer(surface, 'pointerup', 400, 300)
      })
      const draft = screen.getByTestId('capture-text-draft')
      expect(draft.style.left).toBe('400px')
      expect(draft.style.top).toBe('300px')
    })
  })

  it('AC-66.11 negative: a zero-length arrow and a sub-threshold body drag at s = 2 change nothing', async () => {
    await withSurfaceRect({ width: 800, height: 600 }, async () => {
      const surface = await openZoomSurface()
      await zoomInTimes(10)
      await middleDrag(surface, 300, 200, 500, 350)
      await user.click(screen.getByTestId('capture-tool-arrow'))
      await drag(surface, 400, 300, 400, 300)
      expect(annotationCount()).toBe(0)
      await drag(surface, 400, 300, 500, 300)
      expect(annotationCount()).toBe(1)
      expect(screen.getByTestId('capture-tool-select').getAttribute('aria-pressed')).toBe('true')
      const line = document.querySelector('[data-annotation-type="arrow"] line') as SVGLineElement
      const before = [line.getAttribute('x1'), line.getAttribute('y1'), line.getAttribute('x2'), line.getAttribute('y2')]
      await drag(surface, 450, 300, 452, 300)
      const after = document.querySelector('[data-annotation-type="arrow"] line') as SVGLineElement
      expect([after.getAttribute('x1'), after.getAttribute('y1'), after.getAttribute('x2'), after.getAttribute('y2')]).toEqual(
        before,
      )
      await user.click(screen.getByTestId('capture-undo'))
      expect(annotationCount()).toBe(0)
    })
  })

  // ── A-4 / AC-66.18: a mouse click on a toolbar button hands focus to the draw surface (CAPTURE_LOOK L5) ──
  it('AC-66.18 a mouse click on a tool focuses the surface, so Space+drag then pans without a mark', async () => {
    await withSurfaceRect({ width: 800, height: 600 }, async () => {
      const surface = await openZoomSurface()
      await zoomInTimes(10)
      const before = zoomView()
      await user.click(screen.getByTestId('capture-tool-arrow'))
      expect(screen.getByTestId('capture-tool-arrow').getAttribute('aria-pressed')).toBe('true')
      expect(document.activeElement).toBe(surface)
      await user.keyboard('{ >}')
      await act(async () => {
        dispatchPointer(surface, 'pointerdown', 300, 300)
        dispatchPointer(surface, 'pointermove', 350, 330)
        dispatchPointer(surface, 'pointerup', 350, 330)
      })
      await user.keyboard('{/ }')
      expect(zoomView().ox).toBeCloseTo(before.ox + 50, 3)
      expect(zoomView().oy).toBeCloseTo(before.oy + 30, 3)
      expect(annotationCount()).toBe(0)
    })
  })

  it('AC-66.18 negative: keyboard activation keeps focus on the button, and Space there does not arm pan', async () => {
    await withSurfaceRect({ width: 800, height: 600 }, async () => {
      const surface = await openZoomSurface()
      await zoomInTimes(10)
      const box = screen.getByTestId('capture-tool-box')
      box.focus()
      await user.keyboard('{Enter}')
      expect(box.getAttribute('aria-pressed')).toBe('true')
      expect(document.activeElement).toBe(box)
      const before = zoomView()
      await user.keyboard('{ >}')
      await act(async () => {
        dispatchPointer(surface, 'pointerdown', 300, 200)
        dispatchPointer(surface, 'pointermove', 360, 260)
        dispatchPointer(surface, 'pointerup', 360, 260)
      })
      await user.keyboard('{/ }')
      expect(document.activeElement).toBe(box)
      expect(zoomView().ox).toBeCloseTo(before.ox, 3)
      expect(zoomView().oy).toBeCloseTo(before.oy, 3)
      expect(document.querySelectorAll('[data-annotation-type="rect"]')).toHaveLength(1)
    })
  })

  // MEU-85 (Session 37): size scrub. Loaded marks carry no history, so Undo starts disabled.
  const SCRUB_BOX_A = { type: 'rect', x: 1, y: 1, width: 2, height: 2, color: '#E0AF68', stroke_width: 3 }
  const SCRUB_BOX_B = { type: 'rect', x: 5, y: 5, width: 2, height: 2, color: '#E0AF68', stroke_width: 3 }
  const SCRUB_TEXT = { type: 'text', x: 1, y: 6, text: 'Hi', color: '#FFFFFF', font_size: 16, bg_color: null }
  const SCRUB_BOX_WIDE = { ...SCRUB_BOX_B, stroke_width: 20 }
  const SCRUB_TEXT_BIG = { ...SCRUB_TEXT, x: 5, font_size: 40 }

  /** Stroke widths left to right: the viewport paints the selected mark first, so DOM order follows the selection. */
  function rectStrokes(): string[] {
    return Array.from(document.querySelectorAll('[data-annotation-type="rect"]'))
      .sort((a, b) => Number(a.getAttribute('x')) - Number(b.getAttribute('x')))
      .map((node) => node.getAttribute('stroke-width') ?? '')
  }

  function rectX(): string | null {
    return document.querySelector('[data-annotation-type="rect"]')?.getAttribute('x') ?? null
  }

  function textSize(): string | null {
    return document.querySelector('[data-annotation-type="text"]')?.getAttribute('font-size') ?? null
  }

  /** Font sizes left to right, as rectStrokes does for boxes. */
  function textSizes(): string[] {
    return Array.from(document.querySelectorAll('[data-annotation-type="text"]'))
      .sort((a, b) => Number(a.getAttribute('x')) - Number(b.getAttribute('x')))
      .map((node) => node.getAttribute('font-size') ?? '')
  }

  function markChip(index: number): HTMLElement {
    return screen.getByTestId('capture-mark-list').querySelectorAll('button')[index] as HTMLElement
  }

  function undoButton(): HTMLButtonElement {
    return screen.getByTestId('capture-undo') as HTMLButtonElement
  }

  function redoButton(): HTMLButtonElement {
    return screen.getByTestId('capture-redo') as HTMLButtonElement
  }

  async function selectMarkAt(index: number): Promise<void> {
    await user.click(screen.getByTestId('capture-mark-list').querySelectorAll('button')[index] as HTMLElement)
  }

  function scrubPointer(handle: HTMLElement, type: string, clientX: number, init: PointerEventInit = {}): void {
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
          ...init,
        }),
      )
    })
  }

  function wheelOver(id: string, deltaY: number): void {
    act(() => {
      screen
        .getByTestId(id)
        .dispatchEvent(new WheelEvent('wheel', { deltaY, deltaMode: 0, bubbles: true, cancelable: true }))
    })
  }

  function windowKey(type: 'keydown' | 'keyup', key: string): void {
    act(() => {
      window.dispatchEvent(new KeyboardEvent(type, { key, bubbles: true, cancelable: true }))
    })
  }

  function clickNow(element: HTMLElement): void {
    act(() => {
      fireEvent.click(element)
    })
  }

  /** Fake setTimeout only, so the scrub field's WHEEL_RESET_MS commit runs on demand (userEvent is not used inside). */
  async function withFakeTimers(work: () => Promise<void> | void): Promise<void> {
    vi.useFakeTimers({ toFake: ['setTimeout', 'clearTimeout'] })
    try {
      await work()
    } finally {
      vi.useRealTimers()
    }
  }

  function passBurst(): void {
    act(() => {
      vi.advanceTimersByTime(WHEEL_RESET_MS + 1)
    })
  }

  it('AC-85.6 a Stroke-label drag previews the selected box live and is one undo step; a font wheel burst is one step', async () => {
    detailAnnotations['shot-1'] = [SCRUB_BOX_A, SCRUB_TEXT]
    await openSelectedSurface()
    await selectMarkAt(0)
    expect(screen.queryByTestId('capture-stroke-scrub')).not.toBeNull()
    const handle = screen.getByTestId('capture-stroke-scrub')
    scrubPointer(handle, 'pointerdown', 100)
    scrubPointer(handle, 'pointermove', 110)
    scrubPointer(handle, 'pointermove', 120)
    expect(rectStrokes()).toEqual(['13'])
    expect((screen.queryByTestId('capture-save') as HTMLButtonElement | null)?.disabled).toBe(true)
    scrubPointer(handle, 'pointerup', 120)
    expect(rectStrokes()).toEqual(['13'])
    expect((screen.getByTestId('capture-stroke') as HTMLInputElement).value).toBe('13')
    await user.click(undoButton())
    expect(rectStrokes()).toEqual(['3'])
    await user.click(redoButton())
    expect(rectStrokes()).toEqual(['13'])
    await selectMarkAt(1)
    expect((screen.getByTestId('capture-font-size') as HTMLInputElement).value).toBe('16')
    await withFakeTimers(() => {
      wheelOver('capture-font-size', -100)
      wheelOver('capture-font-size', -100)
      wheelOver('capture-font-size', -100)
      expect(textSize()).toBe('19')
      expect(undoButton().disabled).toBe(true)
      passBurst()
      expect(undoButton().disabled).toBe(false)
      clickNow(undoButton())
      expect(textSize()).toBe('16')
    })
  })

  it('AC-85.6 negative: Escape mid-drag restores stroke 3 and adds no history', async () => {
    detailAnnotations['shot-1'] = [SCRUB_BOX_A]
    await openSelectedSurface()
    await selectMarkAt(0)
    expect(screen.queryByTestId('capture-stroke-scrub')).not.toBeNull()
    const handle = screen.getByTestId('capture-stroke-scrub')
    scrubPointer(handle, 'pointerdown', 100)
    scrubPointer(handle, 'pointermove', 120)
    expect(rectStrokes()).toEqual(['13'])
    act(() => {
      ;(document.activeElement ?? document.body).dispatchEvent(
        new KeyboardEvent('keydown', { key: 'Escape', bubbles: true, cancelable: true }),
      )
    })
    scrubPointer(handle, 'pointerup', 120)
    expect(rectStrokes()).toEqual(['3'])
    expect((screen.getByTestId('capture-stroke') as HTMLInputElement).value).toBe('3')
    expect(undoButton().disabled).toBe(true)
  })

  it('AC-85.6 a drag that leaves the label without pointer capture keeps scrubbing and is one undo step', async () => {
    // S6 A-3: the moves and the release land off the label, as they do when capture never takes effect.
    detailAnnotations['shot-1'] = [SCRUB_BOX_A]
    await openSelectedSurface()
    await selectMarkAt(0)
    expect(screen.queryByTestId('capture-stroke-scrub')).not.toBeNull()
    const handle = screen.getByTestId('capture-stroke-scrub')
    scrubPointer(handle, 'pointerdown', 100)
    scrubPointer(document.body, 'pointermove', 110)
    scrubPointer(document.body, 'pointermove', 140)
    expect(rectStrokes()).toEqual(['23'])
    scrubPointer(document.body, 'pointerup', 140)
    expect((screen.getByTestId('capture-stroke') as HTMLInputElement).value).toBe('23')
    scrubPointer(document.body, 'pointermove', 200)
    expect(rectStrokes()).toEqual(['23'])
    await user.click(undoButton())
    expect(rectStrokes()).toEqual(['3'])
    expect(undoButton().disabled).toBe(true)
  })

  it('AC-85.7 with no applicable mark a Stroke drag sets only the field, and the next box uses it', async () => {
    detailAnnotations['shot-1'] = [SCRUB_BOX_A]
    const surface = await openSelectedSurface()
    await user.click(screen.getByTestId('capture-tool-box'))
    expect(screen.queryByTestId('capture-stroke-scrub')).not.toBeNull()
    const handle = screen.getByTestId('capture-stroke-scrub')
    scrubPointer(handle, 'pointerdown', 100)
    scrubPointer(handle, 'pointermove', 110)
    scrubPointer(handle, 'pointerup', 110)
    expect((screen.getByTestId('capture-stroke') as HTMLInputElement).value).toBe('8')
    expect(rectStrokes()).toEqual(['3'])
    expect(undoButton().disabled).toBe(true)
    await drag(surface, 110, 110, 190, 190)
    expect(rectStrokes()).toEqual(['3', '8'])
  })

  it('AC-85.8 typed edits keep one undo step per change, and a typed change ends an open wheel burst', async () => {
    detailAnnotations['shot-1'] = [SCRUB_BOX_A, SCRUB_TEXT]
    await openSelectedSurface()
    await selectMarkAt(0)
    expect(screen.queryByTestId('capture-stroke-scrub')).not.toBeNull()
    const stroke = screen.getByTestId('capture-stroke')
    fireEvent.change(stroke, { target: { value: '5' } })
    fireEvent.change(stroke, { target: { value: '7' } })
    expect(rectStrokes()).toEqual(['7'])
    await user.click(undoButton())
    expect(rectStrokes()).toEqual(['5'])
    await user.click(undoButton())
    expect(rectStrokes()).toEqual(['3'])
    await selectMarkAt(1)
    await withFakeTimers(() => {
      wheelOver('capture-font-size', -100)
      expect(textSize()).toBe('17')
      act(() => {
        fireEvent.change(screen.getByTestId('capture-font-size'), { target: { value: '20' } })
      })
      expect(textSize()).toBe('20')
      passBurst()
      clickNow(undoButton())
      expect(textSize()).toBe('17')
      clickNow(undoButton())
      expect(textSize()).toBe('16')
      expect(undoButton().disabled).toBe(true)
    })
  })

  it('AC-85.8 negative: a typed 0 changes no mark and adds no history', async () => {
    detailAnnotations['shot-1'] = [SCRUB_BOX_A]
    await openSelectedSurface()
    await selectMarkAt(0)
    expect(screen.queryByTestId('capture-stroke-scrub')).not.toBeNull()
    fireEvent.change(screen.getByTestId('capture-stroke'), { target: { value: '0' } })
    expect(rectStrokes()).toEqual(['3'])
    expect(undoButton().disabled).toBe(true)
  })

  it('AC-85.3 an invalid Stroke field scrubs from the selected box stroke 20, not the default 3', async () => {
    // Review round 1 F1 (SCRUB_BASE): the fallback is the applicable selected mark's own value.
    detailAnnotations['shot-1'] = [SCRUB_BOX_WIDE]
    await openSelectedSurface()
    await selectMarkAt(0)
    expect(screen.queryByTestId('capture-stroke-scrub')).not.toBeNull()
    const stroke = screen.getByTestId('capture-stroke')
    act(() => {
      stroke.focus()
    })
    fireEvent.change(stroke, { target: { value: 'abc' } })
    expect(rectStrokes()).toEqual(['20'])
    fireEvent.keyDown(stroke, { key: 'ArrowUp' })
    fireEvent.keyUp(stroke, { key: 'ArrowUp' })
    expect(rectStrokes()).toEqual(['21'])
    expect((stroke as HTMLInputElement).value).toBe('21')
    await user.click(undoButton())
    expect(rectStrokes()).toEqual(['20'])
  })

  it('AC-85.4 an invalid Size field scrubs from the selected text size 40, not the default 16', async () => {
    detailAnnotations['shot-1'] = [SCRUB_TEXT_BIG]
    await openSelectedSurface()
    await selectMarkAt(0)
    expect(screen.queryByTestId('capture-font-size-scrub')).not.toBeNull()
    const size = screen.getByTestId('capture-font-size')
    act(() => {
      size.focus()
    })
    fireEvent.change(size, { target: { value: '' } })
    expect(textSizes()).toEqual(['40'])
    fireEvent.keyDown(size, { key: 'ArrowUp' })
    fireEvent.keyUp(size, { key: 'ArrowUp' })
    expect(textSizes()).toEqual(['41'])
    expect((size as HTMLInputElement).value).toBe('41')
  })

  it('AC-85.9 the Stroke and Size handles are hidden, untabbable labels; Tab reaches the inputs, which keep their names', async () => {
    detailAnnotations['shot-1'] = [SCRUB_BOX_A]
    await openSelectedSurface()
    await selectMarkAt(0)
    expect(screen.queryByTestId('capture-stroke-scrub')).not.toBeNull()
    const strokeHandle = screen.getByTestId('capture-stroke-scrub')
    expect(strokeHandle.textContent).toBe('Stroke')
    expect(strokeHandle.getAttribute('aria-hidden')).toBe('true')
    expect(strokeHandle.hasAttribute('tabindex')).toBe(false)
    expect(screen.getByTestId('capture-stroke').getAttribute('aria-label')).toBe('Stroke width')
    act(() => {
      screen.getByTestId('capture-named-color').focus()
    })
    const visited: string[] = []
    for (let step = 0; step < 6 && document.activeElement !== screen.getByTestId('capture-stroke'); step += 1) {
      await user.tab()
      visited.push(document.activeElement?.getAttribute('data-testid') ?? '')
    }
    expect(document.activeElement).toBe(screen.getByTestId('capture-stroke'))
    expect(visited.filter((id) => id.endsWith('-scrub'))).toEqual([])
    await user.click(screen.getByTestId('capture-tool-text'))
    expect(screen.queryByTestId('capture-font-size-scrub')).not.toBeNull()
    const sizeHandle = screen.getByTestId('capture-font-size-scrub')
    expect(sizeHandle.textContent).toBe('Size')
    expect(sizeHandle.getAttribute('aria-hidden')).toBe('true')
    expect(sizeHandle.hasAttribute('tabindex')).toBe(false)
    expect(screen.getByTestId('capture-font-size').getAttribute('aria-label')).toBe('Font size')
  })

  it('AC-85.9 negative: the stroke input is not inside a <label>', async () => {
    detailAnnotations['shot-1'] = [SCRUB_BOX_A]
    await openSelectedSurface()
    await selectMarkAt(0)
    expect(screen.queryByTestId('capture-stroke-scrub')).not.toBeNull()
    expect(screen.getByTestId('capture-stroke').closest('label')).toBeNull()
  })

  it('AC-85.12 (a) a nudge during a wheel burst finishes it first: two Undos give stroke 4 at the start, then stroke 3', async () => {
    detailAnnotations['shot-1'] = [SCRUB_BOX_A]
    const surface = await openSelectedSurface()
    await selectMarkAt(0)
    expect(screen.queryByTestId('capture-stroke-scrub')).not.toBeNull()
    const x0 = rectX()
    act(() => {
      surface.focus()
    })
    await withFakeTimers(() => {
      wheelOver('capture-stroke', -100)
      expect(rectStrokes()).toEqual(['4'])
      expect((screen.queryByTestId('capture-save') as HTMLButtonElement | null)?.disabled).toBe(true)
      windowKey('keydown', 'ArrowRight')
      windowKey('keyup', 'ArrowRight')
      expect(rectX()).not.toBe(x0)
      passBurst()
      clickNow(undoButton())
      expect(rectStrokes()).toEqual(['4'])
      expect(rectX()).toBe(x0)
      clickNow(undoButton())
      expect(rectStrokes()).toEqual(['3'])
      expect(undoButton().disabled).toBe(true)
    })
  })

  it('AC-85.12 (b) selecting another mark mid-burst finishes the burst on the first mark only', async () => {
    detailAnnotations['shot-1'] = [SCRUB_BOX_A, SCRUB_BOX_B]
    const surface = await openSelectedSurface()
    await selectMarkAt(0)
    expect(screen.queryByTestId('capture-stroke-scrub')).not.toBeNull()
    await withFakeTimers(() => {
      wheelOver('capture-stroke', -100)
      expect(rectStrokes()).toEqual(['4', '3'])
      act(() => {
        dispatchPointer(surface, 'pointerdown', 125, 150)
        dispatchPointer(surface, 'pointerup', 125, 150)
      })
      expect((screen.getByTestId('capture-stroke') as HTMLInputElement).value).toBe('3')
      expect(rectStrokes()).toEqual(['4', '3'])
      passBurst()
      expect(rectStrokes()).toEqual(['4', '3'])
      clickNow(undoButton())
      expect(rectStrokes()).toEqual(['3', '3'])
      expect(undoButton().disabled).toBe(true)
    })
  })

  it('AC-85.12 (b) keyboard-selecting a stroke-20 box mid-burst rebases the next notch on it: 21, two undo steps', async () => {
    // Review round 1 F2: Enter on B's chip (a click with no pointer, blur or pointerleave) between notches.
    detailAnnotations['shot-1'] = [SCRUB_BOX_A, SCRUB_BOX_WIDE]
    await openSelectedSurface()
    await selectMarkAt(0)
    expect(screen.queryByTestId('capture-stroke-scrub')).not.toBeNull()
    act(() => {
      markChip(1).focus()
    })
    await withFakeTimers(() => {
      wheelOver('capture-stroke', -100)
      expect(rectStrokes()).toEqual(['4', '20'])
      clickNow(markChip(1))
      expect((screen.getByTestId('capture-stroke') as HTMLInputElement).value).toBe('20')
      wheelOver('capture-stroke', -100)
      expect(rectStrokes()).toEqual(['4', '21'])
      passBurst()
      clickNow(undoButton())
      expect(rectStrokes()).toEqual(['4', '20'])
      clickNow(undoButton())
      expect(rectStrokes()).toEqual(['3', '20'])
      expect(undoButton().disabled).toBe(true)
    })
  })

  it('AC-85.12 (b) the same holds for two text marks sharing the Size field: 17 on the first, 41 on the second', async () => {
    detailAnnotations['shot-1'] = [SCRUB_TEXT, SCRUB_TEXT_BIG]
    await openSelectedSurface()
    await selectMarkAt(0)
    expect(screen.queryByTestId('capture-font-size-scrub')).not.toBeNull()
    act(() => {
      markChip(1).focus()
    })
    await withFakeTimers(() => {
      wheelOver('capture-font-size', -100)
      expect(textSizes()).toEqual(['17', '40'])
      clickNow(markChip(1))
      expect((screen.getByTestId('capture-font-size') as HTMLInputElement).value).toBe('40')
      wheelOver('capture-font-size', -100)
      expect(textSizes()).toEqual(['17', '41'])
      passBurst()
      clickNow(undoButton())
      expect(textSizes()).toEqual(['17', '40'])
      clickNow(undoButton())
      expect(textSizes()).toEqual(['16', '40'])
      expect(undoButton().disabled).toBe(true)
    })
  })

  it('AC-85.12 (c) Escape on the window cancels an unfocused wheel burst without history', async () => {
    detailAnnotations['shot-1'] = [SCRUB_BOX_A]
    await openSelectedSurface()
    await selectMarkAt(0)
    expect(screen.queryByTestId('capture-stroke-scrub')).not.toBeNull()
    act(() => {
      ;(document.activeElement as HTMLElement | null)?.blur()
    })
    await withFakeTimers(() => {
      wheelOver('capture-stroke', -100)
      expect(rectStrokes()).toEqual(['4'])
      windowKey('keydown', 'Escape')
      expect(rectStrokes()).toEqual(['3'])
      expect((screen.getByTestId('capture-stroke') as HTMLInputElement).value).toBe('3')
      passBurst()
      expect(rectStrokes()).toEqual(['3'])
      expect(undoButton().disabled).toBe(true)
    })
  })

  it('AC-85.12 (d) Undo and Redo are held while a wheel burst is open', async () => {
    detailAnnotations['shot-1'] = [SCRUB_BOX_A]
    const surface = await openSelectedSurface()
    await selectMarkAt(0)
    expect(screen.queryByTestId('capture-stroke-scrub')).not.toBeNull()
    const x0 = rectX()
    act(() => {
      surface.focus()
    })
    windowKey('keydown', 'ArrowRight')
    windowKey('keyup', 'ArrowRight')
    windowKey('keydown', 'ArrowRight')
    windowKey('keyup', 'ArrowRight')
    await user.click(undoButton())
    const x1 = rectX()
    expect(x1).not.toBe(x0)
    expect(redoButton().disabled).toBe(false)
    // Undo clears the selection, so select the box again before the wheel notch.
    await selectMarkAt(0)
    await withFakeTimers(() => {
      wheelOver('capture-stroke', -100)
      expect(rectStrokes()).toEqual(['4'])
      expect(undoButton().disabled).toBe(true)
      expect(redoButton().disabled).toBe(true)
      passBurst()
      expect(undoButton().disabled).toBe(false)
      clickNow(undoButton())
      expect(rectStrokes()).toEqual(['3'])
      expect(rectX()).toBe(x1)
      clickNow(undoButton())
      expect(rectX()).toBe(x0)
      expect(undoButton().disabled).toBe(true)
    })
  })

  it('AC-85.12 (e) a shot change mid-burst discards the burst and adds nothing to the new shot', async () => {
    detailAnnotations['shot-1'] = [SCRUB_BOX_A]
    await openSelectedSurface()
    await selectMarkAt(0)
    expect(screen.queryByTestId('capture-stroke-scrub')).not.toBeNull()
    await withFakeTimers(async () => {
      wheelOver('capture-stroke', -100)
      expect(rectStrokes()).toEqual(['4'])
      clickNow(screen.getAllByTestId('capture-filmstrip-item')[1] as HTMLElement)
      clickNow(screen.getByTestId('capture-dirty-confirm'))
      await vi.waitFor(() => {
        expect(screen.getAllByTestId('capture-filmstrip-item')[1]?.getAttribute('aria-current')).toBe('true')
      })
      passBurst()
      await flush()
      expect(document.querySelectorAll('[data-annotation-type="rect"]')).toHaveLength(0)
      expect(undoButton().disabled).toBe(true)
    })
  })

  // ── MEU-99 Capture canvas history chords (Session 43 plan AC-99.1–AC-99.5) ──────────
  describe('MEU-99 canvas history chords', () => {
    type ChordInit = { ctrl?: boolean; meta?: boolean; shift?: boolean; alt?: boolean; repeat?: boolean; composing?: boolean }

    /** Dispatches one keydown on `target` inside act and returns it, so a test reads `defaultPrevented`. */
    async function chord(target: EventTarget, key: string, init: ChordInit = { ctrl: true }): Promise<KeyboardEvent> {
      const event = new KeyboardEvent('keydown', {
        key,
        ctrlKey: init.ctrl ?? false,
        metaKey: init.meta ?? false,
        shiftKey: init.shift ?? false,
        altKey: init.alt ?? false,
        repeat: init.repeat ?? false,
        isComposing: init.composing ?? false,
        bubbles: true,
        cancelable: true,
      })
      await act(async () => {
        target.dispatchEvent(event)
      })
      return event
    }

    function rects(): number {
      return document.querySelectorAll('[data-annotation-type="rect"]').length
    }

    /** Box 1 covers image (1,1)-(3,3) and box 2 (4,4)-(7,7) at the 25 px/px fit; box 2 ends selected. */
    async function drawTwoBoxes(surface: HTMLElement): Promise<void> {
      await user.click(screen.getByTestId('capture-tool-box'))
      await drag(surface, 25, 25, 75, 75)
      await user.click(screen.getByTestId('capture-tool-box'))
      await drag(surface, 100, 100, 175, 175)
      expect(rects(), 'two boxes drawn').toBe(2)
    }

    async function focusSurface(surface: HTMLElement): Promise<void> {
      await act(async () => {
        surface.focus()
      })
    }

    async function blurToBody(): Promise<void> {
      await act(async () => {
        ;(document.activeElement as HTMLElement | null)?.blur()
      })
      expect(document.activeElement).toBe(document.body)
    }

    it('AC-99.1 on the focused image Ctrl+Z undoes, Ctrl+Y and Ctrl+Shift+Z redo, Meta+Z and a held Ctrl+Z undo; Ctrl+Alt+Z does nothing', async () => {
      const surface = await openSelectedSurface()
      await drawTwoBoxes(surface)
      await focusSurface(surface)
      const steps: Array<[string, ChordInit, number]> = [
        ['z', { ctrl: true }, 1],
        ['z', { ctrl: true }, 0],
        ['y', { ctrl: true }, 1],
        ['Z', { ctrl: true, shift: true }, 2],
        ['z', { meta: true }, 1],
        ['z', { ctrl: true, repeat: true }, 0],
        ['y', { ctrl: true }, 1],
      ]
      for (const [key, init, count] of steps) {
        const label = `${JSON.stringify(init)} ${key}`
        const event = await chord(surface, key, init)
        expect(rects(), label).toBe(count)
        expect(event.defaultPrevented, `${label} prevented`).toBe(true)
      }
      const alt = await chord(surface, 'z', { ctrl: true, alt: true })
      expect(rects(), 'Ctrl+Alt+Z').toBe(1)
      expect(alt.defaultPrevented, 'Ctrl+Alt+Z not prevented').toBe(false)
    })

    it('AC-99.2 with focus on the page body, Ctrl+Z on the window undoes one step', async () => {
      const surface = await openSelectedSurface()
      await drawTwoBoxes(surface)
      await blurToBody()
      const event = await chord(window, 'z')
      expect(rects()).toBe(1)
      expect(event.defaultPrevented).toBe(true)
    })

    it('AC-99.3 (a) (b) the text draft and the font size field keep Ctrl+Z', async () => {
      const surface = await openSelectedSurface()
      await drawTwoBoxes(surface)
      await user.click(screen.getByTestId('capture-tool-text'))
      await act(async () => {
        dispatchPointer(surface, 'pointerdown', 25, 175)
        dispatchPointer(surface, 'pointerup', 25, 175)
      })
      const draft = screen.getByTestId('capture-text-draft')
      await act(async () => {
        draft.focus()
      })
      const inDraft = await chord(draft, 'z')
      expect(inDraft.defaultPrevented, '(a) draft not prevented').toBe(false)
      expect(rects(), '(a) draft').toBe(2)
      await user.keyboard('{Escape}')
      expect(screen.queryByTestId('capture-text-draft')).toBeNull()
      await user.click(screen.getByTestId('capture-tool-text'))
      const font = screen.getByTestId('capture-font-size')
      await act(async () => {
        font.focus()
      })
      const inFont = await chord(font, 'z')
      expect(inFont.defaultPrevented, '(b) font size not prevented').toBe(false)
      expect(rects(), '(b) font size').toBe(2)
    })

    it('AC-99.3 (c) (d) an open confirm strip or an aria-modal dialog blocks the chords', async () => {
      const surface = await openSelectedSurface()
      await drawTwoBoxes(surface)
      await user.click(screen.getByTestId('capture-delete'))
      await vi.waitFor(() => {
        expect(document.activeElement).toBe(screen.getByTestId('capture-delete-confirm-cancel'))
      })
      const onCancel = await chord(screen.getByTestId('capture-delete-confirm-cancel'), 'z')
      expect(onCancel.defaultPrevented, '(c) confirm button not prevented').toBe(false)
      expect(rects(), '(c) confirm button').toBe(2)
      await blurToBody()
      const bodyWithConfirm = await chord(window, 'z')
      expect(bodyWithConfirm.defaultPrevented, '(c) body with confirm not prevented').toBe(false)
      expect(rects(), '(c) body with confirm').toBe(2)
      await user.click(screen.getByTestId('capture-delete-confirm-cancel'))
      expect(screen.queryByTestId('capture-confirm-strip')).toBeNull()
      const modal = document.createElement('div')
      modal.setAttribute('aria-modal', 'true')
      document.body.appendChild(modal)
      try {
        await blurToBody()
        const withModal = await chord(window, 'z')
        expect(withModal.defaultPrevented, '(d) aria-modal not prevented').toBe(false)
        expect(rects(), '(d) aria-modal').toBe(2)
      } finally {
        modal.remove()
      }
    })

    it('AC-99.3 (e) during a live move Ctrl+Z is swallowed and the pointer-up still commits the move', async () => {
      const surface = await openSelectedSurface()
      await drawTwoBoxes(surface)
      await focusSurface(surface)
      const firstX = () => document.querySelector('[data-annotation-type="rect"]')?.getAttribute('x')
      const x0 = firstX()
      await act(async () => {
        dispatchPointer(surface, 'pointerdown', 25, 50)
        dispatchPointer(surface, 'pointermove', 60, 50)
      })
      const midGesture = await chord(surface, 'z')
      expect(midGesture.defaultPrevented, '(e) prevented mid-gesture').toBe(true)
      expect(rects(), '(e) mid-gesture').toBe(2)
      await act(async () => {
        dispatchPointer(surface, 'pointerup', 60, 50)
      })
      expect(rects()).toBe(2)
      expect(firstX(), '(e) the move committed').not.toBe(x0)
    })

    it('AC-99.3 (f) (g) (h) composition, toolbar focus, a COLOR_FOCUS_IDS control and an empty history', async () => {
      const surface = await openSelectedSurface()
      await focusSurface(surface)
      const empty = await chord(surface, 'z')
      expect(empty.defaultPrevented, '(h) empty history prevented').toBe(true)
      expect(rects(), '(h) empty history').toBe(0)
      await drawTwoBoxes(surface)
      await focusSurface(surface)
      const composing = await chord(surface, 'z', { ctrl: true, composing: true })
      expect(composing.defaultPrevented, '(f) composing not prevented').toBe(false)
      expect(rects(), '(f) composing').toBe(2)
      const undo = screen.getByTestId('capture-undo')
      await act(async () => {
        undo.focus()
      })
      const onUndo = await chord(undo, 'z')
      expect(onUndo.defaultPrevented, '(g) toolbar button prevented').toBe(true)
      expect(rects(), '(g) toolbar button').toBe(1)
      await user.click(screen.getByTestId('capture-tool-box'))
      const named = screen.getByTestId('capture-named-color')
      await act(async () => {
        named.focus()
      })
      const onNamed = await chord(named, 'z')
      expect(onNamed.defaultPrevented, '(g) named color not prevented').toBe(false)
      expect(rects(), '(g) named color').toBe(1)
    })

    it('AC-99.4 Ctrl+Z, Ctrl+Z, Ctrl+Y ends where Undo, Undo, Redo clicks end, and Save posts the same body', async () => {
      async function run(drive: 'chord' | 'button') {
        cleanup()
        queryClient.clear()
        queryClient.setQueryData(['captures'], { items: [SHOT, SHOT_B], pendingInteractive: false })
        queryClient.setQueryData(['settings', 'capture'], captureSettings)
        fetches.length = 0
        const surface = await openSelectedSurface()
        await drawTwoBoxes(surface)
        if (drive === 'chord') {
          await focusSurface(surface)
          await chord(surface, 'z')
          await chord(surface, 'z')
          await chord(surface, 'y')
        } else {
          await user.click(screen.getByTestId('capture-undo'))
          await user.click(screen.getByTestId('capture-undo'))
          await user.click(screen.getByTestId('capture-redo'))
        }
        const marks = Array.from(document.querySelectorAll('[data-annotation-type]')).map((node) => node.outerHTML)
        const selected = Array.from(screen.getByTestId('capture-mark-list').querySelectorAll('button')).filter(
          (button) => button.getAttribute('aria-pressed') === 'true',
        ).length
        const saveMounted = screen.queryByTestId('capture-save') !== null
        if (saveMounted) {
          await user.click(screen.getByTestId('capture-save'))
        }
        await vi.waitFor(() => {
          expect(fetches.filter((row) => row.method === 'POST' && row.url.includes('/annotate'))).toHaveLength(1)
        })
        const body = fetches.find((row) => row.method === 'POST' && row.url.includes('/annotate'))?.body
        return { marks, selected, saveMounted, body }
      }
      const byChord = await run('chord')
      const byButton = await run('button')
      expect(byButton.selected, 'button run selects nothing').toBe(0)
      expect(byChord).toEqual(byButton)
    })

    it('AC-99.5 Undo and Redo name their chords: aria-keyshortcuts and the focused hint, with the aria-label unchanged', async () => {
      await openSelectedSurface()
      const rows: Array<[string, string, string, string]> = [
        ['capture-undo', 'Undo', 'Control+Z', 'Undo (Ctrl+Z)'],
        ['capture-redo', 'Redo', 'Control+Y', 'Redo (Ctrl+Y)'],
      ]
      for (const [id, name, keys, hint] of rows) {
        const button = screen.getByTestId(id)
        expect(button.getAttribute('aria-keyshortcuts'), `${id} aria-keyshortcuts`).toBe(keys)
        expect(button.getAttribute('aria-label'), `${id} aria-label`).toBe(name)
        expect(focusedHint(toolbarFocusTarget(id), `${id}-hint`), `${id} hint`).toBe(hint)
      }
    })
  })

  // ── MEU-100 Capture resize handles (Session 43 plan AC-100.6–AC-100.9) ──────────
  describe('MEU-100 resize handles', () => {
    // At the 25 px/px fit a box drawn 25,25 → 100,100 covers image (1,1)-(4,4); its se handle sits at CSS (100,100)
    // and CSS (150,175) is image (6,7).
    const geometry = (type: string) => rectGeometry(document.querySelector(`[data-annotation-type="${type}"]`) ?? undefined)
    const resizeHandles = () => Array.from(document.querySelectorAll('[data-testid^="capture-handle-resize-"]'))
    const surfaceEl = () => screen.getByTestId('capture-draw-surface')

    async function drawWith(surface: HTMLElement, toolId: string): Promise<void> {
      await user.click(screen.getByTestId(toolId))
      await drag(surface, 25, 25, 100, 100)
      expect(screen.getByTestId('capture-tool-select').getAttribute('aria-pressed'), `${toolId} hands over to Select`).toBe('true')
    }

    async function key(target: EventTarget, init: KeyboardEventInit): Promise<void> {
      await act(async () => {
        target.dispatchEvent(new KeyboardEvent('keydown', { bubbles: true, cancelable: true, ...init }))
      })
    }

    it('AC-100.6 dragging the se handle of a selected box, highlight, redact or eraser resizes it as one history step; Save carries it', async () => {
      const surface = await openSelectedSurface()
      const cases: Array<[string, string]> = [
        ['capture-tool-box', 'rect'],
        ['capture-tool-highlight', 'highlight'],
        ['capture-tool-redact', 'redact'],
        ['capture-tool-eraser', 'eraser'],
      ]
      for (const [toolId, type] of cases) {
        await drawWith(surface, toolId)
        expect(geometry(type), `${type} drawn`).toEqual([1, 1, 3, 3])
        await drag(surface, 100, 100, 150, 175)
        expect(geometry(type), `${type} resized`).toEqual([1, 1, 5, 6])
        await user.click(screen.getByTestId('capture-undo'))
        expect(document.querySelectorAll(`[data-annotation-type="${type}"]`), `${type} kept by one Undo`).toHaveLength(1)
        expect(geometry(type), `${type} after Undo`).toEqual([1, 1, 3, 3])
        await user.click(screen.getByTestId('capture-redo'))
        expect(geometry(type), `${type} after Redo`).toEqual([1, 1, 5, 6])
      }
      const saved = (await saveBody()) as { annotations: unknown[] }
      const resized = { x: 1, y: 1, width: 5, height: 6 }
      expect(saved.annotations).toEqual([
        { type: 'rect', ...resized, color: expect.any(String), stroke_width: expect.any(Number) },
        { type: 'highlight', ...resized, color: expect.any(String), opacity: 0.35 },
        { type: 'redact', ...resized, color: '#000000' },
        { type: 'eraser', ...resized },
      ])
    })

    it('AC-100.7 a resize drag previews live; Escape, pointercancel and a sub-threshold move record nothing', async () => {
      const surface = await openSelectedSurface()
      await drawWith(surface, 'capture-tool-box')
      await act(async () => {
        dispatchPointer(surface, 'pointerdown', 100, 100)
        dispatchPointer(surface, 'pointermove', 150, 175)
      })
      expect(geometry('rect'), 'preview before Escape').toEqual([1, 1, 5, 6])
      await key(surface, { key: 'Escape' })
      expect(geometry('rect'), 'after Escape').toEqual([1, 1, 3, 3])
      await act(async () => {
        dispatchPointer(surface, 'pointerup', 150, 175)
      })
      expect(geometry('rect'), 'pointerup after Escape').toEqual([1, 1, 3, 3])
      await act(async () => {
        dispatchPointer(surface, 'pointerdown', 100, 100)
        dispatchPointer(surface, 'pointermove', 150, 175)
      })
      expect(geometry('rect'), 'preview before pointercancel').toEqual([1, 1, 5, 6])
      await act(async () => {
        dispatchPointer(surface, 'pointercancel', 150, 175)
      })
      expect(geometry('rect'), 'after pointercancel').toEqual([1, 1, 3, 3])
      await act(async () => {
        dispatchPointer(surface, 'pointerdown', 100, 100)
        dispatchPointer(surface, 'pointermove', 101, 101)
        dispatchPointer(surface, 'pointerup', 101, 101)
      })
      expect(geometry('rect'), 'below DRAG_THRESHOLD_CSS').toEqual([1, 1, 3, 3])
      const saved = (await saveBody()) as { annotations: unknown[] }
      expect(saved.annotations).toEqual([expect.objectContaining({ type: 'rect', x: 1, y: 1, width: 3, height: 3 })])
      // No resize step was recorded: one Undo removes the drawn box and leaves nothing to undo.
      await user.click(screen.getByTestId('capture-undo'))
      expect(document.querySelectorAll('[data-annotation-type="rect"]'), 'one Undo removes the box').toHaveLength(0)
      expect((screen.getByTestId('capture-undo') as HTMLButtonElement).disabled, 'Undo disabled').toBe(true)
    })

    it('AC-100.8 a selected box shows eight resize handles; an arrow, no selection and the annotated view show none; the hover cursor follows the handle and Space wins', async () => {
      queryClient.setQueryData(['captures'], {
        items: [{ ...SHOT, annotated_path: 'C:/shots/a.annotated.png' }, SHOT_B],
        pendingInteractive: false,
      })
      const surface = await openSelectedSurface()
      await drawWith(surface, 'capture-tool-box')
      const ids = resizeHandles().map((element) => element.getAttribute('data-testid'))
      expect(ids.sort(), 'eight handles').toEqual(
        ['nw', 'n', 'ne', 'e', 'se', 's', 'sw', 'w'].map((id) => `capture-handle-resize-${id}`).sort(),
      )
      for (const element of resizeHandles()) {
        expect(element.tagName.toLowerCase()).toBe('rect')
        // RESIZE_HANDLE_CSS (8) over the 25 px/px fit, in image units.
        expect(Number(element.getAttribute('width'))).toBeCloseTo(8 / 25, 5)
        expect(Number(element.getAttribute('height'))).toBeCloseTo(8 / 25, 5)
      }
      // The ne handle is image (4,1), CSS (100,25); CSS (62,45) is inside the box, clear of every handle.
      await act(async () => {
        dispatchPointer(surface, 'pointermove', 100, 25)
      })
      expect(surfaceEl().className, 'hover ne').toContain('cursor-nesw-resize')
      await act(async () => {
        dispatchPointer(surface, 'pointermove', 62, 45)
      })
      expect(surfaceEl().className, 'hover interior').not.toMatch(/-resize/)
      await act(async () => {
        surface.focus()
      })
      await key(surface, { key: ' ' })
      await act(async () => {
        dispatchPointer(surface, 'pointermove', 100, 25)
      })
      expect(surfaceEl().className, 'Space held').toContain('cursor-grab')
      expect(surfaceEl().className, 'Space held').not.toMatch(/-resize/)
      await act(async () => {
        surface.dispatchEvent(new KeyboardEvent('keyup', { key: ' ', bubbles: true, cancelable: true }))
      })
      await user.click(screen.getByTestId('capture-tool-arrow'))
      await drag(surface, 125, 125, 175, 175)
      expect(document.querySelectorAll('[data-annotation-type="arrow"]'), 'arrow drawn').toHaveLength(1)
      expect(resizeHandles(), 'selected arrow').toHaveLength(0)
      expect(surfaceEl().className, 'selected arrow keeps no resize cursor').not.toMatch(/-resize/)
      await act(async () => {
        dispatchPointer(surface, 'pointerdown', 160, 10)
        dispatchPointer(surface, 'pointerup', 160, 10)
      })
      expect(resizeHandles(), 'no selection').toHaveLength(0)
      // On the 8×8 fixture the arrow's 15 px head covers the whole box, so the box is reselected from its chip.
      await user.click(within(screen.getByTestId('capture-mark-list')).getByRole('button', { name: 'Box 1' }))
      expect(resizeHandles(), 'box reselected').toHaveLength(8)
      await user.click(screen.getByTestId('capture-view-annotated'))
      expect(resizeHandles(), 'annotated view').toHaveLength(0)
    })

    it('AC-100.9 Ctrl+Z on the image undoes a resize as the Undo button does; Ctrl+Y reapplies it', async () => {
      const surface = await openSelectedSurface()
      await drawWith(surface, 'capture-tool-box')
      await drag(surface, 100, 100, 150, 175)
      expect(geometry('rect'), 'resized').toEqual([1, 1, 5, 6])
      await act(async () => {
        surface.focus()
      })
      await key(surface, { key: 'z', ctrlKey: true })
      expect(geometry('rect'), 'Ctrl+Z').toEqual([1, 1, 3, 3])
      await key(surface, { key: 'y', ctrlKey: true })
      expect(geometry('rect'), 'Ctrl+Y').toEqual([1, 1, 5, 6])
    })
  })

  // ── MEU-101 Capture text re-edit and scale (Session 43 plan AC-101.2–AC-101.4) ──────────────────
  describe('MEU-101 text re-edit and scale', () => {
    // At the 25 px/px fit, `Hello` at font size 2 from image (1,1) has the plate {1,2,5,1}: CSS (25,50)-(150,75).
    const HELLO: Extract<Annotation, { type: 'text' }> = {
      type: 'text',
      x: 1,
      y: 1,
      text: 'Hello',
      color: '#FFFFFF',
      font_size: 2,
      bg_color: null,
    }
    const textMarks = () => document.querySelectorAll('[data-annotation-type="text"]')
    const draftField = () => screen.queryByTestId('capture-text-draft') as HTMLInputElement | null
    const resizeHandles = () => Array.from(document.querySelectorAll('[data-testid^="capture-handle-resize-"]'))
    const undoDisabled = () => (screen.getByTestId('capture-undo') as HTMLButtonElement).disabled
    const textChip = () => within(screen.getByTestId('capture-mark-list')).getByRole('button', { name: 'Text 1' })

    /** Focuses `target`, dispatches one keydown on it and returns whether a handler prevented it. */
    async function pressOn(target: HTMLElement, init: KeyboardEventInit): Promise<boolean> {
      const event = new KeyboardEvent('keydown', { bubbles: true, cancelable: true, ...init })
      await act(async () => {
        target.focus()
        target.dispatchEvent(event)
      })
      return event.defaultPrevented
    }

    /** A browser double-click: two down/up pairs, then `dblclick`. */
    async function doubleClickAt(surface: HTMLElement, x: number, y: number): Promise<void> {
      await act(async () => {
        for (let i = 0; i < 2; i += 1) {
          dispatchPointer(surface, 'pointerdown', x, y)
          dispatchPointer(surface, 'pointerup', x, y)
        }
        surface.dispatchEvent(new MouseEvent('dblclick', { bubbles: true, cancelable: true, clientX: x, clientY: y, detail: 2 }))
      })
    }

    it('AC-101.2 a double-click reopens a committed text mark; Enter commits the new text as one step and keeps every other field', async () => {
      const surface = await openSelectedSurface()
      await user.click(screen.getByTestId('capture-tool-text'))
      const font = screen.getByTestId('capture-font-size')
      await user.clear(font)
      await user.type(font, '2')
      await act(async () => {
        dispatchPointer(surface, 'pointerdown', 25, 25)
        dispatchPointer(surface, 'pointerup', 25, 25)
      })
      await user.type(screen.getByTestId('capture-text-draft'), 'Hello{Enter}')
      expect(textMarks()[0]?.textContent, 'Hello committed').toBe('Hello')
      const fill = textMarks()[0]?.getAttribute('fill')
      const plates = document.querySelectorAll('[data-testid="capture-text-bg-plate"]').length
      await user.click(screen.getByTestId('capture-tool-select'))
      await doubleClickAt(surface, 87, 62)
      expect(draftField()?.value, 'the draft opens with the text').toBe('Hello')
      expect(textMarks(), 'the edited mark is not painted').toHaveLength(0)
      expect(resizeHandles(), 'no handles while editing').toHaveLength(0)
      await user.clear(draftField() as HTMLInputElement)
      await user.type(draftField() as HTMLInputElement, 'Bye{Enter}')
      expect(draftField(), 'Enter closes the draft').toBeNull()
      expect(textMarks(), 'one text mark').toHaveLength(1)
      expect(textMarks()[0]?.textContent).toBe('Bye')
      expect(textMarks()[0]?.getAttribute('fill'), 'colour kept').toBe(fill)
      expect(document.querySelectorAll('[data-testid="capture-text-bg-plate"]'), 'background kept').toHaveLength(plates)
      await user.click(screen.getByTestId('capture-undo'))
      expect(textMarks()[0]?.textContent, 'one Undo restores Hello').toBe('Hello')
      await user.click(screen.getByTestId('capture-redo'))
      const saved = (await saveBody()) as { annotations: unknown[] }
      expect(saved.annotations).toHaveLength(1)
      expect(saved.annotations[0]).toMatchObject({ type: 'text', x: 1, y: 1, text: 'Bye', font_size: 2 })
    })

    it('AC-101.3 Enter on a selected text mark reopens it; unchanged, emptied or escaped edits record nothing; Enter on a box opens nothing', async () => {
      // Loaded marks carry no history, so Undo stays disabled until an edit records a step.
      detailAnnotations['shot-1'] = [HELLO]
      const surface = await openSelectedSurface()
      await user.click(textChip())
      expect(await pressOn(surface, { key: 'Enter' }), 'Enter on a text mark is prevented').toBe(true)
      expect(draftField()?.value, 'the draft opens with the text').toBe('Hello')
      expect(textMarks(), 'the edited mark is not painted').toHaveLength(0)
      expect(screen.queryByTestId('capture-save'), 'an unchanged edit draft is not dirty').toBeNull()
      await user.type(draftField() as HTMLInputElement, '{Enter}')
      expect(draftField(), 'an unchanged commit closes the draft').toBeNull()
      expect(textMarks()[0]?.textContent, 'painted again').toBe('Hello')
      expect(undoDisabled(), 'an unchanged commit records nothing').toBe(true)
      await user.click(textChip())
      await pressOn(surface, { key: 'Enter' })
      await user.type(draftField() as HTMLInputElement, 'X{Escape}')
      expect(draftField(), 'Escape closes the draft').toBeNull()
      expect(textMarks()[0]?.textContent, 'Escape keeps the original').toBe('Hello')
      expect(undoDisabled(), 'Escape records nothing').toBe(true)
      await user.click(textChip())
      await pressOn(surface, { key: 'Enter' })
      await user.clear(draftField() as HTMLInputElement)
      await user.type(draftField() as HTMLInputElement, '{Enter}')
      expect(draftField(), 'an emptied field closes the draft').toBeNull()
      expect(textMarks()[0]?.textContent, 'an emptied field keeps the original').toBe('Hello')
      expect(undoDisabled(), 'an emptied field records nothing').toBe(true)
      expect(screen.queryByTestId('capture-save'), 'the shot stays clean').toBeNull()
      await user.click(screen.getByTestId('capture-tool-box'))
      await drag(surface, 25, 125, 100, 175)
      expect(document.querySelectorAll('[data-annotation-type="rect"]'), 'box drawn').toHaveLength(1)
      expect(await pressOn(surface, { key: 'Enter' }), 'Enter on a box is not prevented').toBe(false)
      expect(draftField(), 'Enter on a box opens nothing').toBeNull()
    })

    it('AC-101.4 a selected text mark has four corner handles; dragging se scales font_size as one step; the plate edge midpoint is no resize hit', async () => {
      detailAnnotations['shot-1'] = [HELLO]
      const surface = await openSelectedSurface()
      await user.click(textChip())
      const handles = resizeHandles().map((element) => element.getAttribute('data-handle'))
      expect(handles.sort(), 'four corners').toEqual(['ne', 'nw', 'se', 'sw'])
      // The se plate corner is image (6,3), CSS (150,75); CSS (175,100) is image (7,4): ratio max(6/5, 2/1) = 2.
      await drag(surface, 150, 75, 175, 100)
      expect(textMarks()[0]?.getAttribute('font-size'), 'scaled').toBe('4')
      await user.click(screen.getByTestId('capture-undo'))
      expect(textMarks()[0]?.getAttribute('font-size'), 'one Undo').toBe('2')
      expect(undoDisabled(), 'one step').toBe(true)
      const { hitTestMarks } = await import('../../src/renderer/src/features/capture/capture-hit-test')
      // The plate's n edge midpoint is image (3.5,2), CSS (87.5,50).
      const hit = hitTestMarks({
        cssX: 87.5,
        cssY: 50,
        scale: 25,
        ox: 0,
        oy: 0,
        imageW: 8,
        imageH: 8,
        annotations: [HELLO],
        selectedIndex: 0,
      })
      expect(hit?.kind, 'n edge midpoint').not.toBe('resize')
    })

    it('AC-101.4 after a corner scale the Size field shows the new font_size, and ArrowUp steps from it [review F1]', async () => {
      detailAnnotations['shot-1'] = [HELLO]
      const surface = await openSelectedSurface()
      await user.click(textChip())
      await drag(surface, 150, 75, 175, 100)
      expect(textMarks()[0]?.getAttribute('font-size'), 'scaled').toBe('4')
      const font = screen.getByTestId('capture-font-size') as HTMLInputElement
      expect(font.value, 'Size after the scale').toBe('4')
      font.focus()
      await user.keyboard('{ArrowUp}')
      expect(textMarks()[0]?.getAttribute('font-size'), 'ArrowUp after the scale').toBe('5')
    })
  })

  // ── MEU-87 tool lock (TOOL_LOCK, LOCK_KEEPS_TOOL, LOCK_PERSISTS) ─────────────────────────────
  describe('MEU-87 tool lock', () => {
    function lockButton(): HTMLButtonElement {
      return screen.getByTestId('capture-tool-lock') as HTMLButtonElement
    }

    function pressed(id: string): string | null {
      return screen.getByTestId(id).getAttribute('aria-pressed')
    }

    /** Indexes of the mark chips shown as selected. */
    function selectedMarks(): number[] {
      return Array.from(screen.getByTestId('capture-mark-list').querySelectorAll('button')).flatMap((button, index) =>
        button.getAttribute('aria-pressed') === 'true' ? [index] : [],
      )
    }

    function markCount(type: string): number {
      return document.querySelectorAll(`[data-annotation-type="${type}"]`).length
    }

    async function placeText(surface: HTMLElement, x: number, y: number, text: string): Promise<void> {
      await act(async () => {
        dispatchPointer(surface, 'pointerdown', x, y)
        dispatchPointer(surface, 'pointerup', x, y)
      })
      await user.type(screen.getByTestId('capture-text-draft'), `${text}{Enter}`)
    }

    it('AC-87.2 the lock sits straight after the Annotation tool group and toggles aria-pressed without touching tool, selection or Save', async () => {
      const surface = await openSelectedSurface()
      expect(screen.queryByTestId('capture-tool-lock')).not.toBeNull()
      const group = screen.getByRole('group', { name: 'Annotation tool' })
      expect(group.nextElementSibling?.contains(lockButton())).toBe(true)
      expect(pressed('capture-tool-lock')).toBe('false')
      expect(pressed('capture-tool-arrow')).toBe('true')
      await user.click(lockButton())
      expect(pressed('capture-tool-lock')).toBe('true')
      expect(pressed('capture-tool-arrow')).toBe('true')
      expect(screen.queryByTestId('capture-save')).toBeNull()
      await user.click(lockButton())
      expect(pressed('capture-tool-lock')).toBe('false')
      expect(screen.queryByTestId('capture-save')).toBeNull()
      await drag(surface, 25, 25, 150, 150)
      expect(pressed('capture-tool-select')).toBe('true')
      expect(selectedMarks()).toEqual([0])
      await user.click(lockButton())
      expect(pressed('capture-tool-lock')).toBe('true')
      expect(pressed('capture-tool-select')).toBe('true')
      expect(selectedMarks()).toEqual([0])
    })

    it('AC-87.2 negative: with no shot the lock stays enabled while the tools are disabled', async () => {
      catalogItems = []
      queryClient.setQueryData(['captures'], { items: [], pendingInteractive: false })
      await renderPage()
      expect(screen.queryByTestId('capture-tool-lock')).not.toBeNull()
      expect((screen.getByTestId('capture-tool-box') as HTMLButtonElement).disabled).toBe(true)
      expect(lockButton().disabled).toBe(false)
      await user.click(lockButton())
      expect(pressed('capture-tool-lock')).toBe('true')
    })

    it('AC-87.3 with the lock on, two Box drags keep Box with nothing selected, and two Undos remove them one at a time', async () => {
      const surface = await openSelectedSurface()
      expect(screen.queryByTestId('capture-tool-lock')).not.toBeNull()
      await user.click(lockButton())
      await user.click(screen.getByTestId('capture-tool-box'))
      await drag(surface, 20, 20, 60, 60)
      expect(markCount('rect')).toBe(1)
      expect(pressed('capture-tool-box')).toBe('true')
      expect(selectedMarks()).toEqual([])
      await drag(surface, 100, 100, 150, 150)
      expect(markCount('rect')).toBe(2)
      expect(pressed('capture-tool-box')).toBe('true')
      expect(selectedMarks()).toEqual([])
      await user.click(undoButton())
      expect(markCount('rect')).toBe(1)
      await user.click(undoButton())
      expect(markCount('rect')).toBe(0)
    })

    it('AC-87.3 negative: with the lock off, a Box drag returns to Select with the new box selected (AC-60.4)', async () => {
      const surface = await openSelectedSurface()
      expect(screen.queryByTestId('capture-tool-lock')).not.toBeNull()
      expect(pressed('capture-tool-lock')).toBe('false')
      await user.click(screen.getByTestId('capture-tool-box'))
      await drag(surface, 20, 20, 60, 60)
      expect(markCount('rect')).toBe(1)
      expect(pressed('capture-tool-select')).toBe('true')
      expect(selectedMarks()).toEqual([0])
    })

    it('AC-87.4 with the lock on, a text commit keeps Text with nothing selected and the next click opens a new draft', async () => {
      const surface = await openSelectedSurface()
      expect(screen.queryByTestId('capture-tool-lock')).not.toBeNull()
      await user.click(lockButton())
      await user.click(screen.getByTestId('capture-tool-text'))
      await placeText(surface, 50, 50, 'One')
      expect(markCount('text')).toBe(1)
      expect(screen.queryByTestId('capture-text-draft')).toBeNull()
      expect(pressed('capture-tool-text')).toBe('true')
      expect(selectedMarks()).toEqual([])
      await act(async () => {
        dispatchPointer(surface, 'pointerdown', 120, 140)
        dispatchPointer(surface, 'pointerup', 120, 140)
      })
      expect(screen.getByTestId('capture-text-draft')).toBeTruthy()
    })

    it('AC-87.4 negative: with the lock off, a text commit selects the new text and returns to Select', async () => {
      const surface = await openSelectedSurface()
      expect(screen.queryByTestId('capture-tool-lock')).not.toBeNull()
      await user.click(screen.getByTestId('capture-tool-text'))
      await placeText(surface, 50, 50, 'One')
      expect(markCount('text')).toBe(1)
      expect(pressed('capture-tool-select')).toBe('true')
      expect(selectedMarks()).toEqual([0])
    })

    it('AC-87.5 the lock survives a tool change; turning it off restores auto-Select from the next mark', async () => {
      const surface = await openSelectedSurface()
      expect(screen.queryByTestId('capture-tool-lock')).not.toBeNull()
      await user.click(lockButton())
      await user.click(screen.getByTestId('capture-tool-box'))
      await drag(surface, 20, 20, 60, 60)
      await user.click(screen.getByTestId('capture-tool-arrow'))
      await drag(surface, 100, 100, 150, 150)
      expect(markCount('rect')).toBe(1)
      expect(markCount('arrow')).toBe(1)
      expect(pressed('capture-tool-arrow')).toBe('true')
      expect(pressed('capture-tool-lock')).toBe('true')
      expect(selectedMarks()).toEqual([])
      await user.click(lockButton())
      expect(pressed('capture-tool-lock')).toBe('false')
      await drag(surface, 30, 150, 150, 30)
      expect(markCount('arrow')).toBe(2)
      expect(pressed('capture-tool-select')).toBe('true')
      expect(selectedMarks()).toEqual([2])
    })

    it('AC-87.5 negative: choosing Arrow while locked does not turn the lock off', async () => {
      await openSelectedSurface()
      expect(screen.queryByTestId('capture-tool-lock')).not.toBeNull()
      await user.click(lockButton())
      await user.click(screen.getByTestId('capture-tool-box'))
      await user.click(screen.getByTestId('capture-tool-arrow'))
      expect(pressed('capture-tool-arrow')).toBe('true')
      expect(pressed('capture-tool-lock')).toBe('true')
    })
  })
})

const viewportNoop = (): void => undefined

describe('MEU-59 viewport preview', () => {
  it('AC-59.19 SVG text uses start/alphabetic and paints a bg plate', () => {
    render(
      createElement(CaptureViewport, {
        empty: false,
        imageUrl: 'blob:x',
        tool: 'text',
        color: 'red',
        stroke: '3',
        annotations: [
          {
            type: 'text',
            x: 10,
            y: 20,
            text: 'Hi',
            color: 'red',
            font_size: 16,
            bg_color: 'black',
          },
        ],
        canUndo: false,
        canRedo: false,
        textDraft: null,
        onTool: viewportNoop,
        onColor: viewportNoop,
        onStroke: viewportNoop,
        onUndo: viewportNoop,
        onRedo: viewportNoop,
        onPointer: viewportNoop,
        onTextDraftChange: viewportNoop,
        onTextCommit: viewportNoop,
        onTextCancel: viewportNoop,
      }),
    )
    const text = screen.getByTestId('capture-annotation')
    expect(text.getAttribute('text-anchor')).toBe('start')
    expect(text.getAttribute('dominant-baseline')).toBe('alphabetic')
    expect(text.getAttribute('y')).toBe('38')
    expect(screen.getByTestId('capture-text-bg-plate')).toBeTruthy()
    const plate = screen.getByTestId('capture-text-bg-plate')
    expect(plate.getAttribute('x')).toBe('10')
    expect(plate.getAttribute('y')).toBe('26')
    expect(plate.getAttribute('width')).toBe('15')
    expect(plate.getAttribute('height')).toBe('12')
  })
})

describe('MEU-60 viewport handle scale', () => {
  async function withSurfaceSize(size: number, work: () => Promise<void>): Promise<void> {
    const proto = HTMLElement.prototype.getBoundingClientRect
    HTMLElement.prototype.getBoundingClientRect = function (this: HTMLElement): DOMRect {
      if (this.getAttribute('data-testid') === 'capture-draw-surface') {
        return {
          x: 0,
          y: 0,
          left: 0,
          top: 0,
          right: size,
          bottom: size,
          width: size,
          height: size,
          toJSON: () => ({}),
        } as DOMRect
      }
      return proto.call(this)
    }
    try {
      await work()
    } finally {
      HTMLElement.prototype.getBoundingClientRect = proto
    }
  }

  async function renderHandles(): Promise<void> {
    render(
      createElement(CaptureViewport, {
        empty: false,
        imageUrl: 'blob:x',
        imageWidth: 8,
        imageHeight: 8,
        tool: 'select',
        color: '#FF0000',
        stroke: '3',
        selectedIndex: 0,
        annotations: [
          {
            type: 'arrow',
            color: '#FF0000',
            stroke_width: 3,
            from: [1, 1],
            to: [6, 6],
          },
        ],
        canUndo: false,
        canRedo: false,
        textDraft: null,
        onTool: viewportNoop,
        onColor: viewportNoop,
        onStroke: viewportNoop,
        onUndo: viewportNoop,
        onRedo: viewportNoop,
        onPointer: viewportNoop,
        onTextDraftChange: viewportNoop,
        onTextCommit: viewportNoop,
        onTextCancel: viewportNoop,
      }),
    )
    await act(async () => {
      await Promise.resolve()
    })
  }

  it('AC-60.13 rendered handle radius stays HANDLE_RADIUS_CSS at two fit scales', async () => {
    await withSurfaceSize(200, async () => {
      await renderHandles()
      const { s } = fitScaleOrigin({ containerW: 200, containerH: 200, imageW: 8, imageH: 8 })
      expect(Number(screen.getByTestId('capture-handle-from').getAttribute('r')) * s).toBeCloseTo(
        HANDLE_RADIUS_CSS,
      )
    })
    cleanup()
    await withSurfaceSize(400, async () => {
      await renderHandles()
      const { s } = fitScaleOrigin({ containerW: 400, containerH: 400, imageW: 8, imageH: 8 })
      expect(Number(screen.getByTestId('capture-handle-from').getAttribute('r')) * s).toBeCloseTo(
        HANDLE_RADIUS_CSS,
      )
    })
  })
})

/**
 * ZOOM_SEAM_SHOT surface stub (Session 29 plan): a width/height variant of `withSurfaceSize`. It reads
 * `size` on every call, so a test can change the stubbed rect and then fire a fake ResizeObserver.
 */
async function withSurfaceRect(size: { width: number; height: number }, work: () => Promise<void>): Promise<void> {
  const proto = HTMLElement.prototype.getBoundingClientRect
  HTMLElement.prototype.getBoundingClientRect = function (this: HTMLElement): DOMRect {
    if (this.getAttribute('data-testid') === 'capture-draw-surface') {
      return {
        x: 0,
        y: 0,
        left: 0,
        top: 0,
        right: size.width,
        bottom: size.height,
        width: size.width,
        height: size.height,
        toJSON: () => ({}),
      } as DOMRect
    }
    return proto.call(this)
  }
  try {
    await work()
  } finally {
    HTMLElement.prototype.getBoundingClientRect = proto
  }
}

describe('MEU-66 viewport SURFACE_POINTER at zoom (Session 29 plan AC-66.11)', () => {
  function pointer(target: HTMLElement, type: string, x: number, y: number, button: number): void {
    target.dispatchEvent(
      new PointerEvent(type, {
        bubbles: true,
        cancelable: true,
        clientX: x,
        clientY: y,
        button,
        buttons: button === 1 ? 4 : 1,
        pointerId: 3,
        pointerType: 'mouse',
        isPrimary: true,
      }),
    )
  }

  it('AC-66.11 a pointer-down at container (400, 300) on ZOOM_EXAMPLE reports image (700, 375), s 2 and the panned origin', async () => {
    await withSurfaceRect({ width: 800, height: 600 }, async () => {
      const onSurfacePointer = vi.fn()
      render(
        createElement(CaptureViewport, {
          empty: false,
          imageUrl: 'blob:x',
          imageWidth: 1600,
          imageHeight: 900,
          shotId: 'shot-zoom',
          tool: 'arrow',
          color: '#FF0000',
          stroke: '3',
          annotations: [],
          canUndo: false,
          canRedo: false,
          textDraft: null,
          onTool: viewportNoop,
          onColor: viewportNoop,
          onStroke: viewportNoop,
          onUndo: viewportNoop,
          onRedo: viewportNoop,
          onPointer: viewportNoop,
          onSurfacePointer,
          onTextDraftChange: viewportNoop,
          onTextCommit: viewportNoop,
          onTextCancel: viewportNoop,
        }),
      )
      await act(async () => {
        await Promise.resolve()
      })
      const user = userEvent.setup()
      for (let i = 0; i < 10; i += 1) {
        await user.click(screen.getByTestId('capture-zoom-in'))
      }
      const surface = screen.getByTestId('capture-draw-surface')
      await act(async () => {
        pointer(surface, 'pointerdown', 300, 200, 1)
        pointer(surface, 'pointermove', 500, 350, 1)
        pointer(surface, 'pointerup', 500, 350, 1)
      })
      expect(onSurfacePointer).not.toHaveBeenCalled()
      await act(async () => {
        pointer(surface, 'pointerdown', 400, 300, 0)
      })
      const down = onSurfacePointer.mock.calls.map((call) => call[0]).find((event) => event.phase === 'down')
      expect(down).toMatchObject({ cssX: 400, cssY: 300, scale: 2, ox: -1000, oy: -450, image: { x: 700, y: 375 } })
    })
  })
})

const MEU66_UI = resolve(dirname(fileURLToPath(import.meta.url)), '../..')

describe('MEU-66 test ids (AC-66.17)', () => {
  it('AC-66.17 MEU-66 test ids are registered after the MEU-51 marker', () => {
    const registry = readFileSync(resolve(MEU66_UI, 'tests/e2e/test-ids.ts'), 'utf8')
    const [prefix, tail] = registry.split('// MEU-51 primitive harness IDs.')
    const block = (tail ?? '').split('// MEU-66 Capture viewport zoom (additive IDs).')[1] ?? ''
    expect(block.length).toBeGreaterThan(0)
    const viewport = readFileSync(resolve(MEU66_UI, 'src/renderer/src/features/capture/CaptureViewport.tsx'), 'utf8')
    const table = readFileSync(resolve(MEU66_UI, 'src/renderer/src/features/capture/capture-toolbar.ts'), 'utf8')
    for (const id of ['capture-zoom-in', 'capture-zoom-out', 'capture-zoom-fit', 'capture-zoom-level', 'capture-zoom-content']) {
      expect(block, id).toContain(`= '${id}'`)
      expect(prefix, id).not.toContain(`'${id}'`)
      expect(viewport + table, id).toContain(id)
    }
  })
})

// ── MEU-67 Apply to image / Revert (Session 30 plan AC-67.20–23, AC-67.33) ───────────────────
describe('MEU-67 capture flatten and revert GUI', () => {
  type Shot = typeof SHOT
  type Detail = { annotations: unknown[]; backup_path: string | null }
  const MARK = { type: 'rect', x: 1, y: 1, width: 4, height: 4, color: '#ff0000', stroke_width: 2 }
  const PNG_SHOT: Shot = { ...SHOT, id: 'png-1', original_path: 'C:/shots/a.png', display_name: 'a.png' }
  const JPG_SHOT: Shot = {
    ...SHOT,
    id: 'jpg-1',
    original_path: 'C:/shots/photo.jpg',
    display_name: 'photo.jpg',
    created_at: '2026-08-27T10:00:00Z',
    updated_at: '2026-08-27T10:00:00Z',
  }
  const BMP_SHOT: Shot = {
    ...SHOT,
    id: 'bmp-1',
    original_path: 'C:/shots/old.bmp',
    display_name: 'old.bmp',
    created_at: '2026-08-27T09:00:00Z',
    updated_at: '2026-08-27T09:00:00Z',
  }
  const BACKUP = 'C:/shots/.avkit-backup/a.20261003-120000.png'
  let user: ReturnType<typeof userEvent.setup>
  let queryClient: QueryClient
  let items: Shot[] = []
  let details: Record<string, Detail> = {}
  let settings: Record<string, unknown> = {}
  let flattenError: { status: number; message: string } | null = null
  const calls: FetchCall[] = []

  function count(method: string, fragment: string): number {
    return calls.filter((c) => c.method === method && c.url.includes(fragment)).length
  }

  function bump(id: string): Shot {
    const index = items.findIndex((row) => row.id === id)
    const next = { ...(items[index] as Shot), updated_at: '2026-10-03T12:00:00Z', annotated_path: null }
    items[index] = next
    return next
  }

  beforeEach(() => {
    user = userEvent.setup()
    calls.length = 0
    items = [PNG_SHOT, JPG_SHOT, BMP_SHOT]
    details = {
      'png-1': { annotations: [MARK], backup_path: null },
      'jpg-1': { annotations: [MARK], backup_path: null },
      'bmp-1': { annotations: [MARK], backup_path: null },
    }
    settings = {
      inbox_dir: 'C:/shots',
      hotkey: 'F2',
      copy_to_clipboard: false,
      close_to_tray: true,
      flatten_backup: true,
      backup_dir: '',
      annotated_format: 'png',
    }
    flattenError = null
    // The page's commands refresh the app's QUERY_KEY client (capture-commands.ts), so this
    // suite renders with that same client, as the app does.
    queryClient = appQueryClient
    queryClient.setQueryData(['captures'], { items: [...items], pendingInteractive: false })
    queryClient.setQueryData(['settings', 'capture'], settings)
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
        return jsonResponse(settings)
      }
      if (path.includes('/captures/requests')) {
        return jsonResponse({ items: [] })
      }
      if (path.endsWith('/image')) {
        return new Response(new Uint8Array([1, 2, 3]), { status: 200, headers: { 'Content-Type': 'image/png' } })
      }
      const action = path.match(/\/captures\/([^/]+)\/(flatten|revert)$/)
      if (action && method === 'POST') {
        const [, id, verb] = action as unknown as [string, string, string]
        if (verb === 'flatten' && flattenError !== null) {
          return jsonResponse(
            { error: { code: 'capture_flatten_conflict', message: flattenError.message, details: null } },
            flattenError.status,
          )
        }
        if (verb === 'flatten' && id === 'jpg-1') {
          const converted: Shot = {
            ...JPG_SHOT,
            id: 'conv-1',
            original_path: 'C:/shots/photo-converted.png',
            display_name: 'photo-converted.png',
            created_at: '2026-10-03T12:00:00Z',
            updated_at: '2026-10-03T12:00:00Z',
          }
          items = [converted, ...items]
          details['conv-1'] = { annotations: [], backup_path: null }
          return jsonResponse({ ...converted, ...details['conv-1'] })
        }
        if (verb === 'flatten') {
          details[id] = { annotations: [], backup_path: BACKUP }
        }
        return jsonResponse({ ...bump(id), ...details[id] })
      }
      const detail = path.match(/\/captures\/([^/]+)$/)
      if (detail && method === 'GET') {
        const id = detail[1] as string
        const row = items.find((item) => item.id === id)
        return jsonResponse({ ...row, ...(details[id] ?? { annotations: [], backup_path: null }) })
      }
      if (path.includes('/annotate')) {
        return jsonResponse({ ok: true })
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
    queryClient.clear()
    vi.unstubAllGlobals()
  })

  async function open(index = 0): Promise<HTMLElement> {
    render(createElement(QueryClientProvider, { client: queryClient }, createElement(CapturePage)))
    await vi.waitFor(() => {
      expect(screen.getAllByTestId('capture-filmstrip-item').length).toBeGreaterThan(index)
    })
    await user.click(screen.getAllByTestId('capture-filmstrip-item')[index] as HTMLElement)
    await vi.waitFor(() => {
      expect(screen.getByTestId('capture-draw-surface').getAttribute('data-overlay-ready')).toBe('true')
    })
    const surface = screen.getByTestId('capture-draw-surface')
    bindSurface(surface)
    return surface
  }

  function apply(): HTMLButtonElement {
    const button = screen.queryByTestId('capture-apply-image') as HTMLButtonElement | null
    expect(button, 'capture-apply-image rendered').not.toBeNull()
    return button as HTMLButtonElement
  }

  async function select(name: string): Promise<void> {
    const thumb = screen
      .getAllByTestId('capture-filmstrip-item')
      .find((node) => node.textContent?.includes(name)) as HTMLElement
    await user.click(thumb)
    await vi.waitFor(() => {
      expect(screen.getByTestId('capture-shot-info').textContent).toContain(name)
      expect(screen.getByTestId('capture-draw-surface').getAttribute('data-overlay-ready')).toBe('true')
    })
  }

  it('AC-67.20 Apply sits beside the per-shot actions and follows APPLY_ENABLED [TA-12] [TA-13]', async () => {
    const surface = await open(0)
    expect(apply().disabled).toBe(false)
    expect(apply().getAttribute('title')).toBeNull()
    // A-6: Apply sits in a tooltip wrapper; the wrapper is in the same per-shot action row as Delete's tip.
    expect(screen.queryByTestId('capture-delete-tip')?.parentElement).toBe(
      screen.getByTestId('capture-apply-image-tip').parentElement,
    )
    // A shot with saved marks opens in Select; draw with the Arrow tool (setup).
    await user.click(screen.getByTestId('capture-tool-arrow'))
    await act(async () => {
      surface.dispatchEvent(new MouseEvent('mousedown', { clientX: 10, clientY: 10, bubbles: true }))
      surface.dispatchEvent(new MouseEvent('mouseup', { clientX: 40, clientY: 50, bubbles: true }))
    })
    expect(apply().disabled).toBe(true)
    expect(apply().getAttribute('title')).toBeNull()
    expect(focusedHint(screen.getByTestId('capture-apply-image-tip'), 'capture-apply-image-hint')).toBe('Apply to image — Save the overlay first')
    await user.click(screen.getByTestId('capture-undo'))
    expect(apply().disabled).toBe(false)
    await select('photo.jpg')
    expect(apply().disabled).toBe(false)
    await select('old.bmp')
    expect(apply().disabled).toBe(true)
    expect(apply().getAttribute('title')).toBeNull()
    expect(focusedHint(screen.getByTestId('capture-apply-image-tip'), 'capture-apply-image-hint')).toBe(
      'Apply to image — This file type cannot be flattened',
    )
  })

  it('AC-67.20 negative: a shot with no saved marks keeps Apply disabled with "Save marks first" [TA-12]', async () => {
    details['png-1'] = { annotations: [], backup_path: null }
    await open(0)
    expect(apply().disabled).toBe(true)
    expect(apply().getAttribute('title')).toBeNull()
    expect(focusedHint(screen.getByTestId('capture-apply-image-tip'), 'capture-apply-image-hint')).toBe('Apply to image — Save marks first')
  })

  it('AC-67.21 the strip shows FLATTEN_CONFIRM_TEXT; Cancel sends nothing; Confirm POSTs {} once; the strip locks the page', async () => {
    details['png-1'] = { annotations: [MARK], backup_path: BACKUP }
    await open(0)
    await user.click(apply())
    expect(screen.getByTestId('capture-confirm-strip').textContent).toContain(
      'Bake the saved marks into a.png? The original is copied to the backup folder in the inbox first.',
    )
    for (const thumb of screen.getAllByTestId('capture-filmstrip-item')) {
      expect((thumb as HTMLButtonElement).disabled).toBe(true)
    }
    expect((screen.getByTestId('capture-delete') as HTMLButtonElement).disabled).toBe(true)
    expect(apply().disabled).toBe(true)
    expect((screen.getByTestId('capture-revert-image') as HTMLButtonElement).disabled).toBe(true)
    await user.click(screen.getByTestId('capture-flatten-confirm-cancel'))
    expect(screen.queryByTestId('capture-confirm-strip')).toBeNull()
    expect(count('POST', '/flatten')).toBe(0)
    await user.click(apply())
    await user.click(screen.getByTestId('capture-flatten-confirm'))
    await vi.waitFor(() => {
      expect(count('POST', '/captures/png-1/flatten')).toBe(1)
    })
    expect(calls.find((c) => c.url.includes('/flatten'))?.body).toEqual({})
  })

  it('AC-67.21 backups off and a custom backup folder change the strip text', async () => {
    settings = { ...settings, flatten_backup: false }
    queryClient.setQueryData(['settings', 'capture'], settings)
    await open(0)
    await user.click(apply())
    expect(screen.getByTestId('capture-confirm-strip').textContent).toContain(
      'Bake the saved marks into a.png? Backups are off, so this cannot be undone.',
    )
    await user.click(screen.getByTestId('capture-flatten-confirm-cancel'))
    cleanup()
    settings = { ...settings, flatten_backup: true, backup_dir: 'D:/backups' }
    queryClient.setQueryData(['settings', 'capture'], settings)
    await open(0)
    await user.click(apply())
    expect(screen.getByTestId('capture-confirm-strip').textContent).toContain(
      'Bake the saved marks into a.png? The original is copied to D:/backups first.',
    )
  })

  it('AC-67.22 success shows FLATTEN_STATUS, clears the marks, returns to Original and refetches the image', async () => {
    await open(0)
    await vi.waitFor(() => {
      expect(screen.getByTestId('capture-mark-list').children.length).toBe(1)
    })
    const imagesBefore = count('GET', '/captures/png-1/image')
    await user.click(apply())
    await user.click(screen.getByTestId('capture-flatten-confirm'))
    await vi.waitFor(() => {
      expect(screen.getByTestId('capture-status').textContent).toBe(`Applied to image. Backup: ${BACKUP}`)
    })
    await vi.waitFor(() => {
      expect(screen.getByTestId('capture-mark-list').children.length).toBe(0)
      expect(count('GET', '/captures/png-1/image')).toBeGreaterThan(imagesBefore)
    })
    expect((screen.getByTestId('capture-view-annotated') as HTMLButtonElement).disabled).toBe(true)
    expect(screen.getByTestId('capture-view-original').getAttribute('aria-pressed')).toBe('true')
  })

  it('AC-67.22 negative: a 409 shows the API message and leaves marks, saved state and the image alone', async () => {
    flattenError = { status: 409, message: 'Backup folder is the inbox' }
    await open(0)
    await vi.waitFor(() => {
      expect(screen.getByTestId('capture-mark-list').children.length).toBe(1)
    })
    const imagesBefore = count('GET', '/image')
    await user.click(apply())
    await user.click(screen.getByTestId('capture-flatten-confirm'))
    await vi.waitFor(() => {
      expect(screen.getByTestId('capture-status').textContent).toBe('Backup folder is the inbox')
    })
    expect(screen.getByTestId('capture-mark-list').children.length).toBe(1)
    expect(screen.queryByTestId('capture-save')).toBeNull()
    expect(count('GET', '/image')).toBe(imagesBefore)
  })

  it('AC-67.23 Revert is rendered only with a backup; its strip, POST, status and refetch', async () => {
    await open(0)
    expect(screen.queryByTestId('capture-revert-image')).toBeNull()
    cleanup()
    details['png-1'] = { annotations: [], backup_path: BACKUP }
    await open(0)
    await vi.waitFor(() => {
      expect(screen.queryByTestId('capture-revert-image')).not.toBeNull()
    })
    const revert = screen.getByTestId('capture-revert-image') as HTMLButtonElement
    expect(revert.disabled).toBe(false)
    await user.click(revert)
    expect(screen.getByTestId('capture-confirm-strip').textContent).toContain(
      'Replace a.png with its newest backup (a.20261003-120000.png)? The current image is overwritten.',
    )
    await user.click(screen.getByTestId('capture-revert-confirm-cancel'))
    expect(count('POST', '/revert')).toBe(0)
    const imagesBefore = count('GET', '/captures/png-1/image')
    await user.click(screen.getByTestId('capture-revert-image'))
    await user.click(screen.getByTestId('capture-revert-confirm'))
    await vi.waitFor(() => {
      expect(screen.getByTestId('capture-status').textContent).toBe('Reverted from a.20261003-120000.png.')
    })
    expect(count('POST', '/captures/png-1/revert')).toBe(1)
    expect(calls.find((c) => c.url.includes('/revert'))?.body).toEqual({})
    await vi.waitFor(() => {
      expect(count('GET', '/captures/png-1/image')).toBeGreaterThan(imagesBefore)
    })
  })

  it('AC-67.23 negative: Revert is disabled while the overlay is dirty [TA-12]', async () => {
    details['png-1'] = { annotations: [], backup_path: BACKUP }
    const surface = await open(0)
    await vi.waitFor(() => {
      expect(screen.queryByTestId('capture-revert-image')).not.toBeNull()
    })
    await act(async () => {
      surface.dispatchEvent(new MouseEvent('mousedown', { clientX: 10, clientY: 10, bubbles: true }))
      surface.dispatchEvent(new MouseEvent('mouseup', { clientX: 40, clientY: 50, bubbles: true }))
    })
    const revert = screen.getByTestId('capture-revert-image') as HTMLButtonElement
    expect(revert.disabled).toBe(true)
    expect(revert.getAttribute('title')).toBeNull()
    expect(focusedHint(screen.getByTestId('capture-revert-image-tip'), 'capture-revert-image-hint')).toBe(
      'Revert image — Save or discard overlay marks first',
    )
  })

  it('AC-67.33 a JPEG shot bakes into a new PNG copy that becomes the selection; the JPEG stays', async () => {
    await open(1)
    expect(screen.getByTestId('capture-shot-info').textContent).toContain('photo.jpg')
    await user.click(apply())
    expect(screen.getByTestId('capture-confirm-strip').textContent).toContain(
      'Bake the saved marks into a new PNG copy of photo.jpg? photo.jpg itself stays unchanged.',
    )
    await user.click(screen.getByTestId('capture-flatten-confirm'))
    await vi.waitFor(() => {
      expect(screen.getByTestId('capture-status').textContent).toBe('Applied to a new PNG copy: photo-converted.png.')
    })
    expect(count('POST', '/captures/jpg-1/flatten')).toBe(1)
    await vi.waitFor(() => {
      const current = screen
        .getAllByTestId('capture-filmstrip-item')
        .find((node) => node.getAttribute('aria-current') === 'true')
      expect(current?.textContent).toContain('photo-converted.png')
    })
    expect(
      screen.getAllByTestId('capture-filmstrip-item').some((node) => node.textContent?.includes('photo.jpg')),
    ).toBe(true)
    await select('photo.jpg')
    await vi.waitFor(() => {
      expect(screen.getByTestId('capture-mark-list').children.length).toBe(1)
    })
  })

  it('AC-67.20 AC-67.23 A-6 a disabled Apply or Revert shows its reason on a hoverable wrapper [TA-14]', async () => {
    details['png-1'] = { annotations: [MARK], backup_path: BACKUP }
    const surface = await open(0)
    await vi.waitFor(() => {
      expect(screen.queryByTestId('capture-revert-image')).not.toBeNull()
    })
    const applyTip = screen.getByTestId('capture-apply-image-tip')
    const revertTip = screen.getByTestId('capture-revert-image-tip')
    expect(applyTip.contains(apply())).toBe(true)
    expect(revertTip.contains(screen.getByTestId('capture-revert-image'))).toBe(true)
    // Enabled: no reason on either element.
    expect(applyTip.getAttribute('title')).toBeNull()
    expect(revertTip.getAttribute('title')).toBeNull()
    await user.click(screen.getByTestId('capture-tool-arrow'))
    await act(async () => {
      surface.dispatchEvent(new MouseEvent('mousedown', { clientX: 10, clientY: 10, bubbles: true }))
      surface.dispatchEvent(new MouseEvent('mouseup', { clientX: 40, clientY: 50, bubbles: true }))
    })
    expect(apply().disabled).toBe(true)
    // The disabled button ignores the pointer (Button primitive), so the wrapper is the hover and focus
    // target and shows the reason through the hint, never a native title.
    expect(applyTip.getAttribute('title')).toBeNull()
    expect(revertTip.getAttribute('title')).toBeNull()
    expect(focusedHint(applyTip, 'capture-apply-image-hint')).toBe('Apply to image — Save the overlay first')
    expect(focusedHint(revertTip, 'capture-revert-image-hint')).toBe(
      'Revert image — Save or discard overlay marks first',
    )
    expect(applyTip.className).not.toMatch(/pointer-events-none/)
    expect(revertTip.className).not.toMatch(/pointer-events-none/)
  })

  it('AC-67.35 A-10 hovering a disabled Apply or Revert shows a rendered reason label [TA-15]', async () => {
    // HINT_TIMING on real timers: a hover shows the hint after HINT_DELAY_MS (400 ms) and a leave hides it
    // after HINT_GRACE_MS (120 ms), so each read waits with headroom rather than importing the constants.
    const settle = { timeout: 2000 }
    const hintText = (id: string): string | null => screen.queryByTestId(id)?.textContent ?? null
    details['png-1'] = { annotations: [MARK], backup_path: BACKUP }
    const surface = await open(0)
    await vi.waitFor(() => {
      expect(screen.queryByTestId('capture-revert-image')).not.toBeNull()
    })
    // Enabled: the hint shows the plain name, then goes once the pointer leaves.
    await user.hover(screen.getByTestId('capture-apply-image-tip'))
    await vi.waitFor(() => {
      expect(hintText('capture-apply-image-hint')).toBe('Apply to image')
    }, settle)
    await user.unhover(screen.getByTestId('capture-apply-image-tip'))
    await vi.waitFor(() => {
      expect(screen.queryByTestId('capture-apply-image-hint')).toBeNull()
    }, settle)
    await user.click(screen.getByTestId('capture-tool-arrow'))
    await act(async () => {
      surface.dispatchEvent(new MouseEvent('mousedown', { clientX: 10, clientY: 10, bubbles: true }))
      surface.dispatchEvent(new MouseEvent('mouseup', { clientX: 40, clientY: 50, bubbles: true }))
    })
    await user.hover(screen.getByTestId('capture-apply-image-tip'))
    await vi.waitFor(() => {
      expect(hintText('capture-apply-image-hint')).toBe('Apply to image — Save the overlay first')
    }, settle)
    expect(screen.getByTestId('capture-apply-image-hint').getAttribute('role')).toBe('tooltip')
    await user.unhover(screen.getByTestId('capture-apply-image-tip'))
    await vi.waitFor(() => {
      expect(screen.queryByTestId('capture-apply-image-hint')).toBeNull()
    }, settle)
    await user.hover(screen.getByTestId('capture-revert-image-tip'))
    await vi.waitFor(() => {
      expect(hintText('capture-revert-image-hint')).toBe('Revert image — Save or discard overlay marks first')
    }, settle)
  })

  it('AC-80.3 Escape hides a toolbar hint while the drawing surface keeps focus (execution R1 F1)', async () => {
    // The surface stops keydown propagation for its editor keys; the hint must still close on Escape, and the
    // editor must still receive and handle that Escape (it prevents the default).
    const settle = { timeout: 2000 }
    const surface = await open(0)
    act(() => {
      surface.focus()
    })
    expect(document.activeElement).toBe(surface)
    await user.hover(screen.getByTestId('capture-tool-arrow-tip'))
    await vi.waitFor(() => {
      expect(screen.queryByTestId('capture-tool-arrow-hint')).not.toBeNull()
    }, settle)
    const notPrevented = fireEvent.keyDown(surface, { key: 'Escape' })
    expect(screen.queryByTestId('capture-tool-arrow-hint'), 'Escape hides the hint').toBeNull()
    expect(notPrevented, 'the editor still handles its Escape').toBe(false)
    expect(document.activeElement, 'focus stays on the surface').toBe(surface)
  })

  it('AC-67.23 review F5 Revert uses the same secondary trigger variant as Apply (D-18)', async () => {
    details['png-1'] = { annotations: [MARK], backup_path: BACKUP }
    await open(0)
    await vi.waitFor(() => {
      expect(screen.queryByTestId('capture-revert-image')).not.toBeNull()
    })
    expect(screen.getByTestId('capture-revert-image').className).toBe(apply().className)
  })
})

