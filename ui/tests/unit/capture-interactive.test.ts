import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import {
  CaptureApiError,
  clearCompletionJournal,
  getJournalEntry,
  journalSize,
  runInteractiveTick,
  type PendingRequest,
  type PollResult,
} from '../../src/main/capture-register'
import { resetNotifyUserDeps } from '../../src/main/notify-user'

const INBOX_PATH = 'C:/Users/Mat/Pictures/av-kit/2026-08-27_12-00-00.png'
const REQ = 'req-1'

type Notice = { title: string; body: string; path?: string }

/**
 * AC-40.33 — the interactive request lifecycle, driven one tick at a time.
 *
 * `runInteractiveTick` is the seam the 500 ms poll calls: it takes the poll's *result* and the
 * side effects as dependencies, so every case below is a real end-to-end pass through the
 * production decision logic with nothing but the network faked.
 */
describe('MEU-40 AC-40.33 interactive request lifecycle', () => {
  let notices: Notice[]
  let logs: string[]
  let clock: number

  const now = (): number => clock

  beforeEach(() => {
    notices = []
    logs = []
    clock = 1_000_000
    clearCompletionJournal()
    resetNotifyUserDeps()
  })

  afterEach(() => {
    clearCompletionJournal()
    resetNotifyUserDeps()
    vi.restoreAllMocks()
  })

  function deps(overrides: Record<string, unknown> = {}) {
    return {
      capture: vi.fn(async (_row: PendingRequest) => INBOX_PATH),
      complete: vi.fn(async () => undefined),
      cancel: vi.fn(async () => undefined),
      relist: vi.fn(async (): Promise<PollResult> => ({ kind: 'ok', rows: [] })),
      notify: (n: Notice) => {
        notices.push(n)
      },
      log: (line: string) => {
        logs.push(line)
      },
      now,
      ...overrides,
    }
  }

  const pending = (id = REQ): PollResult => ({ kind: 'ok', rows: [{ id, status: 'Pending' }] })
  const withStatus = (status: string, id = REQ): PollResult => ({
    kind: 'ok',
    rows: [{ id, status }],
  })

  it('(a) a published capture whose complete rejects is never cancelled', async () => {
    const d = deps({
      complete: vi.fn(async () => {
        throw new Error('ECONNRESET')
      }),
    })

    await runInteractiveTick(pending(), d)

    expect(d.capture).toHaveBeenCalledTimes(1)
    expect(d.complete).toHaveBeenCalledTimes(1)
    expect(d.cancel).not.toHaveBeenCalled()
    expect(logs.some((l) => l.includes(INBOX_PATH))).toBe(true)
    expect(getJournalEntry(REQ)).toMatchObject({ requestId: REQ, path: INBOX_PATH })
  })

  it('(b) a real picker cancel cancels the request exactly once', async () => {
    const d = deps({ capture: vi.fn(async () => null) })

    await runInteractiveTick(pending(), d)

    expect(d.cancel).toHaveBeenCalledTimes(1)
    expect(d.cancel).toHaveBeenCalledWith(REQ)
    expect(d.complete).not.toHaveBeenCalled()
    expect(journalSize()).toBe(0)
    expect(notices).toEqual([])
  })

  it('(c) a capture that throws before producing a file may still cancel', async () => {
    const d = deps({
      capture: vi.fn(async () => {
        throw new Error('picker exe missing')
      }),
    })

    await runInteractiveTick(pending(), d)

    expect(d.cancel).toHaveBeenCalledTimes(1)
    expect(d.complete).not.toHaveBeenCalled()
    expect(journalSize()).toBe(0)
  })

  it('(d) the next tick retries the journalled completion instead of reopening the picker', async () => {
    const failing = deps({
      complete: vi.fn(async () => {
        throw new Error('ECONNRESET')
      }),
    })
    await runInteractiveTick(pending(), failing)
    expect(journalSize()).toBe(1)

    clock += 1000
    const retry = deps()
    await runInteractiveTick(pending(), retry)

    expect(retry.capture).not.toHaveBeenCalled()
    expect(retry.complete).toHaveBeenCalledTimes(1)
    expect(retry.complete).toHaveBeenCalledWith(REQ, INBOX_PATH)
    expect(journalSize()).toBe(0)
    expect(notices).toEqual([])
  })

  it('(d) a retry that is not yet due does nothing at all', async () => {
    const failing = deps({
      complete: vi.fn(async () => {
        throw new Error('ECONNRESET')
      }),
    })
    await runInteractiveTick(pending(), failing)

    clock += 1
    const early = deps()
    await runInteractiveTick(pending(), early)

    expect(early.complete).not.toHaveBeenCalled()
    expect(early.capture).not.toHaveBeenCalled()
    expect(journalSize()).toBe(1)
  })

  it('(d) the backoff widens 1s, 2s, 4s, 8s, 15s rather than hammering every tick', async () => {
    const reject = () =>
      vi.fn(async () => {
        throw new Error('ECONNRESET')
      })

    const first = deps({ complete: reject() })
    await runInteractiveTick(pending(), first)

    const attemptsAt: number[] = []
    for (const gap of [1000, 2000, 4000, 8000, 15000]) {
      // One tick just before the deadline must not attempt.
      clock += gap - 1
      const tooEarly = deps({ complete: reject() })
      await runInteractiveTick(pending(), tooEarly)
      expect(tooEarly.complete).not.toHaveBeenCalled()

      clock += 1
      const due = deps({ complete: reject() })
      await runInteractiveTick(pending(), due)
      expect(due.complete).toHaveBeenCalledTimes(1)
      attemptsAt.push(gap)
    }

    expect(attemptsAt).toEqual([1000, 2000, 4000, 8000, 15000])
    expect(journalSize()).toBe(1)
  })

  it('(e) an Expired row drops the entry, stops retrying, and notifies exactly once', async () => {
    const failing = deps({
      complete: vi.fn(async () => {
        throw new Error('ECONNRESET')
      }),
    })
    await runInteractiveTick(pending(), failing)

    clock += 1000
    const terminal = deps()
    await runInteractiveTick(withStatus('Expired'), terminal)

    expect(terminal.complete).not.toHaveBeenCalled()
    expect(terminal.capture).not.toHaveBeenCalled()
    expect(journalSize()).toBe(0)
    expect(notices).toHaveLength(1)
    expect(notices[0]?.path).toBe(INBOX_PATH)

    clock += 60_000
    const after = deps()
    await runInteractiveTick(withStatus('Expired'), after)
    expect(after.complete).not.toHaveBeenCalled()
    expect(notices).toHaveLength(1)
  })

  it('(e) a Cancelled row is terminal in the same way', async () => {
    const failing = deps({
      complete: vi.fn(async () => {
        throw new Error('ECONNRESET')
      }),
    })
    await runInteractiveTick(pending(), failing)

    clock += 1000
    const terminal = deps()
    await runInteractiveTick(withStatus('Cancelled'), terminal)

    expect(journalSize()).toBe(0)
    expect(notices).toHaveLength(1)
    expect(notices[0]?.path).toBe(INBOX_PATH)
  })

  it('(f) a backend restart keeps the journal, notifies nobody, and the retry lands after', async () => {
    const failing = deps({
      complete: vi.fn(async () => {
        throw new Error('ECONNRESET')
      }),
    })
    await runInteractiveTick(pending(), failing)

    for (let tick = 0; tick < 5; tick += 1) {
      clock += 500
      const down = deps()
      await runInteractiveTick({ kind: 'unavailable', reason: 'ECONNREFUSED' }, down)
      expect(down.capture).not.toHaveBeenCalled()
      expect(down.cancel).not.toHaveBeenCalled()
      expect(journalSize()).toBe(1)
    }
    expect(notices).toEqual([])

    const back = deps()
    await runInteractiveTick(pending(), back)

    expect(back.complete).toHaveBeenCalledWith(REQ, INBOX_PATH)
    expect(journalSize()).toBe(0)
    expect(notices).toEqual([])
  })

  it('(f) an unavailable poll never opens the picker even with a fresh Pending row waiting', async () => {
    const down = deps()

    await runInteractiveTick({ kind: 'unavailable', reason: 'fetch failed' }, down)

    expect(down.capture).not.toHaveBeenCalled()
    expect(down.complete).not.toHaveBeenCalled()
    expect(down.cancel).not.toHaveBeenCalled()
  })

  it('(g) a journalled id that reads Completed is dropped silently', async () => {
    const failing = deps({
      complete: vi.fn(async () => {
        throw new Error('ECONNRESET')
      }),
    })
    await runInteractiveTick(pending(), failing)

    clock += 1000
    const done = deps()
    await runInteractiveTick(withStatus('Completed'), done)

    expect(done.complete).not.toHaveBeenCalled()
    expect(done.capture).not.toHaveBeenCalled()
    expect(journalSize()).toBe(0)
    expect(notices).toEqual([])
  })

  it('(h) a listing that no longer contains the id is terminal like (e)', async () => {
    const failing = deps({
      complete: vi.fn(async () => {
        throw new Error('ECONNRESET')
      }),
    })
    await runInteractiveTick(pending(), failing)

    clock += 1000
    const gone = deps()
    await runInteractiveTick({ kind: 'ok', rows: [] }, gone)

    expect(journalSize()).toBe(0)
    expect(gone.complete).not.toHaveBeenCalled()
    expect(notices).toHaveLength(1)
    expect(notices[0]?.path).toBe(INBOX_PATH)
  })

  describe('(i) a 409 is reconciled by re-reading the row, never retried into a loop', () => {
    function conflict() {
      return vi.fn(async () => {
        throw new CaptureApiError('request is not pending', 409)
      })
    }

    it('Completed on the reconciling read drops the entry silently', async () => {
      const d = deps({
        complete: conflict(),
        relist: vi.fn(async (): Promise<PollResult> => withStatus('Completed')),
      })

      await runInteractiveTick(pending(), d)

      expect(d.relist).toHaveBeenCalledTimes(1)
      expect(d.complete).toHaveBeenCalledTimes(1)
      expect(d.cancel).not.toHaveBeenCalled()
      expect(journalSize()).toBe(0)
      expect(notices).toEqual([])
    })

    it('Expired on the reconciling read drops the entry WITH the terminal notice', async () => {
      const d = deps({
        complete: conflict(),
        relist: vi.fn(async (): Promise<PollResult> => withStatus('Expired')),
      })

      await runInteractiveTick(pending(), d)

      expect(journalSize()).toBe(0)
      expect(notices).toHaveLength(1)
      expect(notices[0]?.path).toBe(INBOX_PATH)
      expect(d.complete).toHaveBeenCalledTimes(1)
    })

    it('Cancelled on the reconciling read drops the entry WITH the terminal notice', async () => {
      const d = deps({
        complete: conflict(),
        relist: vi.fn(async (): Promise<PollResult> => withStatus('Cancelled')),
      })

      await runInteractiveTick(pending(), d)

      expect(journalSize()).toBe(0)
      expect(notices).toHaveLength(1)
    })

    it('an unavailable reconciling read keeps the entry for a later tick', async () => {
      const d = deps({
        complete: conflict(),
        relist: vi.fn(async (): Promise<PollResult> => ({ kind: 'unavailable', reason: 'down' })),
      })

      await runInteractiveTick(pending(), d)

      expect(journalSize()).toBe(1)
      expect(notices).toEqual([])
    })

    it('a 409 is never re-attempted against the same row on the next tick', async () => {
      const first = deps({
        complete: conflict(),
        relist: vi.fn(async (): Promise<PollResult> => ({ kind: 'unavailable', reason: 'down' })),
      })
      await runInteractiveTick(pending(), first)

      clock += 60_000
      const second = deps({ relist: vi.fn(async (): Promise<PollResult> => withStatus('Completed')) })
      await runInteractiveTick(withStatus('Completed'), second)

      expect(second.complete).not.toHaveBeenCalled()
      expect(journalSize()).toBe(0)
      expect(notices).toEqual([])
    })
  })

  it('the picker only opens for a Pending row that is not already journalled', async () => {
    const failing = deps({
      complete: vi.fn(async () => {
        throw new Error('ECONNRESET')
      }),
    })
    await runInteractiveTick(pending('req-old'), failing)

    clock += 1000
    const mixed = deps()
    await runInteractiveTick(
      {
        kind: 'ok',
        rows: [
          { id: 'req-old', status: 'Pending' },
          { id: 'req-new', status: 'Pending' },
        ],
      },
      mixed,
    )

    expect(mixed.complete).toHaveBeenCalledWith('req-old', INBOX_PATH)
    expect(mixed.capture).toHaveBeenCalledTimes(1)
    expect(mixed.capture.mock.calls[0]?.[0]).toMatchObject({ id: 'req-new' })
  })

  it('a non-Pending head row never opens the picker', async () => {
    const d = deps()

    await runInteractiveTick(withStatus('Completed', 'req-done'), d)

    expect(d.capture).not.toHaveBeenCalled()
    expect(d.complete).not.toHaveBeenCalled()
    expect(d.cancel).not.toHaveBeenCalled()
  })
})
