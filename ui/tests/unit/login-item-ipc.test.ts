import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it, vi } from 'vitest'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')

describe('MEU-61 login-item IPC', () => {
  it('AC-61.8 IPC_GET empty/strict; IPC_SET both booleans required', async () => {
    const { handleIpc } = await import('../../src/main/ipc')
    const effects = { dialog: 0, fs: 0, clipboard: 0, spawn: 0 }
    const getEmpty = await handleIpc('login-item-get', undefined, { sideEffects: effects })
    expect(getEmpty.ok).toBe(true)
    const getObj = await handleIpc('login-item-get', {}, { sideEffects: effects })
    expect(getObj.ok).toBe(true)
    const missing = await handleIpc(
      'login-item-set',
      { enabled: true },
      { sideEffects: effects },
    )
    expect(missing.ok).toBe(false)
  })

  it('AC-61.9 extra IPC fields reject before Electron', async () => {
    const { handleIpc, listRegisteredChannels } = await import('../../src/main/ipc')
    expect(listRegisteredChannels()).toContain('login-item-get')
    expect(listRegisteredChannels()).toContain('login-item-set')
    const effects = { dialog: 0, fs: 0, clipboard: 0, spawn: 0 }
    const extraGet = await handleIpc(
      'login-item-get',
      { extra: true },
      { sideEffects: effects },
    )
    expect(extraGet.ok).toBe(false)
    const extraSet = await handleIpc(
      'login-item-set',
      { enabled: true, minimized: false, path: 'C:/x' },
      { sideEffects: effects },
    )
    expect(extraSet.ok).toBe(false)
    expect(effects.spawn).toBe(0)
  })

  it('AC-61.19 listRegisteredChannels length is IPC_CHANNEL_COUNT including IPC_GET and IPC_SET', async () => {
    const { listRegisteredChannels } = await import('../../src/main/ipc')
    const { RENDERER_TO_MAIN_CHANNELS } = await import('./ipc-channels')
    const registered = listRegisteredChannels()
    expect(registered).toHaveLength(22)
    expect(RENDERER_TO_MAIN_CHANNELS).toHaveLength(22)
    expect(registered).toEqual([...RENDERER_TO_MAIN_CHANNELS])
    expect(registered).toContain('login-item-get')
    expect(registered).toContain('login-item-set')
  })

  it('AC-61.20 preload keys include PRELOAD_GET and PRELOAD_SET', async () => {
    const { getPreloadApiKeys } = await import('../../src/main/preload')
    const keys = getPreloadApiKeys()
    expect(keys).toContain('loginItemGet')
    expect(keys).toContain('loginItemSet')
  })
})

describe('MEU-61 startup-mode and index', () => {
  it('AC-61.22 argv match is whole-token not substring', async () => {
    const { argvHasFlag, START_MINIMIZED_FLAG } = await import('../../src/main/startup-mode')
    expect(START_MINIMIZED_FLAG).toBe('--start-minimized')
    expect(argvHasFlag(['av-kit.exe', '--start-minimized'], START_MINIMIZED_FLAG)).toBe(true)
    expect(
      argvHasFlag(['C:\\start-minimized-tools\\av-kit.exe'], START_MINIMIZED_FLAG),
    ).toBe(false)
  })

  it('AC-61.15 argv START_MINIMIZED_FLAG skips window.show; no FORBIDDEN_ELECTRON', async () => {
    const { revealMainWindow, shouldShowWindowAfterLoad } = await import(
      '../../src/main/startup-mode'
    )
    expect(shouldShowWindowAfterLoad(['--start-minimized'], false)).toBe(false)
    expect(shouldShowWindowAfterLoad(['av-kit.exe'], false)).toBe(true)
    expect(shouldShowWindowAfterLoad(['av-kit.exe'], true)).toBe(false)
    const hidden = { show: vi.fn() }
    revealMainWindow(hidden, ['--start-minimized'], false)
    expect(hidden.show).not.toHaveBeenCalled()
    const shown = { show: vi.fn() }
    revealMainWindow(shown, ['av-kit.exe'], false)
    expect(shown.show).toHaveBeenCalledTimes(1)
    const loginHidden = { show: vi.fn() }
    revealMainWindow(loginHidden, ['av-kit.exe'], true)
    expect(loginHidden.show).not.toHaveBeenCalled()
    const index = readFileSync(resolve(repoRoot, 'ui/src/main/index.ts'), 'utf8')
    expect(index).not.toMatch(/window\.show\(/)
    expect(index).toMatch(
      /revealMainWindow\(\s*window\s*,\s*process\.argv\s*,\s*loginLaunchShouldHideWindow\(/,
    )
    expect(index).not.toContain('openAsHidden')
    const tray = readFileSync(resolve(repoRoot, 'ui/src/main/capture-tray.ts'), 'utf8')
    expect(tray).toMatch(/opts\.window\.show\(\)/)
  })
})
