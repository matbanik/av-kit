/** @vitest-environment jsdom */

/**
 * MEU-55 Transcript page composition (AC-55.3–AC-55.6), exercised through the
 * real page against a stubbed fetch ledger. Every locator resolves inside its
 * owning root (Session 24 RULE-1).
 */
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, render, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { TranscriptPage } from '../../src/renderer/src/features/transcript/TranscriptPage'
import { queryClient } from '../../src/renderer/src/lib/query-client'
import type { TranscriptListItem } from '../../src/renderer/src/features/transcript/useTranscriptQueue'
import { expectBoundHint } from './helpers/bound-hint'

const here = dirname(fileURLToPath(import.meta.url))
const pageSource = readFileSync(
  resolve(here, '../../src/renderer/src/features/transcript/TranscriptPage.tsx'),
  'utf8',
)

type Ledger = Array<{ url: string; method: string; body?: unknown }>

function item(overrides: Partial<TranscriptListItem> & Pick<TranscriptListItem, 'id' | 'channel_name' | 'status'>): TranscriptListItem {
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

const SEED: TranscriptListItem[] = [
  item({
    id: 'a', channel_name: 'Alpha', status: 'Done', video_count: 4, transcripts_done: 4, word_count: 900,
    compiled_path: 'C:/t/Alpha/compiled/all.txt', zip_path: 'C:/t/Alpha.zip', last_title: 'Old', queue_position: 1,
  }),
  item({
    id: 'b', channel_name: 'Bravo', status: 'Processing', video_count: 10, transcripts_done: 2, word_count: 300,
    last_title: 'Episode 3', last_item_status: 'Done', queue_position: 2,
  }),
  item({ id: 'c', channel_name: 'Charlie', status: 'Failed', video_count: 5, transcripts_done: 1, queue_position: 3 }),
  item({ id: 'd', channel_name: 'Delta', status: 'Cancelled', video_count: 3, transcripts_done: 0, queue_position: 4 }),
  item({ id: 'e', channel_name: 'Echo', status: 'Pending', queue_position: 5 }),
]

function mockApi(openPath: (path: string) => Promise<void>): void {
  window.api = {
    getBackendUrl: async () => 'http://127.0.0.1:51234/api/v1',
    getToken: async () => 'gui-nonce',
    logStartupMetric: () => undefined,
    showDirectoryDialog: async () => undefined,
    showFileDialog: async () => undefined,
    showFilesDialog: async () => [],
    getPathForFile: () => '',
    openPath,
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

describe('MEU-55 transcript page composition', () => {
  let user: ReturnType<typeof userEvent.setup>
  let host: HTMLElement
  const fetches: Ledger = []
  const opened: string[] = []
  let items: TranscriptListItem[]
  let processorState: 'Idle' | 'Processing' | 'Paused'
  let postStatus: number
  let holdReorder: Promise<void> | null
  let reorderStatus: number
  let holdStart: Promise<void> | null
  let holdPost: Promise<void> | null

  const path = (url: string): string => new URL(url).pathname.replace('/api/v1', '')
  const requests = (method: string, pattern: RegExp): Ledger =>
    fetches.filter((row) => row.method === method && pattern.test(path(row.url)))

  beforeEach(() => {
    user = userEvent.setup()
    fetches.length = 0
    opened.length = 0
    items = SEED.map((row) => ({ ...row }))
    processorState = 'Processing'
    postStatus = 201
    holdReorder = null
    reorderStatus = 200
    holdStart = null
    holdPost = null
    queryClient.clear()
    mockApi(async (target) => {
      opened.push(target)
    })
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input)
        const method = (init?.method ?? 'GET').toUpperCase()
        const body = init?.body ? (JSON.parse(String(init.body)) as Record<string, unknown>) : undefined
        fetches.push({ url, method, body })
        const p = path(url)
        const envelope = (): Response =>
          new Response(JSON.stringify({ items, processor: { state: processorState } }), { status: 200 })
        if (p === '/settings/transcript') {
          return new Response(JSON.stringify({ delay_between_requests: 20 }), { status: 200 })
        }
        if (p === '/transcripts' && method === 'GET') {
          return envelope()
        }
        if (p === '/transcripts' && method === 'POST') {
          if (holdPost !== null) {
            await holdPost
          }
          if (postStatus >= 400) {
            return new Response(JSON.stringify({ error: { code: 'VALIDATION', message: 'bad channel' } }), {
              status: postStatus,
            })
          }
          return new Response(
            JSON.stringify({ id: 'new', channel_url: String(body?.channel_url), channel_name: 'Foxtrot', video_count: 3 }),
            { status: 201 },
          )
        }
        if (p === '/transcripts/reorder' && method === 'PUT') {
          if (holdReorder !== null) {
            await holdReorder
          }
          if (reorderStatus >= 400) {
            return new Response(JSON.stringify({ error: { code: 'CONFLICT', message: 'reorder rejected' } }), {
              status: reorderStatus,
            })
          }
          const order = (body?.job_ids as string[]) ?? []
          items = order.map((id, index) => ({ ...(items.find((row) => row.id === id) as TranscriptListItem), queue_position: index + 1 }))
          return envelope()
        }
        if (p === '/transcripts/start' && holdStart !== null) {
          await holdStart
        }
        if (/\/compile$/.test(p)) {
          return new Response(JSON.stringify({ compiled_paths: ['C:/t/x/compiled/all.txt'] }), { status: 200 })
        }
        return new Response(JSON.stringify({}), { status: 200 })
      }),
    )
  })

  afterEach(() => {
    cleanup()
    queryClient.clear()
    vi.unstubAllGlobals()
  })

  async function renderPage(): Promise<void> {
    await act(async () => {
      host = render(createElement(QueryClientProvider, { client: queryClient }, createElement(TranscriptPage))).container
    })
    // Setup only: wait for the stubbed queue to load (the empty invite shows
    // before the first fetch resolves), and for the processor state to apply.
    const expected = items.length
    await vi.waitFor(() => {
      expect(fetches.some((row) => row.method === 'GET' && path(row.url) === '/transcripts')).toBe(true)
      if (expected === 0) {
        expect(within(host).queryAllByTestId('transcript-empty-invite')).toHaveLength(1)
      } else {
        expect(within(host).queryAllByTestId('channel-card')).toHaveLength(expected)
      }
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

  function header(): HTMLElement {
    return within(host).getByTestId('queue-header-row')
  }

  function toolbar(): HTMLElement {
    return within(header()).getByRole('group', { name: 'Transcript queue actions' })
  }

  async function openMenu(name: string): Promise<HTMLElement> {
    await user.click(within(card(name)).getByTestId('queue-card-kebab'))
    return within(card(name)).getByTestId('queue-card-menu')
  }

  it('AC-97.4 HINTS channel-input and add-btn carry their chords', async () => {
    await renderPage()
    expectBoundHint(within(host).getByTestId('channel-input'), 'transcript:add')
    expectBoundHint(within(host).getByTestId('add-btn'), 'page:primary')
  })

  it('AC-55.3 header has title, nonzero chips, full-count More and a three-action toolbar', async () => {
    await renderPage()
    const row = header()
    expect(within(row).getByRole('heading', { name: 'Channels' })).toBeTruthy()
    expect(within(row).queryByRole('checkbox')).toBeNull()
    const summary = within(row).getByTestId('transcript-queue-summary')
    for (const status of ['Pending', 'Processing', 'Done', 'Failed', 'Cancelled']) {
      expect(summary.textContent, status).toContain(status)
    }
    expect(summary.textContent).not.toContain('Paused')
    await user.click(within(row).getByTestId('queue-status-more'))
    const details = within(row).getByTestId('queue-status-details')
    expect(details.textContent).toContain('Paused: 0')
    expect(details.textContent).toContain('Done: 1')
    const buttons = within(toolbar()).getAllByRole('button')
    expect(buttons.map((node) => node.getAttribute('data-testid'))).toEqual(['start-btn', 'pause-btn', 'stop-btn'])
    expect(within(host).queryByText(/Clear finished/)).toBeNull()
    expect(within(host).queryByTestId('resume-btn')).toBeNull()
    const mutations = fetches.filter((row) => row.method !== 'GET')
    expect(mutations).toEqual([])
  })

  it('AC-55.3 the Pause/Resume node swaps id, label and command with processor state', async () => {
    processorState = 'Paused'
    await renderPage()
    expect(within(toolbar()).queryByTestId('pause-btn')).toBeNull()
    const resume = within(toolbar()).getByTestId('resume-btn')
    expect(resume.textContent).toContain('Resume')
    await user.click(resume)
    await vi.waitFor(() => {
      expect(requests('POST', /^\/transcripts\/resume$/)).toHaveLength(1)
    })
    expect(requests('POST', /^\/transcripts\/pause$/)).toHaveLength(0)
  })

  it('AC-55.3 processor chip is live while Processing and attached-hidden when Idle; rate chip mirrors the card', async () => {
    await renderPage()
    const live = within(header()).getByTestId('processor-indicator')
    expect(live.hidden).toBe(false)
    expect(live.textContent).toContain('Processing')
    const rate = within(header()).getByTestId('transcript-rate-chip')
    const bravo = card('Bravo')
    expect(rate.textContent).toContain(within(bravo).getByTestId('rate-display').textContent ?? '<none>')
    expect(rate.textContent).toContain('160s')
    await user.click(within(toolbar()).getByTestId('pause-btn'))
    await vi.waitFor(() => {
      expect(requests('POST', /^\/transcripts\/pause$/)).toHaveLength(1)
    })
    cleanup()
    processorState = 'Idle'
    queryClient.clear()
    await renderPage()
    const idle = within(header()).getByTestId('processor-indicator')
    expect(idle.hidden).toBe(true)
    expect(within(header()).queryByTestId('transcript-rate-chip')).toBeNull()
    const pause = within(toolbar()).getByTestId('pause-btn') as HTMLButtonElement
    expect(pause.disabled).toBe(true)
    await user.click(pause)
    expect(requests('POST', /^\/transcripts\/pause$/)).toHaveLength(1)
  })

  it('AC-55.4 channel rows render through QueueCard with single-select and no checkbox or drag handle', async () => {
    await renderPage()
    const cards = within(host).getAllByTestId('channel-card')
    expect(cards.map((node) => node.getAttribute('data-job-id'))).toEqual(['a', 'b', 'c', 'd', 'e'])
    const list = within(host).getByTestId('queue-list')
    expect(within(list).queryAllByRole('checkbox')).toHaveLength(0)
    expect(within(list).queryAllByTestId('queue-card-drag-handle')).toHaveLength(0)
    const charlieRegion = within(card('Charlie')).getByRole('button', { name: 'Select channel Charlie' })
    await user.click(charlieRegion)
    expect(card('Charlie').className).toContain('border-accent/50')
    await user.click(within(card('Alpha')).getByRole('button', { name: 'Select channel Alpha' }))
    expect(card('Alpha').className).toContain('border-accent/50')
    expect(card('Charlie').className).not.toContain('border-accent/50')
    expect(within(card('Alpha')).getByText('Done')).toBeTruthy()
    expect(pageSource).not.toMatch(/width\s*:/)
    expect(pageSource).not.toMatch(/STATUS_COLORS/)
    expect(pageSource).not.toMatch(/function ChannelCard/)
  })

  it('AC-55.4 card lines follow CARD_LINE_RULE', async () => {
    await renderPage()
    const alpha = card('Alpha')
    expect(alpha.textContent).toContain('4 / 4 transcripts · 900 words')
    const alphaBar = within(alpha).getByTestId('channel-progress')
    expect(alphaBar.getAttribute('role')).toBe('progressbar')
    expect((alphaBar.querySelector('[data-progress-fill]') as HTMLElement).className).toContain('bg-accent-green')
    expect(within(alpha).queryByTestId('rate-display')).toBeNull()
    expect(within(alpha).queryByTestId('last-title')).toBeNull()
    const tree = within(alpha).getByTestId('output-tree')
    expect(tree.textContent).toContain('C:/t/Alpha · raw · compiled')
    expect(tree.textContent).toContain('C:/t/Alpha/raw')
    expect(tree.textContent).toContain('C:/t/Alpha/compiled')
    const bravo = card('Bravo')
    expect(within(bravo).getByTestId('rate-display').textContent).toBe('1 req/20s')
    expect(within(bravo).getByTestId('eta-display').textContent).toBe('ETA 160s')
    expect(within(bravo).getByTestId('last-title').textContent).toBe('Last: Episode 3 Done')
    expect(within(bravo).queryByTestId('output-tree')).toBeNull()
    expect(within(card('Charlie')).queryByTestId('channel-progress')).toBeNull()
    expect(within(card('Echo')).queryByTestId('channel-progress')).toBeNull()
    expect(within(card('Delta')).getByTestId('channel-progress')).toBeTruthy()
  })

  it('AC-55.5 menus list only available actions in TRANSCRIPT_MENU_ORDER and opening selects the card', async () => {
    await renderPage()
    const expected: Record<string, string[]> = {
      Alpha: ['compile-btn', 'view-compiled-btn', 'open-zip-btn', 'open-folder-btn', 'remove-btn'],
      Bravo: ['compile-btn', 'open-folder-btn', 'remove-btn'],
      Charlie: ['retry-btn', 'compile-btn', 'open-folder-btn', 'remove-btn'],
      Delta: ['requeue-btn', 'open-folder-btn', 'remove-btn'],
      Echo: ['open-folder-btn', 'remove-btn'],
    }
    for (const [name, ids] of Object.entries(expected)) {
      const menu = await openMenu(name)
      expect(card(name).className, `${name} selected on menu open`).toContain('border-accent/50')
      expect(
        within(menu).getAllByRole('menuitem').map((node) => node.getAttribute('data-testid')),
        name,
      ).toEqual(ids)
      await user.keyboard('{Escape}')
    }
  })

  it('AC-55.5 status links render only when available and never share a menu id', async () => {
    await renderPage()
    const links: Record<string, string[]> = {
      Alpha: ['view-compiled-link', 'open-zip-link'],
      Bravo: ['open-folder-link'],
      Charlie: ['retry-link'],
      Delta: ['requeue-link'],
      Echo: [],
    }
    for (const [name, ids] of Object.entries(links)) {
      const found = Array.from(card(name).querySelectorAll('[data-testid$="-link"]')).map((node) =>
        node.getAttribute('data-testid'),
      )
      expect(found, name).toEqual(ids)
    }
    await user.click(within(card('Alpha')).getByTestId('open-zip-link'))
    await vi.waitFor(() => {
      expect(opened).toEqual(['C:/t/Alpha.zip'])
    })
    await user.click(within(card('Charlie')).getByTestId('retry-link'))
    await vi.waitFor(() => {
      expect(requests('POST', /^\/transcripts\/c\/retry$/)).toHaveLength(1)
    })
    expect(card('Charlie').className).toContain('border-accent/50')
  })

  it('AC-55.5 per-card commands target their own card', async () => {
    await renderPage()
    await user.click(within(card('Alpha')).getByRole('button', { name: 'Select channel Alpha' }))
    const menu = await openMenu('Charlie')
    await user.click(within(menu).getByTestId('compile-btn'))
    await vi.waitFor(() => {
      expect(requests('POST', /^\/transcripts\/c\/compile$/)).toHaveLength(1)
    })
    expect(requests('POST', /^\/transcripts\/a\/compile$/)).toHaveLength(0)
    const alphaMenu = await openMenu('Alpha')
    await user.click(within(alphaMenu).getByTestId('view-compiled-btn'))
    await vi.waitFor(() => {
      expect(opened).toContain('C:/t/Alpha/compiled/all.txt')
    })
  })

  it('AC-55.5 remove from a card menu confirms and deletes that card only', async () => {
    await renderPage()
    await user.click(within(card('Alpha')).getByRole('button', { name: 'Select channel Alpha' }))
    const menu = await openMenu('Delta')
    await user.click(within(menu).getByTestId('remove-btn'))
    const confirm = document.body.querySelector('[data-testid="remove-confirm-btn"]') as HTMLElement
    expect(confirm).not.toBeNull()
    expect(fetches.filter((row) => row.method === 'DELETE')).toHaveLength(0)
    await user.click(confirm)
    await vi.waitFor(() => {
      expect(requests('DELETE', /^\/transcripts\/d$/)).toHaveLength(1)
    })
    expect(fetches.filter((row) => row.method === 'DELETE')).toHaveLength(1)
  })

  it('AC-55.5 ▲ ▼ are disabled at the ends and reorder their own card with the full permutation', async () => {
    await renderPage()
    const first = within(card('Alpha')).getByTestId('up-btn') as HTMLButtonElement
    const last = within(card('Echo')).getByTestId('down-btn') as HTMLButtonElement
    expect(first.disabled).toBe(true)
    expect(last.disabled).toBe(true)
    expect(first.getAttribute('aria-label')).toBe('Move Alpha up')
    await user.click(within(card('Alpha')).getByRole('button', { name: 'Select channel Alpha' }))
    await user.click(within(card('Charlie')).getByTestId('up-btn'))
    await vi.waitFor(() => {
      expect(requests('PUT', /^\/transcripts\/reorder$/)).toHaveLength(1)
    })
    expect(requests('PUT', /^\/transcripts\/reorder$/)[0].body).toEqual({ job_ids: ['a', 'c', 'b', 'd', 'e'] })
    await vi.waitFor(() => {
      expect(within(host).getAllByTestId('channel-card').map((node) => node.getAttribute('data-job-id'))).toEqual([
        'a', 'c', 'b', 'd', 'e',
      ])
    })
    expect(card('Charlie').className).toContain('border-accent/50')
  })

  it('AC-55.5 focus returns to the moved card after the reorder lands (RULE-1, RULE-3)', async () => {
    await renderPage()
    let release: () => void = () => undefined
    holdReorder = new Promise<void>((done) => {
      release = done
    })
    const up = within(card('Bravo')).getByTestId('up-btn')
    await user.click(up)
    expect(document.activeElement).toBe(up)
    // RULE-3: prove the fallback precondition — focus is genuinely lost before the order lands.
    // Setup: jsdom ignores blur() on the now-disabled button (a browser drops its
    // focus on its own), so park focus on an enabled field and blur that instead.
    const parking = within(host).getByTestId('channel-input')
    parking.focus()
    parking.blur()
    expect(document.activeElement).toBe(document.body)
    await act(async () => {
      release()
      await Promise.resolve()
    })
    await vi.waitFor(() => {
      expect(within(host).getAllByTestId('channel-card')[0].getAttribute('data-job-id')).toBe('b')
    })
    // Bravo is now first, so its ▲ is disabled and focus falls back to its ▼.
    await vi.waitFor(() => {
      const moved = within(host).getByTestId('queue-list').querySelector('[data-job-id="b"]') as HTMLElement
      expect(document.activeElement).toBe(within(moved).getByTestId('down-btn'))
    })
  })

  it('AC-55.5 focus returns to the card after a rejected reorder too (RULE-1, RULE-3)', async () => {
    reorderStatus = 409
    await renderPage()
    let release: () => void = () => undefined
    holdReorder = new Promise<void>((done) => {
      release = done
    })
    await user.click(within(card('Bravo')).getByTestId('up-btn'))
    // RULE-3 precondition, as in the success case: focus is genuinely lost in flight.
    const parking = within(host).getByTestId('channel-input')
    parking.focus()
    parking.blur()
    expect(document.activeElement).toBe(document.body)
    await act(async () => {
      release()
      await Promise.resolve()
    })
    await vi.waitFor(() => {
      expect(within(host).getByTestId('error-banner').textContent).toMatch(/reorder rejected/)
    })
    expect(within(host).getAllByTestId('channel-card').map((node) => node.getAttribute('data-job-id'))).toEqual([
      'a', 'b', 'c', 'd', 'e',
    ])
    // The order did not change, so Bravo's ▲ is still available and takes focus back.
    await vi.waitFor(() => {
      const stayed = within(host).getByTestId('queue-list').querySelector('[data-job-id="b"]') as HTMLElement
      expect(document.activeElement).toBe(within(stayed).getByTestId('up-btn'))
    })
  })

  it('AC-55.5 per-card controls are unavailable while a command is in flight', async () => {
    processorState = 'Idle'
    let release: () => void = () => undefined
    holdStart = new Promise<void>((done) => {
      release = done
    })
    await renderPage()
    await user.click(within(toolbar()).getByTestId('start-btn'))
    await vi.waitFor(() => {
      expect((within(card('Charlie')).getByTestId('up-btn') as HTMLButtonElement).disabled).toBe(true)
    })
    const menu = await openMenu('Alpha')
    for (const node of within(menu).getAllByRole('menuitem')) {
      expect((node as HTMLButtonElement).disabled, node.getAttribute('data-testid') ?? '').toBe(true)
    }
    await act(async () => {
      release()
      await Promise.resolve()
    })
  })

  it('AC-55.6 Add row, status line and error surface', async () => {
    postStatus = 422
    await renderPage()
    const input = within(host).getByTestId('channel-input') as HTMLInputElement
    const add = within(host).getByTestId('add-btn')
    expect(input.getAttribute('aria-label')).toBe('Channel URL')
    expect(input.getAttribute('placeholder')).toBe('Channel URL')
    expect(input.parentElement).toBe(add.parentElement)
    expect(within(host).getByTestId('channel-url-hint').hidden).toBe(false)
    expect(within(host).getByTestId('error-banner').hidden).toBe(true)
    await user.click(add)
    expect(requests('POST', /^\/transcripts$/)).toHaveLength(0)
    await user.type(input, 'https://www.youtube.com/@bad')
    await user.click(add)
    await vi.waitFor(() => {
      expect(within(host).getByTestId('error-banner').textContent).toMatch(/bad channel/)
    })
    expect(within(host).getByTestId('error-banner').getAttribute('role')).toBe('alert')
    expect(within(host).getByTestId('channel-url-hint').hidden).toBe(true)
    expect(requests('POST', /^\/transcripts$/)[0].body).toEqual({ channel_url: 'https://www.youtube.com/@bad' })
  })

  it('rc.3 F3 Add shows its progress, then how many videos it queued', async () => {
    let release = (): void => undefined
    holdPost = new Promise<void>((resolve) => {
      release = resolve
    })
    await renderPage()
    expect(within(host).getByTestId('add-status').hidden).toBe(true)
    await user.type(within(host).getByTestId('channel-input'), 'https://www.youtube.com/@foxtrot')
    await user.click(within(host).getByTestId('add-btn'))
    const status = (): HTMLElement => within(host).getByTestId('add-status')
    expect(status().hidden).toBe(false)
    expect(status().textContent).toMatch(/^Adding — reading the channel's video list/)
    expect(status().getAttribute('role')).toBe('status')
    expect(within(host).getByTestId('channel-url-hint').hidden).toBe(true)
    await act(async () => {
      release()
    })
    await vi.waitFor(() => {
      expect(status().textContent).toBe('Queued 3 videos from Foxtrot. Click Start to fetch transcripts.')
    })
    expect(within(host).getByTestId('error-banner').hidden).toBe(true)
  })

  it('rc.3 F3 a failed Add clears the progress line and shows the error', async () => {
    postStatus = 422
    await renderPage()
    await user.type(within(host).getByTestId('channel-input'), 'https://www.youtube.com/@bad')
    await user.click(within(host).getByTestId('add-btn'))
    await vi.waitFor(() => {
      expect(within(host).getByTestId('error-banner').textContent).toMatch(/bad channel/)
    })
    expect(within(host).getByTestId('add-status').hidden).toBe(true)
  })

  it('AC-55.6 empty queue invites a link and the action only focuses the field', async () => {
    items = []
    processorState = 'Idle'
    await renderPage()
    const invite = within(host).getByTestId('transcript-empty-invite')
    expect(invite.textContent).toMatch(/Paste a channel link/)
    const before = fetches.filter((row) => row.method !== 'GET').length
    await user.click(within(invite).getByTestId('transcript-empty-invite-action'))
    expect(document.activeElement).toBe(within(host).getByTestId('channel-input'))
    expect(fetches.filter((row) => row.method !== 'GET')).toHaveLength(before)
  })

  it('AC-55.6 page keeps the content cap and QUEUE_SCROLL_CONTAINER_RULE chain', async () => {
    await renderPage()
    const root = within(host).getByTestId('transcript-page')
    expect(root.className).toContain('h-full')
    expect(root.className).toContain('min-h-0')
    const capped = within(host).getByTestId('channel-input').closest('[class*="max-w-[var(--layout-page-max-width)]"]')
    expect(capped).not.toBeNull()
    const list = within(host).getByTestId('queue-list')
    expect(list.className).not.toContain('overflow-auto')
    const scroller = list.parentElement as HTMLElement
    expect(scroller.className).toContain('overflow-auto')
    expect(scroller.className).toContain('min-h-0')
    const region = list.closest('[class*="min-h-[20rem]"]') as HTMLElement
    expect(region).not.toBeNull()
    expect(region.className).toContain('flex-1')
    expect(region.contains(header())).toBe(true)
    const controls = within(host).getByTestId('channel-input').closest('[class*="overflow-auto"]') as HTMLElement
    expect(controls).not.toBeNull()
    expect(controls.className).toContain('min-h-0')
    expect(controls.contains(list)).toBe(false)
  })

  it('AC-115.14 card line three shows the job message, or the last item message while Processing', async () => {
    const blocked =
      'YouTube is blocking caption requests from this network. Try again later or from another network, then Resume.'
    const failed = "2 of 4 videos failed. Last: Couldn't get captions: the video is age-restricted."
    const skipped = '1 of 1 videos had no transcript. Last: No captions for this video.'
    items = [
      item({ id: 'f', channel_name: 'Foxtrot', status: 'Failed', error_message: failed, queue_position: 1 }),
      item({ id: 'p', channel_name: 'Papa', status: 'Paused', error_message: blocked, queue_position: 2 }),
      item({ id: 's', channel_name: 'Sierra', status: 'Done', error_message: skipped, queue_position: 3 }),
      item({
        id: 't', channel_name: 'Tango', status: 'Processing', last_title: 'Episode 3', last_item_status: 'Skipped',
        last_item_message: 'No captions for this video.', queue_position: 4,
      }),
      item({
        id: 'u', channel_name: 'Uniform', status: 'Processing', last_item_status: 'Failed',
        last_item_message: "Couldn't get captions: the video is age-restricted.", queue_position: 5,
      }),
      item({ id: 'v', channel_name: 'Victor', status: 'Done', video_count: 2, transcripts_done: 2, queue_position: 6 }),
    ]
    await renderPage()
    for (const [name, message] of [['Foxtrot', failed], ['Papa', blocked], ['Sierra', skipped]]) {
      const found = card(name)
      expect(within(found).queryByTestId('job-message')?.textContent, name).toBe(message)
      expect(within(found).queryByTestId('output-tree'), name).toBeNull()
      expect(within(found).queryByTestId('last-title'), name).toBeNull()
    }
    expect(within(card('Tango')).queryByTestId('last-title')?.textContent).toBe(
      'Last: Episode 3 Skipped · No captions for this video.',
    )
    expect(within(card('Uniform')).queryByTestId('last-title')?.textContent).toBe(
      "Last: Failed · Couldn't get captions: the video is age-restricted.",
    )
    for (const name of ['Tango', 'Uniform', 'Victor']) {
      expect(within(card(name)).queryByTestId('job-message'), name).toBeNull()
    }
    const victor = card('Victor')
    expect(within(victor).queryByTestId('output-tree')?.textContent).toContain('C:/t/Victor · raw · compiled')
    expect(within(victor).queryByTestId('last-title')).toBeNull()
  })

  it('rc.3 F6 a Processing card shows its retry message on line three until the job clears it', async () => {
    const waiting =
      'YouTube is blocking caption requests from this network. Attempt 1 of 3 was refused; trying again in 30 s.'
    items = [
      item({
        id: 'r', channel_name: 'Romeo', status: 'Processing', error_message: waiting, last_title: 'Episode 1',
        last_item_status: 'Done', queue_position: 1,
      }),
      item({
        id: 'q', channel_name: 'Quebec', status: 'Processing', last_title: 'Episode 2', last_item_status: 'Done',
        queue_position: 2,
      }),
    ]
    await renderPage()
    const romeo = card('Romeo')
    expect(within(romeo).queryByTestId('job-message')?.textContent).toBe(waiting)
    expect(within(romeo).queryByTestId('last-title')).toBeNull()
    const quebec = card('Quebec')
    expect(within(quebec).queryByTestId('job-message')).toBeNull()
    expect(within(quebec).queryByTestId('last-title')?.textContent).toBe('Last: Episode 2 Done')
  })
})
