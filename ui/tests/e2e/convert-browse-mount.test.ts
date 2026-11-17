import { expect, test, type ElectronApplication, type Page } from '@playwright/test'
import { spawnSync, type ChildProcess } from 'node:child_process'
import { existsSync, mkdirSync, mkdtempSync, readFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { launchElectron } from './electron-app'

/**
 * MEU-157 (Session 89, D-1101, D-1108, D-1111): Ctrl+O's Browse request waits for the Convert
 * page. The page is a lazy chunk, so a Ctrl+O pressed while it loads used to dispatch its browse
 * event before the page listened, and no picker opened. Each test runs a fresh app against the
 * real backend; before the first Convert visit a `file` protocol handler in main holds the
 * ConvertPage chunk back by 1 500 ms (the handler row 3a's probe proved) and the files dialog is
 * replaced by a stub that counts picks and returns no files. Nothing reaches the network.
 *
 * - AC-157.8 and AC-157.9: one or two Ctrl+O while the page loads open exactly one picker.
 * - AC-157.10: a Ctrl+O on the mounted page opens exactly one picker.
 * - AC-157.11: a request held while the page loads is dropped when the user leaves Convert.
 *
 * The launch helpers are copied from `queue-pause-feedback.test.ts:151-284` (Session 88): scratch
 * AVKIT_APP_DATA per launch, the backend pid recorded from `backend.json` and stopped after close
 * only if its start time still matches, and a bounded close. A `setup:` error means the delay did
 * not hold the chunk back, so the test did not test the race (S8).
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
  console.log(`[s89-e2e] ${new Date().toISOString()} ${message}`)
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

/** A fresh app on a scratch profile, with the chunk delay and the counting files dialog in main. */
async function launch(label: string): Promise<Harness> {
  const root = mkdtempSync(join(tmpdir(), `avkit-e2e-s89-${label}-`))
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
    // Before the first Convert visit: hold the ConvertPage chunk back, and count the pickers.
    await app.evaluate(
      ({ ipcMain, net, protocol }, delayMs) => {
        const store = globalThis as { __s89Picks?: number }
        store.__s89Picks = 0
        protocol.handle('file', async (request) => {
          if (/ConvertPage-[^/]*\.js$/.test(new URL(request.url).pathname)) {
            await new Promise((done) => setTimeout(done, delayMs))
          }
          return net.fetch(request.url, { bypassCustomProtocolHandlers: true })
        })
        ipcMain.removeHandler('show-files-dialog')
        ipcMain.handle('show-files-dialog', () => {
          store.__s89Picks = (store.__s89Picks ?? 0) + 1
          return []
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

async function picks(app: ElectronApplication): Promise<number> {
  return app.evaluate(() => (globalThis as { __s89Picks?: number }).__s89Picks ?? 0)
}

/** Throws a setup error when the Convert page has already mounted: the race was not tested. */
async function requireNotMounted(page: Page, when: string): Promise<void> {
  if ((await page.getByTestId('convert-page').count()) !== 0) {
    throw new Error(`setup: convert-page was already mounted ${when}; the chunk delay did not hold it back`)
  }
}

/** Switches to Convert and returns while its page is still loading. */
async function switchToLoadingConvert(page: Page): Promise<void> {
  await page.getByTestId('nav-convert').click()
  await page.waitForFunction(() => window.location.hash === '#/convert', undefined, { timeout: 10_000 })
  await requireNotMounted(page, 'before Ctrl+O')
}

test('AC-157.8 a Ctrl+O pressed while the Convert page loads opens one picker once it mounts', async () => {
  test.setTimeout(TEST_TIMEOUT_MS)
  const { app, page } = await launch('ac-157-8')
  await switchToLoadingConvert(page)
  await page.keyboard.press('Control+O')
  await expect(page.getByTestId('convert-page')).toBeVisible({ timeout: 30_000 })
  await sleep(1_000)
  // One Ctrl+O while the page loads opens one picker.
  const picked = await picks(app)
  expect(picked).toBe(1)
})

test('AC-157.9 two Ctrl+O pressed while the Convert page loads open one picker', async () => {
  test.setTimeout(TEST_TIMEOUT_MS)
  const { app, page } = await launch('ac-157-9')
  await switchToLoadingConvert(page)
  await page.keyboard.press('Control+O')
  await page.keyboard.press('Control+O')
  await requireNotMounted(page, 'after the two Ctrl+O')
  await expect(page.getByTestId('convert-page')).toBeVisible({ timeout: 30_000 })
  await sleep(1_000)
  // Two Ctrl+O while the page loads open one picker.
  const picked = await picks(app)
  expect(picked).toBe(1)
})

test('AC-157.10 a Ctrl+O on the mounted Convert page opens one picker at once', async () => {
  test.setTimeout(TEST_TIMEOUT_MS)
  const { app, page } = await launch('ac-157-10')
  await page.getByTestId('nav-convert').click()
  await expect(page.getByTestId('convert-page')).toBeVisible({ timeout: 30_000 })
  await page.keyboard.press('Control+O')
  await sleep(2_000)
  // A Ctrl+O on the mounted page opens one picker.
  const picked = await picks(app)
  expect(picked).toBe(1)
})

test('AC-157.11 a request held while the page loads is dropped when the user leaves Convert', async () => {
  test.setTimeout(TEST_TIMEOUT_MS)
  const { app, page } = await launch('ac-157-11')
  await switchToLoadingConvert(page)
  await page.keyboard.press('Control+O')
  // Past navigateAndDeliver's two frames, so the request has run on /convert and is held.
  await page.evaluate(
    () =>
      new Promise<void>((done) => {
        window.requestAnimationFrame(() => {
          window.requestAnimationFrame(() => {
            setTimeout(done, 150)
          })
        })
      }),
  )
  await requireNotMounted(page, 'after the request ran; the drop path would not be tested')
  await page.getByTestId('nav-downloader').click()
  await sleep(3_000)
  await page.getByTestId('nav-convert').click()
  await expect(page.getByTestId('convert-page')).toBeVisible({ timeout: 30_000 })
  await sleep(2_000)
  // A request dropped on leaving Convert opens no picker on the next visit.
  const picked = await picks(app)
  expect(picked).toBe(0)
})
