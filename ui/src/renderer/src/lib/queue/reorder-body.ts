/**
 * `REORDER_BODY_MODULE` — sole owner of the queue-reorder permutation
 * builders shared by the downloader and converter pages.
 *
 * `buildReorderBody` used to be duplicated byte-for-byte in
 * `convert-controls.ts` and `download-controls.ts`. Drag support needs a
 * third variant that resolves an arbitrary drop target rather than one of
 * the four fixed directions, and tripling a triplicate is the defect this
 * module removes: every permutation builder now lives in exactly one place,
 * and both controls modules re-export `buildReorderBody` from here
 * (reference identity, AC-49.3) instead of declaring their own copy.
 *
 * Neither builder issues a network request or reads component state — both
 * are pure functions over the caller-supplied id list, per
 * `REORDER_WIRE_CONTRACT`'s requirement that every reorder PUT carry a
 * complete permutation (`{ job_ids: string[] }`), never a relative
 * `{ id, direction }` nudge.
 */

/** The four fixed-direction moves the kebab menu and Alt+Arrow issue. */
export type ReorderDirection = 'up' | 'down' | 'top' | 'bottom'

/**
 * Build the `REORDER_WIRE_CONTRACT` body for a fixed-direction move
 * (AC-49.4). Moved verbatim from `convert-controls.ts:112` /
 * `download-controls.ts:104` — same signature, same behaviour, including the
 * `Math.max`/`Math.min` clamps at the two edges and the defensive unchanged
 * copy returned when `selectedId` is not present in `ids`.
 *
 * @param ids - The full ordered list of job ids currently in the queue.
 * @param selectedId - The id being moved.
 * @param direction - Which way to move it.
 * @returns The complete permutation to send as the PUT body. When
 *   `selectedId` is not present in `ids`, an unchanged COPY of `ids` — never
 *   the same array reference, so a caller can never mutate the input by
 *   mutating the result.
 */
export function buildReorderBody(
  ids: string[],
  selectedId: string,
  direction: ReorderDirection,
): { job_ids: string[] } {
  const index = ids.indexOf(selectedId)
  if (index < 0) {
    return { job_ids: [...ids] }
  }
  const next = [...ids]
  const [row] = next.splice(index, 1)
  if (direction === 'up') {
    next.splice(Math.max(0, index - 1), 0, row)
  } else if (direction === 'down') {
    next.splice(Math.min(next.length, index + 1), 0, row)
  } else if (direction === 'top') {
    next.unshift(row)
  } else {
    next.push(row)
  }
  return { job_ids: next }
}

/**
 * Build the `REORDER_WIRE_CONTRACT` body for an arbitrary drop target
 * (`MOVE_TO_INDEX_CONTRACT`, AC-49.5). This mirrors dnd-kit's own sortable
 * `arrayMove(items, oldIndex, newIndex)` pattern: both indices are resolved
 * against the PRE-MOVE array — `oldIndex = ids.indexOf(movedId)` and
 * `targetIndex` is the FINAL index the moved row must occupy in the result —
 * and handed to a remove-then-reinsert unchanged. `targetIndex` is not read
 * as an index into the post-removal array in isolation; inserting the
 * removed row at that index into the (necessarily one-shorter) remaining
 * array is exactly what leaves it at `targetIndex` in the final, full-length
 * result.
 *
 * Worked examples (mandatory unit assertions per `MOVE_TO_INDEX_CONTRACT`):
 *  - `['A','B','C','D']`, move `A` to index 2 → `['B','C','A','D']` — NOT
 *    `['B','A','C','D']`, the post-removal-index bug this contract forbids.
 *  - `['A','B','C','D']`, move `D` to index 1 → `['A','D','B','C']`.
 *  - `['A','B','C']`, move `A` to index 1 → `['B','A','C']`.
 *
 * @param ids - The full ordered list of job ids currently in the queue, read
 *   BEFORE the move (dnd-kit hands sortable consumers the pre-drag order).
 * @param movedId - The id of the row being dropped.
 * @param targetIndex - The final index `movedId` must occupy in the result.
 *   Clamped to `[0, ids.length - 1]` — a drop target computed from a stale
 *   or out-of-range position neither throws nor drops the row. A non-finite
 *   value (e.g. `NaN`) is treated as `0` for the same reason: per
 *   `MOVE_TO_INDEX_CONTRACT` this function never throws on caller input.
 * @returns The complete permutation to send as the PUT body. When
 *   `movedId` is not present in `ids`, an unchanged COPY of `ids` — the same
 *   defensive shape `buildReorderBody` uses for an unknown `selectedId`.
 *   When `targetIndex` already equals `movedId`'s current index, the
 *   returned permutation is the identity permutation; per
 *   `MOVE_TO_INDEX_CONTRACT` the caller must not issue a PUT for it.
 */
export function buildReorderBodyToIndex(
  ids: string[],
  movedId: string,
  targetIndex: number,
): { job_ids: string[] } {
  const oldIndex = ids.indexOf(movedId)
  if (oldIndex < 0) {
    return { job_ids: [...ids] }
  }
  const safeTarget = Number.isFinite(targetIndex) ? targetIndex : 0
  const clampedIndex = Math.max(0, Math.min(ids.length - 1, safeTarget))
  const next = [...ids]
  const [row] = next.splice(oldIndex, 1)
  next.splice(clampedIndex, 0, row)
  return { job_ids: next }
}

/**
 * Whether a permutation leaves the queue in exactly the order it was already in.
 *
 * `MOVE_TO_INDEX_CONTRACT` makes the identity permutation a legitimate RESULT —
 * a drop on the row's own position produces it — but not a legitimate REQUEST.
 * Sending it would put a PUT on the wire that cannot change anything and can
 * only lose a race with the next real reorder, so both index commands ask this
 * before they call the API.
 *
 * @param before - The order the queue is currently believed to hold.
 * @param after - The permutation that was built from it.
 * @returns Whether the two are the same sequence of ids.
 */
export function isSameOrder(before: readonly string[], after: readonly string[]): boolean {
  return before.length === after.length && before.every((id, index) => id === after[index])
}
