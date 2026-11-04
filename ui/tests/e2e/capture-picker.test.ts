import { _electron, expect, test, type ElectronApplication, type Page } from '@playwright/test'
import { createServer, type IncomingMessage, type Server, type ServerResponse } from 'node:http'
import { spawn } from 'node:child_process'
import { existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

/**
 * AC-40.18 — the real-Electron capture path.
 *
 * The whole production chain runs here: the main process spawns a real child through
 * `AVKIT_REGION_PICKER_PATH` (pointed at the deterministic sidecar stub, so no display and no
 * human are needed), the staged PNG goes through the pixel guard, the `linkSync` name-claim
 * publishes it into the inbox, `POST /captures` registers it against a real HTTP server this
 * spec owns, and the renderer refreshes off `captures:inbox-changed`.
 *
 * Nothing here is mocked in the main process: the only substitutions are the picker executable
 * and the backend, both of which are real processes/servers the app talks to over its normal
 * interfaces.
 */

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')
const STUB_EXE = resolve(repoRoot, 'native/region-picker-stub/publish/avkit-region-picker-stub.exe')

type CaptureRow = {
  id: string
  original_path: string
  annotated_path: string | null
  sidecar_path: string | null
  display_name: string
  width: number
  height: number
  file_size: number
  source: string
  created_at: string
  updated_at: string
}

type Backend = {
  server: Server
  base: string
  registered: Record<string, unknown>[]
  setInbox: (dir: string) => void
  close: () => Promise<void>
}

async function startBackend(inboxDir: string): Promise<Backend> {
  const registered: Record<string, unknown>[] = []
  const rows: CaptureRow[] = []
  let inbox = inboxDir

  const readBody = async (req: IncomingMessage): Promise<Record<string, unknown>> => {
    const chunks: Buffer[] = []
    for await (const chunk of req) {
      chunks.push(chunk as Buffer)
    }
    const text = Buffer.concat(chunks).toString('utf8')
    if (text.trim().length === 0) {
      return {}
    }
    return JSON.parse(text) as Record<string, unknown>
  }

  const send = (res: ServerResponse, status: number, body: unknown): void => {
    const payload = JSON.stringify(body)
    res.writeHead(status, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' })
    res.end(payload)
  }

  const server = createServer((req, res) => {
    void (async () => {
      const url = new URL(req.url ?? '/', 'http://127.0.0.1')
      const path = url.pathname
      const method = (req.method ?? 'GET').toUpperCase()

      if (path.endsWith('/settings/capture')) {
        send(res, 200, {
          inbox_dir: inbox,
          hotkey: 'F2',
          copy_to_clipboard: false,
          close_to_tray: true,
        })
        return
      }
      if (path.includes('/health')) {
        send(res, 200, { ffmpeg: { available: true, version: '7.1.2' }, yt_dlp: { available: true } })
        return
      }
      if (path.includes('/captures/requests')) {
        send(res, 200, { items: [] })
        return
      }
      if (/\/captures\/?$/.test(path) && method === 'POST') {
        const body = await readBody(req)
        registered.push(body)
        const name = String(body.path ?? '').split(/[\\/]/).pop() ?? 'capture.png'
        const row: CaptureRow = {
          id: `e2e-${rows.length + 1}`,
          original_path: String(body.path ?? ''),
          annotated_path: null,
          sidecar_path: null,
          display_name: name,
          width: 8,
          height: 8,
          file_size: 64,
          source: String(body.source ?? 'gui'),
          created_at: '2026-08-27T10:00:00Z',
          updated_at: '2026-08-27T10:00:00Z',
        }
        rows.push(row)
        send(res, 201, row)
        return
      }
      if (/\/captures\/?$/.test(path) && method === 'GET') {
        send(res, 200, { items: [...rows] })
        return
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
  if (address === null || typeof address === 'string') {
    throw new Error('the e2e backend did not bind a TCP port')
  }

  return {
    server,
    base: `http://127.0.0.1:${address.port}/api/v1`,
    registered,
    setInbox: (dir: string) => {
      inbox = dir
    },
    close: () =>
      new Promise<void>((done) => {
        server.close(() => {
          done()
        })
      }),
  }
}

type Harness = {
  app: ElectronApplication
  page: Page
  backend: Backend
  inbox: string
  close: () => Promise<void>
}

async function launch(stubEnv: Record<string, string>): Promise<Harness> {
  expect(
    existsSync(STUB_EXE),
    `the deterministic sidecar stub is missing: run "npm --prefix ui run build:picker-stub" (${STUB_EXE})`,
  ).toBe(true)

  const inbox = mkdtempSync(join(tmpdir(), 'avkit-e2e-inbox-'))
  mkdirSync(inbox, { recursive: true })
  const backend = await startBackend(inbox)

  const app = await _electron.launch({
    args: [resolve(here, '../../out/main/index.js')],
    env: {
      ...process.env,
      AVKIT_E2E: '1',
      AVKIT_E2E_API_BASE: backend.base,
      AVKIT_APP_DATA: mkdtempSync(join(tmpdir(), 'avkit-e2e-picker-')),
      AVKIT_REGION_PICKER_PATH: STUB_EXE,
      ...stubEnv,
    },
  })
  const page = await app.firstWindow()
  await page.getByTestId('nav-capture').click()
  await expect(page.getByTestId('capture-page')).toBeVisible()
  // The main process polls the settings endpoint once a second; wait for it to have adopted
  // this run's inbox before firing, so the capture cannot land in the developer's real one.
  await expect(page.getByTestId('capture-inbox-path')).toHaveValue(inbox, { timeout: 20_000 })

  return {
    app,
    page,
    backend,
    inbox,
    close: async () => {
      await app.close()
      await backend.close()
    },
  }
}

function inboxPngs(dir: string): string[] {
  return readdirSync(dir).filter((name) => name.toLowerCase().endsWith('.png'))
}

test('region picker confirm publishes and registers the capture', async () => {
  const h = await launch({ AVKIT_STUB_EXIT: '0', AVKIT_STUB_PIXEL: 'colour' })
  try {
    await h.page.getByTestId('capture-region').click()

    await expect.poll(() => inboxPngs(h.inbox).length, { timeout: 30_000 }).toBe(1)
    await expect.poll(() => h.backend.registered.length, { timeout: 30_000 }).toBe(1)

    const published = join(h.inbox, inboxPngs(h.inbox)[0] as string)
    const body = h.backend.registered[0] as Record<string, unknown>
    expect(String(body.path).replace(/\\/g, '/')).toBe(published.replace(/\\/g, '/'))
    expect(body.mode).toBe('register')
    expect(body.source).toBe('gui')

    // The renderer only learns about the new file through `captures:inbox-changed`.
    await expect(h.page.getByTestId('capture-filmstrip')).toContainText(
      inboxPngs(h.inbox)[0] as string,
      { timeout: 30_000 },
    )
  } finally {
    await h.close()
  }
})

test('region picker cancel leaves the inbox unchanged', async () => {
  const h = await launch({ AVKIT_STUB_EXIT: '2', AVKIT_STUB_PIXEL: 'colour' })
  try {
    const before = inboxPngs(h.inbox)
    await h.page.getByTestId('capture-region').click()
    await h.page.waitForTimeout(4000)

    expect(inboxPngs(h.inbox)).toEqual(before)
    expect(h.backend.registered).toEqual([])
    // The staging file the helper was handed must not be left behind either.
    expect(readdirSync(h.inbox)).toEqual([])
  } finally {
    await h.close()
  }
})

test('region picker all-black capture is rejected', async () => {
  const h = await launch({ AVKIT_STUB_EXIT: '0', AVKIT_STUB_PIXEL: 'black' })
  try {
    await h.page.getByTestId('capture-region').click()
    await h.page.waitForTimeout(4000)

    expect(inboxPngs(h.inbox)).toEqual([])
    expect(readdirSync(h.inbox)).toEqual([])
    expect(h.backend.registered).toEqual([])
  } finally {
    await h.close()
  }
})

// Guards this spec's own fixture: a stub that silently wrote nothing would make the cancel and
// all-black cases pass for the wrong reason, so prove the stub really does produce pixels when
// it is told to confirm, and really does exit with the code it was given.
test('the sidecar stub writes a real PNG when told to confirm', async () => {
  const probe = mkdtempSync(join(tmpdir(), 'avkit-e2e-stub-'))
  const out = join(probe, 'staged.png')

  const code = await new Promise<number | null>((done) => {
    const child = spawn(STUB_EXE, ['--out', out], {
      shell: false,
      windowsHide: true,
      env: { ...process.env, AVKIT_STUB_EXIT: '0', AVKIT_STUB_PIXEL: 'colour' },
    })
    child.on('close', (c) => {
      done(c)
    })
  })

  expect(code).toBe(0)
  expect(existsSync(out)).toBe(true)
  const bytes = readFileSync(out)
  expect(bytes.subarray(0, 8)).toEqual(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]))
  expect(bytes.byteLength).toBeGreaterThan(64)
})
