import { Command, SquareTerminal } from 'lucide-react'
import { useEffect, useState } from 'react'

import rottibooMark from '../../assets/rottiboo.png'
import { ariaKeyshortcuts } from '../../registry/shortcuts'
import { Button } from '../ui/Button'

const PAGE_LABELS: Record<string, string> = {
  '/': 'Downloader',
  '/transcript': 'Transcript',
  '/tts': 'TTS',
  '/convert': 'Convert',
  '/capture': 'Capture',
  '/settings': 'Settings',
}

function pageLabelFromHash(): string {
  const raw = window.location.hash.replace(/^#/, '')
  const path = raw === '' ? '/' : raw
  return PAGE_LABELS[path] ?? 'Downloader'
}

type HeaderProps = {
  /** Whether the Console panel is mounted; drives the toggle's pressed state (MEU-69). */
  consoleOpen: boolean
  onConsoleToggle: () => void
  onPaletteToggle: () => void
}

export function Header({ consoleOpen, onConsoleToggle, onPaletteToggle }: HeaderProps) {
  const [pageLabel, setPageLabel] = useState(pageLabelFromHash)

  useEffect(() => {
    const sync = () => {
      setPageLabel(pageLabelFromHash())
    }
    window.addEventListener('hashchange', sync)
    return () => {
      window.removeEventListener('hashchange', sync)
    }
  }, [])

  return (
    <header className="header-breadcrumb">
      <nav aria-label="Breadcrumb" className="header-breadcrumb__nav">
        <img className="header-breadcrumb__mark" src={rottibooMark} alt="" aria-hidden="true" />
        <span className="header-breadcrumb__brand">av-kit</span>
        <span className="header-breadcrumb__separator" aria-hidden="true">
          ›
        </span>
        <span className="header-breadcrumb__page">{pageLabel}</span>
      </nav>
      <div className="flex items-center gap-2">
        {/* Toggle button: the label stays "Console"; the pressed state is aria-pressed plus the
            tinted secondary variant. The transparent border keeps the outline variant's width. */}
        <Button
          type="button"
          variant={consoleOpen ? 'secondary' : 'outline'}
          size="sm"
          className={consoleOpen ? 'border border-transparent' : undefined}
          aria-pressed={consoleOpen ? 'true' : 'false'}
          data-testid="header-console-btn"
          title="Console (Ctrl+J)"
          aria-keyshortcuts={ariaKeyshortcuts('Ctrl+J')}
          onClick={onConsoleToggle}
        >
          <SquareTerminal size={14} aria-hidden="true" />
          Console
        </Button>
        <Button
          type="button"
          variant="outline"
          size="sm"
          data-testid="header-palette-btn"
          aria-label="Commands"
          aria-keyshortcuts="Control+K"
          title="Open the command palette (Ctrl+K)"
          onClick={onPaletteToggle}
        >
          <Command size={14} aria-hidden="true" />
          Commands
          <kbd className="text-xs text-fg-muted">Ctrl+K</kbd>
        </Button>
      </div>
    </header>
  )
}
