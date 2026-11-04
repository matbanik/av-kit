/**
 * MEU-45 — converter control predicates and card meta (AC-45.5, AC-45.12, AC-45.17).
 *
 * Three separate contracts share this file because they share one module:
 *
 * - **AC-45.5** widens `controlEnabled('reset')` from `Failed` alone to
 *   `CONVERT_REQUEUEABLE_STATUSES`. The test enumerates the whole conversion
 *   status enum (`REQUEUE_EXHAUSTIVENESS_RULE`) so a future status cannot slip in
 *   unclassified, and asserts `Skipped` stays excluded (`USER_LOCKS` lock 4).
 * - **AC-45.12** deletes the rival `STATUS_COLORS` map: status colour has exactly
 *   one home, `lib/queue/status-tokens.ts`.
 * - **AC-45.17** adds `convertMetaSegments`, which carries the Kind/Mode/Speed/ETA
 *   columns of the deleted `ConvertQueueTable` onto the card's meta line. Speed
 *   and ETA are emitted whenever the field is non-null *regardless of status* —
 *   the backend never clears them (`services/conversion.py:553-573`) — and a mode
 *   that does not resolve yields no segment rather than a stray em dash.
 */

import { readFileSync, readdirSync, statSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

import {
  JOB_STATUSES,
  controlEnabled,
  type ControlContext,
  type QueueItemLike,
} from '../../src/renderer/src/features/converter/convert-controls'
import { PRESET_LABELS } from '../../src/renderer/src/features/converter/convert-presets'
import { STATUS_PILL_TOKENS } from '../../src/renderer/src/lib/queue/status-tokens'

import type * as ConvertControlsModule from '../../src/renderer/src/features/converter/convert-controls'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')
const planDir = resolve(repoRoot, 'docs/execution/plans/2026-09-02-p10-queue-card-migration')
const UI_SRC = resolve(repoRoot, 'ui/src')
const CONVERTER_DIR = resolve(UI_SRC, 'renderer/src/features/converter')

type NamedSet<T> = { value: T; complement?: T }
type NamedSets = {
  CONVERT_REQUEUEABLE_STATUSES: NamedSet<string[]>
  CONVERT_META_SEGMENTS: NamedSet<string[]>
  META_SEPARATOR: NamedSet<string>
}

const SETS = JSON.parse(readFileSync(resolve(planDir, 'named-sets.json'), 'utf-8')) as NamedSets

const REQUEUEABLE = SETS.CONVERT_REQUEUEABLE_STATUSES.value
const NOT_REQUEUEABLE = SETS.CONVERT_REQUEUEABLE_STATUSES.complement ?? []
const CONVERT_META_SEGMENTS = SETS.CONVERT_META_SEGMENTS.value

function loadControls(): Promise<typeof ConvertControlsModule> {
  return import(
    /* @vite-ignore */ '../../src/renderer/src/features/converter/convert-controls'
  ) as Promise<typeof ConvertControlsModule>
}

function walk(dir: string): string[] {
  let entries: string[]
  try {
    entries = readdirSync(dir)
  } catch {
    return []
  }
  const out: string[] = []
  for (const entry of entries) {
    const full = resolve(dir, entry)
    if (statSync(full).isDirectory()) {
      out.push(...walk(full))
    } else if (/\.(ts|tsx)$/.test(entry)) {
      out.push(full)
    }
  }
  return out
}

function item(overrides: Partial<QueueItemLike> = {}): QueueItemLike {
  return {
    id: 'job-1',
    status: 'Pending',
    output_path: null,
    input_path: 'C:/in/clip.mp4',
    ...overrides,
  }
}

function context(status: string): ControlContext {
  return {
    items: [item({ status })],
    selectedId: 'job-1',
    processorState: 'Idle',
    ffmpegAvailable: true,
  }
}

/** A conversion list row with every optional field null unless overridden. */
type ConversionRow = {
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

function row(overrides: Partial<ConversionRow> = {}): ConversionRow {
  return {
    id: 'job-1',
    kind: 'compress',
    input_path: 'C:/in/clip.mp4',
    output_path: null,
    display_name: 'clip.mp4',
    preset_id: null,
    cq: null,
    scale_height: null,
    audio_mode: null,
    gpu_encoder: null,
    in_ms: null,
    out_ms: null,
    copy_mode: null,
    stream_index: null,
    status: 'Pending',
    progress: 0,
    speed: null,
    eta: null,
    file_size: null,
    queue_position: 1,
    ...overrides,
  }
}

describe('MEU-45 convert-controls', () => {
  it('AC-45.5 controlEnabled(reset) is exactly CONVERT_REQUEUEABLE_STATUSES over the full enum', () => {
    // REQUEUE_EXHAUSTIVENESS_RULE: every member of the enum is classified, so a
    // new status cannot arrive unclassified and silently default to disabled.
    const classified = [...REQUEUEABLE, ...NOT_REQUEUEABLE].sort()
    expect(classified, 'the named set partitions the whole conversion enum').toEqual(
      [...JOB_STATUSES].sort(),
    )

    for (const status of JOB_STATUSES) {
      const expected = REQUEUEABLE.includes(status)
      expect(controlEnabled('reset', context(status)), `reset on ${status}`).toBe(expected)
    }

    // USER_LOCKS lock 4, asserted explicitly rather than left to the partition.
    expect(controlEnabled('reset', context('Skipped')), 'Skipped is locked out').toBe(false)
    expect(controlEnabled('reset', context('Cancelled')), 'Cancelled is widened in').toBe(true)

    // The download-only blockers are not conversion statuses; the API answers 409
    // for them, so the converter must never offer Retry on one.
    for (const alien of ['QualityBlocked', 'AgeRestricted']) {
      expect(JOB_STATUSES as readonly string[], `${alien} is not a conversion status`).not.toContain(
        alien,
      )
      expect(controlEnabled('reset', context(alien)), `reset on ${alien}`).toBe(false)
    }

    // With nothing selected there is nothing to re-queue.
    expect(
      controlEnabled('reset', {
        items: [item({ status: 'Failed' })],
        selectedId: null,
        processorState: 'Idle',
        ffmpegAvailable: true,
      }),
    ).toBe(false)
  })

  it('AC-45.12 STATUS_COLORS is gone and status colour comes from status-tokens', async () => {
    const controls = (await loadControls()) as Record<string, unknown>
    expect(
      Object.prototype.hasOwnProperty.call(controls, 'STATUS_COLORS'),
      'the rival status colour map is deleted',
    ).toBe(false)

    // Scope correction (MEU-45 execution): the Red-phase form of this assertion
    // swept all of `ui/src` and demanded an empty list. That is unsatisfiable
    // alongside the landed AC-43.2 census in `queue-primitives.test.ts`, which
    // PINS the six surviving legacy maps (downloader x2, transcript x2, tts x2)
    // and states in-line that "MEU-45 removes both converter entries". AC-45.12
    // itself is scoped to `convert-controls.ts`. The capability asserted here is
    // therefore unchanged but correctly bounded: no rival status->colour map
    // survives anywhere in the CONVERTER feature. The downloader pair retires in
    // MEU-46; transcript/tts sit outside Phase 10 and keep their own maps, whose
    // growth AC-43.2 already guards.
    const offenders = walk(CONVERTER_DIR).filter((file) =>
      readFileSync(file, 'utf-8').includes('STATUS_COLORS'),
    )
    expect(offenders.map((file) => file.replace(repoRoot, '').replace(/\\/g, '/'))).toEqual([])

    // The surviving single statement covers every conversion status.
    for (const status of JOB_STATUSES) {
      expect(
        Object.prototype.hasOwnProperty.call(STATUS_PILL_TOKENS, status),
        `status-tokens covers ${status}`,
      ).toBe(true)
    }
  })

  it('AC-45.17 convertMetaSegments returns CONVERT_META_SEGMENTS with null fields dropped', async () => {
    const { convertMetaSegments } = await loadControls()
    expect(CONVERT_META_SEGMENTS, 'kind, mode, speed, eta').toHaveLength(4)

    // Kind and mode: the labels the deleted table's Kind/Mode columns rendered.
    expect(convertMetaSegments(row({ kind: 'compress', preset_id: 'balanced' }))).toEqual([
      'Compress',
      PRESET_LABELS.balanced,
    ])
    expect(convertMetaSegments(row({ kind: 'cut', in_ms: 1000, out_ms: 4500 }))).toEqual([
      'Cut',
      '1000–4500',
    ])
    expect(convertMetaSegments(row({ kind: 'extract', stream_index: 1 }))).toEqual([
      'Extract',
      'a:1',
    ])

    // Speed and ETA survive on a Done row — the backend does not clear them.
    expect(
      convertMetaSegments(
        row({
          kind: 'compress',
          preset_id: 'mobile',
          status: 'Done',
          speed: '2.4x',
          eta: '00:00',
        }),
      ),
      'a finished row keeps its persisted speed and ETA',
    ).toEqual(['Compress', PRESET_LABELS.mobile, '2.4x', '00:00'])

    // A null field yields no segment at all — never an empty string, never '—'.
    const sparseCut = convertMetaSegments(row({ kind: 'cut', in_ms: null, out_ms: null }))
    expect(sparseCut, 'an unresolved cut mode yields no segment').toEqual(['Cut'])
    const sparseCompress = convertMetaSegments(row({ kind: 'compress', preset_id: null }))
    expect(sparseCompress, 'a compress row with no preset yields no mode segment').toEqual([
      'Compress',
    ])
    // `extract` keeps the deleted table's real fallback rather than dropping the
    // segment: 'audio' says something true about the job, '—' does not.
    const sparseExtract = convertMetaSegments(row({ kind: 'extract' }))
    expect(sparseExtract).toEqual(['Extract', 'audio'])
    for (const segments of [sparseCut, sparseCompress, sparseExtract]) {
      expect(segments.some((segment) => segment.trim() === '')).toBe(false)
      expect(segments).not.toContain('—')
    }

    // Speed without ETA (and the reverse) keeps ordering stable.
    expect(convertMetaSegments(row({ kind: 'compress', preset_id: 'sharing', eta: '01:12' }))).toEqual(
      ['Compress', PRESET_LABELS.sharing, '01:12'],
    )
    expect(
      convertMetaSegments(row({ kind: 'compress', preset_id: 'sharing', speed: '1.1x' })),
    ).toEqual(['Compress', PRESET_LABELS.sharing, '1.1x'])
  })
})
