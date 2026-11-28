/** @vitest-environment jsdom */

// Session 106 (MEU-174) UPDATES_CARD, AC-174.12 and AC-174.13: the Updates section of Settings.
// The card reads the controller's state through `window.api.updateGetState`, follows
// `onUpdateState`, saves the interval with `schedulePut('app', { update_interval })`, and is the
// only caller of `updateInstall`. The card is loaded by a dynamic import inside each test.
import { act, cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement } from 'react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { appPutSchema } from '../../src/renderer/src/features/settings/settings-schemas'

const CARD_MODULE = '../../src/renderer/src/features/settings/UpdatesCard'

const TRUST_NOTE =
  "Updates come from github.com/matbanik/av-kit and are checked against the release's SHA-512. The installer is not signed."

type State = {
  state: 'disabled' | 'idle' | 'checking' | 'downloading' | 'ready' | 'error'
  currentVersion: string
  availableVersion: string | null
  percent: number | null
  lastCheckAt: number | null
  lastResult: 'up-to-date' | 'update-found' | 'error' | null
  errorKind: 'network' | 'checksum' | 'other' | null
}

const CHECKED_AT = Date.UTC(2026, 10, 20, 9, 30)

function base(patch: Partial<State> = {}): State {
  return {
    state: 'idle',
    currentVersion: '1.0.0',
    availableVersion: null,
    percent: null,
    lastCheckAt: null,
    lastResult: null,
    errorKind: null,
    ...patch,
  }
}

/** One row per status line of UPDATES_CARD: label, state, exact text or a prefix. */
const STATUS_ROWS: ReadonlyArray<[string, State, { exact?: string; prefix?: string }]> = [
  ['disabled', base({ state: 'disabled' }), { exact: 'Updates run in the installed app' }],
  ['idle-unchecked', base(), { exact: 'Not checked yet' }],
  [
    'idle-up-to-date',
    base({ lastCheckAt: CHECKED_AT, lastResult: 'up-to-date' }),
    { prefix: 'Up to date. Last checked ' },
  ],
  ['checking', base({ state: 'checking' }), { exact: 'Checking…' }],
  [
    'downloading',
    base({ state: 'downloading', availableVersion: '2.0.0', percent: 41.6 }),
    { exact: 'Downloading version 2.0.0: 42 %' },
  ],
  [
    'ready',
    base({ state: 'ready', availableVersion: '2.0.0', percent: 100, lastCheckAt: CHECKED_AT, lastResult: 'update-found' }),
    { exact: 'Version 2.0.0 is ready to install' },
  ],
  [
    'error',
    base({ state: 'error', errorKind: 'checksum', lastCheckAt: CHECKED_AT, lastResult: 'error' }),
    { prefix: 'Could not check for updates (checksum). Last checked ' },
  ],
]

type Api = {
  updateGetState: ReturnType<typeof vi.fn>
  updateCheck: ReturnType<typeof vi.fn>
  updateInstall: ReturnType<typeof vi.fn>
  onUpdateState: ReturnType<typeof vi.fn>
  push: (state: State) => void
}

function mockApi(state: State, install?: () => Promise<unknown>): Api {
  let listener: ((s: State) => void) | null = null
  const api: Api = {
    updateGetState: vi.fn(async () => state),
    updateCheck: vi.fn(async () => state),
    updateInstall: vi.fn(install ?? (async () => ({ ok: true }))),
    onUpdateState: vi.fn((cb: (s: State) => void) => {
      listener = cb
      return () => {
        listener = null
      }
    }),
    push: (s) => {
      listener?.(s)
    },
  }
  window.api = {
    updateGetState: api.updateGetState,
    updateCheck: api.updateCheck,
    updateInstall: api.updateInstall,
    onUpdateState: api.onUpdateState,
  } as unknown as Window['api']
  return api
}

async function renderCard(state: State, opts: { interval?: string; install?: () => Promise<unknown> } = {}) {
  const mod = (await import(/* @vite-ignore */ CARD_MODULE).catch(() => ({}))) as Record<string, unknown>
  expect(typeof mod.UpdatesCard, 'UpdatesCard.tsx exports UpdatesCard').toBe('function')
  const api = mockApi(state, opts.install)
  const schedulePut = vi.fn()
  render(
    createElement(mod.UpdatesCard as (props: Record<string, unknown>) => React.JSX.Element, {
      interval: opts.interval ?? 'weekly',
      schedulePut,
      current: false,
    }),
  )
  await waitFor(() => {
    expect(api.updateGetState).toHaveBeenCalledTimes(1)
    expect(screen.getByTestId('settings-update-status').textContent).not.toBe('')
  })
  return { api, schedulePut }
}

function statusText(): string {
  return screen.getByTestId('settings-update-status').textContent ?? ''
}

afterEach(() => {
  cleanup()
})

describe('MEU-174 UPDATES_CARD', () => {
  it('AC-174.12 appPutSchema accepts the three wires and stays strict', () => {
    for (const wire of ['weekly', 'monthly', 'never']) {
      expect(appPutSchema.safeParse({ update_interval: wire }).success, wire).toBe(true)
    }
    for (const bad of [{ update_interval: 'daily' }, { update_interval: 'Weekly' }, { update_interval: 7 }]) {
      expect(appPutSchema.safeParse(bad).success, JSON.stringify(bad)).toBe(false)
    }
    expect(appPutSchema.safeParse({ update_intervals: 'weekly' }).success).toBe(false)
  })

  it('AC-174.12 the card renders the select with three options, the version line and Check now', async () => {
    await renderCard(base(), { interval: 'monthly' })
    expect(screen.getByTestId('updates-settings')).toBeInTheDocument()
    const select = screen.getByTestId('settings-leaf-update_interval') as HTMLSelectElement
    expect([...select.options].map((o) => [o.value, o.textContent])).toEqual([
      ['weekly', 'Once a week'],
      ['monthly', 'Once a month'],
      ['never', 'Never'],
    ])
    expect(select.value).toBe('monthly')
    expect(screen.getByTestId('settings-update-version').textContent).toBe('Installed version 1.0.0')
    const check = screen.getByTestId('settings-update-check') as HTMLButtonElement
    expect(check.textContent).toBe('Check now')
    expect(check.disabled).toBe(false)
  })

  it.each(STATUS_ROWS)('AC-174.12 the status line in the state %s', async (_label, state, want) => {
    await renderCard(state)
    if (want.exact !== undefined) expect(statusText()).toBe(want.exact)
    if (want.prefix !== undefined) {
      expect(statusText().startsWith(want.prefix), statusText()).toBe(true)
      expect(statusText().length).toBeGreaterThan(want.prefix.length)
    }
  })

  it('AC-174.12 a change of the select calls schedulePut with update_interval', async () => {
    const { schedulePut } = await renderCard(base())
    await userEvent.selectOptions(screen.getByTestId('settings-leaf-update_interval'), 'never')
    expect(schedulePut).toHaveBeenCalledTimes(1)
    expect(schedulePut).toHaveBeenCalledWith('app', { update_interval: 'never' })
  })

  it('AC-174.12 a click on Check now calls updateCheck once and the card follows the pushed state', async () => {
    const { api } = await renderCard(base())
    await userEvent.click(screen.getByTestId('settings-update-check'))
    expect(api.updateCheck).toHaveBeenCalledTimes(1)
    act(() => {
      api.push(base({ state: 'checking' }))
    })
    expect(statusText()).toBe('Checking…')
    act(() => {
      api.push(base({ state: 'ready', availableVersion: '3.1.0' }))
    })
    expect(statusText()).toBe('Version 3.1.0 is ready to install')
  })

  it('AC-174.12 [neg] the restart button is absent in every state but ready', async () => {
    for (const [label, state] of STATUS_ROWS) {
      await renderCard(state)
      const count = screen.queryAllByTestId('settings-update-restart').length
      expect(count, label).toBe(state.state === 'ready' ? 1 : 0)
      expect(screen.queryAllByTestId('settings-update-restart-note').length, label).toBe(
        state.state === 'ready' ? 1 : 0,
      )
      cleanup()
    }
  })

  it('AC-174.12 [neg] Check now is disabled in checking, downloading and disabled', async () => {
    for (const [label, state] of STATUS_ROWS) {
      await renderCard(state)
      const check = screen.getByTestId('settings-update-check') as HTMLButtonElement
      const off = state.state === 'checking' || state.state === 'downloading' || state.state === 'disabled'
      expect(check.disabled, label).toBe(off)
      cleanup()
    }
  })

  it('AC-174.13 in ready the restart button and its note show and a click calls updateInstall once', async () => {
    const ready = STATUS_ROWS.find(([label]) => label === 'ready')?.[1] ?? base()
    const { api } = await renderCard(ready)
    const restart = screen.getByTestId('settings-update-restart')
    expect(restart.textContent).toBe('Restart and update')
    expect(screen.getByTestId('settings-update-restart-note').textContent).toBe(
      'av-kit closes, installs version 2.0.0 and starts again. Downloads, transcripts, speech and conversions that are running stop.',
    )
    await userEvent.click(restart)
    expect(api.updateInstall).toHaveBeenCalledTimes(1)
    expect(api.updateInstall).toHaveBeenCalledWith()
  })

  it('AC-174.13 [neg] a second click while the install call is pending sends no second call', async () => {
    const ready = STATUS_ROWS.find(([label]) => label === 'ready')?.[1] ?? base()
    const pending = new Promise<unknown>(() => undefined)
    const { api } = await renderCard(ready, { install: () => pending })
    const restart = screen.getByTestId('settings-update-restart')
    await userEvent.click(restart)
    await userEvent.click(restart)
    expect(api.updateInstall).toHaveBeenCalledTimes(1)
  })

  it('AC-174.13 the trust note shows in every state', async () => {
    for (const [label, state] of STATUS_ROWS) {
      await renderCard(state)
      const note = screen.getByTestId('settings-update-trust-note').textContent
      expect(note, label).toBe(TRUST_NOTE)
      cleanup()
    }
  })
})
