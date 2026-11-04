import { spawn, type ChildProcess } from 'node:child_process'
import { realpathSync } from 'node:fs'
import { join } from 'node:path'

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

export function confirmReadyAndPublish(input: {
  readyText: string
  ownedPid: number
  descriptorPid: number | null
  liveImage: string
  oursExe: string
  token: string
  publish: (ready: { apiBase: string; token: string }) => void
}): boolean {
  const match = /AVKIT_READY port=(\d+) instance=(\S+)/.exec(input.readyText)
  if (match === null || match[1] === '0') {
    return false
  }
  // READY arrived on the stdout pipe of the child we spawned. That is the
  // ownership proof (07-distribution: wait for backend.json pid == child OR
  // AVKIT_READY). Pre-spawn live-identity (orphan reap/refuse) stays separate.
  // Do not withhold publish when CIM image/pid strings disagree — that is the
  // Windows delivery failure that left Add on "backend not ready".
  void assertOwnedIdentity({
    ownedPid: input.ownedPid,
    descriptorPid: input.descriptorPid ?? -1,
    liveImage: input.liveImage,
    oursExe: input.oursExe,
  })
  input.publish({
    apiBase: `http://127.0.0.1:${match[1]}/api/v1`,
    token: input.token,
  })
  return true
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
