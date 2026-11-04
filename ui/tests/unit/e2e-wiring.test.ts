import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'

import { describe, expect, it } from 'vitest'

const e2eDir = resolve(__dirname, '../e2e')

describe('AC-19.15 / AC-19.16 E2E waves 0/5/7 written and wired', () => {
  it('keeps wave 0/5/7 files and shell testids', () => {
    const files = [
      'launch.test.ts',
      'console-panel.test.ts',
      'command-palette-nav.spec.ts',
      'convert-queue.test.ts',
      'capture-inbox.test.ts',
      'test-ids.ts',
      'global-setup.ts',
      'global-teardown.ts',
    ]
    for (const file of files) {
      const path = resolve(e2eDir, file)
      expect(existsSync(path), path).toBe(true)
    }
    const ids = readFileSync(resolve(e2eDir, 'test-ids.ts'), 'utf8')
    for (const id of [
      'nav-downloader',
      'nav-transcript',
      'nav-tts',
      'nav-convert',
      'nav-capture',
      'nav-settings',
      'nav-collapse',
      'console-panel',
      'console-filter',
      'console-search',
      'console-clear',
      'console-copy',
      'console-collapse',
      'console-ytdlp-toggle',
      'console-log-to-file',
      'command-palette',
      'command-palette-input',
    ]) {
      expect(ids).toContain(id)
    }
  })
})
