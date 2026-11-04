// Planning probe (Session 37 R-1): does Electron's Windows select popup paint option backgrounds?
const { app, BrowserWindow, desktopCapturer, screen } = require('electron')
const fs = require('fs')
const path = require('path')
const out = process.argv[process.argv.length - 1]
const html = `<!doctype html><body style="background:#1a1b26;margin:20px">
<select id="s" style="font-size:16px;background:#1a1a2e;color:#e0e0e0">
<option value="" style="background-color:#ffffff;color:#1e293b">Named</option>
<option style="background-color:#FF0000;color:#000000">red</option>
<option style="background-color:#FFA500;color:#000000">orange</option>
<option style="background-color:#FFFF00;color:#000000">yellow</option>
<option style="background-color:#008000;color:#FFFFFF">green</option>
<option style="background-color:#0000FF;color:#FFFFFF">blue</option>
<option style="background-color:#FFFFFF;color:#000000">white</option>
<option style="background-color:#000000;color:#FFFFFF">black</option>
</select></body>`
app.whenReady().then(async () => {
  const win = new BrowserWindow({ width: 420, height: 420, x: 80, y: 80, show: true })
  await win.loadURL('data:text/html;charset=utf-8,' + encodeURIComponent(html))
  win.focus()
  await new Promise((r) => setTimeout(r, 800))
  const rect = JSON.parse(await win.webContents.executeJavaScript('JSON.stringify(document.getElementById("s").getBoundingClientRect())'))
  const x = Math.round(rect.x + 10), y = Math.round(rect.y + rect.height / 2)
  win.webContents.sendInputEvent({ type: 'mouseDown', x, y, button: 'left', clickCount: 1 })
  win.webContents.sendInputEvent({ type: 'mouseUp', x, y, button: 'left', clickCount: 1 })
  await new Promise((r) => setTimeout(r, 1500))
  const d = screen.getPrimaryDisplay()
  const size = { width: Math.round(d.size.width * d.scaleFactor), height: Math.round(d.size.height * d.scaleFactor) }
  const sources = await desktopCapturer.getSources({ types: ['screen'], thumbnailSize: size })
  fs.writeFileSync(out, sources[0].thumbnail.toPNG())
  const b = win.getBounds()
  fs.writeFileSync(out + '.json', JSON.stringify({ bounds: b, scale: d.scaleFactor, rect, electron: process.versions.electron, chrome: process.versions.chrome }))
  app.quit()
})
