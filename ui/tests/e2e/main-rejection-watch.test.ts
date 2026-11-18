// Session 90: an unhandled promise rejection in the E2E main process is recorded by the
// main-error watch and fails the wrapped close() with its stack (AC-9); a handled rejection
// leaves no record (AC-10); and stderr still carries the UnhandledPromiseRejectionWarning line
// that capture-inbox.test.ts reads (AC-11). Each test launches with its own scratch AVKIT_APP_DATA.
import { existsSync, mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

import { expect, test, type ElectronApplication } from '@playwright/test'

const here = dirname(fileURLToPath(import.meta.url))
const APP_PATH = resolve(here, 'electron-app.ts')
const PROBE_WARNING = 'UnhandledPromiseRejectionWarning: Error: avkit-e2e-rejection-probe'

type Launch = (options?: { main?: string; env?: Record<string, string | undefined> }) => Promise<ElectronApplication>

async function loadLaunch(): Promise<Launch> {
  // No custom message: red-check.py reads a Playwright diagnostic only as `Error: expect(`.
  expect(existsSync(APP_PATH)).toBe(true)
  const mod = (await import(/* @vite-ignore */ pathToFileURL(APP_PATH).href)) as { launchElectron: Launch }
  return mod.launchElectron
}

function scratch(): string {
  return mkdtempSync(join(tmpdir(), 'avkit-e2e-rejection-'))
}

function pause(ms: number): Promise<void> {
  return new Promise((done) => setTimeout(done, ms))
}

function rejectionCount(app: ElectronApplication): Promise<number> {
  return app.evaluate(
    () => ((globalThis as Record<string, unknown>).__avkitE2eMainRejections as unknown[] | undefined)?.length ?? 0,
  )
}

function rejectSoon(app: ElectronApplication): Promise<void> {
  return app.evaluate(() => {
    setTimeout(() => {
      void Promise.reject(new Error('avkit-e2e-rejection-probe'))
    })
  })
}

test('AC-9 an unhandled main-process rejection is recorded and fails the close with its stack', async () => {
  const launchElectron = await loadLaunch()
  const app = await launchElectron({ env: { AVKIT_APP_DATA: scratch() } })
  try {
    await app.firstWindow()
    const child = app.process()
    await rejectSoon(app)
    let count = 0
    const deadline = Date.now() + 5_000
    while (Date.now() < deadline) {
      count = await rejectionCount(app)
      if (count > 0) break
      await pause(10)
    }
    expect(count).toBe(1)
    expect(child.exitCode).toBeNull()
    const error = await app.close().then(
      () => null,
      (e: unknown) => e,
    )
    expect(error).toBeInstanceOf(Error)
    expect((error as Error).message).toContain('unhandled rejection: Error: avkit-e2e-rejection-probe')
    expect((error as Error).message).toMatch(/\n\s+at /)
  } finally {
    // close() is memoized: this returns the same settled promise, or closes after an early failure.
    await app.close().catch(() => undefined)
  }
})

test('AC-10 a handled main-process rejection leaves no record and the close resolves', async () => {
  const launchElectron = await loadLaunch()
  const app = await launchElectron({ env: { AVKIT_APP_DATA: scratch() } })
  try {
    await app.firstWindow()
    await app.evaluate(() => {
      setTimeout(() => {
        const p = Promise.reject(new Error('avkit-e2e-handled'))
        p.catch(() => undefined)
      })
    })
    await pause(1_000)
    expect(await rejectionCount(app)).toBe(0)
    await expect(app.close()).resolves.toBeUndefined()
  } finally {
    await app.close().catch(() => undefined)
  }
})

test('AC-11 an unhandled main-process rejection still writes the warning line to stderr', async () => {
  const launchElectron = await loadLaunch()
  const app = await launchElectron({ env: { AVKIT_APP_DATA: scratch() } })
  let stderr = ''
  app.process().stderr?.on('data', (chunk: Buffer | string) => {
    stderr += chunk.toString()
  })
  try {
    await app.firstWindow()
    await rejectSoon(app)
    const deadline = Date.now() + 30_000
    while (Date.now() < deadline && !stderr.includes(PROBE_WARNING)) {
      await pause(50)
    }
    expect(stderr).toContain(PROBE_WARNING)
  } finally {
    // The close fails on the recorded rejection once the watch records it; that is AC-9's check.
    await app.close().catch(() => undefined)
  }
})
