import { _electron, expect, test, type ElectronApplication, type Page } from '@playwright/test'
import { mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

// Session 38 (MEU-88/89): the filmstrip thumbnail menu and range delete in the built app.
// Its seam is stateful: a per-id DELETE ledger, per-id failures, and per-id image bytes, so the
// Copy image oracle (SHOT_PIXELS) reads real decoded pixels back from the main-process clipboard.

const here = dirname(fileURLToPath(import.meta.url))

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
  return _electron.launch({
    args: [resolve(here, '../../out/main/index.js')],
    env: {
      ...process.env,
      AVKIT_E2E: '1',
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
          return json({ inbox_dir: '~/Pictures/av-kit', hotkey: 'F2', copy_to_clipboard: false, close_to_tray: true })
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

async function deleteLedger(page: Page): Promise<string[]> {
  return page.evaluate(() => [...((window as unknown as SeamState).__e2eDeletes ?? [])])
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

test('AC-88.12 (c) Shift+F10 and the ContextMenu key open the menu from a focused thumb', async () => {
  const { app, page, thumbs } = await openCapture([SHOT_A, SHOT_B])
  const menu = page.getByTestId('capture-filmstrip-menu')
  const thumb = thumbs.nth(1)
  for (const key of ['Shift+F10', 'ContextMenu']) {
    await thumb.focus()
    await thumb.press(key)
    await expect(menu, key).toBeVisible()
    await expect(page.getByTestId('capture-filmstrip-menu-copy-path'), key).toBeFocused()
    await expect(menu).toHaveCount(1)
    await page.keyboard.press('Escape')
    await expect(menu).toHaveCount(0)
    await expect(thumb, key).toBeFocused()
  }
  await app.close()
})

test('AC-88.12 (d)(e) menu Delete on a non-selected shot removes only it; no menu while a confirm is open', async () => {
  const { app, page, thumbs } = await openCapture([SHOT_A, SHOT_B, SHOT_C])
  const menu = page.getByTestId('capture-filmstrip-menu')

  // (e) the toolbar confirm locks the filmstrip: a right-click opens nothing.
  await page.getByTestId('capture-delete').click()
  await expect(page.getByTestId('capture-confirm-strip')).toBeVisible()
  await thumbs.nth(1).click({ button: 'right', force: true })
  await expect(menu).toHaveCount(0)
  await page.getByTestId('capture-delete-confirm-cancel').click()

  // (d)
  await thumbs.nth(1).click({ button: 'right' })
  await expect(menu).toBeVisible()
  await page.getByTestId('capture-filmstrip-menu-delete').click()
  await expect(page.getByTestId('capture-confirm-strip')).toContainText('Delete "b.webp" and its files from disk?')
  await page.getByTestId('capture-delete-confirm').click()
  await expect(thumbs).toHaveCount(2)
  expect(await deleteLedger(page)).toEqual(['e2e-b'])
  await expect(thumbs.nth(0)).toHaveAttribute('aria-current', 'true')
  await expect(page.getByTestId('capture-filmstrip-name')).toHaveText(['a.png', 'c.png'])
  await app.close()
})

const SHOT_D = sampleShot('e2e-d', 'd.png', '2026-10-14T09:00:00Z')
// RANGE_ORDER for the batch below: the filmstrip shows newest first.
const RANGE_ORDER = ['e2e-a', 'e2e-b', 'e2e-c']

test('AC-89.9 Shift-click range, batch menu, ordered deletes with a reported failure, and a cancelled batch', async () => {
  const { app, page, thumbs } = await openCapture([SHOT_A, SHOT_B, SHOT_C, SHOT_D], ['e2e-b'])
  const menu = page.getByTestId('capture-filmstrip-menu')
  const marked = page.locator('[data-testid="capture-filmstrip-item"][data-in-range="true"]')

  // No prior click: the auto-selected newest shot anchors the range.
  await thumbs.nth(2).click({ modifiers: ['Shift'] })
  await expect(marked).toHaveCount(3)
  await expect(thumbs.nth(3)).not.toHaveAttribute('data-in-range', 'true')
  await expect(thumbs.nth(2)).toHaveAttribute('aria-current', 'true')

  await thumbs.nth(1).click({ button: 'right' })
  await expect(menu).toBeVisible()
  await expect(menu.getByRole('menuitem')).toHaveText(['Delete 3 shots'])
  await expect(page.getByTestId('capture-filmstrip-menu-copy-path')).toHaveCount(0)
  await page.getByTestId('capture-filmstrip-menu-delete-batch').click()
  await expect(page.getByTestId('capture-confirm-strip')).toContainText('Delete 3 captures and their files from disk?')
  await page.getByTestId('capture-delete-confirm').click()

  await expect(thumbs).toHaveCount(2)
  await expect(page.getByTestId('capture-filmstrip-name')).toHaveText(['b.webp', 'd.png'])
  await expect(page.getByTestId('capture-status')).toHaveText('Deleted 2 of 3 shots. Could not delete b.webp: file is locked')
  expect(await deleteLedger(page)).toEqual(RANGE_ORDER)
  await expect(marked).toHaveCount(0)

  // A second batch, cancelled: no DELETE leaves the page.
  await thumbs.nth(1).click({ modifiers: ['Shift'] })
  await expect(marked).toHaveCount(2)
  await thumbs.nth(0).click({ button: 'right' })
  await page.getByTestId('capture-filmstrip-menu-delete-batch').click()
  await expect(page.getByTestId('capture-confirm-strip')).toContainText('Delete 2 captures and their files from disk?')
  await page.getByTestId('capture-delete-confirm-cancel').click()
  await expect(page.getByTestId('capture-confirm-strip')).toHaveCount(0)
  expect(await deleteLedger(page)).toEqual(RANGE_ORDER)
  await expect(thumbs).toHaveCount(2)
  await expect(marked).toHaveCount(2)
  await app.close()
})

test('AC-89.15 a checkbox left of each thumb; ticking the first and third deletes both in filmstrip order', async () => {
  const { app, page, thumbs } = await openCapture([SHOT_A, SHOT_B, SHOT_C])
  const checks = page.getByTestId('capture-filmstrip-check')
  const menu = page.getByTestId('capture-filmstrip-menu')

  await expect(checks).toHaveCount(3)
  for (let index = 0; index < 3; index += 1) {
    await expect(checks.nth(index)).toBeVisible()
    const box = await checks.nth(index).boundingBox()
    const thumb = await thumbs.nth(index).boundingBox()
    expect(box).not.toBeNull()
    expect(thumb).not.toBeNull()
    if (box === null || thumb === null) {
      return
    }
    expect(box.x + box.width).toBeLessThanOrEqual(thumb.x)
    const middle = box.y + box.height / 2
    expect(middle).toBeGreaterThan(thumb.y)
    expect(middle).toBeLessThan(thumb.y + thumb.height)
  }

  await checks.nth(0).check()
  await checks.nth(2).check()
  await expect(checks.nth(1)).not.toBeChecked()
  await thumbs.nth(2).click({ button: 'right' })
  await expect(menu).toBeVisible()
  await expect(menu.getByRole('menuitem')).toHaveText(['Delete 2 shots'])
  await page.getByTestId('capture-filmstrip-menu-delete-batch').click()
  await expect(page.getByTestId('capture-confirm-strip')).toContainText('Delete 2 captures and their files from disk?')
  await page.getByTestId('capture-delete-confirm').click()

  await expect(thumbs).toHaveCount(1)
  await expect(page.getByTestId('capture-filmstrip-name')).toHaveText(['b.webp'])
  expect(await deleteLedger(page)).toEqual(['e2e-a', 'e2e-c'])
  await app.close()
})
