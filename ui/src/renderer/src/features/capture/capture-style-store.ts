import type { QueryClient } from '@tanstack/react-query'

import { apiFetch } from '../../lib/api'
import { captureStylePutSchema, type CapturePut } from '../settings/settings-schemas'
import { TOOL_STYLE_LEAVES, type StyleTool, type ToolStyle } from './capture-tool-style'

/** The one query of `/settings/capture`; `useCaptureSettings` re-exports it. */
export const CAPTURE_SETTINGS_KEY = ['settings', 'capture'] as const

/** One style leaf's last commit; `succeededAt` is the counter when its PUT succeeded. */
type LeafEntry = { value: string | number; commit: number; succeededAt: number | null }

// STYLE_STORE (MEU-105, D-720): the shared write state, at module scope so every page and hook shares it.
// `counter` goes up at every commit and every settled PUT. `generation` changes on reset, so a PUT still
// queued from before a reset changes nothing after it.
let counter = 0
let generation = 0
const latest = new Map<string, LeafEntry>()
let queue: Promise<void> = Promise.resolve()
let queued = 0
let queueFailed = false
let failures = 0
const failureListeners = new Set<() => void>()
// Execution round 1 F1: the committed leaves, for a page whose first GET has not answered. The
// snapshot keeps its identity until `latest` changes, as `useSyncExternalStore` needs.
let committed: Readonly<Record<string, string | number>> = {}
const committedListeners = new Set<() => void>()

function committedChanged(): void {
  const next: Record<string, string | number> = {}
  for (const [leaf, entry] of latest) {
    next[leaf] = entry.value
  }
  committed = next
  for (const listener of committedListeners) {
    listener()
  }
}

/**
 * STYLE_STORE (round 2 F3): the shared GET of `/settings/capture`. A style leaf whose last commit had
 * not succeeded when this GET started shows that commit's value, so no GET installs an older style.
 */
export async function fetchCaptureSettings(): Promise<CapturePut> {
  const startedAt = counter
  const startedIn = generation
  const data = await apiFetch<CapturePut>('/settings/capture')
  if (startedIn !== generation || latest.size === 0 || typeof data !== 'object' || data === null) {
    return data
  }
  const merged: Record<string, unknown> = { ...data }
  for (const [leaf, entry] of latest) {
    if (entry.succeededAt === null || entry.succeededAt > startedAt) {
      merged[leaf] = entry.value
    }
  }
  return merged as CapturePut
}

/** Empties the shared style write state, for tests. */
export function resetCaptureStyleStore(): void {
  generation += 1
  counter = 0
  latest.clear()
  queue = Promise.resolve()
  queued = 0
  queueFailed = false
  failures = 0
  for (const listener of failureListeners) {
    listener()
  }
  committedChanged()
}

/** How many style PUTs have failed; the page shows `Couldn't save the tool style` when it goes up. */
export function styleSaveFailures(): number {
  return failures
}

export function subscribeStyleSaveFailures(listener: () => void): () => void {
  failureListeners.add(listener)
  return () => {
    failureListeners.delete(listener)
  }
}

/**
 * The value of every style leaf committed and not dropped by a failed PUT. The hook reads the tool
 * styles from it while the query has no data, so a commit made before the first GET answers (or after
 * it fails) still reaches the next mark. The cache itself is left empty: a partial object there would
 * make the Settings card show a loaded form.
 */
export function committedStyleLeaves(): Readonly<Record<string, string | number>> {
  return committed
}

export function subscribeCommittedStyleLeaves(listener: () => void): () => void {
  committedListeners.add(listener)
  return () => {
    committedListeners.delete(listener)
  }
}

/**
 * STYLE_STORE: save `patch` as `tool`'s style. The cache shows it at once (before the first GET answers,
 * `committedStyleLeaves` does); one PUT with only its leaves
 * waits for every earlier style PUT to settle, so the server applies them in commit order. A failure
 * drops the leaves it still owns, and once the queue is empty the query is fetched again.
 */
export function saveCaptureToolStyle(client: QueryClient, tool: StyleTool, patch: ToolStyle): void {
  const leaves = TOOL_STYLE_LEAVES[tool]
  const body: Record<string, unknown> = {}
  for (const field of Object.keys(patch) as Array<keyof ToolStyle>) {
    const leaf = leaves[field]
    const value = patch[field]
    if (leaf !== undefined && value !== undefined) {
      body[leaf] = value
    }
  }
  if (Object.keys(body).length === 0) {
    return
  }
  const parsed = captureStylePutSchema.safeParse(body)
  if (!parsed.success) {
    return
  }
  const sent: Record<string, string | number> = {}
  for (const [leaf, value] of Object.entries(parsed.data)) {
    if (value !== undefined) {
      sent[leaf] = value
    }
  }
  counter += 1
  const commit = counter
  const mine = generation
  for (const [leaf, value] of Object.entries(sent)) {
    latest.set(leaf, { value, commit, succeededAt: null })
  }
  committedChanged()
  client.setQueryData<CapturePut>(CAPTURE_SETTINGS_KEY, (current) =>
    current === undefined ? current : ({ ...current, ...sent } as CapturePut),
  )
  queued += 1
  const json = JSON.stringify(sent)
  queue = queue.then(async () => {
    if (mine !== generation) {
      return
    }
    let ok = true
    try {
      await apiFetch('/settings/capture', { method: 'PUT', body: json })
    } catch {
      // The status names no value, and nothing is logged.
      ok = false
    }
    if (mine !== generation) {
      return
    }
    counter += 1
    let dropped = false
    for (const leaf of Object.keys(sent)) {
      const entry = latest.get(leaf)
      if (entry === undefined || entry.commit !== commit) {
        continue
      }
      if (ok) {
        entry.succeededAt = counter
      } else {
        latest.delete(leaf)
        dropped = true
      }
    }
    if (dropped) {
      committedChanged()
    }
    queued -= 1
    if (!ok) {
      queueFailed = true
      failures += 1
      for (const listener of failureListeners) {
        listener()
      }
    }
    if (queued === 0 && queueFailed) {
      queueFailed = false
      void client.invalidateQueries({ queryKey: CAPTURE_SETTINGS_KEY })
    }
  })
}
