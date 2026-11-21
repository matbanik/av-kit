import type { HelpSection } from '../../components/help/HelpCard'

export const TRANSCRIPT_HELP_SECTIONS: HelpSection[] = [
  {
    id: 'resume',
    title: 'Resume after a pause',
    body: 'Resume starts again from the last saved point. It does not get the finished videos again.',
  },
  {
    id: 'cancelled',
    title: 'Stop and Cancelled',
    body: 'Stop marks the running jobs Cancelled. The finished transcripts stay on the disk. Stop interrupts only the work that runs now.',
  },
  {
    id: 'requeue',
    title: 'Requeue a channel',
    body: 'Requeue puts a Cancelled or failed channel back in the queue. It uses the same output folder.',
  },
  {
    id: 'compile',
    title: 'Compile and Zip',
    body: 'Compile puts all the transcripts of a channel in one file. Zip packs that file so that you can share it.',
  },
  {
    id: 'rate',
    title: 'Stay under the rate limits',
    body: 'Set the requests per hour and the batch delay in Settings. These keep you under the YouTube rate limits.',
  },
  {
    id: 'blocked',
    title: 'Blocked caption requests',
    body: 'When YouTube blocks caption requests, the job pauses with that reason and makes no more requests. Resume tries again; another network often works sooner.',
  },
]
