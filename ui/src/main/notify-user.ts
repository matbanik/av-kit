import { app, dialog, Notification, shell, type Tray } from 'electron'

import { appendStdoutLog } from './ipc'

/**
 * The single route for "the user needs to be told something about a capture" (MEU-40, AC-40.30).
 *
 * Windows toast notifications are only delivered to a process with a Start Menu shortcut
 * identity: an unpackaged `electron-vite dev` run has none, so `new Notification(...)` there is
 * silently swallowed by the OS and the user is told nothing at all. That is why the branch below
 * is on `app.isPackaged` and not on a preference — packaged uses the AUMID + toast, and a dev run
 * uses the tray balloon, falling back to a parentless dialog when the tray does not exist yet.
 *
 * Every branch logs first, so the console receipt is complete even when the visible surface is
 * suppressed (E2E) or unavailable.
 */

/** Must match `appId` in `ui/electron-builder.yml` — the toast is discarded without it. */
export const NOTIFY_APP_USER_MODEL_ID = 'com.avkit.app'

export type Notice = {
  title: string
  body: string
  /** The capture this notice is about; absent when the failure produced no file to point at. */
  path?: string
}

export type NotifyDeps = {
  log: (line: string) => void
  /** Packaged branch. */
  toast: (notice: Notice) => void
  /** Unpackaged branch; `false` means the tray could not show it. */
  balloon: (notice: Notice) => boolean
  /** Last resort when no tray exists yet. */
  dialog: (notice: Notice) => void
}

let tray: Tray | null = null

/** `capture-tray.ts` hands its tray over so the balloon branch has somewhere to land. */
export function registerNotifyTray(next: Tray | null): void {
  tray = next
}

function defaultLog(line: string): void {
  appendStdoutLog(line)
}

function defaultToast(notice: Notice): void {
  app.setAppUserModelId(NOTIFY_APP_USER_MODEL_ID)
  const toast = new Notification({ title: notice.title, body: notice.body })
  const path = notice.path
  if (path !== undefined) {
    toast.on('click', () => {
      shell.showItemInFolder(path)
    })
  }
  toast.show()
}

function defaultBalloon(notice: Notice): boolean {
  if (tray === null) {
    return false
  }
  tray.displayBalloon({ title: notice.title, content: notice.body })
  return true
}

function defaultDialog(notice: Notice): void {
  void dialog.showMessageBox({
    type: 'info',
    title: notice.title,
    message: notice.title,
    detail: notice.path === undefined ? notice.body : `${notice.body}\n${notice.path}`,
  })
}

const defaults: NotifyDeps = {
  log: defaultLog,
  toast: defaultToast,
  balloon: defaultBalloon,
  dialog: defaultDialog,
}

let deps: NotifyDeps = { ...defaults }

/** Replaces some or all of the OS surfaces; anything omitted keeps the production behaviour. */
export function setNotifyUserDeps(overrides: Partial<NotifyDeps>): void {
  deps = { ...deps, ...overrides }
}

export function resetNotifyUserDeps(): void {
  deps = { ...defaults }
}

export function notifyUser(notice: Notice): void {
  deps.log(
    `[Capture] notify ${notice.title}: ${notice.body}${notice.path === undefined ? '' : ` (${notice.path})`}`,
  )
  if (process.env.AVKIT_E2E === '1') {
    return
  }
  if (app.isPackaged) {
    deps.toast(notice)
    return
  }
  if (!deps.balloon(notice)) {
    deps.dialog(notice)
  }
}
