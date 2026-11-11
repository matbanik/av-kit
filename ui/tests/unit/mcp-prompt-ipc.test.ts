import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it, vi } from 'vitest'

import { handleIpc, listRegisteredChannels, type IpcDeps } from '../../src/main/ipc'
import { getPreloadApiKeys } from '../../src/main/preload'
import { RENDERER_TO_MAIN_CHANNELS } from './ipc-channels'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')

const CHANNEL = 'get-mcp-setup-prompt'
const SECRET = 'tok-s31b-ipc-secret-81d3'
const LAUNCH = {
  command: 'C:\\Program Files\\av-kit\\av-kit.exe',
  serverPath: 'C:\\Program Files\\av-kit\\resources\\mcp-server\\index.mjs',
}
const APP_DATA = 'C:\\Users\\Test User\\AppData\\Local\\av-kit'

function deps(withLaunch = true): { deps: IpcDeps; readMcpToken: ReturnType<typeof vi.fn> } {
  const readMcpToken = vi.fn(async () => SECRET)
  const effects = { dialog: 0, fs: 0, clipboard: 0, spawn: 0 }
  const base = { sideEffects: effects, appData: APP_DATA, readMcpToken, mcpToken: SECRET }
  return {
    deps: (withLaunch ? { ...base, mcpServerLaunch: LAUNCH } : base) as IpcDeps,
    readMcpToken,
  }
}

describe('MEU-71 PROMPT_HANDLER (AC-71.6)', () => {
  it('AC-71.6 returns the Codex prompt text with the launch and app data, never reading the token', async () => {
    const { deps: d, readMcpToken } = deps()
    const result = await handleIpc(CHANNEL, { client: 'codex', scope: 'user' }, d)
    expect(result.ok, JSON.stringify(result)).toBe(true)
    const text = (result as { ok: true; value: { text: string } }).value.text
    expect(Object.keys((result as { ok: true; value: object }).value)).toEqual(['text'])
    expect(text).toContain('[mcp_servers.avkit]')
    expect(text).toContain(JSON.stringify(LAUNCH.command))
    expect(text).toContain(JSON.stringify(LAUNCH.serverPath))
    expect(text).toContain(JSON.stringify(APP_DATA))
    expect(readMcpToken).toHaveBeenCalledTimes(0)
    expect(text).not.toContain(SECRET)
    expect(d.sideEffects).toEqual({ dialog: 0, fs: 0, clipboard: 0, spawn: 0 })
  })

  it('AC-71.6 negative: bad payloads, a missing launch and a user-only client at project scope return ok false', async () => {
    for (const payload of [
      { client: 'zed', scope: 'user' },
      { client: 'codex' },
      { client: 'codex', scope: 'user', token: 'x' },
    ]) {
      const { deps: d, readMcpToken } = deps()
      const result = await handleIpc(CHANNEL, payload, d)
      expect(result.ok, JSON.stringify(payload)).toBe(false)
      // A schema rejection, not the unknown-channel refusal.
      expect((result as { ok: false; error: string }).error).not.toMatch(/unknown channel/)
      expect(readMcpToken).toHaveBeenCalledTimes(0)
    }
    const missing = await handleIpc(CHANNEL, { client: 'codex', scope: 'user' }, deps(false).deps)
    expect(missing).toEqual({ ok: false, error: 'the MCP server launch is not configured' })
    const generic = await handleIpc(CHANNEL, { client: 'generic', scope: 'project' }, deps().deps)
    expect(generic).toEqual({ ok: false, error: 'Other MCP client has no project-scope config; use user scope' })
  })
})

describe('MEU-71 PROMPT_CHANNEL and PRELOAD_KEY (AC-71.7)', () => {
  it('AC-71.7 the channel is registered, the list has 22 entries, and preload invokes it with opts', () => {
    const registered = listRegisteredChannels()
    expect(RENDERER_TO_MAIN_CHANNELS).toHaveLength(22)
    expect(registered).toEqual([...RENDERER_TO_MAIN_CHANNELS])
    expect(registered.indexOf(CHANNEL)).toBe(registered.indexOf('write-clipboard-image') + 1)
    expect(getPreloadApiKeys()).toContain('getMcpSetupPrompt')
    const preload = readFileSync(resolve(repoRoot, 'ui/src/main/preload.ts'), 'utf8')
    expect(preload).toMatch(
      /getMcpSetupPrompt: \(opts: \{ client: string; scope: 'user' \| 'project' \}\) =>\s*ipcRenderer\.invoke\('get-mcp-setup-prompt', opts\)/,
    )
  })

  it('AC-71.7 negative: a wrong-type payload is refused by the schema', async () => {
    for (const payload of [{ client: 4, scope: 'user' }, { client: 'codex', scope: 'local' }, 'codex', null]) {
      const result = await handleIpc(CHANNEL, payload, deps().deps)
      expect(result.ok, JSON.stringify(payload)).toBe(false)
      expect((result as { ok: false; error: string }).error).not.toMatch(/unknown channel/)
    }
  })
})
