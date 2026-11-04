import { cloneElement, type ReactElement, type ReactNode } from 'react'

export type FormRowProps = {
  id: string
  label: string
  hint?: string
  error?: string
  children: ReactElement
  suffix?: ReactNode
  testId?: string
  className?: string
}

type ControlProps = {
  id?: string
  'aria-describedby'?: string
  'aria-invalid'?: boolean
}

/** Associates one caller-supplied control with its label, hint, and error. */
export function FormRow({
  id, label, hint, error, children, suffix, testId, className,
}: FormRowProps): React.JSX.Element {
  const control = children as ReactElement<ControlProps>
  const description = [control.props['aria-describedby'], hint && `${id}-hint`, error && `${id}-error`]
    .filter(Boolean).join(' ')
  return (
    <div className={['grid gap-1.5 sm:grid-cols-[10.5rem_minmax(0,1fr)] sm:items-start', className ?? ''].join(' ')} data-testid={testId}>
      <label htmlFor={id} className="text-sm text-fg">{label}</label>
      <div className="min-w-0">
        <div className="flex min-w-0 items-center gap-2">
          {cloneElement(control, {
            id,
            'aria-describedby': description || undefined,
            'aria-invalid': Boolean(error),
          })}
          {suffix}
        </div>
        {hint && <p id={`${id}-hint`} className="mt-1 text-xs text-fg-muted">{hint}</p>}
        {error && <p id={`${id}-error`} className="mt-1 text-xs text-error">{error}</p>}
      </div>
    </div>
  )
}
