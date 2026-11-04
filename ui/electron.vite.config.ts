import { resolve } from 'node:path'

import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig, externalizeDepsPlugin } from 'electron-vite'

const primitiveHarnessBuild = process.env.AVKIT_PRIMITIVE_HARNESS_BUILD
if (primitiveHarnessBuild !== undefined && primitiveHarnessBuild !== '1') {
  throw new Error('AVKIT_PRIMITIVE_HARNESS_BUILD must be unset or exactly 1')
}

export default defineConfig({
  main: {
    plugins: [externalizeDepsPlugin()],
    build: {
      rollupOptions: {
        input: {
          index: resolve(__dirname, 'src/main/index.ts'),
        },
      },
    },
  },
  preload: {
    plugins: [externalizeDepsPlugin()],
    build: {
      rollupOptions: {
        input: {
          index: resolve(__dirname, 'src/main/preload.ts'),
        },
        output: {
          format: 'cjs',
          entryFileNames: '[name].js',
        },
      },
    },
  },
  renderer: {
    root: resolve(__dirname, 'src/renderer'),
    plugins: [
      react({
        babel: {
          plugins: [['babel-plugin-react-compiler', {}]],
        },
      }),
      tailwindcss(),
    ],
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src/renderer/src'),
      },
    },
    server: {
      host: '127.0.0.1',
      port: 5173,
    },
    build: {
      rollupOptions: {
        input: {
          index: resolve(__dirname, 'src/renderer/index.html'),
          ...(primitiveHarnessBuild === '1'
            ? { primitiveHarness: resolve(__dirname, 'src/renderer/primitive-harness.html') }
            : {}),
        },
      },
    },
  },
})
