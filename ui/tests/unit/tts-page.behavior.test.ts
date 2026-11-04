/** @vitest-environment jsdom */

/**
 * MEU-56 TTS page composition (AC-56.1–AC-56.5), exercised through the real
 * page against a stubbed fetch ledger. New modules are imported dynamically in
 * the tests that need them, so their absence fails a test, not the suite.
 */
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, render, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { TTSPage } from '../../src/renderer/src/features/tts/TTSPage'
import { PREPARE_STEPS } from '../../src/renderer/src/features/tts/tts-prepare'
import { expectBoundHint } from './helpers/bound-hint'
import { queryClient } from '../../src/renderer/src/lib/query-client'

const here = dirname(fileURLToPath(import.meta.url))
// The run-bar resolver is a new module; a glob keeps its absence a test failure, not a load error.
const runBarModules = import.meta.glob('../../src/renderer/src/features/tts/tts-run-bar.ts')
const pageSource = readFileSync(resolve(here, '../../src/renderer/src/features/tts/TTSPage.tsx'), 'utf8')

type Ledger = Array<{ url: string; method: string; body?: Record<string, unknown> }>

type Job = {
  id: string
  status: string
  output_path: string | null
  segments_done: number
  segments_total: number
  text_preview: string
  text_hash: string
  error_message?: string | null
}

type CatalogRow = (typeof CATALOG)[number]

const VOICES = [
  { voice_id: 'af_heart', language: 'en-us', gender: 'F', style_description: 'warm' },
  { voice_id: 'af_bella', language: 'en-us', gender: 'F', style_description: 'bright' },
  { voice_id: 'bf_emma', language: 'en-gb', gender: 'F', style_description: 'calm' },
]

const CATALOG = [
  { id: 'kokoro-v1.0-pt-fp32', name: 'PyTorch FP32', format: 'pt', precision: 'fp32', size_bytes: 1, path: null, is_downloaded: false },
  { id: 'kokoro-v1.0-onnx-fp16', name: 'ONNX FP16', format: 'onnx', precision: 'fp16', size_bytes: 1, path: 'x', is_downloaded: true },
]

function mockApi(ipc: string[]): void {
  window.api = {
    getBackendUrl: async () => 'http://127.0.0.1:51234/api/v1',
    getToken: async () => 'gui-nonce',
    logStartupMetric: () => undefined,
    showDirectoryDialog: async () => 'D:/audio',
    showFileDialog: async () => undefined,
    showFilesDialog: async () => [],
    getPathForFile: () => '',
    openPath: async (target: string) => {
      ipc.push(`openPath:${target}`)
    },
    showItemInFolder: async (target: string) => {
      ipc.push(`showItemInFolder:${target}`)
    },
    readClipboardText: async () => '',
    writeClipboardText: async () => undefined,
    readTextFile: async () => ({ text: 'from file', basename: 'x.txt' }),
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

describe('MEU-56 TTS page composition', () => {
  let user: ReturnType<typeof userEvent.setup>
  let host: HTMLElement
  const fetches: Ledger = []
  const ipc: string[] = []
  let settings: Record<string, unknown>
  let holdSettings: Promise<void> | null
  let loaded: boolean
  let job: Job | null
  let statusCalls: number
  // Setup-only (MEU-63): mutable catalog, runtime, loaded variant and dependency rows.
  let catalog: CatalogRow[]
  let runtime: Record<string, unknown>
  let loadedId: string
  let deps: Record<string, unknown>

  const path = (url: string): string => new URL(url).pathname.replace('/api/v1', '')
  const puts = (): Array<Record<string, unknown>> =>
    fetches.filter((row) => row.method === 'PUT' && path(row.url) === '/settings/tts').map((row) => row.body ?? {})

  beforeEach(() => {
    user = userEvent.setup()
    fetches.length = 0
    ipc.length = 0
    settings = { input_text: '', voice: 'af_heart', speed: 1, output_format: 'MP3', output_path: '', device: 'auto' }
    holdSettings = null
    loaded = true
    job = null
    statusCalls = 0
    catalog = [...CATALOG]
    runtime = { state: 'Idle', variant_id: null, asset: null, fraction: 0, error_message: null }
    loadedId = 'kokoro-v1.0-onnx-fp16'
    deps = {
      yt_dlp: { available: true, version: '2026.05.15' },
      ffmpeg: { available: true, version: '7.1', path: 'C:/ffmpeg.exe' },
      tts_onnx_vocab: { available: true, version: null, state: 'ready' },
      tts_spacy_model: { available: false, version: null, state: 'missing' },
    }
    queryClient.clear()
    mockApi(ipc)
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input)
        const method = (init?.method ?? 'GET').toUpperCase()
        const body = init?.body ? (JSON.parse(String(init.body)) as Record<string, unknown>) : undefined
        fetches.push({ url, method, body })
        const p = path(url)
        const json = (value: unknown, status = 200): Response => new Response(JSON.stringify(value), { status })
        if (p === '/settings/tts' && method === 'GET') {
          if (holdSettings !== null) {
            await holdSettings
          }
          return json(settings)
        }
        if (p === '/settings/tts' && method === 'PUT') {
          return json({ ...settings, ...body })
        }
        if (p === '/tts/voices') {
          return json({ items: VOICES })
        }
        if (p === '/models/available') {
          return json({ items: catalog })
        }
        if (p === '/models/download' && method === 'POST') {
          return json({ variant: null, asset: body?.asset ?? null }, 202)
        }
        if (p === '/models/load' && method === 'POST') {
          loaded = true
          loadedId = String(body?.variant_id ?? loadedId)
          return json({ is_loaded: true, variant_id: loadedId, device: 'cpu', memory_bytes: 1 })
        }
        if (p === '/models/unload' && method === 'POST') {
          loaded = false
          return new Response(null, { status: 204 })
        }
        if (p === '/health/dependencies') {
          return json(deps)
        }
        if (p === '/models/status') {
          statusCalls += 1
          return json(
            loaded
              ? { is_loaded: true, variant_id: loadedId, device: 'cuda', memory_bytes: 1024 }
              : { is_loaded: false },
          )
        }
        if (p === '/models/download-runtime') {
          return json(runtime)
        }
        if (p === '/tts/prepare') {
          return json({ cleaned_text: `CLEANED:${String(body?.text ?? '')}` })
        }
        if (p === '/tts/generate') {
          job = { id: 'j1', status: 'Generating', output_path: null, segments_done: 2, segments_total: 8, text_preview: 'Hello', text_hash: 'abcdef0123' }
          return json(job, 201)
        }
        if (p === '/tts/j1' && method === 'GET') {
          return json(job)
        }
        return json({})
      }),
    )
  })

  afterEach(() => {
    cleanup()
    queryClient.clear()
    vi.unstubAllGlobals()
  })

  async function renderPage(): Promise<void> {
    await act(async () => {
      host = render(createElement(QueryClientProvider, { client: queryClient }, createElement(TTSPage))).container
    })
    // Setup only: wait for the catalog, status and voices to load.
    // TA-5 (Session 27, MEU-64): the options mount only in the open combobox, so the setup
    // waits on the selection chip instead; every test still starts with the popup closed.
    await vi.waitFor(() => {
      expect(within(host).getByTestId('voice-selected-chip').textContent).toContain(String(settings.voice))
      expect(statusCalls).toBeGreaterThan(0)
    })
    await act(async () => {
      await Promise.resolve()
    })
  }

  const byTestId = (id: string): HTMLElement => within(host).getByTestId(id)

  it('AC-97.4 HINTS generate-btn carries the page:primary chord', async () => {
    await renderPage()
    expectBoundHint(byTestId('generate-btn'), 'page:primary')
  })

  it('AC-56.1 CLEANUP_LABELS covers exactly the prepare steps and checkbox values stay raw ids', async () => {
    const mod = (await import('../../src/renderer/src/features/tts/tts-prepare')) as unknown as {
      CLEANUP_LABELS?: Record<string, string>
    }
    expect(Object.keys(mod.CLEANUP_LABELS ?? {}).sort()).toEqual([...PREPARE_STEPS].sort())
    expect(mod.CLEANUP_LABELS?.urls_emails).toBe('URLs & emails')
    expect(mod.CLEANUP_LABELS?.all_caps).toBe('All caps')
    await renderPage()
    await user.click(byTestId('cleanup-toggle'))
    const boxes = within(byTestId('cleanup-pipeline')).getAllByRole('checkbox') as HTMLInputElement[]
    expect(boxes.map((box) => box.value)).toEqual([...PREPARE_STEPS])
    expect(within(byTestId('cleanup-pipeline')).getByLabelText('URLs & emails')).toBe(
      boxes[PREPARE_STEPS.indexOf('urls_emails')],
    )
  })

  it('AC-56.2 two-column grid with a Text panel and a closed Cleanup disclosure', async () => {
    await renderPage()
    const text = within(host).getByRole('region', { name: 'Text' })
    const voice = within(host).getByRole('region', { name: 'Voice' })
    const grid = text.parentElement as HTMLElement
    expect(grid).toBe(voice.parentElement)
    expect(grid.className).toContain('min-[880px]:grid-cols-[minmax(0,1.45fr)_minmax(300px,1fr)]')
    expect(grid.className).toContain('max-w-[var(--layout-page-max-width)]')
    const area = byTestId('text-input') as HTMLTextAreaElement
    expect(within(text).getByRole('textbox', { name: 'Text' })).toBe(area)
    expect(area.rows).toBe(11)
    expect(area.className).toContain('resize-y')
    expect(text.contains(byTestId('load-file-btn'))).toBe(true)
    expect(text.contains(byTestId('paste-btn'))).toBe(true)
    const toggle = byTestId('cleanup-toggle')
    expect(toggle.getAttribute('aria-expanded')).toBe('false')
    expect(toggle.textContent).toBe('Cleanup · 10 of 11 steps')
    expect(byTestId('cleanup-pipeline').closest('[hidden]')).not.toBeNull()
    const before = fetches.filter((row) => row.method !== 'GET').length
    await user.click(toggle)
    expect(toggle.getAttribute('aria-expanded')).toBe('true')
    expect(byTestId('cleanup-pipeline').closest('[hidden]')).toBeNull()
    expect(fetches.filter((row) => row.method !== 'GET')).toHaveLength(before)
    await user.click(within(byTestId('cleanup-pipeline')).getByLabelText('Numbers'))
    expect(toggle.textContent).toBe('Cleanup · 9 of 11 steps')
    await user.type(area, 'Hello')
    // TA-2 (Session 27, MEU-64): no cleaned preview before Preview runs; no raw pane at all.
    expect(within(host).queryByTestId('preview-cleaned')).toBeNull()
    await user.click(byTestId('preview-cleanup-btn'))
    await vi.waitFor(() => {
      expect(byTestId('preview-cleaned').textContent).toBe('CLEANED:Hello')
    })
    const prepare = fetches.find((row) => path(row.url) === '/tts/prepare')
    expect(Object.keys(prepare?.body ?? {}).sort()).toEqual(['enabled_steps', 'text'])
    expect(within(host).queryByTestId('preview-raw')).toBeNull()
  })

  it('AC-56.3 model chip, Manage disclosure, full details and device PUT', async () => {
    await renderPage()
    const chip = byTestId('loaded-model')
    expect(chip.textContent).toBe('ONNX FP16 · cuda')
    expect(chip.getAttribute('data-tone')).toBe('success')
    expect(within(host).getByRole('region', { name: 'Voice' }).contains(chip)).toBe(true)
    const manage = byTestId('model-manage-toggle')
    expect(manage.getAttribute('aria-expanded')).toBe('false')
    expect(byTestId('model-manager').closest('[hidden]')).not.toBeNull()
    await user.click(manage)
    expect(byTestId('loaded-model-details').textContent).toBe('Loaded: kokoro-v1.0-onnx-fp16 (cuda) · 1024 B')
    // TA-3 (Session 27, MEU-63): one picker row; the action button's test id follows MODEL_ACTION.
    const rows = within(host).getAllByTestId('model-row')
    expect(rows).toHaveLength(1)
    await user.selectOptions(byTestId('model-select'), 'kokoro-v1.0-pt-fp32')
    expect(within(rows[0]).getByTestId('model-get-btn')).toBeTruthy()
    // RULE-2: a late status refetch updates the chip but never closes Manage.
    loaded = false
    await act(async () => {
      await queryClient.invalidateQueries({ queryKey: ['models', 'status'] })
    })
    await vi.waitFor(() => {
      expect(byTestId('loaded-model').textContent).toBe('No model loaded')
    })
    expect(byTestId('loaded-model').getAttribute('data-tone')).toBe('warning')
    expect(manage.getAttribute('aria-expanded')).toBe('true')
    expect(byTestId('model-manager').closest('[hidden]')).toBeNull()
    await user.selectOptions(byTestId('device-select'), 'cpu')
    await vi.waitFor(() => {
      expect(puts()).toContainEqual({ device: 'cpu' })
    })
  })

  it('AC-56.4 voice listbox: roving focus, arrows move focus only, every activation PUTs once', async () => {
    await renderPage()
    // TA-6 (Session 27, MEU-64): the listbox is the combobox popup; open it first.
    await user.click(byTestId('voice-combobox'))
    const list = byTestId('voice-grid')
    expect(list.getAttribute('role')).toBe('listbox')
    expect(list.getAttribute('aria-label')).toBe('Voice')
    const options = within(list).getAllByRole('option')
    expect(options.map((node) => node.getAttribute('aria-selected'))).toEqual(['true', 'false', 'false'])
    expect(options.map((node) => node.tabIndex)).toEqual([0, -1, -1])
    expect(options[0].textContent).toContain('af_heart')
    expect(options[0].textContent).toContain('warm')
    expect(options[0].className).not.toMatch(/bg-bg-subtle/)
    // Re-activating the already-selected voice still PUTs (tts-generate.test.ts:350-354).
    await user.click(options[0])
    await vi.waitFor(() => {
      expect(puts().filter((row) => 'voice' in row)).toEqual([{ voice: 'af_heart' }])
    })
    options[0].focus()
    await user.keyboard('{ArrowDown}')
    expect(document.activeElement).toBe(options[1])
    expect(puts().filter((row) => 'voice' in row)).toHaveLength(1)
    await user.keyboard('{End}')
    expect(document.activeElement).toBe(options[2])
    await user.keyboard('{Enter}')
    await vi.waitFor(() => {
      expect(puts().filter((row) => 'voice' in row)).toEqual([{ voice: 'af_heart' }, { voice: 'bf_emma' }])
    })
    expect(within(list).getAllByRole('option')[2].getAttribute('aria-selected')).toBe('true')
    expect(within(list).getAllByRole('option')[2].tabIndex).toBe(0)
  })

  it('AC-56.4 speed presets, slider range and native format select', async () => {
    await renderPage()
    const slider = byTestId('speed-slider') as HTMLInputElement
    expect([slider.min, slider.max, slider.step]).toEqual(['0.5', '2', '0.1'])
    expect(within(host).getByText('Speed 1.0×')).toBeTruthy()
    const one = byTestId('speed-preset-1-0') as HTMLInputElement
    expect(one.type).toBe('radio')
    expect(one.checked).toBe(true)
    await user.click(byTestId('speed-preset-1-1'))
    await vi.waitFor(() => {
      expect(puts()).toContainEqual({ speed: 1.1 })
    })
    expect(slider.value).toBe('1.1')
    expect(within(host).getByText('Speed 1.1×')).toBeTruthy()
    const format = byTestId('format-select') as HTMLSelectElement
    expect(format.tagName).toBe('SELECT')
    expect(Array.from(format.options).map((option) => option.value)).toEqual(['MP3', 'WAV'])
    expect(within(host).queryByText(/preview voice/i)).toBeNull()
  })

  it('AC-56.4 settings hydration never overwrites a choice the user made first (RULE-2)', async () => {
    settings = { ...settings, input_text: 'saved text', voice: 'af_bella', speed: 0.8 }
    let release: () => void = () => undefined
    holdSettings = new Promise<void>((done) => {
      release = done
    })
    await act(async () => {
      host = render(createElement(QueryClientProvider, { client: queryClient }, createElement(TTSPage))).container
    })
    await user.type(byTestId('text-input'), 'typed first')
    await act(async () => {
      release()
      await Promise.resolve()
    })
    await vi.waitFor(() => {
      expect(within(host).getByText('Speed 0.8×')).toBeTruthy()
    })
    expect((byTestId('text-input') as HTMLTextAreaElement).value).toBe('typed first')
    // TA-6 (Session 27, MEU-64): open the combobox popup before reading its options.
    await user.click(byTestId('voice-combobox'))
    await vi.waitFor(() => {
      const selected = within(byTestId('voice-grid')).getAllByRole('option').find((node) => node.getAttribute('aria-selected') === 'true')
      expect(selected?.textContent).toContain('af_bella')
    })
  })

  it('AC-56.5 static run bar: idle output slot, actionable-only open buttons', async () => {
    expect(Object.keys(runBarModules), 'tts-run-bar.ts exists').toHaveLength(1)
    const slot = (await Object.values(runBarModules)[0]()) as {
      resolveRunBarSlot?: (input: { error: string | null; status: string }) => string
    }
    expect(slot.resolveRunBarSlot?.({ error: 'x', status: 'Generating' })).toBe('error')
    expect(slot.resolveRunBarSlot?.({ error: null, status: 'Generating' })).toBe('progress')
    expect(slot.resolveRunBarSlot?.({ error: null, status: 'Pending' })).toBe('progress')
    expect(slot.resolveRunBarSlot?.({ error: null, status: 'Done' })).toBe('output')
    expect(slot.resolveRunBarSlot?.({ error: null, status: 'Idle' })).toBe('output')
    await renderPage()
    const last = byTestId('last-output')
    expect(last.textContent).toBe('No output yet')
    expect(within(host).queryByTestId('segment-progress')).toBeNull()
    expect(within(host).queryByTestId('open-output-btn')).toBeNull()
    expect(within(host).queryByTestId('open-output-folder-btn')).toBeNull()
    const bar = byTestId('generate-btn').parentElement as HTMLElement
    const runBar = bar.closest('[data-run-bar]') as HTMLElement
    expect(runBar).not.toBeNull()
    expect(runBar.className).not.toMatch(/sticky|fixed/)
    const grid = within(host).getByRole('region', { name: 'Text' }).parentElement as HTMLElement
    expect(grid.compareDocumentPosition(runBar) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    for (const id of ['output-path', 'browse-output-btn', 'cancel-btn']) {
      expect(runBar.contains(byTestId(id)), id).toBe(true)
    }
    expect(pageSource).not.toMatch(/width\s*:/)
  })

  it('AC-56.5 configured output makes open buttons actionable while idle', async () => {
    settings = { ...settings, output_path: 'D:/audio/out.mp3' }
    await renderPage()
    await vi.waitFor(() => {
      expect(within(host).getByTestId('open-output-btn')).toBeTruthy()
    })
    await user.click(byTestId('open-output-folder-btn'))
    await vi.waitFor(() => {
      expect(ipc).toContain('showItemInFolder:D:/audio/out.mp3')
    })
    expect(byTestId('last-output').textContent).toBe('No output yet')
  })

  it('AC-56.5 generating shows the shared ProgressBar in the slot, then output on completion', async () => {
    await renderPage()
    await user.type(byTestId('text-input'), 'Hello world')
    await user.click(byTestId('generate-btn'))
    await vi.waitFor(() => {
      expect(within(host).getByTestId('segment-progress')).toBeTruthy()
    })
    const progress = byTestId('segment-progress-bar')
    expect(progress.getAttribute('role')).toBe('progressbar')
    expect(progress.getAttribute('aria-valuenow')).toBe('25')
    expect(byTestId('segment-progress').textContent).toContain('Segments 2/8')
    expect(within(host).queryByTestId('last-output')).toBeNull()
    job = { ...(job as Job), status: 'Done', segments_done: 8, output_path: 'D:/audio/hello.mp3' }
    await act(async () => {
      await queryClient.invalidateQueries({ queryKey: ['tts', 'job'] })
    })
    await vi.waitFor(() => {
      expect(byTestId('last-output').textContent).toBe('D:/audio/hello.mp3')
    })
    expect(within(host).queryByTestId('segment-progress')).toBeNull()
    await user.click(byTestId('open-output-btn'))
    await vi.waitFor(() => {
      expect(ipc).toContain('openPath:D:/audio/hello.mp3')
    })
  })

  it('AC-56.5 an error replaces the slot content', async () => {
    await renderPage()
    await act(async () => {
      window.dispatchEvent(new CustomEvent('av-kit:tts:error', { detail: 'synthesis failed' }))
    })
    const banner = byTestId('error-banner')
    expect(banner.textContent).toBe('synthesis failed')
    expect(banner.getAttribute('role')).toBe('alert')
    expect(banner.closest('[data-run-bar]')).not.toBeNull()
    expect(within(host).queryByTestId('last-output')).toBeNull()
    expect(within(host).queryByTestId('segment-progress')).toBeNull()
  })

  const posts = (route: string): Array<Record<string, unknown>> =>
    fetches.filter((row) => row.method === 'POST' && path(row.url) === route).map((row) => row.body ?? {})

  const optionLabels = (): string[] =>
    Array.from((byTestId('model-select') as HTMLSelectElement).options).map((option) => option.textContent ?? '')

  it('AC-63.1 model picker lists every variant with its state; device sits in the same row', async () => {
    runtime = { state: 'Downloading', variant_id: 'kokoro-v1.0-pt-fp32', asset: null, fraction: 0.42, error_message: null }
    await renderPage()
    const select = byTestId('model-select') as HTMLSelectElement
    expect(select.tagName).toBe('SELECT')
    await vi.waitFor(() => {
      expect(optionLabels()).toEqual(['PyTorch FP32 — downloading 42%', 'ONNX FP16 — loaded'])
    })
    expect(Array.from(select.options).map((option) => option.value)).toEqual([
      'kokoro-v1.0-pt-fp32',
      'kokoro-v1.0-onnx-fp16',
    ])
    expect(select.value).toBe('kokoro-v1.0-onnx-fp16')
    const row = byTestId('model-row')
    expect(row.contains(select)).toBe(true)
    expect(row.contains(byTestId('device-select'))).toBe(true)
    expect(optionLabels().filter((label) => label.endsWith('— loaded'))).toHaveLength(1)
  })

  it('AC-63.1 default selection falls back to the first downloaded, then the first variant', async () => {
    loaded = false
    await renderPage()
    await vi.waitFor(() => {
      expect((byTestId('model-select') as HTMLSelectElement).value).toBe('kokoro-v1.0-onnx-fp16')
    })
    expect(optionLabels()).toEqual(['PyTorch FP32 — not downloaded', 'ONNX FP16 — downloaded'])
    cleanup()
    queryClient.clear()
    catalog = [CATALOG[0]]
    await renderPage()
    await vi.waitFor(() => {
      expect((byTestId('model-select') as HTMLSelectElement).value).toBe('kokoro-v1.0-pt-fp32')
    })
  })

  it('AC-63.2 one state-driven action: Get downloads, Load loads, Unload unloads', async () => {
    catalog = [
      ...CATALOG,
      { id: 'kokoro-v1.0-onnx-int8', name: 'ONNX INT8', format: 'onnx', precision: 'int8', size_bytes: 1, path: 'y', is_downloaded: true },
    ]
    await renderPage()
    const row = byTestId('model-row')
    // Loaded variant selected by default: Unload.
    const unload = await vi.waitFor(() => within(row).getByTestId('unload-btn'))
    expect(unload.textContent).toBe('Unload')
    expect(within(row).queryByTestId('model-get-btn')).toBeNull()
    expect(within(row).queryByTestId('model-load-btn')).toBeNull()
    await user.click(unload)
    await vi.waitFor(() => {
      expect(fetches.some((row2) => row2.method === 'POST' && path(row2.url) === '/models/unload')).toBe(true)
    })
    // Not downloaded: Get posts a download and never a load.
    await user.selectOptions(byTestId('model-select'), 'kokoro-v1.0-pt-fp32')
    const get = within(row).getByTestId('model-get-btn')
    expect(get.textContent).toBe('Get')
    await user.click(get)
    await vi.waitFor(() => {
      expect(posts('/models/download')).toEqual([{ variant_id: 'kokoro-v1.0-pt-fp32' }])
    })
    expect(posts('/models/load')).toEqual([])
    // Downloaded, not loaded: Load posts the variant and the device.
    await user.selectOptions(byTestId('model-select'), 'kokoro-v1.0-onnx-int8')
    const load = within(row).getByTestId('model-load-btn')
    expect(load.textContent).toBe('Load')
    await user.click(load)
    await vi.waitFor(() => {
      expect(posts('/models/load')).toEqual([{ variant_id: 'kokoro-v1.0-onnx-int8', device: 'auto' }])
    })
  })

  it('AC-63.2 the action is disabled while any download runs; the downloading variant reads Getting…', async () => {
    runtime = { state: 'Downloading', variant_id: 'kokoro-v1.0-pt-fp32', asset: null, fraction: 0.1, error_message: null }
    await renderPage()
    await user.selectOptions(byTestId('model-select'), 'kokoro-v1.0-pt-fp32')
    const busyBtn = await vi.waitFor(() => within(byTestId('model-row')).getByTestId('model-get-btn'))
    expect(busyBtn.textContent).toBe('Getting…')
    expect((busyBtn as HTMLButtonElement).disabled).toBe(true)
    await user.selectOptions(byTestId('model-select'), 'kokoro-v1.0-onnx-fp16')
    expect((within(byTestId('model-row')).getByTestId('unload-btn') as HTMLButtonElement).disabled).toBe(true)
    await user.click(within(byTestId('model-row')).getByTestId('unload-btn'))
    expect(fetches.filter((row) => row.method === 'POST')).toEqual([])
  })

  it('AC-63.3 readiness chips beside the picker; Get posts the asset; downloading shows progress', async () => {
    await renderPage()
    const vocab = await vi.waitFor(() => byTestId('tts-asset-chip-tts_onnx_vocab'))
    expect(vocab.textContent).toContain('Ready')
    expect(within(host).queryByTestId('tts-asset-get-btn-tts_onnx_vocab')).toBeNull()
    expect(byTestId('tts-asset-chip-tts_spacy_model').textContent).toContain('Missing')
    expect(byTestId('model-manager').parentElement?.contains(byTestId('tts-asset-chip-tts_spacy_model'))).toBe(true)
    await user.click(byTestId('tts-asset-get-btn-tts_spacy_model'))
    await vi.waitFor(() => {
      expect(posts('/models/download')).toEqual([{ asset: 'tts_spacy_model' }])
    })
    cleanup()
    queryClient.clear()
    runtime = { state: 'Downloading', variant_id: null, asset: 'tts_spacy_model', fraction: 0.5, error_message: null }
    deps = { ...deps, tts_spacy_model: { available: false, version: null, state: 'downloading' } }
    await renderPage()
    const bar = await vi.waitFor(() => byTestId('download-progress-bar'))
    expect(bar.getAttribute('aria-valuenow')).toBe('50')
    expect((byTestId('tts-asset-get-btn-tts_spacy_model') as HTMLButtonElement).disabled).toBe(true)
  })

  it('AC-63.5 a Failed job shows its error_message in the run bar; a Done job never does', async () => {
    await renderPage()
    await user.type(byTestId('text-input'), 'Hello world')
    await user.click(byTestId('generate-btn'))
    await vi.waitFor(() => {
      expect(within(host).getByTestId('segment-progress')).toBeTruthy()
    })
    job = { ...(job as Job), status: 'Failed', error_message: 'tts asset missing: tts_spacy_model' }
    await act(async () => {
      await queryClient.invalidateQueries({ queryKey: ['tts', 'job'] })
    })
    await vi.waitFor(() => {
      expect(byTestId('error-banner').textContent).toBe('tts asset missing: tts_spacy_model')
    })
    job = { ...(job as Job), status: 'Done', output_path: 'D:/a.mp3', error_message: 'stale' }
    await act(async () => {
      await queryClient.invalidateQueries({ queryKey: ['tts', 'job'] })
    })
    await vi.waitFor(() => {
      expect(within(host).queryByTestId('error-banner')).toBeNull()
    })
  })

  it('AC-64.1 Apply cleanup replaces the text, persists it once and clears the preview', async () => {
    await renderPage()
    const area = byTestId('text-input') as HTMLTextAreaElement
    await user.click(byTestId('cleanup-toggle'))
    const apply = byTestId('apply-cleanup-btn') as HTMLButtonElement
    expect(apply.disabled).toBe(true)
    await user.type(area, 'Hello')
    await user.click(byTestId('preview-cleanup-btn'))
    await vi.waitFor(() => {
      expect(byTestId('preview-cleaned').textContent).toBe('CLEANED:Hello')
    })
    const before = fetches.filter((row) => path(row.url) === '/tts/prepare').length
    await user.click(apply)
    await vi.waitFor(() => {
      expect(area.value).toBe('CLEANED:Hello')
    })
    const prepares = fetches.filter((row) => path(row.url) === '/tts/prepare')
    expect(prepares).toHaveLength(before + 1)
    expect(prepares[prepares.length - 1].body?.text).toBe('Hello')
    expect(within(host).queryByTestId('preview-cleaned')).toBeNull()
    await vi.waitFor(() => {
      expect(puts().filter((row) => 'input_text' in row).at(-1)).toEqual({ input_text: 'CLEANED:Hello' })
    })
  })

  it('AC-64.1 a failed prepare leaves the text unchanged and shows the error', async () => {
    await renderPage()
    const area = byTestId('text-input') as HTMLTextAreaElement
    await user.type(area, 'Keep me')
    // Setup: let the typing debounce PUT land first, so only the Apply path is measured.
    await vi.waitFor(() => {
      expect(puts().some((row) => row.input_text === 'Keep me')).toBe(true)
    })
    await user.click(byTestId('cleanup-toggle'))
    vi.mocked(fetch).mockImplementationOnce(async () =>
      new Response(JSON.stringify({ error: { code: 'SpacyModelNotFoundError', message: 'en_core_web_sm is not available', details: null } }), {
        status: 503,
      }),
    )
    const putsBefore = puts().filter((row) => 'input_text' in row).length
    await user.click(byTestId('apply-cleanup-btn'))
    await vi.waitFor(() => {
      expect(byTestId('error-banner').textContent).toContain('en_core_web_sm is not available')
    })
    expect(area.value).toBe('Keep me')
    await new Promise((done) => setTimeout(done, 350))
    expect(puts().filter((row) => 'input_text' in row)).toHaveLength(putsBefore)
  })

  it('AC-64.2 the cleaned preview unmounts when the text changes', async () => {
    await renderPage()
    await user.type(byTestId('text-input'), 'Hi')
    await user.click(byTestId('cleanup-toggle'))
    await user.click(byTestId('preview-cleanup-btn'))
    await vi.waitFor(() => {
      expect(byTestId('preview-cleaned')).toBeTruthy()
    })
    await user.type(byTestId('text-input'), '!')
    expect(within(host).queryByTestId('preview-cleaned')).toBeNull()
  })

  it('AC-64.4 searchable voice combobox: filter, group by language, keyboard select, Escape keeps the voice', async () => {
    await renderPage()
    const input = byTestId('voice-combobox') as HTMLInputElement
    expect(input.getAttribute('role')).toBe('combobox')
    expect(input.getAttribute('aria-expanded')).toBe('false')
    expect(within(host).queryByTestId('voice-grid')).toBeNull()
    expect(byTestId('voice-selected-chip').textContent).toContain('af_heart')
    await user.click(input)
    expect(input.getAttribute('aria-expanded')).toBe('true')
    const list = byTestId('voice-grid')
    expect(input.getAttribute('aria-controls')).toBe(list.id)
    expect(within(list).getAllByTestId('voice-card')).toHaveLength(VOICES.length)
    const groups = within(list).getAllByRole('group')
    expect(groups.map((group) => group.getAttribute('aria-label'))).toEqual(['en-us', 'en-gb'])
    await user.type(input, 'bella')
    expect(within(list).getAllByRole('option').map((node) => node.textContent)).toEqual([
      expect.stringContaining('af_bella'),
    ])
    await user.clear(input)
    await user.type(input, 'en-gb')
    expect(within(list).getAllByRole('option').map((node) => node.textContent)).toEqual([
      expect.stringContaining('bf_emma'),
    ])
    await user.keyboard('{ArrowDown}')
    expect(input.getAttribute('aria-activedescendant')).toBe(within(list).getAllByRole('option')[0].id)
    await user.keyboard('{Enter}')
    await vi.waitFor(() => {
      expect(puts().filter((row) => 'voice' in row)).toEqual([{ voice: 'bf_emma' }])
    })
    expect(byTestId('voice-selected-chip').textContent).toContain('bf_emma')
    // Escape after moving to another option changes nothing.
    await user.clear(input)
    await user.keyboard('{ArrowDown}{ArrowDown}{Escape}')
    expect(input.getAttribute('aria-expanded')).toBe('false')
    expect(puts().filter((row) => 'voice' in row)).toHaveLength(1)
    expect(byTestId('voice-selected-chip').textContent).toContain('bf_emma')
  })

  it('AC-64.4 no match shows the empty state and Enter sends nothing', async () => {
    await renderPage()
    const input = byTestId('voice-combobox')
    await user.click(input)
    await user.type(input, 'zzz-no-voice')
    expect(within(byTestId('voice-grid')).queryAllByRole('option')).toHaveLength(0)
    expect(byTestId('voice-grid').textContent).toContain('No voices match')
    await user.keyboard('{Enter}')
    expect(puts().filter((row) => 'voice' in row)).toEqual([])
  })

  it('AC-64.5 the language select sits in the open popup and ANDs with the query', async () => {
    await renderPage()
    expect(within(host).queryByTestId('language-select')).toBeNull()
    await user.click(byTestId('voice-combobox'))
    const language = byTestId('language-select') as HTMLSelectElement
    expect(byTestId('voice-grid').parentElement?.contains(language)).toBe(true)
    expect(Array.from(language.options).map((option) => option.textContent)).toEqual(['All', 'en-us', 'en-gb'])
    await user.selectOptions(language, 'en-gb')
    await user.type(byTestId('voice-combobox'), 'af_')
    expect(within(byTestId('voice-grid')).queryAllByRole('option')).toHaveLength(0)
    expect(byTestId('voice-grid').textContent).toContain('No voices match')
  })

  // MEU-79 (Session 35): the device list comes from the selected catalog row (DEVICE_SELECT_VALUE).
  const withDevices = (row: CatalogRow, devices: string[]): CatalogRow =>
    ({ ...row, devices }) as unknown as CatalogRow

  const deviceValues = (): string[] =>
    Array.from((byTestId('device-select') as HTMLSelectElement).options).map((option) => option.value)

  const selectedModelIs = async (id: string): Promise<void> => {
    // Setup only: the catalog and status have loaded and the default selection is in place.
    await vi.waitFor(() => {
      expect((byTestId('model-select') as HTMLSelectElement).value).toBe(id)
    })
  }

  it('AC-79.1 device options are the selected row devices, never the static four', async () => {
    catalog = [withDevices(CATALOG[0], ['auto', 'cuda', 'cpu']), withDevices(CATALOG[1], ['auto', 'cpu'])]
    await renderPage()
    await selectedModelIs('kokoro-v1.0-onnx-fp16')
    expect(deviceValues()).toEqual(['auto', 'cpu'])
    await user.selectOptions(byTestId('model-select'), 'kokoro-v1.0-pt-fp32')
    expect(deviceValues()).toEqual(['auto', 'cuda', 'cpu'])
    expect(deviceValues()).not.toContain('mps')
  })

  it('AC-79.2 a stored device the row lacks shows and loads as auto without a settings PUT', async () => {
    settings = { ...settings, device: 'cuda' }
    loaded = false
    catalog = [withDevices(CATALOG[0], ['auto', 'cuda', 'cpu']), withDevices(CATALOG[1], ['auto', 'cpu'])]
    await renderPage()
    await selectedModelIs('kokoro-v1.0-onnx-fp16')
    expect((byTestId('device-select') as HTMLSelectElement).value).toBe('auto')
    await user.click(within(byTestId('model-row')).getByTestId('model-load-btn'))
    await vi.waitFor(() => {
      expect(posts('/models/load')).toEqual([{ variant_id: 'kokoro-v1.0-onnx-fp16', device: 'auto' }])
    })
    expect(fetches.filter((row) => row.method === 'PUT')).toEqual([])
    await user.selectOptions(byTestId('model-select'), 'kokoro-v1.0-pt-fp32')
    expect((byTestId('device-select') as HTMLSelectElement).value).toBe('cuda')
    expect(fetches.filter((row) => row.method === 'PUT')).toEqual([])
  })

  it('AC-79.3 a catalog row without devices offers auto and cpu only', async () => {
    await renderPage()
    await selectedModelIs('kokoro-v1.0-onnx-fp16')
    expect(deviceValues()).toEqual(['auto', 'cpu'])
    expect(deviceValues()).not.toContain('mps')
  })

  it('AC-79.4 a 422 ModelLoadError from Load shows its message in the error banner', async () => {
    loaded = false
    await renderPage()
    await selectedModelIs('kokoro-v1.0-onnx-fp16')
    const base = vi.mocked(fetch).getMockImplementation()
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      if (path(String(input)) === '/models/load') {
        return new Response(
          JSON.stringify({ error: { code: 'ModelLoadError', message: 'ONNX session failed', details: null } }),
          { status: 422 },
        )
      }
      return (base as typeof fetch)(input, init)
    })
    await user.click(within(byTestId('model-row')).getByTestId('model-load-btn'))
    await vi.waitFor(() => {
      expect(byTestId('error-banner').textContent).toBe('ONNX session failed')
    })
    expect(byTestId('error-banner').textContent).not.toContain('Failed to fetch')
  })

  it('AC-79.6 the voice panel uses the VOICE_GRID classes', async () => {
    await renderPage()
    await selectedModelIs('kokoro-v1.0-onnx-fp16')
    const rowClasses = byTestId('model-row').className.split(/\s+/)
    expect(rowClasses).toContain('grid')
    expect(rowClasses).not.toContain('flex-wrap')
    for (const id of ['model-select', 'device-select']) {
      const classes = byTestId(id).className.split(/\s+/)
      expect(classes, id).not.toContain('w-[110px]')
      expect(classes, id).not.toContain('flex-1')
    }
    expect(within(byTestId('model-row')).getByTestId('unload-btn').className.split(/\s+/)).toContain('h-9')
    const format = byTestId('format-select')
    // The select's own parent is the SelectInput root; the w-28 wrapper holds that root.
    expect(format.parentElement?.parentElement?.className).toBe('w-28')
    expect(format.className.split(/\s+/)).not.toContain('w-[90px]')
    const slider = byTestId('speed-slider')
    expect(slider.className.split(/\s+/)).toContain('h-9')
    expect(slider.parentElement?.parentElement?.className.split(/\s+/)).toContain('grid')
  })

  const outputPathPuts = (): Array<Record<string, unknown>> => puts().filter((body) => 'output_path' in body)

  it('AC-96.5 PAGE_STATE TTS publishes tts:prepare from the Preview button expression', async () => {
    // The command-state module is new (MEU-96); a glob keeps its absence a test failure.
    const commandStateModules = import.meta.glob('../../src/renderer/src/registry/command-state.ts')
    const loader = commandStateModules['../../src/renderer/src/registry/command-state.ts']
    expect(loader, 'registry/command-state.ts exists').toBeDefined()
    const state = (await loader?.()) as { getCommandState: (page: string) => Partial<Record<string, boolean>> }

    await renderPage()
    await vi.waitFor(() => {
      expect(state.getCommandState('/tts')['tts:prepare']).toBe(false)
    })
    await user.type(byTestId('text-input'), 'hello')
    await vi.waitFor(() => {
      expect(state.getCommandState('/tts')['tts:prepare']).toBe(true)
    })
  })

  it('AC-93.3 output-path is a read-only PathRow in the run bar; Browse PUTs once, cancel sends nothing', async () => {
    await renderPage()
    const labelled = within(host).queryAllByLabelText('Output path')
    expect(labelled).toHaveLength(1)
    const field = labelled[0] as HTMLInputElement
    expect(field.getAttribute('data-testid')).toBe('output-path')
    expect(field.readOnly).toBe(true)
    const label = host.querySelector('label[for="tts-output-path"]')
    expect(label, 'the PathRow label for tts-output-path').not.toBeNull()
    const row = label?.parentElement ?? null
    expect(row?.contains(field)).toBe(true)
    expect(row?.contains(byTestId('browse-output-btn'))).toBe(true)
    expect(row?.closest('[data-run-bar]')).not.toBeNull()
    // The field shows OUTPUT_DEFAULT while settings.output_path is empty; the AC is that it keeps its value.
    const initial = field.value
    await user.type(field, 'typed')
    expect(field.value).toBe(initial)
    window.api.showDirectoryDialog = async () => undefined
    await user.click(byTestId('browse-output-btn'))
    await act(async () => {
      await Promise.resolve()
    })
    expect(field.value).toBe(initial)
    expect(outputPathPuts(), 'cancel sends no PUT').toHaveLength(0)
    window.api.showDirectoryDialog = async () => 'D:/audio'
    await user.click(byTestId('browse-output-btn'))
    await vi.waitFor(() => {
      expect(field.value).toBe('D:/audio')
      expect(outputPathPuts()).toEqual([{ output_path: 'D:/audio' }])
    })
  })

  it('AC-93.3 Browse is disabled while a job request runs', async () => {
    let release = (): void => undefined
    const gate = new Promise<void>((resolve) => {
      release = resolve
    })
    const base = globalThis.fetch
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      if (path(String(input)) === '/tts/generate') {
        await gate
      }
      return base(input, init)
    }))
    await renderPage()
    await user.type(byTestId('text-input'), 'Hello world')
    await user.click(byTestId('generate-btn'))
    await vi.waitFor(() => {
      expect((byTestId('browse-output-btn') as HTMLButtonElement).disabled).toBe(true)
    })
    await act(async () => {
      release()
      await Promise.resolve()
    })
    await vi.waitFor(() => {
      expect((byTestId('browse-output-btn') as HTMLButtonElement).disabled).toBe(false)
    })
  })
})
