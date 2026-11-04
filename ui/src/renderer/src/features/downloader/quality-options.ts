export const QUALITY_WIRE = [
  'best',
  '2160p',
  '1440p',
  '1080p',
  '720p',
  '480p',
  '360p',
  '240p',
  '144p',
  'lowest',
] as const

export const AUDIO_WIRE = [
  'default',
  'best',
  'lowest',
  'low_webm',
  'medium_webm',
  'standard_webm',
  'standard_m4a',
  'standard_mp3',
  'high_m4a',
] as const

export type QualityWire = (typeof QUALITY_WIRE)[number]
export type AudioWire = (typeof AUDIO_WIRE)[number]

export const QUALITY_DEFAULT: QualityWire = '1080p'
export const AUDIO_DEFAULT: AudioWire = 'default'

export function qualityOptions(sabrActive: boolean): readonly QualityWire[] {
  return sabrActive ? (['360p'] as const) : QUALITY_WIRE
}

export function audioOptions(sabrActive: boolean): readonly AudioWire[] {
  return sabrActive ? (['standard_mp3', 'high_m4a'] as const) : AUDIO_WIRE
}

export const SELECT_THEME_STYLE = {
  backgroundColor: 'var(--color-bg-elevated)',
  color: 'var(--color-fg)',
  borderColor: 'var(--color-border)',
} as const
