// Session 106 (MEU-174) UPDATE_SCHEDULE, AC-174.1: the pure `isCheckDue` rule. The module is
// loaded by a dynamic import inside each test, so before Green every case fails by assertion.
import { describe, expect, it } from 'vitest'

const MODULE = '../../src/main/update-schedule'
const HOUR = 3_600_000
const DAY = 24 * HOUR
const NOW = Date.UTC(2026, 10, 27, 12, 0, 0)

type Interval = 'weekly' | 'monthly' | 'never'
type DueInput = {
  now: number
  interval: Interval
  lastCheckAt: number | null
  lastAttemptAt: number | null
  pendingVersion: string | null
  recoveryDone: boolean
}

async function loadIsCheckDue(): Promise<(input: DueInput) => boolean> {
  const mod = (await import(MODULE).catch(() => ({}))) as Record<string, unknown>
  expect(typeof mod.isCheckDue, 'update-schedule exports isCheckDue').toBe('function')
  return mod.isCheckDue as (input: DueInput) => boolean
}

function input(over: Partial<DueInput>): DueInput {
  return {
    now: NOW,
    interval: 'weekly',
    lastCheckAt: null,
    lastAttemptAt: null,
    pendingVersion: null,
    recoveryDone: true,
    ...over,
  }
}

describe('MEU-174 UPDATE_SCHEDULE isCheckDue', () => {
  it('AC-174.1 weekly is not due one millisecond before seven days and due at seven days', async () => {
    const isCheckDue = await loadIsCheckDue()
    expect(isCheckDue(input({ lastCheckAt: NOW - 7 * DAY + 1, lastAttemptAt: NOW - 7 * DAY + 1 }))).toBe(false)
    expect(isCheckDue(input({ lastCheckAt: NOW - 7 * DAY, lastAttemptAt: NOW - 7 * DAY }))).toBe(true)
    expect(isCheckDue(input({ lastCheckAt: NOW - 8 * DAY, lastAttemptAt: NOW - 8 * DAY }))).toBe(true)
  })

  it('AC-174.1 monthly is not due one millisecond before thirty days and due at thirty days', async () => {
    const isCheckDue = await loadIsCheckDue()
    const monthly = (at: number) => input({ interval: 'monthly', lastCheckAt: at, lastAttemptAt: at })
    expect(isCheckDue(monthly(NOW - 7 * DAY))).toBe(false)
    expect(isCheckDue(monthly(NOW - 30 * DAY + 1))).toBe(false)
    expect(isCheckDue(monthly(NOW - 30 * DAY))).toBe(true)
  })

  it('AC-174.1 a null lastCheckAt or one in the future is due', async () => {
    const isCheckDue = await loadIsCheckDue()
    for (const interval of ['weekly', 'monthly'] as const) {
      expect(isCheckDue(input({ interval })), `${interval} null`).toBe(true)
      expect(
        isCheckDue(input({ interval, lastCheckAt: NOW + HOUR, lastAttemptAt: NOW - 2 * DAY })),
        `${interval} future`,
      ).toBe(true)
    }
  })

  it('AC-174.1 [neg] never is not due for any input', async () => {
    const isCheckDue = await loadIsCheckDue()
    const cases: Array<Partial<DueInput>> = [
      {},
      { lastCheckAt: NOW - 400 * DAY, lastAttemptAt: NOW - 400 * DAY },
      { lastCheckAt: NOW + DAY },
      { pendingVersion: '2.0.0', recoveryDone: false },
      { pendingVersion: '2.0.0', recoveryDone: true, lastAttemptAt: NOW - 30 * DAY },
    ]
    for (const c of cases) {
      expect(isCheckDue(input({ ...c, interval: 'never' })), JSON.stringify(c)).toBe(false)
    }
  })

  it('AC-174.1 [neg] a failed attempt 23 h ago is not due and one 24 h ago is due', async () => {
    const isCheckDue = await loadIsCheckDue()
    expect(isCheckDue(input({ lastCheckAt: null, lastAttemptAt: NOW - 23 * HOUR }))).toBe(false)
    expect(isCheckDue(input({ lastCheckAt: NOW - 8 * DAY, lastAttemptAt: NOW - 23 * HOUR }))).toBe(false)
    expect(isCheckDue(input({ lastCheckAt: null, lastAttemptAt: NOW - 24 * HOUR }))).toBe(true)
    expect(isCheckDue(input({ lastCheckAt: null, lastAttemptAt: NOW + HOUR }))).toBe(true)
  })

  it('AC-174.1 [neg] a pending version is due once per start: recoveryDone false is due, true is not', async () => {
    const isCheckDue = await loadIsCheckDue()
    const pending = { pendingVersion: '2.0.0', lastCheckAt: NOW - HOUR, lastAttemptAt: NOW - HOUR }
    expect(isCheckDue(input({ ...pending, recoveryDone: false }))).toBe(true)
    expect(isCheckDue(input({ ...pending, recoveryDone: true }))).toBe(false)
    expect(
      isCheckDue(input({ ...pending, recoveryDone: true, lastAttemptAt: NOW - 24 * HOUR })),
      'a pending version passes the period once the 24 h attempt rule allows',
    ).toBe(true)
  })
})
