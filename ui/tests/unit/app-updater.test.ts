// Session 106 (MEU-174) the update controller, AC-174.2 to AC-174.7: UPDATE_TICK, UPDATER_CONFIG,
// UPDATE_STATE, UPDATE_QUIET_FAILURE, UPDATE_NOTICE_ONCE and UPDATE_INSTALL_ORDER. The library is
// a hand-written mock that records property writes and calls; the store is a memory store; the
// clock and the timers are Vitest's fake ones. The module is loaded by a dynamic import inside
// each test, so before Green every case fails by assertion.
// Corrections round 1 (F1 D-1591, F2 D-1592) add the last block: the controller over the real
// electron-updater NsisUpdater and GitHub provider, with only the HTTP executor replaced by an
// in-memory one, so no request leaves the process; each start is a new updater and controller on
// one scratch userData folder.
import { existsSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { NsisUpdater } from 'electron-updater'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const electronMocks = vi.hoisted(() => ({
  showMessageBox: vi.fn(),
  showMessageBoxSync: vi.fn(),
  showErrorBox: vi.fn(),
  BrowserWindow: vi.fn(),
  Notification: vi.fn(),
}))

vi.mock('electron', () => ({
  dialog: {
    showMessageBox: electronMocks.showMessageBox,
    showMessageBoxSync: electronMocks.showMessageBoxSync,
    showErrorBox: electronMocks.showErrorBox,
  },
  BrowserWindow: electronMocks.BrowserWindow,
  Notification: electronMocks.Notification,
}))

const MODULE = '../../src/main/app-updater'
const SECOND = 1000
const MINUTE = 60 * SECOND
const HOUR = 60 * MINUTE
const DAY = 24 * HOUR
const T0 = Date.UTC(2026, 10, 27, 12, 0, 0)
const STORE_KEYS = ['lastCheckAt', 'lastAttemptAt', 'lastResult', 'pendingVersion', 'notifiedVersion']
const NOTICE = {
  title: 'av-kit update ready',
  body: 'Version 2.0.0 is downloaded. Open Settings, Updates, and choose Restart and update.',
}

type UpdateState = {
  state: 'disabled' | 'idle' | 'checking' | 'downloading' | 'ready' | 'error'
  currentVersion: string
  availableVersion: string | null
  percent: number | null
  lastCheckAt: number | null
  lastResult: 'up-to-date' | 'update-found' | 'error' | null
  errorKind: 'network' | 'checksum' | 'other' | null
}
type InstallResult = { ok: true } | { ok: false; reason: 'not-ready' }
type Controller = {
  start(): void
  stop(): void
  check(): Promise<UpdateState>
  install(): Promise<InstallResult>
  getState(): UpdateState
}
type StoreLike = { get(key: string): unknown; set(key: string, value: unknown): void; delete(key: string): void }
type Seam = { feedPath: string; firstTickMs: number; tickMs: number }
type Mod = {
  createAppUpdater: (deps: Record<string, unknown>) => Controller
  updateSeam: (env: Record<string, string | undefined>, exists: (path: string) => boolean) => Seam | null
}

async function load(): Promise<Mod> {
  const mod = (await import(MODULE).catch(() => ({}))) as Record<string, unknown>
  expect(typeof mod.createAppUpdater, 'app-updater exports createAppUpdater').toBe('function')
  expect(typeof mod.updateSeam, 'app-updater exports updateSeam').toBe('function')
  return mod as unknown as Mod
}

type Listener = (...args: unknown[]) => void

function makeUpdater() {
  const listeners = new Map<string, Listener[]>()
  const writes: Array<[string, unknown]> = []
  const calls = { checkForUpdates: 0, setFeedURL: 0, quitAndInstall: [] as unknown[][] }
  const emit = (event: string, ...args: unknown[]) => {
    for (const fn of listeners.get(event) ?? []) fn(...args)
  }
  // What one checkForUpdates() call does; the default never settles (a check that runs).
  let onCheck: () => Promise<unknown> = () => new Promise(() => undefined)
  const target: Record<string, unknown> = {
    // The opposite of what UPDATER_CONFIG asks, so each value must be written.
    allowPrerelease: true,
    allowDowngrade: true,
    autoDownload: false,
    autoInstallOnAppQuit: true,
    on(event: string, fn: Listener) {
      listeners.set(event, [...(listeners.get(event) ?? []), fn])
      return proxy
    },
    checkForUpdates() {
      calls.checkForUpdates++
      return onCheck()
    },
    setFeedURL() {
      calls.setFeedURL++
    },
    quitAndInstall(...args: unknown[]) {
      calls.quitAndInstall.push(args)
      order.push(`quitAndInstall(${args.join(',')})`)
    },
  }
  const order: string[] = []
  const proxy: Record<string, unknown> = new Proxy(target, {
    set(t, key, value) {
      writes.push([String(key), value])
      t[String(key)] = value
      return true
    },
  })
  return {
    updater: proxy,
    writes,
    calls,
    emit,
    order,
    setCheck(fn: () => Promise<unknown>) {
      onCheck = fn
    },
  }
}

function memoryStore(init: Record<string, unknown> = {}) {
  const data: Record<string, unknown> = { ...init }
  const store: StoreLike & { data: Record<string, unknown> } = {
    data,
    get: (key) => data[key],
    set: (key, value) => {
      data[key] = value
    },
    delete: (key) => {
      delete data[key]
    },
  }
  return store
}

type Setup = {
  isPackaged?: boolean
  seam?: Seam | null
  interval?: () => Promise<string>
  openStore?: () => StoreLike
  store?: ReturnType<typeof memoryStore>
  shutdownBackend?: () => Promise<void>
}

function setup(mod: Mod, over: Setup = {}) {
  const u = makeUpdater()
  const store = over.store ?? memoryStore()
  const logs: string[] = []
  const notices: unknown[] = []
  const emitted: UpdateState[] = []
  const reads = { count: 0 }
  const timerCalls = { count: 0 }
  const timers = {
    setTimeout: (fn: () => void, ms: number) => {
      timerCalls.count++
      return setTimeout(fn, ms)
    },
    clearTimeout: (handle: unknown) => clearTimeout(handle as ReturnType<typeof setTimeout>),
    setInterval: (fn: () => void, ms: number) => {
      timerCalls.count++
      return setInterval(fn, ms)
    },
    clearInterval: (handle: unknown) => clearInterval(handle as ReturnType<typeof setInterval>),
  }
  const interval = over.interval ?? (async () => 'weekly')
  const ctl = mod.createAppUpdater({
    updater: u.updater,
    isPackaged: over.isPackaged ?? true,
    seam: over.seam ?? null,
    currentVersion: '1.0.0',
    now: () => Date.now(),
    timers,
    openStore: over.openStore ?? (() => store),
    readInterval: () => {
      reads.count++
      return interval()
    },
    notify: (n: unknown) => {
      notices.push(n)
    },
    log: (line: string) => {
      logs.push(line)
      u.order.push(`log:${line}`)
    },
    shutdownBackend:
      over.shutdownBackend ??
      (async () => {
        await Promise.resolve()
        u.order.push('shutdownBackend resolved')
      }),
    setQuitIntent: () => {
      u.order.push('setQuitIntent')
    },
    emitState: (s: UpdateState) => {
      emitted.push({ ...s })
    },
  })
  return { ctl, u, store, logs, notices, emitted, reads, timerCalls }
}

async function flush(): Promise<void> {
  await vi.advanceTimersByTimeAsync(0)
}

const unhandled: unknown[] = []
const onUnhandled = (reason: unknown) => {
  unhandled.push(reason)
}

beforeEach(() => {
  vi.useFakeTimers({ toFake: ['setTimeout', 'clearTimeout', 'setInterval', 'clearInterval', 'Date'] })
  vi.setSystemTime(T0)
  unhandled.length = 0
  process.on('unhandledRejection', onUnhandled)
  for (const fn of Object.values(electronMocks)) fn.mockClear()
})

afterEach(() => {
  process.off('unhandledRejection', onUnhandled)
  vi.useRealTimers()
})

describe('MEU-174 UPDATE_TICK', () => {
  it('AC-174.2 a packaged controller checks once at the first tick and never twice while the check runs', async () => {
    const mod = await load()
    const { ctl, u } = setup(mod)
    ctl.start()
    await vi.advanceTimersByTimeAsync(MINUTE - 1)
    expect(u.calls.checkForUpdates, 'before the first tick').toBe(0)
    await vi.advanceTimersByTimeAsync(1)
    expect(u.calls.checkForUpdates, 'the first tick, 60 s after start').toBe(1)
    await vi.advanceTimersByTimeAsync(10 * DAY)
    expect(u.calls.checkForUpdates, 'the check never settles').toBe(1)
    ctl.stop()
  })

  it('AC-174.2 a running download keeps the later ticks from checking again', async () => {
    const mod = await load()
    const { ctl, u } = setup(mod)
    u.setCheck(async () => {
      u.emit('checking-for-update')
      u.emit('update-available', { version: '2.0.0' })
      return { updateInfo: { version: '2.0.0' } }
    })
    ctl.start()
    await vi.advanceTimersByTimeAsync(MINUTE)
    expect(u.calls.checkForUpdates).toBe(1)
    expect(ctl.getState().state).toBe('downloading')
    await vi.advanceTimersByTimeAsync(30 * DAY)
    expect(u.calls.checkForUpdates).toBe(1)
    ctl.stop()
  })

  it('AC-174.2 the interval is read at each tick, so a change in Settings applies with no restart', async () => {
    const mod = await load()
    let saved = 'never'
    const { ctl, u, reads } = setup(mod, { interval: async () => saved })
    ctl.start()
    await vi.advanceTimersByTimeAsync(MINUTE)
    expect(reads.count).toBe(1)
    expect(u.calls.checkForUpdates).toBe(0)
    saved = 'weekly'
    await vi.advanceTimersByTimeAsync(HOUR)
    expect(reads.count).toBe(2)
    expect(u.calls.checkForUpdates).toBe(1)
    ctl.stop()
  })

  it('AC-174.2 [neg] a development run (not packaged, no seam) starts no timer and never checks', async () => {
    const mod = await load()
    const { ctl, u, timerCalls, reads } = setup(mod, { isPackaged: false })
    ctl.start()
    await vi.advanceTimersByTimeAsync(60 * DAY)
    expect(u.calls.checkForUpdates).toBe(0)
    expect(timerCalls.count).toBe(0)
    expect(reads.count).toBe(0)
    expect(ctl.getState().state).toBe('disabled')
    expect((await ctl.check()).state).toBe('disabled')
    expect(u.calls.checkForUpdates).toBe(0)
    ctl.stop()
  })

  it.each([
    ['rejects', async () => Promise.reject(new Error('connect ECONNREFUSED 127.0.0.1:1'))],
    ['answers daily', async () => 'daily'],
  ])('AC-174.2 [neg] a readInterval that %s skips every tick with one log line each', async (_name, interval) => {
    const mod = await load()
    const { ctl, u, logs, reads, store, emitted } = setup(mod, { interval })
    ctl.start()
    await vi.advanceTimersByTimeAsync(60 * DAY)
    expect(u.calls.checkForUpdates).toBe(0)
    expect(reads.count).toBeGreaterThanOrEqual(1439)
    expect(reads.count).toBeLessThanOrEqual(1441)
    expect(logs.filter((l) => l === 'update: interval unavailable')).toHaveLength(reads.count)
    expect(store.data, 'no store write').toEqual({})
    expect(emitted, 'no state change').toEqual([])
    expect(ctl.getState().state).toBe('idle')
    ctl.stop()
  })

  it('AC-174.2 [neg] a saved never gives no check over 60 days', async () => {
    const mod = await load()
    const { ctl, u, reads } = setup(mod, { interval: async () => 'never' })
    ctl.start()
    await vi.advanceTimersByTimeAsync(60 * DAY)
    expect(reads.count).toBeGreaterThan(1000)
    expect(u.calls.checkForUpdates).toBe(0)
    ctl.stop()
  })

  it('AC-174.2 [neg] a found version that waits is checked at the first tick, with no second notice and no later check', async () => {
    const mod = await load()
    const store = memoryStore({
      pendingVersion: '2.0.0',
      notifiedVersion: '2.0.0',
      lastResult: 'update-found',
      lastCheckAt: T0 - HOUR,
      lastAttemptAt: T0 - HOUR,
    })
    const { ctl, u, notices } = setup(mod, { store })
    u.setCheck(async () => {
      u.emit('checking-for-update')
      u.emit('update-available', { version: '2.0.0' })
      u.emit('update-downloaded', { version: '2.0.0' })
      return { updateInfo: { version: '2.0.0' } }
    })
    ctl.start()
    await vi.advanceTimersByTimeAsync(MINUTE)
    expect(u.calls.checkForUpdates, 'the recovery check').toBe(1)
    expect(ctl.getState().state).toBe('ready')
    expect(notices).toHaveLength(0)
    await vi.advanceTimersByTimeAsync(20 * HOUR)
    expect(u.calls.checkForUpdates, 'the later ticks of this start').toBe(1)
    ctl.stop()
  })
})

describe('MEU-174 UPDATER_CONFIG and UPDATE_E2E_SEAM', () => {
  it.each([
    ['allowPrerelease', false],
    ['allowDowngrade', false],
    ['autoDownload', true],
    ['autoInstallOnAppQuit', false],
  ] as const)('AC-174.3 after creation %s is %s', async (key, expected) => {
    const mod = await load()
    const { u } = setup(mod)
    expect(u.updater[key]).toBe(expected)
    expect(u.writes.filter(([k]) => k === key).map(([, v]) => v)).toEqual([expected])
  })

  it('AC-174.3 setFeedURL is never called and forceDevUpdateConfig stays unset without the seam', async () => {
    const mod = await load()
    for (const isPackaged of [true, false]) {
      const { u } = setup(mod, { isPackaged })
      expect(u.calls.setFeedURL).toBe(0)
      expect(u.writes.map(([k]) => k)).not.toContain('forceDevUpdateConfig')
      expect(u.writes.map(([k]) => k)).not.toContain('updateConfigPath')
      expect(u.updater.forceDevUpdateConfig).toBeUndefined()
    }
  })

  it('AC-174.3 [neg] with AVKIT_E2E unset the seam stays off and AVKIT_E2E_UPDATE_FEED is never read', async () => {
    const mod = await load()
    const readKeys: string[] = []
    const env = new Proxy({ AVKIT_E2E_UPDATE_FEED: 'C:\\e2e\\app-update.yml' } as Record<string, string | undefined>, {
      get(t, key) {
        readKeys.push(String(key))
        return t[String(key)]
      },
    })
    const exists = vi.fn(() => true)
    expect(mod.updateSeam(env, exists)).toBeNull()
    expect(readKeys).not.toContain('AVKIT_E2E_UPDATE_FEED')
    expect(readKeys).not.toContain('AVKIT_E2E_UPDATE_TICK_MS')
    expect(exists).toHaveBeenCalledTimes(0)
    expect(mod.updateSeam({ AVKIT_E2E: '0', AVKIT_E2E_UPDATE_FEED: 'C:\\e2e\\app-update.yml' }, exists)).toBeNull()
    expect(mod.updateSeam({ AVKIT_E2E: '1', AVKIT_E2E_UPDATE_FEED: 'C:\\e2e\\app-update.yml' }, () => false)).toBeNull()
  })

  it('AC-174.3 with AVKIT_E2E=1 and a feed file the seam sets the config path and runs the ticks unpackaged', async () => {
    const mod = await load()
    const feed = 'C:\\e2e\\app-update.yml'
    expect(mod.updateSeam({ AVKIT_E2E: '1', AVKIT_E2E_UPDATE_FEED: feed }, () => true)).toEqual({
      feedPath: feed,
      firstTickMs: 500,
      tickMs: 1000,
    })
    const seam = mod.updateSeam(
      { AVKIT_E2E: '1', AVKIT_E2E_UPDATE_FEED: feed, AVKIT_E2E_UPDATE_TICK_MS: '250' },
      () => true,
    )
    expect(seam).toEqual({ feedPath: feed, firstTickMs: 500, tickMs: 250 })
    const { ctl, u } = setup(mod, { isPackaged: false, seam })
    expect(u.updater.forceDevUpdateConfig).toBe(true)
    expect(u.updater.updateConfigPath).toBe(feed)
    expect(u.calls.setFeedURL).toBe(0)
    expect(ctl.getState().state).toBe('idle')
    ctl.start()
    await vi.advanceTimersByTimeAsync(500)
    expect(u.calls.checkForUpdates).toBe(1)
    ctl.stop()
  })
})

describe('MEU-174 UPDATE_STATE', () => {
  it('AC-174.4 the events map to the state, each change emits it, and a found version sets pendingVersion', async () => {
    const mod = await load()
    const { ctl, u, store, emitted } = setup(mod)
    expect(ctl.getState()).toEqual({
      state: 'idle',
      currentVersion: '1.0.0',
      availableVersion: null,
      percent: null,
      lastCheckAt: null,
      lastResult: null,
      errorKind: null,
    })
    u.emit('checking-for-update')
    expect(ctl.getState().state).toBe('checking')
    u.emit('update-available', { version: '2.0.0' })
    expect(ctl.getState()).toMatchObject({ state: 'downloading', availableVersion: '2.0.0' })
    expect(store.get('pendingVersion')).toBe('2.0.0')
    u.emit('download-progress', { percent: 42.5 })
    expect(ctl.getState()).toMatchObject({ state: 'downloading', percent: 42.5 })
    u.emit('update-downloaded', { version: '2.0.0' })
    expect(ctl.getState()).toMatchObject({
      state: 'ready',
      availableVersion: '2.0.0',
      lastResult: 'update-found',
      lastCheckAt: T0,
    })
    expect(emitted.map((s) => s.state)).toEqual(['checking', 'downloading', 'downloading', 'ready'])
    expect(emitted.at(-1)).toEqual(ctl.getState())
    expect(store.get('lastCheckAt')).toBe(T0)
    expect(store.get('lastAttemptAt')).toBe(T0)
    expect(store.get('lastResult')).toBe('update-found')
    for (const key of Object.keys(store.data)) expect(STORE_KEYS, key).toContain(key)
  })

  it('AC-174.4 a check that finds none clears pendingVersion and records the time', async () => {
    const mod = await load()
    const store = memoryStore({ pendingVersion: '1.5.0', lastCheckAt: T0 - 9 * DAY, lastAttemptAt: T0 - 9 * DAY })
    const { ctl, u } = setup(mod, { store })
    u.emit('checking-for-update')
    u.emit('update-not-available', { version: '1.0.0' })
    expect(ctl.getState()).toMatchObject({ state: 'idle', lastResult: 'up-to-date', lastCheckAt: T0 })
    expect(store.get('pendingVersion') ?? null).toBeNull()
    expect(store.get('lastCheckAt')).toBe(T0)
    expect(store.get('lastAttemptAt')).toBe(T0)
    for (const key of Object.keys(store.data)) expect(STORE_KEYS, key).toContain(key)
  })

  it('AC-174.4 a reopened store carries the last check into the next start', async () => {
    const mod = await load()
    const store = memoryStore()
    const first = setup(mod, { store })
    first.u.emit('update-available', { version: '2.0.0' })
    first.u.emit('update-downloaded', { version: '2.0.0' })
    vi.setSystemTime(T0 + HOUR)
    const second = setup(mod, { store: memoryStore(store.data) })
    expect(second.ctl.getState()).toMatchObject({ lastCheckAt: T0, lastResult: 'update-found' })
  })

  it('AC-174.4 [neg] a store with a string where a time belongs is read as null and the controller still ticks', async () => {
    const mod = await load()
    const store = memoryStore({ lastCheckAt: 'yesterday', lastAttemptAt: 'x', pendingVersion: 5, lastResult: 7 })
    const { ctl, u } = setup(mod, { store })
    expect(ctl.getState()).toMatchObject({ lastCheckAt: null, lastResult: null })
    ctl.start()
    await vi.advanceTimersByTimeAsync(MINUTE)
    expect(u.calls.checkForUpdates).toBe(1)
    ctl.stop()
  })

  it.each([
    [
      'a store file that is not JSON',
      () => ({
        get: () => {
          throw new SyntaxError('Unexpected token } in JSON at position 3')
        },
        set: () => undefined,
        delete: () => undefined,
      }),
    ],
    [
      'a store constructor that throws',
      () => {
        throw new Error('EPERM: operation not permitted, open update-state.json')
      },
    ],
  ])('AC-174.4 [neg] %s is read as empty and the controller still ticks', async (_name, openStore) => {
    const mod = await load()
    const { ctl, u } = setup(mod, { openStore: openStore as () => StoreLike })
    expect(ctl.getState()).toMatchObject({ state: 'idle', lastCheckAt: null, lastResult: null })
    ctl.start()
    await vi.advanceTimersByTimeAsync(MINUTE)
    expect(u.calls.checkForUpdates).toBe(1)
    ctl.stop()
  })
})

describe('MEU-174 UPDATE_QUIET_FAILURE', () => {
  const LAST_CHECK = T0 - 8 * DAY

  it('AC-174.5 a rejected checkForUpdates gives the state error, one log line, lastAttemptAt set and lastCheckAt unchanged', async () => {
    const mod = await load()
    const store = memoryStore({ lastCheckAt: LAST_CHECK, lastAttemptAt: LAST_CHECK })
    const { ctl, u, logs } = setup(mod, { store })
    u.setCheck(() => Promise.reject(new Error('net::ERR_INTERNET_DISCONNECTED')))
    ctl.start()
    await vi.advanceTimersByTimeAsync(MINUTE)
    expect(u.calls.checkForUpdates).toBe(1)
    expect(ctl.getState()).toMatchObject({ state: 'error', errorKind: 'network', lastResult: 'error' })
    expect(logs.filter((l) => l.startsWith('update: check failed'))).toEqual(['update: check failed kind=network'])
    expect(store.get('lastAttemptAt')).toBe(T0 + MINUTE)
    expect(store.get('lastCheckAt')).toBe(LAST_CHECK)
    ctl.stop()
  })

  it('AC-174.5 an error event gives the state error with its kind and one log line, also when the call rejects too', async () => {
    const mod = await load()
    const store = memoryStore({ lastCheckAt: LAST_CHECK, lastAttemptAt: LAST_CHECK })
    const { ctl, u, logs } = setup(mod, { store })
    const err = new Error('sha512 checksum mismatch, expected abc, got def')
    u.setCheck(async () => {
      u.emit('checking-for-update')
      u.emit('error', err)
      throw err
    })
    const state = await ctl.check()
    expect(state).toMatchObject({ state: 'error', errorKind: 'checksum' })
    expect(logs.filter((l) => l.startsWith('update: check failed'))).toEqual(['update: check failed kind=checksum'])
    expect(store.get('lastAttemptAt')).toBe(T0)
    expect(store.get('lastCheckAt')).toBe(LAST_CHECK)
  })

  it.each([
    ['the checksum code', 'ERR_CHECKSUM_MISMATCH', 'checksum'],
    ['a name lookup failure', 'getaddrinfo ENOTFOUND github.com', 'network'],
    ['a timeout', 'connect ETIMEDOUT 140.82.112.3:443', 'network'],
    ['a refused connection', 'connect ECONNREFUSED 127.0.0.1:443', 'network'],
    ['an HTTP status', 'HttpError: 404\n"method: GET url: https://github.com/matbanik/av-kit/releases.atom"', 'network'],
    ['an unknown message', 'Cannot parse update info', 'other'],
  ])('AC-174.5 an error event with %s has its kind', async (_label, message, kind) => {
    const mod = await load()
    const { ctl, u, logs } = setup(mod)
    u.setCheck(async () => {
      u.emit('error', new Error(message))
      return null
    })
    expect((await ctl.check()).errorKind).toBe(kind)
    expect(logs.filter((l) => l.startsWith('update: check failed'))).toEqual([`update: check failed kind=${kind}`])
  })

  it('AC-174.5 [neg] a failure shows no notice, no dialog and no window, leaks no rejection and logs no query or user path', async () => {
    const mod = await load()
    const { ctl, u, logs, notices } = setup(mod)
    const message =
      'HttpError: 403 url: https://api.github.com/repos/x?access_token=secret at C:\\Users\\alice\\AppData\\Local\\av-kit-ui-updater'
    u.setCheck(async () => {
      u.emit('error', new Error(message))
      throw new Error(message)
    })
    ctl.start()
    await vi.advanceTimersByTimeAsync(MINUTE)
    await ctl.check()
    await flush()
    await new Promise((resolve) => setImmediate(resolve))
    expect(notices).toHaveLength(0)
    expect(electronMocks.showMessageBox).toHaveBeenCalledTimes(0)
    expect(electronMocks.showMessageBoxSync).toHaveBeenCalledTimes(0)
    expect(electronMocks.showErrorBox).toHaveBeenCalledTimes(0)
    expect(electronMocks.BrowserWindow).toHaveBeenCalledTimes(0)
    expect(electronMocks.Notification).toHaveBeenCalledTimes(0)
    expect(unhandled).toEqual([])
    const failed = logs.filter((l) => l.startsWith('update: check failed'))
    expect(failed).toEqual(['update: check failed kind=network', 'update: check failed kind=network'])
    for (const line of logs) {
      expect(line).not.toContain('?')
      expect(line).not.toContain('https://')
      expect(line.toLowerCase()).not.toContain('c:\\users')
    }
    ctl.stop()
  })
})

describe('MEU-174 UPDATE_NOTICE_ONCE', () => {
  it('AC-174.6 one notice per downloaded version, and no quitAndInstall after update-downloaded', async () => {
    const mod = await load()
    const { u, notices, store } = setup(mod)
    u.emit('update-downloaded', { version: '2.0.0' })
    expect(notices).toEqual([NOTICE])
    expect(store.get('notifiedVersion')).toBe('2.0.0')
    u.emit('update-downloaded', { version: '2.0.0' })
    expect(notices).toHaveLength(1)
    u.emit('update-downloaded', { version: '2.0.1' })
    expect(notices).toHaveLength(2)
    expect(u.calls.quitAndInstall).toHaveLength(0)
  })

  it('AC-174.6 [neg] any number of ticks in the state ready produce no quitAndInstall', async () => {
    const mod = await load()
    const { ctl, u } = setup(mod)
    u.setCheck(async () => {
      u.emit('checking-for-update')
      u.emit('update-available', { version: '2.0.0' })
      u.emit('update-downloaded', { version: '2.0.0' })
      return null
    })
    ctl.start()
    await vi.advanceTimersByTimeAsync(60 * DAY)
    expect(u.calls.checkForUpdates).toBeGreaterThanOrEqual(1)
    expect(ctl.getState().state).toBe('ready')
    expect(u.calls.quitAndInstall).toHaveLength(0)
    ctl.stop()
  })
})

describe('MEU-174 UPDATE_INSTALL_ORDER', () => {
  function installSteps(order: string[]): string[] {
    return order.filter((s) => !s.startsWith('log:') || /^log:update: (install|backend)/.test(s))
  }

  it('AC-174.7 in ready, install() logs, sets the quit intent, awaits the backend, then calls quitAndInstall(true, true) once', async () => {
    const mod = await load()
    const { ctl, u } = setup(mod)
    u.emit('update-downloaded', { version: '2.0.0' })
    const result = await ctl.install()
    expect(result).toEqual({ ok: true })
    expect(installSteps(u.order)).toEqual([
      'log:update: install requested version=2.0.0',
      'setQuitIntent',
      'shutdownBackend resolved',
      'log:update: backend stopped',
      'quitAndInstall(true,true)',
    ])
    expect(u.calls.quitAndInstall).toEqual([[true, true]])
  })

  it('AC-174.7 [neg] in every other state install() returns not-ready and calls nothing', async () => {
    const mod = await load()
    const reach: Record<string, (u: ReturnType<typeof makeUpdater>) => void> = {
      idle: () => undefined,
      checking: (u) => u.emit('checking-for-update'),
      downloading: (u) => u.emit('update-available', { version: '2.0.0' }),
      error: (u) => u.emit('error', new Error('net::ERR_FAILED')),
    }
    for (const [state, go] of Object.entries(reach)) {
      const { ctl, u } = setup(mod)
      go(u)
      expect(ctl.getState().state, state).toBe(state)
      expect(await ctl.install(), state).toEqual({ ok: false, reason: 'not-ready' })
      expect(u.order.filter((s) => !s.startsWith('log:')), state).toEqual([])
    }
    const off = setup(mod, { isPackaged: false })
    off.u.emit('update-downloaded', { version: '2.0.0' })
    expect(off.ctl.getState().state).toBe('disabled')
    expect(await off.ctl.install()).toEqual({ ok: false, reason: 'not-ready' })
    expect(off.u.order.filter((s) => !s.startsWith('log:'))).toEqual([])
  })

  it('AC-174.7 [neg] with shutdownBackend pending quitAndInstall waits, and a second install() adds nothing', async () => {
    const mod = await load()
    let release: () => void = () => undefined
    const shutdowns = { count: 0 }
    const { ctl, u } = setup(mod, {
      shutdownBackend: () => {
        shutdowns.count++
        return new Promise<void>((resolve) => {
          release = resolve
        })
      },
    })
    u.emit('update-downloaded', { version: '2.0.0' })
    const pending = ctl.install()
    await flush()
    expect(u.calls.quitAndInstall).toHaveLength(0)
    expect(await ctl.install()).toEqual({ ok: false, reason: 'not-ready' })
    release()
    expect(await pending).toEqual({ ok: true })
    expect(await ctl.install()).toEqual({ ok: false, reason: 'not-ready' })
    expect(u.calls.quitAndInstall).toEqual([[true, true]])
    expect(u.order.filter((s) => s === 'setQuitIntent')).toHaveLength(1)
    expect(shutdowns.count).toBe(1)
  })
})

// --- Corrections round 1: the real library (F1 D-1591, F2 D-1592)
type LibRequest = { hostname?: string; path?: string; headers?: Record<string, unknown> }
type LibExecutor = { request(options: LibRequest): Promise<string> }
type LibApp = NonNullable<ConstructorParameters<typeof NsisUpdater>[1]>

const LIB_VERSION = '0.1.0'
const LIB_TAG = `v${LIB_VERSION}`
const LIB_BASE = '/matbanik/av-kit/releases'
const LIB_ATOM = [
  '<?xml version="1.0" encoding="UTF-8"?>',
  '<feed xmlns="http://www.w3.org/2005/Atom">',
  `<entry><title>${LIB_TAG}</title>`,
  `<link rel="alternate" type="text/html" href="https://github.com${LIB_BASE}/tag/${LIB_TAG}"/>`,
  '<content type="html">notes</content></entry>',
  '</feed>',
].join('\n')
const LIB_LATEST_YML = [
  `version: ${LIB_VERSION}`,
  'files:',
  `  - url: av-kit-Setup-${LIB_VERSION}.exe`,
  '    sha512: c2hhNTEy',
  '    size: 1',
  `path: av-kit-Setup-${LIB_VERSION}.exe`,
  'sha512: c2hhNTEy',
  "releaseDate: '2026-11-01T00:00:00.000Z'",
  '',
].join('\n')

describe('MEU-174 the controller over the real electron-updater', () => {
  let scratch = ''
  let userData = ''
  let consoleSpies: Array<ReturnType<typeof vi.spyOn>> = []

  beforeEach(() => {
    vi.useRealTimers()
    scratch = mkdtempSync(join(tmpdir(), 'avkit-updater-lib-'))
    userData = join(scratch, 'userData')
    writeFileSync(
      join(scratch, 'app-update.yml'),
      'provider: github\nowner: matbanik\nrepo: av-kit\nupdaterCacheDirName: av-kit-updater\n',
    )
    consoleSpies = (['log', 'info', 'warn', 'error', 'debug'] as const).map((name) =>
      vi.spyOn(console, name).mockImplementation(() => undefined),
    )
  })

  afterEach(() => {
    for (const spy of consoleSpies) spy.mockRestore()
    rmSync(scratch, { recursive: true, force: true })
  })

  const libApp = (): LibApp => ({
    version: LIB_VERSION,
    name: 'av-kit',
    isPackaged: true,
    appUpdateConfigPath: join(scratch, 'app-update.yml'),
    userDataPath: userData,
    baseCachePath: join(scratch, 'cache'),
    whenReady: () => Promise.resolve(),
    relaunch: () => undefined,
    quit: () => undefined,
    onQuit: () => undefined,
  })

  // One start: a new real NsisUpdater with the given executor, and a new controller over it.
  const startOnce = (mod: Mod, executor: LibExecutor, log: (line: string) => void): Controller => {
    const updater = new NsisUpdater(undefined, libApp())
    ;(updater as unknown as { httpExecutor: LibExecutor }).httpExecutor = executor
    const memory: Record<string, unknown> = {}
    return mod.createAppUpdater({
      updater,
      isPackaged: true,
      seam: null,
      currentVersion: LIB_VERSION,
      now: () => T0,
      timers: {
        setTimeout: () => null,
        clearTimeout: () => undefined,
        setInterval: () => null,
        clearInterval: () => undefined,
      },
      openStore: () => ({
        get: (key: string) => memory[key],
        set: (key: string, value: unknown) => {
          memory[key] = value
        },
      }),
      readInterval: () => Promise.resolve('daily'),
      notify: () => undefined,
      log,
      shutdownBackend: () => Promise.resolve(),
      setQuitIntent: () => undefined,
      emitState: () => undefined,
    })
  }

  it('AC-174.3 F1 two starts of the real NsisUpdater send no x-user-staging-id and write no .updaterId', async () => {
    const mod = await load()
    const requests: LibRequest[] = []
    const executor: LibExecutor = {
      request(options) {
        requests.push(options)
        const path = options.path ?? ''
        if (path.endsWith(`${LIB_BASE}.atom`)) return Promise.resolve(LIB_ATOM)
        if (path.endsWith(`${LIB_BASE}/latest`)) return Promise.resolve(JSON.stringify({ tag_name: LIB_TAG }))
        if (path.endsWith(`${LIB_BASE}/download/${LIB_TAG}/latest.yml`)) return Promise.resolve(LIB_LATEST_YML)
        return Promise.reject(new Error(`unexpected request ${path}`))
      },
    }
    const logs: string[] = []
    const states: string[] = []
    for (let start = 0; start < 2; start += 1) {
      states.push((await startOnce(mod, executor, (line) => logs.push(line)).check()).state)
    }

    expect(states).toEqual(['idle', 'idle'])
    expect(logs).toEqual([])
    expect(requests.map((options) => options.hostname)).toEqual(Array(6).fill('github.com'))
    expect(requests.filter((options) => (options.path ?? '').endsWith(`${LIB_BASE}/latest`))).toHaveLength(2)
    for (const options of requests) {
      const names = Object.keys(options.headers ?? {}).map((name) => name.toLowerCase())
      expect(names, `headers of ${options.path ?? ''}`).not.toContain('x-user-staging-id')
    }
    expect(existsSync(join(userData, '.updaterId')), 'userData/.updaterId').toBe(false)
  })

  it('AC-174.5 F2 a real-library HTTP error logs only the controller line and nothing from the library', async () => {
    const mod = await load()
    const executor: LibExecutor = {
      request() {
        const err = new Error(
          'HttpError: 500 Internal Server Error\n"method: GET url: https://github.com/matbanik/av-kit/releases.atom?probe=QUERYMARK"',
        )
        const frame = String.raw`C:\Users\PROFILEMARK\AppData\Local\Programs\av-kit\resources\app.asar\out\main\index.js`
        err.stack = `${err.message}\n    at ${frame}:1:1`
        return Promise.reject(err)
      },
    }
    const logs: string[] = []
    const state = await startOnce(mod, executor, (line) => logs.push(line)).check()

    expect(state.state).toBe('error')
    expect(state.errorKind).toBe('network')
    expect(logs).toEqual(['update: check failed kind=network'])
    const libraryEntries = consoleSpies.flatMap((spy) => spy.mock.calls.map((call: unknown[]) => call.map(String).join(' ')))
    expect(libraryEntries).toEqual([])
  })
})
