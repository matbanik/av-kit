/** @vitest-environment jsdom */

/**
 * MEU-156 (Session 89) — Cancel acts only while a job runs.
 *
 * While the queue is Paused no job runs and the services' cancel has nothing to
 * stop (Mat, 2026-11-17, D-1100), so the cancel control is disabled at Paused on
 * Convert and Downloader (`CANCEL_WHEN_RUNNING`). These tests pin the rule table
 * through `controlEnabled` and the commands' guard (`CANCEL_GUARD`): a cancel
 * command run against a cached Paused list sends no request.
 *
 * AC-156.5 to AC-156.10 live in the two page behaviour files; AC-156.11 and
 * AC-156.12 are Electron tests.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { cancelConversion } from '../../src/renderer/src/features/converter/convert-commands'
import {
  controlEnabled as convertControlEnabled,
  type QueueItemLike as ConvertItem,
} from '../../src/renderer/src/features/converter/convert-controls'
import { QUERY_KEY as CONVERT_KEY } from '../../src/renderer/src/features/converter/useConversionQueue'
import { cancelDownload } from '../../src/renderer/src/features/downloader/download-commands'
import {
  controlEnabled as downloadControlEnabled,
  type QueueItemLike as DownloadItem,
} from '../../src/renderer/src/features/downloader/download-controls'
import { QUERY_KEY as DOWNLOAD_KEY } from '../../src/renderer/src/features/downloader/useDownloadQueue'
import { queryClient } from '../../src/renderer/src/lib/query-client'

type Call = { method: string; path: string }
type State = 'Idle' | 'Processing' | 'Paused'

const calls: Call[] = []

beforeEach(() => {
  calls.length = 0
  queryClient.clear()
  window.api = {
    getBackendUrl: async () => 'http://127.0.0.1:51234/api/v1',
    getToken: async () => 'unit-nonce',
  } as unknown as typeof window.api
  vi.stubGlobal(
    'fetch',
    vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const method = (init?.method ?? 'GET').toUpperCase()
      const path = new URL(String(input)).pathname.replace(/^\/api\/v1/, '')
      calls.push({ method, path })
      return new Response(null, { status: 204 })
    }),
  )
})

afterEach(() => {
  vi.unstubAllGlobals()
  queryClient.clear()
})

const STATES: readonly State[] = ['Processing', 'Paused', 'Idle']

/** Today's values for the other controls, unchanged by MEU-156. */
const OTHERS: Record<'pause' | 'resume' | 'start', Record<State, boolean>> = {
  pause: { Processing: true, Paused: false, Idle: false },
  resume: { Processing: false, Paused: true, Idle: false },
  start: { Processing: false, Paused: true, Idle: true },
}

const CANCEL: Record<State, boolean> = { Processing: true, Paused: false, Idle: false }

function convertItem(id: string, status: string): ConvertItem {
  return { id, status, output_path: null, input_path: 'C:/in/' + id + '.mkv' }
}

function downloadItem(id: string, status: string): DownloadItem {
  return { id, status, file_path: null }
}

function posts(path: string): Call[] {
  return calls.filter((call) => call.method === 'POST' && call.path === path)
}

describe('MEU-156 cancel acts only while a job runs', () => {
  it('AC-156.1 Convert: cancel is enabled at Processing only, and pause, resume and start keep their values', () => {
    const items = [convertItem('c1', 'Processing'), convertItem('c2', 'Pending')]
    for (const processorState of STATES) {
      const ctx = { items, selectedId: 'c2', processorState, ffmpegAvailable: true }
      expect(convertControlEnabled('cancel', ctx), 'cancel at ' + processorState).toBe(CANCEL[processorState])
      for (const control of ['pause', 'resume', 'start'] as const) {
        expect(convertControlEnabled(control, ctx), control + ' at ' + processorState).toBe(
          OTHERS[control][processorState],
        )
      }
    }
  })

  it('AC-156.2 Downloader: cancel is enabled at Processing only, and pause, resume and start keep their values', () => {
    const items = [downloadItem('d1', 'Downloading'), downloadItem('d2', 'Pending')]
    for (const processorState of STATES) {
      const ctx = { items, selectedId: 'd2', processorState }
      expect(downloadControlEnabled('cancel', ctx), 'cancel at ' + processorState).toBe(CANCEL[processorState])
      for (const control of ['pause', 'resume', 'start'] as const) {
        expect(downloadControlEnabled(control, ctx), control + ' at ' + processorState).toBe(
          OTHERS[control][processorState],
        )
      }
    }
  })

  it('AC-156.3 cancelConversion sends nothing against a Paused list and POSTs once while a job runs', async () => {
    queryClient.setQueryData(CONVERT_KEY, {
      items: [convertItem('c1', 'Pending')],
      processor: { state: 'Paused', current_job_id: null },
    })
    await cancelConversion()
    expect(posts('/conversions/cancel'), 'no cancel POST while Paused').toHaveLength(0)
    expect(calls, 'no request at all while Paused').toHaveLength(0)

    queryClient.setQueryData(CONVERT_KEY, {
      items: [convertItem('c1', 'Processing')],
      processor: { state: 'Processing', current_job_id: 'c1' },
    })
    await cancelConversion()
    expect(posts('/conversions/cancel'), 'one cancel POST while a job runs').toHaveLength(1)
  })

  it('AC-156.4 cancelDownload sends nothing against a Paused list and POSTs once while a job runs', async () => {
    queryClient.setQueryData(DOWNLOAD_KEY, {
      items: [downloadItem('d1', 'Pending')],
      processor: { state: 'Paused', current_job_id: null },
    })
    await cancelDownload()
    expect(posts('/downloads/cancel'), 'no cancel POST while Paused').toHaveLength(0)
    expect(calls, 'no request at all while Paused').toHaveLength(0)

    queryClient.setQueryData(DOWNLOAD_KEY, {
      items: [downloadItem('d1', 'Downloading')],
      processor: { state: 'Processing', current_job_id: 'd1' },
    })
    await cancelDownload()
    expect(posts('/downloads/cancel'), 'one cancel POST while a job runs').toHaveLength(1)
  })
})
