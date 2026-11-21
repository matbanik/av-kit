import type { HelpSection } from '../../components/help/HelpCard'

export const TTS_HELP_SECTIONS: HelpSection[] = [
  {
    id: 'prepare',
    title: 'Prepare the text',
    body: 'Prepare cleans the text before you click Generate. It corrects the punctuation and the spaces for speech.',
  },
  {
    id: 'voice',
    title: 'Pick a voice',
    body: 'Use the language filter to make the voice list shorter. The speed presets make the speech faster or slower.',
  },
  {
    id: 'download',
    title: 'Get a model',
    body: 'Get downloads a Kokoro model to your models folder when the model is not there.',
  },
  {
    id: 'load',
    title: 'Load and Unload',
    body: 'Load puts the model in memory. Unload frees the memory. Unload the model before you change to a different model.',
  },
  {
    id: 'paste',
    title: 'Paste or open a file',
    body: 'Paste the text, or open a .txt or .md file. The app splits long text into parts. Set the part size in Settings.',
  },
]
