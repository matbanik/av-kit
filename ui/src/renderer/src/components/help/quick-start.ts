/**
 * MEU-162 (Session 99, D-1291) the quick start of each page's How it works card.
 *
 * `quick-start.json` holds the data (schema `help-quick-start/1`). `validateQuickStart` checks
 * its shape and rules; the unit tests and the STE gate (`tools/help_guide_ste.py`) run it, so a
 * bad entry fails a test, never the card. `quickStartHash` binds each page's screenshots to its
 * steps and shots (the image manifest's `stepsHash`).
 */

import data from './quick-start.json'

export type HelpFeature = 'downloader' | 'transcript' | 'tts' | 'converter' | 'capture' | 'settings'

export type QuickStartStep = { text: string; target: string | null }
export type QuickStartShot = { name: string; steps: number[]; alt: string }
export type QuickStartPage = { intro: string; steps: QuickStartStep[]; shots: QuickStartShot[] }

export const HELP_FEATURES: readonly HelpFeature[] = [
  'downloader',
  'transcript',
  'tts',
  'converter',
  'capture',
  'settings',
]

export const QUICK_START = data.pages as Record<HelpFeature, QuickStartPage>

const MIN_STEPS = 4
const MAX_STEPS = 5
const MIN_SHOTS = 1
const MAX_SHOTS = 2
const MAX_SENTENCES = 2
const MAX_WORDS = 20
const PAGE_KEYS = ['intro', 'shots', 'steps']
const STEP_KEYS = ['target', 'text']
const SHOT_KEYS = ['alt', 'name', 'steps']

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function keyProblems(where: string, value: Record<string, unknown>, keys: readonly string[]): string[] {
  const problems: string[] = []
  for (const key of Object.keys(value)) {
    if (!keys.includes(key)) {
      problems.push(`${where}: unknown key ${key}`)
    }
  }
  for (const key of keys) {
    if (!(key in value)) {
      problems.push(`${where}: no ${key}`)
    }
  }
  return problems
}

/** The sentences of a step, split as the STE gate splits them. */
function sentences(text: string): string[] {
  return text
    .trim()
    .split(/(?<=[.!?])\s+/)
    .filter((part) => part.length > 0)
}

function stepTextProblems(where: string, text: string): string[] {
  const problems: string[] = []
  const parts = sentences(text)
  if (parts.length > MAX_SENTENCES) {
    problems.push(`${where}: ${parts.length} sentences (cap ${MAX_SENTENCES})`)
  }
  for (const part of parts) {
    const words = part.split(/\s+/).length
    if (words > MAX_WORDS) {
      problems.push(`${where}: a sentence has ${words} words (cap ${MAX_WORDS})`)
    }
  }
  if (text.includes(';')) {
    problems.push(`${where}: has a ';'`)
  }
  return problems
}

function pageProblems(feature: string, page: unknown, names: Set<string>): string[] {
  if (!isRecord(page)) {
    return [`${feature}: not an object`]
  }
  const problems = keyProblems(feature, page, PAGE_KEYS)
  if (typeof page.intro !== 'string') {
    problems.push(`${feature}: intro is not a string`)
  }

  const steps = Array.isArray(page.steps) ? page.steps : []
  if (!Array.isArray(page.steps) || steps.length < MIN_STEPS || steps.length > MAX_STEPS) {
    problems.push(`${feature}: ${steps.length} steps (want ${MIN_STEPS} to ${MAX_STEPS})`)
  }
  steps.forEach((step: unknown, index) => {
    const where = `${feature} step ${index + 1}`
    if (!isRecord(step)) {
      problems.push(`${where}: not an object`)
      return
    }
    problems.push(...keyProblems(where, step, STEP_KEYS))
    if (typeof step.text === 'string') {
      problems.push(...stepTextProblems(where, step.text))
    } else {
      problems.push(`${where}: text is not a string`)
    }
    if (step.target !== null && typeof step.target !== 'string') {
      problems.push(`${where}: target is not a string or null`)
    }
  })

  const shots = Array.isArray(page.shots) ? page.shots : []
  if (!Array.isArray(page.shots) || shots.length < MIN_SHOTS || shots.length > MAX_SHOTS) {
    problems.push(`${feature}: ${shots.length} shots (want ${MIN_SHOTS} to ${MAX_SHOTS})`)
  }
  const shotsOf = new Map<number, number>()
  shots.forEach((shot: unknown, index) => {
    const where = `${feature} shot ${index + 1}`
    if (!isRecord(shot)) {
      problems.push(`${where}: not an object`)
      return
    }
    problems.push(...keyProblems(where, shot, SHOT_KEYS))
    if (typeof shot.name !== 'string' || shot.name.length === 0) {
      problems.push(`${where}: name is not a string`)
    } else if (names.has(shot.name)) {
      problems.push(`${where}: name ${shot.name} is used twice`)
    } else {
      names.add(shot.name)
    }
    if (typeof shot.alt !== 'string') {
      problems.push(`${where}: alt is not a string`)
    }
    if (!Array.isArray(shot.steps)) {
      problems.push(`${where}: steps is not a list`)
      return
    }
    for (const n of shot.steps as unknown[]) {
      if (typeof n !== 'number' || !Number.isInteger(n) || n < 1 || n > steps.length) {
        problems.push(`${where}: step ${String(n)} is not a step of the page`)
      } else {
        shotsOf.set(n, (shotsOf.get(n) ?? 0) + 1)
      }
    }
  })

  steps.forEach((step: unknown, index) => {
    if (!isRecord(step) || typeof step.target !== 'string') {
      return
    }
    const count = shotsOf.get(index + 1) ?? 0
    if (count !== 1) {
      problems.push(`${feature} step ${index + 1}: target ${step.target} is in ${count} shots (want 1)`)
    }
  })
  return problems
}

/** Every problem of a quick start map (feature to page); an empty list means it is valid. */
export function validateQuickStart(value: unknown): string[] {
  if (!isRecord(value)) {
    return ['quick start: not an object']
  }
  const problems: string[] = []
  for (const key of Object.keys(value)) {
    if (!(HELP_FEATURES as readonly string[]).includes(key)) {
      problems.push(`quick start: unknown page ${key}`)
    }
  }
  const names = new Set<string>()
  for (const feature of HELP_FEATURES) {
    if (!(feature in value)) {
      problems.push(`${feature}: no page`)
      continue
    }
    problems.push(...pageProblems(feature, value[feature], names))
  }
  return problems
}

/** The exact string that `quickStartHash` hashes; the tests hash it with `node:crypto`. */
export function quickStartHashInput(page: QuickStartPage): string {
  return JSON.stringify({ steps: page.steps, shots: page.shots })
}

/** SHA-256 hex of `quickStartHashInput(page)`, by Web Crypto. */
export async function quickStartHash(page: QuickStartPage): Promise<string> {
  const bytes = new TextEncoder().encode(quickStartHashInput(page))
  const digest = await crypto.subtle.digest('SHA-256', bytes)
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, '0')).join('')
}
