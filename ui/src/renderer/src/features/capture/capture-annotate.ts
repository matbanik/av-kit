import { z } from 'zod'

import { PIXELATE_BLOCK_MAX, PIXELATE_BLOCK_MIN } from './capture-region-pass'

export const ANNOTATE_PATH = '/captures/{id}/annotate'


const NAMED_COLORS = ['red', 'orange', 'yellow', 'green', 'blue', 'white', 'black'] as const

const colorSchema = z.union([z.enum(NAMED_COLORS), z.string().regex(/^#[0-9A-Fa-f]{6}$/)])

const arrowSchema = z
  .object({
    type: z.literal('arrow'),
    color: colorSchema,
    stroke_width: z.number().int().positive(),
    from: z.tuple([z.number().int(), z.number().int()]),
    to: z.tuple([z.number().int(), z.number().int()]),
  })
  .strict()

const rectSchema = z
  .object({
    type: z.literal('rect'),
    x: z.number().int(),
    y: z.number().int(),
    width: z.number().int(),
    height: z.number().int(),
    color: colorSchema,
    stroke_width: z.number().int().positive(),
  })
  .strict()

const highlightSchema = z
  .object({
    type: z.literal('highlight'),
    x: z.number().int(),
    y: z.number().int(),
    width: z.number().int(),
    height: z.number().int(),
    color: colorSchema,
    opacity: z.number().min(0).max(1),
  })
  .strict()

const textSchema = z
  .object({
    type: z.literal('text'),
    x: z.number().int(),
    y: z.number().int(),
    text: z.string().min(1).max(500),
    color: colorSchema,
    font_size: z.number().int().positive(),
    bg_color: colorSchema.nullable().optional(),
  })
  .strict()

/** REGION_DTO: block_size is required here; only the API and MCP apply the default. */
const pixelateSchema = z
  .object({
    type: z.literal('pixelate'),
    x: z.number().int(),
    y: z.number().int(),
    width: z.number().int(),
    height: z.number().int(),
    block_size: z.number().int().min(PIXELATE_BLOCK_MIN).max(PIXELATE_BLOCK_MAX),
  })
  .strict()

/** REGION_DTO: an eraser is a rectangle only; its colour comes from ERASER_SAMPLE at bake and preview time. */
const eraserSchema = z
  .object({
    type: z.literal('eraser'),
    x: z.number().int(),
    y: z.number().int(),
    width: z.number().int(),
    height: z.number().int(),
  })
  .strict()

/** REDACT_TYPE (D-679): a solid box over a region; the GUI always sends its colour (`#000000`). */
const redactSchema = z
  .object({
    type: z.literal('redact'),
    x: z.number().int(),
    y: z.number().int(),
    width: z.number().int(),
    height: z.number().int(),
    color: colorSchema,
  })
  .strict()

export const annotateInSchema = z
  .object({
    annotations: z.array(
      z.discriminatedUnion('type', [
        arrowSchema,
        rectSchema,
        highlightSchema,
        textSchema,
        pixelateSchema,
        eraserSchema,
        redactSchema,
      ]),
    ),
  })
  .strict()

export type AnnotateBody = z.infer<typeof annotateInSchema>
export type Annotation = AnnotateBody['annotations'][number]

/** REDACT_TYPE (D-679): a solid box over a region. */
export type RedactAnnotation = Extract<Annotation, { type: 'redact' }>

/** REDACT_MODE (D-680): what the Redact tool draws. */
export type RedactMode = 'solid' | 'pixelate'

export function parseAnnotateBody(input: unknown): AnnotateBody | null {
  const parsed = annotateInSchema.safeParse(input)
  return parsed.success ? parsed.data : null
}
