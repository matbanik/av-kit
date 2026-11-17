import { expect, test, type ElectronApplication, type Page, type Request } from '@playwright/test'
import { spawnSync, type ChildProcess } from 'node:child_process'
import { existsSync, mkdirSync, mkdtempSync, readFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

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
