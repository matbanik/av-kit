/**
 * MEU-47 — `BULK_REORDER_ALGORITHM` (AC-47.7a).
 *
 * The reorder endpoint takes an ABSOLUTE permutation (`REORDER_WIRE_CONTRACT`),
 * not a relative `{id, direction}` nudge. Under `BULK_ENDPOINT_POLICY` a bulk
 * move is therefore N sequential PUTs, and the only correct way to build request
 * k is to fold from the order the server accepted at k-1. Folding from the stale
 * initial order would make each step silently undo the previous one — the exact
 * bug this file exists to prevent, so the failure path (step 2 rejects, step 3
 * must still fold from step 1) gets its own test rather than a branch of one.
 *
 * The real `buildReorderBody` is used, never a stand-in: the permutation the
 * server sees must come from the same function the single-row path uses.
 */

import { describe, expect, it, vi } from 'vitest'

import { buildReorderBody } from '../../src/renderer/src/features/converter/convert-controls'
import type * as BulkReorderModule from '../../src/renderer/src/lib/queue/bulk-reorder'

function loadBulkReorder(): Promise<typeof BulkReorderModule> {
  return import(
    /* @vite-ignore */ '../../src/renderer/src/lib/queue/bulk-reorder'
  ) as Promise<typeof BulkReorderModule>
}

/**
 * A recording stand-in for the page's reorder command.
 *
 * It records the order it was HANDED (that is what becomes the wire body) and
 * optionally rejects for a given id, so a mid-run failure is expressible without
 * a second helper.
 */
function recorder(failFor: readonly string[] = []): {
  reorder: (
    ids: string[],
    selectedId: string,
    direction: 'up' | 'down' | 'top' | 'bottom',
  ) => Promise<unknown>
  bodies: () => string[][]
  ids: () => string[]
} {
  const calls: { ids: string[]; selectedId: string; direction: string }[] = []
  const reorder = vi.fn(
    async (
      ids: string[],
      selectedId: string,
      direction: 'up' | 'down' | 'top' | 'bottom',
    ): Promise<unknown> => {
      calls.push({ ids: [...ids], selectedId, direction })
      if (failFor.includes(selectedId)) {
        throw new Error(`HTTP 409 conflict reordering ${selectedId}`)
      }
      return undefined
    },
  )
  return {
    reorder,
    // What the API would receive: the permutation built from the order handed in.
    bodies: () =>
      calls.map((call) => buildReorderBody(call.ids, call.selectedId, call.direction as 'top').job_ids),
    ids: () => calls.map((call) => call.selectedId),
  }
}

const ORDER = ['a', 'b', 'c', 'd', 'e']

describe('MEU-47 bulkReorder', () => {
  it('AC-47.7a move-to-top folds each request from the preceding accepted order', async () => {
    const { bulkReorder } = await loadBulkReorder()
    const rec = recorder()

    const result = await bulkReorder(ORDER, ['b', 'd'], 'top', {
      reorder: rec.reorder,
      buildBody: buildReorderBody,
    })

    // Reversed render order, so the selected rows keep their relative order once
    // they arrive at the top.
    expect(rec.ids(), 'move-top walks the selection in reverse render order').toEqual(['d', 'b'])

    const bodies = rec.bodies()
    expect(bodies[0], 'step 1 folds from the initial order').toEqual(['d', 'a', 'b', 'c', 'e'])
    expect(bodies[1], 'step 2 folds from step 1, not from the stale initial order').toEqual([
      'b',
      'd',
      'a',
      'c',
      'e',
    ])
    // The whole point: b lands above d, exactly as they sat in the list.
    expect(bodies[bodies.length - 1].slice(0, 2)).toEqual(['b', 'd'])

    expect(result.attempted).toEqual(['d', 'b'])
    expect(result.succeeded).toEqual(['d', 'b'])
    expect(result.failed).toEqual([])
  })

  it('AC-47.7a move-to-bottom folds in render order and preserves relative order', async () => {
    const { bulkReorder } = await loadBulkReorder()
    const rec = recorder()

    await bulkReorder(ORDER, ['b', 'd'], 'bottom', {
      reorder: rec.reorder,
      buildBody: buildReorderBody,
    })

    expect(rec.ids(), 'move-bottom walks the selection in render order').toEqual(['b', 'd'])

    const bodies = rec.bodies()
    expect(bodies[0]).toEqual(['a', 'c', 'd', 'e', 'b'])
    expect(bodies[1], 'step 2 folds from step 1').toEqual(['a', 'c', 'e', 'b', 'd'])
    expect(bodies[bodies.length - 1].slice(-2)).toEqual(['b', 'd'])
  })

  it('AC-47.7a a failed step does not abort the run, and step 3 folds from step 1', async () => {
    const { bulkReorder } = await loadBulkReorder()
    // b's PUT is rejected by the server; a and c succeed.
    const rec = recorder(['b'])

    const result = await bulkReorder(ORDER, ['a', 'b', 'c'], 'bottom', {
      reorder: rec.reorder,
      buildBody: buildReorderBody,
    })

    // CLEAR_FINISHED_SEMANTICS clause 3: every selected id is still attempted.
    expect(rec.ids(), 'clause 3 — the remainder is not aborted').toEqual(['a', 'b', 'c'])

    const bodies = rec.bodies()
    expect(bodies[0]).toEqual(['b', 'c', 'd', 'e', 'a'])
    // Step 2 was computed from step 1's accepted order — and then rejected, so
    // it must NOT advance the fold.
    expect(bodies[1]).toEqual(['c', 'd', 'e', 'a', 'b'])
    // Step 3 folds from step 1's order, the last one the server accepted. Folding
    // from the rejected step 2 would give ['d','e','a','b','c']; folding from the
    // stale initial order would give ['a','b','d','e','c']. Both are wrong.
    expect(bodies[2], 'step 3 folds from the last ACCEPTED order').toEqual([
      'b',
      'd',
      'e',
      'a',
      'c',
    ])

    // Clause 4 + clause 7: successes survive, and the failure carries a reason.
    expect(result.succeeded).toEqual(['a', 'c'])
    expect(result.failed.map((failure) => failure.id)).toEqual(['b'])
    expect(result.failed[0].reason).toContain('409')
    expect(result.message).toContain('409')
    // G35: the partial result reports both counts, and nothing is thrown.
    expect(result.message).toContain('2')
    expect(result.message).toContain('1')
  })

  it('AC-47.7a an empty selection issues no request at all', async () => {
    const { bulkReorder } = await loadBulkReorder()
    const rec = recorder()

    const result = await bulkReorder(ORDER, [], 'top', {
      reorder: rec.reorder,
      buildBody: buildReorderBody,
    })

    expect(rec.ids()).toEqual([])
    expect(result.attempted).toEqual([])
    expect(result.succeeded).toEqual([])
    expect(result.failed).toEqual([])
  })

  it('AC-47.7a requests are sequential — the next is built only after the previous settles', async () => {
    const { bulkReorder } = await loadBulkReorder()

    // BULK_REORDER_ALGORITHM is a fold, so overlap is not merely wasteful: a
    // concurrent second PUT would be computed from an order the server has not
    // acknowledged. Assert at most one request is ever in flight.
    let inFlight = 0
    let maxInFlight = 0
    const reorder = vi.fn(async (): Promise<unknown> => {
      inFlight += 1
      maxInFlight = Math.max(maxInFlight, inFlight)
      await Promise.resolve()
      inFlight -= 1
      return undefined
    })

    await bulkReorder(ORDER, ['a', 'b', 'c'], 'top', { reorder, buildBody: buildReorderBody })

    expect(reorder).toHaveBeenCalledTimes(3)
    expect(maxInFlight, 'reorder PUTs never overlap').toBe(1)
  })
})
