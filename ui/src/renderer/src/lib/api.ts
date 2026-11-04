export const BACKEND_READY_TIMEOUT_MS = 10_000

export class ApiError extends Error {
  readonly status: number
  readonly code: string
  readonly details: object | null

  constructor(status: number, code: string, message: string, details: object | null) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.details = details
  }
}

type Envelope = {
  error?: { code?: string; message?: string; details?: object | null }
}

function e2eSeamActive(): boolean {
  return (window as unknown as { __e2eSeamInstalled?: boolean }).__e2eSeamInstalled === true
}

async function resolveBackend(): Promise<[string, string]> {
  if (e2eSeamActive()) {
    return ['http://127.0.0.1:9/api/v1', 'e2e-token']
  }
  let timer: number | undefined
  const timeout = new Promise<never>((_, reject) => {
    timer = window.setTimeout(() => {
      reject(
        new ApiError(
          503,
          'BACKEND_NOT_READY',
          'Backend not ready — the request never reached the API. Check the console for python/uv spawn errors.',
          null,
        ),
      )
    }, BACKEND_READY_TIMEOUT_MS)
  })
  try {
    return await Promise.race([
      Promise.all([window.api.getBackendUrl(), window.api.getToken()]),
      timeout,
    ])
  } catch (caught) {
    if (caught instanceof ApiError) {
      throw caught
    }
    const message = caught instanceof Error ? caught.message : String(caught)
    throw new ApiError(503, 'BACKEND_NOT_READY', `Backend not ready — ${message}`, null)
  } finally {
    if (timer !== undefined) {
      window.clearTimeout(timer)
    }
  }
}

export async function apiFetch<T = undefined>(path: string, init?: RequestInit): Promise<T> {
  const [base, token] = await resolveBackend()
  const headers = new Headers(init?.headers)
  headers.set('Authorization', `Bearer ${token}`)
  const isForm = typeof FormData !== 'undefined' && init?.body instanceof FormData
  if (isForm) {
    headers.delete('Content-Type')
  } else if (!headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }
  let res: Response
  try {
    res = await window.fetch(`${base}${path}`, { ...init, headers })
  } catch (caught) {
    const message = caught instanceof Error ? caught.message : String(caught)
    throw new ApiError(503, 'FETCH_FAILED', message, null)
  }
  const raw = await res.text()
  const body: unknown = raw.length === 0 ? undefined : JSON.parse(raw)
  if (!res.ok) {
    const env = (body as Envelope | undefined)?.error
    const requestId = (env?.details as { request_id?: unknown } | null | undefined)?.request_id
    const message =
      env?.code === 'internal_error' && typeof requestId === 'string' && requestId !== ''
        ? `Internal server error (request id ${requestId})`
        : (env?.message ?? raw)
    throw new ApiError(res.status, env?.code ?? 'HTTP_ERROR', message, env?.details ?? null)
  }
  if (res.status === 204 || body === undefined) {
    return undefined as T
  }
  return body as T
}
