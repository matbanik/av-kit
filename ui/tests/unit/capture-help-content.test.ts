/** @vitest-environment node */

import { describe, expect, it } from 'vitest'

import { CAPTURE_HELP_SECTIONS } from '../../src/renderer/src/features/capture/capture-help-content'

const HELP_PIXEL_SENTENCE = 'Marks use original image pixels and survive Save then reload.'
const HELP_EDIT_SENTENCE =
  'Select a mark to move it or drag an arrow end until Save. Arrow keys nudge the selected mark, or the arrow end you grabbed or tabbed to; Apply commits color.'
const HISTORY_HELP_SENTENCE =
  'Ctrl+Z undoes and Ctrl+Y or Ctrl+Shift+Z redoes while the image has focus; a text field keeps its own undo.'
// Session 68 REDACT_HELP (D-686, DEP-3): the resize sentence names the redact mark.
const RESIZE_HELP_SENTENCE = 'Drag a square handle on a selected box, highlight, redact, pixelate or eraser mark to resize it.'
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
  'Apply to image bakes the saved marks into the original file after copying it to the backup folder (Settings → Capture); a JPEG or WebP shot gets a new PNG copy instead, and the original stays unchanged. Revert restores the newest backup. Save overlay can write PNG, JPEG or WebP (Settings → Capture).'

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
  'Drag the Stroke or Size label, or use the mouse wheel or Up/Down over its field, to change the size; each gesture is one undo step.'

describe('MEU-85 help', () => {
  it('AC-85.11 HelpCard four-tools body includes the scrub sentence and keeps the zoom sentence', () => {
    const four = CAPTURE_HELP_SECTIONS.find((section) => section.id === 'four-tools')
    expect(four?.body).toContain(SCRUB_HELP_SENTENCE)
    expect(four?.body).toContain(ZOOM_HELP_SENTENCE)
  })
})

const LOCK_HELP_SENTENCE = 'The lock button keeps the current tool after each mark.'

describe('MEU-87 help', () => {
  it('AC-87.7 HelpCard four-tools body includes the lock sentence and keeps the scrub sentence', () => {
    const four = CAPTURE_HELP_SECTIONS.find((section) => section.id === 'four-tools')
    expect(four?.body).toContain(LOCK_HELP_SENTENCE)
    expect(four?.body).toContain(SCRUB_HELP_SENTENCE)
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
    expect(four?.body).toContain(`${HELP_EDIT_SENTENCE} ${HISTORY_HELP_SENTENCE}`)
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
