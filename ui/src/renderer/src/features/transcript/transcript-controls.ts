export const JOB_STATUSES = [
  'Pending',
  'Processing',
  'Paused',
  'Done',
  'Failed',
  'Cancelled',
] as const

export type JobStatus = (typeof JOB_STATUSES)[number]
export type ProcessorState = 'Idle' | 'Processing' | 'Paused'

export type QueueControl =
  | 'start'
  | 'pause'
  | 'resume'
  | 'stop'
  | 'up'
  | 'down'
  | 'remove'
  | 'compile'
  | 'view-compiled'
  | 'open-zip'
  | 'open-folder'

export type QueueItemLike = {
  id: string
  status: string
  transcripts_done: number
  output_dir: string
  zip_path: string | null
  compiled_path?: string | null
}

export type ControlContext = {
  items: QueueItemLike[]
  selectedId: string | null
  processorState: ProcessorState
}

export const STATUS_COLORS: Record<JobStatus, string> = {
  Pending: 'bg-status-pending',
  Processing: 'bg-accent',
  Paused: 'bg-status-pending',
  Done: 'bg-accent-green',
  Failed: 'bg-error',
  Cancelled: 'bg-neutral',
}

function selectedIndex(ctx: ControlContext): number {
  if (ctx.selectedId === null) {
    return -1
  }
  return ctx.items.findIndex((item) => item.id === ctx.selectedId)
}

export function controlEnabled(control: QueueControl, ctx: ControlContext): boolean {
  const selected = selectedIndex(ctx)
  const current = selected >= 0 ? ctx.items[selected] : undefined
  const hasStartable = ctx.items.some((item) => item.status === 'Pending' || item.status === 'Paused')
  switch (control) {
    case 'start':
      return hasStartable && ctx.processorState !== 'Processing'
    case 'pause':
      return ctx.processorState === 'Processing'
    case 'resume':
      return ctx.processorState === 'Paused'
    case 'stop':
      return ctx.processorState === 'Processing' || ctx.processorState === 'Paused'
    case 'up':
      return selected > 0
    case 'down':
      return selected >= 0 && selected < ctx.items.length - 1
    case 'remove':
      return selected >= 0
    case 'compile':
      return current != null && current.transcripts_done > 0
    case 'view-compiled':
      return current?.compiled_path != null && current.compiled_path.length > 0
    case 'open-zip':
      return current?.zip_path != null && current.zip_path.length > 0
    case 'open-folder':
      return current != null && current.output_dir.length > 0
    default: {
      const _never: never = control
      return _never
    }
  }
}

export function actionVisible(action: 'requeue' | 'retry', status: string): boolean {
  if (action === 'requeue') {
    return status === 'Cancelled'
  }
  return status === 'Failed'
}

export function buildReorderBody(
  ids: string[],
  selectedId: string,
  direction: 'up' | 'down',
): { job_ids: string[] } {
  const index = ids.indexOf(selectedId)
  if (index < 0) {
    return { job_ids: [...ids] }
  }
  const next = [...ids]
  const [row] = next.splice(index, 1)
  if (direction === 'up') {
    next.splice(Math.max(0, index - 1), 0, row)
  } else {
    next.splice(Math.min(next.length, index + 1), 0, row)
  }
  return { job_ids: next }
}

export function processorLabel(state: ProcessorState): string | null {
  if (state === 'Idle') {
    return null
  }
  if (state === 'Processing') {
    return 'Processing…'
  }
  return 'Queue Paused'
}
