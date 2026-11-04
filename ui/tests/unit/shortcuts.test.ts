/** @vitest-environment jsdom */

import { existsSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { cleanup, render, screen } from '@testing-library/react'
import { createElement } from 'react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import * as nav from '../../src/renderer/src/components/layout/NavRail'
import * as registry from '../../src/renderer/src/registry/commandRegistry'
import { CHORD_TABLE } from './fixtures/chord-table'

const UI = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const SHORTCUTS_PATH = resolve(UI, 'src/renderer/src/registry/shortcuts.ts')

/*
  The specifier is held in a variable so Vite's import-analysis cannot resolve it
  at transform time: a literal one makes the missing module a whole-file
  collection error instead of one failing assertion per test (RED_PROOF).
*/
const SHORTCUTS_MODULE = '../../src/renderer/src/registry/shortcuts'

type Entry = registry.CommandRegistryEntry & { page?: string; stateful?: true; palette?: false }

type HandlerOptions = {
  commands: Entry[]
  getPage: () => string | null
  getState: (page: string) => Partial<Record<string, boolean>>
  isPaletteOpen: () => boolean
  closePalette: () => void
}

type ShortcutsModule = {
  normalizeChord: (text: string) => string | null
  chordFromEvent: (event: KeyboardEvent) => string | null
  ariaKeyshortcuts: (chord: string) => string
  RESERVED_CHORDS: ReadonlySet<string>
  buildShortcutMap: (commands: Entry[]) => ReadonlyMap<string, Entry>
  createShortcutHandler: (options: HandlerOptions) => (event: KeyboardEvent) => boolean
  PAGE_PRIMARY_CONTROL?: Record<string, string | null>
}

/** Loads registry/shortcuts.ts; a missing file fails as one assertion (RED_PROOF). */
async function loadShortcuts(): Promise<ShortcutsModule> {
  expect(existsSync(SHORTCUTS_PATH), 'registry/shortcuts.ts exists').toBe(true)
  return (await import(/* @vite-ignore */ SHORTCUTS_MODULE)) as ShortcutsModule
}

/** A keydown as Chromium reports it for `chord` (a letter is lowercase unless Shift is held). */
function keyEvent(chord: string, extra: KeyboardEventInit = {}): KeyboardEvent {
  const parts = chord.endsWith('++') ? [...chord.slice(0, -2).split('+'), '+'] : chord.split('+')
  const raw = parts[parts.length - 1] ?? ''
  const shiftKey = parts.includes('Shift')
  const key = raw === 'Plus' ? '+' : raw.length === 1 && !shiftKey ? raw.toLowerCase() : raw
  return new KeyboardEvent('keydown', {
    key,
    ctrlKey: parts.includes('Ctrl'),
    shiftKey,
    altKey: parts.includes('Alt'),
    bubbles: true,
    cancelable: true,
    ...extra,
  })
}

function fixture(id: string, shortcut: string, extra: Partial<Entry> = {}): Entry {
  return {
    id: id as Entry['id'],
    label: id,
    category: 'navigation',
    keywords: [],
    action: () => undefined,
    shortcut,
    ...extra,
  }
}

function allTrue(commands: Entry[]): Partial<Record<string, boolean>> {
  return Object.fromEntries(commands.map((command) => [command.id, true]))
}

/** A registry entry by id, typed loosely so ids added later still compile. */
function entry(id: string): Entry | undefined {
  return (registry.listCommands() as Entry[]).find((command) => command.id === id)
}

afterEach(() => {
  cleanup()
  document.body.innerHTML = ''
  window.location.hash = ''
})

describe('MEU-95 gui-shortcut-binding', () => {
  it('AC-95.1 CHORD_FORMAT normalizes chords, builds them from events and gives the ARIA form', async () => {
    const sc = await loadShortcuts()
    expect(typeof sc.normalizeChord).toBe('function')
    expect(typeof sc.chordFromEvent).toBe('function')
    expect(typeof sc.ariaKeyshortcuts).toBe('function')
    expect(sc.normalizeChord('ctrl+b')).toBe('Ctrl+B')
    expect(sc.normalizeChord('Meta+1')).toBe('Ctrl+1')
    expect(sc.normalizeChord('Shift+Ctrl+d')).toBe('Ctrl+Shift+D')
    expect(sc.normalizeChord('Ctrl++')).toBe('Ctrl+Plus')
    expect(sc.normalizeChord('Ctrl+,')).toBe('Ctrl+,')
    expect(sc.normalizeChord('f1')).toBe('F1')
    expect(sc.normalizeChord('')).toBeNull()
    expect(sc.normalizeChord('Ctrl+')).toBeNull()
    expect(sc.normalizeChord('Ctrl+Ctrl+A')).toBeNull()
    expect(sc.normalizeChord('Hyper+A')).toBeNull()
    expect(sc.chordFromEvent(new KeyboardEvent('keydown', { key: 'l', ctrlKey: true }))).toBe('Ctrl+L')
    expect(sc.chordFromEvent(new KeyboardEvent('keydown', { key: 'Control', ctrlKey: true }))).toBeNull()
    expect(sc.chordFromEvent(new KeyboardEvent('keydown', { key: 'F1' }))).toBe('F1')
    expect(sc.ariaKeyshortcuts('Ctrl+Shift+D')).toBe('Control+Shift+D')
  })

  it('AC-95.2 SHORTCUT_MAP refuses duplicate, mixed-scope, reserved and invalid chords', async () => {
    const sc = await loadShortcuts()
    expect(typeof sc.buildShortcutMap).toBe('function')
    expect(sc.RESERVED_CHORDS).toBeInstanceOf(Set)
    const refused: Array<[string, Entry[]]> = [
      ['Ctrl+B', [fixture('a:one', 'Ctrl+B'), fixture('a:two', 'Ctrl+B')]],
      ['Ctrl+L', [fixture('a:one', 'Ctrl+L'), fixture('a:two', 'Ctrl+L', { page: '/' })]],
      ['Ctrl+C', [fixture('a:one', 'Ctrl+C')]],
      ['Ctrl+', [fixture('a:one', 'Ctrl+')]],
    ]
    for (const [chord, commands] of refused) {
      expect(() => sc.buildShortcutMap(commands), chord).toThrow(chord)
    }
    const perPage = sc.buildShortcutMap([
      fixture('a:one', 'Ctrl+L', { page: '/' }),
      fixture('a:two', 'Ctrl+L', { page: '/transcript' }),
    ])
    expect(perPage.size).toBe(2)
    const commands = registry.listCommands() as Entry[]
    const map = sc.buildShortcutMap(commands)
    expect(map.size).toBe(commands.filter((command) => command.shortcut).length)
    for (const chord of sc.RESERVED_CHORDS) {
      expect(sc.normalizeChord(chord), chord).toBe(chord)
    }
  })

  it('AC-95.3 every registry chord dispatches its own action and nothing else', async () => {
    const sc = await loadShortcuts()
    expect(typeof sc.createShortcutHandler).toBe('function')
    const base = registry.listCommands() as Entry[]
    const bound = base.filter((command) => command.shortcut)
    expect(bound.length).toBeGreaterThan(0)
    for (const target of bound) {
      const spy = vi.fn()
      const other = vi.fn()
      const commands = base.map((command) => ({
        ...command,
        action: command.id === target.id ? spy : other,
      }))
      const handler = sc.createShortcutHandler({
        commands,
        getPage: () => target.page ?? '/',
        getState: () => allTrue(commands),
        isPaletteOpen: () => false,
        closePalette: () => undefined,
      })
      const event = keyEvent(target.shortcut ?? '')
      expect(handler(event), target.id).toBe(true)
      expect(event.defaultPrevented, target.id).toBe(true)
      expect(spy, target.id).toHaveBeenCalledTimes(1)
      expect(other, target.id).not.toHaveBeenCalled()
    }
    const unbound = sc.createShortcutHandler({
      commands: base,
      getPage: () => '/',
      getState: () => allTrue(base),
      isPaletteOpen: () => false,
      closePalette: () => undefined,
    })
    const ctrlQ = keyEvent('Ctrl+Q')
    expect(unbound(ctrlQ)).toBe(false)
    expect(ctrlQ.defaultPrevented).toBe(false)
  })

  it('AC-95.4 guards: repeat, composition, foreign modals and disabled stateful commands', async () => {
    const sc = await loadShortcuts()
    expect(typeof sc.createShortcutHandler).toBe('function')
    const order: string[] = []
    const commands = [
      fixture('nav:transcript', 'Ctrl+2', { action: () => order.push('action') }),
      fixture('download:start', 'Ctrl+L', { page: '/', stateful: true, action: () => order.push('start') }),
    ]
    let paletteOpen = false
    const handler = sc.createShortcutHandler({
      commands,
      getPage: () => '/',
      getState: () => ({}),
      isPaletteOpen: () => paletteOpen,
      closePalette: () => order.push('close'),
    })
    expect(handler(keyEvent('Ctrl+2', { repeat: true }))).toBe(false)
    expect(handler(keyEvent('Ctrl+2', { isComposing: true }))).toBe(false)
    expect(order).toEqual([])

    const modal = document.createElement('div')
    modal.setAttribute('aria-modal', 'true')
    document.body.appendChild(modal)
    expect(handler(keyEvent('Ctrl+2'))).toBe(false)
    expect(order).toEqual([])
    modal.remove()

    expect(handler(keyEvent('Ctrl+2'))).toBe(true)
    expect(order).toEqual(['action'])
    order.length = 0

    const palette = document.createElement('div')
    palette.setAttribute('aria-modal', 'true')
    palette.setAttribute('data-testid', 'command-palette')
    document.body.appendChild(palette)
    paletteOpen = true
    expect(handler(keyEvent('Ctrl+2'))).toBe(true)
    expect(order).toEqual(['close', 'action'])
    palette.remove()
    paletteOpen = false
    order.length = 0

    const disabled = keyEvent('Ctrl+L')
    expect(handler(disabled)).toBe(false)
    expect(disabled.defaultPrevented).toBe(false)
    expect(order).toEqual([])
  })

  it('AC-95.5 Ctrl chords fire from text fields; field editing keys keep their default', async () => {
    const sc = await loadShortcuts()
    expect(typeof sc.createShortcutHandler).toBe('function')
    const base = registry.listCommands() as Entry[]
    for (const tag of ['input', 'textarea'] as const) {
      const spy = vi.fn()
      const commands = base.map((command) =>
        command.id === 'nav:transcript' ? { ...command, action: spy } : { ...command, action: () => undefined },
      )
      const handler = sc.createShortcutHandler({
        commands,
        getPage: () => '/',
        getState: () => allTrue(commands),
        isPaletteOpen: () => false,
        closePalette: () => undefined,
      })
      const field = document.createElement(tag)
      document.body.appendChild(field)
      field.focus()
      expect(document.activeElement).toBe(field)
      const results: boolean[] = []
      const listener = (event: KeyboardEvent) => {
        results.push(handler(event))
      }
      window.addEventListener('keydown', listener)
      try {
        const ctrl2 = keyEvent('Ctrl+2')
        field.dispatchEvent(ctrl2)
        expect(results.at(-1), tag).toBe(true)
        expect(ctrl2.defaultPrevented, tag).toBe(true)
        expect(spy, tag).toHaveBeenCalledTimes(1)
        for (const chord of ['Ctrl+A', 'Enter']) {
          const event = keyEvent(chord)
          field.dispatchEvent(event)
          expect(results.at(-1), `${tag} ${chord}`).toBe(false)
          expect(event.defaultPrevented, `${tag} ${chord}`).toBe(false)
        }
      } finally {
        window.removeEventListener('keydown', listener)
        field.remove()
      }
    }
    const keys = [...sc.buildShortcutMap(base).keys()]
    for (const editing of ['Enter@', 'Ctrl+A@', 'Ctrl+C@', 'Ctrl+V@', 'Ctrl+X@', 'Ctrl+Z@']) {
      expect(keys.filter((key) => key.startsWith(editing)), editing).toEqual([])
    }
  })

  it('AC-95.7 NAV_HINTS: every rail item shows its registry chord in both rail states', async () => {
    for (const collapsed of [false, true]) {
      render(createElement(nav.NavRail, { collapsed }))
      for (const item of nav.SHELL_NAV) {
        expect(registry.getCommand(item.id)?.shortcut, item.id).toBe(item.shortcut)
        const button = screen.getByTestId(item.testid)
        expect(button.getAttribute('title') ?? '', `${item.id} collapsed=${collapsed}`).toContain(item.shortcut)
      }
      cleanup()
    }
    const sc = await loadShortcuts()
    expect(typeof sc.ariaKeyshortcuts).toBe('function')
    for (const collapsed of [false, true]) {
      render(createElement(nav.NavRail, { collapsed }))
      for (const item of nav.SHELL_NAV) {
        const button = screen.getByTestId(item.testid)
        expect(button.getAttribute('aria-keyshortcuts'), `${item.id} collapsed=${collapsed}`).toBe(
          sc.ariaKeyshortcuts(item.shortcut),
        )
      }
      cleanup()
    }
  })
})

const PAGE_PRIMARY: Record<string, string | null> = {
  '/': 'add-btn',
  '/transcript': 'add-btn',
  '/tts': 'generate-btn',
  '/convert': 'convert-add',
  '/capture': 'capture-region',
  '/settings': null,
}

describe('MEU-97 gui-common-shortcuts', () => {
  it('AC-97.1 CHORD_TABLE: every chord and page is in the registry, and the map builds without a reserved key', async () => {
    const sc = await loadShortcuts()
    expect(typeof sc.buildShortcutMap).toBe('function')
    for (const [id, chord, page] of CHORD_TABLE) {
      const command = entry(id)
      expect(command, id).toBeDefined()
      expect(sc.normalizeChord(command?.shortcut ?? ''), id).toBe(chord)
      expect(command?.page, id).toBe(page)
    }
    const map = sc.buildShortcutMap(registry.listCommands() as Entry[])
    for (const key of map.keys()) {
      for (const banned of ['F2', 'Ctrl+=', 'Ctrl+-', 'Ctrl+0', 'Ctrl+Plus']) {
        expect(key.startsWith(`${banned}@`), key).toBe(false)
      }
    }
    expect(() => sc.buildShortcutMap([fixture('a:one', 'Ctrl+=')])).toThrow('Ctrl+=')
  })

  it('AC-97.2 PAGE_PRIMARY: page:primary clicks the enabled primary button of the current page and nothing else', async () => {
    const sc = await loadShortcuts()
    expect(sc.PAGE_PRIMARY_CONTROL, 'PAGE_PRIMARY_CONTROL').toEqual(PAGE_PRIMARY)
    const primary = entry('page:primary')
    expect(primary, 'page:primary').toBeDefined()
    expect(primary?.palette).toBe(false)
    expect(primary?.page).toBeUndefined()
    const testids = [...new Set(Object.values(PAGE_PRIMARY).filter((id): id is string => id !== null))]
    for (const [page, testid] of Object.entries(PAGE_PRIMARY)) {
      window.location.hash = `#${page}`
      for (const disabled of [false, true]) {
        document.body.innerHTML = ''
        const clicks: string[] = []
        for (const id of testids) {
          const button = document.createElement('button')
          button.setAttribute('data-testid', id)
          button.disabled = disabled
          button.addEventListener('click', () => clicks.push(id))
          document.body.appendChild(button)
        }
        primary?.action()
        const expected = testid !== null && !disabled ? [testid] : []
        expect(clicks, `${page} disabled=${disabled}`).toEqual(expected)
      }
    }
  })

  it('AC-97.3 page scope: a page chord does nothing on another page, and Ctrl+S follows the capture:save state', async () => {
    const sc = await loadShortcuts()
    expect(typeof sc.createShortcutHandler).toBe('function')
    const ran: string[] = []
    const commands = (registry.listCommands() as Entry[]).map((command) => ({
      ...command,
      action: () => {
        ran.push(command.id)
      },
    }))
    let page = '/'
    let state: Partial<Record<string, boolean>> = {}
    const handler = sc.createShortcutHandler({
      commands,
      getPage: () => page,
      getState: () => state,
      isPaletteOpen: () => false,
      closePalette: () => undefined,
    })
    for (const [chord, where] of [
      ['Ctrl+L', '/convert'],
      ['Ctrl+O', '/'],
      ['Ctrl+S', '/tts'],
    ] as const) {
      page = where
      const event = keyEvent(chord)
      expect(handler(event), `${chord} on ${where}`).toBe(false)
      expect(event.defaultPrevented, `${chord} on ${where}`).toBe(false)
    }
    page = '/capture'
    state = { 'capture:save': false }
    const closed = keyEvent('Ctrl+S')
    expect(handler(closed), 'Ctrl+S with capture:save false').toBe(false)
    expect(closed.defaultPrevented).toBe(false)
    state = { 'capture:save': true }
    expect(handler(keyEvent('Ctrl+S')), 'Ctrl+S with capture:save true').toBe(true)
    expect(ran).toEqual(['capture:save'])
  })
})
