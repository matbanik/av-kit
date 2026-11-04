export type SegmentOption = {
  id: string
  testId?: string
  value: string
  label: string
  disabled?: boolean
}

export type SegmentedControlProps = {
  name: string
  value: string
  options: readonly SegmentOption[]
  onValueChange: (value: string) => void
  testId?: string
  className?: string
  /** Accessible group name; defaults to `name` for existing callers. */
  label?: string
  /** `md` matches the 36 px control height (Button `md`); `sm` (default) keeps the original markup. */
  size?: 'sm' | 'md'
}

const GROUP_CLASSES = 'inline-flex rounded-[var(--radius-control)] border border-border bg-surface-0 p-0.5'

/** Visual segment over native, caller-identified radios. No free-form value reaches the caller. */
export function SegmentedControl({
  name, value, options, onValueChange, testId, className, label, size = 'sm',
}: SegmentedControlProps): React.JSX.Element {
  function choose(next: string): void {
    if (options.some((option) => option.value === next && !option.disabled)) {
      onValueChange(next)
    }
  }

  return (
    <fieldset aria-label={label ?? name} className={className} data-testid={testId}>
      <div className={size === 'md' ? `${GROUP_CLASSES} h-9` : GROUP_CLASSES}>
        {options.map((option) => (
          <label
            key={option.id}
            htmlFor={option.id}
            className={[
              'inline-flex cursor-pointer items-center gap-1 rounded-[var(--radius-sm)] px-2 py-1 text-sm',
              'transition-[background-color,color] duration-[var(--duration-fast)]',
              option.value === value ? 'bg-accent/15 text-accent' : 'text-fg-muted',
              option.disabled ? 'cursor-not-allowed opacity-50' : '',
            ].join(' ')}
          >
            <input
              id={option.id}
              data-testid={option.testId}
              type="radio"
              name={name}
              value={option.value}
              checked={option.value === value}
              disabled={option.disabled}
              onChange={(event) => choose(event.currentTarget.value)}
              className={option.value === value ? 'accent-accent bg-accent/15' : 'accent-accent'}
            />
            {option.label}
          </label>
        ))}
      </div>
    </fieldset>
  )
}
