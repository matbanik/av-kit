// The environment and error-log helpers behind launchElectron (electron-app.ts). They hold no
// Playwright import, so the Vitest unit tests (ui/tests/unit/e2e-harness.test.ts) load them
// directly.
import { tmpdir } from 'node:os'
import { dirname, isAbsolute, relative, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))

/** The stderr prefix that main-error-watch.cjs writes before each uncaught exception's stack. */
export const MAIN_ERROR_MARKER = '[avkit-e2e-main-error]'

/** The variable that tells main-error-watch.cjs where to write its error log. */
export const MAIN_ERROR_LOG_ENV = 'AVKIT_E2E_MAIN_ERROR_LOG'

/** The preload that watches the main process for uncaught exceptions. */
export const MAIN_ERROR_WATCH = resolve(here, 'main-error-watch.cjs')

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
