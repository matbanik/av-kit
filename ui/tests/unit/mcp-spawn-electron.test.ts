import { spawn } from 'node:child_process'
import { existsSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

import { mcpServerEntry } from '../../src/main/mcp-setup-prompt'

const here = dirname(fileURLToPath(import.meta.url))
const uiRoot = resolve(here, '../..')
const repoRoot = resolve(uiRoot, '..')
const DEADLINE_MS = 15_000

/** The Electron binary, resolved as `electron/index.js` does (the Vitest config aliases `electron` to a stub). */
function electronBinary(): string {
  const pkg = resolve(uiRoot, 'node_modules/electron')
  return resolve(pkg, 'dist', readFileSync(resolve(pkg, 'path.txt'), 'utf8').trim())
}

/** FUSE_PIN: reasons an electron-builder config would switch the RunAsNode fuse off. */
function fusePinViolations(yml: string): string[] {
  const found: string[] = []
  if (/^\s*runAsNode\s*:\s*false\b/m.test(yml)) {
    found.push('runAsNode: false')
  }
  const fuses = yml.match(/^electronFuses\s*:\s*\n((?:[ \t]+.*\n?)*)/m)
  if (fuses !== null && /runAsNode\s*:\s*(false|no|off)\b/i.test(fuses[1])) {
    found.push('electronFuses disables runAsNode')
  }
  return found
}

type Answer = { kind: 'line'; line: string } | { kind: 'exit'; code: number | null; stderr: string } | { kind: 'deadline'; stderr: string }

/** Starts the child, writes one `initialize`, and settles on the first stdout line, an exit or the deadline (never rejects). */
function initializeOnce(command: string, args: string[]): Promise<Answer> {
  return new Promise((settle) => {
    const child = spawn(command, args, {
      env: { ...process.env, ELECTRON_RUN_AS_NODE: '1' },
      stdio: ['pipe', 'pipe', 'pipe'],
      windowsHide: true,
    })
    let out = ''
    let err = ''
    let done = false
    const finish = (answer: Answer) => {
      if (done) return
      done = true
      clearTimeout(timer)
      child.kill()
      settle(answer)
    }
    const timer = setTimeout(() => finish({ kind: 'deadline', stderr: err.slice(-800) }), DEADLINE_MS)
    child.on('error', (error) => finish({ kind: 'exit', code: null, stderr: String(error) }))
    child.on('exit', (code) => finish({ kind: 'exit', code, stderr: err.slice(-800) }))
    child.stderr.on('data', (chunk: Buffer) => {
      err += chunk.toString('utf8')
    })
    child.stdout.on('data', (chunk: Buffer) => {
      out += chunk.toString('utf8')
      const newline = out.indexOf('\n')
      if (newline >= 0) finish({ kind: 'line', line: out.slice(0, newline).trim() })
    })
    child.stdin.write(
      JSON.stringify({
        jsonrpc: '2.0',
        id: 1,
        method: 'initialize',
        params: { protocolVersion: '2025-06-18', capabilities: {}, clientInfo: { name: 's31b-ac-71-10', version: '0' } },
      }) + '\n',
    )
  })
}

describe('MEU-71 MCP_LAUNCH in dev (AC-71.10)', () => {
  it(
    'AC-71.10 Electron with ELECTRON_RUN_AS_NODE on the dev SERVER_ENTRY answers initialize as av-kit',
    async () => {
      const entry = mcpServerEntry({ packaged: false, resourcesPath: '', dirname: resolve(uiRoot, 'out/main') })
      expect(entry).toBe(resolve(repoRoot, 'mcp-server/dist/index.js'))
      expect(existsSync(entry), 'build mcp-server first').toBe(true)
      const answer = await initializeOnce(electronBinary(), [entry])
      expect(answer.kind, JSON.stringify(answer)).toBe('line')
      // The first stdout line is the JSON-RPC response: no Electron app output comes first.
      const response = JSON.parse((answer as { line: string }).line) as {
        jsonrpc: string
        id: number
        result?: { serverInfo?: { name?: string } }
      }
      expect(response.jsonrpc).toBe('2.0')
      expect(response.id).toBe(1)
      expect(response.result?.serverInfo?.name).toBe('av-kit')
    },
    DEADLINE_MS + 10_000,
  )

  it('AC-71.10 FUSE_PIN holds for electron-builder.yml', () => {
    const yml = readFileSync(resolve(uiRoot, 'electron-builder.yml'), 'utf8').replace(/\r\n/g, '\n')
    expect(fusePinViolations(yml)).toEqual([])
  })

  it('AC-71.10 negative: FUSE_PIN refuses runAsNode false and an electronFuses block that disables it', () => {
    expect(fusePinViolations('appId: x\nrunAsNode: false\n')).toEqual(['runAsNode: false'])
    expect(fusePinViolations('appId: x\nelectronFuses:\n  runAsNode: false\n  enableCookieEncryption: true\n')).toContain(
      'electronFuses disables runAsNode',
    )
    expect(fusePinViolations('appId: x\nelectronFuses:\n  enableCookieEncryption: true\n')).toEqual([])
  })
})
