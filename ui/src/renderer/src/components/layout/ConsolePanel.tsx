import { useMemo, useState } from 'react'

import { PanelLeftClose, PanelLeftOpen, X } from 'lucide-react'

import { CONSOLE_LOG_FILE_SPEC_PATH } from '../../lib/console-log-path'
import { Button } from '../ui/Button'
import { useG30Styles } from '../ui/SelectInput'
import { Tooltip } from '../ui/Tooltip'

export const CONSOLE_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] as const
export type ConsoleLevel = (typeof CONSOLE_LEVELS)[number]

export function lineMatchesExactLevel(line: string, level: ConsoleLevel): boolean {
  const match = line.match(/\[(DEBUG|INFO|WARNING|ERROR|CRITICAL)\s*\]/i)
  if (match === null) {
    return false
  }
  return match[1].toUpperCase() === level
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
}: ConsolePanelProps) {
  const [filter, setFilter] = useState<ConsoleLevel>('DEBUG')
  const [search, setSearch] = useState('')
  const [showYtdlp, setShowYtdlp] = useState(true)
  const g30 = useG30Styles()

  const visible = useMemo(() => {
    return lines.filter((line) => {
      if (!lineMatchesExactLevel(line, filter)) {
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
        <p data-testid="console-log-file-path">Persist to {CONSOLE_LOG_FILE_SPEC_PATH}</p>
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
