/** @vitest-environment jsdom */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { SettingsPage } from '../../src/renderer/src/features/settings/SettingsPage'
import { revealSection } from '../../src/renderer/src/features/settings/SettingsRail'
import {
  CHECKBOX_COPY_SOURCES,
  NUMBER_HINT_SOURCES,
  SAVE_MODE_CAPTIONS,
  SETTINGS_SECTION_SET,
  readinessCount,
} from '../../src/renderer/src/features/settings/settings-sections'

type Call = { url: string; method: string; body?: unknown }

function json(payload: unknown, status = 200): Response {
  return new Response(JSON.stringify(payload), { status, headers: { 'Content-Type': 'application/json' } })
}

type Readiness = { descriptorPresent: boolean; portOk: boolean; modelsDirWritable: boolean; logFilePath?: string }

function mockApi(overrides: Partial<Window['api']> = {}): void {
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
    writeClipboardText: async () => undefined,
    readTextFile: async () => ({ text: '', basename: 'x.txt' }),
    copyMcpConfig: async () => ({ ok: true as const }),
    subscribeLogs: () => () => undefined,
    getLogSnapshot: async () => [],
    getSetupReadiness: async (): Promise<Readiness> => ({
      descriptorPresent: true,
      portOk: true,
      modelsDirWritable: false,
      logFilePath: 'C:/Users/test/AppData/Local/av-kit/logs/console.log',
    }),
    getMcpAccessStatus: async () => ({ tokenPresent: true }),
    captureRegion: async () => undefined,
    getHotkeyStatus: async () => ({ accelerator: 'F2', registered: true, inUse: false }),
    loginItemGet: async () => ({ supported: false, reason: 'not-packaged', enabled: false, minimized: false }),
    loginItemSet: async () => ({ supported: false, reason: 'not-packaged', enabled: false, minimized: false }),
    onInboxChanged: () => () => undefined,
    ...overrides,
  } as Window['api']
}

const calls: Call[] = []
let deps: unknown = { yt_dlp: { available: true, version: '2026.08.30' }, ffmpeg: { available: true, version: '7.1', path: 'C:/ffmpeg/bin/ffmpeg.exe' } }

function installFetch(): void {
  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
    const method = (init?.method ?? 'GET').toUpperCase()
    const body = typeof init?.body === 'string' && init.body.length > 0 ? JSON.parse(init.body) : undefined
    calls.push({ url, method, body })
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
    if (url.includes('/health/dependencies')) return json(deps)
    if (url.includes('/downloads/apply-defaults')) return new Response(null, { status: 204 })
    return json({ error: { message: 'unexpected' } }, 422)
  })
  vi.stubGlobal('fetch', fetchMock)
  window.fetch = fetchMock as typeof window.fetch
}

function puts(fragment: string): Call[] {
  return calls.filter((row) => row.method === 'PUT' && row.url.includes(fragment))
}

let client: QueryClient
let user: ReturnType<typeof userEvent.setup>

async function renderPage(): Promise<void> {
  render(createElement(QueryClientProvider, { client }, createElement(SettingsPage)))
  await vi.waitFor(() => {
    expect(screen.getByTestId('settings-page')).toBeTruthy()
  })
}

async function settle(): Promise<void> {
  await act(async () => {
    await new Promise((resolve) => setTimeout(resolve, 0))
  })
}

beforeEach(() => {
  calls.length = 0
  deps = { yt_dlp: { available: true, version: '2026.08.30' }, ffmpeg: { available: true, version: '7.1', path: 'C:/ffmpeg/bin/ffmpeg.exe' } }
  client = new QueryClient({ defaultOptions: { queries: { retry: false, gcTime: 0 } } })
  user = userEvent.setup()
  mockApi()
  installFetch()
})

afterEach(() => {
  cleanup()
  client.clear()
  vi.unstubAllGlobals()
  vi.useRealTimers()
})

describe('MEU-58 settings section table (single-statement contracts)', () => {
  it('AC-58.2 SETTINGS_SECTION_SET lists the 11 live sections in DOM order with rail groups and save modes', () => {
    expect(SETTINGS_SECTION_SET.map((s) => [s.key, s.testId, s.group, s.mode])).toEqual([
      ['download', 'download-settings', 'Pages', 'autosave'],
      ['transcript', 'transcript-settings', 'Pages', 'autosave'],
      ['tts', 'tts-settings', 'Pages', 'autosave'],
      ['convert', 'convert-settings', 'Pages', 'explicit'],
      ['capture', 'capture-settings', 'Pages', 'explicit'],
      ['console', 'console-settings', 'App', 'autosave'],
      ['appearance', 'appearance-settings', 'App', 'immediate'],
      ['startup', 'start-at-sign-in-panel', 'App', 'immediate-os'],
      ['dependencies', 'dependencies-section', 'Setup', 'none'],
      ['readiness', 'readiness-card', 'Setup', 'readiness-count'],
      ['mcp', 'mcp-access-card', 'Setup', 'none'],
    ])
  })

  it('AC-58.4 SAVE_MODE_CAPTIONS wording is exactly the four labelled modes', () => {
    expect(SAVE_MODE_CAPTIONS).toEqual({
      autosave: 'Saves as you type',
      explicit: 'Save required',
      immediate: 'Applies immediately',
      'immediate-os': 'Applies immediately (OS)',
    })
  })

  it('AC-58.5 AC-58.7 hint and explanation copy is limited to the sourced tables', () => {
    expect(NUMBER_HINT_SOURCES).toEqual({
      delay_between_requests: 'seconds',
      retry_delay: 'seconds',
      pause_between_batches: 'seconds',
      playlist_end: '0 = no limit',
      max_words_per_document: 'Split compiled Markdown at this word count',
      chunk_max_chars: 'Smart TTS chunking threshold',
    })
    expect(CHECKBOX_COPY_SOURCES).toEqual({
      archive_tracking: 'Skip previously downloaded videos',
      yt_dlp_debug: 'Show yt-dlp debug messages in console',
      console_visible: 'Show console panel on startup',
      copy_to_clipboard: 'After successful save',
    })
  })

  it('AC-58.9 READINESS_COUNT is null until both sources load and counts true values', () => {
    expect(readinessCount(undefined, true)).toBeNull()
    expect(readinessCount({ descriptorPresent: true, portOk: true, modelsDirWritable: true }, undefined)).toBeNull()
    expect(readinessCount({ descriptorPresent: true, portOk: false, modelsDirWritable: true }, true)).toEqual({ ready: 3, total: 4 })
    expect(readinessCount({ descriptorPresent: false, portOk: false, modelsDirWritable: false }, false)).toEqual({ ready: 0, total: 4 })
  })
})

describe('MEU-58 settings page layout', () => {
  it('AC-58.1 two-column 960px grid: rail then content column with h1, HelpCard, error and all sections', async () => {
    await renderPage()
    const page = screen.getByTestId('settings-page')
    expect(page.className).toContain('max-w-[60rem]')
    expect(page.className).not.toContain('max-w-3xl')
    expect(page.className).toMatch(/grid-cols-\[11rem_minmax\(0,1fr\)\]/)
    const rail = screen.getByTestId('settings-rail')
    const heading = screen.getByRole('heading', { level: 1, name: 'Settings' })
    expect(rail.compareDocumentPosition(heading) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    for (const section of SETTINGS_SECTION_SET.filter((s) => s.key !== 'startup')) {
      expect(screen.getByTestId(section.testId), section.key).toBeTruthy()
    }
  })

  it('AC-58.2 rail has three labelled groups; startup entry is absent while the panel is unsupported', async () => {
    await renderPage()
    await settle()
    const rail = screen.getByTestId('settings-rail')
    expect(rail.tagName).toBe('NAV')
    expect(rail.textContent).toMatch(/Pages[\s\S]*App[\s\S]*Setup/)
    for (const section of SETTINGS_SECTION_SET.filter((s) => s.key !== 'startup')) {
      expect(screen.getByTestId(`settings-rail-${section.key}`), section.key).toBeTruthy()
    }
    expect(screen.queryByTestId('settings-rail-startup')).toBeNull()
    expect(screen.queryByTestId('start-at-sign-in-panel')).toBeNull()
  })

  it('AC-58.2 a supported login item shows the startup rail entry and panel', async () => {
    mockApi({
      loginItemGet: async () => ({ supported: true, enabled: false, minimized: false, startMinimizedSupported: true }),
    } as Partial<Window['api']>)
    await renderPage()
    await vi.waitFor(() => {
      expect(screen.getByTestId('settings-rail-startup')).toBeTruthy()
    })
    expect(screen.getByTestId('start-at-sign-in-panel')).toBeTruthy()
    expect(screen.getByTestId('settings-mode-startup').textContent).toBe('Applies immediately (OS)')
  })

  it('AC-58.2 AC-58.3 activation scrolls and focuses the section with no write; fallback without IntersectionObserver', async () => {
    expect(typeof IntersectionObserver).toBe('undefined')
    const scrolled: string[] = []
    const original = HTMLElement.prototype.scrollIntoView
    HTMLElement.prototype.scrollIntoView = function scrollIntoView(this: HTMLElement) {
      scrolled.push(this.getAttribute('data-testid') ?? '')
    }
    try {
      await renderPage()
      await settle()
      expect(screen.getByTestId('settings-rail-download').getAttribute('aria-current')).toBe('location')
      const before = calls.filter((row) => row.method !== 'GET').length
      await user.click(screen.getByTestId('settings-rail-mcp'))
      expect(scrolled).toContain('mcp-access-card')
      expect(document.activeElement).toBe(screen.getByTestId('mcp-access-card'))
      expect(screen.getByTestId('settings-rail-mcp').getAttribute('aria-current')).toBe('location')
      expect(screen.getByTestId('settings-rail-download').getAttribute('aria-current')).toBeNull()
      screen.getByTestId('settings-rail-transcript').focus()
      await user.keyboard('{Enter}')
      expect(scrolled).toContain('transcript-settings')
      expect(calls.filter((row) => row.method !== 'GET').length).toBe(before)
      expect(document.querySelectorAll('[aria-current="location"]')).toHaveLength(1)
    } finally {
      HTMLElement.prototype.scrollIntoView = original
    }
  })

  it('AC-58.3 IntersectionObserver drives the current entry and disconnects on unmount', async () => {
    const observers: Array<{ callback: IntersectionObserverCallback; targets: Element[]; disconnected: boolean }> = []
    class FakeObserver {
      record: { callback: IntersectionObserverCallback; targets: Element[]; disconnected: boolean }
      constructor(callback: IntersectionObserverCallback) {
        this.record = { callback, targets: [], disconnected: false }
        observers.push(this.record)
      }
      observe(target: Element): void { this.record.targets.push(target) }
      unobserve(): void {}
      disconnect(): void { this.record.disconnected = true }
      takeRecords(): IntersectionObserverEntry[] { return [] }
    }
    vi.stubGlobal('IntersectionObserver', FakeObserver)
    const view = render(createElement(QueryClientProvider, { client }, createElement(SettingsPage)))
    await settle()
    const live = observers.at(-1)
    expect(live).toBeDefined()
    const mcp = screen.getByTestId('mcp-access-card')
    expect(live?.targets).toContain(mcp)
    await act(async () => {
      live?.callback(
        live.targets.map((target) => ({ target, isIntersecting: target === mcp }) as unknown as IntersectionObserverEntry),
        {} as IntersectionObserver,
      )
    })
    expect(screen.getByTestId('settings-rail-mcp').getAttribute('aria-current')).toBe('location')
    expect(document.querySelectorAll('[aria-current="location"]')).toHaveLength(1)
    view.unmount()
    expect(live?.disconnected).toBe(true)
  })

  it('AC-58.3 a crossing dropped during the click lock is reconciled when the lock expires', async () => {
    const observers: Array<{ callback: IntersectionObserverCallback; targets: Element[] }> = []
    class FakeObserver {
      record: { callback: IntersectionObserverCallback; targets: Element[] }
      constructor(callback: IntersectionObserverCallback) {
        this.record = { callback, targets: [] }
        observers.push(this.record)
      }
      observe(target: Element): void { this.record.targets.push(target) }
      unobserve(): void {}
      disconnect(): void {}
      takeRecords(): IntersectionObserverEntry[] { return [] }
    }
    vi.stubGlobal('IntersectionObserver', FakeObserver)
    render(createElement(QueryClientProvider, { client }, createElement(SettingsPage)))
    await settle()
    const live = observers.at(-1)
    const mcp = screen.getByTestId('mcp-access-card')
    vi.useFakeTimers({ toFake: ['setTimeout', 'clearTimeout', 'Date'] })
    act(() => {
      fireEvent.click(screen.getByTestId('settings-rail-tts'))
    })
    expect(screen.getByTestId('settings-rail-tts').getAttribute('aria-current')).toBe('location')
    act(() => {
      live?.callback(
        live.targets.map((target) => ({ target, isIntersecting: target === mcp }) as unknown as IntersectionObserverEntry),
        {} as IntersectionObserver,
      )
    })
    expect(screen.getByTestId('settings-rail-tts').getAttribute('aria-current')).toBe('location')
    act(() => {
      vi.advanceTimersByTime(1000)
    })
    expect(screen.getByTestId('settings-rail-mcp').getAttribute('aria-current')).toBe('location')
    expect(document.querySelectorAll('[aria-current="location"]')).toHaveLength(1)
  })

  it('AC-58.4 captions per section and unchanged persistence per save model', async () => {
    await renderPage()
    await settle()
    for (const section of SETTINGS_SECTION_SET) {
      if (section.mode === 'none' || section.mode === 'readiness-count' || section.key === 'startup') continue
      expect(screen.getByTestId(`settings-mode-${section.key}`).textContent, section.key).toBe(
        SAVE_MODE_CAPTIONS[section.mode],
      )
    }
    expect(screen.queryByTestId('settings-mode-dependencies')).toBeNull()
    expect(screen.queryByTestId('settings-mode-mcp')).toBeNull()
    const outDir = screen.getByTestId('settings-leaf-converter-output_dir')
    await user.clear(outDir)
    await user.type(outDir, 'C:/Videos/next')
    await settle()
    expect(puts('/settings/converter')).toHaveLength(0)
    await user.click(screen.getByTestId('convert-settings-save'))
    await vi.waitFor(() => {
      expect(puts('/settings/converter')).toHaveLength(1)
    })
    await user.click(screen.getByTestId('theme-light-btn'))
    await vi.waitFor(() => {
      expect(puts('/settings/ui')).toHaveLength(1)
    })
  })

  it('AC-58.5 each leaf has exactly one label; path rows pair field and Browse; read-only paths stay read-only', async () => {
    await renderPage()
    await settle()
    for (const [leaf, label] of [
      ['settings-leaf-quality', 'Quality'], ['settings-leaf-log_level', 'Log level'],
      ['settings-leaf-device', 'Device'], ['settings-leaf-default_preset', 'Default preset'],
      ['settings-leaf-requests_per_hour', 'Requests per hour'], ['settings-leaf-voice', 'Voice'],
    ] as const) {
      expect(screen.getAllByLabelText(label, { exact: true }), leaf).toEqual([screen.getByTestId(leaf)])
    }
    for (const [leaf, browse, readOnly] of [
      ['settings-leaf-path', 'browse-download-path-btn', true],
      ['settings-leaf-ffmpeg_path', 'browse-ffmpeg-btn', true],
      ['settings-leaf-output_dir', 'browse-transcript-dir-btn', true],
      ['settings-leaf-models_directory', 'browse-models-dir-btn', true],
      ['settings-leaf-output_path', 'browse-tts-output-btn', true],
      ['settings-leaf-converter-output_dir', 'browse-convert-path-btn', false],
      ['settings-leaf-capture-inbox_dir', 'browse-capture-path-btn', false],
    ] as const) {
      const input = screen.getByTestId(leaf) as HTMLInputElement
      expect(input.readOnly, leaf).toBe(readOnly)
      expect(input.parentElement?.contains(screen.getByTestId(browse)), leaf).toBe(true)
    }
    const hinted = screen.getByTestId('settings-leaf-delay_between_requests')
    expect(document.getElementById(hinted.getAttribute('aria-describedby') ?? '')?.textContent).toBe('seconds')
    expect(screen.getByTestId('settings-leaf-requests_per_hour').getAttribute('aria-describedby')).toBeNull()
    for (const leaf of ['requests_per_hour', 'delay_between_requests', 'playlist_end', 'chunk_max_chars']) {
      const input = screen.getByTestId(`settings-leaf-${leaf}`)
      expect(input.getAttribute('min'), leaf).toBeNull()
      expect(input.getAttribute('max'), leaf).toBeNull()
      expect(input.className, leaf).toMatch(/w-\[5\.25rem\]/)
    }
    const speed = screen.getByTestId('settings-leaf-speed')
    expect([speed.getAttribute('min'), speed.getAttribute('max'), speed.getAttribute('step')]).toEqual(['0.5', '2', '0.1'])
  })

  it('AC-58.6 cookie mode is a native-radio segment; the label click sends one PUT with cookie_mode only', async () => {
    await renderPage()
    await settle()
    const group = screen.getByTestId('settings-leaf-cookie_mode')
    expect(group.tagName).toBe('FIELDSET')
    const file = screen.getByTestId('settings-leaf-cookie_mode-file') as HTMLInputElement
    expect(file.type).toBe('radio')
    // Sync-only setup repair: wait for the downloader query before reading its sub-fields.
    await vi.waitFor(() => {
      expect(screen.getByTestId('settings-leaf-cookie_browser')).toBeTruthy()
    })
    expect(screen.queryByTestId('settings-leaf-cookie_file_path')).toBeNull()
    await user.click(file.closest('label') as HTMLElement)
    await vi.waitFor(() => {
      expect(puts('/settings/downloader')).toHaveLength(1)
    })
    expect(puts('/settings/downloader')[0]?.body).toEqual({ cookie_mode: 'file' })
  })

  it('AC-58.6 the cookie mode group keeps its visible name as its accessible name', async () => {
    await renderPage()
    await settle()
    expect(screen.getByRole('group', { name: 'Cookie mode' })).toBe(screen.getByTestId('settings-leaf-cookie_mode'))
    // ST1 adoption: the SegmentedControl contract pairs each radio with its label by id.
    for (const mode of ['none', 'browser', 'file']) {
      const radio = screen.getByTestId(`settings-leaf-cookie_mode-${mode}`) as HTMLInputElement
      expect(radio.id).toBe(`settings-cookie-mode-${mode}`)
      expect(radio.closest('label')?.htmlFor).toBe(radio.id)
    }
  })

  it('AC-58.7 explanations only from CHECKBOX_COPY_SOURCES; audio format stays enabled with audio only off', async () => {
    await renderPage()
    await settle()
    for (const [leaf, copy] of Object.entries(CHECKBOX_COPY_SOURCES)) {
      const box = screen.getByTestId(`settings-leaf-${leaf}`)
      expect(document.getElementById(box.getAttribute('aria-describedby') ?? '')?.textContent, leaf).toBe(copy)
    }
    for (const leaf of ['skip_existing', 'close_to_tray', 'audio_only']) {
      expect(screen.getByTestId(`settings-leaf-${leaf}`).getAttribute('aria-describedby'), leaf).toBeNull()
    }
    expect((screen.getByTestId('settings-leaf-audio_only') as HTMLInputElement).checked).toBe(false)
    expect((screen.getByTestId('settings-leaf-audio_format') as HTMLSelectElement).disabled).toBe(false)
  })

  it('AC-58.8 explicit-save footers keep their label/class; rail dots follow each draft', async () => {
    await renderPage()
    await settle()
    const save = screen.getByTestId('convert-settings-save')
    expect(save.className).toMatch(/h-7/)
    expect(save.textContent).toBe('Save')
    expect(screen.queryByTestId('settings-rail-dot-convert')).toBeNull()
    expect(screen.queryByTestId('settings-rail-dot-capture')).toBeNull()
    await user.type(screen.getByTestId('settings-leaf-converter-output_dir'), '2')
    expect(save.textContent).toBe('Save Changes •')
    expect(save.className).toContain('btn-save-dirty')
    expect(screen.getByTestId('settings-rail-dot-convert')).toBeTruthy()
    await user.type(screen.getByTestId('settings-leaf-hotkey'), 'X')
    expect(screen.getByTestId('settings-rail-dot-capture')).toBeTruthy()
    await user.click(save)
    await vi.waitFor(() => {
      expect(screen.queryByTestId('settings-rail-dot-convert')).toBeNull()
    })
  })

  it('AC-58.9 no count, dot or missing chip before readiness loads', async () => {
    mockApi({ getSetupReadiness: () => new Promise(() => undefined) } as Partial<Window['api']>)
    await renderPage()
    await settle()
    expect(screen.queryByTestId('settings-readiness-count')).toBeNull()
    expect(screen.queryByTestId('settings-rail-dot-readiness')).toBeNull()
    const card = screen.getByTestId('readiness-card')
    expect(card.querySelector('[data-tone="warning"]')).toBeNull()
    expect(card.textContent).toMatch(/checking/i)
  })

  it('AC-58.9 loaded readiness: count, rail dot, chips, Fix only on failing rows; dependency and MCP chips', async () => {
    await renderPage()
    await vi.waitFor(() => {
      expect(screen.getByTestId('settings-readiness-count').textContent).toBe('3 of 4 ready')
    })
    expect(screen.getByTestId('settings-rail-dot-readiness')).toBeTruthy()
    expect(screen.queryByTestId('readiness-descriptor-link')).toBeNull()
    expect(screen.getByTestId('readiness-models-link')).toBeTruthy()
    const card = screen.getByTestId('readiness-card')
    expect(card.querySelectorAll('[data-tone="success"]')).toHaveLength(3)
    expect(card.querySelectorAll('[data-tone="warning"]')).toHaveLength(1)
    const deps = screen.getByTestId('dependencies-section')
    expect(deps.textContent).toContain('2026.08.30')
    expect(deps.textContent).toContain('C:/ffmpeg/bin/ffmpeg.exe')
    expect(deps.querySelectorAll('[data-tone="success"]')).toHaveLength(2)
    const token = screen.getByTestId('mcp-token-present')
    await vi.waitFor(() => {
      expect(token.textContent).toBe('Token present: yes')
    })
    expect(token.getAttribute('data-tone')).toBe('success')
    expect(document.body.textContent).not.toMatch(/gui-nonce/)
  })

  it('AC-58.9 all four ready shows 4 of 4 and no readiness dot', async () => {
    mockApi({
      getSetupReadiness: async () => ({ descriptorPresent: true, portOk: true, modelsDirWritable: true }),
    } as Partial<Window['api']>)
    await renderPage()
    await vi.waitFor(() => {
      expect(screen.getByTestId('settings-readiness-count').textContent).toBe('4 of 4 ready')
    })
    expect(screen.queryByTestId('settings-rail-dot-readiness')).toBeNull()
  })

  it('AC-58.13 Apply defaults footer, one-row log path with hint, theme segment with aria-pressed', async () => {
    await renderPage()
    await settle()
    const apply = screen.getByTestId('apply-defaults-btn')
    expect(apply.className).toContain('btn-ghost')
    expect(apply.className).toMatch(/h-7/)
    await user.click(apply)
    await vi.waitFor(() => {
      expect(calls.filter((row) => row.method === 'POST' && row.url.includes('/downloads/apply-defaults'))).toHaveLength(1)
    })
    const logRow = screen.getByTestId('settings-leaf-log_to_file').closest('[data-testid="settings-log-row"]')
    expect(logRow?.contains(screen.getByTestId('settings-log-file-path'))).toBe(true)
    expect(logRow?.contains(screen.getByTestId('settings-copy-log-path'))).toBe(true)
    expect(screen.getByTestId('settings-log-file-path').textContent).toContain('logs/console.log')
    await vi.waitFor(() => {
      expect(screen.getByTestId('theme-dark-btn').getAttribute('aria-pressed')).toBe('true')
    })
    expect(screen.getByTestId('theme-light-btn').getAttribute('aria-pressed')).toBe('false')
  })
})

// MEU-70 (Session 31) — appended. SCROLL_RECHECK and TAIL_SPACER are defined once in
// docs/execution/plans/2026-10-10-gui-polish-residuals/implementation-plan.md.

/** Render the page inside a scrolling `main`, as AppShell does, so the rail finds its scroller. */
function renderInScroller(): { main: HTMLElement; unmount: () => void } {
  const view = render(
    createElement(
      'main',
      { style: { overflowY: 'auto' }, 'data-testid': 'scroller' },
      createElement(QueryClientProvider, { client }, createElement(SettingsPage)),
    ),
  )
  return { main: screen.getByTestId('scroller'), unmount: view.unmount }
}

function stubBox(element: Element, top: number, height = 100): void {
  Object.defineProperty(element, 'getBoundingClientRect', {
    configurable: true,
    value: () => ({ top, bottom: top + height, left: 0, right: 800, width: 800, height, x: 0, y: top, toJSON: () => ({}) }),
  })
}

function stubScroller(main: HTMLElement, metrics: { scrollHeight: number; clientHeight: number; scrollTop: number }): void {
  for (const [key, value] of Object.entries(metrics)) {
    Object.defineProperty(main, key, { configurable: true, writable: true, value })
  }
  stubBox(main, 0, metrics.clientHeight)
}

async function nextFrames(): Promise<void> {
  await act(async () => {
    await new Promise((resolve) => setTimeout(resolve, 50))
  })
}

class SilentObserver {
  constructor(_callback: IntersectionObserverCallback) {}
  observe(): void {}
  unobserve(): void {}
  disconnect(): void {}
  takeRecords(): IntersectionObserverEntry[] {
    return []
  }
}

describe('MEU-70 rail re-check on scroll (SCROLL_RECHECK)', () => {
  /** Only the last section's top is on screen; the scroller is at its bottom. */
  function placeAtBottom(main: HTMLElement): void {
    stubScroller(main, { scrollHeight: 2000, clientHeight: 700, scrollTop: 1300 })
    for (const element of main.querySelectorAll('[data-settings-section]')) {
      stubBox(element, element.getAttribute('data-settings-section') === 'mcp' ? 500 : -400)
    }
  }

  it('AC-70.3 a scroll at the bottom makes the last section current with no observer callback', async () => {
    vi.stubGlobal('IntersectionObserver', SilentObserver)
    const { main } = renderInScroller()
    await settle()
    expect(screen.getByTestId('settings-rail-download').getAttribute('aria-current')).toBe('location')
    placeAtBottom(main)
    await act(async () => {
      main.dispatchEvent(new Event('scroll'))
    })
    await nextFrames()
    expect(screen.getByTestId('settings-rail-mcp').getAttribute('aria-current')).toBe('location')
    expect(document.querySelectorAll('[aria-current="location"]')).toHaveLength(1)
  })

  it('AC-70.3 a scroll during a click lock leaves the clicked entry current until the lock is released', async () => {
    vi.stubGlobal('IntersectionObserver', SilentObserver)
    const { main } = renderInScroller()
    await settle()
    placeAtBottom(main)
    act(() => {
      fireEvent.click(screen.getByTestId('settings-rail-tts'))
    })
    await act(async () => {
      main.dispatchEvent(new Event('scroll'))
    })
    await nextFrames()
    expect(screen.getByTestId('settings-rail-tts').getAttribute('aria-current')).toBe('location')
    // The lock releases SCROLL_SETTLE_MS after the last scroll event (A-6); TTS is off screen, so the
    // reconcile then follows the scroller to the bottom.
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 400))
    })
    await nextFrames()
    expect(screen.getByTestId('settings-rail-mcp').getAttribute('aria-current')).toBe('location')
    expect(document.querySelectorAll('[aria-current="location"]')).toHaveLength(1)
  })

  it('AC-70.3 the scroll listener is removed on unmount', async () => {
    vi.stubGlobal('IntersectionObserver', SilentObserver)
    const live = new Set<EventListenerOrEventListenerObject>()
    const added = vi.spyOn(HTMLElement.prototype, 'addEventListener')
    const removed = vi.spyOn(HTMLElement.prototype, 'removeEventListener')
    added.mockImplementation(function (this: HTMLElement, type: string, listener: EventListenerOrEventListenerObject | null, options?: boolean | AddEventListenerOptions) {
      if (type === 'scroll' && listener !== null && this.getAttribute('data-testid') === 'scroller') live.add(listener)
      EventTarget.prototype.addEventListener.call(this, type, listener, options)
    })
    removed.mockImplementation(function (this: HTMLElement, type: string, listener: EventListenerOrEventListenerObject | null, options?: boolean | EventListenerOptions) {
      if (type === 'scroll' && listener !== null) live.delete(listener)
      EventTarget.prototype.removeEventListener.call(this, type, listener, options)
    })
    try {
      const { main, unmount } = renderInScroller()
      await settle()
      expect(live.size).toBeGreaterThan(0)
      unmount()
      expect(live.size).toBe(0)
      expect(() => main.dispatchEvent(new Event('scroll'))).not.toThrow()
    } finally {
      added.mockRestore()
      removed.mockRestore()
    }
  })
})

describe('MEU-70 tail spacer (TAIL_SPACER)', () => {
  it('AC-70.4 the spacer is the hidden last child of the content column and is 0px without ResizeObserver', async () => {
    expect(typeof ResizeObserver).toBe('undefined')
    await renderPage()
    await settle()
    const spacer = screen.queryByTestId('settings-tail-spacer')
    expect(spacer).not.toBeNull()
    expect(spacer?.getAttribute('aria-hidden')).toBe('true')
    expect(spacer?.parentElement?.lastElementChild).toBe(spacer)
    expect(spacer?.previousElementSibling?.getAttribute('data-testid')).toBe('mcp-access-card')
    expect(spacer?.style.height).toBe('0px')
  })

  it('AC-70.4 with ResizeObserver the spacer height follows tailSpacerHeight and re-measures', async () => {
    const callbacks: ResizeObserverCallback[] = []
    class FakeResizeObserver {
      constructor(callback: ResizeObserverCallback) {
        callbacks.push(callback)
      }
      observe(): void {}
      unobserve(): void {}
      disconnect(): void {}
    }
    vi.stubGlobal('ResizeObserver', FakeResizeObserver)
    vi.stubGlobal('IntersectionObserver', SilentObserver)
    const { main } = renderInScroller()
    await settle()
    // 300 px of content below the last section's top → 700 - 16 - 300 = 384.
    stubScroller(main, { scrollHeight: 1500, clientHeight: 700, scrollTop: 0 })
    stubBox(screen.getByTestId('mcp-access-card'), 1200)
    expect(callbacks.length).toBeGreaterThan(0)
    await act(async () => {
      for (const callback of callbacks) callback([], {} as ResizeObserver)
    })
    await nextFrames()
    expect(screen.queryByTestId('settings-tail-spacer')?.style.height).toBe('384px')
    // Content below the last top already fills the scroller: no spacer.
    stubScroller(main, { scrollHeight: 2384 + 384, clientHeight: 700, scrollTop: 0 })
    await act(async () => {
      for (const callback of callbacks) callback([], {} as ResizeObserver)
    })
    await nextFrames()
    expect(screen.queryByTestId('settings-tail-spacer')?.style.height).toBe('0px')
  })

  it('AC-70.4 every rendered section frame carries scroll-mt-4 (SECTION_SCROLL_MARGIN; Review R2 F5)', async () => {
    await renderPage()
    await settle()
    const frames = document.querySelectorAll('[data-settings-section]')
    expect(frames.length).toBeGreaterThanOrEqual(10)
    for (const frame of frames) {
      expect(frame.className.split(/\s+/), frame.getAttribute('data-settings-section') ?? '').toContain('scroll-mt-4')
    }
  })
})

describe('MEU-70 reveal fallback (REVEAL_FALLBACK, Session 31 D-22)', () => {
  /** A section inside a scrolling main, with scrollIntoView recorded (jsdom does not implement it). */
  function revealFixture(): { main: HTMLElement; target: HTMLElement; calls: Array<ScrollIntoViewOptions | boolean | undefined> } {
    const main = document.createElement('main')
    main.style.overflowY = 'auto'
    const target = document.createElement('section')
    target.tabIndex = -1
    main.appendChild(target)
    document.body.appendChild(main)
    const calls: Array<ScrollIntoViewOptions | boolean | undefined> = []
    Object.defineProperty(target, 'scrollIntoView', {
      configurable: true,
      value: (arg?: ScrollIntoViewOptions | boolean) => {
        calls.push(arg)
      },
    })
    return { main, target, calls }
  }

  it('AC-70.10 a smooth reveal that scrolled is never completed by the fallback, even back at its start', () => {
    vi.useFakeTimers({ toFake: ['setTimeout', 'clearTimeout'] })
    const { main, target, calls } = revealFixture()
    try {
      revealSection(target)
      expect(calls).toEqual([{ behavior: 'smooth', block: 'start' }])
      // The smooth scroll started (a scroll event), then the user went back to where it began.
      main.dispatchEvent(new Event('scroll'))
      main.scrollTop = 0
      vi.advanceTimersByTime(1000)
      expect(calls).toHaveLength(1)
    } finally {
      main.remove()
    }
  })

  it('AC-70.10 a smooth reveal that never scrolled is still completed as a jump (A-3 kept)', () => {
    vi.useFakeTimers({ toFake: ['setTimeout', 'clearTimeout'] })
    const { main, target, calls } = revealFixture()
    try {
      revealSection(target)
      vi.advanceTimersByTime(1000)
      expect(calls).toEqual([
        { behavior: 'smooth', block: 'start' },
        { behavior: 'auto', block: 'start' },
      ])
    } finally {
      main.remove()
    }
  })
})

describe('Session 31 A-n rail group headings read as non-interactive bands (Mat, CHROME_LOOK follow-up)', () => {
  it('each group heading is an inert, tinted band distinct from the clickable entries', async () => {
    await renderPage()
    await settle()
    for (const group of ['pages', 'app', 'setup']) {
      const heading = document.getElementById(`settings-rail-group-${group}`)
      expect(heading, group).not.toBeNull()
      expect(heading!.tagName, group).toBe('P')
      expect(heading!.hasAttribute('tabindex'), group).toBe(false)
      expect(heading!.closest('button, a'), group).toBeNull()
      const classes = heading!.className.split(/\s+/)
      expect(classes, group).toEqual(expect.arrayContaining(['cursor-default', 'select-none', 'bg-bg-subtle/20']))
      expect(classes.some((name) => name.startsWith('hover:')), group).toBe(false)
    }
    const entry = screen.getByTestId('settings-rail-download')
    expect(entry.className).not.toContain('bg-bg-subtle/20')
  })
})

describe('Session 31 execution review R1 F1: the tail spacer survives a section-list change', () => {
  it('AC-70.4 a supported Startup that loads after a nonzero spacer keeps the spacer exact, so MCP still reaches the top band', async () => {
    const live = new Set<ResizeObserverCallback>()
    class FakeResizeObserver {
      private readonly callback: ResizeObserverCallback
      constructor(callback: ResizeObserverCallback) {
        this.callback = callback
        live.add(callback)
      }
      observe(): void {}
      unobserve(): void {}
      disconnect(): void {
        live.delete(this.callback)
      }
    }
    async function measureAll(): Promise<void> {
      await act(async () => {
        for (const callback of [...live]) callback([], {} as ResizeObserver)
      })
      await nextFrames()
    }
    vi.stubGlobal('ResizeObserver', FakeResizeObserver)
    vi.stubGlobal('IntersectionObserver', SilentObserver)
    let resolveLogin: (state: { supported: true; enabled: false; minimized: false; startMinimizedSupported: true }) => void = () => undefined
    mockApi({
      loginItemGet: () => new Promise((resolve) => {
        resolveLogin = resolve
      }),
    })
    const { main } = renderInScroller()
    await settle()
    expect(screen.queryByTestId('settings-rail-startup')).toBeNull()
    // 300 px of content below MCP's top in a 700 px scroller: 700 - 16 - 300 = 384.
    stubScroller(main, { scrollHeight: 1500, clientHeight: 700, scrollTop: 0 })
    stubBox(screen.getByTestId('mcp-access-card'), 1200)
    await measureAll()
    expect(screen.getByTestId('settings-tail-spacer').style.height).toBe('384px')
    // The committed spacer is now part of the scroll content.
    stubScroller(main, { scrollHeight: 1500 + 384, clientHeight: 700, scrollTop: 0 })
    // Supported Startup arrives late: the section list changes while the 384 px spacer stays rendered.
    await act(async () => {
      resolveLogin({ supported: true, enabled: false, minimized: false, startMinimizedSupported: true })
    })
    await settle()
    expect(screen.getByTestId('settings-rail-startup')).toBeTruthy()
    await nextFrames()
    expect(screen.getByTestId('settings-tail-spacer').style.height).toBe('384px')
    // The scroller grows to 800 px; the content is unchanged, so the spacer must be 800 - 16 - 300 = 484.
    stubScroller(main, { scrollHeight: 1500 + 384, clientHeight: 800, scrollTop: 0 })
    await measureAll()
    const spacer = Number.parseFloat(screen.getByTestId('settings-tail-spacer').style.height)
    expect(spacer).toBe(484)
    // At maximum scroll MCP's top sits exactly SECTION_SCROLL_MARGIN (16 px) below the scroller's top.
    const maxScrollTop = 1500 + spacer - 800
    expect(1200 - maxScrollTop).toBe(16)
  })
})
