/** @vitest-environment jsdom */

import { act, cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { Header } from '../../src/renderer/src/components/layout/Header'
import { TOGGLE_CONSOLE_EVENT } from '../../src/renderer/src/lib/shell-nav'

/**
 * MEU-69 header toggles (Session 31). CONSOLE_TOGGLE, PALETTE_BUTTON and
 * CONSOLE_PRESSED_INVARIANT are defined once in
 * docs/execution/plans/2026-10-10-gui-polish-residuals/implementation-plan.md.
 */

function renderHeader(consoleOpen: boolean) {
  return render(
    createElement(Header, {
      consoleOpen,
      onConsoleToggle: vi.fn(),
      onPaletteToggle: vi.fn(),
    }),
  )
}

function classTokens(element: Element): string[] {
  return element.className.split(/\s+/).filter((token) => token.length > 0)
}

describe('MEU-69 Header alone (CONSOLE_TOGGLE)', () => {
  afterEach(() => {
    cleanup()
  })

  it('AC-69.1 closed console: aria-pressed false, outline variant, constant name and one hidden icon', () => {
    renderHeader(false)
    const button = screen.getByTestId('header-console-btn')
    expect(button.getAttribute('aria-pressed')).toBe('false')
    expect(screen.queryByRole('button', { name: 'Console' })).toBe(button)
    const tokens = classTokens(button)
    expect(tokens).toContain('btn-outline')
    expect(tokens).not.toContain('btn-ghost')
    expect(tokens).toContain('h-7')
    const icons = button.querySelectorAll('svg')
    expect(icons).toHaveLength(1)
    expect(icons[0]?.getAttribute('aria-hidden')).toBe('true')
  })

  it('AC-69.1 open console: aria-pressed true, secondary variant with a transparent border, same name', () => {
    const view = renderHeader(false)
    view.rerender(
      createElement(Header, { consoleOpen: true, onConsoleToggle: vi.fn(), onPaletteToggle: vi.fn() }),
    )
    const button = screen.getByTestId('header-console-btn')
    expect(button.getAttribute('aria-pressed')).toBe('true')
    expect(screen.queryByRole('button', { name: 'Console' })).toBe(button)
    const tokens = classTokens(button)
    expect(tokens).toContain('btn-secondary')
    expect(tokens).toContain('border')
    expect(tokens).toContain('border-transparent')
    expect(tokens).not.toContain('btn-ghost')
    expect(tokens).toContain('h-7')
    expect(button.querySelectorAll('svg')).toHaveLength(1)
  })
})

describe('MEU-69 header toggles in AppShell', () => {
  let user: ReturnType<typeof userEvent.setup>

  beforeEach(() => {
    user = userEvent.setup()
    window.location.hash = '/'
    window.localStorage.clear()
    // Same seam as chrome-zorivest.test.ts (MEU-26 AppShell chrome).
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
      loginItemGet: async () => ({ supported: false, reason: 'not-packaged', enabled: false, minimized: false }),
      loginItemSet: async () => ({ supported: false, reason: 'not-packaged', enabled: false, minimized: false }),
      onInboxChanged: () => () => undefined,
    }
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => new Response(JSON.stringify({ items: [], last_seq: 0 }), { status: 200 })),
    )
  })

  afterEach(() => {
    cleanup()
    vi.unstubAllGlobals()
  })

  async function renderShell(): Promise<void> {
    const { AppShell } = await import('../../src/renderer/src/components/layout/AppShell')
    await act(async () => {
      render(createElement(AppShell, null, createElement('span', null, 'child')))
    })
  }

  function consoleButton(): HTMLElement {
    return screen.getByTestId('header-console-btn')
  }

  /** CONSOLE_PRESSED_INVARIANT: aria-pressed is "true" exactly when console-panel is mounted. */
  function expectInvariant(step: string, panelOpen: boolean): void {
    const mounted = screen.queryByTestId('console-panel') !== null
    expect(mounted, `${step}: panel mounted`).toBe(panelOpen)
    expect(consoleButton().getAttribute('aria-pressed'), `${step}: aria-pressed`).toBe(mounted ? 'true' : 'false')
  }

  async function fireToggleEvent(): Promise<void> {
    await act(async () => {
      window.dispatchEvent(new CustomEvent(TOGGLE_CONSOLE_EVENT))
    })
  }

  it('AC-69.2 aria-pressed follows the panel through every open and close path', async () => {
    await renderShell()
    expectInvariant('launch', false)
    await user.click(consoleButton())
    expectInvariant('header open', true)
    await user.click(screen.getByTestId('console-close'))
    expectInvariant('console-close', false)
    await user.click(consoleButton())
    expectInvariant('header open again', true)
    await act(async () => {
      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }))
    })
    expectInvariant('Escape', false)
    await fireToggleEvent()
    expectInvariant('palette toggle command opens', true)
    await fireToggleEvent()
    expectInvariant('palette toggle command closes', false)
  })

  it('AC-69.2 a persisted-open launch starts pressed', async () => {
    window.localStorage.setItem('ui.panel.console.visible', JSON.stringify(true))
    await renderShell()
    expectInvariant('persisted-open launch', true)
  })

  it('AC-69.3 Enter and Space toggle the console and focus stays on the button', async () => {
    await renderShell()
    const button = consoleButton()
    button.focus()
    await user.keyboard('{Enter}')
    expectInvariant('Enter', true)
    expect(document.activeElement).toBe(consoleButton())
    await user.keyboard(' ')
    expectInvariant('Space', false)
    expect(document.activeElement).toBe(consoleButton())
  })

  it('AC-69.3 mouse twin: a click keeps focus on the button and Escape then closes the console', async () => {
    await renderShell()
    await user.click(consoleButton())
    expectInvariant('click', true)
    expect(document.activeElement).toBe(consoleButton())
    await user.keyboard('{Escape}')
    expectInvariant('Escape after click', false)
  })

  it('AC-69.4 the palette control reads Commands with the Ctrl+K hint and opens the palette', async () => {
    await renderShell()
    const palette = screen.getByTestId('header-palette-btn')
    expect(screen.queryByRole('button', { name: 'Commands' })).toBe(palette)
    expect(screen.queryByRole('button', { name: 'Open command palette' })).toBeNull()
    expect(palette.textContent).toMatch(/Commands/)
    expect(palette.textContent).toMatch(/Ctrl\+K/)
    expect(palette.textContent).not.toMatch(/Settings/)
    expect(palette.getAttribute('aria-keyshortcuts')).toBe('Control+K')
    const tokens = classTokens(palette)
    expect(tokens).toContain('btn-outline')
    expect(tokens).toContain('h-7')
    const icons = palette.querySelectorAll('svg')
    expect(icons).toHaveLength(1)
    expect(icons[0]?.getAttribute('aria-hidden')).toBe('true')
    expect(palette.previousElementSibling?.getAttribute('data-testid')).toBe('header-console-btn')
    await user.click(palette)
    expect(screen.getByTestId('command-palette')).toBeTruthy()
    expect(screen.getByRole('button', { name: 'Settings' })).toBeTruthy()
  })

  it('AC-69.4 Ctrl+K still opens the palette', async () => {
    await renderShell()
    expect(screen.queryByTestId('command-palette')).toBeNull()
    await act(async () => {
      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'k', ctrlKey: true, bubbles: true }))
    })
    expect(screen.getByTestId('command-palette')).toBeTruthy()
  })
})
