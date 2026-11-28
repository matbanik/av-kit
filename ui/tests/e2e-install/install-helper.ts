// The install stage's helper (Session 106, INSTALL_STAGE_RULES). It runs on the remote E2E host
// only, in the E2E account, under AVKIT_E2E_PAYLOAD_DIR. It holds no Playwright import, so the
// precondition function loads in Vitest with a fake file system and a fake registry
// (tests/unit/install-preconditions.test.ts); the spec injects Playwright's launchers into
// startApp.
import { execFileSync, spawn, type ChildProcess } from 'node:child_process'
import { createHash } from 'node:crypto'
import { copyFileSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { createServer } from 'node:net'
import { basename, dirname, join } from 'node:path'

/** electron-builder's namespace for the NSIS GUID (NsisTarget.js:49, :261; multiUser.nsh:8). */
export const BUILDER_NAMESPACE = '50e065bc-3134-11e6-9bab-38c9862bdaf3'
export const APP_ID = 'com.avkit.app'
export const PRODUCT = 'av-kit'

/** The UUID v5 of a name in a namespace (RFC 4122 section 4.3). */
export function uuidV5(namespace: string, name: string): string {
  const ns = Buffer.from(namespace.replace(/-/g, ''), 'hex')
  const h = createHash('sha1').update(ns).update(Buffer.from(name, 'utf8')).digest()
  const b = Buffer.from(h.subarray(0, 16))
  b[6] = (b[6] & 0x0f) | 0x50
  b[8] = (b[8] & 0x3f) | 0x80
  const x = b.toString('hex')
  return `${x.slice(0, 8)}-${x.slice(8, 12)}-${x.slice(12, 16)}-${x.slice(16, 20)}-${x.slice(20)}`
}

/** The installer's key name under HKCU\Software: c21620fd-8854-5989-9a80-a73c80a17704. */
export const APP_GUID = uuidV5(BUILDER_NAMESPACE, APP_ID)

export const RUN_KEY = 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run'
export const APPROVED_KEY = 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\StartupApproved\\Run'
export const UNINSTALL_KEY = 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall'
export const INSTALLER_KEY = `HKCU\\Software\\${APP_GUID}`
export const OWNER_FILE = 'install-owner.json'

/** The E2E account's folders that the stage reads. */
export interface AccountPaths {
  localAppData: string
  appData: string
  desktop: string
  programs: string
  /** The host root, `<root>` of the run book. */
  root: string
}

/** What the stage reads and changes on the host; the unit test passes a fake. */
export interface Host {
  exists(path: string): boolean
  regValueExists(key: string, name: string): boolean
  regKeyExists(key: string): boolean
  /** The DisplayName of every HKCU uninstall entry. */
  uninstallEntries(): string[]
  portTaken(port: number): Promise<boolean>
  runInstaller(exe: string, args: string[]): Promise<number>
  write(path: string, text: string): void
  remove(path: string): void
}

export type Check = { ok: true } | { ok: false; reason: string; detail: string }

/** The five per-user folder names the stage watches (D-1564 adds %APPDATA%\av-kit). */
export function folders(p: AccountPaths): string[] {
  return [
    join(p.localAppData, 'Programs', PRODUCT),
    join(p.localAppData, PRODUCT),
    join(p.appData, PRODUCT),
    join(p.appData, 'av-kit-ui'),
    join(p.localAppData, 'av-kit-ui-updater'),
  ].map(win)
}

export function shortcuts(p: AccountPaths): string[] {
  return [win(join(p.desktop, `${PRODUCT}.lnk`)), win(join(p.programs, `${PRODUCT}.lnk`))]
}

function win(path: string): string {
  return path.replace(/\//g, '\\')
}

function isAvkitEntry(name: string): boolean {
  return /^av-kit( |$)/i.test(name.trim())
}

/**
 * INSTALL_STAGE_RULES: refuse, with a named reason and before any change, when the account
 * already holds an av-kit trace or the feed port is taken. It only reads the host.
 */
export async function checkPreconditions(host: Host, paths: AccountPaths, opts: { port: number }): Promise<Check> {
  const owner = win(join(paths.root, OWNER_FILE))
  if (host.exists(owner)) return { ok: false, reason: 'install-quarantined', detail: owner }
  for (const f of folders(paths)) {
    if (host.exists(f)) return { ok: false, reason: 'install-folder-exists', detail: f }
  }
  const entries = host.uninstallEntries().filter(isAvkitEntry)
  if (entries.length > 0) return { ok: false, reason: 'uninstall-entry-exists', detail: entries.join(', ') }
  for (const key of [RUN_KEY, APPROVED_KEY]) {
    if (host.regValueExists(key, APP_ID)) return { ok: false, reason: 'sign-in-value-exists', detail: `${key} ${APP_ID}` }
  }
  for (const s of shortcuts(paths)) {
    if (host.exists(s)) return { ok: false, reason: 'shortcut-exists', detail: s }
  }
  if (host.regKeyExists(INSTALLER_KEY)) return { ok: false, reason: 'installer-key-exists', detail: INSTALLER_KEY }
  if (await host.portTaken(opts.port)) return { ok: false, reason: 'feed-port-taken', detail: String(opts.port) }
  return { ok: true }
}

/** The account state the stage compares before and after (the install folder of the run aside). */
export interface Snapshot {
  uninstall: string[]
  installer_key: boolean
  run_value: boolean
  approved_value: boolean
  shortcuts: Record<string, boolean>
  folders: Record<string, boolean>
}

export function snapshot(host: Host, paths: AccountPaths): Snapshot {
  return {
    uninstall: host.uninstallEntries().filter(isAvkitEntry).sort(),
    installer_key: host.regKeyExists(INSTALLER_KEY),
    run_value: host.regValueExists(RUN_KEY, APP_ID),
    approved_value: host.regValueExists(APPROVED_KEY, APP_ID),
    shortcuts: Object.fromEntries(shortcuts(paths).map((s) => [s, host.exists(s)])),
    folders: Object.fromEntries(folders(paths).map((f) => [f, host.exists(f)])),
  }
}

/** The names whose state differs between two snapshots; empty when they are equal. */
export function snapshotDiff(a: Snapshot, b: Snapshot): string[] {
  const out: string[] = []
  if (JSON.stringify(a.uninstall) !== JSON.stringify(b.uninstall)) out.push(`uninstall ${JSON.stringify(b.uninstall)}`)
  for (const k of ['installer_key', 'run_value', 'approved_value'] as const) {
    if (a[k] !== b[k]) out.push(`${k} ${String(b[k])}`)
  }
  for (const group of ['shortcuts', 'folders'] as const) {
    for (const name of Object.keys(a[group])) {
      if (a[group][name] !== b[group][name]) out.push(`${name} ${String(b[group][name])}`)
    }
  }
  return out
}

// --- the real host ----------------------------------------------------------------------------

function reg(args: string[]): { code: number; out: string } {
  try {
    const out = execFileSync('reg.exe', args, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'], windowsHide: true })
    return { code: 0, out }
  } catch (e) {
    const err = e as { status?: number; stdout?: string }
    return { code: err.status ?? 1, out: String(err.stdout ?? '') }
  }
}

function powershell(command: string): string {
  return execFileSync('powershell.exe', ['-NoProfile', '-NonInteractive', '-Command', command], {
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
    windowsHide: true,
  }).trim()
}

export function portTaken(port: number): Promise<boolean> {
  return new Promise((resolve) => {
    const srv = createServer()
    srv.once('error', () => resolve(true))
    srv.listen(port, '127.0.0.1', () => srv.close(() => resolve(false)))
  })
}

export function realHost(): Host {
  return {
    exists: (p) => existsSync(p),
    regValueExists: (key, name) => reg(['query', key, '/v', name]).code === 0,
    regKeyExists: (key) => reg(['query', key]).code === 0,
    uninstallEntries: () => {
      const r = reg(['query', UNINSTALL_KEY, '/s', '/v', 'DisplayName'])
      return r.out
        .split(/\r?\n/)
        .map((ln) => /^\s+DisplayName\s+REG_\w+\s+(.*)$/.exec(ln)?.[1]?.trim())
        .filter((v): v is string => typeof v === 'string' && v.length > 0)
    },
    portTaken,
    runInstaller: (exe, args) =>
      new Promise((resolve, reject) => {
        const child = spawn(exe, args, { windowsHide: true, stdio: 'ignore' })
        child.once('error', reject)
        child.once('exit', (code) => resolve(code ?? -1))
      }),
    write: (p, text) => {
      mkdirSync(dirname(p), { recursive: true })
      writeFileSync(p, text, 'utf8')
    },
    remove: (p) => rmSync(p, { recursive: true, force: true }),
  }
}

export function accountPaths(root: string): AccountPaths {
  const local = process.env.LOCALAPPDATA ?? ''
  const roaming = process.env.APPDATA ?? ''
  const known = powershell("[Environment]::GetFolderPath('Desktop'); [Environment]::GetFolderPath('Programs')").split(/\r?\n/)
  return { localAppData: local, appData: roaming, desktop: known[0].trim(), programs: known[1].trim(), root }
}

// --- the payload ------------------------------------------------------------------------------

export interface Payload {
  mode: string
  installer?: string
  version?: string
  feed_port?: number
  [key: string]: unknown
}

/** The run's folders, from `<root>\runs\<run-id>\payload` that run-e2e.ps1 sets. */
export interface RunFolders {
  payloadDir: string
  runDir: string
  runId: string
  root: string
  installDir: string
  siblingDir: string
}

export function runFolders(payloadDir: string): RunFolders {
  const runDir = dirname(payloadDir)
  const root = dirname(dirname(runDir))
  return {
    payloadDir,
    runDir,
    runId: basename(runDir),
    root,
    installDir: join(runDir, 'install'),
    siblingDir: join(runDir, 'install-sibling'),
  }
}

export function readPayload(payloadDir: string): Payload {
  const text = readFileSync(join(payloadDir, 'payload.json'), 'utf8').replace(/^\uFEFF/, '')
  return JSON.parse(text) as Payload
}

// --- the owner record, the decoy and the processes ---------------------------------------------

export function writeOwner(host: Host, run: RunFolders, before: Snapshot, decoyPid: number | null): string {
  const path = join(run.root, OWNER_FILE)
  const record = {
    run_id: run.runId,
    install_folder: run.installDir,
    before,
    decoy_pid: decoyPid,
    written_utc: new Date().toISOString(),
  }
  host.write(path, JSON.stringify(record, null, 2))
  return path
}

/** The sibling decoy: a copy of PING.EXE named av-kit.exe beside the install folder. */
export function startDecoy(run: RunFolders): ChildProcess {
  mkdirSync(run.siblingDir, { recursive: true })
  const exe = join(run.siblingDir, `${PRODUCT}.exe`)
  copyFileSync(join(process.env.SystemRoot ?? 'C:\\Windows', 'System32', 'PING.EXE'), exe)
  const child = spawn(exe, ['-t', '127.0.0.1'], { windowsHide: true, stdio: 'ignore' })
  child.on('error', () => undefined)
  return child
}

export function alive(pid: number | undefined): boolean {
  if (pid === undefined) return false
  try {
    process.kill(pid, 0)
    return true
  } catch {
    return false
  }
}

/** The pids of the processes whose image path is under a folder, and no other. */
export function pidsUnder(folder: string): number[] {
  const prefix = win(folder).replace(/\\+$/, '') + '\\'
  const out = powershell(
    "Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath } | ForEach-Object { '' + $_.ProcessId + '|' + $_.ExecutablePath }",
  )
  return out
    .split(/\r?\n/)
    .map((ln) => ln.split('|'))
    .filter(([, path]) => typeof path === 'string' && path.toLowerCase().startsWith(prefix.toLowerCase()))
    .map(([pid]) => Number(pid))
    .filter((n) => Number.isInteger(n) && n > 0)
}

/** Stops only the processes whose image path is under the run's install folder. */
export function stopUnder(folder: string): number[] {
  const pids = pidsUnder(folder)
  for (const pid of pids) {
    try {
      process.kill(pid)
    } catch {
      // Already gone.
    }
  }
  return pids
}

/** The newest Code Integrity event id since a time that names a path, or '' when none is logged. */
export function codeIntegrityEvent(since: Date, path: string): string {
  try {
    const leaf = basename(path).replace(/'/g, "''")
    return powershell(
      "$e = Get-WinEvent -FilterHashtable @{ LogName = 'Microsoft-Windows-CodeIntegrity/Operational'; StartTime = [DateTime]::Parse('" +
        since.toISOString() +
        "').ToLocalTime() } -ErrorAction SilentlyContinue | Where-Object { $_.Message -like '*" +
        leaf +
        "*' } | Select-Object -First 1; if ($e) { [string]$e.Id }",
    )
  } catch {
    return ''
  }
}

export async function waitFor(what: () => boolean, ms: number, stepMs = 500): Promise<boolean> {
  const end = Date.now() + ms
  while (Date.now() < end) {
    if (what()) return true
    await new Promise((r) => setTimeout(r, stepMs))
  }
  return what()
}

/** The environment of the installed app: no E2E variables and no app-data override. */
export function appEnv(): Record<string, string> {
  const env: Record<string, string> = {}
  for (const [k, v] of Object.entries(process.env)) {
    if (v === undefined) continue
    if (k.startsWith('AVKIT_') || k === 'ELECTRON_RUN_AS_NODE' || k.startsWith('PLAYWRIGHT_')) continue
    env[k] = v
  }
  return env
}

export class StageError extends Error {
  constructor(
    readonly reason: string,
    detail: string,
  ) {
    super(`${reason}: ${detail}`)
  }
}

/** Runs the installer silently into the run's install folder; a refused start is named. */
export async function install(host: Host, installer: string, run: RunFolders): Promise<void> {
  const started = new Date()
  let code: number
  try {
    code = await host.runInstaller(installer, ['/S', `/D=${run.installDir}`])
  } catch (e) {
    const id = codeIntegrityEvent(started, installer)
    throw new StageError('installer-refused-by-host', `${String(e)}${id ? ` code-integrity-event=${id}` : ''}`)
  }
  if (code !== 0) {
    const id = codeIntegrityEvent(started, installer)
    throw new StageError(id ? 'installer-refused-by-host' : 'installer-failed', `exit ${code}${id ? ` code-integrity-event=${id}` : ''}`)
  }
}

/** The uninstaller copies itself to %TEMP% and returns at once, so the entry is polled. */
export async function uninstall(host: Host, run: RunFolders): Promise<void> {
  const exe = join(run.installDir, `Uninstall ${PRODUCT}.exe`)
  if (!existsSync(exe)) return
  const code = await host.runInstaller(exe, ['/S'])
  if (code !== 0) throw new StageError('uninstaller-failed', `exit ${code}`)
  const gone = await waitFor(() => !host.regKeyExists(`${UNINSTALL_KEY}\\${APP_GUID}`) && !existsSync(exe), 180_000)
  if (!gone) throw new StageError('uninstaller-failed', 'the uninstall entry or the uninstaller is still there after 180 s')
}

export interface Launchers<A> {
  /** Playwright's Electron launch of the installed exe. */
  electron(exe: string, env: Record<string, string>): Promise<A>
  /** The fallback: the exe started with a remote debugging port and a CDP connection. */
  cdp(exe: string, env: Record<string, string>): Promise<A>
}

/** S8: start the installed app under Playwright, else through CDP; a refused start is named. */
export async function startApp<A>(exe: string, launch: Launchers<A>): Promise<{ app: A; via: string }> {
  const started = new Date()
  const errors: string[] = []
  try {
    return { app: await launch.electron(exe, appEnv()), via: 'electron' }
  } catch (e) {
    errors.push(`electron: ${String(e).split('\n')[0]}`)
  }
  try {
    return { app: await launch.cdp(exe, appEnv()), via: 'cdp' }
  } catch (e) {
    errors.push(`cdp: ${String(e).split('\n')[0]}`)
  }
  const id = codeIntegrityEvent(started, exe)
  throw new StageError(id ? 'app-refused-by-host' : 'app-start-failed', `${errors.join('; ')}${id ? ` code-integrity-event=${id}` : ''}`)
}
