/** @vitest-environment jsdom */

/**
 * MEU-55 shared-component extensions (AC-55.1, AC-55.2).
 *
 * New exports and props are reached through dynamic imports inside each test so
 * that, before implementation, an absent export fails the test that needs it
 * rather than the whole suite.
 */
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { cleanup, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement, type ComponentType, type ReactNode } from 'react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { HEADER_ROW_CASE, SLOTLESS_CARD_CASES } from './fixtures/queue-slot-baseline-cases'

const here = dirname(fileURLToPath(import.meta.url))
const baseline = JSON.parse(
  readFileSync(resolve(here, 'fixtures/queue-slot-baseline.json'), 'utf8'),
) as Record<string, string>
const uiSrc = resolve(here, '../../src/renderer/src')

type MenuItem = { id: string; label: string; destructive: boolean; disabled?: boolean; testId?: string; run: () => void }

async function loadCard(): Promise<ComponentType<Record<string, unknown>>> {
  const mod = (await import('../../src/renderer/src/components/queue/QueueCard')) as unknown as {
    QueueCard: ComponentType<Record<string, unknown>>
  }
  return mod.QueueCard
}

afterEach(() => {
  cleanup()
})

describe('MEU-55 CARD_SLOTS, MENU_ITEM_EXTENSION, LIST_SLOT_RESOLVER, PROGRESS_TONE', () => {
  it('AC-55.1 a card with no slot renders the exact pre-change markup', async () => {
    const QueueCard = await loadCard()
    for (const [name, props] of Object.entries(SLOTLESS_CARD_CASES)) {
      const { container, unmount } = render(createElement(QueueCard, props as Record<string, unknown>))
      expect(container.innerHTML, `baseline ${name}`).toBe(baseline[name])
      unmount()
    }
  })

  it('AC-55.1 trailing controls and the region are siblings, never nested', async () => {
    const QueueCard = await loadCard()
    render(
      createElement(QueueCard, {
        job: { id: 'c1', position: 1, status: 'Done', title: 'Channel One' },
        regionLabel: 'Select channel Channel One',
        onOpen: vi.fn(),
        metaContent: createElement('span', { 'data-testid': 'slot-meta' }, 'meta'),
        detailContent: createElement('span', { 'data-testid': 'slot-detail' }, 'detail'),
        trailingControls: createElement('button', { type: 'button', 'data-testid': 'slot-trailing' }, 'Go'),
      }),
    )
    const region = screen.getByRole('button', { name: 'Select channel Channel One' })
    const trailing = screen.getByTestId('slot-trailing')
    expect(region.contains(trailing), 'trailing control nested inside the role=button region').toBe(false)
    expect(region.contains(screen.getByTestId('slot-meta'))).toBe(true)
    expect(region.contains(screen.getByTestId('slot-detail'))).toBe(true)
    const card = screen.getByTestId('queue-card')
    expect(trailing.parentElement).toBe(card)
    // The replaced meta line no longer carries the shared text meta.
    expect(within(card).queryByText('0 B')).toBeNull()
  })

  it('AC-55.1 caller menu items render in order with their data-testid and onMenuOpen fires', async () => {
    const user = userEvent.setup()
    const QueueCard = await loadCard()
    const onMenuOpen = vi.fn()
    const compile = vi.fn()
    const items: MenuItem[] = [
      { id: 'compile', label: 'Compile (3 done)', destructive: false, testId: 'compile-btn', run: compile },
      { id: 'open-folder', label: 'Open folder', destructive: false, testId: 'open-folder-btn', run: vi.fn() },
      { id: 'remove', label: 'Remove…', destructive: true, testId: 'remove-btn', run: vi.fn() },
    ]
    render(
      createElement(QueueCard, {
        job: { id: 'c1', position: 1, status: 'Done', title: 'Channel One' },
        menuItems: items,
        onMenuOpen,
        // Download handlers are ignored once caller items are supplied.
        onOpenFile: vi.fn(),
      }),
    )
    await user.click(screen.getByTestId('queue-card-kebab'))
    expect(onMenuOpen).toHaveBeenCalledTimes(1)
    const menu = screen.getByTestId('queue-card-menu')
    const rendered = within(menu).getAllByRole('menuitem')
    expect(rendered.map((node) => node.getAttribute('data-testid'))).toEqual([
      'compile-btn',
      'open-folder-btn',
      'remove-btn',
    ])
    expect(rendered.map((node) => node.textContent)).toEqual(['Compile (3 done)', 'Open folder', 'Remove…'])
    await user.click(within(menu).getByTestId('compile-btn'))
    expect(compile).toHaveBeenCalledTimes(1)
  })

  it('AC-55.1 the list forwards cardSlots per row', async () => {
    const mod = (await import('../../src/renderer/src/components/queue/QueueList')) as unknown as {
      QueueList: ComponentType<Record<string, unknown>>
    }
    render(
      createElement(mod.QueueList, {
        items: [
          { id: 'a', position: 1, status: 'Done', title: 'A' },
          { id: 'b', position: 2, status: 'Failed', title: 'B' },
        ],
        rowTestId: 'channel-card',
        cardSlots: (job: { id: string }) => ({
          regionLabel: `Select channel ${job.id}`,
          trailingControls: createElement('span', { 'data-testid': `trail-${job.id}` }, job.id),
        }),
        onOpen: vi.fn(),
      }),
    )
    const cards = screen.getAllByTestId('channel-card')
    expect(cards).toHaveLength(2)
    expect(within(cards[0]).getByTestId('trail-a')).toBeTruthy()
    expect(within(cards[1]).getByTestId('trail-b')).toBeTruthy()
    expect(screen.getByRole('button', { name: 'Select channel b' })).toBeTruthy()
  })

  it('AC-55.1 ProgressBar success tone swaps only the fill colour and stays transform-driven', async () => {
    const mod = (await import('../../src/renderer/src/components/ui/ProgressBar')) as unknown as {
      ProgressBar: ComponentType<Record<string, unknown>>
    }
    const tokens = (await import('../../src/renderer/src/lib/queue/status-tokens')) as unknown as {
      PROGRESS_FILL_CLASSES?: Record<string, string>
    }
    expect(tokens.PROGRESS_FILL_CLASSES).toEqual({ accent: 'bg-accent', success: 'bg-accent-green' })
    const { container, rerender } = render(createElement(mod.ProgressBar, { value: 0.5, testId: 'p' }))
    const fill = (): HTMLElement => container.querySelector('[data-progress-fill]') as HTMLElement
    const accentClass = fill().className
    expect(accentClass.split(' ')).toContain('bg-accent')
    rerender(createElement(mod.ProgressBar, { value: 0.5, testId: 'p', tone: 'success' }))
    expect(fill().className.split(' ')).toContain('bg-accent-green')
    expect(fill().className.split(' ')).not.toContain('bg-accent')
    expect(fill().className.replace('bg-accent-green', 'bg-accent')).toBe(accentClass)
    expect(fill().style.transform).toBe('scaleX(0.5)')
    expect(fill().style.width).toBe('')
  })
})

describe('MEU-55 HEADER_FRAME', () => {
  it('AC-55.2 QueueHeaderRow still renders the exact pre-change markup', async () => {
    const mod = (await import('../../src/renderer/src/components/queue/QueueHeaderRow')) as unknown as {
      QueueHeaderRow: ComponentType<typeof HEADER_ROW_CASE>
    }
    const { container } = render(createElement(mod.QueueHeaderRow, HEADER_ROW_CASE))
    expect(container.innerHTML).toBe(baseline.header)
  })

  it('AC-55.2 QueueHeaderFrame renders title, chips, extra chips and actions with no checkbox unless given', async () => {
    const mod = (await import('../../src/renderer/src/components/queue/QueueHeaderRow')) as unknown as {
      QueueHeaderFrame?: ComponentType<{
        title?: string
        leading?: ReactNode
        statuses: readonly string[]
        counts: Readonly<Record<string, number>>
        summaryTestId: string
        processorTestId: string
        processorLabel: string | null
        extraChips?: ReactNode
        actions: ReactNode
      }>
    }
    expect(mod.QueueHeaderFrame, 'QueueHeaderFrame export').toBeTypeOf('function')
    const Frame = mod.QueueHeaderFrame as NonNullable<typeof mod.QueueHeaderFrame>
    render(
      createElement(Frame, {
        title: 'Channels',
        statuses: ['Pending', 'Processing', 'Done'],
        counts: { Pending: 0, Processing: 1, Done: 2 },
        summaryTestId: 'transcript-queue-summary',
        processorTestId: 'processor-indicator',
        processorLabel: null,
        extraChips: createElement('span', { 'data-testid': 'extra-chip' }, 'x'),
        actions: createElement('button', { type: 'button', 'data-testid': 'frame-action' }, 'Start'),
      }),
    )
    const row = screen.getByTestId('queue-header-row')
    expect(within(row).getByRole('heading', { name: 'Channels' })).toBeTruthy()
    expect(within(row).queryByRole('checkbox')).toBeNull()
    const summary = within(row).getByTestId('transcript-queue-summary')
    expect(summary.textContent).toContain('Processing')
    expect(summary.textContent).not.toContain('Pending')
    const processor = within(row).getByTestId('processor-indicator')
    expect(processor.hidden).toBe(true)
    expect(within(row).getByTestId('extra-chip')).toBeTruthy()
    expect(within(row).getByTestId('frame-action')).toBeTruthy()
  })

  it('AC-55.2 SOURCE_PINS: header, card and progress sources keep their pinned text', () => {
    const header = readFileSync(resolve(uiSrc, 'components/queue/QueueHeaderRow.tsx'), 'utf8')
    for (const pin of [
      '<QueueSelectionHeader',
      'total={total}',
      'selectedCount={selectedCount}',
      'onToggleAll={onToggleAll}',
      'flex flex-wrap items-center',
      'data-testid={summaryTestId}',
      '<QueueToolbar {...toolbar} />',
      "from './QueueToolbar'",
      'export function QueueHeaderFrame',
    ]) {
      expect(header, pin).toContain(pin)
    }
    const card = readFileSync(resolve(uiSrc, 'components/queue/QueueCard.tsx'), 'utf8')
    const cancelProps = new Set(Array.from(card.matchAll(/on[A-Za-z]*Cancel[A-Za-z]*/g)).map((m) => m[0]))
    expect(cancelProps).toEqual(new Set(['onCancelQueue']))
    const progress = readFileSync(resolve(uiSrc, 'components/ui/ProgressBar.tsx'), 'utf8')
    expect(progress).toContain('PROGRESS_FILL_CLASSES')
    expect(progress).not.toMatch(/['"`]bg-accent-green['"`]/)
  })
})
