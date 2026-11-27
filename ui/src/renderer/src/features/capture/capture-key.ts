/**
 * MEU-165 CAPTURE_KEY_TOKEN: a text that names the capture key holds `{captureKey}`, and this one
 * formatter replaces it. The module imports nothing, so the help texts, the quick start and the pages
 * can all read it. CAPTURE_KEY_DEFAULT is the key a fresh install saves.
 */

export const CAPTURE_KEY_DEFAULT = 'F2'

export const CAPTURE_KEY_TOKEN = '{captureKey}'

/** The template with every token replaced by the key; a blank or all-space key gives the default. */
export function captureKeyText(template: string, key: string): string {
  const shown = key.trim() === '' ? CAPTURE_KEY_DEFAULT : key
  return template.split(CAPTURE_KEY_TOKEN).join(shown)
}
