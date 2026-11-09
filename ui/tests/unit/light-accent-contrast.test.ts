/** @vitest-environment jsdom */

/**
 * MEU-126 — light accent labels read at 4.5:1 (AC-126.1 … AC-126.7).
 *
 * Every colour is read from `TOKEN_FILE` at test time, so the file holds neither
 * ruled light value and a token edit moves these ratios with nothing to re-pin.
 *
 * `TINT_MODEL`: `bg-accent/N` paints the accent at alpha N/100 over the opaque
 * surface behind it, composited per channel in sRGB and rounded half up. A selected
 * queue card's wash is read from the class the card ships, `CARD_STATE_CLASSES`.
 * `CONTRAST_FLOOR`: WCAG 2.2's ratio with the 0.04045 threshold, unrounded, so a
 * pair at 4.496 fails.
 */

import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

import { CARD_STATE_CLASSES } from '../../src/renderer/src/components/queue/QueueCard'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')
const TOKEN_FILE = resolve(repoRoot, 'ui/src/renderer/src/styles.css')

const FLOOR = 4.5

type Rgb = [number, number, number]
type Pair = [label: string, fg: Rgb, bg: Rgb]

function parseThemeBlock(css: string, opener: string): Map<string, string> {
  const start = css.indexOf(opener)
  if (start === -1) {
    throw new Error(`theme block ${opener} not found in styles.css`)
  }
  const end = css.indexOf('\n}', start)
  if (end === -1) {
    throw new Error(`theme block ${opener} is unterminated`)
  }
  const body = css.slice(start + opener.length, end)
  const map = new Map<string, string>()
  for (const match of body.matchAll(/(--[\w-]+)\s*:\s*([^;]+);/g)) {
    map.set(match[1], match[2].trim())
  }
  return map
}

function themes(): { dark: Map<string, string>; light: Map<string, string> } {
  const css = readFileSync(TOKEN_FILE, 'utf-8')
  return {
    dark: parseThemeBlock(css, '@theme {'),
    light: parseThemeBlock(css, ':root:not(.dark) {'),
  }
}

function toRgb(map: Map<string, string>, token: string): Rgb {
  const value = map.get(token)
  if (value === undefined) {
    throw new Error(`token ${token} is not defined in this theme block`)
  }
  const match = /^#([0-9a-fA-F]{6})$/.exec(value)
  if (match === null) {
    throw new Error(`token ${token} is not a plain 6-digit hex: ${value}`)
  }
  const int = Number.parseInt(match[1], 16)
  return [(int >> 16) & 0xff, (int >> 8) & 0xff, int & 0xff]
}

/** Source-over composite, each channel rounded half up to 8 bits as a browser paints. */
function over(top: Rgb, alpha: number, backdrop: Rgb): Rgb {
  return [0, 1, 2].map((i) => Math.round(top[i] * alpha + backdrop[i] * (1 - alpha))) as Rgb
}

function luminance(rgb: Rgb): number {
  const channel = (raw: number): number => {
    const c = raw / 255
    return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4
  }
  return 0.2126 * channel(rgb[0]) + 0.7152 * channel(rgb[1]) + 0.0722 * channel(rgb[2])
}

function ratio(a: Rgb, b: Rgb): number {
  const la = luminance(a)
  const lb = luminance(b)
  const [hi, lo] = la >= lb ? [la, lb] : [lb, la]
  return (hi + 0.05) / (lo + 0.05)
}

/** The alpha of the `bg-accent/N` class in a card state's classes. */
function washAlpha(classes: string): number {
  const match = /(?:^|\s)bg-accent\/(\d+)(?=\s|$)/.exec(classes)
  if (match === null) {
    throw new Error(`no bg-accent/N class in "${classes}"`)
  }
  return Number(match[1]) / 100
}

/** Each pair below the floor, with its ratio, so a failure names every short pair. */
function belowFloor(pairs: Pair[]): Array<{ pair: string; ratio: number }> {
  return pairs
    .map(([pair, fg, bg]) => ({ pair, ratio: ratio(fg, bg) }))
    .filter((row) => row.ratio < FLOOR)
}

/** Accent labels on the accent at `alpha` over the page, a card and a selected queue card. */
function tintPairs(alpha: number): Pair[] {
  const { light } = themes()
  const accent = toRgb(light, '--color-accent')
  const page = toRgb(light, '--color-bg')
  const selectedCard = over(accent, washAlpha(CARD_STATE_CLASSES['checkbox-selected']), page)
  return [
    ['over the page', accent, over(accent, alpha, page)],
    ['over a card', accent, over(accent, alpha, toRgb(light, '--color-bg-elevated'))],
    ['over a selected queue card', accent, over(accent, alpha, selectedCard)],
  ]
}

describe('MEU-126 light accent contrast', () => {
  it('AC-126.1 white labels on the light accent read at 4.5:1', () => {
    const { light } = themes()
    expect(
      belowFloor([['accent-fg on accent', toRgb(light, '--color-accent-fg'), toRgb(light, '--color-accent')]]),
    ).toEqual([])
  })

  it('AC-126.2 white labels on the light accent hover read at 4.5:1', () => {
    const { light } = themes()
    expect(
      belowFloor([
        ['accent-fg on accent-hover', toRgb(light, '--color-accent-fg'), toRgb(light, '--color-accent-hover')],
      ]),
    ).toEqual([])
  })

  it('AC-126.3 accent labels on the 12% tint read at 4.5:1 over the page, a card and a selected queue card', () => {
    expect(belowFloor(tintPairs(0.12))).toEqual([])
  })

  it('AC-126.4 accent labels on the 20% tint read at 4.5:1 over the page, a card and a selected queue card', () => {
    expect(belowFloor(tintPairs(0.2))).toEqual([])
  })

  it('AC-126.5 a selected segmented option reads at 4.5:1 over its group and the page', () => {
    const { light } = themes()
    const accent = toRgb(light, '--color-accent')
    expect(
      belowFloor([
        ['over its group', accent, over(accent, 0.15, toRgb(light, '--color-surface-0'))],
        ['over the page', accent, over(accent, 0.15, toRgb(light, '--color-bg'))],
      ]),
    ).toEqual([])
  })

  it('AC-126.6 accent text reads at 4.5:1 on the page and a card', () => {
    const { light } = themes()
    const accent = toRgb(light, '--color-accent')
    expect(
      belowFloor([
        ['on the page', accent, toRgb(light, '--color-bg')],
        ['on a card', accent, toRgb(light, '--color-bg-elevated')],
      ]),
    ).toEqual([])
  })

  it('AC-126.7 the dark accent tokens are unchanged and the ratio helper is calibrated', () => {
    const { dark, light } = themes()
    expect({
      accent: dark.get('--color-accent'),
      accentFg: dark.get('--color-accent-fg'),
      accentHover: dark.get('--color-accent-hover'),
      lightAccentFg: light.get('--color-accent-fg'),
    }).toEqual({ accent: '#8be9fd', accentFg: '#282a36', accentHover: '#a6f0ff', lightAccentFg: '#ffffff' })
    expect(ratio([0, 0, 0], [255, 255, 255])).toBeCloseTo(21, 10)
    const grey = ratio([0x76, 0x76, 0x76], [255, 255, 255])
    expect(grey).toBeGreaterThanOrEqual(4.54)
    expect(grey).toBeLessThan(4.55)
  })
})
