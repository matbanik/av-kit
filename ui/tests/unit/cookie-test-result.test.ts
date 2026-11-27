/**
 * MEU-169 — `cookieTestResultText` (AC-169.8): the text the Test Cookies result line holds for each
 * reply (`COOKIE_TEST_SHOWN`). The module is found through `import.meta.glob`, so while it is
 * missing each test fails by assertion and not by an import error.
 */

import { describe, expect, it } from 'vitest'

type CookieTestReply = {
  ok: boolean
  outcome: 'ok' | 'unreadable' | 'check_failed' | null
  error_message: string | null
}

type ResultModule = { cookieTestResultText: (reply: CookieTestReply) => string }

const modules = import.meta.glob<ResultModule>('../../src/renderer/src/features/downloader/cookie-test-result.ts', {
  eager: true,
})

function resultText(): (reply: CookieTestReply) => string {
  const found = Object.values(modules)
  expect(found, 'AC-169.8 the cookie-test-result module exists').toHaveLength(1)
  return (found[0] as ResultModule).cookieTestResultText
}

describe('MEU-169 cookieTestResultText', () => {
  it('AC-169.8 each reply gives its text', () => {
    const text = resultText()
    expect([
      text({ ok: true, outcome: 'ok', error_message: null }),
      text({ ok: false, outcome: 'unreadable', error_message: 'cookie file is missing' }),
      text({ ok: false, outcome: 'check_failed', error_message: 'Sign in to confirm you are not a bot' }),
      text({ ok: true, outcome: null, error_message: null }),
    ]).toEqual([
      'Cookies read. YouTube answered.',
      'Could not read the cookies: cookie file is missing',
      "Cookies read, but YouTube's check failed: Sign in to confirm you are not a bot",
      'Cookie mode is None. Nothing to test.',
    ])
  })

  it('AC-169.8 a failed outcome with no message drops the colon part', () => {
    const text = resultText()
    expect([
      text({ ok: false, outcome: 'unreadable', error_message: null }),
      text({ ok: false, outcome: 'unreadable', error_message: '' }),
      text({ ok: false, outcome: 'check_failed', error_message: null }),
      text({ ok: false, outcome: 'check_failed', error_message: '' }),
    ]).toEqual([
      'Could not read the cookies',
      'Could not read the cookies',
      "Cookies read, but YouTube's check failed",
      "Cookies read, but YouTube's check failed",
    ])
  })
})
