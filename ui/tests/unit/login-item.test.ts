import { describe, expect, it, vi } from 'vitest'

const EXE = 'C:\\Users\\avkit\\AppData\\Local\\Programs\\av-kit\\av-kit.exe'
const LOGIN_ITEM_NAME = 'com.avkit.app'
const START_MINIMIZED_FLAG = '--start-minimized'

type LaunchItemFact = {
  name: string
  path: string
  args: string[]
  scope: 'user' | 'machine'
  enabled: boolean
}

type LoginItemDeps = {
  platform: NodeJS.Platform
  packaged: boolean
  execPath: string
  getLoginItemSettings: (options: { path: string; args: string[] }) => {
    openAtLogin: boolean
    executableWillLaunchAtLogin?: boolean
    launchItems?: LaunchItemFact[]
    openAsHidden?: boolean
    wasOpenedAsHidden?: boolean
  }
  setLoginItemSettings: (settings: {
    openAtLogin: boolean
    path: string
    args: string[]
    name: string
    openAsHidden?: boolean
  }) => void
}

function fakeRunKey(initial: string[] | null = null) {
  let registered: string[] | null = initial
  return {
    getLoginItemSettings: vi.fn((options: { path: string; args: string[] }) => ({
      openAtLogin:
        registered !== null &&
        registered.length === options.args.length &&
        registered.every((a, i) => a === options.args[i]),
    })),
    setLoginItemSettings: vi.fn(
      (s: { openAtLogin: boolean; path: string; args: string[]; name: string }) => {
        registered = s.openAtLogin ? [...s.args] : null
      },
    ),
  }
}

function deps(overrides: Partial<LoginItemDeps> = {}): LoginItemDeps {
  return {
    platform: 'win32',
    packaged: true,
    execPath: EXE,
    getLoginItemSettings: vi.fn(() => ({ openAtLogin: false })),
    setLoginItemSettings: vi.fn(),
    ...overrides,
  }
}

function approvalDeps(opts: {
  registered: string[] | null
  approved: boolean
  omitWindowsFields?: boolean
}): LoginItemDeps {
  return deps({
    getLoginItemSettings: vi.fn((o: { path: string; args: string[] }) => {
      const matches =
        opts.registered !== null &&
        opts.registered.length === o.args.length &&
        opts.registered.every((a, i) => a === o.args[i])
      if (opts.omitWindowsFields) return { openAtLogin: matches }
      const own: LaunchItemFact[] =
        opts.registered === null
          ? []
          : [
              {
                name: LOGIN_ITEM_NAME,
                path: EXE,
                args: opts.registered,
                scope: 'user',
                enabled: opts.approved,
              },
            ]
      return {
        openAtLogin: matches,
        executableWillLaunchAtLogin: opts.registered !== null && opts.approved,
        launchItems: own,
      }
    }),
  })
}

function liveDeps(initial: string[] | null = null) {
  const key = fakeRunKey(initial)
  return deps({
    getLoginItemSettings: key.getLoginItemSettings,
    setLoginItemSettings: key.setLoginItemSettings,
  })
}

describe('MEU-61 login-item', () => {
  it('AC-61.1 classifyLoginItemSupport returns platform then not-packaged then supported', async () => {
    const { classifyLoginItemSupport } = await import('../../src/main/login-item')
    expect(
      classifyLoginItemSupport({ platform: 'linux', packaged: true }),
    ).toEqual({ supported: false, reason: 'platform' })
    expect(
      classifyLoginItemSupport({ platform: 'win32', packaged: false }),
    ).toEqual({ supported: false, reason: 'not-packaged' })
    expect(
      classifyLoginItemSupport({ platform: 'darwin', packaged: false }),
    ).toEqual({ supported: false, reason: 'not-packaged' })
    expect(classifyLoginItemSupport({ platform: 'win32', packaged: true })).toEqual({
      supported: true,
    })
    expect(classifyLoginItemSupport({ platform: 'darwin', packaged: true })).toEqual({
      supported: true,
    })
  })

  it('AC-61.2 every set passes name LOGIN_ITEM_NAME', async () => {
    const { writeStartAtSignIn } = await import('../../src/main/login-item')
    const d = liveDeps()
    writeStartAtSignIn(true, false, d)
    expect(d.setLoginItemSettings).toHaveBeenCalled()
    for (const call of vi.mocked(d.setLoginItemSettings).mock.calls) {
      expect(call[0].name).toBe(LOGIN_ITEM_NAME)
    }
  })

  it('AC-61.3 path is execPath and never FORBIDDEN_PATH_STUB', async () => {
    const { writeStartAtSignIn } = await import('../../src/main/login-item')
    const d = liveDeps()
    writeStartAtSignIn(true, true, d)
    for (const call of vi.mocked(d.setLoginItemSettings).mock.calls) {
      expect(call[0].path).toBe(EXE)
      expect(String(call[0].path)).not.toContain('Update.exe')
    }
  })

  it('AC-61.4 args is empty or START_MINIMIZED_FLAG only', async () => {
    const { writeStartAtSignIn } = await import('../../src/main/login-item')
    const d = liveDeps()
    writeStartAtSignIn(true, false, d)
    const windowed = vi.mocked(d.setLoginItemSettings).mock.calls.at(-1)?.[0]
    expect(windowed?.args).toEqual([])
    writeStartAtSignIn(true, true, d)
    const minimized = vi.mocked(d.setLoginItemSettings).mock.calls.at(-1)?.[0]
    expect(minimized?.args).toEqual([START_MINIMIZED_FLAG])
  })

  it('AC-61.5 read probes minimized then windowed; Windows approval fields disable', async () => {
    const { readStartAtSignIn } = await import('../../src/main/login-item')
    const order: string[][] = []
    const d = deps({
      getLoginItemSettings: vi.fn((o: { path: string; args: string[] }) => {
        order.push(o.args)
        return { openAtLogin: false }
      }),
    })
    expect(readStartAtSignIn(d)).toEqual({
      supported: true,
      enabled: false,
      minimized: false,
      startMinimizedSupported: true,
    })
    expect(order[0]).toEqual([START_MINIMIZED_FLAG])
    expect(order[1]).toEqual([])

    const disabled = approvalDeps({
      registered: [],
      approved: false,
    })
    disabled.getLoginItemSettings = vi.fn(() => ({
      openAtLogin: true,
      executableWillLaunchAtLogin: false,
      launchItems: [
        {
          name: LOGIN_ITEM_NAME,
          path: EXE,
          args: [] as string[],
          scope: 'user' as const,
          enabled: false,
        },
      ],
    }))
    expect(readStartAtSignIn(disabled).enabled).toBe(false)
  })

  it('AC-61.6 write clears the other variant; off clears minimized', async () => {
    const { writeStartAtSignIn, readStartAtSignIn } = await import('../../src/main/login-item')
    const d = liveDeps()
    writeStartAtSignIn(true, true, d)
    const calls = vi.mocked(d.setLoginItemSettings).mock.calls
    expect(calls.length).toBeGreaterThanOrEqual(2)
    const first = calls[0]?.[0]
    const second = calls[1]?.[0]
    expect(first?.openAtLogin).toBe(false)
    expect(second?.openAtLogin).toBe(true)
    expect(second?.args).toEqual([START_MINIMIZED_FLAG])
    const afterOff = writeStartAtSignIn(false, true, d)
    expect(afterOff).toEqual({
      supported: true,
      enabled: false,
      minimized: false,
      startMinimizedSupported: true,
    })
    for (const call of calls) {
      expect(call[0]).not.toHaveProperty('openAsHidden')
    }
    expect(readStartAtSignIn(d).minimized).toBe(false)
  })

  it('AC-61.7 non-boolean args throw TypeError and do not call Electron', async () => {
    const { writeStartAtSignIn } = await import('../../src/main/login-item')
    const d = liveDeps()
    expect(() => writeStartAtSignIn('true' as unknown as boolean, false, d)).toThrow(TypeError)
    expect(() => writeStartAtSignIn(true, 1 as unknown as boolean, d)).toThrow(TypeError)
    expect(d.setLoginItemSettings).toHaveBeenCalledTimes(0)
  })

  it('AC-61.10 unsupported write returns unsupported state without throw', async () => {
    const { writeStartAtSignIn } = await import('../../src/main/login-item')
    const linux = deps({ platform: 'linux', packaged: true })
    expect(writeStartAtSignIn(true, false, linux)).toEqual({
      supported: false,
      reason: 'platform',
      enabled: false,
      minimized: false,
    })
    expect(linux.setLoginItemSettings).toHaveBeenCalledTimes(0)
    const unpackaged = deps({ packaged: false })
    expect(writeStartAtSignIn(true, false, unpackaged)).toEqual({
      supported: false,
      reason: 'not-packaged',
      enabled: false,
      minimized: false,
    })
  })

  it('AC-61.11 default off: no OS entry means enabled false', async () => {
    const { readStartAtSignIn } = await import('../../src/main/login-item')
    expect(readStartAtSignIn(liveDeps(null))).toEqual({
      supported: true,
      enabled: false,
      minimized: false,
      startMinimizedSupported: true,
    })
  })

  it('AC-61.5 darwin openAtLogin is enabled; minimized stays false even if openAsHidden is true', async () => {
    const { readStartAtSignIn } = await import('../../src/main/login-item')
    const d = deps({
      platform: 'darwin',
      getLoginItemSettings: vi.fn(() => ({
        openAtLogin: true,
        openAsHidden: true,
      })),
    })
    expect(readStartAtSignIn(d)).toEqual({
      supported: true,
      enabled: true,
      minimized: false,
      startMinimizedSupported: false,
    })
    expect(d.getLoginItemSettings).toHaveBeenCalledTimes(1)
    expect(vi.mocked(d.getLoginItemSettings).mock.calls[0]?.[0].args).toEqual([])
  })

  it('AC-61.6 darwin write ignores minimized and never passes openAsHidden', async () => {
    const { writeStartAtSignIn } = await import('../../src/main/login-item')
    const state = { openAtLogin: false }
    const d = deps({
      platform: 'darwin',
      getLoginItemSettings: vi.fn(() => ({
        openAtLogin: state.openAtLogin,
      })),
      setLoginItemSettings: vi.fn((s) => {
        state.openAtLogin = s.openAtLogin
      }),
    })
    expect(writeStartAtSignIn(true, true, d)).toEqual({
      supported: true,
      enabled: true,
      minimized: false,
      startMinimizedSupported: false,
    })
    for (const call of vi.mocked(d.setLoginItemSettings).mock.calls) {
      expect(call[0].name).toBe(LOGIN_ITEM_NAME)
      expect(call[0].args).toEqual([])
      expect(String(call[0].path)).not.toContain('Update.exe')
      expect(call[0]).not.toHaveProperty('openAsHidden')
    }
    const last = vi.mocked(d.setLoginItemSettings).mock.calls.at(-1)?.[0]
    expect(last?.openAtLogin).toBe(true)
  })

  it('AC-61.15 loginLaunchShouldHideWindow follows wasOpenedAsHidden only', async () => {
    const { loginLaunchShouldHideWindow } = await import('../../src/main/login-item')
    expect(loginLaunchShouldHideWindow(() => ({}))).toBe(false)
    expect(loginLaunchShouldHideWindow(() => ({ wasOpenedAsHidden: false }))).toBe(false)
    expect(loginLaunchShouldHideWindow(() => ({ wasOpenedAsHidden: true }))).toBe(true)
  })
})
