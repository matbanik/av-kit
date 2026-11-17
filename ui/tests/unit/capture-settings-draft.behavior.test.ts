/** @vitest-environment jsdom */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, render, renderHook, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement, type ReactNode } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { resetCaptureStyleStore } from '../../src/renderer/src/features/capture/capture-style-store'
import {
  CAPTURE_SETTINGS_KEY,
  useCaptureSettings,
  type CaptureForm,
} from '../../src/renderer/src/features/capture/useCaptureSettings'
import { SettingsPage } from '../../src/renderer/src/features/settings/SettingsPage'
import { SettingsValidationError } from '../../src/renderer/src/features/settings/settings-schemas'

/**
 * MEU-151 (Session 81): the Capture settings draft holds only the leaves the user changed
 * (CAPTURE_DRAFT_CHANGED_ONLY), and Save sends only those (CAPTURE_SAVE_CHANGED_ONLY). The hook runs
 * through `renderHook` in a `QueryClientProvider`, over a fetch stub whose GET answer is the mutable
 * `saved`, as settings-runtime.test.ts does. Every check is an assertion, so a Red fails by assertion.
 */

const JSON_HEADERS = { 'Content-Type': 'application/json' }

/** Every leaf differs from CAPTURE_DEFAULTS except the hotkey, so a default copied into the draft shows. */
const SAVED: CaptureForm = {
  inbox_dir: 'C:/Pictures/saved',
  hotkey: 'F2',
  copy_to_clipboard: true,
  close_to_tray: false,
  flatten_backup: false,
  backup_dir: 'C:/Backups/saved',
  annotated_format: 'jpeg',
}

/** The five leaves other than the inbox and the hotkey, each changed from SAVED. */
const NEXT_FIVE = {
  copy_to_clipboard: false,
  close_to_tray: true,
  flatten_backup: true,
  backup_dir: 'C:/Backups/next',
  annotated_format: 'webp',
} as const

let saved: CaptureForm
let puts: unknown[]
let gate: Promise<void> | null
let client: QueryClient

function hrefOf(input: RequestInfo | URL): string {
  if (typeof input === 'string') {
    return input
  }
  if (input instanceof URL) {
    return input.href
  }
  return input.url
}

function mockApi(): void {
  window.api = {
    getBackendUrl: async () => 'http://127.0.0.1:51234/api/v1',
    getToken: async () => 'gui-nonce',
    logStartupMetric: () => undefined,
    showDirectoryDialog: async () => undefined,
    showFileDialog: async () => undefined,
    showFilesDialog: async () => [],
    getPathForFile: () => 'C:/e2e/sample.mp4',
    openPath: async () => undefined,
    showItemInFolder: async () => undefined,
    readClipboardText: async () => '',
    writeClipboardText: async () => undefined,
    readTextFile: async () => ({ text: '', basename: 'x.txt' }),
    copyMcpConfig: async () => ({ ok: true as const }),
    subscribeLogs: () => () => undefined,
    getLogSnapshot: async () => [],
    getSetupReadiness: async () => ({ descriptorPresent: true, portOk: true, modelsDirWritable: true }),
    getMcpAccessStatus: async () => ({ tokenPresent: true }),
    captureRegion: async () => undefined,
    getHotkeyStatus: async () => ({ accelerator: 'F2', registered: true, inUse: false }),
    loginItemGet: async () => ({ supported: false, reason: 'not-packaged', enabled: false, minimized: false }),
    loginItemSet: async () => ({ supported: false, reason: 'not-packaged', enabled: false, minimized: false }),
    onInboxChanged: () => () => undefined,
  } as Window['api']
}

function installFetch(): void {
  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = hrefOf(input)
    const method = (init?.method ?? 'GET').toUpperCase()
    const json = (payload: unknown) => new Response(JSON.stringify(payload), { status: 200, headers: JSON_HEADERS })
    if (url.includes('/settings/capture')) {
      if (method === 'PUT') {
        const body = typeof init?.body === 'string' ? (JSON.parse(init.body) as Partial<CaptureForm>) : {}
        puts.push(body)
        saved = { ...saved, ...body }
        return json(saved)
      }
      if (gate !== null) {
        await gate
      }
      return json(saved)
    }
    if (method === 'PUT') {
      return json(typeof init?.body === 'string' ? (JSON.parse(init.body) as unknown) : {})
    }
    if (url.includes('/settings/app')) return json({ log_level: 'INFO', log_to_file: false, console_visible: true })
    if (url.includes('/settings/ui')) return json({ theme: 'dark' })
    if (url.includes('/health/dependencies')) {
      return json({ yt_dlp: { available: true }, ffmpeg: { available: true, version: '7.1' } })
    }
    if (url.includes('/settings/')) return json({})
    return new Response(JSON.stringify({ error: { message: 'unexpected' } }), { status: 422 })
  })
  vi.stubGlobal('fetch', fetchMock)
  window.fetch = fetchMock as typeof window.fetch
}

// Query results reach subscribers on a later timer, so an assertion straight after the fetch would run too early.
async function queryUpdatesReachTheHook(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
  await new Promise((resolve) => setTimeout(resolve, 0))
}

async function refetch(): Promise<void> {
  await act(async () => {
    await client.invalidateQueries({ queryKey: CAPTURE_SETTINGS_KEY })
    await queryUpdatesReachTheHook()
  })
}

function renderCaptureHook() {
  const wrapper = ({ children }: { children: ReactNode }) => createElement(QueryClientProvider, { client }, children)
  return renderHook(() => useCaptureSettings(), { wrapper }).result
}

async function loadedHook(): Promise<ReturnType<typeof renderCaptureHook>> {
  const result = renderCaptureHook()
  await vi.waitFor(() => {
    expect(result.current.ready).toBe(true)
  })
  await act(async () => {
    await queryUpdatesReachTheHook()
  })
  return result
}

async function save(result: ReturnType<typeof renderCaptureHook>): Promise<void> {
  await act(async () => {
    await result.current.save()
    await queryUpdatesReachTheHook()
  })
}

beforeEach(() => {
  resetCaptureStyleStore()
  client = new QueryClient({ defaultOptions: { queries: { retry: false, gcTime: 0 } } })
  saved = { ...SAVED }
  puts = []
  gate = null
  mockApi()
  installFetch()
})

afterEach(() => {
  cleanup()
  client.clear()
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})

describe('MEU-151 CAPTURE_DRAFT_CHANGED_ONLY and CAPTURE_SAVE_CHANGED_ONLY in useCaptureSettings', () => {
  it('AC-151.1 a refetch reaches every leaf the draft did not change', async () => {
    const result = await loadedHook()
    act(() => {
      result.current.patchForm({ inbox_dir: 'X' })
    })
    saved = { ...saved, ...NEXT_FIVE, hotkey: 'F3' }
    await refetch()
    expect(result.current.form).toEqual({ ...saved, inbox_dir: 'X' })
  })

  it('AC-151.2 Save after a refetch sends one PUT with only the changed leaf', async () => {
    const result = await loadedHook()
    act(() => {
      result.current.patchForm({ inbox_dir: 'X' })
    })
    saved = { ...saved, ...NEXT_FIVE, hotkey: 'F3' }
    await refetch()
    await save(result)
    expect(puts).toEqual([{ inbox_dir: 'X' }])
  })

  it('AC-151.3 an edit set back to the saved value leaves the draft, so a refetch reaches it', async () => {
    const result = await loadedHook()
    act(() => {
      result.current.patchForm({ inbox_dir: 'X' })
    })
    act(() => {
      result.current.patchForm({ hotkey: 'F9' })
    })
    act(() => {
      result.current.patchForm({ hotkey: 'F2' })
    })
    saved = { ...saved, hotkey: 'F3' }
    await refetch()
    expect(result.current.form.hotkey).toBe('F3')
    await save(result)
    expect(puts).toEqual([{ inbox_dir: 'X' }])
  })

  it('AC-151.3 a single edit set back to the saved value is not dirty, and Save sends no PUT and clears the draft', async () => {
    const result = await loadedHook()
    act(() => {
      result.current.patchForm({ hotkey: 'F9' })
    })
    expect(result.current.isDirty).toBe(true)
    act(() => {
      result.current.patchForm({ hotkey: 'F2' })
    })
    expect(result.current.isDirty).toBe(false)
    await save(result)
    expect(puts).toEqual([])
    saved = { ...saved, hotkey: 'F4' }
    await refetch()
    expect(result.current.form.hotkey).toBe('F4')
  })

  it('AC-151.3 an edit that a refetch makes equal to the new saved value sends no PUT', async () => {
    const result = await loadedHook()
    act(() => {
      result.current.patchForm({ inbox_dir: 'X' })
    })
    saved = { ...saved, inbox_dir: 'X' }
    await refetch()
    expect(result.current.isDirty).toBe(false)
    await save(result)
    expect(puts).toEqual([])
  })

  it('AC-151.3 an edit that a refetch makes equal leaves the draft for good, so a second refetch reaches it (CS81-R1-F1)', async () => {
    const result = await loadedHook()
    act(() => {
      result.current.patchForm({ inbox_dir: 'X' })
    })
    act(() => {
      result.current.patchForm({ hotkey: 'F9' })
    })
    saved = { ...saved, hotkey: 'F9' }
    await refetch()
    expect(result.current.form.hotkey).toBe('F9')
    saved = { ...saved, hotkey: 'F3' }
    await refetch()
    expect(result.current.form.hotkey).toBe('F3')
    await save(result)
    expect(puts).toEqual([{ inbox_dir: 'X' }])
  })

  it('AC-151.4 an edit made before the first answer keeps the loaded values for the other leaves', async () => {
    let release = (): void => {}
    gate = new Promise((resolve) => {
      release = resolve
    })
    const result = renderCaptureHook()
    act(() => {
      result.current.patchForm({ hotkey: 'F9' })
    })
    gate = null
    await act(async () => {
      release()
      await vi.waitFor(() => {
        expect(client.getQueryState(CAPTURE_SETTINGS_KEY)?.status).toBe('success')
      })
      await queryUpdatesReachTheHook()
    })
    expect(result.current.form).toEqual({ ...SAVED, hotkey: 'F9' })
  })

  it('AC-151.5 a merged form the capture schema refuses makes Save reject and sends no PUT', async () => {
    const result = await loadedHook()
    act(() => {
      result.current.patchForm({ annotated_format: 'gif' as unknown as CaptureForm['annotated_format'] })
    })
    let refused: unknown = null
    await act(async () => {
      try {
        await result.current.save()
      } catch (error) {
        refused = error
      }
    })
    expect(refused).toBeInstanceOf(SettingsValidationError)
    expect(puts).toEqual([])
  })

  it('AC-151.6 after a successful Save a later answer shows in every leaf, the saved one included', async () => {
    const result = await loadedHook()
    act(() => {
      result.current.patchForm({ inbox_dir: 'X' })
    })
    await save(result)
    expect(puts).toHaveLength(1)
    expect(result.current.isDirty).toBe(false)
    saved = { ...NEXT_FIVE, inbox_dir: 'C:/Pictures/later', hotkey: 'F6' }
    await refetch()
    expect(result.current.form).toEqual(saved)
    expect(result.current.isDirty).toBe(false)
  })
})

describe('MEU-151 the Settings page Capture card keeps an edit across a refetch', () => {
  it('AC-151.8 a refetch changes the hotkey under an inbox edit, and Save sends only the inbox', async () => {
    const user = userEvent.setup()
    render(createElement(QueryClientProvider, { client }, createElement(SettingsPage)))
    await vi.waitFor(() => {
      expect(screen.queryByTestId('settings-leaf-capture-inbox_dir')).not.toBeNull()
    })
    const inbox = screen.getByTestId('settings-leaf-capture-inbox_dir') as HTMLInputElement
    await vi.waitFor(() => {
      expect(inbox.value).toBe('C:/Pictures/saved')
    })
    await user.clear(inbox)
    await user.type(inbox, 'C:/Pictures/edited')
    saved = { ...saved, hotkey: 'F3' }
    await refetch()
    expect((screen.getByTestId('settings-leaf-hotkey') as HTMLInputElement).value).toBe('F3')
    expect(inbox.value).toBe('C:/Pictures/edited')
    await user.click(screen.getByTestId('capture-settings-save'))
    await act(async () => {
      await queryUpdatesReachTheHook()
    })
    await vi.waitFor(() => {
      expect(puts).toHaveLength(1)
    })
    expect(puts).toEqual([{ inbox_dir: 'C:/Pictures/edited' }])
  })
})
