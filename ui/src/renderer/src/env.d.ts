/// <reference types="vite/client" />

export {}

type StartupMetricKey =
  | 'startup.python_spawn_ms'
  | 'startup.renderer_load_ms'
  | 'startup.shell_paint_ms'
  | 'startup.window_show_ms'
  | 'startup.data_ready_ms'
  | 'startup.lazy_preload_ms'

declare global {
  interface Window {
    api: {
      getBackendUrl: () => Promise<string>
      getToken: () => Promise<string>
      logStartupMetric: (key: StartupMetricKey, value: number) => void
      showDirectoryDialog: () => Promise<string | undefined>
      showFileDialog: (
        filters?: { name: string; extensions: string[] }[],
      ) => Promise<string | undefined>
      showFilesDialog: (
        filters?: { name: string; extensions: string[] }[],
      ) => Promise<string[]>
      getPathForFile: (file: File) => string
      openPath: (target: string) => Promise<void>
      showItemInFolder: (target: string) => Promise<void>
      readClipboardText: () => Promise<string>
      writeClipboardText: (text: string) => Promise<void>
      writeClipboardImage?: (png: Uint8Array) => Promise<void>
      getMcpSetupPrompt?: (opts: { client: string; scope: 'user' | 'project' }) => Promise<{ text: string }>
      readTextFile: (opts: { maxBytes?: number }) => Promise<{ text: string; basename: string }>
      copyMcpConfig: (opts?: { pinEndpoint?: boolean }) => Promise<{ ok: true }>
      getSetupReadiness: () => Promise<{
        descriptorPresent: boolean
        portOk: boolean
        modelsDirWritable: boolean
        logFilePath?: string
      }>
      getMcpAccessStatus: () => Promise<{ tokenPresent: boolean }>
      subscribeLogs: (cb: (batch: unknown[]) => void) => () => void
      getLogSnapshot: () => Promise<unknown>
      captureRegion: () => Promise<void>
      getHotkeyStatus: () => Promise<{ accelerator: string; registered: boolean; inUse: boolean }>
      onInboxChanged: (cb: () => void) => () => void
      loginItemGet?: () => Promise<
        | {
            supported: true
            enabled: boolean
            minimized: boolean
            startMinimizedSupported: boolean
          }
        | {
            supported: false
            reason: 'platform' | 'not-packaged'
            enabled: false
            minimized: false
          }
      >
      loginItemSet?: (
        enabled: boolean,
        minimized: boolean,
      ) => Promise<
        | {
            supported: true
            enabled: boolean
            minimized: boolean
            startMinimizedSupported: boolean
          }
        | {
            supported: false
            reason: 'platform' | 'not-packaged'
            enabled: false
            minimized: false
          }
      >
    }
  }
}
