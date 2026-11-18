import { createHeldRequest, currentRoute } from '../../lib/shell-nav'

export const SETTINGS_EVENTS = {
  checkDeps: 'av-kit:settings:check_deps',
} as const

export const HELP_EVENTS = {
  toggle: 'av-kit:help:toggle',
} as const

/** Consumed by HelpCard on mount after off-route navigate-then-toggle. */
export const HELP_PENDING_TOGGLE_KEY = 'av-kit:help:pending-toggle'

/** HELP_FEATURE_ROUTE (MEU-158, D-1176): the route each HelpCard feature lives on. */
export const HELP_FEATURE_ROUTE = {
  downloader: '/',
  transcript: '/transcript',
  tts: '/tts',
  settings: '/settings',
  converter: '/convert',
  capture: '/capture',
} as const

/** HELP_HOLD (MEU-158, D-1175, D-1176): an F1 that no card on its route received, held for that route. */
const helpHold = createHeldRequest((key) => currentRoute() === key)

/** HELP_TAKE_ON_MOUNT: whether an F1 is held for this route; it is cleared, so it toggles once. */
export function takeHeldHelpToggle(route: string): boolean {
  return helpHold.take(route)
}

export const HELP_COMMANDS = {
  /** A card on the route calls preventDefault and toggles; one no card received is held (HELP_HOLD). */
  toggle: () => {
    const route = currentRoute()
    const token = helpHold.begin(route)
    if (token === null) {
      return
    }
    const unreceived = window.dispatchEvent(
      new CustomEvent('av-kit:help:toggle-local', { cancelable: true, detail: { route } }),
    )
    helpHold.settle(token, unreceived)
  },
  /** Queue a toggle for the next mounted HelpCard (off-route palette delivery). */
  queueToggleAfterNavigate: () => {
    try {
      sessionStorage.setItem(HELP_PENDING_TOGGLE_KEY, '1')
    } catch {
      // ignore storage failures; local event may still reach a mounted card
    }
  },
} as const

export const SETTINGS_COMMANDS = {
  checkDeps: () => {
    window.dispatchEvent(new CustomEvent(SETTINGS_EVENTS.checkDeps))
  },
} as const
