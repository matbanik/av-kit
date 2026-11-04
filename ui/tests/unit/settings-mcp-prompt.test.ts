/** @vitest-environment jsdom */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { SettingsPage } from '../../src/renderer/src/features/settings/SettingsPage'
import { SETTINGS_ERROR_EVENT } from '../../src/renderer/src/features/settings/useSettingsPage'

// CLIENT_SET: value and label, in order.
const CLIENT_SET = [
  ['claude-code', 'Claude Code'],
  ['codex', 'Codex'],
  ['cursor', 'Cursor'],
  ['vscode', 'VS Code'],
  ['claude-desktop', 'Claude Desktop'],
  ['windsurf', 'Windsurf (community)'],
  ['generic', 'Other MCP client'],
] as const
const USER_ONLY = ['claude-desktop', 'windsurf', 'generic']
const PROMPT_UNAVAILABLE = 'The setup prompt is not available in this window.'

type PromptOpts = { client: string; scope: 'user' | 'project' }

function json(payload: unknown, status = 200): Response {
  return new Response(JSON.stringify(payload), { status, headers: { 'Content-Type': 'application/json' } })
}

function promptText(opts: PromptOpts): string {
  return `PROMPT for ${opts.client} at ${opts.scope} scope`
}

let getMcpSetupPrompt: ReturnType<typeof vi.fn> | undefined
let writeClipboardText: ReturnType<typeof vi.fn>

function mockApi(): void {
  window.api = {
    getBackendUrl: async () => 'http://127.0.0.1:51234/api/v1',
    getToken: async () => 'gui-nonce',
    logStartupMetric: () => undefined,
    showDirectoryDialog: async () => 'C:/e2e/outdir',
    showFileDialog: async () => 'C:/e2e/sample.txt',
    showFilesDialog: async () => [],
    getPathForFile: () => 'C:/e2e/sample.mp4',
    openPath: async () => undefined,
    showItemInFolder: async () => undefined,
    readClipboardText: async () => '',
    writeClipboardText,
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
    ...(getMcpSetupPrompt === undefined ? {} : { getMcpSetupPrompt }),
  } as Window['api']
}

function installFetch(): void {
  const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
    if (url.includes('/settings/downloader')) {
      return json({
        path: 'C:/Downloads/av-kit', quality: '1080p', audio_only: false, audio_format: 'default',
        cookie_mode: 'browser', cookie_browser: 'chrome', cookie_browser_profile: 'Default', cookie_file_path: '',
        archive_tracking: true, yt_dlp_debug: false, ffmpeg_path: 'C:/bin/ffmpeg.exe',
      })
    }
    if (url.includes('/settings/transcript')) {
      return json({
        output_dir: 'C:/Transcripts', requests_per_hour: 300, delay_between_requests: 6, max_retries: 3,
        retry_delay: 30, batch_size: 50, pause_between_batches: 300, playlist_end: 0, max_words_per_document: 490000,
      })
    }
    if (url.includes('/settings/tts')) {
      return json({
        models_directory: 'C:/models', voice: 'af_heart', speed: 1, output_format: 'MP3',
        output_path: 'C:/Documents', device: 'auto', chunk_max_chars: 250,
      })
    }
    if (url.includes('/settings/app')) return json({ log_level: 'INFO', log_to_file: false, console_visible: true })
    if (url.includes('/settings/ui')) return json({ theme: 'dark' })
    if (url.includes('/settings/converter')) {
      return json({ output_dir: '~/Videos/av-kit', default_preset: 'balanced', skip_existing: true, gpu_preference: 'auto' })
    }
    if (url.includes('/settings/capture')) {
      return json({ inbox_dir: 'C:/Pictures/av-kit', hotkey: 'F2', copy_to_clipboard: false, close_to_tray: true })
    }
    if (url.includes('/health/dependencies')) {
      return json({ yt_dlp: { available: true, version: '2026.08.30' }, ffmpeg: { available: true, version: '7.1' } })
    }
    return json({ error: { message: 'unexpected' } }, 422)
  })
  vi.stubGlobal('fetch', fetchMock)
  window.fetch = fetchMock as typeof window.fetch
}

let client: QueryClient
let user: ReturnType<typeof userEvent.setup>

async function renderPage(): Promise<void> {
  render(createElement(QueryClientProvider, { client }, createElement(SettingsPage)))
  await vi.waitFor(() => {
    expect(screen.queryByTestId('settings-page')).not.toBeNull()
  })
  await act(async () => {
    await new Promise((resolve) => setTimeout(resolve, 0))
  })
}

/** Returns the element for `testId`, failing by assertion when it is absent. */
function byTestId<T extends HTMLElement = HTMLElement>(testId: string): T {
  const element = screen.queryByTestId(testId)
  expect(element, testId).not.toBeNull()
  return element as T
}

function lastPromptCall(): PromptOpts | undefined {
  const calls = getMcpSetupPrompt?.mock.calls ?? []
  return calls.length === 0 ? undefined : (calls[calls.length - 1][0] as PromptOpts)
}

beforeEach(() => {
  getMcpSetupPrompt = vi.fn(async (opts: PromptOpts) => ({ text: promptText(opts) }))
  writeClipboardText = vi.fn(async () => undefined)
  client = new QueryClient({ defaultOptions: { queries: { retry: false, gcTime: 0 } } })
  user = userEvent.setup()
  mockApi()
  installFetch()
})

afterEach(() => {
  cleanup()
  client.clear()
  vi.unstubAllGlobals()
})

describe('MEU-71 Settings MCP card (AC-71.13)', () => {
  it('AC-71.13 CARD_LAYOUT: chip, client, scope, viewer, Copy prompt, status, then Advanced, in order', async () => {
    await renderPage()
    const card = byTestId('mcp-access-card')
    const order = [
      'mcp-token-present',
      'mcp-client-select',
      'mcp-scope-select',
      'mcp-setup-prompt',
      'mcp-copy-prompt-btn',
      'mcp-prompt-status',
      'mcp-advanced',
    ].map((id) => byTestId(id))
    for (const element of order) {
      expect(card.contains(element)).toBe(true)
    }
    for (let i = 1; i < order.length; i += 1) {
      const follows = order[i - 1].compareDocumentPosition(order[i]) & Node.DOCUMENT_POSITION_FOLLOWING
      expect(follows, `${order[i - 1].dataset.testid} before ${order[i].dataset.testid}`).not.toBe(0)
    }
    expect(screen.queryByLabelText('Client')).toBe(order[1])
    expect(screen.queryByLabelText('Scope')).toBe(order[2])
    const viewer = order[3] as HTMLTextAreaElement
    expect(viewer.tagName).toBe('TEXTAREA')
    expect(viewer.readOnly).toBe(true)
    expect(viewer.getAttribute('aria-label')).toBe('MCP setup prompt')
    expect(order[4].textContent).toBe('Copy prompt')
    expect(order[5].tagName).toBe('P')
    expect(order[5].getAttribute('role')).toBe('status')
  })

  it('AC-71.13 the client select lists CLIENT_SET in order; scope lists user then project', async () => {
    await renderPage()
    const clients = byTestId<HTMLSelectElement>('mcp-client-select')
    expect(Array.from(clients.options).map((o) => [o.value, o.textContent])).toEqual(CLIENT_SET.map(([v, l]) => [v, l]))
    const scopes = byTestId<HTMLSelectElement>('mcp-scope-select')
    expect(Array.from(scopes.options).map((o) => [o.value, o.textContent])).toEqual([
      ['user', 'User (all projects)'],
      ['project', 'This project only'],
    ])
  })

  it('AC-71.13 the prompt loads on mount and on each client or scope change; choosing Codex shows its text', async () => {
    await renderPage()
    const viewer = byTestId<HTMLTextAreaElement>('mcp-setup-prompt')
    const clients = byTestId<HTMLSelectElement>('mcp-client-select')
    await vi.waitFor(() => {
      expect(getMcpSetupPrompt).toHaveBeenCalled()
      expect(viewer.value).toBe(promptText({ client: clients.value, scope: 'user' }))
    })
    await user.selectOptions(clients, 'codex')
    await vi.waitFor(() => {
      expect(lastPromptCall()).toEqual({ client: 'codex', scope: 'user' })
      expect(viewer.value).toBe(promptText({ client: 'codex', scope: 'user' }))
    })
    await user.selectOptions(byTestId<HTMLSelectElement>('mcp-scope-select'), 'project')
    await vi.waitFor(() => {
      expect(lastPromptCall()).toEqual({ client: 'codex', scope: 'project' })
      expect(viewer.value).toBe(promptText({ client: 'codex', scope: 'project' }))
    })
  })

  it('AC-71.13 SCOPE_DISABLED: Claude Desktop, Windsurf and Other force user and disable scope; Codex re-enables it', async () => {
    await renderPage()
    const clients = byTestId<HTMLSelectElement>('mcp-client-select')
    const scope = byTestId<HTMLSelectElement>('mcp-scope-select')
    for (const userOnly of USER_ONLY) {
      await user.selectOptions(clients, 'codex')
      await user.selectOptions(scope, 'project')
      expect(scope.value).toBe('project')
      await user.selectOptions(clients, userOnly)
      await vi.waitFor(() => {
        expect(scope.value, userOnly).toBe('user')
        expect(scope.disabled, userOnly).toBe(true)
        expect(lastPromptCall()).toEqual({ client: userOnly, scope: 'user' })
      })
    }
    await user.selectOptions(clients, 'codex')
    await vi.waitFor(() => {
      expect(scope.disabled).toBe(false)
    })
  })

  it('AC-71.13 COPY_PROMPT: Copy prompt writes the viewer text once and shows the copied status', async () => {
    await renderPage()
    await user.selectOptions(byTestId<HTMLSelectElement>('mcp-client-select'), 'codex')
    const viewer = byTestId<HTMLTextAreaElement>('mcp-setup-prompt')
    await vi.waitFor(() => {
      expect(viewer.value).toBe(promptText({ client: 'codex', scope: 'user' }))
    })
    await user.click(byTestId('mcp-copy-prompt-btn'))
    await vi.waitFor(() => {
      expect(byTestId('mcp-prompt-status').textContent).toBe('Copied the Codex setup prompt.')
    })
    expect(writeClipboardText).toHaveBeenCalledTimes(1)
    expect(writeClipboardText).toHaveBeenCalledWith(viewer.value)
  })

  it('AC-71.13 ADVANCED_DISCLOSURE: copy-mcp-btn and pin-mcp-btn sit inside a closed Advanced; the token chip outside', async () => {
    await renderPage()
    const advanced = byTestId('mcp-advanced')
    expect(advanced.tagName).toBe('DETAILS')
    expect((advanced as HTMLDetailsElement).open).toBe(false)
    const summary = byTestId('mcp-advanced-summary')
    expect(summary.tagName).toBe('SUMMARY')
    expect(summary.textContent).toBe('Advanced')
    expect(advanced.contains(byTestId('copy-mcp-btn'))).toBe(true)
    expect(advanced.contains(byTestId('pin-mcp-btn'))).toBe(true)
    expect(advanced.contains(byTestId('mcp-token-present'))).toBe(false)
  })

  it('AC-71.13 negative: without getMcpSetupPrompt the viewer shows PROMPT_UNAVAILABLE and Copy is disabled', async () => {
    getMcpSetupPrompt = undefined
    mockApi()
    await renderPage()
    const viewer = byTestId<HTMLTextAreaElement>('mcp-setup-prompt')
    await vi.waitFor(() => {
      expect(viewer.value).toBe(PROMPT_UNAVAILABLE)
    })
    const copy = byTestId<HTMLButtonElement>('mcp-copy-prompt-btn')
    expect(copy.disabled).toBe(true)
    await user.click(copy)
    expect(writeClipboardText).toHaveBeenCalledTimes(0)
  })

  it('AC-71.13 negative: a rejecting getMcpSetupPrompt reports the settings error and nothing is copied', async () => {
    getMcpSetupPrompt = vi.fn(async () => {
      throw new Error('prompt-failure-s31b')
    })
    mockApi()
    const errors: Array<{ namespace: string; message: string }> = []
    const onError = (event: Event) => {
      errors.push((event as CustomEvent<{ namespace: string; message: string }>).detail)
    }
    window.addEventListener(SETTINGS_ERROR_EVENT, onError)
    try {
      await renderPage()
      await vi.waitFor(() => {
        expect(errors.some((e) => e.namespace === 'general' && e.message.includes('prompt-failure-s31b'))).toBe(true)
      })
      expect(getMcpSetupPrompt).toHaveBeenCalled()
      const viewer = byTestId<HTMLTextAreaElement>('mcp-setup-prompt')
      expect(viewer.value).not.toContain('PROMPT for')
      await user.click(byTestId('mcp-copy-prompt-btn'))
      expect(writeClipboardText).toHaveBeenCalledTimes(0)
    } finally {
      window.removeEventListener(SETTINGS_ERROR_EVENT, onError)
    }
  })
})
