import { useEffect, useRef, useState } from 'react'

import { Button } from '../../components/ui/Button'
import { sectionFrameProps } from './settings-section-frame'
import { SAVE_MODE_CAPTIONS } from './settings-sections'
import { GridSelect } from './SettingsPage'

/** The controller state that `update-get-state` returns and `update-state-changed` pushes (UPDATE_IPC). */
export type UpdateCardState = {
  state: 'disabled' | 'idle' | 'checking' | 'downloading' | 'ready' | 'error'
  currentVersion: string
  availableVersion: string | null
  percent: number | null
  lastCheckAt: number | null
  lastResult: 'up-to-date' | 'update-found' | 'error' | null
  errorKind: 'network' | 'checksum' | 'other' | null
}

export type UpdateIntervalWire = 'weekly' | 'monthly' | 'never'

const INTERVAL_OPTIONS: ReadonlyArray<{ value: UpdateIntervalWire; label: string }> = [
  { value: 'weekly', label: 'Once a week' },
  { value: 'monthly', label: 'Once a month' },
  { value: 'never', label: 'Never' },
]

const TRUST_NOTE =
  "Updates come from github.com/matbanik/av-kit and are checked against the release's SHA-512. The installer is not signed."

const UNAVAILABLE: UpdateCardState = {
  state: 'disabled',
  currentVersion: '',
  availableVersion: null,
  percent: null,
  lastCheckAt: null,
  lastResult: null,
  errorKind: null,
}

function checkedAt(at: number): string {
  return new Date(at).toLocaleString()
}

/** The one status line of UPDATES_CARD for a state. */
export function updateStatusText(s: UpdateCardState): string {
  switch (s.state) {
    case 'disabled':
      return 'Updates run in the installed app'
    case 'checking':
      return 'Checking…'
    case 'downloading':
      return `Downloading version ${s.availableVersion ?? ''}: ${String(Math.round(s.percent ?? 0))} %`
    case 'ready':
      return `Version ${s.availableVersion ?? ''} is ready to install`
    case 'error': {
      const head = `Could not check for updates (${s.errorKind ?? 'other'}).`
      return s.lastCheckAt === null ? head : `${head} Last checked ${checkedAt(s.lastCheckAt)}`
    }
    default:
      return s.lastResult === 'up-to-date' && s.lastCheckAt !== null
        ? `Up to date. Last checked ${checkedAt(s.lastCheckAt)}`
        : 'Not checked yet'
  }
}

/** The Updates section of Settings (UPDATES_CARD, MEU-174). */
export function UpdatesCard({
  interval,
  schedulePut,
  current,
}: {
  interval: string
  schedulePut: (namespace: 'app', body: { update_interval: string }) => void
  /** ACTIVE_SOURCE: whether the rail marks this section current. */
  current: boolean
}): React.JSX.Element {
  const [state, setState] = useState<UpdateCardState | null>(null)
  const installing = useRef(false)

  useEffect(() => {
    let live = true
    const api = window.api
    const off = api.onUpdateState?.((next) => {
      if (live) setState(next as UpdateCardState)
    })
    const get = api.updateGetState
    if (get === undefined) {
      setState(UNAVAILABLE)
    } else {
      get().then(
        (value) => {
          if (live) setState(value as UpdateCardState)
        },
        () => {
          if (live) setState(UNAVAILABLE)
        },
      )
    }
    return () => {
      live = false
      off?.()
    }
  }, [])

  const s = state ?? UNAVAILABLE
  const busy = s.state === 'checking' || s.state === 'downloading' || s.state === 'disabled'

  return (
    <section
      data-testid="updates-settings"
      data-settings-section="updates"
      tabIndex={-1}
      {...sectionFrameProps(current)}
    >
      <div className="flex items-baseline gap-3 border-b border-bg-elevated pb-1">
        <h2 className="text-[15px] font-semibold">Updates</h2>
        <span data-testid="settings-mode-updates" className="text-xs text-fg-muted">
          {SAVE_MODE_CAPTIONS.autosave}
        </span>
      </div>
      <GridSelect
        id="settings-update-interval"
        label="Check for updates"
        testId="settings-leaf-update_interval"
        value={interval}
        options={INTERVAL_OPTIONS}
        onChange={(value) => {
          schedulePut('app', { update_interval: value })
        }}
      />
      <p data-testid="settings-update-version" className="text-sm">
        {`Installed version ${s.currentVersion}`}
      </p>
      <p data-testid="settings-update-status" className="text-sm text-fg-muted">
        {state === null ? '' : updateStatusText(s)}
      </p>
      <div className="flex items-center gap-2">
        <Button
          data-testid="settings-update-check"
          type="button"
          size="sm"
          variant="secondary"
          disabled={busy}
          onClick={() => {
            void window.api.updateCheck?.().catch(() => undefined)
          }}
        >
          Check now
        </Button>
        {s.state === 'ready' ? (
          <Button
            data-testid="settings-update-restart"
            type="button"
            size="sm"
            variant="primary"
            onClick={() => {
              if (installing.current) return
              installing.current = true
              const call = window.api.updateInstall?.() ?? Promise.resolve({ ok: false })
              void call.then(
                (result) => {
                  // A refused install (`not-ready`) lets the button be pressed again.
                  if ((result as { ok?: boolean } | undefined)?.ok === false) installing.current = false
                },
                () => {
                  installing.current = false
                },
              )
            }}
          >
            Restart and update
          </Button>
        ) : null}
      </div>
      {s.state === 'ready' ? (
        <p data-testid="settings-update-restart-note" className="text-sm text-fg-muted">
          {`av-kit closes, installs version ${s.availableVersion ?? ''} and starts again. Downloads, transcripts, speech and conversions that are running stop.`}
        </p>
      ) : null}
      <p data-testid="settings-update-trust-note" className="text-xs text-fg-muted">
        {TRUST_NOTE}
      </p>
    </section>
  )
}
