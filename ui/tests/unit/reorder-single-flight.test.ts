/**
 * MEU-49 — `REORDER_SINGLE_FLIGHT_RULE`, the primitive half.
 *
 * Queue reorder bodies are ABSOLUTE permutations, so two requests computed from
 * the same pre-mutation order clobber each other last-write-wins. The gate that
 * prevents it has to be readable in the SAME synchronous tick the entry point
 * runs in — a `useState` mirror is written asynchronously, so two calls in one
 * tick would both see `false` and both proceed. These tests are that
 * distinction, spelled out as assertions.
 */

import { describe, expect, it } from 'vitest'

import { createSingleFlight } from '../../src/renderer/src/lib/queue/reorder-single-flight'

describe('MEU-49 REORDER_SINGLE_FLIGHT_RULE createSingleFlight', () => {
  it('AC-49.31 the first tryAcquire wins and every later one loses until release', () => {
    const gate = createSingleFlight()

    expect(gate.tryAcquire()).toBe(true)
    // Both of these run before any microtask, let alone a React commit. A
    // state-backed gate returns true here; a plain boolean returns false.
    expect(gate.tryAcquire()).toBe(false)
    expect(gate.tryAcquire()).toBe(false)

    gate.release()

    expect(gate.tryAcquire()).toBe(true)
  })

  it('AC-49.31 held reflects the gate synchronously within the same tick', () => {
    const gate = createSingleFlight()

    expect(gate.held).toBe(false)
    gate.tryAcquire()
    expect(gate.held).toBe(true)
    gate.release()
    expect(gate.held).toBe(false)
  })

  it('AC-49.31 release without a prior acquire is a no-op, not an error or a credit', () => {
    const gate = createSingleFlight()

    expect(() => {
      gate.release()
    }).not.toThrow()
    expect(gate.held).toBe(false)

    // Releasing twice may not bank a second permit: the next acquire still
    // takes the gate, and the one after it is still refused.
    gate.tryAcquire()
    gate.release()
    gate.release()
    expect(gate.tryAcquire()).toBe(true)
    expect(gate.tryAcquire()).toBe(false)
  })

  it('AC-49.31 two instances are independent', () => {
    const first = createSingleFlight()
    const second = createSingleFlight()

    expect(first.tryAcquire()).toBe(true)
    expect(second.tryAcquire()).toBe(true)
    expect(first.held).toBe(true)
    expect(second.held).toBe(true)

    first.release()
    expect(first.held).toBe(false)
    expect(second.held).toBe(true)
    expect(second.tryAcquire()).toBe(false)
  })
})
