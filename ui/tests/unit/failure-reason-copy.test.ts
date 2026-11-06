/**
 * MEU-115 failure-reason copy (AC-115.15, AC-115.16): errors always reach the
 * log file (D-247), and the transcript help names the next step after a block.
 */
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

import { SETTINGS_HELP_SECTIONS } from '../../src/renderer/src/features/settings/settings-help-content'
import { TRANSCRIPT_HELP_SECTIONS } from '../../src/renderer/src/features/transcript/transcript-help-content'

const here = dirname(fileURLToPath(import.meta.url))
const rendererDir = resolve(here, '../../src/renderer/src')

function source(relative: string): string {
  return readFileSync(resolve(rendererDir, relative), 'utf8').replace(/\s+/g, ' ')
}

describe('MEU-115 failure-reason copy', () => {
  it('AC-115.15 the Settings hint, Settings help and Console panel say errors always go to the file', () => {
    const settingsPage = source('features/settings/SettingsPage.tsx')
    expect(settingsPage).toContain(
      'hint="Errors are always written to this file. Turn on Log to file to write every Console line there too."',
    )
    expect(settingsPage).toContain('Persist to {consoleLogFileLabel(readiness?.logFilePath)}')
    const consoleHelp = SETTINGS_HELP_SECTIONS.find((section) => section.id === 'console')
    expect(consoleHelp?.body).toBe(
      'Set log_level, log_to_file, and console_visible under app settings. Errors are always written to ' +
        '{app_data}/logs/console.log; Log to file adds every other line. That path is not configurable. ' +
        'Open the console panel from the header.',
    )
    expect(source('components/layout/ConsolePanel.tsx')).toContain(
      '<p data-testid="console-log-file-path">Errors always go to {CONSOLE_LOG_FILE_SPEC_PATH}. Turn this on for every line.</p>',
    )
  })

  it('AC-115.16 the transcript help has a blocked section after rate that names Resume', () => {
    const ids = TRANSCRIPT_HELP_SECTIONS.map((section) => section.id)
    expect(ids).toEqual(['resume', 'cancelled', 'requeue', 'compile', 'rate', 'blocked'])
    const blocked = TRANSCRIPT_HELP_SECTIONS.find((section) => section.id === 'blocked')
    expect(blocked?.body).toBe(
      'When YouTube blocks caption requests, the job pauses with that reason and makes no more requests. ' +
        'Resume tries again; another network often works sooner.',
    )
  })
})
