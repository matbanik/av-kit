import { z } from 'zod'

import {
  AUDIO_MODE_WIRES,
  GPU_PREF_WIRES,
  PRESET_WIRES,
  type AudioModeWire,
  type GpuPrefWire,
  type PresetWire,
  type ScaleHeight,
} from './convert-presets'

const pathsSchema = z.array(z.string().min(1)).min(1)

const compressSchema = z
  .object({
    paths: pathsSchema,
    kind: z.literal('compress'),
    preset: z.enum(PRESET_WIRES),
    cq: z.number().int().min(18).max(32).optional(),
    scale_height: z.union([z.literal(0), z.literal(1080), z.literal(720), z.literal(480)]).optional(),
    audio_mode: z.enum(AUDIO_MODE_WIRES).optional(),
    gpu_preference: z.enum(GPU_PREF_WIRES).optional(),
  })
  .strict()

const cutSchema = z
  .object({
    paths: pathsSchema,
    kind: z.literal('cut'),
    in_ms: z.number().int().min(0),
    out_ms: z.number().int().min(0),
    copy_mode: z.enum(['fast_copy', 'reencode']).default('fast_copy'),
  })
  .strict()

const extractSchema = z
  .object({
    paths: pathsSchema,
    kind: z.literal('extract'),
    stream_mode: z.enum(['first', 'all']),
    stream_index: z.number().int().min(0).optional(),
  })
  .strict()

const createSchema = z.discriminatedUnion('kind', [compressSchema, cutSchema, extractSchema])

export type ConversionKindWire = 'compress' | 'cut' | 'extract'
export type CopyModeWire = 'fast_copy' | 'reencode'
export type StreamModeWire = 'first' | 'all'

export type ConversionCreateBody =
  | {
      paths: string[]
      kind: 'compress'
      preset: PresetWire
      cq?: number
      scale_height?: ScaleHeight
      audio_mode?: AudioModeWire
      gpu_preference?: GpuPrefWire
    }
  | {
      paths: string[]
      kind: 'cut'
      in_ms: number
      out_ms: number
      copy_mode: CopyModeWire
    }
  | {
      paths: string[]
      kind: 'extract'
      stream_mode: StreamModeWire
      stream_index?: number
    }

function omitUndefined<T extends Record<string, unknown>>(row: T): T {
  const next: Record<string, unknown> = {}
  for (const [key, value] of Object.entries(row)) {
    if (value !== undefined) {
      next[key] = value
    }
  }
  return next as T
}

export function createConversionBody(input: unknown): ConversionCreateBody | null {
  const parsed = createSchema.safeParse(input)
  if (!parsed.success) {
    return null
  }
  if (parsed.data.kind === 'compress') {
    return omitUndefined({
      paths: parsed.data.paths,
      kind: 'compress' as const,
      preset: parsed.data.preset,
      cq: parsed.data.cq,
      scale_height: parsed.data.scale_height,
      audio_mode: parsed.data.audio_mode,
      gpu_preference: parsed.data.gpu_preference,
    })
  }
  if (parsed.data.kind === 'cut') {
    if (parsed.data.out_ms <= parsed.data.in_ms) {
      return null
    }
    return {
      paths: parsed.data.paths,
      kind: 'cut',
      in_ms: parsed.data.in_ms,
      out_ms: parsed.data.out_ms,
      copy_mode: parsed.data.copy_mode,
    }
  }
  return omitUndefined({
    paths: parsed.data.paths,
    kind: 'extract' as const,
    stream_mode: parsed.data.stream_mode,
    stream_index: parsed.data.stream_index,
  })
}
