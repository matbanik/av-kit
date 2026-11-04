/** @vitest-environment jsdom */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { SettingsPage } from '../../src/renderer/src/features/settings/SettingsPage'

/**
 * MEU-93 PATH_ROWS (Session 40): the Settings capture-backup folder is a PathRow. The jsdom
 * harness is settings-emphasis.test.tsx's, with a capture fixture. The source clause follows
 * EC-2 (D-119): a showDirectoryDialog call counts as inside a PathRow onBrowse when it sits in
 * an onBrowse= handler, or in a helper function whose every reference sits in one.
 */

const here = dirname(fileURLToPath(import.meta.url))
const pagePath = resolve(here, '../../src/renderer/src/features/settings/SettingsPage.tsx')

let dialogAnswer: string | undefined

function mockApi(): void {
  window.api = {
    getBackendUrl: async () => 'http://127.0.0.1:51234/api/v1',
    getToken: async () => 'gui-nonce',
    logStartupMetric: () => undefined,
    showDirectoryDialog: async () => dialogAnswer,
    showFileDialog: async () => 'C:/e2e/sample.txt',
    showFilesDialog: async () => [],
    getPathForFile: () => 'C:/e2e/sample.mp4',
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
  } as Window['api']
}

function installFetch(): void {
  const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
    const json = (payload: unknown) =>
      new Response(JSON.stringify(payload), { status: 200, headers: { 'Content-Type': 'application/json' } })
    if (url.includes('/settings/app')) return json({ log_level: 'INFO', log_to_file: false, console_visible: true })
    if (url.includes('/settings/ui')) return json({ theme: 'dark' })
    if (url.includes('/settings/capture')) {
      return json({ inbox_dir: 'C:/inbox', hotkey: 'F2', copy_to_clipboard: false, close_to_tray: false, flatten_backup: true, backup_dir: '' })
    }
    if (url.includes('/health/dependencies')) {
      return json({ yt_dlp: { available: true, version: '2026.08.30' }, ffmpeg: { available: true, version: '7.1', path: 'C:/ffmpeg.exe' } })
    }
    if (url.includes('/settings/')) return json({})
    return new Response(JSON.stringify({ error: { message: 'unexpected' } }), { status: 422 })
  })
  vi.stubGlobal('fetch', fetchMock)
  window.fetch = fetchMock as typeof window.fetch
}

let client: QueryClient
let user: ReturnType<typeof userEvent.setup>

async function renderPage(): Promise<void> {
  render(createElement(QueryClientProvider, { client }, createElement(SettingsPage)))
  await vi.waitFor(() => {
    expect(screen.getByTestId('settings-page')).toBeTruthy()
  })
  await act(async () => {
    await new Promise((resolve) => setTimeout(resolve, 0))
  })
}

/** The [start, end) span of the brace group that opens at `open`. */
function braceSpan(src: string, open: number): [number, number] {
  let depth = 0
  for (let i = open; i < src.length; i += 1) {
    if (src[i] === '{') {
      depth += 1
    } else if (src[i] === '}') {
      depth -= 1
      if (depth === 0) {
        return [open, i + 1]
      }
    }
  }
  return [open, src.length]
}

/** EC-2: the 1-based lines of each showDirectoryDialog( call outside every PathRow onBrowse. */
function dialogCallsOutsideOnBrowse(src: string): number[] {
  const browseSpans = [...src.matchAll(/onBrowse=\{/g)].map((m) => braceSpan(src, (m.index ?? 0) + m[0].length - 1))
  const inBrowse = (at: number): boolean => browseSpans.some(([a, b]) => at >= a && at < b)
  const helpers = [...src.matchAll(/function\s+(\w+)\s*\([^)]*\)[^{]*\{/g)].map((m) => {
    const nameAt = (m.index ?? 0) + m[0].indexOf(m[1])
    const refs = [...src.matchAll(new RegExp(String.raw`\b${m[1]}\b`, 'g'))]
      .map((r) => r.index ?? 0)
      .filter((at) => at !== nameAt)
    return {
      span: braceSpan(src, (m.index ?? 0) + m[0].length - 1),
      onlyFromBrowse: refs.length > 0 && refs.every(inBrowse),
    }
  })
  return [...src.matchAll(/showDirectoryDialog\(/g)]
    .map((m) => m.index ?? 0)
    .filter((at) => !inBrowse(at) && !helpers.some((h) => at >= h.span[0] && at < h.span[1] && h.onlyFromBrowse))
    .map((at) => src.slice(0, at).split('\n').length)
}

beforeEach(() => {
  client = new QueryClient({ defaultOptions: { queries: { retry: false, gcTime: 0 } } })
  user = userEvent.setup()
  dialogAnswer = 'C:/e2e/outdir'
  mockApi()
  installFetch()
})

afterEach(() => {
  cleanup()
  client.clear()
  vi.unstubAllGlobals()
})

describe('MEU-93 Settings path fields (PATH_ROWS)', () => {
  it('AC-93.4 the source check (EC-2) flags a dialog call outside onBrowse and accepts a helper used only there', () => {
    const onClick = 'function Page() {\n  return <Button onClick={async () => { await window.api.showDirectoryDialog() }} />\n}'
    expect(dialogCallsOutsideOnBrowse(onClick)).toEqual([2])
    const sharedHelper = [
      'function Page() {',
      '  async function pick() { await window.api.showDirectoryDialog() }',
      '  return <><PathRow onBrowse={() => void pick()} /><Button onClick={() => void pick()} /></>',
      '}',
    ].join('\n')
    expect(dialogCallsOutsideOnBrowse(sharedHelper)).toEqual([2])
    const browseOnly = [
      'function Page() {',
      '  async function pick() { await window.api.showDirectoryDialog() }',
      '  return <><PathRow onBrowse={() => void pick()} /><PathRow onBrowse={async () => { await window.api.showDirectoryDialog() }} /></>',
      '}',
    ].join('\n')
    expect(dialogCallsOutsideOnBrowse(browseOnly)).toEqual([])
  })

  it('AC-93.4 every showDirectoryDialog call in SettingsPage sits in a PathRow onBrowse, and the backup folder is a PathRow', () => {
    const source = readFileSync(pagePath, 'utf8')
    expect(source.match(/showDirectoryDialog\(/g)?.length ?? 0).toBeGreaterThan(0)
    expect(dialogCallsOutsideOnBrowse(source)).toEqual([])
    expect(source).toMatch(/<PathRow\s+id="settings-capture-backup"/)
  })

  it('AC-93.4 capture backup folder: the placeholder default, Browse fills it, cancel keeps it empty', async () => {
    await renderPage()
    await vi.waitFor(() => {
      expect(screen.getByTestId('settings-leaf-capture-backup_dir').getAttribute('placeholder')).toBe('C:/inbox/.avkit-backup')
    })
    const input = screen.getByTestId('settings-leaf-capture-backup_dir') as HTMLInputElement
    expect(input.value).toBe('')
    const row = document.querySelector('label[for="settings-capture-backup"]')?.parentElement ?? null
    expect(row, 'the FormRow wrapper of settings-capture-backup').not.toBeNull()
    expect(row?.contains(input)).toBe(true)
    const browse = row === null ? null : within(row).queryByTestId('settings-capture-backup-browse')
    expect(browse, 'settings-capture-backup-browse in the same row').not.toBeNull()
    dialogAnswer = undefined
    await user.click(browse as HTMLElement)
    await act(async () => {
      await Promise.resolve()
    })
    expect(input.value).toBe('')
    dialogAnswer = 'C:/e2e/outdir'
    await user.click(browse as HTMLElement)
    await vi.waitFor(() => {
      expect(input.value).toBe('C:/e2e/outdir')
    })
  })
})
