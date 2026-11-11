import { randomUUID } from 'node:crypto'
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { homedir } from 'node:os'
import { join } from 'node:path'

import Store from 'electron-store'
import { app, BrowserWindow, clipboard, dialog, ipcMain, nativeImage, shell } from 'electron'

import { appIconPath } from './app-icon'
import { recordE2eShell } from './e2e-shell'
import { writePngToClipboard } from './clipboard-image'
import {
  descriptorPath,
  readDescriptorPid,
  retireDescriptor,
  retirePortSibling,
} from './backend-descriptor'
import {
  appendStdoutLog,
  createWebPreferences,
  getPublishedBackendReady,
  handleIpc,
  listRegisteredChannels,
  publishBackendReady,
  SHOW_FILES_PROPERTIES,
} from './ipc'
import {
  isPidRunning,
  queryLiveProcess,
  resolveBootIdentity,
} from './live-identity'
import {
  buildDevSpawnArgv,
  buildPackagedSpawnArgv,
  forwardConsoleLines,
  packagedBackendPath,
  publishIfReady,
  resolvePythonImage,
  shutdownOwned,
  spawnOwned,
  waitPidExit,
} from './python-manager'
import { mcpServerEntry } from './mcp-setup-prompt'
import { probeSetupReadiness } from './setup-readiness'
import {
  captureRegionFromGui,
  expandInboxDir,
  pasteClipboardImage,
  PICKER_PATH_PROBE_FLAG,
  PICKER_PATH_PROBE_PREFIX,
  resolvePasteInbox,
  resolvePickerExePath,
} from './capture-picker'
import { registerCaptureHotkey, getHotkeyStatus } from './capture-hotkey'
import { startInboxWatch, stopInboxWatch } from './capture-inbox-watch'
import { isQuitting, setQuitIntent } from './capture-quit'
import {
  applyCaptureRuntime,
  CAPTURE_RUNTIME_DEFAULTS,
  captureRuntimeEqual,
  fetchCaptureRuntime,
  type CaptureRuntime,
} from './capture-runtime'
import { startInteractiveRequestLoop } from './capture-register'
import { startCaptureTray } from './capture-tray'
import { loginLaunchShouldHideWindow, type LoginItemDeps } from './login-item'
import { revealMainWindow } from './startup-mode'

export const RENDERER_CSP =
  "default-src 'self'; img-src 'self' http://localhost:* http://127.0.0.1:* data: blob:; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self' http://127.0.0.1:*"

export const RENDERER_DEV_CSP =
  "default-src 'self'; img-src 'self' http://localhost:* http://127.0.0.1:* data: blob:; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self' http://127.0.0.1:* http://localhost:* ws://127.0.0.1:* ws://localhost:*"

export function activeRendererCsp(): string {
  return process.env.ELECTRON_RENDERER_URL !== undefined ? RENDERER_DEV_CSP : RENDERER_CSP
}

export function allowNavigation(url: string): boolean {
  const renderer = process.env.ELECTRON_RENDERER_URL
  if (renderer === undefined || renderer.trim() === '') {
    return false
  }
  return url.startsWith(renderer)
}

export function applySingleInstance(
  target: {
    requestSingleInstanceLock: () => boolean
    quit: () => void
    on: (event: string, cb: (...args: unknown[]) => void) => void
  },
  _spawnBackend: () => void,
): 'winner' | 'loser' {
  if (process.env.AVKIT_E2E === '1') {
    return 'winner'
  }
  const won = target.requestSingleInstanceLock()
  if (!won) {
    target.quit()
    return 'loser'
  }
  target.on('second-instance', () => {
    const windows = BrowserWindow.getAllWindows()
    const first = windows[0]
    if (first !== undefined) {
      if (first.isMinimized()) {
        first.restore()
      }
      first.focus()
    }
  })
  return 'winner'
}

export function restoreWindowBounds(store: { get: (key: string) => unknown }): {
  x: number
  y: number
  width: number
  height: number
} | undefined {
  const value = store.get('window.bounds')
  if (
    value !== null &&
    typeof value === 'object' &&
    'x' in value &&
    'y' in value &&
    'width' in value &&
    'height' in value
  ) {
    return value as { x: number; y: number; width: number; height: number }
  }
  return undefined
}

export function createWindowOptions(store: { get: (key: string) => unknown }): {
  x?: number
  y?: number
  width: number
  height: number
} {
  const bounds = restoreWindowBounds(store)
  if (bounds === undefined) {
    return { width: 1280, height: 800 }
  }
  return bounds
}

function defaultAppData(): string {
  const override = process.env.AVKIT_APP_DATA
  if (override !== undefined && override.trim() !== '') {
    return override
  }
  if (process.platform === 'win32') {
    const local = process.env.LOCALAPPDATA ?? join(homedir(), 'AppData', 'Local')
    return join(local, 'av-kit')
  }
  return join(homedir(), '.avkit')
}

function readOrCreateMcpToken(appData: string): string {
  const path = join(appData, 'mcp-token.txt')
  if (existsSync(path)) {
    return readFileSync(path, { encoding: 'utf8' }).trim()
  }
  const token = randomUUID()
  writeFileSync(path, `${token}\n`, { encoding: 'utf8' })
  return token
}

async function defaultPythonRunner(cmd: string[]): Promise<string> {
  const { spawn } = await import('node:child_process')
  return await new Promise((resolve, reject) => {
    const child = spawn(cmd[0] ?? 'uv', cmd.slice(1), { stdio: ['ignore', 'pipe', 'pipe'] })
    let out = ''
    let err = ''
    child.stdout?.on('data', (chunk: Buffer) => {
      out += chunk.toString('utf8')
    })
    child.stderr?.on('data', (chunk: Buffer) => {
      err += chunk.toString('utf8')
    })
    child.on('error', reject)
    child.on('close', (code) => {
      if (code === 0) {
        resolve(out)
        return
      }
      reject(new Error(err || `python image resolve exited ${code}`))
    })
  })
}

/**
 * In an end-to-end run the renderer must reach the fixture backend the test started, not the
 * unreachable port-9 placeholder that only exists to unblock the first fetch.
 */
function e2eBackend(ready: { apiBase: string; token: string }): { apiBase: string; token: string } {
  const override = process.env.AVKIT_E2E_API_BASE
  if (override === undefined || override.trim() === '') {
    return ready
  }
  return { ...ready, apiBase: override.trim() }
}

export async function boot(): Promise<void> {
  if (process.argv.includes(PICKER_PATH_PROBE_FLAG)) {
    // Row 9a asks the *installed* app where it would look for the sidecar, which is the only way
    // to prove extraResources landed where the shipped resolver reads. Exactly one line, then out.
    process.stdout.write(PICKER_PATH_PROBE_PREFIX + resolvePickerExePath() + '\n')
    app.exit(0)
    return
  }
  const role = applySingleInstance(
    app as unknown as Parameters<typeof applySingleInstance>[0],
    () => undefined,
  )
  if (role === 'loser') {
    return
  }
  const appData = defaultAppData()
  mkdirSync(appData, { recursive: true })
  if (process.env.AVKIT_APP_DATA !== undefined && process.env.AVKIT_APP_DATA.trim() !== '') {
    app.setPath('userData', appData)
  }
  const guiNonce = randomUUID()
  const mcpToken = readOrCreateMcpToken(appData)
  let captureRuntime: CaptureRuntime = { ...CAPTURE_RUNTIME_DEFAULTS }
  let closeToTray = captureRuntime.close_to_tray
  let captureInboxDir = captureRuntime.inbox_dir
  let captureCopyToClipboard = captureRuntime.copy_to_clipboard
  let capturing = false
  const packaged = app.isPackaged
  const pythonImage = packaged
    ? packagedBackendPath(process.resourcesPath)
    : await resolvePythonImage(defaultPythonRunner)
  const argv = packaged
    ? buildPackagedSpawnArgv({
        packagedBackend: pythonImage,
        token: guiNonce,
        mcpToken,
        appData,
      })
    : buildDevSpawnArgv({ pythonImage, token: guiNonce, mcpToken, appData })
  const descFile = descriptorPath(appData)
  const descriptorRaw = existsSync(descFile) ? readFileSync(descFile, { encoding: 'utf8' }) : null
  const identity = resolveBootIdentity({
    lockHeld: true,
    oursExe: pythonImage,
    oursAppData: appData,
    descriptorRaw,
    isPidRunning,
    queryLive: queryLiveProcess,
  })
  if (identity.decision === 'refuse') {
    return
  }
  if (identity.decision === 'reap_then_spawn' && identity.signalPid !== null) {
    try {
      process.kill(identity.signalPid)
    } catch {
      // already gone
    }
    await waitPidExit(identity.signalPid, isPidRunning)
  }
  const child = spawnOwned(argv, { ...process.env })
  const ownedPid = child.pid ?? null
  let mainWindow: BrowserWindow | null = null
  const onChildOutput = (chunk: Buffer) => {
    const text = chunk.toString('utf8')
    for (const line of text.split(/\r?\n/)) {
      if (line.length === 0) {
        continue
      }
      const item = appendStdoutLog(line)
      forwardConsoleLines(mainWindow, [item])
    }
    if (ownedPid === null) {
      return
    }
    const published = publishIfReady({
      chunkText: text,
      ownedPid,
      readDescriptorPid: () => readDescriptorPid(appData),
      queryLive: queryLiveProcess,
      oursExe: pythonImage,
      token: guiNonce,
      publish: publishBackendReady,
    })
    if (published) {
      const note = appendStdoutLog(`INFO backend published for port in AVKIT_READY`)
      forwardConsoleLines(mainWindow, [note])
    }
  }
  child.stdout?.on('data', onChildOutput)
  child.stderr?.on('data', onChildOutput)
  child.on('exit', () => {
    void shutdownOwned('child-exit', {
      ownedPid,
      signal: () => undefined,
      retireDescriptor: () => {
        retireDescriptor(appData)
      },
      retirePortSibling: () => {
        retirePortSibling(appData)
      },
      waitPid: async (pid) => {
        await waitPidExit(pid, isPidRunning)
      },
    })
  })
  app.on('before-quit', (event) => {
    setQuitIntent()
    if (process.env.AVKIT_E2E === '1') {
      return
    }
    event.preventDefault()
    void shutdownOwned('quit', {
      ownedPid,
      signal: (pid) => {
        try {
          process.kill(pid)
        } catch {
          // already gone
        }
      },
      retireDescriptor: () => {
        retireDescriptor(appData)
      },
      retirePortSibling: () => {
        retirePortSibling(appData)
      },
      waitPid: async (pid) => {
        await waitPidExit(pid, isPidRunning)
      },
    }).finally(() => {
      app.exit(0)
    })
  })

  const deps = {
    appData,
    guiNonce,
    mcpToken,
    showDirectoryDialog: async () => {
      if (process.env.AVKIT_E2E === '1') {
        return 'C:/e2e/outdir'
      }
      const result = await dialog.showOpenDialog({ properties: ['openDirectory'] })
      return result.canceled ? undefined : result.filePaths[0]
    },
    showFileDialog: async (filters?: { name: string; extensions: string[] }[]) => {
      if (process.env.AVKIT_E2E === '1') {
        return 'C:/e2e/sample.txt'
      }
      const result = await dialog.showOpenDialog({
        properties: ['openFile'],
        filters,
      })
      return result.canceled ? undefined : result.filePaths[0]
    },
    showFilesDialog: async (filters?: { name: string; extensions: string[] }[]) => {
      if (process.env.AVKIT_E2E === '1') {
        return ['C:/e2e/sample.mp4']
      }
      const result = await dialog.showOpenDialog({
        properties: [...SHOW_FILES_PROPERTIES],
        filters,
      })
      return result.canceled ? [] : result.filePaths
    },
    probeSetupReadiness: async () =>
      probeSetupReadiness({
        appData,
        getPublishedBackendReady,
      }),
    readFile: async (path: string) => {
      if (process.env.AVKIT_E2E === '1') {
        return 'Loaded from file.'
      }
      return readFileSync(path, { encoding: 'utf8' })
    },
    openPath: async (target: string) => {
      if (process.env.AVKIT_E2E === '1') {
        recordE2eShell('openPath', target)
        return
      }
      await shell.openPath(target)
    },
    showItemInFolder: async (target: string) => {
      if (process.env.AVKIT_E2E === '1') {
        recordE2eShell('showItemInFolder', target)
        return
      }
      shell.showItemInFolder(target)
    },
    readMcpToken: async () => mcpToken,
    readClipboard: async () => {
      if (process.env.AVKIT_E2E === '1') {
        return 'pasted'
      }
      return clipboard.readText()
    },
    writeClipboard: async (text: string) => {
      clipboard.writeText(text)
    },
    writeClipboardImage: async (png: Uint8Array) => writePngToClipboard(png, { nativeImage, clipboard }),
    postStartupMetric: async (input: {
      url: string
      authorization: string
      key: string
      value: number
    }) => {
      await fetch(input.url, {
        method: 'POST',
        headers: { Authorization: input.authorization, 'Content-Type': 'application/json' },
        body: JSON.stringify({ key: input.key, value_ms: input.value }),
      })
    },
    captureRegion: async () => {
      const current = BrowserWindow.getAllWindows()[0]
      if (current === undefined) {
        return
      }
      await captureRegionFromGui({
        inboxDir: captureInboxDir,
        copyToClipboard: captureCopyToClipboard,
        source: 'gui',
        window: current,
      })
    },
    // MEU-132 PASTE_IPC: the inbox comes from the backend settings read at paste time.
    pasteCaptureImage: async () =>
      pasteClipboardImage({
        resolveInboxDir: () => resolvePasteInbox(fetchCaptureRuntime),
        window: BrowserWindow.getAllWindows()[0],
        readClipboardPng: () => {
          const image = clipboard.readImage()
          return image.isEmpty() ? null : image.toPNG()
        },
      }),
    getHotkeyStatus: async () => getHotkeyStatus(),
    loginItem: {
      platform: process.platform,
      packaged: app.isPackaged,
      execPath: process.execPath,
      getLoginItemSettings: (options: { path: string; args: string[] }) =>
        app.getLoginItemSettings(options),
      setLoginItemSettings: (settings: Parameters<LoginItemDeps['setLoginItemSettings']>[0]) => {
        app.setLoginItemSettings(settings)
      },
    },
    mcpServerLaunch: {
      command: process.execPath,
      serverPath: mcpServerEntry({
        packaged: app.isPackaged,
        resourcesPath: process.resourcesPath,
        dirname: __dirname,
      }),
    },
  }

  for (const channel of listRegisteredChannels()) {
    ipcMain.handle(channel, async (_event, payload: unknown) => {
      const result = await handleIpc(channel, payload, deps)
      if (!result.ok) {
        throw new Error(result.error)
      }
      return result.value
    })
  }
  if (process.env.AVKIT_E2E === '1') {
    const delayMs = Number.parseInt(process.env.AVKIT_E2E_BACKEND_DELAY_MS ?? '0', 10)
    if (!Number.isFinite(delayMs) || delayMs <= 0) {
      publishBackendReady(e2eBackend({ apiBase: 'http://127.0.0.1:9/api/v1', token: guiNonce }))
    }
  }

  const uiStore = new Store({ cwd: appData, name: 'ui-state' })
  await app.whenReady()
  const window = new BrowserWindow({
    ...createWindowOptions(uiStore),
    show: false,
    backgroundColor: '#1a1b26',
    icon: appIconPath('icon.ico'),
    webPreferences: {
      ...createWebPreferences(),
      contextIsolation: true,
      sandbox: true,
      preload: existsSync(join(__dirname, '../preload/index.mjs'))
        ? join(__dirname, '../preload/index.mjs')
        : join(__dirname, '../preload/index.js'),
    },
  })
  mainWindow = window
  window.on('close', (event) => {
    uiStore.set('window.bounds', window.getBounds())
    if (process.env.AVKIT_E2E === '1') {
      return
    }
    if (closeToTray && !isQuitting) {
      event.preventDefault()
      window.hide()
    }
  })
  window.webContents.session.webRequest.onHeadersReceived((details, callback) => {
    const headers = { ...details.responseHeaders, 'Content-Security-Policy': [activeRendererCsp()] }
    callback({ responseHeaders: headers })
  })
  window.webContents.setWindowOpenHandler(() => ({ action: 'deny' }))
  window.webContents.on('will-navigate', (event, url) => {
    if (!allowNavigation(url)) {
      event.preventDefault()
    }
  })
  // STARTUP_RELOAD_RACE (Session 27 A-3). Reveal on the first paint, not after the awaited load:
  // a reload during startup aborts the first navigation (the load promise rejects), but the
  // reloaded page still paints, so the window is shown and the rest of boot still runs.
  window.once('ready-to-show', () => {
    revealMainWindow(
      window,
      process.argv,
      loginLaunchShouldHideWindow(() => app.getLoginItemSettings()),
    )
  })
  try {
    if (process.env.ELECTRON_RENDERER_URL !== undefined) {
      await window.loadURL(process.env.ELECTRON_RENDERER_URL)
    } else {
      await window.loadFile(join(__dirname, '../renderer/index.html'))
    }
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err)
    appendStdoutLog(`[Startup] initial renderer load did not complete: ${message}`)
  }

  const fireRegion = (source: 'hotkey' | 'gui') => {
    if (capturing) {
      return
    }
    capturing = true
    void captureRegionFromGui({
      inboxDir: captureInboxDir,
      copyToClipboard: captureCopyToClipboard,
      source,
      window,
    })
      .catch((err: unknown) => {
        const message = err instanceof Error ? err.message : String(err)
        appendStdoutLog(`[Capture] region failed: ${message}`)
      })
      .finally(() => {
        capturing = false
      })
  }
  const applyRuntimeHooks = {
    onHotkey: (accelerator: string) => {
      registerCaptureHotkey(accelerator, () => {
        fireRegion('hotkey')
      })
    },
    onWatch: (inboxDir: string) => {
      stopInboxWatch()
      try {
        startInboxWatch(expandInboxDir(inboxDir), window)
      } catch {
        // inbox may not exist yet
      }
    },
  }
  const refreshCaptureRuntime = async (): Promise<void> => {
    const next = await fetchCaptureRuntime()
    if (next === null) {
      return
    }
    if (captureRuntimeEqual(captureRuntime, next)) {
      closeToTray = next.close_to_tray
      captureInboxDir = next.inbox_dir
      captureCopyToClipboard = next.copy_to_clipboard
      return
    }
    captureRuntime = applyCaptureRuntime(captureRuntime, next, applyRuntimeHooks)
    closeToTray = captureRuntime.close_to_tray
    captureInboxDir = captureRuntime.inbox_dir
    captureCopyToClipboard = captureRuntime.copy_to_clipboard
  }
  startCaptureTray({
    window,
    onRegion: () => {
      fireRegion('gui')
    },
    inboxDir: () => expandInboxDir(captureInboxDir),
  })
  registerCaptureHotkey(captureRuntime.hotkey, () => {
    fireRegion('hotkey')
  })
  try {
    startInboxWatch(expandInboxDir(captureInboxDir), window)
  } catch {
    // inbox may not exist yet
  }
  void refreshCaptureRuntime()
  setInterval(() => {
    void refreshCaptureRuntime()
  }, 1000)
  // The lifecycle itself lives in `runInteractiveTick`; this only supplies the picker. Capture and
  // completion are deliberately no longer inside one try: a completion that fails must retry, not
  // cancel a request whose PNG is already in the inbox.
  startInteractiveRequestLoop({
    ready: () => !capturing,
    capture: async () => {
      capturing = true
      try {
        return await captureRegionFromGui({
          inboxDir: captureInboxDir,
          copyToClipboard: captureCopyToClipboard,
          source: 'gui',
          window,
          register: false,
        })
      } finally {
        capturing = false
      }
    },
  })
  if (process.env.AVKIT_E2E === '1') {
    const delayMs = Number.parseInt(process.env.AVKIT_E2E_BACKEND_DELAY_MS ?? '0', 10)
    if (Number.isFinite(delayMs) && delayMs > 0) {
      setTimeout(() => {
        publishBackendReady(e2eBackend({ apiBase: 'http://127.0.0.1:9/api/v1', token: guiNonce }))
      }, delayMs)
    }
  }
}

if (process.env.VITEST === undefined) {
  void boot()
}
