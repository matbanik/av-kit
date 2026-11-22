import { expect, test, type ElectronApplication, type Locator, type Page } from '@playwright/test'
import { spawnSync, type ChildProcess } from 'node:child_process'
import { existsSync, mkdtempSync, readFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { launchElectron } from './electron-app'

/**
 * MEU-163 (Session 101, D-1354): a Paused transcript job offers Resume in its card menu.
 *
 * - AC-163.7 runs on its own fetch seam (the shape of `installTranscriptSeam` in
 *   `transcript-queue.test.ts`), installed with `addInitScript` before a reload. Its resume
 *   answers like the service: the first Paused job and the processor go to Processing, with 202.
 * - AC-163.8 runs on the real backend that main spawns. `tests/transcript_paused_fixture.py`
 *   seeds a scratch AVKIT_APP_DATA with one Paused job whose only video is already Done, so the
 *   resume compiles and zips with no network.
 *
 * In both tests the first assertion reads the card menu's item ids in order, so at Red the
 * failure is an assertion that names `resume-job-btn`, never a wait for the item. The launch
 * helpers copy `queue-cancel-paused.test.ts` (Session 89): the backend pid is read from
 * `backend.json` and stopped after close only if its start time still matches, and close is
 * bounded.
 */

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')

const PLACEHOLDER_PREFIX = 'http://127.0.0.1:9/'
const POWERSHELL_TIMEOUT_MS = 15_000
const REQUEST_TIMEOUT_MS = 20_000
const CLOSE_TIMEOUT_MS = 30_000
const FIXTURE_TIMEOUT_MS = 120_000
const DONE_TIMEOUT_MS = 30_000

type TranscriptRow = {
  id: string
  channel_name: string
  status: string
  output_dir: string
  transcripts_done: number
  zip_path: string | null
}
type TranscriptList = { items: TranscriptRow[]; processor: { state: string; current_job_id: string | null } }

type Harness = {
  app: ElectronApplication
  page: Page
  close: () => Promise<void>
}

/** Every close function of an app that is still open; afterEach closes them. */
const live = new Set<() => Promise<void>>()

test.afterEach(async () => {
  for (const close of [...live]) await close()
})

function log(message: string): void {
  console.log(`[s101-e2e] ${new Date().toISOString()} ${message}`)
}

function sleep(ms: number): Promise<void> {
  return new Promise((done) => setTimeout(done, ms))
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

/** Closes the app within CLOSE_TIMEOUT_MS, else kills the Electron process this launch started. */
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

/** Launches on `appData`, waits for the real backend and records its pid; afterEach closes it. */
async function launch(label: string, appData: string): Promise<Harness> {
  log(`${label}: launching Electron on ${appData}`)
  const app = await launchElectron({ env: { AVKIT_APP_DATA: appData } })
  // Taken now: after close, Playwright has disposed the app object and process() throws.
  const child = app.process()
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
    return { app, page, close }
  } catch (error) {
    log(`${label}: launch failed (${error instanceof Error ? error.message.split('\n')[0] : String(error)}); closing`)
    await close()
    throw error
  }
}

async function openTranscript(page: Page): Promise<void> {
  await page.getByTestId('nav-transcript').click()
  await page.getByTestId('transcript-page').waitFor()
}

function card(page: Page, name: string): Locator {
  return page.getByTestId('channel-card').filter({ hasText: name })
}

/** Opens the card's menu, waits for the menu itself, and returns its item test ids in order. */
async function menuIds(page: Page, name: string): Promise<Array<string | null>> {
  const owner = card(page, name)
  await owner.getByTestId('queue-card-kebab').click()
  const menu = owner.getByTestId('queue-card-menu')
  await menu.waitFor()
  return menu.getByRole('menuitem').evaluateAll((nodes) => nodes.map((node) => node.getAttribute('data-testid')))
}

async function closeMenu(page: Page, name: string): Promise<void> {
  await page.keyboard.press('Escape')
  await card(page, name).getByTestId('queue-card-menu').waitFor({ state: 'detached' })
}

/** AC-163.7's seam: three seeded channels, and a resume that moves the first Paused job. */
async function installResumeSeam(page: Page): Promise<void> {
  await page.addInitScript(() => {
    const state = window as unknown as {
      __e2eSeamInstalled?: boolean
      __e2eCalls?: Array<{ path: string; method: string; hasBody: boolean }>
      __e2eItems?: Array<Record<string, unknown>>
      __e2eProcessor?: { state: string; current_job_id: string | null }
    }
    const job = (id: string, name: string, status: string, position: number, done: number) => ({
      id,
      channel_url: `https://www.youtube.com/@${name.toLowerCase()}`,
      channel_name: name,
      status,
      output_dir: `C:/out/${name.toLowerCase()}`,
      video_count: 2,
      transcripts_done: done,
      word_count: done * 10,
      zip_path: null,
      last_title: null,
      last_item_status: null,
      last_item_message: null,
      queue_position: position,
      compiled_path: null,
      error_message: null,
      created_at: '2026-11-21T00:00:00Z',
      updated_at: '2026-11-21T00:00:00Z',
    })
    state.__e2eSeamInstalled = true
    state.__e2eCalls = []
    state.__e2eItems = [
      job('a', 'Alpha', 'Paused', 1, 0),
      job('b', 'Bravo', 'Paused', 2, 0),
      job('c', 'Charlie', 'Done', 3, 2),
    ]
    state.__e2eProcessor = { state: 'Idle', current_job_id: null }
    const original = window.fetch.bind(window)
    window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
      const method = (init?.method ?? 'GET').toUpperCase()
      const path = new URL(url).pathname.replace('/api/v1', '')
      const json = (body: unknown, status = 200) =>
        new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
      if (path.startsWith('/transcripts') || path.startsWith('/settings/transcript')) {
        state.__e2eCalls?.push({ path, method, hasBody: init?.body !== undefined && init.body !== null })
      }
      if (path === '/settings/transcript' && method === 'GET') {
        return json({ delay_between_requests: 120 })
      }
      if (path === '/transcripts' && method === 'GET') {
        return json({ items: state.__e2eItems ?? [], processor: state.__e2eProcessor })
      }
      if (path === '/transcripts/resume' && method === 'POST') {
        const items = state.__e2eItems ?? []
        const first = items.find((row) => row.status === 'Paused')
        if (state.__e2eProcessor?.state === 'Processing' || first === undefined) {
          return json({ error: { code: 'CONFLICT', message: 'resume_processing requires Paused' } }, 409)
        }
        state.__e2eItems = items.map((row) => (row === first ? { ...row, status: 'Processing' } : row))
        state.__e2eProcessor = { state: 'Processing', current_job_id: String(first.id) }
        return new Response('', { status: 202 })
      }
      if (path.startsWith('/transcripts') || path.startsWith('/settings/transcript')) {
        return new Response('E2E_SEAM_UNHANDLED', { status: 599 })
      }
      if (path.startsWith('/downloads/sabr')) {
        return json({ mode: 'inactive', source: null, checked_at: null })
      }
      if (path.startsWith('/settings/downloader')) {
        return json({ cookie_mode: 'none' })
      }
      if (path.startsWith('/downloads')) {
        return json({ items: [], processor: { state: 'Idle', current_job_id: null } })
      }
      return original(input, init)
    }
  })
  await page.reload()
  await page.getByTestId('downloader-page').waitFor()
}

async function seamCalls(page: Page): Promise<Array<{ path: string; method: string; hasBody: boolean }>> {
  return page.evaluate(
    () =>
      (window as unknown as { __e2eCalls?: Array<{ path: string; method: string; hasBody: boolean }> }).__e2eCalls ??
      [],
  )
}

test('AC-163.7 seam the first Paused card offers Resume, which sends one bodyless resume', async () => {
  const root = mkdtempSync(join(tmpdir(), 'avkit-e2e-s101-seam-'))
  const h = await launch('seam', join(root, 'profile'))
  const { page } = h
  await installResumeSeam(page)
  await openTranscript(page)
  await card(page, 'Charlie').waitFor()
  expect(await menuIds(page, 'Alpha')).toEqual(['resume-job-btn', 'open-folder-btn', 'remove-btn'])
  await expect(card(page, 'Alpha').getByTestId('resume-job-btn')).toHaveText('Resume')
  await closeMenu(page, 'Alpha')
  expect(await menuIds(page, 'Bravo')).toEqual(['open-folder-btn', 'remove-btn'])
  await closeMenu(page, 'Bravo')
  await card(page, 'Alpha').getByTestId('queue-card-kebab').click()
  await card(page, 'Alpha').getByTestId('resume-job-btn').click()
  await expect
    .poll(async () => (await seamCalls(page)).filter((row) => row.method === 'POST').length, { timeout: 10_000 })
    .toBe(1)
  const posts = (await seamCalls(page)).filter((row) => row.method !== 'GET')
  expect(posts).toEqual([{ path: '/transcripts/resume', method: 'POST', hasBody: false }])
  await expect(page.getByTestId('processor-indicator')).toContainText('Processing')
  await expect(card(page, 'Alpha')).toContainText('Processing')
  expect(await menuIds(page, 'Alpha')).not.toContain('resume-job-btn')
  await closeMenu(page, 'Alpha')
  expect(await menuIds(page, 'Bravo')).not.toContain('resume-job-btn')
  await closeMenu(page, 'Bravo')
  await expect(page.getByTestId('resume-btn')).toHaveCount(0)
  await h.close()
})

test('AC-163.8 real backend a Paused job resumes from its card menu to Done', async () => {
  test.setTimeout(300_000)
  const root = mkdtempSync(join(tmpdir(), 'avkit-e2e-s101-real-'))
  const appData = join(root, 'profile')
  const seeded = spawnSync('uv', ['run', '--no-sync', 'python', '-m', 'tests.transcript_paused_fixture', appData], {
    cwd: repoRoot,
    encoding: 'utf-8',
    timeout: FIXTURE_TIMEOUT_MS,
  })
  const line = /^fixture: paused job (\S+)$/m.exec(seeded.stdout ?? '')
  if (seeded.status !== 0 || line === null) {
    throw new Error(`setup: the paused fixture did not seed (exit ${String(seeded.status)}): ${seeded.stderr ?? ''}`)
  }
  const jobId = line[1]
  log(`fixture seeded job ${jobId} in ${appData}`)
  const h = await launch('real', appData)
  const { page } = h
  await openTranscript(page)
  await card(page, 'Resume Fixture').waitFor()
  expect(await menuIds(page, 'Resume Fixture')).toEqual([
    'resume-job-btn',
    'compile-btn',
    'open-folder-btn',
    'remove-btn',
  ])
  await expect(card(page, 'Resume Fixture')).toContainText('Paused')
  const before = await api<TranscriptList>(page, 'GET', '/transcripts')
  expect(before.processor.state).toBe('Idle')
  expect(before.items.map((row) => [row.id, row.status])).toEqual([[jobId, 'Paused']])
  await card(page, 'Resume Fixture').getByTestId('resume-job-btn').click()
  await expect
    .poll(
      async () => (await api<TranscriptList>(page, 'GET', '/transcripts')).items.find((row) => row.id === jobId)?.status,
      { timeout: DONE_TIMEOUT_MS, intervals: [500] },
    )
    .toBe('Done')
  const after = (await api<TranscriptList>(page, 'GET', '/transcripts')).items.find((row) => row.id === jobId)
  expect(after?.transcripts_done).toBe(1)
  expect(after?.zip_path).not.toBeNull()
  const outDir = join(appData, 'out', 'resume-fixture')
  expect(existsSync(join(outDir, 'resume-fixture_raw.zip'))).toBe(true)
  expect(existsSync(join(outDir, 'compiled', 'resume-fixture_vol1.md'))).toBe(true)
  await expect(card(page, 'Resume Fixture').getByTestId('open-zip-link')).toBeVisible()
  await h.close()
})
