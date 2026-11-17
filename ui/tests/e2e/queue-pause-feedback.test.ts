import { expect, test, type ElectronApplication, type Page } from '@playwright/test'
import { spawnSync, type ChildProcess } from 'node:child_process'
import { existsSync, mkdirSync, mkdtempSync, readFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { basename, join } from 'node:path'

import { launchElectron } from './electron-app'

/**
 * MEU-155 (Session 88, D-1094): Pause after this job, Pausing… and the stop status in the real
 * app. These tests replace manual checks (Mat, 2026-11-16: "why are you giving me e2e tests
 * manually! This should be done with framework and scripts!").
 *
 * - Convert (AC-155.10, AC-155.11 and the Convert half of AC-155.15) runs against the real backend
 *   that main spawns, on clips this test makes with ffmpeg in its own temp folder. Job 1 is a
 *   re-encode Cut of a 90-second 1280x720 clip (libx265, about 28 s on the calibration PC), so
 *   there is time to click Pause and read the pending state while it runs; job 2 is a short copy
 *   Cut that must stay Pending until Resume.
 * - Downloader (AC-155.12 and the Downloader half of AC-155.15) starts the same way, then an
 *   in-page fetch seam, modelled on `download-queue.test.ts`, is installed with `addInitScript`
 *   and the window reloads, so the seam answers the page's first list read. Its pause handler
 *   counts the POST and keeps `Processing`; the test moves it to `Paused` itself. Nothing reaches
 *   the network.
 * - The Session 81 helpers are copied from `convert-queue-labels.test.ts`: scratch AVKIT_APP_DATA
 *   per launch, the backend pid recorded from `backend.json` and stopped after close only if its
 *   start time still matches, bounded child processes, requests and close, and the files dialog
 *   replaced inside main through `app.evaluate` (`__S88_PICKED__`).
 */

const PLACEHOLDER_PREFIX = 'http://127.0.0.1:9/'
const CHILD_TIMEOUT_MS = 60_000
const POWERSHELL_TIMEOUT_MS = 15_000
const REQUEST_TIMEOUT_MS = 20_000
const CLOSE_TIMEOUT_MS = 30_000

const PAUSE_LABEL = 'Pause after this job'
const PAUSE_PENDING_LABEL = 'Pausing\u2026'
const PAUSE_PENDING_STATUS = 'Queue stops when the current job ends'
const PROCESSING_LABEL = 'Processing\u2026'
const PAUSED_LABEL = 'Queue Paused'

const CONVERT = { region: 'convert-queue-region', chip: 'convert-processor' } as const
const DOWNLOAD = { region: 'download-queue-region', chip: 'processor-indicator' } as const
type QueueSurface = typeof CONVERT | typeof DOWNLOAD

type ConversionRow = { id: string; status: string }

type ConversionList = { items: ConversionRow[]; processor: { state: string; current_job_id: string | null } }

type Harness = {
  app: ElectronApplication
  page: Page
  root: string
  outDir: string
  close: () => Promise<void>
}

/** Every close function of an app that is still open; afterEach closes them. */
const live = new Set<() => Promise<void>>()

test.afterEach(async () => {
  for (const close of [...live]) await close()
})

function log(message: string): void {
  console.log(`[s88-e2e] ${new Date().toISOString()} ${message}`)
}

function slashes(path: string): string {
  return path.replace(/\\/g, '/')
}

function sleep(ms: number): Promise<void> {
  return new Promise((done) => setTimeout(done, ms))
}

/** Runs ffmpeg to make one test clip, and fails the test if it cannot. */
function makeClip(path: string, args: string[]): string {
  log(`ffmpeg: making ${basename(path)}`)
  const result = spawnSync('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', ...args, path], {
    encoding: 'utf8',
    timeout: CHILD_TIMEOUT_MS,
  })
  if (result.status !== 0 || !existsSync(path)) {
    throw new Error(`ffmpeg could not make ${path}: ${result.error?.message ?? result.stderr}`)
  }
  return path
}

/** A 4-second 320x240 clip with a keyframe on every frame, so a copy cut lands on its points. */
function shortClip(dir: string, name: string): string {
  return makeClip(join(dir, name), [
    '-f', 'lavfi', '-i', 'testsrc=size=320x240:rate=25:duration=4',
    '-f', 'lavfi', '-i', 'sine=frequency=440:duration=4',
    '-c:v', 'libx264', '-preset', 'ultrafast', '-g', '1', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-shortest',
  ])
}

/** A 90-second 1280x720@30 clip: a libx265 re-encode of it runs for about half a minute. */
function longClip(dir: string, name: string): string {
  return makeClip(join(dir, name), [
    '-f', 'lavfi', '-i', 'testsrc2=size=1280x720:rate=30:duration=90',
    '-f', 'lavfi', '-i', 'sine=frequency=330:duration=90',
    '-c:v', 'libx264', '-preset', 'ultrafast', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-shortest',
  ])
}

function probeSeconds(path: string): number {
  const result = spawnSync(
    'ffprobe',
    ['-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', path],
    { encoding: 'utf8', timeout: CHILD_TIMEOUT_MS },
  )
  if (result.status !== 0) {
    throw new Error(`ffprobe failed on ${path}: ${result.error?.message ?? result.stderr}`)
  }
  return Number.parseFloat(result.stdout.trim())
}

/** One request to the real backend from inside the page, with the page's own URL and token. */
async function api<T>(page: Page, method: string, path: string, body?: unknown): Promise<T> {
  return page.evaluate(
    async ({ method: verb, path: route, body: payload, limit }) => {
      const bridge = (window as unknown as {
        api: { getBackendUrl(): Promise<string>; getToken(): Promise<string> }
      }).api
      const base = await bridge.getBackendUrl()
      const token = await bridge.getToken()
      const response = await fetch(base + route, {
        method: verb,
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: payload === undefined ? undefined : JSON.stringify(payload),
        signal: AbortSignal.timeout(limit),
      })
      const text = await response.text()
      if (!response.ok) {
        throw new Error(`${verb} ${route} -> ${String(response.status)} ${text}`)
      }
      return (text === '' ? null : JSON.parse(text)) as unknown
    },
    { method, path, body, limit: REQUEST_TIMEOUT_MS },
  ) as Promise<T>
}

async function queue(page: Page): Promise<ConversionList> {
  return api<ConversionList>(page, 'GET', '/conversions')
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

async function launch(label: string): Promise<Harness> {
  const root = mkdtempSync(join(tmpdir(), `avkit-e2e-s88-${label}-`))
  const appData = join(root, 'profile')
  const outDir = join(root, 'out')
  mkdirSync(appData, { recursive: true })
  mkdirSync(outDir, { recursive: true })
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
    await app.evaluate(({ ipcMain }) => {
      const store = globalThis as { __S88_PICKED__?: string[] }
      store.__S88_PICKED__ = []
      ipcMain.removeHandler('show-files-dialog')
      ipcMain.handle('show-files-dialog', () => [...(store.__S88_PICKED__ ?? [])])
    })
    log(`${label}: ready`)
    return { app, page, root, outDir, close }
  } catch (error) {
    log(`${label}: launch failed (${error instanceof Error ? error.message.split('\n')[0] : String(error)}); closing`)
    await close()
    throw error
  }
}

/** Sets the converter output folder to this test's tmp folder through the backend. */
async function setOutDir(page: Page, outDir: string): Promise<void> {
  await api(page, 'PUT', '/settings/converter', { output_dir: outDir })
  const saved = await api<{ output_dir: string }>(page, 'GET', '/settings/converter')
  expect(slashes(saved.output_dir)).toBe(slashes(outDir))
  log('converter output folder set')
}

async function openConvert(page: Page): Promise<void> {
  await page.getByTestId('nav-convert').click()
  await expect(page.getByTestId('convert-page')).toBeVisible()
  await page.getByTestId('convert-task-cut').click()
  await expect(page.getByTestId('convert-cut-in')).toBeVisible()
}

/** Stages `path` through Browse and adds one Cut job for it; returns the new job's id. */
async function addCut(
  h: Harness,
  path: string,
  inText: string,
  outText: string,
  mode: 'fast' | 'reencode',
): Promise<string> {
  const before = new Set((await queue(h.page)).items.map((item) => item.id))
  await h.app.evaluate((_app, picked) => {
    ;(globalThis as { __S88_PICKED__?: string[] }).__S88_PICKED__ = picked
  }, [path])
  await h.page.getByTestId(mode === 'fast' ? 'convert-copy-fast' : 'convert-copy-reencode').click()
  await h.page.getByTestId('convert-cut-in').fill(inText)
  await h.page.getByTestId('convert-cut-out').fill(outText)
  await h.page.getByTestId('convert-browse').click()
  await expect(h.page.getByTestId('convert-add')).toHaveText('Add (1)')
  await h.page.getByTestId('convert-add').click()
  await expect(h.page.getByTestId('convert-add')).toHaveText('Add')
  await expect(h.page.getByTestId('error-banner')).toBeHidden()
  let added: string | undefined
  await expect
    .poll(async () => {
      added = (await queue(h.page)).items.find((item) => !before.has(item.id))?.id
      return added
    })
    .toBeDefined()
  await expect(row(h.page, added as string)).toBeVisible()
  log(`added ${mode} Cut ${basename(path)} ${inText}-${outText} as ${String(added)}`)
  return added as string
}

function row(page: Page, id: string) {
  return page.locator(`[data-testid="convert-queue-row"][data-job-id="${id}"]`)
}

async function start(page: Page): Promise<void> {
  await expect(page.getByTestId('queue-toolbar-start')).toBeEnabled()
  await page.getByTestId('queue-toolbar-start').click()
  log('queue started')
}

async function waitAllDone(page: Page, timeout: number): Promise<ConversionList> {
  log(`waiting up to ${String(timeout)} ms for every job to be Done`)
  let last: ConversionList | undefined
  await expect
    .poll(
      async () => {
        last = await queue(page)
        return last.items.length > 0 && last.items.every((item) => item.status === 'Done')
      },
      { timeout, intervals: [500] },
    )
    .toBe(true)
  log('every job is Done')
  return last as ConversionList
}

// --- Session 88 helpers ---------------------------------------------------------------------

/** Two Convert jobs: a long re-encode Cut that runs first and a short copy Cut behind it. */
async function twoJobs(h: Harness): Promise<{ first: string; second: string }> {
  const long = longClip(h.root, 'long.mp4')
  const seconds = probeSeconds(long)
  log(`long clip ${seconds.toFixed(3)} s`)
  expect(seconds).toBeGreaterThan(89)
  const short = shortClip(h.root, 'short.mp4')
  await setOutDir(h.page, h.outDir)
  await openConvert(h.page)
  const first = await addCut(h, long, '0', '89', 'reencode')
  const second = await addCut(h, short, '0', '1', 'fast')
  return { first, second }
}

/** Waits until the backend reports `Processing` with `id` as the current job. */
async function waitRunning(page: Page, id: string): Promise<void> {
  await expect
    .poll(
      async () => {
        const snapshot = await queue(page)
        return snapshot.processor.state === 'Processing' && snapshot.processor.current_job_id === id
      },
      { timeout: 60_000, intervals: [250] },
    )
    .toBe(true)
  log(`job ${id} is running`)
}

/** The processor state and the two jobs' statuses, as the backend reports them. */
async function jobStates(page: Page, first: string, second: string): Promise<(string | undefined)[]> {
  const snapshot = await queue(page)
  const status = new Map(snapshot.items.map((item) => [item.id, item.status]))
  return [snapshot.processor.state, status.get(first), status.get(second)]
}

type ToolbarState = { id: string | null; text: string | null; disabled: boolean | null; chip: string | null }

/** The toggle's test id, text and disabled state, and the processor chip's text (null when hidden). */
async function toolbarState(page: Page, surface: QueueSurface): Promise<ToolbarState> {
  return page.evaluate(({ region, chip }) => {
    const header = document.querySelector(`[data-testid="${region}"] [data-testid="queue-header-row"]`)
    const toggle = header?.querySelector<HTMLButtonElement>(
      '[data-testid="queue-toolbar-pause"], [data-testid="queue-toolbar-resume"]',
    )
    const chipNode = header?.querySelector<HTMLElement>(`[data-testid="${chip}"]`)
    return {
      id: toggle?.dataset.testid ?? null,
      text: toggle?.textContent?.trim() ?? null,
      disabled: toggle ? toggle.disabled : null,
      chip: !chipNode || chipNode.hidden ? null : (chipNode.textContent?.trim() ?? null),
    }
  }, surface)
}

/** Clicks Pause and waits up to `within` ms for Pausing…, disabled, and the stop status. */
async function pauseAndExpectPending(page: Page, surface: QueueSurface, within: number): Promise<void> {
  const header = page.getByTestId(surface.region).getByTestId('queue-header-row')
  const toggle = header.getByTestId('queue-toolbar-pause')
  await expect(toggle).toHaveText(PAUSE_LABEL)
  await expect(toggle).toBeEnabled()
  const clicked = Date.now()
  await toggle.click()
  await expect
    .poll(async () => toolbarState(page, surface), { timeout: within, intervals: [100] })
    .toEqual({ id: 'queue-toolbar-pause', text: PAUSE_PENDING_LABEL, disabled: true, chip: PAUSE_PENDING_STATUS })
  log(`${surface.region}: Pausing… and the stop status shown ${String(Date.now() - clicked)} ms after the click`)
}

type Geometry = {
  clearFinishedX: number
  toggleFits: boolean
  groupRight: number
  headerRight: number
  headerOverflow: boolean
  toggleInViewport: boolean
  pageScrollsSideways: boolean
}

/** Where the toolbar sits: Clear finished's x, whether the toggle's label fits, and the 700 px checks. */
async function geometry(page: Page, surface: QueueSurface): Promise<Geometry> {
  const header = page.getByTestId(surface.region).getByTestId('queue-header-row')
  await header.locator('[data-testid="queue-toolbar-pause"], [data-testid="queue-toolbar-resume"]').scrollIntoViewIfNeeded()
  return page.evaluate((region) => {
    const head = document.querySelector<HTMLElement>(`[data-testid="${region}"] [data-testid="queue-header-row"]`)
    const group = head?.querySelector<HTMLElement>('[data-testid="queue-toolbar"]')
    const toggle = head?.querySelector<HTMLElement>(
      '[data-testid="queue-toolbar-pause"], [data-testid="queue-toolbar-resume"]',
    )
    const clear = head?.querySelector<HTMLElement>('[data-testid="queue-toolbar-clear-finished"]')
    if (!head || !group || !toggle || !clear) throw new Error(`toolbar parts missing in ${region}`)
    const t = toggle.getBoundingClientRect()
    const root = document.documentElement
    return {
      clearFinishedX: clear.getBoundingClientRect().x,
      toggleFits: toggle.scrollWidth <= toggle.clientWidth,
      groupRight: group.getBoundingClientRect().right,
      headerRight: head.getBoundingClientRect().right,
      headerOverflow: head.scrollWidth > head.clientWidth,
      toggleInViewport: t.left >= 0 && t.top >= 0 && t.right <= window.innerWidth && t.bottom <= window.innerHeight,
      pageScrollsSideways: root.scrollWidth > root.clientWidth,
    }
  }, surface.region)
}

function expectSameX(label: string, xs: number[]): void {
  log(`${label}: Clear finished x in Pause after this job, Pausing… and Resume: ${JSON.stringify(xs)}`)
  expect(Math.max(...xs) - Math.min(...xs), `${label}: Clear finished moved`).toBeLessThanOrEqual(0.5)
}

const SEAM_ITEM = {
  url: 'https://example.invalid/watch?v=s88',
  video_id: 's88',
  quality: '1080p',
  audio_only: false,
  audio_format: 'default',
  progress: 0,
  speed: null,
  eta: null,
  file_size: null,
  file_path: null,
  error_message: null,
  created_at: '2026-11-17T00:00:00Z',
}

/**
 * The Downloader fetch seam, modelled on `download-queue.test.ts:171-410`: the list reads answer
 * from in-page state (dl-1 downloading, dl-2 waiting, dl-3 Done), a pause POST is counted and
 * keeps `Processing`, and every other request goes to the real backend. Installed with
 * `addInitScript` and a reload, so the page's first list read already meets it.
 */
async function installPauseSeam(page: Page): Promise<void> {
  await page.addInitScript((sample) => {
    type Item = Record<string, unknown> & { id: string; status: string }
    const seam = {
      items: [
        { ...sample, id: 'dl-1', title: 'DL-1', status: 'Downloading', progress: 42, queue_position: 1 },
        { ...sample, id: 'dl-2', title: 'DL-2', status: 'Pending', queue_position: 2 },
        {
          ...sample,
          id: 'dl-3',
          title: 'DL-3',
          status: 'Done',
          progress: 100,
          file_path: 'C:/e2e/out/dl-3.mp4',
          queue_position: 3,
        },
      ] as Item[],
      processor: { state: 'Processing', current_job_id: 'dl-1' as string | null },
      pausePosts: 0,
    }
    ;(window as unknown as { __s88Seam?: typeof seam }).__s88Seam = seam
    const original = window.fetch.bind(window)
    window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
      const method = (init?.method ?? 'GET').toUpperCase()
      const path = new URL(url).pathname
      const json = (body: unknown, status = 200) =>
        new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
      if (path.includes('/downloads/sabr')) {
        return json({ mode: 'inactive', source: null, checked_at: null })
      }
      if (path.endsWith('/downloads/pause') && method === 'POST') {
        seam.pausePosts += 1
        return new Response('', { status: 202 })
      }
      if (/\/downloads\/?$/.test(path) && method === 'GET') {
        return json({ items: seam.items, processor: seam.processor })
      }
      return original(input, init)
    }
  }, SEAM_ITEM)
  await page.reload()
  await expect(page.getByTestId('downloader-page')).toBeVisible()
  await expect(page.locator('[data-testid="queue-card"][data-job-id="dl-1"]')).toBeVisible()
  log('downloader seam installed')
}

/** The seam's pause landed: dl-1 is Done and the processor is `Paused`. */
async function seamPaused(page: Page): Promise<void> {
  await page.evaluate(() => {
    const seam = (window as unknown as {
      __s88Seam: {
        items: { id: string; status: string; progress: number; file_path: string | null }[]
        processor: { state: string; current_job_id: string | null }
      }
    }).__s88Seam
    const first = seam.items.find((item) => item.id === 'dl-1')
    if (first) {
      first.status = 'Done'
      first.progress = 100
      first.file_path = 'C:/e2e/out/dl-1.mp4'
    }
    seam.processor = { state: 'Paused', current_job_id: null }
  })
}

async function seamPausePosts(page: Page): Promise<number> {
  return page.evaluate(() => (window as unknown as { __s88Seam: { pausePosts: number } }).__s88Seam.pausePosts)
}

// --- Tests ----------------------------------------------------------------------------------

test('AC-155.10 PAUSE_PENDING_TOGGLE Convert: Pause shows Pausing… while job 1 runs, then Paused with job 2 waiting; Resume runs job 2', async () => {
  test.setTimeout(420_000)
  const h = await launch('pause')
  try {
    const { first, second } = await twoJobs(h)
    await start(h.page)
    await waitRunning(h.page, first)
    await pauseAndExpectPending(h.page, CONVERT, 2_000)
    const during = await queue(h.page)
    expect(during.processor.state, 'the backend still runs job 1 while Pausing… shows').toBe('Processing')
    expect(during.processor.current_job_id).toBe(first)

    log('waiting up to 180000 ms for job 1 Done, the processor Paused and job 2 Pending')
    await expect
      .poll(async () => jobStates(h.page, first, second), { timeout: 180_000, intervals: [500] })
      .toEqual(['Paused', 'Done', 'Pending'])
    await expect
      .poll(async () => toolbarState(h.page, CONVERT), { timeout: 15_000, intervals: [250] })
      .toEqual({ id: 'queue-toolbar-resume', text: 'Resume', disabled: false, chip: PAUSED_LABEL })

    await h.page.getByTestId(CONVERT.region).getByTestId('queue-toolbar-resume').click()
    log('resumed')
    await waitAllDone(h.page, 180_000)
  } finally {
    await h.close()
  }
})

test('AC-155.11 Cancel during Pausing… stops at once: Idle, job 1 Cancelled, job 2 Pending, the toggle back to Pause after this job', async () => {
  test.setTimeout(420_000)
  const h = await launch('cancel')
  try {
    const { first, second } = await twoJobs(h)
    await start(h.page)
    await waitRunning(h.page, first)
    await pauseAndExpectPending(h.page, CONVERT, 2_000)

    const cancel = row(h.page, first).getByTestId('queue-card-primary-action')
    await expect(cancel).toBeEnabled()
    await cancel.click()
    const confirm = h.page.getByTestId('confirm-modal-confirm')
    if ((await confirm.count()) > 0) await confirm.click()
    log('cancel clicked on job 1')

    await expect
      .poll(async () => jobStates(h.page, first, second), { timeout: 30_000, intervals: [250] })
      .toEqual(['Idle', 'Cancelled', 'Pending'])
    await expect
      .poll(async () => toolbarState(h.page, CONVERT), { timeout: 15_000, intervals: [250] })
      .toEqual({ id: 'queue-toolbar-pause', text: PAUSE_LABEL, disabled: true, chip: null })
  } finally {
    await h.close()
  }
})

test('AC-155.12 Downloader: Pausing… with the stop status and Cancel enabled, then Resume; the toolbar fits at 700 x 650 in all three states', async () => {
  test.setTimeout(240_000)
  const h = await launch('downloader')
  try {
    await installPauseSeam(h.page)
    await h.page.setViewportSize({ width: 700, height: 650 })
    const header = h.page.getByTestId(DOWNLOAD.region).getByTestId('queue-header-row')
    const fits = async (state: string): Promise<void> => {
      const g = await geometry(h.page, DOWNLOAD)
      log(`700 x 650, ${state}: ${JSON.stringify(g)}`)
      expect(g.groupRight, `${state}: toolbar right edge within the header`).toBeLessThanOrEqual(g.headerRight + 0.5)
      expect(g.headerOverflow, `${state}: header overflows`).toBe(false)
      expect(g.toggleInViewport, `${state}: toggle in the viewport`).toBe(true)
      expect(g.pageScrollsSideways, `${state}: page scrolls sideways`).toBe(false)
    }

    await expect
      .poll(async () => toolbarState(h.page, DOWNLOAD), { timeout: 15_000, intervals: [250] })
      .toEqual({ id: 'queue-toolbar-pause', text: PAUSE_LABEL, disabled: false, chip: PROCESSING_LABEL })
    await fits(PAUSE_LABEL)

    await pauseAndExpectPending(h.page, DOWNLOAD, 10_000)
    expect(await seamPausePosts(h.page), 'one pause POST').toBe(1)
    await expect(
      h.page.locator('[data-testid="queue-card"][data-job-id="dl-1"]').getByTestId('queue-card-primary-action'),
    ).toBeEnabled()
    await fits(PAUSE_PENDING_LABEL)

    await seamPaused(h.page)
    await expect
      .poll(async () => toolbarState(h.page, DOWNLOAD), { timeout: 15_000, intervals: [250] })
      .toEqual({ id: 'queue-toolbar-resume', text: 'Resume', disabled: false, chip: PAUSED_LABEL })
    await expect(header.getByTestId('queue-toolbar-resume')).toBeVisible()
    await fits('Resume')
  } finally {
    await h.close()
  }
})

test('AC-155.15 TOGGLE_WIDTH Clear finished keeps its x in Pause after this job, Pausing… and Resume, on Convert and on Downloader', async () => {
  test.setTimeout(480_000)
  const c = await launch('width-convert')
  try {
    const { first, second } = await twoJobs(c)
    await start(c.page)
    await waitRunning(c.page, first)
    const xs: number[] = []
    const read = async (state: string): Promise<void> => {
      const g = await geometry(c.page, CONVERT)
      log(`Convert, ${state}: ${JSON.stringify(g)}`)
      expect(g.toggleFits, `Convert, ${state}: the toggle label fits`).toBe(true)
      xs.push(g.clearFinishedX)
    }
    await expect
      .poll(async () => toolbarState(c.page, CONVERT), { timeout: 15_000, intervals: [250] })
      .toEqual({ id: 'queue-toolbar-pause', text: PAUSE_LABEL, disabled: false, chip: PROCESSING_LABEL })
    await read(PAUSE_LABEL)
    await pauseAndExpectPending(c.page, CONVERT, 10_000)
    await read(PAUSE_PENDING_LABEL)
    await expect
      .poll(async () => jobStates(c.page, first, second), { timeout: 180_000, intervals: [500] })
      .toEqual(['Paused', 'Done', 'Pending'])
    await expect
      .poll(async () => toolbarState(c.page, CONVERT), { timeout: 15_000, intervals: [250] })
      .toEqual({ id: 'queue-toolbar-resume', text: 'Resume', disabled: false, chip: PAUSED_LABEL })
    await read('Resume')
    expectSameX('Convert', xs)
  } finally {
    await c.close()
  }

  const d = await launch('width-downloader')
  try {
    await installPauseSeam(d.page)
    const xs: number[] = []
    const read = async (state: string): Promise<void> => {
      const g = await geometry(d.page, DOWNLOAD)
      log(`Downloader, ${state}: ${JSON.stringify(g)}`)
      expect(g.toggleFits, `Downloader, ${state}: the toggle label fits`).toBe(true)
      xs.push(g.clearFinishedX)
    }
    await expect
      .poll(async () => toolbarState(d.page, DOWNLOAD), { timeout: 15_000, intervals: [250] })
      .toEqual({ id: 'queue-toolbar-pause', text: PAUSE_LABEL, disabled: false, chip: PROCESSING_LABEL })
    await read(PAUSE_LABEL)
    await pauseAndExpectPending(d.page, DOWNLOAD, 10_000)
    await read(PAUSE_PENDING_LABEL)
    await seamPaused(d.page)
    await expect
      .poll(async () => toolbarState(d.page, DOWNLOAD), { timeout: 15_000, intervals: [250] })
      .toEqual({ id: 'queue-toolbar-resume', text: 'Resume', disabled: false, chip: PAUSED_LABEL })
    await read('Resume')
    expectSameX('Downloader', xs)
  } finally {
    await d.close()
  }
})
