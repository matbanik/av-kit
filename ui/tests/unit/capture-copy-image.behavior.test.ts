/** @vitest-environment jsdom */

import { readdirSync, readFileSync, statSync } from 'node:fs'
import { join, resolve } from 'node:path'

import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClientProvider } from '@tanstack/react-query'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { CapturePage } from '../../src/renderer/src/features/capture/CapturePage'
import * as clipboard from '../../src/renderer/src/features/capture/capture-clipboard'
import {
  APPLY_TITLES,
  REVERT_DIRTY_TITLE,
  applyState,
  flattenConfirmText,
  flattenStatus,
} from '../../src/renderer/src/features/capture/capture-flatten'
import { CAPTURE_HELP_SECTIONS } from '../../src/renderer/src/features/capture/capture-help-content'
import * as image from '../../src/renderer/src/features/capture/capture-image'
import { queryClient } from '../../src/renderer/src/lib/query-client'
import { listCommands } from '../../src/renderer/src/registry/commandRegistry'
import { RESERVED_CHORDS } from '../../src/renderer/src/registry/shortcuts'

// Session 69 (MEU-104): Copy image with the current marks, the as-shown filmstrip copy, the renamed
// shot actions and Save and flatten, on the real CapturePage with the app's query client.

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

function shot(id: string, name: string, createdAt: string, annotatedPath: string | null = null): Shot {
  return {
    id,
    original_path: `C:/shots/${name}`,
    annotated_path: annotatedPath,
    sidecar_path: null,
    display_name: name,
    width: 8,
    height: 8,
    file_size: 32,
    source: 'gui',
    created_at: createdAt,
    updated_at: createdAt,
  }
}

// Filmstrip order is newest first: A, B, C.
const SHOT_A = shot('shot-a', 'a.png', '2026-11-13T12:00:00Z')
const SHOT_B = shot('shot-b', 'b.png', '2026-11-13T11:00:00Z')

const PNG_SIG = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]
const PNG_BYTES = Uint8Array.from([...PNG_SIG, 0, 0, 0, 13, 0x49, 0x48, 0x44, 0x52])
// The fake render route's answer: distinct from PNG_BYTES so the clipboard bytes trace to it.
const RENDER_BYTES = Uint8Array.from([...PNG_SIG, 0x52, 0x45, 0x4e, 0x44])
const SAVED_RECT = { type: 'rect', x: 1, y: 1, width: 2, height: 2, color: '#ff0000', stroke_width: 2 }
const BACKUP = 'C:/shots/.avkit-backup/a.20261113-120000.png'

type FetchCall = { url: string; method: string; body: string | null }
type ChordInit = { ctrl?: boolean; meta?: boolean; shift?: boolean; alt?: boolean; repeat?: boolean }

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

function errorResponse(status: number, message: string): Response {
  return jsonResponse({ error: { code: 'capture_error', message, details: null } }, status)
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

/** Dispatches one keydown on `target` inside act and returns it, so a test reads `defaultPrevented`. */
async function chord(target: EventTarget, key: string, init: ChordInit = { ctrl: true }): Promise<KeyboardEvent> {
  const event = new KeyboardEvent('keydown', {
    key,
    ctrlKey: init.ctrl ?? false,
    metaKey: init.meta ?? false,
    shiftKey: init.shift ?? false,
    altKey: init.alt ?? false,
    repeat: init.repeat ?? false,
    bubbles: true,
    cancelable: true,
  })
  await act(async () => {
    target.dispatchEvent(event)
  })
  return event
}

describe('MEU-104 capture copy image and shot actions', () => {
  let user: ReturnType<typeof userEvent.setup>
  let items: Shot[]
  const calls: FetchCall[] = []
  let savedMarks: unknown[]
  let backupPath: string | null
  let renderStatus: number
  let annotateStatus: number
  let holdDetail: Promise<void> | null
  let writeClipboardImage: ReturnType<typeof vi.fn> | undefined

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
    if (writeClipboardImage !== undefined) {
      ;(window.api as unknown as Record<string, unknown>).writeClipboardImage = writeClipboardImage
    }
  }

  beforeEach(() => {
    user = userEvent.setup()
    items = [SHOT_A, SHOT_B]
    calls.length = 0
    savedMarks = []
    backupPath = null
    renderStatus = 200
    annotateStatus = 200
    holdDetail = null
    writeClipboardImage = vi.fn(async (_png: Uint8Array) => undefined)
    const captureSettings = {
      inbox_dir: 'C:/Pictures/av-kit',
      hotkey: 'F2',
      copy_to_clipboard: false,
      close_to_tray: true,
      flatten_backup: true,
      backup_dir: '',
      annotated_format: 'png',
    }
    queryClient.setQueryData(['captures'], { items: [...items], pendingInteractive: false })
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
      if (/\/captures\/.+\/render$/.test(path)) {
        if (renderStatus !== 200) {
          return errorResponse(renderStatus, 'render refused')
        }
        return new Response(RENDER_BYTES, { status: 200, headers: { 'Content-Type': 'image/png' } })
      }
      if (path.endsWith('/annotate')) {
        if (annotateStatus !== 200) {
          return errorResponse(annotateStatus, 'disk full')
        }
        savedMarks = (JSON.parse(String(init?.body ?? '{}')) as { annotations: unknown[] }).annotations
        return jsonResponse({ ...SHOT_A, annotations: savedMarks, backup_path: backupPath })
      }
      if (path.endsWith('/flatten')) {
        return jsonResponse({ ...SHOT_A, annotations: [], backup_path: BACKUP })
      }
      const one = path.match(/\/captures\/([^/]+)$/)
      if (one && method === 'GET') {
        if (holdDetail !== null) {
          await holdDetail
        }
        const id = decodeURIComponent(one[1] as string)
        const row = items.find((item) => item.id === id) ?? SHOT_A
        return jsonResponse({ ...row, annotations: savedMarks, backup_path: backupPath })
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
    cleanup()
    queryClient.clear()
    vi.unstubAllGlobals()
    window.getSelection()?.removeAllRanges()
  })

  async function renderPage(): Promise<void> {
    queryClient.setQueryData(['captures'], { items: [...items], pendingInteractive: false })
    mockApi()
    render(createElement(QueryClientProvider, { client: queryClient }, createElement(CapturePage)))
    await vi.waitFor(() => {
      expect(screen.queryAllByTestId('capture-filmstrip-item')).toHaveLength(items.length)
    })
  }

  function thumbs(): HTMLElement[] {
    return screen.queryAllByTestId('capture-filmstrip-item')
  }

  function surface(): HTMLElement {
    const found = screen.queryByTestId('capture-draw-surface')
    expect(found).not.toBeNull()
    return found as HTMLElement
  }

  async function waitReady(): Promise<HTMLElement> {
    await vi.waitFor(() => {
      expect(screen.queryByTestId('capture-draw-surface')?.getAttribute('data-overlay-ready')).toBe('true')
    })
    const el = surface()
    bindRect(el, { left: 0, top: 0, width: 200, height: 200 })
    return el
  }

  /** Render, select the newest shot with a click, and wait until its overlay is ready. */
  async function openFirst(): Promise<HTMLElement> {
    await renderPage()
    await user.click(thumbs()[0] as HTMLElement)
    return waitReady()
  }

  async function drawArrow(el: HTMLElement): Promise<void> {
    const pointer = (type: string, x: number, y: number) =>
      el.dispatchEvent(
        new PointerEvent(type, { bubbles: true, cancelable: true, clientX: x, clientY: y, pointerId: 1, pointerType: 'mouse', isPrimary: true }),
      )
    // A shot with saved marks opens on the Select tool (CapturePage.tsx overlay load).
    await user.click(control('capture-tool-arrow'))
    await act(async () => {
      // Clear of SAVED_RECT, which covers screen 25-75 at the 25 px/px fit.
      pointer('pointerdown', 110, 110)
      pointer('pointermove', 190, 190)
      pointer('pointerup', 190, 190)
    })
    expect(document.querySelectorAll('[data-annotation-type="arrow"]')).toHaveLength(1)
  }

  async function focus(el: HTMLElement): Promise<void> {
    await act(async () => {
      el.focus()
    })
  }

  function control(testid: string): HTMLElement {
    const found = screen.queryByTestId(testid)
    expect(found, testid).not.toBeNull()
    return found as HTMLElement
  }

  function renders(): FetchCall[] {
    return calls.filter((call) => call.method === 'POST' && /\/captures\/[^/]+\/render$/.test(call.url))
  }

  function postsTo(suffix: string): FetchCall[] {
    return calls.filter((call) => call.method === 'POST' && call.url.endsWith(suffix))
  }

  function status(): string {
    return screen.queryByTestId('capture-status')?.textContent ?? ''
  }

  /** The order of the action row's mounted buttons, by test id. */
  function actionOrder(): string[] {
    const ids = ['capture-save', 'capture-copy-image', 'capture-apply-image', 'capture-revert-image']
    return Array.from(document.querySelectorAll('button[data-testid]'))
      .map((el) => el.getAttribute('data-testid') ?? '')
      .filter((id) => ids.includes(id))
  }

  function bodyMarks(call: FetchCall | undefined): Array<Record<string, unknown>> {
    expect(call).not.toBeUndefined()
    return (JSON.parse(call?.body ?? '{}') as { annotations: Array<Record<string, unknown>> }).annotations
  }

  it('AC-104.1 the TypeScript signatures of postAuthorizedBlob, renderClipboardPng and loadClipboardPng', () => {
    expect(typeof image.postAuthorizedBlob).toBe('function')
    expect(image.postAuthorizedBlob.length).toBe(2)
    expect(typeof clipboard.renderClipboardPng).toBe('function')
    expect(clipboard.renderClipboardPng.length).toBe(2)
    expect(clipboard.loadClipboardPng.length).toBe(1)
    const source = readFileSync(resolve(__dirname, '../../src/renderer/src/features/capture/capture-clipboard.ts'), 'utf8')
    expect(source).toMatch(
      /export async function loadClipboardPng\(\s*id: string,\s*variant: 'original' \| 'annotated' = 'original',?\s*\): Promise<Uint8Array>/,
    )
    expect(source).toMatch(
      /export async function renderClipboardPng\(id: string, annotations: readonly Annotation\[\]\): Promise<Uint8Array>/,
    )
    const imageSource = readFileSync(resolve(__dirname, '../../src/renderer/src/features/capture/capture-image.ts'), 'utf8')
    expect(imageSource).toMatch(/export async function postAuthorizedBlob\(path: string, body: unknown\): Promise<Blob \| null>/)
  })

  it('AC-104.11 Ctrl+C on the canvas posts the unsaved mark to render and writes exactly the returned bytes', async () => {
    const el = await openFirst()
    await drawArrow(el)
    await focus(el)
    const event = await chord(el, 'c')
    expect(event.defaultPrevented, 'Ctrl+C on the canvas is taken').toBe(true)
    await vi.waitFor(() => {
      expect(writeClipboardImage).toHaveBeenCalledTimes(1)
    })
    expect(renders()).toHaveLength(1)
    expect(renders()[0]?.url).toContain('/captures/shot-a/render')
    const marks = bodyMarks(renders()[0])
    expect(marks).toHaveLength(1)
    expect(marks[0]?.type).toBe('arrow')
    const png = writeClipboardImage?.mock.calls[0]?.[0] as Uint8Array
    expect(Array.from(png)).toEqual(Array.from(RENDER_BYTES))
    expect(postsTo('/annotate')).toHaveLength(0)
    await vi.waitFor(() => {
      expect(status()).toBe('Copied a.png as an image.')
    })
  })

  it('AC-104.12 Ctrl+C and Cmd+C on the canvas each make one render', async () => {
    const el = await openFirst()
    await focus(el)
    const ctrl = await chord(el, 'c', { ctrl: true })
    expect(ctrl.defaultPrevented).toBe(true)
    await vi.waitFor(() => {
      expect(renders()).toHaveLength(1)
    })
    const meta = await chord(el, 'C', { meta: true })
    expect(meta.defaultPrevented).toBe(true)
    await vi.waitFor(() => {
      expect(renders()).toHaveLength(2)
    })
    expect(bodyMarks(renders()[0])).toEqual([])
  })

  it('AC-104.12 the guard rows make no render and no preventDefault, then a plain Ctrl+C makes one', async () => {
    const el = await openFirst()
    const cases: Array<[string, () => Promise<KeyboardEvent>, (() => Promise<void>) | null]> = []
    const textarea = document.createElement('textarea')
    document.body.appendChild(textarea)
    const editable = document.createElement('div')
    editable.setAttribute('contenteditable', 'true')
    document.body.appendChild(editable)
    const para = document.createElement('p')
    para.textContent = 'selected words'
    document.body.appendChild(para)
    cases.push([
      'textarea',
      async () => {
        await focus(textarea)
        return chord(textarea, 'c')
      },
      null,
    ])
    cases.push([
      'contenteditable',
      async () => {
        await focus(editable)
        return chord(editable, 'c')
      },
      null,
    ])
    cases.push([
      'selection',
      async () => {
        await focus(el)
        window.getSelection()?.selectAllChildren(para)
        return chord(el, 'c')
      },
      async () => {
        window.getSelection()?.removeAllRanges()
      },
    ])
    for (const [label, init] of [
      ['repeat', { ctrl: true, repeat: true }],
      ['shift', { ctrl: true, shift: true }],
      ['alt', { ctrl: true, alt: true }],
    ] as Array<[string, ChordInit]>) {
      cases.push([
        label,
        async () => {
          await focus(el)
          return chord(el, 'c', init)
        },
        null,
      ])
    }
    cases.push([
      'confirm open',
      async () => {
        await user.click(control('capture-delete'))
        expect(screen.queryByTestId('capture-confirm-strip')).not.toBeNull()
        await focus(el)
        return chord(el, 'c')
      },
      async () => {
        await user.click(control('capture-delete-confirm-cancel'))
      },
    ])
    cases.push([
      'crop',
      async () => {
        await user.click(control('capture-tool-crop'))
        await focus(el)
        return chord(el, 'c')
      },
      async () => {
        await user.keyboard('{Escape}')
        await user.click(control('capture-tool-select'))
      },
    ])
    cases.push([
      'text draft',
      async () => {
        await user.click(control('capture-tool-text'))
        await act(async () => {
          el.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, cancelable: true, clientX: 25, clientY: 175, pointerId: 1 }))
          el.dispatchEvent(new PointerEvent('pointerup', { bubbles: true, cancelable: true, clientX: 25, clientY: 175, pointerId: 1 }))
        })
        const draft = control('capture-text-draft')
        await focus(draft)
        return chord(draft, 'c')
      },
      async () => {
        await user.keyboard('{Escape}')
        await user.click(control('capture-tool-select'))
      },
    ])
    for (const [label, run, undo] of cases) {
      const event = await run()
      expect(event.defaultPrevented, `${label} not prevented`).toBe(false)
      expect(renders(), `${label} no render`).toHaveLength(0)
      if (undo !== null) {
        await undo()
      }
    }
    await focus(el)
    const plain = await chord(el, 'c')
    expect(plain.defaultPrevented, 'plain Ctrl+C taken').toBe(true)
    await vi.waitFor(() => {
      expect(renders()).toHaveLength(1)
    })
  })

  it('AC-104.12 no shot and an overlay still loading make no render; once ready Ctrl+C makes one', async () => {
    let release: () => void = () => undefined
    holdDetail = new Promise<void>((done) => {
      release = done
    })
    await renderPage()
    const none = await chord(window, 'c')
    expect(none.defaultPrevented, 'no shot not prevented').toBe(false)
    await user.click(thumbs()[0] as HTMLElement)
    const el = surface()
    expect(el.getAttribute('data-overlay-ready')).not.toBe('true')
    await focus(el)
    const loading = await chord(el, 'c')
    expect(loading.defaultPrevented, 'loading not prevented').toBe(false)
    expect(renders()).toHaveLength(0)
    await act(async () => {
      release()
    })
    await waitReady()
    await focus(el)
    const ready = await chord(el, 'c')
    expect(ready.defaultPrevented, 'ready Ctrl+C taken').toBe(true)
    await vi.waitFor(() => {
      expect(renders()).toHaveLength(1)
    })
  })

  it('AC-104.13 the Copy image button sits after Save when dirty and before Flatten, shows Ctrl+C, and posts the current marks', async () => {
    savedMarks = [SAVED_RECT]
    await renderPage()
    const idle = screen.queryByTestId('capture-copy-image') as HTMLButtonElement | null
    expect(idle, 'Copy image is mounted with no shot').not.toBeNull()
    expect(idle?.disabled, 'disabled with no shot').toBe(true)
    await user.click(thumbs()[0] as HTMLElement)
    const el = await waitReady()
    expect(actionOrder()).toEqual(['capture-copy-image', 'capture-apply-image'])
    const button = control('capture-copy-image') as HTMLButtonElement
    expect(button.getAttribute('aria-label')).toBe('Copy image')
    expect(button.getAttribute('aria-keyshortcuts')).toBe('Control+C')
    await focus(button)
    expect(screen.queryByTestId('capture-copy-image-hint')?.textContent).toBe('Copy image (Ctrl+C)')
    await user.click(button)
    await vi.waitFor(() => {
      expect(renders()).toHaveLength(1)
    })
    expect(bodyMarks(renders()[0])).toEqual([SAVED_RECT])
    await drawArrow(el)
    expect(actionOrder()).toEqual(['capture-save', 'capture-copy-image', 'capture-apply-image'])
    await user.click(control('capture-copy-image'))
    await vi.waitFor(() => {
      expect(renders()).toHaveLength(2)
    })
    expect(bodyMarks(renders()[1]).map((mark) => mark.type)).toEqual(['rect', 'arrow'])
    expect(postsTo('/annotate')).toHaveLength(0)
    await vi.waitFor(() => {
      expect(writeClipboardImage).toHaveBeenCalledTimes(2)
    })
  })

  it('AC-104.13 the Copy image button is disabled before the overlay loads and while a text draft is open', async () => {
    let release: () => void = () => undefined
    holdDetail = new Promise<void>((done) => {
      release = done
    })
    await renderPage()
    await user.click(thumbs()[0] as HTMLElement)
    const loading = screen.queryByTestId('capture-copy-image') as HTMLButtonElement | null
    expect(loading, 'mounted while loading').not.toBeNull()
    expect(loading?.disabled, 'disabled while loading').toBe(true)
    await act(async () => {
      release()
    })
    const el = await waitReady()
    expect((control('capture-copy-image') as HTMLButtonElement).disabled).toBe(false)
    await user.click(control('capture-tool-text'))
    await act(async () => {
      el.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, cancelable: true, clientX: 25, clientY: 175, pointerId: 1 }))
      el.dispatchEvent(new PointerEvent('pointerup', { bubbles: true, cancelable: true, clientX: 25, clientY: 175, pointerId: 1 }))
    })
    expect(screen.queryByTestId('capture-text-draft')).not.toBeNull()
    expect((control('capture-copy-image') as HTMLButtonElement).disabled, 'disabled with a draft').toBe(true)
    expect(renders()).toHaveLength(0)
  })

  it('AC-104.14 a refused render, a missing writeClipboardImage and a throwing fake each show the copy error with no path', async () => {
    renderStatus = 404
    const el = await openFirst()
    expect(screen.queryByTestId('capture-copy-image')).not.toBeNull()
    await user.click(control('capture-copy-image'))
    await vi.waitFor(() => {
      expect(status()).toBe('Could not copy a.png: the image could not be loaded')
    })
    expect(writeClipboardImage).not.toHaveBeenCalled()
    renderStatus = 200
    writeClipboardImage?.mockRejectedValueOnce(
      new Error("Error invoking remote method 'clipboard:write-image': Error: the clipboard is busy"),
    )
    await focus(el)
    await chord(el, 'c')
    await vi.waitFor(() => {
      expect(status()).toBe('Could not copy a.png: the clipboard is busy')
    })
    expect(status()).not.toContain('C:/shots')
  })

  it('AC-104.14 without writeClipboardImage Copy image reports it is unavailable and posts no render', async () => {
    writeClipboardImage = undefined
    await openFirst()
    expect(screen.queryByTestId('capture-copy-image')).not.toBeNull()
    await user.click(control('capture-copy-image'))
    await vi.waitFor(() => {
      expect(status()).toBe('Could not copy a.png: copying images is not available in this window')
    })
    expect(renders()).toHaveLength(0)
  })

  it('AC-104.14 renderClipboardPng refuses marks the annotate schema refuses, with COPY_IMAGE_MARKS_ERROR and no request', async () => {
    mockApi()
    const bad = [{ type: 'rect', x: 'C:/shots/a.png' }] as unknown as Parameters<typeof clipboard.renderClipboardPng>[1]
    await expect(clipboard.renderClipboardPng('shot-a', bad)).rejects.toThrow(clipboard.COPY_IMAGE_MARKS_ERROR)
    expect(clipboard.COPY_IMAGE_MARKS_ERROR).not.toContain('C:/')
    expect(calls).toHaveLength(0)
  })

  it('AC-104.15 the filmstrip copy fetches the annotated variant only for a non-empty annotated_path', async () => {
    items = [
      shot('shot-a', 'a.png', '2026-11-13T12:00:00Z', 'C:/shots/a.annotated.png'),
      shot('shot-b', 'b.png', '2026-11-13T11:00:00Z', null),
      shot('shot-c', 'c.png', '2026-11-13T10:00:00Z', ''),
    ]
    await openFirst()
    const expected: Array<[number, string]> = [
      [0, '/captures/shot-a/image?variant=annotated'],
      [1, '/captures/shot-b/image?variant=original'],
      [2, '/captures/shot-c/image?variant=original'],
    ]
    for (const [index, url] of expected) {
      const before = calls.length
      fireEvent.contextMenu(thumbs()[index] as HTMLElement, { clientX: 120, clientY: 80 })
      await user.click(control('capture-filmstrip-menu-copy-image'))
      await vi.waitFor(() => {
        expect(writeClipboardImage).toHaveBeenCalledTimes(index + 1)
      })
      const fetched = calls.slice(before).filter((call) => call.url.includes('/image?variant='))
      expect(fetched.map((call) => call.url.slice(call.url.indexOf('/captures/'))), `thumb ${index}`).toEqual([url])
    }
  })

  it('AC-104.16 the action row and the confirm strips read the new names', async () => {
    savedMarks = [SAVED_RECT]
    backupPath = BACKUP
    const el = await openFirst()
    expect(control('capture-apply-image').getAttribute('aria-label')).toBe('Flatten into image…')
    expect(control('capture-revert-image').getAttribute('aria-label')).toBe('Restore backup…')
    await user.click(control('capture-apply-image'))
    expect(control('capture-flatten-confirm').textContent).toBe('Flatten into image')
    await user.click(control('capture-flatten-confirm-cancel'))
    await user.click(control('capture-revert-image'))
    expect(control('capture-revert-confirm').textContent).toBe('Restore backup')
    await user.click(control('capture-revert-confirm-cancel'))
    await drawArrow(el)
    expect(control('capture-save').getAttribute('aria-label')).toBe('Save annotations')
    await user.click(control('capture-apply-image'))
    expect(control('capture-flatten-confirm').textContent).toBe('Save and flatten')
  })

  it('AC-104.16 no Save overlay, Apply to image or Revert image outside comment lines in ui/src', () => {
    const root = resolve(__dirname, '../../src')
    const files: string[] = []
    const walk = (dir: string): void => {
      for (const name of readdirSync(dir)) {
        const full = join(dir, name)
        if (statSync(full).isDirectory()) {
          walk(full)
        } else if (/\.(ts|tsx)$/.test(name)) {
          files.push(full)
        }
      }
    }
    walk(root)
    const hits: string[] = []
    const old = /Save overlay|Apply to image|Revert image/
    for (const file of files) {
      readFileSync(file, 'utf8')
        .split(/\r?\n/)
        .forEach((line, index) => {
          const trimmed = line.trim()
          if (trimmed.startsWith('//') || trimmed.startsWith('/**') || trimmed.startsWith('*')) {
            return
          }
          if (old.test(line)) {
            hits.push(`${file.slice(root.length)}:${index + 1}`)
          }
        })
    }
    expect(hits).toEqual([])
    for (const kept of [
      'renderer/src/features/capture/CaptureViewport.tsx',
      'renderer/src/features/capture/capture-commands.ts',
      'renderer/src/features/capture/capture-flatten.ts',
      'renderer/src/features/settings/settings-schemas.ts',
    ]) {
      const path = join(root, kept)
      expect(old.test(readFileSync(path, 'utf8')), `${kept} keeps its comment`).toBe(true)
    }
  })

  it('AC-104.17 applyState gives each row of SAVE_AND_FLATTEN', () => {
    const base = { selected: true, confirmOpen: false, originalPath: 'C:/shots/a.png' }
    const rows: Array<[string, Parameters<typeof applyState>[0], boolean, string | undefined]> = [
      ['clean, no saved marks', { ...base, savedCount: 0, currentCount: 0, dirty: false, canSave: true }, false, APPLY_TITLES.noMarks],
      ['clean, saved marks', { ...base, savedCount: 1, currentCount: 1, dirty: false, canSave: true }, true, undefined],
      [
        'clean, unflattenable',
        { ...base, originalPath: 'C:/shots/a.gif', savedCount: 1, currentCount: 1, dirty: false, canSave: true },
        false,
        APPLY_TITLES.fileType,
      ],
      ['dirty, no current marks', { ...base, savedCount: 1, currentCount: 0, dirty: true, canSave: true }, false, APPLY_TITLES.noMarks],
      ['dirty, canSave false', { ...base, savedCount: 0, currentCount: 2, dirty: true, canSave: false }, false, APPLY_TITLES.dirty],
      [
        'dirty, unflattenable',
        { ...base, originalPath: 'C:/shots/a.gif', savedCount: 0, currentCount: 2, dirty: true, canSave: true },
        false,
        APPLY_TITLES.fileType,
      ],
      ['dirty, enabled', { ...base, savedCount: 0, currentCount: 2, dirty: true, canSave: true }, true, undefined],
      ['dirty, enabled, confirm open', { ...base, confirmOpen: true, savedCount: 0, currentCount: 2, dirty: true, canSave: true }, false, undefined],
    ]
    for (const [label, input, enabled, title] of rows) {
      expect(applyState(input), label).toEqual({ enabled, title })
    }
  })

  it('AC-104.18 Save and flatten posts annotate before flatten, in that order', async () => {
    savedMarks = [SAVED_RECT]
    const el = await openFirst()
    await drawArrow(el)
    const apply = control('capture-apply-image') as HTMLButtonElement
    expect(apply.disabled, 'Flatten is enabled while dirty').toBe(false)
    await user.click(apply)
    expect(control('capture-flatten-confirm').textContent).toBe('Save and flatten')
    await user.click(control('capture-flatten-confirm'))
    await vi.waitFor(() => {
      expect(postsTo('/flatten')).toHaveLength(1)
    })
    const order = calls
      .filter((call) => call.method === 'POST' && /\/(annotate|flatten)$/.test(call.url))
      .map((call) => call.url.slice(call.url.lastIndexOf('/') + 1))
    expect(order).toEqual(['annotate', 'flatten'])
    expect(bodyMarks(postsTo('/annotate')[0]).map((mark) => mark.type)).toEqual(['rect', 'arrow'])
  })

  it('AC-104.18 a failed save posts no flatten and shows the error', async () => {
    savedMarks = [SAVED_RECT]
    annotateStatus = 500
    const el = await openFirst()
    await drawArrow(el)
    const apply = control('capture-apply-image') as HTMLButtonElement
    expect(apply.disabled, 'Flatten is enabled while dirty').toBe(false)
    await user.click(apply)
    await user.click(control('capture-flatten-confirm'))
    await vi.waitFor(() => {
      expect(postsTo('/annotate')).toHaveLength(1)
    })
    await vi.waitFor(() => {
      expect(status()).toContain('disk full')
    })
    expect(postsTo('/flatten')).toHaveLength(0)
  })

  it('AC-104.19 the status lines, confirm texts and titles read the D-694 literals', () => {
    expect(APPLY_TITLES.dirty).toBe('Save annotations first')
    expect(REVERT_DIRTY_TITLE).toBe('Save or discard unsaved marks first')
    expect(flattenStatus({ kind: 'flatten', backupBefore: null, backupAfter: 'C:/b/a.1.png' })).toBe(
      'Flattened into image. Backup: C:/b/a.1.png',
    )
    expect(flattenStatus({ kind: 'flatten', backupBefore: 'x', backupAfter: 'x' })).toBe('Flattened into image (no backup).')
    expect(flattenStatus({ kind: 'convert', displayName: 'a-converted.png' })).toBe('Flattened into a new PNG copy: a-converted.png.')
    expect(flattenStatus({ kind: 'revert', backupPath: 'C:/b/a.1.png' })).toBe('Restored from a.1.png.')
    const png = { displayName: 'a.png', originalPath: 'C:/shots/a.png', backupEnabled: true, backupDir: '' }
    const off = { ...png, backupEnabled: false }
    const jpg = { ...png, displayName: 'a.jpg', originalPath: 'C:/shots/a.jpg' }
    expect(flattenConfirmText({ ...png, unsaved: false })).toBe(
      'Bake the saved marks into a.png? The original is copied to the backup folder in the inbox first.',
    )
    expect(flattenConfirmText({ ...off, unsaved: false })).toBe('Bake the saved marks into a.png? Backups are off, so this cannot be undone.')
    expect(flattenConfirmText({ ...jpg, unsaved: false })).toBe(
      'Bake the saved marks into a new PNG copy of a.jpg? a.jpg itself stays unchanged.',
    )
    expect(flattenConfirmText({ ...png, unsaved: true })).toBe(
      'Save the current marks, then bake them into a.png? The original is copied to the backup folder in the inbox first.',
    )
    expect(flattenConfirmText({ ...off, unsaved: true })).toBe(
      'Save the current marks, then bake them into a.png? Backups are off, so this cannot be undone.',
    )
    expect(flattenConfirmText({ ...jpg, unsaved: true })).toBe(
      'Save the current marks, then bake them into a new PNG copy of a.jpg? a.jpg itself stays unchanged.',
    )
  })

  it('AC-104.20 the help body names Copy image, Ctrl+C, the text-field rule and the new action names', () => {
    const text = CAPTURE_HELP_SECTIONS.map((section) => section.body).join('\n')
    expect(text).toContain(
      'Copy image, or Ctrl+C while the image has focus, copies the shot with its current marks, saved or not; a text field keeps its own copy.',
    )
    for (const name of ['Flatten into image', 'Restore backup', 'Save annotations']) {
      expect(text, name).toContain(name)
    }
    expect(text).not.toContain('marks.Right-click')
    expect(text).toContain('a text field keeps its own copy. Right-click a thumbnail')
  })

  it('AC-104.23 RESERVED_CHORDS holds Ctrl+C and the command registry binds no copy command', () => {
    expect(RESERVED_CHORDS.has('Ctrl+C')).toBe(true)
    const entries = listCommands() as unknown as Array<Record<string, unknown>>
    const copies = entries.filter((entry) => /copy/i.test(String(entry.id)))
    expect(copies).toEqual([])
    const bound = entries.filter((entry) => JSON.stringify(entry).includes('"Ctrl+C"'))
    expect(bound).toEqual([])
  })
})
