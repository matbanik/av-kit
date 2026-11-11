import { z } from 'zod'

import { appendStdoutLog, getPublishedBackendReady } from './ipc'
import { notifyUser, type Notice } from './notify-user'

export const TIMESTAMP_FORMAT = 'yyyy-MM-dd_HH-mm-ss'
export const POLL_REQUEST_MS = 500

const completeBodySchema = z.object({ path: z.string().min(1) }).strict()
const cancelBodySchema = z.object({}).strict()

export type RegisterSource = 'hotkey' | 'gui'

function pad2(value: number): string {
  return String(value).padStart(2, '0')
}

function errorMessage(err: unknown): string {
  return err instanceof Error ? err.message : String(err)
}

export function formatLocalTimestamp(now = new Date()): string {
  return `${now.getFullYear()}-${pad2(now.getMonth() + 1)}-${pad2(now.getDate())}_${pad2(now.getHours())}-${pad2(now.getMinutes())}-${pad2(now.getSeconds())}`
}

export function registerFileName(now = new Date()): string {
  return `${formatLocalTimestamp(now)}.png`
}

/** A backend answer that was reached but refused, carrying the HTTP status the caller must branch on. */
export class CaptureApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'CaptureApiError'
    this.status = status
  }
}

async function authorizedFetch(path: string, init: RequestInit): Promise<Response> {
  const ready = getPublishedBackendReady()
  if (ready === null) {
    throw new Error('backend not ready')
  }
  const headers = new Headers(init.headers)
  headers.set('Authorization', `Bearer ${ready.token}`)
  if (!headers.has('Content-Type') && init.body !== undefined) {
    headers.set('Content-Type', 'application/json')
  }
  return fetch(`${ready.apiBase}${path}`, { ...init, headers })
}

export async function registerCapturePng(path: string, source: RegisterSource): Promise<void> {
  const res = await authorizedFetch('/captures', {
    method: 'POST',
    body: JSON.stringify({ mode: 'register', path, source }),
  })
  if (!res.ok) {
    throw new CaptureApiError(`register failed ${res.status}`, res.status)
  }
}

export async function completeCaptureRequest(id: string, path: string): Promise<void> {
  const body = completeBodySchema.parse({ path })
  const res = await authorizedFetch(`/captures/requests/${id}/complete`, {
    method: 'POST',
    body: JSON.stringify(body),
  })
  if (res.status === 404) {
    throw new CaptureApiError('404 capture request not found', 404)
  }
  if (!res.ok) {
    throw new CaptureApiError(`complete failed ${res.status}`, res.status)
  }
}

export async function cancelCaptureRequest(id: string, extra: unknown = {}): Promise<void> {
  const body = cancelBodySchema.parse(extra)
  const res = await authorizedFetch(`/captures/requests/${id}/cancel`, {
    method: 'POST',
    body: JSON.stringify(body),
  })
  if (res.status === 404) {
    throw new CaptureApiError('404 capture request not found', 404)
  }
  if (!res.ok) {
    throw new CaptureApiError(`cancel failed ${res.status}`, res.status)
  }
}

export type PendingRequest = { id: string; status: string }

/**
 * A poll either produced a listing or could not reach the backend. Collapsing the second case to
 * an empty array is what let a backend restart look like "every request disappeared", which in
 * turn cancelled requests whose PNG was already on disk — so the two are kept apart by type.
 */
export type PollResult =
  | { kind: 'ok'; rows: PendingRequest[] }
  | { kind: 'unavailable'; reason: string }

function capturePollLog(err: unknown): void {
  appendStdoutLog(`[Capture] pending-request poll failed: ${errorMessage(err)}`)
}

// --- completion journal -------------------------------------------------------------------
//
// A capture is published to the inbox before the request is completed, so the window between the
// two is where a request can be lost. The journal remembers "this id owes a completion for this
// file" so a failed complete is retried instead of being turned into a cancel. It is deliberately
// in-memory only: see known issue CAPTURE-JOURNAL-VOLATILE.

export type JournalEntry = {
  requestId: string
  path: string
  attempts: number
  lastAttempt: number
}

/** Retry spacing after consecutive failures; the last value repeats. */
export const COMPLETION_BACKOFF_MS = [1_000, 2_000, 4_000, 8_000, 15_000] as const

const journal = new Map<string, JournalEntry>()

export function journalCompletion(requestId: string, path: string, at: number): JournalEntry {
  const entry: JournalEntry = { requestId, path, attempts: 0, lastAttempt: at }
  journal.set(requestId, entry)
  return entry
}

export function getJournalEntry(requestId: string): JournalEntry | undefined {
  return journal.get(requestId)
}

export function journalSize(): number {
  return journal.size
}

export function clearCompletionJournal(): void {
  journal.clear()
}

function backoffFor(attempts: number): number {
  const index = Math.min(Math.max(attempts, 1), COMPLETION_BACKOFF_MS.length) - 1
  return COMPLETION_BACKOFF_MS[index] ?? COMPLETION_BACKOFF_MS[0]
}

export async function listCaptureRequests(): Promise<PollResult> {
  if (getPublishedBackendReady() === null) {
    return { kind: 'unavailable', reason: 'backend not ready' }
  }
  try {
    // While something is journalled the poll must be able to see its terminal status, which the
    // pending-only filter would hide.
    const path = journal.size > 0 ? '/captures/requests' : '/captures/requests?status=pending'
    const res = await authorizedFetch(path, { method: 'GET' })
    if (!res.ok) {
      return { kind: 'unavailable', reason: `request listing failed ${res.status}` }
    }
    const payload = (await res.json()) as { items?: PendingRequest[] }
    return { kind: 'ok', rows: payload.items ?? [] }
  } catch (err: unknown) {
    capturePollLog(err)
    return { kind: 'unavailable', reason: errorMessage(err) }
  }
}

export async function listPendingRequests(): Promise<PendingRequest[]> {
  const result = await listCaptureRequests()
  return result.kind === 'ok' ? result.rows : []
}

export async function finalizeCapturedPng(
  dest: string,
  source: RegisterSource,
  register: boolean,
  notify: () => void,
  onRegisterFailure?: (message: string) => void,
  logFailure = true,
): Promise<void> {
  if (register) {
    try {
      await registerCapturePng(dest, source)
    } catch (err: unknown) {
      const message = errorMessage(err)
      if (logFailure) {
        appendStdoutLog(`[Capture] register failed: ${message}`)
      }
      onRegisterFailure?.(message)
    }
  }
  notify()
}

// --- interactive request lifecycle --------------------------------------------------------

export type InteractiveDeps = {
  /** Opens the picker for `row` and resolves the published inbox path, or `null` if nothing was captured. */
  capture: (row: PendingRequest) => Promise<string | null>
  /** When it returns false the tick still drains the journal but does not open the picker. */
  ready?: () => boolean
  complete?: (id: string, path: string) => Promise<void>
  cancel?: (id: string) => Promise<void>
  relist?: () => Promise<PollResult>
  notify?: (notice: Notice) => void
  log?: (line: string) => void
  now?: () => number
}

type TickContext = {
  complete: (id: string, path: string) => Promise<void>
  cancel: (id: string) => Promise<void>
  relist: () => Promise<PollResult>
  notify: (notice: Notice) => void
  log: (line: string) => void
  now: () => number
}

const STATUS_COMPLETED = 'completed'
const STATUS_EXPIRED = 'expired'
const STATUS_CANCELLED = 'cancelled'
const STATUS_PENDING = 'pending'

function terminalNotice(entry: JournalEntry, ctx: TickContext, reason: string): void {
  ctx.notify({
    title: 'Capture kept, request closed',
    body: `The request closed (${reason}) before av-kit could record the capture.`,
    path: entry.path,
  })
}

async function reconcileConflict(entry: JournalEntry, ctx: TickContext): Promise<void> {
  const result = await ctx.relist()
  if (result.kind !== 'ok') {
    // The backend refused the completion and is now unreachable; keep the entry so a later tick
    // can find out which way the row actually went.
    entry.attempts += 1
    return
  }
  const row = result.rows.find((candidate) => candidate.id === entry.requestId)
  const status = row?.status.toLowerCase()
  if (status === STATUS_COMPLETED) {
    journal.delete(entry.requestId)
    return
  }
  if (row === undefined || status === STATUS_EXPIRED || status === STATUS_CANCELLED) {
    journal.delete(entry.requestId)
    terminalNotice(entry, ctx, status ?? 'no longer listed')
    return
  }
  entry.attempts += 1
}

async function attemptCompletion(entry: JournalEntry, ctx: TickContext): Promise<void> {
  entry.lastAttempt = ctx.now()
  try {
    await ctx.complete(entry.requestId, entry.path)
    journal.delete(entry.requestId)
  } catch (err: unknown) {
    if (err instanceof CaptureApiError && err.status === 409) {
      await reconcileConflict(entry, ctx)
      return
    }
    entry.attempts += 1
    ctx.log(`[Capture] completion pending for ${entry.path}: ${errorMessage(err)}`)
  }
}

async function drainJournalEntry(
  entry: JournalEntry,
  rows: PendingRequest[],
  ctx: TickContext,
): Promise<void> {
  const row = rows.find((candidate) => candidate.id === entry.requestId)
  if (row === undefined) {
    journal.delete(entry.requestId)
    terminalNotice(entry, ctx, 'no longer listed')
    return
  }
  const status = row.status.toLowerCase()
  if (status === STATUS_COMPLETED) {
    journal.delete(entry.requestId)
    return
  }
  if (status === STATUS_EXPIRED || status === STATUS_CANCELLED) {
    journal.delete(entry.requestId)
    terminalNotice(entry, ctx, status)
    return
  }
  if (status !== STATUS_PENDING) {
    return
  }
  if (ctx.now() < entry.lastAttempt + backoffFor(entry.attempts)) {
    return
  }
  await attemptCompletion(entry, ctx)
}

async function cancelQuietly(id: string, ctx: TickContext): Promise<void> {
  try {
    await ctx.cancel(id)
  } catch (err: unknown) {
    ctx.log(`[Capture] cancel failed for ${id}: ${errorMessage(err)}`)
  }
}

/**
 * One pass of the interactive request loop.
 *
 * Order matters: outstanding completions are settled first, and only then is a *new* request
 * allowed to open the picker. An unreachable backend does nothing at all — no capture, no cancel —
 * because the one thing worse than a late completion is cancelling a request whose file already
 * exists.
 */
export async function runInteractiveTick(poll: PollResult, deps: InteractiveDeps): Promise<void> {
  if (poll.kind !== 'ok') {
    return
  }
  const ctx: TickContext = {
    complete: deps.complete ?? completeCaptureRequest,
    cancel: deps.cancel ?? ((id: string) => cancelCaptureRequest(id)),
    relist: deps.relist ?? listCaptureRequests,
    notify: deps.notify ?? notifyUser,
    log: deps.log ?? ((line: string) => void appendStdoutLog(line)),
    now: deps.now ?? Date.now,
  }

  // Snapshotted before the drain so a completion that finishes during this tick cannot make its
  // own row look like a fresh request to capture.
  const alreadyJournalled = new Set(journal.keys())

  for (const entry of [...journal.values()]) {
    await drainJournalEntry(entry, poll.rows, ctx)
  }

  if (deps.ready !== undefined && !deps.ready()) {
    // A hotkey or tray capture already owns the screen; the request waits for the next tick.
    return
  }

  const next = poll.rows.find(
    (row) => row.status.toLowerCase() === STATUS_PENDING && !alreadyJournalled.has(row.id),
  )
  if (next === undefined) {
    return
  }

  let published: string | null = null
  try {
    published = await deps.capture(next)
  } catch (err: unknown) {
    ctx.log(`[Capture] interactive capture failed for ${next.id}: ${errorMessage(err)}`)
    await cancelQuietly(next.id, ctx)
    return
  }
  if (published === null) {
    await cancelQuietly(next.id, ctx)
    return
  }

  const entry = journalCompletion(next.id, published, ctx.now())
  await attemptCompletion(entry, ctx)
}

let pollTimer: ReturnType<typeof setInterval> | null = null
let requestLoopTimer: ReturnType<typeof setInterval> | null = null
let tickInFlight = false

export function startInteractivePoll(onPending: (row: PendingRequest) => void): void {
  if (pollTimer !== null) {
    return
  }
  pollTimer = setInterval(() => {
    void listPendingRequests()
      .then((rows) => {
        const first = rows[0]
        if (first !== undefined) {
          onPending(first)
        }
      })
      .catch((err: unknown) => {
        capturePollLog(err)
      })
  }, POLL_REQUEST_MS)
}

export function stopInteractivePoll(): void {
  if (pollTimer === null) {
    return
  }
  clearInterval(pollTimer)
  pollTimer = null
}

/**
 * Drives {@link runInteractiveTick} every {@link POLL_REQUEST_MS}. Ticks never overlap: the picker
 * is modal to the user, and a second tick while one is open would fight it for the same request.
 */
export function startInteractiveRequestLoop(deps: InteractiveDeps): void {
  if (requestLoopTimer !== null) {
    return
  }
  requestLoopTimer = setInterval(() => {
    if (tickInFlight) {
      return
    }
    tickInFlight = true
    void listCaptureRequests()
      .then((poll) => runInteractiveTick(poll, deps))
      .catch((err: unknown) => {
        capturePollLog(err)
      })
      .finally(() => {
        tickInFlight = false
      })
  }, POLL_REQUEST_MS)
}

export function stopInteractiveRequestLoop(): void {
  if (requestLoopTimer === null) {
    return
  }
  clearInterval(requestLoopTimer)
  requestLoopTimer = null
  tickInFlight = false
}
