/** @vitest-environment jsdom */

import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

import { act, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const rendererRoot = resolve(__dirname, '../../src/renderer/src')

function readSrc(rel: string): string {
  return readFileSync(resolve(rendererRoot, rel), 'utf8')
}

describe('MEU-27 console polish', () => {
  let user: ReturnType<typeof userEvent.setup>

  beforeEach(() => {
    user = userEvent.setup()
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
      writeClipboardText: async () => undefined,
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
      vi.fn(async () => new Response(JSON.stringify({ items: [], last_seq: 0 }), { status: 200 })),
    )
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  async function renderShell(child = 'child'): Promise<void> {
    const { AppShell } = await import('../../src/renderer/src/components/layout/AppShell')
    await act(async () => {
      render(
        createElement(AppShell, null, createElement('span', { 'data-testid': 'main-child' }, child)),
      )
    })
  }

  async function openConsole(): Promise<void> {
    await user.click(screen.getByTestId('header-console-btn'))
  }

  it('AC-27.1 header-left expand toggle uses lucide PanelLeftClose and hides collapse', async () => {
    await renderShell()
    await openConsole()
    const header = screen.queryByTestId('console-header')
    expect(header).not.toBeNull()
    const expand = within(header as HTMLElement).queryByTestId('console-expand')
    expect(expand).not.toBeNull()
    expect(expand?.textContent).toMatch(/Expand/)
    expect(expand?.getAttribute('aria-expanded')).toBe('false')
    expect(expand?.getAttribute('aria-label')).toBe('Expand panel to full width')
    expect(readSrc('components/layout/ConsolePanel.tsx')).toContain('PanelLeftClose')
    expect(screen.queryByTestId('console-collapse')).toBeNull()
    expect(within(header as HTMLElement).queryByTestId('console-close')).not.toBeNull()
  })

  it('AC-27.2 expand applies EXPAND_SOLO and swaps to collapse with PanelLeftOpen', async () => {
    await renderShell()
    await openConsole()
    await user.click(screen.getByTestId('console-expand'))
    expect(screen.queryByTestId('console-panel')?.className).toMatch(/w-full/)
    expect(document.querySelector('main')?.className).toMatch(/hidden/)
    expect(screen.queryByTestId('nav-downloader')).not.toBeNull()
    expect(screen.queryByTestId('header-console-btn')).not.toBeNull()
    const collapse = within(screen.getByTestId('console-header')).queryByTestId('console-collapse')
    expect(collapse).not.toBeNull()
    expect(collapse?.textContent).toMatch(/Collapse/)
    expect(collapse?.getAttribute('aria-expanded')).toBe('true')
    expect(screen.queryByTestId('console-expand')).toBeNull()
    expect(readSrc('components/layout/ConsolePanel.tsx')).toContain('PanelLeftOpen')
  })

  it('AC-27.3 collapse restores the drawer and keeps the panel mounted', async () => {
    await renderShell()
    await openConsole()
    await user.click(screen.getByTestId('console-expand'))
    await user.click(screen.getByTestId('console-collapse'))
    const panel = screen.queryByTestId('console-panel')
    expect(panel).not.toBeNull()
    expect(panel?.className).toMatch(/w-\[40%\]/)
    expect(panel?.className).toMatch(/min-w-\[320px\]/)
    expect(document.querySelector('main')?.className).not.toMatch(/hidden/)
  })

  it('AC-27.4 close paths unmount and clear expanded so main is visible', async () => {
    await renderShell()
    await openConsole()
    expect(
      within(screen.getByTestId('console-header')).queryByTestId('console-close'),
    ).not.toBeNull()
    await user.click(screen.getByTestId('console-expand'))
    await user.click(screen.getByTestId('console-close'))
    expect(screen.queryByTestId('console-panel')).toBeNull()
    expect(document.querySelector('main')?.className).not.toMatch(/hidden/)
    await openConsole()
    await act(async () => {
      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }))
    })
    expect(screen.queryByTestId('console-panel')).toBeNull()
    await openConsole()
    await user.click(screen.getByTestId('header-console-btn'))
    expect(screen.queryByTestId('console-panel')).toBeNull()
  })

  it('AC-27.5 SHELL_VIEWPORT tokens live on app-shell and console-output', () => {
    const shell = readSrc('components/layout/AppShell.tsx')
    const panel = readSrc('components/layout/ConsolePanel.tsx')
    expect(shell).toContain('data-testid="app-shell"')
    expect(shell).toContain('h-screen')
    expect(shell).toContain('overflow-hidden')
    expect(shell).not.toContain('min-h-screen')
    expect(shell).toContain('flex-1 min-h-0 overflow-hidden')
    expect(panel).toContain('flex flex-col h-full min-h-0 overflow-hidden')
    expect(panel).toContain('data-testid="console-output"')
    expect(panel).toContain('flex-1 min-h-0 overflow-auto')
  })

  it('AC-27.6 CONSOLE_OUTPUT_THEME uses token vars and no raw hex in className', () => {
    const css = readSrc('styles.css')
    const panel = readSrc('components/layout/ConsolePanel.tsx')
    expect(css).toContain('--color-console-bg: #000000')
    expect(css).toContain('--color-console-fg: #33ff00')
    expect(panel).toContain('bg-[var(--color-console-bg)]')
    expect(panel).toContain('text-[var(--color-console-fg)]')
    expect(panel).not.toMatch(/className=\{?["'`][^"'`]*#[0-9a-fA-F]{3}/)
  })

  it('AC-27.7 LEVEL_BUTTONS are exclusive radios and INFO click selects only INFO', async () => {
    await renderShell()
    await openConsole()
    const group = screen.queryByTestId('console-filter')
    expect(group?.getAttribute('role')).toBe('radiogroup')
    for (const level of ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']) {
      const button = screen.queryByTestId(`console-level-${level}`)
      expect(button, level).not.toBeNull()
      expect(button?.getAttribute('role')).toBe('radio')
    }
    expect(screen.queryByTestId('console-level-DEBUG')?.getAttribute('aria-checked')).toBe(
      'true',
    )
    await user.click(screen.getByTestId('console-level-INFO'))
    expect(screen.queryByTestId('console-level-INFO')?.getAttribute('aria-checked')).toBe(
      'true',
    )
    expect(screen.queryByTestId('console-level-DEBUG')?.getAttribute('aria-checked')).toBe(
      'false',
    )
    expect(screen.queryByTestId('console-level-WARNING')?.getAttribute('aria-checked')).toBe(
      'false',
    )
  })

  // AC-27.8 and AC-27.9 follow Mat's 2026-11-09 ruling D-1 (the level and above), which
  // replaces MEU-27's exact match; console-level-threshold.test.ts holds the full matrix.
  it('AC-27.8 lineMeetsLevel keeps the level and above and fails closed on tokenless lines', async () => {
    const { lineMeetsLevel } = await import(
      '../../src/renderer/src/components/layout/ConsolePanel'
    )
    expect(lineMeetsLevel('2026-08-20 15:31:51 [debug ] uow.commit', 'DEBUG')).toBe(true)
    expect(lineMeetsLevel('2026-08-20 [info] started', 'DEBUG')).toBe(true)
    expect(lineMeetsLevel('2026-08-20 [debug ] uow.commit', 'INFO')).toBe(false)
    expect(lineMeetsLevel('no level token here', 'DEBUG')).toBe(false)
    expect(lineMeetsLevel('[INFO] ok', 'INFO')).toBe(true)
  })

  it('AC-27.9 open console-output applies the DEBUG threshold to rendered text', async () => {
    const { ConsolePanel } = await import('../../src/renderer/src/components/layout/ConsolePanel')
    await act(async () => {
      render(
        createElement(ConsolePanel, {
          lines: ['[debug ] keep-me', '[info] keep-too', 'tokenless hide'],
        }),
      )
    })
    const output = screen.queryByTestId('console-output')?.textContent ?? ''
    expect(output).toContain('keep-me')
    expect(output).toContain('keep-too')
    expect(output).not.toContain('tokenless hide')
  })

  it('AC-27.10 PAGE_FILES className has no raw hex and SUPERSEDED_26 drops SelectInput/collapse-unmount', () => {
    for (const rel of [
      'styles.css',
      'components/layout/AppShell.tsx',
      'components/layout/ConsolePanel.tsx',
    ]) {
      const src = readSrc(rel)
      const classes = src.match(/className=\{?["'`][^"'`]+["'`]/g) ?? []
      for (const chunk of classes) {
        expect(chunk, rel).not.toMatch(/#[0-9a-fA-F]{3,8}/)
      }
    }
    const panel = readSrc('components/layout/ConsolePanel.tsx')
    expect(panel).not.toMatch(/<SelectInput\b/)
    expect(panel).not.toMatch(/import\s*\{[^}]*\bSelectInput\b[^}]*\}/)
    const chrome = readFileSync(resolve(__dirname, './chrome-zorivest.test.ts'), 'utf8')
    expect(chrome).not.toContain("toContain('SelectInput')")
    expect(chrome).toMatch(/AC-26\.8[\s\S]*console-collapse[\s\S]*not\.toBeNull/)
  })
})
