export const COLLAPSE_RAIL_EVENT = 'av-kit:collapse-rail'
export const TOGGLE_CONSOLE_EVENT = 'av-kit:toggle-console'

export function navigateShell(path: string): void {
  window.location.hash = path.startsWith('#') ? path.slice(1) : path
  window.dispatchEvent(new HashChangeEvent('hashchange'))
}

export function requestCollapseRail(): void {
  window.dispatchEvent(new CustomEvent(COLLAPSE_RAIL_EVENT))
}

/** CURRENT_ROUTE: the hash without its `#` and before any `?`, or `'/'` when it is empty. */
export function currentRoute(): string {
  const route = window.location.hash.replace(/^#/, '').split('?')[0] ?? ''
  return route === '' ? '/' : route
}

type HeldToken = { readonly key: string; held: boolean }

type HeldRequest = {
  begin: (key: string) => HeldToken | null
  isCurrent: (token: HeldToken) => boolean
  settle: (token: HeldToken, unreceived: boolean) => void
  take: (key: string) => boolean
}

/**
 * HELD_REQUEST (MEU-158, D-1175): one outstanding request per instance, made at press time and
 * kept in renderer memory only. A press for the key already outstanding joins it (`begin`
 * returns `null`); a press for another key replaces it. The request is dropped by its one
 * `hashchange` listener as soon as `stillHome(key)` is false. `settle` holds a request that no
 * receiver took while it is still home, and `take` clears an outstanding one, held or waiting,
 * once.
 */
export function createHeldRequest(stillHome: (key: string) => boolean): HeldRequest {
  let outstanding: HeldToken | null = null
  let onHashChange: (() => void) | null = null

  const clear = (): void => {
    outstanding = null
    if (onHashChange !== null) {
      window.removeEventListener('hashchange', onHashChange)
      onHashChange = null
    }
  }

  return {
    begin: (key) => {
      if (outstanding !== null && outstanding.key === key) {
        return null
      }
      clear()
      const token: HeldToken = { key, held: false }
      outstanding = token
      onHashChange = () => {
        if (!stillHome(token.key)) {
          clear()
        }
      }
      window.addEventListener('hashchange', onHashChange)
      return token
    },
    isCurrent: (token) => outstanding === token,
    settle: (token, unreceived) => {
      if (outstanding !== token) {
        return
      }
      if (unreceived && stillHome(token.key)) {
        token.held = true
      } else {
        clear()
      }
    },
    take: (key) => {
      if (outstanding === null || outstanding.key !== key) {
        return false
      }
      clear()
      return true
    },
  }
}
