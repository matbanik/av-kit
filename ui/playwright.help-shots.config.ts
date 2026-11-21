/**
 * MEU-162 (Session 99, HELP_SHOTS_GEN, D-1292) the help screenshot generator:
 * `npm run help:shots` after `npm run build`. The normal `test:e2e` config (`testDir ./tests/e2e`)
 * never runs these files.
 */

import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './tests/help-shots',
  testMatch: '*.shots.ts',
  timeout: 300_000,
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [['list']],
  use: {
    trace: 'off',
  },
})
