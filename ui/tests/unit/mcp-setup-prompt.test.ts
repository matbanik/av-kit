import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

import { buildSetupPrompt, MCP_CLIENTS } from '../../src/main/mcp-setup-prompt'

const here = dirname(fileURLToPath(import.meta.url))
const goldenDir = resolve(here, 'fixtures/mcp-setup-prompt')

// Fixed inputs: paths with spaces and backslashes (AC-71.1).
const COMMAND = 'C:\\Program Files\\av-kit\\av-kit.exe'
const SERVER_PATH = 'C:\\Program Files\\av-kit\\resources\\mcp-server\\index.mjs'
const APP_DATA = 'C:\\Users\\Test User\\AppData\\Local\\av-kit'
const FIXTURE_TOKEN = 'tok-s31b-fixture-5f2c9a'

// CLIENT_SET (plan contracts table), in order.
const CLIENT_SET = ['claude-code', 'codex', 'cursor', 'vscode', 'claude-desktop', 'windsurf', 'generic'] as const
const LABELS: Record<(typeof CLIENT_SET)[number], string> = {
  'claude-code': 'Claude Code',
  codex: 'Codex',
  cursor: 'Cursor',
  vscode: 'VS Code',
  'claude-desktop': 'Claude Desktop',
  windsurf: 'Windsurf (community)',
  generic: 'Other MCP client',
}
const PROJECT_CLIENTS = ['claude-code', 'codex', 'cursor', 'vscode'] as const
const USER_ONLY = ['claude-desktop', 'windsurf', 'generic'] as const
const PROJECT_FILES: Record<(typeof PROJECT_CLIENTS)[number], string> = {
  'claude-code': '.mcp.json',
  codex: '.codex/config.toml',
  cursor: '.cursor/mcp.json',
  vscode: '.vscode/mcp.json',
}
const PATH_QUOTE_ERROR = 'a path contains a quote, $ or backtick; use the Other MCP client block'

type Client = (typeof CLIENT_SET)[number]
type Scope = 'user' | 'project'

const PAIRS: Array<{ client: Client; scope: Scope }> = [
  ...CLIENT_SET.map((client) => ({ client, scope: 'user' as const })),
  ...PROJECT_CLIENTS.map((client) => ({ client, scope: 'project' as const })),
]

function build(client: string, scope: Scope, over: Partial<{ command: string; serverPath: string; appData: string }> = {}): string {
  return buildSetupPrompt({
    client,
    scope,
    command: over.command ?? COMMAND,
    serverPath: over.serverPath ?? SERVER_PATH,
    appData: over.appData ?? APP_DATA,
  } as Parameters<typeof buildSetupPrompt>[0])
}

function normalise(text: string): string {
  return text.replace(/\r\n/g, '\n')
}

function fenced(text: string, lang: string): string {
  const match = text.match(new RegExp('```' + lang + '\\n([\\s\\S]*?)\\n```'))
  expect(match, `no ${lang} block`).not.toBeNull()
  return (match as RegExpMatchArray)[1]
}

/** A minimal TOML table reader: `[table]` headers and `key = <JSON value>` lines (CODEX_BLOCK quotes with JSON.stringify). */
function parseTomlTables(toml: string): Record<string, Record<string, unknown>> {
  const tables: Record<string, Record<string, unknown>> = {}
  let current: Record<string, unknown> | null = null
  for (const line of toml.split('\n')) {
    if (line.trim() === '') continue
    const header = line.match(/^\[([A-Za-z0-9_.]+)\]$/)
    if (header !== null) {
      current = {}
      tables[header[1]] = current
      continue
    }
    const pair = line.match(/^([A-Za-z0-9_]+) = (.+)$/)
    expect(pair, `not a TOML key line: ${line}`).not.toBeNull()
    expect(current, `key outside a table: ${line}`).not.toBeNull()
    ;(current as Record<string, unknown>)[(pair as RegExpMatchArray)[1]] = JSON.parse((pair as RegExpMatchArray)[2])
  }
  return tables
}

const LAUNCH = {
  command: COMMAND,
  args: [SERVER_PATH],
  env: { ELECTRON_RUN_AS_NODE: '1', AVKIT_APP_DATA: APP_DATA },
}

describe('MEU-71 PROMPT_BUILDER (AC-71.1 to AC-71.4)', () => {
  it('AC-71.1 MCP_CLIENTS is CLIENT_SET in order', () => {
    expect([...MCP_CLIENTS]).toEqual([...CLIENT_SET])
  })

  it('AC-71.1 every client and scope pair equals its golden file', () => {
    for (const { client, scope } of PAIRS) {
      const golden = normalise(readFileSync(resolve(goldenDir, `${client}-${scope}.txt`), 'utf8'))
      expect(normalise(build(client, scope)) + '\n', `${client}-${scope}`).toBe(golden)
    }
  })

  it('AC-71.1 the JSON and TOML blocks parse and carry MCP_LAUNCH', () => {
    for (const { client, scope } of PAIRS) {
      const text = build(client, scope)
      if (client === 'claude-code') continue
      if (client === 'codex') {
        const tables = parseTomlTables(fenced(text, 'toml'))
        expect(Object.keys(tables)).toEqual(['mcp_servers.avkit', 'mcp_servers.avkit.env'])
        expect(tables['mcp_servers.avkit']).toEqual({ command: LAUNCH.command, args: LAUNCH.args })
        expect(tables['mcp_servers.avkit.env']).toEqual(LAUNCH.env)
        expect(Object.keys(tables['mcp_servers.avkit.env'])).toEqual(['ELECTRON_RUN_AS_NODE', 'AVKIT_APP_DATA'])
        continue
      }
      const parsed = JSON.parse(fenced(text, 'json')) as Record<string, Record<string, Record<string, unknown>>>
      const container = client === 'vscode' ? 'servers' : 'mcpServers'
      expect(Object.keys(parsed)).toEqual([container])
      expect(Object.keys(parsed[container])).toEqual(['avkit'])
      const entry = parsed[container].avkit
      const expected = client === 'vscode' ? { type: 'stdio', ...LAUNCH } : LAUNCH
      expect(entry, `${client}-${scope}`).toEqual(expected)
      expect(Object.keys(entry.env as Record<string, string>)).toEqual(['ELECTRON_RUN_AS_NODE', 'AVKIT_APP_DATA'])
    }
  })

  it('AC-71.1 the Claude Code block carries MCP_LAUNCH on one add line', () => {
    const text = build('claude-code', 'user')
    expect(text).toContain(
      `claude mcp add avkit --scope user -e ELECTRON_RUN_AS_NODE=1 -e "AVKIT_APP_DATA=${APP_DATA}" -- "${COMMAND}" "${SERVER_PATH}"`,
    )
    expect(text).toContain('claude mcp remove avkit --scope user')
    expect(text.indexOf('claude mcp remove avkit')).toBeLessThan(text.indexOf('claude mcp add avkit'))
  })

  it('AC-71.1 negative: swapping command and serverPath changes every output', () => {
    for (const { client, scope } of PAIRS) {
      const swapped = build(client, scope, { command: SERVER_PATH, serverPath: COMMAND })
      expect(swapped, `${client}-${scope}`).not.toBe(build(client, scope))
    }
  })

  it('AC-71.1 negative: a Codex path containing a quote keeps the TOML string valid', () => {
    const quoted = 'C:\\Tools\\say "hi"\\av-kit.exe'
    const text = build('codex', 'user', { command: quoted })
    expect(text).toContain('command = "C:\\\\Tools\\\\say \\"hi\\"\\\\av-kit.exe"')
    const tables = parseTomlTables(fenced(text, 'toml'))
    expect(tables['mcp_servers.avkit'].command).toBe(quoted)
  })

  it('AC-71.2 SCOPE_RULE: project scope names the project file and user scope the user file', () => {
    for (const client of PROJECT_CLIENTS) {
      const text = build(client, 'project')
      expect(text, client).toContain(`${PROJECT_FILES[client]} in the repository root`)
      expect(text, client).toContain('(project scope: this project only)')
    }
    expect(build('claude-code', 'project')).toContain('claude mcp add avkit --scope project ')
    expect(build('claude-code', 'project')).toContain('claude mcp remove avkit --scope project')
    expect(build('claude-code', 'user')).toContain('claude mcp add avkit --scope user ')
    expect(build('claude-code', 'user')).toContain('~/.claude.json')
    expect(build('codex', 'user')).toContain('~/.codex/config.toml')
    expect(build('cursor', 'user')).toContain('~/.cursor/mcp.json')
    expect(build('vscode', 'user')).toContain('%APPDATA%\\Code\\User\\mcp.json')
    expect(build('vscode', 'user')).toContain('MCP: Open User Configuration')
    expect(build('claude-desktop', 'user')).toContain('%APPDATA%\\Claude\\claude_desktop_config.json')
    expect(build('claude-desktop', 'user')).toContain(
      '%LOCALAPPDATA%\\Packages\\Claude_*\\LocalCache\\Roaming\\Claude\\claude_desktop_config.json',
    )
    expect(build('windsurf', 'user')).toContain('~/.codeium/windsurf/mcp_config.json')
  })

  it('AC-71.2 negative: project scope throws PROJECT_SCOPE_ERROR for user-only clients; no local or scopeless add', () => {
    for (const client of USER_ONLY) {
      expect(() => build(client, 'project'), client).toThrow(
        new Error(`${LABELS[client]} has no project-scope config; use user scope`),
      )
    }
    for (const { client, scope } of PAIRS) {
      const text = build(client, scope)
      expect(text).not.toContain('--scope local')
      for (const line of text.split('\n').filter((l) => l.includes('claude mcp add'))) {
        expect(line).toMatch(/ --scope (user|project) /)
      }
    }
  })

  it('AC-71.3 TOKEN_BOUNDARY: every output carries AVKIT_APP_DATA with the given appData and ELECTRON_RUN_AS_NODE', () => {
    for (const { client, scope } of PAIRS) {
      const text = build(client, scope)
      expect(text, `${client}-${scope}`).toContain('AVKIT_APP_DATA')
      expect(text, `${client}-${scope}`).toContain('ELECTRON_RUN_AS_NODE')
      const appDataShown = client === 'claude-code' ? APP_DATA : JSON.stringify(APP_DATA)
      expect(text, `${client}-${scope}`).toContain(appDataShown)
    }
  })

  it('AC-71.3 negative: no output holds the token, AVKIT_API_TOKEN or ${; a $ path throws PATH_QUOTE_ERROR', () => {
    for (const { client, scope } of PAIRS) {
      const text = build(client, scope)
      expect(text).not.toContain(FIXTURE_TOKEN)
      expect(text).not.toContain('AVKIT_API_TOKEN')
      expect(text).not.toContain('${')
    }
    expect(buildSetupPrompt.length).toBe(1)
    for (const bad of ['C:\\a$b\\av-kit.exe', 'C:\\a"b\\av-kit.exe', 'C:\\a`b\\av-kit.exe']) {
      expect(() => build('claude-code', 'user', { command: bad })).toThrow(new Error(PATH_QUOTE_ERROR))
      expect(() => build('claude-code', 'user', { serverPath: bad })).toThrow(new Error(PATH_QUOTE_ERROR))
      expect(() => build('claude-code', 'user', { appData: bad })).toThrow(new Error(PATH_QUOTE_ERROR))
    }
  })

  it('AC-71.4 PROMPT_STEPS appear in order and the output ends with RESULT_LINE', () => {
    for (const { client, scope } of PAIRS) {
      const text = build(client, scope)
      const label = LABELS[client]
      const lines = text.split('\n')
      expect(lines[0], `${client}-${scope}`).toContain(label)
      expect(lines[0]).toContain(scope === 'user' ? 'user scope' : 'project scope')
      const marks = [
        '1. Find:',
        '2. Back up:',
        '.avkit-backup-<UTC yyyyMMddTHHmmssZ>',
        'If it does not exist yet, skip the backup.',
        '3. Merge: change only the avkit entry and keep every other entry.',
        '```',
        `If the tools do not appear, quit and reopen ${label}, then reply Ready.`,
        '5. Verify: call the avkit_health tool with action: "dependencies".',
        '6. Result:',
      ]
      let at = -1
      for (const mark of marks) {
        const next = text.indexOf(mark, at + 1)
        expect(next, `${client}-${scope}: ${mark}`).toBeGreaterThan(at)
        at = next
      }
      const last = lines[lines.length - 1]
      expect(last.startsWith('6. Result: end your reply with exactly one line')).toBe(true)
      expect(last).toContain('RESULT: connected')
      expect(last).toContain('RESULT: failed (<step>, <error>)')
      expect(last).toContain('backup, merge, restart or verify')
    }
  })

  it('AC-71.4 negative: liveness never counts and token_missing maps to RESULT: failed (verify, token_missing)', () => {
    for (const { client, scope } of PAIRS) {
      const text = build(client, scope)
      expect(text).toContain('A "liveness" result never counts as verified.')
      expect(text).toContain('an error starting "token_missing:" gives RESULT: failed (verify, token_missing)')
    }
  })

  it('AC-71.4 negative: Claude Desktop backs up the one file step 1 chose, MSIX included (review F1)', () => {
    const lines = build('claude-desktop', 'user').split('\n')
    const find = lines.find((l) => l.startsWith('1. Find:')) ?? ''
    const backup = lines.find((l) => l.startsWith('2. Back up:')) ?? ''
    // Step 1 settles on exactly one file: MSIX when its package folder exists, else the standard one.
    expect(find).toContain('%LOCALAPPDATA%\\Packages\\Claude_*\\LocalCache\\Roaming\\Claude\\claude_desktop_config.json if')
    expect(find).toContain('otherwise it is %APPDATA%\\Claude\\claude_desktop_config.json')
    expect(find).toContain('Use that one file in every step below.')
    // Step 2 must not name a fixed path that step 1 may not have chosen.
    expect(backup).not.toContain('%APPDATA%')
    expect(backup).not.toContain('%LOCALAPPDATA%')
    expect(backup).toContain('if the file chosen in step 1 exists, copy it to that path with .avkit-backup-<UTC yyyyMMddTHHmmssZ> appended')
  })
})
