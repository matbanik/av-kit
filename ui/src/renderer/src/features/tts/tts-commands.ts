import { z } from 'zod'

import { apiFetch } from '../../lib/api'
import { queryClient } from '../../lib/query-client'
import { navigateShell } from '../../lib/shell-nav'
import { QUERY_HEALTH_DEPENDENCIES, TTS_ASSET_WIRES, type TtsAssetWire } from './tts-assets'
import { cancelEnabled, generateEnabled } from './tts-controls'
import {
  QUERY_DOWNLOAD_RUNTIME,
  QUERY_JOB_KEY,
  QUERY_MODELS_AVAILABLE,
  QUERY_MODELS_STATUS,
  QUERY_SETTINGS_TTS,
  type TtsJobOut,
} from './useTtsJob'

export const TTS_EVENTS = {
  prepare: 'av-kit:tts:prepare',
  generate: 'av-kit:tts:generate',
} as const

export const TTS_PALETTE_IDS = ['tts:prepare', 'tts:generate'] as const

const DEVICE_VALUES = ['auto', 'cuda', 'cpu', 'mps'] as const

const prepareSchema = z
  .object({
    text: z.string().min(1),
    enabled_steps: z.array(z.string()),
    chunk_max_chars: z.number().int().positive().optional(),
  })
  .strict()

const generateSchema = z
  .object({
    text: z.string().min(1),
    voice: z.string().min(1),
    speed: z.number().min(0.5).max(2.0),
    format: z.enum(['MP3', 'WAV']),
    enabled_steps: z.array(z.string()),
    source_kind: z.enum(['inline', 'file']),
    source_path: z.string().nullable().optional(),
  })
  .strict()

const loadSchema = z
  .object({
    variant_id: z.string().min(1),
    device: z.enum(DEVICE_VALUES),
  })
  .strict()

const downloadSchema = z
  .object({
    variant_id: z.string().min(1),
  })
  .strict()

const assetDownloadSchema = z
  .object({
    asset: z.enum(TTS_ASSET_WIRES),
  })
  .strict()

const settingsSchema = z
  .object({
    input_text: z.string().max(1_000_000).optional(),
    voice: z.string().optional(),
    speed: z.number().min(0.5).max(2.0).optional(),
    output_format: z.enum(['MP3', 'WAV']).optional(),
    output_path: z.string().optional(),
    device: z.enum(DEVICE_VALUES).optional(),
  })
  .strict()

export type GenerateInput = {
  text: string
  voice: string
  speed: number
  format: 'MP3' | 'WAV'
  enabled_steps: string[]
  source_kind: 'inline' | 'file'
  source_path?: string | null
}

export function buildPrepareBody(
  text: string,
  enabled_steps: string[],
  chunk_max_chars?: number,
): { text: string; enabled_steps: string[]; chunk_max_chars?: number } | null {
  if (text.trim().length < 1) {
    return null
  }
  const payload: { text: string; enabled_steps: string[]; chunk_max_chars?: number } = {
    text,
    enabled_steps,
  }
  if (chunk_max_chars !== undefined) {
    payload.chunk_max_chars = chunk_max_chars
  }
  return prepareSchema.parse(payload)
}

export function buildGenerateBody(input: GenerateInput): GenerateInput {
  return generateSchema.parse(input)
}

export function buildLoadBody(input: { variant_id: string; device: string }): {
  variant_id: string
  device: (typeof DEVICE_VALUES)[number]
} {
  return loadSchema.parse(input)
}

export function buildDownloadBody(input: { variant_id: string }): { variant_id: string } {
  return downloadSchema.parse(input)
}

export function buildAssetDownloadBody(input: { asset: string }): { asset: TtsAssetWire } {
  return assetDownloadSchema.parse(input)
}

export function isTtsHome(): boolean {
  const hash = window.location.hash.replace(/^#/, '')
  return hash === '/tts'
}

export function navigateAndDeliver(run: () => void): void {
  if (!isTtsHome()) {
    navigateShell('/tts')
  }
  window.requestAnimationFrame(() => {
    window.requestAnimationFrame(run)
  })
}

function recordIpc(channel: string, target?: string): void {
  const ledger = (window as unknown as { __e2eIpc?: Array<{ channel: string; target?: string }> })
    .__e2eIpc
  if (Array.isArray(ledger)) {
    ledger.push(target === undefined ? { channel } : { channel, target })
  }
}

export async function postPrepare(
  text: string,
  enabled_steps: string[],
  chunk_max_chars?: number,
): Promise<{ cleaned_text: string } | null> {
  const body = buildPrepareBody(text, enabled_steps, chunk_max_chars)
  if (body === null) {
    return null
  }
  return apiFetch<{ cleaned_text: string }>('/tts/prepare', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export async function postGenerate(
  input: GenerateInput,
  ctx: { isLoaded: boolean; status: string },
): Promise<TtsJobOut | null> {
  if (!generateEnabled({ isLoaded: ctx.isLoaded, text: input.text, status: ctx.status })) {
    return null
  }
  const body = buildGenerateBody(input)
  const job = await apiFetch<TtsJobOut>('/tts/generate', {
    method: 'POST',
    body: JSON.stringify(body),
  })
  queryClient.setQueryData([...QUERY_JOB_KEY, job.id], job)
  return job
}

export async function cancelJob(id: string, status: string): Promise<void> {
  if (!cancelEnabled({ status })) {
    return
  }
  await apiFetch(`/tts/${id}`, { method: 'DELETE' })
  await queryClient.invalidateQueries({ queryKey: QUERY_JOB_KEY })
}

export async function postDownload(variant_id: string): Promise<void> {
  const body = buildDownloadBody({ variant_id })
  await apiFetch('/models/download', {
    method: 'POST',
    body: JSON.stringify(body),
  })
  await queryClient.invalidateQueries({ queryKey: QUERY_DOWNLOAD_RUNTIME })
  await queryClient.invalidateQueries({ queryKey: QUERY_MODELS_AVAILABLE })
}

/** `POST /models/download {asset}` (MEU-62), then refresh the runtime and readiness rows. */
export async function postDownloadAsset(asset: string): Promise<void> {
  const body = buildAssetDownloadBody({ asset })
  await apiFetch('/models/download', {
    method: 'POST',
    body: JSON.stringify(body),
  })
  await queryClient.invalidateQueries({ queryKey: QUERY_DOWNLOAD_RUNTIME })
  await queryClient.invalidateQueries({ queryKey: QUERY_HEALTH_DEPENDENCIES })
}

export async function postLoad(variant_id: string, device: string): Promise<void> {
  const body = buildLoadBody({ variant_id, device })
  await apiFetch('/models/load', {
    method: 'POST',
    body: JSON.stringify(body),
  })
  await queryClient.invalidateQueries({ queryKey: QUERY_MODELS_STATUS })
}

export async function postUnload(): Promise<void> {
  await apiFetch('/models/unload', { method: 'POST' })
  await queryClient.invalidateQueries({ queryKey: QUERY_MODELS_STATUS })
}

export async function putSettings(
  patch: z.infer<typeof settingsSchema>,
): Promise<void> {
  const body = settingsSchema.parse(patch)
  await apiFetch('/settings/tts', {
    method: 'PUT',
    body: JSON.stringify(body),
  })
  await queryClient.invalidateQueries({ queryKey: QUERY_SETTINGS_TTS })
}

export async function openOutput(path: string): Promise<void> {
  recordIpc('openPath', path)
  await window.api.openPath(path)
}

export async function openOutputFolder(path: string): Promise<void> {
  recordIpc('showItemInFolder', path)
  await window.api.showItemInFolder(path)
}

export async function loadTextFile(): Promise<{ text: string; basename: string } | null> {
  recordIpc('readTextFile')
  try {
    return await window.api.readTextFile({ maxBytes: 2_097_152 })
  } catch {
    return null
  }
}

export async function pasteClipboard(): Promise<string> {
  recordIpc('readClipboardText')
  return window.api.readClipboardText()
}

export async function browseOutputDir(): Promise<string | undefined> {
  recordIpc('showDirectoryDialog')
  return window.api.showDirectoryDialog()
}

/** Clicks the page's own button when it is an enabled button; otherwise does nothing (LABELS). */
function clickEnabled(testid: string): void {
  const button = document.querySelector(`[data-testid="${testid}"]`)
  if (button instanceof HTMLButtonElement && !button.disabled) {
    button.click()
  }
}

export function deliverPalettePrepare(): void {
  navigateAndDeliver(() => {
    clickEnabled('preview-cleanup-btn')
  })
}

export function deliverPaletteGenerate(): void {
  navigateAndDeliver(() => {
    clickEnabled('generate-btn')
  })
}

export const TTS_COMMANDS = {
  prepare: deliverPalettePrepare,
  generate: deliverPaletteGenerate,
  postPrepare,
  postGenerate,
  cancelJob,
  postDownload,
  postLoad,
  postUnload,
  putSettings,
  openOutput,
  openOutputFolder,
  loadTextFile,
  pasteClipboard,
  browseOutputDir,
}
