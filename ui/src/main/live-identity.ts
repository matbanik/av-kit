import { execFileSync } from 'node:child_process'
import { existsSync, readFileSync, realpathSync } from 'node:fs'

export type IdentityDecision = 'spawn' | 'reap_then_spawn' | 'refuse'

export type LiveQuery = {
  ok: boolean
  image?: string
  cmdline?: string
}

export type DescriptorFields = {
  schema_version: number
  pid: number
  executable_path: string
  app_data: string
  extraKeys?: string[]
}

function normalizePath(value: string): string {
  return value.replace(/\\/g, '/').replace(/^\/\/\?\//, '').toLowerCase()
}

function cmdlineHasAppData(cmdline: string | undefined, oursAppData: string): boolean {
  if (cmdline === undefined) {
    return false
  }
  const marker = '--app-data'
  const idx = cmdline.indexOf(marker)
  if (idx < 0) {
    return false
  }
  const rest = cmdline.slice(idx + marker.length).trim()
  const arg = rest.split(/\s+/)[0] ?? ''
  return normalizePath(arg) === normalizePath(oursAppData)
}

export function evaluateLiveIdentity(input: {
  lockHeld: boolean
  pidRunning: boolean
  query: LiveQuery
  oursExe: string
  oursAppData: string
  descriptor: DescriptorFields | null
}): { decision: IdentityDecision; signalPid: number | null } {
  if (!input.lockHeld) {
    return { decision: 'refuse', signalPid: null }
  }
  if (!input.pidRunning || input.descriptor === null) {
    return { decision: 'spawn', signalPid: null }
  }
  if (!input.query.ok) {
    return { decision: 'refuse', signalPid: null }
  }
  const liveImage = input.query.image ?? ''
  if (normalizePath(liveImage) !== normalizePath(input.oursExe)) {
    return { decision: 'refuse', signalPid: null }
  }
  if (!cmdlineHasAppData(input.query.cmdline, input.oursAppData)) {
    return { decision: 'refuse', signalPid: null }
  }
  if (input.descriptor.schema_version !== 1) {
    return { decision: 'refuse', signalPid: null }
  }
  if ((input.descriptor.extraKeys?.length ?? 0) > 0) {
    return { decision: 'refuse', signalPid: null }
  }
  if (normalizePath(input.descriptor.app_data) !== normalizePath(input.oursAppData)) {
    return { decision: 'refuse', signalPid: null }
  }
  if (normalizePath(input.descriptor.executable_path) !== normalizePath(liveImage)) {
    return { decision: 'refuse', signalPid: null }
  }
  return { decision: 'reap_then_spawn', signalPid: input.descriptor.pid }
}

const DESCRIPTOR_KNOWN_KEYS = new Set([
  'schema_version',
  'pid',
  'instance_id',
  'executable_path',
  'host',
  'port',
  'bind',
  'api_base',
  'app_data',
  'started_at',
])

export function parseDescriptorFields(raw: string | null): DescriptorFields | null {
  if (raw === null || raw.trim() === '') {
    return null
  }
  try {
    const parsed = JSON.parse(raw) as Record<string, unknown>
    if (typeof parsed.pid !== 'number') {
      return null
    }
    const extraKeys = Object.keys(parsed).filter(
      (key) => !DESCRIPTOR_KNOWN_KEYS.has(key) && key !== 'tombstone',
    )
    return {
      schema_version: typeof parsed.schema_version === 'number' ? parsed.schema_version : 0,
      pid: parsed.pid,
      executable_path: typeof parsed.executable_path === 'string' ? parsed.executable_path : '',
      app_data: typeof parsed.app_data === 'string' ? parsed.app_data : '',
      extraKeys,
    }
  } catch {
    return null
  }
}

export function isPidRunning(pid: number): boolean {
  if (!Number.isInteger(pid) || pid <= 0) {
    return false
  }
  try {
    process.kill(pid, 0)
    return true
  } catch {
    return false
  }
}

export function queryLiveProcess(pid: number): LiveQuery {
  try {
    if (process.platform === 'win32') {
      const script = `$p = Get-CimInstance Win32_Process -Filter "ProcessId=${Math.trunc(pid)}"; if ($null -eq $p) { exit 1 }; Write-Output $p.ExecutablePath; Write-Output $p.CommandLine`
      const out = execFileSync('powershell.exe', ['-NoProfile', '-Command', script], {
        encoding: 'utf8',
        timeout: 8000,
        windowsHide: true,
      })
      const lines = out
        .split(/\r?\n/)
        .map((line) => line.trim())
        .filter((line) => line.length > 0)
      if (lines[0] === undefined) {
        return { ok: false }
      }
      return { ok: true, image: lines[0], cmdline: lines.slice(1).join(' ') }
    }
    if (process.platform === 'linux') {
      return {
        ok: true,
        image: realpathSync(`/proc/${pid}/exe`),
        cmdline: existsSync(`/proc/${pid}/cmdline`)
          ? readFileSync(`/proc/${pid}/cmdline`, { encoding: 'utf8' }).replace(/\0/g, ' ')
          : '',
      }
    }
    const out = execFileSync('ps', ['-p', String(pid), '-o', 'comm=', '-o', 'command='], {
      encoding: 'utf8',
      timeout: 5000,
    }).trim()
    const [image, ...rest] = out.split(/\s+/)
    return { ok: true, image: image ?? '', cmdline: rest.join(' ') }
  } catch {
    return { ok: false }
  }
}

export function resolveBootIdentity(input: {
  lockHeld: boolean
  oursExe: string
  oursAppData: string
  descriptorRaw: string | null
  isPidRunning: (pid: number) => boolean
  queryLive: (pid: number) => LiveQuery
}): { decision: IdentityDecision; signalPid: number | null } {
  const descriptor = parseDescriptorFields(input.descriptorRaw)
  const pid = descriptor?.pid
  const pidRunning = pid !== undefined && input.isPidRunning(pid)
  const query = pidRunning && pid !== undefined ? input.queryLive(pid) : { ok: false }
  return evaluateLiveIdentity({
    lockHeld: input.lockHeld,
    pidRunning,
    query,
    oursExe: input.oursExe,
    oursAppData: input.oursAppData,
    descriptor,
  })
}
