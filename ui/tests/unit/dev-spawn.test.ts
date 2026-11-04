import { join } from 'node:path'
import { describe, expect, it } from 'vitest'

describe('AC-19.22 DEV_SPAWN', () => {
  it('owns the resolved Python image, never uv.exe', async () => {
    const { assertOwnedIdentity, buildDevSpawnArgv, buildPackagedSpawnArgv, resolvePythonImage } =
      await import('../../src/main/python-manager')
    const pythonImage = 'C:/Users/Mat/.local/share/uv/python/cpython.exe'
    const resolved = await resolvePythonImage(async (cmd: string[]) => {
      expect(cmd[0]).toBe('uv')
      expect(cmd.slice(1)).toEqual(['run', 'python', '-c', 'import sys; print(sys.executable)'])
      return `${pythonImage}\n`
    })
    expect(resolved).toBe(pythonImage)

    const argv = buildDevSpawnArgv({
      pythonImage,
      token: 'gui-nonce',
      mcpToken: 'mcp-token',
      appData: 'C:/data/av-kit',
    })
    expect(argv[0]).toBe(pythonImage)
    expect(argv[1]).toBe('-m')
    expect(argv[2]).toBe('avkit_api')
    expect(argv).toContain('--token')
    expect(argv).toContain('--mcp-token')
    expect(argv).toContain('--port')
    expect(argv).toContain('0')
    expect(argv).toContain('--app-data')
    expect(argv.some((part) => part.toLowerCase().includes('uv.exe'))).toBe(false)

    const packaged = buildPackagedSpawnArgv({
      packagedBackend: 'C:/Program Files/av-kit/resources/avkit-backend/avkit-backend.exe',
      token: 'gui-nonce',
      mcpToken: 'mcp-token',
      appData: 'C:/data/av-kit',
    })
    expect(packaged[0]).toBe('C:/Program Files/av-kit/resources/avkit-backend/avkit-backend.exe')

    expect(
      assertOwnedIdentity({
        ownedPid: 111,
        descriptorPid: 111,
        liveImage: pythonImage,
        oursExe: pythonImage,
      }),
    ).toBe(true)
    expect(
      assertOwnedIdentity({
        ownedPid: 111,
        descriptorPid: 222,
        liveImage: pythonImage,
        oursExe: pythonImage,
      }),
    ).toBe(false)
    expect(
      assertOwnedIdentity({
        ownedPid: 111,
        descriptorPid: 111,
        liveImage: 'C:/tools/uv.exe',
        oursExe: pythonImage,
      }),
    ).toBe(false)
  })

  it('confirmReadyAndPublish publishes from AVKIT_READY on the owned child stdout', async () => {
    const { confirmReadyAndPublish } = await import('../../src/main/python-manager')
    const published: Array<{ apiBase: string; token: string }> = []
    const publish = (ready: { apiBase: string; token: string }) => {
      published.push(ready)
    }
    const withheld = confirmReadyAndPublish({
      readyText: 'engine.created module=database',
      ownedPid: 111,
      descriptorPid: 111,
      liveImage: 'C:/Users/Mat/.local/share/uv/python/cpython.exe',
      oursExe: 'C:/Users/Mat/.local/share/uv/python/cpython.exe',
      token: 'gui-nonce',
      publish,
    })
    expect(withheld).toBe(false)
    expect(published).toEqual([])

    const portZero = confirmReadyAndPublish({
      readyText: 'AVKIT_READY port=0 instance=abc',
      ownedPid: 111,
      descriptorPid: 111,
      liveImage: 'C:/Users/Mat/.local/share/uv/python/cpython.exe',
      oursExe: 'C:/Users/Mat/.local/share/uv/python/cpython.exe',
      token: 'gui-nonce',
      publish,
    })
    expect(portZero).toBe(false)
    expect(published).toEqual([])

    const raced = confirmReadyAndPublish({
      readyText: 'AVKIT_READY port=13988 instance=70d5efcc-856f-4f37-b90a-eb2b4c09e72e',
      ownedPid: 111,
      descriptorPid: null,
      liveImage: '',
      oursExe: 'P:\\av-kit\\.venv\\Scripts\\python.exe',
      token: 'gui-nonce',
      publish,
    })
    expect(raced).toBe(true)

    const mismatched = confirmReadyAndPublish({
      readyText: 'AVKIT_READY port=13988 instance=70d5efcc-856f-4f37-b90a-eb2b4c09e72e',
      ownedPid: 111,
      descriptorPid: 222,
      liveImage: 'C:/Windows/System32/notepad.exe',
      oursExe: 'P:\\av-kit\\.venv\\Scripts\\python.exe',
      token: 'gui-nonce',
      publish,
    })
    expect(mismatched).toBe(true)
    expect(published).toEqual([
      { apiBase: 'http://127.0.0.1:13988/api/v1', token: 'gui-nonce' },
      { apiBase: 'http://127.0.0.1:13988/api/v1', token: 'gui-nonce' },
    ])
  })

  it('AC-25.3 RESOURCES_BACKEND uses packagedBackendPath, never extra/', async () => {
    const { packagedBackendPath } = await import('../../src/main/python-manager')
    const resourcesPath = 'C:/Program Files/av-kit/resources'
    expect(packagedBackendPath(resourcesPath)).toBe(
      join(resourcesPath, 'avkit-backend', 'avkit-backend.exe'),
    )
    expect(packagedBackendPath(resourcesPath)).not.toContain('extra/')
  })
})
