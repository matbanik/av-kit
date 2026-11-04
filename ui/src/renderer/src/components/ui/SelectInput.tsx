import { forwardRef, useId, type SelectHTMLAttributes } from 'react'

import { useDocumentTheme, type UiTheme } from '../../lib/theme'

export type SelectOption = {
  value: string
  label: string
}

export type SelectInputProps = Omit<SelectHTMLAttributes<HTMLSelectElement>, 'children'> & {
  label: string
  options: SelectOption[]
  error?: string
}

const G30_PAIRS: Record<UiTheme, { backgroundColor: string; color: string }> = {
  dark: { backgroundColor: '#1a1a2e', color: '#e0e0e0' },
  light: { backgroundColor: '#ffffff', color: '#1e293b' },
}

/** G30 inline pair for a native select and its option menu in `theme`. */
export function g30StylesFor(theme: UiTheme): { backgroundColor: string; color: string } {
  return G30_PAIRS[theme]
}

/** G30 pair for the current document theme; the caller re-renders when the theme changes. */
export function useG30Styles(): { backgroundColor: string; color: string } {
  return g30StylesFor(useDocumentTheme())
}

const baseClasses = [
  'w-full h-9 px-3 text-sm font-sans cursor-pointer',
  'rounded-[var(--radius-control)]',
  'border border-border bg-surface-0 text-fg',
  'transition-[border-color,box-shadow]',
  'duration-[var(--duration-fast)] ease-[var(--ease-out)]',
  'hover:border-border-hover',
  'focus:border-accent focus:shadow-[0_0_0_3px_var(--color-accent-ring)] focus:outline-none',
  'disabled:border-border/50 disabled:bg-surface-0/50 disabled:pointer-events-none disabled:opacity-[0.38]',
].join(' ')

export const SelectInput = forwardRef<HTMLSelectElement, SelectInputProps>(function SelectInput(
  { label, options, error, className, id: externalId, style: callerStyle, ...props },
  ref,
) {
  const generatedId = useId()
  const id = externalId ?? generatedId
  const g30 = useG30Styles()
  const mergedSelectStyle = { ...callerStyle, ...g30 }
  const classes = [baseClasses, error ? 'border-error-border' : '', className]
    .filter(Boolean)
    .join(' ')
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={id} className="text-sm font-medium text-fg-muted">
        {label}
      </label>
      <select ref={ref} id={id} className={classes} style={mergedSelectStyle} {...props}>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value} style={g30}>
            {opt.label}
          </option>
        ))}
      </select>
      {error ? <span className="text-sm text-error">{error}</span> : null}
    </div>
  )
})
