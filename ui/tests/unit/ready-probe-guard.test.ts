import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, expect, it, vi } from 'vitest'
import type { LiveQuery } from '../../src/main/live-identity'
import { confirmReadyAndPublish, forwardConsoleLines, publishIfReady } from '../../src/main/python-manager'

const here = dirname(fileURLToPath(import.meta.url))
const OURS = 'P:\\av-kit\\.venv\\Scripts\\python.exe'
const READY = 'AVKIT_READY port=13988 instance=70d5efcc-856f-4f37-b90a-eb2b4c09e72e'

function feed(chunks: string[]) {
  const queryLive = vi.fn((): LiveQuery => ({ ok: true, image: OURS }))
  const published: Array<{ apiBase: string; token: string }> = []
  const results = chunks.map((chunkText) =>
    publishIfReady({
      chunkText,
      ownedPid: 111,
      readDescriptorPid: () => 111,
      queryLive,
      oursExe: OURS,
      token: 'gui-nonce',
      publish: (ready) => {
        published.push(ready)
      },
    }),
  )
  return { queryLive, published, results }
}

describe('MEU-108 READY_GUARD', () => {
  it('AC-108.1 a chunk with no AVKIT_READY line does no process query and publishes nothing', () => {
    const { queryLive, published, results } = feed([
      'engine.created module=database',
      'INFO transcript fetched 12 of 43\nINFO transcript fetched 13 of 43\n',
      'AVKIT_READY',
    ])
    expect(queryLive).toHaveBeenCalledTimes(0)
    expect(published).toEqual([])
    expect(results).toEqual([false, false, false])
  })

  it('AC-108.2 AVKIT_READY port=0 does no process query and publishes nothing', () => {
    const { queryLive, published, results } = feed(['AVKIT_READY port=0 instance=abc'])
    expect(queryLive).toHaveBeenCalledTimes(0)
    expect(published).toEqual([])
    expect(results).toEqual([false])
  })

  it('AC-108.3 a usable READY chunk queries once and publishes what confirmReadyAndPublish publishes', () => {
    const { queryLive, published, results } = feed([`INFO starting\n${READY}\nINFO listening\n`])
    expect(queryLive).toHaveBeenCalledTimes(1)
    expect(queryLive).toHaveBeenCalledWith(111)
    expect(results).toEqual([true])

    const direct: Array<{ apiBase: string; token: string }> = []
    confirmReadyAndPublish({
      readyText: READY,
      ownedPid: 111,
      descriptorPid: 111,
      liveImage: OURS,
      oursExe: OURS,
      token: 'gui-nonce',
      publish: (ready) => {
        direct.push(ready)
      },
    })
    expect(published).toEqual(direct)
    expect(published).toEqual([{ apiBase: 'http://127.0.0.1:13988/api/v1', token: 'gui-nonce' }])
  })

  it('AC-108.4 the output handler queries only through publishIfReady', () => {
    const source = readFileSync(resolve(here, '../../src/main/index.ts'), 'utf8')
    const handler = source.slice(
      source.indexOf('const onChildOutput'),
      source.indexOf("child.stdout?.on('data', onChildOutput)"),
    )
    expect(handler).toContain('publishIfReady(')
    expect(handler).toContain('queryLive: queryLiveProcess')
    expect(source).not.toMatch(/queryLiveProcess\(/)
    expect(source).not.toContain('confirmReadyAndPublish')

    const logLines = Array.from({ length: 50 }, (_, i) => `INFO job progress ${i}`)
    const { queryLive, published } = feed([...logLines, READY, ...logLines])
    expect(queryLive).toHaveBeenCalledTimes(1)
    expect(published).toHaveLength(1)
  })
})

describe('MEU-108 LOG_AFTER_WINDOW', () => {
  const LINES = [{ key: 'ipc:1', message: 'INFO late line', id: 'ipc:1' }]

  function thrownBy(run: () => void): string | null {
    try {
      run()
      return null
    } catch (err: unknown) {
      return String(err)
    }
  }

  it('AC-108.5 a line after the window is destroyed throws nothing', () => {
    // Electron's own behaviour: reading webContents from a destroyed window throws.
    const destroyed = {
      isDestroyed: () => true,
      get webContents(): { send: () => void } {
        throw new TypeError('Object has been destroyed')
      },
    }
    expect(thrownBy(() => forwardConsoleLines(destroyed, LINES))).toBeNull()
  })

  it('AC-108.5 a line after the renderer is torn down throws nothing', () => {
    // The race capture-lifecycle.test.ts names: the window answers alive and the send throws.
    const tornDown = {
      isDestroyed: () => false,
      webContents: {
        send: () => {
          throw new TypeError('Object has been destroyed')
        },
      },
    }
    expect(thrownBy(() => forwardConsoleLines(tornDown, LINES))).toBeNull()
  })

  it('AC-108.6 a live window gets the lines on console-log-batch', () => {
    const send = vi.fn()
    forwardConsoleLines({ isDestroyed: () => false, webContents: { send } }, LINES)
    expect(send).toHaveBeenCalledTimes(1)
    expect(send).toHaveBeenCalledWith('console-log-batch', LINES)
  })

  it('AC-108.6 no window yet sends nothing and throws nothing', () => {
    expect(thrownBy(() => forwardConsoleLines(null, LINES))).toBeNull()
  })

  it('AC-108.6 the output handler reaches the window only through forwardConsoleLines', () => {
    const source = readFileSync(resolve(here, '../../src/main/index.ts'), 'utf8')
    const handler = source.slice(
      source.indexOf('const onChildOutput'),
      source.indexOf("child.stdout?.on('data', onChildOutput)"),
    )
    expect(handler.match(/forwardConsoleLines\(mainWindow, /g)).toHaveLength(2)
    expect(handler).not.toContain('webContents')
  })
})
