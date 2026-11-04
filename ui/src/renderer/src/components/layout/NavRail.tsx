import { Camera, Download, FileText, Film, PanelLeftClose, PanelLeftOpen, Settings, Volume2 } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

import { ariaKeyshortcuts } from '../../registry/shortcuts'
import { Button } from '../ui/Button'

export const SHELL_PRIMARY_NAV = [
  { id: 'nav:downloader', path: '/', shortcut: 'Ctrl+1', testid: 'nav-downloader', label: 'Downloader' },
  {
    id: 'nav:transcript',
    path: '/transcript',
    shortcut: 'Ctrl+2',
    testid: 'nav-transcript',
    label: 'Transcript',
  },
  { id: 'nav:tts', path: '/tts', shortcut: 'Ctrl+3', testid: 'nav-tts', label: 'TTS' },
  { id: 'nav:convert', path: '/convert', shortcut: 'Ctrl+4', testid: 'nav-convert', label: 'Convert' },
  { id: 'nav:capture', path: '/capture', shortcut: 'Ctrl+5', testid: 'nav-capture', label: 'Capture' },
] as const

export const SHELL_PINNED_NAV = [
  {
    id: 'nav:settings',
    path: '/settings',
    shortcut: 'Ctrl+,',
    testid: 'nav-settings',
    label: 'Settings',
  },
] as const

export const SHELL_NAV = [
  ...SHELL_PRIMARY_NAV,
  ...SHELL_PINNED_NAV,
  { id: 'nav:collapse', path: '', shortcut: 'Ctrl+B', testid: 'nav-collapse', label: 'Collapse' },
] as const

const NAV_ICONS: Record<(typeof SHELL_NAV)[number]['id'], LucideIcon> = {
  'nav:downloader': Download,
  'nav:transcript': FileText,
  'nav:tts': Volume2,
  'nav:convert': Film,
  'nav:capture': Camera,
  'nav:settings': Settings,
  'nav:collapse': PanelLeftClose,
}

type NavRailProps = {
  collapsed?: boolean
  onNavigate?: (path: string) => void
  onCollapse?: () => void
}

export function NavRail({ collapsed = false, onNavigate, onCollapse }: NavRailProps) {
  const primary = SHELL_NAV.filter(
    (item) => item.id !== 'nav:settings' && item.id !== 'nav:collapse',
  )
  const settings = SHELL_NAV.find((item) => item.id === 'nav:settings')
  const collapse = SHELL_NAV.find((item) => item.id === 'nav:collapse')

  const renderItem = (item: (typeof SHELL_NAV)[number], opts?: { iconOnly?: boolean }) => {
    const Icon = item.id === 'nav:collapse' && collapsed ? PanelLeftOpen : NAV_ICONS[item.id]
    const name = item.id === 'nav:collapse' ? (collapsed ? 'Expand sidebar' : 'Collapse sidebar') : item.label
    return (
      <Button
        key={item.id}
        type="button"
        variant="ghost"
        size="sm"
        icon={collapsed}
        className={`w-full ${collapsed ? 'justify-center' : 'justify-start'}`}
        data-testid={item.testid}
        title={`${name} (${item.shortcut})`}
        aria-label={name}
        aria-keyshortcuts={ariaKeyshortcuts(item.shortcut)}
        onClick={() => {
          if (item.id === 'nav:collapse') {
            onCollapse?.()
            return
          }
          onNavigate?.(item.path)
        }}
      >
        <Icon size={18} aria-hidden="true" />
        {collapsed || opts?.iconOnly ? null : <span>{item.label}</span>}
      </Button>
    )
  }

  return (
    <nav
      className={`nav-rail ${collapsed ? 'nav-rail--collapsed' : ''}`}
      aria-label="Main"
    >
      <div className="flex flex-col gap-1 p-2 flex-1">
        {primary.map((item) => renderItem(item))}
      </div>
      {settings ? <div className="p-2 mt-auto">{renderItem(settings)}</div> : null}
      {collapse ? <div className="p-2 border-t border-bg-elevated">{renderItem(collapse)}</div> : null}
    </nav>
  )
}
