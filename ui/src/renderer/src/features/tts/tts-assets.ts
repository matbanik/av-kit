/**
 * MEU-62 TTS runtime assets on the GUI: the Kokoro vocab/config file, the managed spaCy
 * English model and (MEU-73) the Kokoro v1.0 voice packs. Rows come from `GET /health/dependencies`; Get posts
 * `POST /models/download {asset}`. No IPC is involved.
 */
import type { StatusChipTone } from '../../components/ui/StatusChip'

/** Wire values of the backend `TtsAsset` enum (`TTS_ASSETS`), in declaration order. */
export const TTS_ASSET_WIRES = ['tts_onnx_vocab', 'tts_spacy_model', 'tts_voice_packs'] as const
export type TtsAssetWire = (typeof TTS_ASSET_WIRES)[number]

/** Wire values of the backend `AssetState` enum (`ASSET_STATES`). */
export type AssetStateWire = 'ready' | 'missing' | 'downloading'

export type TtsAssetRow = { available: boolean; version: string | null; state: AssetStateWire }

export const QUERY_HEALTH_DEPENDENCIES = ['health', 'dependencies'] as const

export const TTS_ASSET_LABELS: Record<TtsAssetWire, string> = {
  tts_onnx_vocab: 'Kokoro vocab',
  tts_spacy_model: 'spaCy English model',
  tts_voice_packs: 'Voice packs',
}

const CHIP: Record<AssetStateWire, { label: string; tone: StatusChipTone }> = {
  ready: { label: 'Ready', tone: 'success' },
  missing: { label: 'Missing', tone: 'warning' },
  downloading: { label: 'Downloading', tone: 'info' },
}

/** Chip for one asset state; an unrecognized wire value fails closed to "Missing". */
export function assetChip(state: string): { label: string; tone: StatusChipTone } {
  return state in CHIP ? CHIP[state as AssetStateWire] : CHIP.missing
}

/**
 * The asset rows present in a dependencies payload, in `TTS_ASSET_WIRES` order. A backend
 * without the rows (an older build) yields none, so nothing is fabricated.
 */
export function presentAssetRows(deps: unknown): Array<[TtsAssetWire, TtsAssetRow]> {
  if (deps === null || typeof deps !== 'object') return []
  const record = deps as Record<string, unknown>
  const rows: Array<[TtsAssetWire, TtsAssetRow]> = []
  for (const wire of TTS_ASSET_WIRES) {
    const row = record[wire]
    if (row !== null && typeof row === 'object' && typeof (row as TtsAssetRow).state === 'string') {
      rows.push([wire, row as TtsAssetRow])
    }
  }
  return rows
}

/** Get is offered only for a missing asset, and is disabled while it downloads. */
export function assetGetVisible(state: string): boolean {
  return state === 'missing' || state === 'downloading'
}
