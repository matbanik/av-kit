import { existsSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')
const nshPath = resolve(repoRoot, 'ui/build/installer.nsh')
const ymlPath = resolve(repoRoot, 'ui/electron-builder.yml')
const LOGIN_ITEM_NAME = 'com.avkit.app'
const RUN_KEY = 'Software\\Microsoft\\Windows\\CurrentVersion\\Run'
const APPROVED_KEY = 'Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\StartupApproved\\Run'

function nsisCodeLines(src: string): string[] {
  return src
    .split(/\r?\n/)
    .map((line) => {
      const semi = line.indexOf(';')
      const code = (semi >= 0 ? line.slice(0, semi) : line).trim()
      return code
    })
    .filter((line) => line.length > 0)
}

describe('MEU-61 NSIS uninstall', () => {
  it('AC-61.18 NSH_FILE has two executable DeleteRegValue HKCU lines and nsis.include value', () => {
    const commentOnly = [
      `; customUnInstall DeleteRegValue HKCU`,
      `; ${RUN_KEY}`,
      `; ${APPROVED_KEY} ${LOGIN_ITEM_NAME}`,
      `!macro customUnInstall`,
      `  DeleteRegValue HKCU "${RUN_KEY}" "${LOGIN_ITEM_NAME}"`,
      `!macroend`,
    ].join('\n')
    const negDeletes = nsisCodeLines(commentOnly).filter((line) =>
      /^DeleteRegValue\s+HKCU\b/.test(line),
    )
    expect(negDeletes).toHaveLength(1)

    expect(existsSync(nshPath), nshPath).toBe(true)
    const nsh = readFileSync(nshPath, 'utf8')
    const deletes = nsisCodeLines(nsh).filter((line) => /^DeleteRegValue\s+HKCU\b/.test(line))
    expect(deletes).toHaveLength(2)
    expect(
      deletes.filter(
        (line) =>
          line.includes(RUN_KEY) &&
          line.includes(LOGIN_ITEM_NAME) &&
          !line.includes('StartupApproved'),
      ),
    ).toHaveLength(1)
    expect(
      deletes.filter((line) => line.includes(APPROVED_KEY) && line.includes(LOGIN_ITEM_NAME)),
    ).toHaveLength(1)

    const yml = readFileSync(ymlPath, 'utf8').split(/\r?\n/)
    let inNsis = false
    let includeVal: string | null = null
    for (const line of yml) {
      if (/^nsis:\s*$/.test(line)) {
        inNsis = true
        continue
      }
      if (inNsis && /^\S/.test(line)) inNsis = false
      const m = line.match(/^\s+include:\s*(.+)\s*$/)
      if (inNsis && m) includeVal = m[1].trim().replace(/^['"]|['"]$/g, '')
    }
    expect(includeVal).toBe('build/installer.nsh')
  })
})
