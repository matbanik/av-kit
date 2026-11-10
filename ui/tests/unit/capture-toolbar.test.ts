/** MEU-65 FIC: AC-65.1 and AC-65.7 from the approved Session 29 plan (2026-10-01-capture-viewport-chrome). */
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { Lock } from 'lucide-react'
import { Eraser, Grid3x3 } from 'lucide-react'
import { describe, expect, it } from 'vitest'

import type { Annotation } from '../../src/renderer/src/features/capture/capture-annotate'
import {
  optionGroups,
  TOOL_BUTTON_IDS,
  TOOLBAR_BUTTONS,
  type OptionGroup,
  type ToolbarButtonSpec,
} from '../../src/renderer/src/features/capture/capture-toolbar'
import type { CaptureTool } from '../../src/renderer/src/features/capture/CaptureViewport'

const ui = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const captureDir = resolve(ui, 'src/renderer/src/features/capture')

// TA-2 (Session 39): + pixelate, eraser. MEU-131: + crop.
const TOOLS: CaptureTool[] = ['select', 'arrow', 'box', 'highlight', 'text', 'pixelate', 'eraser', 'crop']

const MARKS: Record<'none' | 'arrow' | 'rect' | 'highlight' | 'text' | 'pixelate' | 'eraser', Annotation | null> = {
  none: null,
  arrow: { type: 'arrow', color: '#FF0000', stroke_width: 3, from: [1, 1], to: [6, 6] },
  rect: { type: 'rect', x: 1, y: 1, width: 4, height: 4, color: '#FF0000', stroke_width: 3 },
  highlight: { type: 'highlight', x: 1, y: 1, width: 4, height: 4, color: '#FFFF00', opacity: 0.4 },
  text: { type: 'text', x: 1, y: 1, text: 'Hi', color: '#FF0000', font_size: 16 },
  pixelate: { type: 'pixelate', x: 1, y: 1, width: 4, height: 4, block_size: 10 },
  eraser: { type: 'eraser', x: 1, y: 1, width: 4, height: 4 },
}

/** OPTIONS_BY_TOOL, restated independently of the implementation (plan §Single-statement contracts). */
function expectedGroups(tool: CaptureTool, selected: Annotation | null): OptionGroup[] {
  // CROP_ENTRY (MEU-131): the crop has no option group, whatever mark is selected.
  if (tool === 'crop') {
    return []
  }
  // OPTIONS_BY_TOOL_V2 (Session 39): the leading region rule.
  if (tool === 'pixelate' || selected?.type === 'pixelate') {
    return ['block']
  }
  if (tool === 'eraser' || selected?.type === 'eraser') {
    return []
  }
  const text = tool === 'text' || selected?.type === 'text'
  const stroke =
    !text &&
    (tool === 'arrow' ||
      tool === 'box' ||
      (tool === 'select' && (selected === null || selected.type === 'arrow' || selected.type === 'rect')))
  return ['color', ...(stroke ? (['stroke'] as const) : []), ...(text ? (['text'] as const) : [])]
}

describe('MEU-65 capture toolbar table and options rule', () => {
  it('AC-65.1 TOOLBAR_BUTTONS names every tool exactly once with unique ids and non-empty names', () => {
    expect(Object.keys(TOOL_BUTTON_IDS).sort()).toEqual([...TOOLS].sort())
    const toolIds = TOOLS.map((tool) => TOOL_BUTTON_IDS[tool])
    expect(new Set(toolIds).size).toBe(TOOLS.length)
    for (const tool of TOOLS) {
      expect(TOOL_BUTTON_IDS[tool]).toBe(`capture-tool-${tool}`)
    }
    const entries = Object.entries(TOOLBAR_BUTTONS)
    const ids = entries.map(([id]) => id)
    expect(new Set(ids).size).toBe(ids.length)
    for (const id of toolIds) {
      expect(ids).toContain(id)
    }
    for (const id of ['capture-undo', 'capture-redo', 'capture-view-original', 'capture-view-annotated']) {
      expect(ids).toContain(id)
    }
    for (const [id, entry] of entries) {
      expect(typeof entry.name, id).toBe('string')
      expect(entry.name.trim().length, id).toBeGreaterThan(0)
      expect(entry.icon, id).toBeTruthy()
    }
    const names = Object.fromEntries(entries.map(([id, entry]) => [id, entry.name]))
    expect(names).toMatchObject({
      'capture-tool-select': 'Select',
      'capture-tool-arrow': 'Arrow',
      'capture-tool-box': 'Box',
      'capture-tool-highlight': 'Highlight',
      'capture-tool-text': 'Text',
      'capture-tool-pixelate': 'Pixelate',
      'capture-tool-eraser': 'Eraser',
      'capture-undo': 'Undo',
      'capture-redo': 'Redo',
      'capture-view-original': 'Original',
      'capture-view-annotated': 'Annotated',
    })
  })

  it('AC-65.1 optionGroups implements OPTIONS_BY_TOOL for every tool and selection', () => {
    expect(typeof optionGroups).toBe('function')
    for (const tool of TOOLS) {
      for (const [kind, mark] of Object.entries(MARKS)) {
        const got = [...optionGroups(tool, mark)].sort()
        expect(got, `${tool} × ${kind}`).toEqual(expectedGroups(tool, mark).sort())
        const regionCase =
          tool === 'pixelate' ||
          mark?.type === 'pixelate' ||
          tool === 'eraser' ||
          mark?.type === 'eraser' ||
          tool === 'crop'
        expect(got.includes('color'), `${tool} × ${kind} color`).toBe(!regionCase)
        expect(got.includes('text') && got.includes('stroke'), `${tool} × ${kind} text+stroke`).toBe(false)
      }
    }
  })

  it('AC-65.1 negative: highlight and text never show stroke; a selected text mark wins over stroke', () => {
    expect(optionGroups('highlight', null)).not.toContain('stroke')
    expect(optionGroups('highlight', null)).not.toContain('text')
    expect(optionGroups('text', null)).not.toContain('stroke')
    expect(optionGroups('text', null)).toContain('text')
    expect(optionGroups('select', MARKS.highlight)).not.toContain('stroke')
    expect(optionGroups('arrow', MARKS.text)).toContain('text')
    expect(optionGroups('arrow', MARKS.text)).not.toContain('stroke')
    expect(optionGroups('select', null)).toContain('stroke')
  })

  it('AC-65.7 MEU-65 test ids are registered after the MEU-51 marker and used by the source', () => {
    const registry = readFileSync(resolve(ui, 'tests/e2e/test-ids.ts'), 'utf8')
    const [prefix, tail] = registry.split('// MEU-51 primitive harness IDs.')
    expect(tail).toBeDefined()
    const block = (tail ?? '').split('// MEU-65 Capture toolbar and Options (additive IDs).')[1] ?? ''
    expect(block.length).toBeGreaterThan(0)
    const viewport = readFileSync(resolve(captureDir, 'CaptureViewport.tsx'), 'utf8')
    const page = readFileSync(resolve(captureDir, 'CapturePage.tsx'), 'utf8')
    const disclosure = readFileSync(resolve(ui, 'src/renderer/src/components/ui/Disclosure.tsx'), 'utf8')
    for (const id of ['capture-chrome-tools', 'capture-chrome-options', 'capture-settings-chevron']) {
      expect(block, id).toContain(`= '${id}'`)
      expect(prefix, id).not.toContain(`'${id}'`)
    }
    expect(viewport).toContain('"capture-chrome-tools"')
    expect(viewport).toContain('"capture-chrome-options"')
    // The chevron wrapper id is `${id}-chevron` on the shared primitive; Capture's id is capture-settings.
    expect(disclosure).toContain('-chevron')
    expect(page).toContain('id="capture-settings"')
  })
})

describe('MEU-87 tool lock entry (TOOL_LOCK)', () => {
  it('AC-87.1 TOOLBAR_BUTTONS has the Lock entry, which is not a tool', () => {
    const lock = (TOOLBAR_BUTTONS as Record<string, ToolbarButtonSpec | undefined>)['capture-tool-lock']
    expect(lock?.name).toBe('Keep tool after drawing')
    expect(lock?.icon).toBe(Lock)
    expect(Object.values(TOOL_BUTTON_IDS)).not.toContain('capture-tool-lock')
  })

  it('AC-87.1 negative: TOOL_BUTTON_IDS still lists exactly the eight tools (AC-65.1 holds)', () => {
    expect(Object.keys(TOOL_BUTTON_IDS).sort()).toEqual([
      'arrow',
      'box',
      'crop',
      'eraser',
      'highlight',
      'pixelate',
      'select',
      'text',
    ])
  })
})

describe('MEU-90 pixelate tool', () => {
  it('AC-90.9 the Pixelate tool has its id, the Grid3x3 icon and the name; optionGroups gives block for it and a selected pixelate', () => {
    expect(TOOL_BUTTON_IDS.pixelate).toBe('capture-tool-pixelate')
    const entry = TOOLBAR_BUTTONS['capture-tool-pixelate']
    expect(entry?.name).toBe('Pixelate')
    expect(entry?.icon).toBe(Grid3x3)
    expect(optionGroups('pixelate', null)).toEqual(['block'])
    // Negative: not the Session 34 fallthrough for an unknown tool.
    expect(optionGroups('pixelate', null)).not.toEqual(['color', 'stroke'])
    // CROP_ENTRY (MEU-131): the crop's leading rule wins over a selected pixelate.
    for (const tool of TOOLS.filter((t) => t !== 'crop')) {
      expect(optionGroups(tool, MARKS.pixelate), `${tool} × selected pixelate`).toEqual(['block'])
    }
    expect(optionGroups('crop', MARKS.pixelate)).toEqual([])
    for (const kind of ['arrow', 'rect', 'highlight', 'text'] as const) {
      expect(optionGroups('pixelate', MARKS[kind]), `pixelate × ${kind}`).toEqual(['block'])
    }
  })
})

describe('MEU-91 eraser tool', () => {
  it('AC-91.8 the Eraser tool has its id, the Eraser icon and the name; optionGroups gives no group for it and a selected eraser', () => {
    expect(TOOL_BUTTON_IDS.eraser).toBe('capture-tool-eraser')
    const entry = TOOLBAR_BUTTONS['capture-tool-eraser']
    expect(entry?.name).toBe('Eraser')
    expect(entry?.icon).toBe(Eraser)
    expect(optionGroups('eraser', null)).toEqual([])
    // Negative: not the fallthrough color group.
    expect(optionGroups('eraser', null)).not.toEqual(['color'])
    for (const tool of TOOLS.filter((item) => item !== 'pixelate')) {
      expect(optionGroups(tool, MARKS.eraser), `${tool} × selected eraser`).toEqual([])
    }
    // OPTIONS_BY_TOOL_V2 order: the pixelate rule is first, so the Pixelate tool keeps Block size.
    expect(optionGroups('pixelate', MARKS.eraser)).toEqual(['block'])
    for (const kind of ['arrow', 'rect', 'highlight', 'text'] as const) {
      expect(optionGroups('eraser', MARKS[kind]), `eraser × ${kind}`).toEqual([])
    }
  })
})
