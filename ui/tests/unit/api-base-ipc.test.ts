import { describe, expect, it, vi } from 'vitest'

describe('AC-19.13 API_BASE IPC', () => {
  it('never publishes a pre-listen port 0 URL and does not use sendSync', async () => {
    const ipc = await import('../../src/main/ipc')
    ipc.resetBackendIpcState()
    const pending = ipc.handleIpc('get-backend-url', undefined, {
      sideEffects: { dialog: 0, fs: 0, clipboard: 0, spawn: 0 },
    })
    ipc.publishBackendReady({
      apiBase: 'http://127.0.0.1:0/api/v1',
      token: 'gui-nonce',
    })
    const rejected = await pending
    expect(rejected.ok).toBe(false)

    ipc.resetBackendIpcState()
    const ready = ipc.handleIpc('get-backend-url', undefined, {
      sideEffects: { dialog: 0, fs: 0, clipboard: 0, spawn: 0 },
    })
    ipc.publishBackendReady({
      apiBase: 'http://127.0.0.1:51234/api/v1',
      token: 'gui-nonce',
    })
    const url = await ready
    expect(url).toEqual({ ok: true, value: 'http://127.0.0.1:51234/api/v1' })
    const token = await ipc.handleIpc('get-token', {}, {
      sideEffects: { dialog: 0, fs: 0, clipboard: 0, spawn: 0 },
    })
    expect(token).toEqual({ ok: true, value: 'gui-nonce' })
    expect(ipc.usesSendSync()).toBe(false)
  })

  it('get-backend-url rejects after BACKEND_READY_TIMEOUT_MS when never published', async () => {
    vi.useFakeTimers()
    const ipc = await import('../../src/main/ipc')
    ipc.resetBackendIpcState()
    const pending = ipc.handleIpc('get-backend-url', undefined, {
      sideEffects: { dialog: 0, fs: 0, clipboard: 0, spawn: 0 },
    })
    await vi.advanceTimersByTimeAsync(ipc.BACKEND_READY_TIMEOUT_MS)
    await expect(pending).resolves.toEqual({ ok: false, error: 'backend not ready' })
    vi.useRealTimers()
  })
})
