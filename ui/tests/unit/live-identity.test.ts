import { describe, expect, it } from 'vitest'

describe('AC-19.6 LIVE_IDENTITY_PROOF', () => {
  it('refuses when the live query fails and never signals', async () => {
    const { evaluateLiveIdentity } = await import('../../src/main/live-identity')
    const result = evaluateLiveIdentity({
      lockHeld: true,
      pidRunning: true,
      query: { ok: false },
      oursExe: 'C:/av-kit/python.exe',
      oursAppData: 'C:/data/av-kit',
      descriptor: {
        schema_version: 1,
        pid: 4242,
        executable_path: 'C:/av-kit/python.exe',
        app_data: 'C:/data/av-kit',
      },
    })
    expect(result.decision).toBe('refuse')
    expect(result.signalPid).toBeNull()
  })

  it('refuses PID reuse when the live image is foreign', async () => {
    const { evaluateLiveIdentity } = await import('../../src/main/live-identity')
    const result = evaluateLiveIdentity({
      lockHeld: true,
      pidRunning: true,
      query: { ok: true, image: 'C:/Windows/System32/notepad.exe', cmdline: '--app-data C:/data/av-kit' },
      oursExe: 'C:/av-kit/python.exe',
      oursAppData: 'C:/data/av-kit',
      descriptor: {
        schema_version: 1,
        pid: 99,
        executable_path: 'C:/av-kit/python.exe',
        app_data: 'C:/data/av-kit',
      },
    })
    expect(result.decision).toBe('refuse')
    expect(result.signalPid).toBeNull()
  })

  it('reaps an owned orphan when proof succeeds', async () => {
    const { evaluateLiveIdentity } = await import('../../src/main/live-identity')
    const result = evaluateLiveIdentity({
      lockHeld: true,
      pidRunning: true,
      query: {
        ok: true,
        image: 'C:/av-kit/python.exe',
        cmdline: 'python -m avkit_api --app-data C:/data/av-kit',
      },
      oursExe: 'C:/av-kit/python.exe',
      oursAppData: 'C:/data/av-kit',
      descriptor: {
        schema_version: 1,
        pid: 77,
        executable_path: 'C:/av-kit/python.exe',
        app_data: 'C:/data/av-kit',
      },
    })
    expect(result.decision).toBe('reap_then_spawn')
    expect(result.signalPid).toBe(77)
  })

  it('spawns when the descriptor pid is not running', async () => {
    const { evaluateLiveIdentity } = await import('../../src/main/live-identity')
    const result = evaluateLiveIdentity({
      lockHeld: true,
      pidRunning: false,
      query: { ok: false },
      oursExe: 'C:/av-kit/python.exe',
      oursAppData: 'C:/data/av-kit',
      descriptor: null,
    })
    expect(result.decision).toBe('spawn')
    expect(result.signalPid).toBeNull()
  })

  it('resolveBootIdentity refuses an unsupported live descriptor instead of ignoring it', async () => {
    const { resolveBootIdentity } = await import('../../src/main/live-identity')
    const queries: number[] = []
    const result = resolveBootIdentity({
      lockHeld: true,
      oursExe: 'C:/av-kit/python.exe',
      oursAppData: 'C:/data/av-kit',
      descriptorRaw: JSON.stringify({
        schema_version: 999,
        pid: 4242,
        executable_path: 'C:/av-kit/python.exe',
        app_data: 'C:/data/av-kit',
      }),
      isPidRunning: (pid) => pid === 4242,
      queryLive: (pid) => {
        queries.push(pid)
        return {
          ok: true,
          image: 'C:/av-kit/python.exe',
          cmdline: 'python -m avkit_api --app-data C:/data/av-kit',
        }
      },
    })
    expect(queries).toEqual([4242])
    expect(result.decision).toBe('refuse')
    expect(result.signalPid).toBeNull()
  })
})
