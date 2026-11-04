/** @vitest-environment node */

import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

import { parseAnnotateBody } from '../../src/renderer/src/features/capture/capture-annotate'

const NAMED = ['red', 'orange', 'yellow', 'green', 'blue', 'white', 'black'] as const

describe('MEU-59 annotate schema', () => {
  it('AC-59.10 rejects alphabetic colors outside NAMED_COLORS', () => {
    const body = parseAnnotateBody({
      annotations: [
        {
          type: 'arrow',
          from: [0, 0],
          to: [8, 8],
          color: 'chartreuse',
          stroke_width: 2,
        },
      ],
    })
    expect(body).toBeNull()
    for (const color of NAMED) {
      const ok = parseAnnotateBody({
        annotations: [
          {
            type: 'arrow',
            from: [0, 0],
            to: [8, 8],
            color,
            stroke_width: 2,
          },
        ],
      })
      expect(ok).not.toBeNull()
    }
  })

  it('AC-59.11 circle and marker types parse to null', () => {
    for (const forbidden of ['circle', 'marker'] as const) {
      const body = parseAnnotateBody({
        annotations: [{ type: forbidden, x: 1, y: 1, r: 4 }],
      })
      expect(body).toBeNull()
    }
    const rect = parseAnnotateBody({
      annotations: [
        {
          type: 'rect',
          x: 0,
          y: 0,
          width: 8,
          height: 8,
          color: 'red',
          stroke_width: 1,
        },
      ],
    })
    expect(rect).not.toBeNull()
  })
})

const OPENAPI_COMMITTED = resolve(dirname(fileURLToPath(import.meta.url)), '../../../openapi.committed.json')

type BlockBounds = { minimum: number; maximum: number; default: number }

describe('MEU-90 renderer annotate schema (REGION_DTO)', () => {
  it('AC-90.4 renderer schema accepts a pixelate with block_size inside the committed PIXELATE_BLOCK bounds', () => {
    const pixelate = { type: 'pixelate', x: 2, y: 3, width: 20, height: 10, block_size: 7 }
    const body = parseAnnotateBody({ annotations: [pixelate] })
    expect(body).not.toBeNull()
    expect(body?.annotations).toEqual([pixelate])
    const committed = JSON.parse(readFileSync(OPENAPI_COMMITTED, 'utf8')) as {
      components: { schemas: Record<string, { properties: Record<string, BlockBounds> }> }
    }
    const block = committed.components.schemas.PixelateAnnotationIn?.properties.block_size as BlockBounds
    expect(block).toBeDefined()
    expect([block.minimum, block.maximum, block.default]).toEqual([2, 100, 10])
    const accepts = (value: number): boolean =>
      parseAnnotateBody({ annotations: [{ ...pixelate, block_size: value }] }) !== null
    expect([block.minimum - 1, block.minimum, block.maximum, block.maximum + 1].map(accepts)).toEqual([
      false,
      true,
      true,
      false,
    ])
    // Negative: block_size is required in the renderer; extra keys and fractional values are refused.
    const unsized = { type: 'pixelate', x: 2, y: 3, width: 20, height: 10 }
    for (const bad of [unsized, { ...pixelate, color: '#FF0000' }, { ...pixelate, width: 1.5 }, { ...pixelate, block_size: 2.5 }]) {
      expect(parseAnnotateBody({ annotations: [bad] }), JSON.stringify(bad)).toBeNull()
    }
  })
})

describe('MEU-91 renderer annotate schema (REGION_DTO)', () => {
  it('AC-91.4 renderer schema accepts an eraser (a rectangle only) and echoes it', () => {
    const eraser = { type: 'eraser', x: 2, y: 3, width: 20, height: 10 }
    const body = parseAnnotateBody({ annotations: [eraser] })
    expect(body).not.toBeNull()
    expect(body?.annotations).toEqual([eraser])
    // Negative: an eraser has no color and no block; its geometry is integer and complete.
    const noX = { type: 'eraser', y: 3, width: 20, height: 10 }
    for (const bad of [{ ...eraser, color: '#FF0000' }, { ...eraser, block_size: 10 }, { ...eraser, width: 1.5 }, noX]) {
      expect(parseAnnotateBody({ annotations: [bad] }), JSON.stringify(bad)).toBeNull()
    }
  })
})
