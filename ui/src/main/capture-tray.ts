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
  const menu = Menu.buildFromTemplate([
    {
      label: 'Show window',
      click: () => {
        opts.window.show()
        opts.window.focus()
      },
    },
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
  // The dev-mode notification surface is a tray balloon, so the tray has to be reachable from
  // `notify-user.ts` before the first capture completes.
  registerNotifyTray(tray)
  return tray
}
