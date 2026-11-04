import { useEffect, useState, useSyncExternalStore } from 'react'

import { ApiError, apiFetch } from './api'
import { logRenderer } from './renderer-log'

export const THEME_CHANGED_EVENT = 'av-kit:theme-changed'

export const UI_THEMES = ['dark', 'light'] as const

export type UiTheme = (typeof UI_THEMES)[number]

type ThemeChangedDetail = {
  theme: UiTheme
}

/** Renderer `localStorage` mirror of the last applied theme, read by `boot-theme.ts` before the first render. */
export const THEME_STORAGE_KEY = 'av-kit.ui.theme'

/** Backoff before the 2nd, 3rd and 4th boot `GET /settings/ui`; later attempts wait 2000 ms. */
export const BOOT_RETRY_DELAYS_MS = [250, 500, 1000] as const

const BOOT_RETRY_STEADY_MS = 2000

/**
 * No boot attempt starts this long or longer after the first one started, and
 * the boot load as a whole settles by then even if an attempt never answers.
 */
export const BOOT_RETRY_WINDOW_MS = 60_000

/**
 * Map a persisted `ui.theme` value to a document theme.
 * Only the literal `'light'` is light; missing, null, and any other value
 * resolve to `'dark'` (spec default for `ui.theme`).
 */
export function resolveUiTheme(value: unknown): UiTheme {
  return value === 'light' ? 'light' : 'dark'
}

/** The mirrored theme, or `null` when the key is unset, holds any other value, or storage throws. */
export function readBootTheme(): UiTheme | null {
  try {
    const stored = localStorage.getItem(THEME_STORAGE_KEY)
    return stored === 'dark' || stored === 'light' ? stored : null
  } catch {
    return null
  }
}

/**
 * Apply Dark/Light tokens by toggling the document root `dark` class used by
 * `:root:not(.dark)` in `styles.css`, mirror the theme to `localStorage`, then
 * notify listeners so G30 selects re-render.
 */
export function applyDocumentTheme(theme: UiTheme): void {
  if (theme !== 'dark' && theme !== 'light') {
    throw new Error(`invalid ui theme: ${String(theme)}`)
  }
  if (typeof document === 'undefined') {
    return
  }
  const root = document.documentElement
  if (theme === 'dark') {
    root.classList.add('dark')
  } else {
    root.classList.remove('dark')
  }
  root.style.colorScheme = theme
  try {
    localStorage.setItem(THEME_STORAGE_KEY, theme)
  } catch {
    // A denied storage only costs the next boot its mirror.
  }
  window.dispatchEvent(
    new CustomEvent<ThemeChangedDetail>(THEME_CHANGED_EVENT, { detail: { theme } }),
  )
}

function subscribeTheme(onChange: () => void): () => void {
  window.addEventListener(THEME_CHANGED_EVENT, onChange)
  return () => {
    window.removeEventListener(THEME_CHANGED_EVENT, onChange)
  }
}

function documentThemeSnapshot(): UiTheme {
  return document.documentElement.classList.contains('dark') ? 'dark' : 'light'
}

function serverThemeSnapshot(): UiTheme {
  return 'dark'
}

/** The current document theme; every caller re-renders on `THEME_CHANGED_EVENT`. */
export function useDocumentTheme(): UiTheme {
  return useSyncExternalStore(subscribeTheme, documentThemeSnapshot, serverThemeSnapshot)
}

/**
 * AppShell's boot load of `GET /settings/ui`. A 503 (`BACKEND_NOT_READY` or
 * `FETCH_FAILED`) is retried inside `BOOT_RETRY_WINDOW_MS`; any other error,
 * or the last 503, is logged once. Returns `settled`, which turns true after a
 * success is applied, on any error other than `BACKEND_NOT_READY`, on the
 * final failure, or when `BOOT_RETRY_WINDOW_MS` passes with an attempt still
 * pending (logged once; the current document theme stays and a late answer is
 * ignored), and then stays true.
 */
export function useSyncDocumentTheme(): boolean {
  const [settled, setSettled] = useState(false)

  useEffect(() => {
    let cancelled = false
    let finished = false
    let timer: ReturnType<typeof setTimeout> | undefined
    const firstStart = Date.now()

    const finish = () => {
      finished = true
      if (timer !== undefined) {
        clearTimeout(timer)
      }
      clearTimeout(deadline)
      setSettled(true)
    }

    const deadline = setTimeout(() => {
      if (finished) {
        return
      }
      logRenderer('ERROR', `Failed to load ui.theme: no answer within ${BOOT_RETRY_WINDOW_MS} ms`)
      finish()
    }, BOOT_RETRY_WINDOW_MS)

    const attempt = (index: number) => {
      void apiFetch<{ theme?: string | null }>('/settings/ui')
        .then((data) => {
          if (cancelled || finished) {
            return
          }
          applyDocumentTheme(resolveUiTheme(data?.theme))
          finish()
        })
        .catch((caught: unknown) => {
          if (cancelled || finished) {
            return
          }
          const delay = BOOT_RETRY_DELAYS_MS[index] ?? BOOT_RETRY_STEADY_MS
          const retryable = caught instanceof ApiError && caught.status === 503
          if (retryable && Date.now() + delay - firstStart < BOOT_RETRY_WINDOW_MS) {
            if (caught.code !== 'BACKEND_NOT_READY') {
              setSettled(true)
            }
            timer = setTimeout(() => {
              attempt(index + 1)
            }, delay)
            return
          }
          const message = caught instanceof Error ? caught.message : String(caught)
          logRenderer('ERROR', `Failed to load ui.theme: ${message}`)
          finish()
        })
    }
    attempt(0)

    return () => {
      cancelled = true
      if (timer !== undefined) {
        clearTimeout(timer)
      }
      clearTimeout(deadline)
    }
  }, [])

  return settled
}
