import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

import { describe, expect, it } from 'vitest'

describe('AC-19.18 PERSIST_UI_KEYS', () => {
  it('round-trips rail and console persist keys without raw hex class names', async () => {
    const persistMod = await import('../../src/renderer/src/hooks/usePersistedState')
    const { PERSIST_UI_KEYS, createUiPersist } = persistMod
    expect([...PERSIST_UI_KEYS]).toEqual([
      'ui.rail.collapsed',
      'ui.panel.console.visible',
      'ui.panel.console.expanded',
    ])
    expect('DEFAULT_CONSOLE_HEIGHT' in persistMod).toBe(false)
    const store = new Map<string, unknown>()
    const persist = createUiPersist(store)
    persist.write('ui.rail.collapsed', true)
    persist.write('ui.panel.console.visible', true)
    persist.write('ui.panel.console.expanded', false)
    expect(persist.read('ui.rail.collapsed')).toBe(true)
    expect(persist.read('ui.panel.console.visible')).toBe(true)
    expect(persist.read('ui.panel.console.expanded')).toBe(false)

    const { restoreWindowBounds } = await import('../../src/main/index')
    persist.write('window.bounds', { x: 10, y: 20, width: 1280, height: 800 })
    expect(restoreWindowBounds(store)).toEqual({ x: 10, y: 20, width: 1280, height: 800 })

    const shell = readFileSync(
      resolve(__dirname, '../../src/renderer/src/components/layout/AppShell.tsx'),
      'utf8',
    )
    expect(shell).not.toMatch(/className=\{?[`'"][^`'"]*#[0-9a-fA-F]{3,8}/)
  })

  it('usePersistedState writes and createWindowOptions restores stored bounds', async () => {
    const { createWindowOptions } = await import('../../src/main/index')
    const store = new Map<string, unknown>([
      ['window.bounds', { x: 12, y: 24, width: 1100, height: 700 }],
    ])
    expect(createWindowOptions(store)).toMatchObject({
      x: 12,
      y: 24,
      width: 1100,
      height: 700,
    })

    const storage = new Map<string, string>()
    const persist = {
      getItem: (key: string) => storage.get(key) ?? null,
      setItem: (key: string, value: string) => {
        storage.set(key, value)
      },
    }
    const { readPersisted, writePersisted } = await import(
      '../../src/renderer/src/hooks/usePersistedState'
    )
    writePersisted('ui.rail.collapsed', true, persist)
    expect(readPersisted('ui.rail.collapsed', false, persist)).toBe(true)
    persist.setItem('ui.panel.console.expanded', '"true"')
    expect(readPersisted('ui.panel.console.expanded', false, persist)).toBe(false)
  })
})
