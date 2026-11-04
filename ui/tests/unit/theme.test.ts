/** @vitest-environment jsdom */

import { afterEach, describe, expect, it } from 'vitest'

import {
  applyDocumentTheme,
  resolveUiTheme,
  THEME_CHANGED_EVENT,
} from '../../src/renderer/src/lib/theme'

describe('ui document theme', () => {
  afterEach(() => {
    document.documentElement.classList.remove('dark')
    document.documentElement.style.colorScheme = ''
  })

  it('resolveUiTheme treats only light as light and defaults to dark', () => {
    expect(resolveUiTheme('light')).toBe('light')
    expect(resolveUiTheme('dark')).toBe('dark')
    expect(resolveUiTheme(null)).toBe('dark')
    expect(resolveUiTheme(undefined)).toBe('dark')
    expect(resolveUiTheme('system')).toBe('dark')
  })

  it('applyDocumentTheme toggles the document root dark class and color-scheme', () => {
    const seen: string[] = []
    const onTheme = (event: Event) => {
      seen.push((event as CustomEvent<{ theme: string }>).detail.theme)
    }
    window.addEventListener(THEME_CHANGED_EVENT, onTheme)
    applyDocumentTheme('light')
    expect(document.documentElement.classList.contains('dark')).toBe(false)
    expect(document.documentElement.style.colorScheme).toBe('light')
    applyDocumentTheme('dark')
    expect(document.documentElement.classList.contains('dark')).toBe(true)
    expect(document.documentElement.style.colorScheme).toBe('dark')
    window.removeEventListener(THEME_CHANGED_EVENT, onTheme)
    expect(seen).toEqual(['light', 'dark'])
  })
})
