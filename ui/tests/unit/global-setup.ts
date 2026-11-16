// Vitest global setup: install the Electron binary once, before any worker starts. Requiring the
// electron package downloads the binary when it is missing; several workers doing that at once
// raced each other. createRequire bypasses the config's electron alias, which only Vite applies.
import { existsSync } from 'node:fs'
import { createRequire } from 'node:module'

import type { TestProject } from 'vitest/node'

declare module 'vitest' {
  export interface ProvidedContext {
    electronBinary: string
  }
}

const INSTALL_COMMAND = 'node node_modules/electron/install.js'

function installError(detail: string): Error {
  return new Error(
    `The Electron binary is missing and could not be installed (${detail}). ` +
      `Run \`${INSTALL_COMMAND}\` in ui/, then run the tests again.`,
  )
}

/** The Electron binary's path, installed first when it is missing. Throws naming the install command. */
export function ensureElectronBinary(
  requireFn: (id: string) => unknown = createRequire(import.meta.url),
  exists: (path: string) => boolean = existsSync,
): string {
  let binary: unknown
  try {
    binary = requireFn('electron')
  } catch (error) {
    throw installError(error instanceof Error ? error.message : String(error))
  }
  if (typeof binary !== 'string' || !exists(binary)) {
    throw installError(`no binary at ${String(binary)}`)
  }
  return binary
}

export default function setup(project: TestProject): void {
  const binary = ensureElectronBinary()
  project.provide('electronBinary', binary)
}
