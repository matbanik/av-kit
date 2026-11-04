/** @vitest-environment node */

import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const GEOMETRY = JSON.parse(
  readFileSync(resolve(__dirname, '../e2e/fixtures/capture-geometry.json'), 'utf8')
) as { segoe_ascent: Record<string, number> }

describe('MEU-59 text metrics', () => {
  it('AC-59.19 TEXT_MODULE reports start/alphabetic anchors and a bg plate box', async () => {
    const mod = await import('../../src/renderer/src/features/capture/capture-text-metrics')
    expect(mod.SVG_TEXT_ANCHOR).toBe('start')
    expect(mod.SVG_DOMINANT_BASELINE).toBe('alphabetic')
    const box = mod.textBackgroundBox({ x: 10, y: 20, text: 'Hi', font_size: 16 })
    expect(box).toEqual({ x: 10, y: 26, width: 15, height: 12 })
  })
})

describe('MEU-82 text baseline', () => {
  it('AC-82.1 segoeAscentPx equals GEOMETRY_FIXTURE.segoe_ascent and exports SEGOE_UNITS', async () => {
    const segoe = await import('../../src/renderer/src/features/capture/capture-segoe-metrics')
    const mod = await import('../../src/renderer/src/features/capture/capture-text-metrics')
    expect(segoe.SEGOE_UI_UNITS_PER_EM).toBe(2048)
    expect(segoe.SEGOE_UI_ASCENDER).toBe(2210)
    const sizes = Object.keys(GEOMETRY.segoe_ascent).map(Number)
    expect(sizes).toEqual([1, 8, 12, 16, 20, 24, 32, 38, 48, 64, 72, 96, 128, 177, 215, 354, 500])
    for (const size of sizes) {
      expect(mod.segoeAscentPx(size), `size ${size}`).toBe(GEOMETRY.segoe_ascent[String(size)])
    }
  })

  it('AC-82.1 the naive ceil(size*2210/2048) differs at 38, so the fixture can catch it', async () => {
    const mod = await import('../../src/renderer/src/features/capture/capture-text-metrics')
    for (const size of [38, 177, 215, 354]) {
      expect(Math.ceil((size * 2210) / 2048), `size ${size}`).not.toBe(mod.segoeAscentPx(size))
    }
    expect(Math.ceil((38 * 2210) / 2048)).toBe(42)
    expect(mod.segoeAscentPx(38)).toBe(41)
  })

  it('AC-82.3 svgTextBaselineY puts the alphabetic baseline at y + ascent', async () => {
    const mod = await import('../../src/renderer/src/features/capture/capture-text-metrics')
    expect(mod.SVG_DOMINANT_BASELINE).toBe('alphabetic')
    expect(mod.svgTextBaselineY({ y: 20, font_size: 16 })).toBe(38)
    expect(mod.svgTextBaselineY({ y: 30, font_size: 32 })).toBe(65)
    expect(mod.svgTextBaselineY({ y: 5, font_size: 0 })).toBe(5 + mod.segoeAscentPx(1))
  })
})
