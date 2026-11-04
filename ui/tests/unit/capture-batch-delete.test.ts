/** @vitest-environment jsdom */

import { afterEach, beforeEach, describe, expect, it, vi, type MockInstance } from 'vitest'

import { deleteCaptures } from '../../src/renderer/src/features/capture/capture-commands'
import { queryClient } from '../../src/renderer/src/lib/query-client'

// Session 38 (MEU-89): BATCH_DELETE removes shots one at a time, in the given order, and
// reports each failure instead of stopping at the first one.

type Deferred = { promise: Promise<void>; resolve: () => void; reject: (error: Error) => void }

function deferred(): Deferred {
  let resolve!: () => void
  let reject!: (error: Error) => void
  const promise = new Promise<void>((res, rej) => {
    resolve = res
    reject = rej
  })
  return { promise, resolve, reject }
}

describe('MEU-89 deleteCaptures', () => {
  let invalidate: MockInstance<typeof queryClient.invalidateQueries>

  beforeEach(() => {
    invalidate = vi.spyOn(queryClient, 'invalidateQueries').mockResolvedValue(undefined)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('AC-89.7 calls remove once per id in order and starts each call only after the previous one settles', async () => {
    const pending: Record<string, Deferred> = { a: deferred(), b: deferred(), c: deferred() }
    const started: string[] = []
    const remove = vi.fn((id: string) => {
      started.push(id)
      return (pending[id] as Deferred).promise
    })
    const result = deleteCaptures(['a', 'b', 'c'], remove)

    await vi.waitFor(() => {
      expect(started).toEqual(['a'])
    })
    await Promise.resolve()
    expect(started).toEqual(['a'])
    pending.a?.resolve()
    await vi.waitFor(() => {
      expect(started).toEqual(['a', 'b'])
    })
    expect(invalidate).not.toHaveBeenCalled()
    pending.b?.resolve()
    await vi.waitFor(() => {
      expect(started).toEqual(['a', 'b', 'c'])
    })
    pending.c?.resolve()

    await expect(result).resolves.toEqual({ deleted: ['a', 'b', 'c'], failed: [] })
    expect(remove).toHaveBeenCalledTimes(3)
    expect(invalidate).toHaveBeenCalledTimes(1)
    expect(invalidate).toHaveBeenCalledWith({ queryKey: ['captures'] })
  })

  it('AC-89.7 continues past a rejection and reports it as { id, message }', async () => {
    const remove = vi.fn(async (id: string) => {
      if (id === 'b') {
        throw new Error('disk refused b')
      }
    })
    const result = await deleteCaptures(['a', 'b', 'c'], remove)
    expect(remove.mock.calls.map((call) => call[0])).toEqual(['a', 'b', 'c'])
    expect(result).toEqual({ deleted: ['a', 'c'], failed: [{ id: 'b', message: 'disk refused b' }] })
    expect(invalidate).toHaveBeenCalledTimes(1)
  })

  it('AC-89.7 reports every failure when all removes reject, and still invalidates once', async () => {
    const remove = vi.fn(async (id: string) => {
      throw new Error(`locked ${id}`)
    })
    const result = await deleteCaptures(['a', 'b'], remove)
    expect(result).toEqual({
      deleted: [],
      failed: [
        { id: 'a', message: 'locked a' },
        { id: 'b', message: 'locked b' },
      ],
    })
    expect(invalidate).toHaveBeenCalledTimes(1)
  })

  it('AC-89.7 an empty ids list makes no call and no invalidation', async () => {
    const remove = vi.fn(async (_id: string) => undefined)
    await expect(deleteCaptures([], remove)).resolves.toEqual({ deleted: [], failed: [] })
    expect(remove).not.toHaveBeenCalled()
    expect(invalidate).not.toHaveBeenCalled()
  })
})
