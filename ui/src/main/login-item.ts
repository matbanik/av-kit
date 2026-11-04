import { START_MINIMIZED_FLAG } from './startup-mode'

export const LOGIN_ITEM_NAME = 'com.avkit.app'

export type LoginItemUnsupportedReason = 'platform' | 'not-packaged'

export type LoginItemSupport =
  | { supported: true }
  | { supported: false; reason: LoginItemUnsupportedReason }

export type LoginItemState =
  | {
      supported: true
      enabled: boolean
      minimized: boolean
      startMinimizedSupported: boolean
    }
  | {
      supported: false
      reason: LoginItemUnsupportedReason
      enabled: false
      minimized: false
    }

export interface LaunchItemFact {
  name: string
  path: string
  args: string[]
  scope: 'user' | 'machine'
  enabled: boolean
}

export interface LoginItemDeps {
  platform: NodeJS.Platform
  packaged: boolean
  execPath: string
  getLoginItemSettings: (options: { path: string; args: string[] }) => {
    openAtLogin: boolean
    executableWillLaunchAtLogin?: boolean
    launchItems?: LaunchItemFact[]
    openAsHidden?: boolean
    wasOpenedAsHidden?: boolean
  }
  setLoginItemSettings: (settings: {
    openAtLogin: boolean
    path: string
    args: string[]
    name: string
  }) => void
}

export function classifyLoginItemSupport(facts: {
  platform: NodeJS.Platform
  packaged: boolean
}): LoginItemSupport {
  if (facts.platform !== 'win32' && facts.platform !== 'darwin') {
    return { supported: false, reason: 'platform' }
  }
  if (!facts.packaged) {
    return { supported: false, reason: 'not-packaged' }
  }
  return { supported: true }
}

function unsupported(support: {
  supported: false
  reason: LoginItemUnsupportedReason
}): LoginItemState {
  return {
    supported: false,
    reason: support.reason,
    enabled: false,
    minimized: false,
  }
}

function okState(
  enabled: boolean,
  minimized: boolean,
  startMinimizedSupported: boolean,
): LoginItemState {
  return {
    supported: true,
    enabled,
    minimized: enabled && minimized && startMinimizedSupported,
    startMinimizedSupported,
  }
}

function argsFor(minimized: boolean): string[] {
  return minimized ? [START_MINIMIZED_FLAG] : []
}

function canonical(p: string): string {
  return p.trim().replace(/^"|"$/g, '').replace(/\\/g, '/').replace(/\/+$/, '').toLowerCase()
}

function ownLaunchItems(
  items: LaunchItemFact[] | undefined,
  execPath: string,
  args: string[],
): LaunchItemFact[] {
  if (!Array.isArray(items)) return []
  const mine = items.filter(
    (item) =>
      item &&
      typeof item.path === 'string' &&
      canonical(item.path) === canonical(execPath),
  )
  const exact = mine.filter(
    (item) =>
      Array.isArray(item.args) &&
      item.args.length === args.length &&
      item.args.every((a, i) => a === args[i]),
  )
  return exact.length > 0 ? exact : mine
}

function willLaunchAtSignIn(deps: LoginItemDeps, args: string[]): boolean {
  const settings = deps.getLoginItemSettings({ path: deps.execPath, args })
  if (!settings.openAtLogin) return false
  if (settings.executableWillLaunchAtLogin === false) return false
  const ours = ownLaunchItems(settings.launchItems, deps.execPath, args)
  if (ours.length === 0) return true
  return ours.some((item) => item.enabled !== false)
}

export function readStartAtSignIn(deps: LoginItemDeps): LoginItemState {
  const support = classifyLoginItemSupport(deps)
  if (!support.supported) return unsupported(support)
  if (deps.platform === 'darwin') {
    const settings = deps.getLoginItemSettings({ path: deps.execPath, args: [] })
    if (!settings.openAtLogin || settings.executableWillLaunchAtLogin === false) {
      return okState(false, false, false)
    }
    return okState(true, false, false)
  }
  if (willLaunchAtSignIn(deps, argsFor(true))) {
    return okState(true, true, true)
  }
  return okState(willLaunchAtSignIn(deps, argsFor(false)), false, true)
}

export function writeStartAtSignIn(
  enabled: boolean,
  minimized: boolean,
  deps: LoginItemDeps,
): LoginItemState {
  if (typeof enabled !== 'boolean' || typeof minimized !== 'boolean') {
    throw new TypeError(
      'start-at-sign-in expects two booleans, received ' +
        `${typeof enabled} and ${typeof minimized}`,
    )
  }
  const support = classifyLoginItemSupport(deps)
  if (!support.supported) {
    return unsupported(support)
  }
  if (deps.platform === 'darwin') {
    deps.setLoginItemSettings({
      openAtLogin: false,
      path: deps.execPath,
      args: [],
      name: LOGIN_ITEM_NAME,
    })
    deps.setLoginItemSettings({
      openAtLogin: enabled,
      path: deps.execPath,
      args: [],
      name: LOGIN_ITEM_NAME,
    })
    return readStartAtSignIn(deps)
  }
  const wanted = enabled && minimized
  deps.setLoginItemSettings({
    openAtLogin: false,
    path: deps.execPath,
    args: argsFor(!wanted),
    name: LOGIN_ITEM_NAME,
  })
  deps.setLoginItemSettings({
    openAtLogin: enabled,
    path: deps.execPath,
    args: argsFor(wanted),
    name: LOGIN_ITEM_NAME,
  })
  return readStartAtSignIn(deps)
}

export function loginLaunchShouldHideWindow(
  readLaunch: () => { wasOpenedAsHidden?: boolean },
): boolean {
  return readLaunch().wasOpenedAsHidden === true
}
