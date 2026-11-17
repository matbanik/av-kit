/** @vitest-environment jsdom */

/**
 * MEU-155 (Session 88) — queue pause feedback on the Convert and Downloader toolbars.
 *
 * A Pause click asks the backend to stop after the current job, and the backend
 * answers `Processing` until that job ends. These tests pin what the renderer
 * shows in that interval: the toggle reads "Pause after this job", then
 * `Pausing…` (disabled) while the pause is pending, then "Resume"; the chip
 * reads "Queue stops when the current job ends"; and the pending mark lives in
 * the shared query client (`lib/queue/pause-request.ts`), bound to the job that
 * was running when the pause was sent.
 *
 * `pause-request.ts` is new in this MEU, so it is loaded through
 * `import.meta.glob` and every test that uses it asserts its names first: at Red
 * each such test fails by assertion, never by a missing module. AC-155.7, .8,
 * .20 and .21 live in the two page behaviour files; AC-155.10 to .12 and .15 are
 * Electron tests; AC-155.16 to .18 are pytest.
 */

import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, fireEvent, render, renderHook, screen } from '@testing-library/react'
import type { ComponentProps, ReactElement, ReactNode } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import * as qt from '../../src/renderer/src/components/queue/QueueToolbar'
import * as convertCommands from '../../src/renderer/src/features/converter/convert-commands'
import { controlEnabled as convertControlEnabled } from '../../src/renderer/src/features/converter/convert-controls'
import {
  QUERY_KEY as CONVERT_KEY,
  parseListEnvelope as parseConvertEnvelope,
  useConversionQueue,
} from '../../src/renderer/src/features/converter/useConversionQueue'
import * as downloadCommands from '../../src/renderer/src/features/downloader/download-commands'
import { controlEnabled as downloadControlEnabled } from '../../src/renderer/src/features/downloader/download-controls'
import { DOWNLOADER_HELP_SECTIONS } from '../../src/renderer/src/features/downloader/downloader-help-content'
import {
  QUERY_KEY as DOWNLOAD_KEY,
  parseListEnvelope as parseDownloadEnvelope,
  useDownloadQueue,
} from '../../src/renderer/src/features/downloader/useDownloadQueue'
import { TranscriptToolbar } from '../../src/renderer/src/features/transcript/TranscriptToolbar'
import { apiFetch } from '../../src/renderer/src/lib/api'
import { queryClient } from '../../src/renderer/src/lib/query-client'

const here = dirname(fileURLToPath(import.meta.url))
const FIXTURE = resolve(here, 'fixtures/queue-slot-baseline.json')

// ---------------------------------------------------------------------------
// The new module, loaded without a static import (it does not exist at Red).
// ---------------------------------------------------------------------------

type QueueKind = 'convert' | 'download'
type Processor = { state: string; current_job_id?: string | null }
type PauseMark = { jobId: string | null; markedAt?: number }

type PauseRequestModule = {
  isPausePending: (mark: PauseMark | null, processor: Processor | undefined, now?: number) => boolean
  markPauseRequested: (kind: QueueKind, jobId: string | null) => void
  clearPauseRequest: (kind: QueueKind) => void
  readPauseRequest: (kind: QueueKind) => PauseMark | null
  usePausePending: (kind: QueueKind, processor: Processor | undefined) => boolean
  PAUSE_UNBOUND_MS: number
  PAUSE_PENDING_STATUS: string
}

const pqModules = import.meta.glob('../../src/renderer/src/lib/queue/pause-request.ts', { eager: true })
const pqLoaded = (Object.values(pqModules)[0] ?? {}) as Record<string, unknown>
const pq = pqLoaded as unknown as PauseRequestModule

const PQ_FUNCTIONS = [
  'isPausePending',
  'markPauseRequested',
  'clearPauseRequest',
  'readPauseRequest',
  'usePausePending',
] as const

/** Assert every name this file uses from `pause-request.ts` before it is used. */
function requirePauseRequest(): PauseRequestModule {
  for (const name of PQ_FUNCTIONS) {
    expect(typeof pqLoaded[name], `pause-request.ts exports ${name}`).toBe('function')
  }
  expect(typeof pqLoaded.PAUSE_UNBOUND_MS, 'pause-request.ts exports PAUSE_UNBOUND_MS').toBe('number')
  expect(typeof pqLoaded.PAUSE_PENDING_STATUS, 'pause-request.ts exports PAUSE_PENDING_STATUS').toBe(
    'string',
  )
  return pq
}

const HELP_PAUSE =
  'Pause after this job lets the current download finish, then stops the queue with its order intact; ' +
  'Resume continues later. Cancel stops the current download at once and does not delete finished files.'

const FAKED_TIMERS = ['setTimeout', 'clearTimeout', 'setInterval', 'clearInterval', 'Date'] as const

// ---------------------------------------------------------------------------
// The fetch stub: list reads, the pause POST, and every other POST.
// ---------------------------------------------------------------------------

type Call = { method: string; path: string }
type Responder = () => Response | Promise<Response>

const calls: Call[] = []
/** What `GET /conversions` and `GET /downloads` answer unless `listNext` holds a one-shot answer. */
let list: unknown = null
const listNext: Responder[] = []
let pauseStatus = 202

function jsonResponse(payload: unknown, status = 200): Response {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

function envelope(state: string, jobId: string | null): { items: unknown[]; processor: Processor } {
  return {
    items: [
      { id: jobId ?? 'running', status: state === 'Processing' ? 'Processing' : 'Pending' },
      { id: 'next', status: 'Pending' },
    ],
    processor: { state, current_job_id: jobId },
  }
}

function failed(): Response {
  return jsonResponse({ error: { code: 'INTERNAL', message: 'list failed' } }, 500)
}

/** A one-shot list answer held until `release` is called. */
function holdNextList(): { release: () => void } {
  let release: () => void = () => undefined
  const gate = new Promise<void>((done) => {
    release = done
  })
  listNext.push(async () => {
    await gate
    return jsonResponse(list)
  })
  return { release: () => release() }
}

function sent(method: string, path: string): Call[] {
  return calls.filter((call) => call.method === method && call.path === path)
}

beforeEach(() => {
  calls.length = 0
  listNext.length = 0
  list = null
  pauseStatus = 202
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
      if (method === 'GET' && (path === '/conversions' || path === '/downloads')) {
        const next = listNext.shift()
        return next !== undefined ? next() : jsonResponse(list)
      }
      if (method === 'POST' && path.endsWith('/pause') && pauseStatus >= 400) {
        return jsonResponse({ error: { code: 'INTERNAL', message: 'pause failed' } }, pauseStatus)
      }
      return new Response(null, { status: method === 'POST' ? 202 : 204 })
    }),
  )
})

afterEach(() => {
  cleanup()
  vi.useRealTimers()
  vi.unstubAllGlobals()
  queryClient.clear()
})

/** Let fetches, query notifications and effects run, under real or fake timers. */
async function settle(rounds = 6): Promise<void> {
  for (let n = 0; n < rounds; n += 1) {
    await act(async () => {
      if (vi.isFakeTimers()) {
        await vi.advanceTimersByTimeAsync(0)
      } else {
        await new Promise((done) => setTimeout(done, 0))
      }
    })
  }
}

// ---------------------------------------------------------------------------
// The two queue kinds, so AC-155.4/.5, .14, .19 and .22 run once per kind.
// ---------------------------------------------------------------------------

type KindSpec = {
  kind: QueueKind
  base: '/conversions' | '/downloads'
  key: readonly string[]
  /** [the job running when the pause is sent, another job, an older list's job] */
  ids: readonly [string, string, string]
  pause: () => Promise<void>
  start: () => Promise<void>
  resume: () => Promise<void>
  cancel: () => Promise<void>
  parse: (data: unknown) => { processor: Processor }
  pauseEnabled: (data: unknown) => boolean
  useQueue: () => { data?: { processor: Processor } }
}

const CONVERT: KindSpec = {
  kind: 'convert',
  base: '/conversions',
  key: CONVERT_KEY,
  ids: ['c1', 'c2', 'c0'],
  pause: () => convertCommands.pauseConversion(),
  start: () => convertCommands.startConversion(),
  resume: () => convertCommands.resumeConversion(),
  cancel: () => convertCommands.cancelConversion(),
  parse: (data) => parseConvertEnvelope(data),
  pauseEnabled: (data) => {
    const env = parseConvertEnvelope(data)
    return convertControlEnabled('pause', {
      items: env.items,
      selectedId: null,
      processorState: env.processor.state,
      ffmpegAvailable: true,
    })
  },
  useQueue: () => useConversionQueue(),
}

const DOWNLOAD: KindSpec = {
  kind: 'download',
  base: '/downloads',
  key: DOWNLOAD_KEY,
  ids: ['d1', 'd2', 'd0'],
  pause: () => downloadCommands.pauseDownload(),
  start: () => downloadCommands.startDownload(),
  resume: () => downloadCommands.resumeDownload(),
  cancel: () => downloadCommands.cancelDownload(),
  parse: (data) => parseDownloadEnvelope(data),
  pauseEnabled: (data) => {
    const env = parseDownloadEnvelope(data)
    return downloadControlEnabled('pause', {
      items: env.items,
      selectedId: null,
      processorState: env.processor.state,
    })
  },
  useQueue: () => useDownloadQueue(),
}

function seed(spec: KindSpec, state: string, jobId: string | null): void {
  queryClient.setQueryData(spec.key, envelope(state, jobId))
}

function cachedProcessor(spec: KindSpec): Processor | undefined {
  const data = queryClient.getQueryData(spec.key)
  return data === undefined ? undefined : spec.parse(data).processor
}

function wrapper({ children }: { children: ReactNode }): ReactElement {
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
}

/** The real queue hook plus `usePausePending`, as each page wires them. */
function Probe({ spec }: { spec: KindSpec }): ReactElement {
  const queue = spec.useQueue()
  const pending = pq.usePausePending(spec.kind, queue.data?.processor)
  return <output data-testid="pause-probe">{pending ? 'pending' : 'idle'}</output>
}

function mountProbe(spec: KindSpec): ReturnType<typeof render> {
  return render(<Probe spec={spec} />, { wrapper })
}

function probeText(view: ReturnType<typeof render>): string | null {
  return view.getByTestId('pause-probe').textContent
}

// ---------------------------------------------------------------------------
// The toolbar.
// ---------------------------------------------------------------------------

type ToolbarProps = ComponentProps<typeof qt.QueueToolbar>

function renderToolbar(props: Partial<ToolbarProps>): { onPauseResume: ReturnType<typeof vi.fn> } {
  const onPauseResume = vi.fn()
  render(
    <qt.QueueToolbar
      processorState="Processing"
      onStart={vi.fn()}
      onPauseResume={onPauseResume}
      onClearFinished={vi.fn()}
      onClearAll={vi.fn()}
      {...props}
    />,
  )
  return { onPauseResume }
}

describe('MEU-155 the pause toggle', () => {
  it('AC-155.1 the toggle reads "Pause after this job" while processing and "Resume" while paused', () => {
    expect(qt.TOOLBAR_CONTROL_LABELS.pause).toBe('Pause after this job')
    expect(qt.TOOLBAR_CONTROL_LABELS.resume).toBe('Resume')

    renderToolbar({ processorState: 'Processing', canPauseResume: true })
    const pause = screen.getByTestId('queue-toolbar-pause')
    expect(pause).toBeEnabled()
    expect(pause.textContent).toBe('Pause after this job')
    cleanup()

    renderToolbar({ processorState: 'Paused', canPauseResume: true })
    const resume = screen.getByTestId('queue-toolbar-resume')
    expect(resume).toBeEnabled()
    expect(resume.textContent).toBe('Resume')
  })

  it('AC-155.2 a pending pause shows Pausing…, disabled, at a fixed width; the other controls keep theirs', () => {
    const exports = qt as unknown as Record<string, unknown>
    expect(exports.PAUSE_PENDING_LABEL, 'QueueToolbar exports PAUSE_PENDING_LABEL').toBe('Pausing…')
    expect(exports.PAUSE_TOGGLE_WIDTH_CLASSES, 'QueueToolbar exports PAUSE_TOGGLE_WIDTH_CLASSES').toBe(
      'min-w-[12rem] justify-center',
    )
    const widthClasses = String(exports.PAUSE_TOGGLE_WIDTH_CLASSES)
    const common = { canStart: false, canClearFinished: true, canClearAll: false, canPauseResume: true }

    function checkOthers(): void {
      const start = screen.getByTestId('queue-toolbar-start')
      const clearFinished = screen.getByTestId('queue-toolbar-clear-finished')
      expect(start).toBeDisabled()
      expect(clearFinished).toBeEnabled()
      fireEvent.click(screen.getByTestId('queue-toolbar-overflow'))
      const clearAll = screen.getByTestId('queue-toolbar-clear-all')
      expect(clearAll).toBeDisabled()
      for (const control of [start, clearFinished, clearAll]) {
        expect(control.className, `${control.dataset.testid} has no min-width`).not.toContain('min-w-')
      }
    }

    // Pending while Processing: same test id, the Pause icon, Pausing…, disabled.
    const pending = renderToolbar({ ...common, processorState: 'Processing', pausePending: true } as Partial<ToolbarProps>)
    const toggle = screen.getByTestId('queue-toolbar-pause')
    expect(toggle.textContent).toBe('Pausing…')
    expect(toggle.querySelector('svg.lucide-pause'), 'the Pause icon stays').not.toBeNull()
    expect(toggle).toBeDisabled()
    expect(toggle.className).toContain(widthClasses)
    fireEvent.click(toggle)
    expect(pending.onPauseResume).not.toHaveBeenCalled()
    checkOthers()
    cleanup()

    // Paused ignores pending.
    renderToolbar({ ...common, processorState: 'Paused', pausePending: true } as Partial<ToolbarProps>)
    const resume = screen.getByTestId('queue-toolbar-resume')
    expect(resume).toBeEnabled()
    expect(resume.textContent).toBe('Resume')
    expect(resume.className).toContain(widthClasses)
    checkOthers()
    cleanup()

    // pausePending omitted: today's toggle plus the width classes.
    renderToolbar({ ...common, processorState: 'Processing' })
    const plain = screen.getByTestId('queue-toolbar-pause')
    expect(plain).toBeEnabled()
    expect(plain.textContent).toBe('Pause after this job')
    expect(plain.className).toContain(widthClasses)
    checkOthers()
  })
})

describe('MEU-155 the pause mark', () => {
  it('AC-155.3 isPausePending, the mark store and the pending status text', () => {
    const p = requirePauseRequest()
    expect(p.PAUSE_UNBOUND_MS).toBe(15000)
    expect(p.PAUSE_PENDING_STATUS).toBe('Queue stops when the current job ends')

    const t = 1_700_000_000_000
    const processing = (id: string | null): Processor => ({ state: 'Processing', current_job_id: id })
    const bound: PauseMark = { jobId: 'j1' }
    const unbound: PauseMark = { jobId: null, markedAt: t }

    expect(p.isPausePending(null, processing('j1'), t), 'no mark').toBe(false)
    expect(p.isPausePending(bound, undefined, t), 'bound mark, no list').toBe(false)
    expect(p.isPausePending(unbound, undefined, t + 1000), 'unbound mark, no list').toBe(false)
    expect(p.isPausePending(bound, processing('j1'), t), 'j1 running').toBe(true)
    expect(p.isPausePending(bound, processing(null), t), 'no job id yet').toBe(true)
    expect(p.isPausePending(bound, processing('j2'), t), 'another job').toBe(false)
    expect(p.isPausePending(bound, { state: 'Paused', current_job_id: null }, t), 'Paused').toBe(false)
    expect(p.isPausePending(bound, { state: 'Idle', current_job_id: null }, t), 'Idle').toBe(false)
    expect(p.isPausePending(unbound, processing(null), t + 1000), 'unbound, no id, in bound').toBe(true)
    expect(p.isPausePending(unbound, processing('j2'), t + 1000), 'unbound, an id, in bound').toBe(true)
    expect(p.isPausePending(unbound, processing(null), t + p.PAUSE_UNBOUND_MS), 'unbound, at bound').toBe(false)
    expect(p.isPausePending(unbound, processing('j2'), t + p.PAUSE_UNBOUND_MS), 'unbound id, at bound').toBe(false)
    expect(p.isPausePending(unbound, { state: 'Paused', current_job_id: null }, t + 1000), 'unbound, Paused').toBe(
      false,
    )

    p.markPauseRequested('convert', 'j1')
    expect(p.readPauseRequest('convert')).toStrictEqual({ jobId: 'j1' })
    expect(p.readPauseRequest('download')).toBeNull()
    p.clearPauseRequest('convert')
    expect(p.readPauseRequest('convert')).toBeNull()

    vi.useFakeTimers({ toFake: [...FAKED_TIMERS] })
    vi.setSystemTime(t)
    p.markPauseRequested('convert', null)
    expect(p.readPauseRequest('convert')).toStrictEqual({ jobId: null, markedAt: t })
    p.clearPauseRequest('convert')
    expect(p.readPauseRequest('convert')).toBeNull()

    // No observer, past the default five-minute gcTime: the mark stays.
    p.markPauseRequested('download', 'j1')
    vi.advanceTimersByTime(10 * 60 * 1000)
    expect(p.readPauseRequest('download')).toStrictEqual({ jobId: 'j1' })
  })

  for (const [ac, spec] of [
    ['AC-155.4', CONVERT],
    ['AC-155.5', DOWNLOAD],
  ] as const) {
    it(`${ac} ${spec.kind}: pause POSTs, reads the list, marks the running job; start, resume and cancel clear it`, async () => {
      const p = requirePauseRequest()
      const [running, , older] = spec.ids

      // The pause: POST, then the list read, then the mark from that read.
      seed(spec, 'Processing', running)
      list = envelope('Processing', running)
      await spec.pause()
      expect(calls.map((call) => `${call.method} ${call.path}`)).toEqual([
        `POST ${spec.base}/pause`,
        `GET ${spec.base}`,
      ])
      expect(p.readPauseRequest(spec.kind)).toStrictEqual({ jobId: running })
      const before = calls.length
      await spec.pause()
      expect(calls, 'a second pause while pending sends nothing').toHaveLength(before)

      // Ordering: an older list read in flight before the pause cannot land over the read after it.
      queryClient.clear()
      calls.length = 0
      seed(spec, 'Processing', running)
      const held = holdNextList()
      list = envelope('Processing', older)
      const early = queryClient
        .fetchQuery({
          queryKey: spec.key,
          queryFn: async () => spec.parse(await apiFetch<unknown>(spec.base)),
        })
        .catch(() => undefined)
      await vi.waitFor(() => expect(sent('GET', spec.base)).toHaveLength(1))
      const answered = { ...envelope('Processing', running) }
      listNext.push(() => jsonResponse(answered))
      await spec.pause()
      held.release()
      await early
      await settle(2)
      expect(cachedProcessor(spec)).toEqual({ state: 'Processing', current_job_id: running })

      // A failed POST: the call rejects and no mark is set.
      queryClient.clear()
      calls.length = 0
      seed(spec, 'Processing', running)
      list = envelope('Processing', running)
      pauseStatus = 500
      await expect(spec.pause()).rejects.toThrow()
      expect(p.readPauseRequest(spec.kind)).toBeNull()
      pauseStatus = 202

      // Cancel while Processing clears the mark.
      seed(spec, 'Processing', running)
      p.markPauseRequested(spec.kind, running)
      await spec.cancel()
      expect(sent('POST', `${spec.base}/cancel`)).toHaveLength(1)
      expect(p.readPauseRequest(spec.kind)).toBeNull()

      // Start from Paused with a Pending item clears it.
      seed(spec, 'Paused', null)
      p.markPauseRequested(spec.kind, running)
      await spec.start()
      expect(sent('POST', `${spec.base}/start`)).toHaveLength(1)
      expect(p.readPauseRequest(spec.kind)).toBeNull()

      // Resume from Paused clears it.
      seed(spec, 'Paused', null)
      p.markPauseRequested(spec.kind, running)
      await spec.resume()
      expect(sent('POST', `${spec.base}/resume`)).toHaveLength(1)
      expect(p.readPauseRequest(spec.kind)).toBeNull()
    })
  }

  it('AC-155.6 usePausePending binds, clears and expires the mark as the processor moves', async () => {
    const p = requirePauseRequest()
    vi.useFakeTimers({ toFake: [...FAKED_TIMERS] })
    vi.setSystemTime(1_700_000_000_000)
    const processing = (id: string | null): Processor => ({ state: 'Processing', current_job_id: id })

    const { result, rerender } = renderHook(
      ({ processor }: { processor: Processor | undefined }) => p.usePausePending('convert', processor),
      { initialProps: { processor: processing('c1') as Processor | undefined }, wrapper },
    )
    await settle()
    expect(result.current, 'no mark').toBe(false)

    act(() => {
      p.markPauseRequested('convert', 'c1')
    })
    await settle()
    expect(result.current, 'c1 marked, c1 running').toBe(true)

    rerender({ processor: undefined })
    await settle()
    expect(result.current, 'no list yet').toBe(false)
    expect(p.readPauseRequest('convert'), 'a missing list keeps the mark').toStrictEqual({ jobId: 'c1' })

    rerender({ processor: { state: 'Paused', current_job_id: null } })
    await settle()
    expect(result.current, 'Paused').toBe(false)
    expect(p.readPauseRequest('convert'), 'Paused clears the mark').toBeNull()

    rerender({ processor: processing('c2') })
    act(() => {
      p.markPauseRequested('convert', 'c1')
    })
    await settle()
    expect(result.current, 'c1 marked, c2 running').toBe(false)
    expect(p.readPauseRequest('convert'), 'another job clears the mark').toBeNull()

    rerender({ processor: { state: 'Idle', current_job_id: null } })
    act(() => {
      p.markPauseRequested('convert', 'c1')
    })
    await settle()
    expect(result.current, 'Idle').toBe(false)
    expect(p.readPauseRequest('convert'), 'Idle clears the mark').toBeNull()

    // An unbound mark binds to the first job id the list shows, then ends with that job.
    rerender({ processor: processing(null) })
    act(() => {
      p.markPauseRequested('convert', null)
    })
    await settle()
    expect(result.current, 'unbound, no id').toBe(true)
    expect(p.readPauseRequest('convert')?.jobId, 'the mark stays unbound').toBeNull()
    rerender({ processor: processing('c5') })
    await settle()
    expect(result.current, 'bound to c5').toBe(true)
    expect(p.readPauseRequest('convert')).toStrictEqual({ jobId: 'c5' })
    rerender({ processor: processing('c6') })
    await settle()
    expect(result.current, 'c5 ended, c6 running').toBe(false)
    expect(p.readPauseRequest('convert')).toBeNull()

    // An unbound mark that never binds ends at its bound without a rerender.
    rerender({ processor: processing(null) })
    act(() => {
      p.markPauseRequested('convert', null)
    })
    await settle()
    expect(result.current, 'second unbound mark').toBe(true)
    await act(async () => {
      await vi.advanceTimersByTimeAsync(p.PAUSE_UNBOUND_MS)
    })
    await settle()
    expect(result.current, 'the unbound mark expired').toBe(false)
    expect(p.readPauseRequest('convert')).toBeNull()
  })

  it('AC-155.9 the queue-slot fixture pins the new label', () => {
    const fixture = readFileSync(FIXTURE, 'utf-8')
    expect(fixture.split('Pause after this job</button>')).toHaveLength(2)
    expect(fixture.includes('>Pause</button>'), 'no bare Pause label').toBe(false)
  })

  it('AC-155.13 Transcript keeps "Pause"; the Downloader help explains Pause after this job', () => {
    const noop = (): void => undefined
    const props = {
      canStart: true,
      canPause: true,
      canResume: true,
      canStop: true,
      onStart: noop,
      onPause: noop,
      onResume: noop,
      onStop: noop,
    }
    render(<TranscriptToolbar processorState="Processing" {...props} />)
    expect(screen.getByTestId('pause-btn').textContent?.trim()).toBe('Pause')
    cleanup()
    render(<TranscriptToolbar processorState="Paused" {...props} />)
    expect(screen.getByTestId('resume-btn').textContent?.trim()).toBe('Resume')

    const topic = DOWNLOADER_HELP_SECTIONS.find((section) => section.id === 'pause')
    expect(topic?.title).toBe('Pause vs cancel')
    expect(topic?.body).toBe(HELP_PAUSE)
  })

  for (const spec of [CONVERT, DOWNLOAD]) {
    it(`AC-155.14 ${spec.kind}: the list read after the pause POST decides the mark`, async () => {
      const p = requirePauseRequest()
      const [running, other] = spec.ids

      // Another job is running by the time of the read: the mark names it.
      seed(spec, 'Processing', running)
      list = envelope('Processing', other)
      await spec.pause()
      expect(p.readPauseRequest(spec.kind)).toStrictEqual({ jobId: other })
      expect(cachedProcessor(spec)).toEqual({ state: 'Processing', current_job_id: other })
      expect(
        p.isPausePending(p.readPauseRequest(spec.kind), { state: 'Processing', current_job_id: other }),
      ).toBe(true)

      // No job id yet: an unbound mark, stamped now.
      queryClient.clear()
      vi.useFakeTimers({ toFake: [...FAKED_TIMERS] })
      vi.setSystemTime(1_700_000_000_000)
      seed(spec, 'Processing', running)
      list = envelope('Processing', null)
      await spec.pause()
      expect(p.readPauseRequest(spec.kind)).toStrictEqual({ jobId: null, markedAt: Date.now() })
      vi.useRealTimers()

      // Already Paused: no mark, and the cache shows Paused.
      queryClient.clear()
      seed(spec, 'Processing', running)
      list = envelope('Paused', null)
      await spec.pause()
      expect(p.readPauseRequest(spec.kind)).toBeNull()
      expect(cachedProcessor(spec)?.state).toBe('Paused')

      // The read fails: no mark, the call resolves, the list is invalidated, Pause stays usable.
      queryClient.clear()
      calls.length = 0
      seed(spec, 'Processing', running)
      list = envelope('Processing', running)
      listNext.push(failed)
      await expect(spec.pause()).resolves.toBeUndefined()
      expect(p.readPauseRequest(spec.kind)).toBeNull()
      expect(queryClient.getQueryState(spec.key)?.isInvalidated, 'the list is invalidated').toBe(true)
      await spec.pause()
      expect(sent('POST', `${spec.base}/pause`)).toHaveLength(2)
    })
  }

  for (const spec of [CONVERT, DOWNLOAD]) {
    it(`AC-155.19 ${spec.kind}: a remount after the list was collected keeps the mark`, async () => {
      const p = requirePauseRequest()
      const [running] = spec.ids
      vi.useFakeTimers({ toFake: [...FAKED_TIMERS] })
      vi.setSystemTime(1_700_000_000_000)
      list = envelope('Processing', running)

      const first = mountProbe(spec)
      await settle()
      expect(cachedProcessor(spec)?.current_job_id).toBe(running)
      act(() => {
        p.markPauseRequested(spec.kind, running)
      })
      await settle()
      expect(probeText(first)).toBe('pending')
      first.unmount()

      await act(async () => {
        await vi.advanceTimersByTimeAsync(6 * 60 * 1000)
      })
      expect(queryClient.getQueryData(spec.key), 'the list was collected').toBeUndefined()
      expect(p.readPauseRequest(spec.kind)).toStrictEqual({ jobId: running })

      const held = holdNextList()
      const second = mountProbe(spec)
      await settle()
      expect(probeText(second), 'no list yet').toBe('idle')
      expect(p.readPauseRequest(spec.kind), 'the mark waits for the list').toStrictEqual({ jobId: running })

      held.release()
      await settle()
      expect(probeText(second), 'pending again once the list reads the same job').toBe('pending')
    })
  }

  for (const spec of [CONVERT, DOWNLOAD]) {
    it(`AC-155.22 ${spec.kind}: a spent pause does not block the next one`, async () => {
      const p = requirePauseRequest()
      const [running, next] = spec.ids
      vi.useFakeTimers({ toFake: [...FAKED_TIMERS] })
      vi.setSystemTime(1_700_000_000_000)

      // (a) The read after the POST fails; another client pauses and resumes unseen.
      seed(spec, 'Processing', running)
      list = envelope('Processing', running)
      const a1 = mountProbe(spec)
      await settle()
      listNext.push(failed)
      await act(async () => {
        await spec.pause()
      })
      await settle()
      expect(p.readPauseRequest(spec.kind), '(a) no mark after a failed read').toBeNull()
      a1.unmount()
      // Another client paused and resumed while no probe was mounted; the list now runs the next job.
      list = envelope('Processing', next)
      const a2 = mountProbe(spec)
      await settle()
      expect(cachedProcessor(spec)?.current_job_id).toBe(next)
      expect(probeText(a2), '(a) not pending for the next job').toBe('idle')
      expect(spec.pauseEnabled(queryClient.getQueryData(spec.key)), '(a) Pause is enabled').toBe(true)
      await act(async () => {
        await spec.pause()
      })
      expect(sent('POST', `${spec.base}/pause`), '(a) Pause POSTs again').toHaveLength(2)
      a2.unmount()

      // (b) The read shows no job id (an unbound mark); it expires while no page is mounted.
      queryClient.clear()
      p.clearPauseRequest(spec.kind)
      calls.length = 0
      seed(spec, 'Processing', running)
      list = envelope('Processing', running)
      const b1 = mountProbe(spec)
      await settle()
      list = envelope('Processing', null)
      await act(async () => {
        await spec.pause()
      })
      await settle()
      expect(p.readPauseRequest(spec.kind)?.jobId, '(b) an unbound mark').toBeNull()
      expect(p.readPauseRequest(spec.kind), '(b) an unbound mark').not.toBeNull()
      b1.unmount()
      await act(async () => {
        await vi.advanceTimersByTimeAsync(20_000)
      })
      // Another client paused and resumed while no probe was mounted; the list now runs the next job.
      list = envelope('Processing', next)
      const b2 = mountProbe(spec)
      await settle()
      expect(cachedProcessor(spec)?.current_job_id).toBe(next)
      expect(probeText(b2), '(b) not pending for the next job').toBe('idle')
      expect(p.readPauseRequest(spec.kind), '(b) the spent mark is cleared').toBeNull()
      expect(spec.pauseEnabled(queryClient.getQueryData(spec.key)), '(b) Pause is enabled').toBe(true)
      await act(async () => {
        await spec.pause()
      })
      expect(sent('POST', `${spec.base}/pause`), '(b) Pause POSTs again').toHaveLength(2)
      b2.unmount()
    })
  }
})
