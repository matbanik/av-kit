import { expect, test, type ElectronApplication, type Page } from '@playwright/test'
import { randomUUID } from 'node:crypto'
import { mkdtempSync, readFileSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { launchElectron } from './electron-app'
import {
  MCP_ADVANCED_SUMMARY,
  MCP_CLIENT_SELECT,
  MCP_SCOPE_SELECT,
  MCP_SETUP_PROMPT,
} from './test-ids'

// CLIENT_SET: value and label, in order; the first four also have a project scope.
const CLIENT_SET = [
  ['claude-code', 'Claude Code'],
  ['codex', 'Codex'],
  ['cursor', 'Cursor'],
  ['vscode', 'VS Code'],
  ['claude-desktop', 'Claude Desktop'],
  ['windsurf', 'Windsurf (community)'],
  ['generic', 'Other MCP client'],
] as const
const PROJECT_CLIENTS = ['claude-code', 'codex', 'cursor', 'vscode']

async function launchApp(token?: string): Promise<{ app: ElectronApplication; appData: string }> {
  const appData = mkdtempSync(join(tmpdir(), 'avkit-e2e-mcp-prompt-'))
  // Session 100 (D-1307): a test that needs the app's MCP token seeds a throwaway one in its own
  // scratch app data, which readOrCreateMcpToken (src/main/index.ts) reads instead of making one.
  if (token !== undefined) writeFileSync(join(appData, 'mcp-token.txt'), `${token}\n`, { encoding: 'utf8' })
  const app = await launchElectron({
    env: { AVKIT_APP_DATA: appData },
  })
  return { app, appData }
}

/** Settings reads answered in the renderer, so the page renders without a backend (settings.test.ts seam shape). */
async function installSettingsSeam(page: Page): Promise<void> {
  await page.addInitScript(() => {
    window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
      const method = (init?.method ?? 'GET').toUpperCase()
      const json = (payload: unknown, status = 200) =>
        new Response(JSON.stringify(payload), { status, headers: { 'Content-Type': 'application/json' } })
      if (method === 'GET') {
        if (url.includes('/settings/downloader')) return json({ path: 'C:/Downloads/av-kit', quality: '1080p' })
        if (url.includes('/settings/transcript')) return json({ output_dir: 'C:/Transcripts' })
        if (url.includes('/settings/tts')) return json({ models_directory: 'C:/models', chunk_max_chars: 250 })
        if (url.includes('/settings/app')) return json({ log_level: 'INFO', log_to_file: false, console_visible: true })
        if (url.includes('/settings/ui')) return json({ theme: 'dark' })
        if (url.includes('/settings/converter')) {
          return json({ output_dir: '~/Videos/av-kit', default_preset: 'balanced', skip_existing: true, gpu_preference: 'auto' })
        }
        if (url.includes('/settings/capture')) {
          return json({ inbox_dir: '~/Pictures/av-kit', hotkey: 'F2', copy_to_clipboard: false, close_to_tray: true })
        }
        if (url.includes('/health/dependencies')) {
          return json({
            yt_dlp: { available: true, version: '2026.05.15', path: 'C:/bin/yt-dlp.exe' },
            ffmpeg: { available: true, version: '7.1.2', path: 'C:/bin/ffmpeg.exe', ffprobe_available: true },
          })
        }
      }
      return json({ error: { code: 'E2E', message: 'unexpected' } }, 599)
    }
  })
  await page.reload()
  await page.getByTestId('app-shell').waitFor()
}

async function openSettings(page: Page): Promise<void> {
  await page.getByTestId('nav-settings').click()
  await page.getByTestId('settings-page').waitFor()
}

/** Chooses a client and scope, then waits for the viewer to hold that pair's prompt. */
async function showPrompt(page: Page, client: string, label: string, scope: 'user' | 'project'): Promise<string> {
  await page.getByTestId(MCP_CLIENT_SELECT).selectOption(client)
  if (scope === 'project') await page.getByTestId(MCP_SCOPE_SELECT).selectOption('project')
  const heading = `Set up the av-kit MCP server for ${label} (${scope === 'user' ? 'user scope: all projects' : 'project scope: this project only'}).`
  const viewer = page.getByTestId(MCP_SETUP_PROMPT)
  await expect(viewer).toHaveValue(new RegExp(`^${heading.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`))
  return viewer.inputValue()
}

/** The JSON string value on a `key = "..."` TOML line. */
function tomlString(text: string, key: string): string | undefined {
  const line = text.split('\n').find((row) => row.startsWith(`${key} = `))
  return line === undefined ? undefined : (JSON.parse(line.slice(key.length + 3)) as string)
}

test('AC-71.15 Codex prompt carries execPath and app data, Claude Desktop disables scope', async () => {
  const { app, appData } = await launchApp()
  try {
    const page = await app.firstWindow()
    await installSettingsSeam(page)
    await openSettings(page)

    // (a) Codex: the TOML block names the app's own executable and app data folder.
    const text = await showPrompt(page, 'codex', 'Codex', 'user')
    expect(text).toContain('[mcp_servers.avkit]')
    const execPath = await app.evaluate(() => process.execPath)
    expect(tomlString(text, 'command')).toBe(execPath)
    expect(tomlString(text, 'AVKIT_APP_DATA')).toBe(appData)
    expect(tomlString(text, 'ELECTRON_RUN_AS_NODE')).toBe('1')

    // Session 100 (D-1305): (b) Copy prompt runs in copy-system-clipboard.test.ts (gated stage only).

    // (c) Claude Desktop has no project file: scope is forced to user and disabled.
    await page.getByTestId(MCP_SCOPE_SELECT).selectOption('project')
    await page.getByTestId(MCP_CLIENT_SELECT).selectOption('claude-desktop')
    await expect(page.getByTestId(MCP_SCOPE_SELECT)).toBeDisabled()
    await expect(page.getByTestId(MCP_SCOPE_SELECT)).toHaveValue('user')
  } finally {
    await app.close()
  }
})

test('AC-71.15 Advanced starts closed and holds Copy MCP config; no setup prompt contains the app token', async () => {
  const token = randomUUID()
  const { app, appData } = await launchApp(token)
  try {
    const page = await app.firstWindow()
    await installSettingsSeam(page)
    await openSettings(page)

    // (d) Advanced is closed: Copy MCP config is hidden until the summary is clicked.
    await expect(page.getByTestId('mcp-advanced')).not.toHaveAttribute('open', /.*/)
    await expect(page.getByTestId('copy-mcp-btn')).toBeHidden()
    await page.getByTestId(MCP_ADVANCED_SUMMARY).click()
    await expect(page.getByTestId('copy-mcp-btn')).toBeVisible()
    // Session 100 (D-1305): (d)'s Copy MCP config read runs in copy-system-clipboard.test.ts (gated stage only).

    // (e) No viewer text for any client, at any scope it offers, contains the app's token (seeded at launch, D-1307).
    for (const [client, label] of CLIENT_SET) {
      const scopes: Array<'user' | 'project'> = PROJECT_CLIENTS.includes(client) ? ['user', 'project'] : ['user']
      for (const scope of scopes) {
        if (scope === 'user' && PROJECT_CLIENTS.includes(client)) {
          await page.getByTestId(MCP_SCOPE_SELECT).selectOption('user')
        }
        const text = await showPrompt(page, client, label, scope)
        expect(text.includes(token), `${client}-${scope}`).toBe(false)
      }
    }
    // Session 100 (D-1327): the app read the seeded token and kept it, so (e) checked the token it uses.
    expect(readFileSync(join(appData, 'mcp-token.txt'), 'utf8')).toBe(`${token}\n`)
  } finally {
    await app.close()
  }
})
