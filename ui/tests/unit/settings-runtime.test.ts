/** @vitest-environment jsdom */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, render, renderHook, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement, type ReactNode } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { SettingsPage } from '../../src/renderer/src/features/settings/SettingsPage'
import { downloaderPutSchema } from '../../src/renderer/src/features/settings/settings-schemas'
import { useSettingsPage } from '../../src/renderer/src/features/settings/useSettingsPage'
import { QUERY_HEALTH_DEPENDENCIES } from '../../src/renderer/src/features/tts/tts-assets'
import { BROWSE_DENO_BTN, DEPS_JS_RUNTIME_ROW } from '../e2e/test-ids'

/**
 * MEU-141 (Session 66): the `deno_path` leaf in the UI schema (AC-141.1's UI half), the JS runtime
 * row in Settings → Dependencies (RUNTIME_ROW, AC-141.9) and the read-only Deno path field with
 * Browse (DENO_FIELD, AC-141.10). Every lookup is a query, so a missing element fails by assertion.
 */

const JSON_HEADERS = { 'Content-Type': 'application/json' }
const PICKED = 'C:/picked/deno.exe'
const SAVED = 'C:/saved/deno.exe'
/** D-648's none-found text, in the pieces the row must carry. */
const NONE_FOUND_PARTS = [
  'No JavaScript runtime found',
  'yt-dlp runs without one',
  'some YouTube formats may be missing',
  'Set a Deno path',
  'Deno 2.3 or later',
]

type JsRuntime = {
  available: boolean
  name: string | null
  path: string | null
  version: string | null
  source: 'setting' | 'bundled' | 'path' | null
  solver: boolean
}

const FOUND: JsRuntime = {
  available: true,
  name: 'deno',
  path: 'C:/rt/deno/deno.exe',
  version: '2.9.8',
  source: 'bundled',
  solver: true,
}
const NONE: JsRuntime = { available: false, name: null, path: null, version: null, source: null, solver: true }

let fileAnswer: string | undefined
let fileDialog: ReturnType<typeof vi.fn>
let puts: Array<{ url: string; body: unknown }>

function mockApi(): void {
  fileDialog = vi.fn(async () => fileAnswer)
  window.api = {
    getBackendUrl: async () => 'http://127.0.0.1:51234/api/v1',
    getToken: async () => 'gui-nonce',
    logStartupMetric: () => undefined,
    showDirectoryDialog: async () => undefined,
    showFileDialog: fileDialog,
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

function installFetch(runtime: JsRuntime): void {
  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
    const json = (payload: unknown) => new Response(JSON.stringify(payload), { status: 200, headers: JSON_HEADERS })
    if (init?.method === 'PUT') {
      const body = typeof init.body === 'string' ? (JSON.parse(init.body) as unknown) : null
      puts.push({ url, body })
      return json(body ?? {})
    }
    if (url.includes('/settings/downloader')) {
      return json({ path: 'C:/dl', ffmpeg_path: '', cookie_mode: 'none', deno_path: SAVED })
    }
    if (url.includes('/settings/app')) return json({ log_level: 'INFO', log_to_file: false, console_visible: true })
    if (url.includes('/settings/ui')) return json({ theme: 'dark' })
    if (url.includes('/health/dependencies')) {
      return json({
        yt_dlp: { available: true, version: '2026.10.26' },
        ffmpeg: { available: true, version: '7.1', path: 'C:/ffmpeg.exe' },
        js_runtime: runtime,
      })
    }
    if (url.includes('/settings/')) return json({})
    return new Response(JSON.stringify({ error: { message: 'unexpected' } }), { status: 422 })
  })
  vi.stubGlobal('fetch', fetchMock)
  window.fetch = fetchMock as typeof window.fetch
}

let client: QueryClient

async function renderPage(runtime: JsRuntime): Promise<void> {
  installFetch(runtime)
  render(createElement(QueryClientProvider, { client }, createElement(SettingsPage)))
  await vi.waitFor(() => {
    expect(screen.queryByTestId('settings-page')).not.toBeNull()
  })
  await act(async () => {
    await new Promise((resolve) => setTimeout(resolve, 0))
  })
}

async function runtimeRowText(): Promise<string> {
  await vi.waitFor(() => {
    expect(screen.queryByTestId(DEPS_JS_RUNTIME_ROW), DEPS_JS_RUNTIME_ROW).not.toBeNull()
  })
  return screen.queryByTestId(DEPS_JS_RUNTIME_ROW)?.textContent ?? ''
}

/** The hook harness of settings-deps-refresh.test.ts (AC-78.8). */
function hookHarness() {
  Object.defineProperty(window, 'api', {
    configurable: true,
    value: {
      getBackendUrl: vi.fn(async () => 'http://127.0.0.1:51234/api/v1'),
      getToken: vi.fn(async () => 'gui-nonce'),
    },
  })
  const fetchMock = vi.fn(async (_url: string, init?: RequestInit) => {
    if (init?.method === 'PUT') {
      return new Response(typeof init.body === 'string' ? init.body : '{}', { status: 200, headers: JSON_HEADERS })
    }
    return new Response('{}', { status: 200, headers: JSON_HEADERS })
  })
  vi.stubGlobal('fetch', fetchMock)
  const hookClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  const invalidate = vi.spyOn(hookClient, 'invalidateQueries')
  const wrapper = ({ children }: { children: ReactNode }) => createElement(QueryClientProvider, { client: hookClient }, children)
  const { result } = renderHook(() => useSettingsPage(), { wrapper })
  return { result, invalidate, fetchMock }
}

function depsInvalidationOrder(invalidate: ReturnType<typeof hookHarness>['invalidate']): number[] {
  const wanted = JSON.stringify(QUERY_HEALTH_DEPENDENCIES)
  return invalidate.mock.calls.flatMap(([filters], index) =>
    JSON.stringify((filters as { queryKey?: unknown } | undefined)?.queryKey) === wanted
      ? [invalidate.mock.invocationCallOrder[index]]
      : [],
  )
}

/** The error's class name, or `none`, so a refusal fails by assertion on one line. */
async function errorName(call: () => Promise<unknown>): Promise<string> {
  try {
    await call()
    return 'none'
  } catch (error) {
    return error instanceof Error ? error.name : typeof error
  }
}

beforeEach(() => {
  client = new QueryClient({ defaultOptions: { queries: { retry: false, gcTime: 0 } } })
  fileAnswer = PICKED
  puts = []
  mockApi()
})

afterEach(() => {
  cleanup()
  client.clear()
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})

describe('MEU-141 DENO_SETTING in the UI settings schema', () => {
  it('AC-141.1 the downloader PUT schema takes deno_path, as text or empty', () => {
    expect(downloaderPutSchema.safeParse({ deno_path: PICKED }).success).toBe(true)
    expect(downloaderPutSchema.safeParse({ deno_path: '' }).success).toBe(true)
  })

  it('AC-141.1 [neg] an unknown downloader leaf is still refused', () => {
    expect(downloaderPutSchema.safeParse({ deno_path_extra: PICKED }).success).toBe(false)
    expect(downloaderPutSchema.safeParse({ ffmpeg_path: 'C:/bin/ffmpeg.exe' }).success).toBe(true)
  })
})

describe('MEU-141 RUNTIME_ROW in Settings → Dependencies', () => {
  it('AC-141.9 a found runtime names itself, its version, its source and its path', async () => {
    await renderPage(FOUND)
    const text = await runtimeRowText()
    for (const part of ['deno', '2.9.8', 'bundled', 'C:/rt/deno/deno.exe']) {
      expect(text, part).toContain(part)
    }
    for (const part of NONE_FOUND_PARTS) {
      expect(text, part).not.toContain(part)
    }
  })

  it('AC-141.9 [neg] none found says yt-dlp runs without one, what it costs and the fix', async () => {
    await renderPage(NONE)
    const text = await runtimeRowText()
    for (const part of NONE_FOUND_PARTS) {
      expect(text, part).toContain(part)
    }
  })
})

describe('MEU-141 DENO_FIELD in Settings → Downloader', () => {
  it('AC-141.10 the Deno path is read-only, with Browse in its row, and Browse PUTs the pick', async () => {
    await renderPage(FOUND)
    await vi.waitFor(() => {
      expect(screen.queryByTestId('settings-leaf-deno_path'), 'settings-leaf-deno_path').not.toBeNull()
    })
    const input = screen.queryByTestId('settings-leaf-deno_path') as HTMLInputElement | null
    expect(input?.readOnly).toBe(true)
    await vi.waitFor(() => {
      expect(input?.value).toBe(SAVED)
    })
    const row = document.querySelector('label[for="settings-deno-path"]')?.parentElement ?? null
    expect(row, 'the FormRow wrapper of settings-deno-path').not.toBeNull()
    expect(input !== null && row?.contains(input) === true).toBe(true)
    const browse = row === null ? null : within(row).queryByTestId(BROWSE_DENO_BTN)
    expect(browse, `${BROWSE_DENO_BTN} in the same row`).not.toBeNull()
    await userEvent.setup().click(browse as HTMLElement)
    await vi.waitFor(() => {
      expect(puts.filter((put) => put.url.includes('/settings/downloader'))).toHaveLength(1)
    })
    expect(fileDialog).toHaveBeenCalledTimes(1)
    expect(puts.filter((put) => put.url.includes('/settings/downloader'))[0]?.body).toEqual({ deno_path: PICKED })
  })

  it('AC-141.10 [neg] a cancelled Browse PUTs nothing', async () => {
    await renderPage(FOUND)
    await vi.waitFor(() => {
      expect(screen.queryByTestId(BROWSE_DENO_BTN), BROWSE_DENO_BTN).not.toBeNull()
    })
    fileAnswer = undefined
    await userEvent.setup().click(screen.queryByTestId(BROWSE_DENO_BTN) as HTMLElement)
    await act(async () => {
      await Promise.resolve()
    })
    expect(fileDialog).toHaveBeenCalledTimes(1)
    expect(puts).toEqual([])
  })

  it('AC-141.10 a deno_path PUT refetches the dependencies query after it resolves', async () => {
    const { result, invalidate, fetchMock } = hookHarness()
    expect(typeof result.current.putNow).toBe('function')
    let name = 'not run'
    await act(async () => {
      name = await errorName(() => result.current.putNow('downloader', { deno_path: PICKED }))
    })
    expect(name).toBe('none')
    const putIndex = fetchMock.mock.calls.findIndex(([, init]) => init?.method === 'PUT')
    expect(putIndex).toBeGreaterThanOrEqual(0)
    const deps = depsInvalidationOrder(invalidate)
    expect(deps).toHaveLength(1)
    expect(deps[0]).toBeGreaterThan(fetchMock.mock.invocationCallOrder[putIndex])
  })

  it('AC-141.10 [neg] a quality PUT leaves the dependencies query alone', async () => {
    const { result, invalidate, fetchMock } = hookHarness()
    await act(async () => {
      await result.current.putNow('downloader', { quality: '1080p' })
    })
    expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'PUT')).toHaveLength(1)
    expect(depsInvalidationOrder(invalidate)).toEqual([])
  })
})
