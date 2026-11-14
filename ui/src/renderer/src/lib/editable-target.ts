/** FIELD_GUARD (MEU-143, D-751): one test for an editable target, shared by the paste key and the shortcut handler. */
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
