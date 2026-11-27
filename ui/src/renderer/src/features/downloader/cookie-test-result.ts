/**
 * MEU-169 (AC-169.8; COOKIE_TEST_SHOWN): the text of the Test Cookies result line. The reply is
 * `POST /downloads/cookies/test`'s `CookieTestOut`; `outcome` says where the test stopped and is
 * null for cookie mode none. `error_message` is the reason, never a cookie value.
 */

export type CookieTestOutcome = 'ok' | 'unreadable' | 'check_failed'

export type CookieTestReply = {
  ok: boolean
  outcome: CookieTestOutcome | null
  error_message: string | null
}

function withReason(text: string, reason: string | null): string {
  return reason ? `${text}: ${reason}` : text
}

export function cookieTestResultText(reply: CookieTestReply): string {
  switch (reply.outcome) {
    case 'ok':
      return 'Cookies read. YouTube answered.'
    case 'unreadable':
      return withReason('Could not read the cookies', reply.error_message)
    case 'check_failed':
      return withReason("Cookies read, but YouTube's check failed", reply.error_message)
    default:
      return 'Cookie mode is None. Nothing to test.'
  }
}
