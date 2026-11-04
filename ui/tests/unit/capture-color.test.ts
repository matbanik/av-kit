/** @vitest-environment node */

import { describe, expect, it } from 'vitest'

describe('MEU-60 named colors', () => {
  it('AC-60.17 NAMED_COLOR_HEX maps every NAMED_COLORS name; unknown names are not coerced', async () => {
    const mod = await import('../../src/renderer/src/features/capture/capture-color')
    expect(mod.NAMED_COLOR_HEX).toEqual({
      red: '#FF0000',
      orange: '#FFA500',
      yellow: '#FFFF00',
      green: '#008000',
      blue: '#0000FF',
      white: '#FFFFFF',
      black: '#000000',
    })
    expect(mod.hexForNamedColor('green')).toBe('#008000')
    expect(mod.hexForNamedColor('orange')).toBe('#FFA500')
    expect(mod.hexForNamedColor('purple')).toBeNull()
    expect(mod.normalizeHex('#12abcd')).toBe('#12ABCD')
    expect(mod.normalizeHex('red')).toBeNull()
    expect(mod.normalizeHex('#fff')).toBeNull()
  })
})

/** WCAG 2.1 relative luminance of `#RRGGBB`, computed independently of the module under test. */
function wcagLuminance(hex: string): number {
  const channel = (offset: number): number => {
    const c = Number.parseInt(hex.slice(offset, offset + 2), 16) / 255
    return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4
  }
  return 0.2126 * channel(1) + 0.7152 * channel(3) + 0.0722 * channel(5)
}

function wcagRatio(a: string, b: string): number {
  const [hi, lo] = [wcagLuminance(a), wcagLuminance(b)].sort((x, y) => y - x) as [number, number]
  return (hi + 0.05) / (lo + 0.05)
}

describe('MEU-86 contrast text (CONTRAST_TEXT)', () => {
  it('AC-86.1 contrastText gives the R-2 table, every pick reaches 4.5:1, and lowercase input agrees', async () => {
    const mod = await import('../../src/renderer/src/features/capture/capture-color')
    expect(typeof (mod as Record<string, unknown>).contrastText).toBe('function')
    const expected: Record<string, string> = {
      red: '#000000',
      orange: '#000000',
      yellow: '#000000',
      white: '#000000',
      green: '#FFFFFF',
      blue: '#FFFFFF',
      black: '#FFFFFF',
    }
    for (const [name, hex] of Object.entries(mod.NAMED_COLOR_HEX)) {
      const pick = mod.contrastText(hex)
      expect(pick, name).toBe(expected[name])
      expect(wcagRatio(hex, pick), name).toBeGreaterThanOrEqual(4.5)
      expect(mod.contrastText(hex.toLowerCase()), name).toBe(pick)
    }
  })

  it('AC-86.1 negative: a name, a short hex and empty text throw RangeError', async () => {
    const mod = await import('../../src/renderer/src/features/capture/capture-color')
    expect(typeof (mod as Record<string, unknown>).contrastText).toBe('function')
    for (const raw of ['red', '#FFF', '']) {
      expect(() => mod.contrastText(raw), raw).toThrow(RangeError)
    }
  })
})
