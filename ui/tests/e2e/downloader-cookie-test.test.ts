import { expect, test, type ElectronApplication, type Page } from '@playwright/test'
import { mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { launchElectron } from './electron-app'
import { COOKIE_TEST_RESULT } from './test-ids'

/**
 * MEU-169 and MEU-170 (AC-169.11, AC-170.4): the Test Cookies result line, the busy button and the
 * SABR scope clause in the real app. Each test opens a fresh app on a scratch AVKIT_APP_DATA. The
 * spec routes the cookie test and the SABR check, force and read, so no cookie source is read and
 * nothing reaches YouTube.
 */

const TEST_TIMEOUT_MS = 240_000
const SETTLE_MS = 300
const ACTIVE = 'SABR active — quality limited to 360p'

const OK_REPLY = { ok: true, outcome: 'ok', error_message: null }
const OK_TEXT = 'Cookies read. YouTube answered.'

/** The eight Advanced ids in the panel's DOM order (`downloader-advanced-gap.test.ts`). */
const ADVANCED_IDS = [
  'sabr-status',
  'sabr-check-btn',
  'sabr-force-btn',
  'sabr-clear-btn',
  'cookie-browser',
  'cookie-profile',
  'cookie-file',
  'cookie-test-btn',
]

type Reply = { status: number; json: unknown }

type SabrSnapshot = { mode: string; source: string | null; checked_at: string | null }

const apps = new Set<ElectronApplication>()
const releases: Array<() => void> = []

test.afterEach(async () => {
  for (const release of releases.splice(0)) release()
  for (const app of [...apps]) {
    apps.delete(app)
    await app.close()
  }
})

async function launchApp(): Promise<Page> {
  const app = await launchElectron({
    env: { AVKIT_APP_DATA: mkdtempSync(join(tmpdir(), 'avkit-e2e-cookie-test-')) },
  })
  apps.add(app)
  return app.firstWindow({ timeout: 60_000 })
}

/** Answers each POST /downloads/cookies/test from `replies`, after `held` settles when given. */
async function routeCookieTest(page: Page, replies: Reply[], held?: Promise<void>): Promise<string[]> {
  const bodies: string[] = []
  await page.route(
    (url) => /\/downloads\/cookies\/test\/?$/.test(url.pathname),
    async (route) => {
      if (route.request().method() !== 'POST') {
        await route.fallback()
        return
      }
      bodies.push(route.request().postData() ?? '')
      if (held !== undefined) await held
      const next = replies.shift() ?? { status: 200, json: OK_REPLY }
      await route.fulfill({ status: next.status, json: next.json })
    },
  )
  return bodies
}

/** The SABR read answers the last routed check or force; nothing reaches the backend's probe. */
async function routeSabr(page: Page): Promise<void> {
  let snapshot: SabrSnapshot = { mode: 'inactive', source: null, checked_at: null }
  await page.route(
    (url) => /\/downloads\/sabr(\/check|\/force)?\/?$/.test(url.pathname),
    async (route) => {
      const method = route.request().method()
      const path = new URL(route.request().url()).pathname.replace(/\/$/, '')
      if (method === 'POST' && path.endsWith('/check')) {
        snapshot = { mode: 'inactive', source: 'detected', checked_at: new Date().toISOString() }
      } else if (method === 'POST' && path.endsWith('/force')) {
        snapshot = { mode: 'active', source: 'forced', checked_at: new Date().toISOString() }
      } else if (method !== 'GET') {
        await route.fallback()
        return
      }
      await route.fulfill({ json: snapshot })
    },
  )
}

async function openAdvanced(page: Page): Promise<void> {
  await page.getByTestId('downloader-page').waitFor({ state: 'visible', timeout: 60_000 })
  const toggle = page.getByTestId('add-advanced-toggle')
  await toggle.click()
  await expect(toggle).toHaveAttribute('aria-expanded', 'true')
}

type Measure = { tail: number; gap: number; panelDomIds: string[] }

/** `downloader-advanced-gap.test.ts`'s TAIL, GAP and id order, read with the scroller at its end. */
async function measure(page: Page): Promise<Measure> {
  await page.evaluate(() => {
    const scroller = document.querySelector('[data-testid="downloader-page"] form')?.parentElement
    if (scroller) scroller.scrollTop = scroller.scrollHeight
  })
  await new Promise((done) => setTimeout(done, SETTLE_MS))
  return page.evaluate((ids) => {
    const form = document.querySelector('[data-testid="downloader-page"] form')
    const scroller = form?.parentElement ?? null
    const toggle = document.querySelector('[data-testid="add-advanced-toggle"]')
    const disclosure = toggle?.closest('section') ?? null
    const panelId = toggle?.getAttribute('aria-controls') ?? ''
    const panel = panelId ? document.getElementById(panelId) : null
    const queue = document.querySelector('[data-testid="download-queue-region"]')
    const disclosureBox = disclosure?.getBoundingClientRect() ?? null
    const scrollerBox = scroller?.getBoundingClientRect() ?? null
    const queueBox = queue?.getBoundingClientRect() ?? null
    const tail =
      disclosureBox && scrollerBox && scroller
        ? scroller.scrollHeight - (disclosureBox.bottom - scrollerBox.top + scroller.scrollTop)
        : Number.NaN
    const gap = disclosureBox && queueBox ? queueBox.top - disclosureBox.bottom : Number.NaN
    const panelDomIds = panel
      ? [...panel.querySelectorAll('[data-testid]')]
          .map((el) => el.getAttribute('data-testid') ?? '')
          .filter((id) => ids.includes(id))
      : []
    return { tail, gap, panelDomIds }
  }, ADVANCED_IDS)
}

test('AC-169.11 each Test Cookies outcome shows its text beside the button', async () => {
  test.setTimeout(TEST_TIMEOUT_MS)
  const page = await launchApp()
  const bodies = await routeCookieTest(page, [
    { status: 200, json: OK_REPLY },
    { status: 200, json: { ok: false, outcome: 'unreadable', error_message: 'cookie file is missing' } },
    { status: 200, json: { ok: false, outcome: 'check_failed', error_message: 'Sign in to confirm you are not a bot' } },
    { status: 200, json: { ok: true, outcome: null, error_message: null } },
  ])
  const texts = [
    OK_TEXT,
    'Could not read the cookies: cookie file is missing',
    "Cookies read, but YouTube's check failed: Sign in to confirm you are not a bot",
    'Cookie mode is None. Nothing to test.',
  ]
  await openAdvanced(page)
  const button = page.getByTestId('cookie-test-btn')
  const result = page.getByTestId(COOKIE_TEST_RESULT)
  for (const [index, text] of texts.entries()) {
    await button.click()
    await expect(result).toHaveText(text)
    await expect(result).toHaveAttribute('role', 'status')
    const beside = await result.evaluate(
      (el) => el.parentElement?.querySelector('[data-testid="cookie-test-btn"]') !== null,
    )
    expect(beside).toBe(true)
    expect(bodies).toHaveLength(index + 1)
  }
})

test('AC-169.11 the button is disabled while the reply is pending', async () => {
  test.setTimeout(TEST_TIMEOUT_MS)
  const page = await launchApp()
  let open: () => void = () => undefined
  const held = new Promise<void>((done) => {
    open = done
  })
  releases.push(() => open())
  await routeCookieTest(page, [{ status: 200, json: OK_REPLY }], held)
  await openAdvanced(page)
  const button = page.getByTestId('cookie-test-btn')
  await button.click()
  await expect(button).toBeDisabled()
  await expect(button).toHaveAttribute('aria-busy', 'true')
  await expect(page.getByTestId(COOKIE_TEST_RESULT)).toHaveCount(0)
  open()
  await expect(button).toBeEnabled()
  await expect(page.getByTestId(COOKIE_TEST_RESULT)).toHaveText(OK_TEXT)
})

test('AC-169.11 the Advanced panel keeps its ids, tail and gap with a result shown', async () => {
  test.setTimeout(TEST_TIMEOUT_MS)
  const page = await launchApp()
  await routeCookieTest(page, [{ status: 200, json: OK_REPLY }])
  await openAdvanced(page)
  await page.getByTestId('cookie-test-btn').click()
  await expect(page.getByTestId(COOKIE_TEST_RESULT)).toHaveText(OK_TEXT)
  const m = await measure(page)
  expect(m.panelDomIds).toEqual(ADVANCED_IDS)
  expect(m.tail).toBeLessThanOrEqual(1)
  expect(Math.abs(m.gap - 16)).toBeLessThanOrEqual(1)
})

test('AC-170.4 a detected SABR check says that it does not use cookies', async () => {
  test.setTimeout(TEST_TIMEOUT_MS)
  const page = await launchApp()
  await routeSabr(page)
  await openAdvanced(page)
  await page.getByTestId('sabr-check-btn').click()
  await expect(page.getByTestId('sabr-status')).toHaveText(
    /^SABR inactive · checked \d\d:\d\d:\d\d · Check SABR does not use cookies$/,
  )
})

test('AC-170.4 a forced SABR status has no clause', async () => {
  test.setTimeout(TEST_TIMEOUT_MS)
  const page = await launchApp()
  await routeSabr(page)
  await openAdvanced(page)
  await page.getByTestId('sabr-force-btn').click()
  const status = page.getByTestId('sabr-status')
  await expect(status).toHaveText(new RegExp(`^${ACTIVE} · forced \\d\\d:\\d\\d:\\d\\d$`))
  await expect(status).not.toContainText('Check SABR')
})
