import { describe, expect, it } from 'vitest'

import {
  CONSOLE_LOG_FILE_SPEC_PATH,
  consoleLogFileLabel,
} from '../../src/renderer/src/lib/console-log-path'

describe('console log file path label', () => {
  it('uses the spec path when no resolved path is available', () => {
    expect(CONSOLE_LOG_FILE_SPEC_PATH).toBe('{app_data}/logs/console.log')
    expect(consoleLogFileLabel(undefined)).toBe('{app_data}/logs/console.log')
    expect(consoleLogFileLabel('  ')).toBe('{app_data}/logs/console.log')
  })

  it('surfaces the resolved app-data log file path', () => {
    expect(consoleLogFileLabel('C:/Users/test/AppData/Local/av-kit/logs/console.log')).toBe(
      'C:/Users/test/AppData/Local/av-kit/logs/console.log',
    )
  })
})
