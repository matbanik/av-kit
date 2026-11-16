// @vitest-environment node
import { existsSync, readFileSync } from 'node:fs'
import { dirname, isAbsolute, relative, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

import { describe, expect, inject, it } from 'vitest'

const here = dirname(fileURLToPath(import.meta.url))
const ui = resolve(here, '../..')
const SETUP_PATH = resolve(here, 'global-setup.ts')
const ELECTRON_DIST = resolve(ui, 'node_modules/electron/dist')
const INSTALL_COMMAND = 'node node_modules/electron/install.js'

interface FakeProject {
  provide: (key: string, value: unknown) => void
}

interface SetupModule {
  ensureElectronBinary: (requireFn?: (id: string) => unknown, exists?: (path: string) => boolean) => string
  default: (project: FakeProject) => unknown
}

async function loadSetup(): Promise<SetupModule> {
  expect(existsSync(SETUP_PATH), 'ui/tests/unit/global-setup.ts exists').toBe(true)
  return (await import(/* @vite-ignore */ pathToFileURL(SETUP_PATH).href)) as SetupModule
}

function underElectronDist(path: string): boolean {
  const rel = relative(ELECTRON_DIST, resolve(path))
  return rel !== '' && !rel.startsWith('..') && !isAbsolute(rel)
}

describe('Session 78 Electron install', () => {
  it('AC-12 the global setup installs the binary once, names the install command, and provides the path', async () => {
    const { ensureElectronBinary, default: setup } = await loadSetup()
    const binary = resolve(ELECTRON_DIST, 'electron.exe')
    expect(ensureElectronBinary(() => binary, () => true)).toBe(binary)
    expect(() =>
      ensureElectronBinary(
        () => {
          throw new Error('download failed')
        },
        () => true,
      ),
    ).toThrow(INSTALL_COMMAND)
    expect(() => ensureElectronBinary(() => binary, () => false)).toThrow(INSTALL_COMMAND)

    const config = readFileSync(resolve(ui, 'vitest.config.ts'), 'utf8')
    expect(config).toContain("globalSetup: ['./tests/unit/global-setup.ts']")

    const calls: [string, unknown][] = []
    const result = setup({ provide: (key, value) => calls.push([key, value]) })
    expect(result).toBeUndefined()
    expect(calls).toHaveLength(1)
    const [key, path] = calls[0]
    expect(key).toBe('electronBinary')
    expect(typeof path).toBe('string')
    expect(existsSync(path as string), String(path)).toBe(true)
    expect(underElectronDist(path as string), String(path)).toBe(true)
  })

  it('AC-13 the worker receives the binary path that the global setup provided in this run', () => {
    const binary: unknown = inject('electronBinary')
    expect(typeof binary).toBe('string')
    expect(existsSync(binary as string), String(binary)).toBe(true)
    expect(underElectronDist(binary as string), String(binary)).toBe(true)
  })
})
