/** @vitest-environment jsdom */

// MEU-165 (Session 103): the capture key in texts. AC-165.2 scans the renderer sources for the literal;
// guard AC-165.3 pins today's default readings; AC-165.5 to AC-165.7 render CapturePage with a saved key
// and a mocked hotkey status (CAPTURE_KEY_SAVED, CAPTURE_KEY_FOLLOW, CAPTURE_KEY_UNCONFIRMED); AC-165.8
// renders SettingsPage. The harness follows capture-inbox-scope.behavior.test.ts and
// settings-emphasis.test.tsx. It imports no name that MEU-165 adds.

import { act, cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { QueryClientProvider } from '@tanstack/react-query'
import userEvent from '@testing-library/user-event'
import { readdirSync, readFileSync } from 'node:fs'
import { dirname, join, relative, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { QUICK_START } from '../../src/renderer/src/components/help/quick-start'
import { CapturePage } from '../../src/renderer/src/features/capture/CapturePage'
import { CAPTURE_HELP_SECTIONS } from '../../src/renderer/src/features/capture/capture-help-content'
import { SettingsPage } from '../../src/renderer/src/features/settings/SettingsPage'
import { SETTINGS_HELP_SECTIONS } from '../../src/renderer/src/features/settings/settings-help-content'
import { queryClient as appQueryClient } from '../../src/renderer/src/lib/query-client'

type HotkeyStatus = { accelerator: string; registered: boolean; inUse: boolean }
type Call = { path: string; method: string; body?: unknown }

const RENDERER = resolve(dirname(fileURLToPath(import.meta.url)), '../../src/renderer/src')

/** The eight texts that name the capture key, as they read at HEAD e5028a3 (the default reading). */
const EMPTY_STATE_TODAY = 'Press F2 or Capture region'
const CAPTURE_TEXTS_TODAY = [
  'Press F2 or click Capture region to take a region of the screen. Capture keeps the PNG files in your inbox, and you can mark them. Capture never uploads.',
  'When F2 is in use',
  'If ShareX or a different tool uses F2, Capture shows a banner. Quit ShareX or pick a different key.',
  'Close to tray keeps F2',
  'When Close to tray is on and you close the window, the window hides. F2 still works. Click Quit in the tray menu to stop the app.',
] as const
const STARTUP_TODAY =
  'Start when I sign in adds a startup entry for your user only. It needs no administrator approval. Turn it off here or in Task Manager → Startup. Start minimized waits in the notification area, so F2 still works.'
const QUICK_STEP_TODAY = 'Push F2 or click Capture region. Then drag a box on the screen.'
const CAPTURE_IDS_TODAY = [
  'what-capture-does',
  'f2-sharex',
  'inbox-folder',
  'original-annotated',
  'four-tools',
  'mcp-png',
  'close-to-tray',
  'never-uploads',
]
const SETTINGS_IDS_TODAY = ['leaf-keys', 'ffmpeg', 'mcp', 'console', 'startup']

const token = (text: string): string => text.replace('F2', '{captureKey}')

function sourceFiles(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const path = join(dir, entry.name)
    if (entry.isDirectory()) {
      return sourceFiles(path)
    }
    return /\.(ts|tsx|json)$/.test(entry.name) ? [path] : []
  })
}

function source(path: string): string {
  return readFileSync(join(RENDERER, path), 'utf8')
}

describe('MEU-165 one source for the capture key', () => {
  it('AC-165.2 only the leaf, the settings defaults and the shortcut registry hold the literal F2', () => {
    const holders = sourceFiles(RENDERER)
      .filter((path) => /\bF2\b/.test(readFileSync(path, 'utf8')))
      .map((path) => relative(RENDERER, path).replaceAll('\\', '/'))
      .sort()
    expect(holders).toEqual([
      'features/capture/capture-key.ts',
      'features/capture/useCaptureSettings.ts',
      'registry/shortcuts.ts',
    ])
    expect(source('features/capture/CapturePage.tsx')).toContain(`'${token(EMPTY_STATE_TODAY)}'`)
    const captureHelp = source('features/capture/capture-help-content.ts')
    for (const text of CAPTURE_TEXTS_TODAY) {
      expect(captureHelp, text).toContain(`'${token(text)}'`)
    }
    expect(source('features/settings/settings-help-content.ts')).toContain(`'${token(STARTUP_TODAY)}'`)
    expect(source('components/help/quick-start.json')).toContain(`"text": "${token(QUICK_STEP_TODAY)}"`)
  })

  it('guard AC-165.3 the default readings equal today and hold no token', () => {
    expect(CAPTURE_HELP_SECTIONS.map((section) => section.id)).toEqual(CAPTURE_IDS_TODAY)
    expect(SETTINGS_HELP_SECTIONS.map((section) => section.id)).toEqual(SETTINGS_IDS_TODAY)
    const byId = (id: string) => CAPTURE_HELP_SECTIONS.find((section) => section.id === id)
    expect([
      byId('what-capture-does')?.body,
      byId('f2-sharex')?.title,
      byId('f2-sharex')?.body,
      byId('close-to-tray')?.title,
      byId('close-to-tray')?.body,
    ]).toEqual([...CAPTURE_TEXTS_TODAY])
    expect(SETTINGS_HELP_SECTIONS.find((section) => section.id === 'startup')?.body).toBe(STARTUP_TODAY)
    expect(QUICK_START.capture.steps[0]?.text).toBe(QUICK_STEP_TODAY)
    for (const reading of [CAPTURE_HELP_SECTIONS, SETTINGS_HELP_SECTIONS, QUICK_START]) {
      expect(JSON.stringify(reading)).not.toContain('{captureKey}')
    }
  })
})

describe('MEU-165 the pages show the saved capture key', () => {
  let user: ReturnType<typeof userEvent.setup>
  let saved: Record<string, unknown>
  let status: HotkeyStatus
  let refuse = false
  let statusReads = 0
  const calls: Call[] = []

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
      getHotkeyStatus: async () => {
        statusReads += 1
        if (refuse) {
          throw new Error('hotkey status refused')
        }
        return { ...status }
      },
      loginItemGet: async () => ({ supported: false, reason: 'not-packaged', enabled: false, minimized: false }),
      loginItemSet: async () => ({ supported: false, reason: 'not-packaged', enabled: false, minimized: false }),
      onInboxChanged: () => () => undefined,
    } as Window['api']
  }

  function setup(hotkey: string, current: HotkeyStatus): void {
    saved = {
      inbox_dir: 'C:/inbox-k',
      hotkey,
      copy_to_clipboard: false,
      close_to_tray: true,
      flatten_backup: true,
      backup_dir: '',
      annotated_format: 'png',
      tool_lock: false,
    }
    status = current
  }

  beforeEach(() => {
    calls.length = 0
    refuse = false
    statusReads = 0
    setup('F2', { accelerator: 'F2', registered: true, inUse: false })
    mockApi()
    URL.createObjectURL = vi.fn(() => 'blob:capture-shot')
    URL.revokeObjectURL = vi.fn()
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
      const method = (init?.method ?? 'GET').toUpperCase()
      const body = typeof init?.body === 'string' && init.body.length > 0 ? JSON.parse(init.body) : undefined
      const path = new URL(url).pathname
      calls.push({ path, method, body })
      const json = (payload: unknown) =>
        new Response(JSON.stringify(payload), { status: 200, headers: { 'Content-Type': 'application/json' } })
      if (path.includes('/settings/capture')) {
        if (method === 'PUT') {
          saved = { ...saved, ...(body as Record<string, unknown>) }
        }
        return json(saved)
      }
      if (path.includes('/settings/app')) return json({ log_level: 'INFO', log_to_file: false, console_visible: true })
      if (path.includes('/settings/ui')) return json({ theme: 'dark' })
      if (path.includes('/health/dependencies')) {
        return json({
          yt_dlp: { available: true, version: '2026.11.23' },
          ffmpeg: { available: true, version: '7.1', path: 'C:/ffmpeg.exe' },
        })
      }
      if (path.includes('/captures')) return json({ items: [] })
      return json({})
    })
    vi.stubGlobal('fetch', fetchMock)
    window.fetch = fetchMock as typeof window.fetch
  })

  afterEach(() => {
    cleanup()
    // A help card keeps its open state in localStorage; each test starts with every card closed.
    localStorage.clear()
    vi.useRealTimers()
    appQueryClient.clear()
    vi.unstubAllGlobals()
  })

  function present<T extends HTMLElement = HTMLElement>(id: string): T {
    const node = screen.queryByTestId(id)
    expect(node, `${id} rendered`).not.toBeNull()
    return node as T
  }

  const keyCap = (): string | null => screen.queryByTestId('capture-hotkey-keycap')?.textContent ?? null
  const banner = (): string | null => screen.queryByTestId('capture-hotkey-banner')?.textContent ?? null
  const emptyText = (): string => screen.queryByTestId('capture-empty')?.textContent ?? ''
  const unconfirmed = (key: string): string =>
    `${key} is saved, but av-kit cannot confirm it works. Restart av-kit if ${key} does nothing.`

  async function step(ms: number): Promise<void> {
    await act(async () => {
      await vi.advanceTimersByTimeAsync(ms)
    })
  }

  async function settle(ms = 40): Promise<void> {
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, ms))
    })
  }

  async function renderCapture(): Promise<void> {
    render(createElement(QueryClientProvider, { client: appQueryClient }, createElement(CapturePage)))
    await waitFor(() => {
      expect(emptyText()).not.toBe('')
      expect(statusReads).toBeGreaterThan(0)
    })
    await settle()
  }

  async function draftKey(key: string): Promise<void> {
    if (screen.queryByTestId('capture-hotkey') === null) {
      await user.click(present('capture-settings-toggle'))
    }
    await user.click(present('capture-hotkey-change'))
    fireEvent.keyDown(present('capture-hotkey'), { key })
    await waitFor(() => {
      expect(present<HTMLInputElement>('capture-hotkey').value).toBe(key)
    })
  }

  async function openHelp(): Promise<HTMLElement> {
    const card = screen.getAllByTestId('help-card')[0] as HTMLElement
    await user.click(within(card).getByRole('button', { name: /How it works/ }))
    return card
  }

  /** Starts on F2, drafts F9 (no text changes), saves, and waits for the read the saved key change makes. */
  async function saveF9(): Promise<{ emptyNode: HTMLElement; keyRead: number }> {
    await renderCapture()
    await waitFor(() => {
      expect(keyCap()).toBe('F2')
    })
    await draftKey('F9')
    await settle()
    expect(emptyText()).toBe('Press F2 or Capture region')
    expect(keyCap()).toBe('F2')
    const emptyNode = present('capture-empty')
    const before = statusReads
    await user.click(present('capture-page-save'))
    await waitFor(() => {
      expect(calls.filter((call) => call.method === 'PUT').map((call) => call.body)).toEqual([{ hotkey: 'F9' }])
    })
    await waitFor(() => {
      expect(emptyText()).toBe('Press F9 or Capture region')
    })
    expect(present('capture-empty'), 'the same page, no remount').toBe(emptyNode)
    await waitFor(() => {
      expect(statusReads).toBeGreaterThan(before)
    })
    await settle(0)
    return { emptyNode, keyRead: statusReads }
  }

  it('AC-165.5 a saved key F9 shows F9 in every text, the key cap and the help card', async () => {
    user = userEvent.setup()
    setup('F9', { accelerator: 'F9', registered: true, inUse: false })
    await renderCapture()
    await waitFor(() => {
      expect(emptyText()).toBe('Press F9 or Capture region')
    })
    await waitFor(() => {
      expect(keyCap()).toBe('F9')
    })
    const card = await openHelp()
    const steps = within(card).getAllByTestId('help-quick-start-step')
    expect(steps[0]?.textContent).toBe('Push F9 or click Capture region. Then drag a box on the screen.')
    const topics = Array.from(card.querySelectorAll('[data-help-section] summary')).map((node) => node.textContent)
    expect(topics).toContain('When F9 is in use')
    expect(topics).toContain('Close to tray keeps F9')
    expect(document.body.textContent ?? '').not.toMatch(/\bF2\b/)
  })

  describe('the status follow', () => {
    beforeEach(() => {
      vi.useFakeTimers({ shouldAdvanceTime: true })
      user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
    })

    it('AC-165.6 a draft changes nothing; after Save the texts follow and the cap waits for a match', async () => {
      const { keyRead } = await saveF9()
      expect(keyCap(), 'no cap while the status names F2').toBeNull()
      expect(banner()).toBeNull()
      await step(500)
      expect(statusReads).toBe(keyRead + 1)
      await step(500)
      expect(statusReads).toBe(keyRead + 2)
      expect(keyCap()).toBeNull()
      status = { accelerator: 'F9', registered: true, inUse: false }
      await step(500)
      expect(statusReads).toBe(keyRead + 3)
      expect(keyCap()).toBe('F9')
      await step(3000)
      expect(statusReads, 'the reads stop on a match').toBe(keyRead + 3)
      expect(banner()).toBeNull()
    })

    it('AC-165.6 a status that never matches ends after ten follow reads with the unconfirmed notice', async () => {
      const { keyRead } = await saveF9()
      for (let read = 1; read <= 10; read += 1) {
        expect(banner(), `no notice while the follow runs (before read ${read})`).toBeNull()
        await step(500)
        expect(statusReads).toBe(keyRead + read)
      }
      expect(banner()).toContain(unconfirmed('F9'))
      expect(keyCap()).toBeNull()
      await step(5000)
      expect(statusReads, 'no read after the tenth').toBe(keyRead + 10)
      expect(banner()).toContain(unconfirmed('F9'))
    })

    it('AC-165.6 a refused status read after the save shows the notice at once', async () => {
      const { keyRead } = await saveF9()
      refuse = true
      await step(500)
      expect(statusReads).toBe(keyRead + 1)
      expect(banner()).toContain(unconfirmed('F9'))
      expect(keyCap()).toBeNull()
    })

    it('AC-165.6 an unmount stops the follow reads', async () => {
      const { keyRead } = await saveF9()
      await step(500)
      expect(statusReads).toBe(keyRead + 1)
      cleanup()
      await step(5000)
      expect(statusReads).toBe(keyRead + 1)
    })
  })

  it('AC-165.7 the in-use banner names the saved key, not the draft', async () => {
    user = userEvent.setup()
    setup('F9', { accelerator: 'F9', registered: false, inUse: true })
    await renderCapture()
    await waitFor(() => {
      expect(banner()).toContain('F9 is in use — quit ShareX or pick another key')
    })
    expect(keyCap()).toBeNull()
    await draftKey('F10')
    await settle()
    expect(banner()).toContain('F9 is in use — quit ShareX or pick another key')
    expect(banner()).not.toContain('F10')
  })

  /** Renders SettingsPage once the capture settings answered, opens its help card, and reads the startup topic. */
  async function startupTopic(): Promise<() => string> {
    render(createElement(QueryClientProvider, { client: appQueryClient }, createElement(SettingsPage)))
    await waitFor(() => {
      expect(screen.getByTestId('settings-page')).toBeTruthy()
      expect(calls.some((call) => call.path.includes('/settings/capture'))).toBe(true)
    })
    await settle()
    const card = await openHelp()
    return () => card.querySelector('[data-help-section="startup"] p')?.textContent ?? ''
  }

  it('AC-165.8 the Settings startup help names the saved capture key', async () => {
    user = userEvent.setup()
    setup('F9', { accelerator: 'F9', registered: true, inUse: false })
    const topic = await startupTopic()
    await waitFor(() => {
      expect(topic()).toMatch(/so F9 still works\.$/)
    })
  })

  it('guard AC-165.8 with the default key the startup help ends so F2 still works', async () => {
    user = userEvent.setup()
    const topic = await startupTopic()
    await settle()
    expect(topic()).toMatch(/so F2 still works\.$/)
  })
})
