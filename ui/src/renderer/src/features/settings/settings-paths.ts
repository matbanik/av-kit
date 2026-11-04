export const SETTINGS_NAMESPACE_PATHS = {
  downloader: '/settings/downloader',
  transcript: '/settings/transcript',
  tts: '/settings/tts',
  app: '/settings/app',
  ui: '/settings/ui',
  converter: '/settings/converter',
  capture: '/settings/capture',
} as const

export type SettingsNamespace = keyof typeof SETTINGS_NAMESPACE_PATHS
