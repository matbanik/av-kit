import { spawn, type ChildProcess } from 'node:child_process'
import { realpathSync } from 'node:fs'
import { join } from 'node:path'
import type { LiveQuery } from './live-identity'

export async function resolvePythonImage(
  run: (cmd: string[]) => Promise<string>,
): Promise<string> {
  const output = (await run(['uv', 'run', 'python', '-c', 'import sys; print(sys.executable)'])).trim()
  try {
    return realpathSync(output)
  } catch {
    return output
  }
}

export function buildDevSpawnArgv(input: {
  pythonImage: string
  token: string
  mcpToken: string
  appData: string
}): string[] {
  return [
    input.pythonImage,
    '-m',
    'avkit_api',
    '--token',
    input.token,
    '--mcp-token',
    input.mcpToken,
    '--port',
    '0',
    '--app-data',
    input.appData,
  ]
}

export function buildPackagedSpawnArgv(input: {
  packagedBackend: string
  token: string
  mcpToken: string
  appData: string
}): string[] {
  return [
    input.packagedBackend,
    '--token',
    input.token,
    '--mcp-token',
    input.mcpToken,
    '--port',
    '0',
    '--app-data',
    input.appData,
  ]
}

export function packagedBackendPath(resourcesPath: string): string {
  return join(resourcesPath, 'avkit-backend', 'avkit-backend.exe')
}

export function assertOwnedIdentity(input: {
  ownedPid: number
  descriptorPid: number
  liveImage: string
  oursExe: string
}): boolean {
  return input.ownedPid === input.descriptorPid && input.liveImage === input.oursExe
}

export async function shutdownOwned(
  reason: 'quit' | 'child-exit',
  deps: {
    ownedPid: number | null
    foreignPid?: number
    signal: (pid: number) => void
    retireDescriptor: () => void
    retirePortSibling: () => void
    waitPid: (pid: number) => Promise<void>
  },
): Promise<void> {
  if (reason === 'quit' && deps.ownedPid !== null) {
    deps.signal(deps.ownedPid)
    await deps.waitPid(deps.ownedPid)
  }
  deps.retireDescriptor()
  deps.retirePortSibling()
}

// One test of READY, shared by the guard and the publisher so they cannot disagree.
const AVKIT_READY_LINE = /AVKIT_READY port=(\d+) instance=(\S+)/

function usableReadyPort(text: string): string | null {
  const match = AVKIT_READY_LINE.exec(text)
  return match === null || match[1] === '0' ? null : match[1]
}

export function confirmReadyAndPublish(input: {
  readyText: string
  ownedPid: number
  descriptorPid: number | null
  liveImage: string
  oursExe: string
  token: string
  publish: (ready: { apiBase: string; token: string }) => void
}): boolean {
  const port = usableReadyPort(input.readyText)
  if (port === null) {
    return false
  }
  // READY arrived on the stdout pipe of the child we spawned. That is the
  // ownership proof (07-distribution: wait for backend.json pid == child OR
  // AVKIT_READY). Pre-spawn live-identity (orphan reap/refuse) stays separate.
  // Do not withhold publish when CIM image/pid strings disagree — that is the
  // Windows delivery failure that left Add on "backend not ready".
  // D-977 (Session 82): no veto, as before; AC-154.4 pins it for the line reader below.
  void assertOwnedIdentity({
    ownedPid: input.ownedPid,
    descriptorPid: input.descriptorPid ?? -1,
    liveImage: input.liveImage,
    oursExe: input.oursExe,
  })
  input.publish({
    apiBase: `http://127.0.0.1:${port}/api/v1`,
    token: input.token,
  })
  return true
}

/**
 * Sends backend log lines to the window. The backend can write after the window has gone: reading
 * `webContents` from a destroyed window throws, and an uncaught throw in the output handler stops the
 * main process behind an error dialog. The lines stay in the in-memory log either way.
 */
export function forwardConsoleLines(
  window: { isDestroyed(): boolean; webContents: { send(channel: string, ...args: unknown[]): void } } | null,
  lines: unknown[],
): void {
  if (window === null || window.isDestroyed()) {
    return
  }
  try {
    window.webContents.send('console-log-batch', lines)
  } catch {
    // the renderer went away between the check and the send
  }
}

export function publishIfReady(input: {
  chunkText: string
  ownedPid: number
  readDescriptorPid: () => number | null
  queryLive: (pid: number) => LiveQuery
  oursExe: string
  token: string
  publish: (ready: { apiBase: string; token: string }) => void
}): boolean {
  // The query runs PowerShell synchronously on Windows; backend output arrives in many chunks.
  if (usableReadyPort(input.chunkText) === null) {
    return false
  }
  const live = input.queryLive(input.ownedPid)
  return confirmReadyAndPublish({
    readyText: input.chunkText,
    ownedPid: input.ownedPid,
    descriptorPid: input.readDescriptorPid(),
    liveImage: live.image ?? '',
    oursExe: input.oursExe,
    token: input.token,
    publish: input.publish,
  })
}

/** The longest ready line the reader keeps, in UTF-16 code units (`.length`, as capture-picker.ts:69). */
export const READY_LINE_MAX_LENGTH = 4_096

/**
 * Reads the owned child's stdout as lines for the ready handshake (D-979). It keeps the text after
 * the last newline, strips one trailing CR, skips empty lines and hands each whole line to
 * `publishLine` until one returns true; from then on it is latched and ignores all output. A line
 * longer than READY_LINE_MAX_LENGTH never reaches `publishLine`: a carry past the bound is dropped
 * and marked, and the rest of that line is dropped when its newline arrives.
 */
export function createReadyLineReader(publishLine: (line: string) => boolean): {
  push(chunkText: string): boolean
  readonly state: { pendingLength: number; discarded: boolean; published: boolean }
} {
  let pending = ''
  let discarded = false
  let published = false
  return {
    push(chunkText: string): boolean {
      if (published) {
        return false
      }
      const parts = (pending + chunkText).split('\n')
      pending = parts.pop() ?? ''
      for (const part of parts) {
        if (discarded) {
          discarded = false
          continue
        }
        const line = part.endsWith('\r') ? part.slice(0, -1) : part
        if (line.length === 0 || line.length > READY_LINE_MAX_LENGTH) {
          continue
        }
        if (publishLine(line)) {
          published = true
          pending = ''
          return true
        }
      }
      if (pending.length > READY_LINE_MAX_LENGTH) {
        pending = ''
        discarded = true
      }
      return false
    },
    get state() {
      return { pendingLength: pending.length, discarded, published }
    },
  }
}

export async function waitPidExit(
  pid: number,
  isRunning: (pid: number) => boolean,
  timeoutMs = 8000,
): Promise<void> {
  const deadline = Date.now() + timeoutMs
  while (Date.now() < deadline) {
    if (!isRunning(pid)) {
      return
    }
    await new Promise<void>((resolve) => {
      setTimeout(resolve, 50)
    })
  }
}

export function spawnOwned(argv: string[], env: NodeJS.ProcessEnv): ChildProcess {
  const [command, ...args] = argv
  if (command === undefined) {
    throw new Error('spawn argv is empty')
  }
  return spawn(command, args, { env, stdio: ['ignore', 'pipe', 'pipe'] })
}
