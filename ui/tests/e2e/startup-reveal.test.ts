import { _electron, expect, test, type ElectronApplication } from '@playwright/test'
import { mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))

/*
  Session 27 A-3 (STARTUP_RELOAD_RACE). Every e2e seam reloads right after
  firstWindow(). A reload that lands before the first load finishes aborts that
  navigation. The main process used to reveal the window only after the awaited
  loadFile resolved, inside `void boot()` with no catch, so the abort stranded a
  hidden window (Chromium throttles it to about 1 frame per second) and skipped
  the rest of boot. The reload here is deliberately immediate.
*/
async function launchAndReloadEarly(extraEnv: Record<string, string> = {}): Promise<ElectronApplication> {
  const app = await _electron.launch({
    args: [resolve(here, '../../out/main/index.js')],
    env: {
      ...process.env,
      AVKIT_E2E: '1',
      AVKIT_APP_DATA: mkdtempSync(join(tmpdir(), 'avkit-e2e-reveal-')),
      ...extraEnv,
    },
  })
  const page = await app.firstWindow()
  await page.reload()
  await page.getByTestId('app-shell').waitFor()
  return app
}

async function mainWindowVisible(app: ElectronApplication): Promise<boolean> {
  return app.evaluate(({ BrowserWindow }) => BrowserWindow.getAllWindows()[0]?.isVisible() === true)
}

test('A-3 an immediate reload after launch still reveals the main window', async () => {
  const app = await launchAndReloadEarly()
  let visible = false
  for (let tick = 0; tick < 20 && !visible; tick += 1) {
    visible = await mainWindowVisible(app)
    if (!visible) {
      await new Promise((done) => setTimeout(done, 250))
    }
  }
  expect(visible, 'main window shown after an early reload').toBe(true)
  await app.close()
})

test('A-3 an immediate reload after launch still lets boot finish its startup work', async () => {
  // The delayed E2E backend is published by the last step of boot(); it only
  // arrives if boot() survives the aborted first navigation.
  const app = await launchAndReloadEarly({ AVKIT_E2E_BACKEND_DELAY_MS: '600' })
  const page = await app.firstWindow()
  const backend = await page.evaluate(async () => {
    try {
      return await window.api.getBackendUrl()
    } catch (err) {
      return `error: ${err instanceof Error ? err.message : String(err)}`
    }
  })
  expect(backend).toBe('http://127.0.0.1:9/api/v1')
  await app.close()
})
