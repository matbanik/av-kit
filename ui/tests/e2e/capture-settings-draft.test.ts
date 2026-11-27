import { expect, test, type ElectronApplication, type Page, type Request } from '@playwright/test'
import { spawnSync, type ChildProcess } from 'node:child_process'
import { copyFileSync, existsSync, mkdirSync, mkdtempSync, readFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

import { launchElectron } from './electron-app'

/**
 * MEU-151 (Session 81, amendment A2, D-975): the capture Save in the real app, against the real
 * backend that main spawns. It replaces the manual row-5 check HC-4 (Mat, 2026-11-16: "why are
 * you giving me e2e tests manually! This should be done with framework and scripts!").
 *
 * AVKIT_APP_DATA is a new folder under tmpdir(), and the inbox folder the test saves is a tmp
 * folder, so nothing reads or writes the normal profile, database or settings. Main publishes
 * the port-9 placeholder first and the real backend's port once it prints AVKIT_READY; the test
 * waits for the real port before it acts. In an E2E run main does not stop its backend on quit,
 * so the test records the backend pid from `backend.json` in its scratch profile and, after
 * close, stops that pid only if it is still running with the start time recorded at launch.
 *
 * Bounded waits: the powershell start-time read, every backend request and the app close have
 * their own time limits, and each step prints a timed `[s81-e2e]` line. If close does not finish,
 * the Electron process this launch started is killed through its own handle. An afterEach closes
 * the app if the test timed out with it open.
 */

const PLACEHOLDER_PREFIX = 'http://127.0.0.1:9/'
const POWERSHELL_TIMEOUT_MS = 15_000
const REQUEST_TIMEOUT_MS = 20_000
const CLOSE_TIMEOUT_MS = 30_000

type CaptureSettings = { inbox_dir: string; hotkey: string }

/** The open app's close function, if any; afterEach runs it. */
let openClose: (() => Promise<void>) | undefined

test.afterEach(async () => {
  if (openClose) await openClose()
})

function log(message: string): void {
  console.log(`[s81-e2e] ${new Date().toISOString()} ${message}`)
}

function slashes(path: string): string {
  return path.replace(/\\/g, '/')
}

function sleep(ms: number): Promise<void> {
  return new Promise((done) => setTimeout(done, ms))
}

async function api<T>(page: Page, method: string, path: string): Promise<T> {
  return page.evaluate(
    async ({ method: verb, path: route, limit }) => {
      const bridge = (window as unknown as {
        api: { getBackendUrl(): Promise<string>; getToken(): Promise<string> }
      }).api
      const base = await bridge.getBackendUrl()
      const token = await bridge.getToken()
      const response = await fetch(base + route, {
        method: verb,
        headers: { Authorization: `Bearer ${token}` },
        signal: AbortSignal.timeout(limit),
      })
      const text = await response.text()
      if (!response.ok) {
        throw new Error(`${verb} ${route} -> ${String(response.status)} ${text}`)
      }
      return JSON.parse(text) as unknown
    },
    { method, path, limit: REQUEST_TIMEOUT_MS },
  ) as Promise<T>
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
    await new Promise((done) => setTimeout(done, 250))
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
 * process this launch started, through the handle taken at launch, and waits for close to settle;
 * a main-process error that close reports still fails the test.
 */
async function closeBounded(app: ElectronApplication, child: ChildProcess): Promise<void> {
  const closing = app.close()
  let timer: ReturnType<typeof setTimeout> | undefined
  const timedOut = await Promise.race([
    closing.then(() => false),
    new Promise<boolean>((done) => {
      timer = setTimeout(() => done(true), CLOSE_TIMEOUT_MS)
    }),
  ]).finally(() => clearTimeout(timer))
  if (!timedOut) return
  log(`close did not finish in ${String(CLOSE_TIMEOUT_MS)} ms; killing this launch's Electron pid ${String(child.pid)}`)
  if (child.exitCode === null && child.signalCode === null) child.kill()
  await Promise.race([closing, sleep(10_000)])
}

test('AC-151.14 CAPTURE_SAVE_CHANGED_ONLY saving only a new inbox folder in Settings keeps the hotkey, and the Capture page shows the folder', async () => {
  test.setTimeout(240_000)
  const root = mkdtempSync(join(tmpdir(), 'avkit-e2e-s81-inbox-'))
  const appData = join(root, 'profile')
  const inbox = join(root, 'inbox')
  mkdirSync(appData, { recursive: true })
  mkdirSync(inbox, { recursive: true })
  log('inbox: launching Electron')
  const app = await launchElectron({ env: { AVKIT_APP_DATA: appData } })
  // Taken now: after close, Playwright has disposed the app object and process() throws.
  const child = app.process()
  log(`inbox: Electron pid ${String(child.pid)}`)
  let backendPid: number | null = null
  let backendStarted: string | null = null
  let closed: Promise<void> | undefined
  const close = (): Promise<void> => {
    closed ??= (async () => {
      openClose = undefined
      log('inbox: closing')
      try {
        await closeBounded(app, child)
      } finally {
        await stopRecordedBackend(backendPid, backendStarted)
      }
      log('inbox: closed')
    })()
    return closed
  }
  openClose = close
  try {
    const page = await app.firstWindow({ timeout: 60_000 })
    log('inbox: first window open; waiting for the real backend URL')
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
    log(`inbox: backend pid ${String(backendPid)} started ${String(backendStarted)}`)

    const before = await api<CaptureSettings>(page, 'GET', '/settings/capture')
    expect(before.hotkey).not.toBe('')
    expect(slashes(before.inbox_dir)).not.toBe(slashes(inbox))

    const puts: Request[] = []
    page.on('request', (request) => {
      if (request.method() === 'PUT' && request.url().includes('/settings/capture')) puts.push(request)
    })

    await page.getByTestId('nav-settings').click()
    await expect(page.getByTestId('capture-settings')).toBeVisible()
    await expect(page.getByTestId('settings-leaf-hotkey')).toHaveValue(before.hotkey, { timeout: 30_000 })
    await page.getByTestId('settings-leaf-capture-inbox_dir').fill(inbox)
    await page.getByTestId('capture-settings-save').click()

    await expect.poll(() => puts.length, { timeout: 15_000 }).toBe(1)
    const body = JSON.parse(puts[0]?.postData() ?? '{}') as Record<string, unknown>
    log(`capture PUT body keys: ${JSON.stringify(Object.keys(body))}`)
    expect(Object.keys(body)).toEqual(['inbox_dir'])
    expect(slashes(String(body.inbox_dir))).toBe(slashes(inbox))

    await expect
      .poll(async () => slashes((await api<CaptureSettings>(page, 'GET', '/settings/capture')).inbox_dir))
      .toBe(slashes(inbox))
    const after = await api<CaptureSettings>(page, 'GET', '/settings/capture')
    expect(after.hotkey).toBe(before.hotkey)
    await expect(page.getByTestId('settings-leaf-hotkey')).toHaveValue(before.hotkey)

    await page.getByTestId('nav-capture').click()
    await expect(page.getByTestId('capture-page')).toBeVisible()
    await page.getByTestId('capture-settings-toggle').click()
    await expect
      .poll(async () => slashes(await page.getByTestId('capture-inbox-path').inputValue()), { timeout: 15_000 })
      .toBe(slashes(inbox))
    await expect(page.getByTestId('capture-hotkey')).toHaveValue(before.hotkey)
    expect(puts).toHaveLength(1)
  } finally {
    await close()
  }
})

// ── MEU-165 and MEU-166 (Session 103, D-1428): the key and inbox proofs on the real backend ─────────
// Each test launches with a scratch AVKIT_APP_DATA, as AC-151.14 does, and sets the inbox by the API
// to a temp folder before Capture opens, so the catalog never lists or stores a file of the real
// Pictures folder. Main's start-up watcher may list the default folder's file names until its first
// settings read; the tests read nothing from it. The PNG files are copies of the E2E fixture.

const FIXTURE_PNG = join(dirname(fileURLToPath(import.meta.url)), 'fixtures', 'capture-region-original.png')

/** A request with a JSON body, through the page's own backend URL and token. */
async function apiSend<T>(page: Page, method: string, path: string, body: unknown): Promise<T> {
  return page.evaluate(
    async ({ method: verb, path: route, payload, limit }) => {
      const bridge = (window as unknown as {
        api: { getBackendUrl(): Promise<string>; getToken(): Promise<string> }
      }).api
      const base = await bridge.getBackendUrl()
      const token = await bridge.getToken()
      const response = await fetch(base + route, {
        method: verb,
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(limit),
      })
      const text = await response.text()
      if (!response.ok) {
        throw new Error(`${verb} ${route} -> ${String(response.status)} ${text}`)
      }
      return JSON.parse(text) as unknown
    },
    { method, path, payload: body, limit: REQUEST_TIMEOUT_MS },
  ) as Promise<T>
}

type RealBackend = { root: string; page: Page; close: () => Promise<void> }

/** The AC-151.14 launch: a scratch profile, the real backend's port, and the bounded close. */
async function launchRealBackend(label: string): Promise<RealBackend> {
  const root = mkdtempSync(join(tmpdir(), `avkit-e2e-s103-${label}-`))
  const appData = join(root, 'profile')
  mkdirSync(appData, { recursive: true })
  log(`${label}: launching Electron`)
  const app = await launchElectron({ env: { AVKIT_APP_DATA: appData } })
  const child = app.process()
  log(`${label}: Electron pid ${String(child.pid)}`)
  let backendPid: number | null = null
  let backendStarted: string | null = null
  let closed: Promise<void> | undefined
  const close = (): Promise<void> => {
    closed ??= (async () => {
      openClose = undefined
      log(`${label}: closing`)
      try {
        await closeBounded(app, child)
      } finally {
        await stopRecordedBackend(backendPid, backendStarted)
      }
      log(`${label}: closed`)
    })()
    return closed
  }
  openClose = close
  try {
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
    await expect.poll(async () => readBackendPid(appData), { timeout: 30_000 }).not.toBeNull()
    backendPid = readBackendPid(appData)
    backendStarted = backendPid === null ? null : startTime(backendPid)
    log(`${label}: backend pid ${String(backendPid)} started ${String(backendStarted)}`)
    return { root, page, close }
  } catch (error) {
    await close()
    throw error
  }
}

/** Records every `av-kit:capture:error` event the page fires from now on. */
async function recordCaptureErrors(page: Page): Promise<void> {
  await page.evaluate(() => {
    const state = window as unknown as { __s103Errors?: string[] }
    state.__s103Errors = []
    window.addEventListener('av-kit:capture:error', (event) => {
      state.__s103Errors?.push(String((event as CustomEvent<unknown>).detail))
    })
  })
}

async function captureErrors(page: Page): Promise<string[]> {
  return page.evaluate(() => (window as unknown as { __s103Errors?: string[] }).__s103Errors ?? [])
}

test('AC-165.10 a saved capture key shows in the Capture texts with no restart', async () => {
  test.setTimeout(240_000)
  const run = await launchRealBackend('key')
  try {
    const { page } = run
    const inbox = join(run.root, 'inbox')
    mkdirSync(inbox, { recursive: true })
    await apiSend(page, 'PUT', '/settings/capture', { inbox_dir: inbox })
    const before = await api<CaptureSettings>(page, 'GET', '/settings/capture')
    expect(slashes(before.inbox_dir)).toBe(slashes(inbox))
    expect(before.hotkey).toBe('F2')
    const loaded = await page.evaluate(() => performance.timeOrigin)

    await page.getByTestId('nav-capture').click()
    const capture = page.getByTestId('capture-page')
    await expect(capture).toBeVisible()
    const empty = page.getByTestId('capture-empty')
    await expect(empty).toHaveText('Press F2 or Capture region', { timeout: 15_000 })

    await page.getByTestId('capture-settings-toggle').click()
    await page.getByTestId('capture-hotkey-change').click()
    await page.getByTestId('capture-hotkey').press('F9')
    await expect(page.getByTestId('capture-hotkey')).toHaveValue('F9')
    await expect(empty, 'before Save the texts still read F2').toHaveText('Press F2 or Capture region')
    await page.getByTestId('capture-page-save').click()
    await expect
      .poll(async () => (await api<CaptureSettings>(page, 'GET', '/settings/capture')).hotkey, { timeout: 15_000 })
      .toBe('F9')

    await expect(empty, 'after Save the empty state names F9').toHaveText('Press F9 or Capture region', {
      timeout: 15_000,
    })
    const card = capture.getByTestId('help-card')
    await card.locator('button[aria-expanded]').first().click()
    await expect(card.getByTestId('help-quick-start-step').first()).toContainText('F9', { timeout: 15_000 })
    await expect(card.locator('summary', { hasText: 'When F9 is in use' })).toBeVisible({ timeout: 15_000 })

    await expect
      .poll(
        async () =>
          page.evaluate(async () =>
            (
              await (
                window as unknown as { api: { getHotkeyStatus(): Promise<{ accelerator: string }> } }
              ).api.getHotkeyStatus()
            ).accelerator,
          ),
        { timeout: 15_000, intervals: [500] },
      )
      .toBe('F9')
    const status = await page.evaluate(async () =>
      (
        window as unknown as {
          api: { getHotkeyStatus(): Promise<{ accelerator: string; registered: boolean; inUse: boolean }> }
        }
      ).api.getHotkeyStatus(),
    )
    if (status.registered) {
      log('key: main reports F9 registered; checking the key cap')
      await expect(page.getByTestId('capture-hotkey-keycap')).toHaveText('F9', { timeout: 15_000 })
    } else {
      log(`key: main reports F9 not registered (inUse=${String(status.inUse)}); checking the banner`)
      await expect(page.getByTestId('capture-hotkey-banner')).toContainText('F9 is in use', { timeout: 15_000 })
    }
    expect(await page.evaluate(() => performance.timeOrigin), 'no reload').toBe(loaded)
  } finally {
    await run.close()
  }
})

test('AC-166.7 a saved inbox change lists only the new folder', async () => {
  test.setTimeout(240_000)
  const run = await launchRealBackend('scope')
  try {
    const { page } = run
    const folderA = join(run.root, 'inbox-a')
    const folderB = join(run.root, 'inbox-b')
    mkdirSync(folderA, { recursive: true })
    mkdirSync(folderB, { recursive: true })
    const namesA = ['scope-a-1.png', 'scope-a-2.png']
    const namesB = ['scope-b-1.png']
    for (const name of namesA) copyFileSync(FIXTURE_PNG, join(folderA, name))
    for (const name of namesB) copyFileSync(FIXTURE_PNG, join(folderB, name))
    await apiSend(page, 'PUT', '/settings/capture', { inbox_dir: folderA })
    await recordCaptureErrors(page)

    await page.getByTestId('nav-capture').click()
    await expect(page.getByTestId('capture-page')).toBeVisible()
    const items = page.getByTestId('capture-filmstrip-item')
    const names = page.getByTestId('capture-filmstrip-name')
    await expect(items, 'inbox A lists its two shots').toHaveCount(2, { timeout: 15_000 })
    expect((await names.allTextContents()).sort()).toEqual(namesA)

    const saveInbox = async (folder: string): Promise<void> => {
      await page.getByTestId('capture-inbox-path').fill(folder)
      await page.getByTestId('capture-page-save').click()
      await expect
        .poll(async () => slashes((await api<CaptureSettings>(page, 'GET', '/settings/capture')).inbox_dir), {
          timeout: 15_000,
        })
        .toBe(slashes(folder))
    }
    await page.getByTestId('capture-settings-toggle').click()
    await saveInbox(folderB)
    await expect(items, 'inbox B lists only its one shot').toHaveCount(1, { timeout: 15_000 })
    await expect(names).toHaveText(namesB)
    await expect(items.first()).toHaveAttribute('aria-current', 'true')
    expect(await captureErrors(page), 'no capture error').toEqual([])
    await expect(page.getByTestId('capture-status')).not.toHaveText(/not found|error|failed/i)
    for (const name of namesA) {
      expect(existsSync(join(folderA, name)), `${name} is still on disk`).toBe(true)
    }

    await saveInbox(folderA)
    await expect(items, 'back on inbox A the two shots return').toHaveCount(2, { timeout: 15_000 })
    expect((await names.allTextContents()).sort()).toEqual(namesA)
    expect(await captureErrors(page), 'no capture error').toEqual([])
  } finally {
    await run.close()
  }
})
