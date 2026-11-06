/** @vitest-environment jsdom */

/**
 * MEU-80 icon-only inventory (AC-80.8, AC-80.9): every `ICON_ONLY_INVENTORY` control sits in a `TOOLTIP`
 * wrapper, has no `title` (`HINT_TITLE_RULE`, proved in the rendered DOM) and shows `{id}-hint` on focus.
 *
 * This file does not import the Tooltip module, so it loads before the module exists; its first case is the
 * `SETUP_SENTINEL`, which proves the shared Capture harness mounts. Focus shows a hint at once
 * (`HINT_TIMING`), so the cases run on real timers.
 */
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { ConsolePanel } from '../../src/renderer/src/components/layout/ConsolePanel'
import { BulkResultToast } from '../../src/renderer/src/components/queue/BulkResultToast'
import { QueueCard, type QueueCardProps } from '../../src/renderer/src/components/queue/QueueCard'
import { CapturePage } from '../../src/renderer/src/features/capture/CapturePage'
import { TOOLBAR_BUTTONS } from '../../src/renderer/src/features/capture/capture-toolbar'
import { ConvertPage } from '../../src/renderer/src/features/converter/ConvertPage'
import { TranscriptPage } from '../../src/renderer/src/features/transcript/TranscriptPage'
import type { TranscriptListItem } from '../../src/renderer/src/features/transcript/useTranscriptQueue'
import type { BulkResult } from '../../src/renderer/src/lib/queue/run-bulk'
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

/** `CaptureViewport.tsx` NO_SHOT_HINT, the reason the shot-bound buttons carry with no shot. */
const NO_SHOT_HINT = 'Select a shot first'
const NO_SHOT_IDS = new Set([
  'capture-tool-select',
  'capture-tool-arrow',
  'capture-tool-box',
  'capture-tool-highlight',
  'capture-tool-text',
  'capture-tool-pixelate',
  'capture-tool-eraser',
  'capture-zoom-out',
  'capture-zoom-in',
  'capture-zoom-fit',
])
/** TA-3 (D-177): MEU-99 `HISTORY_HINTS` adds the chord to the Undo and Redo hints; the names are unchanged. */
const HINT_OVERRIDE: Record<string, string> = { 'capture-undo': 'Undo (Ctrl+Z)', 'capture-redo': 'Redo (Ctrl+Y)' }

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
    showFilesDialog: async () => ['C:/e2e/sample.mp4'],
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

function transcriptItem(id: string, name: string, position: number): TranscriptListItem {
  return {
    id,
    channel_name: name,
    status: 'Pending',
    channel_url: `https://www.youtube.com/@${name}`,
    output_dir: `C:/t/${name}`,
    video_count: 0,
    transcripts_done: 0,
    word_count: 0,
    zip_path: null,
    last_title: null,
    last_item_status: null,
    last_item_message: null,
    queue_position: position,
    error_message: null,
    compiled_path: null,
  }
}

const TRANSCRIPTS: TranscriptListItem[] = [
  transcriptItem('a', 'Alpha', 1),
  transcriptItem('b', 'Bravo', 2),
  transcriptItem('c', 'Charlie', 3),
]

let catalogItems: Array<typeof SHOT> = [SHOT]

function stubFetch(): void {
  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = hrefOf(input)
    const method = (init?.method ?? 'GET').toUpperCase()
    const path = (url.split('?')[0] ?? url).replace(/^https?:\/\/[^/]+/, '').replace('/api/v1', '')
    if (path === '/settings/capture') {
      return jsonResponse({ inbox_dir: 'C:/Pictures/av-kit', hotkey: 'F2', copy_to_clipboard: false, close_to_tray: true })
    }
    if (path === '/settings/transcript') {
      return jsonResponse({ delay_between_requests: 20 })
    }
    if (path === '/settings/converter') {
      return jsonResponse({ output_dir: '~/Videos/av-kit', default_preset: 'archival', skip_existing: true, gpu_preference: 'auto' })
    }
    if (path === '/settings/ui') {
      return jsonResponse({ theme: 'dark' })
    }
    if (path === '/health/dependencies') {
      return jsonResponse({ ffmpeg: { available: true, version: '7.1.2' }, yt_dlp: { available: true } })
    }
    if (path.startsWith('/conversions/gpu')) {
      return jsonResponse({
        nvidia_nvenc: false,
        amd_amf: false,
        intel_qsv: false,
        vulkan: false,
        software_h265: true,
        software_h264: true,
        recommended_encoder: 'libx265',
        checked_at: '2026-08-26T00:00:00Z',
      })
    }
    if (path === '/conversions' && method === 'GET') {
      return jsonResponse({ items: [], processor: { state: 'Idle', current_job_id: null } })
    }
    if (path === '/transcripts' && method === 'GET') {
      return jsonResponse({ items: TRANSCRIPTS, processor: { state: 'Idle' } })
    }
    if (path === '/captures/requests') {
      return jsonResponse({ items: [] })
    }
    if (path.endsWith('/image')) {
      return new Response(new Uint8Array([1, 2, 3]), { status: 200, headers: { 'Content-Type': 'image/png' } })
    }
    const shot = path.match(/^\/captures\/([^/]+)$/)
    if (shot && method === 'GET') {
      return jsonResponse({ ...SHOT, id: shot[1], annotations: [] })
    }
    if (path === '/captures') {
      return jsonResponse({ items: catalogItems })
    }
    return jsonResponse({})
  })
  vi.stubGlobal('fetch', fetchMock)
  window.fetch = fetchMock as typeof window.fetch
}

function makeClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false, staleTime: Infinity, gcTime: 0 },
    },
  })
}

let user: ReturnType<typeof userEvent.setup>
let client: QueryClient

beforeEach(() => {
  user = userEvent.setup()
  catalogItems = [SHOT]
  client = makeClient()
  appQueryClient.clear()
  mockApi()
  URL.createObjectURL = vi.fn(() => 'blob:capture-shot')
  URL.revokeObjectURL = vi.fn()
  stubFetch()
})

afterEach(() => {
  cleanup()
  client.clear()
  appQueryClient.clear()
  vi.unstubAllGlobals()
})

/** The shared Capture harness: render the page, and with `open` select the first shot. */
async function renderCapture(open: boolean): Promise<void> {
  if (!open) {
    catalogItems = []
  }
  client.setQueryData(['captures'], { items: catalogItems, pendingInteractive: false })
  render(createElement(QueryClientProvider, { client }, createElement(CapturePage)))
  await vi.waitFor(() => {
    expect(screen.getByTestId('capture-page')).toBeTruthy()
  })
  if (open) {
    await vi.waitFor(() => {
      expect(screen.getAllByTestId('capture-filmstrip-item').length).toBeGreaterThan(0)
    })
    await user.click(screen.getAllByTestId('capture-filmstrip-item')[0] as HTMLElement)
    await vi.waitFor(() => {
      expect(screen.getByTestId('capture-draw-surface').getAttribute('data-overlay-ready')).toBe('true')
    })
  }
}

function focusOn(el: HTMLElement): void {
  act(() => {
    el.focus()
  })
}

function blurFrom(el: HTMLElement): void {
  act(() => {
    el.blur()
  })
}

function tokens(el: Element): string[] {
  return (el.getAttribute('aria-describedby') ?? '').split(/\s+/).filter(Boolean)
}

/**
 * One inventory control: it sits in `{id}-tip`, neither node has a `title`, and focusing its focus target
 * (the wrapper when disabled, the control when enabled) shows `{id}-hint` with `expected`.
 */
function expectHinted(scope: HTMLElement, id: string, expected: string, label: string): void {
  const control = within(scope).getByTestId(id)
  const tip = within(scope).getByTestId(`${id}-tip`)
  expect(tip.contains(control), `${label}: ${id} sits in ${id}-tip`).toBe(true)
  expect(control.getAttribute('title'), `${label}: ${id} has no title`).toBeNull()
  expect(tip.getAttribute('title'), `${label}: ${id}-tip has no title`).toBeNull()
  const disabled = (control as HTMLButtonElement).disabled === true
  const target = disabled ? tip : control
  focusOn(target)
  const hint = screen.queryByTestId(`${id}-hint`)
  expect(hint, `${label}: focusing ${disabled ? `${id}-tip` : id} shows ${id}-hint`).not.toBeNull()
  expect(hint?.textContent, `${label}: ${id}-hint text`).toBe(expected)
  expect(tokens(target), `${label}: ${id} focus target is described by the hint`).toContain(hint?.id)
  blurFrom(target)
  expect(screen.queryByTestId(`${id}-hint`), `${label}: ${id}-hint hides on blur`).toBeNull()
}

describe('MEU-80 icon-only inventory hints', () => {
  it('setup sentinel', async () => {
    await renderCapture(true)
    expect(screen.getByTestId('capture-page')).toBeTruthy()
    expect(screen.getByTestId('capture-tool-arrow')).toBeTruthy()
  })

  it('AC-80.8: the 13 Capture toolbar buttons are wrapped, untitled and hinted, with and without a shot', async () => {
    await renderCapture(true)
    const page = screen.getByTestId('capture-page')
    for (const [id, spec] of Object.entries(TOOLBAR_BUTTONS)) {
      expectHinted(page, id, HINT_OVERRIDE[id] ?? spec.name, 'shot open')
    }
    expect(screen.queryByTestId('nav-capture-tip'), 'the nav-capture rail item is not wrapped').toBeNull()
    cleanup()
    await renderCapture(false)
    const empty = screen.getByTestId('capture-page')
    for (const [id, spec] of Object.entries(TOOLBAR_BUTTONS)) {
      const control = within(empty).getByTestId(id) as HTMLButtonElement
      const expected = control.disabled && NO_SHOT_IDS.has(id) ? `${spec.name} — ${NO_SHOT_HINT}` : (HINT_OVERRIDE[id] ?? spec.name)
      expectHinted(empty, id, expected, 'no shot')
    }
    for (const id of NO_SHOT_IDS) {
      expect((within(empty).getByTestId(id) as HTMLButtonElement).disabled, `${id} disabled with no shot`).toBe(true)
    }
  })

  it('AC-80.9: the non-Capture icon-only controls are wrapped, untitled and hinted by their aria-label', async () => {
    // console-close
    const consoleView = render(createElement(ConsolePanel, { lines: [], onClose: vi.fn() }))
    const close = within(consoleView.container).getByTestId('console-close')
    expect(close.getAttribute('aria-label')).toBe('Close console')
    expectHinted(consoleView.container, 'console-close', 'Close console', 'console')
    consoleView.unmount()

    // bulk-toast-dismiss
    const result: BulkResult = { attempted: ['a', 'b'], succeeded: ['a'], failed: [], message: 'Removed 1 of 2' }
    const toastView = render(createElement(BulkResultToast, { result, onDismiss: vi.fn() }))
    const dismiss = within(toastView.container).getByTestId('bulk-toast-dismiss')
    expect(dismiss.getAttribute('aria-label')).toBe('Dismiss')
    expectHinted(toastView.container, 'bulk-toast-dismiss', 'Dismiss', 'bulk toast')
    toastView.unmount()

    // queue-card-drag-handle (enabled and disabled), queue-card-kebab (suppressed while open), and the
    // labelled primary action, which keeps its title and gets no tip.
    const listeners = { onPointerDown: vi.fn(), onKeyDown: vi.fn() }
    const cardProps = (disabled: boolean): QueueCardProps => ({
      job: { id: 'job-1', position: 2, status: 'Done', title: 'Done job', outputPath: 'C:/out/a.mp4' },
      onOpen: vi.fn(),
      isFirst: false,
      isLast: false,
      onOpenFile: vi.fn(),
      onOpenFolder: vi.fn(),
      onCopyLocation: vi.fn(),
      onMoveUp: vi.fn(),
      onMoveDown: vi.fn(),
      onMoveTop: vi.fn(),
      onMoveBottom: vi.fn(),
      onRemove: vi.fn(),
      drag: {
        attributes: { 'aria-roledescription': 'sortable', 'aria-describedby': 'DndDescribedBy-0' },
        listeners,
        setActivatorNodeRef: vi.fn(),
        isDragging: false,
        disabled,
      },
    })
    const cardView = render(createElement(QueueCard, cardProps(false)))
    const card = within(cardView.container).getByTestId('queue-card')
    const handle = within(card).getByTestId('queue-card-drag-handle')
    expect(within(card).getByTestId('queue-card-drag-handle-tip').contains(handle)).toBe(true)
    expect(tokens(handle), 'hidden: DndDescribedBy-0 kept').toEqual(['DndDescribedBy-0'])
    focusOn(handle)
    const handleHint = screen.queryByTestId('queue-card-drag-handle-hint')
    expect(handleHint, 'drag handle hint on focus').not.toBeNull()
    expect(tokens(handle), 'shown: DndDescribedBy-0 then the hint id').toEqual(['DndDescribedBy-0', handleHint?.id])
    blurFrom(handle)
    expect(tokens(handle), 'hidden again: DndDescribedBy-0 kept').toEqual(['DndDescribedBy-0'])
    fireEvent.pointerDown(handle)
    expect(listeners.onPointerDown, 'the pointer sensor still hears the press').toHaveBeenCalled()
    fireEvent.keyDown(handle, { key: ' ', code: 'Space' })
    expect(listeners.onKeyDown, 'the keyboard sensor still hears the key').toHaveBeenCalled()
    expectHinted(card, 'queue-card-drag-handle', 'Reorder Done job', 'drag handle enabled')
    const primary = within(card).getByTestId('queue-card-primary-action')
    expect(primary.getAttribute('title'), 'the labelled primary action keeps its title (AC-44.7)').toBe('C:/out/a.mp4')
    expect(within(card).queryByTestId('queue-card-primary-action-tip')).toBeNull()
    expectHinted(card, 'queue-card-kebab', 'Actions for Done job', 'kebab closed')
    const kebab = within(card).getByTestId('queue-card-kebab')
    focusOn(kebab)
    expect(screen.queryByTestId('queue-card-kebab-hint')).not.toBeNull()
    await user.click(kebab)
    expect(kebab.getAttribute('aria-expanded')).toBe('true')
    expect(screen.queryByTestId('queue-card-kebab-hint'), 'the open menu suppresses the kebab hint').toBeNull()
    focusOn(kebab)
    expect(kebab.getAttribute('aria-expanded')).toBe('true')
    expect(screen.queryByTestId('queue-card-kebab-hint'), 'focus while open shows nothing').toBeNull()
    cardView.unmount()
    const disabledView = render(createElement(QueueCard, cardProps(true)))
    const disabledCard = within(disabledView.container).getByTestId('queue-card')
    expect((within(disabledCard).getByTestId('queue-card-drag-handle') as HTMLButtonElement).disabled).toBe(true)
    expectHinted(disabledCard, 'queue-card-drag-handle', 'Reorder Done job', 'drag handle disabled')
    disabledView.unmount()

    // up-btn and down-btn: the first card's up and the last card's down are disabled.
    let host: HTMLElement | null = null
    await act(async () => {
      host = render(createElement(QueryClientProvider, { client: appQueryClient }, createElement(TranscriptPage))).container
    })
    const transcriptHost = host as unknown as HTMLElement
    await vi.waitFor(() => {
      expect(within(transcriptHost).getAllByTestId('channel-card')).toHaveLength(TRANSCRIPTS.length)
    })
    const channel = (name: string): HTMLElement =>
      within(transcriptHost)
        .getAllByTestId('channel-card')
        .find((node) => node.textContent?.includes(name)) as HTMLElement
    expect((within(channel('Alpha')).getByTestId('up-btn') as HTMLButtonElement).disabled).toBe(true)
    expectHinted(channel('Alpha'), 'up-btn', 'Move Alpha up', 'transcript first up')
    expectHinted(channel('Alpha'), 'down-btn', 'Move Alpha down', 'transcript first down')
    expectHinted(channel('Bravo'), 'up-btn', 'Move Bravo up', 'transcript middle up')
    expect((within(channel('Charlie')).getByTestId('down-btn') as HTMLButtonElement).disabled).toBe(true)
    expectHinted(channel('Charlie'), 'down-btn', 'Move Charlie down', 'transcript last down')
    cleanup()

    // convert-staged-remove: stage one file through Browse.
    await act(async () => {
      render(createElement(QueryClientProvider, { client: appQueryClient }, createElement(ConvertPage, null)))
    })
    await vi.waitFor(() => {
      expect((screen.getByTestId('convert-browse') as HTMLButtonElement).disabled).toBe(false)
    })
    await user.click(screen.getByTestId('convert-browse'))
    await vi.waitFor(() => {
      expect(screen.getAllByTestId('convert-staged-remove')).toHaveLength(1)
    })
    const remove = screen.getByTestId('convert-staged-remove')
    expect(remove.getAttribute('aria-label')).toBe('Remove staged file C:/e2e/sample.mp4')
    expectHinted(document.body, 'convert-staged-remove', 'Remove staged file C:/e2e/sample.mp4', 'convert')
  })
})
