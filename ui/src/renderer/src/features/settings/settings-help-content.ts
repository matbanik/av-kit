import type { HelpSection } from '../../components/help/HelpCard'

export const SETTINGS_HELP_SECTIONS: HelpSection[] = [
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
    body: 'Start when I sign in adds a startup entry for your user only. It needs no administrator approval. Turn it off here or in Task Manager → Startup. Start minimized waits in the notification area, so F2 still works.',
  },
]
