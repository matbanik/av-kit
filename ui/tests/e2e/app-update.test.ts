// Session 106 (MEU-174): the Updates card and the in-app update against a local feed, through
// UPDATE_E2E_SEAM. One Node http server on 127.0.0.1 answers both the stub backend
// (`/api/v1/settings/*`, reached through AVKIT_E2E_API_BASE) and the generic feed (`/feed/*`).
// The feed config file names that URL and the cache folder `av-kit-e2e-updater`; main reads it
// only because AVKIT_E2E=1 and AVKIT_E2E_UPDATE_FEED names it. The recorded install calls are read
// from `globalThis.__AVKIT_E2E_UPDATE__` in the main process. Nothing leaves 127.0.0.1.
import { createHash } from 'node:crypto'
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { createServer, type IncomingMessage, type Server, type ServerResponse } from 'node:http'
import { homedir, tmpdir } from 'node:os'
import { join } from 'node:path'

import { expect, test, type ElectronApplication, type Page } from '@playwright/test'

import { launchElectron } from './electron-app'

/** The cache folder the feed config names; removed before and after each test. */
const CACHE_DIR_NAME = 'av-kit-e2e-updater'
/** The installer the feed offers: 64 KB of fixed bytes. */
const INSTALLER_BYTES = Buffer.alloc(64 * 1024, 0x5a)
/** How long the feed holds `latest.yml` when a test watches the "Checking…" state. */
const HELD_FEED_MS = 1_500

type FeedMode = { version: string; sha512: 'right' | 'wrong'; holdMs: number }

interface Stub {
  server: Server
  apiBase: string
  feedUrl: string
  appPuts: Array<Record<string, unknown>>
  setFeed(mode: FeedMode): void
  close(): Promise<void>
}

function sha512(bytes: Buffer): string {
  return createHash('sha512').update(bytes).digest('base64')
}

function installerName(version: string): string {
  return `av-kit-Setup-${version}.exe`
}

function latestYml(mode: FeedMode): string {
  const name = installerName(mode.version)
  const hash = mode.sha512 === 'right' ? sha512(INSTALLER_BYTES) : sha512(Buffer.from('not the installer'))
  return [
    `version: ${mode.version}`,
    'files:',
    `  - url: ${name}`,
    `    sha512: ${hash}`,
    `    size: ${String(INSTALLER_BYTES.length)}`,
    `path: ${name}`,
    `sha512: ${hash}`,
    "releaseDate: '2026-11-26T00:00:00.000Z'",
    '',
  ].join('\n')
}

function cacheDir(): string {
  return join(process.env.LOCALAPPDATA ?? join(homedir(), 'AppData', 'Local'), CACHE_DIR_NAME)
}

async function readBody(req: IncomingMessage): Promise<Record<string, unknown>> {
  const chunks: Buffer[] = []
  for await (const chunk of req) chunks.push(chunk as Buffer)
  const text = Buffer.concat(chunks).toString('utf8')
  return text === '' ? {} : (JSON.parse(text) as Record<string, unknown>)
}

/** The stub backend and the feed on one 127.0.0.1 port the system picks. */
async function startStub(): Promise<Stub> {
  // The feed answers once the test has named its mode (after the launch reads the running version).
  let feed: FeedMode | undefined
  let named: () => void = () => undefined
  const modeNamed = new Promise<void>((done) => {
    named = done
  })
  const app: Record<string, unknown> = { log_level: 'INFO', log_to_file: false, console_visible: true, update_interval: 'weekly' }
  const appPuts: Array<Record<string, unknown>> = []
  const send = (res: ServerResponse, status: number, body: unknown): void => {
    res.writeHead(status, { 'Content-Type': 'application/json' })
    res.end(JSON.stringify(body))
  }
  const server = createServer((req, res) => {
    void (async () => {
      const path = (req.url ?? '/').split('?')[0]
      const method = (req.method ?? 'GET').toUpperCase()
      if (path.startsWith('/feed/')) await modeNamed
      const mode = feed
      if (mode !== undefined && path === '/feed/latest.yml') {
        const text = latestYml(mode)
        if (mode.holdMs > 0) await new Promise((done) => setTimeout(done, mode.holdMs))
        res.writeHead(200, { 'Content-Type': 'text/yaml' })
        res.end(text)
        return
      }
      if (mode !== undefined && path === `/feed/${installerName(mode.version)}`) {
        res.writeHead(200, { 'Content-Type': 'application/octet-stream', 'Content-Length': String(INSTALLER_BYTES.length) })
        res.end(INSTALLER_BYTES)
        return
      }
      if (path.startsWith('/feed/')) {
        res.writeHead(404)
        res.end()
        return
      }
      if (path === '/api/v1/settings/app') {
        if (method === 'PUT' || method === 'PATCH') {
          const body = await readBody(req)
          appPuts.push(body)
          Object.assign(app, body)
        }
        send(res, 200, app)
        return
      }
      if (path === '/api/v1/settings/downloader') return send(res, 200, { path: 'C:/Downloads/av-kit', quality: '1080p' })
      if (path === '/api/v1/settings/transcript') return send(res, 200, { output_dir: 'C:/Transcripts' })
      if (path === '/api/v1/settings/tts') return send(res, 200, { models_directory: 'C:/models', chunk_max_chars: 250 })
      if (path === '/api/v1/settings/ui') return send(res, 200, { theme: 'dark' })
      if (path === '/api/v1/settings/converter') {
        return send(res, 200, { output_dir: '~/Videos/av-kit', default_preset: 'balanced', skip_existing: true, gpu_preference: 'auto' })
      }
      if (path === '/api/v1/settings/capture') {
        return send(res, 200, { inbox_dir: '~/Pictures/av-kit', hotkey: 'F2', copy_to_clipboard: false, close_to_tray: true })
      }
      if (path === '/api/v1/health/dependencies') {
        return send(res, 200, {
          yt_dlp: { available: true, version: '2026.11.23', path: 'C:/bin/yt-dlp.exe' },
          ffmpeg: { available: true, version: '7.1.2', path: 'C:/bin/ffmpeg.exe', ffprobe_available: true },
        })
      }
      send(res, 200, {})
    })().catch(() => {
      res.writeHead(500)
      res.end('{}')
    })
  })
  await new Promise<void>((ready) => {
    server.listen(0, '127.0.0.1', ready)
  })
  const address = server.address()
  if (address === null || typeof address === 'string') throw new Error('the e2e stub did not bind a TCP port')
  const origin = `http://127.0.0.1:${String(address.port)}`
  return {
    server,
    apiBase: `${origin}/api/v1`,
    feedUrl: `${origin}/feed`,
    appPuts,
    setFeed: (mode) => {
      feed = mode
      named()
    },
    close: () =>
      new Promise<void>((done) => {
        server.close(() => {
          done()
        })
      }),
  }
}

interface Harness {
  app: ElectronApplication
  page: Page
  stub: Stub
  close(): Promise<void>
}

/** Starts the stub with `mode`, writes the feed config into the scratch folder and launches the app. */
async function launch(mode: (running: string) => FeedMode): Promise<Harness> {
  rmSync(cacheDir(), { recursive: true, force: true })
  const scratch = mkdtempSync(join(tmpdir(), 'avkit-e2e-update-'))
  const stub = await startStub()
  const feedConfig = join(scratch, 'app-update.yml')
  writeFileSync(feedConfig, `provider: generic\nurl: ${stub.feedUrl}\nupdaterCacheDirName: ${CACHE_DIR_NAME}\n`, 'utf8')
  const appData = mkdtempSync(join(tmpdir(), 'avkit-e2e-update-data-'))
  const app = await launchElectron({
    env: {
      AVKIT_APP_DATA: appData,
      AVKIT_E2E_API_BASE: stub.apiBase,
      AVKIT_E2E_UPDATE_FEED: feedConfig,
      AVKIT_E2E_UPDATE_TICK_MS: '1000',
    },
  })
  const running = await app.evaluate(({ app: electronApp }) => electronApp.getVersion())
  stub.setFeed(mode(running))
  const page = await app.firstWindow()
  await page.getByTestId('app-shell').waitFor()
  return {
    app,
    page,
    stub,
    close: async () => {
      try {
        await app.close()
      } finally {
        await stub.close()
        rmSync(cacheDir(), { recursive: true, force: true })
        rmSync(scratch, { recursive: true, force: true })
      }
    },
  }
}

async function openUpdates(page: Page): Promise<void> {
  await page.getByTestId('nav-settings').click()
  await page.getByTestId('settings-page').waitFor()
  await expect(page.getByTestId('updates-settings')).toBeVisible()
}

async function installCalls(app: ElectronApplication): Promise<unknown> {
  return app.evaluate(() => {
    const seam = (globalThis as { __AVKIT_E2E_UPDATE__?: { installCalls: unknown } }).__AVKIT_E2E_UPDATE__
    return seam === undefined ? null : seam.installCalls
  })
}

const newer = (): FeedMode => ({ version: '999.0.0', sha512: 'right', holdMs: 0 })

test.describe.configure({ mode: 'serial' })

test('AC-174.15 the Updates section shows, and the interval select saves monthly and keeps it after a reload', async () => {
  const h = await launch(newer)
  try {
    await openUpdates(h.page)
    const select = h.page.getByTestId('settings-leaf-update_interval')
    await expect(select).toBeVisible()
    await expect(h.page.getByTestId('settings-update-version')).toContainText('Installed version ')
    await expect(h.page.getByTestId('settings-update-trust-note')).toHaveText(
      "Updates come from github.com/matbanik/av-kit and are checked against the release's SHA-512. The installer is not signed.",
    )
    await select.selectOption('monthly')
    await expect.poll(() => h.stub.appPuts.filter((put) => 'update_interval' in put)).toEqual([{ update_interval: 'monthly' }])
    await h.page.reload()
    await h.page.getByTestId('app-shell').waitFor()
    await openUpdates(h.page)
    await expect(h.page.getByTestId('settings-leaf-update_interval')).toHaveValue('monthly')
  } finally {
    await h.close()
  }
})

test('AC-174.15 a feed that offers 999.0.0 leads to Version 999.0.0 is ready to install', async () => {
  const h = await launch(newer)
  try {
    await openUpdates(h.page)
    await expect(h.page.getByTestId('settings-update-status')).toHaveText('Version 999.0.0 is ready to install')
    await expect(h.page.getByTestId('settings-update-restart')).toBeVisible()
    await expect(h.page.getByTestId('settings-update-restart-note')).toContainText('installs version 999.0.0')
  } finally {
    await h.close()
  }
})

test('AC-174.15 a feed that offers the running version reads Up to date and shows no restart button', async () => {
  const h = await launch((running) => ({ version: running, sha512: 'right', holdMs: 0 }))
  try {
    await openUpdates(h.page)
    await expect(h.page.getByTestId('settings-update-status')).toContainText('Up to date')
    await expect(h.page.getByTestId('settings-update-restart')).toHaveCount(0)
  } finally {
    await h.close()
  }
})

test('AC-174.16 a click on Check now passes through Checking', async () => {
  const h = await launch((running) => ({ version: running, sha512: 'right', holdMs: 0 }))
  try {
    await openUpdates(h.page)
    const status = h.page.getByTestId('settings-update-status')
    await expect(status).toContainText('Up to date')
    h.stub.setFeed({ version: await h.app.evaluate(({ app }) => app.getVersion()), sha512: 'right', holdMs: HELD_FEED_MS })
    await h.page.getByTestId('settings-update-check').click()
    await expect(status).toHaveText('Checking\u2026')
    await expect(status).toContainText('Up to date')
  } finally {
    await h.close()
  }
})

test('AC-174.16 Restart and update records exactly one quitAndInstall(true, true), and none before the click', async () => {
  const h = await launch(newer)
  try {
    await openUpdates(h.page)
    await expect(h.page.getByTestId('settings-update-status')).toHaveText('Version 999.0.0 is ready to install')
    expect(await installCalls(h.app)).toEqual([])
    await h.page.getByTestId('settings-update-restart').click()
    await expect.poll(() => installCalls(h.app)).toEqual([[true, true]])
  } finally {
    await h.close()
  }
})

test('AC-174.16 a feed with a wrong SHA-512 reads Could not check for updates (checksum) and records no install', async () => {
  const h = await launch(() => ({ version: '999.0.0', sha512: 'wrong', holdMs: 0 }))
  try {
    await openUpdates(h.page)
    await expect(h.page.getByTestId('settings-update-status')).toContainText('Could not check for updates (checksum)')
    await expect(h.page.getByTestId('settings-update-restart')).toHaveCount(0)
    expect(await installCalls(h.app)).toEqual([])
  } finally {
    await h.close()
  }
})
