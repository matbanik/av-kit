import { applyDocumentTheme, readBootTheme } from './lib/theme'

// BOOT_THEME: the first import of main.tsx, so the shell's first paint uses the
// last applied theme. The route waits for the stored theme (AppShell THEME_GATE).
const bootTheme = readBootTheme()
if (bootTheme !== null) {
  applyDocumentTheme(bootTheme)
}
