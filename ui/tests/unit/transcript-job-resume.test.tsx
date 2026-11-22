/** @vitest-environment jsdom */

/**
 * MEU-163 per-card Resume (AC-163.1 to AC-163.4). The rule and the menu are read
 * from their modules; the page is exercised against a stubbed fetch ledger, and
 * `resumeTranscriptJob` against a mocked `GET /transcripts` that stands for the
 * backend's truth. Every locator resolves inside its owning root (Session 24
 * RULE-1). The harness copies the shape of `transcript-page.behavior.test.ts`.
 */
import { QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, render, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { TranscriptPage } from '../../src/renderer/src/features/transcript/TranscriptPage'
import {
  CARD_ACTION_TESTIDS,
  cardLinkActions,
  cardMenuActions,
  TRANSCRIPT_MENU_ORDER,
} from '../../src/renderer/src/features/transcript/transcript-card'
import * as commands from '../../src/renderer/src/features/transcript/transcript-commands'
import {
  controlEnabled,
  type ProcessorState,
  type QueueControl,
} from '../../src/renderer/src/features/transcript/transcript-controls'
import { QUERY_KEY, type TranscriptListItem } from '../../src/renderer/src/features/transcript/useTranscriptQueue'
import { ApiError } from '../../src/renderer/src/lib/api'
import { queryClient } from '../../src/renderer/src/lib/query-client'

type Ledger = Array<{ url: string; method: string; body?: unknown }>

const RESUME_JOB = 'resume-job' as QueueControl

function item(
  overrides: Partial<TranscriptListItem> & Pick<TranscriptListItem, 'id' | 'channel_name' | 'status'>,
): TranscriptListItem {
  return {
    channel_url: `https://www.youtube.com/@${overrides.channel_name}`,
    output_dir: `C:/t/${overrides.channel_name}`,
    video_count: 0,
    transcripts_done: 0,
    word_count: 0,
    zip_path: null,
    last_title: null,
    last_item_status: null,
    last_item_message: null,
    queue_position: 1,
    error_message: null,
    compiled_path: null,
    ...overrides,
  }
}

function mockApi(): void {
  window.api = {
    getBackendUrl: async () => 'http://127.0.0.1:51234/api/v1',
    getToken: async () => 'gui-nonce',
    logStartupMetric: () => undefined,
    showDirectoryDialog: async () => undefined,
    showFileDialog: async () => undefined,
    showFilesDialog: async () => [],
    getPathForFile: () => '',
    openPath: async () => undefined,
    showItemInFolder: async () => undefined,
    readClipboardText: async () => '',
    writeClipboardText: async () => undefined,
    readTextFile: async () => ({ text: '', basename: 'x.txt' }),
    copyMcpConfig: async () => ({ ok: true as const }),
    subscribeLogs: () => () => undefined,
    getLogSnapshot: async () => [],
    getSetupReadiness: async () => ({ descriptorPresent: true, portOk: true, modelsDirWritable: true }),
    getMcpAccessStatus: async () => ({ tokenPresent: true }),
    captureRegion: async () => undefined,
    getHotkeyStatus: async () => ({ accelerator: 'F2', registered: true, inUse: false }),
    loginItemGet: async () => ({ supported: false, reason: 'not-packaged', enabled: false, minimized: false }),
    loginItemSet: async () => ({ supported: false, reason: 'not-packaged', enabled: false, minimized: false }),
    onInboxChanged: () => () => undefined,
  }
}

const fetches: Ledger = []
let items: TranscriptListItem[]
let processorState: ProcessorState
let resumeStatus: number

const path = (url: string): string => new URL(url).pathname.replace('/api/v1', '')
const requests = (method: string, pattern: RegExp): Ledger =>
  fetches.filter((row) => row.method === method && pattern.test(path(row.url)))

function envelopeOf(rows: TranscriptListItem[], state: ProcessorState): { items: TranscriptListItem[]; processor: { state: ProcessorState } } {
  return { items: rows.map((row) => ({ ...row })), processor: { state } }
}

beforeEach(() => {
  fetches.length = 0
  items = []
  processorState = 'Idle'
  resumeStatus = 200
  queryClient.clear()
  mockApi()
  vi.stubGlobal(
    'fetch',
    vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      const method = (init?.method ?? 'GET').toUpperCase()
      const body = init?.body ? (JSON.parse(String(init.body)) as unknown) : undefined
      fetches.push({ url, method, body })
      const p = path(url)
      if (p === '/settings/transcript') {
        return new Response(JSON.stringify({ delay_between_requests: 20 }), { status: 200 })
      }
      if (p === '/transcripts' && method === 'GET') {
        return new Response(JSON.stringify(envelopeOf(items, processorState)), { status: 200 })
      }
      if (p === '/transcripts/resume' && method === 'POST' && resumeStatus >= 400) {
        return new Response(
          JSON.stringify({ error: { code: 'CONFLICT', message: 'resume_processing requires Paused' } }),
          { status: resumeStatus },
        )
      }
      return new Response(JSON.stringify({}), { status: 200 })
    }),
  )
})

afterEach(() => {
  cleanup()
  queryClient.clear()
  vi.restoreAllMocks()
  vi.unstubAllGlobals()
})

describe('MEU-163 CARD_RESUME_RULE', () => {
  const a = item({ id: 'a', channel_name: 'Alpha', status: 'Paused', queue_position: 1 })
  const b = item({ id: 'b', channel_name: 'Bravo', status: 'Paused', queue_position: 2 })
  const c = item({ id: 'c', channel_name: 'Charlie', status: 'Done', queue_position: 3 })
  const ctx = (selectedId: string | null, state: ProcessorState, rows = [a, b, c]) => ({
    items: rows,
    selectedId,
    processorState: state,
  })

  it('AC-163.1 resume-job is enabled for the first Paused job while the processor is not Processing', () => {
    expect(controlEnabled(RESUME_JOB, ctx('a', 'Idle'))).toBe(true)
    expect(controlEnabled(RESUME_JOB, ctx('a', 'Paused'))).toBe(true)
    const x = item({ id: 'x', channel_name: 'Xray', status: 'Pending', queue_position: 1 })
    expect(controlEnabled(RESUME_JOB, ctx('a', 'Idle', [x, a]))).toBe(true)
  })

  it('AC-163.1 resume-job is disabled while Processing, for a later Paused job, a non-Paused job, no selection and an unknown id', () => {
    expect(controlEnabled(RESUME_JOB, ctx('a', 'Processing'))).toBe(false)
    expect(controlEnabled(RESUME_JOB, ctx('b', 'Idle'))).toBe(false)
    expect(controlEnabled(RESUME_JOB, ctx('c', 'Idle'))).toBe(false)
    expect(controlEnabled(RESUME_JOB, ctx(null, 'Idle'))).toBe(false)
    expect(controlEnabled(RESUME_JOB, ctx('zzz', 'Idle'))).toBe(false)
  })
})

describe('MEU-163 CARD_RESUME_MENU', () => {
  const a = item({ id: 'a', channel_name: 'Alpha', status: 'Paused', queue_position: 1 })
  const b = item({ id: 'b', channel_name: 'Bravo', status: 'Paused', queue_position: 2 })

  it('AC-163.2 resume-job leads the menu order and keeps its own test id', () => {
    expect([...TRANSCRIPT_MENU_ORDER]).toEqual([
      'resume-job',
      'requeue',
      'retry',
      'compile',
      'view-compiled',
      'open-zip',
      'open-folder',
      'remove',
    ])
    expect((CARD_ACTION_TESTIDS as Record<string, string>)['resume-job']).toBe('resume-job-btn')
  })

  it('AC-163.2 cardMenuActions offers resume-job only on the first Paused card, and no card links it', () => {
    const idle = { items: [a, b], processorState: 'Idle' as const }
    expect(cardMenuActions(a, idle)[0]).toBe('resume-job')
    expect(cardMenuActions(b, idle)).not.toContain('resume-job')
    expect(cardMenuActions(a, { items: [a, b], processorState: 'Processing' })).not.toContain('resume-job')
    expect(cardLinkActions(a, idle)).toEqual([])
    expect(cardLinkActions(b, idle)).toEqual([])
  })
})

describe('MEU-163 transcript page Resume item', () => {
  let user: ReturnType<typeof userEvent.setup>
  let host: HTMLElement

  beforeEach(() => {
    user = userEvent.setup()
  })

  async function renderPage(): Promise<void> {
    await act(async () => {
      host = render(createElement(QueryClientProvider, { client: queryClient }, createElement(TranscriptPage))).container
    })
    // Setup only: wait for the stubbed queue to load and the processor state to apply.
    const expected = items.length
    await vi.waitFor(() => {
      expect(fetches.some((row) => row.method === 'GET' && path(row.url) === '/transcripts')).toBe(true)
      expect(within(host).queryAllByTestId('channel-card')).toHaveLength(expected)
    })
    await act(async () => {
      await Promise.resolve()
    })
  }

  function card(name: string): HTMLElement {
    const found = within(host)
      .getAllByTestId('channel-card')
      .find((node) => node.textContent?.includes(name))
    if (found === undefined) {
      throw new Error(`no channel card for ${name}`)
    }
    return found
  }

  function toolbar(): HTMLElement {
    return within(within(host).getByTestId('queue-header-row')).getByRole('group', {
      name: 'Transcript queue actions',
    })
  }

  async function openMenu(name: string): Promise<HTMLElement> {
    await user.click(within(card(name)).getByTestId('queue-card-kebab'))
    return within(card(name)).getByTestId('queue-card-menu')
  }

  function menuIds(menu: HTMLElement): Array<string | null> {
    return within(menu)
      .getAllByRole('menuitem')
      .map((node) => node.getAttribute('data-testid'))
  }

  it('AC-163.3 the first Paused card offers Resume, which sends one bodyless resume; the toolbar is unchanged', async () => {
    items = [
      item({ id: 'a', channel_name: 'Alpha', status: 'Paused', queue_position: 1 }),
      item({ id: 'b', channel_name: 'Bravo', status: 'Paused', queue_position: 2 }),
      item({ id: 'c', channel_name: 'Charlie', status: 'Done', video_count: 2, transcripts_done: 2, queue_position: 3 }),
    ]
    processorState = 'Idle'
    await renderPage()
    const alphaMenu = await openMenu('Alpha')
    expect(menuIds(alphaMenu)[0]).toBe('resume-job-btn')
    const resume = within(alphaMenu).getByTestId('resume-job-btn')
    expect(resume.textContent).toBe('Resume')
    await user.keyboard('{Escape}')
    const bravoMenu = await openMenu('Bravo')
    expect(menuIds(bravoMenu)).not.toContain('resume-job-btn')
    await user.keyboard('{Escape}')
    const buttons = within(toolbar()).getAllByRole('button')
    expect(buttons.map((node) => node.getAttribute('data-testid'))).toEqual(['start-btn', 'pause-btn', 'stop-btn'])
    expect(within(host).queryByTestId('resume-btn')).toBeNull()
    await user.click(within(await openMenu('Alpha')).getByTestId('resume-job-btn'))
    await vi.waitFor(() => {
      expect(requests('POST', /^\/transcripts\/resume$/)).toHaveLength(1)
    })
    expect(requests('POST', /^\/transcripts\/resume$/)[0]?.body).toBeUndefined()
    const mutations = fetches.filter((row) => row.method !== 'GET')
    expect(mutations.map((row) => `${row.method} ${path(row.url)}`)).toEqual(['POST /transcripts/resume'])
  })

  it('AC-163.3 no card offers Resume while the processor is Processing', async () => {
    // Guard: the negative below is vacuous unless the menu knows the action.
    expect([...TRANSCRIPT_MENU_ORDER]).toContain('resume-job')
    items = [
      item({ id: 'a', channel_name: 'Alpha', status: 'Paused', queue_position: 1 }),
      item({ id: 'b', channel_name: 'Bravo', status: 'Processing', video_count: 4, queue_position: 2 }),
    ]
    processorState = 'Processing'
    await renderPage()
    for (const name of ['Alpha', 'Bravo']) {
      const menu = await openMenu(name)
      expect(menuIds(menu), name).not.toContain('resume-job-btn')
      await user.keyboard('{Escape}')
    }
    expect(within(host).queryAllByTestId('resume-job-btn')).toHaveLength(0)
  })
})

describe('MEU-163 CARD_RESUME_COMMAND', () => {
  const a = item({ id: 'a', channel_name: 'Alpha', status: 'Paused', queue_position: 1 })
  const b = item({ id: 'b', channel_name: 'Bravo', status: 'Paused', queue_position: 2 })

  type ResumeJob = (id: string) => Promise<void>

  function resumeJob(): ResumeJob {
    const fn = (commands as Record<string, unknown>).resumeTranscriptJob
    expect(typeof fn).toBe('function')
    return fn as ResumeJob
  }

  const gets = (): Ledger => requests('GET', /^\/transcripts$/)
  const resumes = (): Ledger => requests('POST', /^\/transcripts\/resume$/)

  it('AC-163.4 (a) a later Paused job sends one GET and no POST', async () => {
    const run = resumeJob()
    queryClient.setQueryData(QUERY_KEY, envelopeOf([a, b], 'Idle'))
    items = [a, b]
    processorState = 'Idle'
    await run('b')
    expect(gets()).toHaveLength(1)
    expect(resumes()).toHaveLength(0)
  })

  it('AC-163.4 (b) a backend that is Processing sends one GET and no POST', async () => {
    const run = resumeJob()
    queryClient.setQueryData(QUERY_KEY, envelopeOf([a, b], 'Idle'))
    items = [a, b]
    processorState = 'Processing'
    await run('a')
    expect(gets()).toHaveLength(1)
    expect(resumes()).toHaveLength(0)
  })

  it('AC-163.4 (c) the first Paused job while Idle sends one GET, then one bodyless POST', async () => {
    const run = resumeJob()
    queryClient.setQueryData(QUERY_KEY, envelopeOf([a, b], 'Idle'))
    items = [a, b]
    processorState = 'Idle'
    await run('a')
    expect(gets()).toHaveLength(1)
    expect(resumes()).toHaveLength(1)
    expect(resumes()[0]?.body).toBeUndefined()
    expect(fetches.map((row) => `${row.method} ${path(row.url)}`)).toEqual([
      'GET /transcripts',
      'POST /transcripts/resume',
    ])
  })

  it('AC-163.4 (d) a stale cache order never resumes; the cache takes the backend order', async () => {
    const run = resumeJob()
    queryClient.setQueryData(QUERY_KEY, envelopeOf([a, b], 'Idle'))
    items = [b, a]
    processorState = 'Idle'
    await run('a')
    expect(gets()).toHaveLength(1)
    expect(resumes()).toHaveLength(0)
    const cached = queryClient.getQueryData(QUERY_KEY) as { items: TranscriptListItem[] }
    expect(cached.items.map((row) => row.id)).toEqual(['b', 'a'])
  })

  it('AC-163.4 (e) a stale Processing cache never hides a valid resume', async () => {
    const run = resumeJob()
    queryClient.setQueryData(QUERY_KEY, envelopeOf([a], 'Processing'))
    items = [a]
    processorState = 'Idle'
    await run('a')
    expect(gets()).toHaveLength(1)
    expect(resumes()).toHaveLength(1)
    expect(resumes()[0]?.body).toBeUndefined()
  })

  it('AC-163.4 (f) a refused POST rejects with its ApiError and still invalidates the query', async () => {
    const run = resumeJob()
    queryClient.setQueryData(QUERY_KEY, envelopeOf([a, b], 'Idle'))
    items = [a, b]
    processorState = 'Idle'
    resumeStatus = 409
    const invalidate = vi.spyOn(queryClient, 'invalidateQueries')
    let caught: unknown = null
    try {
      await run('a')
    } catch (error) {
      caught = error
    }
    expect(caught).toBeInstanceOf(ApiError)
    expect((caught as ApiError).status).toBe(409)
    expect(resumes()).toHaveLength(1)
    expect(invalidate).toHaveBeenCalledWith({ queryKey: QUERY_KEY })
  })
})
