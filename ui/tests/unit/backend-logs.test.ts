/** @vitest-environment jsdom */

import { describe, expect, it } from 'vitest'

describe('AC-19.12 SEQ_OWNER + IPC_STDOUT_ID', () => {
  it('keys ring events by seq and stdout-only by ipc:*', async () => {
    const { clearView, keyRingEvent, keyStdoutEvent, mergeIntoView } = await import(
      '../../src/renderer/src/hooks/useBackendLogs'
    )
    const ring = keyRingEvent({ seq: 4, message: 'from-ring' })
    const stdout = keyStdoutEvent('7')
    expect(ring).toBe('4')
    expect(stdout).toBe('ipc:7')
    const merged = mergeIntoView(
      [],
      [
        { key: ring, message: 'from-ring', seq: 4 },
        { key: stdout, message: 'access-log', id: 'ipc:7' },
      ],
    )
    expect(merged.map((row) => row.key)).toEqual(['4', 'ipc:7'])
    const cleared = clearView(merged)
    expect(cleared).toEqual([])
    expect(merged).toHaveLength(2)
  })

  it('renderer log events merge into the console view', async () => {
    const { RENDERER_LOG_EVENT, logRenderer } = await import('../../src/renderer/src/lib/renderer-log')
    const { mergeIntoView } = await import('../../src/renderer/src/hooks/useBackendLogs')
    const incoming: Array<{ key: string; message: string }> = []
    const onLog = (event: Event) => {
      incoming.push((event as CustomEvent<{ key: string; message: string }>).detail)
    }
    window.addEventListener(RENDERER_LOG_EVENT, onLog)
    logRenderer('INFO', 'add: posting https://example.invalid/watch?v=e2e0001')
    window.removeEventListener(RENDERER_LOG_EVENT, onLog)
    expect(incoming[0]?.message).toMatch(/^INFO add: posting/)
    const merged = mergeIntoView([], incoming)
    expect(merged[0]?.key.startsWith('ui:')).toBe(true)
  })
})
