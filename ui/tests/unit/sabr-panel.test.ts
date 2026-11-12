/** @vitest-environment jsdom */

/**
 * MEU-138 — `SABR_SHOWN`: the text the `sabr-status` panel holds (AC-138.8).
 *
 * Each row of the contract, with a local time built from its parts, so the expected
 * `HH:MM:SS` does not depend on the machine's time zone.
 */

import { describe, expect, it } from 'vitest'

import { sabrResultText } from '../../src/renderer/src/features/downloader/sabr-panel'

const AT = new Date(2026, 10, 12, 9, 5, 7).toISOString()
const ACTIVE = 'SABR active — quality limited to 360p'

describe('MEU-138 sabrResultText', () => {
  it('AC-138.8 each snapshot gives its contract text', () => {
    const shown = {
      checking: sabrResultText({ mode: 'checking', source: null, checked_at: null }),
      activeChecked: sabrResultText({ mode: 'active', source: 'detected', checked_at: AT }),
      activeForced: sabrResultText({ mode: 'active', source: 'forced', checked_at: AT }),
      activeNoTime: sabrResultText({ mode: 'active', source: 'detected', checked_at: null }),
      activeBadTime: sabrResultText({ mode: 'active', source: 'forced', checked_at: 'not a time' }),
      inactiveChecked: sabrResultText({ mode: 'inactive', source: 'detected', checked_at: AT }),
      inactiveCleared: sabrResultText({ mode: 'inactive', source: null, checked_at: AT }),
      inactiveNoTime: sabrResultText({ mode: 'inactive', source: null, checked_at: null }),
      inactiveBadTime: sabrResultText({ mode: 'inactive', source: 'detected', checked_at: 'soon' }),
      none: sabrResultText(undefined),
    }
    expect(shown).toEqual({
      checking: 'Checking…',
      activeChecked: `${ACTIVE} · checked 09:05:07`,
      activeForced: `${ACTIVE} · forced 09:05:07`,
      activeNoTime: ACTIVE,
      activeBadTime: ACTIVE,
      inactiveChecked: 'SABR inactive · checked 09:05:07',
      inactiveCleared: 'SABR inactive · cleared 09:05:07',
      inactiveNoTime: 'SABR not checked',
      inactiveBadTime: 'SABR not checked',
      none: 'SABR not checked',
    })
  })

  it('AC-138.8 the time is zero-padded local time', () => {
    const early = new Date(2026, 0, 2, 0, 0, 1).toISOString()
    const late = new Date(2026, 0, 2, 23, 59, 59).toISOString()
    expect([
      sabrResultText({ mode: 'inactive', source: 'detected', checked_at: early }),
      sabrResultText({ mode: 'active', source: 'forced', checked_at: late }),
    ]).toEqual(['SABR inactive · checked 00:00:01', `${ACTIVE} · forced 23:59:59`])
  })
})
