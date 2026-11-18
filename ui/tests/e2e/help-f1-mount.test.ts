import { expect, test, type ElectronApplication, type Page } from '@playwright/test'
import { spawnSync, type ChildProcess } from 'node:child_process'
import { existsSync, mkdirSync, mkdtempSync, readFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { launchElectron } from './electron-app'

/**
 * MEU-158 (Session 94, D-1175, D-1176, D-1179): an F1 pressed while a lazy page loads opens that
 * page's help panel once it mounts. Each test runs a fresh app against the real backend on a
 * scratch AVKIT_APP_DATA; before the first Convert or Capture visit a `file` protocol handler in
 * main holds the ConvertPage and CapturePage chunks back by 1 500 ms (the handler row 1a's probe
 * proved). There is no dialog stub, and nothing reaches the network.
 *
 * - AC-158.8 and AC-158.9: one F1 while Convert (Capture) loads opens its help panel, and the
 *   Downloader's panel is not expanded.
 * - AC-158.10: two F1 while Convert loads open the panel once.
 * - AC-158.11: an F1 held while Convert loads is dropped when the user leaves Convert.
 * - AC-158.12 (guard): F1 on the mounted Convert page toggles its panel at once, twice.
 *
 * The launch helpers are copied from `convert-browse-mount.test.ts:27-212` (Session 89), with the
 * handler regex widened and the dialog stub removed. A `setup:` error means the delay did not hold
 * the chunk back, so the test did not test the race (S8).
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
const DOWNLOADER_HELP_KEY = 'av-kit:downloader-help:main:state'

/** Throws a setup error when the page has already mounted: the race was not tested. */
async function requireNotMounted(page: Page, pageId: string, when: string): Promise<void> {
  if ((await page.getByTestId(pageId).count()) !== 0) {
    throw new Error(`setup: ${pageId} was already mounted ${when}; the chunk delay did not hold it back`)
  }
}

/** Switches to a lazy page and returns while it is still loading. */
async function switchToLoading(page: Page, navId: string, pageId: string): Promise<void> {
  const hash = `#/${navId.replace(/^nav-/, '')}`
  await page.getByTestId(navId).click()
  await page.waitForFunction((want) => window.location.hash === want, hash, { timeout: 10_000 })
  await requireNotMounted(page, pageId, 'before F1')
}

/** Waits for the page to be visible and SETTLE_MS more. */
async function waitMounted(page: Page, pageId: string): Promise<void> {
  await page.getByTestId(pageId).waitFor({ state: 'visible', timeout: 30_000 })
  await sleep(SETTLE_MS)
}

async function helpExpanded(page: Page, pageId: string): Promise<string | null> {
  return page
    .getByTestId(pageId)
    .getByTestId('help-card')
    .getByRole('button', { name: /How it works/ })
    .getAttribute('aria-expanded')
}

async function downloaderHelpState(page: Page): Promise<string | null> {
  return page.evaluate((key) => window.localStorage.getItem(key), DOWNLOADER_HELP_KEY)
}

test('AC-158.8 an F1 pressed while the Convert page loads opens its help once it mounts', async () => {
  test.setTimeout(TEST_TIMEOUT_MS)
  const { page } = await launch('ac-158-8')
  await switchToLoading(page, 'nav-convert', 'convert-page')
  await page.keyboard.press('F1')
  await waitMounted(page, 'convert-page')
  const expanded = await helpExpanded(page, 'convert-page')
  const downloader = await downloaderHelpState(page)
  expect(expanded).toBe('true')
  expect(downloader).not.toBe('expanded')
})

test('AC-158.9 an F1 pressed while the Capture page loads opens its help once it mounts', async () => {
  test.setTimeout(TEST_TIMEOUT_MS)
  const { page } = await launch('ac-158-9')
  await switchToLoading(page, 'nav-capture', 'capture-page')
  await page.keyboard.press('F1')
  await waitMounted(page, 'capture-page')
  const expanded = await helpExpanded(page, 'capture-page')
  const downloader = await downloaderHelpState(page)
  expect(expanded).toBe('true')
  expect(downloader).not.toBe('expanded')
})

test('AC-158.10 two F1 pressed while the Convert page loads open its help once', async () => {
  test.setTimeout(TEST_TIMEOUT_MS)
  const { page } = await launch('ac-158-10')
  await switchToLoading(page, 'nav-convert', 'convert-page')
  await page.keyboard.press('F1')
  await page.keyboard.press('F1')
  await requireNotMounted(page, 'convert-page', 'after the two F1')
  await waitMounted(page, 'convert-page')
  const expanded = await helpExpanded(page, 'convert-page')
  expect(expanded).toBe('true')
})

test('AC-158.11 an F1 held while the Convert page loads is dropped when the user leaves Convert', async () => {
  test.setTimeout(TEST_TIMEOUT_MS)
  const { page } = await launch('ac-158-11')
  await switchToLoading(page, 'nav-convert', 'convert-page')
  await page.keyboard.press('F1')
  await requireNotMounted(page, 'convert-page', 'before leaving Convert; the drop path would not be tested')
  await page.getByTestId('nav-downloader').click()
  await waitMounted(page, 'downloader-page')
  await page.getByTestId('nav-convert').click()
  await waitMounted(page, 'convert-page')
  const expanded = await helpExpanded(page, 'convert-page')
  const downloader = await downloaderHelpState(page)
  expect(expanded).toBe('false')
  expect(downloader).not.toBe('expanded')
})

test('AC-158.12 guard: F1 on the mounted Convert page toggles its help at once', async () => {
  test.setTimeout(TEST_TIMEOUT_MS)
  const { page } = await launch('ac-158-12')
  await page.getByTestId('nav-convert').click()
  await waitMounted(page, 'convert-page')
  await page.keyboard.press('F1')
  await sleep(SETTLE_MS)
  const opened = await helpExpanded(page, 'convert-page')
  await page.keyboard.press('F1')
  await sleep(SETTLE_MS)
  const closed = await helpExpanded(page, 'convert-page')
  expect(opened).toBe('true')
  expect(closed).toBe('false')
})
