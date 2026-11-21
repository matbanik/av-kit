/** @vitest-environment jsdom */

/**
 * MEU-162 (Session 99): the quick start in each page's How it works card.
 *
 * - AC-162.1: `QUICK_START` validates, and every step target is rendered on its page.
 * - AC-162.3: the closed header names the quick start; the open card lists the steps first.
 * - AC-162.4: the theme rules (`css`) and one figure per shot with a light and a dark image
 *   (`figures`, red by assertion until the images exist in row 8).
 * - AC-162.5: a search hides the quick start and opens the matching topics; `AC-162.5 no match`
 *   is a guard that passes at Red.
 * - AC-162.6: with the search empty, the topics are closed `<details>`.
 * - AC-162.7: the image manifest matches `QUICK_START` and the WebP files.
 * - AC-162.9: the topic rewrite keeps ids, order, pinned text and the facts, and drops the jargon.
 *
 * `quick-start.ts`, `help-shots.ts` and `assets/help/manifest.json` are new in this MEU, so they
 * are reached through `import.meta.glob` and each test asserts the module and its exports first:
 * at Red each test fails by assertion, never by a missing module.
 */

import { createHash } from 'node:crypto'
import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { cleanup, render } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it } from 'vitest'

import { HelpCard, type HelpSection } from '../../src/renderer/src/components/help/HelpCard'
import { CAPTURE_HELP_SECTIONS } from '../../src/renderer/src/features/capture/capture-help-content'
import { CONVERT_HELP_SECTIONS } from '../../src/renderer/src/features/converter/convert-help-content'
import { DOWNLOADER_HELP_SECTIONS } from '../../src/renderer/src/features/downloader/downloader-help-content'
import { SETTINGS_HELP_SECTIONS } from '../../src/renderer/src/features/settings/settings-help-content'
import { TRANSCRIPT_HELP_SECTIONS } from '../../src/renderer/src/features/transcript/transcript-help-content'
import { TTS_HELP_SECTIONS } from '../../src/renderer/src/features/tts/tts-help-content'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')
const rendererDir = resolve(repoRoot, 'ui/src/renderer/src')
const assetsDir = resolve(rendererDir, 'assets/help')
const PINS_PATH = resolve(repoRoot, 'docs/execution/plans/2026-11-20-help-quick-start/baseline-pins.json')

// ---------------------------------------------------------------------------
// The new modules, loaded without a static import (they do not exist at Red).
// ---------------------------------------------------------------------------

type Feature = 'downloader' | 'transcript' | 'tts' | 'converter' | 'capture' | 'settings'
type Theme = 'light' | 'dark'
type QuickStartStep = { text: string; target: string | null }
type QuickStartShot = { name: string; steps: number[]; alt: string }
type QuickStartPage = { intro: string; steps: QuickStartStep[]; shots: QuickStartShot[] }
type QuickStartData = Record<Feature, QuickStartPage>

type QuickStartModule = {
  QUICK_START: QuickStartData
  validateQuickStart: (data: unknown) => string[]
  quickStartHash: (page: QuickStartPage) => Promise<string>
  quickStartHashInput: (page: QuickStartPage) => string
}
type HelpShotsModule = {
  shotUrl: (name: string, theme: Theme) => string | null
  shotSize: (name: string) => { width: number; height: number } | null
}
type ManifestEntry = {
  name: string
  page: string
  width: number
  height: number
  bytes: { light: number; dark: number }
  stepsHash: string
}

const quickStartModules = import.meta.glob('../../src/renderer/src/components/help/quick-start.ts', { eager: true })
const helpShotsModules = import.meta.glob('../../src/renderer/src/components/help/help-shots.ts', { eager: true })
const manifestModules = import.meta.glob('../../src/renderer/src/assets/help/manifest.json', {
  eager: true,
  import: 'default',
})

function loaded(modules: Record<string, unknown>): Record<string, unknown> {
  return (Object.values(modules)[0] ?? {}) as Record<string, unknown>
}

/** Assert every name this file uses from `quick-start.ts` before it is used. */
function requireQuickStart(): QuickStartModule {
  const mod = loaded(quickStartModules)
  for (const name of ['validateQuickStart', 'quickStartHash', 'quickStartHashInput']) {
    expect(typeof mod[name], `components/help/quick-start.ts exports ${name}`).toBe('function')
  }
  expect(typeof mod.QUICK_START, 'components/help/quick-start.ts exports QUICK_START').toBe('object')
  return mod as unknown as QuickStartModule
}

/** Assert every name this file uses from `help-shots.ts` before it is used. */
function requireHelpShots(): HelpShotsModule {
  const mod = loaded(helpShotsModules)
  for (const name of ['shotUrl', 'shotSize']) {
    expect(typeof mod[name], `components/help/help-shots.ts exports ${name}`).toBe('function')
  }
  return mod as unknown as HelpShotsModule
}

function requireManifest(): ManifestEntry[] {
  const manifest = Object.values(manifestModules)[0]
  expect(manifest, 'assets/help/manifest.json exists').toBeDefined()
  expect(Array.isArray(manifest), 'assets/help/manifest.json is a list').toBe(true)
  return manifest as ManifestEntry[]
}

// ---------------------------------------------------------------------------
// Pages, folders and the card.
// ---------------------------------------------------------------------------

const FEATURES: readonly Feature[] = ['downloader', 'transcript', 'tts', 'converter', 'capture', 'settings']

const SECTIONS: Record<Feature, HelpSection[]> = {
  downloader: DOWNLOADER_HELP_SECTIONS,
  transcript: TRANSCRIPT_HELP_SECTIONS,
  tts: TTS_HELP_SECTIONS,
  converter: CONVERT_HELP_SECTIONS,
  capture: CAPTURE_HELP_SECTIONS,
  settings: SETTINGS_HELP_SECTIONS,
}

const FEATURE_FOLDER: Record<Feature, string> = {
  downloader: 'features/downloader',
  transcript: 'features/transcript',
  tts: 'features/tts',
  converter: 'features/converter',
  capture: 'features/capture',
  settings: 'features/settings',
}

const TAB_KEY = 'main'
const NO_MATCH = 'No help topics match your search.'
const MORE_HEADING = 'More about this page'

function sourceFiles(dir: string): string[] {
  const out: string[] = []
  for (const name of readdirSync(dir)) {
    const path = join(dir, name)
    if (statSync(path).isDirectory()) {
      out.push(...sourceFiles(path))
    } else if (/\.(ts|tsx)$/.test(name) && !/\.test\.tsx?$/.test(name)) {
      out.push(path)
    }
  }
  return out
}

function folderSource(feature: Feature): string {
  return [...sourceFiles(resolve(rendererDir, FEATURE_FOLDER[feature])), ...sourceFiles(resolve(rendererDir, 'components'))]
    .map((path) => readFileSync(path, 'utf8'))
    .join('\n')
}

function escapeRegExp(text: string): string {
  return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

/**
 * A target is rendered when the page's folder or `components/` holds it as a whole string
 * literal (`data-testid="x"`, a constant or a map value), or as a template `` `p${…}` `` whose
 * rest is a whole string literal there (`convert-task-${value}` with `'compress'`).
 */
function targetRendered(target: string, source: string): boolean {
  if (new RegExp(`(['"\`])${escapeRegExp(target)}\\1`).test(source)) {
    return true
  }
  for (const match of source.matchAll(/`([a-z0-9-]+)\$\{/g)) {
    const prefix = match[1]
    if (target.startsWith(prefix) && target.length > prefix.length) {
      const rest = target.slice(prefix.length)
      if (new RegExp(`(['"\`])${escapeRegExp(rest)}\\1`).test(source)) {
        return true
      }
    }
  }
  return false
}

function targetProblems(data: QuickStartData, sources: Record<Feature, string>): string[] {
  const problems: string[] = []
  for (const feature of FEATURES) {
    data[feature].steps.forEach((step, index) => {
      if (step.target !== null && !targetRendered(step.target, sources[feature])) {
        problems.push(`${feature} step ${index + 1}: target ${step.target} is not rendered on the page`)
      }
    })
  }
  return problems
}

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T
}

function renderCard(feature: Feature, expanded: boolean) {
  if (expanded) {
    localStorage.setItem(`av-kit:${feature}-help:${TAB_KEY}:state`, 'expanded')
  }
  const view = render(<HelpCard feature={feature} tabKey={TAB_KEY} sections={SECTIONS[feature]} />)
  const header = view.container.querySelector('button[aria-expanded]')
  expect(header, 'the card header button').not.toBeNull()
  return { ...view, header: header as HTMLButtonElement }
}

function byTestId(root: ParentNode, id: string): Element | null {
  return root.querySelector(`[data-testid="${id}"]`)
}

function allByTestId(root: ParentNode, id: string): Element[] {
  return [...root.querySelectorAll(`[data-testid="${id}"]`)]
}

function moreHeading(root: ParentNode): Element | undefined {
  return [...root.querySelectorAll('h3')].find((h) => h.textContent?.trim() === MORE_HEADING)
}

function topics(root: ParentNode): Element[] {
  return [...root.querySelectorAll('[data-help-section]')]
}

// ---------------------------------------------------------------------------
// The image manifest (AC-162.7).
// ---------------------------------------------------------------------------

const MAX_BYTES = 153_600
const MAX_WIDTH = 1280
const MAX_HEIGHT = 900
const ENTRY_KEYS = ['bytes', 'height', 'name', 'page', 'stepsHash', 'width']

/** Width and height from a RIFF/WebP header (VP8, VP8L or VP8X), or null. */
function webpSize(buf: Buffer): { width: number; height: number } | null {
  if (buf.length < 30 || buf.toString('ascii', 0, 4) !== 'RIFF' || buf.toString('ascii', 8, 12) !== 'WEBP') {
    return null
  }
  const chunk = buf.toString('ascii', 12, 16)
  if (chunk === 'VP8X') {
    return { width: 1 + buf.readUIntLE(24, 3), height: 1 + buf.readUIntLE(27, 3) }
  }
  if (chunk === 'VP8 ' && buf[23] === 0x9d && buf[24] === 0x01 && buf[25] === 0x2a) {
    return { width: buf.readUInt16LE(26) & 0x3fff, height: buf.readUInt16LE(28) & 0x3fff }
  }
  if (chunk === 'VP8L' && buf[20] === 0x2f) {
    const bits = buf.readUInt32LE(21)
    return { width: (bits & 0x3fff) + 1, height: ((bits >> 14) & 0x3fff) + 1 }
  }
  return null
}

function manifestProblems(
  data: QuickStartData,
  manifest: ManifestEntry[],
  read: (file: string) => Buffer | null,
  hash: (page: QuickStartPage) => string,
): string[] {
  const problems: string[] = []
  const owner = new Map<string, Feature>()
  for (const feature of FEATURES) {
    for (const shot of data[feature].shots) {
      owner.set(shot.name, feature)
    }
  }
  const names = manifest.map((entry) => entry.name)
  for (const name of owner.keys()) {
    if (!names.includes(name)) {
      problems.push(`manifest: no entry for shot ${name}`)
    }
  }
  for (const name of names) {
    if (!owner.has(name)) {
      problems.push(`manifest: entry ${name} is not a shot in QUICK_START`)
    }
    if (names.indexOf(name) !== names.lastIndexOf(name)) {
      problems.push(`manifest: entry ${name} occurs more than once`)
    }
  }
  for (const entry of manifest) {
    const keys = Object.keys(entry).sort()
    if (JSON.stringify(keys) !== JSON.stringify(ENTRY_KEYS)) {
      problems.push(`manifest ${entry.name}: keys ${keys.join(',')}`)
      continue
    }
    if (JSON.stringify(Object.keys(entry.bytes).sort()) !== JSON.stringify(['dark', 'light'])) {
      problems.push(`manifest ${entry.name}: bytes keys ${Object.keys(entry.bytes).join(',')}`)
    }
    const feature = owner.get(entry.name)
    if (feature === undefined) {
      continue
    }
    if (entry.page !== feature) {
      problems.push(`manifest ${entry.name}: page ${entry.page}, not ${feature}`)
    }
    if (entry.stepsHash !== hash(data[feature])) {
      problems.push(`${feature}: stepsHash of ${entry.name} differs; the steps changed, so take the images again`)
    }
    if (entry.width > MAX_WIDTH || entry.height > MAX_HEIGHT) {
      problems.push(`manifest ${entry.name}: ${entry.width} x ${entry.height} is over ${MAX_WIDTH} x ${MAX_HEIGHT}`)
    }
    for (const theme of ['light', 'dark'] as const) {
      const file = `${entry.name}-${theme}.webp`
      const buf = read(file)
      if (buf === null) {
        problems.push(`${file} missing`)
        continue
      }
      if (buf.length > MAX_BYTES) {
        problems.push(`${file} is ${buf.length} bytes, over ${MAX_BYTES}`)
      }
      if (entry.bytes[theme] !== buf.length) {
        problems.push(`${file}: manifest says ${entry.bytes[theme]} bytes, the file has ${buf.length}`)
      }
      const size = webpSize(buf)
      if (size === null) {
        problems.push(`${file} has no WebP header`)
      } else if (size.width !== entry.width || size.height !== entry.height) {
        problems.push(`${file} is ${size.width} x ${size.height}, the manifest says ${entry.width} x ${entry.height}`)
      }
    }
  }
  return problems
}

/** A WebP header (VP8X) of the given size, padded to `length` bytes. */
function fakeWebp(width: number, height: number, length = 30): Buffer {
  const buf = Buffer.alloc(length)
  buf.write('RIFF', 0, 'ascii')
  buf.writeUInt32LE(length - 8, 4)
  buf.write('WEBP', 8, 'ascii')
  buf.write('VP8X', 12, 'ascii')
  buf.writeUInt32LE(10, 16)
  buf.writeUIntLE(width - 1, 24, 3)
  buf.writeUIntLE(height - 1, 27, 3)
  return buf
}

// ---------------------------------------------------------------------------
// The topic rewrite (AC-162.9, §Fact table).
// ---------------------------------------------------------------------------

type Pins = {
  modules: Record<
    string,
    {
      path: string
      topics: { id: string; title: string }[]
      pinned: Record<string, { title: string; body: string }>
    }
  >
}

const SAVE_OLD = 'Save POSTs the full annotation list.'
const SAVE_NEW = 'Save stores all the marks on the shot.'

const JARGON = [
  'GET ',
  'PUT ',
  'POST',
  '/settings/',
  '{namespace}',
  'capture.inbox_dir',
  'chunk_max_chars',
  'ffmpeg.available',
  'quit intent',
  'log_level',
  'log_to_file',
  'console_visible',
  '{app_data}',
] as const

const FACTS: Record<string, readonly string[]> = {
  'downloader:url-types': ['video', 'playlist', 'channel'],
  'downloader:sabr': ['SABR', 'check'],
  'downloader:cookies': ['cookie', 'browser', 'file', 'test'],
  'downloader:archive': ['archive', 'Settings', 'skip'],
  'transcript:resume': ['Resume'],
  'transcript:cancelled': ['Stop', 'Cancelled'],
  'transcript:requeue': ['requeue', 'folder'],
  'transcript:compile': ['compile', 'zip'],
  'transcript:rate': ['rate', 'Settings'],
  'tts:prepare': ['prepare', 'Generate'],
  'tts:voice': ['voice', 'language', 'speed'],
  'tts:download': ['download', 'Kokoro', 'models folder'],
  'tts:load': ['load', 'Unload'],
  'tts:paste': ['paste', '.txt', '.md', 'Settings'],
  'converter:what-convert-does': ['Compress', 'cut', 'audio', 'YouTube'],
  'converter:presets-advanced': ['preset', 'Advanced', 'CQ'],
  'converter:gpu-software': ['NVENC', 'AMF', 'QSV', 'Software', 'Refresh', 'FFmpeg'],
  'converter:fast-cut': ['Fast cut', 'keyframe', 'Accurate'],
  'converter:extract-containers': ['first audio', '.m4a', '.wav'],
  'converter:sequential-gpu': ['one file at a time', 'GPU'],
  'capture:what-capture-does': ['F2', 'PNG', 'inbox', 'never uploads'],
  'capture:f2-sharex': ['ShareX', 'banner'],
  'capture:inbox-folder': ['PNG', 'inbox', 'Browse', 'Save'],
  'capture:mcp-png': ['MCP', 'list', 'read'],
  'capture:close-to-tray': ['tray', 'F2', 'Quit'],
  'capture:never-uploads': ['YouTube'],
  'settings:leaf-keys': ['Save', 'card', 'as you type'],
  'settings:ffmpeg': ['FFmpeg', 'Check dependencies'],
  'settings:mcp': ['MCP', 'token'],
  'settings:console': ['Errors', 'always', 'Log to file', 'header'],
  'settings:startup': ['sign in', 'administrator', 'Task Manager', 'Start minimized', 'F2'],
}

const MODULE_SECTIONS: Record<string, HelpSection[]> = {
  downloader: DOWNLOADER_HELP_SECTIONS,
  transcript: TRANSCRIPT_HELP_SECTIONS,
  tts: TTS_HELP_SECTIONS,
  converter: CONVERT_HELP_SECTIONS,
  capture: CAPTURE_HELP_SECTIONS,
  settings: SETTINGS_HELP_SECTIONS,
}

// ---------------------------------------------------------------------------

describe('MEU-162 help quick start', () => {
  afterEach(() => {
    cleanup()
    localStorage.clear()
  })

  it('AC-162.1 QUICK_START validates and every step target is rendered on its page', () => {
    const qs = requireQuickStart()
    expect(qs.validateQuickStart(qs.QUICK_START)).toEqual([])
    expect(Object.keys(qs.QUICK_START).sort()).toEqual([...FEATURES].sort())
    for (const feature of FEATURES) {
      const page = qs.QUICK_START[feature]
      expect(typeof page.intro, `${feature} intro`).toBe('string')
      expect(page.steps.length, `${feature} steps`).toBeGreaterThanOrEqual(4)
      expect(page.steps.length, `${feature} steps`).toBeLessThanOrEqual(5)
      expect(page.shots.length, `${feature} shots`).toBeGreaterThanOrEqual(1)
      expect(page.shots.length, `${feature} shots`).toBeLessThanOrEqual(2)
    }
    const sources = Object.fromEntries(FEATURES.map((f) => [f, folderSource(f)])) as Record<Feature, string>
    expect(targetProblems(qs.QUICK_START, sources)).toEqual([])
  })

  it('AC-162.1 each bad fixture gives one named problem', () => {
    const qs = requireQuickStart()
    const fixtures: [string, Feature, (data: QuickStartData) => void][] = [
      ['a 6-step page', 'downloader', (d) => void d.downloader.steps.push({ text: 'Click Stop.', target: null })],
      ['a step in no shot', 'downloader', (d) => void (d.downloader.shots[0].steps = [2, 3, 4])],
      ['a step in two shots', 'settings', (d) => void d.settings.shots[1].steps.push(2)],
      [
        'a 21-word sentence',
        'transcript',
        (d) =>
          void (d.transcript.steps[0].text =
            'Click the large blue button at the top of the page and then wait for the app to finish the work.'),
      ],
      ['a semicolon', 'tts', (d) => void (d.tts.steps[0].text = 'Select a model; then wait.')],
      ['an unknown key', 'capture', (d) => void ((d.capture as unknown as Record<string, unknown>).extra = 1)],
    ]
    for (const [name, feature, change] of fixtures) {
      const data = clone(qs.QUICK_START)
      change(data)
      const problems = qs.validateQuickStart(data)
      expect(problems, name).toHaveLength(1)
      expect(problems[0], name).toContain(feature)
    }
    const data = clone(qs.QUICK_START)
    data.converter.steps[1].target = 'no-such-target-zz'
    const sources = Object.fromEntries(FEATURES.map((f) => [f, folderSource(f)])) as Record<Feature, string>
    const unknown = targetProblems(data, sources)
    expect(unknown, 'an unknown target').toHaveLength(1)
    expect(unknown[0], 'an unknown target').toContain('no-such-target-zz')
  })

  it('AC-162.3 the closed header names the quick start, and the open card lists the steps before the topics', async () => {
    const qs = requireQuickStart()
    const page = qs.QUICK_START.downloader
    expect(page.steps).toHaveLength(5)
    const user = userEvent.setup()
    const { container, header } = renderCard('downloader', false)
    expect(header.getAttribute('aria-expanded')).toBe('false')
    const hint = byTestId(container, 'help-quick-start-hint')
    expect(hint, 'help-quick-start-hint').not.toBeNull()
    expect(header.contains(hint), 'the hint is inside the header button').toBe(true)
    expect(hint?.textContent).toBe(`Quick start · ${page.steps.length} steps`)
    expect(hint?.textContent).toBe('Quick start · 5 steps')

    await user.click(header)
    expect(header.getAttribute('aria-expanded')).toBe('true')
    const intro = byTestId(container, 'help-quick-start-intro')
    expect(intro?.textContent).toBe(page.intro)
    const list = byTestId(container, 'help-quick-start')
    expect(list?.tagName).toBe('OL')
    const steps = allByTestId(container, 'help-quick-start-step')
    expect(steps.map((el) => el.textContent)).toEqual(page.steps.map((step) => step.text))
    expect(steps.map((el) => el.getAttribute('data-step'))).toEqual(page.steps.map((_, i) => String(i + 1)))
    expect(steps.every((el) => list?.contains(el))).toBe(true)
    const first = topics(container)[0]
    expect(first, 'a topic').toBeDefined()
    expect(Boolean(list && list.compareDocumentPosition(first) & Node.DOCUMENT_POSITION_FOLLOWING)).toBe(true)
    const own = [intro, list, ...steps, ...allByTestId(container, 'help-shot')]
    expect(own.filter((el) => el?.closest('[data-help-section]'))).toEqual([])
  })

  it('AC-162.4 css: styles.css holds the two theme rules once each', () => {
    const css = readFileSync(resolve(rendererDir, 'styles.css'), 'utf8')
    const squash = (text: string) => text.replace(/\s+/g, ' ').replace(/\s*([{};])\s*/g, '$1')
    const flat = squash(css)
    for (const rule of [
      ':root.dark .help-shot__img--light { display: none; }',
      ':root:not(.dark) .help-shot__img--dark { display: none; }',
    ]) {
      expect(flat.split(squash(rule)).length - 1, rule).toBe(1)
    }
  })

  it('AC-162.4 figures: each shot renders one figure with a light and a dark image', () => {
    const qs = requireQuickStart()
    const shots = requireHelpShots()
    const manifest = requireManifest()
    for (const feature of FEATURES) {
      const page = qs.QUICK_START[feature]
      const { container, unmount } = renderCard(feature, true)
      const figures = allByTestId(container, 'help-shot')
      expect(figures, `${feature} figures`).toHaveLength(page.shots.length)
      for (const shot of page.shots) {
        const figure = container.querySelector(`[data-testid="help-shot"][data-shot="${shot.name}"]`)
        expect(figure, `${shot.name} figure`).not.toBeNull()
        expect(figure?.getAttribute('data-shot-steps')).toBe(shot.steps.join(','))
        const entry = manifest.find((e) => e.name === shot.name)
        expect(entry, `${shot.name} manifest entry`).toBeDefined()
        expect(shots.shotSize(shot.name)).toEqual({ width: entry?.width, height: entry?.height })
        const imgs = [...(figure?.querySelectorAll('img') ?? [])]
        expect(imgs, `${shot.name} images`).toHaveLength(2)
        for (const theme of ['light', 'dark'] as const) {
          const img = imgs.find((el) => el.classList.contains(`help-shot__img--${theme}`))
          expect(img, `${shot.name} ${theme} image`).toBeDefined()
          const url = shots.shotUrl(shot.name, theme)
          expect(url, `${shot.name} ${theme} url`).not.toBeNull()
          expect(img?.getAttribute('src')).toBe(url)
          expect(img?.getAttribute('loading')).toBe('lazy')
          expect(img?.getAttribute('decoding')).toBe('async')
          expect(img?.getAttribute('alt')).toBe(shot.alt)
          expect(img?.getAttribute('width')).toBe(String(entry?.width))
          expect(img?.getAttribute('height')).toBe(String(entry?.height))
        }
        expect(figure?.querySelector('figcaption')?.textContent).toBe(shot.alt)
      }
      unmount()
      localStorage.clear()
    }
  })

  it('AC-162.5 search: a query hides the quick start and opens the matching topic', async () => {
    const user = userEvent.setup()
    const { container } = renderCard('downloader', true)
    expect(byTestId(container, 'help-quick-start'), 'quick start list before the search').not.toBeNull()
    expect(byTestId(container, 'help-quick-start-intro'), 'intro before the search').not.toBeNull()
    expect(moreHeading(container), 'the More about this page heading before the search').toBeDefined()

    const search = byTestId(container, 'help-search') as HTMLInputElement
    await user.type(search, 'cookie')
    expect(byTestId(container, 'help-quick-start'), 'quick start list during the search').toBeNull()
    expect(byTestId(container, 'help-quick-start-intro'), 'intro during the search').toBeNull()
    expect(allByTestId(container, 'help-shot'), 'figures during the search').toEqual([])
    expect(moreHeading(container), 'heading during the search').toBeUndefined()
    const found = topics(container)
    expect(found.map((el) => el.getAttribute('data-help-section'))).toEqual(['cookies'])
    expect(found[0].hasAttribute('open'), 'the matching topic is open').toBe(true)

    await user.clear(search)
    expect(byTestId(container, 'help-quick-start'), 'quick start list after the search').not.toBeNull()
    expect(byTestId(container, 'help-quick-start-intro'), 'intro after the search').not.toBeNull()
    expect(moreHeading(container), 'heading after the search').toBeDefined()
    const back = topics(container)
    expect(back).toHaveLength(DOWNLOADER_HELP_SECTIONS.length)
    expect(back.filter((el) => el.hasAttribute('open')), 'open topics after the search').toEqual([])
  })

  it('AC-162.5 no match: a query with no hit shows the no-match text', async () => {
    const user = userEvent.setup()
    const { container, header } = renderCard('downloader', false)
    await user.click(header)
    const search = byTestId(container, 'help-search') as HTMLInputElement
    expect(search, 'help-search').not.toBeNull()
    await user.type(search, 'zzzz')
    expect(topics(container)).toEqual([])
    expect(container.textContent).toContain(NO_MATCH)
  })

  it('AC-162.6 with the search empty the topics are closed details that open on a click', async () => {
    const user = userEvent.setup()
    const { container } = renderCard('settings', true)
    const all = topics(container)
    expect(all).toHaveLength(SETTINGS_HELP_SECTIONS.length)
    for (const [index, el] of all.entries()) {
      const section = SETTINGS_HELP_SECTIONS[index]
      expect(el.tagName, `${section.id} element`).toBe('DETAILS')
      expect(el.hasAttribute('open'), `${section.id} open`).toBe(false)
      expect(el.querySelector('summary')?.textContent, `${section.id} summary`).toBe(section.title)
    }
    const first = all[0] as HTMLDetailsElement
    const summary = first.querySelector('summary')
    expect(summary, 'the first summary').not.toBeNull()
    await user.click(summary as HTMLElement)
    expect(first.open, 'the first topic opens on a click').toBe(true)
    expect(first.querySelector('p')?.textContent).toBe(SETTINGS_HELP_SECTIONS[0].body)
  })

  it('AC-162.7 the manifest matches QUICK_START and the WebP files', () => {
    const qs = requireQuickStart()
    const nodeHash = (page: QuickStartPage) =>
      createHash('sha256').update(qs.quickStartHashInput(page)).digest('hex')

    // Negatives on a fixture manifest built from the current data.
    const good = (data: QuickStartData, bytes = 30): ManifestEntry[] =>
      FEATURES.flatMap((feature) =>
        data[feature].shots.map((shot) => ({
          name: shot.name,
          page: feature,
          width: 800,
          height: 600,
          bytes: { light: bytes, dark: bytes },
          stepsHash: nodeHash(data[feature]),
        })),
      )
    const fixtureRead = () => fakeWebp(800, 600)
    expect(manifestProblems(qs.QUICK_START, good(qs.QUICK_START), fixtureRead, nodeHash), 'fixture').toEqual([])

    const changed = clone(qs.QUICK_START)
    changed.downloader.steps[1].text = 'Paste the link in the field.'
    const stale = manifestProblems(changed, good(qs.QUICK_START), fixtureRead, nodeHash)
    expect(stale, 'a changed step').toHaveLength(1)
    expect(stale[0], 'a changed step').toContain('downloader')

    const firstShot = qs.QUICK_START.downloader.shots[0].name
    const missing = manifestProblems(
      qs.QUICK_START,
      good(qs.QUICK_START),
      (file) => (file === `${firstShot}-dark.webp` ? null : fakeWebp(800, 600)),
      nodeHash,
    )
    expect(missing, 'a missing file').toEqual([`${firstShot}-dark.webp missing`])

    const big = manifestProblems(
      qs.QUICK_START,
      good(qs.QUICK_START, MAX_BYTES + 1),
      () => fakeWebp(800, 600, MAX_BYTES + 1),
      nodeHash,
    )
    expect(big.length, 'over-size files').toBeGreaterThan(0)
    expect(big.every((problem) => problem.includes(`over ${MAX_BYTES}`)), 'over-size files').toBe(true)

    // The real manifest and files.
    const manifest = requireManifest()
    const read = (file: string) => {
      const path = resolve(assetsDir, file)
      return existsSync(path) ? readFileSync(path) : null
    }
    expect(manifestProblems(qs.QUICK_START, manifest, read, nodeHash)).toEqual([])
  })

  it('AC-162.9 the topic rewrite keeps ids, order, pinned text and facts, and drops the jargon', () => {
    const pins = JSON.parse(readFileSync(PINS_PATH, 'utf8')) as Pins
    expect(Object.keys(pins.modules).sort()).toEqual(Object.keys(MODULE_SECTIONS).sort())
    const problems: string[] = []
    const unpinned: string[] = []
    for (const [feature, row0] of Object.entries(pins.modules)) {
      const sections = MODULE_SECTIONS[feature]
      const ids = sections.map((s) => s.id)
      if (JSON.stringify(ids) !== JSON.stringify(row0.topics.map((t) => t.id))) {
        problems.push(`${feature}: topic ids or order ${ids.join(',')} differ from row 0`)
      }
      for (const section of sections) {
        const key = `${feature}:${section.id}`
        const pinned = row0.pinned[section.id]
        if (pinned !== undefined) {
          if (section.title !== pinned.title) {
            problems.push(`${key}: pinned title changed`)
          }
          if (section.body !== pinned.body.replace(SAVE_OLD, SAVE_NEW)) {
            problems.push(`${key}: pinned body changed`)
          }
          continue
        }
        unpinned.push(key)
        const keywords = FACTS[key]
        if (keywords === undefined) {
          problems.push(`${key}: no row in the fact table`)
          continue
        }
        const lower = section.body.toLowerCase()
        for (const word of keywords) {
          if (!lower.includes(word.toLowerCase())) {
            problems.push(`${key}: keyword ${word} missing`)
          }
        }
        for (const token of JARGON) {
          if (section.body.includes(token)) {
            problems.push(`${key}: jargon ${JSON.stringify(token)}`)
          }
        }
      }
    }
    const fourTools = CAPTURE_HELP_SECTIONS.find((s) => s.id === 'four-tools')
    if (pins.modules.capture.pinned['four-tools']?.body.split(SAVE_OLD).length !== 2) {
      problems.push('capture:four-tools: the row-0 body does not hold the Save sentence once')
    }
    if (fourTools?.body.includes('POST')) {
      problems.push('capture:four-tools: holds POST')
    }
    expect(unpinned.sort()).toEqual(Object.keys(FACTS).sort())
    expect(problems).toEqual([])
  })
})
