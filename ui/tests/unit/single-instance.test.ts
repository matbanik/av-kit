import { describe, expect, it, vi } from 'vitest'

describe('AC-19.5 SINGLE_INSTANCE', () => {
  it('winner keeps the lock and loser does not spawn', async () => {
    const { applySingleInstance } = await import('../../src/main/index')
    const spawnBackend = vi.fn()
    const winnerApp = {
      requestSingleInstanceLock: vi.fn(() => true),
      quit: vi.fn(),
      on: vi.fn(),
    }
    expect(applySingleInstance(winnerApp, spawnBackend)).toBe('winner')
    expect(winnerApp.quit).not.toHaveBeenCalled()
    expect(winnerApp.on).toHaveBeenCalledWith('second-instance', expect.any(Function))

    const loserSpawn = vi.fn()
    const loserApp = {
      requestSingleInstanceLock: vi.fn(() => false),
      quit: vi.fn(),
      on: vi.fn(),
    }
    expect(applySingleInstance(loserApp, loserSpawn)).toBe('loser')
    expect(loserApp.quit).toHaveBeenCalledTimes(1)
    expect(loserSpawn).not.toHaveBeenCalled()
  })
})
