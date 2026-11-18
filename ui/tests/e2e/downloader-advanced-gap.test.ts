import { expect, test, type ElectronApplication, type Page } from '@playwright/test'
import { spawnSync, type ChildProcess } from 'node:child_process'
import { existsSync, mkdirSync, mkdtempSync, readFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { launchElectron } from './electron-app'

/**
 * MEU-159 (Session 94, D-1177, D-1180): the Downloader leaves no empty band under the Advanced
 * disclosure. Row 3 measured the band on the unchanged page: the empty status wrapper (`min-h-6`,
 * 24 px) plus one 16 px gap. Each test measures a fresh page on a scratch AVKIT_APP_DATA, with
 * no add and no SABR or cookie action first, because nothing clears a message once it shows.
 *
 * - AC-159.2 and AC-159.3: at the default 1280x800 window, collapsed and expanded, the status is
 *   empty, the eight Advanced ids keep their DOM order, the visible ids match the cookie mode,
 *   TAIL <= 1 px and GAP = 16 +/- 1 px.
 * - AC-159.4: the same at 700x650.
 * - AC-159.5 (guard): an Add with the URL empty shows "URL is required" where the line is today.
 *
 * The launch helpers are row 1b's (`help-f1-mount.test.ts`, copied from
 * `convert-browse-mount.test.ts:27-212`). Nothing reaches the network.
 */

const PLACEHOLDER_PREFIX = 'http://127.0.0.1:9/'
const POWERSHELL_TIMEOUT_MS = 15_000
const CLOSE_TIMEOUT_MS = 30_000
const CHUNK_DELAY_MS = 1_500
const TEST_TIMEOUT_MS = 240_000

type Harness = { app: ElectronApplication; page: Page; close: () => Promise<void> }

/** Every close function of an app that is still open; afterEach closes them. */
const live = new Set<() => Promise<void>>()

test.afterEach(async () => {
  for (const close of [...live]) await close()
})

function log(message: string): void {
  console.log(`[s94-e2e] ${new Date().toISOString()} ${message}`)
}

function sleep(ms: number): Promise<void> {
  return new Promise((done) => setTimeout(done, ms))
}

function readBackendPid(appData: string): number | null {
  const file = join(appData, 'backend.json')
  if (!existsSync(file)) return null
  try {
    const parsed = JSON.parse(readFileSync(file, 'utf8')) as { pid?: unknown }
    return typeof parsed.pid === 'number' ? parsed.pid : null
  } catch {
    return null
  }
}

function running(pid: number): boolean {
  try {
    process.kill(pid, 0)
    return true
  } catch {
    return false
  }
}

/** The process's start time in UTC, or null when no process has that pid. */
function startTime(pid: number): string | null {
  const result = spawnSync(
    'powershell',
    [
      '-NoProfile',
      '-Command',
      `$p = Get-Process -Id ${String(pid)} -ErrorAction SilentlyContinue; if ($p) { $p.StartTime.ToUniversalTime().ToString('o') }`,
    ],
    { encoding: 'utf8', timeout: POWERSHELL_TIMEOUT_MS },
  )
  const text = (result.stdout ?? '').trim()
  return text === '' ? null : text
}

/** After close: waits for the recorded backend to exit, and stops it only if pid and start time still match. */
async function stopRecordedBackend(pid: number | null, started: string | null): Promise<void> {
  if (pid === null) return
  const deadline = Date.now() + 10_000
  while (running(pid) && Date.now() < deadline) {
    await sleep(250)
  }
  if (!running(pid)) {
    log(`backend pid ${String(pid)} exited after close`)
    return
  }
  const now = startTime(pid)
  if (started !== null && now === started) {
    log(`backend pid ${String(pid)} (started ${started}) still running after close; stopping it`)
    process.kill(pid)
  } else {
    log(`pid ${String(pid)} is running but its start time ${String(now)} is not ${String(started)}; left alone`)
  }
}

/**
 * Closes the app within CLOSE_TIMEOUT_MS. If close has not finished by then, kills the Electron
 * process this launch started, through the handle taken at launch, and waits for close to settle.
 */
async function closeBounded(app: ElectronApplication, child: ChildProcess, label: string): Promise<void> {
  const closing = app.close()
  let timer: ReturnType<typeof setTimeout> | undefined
  const timedOut = await Promise.race([
    closing.then(() => false),
    new Promise<boolean>((done) => {
      timer = setTimeout(() => done(true), CLOSE_TIMEOUT_MS)
    }),
  ]).finally(() => clearTimeout(timer))
  if (!timedOut) return
  log(`${label}: close did not finish in ${String(CLOSE_TIMEOUT_MS)} ms; killing this launch's Electron pid ${String(child.pid)}`)
  if (child.exitCode === null && child.signalCode === null) child.kill()
  await Promise.race([closing, sleep(10_000)])
}

/** A fresh app on a scratch profile, with the Convert and Capture chunk delay in main. */
async function launch(label: string): Promise<Harness> {
  const root = mkdtempSync(join(tmpdir(), `avkit-e2e-s94-${label}-`))
  const appData = join(root, 'profile')
  mkdirSync(appData, { recursive: true })
  log(`${label}: launching Electron`)
  const app = await launchElectron({ env: { AVKIT_APP_DATA: appData } })
  // Taken now: after close, Playwright has disposed the app object and process() throws.
  const child = app.process()
  log(`${label}: Electron pid ${String(child.pid)}`)
  let backendPid: number | null = null
  let backendStarted: string | null = null
  let closed: Promise<void> | undefined
  const close = (): Promise<void> => {
    closed ??= (async () => {
      live.delete(close)
      log(`${label}: closing`)
      try {
        await closeBounded(app, child, label)
      } finally {
        await stopRecordedBackend(backendPid, backendStarted)
      }
      log(`${label}: closed`)
    })()
    return closed
  }
  live.add(close)
  try {
    const page = await app.firstWindow({ timeout: 60_000 })
    log(`${label}: first window open; waiting for the real backend URL`)
    await expect
      .poll(
        async () =>
          page.evaluate(async () =>
            (window as unknown as { api: { getBackendUrl(): Promise<string> } }).api.getBackendUrl(),
          ),
        { timeout: 120_000, intervals: [500] },
      )
      .not.toContain(PLACEHOLDER_PREFIX)
    await expect.poll(async () => readBackendPid(appData), { timeout: 30_000 }).not.toBeNull()
    backendPid = readBackendPid(appData)
    backendStarted = backendPid === null ? null : startTime(backendPid)
    log(`${label}: backend pid ${String(backendPid)} started ${String(backendStarted)}`)
    // Before the first Convert or Capture visit: hold their chunks back (the handler row 1a proved).
    await app.evaluate(
      ({ net, protocol }, delayMs) => {
        protocol.handle('file', async (request) => {
          if (/(ConvertPage|CapturePage)-[^/]*\.js$/.test(new URL(request.url).pathname)) {
            await new Promise((done) => setTimeout(done, delayMs))
          }
          return net.fetch(request.url, { bypassCustomProtocolHandlers: true })
        })
      },
      CHUNK_DELAY_MS,
    )
    log(`${label}: ready`)
    return { app, page, close }
  } catch (error) {
    log(`${label}: launch failed (${error instanceof Error ? error.message.split('\n')[0] : String(error)}); closing`)
    await close()
    throw error
  }
}

const SETTLE_MS = 300

/** The eight Advanced ids in the panel's DOM order (row 3 recorded it, `us-row3-measure.txt`). */
const ADVANCED_IDS = [
  'sabr-status',
  'sabr-check-btn',
  'sabr-force-btn',
  'sabr-clear-btn',
  'cookie-browser',
  'cookie-profile',
  'cookie-file',
  'cookie-test-btn',
]

/** The ids shown in every cookie mode once the panel is open. */
const ALWAYS_SHOWN = ['sabr-status', 'sabr-check-btn', 'sabr-force-btn', 'sabr-clear-btn', 'cookie-test-btn']

/** The ids each cookie mode adds (`cookie-bar.ts:78-83`). */
const SHOWN_BY_MODE: Record<string, string[]> = {
  none: [],
  browser: ['cookie-browser', 'cookie-profile'],
  file: ['cookie-file'],
}

type Box = { top: number; bottom: number; left: number; right: number; height: number }

type Measure = {
  tail: number
  gap: number
  panelHeight: number
  statusText: string | null
  addStatusPresent: boolean
  addStatusVisible: boolean
  errorBannerPresent: boolean
  errorBannerVisible: boolean
  cookieMode: string | null
  panelDomIds: string[]
  visibleIds: string[]
  form: Box | null
  status: Box | null
  banner: Box | null
  bannerInStatus: boolean
  queue: Box | null
}

/**
 * Row 3's measurement, with no production id: the form, its parent scroller, the disclosure that
 * holds `add-advanced-toggle`, the panel it controls, the status wrapper (the form's next
 * sibling) and the queue region. TAIL is the scrollable space below the disclosure; GAP is the
 * visible distance from the disclosure to the queue, both read with the scroller at its end.
 */
async function measure(page: Page): Promise<Measure> {
  await page.evaluate(() => {
    const scroller = document.querySelector('[data-testid="downloader-page"] form')?.parentElement
    if (scroller) scroller.scrollTop = scroller.scrollHeight
  })
  await sleep(SETTLE_MS)
  return page.evaluate((ids) => {
    const box = (el: Element | null | undefined): Box | null => {
      if (!el) return null
      const r = el.getBoundingClientRect()
      return { top: r.top, bottom: r.bottom, left: r.left, right: r.right, height: r.height }
    }
    const form = document.querySelector('[data-testid="downloader-page"] form')
    const scroller = form?.parentElement ?? null
    const toggle = document.querySelector('[data-testid="add-advanced-toggle"]')
    const disclosure = toggle?.closest('section') ?? null
    const panelId = toggle?.getAttribute('aria-controls') ?? ''
    const panel = panelId ? document.getElementById(panelId) : null
    const status = form?.nextElementSibling ?? null
    const queue = document.querySelector('[data-testid="download-queue-region"]')
    const addStatus = status?.querySelector('[data-testid="add-status"]') ?? null
    const banner = status?.querySelector('[data-testid="error-banner"]') ?? null
    const disclosureBox = box(disclosure)
    const scrollerBox = box(scroller)
    const queueBox = box(queue)
    const tail =
      disclosureBox && scrollerBox && scroller
        ? scroller.scrollHeight - (disclosureBox.bottom - scrollerBox.top + scroller.scrollTop)
        : Number.NaN
    const gap = disclosureBox && queueBox ? queueBox.top - disclosureBox.bottom : Number.NaN
    const checked = document.querySelector('[data-testid^="cookie-mode-"]:checked')
    const panelDomIds = panel
      ? [...panel.querySelectorAll('[data-testid]')]
          .map((el) => el.getAttribute('data-testid') ?? '')
          .filter((id) => ids.includes(id))
      : []
    const visibleIds = ids
      .filter((id) => panel?.querySelector(`[data-testid="${id}"]`)?.checkVisibility() === true)
      .sort()
    return {
      tail,
      gap,
      panelHeight: box(panel)?.height ?? Number.NaN,
      statusText: status instanceof HTMLElement ? status.innerText.trim() : null,
      addStatusPresent: addStatus !== null,
      addStatusVisible: addStatus?.checkVisibility() ?? false,
      errorBannerPresent: banner !== null,
      errorBannerVisible: banner?.checkVisibility() ?? false,
      cookieMode: checked instanceof HTMLInputElement ? checked.value : null,
      panelDomIds,
      visibleIds,
      form: box(form),
      status: box(status),
      banner: box(banner),
      bannerInStatus: status !== null && banner !== null && status.contains(banner),
      queue: queueBox,
    }
  }, ADVANCED_IDS)
}

function shownFor(mode: string | null): string[] {
  const extra = mode === null ? undefined : SHOWN_BY_MODE[mode]
  if (extra === undefined) return [`unknown cookie mode ${String(mode)}`]
  return [...ALWAYS_SHOWN, ...extra].sort()
}

/** The checks of AC-159.2 (collapsed) or AC-159.3 (expanded), each part on its own. */
function checkCase(m: Measure, expanded: boolean): void {
  // The status is empty: no text, both placeholders present and hidden.
  expect(m.statusText).toBe('')
  expect(m.addStatusPresent).toBe(true)
  expect(m.addStatusVisible).toBe(false)
  expect(m.errorBannerPresent).toBe(true)
  expect(m.errorBannerVisible).toBe(false)
  // Presence and order of the eight ids, visible or not.
  expect(m.panelDomIds).toEqual(ADVANCED_IDS)
  // Visibility, apart from the order: none when collapsed, the set for the mode when expanded.
  expect(m.visibleIds).toEqual(expanded ? shownFor(m.cookieMode) : [])
  // No band under the disclosure: no scrollable tail, one gap to the queue.
  expect(m.tail).toBeLessThanOrEqual(1)
  expect(Math.abs(m.gap - 16)).toBeLessThanOrEqual(1)
  if (!expanded) expect(m.panelHeight).toBe(0)
}

async function freshDownloader(label: string): Promise<Page> {
  const { page } = await launch(label)
  await page.getByTestId('downloader-page').waitFor({ state: 'visible', timeout: 30_000 })
  return page
}

test('AC-159.2 a fresh Downloader page at 1280x800 with Advanced collapsed has no band under it', async () => {
  test.setTimeout(TEST_TIMEOUT_MS)
  const page = await freshDownloader('ac-159-2')
  checkCase(await measure(page), false)
})

test('AC-159.3 a fresh Downloader page at 1280x800 with Advanced expanded has no band under it', async () => {
  test.setTimeout(TEST_TIMEOUT_MS)
  const page = await freshDownloader('ac-159-3')
  await page.getByTestId('add-advanced-toggle').click()
  checkCase(await measure(page), true)
})

test('AC-159.4 the same at 700x650, collapsed and expanded', async () => {
  test.setTimeout(TEST_TIMEOUT_MS)
  const page = await freshDownloader('ac-159-4')
  await page.setViewportSize({ width: 700, height: 650 })
  checkCase(await measure(page), false)
  await page.getByTestId('add-advanced-toggle').click()
  checkCase(await measure(page), true)
})

test('AC-159.5 guard: a message shows in the status line where it does today', async () => {
  test.setTimeout(TEST_TIMEOUT_MS)
  const page = await freshDownloader('ac-159-5')
  await expect(page.getByTestId('url-input')).toHaveValue('')
  await page.getByTestId('add-btn').click()
  await page.getByTestId('error-banner').waitFor({ state: 'visible', timeout: 10_000 })
  const m = await measure(page)
  const text = await page.getByTestId('error-banner').innerText()
  expect(text).toContain('URL is required')
  expect(m.errorBannerVisible).toBe(true)
  expect(m.bannerInStatus).toBe(true)
  expect(m.form).not.toBeNull()
  expect(m.status).not.toBeNull()
  expect(m.banner).not.toBeNull()
  expect(m.queue).not.toBeNull()
  if (m.form && m.status && m.banner && m.queue) {
    expect(m.status.top).toBeGreaterThanOrEqual(m.form.bottom)
    expect(m.banner.top).toBeGreaterThanOrEqual(m.status.top)
    expect(m.banner.bottom).toBeLessThanOrEqual(m.status.bottom)
    expect(m.queue.top).toBeGreaterThan(m.banner.bottom)
  }
})
