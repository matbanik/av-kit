/**
 * `TRANSCRIPT_TOOLBAR` — the transcript queue's header actions (TR1, TR2).
 *
 * Exactly three interactive elements: Start, one Pause/Resume node and Stop.
 * There is no Clear finished control and no overflow, because the transcript
 * queue has no such mutation (TR1). The Pause/Resume node swaps its label, its
 * command and its test id together with the processor state (TR2), so
 * `pause-btn` and `resume-btn` are never both in the DOM.
 */
import { Pause, Play, Square } from 'lucide-react'
import type { ReactElement } from 'react'

import { Button } from '../../components/ui/Button'
import type { ProcessorState } from './transcript-controls'

export type TranscriptToolbarProps = {
  processorState: ProcessorState
  canStart: boolean
  canPause: boolean
  canResume: boolean
  canStop: boolean
  onStart: () => void
  onPause: () => void
  onResume: () => void
  onStop: () => void
}

const iconClasses = 'h-4 w-4'

/**
 * Render the three-action toolbar.
 *
 * @param props - See {@link TranscriptToolbarProps}.
 * @returns The labelled control group.
 */
export function TranscriptToolbar({
  processorState,
  canStart,
  canPause,
  canResume,
  canStop,
  onStart,
  onPause,
  onResume,
  onStop,
}: TranscriptToolbarProps): ReactElement {
  const paused = processorState === 'Paused'
  return (
    <div role="group" aria-label="Transcript queue actions" className="flex items-center gap-1.5 self-start">
      <Button data-testid="start-btn" variant="ghost" size="sm" disabled={!canStart} onClick={onStart}>
        <Play className={iconClasses} aria-hidden="true" />
        Start
      </Button>
      {paused ? (
        <Button data-testid="resume-btn" variant="ghost" size="sm" disabled={!canResume} onClick={onResume}>
          <Play className={iconClasses} aria-hidden="true" />
          Resume
        </Button>
      ) : (
        <Button data-testid="pause-btn" variant="ghost" size="sm" disabled={!canPause} onClick={onPause}>
          <Pause className={iconClasses} aria-hidden="true" />
          Pause
        </Button>
      )}
      <Button data-testid="stop-btn" variant="ghost" size="sm" disabled={!canStop} onClick={onStop}>
        <Square className={iconClasses} aria-hidden="true" />
        Stop
      </Button>
    </div>
  )
}
