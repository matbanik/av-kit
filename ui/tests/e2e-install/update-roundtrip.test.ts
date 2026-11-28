// The install stage's spec (Session 106, HOST_PAYLOAD, INSTALL_STAGE_RULES, ROUND_TRIP). It runs on
// the remote E2E host only, with AVKIT_E2E_PAYLOAD_DIR set by run-e2e.ps1. The test list is built
// from payload.json: a `canary` payload declares the one test AC-174.18 (install silently, show
// the main window, uninstall, and leave the account as it found it); a `roundtrip` payload
// declares AC-174.19 (steps 1 to 7 of ROUND_TRIP, step 4 the negative) and AC-174.20 (step 8), in
// that order in one serial block. Nothing is skipped or retried.
import { execFileSync, spawn, spawnSync, type ChildProcess } from 'node:child_process'
import { createHash, randomBytes } from 'node:crypto'
import { createReadStream, existsSync, readFileSync, statSync, writeFileSync } from 'node:fs'
import { createServer as createHttpServer, type Server } from 'node:http'
import { createServer } from 'node:net'
import { join } from 'node:path'

import { _electron, chromium, expect, test, type Page } from '@playwright/test'

import {
  APP_ID,
  APPROVED_KEY,
  INSTALLER_KEY,
  PRODUCT,
  RUN_KEY,
  accountPaths,
  alive,
  appEnv,
  checkPreconditions,
  install,
  pidsUnder,
  readPayload,
  realHost,
  runFolders,
  snapshot,
  snapshotDiff,
  startApp,
  startDecoy,
  stopUnder,
  uninstall,
  waitFor,
  writeOwner,
  type Payload,
  type RunFolders,
  type Snapshot,
} from './install-helper'

/** The feed port the stage reserves when the payload names none. */
const DEFAULT_FEED_PORT = 47911

/** The installed app under Playwright: its first window, its pid, its stdout, a way to stop it. */
interface Running {
  pid: number | undefined
  window(): Promise<Page>
  output(): string
  close(): Promise<void>
}

function freePort(): Promise<number> {
  return new Promise((resolve, reject) => {
    const srv = createServer()
    srv.once('error', reject)
    srv.listen(0, '127.0.0.1', () => {
      const addr = srv.address()
      const port = typeof addr === 'object' && addr !== null ? addr.port : 0
      srv.close(() => resolve(port))
    })
  })
}

/** Collects a child's stdout (D-1575: the updater's lines reach the main process's stdout). */
function collect(child: ChildProcess): () => string {
  const chunks: string[] = []
  child.stdout?.on('data', (b: Buffer) => chunks.push(b.toString('utf8')))
  child.stderr?.on('data', () => undefined)
  return () => chunks.join('')
}

const launchers = {
  async electron(exe: string, env: Record<string, string>): Promise<Running> {
    const app = await _electron.launch({ executablePath: exe, args: [], env, timeout: 120_000 })
    const output = collect(app.process())
    return {
      pid: app.process().pid,
      window: () => app.firstWindow({ timeout: 120_000 }),
      output,
      close: () => app.close(),
    }
  },
  async cdp(exe: string, env: Record<string, string>): Promise<Running> {
    const port = await freePort()
    const child = spawn(exe, [`--remote-debugging-port=${port}`], { env, stdio: ['ignore', 'pipe', 'pipe'], windowsHide: false })
    child.on('error', () => undefined)
    const output = collect(child)
    let browser: Awaited<ReturnType<typeof chromium.connectOverCDP>> | undefined
    const deadline = Date.now() + 120_000
    while (browser === undefined) {
      try {
        browser = await chromium.connectOverCDP(`http://127.0.0.1:${port}`)
      } catch (e) {
        if (Date.now() > deadline || child.exitCode !== null) throw e
        await new Promise((r) => setTimeout(r, 1_000))
      }
    }
    const connected = browser
    return {
      pid: child.pid,
      async window() {
        const end = Date.now() + 120_000
        for (;;) {
          const pages = connected.contexts().flatMap((c) => c.pages())
          if (pages.length > 0) return pages[0]
          if (Date.now() > end) throw new Error('no page over CDP after 120 s')
          await new Promise((r) => setTimeout(r, 500))
        }
      },
      output,
      close: () => connected.close(),
    }
  },
}

async function mainWindowShows(page: Page): Promise<void> {
  // No waitForLoadState: on the host it missed the first window's domcontentloaded (it logged
  // only networkidle) and hung for 30 s; the main suite never waits on it (D-1578).
  await expect(page.locator('#root')).toBeVisible({ timeout: 120_000 })
  await expect.poll(() => page.locator('#root > *').count(), { timeout: 120_000 }).toBeGreaterThan(0)
}

/**
 * The teardown of INSTALL_STAGE_RULES: stop what runs from the install folder, uninstall, stop the
 * decoy by its pid, remove the data folders this run created, and compare the snapshots. The
 * owner record is deleted only when they are equal. It returns the problems it found.
 */
async function teardown(run: RunFolders, before: Snapshot, decoyPid: number | undefined, owner: string): Promise<string[]> {
  const host = realHost()
  const paths = accountPaths(run.root)
  const problems: string[] = []
  stopUnder(run.installDir)
  if (!(await waitFor(() => pidsUnder(run.installDir).length === 0, 60_000))) {
    problems.push(`processes still run from ${run.installDir}`)
  }
  try {
    await uninstall(host, run)
  } catch (e) {
    problems.push(String(e))
  }
  if (!alive(decoyPid)) problems.push('the sibling decoy is not alive after the uninstaller call')
  if (decoyPid !== undefined && alive(decoyPid)) {
    try {
      process.kill(decoyPid)
    } catch {
      problems.push('the decoy could not be stopped by its pid')
    }
  }
  for (const [folder, was] of Object.entries(before.folders)) {
    if (!was && existsSync(folder)) host.remove(folder)
  }
  const diff = snapshotDiff(before, snapshot(host, paths))
  if (diff.length === 0) {
    host.remove(owner)
  } else {
    problems.push(`the account differs from its before snapshot; ${owner} is kept: ${diff.join('; ')}`)
  }
  return problems
}

async function canary(payload: Payload, payloadDir: string): Promise<void> {
  const run = runFolders(payloadDir)
  const host = realHost()
  const paths = accountPaths(run.root)
  const installer = join(payloadDir, String(payload.installer ?? ''))
  expect(existsSync(installer), `the payload's installer ${installer}`).toBe(true)
  const pre = await checkPreconditions(host, paths, { port: payload.feed_port ?? DEFAULT_FEED_PORT })
  expect(pre, 'INSTALL_STAGE_RULES preconditions').toEqual({ ok: true })
  const before = snapshot(host, paths)
  // The owner record comes before the first change to the account.
  const owner = writeOwner(host, run, before, null)
  const decoy = startDecoy(run)
  writeOwner(host, run, before, decoy.pid ?? null)
  let failure: unknown
  try {
    expect(await waitFor(() => alive(decoy.pid), 10_000), 'the sibling decoy starts').toBe(true)
    await install(host, installer, run)
    expect(alive(decoy.pid), 'the sibling decoy is alive after the installer call').toBe(true)
    expect(host.regKeyExists(INSTALLER_KEY), `the installer's key ${INSTALLER_KEY} (APP_GUID)`).toBe(true)
    const exe = join(run.installDir, `${PRODUCT}.exe`)
    expect(existsSync(exe), `the installed ${exe}`).toBe(true)
    const { app, via } = await startApp(exe, launchers)
    test.info().annotations.push({ type: 'start', description: via })
    try {
      await mainWindowShows(await app.window())
    } finally {
      await app.close().catch(() => undefined)
    }
  } catch (e) {
    failure = e
  }
  const problems = await teardown(run, before, decoy.pid, owner)
  if (failure !== undefined) throw failure
  expect(problems, 'the teardown leaves the account as it found it').toEqual([])
}

// --- ROUND_TRIP --------------------------------------------------------------------------------

/** The roundtrip payload's own fields (build-update.ps1 -Mode pair writes them). */
interface RoundTrip {
  old_installer: string
  new_installer: string
  old_version: string
  new_version: string
  feed: { latest: string; bad: string; blockmap: string }
  feed_port: number
}

function roundTripOf(payload: Payload): RoundTrip {
  const feed = (payload.feed ?? {}) as Record<string, unknown>
  return {
    old_installer: String(payload.old_installer ?? ''),
    new_installer: String(payload.new_installer ?? ''),
    old_version: String(payload.old_version ?? ''),
    new_version: String(payload.new_version ?? ''),
    feed: { latest: String(feed.latest ?? ''), bad: String(feed.bad ?? ''), blockmap: String(feed.blockmap ?? '') },
    feed_port: Number(payload.feed_port ?? DEFAULT_FEED_PORT),
  }
}

type FeedMode = 'off' | 'bad' | 'good'

/** The local generic feed on 127.0.0.1: `off` answers 404, `bad` serves latest-bad.yml. */
interface Feed {
  mode: FeedMode
  requests: string[]
  close(): Promise<void>
}

function serveFeed(dir: string, rt: RoundTrip): Promise<Feed> {
  const files: Record<string, string> = {
    [`/${rt.new_installer}`]: join(dir, rt.new_installer),
    [`/${rt.feed.blockmap}`]: join(dir, rt.feed.blockmap),
  }
  const feed: Feed = { mode: 'off', requests: [], close: () => Promise.resolve() }
  const server: Server = createHttpServer((req, res) => {
    const path = decodeURIComponent(new URL(req.url ?? '/', 'http://127.0.0.1').pathname)
    feed.requests.push(`${feed.mode} ${req.method ?? ''} ${path}`)
    let file: string | undefined
    if (feed.mode !== 'off') {
      file = path === '/latest.yml' ? join(dir, feed.mode === 'bad' ? rt.feed.bad : rt.feed.latest) : files[path]
    }
    if (file === undefined || !existsSync(file)) {
      res.writeHead(404)
      res.end()
      return
    }
    res.writeHead(200, { 'Content-Length': String(statSync(file).size), 'Content-Type': 'application/octet-stream' })
    createReadStream(file).pipe(res)
  })
  return new Promise((resolve, reject) => {
    server.once('error', reject)
    server.listen(rt.feed_port, '127.0.0.1', () => {
      feed.close = () =>
        new Promise((r) => {
          server.closeAllConnections()
          server.close(() => r())
        })
      resolve(feed)
    })
  })
}

function ps(command: string): string {
  try {
    return execFileSync('powershell.exe', ['-NoProfile', '-NonInteractive', '-Command', command], {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'ignore'],
      windowsHide: true,
    }).trim()
  } catch {
    return ''
  }
}

/** The installed exe's product version ('' while the installer holds the file). */
function exeVersion(exe: string): string {
  const v = ps(`(Get-Item -LiteralPath '${exe.replace(/'/g, "''")}').VersionInfo.ProductVersion`)
  return v.replace(/^(\d+\.\d+\.\d+)\.0$/, '$1')
}

/** The pids whose image is exactly this exe. */
function exePids(exe: string): number[] {
  const want = exe.toLowerCase()
  return ps("Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath } | ForEach-Object { '' + $_.ProcessId + '|' + $_.ExecutablePath }")
    .split(/\r?\n/)
    .map((ln) => ln.split('|'))
    .filter(([, path]) => typeof path === 'string' && path.trim().toLowerCase() === want)
    .map(([pid]) => Number(pid))
    .filter((n) => Number.isInteger(n) && n > 0)
}

interface Descriptor {
  pid: number
  api_base: string
}

function readDescriptor(appData: string): Descriptor | null {
  try {
    const d = JSON.parse(readFileSync(join(appData, 'backend.json'), 'utf8').replace(/^\uFEFF/, '')) as Partial<Descriptor>
    return typeof d.pid === 'number' && typeof d.api_base === 'string' ? { pid: d.pid, api_base: d.api_base } : null
  } catch {
    return null
  }
}

async function healthOk(apiBase: string): Promise<boolean> {
  try {
    const r = await fetch(`${apiBase}/health`, { signal: AbortSignal.timeout(5_000) })
    const body = (await r.json()) as { status?: unknown }
    return r.ok && body.status === 'ok'
  } catch {
    return false
  }
}

/** A descriptor whose backend is alive and answers its health route, or null after `ms`. */
async function liveBackend(appData: string, ms: number, not?: number): Promise<Descriptor | null> {
  const end = Date.now() + ms
  while (Date.now() < end) {
    const d = readDescriptor(appData)
    if (d !== null && d.pid !== not && alive(d.pid) && (await healthOk(d.api_base))) return d
    await new Promise((r) => setTimeout(r, 1_000))
  }
  return null
}

/** `app.update_interval` from avkit.db, read by the installed exe's own Node (node:sqlite). */
function storedInterval(exe: string, appData: string, runDir: string): string {
  const script = join(runDir, 'read-interval.mjs')
  writeFileSync(
    script,
    [
      "import { DatabaseSync } from 'node:sqlite'",
      'const db = new DatabaseSync(process.argv[2], { readOnly: true })',
      "const row = db.prepare('SELECT value FROM settings WHERE namespace = ? AND key = ?').get('app', 'update_interval')",
      "process.stdout.write(row === undefined ? '' : String(row.value))",
      '',
    ].join('\n'),
    'utf8',
  )
  const r = spawnSync(exe, [script, join(appData, 'avkit.db')], {
    env: { ...appEnv(), ELECTRON_RUN_AS_NODE: '1' },
    encoding: 'utf8',
    windowsHide: true,
    timeout: 30_000,
  })
  return String(r.stdout ?? '').trim().replace(/^"(.*)"$/, '$1')
}

function sha256(path: string): string {
  return createHash('sha256').update(readFileSync(path)).digest('hex')
}

/** What AC-174.19 leaves for AC-174.20 and for the stage's teardown. */
interface RoundTripState {
  run: RunFolders
  before: Snapshot
  owner: string
  decoy: ChildProcess
  feed?: Feed
  mcp?: ChildProcess
  app?: Running
  tornDown: boolean
}

let rts: RoundTripState | undefined

async function roundTripUpdate(payload: Payload, payloadDir: string): Promise<void> {
  const rt = roundTripOf(payload)
  const run = runFolders(payloadDir)
  const host = realHost()
  const paths = accountPaths(run.root)
  const appData = join(paths.localAppData, PRODUCT)
  const oldInstaller = join(payloadDir, rt.old_installer)
  for (const f of [rt.old_installer, rt.new_installer, rt.feed.latest, rt.feed.bad, rt.feed.blockmap]) {
    expect(f !== '' && existsSync(join(payloadDir, f)), `the payload's ${f || '(unnamed file)'}`).toBe(true)
  }
  const pre = await checkPreconditions(host, paths, { port: rt.feed_port })
  expect(pre, 'INSTALL_STAGE_RULES preconditions').toEqual({ ok: true })
  const before = snapshot(host, paths)
  const owner = writeOwner(host, run, before, null)
  const decoy = startDecoy(run)
  writeOwner(host, run, before, decoy.pid ?? null)
  const state: RoundTripState = { run, before, owner, decoy, tornDown: false }
  rts = state
  expect(await waitFor(() => alive(decoy.pid), 10_000), 'the sibling decoy starts').toBe(true)
  state.feed = await serveFeed(payloadDir, rt)
  const feed = state.feed

  // (1) the old build, installed and started.
  await install(host, oldInstaller, run)
  const exe = join(run.installDir, `${PRODUCT}.exe`)
  expect(existsSync(exe), `the installed ${exe}`).toBe(true)
  expect(exeVersion(exe), 'the installed exe is the old version').toBe(rt.old_version)
  const { app, via } = await startApp(exe, launchers)
  state.app = app
  test.info().annotations.push({ type: 'start', description: via })
  const page = await app.window()
  await mainWindowShows(page)

  // (2) an MCP server started as a client starts it, and the three pids.
  const backend = await liveBackend(appData, 180_000)
  expect(backend, `a live backend in ${appData}\\backend.json`).not.toBeNull()
  const serverEntry = join(run.installDir, 'resources', 'mcp-server', 'index.mjs')
  expect(existsSync(serverEntry), `the packaged MCP server ${serverEntry}`).toBe(true)
  const mcp = spawn(exe, [serverEntry], {
    env: { ...appEnv(), ELECTRON_RUN_AS_NODE: '1', AVKIT_APP_DATA: appData },
    stdio: ['pipe', 'pipe', 'pipe'],
    windowsHide: true,
  })
  mcp.on('error', () => undefined)
  collect(mcp)
  state.mcp = mcp
  await new Promise((r) => setTimeout(r, 3_000))
  expect(mcp.exitCode, 'the MCP server is still running').toBeNull()
  const pids = { app: app.pid, backend: backend?.pid, mcp: mcp.pid }
  test.info().annotations.push({ type: 'pids', description: JSON.stringify(pids) })
  expect(Object.values(pids).every((p) => typeof p === 'number' && alive(p)), `the three pids ${JSON.stringify(pids)}`).toBe(true)

  // (3) the setting, Start at sign-in and the marker file.
  await page.getByTestId('nav-settings').click()
  await page.getByTestId('settings-page').waitFor()
  await expect(page.getByTestId('updates-settings')).toBeVisible()
  await page.getByTestId('settings-leaf-update_interval').selectOption('monthly')
  await expect.poll(() => storedInterval(exe, appData, run.runDir), { timeout: 60_000 }).toBe('monthly')
  const signIn = page.getByTestId('start-at-sign-in-checkbox')
  // A controlled checkbox: it turns checked when loginItemSet answers, after the click, so
  // check()'s own state test fails; click, then wait for the answer (D-1579).
  await expect(signIn).not.toBeChecked()
  await signIn.click()
  await expect(signIn).toBeChecked({ timeout: 30_000 })
  expect(await waitFor(() => host.regValueExists(RUN_KEY, APP_ID), 30_000), `the Run value ${APP_ID}`).toBe(true)
  const marker = join(appData, 's106-marker.bin')
  writeFileSync(marker, randomBytes(4096))
  const markerSha = sha256(marker)

  // (4) the negative: a feed whose SHA-512 is wrong installs nothing.
  const status = page.getByTestId('settings-update-status')
  const check = page.getByTestId('settings-update-check')
  feed.mode = 'bad'
  await expect(check).toBeEnabled({ timeout: 120_000 })
  await check.click()
  await expect(status).toContainText('Could not check for updates (checksum)', { timeout: 600_000 })
  expect(exeVersion(exe), 'the installed exe after the wrong SHA-512').toBe(rt.old_version)
  await expect(page.getByTestId('settings-update-restart')).toHaveCount(0)

  // (5) the true feed, the check and the restart.
  feed.mode = 'good'
  await expect(check).toBeEnabled({ timeout: 120_000 })
  await check.click()
  await expect(status).toContainText(`Version ${rt.new_version} is ready to install`, { timeout: 600_000 })
  try {
    await page.getByTestId('settings-update-restart').click({ noWaitAfter: true })
  } catch (e) {
    // The window may close while the click returns; step (6) proves whether it took effect.
    test.info().annotations.push({ type: 'restart-click', description: String(e).split('\n')[0] })
  }

  // (6) at the first read of the new version, none of the three pids is alive.
  let seen: Record<string, boolean> | undefined
  const end = Date.now() + 600_000
  while (Date.now() < end) {
    if (exeVersion(exe) === rt.new_version) {
      seen = { app: alive(pids.app), backend: alive(pids.backend), mcp: alive(pids.mcp) }
      break
    }
    await new Promise((r) => setTimeout(r, 250))
  }
  expect(seen, `the installed exe reads ${rt.new_version} within 600 s`).toBeDefined()
  expect(seen, 'the old app, its backend and the MCP server at the first new-version read').toEqual({ app: false, backend: false, mcp: false })

  // (7) the new version runs, and what the user had is kept.
  expect(await waitFor(() => exePids(exe).some((p) => p !== pids.app), 180_000), `a running ${exe}`).toBe(true)
  expect(exeVersion(exe), 'the installed exe file version').toBe(rt.new_version)
  const next = await liveBackend(appData, 180_000, pids.backend)
  expect(next, 'a new backend pid from the descriptor whose health answers ok').not.toBeNull()
  expect(host.regValueExists(RUN_KEY, APP_ID), `the Run value ${APP_ID} after the update`).toBe(true)
  expect(alive(decoy.pid), 'the sibling decoy is alive after the update').toBe(true)
  expect(storedInterval(exe, appData, run.runDir), 'app.update_interval after the update').toBe('monthly')
  expect(sha256(marker), 'the marker file after the update').toBe(markerSha)
  const lines = app.output().split(/\r?\n/)
  const requested = lines.findIndex((l) => l.startsWith('update: install requested'))
  const stopped = lines.indexOf('update: backend stopped')
  test.info().annotations.push({ type: 'feed', description: feed.requests.slice(0, 40).join(', ') })
  expect(requested, 'the main log holds update: install requested').toBeGreaterThanOrEqual(0)
  expect(stopped, 'the main log holds update: backend stopped after the install request').toBeGreaterThan(requested)
  await Promise.race([app.close().catch(() => undefined), new Promise((r) => setTimeout(r, 10_000))])
  state.app = undefined
}

async function roundTripUninstall(): Promise<void> {
  const state = rts
  expect(state, 'AC-174.19 left its state').toBeDefined()
  if (state === undefined) return
  const host = realHost()
  const paths = accountPaths(state.run.root)
  const cache = join(paths.localAppData, 'av-kit-ui-updater')
  test.info().annotations.push({ type: 'updater-cache-before', description: String(existsSync(cache)) })
  stopUnder(state.run.installDir)
  expect(await waitFor(() => pidsUnder(state.run.installDir).length === 0, 60_000), 'nothing runs from the install folder').toBe(true)
  await uninstall(host, state.run)
  // The uninstaller's own work (UNINSTALL_CACHE_RECURSIVE); the stage has removed nothing yet.
  const gone = () => !existsSync(cache) && !host.regValueExists(RUN_KEY, APP_ID) && !host.regValueExists(APPROVED_KEY, APP_ID)
  await waitFor(gone, 60_000)
  expect(existsSync(cache), `${cache} after the uninstaller`).toBe(false)
  expect(host.regValueExists(RUN_KEY, APP_ID), `the Run value ${APP_ID} after the uninstaller`).toBe(false)
  expect(host.regValueExists(APPROVED_KEY, APP_ID), `the StartupApproved value ${APP_ID} after the uninstaller`).toBe(false)
  state.tornDown = true
  await state.feed?.close()
  const problems = await teardown(state.run, state.before, state.decoy.pid, state.owner)
  expect(problems, 'the teardown leaves the account as it found it').toEqual([])
}

const payloadDir = process.env.AVKIT_E2E_PAYLOAD_DIR ?? ''
let payload: Payload | undefined
let loadError = ''
try {
  payload = payloadDir ? readPayload(payloadDir) : undefined
  if (!payloadDir) loadError = 'AVKIT_E2E_PAYLOAD_DIR is not set'
} catch (e) {
  loadError = `payload.json: ${String(e)}`
}

test.describe.configure({ mode: 'serial' })

if (payload?.mode === 'canary') {
  const p = payload
  test('AC-174.18 the canary installs silently, shows the main window and leaves the account as it found it', async () => {
    await canary(p, payloadDir)
  })
} else if (payload?.mode === 'roundtrip') {
  const p = payload
  // A failed AC-174.19 stops the serial block, so the teardown also runs here (INSTALL_STAGE_RULES).
  test.afterAll(async () => {
    const state = rts
    if (state === undefined || state.tornDown) return
    state.tornDown = true
    await state.app?.close().catch(() => undefined)
    if (state.mcp?.exitCode === null) state.mcp.kill()
    await state.feed?.close()
    const problems = await teardown(state.run, state.before, state.decoy.pid, state.owner)
    expect(problems, 'the teardown leaves the account as it found it').toEqual([])
  })
  test('AC-174.19 an installed 0.0.901 updates itself to 0.0.902 from the local feed and keeps what the user had', async () => {
    await roundTripUpdate(p, payloadDir)
  })
  test('AC-174.20 the uninstaller removes the updater cache and both sign-in values', async () => {
    await roundTripUninstall()
  })
} else {
  test('AC-174.18 the install stage has a payload it can run', () => {
    expect(loadError || `mode ${String(payload?.mode)} has no tests yet`).toBe('')
  })
}
