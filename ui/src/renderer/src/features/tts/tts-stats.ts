export const DURATION_WPM = 150

export type TextStats = {
  words: number
  sentences: number
  durationSeconds: number
}

export function textStats(text: string, speed: number): TextStats {
  const trimmed = text.trim()
  const words = trimmed.length === 0 ? 0 : trimmed.split(/\s+/).filter(Boolean).length
  const sentences =
    trimmed.length === 0 ? 0 : (trimmed.match(/[.!?]+(?:\s|$)/g) ?? []).length || (trimmed.length > 0 ? 1 : 0)
  const durationSeconds =
    words === 0 || !Number.isFinite(speed) || speed <= 0 ? 0 : (words / (DURATION_WPM * speed)) * 60
  return { words, sentences, durationSeconds }
}
