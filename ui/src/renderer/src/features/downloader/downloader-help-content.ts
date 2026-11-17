import type { HelpSection } from '../../components/help/HelpCard'

export const DOWNLOADER_HELP_SECTIONS: HelpSection[] = [
  {
    id: 'url-types',
    title: 'URL types',
    body: 'Paste a video URL, playlist URL, or channel page URL into the queue. Each URL type resolves metadata before download starts.',
  },
  {
    id: 'sabr',
    title: 'SABR restrictions',
    body: 'When SABR is active, quality and audio options are limited. Run a SABR check to see whether Server-Adaptive Bitrate is blocking higher formats.',
  },
  {
    id: 'cookies',
    title: 'Cookie authentication',
    body: 'Use cookie mode browser or file when YouTube requires signed-in access. Test cookies before starting large batches.',
  },
  {
    id: 'archive',
    title: 'Archive tracking',
    body: 'Enable archive tracking in settings to skip videos you already downloaded in prior sessions.',
  },
  {
    id: 'pause',
    title: 'Pause vs cancel',
    body: 'Pause after this job lets the current download finish, then stops the queue with its order intact; Resume continues later. Cancel stops the current download at once and does not delete finished files.',
  },
]
