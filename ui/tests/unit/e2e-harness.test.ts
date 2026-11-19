// @vitest-environment node
import { spawnSync } from 'node:child_process'
import { existsSync, mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

import { describe, expect, it } from 'vitest'

const here = dirname(fileURLToPath(import.meta.url))
const e2eDir = resolve(here, '../e2e')
const ENV_PATH = resolve(e2eDir, 'electron-env.ts')
const APP_PATH = resolve(e2eDir, 'electron-app.ts')
const WATCH_PATH = resolve(e2eDir, 'main-error-watch.cjs')
// Built from parts so that this file never holds the launch call's text itself.
const LAUNCH_CALL = ['_electron', 'launch('].join('.')
const PLAYWRIGHT_ELECTRON = '_electron'

type Env = Record<string, string | undefined>

interface MainErrorRecord {
  name?: string
  message?: string
  stack?: string
  raw?: string
}

interface EnvModule {
  electronEnv: (base?: Env, extra?: Env) => Record<string, string>
  mainErrorRecords: (text: string) => MainErrorRecord[]
  requireScratchAppData: (env?: Env) => string
  MAIN_ERROR_LOG_ENV: string
  MAIN_ERROR_MARKER: string
  MAIN_ERROR_WATCH: string
}

async function loadEnv(): Promise<EnvModule> {
  expect(existsSync(ENV_PATH), 'ui/tests/e2e/electron-env.ts exists').toBe(true)
  return (await import(/* @vite-ignore */ pathToFileURL(ENV_PATH).href)) as EnvModule
}

function count(text: string, needle: string): number {
  return text.split(needle).length - 1
}

describe('Session 78 E2E harness', () => {
  it('AC-1 electronEnv drops ELECTRON_RUN_AS_NODE after the merge and keeps its base unchanged', async () => {
    const { electronEnv } = await loadEnv()
    const base: Env = { ELECTRON_RUN_AS_NODE: '1', KEEP: 'k', GONE: undefined }
    const before = { ...base }
    const env = electronEnv(base, { ELECTRON_RUN_AS_NODE: '1', EXTRA: 'e' })
    expect(Object.keys(env)).not.toContain('ELECTRON_RUN_AS_NODE')
    expect(env.AVKIT_E2E).toBe('1')
    expect(env.KEEP).toBe('k')
    expect(env.EXTRA).toBe('e')
    expect(Object.keys(env)).not.toContain('GONE')
    expect(base).toStrictEqual(before)
  })

  it('AC-2 only electron-app.ts names the Playwright Electron launcher, once', () => {
    const files = readdirSync(e2eDir).filter((name) => name.endsWith('.ts') || name.endsWith('.cjs'))
    const texts = new Map(files.map((name) => [name, readFileSync(resolve(e2eDir, name), 'utf8')]))
    const holders = files.filter((name) => (texts.get(name) ?? '').includes(PLAYWRIGHT_ELECTRON)).sort()
    expect(holders, 'files under ui/tests/e2e that name the Playwright Electron launcher').toEqual(['electron-app.ts'])
    expect(count(texts.get('electron-app.ts') ?? '', LAUNCH_CALL), 'launch calls in electron-app.ts').toBe(1)
    expect(count(texts.get('electron-env.ts') ?? '', '...process.env'), 'process.env spreads in electron-env.ts').toBeLessThanOrEqual(1)
  })

  it('AC-3 the watch keeps a process alive on an uncaught exception and logs its full record', async () => {
    expect(existsSync(WATCH_PATH), 'ui/tests/e2e/main-error-watch.cjs exists').toBe(true)
    const { MAIN_ERROR_LOG_ENV, MAIN_ERROR_MARKER, MAIN_ERROR_WATCH } = await loadEnv()
    const dir = mkdtempSync(join(tmpdir(), 'avkit-ac3-'))
    try {
      const thrower = join(dir, 'thrower.cjs')
      const log = join(dir, 'errors.jsonl')
      writeFileSync(
        thrower,
        [
          `process.stdout.write(String(process.env[${JSON.stringify(MAIN_ERROR_LOG_ENV)}] === undefined) + '\\n')`,
          "setTimeout(() => { throw new Error('avkit-ac3-probe') })",
          "setTimeout(() => { process.stdout.write('alive\\n') }, 50)",
          '',
        ].join('\n'),
      )
      const plainEnv: Env = { ...process.env }
      delete plainEnv[MAIN_ERROR_LOG_ENV]
      const plain = spawnSync(process.execPath, [thrower], { env: plainEnv, encoding: 'utf8', timeout: 15_000 })
      expect(plain.status, 'exit code without the watch').not.toBe(0)
      expect(plain.stdout, 'stdout without the watch').not.toContain('alive')

      const watched = spawnSync(process.execPath, ['-r', MAIN_ERROR_WATCH, thrower], {
        env: { ...process.env, [MAIN_ERROR_LOG_ENV]: log },
        encoding: 'utf8',
        timeout: 15_000,
      })
      expect(watched.status, 'exit code with the watch').toBe(0)
      expect(watched.stdout, 'stdout with the watch').toContain('true')
      expect(watched.stdout, 'stdout with the watch').toContain('alive')
      expect(watched.stderr, 'stderr with the watch').toContain(MAIN_ERROR_MARKER)

      const lines = readFileSync(log, 'utf8').split('\n').filter((line) => line !== '')
      expect(lines, 'log lines').toHaveLength(1)
      const record = JSON.parse(lines[0]) as MainErrorRecord
      expect(record.message).toBe('avkit-ac3-probe')
      expect(record.stack).toContain('thrower.cjs')
      expect(record.stack).toContain('\n    at ')
    } finally {
      rmSync(dir, { recursive: true, force: true })
    }
  })

  it('AC-4 mainErrorRecords keeps every non-empty line, multi-line stacks included', async () => {
    const { mainErrorRecords } = await loadEnv()
    const a = { name: 'Error', message: 'a', stack: 'Error: a\n    at f (x.js:1:1)\n    at g (y.js:2:2)' }
    const b = { name: 'TypeError', message: 'b', stack: 'TypeError: b\n    at h (z.js:3:3)\n    at k (w.js:4:4)' }
    const text = [JSON.stringify(a), '', JSON.stringify(b), 'not json', ''].join('\n')
    expect(mainErrorRecords(text)).toEqual([a, b, { raw: 'not json' }])
    expect(mainErrorRecords('')).toEqual([])
  })

  it('AC-19 requireScratchAppData accepts only a folder inside tmpdir(), and the launcher asks it first', async () => {
    const { requireScratchAppData } = await loadEnv()
    const scratch = join(tmpdir(), 'avkit-ac19')
    expect(requireScratchAppData({ AVKIT_APP_DATA: scratch })).toBe(scratch)
    for (const env of [{}, { AVKIT_APP_DATA: '' }, { AVKIT_APP_DATA: tmpdir() }, { AVKIT_APP_DATA: resolve(tmpdir(), '..', 'av-kit-ac19') }]) {
      expect(() => requireScratchAppData(env), JSON.stringify(env)).toThrow('scratch AVKIT_APP_DATA')
    }
    expect(existsSync(APP_PATH), 'ui/tests/e2e/electron-app.ts exists').toBe(true)
    const app = readFileSync(APP_PATH, 'utf8')
    expect(count(app, 'requireScratchAppData(env'), 'requireScratchAppData(env calls').toBe(1)
    const launchAt = app.indexOf(LAUNCH_CALL)
    expect(launchAt, 'the launch call in electron-app.ts').toBeGreaterThan(-1)
    expect(app.indexOf('requireScratchAppData(env'), 'the scratch check comes before the launch call').toBeLessThan(launchAt)
  })
})

describe('Session 97 host parity', () => {
  const TEXT_FILE = /\.(ts|cjs|mjs|js|json)$/
  const e2eText = (name: string): string => readFileSync(resolve(e2eDir, name), 'utf8')
  const span = (text: string, start: string, end: string): string => {
    const from = text.indexOf(start)
    if (from < 0) return ''
    const to = text.indexOf(end, from)
    return to < 0 ? text.slice(from) : text.slice(from, to)
  }
  const lineHolding = (text: string, needle: string): string =>
    text.split(/\r?\n/).find((line) => line.includes(needle)) ?? ''
  const othersHolding = (needle: string, owner: string): string[] =>
    (readdirSync(e2eDir, { recursive: true }) as string[])
      .filter((name) => TEXT_FILE.test(name) && name !== owner)
      .filter((name) => e2eText(name).includes(needle))
      .sort()

  it('AC-161.8 FIDELITY_FRAME the three fidelity specs launch at a device scale of 1, and only they', () => {
    const app = readFileSync(APP_PATH, 'utf8')
    const options = span(app, 'export interface LaunchOptions', '\n}')
    expect(options.includes('args?: readonly string[]'), 'LaunchOptions declares args?: readonly string[]').toBe(true)
    expect(count(app, 'main ?? DEFAULT_MAIN, ...(args ?? [])'), 'the args spread after the main entry').toBe(1)

    const inbox = e2eText('capture-inbox.test.ts')
    const flag = "'--force-device-scale-factor=1'"
    expect(count(inbox, flag), 'the device-scale flag in capture-inbox.test.ts').toBe(1)
    expect(lineHolding(inbox, flag).startsWith('const FIDELITY_ARGS = ['), 'the flag sits in FIDELITY_ARGS').toBe(true)
    expect(count(inbox, 'launchApp(FIDELITY_ARGS)'), 'launchApp(FIDELITY_ARGS) calls').toBe(2)
    const oracle = span(inbox, "test('AC-82.6 TEXT_PIXEL_ORACLE", '\n})')
    expect(count(oracle, 'launchApp(FIDELITY_ARGS)'), 'launchApp(FIDELITY_ARGS) in AC-82.6').toBe(1)
    const views = span(inbox, 'async function fidelityViews(', '\n}')
    expect(count(views, 'launchApp(FIDELITY_ARGS)'), 'launchApp(FIDELITY_ARGS) in fidelityViews').toBe(1)
    expect(othersHolding('force-device-scale-factor', 'capture-inbox.test.ts'), 'other e2e files with the flag').toEqual([])
  })

  it('AC-161.9 HOVER_CAPABLE AC-126.8 states a mouse-capable device and checks it before the hover', () => {
    const settings = e2eText('settings.test.ts')
    const capable = '--blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4'
    expect(count(settings, capable), 'the capable blink settings in settings.test.ts').toBe(1)
    expect(lineHolding(settings, capable).startsWith('const HOVER_CAPABLE_ARGS = ['), 'they sit in HOVER_CAPABLE_ARGS').toBe(true)
    expect(count(settings, 'launchApp(HOVER_CAPABLE_ARGS)'), 'launchApp(HOVER_CAPABLE_ARGS) calls').toBe(1)

    const test = span(settings, "test('AC-126.8 light accent paints the ruled colours'", '\n})')
    const launchAt = test.indexOf('launchApp(HOVER_CAPABLE_ARGS)')
    expect(launchAt, 'launchApp(HOVER_CAPABLE_ARGS) in AC-126.8').toBeGreaterThan(-1)
    const precondition = lineHolding(test, "matchMedia('(hover: hover)')")
    expect(precondition.includes('expect('), 'the hover precondition is an expect').toBe(true)
    expect(precondition.trimEnd().endsWith('.toBe(true)'), 'the hover precondition ends .toBe(true)').toBe(true)
    const hoverAt = test.indexOf('.hover(')
    expect(hoverAt, 'the hover in AC-126.8').toBeGreaterThan(-1)
    expect(test.indexOf(precondition), 'the precondition comes before the first hover').toBeLessThan(hoverAt)
    const colourAt = test.indexOf("toHaveCSS('background-color', 'rgb(22, 78, 99)')")
    expect(colourAt, 'the hover colour assertion after the launch').toBeGreaterThan(launchAt)
    const between = test.slice(launchAt, colourAt).split(/\r?\n/)
    const exits = between.filter((line) => /^\s*return\b/.test(line) || /test\.(skip|fixme)/.test(line))
    expect(exits, 'a return, skip or fixme call between the launch and the colour').toEqual([])
    expect(othersHolding('blink-settings', 'settings.test.ts'), 'other e2e files with blink settings').toEqual([])
  })
})
