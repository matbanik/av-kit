/** @vitest-environment jsdom */

import { QueryClientProvider } from '@tanstack/react-query'
import { act, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { existsSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { buildReorderBody } from '../../src/renderer/src/features/converter/convert-controls'
import * as convertCommands from '../../src/renderer/src/features/converter/convert-commands'
import { ConvertPage } from '../../src/renderer/src/features/converter/ConvertPage'
import { CONVERT_DIALOG_FILTERS } from '../../src/renderer/src/features/converter/convert-filters'
import { SettingsPage } from '../../src/renderer/src/features/settings/SettingsPage'
import { queryClient } from '../../src/renderer/src/lib/query-client'
import { expectBoundHint } from './helpers/bound-hint'

type FetchCall = { url: string; method: string; body?: unknown }

function jsonResponse(payload: unknown, status = 200): Response {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

function mockApi(showFilesDialog: (filters?: unknown) => Promise<string[]>): void {
  window.api = {
    getBackendUrl: async () => 'http://127.0.0.1:51234/api/v1',
    getToken: async () => 'gui-nonce',
    logStartupMetric: () => undefined,
    showDirectoryDialog: async () => 'C:/e2e/outdir',
    showFileDialog: async () => 'C:/e2e/sample.txt',
    showFilesDialog,
    getPathForFile: () => 'C:/e2e/sample.mp4',
    openPath: async () => undefined,
    showItemInFolder: async () => undefined,
    readClipboardText: async () => '',
    writeClipboardText: async () => undefined,
    readTextFile: async () => ({ text: '', basename: 'x.txt' }),
    copyMcpConfig: async () => ({ ok: true as const }),
    subscribeLogs: () => () => undefined,
    getLogSnapshot: async () => [],
    getSetupReadiness: async () => ({
      descriptorPresent: true,
      portOk: true,
      modelsDirWritable: true,
    }),
    getMcpAccessStatus: async () => ({ tokenPresent: true }),
    captureRegion: async () => undefined,
    getHotkeyStatus: async () => ({ accelerator: 'F2', registered: true, inUse: false }),
    loginItemGet: async () => ({
      supported: false,
      reason: 'not-packaged',
      enabled: false,
      minimized: false,
    }),
    loginItemSet: async () => ({
      supported: false,
      reason: 'not-packaged',
      enabled: false,
      minimized: false,
    }),
    onInboxChanged: () => () => undefined,
  }
}

describe('MEU-33 convert GUI runtime (exec r1 F1–F4)', () => {
  let user: ReturnType<typeof userEvent.setup>
  const fetches: FetchCall[] = []
  let converterGet = {
    output_dir: '~/Videos/av-kit',
    default_preset: 'archival' as const,
    skip_existing: true,
    gpu_preference: 'auto' as const,
  }
  const dialogFilters: unknown[] = []

  beforeEach(() => {
    user = userEvent.setup()
    fetches.length = 0
    dialogFilters.length = 0
    converterGet = {
      output_dir: '~/Videos/av-kit',
      default_preset: 'archival',
      skip_existing: true,
      gpu_preference: 'auto',
    }
    queryClient.clear()
    mockApi(async (filters) => {
      dialogFilters.push(filters)
      return ['C:/e2e/sample.mp4']
    })
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string, init?: RequestInit) => {
        const method = (init?.method ?? 'GET').toUpperCase()
        let body: unknown
        if (typeof init?.body === 'string' && init.body.length > 0) {
          body = JSON.parse(init.body)
        }
        fetches.push({ url: String(url), method, body })
        if (url.includes('/settings/downloader')) {
          return jsonResponse({
            path: 'C:/Downloads/av-kit',
            quality: '1080p',
            audio_only: false,
            audio_format: 'default',
            cookie_mode: 'none',
            cookie_browser: 'chrome',
            cookie_browser_profile: 'Default',
            cookie_file_path: '',
            archive_tracking: true,
            yt_dlp_debug: false,
            ffmpeg_path: 'C:/bin/ffmpeg.exe',
          })
        }
        if (url.includes('/settings/transcript')) {
          return jsonResponse({
            output_dir: 'C:/Transcripts',
            requests_per_hour: 300,
            delay_between_requests: 6,
            max_retries: 3,
            retry_delay: 30,
            batch_size: 50,
            pause_between_batches: 300,
            playlist_end: 0,
            max_words_per_document: 490000,
          })
        }
        if (url.includes('/settings/tts')) {
          return jsonResponse({
            models_directory: 'C:/models',
            voice: 'af_heart',
            speed: 1,
            output_format: 'MP3',
            output_path: 'C:/Documents',
            device: 'auto',
            chunk_max_chars: 250,
          })
        }
        if (url.includes('/settings/app')) {
          return jsonResponse({ log_level: 'INFO', log_to_file: false, console_visible: true })
        }
        if (url.includes('/settings/ui')) {
          return jsonResponse({ theme: 'dark' })
        }
        if (url.includes('/settings/converter')) {
          if (method === 'PUT') {
            converterGet = body as typeof converterGet
            return jsonResponse(converterGet)
          }
          return jsonResponse(converterGet)
        }
        if (url.includes('/health/dependencies')) {
          return jsonResponse({
            ffmpeg: { available: true, version: '7.1.2' },
            yt_dlp: { available: true },
          })
        }
        if (url.includes('/conversions/gpu')) {
          return jsonResponse({
            nvidia_nvenc: false,
            amd_amf: false,
            intel_qsv: false,
            vulkan: false,
            software_h265: true,
            software_h264: true,
            recommended_encoder: 'libx265',
            checked_at: '2026-08-26T00:00:00Z',
          })
        }
        if (url.includes('/conversions') && method === 'POST' && !url.includes('/gpu')) {
          return jsonResponse({ items: [{ id: 'job-1' }] }, 201)
        }
        if (url.includes('/conversions') && method === 'GET') {
          return jsonResponse({ items: [], processor: { state: 'Idle', current_job_id: null } })
        }
        return jsonResponse({ error: { message: 'unexpected' } }, 422)
      }),
    )
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    queryClient.clear()
  })

  async function renderConvert(): Promise<void> {
    await act(async () => {
      render(
        createElement(QueryClientProvider, { client: queryClient }, createElement(ConvertPage, null)),
      )
    })
    await vi.waitFor(() => {
      expect(screen.queryByTestId('convert-page')).not.toBeNull()
    })
  }

  async function renderSettings(): Promise<void> {
    await act(async () => {
      render(
        createElement(QueryClientProvider, { client: queryClient }, createElement(SettingsPage, null)),
      )
    })
    await vi.waitFor(() => {
      expect(screen.queryByTestId('convert-settings')).not.toBeNull()
    })
  }

  it('AC-33.4 saved default_preset archival is selected and POSTed on Add', async () => {
    expect(CONVERT_DIALOG_FILTERS.some((row) => row.name === 'Audio')).toBe(true)
    await renderConvert()
    await vi.waitFor(() => {
      const archival = screen.queryByTestId('convert-preset-archival')
      expect(archival?.className).toMatch(/bg-accent/)
    })
    await user.click(screen.getByTestId('convert-browse'))
    await user.click(screen.getByTestId('convert-add'))
    await vi.waitFor(() => {
      const post = fetches.find(
        (row) => row.method === 'POST' && row.url.includes('/conversions') && !row.url.includes('/gpu'),
      )
      expect(post?.body).toMatchObject({ kind: 'compress', preset: 'archival', paths: ['C:/e2e/sample.mp4'] })
    })
  })

  it('AC-33.5 Advanced disclosure is Compress-only', async () => {
    await renderConvert()
    expect(screen.queryByTestId('convert-advanced')).not.toBeNull()
    await user.click(screen.getByTestId('convert-task-cut'))
    expect(screen.queryByTestId('convert-advanced')).toBeNull()
    await user.click(screen.getByTestId('convert-task-compress'))
    expect(screen.queryByTestId('convert-advanced')).not.toBeNull()
  })

  it('AC-33.7 Browse requests video and audio filters', async () => {
    await renderConvert()
    await user.click(screen.getByTestId('convert-browse'))
    await vi.waitFor(() => {
      expect(dialogFilters[0]).toEqual(
        CONVERT_DIALOG_FILTERS.map((row) => ({
          name: row.name,
          extensions: [...row.extensions],
        })),
      )
    })
  })

  it('AC-33.16 converter settings PUT only on Save with strict four keys', async () => {
    await renderSettings()
    await vi.waitFor(() => {
      const sel = screen.queryByTestId('settings-leaf-default_preset')
      expect(sel).toBeInstanceOf(HTMLSelectElement)
      expect((sel as HTMLSelectElement).value).toBe('archival')
    })
    const putsBefore = fetches.filter((row) => row.method === 'PUT' && row.url.includes('/settings/converter'))
    expect(putsBefore).toHaveLength(0)
    const dir = screen.getByTestId('settings-leaf-converter-output_dir')
    if (!(dir instanceof HTMLInputElement)) {
      throw new Error('expected output_dir input')
    }
    await user.clear(dir)
    await user.type(dir, 'C:/converted')
    const save = screen.getByTestId('convert-settings-save')
    expect(save.className).toMatch(/btn-save-dirty/)
    expect(save.textContent).toContain('Save Changes')
    const putsWhileDirty = fetches.filter((row) => row.method === 'PUT' && row.url.includes('/settings/converter'))
    expect(putsWhileDirty).toHaveLength(0)
    await user.click(save)
    await vi.waitFor(() => {
      const puts = fetches.filter((row) => row.method === 'PUT' && row.url.includes('/settings/converter'))
      expect(puts).toHaveLength(1)
      expect(puts[0]?.body).toEqual({
        output_dir: 'C:/converted',
        default_preset: 'archival',
        skip_existing: true,
        gpu_preference: 'auto',
      })
    })
  })

  it('AC-33.17 page output/skip persist only via convert-page-save', async () => {
    await renderConvert()
    await vi.waitFor(() => {
      const archival = screen.queryByTestId('convert-preset-archival')
      expect(archival?.className).toMatch(/bg-accent/)
    })
    const dir = screen.getByTestId('convert-output-dir')
    if (!(dir instanceof HTMLInputElement)) {
      throw new Error('expected convert-output-dir')
    }
    await user.clear(dir)
    await user.type(dir, 'C:/page-out')
    const putsWhileDirty = fetches.filter((row) => row.method === 'PUT' && row.url.includes('/settings/converter'))
    expect(putsWhileDirty).toHaveLength(0)
    const save = screen.getByTestId('convert-page-save')
    expect(save.className).toMatch(/btn-save-dirty/)
    await user.click(save)
    await vi.waitFor(() => {
      const puts = fetches.filter((row) => row.method === 'PUT' && row.url.includes('/settings/converter'))
      expect(puts).toHaveLength(1)
      expect(puts[0]?.body).toMatchObject({ output_dir: 'C:/page-out', skip_existing: true })
    })
  })

  const converterPuts = (): FetchCall[] =>
    fetches.filter((row) => row.method === 'PUT' && row.url.includes('/settings/converter'))

  it('AC-93.2 Output folder is a PathRow whose Browse fills the field; only convert-page-save sends it', async () => {
    await renderConvert()
    await vi.waitFor(() => {
      expect((screen.getByTestId('convert-output-dir') as HTMLInputElement).value).toBe('~/Videos/av-kit')
    })
    const labelled = screen.queryAllByLabelText('Output folder')
    expect(labelled).toHaveLength(1)
    const field = labelled[0] as HTMLInputElement
    expect(field.getAttribute('data-testid')).toBe('convert-output-dir')
    const row = document.querySelector('label[for="convert-output-dir"]')?.parentElement ?? null
    expect(row, 'the FormRow wrapper of convert-output-dir').not.toBeNull()
    expect(row?.contains(field)).toBe(true)
    const browse = row === null ? null : within(row).queryByTestId('convert-output-dir-browse')
    expect(browse, 'convert-output-dir-browse in the same FormRow').not.toBeNull()
    await user.click(browse as HTMLElement)
    await vi.waitFor(() => {
      expect(field.value).toBe('C:/e2e/outdir')
    })
    expect(converterPuts(), 'Browse alone sends no PUT').toHaveLength(0)
    const save = screen.getByTestId('convert-page-save')
    expect(save.className).toMatch(/btn-save-dirty/)
    await user.click(save)
    await vi.waitFor(() => {
      expect(converterPuts()).toHaveLength(1)
      expect(converterPuts()[0]?.body).toMatchObject({ output_dir: 'C:/e2e/outdir' })
    })
  })

  it('AC-93.2 a cancelled Browse keeps the value and leaves the save clean', async () => {
    window.api.showDirectoryDialog = async () => undefined
    await renderConvert()
    const field = screen.getByTestId('convert-output-dir') as HTMLInputElement
    await vi.waitFor(() => {
      expect(field.value).toBe('~/Videos/av-kit')
    })
    const browse = screen.queryByTestId('convert-output-dir-browse')
    expect(browse, 'convert-output-dir-browse').not.toBeNull()
    await user.click(browse as HTMLElement)
    await act(async () => {
      await Promise.resolve()
    })
    expect(field.value).toBe('~/Videos/av-kit')
    expect(screen.getByTestId('convert-page-save').className).not.toMatch(/btn-save-dirty/)
    expect(converterPuts()).toHaveLength(0)
  })
})

// ---------------------------------------------------------------------------
// MEU-45 — ConvertPage on the shared queue surface (AC-45.6, .8, .9, .10, .11).
//
// The FIC's Test(s) column names `convert-page.test.ts` for these five, but that
// file is a node-environment static-source analysis: it reads sources off disk
// and never mounts React. AC-45.6/.8/.9/.10/.11 are all *runtime* contracts —
// rendered rows, an opened menu, an intercepted request body — so they live here,
// in the converter's jsdom behaviour suite, alongside the MEU-33 runtime cases
// they supersede. AC-45.7 stays in `convert-page.test.ts`, where it belongs: it
// is a pure source-tree assertion. (Recorded as a deviation in the handoff.)
// ---------------------------------------------------------------------------

describe('MEU-45 ConvertPage queue surface', () => {
  let user: ReturnType<typeof userEvent.setup>
  const fetches: FetchCall[] = []
  const opened: string[] = []
  let processorState: 'Idle' | 'Processing' | 'Paused' = 'Processing'

  /** Order matters: the reorder assertions read the rendered sequence. */
  function queueItems(): Record<string, unknown>[] {
    const rows = [
      { id: 'job-1', kind: 'compress', preset_id: 'balanced', status: 'Pending', position: 1 },
      { id: 'job-2', kind: 'cut', in_ms: 1000, out_ms: 4500, status: 'Processing', position: 2 },
      {
        id: 'job-3',
        kind: 'compress',
        preset_id: 'mobile',
        status: 'Done',
        position: 3,
        output_path: 'C:/out/job-3.mp4',
        gpu_encoder: 'h264_nvenc',
      },
      { id: 'job-4', kind: 'extract', stream_index: 1, status: 'Failed', position: 4 },
      { id: 'job-5', kind: 'compress', preset_id: null, status: 'Skipped', position: 5 },
    ]
    return rows.map((row) => ({
      input_path: 'C:/in/' + row.id + '.mkv',
      output_path: null,
      display_name: row.id + '.mkv',
      cq: null,
      scale_height: null,
      audio_mode: null,
      gpu_encoder: null,
      in_ms: null,
      out_ms: null,
      copy_mode: null,
      stream_index: null,
      preset_id: null,
      progress: 0,
      speed: null,
      eta: null,
      file_size: null,
      queue_position: row.position,
      ...row,
    }))
  }

  const RENDERED_IDS = ['job-1', 'job-2', 'job-3', 'job-4', 'job-5']

  beforeEach(() => {
    user = userEvent.setup()
    fetches.length = 0
    opened.length = 0
    processorState = 'Processing'
    queryClient.clear()
    mockApi(async () => ['C:/e2e/sample.mp4'])
    window.api.openPath = async (path: string) => {
      opened.push(path)
    }
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string, init?: RequestInit) => {
        const method = (init?.method ?? 'GET').toUpperCase()
        let body: unknown
        if (typeof init?.body === 'string' && init.body.length > 0) {
          body = JSON.parse(init.body)
        }
        const href = String(url)
        fetches.push({ url: href, method, body })
        if (href.includes('/settings/converter')) {
          return jsonResponse({
            output_dir: '~/Videos/av-kit',
            default_preset: 'archival',
            skip_existing: true,
            gpu_preference: 'auto',
          })
        }
        if (href.includes('/settings/ui')) {
          return jsonResponse({ theme: 'dark' })
        }
        if (href.includes('/health/dependencies')) {
          return jsonResponse({
            ffmpeg: { available: true, version: '7.1.2' },
            yt_dlp: { available: true },
          })
        }
        if (href.includes('/conversions/gpu')) {
          return jsonResponse({
            nvidia_nvenc: false,
            amd_amf: false,
            intel_qsv: false,
            vulkan: false,
            software_h265: true,
            software_h264: true,
            recommended_encoder: 'libx265',
            checked_at: '2026-08-26T00:00:00Z',
          })
        }
        if (href.includes('/conversions') && method === 'GET') {
          return jsonResponse({
            items: queueItems(),
            processor: { state: processorState, current_job_id: 'job-2' },
          })
        }
        return new Response(null, { status: 204 })
      }),
    )
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    queryClient.clear()
  })

  async function renderQueue(): Promise<void> {
    await act(async () => {
      render(
        createElement(QueryClientProvider, { client: queryClient }, createElement(ConvertPage, null)),
      )
    })
    await vi.waitFor(() => {
      expect(screen.queryAllByTestId('convert-queue-row')).toHaveLength(RENDERED_IDS.length)
    })
  }

  function row(id: string): HTMLElement {
    const el = screen.getAllByTestId('convert-queue-row').find((card) => card.dataset.jobId === id)
    if (el === undefined) {
      throw new Error('no rendered card for ' + id)
    }
    return el
  }

  function inside(scope: HTMLElement, testId: string): HTMLElement | null {
    return within(scope).queryByTestId(testId)
  }

  async function click(el: Element | null): Promise<void> {
    if (el === null) {
      throw new Error('cannot click a missing element')
    }
    await user.click(el)
  }

  /**
   * A keyboard gesture aimed at a card. `QueueCard` listens on the card
   * container, which no keyboard can focus, so the chord is delivered the way a
   * user delivers it: focus the card's open region — never the kebab, whose own
   * ArrowDown would open the menu — and press. `document.body` keeps its old
   * meaning of "no particular control": the key lands wherever focus already is
   * and reaches the document-level listeners on the way up.
   */
  async function keydown(
    el: HTMLElement,
    key: string,
    modifiers: { altKey?: boolean } = {},
  ): Promise<void> {
    if (el !== document.body) {
      within(el)
        .getByRole('button', { name: /^Open details for / })
        .focus()
    }
    const chord = '{' + key + '}'
    await user.keyboard(modifiers.altKey === true ? '{Alt>}' + chord + '{/Alt}' : chord)
  }

  function requests(fragment: string, method: string): FetchCall[] {
    return fetches.filter((call) => call.url.includes(fragment) && call.method === method)
  }

  async function openKebab(id: string): Promise<HTMLElement> {
    await click(inside(row(id), 'queue-card-kebab'))
    const menu = screen.queryByTestId('queue-card-menu')
    if (menu === null) {
      throw new Error('kebab menu did not open for ' + id)
    }
    return menu
  }

  function menuItems(menu: HTMLElement): HTMLElement[] {
    return within(menu).queryAllByRole('menuitem')
  }

  function menuAction(menu: HTMLElement, action: string): HTMLElement | null {
    return menuItems(menu).find((item) => item.dataset.menuAction === action) ?? null
  }

  it('AC-45.6 the page renders QueueList cards and a four-control toolbar, not a table', async () => {
    await renderQueue()

    const list = screen.queryByTestId('convert-queue')
    expect(list, 'the queue region survives under its preserved testid').not.toBeNull()
    expect(list?.tagName, 'QueueList is not a table').not.toBe('TABLE')
    expect(list?.querySelector('table'), 'no table survives inside the queue region').toBeNull()
    expect(screen.queryAllByTestId('convert-queue-row')).toHaveLength(RENDERED_IDS.length)
    for (const id of RENDERED_IDS) {
      expect(row(id)).not.toBeNull()
    }

    // DEC-2 — exactly TOOLBAR_CONTROLS interactive elements; a fifth fails.
    const toolbar = screen.queryByTestId('queue-toolbar')
    expect(toolbar, 'the reduced toolbar is mounted').not.toBeNull()
    const controls = Array.from(
      (toolbar as HTMLElement).querySelectorAll<HTMLElement>(
        'button, [role="button"], [role="menuitem"], a[href], input, select, textarea',
      ),
    )
    expect(controls, 'exactly four toolbar controls').toHaveLength(4)

    // Retired per-selection toolbar buttons are gone from the page entirely.
    for (const retired of ['convert-up', 'convert-down', 'convert-top', 'convert-bottom']) {
      expect(screen.queryByTestId(retired), retired + ' no longer renders').toBeNull()
    }
  })

  it('AC-45.8 the kebab exposes KEBAB_MENU_ORDER with unavailable actions absent', async () => {
    await renderQueue()

    // A finished middle row: every action is available, so the full order shows.
    const full = await openKebab('job-3')
    expect(menuItems(full).map((item) => item.dataset.menuAction)).toEqual([
      'open-file',
      'open-folder',
      'copy-location',
      'move-up',
      'move-down',
      'move-top',
      'move-bottom',
      'remove',
    ])
    expect(
      menuAction(full, 'copy-location')?.textContent?.trim(),
      'an output file exists',
    ).toBe('Copy path')
    for (const item of menuItems(full)) {
      expect(item.hasAttribute('disabled'), 'no menu item is ever disabled').toBe(false)
      expect(item.getAttribute('aria-disabled')).not.toBe('true')
    }
    await keydown(document.body, 'Escape')

    // The first, unfinished row: no output file and nothing above it, so
    // open-file, open-folder, move-up and move-top are ABSENT — not disabled.
    const first = await openKebab('job-1')
    const firstActions = menuItems(first).map((item) => item.dataset.menuAction)
    expect(firstActions).toEqual(['copy-location', 'move-down', 'move-bottom', 'remove'])
    expect(firstActions).not.toContain('open-file')
    expect(firstActions).not.toContain('move-up')
    expect(
      menuAction(first, 'copy-location')?.textContent?.trim(),
      'no output file yet',
    ).toBe('Copy URL')
    for (const item of menuItems(first)) {
      expect(item.hasAttribute('disabled')).toBe(false)
    }
    await keydown(document.body, 'Escape')

    // The last row loses move-down and move-bottom for the same reason.
    const last = await openKebab('job-5')
    const lastActions = menuItems(last).map((item) => item.dataset.menuAction)
    expect(lastActions).not.toContain('move-down')
    expect(lastActions).not.toContain('move-bottom')
    expect(lastActions).toContain('move-up')
  })

  it('AC-45.9 move actions and Alt+Arrow send the full REORDER_WIRE_CONTRACT permutation', async () => {
    await renderQueue()

    await click(menuAction(await openKebab('job-3'), 'move-up'))
    await vi.waitFor(() => {
      expect(requests('/conversions/reorder', 'PUT')).toHaveLength(1)
    })
    const kebabBody = requests('/conversions/reorder', 'PUT')[0].body
    expect(kebabBody).toEqual(buildReorderBody(RENDERED_IDS, 'job-3', 'up'))
    expect(kebabBody).toEqual({ job_ids: ['job-1', 'job-3', 'job-2', 'job-4', 'job-5'] })
    expect(kebabBody, 'never a {id, direction} body — the API 422s it').not.toHaveProperty(
      'direction',
    )

    // Alt+ArrowDown from inside the card issues the same request with `down`,
    // and does NOT open the kebab menu that a bare ArrowDown would.
    await keydown(row('job-1'), 'ArrowDown', { altKey: true })
    await vi.waitFor(() => {
      expect(requests('/conversions/reorder', 'PUT')).toHaveLength(2)
    })
    expect(requests('/conversions/reorder', 'PUT')[1].body).toEqual(
      buildReorderBody(RENDERED_IDS, 'job-1', 'down'),
    )
    expect(screen.queryByTestId('queue-card-menu')).toBeNull()

    await keydown(row('job-3'), 'ArrowUp', { altKey: true })
    await vi.waitFor(() => {
      expect(requests('/conversions/reorder', 'PUT')).toHaveLength(3)
    })
    expect(requests('/conversions/reorder', 'PUT')[2].body).toEqual(
      buildReorderBody(RENDERED_IDS, 'job-3', 'up'),
    )

    // Without Alt the arrow keys are navigation, not reordering.
    await keydown(row('job-3'), 'ArrowUp')
    await keydown(row('job-3'), 'ArrowDown')
    expect(requests('/conversions/reorder', 'PUT'), 'a bare arrow never reorders').toHaveLength(3)
  })

  it('AC-45.10 the primary action follows PRIMARY_ACTION_MAP and cancels without a confirm', async () => {
    await renderQueue()

    const primary = (id: string): HTMLElement | null => inside(row(id), 'queue-card-primary-action')

    // Statuses that map to `none` render no primary action at all.
    expect(primary('job-1'), 'Pending has no primary action').toBeNull()
    expect(primary('job-5'), 'Skipped has no primary action').toBeNull()

    // Done → Open file; Failed → Retry; in-flight → Cancel queue.
    expect(primary('job-3')?.textContent?.trim()).toBe('Open file')
    expect(primary('job-4')?.textContent?.trim()).toBe('Retry')

    const cancel = primary('job-2')
    expect(cancel, 'the in-flight row carries the cancel control').not.toBeNull()
    const cancelName =
      (cancel as HTMLElement).getAttribute('aria-label') ??
      (cancel as HTMLElement).textContent?.trim() ??
      ''
    expect(cancelName).toBe('Cancel queue')

    // CANCEL_LABEL_FORBIDDEN — exact-match, so `Cancel queue` itself is allowed.
    const forbidden = ['Cancel', 'Cancel item', 'Cancel download', 'Stop']
    for (const id of RENDERED_IDS) {
      const label = primary(id)?.textContent?.trim()
      if (label === undefined) {
        continue
      }
      expect(forbidden, id + ' renders a forbidden cancel label').not.toContain(label)
    }

    // USER_LOCKS — cancelling the queue takes effect with NO confirm dialog.
    await click(cancel)
    await vi.waitFor(() => {
      expect(requests('/conversions/cancel', 'POST')).toHaveLength(1)
    })
    expect(
      screen.queryByTestId('confirm-modal'),
      'cancel never opens a confirm',
    ).toBeNull()

    // Retry re-queues through the per-id reset endpoint.
    await click(primary('job-4'))
    await vi.waitFor(() => {
      expect(requests('/conversions/job-4/reset', 'POST')).toHaveLength(1)
    })

    // Open file goes through the existing IPC, not a fetch.
    await click(primary('job-3'))
    await vi.waitFor(() => {
      expect(opened).toEqual(['C:/out/job-3.mp4'])
    })
  })

  it('AC-45.11 Remove routes through the shared ConfirmModal with a verb label', async () => {
    const confirmSpy = vi.fn(() => true)
    vi.stubGlobal('confirm', confirmSpy)
    await renderQueue()

    await click(menuAction(await openKebab('job-1'), 'remove'))

    const modal = screen.queryByTestId('confirm-modal')
    expect(modal, 'G20_RULE — the shared portal modal, never window.confirm').not.toBeNull()
    expect(confirmSpy, 'window.confirm is forbidden').not.toHaveBeenCalled()
    expect((modal as HTMLElement).getAttribute('role')).toBe('dialog')
    expect(
      inside(modal as HTMLElement, 'confirm-modal-confirm')?.textContent?.trim(),
      'USER_LOCKS — a verb, never OK/Yes',
    ).toBe('Remove')

    // RETIRED_TESTIDS — the hand-rolled convert confirm is gone from the tree.
    for (const retired of ['convert-remove-confirm', 'convert-remove-confirm-cancel']) {
      expect(screen.queryByTestId(retired), retired).toBeNull()
    }

    // Dismissing issues no DELETE.
    await click(inside(modal as HTMLElement, 'confirm-modal-cancel'))
    expect(screen.queryByTestId('confirm-modal')).toBeNull()
    expect(requests('/conversions/job-1', 'DELETE'), 'dismiss is not a delete').toHaveLength(0)

    // Confirming does.
    await click(menuAction(await openKebab('job-1'), 'remove'))
    const reopened = screen.queryByTestId('confirm-modal')
    await click(inside(reopened as HTMLElement, 'confirm-modal-confirm'))
    await vi.waitFor(() => {
      expect(requests('/conversions/job-1', 'DELETE')).toHaveLength(1)
    })
    expect(requests('/conversions/job-1', 'DELETE')[0].body, 'files stay on disk').toBeUndefined()
  })

  /** MEU-96: the command-state module is new, so it is loaded after an existence check. */
  async function loadCommandState(): Promise<{ getCommandState: (page: string) => Partial<Record<string, boolean>> }> {
    const here = dirname(fileURLToPath(import.meta.url))
    expect(existsSync(resolve(here, '../../src/renderer/src/registry/command-state.ts')), 'registry/command-state.ts exists').toBe(
      true,
    )
    const specifier = '../../src/renderer/src/registry/command-state'
    return (await import(/* @vite-ignore */ specifier)) as {
      getCommandState: (page: string) => Partial<Record<string, boolean>>
    }
  }

  it('AC-96.5 PAGE_STATE Convert with an empty queue publishes convert:clear false', async () => {
    const state = await loadCommandState()
    processorState = 'Idle'
    const base = globalThis.fetch
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string, init?: RequestInit) => {
        const href = String(url)
        const method = (init?.method ?? 'GET').toUpperCase()
        if (/\/conversions\/?(\?.*)?$/.test(href) && method === 'GET') {
          fetches.push({ url: href, method })
          return jsonResponse({ items: [], processor: { state: 'Idle', current_job_id: null } })
        }
        return base(url, init)
      }),
    )
    await act(async () => {
      render(createElement(QueryClientProvider, { client: queryClient }, createElement(ConvertPage, null)))
    })
    await vi.waitFor(() => {
      expect(state.getCommandState('/convert')['convert:clear']).toBe(false)
    })
  })

  it('AC-96.7 CONFIRM_ROUTE the palette cancel event confirms first and Confirm cancels once', async () => {
    const confirmEvent = (convertCommands as unknown as Record<string, unknown>).CONVERT_CONFIRM_EVENT
    expect(confirmEvent).toBe('av-kit:convert:confirm')
    const name = String(confirmEvent)
    await renderQueue()

    await act(async () => {
      window.dispatchEvent(new CustomEvent(name, { detail: { kind: 'cancel' } }))
    })
    const modal = screen.queryByTestId('confirm-modal')
    expect(modal).not.toBeNull()
    expect(inside(modal as HTMLElement, 'confirm-modal-confirm')?.textContent?.trim()).toBe('Cancel conversions')
    expect(inside(modal as HTMLElement, 'confirm-modal-cancel')?.textContent?.trim()).toBe('Keep running')
    await click(inside(modal as HTMLElement, 'confirm-modal-cancel'))
    expect(screen.queryByTestId('confirm-modal')).toBeNull()
    expect(requests('/conversions/cancel', 'POST')).toHaveLength(0)

    await act(async () => {
      window.dispatchEvent(new CustomEvent(name, { detail: { kind: 'cancel' } }))
    })
    await click(inside(screen.getByTestId('confirm-modal'), 'confirm-modal-confirm'))
    await vi.waitFor(() => {
      expect(requests('/conversions/cancel', 'POST')).toHaveLength(1)
    })
  })

  it('AC-52.1/.2/.4 mounts one shared queue header with live selection, all counts, and toolbar', async () => {
    await renderQueue()
    const region = screen.getByTestId('convert-queue-region')
    const header = within(region).getByTestId('queue-header-row')
    expect(within(header).getByTestId('queue-select-all').tagName).toBe('INPUT')
    expect(within(header).getByTestId('convert-queue-summary')).toBeTruthy()
    expect(within(header).getByTestId('convert-processor')).toHaveTextContent('Processing')
    expect(within(header).getByTestId('queue-toolbar').querySelectorAll('button')).toHaveLength(4)
    expect(within(region).getAllByTestId('queue-header-row')).toHaveLength(1)

    const summary = within(header).getByTestId('convert-queue-summary')
    expect(summary.querySelectorAll('[data-tone]')).toHaveLength(5)
    expect(summary).not.toHaveTextContent('Cancelled')
    const requestsBefore = fetches.length
    await user.click(within(header).getByTestId('queue-status-more'))
    expect(within(header).getByTestId('queue-status-details')).toHaveTextContent('Cancelled: 0')
    expect(fetches).toHaveLength(requestsBefore)

    await user.click(within(header).getByTestId('queue-select-all'))
    expect(screen.getByTestId('bulk-selection-count')).toHaveTextContent('5')
    await user.click(within(header).getByTestId('queue-toolbar-pause'))
    await vi.waitFor(() => expect(requests('/conversions/pause', 'POST')).toHaveLength(1))
  })

  it('AC-52.3/.5 keeps Idle without a live chip and preserves header, bulk, scroller order', async () => {
    processorState = 'Idle'
    await renderQueue()
    const region = screen.getByTestId('convert-queue-region')
    const header = within(region).getByTestId('queue-header-row')
    expect(within(header).getByTestId('convert-processor')).not.toBeVisible()
    await user.click(within(header).getByTestId('queue-select-all'))
    const bulk = within(region).getByTestId('bulk-action-bar')
    const list = within(region).getByTestId('convert-queue')
    expect(header.compareDocumentPosition(bulk) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(bulk.compareDocumentPosition(list) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(list.parentElement?.className).toContain('overflow-auto')
    expect(region.className).toContain('min-h-[20rem]')
  })

  it('AC-54.1 task radios, exact GPU chip, and one always-visible Refresh keep their live IDs', async () => {
    await renderQueue()
    for (const [id, value] of [
      ['convert-task-compress', 'compress'],
      ['convert-task-cut', 'cut'],
      ['convert-task-extract', 'extract'],
    ] as const) {
      const radio = screen.getByTestId(id) as HTMLInputElement
      expect(radio.tagName).toBe('INPUT')
      expect(radio.type).toBe('radio')
      expect(radio.value).toBe(value)
    }
    expect(screen.getByTestId('convert-gpu-chip')).toHaveTextContent('Encoder: Software (libx265)')
    const refresh = screen.getAllByTestId('convert-gpu-refresh')
    expect(refresh).toHaveLength(1)
    expect(refresh[0]).toBeVisible()
    await user.click(refresh[0])
    await vi.waitFor(() => expect(requests('/conversions/gpu/refresh', 'POST')).toHaveLength(1))
  })

  it('AC-97.4 HINTS convert-add and convert-browse carry their chords', async () => {
    await renderQueue()
    expectBoundHint(screen.getByTestId('convert-add'), 'page:primary')
    expectBoundHint(screen.getByTestId('convert-browse'), 'convert:browse')
  })

  it('AC-54.2/.3 removes one duplicate staged chip locally, then Add posts only the remaining path', async () => {
    await renderQueue()
    const add = screen.getByTestId('convert-add')
    expect(add).toHaveTextContent('Add')
    await user.click(add)
    expect(requests('/conversions', 'POST')).toHaveLength(0)
    await user.click(screen.getByTestId('convert-browse'))
    await user.click(screen.getByTestId('convert-browse'))
    await vi.waitFor(() => expect(screen.getAllByTestId('convert-staged-remove')).toHaveLength(2))
    expect(add).toHaveTextContent('Add (2)')
    const mutationsBefore = fetches.filter((call) => call.method !== 'GET').length
    await user.click(screen.getAllByTestId('convert-staged-remove')[0])
    expect(screen.getAllByTestId('convert-staged-remove')).toHaveLength(1)
    expect(add).toHaveTextContent('Add (1)')
    expect(fetches.filter((call) => call.method !== 'GET')).toHaveLength(mutationsBefore)
    await user.click(add)
    await vi.waitFor(() => expect(requests('/conversions', 'POST')).toHaveLength(1))
    expect(requests('/conversions', 'POST')[0].body).toEqual({
      paths: ['C:/e2e/sample.mp4'], kind: 'compress', preset: 'archival',
    })
    expect(requests('/conversions/job-1', 'DELETE')).toHaveLength(0)
  })

  it('AC-54.4 native preset/cut/extract choices and controlled Advanced retain wire values', async () => {
    await renderQueue()
    const preset = screen.getByTestId('convert-preset-mobile') as HTMLInputElement
    expect(preset.type).toBe('radio')
    expect(preset.value).toBe('mobile')
    await user.click(preset)
    expect(preset.checked).toBe(true)
    const advanced = screen.getByTestId('convert-advanced')
    expect(advanced.tagName).toBe('BUTTON')
    expect(advanced).toHaveAttribute('aria-expanded', 'false')
    expect(screen.getByLabelText('CQ')).not.toBeVisible()
    await user.click(advanced)
    expect(advanced).toHaveAttribute('aria-expanded', 'true')
    expect(screen.getByLabelText('CQ')).toBeVisible()
    await user.click(screen.getByTestId('convert-task-cut'))
    expect(screen.queryByTestId('convert-advanced')).toBeNull()
    const copy = screen.getByTestId('convert-copy-reencode') as HTMLInputElement
    expect(copy.type).toBe('radio')
    expect(copy.value).toBe('reencode')
    await user.click(copy)
    expect(copy.checked).toBe(true)
    await user.click(screen.getByTestId('convert-task-extract'))
    const scope = screen.getByTestId('convert-extract-all') as HTMLInputElement
    expect(scope.type).toBe('radio')
    expect(scope.value).toBe('all')
    await user.click(scope)
    expect(scope.checked).toBe(true)
  })

  it('AC-54.5 Output footer keeps explicit Save, clean ghost and dirty primary state', async () => {
    await renderQueue()
    const output = screen.getByTestId('convert-output-dir') as HTMLInputElement
    const save = screen.getByTestId('convert-page-save')
    expect(save).toHaveClass('btn-ghost')
    expect(save).toHaveClass('h-7')
    await user.clear(output)
    await user.type(output, 'C:/e2e/new-output')
    expect(save).toHaveClass('btn-primary')
    expect(save).toHaveTextContent('Save Changes')
    expect(requests('/settings/converter', 'PUT')).toHaveLength(0)
    await user.click(save)
    await vi.waitFor(() => expect(requests('/settings/converter', 'PUT')).toHaveLength(1))
    expect(requests('/settings/converter', 'PUT')[0].body).toEqual({
      output_dir: 'C:/e2e/new-output', default_preset: 'archival',
      skip_existing: true, gpu_preference: 'auto',
    })
  })

  it('AC-54.6 carried encoder metadata and kind-only fallback preserve queue header and scroller', async () => {
    await renderQueue()
    expect(row('job-3')).toHaveTextContent('h264_nvenc')
    const fallback = row('job-5').querySelector('[data-testid="queue-card-meta"]')
    expect(fallback).toHaveTextContent('Compress')
    expect(fallback?.textContent).not.toContain('undefined')
    const region = screen.getByTestId('convert-queue-region')
    expect(within(region).getByTestId('queue-header-row')).toBeTruthy()
    expect(region.className).toContain('min-h-[20rem]')
    expect(within(region).getByTestId('convert-queue').parentElement?.className).toContain('overflow-auto')
  })
})

// ---------------------------------------------------------------------------
// MEU-47 — selection and bulk actions on the converter (AC-47.1, .3, .4, .6,
// .7, .8).
//
// A separate harness from the MEU-45 block above, because these cases need a
// queue the test can mutate mid-run: the snapshot clause of
// CLEAR_FINISHED_SEMANTICS is only observable if a row can turn `Done` between
// the click and the fan-out, and the partial-failure toast is only observable if
// one id's DELETE can answer 404 while its sibling succeeds.
// ---------------------------------------------------------------------------

describe('MEU-47 ConvertPage bulk selection', () => {
  let user: ReturnType<typeof userEvent.setup>
  const fetches: FetchCall[] = []
  /** Mutable so a test can change the queue while a fan-out is in flight. */
  let items: Record<string, unknown>[] = []
  /** ids whose per-row DELETE answers 404, as a server that lost the row would. */
  let deleteFails = new Set<string>()
  /** Called with each DELETEd id, so a test can mutate the queue mid-run. */
  let onDelete: (id: string) => void = () => undefined
  /** Status the reorder PUT answers with, so a test can reject the whole fold. */
  let reorderStatus = 204
  /** Gate held closed to observe the page WHILE a fan-out is still in flight. */
  let holdReorder: (() => void) | null = null

  function conversion(row: Record<string, unknown>): Record<string, unknown> {
    return {
      input_path: 'C:/in/' + String(row.id) + '.mkv',
      output_path: null,
      display_name: String(row.id) + '.mkv',
      kind: 'compress',
      preset_id: 'balanced',
      cq: null,
      scale_height: null,
      audio_mode: null,
      gpu_encoder: null,
      in_ms: null,
      out_ms: null,
      copy_mode: null,
      stream_index: null,
      progress: 0,
      speed: null,
      eta: null,
      file_size: null,
      queue_position: row.position,
      ...row,
    }
  }

  /** Two Done rows, so a partial sweep has both a success and a failure. */
  function mixedQueue(): Record<string, unknown>[] {
    return [
      conversion({ id: 'job-1', status: 'Pending', position: 1 }),
      conversion({ id: 'job-2', status: 'Processing', position: 2 }),
      conversion({ id: 'job-3', status: 'Done', position: 3, output_path: 'C:/out/job-3.mp4' }),
      conversion({ id: 'job-4', status: 'Failed', position: 4 }),
      conversion({ id: 'job-5', status: 'Done', position: 5, output_path: 'C:/out/job-5.mp4' }),
      conversion({ id: 'job-6', status: 'Skipped', position: 6 }),
    ]
  }

  beforeEach(() => {
    user = userEvent.setup()
    fetches.length = 0
    items = mixedQueue()
    deleteFails = new Set<string>()
    onDelete = () => undefined
    reorderStatus = 204
    holdReorder = null
    queryClient.clear()
    mockApi(async () => ['C:/e2e/sample.mp4'])
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string, init?: RequestInit) => {
        const method = (init?.method ?? 'GET').toUpperCase()
        let body: unknown
        if (typeof init?.body === 'string' && init.body.length > 0) {
          body = JSON.parse(init.body)
        }
        const href = String(url)
        fetches.push({ url: href, method, body })
        if (href.includes('/settings/converter')) {
          return jsonResponse({
            output_dir: '~/Videos/av-kit',
            default_preset: 'archival',
            skip_existing: true,
            gpu_preference: 'auto',
          })
        }
        if (href.includes('/settings/ui')) {
          return jsonResponse({ theme: 'dark' })
        }
        if (href.includes('/health/dependencies')) {
          return jsonResponse({
            ffmpeg: { available: true, version: '7.1.2' },
            yt_dlp: { available: true },
          })
        }
        if (href.includes('/conversions/gpu')) {
          return jsonResponse({
            nvidia_nvenc: false,
            amd_amf: false,
            intel_qsv: false,
            vulkan: false,
            software_h265: true,
            software_h264: true,
            recommended_encoder: 'libx265',
            checked_at: '2026-08-26T00:00:00Z',
          })
        }
        if (href.includes('/conversions') && method === 'GET') {
          return jsonResponse({
            items,
            processor: { state: 'Processing', current_job_id: 'job-2' },
          })
        }
        if (href.includes('/conversions/reorder') && method === 'PUT') {
          if (holdReorder !== null) {
            await new Promise<void>((resolve) => {
              holdReorder = resolve
            })
          }
          return reorderStatus === 204
            ? new Response(null, { status: 204 })
            : jsonResponse({ detail: 'reorder rejected' }, reorderStatus)
        }
        if (method === 'DELETE') {
          const id = href.split('/conversions/')[1] ?? ''
          onDelete(id)
          if (deleteFails.has(id)) {
            return jsonResponse({ detail: 'conversion ' + id + ' not found' }, 404)
          }
          items = items.filter((item) => item.id !== id)
          return new Response(null, { status: 204 })
        }
        return new Response(null, { status: 204 })
      }),
    )
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    queryClient.clear()
  })

  async function renderQueue(): Promise<void> {
    await act(async () => {
      render(
        createElement(QueryClientProvider, { client: queryClient }, createElement(ConvertPage, null)),
      )
    })
    await vi.waitFor(() => {
      expect(screen.queryAllByTestId('convert-queue-row')).toHaveLength(items.length)
    })
  }

  function row(id: string): HTMLElement {
    const el = screen.getAllByTestId('convert-queue-row').find((card) => card.dataset.jobId === id)
    if (el === undefined) {
      throw new Error('no rendered card for ' + id)
    }
    return el
  }

  function testId(scope: HTMLElement, id: string): HTMLElement | null {
    return within(scope).queryByTestId(id)
  }

  function required(scope: HTMLElement, id: string): HTMLElement {
    return within(scope).getByTestId(id)
  }

  /**
   * user-event models a modifier as a key held across the whole gesture rather
   * than a flag on one event, so a Shift+click is pressed the way a hand presses
   * it: hold Shift, click, release.
   */
  async function click(el: Element | null, modifiers: { shiftKey?: boolean } = {}): Promise<void> {
    if (el === null) {
      throw new Error('cannot click a missing element')
    }
    if (modifiers.shiftKey === true) {
      await user.keyboard('{Shift>}')
      await user.click(el)
      await user.keyboard('{/Shift}')
      return
    }
    await user.click(el)
  }

  /** Tick a row's checkbox the way a user does. */
  async function select(id: string, modifiers: { shiftKey?: boolean } = {}): Promise<void> {
    await click(testId(row(id), 'selection-checkbox'), modifiers)
  }

  function requests(fragment: string, method: string): FetchCall[] {
    return fetches.filter((call) => call.url.includes(fragment) && call.method === method)
  }

  function toast(): HTMLElement | null {
    return screen.queryByTestId('bulk-toast')
  }

  it('AC-47.3 a partial bulk run raises a G35 toast naming every failure reason', async () => {
    await renderQueue()

    // job-3 is gone server-side; job-5 is still there. The user selected both.
    deleteFails.add('job-3')
    await select('job-3')
    await select('job-5')

    const bar = required(document.body, 'bulk-action-bar')
    await click(testId(bar, 'bulk-remove'))
    await click(testId(required(document.body, 'confirm-modal'), 'confirm-modal-confirm'))

    await vi.waitFor(() => {
      expect(toast(), 'G35 — a partial run reports').not.toBeNull()
    })
    const note = toast() as HTMLElement
    // A live region, so the outcome reaches a screen reader without focus moving.
    expect(note.getAttribute('role')).toBe('status')
    expect(note.getAttribute('aria-live')).toBe('polite')

    const text = note.textContent ?? ''
    expect(text, 'the succeeded count').toContain('1')
    expect(text, 'clause 7 — a reason per failure').toContain('404')
    expect(text, 'the failure names the row it belongs to').toContain('job-3')
    // Dismissible (ERROR_SURFACE): the user can clear it, it is not a flash.
    await click(testId(note, 'bulk-toast-dismiss'))
    expect(toast()).toBeNull()

    // Clause 4: the success is not rolled back by its sibling's failure.
    expect(requests('/conversions/job-5', 'DELETE')).toHaveLength(1)
    await vi.waitFor(() => {
      expect(document.querySelector('[data-job-id="job-5"]')).toBeNull()
    })
  })

  it('AC-47.1 the bar appears above the list on selection and clears after a bulk action', async () => {
    await renderQueue()

    // No selection, no bar — but the header checkbox is always there.
    expect(screen.queryByTestId('bulk-action-bar')).toBeNull()
    expect(testId(document.body, 'queue-select-all'), 'the header is always mounted').not.toBeNull()

    await select('job-1')
    const bar = required(document.body, 'bulk-action-bar')
    expect(required(bar, 'bulk-selection-count').textContent).toContain('1')

    // USER_LOCKS — sticky ABOVE the list: the bar precedes the queue region in
    // document order, inside the same panel.
    const list = required(document.body, 'convert-queue')
    expect(
      bar.compareDocumentPosition(list) & Node.DOCUMENT_POSITION_FOLLOWING,
      'the bar is rendered above the list',
    ).toBeTruthy()

    // Shift+click extends the selection to an inclusive range in render order.
    await select('job-4', { shiftKey: true })
    expect(required(document.body, 'bulk-selection-count').textContent).toContain('4')

    // Clear selection returns the page to its unselected state.
    await click(testId(required(document.body, 'bulk-action-bar'), 'bulk-clear-selection'))
    expect(screen.queryByTestId('bulk-action-bar')).toBeNull()
    for (const box of screen.queryAllByTestId<HTMLInputElement>('selection-checkbox')) {
      expect(box.checked, 'every row checkbox is cleared').toBe(false)
    }

    // SELECTION_MODEL — the selection is cleared once a bulk action completes,
    // so the bar never survives holding ids the server has already dropped.
    await select('job-1')
    await click(testId(required(document.body, 'bulk-action-bar'), 'bulk-remove'))
    await click(testId(required(document.body, 'confirm-modal'), 'confirm-modal-confirm'))
    await vi.waitFor(() => {
      expect(screen.queryByTestId('bulk-action-bar')).toBeNull()
    })
  })

  it('AC-47.6 bulk-remove confirms with the verb label and dismissing issues no DELETE', async () => {
    const confirmSpy = vi.fn(() => true)
    vi.stubGlobal('confirm', confirmSpy)
    await renderQueue()

    await select('job-1')
    await select('job-4')
    await click(testId(required(document.body, 'bulk-action-bar'), 'bulk-remove'))

    const modal = required(document.body, 'confirm-modal')
    expect(modal.getAttribute('role'), 'G20_RULE — the shared portal dialog').toBe('dialog')
    expect(confirmSpy, 'window.confirm is forbidden').not.toHaveBeenCalled()
    expect(
      required(modal, 'confirm-modal-confirm').textContent?.trim(),
      'USER_LOCKS — a verb-labelled confirm, never OK/Yes',
    ).toBe('Remove 2 items')

    await click(testId(modal, 'confirm-modal-cancel'))
    expect(screen.queryByTestId('confirm-modal')).toBeNull()
    expect(
      fetches.filter((call) => call.method === 'DELETE'),
      'dismissal issues no request at all',
    ).toHaveLength(0)
    // The selection survives a dismissal — the user has not changed their mind
    // about what is selected, only about deleting it.
    expect(required(document.body, 'bulk-selection-count').textContent).toContain('2')
  })

  it('AC-47.7 Clear finished sweeps only CLEAR_FINISHED_SNAPSHOT_STATUSES and survives a mid-run 404', async () => {
    await renderQueue()

    // job-3's DELETE will 404, and the moment the first request goes out job-1
    // finishes. Neither may change which ids the run attempts.
    deleteFails.add('job-3')
    onDelete = () => {
      items = items.map((item) =>
        item.id === 'job-1' ? { ...item, status: 'Done', output_path: 'C:/out/job-1.mp4' } : item,
      )
    }

    await click(testId(required(document.body, 'queue-toolbar'), 'queue-toolbar-clear-finished'))

    await vi.waitFor(() => {
      expect(toast()).not.toBeNull()
    })

    const deletes = fetches
      .filter((call) => call.method === 'DELETE')
      .map((call) => call.url.split('/conversions/')[1] ?? '')
    // Only the two rows that were Done when the button was clicked.
    expect(deletes.slice().sort(), 'only CLEAR_FINISHED_SNAPSHOT_STATUSES rows').toEqual([
      'job-3',
      'job-5',
    ])
    expect(deletes, 'clause 1 — a row that becomes Done mid-run is not swept').not.toContain('job-1')
    expect(deletes, 'Failed is not swept').not.toContain('job-4')
    expect(deletes, 'Skipped is not swept').not.toContain('job-6')
    // Clause 2/3: every snapshotted id attempted exactly once, the 404 included.
    expect(deletes.filter((id) => id === 'job-3'), 'attempted exactly once').toHaveLength(1)
    expect(deletes.filter((id) => id === 'job-5'), 'the 404 did not abort the run').toHaveLength(1)

    // Clause 5: the queue record goes, the file does not — no purge flag, and no
    // request to any file-deleting path.
    for (const call of fetches.filter((entry) => entry.method === 'DELETE')) {
      expect(call.body, 'no purge payload').toBeUndefined()
      expect(call.url).not.toMatch(/purge|files/)
    }

    // Clause 7: a report the user can read, naming the failure.
    expect(toast()?.textContent).toContain('404')
    expect(toast()?.textContent).toContain('job-3')
  })

  it('AC-47.8 no bulk action issues a request to a /bulk path', async () => {
    await renderQueue()

    // Re-tick before each verb: `SELECTION_MODEL` releases the selection after a
    // bulk action COMPLETES, so one gesture is one action. (Setup only — the
    // assertions below are unchanged. Exec-review round 1, Finding 2: the
    // earlier version of this test chained three verbs off a single tick, which
    // only worked because the selection was wrongly being kept alive.)
    for (const verb of ['bulk-move-top', 'bulk-move-bottom', 'bulk-retry']) {
      await click(required(document.body, 'queue-select-all'))
      await click(testId(required(document.body, 'bulk-action-bar'), verb))
    }
    await click(testId(required(document.body, 'queue-toolbar'), 'queue-toolbar-clear-finished'))

    // BULK_ENDPOINT_POLICY — POST /{queue}/bulk does not exist and may not be
    // invented; every bulk action is a fan-out of the per-id endpoints.
    for (const call of fetches) {
      expect(call.url, 'no /bulk endpoint').not.toMatch(/\/bulk\b/)
    }
    expect(
      requests('/conversions/reorder', 'PUT').length,
      'a reorder PUT per selected row, not one batched call',
    ).toBeGreaterThan(1)
  })
  it('AC-47.1 R1-F2 a bulk move that moved NOTHING still releases the selection', async () => {
    /*
      Exec-review round 1, Finding 2. `SELECTION_MODEL` clears the selection
      after a bulk action COMPLETES; an earlier version cleared only when the
      reconciled order differed from the order at click time, which made a
      frozen rule depend on react-query render timing and left a stale
      selection live after a run in which every request was rejected.
    */
    await renderQueue()
    reorderStatus = 500

    await click(required(document.body, 'queue-select-all'))
    const bar = required(document.body, 'bulk-action-bar')
    await click(testId(bar, 'bulk-move-top'))

    expect(
      requests('/conversions/reorder', 'PUT').length,
      'the fold ran; every step was rejected',
    ).toBeGreaterThan(0)
    await vi.waitFor(() => {
      expect(
        screen.queryByTestId('bulk-action-bar'),
        'a completed bulk action releases the selection even when nothing moved',
      ).toBeNull()
    })
    expect(toast()?.textContent ?? '', 'the failures are still reported').toContain('failed')
  })

  it('AC-47.7a R1-F3 a bulk move reconciles ONCE, not once per folded step', async () => {
    /*
      Exec-review round 1, Finding 3. The pages handed `bulkReorder` the
      RECONCILING single-row command, so every accepted step awaited an
      invalidate and the list refetched N times inside one gesture — against
      CLEAR_FINISHED_SEMANTICS clause 6, and visibly re-rendering the queue
      between the steps of one absolute permutation.
    */
    await renderQueue()

    await click(required(document.body, 'queue-select-all'))
    const mark = fetches.length
    await click(testId(required(document.body, 'bulk-action-bar'), 'bulk-move-bottom'))

    const isList = (call: { url: string; method: string }): boolean =>
      call.method === 'GET' && /\/conversions\/?$/.test(new URL(call.url).pathname)

    await vi.waitFor(() => {
      expect(fetches.slice(mark).filter(isList).length).toBeGreaterThan(0)
    })
    const after = fetches.slice(mark)
    const puts = after.filter(
      (call) => call.method === 'PUT' && call.url.includes('/conversions/reorder'),
    )
    const lists = after.filter(isList)
    expect(puts.length, 'one PUT per selected row - the fold is unchanged').toBeGreaterThan(1)
    expect(lists.length, 'exactly one list refetch for the whole fan-out').toBe(1)
    expect(
      after.indexOf(lists[0]) > after.indexOf(puts[puts.length - 1]),
      'the single reconcile happens AFTER the last request, not between steps',
    ).toBe(true)
  })

  it('AC-47.4 R1-F6 the acting verbs are dead while a fan-out is in flight', async () => {
    /*
      Exec-review round 1, Finding 6. The bar took no busy input, so a second
      click during a slow run duplicated the per-id mutations, and two
      overlapping moves each sent an absolute permutation derived from the same
      stale order — the later one silently clobbering the earlier.
    */
    await renderQueue()
    holdReorder = () => undefined

    await click(required(document.body, 'queue-select-all'))
    const bar = required(document.body, 'bulk-action-bar')
    await click(testId(bar, 'bulk-move-top'))

    await vi.waitFor(() => {
      expect(requests('/conversions/reorder', 'PUT').length).toBe(1)
    })

    const live = required(document.body, 'bulk-action-bar')
    for (const control of ['bulk-retry', 'bulk-move-top', 'bulk-move-bottom', 'bulk-remove']) {
      expect(
        (required(live, control) as HTMLButtonElement).disabled,
        control + ' must not accept a second gesture mid-run',
      ).toBe(true)
    }
    // The escape hatch stays live: it touches no endpoint, and a slow run is
    // exactly when the user reaches for it.
    expect((required(live, 'bulk-clear-selection') as HTMLButtonElement).disabled).toBe(false)

    await click(testId(live, 'bulk-move-bottom'))
    expect(
      requests('/conversions/reorder', 'PUT').length,
      'the disabled control issued no request',
    ).toBe(1)

    const release = holdReorder
    holdReorder = null
    await act(async () => {
      release?.()
    })
  })
})

// ---------------------------------------------------------------------------
// MEU-49 — drag reorder on the converter queue.
//
// Covers AC-49.21, AC-49.22, AC-49.23 (preservation), AC-49.32-49.35, AC-49.37
// and AC-49.38. The two repo-wide facts (AC-49.24 testid registry, AC-49.39 the
// G37 migration) are asserted once, in the downloader behaviour file — they are
// properties of the tree, not of a page, and restating them here would be a
// second copy to keep in sync rather than a second piece of evidence.
//
// `JSDOM_RECT_RULE`: jsdom reports every rect as all-zero, so dnd-kit's own
// collision detection can never resolve a drop here. Both dnd-kit packages are
// therefore mocked at module scope as pass-through fragments that record the
// props they were handed, which is the only way to reach `onDragEnd` without a
// completed drag. `vi.mock` is file-scoped and hoisted, so the MEU-33/45/47
// describes above also render against the stubs — harmless, since none of them
// asserts anything about dragging and the stubs render children exactly as the
// real components do. The pointer gesture itself is proved once, against real
// Electron, by `E2E_DRAG_DRIVER`.
// ---------------------------------------------------------------------------

const dnd = vi.hoisted(() => ({
  context: null as Record<string, unknown> | null,
  sortableItems: null as unknown[] | null,
  draggingId: null as string | null,
}))

vi.mock('@dnd-kit/core', async () => {
  const react = await import('react')
  return {
    DndContext: (props: Record<string, unknown>) => {
      dnd.context = props
      return react.createElement(react.Fragment, null, props.children as never)
    },
    DragOverlay: (props: Record<string, unknown>) =>
      react.createElement(react.Fragment, null, props.children as never),
    PointerSensor: function PointerSensor() {},
    KeyboardSensor: function KeyboardSensor() {},
    useSensor: (sensor: unknown, options?: unknown) => ({ sensor, options }),
    useSensors: (...sensors: unknown[]) => sensors,
    closestCenter: function closestCenter() {
      return []
    },
    closestCorners: function closestCorners() {
      return []
    },
  }
})

vi.mock('@dnd-kit/sortable', async () => {
  const react = await import('react')
  return {
    SortableContext: (props: Record<string, unknown>) => {
      dnd.sortableItems = props.items as unknown[]
      return react.createElement(react.Fragment, null, props.children as never)
    },
    verticalListSortingStrategy: 'verticalListSortingStrategy',
    sortableKeyboardCoordinates: function sortableKeyboardCoordinates() {
      return undefined
    },
    arrayMove: <T,>(list: T[], from: number, to: number): T[] => {
      const next = [...list]
      const [entry] = next.splice(from, 1)
      next.splice(to, 0, entry)
      return next
    },
    useSortable: (args: { id: string }) => ({
      attributes: { 'aria-roledescription': 'sortable' },
      listeners: { onPointerDown: () => undefined },
      setNodeRef: () => undefined,
      setActivatorNodeRef: () => undefined,
      transform: null,
      transition: undefined,
      isDragging: dnd.draggingId === args.id,
    }),
  }
})

describe('MEU-49 ConvertPage drag reorder', () => {
  const REPO_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '../../..')
  const PLAN_DIR = resolve(REPO_ROOT, 'docs/execution/plans/2026-09-03-p10-queue-card-dnd')
  const SETS = JSON.parse(readFileSync(resolve(PLAN_DIR, 'named-sets.json'), 'utf8')) as Record<
    string,
    { value: string[] }
  >
  const DRAG_HANDLE_TESTID = SETS.DND_TESTIDS.value[0]
  /*
    A variable specifier on purpose. A literal one is resolved by Vite at
    transform time, and a module that does not exist yet aborts collection for
    the whole file — which would delete this describe's tests from the count
    `RED_PHASE_ORACLE` clause (b) reads instead of failing them. Built from a
    variable, the failure lands at test time, where the oracle can see it.
  */
  const SINGLE_FLIGHT_MODULE = '../../src/renderer/src/lib/queue/reorder-single-flight'

  let user: ReturnType<typeof userEvent.setup>
  /** Kept so AC-49.37 can unmount the route while a PUT is still on the wire. */
  let teardown: () => void = () => undefined
  const fetches: FetchCall[] = []
  let items: Record<string, unknown>[] = []
  /** Status the reorder PUT answers with, so a test can reject one. */
  let reorderStatus = 204
  /** Gate held closed to observe the page WHILE a reorder is still in flight. */
  let holdReorder: (() => void) | null = null

  function conversion(row: Record<string, unknown>): Record<string, unknown> {
    return {
      input_path: 'C:/in/' + String(row.id) + '.mkv',
      output_path: null,
      display_name: String(row.id) + '.mkv',
      kind: 'compress',
      preset_id: 'balanced',
      status: 'Pending',
      cq: null,
      scale_height: null,
      audio_mode: null,
      gpu_encoder: null,
      in_ms: null,
      out_ms: null,
      copy_mode: null,
      stream_index: null,
      progress: 0,
      speed: null,
      eta: null,
      file_size: null,
      queue_position: row.position,
      ...row,
    }
  }

  /** Six rows, so there is a first, a last and four unambiguous middles. */
  function defaultQueue(): Record<string, unknown>[] {
    return [
      conversion({ id: 'job-1', position: 1 }),
      conversion({ id: 'job-2', position: 2 }),
      conversion({ id: 'job-3', position: 3 }),
      conversion({ id: 'job-4', position: 4 }),
      conversion({ id: 'job-5', position: 5 }),
      conversion({ id: 'job-6', position: 6 }),
    ]
  }

  const IDS = ['job-1', 'job-2', 'job-3', 'job-4', 'job-5', 'job-6']

  beforeEach(() => {
    user = userEvent.setup()
    fetches.length = 0
    items = defaultQueue()
    reorderStatus = 204
    holdReorder = null
    dnd.context = null
    dnd.sortableItems = null
    dnd.draggingId = null
    teardown = () => undefined
    queryClient.clear()
    mockApi(async () => ['C:/e2e/sample.mp4'])
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string, init?: RequestInit) => {
        const method = (init?.method ?? 'GET').toUpperCase()
        let body: unknown
        if (typeof init?.body === 'string' && init.body.length > 0) {
          body = JSON.parse(init.body)
        }
        const href = String(url)
        fetches.push({ url: href, method, body })
        if (href.includes('/settings/converter')) {
          return jsonResponse({
            output_dir: '~/Videos/av-kit',
            default_preset: 'archival',
            skip_existing: true,
            gpu_preference: 'auto',
          })
        }
        if (href.includes('/settings/ui')) {
          return jsonResponse({ theme: 'dark' })
        }
        if (href.includes('/health/dependencies')) {
          return jsonResponse({
            ffmpeg: { available: true, version: '7.1.2' },
            yt_dlp: { available: true },
          })
        }
        if (href.includes('/conversions/gpu')) {
          return jsonResponse({
            nvidia_nvenc: false,
            amd_amf: false,
            intel_qsv: false,
            vulkan: false,
            software_h265: true,
            software_h264: true,
            recommended_encoder: 'libx265',
            checked_at: '2026-08-26T00:00:00Z',
          })
        }
        if (href.includes('/conversions/reorder') && method === 'PUT') {
          if (holdReorder !== null) {
            await new Promise<void>((release) => {
              holdReorder = release
            })
          }
          return reorderStatus === 204
            ? new Response(null, { status: 204 })
            : jsonResponse({ detail: 'reorder rejected' }, reorderStatus)
        }
        if (/\/conversions\/?$/.test(new URL(href).pathname) && method === 'GET') {
          return jsonResponse({
            items,
            processor: { state: 'Idle', current_job_id: null },
          })
        }
        return new Response(null, { status: 204 })
      }),
    )
  })

  afterEach(async () => {
    // Never leave a held PUT behind: the gate is MODULE-level by
    // REORDER_SINGLE_FLIGHT_RULE, so a request left hanging would hold it into
    // the next test and turn one failure into a cascade.
    if (holdReorder !== null) {
      const release = holdReorder
      holdReorder = null
      await act(async () => {
        release()
        await Promise.resolve()
      })
    }
    teardown()
    vi.unstubAllGlobals()
    queryClient.clear()
  })

  async function renderQueue(): Promise<void> {
    await act(async () => {
      const view = render(
        createElement(QueryClientProvider, { client: queryClient }, createElement(ConvertPage, null)),
      )
      teardown = view.unmount
    })
    await vi.waitFor(() => {
      expect(screen.queryAllByTestId('convert-queue-row')).toHaveLength(items.length)
    })
  }

  function card(id: string): HTMLElement {
    const el = screen.getAllByTestId('convert-queue-row').find((node) => node.dataset.jobId === id)
    if (el === undefined) {
      throw new Error('no rendered card for ' + id)
    }
    return el
  }

  /** Every recorded reorder PUT, in the order the page issued them. */
  function reorderPuts(): FetchCall[] {
    return fetches.filter(
      (call) => call.method === 'PUT' && call.url.includes('/conversions/reorder'),
    )
  }

  function listGets(): FetchCall[] {
    return fetches.filter(
      (call) => call.method === 'GET' && /\/conversions\/?$/.test(new URL(call.url).pathname),
    )
  }

  /** `MOVE_TO_INDEX_CONTRACT` — targetIndex is FINAL, resolved pre-move. */
  function movedTo(ids: string[], id: string, targetIndex: number): { job_ids: string[] } {
    const next = [...ids]
    const [entry] = next.splice(next.indexOf(id), 1)
    next.splice(targetIndex, 0, entry)
    return { job_ids: next }
  }

  /**
   * The drop dnd-kit would deliver. `DndContext` is stubbed, so its `onDragEnd`
   * is reachable directly — the one callback a jsdom drag cannot otherwise
   * produce.
   */
  async function drop(activeId: string, overId: string | null): Promise<void> {
    const context = dnd.context
    if (context === null) {
      throw new Error('QueueList mounted no DndContext — the page passed no onMoveToIndex')
    }
    const onDragEnd = context.onDragEnd
    if (typeof onDragEnd !== 'function') {
      throw new Error('DndContext was given no onDragEnd')
    }
    await act(async () => {
      ;(onDragEnd as (event: unknown) => void)({
        active: { id: activeId },
        over: overId === null ? null : { id: overId },
      })
      await Promise.resolve()
    })
  }

  /** Focus the card's open region and press a chord, exactly as MEU-45 does. */
  async function keydown(id: string, key: string, alt: boolean): Promise<void> {
    within(card(id))
      .getByRole('button', { name: /^Open details for / })
      .focus()
    const chord = '{' + key + '}'
    await user.keyboard(alt ? '{Alt>}' + chord + '{/Alt}' : chord)
  }

  async function openKebab(id: string): Promise<HTMLElement> {
    await user.click(within(card(id)).getByTestId('queue-card-kebab'))
    const menu = screen.queryByTestId('queue-card-menu')
    if (menu === null) {
      throw new Error('kebab menu did not open for ' + id)
    }
    return menu
  }

  function menuAction(menu: HTMLElement, action: string): HTMLButtonElement | null {
    return (
      (within(menu)
        .queryAllByRole('menuitem')
        .find((item) => item.dataset.menuAction === action) as HTMLButtonElement | undefined) ??
      null
    )
  }

  function handles(): HTMLButtonElement[] {
    return screen.queryAllByTestId(DRAG_HANDLE_TESTID) as HTMLButtonElement[]
  }

  /**
   * Node-identity comparison. `toEqual` on two DOM elements walks the whole
   * subtree and would pass for a freshly mounted twin, which is the case this
   * assertion exists to exclude.
   */
  function sameNodes(before: HTMLElement[], after: HTMLElement[]): void {
    expect(after, 'the same number of handles').toHaveLength(before.length)
    before.forEach((node, index) => {
      expect(after[index], 'handle ' + index + ' is the same DOM node, not a remount').toBe(node)
    })
  }

  it('AC-49.21 reorderConversionToIndex issues one absolute permutation and reconciles once', async () => {
    await renderQueue()

    const command = (convertCommands as unknown as Record<string, unknown>)
      .reorderConversionToIndex
    expect(
      typeof command,
      'COMMAND_MODULE_RULE — the index-based reorder is a command, not a page onClick',
    ).toBe('function')

    const mark = fetches.length
    await act(async () => {
      await (command as (ids: string[], id: string, index: number) => Promise<void>)(
        IDS,
        'job-1',
        2,
      )
    })
    await vi.waitFor(() => {
      expect(fetches.slice(mark).some((call) => call.method === 'GET')).toBe(true)
    })

    const after = fetches.slice(mark)
    const puts = after.filter((c) => c.method === 'PUT' && c.url.includes('/conversions/reorder'))
    expect(puts, 'one PUT for one move').toHaveLength(1)

    // REORDER_WIRE_CONTRACT — a complete permutation, never {id, direction}.
    expect(puts[0].body).toEqual({
      job_ids: ['job-2', 'job-3', 'job-1', 'job-4', 'job-5', 'job-6'],
    })
    expect(puts[0].body).toEqual(movedTo(IDS, 'job-1', 2))
    expect(puts[0].body).not.toHaveProperty('direction')

    // Exactly one reconcile, mirroring `reorderConversion`'s single-gesture shape.
    expect(
      after.filter(
        (c) => c.method === 'GET' && /\/conversions\/?$/.test(new URL(c.url).pathname),
      ),
      'the list refetches once, after the PUT',
    ).toHaveLength(1)
  })

  it('AC-49.22 the converter hands QueueList an onMoveToIndex wired to its own command', async () => {
    await renderQueue()

    expect(dnd.context, 'DND_OPT_IN_RULE — the converter opts in too').not.toBeNull()
    expect(dnd.sortableItems, 'SortableContext receives the queue ids').toEqual(IDS)

    const mark = fetches.length
    await drop('job-1', 'job-3')
    await vi.waitFor(() => {
      expect(
        fetches.slice(mark).filter((c) => c.method === 'PUT').length,
        'the drop reaches the command module',
      ).toBe(1)
    })
    expect(fetches.slice(mark).filter((c) => c.method === 'PUT')[0].body).toEqual(
      movedTo(IDS, 'job-1', 2),
    )
  })

  it('AC-49.22 a rejected drop surfaces the error and leaves the rendered order alone', async () => {
    reorderStatus = 500
    await renderQueue()

    const before = screen
      .queryAllByTestId('convert-queue-row')
      .map((node) => node.dataset.jobId)

    await drop('job-1', 'job-4')

    await vi.waitFor(() => {
      const banner = screen.queryByTestId('error-banner')
      expect(banner?.hasAttribute('hidden')).toBe(false)
      expect(banner?.textContent ?? '').not.toBe('')
    })
    // NO_DEAD_CONTROL_RULE / REORDER_FEEDBACK_TIER clause 2: no optimistic
    // reorder survives a rejection — the row the server refused to move is
    // still where it was.
    expect(
      screen.queryAllByTestId('convert-queue-row').map((node) => node.dataset.jobId),
      'the list is not left in a state the server never accepted',
    ).toEqual(before)
  })

  it('AC-49.23 the converter keeps its kebab and Alt+Arrow reorder paths once it drags', async () => {
    await renderQueue()

    // This is a PRESERVATION criterion: it is green from the first run and stays
    // green once drag lands. That is the whole assertion -- the "once it drags"
    // half is proved by this same body still passing after the page is wrapped
    // in a DndContext, not by an extra expect() that would only be satisfiable
    // post-implementation and would drag a preservation AC into the Red set.

    // WCAG_DRAG_RULE — the single-pointer alternative is all four items, on a
    // middle row where all four are possible.
    const middle = await openKebab('job-3')
    const actions = within(middle)
      .queryAllByRole('menuitem')
      .map((item) => item.dataset.menuAction)
    for (const action of ['move-up', 'move-down', 'move-top', 'move-bottom']) {
      expect(actions, 'the kebab keeps ' + action).toContain(action)
    }

    await user.click(menuAction(middle, 'move-up') as HTMLButtonElement)
    await vi.waitFor(() => {
      expect(reorderPuts()).toHaveLength(1)
    })
    expect(reorderPuts()[0].body).toEqual(buildReorderBody(IDS, 'job-3', 'up'))

    // And the keyboard alternative still issues its own request.
    await keydown('job-2', 'ArrowDown', true)
    await vi.waitFor(() => {
      expect(reorderPuts()).toHaveLength(2)
    })
    expect(reorderPuts()[1].body).toEqual(buildReorderBody(IDS, 'job-2', 'down'))
  })

  it('AC-49.32 an in-flight conversion reorder blocks a concurrent drop, and the next one goes through', async () => {
    await renderQueue()
    holdReorder = () => undefined

    // Alt+Arrow takes the gate first and parks on the wire.
    await keydown('job-2', 'ArrowDown', true)
    await vi.waitFor(() => {
      expect(reorderPuts()).toHaveLength(1)
    })

    // The drop arrives while the first body is still unacknowledged. Its own
    // body would be computed from the SAME pre-mutation order, so letting it
    // through is the last-write-wins clobber REORDER_SINGLE_FLIGHT_RULE exists
    // to prevent.
    await drop('job-5', 'job-1')
    expect(reorderPuts(), 'the gate refused the second permutation').toHaveLength(1)

    const release = holdReorder
    holdReorder = null
    await act(async () => {
      release?.()
      await Promise.resolve()
    })
    await vi.waitFor(() => {
      expect(listGets().length).toBeGreaterThan(1)
    })

    // Suppression is for the duration of the flight, not forever.
    await drop('job-5', 'job-1')
    await vi.waitFor(() => {
      expect(reorderPuts(), 'the gate is free once the first request settled').toHaveLength(2)
    })
    expect(reorderPuts()[1].body).toEqual(movedTo(IDS, 'job-5', 0))
  })

  it('AC-49.33 a converter bulk fold holds the gate for the whole sequence, not per request', async () => {
    await renderQueue()
    holdReorder = () => undefined

    await user.click(screen.getByTestId('queue-select-all'))
    await user.click(within(screen.getByTestId('bulk-action-bar')).getByTestId('bulk-move-top'))
    await vi.waitFor(() => {
      expect(reorderPuts().length).toBe(1)
    })

    // Mid-fold: the bulk run owns the gate, so the drop issues nothing. A gate
    // acquired per-request inside the fold would let this interleave between
    // two of the fold's own PUTs.
    await drop('job-6', 'job-1')
    expect(reorderPuts(), 'the drop found the gate held by the fold').toHaveLength(1)

    const release = holdReorder
    holdReorder = null
    await act(async () => {
      release?.()
      await Promise.resolve()
    })

    // The fold's own N requests are unaffected by the blocked drop.
    await vi.waitFor(() => {
      expect(reorderPuts().length, 'one PUT per selected row').toBeGreaterThan(1)
    })
    await vi.waitFor(() => {
      expect(listGets().length, 'one reconcile for the whole fan-out').toBeGreaterThan(1)
    })

    // Second completion order: the gate is released only AFTER the fold has
    // reconciled, so a drop retried now computes its body from the post-fold
    // order the refetch installed — never from the pre-fold one.
    const settled = reorderPuts().length
    await drop('job-6', 'job-1')
    await vi.waitFor(() => {
      expect(reorderPuts().length, 'the retried drop is admitted once the fold is done').toBe(
        settled + 1,
      )
    })
    const body = reorderPuts()[settled].body as { job_ids: string[] }
    expect(
      body.job_ids.slice().sort(),
      'the permutation is still complete and still the same six ids',
    ).toEqual(IDS.slice().sort())
    expect(body.job_ids[0], 'job-6 landed at the index the drop named').toBe('job-6')
  })

  it('AC-49.34 the converter releases in a finally, so a rejected reorder does not deadlock', async () => {
    reorderStatus = 500
    await renderQueue()

    await drop('job-1', 'job-3')
    await vi.waitFor(() => {
      const banner = screen.queryByTestId('error-banner')
      expect(banner?.hasAttribute('hidden')).toBe(false)
    })
    expect(reorderPuts()).toHaveLength(1)

    // The gate must have been released on the failure path. Releasing only on
    // success turns one 500 into a permanently unreorderable queue.
    reorderStatus = 204
    await drop('job-1', 'job-3')
    await vi.waitFor(() => {
      expect(reorderPuts(), 'the second attempt still acquires the gate').toHaveLength(2)
    })
  })

  it('AC-49.35 while the converter gate is held every drag handle is disabled, without a remount', async () => {
    await renderQueue()

    const before = handles()
    expect(before.length, 'every row has a handle').toBe(items.length)
    for (const handle of before) {
      expect(handle.disabled, 'nothing is held yet').toBe(false)
    }

    holdReorder = () => undefined
    // The gate is taken by ANOTHER card's Alt+Arrow. A page-local useState
    // mirror is not written by that card, so only the module-level store in
    // REORDER_HELD_HOOK can make this assertion true.
    await keydown('job-2', 'ArrowDown', true)
    await vi.waitFor(() => {
      expect(reorderPuts()).toHaveLength(1)
    })

    await vi.waitFor(() => {
      for (const handle of handles()) {
        expect(handle.disabled, 'a held gate disables every handle in the list').toBe(true)
      }
    })
    // Same DOM nodes: the disabled state is a re-render, not a remount, so
    // focus and the dnd-kit activator ref survive it.
    sameNodes(before, handles())

    const release = holdReorder
    holdReorder = null
    await act(async () => {
      release?.()
      await Promise.resolve()
    })
    await vi.waitFor(() => {
      for (const handle of handles()) {
        expect(handle.disabled, 'the handles come back live').toBe(false)
      }
    })
    sameNodes(before, handles())
  })

  it('AC-49.37 the converter gate is its own key, and outlives the component', async () => {
    const gate = (await import(SINGLE_FLIGHT_MODULE)) as unknown as {
      acquireQueueReorder: (key: string) => (() => void) | null
      isQueueReorderHeld: (key: string) => boolean
    }

    await renderQueue()
    holdReorder = () => undefined
    await keydown('job-2', 'ArrowDown', true)
    await vi.waitFor(() => {
      expect(reorderPuts()).toHaveLength(1)
    })
    expect(gate.isQueueReorderHeld('convert')).toBe(true)

    // Holding `convert` says nothing about `download` — REORDER_QUEUE_KEYS is a
    // map, not a single global flag.
    const downloadRelease = gate.acquireQueueReorder('download')
    expect(downloadRelease, 'the other queue is still free').not.toBeNull()
    downloadRelease?.()

    // The route unmounts while the PUT is still on the wire. A gate held in a
    // useRef dies here and hands the remounted page a free gate, which then
    // sends a second absolute permutation built from the pre-mutation order.
    teardown()
    teardown = () => undefined
    expect(
      gate.acquireQueueReorder('convert'),
      'the in-flight reorder still owns the convert gate after the unmount',
    ).toBeNull()

    await renderQueue()
    expect(gate.acquireQueueReorder('convert')).toBeNull()

    const release = holdReorder
    holdReorder = null
    await act(async () => {
      release?.()
      await Promise.resolve()
    })
    await vi.waitFor(() => {
      expect(gate.isQueueReorderHeld('convert'), 'the settled request frees it').toBe(false)
    })
    const freed = gate.acquireQueueReorder('convert')
    expect(freed).not.toBeNull()
    freed?.()
  })

  it('AC-49.38 every converter reorder affordance that is present goes inert while the gate is held', async () => {
    await renderQueue()
    holdReorder = () => undefined

    await keydown('job-2', 'ArrowDown', true)
    await vi.waitFor(() => {
      expect(reorderPuts()).toHaveLength(1)
    })

    // A middle card can move all four ways, so all four items are present and
    // all four must read as unavailable.
    const middle = await openKebab('job-4')
    for (const action of ['move-up', 'move-down', 'move-top', 'move-bottom']) {
      const item = menuAction(middle, action)
      expect(item, 'the middle card offers ' + action).not.toBeNull()
      expect(item?.disabled, action + ' must not look live while the gate is held').toBe(true)
    }
    await user.keyboard('{Escape}')

    // The LAST card can only move up. QueueCardMenu rule 1 is "unavailable
    // actions are absent, never disabled", so move-down and move-bottom stay
    // absent — demanding four disabled items here would contradict the
    // component.
    const last = await openKebab('job-6')
    expect(menuAction(last, 'move-down'), 'absent, not disabled').toBeNull()
    expect(menuAction(last, 'move-bottom'), 'absent, not disabled').toBeNull()
    for (const action of ['move-up', 'move-top']) {
      const item = menuAction(last, action)
      expect(item, 'the last card still offers ' + action).not.toBeNull()
      expect(item?.disabled, action + ' is present, so it must read as unavailable').toBe(true)
    }
    await user.keyboard('{Escape}')

    // ALT_ARROW_SUPPRESSION_RULE — the keyboard path is inert on the same
    // guard, and silently, since there is nothing to disable.
    await keydown('job-4', 'ArrowUp', true)
    await keydown('job-4', 'ArrowDown', true)
    expect(reorderPuts(), 'Alt+Arrow issues nothing while the gate is held').toHaveLength(1)

    const release = holdReorder
    holdReorder = null
    await act(async () => {
      release?.()
      await Promise.resolve()
    })
    await vi.waitFor(() => {
      expect(listGets().length).toBeGreaterThan(1)
    })

    // Inert for the duration of the flight only.
    const live = await openKebab('job-4')
    for (const action of ['move-up', 'move-down', 'move-top', 'move-bottom']) {
      expect(menuAction(live, action)?.disabled, action + ' is live again').toBe(false)
    }
    await user.keyboard('{Escape}')
  })
})
