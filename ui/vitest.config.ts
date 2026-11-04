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
  },
})
