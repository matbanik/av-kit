/**
 * Per-feature status configuration (STATUS_CONFIG_POLICY).
 *
 * The four queues do not share a status set — the downloader has transfer-only
 * states the converter never reaches, and the converter has none of them. A
 * single merged union would let a card render a status its own backend can never
 * report, so each feature's config is keyed by *that feature's* `JOB_STATUSES`
 * constant, imported rather than restated. Adding a status to a controls module
 * therefore extends its config automatically, and only its config.
 */
import { JOB_STATUSES as CONVERT_STATUSES } from '../../features/converter/convert-controls'
import { JOB_STATUSES as DOWNLOAD_STATUSES } from '../../features/downloader/download-controls'
import { JOB_STATUSES as TRANSCRIPT_STATUSES } from '../../features/transcript/transcript-controls'
import { JOB_STATUSES as TTS_STATUSES } from '../../features/tts/tts-controls'
import { resolveStatusPill, type StatusPill } from './status-tokens'

/** How one status of one feature renders. */
export type QueueStatusEntry = {
  /** The status name, echoed so an entry is self-describing when destructured. */
  readonly status: string
  /** Pill contract resolved from the canonical token table. */
  readonly pill: StatusPill
}

/** Config for one feature: every status it can report, in its declared order. */
export type FeatureStatusConfig<T extends readonly string[]> = {
  readonly [K in T[number]]: QueueStatusEntry
}

/**
 * Build a feature's status config from its own status tuple.
 *
 * @param statuses - The feature's `JOB_STATUSES` constant.
 * @returns A config keyed by those statuses, in the same order.
 */
function buildStatusConfig<T extends readonly string[]>(statuses: T): FeatureStatusConfig<T> {
  return Object.fromEntries(
    statuses.map((status) => [status, { status, pill: resolveStatusPill(status) }]),
  ) as FeatureStatusConfig<T>
}

/** Status configs for all four queue features, keyed by feature slug. */
export const QUEUE_STATUS_CONFIGS = {
  download: buildStatusConfig(DOWNLOAD_STATUSES),
  convert: buildStatusConfig(CONVERT_STATUSES),
  transcript: buildStatusConfig(TRANSCRIPT_STATUSES),
  tts: buildStatusConfig(TTS_STATUSES),
} as const

/** A queue feature slug. */
export type QueueFeature = keyof typeof QUEUE_STATUS_CONFIGS
