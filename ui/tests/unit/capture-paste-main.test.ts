/** MEU-132 paste in main: AC-132.6 to AC-132.12 (plan 2026-11-10-gui-capture-image-import, D-556, D-557). */
import fs from 'node:fs'
import { mkdtempSync, readdirSync, readFileSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { basename, dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import {
  pasteClipboardImage,
  PICKER_STAGING_PREFIX,
  resetPickerState,
  resolvePasteInbox,
  setPickerLog,
  type PasteDeps,
} from '../../src/main/capture-picker'
import { resetInboxWatchState } from '../../src/main/capture-inbox-watch'
import { registerFileName } from '../../src/main/capture-register'
import { handleIpc, publishBackendReady, resetBackendIpcState, RENDERER_TO_MAIN_CHANNELS } from '../../src/main/ipc'
import { resetNotifyUserDeps, setNotifyUserDeps } from '../../src/main/notify-user'
import { getPreloadApiKeys } from '../../src/main/preload'
import { __resetElectronStub, __setNativeImageFactory, clipboard } from './helpers/electron-stub'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')

const NAME_RE = /^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.png$/

/** A 4x3 "PNG": the signature then marker bytes. The stub's nativeImage decides what it decodes to. */
const PNG = Buffer.concat([Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]), Buffer.from('s61-4x3-red')])

function nonBlack4x3(): void {
  __setNativeImageFactory(() => ({
    isEmpty: () => false,
    getSize: () => ({ width: 4, height: 3 }),
    toBitmap: () => Buffer.alloc(48, 180),
    toPNG: () => PNG,
  }))
}

function fakeWindow(): { window: never; sent: string[] } {
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
    } as never,
  }
}

function errnoError(code: string, message: string): NodeJS.ErrnoException {
  return Object.assign(new Error(message), { code })
}

function pngs(dir: string): string[] {
  return readdirSync(dir).filter((n) => n.endsWith('.png'))
}

function stagingNames(dir: string): string[] {
  return readdirSync(dir).filter((n) => n.startsWith(PICKER_STAGING_PREFIX))
}

type Deferred = { promise: Promise<Response>; resolve: (r: Response) => void }

function deferred(): Deferred {
  let resolveFn: (r: Response) => void = () => undefined
  const promise = new Promise<Response>((r) => {
    resolveFn = r
  })
  return { promise, resolve: resolveFn }
}

describe('MEU-132 paste in main', () => {
  let root: string
  let inboxA: string
  let inboxB: string
  let defaultInbox: string
  let pickerLines: string[]
  let notified: string[]
  let bodies: Array<Record<string, unknown>>
  let fetchSpy: ReturnType<typeof vi.fn>
  let registerAnswer: () => Promise<Response>

  /** Every line main logged: the picker sink, the in-app log and the notify log. */
  async function allLogLines(): Promise<string[]> {
    const snapshot = await handleIpc('get-log-snapshot', undefined)
    const items = snapshot.ok ? (snapshot.value as Array<{ message: string }>) : []
    return [...pickerLines, ...items.map((i) => i.message), ...notified]
  }

  function deps(overrides: Partial<PasteDeps> = {}): PasteDeps {
    return {
      resolveInboxDir: async () => inboxA,
      window: fakeWindow().window,
      readClipboardPng: () => PNG,
      ...overrides,
    }
  }

  beforeEach(() => {
    root = mkdtempSync(join(tmpdir(), 'avkit-paste-'))
    inboxA = join(root, 'inbox-a')
    inboxB = join(root, 'inbox-b')
    defaultInbox = join(root, 'default-inbox')
    fs.mkdirSync(inboxA)
    fs.mkdirSync(inboxB)
    resetPickerState()
    resetInboxWatchState()
    resetBackendIpcState()
    __resetElectronStub()
    nonBlack4x3()
    pickerLines = []
    setPickerLog((line) => {
      pickerLines.push(line)
    })
    notified = []
    setNotifyUserDeps({
      log: (line) => {
        notified.push(line)
      },
      toast: () => undefined,
      balloon: () => true,
      dialog: () => undefined,
    })
    publishBackendReady({ apiBase: 'http://127.0.0.1:9/api/v1', token: 't' })
    bodies = []
    registerAnswer = async () => new Response('{}', { status: 201 })
    fetchSpy = vi.fn((_url: string, init: RequestInit) => {
      bodies.push(JSON.parse(String(init.body)) as Record<string, unknown>)
      return registerAnswer()
    })
    vi.stubGlobal('fetch', fetchSpy)
    delete process.env.AVKIT_E2E
  })

  afterEach(() => {
    setPickerLog(null)
    resetPickerState()
    resetInboxWatchState()
    resetBackendIpcState()
    resetNotifyUserDeps()
    __resetElectronStub()
    vi.restoreAllMocks()
    vi.unstubAllGlobals()
    vi.useRealTimers()
    fs.rmSync(root, { recursive: true, force: true })
  })

  describe('AC-132.6 PASTE_MAIN saved', () => {
    it('AC-132.6 saves into the inbox the settings name, registers it as gui, and follows a changed inbox', async () => {
      let current = inboxA
      const read = vi.fn(async () => ({ inbox_dir: current }))
      const writeImage = vi.spyOn(clipboard, 'writeImage')
      const win = fakeWindow()

      const first = await pasteClipboardImage(deps({ resolveInboxDir: () => resolvePasteInbox(read), window: win.window }))
      expect(first).toMatchObject({ kind: 'saved', registered: true })
      const name = (first as { name: string }).name
      expect(name).toMatch(NAME_RE)
      expect(pngs(inboxA)).toEqual([name])
      expect(readFileSync(join(inboxA, name)).equals(PNG)).toBe(true)
      expect(bodies).toEqual([{ mode: 'register', source: 'gui', path: join(inboxA, name) }])
      expect(fs.existsSync(defaultInbox)).toBe(false)
      expect(win.sent).toContain('captures:inbox-changed')
      expect(stagingNames(inboxA)).toEqual([])
      expect(notified).toEqual([])
      expect(writeImage).not.toHaveBeenCalled()

      // A Save in Settings moves the inbox; the next paste follows it with no poll between.
      current = inboxB
      const second = await pasteClipboardImage(deps({ resolveInboxDir: () => resolvePasteInbox(read) }))
      expect(second).toMatchObject({ kind: 'saved', registered: true })
      const secondName = (second as { name: string }).name
      expect(pngs(inboxB)).toEqual([secondName])
      expect(bodies[1]).toEqual({ mode: 'register', source: 'gui', path: join(inboxB, secondName) })
      expect(pngs(inboxA)).toHaveLength(1)
      expect(read).toHaveBeenCalledTimes(2)
    })
  })

  describe('AC-132.6 PASTE_IPC resolver', () => {
    it('AC-132.6 resolvePasteInbox answers the read inbox_dir, reading once per call', async () => {
      const read = vi.fn(async () => ({ inbox_dir: inboxA }))
      await expect(resolvePasteInbox(read)).resolves.toBe(inboxA)
      expect(read).toHaveBeenCalledTimes(1)
    })
  })

  describe('AC-132.7 PASTE_MAIN not-ready, empty and busy', () => {
    it('AC-132.7 a null or rejected inbox answers not-ready before the clipboard or any fs call', async () => {
      const mkdirSpy = vi.spyOn(fs, 'mkdirSync')
      const openSpy = vi.spyOn(fs, 'openSync')
      for (const resolveInboxDir of [async () => null, async () => Promise.reject(new Error('settings down'))]) {
        const readClipboardPng = vi.fn(() => PNG)
        const out = await pasteClipboardImage(deps({ resolveInboxDir, readClipboardPng }))
        expect(out).toEqual({ kind: 'not-ready' })
        expect(readClipboardPng).not.toHaveBeenCalled()
      }
      expect(mkdirSpy).not.toHaveBeenCalled()
      expect(openSpy).not.toHaveBeenCalled()
      expect(fs.existsSync(defaultInbox)).toBe(false)
    })

    it('AC-132.7 through resolvePasteInbox a null or rejected read after a move writes nothing anywhere', async () => {
      let answer: () => Promise<{ inbox_dir: string } | null> = async () => ({ inbox_dir: inboxA })
      const read = vi.fn(() => answer())
      const saved = await pasteClipboardImage(deps({ resolveInboxDir: () => resolvePasteInbox(read) }))
      expect(saved).toMatchObject({ kind: 'saved' })
      answer = async () => ({ inbox_dir: inboxB })
      for (const next of [async () => null, async () => Promise.reject(new Error('settings down'))]) {
        answer = next
        const readClipboardPng = vi.fn(() => PNG)
        const out = await pasteClipboardImage(deps({ resolveInboxDir: () => resolvePasteInbox(read), readClipboardPng }))
        expect(out).toEqual({ kind: 'not-ready' })
        expect(readClipboardPng).not.toHaveBeenCalled()
      }
      expect(readdirSync(inboxA)).toHaveLength(1)
      expect(readdirSync(inboxB)).toEqual([])
    })

    it('AC-132.7 an empty clipboard answers empty and writes nothing', async () => {
      const out = await pasteClipboardImage(deps({ readClipboardPng: () => null }))
      expect(out).toEqual({ kind: 'empty' })
      expect(readdirSync(inboxA)).toEqual([])
      expect(fetchSpy).not.toHaveBeenCalled()
    })

    it('AC-132.7 a second paste while the first awaits its register answers busy; a third runs after', async () => {
      const gate = deferred()
      registerAnswer = () => gate.promise
      try {
        const first = pasteClipboardImage(deps())
        await vi.waitFor(() => {
          expect(fetchSpy).toHaveBeenCalledTimes(1)
        })
        const second = await pasteClipboardImage(deps())
        expect(second).toEqual({ kind: 'busy' })
        expect(pngs(inboxA)).toHaveLength(1)
        gate.resolve(new Response('{}', { status: 201 }))
        await expect(first).resolves.toMatchObject({ kind: 'saved', registered: true })
      } finally {
        gate.resolve(new Response('{}', { status: 201 }))
      }
      registerAnswer = async () => new Response('{}', { status: 201 })
      const third = await pasteClipboardImage(deps())
      expect(third).toMatchObject({ kind: 'saved' })
    })
  })

  describe('AC-132.8 PASTE_MAIN blocked', () => {
    it('AC-132.8 an all-black image answers blocked black and leaves nothing', async () => {
      __setNativeImageFactory(() => ({
        isEmpty: () => false,
        getSize: () => ({ width: 2, height: 2 }),
        toBitmap: () => Buffer.alloc(16, 0),
        toPNG: () => PNG,
      }))
      const out = await pasteClipboardImage(deps())
      expect(out).toEqual({ kind: 'blocked', reason: 'black' })
      expect(readdirSync(inboxA)).toEqual([])
      expect(notified).toEqual([])
      expect(fetchSpy).not.toHaveBeenCalled()
    })

    it('AC-132.8 a zero-pixel image answers blocked empty and leaves nothing', async () => {
      __setNativeImageFactory(() => ({
        isEmpty: () => true,
        getSize: () => ({ width: 0, height: 0 }),
        toBitmap: () => Buffer.alloc(0),
        toPNG: () => Buffer.alloc(0),
      }))
      const out = await pasteClipboardImage(deps())
      expect(out).toEqual({ kind: 'blocked', reason: 'empty' })
      expect(readdirSync(inboxA)).toEqual([])
      expect(notified).toEqual([])
    })
  })

  describe('AC-132.9 exclusive staging', () => {
    it('AC-132.9 a staging name another writer holds is never opened; a new one is drawn', async () => {
      const held = join(inboxA, `${PICKER_STAGING_PREFIX}held.tmp`)
      writeFileSync(held, 'OTHER')
      const nextStagingName = vi.fn().mockReturnValueOnce('held').mockReturnValue('fresh')
      const out = await pasteClipboardImage(deps({ nextStagingName }))
      expect(out).toMatchObject({ kind: 'saved' })
      expect(nextStagingName).toHaveBeenCalledTimes(2)
      expect(readFileSync(held, 'utf8')).toBe('OTHER')
      expect(stagingNames(inboxA)).toEqual([basename(held)])
      const name = (out as { name: string }).name
      expect(readFileSync(join(inboxA, name)).equals(PNG)).toBe(true)
    })

    it('AC-132.9 a taken name in the same second gives _2 and leaves the first file alone', async () => {
      vi.useFakeTimers({ toFake: ['Date'] })
      vi.setSystemTime(new Date(2026, 10, 10, 9, 30, 15, 500))
      const taken = registerFileName()
      writeFileSync(join(inboxA, taken), 'first')
      const out = await pasteClipboardImage(deps())
      expect(out).toMatchObject({ kind: 'saved', name: taken.replace(/\.png$/, '_2.png') })
      expect(readFileSync(join(inboxA, taken), 'utf8')).toBe('first')
    })
  })

  describe('AC-132.10 failure mapping', () => {
    it('AC-132.10 an inbox path that is a file answers failed', async () => {
      const fileInbox = join(root, 'not-a-folder')
      writeFileSync(fileInbox, 'x')
      const mkdirSpy = vi.spyOn(fs, 'mkdirSync')
      await expect(pasteClipboardImage(deps({ resolveInboxDir: async () => fileInbox }))).resolves.toEqual({
        kind: 'failed',
      })
      expect(mkdirSpy.mock.calls.some((c) => String(c[0]) === fileInbox)).toBe(true)
      expect(readFileSync(fileInbox, 'utf8')).toBe('x')
    })

    it('AC-132.10 openSync EACCES answers failed', async () => {
      const realOpen = fs.openSync.bind(fs)
      const openSpy = vi.spyOn(fs, 'openSync').mockImplementation(((path: fs.PathLike, ...rest: never[]) => {
        if (String(path).startsWith(inboxA)) {
          throw errnoError('EACCES', `EACCES: permission denied, open '${String(path)}'`)
        }
        return (realOpen as (...a: unknown[]) => number)(path, ...rest)
      }) as typeof fs.openSync)
      await expect(pasteClipboardImage(deps())).resolves.toEqual({ kind: 'failed' })
      expect(openSpy.mock.calls.some((c) => String(c[0]).startsWith(inboxA))).toBe(true)
      expect(readdirSync(inboxA)).toEqual([])
    })

    it('AC-132.10 a writeSync failure answers failed and removes its own staging file', async () => {
      const realOpen = fs.openSync.bind(fs)
      const realWrite = fs.writeSync.bind(fs)
      const ours = new Set<number>()
      vi.spyOn(fs, 'openSync').mockImplementation(((path: fs.PathLike, ...rest: never[]) => {
        const fd = (realOpen as (...a: unknown[]) => number)(path, ...rest)
        if (String(path).startsWith(inboxA)) {
          ours.add(fd)
        }
        return fd
      }) as typeof fs.openSync)
      const writeSpy = vi.spyOn(fs, 'writeSync').mockImplementation(((fd: number, ...rest: never[]) => {
        if (ours.has(fd)) {
          throw errnoError('EIO', `EIO: i/o error, write`)
        }
        return (realWrite as (...a: unknown[]) => number)(fd, ...rest)
      }) as typeof fs.writeSync)
      await expect(pasteClipboardImage(deps())).resolves.toEqual({ kind: 'failed' })
      expect(writeSpy.mock.calls.some((c) => ours.has(c[0] as number))).toBe(true)
      expect(readdirSync(inboxA)).toEqual([])
    })

    it('AC-132.10 a claim linkSync EACCES answers failed and leaves no staging file', async () => {
      const realLink = fs.linkSync.bind(fs)
      const linkSpy = vi.spyOn(fs, 'linkSync').mockImplementation(((from: fs.PathLike, to: fs.PathLike) => {
        if (String(to).startsWith(inboxA)) {
          throw errnoError('EACCES', `EACCES: permission denied, link '${String(from)}' -> '${String(to)}'`)
        }
        realLink(from, to)
      }) as typeof fs.linkSync)
      await expect(pasteClipboardImage(deps())).resolves.toEqual({ kind: 'failed' })
      expect(linkSpy.mock.calls.some((c) => String(c[1]).startsWith(inboxA))).toBe(true)
      expect(readdirSync(inboxA)).toEqual([])
      expect(fetchSpy).not.toHaveBeenCalled()
    })
  })

  describe('AC-132.11 PASTE_LOG', () => {
    function expectNoPath(lines: string[]): void {
      for (const line of lines) {
        for (const dir of [root, root.replace(/\\/g, '/')]) {
          expect(line, line).not.toContain(dir)
        }
        expect(line, line).not.toContain(PICKER_STAGING_PREFIX)
      }
    }

    it('AC-132.11 saved, not-ready, empty and blocked log a code and at most the basename', async () => {
      const saved = await pasteClipboardImage(deps())
      expect(saved).toMatchObject({ kind: 'saved' })
      const name = (saved as { name: string }).name
      await pasteClipboardImage(deps({ resolveInboxDir: async () => null }))
      await pasteClipboardImage(deps({ readClipboardPng: () => null }))
      __setNativeImageFactory(() => ({
        isEmpty: () => false,
        getSize: () => ({ width: 2, height: 2 }),
        toBitmap: () => Buffer.alloc(16, 0),
        toPNG: () => PNG,
      }))
      await pasteClipboardImage(deps())
      const lines = await allLogLines()
      expect(lines.some((l) => l.endsWith(`paste saved ${name}`))).toBe(true)
      expect(lines.some((l) => l.endsWith('paste not ready'))).toBe(true)
      expect(lines.some((l) => l.endsWith('paste empty'))).toBe(true)
      expect(lines.some((l) => l.endsWith('paste blocked black'))).toBe(true)
      expectNoPath(lines)
    })

    it('AC-132.11 a register failure keeps the file, answers registered false and logs the basename only', async () => {
      registerAnswer = async () => new Response('{}', { status: 500 })
      const out = await pasteClipboardImage(deps())
      expect(out).toMatchObject({ kind: 'saved', registered: false })
      const name = (out as { name: string }).name
      expect(pngs(inboxA)).toEqual([name])
      const lines = await allLogLines()
      expect(lines.some((l) => l.endsWith(`paste register failed, kept ${name}`))).toBe(true)
      expect(lines.some((l) => l.includes('register failed:'))).toBe(false)
      expect(notified).toEqual([])
      expectNoPath(lines)
    })

    it('AC-132.11 a claim failure logs its code with no path', async () => {
      const realLink = fs.linkSync.bind(fs)
      vi.spyOn(fs, 'linkSync').mockImplementation(((from: fs.PathLike, to: fs.PathLike) => {
        if (String(to).startsWith(inboxA)) {
          throw errnoError('EACCES', `EACCES: permission denied, link '${String(from)}' -> '${String(to)}'`)
        }
        realLink(from, to)
      }) as typeof fs.linkSync)
      await pasteClipboardImage(deps())
      const lines = await allLogLines()
      expect(lines.some((l) => l.endsWith('could not claim a name (EACCES)'))).toBe(true)
      expectNoPath(lines)
    })

    it('AC-132.11 a filesystem failure logs paste failed with its code', async () => {
      const realOpen = fs.openSync.bind(fs)
      vi.spyOn(fs, 'openSync').mockImplementation(((path: fs.PathLike, ...rest: never[]) => {
        if (String(path).startsWith(inboxA)) {
          throw errnoError('EACCES', `EACCES: permission denied, open '${String(path)}'`)
        }
        return (realOpen as (...a: unknown[]) => number)(path, ...rest)
      }) as typeof fs.openSync)
      await pasteClipboardImage(deps())
      const lines = await allLogLines()
      expect(lines.some((l) => l.endsWith('paste failed EACCES'))).toBe(true)
      expectNoPath(lines)
    })
  })

  describe('AC-132.12 PASTE_IPC', () => {
    it('AC-132.12 capture-paste-image is the last channel and takes no payload', async () => {
      expect(RENDERER_TO_MAIN_CHANNELS[RENDERER_TO_MAIN_CHANNELS.length - 1]).toBe('capture-paste-image')
      const dep = vi.fn(async () => ({ kind: 'empty' as const }))
      expect((await handleIpc('capture-paste-image', {}, { pasteCaptureImage: dep })).ok).toBe(true)
      expect((await handleIpc('capture-paste-image', { extra: true }, { pasteCaptureImage: dep })).ok).toBe(false)
      expect((await handleIpc('capture-paste-image', 'x', { pasteCaptureImage: dep })).ok).toBe(false)
    })

    it('AC-132.12 the handler calls the dep once and returns its outcome', async () => {
      const outcome = { kind: 'saved' as const, name: '2026-11-10_09-30-15.png', registered: true }
      const dep = vi.fn(async () => outcome)
      const result = await handleIpc('capture-paste-image', undefined, { pasteCaptureImage: dep })
      expect(dep).toHaveBeenCalledTimes(1)
      expect(result).toEqual({ ok: true, value: outcome })
    })

    it('AC-132.12 with no dep the handler answers failed', async () => {
      await expect(handleIpc('capture-paste-image', undefined, {})).resolves.toEqual({
        ok: true,
        value: { kind: 'failed' },
      })
    })

    it('AC-132.12 preload exposes pasteCaptureImage last, invoking the channel on one line', () => {
      const keys = getPreloadApiKeys()
      expect(keys[keys.length - 1]).toBe('pasteCaptureImage')
      const preload = readFileSync(join(repoRoot, 'ui/src/main/preload.ts'), 'utf8')
      expect(preload).toContain("pasteCaptureImage: () => ipcRenderer.invoke('capture-paste-image'),")
    })
  })
})
