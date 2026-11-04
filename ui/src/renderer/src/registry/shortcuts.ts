import type { CommandRegistryEntry } from './commandRegistry'

/** The six routed shell pages (06 §Shortcut binding; `navigateShell` sets the hash). */
export type ShellPage = '/' | '/transcript' | '/tts' | '/convert' | '/capture' | '/settings'

const SHELL_PAGES: readonly ShellPage[] = ['/', '/transcript', '/tts', '/convert', '/capture', '/settings']

/** Each page's primary-variant button, which `page:primary` (Ctrl+Enter) presses (PAGE_PRIMARY, D-146). */
export const PAGE_PRIMARY_CONTROL: Record<ShellPage, string | null> = {
  '/': 'add-btn',
  '/transcript': 'add-btn',
  '/tts': 'generate-btn',
  '/convert': 'convert-add',
  '/capture': 'capture-region',
  '/settings': null,
}

/**
 * Every rendered control a chord performs (HINTS, D-147). Each carries `aria-keyshortcuts`
 * and shows its chord. `header-palette-btn` is not here: Ctrl+K is shell-owned.
 */
export const BOUND_CONTROLS: ReadonlyArray<{ testid: string; commandId: string }> = [
  { testid: 'nav-downloader', commandId: 'nav:downloader' },
  { testid: 'nav-transcript', commandId: 'nav:transcript' },
  { testid: 'nav-tts', commandId: 'nav:tts' },
  { testid: 'nav-convert', commandId: 'nav:convert' },
  { testid: 'nav-capture', commandId: 'nav:capture' },
  { testid: 'nav-settings', commandId: 'nav:settings' },
  { testid: 'nav-collapse', commandId: 'nav:collapse' },
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

/** The routed page from `window.location.hash`, or `null` for any other path. */
export function currentShellPage(): ShellPage | null {
  const path = window.location.hash.replace(/^#/, '').split('?')[0] ?? ''
  const page = path === '' ? '/' : path
  return SHELL_PAGES.find((candidate) => candidate === page) ?? null
}

const MODIFIERS: Record<string, 'Ctrl' | 'Shift' | 'Alt'> = {
  ctrl: 'Ctrl',
  control: 'Ctrl',
  meta: 'Ctrl',
  cmd: 'Ctrl',
  shift: 'Shift',
  alt: 'Alt',
}

const NAMED_KEYS = ['Plus', 'Enter', 'Escape', ...Array.from({ length: 12 }, (_, i) => `F${i + 1}`)]

function normalizeKey(raw: string): string | null {
  if (raw === '+') {
    return 'Plus'
  }
  if (raw.length === 1) {
    if (/^[a-z]$/i.test(raw)) {
      return raw.toUpperCase()
    }
    return /^[0-9,=-]$/.test(raw) ? raw : null
  }
  return NAMED_KEYS.find((name) => name.toLowerCase() === raw.toLowerCase()) ?? null
}

function joinChord(mods: ReadonlySet<string>, key: string): string {
  return [...['Ctrl', 'Shift', 'Alt'].filter((mod) => mods.has(mod)), key].join('+')
}

/**
 * The canonical chord (CHORD_FORMAT): `Ctrl+`, `Shift+`, `Alt+` in that order, then
 * the key. `Meta`, `Cmd` and `Control` count as `Ctrl`; a trailing `+` is the key
 * `Plus`. A key-less chord, an unknown key or a repeated modifier gives `null`.
 */
export function normalizeChord(text: string): string | null {
  const parts = text.endsWith('++') ? [...text.slice(0, -2).split('+'), '+'] : text.split('+')
  const key = normalizeKey(parts.pop() ?? '')
  if (key === null) {
    return null
  }
  const mods = new Set<string>()
  for (const part of parts) {
    const mod = MODIFIERS[part.toLowerCase()]
    if (mod === undefined || mods.has(mod)) {
      return null
    }
    mods.add(mod)
  }
  return joinChord(mods, key)
}

const BARE_MODIFIER_KEYS = new Set(['Control', 'Shift', 'Alt', 'Meta', 'AltGraph', 'OS'])

/** The canonical chord a keydown spells, or `null` for a bare modifier or an unknown key. */
export function chordFromEvent(event: KeyboardEvent): string | null {
  if (BARE_MODIFIER_KEYS.has(event.key)) {
    return null
  }
  const key = normalizeKey(event.key)
  if (key === null) {
    return null
  }
  const mods = new Set<string>()
  if (event.ctrlKey || event.metaKey) mods.add('Ctrl')
  if (event.shiftKey) mods.add('Shift')
  if (event.altKey) mods.add('Alt')
  return joinChord(mods, key)
}

/** The WAI-ARIA `aria-keyshortcuts` form of a canonical chord (`Ctrl` → `Control`, `Plus` → `+`). */
export function ariaKeyshortcuts(chord: string): string {
  const parts = chord.split('+')
  return parts.map((part) => (part === 'Ctrl' ? 'Control' : part === 'Plus' ? '+' : part)).join('+')
}

/**
 * Chords no registry entry may take (D-136): the Electron default menu's Windows
 * accelerators, Capture's F2 hotkey (its zoom keys are in the menu set), the
 * shell-owned palette opener and a text field's plain Enter.
 * Capture handles Ctrl+Z, Ctrl+Y and Ctrl+Shift+Z itself while its image has focus (D-163); they stay
 * reserved so no registry entry takes them.
 */
export const RESERVED_CHORDS: ReadonlySet<string> = new Set([
  'Ctrl+Z',
  'Ctrl+Y',
  'Ctrl+Shift+Z',
  'Ctrl+X',
  'Ctrl+C',
  'Ctrl+V',
  'Ctrl+A',
  'Ctrl+R',
  'Ctrl+Shift+R',
  'Ctrl+Shift+I',
  'Ctrl+0',
  'Ctrl+=',
  'Ctrl+Plus',
  'Ctrl+Shift+Plus',
  'Ctrl+-',
  'F11',
  'Ctrl+M',
  'Ctrl+W',
  'F2',
  'Ctrl+K',
  'Enter',
])

/**
 * One map from the registry's `shortcut` fields (SHORTCUT_MAP), keyed
 * `${chord}@${page ?? '*'}`. Throws on an invalid, reserved or duplicate chord, or a
 * chord used both globally and on a page; the same chord on two pages is allowed.
 */
export function buildShortcutMap(
  commands: readonly CommandRegistryEntry[],
): ReadonlyMap<string, CommandRegistryEntry> {
  const map = new Map<string, CommandRegistryEntry>()
  for (const command of commands) {
    if (command.shortcut === undefined) {
      continue
    }
    const chord = normalizeChord(command.shortcut)
    if (chord === null) {
      throw new Error(`${command.id}: invalid chord ${command.shortcut}`)
    }
    if (RESERVED_CHORDS.has(chord)) {
      throw new Error(`${command.id}: ${chord} is reserved`)
    }
    const key = `${chord}@${command.page ?? '*'}`
    const clash =
      map.get(key) ??
      (command.page === undefined
        ? [...map.entries()].find(([other]) => other.startsWith(`${chord}@`))?.[1]
        : map.get(`${chord}@*`))
    if (clash !== undefined) {
      throw new Error(`${clash.id} and ${command.id} both take ${chord}`)
    }
    map.set(key, command)
  }
  return map
}

export type ShortcutHandlerOptions = {
  commands: readonly CommandRegistryEntry[]
  getPage: () => ShellPage | null
  getState: (page: ShellPage) => Partial<Record<string, boolean>>
  isPaletteOpen: () => boolean
  closePalette: () => void
}

/** Any open modal other than the palette suspends chords (MODAL_GUARD, D-134). */
function foreignModalOpen(): boolean {
  return [...document.querySelectorAll('[aria-modal="true"]')].some(
    (element) => !element.matches('[data-testid="command-palette"]'),
  )
}

/**
 * The window keydown handler (SHORTCUT_HANDLER). It returns `true` when it ran a
 * registry command. The focused element is ignored, so Ctrl and F-key chords fire
 * from text fields; field editing keys are reserved and never bound.
 */
export function createShortcutHandler(options: ShortcutHandlerOptions): (event: KeyboardEvent) => boolean {
  const map = buildShortcutMap(options.commands)
  return (event) => {
    if (event.repeat || event.isComposing) {
      return false
    }
    const chord = chordFromEvent(event)
    if (chord === null || foreignModalOpen()) {
      return false
    }
    const page = options.getPage()
    const entry = (page === null ? undefined : map.get(`${chord}@${page}`)) ?? map.get(`${chord}@*`)
    if (entry === undefined) {
      return false
    }
    if (entry.stateful && (page === null || options.getState(page)[entry.id] !== true)) {
      return false
    }
    event.preventDefault()
    if (options.isPaletteOpen()) {
      options.closePalette()
    }
    entry.action()
    return true
  }
}

/**
 * The commands the palette lists (PALETTE_LIST, D-137): never `palette: false`;
 * only global entries and the current page's own; a stateful entry only while its
 * page publishes it enabled; resume folded into pause when both survive. The
 * page's entries come first, each part in registry order.
 */
export function paletteCommands(
  commands: readonly CommandRegistryEntry[],
  page: ShellPage | null,
  state: Partial<Record<string, boolean>>,
): CommandRegistryEntry[] {
  const listed = commands.filter(
    (command) =>
      command.palette !== false &&
      (command.page === undefined || command.page === page) &&
      (!command.stateful || state[command.id] === true),
  )
  const ids = new Set<string>(listed.map((command) => command.id))
  const folded = listed.filter((command) => {
    const feature = /^(.+):resume$/.exec(command.id)?.[1]
    return feature === undefined || !ids.has(`${feature}:pause`)
  })
  return [
    ...folded.filter((command) => command.page !== undefined),
    ...folded.filter((command) => command.page === undefined),
  ]
}
