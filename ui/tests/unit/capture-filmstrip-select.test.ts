/** @vitest-environment node */

import { describe, expect, it } from 'vitest'

import { rangeBetween, toggleSelection } from '../../src/renderer/src/features/capture/capture-filmstrip-select'

// Session 38 (MEU-89): rangeBetween is the inclusive slice behind Shift-click range selection;
// toggleSelection (D-25) is what a filmstrip checkbox does to the selection set.

const ORDER = ['a', 'b', 'c', 'd', 'e']

describe('MEU-89 rangeBetween', () => {
  it('AC-89.1 returns the inclusive slice in filmstrip order when the target is after the anchor', () => {
    expect(rangeBetween(ORDER, 'b', 'd')).toEqual(['b', 'c', 'd'])
    expect(rangeBetween(ORDER, 'a', 'e')).toEqual(['a', 'b', 'c', 'd', 'e'])
  })

  it('AC-89.1 returns the same order when the target is before the anchor', () => {
    expect(rangeBetween(ORDER, 'd', 'b')).toEqual(['b', 'c', 'd'])
    expect(rangeBetween(ORDER, 'e', 'a')).toEqual(['a', 'b', 'c', 'd', 'e'])
  })

  it('AC-89.1 the anchor itself gives a range of one', () => {
    expect(rangeBetween(ORDER, 'c', 'c')).toEqual(['c'])
  })

  it('AC-89.1 an unknown target gives [] and an unknown anchor gives [target]', () => {
    expect(rangeBetween(ORDER, 'b', 'zz')).toEqual([])
    expect(rangeBetween(ORDER, 'zz', 'c')).toEqual(['c'])
    expect(rangeBetween([], 'a', 'b')).toEqual([])
  })
})

describe('MEU-89 toggleSelection', () => {
  it('AC-89.10 adds an absent id and removes a present one', () => {
    expect(toggleSelection(ORDER, [], 'd')).toEqual(['d'])
    expect(toggleSelection(ORDER, ['d'], 'b')).toEqual(['b', 'd'])
    expect(toggleSelection(ORDER, ['b', 'd'], 'b')).toEqual(['d'])
    expect(toggleSelection(ORDER, ['b', 'c', 'd'], 'c')).toEqual(['b', 'd'])
    expect(toggleSelection(ORDER, ['c'], 'c')).toEqual([])
  })

  it('AC-89.10 returns orderedIds order whatever order the ids were ticked in', () => {
    expect(toggleSelection(ORDER, ['e', 'a'], 'c')).toEqual(['a', 'c', 'e'])
    expect(toggleSelection(ORDER, ['d', 'b', 'a'], 'b')).toEqual(['a', 'd'])
  })

  it('AC-89.10 an id not in orderedIds leaves the selection unchanged', () => {
    expect(toggleSelection(ORDER, ['b', 'd'], 'zz')).toEqual(['b', 'd'])
    expect(toggleSelection(ORDER, [], 'zz')).toEqual([])
  })
})
