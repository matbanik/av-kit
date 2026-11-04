import { _electron, expect, test, type Page } from '@playwright/test'
import { spawn, type ChildProcess } from 'node:child_process'
import { mkdtempSync, readFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))

/** MEU-80 HINT_TIMING (`components/ui/Tooltip.tsx`): a hover shows after the delay; a leave hides after the grace. */
const HINT_DELAY_MS = 400
const HINT_GRACE_MS = 120

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

const PNG_1X1 = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==',
  'base64',
)

/** `size` is the optional ZOOM_SHOT override (Session 29); every existing caller keeps the 8×8 default. */
function sampleShot(
  id: string,
  name: string,
  createdAt: string,
  size: { width: number; height: number } = { width: 8, height: 8 },
): CaptureItem {
  return {
    id,
    original_path: `C:/e2e/${name}`,
    annotated_path: null,
    sidecar_path: null,
    display_name: name,
    width: size.width,
    height: size.height,
    file_size: 32,
    source: 'gui',
    created_at: createdAt,
    updated_at: createdAt,
  }
}

async function clickSampleImagePoint(page: Page, x: number, y: number): Promise<void> {
  const surface = page.getByTestId('capture-draw-surface')
  const box = await surface.boundingBox()
  expect(box).toBeTruthy()
  const scale = Math.min((box?.width ?? 1) / 8, (box?.height ?? 1) / 8)
  const originX = ((box?.width ?? 0) - 8 * scale) / 2
  const originY = ((box?.height ?? 0) - 8 * scale) / 2
  await surface.click({ position: { x: originX + x * scale, y: originY + y * scale } })
}

async function launchApp() {
  return _electron.launch({
    args: [resolve(here, '../../out/main/index.js')],
    env: {
      ...process.env,
      AVKIT_E2E: '1',
      AVKIT_APP_DATA: mkdtempSync(join(tmpdir(), 'avkit-e2e-capture-')),
    },
  })
}

function isCapturesCollection(pathname: string): boolean {
  return /\/api\/v1\/captures\/?$/.test(pathname) || /\/captures\/?$/.test(pathname)
}

async function installSeam(page: Page, seed: CaptureItem[] = []): Promise<void> {
  const items = [...seed]
  let captureSettings = {
    inbox_dir: '~/Pictures/av-kit',
    hotkey: 'F2',
    copy_to_clipboard: false,
    close_to_tray: true,
  }
  await page.route((url) => url.pathname.includes('/health/dependencies'), async (route) => {
    await route.fulfill({
      json: { ffmpeg: { available: true, version: '7.1.2' }, yt_dlp: { available: true } },
    })
  })
  await page.route((url) => url.pathname.includes('/settings/capture'), async (route) => {
    const request = route.request()
    if (request.method() === 'PUT') {
      const body = request.postDataJSON() as Partial<typeof captureSettings>
      captureSettings = { ...captureSettings, ...body }
      await route.fulfill({ json: captureSettings })
      return
    }
    await route.fulfill({ json: captureSettings })
  })
  await page.route((url) => url.pathname.includes('/captures/requests'), async (route) => {
    await route.fulfill({ json: { items: [] } })
  })
  await page.route((url) => url.pathname.includes('/image'), async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'image/png',
      body: PNG_1X1,
    })
  })
  await page.route((url) => isCapturesCollection(url.pathname), async (route) => {
    const method = route.request().method()
    if (method === 'GET') {
      await route.fulfill({ json: { items: [...items] } })
      return
    }
    if (method === 'POST') {
      await route.fulfill({ json: { items: [...items] }, status: 201 })
      return
    }
    await route.fulfill({ json: { items: [...items] } })
  })
  await page.route((url) => url.pathname.includes('/captures/'), async (route) => {
    const method = route.request().method()
    if (method === 'DELETE') {
      items.splice(0, items.length)
      await route.fulfill({ status: 204, body: '' })
      return
    }
    if (method === 'POST') {
      await route.fulfill({ json: items[0] ?? sampleShot('e2e-cap-1', 'a.png', '2026-08-27T00:00:00Z') })
      return
    }
    await route.fulfill({ json: items[0] ?? {} })
  })
  await page.addInitScript((seeded: CaptureItem[]) => {
    const state = window as unknown as { __e2eSeamInstalled?: boolean; __e2eCaptures?: CaptureItem[] }
    state.__e2eSeamInstalled = true
    state.__e2eCaptures = seeded
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
        return json({
          inbox_dir: '~/Pictures/av-kit',
          hotkey: 'F2',
          copy_to_clipboard: false,
          close_to_tray: true,
        })
      }
      if (url.includes('/captures/requests')) {
        return json({ items: [] })
      }
      if (url.includes('/image')) {
        const bytes = Uint8Array.from([
          137, 80, 78, 71, 13, 10, 26, 10, 0, 0, 0, 13, 73, 72, 68, 82, 0, 0, 0, 1, 0, 0, 0, 1, 8, 6, 0, 0, 0,
          31, 21, 196, 137, 0, 0, 0, 13, 73, 68, 65, 84, 120, 156, 99, 0, 1, 0, 0, 5, 0, 1, 13, 10, 45, 180, 0,
          0, 0, 0, 73, 69, 78, 68, 174, 66, 96, 130,
        ])
        return new Response(bytes, { status: 200, headers: { 'Content-Type': 'image/png' } })
      }
      const path = new URL(url).pathname
      if (/\/captures\/?$/.test(path) && method === 'GET') {
        return json({ items: state.__e2eCaptures ?? [] })
      }
      if (path.includes('/captures/') && method === 'DELETE') {
        state.__e2eCaptures = []
        return new Response(null, { status: 204 })
      }
      if (path.includes('/annotate') && method === 'POST') {
        return json(state.__e2eCaptures?.[0] ?? {})
      }
      return original(input, init)
    }
  }, seed)
  await page.reload()
  await page.getByTestId('downloader-page').waitFor()
}

test('W9-1 Capture home shows capture-page', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page)
  await page.getByTestId('nav-capture').click()
  await expect(page.getByTestId('capture-page')).toBeVisible()
  await app.close()
})

test('W9-2 nav-capture shows capture-page with zero POST /captures', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page)
  let capturePostCount = 0
  page.on('request', (req) => {
    if (req.method() === 'POST' && new URL(req.url()).pathname === '/api/v1/captures') {
      capturePostCount += 1
    }
  })
  await page.getByTestId('nav-capture').click()
  await expect(page.getByTestId('capture-page')).toBeVisible()
  expect(capturePostCount).toBe(0)
  await app.close()
})

test('W9-3 capture controls visible interact tools fill inbox and settings [TA-18]', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page)
  await page.getByTestId('nav-capture').click()
  await expect(page.getByTestId('capture-page')).toBeVisible()
  await expect(page.getByTestId('capture-region')).toBeVisible()
  await expect(page.getByTestId('capture-filmstrip')).toBeVisible()
  await expect(page.getByTestId('capture-viewport')).toBeVisible()
  await expect(page.getByTestId('capture-tool-arrow')).toBeVisible()
  await expect(page.getByTestId('capture-tool-box')).toBeVisible()
  await expect(page.getByTestId('capture-tool-highlight')).toBeVisible()
  await expect(page.getByTestId('capture-tool-text')).toBeVisible()
  await expect(page.getByTestId('capture-undo')).toBeVisible()
  await expect(page.getByTestId('capture-redo')).toBeVisible()
  // TM-2 (CP1): Save overlay mounts only when the overlay is dirty; with no shot it is absent.
  await expect(page.getByTestId('capture-save')).toHaveCount(0)
  await expect(page.getByTestId('capture-delete')).toBeVisible()
  await expect(page.getByTestId('capture-open-file')).toBeVisible()
  await expect(page.getByTestId('capture-open-folder')).toBeVisible()
  // TM-4 (OQ-3): the Settings disclosure starts closed; open it before its controls (setup only).
  await page.getByTestId('capture-settings-toggle').click()
  await expect(page.getByTestId('capture-inbox-path')).toBeVisible()
  await expect(page.getByTestId('capture-inbox-browse')).toBeVisible()
  await expect(page.getByTestId('capture-hotkey')).toBeVisible()
  await expect(page.getByTestId('capture-hotkey-change')).toBeVisible()
  await expect(page.getByTestId('capture-status')).toBeVisible()
  await expect(page.getByTestId('capture-empty')).toBeVisible()
  // HEADER_STATUS: the banner is mounted only while the hotkey is in use.
  const hotkey = await page.evaluate(async () => window.api.getHotkeyStatus())
  if (hotkey.inUse) {
    await expect(page.getByTestId('capture-hotkey-banner')).toBeVisible()
  } else {
    await expect(page.getByTestId('capture-hotkey-banner')).toHaveCount(0)
  }
  await expect(page.getByTestId('capture-hotkey')).toBeEnabled()
  // TM-3 (CP5, OQ-2): with no shot the tools are visible but disabled.
  for (const id of ['capture-tool-arrow', 'capture-tool-box', 'capture-tool-highlight', 'capture-tool-text']) {
    await expect(page.getByTestId(id)).toBeDisabled()
  }
  await page.getByTestId('capture-undo').click({ force: true })
  await page.getByTestId('capture-redo').click({ force: true })
  await page.getByTestId('capture-inbox-path').fill('C:/Pictures/av-kit-e2e')
  await page.getByTestId('capture-page-save').click()
  await page.getByTestId('capture-color').fill('#E0AF68')
  await page.getByTestId('capture-stroke').fill('3')
  await page.getByTestId('nav-settings').click()
  await expect(page.getByTestId('capture-settings')).toBeVisible()
  await expect(page.getByTestId('settings-leaf-capture-inbox_dir')).toBeVisible()
  await expect(page.getByTestId('settings-leaf-hotkey')).toBeVisible()
  await expect(page.getByTestId('settings-leaf-copy_to_clipboard')).toBeVisible()
  await expect(page.getByTestId('settings-leaf-close_to_tray')).toBeVisible()
  await expect(page.getByTestId('browse-capture-path-btn')).toBeVisible()
  await expect(page.getByTestId('capture-settings-save')).toBeVisible()
  await page.getByTestId('settings-leaf-capture-inbox_dir').fill('~/Pictures/av-kit')
  await page.getByTestId('settings-leaf-hotkey').fill('F2')
  await page.getByTestId('settings-leaf-copy_to_clipboard').click()
  await page.getByTestId('settings-leaf-close_to_tray').click()
  await page.getByTestId('browse-capture-path-btn').click()
  await page.getByTestId('capture-settings-save').click()
  await app.close()
})

test('W9-4 region stub shows filmstrip then delete confirm click', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await page.route((url) => url.pathname.includes('/captures'), async (route) => {
    await route.fallback()
  })
  await installSeam(page, [
    sampleShot('e2e-cap-1', 'a.png', '2026-08-27T12:00:00Z'),
  ])
  await page.getByTestId('nav-capture').click()
  await page.getByTestId('capture-region').click()
  await expect(page.getByTestId('capture-filmstrip-item')).toBeVisible()
  await page.getByTestId('capture-filmstrip-item').first().click()
  await expect(page.getByTestId('capture-viewport-image')).toBeVisible()
  await page.evaluate(() => {
    const state = window as unknown as { __e2eCaptures?: Array<{ id: string }> }
    const extra = {
      id: 'e2e-cap-2',
      original_path: 'C:/e2e/b.png',
      annotated_path: null,
      sidecar_path: null,
      display_name: 'b.png',
      width: 8,
      height: 8,
      file_size: 32,
      source: 'gui',
      created_at: '2026-08-27T11:00:00Z',
      updated_at: '2026-08-27T11:00:00Z',
    }
    state.__e2eCaptures = [...(state.__e2eCaptures ?? []), extra]
  })
  await page.getByTestId('nav-settings').click()
  await page.getByTestId('nav-capture').click()
  await page.getByTestId('capture-filmstrip-item').first().click()
  await page.getByTestId('capture-tool-arrow').click()
  const surface = page.getByTestId('capture-draw-surface')
  const box = await surface.boundingBox()
  expect(box).toBeTruthy()
  const scale = Math.min((box?.width ?? 1) / 8, (box?.height ?? 1) / 8)
  const originX = (box?.x ?? 0) + ((box?.width ?? 0) - 8 * scale) / 2
  const originY = (box?.y ?? 0) + ((box?.height ?? 0) - 8 * scale) / 2
  await page.mouse.move(originX + 2 * scale, originY + 2 * scale)
  await page.mouse.down()
  await page.mouse.move(originX + 6 * scale, originY + 6 * scale)
  await page.mouse.up()
  await expect(page.locator('[data-annotation-type="arrow"]')).toHaveCount(1)
  await page.getByTestId('capture-filmstrip-item').nth(1).click()
  await page.getByTestId('capture-dirty-confirm-cancel').click()
  await page.getByTestId('capture-filmstrip-item').nth(1).click()
  await page.getByTestId('capture-dirty-confirm').click()
  await page.getByTestId('capture-delete').click()
  await page.getByTestId('capture-delete-confirm-cancel').click()
  await page.getByTestId('capture-delete').click()
  await page.getByTestId('capture-delete-confirm').click()
  await app.close()
})

test('W9-5 capture controls enabled or disabled by selection', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page)
  await page.getByTestId('nav-capture').click()
  await expect(page.getByTestId('capture-region')).toBeEnabled()
  // TM-2 (CP1): no shot, no dirty overlay, so Save overlay is not mounted.
  await expect(page.getByTestId('capture-save')).toHaveCount(0)
  await expect(page.getByTestId('capture-delete')).toBeDisabled()
  await expect(page.getByTestId('capture-open-file')).toBeDisabled()
  await expect(page.getByTestId('capture-open-folder')).toBeEnabled()
  await expect(page.getByTestId('capture-undo')).toBeDisabled()
  await expect(page.getByTestId('capture-redo')).toBeDisabled()
  await expect(page.getByTestId('capture-inbox-browse')).toBeEnabled()
  await expect(page.getByTestId('capture-hotkey-change')).toBeEnabled()
  await app.close()
})

test('W9-6 capture:region palette delivers with zero POST /captures', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page)
  let capturePostCount = 0
  page.on('request', (req) => {
    if (req.method() === 'POST' && new URL(req.url()).pathname === '/api/v1/captures') {
      capturePostCount += 1
    }
  })
  await page.getByTestId('header-palette-btn').click()
  await page.getByTestId('command-palette-input').fill('capture:region')
  await expect(page.getByRole('dialog').getByRole('button', { name: 'Capture region' })).toHaveCount(0)
  await page.getByTestId('command-palette-input').fill('Capture')
  await page.getByRole('dialog').getByRole('button', { name: /^Capture( ?Ctrl\+5)?$/ }).click()
  await expect(page).toHaveURL(/#\/capture/)
  await expect(page.getByTestId('capture-page')).toBeVisible()
  await page.getByTestId('header-palette-btn').click()
  await page.getByTestId('command-palette-input').fill('capture:region')
  await page.getByRole('dialog').getByRole('button', { name: 'Capture region' }).click()
  await expect(page.getByTestId('capture-page')).toBeVisible()
  expect(capturePostCount).toBe(0)
  await app.close()
})

test('W9-7 delayed backend does not unhandled-reject the capture request poll', async () => {
  const app = await _electron.launch({
    args: [resolve(here, '../../out/main/index.js')],
    env: {
      ...process.env,
      AVKIT_E2E: '1',
      AVKIT_E2E_BACKEND_DELAY_MS: '800',
      AVKIT_APP_DATA: mkdtempSync(join(tmpdir(), 'avkit-e2e-capture-delay-')),
    },
  })
  const proc = app.process()
  expect(proc, 'electron process must be available').toBeTruthy()
  expect(proc?.stderr, 'electron stderr must be captured').toBeTruthy()
  let stderr = ''
  proc?.stderr?.on('data', (chunk: Buffer | string) => {
    stderr += chunk.toString()
  })
  await app.firstWindow()
  await new Promise<void>((resolve) => {
    setTimeout(resolve, 1200)
  })
  expect(stderr).not.toMatch(/UnhandledPromiseRejectionWarning: Error: backend not ready/)
  await app.close()
})

test('AC-59.12 arrow and text marks survive Save then reload', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const shot = sampleShot('e2e-ann-1', 'ann.png', '2026-09-19T12:00:00Z')
  await installSeam(page, [shot])
  await installAnnotationStore(page)
  await page.getByTestId('nav-capture').click()
  await expect(page.getByTestId('capture-page')).toBeVisible()
  await page.getByTestId('capture-filmstrip-item').first().click()
  await expect(page.getByTestId('capture-viewport-image')).toBeVisible()
  // TM-7 (CP1): readiness is CAPTURE_READY_SIGNAL on a clean shot; Save is not mounted yet.
  await expect(page.getByTestId('capture-draw-surface')).toHaveAttribute('data-overlay-ready', 'true')
  await expect(page.getByTestId('capture-save')).toHaveCount(0)
  await page.getByTestId('capture-tool-arrow').click()
  const surface = page.getByTestId('capture-draw-surface')
  const box = await surface.boundingBox()
  expect(box).toBeTruthy()
  const imageW = 8
  const imageH = 8
  const scale = Math.min((box?.width ?? 1) / imageW, (box?.height ?? 1) / imageH)
  const originX = (box?.x ?? 0) + ((box?.width ?? 0) - imageW * scale) / 2
  const originY = (box?.y ?? 0) + ((box?.height ?? 0) - imageH * scale) / 2
  await page.mouse.move(originX + 2 * scale, originY + 2 * scale)
  await page.mouse.down()
  await page.mouse.move(originX + 6 * scale, originY + 6 * scale)
  await page.mouse.up()
  await expect(page.locator('[data-annotation-type="arrow"]')).toHaveCount(1)
  await page.getByTestId('capture-tool-text').click()
  await page.getByTestId('capture-font-size').fill('18')
  await clickSampleImagePoint(page, 3, 6)
  await page.getByTestId('capture-text-draft').fill('Note')
  await page.getByTestId('capture-text-draft').press('Enter')
  await expect(page.locator('[data-annotation-type="text"]')).toHaveCount(1)
  await page.getByTestId('capture-save').click()
  const posted = await page.evaluate(() => {
    const stored = (window as unknown as { __e2eAnnotations?: Record<string, unknown[]> }).__e2eAnnotations ?? {}
    return stored['e2e-ann-1'] ?? []
  })
  const arrow = posted.find((row) => (row as { type?: string }).type === 'arrow') as {
    from: number[]
    to: number[]
  }
  const text = posted.find((row) => (row as { type?: string }).type === 'text') as {
    x: number
    y: number
    text: string
    font_size: number
  }
  expect(arrow.from).toEqual([2, 2])
  expect(arrow.to).toEqual([6, 6])
  expect(text).toMatchObject({ x: 3, y: 6, text: 'Note', font_size: 18 })
  await expect(page.getByTestId('capture-status')).toHaveText('')
  await page.getByTestId('nav-settings').click()
  await page.getByTestId('nav-capture').click()
  await page.getByTestId('capture-filmstrip-item').first().click()
  // TM-7 (CP1): the reloaded marks are saved, so the shot is clean and Save is not mounted.
  await expect(page.getByTestId('capture-draw-surface')).toHaveAttribute('data-overlay-ready', 'true')
  await expect(page.getByTestId('capture-save')).toHaveCount(0)
  await expect(page.locator('[data-annotation-type="arrow"]')).toHaveCount(1)
  await expect(page.locator('[data-annotation-type="text"]')).toHaveCount(1)
  await expect(page.getByTestId('capture-view-original')).toBeVisible()
  await expect(page.getByTestId('capture-view-annotated')).toBeVisible()
  await page.getByTestId('capture-tool-arrow').click()
  await expect(page.getByTestId('capture-text-bg')).toBeHidden()
  await app.close()
})

test('AC-60.12 edit until Save: create arrow+text, drag ends and text, typed hex, Apply, Save, reload, annotated has no SVG [TA-19]', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const shot = sampleShot('e2e-edit-1', 'edit.png', '2026-09-20T12:00:00Z')
  await installSeam(page, [shot])
  await page.evaluate(() => {
    const state = window as unknown as { __e2eAnnotations?: Record<string, unknown[]> }
    state.__e2eAnnotations = {}
    const original = window.fetch.bind(window)
    window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
      const method = (init?.method ?? 'GET').toUpperCase()
      const json = (body: unknown, status = 200) =>
        new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
      const path = new URL(url).pathname
      const stored = (window as unknown as { __e2eAnnotations?: Record<string, unknown[]> }).__e2eAnnotations ?? {}
      if (path.includes('/annotate') && method === 'POST') {
        const body = typeof init?.body === 'string' ? JSON.parse(init.body) : {}
        const id = path.split('/').filter(Boolean).at(-2) ?? 'e2e-edit-1'
        stored[id] = Array.isArray(body.annotations) ? body.annotations : []
        const captures = (window as unknown as { __e2eCaptures?: CaptureItem[] }).__e2eCaptures ?? []
        const shot = captures.find((row) => row.id === id)
        if (shot !== undefined) {
          shot.annotated_path = shot.original_path.replace(/\.png$/i, '.annotated.png')
        }
        return json({ ...(shot ?? { ok: true }), annotations: stored[id] })
      }
      if (/\/captures\/[^/]+$/.test(path) && method === 'GET') {
        const id = path.split('/').filter(Boolean).at(-1) ?? ''
        const items = (window as unknown as { __e2eCaptures?: CaptureItem[] }).__e2eCaptures ?? []
        const item = items.find((row) => row.id === id)
        return json({ ...(item ?? {}), annotations: stored[id] ?? [] })
      }
      return original(input, init)
    }
    const proto = CanvasRenderingContext2D.prototype
    proto.getImageData = function getImageData(sx: number, sy: number, sw: number, sh: number) {
      const image = new ImageData(Math.max(1, sw), Math.max(1, sh))
      for (let i = 0; i < image.data.length; i += 4) {
        image.data[i] = 18
        image.data[i + 1] = 171
        image.data[i + 2] = 205
        image.data[i + 3] = 255
      }
      return image
    }
  })
  await page.getByTestId('nav-capture').click()
  await expect(page.getByTestId('capture-page')).toBeVisible()
  await page.getByTestId('capture-filmstrip-item').first().click()
  await expect(page.getByTestId('capture-draw-surface')).toBeVisible()
  // TM-7 (CP1): readiness is CAPTURE_READY_SIGNAL on a clean shot; Save is not mounted yet.
  await expect(page.getByTestId('capture-draw-surface')).toHaveAttribute('data-overlay-ready', 'true')
  await expect(page.getByTestId('capture-save')).toHaveCount(0)
  await page.getByTestId('capture-tool-arrow').click()
  const surface = page.getByTestId('capture-draw-surface')
  const box = await surface.boundingBox()
  expect(box).toBeTruthy()
  const imageW = 8
  const imageH = 8
  const scale = Math.min((box?.width ?? 1) / imageW, (box?.height ?? 1) / imageH)
  const originX = (box?.x ?? 0) + ((box?.width ?? 0) - imageW * scale) / 2
  const originY = (box?.y ?? 0) + ((box?.height ?? 0) - imageH * scale) / 2
  const at = (x: number, y: number) => ({ x: originX + x * scale, y: originY + y * scale })
  const start = at(2, 2)
  const end = at(6, 6)
  await page.mouse.move(start.x, start.y)
  await page.mouse.down()
  await page.mouse.move(end.x, end.y)
  await page.mouse.up()
  await expect(page.locator('[data-annotation-type="arrow"]')).toHaveCount(1)
  const fromHandle = page.getByTestId('capture-handle-from')
  const toHandle = page.getByTestId('capture-handle-to')
  await expect(fromHandle).toBeVisible()
  await expect(toHandle).toBeVisible()
  const fromBox = await fromHandle.boundingBox()
  const toBox = await toHandle.boundingBox()
  expect(fromBox).toBeTruthy()
  expect(toBox).toBeTruthy()
  await page.mouse.move((fromBox?.x ?? 0) + (fromBox?.width ?? 1) / 2, (fromBox?.y ?? 0) + (fromBox?.height ?? 1) / 2)
  await page.mouse.down()
  const newFrom = at(1, 3)
  await page.mouse.move(newFrom.x, newFrom.y)
  await page.mouse.up()
  await page.mouse.move((toBox?.x ?? 0) + (toBox?.width ?? 1) / 2, (toBox?.y ?? 0) + (toBox?.height ?? 1) / 2)
  await page.mouse.down()
  const newTo = at(7, 4)
  await page.mouse.move(newTo.x, newTo.y)
  await page.mouse.up()
  await page.getByTestId('capture-tool-text').click()
  await page.getByTestId('capture-font-size').fill('2')
  await clickSampleImagePoint(page, 3, 6)
  await page.getByTestId('capture-text-draft').fill('Note')
  await page.getByTestId('capture-text-draft').press('Enter')
  await expect(page.locator('[data-annotation-type="text"]')).toHaveCount(1)
  await expect(page.getByTestId('capture-text-draft')).toHaveCount(0)
  await page.getByTestId('capture-tool-select').click()
  await expect(page.getByTestId('capture-tool-select')).toHaveAttribute('aria-pressed', 'true')
  await page.getByTestId('capture-mark-list').locator('button', { hasText: 'Text' }).click()
  await page.evaluate(() => {
    const surface = document.querySelector('[data-testid="capture-draw-surface"]')
    if (!(surface instanceof HTMLElement)) {
      throw new Error('capture-draw-surface missing')
    }
    const box = surface.getBoundingClientRect()
    const imageW = 8
    const imageH = 8
    const scale = Math.min(box.width / imageW, box.height / imageH)
    const ox = (box.width - imageW * scale) / 2
    const oy = (box.height - imageH * scale) / 2
    const client = (x: number, y: number) => ({ x: box.left + ox + x * scale, y: box.top + oy + y * scale })
    const from = client(3, 6)
    const to = client(0, 1)
    const fire = (type: string, x: number, y: number, buttons: number) => {
      surface.dispatchEvent(
        new PointerEvent(type, {
          bubbles: true,
          cancelable: true,
          composed: true,
          clientX: x,
          clientY: y,
          pointerId: 1,
          pointerType: 'mouse',
          buttons,
        }),
      )
    }
    fire('pointerdown', from.x, from.y, 1)
    fire('pointermove', to.x, to.y, 1)
    fire('pointerup', to.x, to.y, 0)
  })
  await page.getByTestId('capture-mark-list').locator('button').first().click()
  await page.getByTestId('capture-color').fill('#12ABCD')
  await expect(page.getByTestId('capture-color')).toHaveValue('#12ABCD')
  await page.getByTestId('capture-color-apply').click()
  await expect(page.getByTestId('capture-save')).toBeEnabled()
  await page.getByTestId('capture-save').click()
  const posted = await page.evaluate(() => {
    const stored = (window as unknown as { __e2eAnnotations?: Record<string, unknown[]> }).__e2eAnnotations ?? {}
    return stored['e2e-edit-1'] ?? []
  })
  expect(posted.length).toBe(2)
  const arrow = posted.find((row) => (row as { type?: string }).type === 'arrow') as {
    from: number[]
    to: number[]
    color: string
  }
  const text = posted.find((row) => (row as { type?: string }).type === 'text') as { x: number; y: number }
  expect(arrow.from).not.toEqual([2, 2])
  expect(arrow.to).not.toEqual([6, 6])
  expect(arrow.color.toUpperCase()).toBe('#12ABCD')
  expect(text.x).not.toBe(3)
  await page.getByTestId('nav-settings').click()
  await page.getByTestId('nav-capture').click()
  await page.getByTestId('capture-filmstrip-item').first().click()
  await page.getByTestId('capture-view-annotated').click()
  await expect(page.locator('[data-testid="capture-annotation"]')).toHaveCount(0)
  await expect(page.getByTestId('capture-status')).toHaveText('')
  await app.close()
})

// ── MEU-57 Capture page layout (Phase 11 §Capture) — AC-57.10 real-Electron wave ───────────

// The seam answers some calls inside window.fetch without touching the network, so request
// events cannot see them. Record every renderer fetch (method + URL) in a page-side ledger.
async function installFetchLedger(page: Page): Promise<void> {
  await page.evaluate(() => {
    const state = window as unknown as { __e2eLedger?: string[] }
    state.__e2eLedger = []
    const inner = window.fetch.bind(window)
    window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
      state.__e2eLedger?.push(`${(init?.method ?? 'GET').toUpperCase()} ${url}`)
      return inner(input, init)
    }
  })
}

async function ledger(page: Page, prefix: string, fragment: string): Promise<number> {
  return page.evaluate(
    ([p, f]) =>
      ((window as unknown as { __e2eLedger?: string[] }).__e2eLedger ?? []).filter(
        (row) => row.startsWith(p) && row.includes(f),
      ).length,
    [prefix, fragment] as const,
  )
}

async function drawArrow(page: Page): Promise<void> {
  const surface = page.getByTestId('capture-draw-surface')
  const box = await surface.boundingBox()
  expect(box).toBeTruthy()
  const scale = Math.min((box?.width ?? 1) / 8, (box?.height ?? 1) / 8)
  const originX = (box?.x ?? 0) + ((box?.width ?? 0) - 8 * scale) / 2
  const originY = (box?.y ?? 0) + ((box?.height ?? 0) - 8 * scale) / 2
  await page.mouse.move(originX + 2 * scale, originY + 2 * scale)
  await page.mouse.down()
  await page.mouse.move(originX + 6 * scale, originY + 6 * scale)
  await page.mouse.up()
}

test('AC-57.10 header: key cap follows hotkey registration; Settings disclosure opens and saves once', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page, [sampleShot('e2e-l-1', 'a.png', '2026-09-03T12:00:00Z')])
  await installFetchLedger(page)
  await page.getByTestId('nav-capture').click()
  await expect(page.getByTestId('capture-page')).toBeVisible()
  const status = await page.evaluate(async () => window.api.getHotkeyStatus())
  const keycap = page.getByTestId('capture-hotkey-keycap')
  if (status.registered) {
    await expect(keycap).toBeVisible()
    await expect(page.getByTestId('capture-region')).toContainText(status.accelerator)
  } else {
    await expect(keycap).toHaveCount(0)
  }
  await expect(page.getByTestId('capture-region')).toContainText('Capture region')
  const toggle = page.getByTestId('capture-settings-toggle')
  await expect(toggle).toHaveAttribute('aria-expanded', 'false')
  await expect(page.getByTestId('capture-inbox-path')).toBeHidden()
  await toggle.click()
  await expect(toggle).toHaveAttribute('aria-expanded', 'true')
  await expect(page.getByTestId('capture-inbox-path')).toBeVisible()
  expect(await ledger(page, 'PUT', '/settings/capture')).toBe(0)
  await page.getByTestId('capture-inbox-path').fill('C:/Pictures/av-kit-layout')
  expect(await ledger(page, 'PUT', '/settings/capture')).toBe(0)
  await expect(page.getByTestId('capture-page-save')).toHaveClass(/btn-save-dirty/)
  await expect(page.getByTestId('capture-page-save')).toContainText('Save settings')
  await page.getByTestId('capture-page-save').click()
  await expect.poll(() => ledger(page, 'PUT', '/settings/capture')).toBe(1)
  await app.close()
})

test('AC-57.10 filmstrip: 200px column, stripped name, time line, aria-current', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page, [
    sampleShot('e2e-l-1', '2026-09-03 14-22-08 settings-dialog.png', '2026-09-03T14:22:08Z'),
    sampleShot('e2e-l-2', 'queue-card-menu.png', '2026-09-03T14:19:51Z'),
  ])
  await page.getByTestId('nav-capture').click()
  const film = page.getByTestId('capture-filmstrip')
  await expect(film).toBeVisible()
  const aside = await film.evaluate((node) => node.closest('aside')?.getBoundingClientRect().width ?? 0)
  expect(aside).toBeGreaterThanOrEqual(190)
  expect(aside).toBeLessThanOrEqual(210)
  await expect(page.getByTestId('capture-filmstrip-name').first()).toHaveText('14-22-08 settings-dialog.png')
  await expect(page.getByTestId('capture-filmstrip-time').first()).toHaveText(/^\d{2}:\d{2}:\d{2}$/)
  await expect(page.getByTestId('capture-filmstrip-item').first()).toHaveAttribute('aria-current', 'true')
  await expect(page.getByTestId('capture-filmstrip-item').nth(1)).not.toHaveAttribute('aria-current', 'true')
  await app.close()
})

test('AC-57.10 no shot: tools disabled, no Save overlay, empty state inside the viewport', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page)
  await page.getByTestId('nav-capture').click()
  for (const id of ['capture-tool-select', 'capture-tool-arrow', 'capture-tool-box', 'capture-tool-highlight', 'capture-tool-text']) {
    await expect(page.getByTestId(id)).toBeDisabled()
  }
  await expect(page.getByTestId('capture-save')).toHaveCount(0)
  await expect(page.getByTestId('capture-viewport').getByTestId('capture-empty')).toBeVisible()
  await expect(page.getByTestId('capture-draw-surface')).toHaveCount(0)
  await expect(page.getByTestId('capture-shot-info')).toHaveText('')
  await app.close()
})

test('AC-57.10 Save overlay mount rule, inline confirm strips and shot info versus status [TA-20]', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page, [
    sampleShot('e2e-l-1', 'a.png', '2026-09-03T12:00:00Z'),
    sampleShot('e2e-l-2', 'b.png', '2026-09-03T11:00:00Z'),
  ])
  await installFetchLedger(page)
  await page.getByTestId('nav-capture').click()
  await page.getByTestId('capture-filmstrip-item').first().click()
  await expect(page.getByTestId('capture-draw-surface')).toHaveAttribute('data-overlay-ready', 'true')
  await expect(page.getByTestId('capture-save')).toHaveCount(0)
  await expect(page.getByTestId('capture-shot-info')).toHaveText('a.png · 8×8')
  await expect(page.getByTestId('capture-status')).toHaveText('')
  await page.getByTestId('capture-tool-arrow').click()
  await drawArrow(page)
  await expect(page.locator('[data-annotation-type="arrow"]')).toHaveCount(1)
  await expect(page.getByTestId('capture-save')).toBeEnabled()
  await expect(page.getByTestId('capture-save')).toHaveAttribute('aria-label', 'Save overlay')
  await expect(page.getByTestId('capture-filmstrip-item').first()).toHaveAttribute('data-dirty', 'true')
  await page.getByTestId('capture-filmstrip-item').nth(1).click()
  const strip = page.getByTestId('capture-viewport').getByTestId('capture-confirm-strip')
  await expect(strip).toBeVisible()
  await expect(strip).toContainText('Discard unsaved overlay marks on this shot?')
  await expect(page.getByTestId('capture-dirty-confirm-cancel')).toBeFocused()
  await expect(page.getByTestId('capture-filmstrip-item').nth(1)).toBeDisabled()
  await page.getByTestId('capture-dirty-confirm-cancel').click()
  await expect(strip).toHaveCount(0)
  await page.getByTestId('capture-delete').click()
  await expect(page.getByTestId('capture-delete-confirm')).toHaveText('Delete capture')
  await expect(page.getByTestId('capture-delete-confirm-cancel')).toBeFocused()
  await page.getByTestId('capture-delete-confirm-cancel').click()
  await expect(page.getByTestId('capture-confirm-strip')).toHaveCount(0)
  expect(await ledger(page, 'DELETE', '/captures/')).toBe(0)
  await expect(page.getByTestId('capture-filmstrip-item')).toHaveCount(2)
  await app.close()
})

// ── MEU-65 Capture toolbar icons and Options (Session 29 plan AC-65.4, AC-65.5) ───────────────────

/**
 * WINDOW_SETTLED (Session 29 plan; copied from `download-queue.test.ts` `windowSettled`). The app
 * window resizes once just after launch (1280x800 -> 1280x773 as it is shown), so a geometry read
 * waits for a shown window at full frame rate and then 500 ms without a resize.
 */
async function windowSettled(page: Page): Promise<void> {
  await page.waitForFunction(() => document.visibilityState === 'visible')
  const shown = await page.evaluate(
    () =>
      new Promise<boolean>((resolve) => {
        const deadline = performance.now() + 15_000
        let last = performance.now()
        let fast = 0
        const tick = (now: number): void => {
          fast = now - last < 50 ? fast + 1 : 0
          last = now
          if (fast >= 6) {
            resolve(true)
          } else if (now > deadline) {
            resolve(false)
          } else {
            requestAnimationFrame(tick)
          }
        }
        requestAnimationFrame(tick)
      }),
  )
  if (!shown) {
    throw new Error('E2E_WINDOW_SHOWN: the window never reached full-rate frames within 15 s')
  }
  await page.evaluate(
    () =>
      new Promise<void>((resolve) => {
        const quiet = 500
        let timer = window.setTimeout(done, quiet)
        function onResize(): void {
          window.clearTimeout(timer)
          timer = window.setTimeout(done, quiet)
        }
        function done(): void {
          window.removeEventListener('resize', onResize)
          resolve()
        }
        window.addEventListener('resize', onResize)
      }),
  )
}

async function twoFrames(page: Page): Promise<void> {
  await page.evaluate(
    () =>
      new Promise<void>((resolve) => {
        requestAnimationFrame(() => requestAnimationFrame(() => resolve()))
      }),
  )
}

type RowBox = { scroll: number; client: number }

async function chromeRows(
  page: Page,
): Promise<{ tools: RowBox | null; options: RowBox | null; marks: RowBox | null; width: number }> {
  return page.evaluate(() => {
    const read = (id: string): { scroll: number; client: number } | null => {
      const row = document.querySelector(`[data-testid="${id}"]`)
      return row instanceof HTMLElement ? { scroll: row.scrollWidth, client: row.clientWidth } : null
    }
    return {
      tools: read('capture-chrome-tools'),
      options: read('capture-chrome-options'),
      marks: read('capture-chrome-marks'),
      width: window.innerWidth,
    }
  })
}

async function expectNoOverflow(page: Page, label: string): Promise<void> {
  await twoFrames(page)
  const rows = await chromeRows(page)
  const where = `${label} at innerWidth ${rows.width}`
  expect(rows.tools?.scroll ?? Number.POSITIVE_INFINITY, `${where}: capture-chrome-tools scrollWidth`).toBeLessThanOrEqual(
    rows.tools?.client ?? 0,
  )
  expect(
    rows.options?.scroll ?? Number.POSITIVE_INFINITY,
    `${where}: capture-chrome-options scrollWidth`,
  ).toBeLessThanOrEqual(rows.options?.client ?? 0)
  expect(rows.marks?.scroll ?? Number.POSITIVE_INFINITY, `${where}: capture-chrome-marks scrollWidth`).toBeLessThanOrEqual(
    rows.marks?.client ?? 0,
  )
}

test('AC-65.4 NO_OVERFLOW at the default window: tools, options and marks rows never scroll for any tool or a selected text mark [TA-21]', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page, [sampleShot('e2e-ovf-1', 'a.png', '2026-10-01T12:00:00Z')])
  await page.getByTestId('nav-capture').click()
  await page.getByTestId('capture-filmstrip-item').first().click()
  await page.waitForSelector('[data-testid="capture-draw-surface"][data-overlay-ready="true"]')
  await windowSettled(page)
  for (const tool of ['select', 'arrow', 'box', 'highlight', 'text', 'pixelate', 'eraser']) {
    await page.getByTestId(`capture-tool-${tool}`).click()
    await expectNoOverflow(page, `tool ${tool}`)
  }
  await page.getByTestId('capture-tool-text').click()
  await clickSampleImagePoint(page, 4, 4)
  await page.getByTestId('capture-text-draft').fill('Note')
  await page.getByTestId('capture-text-draft').press('Enter')
  await expect(page.getByTestId('capture-tool-select')).toHaveAttribute('aria-pressed', 'true')
  await expect(page.getByTestId('capture-font-size')).toBeVisible()
  await expectNoOverflow(page, 'selected text mark')
  await app.close()
})

test('AC-65.5 header Options button: accessible name, secondary fill, icon, chevron follows aria-expanded', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page, [sampleShot('e2e-opt-1', 'a.png', '2026-10-01T12:00:00Z')])
  await page.getByTestId('nav-capture').click()
  const toggle = page.getByTestId('capture-settings-toggle')
  await expect(page.getByRole('button', { name: 'Options', exact: true })).toHaveCount(1)
  await expect(toggle).toHaveAccessibleName('Options')
  await expect(toggle).toHaveClass(/btn-secondary/)
  await expect(toggle).not.toContainText('Settings')
  await expect(toggle.locator('svg').first()).toBeVisible()
  const chevron = page.getByTestId('capture-settings-chevron')
  await expect(chevron).toBeVisible()
  await expect(toggle).toHaveAttribute('aria-expanded', 'false')
  await expect(chevron).toHaveAttribute('data-state', 'closed')
  await expect(page.getByTestId('capture-inbox-path')).toBeHidden()
  await toggle.click()
  await expect(toggle).toHaveAttribute('aria-expanded', 'true')
  await expect(chevron).toHaveAttribute('data-state', 'open')
  await expect(page.getByTestId('capture-inbox-path')).toBeVisible()
  await toggle.click()
  await expect(toggle).toHaveAttribute('aria-expanded', 'false')
  await expect(chevron).toHaveAttribute('data-state', 'closed')
  await expect(page.getByTestId('capture-inbox-path')).toBeHidden()
  await app.close()
})

// ── MEU-66 Capture viewport zoom (Session 29 plan AC-66.12 – AC-66.15; ZOOM_SHOT 2400×1600) ─────────

/** Chromium kPresetBrowserZoomFactorsArray, restated for the oracle (plan D-14; AC-66.1 pins the product copy). */
const LADDER = [0.25, 1 / 3, 0.5, 2 / 3, 0.75, 0.8, 0.9, 1, 1.1, 1.25, 1.5, 1.75, 2, 2.5, 3, 4, 5]
const ZOOM_W = 2400
const ZOOM_H = 1600

type ZoomRead = {
  kind: string | null
  s: number
  ox: number
  oy: number
  left: number
  top: number
  width: number
  height: number
  readout: string
  scrollTops: number[]
}

async function readZoom(page: Page): Promise<ZoomRead> {
  // Two frames first, so a ResizeObserver re-measure from the last render has landed in the observables.
  await twoFrames(page)
  return page.evaluate(() => {
    const surface = document.querySelector('[data-testid="capture-draw-surface"]') as HTMLElement
    const rect = surface.getBoundingClientRect()
    const scrollers = [document.scrollingElement, document.querySelector('main')].filter(
      (node): node is Element => node !== null,
    )
    return {
      kind: surface.getAttribute('data-zoom-kind'),
      s: Number(surface.getAttribute('data-zoom-scale')),
      ox: Number(surface.getAttribute('data-zoom-ox')),
      oy: Number(surface.getAttribute('data-zoom-oy')),
      left: rect.left,
      top: rect.top,
      width: rect.width,
      height: rect.height,
      readout: document.querySelector('[data-testid="capture-zoom-level"]')?.textContent ?? '',
      scrollTops: scrollers.map((node) => node.scrollTop),
    }
  })
}

function nextUp(scale: number): number {
  const up = LADDER.find((value) => value > scale + 1e-9)
  if (up === undefined) {
    throw new Error(`no ladder level above ${scale}`)
  }
  return up
}

function nextDown(scale: number): number {
  const down = [...LADDER].reverse().find((value) => value < scale - 1e-9)
  if (down === undefined) {
    throw new Error(`no ladder level below ${scale}`)
  }
  return down
}

function percent(scale: number): string {
  return `${Math.round(scale * 100)}%`
}

function fitScaleOf(view: ZoomRead): number {
  return Math.min(view.width / ZOOM_W, view.height / ZOOM_H)
}

async function pageZoomFactor(app: Awaited<ReturnType<typeof launchApp>>): Promise<number> {
  return app.evaluate(({ BrowserWindow }) => BrowserWindow.getAllWindows()[0]?.webContents.getZoomFactor() ?? -1)
}

async function openZoomShot(page: Page): Promise<void> {
  await installSeam(page, [
    sampleShot('e2e-zoom-1', 'zoom.png', '2026-10-01T12:00:00Z', { width: ZOOM_W, height: ZOOM_H }),
    sampleShot('e2e-zoom-2', 'zoom-b.png', '2026-10-01T11:00:00Z', { width: ZOOM_W, height: ZOOM_H }),
  ])
  await page.getByTestId('nav-capture').click()
  await page.getByTestId('capture-filmstrip-item').first().click()
  await page.waitForSelector('[data-testid="capture-draw-surface"][data-overlay-ready="true"]')
  await windowSettled(page)
}

/** The AC-59.12 seam: annotate POSTs are stored per shot and the detail GET returns them. */
async function installAnnotationStore(page: Page): Promise<void> {
  await page.evaluate(() => {
    const state = window as unknown as {
      __e2eAnnotations?: Record<string, unknown[]>
    }
    state.__e2eAnnotations = {}
    const original = window.fetch.bind(window)
    window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
      const method = (init?.method ?? 'GET').toUpperCase()
      const json = (body: unknown, status = 200) =>
        new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
      const path = new URL(url).pathname
      const stored = (window as unknown as { __e2eAnnotations?: Record<string, unknown[]> }).__e2eAnnotations ?? {}
      if (path.includes('/annotate') && method === 'POST') {
        const body = typeof init?.body === 'string' ? JSON.parse(init.body) : {}
        const id = path.split('/').filter(Boolean).at(-2) ?? 'e2e-ann-1'
        stored[id] = Array.isArray(body.annotations) ? body.annotations : []
        return json({ ok: true })
      }
      if (/\/captures\/[^/]+$/.test(path) && method === 'GET') {
        const id = path.split('/').filter(Boolean).at(-1) ?? ''
        const items = (window as unknown as { __e2eCaptures?: CaptureItem[] }).__e2eCaptures ?? []
        const item = items.find((row) => row.id === id)
        return json({ ...(item ?? {}), annotations: stored[id] ?? [] })
      }
      return original(input, init)
    }
  })
}

/** Installs a fetch ledger that also keeps POST bodies, so the annotate oracle reads the stored pixels. */
async function installBodyLedger(page: Page): Promise<void> {
  await page.evaluate(() => {
    const state = window as unknown as { __e2eBodies?: Array<{ method: string; url: string; body: unknown }> }
    state.__e2eBodies = []
    const inner = window.fetch.bind(window)
    window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
      const body = typeof init?.body === 'string' ? (JSON.parse(init.body) as unknown) : null
      state.__e2eBodies?.push({ method: (init?.method ?? 'GET').toUpperCase(), url, body })
      return inner(input, init)
    }
  })
}

async function annotatePosts(page: Page): Promise<Array<{ annotations: Array<Record<string, unknown>> }>> {
  return page.evaluate(() =>
    ((window as unknown as { __e2eBodies?: Array<{ method: string; url: string; body: unknown }> }).__e2eBodies ?? [])
      .filter((row) => row.method === 'POST' && row.url.includes('/annotate'))
      .map((row) => row.body as { annotations: Array<Record<string, unknown>> }),
  )
}

/**
 * TA-1 (A-3, Session 29): zoom about the cursor, per axis. An axis whose content overflows the frame keeps
 * the cursor's image pixel within 1 px; an axis whose content fits is centred (VIEW_TRANSFORM, 09:636).
 */
function expectAboutCursor(
  view: ZoomRead,
  after: { x: number; y: number },
  before: { x: number; y: number },
  label: string,
): void {
  const axes = [
    { name: 'x', frame: view.width, content: ZOOM_W * view.s, offset: view.ox, moved: after.x - before.x },
    { name: 'y', frame: view.height, content: ZOOM_H * view.s, offset: view.oy, moved: after.y - before.y },
  ]
  expect(axes.some((axis) => axis.content > axis.frame), `${label}: at least one axis overflows`).toBe(true)
  for (const axis of axes) {
    if (axis.content > axis.frame) {
      expect(Math.abs(axis.moved), `${label} ${axis.name}: cursor pixel moved`).toBeLessThanOrEqual(1)
    } else {
      // Sub-pixel tolerance: the observables carry the scale to 4 decimals (1/3 reads 0.3333).
      expect(axis.offset, `${label} ${axis.name}: a fitting axis is centred`).toBeCloseTo((axis.frame - axis.content) / 2, 0)
    }
  }
}

test('AC-66.12 one wheel step zooms about the cursor without page zoom or scroll', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await openZoomShot(page)
  const before = await readZoom(page)
  expect(before.kind).toBe('fit')
  const fit = fitScaleOf(before)
  const cursor = { x: before.left + before.width * 0.3, y: before.top + before.height * 0.4 }
  const imageAt = (view: ZoomRead) => ({
    x: (cursor.x - view.left - view.ox) / view.s,
    y: (cursor.y - view.top - view.oy) / view.s,
  })
  await page.mouse.move(cursor.x, cursor.y)
  await page.mouse.wheel(0, -100)
  await expect(page.getByTestId('capture-zoom-level')).toHaveText(percent(nextUp(fit)))
  const after = await readZoom(page)
  expect(after.s).toBeCloseTo(nextUp(fit), 3)
  expectAboutCursor(after, imageAt(after), imageAt(before), 'wheel')
  expect(await pageZoomFactor(app)).toBe(1)
  expect(after.scrollTops).toEqual(before.scrollTops)
  await page.keyboard.down('Control')
  await page.mouse.wheel(0, -100)
  await page.keyboard.up('Control')
  await expect(page.getByTestId('capture-zoom-level')).toHaveText(percent(nextUp(nextUp(fit))))
  const ctrl = await readZoom(page)
  expectAboutCursor(ctrl, imageAt(ctrl), imageAt(before), 'Ctrl+wheel')
  expect(await pageZoomFactor(app)).toBe(1)
  expect(ctrl.scrollTops).toEqual(before.scrollTops)
  await app.close()
})

test('AC-66.13 zoom buttons and Ctrl+= / Ctrl+- / Ctrl+0 step the image only, from the surface and from body', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await openZoomShot(page)
  const fit = fitScaleOf(await readZoom(page))
  const level = page.getByTestId('capture-zoom-level')
  await page.getByTestId('capture-zoom-in').click()
  await page.getByTestId('capture-zoom-in').click()
  await expect(level).toHaveText(percent(nextUp(nextUp(fit))))
  await page.getByTestId('capture-zoom-out').click()
  await expect(level).toHaveText(percent(nextUp(fit)))
  await page.getByTestId('capture-zoom-fit').click()
  await expect(level).toHaveText('Fit')
  for (const focus of ['surface', 'body'] as const) {
    if (focus === 'surface') {
      await page.getByTestId('capture-draw-surface').focus()
    } else {
      await page.evaluate(() => {
        ;(document.activeElement as HTMLElement | null)?.blur()
      })
    }
    await page.keyboard.press('Control+Equal')
    await expect(level, `${focus} Ctrl+=`).toHaveText(percent(nextUp(fit)))
    expect(await pageZoomFactor(app), `${focus} Ctrl+=`).toBe(1)
    // TA-2 (A-3): a second Ctrl+= first, so Ctrl+- has a ladder level to step back to.
    await page.keyboard.press('Control+Equal')
    await expect(level, `${focus} Ctrl+= twice`).toHaveText(percent(nextUp(nextUp(fit))))
    expect(await pageZoomFactor(app), `${focus} Ctrl+= twice`).toBe(1)
    await page.keyboard.press('Control+Minus')
    await expect(level, `${focus} Ctrl+-`).toHaveText(percent(nextDown(nextUp(nextUp(fit)))))
    expect(await pageZoomFactor(app), `${focus} Ctrl+-`).toBe(1)
    await page.keyboard.press('Control+Digit0')
    await expect(level, `${focus} Ctrl+0`).toHaveText('Fit')
    expect(await pageZoomFactor(app), `${focus} Ctrl+0`).toBe(1)
  }
  await page.getByTestId('capture-zoom-in').click()
  await page.getByTestId('capture-color').focus()
  await page.keyboard.press('Control+Minus')
  await expect(level).toHaveText(percent(nextUp(fit)))
  await app.close()
})

test('AC-66.14 an arrow drawn at 100% stores the zoomed image pixels; a Fit arrow keeps the fit mapping', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await openZoomShot(page)
  await installBodyLedger(page)
  const level = page.getByTestId('capture-zoom-level')
  for (let i = 0; i < LADDER.length && (await level.textContent()) !== '100%'; i += 1) {
    await page.getByTestId('capture-zoom-in').click()
  }
  await expect(level).toHaveText('100%')
  const centred = await readZoom(page)
  await page.mouse.move(centred.left + centred.width / 2, centred.top + centred.height / 2)
  await page.mouse.down({ button: 'middle' })
  await page.mouse.move(centred.left + centred.width / 2 - 40, centred.top + centred.height / 2 - 30)
  await page.mouse.up({ button: 'middle' })
  const view = await readZoom(page)
  expect(view.ox).toBeCloseTo(centred.ox - 40, 3)
  const toClient = (x: number, y: number) => ({ x: view.left + view.ox + x * view.s, y: view.top + view.oy + y * view.s })
  const from = toClient(1200, 800)
  const to = toClient(1260, 830)
  for (const point of [from, to]) {
    expect(point.x).toBeGreaterThan(view.left)
    expect(point.x).toBeLessThan(view.left + view.width)
    expect(point.y).toBeGreaterThan(view.top)
    expect(point.y).toBeLessThan(view.top + view.height)
  }
  const fitS = fitScaleOf(view)
  const fitOx = (view.width - ZOOM_W * fitS) / 2
  const fitOy = (view.height - ZOOM_H * fitS) / 2
  const fitOnly = { x: (from.x - view.left - fitOx) / fitS, y: (from.y - view.top - fitOy) / fitS }
  expect(Math.hypot(fitOnly.x - 1200, fitOnly.y - 800)).toBeGreaterThanOrEqual(50)
  await page.getByTestId('capture-tool-arrow').click()
  await page.mouse.move(from.x, from.y)
  await page.mouse.down()
  await page.mouse.move(to.x, to.y)
  await page.mouse.up()
  await expect(page.locator('[data-annotation-type="arrow"]')).toHaveCount(1)
  await page.getByTestId('capture-save').click()
  await expect.poll(async () => (await annotatePosts(page)).length).toBe(1)
  const first = (await annotatePosts(page))[0]?.annotations[0]
  expect(first?.from).toEqual([1200, 800])
  expect(first?.to).toEqual([1260, 830])
  const line = page.locator('[data-annotation-type="arrow"] line').first()
  await expect(line).toHaveAttribute('x1', '1200')
  await expect(line).toHaveAttribute('y1', '800')
  const mark = page.locator('[data-annotation-type="arrow"]').first()
  await expect(mark).toHaveAttribute('x2', '1260')
  await expect(mark).toHaveAttribute('y2', '830')
  await page.getByTestId('capture-zoom-fit').click()
  await expect(level).toHaveText('Fit')
  const fitView = await readZoom(page)
  const fitClient = (x: number, y: number) => ({
    x: fitView.left + fitView.ox + x * fitView.s,
    y: fitView.top + fitView.oy + y * fitView.s,
  })
  await page.getByTestId('capture-tool-arrow').click()
  const a = fitClient(600, 400)
  const b = fitClient(900, 600)
  await page.mouse.move(a.x, a.y)
  await page.mouse.down()
  await page.mouse.move(b.x, b.y)
  await page.mouse.up()
  await expect(page.locator('[data-annotation-type="arrow"]')).toHaveCount(2)
  await page.getByTestId('capture-save').click()
  await expect.poll(async () => (await annotatePosts(page)).length).toBe(2)
  const second = (await annotatePosts(page))[1]?.annotations ?? []
  expect(second[0]?.from).toEqual([1200, 800])
  expect(second[0]?.to).toEqual([1260, 830])
  expect(second[1]?.from).toEqual([600, 400])
  expect(second[1]?.to).toEqual([900, 600])
  await app.close()
})

test('AC-66.15 a shot change resets to Fit; Space+drag pans at 100% and creates no annotation', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await openZoomShot(page)
  await installBodyLedger(page)
  const level = page.getByTestId('capture-zoom-level')
  await page.getByTestId('capture-zoom-in').click()
  await expect(level).not.toHaveText('Fit')
  await page.getByTestId('capture-filmstrip-item').nth(1).click()
  await expect(level).toHaveText('Fit')
  await expect(page.getByTestId('capture-draw-surface')).toHaveAttribute('data-zoom-kind', 'fit')
  for (let i = 0; i < LADDER.length && (await level.textContent()) !== '100%'; i += 1) {
    await page.getByTestId('capture-zoom-in').click()
  }
  await expect(level).toHaveText('100%')
  const before = await readZoom(page)
  await page.getByTestId('capture-draw-surface').focus()
  const start = { x: before.left + before.width / 2, y: before.top + before.height / 2 }
  await page.keyboard.down('Space')
  await page.mouse.move(start.x, start.y)
  await page.mouse.down()
  await page.mouse.move(start.x + 60, start.y + 40)
  await page.mouse.up()
  await page.keyboard.up('Space')
  const after = await readZoom(page)
  expect(after.ox).toBeCloseTo(before.ox + 60, 3)
  expect(after.oy).toBeCloseTo(before.oy + 40, 3)
  await expect(page.getByTestId('capture-annotation')).toHaveCount(0)
  await expect(page.getByTestId('capture-save')).toHaveCount(0)
  expect(await annotatePosts(page)).toHaveLength(0)
  await app.close()
})

// ── A-4 / A-5 (CAPTURE_LOOK follow-ups): AC-66.18, AC-65.8, AC-66.19 ───────────────────────────────

test('AC-66.18 after a mouse click on the Arrow tool, Space+drag pans and draws nothing (CAPTURE_LOOK L5)', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await openZoomShot(page)
  await installBodyLedger(page)
  const level = page.getByTestId('capture-zoom-level')
  for (let i = 0; i < LADDER.length && (await level.textContent()) !== '100%'; i += 1) {
    await page.getByTestId('capture-zoom-in').click()
  }
  await expect(level).toHaveText('100%')
  await page.getByTestId('capture-tool-arrow').click()
  await expect(page.getByTestId('capture-tool-arrow')).toHaveAttribute('aria-pressed', 'true')
  await expect(page.getByTestId('capture-draw-surface')).toBeFocused()
  const before = await readZoom(page)
  const start = { x: before.left + before.width / 2, y: before.top + before.height / 2 }
  await page.keyboard.down('Space')
  await page.mouse.move(start.x, start.y)
  await page.mouse.down()
  await page.mouse.move(start.x + 60, start.y + 40)
  await page.mouse.up()
  await page.keyboard.up('Space')
  const after = await readZoom(page)
  expect(after.ox).toBeCloseTo(before.ox + 60, 3)
  expect(after.oy).toBeCloseTo(before.oy + 40, 3)
  await expect(page.getByTestId('capture-annotation')).toHaveCount(0)
  await expect(page.getByTestId('capture-save')).toHaveCount(0)
  await app.close()
})

test('AC-65.8 opening the Options panel leaves the Options toggle in place on the header row', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page, [sampleShot('e2e-opt-2', 'a.png', '2026-10-02T12:00:00Z')])
  await page.getByTestId('nav-capture').click()
  await windowSettled(page)
  const toggle = page.getByTestId('capture-settings-toggle')
  const region = await page.getByTestId('capture-region').boundingBox()
  const before = await toggle.boundingBox()
  await toggle.click()
  await expect(page.getByTestId('capture-inbox-path')).toBeVisible()
  await twoFrames(page)
  const after = await toggle.boundingBox()
  expect(Math.abs((after?.y ?? -1) - (before?.y ?? -100)), 'toggle top').toBeLessThanOrEqual(1)
  expect(Math.abs((after?.x ?? -1) - (before?.x ?? -100)), 'toggle left').toBeLessThanOrEqual(1)
  expect(Math.abs((after?.y ?? -1) - (region?.y ?? -100)), 'same row as Capture region').toBeLessThanOrEqual(1)
  await app.close()
})

test('AC-66.19 the Capture page fills main and the draw surface grows into it at the default window', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await openZoomShot(page)
  const layout = await page.evaluate(() => {
    const main = document.querySelector('main') as HTMLElement
    const capture = document.querySelector('[data-testid="capture-page"]') as HTMLElement
    const surface = document.querySelector('[data-testid="capture-draw-surface"]') as HTMLElement
    return {
      mainBottom: main.getBoundingClientRect().bottom,
      pageBottom: capture.getBoundingClientRect().bottom,
      scrollHeight: main.scrollHeight,
      clientHeight: main.clientHeight,
      surfaceHeight: surface.getBoundingClientRect().height,
    }
  })
  expect(Math.abs(layout.pageBottom - layout.mainBottom), `page bottom vs main bottom ${JSON.stringify(layout)}`).toBeLessThanOrEqual(1)
  expect(layout.scrollHeight, 'main does not scroll').toBeLessThanOrEqual(layout.clientHeight)
  expect(layout.surfaceHeight, 'surface grows past its 200 px floor').toBeGreaterThan(210)
  await app.close()
})


// ── MEU-67 Apply to image / Revert (Session 30 plan AC-67.20–24, AC-67.33) ─────────────────
// FIXTURE_REPAIRS (c): a stateful in-page seam that serves flatten/revert, backup_path on the
// detail, the converted shot in the list and the capture settings with the three new leaves.

type FlattenSeed = { shots: CaptureItem[]; marks: Record<string, unknown[]> }

const S30_MARK = { type: 'rect', x: 1, y: 1, width: 4, height: 4, color: '#ff0000', stroke_width: 2 }
const S30_BACKUP = 'C:/e2e/.avkit-backup/a.20261003-120000.png'

async function installFlattenSeam(page: Page, seed: FlattenSeed): Promise<void> {
  await page.addInitScript(
    ([data, backup]: [FlattenSeed, string]) => {
      type Item = (typeof data.shots)[number]
      const state = window as unknown as {
        __e2eSeamInstalled?: boolean
        __s30?: { items: Item[]; details: Record<string, { annotations: unknown[]; backup_path: string | null }>; puts: unknown[] }
      }
      state.__e2eSeamInstalled = true
      const s = {
        items: [...data.shots],
        details: Object.fromEntries(
          data.shots.map((shot) => [shot.id, { annotations: data.marks[shot.id] ?? [], backup_path: null as string | null }]),
        ),
        puts: [] as unknown[],
      }
      state.__s30 = s
      let settings: Record<string, unknown> = {
        inbox_dir: 'C:/e2e',
        hotkey: 'F2',
        copy_to_clipboard: false,
        close_to_tray: true,
        flatten_backup: true,
        backup_dir: '',
        annotated_format: 'png',
      }
      const original = window.fetch.bind(window)
      const png = Uint8Array.from([
        137, 80, 78, 71, 13, 10, 26, 10, 0, 0, 0, 13, 73, 72, 68, 82, 0, 0, 0, 1, 0, 0, 0, 1, 8, 6, 0, 0, 0, 31,
        21, 196, 137, 0, 0, 0, 13, 73, 68, 65, 84, 120, 156, 99, 0, 1, 0, 0, 5, 0, 1, 13, 10, 45, 180, 0, 0, 0, 0,
        73, 69, 78, 68, 174, 66, 96, 130,
      ])
      const json = (body: unknown, status = 200) =>
        new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
      const detailOf = (id: string) => ({ ...s.items.find((row) => row.id === id), ...s.details[id] })
      window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
        const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
        const method = (init?.method ?? 'GET').toUpperCase()
        const path = new URL(url).pathname
        if (path.includes('/health/dependencies')) {
          return json({ ffmpeg: { available: true, version: '7.1.2' }, yt_dlp: { available: true } })
        }
        if (path.endsWith('/settings/capture')) {
          if (method === 'PUT') {
            const body = JSON.parse(String(init?.body ?? '{}')) as Record<string, unknown>
            s.puts.push(body)
            settings = { ...settings, ...body }
          }
          return json(settings)
        }
        if (path.includes('/captures/requests')) {
          return json({ items: [] })
        }
        if (path.endsWith('/image')) {
          return new Response(png, { status: 200, headers: { 'Content-Type': 'image/png' } })
        }
        const action = path.match(/\/captures\/([^/]+)\/(flatten|revert)$/)
        if (action && method === 'POST') {
          const id = action[1] as string
          const stamp = new Date().toISOString()
          if (action[2] === 'flatten' && /\.(jpe?g|webp)$/i.test(s.items.find((row) => row.id === id)?.original_path ?? '')) {
            const source = s.items.find((row) => row.id === id) as Item
            const stem = source.display_name.replace(/\.[^.]+$/, '')
            const converted = {
              ...source,
              id: `${id}-converted`,
              original_path: `C:/e2e/${stem}-converted.png`,
              display_name: `${stem}-converted.png`,
              created_at: stamp,
              updated_at: stamp,
            }
            s.items = [converted, ...s.items]
            s.details[converted.id] = { annotations: [], backup_path: null }
            return json(detailOf(converted.id))
          }
          if (action[2] === 'flatten') {
            s.details[id] = { annotations: [], backup_path: backup }
          }
          s.items = s.items.map((row) => (row.id === id ? { ...row, annotated_path: null, updated_at: stamp } : row))
          return json(detailOf(id))
        }
        const detail = path.match(/\/captures\/([^/]+)$/)
        if (detail && method === 'GET') {
          return json(detailOf(detail[1] as string))
        }
        if (/\/captures\/?$/.test(path) && method === 'GET') {
          return json({ items: s.items })
        }
        if (path.includes('/annotate') && method === 'POST') {
          const id = path.split('/').slice(-2)[0] as string
          const body = JSON.parse(String(init?.body ?? '{}')) as { annotations?: unknown[] }
          s.details[id] = { ...(s.details[id] ?? { backup_path: null }), annotations: body.annotations ?? [] }
          return json(detailOf(id))
        }
        return original(input, init)
      }
    },
    [seed, S30_BACKUP] as [FlattenSeed, string],
  )
  await page.reload()
  await page.getByTestId('downloader-page').waitFor()
}

async function ledgerRows(page: Page): Promise<string[]> {
  return page.evaluate(() => (window as unknown as { __e2eLedger?: string[] }).__e2eLedger ?? [])
}

async function imageFetches(page: Page, id: string): Promise<{ viewport: number; thumb: number }> {
  const rows = await ledgerRows(page)
  return {
    viewport: rows.filter((row) => row.startsWith('GET') && row.includes(`/captures/${id}/image?variant=original`)).length,
    thumb: rows.filter((row) => row.startsWith('GET') && row.endsWith(`/captures/${id}/image`)).length,
  }
}

async function openFlattenShot(page: Page, index = 0): Promise<void> {
  await page.getByTestId('nav-capture').click()
  await page.getByTestId('capture-filmstrip-item').nth(index).click()
  await expect(page.getByTestId('capture-draw-surface')).toHaveAttribute('data-overlay-ready', 'true')
  await expect(page.getByTestId('capture-mark-list').locator('button')).toHaveCount(1)
}

test('AC-67.20 AC-67.21 AC-67.22 Apply: enabled with saved marks, off after an edit; Cancel sends nothing; Confirm bakes once and refetches [TA-22]', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installFlattenSeam(page, {
    shots: [sampleShot('e2e-f-1', 'a.png', '2026-10-03T12:00:00Z')],
    marks: { 'e2e-f-1': [S30_MARK] },
  })
  await installFetchLedger(page)
  await openFlattenShot(page)
  const applyButton = page.getByTestId('capture-apply-image')
  await expect(applyButton).toBeEnabled()
  await page.getByTestId('capture-tool-arrow').click()
  await drawArrow(page)
  await expect(applyButton).toBeDisabled()
  await page.getByTestId('capture-apply-image-tip').hover()
  await expect(page.getByTestId('capture-apply-image-hint')).toHaveText('Apply to image — Save the overlay first')
  await page.getByTestId('capture-undo').click()
  await expect(applyButton).toBeEnabled()
  await applyButton.click()
  await expect(page.getByTestId('capture-confirm-strip')).toContainText(
    'Bake the saved marks into a.png? The original is copied to the backup folder in the inbox first.',
  )
  await expect(page.getByTestId('capture-filmstrip-item').first()).toBeDisabled()
  await expect(page.getByTestId('capture-delete')).toBeDisabled()
  await page.getByTestId('capture-flatten-confirm-cancel').click()
  expect(await ledger(page, 'POST', '/flatten')).toBe(0)
  const before = await imageFetches(page, 'e2e-f-1')
  await applyButton.click()
  await page.getByTestId('capture-flatten-confirm').click()
  await expect(page.getByTestId('capture-status')).toHaveText(`Applied to image. Backup: ${S30_BACKUP}`)
  expect(await ledger(page, 'POST', '/captures/e2e-f-1/flatten')).toBe(1)
  await expect(page.getByTestId('capture-mark-list').locator('button')).toHaveCount(0)
  await expect(page.getByTestId('capture-view-annotated')).toBeDisabled()
  await expect.poll(async () => (await imageFetches(page, 'e2e-f-1')).viewport).toBeGreaterThan(before.viewport)
  await expect.poll(async () => (await imageFetches(page, 'e2e-f-1')).thumb).toBeGreaterThan(before.thumb)
  await app.close()
})

test('AC-67.23 flatten then revert round trip on one shot', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installFlattenSeam(page, {
    shots: [sampleShot('e2e-f-1', 'a.png', '2026-10-03T12:00:00Z')],
    marks: { 'e2e-f-1': [S30_MARK] },
  })
  await installFetchLedger(page)
  await openFlattenShot(page)
  await expect(page.getByTestId('capture-revert-image')).toHaveCount(0)
  await page.getByTestId('capture-apply-image').click()
  await page.getByTestId('capture-flatten-confirm').click()
  await expect(page.getByTestId('capture-status')).toHaveText(`Applied to image. Backup: ${S30_BACKUP}`)
  const revert = page.getByTestId('capture-revert-image')
  await expect(revert).toBeEnabled()
  await revert.click()
  await expect(page.getByTestId('capture-confirm-strip')).toContainText(
    'Replace a.png with its newest backup (a.20261003-120000.png)? The current image is overwritten.',
  )
  await page.getByTestId('capture-revert-confirm-cancel').click()
  expect(await ledger(page, 'POST', '/revert')).toBe(0)
  const before = await imageFetches(page, 'e2e-f-1')
  await revert.click()
  await page.getByTestId('capture-revert-confirm').click()
  await expect(page.getByTestId('capture-status')).toHaveText('Reverted from a.20261003-120000.png.')
  expect(await ledger(page, 'POST', '/captures/e2e-f-1/revert')).toBe(1)
  await expect.poll(async () => (await imageFetches(page, 'e2e-f-1')).viewport).toBeGreaterThan(before.viewport)
  await app.close()
})

test('AC-67.33 a JPEG shot bakes into a new PNG copy that becomes the selection; the JPEG stays', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installFlattenSeam(page, {
    shots: [sampleShot('e2e-j-1', 'photo.jpg', '2026-10-03T11:00:00Z')],
    marks: { 'e2e-j-1': [S30_MARK] },
  })
  await installFetchLedger(page)
  await openFlattenShot(page)
  await page.getByTestId('capture-apply-image').click()
  await expect(page.getByTestId('capture-confirm-strip')).toContainText(
    'Bake the saved marks into a new PNG copy of photo.jpg? photo.jpg itself stays unchanged.',
  )
  await page.getByTestId('capture-flatten-confirm').click()
  await expect(page.getByTestId('capture-status')).toHaveText('Applied to a new PNG copy: photo-converted.png.')
  expect(await ledger(page, 'POST', '/captures/e2e-j-1/flatten')).toBe(1)
  await expect(page.locator('[data-testid="capture-filmstrip-item"][aria-current="true"]')).toContainText(
    'photo-converted.png',
  )
  await expect(page.getByTestId('capture-filmstrip-item')).toHaveCount(2)
  await expect(page.getByTestId('capture-filmstrip-name').filter({ hasText: /^photo\.jpg$/ })).toHaveCount(1)
  await app.close()
})

test('AC-67.24 Settings Capture card shows the three leaves and Save PUTs them', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installFlattenSeam(page, { shots: [], marks: {} })
  await page.getByTestId('nav-settings').click()
  await page.getByTestId('settings-rail-capture').click()
  const backup = page.getByTestId('settings-leaf-flatten_backup')
  await expect(backup).toBeVisible()
  await expect(backup).toBeChecked()
  const dir = page.getByTestId('settings-leaf-capture-backup_dir')
  await expect(dir).toHaveValue('')
  await expect(dir).toHaveAttribute('placeholder', /\.avkit-backup$/)
  await expect(page.getByTestId('settings-capture-backup-browse')).toBeVisible()
  const format = page.getByTestId('settings-leaf-annotated_format')
  await expect(format).toHaveValue('png')
  await backup.uncheck()
  await dir.fill('D:/backups')
  await format.selectOption('jpeg')
  await page.getByTestId('capture-settings-save').click()
  await expect
    .poll(() => page.evaluate(() => (window as unknown as { __s30?: { puts: unknown[] } }).__s30?.puts.length ?? 0))
    .toBe(1)
  const put = await page.evaluate(() => (window as unknown as { __s30?: { puts: unknown[] } }).__s30?.puts[0])
  expect(put).toEqual(
    expect.objectContaining({ flatten_backup: false, backup_dir: 'D:/backups', annotated_format: 'jpeg' }),
  )
  await app.close()
})

test('AC-67.20 A-6 a disabled Apply shows its reason where the pointer lands [TA-23]', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installFlattenSeam(page, {
    shots: [sampleShot('e2e-f-1', 'a.png', '2026-10-03T12:00:00Z')],
    marks: { 'e2e-f-1': [S30_MARK] },
  })
  await openFlattenShot(page)
  await page.getByTestId('capture-tool-arrow').click()
  await drawArrow(page)
  const applyButton = page.getByTestId('capture-apply-image')
  await expect(applyButton).toBeDisabled()
  const box = await applyButton.boundingBox()
  expect(box).toBeTruthy()
  await page.mouse.move((box?.x ?? 0) + (box?.width ?? 0) / 2, (box?.y ?? 0) + (box?.height ?? 0) / 2)
  // MEU-80: the wrapper under the pointer shows the reason through the rendered hint, not a native title.
  const hint = page.getByTestId('capture-apply-image-hint')
  await expect(hint).toBeVisible()
  await expect(hint).toHaveText('Apply to image — Save the overlay first')
  await app.close()
})

test('AC-67.35 A-10 hovering the disabled Apply shows a visible reason label inside the window [TA-24]', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installFlattenSeam(page, {
    shots: [sampleShot('e2e-f-1', 'a.png', '2026-10-03T12:00:00Z')],
    marks: { 'e2e-f-1': [S30_MARK] },
  })
  await openFlattenShot(page)
  const applyButton = page.getByTestId('capture-apply-image')
  const reason = page.getByTestId('capture-apply-image-hint')
  // Enabled: after a real hover and HINT_DELAY_MS the hint shows the plain name; moving away hides it.
  await applyButton.hover()
  await page.waitForTimeout(HINT_DELAY_MS)
  await expect(reason).toHaveText('Apply to image')
  await page.mouse.move(5, 5)
  await page.waitForTimeout(HINT_GRACE_MS)
  await expect(reason).toHaveCount(0)
  await page.getByTestId('capture-tool-arrow').click()
  await drawArrow(page)
  await expect(applyButton).toBeDisabled()
  const box = await applyButton.boundingBox()
  await page.mouse.move((box?.x ?? 0) + (box?.width ?? 0) / 2, (box?.y ?? 0) + (box?.height ?? 0) / 2)
  await expect(reason).toBeVisible()
  await expect(reason).toHaveText('Apply to image — Save the overlay first')
  const tip = await reason.boundingBox()
  const size = page.viewportSize() ?? (await page.evaluate(() => ({ width: window.innerWidth, height: window.innerHeight })))
  expect(tip).toBeTruthy()
  expect((tip?.x ?? -1) >= 0 && (tip?.y ?? -1) >= 0).toBe(true)
  expect((tip?.x ?? 0) + (tip?.width ?? 0)).toBeLessThanOrEqual(size.width)
  await page.mouse.move(5, 5)
  await expect(reason).toHaveCount(0)
  await app.close()
})


test('AC-80.10: a real hover shows the enabled Arrow hint and the disabled Undo hint inside the window; focus and Escape', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page, [sampleShot('e2e-hint-1', 'a.png', '2026-10-14T12:00:00Z')])
  await page.getByTestId('nav-capture').click()
  await page.getByTestId('capture-filmstrip-item').first().click()
  await page.waitForSelector('[data-testid="capture-draw-surface"][data-overlay-ready="true"]')
  await windowSettled(page)
  const size = await page.evaluate(() => ({ width: window.innerWidth, height: window.innerHeight }))
  const expectInside = async (id: string): Promise<void> => {
    const box = await page.getByTestId(id).boundingBox()
    expect(box, `${id} has a box`).toBeTruthy()
    expect((box?.x ?? -1) >= 0 && (box?.y ?? -1) >= 0, `${id} starts inside the window`).toBe(true)
    expect((box?.x ?? 0) + (box?.width ?? 0), `${id} right edge`).toBeLessThanOrEqual(size.width)
    expect((box?.y ?? 0) + (box?.height ?? 0), `${id} bottom edge`).toBeLessThanOrEqual(size.height)
  }
  // Enabled: the Arrow tool, shot open.
  const arrowHint = page.getByTestId('capture-tool-arrow-hint')
  await expect(arrowHint).toHaveCount(0)
  await expect(page.getByTestId('capture-tool-arrow-tip')).toHaveCount(1)
  await page.getByTestId('capture-tool-arrow').hover()
  await page.waitForTimeout(HINT_DELAY_MS)
  await expect(arrowHint).toBeVisible()
  await expect(arrowHint).toHaveAttribute('role', 'tooltip')
  await expect(arrowHint).toHaveText('Arrow')
  await expectInside('capture-tool-arrow-hint')
  await page.mouse.move(5, 5)
  await page.waitForTimeout(HINT_GRACE_MS)
  await expect(arrowHint).toHaveCount(0)
  // Disabled: Undo with no history; the pointer lands on the wrapper.
  const undo = page.getByTestId('capture-undo')
  const undoTip = page.getByTestId('capture-undo-tip')
  const undoHint = page.getByTestId('capture-undo-hint')
  await expect(undo).toBeDisabled()
  await expect(undoTip).toHaveCount(1)
  const box = await undo.boundingBox()
  await page.mouse.move((box?.x ?? 0) + (box?.width ?? 0) / 2, (box?.y ?? 0) + (box?.height ?? 0) / 2)
  await page.waitForTimeout(HINT_DELAY_MS)
  await expect(undoHint).toBeVisible()
  await expect(undoHint).toHaveText('Undo (Ctrl+Z)')
  await expectInside('capture-undo-hint')
  await page.mouse.move(5, 5)
  await page.waitForTimeout(HINT_GRACE_MS)
  await expect(undoHint).toHaveCount(0)
  // Keyboard: the disabled control's wrapper is the tab stop; Escape dismisses.
  await undoTip.focus()
  await expect(undoHint).toBeVisible()
  await page.keyboard.press('Escape')
  await expect(undoHint).toHaveCount(0)
  await app.close()
})


// ── MEU-81 Capture action row (Session 34 plan AC-81.9, AC-81.11, AC-81.14) ──────────────────

/** ACTION_BUTTONS ids, in ACTION_ORDER (Delete last). */
const ACTION_IDS = [
  'capture-remove-mark',
  'capture-save',
  'capture-apply-image',
  'capture-revert-image',
  'capture-open-file',
  'capture-open-folder',
  'capture-delete',
]

/** `capture-hit-test.ts` HANDLE_RADIUS_CSS, restated for the oracle. */
const HANDLE_RADIUS_CSS = 5

const ROW_W = 400
const ROW_H = 300

/** NO_OVERFLOW_FIXTURE: 12 saved marks, 3 per type, inside a 400×300 shot. */
function twelveMarks(): unknown[] {
  const marks: unknown[] = []
  for (let i = 0; i < 3; i += 1) {
    marks.push({ type: 'arrow', color: '#ff0000', stroke_width: 2, from: [20 + i * 40, 20], to: [50 + i * 40, 50] })
  }
  for (let i = 0; i < 3; i += 1) {
    marks.push({ type: 'rect', x: 160 + i * 40, y: 20, width: 30, height: 30, color: '#00aa00', stroke_width: 2 })
  }
  for (let i = 0; i < 3; i += 1) {
    marks.push({ type: 'highlight', x: 20 + i * 40, y: 120, width: 30, height: 15, color: '#ffff00', opacity: 0.4 })
  }
  for (let i = 0; i < 3; i += 1) {
    marks.push({ type: 'text', x: 160 + i * 50, y: 130, text: `T${i}`, color: '#ffffff', font_size: 16, bg_color: null })
  }
  return marks
}

type ActionRowRead = {
  scroll: number
  client: number
  offset: number
  scrollHeight: number
  left: number
  right: number
  top: number
  bottom: number
  tips: Array<{ id: string; left: number; right: number; top: number; bottom: number }>
}

async function readActionRow(page: Page): Promise<ActionRowRead | null> {
  await page.evaluate(async () => {
    await document.fonts.ready
  })
  await twoFrames(page)
  return page.evaluate((ids) => {
    const row = document.querySelector('[data-testid="capture-chrome-marks"]')
    if (!(row instanceof HTMLElement)) {
      return null
    }
    const box = row.getBoundingClientRect()
    const tips = ids.flatMap((id) => {
      const tip = document.querySelector(`[data-testid="${id}-tip"]`)
      if (tip === null) {
        return []
      }
      const rect = tip.getBoundingClientRect()
      return [{ id, left: rect.left, right: rect.right, top: rect.top, bottom: rect.bottom }]
    })
    return {
      scroll: row.scrollWidth,
      client: row.clientWidth,
      offset: row.offsetHeight,
      scrollHeight: row.scrollHeight,
      left: box.left,
      right: box.right,
      top: box.top,
      bottom: box.bottom,
      tips,
    }
  }, ACTION_IDS)
}

async function expectActionRowFits(page: Page, label: string): Promise<void> {
  await expect(page.getByTestId('capture-delete-tip'), `${label}: capture-delete-tip`).toHaveCount(1, { timeout: 5_000 })
  const row = await readActionRow(page)
  expect(row, `${label}: capture-chrome-marks`).not.toBeNull()
  const read = row as ActionRowRead
  expect(read.scroll, `${label}: marks row scrollWidth`).toBeLessThanOrEqual(read.client)
  expect(read.offset, `${label}: marks row offsetHeight equals scrollHeight`).toBe(read.scrollHeight)
  expect(read.offset, `${label}: marks row height`).toBeGreaterThanOrEqual(36)
  for (const tip of read.tips) {
    expect(tip.left, `${label}: ${tip.id}-tip left`).toBeGreaterThanOrEqual(read.left - 0.5)
    expect(tip.right, `${label}: ${tip.id}-tip right`).toBeLessThanOrEqual(read.right + 0.5)
    expect(tip.top, `${label}: ${tip.id}-tip top`).toBeGreaterThanOrEqual(read.top - 0.5)
    expect(tip.bottom, `${label}: ${tip.id}-tip bottom`).toBeLessThanOrEqual(read.bottom + 0.5)
  }
  const rightmost = Math.max(...read.tips.map((tip) => tip.right))
  expect(read.tips.find((tip) => tip.id === 'capture-delete')?.right, `${label}: Delete is rightmost`).toBe(rightmost)
}

test('AC-81.9: NO_OVERFLOW_FIXTURE: the marks row never overflows and every action tip stays inside it, Delete rightmost', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const id = 'e2e-row81-1'
  await installFlattenSeam(page, {
    shots: [sampleShot(id, 'a.png', '2026-10-14T12:00:00Z', { width: ROW_W, height: ROW_H })],
    marks: { [id]: twelveMarks() },
  })
  await page.evaluate(
    ([shot, backup]) => {
      const state = window as unknown as {
        __s30?: { details: Record<string, { annotations: unknown[]; backup_path: string | null }> }
      }
      const detail = state.__s30?.details[shot]
      if (detail !== undefined) {
        detail.backup_path = backup
      }
    },
    [id, S30_BACKUP] as const,
  )
  await page.getByTestId('nav-capture').click()
  await page.getByTestId('capture-filmstrip-item').first().click()
  await expect(page.getByTestId('capture-draw-surface')).toHaveAttribute('data-overlay-ready', 'true')
  await expect(page.getByTestId('capture-mark-list').locator('button')).toHaveCount(12)
  await windowSettled(page)
  // Dirty, with an arrow selected: draw a 13th mark, which commits and selects it.
  const view = await readZoom(page)
  const toClient = (x: number, y: number) => ({ x: view.left + view.ox + x * view.s, y: view.top + view.oy + y * view.s })
  await page.getByTestId('capture-tool-arrow').click()
  const from = toClient(250, 220)
  const to = toClient(350, 270)
  await page.mouse.move(from.x, from.y)
  await page.mouse.down()
  await page.mouse.move(to.x, to.y)
  await page.mouse.up()
  await expect(page.locator('[data-annotation-type="arrow"]')).toHaveCount(4)
  await expect(page.getByTestId('capture-save')).toBeVisible()
  await expect(page.getByTestId('capture-revert-image')).toBeVisible()
  await expect(page.getByTestId('capture-remove-mark')).toBeVisible()
  await expectActionRowFits(page, 'arrow selected, dirty, backup')
  await page.getByTestId('capture-tool-text').click()
  await expectActionRowFits(page, 'Text tool')
  await page.getByTestId('capture-settings-toggle').click()
  await expect(page.getByTestId('capture-settings-toggle')).toHaveAttribute('aria-expanded', 'true')
  await expectActionRowFits(page, 'Options open')
  await app.close()
})

/**
 * HOTKEY_IN_USE_FIXTURE helper: registers F2 (no modifiers) on its own thread, prints HELD, then
 * blocks on GetMessage so the registration lives until the process is killed.
 */
const HOLD_F2 = [
  "$ErrorActionPreference = 'Stop'",
  "Add-Type -Namespace AvKitE2E -Name HotkeyHold -MemberDefinition @'",
  '[System.Runtime.InteropServices.DllImport("user32.dll", SetLastError = true)]',
  'public static extern bool RegisterHotKey(System.IntPtr hWnd, int id, uint fsModifiers, uint vk);',
  '[System.Runtime.InteropServices.DllImport("user32.dll")]',
  'public static extern int GetMessage(out MSG msg, System.IntPtr hWnd, uint min, uint max);',
  '[System.Runtime.InteropServices.StructLayout(System.Runtime.InteropServices.LayoutKind.Sequential)]',
  'public struct MSG { public System.IntPtr hwnd; public uint message; public System.IntPtr wParam; public System.IntPtr lParam; public uint time; public int x; public int y; }',
  "'@",
  'if (-not [AvKitE2E.HotkeyHold]::RegisterHotKey([System.IntPtr]::Zero, 0x5334, 0, 0x71)) {',
  "  [Console]::Out.WriteLine('FAILED ' + [System.Runtime.InteropServices.Marshal]::GetLastWin32Error())",
  '  exit 1',
  '}',
  "[Console]::Out.WriteLine('HELD')",
  '$msg = New-Object AvKitE2E.HotkeyHold+MSG',
  'while ([AvKitE2E.HotkeyHold]::GetMessage([ref]$msg, [System.IntPtr]::Zero, 0, 0) -gt 0) { }',
].join('\n')

/** Resolves 'HELD', the FAILED line, 'timeout' (5 s), the early exit or the spawn error. */
function waitForHold(child: ChildProcess): Promise<string> {
  return new Promise((done) => {
    let out = ''
    const timer = setTimeout(() => finish('timeout'), 5_000)
    function finish(value: string): void {
      clearTimeout(timer)
      done(value)
    }
    child.once('error', (error) => finish(`spawn error ${error.message}`))
    child.once('exit', (code) => finish(`exit ${code} ${out.trim()}`))
    child.stdout?.on('data', (chunk) => {
      out += String(chunk)
      if (/^HELD\s*$/m.test(out)) {
        finish('HELD')
      } else if (/^FAILED/m.test(out)) {
        finish(out.trim())
      }
    })
  })
}

/** Kills the helper and awaits its exit, capped at 5 s. */
async function releaseHold(child: ChildProcess): Promise<void> {
  if (child.exitCode !== null || child.signalCode !== null) {
    return
  }
  const exited = new Promise<void>((done) => child.once('exit', () => done()))
  child.kill()
  await Promise.race([exited, new Promise<void>((done) => setTimeout(done, 5_000))])
}

type HeaderRead = {
  header: { top: number; bottom: number; left: number; right: number; height: number }
  viewportTop: number
  banner: { top: number; bottom: number; left: number; right: number; scroll: number; client: number } | null
}

async function readHeader(page: Page): Promise<HeaderRead> {
  await expect(page.getByTestId('capture-header'), 'capture-header').toBeVisible({ timeout: 5_000 })
  await windowSettled(page)
  await twoFrames(page)
  return page.evaluate(() => {
    const header = (document.querySelector('[data-testid="capture-header"]') as HTMLElement).getBoundingClientRect()
    const viewport = document.querySelector('[data-testid="capture-viewport"]') as HTMLElement
    const banner = document.querySelector('[data-testid="capture-hotkey-banner"]')
    const bannerBox = banner instanceof HTMLElement ? banner.getBoundingClientRect() : null
    return {
      header: { top: header.top, bottom: header.bottom, left: header.left, right: header.right, height: header.height },
      viewportTop: viewport.getBoundingClientRect().top,
      banner:
        banner instanceof HTMLElement && bannerBox !== null
          ? {
              top: bannerBox.top,
              bottom: bannerBox.bottom,
              left: bannerBox.left,
              right: bannerBox.right,
              scroll: banner.scrollWidth,
              client: banner.clientWidth,
            }
          : null,
    }
  })
}

test('AC-81.11: HOTKEY_IN_USE_FIXTURE: the banner sits inside the header and nothing below it moves', async () => {
  const seed = [sampleShot('e2e-hk81-1', 'a.png', '2026-10-14T12:00:00Z')]
  let inUse: HeaderRead | null = null
  let helper: ChildProcess | null = null
  let held: Awaited<ReturnType<typeof launchApp>> | null = null
  try {
    helper = spawn('pwsh', ['-NoProfile', '-NonInteractive', '-Command', HOLD_F2], {
      stdio: ['ignore', 'pipe', 'pipe'],
      windowsHide: true,
    })
    expect(await waitForHold(helper), 'F2 held by another process').toBe('HELD')
    held = await launchApp()
    const page = await held.firstWindow()
    await installSeam(page, seed)
    await page.getByTestId('nav-capture').click()
    await expect
      .poll(() => page.evaluate(async () => (await window.api.getHotkeyStatus()).inUse), { timeout: 5_000 })
      .toBe(true)
    await expect(page.getByTestId('capture-hotkey-banner')).toBeVisible()
    await expect(page.getByTestId('capture-hotkey-banner')).toContainText('F2 is in use')
    inUse = await readHeader(page)
    await held.close()
    held = null
  } finally {
    if (held !== null) {
      await held.close().catch(() => undefined)
    }
    if (helper !== null) {
      await releaseHold(helper)
    }
  }
  const banner = inUse?.banner
  expect(banner, 'in-use banner box').toBeTruthy()
  const header = (inUse as HeaderRead).header
  expect(banner?.top ?? -1, 'banner top inside the header').toBeGreaterThanOrEqual(header.top - 0.5)
  expect(banner?.bottom ?? Number.POSITIVE_INFINITY, 'banner bottom inside the header').toBeLessThanOrEqual(header.bottom + 0.5)
  expect(banner?.left ?? -1, 'banner left inside the header').toBeGreaterThanOrEqual(header.left - 0.5)
  expect(banner?.right ?? Number.POSITIVE_INFINITY, 'banner right inside the header').toBeLessThanOrEqual(header.right + 0.5)
  expect(banner?.scroll ?? Number.POSITIVE_INFINITY, 'banner is not truncated').toBeLessThanOrEqual(banner?.client ?? 0)
  // Free run: a second launch after the helper has exited.
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page, seed)
  await page.getByTestId('nav-capture').click()
  const status = await page.evaluate(async () => window.api.getHotkeyStatus())
  expect(status.inUse, 'F2 held by another process').toBe(false)
  await expect(page.getByTestId('capture-hotkey-banner')).toHaveCount(0)
  const free = await readHeader(page)
  expect(Math.abs(header.height - free.header.height), 'header height in-use vs free').toBeLessThanOrEqual(0.5)
  expect(Math.abs((inUse as HeaderRead).viewportTop - free.viewportTop), 'viewport top in-use vs free').toBeLessThanOrEqual(0.5)
  await app.close()
})

test('AC-81.14: at 100% after a pan the arrow handles track the arrow, a grab moves the head, and Tab then arrow keys nudge it', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await openZoomShot(page)
  const level = page.getByTestId('capture-zoom-level')
  for (let i = 0; i < LADDER.length && (await level.textContent()) !== '100%'; i += 1) {
    await page.getByTestId('capture-zoom-in').click()
  }
  await expect(level).toHaveText('100%')
  const centred = await readZoom(page)
  await page.mouse.move(centred.left + centred.width / 2, centred.top + centred.height / 2)
  await page.mouse.down({ button: 'middle' })
  await page.mouse.move(centred.left + centred.width / 2 - 40, centred.top + centred.height / 2 - 30)
  await page.mouse.up({ button: 'middle' })
  const view = await readZoom(page)
  expect(view.ox).toBeCloseTo(centred.ox - 40, 3)
  const toClient = (x: number, y: number) => ({ x: view.left + view.ox + x * view.s, y: view.top + view.oy + y * view.s })
  const start = toClient(1200, 800)
  const end = toClient(1260, 830)
  await page.getByTestId('capture-tool-arrow').click()
  await page.mouse.move(start.x, start.y)
  await page.mouse.down()
  await page.mouse.move(end.x, end.y)
  await page.mouse.up()
  await expect(page.locator('[data-annotation-type="arrow"]')).toHaveCount(1)
  await expect(page.getByTestId('capture-tool-select')).toHaveAttribute('aria-pressed', 'true')
  const fromHandle = page.getByTestId('capture-handle-from')
  const toHandle = page.getByTestId('capture-handle-to')
  await expect(fromHandle).toHaveCount(1)
  await expect(toHandle).toHaveCount(1)
  const circle = async (handle: typeof toHandle) => ({
    cx: Number(await handle.getAttribute('cx')),
    cy: Number(await handle.getAttribute('cy')),
  })
  // The surface can move when the selection mounts chrome above it, so each check re-reads the view.
  // The width is checked at rest only: the focus ring's wider stroke widens a focused handle's box.
  const expectOnArrowEnd = async (handle: typeof toHandle, label: string, atRest = true): Promise<void> => {
    const now = await readZoom(page)
    const { cx, cy } = await circle(handle)
    const box = await handle.boundingBox()
    expect(box, `${label} box`).toBeTruthy()
    const centre = { x: (box?.x ?? 0) + (box?.width ?? 0) / 2, y: (box?.y ?? 0) + (box?.height ?? 0) / 2 }
    const expected = { x: now.left + now.ox + cx * now.s, y: now.top + now.oy + cy * now.s }
    expect(Math.abs(centre.x - expected.x), `${label} centre x`).toBeLessThanOrEqual(1)
    expect(Math.abs(centre.y - expected.y), `${label} centre y`).toBeLessThanOrEqual(1)
    if (atRest) {
      expect(Math.abs((box?.width ?? 0) - 2 * HANDLE_RADIUS_CSS), `${label} width`).toBeLessThanOrEqual(1)
    }
  }
  await expectOnArrowEnd(fromHandle, 'capture-handle-from')
  await expectOnArrowEnd(toHandle, 'capture-handle-to')
  // Grab: a real drag on the head moves only `to`.
  const line = page.locator('[data-annotation-type="arrow"] line').first()
  const ends = async () => ({
    x1: Number(await line.getAttribute('x1')),
    y1: Number(await line.getAttribute('y1')),
    x2: Number(await line.getAttribute('x2')),
    y2: Number(await line.getAttribute('y2')),
  })
  const before = await ends()
  const grabView = await readZoom(page)
  const headBox = await toHandle.boundingBox()
  const head = { x: (headBox?.x ?? 0) + (headBox?.width ?? 0) / 2, y: (headBox?.y ?? 0) + (headBox?.height ?? 0) / 2 }
  await page.mouse.move(head.x, head.y)
  await page.mouse.down()
  await page.mouse.move(head.x + 20, head.y)
  await page.mouse.up()
  const grabbed = await ends()
  expect(Math.abs(grabbed.x2 - before.x2 - 20 / grabView.s), 'x2 grows by 20 / s').toBeLessThanOrEqual(1)
  expect(grabbed.x1).toBe(before.x1)
  expect(grabbed.y1).toBe(before.y1)
  // Keys: Tab from the surface to the head handle, then ArrowUp ×3 moves only `to`.
  const surface = page.getByTestId('capture-draw-surface')
  await surface.focus()
  let onHead = false
  for (let presses = 0; presses < 4 && !onHead; presses += 1) {
    await page.keyboard.press('Tab')
    onHead = await page.evaluate(
      () => document.activeElement?.getAttribute('data-testid') === 'capture-handle-to',
    )
  }
  expect(onHead, 'Tab reaches capture-handle-to within 4 presses').toBe(true)
  const fromBefore = await circle(fromHandle)
  const toBefore = await circle(toHandle)
  for (let i = 0; i < 3; i += 1) {
    await page.keyboard.press('ArrowUp')
  }
  const toAfter = await circle(toHandle)
  expect(toAfter.cy, 'to cy decreases by 3').toBeCloseTo(toBefore.cy - 3, 3)
  expect(toAfter.cx).toBe(toBefore.cx)
  expect(await circle(fromHandle)).toEqual(fromBefore)
  await expectOnArrowEnd(toHandle, 'capture-handle-to after keys', false)
  const scroll = await surface.evaluate((node) => ({ left: node.scrollLeft, top: node.scrollTop }))
  expect(scroll, 'focus did not scroll the surface').toEqual({ left: 0, top: 0 })
  // capture-color owns its arrow keys.
  const hex = page.getByTestId('capture-color')
  await expect(hex).toBeVisible()
  await hex.focus()
  const value = await hex.inputValue()
  const fromHold = await circle(fromHandle)
  const toHold = await circle(toHandle)
  await page.keyboard.press('ArrowUp')
  expect(await circle(fromHandle)).toEqual(fromHold)
  expect(await circle(toHandle)).toEqual(toHold)
  expect(await hex.inputValue()).toBe(value)
  await app.close()
})

// ── MEU-82 text baseline (Session 36 plan AC-82.6, TEXT_PIXEL_ORACLE) ──────────────────────
// The seam serves the committed TEXT_FIXTURE PNGs by variant and returns TEXT_FIXTURE_MARK on
// the detail, so the Original view (PNG + SVG preview) and the Annotated view (the real bake)
// can be compared pixel for pixel at ZOOM_1TO1.

const FIDELITY_MARK = { type: 'text', x: 20, y: 30, text: 'Hi', color: '#000000', font_size: 32, bg_color: '#FFD400' }

type PixelBox = { left: number; top: number; right: number; bottom: number }
type FidelityBoxes = { ink: PixelBox | null; plate: PixelBox | null; width: number; height: number; rect: { left: number; top: number } }

async function installFidelitySeam(page: Page, shot: CaptureItem): Promise<void> {
  const fixtures = resolve(here, 'fixtures')
  const original = readFileSync(join(fixtures, 'capture-fidelity-original.png')).toString('base64')
  const annotated = readFileSync(join(fixtures, 'capture-fidelity-annotated.png')).toString('base64')
  await page.addInitScript(
    ([item, mark, png]: [CaptureItem, typeof FIDELITY_MARK, { original: string; annotated: string }]) => {
      const state = window as unknown as { __e2eSeamInstalled?: boolean }
      state.__e2eSeamInstalled = true
      const bytes = (b64: string) => Uint8Array.from(atob(b64), (c) => c.charCodeAt(0))
      const json = (body: unknown, status = 200) =>
        new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
      const original = window.fetch.bind(window)
      window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
        const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
        const method = (init?.method ?? 'GET').toUpperCase()
        const parsed = new URL(url)
        const path = parsed.pathname
        if (path.includes('/health/dependencies')) {
          return json({ ffmpeg: { available: true, version: '7.1.2' }, yt_dlp: { available: true } })
        }
        if (path.endsWith('/settings/capture')) {
          return json({ inbox_dir: 'C:/e2e', hotkey: 'F2', copy_to_clipboard: false, close_to_tray: true })
        }
        if (path.includes('/captures/requests')) {
          return json({ items: [] })
        }
        if (path.endsWith('/image')) {
          const variant = parsed.searchParams.get('variant') === 'annotated' ? png.annotated : png.original
          return new Response(bytes(variant), { status: 200, headers: { 'Content-Type': 'image/png' } })
        }
        const detail = path.match(/\/captures\/([^/]+)$/)
        if (detail && method === 'GET') {
          return json({ ...item, annotations: [mark] })
        }
        if (/\/captures\/?$/.test(path) && method === 'GET') {
          return json({ items: [item] })
        }
        return original(input, init)
      }
    },
    [shot, FIDELITY_MARK, { original, annotated }] as [CaptureItem, typeof FIDELITY_MARK, { original: string; annotated: string }],
  )
  await page.reload()
  await page.getByTestId('downloader-page').waitFor()
}

/**
 * Screenshots the viewport image box and decodes it in the page; boxes are image px (device px / DPR).
 * The box can sit at a fractional CSS origin, so the screenshot rounds outward and its edge pixels
 * carry the surface background: the scan skips a 2 px inset ring (the mark is far from the edges).
 */
async function fidelityBoxes(page: Page): Promise<FidelityBoxes> {
  await twoFrames(page)
  const shot = await page.getByTestId('capture-viewport-image').screenshot({ scale: 'device' })
  return page.evaluate(async (b64: string): Promise<FidelityBoxes> => {
    const data = Uint8Array.from(atob(b64), (c) => c.charCodeAt(0))
    const bitmap = await createImageBitmap(new Blob([data], { type: 'image/png' }))
    const canvas = document.createElement('canvas')
    canvas.width = bitmap.width
    canvas.height = bitmap.height
    const context = canvas.getContext('2d') as CanvasRenderingContext2D
    context.drawImage(bitmap, 0, 0)
    const pixels = context.getImageData(0, 0, bitmap.width, bitmap.height).data
    const dpr = window.devicePixelRatio || 1
    const inset = Math.ceil(2 * dpr)
    const image = document.querySelector('[data-testid="capture-viewport-image"]') as HTMLElement
    const rect = image.getBoundingClientRect()
    const grow = (box: PixelBox | null, x: number, y: number): PixelBox => ({
      left: Math.min(box?.left ?? x, x),
      top: Math.min(box?.top ?? y, y),
      right: Math.max(box?.right ?? x, x),
      bottom: Math.max(box?.bottom ?? y, y),
    })
    let ink: PixelBox | null = null
    let plate: PixelBox | null = null
    for (let y = inset; y < bitmap.height - inset; y += 1) {
      for (let x = inset; x < bitmap.width - inset; x += 1) {
        const i = (y * bitmap.width + x) * 4
        const r = pixels[i] as number
        const g = pixels[i + 1] as number
        const b = pixels[i + 2] as number
        if (0.299 * r + 0.587 * g + 0.114 * b < 96) {
          ink = grow(ink, x, y)
        }
        if (Math.abs(r - 0xff) <= 40 && Math.abs(g - 0xd4) <= 40 && Math.abs(b - 0x00) <= 40) {
          plate = grow(plate, x, y)
        }
      }
    }
    const toImage = (box: PixelBox | null): PixelBox | null =>
      box === null
        ? null
        : {
            left: Math.floor(box.left / dpr),
            top: Math.floor(box.top / dpr),
            right: Math.floor(box.right / dpr),
            bottom: Math.floor(box.bottom / dpr),
          }
    return {
      ink: toImage(ink),
      plate: toImage(plate),
      width: bitmap.width / dpr,
      height: bitmap.height / dpr,
      rect: { left: rect.left, top: rect.top },
    }
  }, shot.toString('base64'))
}

// No custom expect messages here: the Red receipt must carry Playwright's `Error: expect(` line
// (red-check.py); the logged boxes name the failing side.
function expectBoxesAgree(preview: PixelBox | null, bake: PixelBox | null): void {
  expect(preview).not.toBeNull()
  expect(bake).not.toBeNull()
  for (const side of ['left', 'top', 'right', 'bottom'] as const) {
    expect(Math.abs((preview?.[side] ?? 0) - (bake?.[side] ?? 0))).toBeLessThanOrEqual(1)
  }
}

function expectInkInsidePlate(view: FidelityBoxes): void {
  const { ink, plate } = view
  expect(ink !== null && plate !== null).toBe(true)
  expect(ink?.left ?? 0).toBeGreaterThanOrEqual((plate?.left ?? 0) - 1)
  expect(ink?.top ?? 0).toBeGreaterThanOrEqual((plate?.top ?? 0) - 1)
  expect(ink?.right ?? 0).toBeLessThanOrEqual((plate?.right ?? 0) + 1)
  expect(ink?.bottom ?? 0).toBeLessThanOrEqual((plate?.bottom ?? 0) + 1)
}

test('AC-82.6 TEXT_PIXEL_ORACLE: the preview text and plate match the baked PNG within 1 px at 100%', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const shot = {
    ...sampleShot('e2e-fid-1', 'fidelity.png', '2026-10-14T12:00:00Z', { width: 240, height: 120 }),
    annotated_path: 'C:/e2e/fidelity.annotated.png',
  }
  await installFidelitySeam(page, shot)
  await page.getByTestId('nav-capture').click()
  await page.getByTestId('capture-filmstrip-item').first().click()
  await page.waitForSelector('[data-testid="capture-draw-surface"][data-overlay-ready="true"]')
  await expect(page.locator('[data-annotation-type="text"]')).toHaveCount(1)
  await windowSettled(page)
  const level = page.getByTestId('capture-zoom-level')
  for (let i = 0; i < 2 * LADDER.length && (await level.textContent()) !== '100%'; i += 1) {
    const view = await readZoom(page)
    await page.getByTestId(view.s < 1 ? 'capture-zoom-in' : 'capture-zoom-out').click()
  }
  await expect(level).toHaveText('100%')
  expect((await readZoom(page)).s).toBe(1)
  await page.mouse.move(1, 1)
  const loaded = (previous: string) =>
    page.waitForFunction((prior: string) => {
      const image = document.querySelector('[data-testid="capture-viewport-image"]') as HTMLImageElement | null
      return image !== null && image.src !== prior && image.complete && image.naturalWidth === 240
    }, previous)
  await page.getByTestId('capture-view-original').click()
  await expect(page.locator('[data-annotation-type="text"]')).toHaveCount(1)
  await loaded('')
  const originalSrc = await page.getByTestId('capture-viewport-image').evaluate((node) => (node as HTMLImageElement).src)
  const preview = await fidelityBoxes(page)
  await page.getByTestId('capture-view-annotated').click()
  await expect(page.locator('[data-annotation-type="text"]')).toHaveCount(0)
  await loaded(originalSrc)
  const bake = await fidelityBoxes(page)
  console.log(`AC-82.6 boxes ${JSON.stringify({ preview, bake })}`)
  for (const view of [preview, bake]) {
    expect(Math.abs(view.width - 240)).toBeLessThanOrEqual(1)
    expect(Math.abs(view.height - 120)).toBeLessThanOrEqual(1)
  }
  expectBoxesAgree(preview.ink, bake.ink)
  expectBoxesAgree(preview.plate, bake.plate)
  expectInkInsidePlate(preview)
  expectInkInsidePlate(bake)
  await app.close()
})

type ShellEntry = { op: 'openPath' | 'showItemInFolder'; target: string }

async function shellLog(app: Awaited<ReturnType<typeof launchApp>>): Promise<ShellEntry[] | null> {
  return app.evaluate(
    () => (globalThis as { __AVKIT_E2E_SHELL_LOG__?: ShellEntry[] }).__AVKIT_E2E_SHELL_LOG__ ?? null,
  )
}

test('AC-84.5 Open file and Open folder ask the shell for the file the viewport shows (VIEWED_FILE)', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const shot = {
    ...sampleShot('e2e-viewed-1', 'viewed.png', '2026-10-16T12:00:00Z'),
    annotated_path: 'C:/e2e/viewed.annotated.png',
    sidecar_path: 'C:/e2e/viewed.ann.json',
  }
  await installSeam(page, [shot])
  await page.getByTestId('nav-capture').click()
  await expect(page.getByTestId('capture-page')).toBeVisible()
  await page.getByTestId('capture-filmstrip-item').first().click()
  await expect(page.getByTestId('capture-draw-surface')).toHaveAttribute('data-overlay-ready', 'true')
  expect(await shellLog(app)).toEqual([])
  const openBoth = async (count: number): Promise<void> => {
    await page.getByTestId('capture-open-file').click()
    await expect.poll(async () => (await shellLog(app))?.length).toBe(count + 1)
    await page.getByTestId('capture-open-folder').click()
    await expect.poll(async () => (await shellLog(app))?.length).toBe(count + 2)
  }
  await page.getByTestId('capture-view-annotated').click()
  await expect(page.getByTestId('capture-view-annotated')).toHaveAttribute('aria-pressed', 'true')
  await openBoth(0)
  expect((await shellLog(app))?.slice(-2)).toEqual([
    { op: 'openPath', target: shot.annotated_path },
    { op: 'showItemInFolder', target: shot.annotated_path },
  ])
  await page.getByTestId('capture-view-original').click()
  await expect(page.getByTestId('capture-view-original')).toHaveAttribute('aria-pressed', 'true')
  await openBoth(2)
  expect((await shellLog(app))?.slice(2)).toEqual([
    { op: 'openPath', target: shot.original_path },
    { op: 'showItemInFolder', target: shot.original_path },
  ])
  await app.close()
})

/** RENDERER_PIN (Session 37): the window loaded the renderer this worktree built, not an `ELECTRON_RENDERER_URL` server. */
function expectBuiltRenderer(page: Page): void {
  expect(fileURLToPath(page.url().split('#')[0] ?? '')).toBe(resolve(here, '../../out/renderer/index.html'))
}

async function drawBox(page: Page): Promise<void> {
  await page.getByTestId('capture-tool-box').click()
  await drawArrow(page)
}

async function scrubDrag(page: Page, handleId: string, dx: number, shift = false): Promise<{ x: number; y: number }> {
  const box = await page.getByTestId(handleId).boundingBox()
  expect(box).toBeTruthy()
  // Whole pixels: the step count depends only on the total travel, which then stays exact.
  const x = Math.round((box?.x ?? 0) + (box?.width ?? 0) / 2)
  const y = Math.round((box?.y ?? 0) + (box?.height ?? 0) / 2)
  await page.mouse.move(x, y)
  if (shift) await page.keyboard.down('Shift')
  await page.mouse.down()
  await page.mouse.move(x + dx, y, { steps: 4 })
  return { x: x + dx, y }
}

test('AC-85.10 Stroke label drag previews live, Shift is coarse, capture holds past the edge, and each drag is one Undo', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page, [sampleShot('e2e-scrub-1', 'scrub.png', '2026-10-16T12:00:00Z')])
  await page.getByTestId('nav-capture').click()
  await page.getByTestId('capture-filmstrip-item').first().click()
  await expect(page.getByTestId('capture-draw-surface')).toHaveAttribute('data-overlay-ready', 'true')
  expectBuiltRenderer(page)
  await drawBox(page)
  const rect = page.locator('[data-annotation-type="rect"]')
  await expect(rect).toHaveCount(1)
  await expect(rect).toHaveAttribute('stroke-width', '3')
  expect(await page.getByTestId('capture-stroke-scrub').count()).toBe(1)
  await scrubDrag(page, 'capture-stroke-scrub', 40)
  await expect(rect).toHaveAttribute('stroke-width', '23')
  await page.mouse.up()
  await expect(page.getByTestId('capture-stroke')).toHaveValue('23')
  await scrubDrag(page, 'capture-stroke-scrub', 6, true)
  await expect(rect).toHaveAttribute('stroke-width', '53')
  await page.mouse.up()
  await page.keyboard.up('Shift')
  await scrubDrag(page, 'capture-stroke-scrub', 200)
  await expect(rect).toHaveAttribute('stroke-width', '100')
  await page.mouse.up()
  await expect(page.getByTestId('capture-stroke')).toHaveValue('100')
  for (const expected of ['53', '23', '3']) {
    await page.getByTestId('capture-undo').click()
    await expect(rect).toHaveAttribute('stroke-width', expected)
  }
  await app.close()
})

test('AC-86.3 each Named option renders its own colour with the contrast-picked text colour', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page, [sampleShot('e2e-swatch-1', 'swatch.png', '2026-10-16T12:00:00Z')])
  await page.getByTestId('nav-capture').click()
  await page.getByTestId('capture-filmstrip-item').first().click()
  await expect(page.getByTestId('capture-draw-surface')).toHaveAttribute('data-overlay-ready', 'true')
  expectBuiltRenderer(page)
  const rendered = await page.getByTestId('capture-named-color').evaluate((select) =>
    Array.from((select as HTMLSelectElement).options)
      .filter((option) => option.value !== '')
      .map((option) => {
        const style = getComputedStyle(option)
        return { value: option.value, backgroundColor: style.backgroundColor, color: style.color }
      }),
  )
  // SWATCH_OPTIONS: NAMED_COLOR_HEX as rgb(), with the CONTRAST_TEXT pick (R-2 table).
  const black = 'rgb(0, 0, 0)'
  const white = 'rgb(255, 255, 255)'
  expect(rendered).toEqual([
    { value: 'red', backgroundColor: 'rgb(255, 0, 0)', color: black },
    { value: 'orange', backgroundColor: 'rgb(255, 165, 0)', color: black },
    { value: 'yellow', backgroundColor: 'rgb(255, 255, 0)', color: black },
    { value: 'green', backgroundColor: 'rgb(0, 128, 0)', color: white },
    { value: 'blue', backgroundColor: 'rgb(0, 0, 255)', color: white },
    { value: 'white', backgroundColor: white, color: black },
    { value: 'black', backgroundColor: black, color: white },
  ])
  await app.close()
})

/** A real-mouse drag between two image pixels of the 8 x 8 sample shot (the `drawArrow` mapping). */
async function dragImage(page: Page, from: [number, number], to: [number, number]): Promise<void> {
  const surface = page.getByTestId('capture-draw-surface')
  const box = await surface.boundingBox()
  expect(box).toBeTruthy()
  const scale = Math.min((box?.width ?? 1) / 8, (box?.height ?? 1) / 8)
  const originX = (box?.x ?? 0) + ((box?.width ?? 0) - 8 * scale) / 2
  const originY = (box?.y ?? 0) + ((box?.height ?? 0) - 8 * scale) / 2
  await page.mouse.move(originX + from[0] * scale, originY + from[1] * scale)
  await page.mouse.down()
  await page.mouse.move(originX + to[0] * scale, originY + to[1] * scale, { steps: 4 })
  await page.mouse.up()
}

test('AC-87.6 with the tool lock on, two real Box drags give two boxes and Box stays pressed', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page, [sampleShot('e2e-lock-1', 'lock.png', '2026-10-16T12:00:00Z')])
  await page.getByTestId('nav-capture').click()
  await page.getByTestId('capture-filmstrip-item').first().click()
  await expect(page.getByTestId('capture-draw-surface')).toHaveAttribute('data-overlay-ready', 'true')
  expectBuiltRenderer(page)
  expect(await page.getByTestId('capture-tool-lock').count()).toBe(1)
  const lock = page.getByTestId('capture-tool-lock')
  await lock.click()
  await expect(lock).toHaveAttribute('aria-pressed', 'true')
  await page.getByTestId('capture-tool-box').click()
  await dragImage(page, [1, 1], [3, 3])
  await dragImage(page, [5, 5], [7, 7])
  await expect(page.locator('rect[data-annotation-type="rect"]')).toHaveCount(2)
  await expect(page.getByTestId('capture-tool-box')).toHaveAttribute('aria-pressed', 'true')
  await expect(lock).toHaveAttribute('aria-pressed', 'true')
  await app.close()
})

// ── MEU-90 REGION_PIXEL_ORACLE (Session 39 plan AC-90.12, REGION_E2E_RED) ───────────────────────────
// The seam serves REGION_IMAGE_FIXTURE by variant and REGION_IMAGE_MARKS on the detail, flags the
// served detail and records every av-kit:capture:error, so a renderer that refuses the marks fails
// at the first assertion instead of timing out.

const REGION_IMAGE_MARKS = [
  { type: 'pixelate', x: 10, y: 10, width: 100, height: 70, block_size: 10 },
  { type: 'eraser', x: 140, y: 40, width: 40, height: 30 },
]
const REGION_W = 240
const REGION_H = 160

type RegionSeamState = { __e2eDetailServed?: boolean; __e2eCaptureErrors?: string[] }
type RegionPixels = { width: number; height: number; data: number[] }
type RegionRect = { x: number; y: number; width: number; height: number }

function regionPng(name: string): string {
  return readFileSync(join(resolve(here, 'fixtures'), name)).toString('base64')
}

async function installRegionSeam(page: Page, shot: CaptureItem, marks: Array<Record<string, unknown>>): Promise<void> {
  const original = regionPng('capture-region-original.png')
  const annotated = regionPng('capture-region-annotated.png')
  await page.addInitScript(
    ([item, detailMarks, png]: [CaptureItem, Array<Record<string, unknown>>, { original: string; annotated: string }]) => {
      const state = window as unknown as { __e2eSeamInstalled?: boolean } & RegionSeamState
      state.__e2eSeamInstalled = true
      state.__e2eDetailServed = false
      state.__e2eCaptureErrors = []
      window.addEventListener('av-kit:capture:error', (event) => {
        state.__e2eCaptureErrors?.push(String((event as CustomEvent<unknown>).detail))
      })
      const bytes = (b64: string) => Uint8Array.from(atob(b64), (c) => c.charCodeAt(0))
      const json = (body: unknown, status = 200) =>
        new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
      const passThrough = window.fetch.bind(window)
      window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
        const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
        const method = (init?.method ?? 'GET').toUpperCase()
        const parsed = new URL(url)
        const path = parsed.pathname
        if (path.includes('/health/dependencies')) {
          return json({ ffmpeg: { available: true, version: '7.1.2' }, yt_dlp: { available: true } })
        }
        if (path.endsWith('/settings/capture')) {
          return json({ inbox_dir: 'C:/e2e', hotkey: 'F2', copy_to_clipboard: false, close_to_tray: true })
        }
        if (path.includes('/captures/requests')) {
          return json({ items: [] })
        }
        if (path.endsWith('/image')) {
          const variant = parsed.searchParams.get('variant') === 'annotated' ? png.annotated : png.original
          return new Response(bytes(variant), { status: 200, headers: { 'Content-Type': 'image/png' } })
        }
        const detail = path.match(/\/captures\/([^/]+)$/)
        if (detail && method === 'GET') {
          state.__e2eDetailServed = true
          return json({ ...item, annotations: detailMarks })
        }
        if (/\/captures\/?$/.test(path) && method === 'GET') {
          return json({ items: [item] })
        }
        return passThrough(input, init)
      }
    },
    [shot, marks, { original, annotated }] as [
      CaptureItem,
      Array<Record<string, unknown>>,
      { original: string; annotated: string },
    ],
  )
  await page.reload()
  await page.getByTestId('downloader-page').waitFor()
}

/** REGION_E2E_RED: wait for the served detail and then either a capture error or the ready overlay. */
async function openRegionShot(page: Page): Promise<void> {
  await page.getByTestId('nav-capture').click()
  await page.getByTestId('capture-filmstrip-item').first().click()
  await page.waitForFunction(() => {
    const state = window as unknown as RegionSeamState
    const surface = document.querySelector('[data-testid="capture-draw-surface"]')
    return (
      state.__e2eDetailServed === true &&
      ((state.__e2eCaptureErrors?.length ?? 0) > 0 || surface?.getAttribute('data-overlay-ready') === 'true')
    )
  })
  const errors = await page.evaluate(() => (window as unknown as RegionSeamState).__e2eCaptureErrors ?? [])
  expect(errors).toEqual([])
  expect(await page.getByTestId('capture-draw-surface').getAttribute('data-overlay-ready')).toBe('true')
}

async function zoomToOneToOne(page: Page): Promise<void> {
  const level = page.getByTestId('capture-zoom-level')
  for (let i = 0; i < 2 * LADDER.length && (await level.textContent()) !== '100%'; i += 1) {
    const view = await readZoom(page)
    await page.getByTestId(view.s < 1 ? 'capture-zoom-in' : 'capture-zoom-out').click()
  }
  await expect(level).toHaveText('100%')
  expect((await readZoom(page)).s).toBe(1)
}

/** Decodes a PNG in the page (createImageBitmap + canvas) to RGBA. */
async function decodeInPage(page: Page, b64: string): Promise<RegionPixels> {
  return page.evaluate(async (data: string): Promise<RegionPixels> => {
    const bytes = Uint8Array.from(atob(data), (c) => c.charCodeAt(0))
    const bitmap = await createImageBitmap(new Blob([bytes], { type: 'image/png' }))
    const canvas = document.createElement('canvas')
    canvas.width = bitmap.width
    canvas.height = bitmap.height
    const context = canvas.getContext('2d') as CanvasRenderingContext2D
    context.drawImage(bitmap, 0, 0)
    return {
      width: bitmap.width,
      height: bitmap.height,
      data: Array.from(context.getImageData(0, 0, bitmap.width, bitmap.height).data),
    }
  }, b64)
}

async function regionLayerPixels(page: Page): Promise<RegionPixels> {
  return page.getByTestId('capture-region-layer').evaluate((node): RegionPixels => {
    const canvas = node as HTMLCanvasElement
    const context = canvas.getContext('2d') as CanvasRenderingContext2D
    return {
      width: canvas.width,
      height: canvas.height,
      data: Array.from(context.getImageData(0, 0, canvas.width, canvas.height).data),
    }
  })
}

/** Viewport-image screenshot samples at image points, mapped through the device pixel ratio. */
async function viewportSamples(page: Page, points: Array<[number, number]>): Promise<number[][]> {
  await twoFrames(page)
  const shot = await page.getByTestId('capture-viewport-image').screenshot({ scale: 'device' })
  return page.evaluate(
    async ([b64, at]: [string, Array<[number, number]>]): Promise<number[][]> => {
      const data = Uint8Array.from(atob(b64), (c) => c.charCodeAt(0))
      const bitmap = await createImageBitmap(new Blob([data], { type: 'image/png' }))
      const canvas = document.createElement('canvas')
      canvas.width = bitmap.width
      canvas.height = bitmap.height
      const context = canvas.getContext('2d') as CanvasRenderingContext2D
      context.drawImage(bitmap, 0, 0)
      const pixels = context.getImageData(0, 0, bitmap.width, bitmap.height).data
      const dpr = window.devicePixelRatio || 1
      return at.map(([x, y]) => {
        const px = Math.min(bitmap.width - 1, Math.floor((x + 0.5) * dpr))
        const py = Math.min(bitmap.height - 1, Math.floor((y + 0.5) * dpr))
        const i = (py * bitmap.width + px) * 4
        return [pixels[i] as number, pixels[i + 1] as number, pixels[i + 2] as number]
      })
    },
    [shot.toString('base64'), points] as [string, Array<[number, number]>],
  )
}

function insideAny(rects: RegionRect[], x: number, y: number): boolean {
  return rects.some((r) => x >= r.x && x < r.x + r.width && y >= r.y && y < r.y + r.height)
}

/** The centre pixel of every whole block of a pixelate (blocks anchored at its top-left). */
function blockCentres(mark: RegionRect & { block_size: number }): Array<[number, number]> {
  const centres: Array<[number, number]> = []
  const half = Math.floor(mark.block_size / 2)
  for (let by = mark.y; by + mark.block_size <= mark.y + mark.height; by += mark.block_size) {
    for (let bx = mark.x; bx + mark.block_size <= mark.x + mark.width; bx += mark.block_size) {
      centres.push([bx + half, by + half])
    }
  }
  return centres
}

test('AC-90.12 REGION_PIXEL_ORACLE: the pixelate layer matches the bake, the 1:1 views agree, and the drag previews live', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const shot = {
    ...sampleShot('e2e-region-1', 'region.png', '2026-10-16T12:00:00Z', { width: REGION_W, height: REGION_H }),
    annotated_path: 'C:/e2e/region.annotated.png',
  }
  await installRegionSeam(page, shot, REGION_IMAGE_MARKS)
  await openRegionShot(page)
  await expect(page.locator('[data-annotation-type="pixelate"]')).toHaveCount(1)
  await windowSettled(page)
  await zoomToOneToOne(page)
  await page.mouse.move(1, 1)
  const loaded = (previous: string) =>
    page.waitForFunction((prior: string) => {
      const image = document.querySelector('[data-testid="capture-viewport-image"]') as HTMLImageElement | null
      return image !== null && image.src !== prior && image.complete && image.naturalWidth === 240
    }, previous)
  await loaded('')
  const pixelate = REGION_IMAGE_MARKS[0] as RegionRect & { block_size: number }

  // (a) the layer equals the decoded bake within 1 inside the pixelate and is transparent outside
  // every region mark.
  const bake = await decodeInPage(page, regionPng('capture-region-annotated.png'))
  await twoFrames(page)
  const layer = await regionLayerPixels(page)
  expect([layer.width, layer.height]).toEqual([REGION_W, REGION_H])
  let worst = 0
  let opaqueInside = true
  let leaks = 0
  for (let y = 0; y < REGION_H; y += 1) {
    for (let x = 0; x < REGION_W; x += 1) {
      const i = (y * REGION_W + x) * 4
      if (insideAny([pixelate], x, y)) {
        for (let band = 0; band < 3; band += 1) {
          worst = Math.max(worst, Math.abs((layer.data[i + band] as number) - (bake.data[i + band] as number)))
        }
        opaqueInside = opaqueInside && layer.data[i + 3] === 255
      } else if (!insideAny(REGION_IMAGE_MARKS as RegionRect[], x, y) && layer.data[i + 3] !== 0) {
        leaks += 1
      }
    }
  }
  console.log(`AC-90.12 (a) ${JSON.stringify({ worst, opaqueInside, leaks })}`)
  expect(worst).toBeLessThanOrEqual(1)
  expect(opaqueInside).toBe(true)
  expect(leaks).toBe(0)

  // (b) at ZOOM_1TO1 the Original view (image + layer + SVG) and the bake agree at every block centre.
  const centres = blockCentres(pixelate)
  expect(centres).toHaveLength(70)
  const originalSrc = await page.getByTestId('capture-viewport-image').evaluate((node) => (node as HTMLImageElement).src)
  const previewSamples = await viewportSamples(page, centres)
  await page.getByTestId('capture-view-annotated').click()
  await expect(page.locator('[data-annotation-type="pixelate"]')).toHaveCount(0)
  await loaded(originalSrc)
  const bakeSamples = await viewportSamples(page, centres)
  let viewWorst = 0
  for (let k = 0; k < centres.length; k += 1) {
    for (let band = 0; band < 3; band += 1) {
      viewWorst = Math.max(
        viewWorst,
        Math.abs((previewSamples[k]?.[band] ?? -1000) - (bakeSamples[k]?.[band] ?? 1000)),
      )
    }
  }
  console.log(`AC-90.12 (b) ${JSON.stringify({ viewWorst })}`)
  expect(viewWorst).toBeLessThanOrEqual(2)

  // (c) live: during a Pixelate drag on the gradient half, before pointer-up, the layer has the mosaic.
  await page.getByTestId('capture-view-original').click()
  await expect(page.locator('[data-annotation-type="pixelate"]')).toHaveCount(1)
  await page.getByTestId('capture-tool-pixelate').click()
  const box = await page.getByTestId('capture-viewport-image').boundingBox()
  expect(box).not.toBeNull()
  const at = (x: number, y: number): [number, number] => [(box?.x ?? 0) + x + 0.5, (box?.y ?? 0) + y + 0.5]
  const original = await decodeInPage(page, regionPng('capture-region-original.png'))
  await page.mouse.move(...at(20, 90))
  await page.mouse.down()
  await page.mouse.move(...at(80, 130), { steps: 4 })
  await twoFrames(page)
  const live = await regionLayerPixels(page)
  const centre = (110 * REGION_W + 50) * 4
  const liveRgba = live.data.slice(centre, centre + 4)
  const sourceRgb = original.data.slice(centre, centre + 3)
  console.log(`AC-90.12 (c) ${JSON.stringify({ liveRgba, sourceRgb })}`)
  expect(liveRgba[3]).toBe(255)
  expect(liveRgba.slice(0, 3)).not.toEqual(sourceRgb)
  await page.mouse.up()
  await expect(page.locator('[data-annotation-type="pixelate"]')).toHaveCount(2)
  await app.close()
})

// ── MEU-91 REGION_PIXEL_ORACLE for the eraser (Session 39 plan AC-91.10; REGION_TOLERANCE 0 in (a)) ──

test('AC-91.10 REGION_PIXEL_ORACLE: the eraser layer equals the bake exactly and the 1:1 views agree', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const shot = {
    ...sampleShot('e2e-region-2', 'region.png', '2026-10-16T12:00:00Z', { width: REGION_W, height: REGION_H }),
    annotated_path: 'C:/e2e/region.annotated.png',
  }
  await installRegionSeam(page, shot, REGION_IMAGE_MARKS)
  await openRegionShot(page)
  await expect(page.locator('[data-annotation-type="eraser"]')).toHaveCount(1)
  await windowSettled(page)
  await zoomToOneToOne(page)
  await page.mouse.move(1, 1)
  const loaded = (previous: string) =>
    page.waitForFunction((prior: string) => {
      const image = document.querySelector('[data-testid="capture-viewport-image"]') as HTMLImageElement | null
      return image !== null && image.src !== prior && image.complete && image.naturalWidth === 240
    }, previous)
  await loaded('')
  const eraser = REGION_IMAGE_MARKS[1] as RegionRect

  // (a) inside the eraser the layer equals the decoded bake exactly and is opaque; outside every
  // region mark it is transparent.
  const bake = await decodeInPage(page, regionPng('capture-region-annotated.png'))
  const centre = ((eraser.y + eraser.height / 2) * REGION_W + eraser.x + eraser.width / 2) * 4
  expect(bake.data.slice(centre, centre + 3)).toEqual([240, 240, 240])
  await twoFrames(page)
  const layer = await regionLayerPixels(page)
  expect([layer.width, layer.height]).toEqual([REGION_W, REGION_H])
  let worst = 0
  let opaqueInside = true
  let leaks = 0
  for (let y = 0; y < REGION_H; y += 1) {
    for (let x = 0; x < REGION_W; x += 1) {
      const i = (y * REGION_W + x) * 4
      if (insideAny([eraser], x, y)) {
        for (let band = 0; band < 3; band += 1) {
          worst = Math.max(worst, Math.abs((layer.data[i + band] as number) - (bake.data[i + band] as number)))
        }
        opaqueInside = opaqueInside && layer.data[i + 3] === 255
      } else if (!insideAny(REGION_IMAGE_MARKS as RegionRect[], x, y) && layer.data[i + 3] !== 0) {
        leaks += 1
      }
    }
  }
  console.log(`AC-91.10 (a) ${JSON.stringify({ worst, opaqueInside, leaks })}`)
  expect(worst).toBe(0)
  expect(opaqueInside).toBe(true)
  expect(leaks).toBe(0)

  // (b) at ZOOM_1TO1 the Original view (image + layer + SVG) and the bake agree inside the eraser.
  const points = [45, 55, 65].flatMap((y) => [145, 160, 175].map((x): [number, number] => [x, y]))
  const originalSrc = await page.getByTestId('capture-viewport-image').evaluate((node) => (node as HTMLImageElement).src)
  const previewSamples = await viewportSamples(page, points)
  await page.getByTestId('capture-view-annotated').click()
  await expect(page.locator('[data-annotation-type="eraser"]')).toHaveCount(0)
  await loaded(originalSrc)
  const bakeSamples = await viewportSamples(page, points)
  let viewWorst = 0
  for (let k = 0; k < points.length; k += 1) {
    for (let band = 0; band < 3; band += 1) {
      viewWorst = Math.max(
        viewWorst,
        Math.abs((previewSamples[k]?.[band] ?? -1000) - (bakeSamples[k]?.[band] ?? 1000)),
      )
    }
  }
  console.log(`AC-91.10 (b) ${JSON.stringify({ viewWorst })}`)
  expect(viewWorst).toBeLessThanOrEqual(2)
  await app.close()
})

test('AC-97.8 Ctrl+S saves a dirty shot once and is inert on a clean one', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page, [sampleShot('e2e-ann-1', 'ann.png', '2026-09-19T12:00:00Z')])
  await installAnnotationStore(page)
  await installBodyLedger(page)
  await page.getByTestId('nav-capture').click()
  await page.getByTestId('capture-filmstrip-item').first().click()
  await expect(page.getByTestId('capture-draw-surface')).toHaveAttribute('data-overlay-ready', 'true')
  await expect(page.getByTestId('capture-save')).toHaveCount(0)
  await page.keyboard.press('Control+S')
  await twoFrames(page)
  expect(await annotatePosts(page), 'Ctrl+S on a clean shot').toHaveLength(0)
  await page.getByTestId('capture-tool-arrow').click()
  await drawArrow(page)
  await expect(page.getByTestId('capture-save')).toBeEnabled()
  await page.keyboard.press('Control+S')
  await expect.poll(async () => (await annotatePosts(page)).length).toBe(1)
  const [posted] = await annotatePosts(page)
  expect(posted?.annotations.map((mark) => mark.type)).toEqual(['arrow'])
  await expect(page.getByTestId('capture-save')).toHaveCount(0)
  await page.keyboard.press('Control+S')
  await twoFrames(page)
  expect(await annotatePosts(page), 'a second Ctrl+S').toHaveLength(1)
  await app.close()
})

/** Draws one box on the 8x8 sample shot from image pixel (x1, y1) to (x2, y2). */
async function drawBoxAt(page: Page, x1: number, y1: number, x2: number, y2: number): Promise<void> {
  await page.getByTestId('capture-tool-box').click()
  const surface = page.getByTestId('capture-draw-surface')
  const box = await surface.boundingBox()
  expect(box).toBeTruthy()
  const scale = Math.min((box?.width ?? 1) / 8, (box?.height ?? 1) / 8)
  const originX = (box?.x ?? 0) + ((box?.width ?? 0) - 8 * scale) / 2
  const originY = (box?.y ?? 0) + ((box?.height ?? 0) - 8 * scale) / 2
  await page.mouse.move(originX + x1 * scale, originY + y1 * scale)
  await page.mouse.down()
  await page.mouse.move(originX + x2 * scale, originY + y2 * scale)
  await page.mouse.up()
}

test('AC-99.7 Ctrl+Z, Ctrl+Y and Ctrl+Shift+Z step the Capture history from the image and the body; a text draft keeps native undo', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page, [sampleShot('e2e-s43-1', 's43.png', '2026-10-29T12:00:00Z')])
  await installAnnotationStore(page)
  await installBodyLedger(page)
  await page.getByTestId('nav-capture').click()
  await page.getByTestId('capture-filmstrip-item').first().click()
  await expect(page.getByTestId('capture-draw-surface')).toHaveAttribute('data-overlay-ready', 'true')
  const rects = page.locator('[data-annotation-type="rect"]')
  await drawBoxAt(page, 1, 1, 3, 3)
  await drawBoxAt(page, 4, 4, 7, 7)
  await expect(rects).toHaveCount(2)
  await page.evaluate(() => {
    ;(window as unknown as { __s43Marker?: number }).__s43Marker = 1
  })
  // The chords act on the Capture history only: no page zoom, no navigation, no reload. Labels live in
  // test.step, not in expect messages, so a failure keeps Playwright's `expect(` header for red-check.
  const intact = async (): Promise<void> => {
    expect(await pageZoomFactor(app)).toBe(1)
    expect(new URL(page.url()).hash).toBe('#/capture')
    expect(await page.evaluate(() => (window as unknown as { __s43Marker?: number }).__s43Marker)).toBe(1)
  }
  await page.getByTestId('capture-draw-surface').focus()
  const steps: Array<[string, number]> = [
    ['Control+KeyZ', 1],
    ['Control+Shift+KeyZ', 2],
    ['Control+KeyZ', 1],
    ['Control+KeyY', 2],
  ]
  for (const [keys, count] of steps) {
    await test.step(`surface ${keys}`, async () => {
      await page.keyboard.press(keys)
      await expect.poll(() => rects.count()).toBe(count)
      await intact()
    })
  }
  await page.evaluate(() => {
    ;(document.activeElement as HTMLElement | null)?.blur()
  })
  await test.step('body Ctrl+Z', async () => {
    await page.keyboard.press('Control+KeyZ')
    await expect.poll(() => rects.count()).toBe(1)
    await intact()
  })
  await page.getByTestId('capture-save').click()
  await expect.poll(async () => (await annotatePosts(page)).length).toBe(1)
  const posted = (await annotatePosts(page))[0]?.annotations ?? []
  expect(posted.map((row) => row.type)).toEqual(['rect'])
  await page.getByTestId('capture-tool-text').click()
  await clickSampleImagePoint(page, 5, 1)
  const draft = page.getByTestId('capture-text-draft')
  await draft.pressSequentially('abc')
  await expect(draft).toHaveValue('abc')
  await test.step('draft Ctrl+Z keeps native undo', async () => {
    await draft.press('Control+KeyZ')
    expect((await draft.inputValue()).length).toBeLessThan(3)
    await expect(rects).toHaveCount(1)
    await intact()
  })
  await app.close()
})

/** The page point of image pixel (x, y) on the 8×8 sample shot. */
async function sampleImagePagePoint(page: Page, x: number, y: number): Promise<{ x: number; y: number }> {
  const box = await page.getByTestId('capture-draw-surface').boundingBox()
  expect(box).toBeTruthy()
  const scale = Math.min((box?.width ?? 1) / 8, (box?.height ?? 1) / 8)
  const originX = (box?.x ?? 0) + ((box?.width ?? 0) - 8 * scale) / 2
  const originY = (box?.y ?? 0) + ((box?.height ?? 0) - 8 * scale) / 2
  return { x: originX + x * scale, y: originY + y * scale }
}

async function centreOf(page: Page, testId: string): Promise<{ x: number; y: number }> {
  const box = await page.getByTestId(testId).boundingBox()
  expect(box).toBeTruthy()
  return { x: (box?.x ?? 0) + (box?.width ?? 0) / 2, y: (box?.y ?? 0) + (box?.height ?? 0) / 2 }
}

test('AC-100.11 a real drag on the se handle resizes a box as one step; Ctrl+Z and Ctrl+Y step it; the e handle shows ew-resize', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page, [sampleShot('e2e-s43-2', 's43-resize.png', '2026-10-29T12:05:00Z')])
  await installAnnotationStore(page)
  await installBodyLedger(page)
  await page.getByTestId('nav-capture').click()
  await page.getByTestId('capture-filmstrip-item').first().click()
  await expect(page.getByTestId('capture-draw-surface')).toHaveAttribute('data-overlay-ready', 'true')
  const rect = page.locator('[data-annotation-type="rect"]')
  const geometry = async (): Promise<number[]> =>
    Promise.all(['x', 'y', 'width', 'height'].map(async (name) => Number(await rect.getAttribute(name))))
  await drawBoxAt(page, 1, 1, 4, 4)
  await expect(rect).toHaveCount(1)
  await expect.poll(geometry).toEqual([1, 1, 3, 3])
  const se = page.getByTestId('capture-handle-resize-se')
  // A count poll first: a locator assertion on a missing element adds `element(s) not found`, which red-check
  // does not attribute as an assertion.
  await expect.poll(() => se.count()).toBe(1)
  await expect(se).toBeVisible()
  await test.step('drag the se handle to image (6,7)', async () => {
    const from = await centreOf(page, 'capture-handle-resize-se')
    const to = await sampleImagePagePoint(page, 6, 7)
    await page.mouse.move(from.x, from.y)
    await page.mouse.down()
    await page.mouse.move((from.x + to.x) / 2, (from.y + to.y) / 2)
    await page.mouse.move(to.x, to.y)
    await page.mouse.up()
    await expect(rect).toHaveCount(1)
    await expect.poll(geometry).toEqual([1, 1, 5, 6])
  })
  await test.step('hover the e handle', async () => {
    const east = await centreOf(page, 'capture-handle-resize-e')
    await page.mouse.move(east.x, east.y)
    await expect
      .poll(() => page.getByTestId('capture-draw-surface').evaluate((element) => getComputedStyle(element).cursor))
      .toBe('ew-resize')
  })
  await page.getByTestId('capture-draw-surface').focus()
  await test.step('Ctrl+Z restores the drawn box', async () => {
    await page.keyboard.press('Control+KeyZ')
    await expect.poll(geometry).toEqual([1, 1, 3, 3])
  })
  await test.step('Ctrl+Y reapplies the resize', async () => {
    await page.keyboard.press('Control+KeyY')
    await expect.poll(geometry).toEqual([1, 1, 5, 6])
  })
  await page.getByTestId('capture-save').click()
  await expect.poll(async () => (await annotatePosts(page)).length).toBe(1)
  const posted = (await annotatePosts(page))[0]?.annotations ?? []
  expect(posted).toHaveLength(1)
  expect(posted[0]).toMatchObject({ type: 'rect', x: 1, y: 1, width: 5, height: 6 })
  await app.close()
})

test('AC-101.6 a double-click reopens a committed text mark; Save posts the new text in place; a corner drag scales it', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page, [sampleShot('e2e-s43-3', 's43-text.png', '2026-10-29T12:10:00Z')])
  await installAnnotationStore(page)
  await installBodyLedger(page)
  await page.getByTestId('nav-capture').click()
  await page.getByTestId('capture-filmstrip-item').first().click()
  await expect(page.getByTestId('capture-draw-surface')).toHaveAttribute('data-overlay-ready', 'true')
  const text = page.locator('[data-annotation-type="text"]')
  const draft = page.getByTestId('capture-text-draft')
  await page.getByTestId('capture-tool-text').click()
  await page.getByTestId('capture-font-size').fill('2')
  await clickSampleImagePoint(page, 3, 6)
  await draft.fill('Note')
  await draft.press('Enter')
  await expect(text).toHaveCount(1)
  await expect(draft).toHaveCount(0)
  await page.getByTestId('capture-tool-select').click()
  await test.step('double-click the Note plate', async () => {
    // `Note` at font size 2 from (3,6) has the plate {3,7,4,1}; its centre is image (5,7.5).
    const centre = await sampleImagePagePoint(page, 5, 7.5)
    await page.mouse.dblclick(centre.x, centre.y)
    await expect.poll(() => draft.count()).toBe(1)
    await expect(draft).toHaveValue('Note')
  })
  await draft.fill('Done')
  await draft.press('Enter')
  await expect(draft).toHaveCount(0)
  await page.getByTestId('capture-save').click()
  await expect.poll(async () => (await annotatePosts(page)).length).toBe(1)
  const edited = (await annotatePosts(page))[0]?.annotations ?? []
  expect(edited).toHaveLength(1)
  expect(edited[0]).toMatchObject({ type: 'text', text: 'Done', x: 3, y: 6, font_size: 2 })
  await test.step('drag the nw plate corner outward', async () => {
    // `Done` has the plate {3,7,5,1}: its se corner is the image corner (8,8), where the clamped pointer
    // cannot move it outward, so the drag takes the nw corner (3,7) out to (0,0) about the se anchor.
    await page.getByTestId('capture-mark-list').locator('button', { hasText: 'Text' }).click()
    const nw = page.getByTestId('capture-handle-resize-nw')
    await expect.poll(() => nw.count()).toBe(1)
    const from = await centreOf(page, 'capture-handle-resize-nw')
    const to = await sampleImagePagePoint(page, 0, 0)
    await page.mouse.move(from.x, from.y)
    await page.mouse.down()
    await page.mouse.move((from.x + to.x) / 2, (from.y + to.y) / 2)
    await page.mouse.move(to.x, to.y)
    await page.mouse.up()
  })
  await page.getByTestId('capture-save').click()
  await expect.poll(async () => (await annotatePosts(page)).length).toBe(2)
  const scaled = (await annotatePosts(page))[1]?.annotations ?? []
  expect(scaled).toHaveLength(1)
  expect(scaled[0]).toMatchObject({ type: 'text', text: 'Done' })
  expect((scaled[0] as { font_size?: number }).font_size).toBeGreaterThan(2)
  await app.close()
})
