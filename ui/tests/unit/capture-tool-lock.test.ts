/** @vitest-environment node */

import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import type { QueryClient } from '@tanstack/react-query'
import { describe, expect, it } from 'vitest'

import type { Annotation } from '../../src/renderer/src/features/capture/capture-annotate'
import * as cropBar from '../../src/renderer/src/features/capture/CaptureCropBar'
import type { ImagePoint } from '../../src/renderer/src/features/capture/capture-fit-map'
import * as importModule from '../../src/renderer/src/features/capture/capture-import'
import * as mods from '../../src/renderer/src/features/capture/capture-modifiers'
import * as styleStore from '../../src/renderer/src/features/capture/capture-style-store'
import * as lock from '../../src/renderer/src/features/capture/capture-tool-lock'
import * as toolbar from '../../src/renderer/src/features/capture/capture-toolbar'
import type { BoxMark, HandleId } from '../../src/renderer/src/features/capture/capture-transform'
import type { CaptureTool, SurfacePointer } from '../../src/renderer/src/features/capture/CaptureViewport'
import * as lockHook from '../../src/renderer/src/features/capture/useCaptureToolLock'
import * as settingsSchemas from '../../src/renderer/src/features/settings/settings-schemas'
import * as editable from '../../src/renderer/src/lib/editable-target'
import * as registry from '../../src/renderer/src/registry/commandRegistry'
import * as shortcuts from '../../src/renderer/src/registry/shortcuts'

// Session 71b (MEU-143): the tool lock, the tool letters and the draw modifiers as pure names. The
// modules are imported as namespaces and each name's type is asserted first, so a missing one fails by
// assertion. The image is 100x80; a point inside it lies in [0, 99] x [0, 79] (clampImagePoint).

const UI = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const IMAGE_W = 100
const IMAGE_H = 80

/** A draw's two points as the box createDrawnMark makes of them (x = min, width = |dx|). */
function box(bounds: { start: ImagePoint; end: ImagePoint }): { x: number; y: number; width: number; height: number } {
  return {
    x: Math.min(bounds.start.x, bounds.end.x),
    y: Math.min(bounds.start.y, bounds.end.y),
    width: Math.abs(bounds.end.x - bounds.start.x),
    height: Math.abs(bounds.end.y - bounds.start.y),
  }
}

function geometry(mark: BoxMark): [number, number, number, number] {
  return [mark.x, mark.y, mark.width, mark.height]
}

const BOX_40X20: Extract<Annotation, { type: 'rect' }> = {
  type: 'rect',
  x: 30,
  y: 30,
  width: 40,
  height: 20,
  color: '#FF0000',
  stroke_width: 2,
}

describe('MEU-143 tool lock, letters and modifiers (pure)', () => {
  it('AC-143.1 the TS names and their arity', () => {
    expect(typeof lock.readToolLock).toBe('function')
    const read: (data: unknown) => boolean = lock.readToolLock
    expect(read.length).toBe(1)

    expect(typeof styleStore.saveCaptureToolLock).toBe('function')
    const save: (client: QueryClient, locked: boolean) => void = styleStore.saveCaptureToolLock
    expect(save.length).toBe(2)
    const failures: () => number = styleStore.lockSaveFailures
    expect(typeof failures).toBe('function')
    expect(failures.length).toBe(0)
    const subscribe: (listener: () => void) => () => void = styleStore.subscribeLockSaveFailures
    expect(typeof subscribe).toBe('function')
    expect(subscribe.length).toBe(1)

    expect(typeof lockHook.useCaptureToolLock).toBe('function')
    const hook: () => { locked: boolean; setLocked(next: boolean): void; failures: number } = lockHook.useCaptureToolLock
    expect(hook.length).toBe(0)

    const schema = settingsSchemas.captureLockPutSchema
    expect(schema.parse({ tool_lock: false })).toEqual({ tool_lock: false })
    expect(schema.safeParse({ tool_lock: false, arrow_color: '#123456' }).success, 'strict').toBe(false)
    expect(schema.safeParse({ tool_lock: 'false' }).success).toBe(false)
    expect(schema.safeParse({}).success).toBe(false)

    const letters: Readonly<Record<CaptureTool, string>> = toolbar.TOOL_LETTERS
    expect(Object.keys(letters)).toHaveLength(8)
    expect(registry.CAPTURE_TOOL_IDS).toHaveLength(8)

    expect(typeof editable.isEditableTarget).toBe('function')
    const isEditable: (target: EventTarget | null) => boolean = editable.isEditableTarget
    expect(isEditable.length).toBe(1)
    expect(importModule.isEditableTarget, 'capture-import re-exports it').toBe(editable.isEditableTarget)

    expect(cropBar.FIELD_STEP_SHIFT).toBe(10)

    const draw: (
      anchor: ImagePoint,
      point: ImagePoint,
      m: { square: boolean; centre: boolean },
      imageW: number,
      imageH: number,
    ) => { start: ImagePoint; end: ImagePoint } = mods.drawBounds
    expect(typeof draw).toBe('function')
    expect(draw.length).toBe(5)
    const snap: (fixed: ImagePoint, moving: ImagePoint, imageW: number, imageH: number) => ImagePoint = mods.snapArrowEnd
    expect(typeof snap).toBe('function')
    expect(snap.length).toBe(4)
    const keep: (start: BoxMark, handle: HandleId, point: ImagePoint, imageW: number, imageH: number) => BoxMark =
      mods.keepRatioResize
    expect(typeof keep).toBe('function')
    expect(keep.length).toBe(5)

    const altKey: SurfacePointer['altKey'] = false
    expect(typeof altKey).toBe('boolean')
  })

  it('AC-143.6 readToolLock is false only for tool_lock exactly false', () => {
    const on: unknown[] = [
      undefined,
      null,
      {},
      { tool_lock: true },
      { tool_lock: 'false' },
      { tool_lock: 0 },
      { tool_lock: '' },
      { tool_lock: '\uD800' },
      { tool_lock: '\u0007' },
    ]
    for (const data of on) {
      expect(lock.readToolLock(data), JSON.stringify(data) ?? 'undefined').toBe(true)
    }
    expect(lock.readToolLock({ tool_lock: false })).toBe(false)
  })

  it('AC-143.15 the letter entries, TOOL_LETTERS, the palette, BOUND_CONTROLS and the toolbar order', () => {
    expect(toolbar.TOOL_LETTERS).toEqual({
      select: 'V',
      arrow: 'A',
      box: 'R',
      highlight: 'H',
      text: 'T',
      redact: 'X',
      eraser: 'E',
      crop: 'C',
    })
    expect([...registry.CAPTURE_TOOL_IDS]).toEqual([
      'capture:tool_select',
      'capture:tool_arrow',
      'capture:tool_box',
      'capture:tool_highlight',
      'capture:tool_text',
      'capture:tool_redact',
      'capture:tool_eraser',
      'capture:tool_crop',
    ])
    const commands = registry.listCommands()
    const ids = commands.map((command) => command.id)
    const folder = ids.indexOf('capture:open_folder')
    expect(folder, 'capture:open_folder is listed').toBeGreaterThanOrEqual(0)
    expect(ids.slice(folder + 1, folder + 9), 'the eight letters follow capture:open_folder').toEqual([
      ...registry.CAPTURE_TOOL_IDS,
    ])
    const letters = ['V', 'A', 'R', 'H', 'T', 'X', 'E', 'C']
    registry.CAPTURE_TOOL_IDS.forEach((id, index) => {
      const entry = commands.find((command) => command.id === id)
      expect(entry, id).toBeDefined()
      expect(entry?.category, id).toBe('capture')
      expect(entry?.page, id).toBe('/capture')
      expect(entry?.stateful, id).toBe(true)
      expect(entry?.palette, id).toBe(false)
      expect(entry?.shortcut, id).toBe(letters[index])
    })
    const allOn = Object.fromEntries(ids.map((id) => [id, true]))
    const listed = shortcuts.paletteCommands(commands, '/capture', allOn).map((command) => command.id)
    for (const id of registry.CAPTURE_TOOL_IDS) {
      expect(listed, `the palette lists no ${id}`).not.toContain(id)
    }
    const bound = shortcuts.BOUND_CONTROLS.map((pair) => `${pair.testid}=${pair.commandId}`)
    const save = bound.indexOf('capture-save=capture:save')
    expect(save, 'capture-save is bound').toBeGreaterThanOrEqual(0)
    expect(bound.slice(save + 1, save + 9)).toEqual([
      'capture-tool-select=capture:tool_select',
      'capture-tool-arrow=capture:tool_arrow',
      'capture-tool-box=capture:tool_box',
      'capture-tool-highlight=capture:tool_highlight',
      'capture-tool-text=capture:tool_text',
      'capture-tool-redact=capture:tool_redact',
      'capture-tool-eraser=capture:tool_eraser',
      'capture-tool-crop=capture:tool_crop',
    ])
    // Sessions 59 and 63: the Annotation tool group, then Lock, Crop, then History.
    const viewport = readFileSync(resolve(UI, 'src/renderer/src/features/capture/CaptureViewport.tsx'), 'utf8')
    const order = Array.from(viewport.matchAll(/\bid="(capture-(?:tool-[a-z]+|undo|redo))"/g), (match) => match[1])
    expect(order).toEqual([
      'capture-tool-select',
      'capture-tool-arrow',
      'capture-tool-box',
      'capture-tool-highlight',
      'capture-tool-text',
      'capture-tool-redact',
      'capture-tool-eraser',
      'capture-tool-lock',
      'capture-tool-crop',
      'capture-undo',
      'capture-redo',
    ])
  })

  it('AC-143.23 drawBounds: a square in each drag direction, cut to the image', () => {
    const square = { square: true, centre: false }
    const cases: Array<[ImagePoint, ImagePoint, [number, number, number, number]]> = [
      [{ x: 10, y: 10 }, { x: 50, y: 30 }, [10, 10, 40, 40]],
      [{ x: 90, y: 70 }, { x: 30, y: 60 }, [30, 10, 60, 60]],
      [{ x: 10, y: 70 }, { x: 50, y: 60 }, [10, 30, 40, 40]],
      [{ x: 90, y: 10 }, { x: 60, y: 20 }, [60, 10, 30, 30]],
      // Leaves the image: 15 across and 60 down from (80, 10); only 19 fits to the right.
      [{ x: 80, y: 10 }, { x: 95, y: 70 }, [80, 10, 19, 19]],
    ]
    for (const [anchor, point, want] of cases) {
      const got = box(mods.drawBounds(anchor, point, square, IMAGE_W, IMAGE_H))
      expect([got.x, got.y, got.width, got.height], `${JSON.stringify(anchor)} to ${JSON.stringify(point)}`).toEqual(want)
    }
    const plain = mods.drawBounds({ x: 10, y: 10 }, { x: 50, y: 30 }, { square: false, centre: false }, IMAGE_W, IMAGE_H)
    expect(plain).toEqual({ start: { x: 10, y: 10 }, end: { x: 50, y: 30 } })
  })

  it('AC-143.24 keepRatioResize: each corner keeps 2:1, the box stops at the image, an edge resizes plainly', () => {
    const cases: Array<[HandleId, ImagePoint, [number, number, number, number]]> = [
      // The width changes by half and the height by a tenth: the width drives.
      ['se', { x: 90, y: 52 }, [30, 30, 60, 30]],
      ['nw', { x: 10, y: 28 }, [10, 20, 60, 30]],
      ['ne', { x: 90, y: 28 }, [30, 20, 60, 30]],
      ['sw', { x: 10, y: 52 }, [10, 30, 60, 30]],
      // The height changes by half and the width by a twentieth: the height drives.
      ['se', { x: 72, y: 60 }, [30, 30, 60, 30]],
      // Past the image edge: 69 px fit to the right of x = 30, so the 2:1 box is 68x34.
      ['se', { x: 99, y: 79 }, [30, 30, 68, 34]],
    ]
    for (const [handle, point, want] of cases) {
      const got = mods.keepRatioResize(BOX_40X20, handle, point, IMAGE_W, IMAGE_H)
      expect(geometry(got), `${handle} to ${JSON.stringify(point)}`).toEqual(want)
      expect(got.type).toBe('rect')
    }
    const edge = mods.keepRatioResize(BOX_40X20, 'e', { x: 80, y: 44 }, IMAGE_W, IMAGE_H)
    expect(geometry(edge), 'the e handle ignores the ratio').toEqual([30, 30, 50, 20])
  })

  it('AC-143.25 snapArrowEnd: the eight directions keep the length; an end outside the image is shortened', () => {
    const fixed = { x: 50, y: 40 }
    const cases: Array<[ImagePoint, ImagePoint]> = [
      [{ x: 70, y: 43 }, { x: 70, y: 40 }],
      [{ x: 65, y: 53 }, { x: 64, y: 54 }],
      [{ x: 52, y: 60 }, { x: 50, y: 60 }],
      [{ x: 36, y: 56 }, { x: 35, y: 55 }],
      [{ x: 30, y: 37 }, { x: 30, y: 40 }],
      [{ x: 37, y: 25 }, { x: 36, y: 26 }],
      [{ x: 47, y: 20 }, { x: 50, y: 20 }],
      [{ x: 64, y: 24 }, { x: 65, y: 25 }],
    ]
    for (const [moving, want] of cases) {
      expect(mods.snapArrowEnd(fixed, moving, IMAGE_W, IMAGE_H), JSON.stringify(moving)).toEqual(want)
    }
    expect(mods.snapArrowEnd({ x: 10, y: 10 }, { x: 50, y: 22 }, IMAGE_W, IMAGE_H)).toEqual({ x: 52, y: 10 })
    expect(mods.snapArrowEnd({ x: 10, y: 10 }, { x: 40, y: 38 }, IMAGE_W, IMAGE_H)).toEqual({ x: 39, y: 39 })
    // 14.87 px at 0 degrees from x = 85 would end at 100; it stops at the last pixel column.
    const out = mods.snapArrowEnd({ x: 85, y: 40 }, { x: 99, y: 45 }, IMAGE_W, IMAGE_H)
    expect(out).toEqual({ x: 99, y: 40 })
    expect(out.x).toBeLessThanOrEqual(IMAGE_W - 1)
  })

  it('AC-143.26 drawBounds with centre: the anchor is the centre and the half-extents stay inside the image', () => {
    const centre = { square: false, centre: true }
    const both = { square: true, centre: true }
    const got = box(mods.drawBounds({ x: 30, y: 30 }, { x: 40, y: 35 }, centre, IMAGE_W, IMAGE_H))
    expect([got.x, got.y, got.width, got.height]).toEqual([20, 25, 20, 10])
    const squared = box(mods.drawBounds({ x: 30, y: 30 }, { x: 40, y: 35 }, both, IMAGE_W, IMAGE_H))
    expect([squared.x, squared.y, squared.width, squared.height]).toEqual([20, 20, 20, 20])
    const cut = box(mods.drawBounds({ x: 5, y: 5 }, { x: 20, y: 10 }, centre, IMAGE_W, IMAGE_H))
    expect([cut.x, cut.y, cut.width, cut.height], 'the centre stays at (5, 5)').toEqual([0, 0, 10, 10])
    const up = box(mods.drawBounds({ x: 50, y: 40 }, { x: 40, y: 30 }, centre, IMAGE_W, IMAGE_H))
    expect([up.x, up.y, up.width, up.height], 'a drag up and left').toEqual([40, 30, 20, 20])
  })
})
