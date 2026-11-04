import { existsSync, readdirSync, statSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))

/**
 * The newest modification time under `dir`, together with the file that carries it.
 *
 * A directory's own mtime is not sufficient — it does not move when a nested file is edited —
 * so the tree is walked rather than stat'd at the root.
 */
function newestSource(dir: string): { path: string; mtimeMs: number } {
  let newest = { path: dir, mtimeMs: 0 }
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name)
    const found = entry.isDirectory()
      ? newestSource(full)
      : { path: full, mtimeMs: statSync(full).mtimeMs }
    if (found.mtimeMs > newest.mtimeMs) {
      newest = found
    }
  }
  return newest
}

export default async function globalSetup(): Promise<void> {
  const selected = process.env.AVKIT_E2E_OUT_DIR ?? 'out'
  if (selected !== 'out' && selected !== 'out-e2e') {
    throw new Error('AVKIT_E2E_OUT_DIR must be out or out-e2e')
  }
  const main = resolve(here, `../../${selected}/main/index.js`)
  if (!existsSync(main)) {
    throw new Error(`${selected}/main/index.js missing — run npm run build before Playwright`)
  }
  // A bundle that merely *exists* proves nothing. A freshly stamped Playwright report over a
  // stale `out/` reads exactly like real evidence while actually exercising the previous
  // implementation — which is how three corrected defects passed a green real-Electron run
  // (execution review round 2, finding R2-1). Fail closed the moment a source outruns the build.
  const newest = newestSource(resolve(here, '../../src'))
  const built = statSync(main).mtimeMs
  const config = resolve(here, '../../electron.vite.config.ts')
  if (newest.mtimeMs > built || statSync(config).mtimeMs > built) {
    throw new Error(
      `${selected}/main/index.js is older than ${newest.path} or ${config} — run npm run build before Playwright`,
    )
  }
  if (selected === 'out-e2e') {
    const html = resolve(here, '../../out-e2e/renderer/primitive-harness.html')
    if (!existsSync(html)) {
      throw new Error('out-e2e/renderer/primitive-harness.html missing — build the isolated harness')
    }
    const entry = resolve(here, '../../src/renderer/src/primitive-harness.tsx')
    if (statSync(entry).mtimeMs > statSync(html).mtimeMs || statSync(config).mtimeMs > statSync(html).mtimeMs) {
      throw new Error('out-e2e/renderer/primitive-harness.html is stale — rebuild the isolated harness')
    }
  }
}
