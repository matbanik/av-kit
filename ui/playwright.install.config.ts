// The install stage's config (Session 106, HOST_PAYLOAD): run-e2e.ps1 runs it on the remote E2E
// host only, after the main and gated stages, with AVKIT_E2E_PAYLOAD_DIR set for its own process.
// It has no global setup: the installed app is started by its own exe, not by the dev build.
import { defineConfig, type ReporterDescription } from '@playwright/test'

const jsonOut = process.env.PLAYWRIGHT_JSON_OUTPUT_NAME
const reporter: ReporterDescription[] = jsonOut
  ? [
      ['json', { outputFile: jsonOut }],
      ['list'],
    ]
  : [['list']]

export default defineConfig({
  testDir: './tests/e2e-install',
  testMatch: ['*.test.ts'],
  // One silent install, a start, a stop and a silent uninstall of a 370 MB installer.
  timeout: 20 * 60_000,
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter,
  use: {
    trace: 'off',
  },
})
