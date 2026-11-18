// @vitest-environment node
// Session 90: `npm run dev` runs ui/scripts/electron-vite-dev.mjs, which starts electron-vite
// without ELECTRON_RUN_AS_NODE (AC-13) and passes its arguments and exit code through (AC-14).
// The module is loaded through a dynamic import; importing it starts nothing.
import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { pathToFileURL } from 'node:url'

import { describe, expect, it } from 'vitest'

const SCRIPT = resolve(__dirname, '../../scripts/electron-vite-dev.mjs')
const PACKAGE_JSON = resolve(__dirname, '../../package.json')

type Env = Record<string, string | undefined>

interface DevModule {
  devEnv: (base: Env) => { env: Env; cleared: boolean }
  devArgs: (extra: string[]) => string[]
  isEntry: (argv1: string | undefined, moduleUrl: string) => boolean
  exitCodeFor: (code: number | null, signal: string | null, platform?: string) => number
  DEV_NOTICE: string
}

async function loadScript(): Promise<DevModule> {
  expect(existsSync(SCRIPT)).toBe(true)
  return (await import(/* @vite-ignore */ pathToFileURL(SCRIPT).href)) as DevModule
}

describe('Session 90 dev script', () => {
  it('AC-13 devEnv drops ELECTRON_RUN_AS_NODE in any case and keeps its base unchanged', async () => {
    const mod = await loadScript()
    const base: Env = { ELECTRON_RUN_AS_NODE: '1', electron_run_as_node: '1', PATH: 'p' }
    const { env, cleared } = mod.devEnv(base)
    expect(env).toEqual({ PATH: 'p' })
    expect(cleared).toBe(true)
    expect(Object.keys(base)).toHaveLength(3)
    expect(mod.devEnv({ PATH: 'p' }).cleared).toBe(false)
    expect(mod.DEV_NOTICE).toBe('electron-vite-dev: cleared ELECTRON_RUN_AS_NODE')
  })

  it('AC-14 devArgs, isEntry, exitCodeFor and the package scripts', async () => {
    const mod = await loadScript()
    const args = mod.devArgs(['--x'])
    expect(args).toHaveLength(3)
    expect(args.slice(1)).toEqual(['dev', '--x'])
    expect(existsSync(args[0])).toBe(true)
    expect(args[0].replace(/\\/g, '/')).toMatch(/electron-vite\/bin\/electron-vite\.js$/)

    const url = pathToFileURL(SCRIPT).href
    expect(mod.isEntry(SCRIPT, url)).toBe(true)
    if (process.platform === 'win32') expect(mod.isEntry(SCRIPT.toUpperCase(), url)).toBe(true)
    expect(mod.isEntry(PACKAGE_JSON, url)).toBe(false)
    expect(mod.isEntry(undefined, url)).toBe(false)

    expect(mod.exitCodeFor(0, null)).toBe(0)
    expect(mod.exitCodeFor(3, null)).toBe(3)
    expect(mod.exitCodeFor(null, 'SIGTERM', 'win32')).toBe(1)
    expect(mod.exitCodeFor(null, null, 'win32')).toBe(1)
    expect(mod.exitCodeFor(null, 'SIGINT', 'linux')).toBe(130)
    expect(mod.exitCodeFor(null, null, 'linux')).toBe(1)

    const pkg = JSON.parse(readFileSync(PACKAGE_JSON, 'utf8')) as { scripts: Record<string, string> }
    expect(pkg.scripts.dev).toBe('node ./scripts/electron-vite-dev.mjs')
    expect(pkg.scripts.preview).toBe('node ./scripts/electron-vite-preview.mjs')
  })
})
