/** @vitest-environment jsdom */

import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { SettingsPage } from '../../src/renderer/src/features/settings/SettingsPage'
import { TTS_ASSET_LABELS, TTS_ASSET_WIRES } from '../../src/renderer/src/features/tts/tts-assets'
import * as ttsJob from '../../src/renderer/src/features/tts/useTtsJob'
import { queryClient } from '../../src/renderer/src/lib/query-client'

const here = dirname(fileURLToPath(import.meta.url))
const settingsPagePath = resolve(here, '../../src/renderer/src/features/settings/SettingsPage.tsx')

const DEPS_KEY = ['health', 'dependencies']
const RUNTIME_KEY = ['models', 'download-runtime']

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

function sameKey(a: unknown, b: readonly string[]): boolean {
  return JSON.stringify(a) === JSON.stringify(b)
}

describe('MEU-73 Settings TTS runtime', () => {
  const posts: Array<{ url: string; body: unknown }> = []
  let runtimeState = 'Idle'
  let runtimeCalls = 0
  let assets: Record<string, { available: boolean; version: string | null; state: string }> = {}

  async function renderSettingsPage(): Promise<void> {
    await act(async () => {
      render(createElement(QueryClientProvider, { client: queryClient }, createElement(SettingsPage)))
    })
  }

  function depsInvalidations(spy: { mock: { calls: unknown[][] } }): number {
    return spy.mock.calls.filter(([filters]) => sameKey((filters as { queryKey?: unknown } | undefined)?.queryKey, DEPS_KEY))
      .length
  }

  /** Setup sync: the first `Downloading` poll has landed in the cache (a refetch issued while
   * it is still in flight would be deduped into it). */
  async function waitForRuntimeDownloading(): Promise<void> {
    await vi.waitFor(() =>
      expect((queryClient.getQueryData(RUNTIME_KEY) as { state?: string } | undefined)?.state).toBe(
        'Downloading',
      ),
    )
  }

  async function refetchRuntime(): Promise<void> {
    await act(async () => {
      await queryClient.refetchQueries({ queryKey: RUNTIME_KEY })
    })
  }

  afterEach(() => {
    cleanup()
    vi.restoreAllMocks()
    vi.unstubAllGlobals()
  })

  beforeEach(() => {
    posts.length = 0
    runtimeState = 'Idle'
    runtimeCalls = 0
    assets = {
      tts_onnx_vocab: { available: true, version: null, state: 'ready' },
      tts_spacy_model: { available: true, version: '3.8.0', state: 'ready' },
      tts_voice_packs: { available: false, version: null, state: 'missing' },
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
          return jsonResponse({
            yt_dlp: { available: true, version: '2026.08.30' },
            ffmpeg: { available: true, version: '7.1', path: 'C:/ffmpeg/bin/ffmpeg.exe' },
            ...assets,
          })
        }
        if (url.includes('/models/download-runtime')) {
          runtimeCalls += 1
          return jsonResponse({ state: runtimeState, variant_id: null, asset: 'tts_voice_packs', fraction: 0.5 })
        }
        if (url.includes('/models/download') && method === 'POST') {
          return jsonResponse({ variant: null, asset: 'tts_voice_packs' }, 202)
        }
        return jsonResponse({})
      }),
    )
    queryClient.clear()
  })

  it('AC-73.10 useTtsJob exports the shared hook, and SettingsPage calls it', () => {
    expect(typeof (ttsJob as Record<string, unknown>).useRefreshDependenciesOnSettle).toBe('function')
    expect(readFileSync(settingsPagePath, 'utf8')).toContain('useRefreshDependenciesOnSettle(')
  })

  it('AC-73.10 Downloading -> Idle invalidates the dependencies query exactly once', async () => {
    const spy = vi.spyOn(queryClient, 'invalidateQueries')
    runtimeState = 'Downloading'
    await renderSettingsPage()
    await vi.waitFor(() => expect(runtimeCalls).toBeGreaterThan(0))
    await waitForRuntimeDownloading()
    expect(depsInvalidations(spy)).toBe(0)
    runtimeState = 'Idle'
    await refetchRuntime()
    await vi.waitFor(() => expect(depsInvalidations(spy)).toBe(1))
    await refetchRuntime()
    await refetchRuntime()
    expect(depsInvalidations(spy)).toBe(1)
  })

  it('AC-73.10 a Downloading -> Failed settle also invalidates once', async () => {
    const spy = vi.spyOn(queryClient, 'invalidateQueries')
    runtimeState = 'Downloading'
    await renderSettingsPage()
    await vi.waitFor(() => expect(runtimeCalls).toBeGreaterThan(0))
    await waitForRuntimeDownloading()
    runtimeState = 'Failed'
    await refetchRuntime()
    await vi.waitFor(() => expect(depsInvalidations(spy)).toBe(1))
  })

  it('AC-73.10 a steady Idle runtime never invalidates the dependencies query', async () => {
    const spy = vi.spyOn(queryClient, 'invalidateQueries')
    await renderSettingsPage()
    await vi.waitFor(() => expect(runtimeCalls).toBeGreaterThan(0))
    await refetchRuntime()
    await refetchRuntime()
    expect(runtimeCalls).toBeGreaterThanOrEqual(3)
    expect(depsInvalidations(spy)).toBe(0)
  })

  it('AC-73.11 the wire list and label include Voice packs', () => {
    expect([...TTS_ASSET_WIRES]).toEqual(['tts_onnx_vocab', 'tts_spacy_model', 'tts_voice_packs'])
    expect((TTS_ASSET_LABELS as Record<string, string>).tts_voice_packs).toBe('Voice packs')
  })

  it('AC-73.11 a missing Voice packs row shows Get, which posts the asset', async () => {
    await renderSettingsPage()
    const row = await vi.waitFor(() => screen.getByTestId('tts-asset-row-tts_voice_packs'))
    expect(row.textContent).toContain('Voice packs')
    expect(row.textContent).toContain('Missing')
    const get = screen.getByTestId('tts-asset-get-btn-tts_voice_packs')
    await userEvent.setup().click(get)
    await vi.waitFor(() => {
      expect(posts).toEqual([
        { url: expect.stringContaining('/models/download'), body: { asset: 'tts_voice_packs' } },
      ])
    })
  })

  it('AC-73.11 a ready Voice packs row has no Get button', async () => {
    assets.tts_voice_packs = { available: true, version: null, state: 'ready' }
    await renderSettingsPage()
    const row = await vi.waitFor(() => screen.getByTestId('tts-asset-row-tts_voice_packs'))
    expect(row.textContent).toContain('Ready')
    expect(screen.queryByTestId('tts-asset-get-btn-tts_voice_packs')).toBeNull()
  })
})

const ESPEAK_RELEASES = 'https://github.com/espeak-ng/espeak-ng/releases'

describe('MEU-74 Settings eSpeak NG row', () => {
  let espeak: { available: boolean; version: string | null; path: string | null } | undefined
  let copied: string[] = []

  async function renderSettingsPage(): Promise<void> {
    await act(async () => {
      render(createElement(QueryClientProvider, { client: queryClient }, createElement(SettingsPage)))
    })
  }

  afterEach(() => {
    cleanup()
    vi.restoreAllMocks()
    vi.unstubAllGlobals()
  })

  beforeEach(() => {
    espeak = { available: false, version: null, path: null }
    copied = []
    mockApi()
    window.api.writeClipboardText = async (text: string) => {
      copied.push(text)
    }
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string) => {
        if (url.includes('/health/dependencies')) {
          return jsonResponse({
            yt_dlp: { available: true, version: '2026.08.30' },
            ffmpeg: { available: true, version: '7.1', path: 'C:/ffmpeg/bin/ffmpeg.exe' },
            tts_onnx_vocab: { available: true, version: null, state: 'ready' },
            tts_spacy_model: { available: true, version: '3.8.0', state: 'ready' },
            tts_voice_packs: { available: true, version: null, state: 'ready' },
            ...(espeak === undefined ? {} : { tts_espeak: espeak }),
          })
        }
        if (url.includes('/models/download-runtime')) {
          return jsonResponse({ state: 'Idle', variant_id: null, asset: null, fraction: 0 })
        }
        return jsonResponse({})
      }),
    )
    queryClient.clear()
  })

  it('AC-74.7 a detected eSpeak NG reads Detected plus the version, with no guidance and no Get', async () => {
    espeak = { available: true, version: '1.52.0', path: 'C:/Program Files/eSpeak NG/espeak-ng.exe' }
    await renderSettingsPage()
    const row = await vi.waitFor(() => screen.getByTestId('tts-espeak-row'))
    expect(row.textContent).toContain('eSpeak NG')
    expect(row.textContent).toContain('Detected')
    expect(row.textContent).toContain('1.52.0')
    expect(screen.queryByTestId('tts-espeak-guidance')).toBeNull()
    expect(within(row).queryAllByRole('button')).toEqual([])
  })

  it('AC-74.7 an absent eSpeak NG reads Not installed and shows the guidance with a copy link', async () => {
    await renderSettingsPage()
    const row = await vi.waitFor(() => screen.getByTestId('tts-espeak-row'))
    expect(row.textContent).toContain('Not installed')
    const guidance = screen.getByTestId('tts-espeak-guidance')
    for (const language of ['Spanish', 'French', 'Hindi', 'Italian', 'Portuguese']) {
      expect(guidance.textContent).toContain(language)
    }
    expect(guidance.textContent).toContain('eSpeak NG')
    expect(guidance.textContent).toContain(ESPEAK_RELEASES)
    expect(within(row).queryByRole('button', { name: /^get/i })).toBeNull()
    expect(screen.queryByTestId('tts-asset-get-btn-tts_espeak')).toBeNull()
    await userEvent.setup().click(within(guidance).getByRole('button', { name: 'Copy link' }))
    await vi.waitFor(() => expect(copied).toEqual([ESPEAK_RELEASES]))
  })

  it('AC-74.7 an older backend without tts_espeak renders no row', async () => {
    espeak = undefined
    await renderSettingsPage()
    await vi.waitFor(() => screen.getByTestId('tts-asset-row-tts_voice_packs'))
    expect(screen.queryByTestId('tts-espeak-row')).toBeNull()
    expect(screen.queryByTestId('tts-espeak-guidance')).toBeNull()
  })
})
