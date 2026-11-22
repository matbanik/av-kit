import { app, Menu, shell, Tray, type BrowserWindow } from 'electron'

import { trayIconImage } from './app-icon'
import { isQuitting, setQuitIntent } from './capture-quit'
import { registerNotifyTray } from './notify-user'

export function startCaptureTray(opts: {
  window: BrowserWindow
  onRegion: () => void
  inboxDir: () => string
}): Tray {
  const tray = new Tray(trayIconImage())
  tray.setToolTip('av-kit')
  // Show window and a double-click on the icon run this one function (MEU-164). A minimized window
  // is restored first, as a second launch of the app already does.
  const showWindow = (): void => {
    if (opts.window.isMinimized()) {
      opts.window.restore()
    }
    opts.window.show()
    opts.window.focus()
  }
  const menu = Menu.buildFromTemplate([
    { label: 'Show window', click: showWindow },
    {
      label: 'Capture region',
      click: () => {
        opts.onRegion()
      },
    },
    {
      label: 'Open inbox folder',
      click: () => {
        shell.showItemInFolder(opts.inboxDir())
      },
    },
    {
      label: 'Quit',
      click: () => {
        setQuitIntent()
        if (isQuitting) {
          app.quit()
        }
      },
    },
  ])
  tray.setContextMenu(menu)
  tray.on('double-click', showWindow)
  // Playwright drives the tray through app.evaluate. Only a launch with AVKIT_E2E=1 exposes it.
  if (process.env.AVKIT_E2E === '1') {
    const trayGlobal = globalThis as { __AVKIT_E2E_TRAY__?: { tray: Tray; menu: Menu } }
    trayGlobal.__AVKIT_E2E_TRAY__ = { tray, menu }
  }
  // The dev-mode notification surface is a tray balloon, so the tray has to be reachable from
  // `notify-user.ts` before the first capture completes.
  registerNotifyTray(tray)
  return tray
}
