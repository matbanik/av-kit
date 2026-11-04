/** @vitest-environment jsdom */

import { existsSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { render, screen, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement } from 'react'
import { beforeEach, describe, expect, it } from 'vitest'

import { HelpCard } from '../../src/renderer/src/components/help/HelpCard'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')
const helpDir = resolve(repoRoot, 'ui/src/renderer/src/components/help')
const helpCardPath = resolve(helpDir, 'HelpCard.tsx')
const appShellPath = resolve(repoRoot, 'ui/src/renderer/src/components/layout/AppShell.tsx')
const registryPath = resolve(repoRoot, 'ui/src/renderer/src/registry/commandRegistry.ts')
const downloaderPagePath = resolve(repoRoot, 'ui/src/renderer/src/features/downloader/DownloaderPage.tsx')
const transcriptPagePath = resolve(repoRoot, 'ui/src/renderer/src/features/transcript/TranscriptPage.tsx')
const ttsPagePath = resolve(repoRoot, 'ui/src/renderer/src/features/tts/TTSPage.tsx')
const settingsPagePath = resolve(repoRoot, 'ui/src/renderer/src/features/settings/SettingsPage.tsx')

const HELP_SECTIONS = [{ id: 'one', title: 'URL help', body: 'Paste a URL.' }]

const HELP_MODULES = [
  {
    file: 'downloader-help-content.ts',
    topics: ['URL', 'SABR', 'cookie', 'archive', 'pause'],
  },
  {
    file: 'transcript-help-content.ts',
    topics: ['resume', 'Cancelled', 'requeue', 'compile', 'rate'],
  },
  {
    file: 'tts-help-content.ts',
    topics: ['prepare', 'voice', 'download', 'load', 'paste'],
  },
  {
    file: 'settings-help-content.ts',
    topics: ['leaf', 'FFmpeg', 'MCP', 'console'],
  },
] as const

function readRequired(path: string): string {
  expect(existsSync(path), path).toBe(true)
  return readFileSync(path, 'utf8')
}

describe('MEU-23 HelpCard', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('AC-23.17 HelpCard toggles expanded on toggle-local event', async () => {
    // G37_RULE: this spec drives HelpCard through the app-level `av-kit:help:*`
    // window events the command palette emits, not through the disclosure button,
    // so `setup()` installs the user-event surface without a pointer call to make.
    userEvent.setup()
    await act(async () => {
      render(
        createElement(HelpCard, {
          feature: 'settings',
          tabKey: 'main',
          sections: HELP_SECTIONS,
        }),
      )
    })
    const toggle = screen.getByTestId('help-card').querySelector('button')
    expect(toggle?.textContent).toContain('How it works')
    // First visit is collapsed by default.
    expect(toggle?.getAttribute('aria-expanded')).toBe('false')
    await act(async () => {
      window.dispatchEvent(new CustomEvent('av-kit:help:toggle-local'))
    })
    expect(toggle?.getAttribute('aria-expanded')).toBe('true')
    await act(async () => {
      window.dispatchEvent(new CustomEvent('av-kit:help:toggle-local'))
    })
    expect(toggle?.getAttribute('aria-expanded')).toBe('false')
  })

  it('AC-23.15 HelpCard exposes ARIA disclosure and HELP_COLLAPSE_KEY storage', () => {
    const card = readRequired(helpCardPath)
    expect(card).toContain('help-card')
    expect(card).toMatch(/aria-expanded/)
    expect(card).toMatch(/aria-controls/)
    expect(card).toMatch(/av-kit:[a-z]+-help:[^'"]+:state/)
    expect(card).toMatch(/localStorage/)
  })

  it('AC-23.16 four HELP_MODULES export minimum topics on feature pages', () => {
    for (const mod of HELP_MODULES) {
      const path = resolve(repoRoot, 'ui/src/renderer/src/features', mod.file.replace('-help-content.ts', ''), mod.file)
      const altSettings = resolve(repoRoot, 'ui/src/renderer/src/features/settings', mod.file)
      const src = existsSync(path) ? readFileSync(path, 'utf8') : existsSync(altSettings) ? readFileSync(altSettings, 'utf8') : ''
      expect(src.length, mod.file).toBeGreaterThan(0)
      for (const topic of mod.topics) {
        expect(src.toLowerCase()).toContain(topic.toLowerCase())
      }
    }
    expect(readRequired(downloaderPagePath)).toMatch(/HelpCard|help-card/)
    expect(readRequired(transcriptPagePath)).toMatch(/HelpCard|help-card/)
    expect(readRequired(ttsPagePath)).toMatch(/HelpCard|help-card/)
    expect(readRequired(settingsPagePath)).toMatch(/HelpCard|help-card/)
  })

  it('AC-23.17 HelpCard applies pending toggle queued before mount', async () => {
    sessionStorage.setItem('av-kit:help:pending-toggle', '1')
    await act(async () => {
      render(
        createElement(HelpCard, {
          feature: 'settings',
          tabKey: 'main',
          sections: HELP_SECTIONS,
        }),
      )
    })
    const toggle = screen.getByTestId('help-card').querySelector('button')
    // Default first visit is collapsed; pending toggle flips to expanded.
    expect(toggle?.getAttribute('aria-expanded')).toBe('true')
    expect(sessionStorage.getItem('av-kit:help:pending-toggle')).toBeNull()
  })

  it('AC-23.17 help:toggle palette delivery via AppShell and HELP_COMMANDS', () => {
    const registry = readRequired(registryPath)
    expect(registry).toContain('help:toggle')
    expect(registry).toMatch(/HELP_EVENTS|av-kit:help:toggle/)
    const shell = readRequired(appShellPath)
    expect(shell).toMatch(/HELP_COMMANDS\.toggle/)
    expect(shell).toMatch(/queueToggleAfterNavigate/)
    expect(shell).toMatch(/navigateShell/)
    expect(readRequired(resolve(repoRoot, 'ui/src/renderer/src/features/settings/settings-commands.ts'))).toMatch(
      /HELP_PENDING_TOGGLE_KEY|av-kit:help:pending-toggle/,
    )
    expect(readRequired(helpCardPath)).toMatch(/HELP_PENDING_TOGGLE_KEY|av-kit:help:pending-toggle/)
    expect(readRequired(helpCardPath)).toMatch(/av-kit:help:toggle-local/)
  })
})
