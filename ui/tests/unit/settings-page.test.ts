/** @vitest-environment jsdom */

import { existsSync, readdirSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { SettingsPage } from '../../src/renderer/src/features/settings/SettingsPage'
import { SETTINGS_EVENTS } from '../../src/renderer/src/features/settings/settings-commands'
import { SETTINGS_ERROR_EVENT } from '../../src/renderer/src/features/settings/useSettingsPage'
import { queryClient } from '../../src/renderer/src/lib/query-client'
import { expectBoundHint } from './helpers/bound-hint'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')
const settingsDir = resolve(repoRoot, 'ui/src/renderer/src/features/settings')
const routerPath = resolve(repoRoot, 'ui/src/renderer/src/router.tsx')
const schemasPath = resolve(settingsDir, 'settings-schemas.ts')
const hookPath = resolve(settingsDir, 'useSettingsPage.ts')

const TRANSCRIPT_LEAVES = [
  'output_dir',
  'requests_per_hour',
  'delay_between_requests',
  'max_retries',
  'retry_delay',
  'batch_size',
  'pause_between_batches',
  'playlist_end',
  'max_words_per_document',
] as const

const TTS_LEAVES = [
  'models_directory',
  'voice',
  'speed',
  'output_format',
  'output_path',
  'device',
  'chunk_max_chars',
] as const

function readRequired(path: string): string {
  expect(existsSync(path), path).toBe(true)
  return readFileSync(path, 'utf8')
}

function mockApi(): void {
  window.api = {
    getBackendUrl: async () => 'http://127.0.0.1:51234/api/v1',
    getToken: async () => 'gui-nonce',
    logStartupMetric: () => undefined,
    showDirectoryDialog: async () => 'C:/e2e/outdir',
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
      descriptorPresent: false,
      portOk: false,
      modelsDirWritable: false,
      logFilePath: 'C:/Users/test/AppData/Local/av-kit/logs/console.log',
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

function jsonResponse(payload: unknown, status = 200): Response {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

describe('MEU-23 settings page', () => {
  let user: ReturnType<typeof userEvent.setup>
  const fetches: Array<{ url: string; method: string; body?: unknown }> = []

  beforeEach(() => {
    user = userEvent.setup()
    fetches.length = 0
    mockApi()
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string, init?: RequestInit) => {
        const method = (init?.method ?? 'GET').toUpperCase()
        let body: unknown
        if (typeof init?.body === 'string' && init.body.length > 0) {
          body = JSON.parse(init.body)
        }
        fetches.push({ url: String(url), method, body })
        if (url.includes('/settings/downloader')) {
          return jsonResponse({
            path: 'C:/Downloads/av-kit',
            quality: '1080p',
            audio_only: false,
            audio_format: 'default',
            cookie_mode: 'browser',
            cookie_browser: 'chrome',
            cookie_browser_profile: 'Default',
            cookie_file_path: '',
            archive_tracking: true,
            yt_dlp_debug: false,
            ffmpeg_path: 'C:/bin/ffmpeg.exe',
          })
        }
        if (url.includes('/settings/transcript')) {
          return jsonResponse({
            output_dir: 'C:/Transcripts',
            requests_per_hour: 300,
            delay_between_requests: 6,
            max_retries: 3,
            retry_delay: 30,
            batch_size: 50,
            pause_between_batches: 300,
            playlist_end: 0,
            max_words_per_document: 490000,
          })
        }
        if (url.includes('/settings/tts')) {
          return jsonResponse({
            models_directory: 'C:/models',
            voice: 'af_heart',
            speed: 1,
            output_format: 'MP3',
            output_path: 'C:/Documents',
            device: 'auto',
            chunk_max_chars: 250,
          })
        }
        if (url.includes('/settings/app')) {
          return jsonResponse({ log_level: 'INFO', log_to_file: false, console_visible: true })
        }
        if (url.includes('/settings/ui')) {
          return jsonResponse({ theme: 'dark' })
        }
        if (url.includes('/settings/converter')) {
          return jsonResponse({
            output_dir: '~/Videos/av-kit',
            default_preset: 'balanced',
            skip_existing: true,
            gpu_preference: 'auto',
          })
        }
        if (url.includes('/health/dependencies')) {
          return jsonResponse({
            yt_dlp: { available: true, version: '2026.05.15' },
            ffmpeg: { available: false, version: null },
          })
        }
        if (url.includes('/downloads/apply-defaults')) {
          return new Response(null, { status: 204 })
        }
        return jsonResponse({ error: { message: 'unexpected' } }, 422)
      }),
    )
  })

  afterEach(() => {
    view = null
    document.documentElement.classList.remove('dark')
    document.documentElement.style.colorScheme = ''
    vi.unstubAllGlobals()
    vi.useRealTimers()
  })

  let view: ReturnType<typeof render> | null = null

  async function renderSettingsPage(): Promise<void> {
    // A spec may re-render under a different fetch mock. That re-renders the
    // SAME tree, exactly as the shared root did, so only one SettingsPage is
    // ever mounted and an in-flight query is not orphaned by a remount.
    const tree = createElement(
      QueryClientProvider,
      { client: queryClient },
      createElement(SettingsPage, null),
    )
    await act(async () => {
      if (view === null) {
        view = render(tree)
      } else {
        view.rerender(tree)
      }
    })
    await vi.waitFor(() => {
      expect(screen.queryByTestId('settings-page')).not.toBeNull()
    })
  }

  it('AC-23.1 SETTINGS_HOME routes /settings to SettingsPage with populated cards', () => {
    const router = readRequired(routerPath)
    expect(router).toMatch(/SettingsPage/)
    expect(router).not.toMatch(/component:\s*SettingsChrome/)
  })

  it('AC-23.2/6/7 renders editable control for every settings leaf', async () => {
    await renderSettingsPage()
    await vi.waitFor(() => {
      expect(screen.queryByTestId('settings-leaf-cookie_browser')).not.toBeNull()
    })
    const alwaysDownloader = [
      'path',
      'ffmpeg_path',
      'quality',
      'audio_only',
      'audio_format',
      'cookie_mode',
      'archive_tracking',
      'yt_dlp_debug',
    ] as const
    for (const leaf of alwaysDownloader) {
      expect(screen.queryByTestId(`settings-leaf-${leaf}`)).not.toBeNull()
    }
    expect(screen.queryByTestId('settings-leaf-cookie_browser_profile')).not.toBeNull()

    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string, init?: RequestInit) => {
        const method = (init?.method ?? 'GET').toUpperCase()
        let body: unknown
        if (typeof init?.body === 'string' && init.body.length > 0) {
          body = JSON.parse(init.body)
        }
        fetches.push({ url: String(url), method, body })
        if (url.includes('/settings/downloader')) {
          return jsonResponse({
            path: 'C:/Downloads/av-kit',
            quality: '1080p',
            cookie_mode: 'file',
            cookie_file_path: 'C:/cookies.txt',
          })
        }
        if (url.includes('/settings/transcript')) {
          return jsonResponse({ output_dir: 'C:/Transcripts', requests_per_hour: 300 })
        }
        if (url.includes('/settings/tts')) {
          return jsonResponse({ models_directory: 'C:/models', voice: 'af_heart', device: 'auto' })
        }
        if (url.includes('/settings/app')) {
          return jsonResponse({ log_level: 'INFO' })
        }
        if (url.includes('/settings/ui')) {
          return jsonResponse({ theme: 'dark' })
        }
        if (url.includes('/settings/converter')) {
          return jsonResponse({
            output_dir: '~/Videos/av-kit',
            default_preset: 'balanced',
            skip_existing: true,
            gpu_preference: 'auto',
          })
        }
        if (url.includes('/health/dependencies')) {
          return jsonResponse({ yt_dlp: { available: true }, ffmpeg: { available: true } })
        }
        return jsonResponse({})
      }),
    )
    queryClient.clear()
    await renderSettingsPage()
    await vi.waitFor(() => {
      expect(screen.queryByTestId('settings-leaf-cookie_file_path')).not.toBeNull()
    })

    for (const leaf of TRANSCRIPT_LEAVES) {
      expect(screen.queryByTestId(`settings-leaf-${leaf}`)).not.toBeNull()
    }
    for (const leaf of TTS_LEAVES) {
      expect(screen.queryByTestId(`settings-leaf-${leaf}`)).not.toBeNull()
    }
  })

  it('AC-23.3 APPLY_DEFAULTS POSTs apply-defaults without a quality body', async () => {
    await renderSettingsPage()
    await user.click(screen.getByTestId('apply-defaults-btn'))
    await vi.waitFor(() => {
      expect(fetches.some((row) => row.url.includes('/downloads/apply-defaults') && row.method === 'POST')).toBe(
        true,
      )
    })
    const apply = fetches.find((row) => row.url.includes('/downloads/apply-defaults'))
    expect(apply?.body).toBeUndefined()
  })

  it('AC-23.10 checkDeps dispatches once without recursion', async () => {
    const dispatchSpy = vi.spyOn(window, 'dispatchEvent')
    await renderSettingsPage()
    dispatchSpy.mockClear()
    await user.click(screen.getByTestId('check-deps-btn'))
    const checkDepsEvents = dispatchSpy.mock.calls.filter(
      (call) => call[0] instanceof Event && call[0].type === SETTINGS_EVENTS.checkDeps,
    )
    expect(checkDepsEvents.length).toBe(1)
    await vi.waitFor(() => {
      expect(fetches.filter((row) => row.url.includes('/health/dependencies')).length).toBeGreaterThan(0)
    })
  })

  it('AC-23.11 readiness card shows deep links when checks fail', async () => {
    await renderSettingsPage()
    expect(screen.queryByTestId('readiness-descriptor-link')).not.toBeNull()
    expect(screen.queryByTestId('readiness-port-link')).not.toBeNull()
    expect(screen.queryByTestId('readiness-models-link')).not.toBeNull()
    expect(screen.queryByTestId('readiness-ffmpeg-link')).not.toBeNull()
  })

  it('AC-23.13 debounces leaf PUT for DEBOUNCE_MS and skips unchanged blur', () => {
    const hook = readRequired(hookPath)
    expect(hook).toMatch(/300|DEBOUNCE_MS/)
    expect(hook).toMatch(/setTimeout|debounce/)
    expect(hook).toMatch(/\/settings\//)
  })

  it('AC-23.14 ERROR_SURFACE dispatches banner on immediate putNow failure', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string, init?: RequestInit) => {
        const method = (init?.method ?? 'GET').toUpperCase()
        if (url.includes('/settings/ui') && method === 'PUT') {
          return jsonResponse({ error: { code: 'HTTP_ERROR', message: 'invalid theme' } }, 422)
        }
        if (url.includes('/settings/downloader')) {
          return jsonResponse({ path: 'C:/Downloads', cookie_mode: 'none', quality: '1080p' })
        }
        if (url.includes('/settings/transcript')) {
          return jsonResponse({ output_dir: 'C:/Transcripts' })
        }
        if (url.includes('/settings/tts')) {
          return jsonResponse({ models_directory: 'C:/models' })
        }
        if (url.includes('/settings/app')) {
          return jsonResponse({ log_level: 'INFO' })
        }
        if (url.includes('/settings/ui')) {
          return jsonResponse({ theme: 'dark' })
        }
        if (url.includes('/settings/converter')) {
          return jsonResponse({
            output_dir: '~/Videos/av-kit',
            default_preset: 'balanced',
            skip_existing: true,
            gpu_preference: 'auto',
          })
        }
        if (url.includes('/health/dependencies')) {
          return jsonResponse({ yt_dlp: { available: true }, ffmpeg: { available: true } })
        }
        return jsonResponse({})
      }),
    )
    const errors: string[] = []
    const onError = (event: Event) => {
      const detail = (event as CustomEvent<{ message?: string }>).detail
      errors.push(detail?.message ?? '')
    }
    window.addEventListener(SETTINGS_ERROR_EVENT, onError)
    await renderSettingsPage()
    await user.click(screen.getByTestId('theme-light-btn'))
    await vi.waitFor(() => {
      expect(errors.length).toBeGreaterThan(0)
    })
    window.removeEventListener(SETTINGS_ERROR_EVENT, onError)
  })

  it('AC-97.4 HINTS the theme buttons carry the appearance chords', async () => {
    await renderSettingsPage()
    expectBoundHint(screen.getByTestId('theme-dark-btn'), 'appearance:dark')
    expectBoundHint(screen.getByTestId('theme-light-btn'), 'appearance:light')
  })

  it('AC-23.14 strict schema rejects unknown leaf keys', () => {
    const schemas = readRequired(schemasPath)
    expect(schemas).toMatch(/\.strict\(\)/)
    expect(schemas).toMatch(/SettingsValidationError/)
  })

  it('AC-23.8/9 console and theme leaves are wired to settings namespaces', async () => {
    await renderSettingsPage()
    expect(screen.queryByTestId('settings-leaf-log_level')).not.toBeNull()
    expect(screen.queryByTestId('settings-leaf-log_to_file')).not.toBeNull()
    expect(screen.queryByTestId('settings-leaf-console_visible')).not.toBeNull()
    expect(screen.queryByTestId('settings-log-file-path')?.textContent).toContain(
      'logs/console.log',
    )
    expect(screen.queryByTestId('theme-dark-btn')).not.toBeNull()
    expect(screen.queryByTestId('theme-light-btn')).not.toBeNull()
  })

  it('AC-23.9 light theme PUT removes the document root dark class', async () => {
    document.documentElement.classList.add('dark')
    await renderSettingsPage()
    await user.click(screen.getByTestId('theme-light-btn'))
    await vi.waitFor(() => {
      expect(document.documentElement.classList.contains('dark')).toBe(false)
    })
  })

  it('AC-23.9 dark theme PUT adds the document root dark class', async () => {
    document.documentElement.classList.remove('dark')
    await renderSettingsPage()
    await user.click(screen.getByTestId('theme-dark-btn'))
    await vi.waitFor(() => {
      expect(document.documentElement.classList.contains('dark')).toBe(true)
    })
  })

  it('AC-23.9 failed theme PUT leaves the document root class unchanged', async () => {
    document.documentElement.classList.add('dark')
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string, init?: RequestInit) => {
        const method = (init?.method ?? 'GET').toUpperCase()
        if (url.includes('/settings/ui') && method === 'PUT') {
          return jsonResponse({ error: { code: 'HTTP_ERROR', message: 'invalid theme' } }, 422)
        }
        if (url.includes('/settings/downloader')) {
          return jsonResponse({ path: 'C:/Downloads', cookie_mode: 'none', quality: '1080p' })
        }
        if (url.includes('/settings/transcript')) {
          return jsonResponse({ output_dir: 'C:/Transcripts' })
        }
        if (url.includes('/settings/tts')) {
          return jsonResponse({ models_directory: 'C:/models' })
        }
        if (url.includes('/settings/app')) {
          return jsonResponse({ log_level: 'INFO' })
        }
        if (url.includes('/settings/ui')) {
          return jsonResponse({ theme: 'dark' })
        }
        if (url.includes('/settings/converter')) {
          return jsonResponse({
            output_dir: '~/Videos/av-kit',
            default_preset: 'balanced',
            skip_existing: true,
            gpu_preference: 'auto',
          })
        }
        if (url.includes('/health/dependencies')) {
          return jsonResponse({ yt_dlp: { available: true }, ffmpeg: { available: true } })
        }
        return jsonResponse({})
      }),
    )
    const errors: string[] = []
    const onError = (event: Event) => {
      const detail = (event as CustomEvent<{ message?: string }>).detail
      errors.push(detail?.message ?? '')
    }
    window.addEventListener(SETTINGS_ERROR_EVENT, onError)
    await renderSettingsPage()
    await user.click(screen.getByTestId('theme-light-btn'))
    await vi.waitFor(() => {
      expect(errors.length).toBeGreaterThan(0)
    })
    window.removeEventListener(SETTINGS_ERROR_EVENT, onError)
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('AC-23.12 mcp card uses getMcpAccessStatus and never renders token', async () => {
    await renderSettingsPage()
    expect(screen.queryByTestId('mcp-access-card')).not.toBeNull()
    expect(screen.queryByTestId('mcp-token-present')?.textContent).toMatch(/yes|no/)
    expect(document.body.textContent).not.toMatch(/gui-nonce/)
  })

  it('AC-58.1 settings page renders the rail beside a 960px content column', async () => {
    await renderSettingsPage()
    const page = screen.getByTestId('settings-page')
    expect(page.className).toContain('max-w-[60rem]')
    expect(page.className).not.toContain('max-w-3xl')
    expect(screen.queryByTestId('settings-rail')).not.toBeNull()
  })

  it('AC-139.8 the yt-dlp debug switch saves true and then false', async () => {
    // D-630: a characterisation of the existing switch. The stub keeps the saved value, so
    // the refetch after each PUT shows what was saved.
    const base = globalThis.fetch
    let debug = false
    const puts: Array<{ path: string; body: unknown }> = []
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string, init?: RequestInit) => {
        if (!String(url).includes('/settings/downloader')) return base(url, init)
        const method = (init?.method ?? 'GET').toUpperCase()
        if (method === 'PUT') {
          const body = JSON.parse(String(init?.body)) as { yt_dlp_debug?: unknown }
          puts.push({ path: new URL(String(url), 'http://x').pathname, body })
          if (typeof body.yt_dlp_debug === 'boolean') debug = body.yt_dlp_debug
        }
        const stored = (await (await base(url, { method: 'GET' })).json()) as Record<string, unknown>
        return jsonResponse({ ...stored, yt_dlp_debug: debug })
      }),
    )
    await renderSettingsPage()
    const toggle = (): HTMLInputElement =>
      screen.getByTestId('settings-leaf-yt_dlp_debug') as HTMLInputElement
    await vi.waitFor(() => expect(toggle().checked).toBe(false))

    await user.click(toggle())
    await vi.waitFor(() => expect(puts).toHaveLength(1))
    await vi.waitFor(() => expect(toggle().checked).toBe(true))
    await user.click(toggle())
    await vi.waitFor(() => expect(puts).toHaveLength(2))
    expect(puts.map((put) => [put.path.replace(/^.*\/settings\//, ''), put.body])).toEqual([
      ['downloader', { yt_dlp_debug: true }],
      ['downloader', { yt_dlp_debug: false }],
    ])
  })
})

describe('MEU-58 settings source location (SETTINGS_SOURCE_LOCATION)', () => {
  it('AC-58.11 sections stay in top-level settings files and new IDs follow the MEU-57 block', () => {
    const entries = readdirSync(settingsDir, { withFileTypes: true })
    expect(entries.filter((entry) => entry.isDirectory()).map((entry) => entry.name)).toEqual([])
    const page = readRequired(resolve(settingsDir, 'SettingsPage.tsx'))
    for (const id of ['convert-settings', 'capture-settings', 'convert-settings-save', 'capture-settings-save']) {
      expect(page, id).toContain(id)
    }
    expect(existsSync(resolve(settingsDir, 'SettingsRail.tsx'))).toBe(true)
    expect(existsSync(resolve(settingsDir, 'settings-sections.ts'))).toBe(true)
    const ids = readRequired(resolve(repoRoot, 'ui/tests/e2e/test-ids.ts'))
    const tail = ids.split('// MEU-57 Capture page')[1] ?? ''
    for (const id of ['settings-rail', 'settings-readiness-count', 'settings-rail-dot-readiness', 'settings-mode-download']) {
      expect(tail, id).toContain(`'${id}'`)
    }
  })
})

describe('MEU-23 settings source contracts', () => {
  function settingsSources(): string {
    return readdirSync(settingsDir)
      .filter((name) => name.endsWith('.ts') || name.endsWith('.tsx'))
      .map((name) => readFileSync(resolve(settingsDir, name), 'utf8'))
      .join('\n')
  }

  it('AC-23.4/5 browse and cookie visibility wiring exists in sources', () => {
    const sources = settingsSources()
    expect(sources).toContain('browse-ffmpeg-btn')
    expect(sources).toMatch(/showFileDialog/)
    expect(sources).toMatch(/cookie_mode|cookieMode/)
    expect(sources).toMatch(/settings-leaf-cookie_browser/)
    expect(sources).toMatch(/settings-leaf-cookie_file_path/)
  })
})

type LoginItemState =
  | {
      supported: true
      enabled: boolean
      minimized: boolean
      startMinimizedSupported: boolean
    }
  | { supported: false; reason: 'platform' | 'not-packaged'; enabled: false; minimized: false }

function assignLoginItemApi(handlers: {
  get?: () => Promise<LoginItemState>
  set?: (enabled: boolean, minimized: boolean) => Promise<LoginItemState>
}): void {
  Object.assign(window.api, {
    loginItemGet: handlers.get,
    loginItemSet: handlers.set,
  })
}

describe('MEU-61 settings startup card', () => {
  let user: ReturnType<typeof userEvent.setup>
  const puts: Array<{ url: string; body?: unknown }> = []

  beforeEach(() => {
    user = userEvent.setup()
    puts.length = 0
    mockApi()
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string, init?: RequestInit) => {
        const method = (init?.method ?? 'GET').toUpperCase()
        let body: unknown
        if (typeof init?.body === 'string' && init.body.length > 0) {
          body = JSON.parse(init.body)
        }
        if (method === 'PUT') puts.push({ url: String(url), body })
        if (url.includes('/settings/downloader')) {
          return jsonResponse({
            path: 'C:/Downloads/av-kit',
            quality: '1080p',
            audio_only: false,
            audio_format: 'default',
            cookie_mode: 'browser',
            cookie_browser: 'chrome',
            cookie_browser_profile: 'Default',
            cookie_file_path: '',
            archive_tracking: true,
            yt_dlp_debug: false,
            ffmpeg_path: 'C:/bin/ffmpeg.exe',
          })
        }
        if (url.includes('/settings/transcript')) {
          return jsonResponse({ output_dir: 'C:/Transcripts' })
        }
        if (url.includes('/settings/tts')) {
          return jsonResponse({ models_directory: 'C:/models', voice: 'af_heart', speed: 1 })
        }
        if (url.includes('/settings/app')) {
          return jsonResponse({ log_level: 'INFO', log_to_file: false, console_visible: true })
        }
        if (url.includes('/settings/ui')) {
          return jsonResponse({ theme: 'dark' })
        }
        if (url.includes('/settings/converter')) {
          return jsonResponse({
            output_dir: '~/Videos/av-kit',
            default_preset: 'balanced',
            skip_existing: true,
            gpu_preference: 'auto',
          })
        }
        if (url.includes('/health/dependencies')) {
          return jsonResponse({ yt_dlp: { available: true }, ffmpeg: { available: true } })
        }
        return jsonResponse({})
      }),
    )
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    queryClient.clear()
  })

  async function renderSettingsPage(): Promise<void> {
    await act(async () => {
      render(
        createElement(QueryClientProvider, { client: queryClient }, createElement(SettingsPage)),
      )
    })
  }

  it('AC-61.12 panel hidden when unsupported; shown when supported true', async () => {
    assignLoginItemApi({
      get: async () => ({
        supported: false,
        reason: 'not-packaged',
        enabled: false,
        minimized: false,
      }),
    })
    await renderSettingsPage()
    expect(screen.queryByTestId('start-at-sign-in-panel')).toBeNull()

    assignLoginItemApi({
      get: async () => ({
        supported: true,
        enabled: false,
        minimized: false,
        startMinimizedSupported: true,
      }),
    })
    await renderSettingsPage()
    await vi.waitFor(() => {
      expect(screen.getByTestId('start-at-sign-in-panel')).toBeTruthy()
    })
  })

  it('AC-61.13 MINIMIZED_TESTID only while parent on', async () => {
    assignLoginItemApi({
      get: async () => ({
        supported: true,
        enabled: false,
        minimized: false,
        startMinimizedSupported: true,
      }),
    })
    await renderSettingsPage()
    await vi.waitFor(() => {
      expect(screen.getByTestId('start-at-sign-in-checkbox')).toBeTruthy()
    })
    expect(screen.queryByTestId('start-minimized-checkbox')).toBeNull()
    cleanup()
    assignLoginItemApi({
      get: async () => ({
        supported: true,
        enabled: true,
        minimized: false,
        startMinimizedSupported: true,
      }),
    })
    await renderSettingsPage()
    await vi.waitFor(() => {
      expect(screen.getByTestId('start-minimized-checkbox')).toBeTruthy()
    })
    cleanup()
    assignLoginItemApi({
      get: async () => ({
        supported: true,
        enabled: true,
        minimized: false,
        startMinimizedSupported: false,
      }),
    })
    await renderSettingsPage()
    await vi.waitFor(() => {
      expect(screen.getByTestId('start-at-sign-in-checkbox')).toBeTruthy()
    })
    expect(screen.queryByTestId('start-minimized-checkbox')).toBeNull()
  })

  it('AC-61.14 checkbox click does not PUT settings; schemas omit forbidden leaves', async () => {
    const schemas = readRequired(schemasPath)
    expect(schemas).not.toContain('open_at_login')
    expect(schemas).not.toContain('start_minimized')
    assignLoginItemApi({
      get: async () => ({
        supported: true,
        enabled: false,
        minimized: false,
        startMinimizedSupported: true,
      }),
      set: async () => ({
        supported: true,
        enabled: true,
        minimized: false,
        startMinimizedSupported: true,
      }),
    })
    await renderSettingsPage()
    await vi.waitFor(() => {
      expect(screen.getByTestId('start-at-sign-in-checkbox')).toBeTruthy()
    })
    await user.click(screen.getByTestId('start-at-sign-in-checkbox'))
    expect(puts.some((row) => JSON.stringify(row.body).includes('open_at_login'))).toBe(false)
    expect(puts.some((row) => row.url.includes('/settings/'))).toBe(false)
  })

  it('AC-61.16 HELP_FILE section HELP_ID contains HELP_STARTUP_TOKENS', () => {
    const helpPath = resolve(settingsDir, 'settings-help-content.ts')
    const help = readRequired(helpPath)
    expect(help).toContain("id: 'startup'")
    expect(help).toContain('per-user Startup entry')
    expect(help).toContain('administrator')
    expect(help).toContain('Task Manager')
    expect(help).toContain('notification area')
    expect(help).toContain('F2')
  })

  it('AC-61.20 omitting get at runtime yields unsupported, no throw', async () => {
    const { getPreloadApiKeys } = await import('../../src/main/preload')
    expect(getPreloadApiKeys()).toContain('loginItemGet')
    const api = window.api as { loginItemGet?: unknown }
    delete api.loginItemGet
    await renderSettingsPage()
    expect(screen.queryByTestId('start-at-sign-in-panel')).toBeNull()
  })
})

describe('MEU-62 AC-62.15 TTS asset rows on the Dependencies card', () => {
  const posts: Array<{ url: string; body: unknown }> = []
  let depsCalls = 0
  let assets: Record<string, { available: boolean; version: string | null; state: string }> = {}

  async function renderSettingsPage(): Promise<void> {
    await act(async () => {
      render(
        createElement(QueryClientProvider, { client: queryClient }, createElement(SettingsPage)),
      )
    })
  }

  afterEach(() => {
    cleanup()
    vi.unstubAllGlobals()
  })

  beforeEach(() => {
    posts.length = 0
    depsCalls = 0
    assets = {
      tts_onnx_vocab: { available: true, version: null, state: 'ready' },
      tts_spacy_model: { available: false, version: null, state: 'missing' },
      tts_voice_packs: { available: true, version: null, state: 'ready' },
    }
    mockApi()
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string, init?: RequestInit) => {
        const method = (init?.method ?? 'GET').toUpperCase()
        if (method === 'POST' && typeof init?.body === 'string') {
          posts.push({ url: String(url), body: JSON.parse(init.body) })
        }
        if (url.includes('/health/dependencies')) {
          depsCalls += 1
          return jsonResponse({
            yt_dlp: { available: true, version: '2026.08.30' },
            ffmpeg: { available: true, version: '7.1', path: 'C:/ffmpeg/bin/ffmpeg.exe' },
            tts_espeak: { available: true, version: '1.52.0', path: 'C:/Program Files/eSpeak NG/espeak-ng.exe' },
            ...assets,
          })
        }
        if (url.includes('/models/download') && method === 'POST') {
          return jsonResponse({ variant: null, asset: 'tts_spacy_model' }, 202)
        }
        return jsonResponse({})
      }),
    )
    queryClient.clear()
  })

  it('AC-62.15 renders both asset rows after yt-dlp and FFmpeg with state chips', async () => {
    await renderSettingsPage()
    const card = await vi.waitFor(() => {
      const found = screen.getByTestId('dependencies-section')
      expect(found.querySelector('[data-testid="tts-asset-row-tts_spacy_model"]')).not.toBeNull()
      return found
    })
    const text = card.textContent ?? ''
    expect(text.indexOf('yt-dlp')).toBeLessThan(text.indexOf('FFmpeg'))
    const vocab = screen.getByTestId('tts-asset-row-tts_onnx_vocab')
    const spacy = screen.getByTestId('tts-asset-row-tts_spacy_model')
    expect(text.indexOf('FFmpeg')).toBeLessThan(text.indexOf(vocab.textContent ?? '\u0000'))
    expect(vocab.textContent).toContain('Ready')
    expect(spacy.textContent).toContain('Missing')
    expect(screen.queryByTestId('tts-asset-get-btn-tts_onnx_vocab')).toBeNull()
    expect(screen.getByTestId('tts-asset-get-btn-tts_spacy_model')).toBeTruthy()
  })

  it('AC-62.15 Get posts the asset and refetches dependencies, with no IPC', async () => {
    const ipc = vi.fn()
    ;(window.api as unknown as Record<string, unknown>).downloadAsset = ipc
    await renderSettingsPage()
    const get = await vi.waitFor(() => screen.getByTestId('tts-asset-get-btn-tts_spacy_model'))
    const before = depsCalls
    await userEvent.setup().click(get)
    await vi.waitFor(() => {
      expect(posts).toEqual([
        { url: expect.stringContaining('/models/download'), body: { asset: 'tts_spacy_model' } },
      ])
      expect(depsCalls).toBeGreaterThan(before)
    })
    expect(ipc).not.toHaveBeenCalled()
  })

  it('AC-62.15 a downloading row disables Get; rows absent from an older backend are not rendered', async () => {
    assets.tts_spacy_model = { available: false, version: null, state: 'downloading' }
    await renderSettingsPage()
    const get = await vi.waitFor(() => screen.getByTestId('tts-asset-get-btn-tts_spacy_model'))
    expect((get as HTMLButtonElement).disabled).toBe(true)
    expect(screen.getByTestId('tts-asset-row-tts_spacy_model').textContent).toContain('Downloading')
    cleanup()
    assets = {}
    queryClient.clear()
    await renderSettingsPage()
    await vi.waitFor(() => expect(depsCalls).toBeGreaterThan(0))
    expect(screen.queryByTestId('tts-asset-row-tts_onnx_vocab')).toBeNull()
    expect(screen.queryByTestId('tts-asset-row-tts_spacy_model')).toBeNull()
    expect(screen.queryByTestId('tts-asset-row-tts_voice_packs')).toBeNull()
  })
})
