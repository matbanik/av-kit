import type { BrowserWindow } from 'electron'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

// MEU-164 (Session 102): a double-click on the tray icon runs Show window (TRAY_SHOW_SHARED),
// and a launch with AVKIT_E2E=1 exposes the tray to Playwright (TRAY_E2E_HOOK).

const fakes = vi.hoisted(() => {
  type Listener = (...args: unknown[]) => void
  type Item = { label?: string; click?: Listener }
  class FakeTray {
    static created: FakeTray[] = []
    listeners: { event: string; listener: Listener }[] = []
    contextMenu: unknown = undefined
    tooltip = ''
    constructor(readonly image: unknown) {
      FakeTray.created.push(this)
    }
    on(event: string, listener: Listener): this {
      this.listeners.push({ event, listener })
      return this
    }
    setContextMenu(menu: unknown): void {
      this.contextMenu = menu
    }
    setToolTip(text: string): void {
      this.tooltip = text
    }
  }
  const built: { template: Item[] }[] = []
  const Menu = {
    buildFromTemplate: (template: Item[]): { template: Item[] } => {
      const menu = { template }
      built.push(menu)
      return menu
    },
  }
  return { FakeTray, Menu, built }
})

vi.mock('electron', async (importOriginal) => ({
  ...(await importOriginal<Record<string, unknown>>()),
  Tray: fakes.FakeTray,
  Menu: fakes.Menu,
}))
vi.mock('../../src/main/app-icon', () => ({ trayIconImage: () => ({}) }))
vi.mock('../../src/main/notify-user', () => ({ registerNotifyTray: () => undefined }))

import { shell } from 'electron'

import { startCaptureTray } from '../../src/main/capture-tray'

type FakeTray = InstanceType<typeof fakes.FakeTray>
type HookGlobal = { __AVKIT_E2E_TRAY__?: { tray: unknown; menu: unknown } }

const LABELS = ['Show window', 'Capture region', 'Open inbox folder', 'Quit']

function fakeWindow(minimized: boolean): { window: BrowserWindow; calls: string[] } {
  const calls: string[] = []
  let isMin = minimized
  const window = {
    isMinimized: (): boolean => isMin,
    restore: (): void => {
      calls.push('restore')
      isMin = false
    },
    show: (): void => {
      calls.push('show')
    },
    focus: (): void => {
      calls.push('focus')
    },
  }
  return { window: window as unknown as BrowserWindow, calls }
}

function start(minimized = false) {
  const onRegion = vi.fn()
  const inboxDir = vi.fn(() => 'C:/inbox')
  const win = fakeWindow(minimized)
  const tray = startCaptureTray({ window: win.window, onRegion, inboxDir }) as unknown as FakeTray
  const menu = fakes.built[fakes.built.length - 1]
  const doubleClick = tray.listeners.find((entry) => entry.event === 'double-click')?.listener
  return { tray, menu, onRegion, inboxDir, doubleClick, ...win }
}

let savedE2e: string | undefined

beforeEach(() => {
  fakes.FakeTray.created.length = 0
  fakes.built.length = 0
  savedE2e = process.env.AVKIT_E2E
  delete process.env.AVKIT_E2E
})

afterEach(() => {
  if (savedE2e === undefined) {
    delete process.env.AVKIT_E2E
  } else {
    process.env.AVKIT_E2E = savedE2e
  }
  delete (globalThis as HookGlobal).__AVKIT_E2E_TRAY__
  vi.restoreAllMocks()
})

describe('capture tray', () => {
  it('AC-164.1 a double-click runs the Show window item and the menu is unchanged', () => {
    const { tray, menu } = start()
    expect(fakes.FakeTray.created).toHaveLength(1)
    expect(menu.template.map((item) => item.label)).toEqual(LABELS)
    expect(tray.contextMenu).toBe(menu)
    expect(tray.tooltip).toBe('av-kit')
    expect(tray.listeners.map((entry) => entry.event)).toEqual(['double-click'])
    expect(tray.listeners[0]?.listener).toBe(menu.template[0]?.click)
  })

  it('AC-164.2 Show window restores a minimized window, then shows and focuses it', () => {
    const { doubleClick, menu, calls, onRegion } = start(true)
    const showItem = vi.spyOn(shell, 'showItemInFolder')
    expect(typeof doubleClick).toBe('function')
    doubleClick?.()
    expect(calls).toEqual(['restore', 'show', 'focus'])
    expect(onRegion).not.toHaveBeenCalled()
    expect(showItem).not.toHaveBeenCalled()

    const viaMenu = start(true)
    viaMenu.menu.template[0]?.click?.()
    expect(viaMenu.calls).toEqual(['restore', 'show', 'focus'])
    expect(menu.template[0]?.click).toBe(doubleClick)
  })

  it('AC-164.2 Show window on a window that is not minimized only shows and focuses it', () => {
    const { doubleClick, calls, onRegion } = start(false)
    const showItem = vi.spyOn(shell, 'showItemInFolder')
    expect(typeof doubleClick).toBe('function')
    doubleClick?.()
    expect(calls).toEqual(['show', 'focus'])
    expect(onRegion).not.toHaveBeenCalled()
    expect(showItem).not.toHaveBeenCalled()
  })

  it('AC-164.3 without AVKIT_E2E the tray is not exposed', () => {
    start()
    expect((globalThis as HookGlobal).__AVKIT_E2E_TRAY__).toBeUndefined()
  })

  it('AC-164.3 with AVKIT_E2E=1 the hook holds the created tray and the built menu', () => {
    process.env.AVKIT_E2E = '1'
    const { tray, menu } = start()
    const hook = (globalThis as HookGlobal).__AVKIT_E2E_TRAY__
    expect(hook?.tray).toBe(tray)
    expect(hook?.menu).toBe(menu)
  })
})
