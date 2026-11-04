import { resolve } from 'node:path'

import { defineConfig } from 'vitest/config'

export default defineConfig({
  resolve: {
    alias: {
      electron: resolve(__dirname, 'tests/unit/helpers/electron-stub.ts'),
    },
  },
  test: {
    allowOnly: false,
    globals: true,
    environment: 'node',
    include: ['src/**/*.test.{ts,tsx}', 'tests/unit/**/*.test.{ts,tsx}'],
    setupFiles: ['@testing-library/jest-dom/vitest', './tests/unit/setup.ts'],
    // Node 25+ adds its own localStorage global, undefined without --localstorage-file, which hides
    // jsdom's storage. Vitest 5 fixes this (vitest#10867); Vitest 4 removed poolOptions, so an
    // upgrade must move or drop this line.
    poolOptions: { forks: { execArgv: ['--no-experimental-webstorage'] } },
  },
})
