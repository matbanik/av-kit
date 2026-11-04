/** @vitest-environment jsdom */

/**
 * `lib/queue/shell-ipc-ledger` — the queue cards' E2E IPC ledger.
 *
 * The ledger exists because `window.api` is a frozen contextBridge proxy that a
 * Playwright test cannot stub. These tests pin both halves of the contract: it
 * records when a test created the array, and it is inert otherwise, so a
 * production run carries no observable side effect.
 */
import { afterEach, describe, expect, it } from 'vitest'

import {
  recordShellIpc,
  type ShellIpcEntry,
} from '../../src/renderer/src/lib/queue/shell-ipc-ledger'

type Host = { __e2eIpc?: unknown }

afterEach(() => {
  delete (window as unknown as Host).__e2eIpc
})

describe('recordShellIpc', () => {
  it('appends channel and target in call order when a ledger exists', () => {
    const ledger: ShellIpcEntry[] = []
    ;(window as unknown as Host).__e2eIpc = ledger
    recordShellIpc('openPath', 'C:/out/job-3.mp4')
    recordShellIpc('showItemInFolder', 'C:/out/job-3.mp4')
    expect(ledger).toEqual([
      { channel: 'openPath', target: 'C:/out/job-3.mp4' },
      { channel: 'showItemInFolder', target: 'C:/out/job-3.mp4' },
    ])
  })

  it('is a no-op when no ledger was installed', () => {
    recordShellIpc('openPath', 'C:/out/job-3.mp4')
    expect((window as unknown as Host).__e2eIpc).toBeUndefined()
  })

  it('is a no-op when the ledger slot holds a non-array', () => {
    ;(window as unknown as Host).__e2eIpc = 'not-an-array'
    expect(() => {
      recordShellIpc('openPath', 'C:/out/job-3.mp4')
    }).not.toThrow()
    expect((window as unknown as Host).__e2eIpc).toBe('not-an-array')
  })
})
