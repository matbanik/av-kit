/** @vitest-environment jsdom */

import { act, cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClientProvider } from '@tanstack/react-query'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { CapturePage } from '../../src/renderer/src/features/capture/CapturePage'
import { queryClient } from '../../src/renderer/src/lib/query-client'

// Session 38 (MEU-88/89): the thumbnail menu and range selection on the real CapturePage.
// It renders with the app's query client because the page's commands invalidate that client
// (capture-commands.ts), so a DELETE refetches the catalog as it does in the app.

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

function shot(id: string, name: string, createdAt: string): Shot {
  return {
    id,
    original_path: `C:/shots/${name}`,
    annotated_path: null,
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

// Filmstrip order is newest first (sortFilmstrip): A, B.
const SHOT_A = shot('shot-a', 'a.png', '2026-08-27T12:00:00Z')
const SHOT_B = shot('shot-b', 'b.png', '2026-08-27T11:00:00Z')
// An id with a reserved character: COPY_IMAGE_SOURCE must percent-encode it (RULE-2).
const SHOT_SLASH = shot('dir/shot-s', 's.png', '2026-08-27T09:00:00Z')

const PNG_BYTES = Uint8Array.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0, 0, 0, 13, 0x49, 0x48, 0x44, 0x52])

type FetchCall = { url: string; method: string }

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

describe('MEU-88 capture filmstrip thumbnail menu', () => {
  let user: ReturnType<typeof userEvent.setup>
  let items: Shot[]
  const calls: FetchCall[] = []
  let deleteStatus: Record<string, number>
  let imageStatus: Record<string, number>
  let writeClipboardText: ReturnType<typeof vi.fn>
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
      writeClipboardText: writeClipboardText as unknown as (text: string) => Promise<void>,
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
    deleteStatus = {}
    imageStatus = {}
    writeClipboardText = vi.fn(async (_text: string) => undefined)
    writeClipboardImage = vi.fn(async (_png: Uint8Array) => undefined)
    queryClient.setQueryData(['captures'], { items: [...items], pendingInteractive: false })
    queryClient.setQueryData(['settings', 'capture'], {
      inbox_dir: 'C:/Pictures/av-kit',
      hotkey: 'F2',
      copy_to_clipboard: false,
      close_to_tray: true,
    })
    URL.createObjectURL = vi.fn(() => 'blob:capture-shot')
    URL.revokeObjectURL = vi.fn()
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = hrefOf(input)
      const method = (init?.method ?? 'GET').toUpperCase()
      calls.push({ url, method })
      const path = url.split('?')[0] ?? url
      if (path.includes('/settings/capture')) {
        return jsonResponse({ inbox_dir: 'C:/Pictures/av-kit', hotkey: 'F2', copy_to_clipboard: false, close_to_tray: true })
      }
      if (path.includes('/captures/requests')) {
        return jsonResponse({ items: [] })
      }
      const image = path.match(/\/captures\/(.+)\/image$/)
      if (image) {
        const id = decodeURIComponent(image[1] as string)
        const status = imageStatus[id]
        if (status !== undefined) {
          return errorResponse(status, 'not found')
        }
        return new Response(PNG_BYTES, { status: 200, headers: { 'Content-Type': 'image/png' } })
      }
      if (path.includes('/annotate')) {
        return jsonResponse({ ok: true })
      }
      const one = path.match(/\/captures\/([^/]+)$/)
      if (one && method === 'DELETE') {
        const id = decodeURIComponent(one[1] as string)
        const status = deleteStatus[id]
        if (status !== undefined) {
          return errorResponse(status, `disk refused ${id}`)
        }
        items = items.filter((item) => item.id !== id)
        return new Response(null, { status: 204 })
      }
      if (one && method === 'GET') {
        const id = decodeURIComponent(one[1] as string)
        const row = items.find((item) => item.id === id) ?? SHOT_A
        return jsonResponse({ ...row, annotations: [], backup_path: null })
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
  })

  async function renderPage(): Promise<void> {
    queryClient.setQueryData(['captures'], { items: [...items], pendingInteractive: false })
    mockApi()
    render(createElement(QueryClientProvider, { client: queryClient }, createElement(CapturePage)))
    await vi.waitFor(() => {
      expect(screen.getAllByTestId('capture-filmstrip-item')).toHaveLength(items.length)
    })
  }

  function thumbs(): HTMLElement[] {
    return screen.getAllByTestId('capture-filmstrip-item')
  }

  /** Render, select the newest shot with a click, and wait until its overlay is ready. */
  async function openFirst(): Promise<HTMLElement> {
    await renderPage()
    await user.click(thumbs()[0] as HTMLElement)
    await vi.waitFor(() => {
      expect(screen.getByTestId('capture-draw-surface').getAttribute('data-overlay-ready')).toBe('true')
    })
    const surface = screen.getByTestId('capture-draw-surface')
    bindRect(surface, { left: 0, top: 0, width: 200, height: 200 })
    return surface
  }

  async function drawArrow(surface: HTMLElement): Promise<void> {
    const pointer = (type: string, x: number, y: number) =>
      surface.dispatchEvent(
        new PointerEvent(type, { bubbles: true, cancelable: true, clientX: x, clientY: y, pointerId: 1, pointerType: 'mouse', isPrimary: true }),
      )
    await act(async () => {
      pointer('pointerdown', 25, 25)
      pointer('pointermove', 150, 150)
      pointer('pointerup', 150, 150)
    })
    expect(document.querySelectorAll('[data-annotation-type="arrow"]')).toHaveLength(1)
  }

  function menu(): HTMLElement | null {
    return screen.queryByTestId('capture-filmstrip-menu')
  }

  /** Right-click a thumb at a pointer position and return the menu (asserted, so Red is an assertion). */
  function rightClick(thumb: HTMLElement, clientX = 120, clientY = 80): HTMLElement {
    fireEvent.contextMenu(thumb, { clientX, clientY })
    const opened = menu()
    expect(opened).not.toBeNull()
    return opened as HTMLElement
  }

  function menuItem(testid: string): HTMLElement {
    const found = screen.queryByTestId(testid)
    expect(found).not.toBeNull()
    return found as HTMLElement
  }

  function deletes(): string[] {
    return calls.filter((call) => call.method === 'DELETE').map((call) => call.url)
  }

  function status(): string {
    return screen.getByTestId('capture-status').textContent ?? ''
  }

  it('AC-88.1 right-click on a non-selected thumb opens Shot actions at the pointer without changing the selection', async () => {
    await openFirst()
    const opened = rightClick(thumbs()[1] as HTMLElement, 120, 80)
    expect(opened.getAttribute('role')).toBe('menu')
    expect(opened.getAttribute('aria-label')).toBe('Shot actions')
    const entries = within(opened).getAllByRole('menuitem')
    expect(entries.map((entry) => entry.textContent)).toEqual(['Copy full path', 'Copy image', 'Delete'])
    expect(entries.map((entry) => entry.getAttribute('data-testid'))).toEqual([
      'capture-filmstrip-menu-copy-path',
      'capture-filmstrip-menu-copy-image',
      'capture-filmstrip-menu-delete',
    ])
    await vi.waitFor(() => {
      expect(document.activeElement).toBe(entries[0])
    })
    expect(opened.style.position).toBe('fixed')
    expect(opened.style.left).toBe('120px')
    expect(opened.style.top).toBe('80px')
    expect(thumbs()[0]?.getAttribute('aria-current')).toBe('true')
    expect(thumbs()[1]?.getAttribute('aria-current')).toBeNull()
  })

  it('AC-88.1 no menu opens while the confirm strip is open, and opening a confirm closes an open menu', async () => {
    await openFirst()
    rightClick(thumbs()[1] as HTMLElement)
    // A keyboard-free click: no pointer-down, so only MENU_LOCK can close the menu.
    act(() => {
      ;(screen.getByTestId('capture-delete') as HTMLButtonElement).click()
    })
    expect(screen.queryByTestId('capture-confirm-strip')).not.toBeNull()
    expect(menu()).toBeNull()
    fireEvent.contextMenu(thumbs()[1] as HTMLElement, { clientX: 120, clientY: 80 })
    expect(menu()).toBeNull()
  })

  it('AC-88.2 ContextMenu and Shift+F10 open the menu at the thumb; arrows wrap, Home/End jump, Escape returns focus', async () => {
    await openFirst()
    const thumb = thumbs()[1] as HTMLElement
    bindRect(thumb, { left: 40, top: 44, width: 200, height: 46 })
    act(() => {
      thumb.focus()
    })
    fireEvent.keyDown(thumb, { key: 'F10', shiftKey: true })
    const opened = menu()
    expect(opened).not.toBeNull()
    expect(opened?.style.left).toBe('40px')
    expect(opened?.style.top).toBe('90px')
    const entries = within(opened as HTMLElement).getAllByRole('menuitem')
    await vi.waitFor(() => {
      expect(document.activeElement).toBe(entries[0])
    })
    await user.keyboard('{ArrowDown}')
    expect(document.activeElement).toBe(entries[1])
    await user.keyboard('{ArrowDown}{ArrowDown}')
    expect(document.activeElement).toBe(entries[0])
    await user.keyboard('{ArrowUp}')
    expect(document.activeElement).toBe(entries[2])
    await user.keyboard('{Home}')
    expect(document.activeElement).toBe(entries[0])
    await user.keyboard('{End}')
    expect(document.activeElement).toBe(entries[2])
    await user.keyboard('{Escape}')
    expect(menu()).toBeNull()
    expect(document.activeElement).toBe(thumb)

    fireEvent.keyDown(thumb, { key: 'ContextMenu' })
    expect(menu()).not.toBeNull()
    await user.keyboard('{Tab}')
    expect(menu()).toBeNull()

    // A contextmenu at 0,0 (the keyboard path on some hosts) anchors to the thumb as well.
    rightClick(thumb, 0, 0)
    expect(menu()?.style.left).toBe('40px')
    expect(menu()?.style.top).toBe('90px')
    await user.click(screen.getByTestId('capture-status'))
    expect(menu()).toBeNull()
  })

  it('AC-88.2 F10 without Shift and a letter key open nothing; a second open signal leaves one menu', async () => {
    await openFirst()
    const thumb = thumbs()[1] as HTMLElement
    fireEvent.keyDown(thumb, { key: 'F10' })
    fireEvent.keyDown(thumb, { key: 'a' })
    expect(menu()).toBeNull()
    fireEvent.keyDown(thumb, { key: 'ContextMenu' })
    expect(menu()).not.toBeNull()
    fireEvent.contextMenu(thumb, { clientX: 0, clientY: 0 })
    expect(screen.queryAllByTestId('capture-filmstrip-menu')).toHaveLength(1)
  })

  it('AC-88.3 Copy full path on a non-selected shot copies that shot path and reports it in capture-status', async () => {
    await openFirst()
    rightClick(thumbs()[1] as HTMLElement)
    await user.click(menuItem('capture-filmstrip-menu-copy-path'))
    expect(writeClipboardText).toHaveBeenCalledTimes(1)
    expect(writeClipboardText).toHaveBeenCalledWith('C:/shots/b.png')
    expect(menu()).toBeNull()
    await vi.waitFor(() => {
      expect(status()).toBe('Copied the path of b.png.')
    })
    expect(thumbs()[0]?.getAttribute('aria-current')).toBe('true')
  })

  it('AC-88.3 a rejecting writeClipboardText reports the failure and no success notice', async () => {
    writeClipboardText = vi.fn(async (_text: string) => {
      throw new Error('clipboard busy')
    })
    await openFirst()
    rightClick(thumbs()[1] as HTMLElement)
    await user.click(menuItem('capture-filmstrip-menu-copy-path'))
    await vi.waitFor(() => {
      expect(status()).toBe('Could not copy b.png: clipboard busy')
    })
    expect(status()).not.toContain('Copied the path')
  })

  it('AC-88.5 Copy image fetches the percent-encoded original and sends PNG bytes to writeClipboardImage', async () => {
    items = [SHOT_A, SHOT_B, SHOT_SLASH]
    await openFirst()
    rightClick(thumbs()[2] as HTMLElement)
    await user.click(menuItem('capture-filmstrip-menu-copy-image'))
    await vi.waitFor(() => {
      expect(writeClipboardImage).toHaveBeenCalledTimes(1)
    })
    expect(calls.some((call) => call.method === 'GET' && call.url.includes('/captures/dir%2Fshot-s/image?variant=original'))).toBe(true)
    const png = writeClipboardImage?.mock.calls[0]?.[0] as Uint8Array
    expect(Object.prototype.toString.call(png)).toBe('[object Uint8Array]')
    expect(Array.from(png.slice(0, 8))).toEqual([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a])
    expect(menu()).toBeNull()
    await vi.waitFor(() => {
      expect(status()).toBe('Copied s.png as an image.')
    })
  })

  it('AC-88.5 an image GET 404 reports the load failure and never writes the clipboard', async () => {
    imageStatus = { 'shot-b': 404 }
    await openFirst()
    rightClick(thumbs()[1] as HTMLElement)
    await user.click(menuItem('capture-filmstrip-menu-copy-image'))
    await vi.waitFor(() => {
      expect(status()).toBe('Could not copy b.png: the image could not be loaded')
    })
    expect(writeClipboardImage).not.toHaveBeenCalled()
  })

  it('AC-88.5 without window.api.writeClipboardImage Copy image reports it is unavailable and fetches nothing', async () => {
    writeClipboardImage = undefined
    await openFirst()
    rightClick(thumbs()[1] as HTMLElement)
    await user.click(menuItem('capture-filmstrip-menu-copy-image'))
    await vi.waitFor(() => {
      expect(status()).toBe('Could not copy b.png: copying images is not available in this window')
    })
    expect(calls.some((call) => call.url.includes('/captures/shot-b/image?variant=original'))).toBe(false)
  })

  it('AC-88.9 menu Delete on the selected shot reuses the confirm and the selection falls to the newest shot', async () => {
    await openFirst()
    rightClick(thumbs()[0] as HTMLElement)
    await user.click(menuItem('capture-filmstrip-menu-delete'))
    expect(screen.getByTestId('capture-confirm-strip').textContent).toContain('Delete this capture and its files from disk?')
    expect(screen.getByTestId('capture-delete-confirm').textContent).toBe('Delete capture')
    await user.click(screen.getByTestId('capture-delete-confirm'))
    await vi.waitFor(() => {
      expect(thumbs()).toHaveLength(1)
    })
    expect(deletes()).toHaveLength(1)
    expect(deletes()[0]).toMatch(/\/captures\/shot-a$/)
    await vi.waitFor(() => {
      expect(thumbs()[0]?.getAttribute('aria-current')).toBe('true')
    })
  })

  it('AC-88.9 Cancel sends no DELETE and a following toolbar Delete targets the selected shot', async () => {
    await openFirst()
    rightClick(thumbs()[1] as HTMLElement)
    await user.click(menuItem('capture-filmstrip-menu-delete'))
    await user.click(screen.getByTestId('capture-delete-confirm-cancel'))
    expect(deletes()).toHaveLength(0)
    await user.click(screen.getByTestId('capture-delete'))
    expect(screen.getByTestId('capture-confirm-strip').textContent).toContain('Delete this capture and its files from disk?')
    await user.click(screen.getByTestId('capture-delete-confirm'))
    await vi.waitFor(() => {
      expect(deletes()).toHaveLength(1)
    })
    expect(deletes()[0]).toMatch(/\/captures\/shot-a$/)
  })

  it('AC-88.10 menu Delete on a non-selected shot names it, deletes only it, and keeps the editor shot, marks and dirty state', async () => {
    const surface = await openFirst()
    await drawArrow(surface)
    expect(thumbs()[0]?.getAttribute('data-dirty')).toBe('true')
    rightClick(thumbs()[1] as HTMLElement)
    await user.click(menuItem('capture-filmstrip-menu-delete'))
    expect(screen.getByTestId('capture-confirm-strip').textContent).toContain('Delete "b.png" and its files from disk?')
    expect(screen.getByTestId('capture-delete-confirm').textContent).toBe('Delete capture')
    await user.click(screen.getByTestId('capture-delete-confirm'))
    await vi.waitFor(() => {
      expect(thumbs()).toHaveLength(1)
    })
    expect(deletes()).toHaveLength(1)
    expect(deletes()[0]).toMatch(/\/captures\/shot-b$/)
    expect(deletes().some((url) => /\/captures\/shot-a$/.test(url))).toBe(false)
    expect(screen.queryByTestId('capture-dirty-confirm')).toBeNull()
    expect(thumbs()[0]?.getAttribute('aria-current')).toBe('true')
    expect(thumbs()[0]?.getAttribute('data-dirty')).toBe('true')
    expect(document.querySelectorAll('[data-annotation-type="arrow"]')).toHaveLength(1)
  })

  describe('MEU-89 capture filmstrip range selection', () => {
    // Filmstrip order with these: A, B, C, (SLASH,) D.
    const SHOT_C = shot('shot-c', 'c.png', '2026-08-27T10:00:00Z')
    const SHOT_D = shot('shot-d', 'd.png', '2026-08-27T08:00:00Z')

    let inFlight: number
    let maxInFlight: number

    // Each DELETE is held for a few milliseconds, so overlapping requests would show here.
    beforeEach(() => {
      inFlight = 0
      maxInFlight = 0
      const inner = window.fetch
      const tracked = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        if ((init?.method ?? 'GET').toUpperCase() !== 'DELETE') {
          return inner(input, init)
        }
        inFlight += 1
        maxInFlight = Math.max(maxInFlight, inFlight)
        try {
          await new Promise((resolve) => setTimeout(resolve, 5))
          return await inner(input, init)
        } finally {
          inFlight -= 1
        }
      })
      vi.stubGlobal('fetch', tracked)
      window.fetch = tracked as typeof window.fetch
    })

    function shiftClick(thumb: HTMLElement): void {
      fireEvent.click(thumb, { shiftKey: true })
    }

    function inRange(): boolean[] {
      return thumbs().map((thumb) => thumb.getAttribute('data-in-range') === 'true')
    }

    function currentIndex(): number {
      return thumbs().findIndex((thumb) => thumb.getAttribute('aria-current') === 'true')
    }

    function names(): string[] {
      return screen.getAllByTestId('capture-filmstrip-name').map((name) => name.textContent ?? '')
    }

    async function openBatchConfirm(member: number): Promise<void> {
      rightClick(thumbs()[member] as HTMLElement)
      await user.click(menuItem('capture-filmstrip-menu-delete-batch'))
    }

    it('AC-89.2 click A then Shift+click C marks A, B, C, moves the editor to C and shows the count', async () => {
      items = [SHOT_A, SHOT_B, SHOT_C, SHOT_D]
      await openFirst()
      shiftClick(thumbs()[2] as HTMLElement)
      await vi.waitFor(() => {
        expect(currentIndex()).toBe(2)
      })
      expect(inRange()).toEqual([true, true, true, false])
      for (const index of [0, 1, 2]) {
        expect(thumbs()[index]?.className).toContain('ring-accent/40')
        expect(thumbs()[index]?.textContent).toContain(', selected')
      }
      expect(thumbs()[3]?.textContent).not.toContain(', selected')
      await vi.waitFor(() => {
        expect(status()).toBe('3 shots selected')
      })

      // The anchor stays A.
      shiftClick(thumbs()[1] as HTMLElement)
      await vi.waitFor(() => {
        expect(currentIndex()).toBe(1)
      })
      expect(inRange()).toEqual([true, true, false, false])
      await vi.waitFor(() => {
        expect(status()).toBe('2 shots selected')
      })

      // A plain click clears every range mark and the count.
      await user.click(thumbs()[3] as HTMLElement)
      await vi.waitFor(() => {
        expect(currentIndex()).toBe(3)
      })
      expect(inRange()).toEqual([false, false, false, false])
      expect(thumbs().some((thumb) => thumb.textContent?.includes(', selected'))).toBe(false)
      expect(status()).not.toContain('shots selected')
    })

    it('AC-89.2 with no click the auto-selected newest shot anchors the range; Shift+click on the anchor marks nothing', async () => {
      items = [SHOT_A, SHOT_B, SHOT_C, SHOT_D]
      await renderPage()
      await vi.waitFor(() => {
        expect(currentIndex()).toBe(0)
      })
      shiftClick(thumbs()[0] as HTMLElement)
      expect(inRange()).toEqual([false, false, false, false])
      expect(status()).not.toContain('shots selected')

      shiftClick(thumbs()[2] as HTMLElement)
      await vi.waitFor(() => {
        expect(inRange()).toEqual([true, true, true, false])
      })
      expect(currentIndex()).toBe(2)
      await vi.waitFor(() => {
        expect(status()).toBe('3 shots selected')
      })
    })

    it("AC-89.2 after the anchor's shot is deleted the next Shift+click anchors on the editor's current shot", async () => {
      items = [SHOT_A, SHOT_B, SHOT_C, SHOT_D]
      await openFirst()
      await user.click(screen.getByTestId('capture-delete'))
      await user.click(screen.getByTestId('capture-delete-confirm'))
      await vi.waitFor(() => {
        expect(names()).toEqual(['b.png', 'c.png', 'd.png'])
      })
      await vi.waitFor(() => {
        expect(currentIndex()).toBe(0)
      })
      shiftClick(thumbs()[2] as HTMLElement)
      await vi.waitFor(() => {
        expect(inRange()).toEqual([true, true, true])
      })
      expect(currentIndex()).toBe(2)
    })

    it('AC-89.3 a Shift+click with unsaved marks asks first; Cancel keeps the shot, marks and range, Confirm applies them', async () => {
      items = [SHOT_A, SHOT_B, SHOT_C, SHOT_D]
      await openFirst()
      shiftClick(thumbs()[1] as HTMLElement)
      await vi.waitFor(() => {
        expect(currentIndex()).toBe(1)
      })
      expect(inRange()).toEqual([true, true, false, false])
      await vi.waitFor(() => {
        expect(screen.getByTestId('capture-draw-surface').getAttribute('data-overlay-ready')).toBe('true')
      })
      const surface = screen.getByTestId('capture-draw-surface')
      bindRect(surface, { left: 0, top: 0, width: 200, height: 200 })
      await drawArrow(surface)
      expect(thumbs()[1]?.getAttribute('data-dirty')).toBe('true')

      shiftClick(thumbs()[2] as HTMLElement)
      expect(screen.queryByTestId('capture-dirty-confirm')).not.toBeNull()
      await user.click(screen.getByTestId('capture-dirty-confirm-cancel'))
      expect(currentIndex()).toBe(1)
      expect(inRange()).toEqual([true, true, false, false])
      expect(document.querySelectorAll('[data-annotation-type="arrow"]')).toHaveLength(1)

      shiftClick(thumbs()[2] as HTMLElement)
      await user.click(screen.getByTestId('capture-dirty-confirm'))
      await vi.waitFor(() => {
        expect(currentIndex()).toBe(2)
      })
      expect(inRange()).toEqual([true, true, true, false])
      await vi.waitFor(() => {
        expect(status()).toBe('3 shots selected')
      })
    })

    it('AC-89.4 right-clicking a range member offers only Delete 3 shots; a shot outside the range gets the single menu', async () => {
      items = [SHOT_A, SHOT_B, SHOT_C, SHOT_D]
      await openFirst()
      shiftClick(thumbs()[2] as HTMLElement)
      await vi.waitFor(() => {
        expect(inRange()).toEqual([true, true, true, false])
      })

      const batch = rightClick(thumbs()[1] as HTMLElement)
      const entries = within(batch).getAllByRole('menuitem')
      expect(entries.map((entry) => entry.textContent)).toEqual(['Delete 3 shots'])
      expect(entries.map((entry) => entry.getAttribute('data-testid'))).toEqual(['capture-filmstrip-menu-delete-batch'])
      expect(screen.queryByTestId('capture-filmstrip-menu-copy-path')).toBeNull()
      expect(screen.queryByTestId('capture-filmstrip-menu-copy-image')).toBeNull()
      await user.keyboard('{Escape}')
      expect(menu()).toBeNull()

      const single = rightClick(thumbs()[3] as HTMLElement)
      expect(within(single).getAllByRole('menuitem').map((entry) => entry.textContent)).toEqual([
        'Copy full path',
        'Copy image',
        'Delete',
      ])
      expect(inRange()).toEqual([true, true, true, false])
      expect(currentIndex()).toBe(2)
    })

    it('AC-89.5 the batch confirm names the count; Cancel sends nothing; accept deletes in order, one at a time, encoded', async () => {
      items = [SHOT_A, SHOT_B, SHOT_SLASH, SHOT_D]
      await openFirst()
      shiftClick(thumbs()[2] as HTMLElement)
      await vi.waitFor(() => {
        expect(inRange()).toEqual([true, true, true, false])
      })

      await openBatchConfirm(1)
      expect(screen.getByTestId('capture-confirm-strip').textContent).toContain('Delete 3 captures and their files from disk?')
      expect(screen.getByTestId('capture-delete-confirm').textContent).toBe('Delete 3 captures')
      await user.click(screen.getByTestId('capture-delete-confirm-cancel'))
      expect(deletes()).toHaveLength(0)
      expect(inRange()).toEqual([true, true, true, false])

      await openBatchConfirm(0)
      await user.click(screen.getByTestId('capture-delete-confirm'))
      await vi.waitFor(() => {
        expect(names()).toEqual(['d.png'])
      })
      expect(deletes()).toHaveLength(3)
      expect(deletes()[0]).toMatch(/\/captures\/shot-a$/)
      expect(deletes()[1]).toMatch(/\/captures\/shot-b$/)
      expect(deletes()[2]).toMatch(/\/captures\/dir%2Fshot-s$/)
      expect(maxInFlight).toBe(1)
      expect(inRange()).toEqual([false])
      await vi.waitFor(() => {
        expect(currentIndex()).toBe(0)
      })
      await vi.waitFor(() => {
        expect(status()).toBe('Deleted 3 shots.')
      })
    })

    it('AC-89.5 deleting every shot still reports the result once nothing is left to select', async () => {
      items = [SHOT_A, SHOT_B]
      await openFirst()
      shiftClick(thumbs()[1] as HTMLElement)
      await vi.waitFor(() => {
        expect(inRange()).toEqual([true, true])
      })
      await openBatchConfirm(0)
      await user.click(screen.getByTestId('capture-delete-confirm'))
      await vi.waitFor(() => {
        expect(screen.queryAllByTestId('capture-filmstrip-name')).toHaveLength(0)
      })
      expect(deletes()).toHaveLength(2)
      await vi.waitFor(() => {
        expect(status()).toBe('Deleted 2 shots.')
      })
    })

    it('AC-89.6 a failing middle DELETE does not stop the batch; the failed shot stays and is named', async () => {
      items = [SHOT_A, SHOT_B, SHOT_C, SHOT_D]
      deleteStatus = { 'shot-b': 500 }
      await openFirst()
      shiftClick(thumbs()[2] as HTMLElement)
      await vi.waitFor(() => {
        expect(inRange()).toEqual([true, true, true, false])
      })
      await openBatchConfirm(0)
      await user.click(screen.getByTestId('capture-delete-confirm'))
      await vi.waitFor(() => {
        expect(names()).toEqual(['b.png', 'd.png'])
      })
      expect(deletes()).toHaveLength(3)
      expect(deletes()[0]).toMatch(/\/captures\/shot-a$/)
      expect(deletes()[1]).toMatch(/\/captures\/shot-b$/)
      expect(deletes()[2]).toMatch(/\/captures\/shot-c$/)
      await vi.waitFor(() => {
        expect(status()).toBe('Deleted 2 of 3 shots. Could not delete b.png: disk refused shot-b')
      })
      expect(inRange()).toEqual([false, false])
      // NEXT_SELECTION: the editor's shot went, so the first survivor in filmstrip order takes it.
      expect(currentIndex()).toBe(0)
    })

    it('AC-89.6 with two failures both shots are named in order', async () => {
      items = [SHOT_A, SHOT_B, SHOT_C, SHOT_D]
      deleteStatus = { 'shot-b': 500, 'shot-c': 500 }
      await openFirst()
      shiftClick(thumbs()[2] as HTMLElement)
      await vi.waitFor(() => {
        expect(inRange()).toEqual([true, true, true, false])
      })
      await openBatchConfirm(2)
      await user.click(screen.getByTestId('capture-delete-confirm'))
      await vi.waitFor(() => {
        expect(status()).toBe(
          'Deleted 1 of 3 shots. Could not delete b.png: disk refused shot-b; c.png: disk refused shot-c',
        )
      })
      expect(deletes()).toHaveLength(3)
      expect(names()).toEqual(['b.png', 'c.png', 'd.png'])
      expect(inRange()).toEqual([false, false, false])
    })

    // D-25: a checkbox left of each thumb toggles that shot in the selection set.

    /** Every row's checkbox, asserted one per thumb so a missing box is an assertion failure. */
    function checks(): HTMLInputElement[] {
      const boxes = screen.queryAllByTestId('capture-filmstrip-check') as HTMLInputElement[]
      expect(boxes).toHaveLength(thumbs().length)
      return boxes
    }

    function ticked(): boolean[] {
      return checks().map((box) => box.checked)
    }

    function check(index: number): HTMLInputElement {
      return checks()[index] as HTMLInputElement
    }

    it('AC-89.11 a Select checkbox precedes each thumb; ticking B and D selects both and leaves the editor on A', async () => {
      items = [SHOT_A, SHOT_B, SHOT_C, SHOT_D]
      await openFirst()
      const boxes = checks()
      const full = ['a.png', 'b.png', 'c.png', 'd.png']
      boxes.forEach((box, index) => {
        const thumb = thumbs()[index] as HTMLElement
        expect(box.type).toBe('checkbox')
        expect(box.getAttribute('aria-label')).toBe(`Select ${full[index]}`)
        expect(thumb.contains(box)).toBe(false)
        expect(box.compareDocumentPosition(thumb) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
      })
      expect(thumbs().some((thumb) => thumb.textContent?.includes('Select'))).toBe(false)
      expect(ticked()).toEqual([false, false, false, false])

      // One tick shows the tick, but membership counts only above one shot.
      await user.click(check(1))
      expect(ticked()).toEqual([false, true, false, false])
      expect(inRange()).toEqual([false, false, false, false])
      expect(status()).not.toContain('shots selected')
      expect(currentIndex()).toBe(0)

      await user.click(check(3))
      expect(ticked()).toEqual([false, true, false, true])
      expect(inRange()).toEqual([false, true, false, true])
      expect(thumbs()[1]?.textContent).toContain(', selected')
      expect(thumbs()[3]?.textContent).toContain(', selected')
      expect(currentIndex()).toBe(0)
      await vi.waitFor(() => {
        expect(status()).toBe('2 shots selected')
      })

      // Ticking B again unticks it.
      await user.click(check(1))
      expect(ticked()).toEqual([false, false, false, true])
      expect(inRange()).toEqual([false, false, false, false])

      // A plain thumb click clears every tick.
      await user.click(check(1))
      expect(ticked()).toEqual([false, true, false, true])
      await user.click(thumbs()[2] as HTMLElement)
      await vi.waitFor(() => {
        expect(currentIndex()).toBe(2)
      })
      expect(ticked()).toEqual([false, false, false, false])
      expect(inRange()).toEqual([false, false, false, false])
      expect(status()).not.toContain('shots selected')
    })

    it('AC-89.12 ticking with unsaved marks asks nothing and keeps the shot; Shift+click on a box ticks the range', async () => {
      items = [SHOT_A, SHOT_B, SHOT_C, SHOT_D]
      const surface = await openFirst()
      await drawArrow(surface)
      expect(thumbs()[0]?.getAttribute('data-dirty')).toBe('true')

      await user.click(check(1))
      expect(screen.queryByTestId('capture-dirty-confirm')).toBeNull()
      expect(ticked()).toEqual([false, true, false, false])
      expect(currentIndex()).toBe(0)
      expect(thumbs()[0]?.getAttribute('data-dirty')).toBe('true')
      expect(document.querySelectorAll('[data-annotation-type="arrow"]')).toHaveLength(1)

      fireEvent.click(check(3), { shiftKey: true })
      expect(screen.queryByTestId('capture-dirty-confirm')).toBeNull()
      expect(ticked()).toEqual([false, true, true, true])
      expect(inRange()).toEqual([false, true, true, true])
      expect(currentIndex()).toBe(0)
      expect(thumbs()[0]?.getAttribute('data-dirty')).toBe('true')
      expect(document.querySelectorAll('[data-annotation-type="arrow"]')).toHaveLength(1)
      await vi.waitFor(() => {
        expect(status()).toBe('3 shots selected')
      })
    })

    it('AC-89.13 ticked D then B delete in filmstrip order, one at a time, and the editor keeps A', async () => {
      items = [SHOT_A, SHOT_B, SHOT_C, SHOT_D]
      await openFirst()
      await user.click(check(3))
      await user.click(check(1))

      const batch = rightClick(thumbs()[1] as HTMLElement)
      expect(within(batch).getAllByRole('menuitem').map((entry) => entry.textContent)).toEqual(['Delete 2 shots'])
      await user.click(menuItem('capture-filmstrip-menu-delete-batch'))
      expect(screen.getByTestId('capture-confirm-strip').textContent).toContain('Delete 2 captures and their files from disk?')
      await user.click(screen.getByTestId('capture-delete-confirm'))
      await vi.waitFor(() => {
        expect(names()).toEqual(['a.png', 'c.png'])
      })
      expect(deletes()).toHaveLength(2)
      expect(deletes()[0]).toMatch(/\/captures\/shot-b$/)
      expect(deletes()[1]).toMatch(/\/captures\/shot-d$/)
      expect(maxInFlight).toBe(1)
      expect(currentIndex()).toBe(0)
      expect(ticked()).toEqual([false, false])
      await vi.waitFor(() => {
        expect(status()).toBe('Deleted 2 shots.')
      })
    })

    it('AC-89.13 unticking the middle of a Shift-click range of 3 leaves Delete 2 shots', async () => {
      items = [SHOT_A, SHOT_B, SHOT_C, SHOT_D]
      await openFirst()
      shiftClick(thumbs()[2] as HTMLElement)
      await vi.waitFor(() => {
        expect(inRange()).toEqual([true, true, true, false])
      })
      expect(ticked()).toEqual([true, true, true, false])

      await user.click(check(1))
      expect(ticked()).toEqual([true, false, true, false])
      expect(inRange()).toEqual([true, false, true, false])
      const batch = rightClick(thumbs()[2] as HTMLElement)
      expect(within(batch).getAllByRole('menuitem').map((entry) => entry.textContent)).toEqual(['Delete 2 shots'])
    })

    it('AC-89.14 checkboxes are disabled while the batch confirm is open and unchanged after Cancel', async () => {
      items = [SHOT_A, SHOT_B, SHOT_C, SHOT_D]
      await openFirst()
      await user.click(check(1))
      await user.click(check(2))
      await openBatchConfirm(1)
      expect(checks().map((box) => box.disabled)).toEqual([true, true, true, true])

      await user.click(screen.getByTestId('capture-delete-confirm-cancel'))
      expect(checks().map((box) => box.disabled)).toEqual([false, false, false, false])
      expect(ticked()).toEqual([false, true, true, false])
      expect(deletes()).toHaveLength(0)
    })
  })
})
