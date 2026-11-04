/** @vitest-environment jsdom */

/**
 * MEU-46 — the per-id downloader commands (AC-46.1, AC-46.1a).
 *
 * `download-commands.ts` is a **live** module: `DOWNLOAD_COMMANDS` drives the
 * command palette through `AppShell.tsx:5` and `commandRegistry.ts:3`, and
 * `DownloaderPage.tsx:36` imports from it directly. MEU-46 *extends* it with
 * `resetDownload`, `removeDownload` and `reorderDownload` (`COMMAND_MODULE_RULE`)
 * — it never rewrites it, so AC-46.1a pins every existing export before AC-46.1
 * asks for the new ones.
 *
 * `ERROR_SURFACE` is the point of AC-46.1: a non-2xx response must reject with a
 * message carrying the HTTP status, because the kebab and the primary action both
 * render that message to the user. A command that resolved on a 409 would show a
 * queue that silently did not change.
 */

import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { buildReorderBody } from '../../src/renderer/src/features/downloader/download-controls'
import { queryClient } from '../../src/renderer/src/lib/query-client'

import type * as DownloadCommandsModule from '../../src/renderer/src/features/downloader/download-commands'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')
const planDir = resolve(repoRoot, 'docs/execution/plans/2026-09-02-p10-queue-card-migration')
const COMMANDS_SOURCE = resolve(
  repoRoot,
  'ui/src/renderer/src/features/downloader/download-commands.ts',
)

type NamedSet<T> = { value: T }
type NamedSets = {
  COMMAND_MODULE_PRESERVED_EXPORTS: NamedSet<Record<string, string[]>>
}

const SETS = JSON.parse(readFileSync(resolve(planDir, 'named-sets.json'), 'utf-8')) as NamedSets
const PRESERVED = SETS.COMMAND_MODULE_PRESERVED_EXPORTS.value['download-commands.ts']

function loadCommands(): Promise<typeof DownloadCommandsModule> {
  return import(
    /* @vite-ignore */ '../../src/renderer/src/features/downloader/download-commands'
  ) as Promise<typeof DownloadCommandsModule>
}

type FetchCall = { url: string; method: string; body?: unknown }

const fetches: FetchCall[] = []

function jsonResponse(payload: unknown, status = 200): Response {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

/** Per-path status overrides, so one case can fail exactly one endpoint. */
let failures: { match: string; status: number; message: string }[] = []

const QUEUE = [
  { id: 'dl-1', status: 'Failed', file_path: null, queue_position: 1 },
  { id: 'dl-2', status: 'Done', file_path: 'C:/out/b.mp4', queue_position: 2 },
  { id: 'dl-3', status: 'Pending', file_path: null, queue_position: 3 },
]

beforeEach(() => {
  fetches.length = 0
  failures = []
  queryClient.clear()
  window.api = {
    getBackendUrl: async () => 'http://127.0.0.1:51234/api/v1',
    getToken: async () => 'unit-nonce',
    loginItemGet: async () => ({
      supported: false,
      reason: 'not-packaged',
      enabled: false,
      minimized: false,
    }),
    loginItemSet: async () => ({
      supported: false,
      reason: 'not-packaged',
      enabled: false,
      minimized: false,
    }),
  } as unknown as typeof window.api
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url: string, init?: RequestInit) => {
      const method = (init?.method ?? 'GET').toUpperCase()
      let body: unknown
      if (typeof init?.body === 'string' && init.body.length > 0) {
        body = JSON.parse(init.body)
      }
      const href = String(url)
      fetches.push({ url: href, method, body })

      const failure = failures.find((row) => href.includes(row.match) && method !== 'GET')
      if (failure !== undefined) {
        return jsonResponse(
          { error: { code: 'CONFLICT', message: failure.message } },
          failure.status,
        )
      }
      if (method === 'GET' && href.includes('/downloads')) {
        return jsonResponse({ items: QUEUE, processor: { state: 'Idle' } })
      }
      return new Response(null, { status: 204 })
    }),
  )
})

afterEach(() => {
  vi.unstubAllGlobals()
  queryClient.clear()
})

function callsTo(fragment: string, method: string): FetchCall[] {
  return fetches.filter((row) => row.url.includes(fragment) && row.method === method)
}

describe('MEU-46 download-commands', () => {
  it('AC-46.1a every COMMAND_MODULE_PRESERVED_EXPORTS name survives', async () => {
    const commands = (await loadCommands()) as unknown as Record<string, unknown>
    const source = readFileSync(COMMANDS_SOURCE, 'utf-8')

    expect(PRESERVED.length, 'the preserved-export list is non-empty').toBeGreaterThan(0)
    for (const name of PRESERVED) {
      if (Object.prototype.hasOwnProperty.call(commands, name)) {
        expect(commands[name], `${name} is defined`).toBeDefined()
        continue
      }
      // A type-only export has no runtime binding; it still has to exist, so it
      // is pinned against the source rather than the module namespace.
      expect(
        new RegExp(`export (type|interface) ${name}\\b`).test(source),
        `${name} survives as a type export`,
      ).toBe(true)
    }

    // The palette wiring specifically: ids and command map unchanged.
    const { DOWNLOAD_PALETTE_IDS, DOWNLOAD_COMMANDS, DOWNLOAD_EVENTS } = await loadCommands()
    expect([...DOWNLOAD_PALETTE_IDS]).toEqual([
      'download:add',
      'download:start',
      'download:pause',
      'download:resume',
      'download:cancel',
      'download:clear',
      'download:sabr_check',
    ])
    for (const id of DOWNLOAD_PALETTE_IDS) {
      expect(
        Object.prototype.hasOwnProperty.call(DOWNLOAD_COMMANDS, id),
        `${id} is still wired in DOWNLOAD_COMMANDS`,
      ).toBe(true)
    }
    expect(Object.keys(DOWNLOAD_EVENTS)).toEqual([
      'add',
      'start',
      'pause',
      'resume',
      'cancel',
      'clear',
      'sabrCheck',
    ])
  })

  it('AC-46.1 each new command hits its existing endpoint and refreshes the list', async () => {
    const { resetDownload, removeDownload, reorderDownload } = await loadCommands()

    await resetDownload('dl-1')
    const reset = callsTo('/downloads/dl-1/reset', 'POST')
    expect(reset, 'POST /downloads/{id}/reset').toHaveLength(1)

    await removeDownload('dl-2')
    const removed = callsTo('/downloads/dl-2', 'DELETE')
    expect(removed, 'DELETE /downloads/{id}').toHaveLength(1)
    // CLEAR_FINISHED_SEMANTICS clause 5 — the queue record only, no purge flag.
    expect(removed[0].body).toBeUndefined()

    const ids = QUEUE.map((row) => row.id)
    await reorderDownload(ids, 'dl-3', 'up')
    const reorder = callsTo('/downloads/reorder', 'PUT')
    expect(reorder, 'PUT /downloads/reorder').toHaveLength(1)
    // REORDER_WIRE_CONTRACT: the complete permutation, never {id, direction}.
    expect(reorder[0].body).toEqual(buildReorderBody(ids, 'dl-3', 'up'))
    expect(reorder[0].body).toEqual({ job_ids: ['dl-1', 'dl-3', 'dl-2'] })
    expect(reorder[0].body).not.toHaveProperty('direction')
  })

  it('AC-46.1 each new command rejects with the HTTP status in the message', async () => {
    const { resetDownload, removeDownload, reorderDownload } = await loadCommands()

    const cases = [
      {
        name: 'resetDownload',
        match: '/downloads/dl-1/reset',
        status: 409,
        message: 'job is still running',
        run: async () => {
          await resetDownload('dl-1')
        },
      },
      {
        name: 'removeDownload',
        match: '/downloads/dl-2',
        status: 404,
        message: 'no such download',
        run: async () => {
          await removeDownload('dl-2')
        },
      },
      {
        name: 'reorderDownload',
        match: '/downloads/reorder',
        status: 422,
        message: 'job_ids must be a complete permutation',
        run: async () => {
          await reorderDownload(QUEUE.map((row) => row.id), 'dl-3', 'top')
        },
      },
    ]

    for (const scenario of cases) {
      failures = [
        { match: scenario.match, status: scenario.status, message: scenario.message },
      ]
      let caught: unknown
      try {
        await scenario.run()
      } catch (error) {
        caught = error
      }
      expect(caught, `${scenario.name} never resolves silently`).toBeInstanceOf(Error)
      const failure = caught as Error & { status?: number }
      expect(failure.status, `${scenario.name} carries the status`).toBe(scenario.status)
      expect(
        failure.message,
        `${scenario.name} message carries the status`,
      ).toContain(String(scenario.status))
      expect(
        failure.message,
        `${scenario.name} message keeps the server's reason`,
      ).toContain(scenario.message)
    }
  })
})
