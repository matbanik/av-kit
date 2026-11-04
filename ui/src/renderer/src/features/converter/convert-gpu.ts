export type GpuSnapshot = {
  nvidia_nvenc: boolean
  amd_amf: boolean
  intel_qsv: boolean
}

export function gpuChipLabel(opts: {
  ffmpegAvailable: boolean | undefined
  gpu: GpuSnapshot | undefined
}): string {
  if (opts.ffmpegAvailable === false) {
    return 'FFmpeg missing'
  }
  if (opts.gpu === undefined) {
    return 'Encoder: Checking…'
  }
  if (opts.gpu.nvidia_nvenc) {
    return 'Encoder: NVIDIA NVENC'
  }
  if (opts.gpu.amd_amf) {
    return 'Encoder: AMD AMF'
  }
  if (opts.gpu.intel_qsv) {
    return 'Encoder: Intel QSV'
  }
  return 'Encoder: Software (libx265)'
}
