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

const pkgPath = resolve(repoRoot, 'ui/package.json')
const DELETE_COPY = 'Delete "$LOCALAPPDATA\\${APP_INSTALLER_STORE_FILE}"'

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

function updaterDir(): string {
  const pkg = JSON.parse(readFileSync(pkgPath, 'utf8')) as { name: string }
  return `${pkg.name}-updater`
}

describe('MEU-114 NSIS uninstall removes the installer copy', () => {
  it('AC-114.1 customUnInstall deletes the copy and its folder inside the not-updated guard', () => {
    const unguarded = [
      '!macro customUnInstall',
      `  ${DELETE_COPY}`,
      '  RMDir "$LOCALAPPDATA\\av-kit-ui-updater"',
      '!macroend',
    ].join('\n')
    expect(notUpdatedBlock(macroBody(unguarded, 'customUnInstall'))).toHaveLength(0)

    const block = notUpdatedBlock(macroBody(readFileSync(nshPath, 'utf8'), 'customUnInstall'))
    expect(block.filter((line) => line === DELETE_COPY)).toHaveLength(1)
    expect(block.filter((line) => /^RMDir\s+"\$LOCALAPPDATA\\[^"]+"$/.test(line))).toHaveLength(1)
  })

  it('AC-114.2 the folder RMDir removes is the package name plus -updater', () => {
    expect(updaterDir()).toBe('av-kit-ui-updater')
    const body = macroBody(readFileSync(nshPath, 'utf8'), 'customUnInstall')
    const rmdirs = body.filter((line) => /^RMDir\b/.test(line))
    expect(rmdirs).toEqual([`RMDir "$LOCALAPPDATA\\${updaterDir()}"`])
  })

  it('AC-114.3 the two DeleteRegValue lines stay the only two and no RMDir is recursive', () => {
    const lines = nsisCodeLines(readFileSync(nshPath, 'utf8'))
    expect(lines.filter((line) => /^DeleteRegValue\b/.test(line))).toHaveLength(2)
    expect(lines.filter((line) => /^RMDir\s+\/r\b/i.test(line))).toHaveLength(0)
  })
})
