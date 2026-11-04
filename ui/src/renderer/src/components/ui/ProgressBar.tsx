/**
 * Determinate progress bar for queue rows (G33_RULE).
 *
 * The fill animates `transform: scaleX(...)` rather than a geometry property.
 * Animating geometry runs layout on every frame for every visible row, which is
 * the jank this redesign exists to remove; `transform` is composited instead.
 */
import type { ReactElement } from 'react'

import { PROGRESS_FILL_CLASSES, type ProgressTone } from '../../lib/queue/status-tokens'

export type ProgressBarProps = {
  /** Progress in the 0..1 range. Out-of-range and NaN values are clamped. */
  value: number
  /** Override the default `data-testid`. */
  testId?: string
  /** Extra classes appended to the track. */
  className?: string
  /** Accessible name, when the bar is not already labelled by its row. */
  ariaLabel?: string
  /** Fill tone; `success` marks a finished row. Defaults to `accent`. */
  tone?: ProgressTone
}

/**
 * Clamp an arbitrary number into the 0..1 progress range.
 *
 * @param value - Raw progress, possibly NaN or out of range.
 * @returns A finite ratio in 0..1.
 */
function clampRatio(value: number): number {
  if (!Number.isFinite(value)) {
    return 0
  }
  if (value < 0) {
    return 0
  }
  if (value > 1) {
    return 1
  }
  return value
}

const trackClasses = [
  'relative h-1.5 w-full overflow-hidden',
  'rounded-[var(--radius-full)] bg-neutral/30',
].join(' ')

/**
 * Fill classes for one tone. The hue comes from `PROGRESS_FILL_CLASSES`; the
 * geometry and motion are shared, so a tone can never change how the bar moves.
 *
 * @param tone - The fill tone.
 * @returns The fill element's class list.
 */
function fillClasses(tone: ProgressTone): string {
  return [
    'absolute inset-0',
    PROGRESS_FILL_CLASSES[tone],
    'rounded-[var(--radius-full)] transition-[transform]',
  ].join(' ')
}

/**
 * Render the progress bar.
 *
 * @param props - See {@link ProgressBarProps}.
 * @returns A `progressbar` element whose fill is driven by a transform.
 */
export function ProgressBar({
  value,
  testId = 'progress-bar',
  className,
  ariaLabel,
  tone = 'accent',
}: ProgressBarProps): ReactElement {
  const ratio = clampRatio(value)
  const percent = Math.round(ratio * 100)
  return (
    <div
      className={[trackClasses, className ?? ''].filter((part) => part !== '').join(' ')}
      data-testid={testId}
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={percent}
      aria-label={ariaLabel}
    >
      <div
        className={fillClasses(tone)}
        data-progress-fill=""
        style={{
          transform: `scaleX(${String(ratio)})`,
          transformOrigin: 'left',
          transitionDuration: 'var(--duration-normal)',
          transitionTimingFunction: 'var(--ease-out)',
        }}
      />
    </div>
  )
}
