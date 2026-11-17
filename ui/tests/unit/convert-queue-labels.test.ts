/** @vitest-environment jsdom */

/**
 * MEU-152 (Session 81) — Convert queue labels: Cut time codes, row numbers and waiting texts.
 *
 * - **AC-152.1 / AC-152.2** pin `CONVERT_TIMECODE`: `formatConvertTime(ms)` gives `HH:MM:SS.mmm`, the
 *   form `format_timecode` writes on the Python side, round-trips with `parseConvertTime`, and refuses
 *   a value that is not a whole, non-negative number of milliseconds within `CONVERT_TIME_MAX_MS`.
 * - **AC-152.3** pins `CUT_SEGMENT_TIMECODE`'s out-of-range and sparse cases; the in-range pin lives in
 *   `convert-controls.test.ts` (AC-45.17).
 * - **AC-152.4 to AC-152.7** pin `QUEUE_ROW_NUMBER`: the row is the 1-based array index and the waiting
 *   value counts only the Pending jobs, so a finish, a remove or a move renumbers both (D-970).
 * - **AC-152.8** pins `WAITING_POSITION` on `QueueCard`.
 *
 * Every test loads its module as a namespace and asserts the new export is a function before it calls
 * it, so the Red phase fails by assertion rather than by a missing import.
 */

import { render, screen } from '@testing-library/react'
import { createElement } from 'react'
import { afterEach, describe, expect, it } from 'vitest'

import type * as ConvertControlsModule from '../../src/renderer/src/features/converter/convert-controls'
import type * as ConvertTimeModule from '../../src/renderer/src/features/converter/convert-time'
import type * as QueueCardModule from '../../src/renderer/src/components/queue/QueueCard'

type CutRow = {
  id: string
  kind: string
  preset_id: string | null
  gpu_encoder: string | null
  in_ms: number | null
  out_ms: number | null
  stream_index: number | null
  speed: string | null
  eta: string | null
  status: string
}

type Positions = Map<string, { row: number; waiting: number | null }>

async function loadTime(): Promise<typeof ConvertTimeModule> {
  return (await import('../../src/renderer/src/features/converter/convert-time')) as typeof ConvertTimeModule
}

async function loadControls(): Promise<typeof ConvertControlsModule> {
  return (await import(
    '../../src/renderer/src/features/converter/convert-controls'
  )) as typeof ConvertControlsModule
}

async function loadCard(): Promise<typeof QueueCardModule> {
  return (await import('../../src/renderer/src/components/queue/QueueCard')) as typeof QueueCardModule
}

/** The time helper under test, asserted to exist first. */
async function formatter(): Promise<(ms: number) => string | null> {
  const time = (await loadTime()) as unknown as Record<string, unknown>
  expect(typeof time.formatConvertTime, 'convert-time exports formatConvertTime').toBe('function')
  return time.formatConvertTime as (ms: number) => string | null
}

/** The row-number helper under test, asserted to exist first. */
async function positioner(): Promise<(items: readonly { id: string; status: string }[]) => Positions> {
  const controls = (await loadControls()) as unknown as Record<string, unknown>
  expect(typeof controls.convertQueuePositions, 'convert-controls exports convertQueuePositions').toBe(
    'function',
  )
  return controls.convertQueuePositions as (items: readonly { id: string; status: string }[]) => Positions
}

function cut(overrides: Partial<CutRow> = {}): CutRow {
  return {
    id: 'job-1',
    kind: 'cut',
    preset_id: null,
    gpu_encoder: null,
    in_ms: 1000,
    out_ms: 4500,
    stream_index: null,
    speed: null,
    eta: null,
    status: 'Pending',
    ...overrides,
  }
}

function queue(statuses: readonly string[], stored: readonly number[]): { id: string; status: string; queue_position: number }[] {
  return statuses.map((status, index) => ({
    id: `job-${String(index + 1)}`,
    status,
    queue_position: stored[index] ?? index,
  }))
}

function rowsAndWaiting(positions: Positions, ids: readonly string[]): [number[], (number | null)[]] {
  return [ids.map((id) => positions.get(id)?.row ?? -1), ids.map((id) => positions.get(id)?.waiting ?? null)]
}

afterEach(() => {
  document.body.innerHTML = ''
})

describe('MEU-152 Convert queue labels', () => {
  it('AC-152.1 formatConvertTime gives HH:MM:SS.mmm', async () => {
    const format = await formatter()
    expect(format(0)).toBe('00:00:00.000')
    expect(format(1000)).toBe('00:00:01.000')
    expect(format(4500)).toBe('00:00:04.500')
    expect(format(3_723_004)).toBe('01:02:03.004')
    expect(format(359_999_999)).toBe('99:59:59.999')
  })

  it('AC-152.2 formatConvertTime round-trips with parseConvertTime and refuses values out of range', async () => {
    const format = await formatter()
    const time = await loadTime()
    for (const ms of [0, 1000, 4500, 3_723_004, 359_999_999, 59_999]) {
      const text = format(ms)
      expect(text, `${String(ms)} formats`).not.toBeNull()
      expect(time.parseConvertTime(text ?? ''), `${String(ms)} round-trips`).toBe(ms)
    }
    for (const ms of [-1, 1.5, Number.NaN, Number.POSITIVE_INFINITY, 360_000_000]) {
      expect(format(ms), `${String(ms)} is refused`).toBeNull()
    }
  })

  it('AC-152.3 a Cut out of range drops its mode segment, and a sparse Cut gives only its kind', async () => {
    await formatter()
    const controls = await loadControls()
    expect(controls.convertMetaSegments(cut({ out_ms: 360_000_000 }))).toEqual(['Cut'])
    expect(controls.convertMetaSegments(cut({ in_ms: null, out_ms: null }))).toEqual(['Cut'])
  })

  it('AC-152.4 rows count every card and the waiting value counts the Pending jobs', async () => {
    const positions = await positioner()
    const items = queue(['Processing', 'Pending', 'Pending'], [0, 1, 2])
    expect(rowsAndWaiting(positions(items), ['job-1', 'job-2', 'job-3'])).toEqual([
      [1, 2, 3],
      [null, 1, 2],
    ])
  })

  it('AC-152.5 after a finish the first waiting job reads 1 although two cards are above it', async () => {
    const positions = await positioner()
    const items = queue(['Done', 'Processing', 'Pending', 'Pending'], [0, 1, 2, 3])
    expect(rowsAndWaiting(positions(items), ['job-1', 'job-2', 'job-3', 'job-4'])).toEqual([
      [1, 2, 3, 4],
      [null, null, 1, 2],
    ])
  })

  it('AC-152.6 after a remove a gap in the stored positions still gives contiguous rows', async () => {
    const positions = await positioner()
    const items = queue(['Pending', 'Pending', 'Pending'], [0, 2, 5])
    expect(rowsAndWaiting(positions(items), ['job-1', 'job-2', 'job-3'])).toEqual([
      [1, 2, 3],
      [1, 2, 3],
    ])
  })

  it('AC-152.7 after a move the array order decides, not the stored position', async () => {
    const positions = await positioner()
    const items = queue(['Pending', 'Pending', 'Pending'], [2, 0, 1])
    expect(rowsAndWaiting(positions(items), ['job-1', 'job-2', 'job-3'])).toEqual([
      [1, 2, 3],
      [1, 2, 3],
    ])
  })

  it('AC-152.8 QueueCard shows the row and the waiting text, and keeps the old text without waitingPosition', async () => {
    await positioner()
    const { QueueCard } = await loadCard()
    const noop = (): void => undefined
    const base = { id: 'job-3', position: 3, status: 'Pending', title: 'clip.mp4' }
    const metaWith = (waitingPosition?: number): string => {
      const job = waitingPosition === undefined ? base : { ...base, waitingPosition }
      const view = render(createElement(QueueCard, { job, onOpen: noop }))
      expect(screen.getByTestId('queue-card-position').textContent).toBe('3')
      const text = screen.getByTestId('queue-card-meta').textContent ?? ''
      view.unmount()
      return text
    }
    const next = metaWith(1)
    expect(next).toBe('Waiting - next')
    const second = metaWith(2)
    expect(second).toBe('Waiting - 2 in line')
    expect(next).not.toContain('position')
    expect(second).not.toContain('position')
    expect(metaWith()).toBe('Waiting - position 3 in queue')
  })
})
