import { useEffect, useId, useMemo, useState } from 'react'

import { HELP_PENDING_TOGGLE_KEY } from '../../features/settings/settings-commands'
import { ariaKeyshortcuts } from '../../registry/shortcuts'

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

function writeExpanded(feature: string, tabKey: string, expanded: boolean): void {
  try {
    localStorage.setItem(storageKey(feature, tabKey), expanded ? 'expanded' : 'collapsed')
  } catch {
    // ignore storage failures
  }
}

export function HelpCard({ feature, tabKey, sections }: HelpCardProps) {
  const panelId = useId()
  const [expanded, setExpanded] = useState(() => readExpanded(feature, tabKey))
  const [query, setQuery] = useState('')

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
    const onToggle = () => {
      setExpanded((value) => !value)
    }
    window.addEventListener('av-kit:help:toggle-local', onToggle)
    return () => {
      window.removeEventListener('av-kit:help:toggle-local', onToggle)
    }
  }, [])

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
          {filtered.map((section) => (
            <article key={section.id} data-help-section={section.id}>
              <h3 className="font-medium text-sm">{section.title}</h3>
              <p className="text-sm text-muted mt-1">{section.body}</p>
            </article>
          ))}
          {filtered.length === 0 ? (
            <p className="text-sm text-muted">No help topics match your search.</p>
          ) : null}
        </div>
      ) : null}
    </section>
  )
}
