import { appendStdoutLog, getPublishedBackendReady } from './ipc'

export type CaptureRuntime = {
  inbox_dir: string
  hotkey: string
  copy_to_clipboard: boolean
  close_to_tray: boolean
}

export const CAPTURE_RUNTIME_DEFAULTS: CaptureRuntime = {
  inbox_dir: '~/Pictures/av-kit',
  hotkey: 'F2',
  copy_to_clipboard: false,
  close_to_tray: true,
}

export function parseCaptureRuntime(payload: unknown): CaptureRuntime {
  if (payload === null || typeof payload !== 'object' || Array.isArray(payload)) {
    return { ...CAPTURE_RUNTIME_DEFAULTS }
  }
  const record = payload as Record<string, unknown>
  return {
    inbox_dir:
      typeof record.inbox_dir === 'string' ? record.inbox_dir : CAPTURE_RUNTIME_DEFAULTS.inbox_dir,
    hotkey: typeof record.hotkey === 'string' ? record.hotkey : CAPTURE_RUNTIME_DEFAULTS.hotkey,
    copy_to_clipboard:
      typeof record.copy_to_clipboard === 'boolean'
        ? record.copy_to_clipboard
        : CAPTURE_RUNTIME_DEFAULTS.copy_to_clipboard,
    close_to_tray:
      typeof record.close_to_tray === 'boolean'
        ? record.close_to_tray
        : CAPTURE_RUNTIME_DEFAULTS.close_to_tray,
  }
}

export function captureRuntimeEqual(left: CaptureRuntime, right: CaptureRuntime): boolean {
  return (
    left.inbox_dir === right.inbox_dir &&
    left.hotkey === right.hotkey &&
    left.copy_to_clipboard === right.copy_to_clipboard &&
    left.close_to_tray === right.close_to_tray
  )
}

export type CaptureRuntimeHooks = {
  onHotkey: (accelerator: string) => void
  onWatch: (inboxDir: string) => void
}

export function applyCaptureRuntime(
  prev: CaptureRuntime,
  next: CaptureRuntime,
  hooks: CaptureRuntimeHooks,
): CaptureRuntime {
  if (prev.hotkey !== next.hotkey) {
    hooks.onHotkey(next.hotkey)
  }
  if (prev.inbox_dir !== next.inbox_dir) {
    hooks.onWatch(next.inbox_dir)
  }
  return next
}

export async function fetchCaptureRuntime(): Promise<CaptureRuntime | null> {
  const ready = getPublishedBackendReady()
  if (ready === null) {
    return null
  }
  try {
    const res = await fetch(`${ready.apiBase}/settings/capture`, {
      headers: { Authorization: `Bearer ${ready.token}` },
    })
    if (!res.ok) {
      return null
    }
    return parseCaptureRuntime(await res.json())
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err)
    appendStdoutLog(`[Capture] settings poll failed: ${message}`)
    return null
  }
}
