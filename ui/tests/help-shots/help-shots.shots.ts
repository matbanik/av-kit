/**
 * MEU-162 (Session 99, HELP_SHOTS_GEN, D-1292) writes the help card's screenshots:
 * `ui/src/renderer/src/assets/help/<name>-<theme>.webp` and `manifest.json`.
 *
 * For each page and for `light` then `dark` it launches the built app on a fresh scratch root
 * (`launchIsolated`), runs the page's demo stage, sets the theme and closes the help card. For
 * each shot it scrolls the targets to the middle of the view, measures every target box, widens
 * the boxes to whole rows of their `section` and adds their labels (context boxes, cut to the
 * viewport), and takes the clip from `shotClip` (S9 on an error). It draws a numbered badge and an outline on each target,
 * masks the elements that show machine paths, and converts the PNG to WebP of 150 KB or less in
 * the renderer. The privacy guard reads only the text that the image can show and blocks the
 * file on a private path (S10).
 *
 * The tests run in serial mode, so one failure skips the rest. The last test writes every file
 * and the manifest, and only when every page and theme passed in this run. A `--grep` run never
 * writes.
 *
 * `AVKIT_HELP_SHOTS_STAGE` names another `stage.ts` for the stages (the planted negative run of
 * row 8). That file imports `../e2e/electron-app` and `@playwright/test`, which resolve only from
 * this folder, so the generator copies it here under a temporary name, imports it and deletes
 * the copy.
 */

import { test, type Locator, type Page } from '@playwright/test'
import { createHash } from 'node:crypto'
import { copyFileSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs'
import { homedir, tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

import { CAPTURE_KEY_DEFAULT, captureKeyText } from '../../src/renderer/src/features/capture/capture-key'
import { CLIP_MAX_HEIGHT, CLIP_MAX_WIDTH, shotClip, type Rect, type TargetBox } from './clip'
import { clipText, findPrivatePath, type TextItem } from './privacy'
import { FEATURE_PAGES, HELP_FEATURES, STAGES, launchIsolated, type HelpFeature, type IsolatedApp } from './stage'

const here = dirname(fileURLToPath(import.meta.url))
const REPO_ROOT = resolve(here, '../../..')
const QUICK_START_FILE = resolve(here, '../../src/renderer/src/components/help/quick-start.json')
const ASSETS = resolve(here, '../../src/renderer/src/assets/help')

const THEMES = ['light', 'dark'] as const
type Theme = (typeof THEMES)[number]

/** The two elements that show machine paths (the MCP prompt and the Console log path). */
const SHOT_MASKS = ['mcp-setup-prompt', 'settings-log-row']
const MAX_BYTES = 153_600
const QUALITY_START = 0.85
const QUALITY_STEP = 0.05
const QUALITY_FLOOR = 0.5

type QuickStartPage = {
  intro: string
  steps: Array<{ text: string; target: string | null }>
  shots: Array<{ name: string; steps: number[]; alt: string }>
}

type Taken = { name: string; feature: HelpFeature; theme: Theme; width: number; height: number; webp: Buffer }

const QUICK_START = (JSON.parse(readFileSync(QUICK_START_FILE, 'utf8')) as { pages: Record<HelpFeature, QuickStartPage> })
  .pages

/** The same string as `quickStartHashInput(page)` in `quick-start.ts`, hashed by `node:crypto`. */
function stepsHash(page: QuickStartPage): string {
  // MEU-165: the default reading (CAPTURE_KEY_DEFAULT_READING), the page `QUICK_START` holds in the app.
  const steps = page.steps.map((step) => ({ ...step, text: captureKeyText(step.text, CAPTURE_KEY_DEFAULT) }))
  const shots = page.shots.map((shot) => ({ ...shot, alt: captureKeyText(shot.alt, CAPTURE_KEY_DEFAULT) }))
  return createHash('sha256')
    .update(JSON.stringify({ steps, shots }))
    .digest('hex')
}

/** Every file of this run, kept in memory until the last test writes them all. */
const taken: Taken[] = []
let stages: Record<HelpFeature, (page: Page) => Promise<void>> = STAGES

async function loadStages(): Promise<void> {
  const override = process.env.AVKIT_HELP_SHOTS_STAGE
  if (override === undefined || override.trim() === '') return
  const copy = join(here, `.stage-override-${process.pid}.ts`)
  copyFileSync(override, copy)
  try {
    const module = (await import(pathToFileURL(copy).href)) as {
      STAGES: Record<HelpFeature, (page: Page) => Promise<void>>
    }
    stages = module.STAGES
  } finally {
    rmSync(copy, { force: true })
  }
  console.log(`stage override: ${override}`)
}

// ---------------------------------------------------------------------------
// In-page functions. Each runs through `page.evaluate`: no imports, nothing from this module.
// ---------------------------------------------------------------------------

/** PRIVACY_GUARD (F6): every text node and control value with its rects and its masked flag. */
function gatherShotText(masks: string[]): TextItem[] {
  const maskEls: Element[] = []
  for (const id of masks) {
    maskEls.push(...Array.from(document.querySelectorAll(`[data-testid="${id}"]`)))
  }
  const isMasked = (el: Element | null): boolean => {
    if (el === null) return true
    for (let e: Element | null = el; e !== null; e = e.parentElement) {
      if (maskEls.includes(e)) return true
    }
    return getComputedStyle(el).visibility !== 'visible'
  }
  const toRect = (r: DOMRect) => ({ x: r.x, y: r.y, width: r.width, height: r.height })
  const items: Array<{ text: string; rects: Array<{ x: number; y: number; width: number; height: number }>; masked: boolean }> = []
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT)
  for (let node = walker.nextNode(); node !== null; node = walker.nextNode()) {
    const text = node.nodeValue ?? ''
    if (text.trim() === '') continue
    const range = document.createRange()
    range.selectNodeContents(node)
    items.push({ text, rects: Array.from(range.getClientRects()).map(toRect), masked: isMasked(node.parentElement) })
  }
  for (const el of Array.from(document.querySelectorAll('input, textarea, select'))) {
    const control = el as HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    const placeholder = control instanceof HTMLSelectElement ? '' : control.placeholder
    const text = control.value !== '' ? control.value : placeholder
    if (text === '') continue
    items.push({ text, rects: [toRect(control.getBoundingClientRect())], masked: isMasked(control) })
  }
  return items
}

/** Draws the outline and badge of each mark; returns the badges that are not fully in the clip. */
function drawOverlay(init: {
  marks: Array<{ step: number; x: number; y: number; width: number; height: number }>
  clip: { x: number; y: number; width: number; height: number }
}): string[] {
  const layer = document.createElement('div')
  layer.id = 'help-shot-overlay'
  layer.style.cssText = 'position:fixed;inset:0;pointer-events:none;z-index:2147483647'
  for (const mark of init.marks) {
    const ring = document.createElement('div')
    ring.style.cssText = [
      'position:fixed',
      `left:${mark.x - 3}px`,
      `top:${mark.y - 3}px`,
      `width:${mark.width + 6}px`,
      `height:${mark.height + 6}px`,
      'border:2px solid var(--color-accent)',
      'border-radius:var(--radius-md)',
      'box-sizing:border-box',
    ].join(';')
    const badge = document.createElement('div')
    badge.dataset.helpShotBadge = String(mark.step)
    badge.textContent = String(mark.step)
    badge.style.cssText = [
      'position:fixed',
      `left:${mark.x - 16}px`,
      `top:${mark.y - 16}px`,
      'width:22px',
      'height:22px',
      'border-radius:var(--radius-full)',
      'background:var(--color-accent)',
      'color:var(--color-accent-fg)',
      'font:700 12px/22px system-ui, sans-serif',
      'text-align:center',
      'box-shadow:0 0 0 2px var(--color-bg)',
    ].join(';')
    layer.append(ring, badge)
  }
  document.body.append(layer)
  const { clip } = init
  const outside: string[] = []
  for (const badge of Array.from(layer.querySelectorAll<HTMLElement>('[data-help-shot-badge]'))) {
    const r = badge.getBoundingClientRect()
    const inside =
      r.left >= clip.x &&
      r.top >= clip.y &&
      r.right <= clip.x + clip.width &&
      r.bottom <= clip.y + clip.height
    if (!inside) outside.push(`badge ${badge.dataset.helpShotBadge} at ${r.left},${r.top}`)
  }
  return outside
}

function removeOverlay(): void {
  document.getElementById('help-shot-overlay')?.remove()
}

/** PNG (base64) to WebP at the first quality from 0.85 down that is 150 KB or less. */
async function toWebp(init: {
  png: string
  width: number
  height: number
  start: number
  step: number
  floor: number
  maxBytes: number
}): Promise<{ data: string; quality: number; bytes: number; type: string }> {
  const raw = Uint8Array.from(atob(init.png), (c) => c.charCodeAt(0))
  const bitmap = await createImageBitmap(new Blob([raw], { type: 'image/png' }))
  const canvas = document.createElement('canvas')
  canvas.width = init.width
  canvas.height = init.height
  const context = canvas.getContext('2d')
  if (context === null) throw new Error('no 2d context')
  context.drawImage(bitmap, 0, 0, init.width, init.height)
  let last = { data: '', quality: 0, bytes: Number.POSITIVE_INFINITY, type: '' }
  for (let i = 0; ; i += 1) {
    const quality = Math.round((init.start - init.step * i) * 100) / 100
    if (quality < init.floor) break
    const url = canvas.toDataURL('image/webp', quality)
    const comma = url.indexOf(',')
    const data = url.slice(comma + 1)
    const padding = data.endsWith('==') ? 2 : data.endsWith('=') ? 1 : 0
    const bytes = (data.length * 3) / 4 - padding
    last = { data, quality, bytes, type: url.slice(0, comma) }
    if (bytes <= init.maxBytes) break
  }
  return last
}

/**
 * Scrolls the first target's scroll container so that the union of the targets sits in the middle
 * of the visible area, with room above for the labels. A union too tall to center starts 48 px
 * below the top of the visible area.
 */
function centerTargets(ids: string[]): void {
  const elements = ids
    .map((id) => document.querySelector(`[data-testid="${CSS.escape(id)}"]`))
    .filter((el): el is HTMLElement => el instanceof HTMLElement)
  const first = elements[0]
  if (first === undefined) return
  first.scrollIntoView({ block: 'center' })
  let scroller: HTMLElement | null = first.parentElement
  while (scroller !== null) {
    const overflow = getComputedStyle(scroller).overflowY
    if ((overflow === 'auto' || overflow === 'scroll') && scroller.scrollHeight > scroller.clientHeight) break
    scroller = scroller.parentElement
  }
  const rects = elements.map((el) => el.getBoundingClientRect())
  const top = Math.min(...rects.map((r) => r.top))
  const bottom = Math.max(...rects.map((r) => r.bottom))
  const frame = scroller === null ? { top: 0, height: window.innerHeight } : scroller.getBoundingClientRect()
  const viewTop = Math.max(0, frame.top)
  const viewBottom = Math.min(window.innerHeight, frame.top + (scroller === null ? frame.height : scroller.clientHeight))
  const delta =
    bottom - top + 96 > viewBottom - viewTop ? top - 48 - viewTop : (top + bottom) / 2 - (viewTop + viewBottom) / 2
  if (scroller === null) window.scrollBy(0, delta)
  else scroller.scrollTop += delta
}

/**
 * The context of each target, so that the image shows whole rows: the target's own rows across the
 * full width of its nearest `section`, and each `<label>` of the target. These boxes only widen the
 * clip; they carry no badge and no outline.
 */
function contextBoxes(ids: string[]): Array<{ x: number; y: number; width: number; height: number }> {
  const boxes: Array<{ x: number; y: number; width: number; height: number }> = []
  for (const id of ids) {
    const el = document.querySelector(`[data-testid="${CSS.escape(id)}"]`)
    if (!(el instanceof HTMLElement)) continue
    const own = el.getBoundingClientRect()
    const section = el.parentElement?.closest('section')
    if (section instanceof HTMLElement) {
      const s = section.getBoundingClientRect()
      boxes.push({ x: s.left, y: own.top, width: s.width, height: own.height })
    }
    const labels = (el as Partial<HTMLInputElement>).labels
    if (labels !== undefined && labels !== null) {
      for (const label of Array.from(labels)) {
        const l = label.getBoundingClientRect()
        boxes.push({ x: l.left, y: l.top, width: l.width, height: l.height })
      }
    }
  }
  return boxes
}

function nextFrames(): Promise<void> {
  return new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(() => done())))
}

// ---------------------------------------------------------------------------
// Node side.
// ---------------------------------------------------------------------------

/** The G30 select background per theme, as `SelectInput.tsx` `G30_PAIRS` sets it inline. */
const G30_BACKGROUND: Record<Theme, string> = { dark: 'rgb(26, 26, 46)', light: 'rgb(255, 255, 255)' }

/**
 * The app's own theme switch (`applyDocumentTheme` in `lib/theme.ts`): the `dark` class, the
 * colour scheme and the theme event, so controls that follow the event (the G30 select colours)
 * render in the theme too. Then a select whose inline background is still the other theme's G30
 * colour refuses the shot (D-1295); a select styled by a CSS variable follows the class itself.
 */
async function applyTheme(page: Page, theme: Theme): Promise<void> {
  await page.evaluate((t) => {
    const root = document.documentElement
    root.classList.toggle('dark', t === 'dark')
    root.style.colorScheme = t
    window.dispatchEvent(new CustomEvent('av-kit:theme-changed', { detail: { theme: t } }))
  }, theme)
  await page.evaluate(
    () => new Promise<void>((done) => requestAnimationFrame(() => requestAnimationFrame(() => done()))),
  )
  const other: Theme = theme === 'dark' ? 'light' : 'dark'
  const wrong = await page.evaluate(
    (stale) =>
      Array.from(document.querySelectorAll('select'))
        .filter((s) => s.style.backgroundColor === stale)
        .map((s) => `${s.id || s.getAttribute('data-testid') || 'select'}=${s.style.backgroundColor}`),
    G30_BACKGROUND[other],
  )
  if (wrong.length > 0) throw new Error(`theme ${theme}: select colour not switched: ${wrong.join(', ')}`)
}

function meets(a: Rect, b: Rect): boolean {
  return a.x < b.x + b.width && b.x < a.x + a.width && a.y < b.y + b.height && b.y < a.y + a.height
}

/** How far a badge reaches outside its target: the badge at -16 px plus its 2 px ring. */
const BADGE_REACH = 18
/** How far the outline reaches outside its target. */
const RING_REACH = 3
const TIDY_GAP = 4
const TIDY_PASSES = 8

/**
 * Moves each clip edge off every line of text and every control that it cuts, so that no text is
 * cut in the image. An edge moves inward when the line lies wholly past the targets, their badges
 * and their outlines; otherwise it moves outward, never past the viewport. Masked items show as a
 * plain block and are ignored, and so is an item that crosses both opposite edges.
 */
function tidyClip(
  clip: Rect,
  items: readonly TextItem[],
  targets: readonly Rect[],
  viewport: { width: number; height: number },
): Rect {
  const keep = {
    left: Math.min(...targets.map((t) => t.x)) - BADGE_REACH,
    top: Math.min(...targets.map((t) => t.y)) - BADGE_REACH,
    right: Math.max(...targets.map((t) => t.x + t.width)) + RING_REACH,
    bottom: Math.max(...targets.map((t) => t.y + t.height)) + RING_REACH,
  }
  let left = clip.x
  let top = clip.y
  let right = clip.x + clip.width
  let bottom = clip.y + clip.height
  const rects = items
    .filter((item) => !item.masked && item.text.trim() !== '')
    .flatMap((item) => item.rects)
    .filter((r) => r.width > 0 && r.height > 0)
  for (let pass = 0; pass < TIDY_PASSES; pass += 1) {
    let changed = false
    for (const r of rects) {
      const rRight = r.x + r.width
      const rBottom = r.y + r.height
      if (!(r.x < right && rRight > left && r.y < bottom && rBottom > top)) continue
      if (r.y < bottom && rBottom > bottom && r.y >= top) {
        const inward = Math.floor(r.y) - TIDY_GAP
        bottom = inward >= keep.bottom ? inward : Math.min(viewport.height, Math.ceil(rBottom) + TIDY_GAP)
        changed = true
      } else if (r.y < top && rBottom > top && rBottom <= bottom) {
        const inward = Math.ceil(rBottom) + TIDY_GAP
        top = inward <= keep.top ? inward : Math.max(0, Math.floor(r.y) - TIDY_GAP)
        changed = true
      }
      if (r.x < right && rRight > right && r.x >= left) {
        const inward = Math.floor(r.x) - TIDY_GAP
        right = inward >= keep.right ? inward : Math.min(viewport.width, Math.ceil(rRight) + TIDY_GAP)
        changed = true
      } else if (r.x < left && rRight > left && rRight <= right) {
        const inward = Math.ceil(rRight) + TIDY_GAP
        left = inward <= keep.left ? inward : Math.max(0, Math.floor(r.x) - TIDY_GAP)
        changed = true
      }
    }
    if (!changed) break
  }
  return { x: left, y: top, width: right - left, height: bottom - top }
}

async function closeHelpCard(page: Page, feature: HelpFeature): Promise<void> {
  const header = page
    .getByTestId(FEATURE_PAGES[feature].page)
    .getByTestId('help-card')
    .locator('button[aria-expanded]')
    .first()
  if ((await header.getAttribute('aria-expanded')) === 'true') {
    await header.click()
  }
  await page.evaluate(() => {
    const active = document.activeElement
    if (active instanceof HTMLElement) active.blur()
  })
  await page.mouse.move(0, 0)
}

async function takeShot(
  page: Page,
  feature: HelpFeature,
  theme: Theme,
  shot: QuickStartPage['shots'][number],
  roots: readonly string[],
): Promise<Taken> {
  const label = `${shot.name}-${theme}`
  const steps = QUICK_START[feature].steps
  const marks = shot.steps.map((n) => {
    const target = steps[n - 1]?.target
    if (target === null || target === undefined) throw new Error(`S9: ${label}: step ${n} has no target`)
    return { step: n, target }
  })
  const first = marks[0]
  if (first === undefined) throw new Error(`S9: ${label}: the shot has no steps`)
  const ids = marks.map((mark) => mark.target)
  await page.evaluate(centerTargets, ids)
  await page.evaluate(nextFrames)

  const boxes: TargetBox[] = []
  for (const mark of marks) {
    const box = await page.getByTestId(mark.target).first().boundingBox()
    if (box === null) throw new Error(`S9: ${label}: target ${mark.target} has no box`)
    boxes.push({ ...box, target: mark.target })
  }
  const viewport = await page.evaluate(() => ({ width: window.innerWidth, height: window.innerHeight }))
  // Context boxes are cut to the viewport; a target box never is (`shotClip` checks it).
  const context: TargetBox[] = []
  for (const box of await page.evaluate(contextBoxes, ids)) {
    const x = Math.max(0, box.x)
    const y = Math.max(0, box.y)
    const width = Math.min(viewport.width, box.x + box.width) - x
    const height = Math.min(viewport.height, box.y + box.height) - y
    if (width > 0 && height > 0) context.push({ x, y, width, height, target: 'context' })
  }
  const result = shotClip([...boxes, ...context], viewport)
  if (!result.ok) throw new Error(`S9: ${label}: ${result.error}`)
  const items = await page.evaluate(gatherShotText, SHOT_MASKS)
  const clip = tidyClip(result.clip, items, boxes, viewport)
  if (clip.width > CLIP_MAX_WIDTH || clip.height > CLIP_MAX_HEIGHT) {
    throw new Error(`S9: ${label}: the tidied clip is ${clip.width} x ${clip.height}, over the cap`)
  }

  const masks: Locator[] = []
  for (const id of SHOT_MASKS) {
    for (const element of await page.getByTestId(id).all()) {
      const box = await element.boundingBox()
      if (box === null || !meets(box, clip)) continue
      const hit = boxes.find((target) => meets(box, target))
      if (hit !== undefined) throw new Error(`S9: ${label}: mask ${id} meets target ${hit.target}`)
      masks.push(element)
    }
  }

  if (findPrivatePath(clipText(items, clip), roots) !== null) {
    console.log(`privacy: blocked ${label}`)
    throw new Error(`S10: ${label} shows a private path; no file is written`)
  }

  const maskColor = await page.evaluate(() =>
    getComputedStyle(document.documentElement).getPropertyValue('--color-bg-elevated').trim(),
  )
  const outside = await page.evaluate(drawOverlay, {
    marks: marks.map((mark, i) => ({ step: mark.step, ...(boxes[i] as Rect) })),
    clip,
  })
  if (outside.length > 0) {
    await page.evaluate(removeOverlay)
    throw new Error(`S9: ${label}: ${outside.join(', ')} outside the clip`)
  }
  let png: Buffer
  try {
    png = await page.screenshot({ clip, mask: masks, maskColor, scale: 'css', animations: 'disabled' })
  } finally {
    await page.evaluate(removeOverlay)
  }

  const webp = await page.evaluate(toWebp, {
    png: png.toString('base64'),
    width: clip.width,
    height: clip.height,
    start: QUALITY_START,
    step: QUALITY_STEP,
    floor: QUALITY_FLOOR,
    maxBytes: MAX_BYTES,
  })
  if (webp.type !== 'data:image/webp;base64') throw new Error(`S9: ${label}: the canvas gave ${webp.type}`)
  if (webp.bytes > MAX_BYTES) {
    throw new Error(`S9: ${label}: ${webp.bytes} bytes at quality ${webp.quality}, over ${MAX_BYTES}`)
  }
  console.log(`privacy: clean ${label}`)
  console.log(`shot ${label}: ${clip.width} x ${clip.height}, quality ${webp.quality}, ${webp.bytes} bytes`)
  return {
    name: shot.name,
    feature,
    theme,
    width: clip.width,
    height: clip.height,
    webp: Buffer.from(webp.data, 'base64'),
  }
}

function writeAll(): void {
  const names = HELP_FEATURES.flatMap((feature) => QUICK_START[feature].shots.map((shot) => shot.name))
  const manifest = []
  for (const feature of HELP_FEATURES) {
    for (const shot of QUICK_START[feature].shots) {
      const light = taken.find((t) => t.name === shot.name && t.theme === 'light')
      const dark = taken.find((t) => t.name === shot.name && t.theme === 'dark')
      if (light === undefined || dark === undefined) throw new Error(`write: ${shot.name} has no ${light ? 'dark' : 'light'} image`)
      if (light.width !== dark.width || light.height !== dark.height) {
        throw new Error(
          `S9: ${shot.name}: light ${light.width} x ${light.height}, dark ${dark.width} x ${dark.height}`,
        )
      }
      manifest.push({
        name: shot.name,
        page: feature,
        width: light.width,
        height: light.height,
        bytes: { light: light.webp.length, dark: dark.webp.length },
        stepsHash: stepsHash(QUICK_START[feature]),
      })
    }
  }
  mkdirSync(ASSETS, { recursive: true })
  for (const file of readdirSync(ASSETS)) {
    if (file.endsWith('.webp') || file === 'manifest.json') rmSync(join(ASSETS, file))
  }
  for (const item of taken) {
    writeFileSync(join(ASSETS, `${item.name}-${item.theme}.webp`), item.webp)
  }
  writeFileSync(join(ASSETS, 'manifest.json'), `${JSON.stringify(manifest, null, 2)}\n`, 'utf8')
  console.log(`wrote ${taken.length} images and manifest.json for ${names.length} shots`)
}

test.describe.configure({ mode: 'serial' })

test.describe('help shots', () => {
  test.beforeAll(async () => {
    await loadStages()
  })

  for (const feature of HELP_FEATURES) {
    for (const theme of THEMES) {
      test(`${feature} ${theme}`, async () => {
        let isolated: IsolatedApp | undefined
        try {
          isolated = await launchIsolated()
          const { page, root, home } = isolated
          const roots = [homedir(), home, root, tmpdir(), REPO_ROOT]
          await stages[feature](page)
          await applyTheme(page, theme)
          await closeHelpCard(page, feature)
          for (const shot of QUICK_START[feature].shots) {
            taken.push(await takeShot(page, feature, theme, shot, roots))
          }
        } finally {
          await isolated?.app.close()
        }
      })
    }
  }

  test('write the images and the manifest', () => {
    const want = HELP_FEATURES.reduce((n, feature) => n + QUICK_START[feature].shots.length, 0) * THEMES.length
    if (taken.length !== want) throw new Error(`write: ${taken.length} images taken, ${want} expected`)
    writeAll()
  })
})
