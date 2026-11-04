/** @vitest-environment jsdom */

/**
 * MEU-43 — shared GUI primitives (AC-43.1 … AC-43.13).
 *
 * Red-phase contract for `UI_QUEUE_LIB_DIR` (`format`, `status-tokens`,
 * `status-config`, `envelope`) and `UI_PRIMITIVES_DIR` (`StatusBadge`,
 * `ProgressBar`, `SelectionCheckbox`, `ConfirmModal`). Every module is loaded with
 * a dynamic `import()` inside the test that needs it, so a missing module fails
 * exactly one AC instead of collapsing collection (RED_ORACLE requires one failed
 * title per AC id).
 *
 * No colour hex is authored here: AC-43.3/AC-43.4 parse `TOKEN_FILE` at test time
 * (`CONTRAST_THEME_SOURCE`) and compare against `CONTRAST_MEASURED`.
 */

import { readFileSync, readdirSync, statSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { act, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement, useState, type ReactElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { ApiError } from '../../src/renderer/src/lib/api'
import { JOB_STATUSES as CONVERT_STATUSES } from '../../src/renderer/src/features/converter/convert-controls'
import { JOB_STATUSES as DOWNLOAD_STATUSES } from '../../src/renderer/src/features/downloader/download-controls'
import { JOB_STATUSES as TRANSCRIPT_STATUSES } from '../../src/renderer/src/features/transcript/transcript-controls'
import { JOB_STATUSES as TTS_STATUSES } from '../../src/renderer/src/features/tts/tts-controls'

// Type-only imports are erased before the module is executed, so they give the
// Red phase full typing against modules that do not exist yet without making
// Vite resolve them at transform time.
import type * as FormatModule from '../../src/renderer/src/lib/queue/format'
import type * as StatusTokensModule from '../../src/renderer/src/lib/queue/status-tokens'
import type * as StatusConfigModule from '../../src/renderer/src/lib/queue/status-config'
import type * as EnvelopeModule from '../../src/renderer/src/lib/queue/envelope'
import type * as StatusBadgeModule from '../../src/renderer/src/components/ui/StatusBadge'
import type * as ProgressBarModule from '../../src/renderer/src/components/ui/ProgressBar'
import type * as SelectionCheckboxModule from '../../src/renderer/src/components/ui/SelectionCheckbox'
import type * as ConfirmModalModule from '../../src/renderer/src/components/ui/ConfirmModal'
import type * as QueueCardModule from '../../src/renderer/src/components/queue/QueueCard'
import type * as QueueListModule from '../../src/renderer/src/components/queue/QueueList'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')
const planDir = resolve(repoRoot, 'docs/execution/plans/2026-08-28-p10-queue-card-foundations')

const UI_ROOT = resolve(repoRoot, 'ui/src/renderer/src')
const UI_PRIMITIVES_DIR = resolve(UI_ROOT, 'components/ui')
const UI_QUEUE_LIB_DIR = resolve(UI_ROOT, 'lib/queue')
const UI_QUEUE_COMPONENTS_DIR = resolve(UI_ROOT, 'components/queue')
const UNIT_TEST_DIR_UI = resolve(repoRoot, 'ui/tests/unit')
const TOKEN_FILE = resolve(UI_ROOT, 'styles.css')
const TESTID_REGISTRY = resolve(repoRoot, 'ui/tests/e2e/test-ids.ts')

// ---------------------------------------------------------------------------
// Named sets — the plan's canon, read rather than restated.
// ---------------------------------------------------------------------------

type PillEntry = {
  slug: string
  token: string
  fillAlpha: number
  fillClass: string
  labelClass: string
  iconClass: string
}
type Backdrop = { expr: string; note: string }
type NamedSets = {
  CONTRAST_MIN: number
  CONTRAST_BACKDROPS: Record<string, Backdrop>
  STATUS_PILL_TABLE: Record<string, PillEntry>
  STATUS_CONFIG_FEATURES: string[]
  NEW_TESTIDS: string[]
  PRESERVED_TESTIDS: string[]
}
type MatrixRow = {
  theme: string
  status: string
  backdrop: string
  token: string
  ratio: number
}
type ContrastMatrix = { label: MatrixRow[]; icon: MatrixRow[] }

function readJson<T>(path: string): T {
  return JSON.parse(readFileSync(path, 'utf-8')) as T
}

const SETS = readJson<NamedSets>(resolve(planDir, 'named-sets.json'))
const MATRIX = readJson<ContrastMatrix>(resolve(planDir, 'contrast-matrix.json'))
const PILL_TABLE = SETS.STATUS_PILL_TABLE
const PILL_STATUSES = Object.keys(PILL_TABLE)

/** `CONTRAST_BACKDROPS` keys the neutral card state `default`; the measured
 *  baseline spells the same pairing `card`. Bridge, not a second source. */
const BACKDROP_MATRIX_NAME: Record<string, string> = { default: 'card' }
const matrixBackdropName = (key: string): string => BACKDROP_MATRIX_NAME[key] ?? key

// ---------------------------------------------------------------------------
// Source scanning
// ---------------------------------------------------------------------------

function walk(dir: string): string[] {
  let entries: string[]
  try {
    entries = readdirSync(dir)
  } catch {
    return []
  }
  const out: string[] = []
  for (const entry of entries) {
    const full = resolve(dir, entry)
    if (statSync(full).isDirectory()) {
      out.push(...walk(full))
    } else if (/\.(ts|tsx)$/.test(entry)) {
      out.push(full)
    }
  }
  return out
}

const read = (path: string): string => readFileSync(path, 'utf-8')
const rel = (path: string): string => path.slice(repoRoot.length + 1).replace(/\\/g, '/')

// ---------------------------------------------------------------------------
// Module loaders — dynamic so a missing module fails one AC, not collection.
// ---------------------------------------------------------------------------

const QUEUE_LIB = '../../src/renderer/src/lib/queue'
const PRIMITIVES = '../../src/renderer/src/components/ui'

function loadModule<T>(specifier: string): Promise<T> {
  return import(/* @vite-ignore */ specifier) as Promise<T>
}

const load = {
  format: () => loadModule<typeof FormatModule>(`${QUEUE_LIB}/format`),
  statusTokens: () => loadModule<typeof StatusTokensModule>(`${QUEUE_LIB}/status-tokens`),
  statusConfig: () => loadModule<typeof StatusConfigModule>(`${QUEUE_LIB}/status-config`),
  envelope: () => loadModule<typeof EnvelopeModule>(`${QUEUE_LIB}/envelope`),
  statusBadge: () => loadModule<typeof StatusBadgeModule>(`${PRIMITIVES}/StatusBadge`),
  progressBar: () => loadModule<typeof ProgressBarModule>(`${PRIMITIVES}/ProgressBar`),
  selectionCheckbox: () =>
    loadModule<typeof SelectionCheckboxModule>(`${PRIMITIVES}/SelectionCheckbox`),
  confirmModal: () => loadModule<typeof ConfirmModalModule>(`${PRIMITIVES}/ConfirmModal`),
}

// ---------------------------------------------------------------------------
// Rendering — Testing Library, one tree at a time.
// ---------------------------------------------------------------------------

/**
 * Several specs sweep a table of statuses or values and mount a fresh tree per
 * row. Each row unmounts before the next mounts, so the document-wide `screen`
 * queries below are never ambiguous — and `mount()` still hands back the
 * container, which AC-43.9 needs to prove the dialog escapes it through a portal.
 */
let currentUnmount: (() => void) | null = null

function mount(element: ReactElement): HTMLElement {
  const view = render(element)
  currentUnmount = view.unmount
  return view.container
}

function unmount(): void {
  currentUnmount?.()
  currentUnmount = null
}

/**
 * Shift+click. user-event models a modifier as a key held across the gesture
 * rather than a flag on one event, so the chord is pressed the way a hand
 * presses it: hold Shift, click, release.
 */
async function shiftClick(
  user: ReturnType<typeof userEvent.setup>,
  element: Element,
): Promise<void> {
  await user.keyboard('{Shift>}')
  await user.click(element)
  await user.keyboard('{/Shift}')
}

beforeEach(() => {
  currentUnmount = null
})

afterEach(() => {
  unmount()
  vi.restoreAllMocks()
})

// ---------------------------------------------------------------------------
// Colour maths — WCAG 2.2 SC 1.4.3, browser-style 8-bit compositing.
// ---------------------------------------------------------------------------

type Rgb = [number, number, number]

function parseThemeBlock(css: string, opener: string): Map<string, string> {
  const start = css.indexOf(opener)
  if (start === -1) {
    throw new Error(`theme block ${opener} not found in styles.css`)
  }
  const end = css.indexOf('\n}', start)
  if (end === -1) {
    throw new Error(`theme block ${opener} is unterminated`)
  }
  const body = css.slice(start + opener.length, end)
  const map = new Map<string, string>()
  for (const match of body.matchAll(/(--[\w-]+)\s*:\s*([^;]+);/g)) {
    map.set(match[1], match[2].trim())
  }
  return map
}

function toRgb(map: Map<string, string>, token: string): Rgb {
  const value = map.get(token)
  if (value === undefined) {
    throw new Error(`token ${token} is not defined in this theme block`)
  }
  const match = /^#([0-9a-fA-F]{6})$/.exec(value)
  if (match === null) {
    throw new Error(`token ${token} is not a plain 6-digit hex: ${value}`)
  }
  const int = Number.parseInt(match[1], 16)
  return [(int >> 16) & 0xff, (int >> 8) & 0xff, int & 0xff]
}

/** Source-over composite, rounded to 8-bit channels exactly as a browser paints. */
function over(fg: Rgb, alpha: number, bg: Rgb): Rgb {
  return [0, 1, 2].map((i) => Math.round(fg[i] * alpha + bg[i] * (1 - alpha))) as Rgb
}

function luminance(rgb: Rgb): number {
  const channel = (raw: number): number => {
    const c = raw / 255
    return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4
  }
  return 0.2126 * channel(rgb[0]) + 0.7152 * channel(rgb[1]) + 0.0722 * channel(rgb[2])
}

function ratio(a: Rgb, b: Rgb): number {
  const la = luminance(a)
  const lb = luminance(b)
  const [hi, lo] = la >= lb ? [la, lb] : [lb, la]
  return Math.round(((hi + 0.05) / (lo + 0.05)) * 100) / 100
}

/** Resolve a `CONTRAST_BACKDROPS` expression: `--x`, or `--x @ a over --y`. */
function resolveBackdrop(map: Map<string, string>, expr: string): Rgb {
  const composed = /^(--[\w-]+)\s*@\s*([\d.]+)\s*over\s*(--[\w-]+)$/.exec(expr.trim())
  if (composed !== null) {
    return over(toRgb(map, composed[1]), Number.parseFloat(composed[2]), toRgb(map, composed[3]))
  }
  return toRgb(map, expr.trim())
}

type MatrixOptions = {
  labelToken?: (status: string, entry: PillEntry) => string
  alpha?: (entry: PillEntry) => number
  backdropMap?: (theme: 'dark' | 'light') => Map<string, string>
}

function computeMatrix(
  tokensByTheme: Record<'dark' | 'light', Map<string, string>>,
  table: Record<string, PillEntry>,
  options: MatrixOptions = {},
): { label: MatrixRow[]; icon: MatrixRow[] } {
  const label: MatrixRow[] = []
  const icon: MatrixRow[] = []
  for (const theme of ['dark', 'light'] as const) {
    const hueMap = tokensByTheme[theme]
    const backdropSource = options.backdropMap?.(theme) ?? hueMap
    for (const [status, entry] of Object.entries(table)) {
      for (const [key, backdrop] of Object.entries(SETS.CONTRAST_BACKDROPS)) {
        const base = resolveBackdrop(backdropSource, backdrop.expr)
        const alpha = options.alpha?.(entry) ?? entry.fillAlpha
        const fill = over(toRgb(hueMap, entry.token), alpha, base)
        const labelToken = options.labelToken?.(status, entry) ?? '--color-fg'
        const row = { theme, status, backdrop: matrixBackdropName(key), token: entry.token }
        label.push({ ...row, ratio: ratio(toRgb(hueMap, labelToken), fill) })
        icon.push({ ...row, ratio: ratio(toRgb(hueMap, entry.token), base) })
      }
    }
  }
  return { label, icon }
}

function themeMaps(css: string): Record<'dark' | 'light', Map<string, string>> {
  return {
    dark: parseThemeBlock(css, '@theme {'),
    light: parseThemeBlock(css, ':root:not(.dark) {'),
  }
}

// ===========================================================================

/**
 * The converter ids MEU-45 retires, read from that plan's own named sets so the
 * two documents cannot drift. Only the converter half is retired here; the
 * downloader's `*-btn` ids stay registered until MEU-46 moves them.
 */
const MIGRATION_PLAN_DIR = resolve(
  repoRoot,
  'docs/execution/plans/2026-09-02-p10-queue-card-migration',
)
const MIGRATION_SETS = JSON.parse(read(resolve(MIGRATION_PLAN_DIR, 'named-sets.json'))) as {
  RETIRED_TOOLBAR_CONTROLS: { value: { converter: Record<string, unknown> } }
  RETIRED_TESTIDS: { value: Record<string, string> }
}
const MIGRATED_AWAY = new Set<string>([
  ...Object.keys(MIGRATION_SETS.RETIRED_TOOLBAR_CONTROLS.value.converter),
  ...Object.keys(MIGRATION_SETS.RETIRED_TESTIDS.value).filter((id) => id.startsWith('convert-')),
])

describe('MEU-43 queue primitives', () => {
  it('AC-43.1 formatFileSize is defined exactly once and both queue features import it', async () => {
    const declarations = walk(UI_ROOT).filter((file) =>
      /(function|const)\s+formatFileSize\b/.test(read(file)),
    )
    expect(declarations.map(rel)).toEqual(['ui/src/renderer/src/lib/queue/format.ts'])

    const { formatFileSize } = await load.format()
    expect(formatFileSize(null)).toBe('—')
    expect(formatFileSize(Number.NaN)).toBe('—')
    expect(formatFileSize(999)).toBe('999 B')
    expect(formatFileSize(1_500)).toBe('2 KB')
    expect(formatFileSize(245_000_000)).toBe('245 MB')

    /*
      MEU-45 supersession: the converter's direct importer was
      `ConvertQueueTable.tsx`, which MEU-45 deletes. The capability asserted
      here is unchanged — the converter renders sizes with the ONE shared
      formatter and never a private copy — so it is re-asserted at the
      formatter's new home: the page mounts the shared queue package, and
      that package imports `lib/queue/format`.

      MEU-46 supersession (AC-46.5): the downloader's direct importer was
      `DownloadQueueTable.tsx`, now deleted for the same reason. Its arm is
      re-asserted the same way the converter's was — the page mounts the shared
      queue package, which owns the one import — so BOTH features are now
      checked by the identical rule below.
    */
    const importsFormat = (file: string): boolean =>
      /from\s+'[^']*lib\/queue\/format'/.test(read(file))

    const downloaderFiles = walk(resolve(UI_ROOT, 'features', 'downloader'))
    expect(
      downloaderFiles.some((file) => /from\s+'[^']*components\/queue\//.test(read(file))),
      'downloader must mount the shared queue package',
    ).toBe(true)
    expect(
      downloaderFiles.filter((file) => /(function|const)\s+formatFileSize\b/.test(read(file))),
      'and never keep a private copy of the formatter',
    ).toEqual([])

    const converterFiles = walk(resolve(UI_ROOT, 'features', 'converter'))
    expect(
      converterFiles.some((file) => /from\s+'[^']*components\/queue\//.test(read(file))),
      'converter must mount the shared queue package',
    ).toBe(true)
    expect(
      walk(resolve(UI_ROOT, 'components', 'queue')).filter(importsFormat).length,
      'the shared queue package must import the shared helper',
    ).toBeGreaterThan(0)
    expect(
      converterFiles.filter((file) => /function\s+format(File)?Size/.test(read(file))).map(rel),
      'no converter file may define a rival size formatter',
    ).toEqual([])
  })

  it('AC-43.2 status pill table is a single hex-free statement with no rival status map', async () => {
    const mod = await load.statusTokens()
    expect(mod.STATUS_PILL_TOKENS).toEqual(PILL_TABLE)
    expect(Object.keys(mod.STATUS_PILL_TOKENS)).toEqual(PILL_STATUSES)
    for (const entry of Object.values(mod.STATUS_PILL_TOKENS)) {
      expect(Object.keys(entry).sort()).toEqual(
        ['fillAlpha', 'fillClass', 'iconClass', 'labelClass', 'slug', 'token'],
      )
    }

    const source = read(resolve(UI_QUEUE_LIB_DIR, 'status-tokens.ts'))
    expect(source).not.toMatch(/#[0-9a-fA-F]{3,8}\b/)

    // The only pre-existing status->colour maps are the legacy feature controls
    // modules and the pages they feed, all scheduled for deletion by the MEU-45+
    // page migration. Pin that census so no *new* one appears, and shrink it as
    // each page migrates -- MEU-45 removes both converter entries (AC-45.12)
    // and MEU-46 removes the DownloadQueueTable entry with the table itself
    // (AC-46.5) plus `download-controls.ts`: MOUNT_GATE_SCRIPT clause 6 sweeps
    // every obligated page's feature dir, so the downloader map retires with
    // the page (AC-46.12), and AC-41.5 now pins the AgeRestricted token on the
    // shared status-tokens instead. Transcript and TTS sit outside Phase 10.
    const legacy = walk(UI_ROOT)
      .filter((file) => /\bSTATUS_COLORS\b/.test(read(file)))
      .map(rel)
      .sort()
    // TA-2 (Session 25, class C): MEU-55 moves the transcript page onto the shared
    // StatusBadge, so only its controls module still exports the legacy map.
    expect(legacy).toEqual([
      'ui/src/renderer/src/features/transcript/transcript-controls.ts',
      'ui/src/renderer/src/features/tts/TTSPage.tsx',
      'ui/src/renderer/src/features/tts/tts-controls.ts',
    ])
    const newSurface = [...walk(UI_QUEUE_LIB_DIR), ...walk(UI_PRIMITIVES_DIR), ...walk(UI_QUEUE_COMPONENTS_DIR)]
    for (const file of newSurface) {
      if (rel(file).endsWith('lib/queue/status-tokens.ts')) {
        continue
      }
      expect(read(file), `${rel(file)} must not restate the pill palette`).not.toMatch(
        /['"`](?:bg|text)-(?:status|accent)-[\w-]+(?:\/\d+)?['"`]/,
      )
    }
  })

  it('AC-43.3 every one of the 80 label pairings clears CONTRAST_MIN and matches the baseline', async () => {
    const { STATUS_PILL_TOKENS } = await load.statusTokens()
    const css = read(TOKEN_FILE)
    const maps = themeMaps(css)
    const computed = computeMatrix(maps, STATUS_PILL_TOKENS)

    expect(computed.label).toHaveLength(80)
    for (const row of computed.label) {
      expect(
        row.ratio,
        `${row.theme}/${row.status}/${row.backdrop} label contrast`,
      ).toBeGreaterThanOrEqual(SETS.CONTRAST_MIN)
    }
    expect(computed.label).toEqual(MATRIX.label)
    // Advisory per STATUS_ICON_RULE, but still pinned so a drift is visible.
    expect(computed.icon).toEqual(MATRIX.icon)

    // The oracle must be sensitive, not vacuous — each negative moves the matrix.
    const alphaRaised = computeMatrix(maps, STATUS_PILL_TOKENS, { alpha: () => 0.6 })
    expect(alphaRaised.label).not.toEqual(MATRIX.label)
    const crossTheme = computeMatrix(maps, STATUS_PILL_TOKENS, {
      backdropMap: () => maps.light,
    })
    expect(crossTheme.label).not.toEqual(MATRIX.label)
    const sameTokenLabel = computeMatrix(maps, STATUS_PILL_TOKENS, {
      labelToken: (_status, entry) => entry.token,
    })
    // Cancelled: its hue is the same in both palettes, so the oracle does not move when the
    // other light hues are re-ported (the darker light Paused label clears 4.5 on its own hue).
    const lightCancelled = sameTokenLabel.label.filter(
      (row) => row.theme === 'light' && row.status === 'Cancelled',
    )
    expect(lightCancelled.length).toBe(4)
    expect(Math.min(...lightCancelled.map((row) => row.ratio))).toBeLessThan(SETS.CONTRAST_MIN)
  })

  it('AC-43.4 every pill token exists in both theme blocks and binds to its own classes', async () => {
    const { STATUS_PILL_TOKENS } = await load.statusTokens()
    const maps = themeMaps(read(TOKEN_FILE))

    for (const theme of ['dark', 'light'] as const) {
      expect(maps[theme].has('--color-fg'), `--color-fg missing from ${theme}`).toBe(true)
      for (const entry of Object.values(STATUS_PILL_TOKENS)) {
        expect(maps[theme].has(entry.token), `${entry.token} missing from ${theme}`).toBe(true)
      }
    }

    for (const [status, entry] of Object.entries(STATUS_PILL_TOKENS)) {
      const tail = entry.token.replace(/^--color-/, '')
      expect(entry.fillClass, `${status} fillClass`).toBe(
        `bg-${tail}/${Math.round(entry.fillAlpha * 100)}`,
      )
      expect(entry.iconClass, `${status} iconClass`).toBe(`text-${tail}`)
      expect(entry.labelClass, `${status} labelClass`).toBe('text-fg')
      // Zorivest MEU-389: an accent hue at /20 is the banned washed-out fill.
      expect(entry.fillClass).not.toMatch(/^bg-accent-[\w-]+\/20$/)
    }
  })

  it('AC-43.5 StatusBadge renders a text label on its fill, with an aria-hidden status icon', async () => {
    const { StatusBadge, StatusIcon } = await load.statusBadge()
    const { STATUS_PILL_TOKENS } = await load.statusTokens()

    for (const [status, entry] of Object.entries(STATUS_PILL_TOKENS)) {
      mount(
        createElement('div', null, [
          createElement(StatusBadge, { key: 'badge', status }),
          createElement(StatusIcon, { key: 'icon', status }),
        ]),
      )
      const badge = screen.getByTestId('status-badge')
      expect(badge.textContent?.trim(), `${status} label`).not.toBe('')
      expect(badge.className).toContain(entry.fillClass)
      expect(badge.className).toContain(entry.labelClass)

      const icon = screen.getByTestId('queue-card-status-icon')
      expect(icon.className).toContain(entry.iconClass)
      expect(icon.getAttribute('aria-hidden')).toBe('true')

      unmount()
    }

    mount(createElement(StatusBadge, { status: 'Nonsense' }))
    const fallback = screen.getByTestId('status-badge')
    expect(fallback.textContent).toContain('Nonsense')
  })

  it('AC-43.6 ProgressBar animates transform, never geometry', async () => {
    const { ProgressBar } = await load.progressBar()
    mount(createElement(ProgressBar, { value: 0.42 }))
    const bar = screen.getByTestId('progress-bar')
    const fill = bar.querySelector<HTMLElement>('[data-progress-fill]')
    expect(fill).not.toBeNull()
    expect(fill?.style.transform).toBe('scaleX(0.42)')
    expect(fill?.style.transformOrigin).toBe('left')
    expect(fill?.style.width).toBe('')

    const source = read(resolve(UI_PRIMITIVES_DIR, 'ProgressBar.tsx'))
    expect(source).not.toMatch(/transition-all/)
    expect(source).not.toMatch(/w-\[/)
    expect(source).not.toMatch(/width\s*:/)
    expect(source).toContain('transition-[transform]')
    expect(source).toContain('var(--duration-normal)')
    expect(source).toContain('var(--ease-out)')
  })

  it('AC-43.7 ProgressBar exposes clamped progressbar ARIA', async () => {
    const { ProgressBar } = await load.progressBar()
    const cases: Array<[number, string]> = [
      [0, '0'],
      [0.427, '43'],
      [1, '100'],
      [-0.5, '0'],
      [1.7, '100'],
      [Number.NaN, '0'],
    ]
    for (const [value, expected] of cases) {
      mount(createElement(ProgressBar, { value }))
      const bar = screen.getByTestId('progress-bar')
      expect(bar.getAttribute('role')).toBe('progressbar')
      expect(bar.getAttribute('aria-valuemin')).toBe('0')
      expect(bar.getAttribute('aria-valuemax')).toBe('100')
      expect(bar.getAttribute('aria-valuenow'), `value ${String(value)}`).toBe(expected)
      unmount()
    }
  })

  it('AC-43.8 SelectionCheckbox is indeterminate-capable, tokenised and click-isolated', async () => {
    const { SelectionCheckbox } = await load.selectionCheckbox()
    const user = userEvent.setup()
    const onChange = vi.fn()
    const onWrapperClick = vi.fn()

    mount(
      createElement(
        'div',
        { role: 'button', tabIndex: 0, onClick: onWrapperClick },
        createElement(SelectionCheckbox, {
          checked: false,
          indeterminate: true,
          onChange,
          ariaLabel: 'Select row',
        }),
      ),
    )
    const box = screen.getByTestId('selection-checkbox')
    expect(box).toBeInstanceOf(HTMLInputElement)
    const input = box as HTMLInputElement
    expect(input.indeterminate).toBe(true)
    expect(input.hasAttribute('indeterminate')).toBe(false)

    await user.click(input)
    expect(onChange).toHaveBeenCalledTimes(1)
    // MEU-47 rewrite (AC-47.1a), E2E_REWRITE_RULE: SELECTION_PRIMITIVE_EXTENSION
    // widens onChange to forward modifier state, so the exact-arity form this
    // line used to assert (`toHaveBeenCalledWith(true)`) no longer describes the
    // contract. The capability it pinned - a plain click reports `checked: true`
    // and nothing else changes - is preserved, now including the modifiers the
    // range select needs.
    expect(onChange).toHaveBeenCalledWith(true, { shiftKey: false })
    expect(onWrapperClick).not.toHaveBeenCalled()

    const source = read(resolve(UI_PRIMITIVES_DIR, 'SelectionCheckbox.tsx'))
    expect(source).toContain('var(--color-accent)')
    expect(source).not.toMatch(/#[0-9a-fA-F]{3,8}\b/)

    unmount()

    mount(
      createElement(SelectionCheckbox, {
        checked: true,
        onChange,
        ariaLabel: 'Select all',
        testId: 'queue-select-all',
      }),
    )
    expect(screen.getByTestId('queue-select-all')).toBeInstanceOf(HTMLInputElement)
  })

  it('AC-47.1a SelectionCheckbox and QueueCard forward { shiftKey } and stopPropagation keeps it', async () => {
    // SELECTION_MODEL's Shift+click range select is only reachable if the
    // modifier survives the two hops between the DOM event and the page's
    // selection state. Today it survives neither: SelectionCheckbox.onChange is
    // `(checked) => void` and QueueCard.onSelectChange is `(id, checked) => void`,
    // so the range would work in a test harness and never in the running app.
    const { SelectionCheckbox } = await load.selectionCheckbox()
    const user = userEvent.setup()
    const onChange = vi.fn()
    const onWrapperClick = vi.fn()

    /*
      The box is mounted CONTROLLED, the way a page mounts it: `checked` follows
      what the last change reported. A fixed `checked={false}` would not exercise
      the real thing - React restores a controlled checkbox's DOM state after
      every change event, so a static harness would report `true` twice and never
      show whether the second gesture is read correctly.
    */
    function Harness(): ReactElement {
      const [checked, setChecked] = useState(false)
      return createElement(
        'div',
        { role: 'button', tabIndex: 0, onClick: onWrapperClick },
        createElement(SelectionCheckbox, {
          checked,
          onChange: (next: boolean, modifiers: { shiftKey: boolean }) => {
            onChange(next, modifiers)
            setChecked(next)
          },
          ariaLabel: 'Select row',
        }),
      )
    }

    mount(createElement(Harness))
    const input = screen.getByTestId('selection-checkbox') as HTMLInputElement

    await shiftClick(user, input)
    expect(onChange).toHaveBeenCalledWith(true, { shiftKey: true })
    // The click-isolation from AC-43.8 still holds - and stopping propagation
    // must not be implemented by swallowing the event the modifier rides on.
    expect(onWrapperClick).not.toHaveBeenCalled()

    // A plain click reports the modifier as `false`, never `undefined`: the page
    // reads `modifiers.shiftKey` directly, so an absent object is a range select
    // that silently degrades to a single toggle.
    onChange.mockClear()
    await user.click(input)
    expect(onChange).toHaveBeenCalledWith(false, { shiftKey: false })

    unmount()

    // Hop two: the card must pass the modifiers on with the row id rather than
    // narrowing them away.
    const { QueueCard } = (await import(
      /* @vite-ignore */ '../../src/renderer/src/components/queue/QueueCard'
    )) as typeof QueueCardModule
    const onSelectChange = vi.fn()
    mount(
      createElement(QueueCard, {
        job: { id: 'job-7', position: 1, status: 'Pending', title: 'Seventh job' },
        selectable: true,
        selected: false,
        onSelectChange,
      }),
    )
    const rowBox = screen.getByTestId('selection-checkbox') as HTMLInputElement
    await shiftClick(user, rowBox)
    expect(onSelectChange).toHaveBeenCalledWith('job-7', true, { shiftKey: true })

    // Static backstop: a signature that compiles but drops the modifier would
    // pass a lenient assertion, so both files must name it.
    expect(read(resolve(UI_PRIMITIVES_DIR, 'SelectionCheckbox.tsx'))).toContain('shiftKey')
    expect(read(resolve(UI_QUEUE_COMPONENTS_DIR, 'QueueCard.tsx'))).toContain('shiftKey')
  })

  it('AC-43.9 ConfirmModal is a labelled portal dialog with a verb confirm label', async () => {
    const { ConfirmModal } = await load.confirmModal()
    const host = mount(
      createElement(ConfirmModal, {
        open: true,
        title: 'Remove 3 items?',
        description: 'They leave the queue.',
        confirmLabel: 'Remove',
        onConfirm: () => undefined,
        onCancel: () => undefined,
      }),
    )

    const dialog = screen.getByTestId('confirm-modal')
    expect(host.contains(dialog), 'dialog must render through a portal').toBe(false)
    expect(dialog.getAttribute('role')).toBe('dialog')
    expect(dialog.getAttribute('aria-modal')).toBe('true')
    const labelledBy = dialog.getAttribute('aria-labelledby')
    expect(labelledBy).toBeTruthy()
    expect(document.getElementById(labelledBy ?? '')?.textContent).toContain('Remove 3 items?')

    const confirm = screen.getByTestId('confirm-modal-confirm')
    expect(confirm.textContent?.trim()).toBe('Remove')
    expect(['OK', 'Yes']).not.toContain(confirm.textContent?.trim())
    expect(screen.getByTestId('confirm-modal-cancel')).toBeInstanceOf(HTMLElement)

    const nativeConfirm = ['window', 'confirm'].join('.')
    for (const file of walk(UI_ROOT)) {
      expect(read(file), `${rel(file)} must not use the native confirm`).not.toContain(nativeConfirm)
    }
  })

  it('AC-43.10 ConfirmModal traps focus and routes Escape and backdrop to cancel', async () => {
    const { ConfirmModal } = await load.confirmModal()
    const user = userEvent.setup()
    const onCancel = vi.fn()
    const onConfirm = vi.fn()
    const props = {
      open: true,
      title: 'Remove item?',
      confirmLabel: 'Remove',
      onConfirm,
      onCancel,
    }

    mount(createElement(ConfirmModal, props))
    const cancel = screen.getByTestId('confirm-modal-cancel')
    expect(document.activeElement).toBe(cancel)

    const dialog = screen.getByTestId('confirm-modal')
    await user.tab()
    expect(dialog.contains(document.activeElement), 'focus must stay in the dialog').toBe(true)
    await user.tab()
    expect(dialog.contains(document.activeElement)).toBe(true)

    await user.keyboard('{Escape}')
    expect(onCancel).toHaveBeenCalledTimes(1)

    await user.click(screen.getByTestId('confirm-modal-confirm'))
    expect(onConfirm).toHaveBeenCalledTimes(1)

    const backdrop = document.querySelector<HTMLElement>('[data-confirm-backdrop]')
    expect(backdrop).not.toBeNull()
    if (backdrop !== null) {
      await user.click(backdrop)
    }
    expect(onCancel).toHaveBeenCalledTimes(2)
  })

  it('AC-43.11 the envelope parser rejects bare arrays and unknown wrapper keys via ApiError', async () => {
    const { parseQueueEnvelope } = await load.envelope()

    const parsed = parseQueueEnvelope({ items: [{ id: 'a' }], processor: 'Idle' })
    expect(parsed.items).toHaveLength(1)
    expect(parsed.processor).toBe('Idle')
    expect(parseQueueEnvelope({ items: [] }).processor).toBeUndefined()

    for (const bad of [[], [{ id: 'a' }], { items: [], nope: 1 }, { processor: 'Idle' }]) {
      let caught: unknown = null
      try {
        parseQueueEnvelope(bad)
      } catch (error) {
        caught = error
      }
      expect(caught, `${JSON.stringify(bad)} must be rejected`).toBeInstanceOf(ApiError)
      expect((caught as ApiError).status).toBe(422)
    }

    for (const file of [...walk(UI_QUEUE_LIB_DIR), ...walk(UI_QUEUE_COMPONENTS_DIR)]) {
      expect(read(file), `${rel(file)} must not map a raw fetch result`).not.toMatch(
        /apiFetch<[^>]*>\([^)]*\)[\s\S]{0,60}?\.map\(/,
      )
    }
  })

  it('AC-43.12 each feature status config is keyed by that feature own JOB_STATUSES', async () => {
    const { QUEUE_STATUS_CONFIGS } = await load.statusConfig()
    expect(Object.keys(QUEUE_STATUS_CONFIGS).sort()).toEqual([...SETS.STATUS_CONFIG_FEATURES].sort())

    const controls: Record<string, readonly string[]> = {
      download: DOWNLOAD_STATUSES,
      convert: CONVERT_STATUSES,
      transcript: TRANSCRIPT_STATUSES,
      tts: TTS_STATUSES,
    }
    for (const feature of SETS.STATUS_CONFIG_FEATURES) {
      const config = QUEUE_STATUS_CONFIGS[feature as keyof typeof QUEUE_STATUS_CONFIGS]
      expect(Object.keys(config), `${feature} key set`).toEqual([...controls[feature]])
    }
    expect(Object.keys(QUEUE_STATUS_CONFIGS.convert)).not.toContain('Downloading')

    // Imported, not restated: no status string literal is authored in the config.
    const source = read(resolve(UI_QUEUE_LIB_DIR, 'status-config.ts'))
    for (const status of ['Pending', 'Downloading', 'Generating', 'QualityBlocked']) {
      expect(source, `${status} must be imported, not restated`).not.toMatch(
        new RegExp(`['"\`]${status}['"\`]`),
      )
    }
  })

  it('AC-43.13 standards sweep passes and the testid registry carries the new and preserved ids', () => {
    const newSurface = [...walk(UI_PRIMITIVES_DIR), ...walk(UI_QUEUE_LIB_DIR), ...walk(UI_QUEUE_COMPONENTS_DIR)]
    expect(newSurface.length).toBeGreaterThan(0)

    for (const file of newSurface) {
      const source = read(file)
      for (const line of source.split('\n')) {
        if (!/#[0-9a-fA-F]{3,8}\b/.test(line)) {
          continue
        }
        // G30 exception: native <option> styling cannot read CSS custom
        // properties in Electron, so SelectInput keeps inline hex — but never
        // inside a className / Tailwind arbitrary value.
        expect(line, `${rel(file)} raw hex in a class string`).not.toMatch(/className|-\[/)
      }
      expect(source, `${rel(file)} transition-all`).not.toMatch(/transition-all/)
      expect(source, `${rel(file)} arbitrary duration`).not.toMatch(/duration-\[(?!var\(--duration-)/)
      expect(source, `${rel(file)} deferral marker`).not.toMatch(/TODO|FIXME|NotImplementedError/)
    }

    const button = read(resolve(UI_PRIMITIVES_DIR, 'Button.tsx'))
    const variants = /const variantClasses: Record<ButtonVariant, string> = \{([\s\S]*?)\n\}/.exec(button)
    const sizes = /const sizeClasses: Record<ButtonSize, string> = \{([\s\S]*?)\n\}/.exec(button)
    expect(variants).not.toBeNull()
    expect(sizes).not.toBeNull()
    const keysOf = (block: string): string[] =>
      Array.from(block.matchAll(/^\s{2}([a-zA-Z]+):/gm)).map((m) => m[1])
    expect(keysOf(variants?.[1] ?? '')).toEqual([
      'primary',
      'secondary',
      'outline',
      'ghost',
      'destructive',
    ])
    expect(keysOf(sizes?.[1] ?? '')).toEqual(['sm', 'md', 'lg'])

    const guards = [
      ['test', 'skip'].join('.'),
      ['it', 'skip'].join('.'),
      ['describe', 'skip'].join('.'),
      ['test', 'only'].join('.'),
      ['it', 'only'].join('.'),
      ['describe', 'only'].join('.'),
      ['test', 'todo'].join('.'),
      ['it', 'todo'].join('.'),
    ]
    for (const file of walk(UNIT_TEST_DIR_UI)) {
      const source = read(file)
      for (const guard of guards) {
        expect(source, `${rel(file)} contains ${guard}`).not.toContain(guard)
      }
    }

    const registry = read(TESTID_REGISTRY)
    for (const id of SETS.NEW_TESTIDS) {
      expect(registry, `NEW_TESTIDS ${id} missing from the registry`).toContain(`'${id}'`)
    }
    // MEU-45 supersession: this list was written before the migration named its
    // new homes, so the converter ids it carries are now retired with declared
    // replacements (RETIRED_TOOLBAR_CONTROLS.converter + RETIRED_TESTIDS). A
    // retired id must be GONE from the registry - keeping dead ids is the stale
    // canon the migration removes - while every id whose page has not migrated
    // yet is still pinned exactly as before.
    for (const id of SETS.PRESERVED_TESTIDS) {
      if (MIGRATED_AWAY.has(id)) {
        expect(registry, `retired ${id} still registered`).not.toContain(`'${id}'`)
        continue
      }
      expect(registry, `PRESERVED_TESTIDS ${id} dropped from the registry`).toContain(`'${id}'`)
    }
  })
})

// ---------------------------------------------------------------------------
// MEU-49 — QueueList drag wiring (DND_OPT_IN_RULE, MOVE_TO_INDEX_CONTRACT,
// DRAG_STATE_ISOLATION_RULE, G33_RULE).
//
// dnd-kit is replaced by capturing stand-ins for these specs. That is not a
// convenience: jsdom returns an all-zero getBoundingClientRect, so no real
// drag can complete here (`JSDOM_RECT_RULE`), and what a unit test CAN prove is
// that QueueList hands dnd-kit the right inputs and reacts correctly to the
// callbacks dnd-kit invokes. The completed drag is proved once, in Playwright.
// ---------------------------------------------------------------------------

const dndPlanDir = resolve(repoRoot, 'docs/execution/plans/2026-09-03-p10-queue-card-dnd')
const DND_HANDLE_TESTID = readJson<{ DND_TESTIDS: { value: string[] } }>(
  resolve(dndPlanDir, 'named-sets.json'),
).DND_TESTIDS.value[0]

type DragCallbackArgs = { active: { id: string }; over?: { id: string } | null }
type DndContextProps = {
  announcements?: unknown
  screenReaderInstructions?: unknown
  sensors?: unknown
  collisionDetection?: unknown
  onDragStart?: (args: DragCallbackArgs) => void
  onDragOver?: (args: DragCallbackArgs) => void
  onDragEnd?: (args: DragCallbackArgs) => void
  onDragCancel?: (args: DragCallbackArgs) => void
}

const dnd = vi.hoisted(() => ({
  /** Props the component under test passed to `DndContext`, or null if none. */
  context: null as Record<string, unknown> | null,
  /** The `items` array `SortableContext` received, or null if never rendered. */
  sortableItems: null as unknown[] | null,
  /** Strategy prop, so the vertical list preset can be asserted. */
  sortableStrategy: null as unknown,
  /** Per-row `useSortable` return values the stand-in should hand back. */
  transformById: {} as Record<string, { x: number; y: number } | null>,
  transitionById: {} as Record<string, string | undefined>,
  draggingId: null as string | null,
  /** Every id `useSortable` was called with, in render order. */
  sortableCalls: [] as string[],
}))

vi.mock('@dnd-kit/core', async () => {
  const react = await import('react')
  return {
    DndContext: (props: Record<string, unknown>) => {
      dnd.context = props
      return react.createElement(react.Fragment, null, props.children as never)
    },
    DragOverlay: (props: Record<string, unknown>) =>
      react.createElement(react.Fragment, null, props.children as never),
    PointerSensor: function PointerSensor() {},
    KeyboardSensor: function KeyboardSensor() {},
    useSensor: (sensor: unknown, options?: unknown) => ({ sensor, options }),
    useSensors: (...sensors: unknown[]) => sensors,
    closestCenter: function closestCenter() {
      return []
    },
    closestCorners: function closestCorners() {
      return []
    },
  }
})

vi.mock('@dnd-kit/sortable', async () => {
  const react = await import('react')
  return {
    SortableContext: (props: Record<string, unknown>) => {
      dnd.sortableItems = props.items as unknown[]
      dnd.sortableStrategy = props.strategy
      return react.createElement(react.Fragment, null, props.children as never)
    },
    verticalListSortingStrategy: 'verticalListSortingStrategy',
    sortableKeyboardCoordinates: function sortableKeyboardCoordinates() {
      return undefined
    },
    arrayMove: <T,>(list: readonly T[], from: number, to: number): T[] => {
      const next = [...list]
      const [row] = next.splice(from, 1)
      next.splice(to, 0, row)
      return next
    },
    useSortable: (args: { id: string }) => {
      dnd.sortableCalls.push(args.id)
      return {
        attributes: { 'aria-roledescription': 'sortable' },
        listeners: { onPointerDown: () => undefined },
        setNodeRef: () => undefined,
        setActivatorNodeRef: () => undefined,
        transform: dnd.transformById[args.id] ?? null,
        transition: dnd.transitionById[args.id],
        isDragging: dnd.draggingId === args.id,
      }
    },
  }
})

const QUEUE_COMPONENTS_SPECIFIER = '../../src/renderer/src/components/queue'
const loadList = (): Promise<typeof QueueListModule> =>
  loadModule<typeof QueueListModule>(`${QUEUE_COMPONENTS_SPECIFIER}/QueueList`)

/** The list's own props are the same in every drag spec; only the wiring differs. */
function listJobs(ids: readonly string[]): { id: string; position: number; status: string; title: string }[] {
  return ids.map((id, index) => ({
    id,
    position: index + 1,
    status: 'Pending',
    title: `Job ${id.toUpperCase()}`,
  }))
}

/**
 * jsdom has no DragEvent carrying a DataTransfer, so the payload the drop zone
 * reads is attached to a plain Event. This is the FILE drag — the other event
 * family entirely from the pointer events dnd-kit uses, which is exactly what
 * DRAG_STATE_ISOLATION_RULE is about.
 */
function fireFileDrag(el: Element, type: string): void {
  const event = new Event(type, { bubbles: true, cancelable: true })
  Object.defineProperty(event, 'dataTransfer', {
    value: {
      items: [{ kind: 'file', type: 'video/mp4' }],
      files: [],
      types: ['Files'],
      dropEffect: 'copy',
      effectAllowed: 'copy',
    },
  })
  act(() => {
    el.dispatchEvent(event)
  })
}

function resetDnd(): void {
  dnd.context = null
  dnd.sortableItems = null
  dnd.sortableStrategy = null
  dnd.transformById = {}
  dnd.transitionById = {}
  dnd.draggingId = null
  dnd.sortableCalls = []
}

describe('MEU-49 QueueList drag wiring', () => {
  beforeEach(() => {
    resetDnd()
  })

  it('AC-49.14 without onMoveToIndex there is no DndContext, no SortableContext, no handle and no live region', async () => {
    const { QueueList } = await loadList()

    const host = mount(
      createElement(QueueList, {
        items: listJobs(['a', 'b', 'c']),
        onOpen: () => undefined,
      }),
    )

    // Drag is opt-in: the transcript and TTS queues mount this same component
    // and must keep the DOM they have today. Byte-identity to the pre-MEU
    // output is carried by the MEU-44/45 QueueList specs, which are untouched
    // and must stay green; what this asserts is that nothing was ADDED.
    expect(dnd.context, 'no DndContext is constructed').toBeNull()
    expect(dnd.sortableItems, 'no SortableContext is constructed').toBeNull()
    expect(dnd.sortableCalls, 'no row calls useSortable').toEqual([])
    expect(within(host).queryAllByTestId(DND_HANDLE_TESTID)).toEqual([])
    expect(host.querySelector('[id^="DndLiveRegion"]'), 'no live region').toBeNull()
    expect(host.querySelector('[aria-roledescription="sortable"]')).toBeNull()
  })

  it('AC-49.15 SortableContext receives the item ids in render order and follows a queue update', async () => {
    const { QueueList } = await loadList()
    const onMoveToIndex = vi.fn()

    const view = render(
      createElement(QueueList, {
        items: listJobs(['a', 'b', 'c']),
        onOpen: () => undefined,
        onMoveToIndex,
        queueKey: 'download',
      }),
    )
    currentUnmount = view.unmount

    expect(dnd.sortableItems).toEqual(['a', 'b', 'c'])
    expect(dnd.sortableStrategy).toBe('verticalListSortingStrategy')
    expect(dnd.sortableCalls).toEqual(['a', 'b', 'c'])

    // A queue poll lands: the id list must follow it, or the next drop resolves
    // its target against an order that is no longer on screen.
    dnd.sortableCalls = []
    view.rerender(
      createElement(QueueList, {
        items: listJobs(['c', 'a', 'd']),
        onOpen: () => undefined,
        onMoveToIndex,
        queueKey: 'download',
      }),
    )

    expect(dnd.sortableItems).toEqual(['c', 'a', 'd'])
    expect(dnd.sortableCalls).toEqual(['c', 'a', 'd'])
  })

  it('AC-49.18 a drop on another row calls onMoveToIndex once with arrayMove index semantics', async () => {
    const { QueueList } = await loadList()
    const onMoveToIndex = vi.fn()

    mount(
      createElement(QueueList, {
        items: listJobs(['a', 'b', 'c', 'd']),
        onOpen: () => undefined,
        onMoveToIndex,
        queueKey: 'download',
      }),
    )
    const context = dnd.context as DndContextProps | null
    expect(context, 'the DndContext exists when drag is enabled').not.toBeNull()

    // A dropped over C, whose index in the PRE-MOVE array is 2. That index is
    // the FINAL position, not a post-removal one (MOVE_TO_INDEX_CONTRACT).
    act(() => {
      context?.onDragEnd?.({ active: { id: 'a' }, over: { id: 'c' } })
    })

    expect(onMoveToIndex).toHaveBeenCalledTimes(1)
    expect(onMoveToIndex).toHaveBeenCalledWith('a', 2)
  })

  it('AC-49.18 a self-drop and a cancelled drag call onMoveToIndex zero times', async () => {
    const { QueueList } = await loadList()
    const onMoveToIndex = vi.fn()

    mount(
      createElement(QueueList, {
        items: listJobs(['a', 'b', 'c', 'd']),
        onOpen: () => undefined,
        onMoveToIndex,
        queueKey: 'download',
      }),
    )
    const context = dnd.context as DndContextProps | null

    act(() => {
      context?.onDragEnd?.({ active: { id: 'b' }, over: { id: 'b' } })
    })
    act(() => {
      context?.onDragEnd?.({ active: { id: 'b' }, over: null })
    })
    act(() => {
      context?.onDragCancel?.({ active: { id: 'b' } })
    })

    // An identity permutation on the wire is a PUT that can only lose a race.
    expect(onMoveToIndex).not.toHaveBeenCalled()
  })

  it('AC-49.19 a row drag leaves the file-drop state alone, and a file drag still works', async () => {
    const { QueueList } = await loadList()
    const onMoveToIndex = vi.fn()

    const host = mount(
      createElement(QueueList, {
        items: listJobs(['a', 'b', 'c']),
        onOpen: () => undefined,
        onMoveToIndex,
        queueKey: 'download',
        accept: () => true,
        onDropFiles: () => undefined,
      }),
    )
    const list = within(host).getByTestId('queue-list')
    const context = dnd.context as DndContextProps | null
    // Without this the whole case passes vacuously on a list that cannot drag
    // at all: every `context?.` call below is a no-op, and an idle drag state
    // with no overlay is exactly what an un-dragged list already reports.
    expect(context, 'the list drives a row drag in the first place').not.toBeNull()

    act(() => {
      context?.onDragStart?.({ active: { id: 'b' } })
    })
    dnd.draggingId = 'b'

    // dnd-kit is pointer events; the drop zone is native HTML5 drag events.
    // Merging DndContext INTO the drop-zone container is what breaks this.
    expect(list.getAttribute('data-drag-state')).toBe('idle')
    expect(within(host).queryByTestId('queue-drop-overlay')).toBeNull()

    act(() => {
      context?.onDragEnd?.({ active: { id: 'b' }, over: { id: 'c' } })
    })

    // The other direction: a file drag still lights the list up as before.
    fireFileDrag(list, 'dragenter')
    expect(list.getAttribute('data-drag-state')).not.toBe('idle')
    expect(within(host).queryByTestId('queue-drop-overlay')).not.toBeNull()
  })

  it('AC-49.20 row displacement is transform/transition only, never top/left/margin', async () => {
    const { QueueList } = await loadList()
    const { CSS: DndCss } = await import('@dnd-kit/utilities')
    const transform = { x: 0, y: 48, scaleX: 1, scaleY: 1 }
    dnd.transformById = { b: transform }
    dnd.transitionById = { b: 'transform 200ms ease' }
    dnd.draggingId = 'b'

    const host = mount(
      createElement(QueueList, {
        items: listJobs(['a', 'b', 'c']),
        onOpen: () => undefined,
        onMoveToIndex: () => undefined,
        queueKey: 'download',
      }),
    )
    const moved = within(host)
      .getAllByTestId('queue-card')
      .find((card) => card.dataset.jobId === 'b')
    expect(moved, 'the moved row is rendered').toBeDefined()

    // setNodeRef goes on the sortable row wrapper, so that element carries the
    // displacement; the card itself keeps its own untouched class list.
    const row = moved?.parentElement as HTMLElement
    const style = row.getAttribute('style') ?? ''

    // The exact string dnd-kit's own helper produces — a hand-rolled
    // `translate3d` that drifts from it is a silent visual regression.
    expect(style).toContain(DndCss.Transform.toString(transform) ?? '')
    expect(style).toContain('transition: transform 200ms ease')

    // G33_RULE — geometry is never the animated property.
    for (const forbidden of ['top:', 'left:', 'margin', 'width:', 'height:', 'box-shadow']) {
      expect(style, `${forbidden} must not carry the displacement`).not.toContain(forbidden)
    }
  })
})
