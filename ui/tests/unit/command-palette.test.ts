import { describe, expect, it } from 'vitest'

describe('AC-19.17 SHELL_PALETTE_IDS', () => {
  it('registers only shell palette ids and keeps Ctrl+K on AppShell', async () => {
    const { listPaletteIds } = await import('../../src/renderer/src/registry/commandRegistry')
    const ids = listPaletteIds()
    expect(ids).toEqual(expect.arrayContaining(['nav:collapse', 'nav:downloader', 'nav:settings', 'nav:transcript', 'nav:tts', 'nav:convert']))
    expect(ids).toContain('download:add')
    const { OPEN_PALETTE_EVENT, handleGlobalShortcut } = await import(
      '../../src/renderer/src/components/layout/AppShell'
    )
    expect(OPEN_PALETTE_EVENT).toBe('av-kit:open-palette')
    expect(handleGlobalShortcut('Ctrl+K')).toBe('av-kit:open-palette')
  })
})
