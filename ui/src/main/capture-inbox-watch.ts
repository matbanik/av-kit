import fs from 'node:fs'
import { basename } from 'node:path'

import type { BrowserWindow } from 'electron'

/**
 * Inbox change notification (MEU-40, AC-40.30 d–h).
 *
 * `fs.watch` on Windows is a hint, not a contract: it coalesces, it fires more than once for a
 * single file, and it frequently delivers `filename === null`. Deciding from the *event* therefore
 * either double-announces a capture or misses one entirely. So every event is treated as nothing
 * more than "something moved" — the handler rescans the directory and the decision is made by
 * comparing three sets:
 *
 *   current   — the names on disk right now
 *   lastEmitted — the names the renderer has already been told about
 *   reserved  — names this process is mid-publication on (claimed but not yet announced)
 *
 * The reservation is what keeps the watcher quiet while `linkSync` + `POST /captures` are still in
 * flight: the publisher announces the file itself, exactly once, when it has finished.
 */

/** Prefix of the temp file the sidecar writes into before it is claimed into the inbox. */
export const STAGING_PREFIX = '.avkit-staging-'

const ANNOTATED_SUFFIX = 'annotated.png'

let watcher: fs.FSWatcher | null = null
let rescanInFlight = false
let rescanQueued = false

let lastEmitted = new Set<string>()
const reserved = new Set<string>()

/** Only finished, un-annotated capture PNGs are worth telling the renderer about. */
export function shouldNotifyInboxChange(name: string): boolean {
  if (name.length === 0) {
    return false
  }
  if (name.startsWith(STAGING_PREFIX)) {
    return false
  }
  if (!name.toLowerCase().endsWith('.png')) {
    return false
  }
  return !name.toLowerCase().endsWith(ANNOTATED_SUFFIX)
}

export type InboxNotificationInput = {
  current: readonly string[]
  lastEmitted: ReadonlySet<string>
  reserved: ReadonlySet<string>
}

export type InboxNotificationDecision = {
  notify: boolean
  nextEmitted: Set<string>
}

/**
 * The whole decision, as a pure function of the three sets, so it can be reasoned about and
 * tested without a filesystem, a window, or a watcher.
 */
export function computeInboxNotification(input: InboxNotificationInput): InboxNotificationDecision {
  const eligible = input.current
    .filter((name) => shouldNotifyInboxChange(name))
    .filter((name) => !input.reserved.has(name))
  const nextEmitted = new Set(eligible)
  const notify = eligible.some((name) => !input.lastEmitted.has(name))
  return { notify, nextEmitted }
}

/** Applies a fresh directory listing to the module state and reports whether to announce. */
export function onInboxListing(names: readonly string[]): boolean {
  const decision = computeInboxNotification({ current: names, lastEmitted, reserved })
  lastEmitted = decision.nextEmitted
  return decision.notify
}

/**
 * Adopts a listing as already-announced. Used when the watcher starts over a non-empty inbox, so
 * the files that were there before av-kit launched do not all arrive as "new".
 */
export function seedInboxBaseline(names: readonly string[]): void {
  lastEmitted = new Set(names.filter((name) => shouldNotifyInboxChange(name)))
}

/** Suppresses `fullPath` until the publisher settles or releases it. */
export function reserveInboxPath(fullPath: string): void {
  reserved.add(basename(fullPath))
}

/**
 * Gives up a reservation without announcing it — the name was contested (`EEXIST`) or the
 * publication failed, so the watcher must be free to notice it again.
 */
export function releaseInboxPath(fullPath: string): void {
  reserved.delete(basename(fullPath))
}

/** Publication finished: the name is announced by the publisher, so the watcher must not repeat it. */
export function settleInboxPath(fullPath: string): void {
  const name = basename(fullPath)
  reserved.delete(name)
  lastEmitted.add(name)
}

export function resetInboxWatchState(): void {
  lastEmitted = new Set<string>()
  reserved.clear()
  rescanInFlight = false
  rescanQueued = false
}

function listInbox(inboxDir: string): string[] {
  try {
    return fs.readdirSync(inboxDir)
  } catch {
    // The inbox can be renamed or removed while the watcher is alive; an unreadable directory
    // simply has nothing new to announce.
    return []
  }
}

/**
 * Rescans and announces at most once per settled listing. Overlapping events collapse into a
 * single trailing rescan so a burst never produces a burst of IPC.
 */
function rescan(inboxDir: string, window: BrowserWindow): void {
  if (rescanInFlight) {
    rescanQueued = true
    return
  }
  rescanInFlight = true
  try {
    do {
      rescanQueued = false
      if (onInboxListing(listInbox(inboxDir))) {
        notifyInboxChanged(window)
      }
    } while (rescanQueued)
  } finally {
    rescanInFlight = false
    rescanQueued = false
  }
}

export function startInboxWatch(inboxDir: string, window: BrowserWindow): void {
  stopInboxWatch()
  seedInboxBaseline(listInbox(inboxDir))
  try {
    watcher = fs.watch(inboxDir, { persistent: true }, () => {
      // The event's `filename` is deliberately ignored: it is `null` often enough on Windows that
      // trusting it would drop announcements. The rescan below is the source of truth.
      rescan(inboxDir, window)
    })
  } catch {
    // A missing inbox directory must not take the app down; the settings poll re-arms the watcher
    // as soon as a readable directory is configured.
    watcher = null
  }
}

export function stopInboxWatch(): void {
  watcher?.close()
  watcher = null
}

export function notifyInboxChanged(window: BrowserWindow): void {
  if (!window.isDestroyed()) {
    window.webContents.send('captures:inbox-changed')
  }
}
