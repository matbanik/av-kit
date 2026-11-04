export const CONVERT_VIDEO_EXTENSIONS = ['mp4', 'mkv', 'mov', 'webm', 'avi', 'm4v'] as const
export const CONVERT_AUDIO_EXTENSIONS = [
  'mp3',
  'wav',
  'm4a',
  'aac',
  'flac',
  'ogg',
  'opus',
  'wma',
  'ac3',
] as const

export const CONVERT_DIALOG_FILTERS = [
  { name: 'Video', extensions: [...CONVERT_VIDEO_EXTENSIONS] },
  { name: 'Audio', extensions: [...CONVERT_AUDIO_EXTENSIONS] },
] as const
