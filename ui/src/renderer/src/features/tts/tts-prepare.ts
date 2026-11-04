export const PREPARE_STEPS = [
  'punctuation',
  'symbols',
  'numbers',
  'currency',
  'all_caps',
  'chapter_markers',
  'urls_emails',
  'page_numbers',
  'whitespace',
  'chunk',
  'kokoro',
] as const

export type PrepareStep = (typeof PREPARE_STEPS)[number]

export const PREPARE_DEFAULT_ON: PrepareStep[] = PREPARE_STEPS.filter(
  (step) => step !== 'chapter_markers',
)

/**
 * `CLEANUP_LABELS` — human labels for the cleanup steps (TT2).
 *
 * Presentation only: every checkbox keeps its step id as its value, and that id
 * is what reaches `enabled_steps`. The `Record` over `PrepareStep` makes a new
 * step fail to compile until it is labelled.
 */
export const CLEANUP_LABELS: Readonly<Record<PrepareStep, string>> = {
  punctuation: 'Punctuation',
  symbols: 'Symbols',
  numbers: 'Numbers',
  currency: 'Currency',
  all_caps: 'All caps',
  chapter_markers: 'Chapter markers',
  urls_emails: 'URLs & emails',
  page_numbers: 'Page numbers',
  whitespace: 'Whitespace',
  chunk: 'Chunk',
  kokoro: 'Kokoro',
}
