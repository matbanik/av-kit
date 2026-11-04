export const RENDERER_LOG_EVENT = 'av-kit:renderer-log'

export type RendererLogDetail = {
  key: string
  message: string
}

let seq = 0

export function logRenderer(level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR', message: string): void {
  seq += 1
  const detail: RendererLogDetail = {
    key: `ui:${seq}`,
    message: `${level} ${message}`,
  }
  window.dispatchEvent(new CustomEvent<RendererLogDetail>(RENDERER_LOG_EVENT, { detail }))
}
