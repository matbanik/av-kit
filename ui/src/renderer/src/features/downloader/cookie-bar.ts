import { z } from 'zod'

export const COOKIE_MODES = ['none', 'browser', 'file'] as const
export type CookieMode = (typeof COOKIE_MODES)[number]

export const COOKIE_BROWSERS = [
  'chrome',
  'firefox',
  'edge',
  'brave',
  'opera',
  'vivaldi',
  'chromium',
  'whale',
  'safari',
] as const

export const COOKIE_SETTINGS_LEAVES = [
  'cookie_mode',
  'cookie_browser',
  'cookie_browser_profile',
  'cookie_file_path',
] as const

const settingsSchema = z
  .object({
    cookie_mode: z.enum(COOKIE_MODES),
    cookie_browser: z.enum(COOKIE_BROWSERS),
    cookie_browser_profile: z.string(),
    cookie_file_path: z.string(),
  })
  .strict()

const testSchema = z.discriminatedUnion('mode', [
  z.object({ mode: z.literal('none') }).strict(),
  z
    .object({
      mode: z.literal('browser'),
      browser: z.enum(COOKIE_BROWSERS),
      profile: z.string().optional(),
    })
    .strict(),
  z
    .object({
      mode: z.literal('file'),
      cookie_file: z.string().min(1),
    })
    .strict(),
])

export function cookieSettingsPutBody(input: {
  cookie_mode: CookieMode
  cookie_browser: string
  cookie_browser_profile: string
  cookie_file_path: string
}): {
  cookie_mode: CookieMode
  cookie_browser: string
  cookie_browser_profile: string
  cookie_file_path: string
} {
  return settingsSchema.parse(input)
}

export function cookieTestBody(input: {
  mode: CookieMode
  browser?: string
  profile?: string
  cookie_file?: string
}): { mode: CookieMode; browser?: string; profile?: string; cookie_file?: string } {
  return testSchema.parse(input)
}

export function audioFormatVisible(audioOnly: boolean): boolean {
  return audioOnly
}

export function cookieBrowserVisible(mode: CookieMode): boolean {
  return mode === 'browser'
}

export function cookieFileVisible(mode: CookieMode): boolean {
  return mode === 'file'
}
