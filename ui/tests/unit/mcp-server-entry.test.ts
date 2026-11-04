import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

import { mcpServerEntry } from '../../src/main/mcp-setup-prompt'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')

describe('MEU-71 SERVER_ENTRY (AC-71.5)', () => {
  it('AC-71.5 packaged returns resources/mcp-server/index.mjs; dev returns mcp-server/dist/index.js', () => {
    const resourcesPath = 'C:\\Program Files\\av-kit\\resources'
    expect(mcpServerEntry({ packaged: true, resourcesPath, dirname: 'C:\\ignored' })).toBe(
      join(resourcesPath, 'mcp-server', 'index.mjs'),
    )
    const dev = resolve(repoRoot, 'ui/out/main')
    expect(mcpServerEntry({ packaged: false, resourcesPath, dirname: dev })).toBe(
      resolve(dev, '../../../mcp-server/dist/index.js'),
    )
  })

  it('AC-71.5 negative: a dev dirname of <repo>/ui/out/main resolves to <repo>/mcp-server/dist/index.js; packaged never yields dist', () => {
    const dev = mcpServerEntry({ packaged: false, resourcesPath: '', dirname: join(repoRoot, 'ui', 'out', 'main') })
    expect(dev).toBe(join(repoRoot, 'mcp-server', 'dist', 'index.js'))
    for (const resourcesPath of ['C:\\av-kit\\resources', join(repoRoot, 'ui', 'dist', 'win-unpacked', 'resources')]) {
      const packaged = mcpServerEntry({ packaged: true, resourcesPath, dirname: join(repoRoot, 'ui', 'out', 'main') })
      expect(packaged.endsWith(join('mcp-server', 'index.mjs'))).toBe(true)
      expect(packaged.includes(join('mcp-server', 'dist'))).toBe(false)
    }
  })
})
