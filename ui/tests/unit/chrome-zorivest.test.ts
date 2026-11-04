/** @vitest-environment jsdom */

import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const rendererRoot = resolve(__dirname, '../../src/renderer/src')

function readSrc(rel: string): string {
  return readFileSync(resolve(rendererRoot, rel), 'utf8')
}

describe('MEU-26 zorivest chrome', () => {
  it('AC-26.1 TOKEN_SET is present without pnl tokens', () => {
    const css = readSrc('styles.css')
    expect(css).toContain('--color-bg: #282a36')
    expect(css).toContain('--color-accent: #8be9fd')
    expect(css).toContain('--color-bg-subtle')
    expect(css).toContain('--color-accent-ring')
    expect(css).toContain('--duration-fast')
    expect(css).toContain('--ease-out')
    expect(css).toContain('--radius-control')
    expect(css).not.toContain('--color-pnl-')
    expect(css).not.toMatch(/--color-bg:\s*#1a1b26/)
  })

  it('AC-26.2 Button uses zorivest icon/radius/duration/ring tokens', () => {
    const src = readSrc('components/ui/Button.tsx')
    expect(src).toMatch(/icon\?:/)
    expect(src).toContain('rounded-[var(--radius-control)]')
    expect(src).toContain('duration-[var(--duration-fast)]')
    expect(src).toContain('focus-visible:shadow-[0_0_0_3px_var(--color-accent-ring)]')
  })

  it('AC-26.3 NavRail pins settings and snaps 200/56 without width transition', () => {
    const src = readSrc('components/layout/NavRail.tsx')
    const css = readSrc('styles.css')
    expect(src).toContain('mt-auto')
    expect(src).toContain('nav-rail')
    expect(css).toMatch(/\.nav-rail[^{]*\{[^}]*width:\s*200px/)
    expect(css).toMatch(/\.nav-rail--collapsed[^{]*\{[^}]*width:\s*56px/)
    expect(css).not.toMatch(/\.nav-rail[^{]*\{[^}]*transition:[^}]*width/)
  })

  it('AC-26.11 useBackendLogs(open) polls 500 open and 5000 closed', () => {
    const src = readSrc('hooks/useBackendLogs.ts')
    expect(src).toMatch(/useBackendLogs\(\s*open/)
    expect(src).toContain('5000')
    expect(src).toMatch(/open\s*\?\s*500\s*:\s*5000|open\s*\?\s*CONSOLE_POLL_OPEN_MS\s*:\s*CONSOLE_POLL_CLOSED_MS/)
  })

  it('AC-26.12 PERSIST_UI_KEYS drops height and keeps visible/expanded', async () => {
    const persist = await import('../../src/renderer/src/hooks/usePersistedState')
    expect([...persist.PERSIST_UI_KEYS]).toEqual([
      'ui.rail.collapsed',
      'ui.panel.console.visible',
      'ui.panel.console.expanded',
    ])
    expect('DEFAULT_CONSOLE_HEIGHT' in persist).toBe(false)
  })

  it('AC-26.14 PAGE_FILES className strings have no raw hex', () => {
    const files = [
      'styles.css',
      'components/ui/Button.tsx',
      'components/ui/SelectInput.tsx',
      'components/layout/AppShell.tsx',
      'components/layout/NavRail.tsx',
      'components/layout/Header.tsx',
      'components/layout/ConsolePanel.tsx',
      'hooks/usePersistedState.ts',
      'hooks/useBackendLogs.ts',
      'registry/commandRegistry.ts',
      'router.tsx',
      'features/settings/SettingsChrome.tsx',
    ]
    for (const file of files) {
      const src = readSrc(file)
      expect(src, file).not.toMatch(/className=\{?[`'"][^`'"]*#[0-9a-fA-F]{3,8}/)
    }
  })

  it('AC-26.16 lucide-react is pinned and used on the rail', () => {
    const pkg = readFileSync(resolve(__dirname, '../../package.json'), 'utf8')
    expect(pkg).toContain('"lucide-react": "^0.400.0"')
    const rail = readSrc('components/layout/NavRail.tsx')
    expect(rail).toContain('lucide-react')
  })

  it('AC-26.17 palette lists console:toggle and Ctrl+K still opens the palette', async () => {
    const { listPaletteIds } = await import('../../src/renderer/src/registry/commandRegistry')
    expect(listPaletteIds()).toContain('console:toggle')
    const { handleGlobalShortcut } = await import('../../src/renderer/src/components/layout/AppShell')
    expect(handleGlobalShortcut('Ctrl+K')).toBe('av-kit:open-palette')
  })
})

describe('MEU-26 AppShell chrome', () => {
  let user: ReturnType<typeof userEvent.setup>
  const clipboardWrites: string[] = []
  const fetches: Array<{ url: string; init?: RequestInit }> = []

  beforeEach(() => {
    user = userEvent.setup()
    clipboardWrites.length = 0
    fetches.length = 0
    window.location.hash = '/'
    window.localStorage.clear()
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
      writeClipboardText: async (text: string) => {
        clipboardWrites.push(text)
      },
      readTextFile: async () => ({ text: '', basename: 'x.txt' }),
      copyMcpConfig: async () => ({ ok: true as const }),
      subscribeLogs: () => () => undefined,
      getLogSnapshot: async () => [{ key: '4', message: '[debug ] ring-line', seq: 4 }],
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
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string, init?: RequestInit) => {
        fetches.push({ url: String(url), init })
        return new Response(JSON.stringify({ items: [], last_seq: 0 }), { status: 200 })
      }),
    )
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  async function renderShell(): Promise<void> {
    const { AppShell } = await import('../../src/renderer/src/components/layout/AppShell')
    await act(async () => {
      render(
        createElement(AppShell, null, createElement('span', { 'data-testid': 'main-child' }, 'child')),
      )
    })
  }

  it('AC-26.4 header breadcrumb and Commands Ctrl+K palette trigger', async () => {
    await renderShell()
    expect(document.body.textContent).toMatch(/av-kit/)
    expect(document.querySelector('.header-breadcrumb__page')?.textContent).toBe('Downloader')
    const palette = screen.queryByTestId('header-palette-btn')
    expect(palette?.textContent).toMatch(/Commands/)
    expect(palette?.textContent).toMatch(/Ctrl\+K/)
    await user.click(screen.getByTestId('nav-settings'))
    expect(document.querySelector('.header-breadcrumb__page')?.textContent).toBe('Settings')
  })

  it('AC-26.5 header-console-btn is the previous sibling of header-palette-btn', async () => {
    await renderShell()
    const palette = screen.queryByTestId('header-palette-btn')
    expect(palette?.previousElementSibling?.getAttribute('data-testid')).toBe('header-console-btn')
  })

  it('AC-26.6 console-panel is absent on first paint then mounts after toggle', async () => {
    await renderShell()
    expect(screen.queryByTestId('console-panel')).toBeNull()
    const toggle = screen.queryByTestId('header-console-btn')
    expect(toggle).not.toBeNull()
    await user.click(toggle as HTMLElement)
    const panel = screen.queryByTestId('console-panel')
    expect(panel).not.toBeNull()
    expect(panel?.className).toMatch(/w-\[40%\]/)
    expect(panel?.className).toMatch(/min-w-\[320px\]/)
  })

  it('AC-26.7 console-expand toggles w-full then restores drawer geometry', async () => {
    await renderShell()
    await user.click(screen.getByTestId('header-console-btn'))
    await user.click(screen.getByTestId('console-expand'))
    const panel = screen.queryByTestId('console-panel')
    expect(panel?.className).toMatch(/w-full/)
    expect(document.querySelector('main')?.className).toMatch(/hidden/)
    await user.click(screen.getByTestId('console-collapse'))
    expect(screen.queryByTestId('console-panel')?.className).toMatch(/min-w-\[320px\]/)
  })

  it('AC-26.8 open panel closes via X, header toggle, and Escape; collapse stays mounted', async () => {
    await renderShell()
    const open = async () => {
      await user.click(screen.getByTestId('header-console-btn'))
    }
    await open()
    await user.click(screen.getByTestId('console-close'))
    expect(screen.queryByTestId('console-panel')).toBeNull()
    await open()
    await user.click(screen.getByTestId('console-expand'))
    await user.click(screen.getByTestId('console-collapse'))
    expect(screen.queryByTestId('console-panel')).not.toBeNull()
    await user.click(screen.getByTestId('console-close'))
    expect(screen.queryByTestId('console-panel')).toBeNull()
    await open()
    await user.click(screen.getByTestId('header-console-btn'))
    expect(screen.queryByTestId('console-panel')).toBeNull()
    await open()
    await act(async () => {
      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }))
    })
    expect(screen.queryByTestId('console-panel')).toBeNull()
    await open()
    await user.click(screen.getByTestId('console-expand'))
    expect(document.querySelector('main')?.className).toMatch(/hidden/)
    await user.click(screen.getByTestId('header-console-btn'))
    expect(screen.queryByTestId('console-panel')).toBeNull()
    expect(document.querySelector('main')?.className).not.toMatch(/hidden/)
    await open()
    await user.click(screen.getByTestId('console-expand'))
    const { getCommand } = await import('../../src/renderer/src/registry/commandRegistry')
    await act(async () => {
      getCommand('console:toggle')?.action()
    })
    expect(screen.queryByTestId('console-panel')).toBeNull()
    expect(document.querySelector('main')?.className).not.toMatch(/hidden/)
  })

  it('recovers visible main from persisted closed+expanded console', async () => {
    window.localStorage.setItem('ui.panel.console.visible', 'false')
    window.localStorage.setItem('ui.panel.console.expanded', 'true')
    await renderShell()
    expect(screen.queryByTestId('console-panel')).toBeNull()
    expect(document.querySelector('main')?.className).not.toMatch(/hidden/)
    expect(window.localStorage.getItem('ui.panel.console.expanded')).toBe('false')
  })

  it('recovers visible main from persisted non-boolean expanded value', async () => {
    window.localStorage.setItem('ui.panel.console.visible', 'false')
    window.localStorage.setItem('ui.panel.console.expanded', '"true"')
    await renderShell()
    expect(screen.queryByTestId('console-panel')).toBeNull()
    expect(document.querySelector('main')?.className).not.toMatch(/hidden/)
  })

  it('AC-26.9 AppShell is the only production TOGGLE_CONSOLE_EVENT listener', async () => {
    const shell = readSrc('components/layout/AppShell.tsx')
    const panel = readSrc('components/layout/ConsolePanel.tsx')
    expect(shell).toContain('av-kit:toggle-console')
    expect(shell).toContain('addEventListener')
    expect(panel).not.toContain('av-kit:toggle-console')
    await renderShell()
    expect(screen.queryByTestId('console-panel')).toBeNull()
    await act(async () => {
      window.dispatchEvent(new CustomEvent('av-kit:toggle-console'))
    })
    expect(screen.queryByTestId('console-panel')).not.toBeNull()
  })

  it('AC-26.10 open console exposes CONSOLE_CONTROLS and G30 search styles', async () => {
    await renderShell()
    await user.click(screen.getByTestId('header-console-btn'))
    for (const id of [
      'console-panel',
      'console-header',
      'console-filter',
      'console-level-DEBUG',
      'console-search',
      'console-clear',
      'console-copy',
      'console-expand',
      'console-output',
      'console-close',
      'console-ytdlp-toggle',
      'console-log-to-file',
    ]) {
      expect(screen.queryByTestId(id), id).not.toBeNull()
    }
    expect(screen.queryByTestId('console-collapse')).toBeNull()
    expect(readSrc('components/layout/ConsolePanel.tsx')).toContain('useG30Styles')
    expect(readSrc('components/layout/ConsolePanel.tsx')).not.toMatch(/G30_DARK\s*=/)
    const expand = screen.queryByTestId('console-expand')
    expect(expand?.getAttribute('aria-expanded')).toBe('false')
    expect(screen.queryByTestId('console-clear')?.className).toMatch(/outline-btn/)
    expect(screen.queryByTestId('console-copy')?.className).toMatch(/bg-accent/)
    expect(screen.queryByTestId('console-close')?.className).toMatch(/outline-btn/)
  })

  it('AC-26.13 settings route renders SettingsChrome cards without fetch', () => {
    const chrome = readSrc('features/settings/SettingsChrome.tsx')
    expect(chrome).toContain('settings-page')
    expect(chrome).toContain('download-settings')
    expect(chrome).not.toMatch(/apiFetch|fetch\(/)
    expect(readSrc('router.tsx')).toContain('SettingsPage')
  })

  it('AC-26.15 open console-panel is complementary and not a dialog', async () => {
    await renderShell()
    await user.click(screen.getByTestId('header-console-btn'))
    const panel = screen.queryByTestId('console-panel')
    expect(panel?.getAttribute('role')).toBe('complementary')
    expect(panel?.getAttribute('role')).not.toBe('dialog')
  })

  it('AC-26.18 copy and log-to-file work after the panel is opened', async () => {
    await renderShell()
    expect(screen.queryByTestId('console-panel')).toBeNull()
    await user.click(screen.getByTestId('header-console-btn'))
    await user.click(screen.getByTestId('console-copy'))
    expect(clipboardWrites.length).toBe(1)
    expect(clipboardWrites[0]).toBe('[debug ] ring-line')
    const beforePuts = fetches.filter((row) => row.url.includes('/settings/app')).length
    const logToFile = screen.queryByTestId('console-log-to-file')
    await act(async () => {
      if (logToFile instanceof HTMLInputElement) {
        logToFile.click()
      }
    })
    await vi.waitFor(() => {
      expect(fetches.filter((row) => row.url.includes('/settings/app')).length).toBe(beforePuts + 1)
    })
    const puts = fetches.filter((row) => row.url.includes('/settings/app'))
    expect(puts).toHaveLength(beforePuts + 1)
    expect(puts[puts.length - 1]?.init?.method).toBe('PUT')
    expect(puts[puts.length - 1]?.init?.body).toBe(JSON.stringify({ log_to_file: true }))
  })
})
