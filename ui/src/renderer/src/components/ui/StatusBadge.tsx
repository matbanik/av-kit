/**
 * Status pill and decorative status dot for queue surfaces.
 *
 * The pill always carries a *text* label — colour alone never conveys the
 * status (WCAG 2.2 SC 1.4.1). The dot beside it is `aria-hidden`, so a screen
 * reader announces the status exactly once.
 */
import { Circle } from 'lucide-react'
import type { ReactElement } from 'react'

import { resolveStatusPill } from '../../lib/queue/status-tokens'

export type StatusBadgeProps = {
  /** Status name as the API reported it. Unknown values render muted. */
  status: string
  /** Override the default `data-testid`. */
  testId?: string
  /** Extra classes appended after the token classes. */
  className?: string
}

const badgeBaseClasses = [
  'inline-flex items-center gap-1.5 px-2 py-0.5',
  'rounded-[var(--radius-full)] text-xs font-medium whitespace-nowrap',
].join(' ')

/**
 * Render the status pill.
 *
 * @param props - See {@link StatusBadgeProps}.
 * @returns A labelled pill painted from the canonical token table.
 */
export function StatusBadge({
  status,
  testId = 'status-badge',
  className,
}: StatusBadgeProps): ReactElement {
  const pill = resolveStatusPill(status)
  const classes = [badgeBaseClasses, pill.fillClass, pill.labelClass, className ?? '']
    .filter((part) => part !== '')
    .join(' ')
  return (
    <span className={classes} data-testid={testId} data-status={pill.slug}>
      <Circle className="h-2 w-2 fill-current" aria-hidden="true" />
      {status}
    </span>
  )
}

export type StatusIconProps = {
  /** Status name as the API reported it. */
  status: string
  /** Override the default `data-testid`. */
  testId?: string
  /** Extra classes appended after the token classes. */
  className?: string
}

/**
 * Render the decorative status dot used on the collapsed card row.
 *
 * Purely redundant with the adjacent pill label, so it is hidden from the
 * accessibility tree rather than announced twice.
 *
 * @param props - See {@link StatusIconProps}.
 * @returns An `aria-hidden` hue-coloured dot.
 */
export function StatusIcon({
  status,
  testId = 'queue-card-status-icon',
  className,
}: StatusIconProps): ReactElement {
  const pill = resolveStatusPill(status)
  const classes = ['inline-flex items-center', pill.iconClass, className ?? '']
    .filter((part) => part !== '')
    .join(' ')
  return (
    <span className={classes} data-testid={testId} data-status={pill.slug} aria-hidden="true">
      <Circle className="h-2.5 w-2.5 fill-current" aria-hidden="true" />
    </span>
  )
}
