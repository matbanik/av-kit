/**
 * Client-side bulk fan-out for the queue pages.
 *
 * `BULK_ENDPOINT_POLICY` is the reason this module exists: there is no
 * `POST /{queue}/bulk` endpoint and none may be invented, so every bulk action
 * issues the existing per-id request N times. That makes partial success the
 * normal case rather than an edge case, and `CLEAR_FINISHED_SEMANTICS` states
 * exactly how a partial run must behave — snapshot once, attempt each id
 * exactly once, never roll a success back, reconcile once, and report a reason
 * per failure (G35).
 *
 * Nothing here throws for a per-item failure: the caller always receives a
 * result it can render, because a bulk action that vanishes into an exception
 * leaves the user with a queue that silently did not change.
 */

/** One id that could not be processed, with the reason to show the user. */
export type BulkFailure = {
  /** The id whose request failed. */
  id: string
  /** Human-readable reason, carrying the HTTP status where there was one. */
  reason: string
}

/** The outcome of a bulk fan-out. */
export type BulkResult = {
  /** Every id the run attempted, in snapshot order. */
  attempted: string[]
  /** Ids whose request resolved. */
  succeeded: string[]
  /** Ids whose request rejected, with reasons. */
  failed: BulkFailure[]
  /** The G35 partial-result summary: counts plus a reason per failure. */
  message: string
}

/** The statuses `clearFinished` sweeps (`CLEAR_FINISHED_SNAPSHOT_STATUSES`). */
export const CLEAR_FINISHED_STATUSES: readonly string[] = ['Done']

/** The minimum a row needs to expose to take part in a sweep. */
export type BulkSweepItem = {
  id: string
  status: string
}

/**
 * Turn an unknown rejection into a reason string.
 *
 * @param error - Whatever the per-id function rejected with.
 * @returns The error's message, or a stringified fallback for a non-Error.
 */
function reasonFor(error: unknown): string {
  // The command layer already normalises an API rejection into an Error whose
  // message carries the HTTP status (`toCommandError`), which is what makes a
  // 404 ("the row was already gone") distinguishable from a 5xx ("worth
  // retrying") in the report.
  if (error instanceof Error && error.message !== '') {
    return error.message
  }
  const text = String(error)
  return text === '' ? 'unknown error' : text
}

/**
 * Compose the G35 partial-result message (clause 7).
 *
 * @param succeeded - Ids whose request resolved.
 * @param failed - Ids whose request rejected, with reasons.
 * @param verb - Past-tense verb describing what succeeded, e.g. `Removed`.
 * @returns A single line stating both counts and every failure reason.
 */
function composeMessage(
  succeeded: readonly string[],
  failed: readonly BulkFailure[],
  verb: string,
): string {
  const total = succeeded.length + failed.length
  const head = `${verb} ${String(succeeded.length)} of ${String(total)}`
  if (failed.length === 0) {
    return `${head}.`
  }
  const reasons = failed.map((failure) => `${failure.id} - ${failure.reason}`).join('; ')
  return `${head}. ${String(failed.length)} failed: ${reasons}`
}

/** How one bulk run names itself and reconciles when it is done. */
export type BulkOptions = {
  /** Past-tense verb for the G35 report, e.g. `Retried`. Defaults to `Removed`. */
  verb?: string
  /**
   * Reconciles the list against the server. Called exactly once after the whole
   * fan-out settles — including when the id list was empty.
   */
  refetch?: () => Promise<unknown>
  /**
   * Hold each request back until the previous one has settled.
   *
   * Only a fan-out whose next request is BUILT FROM the previous one's outcome
   * needs this — `bulkReorder`'s fold is the only such caller, and issuing its
   * steps together would have every one of them computed from the same stale
   * order. Independent actions (retry, remove, sweep) leave it off: clause 2
   * says the rows do not depend on each other, and serialising them would make
   * one user gesture arrive at the queue as N separate mutations spread over N
   * round trips, with the list visibly rewriting itself between each.
   */
  dependent?: boolean
}

/**
 * Fan a per-id request out over a fixed id list.
 *
 * The ids are processed in order and **exactly once each** (clause 3): a
 * rejection is recorded and the run continues, and a success already confirmed
 * is never re-issued as a rollback (clause 4). "In order" is about the requests
 * the run ISSUES and the order it REPORTS them in, not about waiting: by
 * default every request is handed to the transport in one pass, because clause
 * 2 makes the rows independent and a bulk gesture should reach the queue as one
 * change rather than N. A caller whose next request depends on the previous
 * one's result asks for `dependent: true`. The per-id function is called
 * with the id and nothing else, which is what keeps a purge flag or a bulk body
 * structurally impossible (clause 5, `BULK_ENDPOINT_POLICY`).
 *
 * The single reconcile (clause 6) lives here rather than at the call sites so a
 * bulk Retry or Move cannot forget it, and so it cannot accidentally be issued
 * per-id: the list the user ends up looking at is always the server's.
 *
 * @param ids - The ids to process; copied, so later mutation cannot widen the run.
 * @param run - The per-id request; rejects to report a failure.
 * @param options - The report verb and the optional single reconcile.
 * @returns The per-id outcome and the message to render. Never rejects.
 */
export async function runBulk(
  ids: readonly string[],
  run: (id: string) => Promise<unknown>,
  options: BulkOptions = {},
): Promise<BulkResult> {
  const { verb = 'Removed', refetch, dependent = false } = options
  const attempted = [...ids]
  const succeeded: string[] = []
  const failed: BulkFailure[] = []

  if (dependent) {
    for (const id of attempted) {
      try {
        await run(id)
        succeeded.push(id)
      } catch (error) {
        failed.push({ id, reason: reasonFor(error) })
      }
    }
  } else {
    /*
      `map` invokes `run` for every id in one synchronous pass, so the requests
      leave together and the queue is not observable in a half-applied state
      between them. `allSettled` then reports in INPUT order regardless of which
      one answered first, which is what keeps `succeeded`/`failed` — and the
      G35 message built from them — in the order the user's rows are listed.
    */
    const outcomes = await Promise.allSettled(attempted.map((id) => run(id)))
    outcomes.forEach((outcome, index) => {
      const id = attempted[index]
      if (outcome.status === 'fulfilled') {
        succeeded.push(id)
        return
      }
      failed.push({ id, reason: reasonFor(outcome.reason) })
    })
  }

  if (refetch !== undefined) {
    await refetch()
  }

  return { attempted, succeeded, failed, message: composeMessage(succeeded, failed, verb) }
}

/**
 * Sweep every finished row off the queue.
 *
 * The snapshot is taken before the first request (clause 1), so a job that
 * reaches `Done` while the fan-out is in flight survives to the next sweep
 * rather than disappearing under the user. The list is refetched exactly once
 * after the fan-out settles — including when the snapshot was empty — because
 * the rendered list must be the server's, never local optimistic state
 * (clause 6).
 *
 * @param items - The queue as currently rendered.
 * @param remove - Removes one queue record by id; the media file stays on disk.
 * @param refetch - Reconciles the list against the server.
 * @returns The per-id outcome and the message to render. Never rejects.
 */
export async function clearFinished(
  items: readonly BulkSweepItem[],
  remove: (id: string) => Promise<unknown>,
  refetch: () => Promise<unknown>,
): Promise<BulkResult> {
  const snapshot = items
    .filter((item) => CLEAR_FINISHED_STATUSES.includes(item.status))
    .map((item) => item.id)

  return runBulk(snapshot, remove, { refetch })
}
