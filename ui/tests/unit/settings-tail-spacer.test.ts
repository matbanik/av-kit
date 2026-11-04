import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

import { describe, expect, it } from 'vitest'

import {
  SECTION_SCROLL_MARGIN,
  belowLastTop,
  tailSpacerHeight,
} from '../../src/renderer/src/features/settings/settings-tail-spacer'

/**
 * MEU-70 TAIL_SPACER_HEIGHT and SECTION_SCROLL_MARGIN (Session 31; defined once in
 * docs/execution/plans/2026-10-10-gui-polish-residuals/implementation-plan.md).
 */

const repoRoot = resolve(__dirname, '../../..')

describe('MEU-70 tail spacer height (TAIL_SPACER_HEIGHT)', () => {
  it('AC-70.1 exports the pure height function and the scroll margin', () => {
    expect(typeof tailSpacerHeight).toBe('function')
    expect(typeof belowLastTop).toBe('function')
    expect(SECTION_SCROLL_MARGIN).toBe(16)
  })

  it('AC-70.1 worked examples', () => {
    expect(tailSpacerHeight({ clientHeight: 700, belowLastTop: 300, margin: 16 })).toBe(384)
    expect(tailSpacerHeight({ clientHeight: 700, belowLastTop: 900, margin: 16 })).toBe(0)
    expect(tailSpacerHeight({ clientHeight: 700, belowLastTop: 683.5, margin: 16 })).toBe(1)
  })

  it('AC-70.1 the measurement is a fixpoint: the spacer it adds does not change the next measurement', () => {
    // Scroller 700 tall; the last section's top sits 1200 px into the content; 300 px of content follow it.
    const without = belowLastTop({ scrollHeight: 1500, spacerHeight: 0, lastTopInViewport: 1200, scrollerTop: 0, scrollTop: 0 })
    const first = tailSpacerHeight({ clientHeight: 700, belowLastTop: without, margin: SECTION_SCROLL_MARGIN })
    expect(first).toBe(384)
    // With the spacer in place and the page scrolled to its new maximum, the last section's top is at the margin.
    const maxScroll = 1500 + first - 700
    const withSpacer = belowLastTop({
      scrollHeight: 1500 + first,
      spacerHeight: first,
      lastTopInViewport: 1200 - maxScroll,
      scrollerTop: 0,
      scrollTop: maxScroll,
    })
    expect(withSpacer).toBe(without)
    expect(tailSpacerHeight({ clientHeight: 700, belowLastTop: withSpacer, margin: SECTION_SCROLL_MARGIN })).toBe(first)
    expect(1200 - maxScroll).toBe(SECTION_SCROLL_MARGIN)
  })

  it('AC-70.1 non-finite or negative input fails closed to 0', () => {
    const good = { clientHeight: 700, belowLastTop: 300, margin: 16 }
    for (const field of ['clientHeight', 'belowLastTop', 'margin'] as const) {
      for (const bad of [Number.NaN, Number.POSITIVE_INFINITY, -1]) {
        const height = tailSpacerHeight({ ...good, [field]: bad })
        expect(height, `${field}=${bad}`).toBe(0)
      }
    }
  })

  it('AC-70.1 the result is never negative and always an integer', () => {
    for (const below of [0, 0.25, 99.9, 683.99, 684, 5000]) {
      const height = tailSpacerHeight({ clientHeight: 700, belowLastTop: below, margin: 16 })
      expect(height).toBeGreaterThanOrEqual(0)
      expect(Number.isInteger(height)).toBe(true)
    }
  })
})

describe('MEU-70 test-id registration (NEW_TESTIDS)', () => {
  it('AC-70.8 settings-tail-spacer is registered in the MEU-70 block at the end and used literally', () => {
    const ids = readFileSync(resolve(repoRoot, 'ui/tests/e2e/test-ids.ts'), 'utf8')
    const marker = '// MEU-70 Settings section emphasis (additive IDs).'
    expect(ids).toContain(marker)
    const tail = ids.split(marker)[1] ?? ''
    expect(tail).toContain("export const SETTINGS_TAIL_SPACER = 'settings-tail-spacer'")
    expect(ids.indexOf(marker)).toBeGreaterThan(ids.indexOf('// MEU-66 Capture viewport zoom (additive IDs).'))
    expect(ids.split("'settings-tail-spacer'")).toHaveLength(2)
    const page = readFileSync(resolve(repoRoot, 'ui/src/renderer/src/features/settings/SettingsPage.tsx'), 'utf8')
    expect(page).toContain('data-testid="settings-tail-spacer"')
  })
})
