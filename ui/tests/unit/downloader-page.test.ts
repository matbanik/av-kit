import { existsSync, readFileSync, readdirSync } from 'node:fs'
import { resolve } from 'node:path'

import { describe, expect, it } from 'vitest'

const renderer = resolve(__dirname, '../../src/renderer/src')
const downloaderDir = resolve(renderer, 'features/downloader')
const pagePath = resolve(downloaderDir, 'DownloaderPage.tsx')
const queueListPath = resolve(renderer, 'components/queue/QueueList.tsx')
const routerPath = resolve(renderer, 'router.tsx')
const appShellPath = resolve(renderer, 'components/layout/AppShell.tsx')
const registryPath = resolve(renderer, 'registry/commandRegistry.ts')
const stylesPath = resolve(renderer, 'styles.css')
const packagePath = resolve(__dirname, '../../package.json')
const launchPath = resolve(__dirname, '../e2e/launch.test.ts')
const testIdsPath = resolve(__dirname, '../e2e/test-ids.ts')
const apiDownloadsPath = resolve(__dirname, '../../../packages/api/src/avkit_api/routes/downloads.py')
const mcpDir = resolve(__dirname, '../../../mcp-server')

/*
  MEU-46 rewrite (AC-46.4/.6). Six of the eleven Wave-1 ids retired with the
  table and the thirteen-button toolbar; each is REPLACED by the id that now
  carries its capability, never dropped:

    queue-table -> queue-list        queue-row   -> queue-card
    start-btn   -> queue-toolbar-start   pause-btn  -> queue-toolbar-pause
    resume-btn  -> queue-toolbar-resume  cancel-btn -> queue-card-primary-action

  The replacements live in the shared queue components rather than in the page,
  so AC-20.16 resolves each id against the page OR those components (see below).
*/
const WAVE1_TESTIDS = [
  'downloader-page',
  'url-input',
  'add-btn',
  'queue-list',
  'queue-card',
  'queue-toolbar-start',
  'queue-toolbar-pause',
  'queue-toolbar-resume',
  'queue-card-primary-action',
  'sabr-status',
  'sabr-check-btn',
] as const

const WAVE1_EXTRA_TESTIDS = [
  'quality-select',
  'audio-only',
  'audio-format',
  'cookie-mode-none',
  'cookie-mode-browser',
  'cookie-mode-file',
  'cookie-browser',
  'cookie-profile',
  'cookie-file',
  'cookie-test-btn',
  'sabr-force-btn',
  'sabr-clear-btn',
  /*
    MEU-46 rewrite (AC-46.6), same E2E_REWRITE_RULE as WAVE1_TESTIDS above: the
    thirteen retired row/toolbar buttons are REPLACED by the ids that now carry
    their capability, never dropped. Eight of them (up/down/top/bottom/reset/
    remove/open-file/open-folder) collapse onto the card's kebab and its single
    primary action; clear-all moves behind the toolbar's overflow menu.

      up/down/top/bottom/remove/open-file/open-folder-btn
                      -> queue-card-kebab > queue-card-menu
      reset-btn       -> queue-card-primary-action  (in WAVE1_TESTIDS)
      clear-all-btn   -> queue-toolbar-overflow > queue-toolbar-clear-all
  */
  'queue-card-kebab',
  'queue-card-menu',
  'queue-toolbar-clear-finished',
  'queue-toolbar-overflow',
  'queue-toolbar-clear-all',
  'queue-summary',
  'processor-indicator',
] as const

const QUALITY_WIRE = [
  'best',
  '2160p',
  '1440p',
  '1080p',
  '720p',
  '480p',
  '360p',
  '240p',
  '144p',
  'lowest',
] as const

const AUDIO_WIRE = [
  'default',
  'best',
  'lowest',
  'low_webm',
  'medium_webm',
  'standard_webm',
  'standard_m4a',
  'standard_mp3',
  'high_m4a',
] as const

const JOB_STATUSES = [
  'Pending',
  'Downloading',
  'Done',
  'Failed',
  'Skipped',
  'QualityBlocked',
  'AgeRestricted',
  'Cancelled',
] as const

const DOWNLOAD_PALETTE_IDS = [
  'download:add',
  'download:start',
  'download:pause',
  'download:resume',
  'download:cancel',
  'download:clear',
  'download:sabr_check',
] as const

function readRequired(path: string): string {
  expect(existsSync(path), path).toBe(true)
  return readFileSync(path, 'utf8')
}


/** Every .ts/.tsx file under ui/src, for whole-tree reference sweeps. */
function walkUiSources(dir: string = renderer): string[] {
  const out: string[] = []
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = resolve(dir, entry.name)
    if (entry.isDirectory()) {
      out.push(...walkUiSources(full))
    } else if (/\.(ts|tsx)$/.test(entry.name)) {
      out.push(full)
    }
  }
  return out
}
/** Every shared queue component the downloader page mounts. */
function queueComponentSources(): string[] {
  const dir = resolve(renderer, 'components/queue')
  if (!existsSync(dir)) {
    return []
  }
  return readdirSync(dir)
    .filter((name) => /\.(ts|tsx)$/.test(name))
    .map((name) => readFileSync(resolve(dir, name), 'utf8'))
}

function downloaderSources(): string[] {
  expect(existsSync(downloaderDir), downloaderDir).toBe(true)
  return readdirSync(downloaderDir)
    .filter((name) => name.endsWith('.ts') || name.endsWith('.tsx'))
    .map((name) => readFileSync(resolve(downloaderDir, name), 'utf8'))
}

describe('MEU-20 downloader', () => {
  it('AC-20.1 routes / to DownloaderPage with downloader-page and url-input', () => {
    const src = readRequired(routerPath)
    expect(src).toMatch(/DownloaderPage/)
    expect(src).not.toMatch(/component:\s*ShellHome/)
    const page = readRequired(pagePath)
    expect(page).toContain('downloader-page')
    expect(page).toContain('url-input')
    expect(page).not.toMatch(/Connecting to backend/)
  })

  it('AC-20.2 QUALITY_WIRE and AUDIO_WIRE use API wire values and defaults', async () => {
    const mod = await import('../../src/renderer/src/features/downloader/quality-options')
    expect(mod.QUALITY_WIRE).toEqual([...QUALITY_WIRE])
    expect(mod.AUDIO_WIRE).toEqual([...AUDIO_WIRE])
    expect(mod.QUALITY_DEFAULT).toBe('1080p')
    expect(mod.AUDIO_DEFAULT).toBe('default')
    expect(mod.QUALITY_WIRE).not.toContain('P1080')
    expect(mod.QUALITY_WIRE).not.toContain('1080P')
    expect(mod.QUALITY_WIRE).not.toContain('Best')
    expect(mod.qualityOptions(false)).toEqual([...QUALITY_WIRE])
    expect(mod.audioOptions(false)).toEqual([...AUDIO_WIRE])
  })

  it('AC-20.3 CREATE_BODY is url quality audio_only audio_format only', async () => {
    const mod = await import('../../src/renderer/src/features/downloader/download-commands')
    expect(mod.createDownloadBody({ url: '', quality: '1080p', audio_only: false, audio_format: 'default' })).toBeNull()
    const body = mod.createDownloadBody({
      url: 'https://example.invalid/watch?v=e2e0001',
      quality: '1080p',
      audio_only: false,
      audio_format: 'default',
    })
    expect(body).toEqual({
      url: 'https://example.invalid/watch?v=e2e0001',
      quality: '1080p',
      audio_only: false,
      audio_format: 'default',
    })
    expect(Object.keys(body ?? {})).toEqual(['url', 'quality', 'audio_only', 'audio_format'])
    expect(body).not.toHaveProperty('cookies')
  })

  it('AC-20.4 LIST_ENVELOPE and QUERY_KEY reject a bare array', async () => {
    const mod = await import('../../src/renderer/src/features/downloader/useDownloadQueue')
    expect(mod.QUERY_KEY).toEqual(['downloads'])
    expect(() => mod.parseListEnvelope([])).toThrow()
    const parsed = mod.parseListEnvelope({
      items: [],
      processor: { state: 'Idle' },
    })
    expect(parsed).toEqual({ items: [], processor: { state: 'Idle' } })
    expect(parsed).not.toBeInstanceOf(Array)
  })

  it('AC-20.5 downloadPollInterval uses Query v5 query.state.data', async () => {
    const { downloadPollInterval } = await import(
      '../../src/renderer/src/features/downloader/useDownloadQueue'
    )
    expect(
      downloadPollInterval({ state: { data: { processor: { state: 'Processing' } } } }),
    ).toBe(1000)
    expect(downloadPollInterval({ state: { data: { processor: { state: 'Idle' } } } })).toBe(5000)
    expect(downloadPollInterval({ state: { data: { processor: { state: 'Paused' } } } })).toBe(5000)
    expect(downloadPollInterval({ state: { data: undefined } })).toBe(5000)
  })

  it('AC-20.6 SABR panel uses GET /downloads/sabr and named POSTs', () => {
    const sources = downloaderSources().join('\n')
    expect(sources).toContain('/downloads/sabr')
    expect(sources).toMatch(/POST[\s\S]*\/downloads\/sabr\/check|\/downloads\/sabr\/check/)
    expect(sources).toContain('/downloads/sabr/force')
    expect(sources).toContain('/downloads/sabr/clear')
    expect(sources).toContain('sabr-status')
    expect(sources).toContain('sabr-check-btn')
    expect(sources).toContain('sabr-force-btn')
    expect(sources).toContain('sabr-clear-btn')
  })

  it('AC-20.7 SABR_QUALITY and SABR_AUDIO replace full wires while active', async () => {
    const mod = await import('../../src/renderer/src/features/downloader/quality-options')
    expect(mod.qualityOptions(true)).toEqual(['360p'])
    expect(mod.audioOptions(true)).toEqual(['standard_mp3', 'high_m4a'])
    expect(mod.qualityOptions(true)).not.toContain('1080p')
  })

  it('AC-20.8 cookie settings PUT leaves and test body never include cookie bytes', async () => {
    const mod = await import('../../src/renderer/src/features/downloader/cookie-bar')
    const put = mod.cookieSettingsPutBody({
      cookie_mode: 'file',
      cookie_browser: 'chrome',
      cookie_browser_profile: 'Default',
      cookie_file_path: 'C:/cookies.txt',
    })
    expect(put).toEqual({
      cookie_mode: 'file',
      cookie_browser: 'chrome',
      cookie_browser_profile: 'Default',
      cookie_file_path: 'C:/cookies.txt',
    })
    expect(JSON.stringify(put)).not.toMatch(/Netscape|# HTTP Cookie File/)
    const testBody = mod.cookieTestBody({
      mode: 'file',
      cookie_file: 'C:/cookies.txt',
    })
    expect(testBody).toEqual({ mode: 'file', cookie_file: 'C:/cookies.txt' })
    expect(testBody).not.toHaveProperty('cookies')
    expect(JSON.stringify(testBody)).not.toMatch(/Cookie:/)
  })

  it('AC-20.9 ENABLED_WHEN gates Start Pause Resume Cancel and queue actions', async () => {
    const { controlEnabled } = await import(
      '../../src/renderer/src/features/downloader/download-controls'
    )
    const pending = [{ id: 'a', status: 'Pending', file_path: null }]
    const failed = [{ id: 'a', status: 'Failed', file_path: null }]
    expect(
      controlEnabled('start', { items: pending, selectedId: 'a', processorState: 'Idle' }),
    ).toBe(true)
    expect(
      controlEnabled('start', { items: pending, selectedId: 'a', processorState: 'Processing' }),
    ).toBe(false)
    expect(
      controlEnabled('pause', { items: pending, selectedId: 'a', processorState: 'Processing' }),
    ).toBe(true)
    expect(
      controlEnabled('resume', { items: pending, selectedId: 'a', processorState: 'Paused' }),
    ).toBe(true)
    expect(
      controlEnabled('cancel', { items: pending, selectedId: 'a', processorState: 'Paused' }),
    ).toBe(true)
    expect(
      controlEnabled('clear-all', { items: [], selectedId: null, processorState: 'Idle' }),
    ).toBe(false)
    expect(
      controlEnabled('reset', { items: failed, selectedId: 'a', processorState: 'Idle' }),
    ).toBe(true)
    expect(
      controlEnabled('remove', { items: pending, selectedId: 'a', processorState: 'Idle' }),
    ).toBe(true)
  })

  it('AC-20.10 REORDER_BODY is a full job_ids permutation', async () => {
    const { buildReorderBody } = await import(
      '../../src/renderer/src/features/downloader/download-controls'
    )
    const ids = ['a', 'b', 'c']
    expect(buildReorderBody(ids, 'b', 'up')).toEqual({ job_ids: ['b', 'a', 'c'] })
    expect(buildReorderBody(ids, 'b', 'down')).toEqual({ job_ids: ['a', 'c', 'b'] })
    expect(buildReorderBody(ids, 'c', 'top')).toEqual({ job_ids: ['c', 'a', 'b'] })
    expect(buildReorderBody(ids, 'a', 'bottom')).toEqual({ job_ids: ['b', 'c', 'a'] })
    expect(buildReorderBody(ids, 'b', 'up')).not.toEqual({ job_ids: ['b'] })
  })

  it('AC-20.11 summary counts every JOB_STATUS and Paused is processor-only', async () => {
    const mod = await import('../../src/renderer/src/features/downloader/download-controls')
    expect(mod.JOB_STATUSES).toEqual([...JOB_STATUSES])
    expect(mod.JOB_STATUSES).not.toContain('Paused')
    const summary = mod.queueSummary([
      { status: 'Pending' },
      { status: 'Done' },
      { status: 'Done' },
    ])
    expect(summary.Pending).toBe(1)
    expect(summary.Done).toBe(2)
    expect(summary.Failed).toBe(0)
    expect(summary).not.toHaveProperty('Paused')
    expect(mod.processorLabel('Idle')).toBeNull()
    expect(mod.processorLabel('Processing')).toMatch(/Processing/)
    expect(mod.processorLabel('Paused')).toMatch(/Paused/)
  })

  it('AC-20.12 Add and Start do not swallow ApiError', () => {
    const sources = downloaderSources().join('\n')
    expect(sources).not.toMatch(/\.catch\(\s*\(\s*\)\s*=>\s*undefined/)
    expect(sources).toMatch(/ApiError|error/)
    expect(readRequired(pagePath)).toMatch(/data-testid=["']error-banner["']|error-banner/)
  })

  it('AC-20.13 AppShell owns DOWNLOAD_PALETTE_IDS and registry does not fetch', () => {
    const shell = readRequired(appShellPath)
    expect(shell).toMatch(/av-kit:download:/)
    expect(shell).toMatch(/download-commands|DOWNLOAD_COMMANDS/)
    const registry = readRequired(registryPath)
    expect(registry).not.toMatch(/apiFetch/)
    for (const id of DOWNLOAD_PALETTE_IDS) {
      expect(registry).toContain(id)
    }
  })

  it('AC-20.14 local download actions exist and Settings apply-defaults does not', () => {
    const page = readRequired(pagePath)
    // MEU-46 rewrite (AC-46.6), same E2E_REWRITE_RULE as WAVE1_TESTIDS: remove/
    // reset/open-file/open-folder-btn retired with the row-button strip, so the
    // capability is resolved against the shared queue components that now host
    // them (the kebab menu and the single primary action) rather than against
    // four page-local button ids that no longer exist. The three SABR/cookie
    // ids stay page-local, because those controls did not move.
    const sources = [...downloaderSources(), ...queueComponentSources()].join('\n')
    for (const id of [
      'sabr-force-btn',
      'sabr-clear-btn',
      'cookie-test-btn',
      'queue-card-menu',
      'queue-card-primary-action',
    ]) {
      expect(sources, `${id} must exist in production`).toContain(id)
    }
    // remove / reset / open-file / open-folder are still reachable -- as kebab
    // actions and the card's primary action, not as toolbar buttons.
    for (const action of ['remove', 'open-file', 'open-folder']) {
      expect(sources, `${action} survives as a kebab action`).toContain(`'${action}'`)
    }
    expect(sources, 'reset survives as the card Retry action').toContain('onRetry')
    expect(page).not.toContain('download:apply_quality_pending')
    expect(page).not.toContain('download:browse_path')
    expect(page).not.toMatch(/Apply defaults|apply-defaults/)
  })

  it('AC-20.15 open file and folder use existing IPC and stay disabled without file_path', async () => {
    const { controlEnabled } = await import(
      '../../src/renderer/src/features/downloader/download-controls'
    )
    const noPath = [{ id: 'a', status: 'Done', file_path: null }]
    const withPath = [{ id: 'a', status: 'Done', file_path: 'C:/media/a.mp4' }]
    expect(
      controlEnabled('open-file', { items: noPath, selectedId: 'a', processorState: 'Idle' }),
    ).toBe(false)
    expect(
      controlEnabled('open-folder', { items: noPath, selectedId: 'a', processorState: 'Idle' }),
    ).toBe(false)
    expect(
      controlEnabled('open-file', { items: withPath, selectedId: 'a', processorState: 'Idle' }),
    ).toBe(true)
    const sources = downloaderSources().join('\n')
    expect(sources).toMatch(/openPath|open-path/)
    expect(sources).toMatch(/showItemInFolder|show-item-in-folder/)
  })

  it('AC-20.16 production page registers every Wave 1 and extra testid', () => {
    // MEU-46: the queue ids moved into the shared components the page mounts, so
    // the id must be real *somewhere in production* and registered -- the
    // capability this test guards -- rather than literally inside the page file.
    const surface = [readRequired(pagePath), ...queueComponentSources()].join('\n')
    const ids = readRequired(testIdsPath)
    for (const id of [...WAVE1_TESTIDS, ...WAVE1_EXTRA_TESTIDS]) {
      expect(surface, `${id} must exist in production`).toContain(id)
      expect(ids, `${id} must be registered`).toContain(id)
    }
  })

  it('AC-20.17 wave0 launch home expects url-input on DOWNLOADER_HOME', () => {
    const launch = readRequired(launchPath)
    expect(launch).not.toMatch(/skeleton, not a downloader form/)
    expect(launch).toContain("getByTestId('url-input')")
    expect(launch).toMatch(/url-input[\s\S]{0,80}toBeVisible/)
  })

  it('AC-20.18 audio format and cookie chrome stay hidden until their gates', async () => {
    const mod = await import('../../src/renderer/src/features/downloader/cookie-bar')
    expect(mod.audioFormatVisible(false)).toBe(false)
    expect(mod.audioFormatVisible(true)).toBe(true)
    expect(mod.cookieBrowserVisible('none')).toBe(false)
    expect(mod.cookieBrowserVisible('browser')).toBe(true)
    expect(mod.cookieFileVisible('file')).toBe(true)
    expect(mod.cookieFileVisible('browser')).toBe(false)
    const page = readRequired(pagePath)
    expect(page).toMatch(/Audio Only|audio-only/)
    expect(page).toMatch(/Cookie Authentication/)
  })

  it('AC-20.19 STATUS_COLORS and G30 selects use theme tokens not raw hex classNames', () => {
    const styles = readRequired(stylesPath)
    expect(styles).toMatch(/--color-status-pending|--color-accent-amber|--color-accent-green/)
    const pkg = readRequired(packagePath)
    // Rewritten by AC-46.5: `DownloadQueueTable` was react-table's last consumer,
    // so the dependency is uninstalled. The capability the original assertion
    // guarded -- the queue's rendering library is pinned, not floating -- is
    // preserved by inverting it: the library must now be absent entirely.
    expect(pkg).not.toMatch(/"@tanstack\/react-table"/)
    const sources = downloaderSources().join('\n')
    expect(sources).not.toMatch(/className=\{?[`'"][^`'"]*#[0-9a-fA-F]{3,8}/)
    expect(sources).toMatch(/quality-select/)
    expect(sources).toMatch(/style=\{\{/)
  })

  it('AC-20.20 MEU-20 sources have no placeholder or skip guards', () => {
    const sources = downloaderSources().join('\n')
    expect(sources).not.toMatch(/TODO|FIXME|NotImplementedError/)
    const unit = readFileSync(resolve(__dirname, 'downloader-page.test.ts'), 'utf8')
    expect(unit).not.toMatch(/it\.skip|describe\.skip|test\.skip|it\.only|describe\.only|test\.only/)
  })

  it('AC-20.21 playlist create uses DownloadCreateOut.items then invalidates QUERY_KEY', async () => {
    const { applyCreateItems } = await import(
      '../../src/renderer/src/features/downloader/download-commands'
    )
    const next = applyCreateItems({ items: [{ id: '1' }, { id: '2' }] })
    expect(next.map((row: { id: string }) => row.id)).toEqual(['1', '2'])
    const sources = downloaderSources().join('\n')
    expect(sources).toMatch(/invalidateQueries|QUERY_KEY/)
    expect(sources).toMatch(/\.items/)
  })

  it('AC-20.22 DownloaderPage exists without editing FastAPI or MCP', () => {
    expect(existsSync(pagePath)).toBe(true)
    expect(existsSync(apiDownloadsPath)).toBe(true)
    const api = readFileSync(apiDownloadsPath, 'utf8')
    expect(api).toContain('DownloadCreateIn')
    expect(api).not.toContain('MEU-20')
    expect(existsSync(mcpDir)).toBe(true)
  })
})

describe('MEU-46 downloader migration source contracts', () => {
  it('AC-46.5 DownloadQueueTable is deleted and react-table is gone from both manifests', () => {
    const tablePath = resolve(downloaderDir, 'DownloadQueueTable.tsx')
    expect(existsSync(tablePath), 'DownloadQueueTable.tsx must not survive').toBe(false)

    // Nothing anywhere in ui/src still names it -- a surviving reference fails
    // mount-gate clause 3.
    const referrers = walkUiSources().filter((file) =>
      readFileSync(file, 'utf8').includes('DownloadQueueTable'),
    )
    expect(
      referrers.map((file) => file.replace(/\\/g, '/').split('/ui/').pop() ?? file),
      'a surviving reference fails mount-gate clause 3',
    ).toEqual([])

    // Both manifests, because `npm uninstall` -- not a hand edit -- is what
    // removes the dependency, and a hand edit would leave the lockfile behind.
    const pkg = readRequired(packagePath)
    expect(pkg, '@tanstack/react-table is uninstalled from package.json').not.toContain(
      '@tanstack/react-table',
    )
    const lock = readRequired(resolve(__dirname, '../../package-lock.json'))
    expect(lock, '@tanstack/react-table is uninstalled from package-lock.json').not.toContain(
      '@tanstack/react-table',
    )

    // No ui/src file imports it any more, under any name.
    const importers = walkUiSources().filter((file) =>
      readFileSync(file, 'utf8').includes('@tanstack/react-table'),
    )
    expect(importers.map((file) => file.replace(/\\/g, '/').split('/ui/').pop() ?? file)).toEqual([])

    // The page mounts the shared list and toolbar instead.
    const page = readRequired(pagePath)
    expect(page).toMatch(/from '\.\.\/\.\.\/components\/queue\/QueueList'/)
    expect(page).toMatch(/from '\.\.\/\.\.\/components\/queue\/QueueHeaderRow'/)
    const header = readRequired(resolve(queueListPath, '../QueueHeaderRow.tsx'))
    expect(header).toMatch(/from '\.\/QueueToolbar'/)
    expect(header).toContain('<QueueToolbar {...toolbar} />')
  })
})

describe('QUEUE_SCROLL_CONTAINER_RULE (execution X3, not an AC)', () => {
  it('page root fills main and the list scroller owns overflow, not listClasses', () => {
    const page = readRequired(pagePath)
    const list = readRequired(queueListPath)
    const root = page.match(/<section data-testid="downloader-page" className="([^"]+)"/)
    expect(root, 'downloader-page root className').not.toBeNull()
    const rootClasses = root?.[1].split(/\s+/) ?? []
    expect(rootClasses).toEqual(expect.arrayContaining(['h-full', 'min-h-0']))

    const regionAt = page.indexOf('data-testid="download-queue-region"')
    expect(regionAt, 'download-queue-region').toBeGreaterThan(-1)
    const regionOpen = page.slice(regionAt - 80)
    const regionClass = regionOpen.match(/className="([^"]+)"/)
    expect(regionClass?.[1].split(/\s+/)).toEqual(
      expect.arrayContaining(['flex-1', 'min-h-[20rem]']),
    )

    // Session 24 keeps the controls pane as the height donor and puts the
    // composed header before the scroller. Real Electron AC-52.6/AC-53.5
    // verifies the resulting height and keyboard reorder behavior.
    expect(page, 'controls pane absorbs the deficit').toContain(
      '<div className="flex min-h-0 flex-col gap-4 overflow-auto">',
    )
    const headerAt = page.indexOf('<QueueHeaderRow', regionAt)
    const listAt = page.indexOf('<QueueList', regionAt)
    expect(headerAt, 'header is inside the queue region').toBeGreaterThan(regionAt)
    expect(headerAt, 'header stays above the list scroller').toBeLessThan(listAt)
    const header = readRequired(resolve(queueListPath, '../QueueHeaderRow.tsx'))
    expect(header).toContain('flex flex-wrap items-center')
    expect(header).toContain('data-testid={summaryTestId}')
    expect(header).toContain('<QueueToolbar {...toolbar} />')

    expect(page).toMatch(/overflow-auto[\s\S]{0,400}<QueueList/)
    expect(list).toContain("const listClasses = 'relative flex flex-col gap-2'")
    expect(list).not.toMatch(/listClasses = '[^']*overflow-auto/)
  })
})
