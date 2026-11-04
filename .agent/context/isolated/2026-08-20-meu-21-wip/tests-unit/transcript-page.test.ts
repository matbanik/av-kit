import { existsSync, readdirSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')
const transcriptDir = resolve(repoRoot, 'ui/src/renderer/src/features/transcript')
const pagePath = resolve(transcriptDir, 'TranscriptPage.tsx')
const routerPath = resolve(repoRoot, 'ui/src/renderer/src/router.tsx')
const appShellPath = resolve(repoRoot, 'ui/src/renderer/src/components/layout/AppShell.tsx')
const registryPath = resolve(repoRoot, 'ui/src/renderer/src/registry/commandRegistry.ts')
const testIdsPath = resolve(repoRoot, 'ui/tests/e2e/test-ids.ts')
const stylesPath = resolve(repoRoot, 'ui/src/renderer/src/styles.css')
const apiTranscriptsPath = resolve(repoRoot, 'packages/api/src/avkit_api/routes/transcripts.py')
const mcpDir = resolve(repoRoot, 'mcp-server')
const WAVE2_TESTIDS = [
  'transcript-page',
  'channel-input',
  'channel-card',
  'compile-btn',
  'channel-progress',
] as const

const WAVE2_EXTRA_TESTIDS = [
  'add-btn',
  'start-btn',
  'pause-btn',
  'resume-btn',
  'stop-btn',
  'up-btn',
  'down-btn',
  'remove-btn',
  'requeue-btn',
  'retry-btn',
  'view-compiled-btn',
  'open-zip-btn',
  'open-folder-btn',
  'processor-indicator',
  'output-tree',
  'rate-display',
  'eta-display',
  'last-title',
  'channel-url-hint',
  'remove-confirm-btn',
  'remove-confirm-cancel',
] as const

const TRANSCRIPT_PALETTE_IDS = [
  'transcript:add',
  'transcript:start',
  'transcript:pause',
  'transcript:resume',
  'transcript:stop',
] as const

function readRequired(path: string): string {
  expect(existsSync(path), path).toBe(true)
  return readFileSync(path, 'utf8')
}

function transcriptSources(): string[] {
  expect(existsSync(transcriptDir), transcriptDir).toBe(true)
  return readdirSync(transcriptDir)
    .filter((name) => name.endsWith('.ts') || name.endsWith('.tsx'))
    .map((name) => readFileSync(resolve(transcriptDir, name), 'utf8'))
}

describe('MEU-21 transcript', () => {
  it('AC-21.1 TRANSCRIPT_HOME routes /transcript to TranscriptPage', () => {
    const src = readRequired(routerPath)
    expect(src).toMatch(/TranscriptPage/)
    expect(src).not.toMatch(/path:\s*'\/transcript'[\s\S]{0,80}LazyPlaceholder/)
    const page = readRequired(pagePath)
    expect(page).toContain('transcript-page')
    expect(page).toContain('channel-input')
    expect(page).not.toMatch(/Connecting to backend/)
  })

  it('AC-21.2 CREATE_BODY is channel_url only', async () => {
    const mod = await import('../../src/renderer/src/features/transcript/transcript-commands')
    expect(mod.createTranscriptBody('')).toBeNull()
    const body = mod.createTranscriptBody('https://www.youtube.com/@e2e-invalid')
    expect(body).toEqual({ channel_url: 'https://www.youtube.com/@e2e-invalid' })
    expect(Object.keys(body ?? {})).toEqual(['channel_url'])
    expect(body).not.toHaveProperty('cookies')
  })

  it('AC-21.3 LIST_ENVELOPE and QUERY_KEY reject a bare array', async () => {
    const mod = await import('../../src/renderer/src/features/transcript/useTranscriptQueue')
    expect(mod.QUERY_KEY).toEqual(['transcripts'])
    expect(() => mod.parseListEnvelope([])).toThrow()
    const parsed = mod.parseListEnvelope({
      items: [],
      processor: { state: 'Idle' },
    })
    expect(parsed).toEqual({ items: [], processor: { state: 'Idle' } })
    expect(parsed).not.toBeInstanceOf(Array)
  })

  it('AC-21.4 transcriptPollInterval uses Query v5 query.state.data', async () => {
    const { transcriptPollInterval } = await import(
      '../../src/renderer/src/features/transcript/useTranscriptQueue'
    )
    expect(
      transcriptPollInterval({ state: { data: { processor: { state: 'Processing' } } } }),
    ).toBe(1000)
    expect(transcriptPollInterval({ state: { data: { processor: { state: 'Idle' } } } })).toBe(5000)
    expect(transcriptPollInterval({ state: { data: { processor: { state: 'Paused' } } } })).toBe(5000)
    expect(transcriptPollInterval({ state: { data: undefined } })).toBe(5000)
  })

  it('AC-21.5 CARD_FIELDS and CARD_QUEUE never bind video_ids or a table', () => {
    const sources = transcriptSources().join('\n')
    expect(sources).toContain('channel-card')
    expect(sources).toContain('channel_name')
    expect(sources).toContain('video_count')
    expect(sources).toContain('transcripts_done')
    expect(sources).toContain('word_count')
    expect(sources).toContain('output_dir')
    expect(sources).not.toMatch(/video_ids|processed_ids|progress\.json/)
    expect(sources).not.toMatch(/queue-table|TanStack|useReactTable/)
  })

  it('AC-21.6 OUTPUT_TREE labels raw and compiled under output_dir', async () => {
    const { outputTreeLabels } = await import(
      '../../src/renderer/src/features/transcript/output-tree'
    )
    const labels = outputTreeLabels('C:/out/fireship')
    expect(labels.raw).toBe('C:/out/fireship/raw')
    expect(labels.compiled).toBe('C:/out/fireship/compiled')
    expect(labels.raw).not.toBe('C:/out/fireship/fireship/raw')
    expect(JSON.stringify(labels)).not.toMatch(/C:\/out\/fireship\/fireship\/raw/)
  })

  it('AC-21.7 ENABLED_WHEN and STOP_VERB gate processor buttons', async () => {
    const { controlEnabled } = await import(
      '../../src/renderer/src/features/transcript/transcript-controls'
    )
    const pending = [{ id: 'a', status: 'Pending', transcripts_done: 0, output_dir: 'C:/o', zip_path: null }]
    const pausedJob = [{ id: 'a', status: 'Paused', transcripts_done: 0, output_dir: 'C:/o', zip_path: null }]
    expect(
      controlEnabled('start', { items: pending, selectedId: 'a', processorState: 'Idle' }),
    ).toBe(true)
    expect(
      controlEnabled('start', { items: pending, selectedId: 'a', processorState: 'Processing' }),
    ).toBe(false)
    expect(
      controlEnabled('start', { items: pausedJob, selectedId: 'a', processorState: 'Idle' }),
    ).toBe(true)
    expect(
      controlEnabled('pause', { items: pending, selectedId: 'a', processorState: 'Processing' }),
    ).toBe(true)
    expect(
      controlEnabled('resume', { items: pending, selectedId: 'a', processorState: 'Paused' }),
    ).toBe(true)
    expect(
      controlEnabled('stop', { items: pending, selectedId: 'a', processorState: 'Paused' }),
    ).toBe(true)
    const sources = transcriptSources().join('\n')
    expect(sources).toContain('stop-btn')
    expect(sources).not.toMatch(/cancel-btn|download:cancel/)
  })

  it('AC-21.8 REORDER_BODY is a full job_ids permutation', async () => {
    const { buildReorderBody } = await import(
      '../../src/renderer/src/features/transcript/transcript-controls'
    )
    const ids = ['a', 'b', 'c']
    expect(buildReorderBody(ids, 'b', 'up')).toEqual({ job_ids: ['b', 'a', 'c'] })
    expect(buildReorderBody(ids, 'b', 'down')).toEqual({ job_ids: ['a', 'c', 'b'] })
    expect(buildReorderBody(ids, 'b', 'up')).not.toEqual({ job_ids: ['b'] })
  })

  it('AC-21.9 Requeue and Retry visibility is status-gated', async () => {
    const { actionVisible } = await import(
      '../../src/renderer/src/features/transcript/transcript-controls'
    )
    expect(actionVisible('requeue', 'Cancelled')).toBe(true)
    expect(actionVisible('requeue', 'Failed')).toBe(false)
    expect(actionVisible('retry', 'Failed')).toBe(true)
    expect(actionVisible('retry', 'Cancelled')).toBe(false)
    expect(actionVisible('retry', 'Pending')).toBe(false)
  })

  it('AC-21.10 compile and completed opens use compile paths and IPC', async () => {
    const { controlEnabled } = await import(
      '../../src/renderer/src/features/transcript/transcript-controls'
    )
    const done = [
      {
        id: 'a',
        status: 'Done',
        transcripts_done: 2,
        output_dir: 'C:/out/ch',
        zip_path: 'C:/out/ch/ch_raw.zip',
        compiled_path: 'C:/out/ch/compiled/ch_vol1.md',
      },
    ]
    const empty = [
      {
        id: 'a',
        status: 'Pending',
        transcripts_done: 0,
        output_dir: '',
        zip_path: null,
        compiled_path: null,
      },
    ]
    expect(controlEnabled('compile', { items: done, selectedId: 'a', processorState: 'Idle' })).toBe(true)
    expect(controlEnabled('compile', { items: empty, selectedId: 'a', processorState: 'Idle' })).toBe(false)
    expect(
      controlEnabled('view-compiled', { items: done, selectedId: 'a', processorState: 'Idle' }),
    ).toBe(true)
    expect(controlEnabled('open-zip', { items: done, selectedId: 'a', processorState: 'Idle' })).toBe(true)
    expect(controlEnabled('open-folder', { items: done, selectedId: 'a', processorState: 'Idle' })).toBe(true)
    expect(
      controlEnabled('view-compiled', { items: empty, selectedId: 'a', processorState: 'Idle' }),
    ).toBe(false)
    const sources = transcriptSources().join('\n')
    expect(sources).toMatch(/\/transcripts\/.+\/compile|\/compile/)
    expect(sources).toMatch(/openPath/)
    expect(sources).not.toMatch(/C:\/outside\/tool\.exe/)
  })

  it('AC-21.11 IN_PAGE_CONFIRM is a G20 portaled modal', () => {
    const sources = transcriptSources().join('\n')
    expect(sources).toMatch(/createPortal/)
    expect(sources).toMatch(/document\.body/)
    expect(sources).toContain('remove-confirm-btn')
    expect(sources).toContain('remove-confirm-cancel')
    expect(sources).toMatch(/--color-bg-elevated|--color-fg|--color-border/)
    expect(sources).toMatch(/Escape|keydown/)
    expect(sources).not.toMatch(/window\.confirm|window\.alert|window\.prompt/)
  })

  it('AC-21.12 ERROR_SURFACE does not swallow ApiError', () => {
    const sources = transcriptSources().join('\n')
    expect(sources).not.toMatch(/\.catch\(\s*\(\s*\)\s*=>\s*undefined/)
    expect(sources).toMatch(/ApiError|error/)
    expect(readRequired(pagePath)).toMatch(/error-banner/)
  })

  it('AC-21.13 PALETTE_DELIVER AppShell owns transcript palette ids', () => {
    const shell = readRequired(appShellPath)
    expect(shell).toMatch(/av-kit:transcript:/)
    expect(shell).toMatch(/transcript-commands|TRANSCRIPT_COMMANDS/)
    const registry = readRequired(registryPath)
    expect(registry).not.toMatch(/apiFetch/)
    for (const id of TRANSCRIPT_PALETTE_IDS) {
      expect(registry).toContain(id)
    }
  })

  it('AC-21.14 TRANSCRIPT_LOCAL_IDS exist and Settings Browse does not', () => {
    const sources = transcriptSources().join('\n')
    for (const id of [
      'requeue-btn',
      'retry-btn',
      'compile-btn',
      'remove-btn',
      'view-compiled-btn',
      'open-zip-btn',
      'open-folder-btn',
    ]) {
      expect(sources).toContain(id)
    }
    expect(sources).not.toContain('settings:browse_transcript_dir')
    expect(sources).not.toContain('browse-transcript-dir')
  })

  it('AC-21.15 card opens use IPC and stay disabled without paths', async () => {
    const { controlEnabled } = await import(
      '../../src/renderer/src/features/transcript/transcript-controls'
    )
    const noPath = [
      {
        id: 'a',
        status: 'Done',
        transcripts_done: 1,
        output_dir: '',
        zip_path: null,
        compiled_path: null,
      },
    ]
    expect(
      controlEnabled('open-folder', { items: noPath, selectedId: 'a', processorState: 'Idle' }),
    ).toBe(false)
    expect(controlEnabled('open-zip', { items: noPath, selectedId: 'a', processorState: 'Idle' })).toBe(
      false,
    )
    const sources = transcriptSources().join('\n')
    expect(sources).toMatch(/openPath/)
  })

  it('AC-21.16 Wave 2 testids are registered on the page and in test-ids.ts', () => {
    const page = readRequired(pagePath)
    const ids = readRequired(testIdsPath)
    for (const id of [...WAVE2_TESTIDS, ...WAVE2_EXTRA_TESTIDS]) {
      expect(page).toContain(id)
      expect(ids).toContain(id)
    }
  })

  it('AC-21.17 RATE_ETA and BATCH_OMIT hide on non-finite delay', async () => {
    const { formatRateEta } = await import('../../src/renderer/src/features/transcript/rate-eta')
    expect(formatRateEta({ delay: 6, videoCount: 10, transcriptsDone: 4 })).toEqual({
      rate: '1 req/6s',
      etaSeconds: 36,
    })
    expect(formatRateEta({ delay: Number.NaN, videoCount: 10, transcriptsDone: 4 })).toBeNull()
    expect(formatRateEta({ delay: Number.POSITIVE_INFINITY, videoCount: 10, transcriptsDone: 0 })).toBeNull()
    const sources = transcriptSources().join('\n')
    expect(sources).not.toMatch(/Batch /)
    expect(sources).not.toMatch(/batch_index/)
  })

  it('AC-21.18 STATUS_COLORS include Paused and use theme tokens', async () => {
    const { JOB_STATUSES, STATUS_COLORS } = await import(
      '../../src/renderer/src/features/transcript/transcript-controls'
    )
    expect(JOB_STATUSES).toContain('Paused')
    expect(STATUS_COLORS.Paused).toMatch(/^bg-/)
    expect(STATUS_COLORS.Paused).not.toMatch(/#/)
    const sources = transcriptSources().join('\n')
    expect(sources).not.toMatch(/className=\{?[`'"][^`'"]*#[0-9a-fA-F]{3,8}/)
    expect(sources).not.toMatch(/<select/)
    const styles = readRequired(stylesPath)
    expect(styles).toMatch(/--color-status-pending|--color-accent-green|--color-error/)
  })

  it('AC-21.19 MEU-21 sources have no placeholder or skip guards', () => {
    const sources = transcriptSources().join('\n')
    expect(sources).not.toMatch(/TODO|FIXME|NotImplementedError/)
    const unit = readFileSync(resolve(here, 'transcript-page.test.ts'), 'utf8')
    expect(unit).not.toMatch(/it\.skip|describe\.skip|test\.skip|it\.only|describe\.only|test\.only/)
  })

  it('AC-21.20 create uses TranscriptJobOut then invalidates QUERY_KEY', async () => {
    const { applyCreateJob } = await import(
      '../../src/renderer/src/features/transcript/transcript-commands'
    )
    const job = applyCreateJob({ id: 'j1', channel_url: 'https://www.youtube.com/@x' })
    expect(job.id).toBe('j1')
    const sources = transcriptSources().join('\n')
    expect(sources).toMatch(/invalidateQueries|QUERY_KEY/)
    expect(sources).not.toMatch(/created\.items|out\.items/)
  })

  it('AC-21.21 TranscriptPage exists without editing FastAPI or MCP', () => {
    expect(existsSync(pagePath)).toBe(true)
    expect(existsSync(apiTranscriptsPath)).toBe(true)
    const api = readFileSync(apiTranscriptsPath, 'utf8')
    expect(api).toContain('TranscriptCreateIn')
    expect(api).not.toContain('MEU-21')
    expect(existsSync(mcpDir)).toBe(true)
  })

  it('AC-21.22 CHANNEL_URL_HINT is visible and blank Add no-ops', async () => {
    const page = readRequired(pagePath)
    expect(page).toContain('channel-url-hint')
    expect(page).toMatch(/\/@handle/)
    const mod = await import('../../src/renderer/src/features/transcript/transcript-commands')
    expect(mod.createTranscriptBody('   ')).toBeNull()
  })
})
