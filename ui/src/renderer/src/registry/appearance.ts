import { putSettingsNamespace } from '../features/settings/useSettingsPage'
import { queryClient } from '../lib/query-client'
import { logRenderer } from '../lib/renderer-log'
import type { UiTheme } from '../lib/theme'

/** Saves `ui.theme` through the Settings PUT path (APPEARANCE); a failure is logged, never thrown. */
export function setAppearance(theme: UiTheme): void {
  void putSettingsNamespace(queryClient, 'ui', { theme }).catch((error: unknown) => {
    const message = error instanceof Error ? error.message : String(error)
    logRenderer('ERROR', `Appearance: ${message}`)
  })
}
