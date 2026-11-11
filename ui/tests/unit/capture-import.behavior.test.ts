/** @vitest-environment jsdom */

// MEU-132 (Session 61) image import on the Capture page: AC-132.13 to AC-132.19.
// The harness is copied from capture-crop-tool.behavior.test.ts:1-222 (PointerEvent polyfill, hrefOf,
// jsonResponse, mockApi, the surface binding) with fakes for showFilesDialog, getPathForFile and
// pasteCaptureImage, and a stubbed fetch that records each request. No image leaves the test: /image
// answers three bytes and a dropped File holds one byte. Every element is looked up with queryByTestId
// and asserted present before use, so a Red run fails by assertion (red-check.py).

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
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

type PasteAnswer = Awaited<ReturnType<NonNullable<Window['api']['pasteCaptureImage']>>>

function mockApi(fakes: {
  showFilesDialog: (filters?: { name: string; extensions: string[] }[]) => Promise<string[]>
  getPathForFile: (file: File) => string
  pasteCaptureImage: () => Promise<PasteAnswer>
  writeClipboardText: (text: string) => Promise<void>
}): void {
  window.api = {
    getBackendUrl: async () => 'http://127.0.0.1:51234/api/v1',
    getToken: async () => 'gui-nonce',
    logStartupMetric: () => undefined,
    showDirectoryDialog: async () => 'C:/Pictures/av-kit',
    showFileDialog: async () => 'C:/e2e/sample.txt',
    showFilesDialog: fakes.showFilesDialog,
    getPathForFile: fakes.getPathForFile,
    openPath: async () => undefined,
    showItemInFolder: async () => undefined,
    readClipboardText: async () => '',
    writeClipboardText: fakes.writeClipboardText,
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
    pasteCaptureImage: fakes.pasteCaptureImage,
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

/** Every element is asserted present before use, so a missing one fails by assertion. */
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

async function drag(surface: HTMLElement, points: Array<[number, number]>): Promise<void> {
  const [first, ...rest] = points as [[number, number], ...Array<[number, number]>]
  const last = rest[rest.length - 1] ?? first
  await act(async () => {
    dispatchPointer(surface, 'pointerdown', first[0], first[1])
    for (const [x, y] of rest) {
      dispatchPointer(surface, 'pointermove', x, y)
    }
    dispatchPointer(surface, 'pointerup', last[0], last[1])
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

function shot(id: string, name: string, hour: number, minute = 0): Shot {
  const stamp = `2026-11-10T${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}:00Z`
  return {
    id,
    original_path: `C:/shots/${name}`,
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

const LAND = shot('land-1', 'land.png', 12)
const SPACED = shot('spaced-1', 'spaced.png', 11)
const OTHER = shot('other-1', 'other.png', 10)

const NOT_AN_IMAGE = 'not an image av-kit can open (png, jpg, jpeg, webp)'
const CROP_REASON = 'Finish or cancel the crop first'
const IMPORT_TITLE = 'Import image files. You can also drop them here or paste with Ctrl+V.'

type Call = { url: string; method: string; body?: unknown }

describe('MEU-132 capture image import page', () => {
  let user: ReturnType<typeof userEvent.setup>
  let queryClient: QueryClient
  let items: Shot[] = []
  let marks: Record<string, unknown[]> = {}
  /** Answers an import POST; the default adds a shot named for the path and answers 201 `{item}`. */
  let importAnswer: (path: string) => Promise<Response> | Response
  let importHold = false
  let importRelease: Array<() => void> = []
  let made = 0
  const calls: Call[] = []
  const paths = new Map<File, string>()
  let showFilesDialog: ReturnType<typeof vi.fn>
  let getPathForFile: ReturnType<typeof vi.fn>
  let pasteCaptureImage: ReturnType<typeof vi.fn>
  let writeClipboardText: ReturnType<typeof vi.fn>

  function listPath(url: string): boolean {
    return /\/captures\/?$/.test(url.split('?')[0] ?? url)
  }

  function importPosts(): string[] {
    return calls
      .filter((call) => call.method === 'POST' && listPath(call.url) && (call.body as { mode?: string })?.mode === 'import')
      .map((call) => String((call.body as { path?: string }).path))
  }

  function importBodies(): unknown[] {
    return calls.filter((call) => call.method === 'POST' && listPath(call.url)).map((call) => call.body)
  }

  function listGets(): number {
    return calls.filter((call) => call.method === 'GET' && listPath(call.url)).length
  }

  function addShotFor(path: string): Shot {
    made += 1
    const name = path.split(/[\\/]/).pop() ?? 'import.png'
    const row: Shot = { ...shot(`import-${made}`, name, 9, made), original_path: `C:/shots/${name}` }
    items = [...items, row]
    return row
  }

  beforeEach(() => {
    user = userEvent.setup()
    calls.length = 0
    paths.clear()
    items = [LAND, SPACED, OTHER]
    marks = {}
    made = 0
    importHold = false
    importRelease = []
    importAnswer = (path) => jsonResponse({ item: addShotFor(path) }, 201)
    queryClient = appQueryClient
    queryClient.setQueryData(['settings', 'capture'], {
      inbox_dir: 'C:/shots',
      hotkey: 'F2',
      copy_to_clipboard: false,
      close_to_tray: true,
    })
    showFilesDialog = vi.fn(async () => [] as string[])
    getPathForFile = vi.fn((file: File) => paths.get(file) ?? '')
    pasteCaptureImage = vi.fn(async (): Promise<PasteAnswer> => ({ kind: 'empty' }))
    writeClipboardText = vi.fn(async (_text: string) => undefined)
    mockApi({
      showFilesDialog: showFilesDialog as never,
      getPathForFile: getPathForFile as never,
      pasteCaptureImage: pasteCaptureImage as never,
      writeClipboardText: writeClipboardText as never,
    })
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
      if (listPath(path) && method === 'POST') {
        if (importHold) {
          await new Promise<void>((resolve) => {
            importRelease.push(resolve)
          })
        }
        return importAnswer(String((body as { path?: string }).path))
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
      if (listPath(path)) {
        return jsonResponse({ items })
      }
      return jsonResponse({})
    })
    vi.stubGlobal('fetch', fetchMock)
    window.fetch = fetchMock as typeof window.fetch
  })

  afterEach(() => {
    for (const release of importRelease) {
      release()
    }
    cleanup()
    queryClient.clear()
    vi.unstubAllGlobals()
    for (const node of Array.from(document.querySelectorAll('[data-s61-extra]'))) {
      node.remove()
    }
  })

  async function renderPage(): Promise<void> {
    queryClient.setQueryData(['captures'], { items: [...items], pendingInteractive: false })
    render(createElement(QueryClientProvider, { client: queryClient }, createElement(CapturePage)))
    await vi.waitFor(() => {
      expect(screen.queryAllByTestId('capture-filmstrip-item').length).toBe(items.length)
    })
  }

  /** Renders the page and selects `name`, waiting until its overlay is ready. */
  async function open(name: string): Promise<HTMLElement> {
    await renderPage()
    await select(name)
    const surface = screen.getByTestId('capture-draw-surface')
    bindSurface(surface, 400, 200)
    return surface
  }

  async function select(name: string): Promise<void> {
    const thumb = screen.getAllByTestId('capture-filmstrip-item').find((node) => node.textContent?.includes(name))
    expect(thumb, `thumb ${name}`).toBeDefined()
    await user.click(thumb as HTMLElement)
    await vi.waitFor(() => {
      expect(screen.getByTestId('capture-shot-info').textContent).toContain(name)
      expect(screen.getByTestId('capture-draw-surface').getAttribute('data-overlay-ready')).toBe('true')
    })
  }

  /** A one-byte File named `name`, whose path getPathForFile answers (empty unless given). */
  function file(name: string, path?: string): File {
    const made = new File([new Uint8Array([1])], name, { type: name.endsWith('.txt') ? 'text/plain' : 'image/png' })
    if (path !== undefined) {
      paths.set(made, path)
    }
    return made
  }

  /** Dispatches dragover then drop on capture-page; answers whether each was default-prevented. */
  function drop(files: File[], types: string[] = ['Files']): { dragover: boolean; drop: boolean } {
    const page = present('capture-page')
    const dataTransfer = { files, types, items: [], dropEffect: 'none', effectAllowed: 'all' }
    const overPassed = fireEvent.dragOver(page, { dataTransfer })
    const dropPassed = fireEvent.drop(page, { dataTransfer })
    return { dragover: !overPassed, drop: !dropPassed }
  }

  /** Fires a paste on `target`; answers whether it was default-prevented. */
  function paste(target: EventTarget): boolean {
    return !fireEvent.paste(target as Element)
  }

  function toastText(): string | null {
    return screen.queryByTestId('bulk-toast')?.textContent ?? null
  }

  async function waitToast(): Promise<string> {
    await vi.waitFor(() => {
      expect(screen.queryByTestId('bulk-toast'), 'the import toast').not.toBeNull()
    })
    return toastMessage()
  }

  /** The toast's message without its Dismiss label. */
  function toastMessage(): string {
    const toast = present('bulk-toast')
    const dismiss = screen.queryByTestId('bulk-toast-dismiss')
    const all = toast.textContent ?? ''
    return dismiss !== null ? all.replace(dismiss.textContent ?? '', '').trim() : all.trim()
  }

  async function settle(): Promise<void> {
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 30))
    })
  }

  describe('AC-132.13 IMPORT_BUTTON', () => {
    it('AC-132.13 the button follows capture-region in the header with its label, icon and title', async () => {
      await renderPage()
      const header = present('capture-header')
      const region = present('capture-region')
      const button = present<HTMLButtonElement>('capture-import')
      expect(header.contains(button)).toBe(true)
      expect(region.nextElementSibling).toBe(button)
      expect(button.textContent?.trim()).toBe('Import image…')
      const icon = button.querySelector('svg')
      expect(icon, 'the ImagePlus icon').not.toBeNull()
      expect(icon?.getAttribute('class') ?? '').toContain('lucide-image-plus')
      expect(icon?.getAttribute('aria-hidden')).toBe('true')
      expect(button.getAttribute('title')).toBe(IMPORT_TITLE)
    })

    it('AC-132.13 a click opens the image dialog and imports each chosen path in order, then refetches once', async () => {
      showFilesDialog.mockResolvedValueOnce(['C:\\in\\a.png', 'C:\\in\\b.jpg'])
      await renderPage()
      await user.click(present('capture-import'))
      expect(await waitToast()).toBe('Imported 2 of 2.')
      expect(showFilesDialog).toHaveBeenCalledTimes(1)
      expect(showFilesDialog).toHaveBeenCalledWith([{ name: 'Images', extensions: ['png', 'jpg', 'jpeg', 'webp'] }])
      expect(importBodies()).toEqual([
        { mode: 'import', path: 'C:\\in\\a.png' },
        { mode: 'import', path: 'C:\\in\\b.jpg' },
      ])
      // Counted from the first import POST: the list query's own refetch on mount may land before it.
      const methods = calls.map((call) => call.method)
      const listGetsFrom = (index: number): number =>
        calls.slice(index).filter((call) => call.method === 'GET' && listPath(call.url)).length
      expect(listGetsFrom(methods.lastIndexOf('POST'))).toBe(1)
      expect(listGetsFrom(methods.indexOf('POST'))).toBe(1)
    })

    it('AC-132.13 an empty dialog result sends nothing and shows no toast', async () => {
      await renderPage()
      await user.click(present('capture-import'))
      await vi.waitFor(() => {
        expect(showFilesDialog).toHaveBeenCalledTimes(1)
      })
      await settle()
      expect(importBodies()).toEqual([])
      expect(toastText()).toBeNull()
    })
  })

  describe('AC-132.14 IMPORT_DROP', () => {
    it('AC-132.14 a drop of three files imports the two images in order with the paths getPathForFile gave', async () => {
      await renderPage()
      const prevented = drop([
        file('red.png', 'C:\\drop\\red.png'),
        file('notes.txt', 'C:\\drop\\notes.txt'),
        file('green.png', 'C:\\drop\\green.png'),
      ])
      expect(prevented).toEqual({ dragover: true, drop: true })
      await waitToast()
      expect(importPosts()).toEqual(['C:\\drop\\red.png', 'C:\\drop\\green.png'])
      expect(getPathForFile).toHaveBeenCalledTimes(3)
    })

    it('AC-132.14 a drag with only text/plain is left alone', async () => {
      await renderPage()
      expect(drop([], ['text/plain'])).toEqual({ dragover: false, drop: false })
      await settle()
      expect(importBodies()).toEqual([])
    })

    it('AC-132.14 dragover and drop with Files are prevented while the crop is open', async () => {
      await open('land.png')
      await user.click(present('capture-tool-crop'))
      expect(screen.queryByTestId('capture-crop-bar'), 'the crop bar opens').not.toBeNull()
      expect(drop([file('red.png', 'C:\\drop\\red.png')])).toEqual({ dragover: true, drop: true })
      await settle()
      expect(importBodies()).toEqual([])
    })

    it('AC-132.14 a file with no path on disk is named not a file on disk and not sent', async () => {
      await renderPage()
      drop([file('clip.png'), file('ok.png', 'C:\\drop\\ok.png')])
      expect(await waitToast()).toBe('Imported 1 of 2. 1 failed: clip.png - not a file on disk')
      expect(importPosts()).toEqual(['C:\\drop\\ok.png'])
    })
  })

  describe('AC-132.15 IMPORT_TOAST', () => {
    it('AC-132.15 the drop toast names the text file; a second run replaces it; Dismiss removes it', async () => {
      await renderPage()
      drop([
        file('red.png', 'C:\\drop\\red.png'),
        file('notes.txt', 'C:\\drop\\notes.txt'),
        file('green.png', 'C:\\drop\\green.png'),
      ])
      expect(await waitToast()).toBe(`Imported 2 of 3. 1 failed: notes.txt - ${NOT_AN_IMAGE}`)
      drop([file('blue.png', 'C:\\drop\\blue.png')])
      await vi.waitFor(() => {
        expect(toastMessage()).toBe('Imported 1 of 1.')
      })
      expect(screen.queryAllByTestId('bulk-toast')).toHaveLength(1)
      await user.click(present('bulk-toast-dismiss'))
      expect(toastText()).toBeNull()
    })

    it('AC-132.15 the import route refusal names the file with its own text', async () => {
      importAnswer = () =>
        jsonResponse({ error: { code: 'InboxPathError', message: 'no file at that path', details: null } }, 422)
      await renderPage()
      drop([file('gone.png', 'C:\\drop\\gone.png')])
      expect(await waitToast()).toBe('Imported 0 of 1. 1 failed: gone.png - no file at that path')
    })

    it('AC-132.15 a rejected fetch through importCapture and apiFetch gives the fixed reason and no path', async () => {
      importAnswer = () => {
        throw new TypeError('Failed to fetch C:\\secret\\red.png')
      }
      await renderPage()
      drop([file('red.png', 'C:\\secret\\red.png')])
      const text = await waitToast()
      expect(text).toBe('Imported 0 of 1. 1 failed: red.png - the import could not be completed')
      expect(text).not.toContain('C:\\')
      expect(importPosts()).toEqual(['C:\\secret\\red.png'])
    })
  })

  describe('AC-132.16 PASTE_KEY', () => {
    it('AC-132.16 a paste on the body, on a clicked button and on a button reached with Tab is taken', async () => {
      await renderPage()
      expect(paste(document.body)).toBe(true)
      await vi.waitFor(() => {
        expect(pasteCaptureImage).toHaveBeenCalledTimes(1)
      })

      const toggle = present('capture-settings-toggle')
      await user.click(toggle)
      expect(document.activeElement).toBe(toggle)
      expect(paste(toggle)).toBe(true)
      await vi.waitFor(() => {
        expect(pasteCaptureImage).toHaveBeenCalledTimes(2)
      })

      act(() => {
        present('capture-import').focus()
      })
      await user.tab()
      expect(document.activeElement).toBe(toggle)
      await user.keyboard('{Enter}')
      expect(paste(document.activeElement as Element)).toBe(true)
      await vi.waitFor(() => {
        expect(pasteCaptureImage).toHaveBeenCalledTimes(3)
      })
    })

    it('AC-132.16 the inbox field, a textarea and a contenteditable keep their native paste', async () => {
      await renderPage()
      await user.click(present('capture-settings-toggle'))
      const inbox = present('capture-inbox-path')
      const textarea = document.createElement('textarea')
      const editable = document.createElement('div')
      editable.setAttribute('contenteditable', 'true')
      for (const extra of [textarea, editable]) {
        extra.setAttribute('data-s61-extra', '')
        document.body.append(extra)
      }
      for (const target of [inbox, textarea, editable]) {
        expect(paste(target), target.tagName).toBe(false)
      }
      await settle()
      expect(pasteCaptureImage).not.toHaveBeenCalled()
    })

    it('AC-132.16 after unmount a paste calls nothing', async () => {
      await renderPage()
      cleanup()
      expect(paste(document.body)).toBe(false)
      await settle()
      expect(pasteCaptureImage).not.toHaveBeenCalled()
    })
  })

  describe('AC-132.17 PASTE_MESSAGES', () => {
    const cases: Array<[PasteAnswer, string]> = [
      [{ kind: 'saved', name: '2026-11-10_09-30-15.png', registered: true }, 'Pasted as 2026-11-10_09-30-15.png.'],
      [
        { kind: 'saved', name: '2026-11-10_09-30-16.png', registered: false },
        'Pasted as 2026-11-10_09-30-16.png, but the library did not record it.',
      ],
      [{ kind: 'empty' }, 'Nothing to paste: the clipboard holds no image.'],
      [{ kind: 'blocked', reason: 'black' }, 'The pasted image is entirely black, so nothing was saved.'],
      [{ kind: 'blocked', reason: 'empty' }, 'The pasted image has no pixels, so nothing was saved.'],
      [{ kind: 'not-ready' }, "The inbox isn't ready yet, so nothing was saved. Try again in a moment."],
      [{ kind: 'failed' }, 'The pasted image could not be saved to the inbox.'],
    ]

    it('AC-132.17 each outcome shows its text, and only saved refetches the list', async () => {
      await renderPage()
      for (const [answer, text] of cases) {
        pasteCaptureImage.mockResolvedValueOnce(answer)
        const before = listGets()
        paste(document.body)
        await vi.waitFor(() => {
          expect(toastText(), answer.kind).not.toBeNull()
          expect(toastMessage(), answer.kind).toBe(text)
        })
        await settle()
        if (answer.kind === 'saved') {
          expect(listGets() - before, text).toBeGreaterThanOrEqual(1)
        } else {
          expect(listGets() - before, text).toBe(0)
        }
      }
    })

    it('AC-132.17 busy shows no toast and a rejected IPC shows the failed text', async () => {
      await renderPage()
      pasteCaptureImage.mockResolvedValueOnce({ kind: 'busy' })
      paste(document.body)
      await vi.waitFor(() => {
        expect(pasteCaptureImage).toHaveBeenCalledTimes(1)
      })
      await settle()
      expect(toastText()).toBeNull()
      pasteCaptureImage.mockRejectedValueOnce(new Error('ipc gone C:\\secret'))
      paste(document.body)
      expect(await waitToast()).toBe('The pasted image could not be saved to the inbox.')
    })
  })

  describe('AC-132.18 IMPORT_GATE', () => {
    it('AC-132.18 with the crop open the button is disabled with the reason, and a drop and a paste call nothing', async () => {
      await open('land.png')
      await user.click(present('capture-tool-crop'))
      expect(screen.queryByTestId('capture-crop-bar'), 'the crop bar opens').not.toBeNull()
      const button = present<HTMLButtonElement>('capture-import')
      expect(button.disabled).toBe(true)
      expect(button.getAttribute('title')).toBe(CROP_REASON)
      drop([file('red.png', 'C:\\drop\\red.png')])
      paste(document.body)
      await settle()
      expect(importBodies()).toEqual([])
      expect(pasteCaptureImage).not.toHaveBeenCalled()
      expect(toastText()).toBeNull()
    })

    it('AC-132.18 with a delete confirm open, a drop and a paste call nothing', async () => {
      await open('land.png')
      await user.click(present('capture-delete'))
      expect(screen.queryByTestId('capture-confirm-strip'), 'the confirm opens').not.toBeNull()
      drop([file('red.png', 'C:\\drop\\red.png')])
      paste(document.body)
      await settle()
      expect(importBodies()).toEqual([])
      expect(pasteCaptureImage).not.toHaveBeenCalled()
    })

    it('AC-132.18 while an import runs the button is busy and a second drop sends nothing', async () => {
      importHold = true
      await renderPage()
      drop([file('red.png', 'C:\\drop\\red.png')])
      await vi.waitFor(() => {
        expect(importPosts()).toEqual(['C:\\drop\\red.png'])
      })
      expect(present('capture-import').getAttribute('aria-busy')).toBe('true')
      drop([file('green.png', 'C:\\drop\\green.png')])
      paste(document.body)
      await settle()
      expect(importPosts()).toEqual(['C:\\drop\\red.png'])
      expect(pasteCaptureImage).not.toHaveBeenCalled()
      importHold = false
      for (const release of importRelease) {
        release()
      }
      expect(await waitToast()).toBe('Imported 1 of 1.')
      expect(present('capture-import').getAttribute('aria-busy')).not.toBe('true')
    })

    it('AC-132.18 unsaved marks do not block a drop, and the marks are still there after it', async () => {
      const surface = await open('land.png')
      await user.click(present('capture-tool-box'))
      await drag(surface, [
        [60, 60],
        [120, 120],
      ])
      expect(document.querySelectorAll('[data-testid="capture-annotation"]')).toHaveLength(1)
      drop([file('red.png', 'C:\\drop\\red.png')])
      expect(await waitToast()).toBe('Imported 1 of 1.')
      expect(importPosts()).toEqual(['C:\\drop\\red.png'])
      expect(document.querySelectorAll('[data-testid="capture-annotation"]')).toHaveLength(1)
    })
  })

  describe('AC-132.19 SELECTION_EFFECTS', () => {
    it('AC-132.19 on an empty inbox the first import becomes selected after the refetch', async () => {
      items = []
      await renderPage()
      expect(screen.queryByTestId('capture-shot-info')?.textContent ?? '').not.toContain('red.png')
      drop([file('red.png', 'C:\\drop\\red.png')])
      expect(await waitToast()).toBe('Imported 1 of 1.')
      await vi.waitFor(() => {
        expect(screen.getAllByTestId('capture-filmstrip-item')).toHaveLength(1)
        expect(present('capture-shot-info').textContent).toContain('red.png')
      })
    })

    it('AC-132.19 an import leaves the selection, the marks, the range and the notice as they were', async () => {
      const surface = await open('spaced.png')
      // A range: shift-click the thumb after the selected one.
      const thumbs = (): HTMLElement[] => screen.getAllByTestId('capture-filmstrip-item')
      fireEvent.click(thumbs()[2] as HTMLElement, { shiftKey: true })
      const inRange = (): boolean[] => thumbs().map((thumb) => thumb.getAttribute('data-in-range') === 'true')
      await vi.waitFor(() => {
        expect(inRange().filter(Boolean).length).toBeGreaterThan(0)
      })
      // Unsaved marks.
      await user.click(present('capture-tool-box'))
      await drag(surface, [
        [60, 60],
        [120, 120],
      ])
      expect(document.querySelectorAll('[data-testid="capture-annotation"]')).toHaveLength(1)
      // A notice keyed to the selected shot.
      fireEvent.contextMenu(thumbs()[0] as HTMLElement, { clientX: 120, clientY: 80 })
      await user.click(present('capture-filmstrip-menu-copy-path'))
      await vi.waitFor(() => {
        expect(present('capture-status').textContent).toBe('Copied the path of land.png.')
      })
      const rangeBefore = inRange()
      const currentBefore = thumbs().map((thumb) => thumb.getAttribute('aria-current'))
      // The shift-click moves the selection to the clicked thumb, so the selection is read here.
      const infoBefore = present('capture-shot-info').textContent ?? ''
      expect(infoBefore).toMatch(/\.png/)

      drop([file('red.png', 'C:\\drop\\red.png')])
      expect(await waitToast()).toBe('Imported 1 of 1.')
      await vi.waitFor(() => {
        expect(thumbs()).toHaveLength(4)
      })
      expect(present('capture-shot-info').textContent).toBe(infoBefore)
      expect(document.querySelectorAll('[data-testid="capture-annotation"]')).toHaveLength(1)
      expect(inRange().slice(0, 3)).toEqual(rangeBefore)
      expect(thumbs().map((thumb) => thumb.getAttribute('aria-current')).slice(0, 3)).toEqual(currentBefore)
      expect(present('capture-status').textContent).toBe('Copied the path of land.png.')
    })
  })
})
