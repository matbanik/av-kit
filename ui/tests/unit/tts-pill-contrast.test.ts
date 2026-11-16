/** @vitest-environment jsdom */

/**
 * MEU-149 — the TTS status pill reads at 4.5:1 in both themes (AC-149.5, `PILL_CONTRAST_TEST`).
 *
 * Each job status renders the shipped `StatusChip` with its `TTS_STATUS_TONE`, and the
 * fill token, its alpha and the label token are read from the classes the chip ships
 * (`bg-<token>/<n>`, `text-<token>`). Every colour is read from `TOKEN_FILE` at test time:
 * dark is the `@theme {` block, light is `:root:not(.dark) {` laid over dark. A token or
 * chip edit moves these ratios with nothing to re-pin (D-960).
 *
 * `TINT_MODEL` and `CONTRAST_FLOOR` as `light-accent-contrast.test.ts` defines them: the
 * fill is composited source-over per channel in sRGB, rounded half up, on each backdrop
 * the run bar can sit on; the ratio is WCAG 2.2's with the 0.04045 threshold, unrounded.
 */

import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { cleanup, render } from '@testing-library/react'
import { createElement } from 'react'
import { afterEach, describe, expect, it } from 'vitest'

import { StatusChip, type StatusChipTone } from '../../src/renderer/src/components/ui/StatusChip'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')
const TOKEN_FILE = resolve(repoRoot, 'ui/src/renderer/src/styles.css')

const FLOOR = 4.5
const BACKDROPS = ['--color-bg', '--color-bg-elevated', '--color-surface-0'] as const

type Rgb = [number, number, number]
type Theme = Map<string, string>
type Controls = {
  JOB_STATUSES: readonly string[]
  TTS_STATUS_TONE?: Record<string, StatusChipTone>
}

function parseThemeBlock(css: string, opener: string): Theme {
  const start = css.indexOf(opener)
  if (start === -1) {
    throw new Error(`theme block ${opener} not found in styles.css`)
  }
  const end = css.indexOf('\n}', start)
  if (end === -1) {
    throw new Error(`theme block ${opener} is unterminated`)
  }
  const body = css.slice(start + opener.length, end)
  const map: Theme = new Map()
  for (const match of body.matchAll(/(--[\w-]+)\s*:\s*([^;]+);/g)) {
    map.set(match[1], match[2].trim())
  }
  return map
}

function themes(): { dark: Theme; light: Theme } {
  const css = readFileSync(TOKEN_FILE, 'utf-8')
  const dark = parseThemeBlock(css, '@theme {')
  return { dark, light: new Map([...dark, ...parseThemeBlock(css, ':root:not(.dark) {')]) }
}

function toRgb(theme: Theme, token: string): Rgb {
  const value = theme.get(token)
  if (value === undefined) {
    throw new Error(`token ${token} is not defined in this theme`)
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

/** The class tokens the shipped chip renders for `tone`. */
function chipClasses(tone: StatusChipTone): string[] {
  const { container } = render(createElement(StatusChip, { label: 'Status', tone, testId: 'pill' }))
  const chip = container.querySelector('[data-testid="pill"]')
  expect(chip, `StatusChip renders for ${tone}`).not.toBeNull()
  const classes = (chip as HTMLElement).className.split(/\s+/).filter((name) => name !== '')
  cleanup()
  return classes
}

/** The chip's one `bg-<token>/<n>` fill and its one `text-<token>` colour that the theme defines. */
function chipColours(classes: string[], theme: Theme): { fill: string; alpha: number; label: string } {
  const fills = classes.flatMap((name) => {
    const match = /^bg-([a-z][\w-]*)\/(\d+)$/.exec(name)
    return match === null ? [] : [{ fill: `--color-${match[1]}`, alpha: Number(match[2]) / 100 }]
  })
  const labels = classes.flatMap((name) => {
    const match = /^text-([a-z][\w-]*)$/.exec(name)
    return match !== null && theme.has(`--color-${match[1]}`) ? [`--color-${match[1]}`] : []
  })
  expect(fills, `one tinted fill in ${classes.join(' ')}`).toHaveLength(1)
  expect(labels, `one label colour in ${classes.join(' ')}`).toHaveLength(1)
  return { ...fills[0], label: labels[0] }
}

describe('MEU-149 TTS status pill contrast', () => {
  afterEach(() => {
    cleanup()
  })

  it('AC-149.5 every TTS status pill reads at 4.5:1 in both themes', async () => {
    const controls = (await import('../../src/renderer/src/features/tts/tts-controls')) as unknown as Controls
    expect(typeof controls.TTS_STATUS_TONE).toBe('object')
    const tones = controls.TTS_STATUS_TONE as Record<string, StatusChipTone>
    const { dark, light } = themes()
    const pairs: Array<{ pair: string; ratio: number }> = []
    for (const [name, theme] of [['dark', dark], ['light', light]] as const) {
      for (const status of controls.JOB_STATUSES) {
        const { fill, alpha, label } = chipColours(chipClasses(tones[status]), theme)
        for (const backdrop of BACKDROPS) {
          pairs.push({
            pair: `${name} ${status}: ${label} on ${fill} at ${String(alpha)} over ${backdrop}`,
            ratio: ratio(toRgb(theme, label), over(toRgb(theme, fill), alpha, toRgb(theme, backdrop))),
          })
        }
      }
    }
    expect(pairs).toHaveLength(36)
    expect(pairs.filter((row) => row.ratio < FLOOR)).toEqual([])
  })

  it('AC-149.5 the ratio helper measures the old solid fills below the floor', () => {
    // Calibration: the old dark Generating pill was text-fg on a solid bg-accent.
    const { dark } = themes()
    const old = ratio(toRgb(dark, '--color-fg'), toRgb(dark, '--color-accent'))
    expect(old.toFixed(2)).toBe('1.30')
    expect(old).toBeLessThan(FLOOR)
  })
})
