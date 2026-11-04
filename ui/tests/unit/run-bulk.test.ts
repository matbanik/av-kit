/**
 * MEU-45 — the shared bulk executor (AC-45.18).
 *
 * `runBulk` and the `clearFinished` built on it land in MEU-45, before any
 * toolbar mounts `Clear finished`, so no control is ever dead at a MEU boundary
 * (`NO_DEAD_CONTROL_RULE`). Every one of the seven `CLEAR_FINISHED_SEMANTICS`
 * clauses is normative, so each gets its own assertion here — the clause text is
 * read from the plan's `named-sets.json` rather than restated, and the test
 * fails loudly if the clause list ever changes length.
 *
 * `BULK_ENDPOINT_POLICY` is asserted structurally: the executor only ever calls
 * the caller's per-id function with the id and nothing else, so there is no way
 * to smuggle a `POST /{queue}/bulk` body or a `purge_files` flag through it.
 */

import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it, vi } from 'vitest'

import type * as RunBulkModule from '../../src/renderer/src/lib/queue/run-bulk'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')
const planDir = resolve(repoRoot, 'docs/execution/plans/2026-09-02-p10-queue-card-migration')

type NamedSet<T> = { value: T }
type NamedSets = {
  CLEAR_FINISHED_SEMANTICS: NamedSet<string[]>
  CLEAR_FINISHED_SNAPSHOT_STATUSES: NamedSet<string[]>
}

const SETS = JSON.parse(readFileSync(resolve(planDir, 'named-sets.json'), 'utf-8')) as NamedSets

const CLAUSES = SETS.CLEAR_FINISHED_SEMANTICS.value
const SNAPSHOT_STATUSES = SETS.CLEAR_FINISHED_SNAPSHOT_STATUSES.value

function loadRunBulk(): Promise<typeof RunBulkModule> {
  return import(
    /* @vite-ignore */ '../../src/renderer/src/lib/queue/run-bulk'
  ) as Promise<typeof RunBulkModule>
}

type Item = { id: string; status: string }

/** A queue whose statuses cover the snapshot set and its complement. */
function queue(): Item[] {
  return [
    { id: 'a', status: 'Done' },
    { id: 'b', status: 'Failed' },
    { id: 'c', status: 'Done' },
    { id: 'd', status: 'Processing' },
    { id: 'e', status: 'Cancelled' },
    { id: 'f', status: 'Pending' },
    { id: 'g', status: 'Skipped' },
  ]
}

describe('MEU-45 runBulk / clearFinished', () => {
  it('AC-45.18 runBulk/clearFinished satisfy all 7 CLEAR_FINISHED_SEMANTICS clauses', async () => {
    const { runBulk, clearFinished } = await loadRunBulk()
    expect(CLAUSES, 'the clause table is still seven clauses').toHaveLength(7)
    expect(SNAPSHOT_STATUSES, 'only Done rows are swept').toEqual(['Done'])

    // -- Clause 1: snapshot once -------------------------------------------
    // A job that reaches Done *during* the fan-out is not swept.
    const items = queue()
    const order: string[] = []
    const removeThenFinishAnother = vi.fn(async (id: string) => {
      order.push(`remove:${id}`)
      items.push({ id: 'late', status: 'Done' })
      return undefined
    })
    const refetchOnce = vi.fn(async () => {
      order.push('refetch')
      return undefined
    })

    const swept = await clearFinished(items, removeThenFinishAnother, refetchOnce)

    const attemptedIds = removeThenFinishAnother.mock.calls.map((call) => call[0])
    expect(attemptedIds.sort(), 'clause 1 — the Done set is snapshotted before the first request')
      .toEqual(['a', 'c'])
    expect(attemptedIds, 'clause 1 — a mid-run Done job is not swept').not.toContain('late')
    expect(swept.attempted.slice().sort()).toEqual(['a', 'c'])

    // -- Clause 2: independence + BULK_ENDPOINT_POLICY ----------------------
    expect(removeThenFinishAnother, 'clause 2 — one DELETE per snapshotted id').toHaveBeenCalledTimes(
      2,
    )
    for (const call of removeThenFinishAnother.mock.calls) {
      expect(call, 'clause 2 — the per-id function takes the id and nothing else').toHaveLength(1)
      expect(typeof call[0]).toBe('string')
    }

    // -- Clause 5: files stay on disk ---------------------------------------
    // Structural: with no second argument there is no purge flag to set, so the
    // executor cannot ask the API for anything beyond the queue record.
    expect(
      removeThenFinishAnother.mock.calls.every((call) => call.length === 1),
      'clause 5 — no purge/delete-files argument is ever passed',
    ).toBe(true)

    // -- Clause 6: exactly one refetch, after the fan-out settles ------------
    expect(refetchOnce, 'clause 6 — exactly one list refetch').toHaveBeenCalledTimes(1)
    expect(order, 'clause 6 — the refetch runs after every request settles').toEqual([
      'remove:a',
      'remove:c',
      'refetch',
    ])

    // -- Clause 3: continue on failure --------------------------------------
    const attempts: string[] = []
    const flaky = vi.fn(async (id: string) => {
      attempts.push(id)
      if (id === 'b') {
        throw new Error('HTTP 500 upstream exploded')
      }
      if (id === 'c') {
        throw new Error('HTTP 404 already gone')
      }
      return undefined
    })

    const result = await runBulk(['a', 'b', 'c', 'd', 'e'], flaky)

    expect(attempts, 'clause 3 — every id is attempted exactly once').toEqual([
      'a',
      'b',
      'c',
      'd',
      'e',
    ])
    expect(flaky).toHaveBeenCalledTimes(5)

    // -- Clause 4: successes kept -------------------------------------------
    expect(result.succeeded, 'clause 4 — confirmed deletions survive a later failure').toEqual([
      'a',
      'd',
      'e',
    ])
    expect(
      attempts.filter((id) => id === 'a'),
      'clause 4 — a succeeded id is never re-issued as a rollback',
    ).toHaveLength(1)

    // -- Clause 7: report ----------------------------------------------------
    expect(result.failed.map((failure) => failure.id)).toEqual(['b', 'c'])
    expect(result.failed[0].reason, 'clause 7 — a reason per failure').toContain('500')
    expect(result.failed[1].reason, 'clause 7 — a reason per failure').toContain('404')
    expect(result.message, 'clause 7 — the removed count').toContain('3')
    expect(result.message, 'clause 7 — the failed-or-skipped count').toContain('2')
    for (const failure of result.failed) {
      expect(result.message, `clause 7 — ${failure.id}'s reason reaches the report`).toContain(
        failure.reason,
      )
    }

    // A per-item failure is reported, never thrown: the caller always gets a
    // result it can render (ERROR_SURFACE / G35).
    await expect(runBulk(['b'], flaky)).resolves.toBeDefined()
  })

  it('AC-45.18 an all-success run still reports counts and refetches exactly once', async () => {
    const { runBulk, clearFinished } = await loadRunBulk()

    const remove = vi.fn(async () => undefined)
    const refetch = vi.fn(async () => undefined)
    const result = await clearFinished(queue(), remove, refetch)

    expect(remove).toHaveBeenCalledTimes(2)
    expect(refetch).toHaveBeenCalledTimes(1)
    expect(result.failed).toEqual([])
    expect(result.succeeded).toEqual(['a', 'c'])
    expect(result.message).toContain('2')

    // An empty snapshot issues no request at all, and still reconciles once so
    // the rendered list is the server's, never local optimistic state.
    const noneRemove = vi.fn(async () => undefined)
    const noneRefetch = vi.fn(async () => undefined)
    const none = await clearFinished(
      [{ id: 'x', status: 'Pending' }],
      noneRemove,
      noneRefetch,
    )
    expect(noneRemove).not.toHaveBeenCalled()
    expect(noneRefetch).toHaveBeenCalledTimes(1)
    expect(none.attempted).toEqual([])

    // runBulk itself is queue-agnostic — it fans out whatever ids it is given.
    const plain = await runBulk([], vi.fn(async () => undefined))
    expect(plain.attempted).toEqual([])
    expect(plain.succeeded).toEqual([])
    expect(plain.failed).toEqual([])
  })
})

/**
 * MEU-47 widens the executor so every bulk action — not just `Clear finished` —
 * runs through one implementation of `CLEAR_FINISHED_SEMANTICS`. Two things
 * change: the caller may name the operation (the G35 message is not always
 * "Removed"), and the single-reconcile rule (clause 6) moves inside `runBulk`
 * so a bulk Retry or Move cannot forget it.
 */
describe('MEU-47 runBulk selection fan-out', () => {
  it('AC-47.2 runBulk snapshots, continues on failure, refetches exactly once', async () => {
    const { runBulk } = await loadRunBulk()

    const ids = ['s1', 'f1', 's2', 'f2', 'f3']
    const settled: string[] = []
    const timeline: string[] = []
    const run = vi.fn(async (id: string) => {
      settled.push(id)
      timeline.push(`run:${id}`)
      if (id.startsWith('f')) {
        throw new Error(`HTTP 500 ${id} rejected`)
      }
      return undefined
    })
    const refetch = vi.fn(async () => {
      timeline.push('refetch')
      return undefined
    })

    // Clause 1: the caller's array is snapshotted. Mutating it mid-run — which
    // is exactly what a poll landing during the fan-out does — changes nothing.
    const result = await runBulk(ids, run, { verb: 'Retried', refetch })
    ids.push('late')

    expect(settled, 'clause 2/3 — every id attempted exactly once, in order').toEqual([
      's1',
      'f1',
      's2',
      'f2',
      'f3',
    ])
    expect(result.attempted, 'clause 1 — the snapshot ignores later mutation').toEqual([
      's1',
      'f1',
      's2',
      'f2',
      'f3',
    ])

    // Clause 4: the two successes persist even though three later calls rejected.
    expect(result.succeeded).toEqual(['s1', 's2'])
    expect(result.failed.map((failure) => failure.id)).toEqual(['f1', 'f2', 'f3'])

    // Clause 6: exactly one reconcile, and only after the last request settles.
    expect(refetch, 'clause 6 — exactly one refetch').toHaveBeenCalledTimes(1)
    expect(timeline[timeline.length - 1]).toBe('refetch')

    // Clause 7: counts plus the caller's verb, so a bulk Retry does not report
    // itself as a removal.
    expect(result.message).toContain('2')
    expect(result.message).toContain('3')
    expect(result.message, 'the operation names itself').toContain('Retried')
    for (const failure of result.failed) {
      expect(result.message).toContain(failure.reason)
    }
  })

  it('AC-47.2 runBulk without a refetch still reports, and an empty run reconciles once', async () => {
    const { runBulk } = await loadRunBulk()

    // The refetch is optional: a caller that reconciles by other means (or not
    // at all) must still get a renderable result rather than a throw.
    const bare = await runBulk(['x'], vi.fn(async () => undefined))
    expect(bare.succeeded).toEqual(['x'])
    expect(bare.message).toContain('1')

    // An empty selection issues no per-id request but still reconciles, so the
    // rendered list is always the server's.
    const run = vi.fn(async () => undefined)
    const refetch = vi.fn(async () => undefined)
    const none = await runBulk([], run, { refetch })
    expect(run).not.toHaveBeenCalled()
    expect(refetch).toHaveBeenCalledTimes(1)
    expect(none.attempted).toEqual([])
  })
})
