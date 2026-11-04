import { useEffect, useState } from 'react'

import { apiFetch } from '../lib/api'
import { RENDERER_LOG_EVENT, type RendererLogDetail } from '../lib/renderer-log'

export type LogViewItem = {
  key: string
  message: string
  seq?: number
  id?: string
}

type ConsoleSnapshot = {
  items?: Array<{ seq: number; message: string; level?: string; module?: string }>
  last_seq?: number
}

export function keyRingEvent(event: { seq: number; message?: string }): string {
  return String(event.seq)
}

export function keyStdoutEvent(ipcId: string): string {
  return `ipc:${ipcId}`
}

export function mergeIntoView(current: LogViewItem[], incoming: LogViewItem[]): LogViewItem[] {
  const seen = new Set(current.map((row) => row.key))
  const next = [...current]
  for (const row of incoming) {
    if (seen.has(row.key)) {
      continue
    }
    seen.add(row.key)
    next.push(row)
  }
  return next
}

export function clearView(_current: LogViewItem[]): LogViewItem[] {
  return []
}

async function pollConsole(afterSeq: number): Promise<LogViewItem[]> {
  const snap = await apiFetch<ConsoleSnapshot>(`/health/console?after_seq=${afterSeq}`)
  const items = snap?.items ?? []
  return items.map((event) => ({
    key: keyRingEvent(event),
    message: event.message,
    seq: event.seq,
  }))
}

export const CONSOLE_POLL_OPEN_MS = 500
export const CONSOLE_POLL_CLOSED_MS = 5000

export function useBackendLogs(open: boolean): {
  items: LogViewItem[]
  lines: string[]
  clear: () => void
} {
  const [items, setItems] = useState<LogViewItem[]>([])

  useEffect(() => {
    let cancelled = false
    const api = window.api
    if (api === undefined) {
      return
    }
    void api.getLogSnapshot().then((snap) => {
      if (cancelled || !Array.isArray(snap)) {
        return
      }
      setItems((current) => mergeIntoView(current, snap as LogViewItem[]))
    })
    const unsub = api.subscribeLogs((batch) => {
      if (!Array.isArray(batch)) {
        return
      }
      setItems((current) => mergeIntoView(current, batch as LogViewItem[]))
    })
    const onRendererLog = (event: Event) => {
      const detail = (event as CustomEvent<RendererLogDetail>).detail
      if (detail === undefined || typeof detail.message !== 'string' || typeof detail.key !== 'string') {
        return
      }
      setItems((current) => mergeIntoView(current, [{ key: detail.key, message: detail.message }]))
    }
    window.addEventListener(RENDERER_LOG_EVENT, onRendererLog)
    let afterSeq = 0
    const timer = setInterval(() => {
      void pollConsole(afterSeq)
        .then((incoming) => {
          if (cancelled || incoming.length === 0) {
            return
          }
          afterSeq = incoming.reduce((max, row) => Math.max(max, row.seq ?? 0), afterSeq)
          setItems((current) => mergeIntoView(current, incoming))
        })
        .catch(() => undefined)
    }, open ? CONSOLE_POLL_OPEN_MS : CONSOLE_POLL_CLOSED_MS)
    return () => {
      cancelled = true
      unsub()
      window.removeEventListener(RENDERER_LOG_EVENT, onRendererLog)
      clearInterval(timer)
    }
  }, [open])

  return {
    items,
    lines: items.map((row) => row.message),
    clear: () => {
      setItems((current) => clearView(current))
    },
  }
}
