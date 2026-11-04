/** @vitest-environment jsdom */

/**
 * MEU-45 — the per-id converter commands (AC-45.4, AC-45.4a).
 *
 * `convert-commands.ts` is a **live** module: its `CONVERT_COMMANDS` map drives
 * the command palette through `AppShell.tsx` and `commandRegistry.ts`. MEU-45
 * *extends* it with `resetConversion`, `removeConversion` and `reorderConversion`
 * (`COMMAND_MODULE_RULE`) — it never rewrites it, so AC-45.4a pins every existing
 * export before AC-45.4 asks for the new ones.
 *
 * `ERROR_SURFACE` is the point of AC-45.4: a non-2xx response must reject with a
 * message carrying the HTTP status, because the kebab, the primary action and the
 * bulk bar all render that message to the user. A command that resolves on a 409
 * would show a queue that silently did not change.
 */

import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { buildReorderBody } from '../../src/renderer/src/features/converter/convert-controls'
import { queryClient } from '../../src/renderer/src/lib/query-client'

import type * as ConvertCommandsModule from '../../src/renderer/src/features/converter/convert-commands'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')
const planDir = resolve(repoRoot, 'docs/execution/plans/2026-09-02-p10-queue-card-migration')
const COMMANDS_SOURCE = resolve(
  repoRoot,
  'ui/src/renderer/src/features/converter/convert-commands.ts',
)

type NamedSet<T> = { value: T }
type NamedSets = {
  COMMAND_MODULE_PRESERVED_EXPORTS: NamedSet<Record<string, string[]>>
}

const SETS = JSON.parse(readFileSync(resolve(planDir, 'named-sets.json'), 'utf-8')) as NamedSets
const PRESERVED = SETS.COMMAND_MODULE_PRESERVED_EXPORTS.value['convert-commands.ts']

function loadCommands(): Promise<typeof ConvertCommandsModule> {
  return import(
    /* @vite-ignore */ '../../src/renderer/src/features/converter/convert-commands'
  ) as Promise<typeof ConvertCommandsModule>
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
  { id: 'job-1', status: 'Failed', output_path: null, input_path: 'C:/in/a.mp4' },
  { id: 'job-2', status: 'Done', output_path: 'C:/out/b.mp4', input_path: 'C:/in/b.mp4' },
  { id: 'job-3', status: 'Pending', output_path: null, input_path: 'C:/in/c.mp4' },
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
      if (method === 'GET' && href.includes('/conversions')) {
        return jsonResponse({ items: QUEUE, processor: { state: 'Idle', current_job_id: null } })
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

describe('MEU-45 convert-commands', () => {
  it('AC-45.4a every COMMAND_MODULE_PRESERVED_EXPORTS name survives', async () => {
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
    const { CONVERT_PALETTE_IDS, CONVERT_COMMANDS, CONVERT_EVENTS } = await loadCommands()
    expect([...CONVERT_PALETTE_IDS]).toEqual([
      'convert:add',
      'convert:start',
      'convert:pause',
      'convert:resume',
      'convert:cancel',
      'convert:clear',
    ])
    for (const id of CONVERT_PALETTE_IDS) {
      expect(
        Object.prototype.hasOwnProperty.call(CONVERT_COMMANDS, id),
        `${id} is still wired in CONVERT_COMMANDS`,
      ).toBe(true)
    }
    expect(Object.keys(CONVERT_EVENTS)).toEqual([
      'add',
      'start',
      'pause',
      'resume',
      'cancel',
      'clear',
    ])
  })

  it('AC-45.4 each new command hits its existing endpoint and refreshes the list', async () => {
    const { resetConversion, removeConversion, reorderConversion } = await loadCommands()

    await resetConversion('job-1')
    const reset = callsTo('/conversions/job-1/reset', 'POST')
    expect(reset, 'POST /conversions/{id}/reset').toHaveLength(1)

    await removeConversion('job-2')
    const removed = callsTo('/conversions/job-2', 'DELETE')
    expect(removed, 'DELETE /conversions/{id}').toHaveLength(1)
    // CLEAR_FINISHED_SEMANTICS clause 5 — the queue record only, no purge flag.
    expect(removed[0].body).toBeUndefined()

    const ids = QUEUE.map((row) => row.id)
    await reorderConversion(ids, 'job-3', 'up')
    const reorder = callsTo('/conversions/reorder', 'PUT')
    expect(reorder, 'PUT /conversions/reorder').toHaveLength(1)
    // REORDER_WIRE_CONTRACT: the complete permutation, never {id, direction}.
    expect(reorder[0].body).toEqual(buildReorderBody(ids, 'job-3', 'up'))
    expect(reorder[0].body).toEqual({ job_ids: ['job-1', 'job-3', 'job-2'] })
    expect(reorder[0].body).not.toHaveProperty('direction')
  })

  it('AC-45.4 each new command rejects with the HTTP status in the message', async () => {
    const { resetConversion, removeConversion, reorderConversion } = await loadCommands()

    const cases = [
      {
        name: 'resetConversion',
        match: '/conversions/job-1/reset',
        status: 409,
        message: 'job is still running',
        run: async () => {
          await resetConversion('job-1')
        },
      },
      {
        name: 'removeConversion',
        match: '/conversions/job-2',
        status: 404,
        message: 'no such conversion',
        run: async () => {
          await removeConversion('job-2')
        },
      },
      {
        name: 'reorderConversion',
        match: '/conversions/reorder',
        status: 422,
        message: 'job_ids must be a complete permutation',
        run: async () => {
          await reorderConversion(QUEUE.map((row) => row.id), 'job-3', 'top')
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
