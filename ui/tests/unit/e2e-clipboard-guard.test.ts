// @vitest-environment node
// Session 100 (docs/execution/plans/2026-11-20-e2e-devpc-clipboard): the dev-PC clipboard guard.
// S100 AC-5 is the static scan, the twin of the plan's writer-scan.py (D-1312, D-1326, D-1331);
// S100 AC-6 and AC-7 check the launch helpers of electron-env.ts (D-1310, D-1321); S100 AC-8
// runs the preload clipboard-guard.cjs on fakes whose originals throw if called, so no test here
// reaches the system clipboard (D-1320, D-1322, D-1324, D-1331); S100 AC-9 reads electron-app.ts.
// Each test asserts its target's type or existence first, so before the guard exists it fails by
// assertion.
import { existsSync, mkdtempSync, readdirSync, readFileSync, rmSync, statSync } from 'node:fs'
import { createRequire } from 'node:module'
import { tmpdir } from 'node:os'
import { dirname, join, relative, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

import * as env from '../e2e/electron-env'

const here = dirname(fileURLToPath(import.meta.url))
const E2E_DIR = resolve(here, '../e2e')
const KNOWN_FILE = resolve(here, '../../../tools/e2e_host/known-failures.json')
const GUARD_PATH = resolve(E2E_DIR, 'clipboard-guard.cjs')
const APP_PATH = resolve(E2E_DIR, 'electron-app.ts')
// Built from parts, so this file never holds the guard's message prefix or the launch call itself.
const PREFIX = ['CLIPBOARD', 'GUARD:'].join('_')
const LAUNCH = ['_electron', 'launch'].join('.')

type Env = Record<string, string | undefined>
type Fn = (...args: unknown[]) => unknown

interface GuardEnv {
  CLIPBOARD_GUARD_WATCH: string
  CLIPBOARD_GUARD_LOG_ENV: string
  clipboardGuardArgs: (env: Env) => string[]
  clipboardGuardLogPath: (scratch: string, diag: string | null, launch: number) => string
  clipboardGuardVerdict: (text: string | null) => { ok: boolean; message: string }
}

interface GuardModule {
  install: (electron: unknown, log: string | undefined) => { ok: boolean; failed: string[] }
  rendererGuard: (g: unknown) => void
  NAMES: readonly string[]
  MARK: string
  CONSOLE_TAG: string
}

const guardEnv = env as unknown as Partial<GuardEnv>

// ---------------------------------------------------------------------------------------------
// S100 AC-5: the scan. The same patterns, kinds and exemptions as writer-scan.py.
// ---------------------------------------------------------------------------------------------

const ALLOWED_FILES = ['clipboard-guard.cjs', 'clipboard-guard.test.ts']
const LAUNCH_FILES = ['electron-app.ts', 'electron-env.ts']
const ALLOWED_IDS = ['settings-leaf-copy_to_clipboard', 'convert-copy-fast', 'convert-copy-reencode']
const WRITER_IDS = ['pin-mcp-btn']
const Q = '[\'"`]'
const NQ = '[^\'"`]'
const PICK = String.raw`(?:\s*\.\s*(?:first|last)\(\s*\)|\s*\.\s*nth\(\s*\d+\s*\))*`
const ACT = PICK + String.raw`\s*\.\s*(?:click|dblclick|press|tap)\(`
const escapeRe = (s: string): string => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
const LOC_ID = new RegExp(String.raw`getByTestId\(\s*` + Q + '(' + NQ + '*copy' + NQ + '*)' + Q + String.raw`\s*\)`, 'gi')
const LOC_CONST = /getByTestId\(\s*([A-Za-z_$][\w$.]*)\s*\)/g
const LOC_WRITER = new RegExp(
  String.raw`getByTestId\(\s*` + Q + '(' + WRITER_IDS.map(escapeRe).join('|') + ')' + Q + String.raw`\s*\)`,
  'g',
)
const LOC_TEXT = /getBy(?:Role|Text|Label|Title)\(([^)]*)\)/g
const LOC_CSS = new RegExp(String.raw`\.locator\(\s*` + Q + '(' + NQ + '*copy' + NQ + '*)' + Q + String.raw`\s*\)`, 'gi')
const COPY_WORD = /\bcopy/i
const SIMPLE: ReadonlyArray<readonly [string, RegExp]> = [
  ['clipboard-call', /(?<!navigator\.)\bclipboard\s*\.\s*(?:read|write|clear|has|available)\w*\s*\(/g],
  ['navigator-clipboard', /\bnavigator\s*\.\s*clipboard\b/g],
  ['exec-copy', new RegExp(String.raw`execCommand\(\s*` + Q + '(?:copy|cut)' + Q, 'gi')],
  ['exec-paste', new RegExp(String.raw`execCommand\(\s*` + Q + 'paste' + Q, 'gi')],
  ['native-copy', /\b(?:webContents|wc|contents)\s*\??\s*\.\s*(?:copy|cut)\s*\(/gi],
  ['native-copy', /\.\s*copyImageAt\s*\(/g],
  ['native-paste', /\.\s*paste\s*\(/g],
  ['native-paste', /\bpasteAndMatchStyle\b/g],
  [
    'paste-chord',
    new RegExp(
      String.raw`\.press\(\s*` +
        Q +
        NQ +
        String.raw`*(?:\b(?:Shift\+)?(?:Control|Meta|ControlOrMeta)\+(?:Shift\+)?(?:v|KeyV)|\bShift\+Insert)` +
        Q,
      'gi',
    ),
  ],
  [
    'copy-chord',
    new RegExp(
      String.raw`\.press\(\s*` + Q + NQ + String.raw`*(?:\b(?:Control|Meta|ControlOrMeta)\+(?:[cx]|Key[cx]|Insert)|\bShift\+Delete)` + Q,
      'gi',
    ),
  ],
  ['electron-launch', new RegExp(escapeRe(LAUNCH).replace('\\.', String.raw`\s*\.\s*`) + String.raw`\(`, 'g')],
]
const BINDING = /\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*/g

function copyLocators(text: string): Array<[number, number, string]> {
  const out: Array<[number, number, string]> = []
  for (const m of text.matchAll(LOC_ID)) {
    if (!ALLOWED_IDS.includes(m[1])) out.push([m.index, m.index + m[0].length, 'copy-id-click'])
  }
  for (const m of text.matchAll(LOC_CONST)) {
    if (m[1].toLowerCase().includes('copy')) out.push([m.index, m.index + m[0].length, 'copy-const-click'])
  }
  for (const m of text.matchAll(LOC_WRITER)) out.push([m.index, m.index + m[0].length, 'writer-id-click'])
  for (const m of text.matchAll(LOC_TEXT)) {
    if (COPY_WORD.test(m[1])) out.push([m.index, m.index + m[0].length, 'copy-locator-click'])
  }
  for (const m of text.matchAll(LOC_CSS)) {
    if (!ALLOWED_IDS.some((id) => m[1].includes(id))) out.push([m.index, m.index + m[0].length, 'copy-css-click'])
  }
  return out
}

/** The bound expression: the rest of the line plus each following line that starts with `.`. */
function bindingText(text: string, start: number): string {
  let end = text.indexOf('\n', start)
  end = end < 0 ? text.length : end
  while (end < text.length) {
    let next = text.indexOf('\n', end + 1)
    next = next < 0 ? text.length : next
    if (!text.slice(end + 1, next).trimStart().startsWith('.')) break
    end = next
  }
  return text.slice(start, end)
}

/** Every hit in one file's text as `<line>: <kind>`, in source order. */
function hitsIn(name: string, text: string): string[] {
  const found: Array<[number, string]> = []
  for (const [kind, pattern] of SIMPLE) {
    if (kind === 'electron-launch' && LAUNCH_FILES.includes(name)) continue
    for (const m of text.matchAll(pattern)) found.push([m.index, kind])
  }
  const act = new RegExp(ACT, 'y')
  for (const [start, end, kind] of copyLocators(text)) {
    act.lastIndex = end
    if (act.test(text)) found.push([start, kind])
  }
  for (const m of text.matchAll(BINDING)) {
    const at = m.index + m[0].length
    const expr = bindingText(text, at)
    if (copyLocators(expr).length === 0 || new RegExp(ACT, 's').test(expr)) continue
    const use = new RegExp(String.raw`(?<![\w$.])` + escapeRe(m[1]) + ACT, 'g')
    use.lastIndex = at
    for (let call = use.exec(text); call !== null; call = use.exec(text)) found.push([call.index, 'copy-var-click'])
  }
  found.sort((a, b) => a[0] - b[0] || (a[1] < b[1] ? -1 : a[1] > b[1] ? 1 : 0))
  return found.map(([start, kind]) => `${text.slice(0, start).split('\n').length}: ${kind}`)
}

function gatedFiles(): string[] {
  const known = JSON.parse(readFileSync(KNOWN_FILE, 'utf8')) as { gated?: Array<{ file: string }> }
  return [...new Set((known.gated ?? []).map((row) => String(row.file)))].sort()
}

function e2eFiles(dir: string): string[] {
  const out: string[] = []
  for (const entry of readdirSync(dir).sort()) {
    const path = join(dir, entry)
    if (statSync(path).isDirectory()) out.push(...e2eFiles(path))
    else if (/\.(ts|cjs|mjs)$/.test(entry)) out.push(path)
  }
  return out
}

const kinds = (name: string, text: string): string[] => hitsIn(name, text).map((hit) => hit.replace(/^\d+: /, ''))

describe('Session 100 dev-PC clipboard guard', () => {
  it('S100 AC-5 no clipboard call, native copy or paste, copy or paste chord or copy click in ui/tests/e2e outside the gated and guard files', () => {
    expect(existsSync(E2E_DIR), 'ui/tests/e2e exists').toBe(true)
    expect(existsSync(KNOWN_FILE), 'tools/e2e_host/known-failures.json exists').toBe(true)
    // The paste kinds of D-1331, one source line each, every one a hit.
    const hits: Array<[string, string]> = [
      ["await app.evaluate(({ clipboard }) => clipboard.writeText('s'))", 'clipboard-call'],
      ["await page.evaluate(() => navigator.clipboard.readText())", 'navigator-clipboard'],
      ["document.execCommand('copy')", 'exec-copy'],
      ["document.execCommand('paste')", 'exec-paste'],
      ['await app.evaluate(() => wc.paste())', 'native-paste'],
      ['BrowserWindow.getAllWindows()[0]\n  .webContents\n  .paste()', 'native-paste'],
      ['contents.pasteAndMatchStyle()', 'native-paste'],
      ['wc.copyImageAt(10, 20)', 'native-copy'],
      ['BrowserWindow.getAllWindows()[0].webContents.cut()', 'native-copy'],
      ["await page.keyboard.press('Control+V')", 'paste-chord'],
      ["await page.keyboard.press('Control+Shift+V')", 'paste-chord'],
      ["await page.keyboard.press('Shift+Control+v')", 'paste-chord'],
      ["await field.press('ControlOrMeta+KeyV')", 'paste-chord'],
      ["await page.keyboard.press('Shift+Insert')", 'paste-chord'],
      ["await page.keyboard.press('Control+C')", 'copy-chord'],
      ["await field.press('Shift+Delete')", 'copy-chord'],
      ["await page.getByTestId('console-copy').click()", 'copy-id-click'],
      ['await page.getByTestId(MCP_COPY_PROMPT_BTN).click()', 'copy-const-click'],
      ["await page.getByTestId('pin-mcp-btn').click()", 'writer-id-click'],
      ["await page.getByRole('button', { name: /copy/i }).first().click()", 'copy-locator-click'],
      ["await page.locator('[data-testid=console-copy]').click()", 'copy-css-click'],
      ["const btn = page.getByTestId('console-copy')\nawait btn.click()", 'copy-var-click'],
      [`const app = await ${LAUNCH}({ args })`, 'electron-launch'],
    ]
    for (const [source, kind] of hits) expect(kinds('a.test.ts', source), source).toEqual([kind])
    // The negatives: none is a hit.
    const misses = [
      "await page.keyboard.press('v')",
      "await page.keyboard.press('Shift+V')",
      "await page.keyboard.press('Insert')",
      "await page.keyboard.press('Control+Verbose')",
      "await page.getByTestId('paste-btn').click()",
      "wc.replace('x')",
      "wc.replaceMisspelling('y')",
      "await page.getByTestId('settings-leaf-copy_to_clipboard').click()",
      "await expect(page.getByTestId('copy-mcp-btn')).toBeVisible()",
      "await page.getByRole('button', { name: 'Photocopy' }).click()",
    ]
    for (const source of misses) expect(kinds('a.test.ts', source), source).toEqual([])
    expect(kinds('electron-app.ts', `app = await ${LAUNCH}({`), 'the launch helper').toEqual([])
    expect(hitsIn('a.test.ts', "x\ny\nawait page\n  .getByTestId('console-copy')\n  .click()"), 'line of a split chain').toEqual([
      '4: copy-id-click',
    ])

    const gated = gatedFiles()
    const found: string[] = []
    for (const path of e2eFiles(E2E_DIR)) {
      const name = path.split(/[\\/]/).pop() ?? ''
      if (gated.includes(name) || ALLOWED_FILES.includes(name)) continue
      const rel = relative(E2E_DIR, path).split('\\').join('/')
      for (const hit of hitsIn(name, readFileSync(path, 'utf8'))) found.push(`${rel}:${hit}`)
    }
    expect(found, `clipboard hits outside the gated files ${JSON.stringify(gated)}`).toEqual([])
  })

  it('S100 AC-6 clipboardGuardArgs preloads the guard unless AVKIT_E2E_CLIPBOARD_GATED is 1, and clipboardGuardLogPath names the log', () => {
    expect(typeof guardEnv.clipboardGuardArgs, 'electron-env.ts exports clipboardGuardArgs').toBe('function')
    expect(typeof guardEnv.clipboardGuardLogPath, 'electron-env.ts exports clipboardGuardLogPath').toBe('function')
    expect(typeof guardEnv.CLIPBOARD_GUARD_WATCH, 'electron-env.ts exports CLIPBOARD_GUARD_WATCH').toBe('string')
    const { clipboardGuardArgs, clipboardGuardLogPath, CLIPBOARD_GUARD_WATCH, CLIPBOARD_GUARD_LOG_ENV } = guardEnv as GuardEnv
    expect(CLIPBOARD_GUARD_WATCH).toBe(GUARD_PATH)
    expect(existsSync(CLIPBOARD_GUARD_WATCH), 'the preload exists').toBe(true)
    expect(CLIPBOARD_GUARD_LOG_ENV).toBe('AVKIT_E2E_CLIPBOARD_GUARD_LOG')
    for (const value of [undefined, '', '0', 'true', ' 1']) {
      expect(clipboardGuardArgs({ AVKIT_E2E_CLIPBOARD_GATED: value }), String(value)).toEqual(['-r', GUARD_PATH])
    }
    expect(clipboardGuardArgs({})).toEqual(['-r', GUARD_PATH])
    expect(clipboardGuardArgs({ AVKIT_E2E_CLIPBOARD_GATED: '1' })).toEqual([])
    const scratch = join(tmpdir(), 'avkit-s100-scratch')
    const diag = join(tmpdir(), 'avkit-s100-diag')
    expect(clipboardGuardLogPath(scratch, diag, 12345001)).toBe(join(diag, 'clipboard-12345001.jsonl'))
    expect(clipboardGuardLogPath(scratch, null, 12345001)).toBe(join(scratch, 'clipboard.jsonl'))
  })

  it('S100 AC-7 clipboardGuardVerdict passes only an installed guard with no call and names every other case', () => {
    expect(typeof guardEnv.clipboardGuardVerdict, 'electron-env.ts exports clipboardGuardVerdict').toBe('function')
    const { clipboardGuardVerdict } = guardEnv as GuardEnv
    const installed = JSON.stringify({ installed: true, names: ['writeText'] })
    const call = (name: string, kind: string): string => JSON.stringify({ call: name, kind })
    expect(clipboardGuardVerdict(null)).toEqual({ ok: false, message: `${PREFIX} the guard log is missing` })
    expect(clipboardGuardVerdict(JSON.stringify({ failed: 'missing has, unreplaced readText' }) + '\n')).toEqual({
      ok: false,
      message: `${PREFIX} the guard failed to install: missing has, unreplaced readText`,
    })
    expect(clipboardGuardVerdict('')).toEqual({ ok: false, message: `${PREFIX} the guard was never installed` })
    expect(clipboardGuardVerdict(call('main writeText', 'write') + '\n')).toEqual({
      ok: false,
      message: `${PREFIX} the guard was never installed`,
    })
    expect(clipboardGuardVerdict(installed + '\nnot json\n')).toEqual({ ok: false, message: `${PREFIX} invalid guard log line 2` })
    expect(clipboardGuardVerdict(installed + '\n[1]\n')).toEqual({ ok: false, message: `${PREFIX} invalid guard log line 2` })
    const calls = [call('main writeText', 'write'), call('renderer writeText', 'write'), call('webContents copy', 'write')]
    expect(clipboardGuardVerdict([installed, ...calls].join('\n') + '\n')).toEqual({
      ok: false,
      message: `${PREFIX} clipboard call(s) in a launch without AVKIT_E2E_CLIPBOARD_GATED=1: main writeText, renderer writeText, webContents copy`,
    })
    expect(clipboardGuardVerdict([installed, call('webContents paste', 'read')].join('\n') + '\n')).toEqual({
      ok: false,
      message: `${PREFIX} clipboard call(s) in a launch without AVKIT_E2E_CLIPBOARD_GATED=1: webContents paste`,
    })
    expect(clipboardGuardVerdict(installed + '\n')).toEqual({ ok: true, message: '' })
  })

  it('S100 AC-8 the preload replaces every clipboard function, the native copies and pastes, the chords and permissions, and the page calls, never reaching an original', async () => {
    expect(existsSync(GUARD_PATH), 'ui/tests/e2e/clipboard-guard.cjs exists').toBe(true)
    const guard = createRequire(import.meta.url)(GUARD_PATH) as GuardModule
    expect(typeof guard.install, 'the preload exports install').toBe('function')
    const { install, rendererGuard, NAMES, MARK, CONSOLE_TAG } = guard
    expect(MARK).toBe('__avkitClipboardGuard')
    expect(CONSOLE_TAG).toBe('[avkit-e2e-clipboard-guard]')
    expect([...NAMES]).toEqual([
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
    const g = globalThis as Record<string, unknown>
    const scratch = mkdtempSync(join(tmpdir(), 'avkit-s100-guard-'))
    const original = (name: string): Fn => () => {
      throw new Error(`the original ${name} was called`)
    }
    const lines = (log: string): Array<Record<string, unknown>> =>
      existsSync(log)
        ? readFileSync(log, 'utf8')
            .split('\n')
            .filter((line) => line !== '')
            .map((line) => JSON.parse(line) as Record<string, unknown>)
        : []
    const reset = (): void => {
      delete g[MARK]
      delete g.__avkitClipboardGuardCalls
    }
    const EMPTY_IMAGE = { empty: true }
    interface FakeApp {
      handlers: Map<string, Fn[]>
      on: (event: string, fn: Fn) => FakeApp
    }
    const fakeApp = (): FakeApp => {
      const app: FakeApp = {
        handlers: new Map(),
        on(event, fn) {
          app.handlers.set(event, [...(app.handlers.get(event) ?? []), fn])
          return app
        },
      }
      return app
    }
    const electron = (clipboard: object, app: FakeApp): object => ({
      clipboard,
      app,
      nativeImage: { createEmpty: () => EMPTY_IMAGE },
    })
    const ownClipboard = (names: readonly string[]): Record<string, unknown> =>
      Object.fromEntries(names.map((name) => [name, original(`clipboard.${name}`)]))

    try {
      // Every name an own property: all replaced and tagged, the empty values returned, the calls logged.
      reset()
      const log1 = join(scratch, 'own.jsonl')
      const clip1 = ownClipboard(NAMES)
      const app1 = fakeApp()
      expect(install(electron(clip1, app1), log1)).toEqual({ ok: true, failed: [] })
      expect(lines(log1)).toEqual([{ installed: true, names: [...NAMES] }])
      expect(g[MARK]).toBe(true)
      for (const name of NAMES) {
        const fn = clip1[name] as Fn
        expect(Reflect.get(fn, MARK), `${name} is tagged`).toBe(true)
        expect(Object.keys(clip1), `${name} is not enumerable`).not.toContain(name)
      }
      const call = (name: string, ...args: unknown[]): unknown => {
        const fn = clip1[name] as Fn
        if (Reflect.get(fn, MARK) !== true) throw new Error(`${name} is not the tagged recorder`)
        return fn(...args)
      }
      expect(call('writeText', 'x')).toBeUndefined()
      expect(call('readText')).toBe('')
      expect(call('readHTML')).toBe('')
      expect(call('readRTF')).toBe('')
      expect(call('readFindText')).toBe('')
      expect(call('availableFormats')).toEqual([])
      expect(call('has', 'text/plain')).toBe(false)
      expect(call('readImage')).toBe(EMPTY_IMAGE)
      expect(call('readBookmark')).toEqual({ title: '', url: '' })
      expect(String(call('read', 'x') ?? '')).toBe('')
      expect(String(call('readBuffer', 'x') ?? '')).toBe('')
      expect(call('clear')).toBeUndefined()
      expect(lines(log1).slice(1)).toEqual([
        { call: 'main writeText', kind: 'write' },
        { call: 'main readText', kind: 'read' },
        { call: 'main readHTML', kind: 'read' },
        { call: 'main readRTF', kind: 'read' },
        { call: 'main readFindText', kind: 'read' },
        { call: 'main availableFormats', kind: 'read' },
        { call: 'main has', kind: 'read' },
        { call: 'main readImage', kind: 'read' },
        { call: 'main readBookmark', kind: 'read' },
        { call: 'main read', kind: 'read' },
        { call: 'main readBuffer', kind: 'read' },
        { call: 'main clear', kind: 'write' },
      ])
      expect(g.__avkitClipboardGuardCalls).toEqual(lines(log1).slice(1).map((row) => row.call))

      // A writer on the prototype, and another function there: both replaced by own recorders.
      reset()
      const log2 = join(scratch, 'proto.jsonl')
      const proto = { writeText: original('proto writeText'), writeSomethingNew: original('proto writeSomethingNew') }
      const clip2 = Object.assign(Object.create(proto) as Record<string, unknown>, ownClipboard(NAMES.filter((n) => n !== 'writeText')))
      expect(Object.prototype.hasOwnProperty.call(clip2, 'writeText')).toBe(false)
      expect(install(electron(clip2, fakeApp()), log2).ok).toBe(true)
      for (const name of ['writeText', 'writeSomethingNew']) {
        expect(Object.prototype.hasOwnProperty.call(clip2, name), `${name} is an own recorder`).toBe(true)
        expect(Reflect.get(clip2[name] as Fn, MARK), `${name} is tagged`).toBe(true)
        expect(() => (clip2[name] as Fn)('x'), name).not.toThrow()
      }
      expect(lines(log2)[0]).toEqual({ installed: true, names: [...NAMES] })

      // A name missing: refused, a failed line naming it, no installed line, no marker, no hooks.
      reset()
      const log3 = join(scratch, 'missing.jsonl')
      const app3 = fakeApp()
      const result3 = install(electron(ownClipboard(NAMES.filter((n) => n !== 'has')), app3), log3)
      expect(result3.ok).toBe(false)
      expect(result3.failed).toContain('missing has')
      expect(lines(log3)).toEqual([{ failed: 'missing has' }])
      expect(g[MARK]).toBeUndefined()
      expect(app3.handlers.size).toBe(0)

      // A name that cannot be replaced: refused the same way.
      reset()
      const log4 = join(scratch, 'fixed.jsonl')
      const clip4 = ownClipboard(NAMES.filter((n) => n !== 'readText'))
      Object.defineProperty(clip4, 'readText', { value: original('clipboard.readText'), writable: false, configurable: false })
      const app4 = fakeApp()
      const result4 = install(electron(clip4, app4), log4)
      expect(result4.ok).toBe(false)
      expect(result4.failed).toEqual(['unreplaced readText'])
      expect(lines(log4)).toEqual([{ failed: 'unreplaced readText' }])
      expect(g[MARK]).toBeUndefined()
      expect(app4.handlers.size).toBe(0)

      // The hooks, on a fake webContents whose native methods throw if called.
      reset()
      const log5 = join(scratch, 'hooks.jsonl')
      const app5 = fakeApp()
      expect(install(electron(ownClipboard(NAMES), app5), log5).ok).toBe(true)
      const created = app5.handlers.get('web-contents-created') ?? []
      expect(created).toHaveLength(1)
      const permissionSetters = { request: 0, check: 0 }
      let requestHandler: Fn = () => undefined
      let checkHandler: Fn = () => undefined
      const session = {
        setPermissionRequestHandler(fn: Fn) {
          permissionSetters.request += 1
          requestHandler = fn
        },
        setPermissionCheckHandler(fn: Fn) {
          permissionSetters.check += 1
          checkHandler = fn
        },
      }
      const fakeWc = (): {
        wc: Record<string, unknown>
        handlers: Map<string, Fn[]>
        onceEvents: string[]
        scripts: string[]
      } => {
        const handlers = new Map<string, Fn[]>()
        const onceEvents: string[] = []
        const scripts: string[] = []
        const wc: Record<string, unknown> = {
          session,
          on(event: string, fn: Fn) {
            handlers.set(event, [...(handlers.get(event) ?? []), fn])
            return wc
          },
          once(event: string) {
            onceEvents.push(event)
            return wc
          },
          executeJavaScript(script: string) {
            scripts.push(script)
            return Promise.resolve()
          },
          replace: original('wc.replace'),
          replaceMisspelling: original('wc.replaceMisspelling'),
        }
        for (const name of ['copy', 'cut', 'paste', 'pasteAndMatchStyle', 'copyImageAt']) wc[name] = original(`wc.${name}`)
        return { wc, handlers, onceEvents, scripts }
      }
      const first = fakeWc()
      const replaceBefore = first.wc.replace
      const misspellingBefore = first.wc.replaceMisspelling
      created[0]({}, first.wc)
      created[0]({}, fakeWc().wc)
      expect(permissionSetters, 'the permission handlers are set once per session').toEqual({ request: 1, check: 1 })
      expect(first.onceEvents, 'no hook is registered once').toEqual([])
      const emit = (event: string, ...args: unknown[]): void => {
        for (const fn of first.handlers.get(event) ?? []) fn(...args)
      }
      expect(first.handlers.get('dom-ready'), 'dom-ready is registered with on').toHaveLength(1)
      emit('dom-ready')
      emit('dom-ready')
      expect(first.scripts, 'each load patches the page again').toHaveLength(2)
      expect(first.scripts[0].endsWith(')(globalThis)')).toBe(true)
      expect(first.wc.replace, 'wc.replace is left alone').toBe(replaceBefore)
      expect(first.wc.replaceMisspelling, 'wc.replaceMisspelling is left alone').toBe(misspellingBefore)
      const start5 = lines(log5).length
      for (const name of ['copy', 'cut', 'paste', 'pasteAndMatchStyle', 'copyImageAt']) {
        const fn = first.wc[name] as Fn
        if (Reflect.get(fn, MARK) !== true) throw new Error(`wc.${name} is not the tagged recorder`)
        expect(() => fn(1, 2), `wc.${name}`).not.toThrow()
      }
      expect(lines(log5).slice(start5)).toEqual([
        { call: 'webContents copy', kind: 'write' },
        { call: 'webContents cut', kind: 'write' },
        { call: 'webContents paste', kind: 'read' },
        { call: 'webContents pasteAndMatchStyle', kind: 'read' },
        { call: 'webContents copyImageAt', kind: 'write' },
      ])

      // The renderer's reports through console-message, in the event form and the positional form.
      const start5b = lines(log5).length
      emit('console-message', { message: CONSOLE_TAG + JSON.stringify({ call: 'writeText' }) })
      emit('console-message', {}, 1, CONSOLE_TAG + JSON.stringify({ call: 'execCommand paste' }), 1, 'x')
      emit('console-message', { message: 'an ordinary log line' })
      expect(lines(log5).slice(start5b)).toEqual([
        { call: 'renderer writeText', kind: 'write' },
        { call: 'renderer execCommand paste', kind: 'read' },
      ])

      // The copy and paste chords are recorded and prevented; the negative oracles pass.
      const key = (k: string, mods: { control?: boolean; meta?: boolean; shift?: boolean } = {}) => ({
        type: 'keyDown',
        key: k,
        control: mods.control ?? false,
        meta: mods.meta ?? false,
        shift: mods.shift ?? false,
        alt: false,
      })
      const press = (input: ReturnType<typeof key>): boolean => {
        let prevented = false
        emit('before-input-event', { preventDefault: () => (prevented = true) }, input)
        return prevented
      }
      const start5c = lines(log5).length
      const chords: Array<[ReturnType<typeof key>, string]> = [
        [key('c', { control: true }), 'Control+C'],
        [key('x', { control: true }), 'Control+X'],
        [key('Insert', { control: true }), 'Control+Insert'],
        [key('Delete', { shift: true }), 'Shift+Delete'],
        [key('v', { control: true }), 'Control+V'],
        [key('V', { control: true, shift: true }), 'Control+Shift+V'],
        [key('Insert', { shift: true }), 'Shift+Insert'],
      ]
      for (const [input, name] of chords) expect(press(input), name).toBe(true)
      for (const input of [key('v'), key('V', { shift: true }), key('Insert')]) {
        expect(press(input), JSON.stringify(input)).toBe(false)
      }
      expect(lines(log5).slice(start5c)).toEqual([
        { call: 'input Control+C', kind: 'write' },
        { call: 'input Control+X', kind: 'write' },
        { call: 'input Control+Insert', kind: 'write' },
        { call: 'input Shift+Delete', kind: 'write' },
        { call: 'input Control+V', kind: 'read' },
        { call: 'input Control+Shift+V', kind: 'read' },
        { call: 'input Shift+Insert', kind: 'read' },
      ])

      // The two clipboard permissions are denied and recorded; another is allowed.
      const start5d = lines(log5).length
      const granted: Array<[string, unknown]> = []
      for (const permission of ['clipboard-read', 'clipboard-sanitized-write', 'media']) {
        requestHandler(first.wc, permission, (allow: unknown) => granted.push([permission, allow]))
      }
      expect(granted).toEqual([
        ['clipboard-read', false],
        ['clipboard-sanitized-write', false],
        ['media', true],
      ])
      expect(checkHandler(first.wc, 'clipboard-read')).toBe(false)
      expect(checkHandler(first.wc, 'clipboard-sanitized-write')).toBe(false)
      expect(checkHandler(first.wc, 'notifications')).toBe(true)
      expect(lines(log5).slice(start5d)).toEqual([
        { call: 'permission clipboard-read', kind: 'read' },
        { call: 'permission clipboard-sanitized-write', kind: 'write' },
        { call: 'permission clipboard-read', kind: 'read' },
        { call: 'permission clipboard-sanitized-write', kind: 'write' },
      ])

      // The page half on a fake page, run twice; and the same function as the script text it ships.
      const pageGlobal = (): {
        page: Record<string, unknown>
        logged: string[]
        commands: string[]
        Clipboard: { prototype: Record<string, unknown> }
        Document: { prototype: Record<string, unknown> }
      } => {
        const logged: string[] = []
        const commands: string[] = []
        const Clipboard = { prototype: {} as Record<string, unknown> }
        for (const name of ['read', 'readText', 'write', 'writeText']) Clipboard.prototype[name] = original(`Clipboard.${name}`)
        const Document = {
          prototype: {
            execCommand(command: string) {
              commands.push(command)
              return true
            },
          } as Record<string, unknown>,
        }
        const page = { Clipboard, Document, console: { log: (line: string) => logged.push(line) } }
        return { page, logged, commands, Clipboard, Document }
      }
      for (const runner of ['function', 'script'] as const) {
        const fake = pageGlobal()
        const run = (): void => {
          if (runner === 'function') rendererGuard(fake.page)
          else new Function('globalThis', first.scripts[0])(fake.page)
        }
        run()
        const patched = ['read', 'readText', 'write', 'writeText'].map((name) => fake.Clipboard.prototype[name])
        const exec = fake.Document.prototype.execCommand
        run()
        expect(['read', 'readText', 'write', 'writeText'].map((name) => fake.Clipboard.prototype[name]), runner).toEqual(patched)
        expect(fake.Document.prototype.execCommand, runner).toBe(exec)
        expect(fake.page[MARK], runner).toBe(true)
        const results: unknown[] = []
        for (const name of ['writeText', 'readText', 'read', 'write']) {
          const fn = fake.Clipboard.prototype[name] as Fn
          if (Reflect.get(fn, MARK) !== true) throw new Error(`Clipboard.${name} is not the tagged recorder`)
          results.push(await (fn.call({}, 'x') as Promise<unknown>))
        }
        expect(results, runner).toEqual([undefined, '', [], undefined])
        const execCommand = exec as Fn
        expect(Reflect.get(execCommand, MARK), runner).toBe(true)
        expect(execCommand.call({}, 'copy'), runner).toBe(false)
        expect(execCommand.call({}, 'cut'), runner).toBe(false)
        expect(execCommand.call({}, 'paste'), runner).toBe(false)
        expect(execCommand.call({}, 'bold'), runner).toBe(true)
        expect(fake.commands, runner).toEqual(['bold'])
        expect(fake.logged, runner).toEqual(
          ['writeText', 'readText', 'read', 'write', 'execCommand copy', 'execCommand cut', 'execCommand paste'].map(
            (name) => CONSOLE_TAG + JSON.stringify({ call: name }),
          ),
        )
      }
    } finally {
      reset()
      rmSync(scratch, { recursive: true, force: true })
    }
  })

  it('S100 AC-9 launchElectron preloads the guard, names its log and joins its verdict with the main-error check at close', () => {
    expect(existsSync(APP_PATH), 'ui/tests/e2e/electron-app.ts exists').toBe(true)
    const app = readFileSync(APP_PATH, 'utf8')
    for (const name of ['clipboardGuardArgs(', 'clipboardGuardLogPath(', 'clipboardGuardVerdict(']) {
      // A boolean, so a failure never prints the file (it holds the launch call).
      expect(app.includes(name), `electron-app.ts calls ${name}`).toBe(true)
    }
    const closeAt = app.indexOf('app.close = ')
    expect(closeAt, 'the close wrapper').toBeGreaterThan(-1)
    const close = app.slice(closeAt)
    const checkAt = close.indexOf('checkMainErrors(')
    expect(checkAt, 'checkMainErrors( in close').toBeGreaterThan(-1)
    const readAt = close.indexOf('readFileSync(guardLog')
    expect(readAt, 'the guard-log read in close').toBeGreaterThan(-1)
    expect(readAt, 'the guard log is read before checkMainErrors deletes the folder').toBeLessThan(checkAt)
    const tryAt = close.lastIndexOf('try {', checkAt)
    expect(tryAt, 'checkMainErrors( sits inside a try').toBeGreaterThan(-1)
    expect(close.slice(tryAt, checkAt).includes('}'), 'no block closes between the try and checkMainErrors(').toBe(false)
    expect(close.indexOf('clipboardGuardVerdict('), 'the verdict is taken in close').toBeGreaterThan(-1)
  })
})
