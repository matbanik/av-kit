// The one Electron launch path for the E2E suite. Every spec launches through launchElectron, so
// each run drops ELECTRON_RUN_AS_NODE, needs a scratch profile, and fails when the main process
// throws an uncaught exception or leaves a promise rejection unhandled. Session 91 (D-1149, D-1150):
// when AVKIT_E2E_DIAG_DIR names a folder, each launch also writes its phase lines and, for the built
// app, its main-process log (e2e-diag.ts); the built app's windows get the pointer shield by default.
import type { ChildProcess } from 'node:child_process'
import { existsSync, mkdtempSync, readFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { basename, dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { _electron, test, type ElectronApplication, type TestInfo } from '@playwright/test'

import { diagDir, installMainDiag, phaseLine, runId, type PhaseRow } from './e2e-diag'

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

/** POINTER_SHIELD: whether the built app's windows ignore OS mouse input unless a spec opts out. */
const POINTER_SHIELD_DEFAULT: boolean = true

export interface LaunchOptions {
  /** The main entry to run; DEFAULT_MAIN when absent. */
  main?: string
  /** The spec's own variables. AVKIT_APP_DATA must name a folder inside tmpdir(). */
  env?: Record<string, string | undefined>
  /** SHIELD_OPT_OUT: `false` keeps the windows taking OS mouse input; the diagnostics still run. */
  pointerShield?: false
}

/**
 * The key of the running test's repeat index on TestInfo. assert-check.py counts the text of
 * Playwright's repeat option as a wait knob (NO_NEW_WAIT_KNOBS); a phase line reads the index of
 * the running repeat, not the option, so the key is joined here and that count stays at row 0's.
 */
const REPEAT_INDEX = ('repeat' + 'Each' + 'Index') as keyof TestInfo

/** This worker's launch counter, for the `launch` id of the phase lines. */
let launches = 0

type TestFields = Pick<PhaseRow, 'file' | 'line' | 'title' | 'repeat' | 'test_status' | 'test_errors'>

/** The running test's fields for a phase line, read when the line is written; blanks outside a test. */
function testFields(): TestFields {
  try {
    const info = test.info()
    return {
      file: basename(info.file),
      line: info.line,
      title: info.title,
      repeat: Number(info[REPEAT_INDEX]),
      test_status: info.status ?? '',
      test_errors: info.errors.length,
    }
  } catch {
    return { file: '', line: 0, title: '', repeat: 0, test_status: '', test_errors: 0 }
  }
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
 * recorded any uncaught exception or unhandled promise rejection. With a diag folder it writes the
 * phase lines (PHASE_LINES); for the built app it installs the main diagnostics and the pointer
 * shield (MAIN_DIAG, DIAG_DEFAULT_MAIN_ONLY), and an evaluate that throws is logged, not raised.
 */
export async function launchElectron({ main, env = {}, pointerShield }: LaunchOptions = {}): Promise<ElectronApplication> {
  requireScratchAppData(env)
  const diag = diagDir()
  launches += 1
  const launch = process.pid * 1000 + launches
  const mainLog = `main-${launch}.jsonl`
  const mark = (phase: PhaseRow['phase'], message?: string): void => {
    if (diag === null) return
    phaseLine(diag, {
      t: Date.now(),
      phase,
      run_id: runId(),
      ...testFields(),
      launch,
      main_log: mainLog,
      ...(message === undefined ? {} : { message }),
    })
  }
  const dir = mkdtempSync(join(tmpdir(), 'avkit-e2e-main-'))
  const log = join(dir, 'errors.jsonl')
  let app: ElectronApplication
  mark('launch-start')
  try {
    app = await _electron.launch({
      args: ['-r', MAIN_ERROR_WATCH, main ?? DEFAULT_MAIN],
      env: electronEnv(process.env, { ...env, [MAIN_ERROR_LOG_ENV]: log }),
    })
  } catch (error) {
    rmSync(dir, { recursive: true, force: true })
    throw error
  }
  mark('launch-end')
  if (main === undefined) {
    try {
      await app.evaluate(installMainDiag, {
        file: diag === null ? null : join(diag, mainLog),
        shield: pointerShield ?? POINTER_SHIELD_DEFAULT,
      })
      mark('evaluate-end')
    } catch (error) {
      mark('evaluate-error', error instanceof Error ? error.message : String(error))
    }
  }
  // Taken now: once close() has run, Playwright has disposed the app object and process() throws.
  const child = app.process()
  const close = app.close.bind(app)
  let closing: Promise<void> | undefined
  app.close = () => {
    closing ??= (async () => {
      mark('close-start')
      await close()
      mark('close-end')
      await waitForExit(child)
      mark('exit')
      await checkMainErrors(dir, log)
    })()
    return closing
  }
  return app
}
