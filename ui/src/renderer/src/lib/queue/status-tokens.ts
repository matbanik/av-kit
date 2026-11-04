/**
 * Canonical status → pill token table for every av-kit queue surface.
 *
 * MEU-41 fixed the palette in `styles.css`; this module is the single runtime
 * binding of a job status to the classes that render its pill (AC-43.2). No hex
 * is authored here — every colour arrives through a `--color-*` custom property,
 * so the light/dark theme swap is handled entirely by the token layer.
 *
 * `fillAlpha` is 0.1 for every status: the label is `--color-fg` painted over a
 * 10% hue wash, which clears WCAG 2.2 SC 1.4.3 on all four card backdrops in
 * both themes (the 80-pairing matrix is pinned in `contrast-matrix.json`).
 */

/** One status's rendering contract: the token it reads and the classes it binds. */
export type StatusPill = {
  /** Lower-cased status name, for `data-*` attributes and CSS hooks. */
  readonly slug: string
  /** The `--color-*` custom property this pill's hue comes from. */
  readonly token: string
  /** Alpha the hue is composited at to produce the pill fill. */
  readonly fillAlpha: number
  /** Tailwind class painting the pill background. */
  readonly fillClass: string
  /** Tailwind class painting the pill label. */
  readonly labelClass: string
  /** Tailwind class painting the (decorative) status icon. */
  readonly iconClass: string
}

/**
 * The pill table. Deliberately one statement: a second, rival status→colour map
 * is the defect this MEU exists to remove, so there is exactly one place to edit.
 */
export const STATUS_PILL_TOKENS = {
  Pending: {
    slug: 'pending',
    token: '--color-status-pending',
    fillAlpha: 0.1,
    fillClass: 'bg-status-pending/10',
    labelClass: 'text-fg',
    iconClass: 'text-status-pending',
  },
  Processing: {
    slug: 'processing',
    token: '--color-accent-cyan',
    fillAlpha: 0.1,
    fillClass: 'bg-accent-cyan/10',
    labelClass: 'text-fg',
    iconClass: 'text-accent-cyan',
  },
  Downloading: {
    slug: 'downloading',
    token: '--color-accent-cyan',
    fillAlpha: 0.1,
    fillClass: 'bg-accent-cyan/10',
    labelClass: 'text-fg',
    iconClass: 'text-accent-cyan',
  },
  Paused: {
    slug: 'paused',
    token: '--color-accent-yellow',
    fillAlpha: 0.1,
    fillClass: 'bg-accent-yellow/10',
    labelClass: 'text-fg',
    iconClass: 'text-accent-yellow',
  },
  Done: {
    slug: 'done',
    token: '--color-status-filled',
    fillAlpha: 0.1,
    fillClass: 'bg-status-filled/10',
    labelClass: 'text-fg',
    iconClass: 'text-status-filled',
  },
  Failed: {
    slug: 'failed',
    token: '--color-status-rejected',
    fillAlpha: 0.1,
    fillClass: 'bg-status-rejected/10',
    labelClass: 'text-fg',
    iconClass: 'text-status-rejected',
  },
  Skipped: {
    slug: 'skipped',
    token: '--color-accent-purple',
    fillAlpha: 0.1,
    fillClass: 'bg-accent-purple/10',
    labelClass: 'text-fg',
    iconClass: 'text-accent-purple',
  },
  Cancelled: {
    slug: 'cancelled',
    token: '--color-status-canceled',
    fillAlpha: 0.1,
    fillClass: 'bg-status-canceled/10',
    labelClass: 'text-fg',
    iconClass: 'text-status-canceled',
  },
  QualityBlocked: {
    slug: 'qualityblocked',
    token: '--color-accent-orange',
    fillAlpha: 0.1,
    fillClass: 'bg-accent-orange/10',
    labelClass: 'text-fg',
    iconClass: 'text-accent-orange',
  },
  AgeRestricted: {
    slug: 'agerestricted',
    token: '--color-accent-red',
    fillAlpha: 0.1,
    fillClass: 'bg-accent-red/10',
    labelClass: 'text-fg',
    iconClass: 'text-accent-red',
  },
} as const satisfies Record<string, StatusPill>

/** A status name the table knows about. */
export type PillStatus = keyof typeof STATUS_PILL_TOKENS

/**
 * Fallback for statuses outside the table (`Idle`, `Generating`, or anything a
 * future backend adds). Muted rather than invisible — an unknown status must
 * still render a readable pill instead of an unstyled bare word.
 */
export const NEUTRAL_PILL: StatusPill = {
  slug: 'unknown',
  token: '--color-fg-muted',
  fillAlpha: 0.1,
  fillClass: 'bg-fg-muted/10',
  labelClass: 'text-fg',
  iconClass: 'text-fg-muted',
}

/**
 * Resolve a status name to its pill contract.
 *
 * @param status - Status string as the API reported it.
 * @returns The table entry, or {@link NEUTRAL_PILL} when the status is unknown.
 */
export function resolveStatusPill(status: string): StatusPill {
  return (
    (STATUS_PILL_TOKENS as Record<string, StatusPill | undefined>)[status] ?? NEUTRAL_PILL
  )
}

/** Progress-bar fill tones (`PROGRESS_TONE`). `success` marks a finished row. */
export type ProgressTone = 'accent' | 'success'

/**
 * Fill class per progress tone (`PROGRESS_FILL_CLASSES`).
 *
 * Kept beside the pill table because AC-43.2 allows exactly one module to bind
 * a status hue to a class; `ProgressBar` reads its fill from here rather than
 * restating a palette literal.
 */
export const PROGRESS_FILL_CLASSES: Readonly<Record<ProgressTone, string>> = {
  accent: 'bg-accent',
  success: 'bg-accent-green',
}
