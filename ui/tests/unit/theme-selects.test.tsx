/** @vitest-environment jsdom */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, render, renderHook, screen } from '@testing-library/react'
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs'
import { join, relative, resolve } from 'node:path'
import { createElement, type CSSProperties, type FunctionComponent } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import * as shell from '../../src/renderer/src/components/layout/AppShell'
import * as select from '../../src/renderer/src/components/ui/SelectInput'
import { SettingsPage } from '../../src/renderer/src/features/settings/SettingsPage'
import { ApiError } from '../../src/renderer/src/lib/api'
import * as theme from '../../src/renderer/src/lib/theme'

/**
 * MEU-94 (Session 40): THEME_HOOK, G30_STYLES, BOOT_THEME, BOOT_RETRY and THEME_GATE, defined once in
 * docs/execution/plans/2026-10-24-gui-theme-path-fields/implementation-plan.md. Every new export is
 * reached through a namespace import and its type is asserted first, so a missing name fails as an
 * assertion. `boot-theme.ts` is read as source text, never imported.
 */

const mocks = vi.hoisted(() => ({
  apiFetch: null as null | ((path: string, init?: RequestInit) => Promise<unknown>),
  realApiFetch: null as null | ((path: string, init?: RequestInit) => Promise<unknown>),
  calls: [] as string[],
  logRenderer: vi.fn(),
}))

vi.mock('../../src/renderer/src/lib/api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../../src/renderer/src/lib/api')>()
  mocks.realApiFetch = actual.apiFetch as (path: string, init?: RequestInit) => Promise<unknown>
  return {
    ...actual,
    apiFetch: (path: string, init?: RequestInit) => {
      mocks.calls.push(path)
      return (mocks.apiFetch ?? mocks.realApiFetch)!(path, init)
    },
  }
})

vi.mock('../../src/renderer/src/lib/renderer-log', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../../src/renderer/src/lib/renderer-log')>()
  return { ...actual, logRenderer: mocks.logRenderer }
})

const DARK_PAIR = { backgroundColor: '#1a1a2e', color: '#e0e0e0' }
const LIGHT_PAIR = { backgroundColor: '#ffffff', color: '#1e293b' }

const RENDERER_SRC = resolve(__dirname, '../../src/renderer/src')

/** jsdom's normalised form of a colour (a probe element given the hex reads it back). */
function normalised(value: string): string {
  const probe = document.createElement('div')
  probe.style.color = value
  return probe.style.color
}

function pairFor(name: 'dark' | 'light'): { backgroundColor: string; color: string } {
  const pair = name === 'dark' ? DARK_PAIR : LIGHT_PAIR
  return { backgroundColor: normalised(pair.backgroundColor), color: normalised(pair.color) }
}

function inlinePair(element: HTMLElement): { backgroundColor: string; color: string } {
  return { backgroundColor: element.style.backgroundColor, color: element.style.color }
}

/** Every select and option under `root` that does not carry `name`'s pair, as `tag#index`. */
function offPair(root: ParentNode, name: 'dark' | 'light'): string[] {
  const want = pairFor(name)
  const off: string[] = []
  root.querySelectorAll<HTMLElement>('select, option').forEach((element, index) => {
    const got = inlinePair(element)
    if (got.backgroundColor !== want.backgroundColor || got.color !== want.color) {
      off.push(`${element.tagName.toLowerCase()}#${index}:${element.getAttribute('data-testid') ?? ''}`)
    }
  })
  return off
}

function sourceFiles(dir: string): string[] {
  const out: string[] = []
  for (const name of readdirSync(dir)) {
    const full = join(dir, name)
    if (statSync(full).isDirectory()) {
      out.push(...sourceFiles(full))
    } else if (/\.(ts|tsx)$/.test(name)) {
      out.push(full)
    }
  }
  return out
}

function readSource(path: string): string {
  return readFileSync(join(RENDERER_SRC, path), 'utf8')
}

function mockWindowApi(): void {
  const loginItem = { supported: false, reason: 'not-packaged', enabled: false, minimized: false } as const
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
    getSetupReadiness: async () => ({ descriptorPresent: true, portOk: true, modelsDirWritable: true }),
    getMcpAccessStatus: async () => ({ tokenPresent: true }),
    captureRegion: async () => undefined,
    getHotkeyStatus: async () => ({ accelerator: 'F2', registered: true, inUse: false }),
    loginItemGet: async () => loginItem,
    loginItemSet: async () => loginItem,
    onInboxChanged: () => () => undefined,
  } as Window['api']
}

function json(payload: unknown, status = 200): Response {
  return new Response(JSON.stringify(payload), { status, headers: { 'Content-Type': 'application/json' } })
}

/** The settings-emphasis harness answers; `/settings/ui` is answered by `ui` when given. */
function installFetch(ui?: () => Promise<Response>): void {
  const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
    if (url.includes('/settings/ui')) return ui ? ui() : json({ theme: 'dark' })
    if (url.includes('/settings/app')) return json({ log_level: 'INFO', log_to_file: false, console_visible: true })
    if (url.includes('/health/dependencies')) {
      return json({ yt_dlp: { available: true, version: '2026.08.30' }, ffmpeg: { available: true, version: '7.1', path: 'C:/ffmpeg.exe' } })
    }
    if (url.includes('/settings/')) return json({})
    return json({ items: [], last_seq: 0 })
  })
  vi.stubGlobal('fetch', fetchMock)
  window.fetch = fetchMock as typeof window.fetch
}

function deferred<T>(): { promise: Promise<T>; resolve: (value: T) => void } {
  let resolve!: (value: T) => void
  const promise = new Promise<T>((done) => {
    resolve = done
  })
  return { promise, resolve }
}

beforeEach(() => {
  document.documentElement.classList.add('dark')
  mocks.apiFetch = null
  mocks.calls.length = 0
  mocks.logRenderer.mockReset()
  try {
    localStorage.clear()
  } catch {
    // jsdom storage is always available; the clear only resets state between tests.
  }
})

afterEach(() => {
  cleanup()
  vi.useRealTimers()
  vi.restoreAllMocks()
  vi.unstubAllGlobals()
  document.documentElement.classList.remove('dark')
  document.documentElement.style.colorScheme = ''
})

describe('MEU-94 THEME_HOOK', () => {
  it('AC-94.1 useDocumentTheme follows THEME_CHANGED_EVENT without a remount and unsubscribes', () => {
    expect(typeof theme.useDocumentTheme).toBe('function')
    const removeSpy = vi.spyOn(window, 'removeEventListener')
    let renders = 0
    const { result, unmount } = renderHook(() => {
      renders += 1
      return theme.useDocumentTheme()
    })
    expect(result.current).toBe('dark')
    const before = renders
    act(() => {
      theme.applyDocumentTheme('light')
    })
    expect(result.current).toBe('light')
    expect(renders).toBe(before + 1)
    act(() => {
      theme.applyDocumentTheme('dark')
    })
    expect(result.current).toBe('dark')
    expect(renders).toBe(before + 2)
    unmount()
    expect(removeSpy.mock.calls.some(([type]) => type === theme.THEME_CHANGED_EVENT)).toBe(true)
  })
})

describe('MEU-94 G30_STYLES', () => {
  it('AC-94.2 g30StylesFor returns the G30 pairs and SelectInput restyles the select and every option', () => {
    expect(typeof select.g30StylesFor).toBe('function')
    expect(typeof select.useG30Styles).toBe('function')
    expect(select.g30StylesFor('dark')).toEqual(DARK_PAIR)
    expect(select.g30StylesFor('light')).toEqual(LIGHT_PAIR)
    const callerStyle: CSSProperties = { backgroundColor: 'red', width: 50 }
    const { container } = render(
      createElement(select.SelectInput, {
        label: 'Pick',
        'data-testid': 'g30-probe',
        style: callerStyle,
        options: [
          { value: 'a', label: 'A' },
          { value: 'b', label: 'B' },
          { value: 'c', label: 'C' },
        ],
      } as select.SelectInputProps),
    )
    const element = container.querySelector('select')
    expect(element).not.toBeNull()
    expect(container.querySelectorAll('option')).toHaveLength(3)
    // [neg] In Dark no option carries the light pair (the baseline NATIVE_OPTION_MENU_STYLE did).
    expect(offPair(container, 'dark')).toEqual([])
    for (const next of ['light', 'dark', 'light'] as const) {
      act(() => {
        theme.applyDocumentTheme(next)
      })
      expect(container.querySelector('select')).toBe(element)
      expect(offPair(container, next)).toEqual([])
      expect(element?.style.width).toBe('50px')
    }
  })

  it('AC-94.3 one G30 copy and no render-time read of the dark class (source)', () => {
    const files = sourceFiles(RENDERER_SRC)
    const named = (pattern: RegExp) =>
      files.filter((file) => pattern.test(readFileSync(file, 'utf8'))).map((file) => relative(RENDERER_SRC, file).replace(/\\/g, '/'))
    expect(named(/getG30Styles|NATIVE_OPTION_MENU_STYLE/)).toEqual([])
    expect(named(/classList\.contains\(\s*['"]dark['"]\s*\)/)).toEqual(['lib/theme.ts'])
    expect(readSource('components/layout/ConsolePanel.tsx')).toContain('useG30Styles')
    expect(readSource('components/layout/ConsolePanel.tsx')).not.toMatch(/G30_(DARK|LIGHT)\s*=/)
    expect(readSource('features/capture/CaptureViewport.tsx')).toContain('useG30Styles')

    const settings = readSource('features/settings/SettingsPage.tsx')
    expect(settings).toContain('useG30Styles()')
    const hookNames = [...settings.matchAll(/const\s+(\w+)\s*=\s*useG30Styles\(\)/g)].map((m) => m[1])
    const styledBy = (tag: string) =>
      [...settings.matchAll(new RegExp(`<${tag}\\b[^>]*?style=\\{([^}]*)\\}`, 'g'))].map((m) => m[1].trim())
    const tagCount = (tag: string) => [...settings.matchAll(new RegExp(`<${tag}\\b`, 'g'))].length
    expect(tagCount('select')).toBe(2)
    expect(styledBy('select')).toHaveLength(2)
    expect(styledBy('option')).toHaveLength(tagCount('option'))
    for (const value of [...styledBy('select'), ...styledBy('option')]) {
      expect(hookNames.includes(value) || value === 'useG30Styles()', `style={${value}}`).toBe(true)
    }

    for (const path of ['features/tts/TTSPage.tsx', 'features/tts/VoiceCombobox.tsx']) {
      const blocks = [...readSource(path).matchAll(/<SelectInput\b[\s\S]*?\/>/g)].map((m) => m[0])
      expect(blocks.length, `${path} SelectInput sites`).toBeGreaterThan(0)
      expect(blocks.filter((block) => /\bstyle=/.test(block)), `${path} style props`).toEqual([])
    }
  })

  it('AC-94.4 every Settings select and option follows the theme without a remount', async () => {
    mockWindowApi()
    installFetch()
    const client = new QueryClient({ defaultOptions: { queries: { retry: false, gcTime: 0 } } })
    render(createElement(QueryClientProvider, { client }, createElement(SettingsPage)))
    await vi.waitFor(() => {
      expect(screen.getByTestId('settings-page')).toBeTruthy()
    })
    await act(async () => {
      await new Promise((done) => setTimeout(done, 0))
    })
    const page = screen.getByTestId('settings-page')
    const selects = Array.from(page.querySelectorAll('select'))
    expect(selects.length).toBeGreaterThanOrEqual(8)
    for (const next of ['light', 'dark'] as const) {
      act(() => {
        theme.applyDocumentTheme(next)
      })
      expect(Array.from(page.querySelectorAll('select'))).toEqual(selects)
      expect(offPair(page, next), `after ${next}`).toEqual([])
    }
    client.clear()
  })
})

describe('MEU-94 BOOT_THEME', () => {
  it('AC-94.5 applyDocumentTheme mirrors the theme and readBootTheme reads it back', () => {
    expect(typeof theme.readBootTheme).toBe('function')
    expect(typeof theme.THEME_STORAGE_KEY).toBe('string')
    expect(theme.THEME_STORAGE_KEY).toBe('av-kit.ui.theme')
    expect(theme.readBootTheme()).toBeNull()
    theme.applyDocumentTheme('light')
    expect(localStorage.getItem(theme.THEME_STORAGE_KEY)).toBe('light')
    expect(theme.readBootTheme()).toBe('light')
    theme.applyDocumentTheme('dark')
    expect(theme.readBootTheme()).toBe('dark')
    localStorage.setItem(theme.THEME_STORAGE_KEY, 'blue')
    expect(theme.readBootTheme()).toBeNull()
  })

  it('AC-94.5 a throwing storage reads null and never stops the class toggle or the event', () => {
    expect(typeof theme.readBootTheme).toBe('function')
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('storage denied')
    })
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('storage denied')
    })
    expect(theme.readBootTheme()).toBeNull()
    const seen: string[] = []
    const onTheme = (event: Event) => {
      seen.push((event as CustomEvent<{ theme: string }>).detail.theme)
    }
    window.addEventListener(theme.THEME_CHANGED_EVENT, onTheme)
    theme.applyDocumentTheme('light')
    window.removeEventListener(theme.THEME_CHANGED_EVENT, onTheme)
    expect(document.documentElement.classList.contains('dark')).toBe(false)
    expect(seen).toEqual(['light'])
  })

  it('AC-94.5 boot-theme.ts applies the mirror and is the first import of main.tsx (source)', () => {
    const bootPath = join(RENDERER_SRC, 'boot-theme.ts')
    expect(existsSync(bootPath), 'boot-theme.ts exists').toBe(true)
    const boot = readFileSync(bootPath, 'utf8')
    expect(boot).toContain('readBootTheme()')
    expect(boot).toContain('applyDocumentTheme(')
    const main = readSource('main.tsx')
    const firstImport = main.split(/\r?\n/).find((line) => /^\s*import\b/.test(line))
    expect(firstImport?.trim()).toBe("import './boot-theme'")
    // [neg] index.html gains no inline script (production CSP is script-src 'self').
    const html = readFileSync(resolve(RENDERER_SRC, '../index.html'), 'utf8')
    const scripts = [...html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)]
    expect(scripts.filter(([, attrs, body]) => !/\bsrc=/.test(attrs) || body.trim() !== '')).toEqual([])
  })
})

describe('MEU-94 BOOT_RETRY', () => {
  const NOT_READY = () => new ApiError(503, 'BACKEND_NOT_READY', 'Backend not ready', null)

  function useFakeClock(): void {
    vi.useFakeTimers({ toFake: ['setTimeout', 'clearTimeout', 'setInterval', 'clearInterval', 'Date'] })
  }

  async function advance(ms: number): Promise<void> {
    await act(async () => {
      await vi.advanceTimersByTimeAsync(ms)
    })
  }

  function themeLogs(): number {
    return mocks.logRenderer.mock.calls.filter(
      ([level, message]) => level === 'ERROR' && String(message).startsWith('Failed to load ui.theme: '),
    ).length
  }

  it('AC-94.6 (a) retries a not-ready backend, applies light, and settles with the theme applied', async () => {
    expect(typeof theme.useSyncDocumentTheme).toBe('function')
    useFakeClock()
    let answers = 0
    mocks.apiFetch = async () => {
      answers += 1
      if (answers <= 2) throw NOT_READY()
      return { theme: 'light' }
    }
    let darkAtFirstTrue: boolean | undefined
    const { result } = renderHook(() => {
      const settled = theme.useSyncDocumentTheme()
      if (settled === true && darkAtFirstTrue === undefined) {
        darkAtFirstTrue = document.documentElement.classList.contains('dark')
      }
      return settled
    })
    expect(result.current).toBe(false)
    await advance(0)
    expect(mocks.calls).toHaveLength(1)
    expect(result.current).toBe(false)
    await advance(250)
    expect(mocks.calls).toHaveLength(2)
    expect(result.current).toBe(false)
    expect(document.documentElement.classList.contains('dark')).toBe(true)
    await advance(500)
    expect(mocks.calls).toHaveLength(3)
    expect(document.documentElement.classList.contains('dark')).toBe(false)
    expect(result.current).toBe(true)
    expect(darkAtFirstTrue).toBe(false)
    expect(themeLogs()).toBe(0)
  })

  it('AC-94.6 (b) any other error logs once, settles at once and never retries', async () => {
    expect(typeof theme.useSyncDocumentTheme).toBe('function')
    useFakeClock()
    mocks.apiFetch = async () => {
      throw new ApiError(500, 'HTTP_ERROR', 'boom', null)
    }
    const { result } = renderHook(() => theme.useSyncDocumentTheme())
    expect(result.current).toBe(false)
    await advance(0)
    expect(mocks.calls).toHaveLength(1)
    expect(themeLogs()).toBe(1)
    expect(result.current).toBe(true)
    await advance(70_000)
    expect(mocks.calls).toHaveLength(1)
    expect(themeLogs()).toBe(1)
  })

  it('AC-94.6 (c) FETCH_FAILED settles after the first call and retries 33 times in the window', async () => {
    expect(typeof theme.useSyncDocumentTheme).toBe('function')
    useFakeClock()
    mocks.apiFetch = async () => {
      throw new ApiError(503, 'FETCH_FAILED', 'fetch failed', null)
    }
    const { result } = renderHook(() => theme.useSyncDocumentTheme())
    expect(result.current).toBe(false)
    await advance(0)
    expect(mocks.calls).toHaveLength(1)
    expect(result.current).toBe(true)
    expect(themeLogs()).toBe(0)
    await advance(70_000)
    expect(mocks.calls).toHaveLength(33)
    expect(themeLogs()).toBe(1)
    expect(result.current).toBe(true)
  })

  it('AC-94.6 (d) BACKEND_NOT_READY stays unsettled until the 33rd call fails', async () => {
    expect(typeof theme.useSyncDocumentTheme).toBe('function')
    useFakeClock()
    mocks.apiFetch = async () => {
      throw NOT_READY()
    }
    const { result } = renderHook(() => theme.useSyncDocumentTheme())
    expect(result.current).toBe(false)
    await advance(59_000)
    expect(mocks.calls).toHaveLength(32)
    expect(result.current).toBe(false)
    expect(themeLogs()).toBe(0)
    await advance(1_000)
    expect(mocks.calls).toHaveLength(33)
    expect(result.current).toBe(true)
    expect(themeLogs()).toBe(1)
    await advance(70_000)
    expect(mocks.calls).toHaveLength(33)
    expect(themeLogs()).toBe(1)
  })

  it('AC-94.6 (e) unmounting during a backoff cancels the next call', async () => {
    expect(typeof theme.useSyncDocumentTheme).toBe('function')
    useFakeClock()
    mocks.apiFetch = async () => {
      throw NOT_READY()
    }
    const { result, unmount } = renderHook(() => theme.useSyncDocumentTheme())
    expect(result.current).toBe(false)
    await advance(0)
    expect(mocks.calls).toHaveLength(1)
    unmount()
    await advance(70_000)
    expect(mocks.calls).toHaveLength(1)
    expect(themeLogs()).toBe(0)
  })

  it('AC-94.6 (f) an attempt that never answers settles at the window, logs once and ignores a late answer', async () => {
    expect(typeof theme.useSyncDocumentTheme).toBe('function')
    useFakeClock()
    const answer = deferred<unknown>()
    mocks.apiFetch = () => answer.promise
    const { result } = renderHook(() => theme.useSyncDocumentTheme())
    await advance(59_999)
    expect(mocks.calls).toHaveLength(1)
    expect(result.current).toBe(false)
    expect(themeLogs()).toBe(0)
    await advance(1)
    expect(result.current).toBe(true)
    expect(themeLogs()).toBe(1)
    expect(document.documentElement.classList.contains('dark')).toBe(true)
    // [neg] the late answer is ignored: no theme flip under an open route, no second log.
    await act(async () => {
      answer.resolve({ theme: 'light' })
    })
    await advance(70_000)
    expect(document.documentElement.classList.contains('dark')).toBe(true)
    expect(mocks.calls).toHaveLength(1)
    expect(themeLogs()).toBe(1)
  })

  it('AC-94.6 (g) unmounting while an attempt is pending clears the window and ignores the answer', async () => {
    expect(typeof theme.useSyncDocumentTheme).toBe('function')
    useFakeClock()
    const answer = deferred<unknown>()
    mocks.apiFetch = () => answer.promise
    const { unmount } = renderHook(() => theme.useSyncDocumentTheme())
    await advance(0)
    unmount()
    await advance(70_000)
    expect(themeLogs()).toBe(0)
    await act(async () => {
      answer.resolve({ theme: 'light' })
    })
    expect(document.documentElement.classList.contains('dark')).toBe(true)
    expect(mocks.calls).toHaveLength(1)
  })
})

describe('MEU-94 THEME_GATE', () => {
  it('AC-94.11 RouteThemePending is a status that says Still loading after 3 s', async () => {
    expect(typeof shell.RouteThemePending).toBe('function')
    vi.useFakeTimers({ toFake: ['setTimeout', 'clearTimeout', 'setInterval', 'clearInterval', 'Date'] })
    render(createElement(shell.RouteThemePending as FunctionComponent))
    const status = screen.getByTestId('route-theme-pending')
    expect(status.getAttribute('role')).toBe('status')
    expect(status.textContent).toBe('Connecting...')
    await act(async () => {
      await vi.advanceTimersByTimeAsync(2_999)
    })
    expect(status.textContent).toBe('Connecting...')
    await act(async () => {
      await vi.advanceTimersByTimeAsync(1)
    })
    expect(status.textContent).toBe('Still loading…')
  })

  function routeChild(seen: boolean[]) {
    return function RouteChild() {
      seen.push(document.documentElement.classList.contains('dark'))
      return createElement('span', { 'data-testid': 'route-child' }, 'child')
    }
  }

  it('AC-94.11 AppShell holds the route behind the placeholder until the theme answer', async () => {
    expect(typeof shell.RouteThemePending).toBe('function')
    mockWindowApi()
    const answer = deferred<Response>()
    installFetch(() => answer.promise)
    const seen: boolean[] = []
    await act(async () => {
      render(createElement(shell.AppShell, null, createElement(routeChild(seen))))
    })
    await vi.waitFor(() => {
      expect(mocks.calls.filter((path) => path === '/settings/ui')).toHaveLength(1)
    })
    expect(screen.queryByTestId('route-theme-pending')).not.toBeNull()
    expect(screen.queryByTestId('nav-settings')).not.toBeNull()
    expect(screen.queryByTestId('header-console-btn')).not.toBeNull()
    expect(screen.queryByTestId('route-child')).toBeNull()
    await act(async () => {
      answer.resolve(json({ theme: 'light' }))
    })
    await vi.waitFor(() => {
      expect(screen.queryByTestId('route-child')).not.toBeNull()
    })
    expect(screen.queryByTestId('route-theme-pending')).toBeNull()
    expect(seen[0]).toBe(false)
  })

  it('AC-94.11 AppShell opens the route after one 599 theme answer', async () => {
    expect(typeof shell.RouteThemePending).toBe('function')
    mockWindowApi()
    const answer = deferred<Response>()
    installFetch(() => answer.promise)
    const seen: boolean[] = []
    await act(async () => {
      render(createElement(shell.AppShell, null, createElement(routeChild(seen))))
    })
    await vi.waitFor(() => {
      expect(mocks.calls.filter((path) => path === '/settings/ui')).toHaveLength(1)
    })
    expect(screen.queryByTestId('route-child')).toBeNull()
    await act(async () => {
      answer.resolve(json({ error: { code: 'E2E', message: 'unexpected' } }, 599))
    })
    await vi.waitFor(() => {
      expect(screen.queryByTestId('route-child')).not.toBeNull()
    })
    expect(mocks.calls.filter((path) => path === '/settings/ui')).toHaveLength(1)
  })

  it('AC-94.11 AppShell opens the route at the boot window when the theme request never answers', async () => {
    expect(typeof shell.RouteThemePending).toBe('function')
    vi.useFakeTimers({ toFake: ['setTimeout', 'clearTimeout', 'setInterval', 'clearInterval', 'Date'] })
    mockWindowApi()
    installFetch(() => new Promise<Response>(() => {}))
    const seen: boolean[] = []
    await act(async () => {
      render(createElement(shell.AppShell, null, createElement(routeChild(seen))))
    })
    await act(async () => {
      await vi.advanceTimersByTimeAsync(59_000)
    })
    expect(mocks.calls.filter((path) => path === '/settings/ui')).toHaveLength(1)
    expect(screen.queryByTestId('route-theme-pending')).not.toBeNull()
    expect(screen.queryByTestId('route-child')).toBeNull()
    await act(async () => {
      await vi.advanceTimersByTimeAsync(1_000)
    })
    expect(screen.queryByTestId('route-child')).not.toBeNull()
    expect(screen.queryByTestId('route-theme-pending')).toBeNull()
  })
})
