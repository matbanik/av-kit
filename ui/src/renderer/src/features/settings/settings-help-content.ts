import type { HelpSection } from '../../components/help/HelpCard'
import { CAPTURE_KEY_DEFAULT, captureKeyText } from '../capture/capture-key'

/** The topics with the `{captureKey}` token (CAPTURE_KEY_TOKEN); the readers below resolve it. */
const SETTINGS_HELP_TEMPLATES: HelpSection[] = [
  {
    id: 'leaf-keys',
    title: 'How each card saves',
    body: 'Each card shows how it saves next to its name. Most cards save as you type. Convert and Capture need Save. Appearance applies at once. A change on one card does not change a different card.',
  },
  {
    id: 'ffmpeg',
    title: 'Check FFmpeg',
    body: 'Browse to FFmpeg, then click Check dependencies. Do this before you run media jobs.',
  },
  {
    id: 'mcp',
    title: 'MCP setup',
    body: 'Copy the MCP setup for your client. The app shows only if a token exists. It never shows the token.',
  },
  {
    id: 'console',
    title: 'Console and logging',
    body: 'Set Log level, Log to file and Console visible on the Console card. Errors are always written to console.log in the logs folder of the app data. Log to file adds every other line. You cannot change that path. Open the Console panel from the header.',
  },
  {
    id: 'startup',
    title: 'Start with Windows',
    body: 'Start when I sign in adds a startup entry for your user only. It needs no administrator approval. Turn it off here or in Task Manager → Startup. Start minimized waits in the notification area, so {captureKey} still works.',
  },
]

/** CAPTURE_KEY_DEFAULT_READING (MEU-165): the topics with the given capture key. */
export function settingsHelpSections(key: string): HelpSection[] {
  return SETTINGS_HELP_TEMPLATES.map((section) => ({
    ...section,
    title: captureKeyText(section.title, key),
    body: captureKeyText(section.body, key),
  }))
}

/** The topics with the default key, as they read before MEU-165. */
export const SETTINGS_HELP_SECTIONS: HelpSection[] = settingsHelpSections(CAPTURE_KEY_DEFAULT)
