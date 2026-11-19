// @vitest-environment node
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

// MEU-161 (Session 97): the preview's text plate follows the bake. The fixture holds the box the
// bake paints for each case (adapter.text_plate_box as [l, t, r - l + 1, b - t + 1]), written by
// the plan's plate-fixture.py and guarded against Pillow by test_capture_text_plates.py.
// Each test loads the modules by dynamic import(), so a missing export fails an assertion.

type Box = { x: number; y: number; width: number; height: number }
type Section = { x: number; y: number; sizes: number[]; cases: { text: string; boxes: number[][] }[] }
type Plates = { breadth: Section; matrix: Section }

const FIXTURE = resolve(dirname(fileURLToPath(import.meta.url)), '../e2e/fixtures/capture-text-plates.json')

function plates(): Plates {
  return JSON.parse(readFileSync(FIXTURE, 'utf8')) as Plates
}

/** Per side l, t, r, b: the preview's inclusive edge minus the painted one. */
function sides(box: Box, painted: number[]): number[] {
  const [x, y, width, height] = painted
  return [
    box.x - x,
    box.y - y,
    box.x + box.width - 1 - (x + width - 1),
    box.y + box.height - 1 - (y + height - 1),
  ]
}

function asBox(painted: number[]): Box {
  const [x, y, width, height] = painted
  return { x, y, width, height }
}

/** The four matrix cases the model does not paint exactly, each 1 px off on one side (D-1244). */
const MATRIX_RESIDUALS: Record<string, Box> = {
  '"Hello\\nW\\ngy"@32': { x: 10, y: 31, width: 76, height: 111 },
  '"Hello\\nW\\ngy"@64': { x: 10, y: 43, width: 149, height: 211 },
  '"i\\nWWWW"@8': { x: 10, y: 23, width: 29, height: 20 },
  '"Hello"@8': { x: 10, y: 23, width: 20, height: 7 },
}

describe('MEU-161 text plate metrics', () => {
  it('AC-161.3 SEGOE_UI_GLYPH_UNITS holds the 95 printable ASCII glyphs in font units', async () => {
    const mod = (await import('../../src/renderer/src/features/capture/capture-segoe-metrics')) as unknown as Record<string, unknown>
    expect(typeof mod.SEGOE_UI_GLYPH_UNITS, 'SEGOE_UI_GLYPH_UNITS is exported').toBe('object')
    const glyphs = (mod.SEGOE_UI_GLYPH_UNITS ?? {}) as Record<string, Record<string, unknown>>
    const printable = Array.from({ length: 95 }, (_, i) => String.fromCharCode(0x20 + i))
    expect(Object.keys(glyphs).sort(), 'the glyph keys').toEqual([...printable].sort())
    for (const [ch, glyph] of Object.entries(glyphs)) {
      expect(Object.keys(glyph).sort(), `${JSON.stringify(ch)} fields`).toEqual(['adv', 'b', 'l', 'r', 't'])
      for (const value of Object.values(glyph)) {
        expect(Number.isInteger(value), `${JSON.stringify(ch)} ${String(value)} is whole`).toBe(true)
      }
    }
    expect(mod.SEGOE_UI_UNITS_PER_EM, 'SEGOE_UI_UNITS_PER_EM').toBe(2048)
    expect(mod.SEGOE_UI_ASCENDER, 'SEGOE_UI_ASCENDER').toBe(2210)
    expect(typeof mod.SEGOE_UI_KERN_UNITS, 'SEGOE_UI_KERN_UNITS is exported').toBe('object')
    const kerns = (mod.SEGOE_UI_KERN_UNITS ?? {}) as Record<string, unknown>
    expect(Object.keys(kerns), 'the kerning pairs').toHaveLength(372)
    for (const [pair, units] of Object.entries(kerns)) {
      expect(pair.length === 2 && [...pair].every((ch) => printable.includes(ch)), `${JSON.stringify(pair)} is two printable characters`).toBe(true)
      expect(Number.isInteger(units), `${JSON.stringify(pair)} ${String(units)} is whole`).toBe(true)
    }
    expect('SEGOE_LA_GLYPHS' in mod, 'the 16 px table is gone').toBe(false)
  })

  it('AC-161.5 PREVIEW_FOLLOWS_BAKE breadth', async () => {
    const { textBackgroundBox } = await import('../../src/renderer/src/features/capture/capture-text-metrics')
    const { breadth } = plates()
    let cases = 0
    let exact = 0
    let worst = 0
    const over: string[] = []
    for (const item of breadth.cases) {
      breadth.sizes.forEach((size, i) => {
        const box = textBackgroundBox({ x: breadth.x, y: breadth.y, text: item.text, font_size: size })
        const diff = sides(box, item.boxes[i] ?? [])
        const most = Math.max(...diff.map((d) => Math.abs(d)))
        cases += 1
        if (most === 0) exact += 1
        if (most > 1) over.push(`${JSON.stringify(item.text)}@${size} l,t,r,b ${diff.join(',')}`)
        worst = Math.max(worst, most)
      })
    }
    console.log(`AC-161.5 breadth: ${cases} cases, ${exact} exact, ${over.length} over 1 px, worst ${worst}`)
    for (const line of over) console.log(`  over 1 px: ${line}`)
    expect(cases, 'breadth cases').toBe(2448)
    expect(exact, 'cases exact on all four sides').toBeGreaterThanOrEqual(1702)
    expect(over.length, 'cases over 1 px on a side').toBeLessThanOrEqual(5)
    expect(worst, 'the largest side difference').toBeLessThanOrEqual(2)
  })

  it('AC-161.5 PREVIEW_FOLLOWS_BAKE matrix', async () => {
    const { textBackgroundBox } = await import('../../src/renderer/src/features/capture/capture-text-metrics')
    const { matrix } = plates()
    let cases = 0
    let exact = 0
    const named: string[] = []
    for (const item of matrix.cases) {
      matrix.sizes.forEach((size, i) => {
        const label = `${JSON.stringify(item.text)}@${size}`
        const painted = item.boxes[i] ?? []
        const box = textBackgroundBox({ x: matrix.x, y: matrix.y, text: item.text, font_size: size })
        cases += 1
        const residual = MATRIX_RESIDUALS[label]
        if (residual === undefined) {
          expect(box, label).toEqual(asBox(painted))
          exact += 1
          return
        }
        named.push(label)
        expect(box, `${label} the named residual`).toEqual(residual)
        const diff = sides(box, painted)
        expect(diff.filter((d) => d !== 0), `${label} differs by 1 px on one side`).toHaveLength(1)
        expect(Math.max(...diff.map((d) => Math.abs(d))), `${label} by 1 px`).toBe(1)
      })
    }
    console.log(`AC-161.5 matrix: ${cases} cases, ${exact} exact, named ${named.join(' ')}`)
    expect(cases, 'matrix cases').toBe(40)
    expect(exact, 'matrix cases exact').toBe(36)
    expect(named.sort(), 'the named residuals').toEqual(Object.keys(MATRIX_RESIDUALS).sort())
  })

  it('AC-161.5 PREVIEW_FOLLOWS_BAKE the fidelity marks', async () => {
    const { textBackgroundBox } = await import('../../src/renderer/src/features/capture/capture-text-metrics')
    expect(textBackgroundBox({ x: 20, y: 30, text: 'Hi', font_size: 32 }), "'Hi' at 32").toEqual({ x: 20, y: 42, width: 32, height: 24 })
    expect(textBackgroundBox({ x: 20, y: 16, text: 'Hi\n\nHi\n', font_size: 32 }), "'Hi\\n\\nHi\\n' at 32").toEqual({
      x: 20,
      y: 28,
      width: 32,
      height: 106,
    })
  })
})
