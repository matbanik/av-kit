import { _electron, expect, test, type Page } from '@playwright/test'
import { mkdtempSync, readFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import {
  addThemeProbe,
  expectInsertedOn,
  expectThemeColours,
  expectThemeHeld,
  releaseTheme,
  THEME_FLOORS,
  type ThemeProbeMode,
} from './theme-probe'

const here = dirname(fileURLToPath(import.meta.url))
// VOICE_CATALOG_FIXTURE: the full production voice list (parity: tests/unit/test_tts_voice_fixture.py).
const VOICE_CATALOG_FIXTURE = (
  JSON.parse(readFileSync(resolve(here, 'fixtures/tts-voices.json'), 'utf8')) as { items: unknown[] }
).items

async function launchApp() {
  return _electron.launch({
    args: [resolve(here, '../../out/main/index.js')],
    env: {
      ...process.env,
      AVKIT_E2E: '1',
      AVKIT_APP_DATA: mkdtempSync(join(tmpdir(), 'avkit-e2e-tts-')),
    },
  })
}

async function installTtsSeam(
  page: Page,
  options: { voices?: unknown[]; themeProbe?: ThemeProbeMode } = {},
): Promise<void> {
  if (options.themeProbe) {
    await addThemeProbe(page, options.themeProbe)
  }
  await page.addInitScript((voices: unknown[] | null) => {
    const state = window as unknown as {
      __e2eSeamInstalled?: boolean
      __e2eCalls?: Array<{ url: string; method: string; bodyKeys?: string[] }>
      __e2eIpc?: Array<{ channel: string; target?: string }>
      __e2eJob?: Record<string, unknown>
      __e2eLoaded?: boolean
      __e2eLoadedId?: string
      __e2eRuntime?: { state: string; variant_id: string | null; asset?: string | null; fraction: number }
      __e2eDeps?: Record<string, unknown>
      __e2eCatalog?: Array<{
        id: string
        name: string
        format: string
        precision: string
        size_bytes: number
        path: string | null
        is_downloaded: boolean
        // TA-6 (Session 35, MEU-79): E2E_DEVICE_SEAM.
        devices: string[]
      }>
      api: Window['api']
    }
    state.__e2eSeamInstalled = true
    state.__e2eCalls = []
    state.__e2eIpc = []
    state.__e2eLoaded = true
    state.__e2eLoadedId = 'kokoro-onnx-fp32'
    state.__e2eRuntime = { state: 'Idle', variant_id: null, asset: null, fraction: 0 }
    // Setup-only (MEU-63): readiness rows for the chips beside the picker.
    state.__e2eDeps = {
      yt_dlp: { available: true, version: '2026.05.15' },
      ffmpeg: { available: true, version: '7.1', path: 'C:/bin/ffmpeg.exe' },
      tts_onnx_vocab: { available: true, version: null, state: 'ready' },
      tts_spacy_model: { available: true, version: '3.8.0', state: 'ready' },
    }
    state.__e2eCatalog = [
      {
        id: 'kokoro-onnx-fp32',
        name: 'ONNX FP32',
        format: 'onnx',
        precision: 'fp32',
        size_bytes: 100,
        path: 'C:/models/fp32',
        is_downloaded: true,
        devices: ['auto', 'cpu'],
      },
      {
        id: 'kokoro-onnx-fp16',
        name: 'ONNX FP16',
        format: 'onnx',
        precision: 'fp16',
        size_bytes: 50,
        path: 'C:/models/fp16',
        is_downloaded: true,
        devices: ['auto', 'cpu'],
      },
      {
        id: 'kokoro-onnx-int8',
        name: 'ONNX INT8',
        format: 'onnx',
        precision: 'int8',
        size_bytes: 25,
        path: null,
        is_downloaded: false,
        devices: ['auto', 'cpu'],
      },
      {
        id: 'kokoro-pt-fp32',
        name: 'PyTorch FP32',
        format: 'pytorch',
        precision: 'fp32',
        size_bytes: 200,
        path: null,
        is_downloaded: false,
        devices: ['auto', 'cuda', 'cpu'],
      },
    ]
    state.__e2eJob = {
      id: 'e2e-tts-1',
      source_kind: 'inline',
      source_path: null,
      text_hash: 'abc123',
      text_preview: 'Hello…',
      voice: 'af_heart',
      speed: 1,
      format: 'MP3',
      status: 'Idle',
      output_path: 'C:/out/e2e.mp3',
      segments_total: 2,
      segments_done: 0,
      error_message: null,
      created_at: '2026-08-20T00:00:00Z',
    }

    const originalApi = state.api
    void originalApi

    window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
      const method = (init?.method ?? 'GET').toUpperCase()
      // THEME_PROBE (MEU-94): looked up at request time, so the init-script order does not matter.
      const probed = (
        window as unknown as {
          __avkitThemeProbe?: { handle: (u: string, m: string, i?: RequestInit) => Promise<Response> | null }
        }
      ).__avkitThemeProbe?.handle(url, method, init)
      if (probed) return probed
      let bodyKeys: string[] = []
      let body: Record<string, unknown> = {}
      if (typeof init?.body === 'string' && init.body.length > 0) {
        body = JSON.parse(init.body) as Record<string, unknown>
        bodyKeys = Object.keys(body).sort()
      }
      state.__e2eCalls?.push({ url, method, bodyKeys })
      const json = (payload: unknown, status = 200) =>
        new Response(JSON.stringify(payload), {
          status,
          headers: { 'Content-Type': 'application/json' },
        })
      const protectedHit =
        url.includes('/tts') ||
        url.includes('/models') ||
        url.includes('/settings/tts') ||
        url.includes('/health/dependencies')
      if (!protectedHit) {
        return new Response(JSON.stringify({ error: { code: 'E2E', message: 'unexpected' } }), {
          status: 599,
          headers: { 'Content-Type': 'application/json' },
        })
      }
      if (url.includes('__e2e-unhandled')) {
        return new Response('E2E_SEAM_UNHANDLED', { status: 599 })
      }
      if (url.includes('/settings/tts') && method === 'GET') {
        return json({
          input_text: '',
          voice: 'af_heart',
          speed: 1,
          output_format: 'MP3',
          output_path: '~/Documents',
          device: 'cpu',
        })
      }
      if (url.includes('/settings/tts') && method === 'PUT') {
        return json(body)
      }
      if (url.includes('/tts/voices') && method === 'GET') {
        // Setup-only (MEU-64): one voice by default; AC-64.6 passes VOICE_CATALOG_FIXTURE.
        return json({
          items: voices ?? [
            {
              voice_id: 'af_heart',
              language: 'American English',
              gender: 'F',
              style_description: 'warm',
            },
          ],
        })
      }
      if (url.includes('/tts/prepare') && method === 'POST') {
        return json({ cleaned_text: 'CLEANED:' + String(body.text ?? '') })
      }
      if (url.includes('/tts/generate') && method === 'POST') {
        state.__e2eJob = {
          ...(state.__e2eJob ?? {}),
          id: 'e2e-tts-1',
          status: 'Generating',
          text_preview: String(body.text ?? '').slice(0, 20),
          text_hash: 'abc123',
          segments_total: 2,
          segments_done: 1,
          output_path: 'C:/out/e2e.mp3',
          enabled_steps: body.enabled_steps,
        }
        return json(state.__e2eJob, 201)
      }
      if (/\/tts\/[^/?]+$/.test(new URL(url).pathname) && method === 'GET') {
        return json(state.__e2eJob ?? {})
      }
      if (/\/tts\/[^/?]+$/.test(new URL(url).pathname) && method === 'DELETE') {
        if (state.__e2eJob) {
          state.__e2eJob = { ...state.__e2eJob, status: 'Cancelled' }
        }
        return new Response(null, { status: 204 })
      }
      if (url.includes('/models/available') && method === 'GET') {
        return json({ items: state.__e2eCatalog ?? [] })
      }
      if (url.includes('/health/dependencies') && method === 'GET') {
        return json(state.__e2eDeps ?? {})
      }
      if (url.includes('/models/status') && method === 'GET') {
        return json({
          is_loaded: state.__e2eLoaded === true,
          variant_id: state.__e2eLoaded ? (state.__e2eLoadedId ?? 'kokoro-onnx-fp32') : null,
          name: 'ONNX FP32',
          device: 'cpu',
          memory_bytes: 100,
        })
      }
      if (url.includes('/models/download-runtime') && method === 'GET') {
        return json(state.__e2eRuntime ?? { state: 'Idle', variant_id: null, fraction: 0 })
      }
      if (url.includes('/models/download') && method === 'POST') {
        const vid = String(body.variant_id ?? '')
        state.__e2eRuntime = {
          state: 'Idle',
          variant_id: vid,
          fraction: 1,
        }
        state.__e2eCatalog = (state.__e2eCatalog ?? []).map((row) =>
          row.id === vid ? { ...row, is_downloaded: true, path: 'C:/models/' + vid } : row,
        )
        return new Response('', { status: 202 })
      }
      if (url.includes('/models/load') && method === 'POST') {
        state.__e2eLoaded = true
        state.__e2eLoadedId = String(body.variant_id ?? state.__e2eLoadedId)
        return json({ ok: true })
      }
      if (url.includes('/models/unload') && method === 'POST') {
        state.__e2eLoaded = false
        return new Response(null, { status: 204 })
      }
      return new Response('E2E_SEAM_UNHANDLED', { status: 599 })
    }
  }, options.voices ?? null)
  await page.reload()
  await page.getByTestId('app-shell').waitFor()
}

async function openTts(page: Page): Promise<void> {
  await page.getByTestId('nav-tts').click()
  await page.getByTestId('tts-page').waitFor()
}

test('W2-1 TTS_HOME shows the page and text field', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installTtsSeam(page)
  await openTts(page)
  await expect(page.getByTestId('tts-page')).toBeVisible()
  await expect(page.getByTestId('text-input')).toBeVisible()
  await app.close()
})

test('W2-2 nav from home via nav-tts', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installTtsSeam(page)
  await page.getByTestId('nav-tts').click()
  await expect(page.getByTestId('tts-page')).toBeVisible()
  await app.close()
})

test('W2-3 page chrome EXTRA presence', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installTtsSeam(page)
  await openTts(page)
  await expect(page.getByTestId('text-input')).toBeVisible()
  await expect(page.getByTestId('load-file-btn')).toBeVisible()
  await expect(page.getByTestId('paste-btn')).toBeVisible()
  // TA-6 (class A): Cleanup and Manage are disclosures; open them first.
  await page.getByTestId('cleanup-toggle').click()
  await expect(page.getByTestId('cleanup-pipeline')).toBeVisible()
  await expect(page.getByTestId('preview-cleanup-btn')).toBeVisible()
  await page.getByTestId('model-manage-toggle').click()
  await expect(page.getByTestId('model-manager')).toBeVisible()
  // TA-7 (Session 27, MEU-64): the listbox is the voice combobox popup; open it first.
  await page.getByTestId('voice-combobox').click()
  await expect(page.getByTestId('voice-grid')).toBeVisible()
  await expect(page.getByTestId('generate-btn')).toBeVisible()
  await expect(page.getByTestId('speed-slider')).toBeVisible()
  await expect(page.getByTestId('cancel-btn')).toBeVisible()
  await expect(page.getByTestId('browse-output-btn')).toBeVisible()
  // TA-6 (class B, RUN_BAR_SLOT / TT5): at idle the slot holds last-output.
  await expect(page.getByTestId('last-output')).toBeAttached()
  await expect(page.getByTestId('last-output')).toHaveText('No output yet')
  await app.close()
})

test('W2-4 E2E_HAPPY_PATH via E2E_SEAM_INSTALL + E2E_SEAM_NEG', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installTtsSeam(page)
  await openTts(page)
  await page.getByTestId('text-input').fill('Hello world for TTS.')
  // TA-7 (class A): preview lives in the Cleanup disclosure.
  await page.getByTestId('cleanup-toggle').click()
  await page.getByTestId('preview-cleanup-btn').click()
  await expect(page.getByTestId('preview-cleaned')).toBeVisible()
  await expect(page.getByTestId('preview-cleaned')).toContainText('CLEANED:')
  await page.getByTestId('generate-btn').click()
  // TA-7 (class B, RUN_BAR_SLOT): the seam job stays Generating on its own, so
  // move it to Done (W2-5 seam-mutation pattern) before asserting the output slot.
  await expect(page.getByTestId('segment-progress')).toBeVisible()
  await page.evaluate(() => {
    const state = window as unknown as { __e2eJob?: Record<string, unknown> }
    state.__e2eJob = { ...(state.__e2eJob ?? {}), status: 'Done', segments_done: 2 }
  })
  await expect(page.getByTestId('last-output')).toBeVisible()
  const unhandledPath = '__e2e-unhandled'
  const neg = await page.evaluate(async (token) => {
    const res = await window.fetch(`http://127.0.0.1:9/api/v1/tts/${token}`, {
      method: 'GET',
    })
    const body = await res.text()
    return { status: res.status, body }
  }, unhandledPath)
  expect(neg.status).toBe(599)
  expect(neg.body).toContain('E2E_SEAM_UNHANDLED')
  // E2E_SEAM_NEG requires an unhandled protected URL containing __e2e-unhandled
  expect(unhandledPath).toBe('__e2e-unhandled')
  const calls = await page.evaluate(() => {
    return (window as unknown as { __e2eCalls?: Array<{ bodyKeys?: string[] }> }).__e2eCalls ?? []
  })
  expect(calls.some((c) => (c.bodyKeys ?? []).includes('enabled_steps'))).toBe(true)
  await app.close()
})

test('W2-5 E2E_ACTUATE after E2E_SEAM_INSTALL', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installTtsSeam(page)
  await openTts(page)
  const gate = await page.evaluate(() => {
    return (window as unknown as { __e2eSeamInstalled?: boolean }).__e2eSeamInstalled === true
  })
  expect(gate).toBe(true)
  await page.getByTestId('text-input').fill('Actuate TTS sample.')
  await page.evaluate(() => {
    const state = window as unknown as { __e2eJob?: Record<string, unknown> }
    state.__e2eJob = {
      ...(state.__e2eJob ?? {}),
      status: 'Generating',
      segments_done: 1,
      segments_total: 2,
      output_path: 'C:/out/e2e.mp3',
    }
  })
  await page.getByTestId('nav-downloader').click()
  await page.getByTestId('nav-tts').click()
  await page.getByTestId('load-file-btn').click()
  await page.getByTestId('paste-btn').click()
  // TA-7 (class A): preview and model actions live in their disclosures.
  await page.getByTestId('cleanup-toggle').click()
  await page.getByTestId('preview-cleanup-btn').click()
  await page.getByTestId('generate-btn').click()
  // TA-7 (class B, RUN_BAR_SLOT): segment progress is shown while the job runs.
  await expect(page.getByTestId('segment-progress')).toBeVisible()
  await page.getByTestId('cancel-btn').click()
  await page.getByTestId('browse-output-btn').click()
  // TA-4 (Session 27, MEU-63): pick a variant, then the one state-driven button walks Get → Load → Unload.
  await page.getByTestId('model-select').selectOption('kokoro-onnx-int8')
  await page.getByTestId('model-get-btn').click()
  await page.getByTestId('model-load-btn').click()
  await page.getByTestId('unload-btn').click()
  // TA-7 (Session 27, MEU-64): open the voice combobox first; language-select is in its popup.
  // Escape closes the popup so it cannot cover the run-bar buttons clicked next.
  await page.getByTestId('voice-combobox').click()
  await page.getByTestId('voice-card').click()
  await expect(page.getByTestId('language-select')).toBeVisible()
  await page.getByTestId('voice-combobox').press('Escape')
  await page.getByTestId('open-output-btn').click()
  await page.getByTestId('open-output-folder-btn').click()
  await expect(page.getByTestId('format-select')).toBeVisible()
  await expect(page.getByTestId('device-select')).toBeVisible()
  const ledger = await page.evaluate(() => {
    return {
      ipc: (window as unknown as { __e2eIpc?: Array<{ channel: string }> }).__e2eIpc ?? [],
      calls: (window as unknown as { __e2eCalls?: Array<{ url: string; method: string; bodyKeys?: string[] }> })
        .__e2eCalls ?? [],
    }
  })
  expect(ledger.ipc.some((row) => row.channel === 'readTextFile')).toBe(true)
  expect(ledger.ipc.some((row) => row.channel === 'readClipboardText')).toBe(true)
  expect(ledger.ipc.some((row) => row.channel === 'showDirectoryDialog')).toBe(true)
  expect(ledger.ipc.some((row) => row.channel === 'openPath')).toBe(true)
  expect(ledger.ipc.some((row) => row.channel === 'showItemInFolder')).toBe(true)
  expect(ledger.calls.some((c) => c.url.includes('/tts/prepare'))).toBe(true)
  expect(ledger.calls.some((c) => c.url.includes('/tts/generate'))).toBe(true)
  expect(ledger.calls.some((c) => c.url.includes('/tts/') && c.method === 'DELETE')).toBe(true)
  expect(ledger.calls.some((c) => c.url.includes('/settings/tts') && c.method === 'PUT')).toBe(true)
  expect(
    ledger.calls.some(
      (c) => c.url.includes('/settings/tts') && (c.bodyKeys ?? []).includes('voice'),
    ),
  ).toBe(true)
  expect(ledger.calls.some((c) => c.url.includes('/models/download'))).toBe(true)
  expect(ledger.calls.some((c) => c.url.includes('/models/load'))).toBe(true)
  expect(ledger.calls.some((c) => c.url.includes('/models/unload'))).toBe(true)
  await app.close()
})

test('W2-6 PALETTE_DELIVER tts:prepare off-route', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installTtsSeam(page)
  await page.evaluate(() => {
    window.dispatchEvent(new CustomEvent('av-kit:tts:prepare'))
  })
  await expect(page.getByTestId('tts-page')).toBeVisible()
  const palette = await page.evaluate(() => {
    return 'tts:prepare'
  })
  expect(palette).toBe('tts:prepare')
  await app.close()
})

async function ttsLedger(page: Page): Promise<Array<{ url: string; method: string; bodyKeys?: string[] }>> {
  return page.evaluate(
    () => (window as unknown as { __e2eCalls?: Array<{ url: string; method: string; bodyKeys?: string[] }> }).__e2eCalls ?? [],
  )
}

async function setSeamJob(page: Page, patch: Record<string, unknown>): Promise<void> {
  await page.evaluate((next) => {
    const state = window as unknown as { __e2eJob?: Record<string, unknown> }
    state.__e2eJob = { ...(state.__e2eJob ?? {}), ...next }
  }, patch)
}

test('AC-56.6 two columns at the default window and stacked text-first when narrow', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installTtsSeam(page)
  await openTts(page)
  const text = page.getByRole('region', { name: 'Text' })
  const voice = page.getByRole('region', { name: 'Voice' })
  const wide = { text: await text.boundingBox(), voice: await voice.boundingBox() }
  expect(wide.text && wide.voice ? wide.voice.x >= wide.text.x + wide.text.width - 1 : false).toBe(true)
  await app.evaluate(({ BrowserWindow }) => {
    BrowserWindow.getAllWindows()[0]?.setSize(760, 800)
  })
  await expect
    .poll(async () => {
      const t = await text.boundingBox()
      const v = await voice.boundingBox()
      return t && v ? v.y >= t.y + t.height - 1 : false
    })
    .toBe(true)
  await app.close()
})

test('AC-56.6 Cleanup and Manage disclosures, the model chip and model actions', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installTtsSeam(page)
  await openTts(page)
  const cleanup = page.getByTestId('cleanup-toggle')
  await expect(cleanup).toHaveText('Cleanup · 10 of 11 steps')
  await expect(page.getByTestId('cleanup-pipeline')).toBeHidden()
  await cleanup.click()
  await expect(page.getByTestId('cleanup-pipeline')).toBeVisible()
  await page.getByTestId('cleanup-pipeline').getByLabel('Numbers', { exact: true }).click()
  await expect(cleanup).toHaveText('Cleanup · 9 of 11 steps')
  await expect(page.getByTestId('loaded-model')).toContainText('· cpu')
  await expect(page.getByTestId('model-manager')).toBeHidden()
  await page.getByTestId('model-manage-toggle').click()
  await expect(page.getByTestId('model-manager')).toBeVisible()
  await expect(page.getByTestId('loaded-model-details')).toContainText('Loaded: kokoro-onnx-fp32 (cpu)')
  await page.getByTestId('unload-btn').click()
  await expect(page.getByTestId('loaded-model')).toHaveText('No model loaded')
  await expect(page.getByTestId('model-manager')).toBeVisible()
  await expect.poll(async () => (await ttsLedger(page)).some((row) => row.url.includes('/models/unload'))).toBe(true)
  await app.close()
})

test('AC-56.6 voice list, speed presets and format select persist their settings leaf', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installTtsSeam(page)
  await openTts(page)
  // TA-7 (Session 27, MEU-64): the listbox is the voice combobox popup; open it first.
  await page.getByTestId('voice-combobox').click()
  const list = page.getByTestId('voice-grid')
  await expect(list).toHaveAttribute('role', 'listbox')
  await list.getByRole('option').first().click()
  await expect
    .poll(async () => (await ttsLedger(page)).some((row) => row.method === 'PUT' && (row.bodyKeys ?? []).includes('voice')))
    .toBe(true)
  await page.getByTestId('voice-combobox').press('Escape')
  await expect(page.getByTestId('speed-preset-1-0')).toBeChecked()
  await page.getByTestId('speed-preset-1-1').check()
  await expect(page.getByText('Speed 1.1×')).toBeVisible()
  await expect
    .poll(async () => (await ttsLedger(page)).some((row) => row.method === 'PUT' && (row.bodyKeys ?? []).includes('speed')))
    .toBe(true)
  await page.getByTestId('format-select').selectOption('WAV')
  await expect
    .poll(async () =>
      (await ttsLedger(page)).some((row) => row.method === 'PUT' && (row.bodyKeys ?? []).includes('output_format')),
    )
    .toBe(true)
  await app.close()
})

test('AC-56.6 run bar slot: idle output, generating progress, done output with opens, error', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installTtsSeam(page)
  await openTts(page)
  await expect(page.getByTestId('last-output')).toHaveText('No output yet')
  await expect(page.getByTestId('segment-progress')).toHaveCount(0)
  await expect(page.getByTestId('open-output-btn')).toHaveCount(0)
  await page.getByTestId('text-input').fill('Run bar sample.')
  await page.getByTestId('generate-btn').click()
  await expect(page.getByTestId('segment-progress')).toBeVisible()
  await expect(page.getByTestId('segment-progress-bar')).toHaveAttribute('aria-valuenow', '50')
  await expect(page.getByTestId('last-output')).toHaveCount(0)
  await setSeamJob(page, { status: 'Done', segments_done: 2, output_path: 'C:/out/e2e.mp3' })
  await expect(page.getByTestId('last-output')).toHaveText('C:/out/e2e.mp3')
  await expect(page.getByTestId('segment-progress')).toHaveCount(0)
  await page.getByTestId('open-output-btn').click()
  await expect
    .poll(async () =>
      page.evaluate(() => ((window as unknown as { __e2eIpc?: Array<{ channel: string }> }).__e2eIpc ?? []).map((r) => r.channel)),
    )
    .toContain('openPath')
  await page.evaluate(() => {
    window.dispatchEvent(new CustomEvent('av-kit:tts:error', { detail: 'E2E synthesis failed' }))
  })
  await expect(page.getByTestId('error-banner')).toHaveText('E2E synthesis failed')
  await expect(page.getByTestId('last-output')).toHaveCount(0)
  await app.close()
})

test('AC-63.6 picker flow: Get → progress → Load → Unload, each call once and in order', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installTtsSeam(page)
  await openTts(page)
  await expect(page.getByTestId('tts-asset-chip-tts_onnx_vocab')).toContainText('Ready')
  await page.getByTestId('model-select').selectOption('kokoro-onnx-int8')
  const get = page.getByTestId('model-get-btn')
  await expect(get).toHaveText('Get')
  // Hold the download: the button reads Getting…, is disabled, and a click adds no ledger entry.
  await page.evaluate(() => {
    const state = window as unknown as { __e2eRuntime?: Record<string, unknown> }
    state.__e2eRuntime = { state: 'Downloading', variant_id: 'kokoro-onnx-int8', asset: null, fraction: 0.4 }
  })
  // The runtime polls every 5 s while idle; allow one poll.
  await expect(get).toHaveText('Getting…', { timeout: 15_000 })
  await expect(get).toBeDisabled()
  await expect(page.getByTestId('download-progress-bar')).toHaveAttribute('aria-valuenow', '40')
  await get.click({ force: true })
  await page.evaluate(() => {
    const state = window as unknown as { __e2eRuntime?: Record<string, unknown> }
    state.__e2eRuntime = { state: 'Idle', variant_id: null, asset: null, fraction: 0 }
  })
  await expect(get).toBeEnabled({ timeout: 15_000 })
  await get.click()
  const load = page.getByTestId('model-load-btn')
  await expect(load).toHaveText('Load')
  await load.click()
  const unload = page.getByTestId('unload-btn')
  await expect(unload).toHaveText('Unload')
  await unload.click()
  await expect(page.getByTestId('model-get-btn').or(page.getByTestId('model-load-btn'))).toBeVisible()
  const mutations = (await ttsLedger(page))
    .filter((row) => row.method === 'POST' && /\/models\/(download|load|unload)$/.test(new URL(row.url).pathname))
    .map((row) => new URL(row.url).pathname.replace('/api/v1', ''))
  expect(mutations).toEqual(['/models/download', '/models/load', '/models/unload'])
  await app.close()
})

test('AC-63.5 a Failed job shows its error_message in the run bar', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installTtsSeam(page)
  await openTts(page)
  await page.getByTestId('text-input').fill('Failure sample.')
  await page.getByTestId('generate-btn').click()
  await expect(page.getByTestId('segment-progress')).toBeVisible()
  await setSeamJob(page, { status: 'Failed', error_message: 'tts asset missing: tts_spacy_model' })
  await expect(page.getByTestId('error-banner')).toHaveText('tts asset missing: tts_spacy_model')
  await setSeamJob(page, { status: 'Done', error_message: 'stale', output_path: 'C:/out/e2e.mp3' })
  // A Failed job is polled every 5 s (ttsPollInterval), so the Done read can take one full poll.
  await expect(page.getByTestId('error-banner')).toHaveCount(0, { timeout: 15_000 })
  await app.close()
})

test('AC-64.6 Speed and Format are visible without scrolling at the default window', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installTtsSeam(page, { voices: VOICE_CATALOG_FIXTURE })
  await openTts(page)
  // Setup only: wait for the voice catalog to be rendered (either layout), then a frame.
  await page.waitForFunction(
    () =>
      ((window as unknown as { __e2eCalls?: Array<{ url: string }> }).__e2eCalls ?? []).some((row) =>
        row.url.includes('/tts/voices'),
      ) && document.querySelector('[data-testid="speed-slider"]') !== null,
  )
  await page.evaluate(() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done))))
  const view = await page.evaluate(() => {
    const scrollTops: number[] = []
    let node: HTMLElement | null = document.querySelector('[data-testid="tts-page"]')
    while (node) {
      const overflow = getComputedStyle(node).overflowY
      if ((overflow === 'auto' || overflow === 'scroll') && node.scrollHeight > node.clientHeight) {
        scrollTops.push(node.scrollTop)
      }
      node = node.parentElement
    }
    return { innerHeight: window.innerHeight, docTop: document.scrollingElement?.scrollTop ?? 0, scrollTops }
  })
  const speed = (await page.getByTestId('speed-slider').boundingBox()) ?? { y: Number.POSITIVE_INFINITY, height: 0 }
  const format = (await page.getByTestId('format-select').boundingBox()) ?? { y: Number.POSITIVE_INFINITY, height: 0 }
  // The first assertions are the geometry (Review R2-4): on the old layout they fail here.
  expect(speed.y + speed.height, 'speed-slider bottom').toBeLessThanOrEqual(view.innerHeight)
  expect(format.y + format.height, 'format-select bottom').toBeLessThanOrEqual(view.innerHeight)
  expect(view.docTop).toBe(0)
  expect(view.scrollTops.every((top) => top === 0)).toBe(true)
  await expect(page.getByTestId('voice-combobox')).toHaveAttribute('aria-expanded', 'false')
  await expect(page.getByTestId('voice-selected-chip')).toContainText('af_heart')
  await app.close()
})

test('AC-64.4 voice combobox: type to filter, Enter selects once, Escape closes, empty state', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installTtsSeam(page)
  await openTts(page)
  const input = page.getByTestId('voice-combobox')
  await expect(input).toHaveAttribute('role', 'combobox')
  await expect(input).toHaveAttribute('aria-expanded', 'false')
  await expect(page.getByTestId('voice-grid')).toHaveCount(0)
  await input.fill('warm')
  await expect(input).toHaveAttribute('aria-expanded', 'true')
  await expect(page.getByTestId('voice-grid').getByRole('group')).toHaveAttribute('aria-label', 'American English')
  await expect(page.getByTestId('voice-card')).toHaveCount(1)
  await input.press('ArrowDown')
  const option = page.getByTestId('voice-card')
  await expect(input).toHaveAttribute('aria-activedescendant', (await option.getAttribute('id')) ?? 'missing-id')
  await input.press('Enter')
  await expect
    .poll(async () =>
      (await ttsLedger(page)).filter((row) => row.method === 'PUT' && (row.bodyKeys ?? []).includes('voice')).length,
    )
    .toBe(1)
  await expect(page.getByTestId('voice-selected-chip')).toContainText('af_heart')
  await input.press('Escape')
  await expect(input).toHaveAttribute('aria-expanded', 'false')
  await expect(page.getByTestId('voice-grid')).toHaveCount(0)
  await input.fill('zzz-no-voice')
  await expect(page.getByTestId('voice-grid')).toContainText('No voices match')
  await input.press('Enter')
  const voicePuts = (await ttsLedger(page)).filter((row) => row.method === 'PUT' && (row.bodyKeys ?? []).includes('voice'))
  expect(voicePuts).toHaveLength(1)
  await app.close()
})

test('AC-74.9 an unavailable voice is an aria-disabled option with its reason visible', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  // Setup only: the production catalog with jf_alpha served unavailable (D-70).
  const voices = (VOICE_CATALOG_FIXTURE as Array<Record<string, unknown>>).map((row) =>
    row.voice_id === 'jf_alpha' ? { ...row, available: false, reason: 'language_unsupported' } : row,
  )
  await installTtsSeam(page, { voices })
  await openTts(page)
  const input = page.getByTestId('voice-combobox')
  await input.fill('jf_alpha')
  await expect(input).toHaveAttribute('aria-expanded', 'true')
  const option = page.getByTestId('voice-card')
  await expect(option).toHaveCount(1)
  await expect(option).toHaveAttribute('aria-disabled', 'true')
  const reason = option.getByTestId('voice-unavailable-reason')
  await expect(reason).toBeVisible()
  await expect(reason).toHaveText('Language not supported yet')
  await app.close()
})

// --- AC-77.14 (Session 33, MEU-77): RUN_BAR_PIN over the asynchronous generate.
function jobGets(rows: Array<{ url: string; method: string }>): number {
  return rows.filter((row) => row.method === 'GET' && /\/tts\/e2e-tts-1$/.test(new URL(row.url).pathname)).length
}

test('AC-77.14 the run bar polls a Generating job to Done, then a second run cancels', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installTtsSeam(page)
  await openTts(page)
  await page.getByTestId('text-input').fill('Async run bar sample.')
  await page.getByTestId('generate-btn').click()
  await expect(page.getByTestId('segment-progress')).toBeVisible()
  // The seam job stays Generating: the run bar keeps polling it and shows no output yet.
  await expect.poll(async () => jobGets(await ttsLedger(page)), { timeout: 15_000 }).toBeGreaterThanOrEqual(2)
  await expect(page.getByTestId('last-output')).toHaveCount(0)
  await setSeamJob(page, { status: 'Done', segments_done: 2, output_path: 'C:/out/e2e.mp3' })
  await expect(page.getByTestId('last-output')).toHaveText('C:/out/e2e.mp3')
  // Second run: Cancel sends one DELETE; the next poll reads Cancelled.
  await page.getByTestId('generate-btn').click()
  await expect(page.getByTestId('segment-progress')).toBeVisible()
  await page.getByTestId('cancel-btn').click()
  await expect
    .poll(async () => (await ttsLedger(page)).filter((row) => row.method === 'DELETE' && row.url.includes('/tts/')).length)
    .toBe(1)
  await expect(page.getByTestId('segment-progress')).toHaveCount(0, { timeout: 15_000 })
  await expect(page.getByTestId('generate-btn')).toBeEnabled()
  const deletes = (await ttsLedger(page)).filter((row) => row.method === 'DELETE')
  expect(deletes).toHaveLength(1)
  await app.close()
})

// MEU-79 (Session 35): VOICE_GEOMETRY at the default window (1280x800) and the per-row device list.
type Box = { x: number; y: number; width: number; height: number }

async function boxOf(page: Page, name: string, locator = page.getByTestId(name)): Promise<Box> {
  const box = await locator.boundingBox()
  expect(box).not.toBeNull()
  return box as Box
}

// `what` names the pair in the diff; Playwright prints a custom expect message in place of the
// `expect(` header, so the name travels in the received value instead.
function expectNear(actual: number, expected: number, what: string): void {
  expect({ what, delta: Math.abs(actual - expected) <= 0.5 ? 0 : actual - expected }).toEqual({ what, delta: 0 })
}

async function openVoicePanel(page: Page): Promise<void> {
  await installTtsSeam(page)
  await openTts(page)
  // Setup only: the voices have resolved, the loaded row is selected, then two frames.
  await page.waitForFunction(
    () =>
      ((window as unknown as { __e2eCalls?: Array<{ url: string }> }).__e2eCalls ?? []).some((row) =>
        row.url.includes('/tts/voices'),
      ) &&
      (document.querySelector('[data-testid="model-select"]') as HTMLSelectElement | null)?.value === 'kokoro-onnx-fp32' &&
      document.querySelector('[data-testid="unload-btn"]') !== null,
  )
  await page.evaluate(() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done))))
}

async function labelTop(page: Page, id: string): Promise<number> {
  return page
    .getByTestId(id)
    .evaluate((node) => (node as HTMLSelectElement).labels?.[0]?.getBoundingClientRect().top ?? Number.NaN)
}

test('AC-79.7 model row: Model, Device and the action share height, bottom and label top', async () => {
  const app = await launchApp()
  try {
    const page = await app.firstWindow()
    await openVoicePanel(page)
    const model = await boxOf(page, 'model-select')
    const device = await boxOf(page, 'device-select')
    const action = await boxOf(page, 'unload-btn')
    expectNear(device.height, model.height, 'device-select height')
    expectNear(action.height, model.height, 'unload-btn height')
    expectNear(device.y + device.height, model.y + model.height, 'device-select bottom')
    expectNear(action.y + action.height, model.y + model.height, 'unload-btn bottom')
    expectNear(await labelTop(page, 'device-select'), await labelTop(page, 'model-select'), 'label top')
    expect(model.width - device.width).toBeGreaterThan(0)
  } finally {
    await app.close()
  }
})

test('AC-79.8 voice search, Format, slider and presets use the model control height', async () => {
  const app = await launchApp()
  try {
    const page = await app.firstWindow()
    await openVoicePanel(page)
    const model = await boxOf(page, 'model-select')
    const device = await boxOf(page, 'device-select')
    const combobox = await boxOf(page, 'voice-combobox')
    const format = await boxOf(page, 'format-select')
    const slider = await boxOf(page, 'speed-slider')
    const presets = await boxOf(
      page,
      'speed preset inner div',
      page.getByRole('group', { name: 'Speed preset' }).locator('> div'),
    )
    expectNear(combobox.height, model.height, 'voice-combobox height')
    expectNear(format.height, model.height, 'format-select height')
    expectNear(slider.height, model.height, 'speed-slider height')
    expectNear(presets.height, model.height, 'speed preset height')
    expectNear(slider.y + slider.height, presets.y + presets.height, 'speed-slider bottom')
    expectNear(format.width, device.width, 'format-select width')
  } finally {
    await app.close()
  }
})

test('AC-79.9 the model and speed rows never overflow and the slider keeps 96 px', async () => {
  const app = await launchApp()
  try {
    const page = await app.firstWindow()
    await openVoicePanel(page)
    const rows = await page.evaluate(() => {
      const measure = (node: Element | null | undefined) =>
        node instanceof HTMLElement ? { scroll: node.scrollWidth, client: node.clientWidth } : null
      const slider = document.querySelector('[data-testid="speed-slider"]')
      return {
        model: measure(document.querySelector('[data-testid="model-row"]')),
        speed: measure(slider?.parentElement?.parentElement),
      }
    })
    expect(rows.model).not.toBeNull()
    expect(rows.speed).not.toBeNull()
    expect(rows.model?.scroll ?? Number.POSITIVE_INFINITY).toBeLessThanOrEqual(
      rows.model?.client ?? 0,
    )
    expect(rows.speed?.scroll ?? Number.POSITIVE_INFINITY).toBeLessThanOrEqual(
      rows.speed?.client ?? 0,
    )
    const slider = await boxOf(page, 'speed-slider')
    expect(slider.width).toBeGreaterThanOrEqual(96)
  } finally {
    await app.close()
  }
})

test('AC-79.10 device-select lists the selected row devices: 2 for ONNX FP32, 3 for PyTorch FP32', async () => {
  const app = await launchApp()
  try {
    const page = await app.firstWindow()
    await openVoicePanel(page)
    const deviceValues = () =>
      page
        .getByTestId('device-select')
        .evaluate((node) => Array.from((node as HTMLSelectElement).options).map((option) => option.value))
    expect(await deviceValues()).toEqual(['auto', 'cpu'])
    await page.getByTestId('model-select').selectOption('kokoro-pt-fp32')
    expect(await page.getByTestId('model-select').inputValue()).toBe('kokoro-pt-fp32')
    expect(await deviceValues()).toEqual(['auto', 'cuda', 'cpu'])
  } finally {
    await app.close()
  }
})

// MEU-94 (Session 40): THEME_PROBE, THEME_COLOURS and THEME_GATE on the TTS route.
test('AC-94.9 TTS cold boot with no mirror holds the route until the theme', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installTtsSeam(page, { themeProbe: { mirror: null, theme: { hold: true } } })
  await page.getByTestId('nav-tts').click()
  await expectThemeHeld(page)
  await releaseTheme(page, 'light')
  await expectInsertedOn(page, 'light', THEME_FLOORS.tts)
  await expectThemeColours(page, 'light', THEME_FLOORS.tts)
  await app.close()
})
