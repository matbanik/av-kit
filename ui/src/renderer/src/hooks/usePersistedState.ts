import { useState } from 'react'

export const PERSIST_UI_KEYS = [
  'ui.rail.collapsed',
  'ui.panel.console.visible',
  'ui.panel.console.expanded',
] as const

export type PersistStorage = {
  getItem: (key: string) => string | null
  setItem: (key: string, value: string) => void
}

export function createUiPersist(store: Map<string, unknown>): {
  read: (key: string) => unknown
  write: (key: string, value: unknown) => void
} {
  return {
    read: (key: string) => store.get(key),
    write: (key: string, value: unknown) => {
      store.set(key, value)
    },
  }
}

function memoryStorage(): PersistStorage {
  const mem = new Map<string, string>()
  return {
    getItem: (key) => mem.get(key) ?? null,
    setItem: (key, value) => {
      mem.set(key, value)
    },
  }
}

function defaultStorage(): PersistStorage {
  if (typeof localStorage !== 'undefined') {
    return localStorage
  }
  return memoryStorage()
}

export function readPersisted<T>(
  key: string,
  fallback: T,
  storage: PersistStorage = defaultStorage(),
): T {
  const raw = storage.getItem(key)
  if (raw === null) {
    return fallback
  }
  try {
    const parsed: unknown = JSON.parse(raw)
    if (typeof parsed !== typeof fallback) {
      return fallback
    }
    return parsed as T
  } catch {
    return fallback
  }
}

export function writePersisted(
  key: string,
  value: unknown,
  storage: PersistStorage = defaultStorage(),
): void {
  storage.setItem(key, JSON.stringify(value))
}

export function usePersistedState<T>(
  key: (typeof PERSIST_UI_KEYS)[number],
  fallback: T,
): [T, (value: T | ((prev: T) => T)) => void] {
  const [value, setValue] = useState<T>(() => readPersisted(key, fallback))
  const set = (next: T | ((prev: T) => T)) => {
    setValue((prev) => {
      const resolved = typeof next === 'function' ? (next as (prev: T) => T)(prev) : next
      writePersisted(key, resolved)
      return resolved
    })
  }
  return [value, set]
}
