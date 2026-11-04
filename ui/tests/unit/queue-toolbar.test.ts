/** @vitest-environment jsdom */

/**
 * MEU-45 — the reduced queue toolbar (AC-45.3).
 *
 * The global queue toolbar drops from 13 buttons to `TOOLBAR_CONTROLS`: Start,
 * one Pause/Resume toggle, Clear finished, and a kebab whose menu holds
 * `QUEUE_OVERFLOW_MENU`. Three rules are asserted here and nowhere else:
 *
 * 1. **Exactly four interactive elements** live inside `[data-testid="queue-toolbar"]`
 *    — in every state, including while the overflow menu is open. The menu is a
 *    sibling of the control group, not a fifth child of it.
 * 2. **`pause-resume` is ONE button** whose label and testid suffix follow
 *    `PAUSE_SCOPE` (the processor's state, never a per-job state).
 * 3. **Icon *plus* persistent text label** (`TOOLBAR_LABEL_RULE`). A control whose
 *    only name is a `title` or `aria-label` attribute fails: `textContent` has to
 *    carry the label, and an `<svg>` has to sit beside it.
 *
 * No label is authored here — every expected string comes from the component's
 * own `TOOLBAR_CONTROL_LABELS` table, and every id and count from the plan's
 * `named-sets.json`, so the copy and the canon each have exactly one home.
 */

import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement, type ReactElement } from 'react'
import { afterEach, describe, expect, it, type Mock, vi } from 'vitest'

import type * as QueueToolbarModule from '../../src/renderer/src/components/queue/QueueToolbar'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')
const planDir = resolve(repoRoot, 'docs/execution/plans/2026-09-02-p10-queue-card-migration')

type NamedSet<T> = { value: T }
type NamedSets = {
  TOOLBAR_CONTROLS: NamedSet<string[]>
  QUEUE_OVERFLOW_MENU: NamedSet<string[]>
  NEW_TESTIDS: NamedSet<string[]>
}

const SETS = JSON.parse(readFileSync(resolve(planDir, 'named-sets.json'), 'utf-8')) as NamedSets

const TOOLBAR_CONTROLS = SETS.TOOLBAR_CONTROLS.value
const QUEUE_OVERFLOW_MENU = SETS.QUEUE_OVERFLOW_MENU.value
const NEW_TESTIDS = SETS.NEW_TESTIDS.value

const QUEUE_COMPONENTS = '../../src/renderer/src/components/queue'

function loadToolbar(): Promise<typeof QueueToolbarModule> {
  return import(/* @vite-ignore */ `${QUEUE_COMPONENTS}/QueueToolbar`) as Promise<
    typeof QueueToolbarModule
  >
}

// ---------------------------------------------------------------------------
// Rendering — Testing Library `render`/`screen`. One tree is mounted at a time,
// so the document-wide `screen` queries below are unambiguous; assertions that
// depend on *where* an element sits keep their scope through `within`.
// ---------------------------------------------------------------------------

let currentUnmount: (() => void) | null = null

function mount(element: ReactElement): void {
  currentUnmount = render(element).unmount
}

function unmount(): void {
  currentUnmount?.()
  currentUnmount = null
}

afterEach(() => {
  unmount()
  vi.restoreAllMocks()
})

const INTERACTIVE = 'button, [role="button"], [role="menuitem"], a[href], input, select, textarea'

function interactiveIn(scope: ParentNode): HTMLElement[] {
  return Array.from(scope.querySelectorAll<HTMLElement>(INTERACTIVE))
}

/** Handlers every case supplies, so an unfired one is an observable failure. */
function handlers(): {
  onStart: Mock<(...args: unknown[]) => void>
  onPauseResume: Mock<(...args: unknown[]) => void>
  onClearFinished: Mock<(...args: unknown[]) => void>
  onClearAll: Mock<(...args: unknown[]) => void>
} {
  return {
    onStart: vi.fn(),
    onPauseResume: vi.fn(),
    onClearFinished: vi.fn(),
    onClearAll: vi.fn(),
  }
}

describe('MEU-45 QueueToolbar', () => {
  it('AC-45.3 the toolbar renders exactly TOOLBAR_CONTROLS with persistent labels', async () => {
    const { QueueToolbar, TOOLBAR_CONTROL_LABELS } = await loadToolbar()
    const user = userEvent.setup()
    const spies = handlers()
    mount(createElement(QueueToolbar, { processorState: 'Processing', ...spies }))

    const toolbar = screen.getByTestId('queue-toolbar')
    const controls = interactiveIn(toolbar)
    expect(TOOLBAR_CONTROLS).toHaveLength(4)
    expect(controls, 'exactly TOOLBAR_CONTROLS interactive elements').toHaveLength(
      TOOLBAR_CONTROLS.length,
    )

    // Every control is icon + persistent text label (TOOLBAR_LABEL_RULE).
    const expectedLabels = [
      TOOLBAR_CONTROL_LABELS.start,
      TOOLBAR_CONTROL_LABELS.pause,
      TOOLBAR_CONTROL_LABELS['clear-finished'],
      TOOLBAR_CONTROL_LABELS['queue-overflow'],
    ]
    controls.forEach((control, index) => {
      expect(control.querySelector('svg'), `control ${index} renders an icon`).not.toBeNull()
      expect(control.textContent?.trim(), `control ${index} renders a text label`).toBe(
        expectedLabels[index],
      )
    })

    // The testids are the canonical NEW_TESTIDS, in TOOLBAR_CONTROLS order.
    const ids = controls.map((control) => control.dataset.testid ?? '')
    expect(ids).toEqual([
      'queue-toolbar-start',
      'queue-toolbar-pause',
      'queue-toolbar-clear-finished',
      'queue-toolbar-overflow',
    ])
    for (const id of ids) {
      expect(NEW_TESTIDS, `${id} is a registered NEW_TESTID`).toContain(id)
    }

    await user.click(within(toolbar).getByTestId('queue-toolbar-start'))
    expect(spies.onStart).toHaveBeenCalledTimes(1)
    await user.click(within(toolbar).getByTestId('queue-toolbar-clear-finished'))
    expect(spies.onClearFinished).toHaveBeenCalledTimes(1)
  })

  it('AC-45.3 pause-resume is one button whose label and testid follow PAUSE_SCOPE', async () => {
    const { QueueToolbar, TOOLBAR_CONTROL_LABELS } = await loadToolbar()
    const user = userEvent.setup()

    const cases = [
      { state: 'Idle', testId: 'queue-toolbar-pause', label: TOOLBAR_CONTROL_LABELS.pause },
      { state: 'Processing', testId: 'queue-toolbar-pause', label: TOOLBAR_CONTROL_LABELS.pause },
      { state: 'Paused', testId: 'queue-toolbar-resume', label: TOOLBAR_CONTROL_LABELS.resume },
    ] as const

    for (const { state, testId, label } of cases) {
      const spies = handlers()
      mount(createElement(QueueToolbar, { processorState: state, ...spies }))
      const toolbar = screen.getByTestId('queue-toolbar')

      // ONE button, never two: the sibling testid is absent, not merely hidden.
      expect(within(toolbar).getByTestId(testId).textContent?.trim(), `${state} label`).toBe(label)
      const sibling =
        testId === 'queue-toolbar-pause' ? 'queue-toolbar-resume' : 'queue-toolbar-pause'
      expect(within(toolbar).queryByTestId(sibling), `${state} renders no ${sibling}`).toBeNull()
      expect(interactiveIn(toolbar), `${state} control count`).toHaveLength(
        TOOLBAR_CONTROLS.length,
      )

      await user.click(within(toolbar).getByTestId(testId))
      expect(spies.onPauseResume, `${state} toggle fires`).toHaveBeenCalledTimes(1)
      unmount()
    }
  })

  it('AC-45.3 the overflow menu holds QUEUE_OVERFLOW_MENU outside the four controls', async () => {
    const { QueueToolbar, TOOLBAR_CONTROL_LABELS } = await loadToolbar()
    const user = userEvent.setup()
    const spies = handlers()
    mount(createElement(QueueToolbar, { processorState: 'Idle', ...spies }))
    const toolbar = screen.getByTestId('queue-toolbar')

    // Clear all is not a toolbar button — it exists only once the kebab opens.
    expect(screen.queryByTestId('queue-toolbar-clear-all')).toBeNull()

    await user.click(within(toolbar).getByTestId('queue-toolbar-overflow'))

    const clearAll = screen.getByTestId('queue-toolbar-clear-all')
    expect(QUEUE_OVERFLOW_MENU).toEqual(['clear-all'])
    expect(clearAll.textContent?.trim()).toBe(TOOLBAR_CONTROL_LABELS['clear-all'])

    // The open menu is a sibling of the control group, so the "exactly 4"
    // invariant survives the open state.
    expect(toolbar.contains(clearAll), 'menu is not inside [data-testid=queue-toolbar]').toBe(
      false,
    )
    expect(interactiveIn(toolbar), 'control count with the menu open').toHaveLength(
      TOOLBAR_CONTROLS.length,
    )

    await user.click(clearAll)
    expect(spies.onClearAll).toHaveBeenCalledTimes(1)
  })
})

/**
 * Regression — the overflow popup drifted to the page's right edge (G19).
 *
 * Reported against the running app: the "More" menu rendered flush with the
 * window's right edge, and left the frame entirely when the window was not
 * maximised. The popup is `absolute right-0`, so it resolves against its
 * nearest positioned ancestor — the wrapper that carries `relative`. Both queue
 * pages mount the toolbar as a direct child of a `flex flex-col` section, and a
 * column flex container stretches its items across the cross axis. `inline-flex`
 * does not save the wrapper: a flex item's display is blockified, so the wrapper
 * took the section's full width and `right-0` landed at the page edge.
 *
 * The anchor therefore has to opt out of that stretch. jsdom performs no layout
 * and loads no Tailwind, so the assertion is on the declared class: the element
 * the popup is positioned against must shrink-wrap its content.
 */
describe('queue toolbar overflow anchor', () => {
  it('anchors the overflow popup to a shrink-wrapped box, not a stretched flex item', async () => {
    const { QueueToolbar } = await loadToolbar()
    const user = userEvent.setup()
    const spies = handlers()

    // Mount inside a replica of the real page root so the wrapper is a flex
    // item exactly as it is in ConvertPage / DownloaderPage.
    mount(
      createElement(
        'section',
        { className: 'flex flex-col gap-4 p-4' },
        createElement(QueueToolbar, { processorState: 'Idle', ...spies }),
      ),
    )

    const toolbar = screen.getByTestId('queue-toolbar')
    await user.click(within(toolbar).getByTestId('queue-toolbar-overflow'))
    const menu = screen.getByTestId('queue-toolbar-clear-all').closest<HTMLElement>('[role="menu"]')
    expect(menu, 'the open menu is in the DOM').not.toBeNull()

    // Walk to the box `absolute right-0` actually resolves against.
    let anchor: HTMLElement | null = menu?.parentElement ?? null
    while (anchor !== null && !anchor.classList.contains('relative')) {
      anchor = anchor.parentElement
    }
    expect(anchor, 'the popup has a positioned ancestor').not.toBeNull()
    expect(anchor?.contains(toolbar), 'the anchor wraps the control group').toBe(true)
    expect(
      anchor?.classList.contains('self-start'),
      'the positioning anchor must not stretch to the column flex parent\'s width',
    ).toBe(true)
  })
})
