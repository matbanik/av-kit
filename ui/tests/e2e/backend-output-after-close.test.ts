import { _electron, expect, test } from '@playwright/test'
import { mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))

test('AC-108.7 a backend line after the window is destroyed throws nothing in the real main process', async () => {
  const app = await _electron.launch({
    args: [resolve(here, '../../out/main/index.js')],
    env: {
      ...process.env,
      AVKIT_E2E: '1',
      AVKIT_APP_DATA: mkdtempSync(join(tmpdir(), 'avkit-e2e-late-line-')),
    },
  })
  await app.firstWindow()
  const outcome = await app.evaluate(({ app: electronApp, BrowserWindow }) => {
    // Without a listener, the last window going away quits the app before the handler can run.
    electronApp.on('window-all-closed', () => undefined)
    const window = BrowserWindow.getAllWindows()[0]
    window?.destroy()
    type Stream = { listeners?: (event: string) => Array<{ name: string }>; emit: (event: string, chunk: Buffer) => void }
    const handles = (process as unknown as { _getActiveHandles(): Stream[] })._getActiveHandles()
    const streams = handles.filter((handle) =>
      handle.listeners?.('data').some((listener) => listener.name === 'onChildOutput'),
    )
    const thrown: string[] = []
    for (const stream of streams) {
      try {
        stream.emit('data', Buffer.from('INFO late line\n'))
      } catch (err: unknown) {
        // Caught here so a failing run reports it, instead of stopping on the error dialog.
        thrown.push(String(err))
      }
    }
    return { destroyed: window?.isDestroyed() ?? false, streams: streams.length, thrown }
  })
  expect(outcome.destroyed).toBe(true)
  expect(outcome.streams).toBeGreaterThan(0)
  expect(outcome.thrown).toEqual([])
  await app.close()
})
