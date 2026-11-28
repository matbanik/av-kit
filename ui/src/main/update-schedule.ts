// UPDATE_SCHEDULE (Session 106, MEU-174): when a scheduled update check is due. Pure: the clock,
// the saved interval and the stored times come in, a yes or no goes out.

export const UPDATE_INTERVAL_WIRES = ['weekly', 'monthly', 'never'] as const
export type UpdateInterval = (typeof UPDATE_INTERVAL_WIRES)[number]

const DAY_MS = 24 * 60 * 60 * 1000
/** A failed attempt waits this long before the next scheduled one. */
export const RETRY_AFTER_MS = DAY_MS
export const PERIOD_MS: Record<Exclude<UpdateInterval, 'never'>, number> = {
  weekly: 7 * DAY_MS,
  monthly: 30 * DAY_MS,
}

export function isUpdateInterval(value: unknown): value is UpdateInterval {
  return typeof value === 'string' && (UPDATE_INTERVAL_WIRES as readonly string[]).includes(value)
}

export function isCheckDue(input: {
  now: number
  interval: UpdateInterval
  lastCheckAt: number | null
  lastAttemptAt: number | null
  pendingVersion: string | null
  recoveryDone: boolean
}): boolean {
  const { now, interval, lastCheckAt, lastAttemptAt, pendingVersion, recoveryDone } = input
  if (interval === 'never') {
    return false
  }
  // A found version that waits is checked once per app start, whatever the 24 h rule says.
  if (pendingVersion !== null && !recoveryDone) {
    return true
  }
  const periodOver =
    lastCheckAt === null || lastCheckAt > now || now - lastCheckAt >= PERIOD_MS[interval] || pendingVersion !== null
  const retryAllowed = lastAttemptAt === null || lastAttemptAt > now || now - lastAttemptAt >= RETRY_AFTER_MS
  return periodOver && retryAllowed
}
