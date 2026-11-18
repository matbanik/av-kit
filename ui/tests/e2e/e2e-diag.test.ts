// Session 91 (2026-11-17-e2e-pointer-flakes): the E2E diagnostics and the pointer shield in the
// built app. AC-4: a launch writes its phase lines and its main log. AC-8: pointerOn waits until
// its target is the element under the point. AC-9: the default launch makes the window ignore OS
// mouse input while Playwright's input still arrives. AC-10 (guard): `pointerShield: false` keeps
// the window's input as it is. Each module is checked with existsSync and loaded through a dynamic
// import, as electron-harness.test.ts does. No custom expect message: red-check.py reads a
// Playwright diagnostic only as `Error: expect(`.
import { spawnSync } from 'node:child_process'
import { existsSync, mkdtempSync, readFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

import { expect, test, type ElectronApplication, type Locator, type Page } from '@playwright/test'

const here = dirname(fileURLToPath(import.meta.url))
const APP_PATH = resolve(here, 'electron-app.ts')
const SETTLE_PATH = resolve(here, 'pointer-settle.ts')
const DIAG_PATH = resolve(here, 'e2e-diag.ts')
/** The one allowed spawn bound (assert-check.py ALLOWED_TIMEOUT), so a stuck pwsh child cannot hold AC-9 or AC-10. */
const AC9_SPAWN_TIMEOUT_MS = 30_000
const WS_EX_TRANSPARENT = 0x20
const WS_EX_LAYERED = 0x80000
const GWL_EXSTYLE = -20

// A run outside flake-run.py has no diag folder; this file needs one, so it makes its own.
if (!process.env.AVKIT_E2E_DIAG_DIR) {
  process.env.AVKIT_E2E_DIAG_DIR = mkdtempSync(join(tmpdir(), 'avkit-e2e-diag-'))
}

type Launch = (options?: {
  main?: string
  env?: Record<string, string | undefined>
  pointerShield?: false
}) => Promise<ElectronApplication>

type Box = { x: number; y: number; width: number; height: number }

interface SettleModule {
  settledBox: (page: Page, locator: Locator) => Promise<Box | null>
  pointerOn: (page: Page, locator: Locator) => Promise<{ x: number; y: number }>
}

type Line = Record<string, unknown>

async function loadLaunch(): Promise<Launch> {
  expect(existsSync(APP_PATH)).toBe(true)
  const mod = (await import(/* @vite-ignore */ pathToFileURL(APP_PATH).href)) as { launchElectron: Launch }
  return mod.launchElectron
}

async function loadSettle(): Promise<SettleModule> {
  expect(existsSync(SETTLE_PATH)).toBe(true)
  expect(existsSync(DIAG_PATH)).toBe(true)
  return (await import(/* @vite-ignore */ pathToFileURL(SETTLE_PATH).href)) as SettleModule
}

function scratch(): string {
  return mkdtempSync(join(tmpdir(), 'avkit-e2e-diag-app-'))
}

function jsonLines(file: string): Line[] {
  if (!existsSync(file)) return []
  return readFileSync(file, 'utf8')
    .split('\n')
    .filter((line) => line !== '')
    .map((line) => JSON.parse(line) as Line)
}

/** The extended window style of the page's native window, read through user32 in a pwsh child. */
async function windowStyle(app: ElectronApplication, page: Page): Promise<number> {
  const win = await app.browserWindow(page)
  const hwnd = await win.evaluate((w) => w.getNativeWindowHandle().readBigUInt64LE(0).toString())
  const script = [
    "$sig = '[DllImport(\"user32.dll\")] public static extern IntPtr GetWindowLongPtrW(IntPtr hWnd, int nIndex);'",
    "$type = Add-Type -MemberDefinition $sig -Name 'AvkitS91Style' -Namespace 'AvkitE2E' -PassThru",
    `$type::GetWindowLongPtrW([IntPtr]::new([long]'${hwnd}'), ${String(GWL_EXSTYLE)}).ToInt64()`,
  ].join('; ')
  const result = spawnSync('pwsh', ['-NoProfile', '-Command', script], {
    encoding: 'utf8',
    timeout: AC9_SPAWN_TIMEOUT_MS,
  })
  expect(result.error).toBeUndefined()
  expect(result.status).toBe(0)
  const style = Number(result.stdout.trim())
  expect(Number.isInteger(style)).toBe(true)
  return style
}

test('AC-4 a launch writes its phase lines and its main log, and the close adds its own', async () => {
  const launchElectron = await loadLaunch()
  const dir = process.env.AVKIT_E2E_DIAG_DIR ?? ''
  const phases = join(dir, 'phases.jsonl')
  const info = test.info()
  const runId = process.env.AVKIT_E2E_RUN_ID ?? ''
  const mine = (): Line[] =>
    jsonLines(phases).filter(
      (line) =>
        line.title === info.title && line.file === 'e2e-diag.test.ts' && line.line === info.line && line.run_id === runId,
    )
  const app = await launchElectron({ env: { AVKIT_APP_DATA: scratch() } })
  try {
    expect(existsSync(phases)).toBe(true)
    const opened = mine()
    expect(opened.map((line) => line.phase)).toEqual(['launch-start', 'launch-end', 'evaluate-end'])
    expect(new Set(opened.map((line) => line.launch)).size).toBe(1)
    for (const line of opened) {
      expect(line.test_status).toBe('passed')
      expect(line.test_errors).toBe(0)
    }
    const mainLog = join(dir, String(opened[0]?.main_log))
    expect(jsonLines(mainLog).map((line) => line.event)).toContain('install')
    const resizes = (): number => jsonLines(mainLog).filter((line) => line.event === 'resize').length
    const page = await app.firstWindow()
    const before = resizes()
    const win = await app.browserWindow(page)
    await win.evaluate((w) => {
      const [width, height] = w.getSize()
      w.setSize(width - 40, height - 40)
    })
    await expect.poll(resizes).toBeGreaterThan(before)
    await app.close()
    const all = mine()
    expect(all.map((line) => line.phase)).toEqual([
      'launch-start',
      'launch-end',
      'evaluate-end',
      'close-start',
      'close-end',
      'exit',
    ])
    expect(new Set(all.map((line) => line.launch)).size).toBe(1)
    for (const line of all) {
      expect(line.test_status).toBe('passed')
      expect(line.test_errors).toBe(0)
    }
    expect(jsonLines(phases).filter((line) => line.phase === 'evaluate-error')).toEqual([])
  } finally {
    await app.close()
  }
})

test('AC-8 pointerOn waits while another element covers the target, and settledBox matches the box', async () => {
  const launchElectron = await loadLaunch()
  const { pointerOn, settledBox } = await loadSettle()
  const app = await launchElectron({ env: { AVKIT_APP_DATA: scratch() } })
  try {
    const page = await app.firstWindow()
    const button = page.getByTestId('nav-convert')
    await expect(button).toBeVisible()
    await page.evaluate(() => {
      const cover = document.createElement('div')
      cover.id = 'avkit-s91-cover'
      cover.style.cssText = 'position: fixed; inset: 0; z-index: 2147483647;'
      document.body.appendChild(cover)
    })
    let resolved = false
    const pending = pointerOn(page, button).then((point) => {
      resolved = true
      return point
    })
    pending.catch(() => undefined)
    const frames = await page.evaluate(
      () =>
        new Promise<number>((done) => {
          let n = 0
          const tick = (): void => {
            n += 1
            if (n >= 10) done(n)
            else requestAnimationFrame(tick)
          }
          requestAnimationFrame(tick)
        }),
    )
    expect(frames).toBe(10)
    expect(resolved).toBe(false)
    await page.evaluate(() => document.getElementById('avkit-s91-cover')?.remove())
    const point = await pending
    const hit = await button.evaluate((element, at) => {
      const under = document.elementFromPoint(at.x, at.y)
      return under !== null && (under === element || element.contains(under))
    }, point)
    expect(hit).toBe(true)
    const settled = await settledBox(page, button)
    expect(settled).toEqual(await button.boundingBox())
  } finally {
    await app.close()
  }
})

test('AC-9 the default launch makes the window ignore OS mouse input, and Playwright input still arrives', async () => {
  const launchElectron = await loadLaunch()
  const app = await launchElectron({ env: { AVKIT_APP_DATA: scratch() } })
  try {
    const page = await app.firstWindow()
    await expect(page.getByTestId('nav-convert')).toBeVisible()
    const style = await windowStyle(app, page)
    expect(style & WS_EX_TRANSPARENT).toBe(WS_EX_TRANSPARENT)
    expect(style & WS_EX_LAYERED).toBe(WS_EX_LAYERED)
    await page.getByTestId('nav-convert').click()
    await expect.poll(() => page.evaluate(() => window.location.hash)).toBe('#/convert')
    await page.getByTestId('header-console-btn').click()
    await expect(page.getByTestId('console-panel')).toBeVisible()
    await page.getByTestId('console-close').hover()
    await expect(page.getByTestId('console-close-hint')).toBeVisible()
    await expect(page.getByTestId('console-close-hint')).toHaveText('Close console')
  } finally {
    await app.close()
  }
})

test('AC-10 a launch with pointerShield false keeps the window taking OS mouse input', async () => {
  const launchElectron = await loadLaunch()
  const app = await launchElectron({ env: { AVKIT_APP_DATA: scratch() }, pointerShield: false })
  try {
    const page = await app.firstWindow()
    await expect(page.getByTestId('nav-convert')).toBeVisible()
    const style = await windowStyle(app, page)
    expect(style & WS_EX_TRANSPARENT).toBe(0)
  } finally {
    await app.close()
  }
})
