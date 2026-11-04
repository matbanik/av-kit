import { describe, expect, it, vi } from 'vitest'

describe('AC-19.8 SECRET_PATH_DENY + READ_TEXT_EXTS', () => {
  it('rejects secret files and renderer-supplied raw paths', async () => {
    const { handleIpc } = await import('../../src/main/ipc')
    const appData = 'C:/Users/test/AppData/Local/av-kit'
    const sideEffects = { dialog: 0, fs: 0, clipboard: 0, spawn: 0 }
    const deps = {
      appData,
      sideEffects,
      showFileDialog: vi.fn(async () => `${appData}/mcp-token.txt`),
      showFilesDialog: vi.fn(async () => []),
      getPathForFile: () => '',
      readFile: vi.fn(async () => 'secret'),
      openPath: vi.fn(async () => undefined),
      showItemInFolder: vi.fn(async () => undefined),
    }

    const deniedRead = await handleIpc('read-text-file', { maxBytes: 1024 }, deps)
    expect(deniedRead.ok).toBe(false)
    expect(deps.readFile).not.toHaveBeenCalled()
    expect(sideEffects.fs).toBe(0)

    const rawPath = await handleIpc(
      'read-text-file',
      { maxBytes: 1024, path: `${appData}/notes.txt` },
      deps,
    )
    expect(rawPath.ok).toBe(false)
    expect(sideEffects.fs).toBe(0)

    const exe = await handleIpc('open-path', { target: `${appData}/tool.exe` }, deps)
    expect(exe.ok).toBe(false)
    expect(deps.openPath).not.toHaveBeenCalled()

    const url = await handleIpc('show-item-in-folder', { target: 'https://example.com' }, deps)
    expect(url.ok).toBe(false)
    expect(deps.showItemInFolder).not.toHaveBeenCalled()
  })

  it('rejects an external .exe and honors read-text maxBytes', async () => {
    const { handleIpc } = await import('../../src/main/ipc')
    const sideEffects = { dialog: 0, fs: 0, clipboard: 0, spawn: 0 }
    const deps = {
      appData: 'C:/Users/test/AppData/Local/av-kit',
      sideEffects,
      showFileDialog: vi.fn(async () => 'C:/notes/readme.txt'),
      showFilesDialog: vi.fn(async () => []),
      getPathForFile: () => '',
      readFile: vi.fn(async () => 'ABCD1234'),
      openPath: vi.fn(async () => undefined),
      showItemInFolder: vi.fn(async () => undefined),
    }

    const exe = await handleIpc('open-path', { target: 'C:/outside/tool.exe' }, deps)
    expect(exe.ok).toBe(false)
    expect(deps.openPath).not.toHaveBeenCalled()
    expect(sideEffects.fs).toBe(0)

    const shown = await handleIpc('show-item-in-folder', { target: 'C:/outside/tool.exe' }, deps)
    expect(shown.ok).toBe(false)
    expect(deps.showItemInFolder).not.toHaveBeenCalled()

    const limited = await handleIpc('read-text-file', { maxBytes: 1 }, deps)
    expect(limited).toEqual({ ok: true, value: { text: 'A', basename: 'readme.txt' } })
    expect(deps.readFile).toHaveBeenCalledTimes(1)
  })
})
