export const NAMED_COLOR_HEX = {
  red: '#FF0000',
  orange: '#FFA500',
  yellow: '#FFFF00',
  green: '#008000',
  blue: '#0000FF',
  white: '#FFFFFF',
  black: '#000000',
} as const

export type NamedColor = keyof typeof NAMED_COLOR_HEX

const HEX6 = /^#[0-9A-Fa-f]{6}$/

export function hexForNamedColor(name: string): string | null {
  if (Object.prototype.hasOwnProperty.call(NAMED_COLOR_HEX, name)) {
    return NAMED_COLOR_HEX[name as NamedColor]
  }
  return null
}

export function normalizeHex(value: string): string | null {
  if (!HEX6.test(value)) {
    return null
  }
  return value.toUpperCase()
}

export function displayHex(color: string): string {
  return hexForNamedColor(color) ?? normalizeHex(color) ?? color
}

/** WCAG 2.1 relative luminance of a normalized `#RRGGBB`. */
function relativeLuminance(hex: string): number {
  const channel = (offset: number): number => {
    const c = Number.parseInt(hex.slice(offset, offset + 2), 16) / 255
    return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4
  }
  return 0.2126 * channel(1) + 0.7152 * channel(3) + 0.0722 * channel(5)
}

/**
 * CONTRAST_TEXT (MEU-86): black or white text, whichever has the higher WCAG contrast ratio on
 * `hex`; a tie goes to black. Anything but `#RRGGBB` throws RangeError.
 */
export function contrastText(hex: string): '#000000' | '#FFFFFF' {
  const normalized = normalizeHex(hex)
  if (normalized === null) {
    throw new RangeError(`contrastText needs #RRGGBB, got ${JSON.stringify(hex)}`)
  }
  const luminance = relativeLuminance(normalized)
  return (luminance + 0.05) / 0.05 >= 1.05 / (luminance + 0.05) ? '#000000' : '#FFFFFF'
}
