/**
 * MEU-46 — downloader control predicates and card meta (AC-46.2, AC-46.3).
 *
 * Two contracts share this file because they share one module:
 *
 * - **AC-46.2** widens `controlEnabled('reset')` from `Failed` alone to
 *   `DOWNLOAD_REQUEUEABLE_STATUSES`. The test enumerates the whole download
 *   status enum (`REQUEUE_EXHAUSTIVENESS_RULE`) so a future status cannot slip
 *   in unclassified, and asserts `Skipped` stays excluded (`USER_LOCKS` lock 4)
 *   — a skipped download was skipped because the file already exists, so
 *   offering Retry there would silently re-download over it.
 * - **AC-46.3** adds `downloadMetaSegments`, which carries the Quality/Speed/ETA
 *   columns of the deleted `DownloadQueueTable` onto the card's meta line. Speed
 *   and ETA are emitted whenever the field is non-null *regardless of status* —
 *   the backend never clears them (`services/download.py:559-568`) — and a null
 *   field yields no segment rather than a stray em dash.
 */

import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

import {
  JOB_STATUSES,
  controlEnabled,
  type ControlContext,
  type QueueItemLike,
} from '../../src/renderer/src/features/downloader/download-controls'

import type * as DownloadControlsModule from '../../src/renderer/src/features/downloader/download-controls'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')
const planDir = resolve(repoRoot, 'docs/execution/plans/2026-09-02-p10-queue-card-migration')

type NamedSet<T> = { value: T; complement?: T }
type NamedSets = {
  DOWNLOAD_REQUEUEABLE_STATUSES: NamedSet<string[]>
  DOWNLOAD_META_SEGMENTS: NamedSet<string[]>
}

const SETS = JSON.parse(readFileSync(resolve(planDir, 'named-sets.json'), 'utf-8')) as NamedSets

const REQUEUEABLE = SETS.DOWNLOAD_REQUEUEABLE_STATUSES.value
const NOT_REQUEUEABLE = SETS.DOWNLOAD_REQUEUEABLE_STATUSES.complement ?? []
const DOWNLOAD_META_SEGMENTS = SETS.DOWNLOAD_META_SEGMENTS.value

function loadControls(): Promise<typeof DownloadControlsModule> {
  return import(
    /* @vite-ignore */ '../../src/renderer/src/features/downloader/download-controls'
  ) as Promise<typeof DownloadControlsModule>
}

function item(overrides: Partial<QueueItemLike> = {}): QueueItemLike {
  return {
    id: 'dl-1',
    status: 'Pending',
    file_path: null,
    ...overrides,
  }
}

function context(status: string): ControlContext {
  return {
    items: [item({ status })],
    selectedId: 'dl-1',
    processorState: 'Idle',
  }
}

/** A download list row with every optional field null unless overridden. */
type DownloadRow = {
  quality: string
  speed: string | null
  eta: string | null
  status: string
  received_height: number | null
}

function row(overrides: Partial<DownloadRow> = {}): DownloadRow {
  return {
    quality: '1080p',
    speed: null,
    eta: null,
    status: 'Pending',
    received_height: null,
    ...overrides,
  }
}

describe('MEU-46 download-controls', () => {
  it('AC-46.2 controlEnabled(reset) is exactly DOWNLOAD_REQUEUEABLE_STATUSES over the full enum', () => {
    // REQUEUE_EXHAUSTIVENESS_RULE: every member of the enum is classified, so a
    // new status cannot arrive unclassified and silently default to disabled.
    const classified = [...REQUEUEABLE, ...NOT_REQUEUEABLE].sort()
    expect(classified, 'the named set partitions the whole download enum').toEqual(
      [...JOB_STATUSES].sort(),
    )

    for (const status of JOB_STATUSES) {
      const expected = REQUEUEABLE.includes(status)
      expect(controlEnabled('reset', context(status)), `reset on ${status}`).toBe(expected)
    }

    // USER_LOCKS lock 4, asserted explicitly rather than left to the partition:
    // a skipped download already exists on disk.
    expect(controlEnabled('reset', context('Skipped')), 'Skipped is locked out').toBe(false)

    // The three statuses MEU-46 widens in. The API answers 200 on
    // POST /downloads/{id}/reset for each; before MEU-46 only Failed offered it,
    // so a quality-blocked or age-restricted job was a dead end in the GUI.
    for (const widened of ['Cancelled', 'QualityBlocked', 'AgeRestricted']) {
      expect(controlEnabled('reset', context(widened)), `${widened} is widened in`).toBe(true)
    }

    // In-flight and finished rows are never re-queueable.
    for (const locked of ['Pending', 'Downloading', 'Done']) {
      expect(controlEnabled('reset', context(locked)), `${locked} stays locked`).toBe(false)
    }

    // With nothing selected there is nothing to re-queue.
    expect(
      controlEnabled('reset', {
        items: [item({ status: 'Failed' })],
        selectedId: null,
        processorState: 'Idle',
      }),
    ).toBe(false)
  })

  it('AC-46.3 downloadMetaSegments returns DOWNLOAD_META_SEGMENTS with null fields dropped', async () => {
    const { downloadMetaSegments } = await loadControls()
    expect(DOWNLOAD_META_SEGMENTS, 'quality, speed, eta').toHaveLength(3)

    // Quality always — it is the one field the deleted table's Quality column
    // rendered unconditionally.
    expect(downloadMetaSegments(row({ quality: '720p' }))).toEqual(['720p'])

    // Speed and ETA survive on a Done row — the backend does not clear them.
    expect(
      downloadMetaSegments(
        row({ quality: '1080p', status: 'Done', speed: '4.2MiB/s', eta: '00:00' }),
      ),
      'a finished row keeps its persisted speed and ETA',
    ).toEqual(['1080p', '4.2MiB/s', '00:00'])

    // An in-flight row carries all three in the same order.
    expect(
      downloadMetaSegments(
        row({ quality: '4k', status: 'Downloading', speed: '1.1MiB/s', eta: '02:13' }),
      ),
    ).toEqual(['4k', '1.1MiB/s', '02:13'])

    // A null field yields no segment at all — never an empty string, never '—'.
    const sparse = downloadMetaSegments(row({ quality: '480p', speed: null, eta: null }))
    expect(sparse, 'a queued row has neither speed nor ETA yet').toEqual(['480p'])
    expect(sparse.some((segment) => segment.trim() === '')).toBe(false)
    expect(sparse).not.toContain('—')

    // Speed without ETA (and the reverse) keeps ordering stable.
    expect(downloadMetaSegments(row({ quality: '720p', eta: '01:12' }))).toEqual([
      '720p',
      '01:12',
    ])
    expect(downloadMetaSegments(row({ quality: '720p', speed: '2.0MiB/s' }))).toEqual([
      '720p',
      '2.0MiB/s',
    ])

    // An empty quality string is dropped rather than rendered as a blank chip.
    expect(downloadMetaSegments(row({ quality: '', speed: '2.0MiB/s' }))).toEqual(['2.0MiB/s'])
  })
})

describe('MEU-124 download-controls', () => {
  it('AC-124.14 downloadMetaSegments shows the received quality next to the request when they differ', async () => {
    const { downloadMetaSegments } = await loadControls()
    const done = { status: 'Done', speed: '4.2MiB/s', eta: '00:00' }

    // SHOWN_WHEN_DIFFERENT: a received height that matches the request shows once.
    expect(downloadMetaSegments(row({ ...done, quality: '1080p', received_height: 1080 }))).toEqual([
      '1080p',
      '4.2MiB/s',
      '00:00',
    ])
    expect(downloadMetaSegments(row({ ...done, quality: '1080p', received_height: 360 }))).toEqual([
      '360p (asked 1080p)',
      '4.2MiB/s',
      '00:00',
    ])
    // A row without a received height shows its request, as before MEU-124.
    expect(downloadMetaSegments(row({ ...done, quality: '1080p', received_height: null }))).toEqual([
      '1080p',
      '4.2MiB/s',
      '00:00',
    ])
    expect(downloadMetaSegments(row({ ...done, quality: 'best', received_height: 1080 }))).toEqual([
      '1080p (asked best)',
      '4.2MiB/s',
      '00:00',
    ])
  })
})
