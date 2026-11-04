import { useEffect, useSyncExternalStore } from 'react'

import type { ShellPage } from './shortcuts'

/** Which stateful commands a page's controls currently allow (COMMAND_STATE, D-138). */
export type CommandState = Partial<Record<string, boolean>>

const EMPTY: CommandState = Object.freeze({})

const records = new Map<ShellPage, CommandState>()
const listeners = new Set<() => void>()

function sameState(a: CommandState, b: CommandState): boolean {
  const keys = Object.keys(a)
  return keys.length === Object.keys(b).length && keys.every((key) => a[key] === b[key])
}

function notify(): void {
  for (const listener of [...listeners]) {
    listener()
  }
}

/** Replaces the page's record; listeners hear only a change in value. */
export function publishCommandState(page: ShellPage, state: CommandState): void {
  if (sameState(records.get(page) ?? EMPTY, state)) {
    return
  }
  records.set(page, Object.freeze({ ...state }))
  notify()
}

export function clearCommandState(page: ShellPage): void {
  if (!records.has(page)) {
    return
  }
  records.delete(page)
  notify()
}

/** The page's stable record, or a frozen empty one. */
export function getCommandState(page: ShellPage): CommandState {
  return records.get(page) ?? EMPTY
}

export function subscribeCommandState(listener: () => void): () => void {
  listeners.add(listener)
  return () => {
    listeners.delete(listener)
  }
}

/** Publishes the page's state when its values change and clears it on unmount. */
export function usePublishCommandState(page: ShellPage, state: CommandState): void {
  const signature = JSON.stringify(Object.entries(state).sort(([a], [b]) => a.localeCompare(b)))
  useEffect(() => {
    publishCommandState(page, Object.fromEntries(JSON.parse(signature) as Array<[string, boolean]>))
  }, [page, signature])
  useEffect(
    () => () => {
      clearCommandState(page)
    },
    [page],
  )
}

/** The page's record as React state; `null` (no routed page) reads empty. */
export function useCommandState(page: ShellPage | null): CommandState {
  return useSyncExternalStore(subscribeCommandState, () => (page === null ? EMPTY : getCommandState(page)))
}
