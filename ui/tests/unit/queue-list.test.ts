/** @vitest-environment jsdom */

/**
 * MEU-45 — `QueueList` empty state and drop targets (AC-45.19, AC-45.19a).
 *
 * Today `QueueList` returns a bare `<div>` with only a hover overlay when
 * `items` is empty, so migrating the converter onto it would replace the table's
 * empty-state row with a blank panel. `EMPTY_STATE_CONTRACT` closes that hole —
 * and does it **per page**, because the two queues have different intake
 * contracts:
 *
 * - **Converter (file intake).** Empty → `EmptyDropZone` under the canonical ids
 *   `queue-empty-dropzone` / `queue-empty-browse`. Non-empty → the list plus the
 *   compact `queue-drop-strip`.
 * - **Downloader (URL intake).** There is no local-file intake path and Phase 10
 *   adds no REST surface, so the host supplies its own empty slot instead and
 *   `QueueList` must render **no** file-drop invitation at all (AC-45.19a — the
 *   round-2 F12 defect).
 *
 * The Browse control is asserted as a real, named `<button>` rather than by its
 * exact label: `EmptyDropZone` is not in this MEU's Files Modified, so the copy
 * it owns stays its own. The spec's headline microcopy *is* pinned, because that
 * string is what `QueueList` passes in.
 */

import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement, type ReactElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import type * as QueueListModule from '../../src/renderer/src/components/queue/QueueList'

/** Spec microcopy — docs/build-plan/10-queue-card-ui.md §Empty state and drop targets. */
const EMPTY_HEADLINE = 'Drop video or audio files here'

const QUEUE_COMPONENTS = '../../src/renderer/src/components/queue'

function loadList(): Promise<typeof QueueListModule> {
  return import(/* @vite-ignore */ `${QUEUE_COMPONENTS}/QueueList`) as Promise<
    typeof QueueListModule
  >
}

/**
 * Each spec mounts one tree at a time and unmounts it before the next, so the
 * document-wide `screen` queries below are never ambiguous.
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

beforeEach(() => {
  currentUnmount = null
})

afterEach(() => {
  unmount()
  vi.restoreAllMocks()
})

function job(id: string, position: number): {
  id: string
  position: number
  status: string
  title: string
} {
  return { id, position, status: 'Pending', title: `Clip ${id}` }
}

/** jsdom has no DragEvent carrying a DataTransfer; the payload is attached. */
function fireDrop(el: Element, files: File[]): void {
  const event = new Event('drop', { bubbles: true, cancelable: true })
  Object.defineProperty(event, 'dataTransfer', {
    value: {
      items: files.map((file) => ({ kind: 'file', type: file.type })),
      files,
      types: ['Files'],
      dropEffect: 'copy',
      effectAllowed: 'copy',
    },
  })
  act(() => {
    el.dispatchEvent(event)
  })
}

describe('MEU-45 QueueList empty state', () => {
  it('AC-45.19 QueueList renders EmptyDropZone when empty and the drop strip when not', async () => {
    const { QueueList } = await loadList()
    const user = userEvent.setup()
    const onBrowse = vi.fn()
    const onDropFiles = vi.fn()

    // --- Empty: the invitation, not a blank panel -------------------------
    mount(createElement(QueueList, { items: [], onBrowse, onDropFiles, testId: 'convert-queue' }))
    const zone = screen.getByTestId('queue-empty-dropzone')
    expect(zone.textContent, 'spec headline microcopy').toContain(EMPTY_HEADLINE)

    // Browse is an equal path, not a decoration: a real button in the tab order.
    const browse = screen.getByTestId('queue-empty-browse')
    expect(browse.tagName).toBe('BUTTON')
    expect(browse.textContent?.trim().length, 'the browse control is named').toBeGreaterThan(0)
    expect(browse.textContent).toMatch(/Browse/i)
    await user.click(browse)
    expect(onBrowse, 'browse routes to the host picker, never a no-op').toHaveBeenCalledTimes(1)

    // Dropping onto the empty zone routes to the same host intake.
    fireDrop(zone, [new File(['x'], 'a.mp4', { type: 'video/mp4' })])
    expect(onDropFiles).toHaveBeenCalledTimes(1)

    // The non-empty strip is absent while the queue is empty.
    expect(screen.queryByTestId('queue-drop-strip')).toBeNull()
    unmount()

    // --- Non-empty: the list plus the compact strip ------------------------
    mount(
      createElement(QueueList, {
        items: [job('a', 1), job('b', 2)],
        onBrowse,
        onDropFiles,
        testId: 'convert-queue',
        rowTestId: 'convert-queue-row',
      }),
    )
    expect(screen.getAllByTestId('convert-queue-row')).toHaveLength(2)
    expect(
      screen.queryByTestId('queue-empty-dropzone'),
      'no invitation over a full queue',
    ).toBeNull()

    const strip = screen.getByTestId('queue-drop-strip')
    expect(strip.textContent?.trim().length, 'the strip names the affordance').toBeGreaterThan(0)
    fireDrop(strip, [new File(['x'], 'b.mp4', { type: 'video/mp4' })])
    expect(onDropFiles, 'the strip drops into the same intake').toHaveBeenCalledTimes(2)
  })

  it('AC-45.19a a host-supplied empty slot replaces EmptyDropZone entirely', async () => {
    const { QueueList } = await loadList()
    const onBrowse = vi.fn()

    // The downloader's case: a URL-intake queue supplies its own invitation.
    const hostSlot = createElement(
      'div',
      { 'data-testid': 'queue-empty-invite' },
      'Paste a video link above to queue a download',
    )
    mount(createElement(QueueList, { items: [], emptyState: hostSlot }))

    expect(screen.getByTestId('queue-empty-invite')).not.toBeNull()
    expect(
      screen.queryByTestId('queue-empty-dropzone'),
      'no file-drop invitation is forced onto a URL-intake queue',
    ).toBeNull()
    expect(screen.queryByTestId('queue-empty-browse')).toBeNull()
    unmount()

    // The slot wins even when a browse handler is also supplied — the host, not
    // the component, decides what an empty queue says.
    mount(createElement(QueueList, { items: [], onBrowse, emptyState: hostSlot }))
    expect(screen.getByTestId('queue-empty-invite')).not.toBeNull()
    expect(screen.queryByTestId('queue-empty-dropzone')).toBeNull()
    unmount()

    // And a queue with no file intake at all renders no drop strip either.
    mount(createElement(QueueList, { items: [job('a', 1)], emptyState: hostSlot }))
    expect(screen.queryByTestId('queue-drop-strip')).toBeNull()
    expect(screen.getAllByTestId('queue-card')).toHaveLength(1)
  })
})
