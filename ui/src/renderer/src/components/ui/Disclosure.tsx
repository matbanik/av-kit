import type { ReactNode } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'

import { Button, type ButtonVariant } from './Button'

export type DisclosureProps = {
  id: string
  title: string
  open: boolean
  onOpenChange: (open: boolean) => void
  children: ReactNode
  testId?: string
  className?: string
  /** Trigger variant; defaults to `ghost`, which every page used before MEU-65. */
  variant?: ButtonVariant
  /** Leading icon rendered before the title (callers pass it `aria-hidden`). */
  icon?: ReactNode
  /** Trailing chevron whose `data-state` follows `open`; its wrapper test id is `${id}-chevron`. */
  chevron?: boolean
}

/** Controlled, native-button disclosure. The hidden panel stays associated but cannot receive focus. */
export function Disclosure({
  id, title, open, onOpenChange, children, testId, className, variant = 'ghost', icon, chevron = false,
}: DisclosureProps): React.JSX.Element {
  const panelId = `${id}-panel`
  return (
    <section className={className}>
      <Button
        aria-controls={panelId}
        aria-expanded={open}
        data-testid={testId}
        onClick={() => onOpenChange(!open)}
        variant={variant}
      >
        {icon}
        {title}
        {chevron ? (
          <span data-testid={`${id}-chevron`} data-state={open ? 'open' : 'closed'} className="inline-flex">
            {open ? <ChevronUp size={16} aria-hidden="true" /> : <ChevronDown size={16} aria-hidden="true" />}
          </span>
        ) : null}
      </Button>
      <div id={panelId} hidden={!open}>
        {children}
      </div>
    </section>
  )
}
