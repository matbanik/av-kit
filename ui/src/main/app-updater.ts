// The installed app's update controller (Session 106, MEU-174): UPDATER_CONFIG, UPDATE_TICK,
// UPDATE_STATE, UPDATE_QUIET_FAILURE, UPDATE_NOTICE_ONCE, UPDATE_INSTALL_ORDER and the
// UPDATE_E2E_SEAM's pure half. The library, the clock, the timers, the store and every effect
// come in through `deps`; the wiring in `index.ts` passes `electronUpdater.autoUpdater`.
import { isCheckDue, isUpdateInterval } from './update-schedule'

export type UpdateStateName = 'disabled' | 'idle' | 'checking' | 'downloading' | 'ready' | 'error'
export type UpdateErrorKind = 'network' | 'checksum' | 'other'
export type UpdateResult = 'up-to-date' | 'update-found' | 'error'

export type UpdateState = {
  state: UpdateStateName
  currentVersion: string
  availableVersion: string | null
  percent: number | null
  lastCheckAt: number | null
  lastResult: UpdateResult | null
  errorKind: UpdateErrorKind | null
}

export type InstallResult = { ok: true } | { ok: false; reason: 'not-ready' }

/** The part of electron-updater's `AppUpdater` the controller touches. */
export type UpdaterLike = {
  allowPrerelease: boolean
  allowDowngrade: boolean
  autoDownload: boolean
  autoInstallOnAppQuit: boolean
  forceDevUpdateConfig?: boolean
  updateConfigPath?: string | null
  on(event: string, listener: (...args: never[]) => void): unknown
  checkForUpdates(): Promise<unknown>
  quitAndInstall(isSilent?: boolean, isForceRunAfter?: boolean): void
}

export type UpdateStoreLike = {
  get(key: string): unknown
  set(key: string, value: unknown): void
  delete?(key: string): void
}

export type UpdateTimers = {
  setTimeout(fn: () => void, ms: number): unknown
  clearTimeout(handle: unknown): void
  setInterval(fn: () => void, ms: number): unknown
  clearInterval(handle: unknown): void
}

export type UpdateSeam = { feedPath: string; firstTickMs: number; tickMs: number }

export type AppUpdaterDeps = {
  updater: UpdaterLike
  isPackaged: boolean
  seam: UpdateSeam | null
  currentVersion: string
  now: () => number
  timers: UpdateTimers
  openStore: () => UpdateStoreLike
  readInterval: () => Promise<string>
  notify: (notice: { title: string; body: string }) => void
  log: (line: string) => void
  shutdownBackend: () => Promise<void>
  setQuitIntent: () => void
  emitState: (state: UpdateState) => void
}

export type AppUpdaterController = {
  start(): void
  stop(): void
  check(): Promise<UpdateState>
  install(): Promise<InstallResult>
  getState(): UpdateState
}

export const FIRST_TICK_MS = 60_000
export const TICK_MS = 60 * 60_000
export const E2E_FIRST_TICK_MS = 500
export const E2E_TICK_MS = 1000

const RESULTS: readonly UpdateResult[] = ['up-to-date', 'update-found', 'error']

/** UPDATE_E2E_SEAM: on only with AVKIT_E2E=1 and a feed file; otherwise neither variable is read. */
export function updateSeam(
  env: Record<string, string | undefined>,
  exists: (path: string) => boolean,
): UpdateSeam | null {
  if (env.AVKIT_E2E !== '1') {
    return null
  }
  const feedPath = env.AVKIT_E2E_UPDATE_FEED
  if (feedPath === undefined || feedPath.trim() === '' || !exists(feedPath)) {
    return null
  }
  const tick = Number.parseInt(env.AVKIT_E2E_UPDATE_TICK_MS ?? '', 10)
  return {
    feedPath,
    firstTickMs: E2E_FIRST_TICK_MS,
    tickMs: Number.isFinite(tick) && tick > 0 ? tick : E2E_TICK_MS,
  }
}

/** UPDATE_STATE's errorKind, from the message (and the library's error code) only. */
export function updateErrorKind(err: unknown): UpdateErrorKind {
  const message = err instanceof Error ? err.message : String(err)
  const fields = (typeof err === 'object' && err !== null ? err : {}) as { code?: unknown; statusCode?: unknown }
  if (fields.code === 'ERR_CHECKSUM_MISMATCH' || /ERR_CHECKSUM_MISMATCH|sha512 checksum mismatch/i.test(message)) {
    return 'checksum'
  }
  if (
    typeof fields.statusCode === 'number' ||
    /net::|ENOTFOUND|ETIMEDOUT|ECONNREFUSED|ECONNRESET|EAI_AGAIN|HttpError|\bstatus(?:Code)?[ =:]+\d{3}\b/.test(message)
  ) {
    return 'network'
  }
  return 'other'
}

// The store's constructor and each read are guarded: a store that cannot be opened or parsed is
// read as empty, and the controller keeps its own copy so it still works from that state.
function guardedStore(open: () => UpdateStoreLike): Required<UpdateStoreLike> {
  let store: UpdateStoreLike | null = null
  try {
    store = open()
  } catch {
    store = null
  }
  const memory: Record<string, unknown> = {}
  return {
    get(key) {
      if (store !== null) {
        try {
          return store.get(key)
        } catch {
          return memory[key]
        }
      }
      return memory[key]
    },
    set(key, value) {
      memory[key] = value
      try {
        store?.set(key, value)
      } catch {
        // the memory copy stands in
      }
    },
    delete(key) {
      delete memory[key]
      try {
        if (store?.delete !== undefined) {
          store.delete(key)
        } else {
          store?.set(key, null)
        }
      } catch {
        // the memory copy stands in
      }
    },
  }
}

function versionOf(info: unknown): string | null {
  const version = (typeof info === 'object' && info !== null ? info : {}) as { version?: unknown }
  return typeof version.version === 'string' ? version.version : null
}

export const NIL_STAGING_ID = '00000000-0000-0000-0000-000000000000'

type UpdaterInternals = {
  logger: unknown
  stagingUserIdPromise: { readonly value: Promise<string> }
  computeFinalHeaders?: (headers: Record<string, string>) => Record<string, string>
}

/**
 * UPDATER_CONFIG's no-identifier and quiet-library parts (D-1591, D-1592). These reach
 * electron-updater 6.8.11 internals, `out/AppUpdater.js`; re-check the lines when it moves.
 * - :189 makes `stagingUserIdPromise` a Lazy over getOrCreateStagingUserId (:501-525), which
 *   writes `userData/.updaterId`. Here it is a lazy nil UUID, so that file is never written.
 * - :386-387 sends that id as `x-user-staging-id` through computeFinalHeaders (:333). The wrap
 *   deletes the header before the library's own merge, so no request carries it.
 * - :65-66 maps a null logger to its NoOpLogger, which also quiets the constructor's raw
 *   `error` listener (:201-202); the controller's sanitized line is the only log output.
 */
export function hardenUpdater(updater: UpdaterLike): void {
  const internals = updater as unknown as UpdaterInternals
  internals.logger = null
  internals.stagingUserIdPromise = {
    get value() {
      return Promise.resolve(NIL_STAGING_ID)
    },
  }
  const merge = internals.computeFinalHeaders
  if (typeof merge === 'function') {
    internals.computeFinalHeaders = (headers) => {
      delete headers['x-user-staging-id']
      return merge.call(updater, headers)
    }
  }
}

export function createAppUpdater(deps: AppUpdaterDeps): AppUpdaterController {
  const { updater, timers } = deps
  hardenUpdater(updater)
  // UPDATER_CONFIG: the four values, and never setFeedURL (the feed is the build's app-update.yml).
  updater.allowPrerelease = false
  updater.allowDowngrade = false
  updater.autoDownload = true
  updater.autoInstallOnAppQuit = false
  if (deps.seam !== null) {
    updater.updateConfigPath = deps.seam.feedPath
    updater.forceDevUpdateConfig = true
  }
  const enabled = deps.isPackaged || deps.seam !== null
  const store = guardedStore(deps.openStore)
  const readTime = (key: string): number | null => {
    const value = store.get(key)
    return typeof value === 'number' && Number.isFinite(value) ? value : null
  }
  const readText = (key: string): string | null => {
    const value = store.get(key)
    return typeof value === 'string' ? value : null
  }
  const readResult = (): UpdateResult | null => {
    const value = store.get('lastResult')
    return (RESULTS as readonly unknown[]).includes(value) ? (value as UpdateResult) : null
  }

  let state: UpdateState = {
    state: enabled ? 'idle' : 'disabled',
    currentVersion: deps.currentVersion,
    availableVersion: null,
    percent: null,
    lastCheckAt: readTime('lastCheckAt'),
    lastResult: readResult(),
    errorKind: null,
  }
  let recoveryDone = false
  let inFlight = false
  let failureLogged = false
  let installing = false
  let started = false
  let firstTimer: unknown = null
  let tickTimer: unknown = null

  const getState = (): UpdateState => ({ ...state })
  const change = (patch: Partial<UpdateState>): void => {
    state = { ...state, ...patch }
    try {
      deps.emitState(getState())
    } catch {
      // a window that is gone does not stop the controller
    }
  }
  const busy = (): boolean => inFlight || installing || state.state === 'checking' || state.state === 'downloading'

  // UPDATE_QUIET_FAILURE: one log line per check, the state, and nothing the user sees.
  const fail = (err: unknown): void => {
    const kind = updateErrorKind(err)
    store.set('lastAttemptAt', deps.now())
    store.set('lastResult', 'error')
    if (!failureLogged) {
      failureLogged = true
      deps.log(`update: check failed kind=${kind}`)
    }
    change({ state: 'error', errorKind: kind, lastResult: 'error', percent: null })
  }

  const on = (event: string, listener: (...args: unknown[]) => void): void => {
    updater.on(event, ((...args: unknown[]) => {
      try {
        listener(...args)
      } catch {
        // no listener error leaves the controller
      }
    }) as (...args: never[]) => void)
  }

  if (enabled) {
    on('checking-for-update', () => {
      change({ state: 'checking', errorKind: null })
    })
    on('update-available', (info) => {
      const version = versionOf(info)
      if (version !== null) {
        store.set('pendingVersion', version)
      }
      change({ state: 'downloading', availableVersion: version, percent: null, errorKind: null })
    })
    on('download-progress', (progress) => {
      const percent = (typeof progress === 'object' && progress !== null ? progress : {}) as { percent?: unknown }
      change({ state: 'downloading', percent: typeof percent.percent === 'number' ? percent.percent : null })
    })
    on('update-not-available', () => {
      const now = deps.now()
      store.set('lastCheckAt', now)
      store.set('lastAttemptAt', now)
      store.set('lastResult', 'up-to-date')
      store.delete('pendingVersion')
      change({
        state: 'idle',
        availableVersion: null,
        percent: null,
        lastCheckAt: now,
        lastResult: 'up-to-date',
        errorKind: null,
      })
    })
    on('update-downloaded', (info) => {
      const now = deps.now()
      const version = versionOf(info) ?? state.availableVersion
      store.set('lastCheckAt', now)
      store.set('lastAttemptAt', now)
      store.set('lastResult', 'update-found')
      if (version !== null) {
        store.set('pendingVersion', version)
      }
      change({
        state: 'ready',
        availableVersion: version,
        percent: 100,
        lastCheckAt: now,
        lastResult: 'update-found',
        errorKind: null,
      })
      // UPDATE_NOTICE_ONCE
      if (version !== null && readText('notifiedVersion') !== version) {
        store.set('notifiedVersion', version)
        deps.notify({
          title: 'av-kit update ready',
          body: `Version ${version} is downloaded. Open Settings, Updates, and choose Restart and update.`,
        })
      }
    })
    on('error', (err) => {
      fail(err)
    })
  }

  const runCheck = async (): Promise<void> => {
    inFlight = true
    recoveryDone = true
    failureLogged = false
    try {
      const result = await updater.checkForUpdates()
      // The library's download promise rejects too when the download fails; its `error` event
      // has already been handled, so the rejection stops here.
      const download = (typeof result === 'object' && result !== null ? result : {}) as { downloadPromise?: unknown }
      if (download.downloadPromise instanceof Promise) {
        download.downloadPromise.catch(() => undefined)
      }
    } catch (err: unknown) {
      fail(err)
    } finally {
      inFlight = false
    }
  }

  // UPDATE_TICK: read the interval, then check once when due and nothing runs.
  const tick = async (): Promise<void> => {
    try {
      let interval: string
      try {
        interval = await deps.readInterval()
      } catch {
        deps.log('update: interval unavailable')
        return
      }
      if (!isUpdateInterval(interval)) {
        deps.log('update: interval unavailable')
        return
      }
      if (busy()) {
        return
      }
      const due = isCheckDue({
        now: deps.now(),
        interval,
        lastCheckAt: readTime('lastCheckAt'),
        lastAttemptAt: readTime('lastAttemptAt'),
        pendingVersion: readText('pendingVersion'),
        recoveryDone,
      })
      if (due) {
        void runCheck()
      }
    } catch {
      // no tick error leaves the controller
    }
  }

  return {
    start() {
      if (!enabled || started) {
        return
      }
      started = true
      const every = deps.seam?.tickMs ?? TICK_MS
      firstTimer = timers.setTimeout(() => {
        firstTimer = null
        void tick()
        tickTimer = timers.setInterval(() => {
          void tick()
        }, every)
      }, deps.seam?.firstTickMs ?? FIRST_TICK_MS)
    },
    stop() {
      if (firstTimer !== null) {
        timers.clearTimeout(firstTimer)
        firstTimer = null
      }
      if (tickTimer !== null) {
        timers.clearInterval(tickTimer)
        tickTimer = null
      }
    },
    // UPDATE_IPC `update-check`: one check now, whatever the interval says (D-1548).
    async check() {
      if (enabled && !busy()) {
        await runCheck()
      }
      return getState()
    },
    // UPDATE_INSTALL_ORDER: the only caller of quitAndInstall.
    async install() {
      if (state.state !== 'ready' || installing) {
        return { ok: false, reason: 'not-ready' }
      }
      installing = true
      deps.log(`update: install requested version=${state.availableVersion ?? ''}`)
      deps.setQuitIntent()
      try {
        await deps.shutdownBackend()
        deps.log('update: backend stopped')
      } catch {
        deps.log('update: backend stop failed')
      }
      updater.quitAndInstall(true, true)
      return { ok: true }
    },
    getState,
  }
}
