/**
 * Phase 11 Settings canon tables (MEU-58). Each set is stated once here and referenced by the
 * page and rail; the plan names them SETTINGS_SECTION_SET, SAVE_MODE_CAPTIONS,
 * CHECKBOX_COPY_SOURCES, NUMBER_HINT_SOURCES and READINESS_COUNT.
 */

export type SettingsSectionKey =
  | 'download'
  | 'transcript'
  | 'tts'
  | 'convert'
  | 'capture'
  | 'console'
  | 'appearance'
  | 'startup'
  | 'dependencies'
  | 'readiness'
  | 'mcp'

export type SaveMode = 'autosave' | 'explicit' | 'immediate' | 'immediate-os' | 'readiness-count' | 'none'

export type RailGroup = 'Pages' | 'App' | 'Setup'

export type SettingsSection = {
  key: SettingsSectionKey
  /** Existing section test ID; unchanged by the recomposition. */
  testId: string
  label: string
  group: RailGroup
  mode: SaveMode
}

/** The live sections in DOM order. `startup` renders only when the login item is supported. */
export const SETTINGS_SECTION_SET: readonly SettingsSection[] = [
  { key: 'download', testId: 'download-settings', label: 'Download', group: 'Pages', mode: 'autosave' },
  { key: 'transcript', testId: 'transcript-settings', label: 'Transcript', group: 'Pages', mode: 'autosave' },
  { key: 'tts', testId: 'tts-settings', label: 'TTS', group: 'Pages', mode: 'autosave' },
  { key: 'convert', testId: 'convert-settings', label: 'Convert', group: 'Pages', mode: 'explicit' },
  { key: 'capture', testId: 'capture-settings', label: 'Capture', group: 'Pages', mode: 'explicit' },
  { key: 'console', testId: 'console-settings', label: 'Console & logging', group: 'App', mode: 'autosave' },
  { key: 'appearance', testId: 'appearance-settings', label: 'Appearance', group: 'App', mode: 'immediate' },
  { key: 'startup', testId: 'start-at-sign-in-panel', label: 'Startup', group: 'App', mode: 'immediate-os' },
  { key: 'dependencies', testId: 'dependencies-section', label: 'Dependencies', group: 'Setup', mode: 'none' },
  { key: 'readiness', testId: 'readiness-card', label: 'Readiness', group: 'Setup', mode: 'readiness-count' },
  { key: 'mcp', testId: 'mcp-access-card', label: 'MCP access', group: 'Setup', mode: 'none' },
]

export const RAIL_GROUPS: readonly RailGroup[] = ['Pages', 'App', 'Setup']

/** Caption per persistence model (ST2). Labels existing behavior; no mutation is unified. */
export const SAVE_MODE_CAPTIONS: Readonly<Record<'autosave' | 'explicit' | 'immediate' | 'immediate-os', string>> = {
  autosave: 'Saves as you type',
  explicit: 'Save required',
  immediate: 'Applies immediately',
  'immediate-os': 'Applies immediately (OS)',
}

/** The only checkbox explanation lines (ST5), each from a cited source line. */
export const CHECKBOX_COPY_SOURCES: Readonly<Record<string, string>> = {
  archive_tracking: 'Skip previously downloaded videos', // docs/build-plan/06-gui.md:963
  yt_dlp_debug: 'Show yt-dlp debug messages in console', // docs/build-plan/06-gui.md:964
  console_visible: 'Show console panel on startup', // docs/build-plan/06-gui.md:1004
  copy_to_clipboard: 'After successful save', // docs/build-plan/09-screenshot-capture.md:554
}

/** The only number hints (ST4), each from a cited source line; no new min/max/step. */
export const NUMBER_HINT_SOURCES: Readonly<Record<string, string>> = {
  delay_between_requests: 'seconds', // docs/build-plan/06-gui.md:972
  retry_delay: 'seconds', // docs/build-plan/06-gui.md:974
  pause_between_batches: 'seconds', // docs/build-plan/06-gui.md:976
  playlist_end: '0 = no limit', // docs/build-plan/06-gui.md:977
  max_words_per_document: 'Split compiled Markdown at this word count', // docs/build-plan/06-gui.md:978
  chunk_max_chars: 'Smart TTS chunking threshold', // docs/build-plan/06-gui.md:989
}

export type ReadinessFlags = {
  descriptorPresent: boolean
  portOk: boolean
  modelsDirWritable: boolean
}

/**
 * READINESS_COUNT (ST7): null until both the readiness probe and the dependency check have
 * loaded, so no count is fabricated; otherwise the number of true checks out of four.
 */
export function readinessCount(
  readiness: ReadinessFlags | undefined,
  ffmpegAvailable: boolean | undefined,
): { ready: number; total: 4 } | null {
  if (readiness === undefined || ffmpegAvailable === undefined) {
    return null
  }
  const checks = [readiness.descriptorPresent, readiness.portOk, readiness.modelsDirWritable, ffmpegAvailable]
  return { ready: checks.filter(Boolean).length, total: 4 }
}
