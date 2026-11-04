/** @vitest-environment jsdom */

import { render, screen, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement } from 'react'
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const APP_SHELL_PATH = resolve(
  dirname(fileURLToPath(import.meta.url)),
  '../../src/renderer/src/components/layout/AppShell.tsx',
)

describe('AC-19.11 / AC-19.17 / AC-19.19 production AppShell wiring', () => {
  const clipboardWrites: string[] = []
  const fetches: Array<{ url: string; init?: RequestInit }> = []

  beforeEach(() => {
    clipboardWrites.length = 0
    fetches.length = 0
    window.location.hash = '/'
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
      getLogSnapshot: async () => [{ key: '4', message: 'ring-line', seq: 4 }],
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
    document.documentElement.classList.remove('dark')
    document.documentElement.style.colorScheme = ''
    vi.unstubAllGlobals()
  })

  it('navigates from the rail and palette and copies plus persists console log-to-file', async () => {
    const user = userEvent.setup()
    const { AppShell } = await import('../../src/renderer/src/components/layout/AppShell')
    await act(async () => {
      render(createElement(AppShell, null, createElement('span', null, 'child')))
    })

    const transcript = screen.getByTestId('nav-transcript')
    expect(transcript).not.toBeNull()
    await user.click(transcript)
    expect(window.location.hash).toBe('#/transcript')

    const palette = screen.getByTestId('header-palette-btn')
    expect(palette.textContent).toMatch(/Commands/)
    await user.click(palette)
    const settings = screen.getByRole('button', { name: 'Settings' })
    await user.click(settings)
    expect(window.location.hash).toBe('#/settings')

    await user.click(screen.getByTestId('header-console-btn'))
    await user.click(screen.getByTestId('console-copy'))
    expect(clipboardWrites.length).toBeGreaterThan(0)

    const logToFile = screen.getByTestId('console-log-to-file')
    expect(logToFile).toBeInstanceOf(HTMLInputElement)
    await user.click(logToFile)
    await vi.waitFor(() => {
      expect(fetches.some((row) => row.url.includes('/settings/app'))).toBe(true)
    })
  })

  it('applies saved light ui.theme from GET /settings/ui onto the document root', async () => {
    document.documentElement.classList.add('dark')
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string) => {
        if (String(url).includes('/settings/ui')) {
          return new Response(JSON.stringify({ theme: 'light' }), {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
          })
        }
        return new Response(JSON.stringify({ items: [], last_seq: 0 }), { status: 200 })
      }),
    )
    const { AppShell } = await import('../../src/renderer/src/components/layout/AppShell')
    await act(async () => {
      render(createElement(AppShell, null, createElement('span', null, 'child')))
    })
    await vi.waitFor(() => {
      expect(document.documentElement.classList.contains('dark')).toBe(false)
    })
  })

  it('AC-95.6 AppShell binds every registry chord through one window keydown listener', async () => {
    const { AppShell } = await import('../../src/renderer/src/components/layout/AppShell')
    await act(async () => {
      render(createElement(AppShell, null, createElement('span', null, 'child')))
    })
    const press = async (key: string) => {
      await act(async () => {
        window.dispatchEvent(new KeyboardEvent('keydown', { key, ctrlKey: true, bubbles: true, cancelable: true }))
      })
    }
    const routes: Array<[string, string]> = [
      ['2', '#/transcript'],
      ['3', '#/tts'],
      ['4', '#/convert'],
      ['5', '#/capture'],
      [',', '#/settings'],
      ['1', '#/'],
    ]
    for (const [key, hash] of routes) {
      await press(key)
      expect(window.location.hash, `Ctrl+${key}`).toBe(hash)
    }

    const collapse = screen.getByTestId('nav-collapse')
    const before = collapse.getAttribute('aria-label')
    expect(['Collapse sidebar', 'Expand sidebar']).toContain(before)
    await press('b')
    expect(screen.getByTestId('nav-collapse').getAttribute('aria-label')).toBe(
      before === 'Collapse sidebar' ? 'Expand sidebar' : 'Collapse sidebar',
    )

    await press('k')
    expect(screen.getByTestId('command-palette')).toBeInTheDocument()

    const shell = readFileSync(APP_SHELL_PATH, 'utf8')
    expect(shell).toContain('createShortcutHandler')
    expect(shell).not.toContain("event.key === '4'")
    expect(shell).not.toContain("event.key === '5'")
    expect(shell.match(/addEventListener\('keydown'/g) ?? []).toHaveLength(1)
    expect(shell).toMatch(/window\.addEventListener\('keydown'/)
  })
})
