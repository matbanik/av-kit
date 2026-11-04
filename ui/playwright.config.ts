import { defineConfig, type ReporterDescription } from '@playwright/test'

const jsonOut = process.env.PLAYWRIGHT_JSON_OUTPUT_NAME
const reporter: ReporterDescription[] = jsonOut
  ? [
      ['json', { outputFile: jsonOut }],
      ['list'],
    ]
  : [['list']]

export default defineConfig({
  testDir: './tests/e2e',
  testMatch: ['*.test.ts', '*.spec.ts'],
  globalSetup: './tests/e2e/global-setup.ts',
  globalTeardown: './tests/e2e/global-teardown.ts',
  timeout: 60_000,
  fullyParallel: false,
  workers: 1,
  reporter,
  use: {
    trace: 'off',
  },
})
