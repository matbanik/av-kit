import { join, resolve } from 'node:path'

// CLIENT_SET: the clients the Settings MCP card offers, in display order.
export const MCP_CLIENTS = ['claude-code', 'codex', 'cursor', 'vscode', 'claude-desktop', 'windsurf', 'generic'] as const

export type McpClient = (typeof MCP_CLIENTS)[number]
export type McpScope = 'user' | 'project'

export const MCP_CLIENT_LABELS: Record<McpClient, string> = {
  'claude-code': 'Claude Code',
  codex: 'Codex',
  cursor: 'Cursor',
  vscode: 'VS Code',
  'claude-desktop': 'Claude Desktop',
  windsurf: 'Windsurf (community)',
  generic: 'Other MCP client',
}

// SCOPE_RULE: only these clients read a project-level config file.
export const PROJECT_SCOPE_CLIENTS: readonly McpClient[] = ['claude-code', 'codex', 'cursor', 'vscode']

export const PATH_QUOTE_ERROR = 'a path contains a quote, $ or backtick; use the Other MCP client block'

export type SetupPromptInput = {
  client: McpClient
  scope: McpScope
  command: string
  serverPath: string
  appData: string
}

/** SERVER_ENTRY: the bundled server in a packaged app, the built dev server otherwise. No file I/O. */
export function mcpServerEntry(opts: { packaged: boolean; resourcesPath: string; dirname: string }): string {
  if (opts.packaged) {
    return join(opts.resourcesPath, 'mcp-server', 'index.mjs')
  }
  return resolve(opts.dirname, '../../../mcp-server/dist/index.js')
}

type Block = {
  /** The text after "1. Find: ". */
  find: string
  /** The file named in the backup step. */
  backupFile: string
  /** The whole backup step text, when step 1 chooses between files (so step 2 names no fixed path). */
  backup?: string
  /** The text after "3. Merge: change only the avkit entry and keep every other entry. ". */
  merge: string
  /** The fence language ('' for a plain fence). */
  lang: string
  body: string
}

/** MCP_LAUNCH as JSON: command, then one absolute server path, then the two env keys in order. */
function launchEntry(input: SetupPromptInput): { command: string; args: string[]; env: Record<string, string> } {
  return {
    command: input.command,
    args: [input.serverPath],
    env: { ELECTRON_RUN_AS_NODE: '1', AVKIT_APP_DATA: input.appData },
  }
}

function claudeCodeBlock(input: SetupPromptInput): Block {
  for (const value of [input.command, input.serverPath, input.appData]) {
    if (/["$`]/.test(value)) {
      throw new Error(PATH_QUOTE_ERROR)
    }
  }
  const file = input.scope === 'user' ? '~/.claude.json' : '.mcp.json'
  const where = input.scope === 'user' ? file : `${file} in the repository root`
  return {
    find: `Claude Code keeps this server in ${where}. Do not edit that file by hand; the commands in step 3 change it.`,
    backupFile: file,
    merge: 'Run these two commands in a terminal, in order. The first may say avkit was not found; that is fine.',
    lang: '',
    body: [
      `claude mcp remove avkit --scope ${input.scope}`,
      `claude mcp add avkit --scope ${input.scope} -e ELECTRON_RUN_AS_NODE=1 -e "AVKIT_APP_DATA=${input.appData}" -- "${input.command}" "${input.serverPath}"`,
    ].join('\n'),
  }
}

function codexBlock(input: SetupPromptInput): Block {
  const file = input.scope === 'user' ? '~/.codex/config.toml' : '.codex/config.toml'
  const where = input.scope === 'user' ? file : `${file} in the repository root`
  // JSON.stringify gives a valid TOML basic string (\\, \" and \uXXXX escapes).
  const q = (value: string) => JSON.stringify(value)
  return {
    find: `the config file is ${where}.`,
    backupFile: file,
    merge:
      'Replace the [mcp_servers.avkit] and [mcp_servers.avkit.env] tables with the block below (add them if they are missing) and keep every other table.',
    lang: 'toml',
    body: [
      '[mcp_servers.avkit]',
      `command = ${q(input.command)}`,
      `args = [${q(input.serverPath)}]`,
      '',
      '[mcp_servers.avkit.env]',
      'ELECTRON_RUN_AS_NODE = "1"',
      `AVKIT_APP_DATA = ${q(input.appData)}`,
    ].join('\n'),
  }
}

function jsonBlock(input: SetupPromptInput, find: string, backupFile: string): Block {
  const container = input.client === 'vscode' ? 'servers' : 'mcpServers'
  const entry = input.client === 'vscode' ? { type: 'stdio', ...launchEntry(input) } : launchEntry(input)
  return {
    find,
    backupFile,
    merge: `Add or replace the "avkit" key inside "${container}" with the one below and keep every other key. If the file does not exist, create it with exactly this content.`,
    lang: 'json',
    body: JSON.stringify({ [container]: { avkit: entry } }, null, 2),
  }
}

function clientBlock(input: SetupPromptInput): Block {
  const project = input.scope === 'project'
  switch (input.client) {
    case 'claude-code':
      return claudeCodeBlock(input)
    case 'codex':
      return codexBlock(input)
    case 'cursor': {
      const file = project ? '.cursor/mcp.json' : '~/.cursor/mcp.json'
      return jsonBlock(input, `the config file is ${project ? `${file} in the repository root` : file}.`, file)
    }
    case 'vscode': {
      if (project) {
        return jsonBlock(input, 'the config file is .vscode/mcp.json in the repository root.', '.vscode/mcp.json')
      }
      const file = '%APPDATA%\\Code\\User\\mcp.json'
      return jsonBlock(input, `the config file is ${file} (the "MCP: Open User Configuration" command opens it).`, file)
    }
    case 'claude-desktop': {
      const file = '%APPDATA%\\Claude\\claude_desktop_config.json'
      const msix = '%LOCALAPPDATA%\\Packages\\Claude_*\\LocalCache\\Roaming\\Claude\\claude_desktop_config.json'
      // Step 1 settles on one file, so step 2 backs up that file and not a fixed path (review F1).
      return {
        ...jsonBlock(
          input,
          `the config file is ${msix} if a %LOCALAPPDATA%\\Packages\\Claude_* folder exists (Claude Desktop installed from the Microsoft Store, MSIX); otherwise it is ${file}. Use that one file in every step below.`,
          file,
        ),
        backup:
          'if the file chosen in step 1 exists, copy it to that path with .avkit-backup-<UTC yyyyMMddTHHmmssZ> appended, before changing it, with the current UTC time in that name. If it does not exist yet, skip the backup.',
      }
    }
    case 'windsurf': {
      const file = '~/.codeium/windsurf/mcp_config.json'
      return jsonBlock(input, `the config file is ${file}.`, file)
    }
    case 'generic':
      return jsonBlock(
        input,
        `your MCP client's config file. Most clients use an "mcpServers" object as below; if yours uses another shape, give it the same three fields: command, args and env.`,
        '<config file>',
      )
  }
}

/** PROMPT_BUILDER: the setup prompt for one client and scope. Pure: no I/O, no clock, no token. */
export function buildSetupPrompt(input: SetupPromptInput): string {
  const label = MCP_CLIENT_LABELS[input.client]
  if (input.scope === 'project' && !PROJECT_SCOPE_CLIENTS.includes(input.client)) {
    throw new Error(`${label} has no project-scope config; use user scope`)
  }
  const block = clientBlock(input)
  const scopeText = input.scope === 'user' ? 'user scope: all projects' : 'project scope: this project only'
  return [
    `Set up the av-kit MCP server for ${label} (${scopeText}).`,
    '',
    'Follow the steps in order. The server reads its own token from the app data folder, so no token goes in any config.',
    '',
    `1. Find: ${block.find}`,
    `2. Back up: ${block.backup ?? `if ${block.backupFile} exists, copy it to ${block.backupFile}.avkit-backup-<UTC yyyyMMddTHHmmssZ> before changing it, with the current UTC time in that name. If it does not exist yet, skip the backup.`}`,
    `3. Merge: change only the avkit entry and keep every other entry. ${block.merge}`,
    '',
    '```' + block.lang,
    block.body,
    '```',
    '',
    `4. Restart: If the tools do not appear, quit and reopen ${label}, then reply Ready.`,
    '5. Verify: call the avkit_health tool with action: "dependencies". It must return successfully. A "liveness" result never counts as verified.',
    '6. Result: end your reply with exactly one line, either RESULT: connected or RESULT: failed (<step>, <error>), where <step> is backup, merge, restart or verify. When the verify call returns an error whose text starts with "<code>:", <error> is that code: an error starting "token_missing:" gives RESULT: failed (verify, token_missing).',
  ].join('\n')
}
