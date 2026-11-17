import { expect, test, type ElectronApplication, type Page } from '@playwright/test'
import { spawnSync, type ChildProcess } from 'node:child_process'
import { createHash } from 'node:crypto'
import { existsSync, mkdirSync, mkdtempSync, readFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { basename, join } from 'node:path'

import { launchElectron } from './electron-app'

/**
 * MEU-152 (Session 81, amendment A2, D-975): the Convert queue labels and output names in the
 * real app, against the real backend that main spawns, on files this test makes with ffmpeg.
 *
 * These tests replace the manual row-5 checks HC-1, HC-2, HC-3 and HC-5 (Mat, 2026-11-16: "why
 * are you giving me e2e tests manually! This should be done with framework and scripts!").
 *
 * - Profile: AVKIT_APP_DATA is a new folder under tmpdir() for every launch, and the converter
 *   output folder is a tmp folder set before the first Add. Nothing reads or writes the normal
 *   profile, database or settings.
 * - Backend: main publishes the port-9 placeholder first and the real backend's port once it
 *   prints AVKIT_READY. The renderer reads the URL on every request, so each test waits for the
 *   real port before it acts. Direct reads use the same URL and token from inside the page.
 * - Files dialog: in an E2E run main's dialog stub always returns `C:/e2e/sample.mp4`. This test
 *   replaces that one IPC handler, inside main through `app.evaluate`, with one that returns the
 *   paths in `globalThis.__S81_PICKED__`. Product code is unchanged; Browse then stages the real
 *   fixture through the page's own picker path.
 * - Backend process: in an E2E run main does not stop its backend on quit. Each test records the
 *   backend pid from `backend.json` in its own scratch profile, and after close stops that pid
 *   only if it is still running with the start time recorded at launch.
 * - Bounded waits: every child process (ffmpeg, ffprobe, powershell), every backend request and
 *   the app close has its own time limit, and each step prints a timed `[s81-e2e]` line, so a slow
 *   machine fails at a named step instead of at the test timeout. If close does not finish, the
 *   Electron process this launch started is killed through its own handle. An afterEach closes
 *   any app a timed-out test left open.
 */

const PLACEHOLDER_PREFIX = 'http://127.0.0.1:9/'
const CHILD_TIMEOUT_MS = 60_000
const POWERSHELL_TIMEOUT_MS = 15_000
const REQUEST_TIMEOUT_MS = 20_000
const CLOSE_TIMEOUT_MS = 30_000
const ENCODER_TOKEN =
  /\b(?:lib(?:x264|x265|svtav1|aom-av1|vpx(?:-vp9)?)|[a-z0-9]+_(?:nvenc|amf|qsv|vaapi|videotoolbox|vulkan|mf))\b/i

type ConversionRow = {
  id: string
  kind: string
  status: string
  output_path: string
  gpu_encoder: string | null
  in_ms: number | null
  out_ms: number | null
}

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
  console.log(`[s81-e2e] ${new Date().toISOString()} ${message}`)
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

/** A 15-second 1280x720 clip: a software re-encode of it runs for several seconds. */
function longClip(dir: string, name: string): string {
  return makeClip(join(dir, name), [
    '-f', 'lavfi', '-i', 'testsrc2=size=1280x720:rate=30:duration=15',
    '-f', 'lavfi', '-i', 'sine=frequency=330:duration=15',
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

function sha256(path: string): string {
  return createHash('sha256').update(readFileSync(path)).digest('hex')
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
  const root = mkdtempSync(join(tmpdir(), `avkit-e2e-s81-${label}-`))
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
      const store = globalThis as { __S81_PICKED__?: string[] }
      store.__S81_PICKED__ = []
      ipcMain.removeHandler('show-files-dialog')
      ipcMain.handle('show-files-dialog', () => [...(store.__S81_PICKED__ ?? [])])
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
async function useOutDir(page: Page, outDir: string): Promise<void> {
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
    ;(globalThis as { __S81_PICKED__?: string[] }).__S81_PICKED__ = picked
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

function meta(page: Page, id: string) {
  return row(page, id).getByTestId('queue-card-meta')
}

async function positionsInOrder(page: Page): Promise<{ id: string; position: string }[]> {
  return page.locator('[data-testid="convert-queue-row"]').evaluateAll((rows) =>
    rows.map((node) => ({
      id: node.getAttribute('data-job-id') ?? '',
      position: node.querySelector('[data-testid="queue-card-position"]')?.textContent?.trim() ?? '',
    })),
  )
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

test('AC-152.21 CONVERT_TIMECODE a Cut card shows its segment as HH:MM:SS.mmm–HH:MM:SS.mmm, waiting and Done', async () => {
  test.setTimeout(240_000)
  const h = await launch('timecode')
  try {
    const clip = shortClip(h.root, 'timecode.mp4')
    await useOutDir(h.page, h.outDir)
    await openConvert(h.page)
    const id = await addCut(h, clip, '00:00:01.000', '00:00:02.500', 'fast')
    await expect(meta(h.page, id)).toContainText('00:00:01.000–00:00:02.500')
    await expect(meta(h.page, id)).toContainText('Waiting - next')
    await start(h.page)
    await waitAllDone(h.page, 60_000)
    await expect(meta(h.page, id)).toContainText('00:00:01.000–00:00:02.500', { timeout: 15_000 })
    await expect(meta(h.page, id)).not.toContainText('Waiting')
  } finally {
    await h.close()
  }
})

test('AC-152.22 QUEUE_ROW_NUMBER and WAITING_POSITION the cards read 1..n and the waiting texts move up after a remove and a finish', async () => {
  test.setTimeout(300_000)
  const h = await launch('positions')
  try {
    const fast = shortClip(h.root, 'fast.mp4')
    const slow = longClip(h.root, 'slow.mp4')
    await useOutDir(h.page, h.outDir)
    await openConvert(h.page)
    const a = await addCut(h, fast, '0', '1', 'fast')
    const b = await addCut(h, slow, '0', '15', 'reencode')
    const x = await addCut(h, fast, '1', '2', 'fast')
    const c = await addCut(h, fast, '2', '3', 'fast')

    await expect
      .poll(async () => positionsInOrder(h.page))
      .toEqual([
        { id: a, position: '1' },
        { id: b, position: '2' },
        { id: x, position: '3' },
        { id: c, position: '4' },
      ])
    await expect(meta(h.page, a)).toContainText('Waiting - next')
    await expect(meta(h.page, b)).toContainText('Waiting - 2 in line')
    await expect(meta(h.page, x)).toContainText('Waiting - 3 in line')
    await expect(meta(h.page, c)).toContainText('Waiting - 4 in line')

    // Remove X (a waiting job): A is still next, C moves up to 3 in line and the cards renumber 1..3.
    await row(h.page, x).getByTestId('queue-card-kebab').click()
    await expect(h.page.getByTestId('queue-card-menu')).toBeVisible()
    await h.page.getByTestId('queue-card-menu').locator('[data-menu-action="remove"]').click()
    await h.page.getByTestId('confirm-modal-confirm').click()
    await expect(row(h.page, x)).toHaveCount(0)
    await expect
      .poll(async () => positionsInOrder(h.page))
      .toEqual([
        { id: a, position: '1' },
        { id: b, position: '2' },
        { id: c, position: '3' },
      ])
    await expect(meta(h.page, a)).toContainText('Waiting - next')
    await expect(meta(h.page, b)).toContainText('Waiting - 2 in line')
    await expect(meta(h.page, c)).toContainText('Waiting - 3 in line')

    // Start: once A is Done and B is running, C is the next waiting job and the rows stay 1..3.
    await start(h.page)
    await expect
      .poll(
        async () => {
          const snapshot = await queue(h.page)
          const status = new Map(snapshot.items.map((item) => [item.id, item.status]))
          return [status.get(a), status.get(b), status.get(c)]
        },
        { timeout: 60_000, intervals: [250] },
      )
      .toEqual(['Done', 'Processing', 'Pending'])
    await expect(meta(h.page, c)).toContainText('Waiting - next', { timeout: 10_000 })
    await expect(meta(h.page, a)).not.toContainText('Waiting')
    expect(await positionsInOrder(h.page)).toEqual([
      { id: a, position: '1' },
      { id: b, position: '2' },
      { id: c, position: '3' },
    ])
    const stillRunning = await queue(h.page)
    expect(stillRunning.items.find((item) => item.id === b)?.status).toBe('Processing')

    await waitAllDone(h.page, 180_000)
    for (const id of [a, b, c]) {
      await expect(meta(h.page, id)).not.toContainText('Waiting', { timeout: 15_000 })
    }
  } finally {
    await h.close()
  }
})

test('AC-152.23 CUT_NO_GPU_ENCODER a Fast copy Cut card never shows an encoder, running or Done; a re-encode Cut shows libx265', async () => {
  test.setTimeout(240_000)
  const h = await launch('encoder')
  try {
    const clip = shortClip(h.root, 'encoder.mp4')
    await useOutDir(h.page, h.outDir)
    await openConvert(h.page)
    const copy = await addCut(h, clip, '0', '3', 'fast')
    const reencode = await addCut(h, clip, '0', '2', 'reencode')

    // Record every text the Fast copy card's meta shows from here on, across re-renders.
    await h.page.evaluate((id) => {
      const seen: string[] = []
      ;(window as unknown as { __s81Seen?: string[] }).__s81Seen = seen
      const read = (): void => {
        const node = document.querySelector(
          `[data-testid="convert-queue-row"][data-job-id="${id}"] [data-testid="queue-card-meta"]`,
        )
        const text = node?.textContent ?? ''
        if (text !== '' && seen[seen.length - 1] !== text) seen.push(text)
      }
      read()
      const region = document.querySelector('[data-testid="convert-queue-region"]') ?? document.body
      new MutationObserver(read).observe(region, { subtree: true, childList: true, characterData: true })
    }, copy)

    await start(h.page)
    const done = await waitAllDone(h.page, 90_000)
    await expect(meta(h.page, reencode)).toContainText('libx265', { timeout: 15_000 })
    await expect(meta(h.page, copy)).not.toContainText('Waiting', { timeout: 15_000 })

    const seen = await h.page.evaluate(() => (window as unknown as { __s81Seen?: string[] }).__s81Seen ?? [])
    log(`Fast copy card meta texts seen: ${JSON.stringify(seen)}`)
    expect(seen.length).toBeGreaterThan(1)
    expect(seen.filter((text) => ENCODER_TOKEN.test(text))).toEqual([])
    expect(await meta(h.page, copy).textContent()).not.toMatch(ENCODER_TOKEN)
    const rows = new Map(done.items.map((item) => [item.id, item]))
    expect(rows.get(copy)?.gpu_encoder).toBeNull()
    expect(rows.get(reencode)?.gpu_encoder).toBe('libx265')
  } finally {
    await h.close()
  }
})

test('AC-152.24 QUEUE_OUTPUT_RESERVED two Adds of one video as Cut give <stem>_cut.mp4 and <stem>_cut_1.mp4, both kept', async () => {
  test.setTimeout(240_000)
  const h = await launch('names')
  try {
    const clip = shortClip(h.root, 'twice.mp4')
    await openConvert(h.page)
    // The output folder is set the way a person sets it: the page's field, then Save.
    await h.page.getByTestId('convert-output-dir').fill(h.outDir)
    await h.page.getByTestId('convert-page-save').click()
    await expect
      .poll(async () => slashes((await api<{ output_dir: string }>(h.page, 'GET', '/settings/converter')).output_dir))
      .toBe(slashes(h.outDir))

    const first = await addCut(h, clip, '0', '1', 'fast')
    const second = await addCut(h, clip, '1', '3', 'fast')
    const waiting = new Map((await queue(h.page)).items.map((item) => [item.id, item]))
    const firstPath = waiting.get(first)?.output_path ?? ''
    const secondPath = waiting.get(second)?.output_path ?? ''
    expect(slashes(firstPath)).toBe(slashes(join(h.outDir, 'twice_cut.mp4')))
    expect(slashes(secondPath)).toBe(slashes(join(h.outDir, 'twice_cut_1.mp4')))

    await start(h.page)
    await waitAllDone(h.page, 90_000)
    for (const [id, path] of [
      [first, firstPath],
      [second, secondPath],
    ] as const) {
      const open = row(h.page, id).getByTestId('queue-card-primary-action')
      await expect(open).toHaveText('Open file', { timeout: 15_000 })
      expect(slashes((await open.getAttribute('title')) ?? '')).toBe(slashes(path))
    }

    expect(existsSync(firstPath)).toBe(true)
    expect(existsSync(secondPath)).toBe(true)
    const firstSeconds = probeSeconds(firstPath)
    const secondSeconds = probeSeconds(secondPath)
    log(`${basename(firstPath)} ${firstSeconds.toFixed(3)} s, ${basename(secondPath)} ${secondSeconds.toFixed(3)} s`)
    expect(Math.abs(firstSeconds - 1)).toBeLessThan(0.35)
    expect(Math.abs(secondSeconds - 2)).toBeLessThan(0.35)
    expect(sha256(firstPath)).not.toBe(sha256(secondPath))
  } finally {
    await h.close()
  }
})
