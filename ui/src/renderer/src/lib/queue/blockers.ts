/**
 * Remediation copy for the queue's *blocker* statuses.
 *
 * A blocker is not a transient failure: the job stopped because the user's own
 * configuration forbids it, so the only useful thing the card can say is where
 * to go and change that. The strings live here rather than in `QueueCard` so
 * that the card renders remediation it does not author — one owner for the copy,
 * and a settings-path rename lands in exactly one file.
 */

/**
 * Settings path to fix each blocker, keyed by the status the API reports.
 *
 * Verbatim from the plan's `BLOCKER_REMEDIATION` named set.
 */
export const BLOCKER_REMEDIATION: Readonly<Record<string, string>> = {
  QualityBlocked:
    'Settings > Downloader > Quality (choose a lower quality, or a supported audio format for audio-only jobs)',
  AgeRestricted: 'Settings > Cookies & Authentication (sign-in required for this video)',
}

/** Statuses that carry remediation copy. */
export const BLOCKER_STATUSES: readonly string[] = Object.keys(BLOCKER_REMEDIATION)

/**
 * Look up the remediation line for a status.
 *
 * @param status - Status name as the API reported it.
 * @returns The remediation copy, or `null` when the status is not a blocker.
 */
export function resolveBlockerRemediation(status: string): string | null {
  return BLOCKER_REMEDIATION[status] ?? null
}
