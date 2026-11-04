/** @vitest-environment jsdom */

/**
 * MEU-44 — queue card, menu, list and empty drop zone (AC-44.1 … AC-44.16).
 *
 * Red-phase contract for `UI_QUEUE_COMPONENTS_DIR` (`QueueCard`, `QueueCardMenu`,
 * `QueueList`, `EmptyDropZone`). Every module is loaded with a dynamic `import()`
 * inside the test that needs it, so a missing module fails exactly one AC instead
 * of collapsing collection (RED_ORACLE requires one failed title per AC id).
 *
 * The plan's Files Modified row names `queue-card.test.tsx`; `ui/vitest.config.ts`
 * collects only `tests/unit/**\/*.test.ts`, so this file is `.test.ts` and builds
 * elements with `createElement`, exactly as `queue-primitives.test.ts` does.
 *
 * No copy, class or hue is authored here: every expected string comes from
 * `named-sets.json` (`CARD_STATE_CLASSES`, `KEBAB_*`, `CANCEL_*`,
 * `BLOCKER_REMEDIATION`, `QUEUE_CARD_ZONE_ORDER`, `DRAG_STATES`).
 */

import { readFileSync, readdirSync, statSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { act, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement, type ReactElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { formatFileSize } from '../../src/renderer/src/lib/queue/format'

// Type-only imports are erased before the module is executed, so they give the
// Red phase full typing against modules that do not exist yet without making
// Vite resolve them at transform time.
import type * as QueueCardModule from '../../src/renderer/src/components/queue/QueueCard'
import type * as QueueCardMenuModule from '../../src/renderer/src/components/queue/QueueCardMenu'
import type * as QueueListModule from '../../src/renderer/src/components/queue/QueueList'
import type * as EmptyDropZoneModule from '../../src/renderer/src/components/queue/EmptyDropZone'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')
const planDir = resolve(repoRoot, 'docs/execution/plans/2026-08-28-p10-queue-card-foundations')

const UI_ROOT = resolve(repoRoot, 'ui/src/renderer/src')
const UI_QUEUE_COMPONENTS_DIR = resolve(UI_ROOT, 'components/queue')
const FEATURES_DIR = resolve(UI_ROOT, 'features')
const E2E_DIR = resolve(repoRoot, 'ui/tests/e2e')
const TESTID_REGISTRY = resolve(repoRoot, 'ui/tests/e2e/test-ids.ts')
const UI_PACKAGE_JSON = resolve(repoRoot, 'ui/package.json')

// ---------------------------------------------------------------------------
// Named sets — the plan's canon, read rather than restated.
// ---------------------------------------------------------------------------

type CopyLocationLabels = { withOutputPath: string; withoutOutputPath: string }
type NamedSets = {
  QUEUE_CARD_ZONE_ORDER: string[]
  CARD_STATE_CLASSES: Record<string, string>
  CARD_STATE_PRECEDENCE: string[]
  FORBIDDEN_SELECTION_FILL: string
  SELECTION_FILL_ALLOWED: string[]
  PRIMARY_ACTION_MAX_PER_CARD: number
  KEBAB_MENU_ORDER: string[]
  KEBAB_ACTION_LABELS: Record<string, string | CopyLocationLabels>
  CARD_INTERACTIVE_ZONES: string[]
  DRAG_STATES: string[]
  BLOCKER_STATUSES: string[]
  BLOCKER_REMEDIATION: Record<string, string>
  CANCEL_CONTROL_LABEL: string
  CANCEL_CONTROL_TITLE: string
  CANCEL_LABEL_FORBIDDEN: string[]
  REQUEUEABLE_DOWNLOAD_STATUSES: string[]
  NEW_TESTIDS: string[]
  PRESERVED_TESTIDS: string[]
  E2E_BASELINE_COUNT: number
}

function readJson<T>(path: string): T {
  return JSON.parse(readFileSync(path, 'utf-8')) as T
}

const SETS = readJson<NamedSets>(resolve(planDir, 'named-sets.json'))
const LABELS = SETS.KEBAB_ACTION_LABELS
const COPY_LABELS = LABELS['copy-location'] as CopyLocationLabels

/** `QUEUE_CARD_ZONE_ORDER` names zones; `NEW_TESTIDS` names the nodes. */
const ZONE_TESTID: Record<string, string> = {
  checkbox: 'selection-checkbox',
  position: 'queue-card-position',
  'status-icon': 'queue-card-status-icon',
  'title-meta': 'queue-card-title',
  progress: 'progress-bar',
  'status-pill': 'status-badge',
  'primary-action': 'queue-card-primary-action',
  kebab: 'queue-card-kebab',
}

const read = (path: string): string => readFileSync(path, 'utf-8')

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

// ---------------------------------------------------------------------------
// Module loaders — dynamic so a missing module fails one AC, not collection.
// ---------------------------------------------------------------------------

const QUEUE_COMPONENTS = '../../src/renderer/src/components/queue'

function loadModule<T>(specifier: string): Promise<T> {
  return import(/* @vite-ignore */ specifier) as Promise<T>
}

const load = {
  card: () => loadModule<typeof QueueCardModule>(`${QUEUE_COMPONENTS}/QueueCard`),
  menu: () => loadModule<typeof QueueCardMenuModule>(`${QUEUE_COMPONENTS}/QueueCardMenu`),
  list: () => loadModule<typeof QueueListModule>(`${QUEUE_COMPONENTS}/QueueList`),
  emptyZone: () => loadModule<typeof EmptyDropZoneModule>(`${QUEUE_COMPONENTS}/EmptyDropZone`),
}

// ---------------------------------------------------------------------------
// Rendering — Testing Library.
// ---------------------------------------------------------------------------

/**
 * Several specs mount two or three cards side by side to compare them, so a
 * lookup is scoped with `within(host)` against the container `mount()` returns;
 * `screen` is reserved for the genuinely document-wide questions (is a dialog
 * open anywhere? did the menu popup mount?). `unmount()` tears down the most
 * recent tree, which is what the sweeps use between rows; Testing Library's
 * automatic cleanup takes the rest at the end of each test.
 */
let user: ReturnType<typeof userEvent.setup>
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

beforeEach(() => {
  user = userEvent.setup()
  currentUnmount = null
})

afterEach(() => {
  unmount()
  vi.restoreAllMocks()
})

function countTestId(scope: HTMLElement, id: string): number {
  return within(scope).queryAllByTestId(id).length
}

function openRegion(card: HTMLElement): HTMLElement {
  const region = card.querySelector<HTMLElement>('[role="button"]')
  if (region === null) {
    throw new Error('card has no role="button" open-region')
  }
  return region
}

/** Document-order sequence of the zone testids actually rendered in the card. */
function renderedZoneIds(card: HTMLElement): string[] {
  const wanted = new Set(Object.values(ZONE_TESTID))
  return Array.from(card.querySelectorAll<HTMLElement>('[data-testid]'))
    .map((el) => el.dataset.testid ?? '')
    .filter((id) => wanted.has(id))
}

// ---------------------------------------------------------------------------
// Drag events — jsdom has no DragEvent constructor with a DataTransfer, so the
// payload a component reads (`nativeEvent.dataTransfer`) is attached directly.
// ---------------------------------------------------------------------------

type DragItemLike = { kind: string; type: string }

function fireDrag(
  el: Element,
  type: string,
  init: { items?: DragItemLike[]; files?: File[] } = {},
): void {
  const event = new Event(type, { bubbles: true, cancelable: true })
  Object.defineProperty(event, 'dataTransfer', {
    value: {
      items: init.items ?? [],
      files: init.files ?? [],
      types: ['Files'],
      dropEffect: 'copy',
      effectAllowed: 'copy',
    },
  })
  act(() => {
    el.dispatchEvent(event)
  })
}

const MEDIA_ITEM: DragItemLike = { kind: 'file', type: 'video/mp4' }
const TEXT_ITEM: DragItemLike = { kind: 'file', type: 'text/plain' }
const acceptsMedia = (items: readonly DragItemLike[]): boolean =>
  items.length > 0 && items.every((item) => item.type.startsWith('video/'))

// ---------------------------------------------------------------------------
// Job fixtures
// ---------------------------------------------------------------------------

type Job = {
  id: string
  position: number
  status: string
  title: string
  progress?: number | null
  fileSize?: number | null
  errorMessage?: string | null
  outputPath?: string | null
  sourceUrl?: string | null
}

function job(overrides: Partial<Job> = {}): Job {
  return {
    id: 'job-1',
    position: 1,
    status: 'Pending',
    title: 'Example video',
    sourceUrl: 'https://youtu.be/dQw4w9wgGc',
    ...overrides,
  }
}

const noop = (): void => undefined

/** Every kebab callback supplied, so only KEBAB_AVAILABILITY can omit an item. */
function allMenuHandlers(): Record<string, ReturnType<typeof vi.fn>> {
  return {
    onOpenFile: vi.fn(),
    onOpenFolder: vi.fn(),
    onCopyLocation: vi.fn(),
    onMoveUp: vi.fn(),
    onMoveDown: vi.fn(),
    onMoveTop: vi.fn(),
    onMoveBottom: vi.fn(),
    onRemove: vi.fn(),
  }
}

function menuItems(host: HTMLElement): HTMLElement[] {
  return within(within(host).getByTestId('queue-card-menu')).queryAllByRole('menuitem')
}

function menuLabels(host: HTMLElement): string[] {
  return menuItems(host).map((item) => (item.textContent ?? '').trim())
}

/**
 * The ids MEU-45 retires, and the homes their capability moved to.
 *
 * Read from the migration plan's own named sets so the two projects cannot
 * drift: `RETIRED_TOOLBAR_CONTROLS` maps each retired control id to its new
 * home, and `RETIRED_TESTIDS` does the same for the hand-rolled confirm ids.
 */
type RetiredHome = { home: string; meu: string }
const migrationSets = readJson<{
  RETIRED_TOOLBAR_CONTROLS: { value: { converter: Record<string, RetiredHome[]> } }
  RETIRED_TESTIDS: { value: Record<string, string> }
}>(
  resolve(repoRoot, 'docs/execution/plans/2026-09-02-p10-queue-card-migration/named-sets.json'),
)

const MIGRATED_AWAY = new Set<string>([
  ...Object.keys(migrationSets.RETIRED_TOOLBAR_CONTROLS.value.converter),
  ...Object.keys(migrationSets.RETIRED_TESTIDS.value).filter((id) => id.startsWith('convert-')),
])

// A home is only assertable against the registry when it *is* a testid; the
// prose entries ("Alt+ArrowUp on a focused card") are covered by the mount gate.
const MIGRATED_HOMES = new Set<string>(
  [
    ...Object.values(migrationSets.RETIRED_TOOLBAR_CONTROLS.value.converter)
      .flat()
      .map((entry) => entry.home),
    ...Object.values(migrationSets.RETIRED_TESTIDS.value),
  ].filter((home) => /^[a-z0-9-]+$/.test(home)),
)

describe('MEU-44 queue card, menu, list and empty drop zone', () => {
  it('AC-44.1 the card renders QUEUE_CARD_ZONE_ORDER in document order with no placeholder zones', async () => {
    const { QueueCard } = await load.card()
    const handlers = allMenuHandlers()
    const host = mount(
      createElement(QueueCard, {
        job: job({ status: 'Downloading', progress: 0.4, outputPath: 'C:/out/a.mp4' }),
        isInFlight: true,
        selectable: true,
        onSelectChange: noop,
        onOpen: noop,
        onCancelQueue: noop,
        ...handlers,
      }),
    )
    const card = within(host).getByTestId('queue-card')
    const expected = SETS.QUEUE_CARD_ZONE_ORDER.map((zone) => ZONE_TESTID[zone])
    expect(renderedZoneIds(card)).toEqual(expected)

    unmount()

    // A bare Pending card: the optional zones are absent, not empty stand-ins.
    const bare = mount(
      createElement(QueueCard, { job: job({ status: 'Pending' }), onOpen: noop }),
    )
    const bareCard = within(bare).getByTestId('queue-card')
    expect(countTestId(bareCard, 'selection-checkbox')).toBe(0)
    expect(countTestId(bareCard, 'progress-bar')).toBe(0)
    expect(countTestId(bareCard, 'queue-card-primary-action')).toBe(0)
    expect(countTestId(bareCard, 'queue-card-kebab')).toBe(0)
    expect(renderedZoneIds(bareCard)).toEqual([
      ZONE_TESTID.position,
      ZONE_TESTID['status-icon'],
      ZONE_TESTID['title-meta'],
      ZONE_TESTID['status-pill'],
    ])
  })

  it('AC-44.2 the card body is a keyboard-activated button that does not contain the checkbox', async () => {
    const { QueueCard } = await load.card()
    const onOpen = vi.fn()
    const host = mount(
      createElement(QueueCard, {
        job: job(),
        onOpen,
        selectable: true,
        onSelectChange: noop,
      }),
    )
    const card = within(host).getByTestId('queue-card')
    const region = openRegion(card)
    expect(region.getAttribute('role')).toBe('button')
    expect(region.tabIndex).toBe(0)

    region.focus()
    await user.keyboard('{Enter}')
    expect(onOpen).toHaveBeenCalledTimes(1)
    expect(onOpen).toHaveBeenCalledWith('job-1')

    region.focus()
    await user.keyboard(' ')
    expect(onOpen).toHaveBeenCalledTimes(2)

    // Space must activate, never scroll the list underneath.
    const space = new KeyboardEvent('keydown', { key: ' ', bubbles: true, cancelable: true })
    act(() => {
      region.dispatchEvent(space)
    })
    expect(space.defaultPrevented).toBe(true)

    const checkbox = within(card).getByTestId('selection-checkbox')
    expect(region.contains(checkbox)).toBe(false)
  })

  it('AC-44.3 card state classes follow CARD_STATE_PRECEDENCE and never use the forbidden fill', async () => {
    const { QueueCard } = await load.card()
    const classesFor = (props: Record<string, unknown>): string => {
      const host = mount(createElement(QueueCard, { job: job(), onOpen: noop, ...props }))
      const className = within(host).getByTestId('queue-card').className
      unmount()
      return className
    }

    const detailOpen = classesFor({ detailOpen: true, selected: true })
    for (const cls of SETS.CARD_STATE_CLASSES['detail-open'].split(' ')) {
      expect(detailOpen, 'detail-open wins over checkbox-selected').toContain(cls)
    }

    const selected = classesFor({ selected: true })
    for (const cls of SETS.CARD_STATE_CLASSES['checkbox-selected'].split(' ')) {
      expect(selected).toContain(cls)
    }

    const plain = classesFor({})
    for (const cls of SETS.CARD_STATE_CLASSES.default.split(' ')) {
      expect(plain).toContain(cls)
    }

    for (const className of [detailOpen, selected, plain]) {
      expect(className).not.toContain(SETS.FORBIDDEN_SELECTION_FILL)
    }
    const source = read(resolve(UI_QUEUE_COMPONENTS_DIR, 'QueueCard.tsx'))
    expect(source).not.toContain(SETS.FORBIDDEN_SELECTION_FILL)
  })

  it('AC-44.4 exactly one primary action is chosen by state and every control is named', async () => {
    const { QueueCard } = await load.card()
    const requeueableStatuses = SETS.REQUEUEABLE_DOWNLOAD_STATUSES
    const cases: Array<{
      props: Partial<QueueCardModule.QueueCardProps> & { job: Job }
      label: string | null
    }> = [
      { props: { job: job({ status: 'Failed' }), onRetry: noop }, label: 'Retry' },
      {
        props: { job: job({ status: 'Done', outputPath: 'C:/out/a.mp4' }), onOpenFile: noop },
        label: 'Open file',
      },
      {
        props: {
          job: job({ status: 'Downloading', progress: 0.2 }),
          isInFlight: true,
          onCancelQueue: noop,
        },
        label: SETS.CANCEL_CONTROL_LABEL,
      },
      { props: { job: job({ status: 'Pending' }) }, label: null },
      { props: { job: job({ status: 'Skipped' }), onRetry: noop }, label: null },
    ]

    for (const testCase of cases) {
      const host = mount(
        createElement(QueueCard, { onOpen: noop, requeueableStatuses, ...testCase.props }),
      )
      const card = within(host).getByTestId('queue-card')
      const controls = card.querySelectorAll<HTMLElement>(
        '[data-testid="queue-card-primary-action"]',
      )
      expect(controls.length).toBeLessThanOrEqual(SETS.PRIMARY_ACTION_MAX_PER_CARD)
      if (testCase.label === null) {
        expect(controls.length).toBe(0)
      } else {
        expect(controls.length).toBe(1)
        const control = controls[0]
        expect((control.textContent ?? '').trim()).toBe(testCase.label)
        expect(control.getAttribute('title')).toBeTruthy()
      }
      unmount()
    }
  })

  it('AC-44.5 the per-card cancel is in-flight-only and calls the queue-level callback', async () => {
    const { QueueCard } = await load.card()
    const onCancelQueue = vi.fn()

    const idle = mount(
      createElement(QueueCard, {
        job: job({ status: 'Pending' }),
        onOpen: noop,
        onCancelQueue,
      }),
    )
    expect(countTestId(within(idle).getByTestId('queue-card'), 'queue-card-primary-action')).toBe(0)
    unmount()

    const host = mount(
      createElement(QueueCard, {
        job: job({ status: 'Downloading', progress: 0.6 }),
        isInFlight: true,
        onOpen: noop,
        onCancelQueue,
      }),
    )
    const control = within(host).getByTestId('queue-card-primary-action')
    await user.click(control)
    expect(onCancelQueue).toHaveBeenCalledTimes(1)
    expect(onCancelQueue).toHaveBeenCalledWith()

    // No per-item cancel prop or path exists anywhere in the component.
    const source = read(resolve(UI_QUEUE_COMPONENTS_DIR, 'QueueCard.tsx'))
    const cancelProps = Array.from(source.matchAll(/on[A-Za-z]*Cancel[A-Za-z]*/g)).map(
      (match) => match[0],
    )
    expect(new Set(cancelProps)).toEqual(new Set(['onCancelQueue']))
    expect(source).not.toMatch(/cancelItem|cancel-item|cancelJob/)
  })

  it('AC-44.6 the meta zone is state-dependent and the progress bar is in-flight-only', async () => {
    const { QueueCard } = await load.card()
    const render = (overrides: Partial<Job>, props: Record<string, unknown> = {}): HTMLElement => {
      const host = mount(createElement(QueueCard, { job: job(overrides), onOpen: noop, ...props }))
      return within(host).getByTestId('queue-card')
    }

    const inFlight = render({ status: 'Downloading', progress: 0.5 }, { isInFlight: true })
    expect(countTestId(inFlight, 'progress-bar')).toBe(1)
    unmount()

    const pending = render({ status: 'Pending', position: 7 })
    expect(countTestId(pending, 'progress-bar')).toBe(0)
    const pendingMeta = within(pending).getByTestId('queue-card-meta').textContent ?? ''
    expect(pendingMeta).toMatch(/wait/i)
    expect(pendingMeta).toContain('7')
    unmount()

    const done = render({ status: 'Done', fileSize: 245_000_000 })
    expect(within(done).getByTestId('queue-card-meta').textContent).toContain(formatFileSize(245_000_000))
    unmount()

    const longError = `yt-dlp exited 1: ${'requested format is not available. '.repeat(6)}`
    const failed = render({ status: 'Failed', errorMessage: longError })
    const failedMeta = within(failed).getByTestId('queue-card-meta')
    expect(failedMeta.className).toContain('truncate')
    expect(failedMeta.getAttribute('title')).toBe(longError)
  })

  it('AC-44.7 the title and meta truncate while keeping the full string in a tooltip', async () => {
    const { QueueCard } = await load.card()
    const longTitle = `A very long video title ${'that keeps going '.repeat(8)}`
    const longError = `ffmpeg failed: ${'unsupported codec parameters '.repeat(8)}`
    const host = mount(
      createElement(QueueCard, {
        job: job({ status: 'Failed', title: longTitle, errorMessage: longError }),
        onOpen: noop,
      }),
    )
    const card = within(host).getByTestId('queue-card')
    const title = within(card).getByTestId('queue-card-title')
    const meta = within(card).getByTestId('queue-card-meta')
    expect(title.className).toContain('truncate')
    expect(title.getAttribute('title')).toBe(longTitle)
    expect(meta.className).toContain('truncate')
    expect(meta.getAttribute('title')).toBe(longError)
  })

  it('AC-44.8 the kebab menu renders only applicable actions, in order, with state-correct labels', async () => {
    const { QueueCard } = await load.card()

    // (a) a Done job in the middle of a multi-item list — all eight ids.
    const handlersA = allMenuHandlers()
    const hostA = mount(
      createElement(QueueCard, {
        job: job({ status: 'Done', outputPath: 'C:/out/a.mp4' }),
        onOpen: noop,
        isFirst: false,
        isLast: false,
        ...handlersA,
      }),
    )
    const kebab = within(hostA).getByTestId('queue-card-kebab')
    expect(kebab.getAttribute('aria-haspopup')).toBe('menu')
    expect(kebab.getAttribute('aria-expanded')).toBe('false')
    await user.click(kebab)
    expect(kebab.getAttribute('aria-expanded')).toBe('true')
    expect(menuLabels(hostA)).toEqual([
      LABELS['open-file'],
      LABELS['open-folder'],
      COPY_LABELS.withOutputPath,
      LABELS['move-up'],
      LABELS['move-down'],
      LABELS['move-top'],
      LABELS['move-bottom'],
      LABELS.remove,
    ])
    const items = menuItems(hostA)
    expect(items.every((item) => !item.hasAttribute('disabled'))).toBe(true)
    expect(items.every((item) => item.getAttribute('aria-disabled') === null)).toBe(true)
    expect(items[items.length - 1].className).toContain('text-error')

    // Arrow keys move between rendered items; Escape closes and restores focus.
    expect(document.activeElement).toBe(items[0])
    await user.keyboard('{ArrowDown}')
    expect(document.activeElement).toBe(items[1])
    await user.keyboard('{ArrowUp}')
    expect(document.activeElement).toBe(items[0])

    // `Copy path` must copy the path it names.
    await user.click(items[2])
    expect(handlersA.onCopyLocation).toHaveBeenCalledWith('C:/out/a.mp4')

    await user.click(kebab)
    await user.keyboard('{Escape}')
    expect(within(hostA).queryAllByTestId('queue-card-menu')).toHaveLength(0)
    expect(document.activeElement).toBe(kebab)
    unmount()

    // (b) a Pending job first in a multi-item list — the downward moves survive.
    const handlersB = allMenuHandlers()
    const hostB = mount(
      createElement(QueueCard, {
        job: job({ status: 'Pending', sourceUrl: 'https://youtu.be/abc' }),
        onOpen: noop,
        isFirst: true,
        isLast: false,
        ...handlersB,
      }),
    )
    await user.click(within(hostB).getByTestId('queue-card-kebab'))
    expect(menuLabels(hostB)).toEqual([
      COPY_LABELS.withoutOutputPath,
      LABELS['move-down'],
      LABELS['move-bottom'],
      LABELS.remove,
    ])
    const itemsB = menuItems(hostB)
    // `Copy URL` must copy the URL it names.
    await user.click(itemsB[0])
    expect(handlersB.onCopyLocation).toHaveBeenCalledWith('https://youtu.be/abc')
    unmount()

    // (c) the only job in a one-item queue — no move target in either direction.
    const hostC = mount(
      createElement(QueueCard, {
        job: job({ status: 'Pending' }),
        onOpen: noop,
        isFirst: true,
        isLast: true,
        ...allMenuHandlers(),
      }),
    )
    await user.click(within(hostC).getByTestId('queue-card-kebab'))
    expect(menuLabels(hostC)).toEqual([COPY_LABELS.withoutOutputPath, LABELS.remove])
    unmount()

    // (d) only `onRemove` supplied.
    const hostD = mount(
      createElement(QueueCard, {
        job: job({ status: 'Pending' }),
        onOpen: noop,
        isFirst: false,
        isLast: false,
        onRemove: noop,
      }),
    )
    await user.click(within(hostD).getByTestId('queue-card-kebab'))
    expect(menuLabels(hostD)).toEqual([LABELS.remove])
  })

  it('AC-44.9 QueueList preserves server order and parameterizes the row testid', async () => {
    const { QueueList } = await load.list()
    const items: Job[] = [
      job({ id: 'c', position: 9, title: 'third-in-queue' }),
      job({ id: 'a', position: 2, title: 'first-in-queue' }),
      job({ id: 'b', position: 5, title: 'second-in-queue' }),
    ]
    const host = mount(createElement(QueueList, { items, onOpen: noop }))
    const list = within(host).getByTestId('queue-list')
    const titles = Array.from(list.querySelectorAll<HTMLElement>('[data-testid="queue-card-title"]'))
    expect(titles.map((el) => el.textContent)).toEqual([
      'third-in-queue',
      'first-in-queue',
      'second-in-queue',
    ])
    expect(countTestId(list, 'queue-card')).toBe(3)
    unmount()

    const custom = mount(
      createElement(QueueList, { items, onOpen: noop, rowTestId: 'convert-queue-row' }),
    )
    expect(countTestId(custom, 'convert-queue-row')).toBe(3)
    expect(countTestId(custom, 'queue-card')).toBe(0)

    const source = read(resolve(UI_QUEUE_COMPONENTS_DIR, 'QueueList.tsx'))
    expect(source).not.toMatch(/\.sort\(/)
  })

  it('AC-44.10 EmptyDropZone offers a keyboard-reachable Browse path', async () => {
    const { EmptyDropZone } = await load.emptyZone()
    const onBrowse = vi.fn()
    const host = mount(createElement(EmptyDropZone, { onBrowse }))
    const zone = within(host).getByTestId('empty-drop-zone')
    expect(zone.className).toContain('border-dashed')
    expect((zone.textContent ?? '').trim().length).toBeGreaterThan(0)

    const browse = within(host).getByTestId('empty-drop-zone-browse')
    expect(browse).toBeInstanceOf(HTMLButtonElement)
    expect(browse.tabIndex).toBeGreaterThanOrEqual(0)

    document.body.focus()
    await user.tab()
    expect(document.activeElement).toBe(browse)

    await user.click(browse)
    expect(onBrowse).toHaveBeenCalledTimes(1)
  })

  it('AC-44.11 EmptyDropZone reflects every DRAG_STATES value and explains a rejection mid-drag', async () => {
    const { EmptyDropZone } = await load.emptyZone()
    const rejectionReason = 'Only video files can be added here.'
    const onDropFiles = vi.fn()
    const host = mount(
      createElement(EmptyDropZone, {
        onBrowse: noop,
        onDropFiles,
        accept: acceptsMedia,
        rejectionReason,
        windowDragActive: false,
      }),
    )
    const zone = within(host).getByTestId('empty-drop-zone')
    expect(zone.dataset.dragState).toBe('idle')

    fireDrag(zone, 'dragenter', { items: [MEDIA_ITEM] })
    expect(zone.dataset.dragState).toBe('direct-hover')

    // A child entering and leaving must not flicker the state (enter/leave counter).
    const child = within(host).getByTestId('empty-drop-zone-browse')
    fireDrag(child, 'dragenter', { items: [MEDIA_ITEM] })
    expect(zone.dataset.dragState).toBe('direct-hover')
    fireDrag(child, 'dragleave', { items: [MEDIA_ITEM] })
    expect(zone.dataset.dragState).toBe('direct-hover')

    fireDrag(zone, 'dragleave', { items: [MEDIA_ITEM] })
    expect(zone.dataset.dragState).toBe('idle')

    // Invalid payload: the reason is visible during the drag, before any drop.
    fireDrag(zone, 'dragenter', { items: [TEXT_ITEM] })
    expect(zone.dataset.dragState).toBe('invalid')
    expect(zone.textContent).toContain(rejectionReason)
    expect(onDropFiles).not.toHaveBeenCalled()
    fireDrag(zone, 'dragleave', { items: [TEXT_ITEM] })
    unmount()

    const dragging = mount(
      createElement(EmptyDropZone, { onBrowse: noop, accept: acceptsMedia, windowDragActive: true }),
    )
    expect(within(dragging).getByTestId('empty-drop-zone').dataset.dragState).toBe('window-drag')

    // Every declared state is observable.
    expect(new Set(SETS.DRAG_STATES)).toEqual(
      new Set(['idle', 'window-drag', 'direct-hover', 'invalid']),
    )
  })

  it('AC-44.12 a populated QueueList stays a drop target and keeps its cards visible', async () => {
    const { QueueList } = await load.list()
    const items = [job({ id: 'a', title: 'kept-visible' }), job({ id: 'b', title: 'also-visible' })]
    const host = mount(
      createElement(QueueList, { items, onOpen: noop, accept: acceptsMedia, onDropFiles: noop }),
    )
    const list = within(host).getByTestId('queue-list')
    expect(countTestId(list, 'queue-drop-overlay')).toBe(0)

    fireDrag(list, 'dragenter', { items: [MEDIA_ITEM] })
    const overlay = within(list).getByTestId('queue-drop-overlay')
    expect((overlay.textContent ?? '').trim().length).toBeGreaterThan(0)
    expect(countTestId(list, 'queue-card')).toBe(2)

    fireDrag(list, 'dragleave', { items: [MEDIA_ITEM] })
    expect(countTestId(list, 'queue-drop-overlay')).toBe(0)
  })

  it('AC-44.13 the standards sweep passes, no dependency is added and no page imports the card', () => {
    const sources = walk(UI_QUEUE_COMPONENTS_DIR)
    expect(sources.length).toBeGreaterThan(0)

    for (const file of sources) {
      const source = read(file)
      for (const line of source.split('\n')) {
        if (line.includes('className') || line.includes('-[')) {
          expect(line, `raw hex in ${file}`).not.toMatch(/#[0-9a-fA-F]{3,8}\b/)
        }
      }
      expect(source, file).not.toContain('transition-all')
      expect(source, file).not.toMatch(/duration-\[(?!var\()/)
      expect(source, file).not.toMatch(/TODO|FIXME|NotImplementedError/)
      expect(source, file).not.toMatch(/variant="(?!primary|secondary|outline|ghost|destructive)/)
    }

    for (const file of walk(resolve(repoRoot, 'ui/tests/unit'))) {
      expect(read(file), file).not.toMatch(
        /it\.skip|describe\.skip|test\.skip|it\.todo|test\.todo|it\.only|describe\.only|test\.only/,
      )
    }

    const pkg = JSON.parse(read(UI_PACKAGE_JSON)) as {
      dependencies?: Record<string, string>
      devDependencies?: Record<string, string>
    }
    const names = [
      ...Object.keys(pkg.dependencies ?? {}),
      ...Object.keys(pkg.devDependencies ?? {}),
    ]
    // MEU-49 supersession (same in-place pattern as the MEU-45 note below):
    // docs/build-plan/10-queue-card-ui.md:254-256 makes dnd-kit *the* drag-and-drop
    // dependency for this phase, so the half of this guard that forbade it has
    // expired. The virtualization half has not — 10-queue-card-ui.md:47 still
    // forbids one — so the regex is NARROWED and stays armed rather than deleted.
    expect(names.filter((name) => /react-virtual/.test(name))).toEqual([])

    // MEU-45 supersession (E2E_REWRITE_RULE discipline at unit level): MEU-44
    // froze the pages away from the queue package because nothing had migrated
    // yet. MEU-45 migrates the converter onto it, so the "yet" has expired. The
    // invariant the assertion actually protected — the shared queue package
    // stays page-agnostic — is asserted here in the direction that survives
    // every remaining MEU: components never reach back into a feature.
    for (const file of sources) {
      expect(read(file), `${file} must not depend on a page`).not.toMatch(
        /from '[^']*features\//,
      )
    }
    const converterImports = walk(FEATURES_DIR).some((file) =>
      read(file).includes('components/queue'),
    )
    expect(converterImports, 'a page now mounts the shared queue package').toBe(true)

    const registry = read(TESTID_REGISTRY)
    for (const id of [...SETS.NEW_TESTIDS, ...SETS.PRESERVED_TESTIDS]) {
      // MEU-45 supersession: an id this project retires must be *absent* —
      // a registry of dead ids is exactly the stale canon the migration removes.
      // Its capability is not lost: MIGRATED_HOMES names where each one landed
      // and that id is asserted present in its place.
      if (MIGRATED_AWAY.has(id)) {
        expect(registry, `retired ${id} is still registered`).not.toContain(`'${id}'`)
        continue
      }
      expect(registry, `testid ${id} is unregistered`).toContain(`'${id}'`)
    }
    for (const home of MIGRATED_HOMES) {
      expect(registry, `new home ${home} is unregistered`).toContain(`'${home}'`)
    }

    const titles: string[] = []
    for (const entry of readdirSync(E2E_DIR)) {
      if (!/\.(test|spec)\.ts$/.test(entry)) {
        continue
      }
      for (const line of read(resolve(E2E_DIR, entry)).split('\n')) {
        if (/^\s*test\(\s*(['"`])(.+?)\1/.test(line)) {
          titles.push(line)
        }
      }
    }
    // MEU-45 supersession: E2E_ASSERTION_CENSUS_RULE replaces MEU-44's frozen
    // equality with a floor — the suite may grow as pages migrate, never shrink.
    expect(titles.length).toBeGreaterThanOrEqual(SETS.E2E_BASELINE_COUNT)
  })

  it('AC-44.14 the in-flight cancel discloses queue scope and opens no dialog', async () => {
    const { QueueCard } = await load.card()
    const onCancelQueue = vi.fn()
    const host = mount(
      createElement(QueueCard, {
        job: job({ status: 'Downloading', progress: 0.3 }),
        isInFlight: true,
        onOpen: noop,
        onCancelQueue,
      }),
    )
    const control = within(host).getByTestId('queue-card-primary-action')
    const accessibleName = (control.getAttribute('aria-label') ?? control.textContent ?? '').trim()
    expect(accessibleName).toBe(SETS.CANCEL_CONTROL_LABEL)
    expect(control.getAttribute('title')).toBe(SETS.CANCEL_CONTROL_TITLE)
    for (const forbidden of SETS.CANCEL_LABEL_FORBIDDEN) {
      expect(accessibleName).not.toBe(forbidden)
    }

    await user.click(control)
    expect(onCancelQueue).toHaveBeenCalledTimes(1)
    expect(screen.queryAllByRole('dialog')).toHaveLength(0)
  })

  it('AC-44.15 blocker cards render the job reason and the shared remediation as distinct nodes', async () => {
    const { QueueCard } = await load.card()
    const cardSource = read(resolve(UI_QUEUE_COMPONENTS_DIR, 'QueueCard.tsx'))

    for (const status of SETS.BLOCKER_STATUSES) {
      const reason = `blocked: ${status} for this video`
      const host = mount(
        createElement(QueueCard, {
          job: job({ status, errorMessage: reason }),
          onOpen: noop,
        }),
      )
      const card = within(host).getByTestId('queue-card')
      const remediation = SETS.BLOCKER_REMEDIATION[status]
      const reasonNode = within(card).getByTestId('queue-card-meta')
      const remediationNode = card.querySelector<HTMLElement>('[data-blocker-remediation]')
      expect(reasonNode.textContent).toContain(reason)
      expect(remediationNode, `no remediation node for ${status}`).not.toBeNull()
      expect(remediationNode?.textContent).toContain(remediation)
      expect(remediationNode).not.toBe(reasonNode)
      expect(reasonNode.contains(remediationNode)).toBe(false)
      // Neither string is authored by the component.
      expect(cardSource).not.toContain(remediation)
      unmount()
    }

    // A missing reason is never masked by the remediation copy.
    const host = mount(
      createElement(QueueCard, {
        job: job({ status: SETS.BLOCKER_STATUSES[0], errorMessage: null }),
        onOpen: noop,
      }),
    )
    const meta = within(host).getByTestId('queue-card').querySelector<HTMLElement>(
      '[data-testid="queue-card-meta"]',
    )
    expect(meta?.textContent ?? '').not.toContain(SETS.BLOCKER_REMEDIATION[SETS.BLOCKER_STATUSES[0]])
  })

  it('AC-44.16 no CARD_INTERACTIVE_ZONES control lives inside the open-region', async () => {
    const { QueueCard } = await load.card()
    const onOpen = vi.fn()
    const onSelectChange = vi.fn()
    const onRetry = vi.fn()
    const host = mount(
      createElement(QueueCard, {
        job: job({ status: 'Failed', errorMessage: 'yt-dlp exited 1' }),
        requeueableStatuses: SETS.REQUEUEABLE_DOWNLOAD_STATUSES,
        selectable: true,
        isFirst: false,
        isLast: false,
        onOpen,
        onSelectChange,
        onRetry,
        onRemove: noop,
      }),
    )
    const card = within(host).getByTestId('queue-card')
    const region = openRegion(card)

    const zoneIds: Record<string, string> = {
      'selection-checkbox': 'selection-checkbox',
      'primary-action': 'queue-card-primary-action',
      'kebab-trigger': 'queue-card-kebab',
    }
    for (const zone of SETS.CARD_INTERACTIVE_ZONES) {
      const control = within(card).getByTestId(zoneIds[zone])
      expect(region.contains(control), `${zone} is inside the open-region`).toBe(false)
      expect(control.closest('[role="button"]'), `${zone} nests in a button`).toBeNull()
      expect(control.tabIndex).toBeGreaterThanOrEqual(0)
    }

    await user.click(within(card).getByTestId('selection-checkbox'))
    expect(onSelectChange).toHaveBeenCalledTimes(1)
    expect(onOpen).not.toHaveBeenCalled()

    await user.click(within(card).getByTestId('queue-card-primary-action'))
    expect(onRetry).toHaveBeenCalledTimes(1)
    expect(onOpen).not.toHaveBeenCalled()

    const kebab = within(card).getByTestId('queue-card-kebab')
    kebab.focus()
    await user.keyboard('{Enter}')
    expect(countTestId(card, 'queue-card-menu')).toBe(1)
    expect(onOpen).not.toHaveBeenCalled()
  })
})

// ---------------------------------------------------------------------------
// MEU-45 — the two card contracts the converter migration adds (AC-45.1, AC-45.2).
//
// AC-45.1 gives the card a `metaSegments` prop so a page can append its own
// columns (the converter's Kind/Mode/Speed/ETA) to the shared `resolveMeta`
// line without either page owning the other's copy.
// AC-45.2 closes `DEAD_REGION_RULE`: the title region currently advertises
// `role="button"`, `tabIndex` and an `aria-label` even when no `onOpen` is
// supplied, so a screen-reader user is told to activate a control that does
// nothing. Without `onOpen` all three affordances must be absent.
// ---------------------------------------------------------------------------

const meu45PlanDir = resolve(repoRoot, 'docs/execution/plans/2026-09-02-p10-queue-card-migration')

type Meu45Sets = {
  META_SEPARATOR: { value: string }
  META_SEGMENTS_CONTRACT: { value: string }
  DEAD_REGION_RULE: { value: string }
}

const MEU45 = readJson<Meu45Sets>(resolve(meu45PlanDir, 'named-sets.json'))
const META_SEPARATOR = MEU45.META_SEPARATOR.value

describe('MEU-45 queue card meta segments and dead-region rule', () => {
  it('AC-45.1 R1-F4 the placeholder never leads a line that has real segments', async () => {
    /*
      Exec-review round 1, Finding 4. The filter ran over the page-owned TAIL
      only, so whenever `resolveMeta` had nothing to say it emitted the em-dash
      sentinel and that sentinel was joined in front of the page's real columns:
      a Skipped row read `— · Compress · Balanced`, a placeholder standing in
      front of the very facts it exists to substitute for.
    */
    const { QueueCard } = await load.card()

    // Skipped: `resolveMeta` has nothing to report, the page does.
    const host = mount(
      createElement(QueueCard, {
        job: job({ status: 'Skipped' }),
        isFirst: true,
        isLast: true,
        onOpen: noop,
        metaSegments: ['Compress', 'Balanced'],
      }),
    )
    const text = (within(host).getByTestId('queue-card-meta').textContent ?? '').trim()
    expect(text).toBe(['Compress', 'Balanced'].join(META_SEPARATOR))
    expect(text.startsWith('—'), 'no sentinel in the lead position').toBe(false)
    unmount()

    // A sentinel arriving from the PAGE is dropped the same way - the filter is
    // over the whole sequence, not over one half of it.
    const fromPage = mount(
      createElement(QueueCard, {
        job: job({ status: 'Done', fileSize: 1_048_576, outputPath: 'C:/out/a.mp4' }),
        isFirst: true,
        isLast: true,
        onOpen: noop,
        metaSegments: ['—', 'Balanced'],
      }),
    )
    expect((within(fromPage).getByTestId('queue-card-meta').textContent ?? '').trim()).toBe(
      [formatFileSize(1_048_576), 'Balanced'].join(META_SEPARATOR),
    )
    unmount()

    // ...but it survives alone, because the row must keep its height whatever
    // the state (DEAD_REGION_RULE).
    const nothing = mount(
      createElement(QueueCard, {
        job: job({ status: 'Skipped' }),
        isFirst: true,
        isLast: true,
        onOpen: noop,
        metaSegments: ['', '   '],
      }),
    )
    expect((within(nothing).getByTestId('queue-card-meta').textContent ?? '').trim()).toBe('—')
    unmount()
  })

  it('AC-45.1 metaSegments append to resolveMeta and empty segments are dropped', async () => {
    const { QueueCard } = await load.card()
    expect(META_SEPARATOR, 'the separator is a single named statement').toBe(' \u00b7 ')

    // The shared meta line still leads: the page's segments are appended to it,
    // never in place of it.
    const host = mount(
      createElement(QueueCard, {
        job: job({ status: 'Done', fileSize: 1_048_576, outputPath: 'C:/out/a.mp4' }),
        isFirst: true,
        isLast: true,
        onOpen: noop,
        metaSegments: ['Compress', 'Balanced', '2.4x'],
      }),
    )
    const meta = within(host).getByTestId('queue-card-meta')
    const rendered = (meta.textContent ?? '').trim()
    expect(rendered).toBe(
      [formatFileSize(1_048_576), 'Compress', 'Balanced', '2.4x'].join(META_SEPARATOR),
    )
    unmount()

    // Empty and whitespace-only segments are dropped, so a page that cannot
    // resolve a column never produces a dangling separator.
    const sparse = mount(
      createElement(QueueCard, {
        job: job({ status: 'Done', fileSize: 1_048_576, outputPath: 'C:/out/a.mp4' }),
        isFirst: true,
        isLast: true,
        onOpen: noop,
        metaSegments: ['Cut', '', '   ', 'a:1'],
      }),
    )
    const sparseText = (within(sparse).getByTestId('queue-card-meta').textContent ?? '').trim()
    expect(sparseText).toBe([formatFileSize(1_048_576), 'Cut', 'a:1'].join(META_SEPARATOR))
    expect(sparseText).not.toMatch(/\u00b7\s*\u00b7/)
    expect(sparseText.endsWith(META_SEPARATOR.trimEnd())).toBe(false)
    unmount()

    // Omitting the prop leaves the MEU-44 line byte-identical — the downloader
    // page passes nothing and must be unaffected.
    const bare = mount(
      createElement(QueueCard, {
        job: job({ status: 'Done', fileSize: 1_048_576, outputPath: 'C:/out/a.mp4' }),
        isFirst: true,
        isLast: true,
        onOpen: noop,
      }),
    )
    expect((within(bare).getByTestId('queue-card-meta').textContent ?? '').trim()).toBe(
      formatFileSize(1_048_576),
    )
  })

  it('AC-45.2 without onOpen the title region advertises no dead affordance', async () => {
    const { QueueCard } = await load.card()

    // DEAD_REGION_RULE — no handler, no role, no tab stop, no aria-label.
    const host = mount(
      createElement(QueueCard, {
        job: job({ status: 'Pending' }),
        isFirst: true,
        isLast: true,
      }),
    )
    const card = within(host).getByTestId('queue-card')
    const title = within(card).getByTestId('queue-card-title')
    expect(card.querySelector('[role="button"]'), 'no dead open-region').toBeNull()
    expect(title.getAttribute('role'), 'no role without onOpen').toBeNull()
    expect(title.hasAttribute('tabindex'), 'no tab stop without onOpen').toBe(false)
    expect(title.getAttribute('aria-label'), 'no aria-label without onOpen').toBeNull()
    // The title is still rendered — the rule removes the affordance, not the text.
    expect((title.textContent ?? '').trim().length).toBeGreaterThan(0)
    unmount()

    // With the handler all three come back and both activation keys work.
    const onOpen = vi.fn()
    const live = mount(
      createElement(QueueCard, {
        job: job({ status: 'Pending', title: 'Example video' }),
        isFirst: true,
        isLast: true,
        onOpen,
      }),
    )
    const region = openRegion(within(live).getByTestId('queue-card'))
    expect(region.getAttribute('role')).toBe('button')
    expect(region.tabIndex).toBe(0)
    expect(region.getAttribute('aria-label')).toBe('Open details for Example video')

    region.focus()
    await user.keyboard('{Enter}')
    expect(onOpen, 'Enter opens').toHaveBeenCalledTimes(1)
    await user.keyboard(' ')
    expect(onOpen, 'Space opens').toHaveBeenCalledTimes(2)
  })
})

// ---------------------------------------------------------------------------
// MEU-47 — selection does not fight the card's nested controls (AC-47.9).
//
// The card is one big activation target with smaller ones inside it. Once rows
// are selectable, every one of those inner controls is a chance to toggle the
// selection by accident — the classic nested-interactive bug, and the reason the
// spec calls it out. Each nested control gets its own assertion, because a fix
// applied to the kebab alone would leave the others wrong.
// ---------------------------------------------------------------------------

describe('MEU-47 QueueCard selection isolation', () => {
  it('AC-47.9 nested controls do not toggle selection', async () => {
    const { QueueCard } = await load.card()
    const onSelectChange = vi.fn()
    const onOpen = vi.fn()
    const onRetry = vi.fn()

    const host = mount(
      createElement(QueueCard, {
        job: job({ id: 'job-9', status: 'Failed', errorMessage: 'ffmpeg exited 1' }),
        selectable: true,
        selected: false,
        requeueableStatuses: SETS.REQUEUEABLE_DOWNLOAD_STATUSES,
        onSelectChange,
        onOpen,
        onRetry,
        ...allMenuHandlers(),
      }),
    )
    const card = within(host).getByTestId('queue-card')

    // The kebab: opening the menu is not a selection gesture.
    await user.click(within(card).getByTestId('queue-card-kebab'))
    expect(onSelectChange, 'the kebab does not toggle selection').not.toHaveBeenCalled()

    const menu = screen.queryByTestId('queue-card-menu')
    expect(menu, 'the menu opened').not.toBeNull()
    await user.keyboard('{Escape}')

    // The primary action: Retry runs, the selection does not change.
    await user.click(within(card).getByTestId('queue-card-primary-action'))
    expect(onRetry, 'the primary action still fires').toHaveBeenCalledTimes(1)
    expect(onSelectChange, 'the primary action does not toggle selection').not.toHaveBeenCalled()

    // The open region: opening the detail panel is its own gesture. A card that
    // toggled selection here would make every detail view a selection change.
    await user.click(openRegion(card))
    expect(onOpen).toHaveBeenCalledTimes(1)
    expect(onSelectChange, 'opening the row does not toggle selection').not.toHaveBeenCalled()

    // And the checkbox itself still works — isolation is not deafness.
    await user.click(within(card).getByTestId('selection-checkbox'))
    expect(onSelectChange).toHaveBeenCalledTimes(1)
    expect(onSelectChange).toHaveBeenCalledWith('job-9', true, { shiftKey: false })
    expect(onOpen, 'ticking the checkbox does not open the row').toHaveBeenCalledTimes(1)
  })
})

// ---------------------------------------------------------------------------
// MEU-49 — drag handle (DND_HANDLE_CONTRACT, DND_HOVER_REVEAL_RULE,
// DND_TOUCH_ACTION_RULE, ALT_ARROW_SUPPRESSION_RULE, G33_RULE, G34_RULE).
// ---------------------------------------------------------------------------

const dndPlanDir = resolve(repoRoot, 'docs/execution/plans/2026-09-03-p10-queue-card-dnd')
const dndSets = readJson<{
  DND_TESTIDS: { value: string[] }
}>(resolve(dndPlanDir, 'named-sets.json'))
const DRAG_HANDLE_TESTID = dndSets.DND_TESTIDS.value[0]

/**
 * The dnd-kit surface `useSortable` hands a row, in the shape `QueueList` will
 * forward it. It is passed as a prop rather than read from a context so the
 * card stays assertable without a `DndContext`: jsdom cannot complete a drag
 * (`JSDOM_RECT_RULE`), so what a unit test can prove is that every piece
 * dnd-kit supplies actually reaches the activator element.
 */
function dragProp(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    attributes: {
      'aria-roledescription': 'sortable',
      'aria-describedby': 'DndDescribedBy-0',
    },
    listeners: { onPointerDown: vi.fn(), onKeyDown: vi.fn() },
    setActivatorNodeRef: vi.fn(),
    isDragging: false,
    ...overrides,
  }
}

function dragHandle(card: HTMLElement): HTMLElement {
  return within(card).getByTestId(DRAG_HANDLE_TESTID)
}

describe('MEU-49 QueueCard drag handle', () => {
  it('AC-49.8 the handle is the first child, a real button, and carries every dnd-kit surface [TA-25]', async () => {
    const { QueueCard } = await load.card()
    const drag = dragProp()

    const host = mount(
      createElement(QueueCard, {
        job: job({ id: 'job-d1', title: 'Example video' }),
        selectable: true,
        selected: false,
        onSelectChange: noop,
        onOpen: noop,
        drag,
        ...allMenuHandlers(),
      }),
    )
    const card = within(host).getByTestId('queue-card')
    const handle = dragHandle(card)

    // FIRST child — ahead of the checkbox, which is the zone it displaces. MEU-80: the handle sits in its
    // TOOLTIP wrapper, so the wrapper leads the row and holds the handle alone.
    const handleTip = within(card).getByTestId(`${DRAG_HANDLE_TESTID}-tip`)
    expect(card.firstElementChild, 'the handle tip leads the row').toBe(handleTip)
    expect(handleTip.children.length, 'the tip holds one element').toBe(1)
    expect(handleTip.firstElementChild, 'the handle is the tip only child').toBe(handle)

    // A real <button type="button">, not a div wearing role="button": only a
    // real button is reachable by Tab, which is what makes the keyboard drag
    // and the live-region announcements reachable at all.
    expect(handle.tagName).toBe('BUTTON')
    expect(handle.getAttribute('type')).toBe('button')

    // The canonical Button's own marker class (G34_RULE) — a bare <button>
    // with ad-hoc padding would satisfy the tag assertion and fail this one.
    expect(handle.className).toContain('btn-ghost')

    expect(handle.getAttribute('aria-label')).toBe('Reorder Example video')

    // dnd-kit's `attributes` reach the element verbatim.
    expect(handle.getAttribute('aria-roledescription')).toBe('sortable')
    expect(handle.getAttribute('aria-describedby')).toBe('DndDescribedBy-0')

    // `setActivatorNodeRef` receives THIS element — the ref is what gives
    // dnd-kit focus restoration after a keyboard drag.
    const setActivatorNodeRef = drag.setActivatorNodeRef as ReturnType<typeof vi.fn>
    expect(setActivatorNodeRef).toHaveBeenCalledWith(handle)

    // dnd-kit's `listeners` are live, not merely present in the props object.
    const listeners = drag.listeners as Record<string, ReturnType<typeof vi.fn>>
    await user.click(handle)
    expect(listeners.onPointerDown, 'the pointer sensor hears the press').toHaveBeenCalled()
    handle.focus()
    await user.keyboard('[Space]')
    expect(listeners.onKeyDown, 'the keyboard sensor hears the lift').toHaveBeenCalled()
  })

  it('AC-49.9 the handle is a sibling of every other zone, never an ancestor or a descendant [TA-25]', async () => {
    const { QueueCard } = await load.card()

    const host = mount(
      createElement(QueueCard, {
        job: job({ id: 'job-d2', status: 'Failed', errorMessage: 'ffmpeg exited 1' }),
        selectable: true,
        selected: false,
        requeueableStatuses: SETS.REQUEUEABLE_DOWNLOAD_STATUSES,
        onSelectChange: noop,
        onOpen: noop,
        onRetry: noop,
        drag: dragProp(),
        ...allMenuHandlers(),
      }),
    )
    const card = within(host).getByTestId('queue-card')
    const handle = dragHandle(card)

    const handleTip = within(card).getByTestId(`${DRAG_HANDLE_TESTID}-tip`)
    expect(handleTip.parentElement, 'the handle tip hangs off the card container').toBe(card)
    expect(handle.parentElement, 'the handle sits directly in its tip').toBe(handleTip)

    const region = openRegion(card)
    expect(region.contains(handle), 'the handle is not inside the activatable region').toBe(false)
    expect(handle.contains(region)).toBe(false)

    for (const id of ['selection-checkbox', 'queue-card-primary-action', 'queue-card-kebab']) {
      const zone = within(card).getByTestId(id)
      expect(handle.contains(zone), 'the handle does not wrap ' + id).toBe(false)
      expect(zone.contains(handle), id + ' does not wrap the handle').toBe(false)
    }
  })

  it('AC-49.10 the reveal is opacity-only and the activator disables touch scrolling', async () => {
    const { QueueCard } = await load.card()

    const host = mount(
      createElement(QueueCard, {
        job: job({ id: 'job-d3' }),
        onOpen: noop,
        drag: dragProp(),
        ...allMenuHandlers(),
      }),
    )
    const card = within(host).getByTestId('queue-card')
    const handle = dragHandle(card)
    const classes = handle.className

    // Always mounted, always focusable, faded until the row is engaged.
    expect(classes).toContain('opacity-0')
    expect(classes).toContain('group-hover:opacity-100')
    expect(classes).toContain('group-focus-within:opacity-100')
    expect(classes).toContain('focus-visible:opacity-100')

    // The container has to be the `group` those variants resolve against, or
    // the handle is permanently invisible to a mouse user.
    expect(card.className.split(/\s+/)).toContain('group')

    // DND_TOUCH_ACTION_RULE — without this a touch drag is claimed by the
    // browser's native scroll gesture and the row never moves.
    expect(classes.split(/\s+/)).toContain('touch-none')
    expect(classes).not.toContain('touch-auto')
    expect(classes).not.toContain('touch-pan-y')

    // Never removed from the tree or the accessibility tree.
    expect(classes.split(/\s+/)).not.toContain('hidden')
    expect(handle.getAttribute('aria-hidden')).toBeNull()
    expect(handle.getAttribute('style') ?? '').not.toContain('display')

    // G33_RULE — opacity is the only animated property; no geometry.
    for (const geometry of ['w-', 'h-', 'top-', 'left-', 'margin', 'shadow']) {
      expect(
        classes.includes('transition-[' + geometry) || classes.includes('animate-' + geometry),
        'the reveal must not animate ' + geometry,
      ).toBe(false)
    }
  })

  it('AC-49.11 with drag disabled the card renders no handle and no dnd attributes', async () => {
    const { QueueCard } = await load.card()

    const host = mount(
      createElement(QueueCard, {
        job: job({ id: 'job-d4' }),
        selectable: true,
        selected: false,
        onSelectChange: noop,
        onOpen: noop,
        ...allMenuHandlers(),
      }),
    )
    const card = within(host).getByTestId('queue-card')

    expect(countTestId(card, DRAG_HANDLE_TESTID)).toBe(0)
    expect(within(card).queryByRole('button', { name: /^Reorder / })).toBeNull()
    expect(card.querySelector('[aria-roledescription="sortable"]')).toBeNull()

    // The pre-MEU leading zone is back in front, so nothing shifted for the
    // transcript and TTS queues, which never opt in.
    expect(card.firstElementChild).toBe(within(card).getByTestId('selection-checkbox'))
  })

  it('AC-49.12 Alt+Arrow is inert while the row is being dragged and live when it is not', async () => {
    const { QueueCard } = await load.card()
    const handlers = allMenuHandlers()

    const dragging = mount(
      createElement(QueueCard, {
        job: job({ id: 'job-d5', position: 2 }),
        isFirst: false,
        isLast: false,
        onOpen: noop,
        drag: dragProp({ isDragging: true }),
        ...handlers,
      }),
    )
    const draggingCard = within(dragging).getByTestId('queue-card')
    within(draggingCard).getByRole('button', { name: /^Open details for / }).focus()

    await user.keyboard('{Alt>}{ArrowUp}{/Alt}')
    await user.keyboard('{Alt>}{ArrowDown}{/Alt}')

    // The visible order mid-drag is uncommitted, so a keyboard move here would
    // fold a permutation from a stale base and clobber the drop that follows.
    expect(handlers.onMoveUp, 'Alt+ArrowUp is suppressed mid-drag').not.toHaveBeenCalled()
    expect(handlers.onMoveDown, 'Alt+ArrowDown is suppressed mid-drag').not.toHaveBeenCalled()

    unmount()

    const idle = mount(
      createElement(QueueCard, {
        job: job({ id: 'job-d5', position: 2 }),
        isFirst: false,
        isLast: false,
        onOpen: noop,
        drag: dragProp({ isDragging: false }),
        ...handlers,
      }),
    )
    const idleCard = within(idle).getByTestId('queue-card')
    within(idleCard).getByRole('button', { name: /^Open details for / }).focus()

    await user.keyboard('{Alt>}{ArrowUp}{/Alt}')
    await user.keyboard('{Alt>}{ArrowDown}{/Alt}')

    // Suppression, not removal: Alt+Arrow stays the equal reorder path.
    expect(handlers.onMoveUp).toHaveBeenCalledWith('job-d5')
    expect(handlers.onMoveDown).toHaveBeenCalledWith('job-d5')
  })

  it('AC-49.12 the isFirst / isLast guards are unchanged when drag is enabled', async () => {
    const { QueueCard } = await load.card()
    const handlers = allMenuHandlers()

    const host = mount(
      createElement(QueueCard, {
        job: job({ id: 'job-d6', position: 1 }),
        isFirst: true,
        isLast: false,
        onOpen: noop,
        drag: dragProp(),
        ...handlers,
      }),
    )
    const card = within(host).getByTestId('queue-card')
    within(card).getByRole('button', { name: /^Open details for / }).focus()

    await user.keyboard('{Alt>}{ArrowUp}{/Alt}')
    expect(handlers.onMoveUp, 'the first row still has no up').not.toHaveBeenCalled()

    await user.keyboard('{Alt>}{ArrowDown}{/Alt}')
    expect(handlers.onMoveDown).toHaveBeenCalledWith('job-d6')
  })

  it('AC-49.13 the handle introduces no sixth variant and no fourth size', async () => {
    const { QueueCard } = await load.card()

    const host = mount(
      createElement(QueueCard, {
        job: job({ id: 'job-d7' }),
        onOpen: noop,
        drag: dragProp(),
        ...allMenuHandlers(),
      }),
    )
    const handle = dragHandle(within(host).getByTestId('queue-card'))

    // An existing variant/size pair, named in the DOM by Button itself.
    expect(handle.className).toContain('btn-ghost')
    for (const forbidden of ['btn-drag', 'btn-handle', 'btn-icon']) {
      expect(handle.className).not.toContain(forbidden)
    }

    // The frozen 5x3 maps: read from Button.tsx rather than restated, so a new
    // entry fails here even if the handle itself never uses it.
    const buttonSource = read(resolve(UI_ROOT, 'components/ui/Button.tsx'))
    const variantUnion = /export type ButtonVariant = ([^\n]+)/.exec(buttonSource)?.[1] ?? ''
    const sizeUnion = /export type ButtonSize = ([^\n]+)/.exec(buttonSource)?.[1] ?? ''
    expect(variantUnion.split('|').length, 'Button still exposes 5 variants').toBe(5)
    expect(sizeUnion.split('|').length, 'Button still exposes 3 sizes').toBe(3)
    expect(variantUnion).toContain("'ghost'")
    expect(sizeUnion).toContain("'sm'")
  })
})
