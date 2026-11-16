// Session 78: the shared Electron launch path (electron-app.ts). Each test launches with its own
// scratch AVKIT_APP_DATA and checks that the app's profile and session storage stay in it (AC-19).
import { existsSync, mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

import { expect, test, type ElectronApplication } from '@playwright/test'

const here = dirname(fileURLToPath(import.meta.url))
const APP_PATH = resolve(here, 'electron-app.ts')
const STARTUP_MAIN = resolve(here, 'fixtures/startup-throw-main.mjs')

type Launch = (options?: { main?: string; env?: Record<string, string | undefined> }) => Promise<ElectronApplication>

async function loadLaunch(): Promise<Launch> {
  // No custom message: red-check.py reads a Playwright diagnostic only as `Error: expect(`.
  expect(existsSync(APP_PATH)).toBe(true)
  const mod = (await import(/* @vite-ignore */ pathToFileURL(APP_PATH).href)) as { launchElectron: Launch }
  return mod.launchElectron
}

function scratch(): string {
  return mkdtempSync(join(tmpdir(), 'avkit-e2e-harness-'))
}

function profilePaths(app: ElectronApplication): Promise<string[]> {
  return app.evaluate(({ app: electronApp }) => [electronApp.getPath('userData'), electronApp.getPath('sessionData')])
}

test('AC-5 the launch drops ELECTRON_RUN_AS_NODE that the worker has set', async () => {
  const launchElectron = await loadLaunch()
  const before = process.env.ELECTRON_RUN_AS_NODE
  let app: ElectronApplication | undefined
  try {
    process.env.ELECTRON_RUN_AS_NODE = '1'
    const dir = scratch()
    app = await launchElectron({ env: { AVKIT_APP_DATA: dir } })
    const window = await app.firstWindow()
    await window.waitForLoadState('domcontentloaded')
    expect(await app.evaluate(() => process.env.ELECTRON_RUN_AS_NODE)).toBeUndefined()
    expect(await profilePaths(app)).toEqual([dir, dir])
  } finally {
    if (before === undefined) delete process.env.ELECTRON_RUN_AS_NODE
    else process.env.ELECTRON_RUN_AS_NODE = before
    await app?.close()
  }
})

test('AC-6 the main-error watch is loaded before main', async () => {
  const launchElectron = await loadLaunch()
  let app: ElectronApplication | undefined
  try {
    const dir = scratch()
    app = await launchElectron({ env: { AVKIT_APP_DATA: dir } })
    const [watch, listeners] = await app.evaluate(() => [
      (globalThis as Record<string, unknown>).__avkitE2eMainErrorWatch,
      process.listenerCount('uncaughtException'),
    ])
    expect(watch).toBe(true)
    expect(listeners).toBeGreaterThanOrEqual(2)
    await app.firstWindow()
    expect(await profilePaths(app)).toEqual([dir, dir])
  } finally {
    await app?.close()
  }
})

test('AC-7 after launch an uncaught main-process exception fails the close with its stack', async () => {
  const launchElectron = await loadLaunch()
  const dir = scratch()
  const app = await launchElectron({ env: { AVKIT_APP_DATA: dir } })
  try {
    await app.firstWindow()
    expect(await profilePaths(app)).toEqual([dir, dir])
    await app.evaluate(() => {
      setTimeout(() => {
        throw new Error('avkit-e2e-probe')
      })
    })
    await expect
      .poll(() => app.evaluate(() => ((globalThis as Record<string, unknown>).__avkitE2eMainErrors as unknown[]).length))
      .toBe(1)
    const error = await app.close().then(
      () => null,
      (e: unknown) => e,
    )
    expect(error).toBeInstanceOf(Error)
    expect((error as Error).message).toMatch(/avkit-e2e-probe/)
    expect((error as Error).message).toMatch(/\n\s+at /)
  } finally {
    // close() is memoized: this returns the same settled promise, or closes after an early failure.
    await app.close().catch(() => undefined)
  }
})

test('AC-7 during startup an uncaught main-process exception fails the close with its stack', async () => {
  const launchElectron = await loadLaunch()
  const dir = scratch()
  const app = await launchElectron({ main: STARTUP_MAIN, env: { AVKIT_APP_DATA: dir } })
  try {
    await app.firstWindow()
    expect(await profilePaths(app)).toEqual([join(dir, 'user-data'), join(dir, 'session-data')])
    const error = await app.close().then(
      () => null,
      (e: unknown) => e,
    )
    expect(error).toBeInstanceOf(Error)
    expect((error as Error).message).toContain('avkit-e2e-startup-probe')
    expect((error as Error).message).toContain('startup-throw-main.mjs')
  } finally {
    // close() is memoized: this returns the same settled promise, or closes after an early failure.
    await app.close().catch(() => undefined)
  }
})

test('AC-8 a launch without a main-process error closes cleanly', async () => {
  const launchElectron = await loadLaunch()
  let app: ElectronApplication | undefined
  try {
    const dir = scratch()
    app = await launchElectron({ env: { AVKIT_APP_DATA: dir } })
    await app.firstWindow()
    expect(await profilePaths(app)).toEqual([dir, dir])
    await expect(app.close()).resolves.toBeUndefined()
  } finally {
    await app?.close()
  }
})
