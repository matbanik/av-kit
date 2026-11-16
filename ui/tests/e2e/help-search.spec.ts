import { expect, test } from '@playwright/test'
import { mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { launchElectron } from './electron-app'

async function launchApp() {
  return launchElectron({
    env: {
      AVKIT_APP_DATA: mkdtempSync(join(tmpdir(), 'avkit-e2e-help-')),
    },
  })
}

test('W6-1 help-card visible on downloader after mount', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await page.getByTestId('app-shell').waitFor()
  await expect(page.getByTestId('downloader-page')).toBeVisible()
  await expect(page.getByTestId('help-card')).toBeVisible()
  await app.close()
})

test('W6-2 help-search fill filters visible section count', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await page.getByTestId('app-shell').waitFor()
  await expect(page.getByTestId('help-card')).toBeVisible()
  // The card is collapsed on first visit — expand it before searching.
  await page.getByTestId('help-card').locator('button').first().click()
  const before = await page.locator('[data-help-section]').count()
  expect(before).toBeGreaterThan(0)
  await page.getByTestId('help-search').fill('SABR')
  const after = await page.locator('[data-help-section]:visible').count()
  expect(after).toBeLessThan(before)
  await app.close()
})

test('W6-3 off-route help:toggle navigates then expands Settings HelpCard', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await page.getByTestId('app-shell').waitFor()
  await page.evaluate(() => {
    localStorage.setItem('av-kit:settings-help:main:state', 'collapsed')
    window.location.hash = '/no-such-route'
  })
  await page.waitForFunction(() => {
    const hash = window.location.hash.replace(/^#/, '') || '/'
    return hash.split('?')[0] === '/no-such-route'
  })
  await page.evaluate(() => {
    window.dispatchEvent(new CustomEvent('av-kit:help:toggle'))
  })
  await expect(page).toHaveURL(/#\/settings/)
  await expect(page.getByTestId('settings-page')).toBeVisible()
  await expect(page.getByTestId('help-card').locator('button').first()).toHaveAttribute(
    'aria-expanded',
    'true',
  )
  await app.close()
})
