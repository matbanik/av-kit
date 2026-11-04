import { _electron, expect, type Page } from '@playwright/test'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

/**
 * THEME_PROBE (MEU-94, Session 40): a helper, not a test file. Defined once in
 * docs/execution/plans/2026-10-24-gui-theme-path-fields/implementation-plan.md.
 *
 * `addThemeProbe` only registers an init script; the seam installer that calls it does the reload.
 * The probe never replaces `window.fetch`: each seam looks up `window.__avkitThemeProbe` at request
 * time, so the unspecified order of the two init scripts does not matter.
 */

const here = dirname(fileURLToPath(import.meta.url))

export type UiTheme = 'dark' | 'light'

export type ThemeProbeMode = {
  mirror?: UiTheme | null
  theme: { hold: true } | { answer: UiTheme }
}

export type InsertedSelect = {
  id: string
  whileHeld: boolean
  backgroundColor: string
  color: string
}

type ProbeState = {
  counts: { held: number; released: number }
  inserted: InsertedSelect[]
  handle: (url: string, method: string, init?: RequestInit) => Promise<Response> | null
  release: (theme: UiTheme) => void
}

/** G30_PAIRS computed oracles in Chromium. */
export const THEME_ORACLE: Record<UiTheme, { backgroundColor: string; color: string }> = {
  dark: { backgroundColor: 'rgb(26, 26, 46)', color: 'rgb(224, 224, 224)' },
  light: { backgroundColor: 'rgb(255, 255, 255)', color: 'rgb(30, 41, 59)' },
}

/** THEME_COLOURS page floors. */
export const THEME_FLOORS = { settings: 8, tts: 3, convert: 3 } as const

export async function addThemeProbe(page: Page, mode: ThemeProbeMode): Promise<void> {
  await page.addInitScript((probeMode: ThemeProbeMode) => {
    // BOOT_THEME's THEME_STORAGE_KEY, as a literal: an init script closes over nothing.
    const storageKey = 'av-kit.ui.theme'
    try {
      if (probeMode.mirror === null) {
        localStorage.removeItem(storageKey)
      } else if (probeMode.mirror !== undefined) {
        localStorage.setItem(storageKey, probeMode.mirror)
      }
    } catch {
      // A storage failure leaves the mirror as it was; the probed assertions then fail visibly.
    }
    const held: Array<(response: Response) => void> = []
    let answer: UiTheme | null = 'answer' in probeMode.theme ? probeMode.theme.answer : null
    const respond = (theme: UiTheme) =>
      new Response(JSON.stringify({ theme }), { status: 200, headers: { 'Content-Type': 'application/json' } })
    const state: ProbeState = {
      counts: { held: 0, released: 0 },
      inserted: [],
      handle(url, method, init) {
        if (!url.includes('/settings/ui')) {
          return null
        }
        if (method === 'PUT') {
          if (typeof init?.body === 'string') {
            try {
              const body = JSON.parse(init.body) as { theme?: unknown }
              if (body.theme === 'dark' || body.theme === 'light') {
                answer = body.theme
              }
            } catch {
              // Not JSON: the seam answers it unchanged.
            }
          }
          return null
        }
        if (method !== 'GET') {
          return null
        }
        if (answer !== null) {
          return Promise.resolve(respond(answer))
        }
        state.counts.held += 1
        return new Promise<Response>((done) => {
          held.push(done)
        })
      },
      release(theme) {
        answer = theme
        for (const done of held.splice(0)) {
          state.counts.released += 1
          done(respond(theme))
        }
      },
    }
    ;(window as unknown as { __avkitThemeProbe?: ProbeState }).__avkitThemeProbe = state

    let index = 0
    const record = (element: HTMLSelectElement) => {
      const computed = getComputedStyle(element)
      state.inserted.push({
        id: element.getAttribute('data-testid') ?? `#${index}`,
        whileHeld: held.length > 0,
        backgroundColor: computed.backgroundColor,
        color: computed.color,
      })
      index += 1
    }
    new MutationObserver((mutations) => {
      for (const mutation of mutations) {
        mutation.addedNodes.forEach((node) => {
          if (!(node instanceof Element)) {
            return
          }
          if (node instanceof HTMLSelectElement) {
            record(node)
          }
          node.querySelectorAll('select').forEach(record)
        })
      }
    }).observe(document, { childList: true, subtree: true })
  }, mode)
}

export async function releaseTheme(page: Page, theme: UiTheme): Promise<void> {
  await page.evaluate((next: UiTheme) => {
    ;(window as unknown as { __avkitThemeProbe?: ProbeState }).__avkitThemeProbe?.release(next)
  }, theme)
}

export async function themeProbeCounts(page: Page): Promise<{ held: number; released: number }> {
  return page.evaluate(() => {
    const state = (window as unknown as { __avkitThemeProbe?: ProbeState }).__avkitThemeProbe
    return { held: state?.counts.held ?? 0, released: state?.counts.released ?? 0 }
  })
}

export async function insertedSelects(page: Page): Promise<InsertedSelect[]> {
  return page.evaluate(() => {
    const state = (window as unknown as { __avkitThemeProbe?: ProbeState }).__avkitThemeProbe
    return state?.inserted.map((row) => ({ ...row })) ?? []
  })
}

/** The computed pair of every visible select and of its selected option. */
export async function visibleSelectColors(
  page: Page,
): Promise<Array<{ id: string; select: { backgroundColor: string; color: string }; option: { backgroundColor: string; color: string } | null }>> {
  return page.evaluate(() =>
    Array.from(document.querySelectorAll('select'))
      .filter((element) => element.getClientRects().length > 0 && getComputedStyle(element).visibility !== 'hidden')
      .map((element, index) => {
        const pair = (target: Element) => {
          const computed = getComputedStyle(target)
          return { backgroundColor: computed.backgroundColor, color: computed.color }
        }
        const selected = element.selectedOptions[0] ?? null
        return {
          id: element.getAttribute('data-testid') ?? `#${index}`,
          select: pair(element),
          option: selected === null ? null : pair(selected),
        }
      }),
  )
}

export async function documentIsDark(page: Page): Promise<boolean> {
  return page.evaluate(() => document.documentElement.classList.contains('dark'))
}

export async function isShown(page: Page, testId: string): Promise<boolean> {
  return page.getByTestId(testId).isVisible()
}

/** THEME_COLOURS: at least `floor` visible selects, and each select and selected option on the oracle. */
export async function expectThemeColours(page: Page, theme: UiTheme, floor: number): Promise<void> {
  const want = THEME_ORACLE[theme]
  await expect
    .poll(async () => {
      const rows = await visibleSelectColors(page)
      const off = rows
        .filter(
          (row) =>
            row.select.backgroundColor !== want.backgroundColor ||
            row.select.color !== want.color ||
            row.option === null ||
            row.option.backgroundColor !== want.backgroundColor ||
            row.option.color !== want.color,
        )
        .map((row) => `${row.id} select=${row.select.backgroundColor}/${row.select.color} option=${row.option?.backgroundColor}/${row.option?.color}`)
      return { enough: rows.length >= floor, off }
    })
    .toEqual({ enough: true, off: [] })
}

/** Every select inserted so far is on the oracle and none was inserted while a theme answer was held. */
export async function expectInsertedOn(page: Page, theme: UiTheme, floor: number): Promise<void> {
  const want = THEME_ORACLE[theme]
  await expect
    .poll(async () => {
      const rows = await insertedSelects(page)
      const off = rows
        .filter((row) => row.whileHeld || row.backgroundColor !== want.backgroundColor || row.color !== want.color)
        .map((row) => `${row.id} whileHeld=${row.whileHeld} ${row.backgroundColor}/${row.color}`)
      return { enough: rows.length >= floor, off }
    })
    .toEqual({ enough: true, off: [] })
}

/** While a theme answer is held: a held request, the shell, the route placeholder, and no select. */
export async function expectThemeHeld(page: Page): Promise<void> {
  await expect.poll(async () => (await themeProbeCounts(page)).held).toBeGreaterThanOrEqual(1)
  await expect.poll(() => isShown(page, 'app-shell')).toBe(true)
  await expect.poll(() => isShown(page, 'route-theme-pending')).toBe(true)
  expect(await insertedSelects(page)).toEqual([])
}

/** The renderer's BOOT_THEME mirror value. */
export async function storedMirror(page: Page): Promise<string | null> {
  return page.evaluate(() => localStorage.getItem('av-kit.ui.theme'))
}

/** Launch with a caller-owned AVKIT_APP_DATA, so two launches share localStorage. */
export async function launchWithAppData(dir: string) {
  return _electron.launch({
    args: [resolve(here, '../../out/main/index.js')],
    env: {
      ...process.env,
      AVKIT_E2E: '1',
      AVKIT_APP_DATA: dir,
    },
  })
}
