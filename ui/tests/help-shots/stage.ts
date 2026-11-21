/**
 * MEU-162 (Session 99) DEMO_STAGE (D-1292): the demo state of each page for the help quick
 * start, shared by the screenshot generator (`help-shots.shots.ts`) and the Electron drift test
 * (`tests/e2e/help-quick-start.test.ts`).
 *
 * - `launchIsolated()` launches the built app on a fresh scratch root: `AVKIT_APP_DATA`,
 *   `USERPROFILE` and `HOME` all point inside it, and main must report those three paths before
 *   any page is used (Stop condition S12). Then it waits for the real backend URL, as
 *   `help-f1-mount.test.ts` does, and prints `isolation: ok`.
 * - `installSeam(page, seed)` replaces `window.fetch` in the renderer. It answers every request
 *   it knows from the seed and rejects any other with an error that names the path. It never
 *   calls the real `fetch`, so the renderer never reaches the backend.
 * - `STAGES[feature](page)` installs the seam with that page's seed, opens the page, reaches the
 *   state the quick start steps describe and waits until every step target is visible.
 *
 * The seam shapes are copied from the existing specs (`download-queue`, `transcript-queue`,
 * `tts-generate`, `convert-queue`, `capture-inbox` and `settings`); this file does not import
 * them. Every path in a seed is under `D:\Media\av-kit` or `C:/e2e/`, and no seed holds a user
 * name, a home folder or a real channel name.
 */

import { expect, type ElectronApplication, type Page } from '@playwright/test'
import { mkdirSync, mkdtempSync, readFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { launchElectron } from '../e2e/electron-app'

const here = dirname(fileURLToPath(import.meta.url))

export type HelpFeature = 'downloader' | 'transcript' | 'tts' | 'converter' | 'capture' | 'settings'

export const HELP_FEATURES: readonly HelpFeature[] = [
  'downloader',
  'transcript',
  'tts',
  'converter',
  'capture',
  'settings',
]

/** The nav button and the page root of each feature. */
export const FEATURE_PAGES: Record<HelpFeature, { nav: string; page: string }> = {
  downloader: { nav: 'nav-downloader', page: 'downloader-page' },
  transcript: { nav: 'nav-transcript', page: 'transcript-page' },
  tts: { nav: 'nav-tts', page: 'tts-page' },
  converter: { nav: 'nav-convert', page: 'convert-page' },
  capture: { nav: 'nav-capture', page: 'capture-page' },
  settings: { nav: 'nav-settings', page: 'settings-page' },
}

/**
 * The test ids each stage leaves visible: the quick start step targets of that page. The drift
 * test checks the JSON's targets on top of these, so a JSON target that a stage does not show
 * still fails.
 */
export const STAGE_TARGETS: Record<HelpFeature, readonly string[]> = {
  downloader: ['url-input', 'add-btn', 'queue-toolbar-start', 'queue-card-primary-action'],
  transcript: ['channel-input', 'add-btn', 'start-btn', 'open-zip-link'],
  tts: ['model-select', 'model-get-btn', 'text-input', 'voice-combobox', 'generate-btn'],
  converter: [
    'convert-task-compress',
    'convert-dropzone',
    'convert-preset-balanced',
    'convert-add',
    'queue-card-primary-action',
  ],
  capture: ['capture-region', 'capture-filmstrip-item', 'capture-tool-arrow', 'capture-save'],
  settings: [
    'settings-mode-download',
    'browse-download-path-btn',
    'settings-readiness-count',
    'mcp-copy-prompt-btn',
  ],
}

const PLACEHOLDER_PREFIX = 'http://127.0.0.1:9/'
const MEDIA = 'D:\\Media\\av-kit'

export type IsolatedApp = {
  app: ElectronApplication
  page: Page
  /** The scratch root; `appData` and `home` are inside it. */
  root: string
  appData: string
  home: string
}

/**
 * Launches the built app on a fresh scratch root and proves the isolation (F2, S12): main sees
 * the scratch `USERPROFILE`, `HOME` and `AVKIT_APP_DATA`, and the backend is ready before the
 * caller touches a page. Prints `isolation: ok` once per launch.
 */
export async function launchIsolated(): Promise<IsolatedApp> {
  const root = mkdtempSync(join(tmpdir(), 'avkit-help-'))
  const appData = join(root, 'appdata')
  const home = join(root, 'home')
  mkdirSync(appData, { recursive: true })
  mkdirSync(home, { recursive: true })
  const app = await launchElectron({ env: { AVKIT_APP_DATA: appData, USERPROFILE: home, HOME: home } })
  try {
    const seen = await app.evaluate(() => [
      process.env.USERPROFILE ?? '',
      process.env.HOME ?? '',
      process.env.AVKIT_APP_DATA ?? '',
    ])
    const want = [home, home, appData]
    if (JSON.stringify(seen) !== JSON.stringify(want)) {
      throw new Error(`S12: main sees ${JSON.stringify(seen)}, not the scratch paths ${JSON.stringify(want)}`)
    }
    const page = await app.firstWindow({ timeout: 60_000 })
    await expect
      .poll(
        async () =>
          page.evaluate(async () =>
            (window as unknown as { api: { getBackendUrl(): Promise<string> } }).api.getBackendUrl(),
          ),
        { timeout: 120_000, intervals: [500] },
      )
      .not.toContain(PLACEHOLDER_PREFIX)
    console.log('isolation: ok')
    return { app, page, root, appData, home }
  } catch (error) {
    await app.close()
    throw error
  }
}

type Row = Record<string, unknown>

/** Everything the seam answers from. Plain data only: it is serialised into the renderer. */
export type SeamSeed = {
  downloads: Row[]
  transcripts: Row[]
  conversions: Row[]
  captures: Row[]
  catalog: Row[]
  ffmpegAvailable: boolean
  /** Base64 PNG served for every `/captures/<id>/image`; empty serves a 1 x 1 PNG. */
  png: string
}

const PNG_1X1 =
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='

export const EMPTY_SEED: SeamSeed = {
  downloads: [],
  transcripts: [],
  conversions: [],
  captures: [],
  catalog: [],
  ffmpegAvailable: true,
  png: '',
}

/**
 * The renderer-side seam. It runs in the page through `addInitScript`, so it uses nothing
 * from this module: the seed and the settings travel as its argument.
 */
function seamScript(init: { seed: SeamSeed; media: string; png1x1: string }): void {
  const { seed, media } = init
  const state = window as unknown as {
    __e2eSeamInstalled?: boolean
    __helpSeamMisses?: string[]
  }
  state.__e2eSeamInstalled = true
  state.__helpSeamMisses = []
  const settings: Record<string, Record<string, unknown>> = {
    downloader: {
      path: media,
      quality: '1080p',
      cookie_mode: 'none',
      cookie_browser: 'chrome',
      cookie_browser_profile: 'Default',
      cookie_file_path: '',
    },
    transcript: { output_dir: media, delay_between_requests: 6 },
    tts: {
      input_text: '',
      voice: 'af_heart',
      speed: 1,
      output_format: 'MP3',
      output_path: media,
      device: 'cpu',
      models_directory: media,
      chunk_max_chars: 250,
    },
    app: { log_level: 'INFO', log_to_file: false, console_visible: false },
    ui: { theme: 'light' },
    converter: { output_dir: media, default_preset: 'balanced', skip_existing: true, gpu_preference: 'auto' },
    capture: { inbox_dir: media, hotkey: 'F2', copy_to_clipboard: false, close_to_tray: true, tool_lock: false },
  }
  const idle = { state: 'Idle', current_job_id: null }
  const json = (body: unknown, status = 200): Response =>
    new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
  const png = (): Response => {
    const bytes = Uint8Array.from(atob(seed.png === '' ? init.png1x1 : seed.png), (c) => c.charCodeAt(0))
    return new Response(bytes, { status: 200, headers: { 'Content-Type': 'image/png' } })
  }
  const answer = (method: string, path: string, body: unknown): Response | null => {
    if (method === 'GET') {
      if (path === '/health/dependencies') {
        return json({
          yt_dlp: { available: true, version: '2026.05.15' },
          ffmpeg: seed.ffmpegAvailable
            ? { available: true, version: '7.1.2', ffprobe_available: true }
            : { available: false, version: null, ffprobe_available: false },
          tts_onnx_vocab: { available: true, version: null, state: 'ready' },
          tts_spacy_model: { available: true, version: '3.8.0', state: 'ready' },
        })
      }
      if (path === '/health/console') return json({ items: [], last_seq: 0 })
      const ns = /^\/settings\/([a-z]+)$/.exec(path)
      if (ns !== null && ns[1] !== undefined && ns[1] in settings) return json(settings[ns[1]])
      if (path === '/downloads') return json({ items: seed.downloads, processor: idle })
      if (path === '/downloads/sabr') return json({ mode: 'inactive', source: null, checked_at: null })
      if (path === '/transcripts') return json({ items: seed.transcripts, processor: idle })
      if (path === '/conversions') return json({ items: seed.conversions, processor: idle })
      if (path === '/conversions/gpu') {
        return json({
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
      if (path === '/captures') return json({ items: seed.captures })
      if (path === '/captures/requests') return json({ items: [] })
      if (/^\/captures\/[^/]+\/image$/.test(path)) return png()
      const shot = /^\/captures\/([^/]+)$/.exec(path)
      if (shot !== null) {
        const id = decodeURIComponent(shot[1] ?? '')
        const found = seed.captures.find((row) => row.id === id)
        return found === undefined ? null : json({ ...found, annotations: [], backup_path: null })
      }
      if (path === '/models/available') return json({ items: seed.catalog })
      if (path === '/models/status') {
        return json({ is_loaded: false, variant_id: null, name: null, device: 'cpu', memory_bytes: null })
      }
      if (path === '/models/download-runtime') return json({ state: 'Idle', variant_id: null, asset: null, fraction: 0 })
      if (path === '/tts/voices') {
        return json({
          items: [{ voice_id: 'af_heart', language: 'American English', gender: 'F', style_description: 'warm' }],
        })
      }
      return null
    }
    const put = /^\/settings\/([a-z]+)$/.exec(path)
    if (method === 'PUT' && put !== null && put[1] !== undefined && put[1] in settings) {
      settings[put[1]] = { ...settings[put[1]], ...(body as Record<string, unknown>) }
      return json(settings[put[1]])
    }
    return null
  }
  window.fetch = async (input: RequestInfo | URL, request?: RequestInit): Promise<Response> => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
    const method = (request?.method ?? 'GET').toUpperCase()
    const path = new URL(url, window.location.href).pathname.replace(/^\/api\/v1(?=\/)/, '').replace(/\/$/, '')
    let body: unknown = undefined
    if (typeof request?.body === 'string' && request.body.length > 0) {
      try {
        body = JSON.parse(request.body)
      } catch {
        body = request.body
      }
    }
    const response = answer(method, path, body)
    if (response !== null) return response
    state.__helpSeamMisses?.push(`${method} ${path}`)
    throw new TypeError(`help seam: no answer for ${method} ${path}`)
  }
}

/** Installs the seam with `seed` and reloads, so every request after this goes to the seam. */
export async function installSeam(page: Page, seed: SeamSeed = EMPTY_SEED): Promise<void> {
  await page.addInitScript(seamScript, { seed, media: MEDIA, png1x1: PNG_1X1 })
  await page.reload()
  await page.getByTestId('app-shell').waitFor({ timeout: 60_000 })
}

/** The requests the seam refused so far; a stage refuses to finish while any exist. */
export async function seamMisses(page: Page): Promise<string[]> {
  return page.evaluate(() => (window as unknown as { __helpSeamMisses?: string[] }).__helpSeamMisses ?? [])
}

/** Opens a feature's page through its nav button. */
export async function openFeature(page: Page, feature: HelpFeature): Promise<void> {
  const { nav, page: pageId } = FEATURE_PAGES[feature]
  await page.getByTestId(nav).click()
  await page.getByTestId(pageId).waitFor({ state: 'visible', timeout: 30_000 })
}

async function finish(page: Page, feature: HelpFeature): Promise<void> {
  for (const target of STAGE_TARGETS[feature]) {
    await expect(page.getByTestId(target).first()).toBeVisible({ timeout: 15_000 })
  }
  const misses = await seamMisses(page)
  if (misses.length > 0) {
    throw new Error(`setup: the ${feature} stage made requests the seam does not know: ${misses.join(', ')}`)
  }
}

const CREATED = '2026-08-20T00:00:00Z'

function download(id: string, title: string, status: string, position: number): Row {
  const done = status === 'Done'
  return {
    id,
    url: `https://www.youtube.com/watch?v=${id}`,
    video_id: id,
    title,
    quality: '1080p',
    audio_only: false,
    audio_format: 'default',
    status,
    progress: done ? 100 : 0,
    speed: null,
    eta: null,
    file_size: done ? 163_577_856 : null,
    file_path: done ? `${MEDIA}\\${title}.mp4` : null,
    error_message: null,
    queue_position: position,
    created_at: CREATED,
  }
}

function transcript(id: string, name: string, status: string, position: number): Row {
  const done = status === 'Done'
  const folder = `${MEDIA}\\transcripts\\${id}`
  return {
    id,
    channel_url: `https://www.youtube.com/channel/${id}`,
    channel_name: name,
    status,
    output_dir: folder,
    video_count: done ? 24 : 0,
    transcripts_done: done ? 24 : 0,
    word_count: done ? 48_200 : 0,
    zip_path: done ? `${folder}\\${id}_raw.zip` : null,
    last_title: null,
    last_item_status: null,
    last_item_message: null,
    queue_position: position,
    compiled_path: null,
    error_message: null,
    created_at: CREATED,
    updated_at: CREATED,
  }
}

function conversion(id: string, name: string, status: string, position: number): Row {
  const done = status === 'Done'
  return {
    id,
    kind: 'compress',
    input_path: `${MEDIA}\\${name}`,
    output_path: done ? `${MEDIA}\\compressed\\${name}` : null,
    display_name: name,
    preset_id: 'balanced',
    cq: 25,
    scale_height: 0,
    audio_mode: 'aac_128',
    gpu_encoder: null,
    in_ms: null,
    out_ms: null,
    copy_mode: null,
    stream_index: null,
    status,
    progress: done ? 100 : 0,
    speed: null,
    eta: null,
    file_size: done ? 48_234_496 : null,
    queue_position: position,
  }
}

function capture(id: string, name: string, createdAt: string): Row {
  return {
    id,
    original_path: `C:/e2e/${name}`,
    annotated_path: null,
    sidecar_path: null,
    display_name: name,
    width: 240,
    height: 120,
    file_size: 403,
    source: 'gui',
    created_at: createdAt,
    updated_at: createdAt,
  }
}

function fixturePng(): string {
  return readFileSync(resolve(here, '../e2e/fixtures/capture-fidelity-original.png')).toString('base64')
}

async function downloaderStage(page: Page): Promise<void> {
  await installSeam(page, {
    ...EMPTY_SEED,
    downloads: [
      download('demo0000001', 'Garden tour', 'Done', 1),
      download('demo0000002', 'Bread at home', 'Done', 2),
      download('demo0000003', 'City walk at night', 'Pending', 3),
    ],
  })
  await openFeature(page, 'downloader')
  await page.getByTestId('url-input').fill('https://www.youtube.com/watch?v=demo')
  await finish(page, 'downloader')
}

async function transcriptStage(page: Page): Promise<void> {
  await installSeam(page, {
    ...EMPTY_SEED,
    transcripts: [transcript('demo-a', 'Demo channel', 'Done', 1), transcript('demo-b', 'Sample talks', 'Pending', 2)],
  })
  await openFeature(page, 'transcript')
  await finish(page, 'transcript')
}

async function ttsStage(page: Page): Promise<void> {
  await installSeam(page, {
    ...EMPTY_SEED,
    catalog: [
      {
        id: 'kokoro-onnx-int8',
        name: 'ONNX INT8',
        format: 'onnx',
        precision: 'int8',
        size_bytes: 92_000_000,
        path: null,
        is_downloaded: false,
        devices: ['auto', 'cpu'],
      },
    ],
  })
  await openFeature(page, 'tts')
  await page.getByTestId('text-input').fill('Hello. This is a short demo of the voice.')
  await finish(page, 'tts')
}

async function converterStage(page: Page): Promise<void> {
  await installSeam(page, {
    ...EMPTY_SEED,
    conversions: [conversion('demo-c1', 'Garden tour.mp4', 'Done', 1), conversion('demo-c2', 'City walk.mp4', 'Pending', 2)],
  })
  await openFeature(page, 'converter')
  await page.getByTestId('convert-task-compress').click()
  await finish(page, 'converter')
}

async function captureStage(page: Page): Promise<void> {
  await installSeam(page, {
    ...EMPTY_SEED,
    captures: [
      capture('demo-shot-1', 'shot-1.png', '2026-08-27T11:00:00Z'),
      capture('demo-shot-2', 'shot-2.png', '2026-08-27T10:00:00Z'),
    ],
    png: fixturePng(),
  })
  await openFeature(page, 'capture')
  await page.getByTestId('capture-filmstrip-item').first().click()
  await page.getByTestId('capture-tool-arrow').click()
  const surface = page.getByTestId('capture-draw-surface')
  await expect(surface).toBeVisible()
  const box = await surface.boundingBox()
  if (box === null) throw new Error('setup: capture-draw-surface has no box')
  const scale = Math.min(box.width / 240, box.height / 120)
  const originX = box.x + (box.width - 240 * scale) / 2
  const originY = box.y + (box.height - 120 * scale) / 2
  await page.mouse.move(originX + 40 * scale, originY + 90 * scale)
  await page.mouse.down()
  await page.mouse.move(originX + 120 * scale, originY + 50 * scale, { steps: 4 })
  await page.mouse.move(originX + 180 * scale, originY + 30 * scale, { steps: 4 })
  await page.mouse.up()
  await expect(page.locator('[data-annotation-type="arrow"]')).toHaveCount(1)
  await finish(page, 'capture')
}

async function settingsStage(page: Page): Promise<void> {
  await installSeam(page, { ...EMPTY_SEED, ffmpegAvailable: false })
  await openFeature(page, 'settings')
  await expect(page.getByTestId('readiness-ffmpeg-link')).toBeVisible({ timeout: 15_000 })
  await finish(page, 'settings')
}

export const STAGES: Record<HelpFeature, (page: Page) => Promise<void>> = {
  downloader: downloaderStage,
  transcript: transcriptStage,
  tts: ttsStage,
  converter: converterStage,
  capture: captureStage,
  settings: settingsStage,
}
