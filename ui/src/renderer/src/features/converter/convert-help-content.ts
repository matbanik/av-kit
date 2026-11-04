import type { HelpSection } from '../../components/help/HelpCard'

export const CONVERT_HELP_SECTIONS: HelpSection[] = [
  {
    id: 'what-convert-does',
    title: 'What Convert does',
    body: 'Convert compresses, cuts, or extracts audio from local video files. Drop files, pick a task, then Add then Start. Work stays on disk — Convert never uploads to YouTube.',
  },
  {
    id: 'presets-advanced',
    title: 'Presets vs Advanced',
    body: 'Preset chips pick a named quality recipe. Open Advanced to change CQ, scale, and audio. Changing a preset resets Advanced to that catalog.',
  },
  {
    id: 'gpu-software',
    title: 'GPU auto / software fallback',
    body: 'The encoder chip reports NVIDIA NVENC, AMD AMF, Intel QSV, or Software (libx265). Refresh re-runs detection. Missing FFmpeg disables Add and Start.',
  },
  {
    id: 'fast-cut',
    title: 'Fast cut vs Accurate',
    body: 'Fast cut copies packets and may snap to keyframes. Accurate re-encodes the trimmed span when you need exact In/Out times.',
  },
  {
    id: 'extract-containers',
    title: 'Extract containers',
    body: 'Extract copies the first audio stream or all streams. The container follows the codec (AAC to .m4a, PCM to .wav). No re-encode on the default path.',
  },
  {
    id: 'sequential-gpu',
    title: 'Sequential GPU',
    body: 'Jobs run one file at a time so a single GPU encode does not overlap. Add files to the queue, then Start.',
  },
]
