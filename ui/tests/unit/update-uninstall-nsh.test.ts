// Session 106 (MEU-174) UNINSTALL_CACHE_RECURSIVE, AC-174.14: in `customUnInstall` the updater
// cache is removed with `RMDir /r` and the two sign-in `DeleteRegValue HKCU` lines sit inside
// the `${ifNot} ${isUpdated}` block, so an update keeps the entry and a real uninstall removes it.
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')
const nshPath = resolve(repoRoot, 'ui/build/installer.nsh')

const CACHE_LINE = 'RMDir /r "$LOCALAPPDATA\\av-kit-ui-updater"'
const RUN_DELETE = 'DeleteRegValue HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Run" "com.avkit.app"'
const APPROVED_DELETE =
  'DeleteRegValue HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\StartupApproved\\Run" "com.avkit.app"'
const GUARD_OPEN = '${ifNot} ${isUpdated}'

function nsisCodeLines(src: string): string[] {
  return src
    .split(/\r?\n/)
    .map((line) => {
      const semi = line.indexOf(';')
      return (semi >= 0 ? line.slice(0, semi) : line).trim()
    })
    .filter((line) => line.length > 0)
}

function macroBody(src: string, name: string): string[] {
  const lines = nsisCodeLines(src)
  const start = lines.indexOf(`!macro ${name}`)
  const end = lines.indexOf('!macroend', start)
  return start >= 0 && end > start ? lines.slice(start + 1, end) : []
}

// The lines inside `${ifNot} ${isUpdated}` ... its matching `${endIf}`, nested blocks included.
function notUpdatedBlock(body: string[]): string[] {
  const start = body.findIndex((line) => /^\$\{ifNot\}\s+\$\{isUpdated\}$/.test(line))
  if (start < 0) return []
  let depth = 1
  for (let i = start + 1; i < body.length; i++) {
    if (/^\$\{if(Not)?\}\s/i.test(body[i])) depth++
    if (/^\$\{endIf\}$/i.test(body[i]) && --depth === 0) return body.slice(start + 1, i)
  }
  return []
}

// Every way the uninstall macro can break UNINSTALL_CACHE_RECURSIVE; an empty list is a pass.
function problems(src: string): string[] {
  const body = macroBody(src, 'customUnInstall')
  const block = notUpdatedBlock(body)
  const found: string[] = []
  const blockRmdirs = block.filter((line) => /^RMDir\b/i.test(line))
  if (blockRmdirs.length !== 1 || blockRmdirs[0] !== CACHE_LINE) {
    found.push(`not-updated block RMDir lines ${JSON.stringify(blockRmdirs)}`)
  }
  const bodyRmdirs = body.filter((line) => /^RMDir\b/i.test(line))
  if (bodyRmdirs.length !== blockRmdirs.length) found.push('an RMDir outside the not-updated block')
  for (const line of [RUN_DELETE, APPROVED_DELETE]) {
    if (block.filter((l) => l === line).length !== 1) found.push(`not in the block once: ${line}`)
  }
  const bodyDeletes = body.filter((line) => /^DeleteRegValue\b/i.test(line))
  const blockDeletes = block.filter((line) => /^DeleteRegValue\b/i.test(line))
  if (bodyDeletes.length !== blockDeletes.length) found.push('a DeleteRegValue outside the not-updated block')
  return found
}

function fixture(lines: string[]): string {
  return ['!macro customUnInstall', ...lines.map((l) => `  ${l}`), '!macroend'].join('\n')
}

const GOOD = [
  GUARD_OPEN,
  '  Delete "$LOCALAPPDATA\\${APP_INSTALLER_STORE_FILE}"',
  `  ${CACHE_LINE}`,
  `  ${RUN_DELETE}`,
  `  ${APPROVED_DELETE}`,
  '${endIf}',
]

describe('MEU-174 UNINSTALL_CACHE_RECURSIVE', () => {
  it('AC-174.14 the not-updated block holds the recursive cache line once and both DeleteRegValue lines', () => {
    expect(problems(fixture(GOOD)), 'the good fixture').toEqual([])
    const nsh = readFileSync(nshPath, 'utf8')
    expect(problems(nsh)).toEqual([])
    const block = notUpdatedBlock(macroBody(nsh, 'customUnInstall'))
    expect(block.filter((line) => line === CACHE_LINE)).toHaveLength(1)
    expect(nsisCodeLines(nsh).filter((line) => /^DeleteRegValue\b/.test(line))).toHaveLength(2)
  })

  it('AC-174.14 [neg] the cache line outside the guard, a second recursive delete, or the sign-in lines before the guard each fail', () => {
    const outside = fixture([CACHE_LINE, ...GOOD.filter((l) => l.trim() !== CACHE_LINE)])
    expect(problems(outside).length, 'cache line outside the guard').toBeGreaterThan(0)
    const second = fixture([...GOOD.slice(0, 3), '  RMDir /r "$LOCALAPPDATA\\av-kit"', ...GOOD.slice(3)])
    expect(problems(second).length, 'a second recursive delete').toBeGreaterThan(0)
    const today = fixture([
      RUN_DELETE,
      APPROVED_DELETE,
      GUARD_OPEN,
      '  Delete "$LOCALAPPDATA\\${APP_INSTALLER_STORE_FILE}"',
      `  ${CACHE_LINE}`,
      '${endIf}',
    ])
    expect(problems(today).length, 'the DeleteRegValue lines before the guard, as today').toBeGreaterThan(0)
  })
})
