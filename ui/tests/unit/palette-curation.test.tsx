/** @vitest-environment jsdom */

import { existsSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { QueryClient } from '@tanstack/react-query'
import { act, render, screen, within } from '@testing-library/react'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import * as paletteModule from '../../src/renderer/src/components/CommandPalette'
import * as convertCommands from '../../src/renderer/src/features/converter/convert-commands'
import * as downloadCommands from '../../src/renderer/src/features/downloader/download-commands'
import { SETTINGS_EVENTS } from '../../src/renderer/src/features/settings/settings-commands'
import { SETTINGS_NAMESPACE_PATHS } from '../../src/renderer/src/features/settings/settings-paths'
import * as ttsCommands from '../../src/renderer/src/features/tts/tts-commands'
import { RENDERER_LOG_EVENT, type RendererLogDetail } from '../../src/renderer/src/lib/renderer-log'
import { navigateShell } from '../../src/renderer/src/lib/shell-nav'
import { getCommand, listCommands, type CommandRegistryEntry } from '../../src/renderer/src/registry/commandRegistry'
import * as shortcuts from '../../src/renderer/src/registry/shortcuts'

import type * as CommandStateModule from '../../src/renderer/src/registry/command-state'
import type * as AppearanceModule from '../../src/renderer/src/registry/appearance'

/*
  MEU-96 PALETTE_LIST, COMMAND_STATE, APPEARANCE, CONFIRM_ROUTE (commands),
  LABELS and CHECK_DEPS_ROUTE. The two new registry modules are loaded by a
  variable specifier after an existence check, so their absence fails one
  assertion per test instead of the whole file.
*/

// The real putSettingsNamespace is kept for AC-96.6's first half; the mock wraps it.
const probe = vi.hoisted(() => ({ realPut: undefined as unknown }))
vi.mock('../../src/renderer/src/features/settings/useSettingsPage', async (importOriginal) => {
  const actual = await importOriginal<Record<string, unknown>>()
  probe.realPut = actual.putSettingsNamespace
  return { ...actual, putSettingsNamespace: vi.fn(async () => undefined) }
})

const here = dirname(fileURLToPath(import.meta.url))
const REGISTRY_DIR = resolve(here, '../../src/renderer/src/registry')
const COMMAND_STATE_PATH = resolve(REGISTRY_DIR, 'command-state.ts')
const APPEARANCE_PATH = resolve(REGISTRY_DIR, 'appearance.ts')
const REGISTRY_SOURCE = resolve(REGISTRY_DIR, 'commandRegistry.ts')
const TTS_COMMANDS_SOURCE = resolve(here, '../../src/renderer/src/features/tts/tts-commands.ts')
const COMMAND_STATE_SPECIFIER = '../../src/renderer/src/registry/command-state'
const APPEARANCE_SPECIFIER = '../../src/renderer/src/registry/appearance'
const SETTINGS_PAGE_SPECIFIER = '../../src/renderer/src/features/settings/useSettingsPage'

type ShellPage = '/' | '/transcript' | '/tts' | '/convert' | '/capture' | '/settings'
type State = Partial<Record<string, boolean>>
type PaletteCommands = (commands: CommandRegistryEntry[], page: ShellPage | null, state: State) => CommandRegistryEntry[]

const PAGES: ShellPage[] = ['/', '/transcript', '/tts', '/convert', '/capture', '/settings']

const GLOBAL_IDS = [
  'nav:downloader',
  'nav:transcript',
  'nav:tts',
  'nav:convert',
  'nav:capture',
  'nav:settings',
  'nav:collapse',
  'console:toggle',
  'help:toggle',
  'appearance:dark',
  'appearance:light',
  'settings:check_deps',
]

const ENTRY_IDS: Record<ShellPage, string[]> = {
  '/': ['download:add', 'download:sabr_check'],
  '/transcript': ['transcript:add'],
  '/tts': [],
  '/convert': ['convert:add', 'convert:browse'],
  '/capture': ['capture:region', 'capture:open_folder'],
  '/settings': [],
}

const STATEFUL_IDS = [
  'download:start',
  'download:pause',
  'download:resume',
  'download:cancel',
  'download:clear',
  'transcript:start',
  'transcript:pause',
  'transcript:resume',
  'transcript:stop',
  'convert:start',
  'convert:pause',
  'convert:resume',
  'convert:cancel',
  'convert:clear',
  'tts:prepare',
  'tts:generate',
  'capture:save',
]

async function loadCommandState(): Promise<typeof CommandStateModule> {
  expect(existsSync(COMMAND_STATE_PATH), 'registry/command-state.ts exists').toBe(true)
  return (await import(/* @vite-ignore */ COMMAND_STATE_SPECIFIER)) as typeof CommandStateModule
}

async function loadAppearance(): Promise<typeof AppearanceModule> {
  expect(existsSync(APPEARANCE_PATH), 'registry/appearance.ts exists').toBe(true)
  return (await import(/* @vite-ignore */ APPEARANCE_SPECIFIER)) as typeof AppearanceModule
}

function paletteCommands(): PaletteCommands {
  const fn = (shortcuts as unknown as Record<string, unknown>).paletteCommands
  expect(typeof fn, 'shortcuts.paletteCommands').toBe('function')
  return fn as PaletteCommands
}

function ids(list: CommandRegistryEntry[]): string[] {
  return list.map((entry) => entry.id)
}

function fixture(id: string, extra: Partial<Omit<CommandRegistryEntry, 'id'>> = {}): CommandRegistryEntry {
  return {
    id,
    label: id,
    category: 'navigation',
    keywords: [],
    action: () => undefined,
    ...extra,
  } as unknown as CommandRegistryEntry
}

/** Animation frames are queued and run by hand, so "after two frames" is exact. */
let frames: FrameRequestCallback[] = []

function flushFrame(): void {
  const run = frames
  frames = []
  for (const callback of run) {
    callback(0)
  }
}

const fetchMock = vi.fn(
  async (_input: RequestInfo | URL, _init?: RequestInit) =>
    new Response('{}', { status: 200, headers: { 'Content-Type': 'application/json' } }),
)

beforeEach(() => {
  frames = []
  window.location.hash = '#/'
  vi.spyOn(window, 'requestAnimationFrame').mockImplementation((callback) => {
    frames.push(callback)
    return frames.length
  })
  fetchMock.mockClear()
  vi.stubGlobal('fetch', fetchMock)
  Object.defineProperty(window, 'api', {
    configurable: true,
    value: {
      getBackendUrl: vi.fn(async () => 'http://127.0.0.1:51234/api/v1'),
      getToken: vi.fn(async () => 'unit-nonce'),
    },
  })
})

afterEach(() => {
  document.body.innerHTML = ''
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})

describe('MEU-96 PALETTE_LIST', () => {
  it('AC-96.1 paletteCommands filters by palette, page and state, folds resume and orders the page first', () => {
    const list = paletteCommands()
    const commands = [
      fixture('g:one'),
      fixture('g:hidden', { palette: false }),
      fixture('c:add', { page: '/convert' }),
      fixture('d:add', { page: '/' }),
      fixture('c:start', { page: '/convert', stateful: true }),
      fixture('x:pause', { page: '/convert', stateful: true }),
      fixture('x:resume', { page: '/convert', stateful: true }),
      fixture('g:two'),
    ]
    const all = { 'c:start': true, 'x:pause': true, 'x:resume': true }

    for (const page of [...PAGES, null]) {
      expect(ids(list(commands, page, all))).not.toContain('g:hidden')
    }
    expect(ids(list(commands, '/convert', all))).toEqual(['c:add', 'c:start', 'x:pause', 'g:one', 'g:two'])
    expect(ids(list(commands, '/convert', { 'c:start': false }))).not.toContain('c:start')
    expect(ids(list(commands, '/convert', {}))).not.toContain('c:start')
    expect(ids(list(commands, '/', all))).toEqual(['d:add', 'g:one', 'g:two'])
    expect(ids(list(commands, '/convert', { 'x:resume': true }))).toContain('x:resume')
    expect(ids(list(commands, null, all))).toEqual(['g:one', 'g:two'])
  })

  it('AC-96.2 the real registry lists globals and the page entry commands, never stateful or foreign ones', () => {
    const list = paletteCommands()
    const registry = listCommands()
    for (const page of PAGES) {
      const listed = ids(list(registry, page, {}))
      for (const id of GLOBAL_IDS) {
        expect(listed, page + ' lists ' + id).toContain(id)
      }
      const own = ENTRY_IDS[page]
      expect([...listed.slice(0, own.length)].sort(), page + ' begins with its entry commands').toEqual([...own].sort())
      for (const id of STATEFUL_IDS) {
        expect(listed, page + ' hides stateful ' + id).not.toContain(id)
      }
      for (const other of PAGES.filter((p) => p !== page)) {
        for (const id of ENTRY_IDS[other]) {
          expect(listed, page + ' hides ' + other + ' entry ' + id).not.toContain(id)
        }
      }
    }
    const settings = ids(list(registry, '/settings', {}))
    for (const id of ['download:add', 'convert:browse', 'capture:region']) {
      expect(settings).not.toContain(id)
    }

    const base = ids(list(registry, '/', {}))
    const enabled = ids(list(registry, '/', { 'download:start': true, 'download:clear': true }))
    expect(enabled.filter((id) => !base.includes(id)).sort()).toEqual(['download:clear', 'download:start'])

    const everything = Object.fromEntries(registry.map((entry) => [entry.id, true]))
    for (const page of [...PAGES, null]) {
      expect(ids(list(registry, page, everything))).not.toContain('page:primary')
    }
  })
})

describe('MEU-96 COMMAND_STATE', () => {
  it('AC-96.3 publish, get, subscribe and clear; an identical publish is silent; the hook clears on unmount', async () => {
    const state = await loadCommandState()
    for (const name of [
      'publishCommandState',
      'clearCommandState',
      'getCommandState',
      'subscribeCommandState',
      'usePublishCommandState',
      'useCommandState',
    ]) {
      expect(typeof (state as unknown as Record<string, unknown>)[name], name).toBe('function')
    }

    const empty = state.getCommandState('/capture')
    expect(empty).toEqual({})
    expect(Object.isFrozen(empty)).toBe(true)
    expect(state.getCommandState('/capture')).toBe(empty)

    const listener = vi.fn()
    const unsubscribe = state.subscribeCommandState(listener)
    state.publishCommandState('/convert', { 'convert:start': true })
    expect(listener).toHaveBeenCalledTimes(1)
    const first = state.getCommandState('/convert')
    expect(first).toEqual({ 'convert:start': true })
    expect(state.getCommandState('/convert')).toBe(first)

    state.publishCommandState('/convert', { 'convert:start': true })
    expect(listener, 'an identical publish fires no listener').toHaveBeenCalledTimes(1)
    expect(state.getCommandState('/convert')).toBe(first)

    state.publishCommandState('/convert', { 'convert:start': false })
    expect(listener).toHaveBeenCalledTimes(2)
    expect(state.getCommandState('/convert')).toEqual({ 'convert:start': false })

    state.clearCommandState('/convert')
    expect(state.getCommandState('/convert')).toEqual({})
    unsubscribe()
    const settled = listener.mock.calls.length
    state.publishCommandState('/convert', { 'convert:start': true })
    expect(listener, 'no call after unsubscribe').toHaveBeenCalledTimes(settled)
    state.clearCommandState('/convert')

    function Publisher({ text }: { text: string }) {
      state.usePublishCommandState('/tts', { 'tts:prepare': text.length > 0 })
      return null
    }
    const view = render(createElement(Publisher, { text: 'hello' }))
    expect(state.getCommandState('/tts')).toEqual({ 'tts:prepare': true })
    view.rerender(createElement(Publisher, { text: '' }))
    expect(state.getCommandState('/tts')).toEqual({ 'tts:prepare': false })
    view.unmount()
    expect(state.getCommandState('/tts')).toEqual({})
  })

  it('AC-96.4 an open palette recomputes on navigation and on a state publish', async () => {
    window.location.hash = '#/'
    render(createElement(paletteModule.CommandPalette, { open: true, onClose: () => undefined }))
    const palette = screen.getByTestId('command-palette')
    const firstGroup = (): string | null | undefined => palette.querySelector('div.uppercase')?.textContent

    expect(firstGroup()).toBe('Download')
    await act(async () => {
      navigateShell('/convert')
    })
    expect(firstGroup()).toBe('Convert')
    expect(screen.getByTestId('command-palette'), 'no remount').toBe(palette)

    const state = await loadCommandState()
    expect(within(palette).queryByRole('button', { name: /Start conversions/ })).toBeNull()
    await act(async () => {
      state.publishCommandState('/convert', { 'convert:start': true })
    })
    expect(within(palette).queryByRole('button', { name: /Start conversions/ })).not.toBeNull()
    expect(screen.getByTestId('command-palette')).toBe(palette)
    await act(async () => {
      state.clearCommandState('/convert')
    })

    const labels = (paletteModule as unknown as Record<string, unknown>).CATEGORY_LABELS as
      | Record<string, string>
      | undefined
    expect(labels?.appearance).toBe('Appearance')
  })
})

describe('MEU-96 APPEARANCE', () => {
  it('AC-96.6 putSettingsNamespace sets the theme; the Appearance commands go through it and log a failure', async () => {
    expect(typeof probe.realPut, 'useSettingsPage exports putSettingsNamespace').toBe('function')
    const realPut = probe.realPut as (
      client: QueryClient,
      namespace: string,
      patch: Record<string, unknown>,
    ) => Promise<void>

    fetchMock.mockImplementation(async (_input, init) =>
      new Response(typeof init?.body === 'string' ? init.body : '{}', {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    )
    document.documentElement.classList.add('dark')
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    const invalidate = vi.spyOn(client, 'invalidateQueries')
    await realPut(client, 'ui', { theme: 'light' })
    const puts = fetchMock.mock.calls.filter(([, init]) => init?.method === 'PUT')
    expect(puts).toHaveLength(1)
    const [url, init] = puts[0] ?? []
    expect(new URL(String(url)).pathname.endsWith(SETTINGS_NAMESPACE_PATHS.ui)).toBe(true)
    expect(JSON.parse(String(init?.body))).toEqual({ theme: 'light' })
    expect(document.documentElement.classList.contains('dark')).toBe(false)
    expect(invalidate).toHaveBeenCalledWith({ queryKey: ['settings', 'ui'] })

    const settingsPage = (await import(/* @vite-ignore */ SETTINGS_PAGE_SPECIFIER)) as Record<string, unknown>
    const put = vi.mocked(settingsPage.putSettingsNamespace as (...args: unknown[]) => Promise<void>)
    put.mockClear()
    const dark = getCommand('appearance:dark')
    expect(dark?.label).toBe('Appearance: Dark')
    dark?.action()
    await vi.waitFor(() => {
      expect(put).toHaveBeenCalledTimes(1)
    })
    expect(put.mock.calls[0]?.[1]).toBe('ui')
    expect(put.mock.calls[0]?.[2]).toEqual({ theme: 'dark' })

    const { setAppearance } = await loadAppearance()
    const logged: string[] = []
    const onLog = (event: Event) => {
      logged.push((event as CustomEvent<RendererLogDetail>).detail.message)
    }
    window.addEventListener(RENDERER_LOG_EVENT, onLog)
    put.mockRejectedValueOnce(new Error('offline'))
    expect(() => {
      setAppearance('light')
    }).not.toThrow()
    await vi.waitFor(() => {
      expect(logged.filter((line) => line.startsWith('ERROR Appearance:'))).toHaveLength(1)
    })
    window.removeEventListener(RENDERER_LOG_EVENT, onLog)

    expect(readFileSync(REGISTRY_SOURCE, 'utf8')).not.toMatch(/apiFetch/)
    expect(getCommand('appearance:light')?.label).toBe('Appearance: Light')
    for (const [id, chord] of [
      ['appearance:dark', 'Ctrl+Shift+D'],
      ['appearance:light', 'Ctrl+Shift+L'],
    ]) {
      expect((getCommand(id) as { category?: string } | undefined)?.category, id).toBe('appearance')
      expect(getCommand(id)?.shortcut, id).toBe(chord)
    }
  })
})

describe('MEU-96 CONFIRM_ROUTE commands', () => {
  it('AC-96.7 palette clear and cancel request the page confirm after two frames and call no API', async () => {
    const downloadEvent = (downloadCommands as unknown as Record<string, unknown>).DOWNLOAD_CONFIRM_EVENT
    const convertEvent = (convertCommands as unknown as Record<string, unknown>).CONVERT_CONFIRM_EVENT
    expect(downloadEvent).toBe('av-kit:download:confirm')
    expect(convertEvent).toBe('av-kit:convert:confirm')

    const cases: Array<[string, string, () => void, string]> = [
      ['#/', String(downloadEvent), downloadCommands.DOWNLOAD_COMMANDS.clear, 'clear'],
      ['#/', String(downloadEvent), downloadCommands.DOWNLOAD_COMMANDS.cancel, 'cancel'],
      ['#/convert', String(convertEvent), convertCommands.CONVERT_COMMANDS.clear, 'clear'],
      ['#/convert', String(convertEvent), convertCommands.CONVERT_COMMANDS.cancel, 'cancel'],
    ]
    for (const [hash, name, run, kind] of cases) {
      window.location.hash = hash
      const seen: unknown[] = []
      const onConfirm = (event: Event) => {
        seen.push((event as CustomEvent<unknown>).detail)
      }
      window.addEventListener(name, onConfirm)
      run()
      flushFrame()
      expect(seen, name + ' ' + kind + ' waits two frames').toHaveLength(0)
      flushFrame()
      expect(seen, name + ' ' + kind).toEqual([{ kind }])
      window.removeEventListener(name, onConfirm)
    }
    await act(async () => {
      await Promise.resolve()
    })
    expect(fetchMock).not.toHaveBeenCalled()
  })
})

describe('MEU-96 LABELS', () => {
  it('AC-96.8 renamed labels; TTS palette delivery only clicks an enabled page button', async () => {
    expect(getCommand('download:sabr_check')?.label).toBe('Check YouTube quality limit')
    expect(getCommand('download:sabr_check')?.keywords).toContain('sabr')
    expect(getCommand('tts:prepare')?.label).toBe('Preview cleaned text')
    expect(getCommand('download:add')?.label).toBe('Enter download URL')
    expect(getCommand('transcript:add')?.label).toBe('Enter transcript channel URL')
    expect(getCommand('nav:collapse')?.label).toBe('Toggle sidebar')

    const source = readFileSync(TTS_COMMANDS_SOURCE, 'utf8').replace(/\r\n/g, '\n')
    const bodies = source.match(/export function deliverPalette\w+\(\): void \{[\s\S]*?\n\}\n/g) ?? []
    expect(bodies.length).toBeGreaterThanOrEqual(2)
    for (const body of bodies) {
      expect(body).not.toContain('af_heart')
      expect(body).not.toContain('postGenerate(')
      expect(body).not.toContain('postPrepare(')
    }

    window.location.hash = '#/tts'
    ttsCommands.TTS_COMMANDS.generate()
    flushFrame()
    flushFrame()
    await act(async () => {
      await Promise.resolve()
    })
    expect(fetchMock).not.toHaveBeenCalled()

    const button = document.createElement('button')
    button.dataset.testid = 'preview-cleanup-btn'
    button.disabled = true
    document.body.append(button)
    const click = vi.spyOn(button, 'click')
    ttsCommands.TTS_COMMANDS.prepare()
    flushFrame()
    flushFrame()
    expect(click).not.toHaveBeenCalled()
    button.disabled = false
    ttsCommands.TTS_COMMANDS.prepare()
    flushFrame()
    flushFrame()
    expect(click).toHaveBeenCalledTimes(1)
    await act(async () => {
      await Promise.resolve()
    })
    expect(fetchMock).not.toHaveBeenCalled()
  })
})

describe('MEU-96 CHECK_DEPS_ROUTE', () => {
  it('AC-96.9 Check dependencies opens Settings and fires after two frames; on Settings it only fires', () => {
    const fired: number[] = []
    const onCheck = () => {
      fired.push(1)
    }
    window.addEventListener(SETTINGS_EVENTS.checkDeps, onCheck)
    let hashChanges = 0
    const onHash = () => {
      hashChanges += 1
    }

    window.location.hash = '#/'
    getCommand('settings:check_deps')?.action()
    expect(window.location.hash).toBe('#/settings')
    expect(fired, 'not before the frames').toHaveLength(0)
    flushFrame()
    expect(fired).toHaveLength(0)
    flushFrame()
    expect(fired).toHaveLength(1)

    window.addEventListener('hashchange', onHash)
    getCommand('settings:check_deps')?.action()
    flushFrame()
    flushFrame()
    expect(fired).toHaveLength(2)
    expect(window.location.hash).toBe('#/settings')
    expect(hashChanges, 'no hash change on Settings').toBe(0)
    window.removeEventListener('hashchange', onHash)
    window.removeEventListener(SETTINGS_EVENTS.checkDeps, onCheck)
  })
})
