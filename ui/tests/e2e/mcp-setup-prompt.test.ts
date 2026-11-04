import { _electron, expect, test, type ElectronApplication, type Page } from '@playwright/test'
import { mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import {
  MCP_ADVANCED_SUMMARY,
  MCP_CLIENT_SELECT,
  MCP_COPY_PROMPT_BTN,
  MCP_PROMPT_STATUS,
  MCP_SCOPE_SELECT,
  MCP_SETUP_PROMPT,
} from './test-ids'

const here = dirname(fileURLToPath(import.meta.url))

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

async function launchApp(): Promise<{ app: ElectronApplication; appData: string }> {
  const appData = mkdtempSync(join(tmpdir(), 'avkit-e2e-mcp-prompt-'))
  const app = await _electron.launch({
    args: [resolve(here, '../../out/main/index.js')],
    env: { ...process.env, AVKIT_E2E: '1', AVKIT_APP_DATA: appData },
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

test('AC-71.15 Codex prompt carries execPath and app data, Copy prompt fills the clipboard, Claude Desktop disables scope', async () => {
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

    // (b) Copy prompt: the main-process clipboard holds exactly the viewer text.
    // Clipboard listeners (Windows clipboard history) lock the clipboard right after each write, and a
    // write that meets the lock is dropped silently, so click again until the copy lands (D-94).
    await app.evaluate(({ clipboard }) => clipboard.writeText('s31b-clipboard-sentinel'))
    await expect(async () => {
      await page.getByTestId(MCP_COPY_PROMPT_BTN).click()
      expect(await app.evaluate(({ clipboard }) => clipboard.readText())).toBe(text)
    }).toPass({ timeout: 10_000 })
    await expect(page.getByTestId(MCP_PROMPT_STATUS)).toHaveText('Copied the Codex setup prompt.')

    // (c) Claude Desktop has no project file: scope is forced to user and disabled.
    await page.getByTestId(MCP_SCOPE_SELECT).selectOption('project')
    await page.getByTestId(MCP_CLIENT_SELECT).selectOption('claude-desktop')
    await expect(page.getByTestId(MCP_SCOPE_SELECT)).toBeDisabled()
    await expect(page.getByTestId(MCP_SCOPE_SELECT)).toHaveValue('user')
  } finally {
    await app.close()
  }
})

test('AC-71.15 Advanced starts closed and holds Copy MCP config; no setup prompt contains the token it copies', async () => {
  const { app } = await launchApp()
  try {
    const page = await app.firstWindow()
    await installSettingsSeam(page)
    await openSettings(page)

    // (d) Advanced is closed: Copy MCP config is hidden until the summary is clicked.
    await expect(page.getByTestId('mcp-advanced')).not.toHaveAttribute('open', /.*/)
    await expect(page.getByTestId('copy-mcp-btn')).toBeHidden()
    await page.getByTestId(MCP_ADVANCED_SUMMARY).click()
    await expect(page.getByTestId('copy-mcp-btn')).toBeVisible()
    // Same clipboard-lock race as (b): click again until the copy lands (D-94). An empty read is a lost race too.
    await app.evaluate(({ clipboard }) => clipboard.writeText('s31b-clipboard-sentinel'))
    let copiedText = ''
    await expect(async () => {
      await page.getByTestId('copy-mcp-btn').click()
      copiedText = await app.evaluate(({ clipboard }) => clipboard.readText())
      expect(copiedText).not.toBe('s31b-clipboard-sentinel')
      expect(copiedText).not.toBe('')
    }).toPass({ timeout: 10_000 })
    const copied = JSON.parse(copiedText) as { AVKIT_API_TOKEN?: string }
    const token = copied.AVKIT_API_TOKEN ?? ''
    expect(token.length).toBeGreaterThan(0)

    // (e) No viewer text for any client, at any scope it offers, contains that token.
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
  } finally {
    await app.close()
  }
})
