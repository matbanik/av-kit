/**
 * Pure rules for the transcript channel card (MEU-55).
 *
 * The card renders through the shared `QueueCard`; this module decides what it
 * shows. `controlEnabled` and `actionVisible` stay the only source of truth for
 * whether an action is available (TR4) — nothing here restates an enablement
 * rule, it only scopes the existing one to a single card.
 */
import type { QueueCardJob } from '../../components/queue/QueueCard'
import {
  actionVisible,
  controlEnabled,
  JOB_STATUSES,
  type JobStatus,
  type ProcessorState,
  type QueueItemLike,
} from './transcript-controls'
import type { TranscriptListItem } from './useTranscriptQueue'

/**
 * `TRANSCRIPT_MENU_ORDER` — the per-card kebab, in render order. Each id keeps
 * the existing footer button's test id on its menu item.
 */
export const TRANSCRIPT_MENU_ORDER = [
  'requeue',
  'retry',
  'compile',
  'view-compiled',
  'open-zip',
  'open-folder',
  'remove',
] as const

export type TranscriptCardAction = (typeof TRANSCRIPT_MENU_ORDER)[number]

/** The existing test id each action keeps (`PRESERVED_TESTIDS`). */
export const CARD_ACTION_TESTIDS: Readonly<Record<TranscriptCardAction, string>> = {
  requeue: 'requeue-btn',
  retry: 'retry-btn',
  compile: 'compile-btn',
  'view-compiled': 'view-compiled-btn',
  'open-zip': 'open-zip-btn',
  'open-folder': 'open-folder-btn',
  remove: 'remove-btn',
}

/** Link ids are distinct from menu ids so an id never appears twice on a card. */
export const CARD_LINK_TESTIDS: Readonly<Partial<Record<TranscriptCardAction, string>>> = {
  requeue: 'requeue-link',
  retry: 'retry-link',
  'view-compiled': 'view-compiled-link',
  'open-zip': 'open-zip-link',
  'open-folder': 'open-folder-link',
}

/**
 * `CARD_LINKS` — status → candidate links (mockup §06), before availability.
 * Closed over `JobStatus`, so a new status must be classified here to compile.
 */
const LINK_CANDIDATES: Readonly<Record<JobStatus, readonly TranscriptCardAction[]>> = {
  Done: ['view-compiled', 'open-zip'],
  Processing: ['open-folder'],
  Failed: ['retry'],
  Cancelled: ['requeue'],
  Pending: [],
  Paused: [],
}

/** Map an API status string onto the closed status set, as the page always has. */
export function asJobStatus(status: string): JobStatus {
  return (JOB_STATUSES as readonly string[]).includes(status) ? (status as JobStatus) : 'Pending'
}

type CardContext = {
  items: readonly QueueItemLike[]
  processorState: ProcessorState
}

/**
 * `CARD_ACTION_AVAILABLE` — whether an action exists for this card right now.
 *
 * @param action - The per-card action.
 * @param card - The card's item.
 * @param ctx - The whole queue and the processor state.
 * @returns True when the action is available for this card.
 */
export function cardActionAvailable(
  action: TranscriptCardAction | 'up' | 'down',
  card: QueueItemLike,
  ctx: CardContext,
): boolean {
  switch (action) {
    case 'requeue':
    case 'retry':
      return actionVisible(action, card.status)
    case 'compile':
    case 'view-compiled':
    case 'open-zip':
    case 'open-folder':
    case 'remove':
    case 'up':
    case 'down':
      return controlEnabled(action, { items: [...ctx.items], selectedId: card.id, processorState: ctx.processorState })
    default: {
      const unreachable: never = action
      return unreachable
    }
  }
}

/** The available menu actions for a card, in {@link TRANSCRIPT_MENU_ORDER}. */
export function cardMenuActions(card: QueueItemLike, ctx: CardContext): TranscriptCardAction[] {
  return TRANSCRIPT_MENU_ORDER.filter((action) => cardActionAvailable(action, card, ctx))
}

/** The available status links for a card (`CARD_LINKS` ∩ availability). */
export function cardLinkActions(card: QueueItemLike, ctx: CardContext): TranscriptCardAction[] {
  return LINK_CANDIDATES[asJobStatus(card.status)].filter((action) => cardActionAvailable(action, card, ctx))
}

/** Per-status counts over the closed status set, for the header chips. */
export function statusCounts(items: readonly { status: string }[]): Record<JobStatus, number> {
  const counts = Object.fromEntries(JOB_STATUSES.map((status) => [status, 0])) as Record<JobStatus, number>
  for (const item of items) {
    counts[asJobStatus(item.status)] += 1
  }
  return counts
}

/** The shared card's view of a channel row. */
export function toQueueCardJob(item: TranscriptListItem): QueueCardJob {
  return {
    id: item.id,
    position: item.queue_position,
    status: item.status,
    title: item.channel_name,
  }
}

/** Progress ratio for a channel, or null when there is nothing to measure. */
export function channelRatio(item: Pick<TranscriptListItem, 'video_count' | 'transcripts_done'>): number | null {
  return item.video_count > 0 ? item.transcripts_done / item.video_count : null
}
