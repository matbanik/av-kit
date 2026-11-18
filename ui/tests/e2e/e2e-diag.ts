// Session 91 (2026-11-17-e2e-pointer-flakes, D-1149, D-1150): the E2E diagnostics. When
// AVKIT_E2E_DIAG_DIR names a folder, each launch through electron-app.ts appends its phase lines
// to <dir>/phases.jsonl (PHASE_LINES) and its main-process events to <dir>/main-<launch>.jsonl
// (MAIN_DIAG). installMainDiag also sets the pointer shield (POINTER_SHIELD): the app's windows
// ignore OS mouse input, while Playwright's input still reaches the page. This file imports
// nothing from the Playwright package.
import { appendFileSync, mkdirSync } from 'node:fs'
import { join } from 'node:path'

type Env = Record<string, string | undefined>

/** The variable that names the diag folder; flake-run.py sets it per run. */
export const DIAG_DIR_ENV = 'AVKIT_E2E_DIAG_DIR'
/** The variable that names the run; flake-run.py sets it to `<inv>-<i>`. */
export const RUN_ID_ENV = 'AVKIT_E2E_RUN_ID'

/** The diag folder, or `null` when the variable is unset or empty: then no diag line is written. */
export function diagDir(env: Env = process.env): string | null {
  const dir = env[DIAG_DIR_ENV]
  return dir === undefined || dir === '' ? null : dir
}

/** The run id flake-run.py set for this run, or `''`. */
export function runId(env: Env = process.env): string {
  return env[RUN_ID_ENV] ?? ''
}

/** One line of `<dir>/phases.jsonl` (Boundary Inventory). */
export interface PhaseRow {
  t: number
  phase: 'launch-start' | 'launch-end' | 'evaluate-end' | 'evaluate-error' | 'close-start' | 'close-end' | 'exit'
  run_id: string
  file: string
  line: number
  title: string
  repeat: number
  test_status: string
  test_errors: number
  launch: number
  main_log: string
  message?: string
}

/** `PHASE_LINES`: append one JSON line to `<dir>/phases.jsonl`. */
export function phaseLine(dir: string, row: PhaseRow): void {
  mkdirSync(dir, { recursive: true })
  appendFileSync(join(dir, 'phases.jsonl'), JSON.stringify(row) + '\n')
}

type Bounds = { x: number; y: number; width: number; height: number }

interface DiagWindow {
  id: number
  getBounds(): Bounds
  isDestroyed(): boolean
  setIgnoreMouseEvents(ignore: boolean): void
  on(event: string, listener: (...args: unknown[]) => void): unknown
  webContents: { executeJavaScript(code: string): Promise<unknown> }
}

interface DiagEmitter {
  on(event: string, listener: (...args: never[]) => void): unknown
}

interface DiagElectron {
  app: DiagEmitter
  BrowserWindow: { getAllWindows(): DiagWindow[] }
  screen: DiagEmitter & { getCursorScreenPoint(): { x: number; y: number } }
}

export interface MainDiagOptions {
  /** The main log; `null` writes no line, while the shield still applies. */
  file: string | null
  /** `POINTER_SHIELD`: ignore OS mouse input on every window. */
  shield: boolean
}

/**
 * `MAIN_DIAG`: runs in the Electron main process through `app.evaluate`, so it is self-contained:
 * it takes `fs` from `process.getBuiltinModule` and closes over nothing. It appends one JSON line
 * `{ t, event, ... }` per event to `file` and, with `shield`, makes each window ignore OS mouse
 * input. A 250 ms interval, unref'd and cleared on `will-quit`, logs cursor and visibility changes.
 */
export function installMainDiag(electron: unknown, { file, shield }: MainDiagOptions): void {
  const { app, BrowserWindow, screen } = electron as DiagElectron
  const fs = process.getBuiltinModule('node:fs')
  const windowEvents = ['show', 'hide', 'resize', 'move', 'focus', 'blur', 'minimize', 'restore']
  const windows = new Set<DiagWindow>()
  const ids = new Map<DiagWindow, number>()
  const seen = new Map<DiagWindow, string>()
  const pending = new Set<DiagWindow>()
  let stopped = false
  const write = (event: string, extra: Record<string, unknown> = {}): void => {
    if (file === null) return
    try {
      fs.appendFileSync(file, JSON.stringify({ t: Date.now(), event, ...extra }) + '\n')
    } catch {
      // A diag line never breaks the app under test.
    }
  }
  const boundsOf = (win: DiagWindow): Bounds | null => {
    try {
      return win.isDestroyed() ? null : win.getBounds()
    } catch {
      return null
    }
  }
  const cursor = (): { x: number; y: number } | null => {
    try {
      return screen.getCursorScreenPoint()
    } catch {
      return null
    }
  }
  const insideAny = (point: { x: number; y: number } | null): boolean =>
    point !== null &&
    [...windows].some((win) => {
      const b = boundsOf(win)
      return b !== null && point.x >= b.x && point.x < b.x + b.width && point.y >= b.y && point.y < b.y + b.height
    })
  const readVisibility = (win: DiagWindow): void => {
    if (stopped || pending.has(win) || boundsOf(win) === null) return
    pending.add(win)
    let reading: Promise<unknown>
    try {
      reading = win.webContents.executeJavaScript('document.visibilityState')
    } catch {
      pending.delete(win)
      return
    }
    reading.then(
      (state) => {
        pending.delete(win)
        if (stopped || typeof state !== 'string') return
        const last = seen.get(win)
        seen.set(win, state)
        if (last !== undefined && last !== state) write('visibility', { id: ids.get(win), state })
      },
      () => {
        pending.delete(win)
      },
    )
  }
  const hook = (win: DiagWindow): void => {
    if (windows.has(win)) return
    windows.add(win)
    ids.set(win, win.id)
    if (shield) {
      try {
        win.setIgnoreMouseEvents(true)
      } catch {
        // A window destroyed before the shield reached it takes no input anyway.
      }
    }
    for (const event of windowEvents) {
      win.on(event, () => write(event, { id: ids.get(win), bounds: boundsOf(win) }))
    }
    win.on('closed', () => {
      windows.delete(win)
    })
    readVisibility(win)
  }
  for (const win of BrowserWindow.getAllWindows()) hook(win)
  app.on('browser-window-created', (_event: unknown, win: DiagWindow) => hook(win))
  let inside = insideAny(cursor())
  write('install', {
    windows: [...windows].map((win) => ({ id: ids.get(win), bounds: boundsOf(win) })),
    point: cursor(),
  })
  try {
    for (const change of ['added', 'removed', 'metrics-changed']) {
      screen.on(`display-${change}`, () => write('display', { change }))
    }
  } catch {
    // The screen module answers only once the app is ready; the launch waits for that.
  }
  const timer = setInterval(() => {
    const point = cursor()
    const now = insideAny(point)
    if (now !== inside) {
      inside = now
      write(now ? 'cursor-inside' : 'cursor-outside', { point })
    }
    for (const win of windows) readVisibility(win)
  }, 250)
  timer.unref()
  app.on('before-quit', () => write('before-quit'))
  app.on('will-quit', () => {
    stopped = true
    clearInterval(timer)
    write('will-quit')
  })
  app.on('quit', () => write('quit'))
}
