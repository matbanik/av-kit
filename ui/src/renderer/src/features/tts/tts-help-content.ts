import type { HelpSection } from '../../components/help/HelpCard'

export const TTS_HELP_SECTIONS: HelpSection[] = [
  {
    id: 'prepare',
    title: 'Prepare cleanup',
    body: 'Prepare runs text cleanup steps before generation so punctuation and whitespace are speech-ready.',
  },
  {
    id: 'voice',
    title: 'Voice selection',
    body: 'Pick a voice and language filter to narrow Kokoro voices. Speed presets adjust playback rate.',
  },
  {
    id: 'download',
    title: 'Model download',
    body: 'Download fetches a Kokoro variant into your models directory when it is not yet cached locally.',
  },
  {
    id: 'load',
    title: 'Load and unload',
    body: 'Load mounts the selected variant into memory. Unload frees GPU/CPU resources when switching models.',
  },
  {
    id: 'paste',
    title: 'File and paste input',
    body: 'Paste clipboard text or load a .txt/.md file. Large inputs are split using chunk_max_chars from settings.',
  },
]
