/**
 * MEU-67 Apply to image / Revert: the single renderer definitions of APPLY_ENABLED,
 * REVERT_VISIBLE's enabled rule, the confirm texts and FLATTEN_STATUS (Session 30 plan).
 */

/** BACKUP_DIR_DEFAULT_NAME (services/capture.py): the default backup folder inside the inbox. */
export const BACKUP_DIR_DEFAULT_NAME = '.avkit-backup'

/** FLATTEN_INPUTS: PNG flattens in place; CONVERTIBLE suffixes get a new PNG copy. */
export const FLATTEN_PNG_SUFFIX = '.png'
export const CONVERTIBLE_SUFFIXES = ['.jpg', '.jpeg', '.webp'] as const

export const APPLY_TITLES = {
  noMarks: 'Save marks first',
  dirty: 'Save annotations first',
  fileType: 'This file type cannot be flattened',
} as const

export const REVERT_DIRTY_TITLE = 'Save or discard unsaved marks first'

export type ControlState = { enabled: boolean; title: string | undefined }

/** Lowercased suffix of a path's file name ('' when it has none). */
export function shotSuffix(path: string): string {
  const name = basename(path)
  const dot = name.lastIndexOf('.')
  return dot > 0 ? name.slice(dot).toLowerCase() : ''
}

export function isConvertible(path: string): boolean {
  return (CONVERTIBLE_SUFFIXES as readonly string[]).includes(shotSuffix(path))
}

function isFlattenInput(path: string): boolean {
  return shotSuffix(path) === FLATTEN_PNG_SUFFIX || isConvertible(path)
}

/** Last path segment for either separator. */
export function basename(path: string): string {
  const parts = path.split(/[\\/]/)
  return parts[parts.length - 1] ?? path
}

/**
 * APPLY_ENABLED; a disabled button names the first unmet reason in order. SAVE_AND_FLATTEN
 * (MEU-104, D-693): with unsaved marks it counts the current marks and needs a possible save,
 * because accepting saves them first.
 */
export function applyState(input: {
  selected: boolean
  savedCount: number
  currentCount: number
  dirty: boolean
  canSave: boolean
  confirmOpen: boolean
  originalPath: string
}): ControlState {
  if (!input.selected) {
    return { enabled: false, title: undefined }
  }
  const title = input.dirty
    ? input.currentCount < 1
      ? APPLY_TITLES.noMarks
      : !input.canSave
        ? APPLY_TITLES.dirty
        : !isFlattenInput(input.originalPath)
          ? APPLY_TITLES.fileType
          : undefined
    : input.savedCount < 1
      ? APPLY_TITLES.noMarks
      : !isFlattenInput(input.originalPath)
        ? APPLY_TITLES.fileType
        : undefined
  return { enabled: title === undefined && !input.confirmOpen, title }
}

/** Revert's enabled rule; whether it renders at all is REVERT_VISIBLE (backup_path !== null). */
export function revertState(input: { dirty: boolean; confirmOpen: boolean }): ControlState {
  if (input.dirty) {
    return { enabled: false, title: REVERT_DIRTY_TITLE }
  }
  return { enabled: !input.confirmOpen, title: undefined }
}

/** FLATTEN_CONFIRM_TEXT for the three cases; `unsaved` names the current marks, saved first (D-693). */
export function flattenConfirmText(input: {
  displayName: string
  originalPath: string
  backupEnabled: boolean
  backupDir: string
  unsaved: boolean
}): string {
  const name = input.displayName
  const lead = input.unsaved ? 'Save the current marks, then bake them into' : 'Bake the saved marks into'
  if (isConvertible(input.originalPath)) {
    return `${lead} a new PNG copy of ${name}? ${name} itself stays unchanged.`
  }
  if (!input.backupEnabled) {
    return `${lead} ${name}? Backups are off, so this cannot be undone.`
  }
  const folder = input.backupDir.trim().length > 0 ? input.backupDir.trim() : 'the backup folder in the inbox'
  return `${lead} ${name}? The original is copied to ${folder} first.`
}

/** REVERT_CONFIRM_TEXT. */
export function revertConfirmText(displayName: string, backupPath: string): string {
  return `Replace ${displayName} with its newest backup (${basename(backupPath)})? The current image is overwritten.`
}

export type FlattenOutcome =
  | { kind: 'flatten'; backupBefore: string | null; backupAfter: string | null }
  | { kind: 'convert'; displayName: string }
  | { kind: 'revert'; backupPath: string }

/** FLATTEN_STATUS: a flatten wrote a backup exactly when the newest backup changed. */
export function flattenStatus(outcome: FlattenOutcome): string {
  switch (outcome.kind) {
    case 'flatten':
      return outcome.backupAfter !== null && outcome.backupAfter !== outcome.backupBefore
        ? `Flattened into image. Backup: ${outcome.backupAfter}`
        : 'Flattened into image (no backup).'
    case 'convert':
      return `Flattened into a new PNG copy: ${outcome.displayName}.`
    case 'revert':
      return `Restored from ${basename(outcome.backupPath)}.`
    default:
      return assertNever(outcome)
  }
}

export function assertNever(value: never): never {
  throw new Error(`unexpected value ${JSON.stringify(value)}`)
}
