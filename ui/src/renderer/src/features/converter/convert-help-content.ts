import type { HelpSection } from '../../components/help/HelpCard'

export const CONVERT_HELP_SECTIONS: HelpSection[] = [
  {
    id: 'what-convert-does',
    title: 'What Convert does',
    body: 'Convert can compress, cut or extract audio from video files on your computer. Drop the files, pick a task, then click Add and Start. The files stay on your computer. Convert never uploads to YouTube.',
  },
  {
    id: 'presets-advanced',
    title: 'Presets and Advanced',
    body: 'A preset is a named quality recipe. Open Advanced to change CQ, scale and audio. When you pick a different preset, Advanced resets to that preset.',
  },
  {
    id: 'gpu-software',
    title: 'Graphics card or Software',
    body: 'The encoder chip shows NVIDIA NVENC, AMD AMF, Intel QSV or Software. Refresh checks again. If FFmpeg is missing, you cannot use Add and Start.',
  },
  {
    id: 'fast-cut',
    title: 'Fast cut and Accurate',
    body: 'Fast cut copies the video and can move the cut to a keyframe. Accurate encodes the part again for exact In and Out times.',
  },
  {
    id: 'extract-containers',
    title: 'File types for Extract',
    body: 'Extract copies the first audio stream or all the streams. The file type follows the codec: AAC gives .m4a and PCM gives .wav. The default does not encode again.',
  },
  {
    id: 'sequential-gpu',
    title: 'One file at a time',
    body: 'Convert works on one file at a time, so two GPU encodes do not overlap. Add the files to the queue, then click Start.',
  },
]
