/** @vitest-environment jsdom */

/**
 * MEU-49 — `REORDER_BODY_MODULE`.
 *
 * `buildReorderBody` is duplicated byte-for-byte in `convert-controls.ts` and
 * `download-controls.ts` today. A drag needs a third variant, and tripling a
 * triplicate is the defect, so the permutation builders move to one module and
 * both controls re-export it. These tests are the negative oracle for that
 * de-duplication: two copies that merely behave alike fail the identity
 * assertion in AC-49.3.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import * as convertCommands from '../../src/renderer/src/features/converter/convert-commands'
import * as convertControls from '../../src/renderer/src/features/converter/convert-controls'
import * as downloadCommands from '../../src/renderer/src/features/downloader/download-commands'
import * as downloadControls from '../../src/renderer/src/features/downloader/download-controls'
import { bulkReorder, type BulkReorderDeps } from '../../src/renderer/src/lib/queue/bulk-reorder'
import {
  buildReorderBody,
  buildReorderBodyToIndex,
} from '../../src/renderer/src/lib/queue/reorder-body'

/** The fixed fixture AC-49.4 compares against the pre-move implementation. */
const FIVE = ['a', 'b', 'c', 'd', 'e']

type WireCall = { url: string; method: string; body: unknown }

/**
 * Stand the renderer's fetch seam up so a command module can be called for
 * real and every request it issues — or does not issue — is counted.
 */
function installWire(calls: WireCall[]): void {
  Object.defineProperty(window, 'api', {
    configurable: true,
    value: {
      getBackendUrl: vi.fn(async () => 'http://127.0.0.1:51234/api/v1'),
      getToken: vi.fn(async () => 'gui-nonce'),
    },
  })
  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    let body: unknown
    if (typeof init?.body === 'string' && init.body.length > 0) {
      body = JSON.parse(init.body)
    }
    calls.push({ url: String(input), method: (init?.method ?? 'GET').toUpperCase(), body })
    return new Response(JSON.stringify({ items: [] }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    })
  })
  vi.stubGlobal('fetch', fetchMock)
  window.fetch = fetchMock as typeof window.fetch
}

describe('MEU-49 REORDER_BODY_MODULE', () => {
  const calls: WireCall[] = []

  beforeEach(() => {
    calls.length = 0
    installWire(calls)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

  it('AC-49.3 buildReorderBody has ONE owner and both controls re-export that same function', () => {
    // Reference identity, not behavioural equivalence: a second copy that
    // happens to compute the same permutation is exactly what this MEU removes.
    expect(convertControls.buildReorderBody).toBe(buildReorderBody)
    expect(downloadControls.buildReorderBody).toBe(buildReorderBody)
    expect(convertControls.buildReorderBody).toBe(downloadControls.buildReorderBody)
  })

  it('AC-49.4 every direction and the unknown-id branch are byte-identical to the pre-move builder', () => {
    expect(buildReorderBody(FIVE, 'c', 'up').job_ids).toEqual(['a', 'c', 'b', 'd', 'e'])
    expect(buildReorderBody(FIVE, 'c', 'down').job_ids).toEqual(['a', 'b', 'd', 'c', 'e'])
    expect(buildReorderBody(FIVE, 'c', 'top').job_ids).toEqual(['c', 'a', 'b', 'd', 'e'])
    expect(buildReorderBody(FIVE, 'c', 'bottom').job_ids).toEqual(['a', 'b', 'd', 'e', 'c'])

    // The two edges, where the pre-move implementation clamps with Math.max /
    // Math.min rather than running off the end of the array.
    expect(buildReorderBody(FIVE, 'a', 'up').job_ids).toEqual(FIVE)
    expect(buildReorderBody(FIVE, 'e', 'down').job_ids).toEqual(FIVE)

    // An unknown id yields an unchanged COPY — the same defensive shape the
    // pre-move implementation used, so callers can never mutate the input.
    const unknown = buildReorderBody(FIVE, 'zzz', 'top')
    expect(unknown.job_ids).toEqual(FIVE)
    expect(unknown.job_ids).not.toBe(FIVE)
  })

  it('AC-49.5 buildReorderBodyToIndex resolves targetIndex against the PRE-MOVE array', () => {
    // The three mandatory worked examples of MOVE_TO_INDEX_CONTRACT. The
    // forward case is the one that separates arrayMove semantics from a
    // remove-then-insert-at-the-post-removal-index implementation, which would
    // produce ['B','A','C','D'] here.
    expect(buildReorderBodyToIndex(['A', 'B', 'C', 'D'], 'A', 2).job_ids).toEqual([
      'B',
      'C',
      'A',
      'D',
    ])
    expect(buildReorderBodyToIndex(['A', 'B', 'C', 'D'], 'D', 1).job_ids).toEqual([
      'A',
      'D',
      'B',
      'C',
    ])
    expect(buildReorderBodyToIndex(['A', 'B', 'C'], 'A', 1).job_ids).toEqual(['B', 'A', 'C'])

    // Out of range clamps to [0, len-1]; it neither throws nor drops the row.
    expect(buildReorderBodyToIndex(FIVE, 'a', 99).job_ids).toEqual(['b', 'c', 'd', 'e', 'a'])
    expect(buildReorderBodyToIndex(FIVE, 'e', -7).job_ids).toEqual(['e', 'a', 'b', 'c', 'd'])

    const unknown = buildReorderBodyToIndex(FIVE, 'zzz', 1)
    expect(unknown.job_ids).toEqual(FIVE)
    expect(unknown.job_ids).not.toBe(FIVE)
  })

  it('AC-49.6 a self-drop is the identity permutation and issues NO request', async () => {
    expect(buildReorderBodyToIndex(FIVE, 'c', 2).job_ids).toEqual(FIVE)

    await downloadCommands.reorderDownloadToIndex(FIVE, 'c', 2)
    await convertCommands.reorderConversionToIndex(FIVE, 'c', 2)

    expect(
      calls.filter((call) => call.method === 'PUT' && call.url.includes('/reorder')),
      'a drop on the row itself changes nothing, so it may not reach the wire',
    ).toEqual([])
  })

  it('AC-49.7 every pre-existing import site still resolves through the re-exports', async () => {
    // The command modules and the bulk fold reach the builder through the
    // controls modules; a dropped re-export breaks them here as well as in tsc.
    expect(typeof downloadCommands.reorderDownload).toBe('function')
    expect(typeof downloadCommands.reorderDownloadOnly).toBe('function')
    expect(typeof convertCommands.reorderConversion).toBe('function')

    // Typed to the real collaborator signature rather than left to inference:
    // a bare `vi.fn(async () => undefined)` infers a ZERO-arg call tuple, so
    // `call[0]`/`call[1]` below become tuple-index type errors even though they
    // are exactly what the fold has to be checked on.
    const reorder = vi.fn<BulkReorderDeps['reorder']>(async () => undefined)
    const result = await bulkReorder(FIVE, ['b', 'd'], 'top', {
      reorder,
      buildBody: downloadControls.buildReorderBody,
    })

    // The fold is unchanged: one request per selected row, each folded from the
    // order the previous step produced, walked in reverse for the top edge.
    expect(reorder.mock.calls.map((call) => call[1])).toEqual(['d', 'b'])
    expect(reorder.mock.calls[0]?.[0]).toEqual(FIVE)
    expect(reorder.mock.calls[1]?.[0]).toEqual(['d', 'a', 'b', 'c', 'e'])
    expect(result.failed).toEqual([])
  })
})
