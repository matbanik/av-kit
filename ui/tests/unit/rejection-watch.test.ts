// @vitest-environment node
// Session 90: the main-error watch (ui/tests/e2e/main-error-watch.cjs) also records unhandled
// promise rejections (AC-6, AC-7) and keeps its uncaught-exception record as it was (AC-8). Each
// test runs a small Node child with the watch preloaded, as Electron runs it in the E2E suite.
import { spawnSync } from 'node:child_process'
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

import { describe, expect, it } from 'vitest'

const here = dirname(fileURLToPath(import.meta.url))
const ENV_PATH = resolve(here, '../e2e/electron-env.ts')

interface EnvModule {
  MAIN_ERROR_LOG_ENV: string
  MAIN_ERROR_MARKER: string
  MAIN_ERROR_WATCH: string
  MAIN_REJECTION_MARKER?: unknown
}

interface Child {
  status: number | null
  stdout: string
  stderr: string
  records: Record<string, unknown>[]
}

async function loadEnv(): Promise<EnvModule> {
  expect(existsSync(ENV_PATH), 'ui/tests/e2e/electron-env.ts exists').toBe(true)
  return (await import(/* @vite-ignore */ pathToFileURL(ENV_PATH).href)) as EnvModule
}

/** Runs `lines` as a .cjs script under the watch, the way launchElectron preloads it. */
function runWatched(mod: EnvModule, name: string, lines: string[]): Child {
  const dir = mkdtempSync(join(tmpdir(), 'avkit-rejection-watch-'))
  try {
    const script = join(dir, name)
    const log = join(dir, 'errors.jsonl')
    writeFileSync(script, [...lines, ''].join('\n'))
    const child = spawnSync(
      process.execPath,
      ['--unhandled-rejections=warn-with-error-code', '-r', mod.MAIN_ERROR_WATCH, script],
      { env: { ...process.env, [mod.MAIN_ERROR_LOG_ENV]: log }, encoding: 'utf8', timeout: 15_000 },
    )
    const text = existsSync(log) ? readFileSync(log, 'utf8') : ''
    const records = text
      .split('\n')
      .filter((line) => line !== '')
      .map((line) => JSON.parse(line) as Record<string, unknown>)
    return { status: child.status, stdout: child.stdout, stderr: child.stderr, records }
  } finally {
    rmSync(dir, { recursive: true, force: true })
  }
}

describe('Session 90 main-process rejection watch', () => {
  it('AC-6 an unhandled rejection is recorded with its stack and the process lives on', async () => {
    const mod = await loadEnv()
    expect(typeof mod.MAIN_REJECTION_MARKER).toBe('string')
    const child = runWatched(mod, 'rejector.cjs', [
      "Promise.reject(new Error('avkit-ac6-probe'))",
      "setTimeout(() => { process.stdout.write('alive\\n') }, 50)",
    ])
    expect(child.status).toBe(0)
    expect(child.stdout).toContain('alive')
    expect(child.stderr).toContain(String(mod.MAIN_REJECTION_MARKER))
    expect(child.stderr).toContain('UnhandledPromiseRejectionWarning: Error: avkit-ac6-probe')
    expect(child.records).toHaveLength(1)
    const [record] = child.records
    expect(record).toEqual({ kind: 'rejection', name: 'Error', message: 'avkit-ac6-probe', stack: expect.any(String) })
    expect(record.stack).toContain('rejector.cjs')
    expect(record.stack).toContain('\n    at ')
  })

  it('AC-7 a rejection with a string reason is recorded as that string', async () => {
    const mod = await loadEnv()
    expect(typeof mod.MAIN_REJECTION_MARKER).toBe('string')
    const child = runWatched(mod, 'rejector.cjs', [
      "Promise.reject('avkit-ac7-text')",
      "setTimeout(() => { process.stdout.write('alive\\n') }, 50)",
    ])
    expect(child.records).toEqual([
      { kind: 'rejection', name: 'string', message: 'avkit-ac7-text', stack: 'avkit-ac7-text' },
    ])
  })

  it('AC-8 an uncaught exception keeps its record without a kind and its stderr marker', async () => {
    const mod = await loadEnv()
    const child = runWatched(mod, 'thrower.cjs', [
      "setTimeout(() => { throw new Error('avkit-ac8-probe') })",
      "setTimeout(() => { process.stdout.write('alive\\n') }, 50)",
    ])
    expect(child.records).toHaveLength(1)
    expect(Object.keys(child.records[0]).sort()).toEqual(['message', 'name', 'stack'])
    expect(child.records[0].message).toBe('avkit-ac8-probe')
    expect(child.stderr).toContain(mod.MAIN_ERROR_MARKER + ' Error: avkit-ac8-probe')
  })
})
