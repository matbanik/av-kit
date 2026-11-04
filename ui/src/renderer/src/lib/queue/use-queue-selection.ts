/**
 * Client-side row selection for the queue pages (`SELECTION_MODEL`).
 *
 * The selection is the one piece of queue state the client owns outright — the
 * backend has no concept of a "ticked" row — which makes two failure modes
 * cheap to write and expensive to ship: acting on an id the server has already
 * dropped, and selecting rows a filter is hiding. Both are closed here rather
 * than at every call site: the hook is given the SAME list the page renders
 * (already filtered), it derives `selectedIds` from that list on every render,
 * and it prunes anything the list no longer carries.
 *
 * `selectedIds` is therefore always in RENDER order, never in click order.
 * `BULK_REORDER_ALGORITHM` folds its requests in render order, so a stale click
 * sequence would move rows to the wrong place.
 */
import { useCallback, useMemo, useRef, useState } from 'react'

/** The modifier state a click carried, forwarded from the DOM event. */
export type SelectionModifiers = {
  /** Whether Shift was held — the range-select chord. */
  shiftKey: boolean
}

/** The minimum a row must expose to take part in a selection. */
export type SelectableItem = {
  /** The row's stable id. */
  id: string
}

/** The selection API a queue page drives its bulk controls from. */
export type QueueSelection = {
  /** The selected ids, in render order, pruned to the current list. */
  selectedIds: string[]
  /** How many rows are selected. */
  count: number
  /** Whether every row in the (filtered) list is selected. Never true when empty. */
  allSelected: boolean
  /** Whether some — but not all — rows are selected (the indeterminate state). */
  someSelected: boolean
  /** Whether one id is currently selected. */
  isSelected: (id: string) => boolean
  /** Toggle one row; with `shiftKey` this extends the range from the anchor. */
  toggle: (id: string, checked: boolean, modifiers?: SelectionModifiers) => void
  /** Select or clear the whole (filtered) list. */
  selectAll: (checked: boolean) => void
  /** Drop the selection entirely — what a completed bulk action does. */
  clear: () => void
}

/** The shape `isSelectAllShortcut` needs from a keyboard event. */
export type SelectAllChord = {
  /** The event's `key`. */
  key: string
  /** Whether Ctrl was held. */
  ctrlKey: boolean
  /** Whether Meta (⌘) was held. */
  metaKey: boolean
}

/**
 * Whether a keyboard event is the select-all chord.
 *
 * Both platform chords are accepted because the app ships on Windows and macOS
 * from one bundle; the key comparison is case-insensitive because Shift+Ctrl+A
 * reports `A`.
 *
 * @param event - The keyboard event's key and modifier state.
 * @returns `true` for Ctrl+A or Cmd+A, `false` otherwise.
 */
export function isSelectAllShortcut(event: SelectAllChord): boolean {
  return event.key.toLowerCase() === 'a' && (event.ctrlKey || event.metaKey)
}

/**
 * Whether two id sets hold exactly the same members.
 *
 * Membership, deliberately not order: a queue that has merely been rearranged
 * is the same envelope, and rearranging must never cost the user their ticks.
 *
 * @param a - One id set.
 * @param b - The other id set.
 * @returns `true` when both hold the same ids, in any order.
 */
function sameMembers(a: ReadonlySet<string>, b: ReadonlySet<string>): boolean {
  if (a.size !== b.size) {
    return false
  }
  for (const id of a) {
    if (!b.has(id)) {
      return false
    }
  }
  return true
}

/**
 * Track which rows of a queue list are selected.
 *
 * @param items - The rows as rendered, already filtered. Selected ids not in
 *        this list are pruned rather than acted on.
 * @returns The selection API; see {@link QueueSelection}.
 */
export function useQueueSelection(items: readonly SelectableItem[]): QueueSelection {
  const [selected, setSelected] = useState<ReadonlySet<string>>(() => new Set<string>())
  const anchorRef = useRef<string | null>(null)

  const order = useMemo(() => items.map((item) => item.id), [items])
  const envelope = useMemo(() => new Set<string>(order), [order])
  const [knownEnvelope, setKnownEnvelope] = useState<ReadonlySet<string>>(envelope)

  /*
    Prune the BACKING SET, not just the projection, and do it during render
    rather than in an effect.

    Filtering only the derived `selectedIds` would leave a vanished id sitting
    in state: if the row came back on a later refetch — a retried job, a paused
    processor resuming, a filter the user widened again — it would silently
    return already ticked, and the next bulk action would act on a row the user
    never selected. The anchor has the same problem in a quieter form: an
    anchor the list has dropped makes every subsequent Shift+click degrade to a
    plain toggle, because the range has no live end to run from, and nothing
    ever replaces it (a Shift+click deliberately does not move the anchor).

    The comparison is membership-only, so a pure reorder preserves BOTH the
    selection and the anchor. Setting state during render is React's documented
    way to derive state from changed inputs; an effect would leave one rendered
    frame in which a dropped id is still selectable, and a bulk action fired in
    that frame would issue a request for a row the server has already dropped.
  */
  if (!sameMembers(knownEnvelope, envelope)) {
    setKnownEnvelope(envelope)
    setSelected((current) => {
      const next = new Set<string>()
      for (const id of current) {
        if (envelope.has(id)) {
          next.add(id)
        }
      }
      return next.size === current.size ? current : next
    })
    if (anchorRef.current !== null && !envelope.has(anchorRef.current)) {
      anchorRef.current = null
    }
  }


  /*
    Derived, never stored: pruning in an effect would leave one render in which
    a vanished id is still selectable — and a bulk action fired in that window
    would issue a request for a row the server has already dropped.
  */
  const selectedIds = useMemo(
    () => order.filter((id) => selected.has(id)),
    [order, selected],
  )

  const isSelected = useCallback(
    (id: string) => selected.has(id) && order.includes(id),
    [order, selected],
  )

  const toggle = useCallback(
    (id: string, checked: boolean, modifiers?: SelectionModifiers) => {
      const anchor = anchorRef.current
      setSelected((current) => {
        const next = new Set<string>(order.filter((rowId) => current.has(rowId)))
        const index = order.indexOf(id)
        const anchorIndex = anchor === null ? -1 : order.indexOf(anchor)

        // Shift+click extends the INCLUSIVE range from the last anchor, in
        // render order. With no anchor — or an anchor the list has dropped —
        // it degrades to a plain toggle rather than selecting nothing.
        if (
          modifiers?.shiftKey === true &&
          checked &&
          index >= 0 &&
          anchorIndex >= 0
        ) {
          const from = Math.min(index, anchorIndex)
          const to = Math.max(index, anchorIndex)
          for (const rowId of order.slice(from, to + 1)) {
            next.add(rowId)
          }
          return next
        }

        if (checked) {
          next.add(id)
        } else {
          next.delete(id)
        }
        return next
      })

      // The anchor is the last row the user acted on directly, so a follow-up
      // Shift+click ranges from there. A range select does not move it.
      if (modifiers?.shiftKey !== true || anchor === null) {
        anchorRef.current = id
      }
    },
    [order],
  )

  const selectAll = useCallback(
    (checked: boolean) => {
      setSelected(() => (checked ? new Set<string>(order) : new Set<string>()))
      anchorRef.current = checked && order.length > 0 ? order[order.length - 1] : null
    },
    [order],
  )

  const clear = useCallback(() => {
    setSelected(new Set<string>())
    anchorRef.current = null
  }, [])

  const count = selectedIds.length
  const allSelected = order.length > 0 && count === order.length
  const someSelected = count > 0 && count < order.length

  return {
    selectedIds,
    count,
    allSelected,
    someSelected,
    isSelected,
    toggle,
    selectAll,
    clear,
  }
}
