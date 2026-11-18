// `npm run preview`: starts `electron-vite preview` without ELECTRON_RUN_AS_NODE (Session 94,
// D-1178). With that variable set Electron runs as plain Node and no window opens, silently, as
// it did for `npm run dev` before Session 90's wrapper; this one reuses that wrapper's
// runElectronVite, so the two scripts behave the same apart from the subcommand and the notice.
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { isEntry, runElectronVite } from './electron-vite-dev.mjs'

const ui = resolve(dirname(fileURLToPath(import.meta.url)), '..')

/** The line written to stderr when the variable was removed. */
export const PREVIEW_NOTICE = 'electron-vite-preview: cleared ELECTRON_RUN_AS_NODE'

/** The arguments after the Node executable: electron-vite's own bin, `preview`, then `extra`. */
export function previewArgs(extra) {
  return [resolve(ui, 'node_modules/electron-vite/bin/electron-vite.js'), 'preview', ...extra]
}

if (isEntry(process.argv[1], import.meta.url)) runElectronVite('preview', PREVIEW_NOTICE, process.argv.slice(2))
