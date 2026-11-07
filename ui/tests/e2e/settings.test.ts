import { _electron, expect, test, type Page } from '@playwright/test'
import { mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { DEPS_FFPROBE_ROW } from './test-ids'
import {
  addThemeProbe,
  documentIsDark,
  expectInsertedOn,
  expectThemeColours,
  expectThemeHeld,
  launchWithAppData,
  releaseTheme,
  storedMirror,
  themeProbeCounts,
  THEME_FLOORS,
  type ThemeProbeMode,
} from './theme-probe'

const here = dirname(fileURLToPath(import.meta.url))

async function launchApp() {
  return _electron.launch({
    args: [resolve(here, '../../out/main/index.js')],
    env: {
      ...process.env,
      AVKIT_E2E: '1',
      AVKIT_APP_DATA: mkdtempSync(join(tmpdir(), 'avkit-e2e-settings-')),
    },
  })
}

// Setup-only (MEU-62): optional TTS asset rows; the default seam keeps the two-row backend shape.
type AssetRows = Record<string, { available: boolean; version: string | null; state: string }>
// Setup-only (MEU-118): an optional `GET /models/available` report and stored `tts.device`.
// Without a catalog the seam doesn't answer that route, as before.
type CatalogRows = Array<Record<string, unknown>>
type SeamData = { assetRows: AssetRows; catalog: CatalogRows | null; device: string | null }

async function installSettingsSeam(
  page: Page,
  assets: AssetRows = {},
  options: { themeProbe?: ThemeProbeMode; catalog?: CatalogRows; device?: string } = {},
): Promise<void> {
  if (options.themeProbe) {
    await addThemeProbe(page, options.themeProbe)
  }
  const data: SeamData = { assetRows: assets, catalog: options.catalog ?? null, device: options.device ?? null }
  await page.addInitScript(({ assetRows, catalog, device }: SeamData) => {
    const state = window as unknown as {
      __e2eSeamInstalled?: boolean
      __e2eCalls?: Array<{ url: string; method: string; bodyKeys?: string[]; body?: Record<string, unknown> }>
      __e2eIpc?: Array<{ channel: string }>
    }
    state.__e2eSeamInstalled = true
    state.__e2eCalls = []
    state.__e2eIpc = []

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
      state.__e2eCalls?.push({ url, method, bodyKeys, body })
      const json = (payload: unknown, status = 200) =>
        new Response(JSON.stringify(payload), {
          status,
          headers: { 'Content-Type': 'application/json' },
        })
      const protectedHit =
        url.includes('/settings') ||
        url.includes('/downloads/apply-defaults') ||
        url.includes('/health/dependencies') ||
        url.includes('/models/download') ||
        (catalog !== null && url.includes('/models/available'))
      if (!protectedHit) {
        return new Response(JSON.stringify({ error: { code: 'E2E', message: 'unexpected' } }), {
          status: 599,
          headers: { 'Content-Type': 'application/json' },
        })
      }
      if (url.includes('__e2e-unhandled')) {
        return new Response('E2E_SEAM_UNHANDLED', { status: 599 })
      }
      if (url.includes('/settings/downloader') && method === 'GET') {
        return json({
          path: 'C:/Downloads/av-kit',
          quality: '1080p',
          cookie_mode: 'file',
          cookie_file_path: 'C:/cookies.txt',
        })
      }
      if (url.includes('/settings/transcript') && method === 'GET') {
        return json({ output_dir: 'C:/Transcripts' })
      }
      if (url.includes('/settings/tts') && method === 'GET') {
        return json({ models_directory: 'C:/models', chunk_max_chars: 250, ...(device === null ? {} : { device }) })
      }
      if (url.includes('/settings/app') && method === 'GET') {
        return json({ log_level: 'INFO', log_to_file: false, console_visible: true })
      }
      if (url.includes('/settings/ui') && method === 'GET') {
        return json({ theme: 'dark' })
      }
      // Setup-only (MEU-58): drafts for the explicit-save sections so their dirty state is real.
      if (url.includes('/settings/converter') && method === 'GET') {
        return json({ output_dir: '~/Videos/av-kit', default_preset: 'balanced', skip_existing: true, gpu_preference: 'auto' })
      }
      if (url.includes('/settings/capture') && method === 'GET') {
        return json({ inbox_dir: '~/Pictures/av-kit', hotkey: 'F2', copy_to_clipboard: false, close_to_tray: true })
      }
      if (url.includes('/settings/') && method === 'PUT') {
        return json(body)
      }
      if (url.includes('/downloads/apply-defaults') && method === 'POST') {
        return new Response(null, { status: 204 })
      }
      if (url.includes('/health/dependencies') && method === 'GET') {
        return json({
          yt_dlp: { available: true, version: '2026.05.15', path: 'C:/bin/yt-dlp.exe' },
          ffmpeg: { available: true, version: '7.1.2', path: 'C:/bin/ffmpeg.exe', ffprobe_available: true },
          ...assetRows,
        })
      }
      if (url.includes('/models/download') && method === 'POST') {
        return json({ variant: null, asset: body.asset ?? null }, 202)
      }
      if (catalog !== null && url.includes('/models/available') && method === 'GET') {
        return json({ items: catalog })
      }
      return new Response('E2E_SEAM_UNHANDLED', { status: 599 })
    }
  }, data)
  await page.reload()
  await page.getByTestId('app-shell').waitFor()
}

async function openSettings(page: Page): Promise<void> {
  await page.getByTestId('nav-settings').click()
  await page.getByTestId('settings-page').waitFor()
}

test('W4-1 SETTINGS_HOME nav #/settings and settings-page', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSettingsSeam(page)
  await openSettings(page)
  await expect(page).toHaveURL(/#\/settings/)
  await expect(page.getByTestId('settings-page')).toBeVisible()
  await app.close()
})

test('W4-2 section cards visible for WAVE4_TESTIDS', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSettingsSeam(page)
  await openSettings(page)
  await expect(page.getByTestId('settings-page')).toBeVisible()
  await expect(page.getByTestId('download-settings')).toBeVisible()
  await expect(page.getByTestId('transcript-settings')).toBeVisible()
  await expect(page.getByTestId('tts-settings')).toBeVisible()
  await expect(page.getByTestId('console-settings')).toBeVisible()
  await expect(page.getByTestId('appearance-settings')).toBeVisible()
  await expect(page.getByTestId('dependencies-section')).toBeVisible()
  await expect(page.getByTestId('browse-download-path-btn')).toBeVisible()
  await expect(page.getByTestId('apply-defaults-btn')).toBeVisible()
  await expect(page.getByTestId('browse-ffmpeg-btn')).toBeVisible()
  await expect(page.getByTestId('browse-cookie-file-btn')).toBeVisible()
  await expect(page.getByTestId('browse-transcript-dir-btn')).toBeVisible()
  await expect(page.getByTestId('browse-models-dir-btn')).toBeVisible()
  await expect(page.getByTestId('check-deps-btn')).toBeVisible()
  await page.getByTestId('mcp-advanced-summary').click()
  await expect(page.getByTestId('copy-mcp-btn')).toBeVisible()
  await expect(page.getByTestId('pin-mcp-btn')).toBeVisible()
  await expect(page.getByTestId('theme-dark-btn')).toBeVisible()
  await expect(page.getByTestId('theme-light-btn')).toBeVisible()
  await expect(page.getByTestId('readiness-card')).toBeVisible()
  await expect(page.getByTestId('mcp-access-card')).toBeVisible()
  await expect(page.getByTestId('mcp-token-present')).toBeVisible()
  await app.close()
})

test('W4-3 E2E_ACTUATE browse apply check-deps after E2E_SEAM_INSTALL', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const pageErrors: string[] = []
  page.on('pageerror', (error) => {
    pageErrors.push(error.message)
  })
  await installSettingsSeam(page)
  await openSettings(page)
  const gate = await page.evaluate(() => {
    return (window as unknown as { __e2eSeamInstalled?: boolean }).__e2eSeamInstalled === true
  })
  expect(gate).toBe(true)
  await page.getByTestId('browse-download-path-btn').click()
  await page.getByTestId('apply-defaults-btn').click()
  await page.getByTestId('browse-ffmpeg-btn').click()
  await page.getByTestId('browse-cookie-file-btn').click()
  await page.getByTestId('browse-transcript-dir-btn').click()
  await page.getByTestId('browse-models-dir-btn').click()
  await page.getByTestId('check-deps-btn').click()
  await page.getByTestId('mcp-advanced-summary').click()
  await page.getByTestId('copy-mcp-btn').click()
  await page.getByTestId('pin-mcp-btn').click()
  await page.getByTestId('theme-dark-btn').click()
  await page.getByTestId('theme-light-btn').click()
  await expect(page.locator('html')).not.toHaveClass(/dark/)
  const unhandledPath = '__e2e-unhandled'
  const neg = await page.evaluate(async (token) => {
    const res = await window.fetch(`http://127.0.0.1:9/api/v1/settings/${token}`, {
      method: 'GET',
    })
    const body = await res.text()
    return { status: res.status, body }
  }, unhandledPath)
  expect(neg.status).toBe(599)
  expect(neg.body).toContain('E2E_SEAM_UNHANDLED')
  expect(unhandledPath).toBe('__e2e-unhandled')
  const calls = await page.evaluate(() => {
    return (
      window as unknown as {
        __e2eCalls?: Array<{ url: string; method: string; bodyKeys?: string[] }>
      }
    ).__e2eCalls ?? []
  })
  expect(calls.some((row) => row.url.includes('/downloads/apply-defaults'))).toBe(true)
  const depGets = calls.filter((row) => row.url.includes('/health/dependencies') && row.method === 'GET')
  expect(depGets.length).toBeGreaterThanOrEqual(1)
  expect(
    calls.some(
      (row) => row.url.includes('/settings/downloader') && row.method === 'PUT' && row.bodyKeys?.includes('path'),
    ),
  ).toBe(true)
  expect(
    calls.some((row) => row.url.includes('/settings/ui') && row.method === 'PUT' && row.bodyKeys?.includes('theme')),
  ).toBe(true)
  expect(pageErrors).toEqual([])
  await app.close()
})

test('AC-61.17 unpackaged Settings omits start-at-sign-in-panel', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSettingsSeam(page)
  await openSettings(page)
  await expect(page.getByTestId('start-at-sign-in-panel')).toHaveCount(0)
  await app.close()
})

// ── MEU-58 Settings page layout (Phase 11 §Settings) — AC-58.12 real-Electron wave ─────────

const RAIL_KEYS = ['download', 'transcript', 'tts', 'convert', 'capture', 'console', 'appearance',
  'dependencies', 'readiness', 'mcp'] as const

test('AC-58.12 rail groups; click scrolls to the section; scrolling moves the current entry', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSettingsSeam(page)
  await openSettings(page)
  const rail = page.getByTestId('settings-rail')
  await expect(rail).toBeVisible()
  await expect(rail).toContainText('Pages')
  await expect(rail).toContainText('App')
  await expect(rail).toContainText('Setup')
  for (const key of RAIL_KEYS) {
    await expect(page.getByTestId(`settings-rail-${key}`)).toBeVisible()
  }
  await expect(page.getByTestId('settings-rail-startup')).toHaveCount(0)
  const railBox = await rail.boundingBox()
  const headingBox = await page.getByRole('heading', { level: 1, name: 'Settings' }).boundingBox()
  expect((railBox?.x ?? 0) + (railBox?.width ?? 0)).toBeLessThanOrEqual((headingBox?.x ?? 0) + 1)
  await page.getByTestId('settings-rail-mcp').click()
  await expect(page.getByTestId('mcp-access-card')).toBeInViewport()
  await expect(page.getByTestId('settings-rail-mcp')).toHaveAttribute('aria-current', 'location')
  await expect(rail).toBeInViewport()
  await page.evaluate(() => {
    document.querySelector('main')?.scrollTo({ top: 0, behavior: 'instant' as ScrollBehavior })
  })
  await expect(page.getByTestId('settings-rail-download')).toHaveAttribute('aria-current', 'location')
  await expect(page.locator('[aria-current="location"]')).toHaveCount(1)
  await app.close()
})

test('AC-58.12 save-model captions, one-line Browse rows and the Convert dirty dot', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSettingsSeam(page)
  await openSettings(page)
  await expect(page.getByTestId('settings-mode-download')).toHaveText('Saves as you type')
  await expect(page.getByTestId('settings-mode-convert')).toHaveText('Save required')
  await expect(page.getByTestId('settings-mode-appearance')).toHaveText('Applies immediately')
  const field = await page.getByTestId('settings-leaf-path').boundingBox()
  const browse = await page.getByTestId('browse-download-path-btn').boundingBox()
  expect(field && browse).toBeTruthy()
  const overlap = Math.min((field?.y ?? 0) + (field?.height ?? 0), (browse?.y ?? 0) + (browse?.height ?? 0))
    - Math.max(field?.y ?? 0, browse?.y ?? 0)
  expect(overlap).toBeGreaterThan(0)
  await expect(page.getByTestId('settings-rail-dot-convert')).toHaveCount(0)
  await page.getByTestId('settings-leaf-converter-output_dir').fill('C:/Videos/layout')
  await expect(page.getByTestId('settings-rail-dot-convert')).toBeVisible()
  await expect(page.getByTestId('convert-settings-save')).toHaveClass(/btn-save-dirty/)
  await page.getByTestId('convert-settings-save').click()
  await expect(page.getByTestId('settings-rail-dot-convert')).toHaveCount(0)
  const calls = await page.evaluate(() => (window as unknown as { __e2eCalls?: Array<{ url: string; method: string }> }).__e2eCalls ?? [])
  expect(calls.filter((row) => row.method === 'PUT' && row.url.includes('/settings/converter'))).toHaveLength(1)
  await app.close()
})

test('AC-58.12 readiness count after load and a horizontal rail in a narrow window', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSettingsSeam(page)
  await openSettings(page)
  const count = page.getByTestId('settings-readiness-count')
  await expect(count).toHaveText(/^[0-4] of 4 ready$/)
  const ready = Number.parseInt((await count.textContent()) ?? '0', 10)
  await expect(page.getByTestId('settings-rail-dot-readiness')).toHaveCount(ready < 4 ? 1 : 0)
  await app.evaluate(({ BrowserWindow }) => {
    BrowserWindow.getAllWindows()[0]?.setSize(900, 800)
  })
  await expect.poll(() => page.evaluate(() => window.innerWidth)).toBeLessThan(1000)
  const rail = await page.getByTestId('settings-rail').boundingBox()
  const heading = await page.getByRole('heading', { level: 1, name: 'Settings' }).boundingBox()
  expect((rail?.y ?? 0) + (rail?.height ?? 0)).toBeLessThanOrEqual((heading?.y ?? 0) + 1)
  expect(rail?.height ?? 999).toBeLessThan(120)
  await app.close()
})

test('AC-62.15 Dependencies card shows TTS asset rows and Get posts the asset', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSettingsSeam(page, {
    tts_onnx_vocab: { available: true, version: null, state: 'ready' },
    tts_spacy_model: { available: false, version: null, state: 'missing' },
  })
  await openSettings(page)
  const vocab = page.getByTestId('tts-asset-row-tts_onnx_vocab')
  const spacy = page.getByTestId('tts-asset-row-tts_spacy_model')
  await expect(vocab).toContainText('Ready')
  await expect(spacy).toContainText('Missing')
  await expect(page.getByTestId('tts-asset-get-btn-tts_onnx_vocab')).toHaveCount(0)
  await page.getByTestId('tts-asset-get-btn-tts_spacy_model').click()
  await expect
    .poll(async () =>
      page.evaluate(() =>
        ((window as unknown as { __e2eCalls?: Array<{ url: string; method: string; bodyKeys?: string[] }> })
          .__e2eCalls ?? []).filter((c) => c.url.includes('/models/download') && c.method === 'POST'),
      ),
    )
    .toEqual([expect.objectContaining({ bodyKeys: ['asset'] })])
  await app.close()
})

test('A-6 a trailing rail click keeps its entry current through a slow smooth scroll', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSettingsSeam(page)
  await openSettings(page)
  await expect(page.getByTestId('settings-rail-mcp')).toBeVisible()
  // Session 27 A-6: Chromium's Windows smooth scroll to a trailing section outlasts the old fixed
  // 800 ms click lock. Replay that deterministically: a smooth scrollIntoView animates for 1.5 s.
  await page.evaluate(() => {
    const native = Element.prototype.scrollIntoView
    Element.prototype.scrollIntoView = function slowSmooth(this: Element, arg?: boolean | ScrollIntoViewOptions) {
      const smooth = typeof arg === 'object' && arg.behavior === 'smooth'
      let scroller: HTMLElement | null = this.parentElement
      while (scroller !== null && !/(auto|scroll)/.test(getComputedStyle(scroller).overflowY)) {
        scroller = scroller.parentElement
      }
      if (!smooth || scroller === null) {
        native.call(this, arg as ScrollIntoViewOptions)
        return
      }
      const box = scroller
      const from = box.scrollTop
      const to = Math.min(
        from + this.getBoundingClientRect().top - box.getBoundingClientRect().top,
        box.scrollHeight - box.clientHeight,
      )
      const start = performance.now()
      const step = (now: number): void => {
        const k = Math.min(1, (now - start) / 1500)
        box.scrollTop = from + (to - from) * k
        if (k < 1) {
          requestAnimationFrame(step)
        }
      }
      requestAnimationFrame(step)
    }
  })
  await page.getByTestId('settings-rail-mcp').click()
  await expect(page.getByTestId('mcp-access-card')).toBeInViewport({ timeout: 5_000 })
  // Past the old lock and the end of the scroll, the clicked entry is still the current one.
  await page.waitForTimeout(2_500)
  await expect(page.getByTestId('settings-rail-mcp')).toHaveAttribute('aria-current', 'location')
  await expect(page.locator('[aria-current="location"]')).toHaveCount(1)
  await app.close()
})

// MEU-70 (Session 31) — appended. TRAIL_REACH, NO_SHIFT, BOX_SEPARATION, DEFAULT_WINDOW and
// TALL_WINDOW are defined once in docs/execution/plans/2026-10-10-gui-polish-residuals/implementation-plan.md.

const SECTION_TESTIDS: Record<(typeof RAIL_KEYS)[number], string> = {
  download: 'download-settings',
  transcript: 'transcript-settings',
  tts: 'tts-settings',
  convert: 'convert-settings',
  capture: 'capture-settings',
  console: 'console-settings',
  appearance: 'appearance-settings',
  dependencies: 'dependencies-section',
  readiness: 'readiness-card',
  mcp: 'mcp-access-card',
}

/** SECTION_SCROLL_MARGIN (scroll-mt-4). */
const SCROLL_MARGIN = 16

/** WINDOW_SETTLED: two animation frames, then window size unchanged for 500 ms. */
async function windowSettled(page: Page): Promise<void> {
  await page.evaluate(
    () =>
      new Promise<void>((resolve) => {
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            let last = `${window.innerWidth}x${window.innerHeight}`
            let stableSince = performance.now()
            const tick = (): void => {
              const now = `${window.innerWidth}x${window.innerHeight}`
              if (now !== last) {
                last = now
                stableSince = performance.now()
              }
              if (performance.now() - stableSince >= 500) {
                resolve()
              } else {
                window.setTimeout(tick, 50)
              }
            }
            tick()
          })
        })
      }),
  )
}

async function openSettledSettings(page: Page): Promise<void> {
  await installSettingsSeam(page)
  await openSettings(page)
  await expect(page.getByTestId('settings-readiness-count')).toBeVisible()
  await windowSettled(page)
}

type ScrollProbe = {
  inner: string
  clientHeight: number
  scrollHeight: number
  scrollTop: number
  sectionTop: number
  current: string | null
}

async function probe(page: Page, testId: string): Promise<ScrollProbe> {
  return page.evaluate((id) => {
    const main = document.querySelector('main') as HTMLElement
    const section = document.querySelector(`[data-testid="${id}"]`) as HTMLElement
    return {
      inner: `${window.innerWidth}x${window.innerHeight}`,
      clientHeight: main.clientHeight,
      scrollHeight: main.scrollHeight,
      scrollTop: main.scrollTop,
      sectionTop: section.getBoundingClientRect().top - main.getBoundingClientRect().top,
      current: document.querySelector('[aria-current="location"]')?.getAttribute('data-testid') ?? null,
    }
  }, testId)
}

/** TRAIL_REACH: every section becomes current after its own scroll; the bottom marks the last one. */
async function trailReach(page: Page, label: string): Promise<void> {
  const records: Array<{ key: string } & ScrollProbe> = []
  try {
    for (const key of RAIL_KEYS) {
      const testId = SECTION_TESTIDS[key]
      await page.getByTestId(testId).evaluate((element) => {
        element.scrollIntoView({ block: 'start', behavior: 'instant' as ScrollBehavior })
      })
      await page.waitForTimeout(150)
      records.push({ key, ...(await probe(page, testId)) })
      await expect(page.getByTestId(`settings-rail-${key}`)).toHaveAttribute('aria-current', 'location', { timeout: 5_000 })
      await expect(page.locator('[aria-current="location"]')).toHaveCount(1)
    }
    await page.evaluate(() => {
      const main = document.querySelector('main') as HTMLElement
      main.scrollTo({ top: main.scrollHeight, behavior: 'instant' as ScrollBehavior })
    })
    await page.waitForTimeout(150)
    const bottom = await probe(page, SECTION_TESTIDS.mcp)
    records.push({ key: 'bottom', ...bottom })
    await expect(page.getByTestId('settings-rail-mcp')).toHaveAttribute('aria-current', 'location', { timeout: 5_000 })
    expect(bottom.sectionTop, `${label}: last section top at max scroll`).toBeGreaterThanOrEqual(0)
    expect(bottom.sectionTop, `${label}: last section top at max scroll`).toBeLessThanOrEqual(SCROLL_MARGIN + 1)
  } finally {
    await test.info().attach(`trail-reach-${label}.json`, {
      body: JSON.stringify(records, null, 2),
      contentType: 'application/json',
    })
  }
}

test('AC-70.2 DEFAULT_WINDOW every section becomes current while scrolling', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await openSettledSettings(page)
  await trailReach(page, 'default')
  await app.close()
})

test('AC-70.2 TALL_WINDOW every section becomes current while scrolling', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await app.evaluate(({ BrowserWindow }) => {
    BrowserWindow.getAllWindows()[0]?.setSize(1280, 1000)
  })
  await openSettledSettings(page)
  await trailReach(page, 'tall')
  await app.close()
})

type HeadingSample = { current: string | null; boxes: Record<string, { x: number; y: number; width: number; height: number }> }

/** NO_SHIFT sample: section headings in document coordinates (main origin plus scrollTop). */
async function headingSample(page: Page): Promise<HeadingSample> {
  return page.evaluate(() => {
    const main = document.querySelector('main') as HTMLElement
    const origin = main.getBoundingClientRect()
    const boxes: Record<string, { x: number; y: number; width: number; height: number }> = {}
    for (const frame of document.querySelectorAll<HTMLElement>('[data-settings-section]')) {
      const heading = frame.querySelector('h2')
      if (heading === null) continue
      const r = heading.getBoundingClientRect()
      boxes[frame.getAttribute('data-settings-section') ?? ''] = {
        x: r.x - origin.left,
        y: r.y - origin.top + main.scrollTop,
        width: r.width,
        height: r.height,
      }
    }
    return {
      current: document.querySelector('[data-current="true"]')?.getAttribute('data-settings-section') ?? null,
      boxes,
    }
  })
}

test('AC-70.6 the current-section emphasis moves without shifting any heading', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await openSettledSettings(page)
  await page.evaluate(() => {
    document.querySelector('main')?.scrollTo({ top: 0, behavior: 'instant' as ScrollBehavior })
  })
  await expect(page.getByTestId('download-settings')).toHaveAttribute('data-current', 'true')
  const sampleA = await headingSample(page)
  await page.getByTestId('capture-settings').evaluate((element) => {
    element.scrollIntoView({ block: 'start', behavior: 'instant' as ScrollBehavior })
  })
  await expect(page.getByTestId('capture-settings')).toHaveAttribute('data-current', 'true')
  await expect(page.getByTestId('settings-rail-capture')).toHaveAttribute('aria-current', 'location')
  const sampleB = await headingSample(page)
  // Never compare a state with itself.
  expect(sampleA.current).toBe('download')
  expect(sampleB.current).toBe('capture')
  expect(Object.keys(sampleB.boxes).sort()).toEqual(Object.keys(sampleA.boxes).sort())
  for (const [key, a] of Object.entries(sampleA.boxes)) {
    const b = sampleB.boxes[key]
    for (const axis of ['x', 'y', 'width', 'height'] as const) {
      expect(Math.abs((b?.[axis] ?? Number.NaN) - a[axis]), `NO_SHIFT ${key}.${axis}`).toBeLessThanOrEqual(0.5)
    }
  }
  await expect(page.locator('[data-current="true"]')).toHaveCount(1)
  await expect
    .poll(() =>
      page.evaluate(() => {
        const style = (id: string) => getComputedStyle(document.querySelector(`[data-testid="${id}"]`) as HTMLElement)
        return {
          differs: style('capture-settings').backgroundColor !== style('download-settings').backgroundColor,
          border: style('capture-settings').borderLeftColor,
        }
      }),
    )
    .toMatchObject({ differs: true })
  // Both colours animate over --duration-fast, so poll the border like the background above.
  await expect
    .poll(() =>
      page.evaluate(
        () => getComputedStyle(document.querySelector('[data-testid="capture-settings"]') as HTMLElement).borderLeftColor,
      ),
    )
    .not.toMatch(/^(transparent|rgba\(0, 0, 0, 0\))$/)
  // BOX_SEPARATION: adjacent frames' border boxes stay more than SECTION_SCROLL_MARGIN apart.
  const gaps = await page.evaluate(() => {
    const list = Array.from(document.querySelectorAll<HTMLElement>('[data-settings-section]'))
    return list.slice(1).map((frame, index) => {
      const previous = list[index] as HTMLElement
      return {
        pair: `${previous.getAttribute('data-settings-section')}→${frame.getAttribute('data-settings-section')}`,
        gap: frame.getBoundingClientRect().top - previous.getBoundingClientRect().bottom,
      }
    })
  })
  for (const { pair, gap } of gaps) {
    expect(gap, `BOX_SEPARATION ${pair}`).toBeGreaterThan(SCROLL_MARGIN)
  }
  await app.close()
})

type SeamCall = { url: string; method: string; bodyKeys?: string[] }

async function seamCalls(page: Page): Promise<SeamCall[]> {
  return page.evaluate(() => (window as unknown as { __e2eCalls?: SeamCall[] }).__e2eCalls ?? [])
}

async function countCalls(page: Page, match: (call: SeamCall) => boolean): Promise<number> {
  return (await seamCalls(page)).filter(match).length
}

const depsGet = (call: SeamCall): boolean => call.url.includes('/health/dependencies') && call.method === 'GET'

test('AC-78.9 FFprobe row, and an ffmpeg_path PUT refetches dependencies while a theme PUT does not', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSettingsSeam(page)
  await openSettings(page)
  const row = page.getByTestId(DEPS_FFPROBE_ROW)
  await expect(row).toBeVisible({ timeout: 5_000 })
  await expect(row).toContainText('FFprobe')
  await expect(row).toContainText('available')

  // [neg] a theme PUT: once its ui refetch lands, the dependencies GET count is unchanged.
  const depsBeforeTheme = await countCalls(page, depsGet)
  const uiGets = (call: SeamCall): boolean => call.url.includes('/settings/ui') && call.method === 'GET'
  const uiGetsBefore = await countCalls(page, uiGets)
  await page.getByTestId('theme-light-btn').click()
  await expect
    .poll(() => countCalls(page, (call) => call.url.includes('/settings/ui') && call.method === 'PUT'), {
      timeout: 5_000,
    })
    .toBe(1)
  await expect.poll(() => countCalls(page, uiGets), { timeout: 5_000 }).toBeGreaterThan(uiGetsBefore)
  expect(await countCalls(page, depsGet)).toBe(depsBeforeTheme)

  // The ffmpeg path field is read-only; Browse is the control that writes ffmpeg_path (A-9).
  const depsBeforePut = await countCalls(page, depsGet)
  await page.getByTestId('browse-ffmpeg-btn').click()
  await expect
    .poll(
      () =>
        countCalls(
          page,
          (call) =>
            call.url.includes('/settings/downloader') && call.method === 'PUT' && (call.bodyKeys ?? []).includes('ffmpeg_path'),
        ),
      { timeout: 5_000 },
    )
    .toBe(1)
  await expect.poll(() => countCalls(page, depsGet), { timeout: 5_000 }).toBe(depsBeforePut + 1)
  await app.close()
})

// MEU-94 (Session 40): THEME_PROBE, THEME_COLOURS and THEME_GATE, defined once in
// docs/execution/plans/2026-10-24-gui-theme-path-fields/implementation-plan.md.

test('AC-94.7 Settings selects follow a live theme toggle', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSettingsSeam(page, {}, { themeProbe: { theme: { answer: 'dark' } } })
  await openSettings(page)
  await expectThemeColours(page, 'dark', THEME_FLOORS.settings)
  await page.getByTestId('theme-light-btn').click()
  await expectThemeColours(page, 'light', THEME_FLOORS.settings)
  await page.getByTestId('theme-dark-btn').click()
  await expectThemeColours(page, 'dark', THEME_FLOORS.settings)
  await expect(page).toHaveURL(/#\/settings/)
  await app.close()
})

test('AC-94.8 (a) cold boot with stored Light and no mirror holds the route until the theme', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSettingsSeam(page, {}, { themeProbe: { mirror: null, theme: { hold: true } } })
  await page.getByTestId('nav-settings').click()
  await expectThemeHeld(page)
  await releaseTheme(page, 'light')
  await expect.poll(async () => (await themeProbeCounts(page)).released).toBeGreaterThanOrEqual(1)
  await expect.poll(() => documentIsDark(page)).toBe(false)
  await expectInsertedOn(page, 'light', THEME_FLOORS.settings)
  await expectThemeColours(page, 'light', THEME_FLOORS.settings)
  await app.close()
})

test('AC-94.8 (b) cold boot with a stale dark mirror holds the route until the theme', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSettingsSeam(page, {}, { themeProbe: { mirror: 'dark', theme: { hold: true } } })
  await page.getByTestId('nav-settings').click()
  await expectThemeHeld(page)
  await releaseTheme(page, 'light')
  await expect.poll(async () => (await themeProbeCounts(page)).released).toBeGreaterThanOrEqual(1)
  await expect.poll(() => documentIsDark(page)).toBe(false)
  await expectInsertedOn(page, 'light', THEME_FLOORS.settings)
  await expectThemeColours(page, 'light', THEME_FLOORS.settings)
  await app.close()
})

test('AC-94.8 (c) a Light mirror paints the shell light while the theme is held', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSettingsSeam(page, {}, { themeProbe: { mirror: 'light', theme: { hold: true } } })
  await page.getByTestId('nav-settings').click()
  await expect.poll(async () => (await themeProbeCounts(page)).held).toBeGreaterThanOrEqual(1)
  await expect.poll(() => documentIsDark(page)).toBe(false)
  await expectThemeHeld(page)
  await releaseTheme(page, 'light')
  await expectThemeColours(page, 'light', THEME_FLOORS.settings)
  await app.close()
})

test('AC-94.8 (d) the mirror persists across launches on the same app data', async () => {
  const dir = mkdtempSync(join(tmpdir(), 'avkit-e2e-theme-mirror-'))
  const first = await launchWithAppData(dir)
  const firstPage = await first.firstWindow()
  await installSettingsSeam(firstPage, {}, { themeProbe: { theme: { answer: 'light' } } })

  await expect.poll(() => storedMirror(firstPage)).toBe('light')
  await first.close()

  const second = await launchWithAppData(dir)
  const page = await second.firstWindow()
  await installSettingsSeam(page, {}, { themeProbe: { theme: { hold: true } } })
  await page.getByTestId('nav-settings').click()

  await expect.poll(async () => (await themeProbeCounts(page)).held).toBeGreaterThanOrEqual(1)
  await expect.poll(() => documentIsDark(page)).toBe(false)
  await releaseTheme(page, 'dark')
  await expect.poll(() => documentIsDark(page)).toBe(true)
  await expectThemeColours(page, 'dark', THEME_FLOORS.settings)
  await second.close()
})

// docs/execution/plans/2026-10-26-gui-keyboard-palette/implementation-plan.md (APPEARANCE).

async function uiThemePuts(page: Page): Promise<unknown[]> {
  const calls = await page.evaluate(
    () =>
      (window as unknown as { __e2eCalls?: Array<{ url: string; method: string; body?: Record<string, unknown> }> })
        .__e2eCalls ?? [],
  )
  return calls.filter((row) => row.url.includes('/settings/ui') && row.method === 'PUT').map((row) => row.body?.theme)
}

test('AC-96.13 APPEARANCE Ctrl+Shift+L and the palette Appearance: Dark save the theme', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSettingsSeam(page)
  await expect(page.locator('html')).toHaveClass(/dark/)

  await page.keyboard.press('Control+Shift+L')
  await expect(page.locator('html')).not.toHaveClass(/dark/)
  await expect.poll(async () => uiThemePuts(page)).toEqual(['light'])

  await page.getByTestId('header-palette-btn').click()
  await page.getByTestId('command-palette-input').fill('Appearance')
  await page.getByRole('dialog').getByRole('button', { name: 'Appearance: Dark' }).click()
  await expect(page.locator('html')).toHaveClass(/dark/)
  await expect.poll(async () => uiThemePuts(page)).toEqual(['light', 'dark'])
  await app.close()
})

// MEU-118 (Session 51): DEVICE_OPTIONS in Electron. The Settings device select offers what
// `GET /models/available` reports for this build (AC-118.5).

const PYTORCH_REASON = "This build can't run PyTorch models. Choose an ONNX model."

function catalogRow(id: string, devices: string[], available = true): Record<string, unknown> {
  return {
    id,
    name: id,
    format: id.includes('onnx') ? 'ONNX' : 'PyTorch',
    precision: 'FP32',
    size_bytes: 1,
    path: null,
    is_downloaded: false,
    devices,
    available,
    reason: available ? null : PYTORCH_REASON,
  }
}

// A packaged CPU build: the PyTorch row is unavailable, the ONNX rows list auto and cpu.
const CPU_ONLY_REPORT = [
  catalogRow('kokoro-pt-fp32', ['auto', 'cpu'], false),
  catalogRow('kokoro-onnx-fp32', ['auto', 'cpu']),
  catalogRow('kokoro-onnx-int8', ['auto', 'cpu']),
]

const DEVICE_REPORTS = [
  { name: 'a CPU-only report', report: CPU_ONLY_REPORT, expected: ['auto', 'cpu'] },
  {
    name: 'a CUDA report',
    report: [catalogRow('kokoro-pt-fp32', ['auto', 'cuda', 'cpu']), catalogRow('kokoro-onnx-fp32', ['auto', 'cuda', 'cpu'])],
    expected: ['auto', 'cuda', 'cpu'],
  },
  {
    name: 'an unavailable PyTorch row with all four devices plus an ONNX row with auto and cpu',
    report: [
      catalogRow('kokoro-pt-fp32', ['auto', 'cuda', 'cpu', 'mps'], false),
      catalogRow('kokoro-onnx-fp32', ['auto', 'cpu']),
    ],
    expected: ['auto', 'cpu'],
  },
]

// A settings PUT is debounced (`DEBOUNCE_MS`, 300 ms); this waits well past one window.
const PAST_DEBOUNCE_MS = 1_000

const reportGets = (call: SeamCall): boolean => call.url.includes('/models/available') && call.method === 'GET'

async function deviceValues(page: Page): Promise<string[]> {
  return page
    .getByTestId('settings-leaf-device')
    .locator('option')
    .evaluateAll((options) => options.map((option) => (option as HTMLOptionElement).value))
}

async function ttsPuts(page: Page): Promise<unknown[]> {
  const calls = await page.evaluate(
    () =>
      (window as unknown as { __e2eCalls?: Array<{ url: string; method: string; body?: Record<string, unknown> }> })
        .__e2eCalls ?? [],
  )
  return calls.filter((row) => row.url.includes('/settings/tts') && row.method === 'PUT').map((row) => row.body)
}

for (const { name, report, expected } of DEVICE_REPORTS) {
  test(`AC-118.5 ${name} offers ${expected.join(', ')}`, async () => {
    const app = await launchApp()
    const page = await app.firstWindow()
    await installSettingsSeam(page, {}, { catalog: report })
    await openSettings(page)
    await expect.poll(() => countCalls(page, reportGets), { timeout: 5_000 }).toBeGreaterThanOrEqual(1)
    await expect.poll(() => deviceValues(page), { timeout: 5_000 }).toEqual(expected)
    // Still the same once the report has landed, not only before it.
    await page.waitForTimeout(PAST_DEBOUNCE_MS)
    expect(await deviceValues(page)).toEqual(expected)
    await app.close()
  })
}

test('AC-118.5 a stored cuda with a CPU-only report shows auto with no PUT, and choosing cpu PUTs it', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSettingsSeam(page, {}, { catalog: CPU_ONLY_REPORT, device: 'cuda' })
  await openSettings(page)
  const select = page.getByTestId('settings-leaf-device')
  // Until the report lands the select lists the stored cuda; once it has, cuda isn't offered.
  await expect.poll(() => deviceValues(page), { timeout: 5_000 }).toEqual(['auto', 'cpu'])
  await expect(select).toHaveValue('auto')
  await page.waitForTimeout(PAST_DEBOUNCE_MS)
  expect(await ttsPuts(page)).toEqual([])
  await select.selectOption('cpu')
  await expect.poll(() => ttsPuts(page), { timeout: 5_000 }).toEqual([{ device: 'cpu' }])
  await page.waitForTimeout(PAST_DEBOUNCE_MS)
  expect(await ttsPuts(page)).toEqual([{ device: 'cpu' }])
  await app.close()
})
