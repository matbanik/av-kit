import { useQuery } from '@tanstack/react-query'

import { apiFetch } from '../../lib/api'
import type { ProcessorState } from './convert-controls'

export const QUERY_KEY = ['conversions'] as const

export type ConversionListItem = {
  id: string
  kind: string
  input_path: string
  output_path: string | null
  display_name: string
  preset_id: string | null
  cq: number | null
  scale_height: number | null
  audio_mode: string | null
  gpu_encoder: string | null
  in_ms: number | null
  out_ms: number | null
  copy_mode: string | null
  stream_index: number | null
  status: string
  progress: number
  speed: string | null
  eta: string | null
  file_size: number | null
  queue_position: number
}

export type ListEnvelope = {
  items: ConversionListItem[]
  processor: { state: ProcessorState; current_job_id?: string | null }
}

type PollQuery = {
  state: { data?: { processor?: { state?: string } } }
}

export function parseListEnvelope(data: unknown): ListEnvelope {
  if (data === null || typeof data !== 'object' || Array.isArray(data)) {
    throw new Error('LIST_ENVELOPE requires { items, processor }')
  }
  const record = data as { items?: unknown; processor?: unknown }
  if (!Array.isArray(record.items) || record.processor === null || typeof record.processor !== 'object') {
    throw new Error('LIST_ENVELOPE requires { items, processor }')
  }
  const processor = record.processor as { state?: unknown }
  if (processor.state !== 'Idle' && processor.state !== 'Processing' && processor.state !== 'Paused') {
    throw new Error('LIST_ENVELOPE processor.state is invalid')
  }
  return {
    items: record.items as ConversionListItem[],
    processor: {
      state: processor.state,
      current_job_id: (processor as { current_job_id?: string | null }).current_job_id,
    },
  }
}

export function conversionPollInterval(query: PollQuery): number {
  return query.state.data?.processor?.state === 'Processing' ? 1000 : 5000
}

export function useConversionQueue() {
  return useQuery({
    queryKey: QUERY_KEY,
    queryFn: async () => parseListEnvelope(await apiFetch<unknown>('/conversions')),
    refetchInterval: conversionPollInterval,
  })
}
