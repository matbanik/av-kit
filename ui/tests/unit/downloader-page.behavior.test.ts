/** @vitest-environment jsdom */

import { existsSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { QueryClientProvider } from '@tanstack/react-query'
import { act, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import * as downloadCommands from '../../src/renderer/src/features/downloader/download-commands'
import { AppShell } from '../../src/renderer/src/components/layout/AppShell'
import { cookieTestBody } from '../../src/renderer/src/features/downloader/cookie-bar'
import { DOWNLOAD_EVENTS, forceSabr, postDownloadCreate } from '../../src/renderer/src/features/downloader/download-commands'
import { buildReorderBody } from '../../src/renderer/src/features/downloader/download-controls'
import { DownloaderPage } from '../../src/renderer/src/features/downloader/DownloaderPage'
import { expectBoundHint } from './helpers/bound-hint'
import { formatFileSize } from '../../src/renderer/src/lib/queue/format'
import { queryClient } from '../../src/renderer/src/lib/query-client'
import { QUERY_KEY, type DownloadListItem } from '../../src/renderer/src/features/downloader/useDownloadQueue'

const existing: DownloadListItem = {
  id: 'old-1',
  url: 'https://example.invalid/watch?v=old',
  title: 'Existing',
  quality: '720p',
  status: 'Pending',
  progress: 0,
  speed: null,
  eta: null,
  file_size: 156_000_000,
  file_path: null,
  queue_position: 1,
  received_height: null,
}

const created: DownloadListItem = {
  id: 'new-1',
  url: 'https://example.invalid/watch?v=e2e0001',
  title: 'Created',
  quality: '1080p',
  status: 'Pending',
  progress: 0,
  speed: null,
  eta: null,
  file_size: 245_000_000,
  file_path: null,
  queue_position: 2,
  received_height: null,
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

describe('MEU-20 downloader behavior (exec r1 F1–F5)', () => {
  let user: ReturnType<typeof userEvent.setup>
  /** The Testing Library container for the tree under test. */
  let host: HTMLElement
  const fetches: Array<{ url: string; method: string; body?: unknown }> = []
  let listItems: DownloadListItem[]
  let postStatus = 201
  let lastCreateKeys: string[] | null
  let holdPost: Promise<void> | null

  beforeEach(() => {
    user = userEvent.setup()
    fetches.length = 0
    listItems = []
    postStatus = 201
    lastCreateKeys = null
    holdPost = null
    queryClient.clear()
    mockApi()
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input)
        const method = (init?.method ?? 'GET').toUpperCase()
        const parsed = init?.body ? (JSON.parse(String(init.body)) as Record<string, unknown>) : undefined
        fetches.push({ url, method, body: parsed })
        if (url.includes('/downloads/sabr')) {
          return new Response(JSON.stringify({ mode: 'inactive', source: null, checked_at: null }), { status: 200 })
        }
        if (url.includes('/settings/downloader') && method === 'PUT') {
          return new Response(JSON.stringify(parsed ?? {}), { status: 200 })
        }
        if (url.includes('/downloads/cookies/test')) {
          return new Response(JSON.stringify({ ok: true }), { status: 200 })
        }
        if (/\/downloads\/?$/.test(new URL(url).pathname) && method === 'POST') {
          if (holdPost !== null) {
            await holdPost
          }
          lastCreateKeys = Object.keys(parsed ?? {}).sort()
          if (postStatus >= 400) {
            return new Response(
              JSON.stringify({ error: { code: 'VALIDATION', message: 'rejected add' } }),
              { status: postStatus },
            )
          }
          listItems = [...listItems, { ...created, url: String(parsed?.url ?? created.url) }]
          return new Response(JSON.stringify({ items: [listItems[listItems.length - 1]] }), { status: 201 })
        }
        if (/\/downloads\/?$/.test(new URL(url).pathname) && method === 'GET') {
          return new Response(JSON.stringify({ items: listItems, processor: { state: 'Idle' } }), { status: 200 })
        }
        return new Response('', { status: 202 })
      }),
    )
  })

  afterEach(() => {
    queryClient.clear()
    vi.useRealTimers()
    vi.unstubAllGlobals()
  })

  async function renderPage(): Promise<void> {
    await act(async () => {
      host = render(
        createElement(QueryClientProvider, { client: queryClient }, createElement(DownloaderPage)),
      ).container
    })
    await act(async () => {
      await Promise.resolve()
    })
  }

  /**
   * The form's own submit path — its `onSubmit`, not the Add button's click.
   * jsdom implements no implicit submission, so no keyboard gesture produces
   * this event; it is dispatched directly, inside `act`, the way a browser
   * would deliver it after the user presses Enter in the field.
   */
  async function submitForm(): Promise<void> {
    const form = within(host).getByTestId('url-input').closest('form')
    if (form === null) {
      throw new Error('the url field is not inside a form')
    }
    await act(async () => {
      form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
    })
  }

  it('AC-20.3/20.4/20.21 blank Add does not invent a queue row or POST', async () => {
    await renderPage()
    await user.click(within(host).getByTestId('add-btn'))
    expect(within(host).queryByTestId('queue-card')).toBeNull()
    expect(fetches.some((row) => row.method === 'POST' && /\/downloads\/?$/.test(new URL(row.url).pathname))).toBe(
      false,
    )
    expect(JSON.stringify(queryClient.getQueryData(QUERY_KEY))).not.toMatch(/pending-/)
  })

  it('AC-20.3/20.21 rejected Add shows error and does not keep a ghost row', async () => {
    postStatus = 422
    await renderPage()
    const input = within(host).getByTestId('url-input')
    await user.clear(input)
    await user.type(input, created.url)
    await submitForm()
    await vi.waitFor(() => {
      expect(within(host).queryByTestId('error-banner')?.textContent).toMatch(/rejected add/)
    })
    expect(within(host).queryByTestId('queue-card')).toBeNull()
    expect(JSON.stringify(queryClient.getQueryData(QUERY_KEY))).not.toMatch(/pending-/)
  })

  it('AC-20.4/20.21 successful Add keeps existing jobs from the list envelope', async () => {
    listItems = [existing]
    await renderPage()
    await vi.waitFor(() => {
      expect(within(host).queryByTestId('queue-card')?.textContent).toMatch(/Existing/)
    })
    const input = within(host).getByTestId('url-input')
    await user.clear(input)
    await user.type(input, created.url)
    await submitForm()
    await vi.waitFor(() => {
      const rows = Array.from(within(host).queryAllByTestId('queue-card')).map((row) => row.textContent ?? '')
      expect(rows.some((text) => text.includes('Existing'))).toBe(true)
      expect(rows.some((text) => text.includes('Created') || text.includes(created.url))).toBe(true)
    })
    expect(lastCreateKeys).toEqual(['audio_format', 'audio_only', 'quality', 'url'])
    const cached = queryClient.getQueryData(QUERY_KEY) as { items: DownloadListItem[] }
    expect(cached.items.map((item) => item.id).sort()).toEqual(['new-1', 'old-1'])
  })

  it('AC-20.19 (rewritten by AC-46.9) Quality and Size survive the loss of the table', async () => {
    // E2E_REWRITE_RULE: AC-46.5 deletes `DownloadQueueTable`, so the Red-phase
    // form of this test -- which mounted that component and read its <th> row --
    // can no longer exist. The CAPABILITY it guarded (a queued row shows its
    // quality and its size) is not dropped: it is re-pointed at the card surface
    // that replaces the table. `formatFileSize` stays the single home of the
    // byte formatting, as before.
    expect(formatFileSize(245_000_000)).toBe('245 MB')
    // The row is finished, because the size a card reports is the size of a
    // file that exists. The retired table printed the extract's *expected*
    // size on every row, including rows with nothing on disk yet.
    listItems = [{ ...existing, status: 'Done', file_path: 'C:/out/old-1.mp4' }]
    await renderPage()
    await vi.waitFor(() => {
      expect(within(host).queryAllByTestId('queue-card')).toHaveLength(1)
    })
    expect(within(host).queryByRole('table'), 'no table survives on the page').toBeNull()
    expect(within(host).queryAllByRole('columnheader'), 'no table headers survive').toHaveLength(0)
    const card = within(host).queryByTestId('queue-card')?.textContent ?? ''
    expect(card, 'the Quality column moved onto the card meta line').toContain('720p')
    expect(card, 'the Size column moved onto the card meta line').toContain('156 MB')
  })

  it('AC-20.6 SABR mutations invalidate QUERY_KEY and the SABR query', async () => {
    const keys: unknown[] = []
    const spy = vi.spyOn(queryClient, 'invalidateQueries').mockImplementation(async (opts) => {
      keys.push(opts)
    })
    await forceSabr()
    spy.mockRestore()
    expect(keys).toEqual(
      expect.arrayContaining([{ queryKey: QUERY_KEY }, { queryKey: ['downloads', 'sabr'] }]),
    )
  })

  it('AC-20.8 COOKIE_SETTINGS_PUT from the radio uses only the four leaves', async () => {
    await renderPage()
    await user.click(within(host).getByTestId('cookie-mode-file'))
    await vi.waitFor(() => {
      const put = fetches.find((row) => row.method === 'PUT' && row.url.includes('/settings/downloader'))
      expect(put?.body).toEqual({
        cookie_mode: 'file',
        cookie_browser: 'chrome',
        cookie_browser_profile: '',
        cookie_file_path: '',
      })
      expect(Object.keys((put?.body as object) ?? {}).sort()).toEqual(
        ['cookie_browser', 'cookie_browser_profile', 'cookie_file_path', 'cookie_mode'].sort(),
      )
    })
  })

  it('AC-20.13 AppShell palette add focuses url-input without POSTing', async () => {
    await act(async () => {
      host = render(
        createElement(
          QueryClientProvider,
          { client: queryClient },
          createElement(AppShell, null, createElement(DownloaderPage)),
        ),
      ).container
    })
    await act(async () => {
      await Promise.resolve()
    })
    const postsBefore = fetches.filter((row) => row.method === 'POST' && /\/downloads\/?$/.test(new URL(row.url).pathname))
      .length
    await act(async () => {
      window.dispatchEvent(new Event(DOWNLOAD_EVENTS.add))
    })
    await vi.waitFor(() => {
      expect(document.activeElement).toBe(within(host).queryByTestId('url-input') ?? document.activeElement)
    })
    const postsAfter = fetches.filter((row) => row.method === 'POST' && /\/downloads\/?$/.test(new URL(row.url).pathname))
      .length
    expect(postsAfter).toBe(postsBefore)
  })

  it('AC-97.4 HINTS url-input and add-btn carry their chords', async () => {
    await renderPage()
    expectBoundHint(within(host).getByTestId('url-input'), 'download:add')
    expectBoundHint(within(host).getByTestId('add-btn'), 'page:primary')
  })

  it('AC-20.8 COOKIE_TEST_BODY rejects mismatched mode fields', () => {
    expect(() => cookieTestBody({ mode: 'browser' })).toThrow()
    expect(() => cookieTestBody({ mode: 'file' })).toThrow()
    expect(() => cookieTestBody({ mode: 'none', browser: 'chrome' })).toThrow()
    expect(() => cookieTestBody({ mode: 'file', cookie_file: 'C:/cookies.txt', browser: 'chrome' })).toThrow()
    expect(cookieTestBody({ mode: 'browser', browser: 'firefox' })).toEqual({ mode: 'browser', browser: 'firefox' })
  })

  it('Add click shows progress and emits a console line before POST resolves', async () => {
    const lines: string[] = []
    const onLog = (event: Event) => {
      const detail = (event as CustomEvent<{ message?: string }>).detail
      if (typeof detail?.message === 'string') {
        lines.push(detail.message)
      }
    }
    window.addEventListener('av-kit:renderer-log', onLog)
    let release = (): void => undefined
    holdPost = new Promise<void>((resolve) => {
      release = resolve
    })
    await renderPage()
    const input = within(host).getByTestId('url-input')
    await user.clear(input)
    await user.type(input, created.url)
    await user.click(within(host).getByTestId('add-btn'))
    expect(within(host).queryByTestId('add-status')?.textContent).toMatch(/Adding/)
    expect(within(host).queryByTestId('add-btn')?.getAttribute('aria-busy')).toBe('true')
    expect(lines.some((line) => /INFO add: posting/.test(line))).toBe(true)
    await act(async () => {
      release()
    })
    await vi.waitFor(() => {
      expect(within(host).queryByTestId('add-btn')?.getAttribute('aria-busy')).not.toBe('true')
    })
    window.removeEventListener('av-kit:renderer-log', onLog)
  })

  it('hung getBackendUrl surfaces a visible backend-not-ready error', async () => {
    // The clock is faked so the spec can jump the backend-readiness timeout, but
    // Testing Library settles each gesture on a zero-delay timer scheduled on
    // that same clock. `shouldAdvanceTime` lets it keep ticking on its own, so
    // the gestures still resolve while `advanceTimersByTimeAsync` stays free to
    // jump ahead.
    vi.useFakeTimers({ shouldAdvanceTime: true })
    window.api.getBackendUrl = () => new Promise(() => undefined)
    window.api.getToken = () => new Promise(() => undefined)
    await renderPage()
    const input = within(host).getByTestId('url-input')
    await user.clear(input)
    await user.type(input, created.url)
    await user.click(within(host).getByTestId('add-btn'))
    expect(within(host).queryByTestId('add-status')?.textContent).toMatch(/Adding/)
    await act(async () => {
      await vi.advanceTimersByTimeAsync(10_000)
    })
    await vi.waitFor(() => {
      expect(within(host).queryByTestId('error-banner')?.textContent).toMatch(/Backend not ready/i)
    })
    vi.useRealTimers()
  })

  it('postDownloadCreate does not write the create envelope over QUERY_KEY', async () => {
    listItems = [existing]
    queryClient.setQueryData(QUERY_KEY, { items: [existing], processor: { state: 'Idle' } })
    const out = await postDownloadCreate({
      url: created.url,
      quality: '1080p',
      audio_only: false,
      audio_format: 'default',
    })
    expect(out.items).toHaveLength(1)
    const cached = queryClient.getQueryData(QUERY_KEY) as { items: DownloadListItem[] }
    expect(cached.items.map((item) => item.id).sort()).toEqual(['new-1', 'old-1'])
  })
})

// ---------------------------------------------------------------------------
// MEU-46 — DownloaderPage on the shared queue surface (AC-46.4, .6, .7, .8,
// .9, .10, .14).
//
// The FIC names this file for all seven because every one of them is a *runtime*
// contract — a rendered card, an opened menu, an intercepted request body, a
// focused input. The one exception, AC-46.5, is a pure source-tree assertion and
// lives in `downloader-page.test.ts`, the node-environment static suite.
//
// The shape of this block deliberately mirrors `convert-page.behavior.test.ts`
// §"MEU-45 ConvertPage queue surface": AC-46.10 states that primary action,
// kebab, Alt+Arrow and the cancel label behave on the downloader *exactly* as
// AC-45.8/.9/.10 specify for convert, so the assertions are the same assertions
// against the downloader's own endpoints.
// ---------------------------------------------------------------------------

describe('MEU-46 DownloaderPage queue surface', () => {
  let user: ReturnType<typeof userEvent.setup>
  /** The Testing Library container for the tree under test. */
  let host: HTMLElement
  const fetches: Array<{ url: string; method: string; body?: unknown }> = []
  const opened: string[] = []
  const revealed: string[] = []
  let processorState: 'Idle' | 'Processing' | 'Paused' = 'Processing'
  let configuredCookieMode: 'none' | 'browser' | 'file' = 'none'
  let configuredCookieBrowser: 'chrome' | 'firefox' | 'edge' = 'chrome'
  let configuredCookieProfile = 'Default'
  let configuredCookieFile = ''
  let settingsGetGate: Promise<void> | null = null
  let sabrMode: 'inactive' | 'active' = 'inactive'
  let rows: DownloadListItem[] = []

  function queueItem(overrides: Partial<DownloadListItem>): DownloadListItem {
    return {
      id: 'dl-0',
      url: 'https://example.invalid/watch?v=dl0',
      title: 'Clip',
      quality: '1080p',
      status: 'Pending',
      progress: 0,
      speed: null,
      eta: null,
      file_size: null,
      file_path: null,
      queue_position: 1,
      received_height: null,
      ...overrides,
    }
  }

  /** Order matters: the reorder assertions read the rendered sequence. */
  function defaultRows(): DownloadListItem[] {
    return [
      queueItem({ id: 'dl-1', title: 'First', quality: '720p', status: 'Pending', queue_position: 1 }),
      queueItem({
        id: 'dl-2',
        title: 'Second',
        status: 'Downloading',
        quality: '1080p',
        speed: '1.1MiB/s',
        eta: '02:13',
        progress: 42,
        queue_position: 2,
      }),
      queueItem({
        id: 'dl-3',
        title: 'Third',
        status: 'Done',
        quality: '4k',
        speed: '4.2MiB/s',
        eta: '00:00',
        progress: 100,
        file_size: 156_000_000,
        file_path: 'C:/out/dl-3.mp4',
        queue_position: 3,
      }),
      queueItem({ id: 'dl-4', title: 'Fourth', status: 'Failed', queue_position: 4 }),
      queueItem({ id: 'dl-5', title: 'Fifth', status: 'Skipped', queue_position: 5 }),
    ]
  }

  const RENDERED_IDS = ['dl-1', 'dl-2', 'dl-3', 'dl-4', 'dl-5']

  beforeEach(() => {
    user = userEvent.setup()
    fetches.length = 0
    opened.length = 0
    revealed.length = 0
    processorState = 'Processing'
    configuredCookieMode = 'none'
    configuredCookieBrowser = 'chrome'
    configuredCookieProfile = 'Default'
    configuredCookieFile = ''
    settingsGetGate = null
    sabrMode = 'inactive'
    rows = defaultRows()
    queryClient.clear()
    mockApi()
    window.api.openPath = async (target: string) => {
      opened.push(target)
    }
    window.api.showItemInFolder = async (target: string) => {
      revealed.push(target)
    }
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input)
        const method = (init?.method ?? 'GET').toUpperCase()
        let body: unknown
        if (typeof init?.body === 'string' && init.body.length > 0) {
          body = JSON.parse(init.body)
        }
        fetches.push({ url, method, body })
        if (url.includes('/downloads/sabr')) {
          return new Response(
            JSON.stringify({ mode: sabrMode, source: null, checked_at: null }),
            { status: 200 },
          )
        }
        if (url.includes('/settings/downloader')) {
          if (method === 'PUT') {
            const saved = body as {
              cookie_mode: 'none' | 'browser' | 'file'
              cookie_browser: 'chrome' | 'firefox' | 'edge'
              cookie_browser_profile: string
              cookie_file_path: string
            }
            configuredCookieMode = saved.cookie_mode
            configuredCookieBrowser = saved.cookie_browser
            configuredCookieProfile = saved.cookie_browser_profile
            configuredCookieFile = saved.cookie_file_path
            return new Response(null, { status: 204 })
          }
          if (settingsGetGate !== null) {
            await settingsGetGate
          }
          return new Response(
            JSON.stringify({
              path: 'C:/Downloads/av-kit',
              quality: '1080p',
              audio_only: false,
              audio_format: 'default',
              cookie_mode: configuredCookieMode,
              cookie_browser: configuredCookieBrowser,
              cookie_browser_profile: configuredCookieProfile,
              cookie_file_path: configuredCookieFile,
              archive_tracking: true,
              yt_dlp_debug: false,
              ffmpeg_path: 'C:/bin/ffmpeg.exe',
            }),
            { status: 200 },
          )
        }
        if (/\/downloads\/?$/.test(new URL(url).pathname) && method === 'GET') {
          return new Response(
            JSON.stringify({
              items: rows,
              processor: { state: processorState, current_job_id: 'dl-2' },
            }),
            { status: 200 },
          )
        }
        return new Response(null, { status: 204 })
      }),
    )
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    queryClient.clear()
  })

  async function renderQueue(): Promise<ReturnType<typeof render>> {
    let view: ReturnType<typeof render> | undefined
    await act(async () => {
      view = render(
        createElement(QueryClientProvider, { client: queryClient }, createElement(DownloaderPage)),
      )
      host = view.container
    })
    await vi.waitFor(() => {
      expect(within(host).queryAllByTestId('queue-card')).toHaveLength(rows.length)
    })
    if (view === undefined) {
      throw new Error('DownloaderPage did not render')
    }
    return view
  }

  function card(id: string): HTMLElement {
    const el = within(host)
      .getAllByTestId('queue-card')
      .find((entry) => entry.dataset.jobId === id)
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

  /** Requests matched on the exact pathname, so `/downloads` never catches `/downloads/x`. */
  function requests(pathname: string, method: string): Array<{ url: string; method: string; body?: unknown }> {
    return fetches.filter(
      (call) => new URL(call.url).pathname.replace(/\/$/, '').endsWith(pathname) && call.method === method,
    )
  }

  async function openKebab(id: string): Promise<HTMLElement> {
    await click(inside(card(id), 'queue-card-kebab'))
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

  it('AC-46.4 the page renders queue-list cards and no queue-table', async () => {
    await renderQueue()

    const list = within(host).queryByTestId('queue-list')
    expect(list, 'the shared QueueList is mounted').not.toBeNull()
    expect(list?.tagName, 'QueueList is not a table').not.toBe('TABLE')
    expect(list?.querySelector('table'), 'no table survives inside the queue region').toBeNull()
    expect(within(host).queryAllByTestId('queue-card')).toHaveLength(RENDERED_IDS.length)
    for (const id of RENDERED_IDS) {
      expect(card(id)).not.toBeNull()
    }

    // RETIRED_TESTIDS — the table and its rows are gone from the tree entirely.
    expect(within(host).queryByTestId('queue-table'), 'queue-table is retired').toBeNull()
    expect(within(host).queryByTestId('queue-row'), 'queue-row is retired').toBeNull()
  })

  it('AC-46.6 the toolbar is exactly four controls and the summary survives', async () => {
    await renderQueue()

    // DEC-2 — exactly TOOLBAR_CONTROLS interactive elements; a fifth fails.
    const toolbar = within(host).queryByTestId('queue-toolbar')
    expect(toolbar, 'the reduced toolbar is mounted').not.toBeNull()
    const controls = Array.from(
      (toolbar as HTMLElement).querySelectorAll<HTMLElement>(
        'button, [role="button"], [role="menuitem"], a[href], input, select, textarea',
      ),
    )
    expect(controls, 'exactly four toolbar controls').toHaveLength(4)

    // PRESERVED_TESTIDS — the summary and processor indicator are untouched.
    expect(inside(host, 'queue-summary'), 'queue-summary survives').not.toBeNull()
    expect(inside(host, 'processor-indicator'), 'processor-indicator survives').not.toBeNull()
    expect(inside(host, 'add-btn'), 'add-btn survives').not.toBeNull()

    // All 13 RETIRED_TOOLBAR_CONTROLS.downloader ids are gone from the page.
    for (const retired of [
      'start-btn',
      'pause-btn',
      'resume-btn',
      'cancel-btn',
      'up-btn',
      'down-btn',
      'top-btn',
      'bottom-btn',
      'reset-btn',
      'remove-btn',
      'clear-all-btn',
      'open-file-btn',
      'open-folder-btn',
    ]) {
      expect(within(host).queryByTestId(retired), retired + ' no longer renders').toBeNull()
    }
  })

  it('AC-46.7 no page handler calls apiFetch on a queue path', () => {
    // COMMAND_MODULE_RULE: the ~150 lines of inline queue `apiFetch` in
    // DownloaderPage.tsx move into `download-commands.ts`. The page keeps the
    // two NON-queue calls it owns -- the settings PUT and the cookie test --
    // because those are the settings surface, not the queue.
    const source = readFileSync(
      resolve(dirname(fileURLToPath(import.meta.url)), '../../src/renderer/src/features/downloader/DownloaderPage.tsx'),
      'utf-8',
    )
    const calls = source.match(/apiFetch\(\s*[`'"]([^`'"]+)/g) ?? []
    const targets = calls.map((call) => call.replace(/^apiFetch\(\s*[`'"]/, ''))
    expect(targets.sort(), 'only the two settings-surface calls remain').toEqual(
      ['/downloads/cookies/test', '/settings/downloader'],
    )
    for (const forbidden of ['/downloads/reorder', '/reset', '${selectedId}']) {
      expect(source, 'no inline queue call for ' + forbidden).not.toContain(
        'apiFetch(`/downloads/' + forbidden,
      )
    }
    expect(source, 'the page routes through the command module').toMatch(
      /from '\.\/download-commands'/,
    )
  })

  it('AC-46.8 Clear all confirms first and dismissing issues no DELETE', async () => {
    const confirmSpy = vi.fn(() => true)
    vi.stubGlobal('confirm', confirmSpy)
    await renderQueue()

    await click(inside(host, 'queue-toolbar-overflow'))
    await click(screen.queryByTestId('queue-toolbar-clear-all'))

    const modal = screen.queryByTestId('confirm-modal')
    expect(modal, 'G20_RULE — the shared portal modal, never window.confirm').not.toBeNull()
    expect(confirmSpy, 'window.confirm is forbidden').not.toHaveBeenCalled()
    expect((modal as HTMLElement).getAttribute('role')).toBe('dialog')
    expect(
      inside(modal as HTMLElement, 'confirm-modal-confirm')?.textContent?.trim(),
      'USER_LOCKS — a verb, never OK/Yes',
    ).toBe('Clear all')

    // Dismissing issues no DELETE — the downloader previously cleared with no
    // confirm at all, so this is the whole point of the AC.
    await click(inside(modal as HTMLElement, 'confirm-modal-cancel'))
    expect(screen.queryByTestId('confirm-modal')).toBeNull()
    expect(requests('/downloads', 'DELETE'), 'dismiss is not a delete').toHaveLength(0)

    // Confirming does.
    await click(inside(host, 'queue-toolbar-overflow'))
    await click(screen.queryByTestId('queue-toolbar-clear-all'))
    const reopened = screen.queryByTestId('confirm-modal')
    await click(inside(reopened as HTMLElement, 'confirm-modal-confirm'))
    await vi.waitFor(() => {
      expect(requests('/downloads', 'DELETE')).toHaveLength(1)
    })
  })

  /** MEU-96: the command-state module is new, so it is loaded after an existence check. */
  async function loadCommandState(): Promise<{ getCommandState: (page: string) => Partial<Record<string, boolean>> }> {
    const path = resolve(dirname(fileURLToPath(import.meta.url)), '../../src/renderer/src/registry/command-state.ts')
    expect(existsSync(path), 'registry/command-state.ts exists').toBe(true)
    const specifier = '../../src/renderer/src/registry/command-state'
    return (await import(/* @vite-ignore */ specifier)) as {
      getCommandState: (page: string) => Partial<Record<string, boolean>>
    }
  }

  it('AC-96.5 PAGE_STATE the Downloader publishes the enabled state of its queue controls', async () => {
    const state = await loadCommandState()

    processorState = 'Processing'
    const processing = await renderQueue()
    await vi.waitFor(() => {
      expect(state.getCommandState('/')['download:pause']).toBe(true)
    })
    expect(state.getCommandState('/')['download:resume']).toBe(false)
    processing.unmount()

    processorState = 'Paused'
    queryClient.clear()
    const paused = await renderQueue()
    await vi.waitFor(() => {
      expect(state.getCommandState('/')['download:resume']).toBe(true)
    })
    expect(state.getCommandState('/')['download:pause']).toBe(false)
    paused.unmount()

    processorState = 'Idle'
    rows = []
    queryClient.clear()
    await renderQueue()
    await vi.waitFor(() => {
      expect(state.getCommandState('/')['download:clear']).toBe(false)
    })
    expect(state.getCommandState('/')['download:start']).toBe(false)
    expect(state.getCommandState('/')['download:cancel']).toBe(false)
  })

  it('AC-96.7 CONFIRM_ROUTE the palette clear and cancel events open the confirm before any request', async () => {
    const confirmEvent = (downloadCommands as unknown as Record<string, unknown>).DOWNLOAD_CONFIRM_EVENT
    expect(confirmEvent).toBe('av-kit:download:confirm')
    const name = String(confirmEvent)
    await renderQueue()

    await act(async () => {
      window.dispatchEvent(new CustomEvent(name, { detail: { kind: 'clear' } }))
    })
    const modal = screen.queryByTestId('confirm-modal')
    expect(modal).not.toBeNull()
    expect(inside(modal as HTMLElement, 'confirm-modal-confirm')?.textContent?.trim()).toBe('Clear all')
    await click(inside(modal as HTMLElement, 'confirm-modal-cancel'))
    expect(screen.queryByTestId('confirm-modal')).toBeNull()
    expect(requests('/downloads', 'DELETE')).toHaveLength(0)

    await act(async () => {
      window.dispatchEvent(new CustomEvent(name, { detail: { kind: 'clear' } }))
    })
    await click(inside(screen.getByTestId('confirm-modal'), 'confirm-modal-confirm'))
    await vi.waitFor(() => {
      expect(requests('/downloads', 'DELETE')).toHaveLength(1)
    })

    await act(async () => {
      window.dispatchEvent(new CustomEvent(name, { detail: { kind: 'cancel' } }))
    })
    const cancel = screen.getByTestId('confirm-modal')
    expect(inside(cancel, 'confirm-modal-confirm')?.textContent?.trim()).toBe('Cancel downloads')
    expect(inside(cancel, 'confirm-modal-cancel')?.textContent?.trim()).toBe('Keep running')
    expect(requests('/downloads/cancel', 'POST')).toHaveLength(0)
    await click(inside(cancel, 'confirm-modal-confirm'))
    await vi.waitFor(() => {
      expect(requests('/downloads/cancel', 'POST')).toHaveLength(1)
    })
  })

  it('AC-46.9 cards carry DOWNLOAD_META_SEGMENTS including a Done row with speed', async () => {
    await renderQueue()

    // A queued row: quality only, because speed and ETA are still null.
    const first = card('dl-1').textContent ?? ''
    expect(first).toContain('720p')

    // An in-flight row: all three.
    const second = card('dl-2').textContent ?? ''
    expect(second).toContain('1080p')
    expect(second).toContain('1.1MiB/s')
    expect(second).toContain('02:13')

    // A finished row keeps its persisted speed and ETA — the backend never
    // clears them, so the card must not hide them behind a status check.
    const third = card('dl-3').textContent ?? ''
    expect(third).toContain('4k')
    expect(third).toContain('4.2MiB/s')
    expect(third).toContain('00:00')
    expect(third, 'the Size column survives on the card').toContain('156 MB')

    // No empty separator artefacts where a null field used to be.
    expect(first).not.toContain('—')
    expect(first).not.toMatch(/·\s*·/)
  })

  it('AC-46.10 primary/kebab/Alt+Arrow match the converter contract', async () => {
    await renderQueue()

    const primary = (id: string): HTMLElement | null => inside(card(id), 'queue-card-primary-action')

    // PRIMARY_ACTION_MAP — Pending and Skipped map to `none`.
    expect(primary('dl-1'), 'Pending has no primary action').toBeNull()
    expect(primary('dl-5'), 'Skipped has no primary action').toBeNull()

    // Done → Open file; Failed → Retry; in-flight → Cancel queue.
    expect(primary('dl-3')?.textContent?.trim()).toBe('Open file')
    expect(primary('dl-4')?.textContent?.trim()).toBe('Retry')

    const cancel = primary('dl-2')
    expect(cancel, 'the in-flight row carries the cancel control').not.toBeNull()
    const cancelName =
      (cancel as HTMLElement).getAttribute('aria-label') ??
      (cancel as HTMLElement).textContent?.trim() ??
      ''
    expect(cancelName, 'CANCEL_CONTROL_LABEL').toBe('Cancel queue')

    // CANCEL_LABEL_FORBIDDEN — exact-match, so `Cancel queue` itself is allowed.
    for (const id of RENDERED_IDS) {
      const label = primary(id)?.textContent?.trim()
      if (label === undefined) {
        continue
      }
      expect(
        ['Cancel', 'Cancel item', 'Cancel download', 'Stop'],
        id + ' renders a forbidden cancel label',
      ).not.toContain(label)
    }

    // USER_LOCKS — cancelling the queue takes effect with NO confirm dialog.
    await click(cancel)
    await vi.waitFor(() => {
      expect(requests('/downloads/cancel', 'POST')).toHaveLength(1)
    })
    expect(
      screen.queryByTestId('confirm-modal'),
      'cancel never opens a confirm',
    ).toBeNull()

    // Retry re-queues through the per-id reset endpoint.
    await click(primary('dl-4'))
    await vi.waitFor(() => {
      expect(requests('/downloads/dl-4/reset', 'POST')).toHaveLength(1)
    })

    // Open file goes through the existing IPC, not a fetch.
    await click(primary('dl-3'))
    await vi.waitFor(() => {
      expect(opened).toEqual(['C:/out/dl-3.mp4'])
    })

    // KEBAB_MENU_ORDER on a finished middle row: every action is available.
    const full = await openKebab('dl-3')
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
    for (const item of menuItems(full)) {
      expect(item.hasAttribute('disabled'), 'no menu item is ever disabled').toBe(false)
      expect(item.getAttribute('aria-disabled')).not.toBe('true')
    }
    await keydown(document.body, 'Escape')

    // The first row has no file on disk and nothing above it, so open-file,
    // open-folder, move-up and move-top are ABSENT — not disabled.
    const first = await openKebab('dl-1')
    const firstActions = menuItems(first).map((item) => item.dataset.menuAction)
    expect(firstActions).toEqual(['copy-location', 'move-down', 'move-bottom', 'remove'])
    expect(
      menuAction(first, 'copy-location')?.textContent?.trim(),
      'no file on disk yet, so the URL is the location',
    ).toBe('Copy URL')
    await keydown(document.body, 'Escape')

    // REORDER_WIRE_CONTRACT — the kebab move sends the full permutation.
    await click(menuAction(await openKebab('dl-3'), 'move-up'))
    await vi.waitFor(() => {
      expect(requests('/downloads/reorder', 'PUT')).toHaveLength(1)
    })
    const kebabBody = requests('/downloads/reorder', 'PUT')[0].body
    expect(kebabBody).toEqual(buildReorderBody(RENDERED_IDS, 'dl-3', 'up'))
    expect(kebabBody).toEqual({ job_ids: ['dl-1', 'dl-3', 'dl-2', 'dl-4', 'dl-5'] })
    expect(kebabBody, 'never a {id, direction} body — the API 422s it').not.toHaveProperty(
      'direction',
    )

    // Alt+ArrowDown issues the same request with `down`, and does NOT open the
    // kebab menu that a bare ArrowDown would.
    await keydown(card('dl-1'), 'ArrowDown', { altKey: true })
    await vi.waitFor(() => {
      expect(requests('/downloads/reorder', 'PUT')).toHaveLength(2)
    })
    expect(requests('/downloads/reorder', 'PUT')[1].body).toEqual(
      buildReorderBody(RENDERED_IDS, 'dl-1', 'down'),
    )
    expect(screen.queryByTestId('queue-card-menu')).toBeNull()

    // Without Alt the arrow keys are navigation, not reordering.
    await keydown(card('dl-3'), 'ArrowUp')
    await keydown(card('dl-3'), 'ArrowDown')
    expect(requests('/downloads/reorder', 'PUT'), 'a bare arrow never reorders').toHaveLength(2)
  })

  it('AC-46.14 the empty invite focuses url-input and no drop zone is rendered', async () => {
    rows = []
    await renderQueue()

    const invite = inside(host, 'queue-empty-invite')
    expect(invite, 'EMPTY_STATE_CONTRACT — the downloader half').not.toBeNull()
    expect((invite as HTMLElement).textContent).toContain(
      'Paste a video link above to queue a download',
    )

    // The downloader has NO local-file intake, so the file-drop invitation must
    // not appear on this page in either state.
    expect(within(host).queryByTestId('queue-empty-dropzone')).toBeNull()
    expect(within(host).queryByTestId('queue-drop-strip')).toBeNull()

    // The action is real production wiring, not a placeholder: it focuses the
    // page's existing URL field.
    const action = inside(host, 'queue-empty-invite-action')
    expect(action, 'a real button, not decorative copy').not.toBeNull()
    await click(action)
    expect(document.activeElement).toBe(within(host).queryByTestId('url-input'))
  })

  it('AC-52.1/.2/.4 mounts one shared queue header with live selection, status counts, and toolbar', async () => {
    await renderQueue()
    const region = within(host).getByTestId('download-queue-region')
    const header = within(region).getByTestId('queue-header-row')
    expect(within(header).getByTestId('queue-select-all').tagName).toBe('INPUT')
    expect(within(header).getByTestId('queue-summary')).toBeTruthy()
    expect(within(header).getByTestId('processor-indicator')).toHaveTextContent('Processing')
    expect(within(header).getByTestId('queue-toolbar').querySelectorAll('button')).toHaveLength(4)
    expect(within(region).getAllByTestId('queue-header-row')).toHaveLength(1)

    const summary = within(header).getByTestId('queue-summary')
    expect(summary.querySelectorAll('[data-tone]')).toHaveLength(5)
    expect(summary).not.toHaveTextContent('AgeRestricted')
    const requestsBefore = fetches.length
    await user.click(within(header).getByTestId('queue-status-more'))
    const details = within(header).getByTestId('queue-status-details')
    expect(details).toHaveTextContent('AgeRestricted: 0')
    expect(details).toHaveTextContent('QualityBlocked: 0')
    expect(fetches).toHaveLength(requestsBefore)

    await user.click(within(header).getByTestId('queue-select-all'))
    expect(within(host).getByTestId('bulk-selection-count')).toHaveTextContent('5')
    await user.click(within(header).getByTestId('queue-toolbar-pause'))
    await vi.waitFor(() => expect(requests('/downloads/pause', 'POST')).toHaveLength(1))
  })

  it('AC-52.3/.5 keeps Idle without a live chip and preserves header, bulk, scroller order', async () => {
    processorState = 'Idle'
    await renderQueue()
    const region = within(host).getByTestId('download-queue-region')
    const header = within(region).getByTestId('queue-header-row')
    expect(within(header).getByTestId('processor-indicator')).not.toBeVisible()
    await user.click(within(header).getByTestId('queue-select-all'))
    const bulk = within(region).getByTestId('bulk-action-bar')
    const list = within(region).getByTestId('queue-list')
    expect(header.compareDocumentPosition(bulk) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(bulk.compareDocumentPosition(list) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(list.parentElement?.className).toContain('overflow-auto')
    expect(region.className).toContain('min-h-[20rem]')
  })

  it('AC-53.1 Enter submits one exact Add body while blank Add leaves the queue untouched', async () => {
    await renderQueue()
    const url = within(host).getByTestId('url-input') as HTMLInputElement
    const add = within(host).getByTestId('add-btn')
    expect(url.closest('form')).toContainElement(add)
    await user.type(url, 'https://example.invalid/watch?v=layout53{Enter}')
    await vi.waitFor(() => expect(requests('/downloads', 'POST')).toHaveLength(1))
    expect(requests('/downloads', 'POST')[0].body).toEqual({
      url: 'https://example.invalid/watch?v=layout53',
      quality: '1080p', audio_only: false, audio_format: 'default',
    })
    expect(within(host).getAllByTestId('queue-card')).toHaveLength(5)
    await user.clear(url)
    await user.click(add)
    expect(requests('/downloads', 'POST')).toHaveLength(1)
    expect(within(host).getByTestId('error-banner')).toHaveTextContent('URL is required')
  })

  it('AC-53.2 Advanced starts closed for no cookie/SABR and remains local after a SABR refresh', async () => {
    await renderQueue()
    const toggle = within(host).getByTestId('add-advanced-toggle')
    expect(toggle.tagName).toBe('BUTTON')
    expect(toggle).toHaveAttribute('aria-expanded', 'false')
    expect(within(host).getByTestId('cookie-mode-none')).not.toBeVisible()
    const before = requests('/settings/downloader', 'PUT').length
    await user.click(toggle)
    expect(toggle).toHaveAttribute('aria-expanded', 'true')
    expect(within(host).getByTestId('cookie-mode-none')).toBeVisible()
    await user.click(toggle)
    expect(toggle).toHaveAttribute('aria-expanded', 'false')
    sabrMode = 'active'
    await act(async () => { await queryClient.invalidateQueries({ queryKey: ['downloads', 'sabr'] }) })
    expect(toggle).toHaveAttribute('aria-expanded', 'false')
    await user.click(toggle)
    await vi.waitFor(() => expect(within(host).getByTestId('sabr-status')).toBeVisible())
    await user.click(toggle)
    expect(toggle).toHaveAttribute('aria-expanded', 'false')
    expect(requests('/settings/downloader', 'PUT')).toHaveLength(before)
  })

  it('AC-53.2 keeps an explicit Advanced toggle while initial settings are still loading', async () => {
    let releaseSettings!: () => void
    const pendingSettings = new Promise<void>((resolve) => {
      releaseSettings = resolve
    })
    settingsGetGate = pendingSettings

    await renderQueue()
    const toggle = within(host).getByTestId('add-advanced-toggle')
    await user.click(toggle)
    expect(toggle).toHaveAttribute('aria-expanded', 'true')

    await act(async () => {
      releaseSettings()
      await pendingSettings
    })
    await vi.waitFor(() => {
      expect(queryClient.getQueryState(['settings', 'downloader'])?.fetchStatus).toBe('idle')
    })
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0))
    })
    expect(toggle).toHaveAttribute('aria-expanded', 'true')
    expect(within(host).getByTestId('cookie-mode-none')).toBeVisible()
    expect(requests('/settings/downloader', 'PUT')).toHaveLength(0)
  })

  it('AC-53.2/.3 restores successful cookie writes after unmount, cache reuse, and refetch', async () => {
    const first = await renderQueue()
    const firstToggle = within(host).getByTestId('add-advanced-toggle')
    await user.click(firstToggle)
    await user.click(within(host).getByTestId('cookie-mode-browser'))
    await vi.waitFor(() => expect(requests('/settings/downloader', 'PUT')).toHaveLength(1))
    await user.selectOptions(within(host).getByTestId('cookie-browser'), 'firefox')
    await vi.waitFor(() => expect(requests('/settings/downloader', 'PUT')).toHaveLength(2))
    const profile = within(host).getByTestId('cookie-profile')
    await user.clear(profile)
    await user.type(profile, 'Work')
    await user.tab()
    await vi.waitFor(() => expect(requests('/settings/downloader', 'PUT')).toHaveLength(3))

    first.unmount()
    await renderQueue()
    const toggle = within(host).getByTestId('add-advanced-toggle')
    await vi.waitFor(() => expect(toggle).toHaveAttribute('aria-expanded', 'true'))
    expect(within(host).getByTestId('cookie-mode-browser')).toBeChecked()
    expect(within(host).getByTestId('cookie-browser')).toHaveValue('firefox')
    expect(within(host).getByTestId('cookie-profile')).toHaveValue('Work')
    expect(within(host).getByTestId('cookie-file')).toHaveValue('')
  })

  it('AC-53.2/.3 configured browser opens Advanced and native mode radios keep exact PUT/test bodies', async () => {
    configuredCookieMode = 'browser'
    await renderQueue()
    const toggle = within(host).getByTestId('add-advanced-toggle')
    await vi.waitFor(() => expect(toggle).toHaveAttribute('aria-expanded', 'true'))
    const browser = within(host).getByTestId('cookie-mode-browser') as HTMLInputElement
    const file = within(host).getByTestId('cookie-mode-file') as HTMLInputElement
    expect(browser.tagName).toBe('INPUT')
    expect(browser.type).toBe('radio')
    expect(browser.checked).toBe(true)
    expect(file.type).toBe('radio')
    await user.click(file)
    await vi.waitFor(() => expect(requests('/settings/downloader', 'PUT')).toHaveLength(1))
    expect(requests('/settings/downloader', 'PUT')[0].body).toEqual({
      cookie_mode: 'file', cookie_browser: 'chrome',
      cookie_browser_profile: 'Default', cookie_file_path: '',
    })
    expect(within(host).getByTestId('cookie-file')).toBeVisible()
    expect(within(host).getByTestId('cookie-browser')).not.toBeVisible()
    await user.click(browser)
    await vi.waitFor(() => expect(requests('/settings/downloader', 'PUT')).toHaveLength(2))
    await user.click(within(host).getByTestId('cookie-test-btn'))
    await vi.waitFor(() => expect(requests('/downloads/cookies/test', 'POST')).toHaveLength(1))
    expect(requests('/downloads/cookies/test', 'POST')[0].body).toEqual({
      mode: 'browser', browser: 'chrome', profile: 'Default',
    })
  })

  it('AC-53.4 active SABR shows a warning beside Quality and keeps each Advanced command live once', async () => {
    sabrMode = 'active'
    await renderQueue()
    const toggle = within(host).getByTestId('add-advanced-toggle')
    await vi.waitFor(() => expect(toggle).toHaveAttribute('aria-expanded', 'true'))
    const warning = within(host).getByTestId('sabr-quality-chip')
    expect(warning).toHaveAttribute('data-tone', 'warning')
    expect(warning).toHaveTextContent('SABR')
    const status = within(host).getByTestId('sabr-status')
    expect(status).toBeVisible()
    for (const [id, path] of [
      ['sabr-check-btn', '/downloads/sabr/check'],
      ['sabr-force-btn', '/downloads/sabr/force'],
      ['sabr-clear-btn', '/downloads/sabr/clear'],
    ] as const) {
      const button = within(host).getByTestId(id)
      expect(button).toBeVisible()
      await user.click(button)
      await vi.waitFor(() => expect(requests(path, 'POST')).toHaveLength(1))
    }
    expect(requests('/downloads/sabr/check', 'POST')).toHaveLength(1)
    expect(requests('/downloads/sabr/force', 'POST')).toHaveLength(1)
    expect(requests('/downloads/sabr/clear', 'POST')).toHaveLength(1)
  })

  it('AC-53.5 retains the queue region, header, and list scroller after Zone 1 composition', async () => {
    await renderQueue()
    const root = within(host).getByTestId('downloader-page')
    const region = within(root).getByTestId('download-queue-region')
    expect(root.className).toContain('h-full')
    expect(region.className).toContain('min-h-[20rem]')
    expect(within(region).getByTestId('queue-header-row')).toBeTruthy()
    expect(within(region).getByTestId('queue-list').parentElement?.className).toContain('overflow-auto')
    expect(within(root).getByTestId('url-input').closest('form')).toBeTruthy()
  })

  it('AC-124.15 a card shows the received quality next to the request when they differ', async () => {
    rows = [
      queueItem({
        id: 'dl-1',
        title: 'First',
        status: 'Done',
        quality: '1080p',
        received_height: 360,
        progress: 100,
        queue_position: 1,
      }),
      queueItem({ id: 'dl-2', title: 'Second', quality: '720p', queue_position: 2 }),
    ]
    await renderQueue()
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0))
    })

    const meta = (id: string): string => inside(card(id), 'queue-card-meta')?.textContent ?? ''
    expect(meta('dl-1')).toContain('360p (asked 1080p)')
    expect(meta('dl-2')).toContain('720p')
    expect(meta('dl-2')).not.toContain('asked')
  })
})

// ---------------------------------------------------------------------------
// MEU-47 — selection and Clear finished on the downloader (AC-47.4, AC-47.7).
//
// `CLEAR_FINISHED_SEMANTICS` is wired on BOTH pages, and a sibling home passing
// does not cover this one (MOUNT_GATE_CLAUSE_4). The harness is separate from
// the MEU-46 block because these cases need a queue that can change mid-run and
// a DELETE that can answer 404.
// ---------------------------------------------------------------------------

describe('MEU-47 DownloaderPage bulk selection', () => {
  let user: ReturnType<typeof userEvent.setup>
  /** The Testing Library container for the tree under test. */
  let host: HTMLElement
  const fetches: Array<{ url: string; method: string; body?: unknown }> = []
  let rows: DownloadListItem[] = []
  let deleteFails = new Set<string>()
  let onDelete: (id: string) => void = () => undefined
  /** Status the reorder PUT answers with, so a test can reject the whole fold. */
  let reorderStatus = 204
  /** Gate held closed to observe the page WHILE a fan-out is still in flight. */
  let holdReorder: (() => void) | null = null

  function queueItem(overrides: Partial<DownloadListItem>): DownloadListItem {
    return {
      id: 'dl-0',
      url: 'https://example.invalid/watch?v=dl0',
      title: 'Clip',
      quality: '1080p',
      status: 'Pending',
      progress: 0,
      speed: null,
      eta: null,
      file_size: null,
      file_path: null,
      queue_position: 1,
      received_height: null,
      ...overrides,
    }
  }

  /** Two Done rows, so a partial sweep has both a success and a failure. */
  function mixedRows(): DownloadListItem[] {
    return [
      queueItem({ id: 'dl-1', title: 'First', status: 'Pending', queue_position: 1 }),
      queueItem({ id: 'dl-2', title: 'Second', status: 'Downloading', progress: 42, queue_position: 2 }),
      queueItem({
        id: 'dl-3',
        title: 'Third',
        status: 'Done',
        progress: 100,
        file_size: 156_000_000,
        file_path: 'C:/out/dl-3.mp4',
        queue_position: 3,
      }),
      queueItem({ id: 'dl-4', title: 'Fourth', status: 'Failed', queue_position: 4 }),
      queueItem({
        id: 'dl-5',
        title: 'Fifth',
        status: 'Done',
        progress: 100,
        file_path: 'C:/out/dl-5.mp4',
        queue_position: 5,
      }),
      queueItem({ id: 'dl-6', title: 'Sixth', status: 'Skipped', queue_position: 6 }),
    ]
  }

  beforeEach(() => {
    user = userEvent.setup()
    fetches.length = 0
    rows = mixedRows()
    deleteFails = new Set<string>()
    onDelete = () => undefined
    reorderStatus = 204
    holdReorder = null
    queryClient.clear()
    mockApi()
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input)
        const method = (init?.method ?? 'GET').toUpperCase()
        let body: unknown
        if (typeof init?.body === 'string' && init.body.length > 0) {
          body = JSON.parse(init.body)
        }
        fetches.push({ url, method, body })
        if (url.includes('/downloads/sabr')) {
          return new Response(JSON.stringify({ mode: 'inactive', source: null, checked_at: null }), {
            status: 200,
          })
        }
        if (url.includes('/settings/downloader')) {
          return new Response(
            JSON.stringify({
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
            }),
            { status: 200 },
          )
        }
        if (/\/downloads\/?$/.test(new URL(url).pathname) && method === 'GET') {
          return new Response(
            JSON.stringify({
              items: rows,
              processor: { state: 'Processing', current_job_id: 'dl-2' },
            }),
            { status: 200 },
          )
        }
        if (url.includes('/downloads/reorder') && method === 'PUT') {
          if (holdReorder !== null) {
            await new Promise<void>((resolve) => {
              holdReorder = resolve
            })
          }
          return reorderStatus === 204
            ? new Response(null, { status: 204 })
            : new Response(JSON.stringify({ detail: 'reorder rejected' }), {
                status: reorderStatus,
              })
        }
        if (method === 'DELETE') {
          const id = new URL(url).pathname.split('/downloads/')[1] ?? ''
          onDelete(id)
          if (deleteFails.has(id)) {
            return new Response(JSON.stringify({ detail: 'download ' + id + ' not found' }), {
              status: 404,
            })
          }
          rows = rows.filter((entry) => entry.id !== id)
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
      host = render(
        createElement(QueryClientProvider, { client: queryClient }, createElement(DownloaderPage)),
      ).container
    })
    await vi.waitFor(() => {
      expect(within(host).queryAllByTestId('queue-card')).toHaveLength(rows.length)
    })
  }

  function testId(scope: HTMLElement, id: string): HTMLElement | null {
    return within(scope).queryByTestId(id)
  }

  function required(scope: HTMLElement, id: string): HTMLElement {
    return within(scope).getByTestId(id)
  }

  async function click(el: Element | null): Promise<void> {
    if (el === null) {
      throw new Error('cannot click a missing element')
    }
    await user.click(el)
  }

  /** Every recorded call to one endpoint, in the order the page issued them. */
  function requests(fragment: string, method: string): typeof fetches {
    return fetches.filter((call) => call.url.includes(fragment) && call.method === method)
  }

  /** The G35 partial-result report, if one is currently on screen. */
  function toast(): HTMLElement | null {
    return screen.queryByTestId('bulk-toast')
  }

  it('AC-47.7 Clear finished sweeps only CLEAR_FINISHED_SNAPSHOT_STATUSES and survives a mid-run 404', async () => {
    await renderQueue()

    // dl-3 has already been removed by someone else; dl-1 finishes the instant
    // the sweep starts. Neither may change the set of ids the run attempts.
    deleteFails.add('dl-3')
    onDelete = () => {
      rows = rows.map((entry) =>
        entry.id === 'dl-1'
          ? { ...entry, status: 'Done', progress: 100, file_path: 'C:/out/dl-1.mp4' }
          : entry,
      )
    }

    await click(testId(required(host, 'queue-toolbar'), 'queue-toolbar-clear-finished'))

    await vi.waitFor(() => {
      expect(screen.queryByTestId('bulk-toast')).not.toBeNull()
    })

    const deletes = fetches
      .filter((call) => call.method === 'DELETE')
      .map((call) => new URL(call.url).pathname.split('/downloads/')[1] ?? '')
    expect(deletes.slice().sort(), 'only the rows that were Done at click time').toEqual([
      'dl-3',
      'dl-5',
    ])
    expect(deletes, 'clause 1 — a row that becomes Done mid-run is not swept').not.toContain('dl-1')
    expect(deletes, 'Failed is not swept').not.toContain('dl-4')
    expect(deletes, 'Skipped is not swept').not.toContain('dl-6')
    expect(deletes.filter((id) => id === 'dl-5'), 'the 404 did not abort the run').toHaveLength(1)

    // Clause 5: the queue record goes, the downloaded file does not.
    for (const call of fetches.filter((entry) => entry.method === 'DELETE')) {
      expect(call.body, 'no purge payload').toBeUndefined()
      expect(call.url).not.toMatch(/purge|files/)
    }

    // Clause 7: the partial result is reported with a reason per failure.
    const note = screen.queryByTestId('bulk-toast')
    expect(note?.getAttribute('role')).toBe('status')
    expect(note?.textContent).toContain('404')
    expect(note?.textContent).toContain('dl-3')
  })

  it('AC-47.4 the downloader bar is sticky above the list and unmounts on an empty selection', async () => {
    await renderQueue()

    expect(screen.queryByTestId('bulk-action-bar')).toBeNull()
    const header = required(host, 'queue-select-all')

    await click(header)
    const bar = required(host, 'bulk-action-bar')
    expect(required(bar, 'bulk-selection-count').textContent).toContain(String(rows.length))
    expect(bar.className, 'USER_LOCKS — sticky, never a floating bottom bar').toContain('sticky')

    const list = required(host, 'queue-list')
    expect(
      bar.compareDocumentPosition(list) & Node.DOCUMENT_POSITION_FOLLOWING,
      'the bar is rendered above the list',
    ).toBeTruthy()

    await click(testId(bar, 'bulk-clear-selection'))
    expect(screen.queryByTestId('bulk-action-bar')).toBeNull()
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
    const bar = required(host, 'bulk-action-bar')
    await click(testId(bar, 'bulk-move-top'))

    expect(
      requests('/downloads/reorder', 'PUT').length,
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
    await click(testId(required(host, 'bulk-action-bar'), 'bulk-move-bottom'))

    const isList = (call: { url: string; method: string }): boolean =>
      call.method === 'GET' && /\/downloads\/?$/.test(new URL(call.url).pathname)

    await vi.waitFor(() => {
      expect(fetches.slice(mark).filter(isList).length).toBeGreaterThan(0)
    })
    const after = fetches.slice(mark)
    const puts = after.filter(
      (call) => call.method === 'PUT' && call.url.includes('/downloads/reorder'),
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
    const bar = required(host, 'bulk-action-bar')
    await click(testId(bar, 'bulk-move-top'))

    await vi.waitFor(() => {
      expect(requests('/downloads/reorder', 'PUT').length).toBe(1)
    })

    const live = required(host, 'bulk-action-bar')
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
      requests('/downloads/reorder', 'PUT').length,
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
// MEU-49 — drag reorder on the downloader queue.
//
// Covers AC-49.21, AC-49.22, AC-49.23 (preservation), AC-49.24, AC-49.32-49.35,
// AC-49.37, AC-49.38 and AC-49.39.
//
// `JSDOM_RECT_RULE`: jsdom reports every rect as all-zero, so dnd-kit's own
// collision detection can never resolve a drop here. What a unit test CAN prove
// is the wiring on both sides of that gap — that the page hands `QueueList` an
// `onMoveToIndex`, that the callback dnd-kit would invoke produces exactly the
// absolute permutation `REORDER_WIRE_CONTRACT` demands, and that the gate,
// error path and disabled states behave. The pointer gesture itself is proved
// once, against real Electron, by `E2E_DRAG_DRIVER`.
//
// The two dnd-kit packages are therefore mocked at module scope: `DndContext`
// and `SortableContext` become pass-through fragments that record the props
// they were handed, which is the only way to reach `onDragEnd` without a
// completed drag. `vi.mock` is file-scoped and hoisted, so the earlier describes
// in this file also render against the stubs — harmless, since none of them
// asserts anything about dragging, and the stubs render their children exactly
// as the real components do.
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
      const [row] = next.splice(from, 1)
      next.splice(to, 0, row)
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

describe('MEU-49 DownloaderPage drag reorder', () => {
  const REPO_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '../../..')
  const PLAN_DIR = resolve(REPO_ROOT, 'docs/execution/plans/2026-09-03-p10-queue-card-dnd')
  const SETS = JSON.parse(readFileSync(resolve(PLAN_DIR, 'named-sets.json'), 'utf8')) as Record<
    string,
    { value: string[] }
  >
  const DRAG_HANDLE_TESTID = SETS.DND_TESTIDS.value[0]
  const SINGLE_FLIGHT_MODULE = '../../src/renderer/src/lib/queue/reorder-single-flight'

  let user: ReturnType<typeof userEvent.setup>
  /** The Testing Library container for the tree under test. */
  let host: HTMLElement
  /** Kept so AC-49.37 can unmount the route while a PUT is still on the wire. */
  let teardown: () => void = () => undefined
  const fetches: Array<{ url: string; method: string; body?: unknown }> = []
  let rows: DownloadListItem[] = []
  /** Status the reorder PUT answers with, so a test can reject one. */
  let reorderStatus = 204
  /** Gate held closed to observe the page WHILE a reorder is still in flight. */
  let holdReorder: (() => void) | null = null

  function queueItem(overrides: Partial<DownloadListItem>): DownloadListItem {
    return {
      id: 'dl-0',
      url: 'https://example.invalid/watch?v=dl0',
      title: 'Clip',
      quality: '1080p',
      status: 'Pending',
      progress: 0,
      speed: null,
      eta: null,
      file_size: null,
      file_path: null,
      queue_position: 1,
      received_height: null,
      ...overrides,
    }
  }

  /** Six rows, so there is a first, a last and four unambiguous middles. */
  function defaultRows(): DownloadListItem[] {
    return [
      queueItem({ id: 'dl-1', title: 'First', queue_position: 1 }),
      queueItem({ id: 'dl-2', title: 'Second', queue_position: 2 }),
      queueItem({ id: 'dl-3', title: 'Third', queue_position: 3 }),
      queueItem({ id: 'dl-4', title: 'Fourth', queue_position: 4 }),
      queueItem({ id: 'dl-5', title: 'Fifth', queue_position: 5 }),
      queueItem({ id: 'dl-6', title: 'Sixth', queue_position: 6 }),
    ]
  }

  const IDS = ['dl-1', 'dl-2', 'dl-3', 'dl-4', 'dl-5', 'dl-6']

  beforeEach(() => {
    user = userEvent.setup()
    fetches.length = 0
    rows = defaultRows()
    reorderStatus = 204
    holdReorder = null
    dnd.context = null
    dnd.sortableItems = null
    dnd.draggingId = null
    teardown = () => undefined
    queryClient.clear()
    mockApi()
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input)
        const method = (init?.method ?? 'GET').toUpperCase()
        let body: unknown
        if (typeof init?.body === 'string' && init.body.length > 0) {
          body = JSON.parse(init.body)
        }
        fetches.push({ url, method, body })
        if (url.includes('/downloads/sabr')) {
          return new Response(
            JSON.stringify({ mode: 'inactive', source: null, checked_at: null }),
            { status: 200 },
          )
        }
        if (url.includes('/settings/downloader')) {
          return new Response(
            JSON.stringify({
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
            }),
            { status: 200 },
          )
        }
        if (url.includes('/downloads/reorder') && method === 'PUT') {
          if (holdReorder !== null) {
            await new Promise<void>((release) => {
              holdReorder = release
            })
          }
          return reorderStatus === 204
            ? new Response(null, { status: 204 })
            : new Response(JSON.stringify({ detail: 'reorder rejected' }), {
                status: reorderStatus,
              })
        }
        if (/\/downloads\/?$/.test(new URL(url).pathname) && method === 'GET') {
          return new Response(
            JSON.stringify({ items: rows, processor: { state: 'Idle' } }),
            { status: 200 },
          )
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
        createElement(QueryClientProvider, { client: queryClient }, createElement(DownloaderPage)),
      )
      host = view.container
      teardown = view.unmount
    })
    await vi.waitFor(() => {
      expect(within(host).queryAllByTestId('queue-card')).toHaveLength(rows.length)
    })
  }

  function card(id: string): HTMLElement {
    const match = within(host)
      .queryAllByTestId('queue-card')
      .find((row) => (row.textContent ?? '').includes(titleOf(id)))
    if (match === undefined) {
      throw new Error('no rendered card for ' + id)
    }
    return match
  }

  function titleOf(id: string): string {
    const row = rows.find((entry) => entry.id === id)
    if (row === undefined) {
      throw new Error('no queue row named ' + id)
    }
    return row.title
  }

  /** Every recorded reorder PUT, in the order the page issued them. */
  function reorderPuts(): typeof fetches {
    return fetches.filter(
      (call) => call.method === 'PUT' && call.url.includes('/downloads/reorder'),
    )
  }

  function listGets(): typeof fetches {
    return fetches.filter(
      (call) => call.method === 'GET' && /\/downloads\/?$/.test(new URL(call.url).pathname),
    )
  }

  /** `MOVE_TO_INDEX_CONTRACT` — targetIndex is FINAL, resolved pre-move. */
  function movedTo(ids: string[], id: string, targetIndex: number): { job_ids: string[] } {
    const next = [...ids]
    const [row] = next.splice(next.indexOf(id), 1)
    next.splice(targetIndex, 0, row)
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

  /** Focus the card's open region and press a chord, exactly as MEU-46 does. */
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
    return within(host).queryAllByTestId(DRAG_HANDLE_TESTID) as HTMLButtonElement[]
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

  it('AC-49.21 reorderDownloadToIndex issues one absolute permutation and reconciles once', async () => {
    await renderQueue()

    const command = (downloadCommands as unknown as Record<string, unknown>)
      .reorderDownloadToIndex
    expect(
      typeof command,
      'COMMAND_MODULE_RULE — the index-based reorder is a command, not a page onClick',
    ).toBe('function')

    const mark = fetches.length
    await act(async () => {
      await (command as (ids: string[], id: string, index: number) => Promise<void>)(
        IDS,
        'dl-1',
        2,
      )
    })
    await vi.waitFor(() => {
      expect(fetches.slice(mark).some((call) => call.method === 'GET')).toBe(true)
    })

    const after = fetches.slice(mark)
    const puts = after.filter((c) => c.method === 'PUT' && c.url.includes('/downloads/reorder'))
    expect(puts, 'one PUT for one move').toHaveLength(1)

    // REORDER_WIRE_CONTRACT — a complete permutation, never {id, direction}.
    expect(puts[0].body).toEqual({
      job_ids: ['dl-2', 'dl-3', 'dl-1', 'dl-4', 'dl-5', 'dl-6'],
    })
    expect(puts[0].body).toEqual(movedTo(IDS, 'dl-1', 2))
    expect(puts[0].body).not.toHaveProperty('direction')

    // Exactly one reconcile, mirroring `reorderDownload`'s single-gesture shape.
    expect(
      after.filter((c) => c.method === 'GET' && /\/downloads\/?$/.test(new URL(c.url).pathname)),
      'the list refetches once, after the PUT',
    ).toHaveLength(1)
  })

  it('AC-49.21 the same command exists for conversions and takes no direction argument', async () => {
    const convert = (await import(
      '../../src/renderer/src/features/converter/convert-commands'
    )) as unknown as Record<string, unknown>

    expect(typeof convert.reorderConversionToIndex).toBe('function')
    // (ids, movedId, targetIndex) — three parameters, and the third is an
    // index, not a 'up' | 'down' | 'top' | 'bottom' direction.
    expect((convert.reorderConversionToIndex as (...args: unknown[]) => unknown).length).toBe(3)
    expect(
      ((downloadCommands as unknown as Record<string, unknown>).reorderDownloadToIndex as
        | ((...args: unknown[]) => unknown)
        | undefined)?.length,
    ).toBe(3)
  })

  it('AC-49.22 the page hands QueueList an onMoveToIndex wired to its own command', async () => {
    await renderQueue()

    expect(dnd.context, 'DND_OPT_IN_RULE — the downloader opts in').not.toBeNull()
    expect(dnd.sortableItems, 'SortableContext receives the queue ids').toEqual(IDS)

    const mark = fetches.length
    await drop('dl-1', 'dl-3')
    await vi.waitFor(() => {
      expect(
        fetches.slice(mark).filter((c) => c.method === 'PUT').length,
        'the drop reaches the command module',
      ).toBe(1)
    })
    expect(fetches.slice(mark).filter((c) => c.method === 'PUT')[0].body).toEqual(
      movedTo(IDS, 'dl-1', 2),
    )
  })

  it('AC-49.22 a rejected drop surfaces the error and leaves the rendered order alone', async () => {
    reorderStatus = 500
    await renderQueue()

    const before = within(host)
      .queryAllByTestId('queue-card-title')
      .map((node) => node.textContent)

    await drop('dl-1', 'dl-4')

    await vi.waitFor(() => {
      const banner = within(host).queryByTestId('error-banner')
      expect(banner?.hasAttribute('hidden')).toBe(false)
      expect(banner?.textContent ?? '').not.toBe('')
    })
    // NO_DEAD_CONTROL_RULE / REORDER_FEEDBACK_TIER clause 2: no optimistic
    // reorder survives a rejection — the row the server refused to move is
    // still where it was.
    expect(
      within(host)
        .queryAllByTestId('queue-card-title')
        .map((node) => node.textContent),
      'the list is not left in a state the server never accepted',
    ).toEqual(before)
  })

  it('AC-49.23 the kebab and Alt+Arrow reorder paths survive on a page that also drags', async () => {
    await renderQueue()

    // This is a PRESERVATION criterion: it is green from the first run and stays
    // green once drag lands. That is the whole assertion -- the "on a page that
    // also drags" half is proved by this same body still passing after the page
    // is wrapped in a DndContext, not by an extra expect() that would only be
    // satisfiable post-implementation and would drag a preservation AC into the
    // Red failure set.

    // WCAG_DRAG_RULE — the single-pointer alternative is all four items, on a
    // middle row where all four are possible.
    const middle = await openKebab('dl-3')
    const actions = within(middle)
      .queryAllByRole('menuitem')
      .map((item) => item.dataset.menuAction)
    for (const action of ['move-up', 'move-down', 'move-top', 'move-bottom']) {
      expect(actions, 'the kebab keeps ' + action).toContain(action)
    }

    // Cast, not a null-check: `menuAction` is nullable because AC-49.37 asserts
    // absence with it. The `toContain` above has already proved this one exists.
    await user.click(menuAction(middle, 'move-up') as HTMLButtonElement)
    await vi.waitFor(() => {
      expect(reorderPuts()).toHaveLength(1)
    })
    expect(reorderPuts()[0].body).toEqual(buildReorderBody(IDS, 'dl-3', 'up'))

    // And the keyboard alternative still issues its own request.
    await keydown('dl-2', 'ArrowDown', true)
    await vi.waitFor(() => {
      expect(reorderPuts()).toHaveLength(2)
    })
    expect(reorderPuts()[1].body).toEqual(buildReorderBody(IDS, 'dl-2', 'down'))
  })

  it('AC-49.24 every DND_TESTIDS entry is registered in the e2e testid registry', () => {
    const registry = readFileSync(resolve(REPO_ROOT, 'ui/tests/e2e/test-ids.ts'), 'utf8')

    for (const id of SETS.DND_TESTIDS.value) {
      const constant = id.toUpperCase().replace(/-/g, '_')
      expect(
        registry,
        'E2E_LOCATOR_FORM — ' + id + ' must be reachable as a named export',
      ).toContain('export const ' + constant + " = '" + id + "'")
    }
  })

  it('AC-49.32 an in-flight reorder blocks a concurrent drop, and the next one goes through', async () => {
    await renderQueue()
    holdReorder = () => undefined

    // Alt+Arrow takes the gate first and parks on the wire.
    await keydown('dl-2', 'ArrowDown', true)
    await vi.waitFor(() => {
      expect(reorderPuts()).toHaveLength(1)
    })

    // The drop arrives while the first body is still unacknowledged. Its own
    // body would be computed from the SAME pre-mutation order, so letting it
    // through is the last-write-wins clobber REORDER_SINGLE_FLIGHT_RULE exists
    // to prevent.
    await drop('dl-5', 'dl-1')
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
    await drop('dl-5', 'dl-1')
    await vi.waitFor(() => {
      expect(reorderPuts(), 'the gate is free once the first request settled').toHaveLength(2)
    })
    expect(reorderPuts()[1].body).toEqual(movedTo(IDS, 'dl-5', 0))
  })

  it('AC-49.33 a bulk fold holds the gate for the whole sequence, not per request', async () => {
    await renderQueue()
    holdReorder = () => undefined

    await user.click(within(document.body).getByTestId('queue-select-all'))
    await user.click(within(within(host).getByTestId('bulk-action-bar')).getByTestId('bulk-move-top'))
    await vi.waitFor(() => {
      expect(reorderPuts().length).toBe(1)
    })

    // Mid-fold: the bulk run owns the gate, so the drop issues nothing. A gate
    // acquired per-request inside the fold would let this interleave between
    // two of the fold's own PUTs.
    await drop('dl-6', 'dl-1')
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
    await drop('dl-6', 'dl-1')
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
    expect(body.job_ids[0], 'dl-6 landed at the index the drop named').toBe('dl-6')
  })

  it('AC-49.34 release runs in a finally, so a rejected reorder does not deadlock the next one', async () => {
    reorderStatus = 500
    await renderQueue()

    await drop('dl-1', 'dl-3')
    await vi.waitFor(() => {
      const banner = within(host).queryByTestId('error-banner')
      expect(banner?.hasAttribute('hidden')).toBe(false)
    })
    expect(reorderPuts()).toHaveLength(1)

    // The gate must have been released on the failure path. Releasing only on
    // success turns one 500 into a permanently unreorderable queue.
    reorderStatus = 204
    await drop('dl-1', 'dl-3')
    await vi.waitFor(() => {
      expect(reorderPuts(), 'the second attempt still acquires the gate').toHaveLength(2)
    })
  })

  it('AC-49.35 while the gate is held every drag handle is disabled, without a remount', async () => {
    await renderQueue()

    const before = handles()
    expect(before.length, 'every row has a handle').toBe(rows.length)
    for (const handle of before) {
      expect(handle.disabled, 'nothing is held yet').toBe(false)
    }

    holdReorder = () => undefined
    // The gate is taken by ANOTHER card's kebab. A page-local useState mirror
    // is not written by that card, so only the module-level store in
    // REORDER_HELD_HOOK can make this assertion true.
    await keydown('dl-2', 'ArrowDown', true)
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

  it('AC-49.37 the gate lives with the queue, not the component, and is per queue key', async () => {
    const gate = (await import(SINGLE_FLIGHT_MODULE)) as unknown as {
      acquireQueueReorder: (key: string) => (() => void) | null
      isQueueReorderHeld: (key: string) => boolean
    }

    await renderQueue()
    holdReorder = () => undefined
    await keydown('dl-2', 'ArrowDown', true)
    await vi.waitFor(() => {
      expect(reorderPuts()).toHaveLength(1)
    })
    expect(gate.isQueueReorderHeld('download')).toBe(true)

    // Holding `download` says nothing about `convert` — REORDER_QUEUE_KEYS is a
    // map, not a single global flag.
    const convertRelease = gate.acquireQueueReorder('convert')
    expect(convertRelease, 'the other queue is still free').not.toBeNull()
    convertRelease?.()

    // The route unmounts while the PUT is still on the wire. A gate held in a
    // useRef dies here and hands the remounted page a free gate, which then
    // sends a second absolute permutation built from the pre-mutation order.
    teardown()
    teardown = () => undefined
    expect(
      gate.acquireQueueReorder('download'),
      'the in-flight reorder still owns the download gate after the unmount',
    ).toBeNull()

    await renderQueue()
    expect(gate.acquireQueueReorder('download')).toBeNull()

    const release = holdReorder
    holdReorder = null
    await act(async () => {
      release?.()
      await Promise.resolve()
    })
    await vi.waitFor(() => {
      expect(gate.isQueueReorderHeld('download'), 'the settled request frees it').toBe(false)
    })
    const freed = gate.acquireQueueReorder('download')
    expect(freed).not.toBeNull()
    freed?.()
  })

  it('AC-49.38 every reorder affordance that is present goes inert while the gate is held', async () => {
    await renderQueue()
    holdReorder = () => undefined

    await keydown('dl-2', 'ArrowDown', true)
    await vi.waitFor(() => {
      expect(reorderPuts()).toHaveLength(1)
    })

    // A middle card can move all four ways, so all four items are present and
    // all four must read as unavailable.
    const middle = await openKebab('dl-4')
    for (const action of ['move-up', 'move-down', 'move-top', 'move-bottom']) {
      const item = menuAction(middle, action)
      expect(item, 'the middle card offers ' + action).not.toBeNull()
      expect(item?.disabled, action + ' must not look live while the gate is held').toBe(true)
    }
    await user.keyboard('{Escape}')

    // The FIRST card can only move down. QueueCardMenu rule 1 is "unavailable
    // actions are absent, never disabled", so move-up and move-top stay absent
    // — demanding four disabled items here would contradict the component.
    const first = await openKebab('dl-1')
    expect(menuAction(first, 'move-up'), 'absent, not disabled').toBeNull()
    expect(menuAction(first, 'move-top'), 'absent, not disabled').toBeNull()
    for (const action of ['move-down', 'move-bottom']) {
      const item = menuAction(first, action)
      expect(item, 'the first card still offers ' + action).not.toBeNull()
      expect(item?.disabled, action + ' is present, so it must read as unavailable').toBe(true)
    }
    await user.keyboard('{Escape}')

    // ALT_ARROW_SUPPRESSION_RULE — the keyboard path is inert on the same
    // guard, and silently, since there is nothing to disable.
    await keydown('dl-4', 'ArrowUp', true)
    await keydown('dl-4', 'ArrowDown', true)
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
    const live = await openKebab('dl-4')
    for (const action of ['move-up', 'move-down', 'move-top', 'move-bottom']) {
      expect(menuAction(live, action)?.disabled, action + ' is live again').toBe(false)
    }
    await user.keyboard('{Escape}')
  })

  it('AC-49.39 the G37 Testing Library migration is complete, not partial', () => {
    const migration = SETS.TL_MIGRATION_FILES.value
    const interaction = SETS.TL_INTERACTION_FILES.value
    const mountOnly = SETS.TL_MOUNT_ONLY_FILES.value

    // This file is itself entry #7 of TL_MIGRATION_FILES, so the three tokens the
    // migration removes are assembled from fragments instead of written out: a
    // literal here would put them back into the very source this scan reads and
    // the check would fail on its own assertions.
    const SHIM = 'helpers/user' + '-event'
    const HAND_MOUNT = 'react-dom/' + 'client'
    const HAND_ROOT = 'create' + 'Root'

    // (i) The shim is gone and nothing reaches for it.
    expect(
      existsSync(resolve(REPO_ROOT, 'ui/tests/unit/' + SHIM + '.ts')),
      'the local user-event shim is deleted, not merely unused',
    ).toBe(false)

    // (ii) Mount half — all 14.
    expect(migration).toHaveLength(14)
    for (const relative of migration) {
      const source = readFileSync(resolve(REPO_ROOT, relative), 'utf8')
      expect(source, relative + ' imports the RTL renderer').toContain(
        "from '@testing-library/react'",
      )
      expect(source, relative + ' renders through render()').toContain('render(')
      expect(source, relative + ' queries through screen or within').toMatch(
        /\bscreen\b|\bwithin\(/,
      )
      expect(source, relative + ' still imports the deleted shim').not.toContain(SHIM)
      expect(source, relative + ' still mounts by hand').not.toContain(HAND_MOUNT)
      expect(source, relative + ' still calls the raw root API').not.toContain(HAND_ROOT)
      expect(
        /import\s*\{[^}]*\bact\b[^}]*\}\s*from\s*'react'/.test(source),
        relative + " still imports act from 'react' instead of from RTL",
      ).toBe(false)
    }

    // (iii) Interaction half — the 13, with the one exemption registered rather
    // than assumed. Forcing a no-op setup() into a file that simulates nothing
    // would be ceremony, not migration.
    expect(interaction).toHaveLength(13)
    expect(mountOnly).toHaveLength(1)
    expect([...interaction, ...mountOnly].sort()).toEqual([...migration].sort())
    for (const relative of interaction) {
      const source = readFileSync(resolve(REPO_ROOT, relative), 'utf8')
      expect(source, relative + ' imports user-event').toContain(
        "from '@testing-library/user-event'",
      )
      expect(source, relative + ' sets user-event up').toContain('userEvent.setup()')
    }
    for (const relative of mountOnly) {
      expect(interaction, relative + ' cannot be in both halves').not.toContain(relative)
    }

    // (iv) All four packages declared, at their registered ranges.
    const manifest = JSON.parse(
      readFileSync(resolve(REPO_ROOT, 'ui/package.json'), 'utf8'),
    ) as { devDependencies?: Record<string, string>; dependencies?: Record<string, string> }
    for (const entry of SETS.TESTING_LIBRARY_PACKAGES.value) {
      const at = entry.lastIndexOf('@')
      const name = entry.slice(0, at)
      const range = entry.slice(at + 1)
      expect(manifest.devDependencies?.[name], name + ' is a devDependency at ' + range).toBe(
        range,
      )
      expect(manifest.dependencies?.[name], name + ' is test-only').toBeUndefined()
    }
  })
})
