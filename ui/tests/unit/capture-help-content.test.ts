/** @vitest-environment node */

import { describe, expect, it } from 'vitest'

import { CAPTURE_HELP_SECTIONS } from '../../src/renderer/src/features/capture/capture-help-content'

const HELP_PIXEL_SENTENCE = 'Marks use original image pixels and survive Save then reload.'
const HELP_EDIT_SENTENCE =
  'Select a mark to move it or drag an arrow end until Save. Arrow keys nudge the selected mark (Shift+arrow by 10 px), or the arrow end you grabbed or tabbed to.'
const HISTORY_HELP_SENTENCE =
  'Ctrl+Z undoes and Ctrl+Y or Ctrl+Shift+Z redoes while the image has focus; a text field keeps its own undo.'
// Session 68 REDACT_HELP (D-686, DEP-3): the resize sentence names the redact mark.
// Session 72 SHAPES_HELP: and the ellipse.
const RESIZE_HELP_SENTENCE =
  'Drag a square handle on a selected box, ellipse, highlight, redact, pixelate or eraser mark to resize it.'
// Session 72 SHAPES_HELP: the Ctrl+D sentence follows the nudge sentence (AC-99.6's pin moves).
const DUPLICATE_HELP_SENTENCE = 'Ctrl+D duplicates the selected mark 10 px down and right and selects the copy.'
const TEXT_EDIT_HELP_SENTENCE =
  'Double-click a text mark, or press Enter with it selected, to edit its text; drag a corner of its plate to scale it.'

describe('MEU-59 help', () => {
  it('AC-59.20 HelpCard four-tools body includes the pixel/reload sentence', () => {
    const four = CAPTURE_HELP_SECTIONS.find((section) => section.id === 'four-tools')
    expect(four?.body).toContain(HELP_PIXEL_SENTENCE)
  })
})

describe('MEU-60 help', () => {
  it('AC-60.15 HelpCard four-tools body includes the Select/nudge sentence [TA-16]', () => {
    const four = CAPTURE_HELP_SECTIONS.find((section) => section.id === 'four-tools')
    expect(four?.body).toContain(HELP_EDIT_SENTENCE)
  })
})

const ZOOM_HELP_SENTENCE =
  'Zoom with the mouse wheel, the + / − / Fit buttons or Ctrl+= / Ctrl+- / Ctrl+0; hold Space or the middle button and drag to pan. Zoom never changes saved marks.'

describe('MEU-66 help', () => {
  it('AC-66.16 HelpCard four-tools body includes the zoom sentence and keeps the earlier sentences [TA-16]', () => {
    const four = CAPTURE_HELP_SECTIONS.find((section) => section.id === 'four-tools')
    expect(four?.body).toContain(ZOOM_HELP_SENTENCE)
    expect(four?.body).toContain(HELP_PIXEL_SENTENCE)
    expect(four?.body).toContain(HELP_EDIT_SENTENCE)
  })
})

const ORIGINAL_ANNOTATED_SENTENCE =
  'The filmstrip lists originals. Sidecar .annotated.png files are baked copies and are skipped by the inbox watcher.'
const FLATTEN_HELP_SENTENCE =
  'Flatten into image bakes the saved marks into the original file after copying it to the backup folder (Settings → Capture); a JPEG or WebP shot gets a new PNG copy instead, and the original stays unchanged. Restore backup restores the newest backup. Save annotations can write PNG, JPEG or WebP (Settings → Capture).'

describe('MEU-67 help', () => {
  it('AC-67.25 original-annotated body appends FLATTEN_HELP_SENTENCE and keeps the old sentence verbatim', () => {
    const section = CAPTURE_HELP_SECTIONS.find((item) => item.id === 'original-annotated')
    expect(section?.body.startsWith(ORIGINAL_ANNOTATED_SENTENCE)).toBe(true)
    expect(section?.body).toContain(FLATTEN_HELP_SENTENCE)
    expect(section?.body.endsWith(FLATTEN_HELP_SENTENCE)).toBe(true)
  })
})

const RANGE_HELP_SENTENCE =
  'Right-click a thumbnail (or press Shift+F10) to copy its path or image, or delete it; Shift-click selects a range to delete together.'

describe('MEU-89 help', () => {
  it('AC-89.8 HelpCard four-tools body ends with the thumbnail menu and range sentence and keeps the earlier sentences', () => {
    const four = CAPTURE_HELP_SECTIONS.find((section) => section.id === 'four-tools')
    expect(four?.body.endsWith(RANGE_HELP_SENTENCE)).toBe(true)
    expect(four?.body).toContain(HELP_PIXEL_SENTENCE)
    expect(four?.body).toContain(HELP_EDIT_SENTENCE)
    expect(four?.body).toContain(ZOOM_HELP_SENTENCE)
  })

  it('AC-89.8 original-annotated still ends with the flatten sentence and does not carry the range sentence', () => {
    const section = CAPTURE_HELP_SECTIONS.find((item) => item.id === 'original-annotated')
    expect(section?.body.endsWith(FLATTEN_HELP_SENTENCE)).toBe(true)
    expect(section?.body).not.toContain(RANGE_HELP_SENTENCE)
  })
})

const SCRUB_HELP_SENTENCE =
  'Drag the Stroke, Size or Block size label, or use the mouse wheel or Up/Down over its field, to change the size; each gesture is one undo step.'

describe('MEU-85 help', () => {
  it('AC-85.11 HelpCard four-tools body includes the scrub sentence and keeps the zoom sentence', () => {
    const four = CAPTURE_HELP_SECTIONS.find((section) => section.id === 'four-tools')
    expect(four?.body).toContain(SCRUB_HELP_SENTENCE)
    expect(four?.body).toContain(ZOOM_HELP_SENTENCE)
  })
})

// MEU-143 LOCK_HELP (D-744): the lock sentence is LOCK_HELP's first; the old sentence is gone.
const OLD_LOCK_SENTENCE = 'The lock button keeps the current tool after each mark.'
const LOCK_HELP_SENTENCE =
  'The lock is on by default: the tool stays armed after each mark and the new mark stays selected, so a style change restyles it and a press on it moves or resizes it; pick the tool again to set its own style.'

describe('MEU-87 help', () => {
  it('AC-87.7 HelpCard four-tools body includes the lock sentence and keeps the scrub sentence', () => {
    const four = CAPTURE_HELP_SECTIONS.find((section) => section.id === 'four-tools')
    expect(four?.body).toContain(LOCK_HELP_SENTENCE)
    expect(four?.body).toContain(SCRUB_HELP_SENTENCE)
    expect(four?.body).not.toContain(OLD_LOCK_SENTENCE)
  })
})

const LOCK_HELP_TEXT =
  "The lock is on by default: the tool stays armed after each mark and the new mark stays selected, so a style change restyles it and a press on it moves or resizes it; pick the tool again to set its own style. Turn the lock off to return to Select after each mark; Capture remembers the choice. Press V, A, R, H, T, X, E or C for Select, Arrow, Box, Highlight, Text, Redact, Smart eraser or Crop; letters type normally in a text field. Hold Shift to draw a square, keep a box's shape from a corner or snap an arrow to 45 degrees; hold Alt to draw a box from its centre."

describe('MEU-143 help', () => {
  it('AC-143.31 the Annotation tools body holds LOCK_HELP and the Shift nudge, not the old lock sentence', () => {
    const four = CAPTURE_HELP_SECTIONS.find((section) => section.id === 'four-tools')
    expect(four?.body).toContain(LOCK_HELP_TEXT)
    expect(four?.body).toContain('Arrow keys nudge the selected mark (Shift+arrow by 10 px), or the arrow end')
    expect(four?.body).not.toContain(OLD_LOCK_SENTENCE)
  })
})

describe('MEU-91 help', () => {
  it('AC-91.11 the four-tools section is titled Annotation tools and names all six tools', () => {
    const section = CAPTURE_HELP_SECTIONS.find((item) => item.id === 'four-tools')
    expect(section).toBeDefined()
    expect(section?.title).toBe('Annotation tools')
    // Negative: the old title is gone.
    expect(section?.title).not.toBe('four tools')
    // Session 68 REDACT_HELP (D-686): Redact with its Pixelate mode, and the Smart eraser.
    for (const tool of ['Arrow', 'Box', 'Highlight', 'Text', 'Redact', 'Pixelate', 'Smart eraser']) {
      expect(section?.body, tool).toContain(tool)
    }
  })
})

describe('MEU-99 help', () => {
  it('AC-99.6 HelpCard four-tools body follows the edit sentence with the history chord sentence and still ends with the range sentence', () => {
    const four = CAPTURE_HELP_SECTIONS.find((section) => section.id === 'four-tools')
    // Session 72 departure: SHAPES_HELP puts the Ctrl+D sentence between the two.
    expect(four?.body).toContain(`${HELP_EDIT_SENTENCE} ${DUPLICATE_HELP_SENTENCE} ${HISTORY_HELP_SENTENCE}`)
    expect(four?.body.endsWith(RANGE_HELP_SENTENCE)).toBe(true)
  })
})

describe('MEU-100 help', () => {
  it('AC-100.10 HelpCard four-tools body follows the history chord sentence with the resize sentence and still ends with the range sentence', () => {
    const four = CAPTURE_HELP_SECTIONS.find((section) => section.id === 'four-tools')
    expect(four?.body).toContain(`${HISTORY_HELP_SENTENCE} ${RESIZE_HELP_SENTENCE}`)
    expect(four?.body.endsWith(RANGE_HELP_SENTENCE)).toBe(true)
  })
})

describe('MEU-101 help', () => {
  it('AC-101.5 HelpCard four-tools body follows the resize sentence with the text edit sentence and still ends with the range sentence', () => {
    const four = CAPTURE_HELP_SECTIONS.find((section) => section.id === 'four-tools')
    expect(four?.body).toContain(`${RESIZE_HELP_SENTENCE} ${TEXT_EDIT_HELP_SENTENCE}`)
    expect(four?.body.endsWith(RANGE_HELP_SENTENCE)).toBe(true)
  })
})

// Session 72 SHAPES_HELP (MEU-106, MEU-107).
const SEVEN_TOOLS_START = 'Seven annotation tools: Arrow, Box, Highlight, Text and Step draw on the selected shot;'
const REDACT_MODE_SENTENCE =
  'Redact covers its box in Solid black by default; its Pixelate mode turns the box into blocks instead, and picking the other mode with a redaction selected swaps it.'
const SHAPE_CONTROLS_SENTENCE =
  'The Head control turns an arrow into a line or gives it a head at both ends, and the Shape control turns a box into an ellipse; with a mark selected, either one changes that mark.'
const STEP_HELP_SENTENCE = 'Step places the next number at each click.'
const ELLIPSE_MODIFIER_SENTENCE = 'Shift and Alt work the same on an ellipse, and Shift snaps a line to 45 degrees.'

describe('MEU-106 help', () => {
  it('AC-106.27 the Annotation tools body names seven tools and holds each SHAPES_HELP sentence in place', () => {
    const body = CAPTURE_HELP_SECTIONS.find((section) => section.id === 'four-tools')?.body ?? ''
    expect(body.startsWith(SEVEN_TOOLS_START)).toBe(true)
    expect(body).not.toContain('Six annotation tools')
    expect(body).toContain(`${REDACT_MODE_SENTENCE} ${SHAPE_CONTROLS_SENTENCE} ${STEP_HELP_SENTENCE}`)
    expect(body).toContain(`${HELP_EDIT_SENTENCE} ${DUPLICATE_HELP_SENTENCE}`)
    expect(body).toContain(`${HISTORY_HELP_SENTENCE} ${RESIZE_HELP_SENTENCE}`)
    expect(body).not.toContain('selected box, highlight, redact')
    expect(body).toContain(`${LOCK_HELP_TEXT} ${ELLIPSE_MODIFIER_SENTENCE}`)
    // Every MEU-143 sentence stays, and the body still ends with the range sentence.
    expect(body).toContain('Arrow keys nudge the selected mark (Shift+arrow by 10 px), or the arrow end')
    expect(body.endsWith(RANGE_HELP_SENTENCE)).toBe(true)
  })
})

describe('MEU-107 help', () => {
  it('AC-107.25 the Annotation tools body holds the step sentence', () => {
    const body = CAPTURE_HELP_SECTIONS.find((section) => section.id === 'four-tools')?.body ?? ''
    expect(body).toContain(STEP_HELP_SENTENCE)
  })
})
