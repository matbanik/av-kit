import { DOWNLOAD_EVENTS } from '../features/downloader/download-commands'
import { TRANSCRIPT_EVENTS } from '../features/transcript/transcript-commands'
import { navigateShell, requestCollapseRail, TOGGLE_CONSOLE_EVENT } from '../lib/shell-nav'

export const CONSOLE_PALETTE_ID = 'console:toggle' as const

export const SHELL_PALETTE_IDS = [
  'nav:downloader',
  'nav:transcript',
  'nav:tts',
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

export type CommandRegistryEntry = {
  id:
    | (typeof SHELL_PALETTE_IDS)[number]
    | (typeof DOWNLOAD_PALETTE_IDS)[number]
    | (typeof TRANSCRIPT_PALETTE_IDS)[number]
  label: string
  category: 'navigation' | 'download' | 'transcript'
  keywords: string[]
  action: () => void
  shortcut?: string
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
    label: 'Collapse rail',
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
    action: () => {
      window.dispatchEvent(new CustomEvent(TOGGLE_CONSOLE_EVENT))
    },
  },
  {
    id: 'download:add',
    label: 'Focus download URL',
    category: 'download',
    keywords: ['add', 'url'],
    action: () => {
      window.dispatchEvent(new CustomEvent(DOWNLOAD_EVENTS.add))
    },
  },
  {
    id: 'download:start',
    label: 'Start downloads',
    category: 'download',
    keywords: ['start'],
    action: () => {
      window.dispatchEvent(new CustomEvent(DOWNLOAD_EVENTS.start))
    },
  },
  {
    id: 'download:pause',
    label: 'Pause downloads',
    category: 'download',
    keywords: ['pause'],
    action: () => {
      window.dispatchEvent(new CustomEvent(DOWNLOAD_EVENTS.pause))
    },
  },
  {
    id: 'download:resume',
    label: 'Resume downloads',
    category: 'download',
    keywords: ['resume'],
    action: () => {
      window.dispatchEvent(new CustomEvent(DOWNLOAD_EVENTS.resume))
    },
  },
  {
    id: 'download:cancel',
    label: 'Cancel downloads',
    category: 'download',
    keywords: ['cancel'],
    action: () => {
      window.dispatchEvent(new CustomEvent(DOWNLOAD_EVENTS.cancel))
    },
  },
  {
    id: 'download:clear',
    label: 'Clear download queue',
    category: 'download',
    keywords: ['clear'],
    action: () => {
      window.dispatchEvent(new CustomEvent(DOWNLOAD_EVENTS.clear))
    },
  },
  {
    id: 'download:sabr_check',
    label: 'Check SABR',
    category: 'download',
    keywords: ['sabr'],
    action: () => {
      window.dispatchEvent(new CustomEvent(DOWNLOAD_EVENTS.sabrCheck))
    },
  },
  {
    id: 'transcript:add',
    label: 'Focus transcript channel URL',
    category: 'transcript',
    keywords: ['add', 'channel', 'transcript'],
    action: () => {
      window.dispatchEvent(new CustomEvent(TRANSCRIPT_EVENTS.add))
    },
  },
  {
    id: 'transcript:start',
    label: 'Start transcripts',
    category: 'transcript',
    keywords: ['start', 'transcript'],
    action: () => {
      window.dispatchEvent(new CustomEvent(TRANSCRIPT_EVENTS.start))
    },
  },
  {
    id: 'transcript:pause',
    label: 'Pause transcripts',
    category: 'transcript',
    keywords: ['pause', 'transcript'],
    action: () => {
      window.dispatchEvent(new CustomEvent(TRANSCRIPT_EVENTS.pause))
    },
  },
  {
    id: 'transcript:resume',
    label: 'Resume transcripts',
    category: 'transcript',
    keywords: ['resume', 'transcript'],
    action: () => {
      window.dispatchEvent(new CustomEvent(TRANSCRIPT_EVENTS.resume))
    },
  },
  {
    id: 'transcript:stop',
    label: 'Stop transcripts',
    category: 'transcript',
    keywords: ['stop', 'transcript'],
    action: () => {
      window.dispatchEvent(new CustomEvent(TRANSCRIPT_EVENTS.stop))
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
