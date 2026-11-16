import { expect, test, type Page } from '@playwright/test'
import { mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { launchElectron } from './electron-app'

import {
  CONSOLE_CLEAR,
  CONSOLE_EXPAND,
  CONSOLE_COPY,
  CONSOLE_FILTER,
  CONSOLE_LOG_TO_FILE,
  CONSOLE_PANEL,
  CONSOLE_SEARCH,
  CONSOLE_YTDLP_TOGGLE,
  HEADER_CONSOLE_BTN,
} from './test-ids'

async function launchApp() {
  return launchElectron({
    env: {
      AVKIT_APP_DATA: mkdtempSync(join(tmpdir(), 'avkit-e2e-')),
    },
  })
}

async function openConsole(window: Page) {
  await expect(window.getByTestId(HEADER_CONSOLE_BTN)).toBeVisible()
  await window.getByTestId(HEADER_CONSOLE_BTN).click()
  await expect(window.getByTestId(CONSOLE_PANEL)).toBeVisible()
}

test('wave5 console panel opens via header', async () => {
  const app = await launchApp()
  const window = await app.firstWindow()
  await expect(window.getByTestId(CONSOLE_PANEL)).toHaveCount(0)
  await openConsole(window)
  await app.close()
})

test('wave5 console exposes filter search clear collapse and ytdlp', async () => {
  const app = await launchApp()
  const window = await app.firstWindow()
  await openConsole(window)
  await expect(window.getByTestId(CONSOLE_FILTER)).toBeVisible()
  await expect(window.getByTestId(CONSOLE_SEARCH)).toBeVisible()
  await expect(window.getByTestId(CONSOLE_CLEAR)).toBeVisible()
  await expect(window.getByTestId(CONSOLE_EXPAND)).toBeVisible()
  await expect(window.getByTestId(CONSOLE_YTDLP_TOGGLE)).toBeVisible()
  await app.close()
})

test('wave5 console copy and log-to-file controls exist', async () => {
  const app = await launchApp()
  const window = await app.firstWindow()
  await openConsole(window)
  await expect(window.getByTestId(CONSOLE_COPY)).toBeVisible()
  await expect(window.getByTestId(CONSOLE_LOG_TO_FILE)).toBeVisible()
  await app.close()
})
