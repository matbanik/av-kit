/** @vitest-environment jsdom */

/**
 * MEU-47 — `BulkActionBar` and `QueueSelectionHeader` (AC-47.4, AC-47.5, AC-47.5a).
 *
 * The two controls are deliberately separate components because the spec makes
 * them behave differently: the bar exists only while a selection does, while the
 * header checkbox is always mounted — it is the control that *starts* a
 * selection, so a header that appears once a row is ticked can never be used.
 *
 * `BULK_BAR_ACTIONS` is read from the plan rather than restated, so a change to
 * the normative order breaks this test instead of silently drifting.
 */

import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement, type ReactElement } from 'react'
import { afterEach, describe, expect, it, type Mock, vi } from 'vitest'

import { CONVERT_REQUEUEABLE_STATUSES } from '../../src/renderer/src/features/converter/convert-controls'
import { DOWNLOAD_REQUEUEABLE_STATUSES } from '../../src/renderer/src/features/downloader/download-controls'

import type * as BulkActionBarModule from '../../src/renderer/src/components/queue/BulkActionBar'
import type * as QueueSelectionHeaderModule from '../../src/renderer/src/components/queue/QueueSelectionHeader'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')
const planDir = resolve(repoRoot, 'docs/execution/plans/2026-09-02-p10-queue-card-migration')
const QUEUE_COMPONENTS_DIR = resolve(repoRoot, 'ui/src/renderer/src/components/queue')

type NamedSets = {
  BULK_BAR_ACTIONS: { value: string[] }
  SELECTION_HEADER_CONTRACT: { value: string }
  USER_LOCKS: { value: string[] }
}
const SETS = JSON.parse(readFileSync(resolve(planDir, 'named-sets.json'), 'utf-8')) as NamedSets
const BULK_BAR_ACTIONS = SETS.BULK_BAR_ACTIONS.value

function read(path: string): string {
  return readFileSync(path, 'utf-8')
}

/*
  The specifiers are held in variables so Vite's import-analysis cannot resolve
  them at transform time: literal ones make a MISSING module a whole-file
  collection error, which reports no test titles at all and breaks the
  RED_ORACLE mapping of one failing title per AC.
*/
const BAR_MODULE = '../../src/renderer/src/components/queue/BulkActionBar'
const HEADER_MODULE = '../../src/renderer/src/components/queue/QueueSelectionHeader'

function loadBar(): Promise<typeof BulkActionBarModule> {
  return import(/* @vite-ignore */ BAR_MODULE) as Promise<typeof BulkActionBarModule>
}

function loadHeader(): Promise<typeof QueueSelectionHeaderModule> {
  return import(/* @vite-ignore */ HEADER_MODULE) as Promise<typeof QueueSelectionHeaderModule>
}

/**
 * One tree is mounted at a time and unmounted before the next, so the
 * document-wide `screen` queries below are unambiguous; assertions that depend
 * on *where* an element sits keep their scope through `within`.
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

afterEach(() => {
  unmount()
})

/** Every handler the bar takes, recorded. */
function handlers(): {
  onRetry: Mock<(...args: unknown[]) => void>
  onMoveTop: Mock<(...args: unknown[]) => void>
  onMoveBottom: Mock<(...args: unknown[]) => void>
  onRemove: Mock<(...args: unknown[]) => void>
  onClearSelection: Mock<(...args: unknown[]) => void>
} {
  return {
    onRetry: vi.fn(),
    onMoveTop: vi.fn(),
    onMoveBottom: vi.fn(),
    onRemove: vi.fn(),
    onClearSelection: vi.fn(),
  }
}

describe('MEU-47 BulkActionBar', () => {
  it('AC-47.4 the bar is sticky above the list and unmounts on an empty selection', async () => {
    const { BulkActionBar } = await loadBar()

    // An empty selection removes the bar from the DOM. Hiding it with a class
    // would leave its buttons focusable and its handlers reachable.
    mount(
      createElement(BulkActionBar, {
        selectedStatuses: [],
        requeueableStatuses: CONVERT_REQUEUEABLE_STATUSES,
        ...handlers(),
      }),
    )
    expect(screen.queryByTestId('bulk-action-bar')).toBeNull()
    unmount()

    mount(
      createElement(BulkActionBar, {
        selectedStatuses: ['Pending', 'Failed'],
        requeueableStatuses: CONVERT_REQUEUEABLE_STATUSES,
        ...handlers(),
      }),
    )
    const bar = screen.getByTestId('bulk-action-bar')
    expect(bar.className, 'USER_LOCKS — the bar sticks above the list').toContain('sticky')

    // USER_LOCKS: "never a floating viewport-bottom bar". A `fixed` bar pinned
    // to the bottom of the viewport is the pattern the lock rules out.
    const source = read(resolve(QUEUE_COMPONENTS_DIR, 'BulkActionBar.tsx'))
    expect(SETS.USER_LOCKS.value.join('\n')).toContain('STICKY ABOVE THE LIST')
    expect(source, 'no viewport-fixed positioning').not.toMatch(/\bfixed\b/)
    expect(source, 'the bar is not pinned to the viewport bottom').not.toMatch(/\bbottom-0\b/)
    expect(source).toContain('sticky')

    // Both pages must render it inside the queue panel, immediately above the
    // list — its position in the tree is what makes "sticky" mean anything.
    for (const page of [
      'ui/src/renderer/src/features/converter/ConvertPage.tsx',
      'ui/src/renderer/src/features/downloader/DownloaderPage.tsx',
    ]) {
      const pageSource = read(resolve(repoRoot, page))
      const barAt = pageSource.indexOf('<BulkActionBar')
      const listAt = pageSource.indexOf('<QueueList')
      expect(barAt, `${page} mounts BulkActionBar`).toBeGreaterThan(-1)
      expect(listAt, `${page} still mounts QueueList`).toBeGreaterThan(-1)
      expect(barAt, `${page} renders the bar above the list`).toBeLessThan(listAt)
    }
  })

  it('AC-47.5 the bar renders BULK_BAR_ACTIONS in order and gates bulk-retry on the requeueable set', async () => {
    const { BulkActionBar } = await loadBar()
    const user = userEvent.setup()
    const spies = handlers()

    mount(
      createElement(BulkActionBar, {
        selectedStatuses: ['Failed', 'Pending', 'Done'],
        requeueableStatuses: CONVERT_REQUEUEABLE_STATUSES,
        ...spies,
      }),
    )
    const bar = screen.getByTestId('bulk-action-bar')

    // The count is accented copy, not a bare number, and it leads the bar.
    expect(within(bar).getByTestId('bulk-selection-count').textContent).toContain('3')
    expect(within(bar).getByTestId('bulk-selection-count').textContent).toContain('selected')

    // Order is normative: count first, then exactly BULK_BAR_ACTIONS.
    const rendered = Array.from(bar.querySelectorAll<HTMLElement>('[data-testid^="bulk-"]'))
      .map((el) => el.dataset.testid ?? '')
      .filter((id) => id !== 'bulk-action-bar')
    expect(rendered).toEqual([
      'bulk-selection-count',
      ...BULK_BAR_ACTIONS.map((action) => `bulk-${action}`),
    ])

    // Round 1 Finding 2: the bar carries move-TOP/move-BOTTOM and no bar-level
    // select-all. Single-step reorder stays on the kebab and the keyboard path.
    const source = read(resolve(QUEUE_COMPONENTS_DIR, 'BulkActionBar.tsx'))
    for (const forbidden of ['bulk-move-up', 'bulk-move-down', 'bulk-select-all']) {
      expect(source, `${forbidden} is not a bar action`).not.toContain(forbidden)
    }

    // Remove is the destructive variant — it is the one action that discards work.
    expect(within(bar).getByTestId('bulk-remove').className).toMatch(/danger|destructive/)

    // Every action reaches its handler.
    await user.click(within(bar).getByTestId('bulk-retry'))
    await user.click(within(bar).getByTestId('bulk-move-top'))
    await user.click(within(bar).getByTestId('bulk-move-bottom'))
    await user.click(within(bar).getByTestId('bulk-remove'))
    await user.click(within(bar).getByTestId('bulk-clear-selection'))
    expect(spies.onRetry).toHaveBeenCalledTimes(1)
    expect(spies.onMoveTop).toHaveBeenCalledTimes(1)
    expect(spies.onMoveBottom).toHaveBeenCalledTimes(1)
    expect(spies.onRemove).toHaveBeenCalledTimes(1)
    expect(spies.onClearSelection).toHaveBeenCalledTimes(1)

    // `Failed` is requeueable on the converter, so Retry is live.
    expect((within(bar).getByTestId('bulk-retry') as HTMLButtonElement).disabled).toBe(false)
    unmount()

    // USER_LOCKS: `Skipped` is never requeueable, on either page.
    for (const requeueable of [CONVERT_REQUEUEABLE_STATUSES, DOWNLOAD_REQUEUEABLE_STATUSES]) {
      expect(requeueable as readonly string[]).not.toContain('Skipped')
      mount(
        createElement(BulkActionBar, {
          selectedStatuses: ['Skipped', 'Done', 'Pending'],
          requeueableStatuses: requeueable,
          ...handlers(),
        }),
      )
      const disabled = screen.getByTestId('bulk-retry') as HTMLButtonElement
      expect(disabled.disabled, 'no selected row is requeueable').toBe(true)
      unmount()
    }

    // A downloader-only status enables Retry on the downloader and not on the
    // converter — the gate reads the page's set, not a hard-coded list.
    mount(
      createElement(BulkActionBar, {
        selectedStatuses: ['QualityBlocked'],
        requeueableStatuses: DOWNLOAD_REQUEUEABLE_STATUSES,
        ...handlers(),
      }),
    )
    expect((screen.getByTestId('bulk-retry') as HTMLButtonElement).disabled).toBe(false)
    unmount()

    mount(
      createElement(BulkActionBar, {
        selectedStatuses: ['QualityBlocked'],
        requeueableStatuses: CONVERT_REQUEUEABLE_STATUSES,
        ...handlers(),
      }),
    )
    expect((screen.getByTestId('bulk-retry') as HTMLButtonElement).disabled).toBe(true)
  })
})

describe('MEU-47 QueueSelectionHeader', () => {
  it('AC-47.5a queue-select-all is tri-state over the filtered list and is always mounted', async () => {
    const { QueueSelectionHeader } = await loadHeader()
    const user = userEvent.setup()
    const onToggleAll = vi.fn()

    // None selected → unchecked, not indeterminate, and STILL MOUNTED. This is
    // the control that starts a selection, so its presence cannot depend on one.
    const none = mount(
      createElement(QueueSelectionHeader, { total: 5, selectedCount: 0, onToggleAll }),
    )
    const noneBox = screen.getByTestId('queue-select-all') as HTMLInputElement
    expect(noneBox.checked).toBe(false)
    expect(noneBox.indeterminate).toBe(false)
    expect(none.textContent, 'the header carries an "N items" count').toContain('5 items')

    await user.click(noneBox)
    expect(onToggleAll).toHaveBeenCalledWith(true)
    unmount()

    // Some selected → indeterminate, and NOT checked.
    mount(
      createElement(QueueSelectionHeader, { total: 5, selectedCount: 2, onToggleAll }),
    )
    const someBox = screen.getByTestId('queue-select-all') as HTMLInputElement
    expect(someBox.indeterminate, 'SELECTION_HEADER_CONTRACT — partial is indeterminate').toBe(true)
    expect(someBox.checked).toBe(false)
    unmount()

    // All selected → checked, not indeterminate, and toggling clears.
    onToggleAll.mockClear()
    mount(createElement(QueueSelectionHeader, { total: 5, selectedCount: 5, onToggleAll }))
    const allBox = screen.getByTestId('queue-select-all') as HTMLInputElement
    expect(allBox.checked).toBe(true)
    expect(allBox.indeterminate).toBe(false)
    await user.click(allBox)
    expect(onToggleAll).toHaveBeenCalledWith(false)
    unmount()

    // An empty queue is unchecked, never "all selected" by vacuous truth.
    mount(
      createElement(QueueSelectionHeader, { total: 0, selectedCount: 0, onToggleAll }),
    )
    const emptyBox = screen.getByTestId('queue-select-all') as HTMLInputElement
    expect(emptyBox.checked).toBe(false)
    expect(emptyBox.indeterminate).toBe(false)

    // The header acts on what the user can see: both pages hand it the same
    // filtered list they hand QueueList.
    expect(SETS.SELECTION_HEADER_CONTRACT.value).toContain('FILTERED')
    for (const page of [
      'ui/src/renderer/src/features/converter/ConvertPage.tsx',
      'ui/src/renderer/src/features/downloader/DownloaderPage.tsx',
    ]) {
      expect(read(resolve(repoRoot, page)), `${page} mounts the header`).toContain(
        '<QueueHeaderRow',
      )
      expect(read(resolve(repoRoot, page))).toContain('total={cards.length}')
      expect(read(resolve(repoRoot, page))).toContain('selectedCount={bulk.selection.count}')
      expect(read(resolve(repoRoot, page))).toContain('onToggleAll={bulk.onToggleAll}')
    }
    const composed = read(resolve(QUEUE_COMPONENTS_DIR, 'QueueHeaderRow.tsx'))
    expect(composed).toContain('<QueueSelectionHeader')
    expect(composed).toContain('total={total}')
    expect(composed).toContain('selectedCount={selectedCount}')
    expect(composed).toContain('onToggleAll={onToggleAll}')
  })
})
