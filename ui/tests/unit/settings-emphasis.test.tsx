/** @vitest-environment jsdom */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { SettingsPage } from '../../src/renderer/src/features/settings/SettingsPage'

/**
 * MEU-70 EMPHASIS_TESTS (Session 31): ACTIVE_SOURCE and SECTION_EMPHASIS, defined once in
 * docs/execution/plans/2026-10-10-gui-polish-residuals/implementation-plan.md. This suite imports
 * only modules that exist before row 7, so its row 5 Red is an assertion failure (D-21); the
 * SECTION_FRAME_BASE owner (row 7) is loaded at run time and checked as an assertion.
 */

type LoginItem = Awaited<ReturnType<NonNullable<Window['api']['loginItemGet']>>>

const UNSUPPORTED: LoginItem = { supported: false, reason: 'not-packaged', enabled: false, minimized: false }
const SUPPORTED: LoginItem = { supported: true, enabled: false, minimized: false, startMinimizedSupported: true }

/** The state-dependent tokens; everything else on a frame is the shared base. */
const CURRENT_TOKENS = ['bg-bg-elevated/40', 'border-accent']
const IDLE_TOKENS = ['border-transparent']

function mockApi(loginItem: LoginItem): void {
  window.api = {
    getBackendUrl: async () => 'http://127.0.0.1:51234/api/v1',
    getToken: async () => 'gui-nonce',
    logStartupMetric: () => undefined,
    showDirectoryDialog: async () => 'C:/e2e/outdir',
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
    loginItemGet: async () => loginItem,
    loginItemSet: async () => loginItem,
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

async function settle(): Promise<void> {
  await act(async () => {
    await new Promise((resolve) => setTimeout(resolve, 0))
  })
}

async function renderPage(): Promise<void> {
  render(createElement(QueryClientProvider, { client }, createElement(SettingsPage)))
  await vi.waitFor(() => {
    expect(screen.getByTestId('settings-page')).toBeTruthy()
  })
  await settle()
}

function tokens(element: Element): string[] {
  return element.className.split(/\s+/).filter((token) => token.length > 0)
}

function frames(): HTMLElement[] {
  return Array.from(document.querySelectorAll<HTMLElement>('[data-settings-section]'))
}

function frameFor(key: string): HTMLElement {
  const frame = document.querySelector<HTMLElement>(`[data-settings-section="${key}"]`)
  if (frame === null) throw new Error(`no frame ${key}`)
  return frame
}

/** The base tokens of a frame: its class tokens minus the state-dependent ones. */
function baseTokens(element: Element): string[] {
  return tokens(element)
    .filter((token) => !CURRENT_TOKENS.includes(token) && !IDLE_TOKENS.includes(token))
    .sort()
}

/** ACTIVE_SOURCE: exactly one data-current section, and it is the rail's aria-current entry. */
function expectSingleCurrent(step: string): string {
  const current = document.querySelectorAll('[data-current="true"]')
  expect(current, `${step}: data-current sections`).toHaveLength(1)
  const key = current[0]?.getAttribute('data-settings-section') ?? ''
  const rail = document.querySelectorAll('[aria-current="location"]')
  expect(rail, `${step}: aria-current entries`).toHaveLength(1)
  expect(rail[0]?.getAttribute('data-testid'), `${step}: rail matches section`).toBe(`settings-rail-${key}`)
  return key
}

/** SECTION_EMPHASIS state tokens on every frame. */
function expectEmphasis(step: string, currentKey: string): void {
  for (const frame of frames()) {
    const key = frame.getAttribute('data-settings-section') ?? ''
    const list = tokens(frame)
    expect(frame.hasAttribute('aria-current'), `${step}: ${key} aria-current`).toBe(false)
    expect(list.some((token) => token.includes('transition-all')), `${step}: ${key} transition-all`).toBe(false)
    expect(frame.className, `${step}: ${key} raw hex`).not.toMatch(/#[0-9a-fA-F]{3,8}/)
    expect(list.some((token) => /^-m[tby]-/.test(token)), `${step}: ${key} negative vertical margin`).toBe(false)
    if (key === currentKey) {
      expect(frame.getAttribute('data-current'), `${step}: ${key}`).toBe('true')
      for (const token of CURRENT_TOKENS) expect(list, `${step}: ${key}`).toContain(token)
      for (const token of IDLE_TOKENS) expect(list, `${step}: ${key}`).not.toContain(token)
    } else {
      expect(frame.hasAttribute('data-current'), `${step}: ${key}`).toBe(false)
      for (const token of IDLE_TOKENS) expect(list, `${step}: ${key}`).toContain(token)
      for (const token of CURRENT_TOKENS) expect(list, `${step}: ${key}`).not.toContain(token)
    }
  }
}

/** Load SECTION_FRAME_BASE from its row-7 owner at run time (an absent module is an assertion failure). */
async function frameBase(): Promise<string[]> {
  const owner = '../../src/renderer/src/features/settings/settings-section-frame'
  const module = (await import(/* @vite-ignore */ owner).catch(() => null)) as { SECTION_FRAME_BASE?: string } | null
  expect(module, 'settings-section-frame.ts exports SECTION_FRAME_BASE').not.toBeNull()
  const base = (module?.SECTION_FRAME_BASE ?? '').split(/\s+/).filter((token) => token.length > 0)
  for (const token of ['scroll-mt-4', 'border-l-2', '-mx-3', 'pl-2.5', 'pr-3', 'py-2']) {
    expect(base, 'SECTION_FRAME_BASE').toContain(token)
  }
  return base.sort()
}

beforeEach(() => {
  client = new QueryClient({ defaultOptions: { queries: { retry: false, gcTime: 0 } } })
  user = userEvent.setup()
  installFetch()
})

afterEach(() => {
  cleanup()
  client.clear()
  vi.unstubAllGlobals()
})

describe('MEU-70 current-section emphasis (ACTIVE_SOURCE, SECTION_EMPHASIS)', () => {
  it('AC-70.5 one current section, equal to the rail entry, across render, click, keyboard and observer', async () => {
    const observers: Array<{ callback: IntersectionObserverCallback; targets: Element[] }> = []
    class FakeObserver {
      record: { callback: IntersectionObserverCallback; targets: Element[] }
      constructor(callback: IntersectionObserverCallback) {
        this.record = { callback, targets: [] }
        observers.push(this.record)
      }
      observe(target: Element): void {
        this.record.targets.push(target)
      }
      unobserve(): void {}
      disconnect(): void {}
      takeRecords(): IntersectionObserverEntry[] {
        return []
      }
    }
    vi.stubGlobal('IntersectionObserver', FakeObserver)
    mockApi(UNSUPPORTED)
    await renderPage()
    expect(expectSingleCurrent('initial')).toBe('download')
    expectEmphasis('initial', 'download')

    await user.click(screen.getByTestId('settings-rail-capture'))
    await settle()
    expect(expectSingleCurrent('click')).toBe('capture')
    expectEmphasis('click', 'capture')

    screen.getByTestId('settings-rail-transcript').focus()
    await user.keyboard('{Enter}')
    await settle()
    expect(expectSingleCurrent('keyboard')).toBe('transcript')
    expectEmphasis('keyboard', 'transcript')

    // An observer crossing after the click locks expire (A-6: at most 3 s, or 800 ms with no scroll).
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 900))
    })
    const live = observers.at(-1)
    const mcp = screen.getByTestId('mcp-access-card')
    await act(async () => {
      live?.callback(
        live.targets.map((target) => ({ target, isIntersecting: target === mcp }) as unknown as IntersectionObserverEntry),
        {} as IntersectionObserver,
      )
    })
    await settle()
    expect(expectSingleCurrent('observer')).toBe('mcp')
    expectEmphasis('observer', 'mcp')
  })

  it('AC-70.5 every frame carries the shared SECTION_FRAME_BASE', async () => {
    mockApi(UNSUPPORTED)
    await renderPage()
    const base = await frameBase()
    for (const frame of frames()) {
      expect(baseTokens(frame), frame.getAttribute('data-settings-section') ?? '').toEqual(base)
    }
  })

  it('AC-70.9 the supported Startup section gets the same emphasis and reserved geometry', async () => {
    mockApi(SUPPORTED)
    await renderPage()
    await vi.waitFor(() => {
      expect(screen.getByTestId('settings-rail-startup')).toBeTruthy()
    })
    const startup = screen.getByTestId('start-at-sign-in-panel')

    await user.click(screen.getByTestId('settings-rail-startup'))
    await settle()
    expect(expectSingleCurrent('startup current')).toBe('startup')
    expectEmphasis('startup current', 'startup')
    const startupCurrentTokens = tokens(startup).sort()

    await user.click(screen.getByTestId('settings-rail-appearance'))
    await settle()
    expect(expectSingleCurrent('appearance current')).toBe('appearance')
    expectEmphasis('appearance current', 'appearance')
    // The same state renders the same tokens on Startup as on a page frame.
    expect(tokens(frameFor('appearance')).sort()).toEqual(startupCurrentTokens)
    expect(startup.hasAttribute('data-current')).toBe(false)
    expect(tokens(startup).sort()).toEqual(tokens(frameFor('download')).sort())
    expect(baseTokens(startup)).toEqual(await frameBase())
  })
})
