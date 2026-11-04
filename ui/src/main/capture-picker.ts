import { spawn as childProcessSpawn } from 'node:child_process'
import { randomBytes } from 'node:crypto'
import fs from 'node:fs'
import { homedir } from 'node:os'
import { basename, dirname, join } from 'node:path'

import { app, clipboard, nativeImage, type BrowserWindow } from 'electron'

import {
  notifyInboxChanged,
  releaseInboxPath,
  reserveInboxPath,
  settleInboxPath,
  STAGING_PREFIX,
} from './capture-inbox-watch'
import { inspectNativeImagePixels } from './capture-pixels'
import { finalizeCapturedPng, registerFileName, type RegisterSource } from './capture-register'
import { appendStdoutLog } from './ipc'
import { notifyUser } from './notify-user'

/**
 * The region picker sidecar seam (MEU-40).
 *
 * Electron is the right host for av-kit and the wrong region picker: a transparent, click-through
 * `BrowserWindow` over a Chromium-captured freeze frame is a compositor-timing problem dressed up as a
 * UI, which is why the old overlay kept degrading into a black sheet. Selecting a rectangle is a
 * native Win32 job, so it runs in `avkit-region-picker.exe` — a short-lived child process that
 * owns the freeze, the selection UI and the `BitBlt`, and answers on exactly two channels: an
 * exit code, and a PNG at the `--out` path it was given.
 *
 * This module is the Electron half of that contract. It knows nothing about how the rectangle is
 * drawn; it starts the helper, bounds it in time, classifies its exit, and — on a confirm —
 * publishes the staged PNG into the inbox without ever rewriting the bytes.
 */

/** The helper captured a region and wrote the staged PNG. */
export const PICKER_EXIT_CONFIRM = 0
/** The helper could not capture (no display, denied desktop, internal fault). */
export const PICKER_EXIT_ERROR = 1
/** The user pressed Escape or right-clicked out of the selection. */
export const PICKER_EXIT_CANCEL = 2

/** Printed by the helper on stdout as soon as its window is up and taking input. */
export const PICKER_READY_MARKER = 'ready'

/** The staged file lives in the inbox so the claim below is a same-volume hard link. */
export const PICKER_STAGING_PREFIX = STAGING_PREFIX

export const PICKER_EXE_NAME = 'avkit-region-picker.exe'
export const PICKER_EXE_REL = `native/region-picker/publish/${PICKER_EXE_NAME}`
export const PICKER_RESOURCE_DIR = 'region-picker'

/** Time allowed between spawn and the readiness line before the helper is presumed stuck. */
export const PICKER_STARTUP_TIMEOUT_MS = 5_000
/** Time allowed for the human to drag a rectangle before the helper is reclaimed. */
export const PICKER_INTERACTION_TIMEOUT_MS = 120_000
/** Grace between the polite kill and `SIGKILL`. */
export const PICKER_KILL_GRACE_MS = 2_000
/** Only the tail of each pipe is kept: a wedged helper must not grow the main process. */
export const PICKER_LOG_MAX_BYTES = 65_536
/**
 * Cap on the *unterminated* readiness line held by the parser.
 *
 * The pipe tail clamp above bounds what is stored, not what is being parsed: a helper that
 * writes forever without a newline would grow the partial line for the whole startup timeout
 * and kill grace. A line this long cannot become the readiness marker, so it is discarded and
 * the line it belonged to is poisoned rather than silently re-anchored mid-stream.
 */
export const PICKER_LINE_MAX_BYTES = 4_096
/** How much of the helper's stderr is quoted back to the user in a blocked reason. */
export const PICKER_REASON_STDERR_BYTES = 400
/** The first collision suffix; `name.png` is tried bare before `name_2.png`. */
export const PICKER_COLLISION_SUFFIX_START = 2
/** Upper bound on name-claim attempts within a single wall-clock second. */
export const PICKER_COLLISION_LIMIT = 64

/** `--avkit-picker-path` makes the app print where it would look for the helper, then quit. */
export const PICKER_PATH_PROBE_FLAG = '--avkit-picker-path'
export const PICKER_PATH_PROBE_PREFIX = 'PICKER_PATH='

const CONSOLE_MODULE_TAG = '[Capture]'
export const SCREEN_CAPTURE_BLOCKED = 'Screen capture blocked'

export type PickerOutcome =
  | { kind: 'confirm'; path: string }
  | { kind: 'cancel' }
  | { kind: 'blocked'; reason: string }

type PickerSpawn = typeof childProcessSpawn

let spawnImpl: PickerSpawn | null = null
let logImpl: ((line: string) => void) | null = null
let lastOutput: { stdout: string; stderr: string } = { stdout: '', stderr: '' }
let parserState: { pendingLineBytes: number; discarded: boolean } = {
  pendingLineBytes: 0,
  discarded: false,
}
let inFlight = false

/** Swaps the process factory; `null` restores the real `child_process.spawn`. */
export function setPickerSpawn(fn: PickerSpawn | null): void {
  spawnImpl = fn
}

export function getPickerSpawn(): PickerSpawn {
  return spawnImpl ?? childProcessSpawn
}

/** Swaps the console sink; `null` restores the in-app log. */
export function setPickerLog(fn: ((line: string) => void) | null): void {
  logImpl = fn
}

function log(line: string): void {
  if (logImpl !== null) {
    logImpl(line)
    return
  }
  appendStdoutLog(line)
}

/** The tail of the last helper run's pipes, for diagnosing a blocked capture. */
export function getLastPickerOutput(): { stdout: string; stderr: string } {
  return { ...lastOutput }
}

/** Test seam for the bounded readiness parser: what it is still holding for the current line. */
export function getPickerParserState(): {
  pendingLineBytes: number
  discarded: boolean
} {
  return { ...parserState }
}

export function isPickerInFlight(): boolean {
  return inFlight
}

export function resetPickerState(): void {
  inFlight = false
  lastOutput = { stdout: '', stderr: '' }
  parserState = { pendingLineBytes: 0, discarded: false }
}

export function expandInboxDir(dir: string): string {
  if (dir.startsWith('~/')) {
    return join(homedir(), dir.slice(2))
  }
  return dir
}

/**
 * Where the helper lives, in precedence order: an explicit override (the E2E harness and manual
 * smoke runs), the packaged `resources/region-picker/` directory, then the dev publish tree.
 *
 * The dev branch is derived from the working directory rather than `__dirname` because the main
 * bundle's location differs between `electron-vite dev` and a plain node/vitest process, while the
 * repo root is the same in both.
 */
export function resolvePickerExePath(): string {
  const override = process.env.AVKIT_REGION_PICKER_PATH
  if (override !== undefined && override.trim().length > 0) {
    return override
  }
  if (app.isPackaged) {
    const resources =
      typeof process.resourcesPath === 'string' ? process.resourcesPath : process.cwd()
    return join(resources, PICKER_RESOURCE_DIR, PICKER_EXE_NAME)
  }
  const cwd = process.cwd()
  const root = basename(cwd).toLowerCase() === 'ui' ? dirname(cwd) : cwd
  return join(root, PICKER_EXE_REL)
}

function removeStaging(path: string): void {
  try {
    fs.unlinkSync(path)
  } catch {
    // Already gone on every cancel and most error paths; nothing to reclaim.
  }
}

function stagedFileIsUsable(path: string): boolean {
  try {
    return fs.statSync(path).size > 0
  } catch {
    return false
  }
}

function clampTail(text: string): string {
  return text.length > PICKER_LOG_MAX_BYTES ? text.slice(text.length - PICKER_LOG_MAX_BYTES) : text
}

/**
 * Appends the last of the helper's stderr to a blocked reason, as one line.
 *
 * The reason ends up in a Windows toast and a balloon, neither of which can show a multi-line
 * dump, so the tail is collapsed to single spaces and trimmed to PICKER_REASON_STDERR_BYTES.
 */
function withStderrTail(reason: string, stderr: string): string {
  const collapsed = stderr.replace(/\s+/g, ' ').trim()
  if (collapsed.length === 0) {
    return reason
  }
  const tail =
    collapsed.length > PICKER_REASON_STDERR_BYTES
      ? collapsed.slice(collapsed.length - PICKER_REASON_STDERR_BYTES)
      : collapsed
  return `${reason} (helper said: ${tail})`
}

function errorMessage(err: unknown): string {
  return err instanceof Error ? err.message : String(err)
}

/**
 * Runs one helper process to completion and classifies the result.
 *
 * Every path through this function settles exactly once and emits exactly one terminal
 * `[Capture] picker …` line, so a reader of the log can always tell what became of an F2 press.
 * Staging is removed on every outcome but `confirm`.
 */
export function runRegionPicker(stagingPath: string): Promise<PickerOutcome> {
  const exe = resolvePickerExePath()

  return new Promise<PickerOutcome>((resolve) => {
    let settled = false
    let ready = false
    let exited = false
    let killReason: string | null = null
    let stdout = ''
    let stderr = ''
    let lineBuffer = ''
    let lineDiscarded = false
    let startupTimer: ReturnType<typeof setTimeout> | null = null
    let interactionTimer: ReturnType<typeof setTimeout> | null = null
    let graceTimer: ReturnType<typeof setTimeout> | null = null

    // argv array, never a shell string: the exe path is user-configurable and a quoted command
    // line would make it an injection surface.
    const spawn = getPickerSpawn()
    const child = spawn(exe, ['--out', stagingPath], {
      shell: false,
      windowsHide: true,
      stdio: ['ignore', 'pipe', 'pipe'],
    })

    const onWillQuit = (): void => {
      terminate('the app quit while the region picker was open')
    }
    app.on('will-quit', onWillQuit)

    function clearDeadlines(): void {
      if (startupTimer !== null) {
        clearTimeout(startupTimer)
        startupTimer = null
      }
      if (interactionTimer !== null) {
        clearTimeout(interactionTimer)
        interactionTimer = null
      }
    }

    function settle(outcome: PickerOutcome): void {
      if (settled) {
        return
      }
      settled = true
      clearDeadlines()
      app.removeListener('will-quit', onWillQuit)
      lastOutput = { stdout, stderr }
      if (outcome.kind === 'confirm') {
        log(`${CONSOLE_MODULE_TAG} picker confirm ${outcome.path}`)
      } else if (outcome.kind === 'cancel') {
        removeStaging(stagingPath)
        log(`${CONSOLE_MODULE_TAG} picker cancel`)
      } else {
        removeStaging(stagingPath)
        // The helper's own diagnosis is the only thing that distinguishes `denied desktop` from
        // `no such display`, so it travels with the reason instead of living solely in the
        // test-facing pipe capture: the log and the user-visible notice both need it.
        const detailed = withStderrTail(outcome.reason, stderr)
        log(`${CONSOLE_MODULE_TAG} picker blocked: ${detailed}`)
        resolve({ kind: 'blocked', reason: detailed })
        return
      }
      resolve(outcome)
    }

    function killChild(): void {
      if (exited) {
        return
      }
      child.kill()
      // The escalation deliberately outlives `settle`: the caller is already free, but this
      // process still owes the OS a dead child rather than an orphaned full-screen window.
      graceTimer = setTimeout(() => {
        graceTimer = null
        if (!exited) {
          child.kill('SIGKILL')
        }
      }, PICKER_KILL_GRACE_MS)
    }

    function terminate(reason: string): void {
      if (settled) {
        return
      }
      killReason = reason
      killChild()
      settle({ kind: 'blocked', reason })
    }

    function markReady(): void {
      if (ready) {
        return
      }
      ready = true
      if (startupTimer !== null) {
        clearTimeout(startupTimer)
        startupTimer = null
      }
      interactionTimer = setTimeout(() => {
        terminate('the region picker timed out waiting for a selection')
      }, PICKER_INTERACTION_TIMEOUT_MS)
    }

    startupTimer = setTimeout(() => {
      terminate('the region picker failed to start')
    }, PICKER_STARTUP_TIMEOUT_MS)

    child.stdout?.on('data', (chunk: unknown) => {
      const text = String(chunk)
      stdout = clampTail(stdout + text)
      if (ready) {
        return
      }
      lineBuffer += text
      const lines = lineBuffer.split('\n')
      lineBuffer = lines.pop() ?? ''
      for (const line of lines) {
        // Anchored on the whole line so `readyish` and `not ready yet` do not start the clock.
        // A line whose head was discarded by the bound below can no longer be compared whole,
        // so it is refused outright rather than matched on its surviving tail.
        const matched = !lineDiscarded && line.trim() === PICKER_READY_MARKER
        lineDiscarded = false
        if (matched) {
          markReady()
          break
        }
      }
      if (lineBuffer.length > PICKER_LINE_MAX_BYTES) {
        lineBuffer = ''
        lineDiscarded = true
      }
      parserState = {
        pendingLineBytes: lineBuffer.length,
        discarded: lineDiscarded,
      }
    })

    child.stderr?.on('data', (chunk: unknown) => {
      stderr = clampTail(stderr + String(chunk))
    })

    child.on('error', (err: unknown) => {
      settle({
        kind: 'blocked',
        reason: `the region picker could not start: ${errorMessage(err)}`,
      })
    })

    child.on('exit', () => {
      exited = true
      if (graceTimer !== null) {
        clearTimeout(graceTimer)
        graceTimer = null
      }
    })

    child.on('close', (code: number | null, signal: string | null) => {
      exited = true
      if (graceTimer !== null) {
        clearTimeout(graceTimer)
        graceTimer = null
      }
      if (settled) {
        return
      }
      if (killReason !== null) {
        settle({ kind: 'blocked', reason: killReason })
        return
      }
      if (signal !== null && signal !== undefined) {
        settle({
          kind: 'blocked',
          reason: `the region picker was killed by ${signal}`,
        })
        return
      }
      if (code === PICKER_EXIT_CANCEL) {
        settle({ kind: 'cancel' })
        return
      }
      if (code === PICKER_EXIT_CONFIRM) {
        if (!stagedFileIsUsable(stagingPath)) {
          settle({
            kind: 'blocked',
            reason: 'the region picker reported a capture but wrote no usable file',
          })
          return
        }
        settle({ kind: 'confirm', path: stagingPath })
        return
      }
      settle({
        kind: 'blocked',
        reason: `the region picker exited with code ${String(code)}`,
      })
    })
  })
}

/**
 * Claims a name in the inbox by hard-linking the staged file onto it.
 *
 * `link` is used rather than `rename` because it fails loudly with `EEXIST` instead of silently
 * replacing an existing capture, and it never rewrites the helper's bytes. Only `EEXIST` walks to
 * the next suffix; any other error is a real failure and is reported as one.
 */
function claimInboxName(inbox: string, stagingPath: string): string | null {
  const stem = registerFileName().replace(/\.png$/, '')
  for (let attempt = 1; attempt <= PICKER_COLLISION_LIMIT; attempt += 1) {
    const suffix = attempt < PICKER_COLLISION_SUFFIX_START ? '' : `_${attempt}`
    const candidate = join(inbox, `${stem}${suffix}.png`)
    reserveInboxPath(candidate)
    try {
      fs.linkSync(stagingPath, candidate)
      return candidate
    } catch (err: unknown) {
      releaseInboxPath(candidate)
      if ((err as NodeJS.ErrnoException).code === 'EEXIST') {
        continue
      }
      log(`${CONSOLE_MODULE_TAG} could not claim ${candidate}: ${errorMessage(err)}`)
      return null
    }
  }
  log(
    `${CONSOLE_MODULE_TAG} could not claim a name in ${inbox} after ${PICKER_COLLISION_LIMIT} tries`,
  )
  return null
}

async function publishStagedCapture(
  stagingPath: string,
  inbox: string,
  opts: {
    copyToClipboard: boolean
    source: RegisterSource
    window: BrowserWindow
    register?: boolean
  },
): Promise<string | null> {
  const image = nativeImage.createFromPath(stagingPath)
  const pixels = inspectNativeImagePixels(image)
  if (pixels.blocked) {
    const kind = pixels.width < 1 || pixels.height < 1 ? 'empty' : 'black'
    log(`${CONSOLE_MODULE_TAG} ${SCREEN_CAPTURE_BLOCKED} ${kind}`)
    removeStaging(stagingPath)
    notifyUser({
      title: SCREEN_CAPTURE_BLOCKED,
      body:
        kind === 'empty'
          ? 'The region picker returned an image with no pixels.'
          : 'The captured region came back entirely black, so nothing was saved.',
    })
    return null
  }

  if (opts.copyToClipboard) {
    clipboard.writeImage(image)
  }

  const dest = claimInboxName(inbox, stagingPath)
  removeStaging(stagingPath)
  if (dest === null) {
    notifyUser({
      title: SCREEN_CAPTURE_BLOCKED,
      body: `The capture could not be saved into ${inbox}.`,
    })
    return null
  }

  // Publication is committed the moment the link succeeds. Everything below is announcement and
  // bookkeeping on a file the user already owns, and none of it may reject: a rejection reaches
  // `runInteractiveTick` as a *pre*-publication failure and cancels a request whose PNG is
  // already in the inbox (AC-40.33). A renderer torn down between `isDestroyed()` and `send()`
  // is exactly that case.
  try {
    // The reservation is lifted before the announcement so a watcher rescan racing the register
    // call sees an already-announced name rather than a second "new file".
    settleInboxPath(dest)
    await finalizeCapturedPng(
      dest,
      opts.source,
      opts.register !== false,
      () => {
        notifyInboxChanged(opts.window)
      },
      (message) => {
        // The pixels are already safe on disk; a backend that cannot record them must never
        // cost the user the capture, so the file stays and the user is told where it is.
        log(`${CONSOLE_MODULE_TAG} register failed, kept ${dest}: ${message}`)
        notifyUser({
          title: 'Capture saved but not registered',
          body: 'The capture is on disk but the library did not record it.',
          path: dest,
        })
      },
    )
  } catch (err: unknown) {
    log(
      `${CONSOLE_MODULE_TAG} published ${dest}; post-publication step failed: ${errorMessage(err)}`,
    )
  }
  return dest
}

/**
 * The single entry point behind F2 and the Capture region button.
 *
 * Resolves to the published inbox path, or `null` for every non-publication outcome — cancel,
 * blocked helper, black frame, or a second press while one picker is already open. Every
 * `null` except a cancel and a re-entrant press is announced to the user, so a broken helper
 * never reads as an ordinary cancel. It never rejects: the hotkey handler has nowhere to put
 * an exception.
 */
export async function captureRegionFromGui(opts: {
  inboxDir: string
  copyToClipboard: boolean
  source: RegisterSource
  window: BrowserWindow
  register?: boolean
}): Promise<string | null> {
  // Headless CI has no desktop to select a region on, so the default E2E run stops here — but the
  // moment a harness supplies a real helper path the whole chain runs for real, which is how
  // AC-40.18 exercises spawn, publication and register end to end.
  if (process.env.AVKIT_E2E === '1' && process.env.AVKIT_REGION_PICKER_PATH === undefined) {
    notifyInboxChanged(opts.window)
    return null
  }

  if (inFlight) {
    return null
  }
  inFlight = true
  try {
    const inbox = expandInboxDir(opts.inboxDir)
    fs.mkdirSync(inbox, { recursive: true })
    const stagingPath = join(inbox, `${PICKER_STAGING_PREFIX}${randomBytes(8).toString('hex')}.tmp`)

    const outcome = await runRegionPicker(stagingPath)
    if (outcome.kind === 'blocked') {
      // A cancel is the user's own decision and stays silent; a blocked helper is not, and a
      // silent one is indistinguishable from a cancel — which is how a broken installed helper
      // reads as "F2 does nothing". The reason already carries the helper's stderr tail.
      notifyUser({ title: SCREEN_CAPTURE_BLOCKED, body: outcome.reason })
      return null
    }
    if (outcome.kind !== 'confirm') {
      return null
    }
    return await publishStagedCapture(outcome.path, inbox, opts)
  } finally {
    inFlight = false
  }
}
