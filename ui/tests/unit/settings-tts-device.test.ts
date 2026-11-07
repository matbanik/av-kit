/** @vitest-environment jsdom */
/**
 * MEU-118 AC-118.2 and AC-118.3: the Settings device select offers what the backend reports for
 * this build (`DEVICE_OPTIONS`, from `GET /models/available`), and keeps a stored value it can't
 * offer without rewriting it (D-314).
 */

import { QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { g30StylesFor } from '../../src/renderer/src/components/ui/SelectInput'
import { SettingsPage } from '../../src/renderer/src/features/settings/SettingsPage'
import { DEBOUNCE_MS } from '../../src/renderer/src/features/settings/useSettingsPage'
import { queryClient } from '../../src/renderer/src/lib/query-client'

const TTS_KEY = ['settings', 'tts']
const MODELS_KEY = ['models', 'available']

function mockApi(): void {
  window.api = {
    getBackendUrl: async () => 'http://127.0.0.1:51234/api/v1',
    getToken: async () => 'gui-nonce',
    logStartupMetric: () => undefined,
    showDirectoryDialog: async () => 'C:/e2e/outdir',
    showFileDialog: async () => 'C:/e2e/sample.txt',
    showFilesDialog: async () => ['C:/e2e/sample.mp4'],
    getPathForFile: () => 'C:/e2e/sample.mp4',
    openPath: async () => undefined,
    showItemInFolder: async () => undefined,
    readClipboardText: async () => '',
    writeClipboardText: async () => undefined,
    readTextFile: async () => ({ text: '', basename: 'x.txt' }),
    copyMcpConfig: async () => ({ ok: true as const }),
    subscribeLogs: () => () => undefined,
    getLogSnapshot: async () => [],
    getSetupReadiness: async () => ({
      descriptorPresent: false,
      portOk: false,
      modelsDirWritable: false,
      logFilePath: 'C:/Users/test/AppData/Local/av-kit/logs/console.log',
    }),
    getMcpAccessStatus: async () => ({ tokenPresent: true }),
    captureRegion: async () => undefined,
    getHotkeyStatus: async () => ({ accelerator: 'F2', registered: true, inUse: false }),
    loginItemGet: async () => ({ supported: false, reason: 'not-packaged', enabled: false, minimized: false }),
    loginItemSet: async () => ({ supported: false, reason: 'not-packaged', enabled: false, minimized: false }),
    onInboxChanged: () => () => undefined,
  }
}

function jsonResponse(payload: unknown, status = 200): Response {
  return new Response(JSON.stringify(payload), { status, headers: { 'Content-Type': 'application/json' } })
}

const PYTORCH_REASON = "This build can't run PyTorch models. Choose an ONNX model."

function row(id: string, devices: string[], available = true): Record<string, unknown> {
  return {
    id,
    name: id,
    format: id.includes('onnx') ? 'ONNX' : 'PyTorch',
    precision: 'FP32',
    size_bytes: 1,
    path: null,
    is_downloaded: false,
    devices,
    available,
    reason: available ? null : PYTORCH_REASON,
  }
}

// A packaged CPU build: the PyTorch row is unavailable, the ONNX rows list auto and cpu.
const CPU_REPORT = [
  row('kokoro-pt-fp32', ['auto', 'cpu'], false),
  row('kokoro-onnx-fp32', ['auto', 'cpu']),
  row('kokoro-onnx-int8', ['auto', 'cpu']),
]
const CUDA_REPORT = [row('kokoro-pt-fp32', ['auto', 'cuda', 'cpu']), row('kokoro-onnx-fp32', ['auto', 'cuda', 'cpu'])]

describe('MEU-118 Settings TTS device options', () => {
  let storedDevice: string
  // Setup only: how GET /models/available answers.
  let report: Array<Record<string, unknown>> | 'pending' | 'error'
  const puts: Array<Record<string, unknown>> = []

  async function renderSettingsPage(): Promise<void> {
    await act(async () => {
      render(createElement(QueryClientProvider, { client: queryClient }, createElement(SettingsPage)))
    })
  }

  /**
   * Setup sync: the TTS settings have loaded, the catalog query has reached `status`, and the
   * page has rendered it. The query notifies its observers on a `setTimeout(0)`, so a timer
   * queued after the state change runs after that notification.
   */
  async function settled(status: 'pending' | 'success' | 'error'): Promise<void> {
    await vi.waitFor(() => {
      expect(queryClient.getQueryState(TTS_KEY)?.status).toBe('success')
      expect(queryClient.getQueryState(MODELS_KEY)?.status).toBe(status)
    })
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0))
    })
  }

  const deviceSelect = (): HTMLSelectElement => screen.getByTestId('settings-leaf-device') as HTMLSelectElement
  const deviceValues = (): string[] => Array.from(deviceSelect().options).map((option) => option.value)
  // Waits one debounce window past the last change, so a scheduled PUT would have been sent.
  const afterDebounce = async (): Promise<void> => {
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, DEBOUNCE_MS + 100))
    })
  }

  afterEach(() => {
    cleanup()
    queryClient.setQueryDefaults(MODELS_KEY, {})
    vi.restoreAllMocks()
    vi.unstubAllGlobals()
  })

  beforeEach(() => {
    storedDevice = 'auto'
    report = CPU_REPORT
    puts.length = 0
    mockApi()
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input)
        const method = (init?.method ?? 'GET').toUpperCase()
        if (url.includes('/settings/tts') && method === 'PUT' && typeof init?.body === 'string') {
          puts.push(JSON.parse(init.body) as Record<string, unknown>)
          return jsonResponse({})
        }
        if (url.includes('/settings/tts') && method === 'GET') {
          return jsonResponse({ models_directory: 'C:/models', device: storedDevice })
        }
        if (url.includes('/models/available')) {
          if (report === 'pending') {
            return new Promise<Response>(() => undefined)
          }
          if (report === 'error') {
            return jsonResponse({ error: { code: 'internal_error', message: 'Internal server error', details: null } }, 500)
          }
          return jsonResponse({ items: report })
        }
        if (url.includes('/health/dependencies')) {
          return jsonResponse({
            yt_dlp: { available: true, version: '2026.08.30' },
            ffmpeg: { available: true, version: '7.1', path: 'C:/ffmpeg/bin/ffmpeg.exe' },
          })
        }
        if (url.includes('/models/download-runtime')) {
          return jsonResponse({ state: 'Idle', variant_id: null, asset: null, fraction: 0 })
        }
        return jsonResponse({})
      }),
    )
    queryClient.clear()
  })

  it('AC-118.2 a CPU-only report offers exactly auto and cpu, each with the G30 pair', async () => {
    await renderSettingsPage()
    await settled('success')
    expect(deviceValues()).toEqual(['auto', 'cpu'])
    expect(deviceSelect().value).toBe('auto')
    const pair = g30StylesFor(document.documentElement.classList.contains('dark') ? 'dark' : 'light')
    const probe = document.createElement('div')
    probe.style.backgroundColor = pair.backgroundColor
    probe.style.color = pair.color
    for (const option of Array.from(deviceSelect().options)) {
      expect({ backgroundColor: option.style.backgroundColor, color: option.style.color }, option.value).toEqual({
        backgroundColor: probe.style.backgroundColor,
        color: probe.style.color,
      })
    }
  })

  it('AC-118.2 a CUDA report offers auto, cuda and cpu', async () => {
    report = CUDA_REPORT
    await renderSettingsPage()
    await settled('success')
    expect(deviceValues()).toEqual(['auto', 'cuda', 'cpu'])
  })

  it('AC-118.2 choosing cpu sends one PUT with the device', async () => {
    await renderSettingsPage()
    await settled('success')
    expect(deviceValues()).toEqual(['auto', 'cpu'])
    await userEvent.setup().selectOptions(deviceSelect(), 'cpu')
    await vi.waitFor(() => expect(puts).toEqual([{ device: 'cpu' }]))
    await afterDebounce()
    expect(puts).toEqual([{ device: 'cpu' }])
  })

  it('AC-118.3 a stored cuda with a CPU-only report shows auto and sends no PUT', async () => {
    storedDevice = 'cuda'
    await renderSettingsPage()
    await settled('success')
    expect(deviceValues()).toEqual(['auto', 'cpu'])
    expect(deviceSelect().value).toBe('auto')
    await afterDebounce()
    expect(puts).toEqual([])
  })

  it('AC-118.3 while the report is pending, the floor plus the stored cuda, and cuda shows', async () => {
    storedDevice = 'cuda'
    report = 'pending'
    await renderSettingsPage()
    await settled('pending')
    expect(deviceValues()).toEqual(['auto', 'cuda', 'cpu'])
    expect(deviceSelect().value).toBe('cuda')
    await afterDebounce()
    expect(puts).toEqual([])
  })

  it('AC-118.3 when the report answers 500, the floor plus the stored cuda, and cuda shows', async () => {
    storedDevice = 'cuda'
    report = 'error'
    // Setup only: no retries, so the query reaches its failed state at once.
    queryClient.setQueryDefaults(MODELS_KEY, { retry: false })
    await renderSettingsPage()
    await settled('error')
    expect(deviceValues()).toEqual(['auto', 'cuda', 'cpu'])
    expect(deviceSelect().value).toBe('cuda')
    await afterDebounce()
    expect(puts).toEqual([])
  })
})
