import { expect, test, type ElectronApplication } from '@playwright/test'
import type { ChildProcess } from 'node:child_process'
import { mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { launchElectron } from './electron-app'
import { APP_SHELL } from './test-ids'

/*
  MEU-164 (Session 102, D-1363, D-1365, D-1366): a double-click on the tray icon runs Show window.
  The built app is launched with AVKIT_E2E=1, so capture-tray.ts exposes its tray and menu as
  globalThis.__AVKIT_E2E_TRAY__ (TRAY_E2E_HOOK). The spec emits the tray's `double-click` and
  calls the Show window item through that hook, and reads and changes the window through
  app.evaluate. Every wait is a bounded poll, and afterEach closes the app within CLOSE_TIMEOUT_MS.
*/

const POLL = { timeout: 10_000 }
const SHELL_TIMEOUT_MS = 30_000
const CLOSE_TIMEOUT_MS = 30_000

type WindowState = { visible: boolean; focused: boolean; minimized: boolean }

let open: { app: ElectronApplication; child: ChildProcess } | undefined

test.afterEach(async () => {
  const running = open
  open = undefined
  if (running === undefined) return
  let timer: NodeJS.Timeout | undefined
  const timedOut = new Promise<'timeout'>((done) => {
    timer = setTimeout(() => done('timeout'), CLOSE_TIMEOUT_MS)
  })
  try {
    if ((await Promise.race([running.app.close(), timedOut])) === 'timeout') {
      running.child.kill()
    }
  } finally {
    clearTimeout(timer)
  }
})

async function launch(): Promise<ElectronApplication> {
  const app = await launchElectron({
    env: { AVKIT_APP_DATA: mkdtempSync(join(tmpdir(), 'avkit-e2e-tray-')) },
  })
  open = { app, child: app.process() }
  const page = await app.firstWindow()
  await page.getByTestId(APP_SHELL).waitFor({ timeout: SHELL_TIMEOUT_MS })
  await expect
    .poll(() => app.evaluate(() => Boolean((globalThis as Record<string, unknown>).__AVKIT_E2E_TRAY__)), {
      message: 'expect(tray hook)',
      timeout: 10_000,
    })
    .toBe(true)
  await expect.poll(() => windowState(app).then((state) => state.visible), POLL).toBe(true)
  return app
}

function windowState(app: ElectronApplication): Promise<WindowState> {
  return app.evaluate(({ BrowserWindow }) => {
    const window = BrowserWindow.getAllWindows()[0]
    return {
      visible: window?.isVisible() === true,
      focused: window?.isFocused() === true,
      minimized: window?.isMinimized() === true,
    }
  })
}

async function hide(app: ElectronApplication): Promise<void> {
  await app.evaluate(({ BrowserWindow }) => BrowserWindow.getAllWindows()[0]?.hide())
  await expect.poll(() => windowState(app).then((state) => state.visible), POLL).toBe(false)
}

function doubleClickTray(app: ElectronApplication): Promise<void> {
  return app.evaluate(() => {
    const hook = (globalThis as { __AVKIT_E2E_TRAY__?: { tray: { emit: (event: string) => boolean } } })
      .__AVKIT_E2E_TRAY__
    hook?.tray.emit('double-click')
  })
}

function clickShowWindow(app: ElectronApplication): Promise<void> {
  return app.evaluate(() => {
    type Item = { label: string; click: () => void }
    const hook = (globalThis as { __AVKIT_E2E_TRAY__?: { menu: { items: Item[] } } }).__AVKIT_E2E_TRAY__
    hook?.menu.items.find((item) => item.label === 'Show window')?.click()
  })
}

test('AC-164.4 hidden', async () => {
  const app = await launch()
  await hide(app)
  await doubleClickTray(app)
  await expect.poll(() => windowState(app), POLL).toMatchObject({ visible: true, focused: true })

  await hide(app)
  await clickShowWindow(app)
  await expect.poll(() => windowState(app).then((state) => state.visible), POLL).toBe(true)
})

test('AC-164.5 minimized', async () => {
  const app = await launch()
  await app.evaluate(({ BrowserWindow }) => BrowserWindow.getAllWindows()[0]?.minimize())
  await expect.poll(() => windowState(app).then((state) => state.minimized), POLL).toBe(true)
  await doubleClickTray(app)
  await expect.poll(() => windowState(app), POLL).toMatchObject({ minimized: false, visible: true })
})
