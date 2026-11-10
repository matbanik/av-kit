import { useEffect, useMemo, useRef, useState } from 'react'

import { PanelLeftClose, PanelLeftOpen, X } from 'lucide-react'

import { CONSOLE_LOG_FILE_SPEC_PATH } from '../../lib/console-log-path'
import { Button } from '../ui/Button'
import { useG30Styles } from '../ui/SelectInput'
import { Tooltip } from '../ui/Tooltip'

export const CONSOLE_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] as const
export type ConsoleLevel = (typeof CONSOLE_LEVELS)[number]

function isConsoleLevel(value: unknown): value is ConsoleLevel {
  return typeof value === 'string' && (CONSOLE_LEVELS as readonly string[]).includes(value)
}

/**
 * A line passes when its level is the selected level or more severe (D-1, 2026-11-09):
 * DEBUG shows every levelled line. A line without a level token never passes.
 */
export function lineMeetsLevel(line: string, level: ConsoleLevel): boolean {
  const match = line.match(/\[(DEBUG|INFO|WARNING|ERROR|CRITICAL)\s*\]/i)
  if (match === null) {
    return false
  }
  const lineLevel = match[1].toUpperCase()
  if (!isConsoleLevel(lineLevel)) {
    return false
  }
  return CONSOLE_LEVELS.indexOf(lineLevel) >= CONSOLE_LEVELS.indexOf(level)
}

export async function copyVisibleLogs(
  lines: string[],
  writeClipboard: (text: string) => Promise<void>,
): Promise<void> {
  await writeClipboard(lines.join('\n'))
}

export async function putLogToFile(
  enabled: boolean,
  apiFetchImpl: (path: string, init?: RequestInit) => Promise<unknown>,
): Promise<void> {
  await apiFetchImpl('/settings/app', {
    method: 'PUT',
    body: JSON.stringify({ log_to_file: enabled }),
  })
}

export function redactConsoleText(text: string): string {
  return text.replace(/Bearer\s+\S+/gi, 'Bearer [redacted]')
}

type ConsolePanelProps = {
  lines?: string[]
  expanded?: boolean
  onCopy?: (lines: string[]) => void
  onLogToFile?: (enabled: boolean) => void
  onClear?: () => void
  onExpand?: () => void
  onClose?: () => void
  onCollapse?: () => void
  /** Reads Settings → Log level, the level the Console opens at (D-2, 2026-11-09). */
  loadStartLevel?: () => Promise<unknown>
}

export function ConsolePanel({
  lines = [],
  expanded = false,
  onCopy,
  onLogToFile,
  onClear,
  onExpand,
  onClose,
  onCollapse,
  loadStartLevel,
}: ConsolePanelProps) {
  const [filter, setFilter] = useState<ConsoleLevel>('DEBUG')
  const userChoseLevel = useRef(false)
  // Read once when the Console opens; the shell re-renders on every log line.
  const startLevelLoader = useRef(loadStartLevel)
  const [search, setSearch] = useState('')
  const [showYtdlp, setShowYtdlp] = useState(true)
  const g30 = useG30Styles()

  useEffect(() => {
    const load = startLevelLoader.current
    if (load === undefined) {
      return undefined
    }
    let live = true
    load()
      .then((settings) => {
        const saved =
          typeof settings === 'object' && settings !== null
            ? (settings as { log_level?: unknown }).log_level
            : undefined
        if (live && !userChoseLevel.current && isConsoleLevel(saved)) {
          setFilter(saved)
        }
      })
      .catch(() => {
        // Settings unreadable: the Console stays at DEBUG.
      })
    return () => {
      live = false
    }
  }, [])

  const visible = useMemo(() => {
    return lines.filter((line) => {
      if (!lineMeetsLevel(line, filter)) {
        return false
      }
      if (!showYtdlp && /yt-?dlp/i.test(line)) {
        return false
      }
      if (search.trim() !== '' && !line.toLowerCase().includes(search.toLowerCase())) {
        return false
      }
      return true
    })
  }, [filter, lines, search, showYtdlp])

  const geom = expanded ? 'w-full' : 'w-[40%] min-w-[320px] max-w-[500px]'

  return (
    <section
      className={`flex flex-col h-full min-h-0 overflow-hidden bg-bg text-fg ${geom}`}
      data-testid="console-panel"
      role="complementary"
      aria-label="Console"
    >
      <div className="px-4 py-3 border-b border-border-subtle" data-testid="console-header">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            {expanded ? (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                data-testid="console-collapse"
                aria-expanded="true"
                aria-label="Collapse panel"
                onClick={onCollapse}
              >
                <PanelLeftOpen size={16} aria-hidden="true" />
                <span>Collapse</span>
              </Button>
            ) : (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                data-testid="console-expand"
                aria-expanded="false"
                aria-label="Expand panel to full width"
                onClick={onExpand}
              >
                <PanelLeftClose size={16} aria-hidden="true" />
                <span>Expand</span>
              </Button>
            )}
            <span>Console</span>
          </div>
          <Tooltip id="console-close" label="Close console">
            <Button
              type="button"
              variant="outline"
              size="sm"
              icon
              data-testid="console-close"
              aria-label="Close console"
              onClick={onClose}
            >
              <X size={16} aria-hidden="true" />
            </Button>
          </Tooltip>
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-2 px-4 py-2 border-b border-border-subtle">
        <div
          data-testid="console-filter"
          role="radiogroup"
          aria-label="Level"
          className="flex flex-wrap items-center gap-1"
        >
          {CONSOLE_LEVELS.map((level) => {
            const checked = filter === level
            return (
              <Button
                key={level}
                type="button"
                role="radio"
                aria-checked={checked}
                variant={checked ? 'primary' : 'ghost'}
                size="sm"
                data-testid={`console-level-${level}`}
                onClick={() => {
                  userChoseLevel.current = true
                  setFilter(level)
                }}
              >
                {level}
              </Button>
            )
          })}
        </div>
        <input
          data-testid="console-search"
          className="bg-bg text-fg"
          style={g30}
          placeholder="Search"
          value={search}
          onChange={(event) => {
            setSearch(event.target.value)
          }}
        />
        <Button type="button" variant="outline" size="sm" data-testid="console-clear" onClick={onClear}>
          Clear
        </Button>
        <Button
          type="button"
          variant="primary"
          size="sm"
          data-testid="console-copy"
          onClick={() => {
            onCopy?.(visible)
          }}
        >
          Copy
        </Button>
        <label>
          <input
            type="checkbox"
            data-testid="console-ytdlp-toggle"
            checked={showYtdlp}
            onChange={(event) => {
              setShowYtdlp(event.target.checked)
            }}
          />
          Show yt-dlp debug output
        </label>
        <label>
          <input
            type="checkbox"
            data-testid="console-log-to-file"
            onChange={(event) => {
              onLogToFile?.(event.target.checked)
            }}
          />
          Log to file
        </label>
        <p data-testid="console-log-file-path">Errors always go to {CONSOLE_LOG_FILE_SPEC_PATH}. Turn this on for every line.</p>
      </div>
      <pre
        data-testid="console-output"
        className="flex-1 min-h-0 overflow-auto bg-[var(--color-console-bg)] text-[var(--color-console-fg)] font-mono p-3"
      >
        {visible.map((line) => redactConsoleText(line)).join('\n')}
      </pre>
    </section>
  )
}
