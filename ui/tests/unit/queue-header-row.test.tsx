/** @vitest-environment jsdom */

import { cleanup, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement, type ComponentType } from 'react'
import { afterEach, describe, expect, it, vi } from 'vitest'

type HeaderProps = {
  total: number
  selectedCount: number
  onToggleAll: (checked: boolean) => void
  selectionAriaLabel: string
  statuses: readonly string[]
  counts: Readonly<Record<string, number>>
  summaryTestId: string
  processorTestId: string
  processorLabel: string | null
  toolbar: {
    processorState: string
    label: string
    canStart: boolean
    canPauseResume: boolean
    canClearFinished: boolean
    canClearAll: boolean
    onStart: () => void
    onPauseResume: () => void
    onClearFinished: () => void
    onClearAll: () => void
  }
}

const modules = import.meta.glob('../../src/renderer/src/components/queue/QueueHeaderRow.tsx')

async function loadHeader(): Promise<ComponentType<HeaderProps>> {
  expect(Object.keys(modules), 'AC-52.1 one shared component exists for both pages').toHaveLength(1)
  const loaded = await Object.values(modules)[0]() as {
    QueueHeaderRow: ComponentType<HeaderProps>
  }
  expect(loaded.QueueHeaderRow).toBeTypeOf('function')
  return loaded.QueueHeaderRow
}

function props(overrides: Partial<HeaderProps> = {}): HeaderProps {
  return {
    total: 3,
    selectedCount: 0,
    onToggleAll: vi.fn(),
    selectionAriaLabel: 'Select all downloads',
    statuses: ['Pending', 'Downloading', 'Done', 'Failed'],
    counts: { Pending: 2, Downloading: 1, Done: 0, Failed: 0 },
    summaryTestId: 'queue-summary',
    processorTestId: 'processor-indicator',
    processorLabel: 'Processing',
    toolbar: {
      processorState: 'Processing',
      label: 'Download queue actions',
      canStart: true,
      canPauseResume: true,
      canClearFinished: false,
      canClearAll: true,
      onStart: vi.fn(),
      onPauseResume: vi.fn(),
      onClearFinished: vi.fn(),
      onClearAll: vi.fn(),
    },
    ...overrides,
  }
}

afterEach(() => cleanup())

describe('MEU-52 shared QueueHeaderRow', () => {
  it('AC-52.1/.2/.4 composes real select-all, nonzero chips, full-count More, and four live toolbar controls', async () => {
    const Header = await loadHeader()
    const input = props()
    const user = userEvent.setup()
    render(createElement(Header, input))

    const header = screen.getByTestId('queue-header-row')
    const selection = within(header).getByTestId('queue-selection-header')
    const selectAll = within(selection).getByTestId('queue-select-all')
    expect(selectAll.tagName).toBe('INPUT')
    await user.click(selectAll)
    expect(input.onToggleAll).toHaveBeenCalledExactlyOnceWith(true)

    const chips = within(header).getByTestId('queue-summary')
    expect(chips.querySelectorAll('[data-tone]')).toHaveLength(2)
    expect(chips).toHaveTextContent('Pending')
    expect(chips).toHaveTextContent('Downloading')
    expect(chips).not.toHaveTextContent('Failed')
    expect(chips).not.toHaveTextContent('Done')

    const more = within(header).getByTestId('queue-status-more')
    expect(more.tagName).toBe('BUTTON')
    expect(more).toHaveAttribute('aria-expanded', 'false')
    await user.click(more)
    expect(more).toHaveAttribute('aria-expanded', 'true')
    const details = within(header).getByTestId('queue-status-details')
    for (const label of ['Pending', 'Downloading', 'Done', 'Failed']) {
      expect(details).toHaveTextContent(label)
    }
    expect(details).toHaveTextContent('Done: 0')

    const toolbar = within(header).getByTestId('queue-toolbar')
    expect(toolbar.querySelectorAll('button')).toHaveLength(4)
    await user.click(within(toolbar).getByTestId('queue-toolbar-start'))
    expect(input.toolbar.onStart).toHaveBeenCalledTimes(1)
    expect(input.toolbar.onClearFinished).not.toHaveBeenCalled()
  })

  it('AC-52.3 preserves the processor caller ID on a live text chip and leaves Idle without a live chip', async () => {
    const Header = await loadHeader()
    const input = props()
    const view = render(createElement(Header, input))
    const live = screen.getByTestId('processor-indicator')
    expect(live).toHaveAttribute('data-tone')
    expect(live).toHaveTextContent('Processing')

    view.rerender(createElement(Header, props({
      processorLabel: null,
      toolbar: { ...input.toolbar, processorState: 'Idle' },
    })))
    const idle = screen.getByTestId('processor-indicator')
    expect(idle).not.toHaveAttribute('data-tone')
    expect(idle).not.toBeVisible()
    expect(screen.getByTestId('queue-toolbar-pause')).toBeInTheDocument()
  })
})
