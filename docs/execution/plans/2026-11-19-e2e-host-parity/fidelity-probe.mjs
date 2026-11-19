// Session 97 probe (task row 1; D-1242, D-1245): does the device scale and the sub-pixel origin
// hide the plate gap? It builds two views of the committed fidelity fixture in probe-app.cjs's
// window at a chosen CSS origin and measures them with the spec's fidelityBoxes rule (copied from
// ui/tests/e2e/capture-inbox.test.ts). Preview: the original PNG plus an SVG plate for "Hi" at
// (20, 30), size 32, at the old width 30 (x 20, y 42, height 24) and the planned width 32, plus
// the SVG text. Bake: the annotated PNG. Each launch (native, then --force-device-scale-factor=1)
// measures three origins.
// Usage: pwsh -NoProfile -File run-probe.ps1 -Probe fidelity
// It launches only probe-app.cjs, closes each app it launched and prints one JSON line per case.
import { readFileSync } from 'node:fs'
import { createRequire } from 'node:module'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const ui = resolve(here, '../../../../ui')
const require = createRequire(join(ui, 'package.json'))
const { _electron } = require('@playwright/test')
const electronPath = require('electron')
const fixtures = join(ui, 'tests/e2e/fixtures')
const original = readFileSync(join(fixtures, 'capture-fidelity-original.png')).toString('base64')
const annotated = readFileSync(join(fixtures, 'capture-fidelity-annotated.png')).toString('base64')

const env = { ...process.env }
delete env.ELECTRON_RUN_AS_NODE

async function build(page, view, left, top, plateWidth) {
  await page.evaluate(
    ({ view, left, top, original, annotated, plateWidth }) => {
      document.body.innerHTML = ''
      document.body.style.margin = '0'
      document.body.style.background = '#1a1b26'
      const box = document.createElement('div')
      box.style.cssText = `position:absolute;left:${left}px;top:${top}px;width:240px;height:120px`
      const img = document.createElement('img')
      img.id = 'img'
      img.style.cssText = 'position:absolute;left:0;top:0;width:240px;height:120px'
      img.src = 'data:image/png;base64,' + (view === 'bake' ? annotated : original)
      box.appendChild(img)
      if (view === 'preview') {
        const ns = 'http://www.w3.org/2000/svg'
        const svg = document.createElementNS(ns, 'svg')
        svg.setAttribute('viewBox', '0 0 240 120')
        svg.setAttribute('width', '240')
        svg.setAttribute('height', '120')
        svg.style.cssText = 'position:absolute;left:0;top:0;pointer-events:none'
        const rect = document.createElementNS(ns, 'rect')
        for (const [k, v] of Object.entries({ x: 20, y: 42, width: plateWidth, height: 24, fill: '#FFD400' })) rect.setAttribute(k, String(v))
        const text = document.createElementNS(ns, 'text')
        for (const [k, v] of Object.entries({ x: 20, y: 65, fill: '#000000', 'font-size': 32, 'font-family': '"Segoe UI", Arial, sans-serif', 'dominant-baseline': 'alphabetic' })) text.setAttribute(k, String(v))
        text.textContent = 'Hi'
        svg.append(rect, text)
        box.appendChild(svg)
      }
      document.body.appendChild(box)
      return new Promise((done) => (img.complete ? done() : (img.onload = () => done())))
    },
    { view, left, top, original, annotated, plateWidth },
  )
  await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))))
}

async function measure(page) {
  const shot = await page.locator('#img').screenshot({ scale: 'device' })
  return page.evaluate(async (b64) => {
    const data = Uint8Array.from(atob(b64), (c) => c.charCodeAt(0))
    const bitmap = await createImageBitmap(new Blob([data], { type: 'image/png' }))
    const canvas = document.createElement('canvas')
    canvas.width = bitmap.width
    canvas.height = bitmap.height
    const context = canvas.getContext('2d')
    context.drawImage(bitmap, 0, 0)
    const pixels = context.getImageData(0, 0, bitmap.width, bitmap.height).data
    const dpr = window.devicePixelRatio || 1
    const inset = Math.ceil(2 * dpr)
    const rect = document.getElementById('img').getBoundingClientRect()
    const grow = (box, x, y) => ({ left: Math.min(box?.left ?? x, x), top: Math.min(box?.top ?? y, y), right: Math.max(box?.right ?? x, x), bottom: Math.max(box?.bottom ?? y, y) })
    let ink = null
    let plate = null
    for (let y = inset; y < bitmap.height - inset; y += 1) {
      for (let x = inset; x < bitmap.width - inset; x += 1) {
        const i = (y * bitmap.width + x) * 4
        const r = pixels[i]
        const g = pixels[i + 1]
        const b = pixels[i + 2]
        if (0.299 * r + 0.587 * g + 0.114 * b < 96) ink = grow(ink, x, y)
        if (Math.abs(r - 0xff) <= 40 && Math.abs(g - 0xd4) <= 40 && Math.abs(b - 0x00) <= 40) plate = grow(plate, x, y)
      }
    }
    const toImage = (box) => (box === null ? null : { left: Math.floor(box.left / dpr), top: Math.floor(box.top / dpr), right: Math.floor(box.right / dpr), bottom: Math.floor(box.bottom / dpr) })
    return { dpr, ink: toImage(ink), plate: toImage(plate), rect: { left: rect.left, top: rect.top } }
  }, shot.toString('base64'))
}

const pids = []
for (const [launch, extra] of [['native', []], ['dpr1', ['--force-device-scale-factor=1']]]) {
  const app = await _electron.launch({ executablePath: electronPath, args: [join(here, 'probe-app.cjs'), ...extra], env })
  pids.push(app.process().pid)
  try {
    const page = await app.firstWindow()
    await page.getByTestId('b').waitFor()
    for (const [left, top] of [[719.5, 444.5], [718, 442.5], [718, 442]]) {
      await build(page, 'bake', left, top, 0)
      const bake = await measure(page)
      for (const plateWidth of [30, 32]) {
        await build(page, 'preview', left, top, plateWidth)
        const preview = await measure(page)
        const gap = ['left', 'top', 'right', 'bottom'].map((s) => Math.abs((preview.plate?.[s] ?? 0) - (bake.plate?.[s] ?? 0)))
        console.log(JSON.stringify({ launch, origin: [left, top], plate_width: plateWidth, preview, bake, plate_gap_ltrb: gap, oracle_plate_passes: Math.max(...gap) <= 1 }))
      }
    }
  } finally {
    await app.close()
  }
}
console.log(JSON.stringify({ step: 'done', launched_pids: pids }))
