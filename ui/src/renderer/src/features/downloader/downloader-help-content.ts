import type { HelpSection } from '../../components/help/HelpCard'

export const DOWNLOADER_HELP_SECTIONS: HelpSection[] = [
  {
    id: 'url-types',
    title: 'Links you can add',
    body: 'Paste a video, playlist or channel URL into the box. The app reads the details of each link before it downloads.',
  },
  {
    id: 'sabr',
    title: 'SABR limits',
    body: 'When SABR is on, YouTube limits the quality and audio choices. Run the SABR check to see if it blocks better formats.',
  },
  {
    id: 'cookies',
    title: 'Videos that need a sign-in',
    body: 'Some videos need a sign-in. Set the cookie mode to Browser or File to use your sign-in. Test the cookies before you start a large batch.',
  },
  {
    id: 'archive',
    title: 'Skip the videos you have',
    body: 'Enable archive tracking in Settings. The app then skips the videos that you downloaded before.',
  },
  {
    id: 'pause',
    title: 'Pause vs cancel',
    body: 'Pause after this job lets the current download finish, then stops the queue with its order intact; Resume continues later. Cancel stops the current download at once and does not delete finished files.',
  },
]
