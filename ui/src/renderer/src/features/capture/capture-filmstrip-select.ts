/**
 * rangeBetween (MEU-89): the inclusive slice of `orderedIds` between `a` and `b`, in
 * `orderedIds` order whichever comes first. An unknown `b` gives `[]`; an unknown `a` gives `[b]`.
 */
export function rangeBetween(orderedIds: readonly string[], a: string, b: string): string[] {
  const end = orderedIds.indexOf(b)
  if (end === -1) {
    return []
  }
  const start = orderedIds.indexOf(a)
  if (start === -1) {
    return [b]
  }
  return orderedIds.slice(Math.min(start, end), Math.max(start, end) + 1)
}

/**
 * toggleSelection (D-25): what a filmstrip checkbox does. It adds `id` when absent and removes it
 * when present, returning the ids in `orderedIds` order. An id not in `orderedIds` changes nothing.
 */
export function toggleSelection(orderedIds: readonly string[], selected: readonly string[], id: string): string[] {
  if (!orderedIds.includes(id)) {
    return [...selected]
  }
  const next = new Set(selected)
  if (next.has(id)) {
    next.delete(id)
  } else {
    next.add(id)
  }
  return orderedIds.filter((candidate) => next.has(candidate))
}
