import { useEffect, useId, useMemo, useState } from 'react'

import {
  HELP_FEATURE_ROUTE,
  HELP_PENDING_TOGGLE_KEY,
  takeHeldHelpToggle,
} from '../../features/settings/settings-commands'
import { ariaKeyshortcuts } from '../../registry/shortcuts'
import { shotSize, shotUrl } from './help-shots'
import { QUICK_START, quickStartPage, type QuickStartPage, type QuickStartShot } from './quick-start'

export type HelpSection = {
  id: string
  title: string
  body: string
}

/** Example collapse key: av-kit:settings-help:main:state */

type HelpCardProps = {
  feature: 'downloader' | 'transcript' | 'tts' | 'settings' | 'converter' | 'capture'
  tabKey: string
  sections: HelpSection[]
  /** MEU-165: the saved capture key; with it the quick start names that key (`quickStartPage`). */
  captureKey?: string
}

function storageKey(feature: string, tabKey: string): string {
  return `av-kit:${feature}-help:${tabKey}:state`
}

function readExpanded(feature: string, tabKey: string): boolean {
  try {
    const raw = localStorage.getItem(storageKey(feature, tabKey))
    if (raw === 'expanded') {
      return true
    }
  } catch {
    // ignore storage failures
  }
  // First visit collapses by default; the header stays visible as the affordance.
  return false
}

/** One screenshot of the quick start, with a light and a dark image (THEME_SHOT_CSS hides one). */
function HelpShot({ shot }: { shot: QuickStartShot }) {
  const light = shotUrl(shot.name, 'light')
  const dark = shotUrl(shot.name, 'dark')
  const size = shotSize(shot.name)
  if (light === null || dark === null || size === null) {
    return null
  }
  return (
    <figure
      data-testid="help-shot"
      data-shot={shot.name}
      data-shot-steps={shot.steps.join(',')}
      className="help-shot"
    >
      <img
        className="help-shot__img--light"
        src={light}
        alt={shot.alt}
        width={size.width}
        height={size.height}
        loading="lazy"
        decoding="async"
      />
      <img
        className="help-shot__img--dark"
        src={dark}
        alt={shot.alt}
        width={size.width}
        height={size.height}
        loading="lazy"
        decoding="async"
      />
      <figcaption>{shot.alt}</figcaption>
    </figure>
  )
}

/** The intro, the numbered steps and the screenshots; shown only while the search is empty. */
function QuickStart({ page }: { page: QuickStartPage }) {
  return (
    <>
      <p data-testid="help-quick-start-intro" className="text-sm">
        {page.intro}
      </p>
      <ol data-testid="help-quick-start" className="help-quick-start">
        {page.steps.map((step, index) => (
          <li key={index} data-testid="help-quick-start-step" data-step={index + 1}>
            {step.text}
          </li>
        ))}
      </ol>
      {page.shots.map((shot) => (
        <HelpShot key={shot.name} shot={shot} />
      ))}
    </>
  )
}

function writeExpanded(feature: string, tabKey: string, expanded: boolean): void {
  try {
    localStorage.setItem(storageKey(feature, tabKey), expanded ? 'expanded' : 'collapsed')
  } catch {
    // ignore storage failures
  }
}

export function HelpCard({ feature, tabKey, sections, captureKey }: HelpCardProps) {
  const panelId = useId()
  const [expanded, setExpanded] = useState(() => readExpanded(feature, tabKey))
  const [query, setQuery] = useState('')
  const page = useMemo(
    () => (captureKey === undefined ? QUICK_START[feature] : quickStartPage(feature, captureKey)),
    [captureKey, feature],
  )

  useEffect(() => {
    writeExpanded(feature, tabKey, expanded)
  }, [expanded, feature, tabKey])

  useEffect(() => {
    try {
      if (sessionStorage.getItem(HELP_PENDING_TOGGLE_KEY) === '1') {
        sessionStorage.removeItem(HELP_PENDING_TOGGLE_KEY)
        setExpanded((value) => !value)
      }
    } catch {
      // ignore storage failures
    }
  }, [])

  useEffect(() => {
    // HELP_ROUTE_SCOPE (MEU-158, D-1176): the card's route comes from the fixed map, never from
    // the hash at mount. A toggle with a route reaches only the cards on that route, which mark it
    // received (preventDefault); a toggle with no route toggles every card, as before.
    const route = HELP_FEATURE_ROUTE[feature]
    const onToggle = (event: Event) => {
      const detail: unknown = event instanceof CustomEvent ? event.detail : null
      const target =
        typeof detail === 'object' && detail !== null && 'route' in detail ? detail.route : undefined
      if (target !== undefined) {
        if (target !== route) {
          return
        }
        event.preventDefault()
      }
      setExpanded((value) => !value)
    }
    window.addEventListener('av-kit:help:toggle-local', onToggle)
    // HELP_TAKE_ON_MOUNT: an F1 held for this card's route toggles it once. Under StrictMode's
    // double effect the first run takes the request and the second finds none.
    if (takeHeldHelpToggle(route)) {
      setExpanded((value) => !value)
    }
    return () => {
      window.removeEventListener('av-kit:help:toggle-local', onToggle)
    }
  }, [feature])

  const searching = query.trim().length > 0
  const filtered = useMemo(() => {
    const needle = query.trim().toLowerCase()
    if (needle.length === 0) {
      return sections
    }
    return sections.filter(
      (section) =>
        section.title.toLowerCase().includes(needle) || section.body.toLowerCase().includes(needle),
    )
  }, [query, sections])

  return (
    <section data-testid="help-card" className="border border-border rounded-md p-3 mb-4">
      <button
        type="button"
        className="w-full flex items-center justify-between text-left font-medium"
        aria-expanded={expanded}
        aria-controls={panelId}
        title="How it works (F1)"
        aria-keyshortcuts={ariaKeyshortcuts('F1')}
        onClick={() => {
          setExpanded((value) => !value)
        }}
      >
        <span className="flex items-center gap-2">
          <span aria-hidden="true">ℹ️</span>
          <span>How it works</span>
          <span data-testid="help-quick-start-hint" className="text-xs font-normal text-muted">
            {`Quick start · ${page.steps.length} steps`}
          </span>
        </span>
        <span aria-hidden="true">{expanded ? '−' : '+'}</span>
      </button>
      {expanded ? (
        <div id={panelId} className="mt-3 flex flex-col gap-3">
          <label className="flex flex-col gap-1 text-sm">
            <span className="sr-only">Search help</span>
            <input
              data-testid="help-search"
              type="search"
              placeholder="Search help topics…"
              value={query}
              onChange={(event) => {
                setQuery(event.target.value)
              }}
              className="rounded border border-border bg-bg px-2 py-1"
            />
          </label>
          {searching ? null : (
            <>
              <QuickStart page={page} />
              <h3 className="font-medium text-sm">More about this page</h3>
            </>
          )}
          {filtered.map((section) => (
            <details key={section.id} data-help-section={section.id} open={searching} className="help-topic">
              <summary className="font-medium text-sm cursor-pointer">{section.title}</summary>
              <p className="text-sm text-muted mt-1">{section.body}</p>
            </details>
          ))}
          {filtered.length === 0 ? (
            <p className="text-sm text-muted">No help topics match your search.</p>
          ) : null}
        </div>
      ) : null}
    </section>
  )
}
