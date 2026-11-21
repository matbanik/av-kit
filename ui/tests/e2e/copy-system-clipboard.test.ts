// Session 100 (D-1305): the E2E steps that write or read the system clipboard, moved with
// their assertions unchanged from console-chrome.test.ts (C1-5) and mcp-setup-prompt.test.ts
// (AC-71.15 (b) and (d)). The clipboard is shared with the whole desktop, so this file never
// runs on the dev PC (flake-run.py EXCLUDED); on the mini-air, tools/e2e_host/known-failures.json
// names how it runs (gated by the remote-session probe, or skipped).

import { expect, test, type ElectronApplication, type Page } from '@playwright/test'
import { mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { launchElectron } from './electron-app'
import {
  MCP_ADVANCED_SUMMARY,
  MCP_CLIENT_SELECT,
  MCP_COPY_PROMPT_BTN,
  MCP_PROMPT_STATUS,
  MCP_SCOPE_SELECT,
  MCP_SETUP_PROMPT,
} from './test-ids'

// Session 100 (D-1305): as in capture-system-clipboard.test.ts, only the gated stage of
// tools/e2e_host/run-e2e.ps1 sets AVKIT_E2E_CLIPBOARD_GATED=1. Every other run, the dev PC's
// included, lists these tests as skipped.
test.skip(
  process.env.AVKIT_E2E_CLIPBOARD_GATED !== '1',
  'system clipboard spec: runs only in the gated stage on the second Windows host',
)

async function launchApp(): Promise<{ app: ElectronApplication; appData: string }> {
  const appData = mkdtempSync(join(tmpdir(), 'avkit-e2e-mcp-prompt-'))
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

test('C1-5 console copy writes the visible logs to the clipboard', async () => {
  const { app } = await launchApp()
  try {
    const page = await app.firstWindow()
    // C1-5's /settings/app route, kept so the Console opens as it does in console-chrome.test.ts.
    const putBodies: string[] = []
    await page.context().route((url) => url.pathname.includes('/settings/app'), async (route) => {
      // The Console also GETs /settings/app when it opens (its start level); count only PUTs.
      if (route.request().method() === 'PUT') {
        putBodies.push(route.request().postData() ?? '')
      }
      await route.fulfill({ json: { log_to_file: true } })
    })
    await expect(page.getByTestId('header-console-btn')).toBeVisible()
    await page.getByTestId('header-console-btn').click()
    await expect(page.getByTestId('console-panel')).toBeVisible()
    const visibleLogs = await page.locator('[data-testid="console-panel"] pre').innerText()
    await page.getByTestId('console-copy').click()
    const clipboard = await app.evaluate(({ clipboard }) => clipboard.readText())
    expect(clipboard).toBe(visibleLogs)
  } finally {
    await app.close()
  }
})

test('AC-71.15 (b) Copy prompt fills the clipboard with the Codex setup prompt', async () => {
  const { app } = await launchApp()
  try {
    const page = await app.firstWindow()
    await installSettingsSeam(page)
    await openSettings(page)

    const text = await showPrompt(page, 'codex', 'Codex', 'user')

    // (b) Copy prompt: the main-process clipboard holds exactly the viewer text.
    // Clipboard listeners (Windows clipboard history) lock the clipboard right after each write, and a
    // write that meets the lock is dropped silently, so click again until the copy lands (D-94).
    await app.evaluate(({ clipboard }) => clipboard.writeText('s31b-clipboard-sentinel'))
    await expect(async () => {
      await page.getByTestId(MCP_COPY_PROMPT_BTN).click()
      expect(await app.evaluate(({ clipboard }) => clipboard.readText())).toBe(text)
    }).toPass({ timeout: 10_000 })
    await expect(page.getByTestId(MCP_PROMPT_STATUS)).toHaveText('Copied the Codex setup prompt.')
  } finally {
    await app.close()
  }
})

test('AC-71.15 (d) Copy MCP config puts a non-empty app token on the clipboard', async () => {
  const { app } = await launchApp()
  try {
    const page = await app.firstWindow()
    await installSettingsSeam(page)
    await openSettings(page)

    // (d) Copy MCP config: the clipboard holds a config with a non-empty AVKIT_API_TOKEN.
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
  } finally {
    await app.close()
  }
})
