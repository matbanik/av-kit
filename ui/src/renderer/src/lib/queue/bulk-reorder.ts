/**
 * Bulk move-to-top / move-to-bottom (`BULK_REORDER_ALGORITHM`).
 *
 * `REORDER_WIRE_CONTRACT` makes the reorder endpoint take an ABSOLUTE
 * permutation — `{ job_ids: [...] }`, the whole queue — not a relative
 * `{ id, direction }` nudge. Combined with `BULK_ENDPOINT_POLICY` (no
 * `POST /{queue}/bulk` exists, and none may be invented) that means a bulk move
 * is N sequential PUTs, and request k is only correct if it is folded from the
 * order the server accepted at k-1. Folding every request from the stale
 * initial order would make each step undo the one before it.
 *
 * Two consequences fall out and are load-bearing:
 *  - the requests are strictly sequential, never overlapped — a concurrent PUT
 *    would be computed from an order the server has not acknowledged;
 *  - a REJECTED step does not advance the fold, so the next request is built
 *    from the last order the server actually accepted.
 *
 * The permutation itself is always built by the caller's `buildBody` — the same
 * function the single-row move uses — so the bulk path can never drift from the
 * wire shape the single-row path proved.
 */
import { runBulk, type BulkResult } from './run-bulk'

/** Which end of the queue the selection is being moved to. */
export type BulkReorderEdge = 'top' | 'bottom'

/** The two collaborators a bulk move needs from its page. */
export type BulkReorderDeps = {
  /**
   * Issues one reorder request for `selectedId` against `ids`, the order the
   * server is currently believed to hold. Rejects to report a failure.
   */
  reorder: (
    ids: string[],
    selectedId: string,
    direction: 'up' | 'down' | 'top' | 'bottom',
  ) => Promise<unknown>
  /** Builds the `REORDER_WIRE_CONTRACT` body — the shared `buildReorderBody`. */
  buildBody: (
    ids: string[],
    selectedId: string,
    direction: 'up' | 'down' | 'top' | 'bottom',
  ) => { job_ids: string[] }
}

/**
 * Move every selected row to one end of the queue, preserving relative order.
 *
 * The selection is walked in REVERSED render order for `top` and in render
 * order for `bottom`. Either way the last row moved ends up outermost, which is
 * what leaves the moved block in the same relative order the user saw it in.
 *
 * @param order - The queue as currently rendered, in order.
 * @param selectedIds - The selected ids; re-derived into render order here, so
 *        a click-ordered array cannot scramble the fold.
 * @param edge - Which end to move the selection to.
 * @param deps - The page's reorder command and body builder.
 * @returns The per-id outcome and the G35 message. Never rejects.
 */
export async function bulkReorder(
  order: readonly string[],
  selectedIds: readonly string[],
  edge: BulkReorderEdge,
  deps: BulkReorderDeps,
): Promise<BulkResult> {
  const selection = order.filter((id) => selectedIds.includes(id))
  const walk = edge === 'top' ? [...selection].reverse() : selection

  // The fold. Advanced ONLY by a resolved request, so a rejection leaves the
  // next step folding from the last order the server accepted.
  let accepted = [...order]

  return runBulk(
    walk,
    async (id) => {
      const handed = accepted
      await deps.reorder(handed, id, edge)
      accepted = deps.buildBody(handed, id, edge).job_ids
    },
    // The fold is the whole algorithm: step k is built from the order step
    // k-1 produced, so these requests cannot be issued together.
    { verb: 'Moved', dependent: true },
  )
}
