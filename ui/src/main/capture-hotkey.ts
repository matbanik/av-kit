import { globalShortcut } from 'electron'

export type HotkeyStatus = {
  accelerator: string
  registered: boolean
  inUse: boolean
}

let current: HotkeyStatus = {
  accelerator: 'F2',
  registered: false,
  inUse: false,
}

let onFire: (() => void) | null = null

export function getHotkeyStatus(): HotkeyStatus {
  return { ...current }
}

export function unregisterCaptureHotkey(): void {
  globalShortcut.unregister(current.accelerator)
  current = { ...current, registered: false }
}

export function registerCaptureHotkey(accelerator: string, fire: () => void): HotkeyStatus {
  if (current.registered) {
    unregisterCaptureHotkey()
  }
  onFire = fire
  const ok = globalShortcut.register(accelerator, () => {
    onFire?.()
  })
  current = {
    accelerator,
    registered: ok,
    inUse: !ok,
  }
  return getHotkeyStatus()
}

export function startCaptureHotkey(fire: () => void): HotkeyStatus {
  return registerCaptureHotkey(current.accelerator, fire)
}
