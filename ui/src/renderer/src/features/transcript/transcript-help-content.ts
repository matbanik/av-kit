import type { HelpSection } from '../../components/help/HelpCard'

export const TRANSCRIPT_HELP_SECTIONS: HelpSection[] = [
  {
    id: 'resume',
    title: 'Resume after pause',
    body: 'Resume continues transcript extraction from the last saved checkpoint without re-fetching completed videos.',
  },
  {
    id: 'cancelled',
    title: 'Stop and Cancelled',
    body: 'Stop marks in-flight jobs as Cancelled. Finished transcripts remain on disk; only active work is interrupted.',
  },
  {
    id: 'requeue',
    title: 'Requeue failed jobs',
    body: 'Requeue sends a Cancelled or failed channel back to the pending queue with the same output directory.',
  },
  {
    id: 'compile',
    title: 'Compile and zip',
    body: 'Compile merges per-video transcripts into one document. Zip packages the compile output for sharing.',
  },
  {
    id: 'rate',
    title: 'Rate limits',
    body: 'Adjust requests per hour and batch delays in settings to stay under YouTube transcript rate limits.',
  },
]
