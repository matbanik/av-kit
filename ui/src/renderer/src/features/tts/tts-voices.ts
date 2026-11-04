/** Backend `VoiceUnavailableReason` wire values (MEU-74 `VOICE_REASON`). */
export type VoiceUnavailableReason = 'espeak_missing' | 'language_unsupported'

export type VoiceOut = {
  voice_id: string
  language: string
  gender: string
  style_description: string
  /** MEU-74. Absent on an older backend, which means available. */
  available?: boolean
  reason?: VoiceUnavailableReason | null
}

/** The UI owns the wording for each `VOICE_REASON` wire value. */
export const VOICE_REASON_TEXT: Record<VoiceUnavailableReason, string> = {
  espeak_missing: 'Needs eSpeak NG',
  language_unsupported: 'Language not supported yet',
}

/** Why the voice cannot generate now, or null when it can (absent fields mean available). */
export function voiceUnavailableText(voice: VoiceOut): string | null {
  if (voice.available !== false) {
    return null
  }
  return voice.reason ? VOICE_REASON_TEXT[voice.reason] : 'Unavailable'
}

export type VoiceGroup = { language: string; voices: VoiceOut[] }

export function uniqueLanguages(items: VoiceOut[]): string[] {
  return [...new Set(items.map((item) => item.language))].sort()
}

export function filterVoices(items: VoiceOut[], language: string | null): VoiceOut[] {
  if (language === null || language.length === 0) {
    return items
  }
  return items.filter((item) => item.language === language)
}

/**
 * Voices matching the combobox query AND the language filter. The query is trimmed and
 * matched case-insensitively as a substring of the voice id, its description (the
 * voice's display name) or its language.
 */
export function matchVoices(items: VoiceOut[], query: string, language: string | null): VoiceOut[] {
  const needle = query.trim().toLowerCase()
  const pool = filterVoices(items, language)
  if (needle.length === 0) {
    return pool
  }
  return pool.filter((item) =>
    [item.voice_id, item.style_description, item.language].some((field) => field.toLowerCase().includes(needle)),
  )
}

/** Group voices by language, in catalog order (the order the backend lists them). */
export function groupVoices(items: VoiceOut[]): VoiceGroup[] {
  const groups = new Map<string, VoiceOut[]>()
  for (const item of items) {
    const bucket = groups.get(item.language)
    if (bucket) {
      bucket.push(item)
    } else {
      groups.set(item.language, [item])
    }
  }
  return Array.from(groups, ([language, voices]) => ({ language, voices }))
}
