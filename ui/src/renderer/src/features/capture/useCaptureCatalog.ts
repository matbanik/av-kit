import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect } from 'react'

import { apiFetch } from '../../lib/api'

export const QUERY_KEY = ['captures'] as const
export const IPC_INBOX_CHANGED = 'captures:inbox-changed'

export type CaptureListItem = {
  id: string
  original_path: string
  annotated_path: string | null
  sidecar_path: string | null
  display_name: string
  width: number
  height: number
  file_size: number
  source: string
  created_at: string
  updated_at: string
}

export type CatalogEnvelope = {
  items: CaptureListItem[]
  pendingInteractive: boolean
}

type PollQuery = {
  state: { data?: CatalogEnvelope }
}

export function parseCatalogEnvelope(data: unknown, pendingInteractive = false): CatalogEnvelope {
  if (data === null || typeof data !== 'object' || Array.isArray(data)) {
    throw new Error('CATALOG_ENVELOPE requires { items }')
  }
  const record = data as { items?: unknown }
  if (!Array.isArray(record.items)) {
    throw new Error('CATALOG_ENVELOPE requires { items }')
  }
  return {
    items: record.items as CaptureListItem[],
    pendingInteractive,
  }
}

export function capturePollInterval(query: PollQuery): number {
  return query.state.data?.pendingInteractive === true ? 1000 : 5000
}

export function sortFilmstrip(items: CaptureListItem[]): CaptureListItem[] {
  return [...items].sort((a, b) => {
    const byDate = b.created_at.localeCompare(a.created_at)
    if (byDate !== 0) {
      return byDate
    }
    return a.display_name.localeCompare(b.display_name)
  })
}

export function useCaptureCatalog() {
  const queryClient = useQueryClient()
  const query = useQuery({
    queryKey: ['captures'],
    queryFn: async () => {
      const list = await apiFetch<unknown>('/captures')
      let pendingInteractive = false
      try {
        const pending = await apiFetch<{ items?: { status?: string }[] }>('/captures/requests?status=pending')
        pendingInteractive = (pending.items ?? []).some((row) => row.status === 'pending')
      } catch {
        pendingInteractive = false
      }
      return parseCatalogEnvelope(list, pendingInteractive)
    },
    refetchInterval: capturePollInterval,
  })

  useEffect(() => {
    const unsub = window.api.onInboxChanged(() => {
      void queryClient.invalidateQueries({ queryKey: QUERY_KEY })
    })
    void IPC_INBOX_CHANGED
    return unsub
  }, [queryClient])

  return query
}
