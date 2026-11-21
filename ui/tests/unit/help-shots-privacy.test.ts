/**
 * MEU-162 (Session 99) AC-162.8: the screenshot generator's pure guards.
 *
 * - `AC-162.8 privacy`: `findPrivatePath(text, roots)` flags home folders and the given roots,
 *   and passes neutral paths and words (`PRIVACY_GUARD`, D-1292).
 * - `AC-162.8 clip`: `shotClip(boxes, viewport)` returns the union of the target boxes plus
 *   24 px, or a named error; it never clamps a target away.
 * - `AC-162.8 text`: `clipText(items, clip)` keeps only the text that the image can show.
 *
 * `privacy.ts` and `clip.ts` are new in this MEU, so they are reached through
 * `import.meta.glob` and each test asserts its exports first: at Red each test fails by
 * assertion, never by a missing module.
 */

import { describe, expect, it } from 'vitest'

type Rect = { x: number; y: number; width: number; height: number }
type TargetBox = Rect & { target: string }
type ClipResult = { ok: true; clip: Rect } | { ok: false; error: string }
type TextItem = { text: string; rects: Rect[]; masked: boolean }

type PrivacyModule = {
  findPrivatePath: (text: string, roots: readonly string[]) => string | null
  clipText: (items: readonly TextItem[], clip: Rect) => string
}
type ClipModule = {
  shotClip: (boxes: readonly TargetBox[], viewport: { width: number; height: number }) => ClipResult
}

const privacyModules = import.meta.glob('../help-shots/privacy.ts', { eager: true })
const clipModules = import.meta.glob('../help-shots/clip.ts', { eager: true })

function requireExports<T>(modules: Record<string, unknown>, file: string, names: readonly string[]): T {
  const loaded = (Object.values(modules)[0] ?? {}) as Record<string, unknown>
  for (const name of names) {
    expect(typeof loaded[name], `${file} exports ${name}`).toBe('function')
  }
  return loaded as T
}

function requirePrivacy(): PrivacyModule {
  return requireExports<PrivacyModule>(privacyModules, 'tests/help-shots/privacy.ts', [
    'findPrivatePath',
    'clipText',
  ])
}

function requireClip(): ClipModule {
  return requireExports<ClipModule>(clipModules, 'tests/help-shots/clip.ts', ['shotClip'])
}

const ROOTS = ['C:/Temp/av-kit/x/tmp', 'P:/av-kit'] as const

const FLAGGED = [
  'C:\\Users\\alex\\Videos',
  'c:/users/alex/x',
  '/Users/alex/',
  '/home/alex/',
  'c:\\temp\\av-kit\\x\\tmp\\avkit-1\\logs\\console.log',
  'P:\\av-kit\\ui\\out',
] as const

const CLEAN = ['Format', 'C:/e2e/outdir', 'D:\\Media\\av-kit', 'C:\\Users\\Public\\Videos', ''] as const

const PRIVATE = 'C:\\Users\\alex\\x'

describe('MEU-162 help shot guards', () => {
  it('AC-162.8 privacy: findPrivatePath flags home folders and the roots, never a neutral path', () => {
    const { findPrivatePath } = requirePrivacy()
    const missed = FLAGGED.filter((text) => findPrivatePath(text, ROOTS) === null)
    expect(missed, 'private paths not flagged').toEqual([])
    const flagged = CLEAN.filter((text) => findPrivatePath(text, ROOTS) !== null)
    expect(flagged, 'neutral text flagged').toEqual([])
  })

  it('AC-162.8 clip: shotClip gives the union plus 24 px, or an error that names the reason', () => {
    const { shotClip } = requireClip()
    const viewport = { width: 1280, height: 800 }
    const inside = shotClip(
      [
        { target: 'url-input', x: 100, y: 100, width: 200, height: 50 },
        { target: 'add-btn', x: 400, y: 300, width: 100, height: 40 },
      ],
      viewport,
    )
    expect(inside).toEqual({ ok: true, clip: { x: 76, y: 76, width: 448, height: 288 } })

    const edge = shotClip([{ target: 'url-input', x: 10, y: 5, width: 200, height: 50 }], viewport)
    expect(edge, 'only the margin is clamped to the viewport').toEqual({
      ok: true,
      clip: { x: 0, y: 0, width: 234, height: 79 },
    })

    const below = shotClip(
      [
        { target: 'url-input', x: 100, y: 100, width: 200, height: 50 },
        { target: 'start-btn', x: 100, y: 780, width: 120, height: 40 },
      ],
      viewport,
    )
    expect(below.ok, 'a target partly below the viewport').toBe(false)
    expect(below.ok ? '' : below.error).toContain('start-btn')

    const outside = shotClip([{ target: 'open-zip-link', x: 100, y: 900, width: 120, height: 30 }], viewport)
    expect(outside.ok, 'a target fully outside the viewport').toBe(false)
    expect(outside.ok ? '' : outside.error).toContain('open-zip-link')

    const tall = shotClip(
      [
        { target: 'url-input', x: 100, y: 10, width: 200, height: 50 },
        { target: 'add-btn', x: 100, y: 940, width: 100, height: 40 },
      ],
      { width: 1280, height: 1000 },
    )
    expect(tall.ok, 'a union taller than 900 px').toBe(false)
    expect(tall.ok ? '' : tall.error).toContain('900')
  })

  it('AC-162.8 text: clipText keeps only unmasked text with a visible rect inside the clip', () => {
    const { clipText, findPrivatePath } = requirePrivacy()
    const clip = { x: 0, y: 0, width: 100, height: 100 }
    const items: TextItem[] = [
      { text: 'Add', rects: [{ x: 10, y: 10, width: 30, height: 12 }], masked: false },
      { text: 'https://www.youtube.com/watch?v=demo', rects: [{ x: 10, y: 40, width: 80, height: 20 }], masked: false },
      { text: `masked ${PRIVATE}`, rects: [{ x: 10, y: 70, width: 50, height: 12 }], masked: true },
      { text: `outside ${PRIVATE}`, rects: [{ x: 200, y: 200, width: 50, height: 12 }], masked: false },
      { text: `empty ${PRIVATE}`, rects: [{ x: 20, y: 20, width: 0, height: 12 }], masked: false },
    ]
    const text = clipText(items, clip)
    expect(text.split('\n')).toEqual(['Add', 'https://www.youtube.com/watch?v=demo'])
    expect(findPrivatePath(text, [])).toBeNull()

    const shown: TextItem = { text: `shown ${PRIVATE}`, rects: [{ x: 10, y: 70, width: 50, height: 12 }], masked: false }
    expect(findPrivatePath(clipText([...items, shown], clip), [])).not.toBeNull()
  })
})
