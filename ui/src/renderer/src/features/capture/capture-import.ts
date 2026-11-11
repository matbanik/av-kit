/**
 * MEU-132 image import on the Capture page (09 §GUI image import).
 *
 * Pure helpers shared by the three entry points: a drop, the Import image… button and Ctrl+V.
 * Nothing here touches React or the DOM beyond reading an `EventTarget`. A path goes to
 * `port.importOne` and nowhere else: the result names files by `importDisplayName` only.
 */
import { ApiError } from '../../lib/api'
import type { BulkResult } from '../../lib/queue/run-bulk'

/** The paste outcome main answers on `capture-paste-image` (PASTE_MAIN). */
export type PasteOutcome = Awaited<ReturnType<NonNullable<Window['api']['pasteCaptureImage']>>>

/** One file to import: its path on disk and the name the toast may show. */
export type ImportEntry = { path: string; name: string }

/** The calls `importFiles` makes: one import per file, then one refetch. */
export type ImportPort = {
  importOne: (path: string) => Promise<unknown>
  refetch: () => Promise<unknown> | void
}

export const NOT_ON_DISK_REASON = 'not a file on disk'
export const NOT_AN_IMAGE_REASON = 'not an image av-kit can open (png, jpg, jpeg, webp)'
export const IMPORT_FAILED_REASON = 'the import could not be completed'
export const UNNAMED_FILE = '(unnamed file)'

/** IMPORT_TYPES (D-558): the suffixes MEU-129's import route accepts. */
export const IMPORT_EXTENSIONS: readonly string[] = ['png', 'jpg', 'jpeg', 'webp']

/** The error MEU-129's import route raises for its own fixed, path-free refusals (D-416). */
const INBOX_PATH_ERROR = 'InboxPathError'

function lastSegment(name: string): string {
  const cut = Math.max(name.lastIndexOf('/'), name.lastIndexOf('\\'))
  return cut < 0 ? name : name.slice(cut + 1)
}

/**
 * IMPORT_TYPES: the text after the basename's last `.`, lowercased, is one of the four. A dotfile
 * such as `.png` has no suffix, as Python's `Path.suffix` reads it.
 */
export function isImportableName(name: string): boolean {
  const base = lastSegment(name)
  const dot = base.lastIndexOf('.')
  if (dot <= 0) {
    return false
  }
  return IMPORT_EXTENSIONS.includes(base.slice(dot + 1).toLowerCase())
}

/**
 * IMPORT_NAME: the basename, with each control character and each lone surrogate replaced by
 * U+FFFD. It is the only form of a file's name the toast shows.
 */
export function importDisplayName(name: string): string {
  const base = lastSegment(name)
  let out = ''
  for (let i = 0; i < base.length; i += 1) {
    const unit = base.charCodeAt(i)
    if (unit <= 0x1f || unit === 0x7f) {
      out += '\uFFFD'
    } else if (unit >= 0xd800 && unit <= 0xdbff) {
      const next = i + 1 < base.length ? base.charCodeAt(i + 1) : 0
      if (next >= 0xdc00 && next <= 0xdfff) {
        out += base[i] + base[i + 1]
        i += 1
      } else {
        out += '\uFFFD'
      }
    } else if (unit >= 0xdc00 && unit <= 0xdfff) {
      out += '\uFFFD'
    } else {
      out += base[i]
    }
  }
  return out.length === 0 ? UNNAMED_FILE : out
}

/** Only MEU-129's own refusal shows its text; any other error might carry a path. */
function importFailureReason(error: unknown): string {
  if (error instanceof ApiError && error.status === 422 && error.code === INBOX_PATH_ERROR) {
    return error.message
  }
  return IMPORT_FAILED_REASON
}

function importMessage(result: Omit<BulkResult, 'message'>): string {
  const head = `Imported ${result.succeeded.length} of ${result.attempted.length}.`
  if (result.failed.length === 0) {
    return head
  }
  const list = result.failed.map((f) => `${f.id} - ${f.reason}`).join('; ')
  return `${head} ${result.failed.length} failed: ${list}`
}

/**
 * IMPORT_RUN (D-553): one entry at a time, in order. An entry with no path or no image suffix
 * fails with no call; the list is refetched once if any call was made.
 */
export async function importFiles(entries: readonly ImportEntry[], port: ImportPort): Promise<BulkResult> {
  const result: Omit<BulkResult, 'message'> = { attempted: [], succeeded: [], failed: [] }
  let called = false
  for (const entry of entries) {
    const name = importDisplayName(entry.name)
    result.attempted.push(name)
    if (entry.path.length === 0) {
      result.failed.push({ id: name, reason: NOT_ON_DISK_REASON })
      continue
    }
    if (!isImportableName(entry.path)) {
      result.failed.push({ id: name, reason: NOT_AN_IMAGE_REASON })
      continue
    }
    called = true
    try {
      await port.importOne(entry.path)
      result.succeeded.push(name)
    } catch (error: unknown) {
      result.failed.push({ id: name, reason: importFailureReason(error) })
    }
  }
  if (called) {
    await port.refetch()
  }
  return { ...result, message: importMessage(result) }
}

const TEXT_INPUT_TYPES = new Set(['', 'text', 'search', 'url', 'tel', 'email', 'password', 'number'])

/** PASTE_KEY: a text field or an editable element keeps its native paste. */
export function isEditableTarget(target: EventTarget | null): boolean {
  if (target === null || typeof (target as Element).tagName !== 'string') {
    return false
  }
  const element = target as HTMLElement
  if (element.tagName === 'TEXTAREA') {
    return true
  }
  if (element.tagName === 'INPUT') {
    return TEXT_INPUT_TYPES.has((element.getAttribute('type') ?? '').toLowerCase())
  }
  // jsdom implements neither `isContentEditable` nor the `contentEditable` setter, so the
  // property and the attribute are read as well; a browser answers through the first check.
  if (element.isContentEditable === true) {
    return true
  }
  const property = String(element.contentEditable).toLowerCase()
  if (property === 'true' || property === 'plaintext-only') {
    return true
  }
  const editable = element.getAttribute('contenteditable')
  return editable !== null && editable.toLowerCase() !== 'false'
}

const PASTE_FAILED_TEXT = 'The pasted image could not be saved to the inbox.'

/** PASTE_MESSAGES: the one-item note a paste shows, or `null` for `busy`. */
export function pasteToastResult(outcome: PasteOutcome): BulkResult | null {
  const one = (message: string, ok: boolean, name = 'clipboard image'): BulkResult => ({
    attempted: [name],
    succeeded: ok ? [name] : [],
    failed: ok ? [] : [{ id: name, reason: message }],
    message,
  })
  switch (outcome.kind) {
    case 'saved': {
      const name = importDisplayName(outcome.name)
      return outcome.registered
        ? one(`Pasted as ${name}.`, true, name)
        : one(`Pasted as ${name}, but the library did not record it.`, true, name)
    }
    case 'empty':
      return one('Nothing to paste: the clipboard holds no image.', false)
    case 'blocked':
      return outcome.reason === 'black'
        ? one('The pasted image is entirely black, so nothing was saved.', false)
        : one('The pasted image has no pixels, so nothing was saved.', false)
    case 'not-ready':
      return one("The inbox isn't ready yet, so nothing was saved. Try again in a moment.", false)
    case 'busy':
      return null
    default:
      return one(PASTE_FAILED_TEXT, false)
  }
}
