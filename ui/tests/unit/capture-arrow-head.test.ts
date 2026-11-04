/** @vitest-environment node */

import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

type Point = [number, number]
type ArrowCase = {
  from: Point
  to: Point
  stroke: number
  head: number | null
  left: Point | null
  right: Point | null
  shaft_end: Point | null
}

const GEOMETRY = JSON.parse(
  readFileSync(resolve(__dirname, '../e2e/fixtures/capture-geometry.json'), 'utf8')
) as { arrows: ArrowCase[] }

function expectPoint(actual: Point | null, expected: Point, label: string): void {
  expect(actual, label).not.toBeNull()
  expect(Math.abs((actual as Point)[0] - expected[0]), `${label} x`).toBeLessThanOrEqual(1e-9)
  expect(Math.abs((actual as Point)[1] - expected[1]), `${label} y`).toBeLessThanOrEqual(1e-9)
}

function cross(o: Point, a: Point, p: Point): number {
  return (a[0] - o[0]) * (p[1] - o[1]) - (a[1] - o[1]) * (p[0] - o[0])
}

function insideTriangle(p: Point, a: Point, b: Point, c: Point): boolean {
  const signs = [cross(a, b, p), cross(b, c, p), cross(c, a, p)]
  return signs.every((s) => s >= -1e-9) || signs.every((s) => s <= 1e-9)
}

describe('MEU-59 arrow head', () => {
  it('AC-59.2 preview vertices match ARROWHEAD_FORMULA for a horizontal stroke-3 arrow', async () => {
    const mod = await import('../../src/renderer/src/features/capture/capture-arrow-head')
    const verts = mod.arrowheadVertices([0, 0], [100, 0], 3)
    const head = Math.max(10, 5 * 3)
    const left = [100 - head * Math.cos(0 - 0.45), 0 - head * Math.sin(0 - 0.45)]
    const right = [100 - head * Math.cos(0 + 0.45), 0 - head * Math.sin(0 + 0.45)]
    expect(verts.tip).toEqual([100, 0])
    expect(verts.left[0]).toBeCloseTo(left[0])
    expect(verts.left[1]).toBeCloseTo(left[1])
    expect(verts.right[0]).toBeCloseTo(right[0])
    expect(verts.right[1]).toBeCloseTo(right[1])
    expect(head).toBe(15)
    expectPoint(verts.left, GEOMETRY.arrows[0].left as Point, 'ARROW_CASES horizontal left')
    expectPoint(verts.right, GEOMETRY.arrows[0].right as Point, 'ARROW_CASES horizontal right')
  })
})

describe('MEU-83 arrow geometry', () => {
  it('AC-83.1 ARROW_HEAD, arrowheadVertices and arrowShaftEnd reproduce every ARROW_CASES entry to 1e-9', async () => {
    const mod = await import('../../src/renderer/src/features/capture/capture-arrow-head')
    expect(mod.ARROWHEAD_LENGTH_FACTOR).toBe(5)
    expect(mod.ARROWHEAD_ANGLE_RAD).toBe(0.45)
    expect(mod.ARROWHEAD_MIN_PX).toBe(10)
    expect(mod.ARROW_SHAFT_OVERLAP_PX).toBe(1)
    expect(GEOMETRY.arrows).toHaveLength(5)
    for (const c of GEOMETRY.arrows) {
      const label = `${c.from} -> ${c.to} s${c.stroke}`
      const end = mod.arrowShaftEnd(c.from, c.to, c.stroke)
      if (c.shaft_end === null) {
        expect(end, label).toBeNull()
      } else {
        expectPoint(end, c.shaft_end, `${label} shaft_end`)
      }
      if (c.head === null) {
        // Zero length: the legacy from->to shaft and no head (SHAFT_END, 09:366).
        expect(Math.hypot(c.to[0] - c.from[0], c.to[1] - c.from[1]), label).toBe(0)
        expect(end, label).toEqual(c.to)
        continue
      }
      expect(Math.max(mod.ARROWHEAD_MIN_PX, mod.ARROWHEAD_LENGTH_FACTOR * c.stroke), label).toBe(c.head)
      const verts = mod.arrowheadVertices(c.from, c.to, c.stroke)
      expect(verts.tip, label).toEqual(c.to)
      expectPoint(verts.left, c.left as Point, `${label} left`)
      expectPoint(verts.right, c.right as Point, `${label} right`)
    }
  })

  it('AC-83.1 negative: a shaft ending at the tip does not reproduce the horizontal case', () => {
    const horizontal = GEOMETRY.arrows[0]
    expect(horizontal.shaft_end).not.toBeNull()
    expect(Math.abs((horizontal.shaft_end as Point)[0] - horizontal.to[0])).toBeGreaterThan(1)
  })

  it('AC-83.3 SHAFT_INSIDE_HEAD: both flat-cap corners of the shaft end lie inside the head for strokes 1-64', async () => {
    const mod = await import('../../src/renderer/src/features/capture/capture-arrow-head')
    const directions = GEOMETRY.arrows.filter((c) => c.head !== null)
    expect(directions).toHaveLength(4)
    for (const c of directions) {
      const length = Math.hypot(c.to[0] - c.from[0], c.to[1] - c.from[1])
      const u: Point = [(c.to[0] - c.from[0]) / length, (c.to[1] - c.from[1]) / length]
      const normal: Point = [-u[1], u[0]]
      const from: Point = [c.to[0] - 1000 * u[0], c.to[1] - 1000 * u[1]]
      for (let stroke = 1; stroke <= 64; stroke += 1) {
        const label = `${c.from} -> ${c.to} s${stroke}`
        const verts = mod.arrowheadVertices(from, c.to, stroke)
        const end = mod.arrowShaftEnd(from, c.to, stroke) as Point
        expect(end, label).not.toBeNull()
        for (const side of [1, -1]) {
          const corner: Point = [end[0] + side * (stroke / 2) * normal[0], end[1] + side * (stroke / 2) * normal[1]]
          expect(insideTriangle(corner, verts.tip, verts.left, verts.right), `${label} corner ${side}`).toBe(true)
          // Negative: with the shaft ending at the tip, the same corner falls outside the head.
          const atTip: Point = [c.to[0] + side * (stroke / 2) * normal[0], c.to[1] + side * (stroke / 2) * normal[1]]
          expect(insideTriangle(atTip, verts.tip, verts.left, verts.right), `${label} tip corner ${side}`).toBe(false)
        }
      }
    }
  })
})
