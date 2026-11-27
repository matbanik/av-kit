/**
 * MEU-162 (Session 99) help quick start on the real app, one fresh scratch root per launch
 * (`launchIsolated`, DEMO_STAGE F2):
 *
 * - `AC-162.10 closed`: on a first visit every page's help card is closed (D-1289 A).
 * - `AC-162.10 hint`: every page's header reads `Quick start · N steps`, N from the JSON.
 * - `AC-162.11 <page>`: after the page's stage, every step target is visible, the open card
 *   lists the JSON step texts, and each figure loads its light image in the light theme and its
 *   dark image in the dark theme, the other one hidden (D-1292, D-1294).
 * - `AC-162.12 search`: a search hides the quick start and the figures and leaves one topic.
 *
 * The test reads `quick-start.json` with `fs`; a missing file is an empty quick start, so a
 * Red run fails by assertion. No expect carries a custom message: the Red receipt must carry
 * Playwright's `Error: expect(` line (red-check.py).
 */

import { expect, test, type Locator, type Page } from '@playwright/test'
import { existsSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { CAPTURE_KEY_DEFAULT, captureKeyText } from '../../src/renderer/src/features/capture/capture-key'
import {
  FEATURE_PAGES,
  HELP_FEATURES,
  STAGES,
  installSeam,
  launchIsolated,
  openFeature,
  type HelpFeature,
} from '../help-shots/stage'
import { HELP_QUICK_START, HELP_QUICK_START_HINT, HELP_QUICK_START_STEP, HELP_SHOT } from './test-ids'

const here = dirname(fileURLToPath(import.meta.url))
const QUICK_START_FILE = resolve(here, '../../src/renderer/src/components/help/quick-start.json')
const TEST_TIMEOUT_MS = 300_000

type QuickStartPage = {
  intro: string
  steps: Array<{ text: string; target: string | null }>
  shots: Array<{ name: string; steps: number[]; alt: string }>
}

function quickStart(): Partial<Record<HelpFeature, QuickStartPage>> {
  if (!existsSync(QUICK_START_FILE)) return {}
  const data = JSON.parse(readFileSync(QUICK_START_FILE, 'utf8')) as {
    pages?: Partial<Record<HelpFeature, QuickStartPage>>
  }
  return data.pages ?? {}
}

/** Every close function of an app that is still open; afterEach closes them. */
const live = new Set<() => Promise<void>>()

test.afterEach(async () => {
  for (const close of [...live]) await close()
})

async function launch(): Promise<Page> {
  const isolated = await launchIsolated()
  let closed: Promise<void> | undefined
  const close = (): Promise<void> => {
    closed ??= (async () => {
      live.delete(close)
      await isolated.app.close()
    })()
    return closed
  }
  live.add(close)
  return isolated.page
}

function helpCard(page: Page, feature: HelpFeature): Locator {
  return page.getByTestId(FEATURE_PAGES[feature].page).getByTestId('help-card')
}

function helpHeader(page: Page, feature: HelpFeature): Locator {
  return helpCard(page, feature).locator('button[aria-expanded]').first()
}

async function imageLoaded(image: Locator): Promise<boolean> {
  return image.evaluate((node) => {
    const img = node as HTMLImageElement
    return img.complete && img.naturalWidth > 0
  })
}

async function setDark(page: Page, dark: boolean): Promise<void> {
  await page.evaluate((on) => {
    document.documentElement.classList.toggle('dark', on)
  }, dark)
}

test('AC-162.10 closed: every help card is closed on the first visit', async () => {
  test.setTimeout(TEST_TIMEOUT_MS)
  const page = await launch()
  await installSeam(page)
  for (const feature of HELP_FEATURES) {
    await openFeature(page, feature)
    await expect(helpHeader(page, feature)).toHaveAttribute('aria-expanded', 'false')
  }
})

test('AC-162.10 hint: every help header reads Quick start with the step count', async () => {
  test.setTimeout(TEST_TIMEOUT_MS)
  const pages = quickStart()
  const page = await launch()
  await installSeam(page)
  for (const feature of HELP_FEATURES) {
    await openFeature(page, feature)
    const count = pages[feature]?.steps.length ?? 0
    await expect(helpCard(page, feature).getByTestId(HELP_QUICK_START_HINT)).toHaveText(
      `Quick start · ${count} steps`,
    )
  }
})

for (const feature of HELP_FEATURES) {
  test(`AC-162.11 ${feature}: the step targets show, and the steps and figures match the JSON`, async () => {
    test.setTimeout(TEST_TIMEOUT_MS)
    const data = quickStart()[feature]
    const page = await launch()
    await STAGES[feature](page)

    for (const step of data?.steps ?? []) {
      if (step.target !== null) await expect(page.getByTestId(step.target).first()).toBeVisible()
    }
    if (feature === 'transcript') {
      await expect(page.getByTestId('view-compiled-link')).toHaveCount(0)
    }

    const card = helpCard(page, feature)
    await setDark(page, false)
    await helpHeader(page, feature).click()
    await expect(card.getByTestId(HELP_QUICK_START)).toBeVisible()
    await expect(card.getByTestId(HELP_QUICK_START_STEP)).toHaveText(
      // MEU-165: the stored step names the capture key by its token; the isolated app saves the default key.
      (data?.steps ?? []).map((s) => captureKeyText(s.text, CAPTURE_KEY_DEFAULT)),
    )

    const shots = data?.shots ?? []
    await expect(card.getByTestId(HELP_SHOT)).toHaveCount(shots.length)
    for (const theme of ['light', 'dark'] as const) {
      await setDark(page, theme === 'dark')
      const other = theme === 'dark' ? 'light' : 'dark'
      for (const shot of shots) {
        const figure = card.locator(`[data-testid="${HELP_SHOT}"][data-shot="${shot.name}"]`)
        const shown = figure.locator(`img.help-shot__img--${theme}`)
        await shown.scrollIntoViewIfNeeded()
        await expect.poll(async () => imageLoaded(shown), { timeout: 10_000 }).toBe(true)
        await expect(figure.locator(`img.help-shot__img--${other}`)).toHaveCSS('display', 'none')
      }
    }
  })
}

test('AC-162.12 search: a search hides the quick start and the figures and keeps one topic', async () => {
  test.setTimeout(TEST_TIMEOUT_MS)
  const page = await launch()
  await STAGES.downloader(page)
  const card = helpCard(page, 'downloader')
  await helpHeader(page, 'downloader').click()
  await expect(card.getByTestId(HELP_QUICK_START)).toBeVisible()
  await card.getByTestId('help-search').fill('SABR')
  await expect(card.getByTestId(HELP_QUICK_START)).toHaveCount(0)
  await expect(card.getByTestId(HELP_SHOT)).toHaveCount(0)
  await expect(card.locator('[data-help-section]:visible')).toHaveCount(1)
})
