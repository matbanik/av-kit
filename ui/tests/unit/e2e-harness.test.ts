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
