import { existsSync, readFileSync, readdirSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

import { CHORD_TABLE } from './fixtures/chord-table'
import { RENDERER_TO_MAIN_CHANNELS } from './ipc-channels'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')
const indexPath = resolve(repoRoot, 'docs/build-plan/gui-actions-index.md')
const registryPath = resolve(repoRoot, 'ui/src/renderer/src/registry/commandRegistry.ts')
const testIdsPath = resolve(repoRoot, 'ui/tests/e2e/test-ids.ts')
const openapiPath = resolve(repoRoot, 'openapi.committed.json')
const settingsDir = resolve(repoRoot, 'ui/src/renderer/src/features/settings')
const helpDir = resolve(repoRoot, 'ui/src/renderer/src/components/help')
const converterDir = resolve(repoRoot, 'ui/src/renderer/src/features/converter')
const captureDir = resolve(repoRoot, 'ui/src/renderer/src/features/capture')
/*
  MEU-45 scope correction: `queue-toolbar-start` and the rest of the retired
  converter toolbar now live in the shared queue package rather than under
  `features/converter`. The audited capability is unchanged — every audited
  testid exists in production source — so the scan follows the ids to their
  new home instead of the assertion being weakened. `helpDir` already sets
  the precedent of auditing a `components/` directory.
*/
const queueDir = resolve(repoRoot, 'ui/src/renderer/src/components/queue')

const SETTINGS_HELP_TESTIDS: Array<{ testid: string; indexId: string }> = [
  { testid: 'browse-download-path-btn', indexId: 'download:browse_path' },
  { testid: 'apply-defaults-btn', indexId: 'download:apply_quality_pending' },
  { testid: 'browse-ffmpeg-btn', indexId: 'settings:ffmpeg_browse' },
  { testid: 'browse-cookie-file-btn', indexId: 'settings:browse_cookie_file' },
  { testid: 'browse-transcript-dir-btn', indexId: 'settings:browse_transcript_dir' },
  { testid: 'browse-models-dir-btn', indexId: 'settings:browse_models_dir' },
  { testid: 'check-deps-btn', indexId: 'settings:check_deps' },
  { testid: 'copy-mcp-btn', indexId: 'settings:copy_mcp' },
  { testid: 'pin-mcp-btn', indexId: 'settings:pin_mcp' },
  { testid: 'mcp-copy-prompt-btn', indexId: 'settings:copy_mcp_prompt' },
  { testid: 'theme-dark-btn', indexId: 'settings:save' },
  { testid: 'theme-light-btn', indexId: 'settings:save' },
  { testid: 'readiness-card', indexId: 'settings:check_deps' },
  { testid: 'mcp-access-card', indexId: 'settings:copy_mcp' },
  { testid: 'mcp-token-present', indexId: 'settings:copy_mcp' },
  { testid: 'help-card', indexId: 'help:toggle' },
  { testid: 'help-search', indexId: 'help:toggle' },
  { testid: 'tts-espeak-copy-link-btn', indexId: 'settings:copy_espeak_link' },
  { testid: 'settings-copy-log-path', indexId: 'settings:copy_log_path' },
]

const CONVERT_AUDIT_TESTIDS: Array<{ testid: string; indexId: string }> = [
  { testid: 'convert-add', indexId: 'convert:add' },
  // MEU-45 supersession: convert-start retires into the shared queue toolbar
  // (RETIRED_TOOLBAR_CONTROLS.converter); the convert:start index row is
  // unchanged, only the testid that reaches it.
  { testid: 'queue-toolbar-start', indexId: 'convert:start' },
  { testid: 'convert-browse', indexId: 'convert:browse' },
  { testid: 'convert-dropzone', indexId: 'convert:drop' },
  { testid: 'convert-gpu-refresh', indexId: 'convert:gpu_refresh' },
  { testid: 'convert-output-dir-browse', indexId: 'convert:browse_output_dir' },
  { testid: 'convert-settings', indexId: 'convert:add' },
]

const CAPTURE_AUDIT_TESTIDS: Array<{ testid: string; indexId: string }> = [
  { testid: 'capture-region', indexId: 'capture:region' },
  { testid: 'capture-save', indexId: 'capture:save' },
  { testid: 'capture-open-folder', indexId: 'capture:open_folder' },
]

function resolveIpcChannel(cell: string): string | undefined {
  if (cell.includes('getMcpSetupPrompt')) return 'get-mcp-setup-prompt'
  if (cell.includes('writeClipboardText')) return 'write-clipboard-text'
  if (cell.includes('showDirectoryDialog')) return 'show-directory-dialog'
  if (cell.includes('showFileDialog')) return 'show-file-dialog'
  if (cell.includes('showFilesDialog')) return 'show-files-dialog'
  if (cell.includes('copyMcpConfig')) return 'copy-mcp-config'
  if (cell.includes('openPath')) return 'open-path'
  if (cell.includes('readTextFile')) return 'read-text-file'
  if (cell.includes('readClipboardText')) return 'read-clipboard-text'
  if (cell.includes('login-item-get')) return 'login-item-get'
  if (cell.includes('login-item-set')) return 'login-item-set'
  return undefined
}

function parsePaletteYesIds(markdown: string): string[] {
  const ids: string[] = []
  for (const line of markdown.split('\n')) {
    if (!line.startsWith('| `')) continue
    const cols = line.split('|').map((cell) => cell.trim())
    if (cols.length < 4) continue
    const id = cols[1].replace(/^`|`$/g, '')
    const palette = cols[3]
    if (palette === 'yes') {
      ids.push(id)
    }
  }
  return ids
}

function settingsHelpRows(markdown: string): Array<{ id: string; restIpc: string }> {
  const rows: Array<{ id: string; restIpc: string }> = []
  for (const line of markdown.split('\n')) {
    if (!line.startsWith('| `')) continue
    const cols = line.split('|').map((cell) => cell.trim())
    if (cols.length < 5) continue
    const id = cols[1].replace(/^`|`$/g, '')
    if (!id.startsWith('settings:') && !id.startsWith('help:') && !id.startsWith('download:browse_path') && id !== 'download:apply_quality_pending') {
      continue
    }
    rows.push({ id, restIpc: cols[4] })
  }
  return rows
}

function productionSources(): string {
  const chunks: string[] = []
  if (existsSync(settingsDir)) {
    for (const name of readdirSync(settingsDir)) {
      if (name.endsWith('.ts') || name.endsWith('.tsx')) {
        chunks.push(readFileSync(resolve(settingsDir, name), 'utf8'))
      }
    }
  }
  if (existsSync(helpDir)) {
    for (const name of readdirSync(helpDir)) {
      if (name.endsWith('.ts') || name.endsWith('.tsx')) {
        chunks.push(readFileSync(resolve(helpDir, name), 'utf8'))
      }
    }
  }
  if (existsSync(converterDir)) {
    for (const name of readdirSync(converterDir)) {
      if (name.endsWith('.ts') || name.endsWith('.tsx')) {
        chunks.push(readFileSync(resolve(converterDir, name), 'utf8'))
      }
    }
  }
  if (existsSync(captureDir)) {
    for (const name of readdirSync(captureDir)) {
      if (name.endsWith('.ts') || name.endsWith('.tsx')) {
        chunks.push(readFileSync(resolve(captureDir, name), 'utf8'))
      }
    }
  }
  if (existsSync(queueDir)) {
    for (const name of readdirSync(queueDir)) {
      if (name.endsWith('.ts') || name.endsWith('.tsx')) {
        chunks.push(readFileSync(resolve(queueDir, name), 'utf8'))
      }
    }
  }
  return chunks.join('\n')
}

describe('MEU-23 gui-actions audit', () => {
  it('AC-23.18 AUDIT_PALETTE registers every Palette=yes id in commandRegistry', () => {
    const index = readFileSync(indexPath, 'utf8')
    const registry = readFileSync(registryPath, 'utf8')
    const paletteIds = parsePaletteYesIds(index)
    expect(paletteIds).toContain('settings:check_deps')
    expect(paletteIds).toContain('help:toggle')
    for (const id of paletteIds) {
      expect(registry, id).toContain(id)
    }
  })

  it('AC-23.19 AUDIT_TESTIDS maps Phase 6 settings/help testids to index rows', () => {
    const index = readFileSync(indexPath, 'utf8')
    const testIds = readFileSync(testIdsPath, 'utf8')
    const sources = productionSources()
    for (const row of SETTINGS_HELP_TESTIDS) {
      expect(testIds).toContain(row.testid)
      expect(sources).toContain(row.testid)
      expect(index).toContain(row.indexId)
    }
    for (const row of CONVERT_AUDIT_TESTIDS) {
      expect(testIds).toContain(row.testid)
      expect(sources).toContain(row.testid)
      expect(index).toContain(row.indexId)
    }
    for (const row of CAPTURE_AUDIT_TESTIDS) {
      expect(testIds).toContain(row.testid)
      expect(sources).toContain(row.testid)
      expect(index).toContain(row.indexId)
    }
  })

  it('AC-23.20 AUDIT_REST_IPC resolves index REST/IPC cells to OpenAPI or preload channels', () => {
    const index = readFileSync(indexPath, 'utf8')
    const openapi = readFileSync(openapiPath, 'utf8')
    const preloadPath = resolve(repoRoot, 'ui/src/main/preload.ts')
    const preload = readFileSync(preloadPath, 'utf8')
    const rows = settingsHelpRows(index)
    expect(rows.length).toBeGreaterThan(0)
    for (const row of rows) {
      if (row.id === 'settings:login_item' || row.id === 'settings:start_minimized') {
        continue
      }
      const cell = row.restIpc
      if (cell.startsWith('route ') || cell === 'local' || cell.startsWith('local ')) {
        continue
      }
      if (cell.startsWith('`PUT /settings/{namespace}`') || cell.includes('PUT /settings/{namespace}')) {
        expect(openapi).toContain('/api/v1/settings/{namespace}')
        continue
      }
      if (cell.includes('POST /downloads/apply-defaults')) {
        expect(openapi).toContain('/api/v1/downloads/apply-defaults')
        continue
      }
      if (cell.includes('GET /health/dependencies')) {
        expect(openapi).toContain('/api/v1/health/dependencies')
        continue
      }
      const channel = resolveIpcChannel(cell)
      expect(channel, `${row.id} -> ${cell}`).toBeTruthy()
      const resolved = channel as string
      expect(RENDERER_TO_MAIN_CHANNELS).toContain(resolved)
      expect(preload).toMatch(new RegExp(resolved.replace(/-/g, '[-]')))
    }
    expect(preload).toMatch(/getSetupReadiness|get-setup-readiness/)
    expect(preload).toMatch(/getMcpAccessStatus|get-mcp-access-status/)
  })

  it('AC-61.21 ACTIONS_INDEX contains ACTION_IDS and kebab IPC resolves', () => {
    const index = readFileSync(indexPath, 'utf8')
    const testIds = readFileSync(testIdsPath, 'utf8')
    const sources = productionSources()
    const preload = readFileSync(resolve(repoRoot, 'ui/src/main/preload.ts'), 'utf8')
    expect(index).toContain('settings:login_item')
    expect(index).toContain('settings:start_minimized')
    expect(index).toContain('login-item-set')
    expect(testIds).toContain('start-at-sign-in-panel')
    expect(testIds).toContain('start-at-sign-in-checkbox')
    expect(testIds).toContain('start-minimized-checkbox')
    expect(sources).toContain('start-at-sign-in-panel')
    expect(sources).toContain('start-at-sign-in-checkbox')
    expect(RENDERER_TO_MAIN_CHANNELS).toContain('login-item-get')
    expect(RENDERER_TO_MAIN_CHANNELS).toContain('login-item-set')
    expect(preload).toMatch(/loginItemGet|login-item-get/)
    expect(preload).toMatch(/loginItemSet|login-item-set/)
  })
})

// MEU-88 ACTION_ROWS: the thumbnail-menu rows written at plan time (09 :783).
const MEU88_ACTION_ROWS: Array<{ id: string; kind: 'ipc' | 'rest' }> = [
  { id: 'capture:copy_path', kind: 'ipc' },
  { id: 'capture:copy_image', kind: 'ipc' },
  { id: 'capture:menu_delete', kind: 'rest' },
  { id: 'capture:batch_delete', kind: 'rest' },
]
const MEU88_TESTIDS = [
  'capture-filmstrip-menu',
  'capture-filmstrip-menu-copy-path',
  'capture-filmstrip-menu-copy-image',
  'capture-filmstrip-menu-delete',
]

function actionRestIpcCell(markdown: string, id: string): string | undefined {
  const line = markdown.split(/\r?\n/).find((row) => row.startsWith(`| \`${id}\` |`))
  return line?.split('|')[4]?.trim()
}

/** The channel a preload key invokes, read from the preload source (`key: (…) => ipcRenderer.invoke('channel'`). */
function preloadChannelFor(cell: string, preload: string): string | undefined {
  const key = cell.match(/^IPC `([A-Za-z]+)`$/)?.[1]
  if (key === undefined) {
    return undefined
  }
  return preload.match(new RegExp(String.raw`\b${key}: [^\n]*ipcRenderer\.invoke\('([a-z-]+)'`))?.[1]
}

describe('MEU-88 gui-actions audit', () => {
  it('AC-88.11 ACTION_ROWS resolve to registered preload channels, the OpenAPI capture path and production test ids', async () => {
    const { listRegisteredChannels } = await import('../../src/main/ipc')
    const registered = listRegisteredChannels()
    const index = readFileSync(indexPath, 'utf8')
    const openapi = readFileSync(openapiPath, 'utf8')
    const preload = readFileSync(resolve(repoRoot, 'ui/src/main/preload.ts'), 'utf8')
    for (const row of MEU88_ACTION_ROWS) {
      const cell = actionRestIpcCell(index, row.id)
      expect(cell, row.id).toBeTruthy()
      if (row.kind === 'ipc') {
        const channel = preloadChannelFor(cell as string, preload)
        expect(channel, `${row.id} -> ${cell}`).toBeTruthy()
        expect(registered).toContain(channel)
      } else {
        expect(cell).toContain('DELETE /captures/{id}')
        expect(openapi).toContain('"/api/v1/captures/{id}"')
      }
    }
    const testIds = readFileSync(testIdsPath, 'utf8')
    const sources = productionSources()
    for (const testid of MEU88_TESTIDS) {
      expect(testIds).toContain(`'${testid}'`)
      expect(sources, testid).toMatch(new RegExp(`["']${testid}["']`))
    }
  })

  it('AC-88.11 an IPC cell naming a key the preload does not expose resolves to no channel', () => {
    const preload = readFileSync(resolve(repoRoot, 'ui/src/main/preload.ts'), 'utf8')
    expect(preloadChannelFor('IPC `writeClipboardText`', preload)).toBe('write-clipboard-text')
    expect(preloadChannelFor('IPC `writeClipboardBogus`', preload)).toBeUndefined()
  })
})

// MEU-71 INDEX_ROW and NEW_TESTIDS (plan D-77; AC-23.20 precedent).
const MEU71_INDEX_ROW =
  '| `settings:copy_mcp_prompt` | Copy prompt | no | IPC `getMcpSetupPrompt` + `writeClipboardText` (no token) | specified | 07 / 06 |'
const MEU71_NEW_TESTIDS = [
  'mcp-client-select',
  'mcp-scope-select',
  'mcp-setup-prompt',
  'mcp-copy-prompt-btn',
  'mcp-prompt-status',
  'mcp-advanced',
  'mcp-advanced-summary',
]

describe('MEU-71 gui-actions audit', () => {
  it('AC-71.14 INDEX_ROW resolves to a registered channel the preload names; NEW_TESTIDS are in test-ids.ts and production source', async () => {
    const { listRegisteredChannels } = await import('../../src/main/ipc')
    const index = readFileSync(indexPath, 'utf8')
    const cell = actionRestIpcCell(index, 'settings:copy_mcp_prompt')
    expect(cell, 'settings:copy_mcp_prompt').toBeTruthy()
    const channel = resolveIpcChannel(cell as string)
    expect(channel).toBe('get-mcp-setup-prompt')
    expect(RENDERER_TO_MAIN_CHANNELS).toContain(channel)
    expect(listRegisteredChannels()).toContain(channel)
    const preload = readFileSync(resolve(repoRoot, 'ui/src/main/preload.ts'), 'utf8')
    expect(preload).toMatch(/getMcpSetupPrompt: [^\n]*=>\s*ipcRenderer\.invoke\('get-mcp-setup-prompt'/)
    const testIds = readFileSync(testIdsPath, 'utf8')
    const sources = productionSources()
    for (const testid of MEU71_NEW_TESTIDS) {
      expect(testIds, testid).toContain(`'${testid}'`)
      expect(sources, testid).toMatch(new RegExp(`["']${testid}["']`))
    }
  })

  it('AC-71.14 negative: INDEX_ROW appears once, directly after settings:pin_mcp', () => {
    const lines = readFileSync(indexPath, 'utf8').split(/\r?\n/)
    expect(lines.filter((line) => line.startsWith('| `settings:copy_mcp_prompt` |'))).toEqual([MEU71_INDEX_ROW])
    const at = lines.indexOf(MEU71_INDEX_ROW)
    expect(lines[at - 1].startsWith('| `settings:pin_mcp` |')).toBe(true)
  })
})

// MEU-93 CONVERT_BROWSE_INDEX (Session 40 plan; AC-71.14 pattern).
const MEU93_INDEX_ROW =
  '| `convert:browse_output_dir` | Output folder Browse | no | IPC `showDirectoryDialog` + `converter.output_dir` | specified | 08 / 06 |'

describe('MEU-93 gui-actions audit', () => {
  it('AC-93.5 CONVERT_BROWSE_INDEX resolves to a registered channel the preload invokes; the testid is in test-ids.ts, production source and CONVERT_AUDIT_TESTIDS', async () => {
    const { listRegisteredChannels } = await import('../../src/main/ipc')
    const index = readFileSync(indexPath, 'utf8')
    const cell = actionRestIpcCell(index, 'convert:browse_output_dir')
    expect(cell, 'convert:browse_output_dir').toBeTruthy()
    const channel = resolveIpcChannel(cell ?? '')
    expect(channel).toBe('show-directory-dialog')
    expect(RENDERER_TO_MAIN_CHANNELS).toContain(channel)
    expect(listRegisteredChannels()).toContain(channel)
    const preload = readFileSync(resolve(repoRoot, 'ui/src/main/preload.ts'), 'utf8')
    expect(preload).toMatch(/showDirectoryDialog: [^\n]*=>\s*ipcRenderer\.invoke\('show-directory-dialog'/)
    expect(readFileSync(testIdsPath, 'utf8')).toContain("'convert-output-dir-browse'")
    expect(productionSources()).toMatch(/["']convert-output-dir-browse["']/)
    expect(CONVERT_AUDIT_TESTIDS).toContainEqual({ testid: 'convert-output-dir-browse', indexId: 'convert:browse_output_dir' })
  })

  it('AC-93.5 negative: the row appears once, directly after convert:gpu_refresh', () => {
    const lines = readFileSync(indexPath, 'utf8').split(/\r?\n/)
    expect(lines.filter((line) => line.startsWith('| `convert:browse_output_dir` |'))).toEqual([MEU93_INDEX_ROW])
    const at = lines.indexOf(MEU93_INDEX_ROW)
    expect(lines[at - 1]?.startsWith('| `convert:gpu_refresh` |')).toBe(true)
  })

  it('AC-93.6 the MEU-93 test-ids block follows the MEU-71 block and registers convert-output-dir-browse once', () => {
    const registry = readFileSync(testIdsPath, 'utf8')
    const meu71 = '// MEU-71 Settings MCP setup prompt (additive IDs).'
    const marker = '// MEU-93 Path fields (additive IDs).'
    expect(registry.indexOf(meu71)).toBeGreaterThan(-1)
    expect(registry.indexOf(marker)).toBeGreaterThan(registry.indexOf(meu71))
    expect(registry.split(marker)[1] ?? '').toContain("export const CONVERT_OUTPUT_DIR_BROWSE = 'convert-output-dir-browse'")
    expect(registry.match(/'convert-output-dir-browse'/g)).toHaveLength(1)
    expect(registry.split('// MEU-51 primitive harness IDs.')[0]).not.toContain('convert-output-dir-browse')
  })
})

// MEU-96 INDEX_AMEND and CLIPBOARD_RIDER (Session 41 plan; AC-71.14 pattern).
const MEU96_ORDERED_ROWS: Array<{ id: string; after: string }> = [
  { id: 'appearance:dark', after: 'settings:check_deps' },
  { id: 'appearance:light', after: 'appearance:dark' },
  { id: 'page:primary', after: 'help:toggle' },
]
const MEU96_CLIPBOARD_ROWS: Array<{ id: string; after: string; testid: string }> = [
  { id: 'settings:copy_espeak_link', after: 'settings:start_minimized', testid: 'tts-espeak-copy-link-btn' },
  { id: 'settings:copy_log_path', after: 'settings:copy_espeak_link', testid: 'settings-copy-log-path' },
]

function indexRowLines(markdown: string, id: string): string[] {
  return markdown.split(/\r?\n/).filter((line) => line.startsWith(`| \`${id}\` |`))
}

function expectRowAfter(markdown: string, id: string, after: string): void {
  const lines = markdown.split(/\r?\n/)
  expect(indexRowLines(markdown, id), id).toHaveLength(1)
  const at = lines.findIndex((line) => line.startsWith(`| \`${id}\` |`))
  expect(lines[at - 1]?.startsWith(`| \`${after}\` |`), `${id} follows ${after}`).toBe(true)
}

describe('MEU-96 gui-actions audit', () => {
  it('AC-96.10 INDEX_AMEND 06 and the index legend name the context-aware palette model', () => {
    const gui = readFileSync(resolve(repoRoot, 'docs/build-plan/06-gui.md'), 'utf8')
    expect(gui).toContain('| Wiring | Ctrl+K / header field; every registry chord is bound from the registry (§Shortcut binding) |')
    expect(gui).toMatch(/\| Type \| `CommandRegistryEntry`:[^\n]*`appearance`[^\n]*`page`[^\n]*`stateful`[^\n]*`palette`/)
    expect(gui).toContain(
      'Palette-eligible actions are `Palette = yes` rows; the palette lists them by the context-aware model (§Command palette curation)',
    )
    const index = readFileSync(indexPath, 'utf8')
    expect(index).toContain('Eligible rows are listed per page and state (06 §Command palette curation)')
  })

  it('AC-96.10 INDEX_AMEND the Appearance and page:primary rows exist once, in place; convert:browse is Palette yes', () => {
    const index = readFileSync(indexPath, 'utf8')
    for (const row of MEU96_ORDERED_ROWS) {
      expectRowAfter(index, row.id, row.after)
    }
    const paletteYes = parsePaletteYesIds(index)
    expect(paletteYes).toContain('appearance:dark')
    expect(paletteYes).toContain('appearance:light')
    expect(paletteYes).not.toContain('page:primary')
    expect(paletteYes).toContain('convert:browse')
    expect(actionRestIpcCell(index, 'appearance:dark')).toContain('PUT /settings/{namespace}')
    expect(actionRestIpcCell(index, 'appearance:light')).toContain('PUT /settings/{namespace}')
  })

  it('AC-96.10 INDEX_AMEND the palette-eligible registry ids equal the Palette yes ids', async () => {
    const { listCommands } = await import('../../src/renderer/src/registry/commandRegistry')
    const eligible = listCommands()
      .filter((entry) => (entry as { palette?: false }).palette !== false)
      .map((entry) => entry.id)
      .sort()
    const paletteYes = parsePaletteYesIds(readFileSync(indexPath, 'utf8')).sort()
    expect(new Set(paletteYes).size).toBe(paletteYes.length)
    expect(eligible).toEqual(paletteYes)
  })

  it('AC-96.11 CLIPBOARD_RIDER the resolver maps writeClipboardText to the registered preload channel', async () => {
    const { listRegisteredChannels } = await import('../../src/main/ipc')
    expect(resolveIpcChannel('IPC `writeClipboardText`')).toBe('write-clipboard-text')
    expect(RENDERER_TO_MAIN_CHANNELS).toContain('write-clipboard-text')
    expect(listRegisteredChannels()).toContain('write-clipboard-text')
    const preload = readFileSync(resolve(repoRoot, 'ui/src/main/preload.ts'), 'utf8')
    expect(preloadChannelFor('IPC `writeClipboardText`', preload)).toBe('write-clipboard-text')
  })

  it('AC-96.11 CLIPBOARD_RIDER the two Settings copy rows follow settings:start_minimized and resolve to write-clipboard-text', () => {
    const index = readFileSync(indexPath, 'utf8')
    const testIds = readFileSync(testIdsPath, 'utf8')
    const sources = productionSources()
    for (const row of MEU96_CLIPBOARD_ROWS) {
      expectRowAfter(index, row.id, row.after)
      expect(parsePaletteYesIds(index)).not.toContain(row.id)
      const cell = actionRestIpcCell(index, row.id) ?? ''
      expect(cell).toContain('IPC `writeClipboardText`')
      expect(resolveIpcChannel(cell)).toBe('write-clipboard-text')
      expect(testIds, row.testid).toContain(`'${row.testid}'`)
      expect(sources, row.testid).toMatch(new RegExp(`["']${row.testid}["']`))
      expect(SETTINGS_HELP_TESTIDS).toContainEqual({ testid: row.testid, indexId: row.id })
    }
  })

  it('AC-96.11 CLIPBOARD_RIDER the MEU-96 test-ids block follows the MEU-93 block and registers settings-copy-log-path once', () => {
    const registry = readFileSync(testIdsPath, 'utf8')
    const meu93 = '// MEU-93 Path fields (additive IDs).'
    const marker = '// MEU-96 Palette curation (additive IDs).'
    expect(registry.indexOf(meu93)).toBeGreaterThan(-1)
    expect(registry.indexOf(marker)).toBeGreaterThan(registry.indexOf(meu93))
    expect(registry.split(marker)[1] ?? '').toContain("export const SETTINGS_COPY_LOG_PATH = 'settings-copy-log-path'")
    expect(registry.match(/'settings-copy-log-path'/g)).toHaveLength(1)
  })
})

describe('MEU-97 gui-actions audit', () => {
  it('AC-97.5 INDEX_AMEND each CHORD_TABLE id has its chord in its index Trigger cell', () => {
    const lines = readFileSync(indexPath, 'utf8').split(/\r?\n/)
    for (const [id, chord] of CHORD_TABLE) {
      const rows = lines.filter((line) => line.startsWith(`| \`${id}\` |`))
      expect(rows, id).toHaveLength(1)
      expect(rows[0]?.split('|')[2] ?? '', `${id} Trigger`).toContain(chord)
    }
  })
})

const MEU132_ROWS = ['capture:import', 'capture:drop', 'capture:paste'] as const

describe('MEU-132 gui-actions audit', () => {
  it('AC-132.20 ACTIONS_INDEX the three import rows follow capture:region and resolve to real channels, routes and ids', async () => {
    const { listRegisteredChannels } = await import('../../src/main/ipc')
    const registered = listRegisteredChannels()
    const index = readFileSync(indexPath, 'utf8')
    const lines = index.split(/\r?\n/)
    const at = (id: string): number[] =>
      lines.flatMap((line, i) => (line.startsWith(`| \`${id}\` |`) ? [i] : []))
    const region = at('capture:region')
    expect(region, 'capture:region').toHaveLength(1)
    MEU132_ROWS.forEach((id, offset) => {
      const rows = at(id)
      expect(rows, id).toHaveLength(1)
      expect(rows[0], `${id} position`).toBe((region[0] as number) + 1 + offset)
      expect(lines[rows[0] as number]?.split('|')[3]?.trim(), `${id} palette`).toBe('no')
    })

    const preload = readFileSync(resolve(repoRoot, 'ui/src/main/preload.ts'), 'utf8')
    const pasteCell = actionRestIpcCell(index, 'capture:paste') as string
    expect(preloadChannelFor(pasteCell, preload)).toBe('capture-paste-image')
    expect(registered).toContain('capture-paste-image')

    const importCell = actionRestIpcCell(index, 'capture:import') ?? ''
    expect(importCell).toContain('showFilesDialog')
    expect(importCell).toContain('POST /captures')
    expect(RENDERER_TO_MAIN_CHANNELS).toContain('show-files-dialog')

    const dropCell = actionRestIpcCell(index, 'capture:drop') ?? ''
    expect(dropCell).toContain('getPathForFile')
    expect(dropCell).toContain('POST /captures')
    expect(preload).toMatch(/\bgetPathForFile: /)

    expect(readFileSync(openapiPath, 'utf8')).toContain('"/api/v1/captures"')
    expect(readFileSync(testIdsPath, 'utf8')).toContain("'capture-import'")
    expect(productionSources()).toMatch(/["']capture-import["']/)
  })
})
