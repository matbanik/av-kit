export type RateEtaInput = {
  delay: number
  videoCount: number
  transcriptsDone: number
}

export type RateEta = {
  rate: string
  etaSeconds: number
}

export function formatRateEta(input: RateEtaInput): RateEta | null {
  if (!Number.isFinite(input.delay) || input.delay <= 0) {
    return null
  }
  const remaining = Math.max(0, input.videoCount - input.transcriptsDone)
  return {
    rate: `1 req/${input.delay}s`,
    etaSeconds: remaining * input.delay,
  }
}
