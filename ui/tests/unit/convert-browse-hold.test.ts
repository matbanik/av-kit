/** @vitest-environment jsdom */

/**
 * MEU-157 (Session 89) — Ctrl+O's Browse request waits for the Convert page.
 *
 * The page is a lazy chunk, so a Ctrl+O pressed on the way to Convert used to
 * dispatch its browse event before the page listened, and the request was lost
 * (06 §Convert browse waits for the page, D-1101, D-1108). `convert-commands.ts`
 * now keeps one outstanding request (`BROWSE_HOLD`): a request that nobody
 * receives is held until the page takes it on mount (`takeHeldBrowse`), a
 * request the page receives is not held (`BROWSE_ACK`), and leaving Convert
 * drops it (`BROWSE_DROP`).
 *
 * Each test asserts `typeof cc.takeHeldBrowse === 'function'` first, so a
 * missing export fails by assertion, not by a type error.
 *
 * AC-157.6, AC-157.7 and AC-157.14 render the page and live in
 * `convert-page.behavior.test.ts`; AC-157.8 to AC-157.11 are Electron tests.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import * as cc from '../../src/renderer/src/features/converter/convert-commands'

const listeners: EventListener[] = []

function listen(listener: (event: Event) => void): void {
  const wrapped: EventListener = (event) => listener(event)
  listeners.push(wrapped)
  window.addEventListener(cc.CONVERT_BROWSE_EVENT, wrapped)
}

function expectTakeExported(): void {
  expect(typeof cc.takeHeldBrowse, 'takeHeldBrowse is exported from convert-commands').toBe('function')
}

/** Two real animation frames: `navigateAndDeliver` runs its request after two. */
async function twoFrames(): Promise<void> {
  await new Promise<void>((done) => {
    window.requestAnimationFrame(() => {
      window.requestAnimationFrame(() => {
        done()
      })
    })
  })
}

beforeEach(() => {
  window.location.hash = '#/convert'
})

afterEach(() => {
  for (const listener of listeners.splice(0)) {
    window.removeEventListener(cc.CONVERT_BROWSE_EVENT, listener)
  }
  if (typeof cc.takeHeldBrowse === 'function') {
    cc.takeHeldBrowse()
  }
  vi.restoreAllMocks()
  window.location.hash = '#/'
})

describe('MEU-157 a Browse request waits for the Convert page', () => {
  it('AC-157.1 a request that no page receives is held, and is taken once', async () => {
    expectTakeExported()
    cc.deliverPaletteBrowse()
    await twoFrames()
    expect(cc.takeHeldBrowse(), 'the request is held for the page').toBe(true)
    expect(cc.takeHeldBrowse(), 'a held request is taken once').toBe(false)
  })

  it('AC-157.2 a request the page receives is delivered once and not held', async () => {
    expectTakeExported()
    let received = 0
    listen((event) => {
      received += 1
      event.preventDefault()
    })
    cc.deliverPaletteBrowse()
    await twoFrames()
    expect(received, 'the listening page receives the request once').toBe(1)
    expect(cc.takeHeldBrowse(), 'a delivered request is not held').toBe(false)
  })

  it('AC-157.3 a held request is dropped when the user leaves Convert', async () => {
    expectTakeExported()
    cc.deliverPaletteBrowse()
    await twoFrames()
    window.location.hash = '#/'
    window.dispatchEvent(new HashChangeEvent('hashchange'))
    expect(cc.takeHeldBrowse(), 'no request survives leaving Convert').toBe(false)
  })

  it('AC-157.4 a request whose frames run off Convert is not held', async () => {
    expectTakeExported()
    cc.deliverPaletteBrowse()
    window.location.hash = '#/'
    await twoFrames()
    expect(cc.takeHeldBrowse(), 'nothing is held off Convert').toBe(false)
  })

  it('AC-157.5 two presses before the mount are one request, and no frame delivers it after the page took it', () => {
    expectTakeExported()
    const frames: FrameRequestCallback[] = []
    vi.spyOn(window, 'requestAnimationFrame').mockImplementation((callback) => {
      frames.push(callback)
      return frames.length
    })
    /** Runs the callbacks queued before this frame; new ones wait for the next. */
    const frame = (): void => {
      for (const callback of frames.splice(0)) {
        callback(performance.now())
      }
    }

    cc.deliverPaletteBrowse()
    frame()
    cc.deliverPaletteBrowse()
    frame()

    // A stand-in mount, as the page does it: listen first, then take.
    let received = 0
    listen((event) => {
      received += 1
      event.preventDefault()
    })
    expect(cc.takeHeldBrowse(), 'the mount takes the one outstanding request').toBe(true)
    frame()
    frame()
    expect(received, 'no frame delivers a request the page already took').toBe(0)
    expect(cc.takeHeldBrowse(), 'nothing is left to take').toBe(false)
  })
})
