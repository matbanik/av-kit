// Session 97 probe app (task row 1; D-1245, D-1246): one window and one button styled the way
// Tailwind v4 compiles `hover:` (inside @media (hover: hover)). It loads no av-kit code and reads
// no app data. hover-probe.mjs and fidelity-probe.mjs launch it through ui's Playwright.
const { app, BrowserWindow } = require('electron')

const html = `<!doctype html><html><head><meta charset="utf-8"><style>
body { margin: 0; background: #fff; }
.b { margin: 40px; padding: 8px 16px; border: 0; background-color: rgb(21, 94, 117); color: #fff; }
@media (hover: hover) { .b:hover { background-color: rgb(22, 78, 99); } }
</style></head><body><button class="b" data-testid="b">Light</button></body></html>`

app.whenReady().then(() => {
  const win = new BrowserWindow({ width: 1280, height: 800, show: true, webPreferences: { sandbox: true } })
  win.loadURL('data:text/html;charset=utf-8,' + encodeURIComponent(html))
})
app.on('window-all-closed', () => app.quit())
