export const SETTINGS_EVENTS = {
  checkDeps: 'av-kit:settings:check_deps',
} as const

export const HELP_EVENTS = {
  toggle: 'av-kit:help:toggle',
} as const

/** Consumed by HelpCard on mount after off-route navigate-then-toggle. */
export const HELP_PENDING_TOGGLE_KEY = 'av-kit:help:pending-toggle'

export const HELP_COMMANDS = {
  toggle: () => {
    window.dispatchEvent(new CustomEvent('av-kit:help:toggle-local'))
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
