import { setAppearance } from './appearance'
import { buildShortcutMap, chordFromEvent, currentShellPage, PAGE_PRIMARY_CONTROL, type ShellPage } from './shortcuts'
import { CAPTURE_EVENTS } from '../features/capture/capture-commands'
import { CONVERT_EVENTS, deliverPaletteBrowse } from '../features/converter/convert-commands'
import { DOWNLOAD_EVENTS } from '../features/downloader/download-commands'
import { HELP_EVENTS, SETTINGS_EVENTS } from '../features/settings/settings-commands'
import { TRANSCRIPT_EVENTS } from '../features/transcript/transcript-commands'
import { TTS_EVENTS } from '../features/tts/tts-commands'
import { navigateShell, requestCollapseRail, TOGGLE_CONSOLE_EVENT } from '../lib/shell-nav'

export const CONSOLE_PALETTE_ID = 'console:toggle' as const

export const SHELL_PALETTE_IDS = [
  'nav:downloader',
  'nav:transcript',
  'nav:tts',
  'nav:convert',
  'nav:capture',
  'nav:settings',
  'nav:collapse',
  CONSOLE_PALETTE_ID,
] as const

export const DOWNLOAD_PALETTE_IDS = [
  'download:add',
  'download:start',
  'download:pause',
  'download:resume',
  'download:cancel',
  'download:clear',
  'download:sabr_check',
] as const

export const TRANSCRIPT_PALETTE_IDS = [
  'transcript:add',
  'transcript:start',
  'transcript:pause',
  'transcript:resume',
  'transcript:stop',
] as const

export const TTS_PALETTE_IDS = ['tts:prepare', 'tts:generate'] as const

export const CONVERT_PALETTE_IDS = [
  'convert:add',
  'convert:browse',
  'convert:start',
  'convert:pause',
  'convert:resume',
  'convert:cancel',
  'convert:clear',
] as const

export const CAPTURE_PALETTE_IDS = [
  'nav:capture',
  'capture:region',
  'capture:save',
  'capture:open_folder',
] as const

export const SETTINGS_PALETTE_IDS = ['settings:check_deps'] as const

export const APPEARANCE_PALETTE_IDS = ['appearance:dark', 'appearance:light'] as const

export const HELP_PALETTE_IDS = ['help:toggle'] as const

/** Chord-only commands (`palette: false`). */
export const SHORTCUT_ONLY_IDS = ['page:primary'] as const

export type CommandRegistryEntry = {
  id:
    | (typeof SHELL_PALETTE_IDS)[number]
    | (typeof DOWNLOAD_PALETTE_IDS)[number]
    | (typeof TRANSCRIPT_PALETTE_IDS)[number]
    | (typeof TTS_PALETTE_IDS)[number]
    | (typeof CONVERT_PALETTE_IDS)[number]
    | (typeof CAPTURE_PALETTE_IDS)[number]
    | (typeof SETTINGS_PALETTE_IDS)[number]
    | (typeof APPEARANCE_PALETTE_IDS)[number]
    | (typeof HELP_PALETTE_IDS)[number]
    | (typeof SHORTCUT_ONLY_IDS)[number]
  label: string
  category:
    | 'navigation'
    | 'download'
    | 'transcript'
    | 'tts'
    | 'convert'
    | 'capture'
    | 'settings'
    | 'appearance'
    | 'help'
  keywords: string[]
  action: () => void
  shortcut?: string
  /** The page that owns the command (AVAILABILITY). */
  page?: ShellPage
  /** Runs only when its page publishes it enabled (AVAILABILITY). */
  stateful?: true
  /** Never listed in the palette (AVAILABILITY). */
  palette?: false
}

const commands: CommandRegistryEntry[] = [
  {
    id: 'nav:downloader',
    label: 'Downloader',
    category: 'navigation',
    keywords: ['download', 'home'],
    shortcut: 'Ctrl+1',
    action: () => {
      navigateShell('/')
    },
  },
  {
    id: 'nav:transcript',
    label: 'Transcript',
    category: 'navigation',
    keywords: ['transcript'],
    shortcut: 'Ctrl+2',
    action: () => {
      navigateShell('/transcript')
    },
  },
  {
    id: 'nav:tts',
    label: 'TTS',
    category: 'navigation',
    keywords: ['tts', 'speech'],
    shortcut: 'Ctrl+3',
    action: () => {
      navigateShell('/tts')
    },
  },
  {
    id: 'nav:convert',
    label: 'Convert',
    category: 'navigation',
    keywords: ['convert', 'ffmpeg', 'compress'],
    shortcut: 'Ctrl+4',
    action: () => {
      navigateShell('/convert')
    },
  },
  {
    id: 'nav:capture',
    label: 'Capture',
    category: 'navigation',
    keywords: ['capture', 'screenshot'],
    shortcut: 'Ctrl+5',
    action: () => {
      navigateShell('/capture')
    },
  },
  {
    id: 'nav:settings',
    label: 'Settings',
    category: 'navigation',
    keywords: ['settings'],
    shortcut: 'Ctrl+,',
    action: () => {
      navigateShell('/settings')
    },
  },
  {
    id: 'nav:collapse',
    label: 'Toggle sidebar',
    category: 'navigation',
    keywords: ['collapse', 'rail'],
    shortcut: 'Ctrl+B',
    action: () => {
      requestCollapseRail()
    },
  },
  {
    id: CONSOLE_PALETTE_ID,
    label: 'Toggle console',
    category: 'navigation',
    keywords: ['console', 'logs'],
    shortcut: 'Ctrl+J',
    action: () => {
      window.dispatchEvent(new CustomEvent(TOGGLE_CONSOLE_EVENT))
    },
  },
  {
    id: 'download:add',
    label: 'Enter download URL',
    category: 'download',
    page: '/',
    keywords: ['add', 'url'],
    shortcut: 'Ctrl+L',
    action: () => {
      window.dispatchEvent(new CustomEvent(DOWNLOAD_EVENTS.add))
    },
  },
  {
    id: 'download:start',
    label: 'Start downloads',
    category: 'download',
    page: '/',
    stateful: true,
    keywords: ['start'],
    action: () => {
      window.dispatchEvent(new CustomEvent(DOWNLOAD_EVENTS.start))
    },
  },
  {
    id: 'download:pause',
    label: 'Pause downloads',
    category: 'download',
    page: '/',
    stateful: true,
    keywords: ['pause'],
    action: () => {
      window.dispatchEvent(new CustomEvent(DOWNLOAD_EVENTS.pause))
    },
  },
  {
    id: 'download:resume',
    label: 'Resume downloads',
    category: 'download',
    page: '/',
    stateful: true,
    keywords: ['resume'],
    action: () => {
      window.dispatchEvent(new CustomEvent(DOWNLOAD_EVENTS.resume))
    },
  },
  {
    id: 'download:cancel',
    label: 'Cancel downloads',
    category: 'download',
    page: '/',
    stateful: true,
    keywords: ['cancel'],
    action: () => {
      window.dispatchEvent(new CustomEvent(DOWNLOAD_EVENTS.cancel))
    },
  },
  {
    id: 'download:clear',
    label: 'Clear download queue',
    category: 'download',
    page: '/',
    stateful: true,
    keywords: ['clear'],
    action: () => {
      window.dispatchEvent(new CustomEvent(DOWNLOAD_EVENTS.clear))
    },
  },
  {
    id: 'download:sabr_check',
    label: 'Check YouTube quality limit',
    category: 'download',
    page: '/',
    keywords: ['sabr', 'quality', 'youtube'],
    action: () => {
      window.dispatchEvent(new CustomEvent(DOWNLOAD_EVENTS.sabrCheck))
    },
  },
  {
    id: 'transcript:add',
    label: 'Enter transcript channel URL',
    category: 'transcript',
    page: '/transcript',
    keywords: ['add', 'channel', 'transcript'],
    shortcut: 'Ctrl+L',
    action: () => {
      window.dispatchEvent(new CustomEvent(TRANSCRIPT_EVENTS.add))
    },
  },
  {
    id: 'transcript:start',
    label: 'Start transcripts',
    category: 'transcript',
    page: '/transcript',
    stateful: true,
    keywords: ['start', 'transcript'],
    action: () => {
      window.dispatchEvent(new CustomEvent(TRANSCRIPT_EVENTS.start))
    },
  },
  {
    id: 'transcript:pause',
    label: 'Pause transcripts',
    category: 'transcript',
    page: '/transcript',
    stateful: true,
    keywords: ['pause', 'transcript'],
    action: () => {
      window.dispatchEvent(new CustomEvent(TRANSCRIPT_EVENTS.pause))
    },
  },
  {
    id: 'transcript:resume',
    label: 'Resume transcripts',
    category: 'transcript',
    page: '/transcript',
    stateful: true,
    keywords: ['resume', 'transcript'],
    action: () => {
      window.dispatchEvent(new CustomEvent(TRANSCRIPT_EVENTS.resume))
    },
  },
  {
    id: 'transcript:stop',
    label: 'Stop transcripts',
    category: 'transcript',
    page: '/transcript',
    stateful: true,
    keywords: ['stop', 'transcript'],
    action: () => {
      window.dispatchEvent(new CustomEvent(TRANSCRIPT_EVENTS.stop))
    },
  },
  {
    id: 'tts:prepare',
    label: 'Preview cleaned text',
    category: 'tts',
    page: '/tts',
    stateful: true,
    keywords: ['prepare', 'tts', 'cleanup'],
    action: () => {
      window.dispatchEvent(new CustomEvent(TTS_EVENTS.prepare))
    },
  },
  {
    id: 'tts:generate',
    label: 'Generate TTS',
    category: 'tts',
    page: '/tts',
    stateful: true,
    keywords: ['generate', 'tts', 'speech'],
    action: () => {
      window.dispatchEvent(new CustomEvent(TTS_EVENTS.generate))
    },
  },
  {
    id: 'convert:add',
    label: 'Add conversion files',
    category: 'convert',
    page: '/convert',
    keywords: ['add', 'convert', 'drop'],
    action: () => {
      window.dispatchEvent(new CustomEvent(CONVERT_EVENTS.add))
    },
  },
  {
    id: 'convert:browse',
    label: 'Browse files',
    category: 'convert',
    page: '/convert',
    keywords: ['browse', 'convert', 'files', 'open'],
    shortcut: 'Ctrl+O',
    action: () => {
      deliverPaletteBrowse()
    },
  },
  {
    id: 'convert:start',
    label: 'Start conversions',
    category: 'convert',
    page: '/convert',
    stateful: true,
    keywords: ['start', 'convert'],
    action: () => {
      window.dispatchEvent(new CustomEvent(CONVERT_EVENTS.start))
    },
  },
  {
    id: 'convert:pause',
    label: 'Pause conversions',
    category: 'convert',
    page: '/convert',
    stateful: true,
    keywords: ['pause', 'convert'],
    action: () => {
      window.dispatchEvent(new CustomEvent(CONVERT_EVENTS.pause))
    },
  },
  {
    id: 'convert:resume',
    label: 'Resume conversions',
    category: 'convert',
    page: '/convert',
    stateful: true,
    keywords: ['resume', 'convert'],
    action: () => {
      window.dispatchEvent(new CustomEvent(CONVERT_EVENTS.resume))
    },
  },
  {
    id: 'convert:cancel',
    label: 'Cancel conversions',
    category: 'convert',
    page: '/convert',
    stateful: true,
    keywords: ['cancel', 'convert'],
    action: () => {
      window.dispatchEvent(new CustomEvent(CONVERT_EVENTS.cancel))
    },
  },
  {
    id: 'convert:clear',
    label: 'Clear conversion queue',
    category: 'convert',
    page: '/convert',
    stateful: true,
    keywords: ['clear', 'convert'],
    action: () => {
      window.dispatchEvent(new CustomEvent(CONVERT_EVENTS.clear))
    },
  },
  {
    id: 'capture:region',
    label: 'Capture region',
    category: 'capture',
    page: '/capture',
    keywords: ['capture', 'region', 'screenshot'],
    action: () => {
      window.dispatchEvent(new CustomEvent(CAPTURE_EVENTS.region))
    },
  },
  {
    id: 'capture:save',
    label: 'Save annotated capture',
    category: 'capture',
    page: '/capture',
    stateful: true,
    keywords: ['capture', 'save', 'annotate'],
    shortcut: 'Ctrl+S',
    action: () => {
      window.dispatchEvent(new CustomEvent(CAPTURE_EVENTS.save))
    },
  },
  {
    id: 'capture:open_folder',
    label: 'Open capture folder',
    category: 'capture',
    page: '/capture',
    keywords: ['capture', 'folder', 'inbox'],
    action: () => {
      window.dispatchEvent(new CustomEvent(CAPTURE_EVENTS.open_folder))
    },
  },
  {
    id: 'settings:check_deps',
    label: 'Check dependencies',
    category: 'settings',
    keywords: ['dependencies', 'ffmpeg', 'yt-dlp'],
    action: () => {
      // CHECK_DEPS_ROUTE: open Settings first, then fire after two frames.
      if (currentShellPage() !== '/settings') {
        navigateShell('/settings')
      }
      window.requestAnimationFrame(() => {
        window.requestAnimationFrame(() => {
          window.dispatchEvent(new CustomEvent(SETTINGS_EVENTS.checkDeps))
        })
      })
    },
  },
  {
    id: 'appearance:dark',
    label: 'Appearance: Dark',
    category: 'appearance',
    keywords: ['theme', 'appearance', 'dark'],
    shortcut: 'Ctrl+Shift+D',
    action: () => {
      setAppearance('dark')
    },
  },
  {
    id: 'appearance:light',
    label: 'Appearance: Light',
    category: 'appearance',
    keywords: ['theme', 'appearance', 'light'],
    shortcut: 'Ctrl+Shift+L',
    action: () => {
      setAppearance('light')
    },
  },
  {
    id: 'help:toggle',
    label: 'Toggle help',
    category: 'help',
    keywords: ['help', 'guide'],
    shortcut: 'F1',
    action: () => {
      window.dispatchEvent(new CustomEvent(HELP_EVENTS.toggle))
    },
  },
  {
    id: 'page:primary',
    label: 'Run page action',
    category: 'navigation',
    keywords: [],
    shortcut: 'Ctrl+Enter',
    palette: false,
    action: () => {
      // PAGE_PRIMARY: press the current page's primary button only while it is enabled.
      const page = currentShellPage()
      const testid = page === null ? null : PAGE_PRIMARY_CONTROL[page]
      const control = testid === null ? null : document.querySelector(`[data-testid="${testid}"]`)
      if (control instanceof HTMLButtonElement && !control.disabled) {
        control.click()
      }
    },
  },
]

export function listPaletteIds(): string[] {
  return commands.map((command) => command.id)
}

export function listCommands(): CommandRegistryEntry[] {
  return [...commands]
}

export function getCommand(id: string): CommandRegistryEntry | undefined {
  return commands.find((command) => command.id === id)
}

let registryChords: ReadonlySet<string> | null = null

/**
 * Whether a keydown spells a chord some registry entry binds, on any page. A focused
 * surface that contains its own keys lets these through to the shell (CAPTURE_CHORD_BUBBLE).
 */
export function isRegistryChord(event: KeyboardEvent): boolean {
  const chord = chordFromEvent(event)
  if (chord === null) {
    return false
  }
  registryChords ??= new Set([...buildShortcutMap(commands).keys()].map((key) => key.slice(0, key.lastIndexOf('@'))))
  return registryChords.has(chord)
}
