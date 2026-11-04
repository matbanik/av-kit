/**
 * Verb-labelled confirmation dialog rendered through a portal (G20_RULE).
 *
 * Replaces the native `confirm()` the queue surfaces used to call: that dialog
 * cannot be styled, cannot be tested, and blocks the Electron renderer. The
 * confirm button is labelled with the caller's *verb* ("Remove", "Clear") rather
 * than a generic affirmative, so the consequence is legible without re-reading
 * the title.
 */
import { useEffect, useId, useRef, type ReactElement } from 'react'
import { createPortal } from 'react-dom'

import { Button } from './Button'

export type ConfirmModalProps = {
  /** Whether the dialog is mounted. */
  open: boolean
  /** Dialog heading; also the accessible name. */
  title: string
  /** Optional supporting sentence below the heading. */
  description?: string
  /** Verb label for the confirm button — never a bare affirmative. */
  confirmLabel: string
  /** Label for the dismiss button. */
  cancelLabel?: string
  /** Whether the confirm button reads as destructive. */
  destructive?: boolean
  /** Invoked when the user confirms. */
  onConfirm: () => void
  /** Invoked on dismiss: cancel button, Escape, or a backdrop click. */
  onCancel: () => void
}

const FOCUSABLE_SELECTOR = [
  'a[href]',
  'button:not([disabled])',
  'input:not([disabled])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  '[tabindex]:not([tabindex="-1"])',
].join(',')

const backdropClasses = [
  'fixed inset-0 z-50 flex items-center justify-center',
  'bg-black/50 p-4',
].join(' ')

const dialogClasses = [
  'w-full max-w-sm rounded-[var(--radius-lg)] bg-bg-elevated',
  'border border-border p-5 shadow-lg',
].join(' ')

/**
 * Render the confirmation dialog.
 *
 * @param props - See {@link ConfirmModalProps}.
 * @returns The portalled dialog, or `null` when closed.
 */
export function ConfirmModal({
  open,
  title,
  description,
  confirmLabel,
  cancelLabel = 'Cancel',
  destructive = true,
  onConfirm,
  onCancel,
}: ConfirmModalProps): ReactElement | null {
  const titleId = useId()
  const descriptionId = useId()
  const dialogRef = useRef<HTMLDivElement | null>(null)
  const cancelRef = useRef<HTMLButtonElement | null>(null)

  useEffect(() => {
    if (!open) {
      return
    }
    cancelRef.current?.focus()
  }, [open])

  if (!open) {
    return null
  }

  /** Keep Tab inside the dialog; route Escape to dismiss. */
  const handleKeyDown = (event: React.KeyboardEvent<HTMLDivElement>): void => {
    if (event.key === 'Escape') {
      event.preventDefault()
      onCancel()
      return
    }
    if (event.key !== 'Tab') {
      return
    }
    const dialog = dialogRef.current
    if (dialog === null) {
      return
    }
    const focusable = Array.from(dialog.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR))
    if (focusable.length === 0) {
      return
    }
    event.preventDefault()
    const active = document.activeElement
    const current = active instanceof HTMLElement ? focusable.indexOf(active) : -1
    const step = event.shiftKey ? -1 : 1
    const next = (current + step + focusable.length) % focusable.length
    focusable[next].focus()
  }

  return createPortal(
    <div
      className={backdropClasses}
      data-confirm-backdrop=""
      onKeyDown={handleKeyDown}
      onClick={(event) => {
        if (event.target === event.currentTarget) {
          onCancel()
        }
      }}
    >
      <div
        ref={dialogRef}
        className={dialogClasses}
        data-testid="confirm-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={description === undefined ? undefined : descriptionId}
      >
        <h2 id={titleId} className="text-base font-semibold text-fg">
          {title}
        </h2>
        {description === undefined ? null : (
          <p id={descriptionId} className="mt-2 text-sm text-fg-muted">
            {description}
          </p>
        )}
        <div className="mt-5 flex justify-end gap-2">
          <Button
            ref={cancelRef}
            variant="ghost"
            size="sm"
            data-testid="confirm-modal-cancel"
            onClick={onCancel}
          >
            {cancelLabel}
          </Button>
          <Button
            variant={destructive ? 'destructive' : 'primary'}
            size="sm"
            data-testid="confirm-modal-confirm"
            onClick={onConfirm}
          >
            {confirmLabel}
          </Button>
        </div>
      </div>
    </div>,
    document.body,
  )
}
