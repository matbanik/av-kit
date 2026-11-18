// @vitest-environment node
// Session 94 (D-1178, PREVIEW_WRAPPER): `npm run preview` runs ui/scripts/electron-vite-preview.mjs,
// which starts `electron-vite preview` without ELECTRON_RUN_AS_NODE through the dev script's
// runElectronVite (AC-1, AC-2). Both modules are loaded through a dynamic import while
// `child_process.spawn` is mocked and counts its calls, so the test sees that importing them
// starts nothing.
import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { pathToFileURL } from 'node:url'

import { describe, expect, it, vi } from 'vitest'

const spawnCalls = vi.hoisted(() => ({ count: 0 }))

vi.mock('node:child_process', async (importOriginal) => {
  const actual = await importOriginal<Record<string, unknown>>()
  const spawn = () => {
    spawnCalls.count += 1
    const child = {
      on: () => child,
      kill: () => true,
    }
    return child
  }
  return { ...actual, spawn, default: { ...(actual.default as object), spawn } }
})

const DEV_SCRIPT = resolve(__dirname, '../../scripts/electron-vite-dev.mjs')
const PREVIEW_SCRIPT = resolve(__dirname, '../../scripts/electron-vite-preview.mjs')
const PACKAGE_JSON = resolve(__dirname, '../../package.json')

interface DevModule {
  devArgs: (extra: string[]) => string[]
  runElectronVite: (command: string, notice: string, extra: string[]) => void
}

interface PreviewModule {
  PREVIEW_NOTICE: string
  previewArgs: (extra: string[]) => string[]
}

describe('Session 94 preview script', () => {
  it('AC-1 the preview script exists, names its notice and arguments, and importing it starts nothing', async () => {
    expect(existsSync(PREVIEW_SCRIPT)).toBe(true)
    const dev = (await import(/* @vite-ignore */ pathToFileURL(DEV_SCRIPT).href)) as DevModule
    expect(typeof dev.runElectronVite).toBe('function')
    const preview = (await import(
      /* @vite-ignore */ pathToFileURL(PREVIEW_SCRIPT).href
    )) as PreviewModule
    expect(preview.PREVIEW_NOTICE).toBe('electron-vite-preview: cleared ELECTRON_RUN_AS_NODE')
    const args = preview.previewArgs(['--x'])
    expect(args).toEqual([dev.devArgs([])[0], 'preview', '--x'])
    expect(existsSync(args[0])).toBe(true)
    expect(spawnCalls.count).toBe(0)
  })

  it('AC-2 the package preview script runs the wrapper and the dev script is unchanged', () => {
    const pkg = JSON.parse(readFileSync(PACKAGE_JSON, 'utf8')) as { scripts: Record<string, string> }
    expect(pkg.scripts.preview).toBe('node ./scripts/electron-vite-preview.mjs')
    expect(pkg.scripts.dev).toBe('node ./scripts/electron-vite-dev.mjs')
  })
})
