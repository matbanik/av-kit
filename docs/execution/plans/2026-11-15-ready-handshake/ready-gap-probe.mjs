// Ready-gap probe (Session 82, MEU-153 measurement row).
// Spawns the backend, sends a request the moment AVKIT_READY appears on stdout, and records
// whether it was refused and how long the port took to accept. Writes only under --root.
//
// node ready-gap-probe.mjs --root <dir> --runs <n> --mode fetch|cim --out <file.jsonl> -- <backend argv...>
// The backend argv gets `--token T --mcp-token M --port 0 --app-data <run dir>` appended.
import { spawn, execFileSync } from 'node:child_process'
import { mkdirSync, rmSync, appendFileSync, writeFileSync } from 'node:fs'
import net from 'node:net'
import path from 'node:path'

const READY = /AVKIT_READY port=(\d+) instance=(\S+)/

function parse(argv) {
  const sep = argv.indexOf('--')
  const own = argv.slice(0, sep)
  const backend = argv.slice(sep + 1)
  const opt = {}
  for (let i = 0; i < own.length; i += 2) opt[own[i].replace(/^--/, '')] = own[i + 1]
  if (!opt.root || !opt.out || backend.length === 0) throw new Error('usage: --root --out [--runs] [--mode] -- argv')
  return { root: opt.root, out: opt.out, runs: Number(opt.runs ?? '5'), mode: opt.mode ?? 'fetch', backend }
}

function accepts(port) {
  return new Promise((resolve) => {
    const s = net.connect(port, '127.0.0.1')
    s.once('connect', () => { s.destroy(); resolve(true) })
    s.once('error', () => { s.destroy(); resolve(false) })
  })
}

function cimQuery(pid) {
  const script = `$p = Get-CimInstance Win32_Process -Filter "ProcessId=${Math.trunc(pid)}"; if ($null -eq $p) { exit 1 }; Write-Output $p.ExecutablePath`
  try {
    execFileSync('powershell.exe', ['-NoProfile', '-Command', script], { encoding: 'utf8', timeout: 8000, windowsHide: true })
    return true
  } catch {
    return false
  }
}

function killTree(pid) {
  // By pid tree, never by image name.
  try { execFileSync('taskkill.exe', ['/PID', String(pid), '/T', '/F'], { stdio: 'ignore', windowsHide: true }) } catch { /* gone */ }
}

async function once(cfg, i) {
  const runDir = path.join(cfg.root, `run-${cfg.mode}-${i}`)
  rmSync(runDir, { recursive: true, force: true })
  const home = path.join(runDir, 'home')
  const appData = path.join(runDir, 'app-data')
  mkdirSync(home, { recursive: true })
  mkdirSync(appData, { recursive: true })
  const env = { ...process.env, HOME: home, USERPROFILE: home, NO_PROXY: '127.0.0.1,localhost' }
  const [cmd, ...rest] = cfg.backend
  const argv = [...rest, '--token', 'probe-gui-token', '--mcp-token', 'probe-mcp-token', '--port', '0', '--app-data', appData]
  const t0 = performance.now()
  const child = spawn(cmd, argv, { cwd: runDir, env, stdio: ['ignore', 'pipe', 'pipe'], windowsHide: true })
  const record = { mode: cfg.mode, run: i }
  try {
    const port = await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('no READY in 60 s')), 60000)
      let seen = ''
      child.stdout.on('data', (chunk) => {
        seen += chunk.toString('utf8')
        const m = READY.exec(seen)
        if (m) { clearTimeout(timer); resolve(Number(m[1])) }
      })
      child.once('exit', (code) => { clearTimeout(timer); reject(new Error(`exited ${code} before READY`)) })
    })
    const tReady = performance.now()
    record.ready_ms = Math.round(tReady - t0)
    if (cfg.mode === 'cim') {
      record.cim_ok = cimQuery(child.pid)
      record.cim_ms = Math.round(performance.now() - tReady)
    }
    const tReq = performance.now()
    try {
      const res = await fetch(`http://127.0.0.1:${port}/api/v1/health`)
      record.first = `http ${res.status}`
    } catch (err) {
      record.first = String(err?.cause?.code ?? err?.code ?? err?.message ?? err)
    }
    record.first_ms = Math.round(performance.now() - tReq)
    let accepted = await accepts(port)
    while (!accepted && performance.now() - tReady < 30000) {
      await new Promise((r) => setTimeout(r, 5))
      accepted = await accepts(port)
    }
    record.accept_after_ready_ms = Math.round(performance.now() - tReady)
  } catch (err) {
    record.error = String(err?.message ?? err)
  } finally {
    if (child.pid !== undefined) killTree(child.pid)
    await new Promise((r) => setTimeout(r, 300))
    rmSync(runDir, { recursive: true, force: true })
  }
  return record
}

const cfg = parse(process.argv.slice(2))
mkdirSync(cfg.root, { recursive: true })
writeFileSync(cfg.out, '')
const tally = {}
for (let i = 1; i <= cfg.runs; i++) {
  const r = await once(cfg, i)
  appendFileSync(cfg.out, JSON.stringify(r) + '\n')
  const key = r.error ? `error` : r.first
  tally[key] = (tally[key] ?? 0) + 1
  console.log(JSON.stringify(r))
}
console.log('ready-gap-probe tally ' + JSON.stringify({ mode: cfg.mode, runs: cfg.runs, ...tally }))
