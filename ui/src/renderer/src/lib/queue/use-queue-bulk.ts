/**
 * The whole bulk-selection behaviour of a queue page, in one place.
 *
 * The converter and the downloader run the same model over different endpoints,
 * and `BULK_CONTROL_E2E_OBLIGATION` requires every bulk control to work on BOTH
 * pages — so the logic lives here rather than being written twice. A second copy
 * is where the two pages would quietly diverge: one would clear its selection
 * after a Retry and the other would not, and only one of them would have a test
 * that noticed.
 *
 * Three rules are enforced here rather than at the call sites:
 *  - the selection is derived from the FILTERED list the page renders, so a bulk
 *    action can never reach a row the user cannot see (`SELECTION_MODEL`);
 *  - every fan-out goes through `runBulk`, which owns `CLEAR_FINISHED_SEMANTICS`
 *    — snapshot once, continue on failure, reconcile exactly once;
 *  - every completed bulk action releases the selection (`SELECTION_MODEL`),
 *    and each one waits for its own reconcile first, so the ticked rows are let
 *    go only once the list on screen is the one the server actually holds;
 *  - the per-id command handed to a fan-out is the BARE request, never the
 *    reconciling one — `runBulk` refetches once at the end, so a command that
 *    invalidated per row would interleave N redundant refetches between the
 *    requests and re-render the queue mid-run.
 */
import { useCallback, useMemo, useState, type KeyboardEvent } from 'react'

import { bulkReorder, type BulkReorderEdge } from './bulk-reorder'
import { acquireQueueReorder, type ReorderQueueKey } from './reorder-single-flight'
import { clearFinished, runBulk, type BulkResult } from './run-bulk'
import {
  isSelectAllShortcut,
  useQueueSelection,
  type QueueSelection,
  type SelectionModifiers,
} from './use-queue-selection'

/** The direction vocabulary both queues' reorder commands share. */
export type QueueReorderDirection = 'up' | 'down' | 'top' | 'bottom'

/** The minimum a wire row must expose for the bulk model. */
export type QueueBulkItem = {
  /** The row's id. */
  id: string
  /** The row's status, as the API reported it. */
  status: string
}

export type QueueBulkOptions = {
  /** The rows as rendered — already filtered — in queue order. */
  items: readonly QueueBulkItem[]
  /**
   * Which queue's reorder gate the fold takes (`REORDER_SINGLE_FLIGHT_RULE`).
   *
   * Required, not optional: a bulk fold is the longest permutation mutation on
   * the page — N sequential requests over one snapshot — so it is precisely the
   * one a concurrent drag would interleave with. Defaulting it would let a page
   * silently opt out of the gate the drag handle is already respecting.
   */
  queueKey: ReorderQueueKey
  /** The statuses this page allows a retry from. */
  requeueableStatuses: readonly string[]
  /** The page's busy/error wrapper, so bulk runs disable the controls too. */
  run: (action: () => Promise<unknown>) => void
  /** Re-queue one row. */
  retry: (id: string) => Promise<unknown>
  /** Remove one queue record. The media file stays on disk. */
  remove: (id: string) => Promise<unknown>
  /** Issue one reorder request over the order the server is believed to hold. */
  reorder: (
    ids: string[],
    selectedId: string,
    direction: QueueReorderDirection,
  ) => Promise<unknown>
  /** Build the `REORDER_WIRE_CONTRACT` body — the page's `buildReorderBody`. */
  buildBody: (
    ids: string[],
    selectedId: string,
    direction: QueueReorderDirection,
  ) => { job_ids: string[] }
  /** Reconcile the list against the server. */
  refetch: () => Promise<unknown>
}

export type QueueBulk = {
  /** The selection itself, for the header, the rows and the bar. */
  selection: QueueSelection
  /** The statuses of the selected rows, in render order — the bar's input. */
  selectedStatuses: string[]
  /** The last run's report, or `null`. */
  note: BulkResult | null
  /** Clear the report. */
  dismissNote: () => void
  /** The verb-labelled confirm text for the pending removal (`USER_LOCKS`). */
  removeConfirmLabel: string
  /** Forward a row checkbox's change into the selection. */
  onSelectChange: (id: string, checked: boolean, modifiers: SelectionModifiers) => void
  /** Select or clear the whole filtered list. */
  onToggleAll: (checked: boolean) => void
  /** Ctrl/Cmd+A, scoped to the queue region rather than the document. */
  onKeyDown: (event: KeyboardEvent<HTMLElement>) => void
  /** Re-queue every selected row the requeueable set admits. */
  retrySelected: () => void
  /** Move the selection to one end of the queue. */
  moveSelected: (edge: BulkReorderEdge) => void
  /** Remove every selected row. Call only behind the page's confirm. */
  removeSelected: () => void
  /** Sweep the finished rows and report the outcome. */
  clearFinishedNow: () => void
}

/**
 * Wire a queue page's selection, bulk bar and result note.
 *
 * @param options - The page's rows, endpoints and busy wrapper.
 * @returns Everything the page needs to render and drive the bulk controls.
 */
export function useQueueBulk(options: QueueBulkOptions): QueueBulk {
  const { items, queueKey, requeueableStatuses, run, retry, remove, reorder, buildBody, refetch } =
    options
  const selection = useQueueSelection(items)
  const [note, setNote] = useState<BulkResult | null>(null)

  const { selectedIds, clear } = selection

  const selectedStatuses = useMemo(
    () =>
      selectedIds.map((id) => items.find((item) => item.id === id)?.status ?? '').filter(
        (status) => status !== '',
      ),
    [items, selectedIds],
  )

  const order = useMemo(() => items.map((item) => item.id), [items])

  const dismissNote = useCallback(() => {
    setNote(null)
  }, [])

  const retrySelected = useCallback(() => {
    // Only the rows the page's own set admits are sent. The others are not
    // failures — they were never eligible — so they are filtered out rather
    // than attempted and reported as errors the user cannot act on.
    const eligible = selectedIds.filter((id) => {
      const status = items.find((item) => item.id === id)?.status
      return status !== undefined && requeueableStatuses.includes(status)
    })
    run(async () => {
      setNote(await runBulk(eligible, retry, { verb: 'Retried', refetch }))
      clear()
    })
  }, [clear, items, refetch, requeueableStatuses, retry, run, selectedIds])

  const moveSelected = useCallback(
    (edge: BulkReorderEdge) => {
      /*
        Taken synchronously, before `run` and before `order` is committed to a
        request: the gate's job is to keep two permutation mutations from being
        computed against the same pre-move order, and an acquire that waited for
        the async body would already be too late. A refused acquire means another
        reorder is mid-flight, so this fold is dropped outright rather than
        queued — a queued fold would apply an edge to an order the user has since
        changed.
      */
      const release = acquireQueueReorder(queueKey)
      if (release === null) {
        return
      }
      run(async () => {
        try {
          const result = await bulkReorder(order, selectedIds, edge, { reorder, buildBody })
          setNote(result.failed.length === 0 ? null : result)
          /*
            Reconcile, then release — unconditionally. `SELECTION_MODEL` says
            the selection is cleared AFTER A BULK ACTION COMPLETES, and a move
            that moved nothing (every request rejected, or the rows were already
            at that edge) is still a completed bulk action. An earlier version
            cleared only when the reconciled order differed from the order at
            click time; that made a frozen rule depend on react-query render
            timing, and it left a stale selection live after a total failure —
            exactly the state the next fold must not run over.
          */
          await refetch()
          clear()
        } finally {
          /*
            `finally`, so one rejected PUT inside the fan-out cannot leave the
            queue's gate held forever — a leaked gate would disable the drag
            handle and all four kebab reorder items for the rest of the session.
            It runs after the reconcile, so the gate is not released until the
            list on screen is the one the server holds.
          */
          release()
        }
      })
    },
    [buildBody, clear, order, queueKey, refetch, reorder, run, selectedIds],
  )

  const removeSelected = useCallback(() => {
    run(async () => {
      setNote(await runBulk(selectedIds, remove, { verb: 'Removed', refetch }))
      clear()
    })
  }, [clear, refetch, remove, run, selectedIds])

  const clearFinishedNow = useCallback(() => {
    run(async () => {
      setNote(await clearFinished(items, remove, refetch))
    })
  }, [items, refetch, remove, run])

  const onSelectChange = useCallback(
    (id: string, checked: boolean, modifiers: SelectionModifiers) => {
      selection.toggle(id, checked, modifiers)
    },
    [selection],
  )

  const onToggleAll = useCallback(
    (checked: boolean) => {
      selection.selectAll(checked)
    },
    [selection],
  )

  const onKeyDown = useCallback(
    (event: KeyboardEvent<HTMLElement>) => {
      if (!isSelectAllShortcut(event)) {
        return
      }
      // Scoped to the queue region, never the document: a global Ctrl+A would
      // take the chord away from every text field on the page.
      event.preventDefault()
      selection.selectAll(true)
    },
    [selection],
  )

  const count = selectedIds.length
  const removeConfirmLabel = `Remove ${String(count)} ${count === 1 ? 'item' : 'items'}`

  return {
    selection,
    selectedStatuses,
    note,
    dismissNote,
    removeConfirmLabel,
    onSelectChange,
    onToggleAll,
    onKeyDown,
    retrySelected,
    moveSelected,
    removeSelected,
    clearFinishedNow,
  }
}
