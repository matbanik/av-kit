import { spawn } from 'node:child_process'
import fs from 'node:fs'
import { mkdtempSync, readdirSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { basename, dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import {
  captureRegionFromGui,
  getPickerSpawn,
  isPickerInFlight,
  PICKER_EXIT_CANCEL,
  PICKER_EXIT_CONFIRM,
  PICKER_EXIT_ERROR,
  PICKER_READY_MARKER,
  PICKER_STAGING_PREFIX,
  resetPickerState,
  resolvePickerExePath,
  runRegionPicker,
  setPickerSpawn,
} from '../../src/main/capture-picker'
import {
  resetInboxWatchState,
  shouldNotifyInboxChange,
} from '../../src/main/capture-inbox-watch'
import { registerFileName, runInteractiveTick } from '../../src/main/capture-register'
import { publishBackendReady, resetBackendIpcState } from '../../src/main/ipc'
import { createFakeSpawn, type FakeSpawn } from './helpers/fake-picker-child'
import { __resetElectronStub, __setNativeImageFactory } from './helpers/electron-stub'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')

const flush = (): Promise<void> => new Promise((r) => setImmediate(r))

function fakeWindow(): { window: unknown; sent: string[] } {
  const sent: string[] = []
  return {
    sent,
    window: {
      isDestroyed: () => false,
      webContents: {
        send: (channel: string) => {
          sent.push(channel)
        },
      },
    },
  }
}

/** The `--out` path the module handed the helper on its Nth spawn. */
function stagedPath(fake: FakeSpawn, index = 0): string {
  const args = fake.calls[index]?.args ?? []
  const at = args.indexOf('--out')
  expect(at, 'spawn argv must carry --out').toBeGreaterThanOrEqual(0)
  const path = args[at + 1]
  expect(typeof path).toBe('string')
  return String(path)
}

function writeStagedPng(path: string): void {
  writeFileSync(path, Buffer.from([0x89, 0x50, 0x4e, 0x47, 1, 2, 3, 4, 5, 6]))
}

describe('MEU-40 native region picker sidecar', () => {
  let inbox: string
  let fake: FakeSpawn

  beforeEach(() => {
    inbox = mkdtempSync(join(tmpdir(), 'avkit-picker-'))
    fake = createFakeSpawn()
    setPickerSpawn(fake.fn as never)
    resetPickerState()
    resetInboxWatchState()
    resetBackendIpcState()
    __resetElectronStub()
    delete process.env.AVKIT_E2E
    delete process.env.AVKIT_REGION_PICKER_PATH
  })

  afterEach(() => {
    setPickerSpawn(null)
    resetPickerState()
    resetInboxWatchState()
    resetBackendIpcState()
    __resetElectronStub()
    vi.restoreAllMocks()
    vi.unstubAllGlobals()
    vi.useRealTimers()
    delete process.env.AVKIT_E2E
    delete process.env.AVKIT_REGION_PICKER_PATH
    fs.rmSync(inbox, { recursive: true, force: true })
  })

  describe('AC-40.5 exit-code classification and path resolution', () => {
    it('defaults to the real child_process.spawn', () => {
      setPickerSpawn(null)
      expect(getPickerSpawn()).toBe(spawn)
    })

    it('honours the AVKIT_REGION_PICKER_PATH override', () => {
      process.env.AVKIT_REGION_PICKER_PATH = 'C:/over/ride/picker.exe'
      expect(resolvePickerExePath()).toBe('C:/over/ride/picker.exe')
    })

    it('resolves the dev tree path when no override is set', () => {
      const path = resolvePickerExePath()
      expect(path.replace(/\\/g, '/')).toMatch(/native\/region-picker\/publish\/avkit-region-picker\.exe$/)
    })

    it(`maps PICKER_EXIT_CONFIRM (${PICKER_EXIT_CONFIRM}) to a confirm carrying the staged path`, async () => {
      const staging = join(inbox, `${PICKER_STAGING_PREFIX}abc.tmp`)
      const promise = runRegionPicker(staging)
      await flush()
      writeStagedPng(staging)
      fake.child().ready()
      fake.child().finish(PICKER_EXIT_CONFIRM)
      await expect(promise).resolves.toEqual({ kind: 'confirm', path: staging })
    })

    it(`maps PICKER_EXIT_CANCEL (${PICKER_EXIT_CANCEL}) to a cancel`, async () => {
      const staging = join(inbox, `${PICKER_STAGING_PREFIX}def.tmp`)
      const promise = runRegionPicker(staging)
      await flush()
      fake.child().ready()
      fake.child().finish(PICKER_EXIT_CANCEL)
      await expect(promise).resolves.toEqual({ kind: 'cancel' })
    })

    it(`maps PICKER_EXIT_ERROR (${PICKER_EXIT_ERROR}) and an off-contract code to blocked`, async () => {
      for (const code of [PICKER_EXIT_ERROR, 137]) {
        const staging = join(inbox, `${PICKER_STAGING_PREFIX}${code}.tmp`)
        const promise = runRegionPicker(staging)
        await flush()
        const child = fake.calls[fake.calls.length - 1]?.child
        child?.ready()
        child?.finish(code)
        const outcome = await promise
        expect(outcome.kind, `exit ${code}`).toBe('blocked')
      }
    })

    it('never posts to /captures when the picker is blocked', async () => {
      publishBackendReady({ apiBase: 'http://127.0.0.1:9/api/v1', token: 't' })
      const fetchSpy = vi.fn(() => Promise.resolve(new Response('{}', { status: 200 })))
      vi.stubGlobal('fetch', fetchSpy)
      const promise = captureRegionFromGui({
        inboxDir: inbox,
        copyToClipboard: false,
        source: 'gui',
        window: fakeWindow().window as never,
      })
      await flush()
      fake.child().ready()
      fake.child().finish(PICKER_EXIT_ERROR)
      await expect(promise).resolves.toBeNull()
      expect(fetchSpy).not.toHaveBeenCalled()
      expect(readdirSync(inbox).filter((n) => n.endsWith('.png'))).toEqual([])
    })

    it('classifies a missing executable as blocked without throwing into the F2 handler', async () => {
      const staging = join(inbox, `${PICKER_STAGING_PREFIX}missing.tmp`)
      const promise = runRegionPicker(staging)
      await flush()
      fake.child().failToSpawn(Object.assign(new Error('spawn ENOENT'), { code: 'ENOENT' }))
      await expect(promise).resolves.toMatchObject({ kind: 'blocked' })
    })
  })

  describe('AC-40.6 lossless publication', () => {
    it('publishes by claiming a name with linkSync and unlinks the staging file', async () => {
      publishBackendReady({ apiBase: 'http://127.0.0.1:9/api/v1', token: 't' })
      const bodies: string[] = []
      vi.stubGlobal(
        'fetch',
        vi.fn((_url: string, init: RequestInit) => {
          bodies.push(String(init.body))
          return Promise.resolve(new Response('{}', { status: 201 }))
        }),
      )
      const linkSpy = vi.spyOn(fs, 'linkSync')
      const renameSpy = vi.spyOn(fs, 'renameSync')
      const copySpy = vi.spyOn(fs, 'copyFileSync')
      const writeSpy = vi.spyOn(fs, 'writeFileSync')
      const win = fakeWindow()

      const promise = captureRegionFromGui({
        inboxDir: inbox,
        copyToClipboard: false,
        source: 'gui',
        window: win.window as never,
      })
      await flush()
      const staging = stagedPath(fake)
      expect(basename(staging).startsWith(PICKER_STAGING_PREFIX)).toBe(true)
      expect(dirname(staging)).toBe(inbox)
      writeStagedPng(staging)
      fake.child().ready()
      fake.child().finish(PICKER_EXIT_CONFIRM)

      const dest = await promise
      expect(dest).not.toBeNull()
      expect(linkSpy).toHaveBeenCalled()
      expect(renameSpy).not.toHaveBeenCalled()
      expect(copySpy).not.toHaveBeenCalled()
      for (const call of writeSpy.mock.calls) {
        expect(String(call[0])).not.toBe(dest)
      }
      expect(fs.existsSync(staging)).toBe(false)
      expect(fs.existsSync(String(dest))).toBe(true)
      expect(bodies.join('')).toContain('"mode":"register"')
      expect(win.sent.filter((c) => c === 'captures:inbox-changed')).toHaveLength(1)
    })

    it('blocks an all-black staged PNG: no inbox png, no register, staging unlinked', async () => {
      publishBackendReady({ apiBase: 'http://127.0.0.1:9/api/v1', token: 't' })
      const fetchSpy = vi.fn(() => Promise.resolve(new Response('{}', { status: 201 })))
      vi.stubGlobal('fetch', fetchSpy)
      __setNativeImageFactory(() => ({
        isEmpty: () => false,
        getSize: () => ({ width: 2, height: 2 }),
        toBitmap: () => Buffer.alloc(16, 0),
        toPNG: () => Buffer.alloc(4),
      }))

      const promise = captureRegionFromGui({
        inboxDir: inbox,
        copyToClipboard: false,
        source: 'gui',
        window: fakeWindow().window as never,
      })
      await flush()
      const staging = stagedPath(fake)
      writeStagedPng(staging)
      fake.child().ready()
      fake.child().finish(PICKER_EXIT_CONFIRM)

      await expect(promise).resolves.toBeNull()
      expect(readdirSync(inbox).filter((n) => n.endsWith('.png'))).toEqual([])
      expect(fs.existsSync(staging)).toBe(false)
      expect(fetchSpy).not.toHaveBeenCalled()
    })

    it('claims _2 rather than overwriting when the second-resolution name is taken', async () => {
      // Pin the clock: the taken name and the publication must fall in the same second.
      vi.useFakeTimers({ toFake: ['Date'] })
      vi.setSystemTime(new Date(2026, 9, 17, 1, 26, 16, 999))
      publishBackendReady({ apiBase: 'http://127.0.0.1:9/api/v1', token: 't' })
      vi.stubGlobal('fetch', vi.fn(() => Promise.resolve(new Response('{}', { status: 201 }))))
      const taken = join(inbox, registerFileName())
      writeFileSync(taken, 'the first capture of this second')

      const promise = captureRegionFromGui({
        inboxDir: inbox,
        copyToClipboard: false,
        source: 'gui',
        window: fakeWindow().window as never,
      })
      await flush()
      const staging = stagedPath(fake)
      writeStagedPng(staging)
      fake.child().ready()
      fake.child().finish(PICKER_EXIT_CONFIRM)

      const dest = String(await promise)
      expect(dest).not.toBe(taken)
      expect(basename(dest)).toMatch(/_2\.png$/)
      expect(fs.readFileSync(taken, 'utf8')).toBe('the first capture of this second')
    })

    it('keeps the PNG when POST /captures rejects and never unlinks it', async () => {
      publishBackendReady({ apiBase: 'http://127.0.0.1:9/api/v1', token: 't' })
      vi.stubGlobal('fetch', vi.fn(() => Promise.reject(new Error('backend down'))))
      const unlinkSpy = vi.spyOn(fs, 'unlinkSync')

      const promise = captureRegionFromGui({
        inboxDir: inbox,
        copyToClipboard: false,
        source: 'gui',
        window: fakeWindow().window as never,
      })
      await flush()
      const staging = stagedPath(fake)
      writeStagedPng(staging)
      fake.child().ready()
      fake.child().finish(PICKER_EXIT_CONFIRM)

      const dest = String(await promise)
      expect(fs.existsSync(dest)).toBe(true)
      for (const call of unlinkSpy.mock.calls) {
        expect(String(call[0])).not.toBe(dest)
      }
    })

    it('shouldNotifyInboxChange ignores the staging name and non-png files', () => {
      expect(shouldNotifyInboxChange(`${PICKER_STAGING_PREFIX}9f2.tmp`)).toBe(false)
      expect(shouldNotifyInboxChange('2026-08-27_10-00-00.png')).toBe(true)
      expect(shouldNotifyInboxChange('notes.txt')).toBe(false)
      expect(shouldNotifyInboxChange('2026-08-27_10-00-00-annotated.png')).toBe(false)
    })
  })

  describe('AC-40.7 single in-flight picker', () => {
    it('two rapid F2 fires produce exactly one spawn', async () => {
      publishBackendReady({ apiBase: 'http://127.0.0.1:9/api/v1', token: 't' })
      vi.stubGlobal('fetch', vi.fn(() => Promise.resolve(new Response('{}', { status: 201 }))))
      const win = fakeWindow().window as never

      const first = captureRegionFromGui({
        inboxDir: inbox,
        copyToClipboard: false,
        source: 'hotkey',
        window: win,
      })
      await flush()
      expect(isPickerInFlight()).toBe(true)
      const second = await captureRegionFromGui({
        inboxDir: inbox,
        copyToClipboard: false,
        source: 'hotkey',
        window: win,
      })
      expect(second).toBeNull()
      expect(fake.calls).toHaveLength(1)

      fake.child().ready()
      fake.child().finish(PICKER_EXIT_CANCEL)
      await first
      expect(isPickerInFlight()).toBe(false)
    })
  })

  describe('AC-40.11 conditional AVKIT_E2E short-circuit', () => {
    it('does not spawn under AVKIT_E2E while the override is unset', async () => {
      process.env.AVKIT_E2E = '1'
      const win = fakeWindow()
      await expect(
        captureRegionFromGui({
          inboxDir: inbox,
          copyToClipboard: false,
          source: 'gui',
          window: win.window as never,
        }),
      ).resolves.toBeNull()
      expect(fake.calls).toHaveLength(0)
      expect(win.sent).toContain('captures:inbox-changed')
    })

    it('runs the real spawn chain under AVKIT_E2E once the override supplies a path', async () => {
      process.env.AVKIT_E2E = '1'
      process.env.AVKIT_REGION_PICKER_PATH = 'C:/stub/avkit-region-picker-stub.exe'
      publishBackendReady({ apiBase: 'http://127.0.0.1:9/api/v1', token: 't' })
      vi.stubGlobal('fetch', vi.fn(() => Promise.resolve(new Response('{}', { status: 201 }))))

      const promise = captureRegionFromGui({
        inboxDir: inbox,
        copyToClipboard: false,
        source: 'gui',
        window: fakeWindow().window as never,
      })
      await flush()
      expect(fake.calls).toHaveLength(1)
      expect(fake.calls[0]?.exe).toBe('C:/stub/avkit-region-picker-stub.exe')
      const staging = stagedPath(fake)
      writeStagedPng(staging)
      fake.child().ready()
      fake.child().finish(PICKER_EXIT_CONFIRM)
      expect(String(await promise)).toMatch(/\.png$/)
    })

    it('every AVKIT_E2E line in capture-picker.ts also names the override', () => {
      const source = fs.readFileSync(resolve(repoRoot, 'ui/src/main/capture-picker.ts'), 'utf8')
      const lines = source.split('\n').filter((l) => l.includes('AVKIT_E2E') && !l.trim().startsWith('//'))
      expect(lines.length).toBeGreaterThan(0)
      for (const line of lines) {
        expect(line, 'unconditional AVKIT_E2E short-circuit').toContain('AVKIT_REGION_PICKER_PATH')
      }
      expect(source).toContain(PICKER_READY_MARKER)
    })
  })

  describe('AC-40.8 interactive MCP path uses the picker', () => {
    it('a pending request that confirms completes with the published inbox path', async () => {
      publishBackendReady({ apiBase: 'http://127.0.0.1:9/api/v1', token: 't' })
      const posted: string[] = []
      vi.stubGlobal(
        'fetch',
        vi.fn((url: string) => {
          posted.push(String(url))
          return Promise.resolve(new Response('{}', { status: 201 }))
        }),
      )
      const win = fakeWindow().window as never
      const tick = runInteractiveTick(
        { kind: 'ok', rows: [{ id: 'req-1', status: 'Pending' }] },
        {
          capture: () =>
            captureRegionFromGui({
              inboxDir: inbox,
              copyToClipboard: false,
              source: 'gui',
              window: win,
              register: false,
            }),
          notify: () => undefined,
        },
      )
      await flush()
      const staging = stagedPath(fake)
      writeStagedPng(staging)
      fake.child().ready()
      fake.child().finish(PICKER_EXIT_CONFIRM)
      await tick

      const completes = posted.filter((u) => u.endsWith('/complete'))
      expect(completes).toEqual(['http://127.0.0.1:9/api/v1/captures/requests/req-1/complete'])
      expect(posted.filter((u) => u.endsWith('/cancel'))).toEqual([])
    })

    it('a blocked picker cancels and never completes a nonexistent file', async () => {
      publishBackendReady({ apiBase: 'http://127.0.0.1:9/api/v1', token: 't' })
      const posted: string[] = []
      vi.stubGlobal(
        'fetch',
        vi.fn((url: string) => {
          posted.push(String(url))
          return Promise.resolve(new Response('{}', { status: 201 }))
        }),
      )
      const win = fakeWindow().window as never
      const tick = runInteractiveTick(
        { kind: 'ok', rows: [{ id: 'req-2', status: 'Pending' }] },
        {
          capture: () =>
            captureRegionFromGui({
              inboxDir: inbox,
              copyToClipboard: false,
              source: 'gui',
              window: win,
              register: false,
            }),
          notify: () => undefined,
        },
      )
      await flush()
      fake.child().ready()
      fake.child().finish(PICKER_EXIT_ERROR)
      await tick

      expect(posted.filter((u) => u.endsWith('/complete'))).toEqual([])
      expect(posted.filter((u) => u.endsWith('/cancel'))).toEqual([
        'http://127.0.0.1:9/api/v1/captures/requests/req-2/cancel',
      ])
    })
  })
})
