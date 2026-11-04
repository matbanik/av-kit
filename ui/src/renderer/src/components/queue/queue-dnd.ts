/**
 * MEU-49 — screen-reader announcements for a queue row drag
 * (`DND_ANNOUNCEMENT_CONTRACT`).
 *
 * dnd-kit ships default announcements, and they are the reason this module
 * exists: they are droppable-index based ("was moved over droppable area 5"),
 * which reads one lower than the position a sighted user sees and names an
 * internal concept rather than the row. A drag that a screen-reader user can
 * perform but cannot confirm is not an accessible drag, so the wording is part
 * of the deliverable and is asserted directly.
 *
 * Everything here is a pure function of the item list. That is deliberate:
 * jsdom reports an all-zero `getBoundingClientRect`, so no real drag can
 * complete in a unit test (`JSDOM_RECT_RULE`), and pure factories let the exact
 * strings be asserted without one.
 */

/** The minimum a row must expose for an announcement to name it. */
export type QueueAnnouncementItem = {
  /** The dnd-kit sortable id, which is the job id. */
  id: string
  /** Human-facing job title, read verbatim to the user. */
  title: string
}

/** The argument shape dnd-kit passes to every announcement handler. */
export type QueueAnnouncementArgs = {
  active: { id: string | number }
  over?: { id: string | number } | null
}

/**
 * The four handlers dnd-kit calls, in the shape its `announcements` prop takes.
 *
 * A handler may return `undefined` to announce nothing at all — see
 * {@link createQueueAnnouncements} for the one case where that is correct.
 */
export type QueueAnnouncements = {
  onDragStart: (args: QueueAnnouncementArgs) => string | undefined
  onDragOver: (args: QueueAnnouncementArgs) => string | undefined
  onDragEnd: (args: QueueAnnouncementArgs) => string | undefined
  onDragCancel: (args: QueueAnnouncementArgs) => string | undefined
}

/**
 * Instructions dnd-kit renders once, before any drag, for the focused handle.
 *
 * The three keys named here are the whole keyboard drag, and `escape` is the
 * one a user cannot discover by trial: without knowing it, the only way out of
 * an unwanted drag is to commit it somewhere.
 */
export const queueScreenReaderInstructions = {
  draggable:
    'To reorder this item, press space or enter to pick it up, ' +
    'use the up and down arrow keys to choose a new position, ' +
    'then press space or enter to drop it there. ' +
    'Press escape to cancel and return it to its starting position.',
}

/**
 * Resolves a sortable id to its 1-indexed position and title.
 *
 * @param items - The rows in render order.
 * @param id - The dnd-kit id to locate.
 * @returns The row's title and 1-indexed position, or `null` when the id is
 *   not in the list — which happens if a row is removed mid-drag.
 */
function locate(
  items: readonly QueueAnnouncementItem[],
  id: string | number | undefined,
): { title: string; position: number } | null {
  if (id === undefined) {
    return null
  }
  const key = String(id)
  const index = items.findIndex((item) => item.id === key)
  if (index === -1) {
    return null
  }
  return { title: items[index].title, position: index + 1 }
}

/**
 * Builds the announcement handlers for one queue.
 *
 * Every string is position-based, 1-indexed against the list as it is rendered,
 * and names the job title — never a droppable index. `onDragCancel` is included
 * even though dnd-kit does not require it, because Escape is otherwise silent:
 * the row snaps back and the user is told nothing.
 *
 * @param items - The rows in render order; positions are read from this array.
 * @returns Handlers suitable for `DndContext`'s `announcements` prop.
 */
export function createQueueAnnouncements(
  items: readonly QueueAnnouncementItem[],
): QueueAnnouncements {
  const total = items.length

  /** What Escape, and a drop onto nothing, both announce. */
  const cancelled = (args: QueueAnnouncementArgs): string | undefined => {
    const active = locate(items, args.active.id)
    if (active === null) {
      return undefined
    }
    return (
      'Dragging "' +
      active.title +
      '" was cancelled. It returned to position ' +
      String(active.position) +
      ' of ' +
      String(total) +
      '.'
    )
  }

  /**
   * The two mid-flight announcements share everything but their verb, and both
   * depend on there being a row underneath to name a position from.
   */
  const overRow = (args: QueueAnnouncementArgs, verb: string): string | undefined => {
    const active = locate(items, args.active.id)
    const over = locate(items, args.over?.id)
    if (active === null || over === null) {
      return undefined
    }
    return (
      '"' +
      active.title +
      '" was ' +
      verb +
      ' position ' +
      String(over.position) +
      ' of ' +
      String(total) +
      '.'
    )
  }

  return {
    onDragStart: (args) => {
      const active = locate(items, args.active.id)
      if (active === null) {
        return undefined
      }
      return (
        'Picked up "' +
        active.title +
        '". It is in position ' +
        String(active.position) +
        ' of ' +
        String(total) +
        '.'
      )
    },
    /*
      `over` is null whenever the pointer or keyboard cursor leaves the sortable
      area. Announcing a position here would name one the row is not going to
      occupy, so this stays silent rather than lying; dnd-kit treats an
      `undefined` return as "no announcement".
    */
    onDragOver: (args) => overRow(args, 'moved to'),
    /*
      A drop with nothing underneath is not a move — dnd-kit reports the same
      `over: null` it does for a cancel, and the row returns where it started,
      so it gets the cancel wording rather than an invented position.
    */
    onDragEnd: (args) =>
      args.over === null || args.over === undefined
        ? cancelled(args)
        : overRow(args, 'dropped at'),
    onDragCancel: cancelled,
  }
}
