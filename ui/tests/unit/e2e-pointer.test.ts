// @vitest-environment node
// Session 91 (2026-11-17-e2e-pointer-flakes): the pointer settle (AC-1), the E2E diagnostics
// (AC-2, AC-3) and the static reads of the fixed specs (AC-6, AC-7). Each module is checked with
// existsSync first and loaded through a dynamic import, so a missing module fails by assertion.
import { EventEmitter } from 'node:events'
import { existsSync, mkdtempSync, readFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

import { describe, expect, it, vi } from 'vitest'

const here = dirname(fileURLToPath(import.meta.url))
const e2eDir = resolve(here, '../e2e')
const SETTLE_PATH = resolve(e2eDir, 'pointer-settle.ts')
const DIAG_PATH = resolve(e2eDir, 'e2e-diag.ts')
const DOWNLOAD_SPEC = resolve(e2eDir, 'download-queue.test.ts')
const CONVERT_SPEC = resolve(e2eDir, 'convert-queue.test.ts')
const CAPTURE_SPEC = resolve(e2eDir, 'capture-inbox.test.ts')
const SHARED_HELPERS = ['settledCenter', 'rowTransitionsIdle', 'windowSettled', 'grabRow', 'dragOver'] as const

type Point = { x: number; y: number }
type Bounds = { x: number; y: number; width: number; height: number }
type DiagLine = { t?: unknown; event?: string; bounds?: unknown; state?: unknown; [key: string]: unknown }

interface SettleModule {
  settle: <T>(read: () => Promise<T>, nextFrame: () => Promise<void>, maxFrames?: number) => Promise<T>
}

interface DiagModule {
  DIAG_DIR_ENV: string
  RUN_ID_ENV: string
  diagDir: (env?: Record<string, string | undefined>) => string | null
  runId: (env?: Record<string, string | undefined>) => string
  phaseLine: (dir: string, row: Record<string, unknown>) => void
  installMainDiag: (electron: unknown, options: { file: string | null; shield: boolean }) => void
}

async function loadSettle(): Promise<SettleModule> {
  expect(existsSync(SETTLE_PATH), 'ui/tests/e2e/pointer-settle.ts exists').toBe(true)
  const mod = (await import(/* @vite-ignore */ pathToFileURL(SETTLE_PATH).href)) as Partial<SettleModule>
  expect(typeof mod.settle, 'settle is exported').toBe('function')
  return mod as SettleModule
}

async function loadDiag(): Promise<DiagModule> {
  expect(existsSync(DIAG_PATH), 'ui/tests/e2e/e2e-diag.ts exists').toBe(true)
  const mod = (await import(/* @vite-ignore */ pathToFileURL(DIAG_PATH).href)) as Partial<DiagModule>
  for (const name of ['diagDir', 'runId', 'phaseLine', 'installMainDiag'] as const) {
    expect(typeof mod[name], `${name} is exported`).toBe('function')
  }
  return mod as DiagModule
}

function read(path: string): string {
  expect(existsSync(path), `${path} exists`).toBe(true)
  return readFileSync(path, 'utf8')
}

function count(text: string, pattern: RegExp): number {
  return (text.match(new RegExp(pattern.source, 'g')) ?? []).length
}

function definitions(text: string, name: string): number {
  return count(text, new RegExp(`\\bfunction\\s+${name}\\s*[(<]`))
}

/** The text of one test, from its `test('<prefix>` line to the `})` that closes it at column 0. */
function testBody(text: string, prefix: string): string {
  const start = text.indexOf(`\ntest('${prefix}`)
  expect(start, `the test that starts '${prefix}'`).toBeGreaterThan(-1)
  const end = text.indexOf('\n})', start + 1)
  expect(end, `the end of the test that starts '${prefix}'`).toBeGreaterThan(start)
  return text.slice(start, end)
}

/** The text of one top-level function, from its declaration to the `}` that closes it at column 0. */
function functionBody(text: string, declaration: string): string {
  const start = text.indexOf(`\n${declaration}`)
  expect(start, `the function '${declaration}'`).toBeGreaterThan(-1)
  const end = text.indexOf('\n}', start + 1)
  expect(end, `the end of '${declaration}'`).toBeGreaterThan(start)
  return text.slice(start, end)
}

function lines(file: string): DiagLine[] {
  if (!existsSync(file)) return []
  return readFileSync(file, 'utf8')
    .split('\n')
    .filter((line) => line !== '')
    .map((line) => JSON.parse(line) as DiagLine)
}

class FakeWindow extends EventEmitter {
  readonly setIgnoreMouseEvents = vi.fn()
  readonly webContents: { executeJavaScript: (code: string) => Promise<string> }
  state: string

  constructor(
    readonly id: number,
    public bounds: Bounds,
    state = 'visible',
  ) {
    super()
    this.state = state
    this.webContents = { executeJavaScript: () => Promise.resolve(this.state) }
  }

  getBounds(): Bounds {
    return { ...this.bounds }
  }

  isDestroyed(): boolean {
    return false
  }
}

function fakeElectron(windows: FakeWindow[]) {
  const app = new EventEmitter()
  const screen = Object.assign(new EventEmitter(), { point: { x: 5000, y: 5000 } as Point })
  const electron = {
    app,
    BrowserWindow: { getAllWindows: () => [...windows] },
    screen: Object.assign(screen, { getCursorScreenPoint: () => ({ ...screen.point }) }),
  }
  return { electron, app, screen }
}

describe('Session 91 pointer settle and E2E diagnostics', () => {
  it('AC-1 settle returns once two reads one frame apart are equal, and rejects when they never are', async () => {
    const { settle } = await loadSettle()
    const values = [1, 2, 2]
    let reads = 0
    let frames = 0
    const value = await settle(
      async () => values[reads++],
      async () => {
        frames += 1
      },
    )
    expect(value).toBe(2)
    expect(reads, 'reads for 1, 2, 2').toBe(3)
    expect(frames, 'frames for 1, 2, 2').toBe(2)

    let objectReads = 0
    const object = await settle(
      async () => {
        objectReads += 1
        return { a: 1 }
      },
      async () => undefined,
    )
    expect(object).toEqual({ a: 1 })
    expect(objectReads, 'reads for {a:1}, {a:1}').toBe(2)

    let neverReads = 0
    await expect(
      settle(
        async () => {
          neverReads += 1
          return neverReads
        },
        async () => undefined,
        5,
      ),
    ).rejects.toThrow('layout never settled:')
    expect(neverReads, 'reads before the rejection').toBe(5)
  })

  it('AC-2 diagDir and runId read their variables, and phaseLine appends one parsable line per row', async () => {
    const { DIAG_DIR_ENV, RUN_ID_ENV, diagDir, runId, phaseLine } = await loadDiag()
    expect(DIAG_DIR_ENV).toBe('AVKIT_E2E_DIAG_DIR')
    expect(RUN_ID_ENV).toBe('AVKIT_E2E_RUN_ID')
    const dir = mkdtempSync(join(tmpdir(), 'avkit-s91-ac2-'))
    try {
      expect(diagDir({})).toBeNull()
      expect(diagDir({ AVKIT_E2E_DIAG_DIR: '' })).toBeNull()
      expect(diagDir({ AVKIT_E2E_DIAG_DIR: dir })).toBe(dir)
      expect(runId({})).toBe('')
      expect(runId({ AVKIT_E2E_RUN_ID: 'x-1' })).toBe('x-1')
      const base = {
        run_id: 'x-1',
        file: 'download-queue.test.ts',
        line: 1319,
        title: 'AC-49.25 a title',
        repeat: 0,
        launch: 4242001,
        main_log: 'main-4242001.jsonl',
      }
      const rows = [
        { t: 1, phase: 'launch-start', ...base, test_status: 'passed', test_errors: 0 },
        { t: 2, phase: 'close-start', ...base, test_status: 'timedOut', test_errors: 1 },
      ]
      for (const row of rows) phaseLine(dir, row)
      const written = lines(join(dir, 'phases.jsonl'))
      expect(written).toEqual(rows)
      const fields = ['t', 'phase', 'run_id', 'file', 'line', 'title', 'repeat', 'test_status', 'test_errors', 'launch', 'main_log']
      for (const line of written) expect(Object.keys(line).sort()).toEqual([...fields].sort())
      expect(read(DIAG_PATH)).not.toContain('@playwright/test')
    } finally {
      rmSync(dir, { recursive: true, force: true })
    }
  })

  it('AC-3 installMainDiag logs window, cursor and visibility events, shields each window, and stops at will-quit', async () => {
    const { installMainDiag } = await loadDiag()
    const source = String(installMainDiag)
    expect(source).not.toContain('require(')
    expect(source).not.toMatch(/\bimport\b/)
    expect(source).not.toContain('setBackgroundThrottling')
    const dir = mkdtempSync(join(tmpdir(), 'avkit-s91-ac3-'))
    vi.useFakeTimers()
    try {
      // shield: true
      const one = new FakeWindow(1, { x: 0, y: 0, width: 800, height: 600 })
      const two = new FakeWindow(2, { x: 1000, y: 0, width: 400, height: 300 })
      const { electron, app, screen } = fakeElectron([one, two])
      const file = join(dir, 'main-shield.jsonl')
      installMainDiag(electron, { file, shield: true })
      for (const win of [one, two]) {
        expect(win.setIgnoreMouseEvents, `window ${win.id} shield`).toHaveBeenCalledTimes(1)
        expect(win.setIgnoreMouseEvents).toHaveBeenCalledWith(true)
      }
      expect(lines(file).map((line) => line.event)).toEqual(['install'])
      await vi.advanceTimersByTimeAsync(0)

      one.bounds = { x: 0, y: 0, width: 780, height: 580 }
      one.emit('resize')
      const resize = lines(file).at(-1)
      expect(resize?.event).toBe('resize')
      expect(resize?.bounds).toEqual(one.bounds)

      screen.point = { x: 10, y: 10 }
      await vi.advanceTimersByTimeAsync(250)
      expect(lines(file).at(-1)?.event).toBe('cursor-inside')
      screen.point = { x: 5000, y: 5000 }
      await vi.advanceTimersByTimeAsync(250)
      expect(lines(file).at(-1)?.event).toBe('cursor-outside')

      two.emit('minimize')
      expect(lines(file).at(-1)?.event).toBe('minimize')

      const later = new FakeWindow(3, { x: 3000, y: 3000, width: 100, height: 100 })
      app.emit('browser-window-created', {}, later)
      expect(later.setIgnoreMouseEvents, 'a later window shield').toHaveBeenCalledTimes(1)
      expect(later.setIgnoreMouseEvents).toHaveBeenCalledWith(true)
      await vi.advanceTimersByTimeAsync(0)

      one.state = 'hidden'
      await vi.advanceTimersByTimeAsync(250)
      const visibility = lines(file).at(-1)
      expect(visibility?.event).toBe('visibility')
      expect(visibility?.state).toBe('hidden')
      const settled = lines(file).length
      await vi.advanceTimersByTimeAsync(250)
      expect(lines(file).length, 'an unchanged visibility adds no line').toBe(settled)

      app.emit('will-quit')
      screen.point = { x: 10, y: 10 }
      one.state = 'visible'
      await vi.advanceTimersByTimeAsync(1000)
      expect(lines(file).map((line) => line.event)).toEqual([
        'install',
        'resize',
        'cursor-inside',
        'cursor-outside',
        'minimize',
        'visibility',
        'will-quit',
      ])
      for (const line of lines(file)) expect(typeof line.t, `${String(line.event)} t`).toBe('number')

      // shield: false
      const three = new FakeWindow(4, { x: 0, y: 0, width: 800, height: 600 })
      const off = fakeElectron([three])
      const offFile = join(dir, 'main-off.jsonl')
      installMainDiag(off.electron, { file: offFile, shield: false })
      three.emit('resize')
      const offLater = new FakeWindow(5, { x: 3000, y: 3000, width: 100, height: 100 })
      off.app.emit('browser-window-created', {}, offLater)
      offLater.emit('minimize')
      expect(three.setIgnoreMouseEvents).not.toHaveBeenCalled()
      expect(offLater.setIgnoreMouseEvents).not.toHaveBeenCalled()
      expect(lines(offFile).map((line) => line.event)).toEqual(['install', 'resize', 'minimize'])
      off.app.emit('will-quit')
    } finally {
      vi.useRealTimers()
      rmSync(dir, { recursive: true, force: true })
    }
  })

  it('AC-6 the five drag helpers live once in pointer-settle.ts, and both queue specs import them', () => {
    const shared = read(SETTLE_PATH)
    for (const name of SHARED_HELPERS) {
      expect(definitions(shared, name), `${name} in pointer-settle.ts`).toBe(1)
    }
    expect(shared).toContain('rowTestId')
    for (const spec of [DOWNLOAD_SPEC, CONVERT_SPEC]) {
      const text = read(spec)
      for (const name of SHARED_HELPERS) {
        expect(definitions(text, name), `${name} defined in ${spec}`).toBe(0)
      }
      expect(text, `${spec} imports from ./pointer-settle`).toMatch(/from '\.\/pointer-settle'/)
    }
    const body = testBody(read(CONVERT_SPEC), 'AC-49.29 ')
    expect(body).toContain('grabRow(')
    expect(body).toContain('dragOver(')
    expect(body).toContain("'convert-queue-row'")
    expect(body).not.toContain('boundingBox()')
  })

  it('AC-7 the capture spec reads settled zoom, boxes and pointer points at its flaky sites', () => {
    const text = read(CAPTURE_SPEC)
    expect(text).not.toContain('async function windowSettled(')
    expect(text).toMatch(/import \{[^}]*\bwindowSettled\b[^}]*\} from '\.\/pointer-settle'/)
    for (const prefix of ['AC-66.14 ', 'AC-81.14:']) {
      const body = testBody(text, prefix)
      expect(body, `${prefix} reads through settledZoom`).toContain('settledZoom(')
      expect(body, `${prefix} never calls readZoom directly`).not.toContain('readZoom(')
    }
    const grab = testBody(text, 'AC-81.14:')
    const grabbed = grab.indexOf('const grabbed = await ends()')
    expect(grabbed, 'const grabbed = await ends()').toBeGreaterThan(-1)
    const up = grab.lastIndexOf('mouse.up()', grabbed)
    expect(up, 'the last mouse.up() before the grab read').toBeGreaterThan(-1)
    expect(grab.slice(up, grabbed), 'a waitForFunction between the release and the read').toContain('waitForFunction(')
    for (const prefix of ['AC-67.20 A-6 ', 'AC-80.10:']) {
      expect(testBody(text, prefix), `${prefix} calls pointerOn`).toContain('pointerOn(')
    }
    expect(functionBody(text, 'async function dragImage(')).toContain('settledBox(')
  })
})
