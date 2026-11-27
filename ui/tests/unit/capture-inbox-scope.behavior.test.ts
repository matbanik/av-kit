/** @vitest-environment jsdom */

// MEU-166 (Session 103): the Capture page follows a saved inbox change (INBOX_SAVE_REFRESH,
// INBOX_SELECTION_LEFT, INBOX_RESULT_BOUND). The harness follows capture-page.behavior.test.ts and
// capture-crop-tool.behavior.test.ts: a rendered CapturePage on the app's query client (cropCapture
// refreshes that client), a mocked window.api and a recorded fetch whose catalog answers the saved
// inbox's folder. Lists, details and crops can be held, so each answer's order is the test's.

import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import { QueryClientProvider } from '@tanstack/react-query'
import userEvent from '@testing-library/user-event'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { CapturePage } from '../../src/renderer/src/features/capture/CapturePage'
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

type Call = { url: string; path: string; method: string; body?: unknown; at: number }

const INBOX_A = 'C:/inbox-a'
const INBOX_B = 'C:/inbox-b'
const INBOX_C = 'C:/inbox-c'

function shot(id: string, name: string, folder: string, hour: number): Shot {
  const stamp = `2026-11-26T${String(hour).padStart(2, '0')}:00:00Z`
  return {
    id,
    original_path: `${folder}/${name}`,
    annotated_path: null,
    sidecar_path: null,
    display_name: name,
    width: 400,
    height: 200,
    file_size: 32,
    source: 'gui',
    created_at: stamp,
    updated_at: stamp,
  }
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
    showDirectoryDialog: async () => undefined,
    showFileDialog: async () => undefined,
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
  } as Window['api']
}

function bindSurface(surface: HTMLElement): void {
  surface.getBoundingClientRect = () =>
    ({ x: 0, y: 0, left: 0, top: 0, right: 400, bottom: 200, width: 400, height: 200, toJSON: () => ({}) }) as DOMRect
}

function present<T extends HTMLElement = HTMLElement>(id: string): T {
  const node = screen.queryByTestId(id)
  expect(node, `${id} rendered`).not.toBeNull()
  return node as T
}

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

/** The sub-second waits let held answers land and effects run; the 5 s catalog poll never fits in one. */
async function settle(ms = 40): Promise<void> {
  await act(async () => {
    await new Promise((resolve) => setTimeout(resolve, ms))
  })
}

describe('MEU-166 the Capture page follows a saved inbox change', () => {
  let user: ReturnType<typeof userEvent.setup>
  let saved: Record<string, unknown>
  let folders: Record<string, Shot[]>
  /** Ids on disk that no list answer carries yet (a crop copy the catalog has not caught up with). */
  let unlisted: Set<string>
  let listLag = false
  let listHold = false
  let listWaiters: Array<() => void> = []
  let cropHold = false
  let cropWaiters: Array<() => void> = []
  let detailHold: Set<string>
  let detailWaiters: Record<string, Array<() => void>> = {}
  let errors: string[] = []
  const calls: Call[] = []
  const onError = (event: Event): void => {
    errors.push(String((event as CustomEvent<string>).detail))
  }

  function reset(): void {
    calls.length = 0
    saved = {
      inbox_dir: INBOX_A,
      hotkey: 'F2',
      copy_to_clipboard: false,
      close_to_tray: true,
      flatten_backup: true,
      backup_dir: '',
      annotated_format: 'png',
      tool_lock: false,
    }
    folders = {
      [INBOX_A]: [shot('a1', 'a-1.png', INBOX_A, 12), shot('a2', 'a-2.png', INBOX_A, 11)],
      [INBOX_B]: [shot('b1', 'b-1.png', INBOX_B, 10)],
      [INBOX_C]: [],
    }
    unlisted = new Set()
    listLag = false
    listHold = false
    listWaiters = []
    cropHold = false
    cropWaiters = []
    detailHold = new Set()
    detailWaiters = {}
    errors = []
  }

  function inbox(): Shot[] {
    return folders[String(saved.inbox_dir)] ?? []
  }

  beforeEach(() => {
    user = userEvent.setup()
    reset()
    mockApi()
    URL.createObjectURL = vi.fn(() => 'blob:capture-shot')
    URL.revokeObjectURL = vi.fn()
    window.addEventListener('av-kit:capture:error', onError)
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = hrefOf(input)
      const method = (init?.method ?? 'GET').toUpperCase()
      const body = typeof init?.body === 'string' && init.body.length > 0 ? JSON.parse(init.body) : undefined
      const path = new URL(url).pathname
      calls.push({ url, path, method, body, at: performance.now() })
      if (path.includes('/settings/capture')) {
        if (method === 'PUT') {
          saved = { ...saved, ...(body as Record<string, unknown>) }
        }
        return jsonResponse(saved)
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
            cropWaiters.push(resolve)
          })
        }
        const sourceId = decodeURIComponent(crop[1] as string)
        const folder = Object.keys(folders).find((key) => folders[key]?.some((row) => row.id === sourceId)) as string
        const source = (folders[folder] as Shot[]).find((row) => row.id === sourceId) as Shot
        const stem = source.display_name.replace(/\.[^.]+$/, '')
        // Older than both A shots, so the page's newest-shot pick never lands on it by chance.
        const made = { ...shot(`${source.id}-crop`, `${stem}-crop.png`, folder, 9), width: 300, height: 150 }
        folders[folder] = [made, ...(folders[folder] as Shot[])]
        if (listLag) {
          unlisted.add(made.id)
        }
        return jsonResponse({ item: made, source_id: source.id, clamped: false }, 201)
      }
      if (/\/captures\/[^/]+\/annotate$/.test(path) && method === 'POST') {
        return jsonResponse({ ok: true })
      }
      const detail = path.match(/\/captures\/([^/]+)$/)
      if (detail && method === 'GET') {
        const id = decodeURIComponent(detail[1] as string)
        if (detailHold.has(id)) {
          await new Promise<void>((resolve) => {
            detailWaiters[id] = [...(detailWaiters[id] ?? []), resolve]
          })
        }
        // The backend answers by the inbox saved when it answers (INBOX_SCOPE_BY_ID).
        const row = inbox().find((item) => item.id === id)
        if (row === undefined) {
          return jsonResponse(
            { error: { code: 'not_found', message: `capture shot ${id} not found`, details: null } },
            404,
          )
        }
        return jsonResponse({ ...row, annotations: [], backup_path: null })
      }
      if (/\/captures\/?$/.test(path) && method === 'GET') {
        if (listHold) {
          await new Promise<void>((resolve) => {
            listWaiters.push(resolve)
          })
        }
        return jsonResponse({ items: inbox().filter((row) => !unlisted.has(row.id)) })
      }
      return jsonResponse({})
    })
    vi.stubGlobal('fetch', fetchMock)
    window.fetch = fetchMock as typeof window.fetch
  })

  afterEach(() => {
    for (const release of [...cropWaiters, ...listWaiters, ...Object.values(detailWaiters).flat()]) {
      release()
    }
    window.removeEventListener('av-kit:capture:error', onError)
    cleanup()
    appQueryClient.clear()
    vi.unstubAllGlobals()
  })

  function listGets(): Call[] {
    return calls.filter((call) => call.method === 'GET' && /\/captures\/?$/.test(call.path))
  }

  function detailGets(id: string, from = 0): Call[] {
    return calls.slice(from).filter((call) => call.method === 'GET' && call.path.endsWith(`/captures/${id}`))
  }

  function puts(): Call[] {
    return calls.filter((call) => call.method === 'PUT' && call.path.includes('/settings/capture'))
  }

  function currentName(): string {
    return document.querySelector('[data-testid="capture-filmstrip-item"][aria-current="true"]')?.textContent ?? ''
  }

  function filmstripNames(): string[] {
    return screen.queryAllByTestId('capture-filmstrip-item').map((node) => node.textContent ?? '')
  }

  function statusText(): string {
    return screen.queryByTestId('capture-status')?.textContent ?? ''
  }

  /** Ends the hold and answers every held list request, so a later refetch of the same query answers too. */
  function releaseList(): void {
    listHold = false
    const queued = listWaiters
    listWaiters = []
    for (const release of queued) {
      release()
    }
  }

  function releaseDetail(id: string): void {
    detailHold.delete(id)
    const queued = detailWaiters[id] ?? []
    detailWaiters[id] = []
    for (const release of queued) {
      release()
    }
  }

  function releaseCrop(): void {
    const queued = cropWaiters
    cropWaiters = []
    for (const release of queued) {
      release()
    }
  }

  /** Renders on inbox A; a1, the newest, is current. `ready` waits for its detail (unless it is held). */
  async function renderOnA(ready = true): Promise<void> {
    appQueryClient.setQueryData(['captures'], { items: [...inbox()], pendingInteractive: false })
    appQueryClient.setQueryData(['settings', 'capture'], { ...saved })
    render(createElement(QueryClientProvider, { client: appQueryClient }, createElement(CapturePage)))
    await vi.waitFor(() => {
      expect(filmstripNames()).toHaveLength(2)
      expect(currentName()).toContain('a-1.png')
    })
    if (ready) {
      await vi.waitFor(() => {
        expect(present('capture-draw-surface').getAttribute('data-overlay-ready')).toBe('true')
      })
    }
    await settle()
  }

  async function select(name: string): Promise<void> {
    const thumb = screen.getAllByTestId('capture-filmstrip-item').find((node) => node.textContent?.includes(name))
    expect(thumb, `thumb ${name}`).toBeDefined()
    await user.click(thumb as HTMLElement)
    await vi.waitFor(() => {
      expect(present('capture-shot-info').textContent).toContain(name)
      expect(present('capture-draw-surface').getAttribute('data-overlay-ready')).toBe('true')
    })
  }

  async function openOptions(): Promise<void> {
    if (screen.queryByTestId('capture-inbox-path') === null) {
      await user.click(present('capture-settings-toggle'))
    }
    present('capture-inbox-path')
  }

  /** Types `dir` into the page's Inbox field and clicks Save; waits for the PUT. */
  async function saveInbox(dir: string): Promise<void> {
    await openOptions()
    const before = puts().length
    fireEvent.change(present<HTMLInputElement>('capture-inbox-path'), { target: { value: dir } })
    await user.click(present('capture-page-save'))
    await vi.waitFor(() => {
      expect(puts()).toHaveLength(before + 1)
    })
  }

  /** Opens a1 (400×200) in the crop tool, shrinks the box and clicks Save with the POST held. */
  async function startHeldCrop(): Promise<void> {
    await select('a-1.png')
    const surface = present('capture-draw-surface')
    bindSurface(surface)
    await user.click(present('capture-tool-crop'))
    present('capture-crop-bar')
    await act(async () => {
      dispatchPointer(surface, 'pointerdown', 400, 200)
      dispatchPointer(surface, 'pointermove', 300, 150)
      dispatchPointer(surface, 'pointerup', 300, 150)
    })
    cropHold = true
    await user.click(present('capture-crop-save'))
    await vi.waitFor(() => {
      expect(cropWaiters).toHaveLength(1)
    })
  }

  /** Asks the page's catalog query for a fresh answer, as the poll would, without waiting for it. */
  function askForList(): void {
    act(() => {
      void appQueryClient.invalidateQueries({ queryKey: ['captures'] })
    })
  }

  it('AC-166.5 a saved inbox change asks for the list again at once', async () => {
    await renderOnA()
    const before = listGets()
    const lastBefore = before[before.length - 1]?.at ?? performance.now()
    await saveInbox(INBOX_B)
    const putAt = calls.findIndex((call) => call.method === 'PUT' && call.path.includes('/settings/capture'))
    await settle(100)
    await settle(100)
    const after = calls.slice(putAt).filter((call) => call.method === 'GET' && /\/captures\/?$/.test(call.path))
    expect(after, 'one more GET /captures after the save').toHaveLength(1)
    expect((after[0] as Call).at - lastBefore, 'it is not the 5 s poll').toBeLessThan(4500)
  })

  it('guard AC-166.5 a key-only save asks for no list', async () => {
    await renderOnA()
    const before = listGets().length
    await openOptions()
    await user.click(present('capture-hotkey-change'))
    fireEvent.keyDown(present('capture-hotkey'), { key: 'F3' })
    await user.click(present('capture-page-save'))
    await vi.waitFor(() => {
      expect(puts().map((call) => call.body)).toEqual([{ hotkey: 'F3' }])
    })
    await settle(100)
    await settle(100)
    expect(listGets(), 'no GET /captures follows a key-only save').toHaveLength(before)
  })

  it('AC-166.6 a selected shot that left the list is cleared', async () => {
    await renderOnA()
    await select('a-2.png')
    listHold = true
    await saveInbox(INBOX_B)
    askForList()
    await vi.waitFor(() => {
      expect(listWaiters.length).toBeGreaterThan(0)
    })
    const answeredAt = calls.length
    releaseList()
    await settle()
    await vi.waitFor(() => {
      expect(filmstripNames()).toHaveLength(1)
      expect(currentName(), 'b1 is the current filmstrip item').toContain('b-1.png')
      expect(present('capture-shot-info').textContent, 'the viewport shows b1').toContain('b-1.png')
    })
    await settle()
    expect(detailGets('a2', answeredAt), 'no detail request for a2 after the answer').toHaveLength(0)
    expect(errors, 'no av-kit:capture:error event').toEqual([])

    listHold = true
    await saveInbox(INBOX_C)
    askForList()
    await vi.waitFor(() => {
      expect(listWaiters.length).toBeGreaterThan(0)
    })
    const emptyAt = calls.length
    releaseList()
    await settle()
    await vi.waitFor(() => {
      expect(filmstripNames()).toHaveLength(0)
      expect(screen.queryByTestId('capture-empty'), 'the empty state shows').not.toBeNull()
    })
    await settle()
    expect(detailGets('b1', emptyAt), 'no detail request for b1 after the empty answer').toHaveLength(0)
    expect(errors, 'no av-kit:capture:error event').toEqual([])
  })

  it('guard AC-166.6 a selection that no list has held is kept within one inbox', async () => {
    await renderOnA()
    listLag = true
    await startHeldCrop()
    const releasedAt = calls.length
    releaseCrop()
    await vi.waitFor(() => {
      expect(statusText()).toBe('Saved crop as a-1-crop.png.')
    })
    await settle()
    expect(detailGets('a1-crop', releasedAt).length, 'the crop copy stays selected and loads').toBeGreaterThan(0)
    expect(filmstripNames().some((name) => name.includes('a-1-crop.png')), 'no answer has held it yet').toBe(false)
    askForList()
    await settle()
    expect(statusText(), 'a list answer that lacks it keeps it').toBe('Saved crop as a-1-crop.png.')
    unlisted.clear()
    askForList()
    await vi.waitFor(() => {
      expect(currentName()).toContain('a-1-crop.png')
    })
    expect(errors).toEqual([])
  })

  it('AC-166.8 a result or a not-found from the old folder leaves the new list alone', async () => {
    // (a) A crop of a1 is held across the save of inbox B and B's list answer, then released.
    await renderOnA()
    await startHeldCrop()
    await saveInbox(INBOX_B)
    askForList()
    await vi.waitFor(() => {
      expect(filmstripNames()).toHaveLength(1)
      expect(currentName()).toContain('b-1.png')
    })
    const releasedAt = calls.length
    releaseCrop()
    await settle(100)
    await settle(100)
    expect(currentName(), '(a) b1 stays selected').toContain('b-1.png')
    expect(detailGets('a1-crop', releasedAt), "(a) no detail request for the crop's id").toHaveLength(0)
    expect(errors, '(a) no av-kit:capture:error event').toEqual([])
    expect(statusText(), '(a) no crop notice').not.toContain('Saved crop')

    // (b) a1's detail read is held across the save of inbox B; it answers 404 before B's held list.
    cleanup()
    appQueryClient.clear()
    reset()
    detailHold.add('a1')
    await renderOnA(false)
    await vi.waitFor(() => {
      expect(detailWaiters.a1?.length ?? 0).toBeGreaterThan(0)
    })
    listHold = true
    await saveInbox(INBOX_B)
    askForList()
    await vi.waitFor(() => {
      expect(listWaiters.length).toBeGreaterThan(0)
    })
    releaseDetail('a1')
    await settle(100)
    releaseList()
    await settle()
    await vi.waitFor(() => {
      expect(currentName(), '(b) b1 becomes current').toContain('b-1.png')
    })
    expect(errors, '(b) no av-kit:capture:error event').toEqual([])
    expect(statusText(), '(b) no error line').not.toContain('not found')
  })

  it('guard AC-166.8 a crop result in the same inbox is selected', async () => {
    await renderOnA()
    await startHeldCrop()
    releaseCrop()
    await vi.waitFor(() => {
      expect(currentName()).toContain('a-1-crop.png')
      expect(statusText()).toBe('Saved crop as a-1-crop.png.')
    })
    expect(errors).toEqual([])
  })
})
