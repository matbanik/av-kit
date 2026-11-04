import { existsSync, readdirSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')
const ttsDir = resolve(repoRoot, 'ui/src/renderer/src/features/tts')
const pagePath = resolve(ttsDir, 'TTSPage.tsx')
const routerPath = resolve(repoRoot, 'ui/src/renderer/src/router.tsx')
const appShellPath = resolve(repoRoot, 'ui/src/renderer/src/components/layout/AppShell.tsx')
const registryPath = resolve(repoRoot, 'ui/src/renderer/src/registry/commandRegistry.ts')
const testIdsPath = resolve(repoRoot, 'ui/tests/e2e/test-ids.ts')
const e2ePath = resolve(repoRoot, 'ui/tests/e2e/tts-generate.test.ts')
const stylesPath = resolve(repoRoot, 'ui/src/renderer/src/styles.css')
const ipcPath = resolve(repoRoot, 'ui/src/main/ipc.ts')
const preloadPath = resolve(repoRoot, 'ui/src/main/preload.ts')
const envDtsPath = resolve(repoRoot, 'ui/src/renderer/src/env.d.ts')
const indexMainPath = resolve(repoRoot, 'ui/src/main/index.ts')
const apiTtsPath = resolve(repoRoot, 'packages/api/src/avkit_api/routes/tts.py')
const mcpDir = resolve(repoRoot, 'mcp-server')

const PREPARE_STEPS = [
  'punctuation',
  'symbols',
  'numbers',
  'currency',
  'all_caps',
  'chapter_markers',
  'urls_emails',
  'page_numbers',
  'whitespace',
  'chunk',
  'kokoro',
] as const

const WAVE2_TESTIDS = [
  'tts-page',
  'text-input',
  'model-manager',
  'voice-grid',
  'generate-btn',
  'speed-slider',
  'cleanup-pipeline',
  'preview-cleanup-btn',
] as const

const WAVE2_EXTRA_TESTIDS = [
  'load-file-btn',
  'paste-btn',
  'word-count',
  'sentence-count',
  'duration-estimate',
  // TA-1 (Session 27, MEU-64): preview-raw is removed (11-page-layout.md:122, :125).
  'preview-cleaned',
  'language-select',
  'format-select',
  'device-select',
  'output-path',
  'browse-output-btn',
  'cancel-btn',
  'segment-progress',
  'last-output',
  'open-output-btn',
  'open-output-folder-btn',
  'loaded-model',
  'unload-btn',
  'model-row',
  'model-get-btn',
  'model-load-btn',
  'voice-card',
  'download-progress',
] as const

const TTS_PALETTE_IDS = ['tts:prepare', 'tts:generate'] as const

function readRequired(path: string): string {
  expect(existsSync(path), path).toBe(true)
  return readFileSync(path, 'utf8')
}

function ttsSources(): string[] {
  expect(existsSync(ttsDir), ttsDir).toBe(true)
  return readdirSync(ttsDir)
    .filter((name) => name.endsWith('.ts') || name.endsWith('.tsx'))
    .map((name) => readFileSync(resolve(ttsDir, name), 'utf8'))
}

describe('MEU-22 TTS models', () => {
  it('AC-22.1 TTS_HOME routes /tts to TTSPage', () => {
    const src = readRequired(routerPath)
    expect(src).toMatch(/TTSPage/)
    expect(src).not.toMatch(/path:\s*'\/tts'[\s\S]{0,80}LazyPlaceholder/)
    const page = readRequired(pagePath)
    expect(page).toContain('tts-page')
    expect(page).toContain('text-input')
    expect(page).not.toMatch(/Connecting to backend/)
  })

  it('AC-22.2 WORD_COUNT SENTENCE_COUNT DURATION_WPM depend on speed', async () => {
    const mod = await import('../../src/renderer/src/features/tts/tts-stats')
    const stats = mod.textStats('Hello world. Second sentence!', 1.0)
    expect(stats.words).toBe(4)
    expect(stats.sentences).toBeGreaterThanOrEqual(2)
    expect(stats.durationSeconds).toBeGreaterThan(0)
    const faster = mod.textStats('Hello world. Second sentence!', 2.0)
    expect(faster.durationSeconds).toBeLessThan(stats.durationSeconds)
    expect(mod.textStats('', 1.0).durationSeconds).toBe(0)
  })

  it('AC-22.3 FILE_LOAD_OUT returns text and basename only', () => {
    const ipc = readRequired(ipcPath)
    expect(ipc).toMatch(/read-text-file/)
    expect(ipc).toMatch(/basename/)
    expect(ipc).toMatch(/text/)
    const env = readRequired(envDtsPath)
    expect(env).toMatch(/readTextFile/)
    expect(env).toMatch(/basename/)
    expect(env).not.toMatch(/readTextFile:[\s\S]{0,80}Promise<string>/)
    const preload = readRequired(preloadPath)
    expect(preload).toMatch(/readTextFile/)
    const page = readRequired(pagePath)
    expect(page).toContain('load-file-btn')
    expect(page).toMatch(/source_kind/)
    expect(page).toMatch(/source_path/)
  })

  it('AC-22.4 PASTE CLIPBOARD_READ uses deps.readClipboard', () => {
    const ipc = readRequired(ipcPath)
    expect(ipc).toMatch(/read-clipboard-text/)
    expect(ipc).toMatch(/readClipboard/)
    expect(ipc).not.toMatch(/case 'read-clipboard-text':\s*\r?\n\s*return \{ ok: true, value: '' \}/)
    const index = readRequired(indexMainPath)
    expect(index).toMatch(/clipboard\.readText|readClipboard/)
    const sources = ttsSources().join('\n')
    expect(sources).toContain('paste-btn')
    expect(sources).toMatch(/selectionStart|selectionEnd/)
    expect(sources).not.toMatch(/navigator\.clipboard/)
  })

  it('AC-22.5 PREPARE_STEPS defaults chapter_markers off', async () => {
    const mod = await import('../../src/renderer/src/features/tts/tts-prepare')
    expect(mod.PREPARE_STEPS).toEqual([...PREPARE_STEPS])
    expect(mod.PREPARE_STEPS).toHaveLength(11)
    expect(mod.PREPARE_DEFAULT_ON).not.toContain('chapter_markers')
    for (const step of PREPARE_STEPS) {
      if (step === 'chapter_markers') continue
      expect(mod.PREPARE_DEFAULT_ON).toContain(step)
    }
    const page = readRequired(pagePath)
    expect(page).toContain('cleanup-pipeline')
  })

  it('AC-22.6 PREPARE_BODY is text enabled_steps only', async () => {
    const mod = await import('../../src/renderer/src/features/tts/tts-commands')
    expect(mod.buildPrepareBody('', ['punctuation'])).toBeNull()
    const body = mod.buildPrepareBody('Hello', ['punctuation', 'kokoro'])
    expect(body).toEqual({ text: 'Hello', enabled_steps: ['punctuation', 'kokoro'] })
    expect(body).not.toHaveProperty('lang_code')
    expect(Object.keys(body ?? {}).sort()).toEqual(['enabled_steps', 'text'])
    const withChunk = mod.buildPrepareBody('Hello', ['kokoro'], 500)
    expect(withChunk).toEqual({ text: 'Hello', enabled_steps: ['kokoro'], chunk_max_chars: 500 })
    const page = readRequired(pagePath)
    expect(page).toContain('preview-cleanup-btn')
    expect(page).toContain('preview-cleaned')
    // TA-1 (Session 27, MEU-64): the raw preview pane is gone.
    expect(page).not.toContain('preview-raw')
    expect(page).toMatch(/chunkMaxChars|chunk_max_chars/)
  })

  it('AC-22.7 GENERATE_BODY omits output_path and full text on job', async () => {
    const mod = await import('../../src/renderer/src/features/tts/tts-commands')
    const body = mod.buildGenerateBody({
      text: 'Hello',
      voice: 'af_heart',
      speed: 1,
      format: 'MP3',
      enabled_steps: ['kokoro'],
      source_kind: 'inline',
    })
    expect(body).not.toHaveProperty('output_path')
    expect(body).not.toHaveProperty('lang_code')
    expect(body).toMatchObject({
      text: 'Hello',
      voice: 'af_heart',
      format: 'MP3',
      source_kind: 'inline',
    })
    const sources = ttsSources().join('\n')
    expect(sources).toMatch(/text_preview/)
    expect(sources).toMatch(/text_hash/)
    expect(sources).not.toMatch(/job\.text\b|fullText|full_text/)
  })

  it('AC-22.8 JOB_POLL uses Query v5 query.state.data and no GET /tts list', async () => {
    const { ttsPollInterval, QUERY_JOB_KEY } = await import(
      '../../src/renderer/src/features/tts/useTtsJob'
    )
    expect(QUERY_JOB_KEY).toEqual(['tts', 'job'])
    expect(ttsPollInterval({ state: { data: { status: 'Generating' } } })).toBe(1000)
    expect(
      ttsPollInterval({ state: { data: { status: 'Done' } }, runtime: { state: 'Downloading' } }),
    ).toBe(1000)
    expect(ttsPollInterval({ state: { data: { status: 'Done' } } })).toBe(5000)
    expect(ttsPollInterval({ state: { data: undefined } })).toBe(5000)
    const sources = ttsSources().join('\n')
    expect(sources).not.toMatch(/apiFetch\(\s*['"`]\/tts['"`]\s*\)/)
    expect(sources).not.toMatch(/items,\s*processor/)
  })

  it('AC-22.9 ENABLED_WHEN Cancel DELETE and no stop-btn', async () => {
    const { generateEnabled, cancelEnabled } = await import(
      '../../src/renderer/src/features/tts/tts-controls'
    )
    expect(generateEnabled({ isLoaded: false, text: 'hi', status: 'Idle' })).toBe(false)
    expect(generateEnabled({ isLoaded: true, text: 'hi', status: 'Idle' })).toBe(true)
    expect(generateEnabled({ isLoaded: true, text: 'hi', status: 'Pending' })).toBe(false)
    expect(generateEnabled({ isLoaded: true, text: 'hi', status: 'Generating' })).toBe(false)
    expect(cancelEnabled({ status: 'Generating' })).toBe(true)
    expect(cancelEnabled({ status: 'Pending' })).toBe(true)
    expect(cancelEnabled({ status: 'Idle' })).toBe(false)
    const sources = ttsSources().join('\n')
    expect(sources).toContain('cancel-btn')
    expect(sources).toMatch(/DELETE|method:\s*['"]DELETE['"]/)
    expect(sources).not.toContain('stop-btn')
    expect(sources).not.toContain('tts:stop')
  })

  it('AC-22.10 SEGMENT progress binds segments_done and segments_total', () => {
    const sources = ttsSources().join('\n')
    expect(sources).toContain('segment-progress')
    expect(sources).toMatch(/segments_done/)
    expect(sources).toMatch(/segments_total/)
    expect(sources).not.toMatch(/runtime\.fraction/)
  })

  it('AC-22.11 VOICES_ENVELOPE LANG_FILTER uses VoiceOut.language', async () => {
    const mod = await import('../../src/renderer/src/features/tts/tts-voices')
    const items = [
      {
        voice_id: 'af_heart',
        language: 'American English',
        gender: 'F',
        style_description: 'x',
      },
      {
        voice_id: 'bf_emma',
        language: 'British English',
        gender: 'F',
        style_description: 'y',
      },
    ]
    expect(mod.uniqueLanguages(items)).toEqual(['American English', 'British English'])
    expect(mod.filterVoices(items, 'American English').map((v) => v.voice_id)).toEqual(['af_heart'])
    const sources = ttsSources().join('\n')
    expect(sources).toContain('voice-grid')
    expect(sources).toContain('voice-card')
    expect(sources).toContain('language-select')
    expect(sources).not.toMatch(/lang_code/)
    expect(sources).not.toMatch(/English \(US\)/)
  })

  it('AC-22.12 SPEED_RANGE FORMAT_VALUES use SelectInput G30', () => {
    const sources = ttsSources().join('\n')
    expect(sources).toContain('speed-slider')
    expect(sources).toMatch(/0\.5/)
    expect(sources).toMatch(/2\.0|2/)
    expect(sources).toContain('format-select')
    expect(sources).toMatch(/SelectInput/)
    expect(sources).not.toMatch(/getG30Styles/)
    expect(sources).toMatch(/MP3/)
    expect(sources).toMatch(/WAV/)
    expect(sources).not.toMatch(/<select[\s>]/)
  })

  it('AC-22.13 OUTPUT_DEFAULT browse puts output_path only', () => {
    const sources = ttsSources().join('\n')
    expect(sources).toContain('output-path')
    expect(sources).toContain('browse-output-btn')
    expect(sources).toMatch(/showDirectoryDialog/)
    expect(sources).toMatch(/~\/Documents|Documents/)
    expect(sources).toMatch(/output_path/)
    expect(sources).not.toMatch(/models_directory/)
  })

  it('AC-22.14 RESUME_TEXT hydrates and PUTs SETTINGS_LEAVES only', () => {
    const sources = ttsSources().join('\n')
    expect(sources).toMatch(/\/settings\/tts/)
    expect(sources).toMatch(/input_text/)
    expect(sources).toMatch(/debounce|setTimeout|INPUT_DEBOUNCE/)
    expect(sources).not.toMatch(/models_directory/)
  })

  it('AC-22.15 model status unload VOID_204', () => {
    const sources = ttsSources().join('\n')
    expect(sources).toContain('loaded-model')
    expect(sources).toContain('unload-btn')
    expect(sources).toMatch(/\/models\/status/)
    expect(sources).toMatch(/\/models\/unload/)
    expect(sources).toMatch(/is_loaded/)
    expect(sources).toMatch(/memory_bytes/)
  })

  it('AC-22.16 CATALOG_ITEMS RUNTIME_BIND download progress', () => {
    const sources = ttsSources().join('\n')
    expect(sources).toContain('model-row')
    expect(sources).toContain('model-get-btn')
    expect(sources).toContain('download-progress')
    expect(sources).toMatch(/\/models\/available/)
    expect(sources).toMatch(/item\.id|item\.is_downloaded/)
    expect(sources).toMatch(/variant_id/)
    expect(sources).toMatch(/is_downloaded/)
    expect(sources).toMatch(/download-runtime|Downloading/)
    expect(sources).not.toMatch(/kokoro-pt-fp32['"]\s*,\s*['"]kokoro-onnx/)
  })

  it('AC-22.17 LOAD_BODY requires device DEVICE_VALUES', async () => {
    const mod = await import('../../src/renderer/src/features/tts/tts-commands')
    expect(() => mod.buildLoadBody({ variant_id: 'x' } as never)).toThrow()
    expect(mod.buildLoadBody({ variant_id: 'kokoro-onnx-fp32', device: 'cpu' })).toEqual({
      variant_id: 'kokoro-onnx-fp32',
      device: 'cpu',
    })
    expect(() => mod.buildLoadBody({ variant_id: 'x', device: 'gpu' })).toThrow()
    const sources = ttsSources().join('\n')
    expect(sources).toContain('model-load-btn')
    expect(sources).toContain('device-select')
    expect(sources).toMatch(/SelectInput/)
  })

  it('AC-22.18 ERROR_SURFACE does not swallow ApiError', () => {
    const sources = ttsSources().join('\n')
    expect(sources).not.toMatch(/\.catch\(\s*\(\s*\)\s*=>\s*undefined/)
    expect(sources).toMatch(/ApiError|error/)
    expect(readRequired(pagePath)).toMatch(/error-banner/)
  })

  it('AC-22.19 PALETTE_DELIVER AppShell owns tts palette ids', () => {
    const shell = readRequired(appShellPath)
    expect(shell).toMatch(/av-kit:tts:/)
    expect(shell).toMatch(/tts-commands|TTS_COMMANDS/)
    const registry = readRequired(registryPath)
    expect(registry).not.toMatch(/apiFetch/)
    for (const id of TTS_PALETTE_IDS) {
      expect(registry).toContain(id)
    }
  })

  it('AC-22.20 TTS_LOCAL_IDS exist and Settings models Browse does not', () => {
    const sources = ttsSources().join('\n')
    for (const id of [
      'load-file-btn',
      'paste-btn',
      'browse-output-btn',
      'cancel-btn',
      'open-output-btn',
      'open-output-folder-btn',
      'model-get-btn',
      'model-load-btn',
      'unload-btn',
    ]) {
      expect(sources).toContain(id)
    }
    expect(sources).not.toContain('settings:browse_models_dir')
    expect(sources).not.toContain('browse-models-dir')
  })

  it('AC-22.21 completed opens use openPath and showItemInFolder', () => {
    const sources = ttsSources().join('\n')
    expect(sources).toContain('open-output-btn')
    expect(sources).toContain('open-output-folder-btn')
    expect(sources).toMatch(/openPath/)
    expect(sources).toMatch(/showItemInFolder/)
  })

  it('AC-22.22 Wave 2 E2E written with installTtsSeam', () => {
    const e2e = readRequired(e2ePath)
    expect(e2e).toMatch(/installTtsSeam\s*\(/)
    expect(e2e).toMatch(/async\s+function\s+installTtsSeam/)
    expect(e2e).toMatch(/window\.fetch\s*=/)
    expect(e2e).toMatch(/__e2eSeamInstalled/)
    expect(e2e).toMatch(/E2E_SEAM_NEG/)
    expect(e2e).toMatch(/__e2e-unhandled/)
    for (const id of ['W2-1', 'W2-2', 'W2-3', 'W2-4', 'W2-5', 'W2-6']) {
      expect(e2e).toContain(id)
    }
    const page = readRequired(pagePath)
    const ids = readRequired(testIdsPath)
    for (const id of [...WAVE2_TESTIDS, ...WAVE2_EXTRA_TESTIDS]) {
      expect(page).toContain(id)
      expect(ids).toContain(id)
    }
  })

  it('AC-22.23 MEU-22 sources have no placeholder or skip guards', () => {
    const sources = ttsSources().join('\n')
    expect(sources).not.toMatch(/TODO|FIXME|NotImplementedError/)
    expect(sources).not.toMatch(/test\.skip|describe\.skip|it\.skip|\.only\(/)
    expect(existsSync(apiTtsPath)).toBe(true)
    expect(existsSync(pagePath)).toBe(true)
    expect(existsSync(mcpDir)).toBe(true)
  })

  it('AC-22.24 STATUS_COLORS SPEED_PRESETS and no raw hex', async () => {
    const { SPEED_PRESETS, STATUS_COLORS } = await import(
      '../../src/renderer/src/features/tts/tts-controls'
    )
    expect(SPEED_PRESETS).toEqual([0.8, 1.0, 1.1])
    expect(STATUS_COLORS.Generating).toMatch(/^bg-/)
    expect(STATUS_COLORS.Generating).not.toMatch(/#/)
    const sources = ttsSources().join('\n')
    expect(sources).not.toMatch(/className=\{?[`'"][^`'"]*#[0-9a-fA-F]{3,8}/)
    expect(sources).toMatch(/SelectInput/)
    const styles = readRequired(stylesPath)
    expect(styles.length).toBeGreaterThan(0)
  })
})

describe('MEU-64 cleanup buttons', () => {
  it('AC-64.3 Preview cleanup and Apply cleanup are secondary buttons, never ghost', () => {
    const page = readRequired(pagePath)
    for (const id of ['preview-cleanup-btn', 'apply-cleanup-btn']) {
      const at = page.indexOf(`data-testid="${id}"`)
      expect(at, id).toBeGreaterThan(-1)
      const tag = page.slice(page.lastIndexOf('<Button', at), page.indexOf('>', at))
      expect(tag, id).toContain('variant="secondary"')
      expect(tag, id).not.toContain('variant="ghost"')
    }
  })
})
