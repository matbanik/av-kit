import { useEffect, useState, useSyncExternalStore } from 'react'
import { queryClient } from '../query-client'
import type { ProcessorState } from './envelope'

/** Queue kinds that keep a pause request mark (D-1097). */
export type PauseQueueKind = 'convert' | 'download'

/**
 * A pause request mark. A job mark names the job that was running when the
 * pause landed; an unbound mark (`jobId` null) was set between jobs and holds
 * `markedAt` so it can be bound to the next job id or spent after
 * `PAUSE_UNBOUND_MS`.
 */
export type PauseMark = { jobId: string | null; markedAt?: number }

/** The observed processor of a list envelope; `undefined` before any list read. */
export type ObservedProcessor = { state: ProcessorState; current_job_id?: string | null } | undefined

/** How long an unbound mark may wait for a job id before it is spent. */
export const PAUSE_UNBOUND_MS = 15_000

/** Status shown in place of the processor label while a pause is pending. */
export const PAUSE_PENDING_STATUS = 'Queue stops when the current job ends'

const PAUSE_REQUEST_ROOT = 'queue-pause-request'

/** PAUSE_MARK: the mark outlives a page unmount, so it is never collected. */
queryClient.setQueryDefaults([PAUSE_REQUEST_ROOT], { gcTime: Infinity })

export function pauseRequestKey(kind: PauseQueueKind): readonly [string, PauseQueueKind] {
  return [PAUSE_REQUEST_ROOT, kind] as const
}

export function markPauseRequested(kind: PauseQueueKind, jobId: string | null): void {
  const mark: PauseMark = jobId === null ? { jobId: null, markedAt: Date.now() } : { jobId }
  queryClient.setQueryData<PauseMark | null>(pauseRequestKey(kind), mark)
}

export function clearPauseRequest(kind: PauseQueueKind): void {
  if (queryClient.getQueryData<PauseMark | null>(pauseRequestKey(kind)) == null) return
  queryClient.setQueryData<PauseMark | null>(pauseRequestKey(kind), null)
}

export function readPauseRequest(kind: PauseQueueKind): PauseMark | null {
  return queryClient.getQueryData<PauseMark | null>(pauseRequestKey(kind)) ?? null
}

/** PAUSE_PENDING_RULE (D-1091): true while the requested pause has not landed. */
export function isPausePending(
  mark: PauseMark | null,
  processor: ObservedProcessor,
  now: number = Date.now(),
): boolean {
  if (mark === null || processor === undefined || processor.state !== 'Processing') return false
  if (mark.jobId !== null) {
    return processor.current_job_id == null || processor.current_job_id === mark.jobId
  }
  return now - (mark.markedAt ?? 0) < PAUSE_UNBOUND_MS
}

function subscribeToMarks(onChange: () => void): () => void {
  return queryClient.getQueryCache().subscribe(() => onChange())
}

/**
 * PAUSE_PENDING_HOOK (D-1091, D-1097). Acts only on an observed list: while
 * `processor` is undefined it returns false and leaves the mark alone.
 */
export function usePausePending(kind: PauseQueueKind, processor: ObservedProcessor): boolean {
  const mark = useSyncExternalStore(subscribeToMarks, () => readPauseRequest(kind))
  const [expiryTick, setExpiryTick] = useState(0)
  const observed = processor !== undefined
  const state = processor?.state
  const jobId = processor?.current_job_id ?? null
  const pending = isPausePending(mark, processor, Date.now())

  useEffect(() => {
    void expiryTick
    if (!observed || state === undefined || mark === null) return
    const now = Date.now()
    if (
      mark.jobId === null &&
      state === 'Processing' &&
      jobId !== null &&
      now - (mark.markedAt ?? 0) < PAUSE_UNBOUND_MS
    ) {
      markPauseRequested(kind, jobId)
      return
    }
    if (!isPausePending(mark, { state, current_job_id: jobId }, now)) clearPauseRequest(kind)
  }, [kind, mark, observed, state, jobId, expiryTick])

  const unboundSince = mark !== null && mark.jobId === null ? (mark.markedAt ?? 0) : null
  useEffect(() => {
    if (unboundSince === null) return
    const timer = setTimeout(
      () => setExpiryTick((tick) => tick + 1),
      Math.max(0, unboundSince + PAUSE_UNBOUND_MS - Date.now()),
    )
    return () => clearTimeout(timer)
  }, [unboundSince])

  return pending
}
