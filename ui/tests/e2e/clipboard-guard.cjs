/* global process, module */
// Session 100 (D-1310, D-1320 to D-1324, D-1331): preloaded with -r into every E2E Electron main
// process that runs without AVKIT_E2E_CLIPBOARD_GATED=1 (launchElectron, electron-app.ts). The
// system clipboard is shared with the whole desktop, so a guarded launch never reaches it: each
// electron.clipboard function, the page's navigator.clipboard and execCommand('copy'|'cut'|'paste'),
// the webContents copy, cut and paste calls, the copy and paste chords and the two clipboard
// permissions are replaced or denied by recorders that never call the original. Each call is
// appended to the log that AVKIT_E2E_CLIPBOARD_GUARD_LOG names when it happens, so the wrapped
// close() and guard-logs.py both see it. A launch whose guard does not fully install exits 70
// before the app's main script runs. fs comes through getBuiltinModule and Electron through
// module.require because the lint refuses require in .cjs files.
const fs = process.getBuiltinModule('node:fs')

const MARK = '__avkitClipboardGuard'
const CONSOLE_TAG = '[avkit-e2e-clipboard-guard]'
const CALLS = '__avkitClipboardGuardCalls'

/** The twenty electron.clipboard functions the plan-time probe found on Electron 42 (D-1320). */
const NAMES = Object.freeze([
  '_writeFilesForTesting',
  'availableFormats',
  'clear',
  'has',
  'read',
  'readBookmark',
  'readBuffer',
  'readFindText',
  'readHTML',
  'readImage',
  'readRTF',
  'readText',
  'write',
  'writeBookmark',
  'writeBuffer',
  'writeFindText',
  'writeHTML',
  'writeImage',
  'writeRTF',
  'writeText',
])

const WRITE_NAME = /^_?(write|clear)/
const WC_METHODS = Object.freeze({
  copy: 'write',
  cut: 'write',
  copyImageAt: 'write',
  paste: 'read',
  pasteAndMatchStyle: 'read',
})
const PERMISSIONS = Object.freeze({ 'clipboard-read': 'read', 'clipboard-sanitized-write': 'write' })

/** Appends one call to the log and to main's in-memory list (D-1321, D-1323). */
function record(log, call, kind) {
  if (!Array.isArray(globalThis[CALLS])) globalThis[CALLS] = []
  globalThis[CALLS].push(call)
  if (log) fs.appendFileSync(log, JSON.stringify({ call, kind }) + '\n')
}

/** Defines `fn` as a tagged, non-enumerable own property `name` of `target`. */
function defineRecorder(target, name, fn) {
  Object.defineProperty(fn, MARK, { value: true })
  Object.defineProperty(target, name, { value: fn, writable: true, configurable: true, enumerable: false })
  return fn
}

/** The empty value a reader returns: nothing is read from the system clipboard. */
function emptyValue(name, nativeImage) {
  switch (name) {
    case 'availableFormats':
      return []
    case 'has':
      return false
    case 'readImage':
      return nativeImage && typeof nativeImage.createEmpty === 'function' ? nativeImage.createEmpty() : undefined
    case 'readBuffer':
      return globalThis.Buffer.alloc(0)
    case 'readBookmark':
      return { title: '', url: '' }
    default:
      return WRITE_NAME.test(name) ? undefined : ''
  }
}

/** Every function name on `obj` and its prototype chain, stopping before Object.prototype. */
function chainNames(obj) {
  const names = new Set()
  for (let o = obj; o && o !== Object.prototype; o = Object.getPrototypeOf(o)) {
    for (const name of Object.getOwnPropertyNames(o)) {
      if (name === 'constructor') continue
      const d = Object.getOwnPropertyDescriptor(o, name)
      if (d && typeof d.value === 'function') names.add(name)
    }
  }
  return names
}

function hasOnChain(obj, name) {
  for (let o = obj; o && o !== Object.prototype; o = Object.getPrototypeOf(o)) {
    if (Object.prototype.hasOwnProperty.call(o, name)) return true
  }
  return false
}

/** The chord a keyDown input forms, or null when it neither copies nor pastes. */
function chord(input) {
  if (!input || input.type !== 'keyDown') return null
  const key = String(input.key || '')
  const k = key.length === 1 ? key.toLowerCase() : key
  const ctrl = Boolean(input.control)
  const meta = Boolean(input.meta)
  const shift = Boolean(input.shift)
  const mod = ctrl ? 'Control' : meta ? 'Meta' : null
  if (mod && (k === 'c' || k === 'x')) return { name: `${mod}+${k.toUpperCase()}`, kind: 'write' }
  if (ctrl && k === 'Insert') return { name: 'Control+Insert', kind: 'write' }
  if (shift && !mod && k === 'Delete') return { name: 'Shift+Delete', kind: 'write' }
  if (mod && k === 'v') return { name: shift ? `${mod}+Shift+V` : `${mod}+V`, kind: 'read' }
  if (shift && !mod && k === 'Insert') return { name: 'Shift+Insert', kind: 'read' }
  return null
}

/**
 * The page half (D-1322, D-1331), run on every dom-ready through executeJavaScript, so it must
 * stand alone. It replaces the four Clipboard.prototype methods with tagged recorders that report
 * through console.log and resolve empty, and makes execCommand('copy'|'cut'|'paste') record and
 * return false. A second run on the same document changes nothing.
 */
function rendererGuard(g) {
  const mark = '__avkitClipboardGuard'
  const tag = '[avkit-e2e-clipboard-guard]'
  if (g[mark]) return
  const report = (name) => g.console.log(tag + JSON.stringify({ call: name }))
  const tagged = (fn) => {
    Object.defineProperty(fn, mark, { value: true })
    return fn
  }
  const proto = g.Clipboard && g.Clipboard.prototype
  if (proto) {
    const empty = { read: () => [], readText: () => '', write: () => undefined, writeText: () => undefined }
    for (const name of Object.keys(empty)) {
      const value = tagged(function () {
        report(name)
        return Promise.resolve(empty[name]())
      })
      Object.defineProperty(proto, name, { value, writable: true, configurable: true, enumerable: false })
    }
  }
  const doc = g.Document && g.Document.prototype
  if (doc && typeof doc.execCommand === 'function') {
    const original = doc.execCommand
    const value = tagged(function (command, ...rest) {
      const name = String(command).toLowerCase()
      if (name === 'copy' || name === 'cut' || name === 'paste') {
        report('execCommand ' + name)
        return false
      }
      return original.call(this, command, ...rest)
    })
    Object.defineProperty(doc, 'execCommand', { value, writable: true, configurable: true, enumerable: false })
  }
  g[mark] = true
}

/** Records a tagged renderer report from a console message, in either event form. */
function onConsole(log, args) {
  const first = args[0]
  const message = first && typeof first === 'object' && typeof first.message === 'string' ? first.message : args[2]
  if (typeof message !== 'string' || !message.startsWith(CONSOLE_TAG)) return
  let name = 'unknown'
  try {
    const parsed = JSON.parse(message.slice(CONSOLE_TAG.length))
    if (parsed && typeof parsed.call === 'string') name = parsed.call
  } catch {
    name = 'unparsed'
  }
  const kind = /^(write|execCommand (copy|cut))/.test(name) ? 'write' : 'read'
  record(log, 'renderer ' + name, kind)
}

/** The webContents hooks: page patch, console reports, native copy and paste, chords. */
function guardWebContents(log, wc, sessions) {
  const script = '(' + rendererGuard.toString() + ')(globalThis)'
  wc.on('dom-ready', () => {
    Promise.resolve(wc.executeJavaScript(script)).catch(() => undefined)
  })
  wc.on('console-message', (...args) => onConsole(log, args))
  for (const [name, kind] of Object.entries(WC_METHODS)) {
    defineRecorder(wc, name, function () {
      record(log, 'webContents ' + name, kind)
    })
  }
  wc.on('before-input-event', (event, input) => {
    const hit = chord(input)
    if (!hit) return
    record(log, 'input ' + hit.name, hit.kind)
    event.preventDefault()
  })
  const ses = wc.session
  if (ses && !sessions.has(ses)) {
    sessions.add(ses)
    ses.setPermissionRequestHandler((_wc, permission, callback) => {
      if (Object.prototype.hasOwnProperty.call(PERMISSIONS, permission)) {
        record(log, 'permission ' + permission, PERMISSIONS[permission])
        callback(false)
        return
      }
      callback(true)
    })
    ses.setPermissionCheckHandler((_wc, permission) => {
      if (Object.prototype.hasOwnProperty.call(PERMISSIONS, permission)) {
        record(log, 'permission ' + permission, PERMISSIONS[permission])
        return false
      }
      return true
    })
  }
}

/**
 * Replaces every clipboard function and registers the hooks (D-1320). Returns { ok, failed }.
 * Only when all of NAMES are replaced and checked is the `installed` line written and the marker
 * set; otherwise a `failed` line names each missing or unreplaced name.
 */
function install(electron, log) {
  const clipboard = electron && electron.clipboard
  const failed = []
  if (!clipboard || typeof clipboard !== 'object') {
    failed.push('missing clipboard')
  } else {
    const names = new Set(NAMES)
    for (const name of NAMES) {
      if (!hasOnChain(clipboard, name)) failed.push('missing ' + name)
    }
    for (const name of chainNames(clipboard)) names.add(name)
    for (const name of [...names].sort()) {
      if (!hasOnChain(clipboard, name)) continue
      const kind = WRITE_NAME.test(name) ? 'write' : 'read'
      const recorder = function () {
        record(log, 'main ' + name, kind)
        return emptyValue(name, electron.nativeImage)
      }
      try {
        defineRecorder(clipboard, name, recorder)
      } catch {
        // checked below
      }
      if (!(clipboard[name] === recorder && recorder[MARK] === true)) failed.push('unreplaced ' + name)
    }
  }
  if (failed.length > 0) {
    if (log) fs.appendFileSync(log, JSON.stringify({ failed: failed.join(', ') }) + '\n')
    return { ok: false, failed }
  }
  if (log) fs.appendFileSync(log, JSON.stringify({ installed: true, names: [...NAMES] }) + '\n')
  globalThis[MARK] = true
  if (!Array.isArray(globalThis[CALLS])) globalThis[CALLS] = []
  const sessions = new Set()
  electron.app.on('web-contents-created', (_event, wc) => guardWebContents(log, wc, sessions))
  return { ok: true, failed }
}

module.exports = { install, rendererGuard, NAMES, MARK, CONSOLE_TAG }

if (process.versions.electron && process.type === 'browser') {
  const log = process.env.AVKIT_E2E_CLIPBOARD_GUARD_LOG
  delete process.env.AVKIT_E2E_CLIPBOARD_GUARD_LOG
  let result
  try {
    result = install(module.require('electron'), log)
  } catch (error) {
    result = { ok: false, failed: ['threw ' + String(error && error.message)] }
    if (log) fs.appendFileSync(log, JSON.stringify({ failed: result.failed.join(', ') }) + '\n')
  }
  if (!result.ok) {
    process.stderr.write('CLIPBOARD_GUARD: install failed: ' + result.failed.join(', ') + '\n')
    process.exit(70)
  }
}
