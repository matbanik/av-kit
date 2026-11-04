import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'

import { describe, expect, it } from 'vitest'

const routerPath = resolve(__dirname, '../../src/renderer/src/router.tsx')
const homePath = resolve(__dirname, '../../src/renderer/src/features/shell/ShellHome.tsx')
const navPath = resolve(__dirname, '../../src/renderer/src/components/layout/NavRail.tsx')

describe('AC-19.11 SHELL_HOME + SHELL_NAV', () => {
  it('uses DownloaderPage on / after MEU-20 DOWNLOADER_HOME', async () => {
    expect(existsSync(routerPath)).toBe(true)
    const src = readFileSync(routerPath, 'utf8')
    expect(src).toContain('createHashHistory')
    expect(src).toContain('DownloaderPage')
    expect(src).not.toMatch(/component:\s*ShellHome/)

    const { SHELL_NAV } = await import('../../src/renderer/src/components/layout/NavRail')
    expect(SHELL_NAV.map((item) => item.id)).toEqual([
      'nav:downloader',
      'nav:transcript',
      'nav:tts',
      'nav:convert',
      'nav:capture',
      'nav:settings',
      'nav:collapse',
    ])

    const home = readFileSync(homePath, 'utf8')
    expect(home).toMatch(/Connecting to backend/)
    expect(home).not.toMatch(/url-input/)

    const nav = readFileSync(navPath, 'utf8')
    for (const testId of [
      'nav-downloader',
      'nav-transcript',
      'nav-tts',
      'nav-convert',
      'nav-capture',
      'nav-settings',
      'nav-collapse',
    ]) {
      expect(nav).toContain(testId)
    }
  })
})
