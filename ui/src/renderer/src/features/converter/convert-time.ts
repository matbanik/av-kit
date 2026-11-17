const CLOCK = /^(\d{1,2}):(\d{2}):(\d{2})(?:\.(\d{1,3}))?$/
const SECONDS = /^\d+(?:\.\d+)?$/

export function parseConvertTime(raw: string): number | null {
  const trimmed = raw.trim()
  if (trimmed.length < 1) {
    return null
  }
  const clock = CLOCK.exec(trimmed)
  if (clock) {
    const hours = Number(clock[1])
    const minutes = Number(clock[2])
    const seconds = Number(clock[3])
    const millisRaw = clock[4] ?? '0'
    const millis = Number(millisRaw.padEnd(3, '0'))
    if (minutes > 59 || seconds > 59 || millis > 999) {
      return null
    }
    return hours * 3_600_000 + minutes * 60_000 + seconds * 1000 + millis
  }
  if (SECONDS.test(trimmed)) {
    return Math.round(Number(trimmed) * 1000)
  }
  return null
}

/** `TIME_MAX_MS` (`services/video_input.py`): 99:59:59.999, the largest time two-digit hours show. */
export const CONVERT_TIME_MAX_MS = 359_999_999

/**
 * CONVERT_TIMECODE (MEU-152, D-969): `HH:MM:SS.mmm` with two-digit hours, the form `format_timecode`
 * (`services/video_input.py:168-173`) writes. `null` for a value that is not a finite, whole,
 * non-negative number of milliseconds no greater than `CONVERT_TIME_MAX_MS`. Every value it
 * formats parses back to itself with `parseConvertTime`.
 */
export function formatConvertTime(ms: number): string | null {
  if (!Number.isInteger(ms) || ms < 0 || ms > CONVERT_TIME_MAX_MS) {
    return null
  }
  const hours = Math.floor(ms / 3_600_000)
  const minutes = Math.floor((ms % 3_600_000) / 60_000)
  const seconds = Math.floor((ms % 60_000) / 1000)
  const millis = ms % 1000
  const two = (value: number): string => String(value).padStart(2, '0')
  return `${two(hours)}:${two(minutes)}:${two(seconds)}.${String(millis).padStart(3, '0')}`
}
