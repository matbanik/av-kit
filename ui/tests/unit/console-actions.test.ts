import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

import { describe, expect, it, vi } from 'vitest'

describe('AC-19.19 CONSOLE_SHELL_ACTIONS', () => {
  it('copies via IPC and persists log-to-file through PUT /settings/app', async () => {
    const panel = readFileSync(
      resolve(__dirname, '../../src/renderer/src/components/layout/ConsolePanel.tsx'),
      'utf8',
    )
    for (const testId of [
      'console-panel',
      'console-filter',
      'console-search',
      'console-clear',
      'console-copy',
      'console-collapse',
      'console-ytdlp-toggle',
      'console-log-to-file',
      'console-log-file-path',
    ]) {
      expect(panel).toContain(testId)
    }

    const { copyVisibleLogs, putLogToFile, redactConsoleText } = await import(
      '../../src/renderer/src/components/layout/ConsolePanel'
    )
    const writeClipboard = vi.fn(async () => undefined)
    await copyVisibleLogs(['line-a', 'line-b'], writeClipboard)
    expect(writeClipboard).toHaveBeenCalledWith('line-a\nline-b')

    const apiFetch = vi.fn(async () => undefined)
    await putLogToFile(true, apiFetch)
    expect(apiFetch).toHaveBeenCalledWith('/settings/app', {
      method: 'PUT',
      body: JSON.stringify({ log_to_file: true }),
    })

    expect(redactConsoleText('Bearer gui-nonce-abc Authorization: Bearer gui-nonce-abc')).not.toContain(
      'gui-nonce-abc',
    )
  })
})
