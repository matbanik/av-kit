/**
 * `RUN_BAR_SLOT` — what the right side of the TTS run bar shows.
 *
 * Exactly one of three children is mounted, in precedence order: the error
 * (`RUN_BAR_ERROR`, so a failure is never hidden behind progress), then segment progress while
 * the job is active (`RUN_ACTIVE`, i.e. the existing cancel predicate), then the
 * last output — which keeps its muted "No output yet" copy while idle (TT5).
 */
import { cancelEnabled } from './tts-controls'

export type RunBarSlot = 'error' | 'progress' | 'output'

type RunBarInput = { error: string | null; status: string; jobError?: string | null }

/**
 * `RUN_BAR_ERROR`: the client error if non-empty, else the job's `error_message` when the
 * job is `Failed` and the message is non-empty, else null.
 */
export function runBarError(input: RunBarInput): string | null {
  if (input.error !== null && input.error.length > 0) {
    return input.error
  }
  if (input.status === 'Failed' && typeof input.jobError === 'string' && input.jobError.length > 0) {
    return input.jobError
  }
  return null
}

/**
 * Resolve the run-bar slot.
 *
 * @param input - The client error (or null), the job status and the job's error_message.
 * @returns Which single slot child to render; `'error'` exactly when `RUN_BAR_ERROR` is set.
 */
export function resolveRunBarSlot(input: RunBarInput): RunBarSlot {
  if (runBarError(input) !== null) {
    return 'error'
  }
  if (cancelEnabled({ status: input.status })) {
    return 'progress'
  }
  return 'output'
}
