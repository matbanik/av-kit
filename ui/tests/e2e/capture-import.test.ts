import { _electron, expect, test, type ElectronApplication, type Page } from '@playwright/test'
import { createServer, type IncomingMessage, type Server, type ServerResponse } from 'node:http'
import { mkdirSync, mkdtempSync, readdirSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

/**
 * MEU-132 (Session 61) IMPORT_ELECTRON: AC-132.22 (a drop) and AC-132.23 (a paste) in the real app.
 *
 * The stub backend is copied from capture-picker.test.ts `startBackend`. It answers
 * `POST /captures` `mode: "import"` with 201 `{item}` and `mode: "register"` as that file does,
 * and records every body. Every PNG is built in main with `nativeImage.createFromBitmap` and
 * written under this test's temp root; nothing is read from or sent to the network.
 *
 * The paste proof uses the system clipboard as D-560 A rules: main saves its text, HTML, RTF and
 * image first, and `finally` restores them only if this test wrote to it, then reads them back
 * and fails on any difference (S13). The formats before and after are printed for the receipt.
 */

const here = dirname(fileURLToPath(import.meta.url))

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

  const app = await _electron.launch({
    args: [resolve(here, '../../out/main/index.js')],
    env: {
      ...process.env,
      AVKIT_E2E: '1',
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

/** An 8x8 PNG of one colour, built in main (BGRA bitmap), as bytes. */
async function mainPng(app: ElectronApplication, bgra: [number, number, number, number]): Promise<Buffer> {
  const encoded = await app.evaluate(({ nativeImage }, pixel) => {
    const bitmap = Buffer.alloc(8 * 8 * 4)
    for (let i = 0; i < bitmap.length; i += 4) {
      bitmap[i] = pixel[0]
      bitmap[i + 1] = pixel[1]
      bitmap[i + 2] = pixel[2]
      bitmap[i + 3] = pixel[3]
    }
    return nativeImage.createFromBitmap(bitmap, { width: 8, height: 8 }).toPNG().toString('base64')
  }, bgra)
  return Buffer.from(encoded, 'base64')
}

function pngs(dir: string): string[] {
  return readdirSync(dir).filter((name) => name.toLowerCase().endsWith('.png'))
}

function slashes(path: string): string {
  return path.replace(/\\/g, '/')
}

function importBodies(backend: Backend): Record<string, unknown>[] {
  return backend.bodies.filter((body) => body.mode === 'import')
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

test('AC-132.22 a drop of two PNGs and a text file imports the two images in order', async () => {
  const h = await launch()
  try {
    const red = join(h.root, 'red.png')
    const notes = join(h.root, 'notes.txt')
    const green = join(h.root, 'green.png')
    writeFileSync(red, await mainPng(h.app, [0, 0, 255, 255]))
    writeFileSync(notes, 'not an image\n', 'utf8')
    writeFileSync(green, await mainPng(h.app, [0, 255, 0, 255]))

    await h.page.evaluate(() => {
      const input = document.createElement('input')
      input.type = 'file'
      input.multiple = true
      input.id = 's61-drop-files'
      input.style.display = 'none'
      document.body.append(input)
    })
    await h.page.locator('#s61-drop-files').setInputFiles([red, notes, green])
    const prevented = await h.page.evaluate(() => {
      const input = document.getElementById('s61-drop-files') as HTMLInputElement
      const transfer = new DataTransfer()
      for (const file of Array.from(input.files ?? [])) {
        transfer.items.add(file)
      }
      const target = document.querySelector('[data-testid="capture-page"]') as HTMLElement
      const fire = (type: string): boolean =>
        !target.dispatchEvent(new DragEvent(type, { bubbles: true, cancelable: true, dataTransfer: transfer }))
      const over = fire('dragover')
      const dropped = fire('drop')
      input.remove()
      return { over, dropped }
    })

    const toast = h.page.getByTestId('bulk-toast')
    await expect(toast).toBeVisible({ timeout: 10_000 })
    await expect.poll(() => toastMessage(h.page)).toBe(`Imported 2 of 3. 1 failed: notes.txt - ${NOT_AN_IMAGE}`)
    expect(prevented).toEqual({ over: true, dropped: true })
    expect(importBodies(h.backend).map((body) => slashes(String(body.path)))).toEqual([slashes(red), slashes(green)])
    expect(registerBodies(h.backend)).toEqual([])
  } finally {
    await h.close()
  }
})

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
