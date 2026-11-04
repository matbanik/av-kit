/**
 * E2E-observable ledger for the queue cards' shell IPC.
 *
 * `window.api` is a `contextBridge` proxy: the object is deep-frozen and its
 * property on `window` is non-writable and non-configurable (probed against the
 * built app on 2026-09-02: `{writable:false, configurable:false, frozen:true}`).
 * A Playwright test therefore CANNOT stub `window.api.openPath` to observe that
 * a card's Open file action actually reached the shell — the assignment is
 * silently ignored, and the test sees nothing however well the card is wired.
 *
 * So the caller records the request into `window.__e2eIpc` immediately before
 * invoking the IPC, which is what `transcript-commands.ts` and `tts-commands.ts`
 * already do for the same reason. This module is the shared spelling of that
 * pattern for the converter and downloader queues, whose Open file / Show in
 * folder homes are card actions rather than page buttons (MEU-45, MEU-46).
 *
 * Outside E2E the array does not exist and this is a no-op: nothing here
 * changes production behaviour, and it never calls the IPC itself — the page
 * keeps that call, so a source scan still sees which capability it uses.
 */

/** One recorded shell request: the IPC channel and the path it carried. */
export type ShellIpcEntry = { channel: string; target: string }

/**
 * Record a shell IPC request for the E2E seam, if a test installed the ledger.
 *
 * @param channel - The `window.api` method being invoked, e.g. `openPath`.
 * @param target - Absolute path the call carries.
 */
export function recordShellIpc(channel: string, target: string): void {
  const ledger = (window as unknown as { __e2eIpc?: ShellIpcEntry[] }).__e2eIpc
  if (Array.isArray(ledger)) {
    ledger.push({ channel, target })
  }
}
