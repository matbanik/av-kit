import { expect } from 'vitest'

import { getCommand } from '../../../src/renderer/src/registry/commandRegistry'
import { ariaKeyshortcuts } from '../../../src/renderer/src/registry/shortcuts'

/** The chord a command is bound to, read loosely so ids added later still compile. */
export function chordOf(commandId: string): string | undefined {
  return getCommand(commandId as Parameters<typeof getCommand>[0])?.shortcut
}

/**
 * MEU-97 HINTS: a bound control carries the ARIA form of its command's chord and
 * its visible hint (the `title` unless given) contains the chord.
 */
export function expectBoundHint(element: HTMLElement, commandId: string, hint?: string): void {
  const chord = chordOf(commandId)
  expect(chord, `${commandId} chord`).toBeDefined()
  expect(element.getAttribute('aria-keyshortcuts'), commandId).toBe(ariaKeyshortcuts(chord ?? ''))
  expect(hint ?? element.getAttribute('title') ?? '', `${commandId} hint`).toContain(chord ?? '')
}
