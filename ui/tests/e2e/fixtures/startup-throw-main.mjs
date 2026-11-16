/* global process */
// AC-7 startup case: throws once during startup, after the -r watch loaded, and still opens a
// hidden window so firstWindow() resolves. It quits only when Playwright closes the app. Its
// profile and session storage live in the test's scratch AVKIT_APP_DATA; without one it exits
// before ready.
import { join } from 'node:path'
import { app, BrowserWindow } from 'electron'
const appData = process.env.AVKIT_APP_DATA
if (!appData) {
  process.stderr.write('startup-throw-main: AVKIT_APP_DATA is not set\n')
  process.exit(3)
}
app.setPath('userData', join(appData, 'user-data'))
app.setPath('sessionData', join(appData, 'session-data'))
process.nextTick(() => { throw new Error('avkit-e2e-startup-probe') })
app.whenReady().then(async () => { const win = new BrowserWindow({ show: false }); await win.loadURL('about:blank') })
app.on('window-all-closed', () => app.quit())
