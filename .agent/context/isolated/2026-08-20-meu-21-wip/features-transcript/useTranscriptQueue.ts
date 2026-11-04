import { useQuery } from '@tanstack/react-query'

import { apiFetch } from '../../lib/api'
import type { ProcessorState } from './transcript-controls'

export const QUERY_KEY = ['transcripts'] as const

export type TranscriptListItem = {
  id: string
  channel_url: string
  channel_name: string
  status: string
  output_dir: string
  video_count: number
  transcripts_done: number
  word_count: number
  zip_path: string | null
  last_title: string | null
  last_item_status: string | null
  queue_position: number
  compiled_path?: string | null
}

export type ListEnvelope = {
  items: TranscriptListItem[]
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
    items: record.items as TranscriptListItem[],
    processor: {
      state: processor.state,
      current_job_id: (processor as { current_job_id?: string | null }).current_job_id,
    },
  }
}

export function transcriptPollInterval(query: PollQuery): number {
  return query.state.data?.processor?.state === 'Processing' ? 1000 : 5000
}

export function useTranscriptQueue() {
  return useQuery({
    queryKey: QUERY_KEY,
    queryFn: async () => parseListEnvelope(await apiFetch<unknown>('/transcripts')),
    refetchInterval: transcriptPollInterval,
  })
}
