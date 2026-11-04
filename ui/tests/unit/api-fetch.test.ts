/**
 * @vitest-environment jsdom
 */
import { afterEach, describe, expect, it, vi } from 'vitest'

const VOID_204_PATHS = [
  '/downloads/job-1',
  '/downloads',
  '/transcripts/job-1',
  '/tts/job-1',
  '/models/unload',
  '/health/startup-metrics',
] as const

describe('AC-19.10 apiFetch + VOID_204_PATHS + ERROR_ENVELOPE + G17_JSON', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

  it('returns undefined on every 204 path and throws ApiError on a 422 envelope', async () => {
    const { apiFetch, ApiError } = await import('../../src/renderer/src/lib/api')
    Object.defineProperty(window, 'api', {
      configurable: true,
      value: {
        getBackendUrl: vi.fn(async () => 'http://127.0.0.1:51234/api/v1'),
        getToken: vi.fn(async () => 'gui-nonce'),
      },
    })

    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      const method = (init?.method ?? 'GET').toUpperCase()
      const isVoidPost =
        method === 'POST' &&
        (url.endsWith('/health/startup-metrics') || url.endsWith('/models/unload'))
      const isVoidDelete = method === 'DELETE' && VOID_204_PATHS.some((path) => url.endsWith(path))
      if (isVoidPost || isVoidDelete) {
        return new Response('', { status: 204 })
      }
      if (method === 'POST' && url.endsWith('/downloads')) {
        return new Response(
          JSON.stringify({
            error: { code: 'VALIDATION_ERROR', message: 'bad', details: { field: 'url' } },
          }),
          { status: 422, headers: { 'Content-Type': 'application/json' } },
        )
      }
      return new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    })
    vi.stubGlobal('fetch', fetchMock)

    for (const path of VOID_204_PATHS) {
      const method = path.includes('unload') || path.includes('startup-metrics') ? 'POST' : 'DELETE'
      await expect(apiFetch(path, { method })).resolves.toBeUndefined()
    }

    await expect(apiFetch('/downloads', { method: 'POST', body: '{}' })).rejects.toMatchObject({
      status: 422,
      code: 'VALIDATION_ERROR',
      message: 'bad',
    })
    await expect(apiFetch('/downloads', { method: 'POST', body: '{}' })).rejects.toBeInstanceOf(
      ApiError,
    )

    const form = new FormData()
    form.append('file', new Blob(['x']), 'note.txt')
    await apiFetch('/transcripts/job-1/upload', { method: 'POST', body: form })
    const formCall = fetchMock.mock.calls.find((call) => String(call[0]).includes('upload'))
    const headers = new Headers(formCall?.[1]?.headers)
    expect(headers.get('Content-Type')).not.toBe('application/json')
    expect(headers.get('Authorization')).toBe('Bearer gui-nonce')
  })

  it('rejects with BACKEND_NOT_READY when getBackendUrl never resolves', async () => {
    vi.useFakeTimers()
    const { apiFetch, ApiError, BACKEND_READY_TIMEOUT_MS } = await import('../../src/renderer/src/lib/api')
    Object.defineProperty(window, 'api', {
      configurable: true,
      value: {
        getBackendUrl: () => new Promise(() => undefined),
        getToken: () => new Promise(() => undefined),
      },
    })
    const pending = apiFetch('/downloads')
    const rejected = expect(pending).rejects.toMatchObject({
      status: 503,
      code: 'BACKEND_NOT_READY',
    })
    await vi.advanceTimersByTimeAsync(BACKEND_READY_TIMEOUT_MS)
    await rejected
    await expect(pending).rejects.toBeInstanceOf(ApiError)
    vi.useRealTimers()
  })
})

describe('AC-76.8 GUI_ERROR_TEXT', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

  function stubBackend(status: number, body: unknown): void {
    Object.defineProperty(window, 'api', {
      configurable: true,
      value: {
        getBackendUrl: vi.fn(async () => 'http://127.0.0.1:51234/api/v1'),
        getToken: vi.fn(async () => 'gui-nonce'),
      },
    })
    vi.stubGlobal(
      'fetch',
      vi.fn(
        async () =>
          new Response(JSON.stringify(body), {
            status,
            headers: { 'Content-Type': 'application/json' },
          }),
      ),
    )
  }

  it('AC-76.8 a 500 internal_error names its request id', async () => {
    const { apiFetch } = await import('../../src/renderer/src/lib/api')
    stubBackend(500, {
      error: { code: 'internal_error', message: 'Internal server error', details: { request_id: 'rid-1' } },
    })
    await expect(apiFetch('/health/dependencies')).rejects.toMatchObject({
      status: 500,
      code: 'internal_error',
      message: 'Internal server error (request id rid-1)',
    })
  })

  it('AC-76.8 [neg] no request id, or a 422, keeps the envelope message', async () => {
    const { apiFetch } = await import('../../src/renderer/src/lib/api')
    stubBackend(500, { error: { code: 'internal_error', message: 'Internal server error', details: null } })
    await expect(apiFetch('/health/dependencies')).rejects.toMatchObject({
      status: 500,
      message: 'Internal server error',
    })
    stubBackend(422, { error: { code: 'ExtractError', message: 'yt-dlp says no', details: null } })
    await expect(apiFetch('/downloads', { method: 'POST', body: '{}' })).rejects.toMatchObject({
      status: 422,
      code: 'ExtractError',
      message: 'yt-dlp says no',
    })
  })
})
