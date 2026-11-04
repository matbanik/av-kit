export const COLLAPSE_RAIL_EVENT = 'av-kit:collapse-rail'
export const TOGGLE_CONSOLE_EVENT = 'av-kit:toggle-console'

export function navigateShell(path: string): void {
  window.location.hash = path.startsWith('#') ? path.slice(1) : path
  window.dispatchEvent(new HashChangeEvent('hashchange'))
}

export function requestCollapseRail(): void {
  window.dispatchEvent(new CustomEvent(COLLAPSE_RAIL_EVENT))
}
