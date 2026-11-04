import { useCallback, useEffect, useMemo, useRef, useState, type KeyboardEvent } from 'react'
import Fuse from 'fuse.js'

import { useCommandState } from '../registry/command-state'
import { listCommands, type CommandRegistryEntry } from '../registry/commandRegistry'
import { currentShellPage, paletteCommands, type ShellPage } from '../registry/shortcuts'

type CommandPaletteProps = {
  open?: boolean
  onClose?: () => void
}

export const CATEGORY_LABELS: Record<CommandRegistryEntry['category'], string> = {
  navigation: 'Navigation',
  download: 'Download',
  transcript: 'Transcript',
  tts: 'TTS',
  convert: 'Convert',
  capture: 'Capture',
  settings: 'Settings',
  appearance: 'Appearance',
  help: 'Help',
}

/** The routed page, re-read on every `hashchange` (PALETTE_LIST). */
function useShellPage(): ShellPage | null {
  const [page, setPage] = useState(currentShellPage)
  useEffect(() => {
    const onHash = () => {
      setPage(currentShellPage())
    }
    window.addEventListener('hashchange', onHash)
    return () => {
      window.removeEventListener('hashchange', onHash)
    }
  }, [])
  return page
}

/**
 * CommandPalette — centered overlay with backdrop, fuzzy search, keyboard
 * navigation, and category grouping. Opened by Ctrl+K or the header control.
 * It lists the context-aware set (PALETTE_LIST): globals, the current page's
 * entry commands, and its stateful commands while the page allows them.
 */
export function CommandPalette({ open = false, onClose }: CommandPaletteProps) {
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(-1)
  const inputRef = useRef<HTMLInputElement>(null)
  const listRef = useRef<HTMLDivElement>(null)

  const page = useShellPage()
  const state = useCommandState(page)
  const commands = useMemo(() => paletteCommands(listCommands(), page, state), [page, state])
  const fuse = useMemo(
    () => new Fuse(commands, { keys: ['id', 'label', 'keywords'], threshold: 0.4 }),
    [commands],
  )

  const results = useMemo(() => {
    if (query.trim() === '') {
      return commands
    }
    return fuse.search(query).map((row) => row.item)
  }, [commands, fuse, query])

  const grouped = useMemo(() => {
    // Groups appear in the order their category first appears in the list.
    const groups = new Map<CommandRegistryEntry['category'], CommandRegistryEntry[]>()
    for (const command of results) {
      const entries = groups.get(command.category)
      if (entries) {
        entries.push(command)
      } else {
        groups.set(command.category, [command])
      }
    }
    return groups
  }, [results])

  const flatResults = useMemo(() => {
    const items: CommandRegistryEntry[] = []
    for (const entries of grouped.values()) {
      items.push(...entries)
    }
    return items
  }, [grouped])

  // Reset query/selection and focus the input each time the palette opens.
  useEffect(() => {
    if (!open) {
      return
    }
    setQuery('')
    setSelectedIndex(-1)
    const timer = window.setTimeout(() => {
      inputRef.current?.focus()
    }, 0)
    return () => {
      window.clearTimeout(timer)
    }
  }, [open])

  useEffect(() => {
    if (selectedIndex < 0 || !listRef.current) {
      return
    }
    const item = listRef.current.querySelector(`[data-index="${selectedIndex}"]`)
    if (item && typeof item.scrollIntoView === 'function') {
      item.scrollIntoView({ block: 'nearest' })
    }
  }, [selectedIndex])

  const close = useCallback(() => {
    onClose?.()
  }, [onClose])

  const executeCommand = useCallback(
    (command: CommandRegistryEntry) => {
      close()
      command.action()
    },
    [close],
  )

  // Refs keep the keydown handler free of stale closures.
  const selectedIndexRef = useRef(selectedIndex)
  selectedIndexRef.current = selectedIndex
  const flatResultsRef = useRef(flatResults)
  flatResultsRef.current = flatResults

  const handleKeyDown = useCallback(
    (event: KeyboardEvent<HTMLDivElement>) => {
      switch (event.key) {
        case 'Escape':
          event.preventDefault()
          event.stopPropagation()
          close()
          break
        case 'ArrowDown':
          event.preventDefault()
          setSelectedIndex((index) => Math.min(index + 1, flatResultsRef.current.length - 1))
          break
        case 'ArrowUp':
          event.preventDefault()
          setSelectedIndex((index) => Math.max(index - 1, 0))
          break
        case 'Enter': {
          // PALETTE_ENTER: a modified Enter passes through to the window chord handler.
          if (event.ctrlKey || event.metaKey || event.altKey || event.shiftKey) {
            return
          }
          event.preventDefault()
          const index = selectedIndexRef.current
          const command = flatResultsRef.current[index]
          if (index >= 0 && command) {
            executeCommand(command)
          }
          break
        }
        default:
          break
      }
    },
    [close, executeCommand],
  )

  if (!open) {
    return null
  }

  let flatIndex = -1

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]"
      onClick={close}
      onKeyDown={handleKeyDown}
      role="presentation"
    >
      <div className="absolute inset-0 bg-overlay" aria-hidden="true" />
      <div
        data-testid="command-palette"
        role="dialog"
        aria-modal="true"
        aria-label="Command palette"
        className="relative flex max-h-[60vh] w-[560px] max-w-[90vw] flex-col overflow-hidden rounded-lg border border-border bg-bg-elevated text-fg shadow-elevated"
        onClick={(event) => {
          event.stopPropagation()
        }}
      >
        <div className="border-b border-border p-3">
          <input
            ref={inputRef}
            data-testid="command-palette-input"
            type="text"
            role="searchbox"
            placeholder="Type a command…"
            aria-label="Search commands"
            className="w-full bg-transparent text-sm text-fg outline-none placeholder:text-fg-muted"
            value={query}
            onChange={(event) => {
              setQuery(event.target.value)
              setSelectedIndex(-1)
            }}
          />
        </div>
        <div ref={listRef} className="overflow-y-auto p-1">
          {Array.from(grouped.entries()).map(([category, entries]) => (
            <div key={category}>
              <div className="px-3 py-1.5 text-xs font-semibold uppercase tracking-wider text-fg-muted">
                {CATEGORY_LABELS[category]}
              </div>
              {entries.map((command) => {
                flatIndex += 1
                const index = flatIndex
                const isSelected = index === selectedIndex
                return (
                  <button
                    key={command.id}
                    type="button"
                    data-index={index}
                    data-selected={isSelected ? 'true' : undefined}
                    className={`flex w-full items-center gap-3 rounded-md px-3 py-2 text-left text-sm transition-colors ${
                      isSelected
                        ? 'bg-accent-cyan/20 text-fg'
                        : 'text-fg-muted hover:bg-bg-subtle/40 hover:text-fg'
                    }`}
                    onMouseEnter={() => {
                      setSelectedIndex(index)
                    }}
                    onClick={() => {
                      executeCommand(command)
                    }}
                  >
                    <span className="flex-1">{command.label}</span>
                    {command.shortcut ? (
                      <kbd className="rounded border border-border px-1 py-0.5 text-xs text-fg-muted">
                        {command.shortcut}
                      </kbd>
                    ) : null}
                  </button>
                )
              })}
            </div>
          ))}
          {flatResults.length === 0 ? (
            <div className="px-3 py-4 text-center text-sm text-fg-muted">No commands found</div>
          ) : null}
        </div>
      </div>
    </div>
  )
}
