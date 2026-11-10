import { useEffect, useMemo, useRef, useState, type ReactNode } from 'react'

import { CONVERT_COMMANDS, CONVERT_EVENTS } from '../../features/converter/convert-commands'
import { CAPTURE_COMMANDS, CAPTURE_EVENTS } from '../../features/capture/capture-commands'
import { DOWNLOAD_COMMANDS, DOWNLOAD_EVENTS } from '../../features/downloader/download-commands'
import {
  HELP_COMMANDS,
  HELP_EVENTS,
} from '../../features/settings/settings-commands'
import { TRANSCRIPT_COMMANDS, TRANSCRIPT_EVENTS } from '../../features/transcript/transcript-commands'
import { TTS_COMMANDS, TTS_EVENTS } from '../../features/tts/tts-commands'
import { useBackendLogs } from '../../hooks/useBackendLogs'
import { usePersistedState } from '../../hooks/usePersistedState'
import { apiFetch } from '../../lib/api'
import { COLLAPSE_RAIL_EVENT, navigateShell, TOGGLE_CONSOLE_EVENT } from '../../lib/shell-nav'
import { useSyncDocumentTheme } from '../../lib/theme'
import { getCommandState } from '../../registry/command-state'
import { listCommands } from '../../registry/commandRegistry'
import { createShortcutHandler, currentShellPage } from '../../registry/shortcuts'
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

/** Route area while the boot theme request has not settled (06 §Progressive Loading Strategy). */
export function RouteThemePending() {
  const [slow, setSlow] = useState(false)
  useEffect(() => {
    const timer = setTimeout(() => {
      setSlow(true)
    }, 3000)
    return () => {
      clearTimeout(timer)
    }
  }, [])
  return (
    <div data-testid="route-theme-pending" role="status" className="p-4 text-sm text-fg-muted">
      {slow ? 'Still loading…' : 'Connecting...'}
    </div>
  )
}

type AppShellProps = {
  children: ReactNode
}

export function AppShell({ children }: AppShellProps) {
  const [paletteOpen, setPaletteOpen] = useState(false)
  const paletteOpenRef = useRef(paletteOpen)
  paletteOpenRef.current = paletteOpen
  const [helpToggleSignal, setHelpToggleSignal] = useState(0)
  const helpToggleRef = useRef(helpToggleSignal)
  helpToggleRef.current = helpToggleSignal
  const [collapsed, setCollapsed] = usePersistedState('ui.rail.collapsed', false)
  const [consoleOpen, setConsoleOpen] = usePersistedState('ui.panel.console.visible', false)
  const [consoleExpanded, setConsoleExpanded] = usePersistedState('ui.panel.console.expanded', false)
  const logs = useBackendLogs(consoleOpen)
  const themeSettled = useSyncDocumentTheme()
  // Every registry chord, bound once (SHELL_WIRING). A stateful chord fires only
  // while its page publishes it enabled (COMMAND_STATE); no record fails closed.
  const shortcutHandler = useMemo(
    () =>
      createShortcutHandler({
        commands: listCommands(),
        getPage: currentShellPage,
        getState: getCommandState,
        isPaletteOpen: () => paletteOpenRef.current,
        closePalette: () => {
          setPaletteOpen(false)
        },
      }),
    [],
  )

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault()
        window.dispatchEvent(new CustomEvent(OPEN_PALETTE_EVENT))
        return
      }
      if (event.key === 'Escape' && paletteOpenRef.current) {
        event.preventDefault()
        setPaletteOpen(false)
        return
      }
      if (shortcutHandler(event)) {
        return
      }
      if (event.key === 'Escape' && consoleOpen) {
        event.preventDefault()
        setConsoleOpen(false)
        setConsoleExpanded(false)
      }
    }
    const onOpen = () => {
      setPaletteOpen((value) => !value)
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
    // Always-mounted production owner for av-kit:tts:* palette events.
    const onTtsPrepare = () => {
      TTS_COMMANDS.prepare()
    }
    const onTtsGenerate = () => {
      TTS_COMMANDS.generate()
    }
    const onConvertAdd = () => {
      CONVERT_COMMANDS.add()
    }
    const onConvertStart = () => {
      CONVERT_COMMANDS.start()
    }
    const onConvertPause = () => {
      CONVERT_COMMANDS.pause()
    }
    const onConvertResume = () => {
      CONVERT_COMMANDS.resume()
    }
    const onConvertCancel = () => {
      CONVERT_COMMANDS.cancel()
    }
    const onConvertClear = () => {
      CONVERT_COMMANDS.clear()
    }
    const onCaptureRegion = () => {
      window.requestAnimationFrame(() => {
        window.requestAnimationFrame(() => {
          CAPTURE_COMMANDS.region()
        })
      })
    }
    const onCaptureSave = () => {
      window.requestAnimationFrame(() => {
        window.requestAnimationFrame(() => {
          CAPTURE_COMMANDS.save()
        })
      })
    }
    const onCaptureOpenFolder = () => {
      window.requestAnimationFrame(() => {
        window.requestAnimationFrame(() => {
          CAPTURE_COMMANDS.open_folder()
        })
      })
    }
    const onHelpToggle = () => {
      const hash = window.location.hash.replace(/^#/, '') || '/'
      const path = hash.split('?')[0] ?? '/'
      const helpRoutes = ['/', '/transcript', '/tts', '/convert', '/capture', '/settings']
      if (!helpRoutes.includes(path)) {
        // Destination HelpCard is not mounted yet — queue toggle for mount.
        HELP_COMMANDS.queueToggleAfterNavigate()
        navigateShell('/settings')
      } else {
        HELP_COMMANDS.toggle()
      }
      setHelpToggleSignal((value) => value + 1)
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
    window.addEventListener(TTS_EVENTS.prepare, onTtsPrepare)
    window.addEventListener(TTS_EVENTS.generate, onTtsGenerate)
    // Always-mounted production owner for av-kit:convert: palette events.
    window.addEventListener(CONVERT_EVENTS.add, onConvertAdd)
    window.addEventListener(CONVERT_EVENTS.start, onConvertStart)
    window.addEventListener(CONVERT_EVENTS.pause, onConvertPause)
    window.addEventListener(CONVERT_EVENTS.resume, onConvertResume)
    window.addEventListener(CONVERT_EVENTS.cancel, onConvertCancel)
    window.addEventListener(CONVERT_EVENTS.clear, onConvertClear)
    window.addEventListener(CAPTURE_EVENTS.region, onCaptureRegion)
    window.addEventListener(CAPTURE_EVENTS.save, onCaptureSave)
    window.addEventListener(CAPTURE_EVENTS.open_folder, onCaptureOpenFolder)
    window.addEventListener(HELP_EVENTS.toggle, onHelpToggle)
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
      window.removeEventListener(TTS_EVENTS.prepare, onTtsPrepare)
      window.removeEventListener(TTS_EVENTS.generate, onTtsGenerate)
      window.removeEventListener(CONVERT_EVENTS.add, onConvertAdd)
      window.removeEventListener(CONVERT_EVENTS.start, onConvertStart)
      window.removeEventListener(CONVERT_EVENTS.pause, onConvertPause)
      window.removeEventListener(CONVERT_EVENTS.resume, onConvertResume)
      window.removeEventListener(CONVERT_EVENTS.cancel, onConvertCancel)
      window.removeEventListener(CONVERT_EVENTS.clear, onConvertClear)
      window.removeEventListener(CAPTURE_EVENTS.region, onCaptureRegion)
      window.removeEventListener(CAPTURE_EVENTS.save, onCaptureSave)
      window.removeEventListener(CAPTURE_EVENTS.open_folder, onCaptureOpenFolder)
      window.removeEventListener(HELP_EVENTS.toggle, onHelpToggle)
    }
  }, [consoleOpen, setCollapsed, setConsoleExpanded, setConsoleOpen, shortcutHandler])

  useEffect(() => {
    if (!consoleOpen && consoleExpanded) {
      setConsoleExpanded(false)
    }
  }, [consoleOpen, consoleExpanded, setConsoleExpanded])

  return (
    <div className="h-screen overflow-hidden flex flex-col bg-bg text-fg" data-testid="app-shell">
      <Header
        consoleOpen={consoleOpen}
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
        <main
          className={consoleOpen && consoleExpanded ? 'hidden' : 'flex-1 min-h-0 overflow-auto'}
          data-help-toggle={helpToggleSignal}
        >
          {themeSettled ? children : <RouteThemePending />}
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
            loadStartLevel={() => apiFetch('/settings/app')}
          />
        ) : null}
      </div>
      <CommandPalette
        open={paletteOpen}
        onClose={() => {
          setPaletteOpen(false)
        }}
      />
    </div>
  )
}
