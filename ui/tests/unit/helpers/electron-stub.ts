export const app = {
  requestSingleInstanceLock: () => true,
  quit: () => undefined,
  exit: () => undefined,
  on: (..._args: unknown[]): unknown => undefined,
  off: (..._args: unknown[]): unknown => undefined,
  removeListener: (..._args: unknown[]): unknown => undefined,
  setAppUserModelId: (_id: string): void => undefined,
  whenReady: async () => undefined,
  isPackaged: false,
}

export class BrowserWindow {
  static getAllWindows(): BrowserWindow[] {
    return []
  }

  webContents = {
    send: () => undefined,
    session: { webRequest: { onHeadersReceived: () => undefined } },
    setWindowOpenHandler: () => undefined,
    on: () => undefined,
  }

  on(): this {
    return this
  }

  getBounds(): { x: number; y: number; width: number; height: number } {
    return { x: 0, y: 0, width: 1280, height: 800 }
  }

  isMinimized(): boolean {
    return false
  }

  restore(): void {
    return undefined
  }

  focus(): void {
    return undefined
  }

  show(): void {
    return undefined
  }

  loadURL(): Promise<void> {
    return Promise.resolve()
  }

  loadFile(): Promise<void> {
    return Promise.resolve()
  }
}

export const ipcMain = {
  handle: () => undefined,
  on: () => undefined,
}

export const ipcRenderer = {
  invoke: async () => undefined,
  send: () => undefined,
  on: () => undefined,
  removeListener: () => undefined,
}

export const contextBridge = {
  exposeInMainWorld: () => undefined,
}

export const dialog = {
  showOpenDialog: async () => ({ canceled: true, filePaths: [] }),
  showMessageBox: async (..._args: unknown[]) => ({ response: 0 }),
}

export const clipboard = {
  writeText: () => undefined,
  readText: () => '',
  writeImage: (_image: unknown): void => undefined,
}

export const shell = {
  openPath: async () => '',
  showItemInFolder: () => undefined,
}

// --- MEU-40 native region picker surface -------------------------------------------------
//
// The picker lifecycle (AC-40.28) kills its child on `app.will-quit`, and `notify-user.ts`
// (AC-40.30 c) branches on `app.isPackaged`. Both need an `app` that actually dispatches and
// whose flags a test can move, so the no-op `on` above is replaced by a real listener table.

type ElectronListener = (...args: unknown[]) => void

const appListeners = new Map<string, ElectronListener[]>()

export function __emitAppEvent(event: string, ...args: unknown[]): void {
  for (const listener of appListeners.get(event) ?? []) {
    listener(...args)
  }
}

export function __resetElectronStub(): void {
  appListeners.clear()
  app.isPackaged = false
  nativeImageFactory = defaultNativeImage
}

app.on = ((event: string, listener: ElectronListener) => {
  const existing = appListeners.get(event) ?? []
  existing.push(listener)
  appListeners.set(event, existing)
  return app
}) as typeof app.on
app.off = ((event: string, listener: ElectronListener) => {
  const existing = appListeners.get(event) ?? []
  const at = existing.indexOf(listener)
  if (at >= 0) {
    existing.splice(at, 1)
  }
  appListeners.set(event, existing)
  return app
}) as typeof app.off
app.removeListener = app.off
app.setAppUserModelId = () => undefined

export function __appListenerCount(event: string): number {
  return (appListeners.get(event) ?? []).length
}

export type StubNativeImage = {
  isEmpty: () => boolean
  getSize: () => { width: number; height: number }
  toBitmap: () => Buffer
  toPNG: () => Buffer
}

const defaultNativeImage = (_path: string): StubNativeImage => ({
  isEmpty: () => false,
  getSize: () => ({ width: 4, height: 4 }),
  toBitmap: () => Buffer.alloc(64, 200),
  toPNG: () => Buffer.alloc(16, 1),
})

let nativeImageFactory: (path: string) => StubNativeImage = defaultNativeImage

/** Lets a spec decide what `nativeImage.createFromPath` returns for the staged PNG. */
export function __setNativeImageFactory(factory: (path: string) => StubNativeImage): void {
  nativeImageFactory = factory
}

export const nativeImage = {
  createFromPath: (path: string): StubNativeImage => nativeImageFactory(path),
}

/**
 * `notify-user.ts` imports `Notification` at module scope, so the stub must export the binding
 * even though every spec injects its own surface through `setNotifyUserDeps` (AC-40.30 c).
 */
export class Notification {
  static isSupported(): boolean {
    return true
  }

  constructor(_options: { title: string; body: string }) {
    Notification.constructed += 1
  }

  static constructed = 0

  on(): this {
    return this
  }

  show(): void {
    return undefined
  }
}
