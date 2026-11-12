import { apiFetch } from '../../lib/api'

export type SabrSnapshot = {
  mode: 'inactive' | 'active' | 'checking'
  source?: string | null
  checked_at?: string | null
}

const ACTIVE_TEXT = 'SABR active — quality limited to 360p'

/** `HH:MM:SS` in the app's local clock, or null when `value` doesn't parse. */
function localTime(value: string | null | undefined): string | null {
  if (typeof value !== 'string' || value === '') return null
  const at = new Date(value)
  if (Number.isNaN(at.getTime())) return null
  const pad = (n: number): string => String(n).padStart(2, '0')
  return `${pad(at.getHours())}:${pad(at.getMinutes())}:${pad(at.getSeconds())}`
}

/** SABR_SHOWN: the text the `sabr-status` panel holds for the backend's last result. */
export function sabrResultText(snapshot: SabrSnapshot | undefined): string {
  if (snapshot === undefined) return 'SABR not checked'
  if (snapshot.mode === 'checking') return 'Checking…'
  const time = localTime(snapshot.checked_at)
  if (snapshot.mode === 'active') {
    if (time === null) return ACTIVE_TEXT
    return `${ACTIVE_TEXT} · ${snapshot.source === 'forced' ? 'forced' : 'checked'} ${time}`
  }
  if (time === null) return 'SABR not checked'
  return snapshot.source === 'detected' ? `SABR inactive · checked ${time}` : `SABR inactive · cleared ${time}`
}

export async function fetchSabr(): Promise<SabrSnapshot> {
  return apiFetch<SabrSnapshot>('/downloads/sabr')
}
