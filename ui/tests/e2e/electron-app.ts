// The one Electron launch path for the E2E suite. Every spec launches through launchElectron, so
// each run drops ELECTRON_RUN_AS_NODE, needs a scratch profile, and fails when the main process
// throws an uncaught exception or leaves a promise rejection unhandled.
import type { ChildProcess } from 'node:child_process'
import { existsSync, mkdtempSync, readFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { _electron, type ElectronApplication } from '@playwright/test'

import {
  MAIN_ERROR_LOG_ENV,
  MAIN_ERROR_WATCH,
  electronEnv,
  mainErrorRecords,
  requireScratchAppData,
} from './electron-env'

const here = dirname(fileURLToPath(import.meta.url))

/** The built main entry that the specs launch unless they name another. */
export const DEFAULT_MAIN = resolve(here, '../../out/main/index.js')

/** How long close() waits for the process to exit before it reads the error log. */
const EXIT_WAIT_MS = 5_000

export interface LaunchOptions {
  /** The main entry to run; DEFAULT_MAIN when absent. */
  main?: string
  /** The spec's own variables. AVKIT_APP_DATA must name a folder inside tmpdir(). */
  env?: Record<string, string | undefined>
}

function waitForExit(child: ChildProcess): Promise<void> {
  if (child.exitCode !== null || child.signalCode !== null) return Promise.resolve()
  return new Promise<void>((done) => {
    const timer = setTimeout(done, EXIT_WAIT_MS)
    child.once('exit', () => {
      clearTimeout(timer)
      done()
    })
  })
}

async function checkMainErrors(dir: string, log: string): Promise<void> {
  if (!existsSync(log)) {
    rmSync(dir, { recursive: true, force: true })
    throw new Error('main-error watch never started: ' + log)
  }
  let records
  try {
    records = mainErrorRecords(readFileSync(log, 'utf8'))
  } finally {
    rmSync(dir, { recursive: true, force: true })
  }
  if (records.length > 0) {
    throw new Error(
      'main-process uncaught exception(s) or unhandled rejection(s):\n' +
        records.map((r) => (r.kind === 'rejection' ? 'unhandled rejection: ' : '') + (r.stack ?? r.raw)).join('\n---\n'),
    )
  }
}

/**
 * Launches the app (or `main`) with the main-error watch preloaded. The returned app's close()
 * closes it as before, waits briefly for the process to exit, then throws if the main process
 * recorded any uncaught exception or unhandled promise rejection.
 */
export async function launchElectron({ main, env = {} }: LaunchOptions = {}): Promise<ElectronApplication> {
  requireScratchAppData(env)
  const dir = mkdtempSync(join(tmpdir(), 'avkit-e2e-main-'))
  const log = join(dir, 'errors.jsonl')
  let app: ElectronApplication
  try {
    app = await _electron.launch({
      args: ['-r', MAIN_ERROR_WATCH, main ?? DEFAULT_MAIN],
      env: electronEnv(process.env, { ...env, [MAIN_ERROR_LOG_ENV]: log }),
    })
  } catch (error) {
    rmSync(dir, { recursive: true, force: true })
    throw error
  }
  // Taken now: once close() has run, Playwright has disposed the app object and process() throws.
  const child = app.process()
  const close = app.close.bind(app)
  let closing: Promise<void> | undefined
  app.close = () => {
    closing ??= (async () => {
      await close()
      await waitForExit(child)
      await checkMainErrors(dir, log)
    })()
    return closing
  }
  return app
}
