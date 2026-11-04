/**
 * Strict parser for the `{ items, processor? }` queue envelope.
 *
 * Every queue endpoint returns an object wrapper, never a bare array. Accepting
 * a bare array (or an unrecognised wrapper key) silently hides a backend
 * contract break until a card renders empty, so this parser rejects both and
 * raises the same `ApiError` shape the rest of the renderer already handles.
 */
import { z } from 'zod'

import { ApiError } from '../api'

/** Queue-level processor state reported alongside the items. */
export const PROCESSOR_STATES = ['Idle', 'Processing', 'Paused'] as const

/** One of the queue-level processor states. */
export type ProcessorState = (typeof PROCESSOR_STATES)[number]

const envelopeSchema = z
  .object({
    items: z.array(z.unknown()),
    processor: z.enum(PROCESSOR_STATES).optional(),
  })
  .strict()

/** The parsed envelope: raw items plus the optional processor state. */
export type QueueEnvelope = {
  items: unknown[]
  processor?: ProcessorState
}

/**
 * Parse a queue list response.
 *
 * @param raw - The decoded JSON body, unvalidated.
 * @returns The envelope's items and processor state.
 * @throws ApiError - 422 `ENVELOPE_INVALID` when the body is a bare array, is
 *         missing `items`, or carries a key the envelope does not define.
 */
export function parseQueueEnvelope(raw: unknown): QueueEnvelope {
  const result = envelopeSchema.safeParse(raw)
  if (!result.success) {
    const issues = result.error.issues.map((issue) => ({
      path: issue.path.join('.'),
      message: issue.message,
    }))
    const summary = issues.map((issue) => `${issue.path || '<root>'}: ${issue.message}`).join('; ')
    throw new ApiError(422, 'ENVELOPE_INVALID', `queue envelope is invalid — ${summary}`, {
      issues,
    })
  }
  const parsed = result.data
  return parsed.processor === undefined
    ? { items: [...parsed.items] }
    : { items: [...parsed.items], processor: parsed.processor }
}
