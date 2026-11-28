// APP_RUNNING_CHECK (MEU-174, D-1554): the installer's running-app check stops only the
// processes that run from its own install folder. The command is taken from the macro with the
// NSIS substitutions applied and run through powershell.exe against two PING.EXE decoys named
// av-kit.exe, one in <tmp>\install\ and one in <tmp>\install-sibling\.
import { spawn, spawnSync, type ChildProcess } from 'node:child_process'
import { copyFileSync, existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { afterEach, describe, expect, it } from 'vitest'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')
const nshPath = resolve(repoRoot, 'ui/build/installer.nsh')
const SYSDIR = join(process.env.SystemRoot ?? 'C:\\Windows', 'System32')
const POWERSHELL_PREFIX =
  '"$SYSDIR\\WindowsPowerShell\\v1.0\\powershell.exe" -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command "'
const BOUNDED_DIR = "$$d = [IO.Path]::GetFullPath('$INSTDIR').TrimEnd('\\') + '\\'"
const FORBIDDEN = /taskkill|tasklist|\/IM\b|IMAGENAME|nsProcess/i
const REFUSAL = [
  'MessageBox MB_OK|MB_ICONEXCLAMATION "$(appCannotBeClosed)" /SD IDOK',
  'SetErrorLevel 2',
  'Quit',
]

function macroLines(src: string, name: string): string[] {
  const lines = src
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0 && !line.startsWith(';') && !line.startsWith('#'))
  const start = lines.indexOf(`!macro ${name}`)
  const end = lines.indexOf('!macroend', start)
  return start >= 0 && end > start ? lines.slice(start + 1, end) : []
}

function commands(body: string[]): Record<string, string> {
  const found: Record<string, string> = {}
  for (const line of body) {
    const m = line.match(/^nsExec::ExecToLog\s+`([^`]+)`$/)
    const mode = m?.[1].match(/\$\$m = '(find|stop)'/)
    if (m && mode) found[mode[1]] = m[1]
  }
  return found
}

function structureProblems(body: string[]): string[] {
  const problems: string[] = []
  const text = body.join('\n')
  if (!body.includes("System::Call 'kernel32::GetCurrentProcessId() i .r9'")) problems.push('no own pid')
  const cmds = commands(body)
  for (const mode of ['find', 'stop']) {
    const cmd = cmds[mode]
    if (!cmd) {
      problems.push(`no ${mode} command`)
      continue
    }
    if (!cmd.startsWith(POWERSHELL_PREFIX) || !cmd.endsWith('"')) problems.push(`${mode}: not the fixed path`)
    if (!cmd.includes(BOUNDED_DIR)) problems.push(`${mode}: no bounded folder`)
    if (!cmd.includes('OrdinalIgnoreCase')) problems.push(`${mode}: no ordinal match`)
    if (!cmd.includes('-ne $9')) problems.push(`${mode}: does not skip its own pid`)
    if (cmd.includes('"', POWERSHELL_PREFIX.length) && cmd.indexOf('"', POWERSHELL_PREFIX.length) !== cmd.length - 1)
      problems.push(`${mode}: a double quote inside the script`)
  }
  if (!text.includes('"$(appRunning)"') || !text.includes('MB_OKCANCEL')) problems.push('no stock question')
  // Every nsExec result is popped into $R0, and every non-zero $R0 reaches the refusal.
  const pops = body.filter((line) => line === 'Pop $R0').length
  if (pops !== 2) problems.push(`${pops} result pops, not 2`)
  const guard = body.indexOf('${if} $R0 != 0')
  if (guard < 0 || body.lastIndexOf('Pop $R0') > guard) problems.push('no refusal after the last result')
  else if (REFUSAL.some((line, k) => body[guard + 1 + k] !== line)) problems.push('the refusal is not complete')
  if (FORBIDDEN.test(text)) problems.push('a forbidden process call')
  return problems
}

function substitute(cmd: string, instdir: string, pid: number): string {
  return cmd.replace(/\$(\$|INSTDIR|SYSDIR|9)/g, (_all, name: string) =>
    name === '$' ? '$' : name === 'INSTDIR' ? instdir : name === 'SYSDIR' ? SYSDIR : String(pid),
  )
}

// nsExec runs the line with CreateProcess, so it is passed on verbatim.
function runLine(line: string): number | null {
  const m = line.match(/^"([^"]+)" (.*)$/s)
  if (!m) return null
  const run = spawnSync(m[1], [m[2]], { windowsVerbatimArguments: true, timeout: 60_000 })
  return run.status
}

const decoys: ChildProcess[] = []
let scratch: string | null = null

function startDecoy(folder: string): ChildProcess {
  mkdirSync(folder, { recursive: true })
  const exe = join(folder, 'av-kit.exe')
  copyFileSync(join(SYSDIR, 'PING.EXE'), exe)
  const child = spawn(exe, ['-t', '127.0.0.1'], { stdio: 'ignore' })
  decoys.push(child)
  return child
}

function exited(child: ChildProcess, ms: number): Promise<boolean> {
  if (child.exitCode !== null || child.signalCode !== null) return Promise.resolve(true)
  return new Promise((done) => {
    const timer = setTimeout(() => done(false), ms)
    child.once('exit', () => {
      clearTimeout(timer)
      done(true)
    })
  })
}

async function decoyPair(): Promise<{ install: string; inside: ChildProcess; sibling: ChildProcess }> {
  scratch = mkdtempSync(join(tmpdir(), 'aau-app-running-'))
  const install = join(scratch, 'install')
  const inside = startDecoy(install)
  const sibling = startDecoy(join(scratch, 'install-sibling'))
  await new Promise((r) => setTimeout(r, 500))
  return { install, inside, sibling }
}

afterEach(async () => {
  for (const child of decoys.splice(0)) {
    if (child.pid !== undefined && child.exitCode === null) {
      try {
        process.kill(child.pid)
      } catch {
        // already gone
      }
      await exited(child, 5_000)
    }
  }
  if (scratch) rmSync(scratch, { recursive: true, force: true })
  scratch = null
})

describe('MEU-174 APP_RUNNING_CHECK', () => {
  it('AC-174.21 customCheckAppRunning holds the fixed PowerShell path, both modes, the bounded match and the refusal on every non-zero exit', () => {
    const stock = [
      '!macro customCheckAppRunning',
      '  nsExec::ExecToLog `cmd /c taskkill /f /IM "av-kit.exe"`',
      '!macroend',
    ].join('\n')
    expect(structureProblems(macroLines(stock, 'customCheckAppRunning'))).not.toEqual([])

    expect(existsSync(nshPath), nshPath).toBe(true)
    const body = macroLines(readFileSync(nshPath, 'utf8'), 'customCheckAppRunning')
    expect(body.length, 'the macro customCheckAppRunning').toBeGreaterThan(0)
    expect(structureProblems(body)).toEqual([])
  })

  it('AC-174.21 the macro command stops the inside decoy and leaves the sibling running, where the stock filter selects the sibling', async () => {
    const { install, inside, sibling } = await decoyPair()
    // The oracle: the stock filter, StartsWith('$INSTDIR' with no separator, selects both decoys.
    const stock = `"${join(SYSDIR, 'WindowsPowerShell\\v1.0\\powershell.exe')}" -NoProfile -NonInteractive -Command "$p = @(Get-CimInstance -ClassName Win32_Process | ? {$_.Path -and $_.Path.StartsWith('${install}', 'CurrentCultureIgnoreCase')}); exit $p.Count"`
    expect(runLine(stock)).toBe(2)

    const cmds = commands(macroLines(readFileSync(nshPath, 'utf8'), 'customCheckAppRunning'))
    expect(Object.keys(cmds).sort()).toEqual(['find', 'stop'])
    expect(runLine(substitute(cmds.find, install, process.pid))).toBe(1)
    expect(runLine(substitute(cmds.stop, install, process.pid))).toBe(0)
    expect(await exited(inside, 10_000)).toBe(true)
    expect(await exited(sibling, 1_000)).toBe(false)
    expect(runLine(substitute(cmds.find, install, process.pid))).toBe(0)
  }, 120_000)

  it('AC-174.21 an install folder that GetFullPath refuses exits 2 in both modes', () => {
    const cmds = commands(macroLines(readFileSync(nshPath, 'utf8'), 'customCheckAppRunning'))
    expect(Object.keys(cmds).sort()).toEqual(['find', 'stop'])
    const refused = 'C:\\aau|refused<folder>'
    expect(runLine(substitute(cmds.find, refused, process.pid))).toBe(2)
    expect(runLine(substitute(cmds.stop, refused, process.pid))).toBe(2)
  }, 120_000)
})
