export const PRESET_WIRES = ['archival', 'high_quality', 'balanced', 'sharing', 'mobile'] as const
export type PresetWire = (typeof PRESET_WIRES)[number]

export const PRESET_DEFAULT: PresetWire = 'balanced'

export const PRESET_LABELS: Record<PresetWire, string> = {
  archival: 'Archival',
  high_quality: 'High Quality',
  balanced: 'Balanced',
  sharing: 'Sharing',
  mobile: 'Mobile',
}

export const CQ_MIN = 18
export const CQ_MAX = 32
export const CQ_STEP = 1

export const SCALE_HEIGHTS = [0, 1080, 720, 480] as const
export type ScaleHeight = (typeof SCALE_HEIGHTS)[number]

export const AUDIO_MODE_WIRES = ['copy', 'aac_96', 'aac_128', 'aac_192'] as const
export type AudioModeWire = (typeof AUDIO_MODE_WIRES)[number]

export const GPU_PREF_WIRES = ['auto', 'nvidia', 'amd', 'intel', 'software'] as const
export type GpuPrefWire = (typeof GPU_PREF_WIRES)[number]

export type PresetAdvanced = {
  cq: number
  scale_height: ScaleHeight
  audio_mode: AudioModeWire
}

const PRESET_ADVANCED: Record<PresetWire, PresetAdvanced> = {
  archival: { cq: 18, scale_height: 0, audio_mode: 'copy' },
  high_quality: { cq: 22, scale_height: 0, audio_mode: 'aac_128' },
  balanced: { cq: 25, scale_height: 0, audio_mode: 'aac_128' },
  sharing: { cq: 28, scale_height: 0, audio_mode: 'aac_128' },
  mobile: { cq: 30, scale_height: 720, audio_mode: 'aac_96' },
}

export function presetAdvanced(preset: PresetWire): PresetAdvanced {
  return { ...PRESET_ADVANCED[preset] }
}
