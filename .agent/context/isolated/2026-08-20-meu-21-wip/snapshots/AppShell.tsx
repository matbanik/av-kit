import { useEffect, useState, type ReactNode } from 'react'

import { DOWNLOAD_COMMANDS, DOWNLOAD_EVENTS } from '../../features/downloader/download-commands'
import { TRANSCRIPT_COMMANDS, TRANSCRIPT_EVENTS } from '../../features/transcript/transcript-commands'
import { useBackendLogs } from '../../hooks/useBackendLogs'
import { usePersistedState } from '../../hooks/usePersistedState'
import { apiFetch } from '../../lib/api'
import { COLLAPSE_RAIL_EVENT, navigateShell, TOGGLE_CONSOLE_EVENT } from '../../lib/shell-nav'
import { CommandPalette } from '../CommandPalette'
import { ConsolePanel, copyVisibleLogs, putLogToFile } from './ConsolePanel'
import { Header } from './Header'
import { NavRail } from './NavRail'

export const OPEN_PALETTE_EVENT = 'av-kit:open-palette'

export function handleGlobalShortcut(key: string): string | null {
  if (key === 'Ctrl+K') {
    return OPEN_PALETTE_EVENT
  }
  return null
}

type AppShellProps = {
  children: ReactNode
}

export function AppShell({ children }: AppShellProps) {
  const [paletteOpen, setPaletteOpen] = useState(false)
  const [collapsed, setCollapsed] = usePersistedState('ui.rail.collapsed', false)
  const [consoleOpen, setConsoleOpen] = usePersistedState('ui.panel.console.visible', false)
  const [consoleExpanded, setConsoleExpanded] = usePersistedState('ui.panel.console.expanded', false)
  const logs = useBackendLogs(consoleOpen)

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault()
        window.dispatchEvent(new CustomEvent(OPEN_PALETTE_EVENT))
        return
      }
      if (event.key === 'Escape' && consoleOpen) {
        event.preventDefault()
        setConsoleOpen(false)
        setConsoleExpanded(false)
      }
    }
    const onOpen = () => {
      setPaletteOpen(true)
    }
    const onCollapse = () => {
      setCollapsed((value) => !value)
    }
    const onToggleConsole = () => {
      setConsoleOpen((value) => {
        if (value) {
          setConsoleExpanded(false)
        }
        return !value
      })
    }
    // Always-mounted production owner for av-kit:download:* palette events.
    const onDownloadAdd = () => {
      DOWNLOAD_COMMANDS.add()
    }
    const onDownloadStart = () => {
      DOWNLOAD_COMMANDS.start()
    }
    const onDownloadPause = () => {
      DOWNLOAD_COMMANDS.pause()
    }
    const onDownloadResume = () => {
      DOWNLOAD_COMMANDS.resume()
    }
    const onDownloadCancel = () => {
      DOWNLOAD_COMMANDS.cancel()
    }
    const onDownloadClear = () => {
      DOWNLOAD_COMMANDS.clear()
    }
    const onDownloadSabr = () => {
      DOWNLOAD_COMMANDS.sabrCheck()
    }
    // Always-mounted production owner for av-kit:transcript:* palette events.
    const onTranscriptAdd = () => {
      TRANSCRIPT_COMMANDS.add()
    }
    const onTranscriptStart = () => {
      TRANSCRIPT_COMMANDS.start()
    }
    const onTranscriptPause = () => {
      TRANSCRIPT_COMMANDS.pause()
    }
    const onTranscriptResume = () => {
      TRANSCRIPT_COMMANDS.resume()
    }
    const onTranscriptStop = () => {
      TRANSCRIPT_COMMANDS.stop()
    }
    window.addEventListener('keydown', onKey)
    window.addEventListener(OPEN_PALETTE_EVENT, onOpen)
    window.addEventListener(COLLAPSE_RAIL_EVENT, onCollapse)
    window.addEventListener('av-kit:toggle-console', onToggleConsole)
    window.addEventListener(DOWNLOAD_EVENTS.add, onDownloadAdd)
    window.addEventListener(DOWNLOAD_EVENTS.start, onDownloadStart)
    window.addEventListener(DOWNLOAD_EVENTS.pause, onDownloadPause)
    window.addEventListener(DOWNLOAD_EVENTS.resume, onDownloadResume)
    window.addEventListener(DOWNLOAD_EVENTS.cancel, onDownloadCancel)
    window.addEventListener(DOWNLOAD_EVENTS.clear, onDownloadClear)
    window.addEventListener(DOWNLOAD_EVENTS.sabrCheck, onDownloadSabr)
    window.addEventListener(TRANSCRIPT_EVENTS.add, onTranscriptAdd)
    window.addEventListener(TRANSCRIPT_EVENTS.start, onTranscriptStart)
    window.addEventListener(TRANSCRIPT_EVENTS.pause, onTranscriptPause)
    window.addEventListener(TRANSCRIPT_EVENTS.resume, onTranscriptResume)
    window.addEventListener(TRANSCRIPT_EVENTS.stop, onTranscriptStop)
    return () => {
      window.removeEventListener('keydown', onKey)
      window.removeEventListener(OPEN_PALETTE_EVENT, onOpen)
      window.removeEventListener(COLLAPSE_RAIL_EVENT, onCollapse)
      window.removeEventListener('av-kit:toggle-console', onToggleConsole)
      window.removeEventListener(DOWNLOAD_EVENTS.add, onDownloadAdd)
      window.removeEventListener(DOWNLOAD_EVENTS.start, onDownloadStart)
      window.removeEventListener(DOWNLOAD_EVENTS.pause, onDownloadPause)
      window.removeEventListener(DOWNLOAD_EVENTS.resume, onDownloadResume)
      window.removeEventListener(DOWNLOAD_EVENTS.cancel, onDownloadCancel)
      window.removeEventListener(DOWNLOAD_EVENTS.clear, onDownloadClear)
      window.removeEventListener(DOWNLOAD_EVENTS.sabrCheck, onDownloadSabr)
      window.removeEventListener(TRANSCRIPT_EVENTS.add, onTranscriptAdd)
      window.removeEventListener(TRANSCRIPT_EVENTS.start, onTranscriptStart)
      window.removeEventListener(TRANSCRIPT_EVENTS.pause, onTranscriptPause)
      window.removeEventListener(TRANSCRIPT_EVENTS.resume, onTranscriptResume)
      window.removeEventListener(TRANSCRIPT_EVENTS.stop, onTranscriptStop)
    }
  }, [consoleOpen, setCollapsed, setConsoleExpanded, setConsoleOpen])

  useEffect(() => {
    if (!consoleOpen && consoleExpanded) {
      setConsoleExpanded(false)
    }
  }, [consoleOpen, consoleExpanded, setConsoleExpanded])

  return (
    <div className="h-screen overflow-hidden flex flex-col bg-bg text-fg" data-testid="app-shell">
      <Header
        onConsoleToggle={() => {
          window.dispatchEvent(new CustomEvent(TOGGLE_CONSOLE_EVENT))
        }}
        onPaletteToggle={() => {
          window.dispatchEvent(new CustomEvent(OPEN_PALETTE_EVENT))
        }}
      />
      <div className="flex flex-1 min-h-0 overflow-hidden">
        <NavRail
          collapsed={collapsed}
          onNavigate={navigateShell}
          onCollapse={() => {
            setCollapsed((value) => !value)
          }}
        />
        <main className={consoleOpen && consoleExpanded ? 'hidden' : 'flex-1 min-h-0 overflow-auto'}>
          {children}
        </main>
        {consoleOpen ? (
          <ConsolePanel
            lines={logs.lines}
            expanded={consoleExpanded}
            onCopy={(lines) => {
              void copyVisibleLogs(lines, (text) => window.api.writeClipboardText(text))
            }}
            onLogToFile={(enabled) => {
              void putLogToFile(enabled, apiFetch)
            }}
            onClear={logs.clear}
            onExpand={() => {
              setConsoleExpanded(true)
            }}
            onClose={() => {
              setConsoleOpen(false)
              setConsoleExpanded(false)
            }}
            onCollapse={() => {
              setConsoleExpanded(false)
            }}
          />
        ) : null}
      </div>
      <CommandPalette open={paletteOpen} />
    </div>
  )
}
