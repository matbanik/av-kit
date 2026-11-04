import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs'
import { resolve } from 'node:path'

import { describe, expect, it } from 'vitest'

import { STATUS_PILL_TOKENS as QUEUE_PILL_TOKENS } from '../../src/renderer/src/lib/queue/status-tokens'

const uiRoot = resolve(__dirname, '../..')
const repoRoot = resolve(uiRoot, '..')

/** PILL_TOKEN_SOURCE — av-kit's copy of the Zorivest palette its pills were seeded from (_inspiration/zorivest/PROVENANCE.md). */
const PILL_TOKEN_SOURCE = resolve(repoRoot, '_inspiration/zorivest/globals.css')

const PHASE10_SPEC = 'docs/build-plan/10-queue-card-ui.md'
const GUI_SPEC = 'docs/build-plan/06-gui.md'
const TOKEN_FILE = 'ui/src/renderer/src/styles.css'
const MATRIX = 'docs/build-plan/build-priority-matrix.md'
const BUILD_PLAN = 'docs/BUILD_PLAN.md'
const SSOT = '.agent/context/meu-status.yaml'

const THEME_BLOCK_DARK = '@theme {'
const THEME_BLOCK_LIGHT = ':root:not(.dark) {'

const PHASE10_SECTIONS = [
  'Scope and non-goals',
  'QueueCard anatomy',
  'Status token table',
  'Card state precedence',
  'Primary action model',
  'Kebab menu',
  'Selection and bulk model',
  'Toolbar reduction',
  'Reorder model',
  'Empty state and drop targets',
  'Re-queue contract',
  'Supersession of 06-gui.md',
]

const SUPERSEDE_POINTER = 'Superseded for queue surfaces by docs/build-plan/10-queue-card-ui.md'

/** PORTED_TOKENS — dark/light hexes copied verbatim from PILL_TOKEN_SOURCE. */
const PORTED_TOKENS: Record<string, { dark: string; light: string }> = {
  '--color-status-pending': { dark: '#ffb86c', light: '#ea580c' },
  '--color-status-filled': { dark: '#50fa7b', light: '#16a34a' },
  '--color-status-rejected': { dark: '#ff5555', light: '#dc2626' },
  '--color-status-canceled': { dark: '#6272a4', light: '#64748b' },
}

/** Every token STATUS_PILL_TABLE names — av-kit must hold the PILL_TOKEN_SOURCE value for each. */
const STATUS_PILL_TOKENS = [
  '--color-status-pending',
  '--color-status-filled',
  '--color-status-rejected',
  '--color-status-canceled',
  '--color-accent-cyan',
  '--color-accent-yellow',
  '--color-accent-purple',
  '--color-accent-orange',
  '--color-accent-red',
]

const FORBIDDEN_SELECTION_FILL = 'bg-bg-subtle'
const SELECTION_FILL_ALLOWED = ['bg-accent/5', 'bg-accent/10']

const MATRIX_ROWS: Record<string, string> = {
  '10.1': 'MEU-41 canon-queue-cards',
  '10.2': 'MEU-42 svc-requeue-widening',
  '10.3': 'MEU-43 gui-queue-primitives',
  '10.4': 'MEU-44 gui-queue-card',
  '10.5': 'MEU-45 gui-convert-queue',
  '10.6': 'MEU-46 gui-downloader-queue',
  '10.7': 'MEU-47 gui-queue-bulk',
  '10.8': 'MEU-48 gui-queue-convergence',
  '10.9': 'MEU-49 gui-queue-dnd',
}

const PHASE10_MEU_IDS = [
  'MEU-41',
  'MEU-42',
  'MEU-43',
  'MEU-44',
  'MEU-45',
  'MEU-46',
  'MEU-47',
  'MEU-48',
  'MEU-49',
]

function readRepo(relative: string): string {
  const path = resolve(repoRoot, relative)
  expect(existsSync(path), `missing ${relative}`).toBe(true)
  return readFileSync(path, 'utf8')
}

/** Returns the declarations of one top-level CSS block, keyed by custom property. */
function themeTokens(css: string, opener: string): Record<string, string> {
  const start = css.indexOf(opener)
  expect(start, `missing block ${opener}`).toBeGreaterThan(-1)
  const end = css.indexOf('\n}', start)
  expect(end, `unterminated block ${opener}`).toBeGreaterThan(start)
  const body = css.slice(start + opener.length, end)
  const tokens: Record<string, string> = {}
  for (const match of body.matchAll(/^\s*(--color-[a-z0-9-]+)\s*:\s*([^;]+);/gm)) {
    tokens[match[1]] = match[2].trim()
  }
  return tokens
}

function headings(markdown: string): string[] {
  return markdown
    .split('\n')
    .filter((line) => /^#{1,4}\s/.test(line))
    .map((line) => line.replace(/^#{1,4}\s+/, '').trim())
}

/** Every source file under UI_ROOT, for the selection-fill scan. */
function uiSources(): { relative: string; text: string }[] {
  const roots = ['src/renderer/src']
  const files: { relative: string; text: string }[] = []
  const walk = (dir: string): void => {
    for (const entry of readdirSync(resolve(uiRoot, dir))) {
      const relative = `${dir}/${entry}`
      const absolute = resolve(uiRoot, relative)
      if (statSync(absolute).isDirectory()) {
        walk(relative)
      } else if (/\.(ts|tsx|css)$/.test(entry)) {
        files.push({ relative, text: readFileSync(absolute, 'utf8') })
      }
    }
  }
  for (const root of roots) walk(root)
  return files
}

describe('Phase 10 queue-card canon (MEU-41)', () => {
  it('AC-41.1 canon exists and carries every Phase 10 section heading', () => {
    const canon = readRepo(PHASE10_SPEC)
    const present = headings(canon)
    const missing = PHASE10_SECTIONS.filter(
      (section) => !present.some((heading) => heading.includes(section)),
    )
    expect(missing, 'PHASE10_SECTIONS missing from canon').toEqual([])
  })

  it('AC-41.2 06-gui.md keeps both superseded blocks and annotates each with the pointer', () => {
    const gui = readRepo(GUI_SPEC)
    expect(gui, 'DataTable spec deleted').toContain('### DataTable')
    expect(gui, 'DataTable body deleted').toContain('TanStack Table wrapper')
    expect(gui, 'Queue Controls spec deleted').toContain('### Queue Controls')
    expect(gui, 'Queue Controls body deleted').toContain('Clear All')

    for (const anchor of ['### DataTable', '### Queue Controls']) {
      const start = gui.indexOf(anchor)
      const window = gui.slice(start, start + 1200)
      expect(window, `${anchor} lacks SUPERSEDE_POINTER`).toContain(SUPERSEDE_POINTER)
    }
  })

  it('AC-41.3 both themes declare the ported status tokens with Zorivest hexes', () => {
    expect(existsSync(PILL_TOKEN_SOURCE), `missing PILL_TOKEN_SOURCE ${PILL_TOKEN_SOURCE}`).toBe(
      true,
    )
    const source = readFileSync(PILL_TOKEN_SOURCE, 'utf8')
    const sourceDark = themeTokens(source, THEME_BLOCK_DARK)
    const sourceLight = themeTokens(source, THEME_BLOCK_LIGHT)

    const css = readRepo(TOKEN_FILE)
    const dark = themeTokens(css, THEME_BLOCK_DARK)
    const light = themeTokens(css, THEME_BLOCK_LIGHT)

    for (const [token, expected] of Object.entries(PORTED_TOKENS)) {
      expect(sourceDark[token], `PILL_TOKEN_SOURCE dark ${token}`).toBe(expected.dark)
      expect(sourceLight[token], `PILL_TOKEN_SOURCE light ${token}`).toBe(expected.light)
      expect(dark[token], `${TOKEN_FILE} dark ${token}`).toBe(expected.dark)
      expect(light[token], `${TOKEN_FILE} light ${token}`).toBe(expected.light)
    }

    for (const token of STATUS_PILL_TOKENS) {
      expect(dark[token], `${token} dark diverges from PILL_TOKEN_SOURCE`).toBe(sourceDark[token])
      expect(light[token], `${token} light diverges from PILL_TOKEN_SOURCE`).toBe(sourceLight[token])
    }
  })

  it('AC-41.4 selection fill never reuses bg-bg-subtle and canon names the allowed fills', () => {
    const canon = readRepo(PHASE10_SPEC)
    expect(canon, 'canon does not forbid FORBIDDEN_SELECTION_FILL').toContain(
      FORBIDDEN_SELECTION_FILL,
    )
    for (const fill of SELECTION_FILL_ALLOWED) {
      expect(canon, `canon omits allowed selection fill ${fill}`).toContain(fill)
    }

    const offenders = uiSources()
      .flatMap(({ relative, text }) =>
        text
          .split('\n')
          .map((line, index) => ({ relative, index, line }))
          .filter(
            ({ line }) =>
              line.includes(FORBIDDEN_SELECTION_FILL) &&
              /selected|isSelected|active|isActive/.test(line),
          ),
      )
      .map(({ relative, index }) => `${relative}:${index + 1}`)
    expect(offenders, 'selection state paired with FORBIDDEN_SELECTION_FILL').toEqual([])
  })

  it('AC-41.5 AgeRestricted uses the Spec pill token', () => {
    // Rewritten by MOUNT_GATE_SCRIPT clause 6 (MEU-46): the downloader's rival
    // STATUS_COLORS map died with its table, so the token is read from the
    // single statement that survives -- the shared status-tokens the card
    // renders. The pinned value is unchanged.
    expect(QUEUE_PILL_TOKENS.AgeRestricted.fillClass).toBe('bg-accent-red/10')
    expect(QUEUE_PILL_TOKENS.AgeRestricted.fillClass).not.toContain('pink')
  })

  it('AC-41.6 canon records every user lock, including all Clear-finished clauses', () => {
    const canon = readRepo(PHASE10_SPEC)
    const locks: [string, RegExp][] = [
      ['bulk_bar_placement', /sticky[^.\n]{0,80}above the list/i],
      ['remove_confirm', /verb-labeled confirm/i],
      ['remove_confirm undo deferred', /undo[^.\n]{0,60}deferred/i],
      ['drag_and_drop deferred', /drag[^.\n]{0,60}deferred to MEU-49/i],
      ['density_toggle', /single density|no density toggle/i],
      ['per_card_cancel label', /Cancel queue/],
      ['per_card_cancel scope', /POST \/\{queue\}\/cancel/],
      ['per_card_cancel no per-item api', /no per-item cancel/i],
      ['clear_finished snapshot', /snapshot[^.\n]{0,120}before the first request/i],
      ['clear_finished independence', /each[^.\n]{0,60}independent/i],
      ['clear_finished continue_on_failure', /never abort/i],
      ['clear_finished successes_are_kept', /never rolled back/i],
      ['clear_finished files', /files stay on disk|never delete media from disk/i],
      ['clear_finished reconcile', /exactly one list refetch/i],
      ['clear_finished report', /removed count/i],
      ['clear_finished reason per failure', /reason per failure/i],
      ['retry_scope widened', /Cancelled[^.\n]{0,80}QualityBlocked[^.\n]{0,80}AgeRestricted/],
      ['retry_scope skipped excluded', /Skipped[^.\n]{0,60}excluded/i],
    ]
    const missing = locks.filter(([, pattern]) => !pattern.test(canon)).map(([label]) => label)
    expect(missing, 'USER_LOCKS clauses missing from canon').toEqual([])
  })

  it('AC-41.7 canon records the re-queue contract, pause scope, bulk policy and non-goals', () => {
    const canon = readRepo(PHASE10_SPEC)
    const clauses: [string, RegExp][] = [
      ['REQUEUEABLE_DOWNLOAD_STATUSES', /Failed[^.\n]{0,90}Cancelled[^.\n]{0,90}QualityBlocked/],
      ['REQUEUEABLE_CONVERSION_STATUSES', /conversion[^.\n]{0,120}Cancelled/i],
      ['PAUSE_SCOPE', /queue-level only/i],
      ['PAUSE_SCOPE no per-item pause', /no per-item pause/i],
      ['BULK_ENDPOINT_POLICY', /client-side fan-out/i],
      ['BULK_ENDPOINT_POLICY no bulk endpoint', /no[^.\n]{0,40}bulk endpoint/i],
      ['OUT_OF_SCOPE capture', /Capture inbox/i],
      ['OUT_OF_SCOPE new endpoints', /new REST endpoints/i],
      ['OUT_OF_SCOPE per-item api', /per-item cancel or per-item pause/i],
      ['OUT_OF_SCOPE page migration', /page migration/i],
      ['OUT_OF_SCOPE selection model', /BulkActionBar/],
      ['OUT_OF_SCOPE dnd', /dnd-kit/i],
      ['OUT_OF_SCOPE undo toast', /undo-toast/i],
      ['OUT_OF_SCOPE virtualization', /virtualization/i],
    ]
    const missing = clauses.filter(([, pattern]) => !pattern.test(canon)).map(([label]) => label)
    expect(missing, 're-queue contract / non-goal clauses missing from canon').toEqual([])
  })

  it('AC-41.8 Phase 10 is registered across BUILD_PLAN, the matrix and the SSOT', () => {
    const hub = readRepo(BUILD_PLAN)
    expect(hub, 'AUTOGEN phase tracker missing Phase 10').toMatch(/\|\s*10 — Queue card UI\s*\|/)
    expect(hub, 'Build Phases table missing the Phase 10 row').toMatch(
      /\|\s*10\s*\|[^\n]*10-queue-card-ui\.md/,
    )
    expect(hub, 'Phase Specs table missing 10-queue-card-ui.md').toMatch(
      /\[10-queue-card-ui\.md\]\(build-plan\/10-queue-card-ui\.md\)/,
    )

    const matrix = readRepo(MATRIX)
    for (const [order, row] of Object.entries(MATRIX_ROWS)) {
      const [meu, slug] = row.split(' ')
      const pattern = new RegExp(
        `\\|\\s*${order.replace('.', '\\.')}\\s*\\|\\s*${meu}\\s*\\|\\s*\`${slug}\``,
      )
      expect(matrix, `matrix row ${order} (${row})`).toMatch(pattern)
    }

    const ssot = readRepo(SSOT)
    for (const id of PHASE10_MEU_IDS) {
      expect(ssot, `SSOT missing ${id}`).toContain(`row_key: ${id}`)
    }
  })
})
