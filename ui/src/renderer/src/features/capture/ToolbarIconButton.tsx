import { Button, type ButtonVariant } from '../../components/ui/Button'
import { Tooltip } from '../../components/ui/Tooltip'
import { ariaKeyshortcuts } from '../../registry/shortcuts'
import type { ToolbarButtonSpec } from './capture-toolbar'

type ToolbarIconButtonProps = {
  spec: ToolbarButtonSpec
  id: string
  variant: ButtonVariant
  pressed?: boolean
  disabled?: boolean
  /** Why the button is disabled; the hint shows it after the name (HINT_TEXT). */
  reason?: string
  /** The chord that runs this button; the hint shows it after the name (HINTS). */
  shortcut?: string
  onClick: () => void
}

/**
 * ICON_BUTTON: an `sm` button whose only child is its hidden 16 px lucide icon. The name is the aria-label and
 * the rendered Tooltip hint; there is no `title`.
 */
export function ToolbarIconButton({
  spec,
  id,
  variant,
  pressed,
  disabled = false,
  reason,
  shortcut,
  onClick,
}: ToolbarIconButtonProps) {
  const { icon: Icon, name } = spec
  const label = shortcut === undefined ? name : `${name} (${shortcut})`
  return (
    <Tooltip id={id} label={label} reason={reason} disabled={disabled}>
      <Button
        size="sm"
        variant={variant}
        data-testid={id}
        aria-label={name}
        aria-pressed={pressed}
        aria-keyshortcuts={shortcut === undefined ? undefined : ariaKeyshortcuts(shortcut)}
        disabled={disabled}
        onClick={onClick}
      >
        <Icon size={16} aria-hidden="true" />
      </Button>
    </Tooltip>
  )
}
