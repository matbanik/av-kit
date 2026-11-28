// APP_USER_MODEL_ID (MEU-174, D-1583, the root cause of B-17): on Windows, Electron's
// getLoginItemSettings has no name option and reads openAtLogin from the Run value named after the
// current AppUserModelId, while login-item.ts writes that value as LOGIN_ITEM_NAME. Until
// boot() set the id, it was Electron's default at startup (notify-user.ts set it only inside a
// toast), so an installed app never read its own Run value back and the start-at-sign-in box
// stayed unchecked. boot() now sets the id on win32 before it reads the login item or creates a
// window or tray, and the id is the appId electron-builder gives the NSIS shortcut.
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it, vi } from 'vitest'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')

function bootBody(): string {
  const src = readFileSync(resolve(repoRoot, 'ui/src/main/index.ts'), 'utf8').replace(/\r\n/g, '\n')
  const start = src.indexOf('export async function boot(): Promise<void> {')
  expect(start, 'boot() in index.ts').toBeGreaterThanOrEqual(0)
  const end = src.indexOf('\n}\n', start)
  return src.slice(start, end > start ? end : undefined)
}

describe('APP_USER_MODEL_ID (D-1583)', () => {
  it('sets the AppUserModelId to the login item name on win32 only', async () => {
    const index = await import('../../src/main/index')
    const { LOGIN_ITEM_NAME } = await import('../../src/main/login-item')
    expect(typeof index.applyAppUserModelId, 'index.ts exports applyAppUserModelId').toBe('function')
    const win = { setAppUserModelId: vi.fn() }
    index.applyAppUserModelId(win, 'win32')
    expect(win.setAppUserModelId).toHaveBeenCalledTimes(1)
    expect(win.setAppUserModelId).toHaveBeenCalledWith(LOGIN_ITEM_NAME)
    for (const platform of ['darwin', 'linux'] as const) {
      const other = { setAppUserModelId: vi.fn() }
      index.applyAppUserModelId(other, platform)
      expect(other.setAppUserModelId, platform).not.toHaveBeenCalled()
    }
  })

  it('uses the appId that electron-builder gives the NSIS shortcut and the toast id', async () => {
    const { LOGIN_ITEM_NAME } = await import('../../src/main/login-item')
    const { NOTIFY_APP_USER_MODEL_ID } = await import('../../src/main/notify-user')
    const builder = readFileSync(resolve(repoRoot, 'ui/electron-builder.yml'), 'utf8')
    expect(builder).toMatch(new RegExp(`^appId: ${LOGIN_ITEM_NAME.replace(/\./g, '\\.')}\\r?$`, 'm'))
    expect(NOTIFY_APP_USER_MODEL_ID).toBe(LOGIN_ITEM_NAME)
  })

  it('boot() sets the id before the login item is read and before any window or tray', () => {
    const body = bootBody()
    const call = body.indexOf('applyAppUserModelId(')
    expect(call, 'boot() calls applyAppUserModelId').toBeGreaterThanOrEqual(0)
    for (const later of ['getLoginItemSettings', 'new BrowserWindow(', 'startCaptureTray(']) {
      const at = body.indexOf(later)
      expect(at, `${later} in boot()`).toBeGreaterThan(0)
      expect(call, `applyAppUserModelId before ${later}`).toBeLessThan(at)
    }
  })
})
