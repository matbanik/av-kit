import { z } from 'zod'

import { ApiError, apiFetch } from '../../lib/api'
import { queryClient } from '../../lib/query-client'
import { navigateShell } from '../../lib/shell-nav'
import {
  controlEnabled,
  type ProcessorState,
  type QueueItemLike,
} from './transcript-controls'
import { QUERY_KEY, parseListEnvelope } from './useTranscriptQueue'

export const TRANSCRIPT_EVENTS = {
  add: 'av-kit:transcript:add',
  start: 'av-kit:transcript:start',
  pause: 'av-kit:transcript:pause',
  resume: 'av-kit:transcript:resume',
  stop: 'av-kit:transcript:stop',
} as const

export const TRANSCRIPT_PALETTE_IDS = [
  'transcript:add',
  'transcript:start',
  'transcript:pause',
  'transcript:resume',
  'transcript:stop',
] as const

const createSchema = z
  .object({
    channel_url: z.string().min(1),
  })
  .strict()

export type CreateTranscriptInput = {
  channel_url: string
}

export type TranscriptJobOut = {
  id: string
  channel_url: string
  channel_name?: string
  video_count?: number
}

export function createTranscriptBody(channelUrl: string): CreateTranscriptInput | null {
  const channel_url = channelUrl.trim()
  if (channel_url.length < 1) {
    return null
  }
  return createSchema.parse({ channel_url })
}

export function applyCreateJob<T extends { id: string }>(job: T): T {
  return job
}

export function isTranscriptHome(): boolean {
  const hash = window.location.hash.replace(/^#/, '')
  return hash === '/transcript'
}

export function navigateAndDeliver(run: () => void): void {
  if (!isTranscriptHome()) {
    navigateShell('/transcript')
  }
  window.requestAnimationFrame(() => {
    window.requestAnimationFrame(run)
  })
}

export function focusChannelInput(): void {
  const tryFocus = (left: number): void => {
    const el = document.querySelector('[data-testid="channel-input"]')
    if (el instanceof HTMLElement) {
      el.focus()
      return
    }
    if (left > 0) {
      window.requestAnimationFrame(() => {
        tryFocus(left - 1)
      })
    }
  }
  tryFocus(16)
}

async function queueContext(): Promise<{
  items: QueueItemLike[]
  processorState: ProcessorState
  selectedId: string | null
}> {
  const cached = queryClient.getQueryData(QUERY_KEY)
  const envelope = cached
    ? parseListEnvelope(cached)
    : parseListEnvelope(await apiFetch<unknown>('/transcripts'))
  if (!cached) {
    queryClient.setQueryData(QUERY_KEY, envelope)
  }
  return {
    items: envelope.items,
    processorState: envelope.processor.state,
    selectedId: envelope.items[0]?.id ?? null,
  }
}

async function invalidateTranscripts(): Promise<void> {
  await queryClient.invalidateQueries({ queryKey: QUERY_KEY })
}

export async function postTranscriptCreate(channelUrl: string): Promise<TranscriptJobOut | null> {
  const body = createTranscriptBody(channelUrl)
  if (body === null) {
    return null
  }
  const job = applyCreateJob(
    await apiFetch<TranscriptJobOut>('/transcripts', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  )
  await invalidateTranscripts()
  return job
}

export async function startTranscripts(): Promise<void> {
  const ctx = await queueContext()
  if (!controlEnabled('start', ctx)) {
    return
  }
  await apiFetch('/transcripts/start', { method: 'POST' })
  await invalidateTranscripts()
}

export async function pauseTranscripts(): Promise<void> {
  const ctx = await queueContext()
  if (!controlEnabled('pause', ctx)) {
    return
  }
  await apiFetch('/transcripts/pause', { method: 'POST' })
  await invalidateTranscripts()
}

export async function resumeTranscripts(): Promise<void> {
  const ctx = await queueContext()
  if (!controlEnabled('resume', ctx)) {
    return
  }
  await apiFetch('/transcripts/resume', { method: 'POST' })
  await invalidateTranscripts()
}

export async function stopTranscripts(): Promise<void> {
  const ctx = await queueContext()
  if (!controlEnabled('stop', ctx)) {
    return
  }
  await apiFetch('/transcripts/stop', { method: 'POST' })
  await invalidateTranscripts()
}

export async function compileTranscript(id: string): Promise<{ compiled_paths: string[] }> {
  const compiled = await apiFetch<{ compiled_paths: string[] }>(`/transcripts/${id}/compile`, {
    method: 'POST',
    body: JSON.stringify({}),
  })
  await invalidateTranscripts()
  return compiled
}

export async function requeueTranscript(id: string): Promise<void> {
  await apiFetch(`/transcripts/${id}/requeue`, { method: 'POST', body: JSON.stringify({}) })
  await invalidateTranscripts()
}

export async function retryTranscript(id: string): Promise<void> {
  await apiFetch(`/transcripts/${id}/retry`, { method: 'POST', body: JSON.stringify({}) })
  await invalidateTranscripts()
}

export async function removeTranscript(id: string): Promise<void> {
  await apiFetch(`/transcripts/${id}`, { method: 'DELETE' })
  await invalidateTranscripts()
}

function recordOpenPath(target: string): void {
  const ledger = (window as unknown as { __e2eIpc?: Array<{ channel: string; target: string }> }).__e2eIpc
  if (Array.isArray(ledger)) {
    ledger.push({ channel: 'openPath', target })
  }
}

export async function openCompiled(path: string): Promise<void> {
  recordOpenPath(path)
  await window.api.openPath(path)
}

export async function openZip(path: string): Promise<void> {
  recordOpenPath(path)
  await window.api.openPath(path)
}

export async function openFolder(path: string): Promise<void> {
  recordOpenPath(path)
  await window.api.openPath(path)
}

export function deliverPaletteAdd(): void {
  navigateAndDeliver(() => {
    focusChannelInput()
  })
}

export function deliverPaletteStart(): void {
  navigateAndDeliver(() => {
    void startTranscripts().catch(rethrow)
  })
}

export function deliverPalettePause(): void {
  navigateAndDeliver(() => {
    void pauseTranscripts().catch(rethrow)
  })
}

export function deliverPaletteResume(): void {
  navigateAndDeliver(() => {
    void resumeTranscripts().catch(rethrow)
  })
}

export function deliverPaletteStop(): void {
  navigateAndDeliver(() => {
    void stopTranscripts().catch(rethrow)
  })
}

function rethrow(error: unknown): void {
  const message = error instanceof ApiError || error instanceof Error ? error.message : String(error)
  window.dispatchEvent(new CustomEvent('av-kit:transcript:error', { detail: message }))
}

export const TRANSCRIPT_COMMANDS = {
  add: deliverPaletteAdd,
  start: deliverPaletteStart,
  pause: deliverPalettePause,
  resume: deliverPaletteResume,
  stop: deliverPaletteStop,
  postTranscriptCreate,
  compileTranscript,
  requeueTranscript,
  retryTranscript,
  removeTranscript,
  openCompiled,
  openZip,
  openFolder,
}
