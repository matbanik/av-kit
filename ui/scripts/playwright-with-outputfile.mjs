import { spawn } from 'node:child_process'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const args = process.argv.slice(2)
let outputFile

for (let i = 0; i < args.length; i += 1) {
  const arg = args[i]
  if (arg.startsWith('--outputFile=')) {
    outputFile = arg.slice('--outputFile='.length)
  } else if (arg === '--outputFile') {
    outputFile = args[i + 1]
  }
}

const stripJsonReporter = outputFile !== undefined && outputFile.length > 0
const forwarded = []
for (let i = 0; i < args.length; i += 1) {
  const arg = args[i]
  if (arg.startsWith('--outputFile=')) {
    continue
  }
  if (arg === '--outputFile') {
    i += 1
    continue
  }
  if (stripJsonReporter && arg === '--reporter=json') {
    continue
  }
  if (stripJsonReporter && arg === '--reporter' && args[i + 1] === 'json') {
    i += 1
    continue
  }
  forwarded.push(arg)
}

const env = { ...process.env }
if (stripJsonReporter) {
  env.PLAYWRIGHT_JSON_OUTPUT_NAME = outputFile
}

const cli = resolve(here, '../node_modules/@playwright/test/cli.js')
const child = spawn(process.execPath, [cli, 'test', ...forwarded], {
  cwd: resolve(here, '..'),
  env,
  stdio: 'inherit',
})
child.on('exit', (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal)
    return
  }
  process.exit(code ?? 1)
})
