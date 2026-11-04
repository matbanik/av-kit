import fs from 'node:fs'
import { mkdirSync, mkdtempSync, readdirSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { basename, join } from 'node:path'

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import {
  captureRegionFromGui,
  getLastPickerOutput,
  getPickerParserState,
  isPickerInFlight,
  PICKER_EXIT_CANCEL,
  PICKER_EXIT_CONFIRM,
  PICKER_EXIT_ERROR,
  PICKER_INTERACTION_TIMEOUT_MS,
  PICKER_KILL_GRACE_MS,
  PICKER_LINE_MAX_BYTES,
  PICKER_LOG_MAX_BYTES,
  PICKER_READY_MARKER,
  PICKER_STARTUP_TIMEOUT_MS,
  resetPickerState,
  SCREEN_CAPTURE_BLOCKED,
  setPickerLog,
  setPickerSpawn,
} from '../../src/main/capture-picker'
import {
  computeInboxNotification,
  onInboxListing,
  releaseInboxPath,
  reserveInboxPath,
  resetInboxWatchState,
  seedInboxBaseline,
  settleInboxPath,
} from '../../src/main/capture-inbox-watch'
import {
  clearCompletionJournal,
  registerFileName,
  runInteractiveTick,
  type PollResult,
} from '../../src/main/capture-register'
import { notifyUser, resetNotifyUserDeps, setNotifyUserDeps } from '../../src/main/notify-user'
import { publishBackendReady, resetBackendIpcState } from '../../src/main/ipc'
import { createFakeSpawn, type FakeSpawn } from './helpers/fake-picker-child'
import {
  __emitAppEvent,
  __resetElectronStub,
  __setNativeImageFactory,
  app,
  Notification,
} from './helpers/electron-stub'

const flush = (): Promise<void> => new Promise((r) => setImmediate(r))

/** Fake only the clock: `flush()` must keep working, so `setImmediate` stays real. */
const FAKED_TIMERS = ['setTimeout', 'clearTimeout', 'setInterval', 'clearInterval'] as const

type Sent = { window: unknown; sent: string[] }

function fakeWindow(): Sent {
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

function writeStagedPng(path: string): void {
  writeFileSync(path, Buffer.from([0x89, 0x50, 0x4e, 0x47, 1, 2, 3, 4, 5, 6]))
}

describe('MEU-40 picker lifecycle, spawn hygiene and publication', () => {
  let inbox: string
  let fake: FakeSpawn
  let logs: string[]

  beforeEach(() => {
    inbox = mkdtempSync(join(tmpdir(), 'avkit-life-'))
    fake = createFakeSpawn()
    logs = []
    setPickerSpawn(fake.fn as never)
    setPickerLog((line) => {
      logs.push(line)
    })
    resetPickerState()
    resetInboxWatchState()
    resetBackendIpcState()
    resetNotifyUserDeps()
    __resetElectronStub()
    delete process.env.AVKIT_E2E
    delete process.env.AVKIT_REGION_PICKER_PATH
    publishBackendReady({ apiBase: 'http://127.0.0.1:9/api/v1', token: 't' })
    vi.stubGlobal(
      'fetch',
      vi.fn(() => Promise.resolve(new Response('{}', { status: 201 }))),
    )
  })

  afterEach(() => {
    setPickerSpawn(null)
    setPickerLog(null)
    resetPickerState()
    resetInboxWatchState()
    resetBackendIpcState()
    resetNotifyUserDeps()
    __resetElectronStub()
    vi.useRealTimers()
    vi.restoreAllMocks()
    vi.unstubAllGlobals()
    fs.rmSync(inbox, { recursive: true, force: true })
  })

  function fire(): Promise<string | null> {
    return captureRegionFromGui({
      inboxDir: inbox,
      copyToClipboard: false,
      source: 'hotkey',
      window: fakeWindow().window as never,
    })
  }

  function terminalLines(): string[] {
    return logs.filter((l) => /\[Capture\] picker (confirm|cancel|blocked)/.test(l))
  }

  function stagingArg(index = 0): string {
    const args = fake.calls[index]?.args ?? []
    return String(args[args.indexOf('--out') + 1])
  }

  describe('AC-40.28 helper lifecycle totality', () => {
    it('exit 0 with a staged file confirms exactly once and keeps the staged bytes', async () => {
      const promise = fire()
      await flush()
      writeStagedPng(stagingArg())
      fake.child().ready()
      fake.child().finish(PICKER_EXIT_CONFIRM)
      const dest = await promise

      expect(dest).not.toBeNull()
      expect(terminalLines()).toHaveLength(1)
      expect(terminalLines()[0]).toContain('confirm')
      expect(isPickerInFlight()).toBe(false)
    })

    it('exit 2 cancels: one terminal state, no error notice, no register, staging unlinked', async () => {
      const notices: string[] = []
      setNotifyUserDeps({
        balloon: (o) => {
          notices.push(o.body)
          return true
        },
      })
      const fetchSpy = globalThis.fetch as unknown as ReturnType<typeof vi.fn>
      const promise = fire()
      await flush()
      const staging = stagingArg()
      writeStagedPng(staging)
      fake.child().ready()
      fake.child().finish(PICKER_EXIT_CANCEL)

      await expect(promise).resolves.toBeNull()
      expect(terminalLines()).toHaveLength(1)
      expect(terminalLines()[0]).toContain('cancel')
      expect(notices).toEqual([])
      expect(fetchSpy).not.toHaveBeenCalled()
      expect(fs.existsSync(staging)).toBe(false)
      expect(isPickerInFlight()).toBe(false)
    })

    const nonConfirm: [string, () => void][] = []

    it.each([
      ['declared error exit', PICKER_EXIT_ERROR, null],
      ['off-contract exit', 137, null],
      ['killed by signal with a null code', null, 'SIGTERM'],
    ])('%s settles blocked exactly once and unlinks staging', async (_label, code, signal) => {
      const promise = fire()
      await flush()
      const staging = stagingArg()
      writeStagedPng(staging)
      fake.child().ready()
      fake.child().finish(code as number | null, signal as string | null)

      await expect(promise).resolves.toBeNull()
      expect(terminalLines()).toHaveLength(1)
      expect(terminalLines()[0]).toContain('blocked')
      expect(fs.existsSync(staging)).toBe(false)
      expect(isPickerInFlight()).toBe(false)
      expect(nonConfirm).toHaveLength(0)
    })

    it('a spawn error event settles blocked without throwing into the caller', async () => {
      const promise = fire()
      await flush()
      const staging = stagingArg()
      writeStagedPng(staging)
      fake.child().failToSpawn(Object.assign(new Error('spawn EACCES'), { code: 'EACCES' }))

      await expect(promise).resolves.toBeNull()
      expect(terminalLines()).toHaveLength(1)
      expect(fs.existsSync(staging)).toBe(false)
      expect(isPickerInFlight()).toBe(false)
    })

    it('a confirm whose staged file is missing is blocked, not published', async () => {
      const promise = fire()
      await flush()
      fake.child().ready()
      fake.child().finish(PICKER_EXIT_CONFIRM)

      await expect(promise).resolves.toBeNull()
      expect(terminalLines()).toHaveLength(1)
      expect(terminalLines()[0]).toContain('blocked')
      expect(readdirSync(inbox).filter((n) => n.endsWith('.png'))).toEqual([])
    })

    it('a confirm whose staged file is zero bytes is blocked, not published', async () => {
      const promise = fire()
      await flush()
      const staging = stagingArg()
      writeFileSync(staging, Buffer.alloc(0))
      fake.child().ready()
      fake.child().finish(PICKER_EXIT_CONFIRM)

      await expect(promise).resolves.toBeNull()
      expect(terminalLines()[0]).toContain('blocked')
      expect(readdirSync(inbox).filter((n) => n.endsWith('.png'))).toEqual([])
      expect(fs.existsSync(staging)).toBe(false)
    })

    it(`no readiness within PICKER_STARTUP_TIMEOUT_MS (${PICKER_STARTUP_TIMEOUT_MS}) kills and blocks`, async () => {
      vi.useFakeTimers({ toFake: [...FAKED_TIMERS] })
      const promise = fire()
      await flush()
      const staging = stagingArg()
      writeStagedPng(staging)

      await vi.advanceTimersByTimeAsync(PICKER_STARTUP_TIMEOUT_MS + 1)
      expect(fake.child().killed).toBe(true)
      fake.child().finish(null, 'SIGTERM')

      await expect(promise).resolves.toBeNull()
      expect(terminalLines()).toHaveLength(1)
      expect(terminalLines()[0]).toMatch(/failed to start/)
      expect(fs.existsSync(staging)).toBe(false)
      expect(isPickerInFlight()).toBe(false)
    })

    it(`no exit within PICKER_INTERACTION_TIMEOUT_MS (${PICKER_INTERACTION_TIMEOUT_MS}) of readiness kills and blocks`, async () => {
      vi.useFakeTimers({ toFake: [...FAKED_TIMERS] })
      const promise = fire()
      await flush()
      const staging = stagingArg()
      writeStagedPng(staging)
      fake.child().ready()
      await flush()

      await vi.advanceTimersByTimeAsync(PICKER_STARTUP_TIMEOUT_MS + 1)
      expect(terminalLines()).toHaveLength(0)

      await vi.advanceTimersByTimeAsync(PICKER_INTERACTION_TIMEOUT_MS + 1)
      expect(fake.child().killed).toBe(true)
      fake.child().finish(null, 'SIGKILL')

      await expect(promise).resolves.toBeNull()
      expect(terminalLines()).toHaveLength(1)
      expect(terminalLines()[0]).toMatch(/timed out/)
      expect(fs.existsSync(staging)).toBe(false)
      expect(isPickerInFlight()).toBe(false)
    })

    it('app.will-quit mid-flight kills the child and leaves no orphan', async () => {
      const promise = fire()
      await flush()
      const staging = stagingArg()
      writeStagedPng(staging)
      fake.child().ready()
      await flush()

      __emitAppEvent('will-quit')
      expect(fake.child().killed).toBe(true)
      fake.child().finish(null, 'SIGTERM')

      await expect(promise).resolves.toBeNull()
      expect(terminalLines()).toHaveLength(1)
      expect(fs.existsSync(staging)).toBe(false)
      expect(isPickerInFlight()).toBe(false)
    })
  })

  describe('AC-40.29 spawn hygiene', () => {
    it('spawns with shell:false, windowsHide:true, piped stdio and an argv array', async () => {
      const promise = fire()
      await flush()
      const call = fake.calls[0]
      expect(call?.options.shell).toBe(false)
      expect(call?.options.windowsHide).toBe(true)
      expect(call?.options.stdio).toEqual(['ignore', 'pipe', 'pipe'])
      expect(Array.isArray(call?.args)).toBe(true)
      expect(call?.args[0]).toBe('--out')

      fake.child().finish(PICKER_EXIT_CANCEL)
      await promise
    })

    it('passes an exe and an --out path containing a space, an &, a quote and non-ASCII unmangled', async () => {
      const exe = "C:/Program Files/av & kit/pick'er/région-picker.exe"
      process.env.AVKIT_REGION_PICKER_PATH = exe
      const awkward = join(inbox, "sn ap & sho't-dossié")
      mkdirSync(awkward, { recursive: true })

      const promise = captureRegionFromGui({
        inboxDir: awkward,
        copyToClipboard: false,
        source: 'gui',
        window: fakeWindow().window as never,
      })
      await flush()
      const call = fake.calls[0]
      expect(call?.exe).toBe(exe)
      const out = String(call?.args[call.args.indexOf('--out') + 1])
      expect(out).toContain("sn ap & sho't-dossié")
      expect(out).not.toContain('"')
      expect(out).not.toContain('^')

      fake.child().finish(PICKER_EXIT_CANCEL)
      await promise
      delete process.env.AVKIT_REGION_PICKER_PATH
    })

    it(`drains both pipes and keeps only the last PICKER_LOG_MAX_BYTES (${PICKER_LOG_MAX_BYTES}) bytes`, async () => {
      const promise = fire()
      await flush()
      const child = fake.child()
      const noisy = 'x'.repeat(1024)
      for (let i = 0; i < Math.ceil(PICKER_LOG_MAX_BYTES / 1024) + 8; i += 1) {
        child.complain(`${i}:${noisy}`)
      }
      child.say('tail-of-stdout')
      await flush()
      child.finish(PICKER_EXIT_ERROR)
      await promise

      const output = getLastPickerOutput()
      expect(output.stderr.length).toBeLessThanOrEqual(PICKER_LOG_MAX_BYTES)
      expect(output.stderr.endsWith(`${noisy}\n`)).toBe(true)
      expect(output.stderr.startsWith('0:')).toBe(false)
      expect(output.stdout).toContain('tail-of-stdout')
    })

    it('readiness matches only an anchored whole line, and only the first occurrence', async () => {
      vi.useFakeTimers({ toFake: [...FAKED_TIMERS] })
      const promise = fire()
      await flush()
      const child = fake.child()
      child.complain(`${PICKER_READY_MARKER} on stderr does not count`)
      child.say(`not ${PICKER_READY_MARKER} yet`)
      child.say(`${PICKER_READY_MARKER}ish`)
      await flush()

      await vi.advanceTimersByTimeAsync(PICKER_STARTUP_TIMEOUT_MS + 1)
      await expect(promise).resolves.toBeNull()
      expect(terminalLines()[0]).toMatch(/failed to start/)
    })

    it('kills gracefully, then SIGKILL after PICKER_KILL_GRACE_MS', async () => {
      vi.useFakeTimers({ toFake: [...FAKED_TIMERS] })
      const promise = fire()
      await flush()
      fake.child().ready()
      await flush()

      __emitAppEvent('will-quit')
      expect(fake.child().killSignals).toEqual([undefined])

      await vi.advanceTimersByTimeAsync(PICKER_KILL_GRACE_MS + 1)
      expect(fake.child().killSignals).toContain('SIGKILL')

      fake.child().finish(null, 'SIGKILL')
      await promise
    })
  })

  describe('AC-40.30 publication races and failures', () => {
    async function publishOnce(): Promise<string> {
      const promise = fire()
      await flush()
      const staging = stagingArg()
      writeStagedPng(staging)
      fake.child().ready()
      fake.child().finish(PICKER_EXIT_CONFIRM)
      const dest = await promise
      expect(dest).not.toBeNull()
      return String(dest)
    }

    it('(a) walks to _3 when the first two names are taken', async () => {
      // Pin the clock: the taken names and the publication must fall in the same second.
      vi.useFakeTimers({ toFake: ['Date'] })
      vi.setSystemTime(new Date(2026, 9, 17, 1, 26, 16, 999))
      const base = registerFileName().replace(/\.png$/, '')
      writeFileSync(join(inbox, `${base}.png`), 'a')
      writeFileSync(join(inbox, `${base}_2.png`), 'b')
      const dest = await publishOnce()
      expect(basename(dest)).toBe(`${base}_3.png`)
    })

    it('(a) does not swallow a non-EEXIST link error as a collision', async () => {
      const linkSpy = vi.spyOn(fs, 'linkSync').mockImplementation(() => {
        throw Object.assign(new Error('EACCES: permission denied'), {
          code: 'EACCES',
        })
      })
      const promise = fire()
      await flush()
      const staging = stagingArg()
      writeStagedPng(staging)
      fake.child().ready()
      fake.child().finish(PICKER_EXIT_CONFIRM)

      await expect(promise).resolves.toBeNull()
      expect(linkSpy).toHaveBeenCalledTimes(1)
      expect(readdirSync(inbox).filter((n) => n.endsWith('.png'))).toEqual([])
    })

    it('(b) a watcher listing during registration does not emit, and exactly one lands after', async () => {
      let settle: (() => void) | undefined
      vi.stubGlobal(
        'fetch',
        vi.fn(
          () =>
            new Promise<Response>((resolveFetch) => {
              settle = () => {
                resolveFetch(new Response('{}', { status: 201 }))
              }
            }),
        ),
      )
      const win = fakeWindow()
      const promise = captureRegionFromGui({
        inboxDir: inbox,
        copyToClipboard: false,
        source: 'gui',
        window: win.window as never,
      })
      await flush()
      const staging = stagingArg()
      writeStagedPng(staging)
      fake.child().ready()
      fake.child().finish(PICKER_EXIT_CONFIRM)
      await flush()

      // The link has landed; registration has not answered yet.
      expect(onInboxListing(readdirSync(inbox))).toBe(false)
      expect(win.sent).toEqual([])

      settle?.()
      await promise
      expect(win.sent.filter((c) => c === 'captures:inbox-changed')).toHaveLength(1)
      expect(onInboxListing(readdirSync(inbox))).toBe(false)
    })

    it('(c) a register rejection keeps the file, logs the final path and notifies once', async () => {
      vi.stubGlobal(
        'fetch',
        vi.fn(() => Promise.reject(new Error('backend down'))),
      )
      const balloons: (string | undefined)[] = []
      const toasts: (string | undefined)[] = []
      setNotifyUserDeps({
        balloon: (o) => {
          balloons.push(o.path)
          return true
        },
        toast: (o) => {
          toasts.push(o.path)
        },
      })
      const unlinkSpy = vi.spyOn(fs, 'unlinkSync')
      app.isPackaged = false

      const dest = await publishOnce()
      expect(fs.existsSync(dest)).toBe(true)
      expect(balloons).toEqual([dest])
      expect(toasts).toEqual([])
      expect(Notification.constructed).toBe(0)
      expect(logs.some((l) => l.includes(dest))).toBe(true)
      for (const call of unlinkSpy.mock.calls) {
        expect(String(call[0])).not.toBe(dest)
      }
    })

    it('(c) the packaged app takes the toast branch instead of the balloon', async () => {
      vi.stubGlobal(
        'fetch',
        vi.fn(() => Promise.reject(new Error('backend down'))),
      )
      const balloons: (string | undefined)[] = []
      const toasts: (string | undefined)[] = []
      setNotifyUserDeps({
        balloon: (o) => {
          balloons.push(o.path)
          return true
        },
        toast: (o) => {
          toasts.push(o.path)
        },
      })
      app.isPackaged = true

      const dest = await publishOnce()
      expect(toasts).toEqual([dest])
      expect(balloons).toEqual([])
    })

    it('(d) a filename === null event before and after registration still yields exactly one event', () => {
      seedInboxBaseline([])
      const claimed = '2026-08-27_10-00-00.png'
      reserveInboxPath(join(inbox, claimed))

      // `fs.watch` delivered no filename: the handler must rescan and compare sets.
      expect(onInboxListing([claimed])).toBe(false)
      settleInboxPath(join(inbox, claimed))
      expect(onInboxListing([claimed])).toBe(false)
      expect(onInboxListing([claimed])).toBe(false)
    })

    it('(e) a delayed event naming the claimed path after suppression is lifted does not re-emit', () => {
      seedInboxBaseline([])
      const claimed = '2026-08-27_10-00-01.png'
      reserveInboxPath(join(inbox, claimed))
      settleInboxPath(join(inbox, claimed))
      expect(onInboxListing([claimed])).toBe(false)
      expect(onInboxListing([claimed])).toBe(false)
    })

    it('(f) the first listing over a non-empty inbox is adopted as the baseline without notifying', () => {
      const existing = ['2026-08-01_09-00-00.png', '2026-08-02_09-00-00.png']
      seedInboxBaseline(existing)
      expect(onInboxListing(existing)).toBe(false)
      expect(onInboxListing([...existing, 'new.png'])).toBe(true)
    })

    it('(g) a reservation released after a failed link no longer suppresses that name', () => {
      seedInboxBaseline([])
      const candidate = join(inbox, 'contested.png')
      reserveInboxPath(candidate)
      expect(onInboxListing(['contested.png'])).toBe(false)
      releaseInboxPath(candidate)
      expect(onInboxListing(['contested.png'])).toBe(true)
    })

    it('(h) two captures in one second announce exactly once each and never re-announce the first', () => {
      seedInboxBaseline([])
      const base = '2026-08-27_11-11-11'
      const first = join(inbox, `${base}.png`)
      const second = join(inbox, `${base}_2.png`)

      reserveInboxPath(first)
      settleInboxPath(first)
      const afterFirst = onInboxListing([`${base}.png`])
      expect(afterFirst).toBe(false)

      // B reserves the same name, takes EEXIST, releases, then settles at _2.
      reserveInboxPath(first)
      releaseInboxPath(first)
      reserveInboxPath(second)
      settleInboxPath(second)

      expect(onInboxListing([`${base}.png`, `${base}_2.png`])).toBe(false)
      expect(onInboxListing([`${base}.png`, `${base}_2.png`])).toBe(false)
    })

    it('the notification decision is a pure function of the three sets', () => {
      expect(
        computeInboxNotification({
          current: ['a.png', 'b.png'],
          lastEmitted: new Set(['a.png']),
          reserved: new Set(['b.png']),
        }),
      ).toEqual({ notify: false, nextEmitted: new Set(['a.png']) })

      expect(
        computeInboxNotification({
          current: ['a.png', 'c.png'],
          lastEmitted: new Set(['a.png']),
          reserved: new Set<string>(),
        }),
      ).toEqual({ notify: true, nextEmitted: new Set(['a.png', 'c.png']) })
    })

    it('notifyUser always logs, on every branch, and is suppressed under AVKIT_E2E', () => {
      const lines: string[] = []
      const toasts: (string | undefined)[] = []
      setNotifyUserDeps({
        log: (l) => {
          lines.push(l)
        },
        toast: (o) => {
          toasts.push(o.path)
        },
        balloon: () => true,
      })
      app.isPackaged = true
      notifyUser({
        title: 'Capture saved',
        body: 'not registered',
        path: 'C:/caps/a.png',
      })
      expect(lines).toHaveLength(1)
      expect(toasts).toEqual(['C:/caps/a.png'])

      process.env.AVKIT_E2E = '1'
      notifyUser({
        title: 'Capture saved',
        body: 'not registered',
        path: 'C:/caps/b.png',
      })
      expect(lines).toHaveLength(2)
      expect(toasts).toEqual(['C:/caps/a.png'])
      delete process.env.AVKIT_E2E
    })

    it('falls back to a parentless dialog when the tray does not exist yet', () => {
      const dialogs: (string | undefined)[] = []
      setNotifyUserDeps({
        balloon: () => false,
        dialog: (o) => {
          dialogs.push(o.path)
        },
      })
      app.isPackaged = false
      notifyUser({
        title: 'Capture saved',
        body: 'not registered',
        path: 'C:/caps/c.png',
      })
      expect(dialogs).toEqual(['C:/caps/c.png'])
    })

    it('the black-pixel guard still gates publication of the picker PNG (AC-39.22 migrated)', async () => {
      __setNativeImageFactory(() => ({
        isEmpty: () => false,
        getSize: () => ({ width: 2, height: 2 }),
        toBitmap: () => Buffer.alloc(16, 0),
        toPNG: () => Buffer.alloc(4),
      }))
      const promise = fire()
      await flush()
      const staging = stagingArg()
      writeStagedPng(staging)
      fake.child().ready()
      fake.child().finish(PICKER_EXIT_CONFIRM)

      await expect(promise).resolves.toBeNull()
      expect(logs.some((l) => /\[Capture\].*(black|empty)/.test(l))).toBe(true)
      expect(readdirSync(inbox).filter((n) => n.endsWith('.png'))).toEqual([])
    })
  })

  /**
   * Round-2 review corrections. Each case is the failure boundary a reviewer finding named:
   * they are written against the *production* publication and lifecycle paths, not against a
   * mocked stand-in, because the defects live exactly where the mocks used to start.
   */
  describe('round-2: committed publication, visible failures, bounded parser', () => {
    it('a renderer torn down mid-announcement still publishes and never cancels the request', async () => {
      // `isDestroyed()` answers false and the send then throws: the real Electron race in which
      // the window dies between the guard and the IPC call. The PNG is already hard-linked into
      // the inbox at that point, so a rejection here would cancel an honoured request.
      const hostile = {
        isDestroyed: () => false,
        webContents: {
          send: () => {
            throw new Error('Object has been destroyed')
          },
        },
      }
      const cancel = vi.fn(async () => undefined)
      const complete = vi.fn(async () => undefined)
      clearCompletionJournal()

      const poll: PollResult = {
        kind: 'ok',
        rows: [{ id: 'req-hostile', status: 'Pending' }],
      }
      const tick = runInteractiveTick(poll, {
        capture: () =>
          captureRegionFromGui({
            inboxDir: inbox,
            copyToClipboard: false,
            source: 'gui',
            window: hostile as never,
          }),
        complete,
        cancel,
        relist: async (): Promise<PollResult> => ({ kind: 'ok', rows: [] }),
        notify: () => undefined,
        log: (line: string) => {
          logs.push(line)
        },
        now: () => 1,
      })
      await flush()
      writeStagedPng(stagingArg())
      fake.child().ready()
      fake.child().finish(PICKER_EXIT_CONFIRM)
      await tick

      expect(cancel).not.toHaveBeenCalled()
      expect(complete).toHaveBeenCalledTimes(1)
      expect(readdirSync(inbox).filter((n) => n.endsWith('.png'))).toHaveLength(1)
      clearCompletionJournal()
    })

    function collectNotices(): { title: string; body: string }[] {
      const notices: { title: string; body: string }[] = []
      setNotifyUserDeps({
        balloon: (o) => {
          notices.push({ title: o.title, body: o.body })
          return true
        },
      })
      return notices
    }

    it('an error exit tells the user why and carries the helper stderr tail into the log', async () => {
      const notices = collectNotices()
      const promise = fire()
      await flush()
      fake.child().complain('BitBlt failed: access to the desktop was denied')
      await flush()
      fake.child().finish(PICKER_EXIT_ERROR)

      await expect(promise).resolves.toBeNull()
      expect(notices).toHaveLength(1)
      expect(notices[0]?.title).toBe(SCREEN_CAPTURE_BLOCKED)
      expect(notices[0]?.body).toContain('access to the desktop was denied')
      expect(terminalLines()[0]).toContain('access to the desktop was denied')
    })

    it('a spawn error tells the user which executable could not start', async () => {
      const notices = collectNotices()
      const promise = fire()
      await flush()
      fake.child().failToSpawn(Object.assign(new Error('spawn ENOENT'), { code: 'ENOENT' }))

      await expect(promise).resolves.toBeNull()
      expect(notices).toHaveLength(1)
      expect(notices[0]?.body).toContain('ENOENT')
    })

    it('a cancel stays silent while a blocked black frame does not', async () => {
      const notices = collectNotices()
      const cancelled = fire()
      await flush()
      writeStagedPng(stagingArg())
      fake.child().ready()
      fake.child().finish(PICKER_EXIT_CANCEL)
      await expect(cancelled).resolves.toBeNull()
      expect(notices).toEqual([])

      __setNativeImageFactory(() => ({
        isEmpty: () => false,
        getSize: () => ({ width: 2, height: 2 }),
        toBitmap: () => Buffer.alloc(16, 0),
        toPNG: () => Buffer.alloc(4),
      }))
      const black = fire()
      await flush()
      writeStagedPng(stagingArg(1))
      fake.child(1).ready()
      fake.child(1).finish(PICKER_EXIT_CONFIRM)
      await expect(black).resolves.toBeNull()
      expect(notices).toHaveLength(1)
      expect(notices[0]?.title).toBe(SCREEN_CAPTURE_BLOCKED)
    })

    it(`a helper that never writes a newline keeps the parser under PICKER_LINE_MAX_BYTES (${PICKER_LINE_MAX_BYTES})`, async () => {
      const promise = fire()
      await flush()
      const child = fake.child()
      const noisy = 'x'.repeat(4096)
      for (let i = 0; i < 64; i += 1) {
        // No newline anywhere: the tail clamp bounds `stdout`, and only an independently bounded
        // partial-line buffer keeps the readiness parser from growing with it.
        child.stdout.write(noisy)
      }
      await flush()

      expect(getPickerParserState().pendingLineBytes).toBeLessThanOrEqual(PICKER_LINE_MAX_BYTES)
      child.finish(PICKER_EXIT_ERROR)
      await promise
      expect(getLastPickerOutput().stdout.length).toBeLessThanOrEqual(PICKER_LOG_MAX_BYTES)
    })

    it('a line whose head was discarded can never satisfy the readiness match', async () => {
      vi.useFakeTimers({ toFake: [...FAKED_TIMERS] })
      const promise = fire()
      await flush()
      const child = fake.child()
      child.stdout.write('y'.repeat(PICKER_LINE_MAX_BYTES + 1024))
      child.stdout.write(`${PICKER_READY_MARKER}\n`)
      await flush()

      // The whole line was `yyy…ready`, not `ready`; the discard must not turn it into a match.
      await vi.advanceTimersByTimeAsync(PICKER_STARTUP_TIMEOUT_MS + 1)
      await expect(promise).resolves.toBeNull()
      expect(terminalLines()[0]).toMatch(/failed to start/)
    })
  })
})
