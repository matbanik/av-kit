/** CHORD_TABLE (D-146): id, chord, and the page an entry is scoped to (`undefined` = global). */
export const CHORD_TABLE: ReadonlyArray<readonly [string, string, string | undefined]> = [
  ['nav:downloader', 'Ctrl+1', undefined],
  ['nav:transcript', 'Ctrl+2', undefined],
  ['nav:tts', 'Ctrl+3', undefined],
  ['nav:convert', 'Ctrl+4', undefined],
  ['nav:capture', 'Ctrl+5', undefined],
  ['nav:settings', 'Ctrl+,', undefined],
  ['nav:collapse', 'Ctrl+B', undefined],
  ['appearance:dark', 'Ctrl+Shift+D', undefined],
  ['appearance:light', 'Ctrl+Shift+L', undefined],
  ['download:add', 'Ctrl+L', '/'],
  ['transcript:add', 'Ctrl+L', '/transcript'],
  ['convert:browse', 'Ctrl+O', '/convert'],
  ['capture:save', 'Ctrl+S', '/capture'],
  ['page:primary', 'Ctrl+Enter', undefined],
  ['console:toggle', 'Ctrl+J', undefined],
  ['help:toggle', 'F1', undefined],
]
