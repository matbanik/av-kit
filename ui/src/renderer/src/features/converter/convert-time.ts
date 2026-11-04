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
