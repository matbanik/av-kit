/** @vitest-environment jsdom */

/**
 * MEU-47 — `SELECTION_MODEL` (AC-47.1).
 *
 * The selection is the one piece of queue state the client owns outright: the
 * backend knows nothing about which rows a user has ticked. That makes two
 * failure modes cheap to write and expensive to ship — acting on an id the
 * server has already dropped, and selecting rows the user cannot see because a
 * filter hides them. Both get their own assertion here.
 *
 * The hook is loaded with a dynamic `import()` so a missing module fails this
 * one AC rather than collapsing collection (RED_ORACLE requires one failed
 * title per AC id).
 */

import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { act, render, screen } from '@testing-library/react'
import { createElement, type ReactElement } from 'react'
import { afterEach, describe, expect, it } from 'vitest'

import type * as SelectionModule from '../../src/renderer/src/lib/queue/use-queue-selection'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')
const planDir = resolve(repoRoot, 'docs/execution/plans/2026-09-02-p10-queue-card-migration')

type NamedSets = { SELECTION_MODEL: { value: string } }
const SETS = JSON.parse(
  readFileSync(resolve(planDir, 'named-sets.json'), 'utf-8'),
) as NamedSets

/*
  The specifier is held in a variable so Vite's import-analysis cannot resolve
  it at transform time: a literal one makes a MISSING module a whole-file
  collection error, which reports no test titles at all and breaks the
  RED_ORACLE mapping of one failing title per AC.
*/
const SELECTION_MODULE = '../../src/renderer/src/lib/queue/use-queue-selection'

function loadSelection(): Promise<typeof SelectionModule> {
  return import(/* @vite-ignore */ SELECTION_MODULE) as Promise<typeof SelectionModule>
}

/**
 * `useQueueSelection` is headless, so this file is the registered mount-only
 * case: it drives the hook's API directly and never simulates a user gesture.
 * The harness still renders a marker element, which is what `screen` reads to
 * prove the hook actually mounted rather than failing silently.
 */
const HARNESS_TESTID = 'queue-selection-harness'

let rerenderTree: ((element: ReactElement) => void) | null = null
let unmountTree: (() => void) | null = null

function unmount(): void {
  unmountTree?.()
  unmountTree = null
  rerenderTree = null
}

afterEach(() => {
  unmount()
})

type Item = { id: string }

/**
 * Mount the hook and hand the live API back through a mutable box.
 *
 * `rerender` is what proves the pruning clause: the same mounted hook is given
 * a shorter list, exactly as a refetch would.
 */
async function mountSelection(initial: readonly Item[]): Promise<{
  api: () => SelectionModule.QueueSelection
  rerender: (items: readonly Item[]) => void
}> {
  const { useQueueSelection } = await loadSelection()
  const box: { current: SelectionModule.QueueSelection | null } = { current: null }

  function Harness({ items }: { items: readonly Item[] }): ReactElement {
    box.current = useQueueSelection(items)
    return createElement('div', { 'data-testid': HARNESS_TESTID })
  }

  let current: readonly Item[] = initial
  const view = render(createElement(Harness, { items: current }))
  rerenderTree = view.rerender
  unmountTree = view.unmount
  expect(screen.getByTestId(HARNESS_TESTID), 'the hook harness mounted').not.toBeNull()

  return {
    api: () => {
      if (box.current === null) {
        throw new Error('useQueueSelection did not return a selection API')
      }
      return box.current
    },
    rerender: (items) => {
      current = items
      act(() => {
        rerenderTree?.(createElement(Harness, { items: current }))
      })
    },
  }
}

const FIVE: Item[] = [{ id: 'a' }, { id: 'b' }, { id: 'c' }, { id: 'd' }, { id: 'e' }]

describe('MEU-47 useQueueSelection', () => {
  it('AC-47.1 SELECTION_MODEL toggles, shift-ranges from the anchor and clears', async () => {
    // The clause list is read, never restated — if the plan's model changes,
    // this test must be revisited rather than silently drifting.
    expect(SETS.SELECTION_MODEL.value).toContain('Shift+click')

    const { api } = await mountSelection(FIVE)

    expect(api().selectedIds).toEqual([])
    expect(api().count).toBe(0)
    expect(api().allSelected).toBe(false)
    expect(api().someSelected).toBe(false)

    // Plain click toggles exactly one.
    act(() => {
      api().toggle('b', true)
    })
    expect(api().selectedIds).toEqual(['b'])
    expect(api().isSelected('b')).toBe(true)
    expect(api().someSelected).toBe(true)
    expect(api().allSelected).toBe(false)

    act(() => {
      api().toggle('b', false)
    })
    expect(api().selectedIds).toEqual([])

    // Shift+click selects the INCLUSIVE range from the last anchor, in render
    // order — not in click order, and not just the two endpoints.
    act(() => {
      api().toggle('b', true)
    })
    act(() => {
      api().toggle('d', true, { shiftKey: true })
    })
    expect(api().selectedIds).toEqual(['b', 'c', 'd'])

    // A backwards range is the same range.
    act(() => {
      api().clear()
    })
    act(() => {
      api().toggle('d', true)
    })
    act(() => {
      api().toggle('b', true, { shiftKey: true })
    })
    expect(api().selectedIds).toEqual(['b', 'c', 'd'])

    act(() => {
      api().clear()
    })
    expect(api().selectedIds).toEqual([])
    expect(api().count).toBe(0)
  })

  it('AC-47.1 Shift+click with no anchor selects only the clicked row', async () => {
    const { api } = await mountSelection(FIVE)

    act(() => {
      api().toggle('c', true, { shiftKey: true })
    })
    expect(api().selectedIds).toEqual(['c'])
  })

  it('AC-47.1 select-all covers the FILTERED list and Ctrl/Cmd+A is its shortcut', async () => {
    const { isSelectAllShortcut } = await loadSelection()

    // The shortcut predicate is pure, so both platform chords are provable
    // without simulating a browser on each OS.
    expect(isSelectAllShortcut({ key: 'a', ctrlKey: true, metaKey: false })).toBe(true)
    expect(isSelectAllShortcut({ key: 'A', ctrlKey: false, metaKey: true })).toBe(true)
    expect(isSelectAllShortcut({ key: 'a', ctrlKey: false, metaKey: false })).toBe(false)
    expect(isSelectAllShortcut({ key: 'b', ctrlKey: true, metaKey: false })).toBe(false)

    // A filtered list is simply a shorter `items` — select-all must never reach
    // past what the user can see.
    const filtered: Item[] = [{ id: 'b' }, { id: 'd' }]
    const { api } = await mountSelection(filtered)

    act(() => {
      api().selectAll(true)
    })
    expect(api().selectedIds).toEqual(['b', 'd'])
    expect(api().allSelected).toBe(true)
    expect(api().someSelected).toBe(false)

    act(() => {
      api().selectAll(false)
    })
    expect(api().selectedIds).toEqual([])
    expect(api().allSelected).toBe(false)
  })

  it('AC-47.1 ids that vanish from the envelope are pruned, never acted on', async () => {
    const { api, rerender } = await mountSelection(FIVE)

    act(() => {
      api().selectAll(true)
    })
    expect(api().selectedIds).toEqual(['a', 'b', 'c', 'd', 'e'])

    // The next refetch no longer carries c or e — another client removed them.
    rerender([{ id: 'a' }, { id: 'b' }, { id: 'd' }])
    expect(api().selectedIds).toEqual(['a', 'b', 'd'])
    expect(api().isSelected('c')).toBe(false)
    expect(api().count).toBe(3)
    expect(api().allSelected).toBe(true)
  })

  it('AC-47.1 selectedIds is always in render order regardless of click order', async () => {
    const { api, rerender } = await mountSelection(FIVE)

    act(() => {
      api().toggle('e', true)
    })
    act(() => {
      api().toggle('a', true)
    })
    act(() => {
      api().toggle('c', true)
    })
    expect(api().selectedIds).toEqual(['a', 'c', 'e'])

    // Reordering the queue reorders the selection with it: a bulk move folds in
    // render order, so a stale sequence here would move rows to the wrong place.
    rerender([{ id: 'e' }, { id: 'd' }, { id: 'c' }, { id: 'b' }, { id: 'a' }])
    expect(api().selectedIds).toEqual(['e', 'c', 'a'])
  })
  it('AC-47.1 R1-F1 an id that leaves and returns comes back UNSELECTED', async () => {
    /*
      Exec-review round 1, Finding 1. Pruning only the derived projection left
      the vanished id sitting in the backing set, so a row that came back on a
      later refetch — a retried job, a filter the user widened again — returned
      already ticked and the next bulk action acted on a row nobody selected.
    */
    const { api, rerender } = await mountSelection(FIVE)

    act(() => {
      api().selectAll(true)
    })
    expect(api().selectedIds).toEqual(['a', 'b', 'c', 'd', 'e'])

    rerender([{ id: 'a' }, { id: 'b' }, { id: 'd' }])
    expect(api().selectedIds).toEqual(['a', 'b', 'd'])

    // c and e are back. They must return unticked: the user's selection of them
    // was consumed by their disappearance.
    rerender(FIVE)
    expect(api().selectedIds).toEqual(['a', 'b', 'd'])
    expect(api().isSelected('c')).toBe(false)
    expect(api().isSelected('e')).toBe(false)
    expect(api().allSelected).toBe(false)
    expect(api().someSelected).toBe(true)
  })

  it('AC-47.1 R1-F1 an anchor that vanishes is released, so Shift+click still ranges', async () => {
    /*
      Same finding, quieter half: a Shift+click deliberately does NOT move the
      anchor, so a stale anchor is never replaced and every later Shift+click
      degrades to a plain toggle until a plain click happens to reset it.
    */
    const { api, rerender } = await mountSelection(FIVE)

    act(() => {
      api().toggle('b', true)
    })

    // b is gone; the anchor must go with it.
    rerender([{ id: 'a' }, { id: 'c' }, { id: 'd' }, { id: 'e' }])
    expect(api().selectedIds).toEqual([])

    // With the anchor released, this click becomes the new anchor...
    act(() => {
      api().toggle('c', true, { shiftKey: true })
    })
    expect(api().selectedIds).toEqual(['c'])

    // ...and the next Shift+click ranges from it rather than toggling alone.
    act(() => {
      api().toggle('e', true, { shiftKey: true })
    })
    expect(api().selectedIds).toEqual(['c', 'd', 'e'])
  })

  it('AC-47.1 R1-F1 a pure REORDER preserves both the selection and the anchor', async () => {
    // The pruning above keys on MEMBERSHIP, not order — rearranging the queue
    // must cost the user neither their ticks nor their range anchor.
    const { api, rerender } = await mountSelection(FIVE)

    act(() => {
      api().toggle('b', true)
    })
    rerender([{ id: 'e' }, { id: 'd' }, { id: 'c' }, { id: 'b' }, { id: 'a' }])
    expect(api().selectedIds).toEqual(['b'])

    // The anchor survived the reorder: this ranges b..a in the NEW render order.
    act(() => {
      api().toggle('a', true, { shiftKey: true })
    })
    expect(api().selectedIds).toEqual(['b', 'a'])
  })
})
