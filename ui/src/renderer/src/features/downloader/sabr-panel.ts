import { apiFetch } from '../../lib/api'

export type SabrSnapshot = {
  mode: 'inactive' | 'active' | 'checking'
  source?: string | null
  checked_at?: string | null
}

export async function fetchSabr(): Promise<SabrSnapshot> {
  return apiFetch<SabrSnapshot>('/downloads/sabr')
}
