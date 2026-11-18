/* global process */
// Preloaded with -r into every E2E Electron main process (launchElectron, electron-app.ts). An
// uncaught exception is recorded instead of opening Electron's error dialog: one JSON line
// { name, message, stack } goes to the log that AVKIT_E2E_MAIN_ERROR_LOG names, and the wrapped
// close() fails the test with it. An unhandled promise rejection is recorded the same way, as
// { kind: 'rejection', name, message, stack }, and its UnhandledPromiseRejectionWarning line is
// still written to stderr, because the listener silences Electron's own. fs comes through
// getBuiltinModule because the lint refuses require in .cjs files.
const { appendFileSync, writeFileSync } = process.getBuiltinModule('node:fs')

const log = process.env.AVKIT_E2E_MAIN_ERROR_LOG
delete process.env.AVKIT_E2E_MAIN_ERROR_LOG
if (log) writeFileSync(log, '')

globalThis.__avkitE2eMainErrorWatch = true
globalThis.__avkitE2eMainErrors = []
globalThis.__avkitE2eMainRejections = []

process.on('uncaughtException', (error) => {
  globalThis.__avkitE2eMainErrors.push(error)
  const record = {
    name: error && error.name ? String(error.name) : typeof error,
    message: error && error.message !== undefined ? String(error.message) : String(error),
    stack: error && error.stack ? String(error.stack) : String(error),
  }
  if (log) appendFileSync(log, JSON.stringify(record) + '\n')
  process.stderr.write('[avkit-e2e-main-error] ' + record.stack + '\n')
})

process.on('unhandledRejection', (reason) => {
  globalThis.__avkitE2eMainRejections.push(reason)
  const record = {
    kind: 'rejection',
    name: reason && reason.name ? String(reason.name) : typeof reason,
    message: reason && reason.message !== undefined ? String(reason.message) : String(reason),
    stack: reason && reason.stack ? String(reason.stack) : String(reason),
  }
  if (log) appendFileSync(log, JSON.stringify(record) + '\n')
  process.stderr.write('[avkit-e2e-main-rejection] UnhandledPromiseRejectionWarning: ' + record.stack + '\n')
})
