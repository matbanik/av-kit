import { useCallback, useEffect, useState } from 'react'

import { sectionFrameProps } from './settings-section-frame'
import { SAVE_MODE_CAPTIONS } from './settings-sections'

type LoginItemState =
  | {
      supported: true
      enabled: boolean
      minimized: boolean
      startMinimizedSupported: boolean
    }
  | {
      supported: false
      reason: 'platform' | 'not-packaged'
      enabled: false
      minimized: false
    }

function unsupportedState(): LoginItemState {
  return {
    supported: false,
    reason: 'not-packaged',
    enabled: false,
    minimized: false,
  }
}

type StartAtSignInControlProps = {
  /** Reports whether the panel is mounted, so the Settings rail can list it (no extra IPC). */
  onAvailabilityChange?: (available: boolean) => void
  /** Whether the Settings rail marks Startup current (MEU-70 SECTION_EMPHASIS). */
  current?: boolean
}

export function StartAtSignInControl({ onAvailabilityChange, current = false }: StartAtSignInControlProps = {}) {
  const [state, setState] = useState<LoginItemState | null>(null)
  const [busy, setBusy] = useState(false)
  const available = state !== null && state.supported

  const load = useCallback(async () => {
    const get = window.api.loginItemGet
    if (typeof get !== 'function') {
      setState(unsupportedState())
      return
    }
    try {
      setState(await get())
    } catch {
      setState(unsupportedState())
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  useEffect(() => {
    onAvailabilityChange?.(available)
  }, [available, onAvailabilityChange])

  const apply = async (enabled: boolean, minimized: boolean): Promise<void> => {
    const set = window.api.loginItemSet
    if (typeof set !== 'function') {
      setState(unsupportedState())
      return
    }
    setBusy(true)
    try {
      setState(await set(enabled, minimized))
    } catch {
      setState(unsupportedState())
    } finally {
      setBusy(false)
    }
  }

  if (state === null) return null
  if (!state.supported) return null

  return (
    <section
      data-testid="start-at-sign-in-panel"
      data-settings-section="startup"
      tabIndex={-1}
      {...sectionFrameProps(current)}
    >
      <div className="flex items-baseline gap-3 border-b border-bg-elevated pb-1">
        <h2 className="text-[15px] font-semibold">Startup</h2>
        <span data-testid="settings-mode-startup" className="text-xs text-fg-muted">
          {SAVE_MODE_CAPTIONS['immediate-os']}
        </span>
      </div>
      <label className="flex items-center gap-2 text-sm">
        <input
          type="checkbox"
          data-testid="start-at-sign-in-checkbox"
          checked={state.enabled}
          disabled={busy}
          onChange={(event) => {
            void apply(event.target.checked, event.target.checked && state.minimized)
          }}
        />
        <span>Start av-kit when I sign in</span>
      </label>
      {state.enabled && state.startMinimizedSupported ? (
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            data-testid="start-minimized-checkbox"
            checked={state.minimized}
            disabled={busy}
            onChange={(event) => {
              void apply(true, event.target.checked)
            }}
          />
          <span>Start minimized</span>
        </label>
      ) : null}
    </section>
  )
}
