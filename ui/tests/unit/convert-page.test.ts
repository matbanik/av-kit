import { existsSync, readdirSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')
const converterDir = resolve(repoRoot, 'ui/src/renderer/src/features/converter')
const pagePath = resolve(converterDir, 'ConvertPage.tsx')
const tablePath = resolve(converterDir, 'ConvertQueueTable.tsx')
const queueComponentsDir = resolve(repoRoot, 'ui/src/renderer/src/components/queue')
const queueCardMenuPath = resolve(queueComponentsDir, 'QueueCardMenu.tsx')
const queueToolbarPath = resolve(queueComponentsDir, 'QueueToolbar.tsx')
const queueListPath = resolve(queueComponentsDir, 'QueueList.tsx')
const controlsPath = resolve(converterDir, 'convert-controls.ts')
const routerPath = resolve(repoRoot, 'ui/src/renderer/src/router.tsx')
const appShellPath = resolve(repoRoot, 'ui/src/renderer/src/components/layout/AppShell.tsx')
const navPath = resolve(repoRoot, 'ui/src/renderer/src/components/layout/NavRail.tsx')
const headerPath = resolve(repoRoot, 'ui/src/renderer/src/components/layout/Header.tsx')
const registryPath = resolve(repoRoot, 'ui/src/renderer/src/registry/commandRegistry.ts')
const helpCardPath = resolve(repoRoot, 'ui/src/renderer/src/components/help/HelpCard.tsx')
const settingsPagePath = resolve(repoRoot, 'ui/src/renderer/src/features/settings/SettingsPage.tsx')
const settingsSchemasPath = resolve(repoRoot, 'ui/src/renderer/src/features/settings/settings-schemas.ts')
const settingsPathsPath = resolve(repoRoot, 'ui/src/renderer/src/features/settings/settings-paths.ts')
const settingsHookPath = resolve(repoRoot, 'ui/src/renderer/src/features/settings/useSettingsPage.ts')
const formGuardPath = resolve(repoRoot, 'ui/src/renderer/src/styles/form-guard.css')
const stylesPath = resolve(repoRoot, 'ui/src/renderer/src/styles.css')
const ipcPath = resolve(repoRoot, 'ui/src/main/ipc.ts')
const preloadPath = resolve(repoRoot, 'ui/src/main/preload.ts')
const indexMainPath = resolve(repoRoot, 'ui/src/main/index.ts')
const envDtsPath = resolve(repoRoot, 'ui/src/renderer/src/env.d.ts')
const guiAuditPath = resolve(here, 'gui-actions-audit.test.ts')
const testIdsPath = resolve(repoRoot, 'ui/tests/e2e/test-ids.ts')
const launchPath = resolve(repoRoot, 'ui/tests/e2e/launch.test.ts')
const e2ePath = resolve(repoRoot, 'ui/tests/e2e/convert-queue.test.ts')
const e2eWiringPath = resolve(here, 'e2e-wiring.test.ts')
const shellHomePath = resolve(here, 'shell-home.test.ts')
const guiDocPath = resolve(repoRoot, 'docs/build-plan/06-gui.md')
const apiConversionsPath = resolve(repoRoot, 'packages/api/src/avkit_api/routes/conversions.py')
const mcpDir = resolve(repoRoot, 'mcp-server')
const openapiPath = resolve(repoRoot, 'openapi.committed.json')

const WAVE8_TESTIDS = [
  'nav-convert',
  'convert-page',
  'convert-dropzone',
  'convert-browse',
  'convert-add',
  'convert-task-compress',
  'convert-queue',
  'queue-toolbar-start',
] as const

const WAVE8_EXTRA_TESTIDS = [
  'convert-task-cut',
  'convert-task-extract',
  'convert-preset-archival',
  'convert-preset-high_quality',
  'convert-preset-balanced',
  'convert-preset-sharing',
  'convert-preset-mobile',
  'convert-advanced',
  'convert-gpu-chip',
  'convert-gpu-refresh',
  'convert-cut-in',
  'convert-cut-out',
  'convert-extract-first',
  'convert-extract-all',
  'convert-output-dir',
  'convert-skip-existing',
  'convert-page-save',
  'convert-queue-row',
  'convert-queue-summary',
  'convert-processor',
  // MEU-45 supersession (E2E_REWRITE_RULE applied at unit level): the 13
  // converter toolbar ids and the 4 hand-rolled confirm ids are retired, each
  // replaced here by the id of the new home named in RETIRED_TOOLBAR_CONTROLS
  // and RETIRED_TESTIDS. No capability loses its registry entry.
  'queue-toolbar',
  'queue-toolbar-pause',
  'queue-toolbar-resume',
  'queue-toolbar-clear-finished',
  'queue-toolbar-overflow',
  'queue-toolbar-clear-all',
  'queue-card-primary-action',
  'queue-card-kebab',
  'queue-card-menu',
  'queue-empty-dropzone',
  'queue-empty-browse',
  'queue-drop-strip',
  'confirm-modal',
  'confirm-modal-confirm',
  'confirm-modal-cancel',
  'convert-settings',
  'settings-leaf-converter-output_dir',
  'settings-leaf-default_preset',
  'settings-leaf-skip_existing',
  'settings-leaf-gpu_preference',
  'browse-convert-path-btn',
  'convert-settings-save',
] as const

const PRESET_WIRES = ['archival', 'high_quality', 'balanced', 'sharing', 'mobile'] as const
const JOB_STATUSES = ['Pending', 'Processing', 'Done', 'Failed', 'Cancelled', 'Skipped'] as const
const CONVERT_PALETTE_IDS = [
  'convert:add',
  'convert:start',
  'convert:pause',
  'convert:resume',
  'convert:cancel',
  'convert:clear',
] as const
const HELP_TOPICS = [
  'what convert does',
  'preset',
  'advanced',
  'gpu',
  'software',
  'fast cut',
  'accurate',
  'extract',
  'sequential',
  'add then start',
] as const


const uiSrcRoot = resolve(repoRoot, 'ui/src')

function walkUiSources(dir = uiSrcRoot): string[] {
  const out: string[] = []
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = resolve(dir, entry.name)
    if (entry.isDirectory()) {
      out.push(...walkUiSources(full))
    } else if (entry.name.endsWith('.ts') || entry.name.endsWith('.tsx')) {
      out.push(full)
    }
  }
  return out
}

const relative = (file: string): string => file.replace(repoRoot, '').replace(/\\/g, '/')

function readRequired(path: string): string {
  expect(existsSync(path), path).toBe(true)
  return readFileSync(path, 'utf8')
}

function converterSources(): string[] {
  expect(existsSync(converterDir), converterDir).toBe(true)
  return readdirSync(converterDir)
    .filter((name) => name.endsWith('.ts') || name.endsWith('.tsx'))
    .map((name) => readFileSync(resolve(converterDir, name), 'utf8'))
}

describe('MEU-33 convert gui', () => {
  it('AC-33.1 CONVERT_HOME uses lazyRouteComponent without a static ConvertPage import', () => {
    const src = readRequired(routerPath)
    expect(src).toMatch(/lazyRouteComponent/)
    expect(src).toMatch(/features\/converter\/ConvertPage/)
    expect(src).toMatch(/pendingComponent:\s*ModuleSkeleton|ModuleSkeleton/)
    expect(src).not.toMatch(/import\s*\{\s*ConvertPage\s*\}\s*from\s*['"]\.\/features\/converter\/ConvertPage['"]/)
    expect(src).toMatch(/import\s*\{\s*DownloaderPage\s*\}/)
    const page = readRequired(pagePath)
    expect(page).toContain('convert-page')
    expect(page).toMatch(/export function ConvertPage/)
  })

  it('AC-33.2 NAV_CONVERT is 4th primary after TTS and never POSTs on rail or Ctrl+4', () => {
    const nav = readRequired(navPath)
    expect(nav).toContain('nav-convert')
    expect(nav).toContain('nav:convert')
    expect(nav).toMatch(/Film/)
    expect(nav).toMatch(/Ctrl\+4/)
    const primary = nav.match(/SHELL_PRIMARY_NAV[\s\S]+?\] as const/)
    expect(primary?.[0]).toMatch(/nav:tts[\s\S]+nav:convert/)
    expect(primary?.[0]).not.toMatch(/nav:convert[\s\S]+nav:tts/)
    expect(nav).toMatch(/onNavigate\?\.\(item\.path\)/)
    expect(nav).not.toMatch(/apiFetch|\/conversions/)
    const shell = readRequired(appShellPath)
    expect(shell).toMatch(/createShortcutHandler/)
    expect(readRequired(registryPath)).toMatch(/navigateShell\(['"]\/convert['"]\)/)
    expect(shell).not.toMatch(/Ctrl\+4[\s\S]{0,200}convert:add/)
    const header = readRequired(headerPath)
    expect(header).toMatch(/PAGE_LABELS[\s\S]*'\/convert':\s*'Convert'/)
    const registry = readRequired(registryPath)
    expect(registry).toContain('nav:convert')
    expect(registry).toMatch(/shortcut:\s*'Ctrl\+4'/)
  })

  it('AC-33.3 task radios swap options without clearing queue or staging', async () => {
    const { applyTaskKind } = await import('../../src/renderer/src/features/converter/convert-controls')
    const prev = {
      kind: 'compress' as const,
      staging: ['C:/a.mp4'],
      items: [{ id: '1' }],
    }
    const next = applyTaskKind(prev, 'cut')
    expect(next.kind).toBe('cut')
    expect(next.staging).toEqual(['C:/a.mp4'])
    expect(next.items).toEqual([{ id: '1' }])
    const page = readRequired(pagePath)
    const taskSegment = page.match(/<SegmentedControl\s+name="Task"[\s\S]*?\n {8}\/>/)?.[0]
    expect(taskSegment).toBeDefined()
    for (const kind of ['compress', 'cut', 'extract']) {
      expect(taskSegment).toContain(`['${kind}',`)
    }
    expect(taskSegment).toContain('id: `convert-task-${value}`')
    expect(taskSegment).toContain('testId: `convert-task-${value}`')
    expect(taskSegment).toContain('value={kind}')
    expect(taskSegment).toContain('setKind(value)')
    const segment = readRequired(resolve(queueComponentsDir, '../ui/SegmentedControl.tsx'))
    expect(segment).toMatch(/type=["']radio["']/)
    expect(segment).toContain('data-testid={option.testId}')
    expect(page).not.toMatch(/setKind\([^)]+\)[\s\S]{0,80}setStaging\(\[\]\)/)
  })

  it('AC-33.4 presets use PRESET_WIRES labels and reset Advanced to catalog values', async () => {
    const mod = await import('../../src/renderer/src/features/converter/convert-presets')
    expect(mod.PRESET_WIRES).toEqual([...PRESET_WIRES])
    expect(mod.PRESET_DEFAULT).toBe('balanced')
    expect(mod.PRESET_LABELS).toEqual({
      archival: 'Archival',
      high_quality: 'High Quality',
      balanced: 'Balanced',
      sharing: 'Sharing',
      mobile: 'Mobile',
    })
    expect(mod.presetAdvanced('balanced')).toEqual({ cq: 25, scale_height: 0, audio_mode: 'aac_128' })
    expect(mod.presetAdvanced('archival')).toEqual({ cq: 18, scale_height: 0, audio_mode: 'copy' })
    expect(mod.presetAdvanced('mobile')).toEqual({ cq: 30, scale_height: 720, audio_mode: 'aac_96' })
    const body = (await import('../../src/renderer/src/features/converter/convert-body')).createConversionBody({
      paths: ['C:/a.mp4'],
      kind: 'compress',
      preset: 'balanced',
    })
    expect(body).toMatchObject({ preset: 'balanced', kind: 'compress' })
    expect(body).not.toMatchObject({ preset: 'Balanced' })
    expect(JSON.stringify(body)).not.toMatch(/HighQuality|hevc_nvenc/)
    const page = readRequired(pagePath)
    for (const id of PRESET_WIRES) {
      expect(page).toContain(`convert-preset-${id}`)
    }
  })

  it('AC-33.5 Advanced is collapsed with CQ scale audio gpu wires and refresh POST', async () => {
    const mod = await import('../../src/renderer/src/features/converter/convert-presets')
    expect(mod.CQ_MIN).toBe(18)
    expect(mod.CQ_MAX).toBe(32)
    expect(mod.CQ_STEP).toBe(1)
    expect(mod.SCALE_HEIGHTS).toEqual([0, 1080, 720, 480])
    const sources = converterSources().join('\n')
    expect(sources).toContain('convert-advanced')
    expect(sources).toContain('convert-gpu-refresh')
    expect(sources).toMatch(/\/conversions\/gpu\/refresh/)
    expect(sources).not.toMatch(/convert-gpu-chip[\s\S]{0,120}<select/)
    const page = readRequired(pagePath)
    expect(page).toMatch(/advancedOpen|setAdvancedOpen/)
    const compressOptions = page.match(/\{kind === 'compress' \? \([\s\S]*?\) : null\}/)?.[0]
    expect(compressOptions).toBeDefined()
    expect(compressOptions).toContain('<Disclosure')
    expect(compressOptions).toContain('testId="convert-advanced"')
    expect(compressOptions).toContain('open={advancedOpen}')
    expect(compressOptions).toContain('onOpenChange={setAdvancedOpen}')
    expect(page).not.toMatch(/hevc_nvenc/)
  })

  it('AC-33.6 parseConvertTime maps clock and seconds; invalid range skips Add POST', async () => {
    const { parseConvertTime } = await import('../../src/renderer/src/features/converter/convert-time')
    expect(parseConvertTime('01:02:03.456')).toBe(3_723_456)
    expect(parseConvertTime('90')).toBe(90_000)
    expect(parseConvertTime('90.5')).toBe(90_500)
    expect(parseConvertTime('not-a-time')).toBeNull()
    const { createConversionBody } = await import('../../src/renderer/src/features/converter/convert-body')
    expect(
      createConversionBody({
        paths: ['C:/a.mp4'],
        kind: 'cut',
        in_ms: 1000,
        out_ms: 1000,
        copy_mode: 'fast_copy',
      }),
    ).toBeNull()
    expect(
      createConversionBody({
        paths: ['C:/a.mp4'],
        kind: 'cut',
        in_ms: 2000,
        out_ms: 1000,
        copy_mode: 'fast_copy',
      }),
    ).toBeNull()
    const cut = createConversionBody({
      paths: ['C:/a.mp4'],
      kind: 'cut',
      in_ms: 0,
      out_ms: 1500,
      copy_mode: 'fast_copy',
    })
    expect(cut).toEqual({
      paths: ['C:/a.mp4'],
      kind: 'cut',
      in_ms: 0,
      out_ms: 1500,
      copy_mode: 'fast_copy',
    })
    expect(JSON.stringify(cut)).not.toMatch(/01:02:03/)
    const page = readRequired(pagePath)
    expect(page).toContain('convert-cut-in')
    expect(page).toContain('convert-cut-out')
    expect(page).toContain('convert-extract-first')
    expect(page).toContain('convert-extract-all')
  })

  it('AC-33.7 Browse uses show-files-dialog and drop uses getPathForFile without auto-POST', () => {
    const ipc = readRequired(ipcPath)
    expect(ipc).toContain('show-files-dialog')
    expect(ipc).toMatch(/openFile/)
    expect(ipc).toMatch(/multiSelections/)
    const preload = readRequired(preloadPath)
    expect(preload).toMatch(/showFilesDialog/)
    expect(preload).toMatch(/getPathForFile/)
    expect(preload).toMatch(/webUtils/)
    expect(preload).not.toMatch(/invoke\(['"]get-path-for-file/)
    const index = readRequired(indexMainPath)
    expect(index).toContain('C:/e2e/sample.mp4')
    const env = readRequired(envDtsPath)
    expect(env).toMatch(/showFilesDialog/)
    expect(env).toMatch(/getPathForFile/)
    const sources = converterSources().join('\n')
    expect(sources).toContain('convert-browse')
    expect(sources).toContain('convert-dropzone')
    expect(sources).toMatch(/getPathForFile/)
    expect(sources).not.toMatch(/\.path\b/)
    expect(sources).not.toMatch(/readFile\(/)
    expect(sources).not.toMatch(/onDrop[\s\S]{0,400}postConversionCreate|onDrop[\s\S]{0,400}\/conversions/)
    const page = readRequired(pagePath)
    expect(page).toMatch(/CONVERT_DIALOG_FILTERS/)
    expect(readRequired(resolve(converterDir, 'convert-filters.ts'))).toMatch(/mp3/)
  })

  it('AC-33.8 create body is a strict discriminated union and extra keys skip fetch', async () => {
    const { createConversionBody } = await import('../../src/renderer/src/features/converter/convert-body')
    expect(createConversionBody({ paths: [], kind: 'compress', preset: 'balanced' })).toBeNull()
    const compress = createConversionBody({
      paths: ['C:/a.mp4'],
      kind: 'compress',
      preset: 'balanced',
    })
    expect(compress).toEqual({ paths: ['C:/a.mp4'], kind: 'compress', preset: 'balanced' })
    expect(Object.keys(compress ?? {}).sort()).toEqual(['kind', 'paths', 'preset'])
    const withOverride = createConversionBody({
      paths: ['C:/a.mp4'],
      kind: 'compress',
      preset: 'balanced',
      cq: 20,
    })
    expect(withOverride).toMatchObject({ cq: 20, preset: 'balanced' })
    expect(
      createConversionBody({
        paths: ['C:/a.mp4'],
        kind: 'compress',
        preset: 'balanced',
        ffmpeg_args: '-x',
      }),
    ).toBeNull()
    const extract = createConversionBody({
      paths: ['C:/a.mp4'],
      kind: 'extract',
      stream_mode: 'all',
    })
    expect(extract).toEqual({ paths: ['C:/a.mp4'], kind: 'extract', stream_mode: 'all' })
    const sources = converterSources().join('\n')
    expect(sources).toMatch(/discriminatedUnion|\.strict\(\)/)
    expect(sources).toMatch(/POST[\s\S]*\/conversions|\/conversions['"]/)
  })

  it('AC-33.9 LIST_ENVELOPE QUERY_KEY and poll twin downloadPollInterval', async () => {
    const mod = await import('../../src/renderer/src/features/converter/useConversionQueue')
    expect(mod.QUERY_KEY).toEqual(['conversions'])
    expect(() => mod.parseListEnvelope([])).toThrow()
    const parsed = mod.parseListEnvelope({ items: [], processor: { state: 'Idle' } })
    expect(parsed).toEqual({ items: [], processor: { state: 'Idle' } })
    expect(parsed).not.toBeInstanceOf(Array)
    expect(mod.conversionPollInterval({ state: { data: { processor: { state: 'Processing' } } } })).toBe(1000)
    expect(mod.conversionPollInterval({ state: { data: { processor: { state: 'Idle' } } } })).toBe(5000)
    expect(mod.conversionPollInterval({ state: { data: { processor: { state: 'Paused' } } } })).toBe(5000)
    expect(mod.conversionPollInterval({ state: { data: undefined } })).toBe(5000)
  })

  it('AC-33.10 queue table renders JOB_STATUSES and hides processor when Idle', async () => {
    const mod = await import('../../src/renderer/src/features/converter/convert-controls')
    expect(mod.JOB_STATUSES).toEqual([...JOB_STATUSES])
    expect(mod.JOB_STATUSES).not.toContain('Paused')
    const summary = mod.queueSummary([{ status: 'Pending' }, { status: 'Done' }, { status: 'Done' }])
    expect(summary.Pending).toBe(1)
    expect(summary.Done).toBe(2)
    expect(summary).not.toHaveProperty('Paused')
    expect(mod.processorLabel('Idle')).toBeNull()
    expect(mod.processorLabel('Processing')).toMatch(/Processing/)
    // MEU-45 supersession: the Kind/Mode/Speed/ETA columns of the deleted
    // ConvertQueueTable are carried by convertMetaSegments onto the card meta
    // line (AC-45.17), and the queue ids are now rendered by the page itself.
    expect(existsSync(tablePath), 'ConvertQueueTable.tsx is deleted').toBe(false)
    const controls = readRequired(controlsPath)
    expect(controls).toContain('convertMetaSegments')
    const page = readRequired(pagePath)
    expect(page).toContain('convertMetaSegments')
    expect(page).toContain('metaSegments')
    expect(page).toContain('convert-queue')
    expect(page).toContain('convert-queue-row')
    expect(page).toContain('convert-queue-summary')
    expect(page).toContain('convert-processor')
  })

  it('AC-33.11 ENABLED_WHEN gates Start Pause Resume Cancel reorder and ffmpeg', async () => {
    const { controlEnabled } = await import('../../src/renderer/src/features/converter/convert-controls')
    const pending = [{ id: 'a', status: 'Pending', output_path: null, input_path: 'C:/a.mp4' }]
    const failed = [{ id: 'a', status: 'Failed', output_path: null, input_path: 'C:/a.mp4' }]
    const ctx = { items: pending, selectedId: 'a' as string | null, processorState: 'Idle' as const, ffmpegAvailable: true }
    expect(controlEnabled('start', ctx)).toBe(true)
    expect(controlEnabled('start', { ...ctx, processorState: 'Paused' })).toBe(true)
    expect(controlEnabled('start', { ...ctx, processorState: 'Processing' })).toBe(false)
    expect(controlEnabled('start', { ...ctx, ffmpegAvailable: false })).toBe(false)
    expect(controlEnabled('pause', { ...ctx, processorState: 'Processing' })).toBe(true)
    expect(controlEnabled('resume', { ...ctx, processorState: 'Paused' })).toBe(true)
    expect(controlEnabled('cancel', { ...ctx, processorState: 'Processing' })).toBe(true)
    expect(controlEnabled('cancel', { ...ctx, processorState: 'Paused' })).toBe(true)
    expect(controlEnabled('clear-all', { ...ctx, items: [] })).toBe(false)
    expect(controlEnabled('reset', { ...ctx, items: failed })).toBe(true)
    expect(controlEnabled('remove', ctx)).toBe(true)
    expect(controlEnabled('up', ctx)).toBe(false)
    expect(controlEnabled('add', { ...ctx, ffmpegAvailable: false })).toBe(false)
  })

  it('AC-33.12 REORDER_BODY is a full permutation and never sends []', async () => {
    const { buildReorderBody } = await import('../../src/renderer/src/features/converter/convert-controls')
    const ids = ['a', 'b', 'c']
    expect(buildReorderBody(ids, 'b', 'up')).toEqual({ job_ids: ['b', 'a', 'c'] })
    expect(buildReorderBody(ids, 'b', 'down')).toEqual({ job_ids: ['a', 'c', 'b'] })
    expect(buildReorderBody(ids, 'c', 'top')).toEqual({ job_ids: ['c', 'a', 'b'] })
    expect(buildReorderBody(ids, 'a', 'bottom')).toEqual({ job_ids: ['b', 'c', 'a'] })
    expect(buildReorderBody(ids, 'b', 'up').job_ids.length).toBeGreaterThanOrEqual(1)
    expect(buildReorderBody(ids, 'b', 'up')).not.toEqual({ job_ids: [] })
    expect(buildReorderBody(ids, 'b', 'up')).not.toEqual({ job_ids: ['b'] })
    const sources = converterSources().join('\n')
    expect(sources).toMatch(/\/conversions\/reorder/)
  })

  it('AC-33.13 palette ids dispatch CONVERT_EVENTS from AppShell without registry apiFetch', () => {
    const shell = readRequired(appShellPath)
    expect(shell).toMatch(/av-kit:convert:/)
    expect(shell).toMatch(/CONVERT_COMMANDS|convert-commands/)
    expect(shell).not.toMatch(/ConvertPage[\s\S]{0,40}addEventListener\(['"]av-kit:convert/)
    const registry = readRequired(registryPath)
    expect(registry).not.toMatch(/apiFetch/)
    for (const id of CONVERT_PALETTE_IDS) {
      expect(registry).toContain(id)
    }
    const commands = readRequired(resolve(converterDir, 'convert-commands.ts'))
    expect(commands).toMatch(/requestAnimationFrame/)
    expect(commands).toMatch(/convert-dropzone/)
    expect(commands).toMatch(/navigateShell\(['"]\/convert['"]\)/)
  })

  it('AC-33.14 G20 portal confirms remove and clear without window.confirm', () => {
    const page = readRequired(pagePath)
    // MEU-45 supersession: the same capability — a portalled confirm for remove
    // and for clear, and never window.confirm — now comes from the shared
    // ConfirmModal, so the hand-rolled portal and its four ids are retired
    // (G20_RULE + RETIRED_TESTIDS).
    expect(page).toContain('ConfirmModal')
    expect(page).not.toMatch(/createPortal/)
    for (const retired of [
      'convert-remove-confirm',
      'convert-remove-confirm-cancel',
      'convert-clear-confirm',
      'convert-clear-confirm-cancel',
    ]) {
      expect(page, retired + ' is retired').not.toContain(retired)
    }
    expect(page).not.toMatch(/window\.confirm/)
    // Remove now lives in the card kebab; Clear all in the toolbar overflow.
    expect(readRequired(queueCardMenuPath)).toContain('remove')
    expect(readRequired(queueToolbarPath)).toContain('queue-toolbar-clear-all')
  })

  it('AC-33.15 GPU chip labels and FFmpeg missing disable Add/Start', async () => {
    const { gpuChipLabel } = await import('../../src/renderer/src/features/converter/convert-gpu')
    expect(gpuChipLabel({ ffmpegAvailable: false, gpu: undefined })).toBe('FFmpeg missing')
    expect(gpuChipLabel({ ffmpegAvailable: true, gpu: undefined })).toBe('Encoder: Checking…')
    expect(
      gpuChipLabel({
        ffmpegAvailable: true,
        gpu: { nvidia_nvenc: true, amd_amf: false, intel_qsv: false },
      }),
    ).toBe('Encoder: NVIDIA NVENC')
    expect(
      gpuChipLabel({
        ffmpegAvailable: true,
        gpu: { nvidia_nvenc: false, amd_amf: true, intel_qsv: false },
      }),
    ).toBe('Encoder: AMD AMF')
    expect(
      gpuChipLabel({
        ffmpegAvailable: true,
        gpu: { nvidia_nvenc: false, amd_amf: false, intel_qsv: true },
      }),
    ).toBe('Encoder: Intel QSV')
    expect(
      gpuChipLabel({
        ffmpegAvailable: true,
        gpu: { nvidia_nvenc: false, amd_amf: false, intel_qsv: false },
      }),
    ).toBe('Encoder: Software (libx265)')
    const sources = converterSources().join('\n')
    expect(sources).toMatch(/\/conversions\/gpu/)
    expect(sources).toMatch(/\/health\/dependencies/)
    expect(sources).not.toMatch(/\bwmic\b/)
    expect(sources).toContain('convert-gpu-chip')
  })

  it('AC-33.16 converter settings use G23 explicit Save not schedulePut', async () => {
    const schemas = readRequired(settingsSchemasPath)
    expect(schemas).toMatch(/converterPutSchema/)
    expect(schemas).toMatch(/output_dir[\s\S]*default_preset[\s\S]*skip_existing[\s\S]*gpu_preference/)
    const paths = readRequired(settingsPathsPath)
    expect(paths).toMatch(/converter:\s*'\/settings\/converter'/)
    const hook = readRequired(settingsHookPath)
    expect(hook).not.toMatch(/schedulePut\(\s*['"]converter['"]/)
    const css = readRequired(formGuardPath)
    expect(css).toMatch(/btn-save-dirty/)
    expect(readRequired(stylesPath)).toMatch(/form-guard\.css/)
    const settings = readRequired(settingsPagePath)
    expect(settings).toContain('convert-settings')
    expect(settings).toContain('convert-settings-save')
    expect(settings).toContain('btn-save-dirty')
    expect(settings).toContain('Save Changes •')
    expect(settings).toContain('settings-leaf-converter-output_dir')
    expect(settings).toContain('settings-leaf-default_preset')
    expect(settings).toContain('settings-leaf-skip_existing')
    expect(settings).toContain('settings-leaf-gpu_preference')
    expect(settings).toContain('browse-convert-path-btn')
    expect(settings).toMatch(/showDirectoryDialog/)
    expect(settings).not.toMatch(/schedulePut\(\s*['"]converter['"]/)
    const { converterPutSchema } = await import('../../src/renderer/src/features/settings/settings-schemas')
    expect(
      converterPutSchema.safeParse({
        output_dir: 'C:/out',
        default_preset: 'balanced',
        skip_existing: true,
        gpu_preference: 'auto',
        extra: true,
      }).success,
    ).toBe(false)
  })

  it('AC-33.17 page output and skip share the converter G23 form and persist only on Save', () => {
    const page = readRequired(pagePath)
    expect(page).toContain('convert-output-dir')
    expect(page).toContain('convert-skip-existing')
    expect(page).toContain('convert-page-save')
    expect(page).toContain('btn-save-dirty')
    expect(page).toContain('Save Changes •')
    expect(page).not.toMatch(/schedulePut\(\s*['"]converter['"]/)
    const sources = converterSources().join('\n')
    expect(sources).toMatch(/\/settings\/converter/)
    expect(sources).toMatch(/isDirty/)
  })

  it('AC-33.18 HelpCard feature converter covers Spec 208-210 topics', () => {
    const help = readRequired(helpCardPath)
    expect(help).toMatch(/feature:\s*'downloader'\s*\|\s*'transcript'\s*\|\s*'tts'\s*\|\s*'settings'\s*\|\s*'converter'\s*\|\s*'capture'/)
    const content = readRequired(resolve(converterDir, 'convert-help-content.ts'))
    const lower = content.toLowerCase()
    for (const topic of HELP_TOPICS) {
      expect(lower).toContain(topic)
    }
    expect(content).toMatch(/sequential|one file/)
    const page = readRequired(pagePath)
    expect(page).toMatch(/HelpCard/)
    expect(page).toMatch(/feature=["']converter["']|feature=\{?'converter'\}?/)
    const shell = readRequired(appShellPath)
    expect(shell).toMatch(/'\/convert'/)
    expect(help).toMatch(/av-kit:\$\{?feature\}?-help:|av-kit:' \+ feature \+ '-help:/)
  })

  it('AC-33.19 open file and folder use existing IPC and stay disabled without a path', async () => {
    const { controlEnabled } = await import('../../src/renderer/src/features/converter/convert-controls')
    const noPath = [{ id: 'a', status: 'Done', output_path: null, input_path: 'C:/a.mp4' }]
    const withPath = [{ id: 'a', status: 'Done', output_path: 'C:/out/a.mp4', input_path: 'C:/a.mp4' }]
    const base = { selectedId: 'a' as const, processorState: 'Idle' as const, ffmpegAvailable: true }
    expect(controlEnabled('open-file', { ...base, items: noPath })).toBe(false)
    expect(controlEnabled('open-folder', { ...base, items: noPath })).toBe(false)
    expect(controlEnabled('open-file', { ...base, items: withPath })).toBe(true)
    const sources = converterSources().join('\n')
    expect(sources).toMatch(/openPath|open-path/)
    expect(sources).toMatch(/showItemInFolder|show-item-in-folder/)
    // MEU-45 supersession: the two toolbar buttons are retired; the same IPC is
    // reached from the kebab's open-file / open-folder items and, for a Done
    // row, from the card primary action.
    const menu = readRequired(queueCardMenuPath)
    expect(menu).toContain('open-file')
    expect(menu).toContain('open-folder')
    expect(sources).not.toContain('convert-open-file')
    expect(sources).not.toContain('convert-open-folder')
  })

  it('AC-33.20 ERROR_SURFACE shows ApiError and does not swallow Add or Start', () => {
    const sources = converterSources().join('\n')
    expect(sources).not.toMatch(/\.catch\(\s*\(\s*\)\s*=>\s*undefined/)
    expect(sources).toMatch(/ApiError/)
    expect(readRequired(pagePath)).toMatch(/error-banner/)
  })

  it('AC-33.21 Wave 8 convert-queue E2E is written and wired with W8 cases', () => {
    expect(existsSync(pagePath), pagePath).toBe(true)
    const e2e = readRequired(e2ePath)
    for (const caseId of ['W8-1', 'W8-2', 'W8-3', 'W8-4', 'W8-5', 'W8-6']) {
      expect(e2e).toContain(caseId)
    }
    expect(e2e).toMatch(/page\.route/)
    expect(e2e).toMatch(/\/conversions/)
    expect(e2e).toMatch(/AVKIT_APP_DATA/)
    expect(e2e).toMatch(/getByTestId\('nav-convert'\)/)
    expect(e2e).toMatch(/getByTestId\('convert-dropzone'\)\.toBeFocused|getByTestId\('convert-dropzone'\)\)\.toBeFocused/)
    const ids = readRequired(testIdsPath)
    for (const id of [...WAVE8_TESTIDS, ...WAVE8_EXTRA_TESTIDS]) {
      expect(ids).toContain(id)
    }
    const gui = readRequired(guiDocPath)
    expect(gui).toMatch(/\*\*36\*\*/)
  })

  it('AC-33.22 Wave0 shell and e2e-wiring include nav-convert as a fourth primary', () => {
    expect(readRequired(launchPath)).toContain('nav-convert')
    expect(readRequired(e2eWiringPath)).toContain('convert-queue.test.ts')
    expect(readRequired(e2eWiringPath)).toContain('nav-convert')
    expect(readRequired(shellHomePath)).toContain('nav:convert')
    expect(readRequired(shellHomePath)).toContain('nav-convert')
    const nav = readRequired(navPath)
    expect(nav).toContain('nav-convert')
    const registry = readRequired(registryPath)
    expect(registry).toContain('nav:convert')
    expect(readRequired(guiAuditPath)).toMatch(/converter|convert-/)
  })

  it('AC-33.23 G30-G35 and G36 hold on converter sources with no skip or raw hex className', () => {
    const sources = converterSources().join('\n')
    expect(sources).not.toMatch(/TODO|FIXME|NotImplementedError/)
    expect(sources).not.toMatch(/className=\{?[`'"][^`'"]*#[0-9a-fA-F]{3,8}/)
    expect(sources).not.toMatch(/duration-200|transition-all/)
    expect(sources).not.toMatch(/bg-blue-600/)
    expect(readRequired(pagePath)).toMatch(/variant=["']primary["'][\s\S]*convert-add|convert-add[\s\S]*variant=["']primary["']/)
    // MEU-45 supersession: the destructive affordance is the kebab's remove item
    // and the ConfirmModal's destructive confirm, not a toolbar convert-remove.
    expect(readRequired(queueCardMenuPath)).toMatch(/destructive/)
    expect(readRequired(pagePath)).toMatch(/destructive/)
    const unit = readFileSync(resolve(here, 'convert-page.test.ts'), 'utf8')
    expect(unit).not.toMatch(/it\.skip|describe\.skip|test\.skip|it\.only|describe\.only|test\.only/)
    expect(readRequired(formGuardPath)).toMatch(/btn-save-dirty/)
    expect(readRequired(ipcPath)).toContain('show-files-dialog')
  })

  it('AC-33.24 Convert GUI ships without regenerating OpenAPI or editing REST/MCP', () => {
    expect(existsSync(pagePath), pagePath).toBe(true)
    expect(existsSync(apiConversionsPath)).toBe(true)
    expect(existsSync(mcpDir)).toBe(true)
    const api = readFileSync(apiConversionsPath, 'utf8')
    expect(api).toContain('ConversionCreateIn')
    expect(api).not.toContain('MEU-33')
    const openapi = readRequired(openapiPath)
    expect(openapi).toContain('/api/v1/conversions')
    expect(openapi).not.toContain('MEU-33')
  })
})

describe('MEU-45 converter migration source contracts', () => {
  it('AC-45.7 ConvertQueueTable is deleted and the converter drops react-table', () => {
    expect(existsSync(tablePath), 'ConvertQueueTable.tsx must not survive').toBe(false)

    // Nothing anywhere in ui/src still names it, and the converter feature no
    // longer imports the table library it was the only local reason for.
    const uiSources = walkUiSources()
    const referrers = uiSources.filter((file) =>
      readFileSync(file, 'utf8').includes('ConvertQueueTable'),
    )
    expect(referrers.map(relative), 'a surviving reference fails mount-gate clause 2').toEqual([])

    const converter = converterSources().join('\n')
    expect(converter).not.toContain('@tanstack/react-table')

    // The page mounts the shared list instead.
    expect(existsSync(queueListPath)).toBe(true)
    const page = readRequired(pagePath)
    expect(page).toMatch(/from '\.\.\/\.\.\/components\/queue\/QueueList'/)
    expect(page).toContain('QueueList')
  })

  it('AC-45.16 every NEW_TESTIDS id is registered and no PRESERVED id is dropped', () => {
    const plan = resolve(repoRoot, 'docs/execution/plans/2026-09-02-p10-queue-card-migration')
    const sets = JSON.parse(readFileSync(resolve(plan, 'named-sets.json'), 'utf8')) as {
      NEW_TESTIDS: { value: string[] }
      PRESERVED_TESTIDS: { value: string[] }
      RETIRED_TOOLBAR_CONTROLS: { value: { converter: Record<string, unknown> } }
    }
    const registry = readRequired(testIdsPath)

    for (const id of sets.NEW_TESTIDS.value) {
      expect(registry, `NEW_TESTIDS ${id} missing from the registry`).toContain(`'${id}'`)
    }
    for (const id of sets.PRESERVED_TESTIDS.value) {
      expect(registry, `PRESERVED_TESTIDS ${id} dropped from the registry`).toContain(`'${id}'`)
    }
    // The retired converter ids are gone from the registry rather than left as
    // dead canon; each one's capability is asserted at its new home elsewhere.
    for (const id of Object.keys(sets.RETIRED_TOOLBAR_CONTROLS.value.converter)) {
      expect(registry, `retired ${id} still registered`).not.toContain(`'${id}'`)
    }
  })
})

describe('QUEUE_SCROLL_CONTAINER_RULE (execution X3, not an AC)', () => {
  it('page root fills main and the list scroller owns overflow, not listClasses', () => {
    const page = readRequired(pagePath)
    const list = readRequired(queueListPath)
    const root = page.match(/<section data-testid="convert-page" className="([^"]+)"/)
    expect(root, 'convert-page root className').not.toBeNull()
    const rootClasses = root?.[1].split(/\s+/) ?? []
    expect(rootClasses).toEqual(expect.arrayContaining(['h-full', 'min-h-0']))

    const regionAt = page.indexOf('data-testid="convert-queue-region"')
    expect(regionAt, 'convert-queue-region').toBeGreaterThan(-1)
    const regionOpen = page.slice(regionAt - 80)
    const regionClass = regionOpen.match(/className="([^"]+)"/)
    expect(regionClass?.[1].split(/\s+/)).toEqual(
      expect.arrayContaining(['flex-1', 'min-h-[20rem]']),
    )

    // Session 24 keeps the controls pane as the height donor and puts the
    // composed header before the scroller. Real Electron AC-52.6/AC-54.7
    // verifies the resulting height and keyboard reorder behavior.
    expect(page, 'controls pane absorbs the deficit').toContain(
      '<div className="flex min-h-0 flex-col gap-4 overflow-auto">',
    )
    const headerAt = page.indexOf('<QueueHeaderRow', regionAt)
    const listAt = page.indexOf('<QueueList', regionAt)
    expect(headerAt, 'header is inside the queue region').toBeGreaterThan(regionAt)
    expect(headerAt, 'header stays above the list scroller').toBeLessThan(listAt)
    const header = readRequired(resolve(queueComponentsDir, 'QueueHeaderRow.tsx'))
    expect(header).toContain('flex flex-wrap items-center')
    expect(header).toContain('data-testid={summaryTestId}')
    expect(header).toContain('<QueueToolbar {...toolbar} />')

    expect(page).toMatch(/overflow-auto[\s\S]{0,400}<QueueList/)
    expect(list).toContain("const listClasses = 'relative flex flex-col gap-2'")
    expect(list).not.toMatch(/listClasses = '[^']*overflow-auto/)
  })
})
