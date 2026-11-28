import { z } from 'zod'

import { COOKIE_BROWSERS, COOKIE_MODES } from '../downloader/cookie-bar'
import { AUDIO_WIRE, QUALITY_WIRE } from '../downloader/quality-options'
import { GPU_PREF_WIRES, PRESET_WIRES } from '../converter/convert-presets'

const LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] as const
const THEMES = ['dark', 'light'] as const
/** UPDATE_INTERVAL_LEAF: the wires of `app.update_interval` (MEU-174). */
export const UPDATE_INTERVALS = ['weekly', 'monthly', 'never'] as const

export const downloaderPutSchema = z
  .object({
    path: z.string().nullable().optional(),
    ffmpeg_path: z.string().nullable().optional(),
    quality: z.enum(QUALITY_WIRE).nullable().optional(),
    audio_only: z.boolean().nullable().optional(),
    audio_format: z.enum(AUDIO_WIRE).nullable().optional(),
    cookie_mode: z.enum(COOKIE_MODES).nullable().optional(),
    cookie_browser: z.enum(COOKIE_BROWSERS).nullable().optional(),
    cookie_browser_profile: z.string().nullable().optional(),
    cookie_file_path: z.string().nullable().optional(),
    archive_tracking: z.boolean().nullable().optional(),
    yt_dlp_debug: z.boolean().nullable().optional(),
    deno_path: z.string().nullable().optional(),
  })
  .strict()

export const transcriptPutSchema = z
  .object({
    output_dir: z.string().nullable().optional(),
    requests_per_hour: z.number().nullable().optional(),
    delay_between_requests: z.number().nullable().optional(),
    max_retries: z.number().nullable().optional(),
    retry_delay: z.number().nullable().optional(),
    batch_size: z.number().nullable().optional(),
    pause_between_batches: z.number().nullable().optional(),
    playlist_end: z.number().nullable().optional(),
    max_words_per_document: z.number().nullable().optional(),
  })
  .strict()

export const ttsPutSchema = z
  .object({
    models_directory: z.string().nullable().optional(),
    voice: z.string().nullable().optional(),
    speed: z.number().nullable().optional(),
    output_format: z.string().nullable().optional(),
    output_path: z.string().nullable().optional(),
    device: z.string().nullable().optional(),
    chunk_max_chars: z.number().nullable().optional(),
  })
  .strict()

export const appPutSchema = z
  .object({
    log_level: z.enum(LOG_LEVELS).nullable().optional(),
    log_to_file: z.boolean().nullable().optional(),
    console_visible: z.boolean().nullable().optional(),
    update_interval: z.enum(UPDATE_INTERVALS).nullable().optional(),
  })
  .strict()

export const uiPutSchema = z
  .object({
    theme: z.enum(THEMES).nullable().optional(),
  })
  .strict()

export const converterPutSchema = z
  .object({
    output_dir: z.string(),
    default_preset: z.enum(PRESET_WIRES),
    skip_existing: z.boolean(),
    gpu_preference: z.enum(GPU_PREF_WIRES),
  })
  .strict()

/** ANNOTATED_FORMATS (avkit_core.domain.capture): Save overlay file formats. */
export const ANNOTATED_FORMATS = ['png', 'jpeg', 'webp'] as const
export type AnnotatedFormat = (typeof ANNOTATED_FORMATS)[number]

export const capturePutSchema = z
  .object({
    inbox_dir: z.string(),
    hotkey: z.string(),
    copy_to_clipboard: z.boolean(),
    close_to_tray: z.boolean(),
    flatten_backup: z.boolean(),
    backup_dir: z.string(),
    annotated_format: z.enum(ANNOTATED_FORMATS),
  })
  .strict()

const CAPTURE_COLOR = /^#[0-9A-Fa-f]{6}$/
const CAPTURE_COLOR_OR_EMPTY = /^(#[0-9A-Fa-f]{6})?$/

/**
 * STYLE_STORE (MEU-105, D-720): the body of one tool-style PUT, only the style leaves it changes. The
 * Capture card's `capturePutSchema` keeps its seven keys.
 */
export const captureStylePutSchema = z
  .object({
    arrow_color: z.string().regex(CAPTURE_COLOR),
    arrow_stroke: z.number().int().min(1).max(100),
    box_color: z.string().regex(CAPTURE_COLOR),
    box_stroke: z.number().int().min(1).max(100),
    highlight_color: z.string().regex(CAPTURE_COLOR),
    text_color: z.string().regex(CAPTURE_COLOR),
    text_font_size: z.number().int().min(1).max(400),
    text_bg_color: z.string().regex(CAPTURE_COLOR_OR_EMPTY),
    pixelate_block_size: z.number().int().min(2).max(100),
    // STEP_STYLE (MEU-107, D-775): the Step tool's colour and badge size.
    step_color: z.string().regex(CAPTURE_COLOR),
    step_size: z.number().int().min(12).max(200),
  })
  .partial()
  .strict()

/** LOCK_LEAF (MEU-143, D-746): the body of one tool-lock PUT. */
export const captureLockPutSchema = z.object({ tool_lock: z.boolean() }).strict()

export type DownloaderPut = z.infer<typeof downloaderPutSchema>
export type TranscriptPut = z.infer<typeof transcriptPutSchema>
export type TtsPut = z.infer<typeof ttsPutSchema>
export type AppPut = z.infer<typeof appPutSchema>
export type UiPut = z.infer<typeof uiPutSchema>
export type ConverterPut = z.infer<typeof converterPutSchema>
export type CapturePut = z.infer<typeof capturePutSchema>
export type CaptureStylePut = z.infer<typeof captureStylePutSchema>

export type SettingsNamespace = 'downloader' | 'transcript' | 'tts' | 'app' | 'ui' | 'converter' | 'capture'

const schemaByNamespace = {
  downloader: downloaderPutSchema,
  transcript: transcriptPutSchema,
  tts: ttsPutSchema,
  app: appPutSchema,
  ui: uiPutSchema,
  converter: converterPutSchema,
  capture: capturePutSchema,
} as const

export class SettingsValidationError extends Error {
  readonly unknownKeys: string[]

  constructor(message: string, unknownKeys: string[] = []) {
    super(message)
    this.name = 'SettingsValidationError'
    this.unknownKeys = unknownKeys
  }
}

export function parseSettingsPut<N extends SettingsNamespace>(
  namespace: N,
  patch: unknown,
): z.infer<(typeof schemaByNamespace)[N]> {
  const schema = schemaByNamespace[namespace]
  const parsed = schema.safeParse(patch)
  if (!parsed.success) {
    const unknown = parsed.error.issues
      .filter((issue) => issue.code === 'unrecognized_keys')
      .flatMap((issue) => ('keys' in issue ? (issue.keys as string[]) : []))
    throw new SettingsValidationError(parsed.error.message, unknown)
  }
  return parsed.data as z.infer<(typeof schemaByNamespace)[N]>
}

export function safeParseSettingsPut<N extends SettingsNamespace>(
  namespace: N,
  patch: unknown,
):
  | { ok: true; data: z.infer<(typeof schemaByNamespace)[N]> }
  | { ok: false; error: SettingsValidationError } {
  try {
    return { ok: true, data: parseSettingsPut(namespace, patch) }
  } catch (caught) {
    if (caught instanceof SettingsValidationError) {
      return { ok: false, error: caught }
    }
    throw caught
  }
}
