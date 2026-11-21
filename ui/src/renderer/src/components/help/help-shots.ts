/**
 * MEU-162 (Session 99, D-1292) the help card's screenshots.
 *
 * The generator (`npm run help:shots`) writes `assets/help/<name>-<theme>.webp` and
 * `assets/help/manifest.json`. Both are read through `import.meta.glob`, never a static import,
 * so the renderer builds and type-checks with no images and no manifest. A shot with no URL or
 * no size renders no figure.
 */

export type ShotTheme = 'light' | 'dark'

type ManifestEntry = { name: string; width: number; height: number }

const URLS = import.meta.glob<string>('../../assets/help/*.webp', {
  eager: true,
  query: '?url',
  import: 'default',
})

const MANIFESTS = import.meta.glob<ManifestEntry[]>('../../assets/help/manifest.json', {
  eager: true,
  import: 'default',
})

const MANIFEST: ManifestEntry[] = Object.values(MANIFESTS)[0] ?? []

/** The URL of `assets/help/<name>-<theme>.webp`, or null when the file does not exist. */
export function shotUrl(name: string, theme: ShotTheme): string | null {
  return URLS[`../../assets/help/${name}-${theme}.webp`] ?? null
}

/** The manifest's width and height of a shot, or null when the manifest has no entry. */
export function shotSize(name: string): { width: number; height: number } | null {
  const entry = MANIFEST.find((e) => e.name === name)
  return entry ? { width: entry.width, height: entry.height } : null
}
