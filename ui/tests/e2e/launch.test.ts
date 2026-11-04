import { _electron, expect, test } from '@playwright/test'
import { mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))

import {
  NAV_COLLAPSE,
  NAV_DOWNLOADER,
  NAV_SETTINGS,
  NAV_TRANSCRIPT,
  NAV_TTS,
} from './test-ids'

async function launchApp() {
  return _electron.launch({
    args: [resolve(here, '../../out/main/index.js')],
    env: {
      ...process.env,
      AVKIT_E2E: '1',
      AVKIT_APP_DATA: mkdtempSync(join(tmpdir(), 'avkit-e2e-')),
    },
  })
}

test('wave0 shows the nav rail testids', async () => {
  const app = await launchApp()
  const window = await app.firstWindow()
  await expect(window.getByTestId(NAV_DOWNLOADER)).toBeVisible()
  await expect(window.getByTestId(NAV_TRANSCRIPT)).toBeVisible()
  await expect(window.getByTestId(NAV_TTS)).toBeVisible()
  await expect(window.getByTestId('nav-convert')).toBeVisible()
  await expect(window.getByTestId('nav-capture')).toBeVisible()
  await expect(window.getByTestId(NAV_SETTINGS)).toBeVisible()
  await expect(window.getByTestId(NAV_COLLAPSE)).toBeVisible()
  await app.close()
})

test('wave0 home is DOWNLOADER_HOME with url-input', async () => {
  const app = await launchApp()
  const window = await app.firstWindow()
  await expect(window.getByTestId('url-input')).toBeVisible()
  await app.close()
})

test('wave0 hash history stays on the shell home', async () => {
  const app = await launchApp()
  const window = await app.firstWindow()
  await expect(window).toHaveURL(/#\/?$|#\/$/)
  await app.close()
})

test('wave0 transcript rail changes the hash route', async () => {
  const app = await launchApp()
  const window = await app.firstWindow()
  await window.getByTestId(NAV_TRANSCRIPT).click()
  await expect(window).toHaveURL(/#\/transcript/)
  await app.close()
})
