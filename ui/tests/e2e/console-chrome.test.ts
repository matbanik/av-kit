import { _electron, expect, test } from '@playwright/test'
import { mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))

/** MEU-80 HINT_TIMING (`components/ui/Tooltip.tsx`): a hover shows after the delay; a leave hides after the grace. */
const HINT_DELAY_MS = 400
const HINT_GRACE_MS = 120

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

async function firstWindow() {
  const app = await launchApp()
  const page = await app.firstWindow()
  return { app, page }
}

test('C1-1 closed launch keeps console unmounted', async () => {
  const { app, page } = await firstWindow()
  await expect(page.getByTestId('header-console-btn')).toBeVisible()
  await expect(page.getByTestId('header-palette-btn')).toBeVisible()
  await expect(page.getByTestId('console-panel')).toHaveCount(0)
  await app.close()
})

test('C1-2 open shows filter search clear ytdlp output and DEBUG', async () => {
  const { app, page } = await firstWindow()
  await page.getByTestId('header-console-btn').click()
  await expect(page.getByTestId('console-panel')).toBeVisible()
  await expect(page.getByTestId('console-filter')).toBeVisible()
  await expect(page.getByTestId('console-search')).toBeVisible()
  await expect(page.getByTestId('console-clear')).toBeVisible()
  await expect(page.getByTestId('console-ytdlp-toggle')).toBeVisible()
  await expect(page.getByTestId('console-output')).toBeVisible()
  await page.getByTestId('console-level-DEBUG').click()
  await app.close()
})

test('C1-3 expand uses w-full then restores min-w-[320px]', async () => {
  const { app, page } = await firstWindow()
  await expect(page.getByTestId('header-console-btn')).toBeVisible()
  await page.getByTestId('header-console-btn').click()
  await expect(page.getByTestId('console-panel')).toBeVisible()
  await page.getByTestId('console-expand').click()
  await expect(page.getByTestId('console-panel')).toHaveClass(/w-full/)
  await page.getByTestId('console-collapse').click()
  const drawer = await page.getByTestId('console-panel').getAttribute('class')
  expect(drawer).toContain('min-w-[320px]')
  await expect(page.getByTestId('console-panel')).toHaveCount(1)
  await app.close()
})

test('C1-4 close via X Escape and header toggle', async () => {
  const { app, page } = await firstWindow()
  await expect(page.getByTestId('header-console-btn')).toBeVisible()
  await page.getByTestId('header-console-btn').click()
  await expect(page.getByTestId('console-panel')).toBeVisible()
  await page.getByTestId('console-close').click()
  await expect(page.getByTestId('console-panel')).toHaveCount(0)
  await page.getByTestId('header-console-btn').click()
  await page.keyboard.press('Escape')
  await expect(page.getByTestId('console-panel')).toHaveCount(0)
  await page.getByTestId('header-console-btn').click()
  await page.getByTestId('header-console-btn').click()
  await expect(page.getByTestId('console-panel')).toHaveCount(0)
  await app.close()
})

test('C1-5 copy writes clipboard and log-to-file PUTs settings/app', async () => {
  const { app, page } = await firstWindow()
  const putBodies: string[] = []
  await page.context().route((url) => url.pathname.includes('/settings/app'), async (route) => {
    putBodies.push(route.request().postData() ?? '')
    await route.fulfill({ json: { log_to_file: true } })
  })
  await expect(page.getByTestId('header-console-btn')).toBeVisible()
  await page.getByTestId('header-console-btn').click()
  await expect(page.getByTestId('console-panel')).toBeVisible()
  const visibleLogs = await page.locator('[data-testid="console-panel"] pre').innerText()
  await page.getByTestId('console-copy').click()
  const clipboard = await app.evaluate(({ clipboard }) => clipboard.readText())
  expect(clipboard).toBe(visibleLogs)
  await page.getByTestId('console-log-to-file').click()
  await expect.poll(() => putBodies.length).toBe(1)
  expect(putBodies[0]).toBe(JSON.stringify({ log_to_file: true }))
  await app.close()
})

test('C1-6 rail collapse and settings chrome sections', async () => {
  const { app, page } = await firstWindow()
  await expect(page.getByTestId('nav-settings')).toBeVisible()
  await page.getByTestId('nav-collapse').click()
  await expect(page.locator('.nav-rail--collapsed')).toBeVisible()
  await page.getByTestId('nav-settings').click()
  await expect(page.getByTestId('settings-page')).toBeVisible()
  await expect(page.locator('.header-breadcrumb__page')).toHaveText('Settings')
  await expect(page.getByTestId('download-settings')).toBeVisible()
  await expect(page.getByTestId('transcript-settings')).toBeVisible()
  await expect(page.getByTestId('tts-settings')).toBeVisible()
  await expect(page.getByTestId('console-settings')).toBeVisible()
  await expect(page.getByTestId('appearance-settings')).toBeVisible()
  await expect(page.getByTestId('dependencies-section')).toBeVisible()
  await app.close()
})

test('C1-7 INFO exclusive filter keeps INFO and hides DEBUG', async () => {
  const { app, page } = await firstWindow()
  await page.getByTestId('header-console-btn').click()
  await expect(page.getByTestId('console-output')).toBeVisible()
  await page.evaluate(() => {
    window.dispatchEvent(
      new CustomEvent('av-kit:renderer-log', {
        detail: { key: 'e2e-debug', message: '[DEBUG] e2e-debug-line' },
      }),
    )
    window.dispatchEvent(
      new CustomEvent('av-kit:renderer-log', {
        detail: { key: 'e2e-info', message: '[INFO] e2e-info-line' },
      }),
    )
  })
  await page.getByTestId('console-level-INFO').click()
  await expect(page.getByTestId('console-output')).toContainText('INFO')
  await expect(page.getByTestId('console-output')).not.toContainText('DEBUG')
  await app.close()
})

test('C1-8 console-output is contained black-green and app-shell is h-screen', async () => {
  const { app, page } = await firstWindow()
  await expect(page.getByTestId('app-shell')).toHaveClass(/h-screen/)
  await page.getByTestId('header-console-btn').click()
  await expect(page.getByTestId('console-output')).toHaveClass(/overflow-auto/)
  await expect(page.getByTestId('console-output')).toHaveClass(/--color-console-bg/)
  await expect(page.getByTestId('console-output')).toHaveClass(/--color-console-fg/)
  await app.close()
})

// MEU-69 (Session 31) — appended. CONSOLE_TOGGLE, PALETTE_BUTTON and NO_SHIFT are defined once in
// docs/execution/plans/2026-10-10-gui-polish-residuals/implementation-plan.md.

/** WINDOW_SETTLED: two animation frames, then window size unchanged for 500 ms. */
async function windowSettled(page: Awaited<ReturnType<typeof firstWindow>>['page']): Promise<void> {
  await page.evaluate(
    () =>
      new Promise<void>((resolve) => {
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            let last = `${window.innerWidth}x${window.innerHeight}`
            let stableSince = performance.now()
            const tick = (): void => {
              const now = `${window.innerWidth}x${window.innerHeight}`
              if (now !== last) {
                last = now
                stableSince = performance.now()
              }
              if (performance.now() - stableSince >= 500) {
                resolve()
              } else {
                window.setTimeout(tick, 50)
              }
            }
            tick()
          })
        })
      }),
  )
}

test('AC-69.5 header Console is a pressed toggle that follows the panel; Commands opens the palette', async () => {
  const { app, page } = await firstWindow()
  const toggle = page.getByTestId('header-console-btn')
  await expect(toggle).toHaveAttribute('aria-pressed', 'false')
  await windowSettled(page)
  const closed = await toggle.boundingBox()
  await toggle.click()
  await expect(page.getByTestId('console-panel')).toBeVisible()
  await expect(toggle).toHaveAttribute('aria-pressed', 'true')
  const open = await toggle.boundingBox()
  expect(closed).not.toBeNull()
  expect(open).not.toBeNull()
  for (const key of ['x', 'y', 'width', 'height'] as const) {
    expect(Math.abs((open?.[key] ?? 0) - (closed?.[key] ?? 0)), `NO_SHIFT header ${key}`).toBeLessThanOrEqual(0.5)
  }
  await page.keyboard.press('Escape')
  await expect(page.getByTestId('console-panel')).toHaveCount(0)
  await expect(toggle).toHaveAttribute('aria-pressed', 'false')
  const palette = page.getByTestId('header-palette-btn')
  await expect(palette).toContainText('Commands')
  await expect(palette).toContainText('Ctrl+K')
  await palette.click()
  await expect(page.getByTestId('command-palette')).toBeVisible()
  await app.close()
})

test('AC-80.11: hovering console-close shows its hint inside the window, moving away hides it, nav-capture shows none', async () => {
  const { app, page } = await firstWindow()
  await page.getByTestId('header-console-btn').click()
  await expect(page.getByTestId('console-panel')).toBeVisible()
  const hint = page.getByTestId('console-close-hint')
  await expect(hint).toHaveCount(0)
  await expect(page.getByTestId('console-close-tip')).toHaveCount(1)
  await page.getByTestId('console-close').hover()
  await page.waitForTimeout(HINT_DELAY_MS)
  await expect(hint).toBeVisible()
  await expect(hint).toHaveAttribute('role', 'tooltip')
  await expect(hint).toHaveText('Close console')
  const box = await hint.boundingBox()
  const size = await page.evaluate(() => ({ width: window.innerWidth, height: window.innerHeight }))
  expect(box).toBeTruthy()
  expect((box?.x ?? -1) >= 0 && (box?.y ?? -1) >= 0).toBe(true)
  expect((box?.x ?? 0) + (box?.width ?? 0)).toBeLessThanOrEqual(size.width)
  expect((box?.y ?? 0) + (box?.height ?? 0)).toBeLessThanOrEqual(size.height)
  await page.mouse.move(5, 5)
  await page.waitForTimeout(HINT_GRACE_MS)
  await expect(hint).toHaveCount(0)
  // The labelled rail item is outside ICON_ONLY_INVENTORY: no rendered hint.
  await page.getByTestId('nav-capture').hover()
  await page.waitForTimeout(HINT_DELAY_MS + HINT_GRACE_MS)
  await expect(page.getByRole('tooltip')).toHaveCount(0)
  await app.close()
})
