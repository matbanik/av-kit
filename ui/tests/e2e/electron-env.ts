// The environment and error-log helpers behind launchElectron (electron-app.ts). They hold no
// Playwright import, so the Vitest unit tests (ui/tests/unit/e2e-harness.test.ts) load them
// directly.
import { tmpdir } from 'node:os'
import { dirname, isAbsolute, join, relative, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))

/** The stderr prefix that main-error-watch.cjs writes before each uncaught exception's stack. */
export const MAIN_ERROR_MARKER = '[avkit-e2e-main-error]'

/**
 * The stderr prefix that main-error-watch.cjs writes before each unhandled rejection's
 * `UnhandledPromiseRejectionWarning: <stack>` line.
 */
export const MAIN_REJECTION_MARKER = '[avkit-e2e-main-rejection]'

/** The variable that tells main-error-watch.cjs where to write its error log. */
export const MAIN_ERROR_LOG_ENV = 'AVKIT_E2E_MAIN_ERROR_LOG'

/** The preload that watches the main process for uncaught exceptions. */
export const MAIN_ERROR_WATCH = resolve(here, 'main-error-watch.cjs')

/** The preload that keeps a launch off the system clipboard (Session 100, D-1310, D-1320). */
export const CLIPBOARD_GUARD_WATCH = resolve(here, 'clipboard-guard.cjs')

/** The variable that tells clipboard-guard.cjs where to append its log (D-1321). */
export const CLIPBOARD_GUARD_LOG_ENV = 'AVKIT_E2E_CLIPBOARD_GUARD_LOG'

type Env = Record<string, string | undefined>

/**
 * The environment for one E2E Electron launch: a copy of `base` with AVKIT_E2E set and `extra`
 * merged in, then without ELECTRON_RUN_AS_NODE (which makes Electron run as plain Node) and
 * without any key whose value is undefined. `base` is never changed.
 */
export function electronEnv(base: Env = process.env, extra: Env = {}): Record<string, string> {
  const env: Env = { ...base }
  env.AVKIT_E2E = '1'
  Object.assign(env, extra)
  delete env.ELECTRON_RUN_AS_NODE
  const out: Record<string, string> = {}
  for (const [key, value] of Object.entries(env)) {
    if (value !== undefined) out[key] = value
  }
  return out
}

/** One line of the error log: a parsed record, or the raw line when it is not one. */
export interface MainErrorRecord {
  /** 'rejection' for an unhandled promise rejection; absent for an uncaught exception. */
  kind?: 'rejection'
  name?: string
  message?: string
  stack?: string
  raw?: string
}

/** Every non-empty line of the error log, in order. A line that is not a record is kept as raw. */
export function mainErrorRecords(text: string): MainErrorRecord[] {
  const records: MainErrorRecord[] = []
  for (const line of text.split('\n')) {
    if (line.trim() === '') continue
    let parsed: unknown
    try {
      parsed = JSON.parse(line)
    } catch {
      parsed = undefined
    }
    if (
      parsed !== null &&
      typeof parsed === 'object' &&
      !Array.isArray(parsed) &&
      typeof (parsed as MainErrorRecord).stack === 'string'
    ) {
      records.push(parsed as MainErrorRecord)
    } else {
      records.push({ raw: line })
    }
  }
  return records
}

/**
 * The caller's AVKIT_APP_DATA when it names a folder inside tmpdir(). Without one the app would
 * use the normal profile, so anything else is refused before a launch.
 */
export function requireScratchAppData(env: Env = {}): string {
  const value = env.AVKIT_APP_DATA
  if (typeof value === 'string' && value !== '') {
    const rel = relative(resolve(tmpdir()), resolve(value))
    if (rel !== '' && !rel.startsWith('..') && !isAbsolute(rel)) return value
  }
  throw new Error('launchElectron needs a scratch AVKIT_APP_DATA under tmpdir(): ' + String(value))
}

/** Only the gated stage on the second Windows host sets this to 1 (Session 98 D-1282). */
const CLIPBOARD_GATE_ENV = 'AVKIT_E2E_CLIPBOARD_GATED'

/** The prefix of every guard failure message. */
const CLIPBOARD_GUARD_PREFIX = 'CLIPBOARD_GUARD:'

/**
 * The Node arguments that preload the clipboard guard (Session 100, D-1310): none when
 * AVKIT_E2E_CLIPBOARD_GATED is exactly 1, the guard for every other launch.
 */
export function clipboardGuardArgs(env: Env = process.env): string[] {
  return env[CLIPBOARD_GATE_ENV] === '1' ? [] : ['-r', CLIPBOARD_GUARD_WATCH]
}

/**
 * One launch's guard log (D-1321): beside the launch's phase lines when a diag folder is set, so
 * it is kept; else in the launch's scratch folder, which close() deletes.
 */
export function clipboardGuardLogPath(scratch: string, diag: string | null, launch: number): string {
  return diag === null ? join(scratch, 'clipboard.jsonl') : join(diag, `clipboard-${launch}.jsonl`)
}

/**
 * The guard's verdict on one launch's log (D-1321): ok only when the guard installed and
 * recorded no call. Otherwise the message names the first problem: a missing log, a line that is
 * not a JSON object (numbered from 1), an install failure, no install, or the calls in log order.
 */
export function clipboardGuardVerdict(text: string | null): { ok: boolean; message: string } {
  const fail = (what: string): { ok: boolean; message: string } => ({ ok: false, message: `${CLIPBOARD_GUARD_PREFIX} ${what}` })
  if (text === null) return fail('the guard log is missing')
  const rows: Array<Record<string, unknown>> = []
  const lines = text.split('\n')
  for (let i = 0; i < lines.length; i += 1) {
    if (lines[i].trim() === '') continue
    let parsed: unknown
    try {
      parsed = JSON.parse(lines[i])
    } catch {
      parsed = undefined
    }
    if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) return fail(`invalid guard log line ${i + 1}`)
    rows.push(parsed as Record<string, unknown>)
  }
  const failed = rows.filter((row) => typeof row.failed === 'string').map((row) => String(row.failed))
  if (failed.length > 0) return fail(`the guard failed to install: ${failed.join(', ')}`)
  if (!rows.some((row) => row.installed === true)) return fail('the guard was never installed')
  const calls = rows.filter((row) => typeof row.call === 'string').map((row) => String(row.call))
  if (calls.length > 0) return fail(`clipboard call(s) in a launch without ${CLIPBOARD_GATE_ENV}=1: ${calls.join(', ')}`)
  return { ok: true, message: '' }
}
