/** @vitest-environment jsdom */

import { act, cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { Save } from 'lucide-react'
import { createElement, type ComponentProps } from 'react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { CommandPalette } from '../../src/renderer/src/components/CommandPalette'
import { HelpCard } from '../../src/renderer/src/components/help/HelpCard'
import { Header } from '../../src/renderer/src/components/layout/Header'
import { SHELL_NAV } from '../../src/renderer/src/components/layout/NavRail'
import { ToolbarIconButton } from '../../src/renderer/src/features/capture/ToolbarIconButton'
import { TOGGLE_CONSOLE_EVENT } from '../../src/renderer/src/lib/shell-nav'
import * as shortcuts from '../../src/renderer/src/registry/shortcuts'
import { expectBoundHint } from './helpers/bound-hint'

/*
  MEU-97 HINTS (the shell-rendered controls) and PALETTE_ENTER. The page
  controls are checked in each page's own harness; capture-region and the
  capture-save prop are source-text checks in capture-page.test.ts.
*/

type BoundControl = { testid: string; commandId: string }

// BOUND_CONTROLS is added by MEU-97; the loose type keeps this file compiling on the row 5 tree.
const sc = shortcuts as typeof shortcuts & { BOUND_CONTROLS?: readonly BoundControl[] }

const SHELL_BOUND: BoundControl[] = [
  { testid: 'header-console-btn', commandId: 'console:toggle' },
  { testid: 'help-card', commandId: 'help:toggle' },
  { testid: 'url-input', commandId: 'download:add' },
  { testid: 'channel-input', commandId: 'transcript:add' },
  { testid: 'add-btn', commandId: 'page:primary' },
  { testid: 'generate-btn', commandId: 'page:primary' },
  { testid: 'convert-add', commandId: 'page:primary' },
  { testid: 'capture-region', commandId: 'page:primary' },
  { testid: 'convert-browse', commandId: 'convert:browse' },
  { testid: 'capture-save', commandId: 'capture:save' },
  { testid: 'theme-dark-btn', commandId: 'appearance:dark' },
  { testid: 'theme-light-btn', commandId: 'appearance:light' },
]

afterEach(() => {
  cleanup()
  window.location.hash = ''
})

describe('MEU-97 gui-common-shortcuts', () => {
  it('AC-97.4 HINTS: the shell controls carry aria-keyshortcuts and show their chord', () => {
    expect(Array.isArray(sc.BOUND_CONTROLS), 'BOUND_CONTROLS').toBe(true)
    const bound = sc.BOUND_CONTROLS ?? []
    for (const item of SHELL_NAV) {
      expect(bound, item.testid).toContainEqual({ testid: item.testid, commandId: item.id })
    }
    for (const row of SHELL_BOUND) {
      expect(bound, row.testid).toContainEqual(row)
    }
    expect(bound.map((row) => row.testid)).not.toContain('header-palette-btn')

    render(createElement(Header, { consoleOpen: false, onConsoleToggle: () => undefined, onPaletteToggle: () => undefined }))
    const consoleButton = screen.getByTestId('header-console-btn')
    expectBoundHint(consoleButton, 'console:toggle')
    cleanup()

    render(createElement(HelpCard, { feature: 'settings', tabKey: 'hints', sections: [] }))
    const toggle = within(screen.getByTestId('help-card')).getByRole('button', { name: /How it works/ })
    expectBoundHint(toggle, 'help:toggle')
    cleanup()

    const base = {
      spec: { icon: Save, name: 'Save' },
      id: 'capture-save',
      variant: 'primary',
      onClick: () => undefined,
    } as ComponentProps<typeof ToolbarIconButton>
    render(createElement(ToolbarIconButton, { ...base, shortcut: 'Ctrl+S' } as ComponentProps<typeof ToolbarIconButton>))
    const save = screen.getByTestId('capture-save')
    expect(save.getAttribute('title')).toBeNull()
    act(() => {
      save.focus()
    })
    expectBoundHint(save, 'capture:save', screen.queryByTestId('capture-save-hint')?.textContent ?? '')
    expect(screen.getByTestId('capture-save-hint').textContent).toBe('Save (Ctrl+S)')
    cleanup()

    render(createElement(ToolbarIconButton, base))
    expect(screen.getByTestId('capture-save').hasAttribute('aria-keyshortcuts')).toBe(false)
  })

  it('AC-97.10 PALETTE_ENTER: Ctrl+Enter passes through the palette; plain Enter runs the highlighted command', () => {
    window.location.hash = '#/'
    const toggles = vi.fn()
    const reached: Array<{ ctrl: boolean; prevented: boolean }> = []
    const onToggle = () => {
      toggles()
    }
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Enter') {
        reached.push({ ctrl: event.ctrlKey, prevented: event.defaultPrevented })
      }
    }
    window.addEventListener(TOGGLE_CONSOLE_EVENT, onToggle)
    window.addEventListener('keydown', onKeyDown)
    try {
      render(createElement(CommandPalette, { open: true, onClose: () => undefined }))
      const input = screen.getByTestId('command-palette-input')
      fireEvent.change(input, { target: { value: 'Toggle console' } })
      fireEvent.keyDown(input, { key: 'ArrowDown' })
      const highlighted = screen.getByTestId('command-palette').querySelector('[data-selected="true"]')
      expect(highlighted?.textContent ?? '').toContain('Toggle console')

      fireEvent.keyDown(input, { key: 'Enter', ctrlKey: true })
      expect(toggles, 'Ctrl+Enter runs nothing').not.toHaveBeenCalled()
      expect(reached, 'Ctrl+Enter reaches window unprevented').toEqual([{ ctrl: true, prevented: false }])

      fireEvent.keyDown(input, { key: 'Enter' })
      expect(toggles, 'plain Enter runs the highlighted command').toHaveBeenCalledTimes(1)
    } finally {
      window.removeEventListener(TOGGLE_CONSOLE_EVENT, onToggle)
      window.removeEventListener('keydown', onKeyDown)
    }
  })
})
