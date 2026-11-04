import type { HelpSection } from '../../components/help/HelpCard'

export const SETTINGS_HELP_SECTIONS: HelpSection[] = [
  {
    id: 'leaf-keys',
    title: 'Leaf settings keys',
    body: 'Each card saves individual leaf keys with PUT /settings/{namespace}. Bodies never use dotted paths like namespace plus leaf joined by a dot.',
  },
  {
    id: 'ffmpeg',
    title: 'FFmpeg probe',
    body: 'Browse to your FFmpeg binary and check dependencies to confirm ffmpeg.available before running media jobs.',
  },
  {
    id: 'mcp',
    title: 'MCP access',
    body: 'Copy MCP config to clipboard or pin the API base. Token presence is shown as yes/no — the secret is never displayed.',
  },
  {
    id: 'console',
    title: 'Console and logging',
    body: 'Set log_level, log_to_file, and console_visible under app settings. File persist writes to {app_data}/logs/console.log — that path is not configurable. Open the console panel from the header.',
  },
  {
    id: 'startup',
    title: 'Startup',
    body: 'Start when I sign in registers a per-user Startup entry. It needs no administrator approval and can be turned off here or in Task Manager → Startup. Start minimized waits in the notification area so F2 still works.',
  },
]
