import { _electron, expect, test } from '@playwright/test'
import { existsSync, mkdtempSync, statSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const ui = resolve(here, '../..')
const main = resolve(ui, 'out-e2e/main/index.js')
const html = resolve(ui, 'out-e2e/renderer/primitive-harness.html')

test('AC-51.7 real Electron primitive harness exercises all five controls', async () => {
  expect(existsSync(main), 'fresh isolated main build').toBe(true)
  expect(existsSync(html), 'fresh isolated harness HTML').toBe(true)
  expect(statSync(main).mtimeMs).toBeGreaterThanOrEqual(statSync(resolve(ui, 'electron.vite.config.ts')).mtimeMs)
  expect(statSync(html).mtimeMs).toBeGreaterThanOrEqual(statSync(resolve(ui, 'src/renderer/src/primitive-harness.tsx')).mtimeMs)

  const app = await _electron.launch({
    args: [main],
    env: {
      ...process.env,
      AVKIT_E2E: '1',
      AVKIT_APP_DATA: mkdtempSync(join(tmpdir(), 'avkit-primitive-e2e-')),
    },
  })
  try {
    await app.firstWindow()
    const windowPromise = app.waitForEvent('window')
    await app.evaluate(async ({ BrowserWindow }, htmlPath) => {
      const window = new BrowserWindow({ show: true, webPreferences: { sandbox: true } })
      await window.loadFile(htmlPath)
    }, html)
    const page = await windowPromise
    await expect(page.getByTestId('primitive-harness')).toBeVisible()

    const disclosure = page.getByTestId('primitive-disclosure')
    await expect(disclosure).toHaveAttribute('aria-expanded', 'false')
    await expect(page.getByRole('button', { name: 'Inside advanced' })).toHaveCount(0)
    await disclosure.click()
    await expect(disclosure).toHaveAttribute('aria-expanded', 'true')
    await expect(page.getByRole('button', { name: 'Inside advanced' })).toBeVisible()
    await disclosure.focus()
    await page.keyboard.press('Enter')
    await expect(disclosure).toHaveAttribute('aria-expanded', 'false')
    await page.keyboard.press('Space')
    await expect(disclosure).toHaveAttribute('aria-expanded', 'true')

    const segment = page.getByTestId('primitive-segment')
    const browser = segment.getByRole('radio', { name: 'Browser' })
    const file = segment.getByRole('radio', { name: 'File' })
    await browser.check()
    await expect(browser).toBeChecked()
    await expect(page.getByTestId('primitive-segment-value')).toHaveText('browser')
    await browser.focus()
    await page.keyboard.press('ArrowRight')
    await expect(file).toBeChecked()
    await expect(page.getByTestId('primitive-segment-value')).toHaveText('file')
    await expect(file).toHaveCSS('accent-color', /rgb\(/)

    const chip = page.getByTestId('primitive-chip')
    await expect(chip).toContainText('Queued')
    await expect(chip).toContainText('3')
    await expect(chip).toHaveAttribute('data-tone', 'warning')
    await expect(chip).toHaveCSS('color', /rgb\(/)

    const form = page.getByRole('textbox', { name: 'Model name' })
    await expect(form).toHaveAttribute('aria-describedby', /primitive-form-hint.*primitive-form-error/)
    await expect(page.locator('#primitive-form-hint')).toContainText('Required for this run')
    await expect(page.locator('#primitive-form-error')).toContainText('Choose a name')

    const path = page.getByRole('textbox', { name: 'Output folder' })
    await expect(path).toHaveValue('C:/one folder')
    await path.fill('D:/new folder')
    await expect(page.getByTestId('primitive-path-value')).toHaveText('D:/new folder')
    await page.getByTestId('primitive-path-browse').click()
    await expect(page.getByTestId('primitive-browse-count')).toHaveText('1')
    await page.getByTestId('primitive-path-browse').focus()
    await page.keyboard.press('Enter')
    await expect(page.getByTestId('primitive-browse-count')).toHaveText('2')
  } finally {
    await app.close()
  }
})
