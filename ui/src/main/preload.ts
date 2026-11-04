import { contextBridge, ipcRenderer, webUtils } from 'electron'

const API_KEYS = [
  'getBackendUrl',
  'getToken',
  'logStartupMetric',
  'showDirectoryDialog',
  'showFileDialog',
  'showFilesDialog',
  'getPathForFile',
  'openPath',
  'showItemInFolder',
  'readClipboardText',
  'writeClipboardText',
  'readTextFile',
  'copyMcpConfig',
  'getSetupReadiness',
  'getMcpAccessStatus',
  'subscribeLogs',
  'getLogSnapshot',
  'captureRegion',
  'getHotkeyStatus',
  'onInboxChanged',
  'loginItemGet',
  'loginItemSet',
  'writeClipboardImage',
  'getMcpSetupPrompt',
] as const

export function getPreloadApiKeys(): string[] {
  return [...API_KEYS]
}

export function exposePreload(): void {
  contextBridge.exposeInMainWorld('api', {
    getBackendUrl: () => ipcRenderer.invoke('get-backend-url'),
    getToken: () => ipcRenderer.invoke('get-token'),
    logStartupMetric: (key: string, value: number) =>
      ipcRenderer.invoke('startup-metric', { key, value, timestamp: Date.now() }),
    showDirectoryDialog: () => ipcRenderer.invoke('show-directory-dialog'),
    showFileDialog: (filters?: { name: string; extensions: string[] }[]) =>
      ipcRenderer.invoke('show-file-dialog', { filters }),
    showFilesDialog: (filters?: { name: string; extensions: string[] }[]) =>
      ipcRenderer.invoke('show-files-dialog', { filters }),
    getPathForFile: (file: File) => {
      try {
        return webUtils.getPathForFile(file)
      } catch {
        return ''
      }
    },
    openPath: (target: string) => ipcRenderer.invoke('open-path', { target }),
    showItemInFolder: (target: string) => ipcRenderer.invoke('show-item-in-folder', { target }),
    readClipboardText: () => ipcRenderer.invoke('read-clipboard-text'),
    writeClipboardText: (text: string) => ipcRenderer.invoke('write-clipboard-text', { text }),
    readTextFile: (opts: { maxBytes?: number }) => ipcRenderer.invoke('read-text-file', opts),
    copyMcpConfig: (opts?: { pinEndpoint?: boolean }) => ipcRenderer.invoke('copy-mcp-config', opts ?? {}),
    getSetupReadiness: () => ipcRenderer.invoke('get-setup-readiness'),
    getMcpAccessStatus: () => ipcRenderer.invoke('get-mcp-access-status'),
    subscribeLogs: (cb: (batch: unknown[]) => void) => {
      const listener = (_event: unknown, batch: unknown[]) => {
        cb(batch)
      }
      ipcRenderer.on('console-log-batch', listener)
      return () => {
        ipcRenderer.removeListener('console-log-batch', listener)
      }
    },
    getLogSnapshot: () => ipcRenderer.invoke('get-log-snapshot'),
    captureRegion: () => ipcRenderer.invoke('capture-region'),
    getHotkeyStatus: () => ipcRenderer.invoke('get-hotkey-status'),
    loginItemGet: () => ipcRenderer.invoke('login-item-get'),
    loginItemSet: (enabled: boolean, minimized: boolean) =>
      ipcRenderer.invoke('login-item-set', { enabled, minimized }),
    writeClipboardImage: (png: Uint8Array) => ipcRenderer.invoke('write-clipboard-image', { png }),
    getMcpSetupPrompt: (opts: { client: string; scope: 'user' | 'project' }) =>
      ipcRenderer.invoke('get-mcp-setup-prompt', opts),
    onInboxChanged: (cb: () => void) => {
      const listener = () => {
        cb()
      }
      ipcRenderer.on('captures:inbox-changed', listener)
      return () => {
        ipcRenderer.removeListener('captures:inbox-changed', listener)
      }
    },
  })
}

if (process.env.VITEST === undefined) {
  exposePreload()
}
