// Session 97 probe (task row 1; D-1246): the hover media facts and the hover colour of a Tailwind
// `hover:` button, natively and under each Chromium setting the plan weighs.
// Usage: pwsh -NoProfile -File run-probe.ps1 -Probe hover
// It launches only probe-app.cjs through ui's installed Playwright and Electron, closes each app it
// launched, and prints one JSON line per step, the last naming every pid it launched.
import { createRequire } from 'node:module'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const require = createRequire(join(resolve(here, '../../../../ui'), 'package.json'))
const { _electron } = require('@playwright/test')
const electronPath = require('electron')

const env = { ...process.env }
delete env.ELECTRON_RUN_AS_NODE

const HOVER_NONE = '--blink-settings=primaryHoverType=1,availableHoverTypes=1,primaryPointerType=1,availablePointerTypes=1'
const HOVER_CAPABLE = '--blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4'

async function read(page, step) {
  const facts = await page.evaluate(() => ({
    dpr: window.devicePixelRatio,
    hover: matchMedia('(hover: hover)').matches,
    hover_none: matchMedia('(hover: none)').matches,
    any_hover: matchMedia('(any-hover: hover)').matches,
    pointer_fine: matchMedia('(pointer: fine)').matches,
    pointer_none: matchMedia('(pointer: none)').matches,
  }))
  await page.mouse.move(0, 0)
  const button = page.getByTestId('b')
  const rest = await button.evaluate((n) => getComputedStyle(n).backgroundColor)
  await button.hover()
  await page.waitForTimeout(200)
  const hovered = await button.evaluate((n) => getComputedStyle(n).backgroundColor)
  const pseudo = await button.evaluate((n) => n.matches(':hover'))
  console.log(JSON.stringify({ step, ...facts, rest, hovered, matches_hover_pseudo: pseudo }))
}

const pids = []
for (const [step, extra] of [
  ['native', []],
  ['blink-settings-hover-none', [HOVER_NONE]],
  ['blink-settings-hover-capable', [HOVER_CAPABLE]],
  ['hover-none-then-capable', [HOVER_NONE, HOVER_CAPABLE]],
]) {
  const app = await _electron.launch({ executablePath: electronPath, args: [join(here, 'probe-app.cjs'), ...extra], env })
  pids.push(app.process().pid)
  try {
    const page = await app.firstWindow()
    await page.getByTestId('b').waitFor()
    if (step === 'native') {
      const versions = await app.evaluate(() => ({ electron: process.versions.electron, chrome: process.versions.chrome }))
      console.log(JSON.stringify({ step: 'versions', ...versions }))
    }
    await read(page, step)
  } finally {
    await app.close()
  }
}
console.log(JSON.stringify({ step: 'done', launched_pids: pids }))
