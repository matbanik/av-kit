// Session 98 (D-1268, D-1269): the two E2E tests that write the system clipboard,
// moved unchanged from capture-filmstrip-actions.test.ts (AC-88.12 (a)(b)(f)) and
// capture-import.test.ts (AC-132.23) with the blocks they need. The clipboard is
// shared with the whole desktop, so this file never runs on the dev PC (flake-run.py
// EXCLUDED); on the mini-air, tools/e2e_host/known-failures.json names how it runs
// (gated by the remote-session probe, or skipped).

import { expect, test, type ElectronApplication, type Page } from '@playwright/test'
import { mkdtempSync, mkdirSync, readdirSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { createServer, type IncomingMessage, type Server, type ServerResponse } from 'node:http'

import { launchElectron } from './electron-app'

// Session 98 (D-1282): only the gated stage of tools/e2e_host/run-e2e.ps1 sets
// AVKIT_E2E_CLIPBOARD_GATED=1. Every other run, the dev PC's included, lists both tests as skipped.
test.skip(
  process.env.AVKIT_E2E_CLIPBOARD_GATED !== '1',
  'system clipboard spec: runs only in the gated stage on the second Windows host',
)

type CaptureItem = {
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

type ImageFixture = { type: string; bytes: number[] }

type SeamState = {
  __e2eSeamInstalled?: boolean
  __e2eCaptures?: CaptureItem[]
  __e2eDeletes?: string[]
}

const SHOT_W = 8
const SHOT_H = 6

function sampleShot(id: string, name: string, createdAt: string): CaptureItem {
  return {
    id,
    original_path: `C:/e2e/${name}`,
    annotated_path: null,
    sidecar_path: null,
    display_name: name,
    width: SHOT_W,
    height: SHOT_H,
    file_size: 64,
    source: 'gui',
    created_at: createdAt,
    updated_at: createdAt,
  }
}

async function launchApp(): Promise<ElectronApplication> {
  return launchElectron({
    env: {
      AVKIT_APP_DATA: mkdtempSync(join(tmpdir(), 'avkit-e2e-filmstrip-')),
    },
  })
}

/** SHOT_PIXELS fixtures: 8×6, left half opaque #ff0000, right half opaque #0000ff. */
async function buildFixtures(app: ElectronApplication, page: Page): Promise<{ png: number[]; webp: number[] }> {
  const png = await app.evaluate(({ nativeImage }, size) => {
    const bitmap = Buffer.alloc(size.w * size.h * 4)
    for (let y = 0; y < size.h; y += 1) {
      for (let x = 0; x < size.w; x += 1) {
        const i = (y * size.w + x) * 4
        const red = x < size.w / 2
        // createFromBitmap takes BGRA.
        bitmap[i] = red ? 0 : 255
        bitmap[i + 1] = 0
        bitmap[i + 2] = red ? 255 : 0
        bitmap[i + 3] = 255
      }
    }
    return Array.from(nativeImage.createFromBitmap(bitmap, { width: size.w, height: size.h }).toPNG())
  }, { w: SHOT_W, h: SHOT_H })
  const webp = await page.evaluate(async (size) => {
    const canvas = new OffscreenCanvas(size.w, size.h)
    const ctx = canvas.getContext('2d') as OffscreenCanvasRenderingContext2D
    ctx.fillStyle = '#ff0000'
    ctx.fillRect(0, 0, size.w / 2, size.h)
    ctx.fillStyle = '#0000ff'
    ctx.fillRect(size.w / 2, 0, size.w / 2, size.h)
    const blob = await canvas.convertToBlob({ type: 'image/webp', quality: 1 })
    return Array.from(new Uint8Array(await blob.arrayBuffer()))
  }, { w: SHOT_W, h: SHOT_H })
  // The WebP fixture must really be WebP ("RIFF"), or Copy image would skip the re-encode path.
  expect(String.fromCharCode(...webp.slice(0, 4))).toBe('RIFF')
  expect(png.slice(0, 4)).toEqual([0x89, 0x50, 0x4e, 0x47])
  return { png, webp }
}

async function installSeam(
  page: Page,
  seed: CaptureItem[],
  images: Record<string, ImageFixture>,
  failDeletes: string[] = [],
): Promise<void> {
  await page.addInitScript(
    (arg: { seed: CaptureItem[]; images: Record<string, ImageFixture>; failDeletes: string[] }) => {
      const state = window as unknown as SeamState
      state.__e2eSeamInstalled = true
      state.__e2eCaptures = [...arg.seed]
      state.__e2eDeletes = []
      const original = window.fetch.bind(window)
      window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
        const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
        const method = (init?.method ?? 'GET').toUpperCase()
        const json = (body: unknown, status = 200) =>
          new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
        if (url.includes('/health/dependencies')) {
          return json({ ffmpeg: { available: true, version: '7.1.2' }, yt_dlp: { available: true } })
        }
        if (url.includes('/settings/capture')) {
          return json({ inbox_dir: '~/Pictures/av-kit', hotkey: 'F2', copy_to_clipboard: false, close_to_tray: true, tool_lock: false })
        }
        if (url.includes('/captures/requests')) {
          return json({ items: [] })
        }
        const path = new URL(url).pathname
        const image = path.match(/\/captures\/(.+)\/image$/)
        if (image) {
          const fixture = arg.images[decodeURIComponent(image[1] as string)]
          if (fixture === undefined) {
            return json({ error: { code: 'not_found', message: 'no image', details: null } }, 404)
          }
          return new Response(Uint8Array.from(fixture.bytes), { status: 200, headers: { 'Content-Type': fixture.type } })
        }
        if (/\/captures\/?$/.test(path) && method === 'GET') {
          return json({ items: state.__e2eCaptures ?? [] })
        }
        const one = path.match(/\/captures\/([^/]+)$/)
        if (one && method === 'DELETE') {
          const id = decodeURIComponent(one[1] as string)
          state.__e2eDeletes?.push(id)
          if (arg.failDeletes.includes(id)) {
            return json({ error: { code: 'capture_delete_failed', message: 'file is locked', details: null } }, 500)
          }
          state.__e2eCaptures = (state.__e2eCaptures ?? []).filter((item) => item.id !== id)
          return new Response(null, { status: 204 })
        }
        if (one && method === 'GET') {
          const id = decodeURIComponent(one[1] as string)
          const row = (state.__e2eCaptures ?? []).find((item) => item.id === id)
          return json({ ...row, annotations: [], backup_path: null })
        }
        if (path.includes('/annotate') && method === 'POST') {
          return json(state.__e2eCaptures?.[0] ?? {})
        }
        return original(input, init)
      }
    },
    { seed, images, failDeletes },
  )
  await page.reload()
  await page.getByTestId('downloader-page').waitFor()
}

type ClipboardProbe = { empty: boolean; width: number; height: number; left: number[]; right: number[] }

/** Reads the main-process clipboard image: its size and the BGRA pixels at (1,3) and (6,3). */
async function readClipboardImage(app: ElectronApplication): Promise<ClipboardProbe> {
  return app.evaluate(({ clipboard }) => {
    const img = clipboard.readImage()
    const { width, height } = img.getSize()
    const bitmap = img.toBitmap()
    const px = (x: number, y: number): number[] => {
      if (x >= width || y >= height) {
        return []
      }
      const i = (y * width + x) * 4
      return [bitmap[i] ?? 0, bitmap[i + 1] ?? 0, bitmap[i + 2] ?? 0, bitmap[i + 3] ?? 0]
    }
    return { empty: img.isEmpty(), width, height, left: px(1, 3), right: px(6, 3) }
  })
}

/**
 * Clipboard listeners (Windows clipboard history, screenshot tools) open the clipboard right
 * after every write, and a read that loses that race comes back empty. Retry until it is not.
 */
async function readSettledClipboardImage(app: ElectronApplication, label: string): Promise<ClipboardProbe> {
  let probe = await readClipboardImage(app)
  await expect
    .poll(async () => {
      probe = await readClipboardImage(app)
      return probe.empty
    }, { message: `${label}: clipboard image read stayed empty` })
    .toBe(false)
  return probe
}

/** SHOT_PIXELS: (1,3) red and (6,3) blue, each channel within ±16, alpha 255. */
function passesShotPixels(probe: ClipboardProbe): boolean {
  const near = (value: number | undefined, target: number) => value !== undefined && Math.abs(value - target) <= 16
  const [lb, lg, lr, la] = probe.left
  const [rb, rg, rr, ra] = probe.right
  return (
    !probe.empty &&
    near(lb, 0) && near(lg, 0) && near(lr, 255) && la === 255 &&
    near(rb, 255) && near(rg, 0) && near(rr, 0) && ra === 255
  )
}

/** Puts a transparent 8×6 image on the clipboard; the oracle must reject it (AC-88.12 f). */
async function primeTransparentClipboard(app: ElectronApplication): Promise<void> {
  await app.evaluate(({ clipboard, nativeImage }, size) => {
    clipboard.writeImage(nativeImage.createFromBitmap(Buffer.alloc(size.w * size.h * 4), { width: size.w, height: size.h }))
  }, { w: SHOT_W, h: SHOT_H })
  expect(passesShotPixels(await readSettledClipboardImage(app, 'primer'))).toBe(false)
}

const SHOT_A = sampleShot('e2e-a', 'a.png', '2026-10-14T12:00:00Z')
const SHOT_B = sampleShot('e2e-b', 'b.webp', '2026-10-14T11:00:00Z')
const SHOT_C = sampleShot('e2e-c', 'c.png', '2026-10-14T10:00:00Z')

async function openCapture(seed: CaptureItem[], failDeletes: string[] = []) {
  const app = await launchApp()
  const page = await app.firstWindow()
  await page.getByTestId('downloader-page').waitFor()
  const fixtures = await buildFixtures(app, page)
  const images: Record<string, ImageFixture> = {}
  for (const item of seed) {
    images[item.id] = item.display_name.endsWith('.webp')
      ? { type: 'image/webp', bytes: fixtures.webp }
      : { type: 'image/png', bytes: fixtures.png }
  }
  await installSeam(page, seed, images, failDeletes)
  await page.getByTestId('nav-capture').click()
  const thumbs = page.getByTestId('capture-filmstrip-item')
  await expect(thumbs).toHaveCount(seed.length)
  // The newest shot is auto-selected on load.
  await expect(thumbs.nth(0)).toHaveAttribute('aria-current', 'true')
  return { app, page, thumbs }
}

test('AC-88.12 (a)(b)(f) Copy full path and Copy image reach the main-process clipboard', async () => {
  const { app, page, thumbs } = await openCapture([SHOT_A, SHOT_B, SHOT_C])
  const menu = page.getByTestId('capture-filmstrip-menu')

  await app.evaluate(({ clipboard }) => clipboard.writeText('sentinel'))
  await thumbs.nth(1).click({ button: 'right' })
  await expect(menu).toBeVisible()
  await page.getByTestId('capture-filmstrip-menu-copy-path').click()
  await expect.poll(() => app.evaluate(({ clipboard }) => clipboard.readText())).toBe('C:/e2e/b.webp')
  await expect(page.getByTestId('capture-status')).toHaveText('Copied the path of b.webp.')

  // (b) the WebP shot goes through the renderer re-encode; the PNG shot is passed through.
  for (const [index, name] of [[1, 'b.webp'], [2, 'c.png']] as const) {
    await primeTransparentClipboard(app)
    await thumbs.nth(index).click({ button: 'right' })
    await expect(menu).toBeVisible()
    await page.getByTestId('capture-filmstrip-menu-copy-image').click()
    await expect(page.getByTestId('capture-status')).toHaveText(`Copied ${name} as an image.`)
    const probe = await readSettledClipboardImage(app, name)
    expect(probe.empty, name).toBe(false)
    expect({ width: probe.width, height: probe.height }, name).toEqual({ width: SHOT_W, height: SHOT_H })
    expect(passesShotPixels(probe), `${name} ${JSON.stringify(probe)}`).toBe(true)
  }
  await expect(thumbs.nth(0)).toHaveAttribute('aria-current', 'true')
  await app.close()
})

const NOT_AN_IMAGE = 'not an image av-kit can open (png, jpg, jpeg, webp)'
const PASTED_NAME = /^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}(_\d+)?\.png$/

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
  bodies: Record<string, unknown>[]
  setInbox: (dir: string) => void
  close: () => Promise<void>
}

async function startBackend(inboxDir: string): Promise<Backend> {
  const bodies: Record<string, unknown>[] = []
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
          tool_lock: false,
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
        bodies.push(body)
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
          source: body.mode === 'import' ? 'import' : String(body.source ?? 'gui'),
          created_at: '2026-11-10T10:00:00Z',
          updated_at: '2026-11-10T10:00:00Z',
        }
        rows.push(row)
        send(res, 201, body.mode === 'import' ? { item: row } : row)
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
    bodies,
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
  root: string
  inboxA: string
  inboxB: string
  close: () => Promise<void>
}

async function launch(): Promise<Harness> {
  const root = mkdtempSync(join(tmpdir(), 'avkit-e2e-import-'))
  const inboxA = join(root, 'inbox-a')
  const inboxB = join(root, 'inbox-b')
  mkdirSync(inboxA, { recursive: true })
  mkdirSync(inboxB, { recursive: true })
  const backend = await startBackend(inboxA)

  const app = await launchElectron({
    env: {
      AVKIT_E2E_API_BASE: backend.base,
      AVKIT_APP_DATA: mkdtempSync(join(tmpdir(), 'avkit-e2e-import-data-')),
    },
  })
  const page = await app.firstWindow()
  await page.getByTestId('nav-capture').click()
  await expect(page.getByTestId('capture-page')).toBeVisible()
  // Wait for main to adopt this run's inbox, so nothing can land in the developer's real one.
  await expect(page.getByTestId('capture-inbox-path')).toHaveValue(inboxA, { timeout: 20_000 })

  return {
    app,
    page,
    backend,
    root,
    inboxA,
    inboxB,
    close: async () => {
      await app.close()
      await backend.close()
    },
  }
}

function pngs(dir: string): string[] {
  return readdirSync(dir).filter((name) => name.toLowerCase().endsWith('.png'))
}

function slashes(path: string): string {
  return path.replace(/\\/g, '/')
}

function registerBodies(backend: Backend): Record<string, unknown>[] {
  return backend.bodies.filter((body) => body.mode === 'register')
}

/** The nth register body, with its path in forward slashes. */
function registerBody(backend: Backend, index: number): Record<string, unknown> {
  const body = registerBodies(backend)[index] ?? {}
  return { ...body, path: slashes(String(body.path)) }
}

/** The toast's message without its Dismiss label. */
async function toastMessage(page: Page): Promise<string> {
  const all = (await page.getByTestId('bulk-toast').textContent()) ?? ''
  const dismiss = (await page.getByTestId('bulk-toast-dismiss').textContent()) ?? ''
  return all.replace(dismiss, '').trim()
}

type SavedClipboard = {
  formats: string[]
  text: string
  html: string
  rtf: string
  image: string | null
  size: { width: number; height: number } | null
  bitmap: string | null
}

async function readClipboard(app: ElectronApplication): Promise<SavedClipboard> {
  return app.evaluate(({ clipboard }) => {
    const image = clipboard.readImage()
    const empty = image.isEmpty()
    return {
      formats: clipboard.availableFormats(),
      text: clipboard.readText(),
      html: clipboard.readHTML(),
      rtf: clipboard.readRTF(),
      image: empty ? null : image.toPNG().toString('base64'),
      size: empty ? null : image.getSize(),
      bitmap: empty ? null : image.toBitmap().toString('base64'),
    }
  })
}

/** D-560 A: one write of everything saved, or a clear when nothing was on the clipboard. */
async function restoreClipboard(app: ElectronApplication, saved: SavedClipboard): Promise<void> {
  await app.evaluate(({ clipboard, nativeImage }, value) => {
    if (value.formats.length === 0) {
      clipboard.clear()
      return
    }
    const data: Parameters<typeof clipboard.write>[0] = {}
    if (value.text.length > 0) {
      data.text = value.text
    }
    if (value.html.length > 0) {
      data.html = value.html
    }
    if (value.rtf.length > 0) {
      data.rtf = value.rtf
    }
    if (value.image !== null) {
      data.image = nativeImage.createFromBuffer(Buffer.from(value.image, 'base64'))
    }
    clipboard.write(data)
  }, saved)
}

function describeFormats(label: string, formats: string[]): void {
  console.log(`[D-560] clipboard formats ${label}: ${formats.length === 0 ? '(none)' : formats.join(', ')}`)
}

test('AC-132.23 Ctrl+V pastes a clipboard image into the configured inbox, and text fields keep their paste', async () => {
  test.setTimeout(120_000)
  const h = await launch()
  let saved: SavedClipboard | null = null
  let wrote = false
  try {
    const page = h.page
    const toast = page.getByTestId('bulk-toast')
    const notAnImage = `Imported 0 of 1. 1 failed: sample.mp4 - ${NOT_AN_IMAGE}`

    // 1. The button: the E2E dialog answers C:/e2e/sample.mp4.
    await page.getByTestId('capture-import').click()
    await expect(toast).toBeVisible({ timeout: 10_000 })
    await expect.poll(() => toastMessage(page)).toBe(notAnImage)

    // 2. A test PNG on the clipboard, then Ctrl+V on the page body.
    saved = await readClipboard(h.app)
    describeFormats('before', saved.formats)
    await h.app.evaluate(({ clipboard, nativeImage }) => {
      const bitmap = Buffer.alloc(8 * 8 * 4)
      for (let i = 0; i < bitmap.length; i += 4) {
        bitmap[i] = 255
        bitmap[i + 1] = 128
        bitmap[i + 2] = 0
        bitmap[i + 3] = 255
      }
      clipboard.writeImage(nativeImage.createFromBitmap(bitmap, { width: 8, height: 8 }))
    })
    wrote = true
    await page.evaluate(() => {
      ;(document.activeElement as HTMLElement | null)?.blur()
    })
    await page.keyboard.press('Control+V')
    await expect.poll(() => pngs(h.inboxA).length, { timeout: 15_000 }).toBe(1)
    const first = pngs(h.inboxA)[0] as string
    expect(first).toMatch(PASTED_NAME)
    await expect.poll(() => toastMessage(page)).toBe(`Pasted as ${first}.`)
    await expect.poll(() => registerBodies(h.backend).length).toBe(1)
    expect(registerBody(h.backend, 0)).toEqual({ mode: 'register', source: 'gui', path: slashes(join(h.inboxA, first)) })

    // 3. Tab reaches the button and Enter activates it.
    await page.getByTestId('capture-region').focus()
    await page.keyboard.press('Tab')
    expect(await page.evaluate(() => document.activeElement?.getAttribute('data-testid'))).toBe('capture-import')
    await page.keyboard.press('Enter')
    await expect.poll(() => toastMessage(page)).toBe(notAnImage)

    // 4. The inbox moves with no wait for main's poll; the next paste lands in the new folder.
    h.backend.setInbox(h.inboxB)
    await page.keyboard.press('Control+V')
    await expect.poll(() => pngs(h.inboxB).length, { timeout: 15_000 }).toBe(1)
    const second = pngs(h.inboxB)[0] as string
    expect(second).toMatch(PASTED_NAME)
    await expect.poll(() => toastMessage(page)).toBe(`Pasted as ${second}.`)
    await expect(toast).toHaveCount(1)
    await expect.poll(() => registerBodies(h.backend).length).toBe(2)
    expect(registerBody(h.backend, 1)).toEqual({ mode: 'register', source: 'gui', path: slashes(join(h.inboxB, second)) })
    expect(pngs(h.inboxA)).toEqual([first])

    // 5. Ctrl+V in the inbox field keeps the field's own paste and adds no file.
    const field = page.getByTestId('capture-inbox-path')
    if (!(await field.isVisible())) {
      await page.getByTestId('capture-settings-toggle').click()
    }
    await field.focus()
    await page.keyboard.press('Control+V')
    await page.waitForTimeout(2000)
    expect(pngs(h.inboxA)).toEqual([first])
    expect(pngs(h.inboxB)).toEqual([second])
    expect(registerBodies(h.backend)).toHaveLength(2)
  } finally {
    try {
      if (wrote && saved !== null) {
        await restoreClipboard(h.app, saved)
        const after = await readClipboard(h.app)
        describeFormats('after', after.formats)
        const lost = saved.formats.filter((format) => !after.formats.includes(format))
        expect(lost, 'S13: clipboard formats lost by the restore').toEqual([])
        expect(after.text, 'S13: clipboard text').toBe(saved.text)
        expect(after.html, 'S13: clipboard HTML').toBe(saved.html)
        expect(after.rtf, 'S13: clipboard RTF').toBe(saved.rtf)
        expect(after.size, 'S13: clipboard image size').toEqual(saved.size)
        expect(after.bitmap, 'S13: clipboard image bitmap').toBe(saved.bitmap)
      }
    } finally {
      await h.close()
    }
  }
})
