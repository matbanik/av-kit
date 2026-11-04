/** E2E_SHELL_LOG (MEU-84, D-17): what the E2E build asked the shell to open, in call order. */
export type E2eShellOp = 'openPath' | 'showItemInFolder'

export type E2eShellEntry = { op: E2eShellOp; target: string }

export const e2eShellLog: E2eShellEntry[] = []

export function recordE2eShell(op: E2eShellOp, target: string): void {
  e2eShellLog.push({ op, target })
}

// Playwright reads the log through app.evaluate. Only the E2E build exposes it.
if (process.env.AVKIT_E2E === '1') {
  const shellGlobal = globalThis as { __AVKIT_E2E_SHELL_LOG__?: E2eShellEntry[] }
  shellGlobal.__AVKIT_E2E_SHELL_LOG__ = e2eShellLog
}
