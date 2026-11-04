/**
 * FILMSTRIP_LABEL_RULE (Phase 11 CP4): the visible filmstrip name drops a leading ISO date
 * (`YYYY-MM-DD` followed by a space or underscore, as in the picker's TIMESTAMP_FORMAT), and
 * the time line comes from the carried `created_at`. The full `display_name` is always kept
 * so callers can render it accessibly.
 */
const DATE_PREFIX = /^\d{4}-\d{2}-\d{2}[ _]/

export type FilmstripLabel = {
  /** Visible name; the full name when stripping the date would leave nothing. */
  name: string
  /** Local `HH:MM:SS` of `created_at`, or '' when the timestamp does not parse. */
  time: string
  /** The unmodified `display_name`. */
  full: string
}

function pad(value: number): string {
  return String(value).padStart(2, '0')
}

/** Derive the filmstrip row text for one capture from fields the catalog already carries. */
export function filmstripLabel(displayName: string, createdAt: string): FilmstripLabel {
  const stripped = displayName.replace(DATE_PREFIX, '')
  const name = stripped.length > 0 ? stripped : displayName
  const date = new Date(createdAt)
  const time = Number.isNaN(date.getTime())
    ? ''
    : `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
  return { name, time, full: displayName }
}
