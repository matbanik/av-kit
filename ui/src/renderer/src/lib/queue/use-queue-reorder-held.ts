/**
 * `REORDER_HELD_HOOK` — the ONLY React binding over
 * `REORDER_SINGLE_FLIGHT_RULE`'s store (`reorder-single-flight.ts`).
 *
 * The store itself has no React import (`download-commands.ts` and
 * `convert-commands.ts` call `acquireQueueReorder` directly and must stay
 * framework-free), so the `useSyncExternalStore` binding lives here instead,
 * as its own tiny module — the standard split for this pattern: a
 * framework-free store plus a one-line React binding. `QueueCard` and
 * `QueueList` import THIS module, never `useSyncExternalStore` directly, so
 * there is exactly one subscription shape to reason about.
 */
import { useSyncExternalStore } from 'react'

import {
  isQueueReorderHeld,
  subscribeQueueReorder,
  type ReorderQueueKey,
} from './reorder-single-flight'

/**
 * Whether one queue's reorder gate is currently held, kept live via
 * `REORDER_SINGLE_FLIGHT_RULE`'s external-store pair.
 *
 * `getSnapshot` (`() => isQueueReorderHeld(key)`) returns a `boolean`, so it
 * is referentially stable by construction — a primitive compares equal to
 * itself across calls — and therefore cannot trigger React's "the result of
 * getSnapshot should be cached" infinite-render loop, which fires only for
 * a freshly-allocated object/array snapshot.
 *
 * Because `getSnapshot` and the subscription both read/observe the same
 * module-level registry the acquire path writes, a component that unmounts
 * and remounts re-subscribes to the LIVE gate state rather than to a fresh
 * `false` (AC-49.37) — there is no local `useState` initializer to reset.
 *
 * @param key - Which queue's gate to observe (`REORDER_QUEUE_KEYS`).
 * @returns `true` while the queue's reorder gate is held by some in-flight
 *   mutation (on any card, any entry point), `false` otherwise.
 */
export function useQueueReorderHeld(key: ReorderQueueKey): boolean {
  return useSyncExternalStore(
    (onStoreChange) => subscribeQueueReorder(key, onStoreChange),
    () => isQueueReorderHeld(key),
  )
}
