/**
 * `REORDER_SINGLE_FLIGHT_RULE` — the primitive half.
 *
 * Every queue permutation mutation (kebab Move up/down/top/bottom, Alt+Arrow,
 * drag-drop, and the whole bulk-reorder fold) passes through ONE synchronous
 * gate before it reads the current order or builds a `REORDER_WIRE_CONTRACT`
 * body. Every reorder PUT is an ABSOLUTE permutation computed from the order
 * the caller can see, so two overlapping mutations both compute a valid
 * permutation from the same pre-mutation order and whichever response lands
 * last silently overwrites the other. The gate exists to make the second of
 * two synchronous calls lose immediately, in the SAME tick — a `useState`
 * mirror is written asynchronously, so two calls in one tick would both read
 * `false` and both proceed, which is exactly the race this module closes.
 *
 * This module has NO React import. `download-commands.ts` and
 * `convert-commands.ts` are plain-TS command modules with no React import of
 * their own, and they call {@link acquireQueueReorder} directly — putting
 * `useSyncExternalStore` here would drag React into the command layer purely
 * so a component could subscribe. The React binding is `REORDER_HELD_HOOK`
 * (`use-queue-reorder-held.ts`), a separate, tiny module.
 *
 * LIFETIME: the queue registry below is MODULE-LEVEL, not a per-page
 * `useRef`. A route unmount does not cancel an in-flight PUT, so a ref-held
 * gate would be destroyed on navigation while the request it was guarding is
 * still on the wire — the remounted page would then immediately grant a
 * second permutation computed from a pre-mutation order, the exact
 * last-write-wins overwrite this rule exists to prevent.
 */

/**
 * The key space of the module-level reorder registry — `REORDER_QUEUE_KEYS`.
 * The two queues that mount `QueueList`: the downloader and converter pages.
 * Transcript and TTS are out of scope for drag/reorder.
 */
export type ReorderQueueKey = 'download' | 'convert'

/** The concrete values of {@link ReorderQueueKey}, for runtime validation. */
const REORDER_QUEUE_KEYS: readonly ReorderQueueKey[] = ['download', 'convert']

/** A listener notified synchronously on every acquire and release. */
type SingleFlightListener = () => void

/**
 * A single independent single-flight gate: `tryAcquire`/`release`/`held`
 * over a closure-captured plain boolean.
 */
export type SingleFlightGate = {
  /**
   * Attempt to take the gate.
   *
   * @returns `true` and takes the gate when it was free; `false` — and
   *   leaves the gate exactly as it was — when it was already held.
   */
  tryAcquire(): boolean
  /**
   * Free the gate. A no-op — not an error, and not a credit banked for a
   * future double-release — when the gate is not currently held.
   */
  release(): void
  /** Whether the gate is currently held. Read synchronously, never cached. */
  readonly held: boolean
}

/**
 * Create one independent single-flight gate.
 *
 * The gate is a closure over a plain `boolean`, deliberately NOT React
 * state: two synchronous calls to `tryAcquire()` in the same tick — the
 * exact shape of a kebab click racing a keyboard shortcut, or a drag-drop
 * racing the bulk-reorder fold — must not both succeed. A `useState` setter
 * would still read the pre-update value on the second call in the same
 * tick, since the state update is not applied until the next render; a
 * plain boolean mutated synchronously has no such window. Separate calls to
 * `createSingleFlight()` are fully independent — each closes over its own
 * boolean.
 *
 * @returns A new, unheld {@link SingleFlightGate}.
 */
export function createSingleFlight(): SingleFlightGate {
  let heldFlag = false

  return {
    tryAcquire(): boolean {
      if (heldFlag) {
        return false
      }
      heldFlag = true
      return true
    },
    release(): void {
      heldFlag = false
    },
    get held(): boolean {
      return heldFlag
    },
  }
}

/**
 * Validate that `key` is one of {@link REORDER_QUEUE_KEYS}.
 *
 * The type system enforces this for TypeScript call sites, but every export
 * below is also reachable from plain-JS command modules and test doubles, so
 * a malformed key fails loudly here rather than silently fabricating a new
 * registry entry that no page will ever observe.
 *
 * @param key - The candidate queue key.
 * @throws {RangeError} When `key` is not a recognised `ReorderQueueKey`.
 */
function assertValidQueueKey(key: ReorderQueueKey): void {
  if (!REORDER_QUEUE_KEYS.includes(key)) {
    throw new RangeError(
      `Unknown reorder queue key: ${JSON.stringify(key)}. Expected one of ${REORDER_QUEUE_KEYS.join(', ')}.`,
    )
  }
}

/** One registry entry: the queue's gate plus its reactive-store listeners. */
type QueueRegistryEntry = {
  gate: SingleFlightGate
  listeners: Set<SingleFlightListener>
}

/**
 * The module-level registry, one {@link SingleFlightGate} per
 * `ReorderQueueKey`. Module scope (not component scope) is what lets a gate
 * taken by a page that has since unmounted stay held until its in-flight
 * request settles — see the LIFETIME note above.
 */
const registry = new Map<ReorderQueueKey, QueueRegistryEntry>()

/**
 * Get (creating on first use) the registry entry for `key`.
 *
 * @param key - The queue key. Not re-validated here; every exported caller
 *   validates before reaching this helper.
 * @returns The queue's registry entry.
 */
function getEntry(key: ReorderQueueKey): QueueRegistryEntry {
  const existing = registry.get(key)
  if (existing) {
    return existing
  }
  const created: QueueRegistryEntry = { gate: createSingleFlight(), listeners: new Set() }
  registry.set(key, created)
  return created
}

/**
 * Notify every listener subscribed to `key`, synchronously, in subscription
 * order. Listeners are read into an array before iterating so a listener
 * that subscribes or unsubscribes during notification cannot skip or
 * double-visit another listener.
 *
 * @param key - The queue whose gate changed.
 */
function notify(key: ReorderQueueKey): void {
  const entry = registry.get(key)
  if (!entry) {
    return
  }
  for (const listener of Array.from(entry.listeners)) {
    listener()
  }
}

/**
 * Acquire the reorder gate for one queue (`REORDER_SINGLE_FLIGHT_RULE`'s
 * queue-scoped registry). Every reorder entry point — kebab moves,
 * Alt+Arrow, drag-drop, and `useQueueBulk.moveSelected()` — calls this
 * FIRST, before reading the current order or building a permutation body.
 *
 * @param key - Which queue's gate to acquire (`REORDER_QUEUE_KEYS`).
 * @returns A one-shot release callback when the gate was free and is now
 *   held by this caller; `null` when the queue's gate was already held, in
 *   which case the caller must return immediately without reading state or
 *   issuing a request. The returned callback is idempotent — calling it more
 *   than once releases the gate only once.
 * @throws {RangeError} When `key` is not a recognised `ReorderQueueKey`.
 */
export function acquireQueueReorder(key: ReorderQueueKey): (() => void) | null {
  assertValidQueueKey(key)
  const entry = getEntry(key)
  if (!entry.gate.tryAcquire()) {
    return null
  }
  notify(key)

  let released = false
  return () => {
    if (released) {
      return
    }
    released = true
    entry.gate.release()
    notify(key)
  }
}

/**
 * Whether one queue's reorder gate is currently held.
 *
 * A queue with no registry entry yet has never been acquired, so it reads
 * as unheld — creating the entry here is unnecessary: {@link getEntry}
 * initialises a gate as unheld anyway, so a queue with no entry and a queue
 * whose entry has never been acquired are observationally identical.
 *
 * @param key - Which queue to check (`REORDER_QUEUE_KEYS`).
 * @returns `true` while the queue's gate is held, `false` otherwise.
 * @throws {RangeError} When `key` is not a recognised `ReorderQueueKey`.
 */
export function isQueueReorderHeld(key: ReorderQueueKey): boolean {
  assertValidQueueKey(key)
  return registry.get(key)?.gate.held ?? false
}

/**
 * Subscribe to changes in one queue's reorder-gate state. Every listener is
 * invoked synchronously — not deferred to a microtask or a React commit — on
 * each {@link acquireQueueReorder} acquire and on each release of the
 * callback it returned. This is the reactive read surface
 * `REORDER_HELD_HOOK`'s `useSyncExternalStore` binding consumes.
 *
 * Because the registry is module-level, a component that unmounts and
 * remounts and re-subscribes observes the LIVE gate state, not a fresh
 * `false` — the same reason the registry outlives any one page.
 *
 * @param key - Which queue to observe (`REORDER_QUEUE_KEYS`).
 * @param listener - Called with no arguments after every acquire/release.
 * @returns An unsubscribe callback. Idempotent — calling it more than once
 *   after the first has no further effect.
 * @throws {RangeError} When `key` is not a recognised `ReorderQueueKey`.
 */
export function subscribeQueueReorder(
  key: ReorderQueueKey,
  listener: SingleFlightListener,
): () => void {
  assertValidQueueKey(key)
  const entry = getEntry(key)
  entry.listeners.add(listener)
  return () => {
    entry.listeners.delete(listener)
  }
}
