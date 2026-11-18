/** @vitest-environment jsdom */

import { act, cleanup, render, within } from '@testing-library/react'
import { StrictMode } from 'react'
import { afterEach, describe, expect, it } from 'vitest'

import { HelpCard } from '../../src/renderer/src/components/help/HelpCard'
import * as sc from '../../src/renderer/src/features/settings/settings-commands'
import * as nav from '../../src/renderer/src/lib/shell-nav'

/*
  MEU-158 (Session 94, D-1175, D-1176): an F1 pressed while a lazy page's chunk
  loads is held for that page's route and taken once by the page's HelpCard
  when it mounts. The new names are reached through the module namespaces and
  each test that needs one asserts its type first, so a Red fails by assertion,
  never by a missing export (Session 52 RULE-4). AC-158.7 is the guard and
  asserts no new name.
*/

const SECTIONS = [{ id: 'one', title: 'Help topic', body: 'Help body.' }]
const DRAIN_KEYS = ['/', '/convert', '/capture', '/transcript', '/tts', '/settings', '/x', '/y']

type Feature = 'downloader' | 'converter'

function setHash(hash: string, dispatch: boolean): void {
  window.location.hash = hash
  if (dispatch) {
    window.dispatchEvent(new HashChangeEvent('hashchange'))
  }
}

function renderCard(feature: Feature): HTMLElement {
  const { container } = render(
    <StrictMode>
      <HelpCard feature={feature} tabKey="main" sections={SECTIONS} />
    </StrictMode>,
  )
  return container
}

function expandedOf(container: HTMLElement): string | null {
  return within(container).getByRole('button', { name: /How it works/ }).getAttribute('aria-expanded')
}

function toggle(): void {
  act(() => {
    sc.HELP_COMMANDS.toggle()
  })
}

function resetBetweenParts(): void {
  cleanup()
  if (typeof sc.takeHeldHelpToggle === 'function') {
    for (const key of DRAIN_KEYS) {
      sc.takeHeldHelpToggle(key)
    }
  }
  localStorage.clear()
  sessionStorage.clear()
}

describe('MEU-158 F1 held until the page mounts', () => {
  afterEach(() => {
    resetBetweenParts()
    setHash('', false)
  })

  it('AC-158.1 createHeldRequest joins, holds, takes once and clears on settle false', () => {
    setHash('#/x', false)
    expect(typeof nav.createHeldRequest).toBe('function')
    const held = nav.createHeldRequest(() => true)
    const token = held.begin('/x')
    expect(token).not.toBeNull()
    expect(held.begin('/x')).toBeNull()
    held.settle(token as NonNullable<typeof token>, true)
    expect(held.take('/x')).toBe(true)
    expect(held.take('/x')).toBe(false)

    const second = held.begin('/x')
    expect(second).not.toBeNull()
    held.settle(second as NonNullable<typeof second>, false)
    expect(held.take('/x')).toBe(false)
  })

  it('AC-158.2 createHeldRequest drops on leaving, replaces another key, ignores a stale settle; currentRoute', () => {
    setHash('#/x', false)
    expect(typeof nav.createHeldRequest).toBe('function')

    const onRoute = nav.createHeldRequest((key) => nav.currentRoute() === key)
    const token = onRoute.begin('/x')
    expect(token).not.toBeNull()
    onRoute.settle(token as NonNullable<typeof token>, true)
    setHash('#/y', true)
    expect(onRoute.take('/x')).toBe(false)
    setHash('#/x', true)
    expect(onRoute.take('/x')).toBe(false)

    const always = nav.createHeldRequest(() => true)
    const old = always.begin('/x')
    expect(old).not.toBeNull()
    const replacement = always.begin('/y')
    expect(replacement).not.toBeNull()
    expect(always.isCurrent(old as NonNullable<typeof old>)).toBe(false)
    expect(always.isCurrent(replacement as NonNullable<typeof replacement>)).toBe(true)
    expect(always.take('/x')).toBe(false)
    always.settle(old as NonNullable<typeof old>, true)
    expect(always.take('/x')).toBe(false)
    expect(always.take('/y')).toBe(true)

    setHash('', false)
    expect(nav.currentRoute()).toBe('/')
    setHash('#/convert?x=1', false)
    expect(nav.currentRoute()).toBe('/convert')
  })

  it('AC-158.3 an F1 with no card mounted toggles the converter card once when it mounts', () => {
    setHash('#/convert', false)
    expect(typeof sc.takeHeldHelpToggle).toBe('function')
    toggle()
    const card = renderCard('converter')
    expect(expandedOf(card)).toBe('true')
    expect(sc.takeHeldHelpToggle('/convert')).toBe(false)
  })

  it('AC-158.4 two F1 presses before the mount toggle once', () => {
    setHash('#/convert', false)
    expect(typeof sc.takeHeldHelpToggle).toBe('function')
    toggle()
    toggle()
    const card = renderCard('converter')
    expect(expandedOf(card)).toBe('true')
    expect(sc.takeHeldHelpToggle('/convert')).toBe(false)
  })

  it('AC-158.5 leaving the route before the mount drops the held F1', () => {
    setHash('#/convert', false)
    expect(typeof sc.takeHeldHelpToggle).toBe('function')
    toggle()
    setHash('#/', true)
    setHash('#/convert', true)
    const card = renderCard('converter')
    expect(expandedOf(card)).toBe('false')
    expect(sc.takeHeldHelpToggle('/convert')).toBe(false)
  })

  it('AC-158.6 a toggle reaches only the card for its route; a detail-less toggle reaches every card', () => {
    setHash('#/convert', false)
    expect(typeof sc.takeHeldHelpToggle).toBe('function')

    const downloaderOnConvert = renderCard('downloader')
    toggle()
    expect(expandedOf(downloaderOnConvert)).toBe('false')
    const converter = renderCard('converter')
    expect(expandedOf(converter)).toBe('true')
    expect(expandedOf(downloaderOnConvert)).toBe('false')
    resetBetweenParts()

    setHash('#/', true)
    const downloaderHome = renderCard('downloader')
    toggle()
    expect(expandedOf(downloaderHome)).toBe('true')
    resetBetweenParts()

    const bothDownloader = renderCard('downloader')
    const bothConverter = renderCard('converter')
    act(() => {
      window.dispatchEvent(new CustomEvent('av-kit:help:toggle-local'))
    })
    expect(expandedOf(bothDownloader)).toBe('true')
    expect(expandedOf(bothConverter)).toBe('true')
    resetBetweenParts()

    setHash('#/convert', true)
    toggle()
    const downloaderAfterHold = renderCard('downloader')
    expect(expandedOf(downloaderAfterHold)).toBe('false')
    expect(sc.takeHeldHelpToggle('/convert')).toBe(true)
  })

  it('AC-158.7 guard: an F1 a mounted card receives toggles at once and is never held', () => {
    setHash('#/convert', false)
    const card = renderCard('converter')
    toggle()
    expect(expandedOf(card)).toBe('true')
    if (typeof sc.takeHeldHelpToggle === 'function') {
      expect(sc.takeHeldHelpToggle('/convert')).toBe(false)
    }
    toggle()
    expect(expandedOf(card)).toBe('false')
  })
})
