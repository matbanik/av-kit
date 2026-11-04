/**
 * MEU-49 — `DND_ANNOUNCEMENT_CONTRACT`.
 *
 * The spec's deliverable for a drag is not the movement; it is that a screen
 * reader user can perform and confirm the movement. dnd-kit's default
 * announcements are index-based ("was moved over droppable area 5"), which
 * reads one off every position a sighted user sees. These strings are exported
 * as pure functions precisely so they can be asserted without a completed drag,
 * which jsdom cannot produce (`JSDOM_RECT_RULE`).
 */

import { describe, expect, it } from 'vitest'

import {
  createQueueAnnouncements,
  queueScreenReaderInstructions,
} from '../../src/renderer/src/components/queue/queue-dnd'

/** Seven rows, so "of 7" is unambiguous and 1-indexing is visible. */
const ITEMS = [
  { id: 'a', title: 'Alpha' },
  { id: 'b', title: 'Bravo' },
  { id: 'c', title: 'Charlie' },
  { id: 'd', title: 'Delta' },
  { id: 'e', title: 'Echo' },
  { id: 'f', title: 'Foxtrot' },
  { id: 'g', title: 'Golf' },
]

describe('MEU-49 DND_ANNOUNCEMENT_CONTRACT', () => {
  it('AC-49.16 the announcements object defines all four handlers', () => {
    const announcements = createQueueAnnouncements(ITEMS)

    expect(typeof announcements.onDragStart).toBe('function')
    expect(typeof announcements.onDragOver).toBe('function')
    expect(typeof announcements.onDragEnd).toBe('function')
    // The one dnd-kit does not require and the one a keyboard user needs most:
    // without it, Escape silently undoes the drag and says nothing.
    expect(typeof announcements.onDragCancel).toBe('function')
  })

  it('AC-49.16 screenReaderInstructions is non-empty and describes the keyboard drag', () => {
    expect(queueScreenReaderInstructions.draggable.trim().length).toBeGreaterThan(0)
    expect(queueScreenReaderInstructions.draggable).toContain('space')
    expect(queueScreenReaderInstructions.draggable).toContain('arrow')
    expect(queueScreenReaderInstructions.draggable).toContain('escape')
  })

  it('AC-49.17 every announcement is position-based, 1-indexed and names the job title', () => {
    const announcements = createQueueAnnouncements(ITEMS)

    // Charlie is items[2] — the THIRD row — and is dragged over Foxtrot,
    // items[5], the SIXTH. Every string below says 3 and 6, never 2 and 5.
    expect(announcements.onDragStart({ active: { id: 'c' } })).toBe(
      'Picked up "Charlie". It is in position 3 of 7.',
    )
    expect(announcements.onDragOver({ active: { id: 'c' }, over: { id: 'f' } })).toBe(
      '"Charlie" was moved to position 6 of 7.',
    )
    expect(announcements.onDragEnd({ active: { id: 'c' }, over: { id: 'f' } })).toBe(
      '"Charlie" was dropped at position 6 of 7.',
    )
  })

  it('AC-49.17 onDragCancel states the item returned to its starting position', () => {
    const announcements = createQueueAnnouncements(ITEMS)

    expect(announcements.onDragCancel({ active: { id: 'c' } })).toBe(
      'Dragging "Charlie" was cancelled. It returned to position 3 of 7.',
    )
  })

  it('AC-49.17 no announcement contains a 0-based position or a bare droppable index', () => {
    const announcements = createQueueAnnouncements(ITEMS)
    const strings = [
      announcements.onDragStart({ active: { id: 'a' } }),
      announcements.onDragOver({ active: { id: 'a' }, over: { id: 'b' } }),
      announcements.onDragEnd({ active: { id: 'a' }, over: { id: 'b' } }),
      announcements.onDragCancel({ active: { id: 'a' } }),
    ]

    for (const line of strings) {
      // Alpha is the first row: 1-indexed that is "position 1", and the
      // 0-based leak this guards against is "position 0".
      expect(line).toBeTypeOf('string')
      expect(line).not.toMatch(/position 0\b/)
      // dnd-kit's own default wording, which this factory replaces.
      expect(line).not.toContain('droppable area')
      expect(line).toContain('of 7')
    }
    expect(strings[0]).toContain('position 1 of 7')
    expect(strings[1]).toContain('position 2 of 7')
  })

  it('AC-49.17 a drag with no droppable under it announces nothing rather than a wrong position', () => {
    const announcements = createQueueAnnouncements(ITEMS)

    // `over` is null whenever the pointer leaves the sortable area. Reporting a
    // position here would name one the row is not going to occupy.
    expect(announcements.onDragOver({ active: { id: 'c' }, over: null })).toBeUndefined()
    expect(announcements.onDragEnd({ active: { id: 'c' }, over: null })).toBe(
      'Dragging "Charlie" was cancelled. It returned to position 3 of 7.',
    )
  })
})
