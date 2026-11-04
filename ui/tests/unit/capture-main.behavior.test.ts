import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { afterEach, describe, expect, it, vi } from 'vitest'

import {
  finalizeCapturedPng,
  listPendingRequests,
  POLL_REQUEST_MS,
  startInteractivePoll,
  stopInteractivePoll,
} from '../../src/main/capture-register'
import {
  isBlackOrEmptyBitmap,
  inspectNativeImagePixels,
  isPngContainer,
  PNG_SIGNATURE,
} from '../../src/main/capture-pixels'
import { applyCaptureRuntime, fetchCaptureRuntime, parseCaptureRuntime } from '../../src/main/capture-runtime'
import { publishBackendReady, resetBackendIpcState } from '../../src/main/ipc'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')

describe('MEU-39 capture main runtime (exec r1 F2 F3 F6)', () => {
  it('AC-39.22 raw pixels detect black and reject PNG container sampling', () => {
    expect(isBlackOrEmptyBitmap(Buffer.from([0, 0, 0, 255]), 1, 1)).toBe(true)
    expect(isBlackOrEmptyBitmap(Buffer.from([20, 0, 0, 255]), 1, 1)).toBe(false)
    const png = Buffer.concat([PNG_SIGNATURE, Buffer.from([1, 2, 3, 4])])
    expect(isPngContainer(png)).toBe(true)
    expect(() => isBlackOrEmptyBitmap(png, 1, 1)).toThrow(/PNG container/)
    const black = inspectNativeImagePixels({
      isEmpty: () => false,
      getSize: () => ({ width: 1, height: 1 }),
      toBitmap: () => Buffer.from([0, 0, 0, 255]),
      toPNG: () => {
        throw new Error('must not sample PNG container')
      },
    } as never)
    expect(black.blocked).toBe(true)
    const lit = inspectNativeImagePixels({
      isEmpty: () => false,
      getSize: () => ({ width: 1, height: 1 }),
      toBitmap: () => Buffer.from([40, 10, 10, 255]),
      toPNG: () => {
        throw new Error('must not sample PNG container')
      },
    } as never)
    expect(lit.blocked).toBe(false)
    // MEU-40: the guard's caller moved from the deleted Chromium overlay to the picker,
    // which samples the staged PNG the sidecar wrote.
    const picker = readFileSync(resolve(repoRoot, 'ui/src/main/capture-picker.ts'), 'utf8')
    expect(picker).toMatch(/inspectNativeImagePixels/)
    expect(picker).not.toMatch(/isBlackOrEmptyBitmap\(Buffer\.from\(.*toPNG/)
  })

  it('AC-39.5 AC-39.17 AC-39.18 applying capture settings reregisters hotkey and restarts the watcher', () => {
    const hotkeys: string[] = []
    const watches: string[] = []
    const next = applyCaptureRuntime(
      {
        inbox_dir: '~/Pictures/av-kit',
        hotkey: 'F2',
        copy_to_clipboard: false,
        close_to_tray: true,
      },
      {
        inbox_dir: 'C:/Pictures/inbox',
        hotkey: 'F3',
        copy_to_clipboard: true,
        close_to_tray: false,
      },
      {
        onHotkey: (accelerator) => {
          hotkeys.push(accelerator)
        },
        onWatch: (inboxDir) => {
          watches.push(inboxDir)
        },
      },
    )
    expect(hotkeys).toEqual(['F3'])
    expect(watches).toEqual(['C:/Pictures/inbox'])
    expect(next.close_to_tray).toBe(false)
    expect(next.copy_to_clipboard).toBe(true)
    const parsed = parseCaptureRuntime({
      inbox_dir: 'D:/caps',
      hotkey: 'F8',
      copy_to_clipboard: true,
      close_to_tray: false,
    })
    expect(parsed.hotkey).toBe('F8')
    const index = readFileSync(resolve(repoRoot, 'ui/src/main/index.ts'), 'utf8')
    expect(index).toMatch(/fetchCaptureRuntime/)
    expect(index).toMatch(/applyCaptureRuntime/)
    expect(readFileSync(resolve(repoRoot, 'ui/src/main/capture-runtime.ts'), 'utf8')).toMatch(
      /\/settings\/capture/,
    )
    expect(index).not.toMatch(/const closeToTray = true/)
    expect(index).not.toMatch(/registerCaptureHotkey\('F2'/)
  })

  it('E2E window close quits instead of hiding to tray so Playwright app.close can reap the process', () => {
    const index = readFileSync(resolve(repoRoot, 'ui/src/main/index.ts'), 'utf8')
    const closeStart = index.indexOf("window.on('close'")
    expect(closeStart).toBeGreaterThanOrEqual(0)
    const closeBlock = index.slice(closeStart, closeStart + 420)
    expect(closeBlock).toMatch(/process\.env\.AVKIT_E2E === '1'/)
    expect(closeBlock).toMatch(/\breturn\b/)
    expect(closeBlock).toMatch(/preventDefault/)
  })

  it('E2E publishes a dummy backend URL so renderer fetch does not wait on python READY', () => {
    const index = readFileSync(resolve(repoRoot, 'ui/src/main/index.ts'), 'utf8')
    const marker = "apiBase: 'http://127.0.0.1:9/api/v1'"
    const at = index.indexOf(marker)
    expect(at).toBeGreaterThan(0)
    expect(index.slice(Math.max(0, at - 220), at)).toMatch(/process\.env\.AVKIT_E2E === '1'/)
    expect(index.slice(Math.max(0, at - 80), at + marker.length)).toMatch(/publishBackendReady/)
    expect(index).toMatch(/AVKIT_E2E_BACKEND_DELAY_MS/)
    const quitStart = index.indexOf("app.on('before-quit'")
    expect(quitStart).toBeGreaterThanOrEqual(0)
    const quitBlock = index.slice(quitStart, quitStart + 520)
    expect(quitBlock).toMatch(/process\.env\.AVKIT_E2E === '1'/)
  })

  it('AC-39.16 tray Open inbox folder uses showItemInFolder', () => {
    const tray = readFileSync(resolve(repoRoot, 'ui/src/main/capture-tray.ts'), 'utf8')
    expect(tray).toMatch(/showItemInFolder/)
    expect(tray).not.toMatch(/openPath/)
    expect(tray).toContain('Open inbox folder')
  })
})

describe('capture interactive poll before backend ready', () => {
  afterEach(() => {
    stopInteractivePoll()
    resetBackendIpcState()
    vi.useRealTimers()
    vi.unstubAllGlobals()
  })

  async function leakedUnhandledDuring(work: () => Promise<void>): Promise<unknown[]> {
    const leaked: unknown[] = []
    const onUnhandled = (reason: unknown) => {
      leaked.push(reason)
    }
    process.on('unhandledRejection', onUnhandled)
    try {
      await work()
      await Promise.resolve()
      return leaked
    } finally {
      process.off('unhandledRejection', onUnhandled)
    }
  }

  it('listPendingRequests returns [] instead of throwing when backend is unpublished', async () => {
    resetBackendIpcState()
    await expect(listPendingRequests()).resolves.toEqual([])
  })

  it('startInteractivePoll does not leak unhandledRejection before backend ready', async () => {
    resetBackendIpcState()
    vi.useFakeTimers()
    const leaked = await leakedUnhandledDuring(async () => {
      startInteractivePoll(() => undefined)
      await vi.advanceTimersByTimeAsync(POLL_REQUEST_MS * 2)
    })
    expect(leaked).toEqual([])
  })

  it('listPendingRequests returns [] when published backend GET fails', async () => {
    resetBackendIpcState()
    publishBackendReady({ apiBase: 'http://127.0.0.1:9/api/v1', token: 'e2e-token' })
    vi.stubGlobal(
      'fetch',
      vi.fn(() => Promise.reject(new Error('connection refused'))),
    )
    await expect(listPendingRequests()).resolves.toEqual([])
  })

  it('startInteractivePoll does not leak unhandledRejection when pending GET fails', async () => {
    resetBackendIpcState()
    publishBackendReady({ apiBase: 'http://127.0.0.1:9/api/v1', token: 'e2e-token' })
    vi.stubGlobal(
      'fetch',
      vi.fn(() => Promise.reject(new Error('connection refused'))),
    )
    vi.useFakeTimers()
    const leaked = await leakedUnhandledDuring(async () => {
      startInteractivePoll(() => undefined)
      await vi.advanceTimersByTimeAsync(POLL_REQUEST_MS)
    })
    expect(leaked).toEqual([])
  })

  it('startInteractivePoll delivers the first pending row after a successful GET', async () => {
    resetBackendIpcState()
    publishBackendReady({ apiBase: 'http://127.0.0.1:9/api/v1', token: 'e2e-token' })
    vi.stubGlobal(
      'fetch',
      vi.fn(() =>
        Promise.resolve(
          new Response(JSON.stringify({ items: [{ id: 'req-1', status: 'pending' }] }), {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
          }),
        ),
      ),
    )
    vi.useFakeTimers()
    const seen: string[] = []
    startInteractivePoll((row) => {
      seen.push(row.id)
    })
    await vi.advanceTimersByTimeAsync(POLL_REQUEST_MS)
    expect(seen).toEqual(['req-1'])
  })

  it('finalizeCapturedPng notifies even when backend is unpublished', async () => {
    resetBackendIpcState()
    const notify = vi.fn()
    await expect(finalizeCapturedPng('C:/caps/a.png', 'gui', true, notify)).resolves.toBeUndefined()
    expect(notify).toHaveBeenCalledTimes(1)
  })

  it('fetchCaptureRuntime returns null when settings GET fails', async () => {
    resetBackendIpcState()
    publishBackendReady({ apiBase: 'http://127.0.0.1:9/api/v1', token: 'e2e-token' })
    vi.stubGlobal(
      'fetch',
      vi.fn(() => Promise.reject(new Error('connection refused'))),
    )
    await expect(fetchCaptureRuntime()).resolves.toBeNull()
  })

  it('picker publish path calls finalizeCapturedPng after claiming the inbox name', () => {
    const picker = readFileSync(resolve(repoRoot, 'ui/src/main/capture-picker.ts'), 'utf8')
    expect(picker).toMatch(/finalizeCapturedPng/)
    expect(picker).not.toMatch(/await registerCapturePng\(/)
  })
})

describe('MEU-67 inbox watcher invariant (AC-67.13)', () => {
  it('AC-67.13 the backup folder, a temporary sibling and a non-PNG annotated copy never notify', async () => {
    const { shouldNotifyInboxChange } = await import('../../src/main/capture-inbox-watch')
    // BACKUP_DIR_DEFAULT_NAME and TMP_SUFFIX from services/capture.py (ui/src/main unchanged).
    expect(shouldNotifyInboxChange('.avkit-backup')).toBe(false)
    expect(shouldNotifyInboxChange('2026-10-03_12-00-00.png.avkit-tmp')).toBe(false)
    expect(shouldNotifyInboxChange('2026-10-03_12-00-00.annotated.jpg')).toBe(false)
    expect(shouldNotifyInboxChange('2026-10-03_12-00-00.annotated.webp')).toBe(false)
    expect(shouldNotifyInboxChange('2026-10-03_12-00-00.annotated.png')).toBe(false)
    expect(shouldNotifyInboxChange('photo-converted.png')).toBe(true)
  })
})

describe('MEU-84 E2E_SHELL_LOG (AC-84.6)', () => {
  const shellGlobal = globalThis as { __AVKIT_E2E_SHELL_LOG__?: unknown }
  const savedE2e = process.env.AVKIT_E2E

  afterEach(() => {
    if (savedE2e === undefined) {
      delete process.env.AVKIT_E2E
    } else {
      process.env.AVKIT_E2E = savedE2e
    }
    delete shellGlobal.__AVKIT_E2E_SHELL_LOG__
    vi.resetModules()
  })

  it('AC-84.6 recordE2eShell appends {op, target} in call order', async () => {
    const mod = await import('../../src/main/e2e-shell')
    mod.e2eShellLog.length = 0
    mod.recordE2eShell('openPath', 'C:/e2e/a.annotated.png')
    mod.recordE2eShell('showItemInFolder', 'C:/e2e/a.png')
    expect(mod.e2eShellLog).toEqual([
      { op: 'openPath', target: 'C:/e2e/a.annotated.png' },
      { op: 'showItemInFolder', target: 'C:/e2e/a.png' },
    ])
  })

  it('AC-84.6 the log is on globalThis only when AVKIT_E2E is 1', async () => {
    delete process.env.AVKIT_E2E
    delete shellGlobal.__AVKIT_E2E_SHELL_LOG__
    vi.resetModules()
    await import('../../src/main/e2e-shell')
    expect(shellGlobal.__AVKIT_E2E_SHELL_LOG__).toBeUndefined()
    process.env.AVKIT_E2E = '1'
    vi.resetModules()
    const mod = await import('../../src/main/e2e-shell')
    expect(shellGlobal.__AVKIT_E2E_SHELL_LOG__).toBe(mod.e2eShellLog)
  })

  it('AC-84.6 the index.ts E2E branches record the target and never call shell', () => {
    const index = readFileSync(resolve(repoRoot, 'ui/src/main/index.ts'), 'utf8')
    for (const op of ['openPath', 'showItemInFolder'] as const) {
      const start = index.indexOf(`    ${op}: async (target: string) => {`)
      expect(start, op).toBeGreaterThan(-1)
      const handler = index.slice(start, index.indexOf('\n    },', start))
      const branch = handler.match(/if \(process\.env\.AVKIT_E2E === '1'\) \{([\s\S]*?)\n {6}\}/)?.[1] ?? ''
      expect(branch, op).toContain(`recordE2eShell('${op}', target)`)
      expect(branch, op).toMatch(/\breturn\b/)
      expect(branch, op).not.toMatch(/\bshell\./)
      const after = handler.slice(handler.indexOf(branch) + branch.length)
      expect(after, op).toContain(`shell.${op}(target)`)
    }
  })
})
