import { hashKey, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect } from 'react'

import { apiFetch } from '../../lib/api'
import { QUERY_HEALTH_DEPENDENCIES } from './tts-assets'
import type { VoiceOut } from './tts-voices'

export const QUERY_JOB_KEY = ['tts', 'job'] as const
export const QUERY_VOICES_KEY = ['tts', 'voices'] as const
export const QUERY_MODELS_AVAILABLE = ['models', 'available'] as const
export const QUERY_MODELS_STATUS = ['models', 'status'] as const
export const QUERY_DOWNLOAD_RUNTIME = ['models', 'download-runtime'] as const
export const QUERY_SETTINGS_TTS = ['settings', 'tts'] as const

export type TtsJobOut = {
  id: string
  source_kind: string
  source_path: string | null
  text_hash: string
  text_preview: string
  voice: string
  speed: number
  format: string
  status: string
  output_path: string | null
  segments_total: number
  segments_done: number
  error_message: string | null
  created_at: string
}

export type ModelStatus = {
  is_loaded: boolean
  variant_id?: string | null
  name?: string
  device?: string | null
  memory_bytes?: number | null
}

export type DownloadRuntime = {
  state: string
  variant_id?: string | null
  asset?: string | null
  fraction?: number | null
  message?: string | null
  error_message?: string | null
}

export type CatalogItem = {
  id: string
  name: string
  format: string
  precision: string
  size_bytes: number
  path: string | null
  is_downloaded: boolean
  /** Devices this row can load on (wire names, `auto` first); absent means `auto` and `cpu`. */
  devices?: string[]
}

type PollQuery = {
  state: { data?: { status?: string } }
  runtime?: { state?: string }
}

export function ttsPollInterval(query: PollQuery): number {
  const status = query.state.data?.status
  if (status === 'Generating') {
    return 1000
  }
  if (query.runtime?.state === 'Downloading') {
    return 1000
  }
  return 5000
}

export function useTtsJob(jobId: string | null) {
  return useQuery({
    queryKey: [...QUERY_JOB_KEY, jobId],
    queryFn: async () => apiFetch<TtsJobOut>(`/tts/${jobId}`),
    enabled: jobId !== null && jobId.length > 0,
    refetchInterval: (query) => ttsPollInterval(query),
  })
}

export function useVoices() {
  return useQuery({
    queryKey: QUERY_VOICES_KEY,
    // Typed rows: MEU-74 adds the boolean `available`, which a string record cannot hold.
    queryFn: async () => apiFetch<{ items: VoiceOut[] }>('/tts/voices'),
  })
}

export function useModelsAvailable() {
  return useQuery({
    queryKey: QUERY_MODELS_AVAILABLE,
    queryFn: async () => apiFetch<{ items: CatalogItem[] }>('/models/available'),
  })
}

export function useModelStatus() {
  return useQuery({
    queryKey: QUERY_MODELS_STATUS,
    queryFn: async () => apiFetch<ModelStatus>('/models/status'),
  })
}

export function useDownloadRuntime() {
  return useQuery({
    queryKey: QUERY_DOWNLOAD_RUNTIME,
    queryFn: async () => apiFetch<DownloadRuntime>('/models/download-runtime'),
    refetchInterval: (query) =>
      query.state.data?.state === 'Downloading' ? 1000 : 5000,
  })
}

/**
 * Spec 03 "Settings refresh" (AC-73.10): invalidate `GET /health/dependencies` once when the
 * model download runtime leaves `Downloading`, so the asset rows show the settled state. A
 * steady state never refetches.
 *
 * The transition is read from the query cache's update stream, not from rendered data: two
 * runtime results that land before React renders would otherwise hide `Downloading`.
 */
export function useRefreshDependenciesOnSettle(): void {
  const queryClient = useQueryClient()
  useDownloadRuntime()
  useEffect(() => {
    const runtimeHash = hashKey(QUERY_DOWNLOAD_RUNTIME)
    const stateOf = (data: unknown) => (data as DownloadRuntime | undefined)?.state
    let previous = stateOf(queryClient.getQueryData(QUERY_DOWNLOAD_RUNTIME))
    return queryClient.getQueryCache().subscribe((event) => {
      if (event.type !== 'updated' || event.query.queryHash !== runtimeHash) return
      const state = stateOf(event.query.state.data)
      if (state === previous) return
      const settled = previous === 'Downloading'
      previous = state
      if (settled) void queryClient.invalidateQueries({ queryKey: QUERY_HEALTH_DEPENDENCIES })
    })
  }, [queryClient])
}

/** `GET /health/dependencies`, shared with the Settings Dependencies card (same key). */
export function useTtsDependencies() {
  return useQuery({
    queryKey: QUERY_HEALTH_DEPENDENCIES,
    queryFn: async () => apiFetch<Record<string, unknown>>('/health/dependencies'),
  })
}

export function useTtsSettings() {
  return useQuery({
    queryKey: QUERY_SETTINGS_TTS,
    queryFn: async () =>
      apiFetch<{
        input_text?: string
        voice?: string
        speed?: number
        output_format?: string
        output_path?: string
        device?: string
        chunk_max_chars?: number
      }>('/settings/tts'),
  })
}
