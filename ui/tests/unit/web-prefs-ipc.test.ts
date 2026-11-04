import { describe, expect, it } from 'vitest'

import { RENDERER_TO_MAIN_CHANNELS } from './ipc-channels'

describe('AC-19.7 WEB_PREFS + IPC_CHANNELS + IPC_SCHEMAS', () => {
  it('locks BrowserWindow webPreferences', async () => {
    const { createWebPreferences } = await import('../../src/main/ipc')
    expect(createWebPreferences()).toEqual({
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
      webSecurity: true,
    })
  })

  it('registers every renderer-to-main channel and rejects unknowns', async () => {
    const { handleIpc, listRegisteredChannels } = await import('../../src/main/ipc')
    const registered = listRegisteredChannels()
    for (const channel of RENDERER_TO_MAIN_CHANNELS) {
      expect(registered).toContain(channel)
    }
    expect(registered).not.toContain('console-log-batch')
    const unknown = await handleIpc('not-a-channel', {}, {
      sideEffects: { dialog: 0, fs: 0, clipboard: 0, spawn: 0 },
    })
    expect(unknown.ok).toBe(false)
  })

  it('does not expose ipcRenderer on the preload bridge', async () => {
    const { getPreloadApiKeys } = await import('../../src/main/preload')
    const keys = getPreloadApiKeys()
    expect(keys).not.toContain('ipcRenderer')
    expect(keys).not.toContain('send')
  })
})
