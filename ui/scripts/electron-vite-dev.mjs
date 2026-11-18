// `npm run dev`: starts `electron-vite dev` without ELECTRON_RUN_AS_NODE. A shell that has that
// variable set (an agent's tool shell, a VS Code terminal) makes Electron run as plain Node, so
// the window never opens and nothing says why; electron-vite passes its own environment on to
// Electron unchanged. This wrapper drops the variable, says so on stderr, and runs electron-vite.
import { spawn } from 'node:child_process'
import { constants } from 'node:os'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const ui = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const electronViteBin = resolve(ui, 'node_modules/electron-vite/bin/electron-vite.js')

/** The line written to stderr when the variable was removed. */
export const DEV_NOTICE = 'electron-vite-dev: cleared ELECTRON_RUN_AS_NODE'

/**
 * A copy of `base` without any key whose upper-cased name is ELECTRON_RUN_AS_NODE, and whether
 * one was removed. `base` is not changed.
 */
export function devEnv(base) {
  const env = {}
  let cleared = false
  for (const [key, value] of Object.entries(base)) {
    if (key.toUpperCase() === 'ELECTRON_RUN_AS_NODE') {
      cleared = true
    } else {
      env[key] = value
    }
  }
  return { env, cleared }
}

/** The arguments after the Node executable: electron-vite's own bin, `dev`, then `extra`. */
export function devArgs(extra) {
  return [electronViteBin, 'dev', ...extra]
}

/** True only when `argv1` names this module's own file (without case on win32). */
export function isEntry(argv1, moduleUrl) {
  if (argv1 === undefined) return false
  const self = fileURLToPath(moduleUrl)
  const given = resolve(argv1)
  return process.platform === 'win32' ? given.toLowerCase() === self.toLowerCase() : given === self
}

/**
 * The wrapper's exit code for the child's exit: `code` when it is a number; otherwise, off
 * win32, 128 plus the signal's number when `signal` names a known signal; otherwise 1.
 */
export function exitCodeFor(code, signal, platform = process.platform) {
  if (typeof code === 'number') return code
  if (platform !== 'win32' && typeof signal === 'string') {
    const number = constants.signals[signal]
    if (typeof number === 'number') return 128 + number
  }
  return 1
}

/**
 * Runs `electron-vite <command> ...extra` without ELECTRON_RUN_AS_NODE (writing `notice` to stderr
 * when it was removed), passes the child its own Ctrl+C and Ctrl+Break, forwards SIGTERM, and exits
 * with the child's code. `npm run dev` calls it with `dev`; `npm run preview` (Session 94,
 * D-1178) calls it with `preview` from electron-vite-preview.mjs.
 */
export function runElectronVite(command, notice, extra) {
  const { env, cleared } = devEnv(process.env)
  if (cleared) process.stderr.write(notice + '\n')
  const child = spawn(process.execPath, [electronViteBin, command, ...extra], { stdio: 'inherit', env, cwd: ui })
  // Ctrl+C and Ctrl+Break reach the whole console group, so the child gets them itself; the
  // wrapper stays until the child exits, so electron-vite and Electron are never left behind.
  const ignore = () => {}
  process.on('SIGINT', ignore)
  process.on('SIGBREAK', ignore)
  process.on('SIGTERM', () => {
    child.kill('SIGTERM')
  })
  child.on('error', (error) => {
    process.stderr.write('electron-vite-' + command + ': could not start electron-vite: ' + String(error) + '\n')
    process.exit(1)
  })
  child.on('exit', (code, signal) => {
    process.exit(exitCodeFor(code, signal))
  })
}

function main() {
  runElectronVite('dev', DEV_NOTICE, process.argv.slice(2))
}

if (isEntry(process.argv[1], import.meta.url)) main()
