import { describe, expect, it } from 'vitest'

import { IPC_NO_PAYLOAD, RENDERER_TO_MAIN_CHANNELS } from './ipc-channels'

const VALID_PAYLOAD: Record<string, unknown> = {
  'get-backend-url': undefined,
  'get-token': {},
  'startup-metric': { key: 'startup.shell_paint_ms', value: 10, timestamp: 1 },
  'show-directory-dialog': {},
  'show-file-dialog': { filters: [{ name: 'Text', extensions: ['txt'] }] },
  'show-files-dialog': { filters: [{ name: 'Video', extensions: ['mp4'] }] },
  'open-path': { target: 'C:/out/video.mp4' },
  'show-item-in-folder': { target: 'C:/out/video.mp4' },
  'read-clipboard-text': undefined,
  'write-clipboard-text': { text: 'copied' },
  'read-text-file': { maxBytes: 1024 },
  'copy-mcp-config': { pinEndpoint: false },
  'get-log-snapshot': {},
  'get-setup-readiness': {},
  'get-mcp-access-status': {},
  'capture-region': {},
  'get-hotkey-status': {},
  'login-item-get': {},
  'login-item-set': { enabled: false, minimized: false },
  'write-clipboard-image': { png: Uint8Array.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0]) },
  'get-mcp-setup-prompt': { client: 'codex', scope: 'user' },
  'capture-paste-image': {},
}

const TYPE_FAIL: Record<string, unknown> = {
  'get-backend-url': 1,
  'get-token': 'nope',
  'startup-metric': { key: 'not-a-metric', value: 10, timestamp: 1 },
  'show-directory-dialog': [],
  'show-file-dialog': { filters: 'nope' },
  'show-files-dialog': { filters: 'nope' },
  'open-path': { target: '' },
  'show-item-in-folder': { target: 9 },
  'read-clipboard-text': { unexpected: true },
  'write-clipboard-text': { text: 4 },
  'read-text-file': { maxBytes: 0 },
  'copy-mcp-config': { pinEndpoint: 'yes' },
  'get-log-snapshot': 0,
  'get-setup-readiness': { extra: true },
  'get-mcp-access-status': null,
  'capture-region': { extra: true },
  'get-hotkey-status': null,
  'login-item-get': { extra: true },
  'login-item-set': { enabled: true },
  'write-clipboard-image': { png: 'iVBORw0KGgo=' },
  'get-mcp-setup-prompt': { client: 4, scope: 'user' },
  'capture-paste-image': { extra: true },
}

describe('AC-19.21 IPC_STRICT_CENSUS', () => {
  it('rejects extra keys and wrong types before any side effect', async () => {
    const { handleIpc } = await import('../../src/main/ipc')
    expect(RENDERER_TO_MAIN_CHANNELS).toHaveLength(22)
    for (const channel of RENDERER_TO_MAIN_CHANNELS) {
      const extraPayload =
        VALID_PAYLOAD[channel] === undefined ||
        (typeof VALID_PAYLOAD[channel] === 'object' && VALID_PAYLOAD[channel] !== null)
          ? { ...(typeof VALID_PAYLOAD[channel] === 'object' && VALID_PAYLOAD[channel] !== null
              ? (VALID_PAYLOAD[channel] as Record<string, unknown>)
              : {}), extra: true }
          : { extra: true }
      const extraEffects = { dialog: 0, fs: 0, clipboard: 0, spawn: 0 }
      const extra = await handleIpc(channel, extraPayload, { sideEffects: extraEffects })
      expect(extra.ok, `${channel} extra`).toBe(false)
      expect(extraEffects).toEqual({ dialog: 0, fs: 0, clipboard: 0, spawn: 0 })

      const typeEffects = { dialog: 0, fs: 0, clipboard: 0, spawn: 0 }
      const typed = await handleIpc(channel, TYPE_FAIL[channel], { sideEffects: typeEffects })
      expect(typed.ok, `${channel} type`).toBe(false)
      expect(typeEffects).toEqual({ dialog: 0, fs: 0, clipboard: 0, spawn: 0 })
    }
    for (const channel of IPC_NO_PAYLOAD) {
      const effects = { dialog: 0, fs: 0, clipboard: 0, spawn: 0 }
      const bad = await handleIpc(channel, { extra: 1 }, { sideEffects: effects })
      expect(bad.ok).toBe(false)
      expect(effects.dialog + effects.fs + effects.clipboard + effects.spawn).toBe(0)
    }
  })
})
