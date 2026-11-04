export type StatusChipTone = 'neutral' | 'info' | 'success' | 'warning' | 'danger'

export type StatusChipProps = {
  label: string
  count?: number
  tone: StatusChipTone
  testId?: string
  className?: string
}

const toneClasses: Record<StatusChipTone, string> = {
  neutral: 'bg-neutral/10 text-fg',
  info: 'bg-accent-cyan/10 text-fg',
  success: 'bg-status-filled/10 text-fg',
  warning: 'bg-status-pending/10 text-fg',
  danger: 'bg-status-rejected/10 text-fg',
}

/** Count and status stay legible as text in every theme; hue is secondary. */
export function StatusChip({
  label, count, tone, testId, className,
}: StatusChipProps): React.JSX.Element {
  const readable = label.trim()
  if (!readable) throw new Error('StatusChip needs a readable label')
  const safeTone = Object.hasOwn(toneClasses, tone) ? tone : 'neutral'
  return (
    <span
      className={[
        'inline-flex items-center gap-1 rounded-[var(--radius-full)] px-2 py-0.5 text-xs font-medium',
        toneClasses[safeTone], className ?? '',
      ].join(' ')}
      data-testid={testId}
      data-tone={safeTone}
    >
      <span>{readable}</span>
      {count !== undefined && <span>{count}</span>}
    </span>
  )
}
