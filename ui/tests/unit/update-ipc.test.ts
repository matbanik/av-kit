// Session 106 (MEU-174) UPDATE_IPC, AC-174.8: three renderer-to-main channels with the no-payload
// schema, one main-to-renderer push and four preload keys. `update-check` runs a check whatever
// the interval says. The controller is loaded by a dynamic import inside the tests that need it.
import { afterEach, describe, expect, it, vi } from 'vitest'

import { handleIpc, listRegisteredChannels, RENDERER_TO_MAIN_CHANNELS } from '../../src/main/ipc'
import { getPreloadApiKeys } from '../../src/main/preload'

const CHANNELS = ['update-get-state', 'update-check', 'update-install'] as const
const PRELOAD_KEYS = ['updateGetState', 'updateCheck', 'updateInstall', 'onUpdateState'] as const
const UPDATER_MODULE = '../../src/main/app-updater'
const IPC_MODULE = '../../src/main/ipc'

const STATE = {
  state: 'idle',
  currentVersion: '1.0.0',
  availableVersion: null,
  percent: null,
  lastCheckAt: null,
  lastResult: null,
  errorKind: null,
}

function fakeUpdater() {
  return {
    getState: vi.fn(() => ({ ...STATE })),
    check: vi.fn(async () => ({ ...STATE, state: 'checking' })),
    install: vi.fn(async () => ({ ok: false, reason: 'not-ready' })),
  }
}

type Controller = { check(): Promise<{ state: string }>; getState(): { state: string } }

async function realController(isPackaged: boolean) {
  const mod = (await import(UPDATER_MODULE).catch(() => ({}))) as Record<string, unknown>
  expect(typeof mod.createAppUpdater, 'app-updater exports createAppUpdater').toBe('function')
  const calls = { checkForUpdates: 0 }
  const updater = {
    on: () => updater,
    checkForUpdates: async () => {
      calls.checkForUpdates++
      return null
    },
    quitAndInstall: () => undefined,
  }
  const data: Record<string, unknown> = {}
  const create = mod.createAppUpdater as (deps: Record<string, unknown>) => Controller
  const ctl = create({
    updater,
    isPackaged,
    seam: null,
    currentVersion: '1.0.0',
    now: () => Date.now(),
    timers: { setTimeout, clearTimeout, setInterval, clearInterval },
    openStore: () => ({
      get: (k: string) => data[k],
      set: (k: string, v: unknown) => {
        data[k] = v
      },
      delete: (k: string) => {
        delete data[k]
      },
    }),
    readInterval: async () => 'never',
    notify: () => undefined,
    log: () => undefined,
    shutdownBackend: async () => undefined,
    setQuitIntent: () => undefined,
    emitState: () => undefined,
  })
  return { ctl, calls }
}

afterEach(() => {
  vi.doUnmock('electron')
  vi.resetModules()
})

describe('MEU-174 UPDATE_IPC', () => {
  it('AC-174.8 the three channels are registered and answer with no payload', async () => {
    for (const channel of CHANNELS) {
      expect(RENDERER_TO_MAIN_CHANNELS as readonly string[], channel).toContain(channel)
      expect(listRegisteredChannels(), channel).toContain(channel)
    }
    const appUpdater = fakeUpdater()
    const state = await handleIpc('update-get-state', undefined, { appUpdater } as never)
    expect(state).toEqual({ ok: true, value: STATE })
    const checked = await handleIpc('update-check', {}, { appUpdater } as never)
    expect(checked).toEqual({ ok: true, value: { ...STATE, state: 'checking' } })
    const installed = await handleIpc('update-install', undefined, { appUpdater } as never)
    expect(installed).toEqual({ ok: true, value: { ok: false, reason: 'not-ready' } })
    expect(appUpdater.check).toHaveBeenCalledTimes(1)
    expect(appUpdater.install).toHaveBeenCalledTimes(1)
  })

  it('AC-174.8 the push is update-state-changed and the preload exposes the four keys', async () => {
    const keys = getPreloadApiKeys()
    for (const key of PRELOAD_KEYS) expect(keys, key).toContain(key)
    const ipc = (await import(IPC_MODULE)) as Record<string, unknown>
    expect(ipc.UPDATE_STATE_CHANNEL).toBe('update-state-changed')

    const listeners = new Map<string, (...args: unknown[]) => void>()
    const ipcRenderer = {
      invoke: vi.fn(async () => undefined),
      on: vi.fn((channel: string, fn: (...args: unknown[]) => void) => {
        listeners.set(channel, fn)
      }),
      removeListener: vi.fn((channel: string) => {
        listeners.delete(channel)
      }),
    }
    let api: Record<string, (...args: unknown[]) => unknown> = {}
    vi.resetModules()
    vi.doMock('electron', () => ({
      contextBridge: {
        exposeInMainWorld: (_name: string, value: typeof api) => {
          api = value
        },
      },
      ipcRenderer,
      webUtils: { getPathForFile: () => '' },
    }))
    const preload = (await import('../../src/main/preload')) as { exposePreload: () => void }
    preload.exposePreload()
    await api.updateGetState()
    await api.updateCheck()
    await api.updateInstall()
    expect(ipcRenderer.invoke.mock.calls).toEqual([['update-get-state'], ['update-check'], ['update-install']])
    const seen: unknown[] = []
    const unsubscribe = api.onUpdateState((s: unknown) => seen.push(s)) as () => void
    expect(typeof unsubscribe).toBe('function')
    listeners.get('update-state-changed')?.({}, STATE)
    expect(seen).toEqual([STATE])
    unsubscribe()
    expect(ipcRenderer.removeListener).toHaveBeenCalledWith('update-state-changed', expect.any(Function))
    expect(listeners.has('update-state-changed')).toBe(false)
  })

  it('AC-174.8 update-check runs a check whatever the interval says, also with never', async () => {
    const { ctl, calls } = await realController(true)
    const result = await handleIpc('update-check', undefined, { appUpdater: ctl } as never)
    expect(result.ok).toBe(true)
    expect(calls.checkForUpdates).toBe(1)
  })

  it('AC-174.8 [neg] each channel refuses a payload', async () => {
    expect(RENDERER_TO_MAIN_CHANNELS as readonly string[]).toContain('update-check')
    const appUpdater = fakeUpdater()
    for (const channel of CHANNELS) {
      for (const payload of [{ force: true }, 'now', true, 1]) {
        const result = await handleIpc(channel, payload, { appUpdater } as never)
        expect(result.ok, `${channel} ${JSON.stringify(payload)}`).toBe(false)
      }
    }
    expect(appUpdater.getState).toHaveBeenCalledTimes(0)
    expect(appUpdater.check).toHaveBeenCalledTimes(0)
    expect(appUpdater.install).toHaveBeenCalledTimes(0)
  })

  it('AC-174.8 [neg] update-check in the state disabled calls checkForUpdates 0 times', async () => {
    const { ctl, calls } = await realController(false)
    const result = await handleIpc('update-check', undefined, { appUpdater: ctl } as never)
    expect(result).toMatchObject({ ok: true, value: { state: 'disabled' } })
    expect(calls.checkForUpdates).toBe(0)
  })
})
