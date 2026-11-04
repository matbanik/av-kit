import { basename } from 'node:path'

import { z } from 'zod'

import { readStartAtSignIn, writeStartAtSignIn, type LoginItemDeps } from './login-item'
import { buildSetupPrompt, MCP_CLIENTS, type McpClient, type McpScope } from './mcp-setup-prompt'

export const STARTUP_METRIC_KEYS = [
  'startup.python_spawn_ms',
  'startup.renderer_load_ms',
  'startup.shell_paint_ms',
  'startup.window_show_ms',
  'startup.data_ready_ms',
  'startup.lazy_preload_ms',
] as const

export const SHOW_FILES_PROPERTIES = ['openFile', 'multiSelections'] as const

export const RENDERER_TO_MAIN_CHANNELS = [
  'get-backend-url',
  'get-token',
  'startup-metric',
  'show-directory-dialog',
  'show-file-dialog',
  'show-files-dialog',
  'open-path',
  'show-item-in-folder',
  'read-clipboard-text',
  'write-clipboard-text',
  'read-text-file',
  'copy-mcp-config',
  'get-log-snapshot',
  'get-setup-readiness',
  'get-mcp-access-status',
  'capture-region',
  'get-hotkey-status',
  'login-item-get',
  'login-item-set',
  'write-clipboard-image',
  'get-mcp-setup-prompt',
] as const

export const PNG_SIGNATURE = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a] as const
export const COPY_IMAGE_MAX_BYTES = 64 * 1024 * 1024
export const IMAGE_DECODE_ERROR = 'image could not be decoded'
export const LAUNCH_MISSING_ERROR = 'the MCP server launch is not configured'

function hasPngSignature(bytes: Uint8Array): boolean {
  return PNG_SIGNATURE.every((byte, index) => bytes[index] === byte)
}

const noPayloadSchema = z.union([z.undefined(), z.object({}).strict()])

const schemas: Record<(typeof RENDERER_TO_MAIN_CHANNELS)[number], z.ZodType> = {
  'get-backend-url': noPayloadSchema,
  'get-token': noPayloadSchema,
  'startup-metric': z
    .object({
      key: z.enum(STARTUP_METRIC_KEYS),
      value: z.number(),
      timestamp: z.number(),
    })
    .strict(),
  'show-directory-dialog': noPayloadSchema,
  'show-file-dialog': z
    .object({
      filters: z
        .array(z.object({ name: z.string(), extensions: z.array(z.string()) }).strict())
        .optional(),
    })
    .strict(),
  'show-files-dialog': z
    .object({
      filters: z
        .array(z.object({ name: z.string(), extensions: z.array(z.string()) }).strict())
        .optional(),
    })
    .strict(),
  'open-path': z.object({ target: z.string().min(1) }).strict(),
  'show-item-in-folder': z.object({ target: z.string().min(1) }).strict(),
  'read-clipboard-text': noPayloadSchema,
  'write-clipboard-text': z.object({ text: z.string() }).strict(),
  'read-text-file': z
    .object({
      maxBytes: z.number().int().positive().max(2_097_152).optional(),
    })
    .strict(),
  'copy-mcp-config': z.object({ pinEndpoint: z.boolean().optional() }).strict(),
  'get-log-snapshot': noPayloadSchema,
  'get-setup-readiness': noPayloadSchema,
  'get-mcp-access-status': noPayloadSchema,
  'capture-region': noPayloadSchema,
  'get-hotkey-status': noPayloadSchema,
  'login-item-get': noPayloadSchema,
  'login-item-set': z
    .object({
      enabled: z.boolean(),
      minimized: z.boolean(),
    })
    .strict(),
  'write-clipboard-image': z
    .object({
      png: z
        .instanceof(Uint8Array)
        .refine((png) => png.byteLength > 0 && png.byteLength <= COPY_IMAGE_MAX_BYTES, 'png size out of range')
        .refine(hasPngSignature, 'png signature missing'),
    })
    .strict(),
  'get-mcp-setup-prompt': z.object({ client: z.enum(MCP_CLIENTS), scope: z.enum(['user', 'project']) }).strict(),
}

export type SideEffects = {
  dialog: number
  fs: number
  clipboard: number
  spawn: number
}

export type IpcResult = { ok: true; value: unknown } | { ok: false; error: string }

export type SetupReadiness = {
  descriptorPresent: boolean
  portOk: boolean
  modelsDirWritable: boolean
  logFilePath: string
}

export type McpAccessStatus = {
  tokenPresent: boolean
}

export type IpcDeps = {
  sideEffects?: SideEffects
  appData?: string
  showDirectoryDialog?: () => Promise<string | undefined>
  showFileDialog?: (filters?: { name: string; extensions: string[] }[]) => Promise<string | undefined>
  showFilesDialog?: (filters?: { name: string; extensions: string[] }[]) => Promise<string[]>
  probeSetupReadiness?: () => Promise<SetupReadiness>
  readFile?: (path: string) => Promise<string>
  openPath?: (target: string) => Promise<void>
  showItemInFolder?: (target: string) => Promise<void>
  readMcpToken?: () => Promise<string>
  readClipboard?: () => Promise<string>
  writeClipboard?: (text: string) => Promise<void>
  writeClipboardImage?: (png: Uint8Array) => Promise<boolean>
  guiNonce?: string
  mcpToken?: string
  postStartupMetric?: (input: {
    url: string
    authorization: string
    key: string
    value: number
    timestamp: number
  }) => Promise<void>
  captureRegion?: () => Promise<void>
  getHotkeyStatus?: () => Promise<{ accelerator: string; registered: boolean; inUse: boolean }>
  loginItem?: LoginItemDeps
  mcpServerLaunch?: { command: string; serverPath: string }
}

export const BACKEND_READY_TIMEOUT_MS = 10_000

type ReadyState = { apiBase: string; token: string }

let ready: ReadyState | null = null
let waiters: Array<(result: IpcResult) => void> = []
let logSnapshot: Array<{ key: string; message: string; id: string }> = []

function isPortZeroUrl(apiBase: string): boolean {
  try {
    const url = new URL(apiBase)
    return url.port === '0'
  } catch {
    return apiBase.includes(':0/')
  }
}

export function resetBackendIpcState(): void {
  ready = null
  waiters = []
  logSnapshot = []
}

export function appendStdoutLog(message: string): { key: string; message: string; id: string } {
  const n = logSnapshot.length + 1
  const item = { key: `ipc:${n}`, message, id: `ipc:${n}` }
  logSnapshot.push(item)
  return item
}

export function getPublishedBackendReady(): ReadyState | null {
  return ready
}

export function publishBackendReady(input: { apiBase: string; token: string }): void {
  if (isPortZeroUrl(input.apiBase)) {
    const result: IpcResult = { ok: false, error: 'pre-listen port 0 is not a URL' }
    for (const resolve of waiters) {
      resolve(result)
    }
    waiters = []
    return
  }
  ready = input
  const result: IpcResult = { ok: true, value: input.apiBase }
  for (const resolve of waiters) {
    resolve(result)
  }
  waiters = []
}

export function usesSendSync(): boolean {
  return false
}

export function createWebPreferences(): {
  nodeIntegration: false
  contextIsolation: true
  sandbox: true
  webSecurity: true
} {
  return {
    nodeIntegration: false,
    contextIsolation: true,
    sandbox: true,
    webSecurity: true,
  }
}

export function listRegisteredChannels(): string[] {
  return [...RENDERER_TO_MAIN_CHANNELS]
}

function waitForBackendUrl(): Promise<IpcResult> {
  if (ready !== null) {
    return Promise.resolve({ ok: true, value: ready.apiBase })
  }
  return new Promise((resolve) => {
    let settled = false
    const timer = setTimeout(() => {
      if (settled) {
        return
      }
      settled = true
      waiters = waiters.filter((waiter) => waiter !== onReady)
      resolve({ ok: false, error: 'backend not ready' })
    }, BACKEND_READY_TIMEOUT_MS)
    const onReady = (result: IpcResult) => {
      if (settled) {
        return
      }
      settled = true
      clearTimeout(timer)
      resolve(result)
    }
    waiters.push(onReady)
  })
}

function normalize(path: string): string {
  return path.replace(/\\/g, '/').toLowerCase()
}

function isUrl(target: string): boolean {
  return /^[a-zA-Z][a-zA-Z0-9+.-]*:\/\//.test(target)
}

function isDeniedPath(target: string, appData: string): boolean {
  if (isUrl(target)) {
    return true
  }
  const norm = normalize(target)
  const root = normalize(appData)
  if (norm.includes('token')) {
    return true
  }
  if (norm.endsWith('/backend.json') || norm.endsWith('/avkit.db')) {
    return true
  }
  if (root !== '' && (norm === root || norm.startsWith(`${root}/`))) {
    return true
  }
  if (/\.(exe|bat|cmd|com|msi|dll|ps1|scr)$/.test(norm)) {
    return true
  }
  return false
}

function allowedTextExt(path: string): boolean {
  return path.toLowerCase().endsWith('.txt') || path.toLowerCase().endsWith('.md')
}

function resolveLoginItemDeps(deps: IpcDeps): LoginItemDeps {
  if (deps.loginItem !== undefined) {
    return deps.loginItem
  }
  return {
    platform: process.platform,
    packaged: false,
    execPath: process.execPath,
    getLoginItemSettings: () => ({ openAtLogin: false }),
    setLoginItemSettings: () => undefined,
  }
}

export async function handleIpc(
  channel: string,
  payload: unknown,
  deps: IpcDeps = {},
): Promise<IpcResult> {
  if (!(RENDERER_TO_MAIN_CHANNELS as readonly string[]).includes(channel)) {
    return { ok: false, error: `unknown channel ${channel}` }
  }
  const parsed = schemas[channel as (typeof RENDERER_TO_MAIN_CHANNELS)[number]].safeParse(payload)
  if (!parsed.success) {
    return { ok: false, error: parsed.error.message }
  }
  const effects = deps.sideEffects ?? { dialog: 0, fs: 0, clipboard: 0, spawn: 0 }
  const appData = deps.appData ?? ''

  switch (channel) {
    case 'get-backend-url':
      return waitForBackendUrl()
    case 'get-token':
      if (ready === null) {
        const waited = await waitForBackendUrl()
        if (!waited.ok) {
          return waited
        }
      }
      return { ok: true, value: ready?.token }
    case 'startup-metric': {
      if (ready === null) {
        const waited = await waitForBackendUrl()
        if (!waited.ok) {
          return waited
        }
      }
      const payload = parsed.data as { key: string; value: number; timestamp: number }
      const nonce = deps.guiNonce ?? ready?.token ?? ''
      const base = ready?.apiBase
      if (base === undefined) {
        return { ok: false, error: 'backend not ready' }
      }
      await deps.postStartupMetric?.({
        url: `${base}/health/startup-metrics`,
        authorization: `Bearer ${nonce}`,
        key: payload.key,
        value: payload.value,
        timestamp: payload.timestamp,
      })
      return { ok: true, value: undefined }
    }
    case 'show-directory-dialog': {
      effects.dialog += 1
      const chosen = await deps.showDirectoryDialog?.()
      return { ok: true, value: chosen }
    }
    case 'show-file-dialog': {
      effects.dialog += 1
      const filters = (parsed.data as { filters?: { name: string; extensions: string[] }[] }).filters
      const chosen = await deps.showFileDialog?.(filters)
      return { ok: true, value: chosen }
    }
    case 'show-files-dialog': {
      effects.dialog += 1
      const filters = (parsed.data as { filters?: { name: string; extensions: string[] }[] }).filters
      const chosen = await deps.showFilesDialog?.(filters)
      return { ok: true, value: chosen ?? [] }
    }
    case 'open-path': {
      const target = (parsed.data as { target: string }).target
      if (isDeniedPath(target, appData)) {
        return { ok: false, error: 'path denied' }
      }
      effects.fs += 1
      await deps.openPath?.(target)
      return { ok: true, value: undefined }
    }
    case 'show-item-in-folder': {
      const target = (parsed.data as { target: string }).target
      if (isDeniedPath(target, appData)) {
        return { ok: false, error: 'path denied' }
      }
      effects.fs += 1
      await deps.showItemInFolder?.(target)
      return { ok: true, value: undefined }
    }
    case 'read-clipboard-text': {
      effects.clipboard += 1
      const text = (await deps.readClipboard?.()) ?? ''
      return { ok: true, value: text }
    }
    case 'write-clipboard-text': {
      const text = (parsed.data as { text: string }).text
      effects.clipboard += 1
      await deps.writeClipboard?.(text)
      return { ok: true, value: undefined }
    }
    case 'read-text-file': {
      effects.dialog += 1
      const chosen = await deps.showFileDialog?.()
      if (chosen === undefined) {
        return { ok: false, error: 'cancelled' }
      }
      if (isDeniedPath(chosen, appData) || !allowedTextExt(chosen)) {
        return { ok: false, error: 'path denied' }
      }
      effects.fs += 1
      const maxBytes = (parsed.data as { maxBytes?: number }).maxBytes ?? 2_097_152
      const body = (await deps.readFile?.(chosen)) ?? ''
      const sliced = Buffer.from(body, 'utf8').subarray(0, maxBytes).toString('utf8')
      return { ok: true, value: { text: sliced, basename: basename(chosen) } }
    }
    case 'copy-mcp-config': {
      const token = (await deps.readMcpToken?.()) ?? ''
      const pin = (parsed.data as { pinEndpoint?: boolean }).pinEndpoint === true
      const payloadToCopy: Record<string, string> = {
        AVKIT_API_TOKEN: token,
        AVKIT_APP_DATA: appData,
      }
      if (pin && ready !== null) {
        payloadToCopy.AVKIT_API_BASE = ready.apiBase
      }
      const text = JSON.stringify(payloadToCopy)
      await deps.writeClipboard?.(text)
      return { ok: true, value: { ok: true } }
    }
    case 'get-log-snapshot':
      return { ok: true, value: [...logSnapshot] }
    case 'get-setup-readiness': {
      const status = await deps.probeSetupReadiness?.()
      if (status === undefined) {
        return { ok: false, error: 'setup readiness probe unavailable' }
      }
      return { ok: true, value: status }
    }
    case 'get-mcp-access-status': {
      const token = (await deps.readMcpToken?.()) ?? ''
      return { ok: true, value: { tokenPresent: token.trim().length > 0 } satisfies McpAccessStatus }
    }
    case 'capture-region': {
      await deps.captureRegion?.()
      return { ok: true, value: undefined }
    }
    case 'get-hotkey-status': {
      const status = await deps.getHotkeyStatus?.()
      return { ok: true, value: status ?? { accelerator: 'F2', registered: false, inUse: false } }
    }
    case 'login-item-get': {
      return { ok: true, value: readStartAtSignIn(resolveLoginItemDeps(deps)) }
    }
    case 'login-item-set': {
      const body = parsed.data as { enabled: boolean; minimized: boolean }
      return {
        ok: true,
        value: writeStartAtSignIn(body.enabled, body.minimized, resolveLoginItemDeps(deps)),
      }
    }
    case 'write-clipboard-image': {
      const png = (parsed.data as { png: Uint8Array }).png
      effects.clipboard += 1
      const written = (await deps.writeClipboardImage?.(png)) ?? false
      if (!written) {
        return { ok: false, error: IMAGE_DECODE_ERROR }
      }
      return { ok: true, value: undefined }
    }
    case 'get-mcp-setup-prompt': {
      // The prompt names the app data folder, never the token: the server reads the token itself.
      if (deps.mcpServerLaunch === undefined) {
        return { ok: false, error: LAUNCH_MISSING_ERROR }
      }
      const { client, scope } = parsed.data as { client: McpClient; scope: McpScope }
      try {
        const text = buildSetupPrompt({ client, scope, ...deps.mcpServerLaunch, appData })
        return { ok: true, value: { text } }
      } catch (error) {
        return { ok: false, error: error instanceof Error ? error.message : String(error) }
      }
    }
    default:
      return { ok: false, error: `unknown channel ${channel}` }
  }
}
