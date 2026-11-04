/**
 * Tri-state selection checkbox for queue rows and select-all headers (G32_RULE).
 *
 * `indeterminate` is a DOM *property*, not an attribute — React will not set it
 * from JSX, so it is applied through a ref in an effect. The accent colour comes
 * from `--color-accent` with no hex fallback, so the light/dark swap is handled
 * entirely by the token layer.
 *
 * `onChange` also reports the modifier state (`SELECTION_PRIMITIVE_EXTENSION`),
 * because `SELECTION_MODEL`'s Shift+click range select is only reachable if the
 * modifier survives the hop from the DOM event to the page's selection state.
 */
import { useEffect, useRef, type ReactElement } from 'react'

/** The modifier state a selection gesture carried. */
export type SelectionCheckboxModifiers = {
  /** Whether Shift was held — the range-select chord. */
  shiftKey: boolean
}

export type SelectionCheckboxProps = {
  /** Whether the box is checked. */
  checked: boolean
  /** Whether the box shows the mixed state. Ignored when `checked` is true. */
  indeterminate?: boolean
  /**
   * Called with the checkbox's next checked state and the modifier state the
   * gesture carried. `shiftKey` is always a boolean, never absent: a caller
   * reads it directly, so an undefined object is a range select that silently
   * degrades to a single toggle.
   */
  onChange: (checked: boolean, modifiers: SelectionCheckboxModifiers) => void
  /** Accessible name — required, since the box renders no visible label. */
  ariaLabel: string
  /** Override the default `data-testid`. */
  testId?: string
  /** Whether interaction is disabled. */
  disabled?: boolean
  /** Extra classes appended after the base classes. */
  className?: string
}

const baseClasses = [
  'h-4 w-4 shrink-0 cursor-pointer',
  'rounded-[var(--radius-control)] border border-border',
  'focus-visible:outline-none focus-visible:shadow-[0_0_0_3px_var(--color-accent-ring)]',
  'disabled:opacity-50 disabled:cursor-not-allowed',
].join(' ')

/**
 * Render the selection checkbox.
 *
 * The click is stopped from propagating so that toggling selection inside an
 * activatable card row never also activates the row itself.
 *
 * @param props - See {@link SelectionCheckboxProps}.
 * @returns A tri-state checkbox input.
 */
export function SelectionCheckbox({
  checked,
  indeterminate = false,
  onChange,
  ariaLabel,
  testId = 'selection-checkbox',
  disabled = false,
  className,
}: SelectionCheckboxProps): ReactElement {
  const ref = useRef<HTMLInputElement | null>(null)

  useEffect(() => {
    const input = ref.current
    if (input === null) {
      return
    }
    input.indeterminate = !checked && indeterminate
  }, [checked, indeterminate])

  return (
    <input
      ref={ref}
      type="checkbox"
      checked={checked}
      disabled={disabled}
      aria-label={ariaLabel}
      data-testid={testId}
      className={[baseClasses, className ?? ''].filter((part) => part !== '').join(' ')}
      style={{ accentColor: 'var(--color-accent)' }}
      onChange={(event) => {
        /*
          React drives a checkbox's onChange from the native CLICK event, so the
          modifiers are on `nativeEvent` — and keyboard Space synthesises a click
          too, which is why no separate key handler is needed. The `in` guard
          keeps a synthetic non-mouse event from producing `undefined`.
        */
        const native: Event = event.nativeEvent
        const shiftKey = 'shiftKey' in native ? (native as MouseEvent).shiftKey === true : false
        onChange(event.target.checked, { shiftKey })
      }}
      onClick={(event) => {
        event.stopPropagation()
      }}
    />
  )
}
