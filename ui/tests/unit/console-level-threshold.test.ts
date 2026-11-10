/** @vitest-environment jsdom */
/**
 * Console level rulings (Mat, 2026-11-09, "recommendations to decisions are accepted"):
 * D-1 a level button shows that level and everything more severe; D-2 the Console opens at
 * Settings → Log level (`app.log_level`) until a button is clicked.
 */
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

import { act, cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement } from 'react'
import { afterEach, describe, expect, it } from 'vitest'

import {
  ConsolePanel,
  lineMeetsLevel,
} from '../../src/renderer/src/components/layout/ConsolePanel'

const rendererRoot = resolve(__dirname, '../../src/renderer/src')
const LINES = [
  '[debug ] d-line',
  '[info] i-line',
  '[WARNING] w-line',
  '[error] e-line',
  '[CRITICAL] c-line',
  'tokenless t-line',
]

afterEach(() => {
  cleanup()
})

function output(): string {
  return screen.queryByTestId('console-output')?.textContent ?? ''
}

function checked(): string[] {
  return ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'].filter(
    (level) => screen.getByTestId(`console-level-${level}`).getAttribute('aria-checked') === 'true',
  )
}

describe('Console level threshold (D-1)', () => {
  it('a line passes when its level is the selected level or more severe', () => {
    expect(lineMeetsLevel('[debug ] x', 'DEBUG')).toBe(true)
    expect(lineMeetsLevel('[info] x', 'DEBUG')).toBe(true)
    expect(lineMeetsLevel('[CRITICAL] x', 'DEBUG')).toBe(true)
    expect(lineMeetsLevel('[debug ] x', 'INFO')).toBe(false)
    expect(lineMeetsLevel('[warning] x', 'INFO')).toBe(true)
    expect(lineMeetsLevel('[INFO] x', 'WARNING')).toBe(false)
    expect(lineMeetsLevel('[ERROR] x', 'ERROR')).toBe(true)
    expect(lineMeetsLevel('[ERROR] x', 'CRITICAL')).toBe(false)
    expect(lineMeetsLevel('no level token here', 'DEBUG')).toBe(false)
  })

  it('DEBUG shows every levelled line; INFO hides only DEBUG; ERROR keeps ERROR and CRITICAL', async () => {
    const user = userEvent.setup()
    render(createElement(ConsolePanel, { lines: LINES }))
    expect(checked()).toEqual(['DEBUG'])
    for (const word of ['d-line', 'i-line', 'w-line', 'e-line', 'c-line']) {
      expect(output()).toContain(word)
    }
    expect(output()).not.toContain('t-line')
    await user.click(screen.getByTestId('console-level-INFO'))
    expect(output()).not.toContain('d-line')
    for (const word of ['i-line', 'w-line', 'e-line', 'c-line']) {
      expect(output()).toContain(word)
    }
    await user.click(screen.getByTestId('console-level-ERROR'))
    expect(output()).not.toContain('w-line')
    expect(output()).toContain('e-line')
    expect(output()).toContain('c-line')
  })
})

describe('Console opens at Settings → Log level (D-2)', () => {
  it('starts at the saved level', async () => {
    await act(async () => {
      render(
        createElement(ConsolePanel, {
          lines: LINES,
          loadStartLevel: async () => ({ log_level: 'WARNING' }),
        }),
      )
    })
    expect(checked()).toEqual(['WARNING'])
    expect(output()).not.toContain('i-line')
    expect(output()).toContain('w-line')
  })

  it('a click before the setting arrives wins', async () => {
    const user = userEvent.setup()
    let answer: (value: unknown) => void = () => undefined
    const pending = new Promise<unknown>((resolveAnswer) => {
      answer = resolveAnswer
    })
    render(createElement(ConsolePanel, { lines: LINES, loadStartLevel: () => pending }))
    await user.click(screen.getByTestId('console-level-ERROR'))
    await act(async () => {
      answer({ log_level: 'INFO' })
      await pending
    })
    expect(checked()).toEqual(['ERROR'])
  })

  it('an unknown or failed answer keeps DEBUG', async () => {
    await act(async () => {
      render(
        createElement(ConsolePanel, {
          lines: LINES,
          loadStartLevel: async () => ({ log_level: 'LOUD' }),
        }),
      )
    })
    expect(checked()).toEqual(['DEBUG'])
    cleanup()
    await act(async () => {
      render(
        createElement(ConsolePanel, {
          lines: LINES,
          loadStartLevel: async () => {
            throw new Error('offline')
          },
        }),
      )
    })
    expect(checked()).toEqual(['DEBUG'])
  })

  it('the shell reads app settings for the panel, and Settings says what Log level does', () => {
    const shell = readFileSync(resolve(rendererRoot, 'components/layout/AppShell.tsx'), 'utf8')
    expect(shell).toMatch(/loadStartLevel=\{\(\) => apiFetch[^}]*'\/settings\/app'\)/)
    const settings = readFileSync(resolve(rendererRoot, 'features/settings/SettingsPage.tsx'), 'utf8')
    expect(settings).toContain(
      'hint="The level the Console opens at. A level shows its own lines and every more severe one."',
    )
  })
})
