import { useQuery, useQueryClient, type QueryClient } from '@tanstack/react-query'
import { useCallback, useRef } from 'react'

import { ApiError, apiFetch } from '../../lib/api'
import { applyDocumentTheme } from '../../lib/theme'
import { QUERY_HEALTH_DEPENDENCIES } from '../tts/tts-assets'
import {
  parseSettingsPut,
  SettingsValidationError,
  type AppPut,
  type DownloaderPut,
  type TranscriptPut,
  type TtsPut,
  type UiPut,
} from './settings-schemas'
import { SETTINGS_NAMESPACE_PATHS, type SettingsNamespace } from './settings-paths'

export const DEBOUNCE_MS = 300

export const SETTINGS_ERROR_EVENT = 'av-kit:settings:error'

export type DebouncedNamespace = Exclude<SettingsNamespace, 'converter' | 'capture'>

export function reportSettingsError(namespace: SettingsNamespace | 'general', message: string): void {
  window.dispatchEvent(
    new CustomEvent(SETTINGS_ERROR_EVENT, {
      detail: { namespace, message },
    }),
  )
}

/** Debounced leaf PUT to `/settings/` namespaces via SETTINGS_NAMESPACE_PATHS. */

type NamespacePayload = {
  downloader: DownloaderPut & Record<string, unknown>
  transcript: TranscriptPut & Record<string, unknown>
  tts: TtsPut & Record<string, unknown>
  app: AppPut & Record<string, unknown>
  ui: UiPut & Record<string, unknown>
}

const QUERY_KEYS = {
  downloader: ['settings', 'downloader'] as const,
  transcript: ['settings', 'transcript'] as const,
  tts: ['settings', 'tts'] as const,
  app: ['settings', 'app'] as const,
  ui: ['settings', 'ui'] as const,
}

/**
 * One leaf PUT (APPEARANCE): parse, `PUT`, apply a saved theme, refresh the
 * namespace, and refresh Dependencies after an ffmpeg path change.
 */
export async function putSettingsNamespace(
  client: QueryClient,
  namespace: DebouncedNamespace,
  patch: Record<string, unknown>,
): Promise<void> {
  const body = parseSettingsPut(namespace, patch)
  await apiFetch(SETTINGS_NAMESPACE_PATHS[namespace], {
    method: 'PUT',
    body: JSON.stringify(body),
  })
  if (namespace === 'ui' && 'theme' in body) {
    const nextTheme = body.theme
    if (nextTheme === 'dark' || nextTheme === 'light') {
      applyDocumentTheme(nextTheme)
    }
  }
  await client.invalidateQueries({ queryKey: QUERY_KEYS[namespace] })
  // DEPS_REFRESH: a new ffmpeg or Deno path changes what the Dependencies card resolves.
  if (namespace === 'downloader' && ('ffmpeg_path' in body || 'deno_path' in body)) {
    await client.invalidateQueries({ queryKey: QUERY_HEALTH_DEPENDENCIES })
  }
}

export function useSettingsNamespace<N extends DebouncedNamespace>(namespace: N) {
  return useQuery({
    queryKey: QUERY_KEYS[namespace],
    queryFn: async () => apiFetch<NamespacePayload[N]>(SETTINGS_NAMESPACE_PATHS[namespace]),
  })
}

export function useSettingsPage() {
  const queryClient = useQueryClient()
  const timers = useRef<Partial<Record<DebouncedNamespace, ReturnType<typeof setTimeout>>>>({})
  const pending = useRef<Partial<Record<DebouncedNamespace, Record<string, unknown>>>>({})

  const downloaderQuery = useSettingsNamespace('downloader')
  const transcriptQuery = useSettingsNamespace('transcript')
  const ttsQuery = useSettingsNamespace('tts')
  const appQuery = useSettingsNamespace('app')
  const uiQuery = useSettingsNamespace('ui')

  const flushPut = useCallback(
    async (namespace: DebouncedNamespace, patch: Record<string, unknown>) => {
      await putSettingsNamespace(queryClient, namespace, patch)
    },
    [queryClient],
  )

  const schedulePut = useCallback(
    (namespace: DebouncedNamespace, patch: Record<string, unknown>) => {
      const current = queryClient.getQueryData<Record<string, unknown>>(QUERY_KEYS[namespace]) ?? {}
      const filtered: Record<string, unknown> = {}
      for (const [key, value] of Object.entries(patch)) {
        if (value === undefined) {
          continue
        }
        if (typeof value === 'string' && value.trim() === '') {
          continue
        }
        if (Object.is(current[key], value)) {
          continue
        }
        filtered[key] = value
      }
      if (Object.keys(filtered).length === 0) {
        return
      }
      pending.current[namespace] = { ...(pending.current[namespace] ?? {}), ...filtered }
      const existing = timers.current[namespace]
      if (existing !== undefined) {
        clearTimeout(existing)
      }
      timers.current[namespace] = setTimeout(() => {
        const body = pending.current[namespace]
        pending.current[namespace] = undefined
        timers.current[namespace] = undefined
        if (body === undefined || Object.keys(body).length === 0) {
          return
        }
        void flushPut(namespace, body).catch((caught) => {
          if (caught instanceof SettingsValidationError || caught instanceof ApiError) {
            reportSettingsError(namespace, caught.message)
          }
        })
      }, DEBOUNCE_MS)
    },
    [flushPut, queryClient],
  )

  const putNow = useCallback(
    async (namespace: DebouncedNamespace, patch: Record<string, unknown>) => {
      const existing = timers.current[namespace]
      if (existing !== undefined) {
        clearTimeout(existing)
        timers.current[namespace] = undefined
      }
      pending.current[namespace] = undefined
      try {
        await flushPut(namespace, patch)
      } catch (caught) {
        if (caught instanceof SettingsValidationError || caught instanceof ApiError) {
          reportSettingsError(namespace, caught.message)
          return
        }
        throw caught
      }
    },
    [flushPut],
  )

  const runSettingsAction = useCallback(
    async (namespace: SettingsNamespace | 'general', work: () => Promise<void>) => {
      try {
        await work()
      } catch (caught) {
        if (caught instanceof SettingsValidationError || caught instanceof ApiError) {
          reportSettingsError(namespace, caught.message)
          return
        }
        if (caught instanceof Error) {
          reportSettingsError(namespace, caught.message)
          return
        }
        reportSettingsError(namespace, String(caught))
      }
    },
    [],
  )

  return {
    downloaderQuery,
    transcriptQuery,
    ttsQuery,
    appQuery,
    uiQuery,
    schedulePut,
    putNow,
    runSettingsAction,
    reportSettingsError,
  }
}
