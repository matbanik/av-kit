// Session 100 (docs/execution/plans/2026-11-20-e2e-devpc-clipboard; D-1313, D-1320, D-1323): a
// launch without AVKIT_E2E_CLIPBOARD_GATED=1 runs with the clipboard guard preloaded
// (clipboard-guard.cjs). This spec makes three clipboard calls, one in main, one in the page and
// one native webContents copy, and expects the wrapped close() to fail naming all three. Each call
// sits in its own evaluate whose first statement throws unless that exact function carries the
// guard's tag, so even before the guard exists no call can reach the system clipboard.
import { mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { expect, test } from '@playwright/test'

import { launchElectron } from './electron-app'

// The gated stage runs unguarded, so this spec has nothing to prove there.
test.skip(process.env.AVKIT_E2E_CLIPBOARD_GATED === '1', 'the clipboard guard is off in the gated stage')

// Built from parts, so neither this file's titles nor its output carry the guard's message prefix.
const PREFIX = ['CLIPBOARD', 'GUARD:'].join('_')
const MAIN_CALL = 'main writeText'
const RENDERER_CALL = 'renderer writeText'
const NATIVE_CALL = 'webContents copy'

test('S100 AC-10 a guarded launch records main, renderer and webContents clipboard calls and fails at close with a named message', async () => {
  const app = await launchElectron({ env: { AVKIT_APP_DATA: mkdtempSync(join(tmpdir(), 'avkit-e2e-clipboard-guard-')) } })
  try {
    expect(await app.evaluate(() => (globalThis as Record<string, unknown>).__avkitClipboardGuard === true)).toBe(true)
    const page = await app.firstWindow()
    await expect
      .poll(() => page.evaluate(() => (globalThis as Record<string, unknown>).__avkitClipboardGuard === true), { timeout: 10_000 })
      .toBe(true)

    await app.evaluate(({ clipboard }) => {
      if (Reflect.get(clipboard.writeText, '__avkitClipboardGuard') !== true) throw new Error('main writeText is not the guard recorder')
      clipboard.writeText('avkit-s100-main')
    })
    await page.evaluate(() => {
      if (Reflect.get(navigator.clipboard.writeText, '__avkitClipboardGuard') !== true) throw new Error('page writeText is not the guard recorder')
      return navigator.clipboard.writeText('avkit-s100-renderer')
    })
    await app.evaluate(({ BrowserWindow }) => {
      const wc = BrowserWindow.getAllWindows()[0].webContents
      if (Reflect.get(wc.copy, '__avkitClipboardGuard') !== true) throw new Error('webContents copy is not the guard recorder')
      wc.copy()
    })

    await expect
      .poll(
        () => app.evaluate(() => [...(((globalThis as Record<string, unknown>).__avkitClipboardGuardCalls as string[] | undefined) ?? [])]),
        { timeout: 10_000 },
      )
      .toEqual(expect.arrayContaining([MAIN_CALL, RENDERER_CALL, NATIVE_CALL]))

    const error = await app.close().then(
      () => null,
      (e: unknown) => e,
    )
    expect(error).toBeInstanceOf(Error)
    const message = (error as Error).message
    const parts = [PREFIX, MAIN_CALL, RENDERER_CALL, NATIVE_CALL]
    parts.forEach((part, i) => expect(message.includes(part), 'the close message names part ' + i).toBe(true))
  } finally {
    // close() is memoized: this returns the same settled promise, or closes after an early failure.
    await app.close().catch(() => undefined)
  }
})
