/** @vitest-environment jsdom */

import { createHash } from 'node:crypto'
import { existsSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ArchiveRestore, Delete, ExternalLink, FolderOpen, Save, Stamp, Trash2 } from 'lucide-react'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { CAPTURE_HELP_SECTIONS } from '../../src/renderer/src/features/capture/capture-help-content'
import * as toolbar from '../../src/renderer/src/features/capture/capture-toolbar'
import { CapturePage } from '../../src/renderer/src/features/capture/CapturePage'
import { queryClient as appQueryClient } from '../../src/renderer/src/lib/query-client'

// MEU-81 gui-capture-action-row (Session 34 plan AC-81.1–81.8, AC-81.10, AC-81.12, AC-81.13, AC-81.15).

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

/** ACTION_BUTTONS (plan §Single-statement contracts), in ACTION_ORDER. */
const ACTIONS = [
  { id: 'capture-remove-mark', icon: Delete, name: 'Remove mark', variant: 'ghost' },
  { id: 'capture-save', icon: Save, name: 'Save overlay', variant: 'primary' },
  { id: 'capture-apply-image', icon: Stamp, name: 'Apply to image', variant: 'secondary' },
  { id: 'capture-revert-image', icon: ArchiveRestore, name: 'Revert image', variant: 'secondary' },
  { id: 'capture-open-file', icon: ExternalLink, name: 'Open file', variant: 'ghost' },
  { id: 'capture-open-folder', icon: FolderOpen, name: 'Open folder', variant: 'ghost' },
  { id: 'capture-delete', icon: Trash2, name: 'Delete shot', variant: 'destructive' },
] as const

/** RETIRED_CONTROLS test ids. */
const RETIRED_IDS = [
  'capture-nudge-body',
  'capture-nudge-tail',
  'capture-nudge-head',
  'capture-nudge-left',
  'capture-nudge-right',
  'capture-nudge-up',
  'capture-nudge-down',
  'capture-color-sample',
]

const HELP_EDIT_TEXT =
  'Select a mark to move it or drag an arrow end until Save. Arrow keys nudge the selected mark, or the arrow end you grabbed or tabbed to; Apply commits color.'

/** A 100×100 shot on a 200×200 surface: Fit gives s = 2 and no letterbox, so client = 2 × image. */
const SHOT = {
  id: 'row-1',
  original_path: 'C:/shots/row.png',
  annotated_path: null,
  sidecar_path: null,
  display_name: 'row.png',
  width: 100,
  height: 100,
  file_size: 32,
  source: 'gui',
  created_at: '2026-10-14T12:00:00Z',
  updated_at: '2026-10-14T12:00:00Z',
}

const ARROW = { type: 'arrow', color: '#ff0000', stroke_width: 2, from: [20, 20], to: [60, 40] }
const ARROW_B = { type: 'arrow', color: '#00ff00', stroke_width: 2, from: [20, 70], to: [60, 90] }
const BOX = { type: 'rect', x: 70, y: 10, width: 20, height: 20, color: '#ff0000', stroke_width: 2 }
const HIGHLIGHT = { type: 'highlight', x: 70, y: 60, width: 20, height: 10, color: '#ffff00', opacity: 0.4 }
const TEXT = { type: 'text', x: 5, y: 80, text: 'Hi', color: '#ffffff', font_size: 16, bg_color: null }
const BACKUP = 'C:/shots/.avkit-backup/row.20261014-120000.png'

type FetchCall = { url: string; method: string; body?: unknown }

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
    openPath: vi.fn(async () => undefined),
    showItemInFolder: vi.fn(async () => undefined),
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

function classTokens(node: Element): string[] {
  return (node.getAttribute('class') ?? '').split(/\s+/).filter((token) => token.length > 0)
}

describe('MEU-81 Capture action row', () => {
  let user: ReturnType<typeof userEvent.setup>
  let queryClient: QueryClient
  let detail: { annotations: unknown[]; backup_path: string | null } = { annotations: [], backup_path: null }
  const calls: FetchCall[] = []

  function count(method: string, fragment: string): number {
    return calls.filter((call) => call.method === method && call.url.includes(fragment)).length
  }

  beforeEach(() => {
    user = userEvent.setup()
    calls.length = 0
    detail = { annotations: [], backup_path: null }
    const settings = {
      inbox_dir: 'C:/shots',
      hotkey: 'F2',
      copy_to_clipboard: false,
      close_to_tray: true,
      flatten_backup: true,
      backup_dir: '',
      annotated_format: 'png',
    }
    // The page's commands refresh the app's QUERY_KEY client (capture-commands.ts), as in the MEU-67 suite.
    queryClient = appQueryClient
    queryClient.setQueryData(['captures'], { items: [SHOT], pendingInteractive: false })
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
      if (/\/captures\/[^/]+\/(flatten|revert)$/.test(path) && method === 'POST') {
        return jsonResponse({ ...SHOT, ...detail })
      }
      if (path.includes('/annotate')) {
        return jsonResponse({ ok: true })
      }
      if (/\/captures\/[^/]+$/.test(path) && method === 'DELETE') {
        return new Response(null, { status: 204 })
      }
      if (/\/captures\/[^/]+$/.test(path) && method === 'GET') {
        return jsonResponse({ ...SHOT, ...detail })
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
    queryClient.clear()
    vi.unstubAllGlobals()
  })

  async function renderPage(): Promise<void> {
    render(createElement(QueryClientProvider, { client: queryClient }, createElement(CapturePage)))
    await vi.waitFor(() => {
      expect(screen.getByTestId('capture-page')).toBeTruthy()
    })
  }

  /** Opens SHOT with the given saved marks (and backup); returns the bound draw surface. */
  async function openShot(marks: unknown[], backup: string | null = null): Promise<HTMLElement> {
    detail = { annotations: marks, backup_path: backup }
    await renderPage()
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

  async function selectMark(index: number): Promise<void> {
    const buttons = screen.getByTestId('capture-mark-list').querySelectorAll('button')
    expect(buttons.length, 'mark chips rendered').toBeGreaterThan(index)
    await user.click(buttons[index] as HTMLElement)
  }

  function pointer(target: Element, type: string, clientX: number, clientY: number): void {
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
      pointer(surface, 'pointerdown', fromX, fromY)
      pointer(surface, 'pointermove', toX, toY)
      pointer(surface, 'pointerup', toX, toY)
    })
  }

  async function key(target: EventTarget, type: 'keydown' | 'keyup', name: string): Promise<void> {
    await act(async () => {
      target.dispatchEvent(new KeyboardEvent(type, { key: name, bubbles: true, cancelable: true }))
    })
  }

  /** One key press dispatched on `target`: keydown there, then keyup there (bubbling to window). */
  async function press(target: EventTarget, name: string): Promise<void> {
    await key(target, 'keydown', name)
    await key(target, 'keyup', name)
  }

  async function focus(target: Element): Promise<void> {
    await act(async () => {
      ;(target as HTMLElement | SVGElement).focus()
    })
  }

  /** Every rendered mark's geometry, in DTO order. */
  function geometry(): Array<Record<string, string | null>> {
    return Array.from(document.querySelectorAll('[data-annotation-type]')).map((node) => {
      const row: Record<string, string | null> = { type: node.getAttribute('data-annotation-type') }
      for (const name of ['x1', 'y1', 'x2', 'y2', 'x', 'y']) {
        row[name] = node.getAttribute(name)
      }
      return row
    })
  }

  /** ARROW (index 0) or ARROW_B (index 1), found by its color: the viewport paints the selected mark first. */
  function arrowEnds(index = 0): { x1: number; y1: number; x2: number; y2: number } {
    const color = [ARROW.color, ARROW_B.color][index]
    const node = document.querySelector(`[data-annotation-type="arrow"][stroke="${color}"]`)
    expect(node, `arrow ${index} rendered`).toBeTruthy()
    return {
      x1: Number(node?.getAttribute('x1')),
      y1: Number(node?.getAttribute('y1')),
      x2: Number(node?.getAttribute('x2')),
      y2: Number(node?.getAttribute('y2')),
    }
  }

  function undoDisabled(): boolean {
    return (screen.getByTestId('capture-undo') as HTMLButtonElement).disabled
  }

  /** The action slot is the parent of the Delete tip (ACTION_ORDER). */
  function actionSlot(): HTMLElement {
    const tip = screen.queryByTestId('capture-delete-tip')
    expect(tip, 'capture-delete-tip rendered').not.toBeNull()
    return (tip as HTMLElement).parentElement as HTMLElement
  }

  function expectIconAction(action: (typeof ACTIONS)[number]): void {
    const button = screen.queryByTestId(action.id)
    expect(button, `${action.id} mounted`).not.toBeNull()
    const tip = screen.queryByTestId(`${action.id}-tip`)
    expect(tip, `${action.id}-tip`).not.toBeNull()
    expect(tip?.contains(button), `${action.id} inside its tip`).toBe(true)
    expect(button?.textContent?.trim(), `${action.id} has no text`).toBe('')
    expect(button?.getAttribute('aria-label'), `${action.id} aria-label`).toBe(action.name)
    const svgs = button?.querySelectorAll('svg') ?? []
    expect(svgs.length, `${action.id} one svg`).toBe(1)
    expect(svgs[0]?.getAttribute('aria-hidden'), `${action.id} svg hidden`).toBe('true')
    expect(classTokens(button as HTMLElement), `${action.id} variant`).toContain(`btn-${action.variant}`)
    expect(button?.getAttribute('title'), `${action.id} title`).toBeNull()
    expect(tip?.getAttribute('title'), `${action.id}-tip title`).toBeNull()
  }

  function expectSlotOrder(mounted: string[]): void {
    const slot = actionSlot()
    const order = Array.from(slot.children).map((node) => node.getAttribute('data-testid'))
    const expected = [...mounted.map((id) => `${id}-tip`), 'capture-actions-separator', 'capture-delete-tip']
    expect(order).toEqual(expected)
    const separator = screen.getByTestId('capture-actions-separator')
    expect(separator.getAttribute('role')).toBe('separator')
    expect(separator.getAttribute('aria-orientation')).toBe('vertical')
    expect(slot.lastElementChild).toBe(screen.getByTestId('capture-delete-tip'))
    expect(screen.getByTestId('capture-delete-tip').previousElementSibling).toBe(separator)
  }

  it('setup sentinel', async () => {
    await openShot([ARROW])
    expect(screen.getByTestId('capture-page')).toBeTruthy()
    expect(screen.getByTestId('capture-draw-surface')).toBeTruthy()
    expect(document.querySelectorAll('[data-annotation-type="arrow"]')).toHaveLength(1)
  })

  it('AC-81.1: ACTION_BUTTONS has the 7 ids, icons and names, disjoint from TOOLBAR_BUTTONS', () => {
    const table = (toolbar as unknown as Record<string, unknown>).ACTION_BUTTONS as
      | Record<string, { icon: unknown; name: string }>
      | undefined
    expect(table, 'ACTION_BUTTONS exported from capture-toolbar').toBeDefined()
    const rows = table as Record<string, { icon: unknown; name: string }>
    expect(Object.keys(rows)).toEqual(ACTIONS.map((action) => action.id))
    expect(new Set(Object.keys(rows)).size).toBe(ACTIONS.length)
    for (const action of ACTIONS) {
      expect(rows[action.id]?.icon, action.id).toBe(action.icon)
      expect(rows[action.id]?.name, action.id).toBe(action.name)
      // A lucide icon is a forwardRef component.
      expect(typeof rows[action.id]?.icon, action.id).toBe('object')
      expect((rows[action.id]?.icon as { $$typeof?: symbol }).$$typeof, action.id).toBe(Symbol.for('react.forward_ref'))
      expect(Object.keys(toolbar.TOOLBAR_BUTTONS), action.id).not.toContain(action.id)
    }
  })

  it('AC-81.2: every mounted action is icon-only in its tip, per ACTION_ORDER, with Delete last after the separator', async () => {
    const surface = await openShot([ARROW], BACKUP)
    await selectMark(0)
    // Clean: Apply and Revert enabled; Save unmounted.
    expect(screen.queryByTestId('capture-save')).toBeNull()
    expectSlotOrder(['capture-remove-mark', 'capture-apply-image', 'capture-revert-image', 'capture-open-file', 'capture-open-folder'])
    for (const action of ACTIONS.filter((row) => row.id !== 'capture-save')) {
      expectIconAction(action)
    }
    expect((screen.getByTestId('capture-apply-image') as HTMLButtonElement).disabled).toBe(false)
    expect((screen.getByTestId('capture-revert-image') as HTMLButtonElement).disabled).toBe(false)
    // Dirty: a new arrow mounts Save; Apply and Revert are disabled and still carry no title.
    await user.click(screen.getByTestId('capture-tool-arrow'))
    await drag(surface, 20, 120, 120, 180)
    expect(document.querySelectorAll('[data-annotation-type="arrow"]')).toHaveLength(2)
    expectSlotOrder([
      'capture-remove-mark',
      'capture-save',
      'capture-apply-image',
      'capture-revert-image',
      'capture-open-file',
      'capture-open-folder',
    ])
    for (const action of ACTIONS) {
      expectIconAction(action)
    }
    expect((screen.getByTestId('capture-apply-image') as HTMLButtonElement).disabled).toBe(true)
    expect((screen.getByTestId('capture-revert-image') as HTMLButtonElement).disabled).toBe(true)
    // No action button holds a text node.
    for (const action of ACTIONS) {
      const button = screen.getByTestId(action.id)
      const texts = Array.from(button.childNodes).filter(
        (node) => node.nodeType === Node.TEXT_NODE && (node.textContent ?? '').trim() !== '',
      )
      expect(texts, action.id).toHaveLength(0)
    }
    cleanup()
    // Revert with no backup is unmounted, and the order closes up around it.
    await openShot([ARROW])
    expect(screen.queryByTestId('capture-revert-image')).toBeNull()
    expectSlotOrder(['capture-apply-image', 'capture-open-file', 'capture-open-folder'])
  })

  it('AC-81.3: each icon action keeps its behaviour', async () => {
    await openShot([ARROW, BOX], BACKUP)
    // Remove mark is not mounted with no selection.
    expect(screen.queryByTestId('capture-remove-mark')).toBeNull()
    // Apply opens the flatten strip; Revert opens the revert strip (Cancel sends nothing).
    await user.click(screen.getByTestId('capture-apply-image'))
    expect(screen.getByTestId('capture-flatten-confirm')).toBeTruthy()
    await user.click(screen.getByTestId('capture-flatten-confirm-cancel'))
    await user.click(screen.getByTestId('capture-revert-image'))
    expect(screen.getByTestId('capture-revert-confirm')).toBeTruthy()
    await user.click(screen.getByTestId('capture-revert-confirm-cancel'))
    expect(count('POST', '/flatten') + count('POST', '/revert')).toBe(0)
    // Open file and Open folder call the IPC once each.
    await user.click(screen.getByTestId('capture-open-file'))
    await user.click(screen.getByTestId('capture-open-folder'))
    expect(window.api.openPath).toHaveBeenCalledTimes(1)
    expect(window.api.openPath).toHaveBeenCalledWith(SHOT.original_path)
    expect(window.api.showItemInFolder).toHaveBeenCalledTimes(1)
    // Delete opens its strip and sends no request before confirm.
    await user.click(screen.getByTestId('capture-delete'))
    expect(screen.getByTestId('capture-delete-confirm')).toBeTruthy()
    expect(count('DELETE', '/captures')).toBe(0)
    await user.click(screen.getByTestId('capture-delete-confirm-cancel'))
    // Remove mark removes only the selected mark, with no DELETE.
    await selectMark(0)
    await user.click(screen.getByTestId('capture-remove-mark'))
    expect(geometry().map((row) => row.type)).toEqual(['rect'])
    expect(count('DELETE', '/captures')).toBe(0)
    // Save posts annotate once with the one remaining mark.
    await user.click(screen.getByTestId('capture-save'))
    await vi.waitFor(() => {
      expect(count('POST', '/annotate')).toBe(1)
    })
    const posted = calls.find((call) => call.method === 'POST' && call.url.includes('/annotate'))
    expect((posted?.body as { annotations: unknown[] }).annotations).toHaveLength(1)
  })

  it('AC-81.4: the retired controls are gone in every state, and the Color options are well, hex, Apply, Cancel, Named', async () => {
    await openShot([ARROW, BOX, HIGHLIGHT, TEXT])
    const expectRetiredAbsent = (state: string): void => {
      for (const id of RETIRED_IDS) {
        expect(screen.queryByTestId(id), `${id} (${state})`).toBeNull()
      }
    }
    expectRetiredAbsent('no selection')
    for (const [index, type] of ['arrow', 'box', 'highlight', 'text'].entries()) {
      await selectMark(index)
      expectRetiredAbsent(`${type} selected`)
    }
    for (const tool of ['arrow', 'box', 'highlight', 'text', 'select']) {
      await user.click(screen.getByTestId(`capture-tool-${tool}`))
      expectRetiredAbsent(`${tool} tool`)
    }
    await selectMark(0)
    const group = screen.getByTestId('capture-color-well').closest('[role="group"]') as HTMLElement
    expect(group).not.toBeNull()
    const ids = Array.from(group.querySelectorAll('[data-testid]')).map((node) => node.getAttribute('data-testid'))
    expect(ids).toEqual(['capture-color-well', 'capture-color', 'capture-color-apply', 'capture-color-cancel', 'capture-named-color'])
    // The sampler module is gone.
    expect(existsSync(resolve(UI, 'src/renderer/src/features/capture/capture-sample.ts'))).toBe(false)
    const samplePath = '../../src/renderer/src/features/capture/capture-sample'
    await expect(import(/* @vite-ignore */ samplePath)).rejects.toBeTruthy()
  })

  it('AC-81.5: arrow keys on the focused surface nudge the selected mark body; one burst is one history entry', async () => {
    const surface = await openShot([BOX, ARROW])
    // Negative: with no selection a key changes nothing and adds no history.
    const start = geometry()
    await focus(surface)
    await press(surface, 'ArrowRight')
    expect(geometry()).toEqual(start)
    expect(undoDisabled()).toBe(true)
    // A box moves by KEYBOARD_NUDGE_PX in each direction.
    await selectMark(0)
    await focus(surface)
    const box = (): { x: number; y: number } => {
      const node = document.querySelector('[data-annotation-type="rect"]')
      return { x: Number(node?.getAttribute('x')), y: Number(node?.getAttribute('y')) }
    }
    expect(box()).toEqual({ x: 70, y: 10 })
    await press(surface, 'ArrowRight')
    expect(box()).toEqual({ x: 71, y: 10 })
    await press(surface, 'ArrowDown')
    expect(box()).toEqual({ x: 71, y: 11 })
    await press(surface, 'ArrowLeft')
    expect(box()).toEqual({ x: 70, y: 11 })
    await press(surface, 'ArrowUp')
    expect(box()).toEqual({ x: 70, y: 10 })
    // One burst (three keydowns, one keyup) is one history entry.
    for (let step = 0; step < 4; step += 1) {
      await user.click(screen.getByTestId('capture-undo'))
    }
    expect(undoDisabled()).toBe(true)
    expect(box()).toEqual({ x: 70, y: 10 })
    // Undo clears the selection; reselect before the burst.
    await selectMark(0)
    await focus(surface)
    await key(surface, 'keydown', 'ArrowRight')
    await key(surface, 'keydown', 'ArrowRight')
    await key(surface, 'keydown', 'ArrowRight')
    await key(surface, 'keyup', 'ArrowRight')
    expect(box()).toEqual({ x: 73, y: 10 })
    await user.click(screen.getByTestId('capture-undo'))
    expect(box()).toEqual({ x: 70, y: 10 })
    expect(undoDisabled()).toBe(true)
    // Esc during a burst restores the start geometry and adds no history.
    await selectMark(0)
    await focus(surface)
    await key(surface, 'keydown', 'ArrowDown')
    expect(box()).toEqual({ x: 70, y: 11 })
    await key(surface, 'keydown', 'Escape')
    await key(surface, 'keyup', 'ArrowDown')
    expect(box()).toEqual({ x: 70, y: 10 })
    expect(undoDisabled()).toBe(true)
    // With an arrow selected and the surface focused, both ends move.
    await selectMark(1)
    await focus(surface)
    await press(surface, 'ArrowRight')
    expect(arrowEnds()).toEqual({ x1: 21, y1: 20, x2: 61, y2: 40 })
  })

  it('AC-81.6: the arrow handles sit in the handle layer, take focus, and choose the nudged end', async () => {
    const surface = await openShot([ARROW, ARROW_B])
    await selectMark(0)
    const layer = screen.queryByTestId('capture-handle-layer')
    expect(layer, 'capture-handle-layer rendered').not.toBeNull()
    const content = screen.getByTestId('capture-zoom-content')
    const marksSvg = document.querySelector('[data-annotation-type="arrow"]')?.closest('svg') as SVGSVGElement
    expect(layer?.parentElement).toBe(content)
    expect(marksSvg.parentElement).toBe(content)
    expect(layer?.previousElementSibling).toBe(marksSvg)
    expect(layer?.getAttribute('viewBox')).toBe(marksSvg.getAttribute('viewBox'))
    expect(layer?.getAttribute('preserveAspectRatio')).toBe(marksSvg.getAttribute('preserveAspectRatio'))
    expect(surface.contains(layer)).toBe(true)
    expect(layer?.parentElement).not.toBe(surface)
    expect(layer?.closest('[aria-hidden="true"]')).toBeNull()
    const from = screen.getByTestId('capture-handle-from')
    const to = screen.getByTestId('capture-handle-to')
    for (const [handle, label] of [
      [from, 'Arrow tail'],
      [to, 'Arrow head'],
    ] as const) {
      expect(layer?.contains(handle), label).toBe(true)
      expect(handle.getAttribute('tabindex'), label).toBe('0')
      expect(handle.getAttribute('role'), label).toBe('button')
      expect(handle.getAttribute('aria-label'), label).toBe(label)
    }
    // Focus the head, ArrowUp on it: only `to` moves.
    await focus(to)
    await press(to, 'ArrowUp')
    expect(arrowEnds()).toEqual({ x1: 20, y1: 20, x2: 60, y2: 39 })
    // Focus the tail: only `from` moves.
    await focus(screen.getByTestId('capture-handle-from'))
    await press(screen.getByTestId('capture-handle-from'), 'ArrowUp')
    expect(arrowEnds()).toEqual({ x1: 20, y1: 19, x2: 60, y2: 39 })
    // Focus on the surface itself resets to body: both ends move.
    await focus(screen.getByTestId('capture-handle-to'))
    await focus(surface)
    await press(surface, 'ArrowUp')
    expect(arrowEnds()).toEqual({ x1: 20, y1: 18, x2: 60, y2: 38 })
    // A grab (pointerdown/up, no move) on the head, then ArrowLeft: only `to` moves.
    await act(async () => {
      pointer(surface, 'pointerdown', 120, 76)
      pointer(surface, 'pointerup', 120, 76)
    })
    await press(surface, 'ArrowLeft')
    expect(arrowEnds()).toEqual({ x1: 20, y1: 18, x2: 59, y2: 38 })
    // Space on a focused handle does not arm pan.
    const kind = surface.getAttribute('data-zoom-kind')
    await focus(screen.getByTestId('capture-handle-to'))
    await key(screen.getByTestId('capture-handle-to'), 'keydown', ' ')
    expect(surface.getAttribute('data-zoom-kind')).toBe(kind)
    expect(classTokens(surface)).not.toContain('cursor-grab')
    expect(classTokens(surface)).not.toContain('cursor-grabbing')
    await key(screen.getByTestId('capture-handle-to'), 'keyup', ' ')
    // Selecting another mark resets to body: grab A's head, select B, ArrowUp moves both of B's ends.
    await focus(surface)
    await act(async () => {
      pointer(surface, 'pointerdown', 118, 76)
      pointer(surface, 'pointerup', 118, 76)
    })
    await selectMark(1)
    // Dispatched on the surface without refocusing it, so only the selection change can reset the target.
    await press(surface, 'ArrowUp')
    expect(arrowEnds(1)).toEqual({ x1: 20, y1: 69, x2: 60, y2: 89 })
    // Changing tool resets to body.
    await focus(surface)
    await act(async () => {
      pointer(surface, 'pointerdown', 120, 178)
      pointer(surface, 'pointerup', 120, 178)
    })
    await user.click(screen.getByTestId('capture-tool-box'))
    await user.click(screen.getByTestId('capture-tool-select'))
    await selectMark(1)
    await press(surface, 'ArrowUp')
    expect(arrowEnds(1)).toEqual({ x1: 20, y1: 68, x2: 60, y2: 88 })
  })

  it('AC-81.7: arrow keys during a live pointer gesture change no geometry and add no history', async () => {
    const surface = await openShot([ARROW])
    await selectMark(0)
    await focus(surface)
    const start = geometry()
    // Pressed on the body, not yet moved.
    await act(async () => {
      pointer(surface, 'pointerdown', 80, 60)
    })
    await press(surface, 'ArrowRight')
    await act(async () => {
      pointer(surface, 'pointerup', 80, 60)
    })
    expect(geometry()).toEqual(start)
    expect(undoDisabled()).toBe(true)
    // Moving the body: a key mid-drag, then back to the start and up.
    await act(async () => {
      pointer(surface, 'pointerdown', 80, 60)
      pointer(surface, 'pointermove', 100, 60)
    })
    await press(surface, 'ArrowDown')
    await act(async () => {
      pointer(surface, 'pointermove', 80, 60)
      pointer(surface, 'pointerup', 80, 60)
    })
    expect(geometry()).toEqual(start)
    expect(undoDisabled()).toBe(true)
    // Dragging the head: the same.
    await act(async () => {
      pointer(surface, 'pointerdown', 120, 80)
      pointer(surface, 'pointermove', 140, 80)
    })
    await press(surface, 'ArrowUp')
    await act(async () => {
      pointer(surface, 'pointermove', 120, 80)
      pointer(surface, 'pointerup', 120, 80)
    })
    expect(geometry()).toEqual(start)
    expect(undoDisabled()).toBe(true)
  })

  it('AC-81.8: MARKS_ROW_LAYOUT: only the chip list scrolls; the row and the action slot do not shrink', async () => {
    await openShot([ARROW])
    const row = classTokens(screen.getByTestId('capture-chrome-marks'))
    expect(row).toContain('shrink-0')
    expect(row).toContain('flex-nowrap')
    expect(row).not.toContain('overflow-x-auto')
    const list = classTokens(screen.getByTestId('capture-mark-list'))
    expect(list).toEqual(expect.arrayContaining(['min-w-0', 'flex-1', 'overflow-x-auto']))
    expect(classTokens(actionSlot())).toContain('shrink-0')
  })

  it('AC-81.10: HEADER_STATUS: the in-use banner is a child of capture-header; a free hotkey mounts no banner', async () => {
    window.api.getHotkeyStatus = vi.fn(async () => ({ accelerator: 'F2', registered: false, inUse: true }))
    await renderPage()
    await vi.waitFor(() => {
      expect(screen.queryByTestId('capture-hotkey-banner')?.textContent).toContain(
        'F2 is in use — quit ShareX or pick another key',
      )
    })
    const header = screen.queryByTestId('capture-header')
    expect(header, 'capture-header rendered').not.toBeNull()
    expect(classTokens(header as HTMLElement)).toContain('flex-nowrap')
    const banner = screen.getByTestId('capture-hotkey-banner')
    expect(banner.parentElement).toBe(header)
    expect(banner.getAttribute('role')).toBe('status')
    expect(banner.querySelector('[data-tone="warning"]')?.textContent).toBe('Hotkey')
    cleanup()
    window.api.getHotkeyStatus = vi.fn(async () => ({ accelerator: 'F2', registered: true, inUse: false }))
    await renderPage()
    await vi.waitFor(() => {
      expect(window.api.getHotkeyStatus).toHaveBeenCalled()
    })
    await act(async () => {
      await Promise.resolve()
      await Promise.resolve()
    })
    expect(screen.queryByTestId('capture-hotkey-banner')).toBeNull()
    expect(classTokens(screen.getByTestId('capture-header'))).toContain('flex-nowrap')
  })

  it('AC-81.12: the four-tools help holds HELP_EDIT_TEXT and no Capture help mentions Sample', () => {
    const four = CAPTURE_HELP_SECTIONS.find((section) => section.id === 'four-tools')
    expect(four?.body).toContain(HELP_EDIT_TEXT)
    for (const section of CAPTURE_HELP_SECTIONS) {
      expect(section.body, section.id).not.toContain('Sample')
    }
  })

  it('AC-81.13: the registry drops RETIRED_TESTIDS, adds NEW_TESTIDS after MEU-67, and re-pins AC-51.6', () => {
    const registry = readFileSync(resolve(UI, 'tests/e2e/test-ids.ts'), 'utf8')
    for (const name of [
      'CAPTURE_COLOR_SAMPLE',
      'CAPTURE_NUDGE_BODY',
      'CAPTURE_NUDGE_TAIL',
      'CAPTURE_NUDGE_HEAD',
      'CAPTURE_NUDGE_LEFT',
      'CAPTURE_NUDGE_RIGHT',
      'CAPTURE_NUDGE_UP',
      'CAPTURE_NUDGE_DOWN',
    ]) {
      expect(registry, name).not.toMatch(new RegExp(`\\b${name}\\b`))
    }
    const meu67 = '// MEU-67 Capture flatten and revert (additive IDs).'
    const marker = '// MEU-80/81 icon hints and the Capture action row (additive IDs).'
    expect(registry.indexOf(meu67)).toBeGreaterThan(-1)
    expect(registry.indexOf(marker)).toBeGreaterThan(registry.indexOf(meu67))
    const block = registry.split(marker)[1] ?? ''
    const NEW_TESTIDS: Record<string, string> = {
      CAPTURE_HEADER: 'capture-header',
      CAPTURE_ACTIONS_SEPARATOR: 'capture-actions-separator',
      CAPTURE_REMOVE_MARK_TIP: 'capture-remove-mark-tip',
      CAPTURE_TOOL_ARROW_HINT: 'capture-tool-arrow-hint',
      CAPTURE_UNDO_TIP: 'capture-undo-tip',
      CAPTURE_UNDO_HINT: 'capture-undo-hint',
      CAPTURE_APPLY_IMAGE_TIP: 'capture-apply-image-tip',
      CAPTURE_APPLY_IMAGE_HINT: 'capture-apply-image-hint',
      CAPTURE_DELETE_TIP: 'capture-delete-tip',
      CONSOLE_CLOSE_HINT: 'console-close-hint',
    }
    for (const [name, value] of Object.entries(NEW_TESTIDS)) {
      expect(block, name).toContain(`export const ${name} = '${value}'`)
    }
    const prefix = registry.split('// MEU-51 primitive harness IDs.')[0] ?? ''
    const hash = createHash('sha256').update(prefix).digest('hex').toUpperCase()
    expect(hash).toBe('6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454')
  })

  it('AC-81.15: arrow keys in text entry, the filmstrip or the confirm strip move no mark', async () => {
    const surface = await openShot([ARROW])
    const start = geometry()
    // Text draft (Text tool).
    await selectMark(0)
    await user.click(screen.getByTestId('capture-tool-text'))
    await act(async () => {
      pointer(surface, 'pointerdown', 20, 180)
      pointer(surface, 'pointerup', 20, 180)
    })
    const draft = screen.getByTestId('capture-text-draft')
    await focus(draft)
    await press(draft, 'ArrowUp')
    expect(geometry()).toEqual(start)
    await key(draft, 'keydown', 'Escape')
    expect(screen.queryByTestId('capture-text-draft')).toBeNull()
    // The hex input (Color options): the value is unchanged too.
    await user.click(screen.getByTestId('capture-tool-select'))
    await selectMark(0)
    const hex = screen.getByTestId('capture-color') as HTMLInputElement
    await user.click(hex)
    const value = hex.value
    await user.keyboard('{ArrowUp}')
    expect(geometry()).toEqual(start)
    expect(hex.value).toBe(value)
    // A filmstrip item button.
    await selectMark(0)
    const item = screen.getAllByTestId('capture-filmstrip-item')[0] as HTMLElement
    await focus(item)
    await user.keyboard('{ArrowUp}')
    expect(geometry()).toEqual(start)
    // A confirm strip button (Delete confirm open).
    await selectMark(0)
    await user.click(screen.getByTestId('capture-delete'))
    const cancel = screen.getByTestId('capture-delete-confirm-cancel')
    await focus(cancel)
    await user.keyboard('{ArrowUp}')
    expect(geometry()).toEqual(start)
    await user.click(cancel)
    expect(undoDisabled()).toBe(true)
  })
})
