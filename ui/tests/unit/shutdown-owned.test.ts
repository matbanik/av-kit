import { describe, expect, it, vi } from 'vitest'

describe('AC-19.23 SHUTDOWN_OWNED', () => {
  it('retires the descriptor on quit and on unexpected child exit', async () => {
    const { shutdownOwned } = await import('../../src/main/python-manager')
    const signal = vi.fn()
    const retireDescriptor = vi.fn()
    const retirePortSibling = vi.fn()
    const waitPid = vi.fn(async () => undefined)

    await shutdownOwned('quit', {
      ownedPid: 501,
      foreignPid: 999,
      signal,
      retireDescriptor,
      retirePortSibling,
      waitPid,
    })
    expect(signal).toHaveBeenCalledTimes(1)
    expect(signal).toHaveBeenCalledWith(501)
    expect(signal).not.toHaveBeenCalledWith(999)
    expect(waitPid).toHaveBeenCalledWith(501)
    expect(retireDescriptor).toHaveBeenCalledTimes(1)
    expect(retirePortSibling).toHaveBeenCalledTimes(1)

    signal.mockClear()
    retireDescriptor.mockClear()
    retirePortSibling.mockClear()
    waitPid.mockClear()

    await shutdownOwned('child-exit', {
      ownedPid: 501,
      foreignPid: 999,
      signal,
      retireDescriptor,
      retirePortSibling,
      waitPid,
    })
    expect(signal).not.toHaveBeenCalled()
    expect(retireDescriptor).toHaveBeenCalledTimes(1)
    expect(retirePortSibling).toHaveBeenCalledTimes(1)
  })

  it('waitPidExit polls until the owned pid is gone', async () => {
    const { waitPidExit } = await import('../../src/main/python-manager')
    let alive = true
    const running = vi.fn((pid: number) => {
      expect(pid).toBe(501)
      return alive
    })
    const done = waitPidExit(501, running, 1000)
    alive = false
    await done
    expect(running).toHaveBeenCalled()
  })
})
