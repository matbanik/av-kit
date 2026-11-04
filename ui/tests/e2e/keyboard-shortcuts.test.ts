import { _electron, expect, test } from '@playwright/test'
import { mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))

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

/*
  MEU-95 SHORTCUT_BINDING: every registry chord reaches its route from the real
  window, the rail collapses from Ctrl+B, and a Ctrl chord fires from a text field.
*/

const ROUTES: Array<[string, RegExp, string]> = [
  ['Control+2', /#\/transcript$/, 'transcript-page'],
  ['Control+3', /#\/tts$/, 'tts-page'],
  ['Control+4', /#\/convert$/, 'convert-page'],
  ['Control+5', /#\/capture$/, 'capture-page'],
  ['Control+Comma', /#\/settings$/, 'settings-page'],
  ['Control+1', /#\/$/, 'downloader-page'],
]

test('AC-95.8 registry chords navigate, collapse the rail and fire from a text field', async () => {
  const app = await launchApp()
  try {
    const window = await app.firstWindow()
    await expect(window.getByTestId('downloader-page')).toBeVisible()

    // The URL pattern names the chord in the failure, so no custom message is passed.
    for (const [chord, url, page] of ROUTES) {
      await window.keyboard.press(chord)
      await expect(window).toHaveURL(url)
      await expect(window.getByTestId(page)).toBeVisible()
    }

    // A fresh app data dir starts with the rail expanded.
    const rail = window.locator('nav[aria-label="Main"]')
    await expect(rail).toBeVisible()
    await expect(rail).not.toHaveClass(/nav-rail--collapsed/)
    await window.keyboard.press('Control+B')
    await expect(rail).toHaveClass(/nav-rail--collapsed/)
    await window.keyboard.press('Control+B')
    await expect(rail).not.toHaveClass(/nav-rail--collapsed/)

    const urlInput = window.getByTestId('url-input')
    await expect(urlInput).toBeVisible()
    await urlInput.click()
    await window.keyboard.press('Control+3')
    await expect(window).toHaveURL(/#\/tts$/)
    await expect(window.getByTestId('tts-page')).toBeVisible()
  } finally {
    await app.close()
  }
})

/*
  MEU-97 CHORD_TABLE: Ctrl+L focuses the page's own field and does nothing on a
  page without one; Ctrl+J toggles the console; F1 toggles the page help.
*/

test('AC-97.6 Ctrl+L focuses the page field, Ctrl+J toggles the console, F1 toggles help', async () => {
  const app = await launchApp()
  try {
    const window = await app.firstWindow()
    await expect(window.getByTestId('downloader-page')).toBeVisible()
    const blur = () => window.evaluate(() => (document.activeElement as HTMLElement | null)?.blur())
    const bodyFocused = () => window.evaluate(() => document.activeElement === document.body)

    await window.keyboard.press('Control+L')
    await expect(window.getByTestId('url-input')).toBeFocused()
    await blur()

    await window.keyboard.press('Control+2')
    await expect(window.getByTestId('transcript-page')).toBeVisible()
    await window.keyboard.press('Control+L')
    await expect(window.getByTestId('channel-input')).toBeFocused()
    await blur()

    await window.keyboard.press('Control+3')
    await expect(window.getByTestId('tts-page')).toBeVisible()
    await window.keyboard.press('Control+L')
    await expect.poll(bodyFocused).toBe(true)
    await expect(window).toHaveURL(/#\/tts$/)

    const consolePanel = window.getByTestId('console-panel')
    await expect(consolePanel).toHaveCount(0)
    await window.keyboard.press('Control+J')
    await expect(consolePanel).toHaveCount(1)
    await window.keyboard.press('Control+J')
    await expect(consolePanel).toHaveCount(0)

    await window.keyboard.press('Control+Comma')
    await expect(window.getByTestId('settings-page')).toBeVisible()
    const toggle = window.getByTestId('help-card').first().getByRole('button', { name: /How it works/ })
    await expect(toggle).toHaveCount(1)
    const before = await toggle.getAttribute('aria-expanded')
    await window.keyboard.press('F1')
    await expect(toggle).toHaveAttribute('aria-expanded', before === 'true' ? 'false' : 'true')
  } finally {
    await app.close()
  }
})
