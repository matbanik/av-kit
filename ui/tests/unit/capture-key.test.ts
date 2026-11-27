/**
 * MEU-165 (Session 103): the capture key in texts (CAPTURE_KEY_TOKEN, CAPTURE_KEY_DEFAULT_READING).
 * `capture-key.ts` is found through `import.meta.glob`, and the per-key readers are read through
 * namespace imports, so while they are missing each test fails by assertion and not by an import error.
 */

import { describe, expect, it } from 'vitest'

import * as quickStart from '../../src/renderer/src/components/help/quick-start'
import type { HelpFeature, QuickStartPage } from '../../src/renderer/src/components/help/quick-start'
import type { HelpSection } from '../../src/renderer/src/components/help/HelpCard'
import * as captureHelp from '../../src/renderer/src/features/capture/capture-help-content'
import * as settingsHelp from '../../src/renderer/src/features/settings/settings-help-content'

type CaptureKeyModule = {
  CAPTURE_KEY_DEFAULT: string
  captureKeyText: (template: string, key: string) => string
}

const CAPTURE_KEY_PATH = '../../src/renderer/src/features/capture/capture-key.ts'
const loaders = import.meta.glob<CaptureKeyModule>('../../src/renderer/src/features/capture/capture-key.ts')

async function captureKey(): Promise<CaptureKeyModule> {
  const load = loaders[CAPTURE_KEY_PATH]
  expect(load, 'capture-key.ts exists').toBeTypeOf('function')
  return (load as () => Promise<CaptureKeyModule>)()
}

/** A named export of a namespace import, asserted to be a function before it is used. */
function exported<T>(namespace: object, name: string): T {
  const value = (namespace as Record<string, unknown>)[name]
  expect(typeof value, `${name} is exported`).toBe('function')
  return value as T
}

const captureHelpSections = (key: string): HelpSection[] =>
  exported<(key: string) => HelpSection[]>(captureHelp, 'captureHelpSections')(key)
const settingsHelpSections = (key: string): HelpSection[] =>
  exported<(key: string) => HelpSection[]>(settingsHelp, 'settingsHelpSections')(key)
const quickStartPage = (feature: HelpFeature, key: string): QuickStartPage =>
  exported<(feature: HelpFeature, key: string) => QuickStartPage>(quickStart, 'quickStartPage')(feature, key)

/** Today's text with the key in place of `F2` (each of the eight texts names it once). */
function withKey<T>(value: T, key: string): T {
  return JSON.parse(JSON.stringify(value).replaceAll('F2', key)) as T
}

describe('MEU-165 capture key formatter and per-key readings', () => {
  it('AC-165.1 captureKeyText replaces every token and keeps the default and chords', async () => {
    const { CAPTURE_KEY_DEFAULT, captureKeyText } = await captureKey()
    expect(CAPTURE_KEY_DEFAULT).toBe('F2')
    expect(captureKeyText('Press {captureKey} or Capture region', 'F9')).toBe('Press F9 or Capture region')
    expect(captureKeyText('{captureKey} then {captureKey} again', 'F9')).toBe('F9 then F9 again')
    expect(captureKeyText('Capture never uploads.', 'F9')).toBe('Capture never uploads.')
    expect(captureKeyText('Press {captureKey} now', 'Ctrl+Shift+S')).toBe('Press Ctrl+Shift+S now')
    // A blank or all-space key gives the default, never `Press  or`.
    expect(captureKeyText('Press {captureKey} or Capture region', '')).toBe('Press F2 or Capture region')
    expect(captureKeyText('Press {captureKey} or Capture region', '   ')).toBe('Press F2 or Capture region')
  })

  it('AC-165.4 the per-key readings name the given key and keep everything else', () => {
    const capture = captureHelpSections('F9')
    expect(capture).toEqual(withKey(captureHelp.CAPTURE_HELP_SECTIONS, 'F9'))
    const captureF9 = capture.filter((section) => `${section.title} ${section.body}`.includes('F9'))
    expect(captureF9.map((section) => section.id)).toEqual(['what-capture-does', 'f2-sharex', 'close-to-tray'])
    expect(capture.find((section) => section.id === 'f2-sharex')?.title).toBe('When F9 is in use')
    expect(capture.find((section) => section.id === 'close-to-tray')?.title).toBe('Close to tray keeps F9')

    const settings = settingsHelpSections('F9')
    expect(settings.map((section) => section.id)).toEqual(
      settingsHelp.SETTINGS_HELP_SECTIONS.map((section) => section.id),
    )
    expect(settings.find((section) => section.id === 'startup')?.body).toMatch(/so F9 still works\.$/)

    const page = quickStartPage('capture', 'F9')
    expect(page.steps[0]?.text).toBe('Push F9 or click Capture region. Then drag a box on the screen.')
    expect(page.shots).toEqual(quickStart.QUICK_START.capture.shots)
    expect(page.steps.slice(1)).toEqual(quickStart.QUICK_START.capture.steps.slice(1))
    for (const feature of quickStart.HELP_FEATURES.filter((name) => name !== 'capture')) {
      expect(quickStartPage(feature, 'F9'), `${feature} page`).toBe(quickStart.QUICK_START[feature])
    }

    for (const result of [capture, settings, page]) {
      const text = JSON.stringify(result)
      expect(text).not.toContain('F2')
      expect(text).not.toContain('{captureKey}')
    }
  })

  it('AC-165.9 validateQuickStart passes the Capture page with a set key', () => {
    for (const key of ['F9', 'Ctrl+Shift+F12']) {
      const pages = { ...quickStart.QUICK_START, capture: quickStartPage('capture', key) }
      expect(quickStart.validateQuickStart(pages), key).toEqual([])
    }
  })
})
