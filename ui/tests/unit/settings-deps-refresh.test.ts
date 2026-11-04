/** @vitest-environment jsdom */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, renderHook } from '@testing-library/react'
import { createElement, type ReactNode } from 'react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { useSettingsPage } from '../../src/renderer/src/features/settings/useSettingsPage'
import { QUERY_HEALTH_DEPENDENCIES } from '../../src/renderer/src/features/tts/tts-assets'

const JSON_HEADERS = { 'Content-Type': 'application/json' }

function harness(options: { failPut?: boolean } = {}) {
  Object.defineProperty(window, 'api', {
    configurable: true,
    value: {
      getBackendUrl: vi.fn(async () => 'http://127.0.0.1:51234/api/v1'),
      getToken: vi.fn(async () => 'gui-nonce'),
    },
  })
  const fetchMock = vi.fn(async (_url: string, init?: RequestInit) => {
    if (init?.method === 'PUT') {
      if (options.failPut === true) {
        return new Response(
          JSON.stringify({ error: { code: 'validation_error', message: 'Request validation failed', details: null } }),
          { status: 422, headers: JSON_HEADERS },
        )
      }
      return new Response(typeof init.body === 'string' ? init.body : '{}', { status: 200, headers: JSON_HEADERS })
    }
    return new Response('{}', { status: 200, headers: JSON_HEADERS })
  })
  vi.stubGlobal('fetch', fetchMock)
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  const invalidate = vi.spyOn(client, 'invalidateQueries')
  const wrapper = ({ children }: { children: ReactNode }) => createElement(QueryClientProvider, { client }, children)
  const { result } = renderHook(() => useSettingsPage(), { wrapper })
  return { result, invalidate, fetchMock }
}

type InvalidateSpy = ReturnType<typeof harness>['invalidate']

function depsInvalidationOrder(invalidate: InvalidateSpy): number[] {
  const wanted = JSON.stringify(QUERY_HEALTH_DEPENDENCIES)
  return invalidate.mock.calls.flatMap(([filters], index) =>
    JSON.stringify((filters as { queryKey?: unknown } | undefined)?.queryKey) === wanted
      ? [invalidate.mock.invocationCallOrder[index]]
      : [],
  )
}

describe('AC-78.8 DEPS_REFRESH', () => {
  afterEach(() => {
    cleanup()
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

  it('AC-78.8 a downloader ffmpeg_path PUT invalidates the dependencies query after it resolves', async () => {
    const { result, invalidate, fetchMock } = harness()
    expect(typeof result.current.putNow).toBe('function')
    await act(async () => {
      await result.current.putNow('downloader', { ffmpeg_path: 'C:/bin/ffmpeg.exe' })
    })
    const putIndex = fetchMock.mock.calls.findIndex(([, init]) => init?.method === 'PUT')
    expect(putIndex).toBeGreaterThanOrEqual(0)
    const deps = depsInvalidationOrder(invalidate)
    expect(deps).toHaveLength(1)
    expect(deps[0]).toBeGreaterThan(fetchMock.mock.invocationCallOrder[putIndex])
  })

  it('AC-78.8 [neg] a quality PUT, a ui PUT and a failed ffmpeg_path PUT leave the dependencies query alone', async () => {
    const ok = harness()
    await act(async () => {
      await ok.result.current.putNow('downloader', { quality: '1080p' })
      await ok.result.current.putNow('ui', { theme: 'light' })
    })
    expect(ok.fetchMock.mock.calls.filter(([, init]) => init?.method === 'PUT')).toHaveLength(2)
    expect(depsInvalidationOrder(ok.invalidate)).toEqual([])
    cleanup()

    const failed = harness({ failPut: true })
    await act(async () => {
      await failed.result.current.putNow('downloader', { ffmpeg_path: 'C:/bin/ffmpeg.exe' })
    })
    expect(failed.fetchMock.mock.calls.filter(([, init]) => init?.method === 'PUT')).toHaveLength(1)
    expect(depsInvalidationOrder(failed.invalidate)).toEqual([])
  })
})
