import { Button } from './Button'
import { FormRow } from './FormRow'

export type PathRowProps = {
  id: string
  label: string
  value: string
  onChange: (value: string) => void
  onBrowse?: () => void
  hint?: string
  error?: string
  testId?: string
  inputTestId?: string
  browseTestId?: string
  /** Additive (MEU-58): a path that only Browse may change. */
  readOnly?: boolean
  /** Additive (MEU-93): shown in the empty input. */
  placeholder?: string
  /** Additive (MEU-93): disables Browse only; the field keeps its own state. */
  browseDisabled?: boolean
  className?: string
}

/** A controlled path field with an optional caller-owned Browse action. */
export function PathRow({
  id, label, value, onChange, onBrowse, hint, error, testId, inputTestId, browseTestId, readOnly = false, placeholder,
  browseDisabled, className,
}: PathRowProps): React.JSX.Element {
  return (
    <FormRow
      id={id}
      label={label}
      hint={hint}
      error={error}
      testId={testId}
      className={className}
      suffix={onBrowse ? (
        <Button data-testid={browseTestId ?? (testId ? `${testId}-browse` : undefined)} onClick={onBrowse} disabled={browseDisabled} variant="secondary" size="sm">
          Browse
        </Button>
      ) : undefined}
    >
      <input
        data-testid={inputTestId}
        value={value}
        placeholder={placeholder}
        readOnly={readOnly}
        onChange={(event) => {
          if (!readOnly) onChange(event.currentTarget.value)
        }}
        className="min-w-0 flex-1 rounded-[var(--radius-control)] border border-border bg-surface-0 px-2 py-1 text-fg focus-visible:outline-accent"
      />
    </FormRow>
  )
}
