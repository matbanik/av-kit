import { _electron, expect, test } from '@playwright/test'
import { mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))

import { COMMAND_PALETTE, COMMAND_PALETTE_INPUT } from './test-ids'

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

test('wave7 palette opens from the header control', async () => {
  const app = await launchApp()
  const window = await app.firstWindow()
  await window.getByTestId('header-palette-btn').click()
  await expect(window.getByTestId(COMMAND_PALETTE)).toBeVisible()
  await expect(window.getByTestId(COMMAND_PALETTE_INPUT)).toBeVisible()
  await app.close()
})

test('wave7 palette input accepts a query', async () => {
  const app = await launchApp()
  const window = await app.firstWindow()
  await window.getByTestId('header-palette-btn').click()
  await window.getByTestId(COMMAND_PALETTE_INPUT).fill('settings')
  await expect(window.getByTestId(COMMAND_PALETTE_INPUT)).toHaveValue('settings')
  await app.close()
})

test('wave7 palette settings command changes the hash route', async () => {
  const app = await launchApp()
  const window = await app.firstWindow()
  await window.getByTestId('header-palette-btn').click()
  await window.getByTestId(COMMAND_PALETTE_INPUT).fill('settings')
  await window.getByRole('dialog').getByRole('button', { name: 'Settings' }).click()
  await expect(window).toHaveURL(/#\/settings/)
  await app.close()
})
