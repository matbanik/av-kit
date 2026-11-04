/** @vitest-environment jsdom */

/**
 * MEU-50 FIC, written before the Phase 11 canon or token changes.
 * Sources: approved Session 23 plan AC-50.1–50.6, the six mockups §04–§06,
 * BUILD_PLAN Phase 11 composition lock, and the MEU-49 scroll carry-forward.
 */
import { existsSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

const repo = resolve(dirname(fileURLToPath(import.meta.url)), '../../..')
const plan = readFileSync(resolve(repo, 'docs/execution/plans/2026-09-26-p11-layout-canon/implementation-plan.md'), 'utf8')
const canonPath = resolve(repo, 'docs/build-plan/11-page-layout.md')
const groupingPath = resolve(repo, '.agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md')
const statusPath = resolve(repo, '.agent/context/meu-status.yaml')
const hubPath = resolve(repo, 'docs/BUILD_PLAN.md')
const cssPath = resolve(repo, 'ui/src/renderer/src/styles.css')

const mockups = [
  ['DL', 'downloader'],
  ['CV', 'convert'],
  ['TR', 'transcript'],
  ['TT', 'tts'],
  ['CP', 'capture'],
  ['ST', 'settings'],
] as const

function readIfExists(path: string): string {
  return existsSync(path) ? readFileSync(path, 'utf8') : ''
}

function section(markdown: string, title: string): string {
  const escaped = title.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const match = new RegExp(`^## ${escaped}\\s*$`, 'm').exec(markdown)
  if (!match) return ''
  const tail = markdown.slice(match.index + match[0].length)
  const next = /^## /m.exec(tail)
  return next ? tail.slice(0, next.index) : tail
}

function cells(line: string): string[] {
  return line.split(/(?<!\\)\|/).slice(1, -1).map((cell) =>
    cell.trim().replace(/\\\|/g, '|').replace(/`/g, ''),
  )
}

function decisionIds(): string[] {
  const definition = plan.split('\n').find((line) => line.startsWith('| `DECISION_SET` |')) ?? ''
  const spans = [...definition.matchAll(/([A-Z]{2})(\d+)–([A-Z]{2})(\d+)/g)]
  expect(spans).toHaveLength(6)
  return spans.flatMap(([, firstPrefix, first, lastPrefix, last]) => {
    expect(firstPrefix).toBe(lastPrefix)
    return Array.from({ length: Number(last) - Number(first) + 1 }, (_, offset) =>
      `${firstPrefix}${Number(first) + offset}`,
    )
  })
}

function sourceInventory(page: string): { label: string; disposition: string }[] {
  const html = readFileSync(resolve(repo, `docs/proposals/2026-09-03-${page}-page-layout-mockup.html`), 'utf8')
  const doc = new DOMParser().parseFromString(html, 'text/html')
  const heading = [...doc.querySelectorAll('h2')].find((node) =>
    node.querySelector('.sec')?.textContent?.trim() === '05',
  )
  let sibling = heading?.nextElementSibling
  while (sibling && !sibling.matches('table.inv') && !sibling.querySelector('table.inv')) {
    sibling = sibling.nextElementSibling
  }
  const table = sibling?.matches('table.inv') ? sibling : sibling?.querySelector('table.inv')
  expect(table, `${page} §05 inventory`).not.toBeNull()
  return [...(table?.querySelectorAll('tr') ?? [])].slice(1).map((row) => ({
    label: row.querySelector('td')?.textContent?.replace(/\s+/g, ' ').trim() ?? '',
    disposition: row.querySelector('td:last-child')?.textContent?.trim() ?? '',
  }))
}

describe('MEU-50 Phase 11 layout canon', () => {
  it('AC-50.1 records the full 37-decision register once with sections, basis and owner', () => {
    const canon = readIfExists(canonPath)
    const headings = [
      'Scope and non-goals', 'Decision register', 'Shared layout primitives',
      'Queue header row', 'Downloader page layout', 'Convert page layout',
      'Transcript page layout', 'TTS page layout', 'Capture page layout',
      'Settings page layout', 'Supersession', 'Test-ID migration', 'Verification',
    ]
    for (const title of headings) expect(canon, `missing ${title}`).toContain(`## ${title}`)

    const rows = section(canon, 'Decision register').split('\n')
      .filter((line) => /^\| (?:DL|CV|TR|TT|CP|ST)\d+ \|/.test(line))
      .map(cells)
    const expected = decisionIds()
    expect(rows).toHaveLength(37)
    expect(rows.map((row) => row[0]).sort()).toEqual([...expected].sort())
    for (const row of rows) {
      expect(row.length, row[0]).toBeGreaterThanOrEqual(5)
      expect(row[1]?.length, `${row[0]} choice`).toBeGreaterThan(15)
      expect(row[2], `${row[0]} source`).toMatch(/2026-09-03-.*-page-layout-mockup\.html.*§06/)
      expect(row[3], `${row[0]} owner`).toMatch(/^MEU-5[2-8]$/)
      expect(row[4]?.length, `${row[0]} test-ID effect`).toBeGreaterThan(5)
    }
  })

  it('AC-50.2 states the composition lock and keeps staged removal local to pre-Add state', () => {
    const canon = readIfExists(canonPath)
    expect(canon).toContain('COMPOSITION_LOCK')
    expect(canon).toMatch(/same IPC.*same API payloads.*persisted mutations.*enablement/s)
    expect(canon).toMatch(/CV1.*local pre-Add staging/s)
    expect(canon).toMatch(/CV1.*no API request/s)
    expect(canon).toMatch(/TR1.*three.*Start.*Pause\/Resume.*Stop/s)
    expect(canon).toContain('no new Clear finished mutation')
    expect(canon).toContain('No new API endpoint, persisted mutation, or enablement rule')
  })

  it('AC-50.3 preserves all four queue scroll-container clauses and both mockup sources', () => {
    const rule = section(readIfExists(canonPath), 'Queue scroll container rule')
    expect(rule).toContain('QUEUE_SCROLL_CONTAINER_RULE')
    expect(rule).toContain('h-full min-h-0')
    expect(rule).toContain('flex-1 min-h-[20rem]')
    expect(rule).toMatch(/overflow-auto.*wrapper around.*QueueList/s)
    expect(rule).toMatch(/controls.*min-h-0.*overflow-auto.*yield/s)
    expect(rule).toMatch(/shrink-0.*summary.*toolbar/s)
    expect(rule).toContain('2026-09-03-downloader-page-layout-mockup.html §04')
    expect(rule).toContain('2026-09-03-convert-page-layout-mockup.html §04')
    expect(rule).toContain('2026-09-03-p10-queue-card-dnd-reflection.md')
  })

  it('AC-50.4 accounts for every mockup §05 row, closed MEU-48 AC, and live TR1 source', () => {
    const canon = readIfExists(canonPath)
    const inventory = section(canon, 'Test-ID migration')
    expect(inventory).toContain('PRESERVED_TESTIDS')
    for (const [prefix, page] of mockups) {
      const sourceRows = sourceInventory(page)
      const mapped = inventory.split('\n').filter((line) => line.startsWith(`| ${prefix} |`)).map(cells)
      expect(mapped, `${page} inventory count`).toHaveLength(sourceRows.length)
      for (const [index, source] of sourceRows.entries()) {
        const row = mapped[index]
        expect(row[1], `${page} row ${index + 1} ordinal`).toBe(String(index + 1))
        expect(row[2]?.replace(/\s+/g, ' ').trim(), `${page} row ${index + 1} label`).toBe(source.label)
        expect(row[3], `${page} row ${index + 1} disposition`).toBe(source.disposition)
        expect(row[4], `${page} row ${index + 1} owner`).toMatch(/^MEU-5[2-8]$/)
      }
    }
    const supersession = section(canon, 'Supersession')
    expect(supersession).toMatch(/MEU-48.*MEU-55.*ChannelCard.*QueueCard/s)
    expect(supersession).toMatch(/MEU-48.*MEU-56.*ProgressBar/s)
    expect(supersession).toContain('width: %')
    const grouping = readIfExists(groupingPath)
    const status = readIfExists(statusPath)
    expect(grouping).toContain('three-action header toolbar')
    expect(grouping).not.toContain('4-slot header toolbar')
    expect(status).toContain('three-action header toolbar')
    expect(status).not.toContain('4-slot header toolbar')
  })

  it('AC-50.5 declares one column cap and one shared layout vocabulary', () => {
    const css = readIfExists(cssPath)
    const canon = readIfExists(canonPath)
    expect(css.match(/--layout-page-max-width:\s*72rem/g)).toHaveLength(1)
    expect(canon).toContain('--layout-page-max-width: 72rem')
    for (const term of ['zone', 'form grid', 'disclosure', 'segment', 'chip', 'save-model caption']) {
      expect(section(canon, 'Shared layout primitives').toLowerCase()).toContain(term)
    }
    expect(section(canon, 'Shared layout primitives')).not.toMatch(/transition-all|#[0-9a-f]{3,8}/i)
  })

  it('AC-50.6 resolves the existing hub links and replaces stale hand-written status', () => {
    const hub = readIfExists(hubPath)
    expect(existsSync(canonPath)).toBe(true)
    expect(hub).toContain('[11-page-layout.md](build-plan/11-page-layout.md)')
    expect(hub).toContain('Phase 11 page layout spec exists; page composition remains scheduled for MEU-52–58.')
    expect(hub).not.toContain('registered, not yet specced')
  })
})
