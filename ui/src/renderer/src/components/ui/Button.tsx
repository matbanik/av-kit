import { forwardRef, type ButtonHTMLAttributes, type ReactNode } from 'react'

export type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive'
export type ButtonSize = 'sm' | 'md' | 'lg'

export type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant
  size?: ButtonSize
  icon?: boolean
  loading?: boolean
  children?: ReactNode
}

const variantClasses: Record<ButtonVariant, string> = {
  primary: 'bg-accent text-accent-fg hover:bg-accent-hover',
  secondary: 'bg-accent/12 text-accent hover:bg-accent/20',
  outline: 'outline-btn',
  ghost: 'bg-transparent hover:bg-neutral/30',
  destructive: 'bg-error-fill text-white hover:bg-error-fill-hover',
}

const sizeClasses: Record<ButtonSize, string> = {
  sm: 'h-7 px-2.5 text-sm gap-1.5',
  md: 'h-9 px-4 text-sm gap-2',
  lg: 'h-11 px-5 text-base gap-2',
}

const baseClasses = [
  'inline-flex items-center justify-center font-medium select-none',
  'rounded-[var(--radius-control)]',
  'transition-[background-color,border-color,color,opacity]',
  'duration-[var(--duration-fast)] ease-[var(--ease-out)]',
  'focus-visible:outline-none focus-visible:shadow-[0_0_0_3px_var(--color-accent-ring)]',
  'disabled:opacity-50 disabled:pointer-events-none',
].join(' ')

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  {
    variant = 'secondary',
    size = 'md',
    icon = false,
    loading = false,
    disabled,
    className,
    children,
    type = 'button',
    ...rest
  },
  ref,
) {
  const classes = [
    baseClasses,
    variantClasses[variant],
    // The variant is also named in the DOM, not only expressed as colour, so a
    // reader (and an audit) can tell a destructive button from a secondary one
    // without decoding the utility classes it happens to carry today.
    `btn-${variant}`,
    icon ? 'p-0 aspect-square' : sizeClasses[size],
    className ?? '',
  ].join(' ')
  return (
    <button
      ref={ref}
      type={type}
      className={classes}
      disabled={disabled || loading}
      aria-busy={loading}
      {...rest}
    >
      {children}
    </button>
  )
})
