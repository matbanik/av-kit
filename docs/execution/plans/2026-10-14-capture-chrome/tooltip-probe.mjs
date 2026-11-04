// ROOT_CAUSE_PROBE (Session 34 row 2, AC-80.12). Plan-local, not product.
//
// Launches the built app under Playwright _electron, then for each hypothesis moves the real OS cursor over
// nav-capture and capture-tool-arrow, waits 1500 ms and captures the window's content rect from the screen, so
// a native tooltip (a separate layered window) shows in the PNG if Chromium drew one. All coordinates written
// to the run record are physical screen pixels. Usage:
//   node tooltip-probe.mjs --out C:/Temp/av-kit --run C:/Temp/av-kit/s34-probe-run.json
// validate-task.ps1 -Check probe runs it and adds the binding fields (D-31); do not run it by hand for row 2.
import { spawnSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { mkdtempSync, readFileSync, writeFileSync } from 'node:fs'
import { createRequire } from 'node:module'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const repo = resolve(here, '../../../..')
const { _electron } = createRequire(join(repo, 'ui/package.json'))('@playwright/test')

const TARGETS = ['nav-capture', 'capture-tool-arrow']
const HOVER_MS = 1500

function arg(name) {
  const i = process.argv.indexOf(name)
  if (i < 0 || i + 1 >= process.argv.length) throw new Error(`missing ${name}`)
  return process.argv[i + 1]
}

/** Local time with its UTC offset, so the record's times are zoned. */
function zoned(d = new Date()) {
  const off = -d.getTimezoneOffset()
  const pad = (n, w = 2) => String(Math.abs(n)).padStart(w, '0')
  const local = new Date(d.getTime() + off * 60000).toISOString().slice(0, 23)
  return `${local}${off >= 0 ? '+' : '-'}${pad(Math.trunc(off / 60))}:${pad(off % 60)}`
}

/**
 * One pwsh helper per observation: park the cursor outside the window, move it to the target (H2 moves it a
 * second time, 3 px away), wait HOVER_MS, then copy the window rect from the screen DC with SRCCOPY | CAPTUREBLT
 * (the GDI BitBlt that Graphics.CopyFromScreen wraps; .NET rejects the combined flag, and CAPTUREBLT is what
 * includes layered tooltip windows). The helper is per-monitor DPI aware, so SetCursorPos and the capture use physical pixels.
 */
function hoverAndCapture({ park, cursor, nudge, win, png }) {
  const script = `
$ErrorActionPreference = 'Stop'
Add-Type -Namespace S34 -Name U32 -MemberDefinition @'
[DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
[DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(System.IntPtr value);
[DllImport("user32.dll")] public static extern System.IntPtr GetDC(System.IntPtr hwnd);
[DllImport("user32.dll")] public static extern int ReleaseDC(System.IntPtr hwnd, System.IntPtr dc);
[DllImport("gdi32.dll")] public static extern bool BitBlt(System.IntPtr dest, int x, int y, int w, int h, System.IntPtr src, int sx, int sy, int rop);
'@
[void][S34.U32]::SetProcessDpiAwarenessContext([System.IntPtr]::new(-4))
Add-Type -AssemblyName System.Drawing
[void][S34.U32]::SetCursorPos(${park.x}, ${park.y})
Start-Sleep -Milliseconds 400
[void][S34.U32]::SetCursorPos(${cursor.x}, ${cursor.y})
${nudge ? `Start-Sleep -Milliseconds 200\n[void][S34.U32]::SetCursorPos(${nudge.x}, ${nudge.y})` : ''}
Start-Sleep -Milliseconds ${HOVER_MS}
$bmp = [System.Drawing.Bitmap]::new(${win.width}, ${win.height}, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$screenDc = [S34.U32]::GetDC([System.IntPtr]::Zero)
$dest = $g.GetHdc()
$ok = [S34.U32]::BitBlt($dest, 0, 0, ${win.width}, ${win.height}, $screenDc, ${win.x}, ${win.y}, 0x40CC0020)
$g.ReleaseHdc($dest)
[void][S34.U32]::ReleaseDC([System.IntPtr]::Zero, $screenDc)
$g.Dispose()
if (-not $ok) { throw 'BitBlt failed' }
$bmp.Save('${png.replace(/'/g, "''")}', [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
`
  const encoded = Buffer.from(script, 'utf16le').toString('base64')
  const res = spawnSync('pwsh', ['-NoProfile', '-NonInteractive', '-EncodedCommand', encoded], { encoding: 'utf8' })
  if (res.status !== 0) throw new Error(`capture helper exit ${res.status}: ${res.stderr || res.stdout}`)
}

async function main() {
  const out = arg('--out')
  const runPath = arg('--run')
  const env = { ...process.env, AVKIT_E2E: '1', AVKIT_APP_DATA: mkdtempSync(join(tmpdir(), 'avkit-s34-probe-')) }
  delete env.ELECTRON_RUN_AS_NODE

  const app = await _electron.launch({ args: [join(repo, 'ui/out/main/index.js')], cwd: join(repo, 'ui'), env })
  const observations = []
  try {
    const page = await app.firstWindow()
    // The capture-inbox E2E fetch seam, trimmed to what the Capture page reads, with one seeded shot. The shot
    // matters: with none selected every tool button is disabled, and Button's disabled:pointer-events-none
    // means the cursor never reaches it, so the probe would not be testing the native tooltip at all.
    await page.addInitScript(() => {
      const shot = {
        id: 's34-probe-shot', original_path: 'C:/e2e/probe.png', annotated_path: null, sidecar_path: null,
        display_name: 'probe.png', width: 8, height: 8, file_size: 32, source: 'gui',
        created_at: '2026-10-14T00:00:00Z', updated_at: '2026-10-14T00:00:00Z',
      }
      const png = Uint8Array.from([
        137, 80, 78, 71, 13, 10, 26, 10, 0, 0, 0, 13, 73, 72, 68, 82, 0, 0, 0, 1, 0, 0, 0, 1, 8, 6, 0, 0, 0,
        31, 21, 196, 137, 0, 0, 0, 13, 73, 68, 65, 84, 120, 156, 99, 0, 1, 0, 0, 5, 0, 1, 13, 10, 45, 180, 0,
        0, 0, 0, 73, 69, 78, 68, 174, 66, 96, 130,
      ])
      const original = window.fetch.bind(window)
      window.fetch = async (input, init) => {
        const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
        const json = (body) => new Response(JSON.stringify(body), { headers: { 'Content-Type': 'application/json' } })
        if (url.includes('/health/dependencies')) return json({ ffmpeg: { available: true, version: '7.1.2' }, yt_dlp: { available: true } })
        if (url.includes('/settings/capture')) return json({ inbox_dir: '~/Pictures/av-kit', hotkey: 'F2', copy_to_clipboard: false, close_to_tray: true })
        if (url.includes('/captures/requests')) return json({ items: [] })
        if (url.includes('/image')) return new Response(png, { headers: { 'Content-Type': 'image/png' } })
        const path = new URL(url).pathname
        if (/\/captures\/?$/.test(path)) return json({ items: [shot] })
        if (path.includes('/captures/')) return json(shot)
        return original(input, init)
      }
    })
    await page.reload()
    await page.getByTestId('downloader-page').waitFor()
    await page.getByTestId('nav-capture').click()
    await page.getByTestId('capture-filmstrip-item').first().click()
    await page.waitForFunction(() => document.querySelector('[data-testid="capture-tool-arrow"]')?.disabled === false)
    // nav-capture carries its native title only while the rail is collapsed (NavRail.tsx).
    await page.getByTestId('nav-collapse').click()
    await page.waitForFunction(() => !!document.querySelector('[data-testid="nav-capture"]')?.getAttribute('title'))

    for (const n of [1, 2, 3]) {
      if (n === 1) {
        await app.evaluate(({ BrowserWindow }) => {
          const w = BrowserWindow.getAllWindows()[0]
          w.show()
          w.focus()
          w.moveTop()
        })
        console.log('H1: win.show(); win.focus(); win.moveTop() applied')
      }
      if (n === 3) {
        const rg = spawnSync('rg', ['-n', 'appendSwitch|disable-features|tooltip', 'ui/src/main'], { cwd: repo, encoding: 'utf8' })
        const hits = (rg.stdout || '').trim()
        console.log(`H3: rg -n "appendSwitch|disable-features|tooltip" ui/src/main -> exit ${rg.status}`)
        console.log(hits ? hits : 'H3: no match (no Chromium switch or tooltip option in ui/src/main)')
      }
      for (const target of TARGETS) {
        const css = await page.getByTestId(target).evaluate((el) => {
          const r = el.getBoundingClientRect()
          return { x: r.x, y: r.y, width: r.width, height: r.height, title: el.getAttribute('title') ?? '' }
        })
        const geo = await app.evaluate(({ BrowserWindow, screen }, r) => {
          const w = BrowserWindow.getAllWindows()[0]
          const cb = w.getContentBounds()
          const zoom = w.webContents.getZoomFactor()
          const round = (b) => ({ x: Math.round(b.x), y: Math.round(b.y), width: Math.round(b.width), height: Math.round(b.height) })
          const win = round(screen.dipToScreenRect(w, cb))
          const rect = round(screen.dipToScreenRect(w, {
            x: cb.x + r.x * zoom, y: cb.y + r.y * zoom, width: r.width * zoom, height: r.height * zoom,
          }))
          return { win, rect }
        }, css)
        const cursor = { x: Math.round(geo.rect.x + geo.rect.width / 2), y: Math.round(geo.rect.y + geo.rect.height / 2) }
        const nudge = n === 2 ? { x: cursor.x + 3, y: cursor.y } : null
        const park = { x: geo.win.x + geo.win.width + 40, y: geo.win.y + geo.win.height + 40 }
        const png = `${out}/s34-probe-h${n}-${target}.png`.replace(/\\/g, '/')
        hoverAndCapture({ park, cursor, nudge, win: geo.win, png })
        const at = zoned()
        const sha256 = createHash('sha256').update(readFileSync(png)).digest('hex')
        const obs = {
          hypothesis: n, target, cursor: nudge ?? cursor, rect: geo.rect, window: geo.win, at, title: css.title, png, sha256,
        }
        observations.push(obs)
        console.log(`H${n} ${target}: cursor ${obs.cursor.x},${obs.cursor.y} rect ${JSON.stringify(geo.rect)} title ${JSON.stringify(css.title)} -> ${png} ${sha256}`)
      }
    }
  } finally {
    await app.close()
  }
  writeFileSync(runPath, JSON.stringify({ observations }, null, 2))
  console.log(`PROBE-DONE ${observations.map((o) => o.sha256).join(',')}`)
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
