import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

import { describe, expect, it } from 'vitest'

const UNIT_ROOT = resolve(__dirname)
const PY_UNIT = resolve(__dirname, '../../../tests/unit/test_backend_cli.py')
const PY_INT = resolve(__dirname, '../../../tests/integration/test_backend_spawn.py')
const INDEX_HTML = resolve(__dirname, '../../src/renderer/index.html')

describe('AC-19.20 G36 / CSP_IMG / navigation deny', () => {
  it('forbids focused/skipped tests and requires CSP_IMG', async () => {
    const sources = [
      ...['single-instance.test.ts', 'live-identity.test.ts', 'ipc-strict-census.test.ts'].map((name) =>
        resolve(UNIT_ROOT, name),
      ),
      PY_UNIT,
      PY_INT,
    ]
    const deny = [
      ['it', 'skip'].join('.'),
      ['describe', 'skip'].join('.'),
      ['test', 'skip'].join('.'),
      ['it', 'todo'].join('.'),
      ['x', 'it('].join(''),
      ['x', 'describe('].join(''),
      ['it', 'only'].join('.'),
      ['describe', 'only'].join('.'),
      ['test', 'only'].join('.'),
      ['f', 'it('].join(''),
      ['f', 'describe('].join(''),
    ]
    for (const file of sources) {
      const text = readFileSync(file, 'utf8')
      for (const token of deny) {
        expect(text.includes(token), `${file} ${token}`).toBe(false)
      }
    }

    const { RENDERER_CSP, RENDERER_DEV_CSP, allowNavigation } = await import('../../src/main/index')
    expect(RENDERER_CSP).toMatch(/img-src[^;]*'self'/)
    expect(RENDERER_CSP).toMatch(/http:\/\/localhost:\*/)
    expect(RENDERER_CSP).toMatch(/http:\/\/127\.0\.0\.1:\*/)
    expect(RENDERER_CSP).toMatch(/data:/)
    expect(RENDERER_CSP).toMatch(/img-src[^;]*blob:/)
    expect(RENDERER_CSP).not.toMatch(/unsafe-eval/)
    expect(RENDERER_DEV_CSP).toMatch(/img-src[^;]*blob:/)
    expect(RENDERER_DEV_CSP).toMatch(/unsafe-eval/)
    expect(RENDERER_DEV_CSP).toMatch(/ws:\/\/127\.0\.0\.1:\*/)
    // Migrated from the retired overlay-hit-test spec (MEU-40): the renderer's CSP is set by
    // the main process per environment, so index.html must not pin a production-only one.
    expect(readFileSync(INDEX_HTML, 'utf8')).not.toMatch(/http-equiv=["']Content-Security-Policy["']/)
    expect(allowNavigation('https://example.com')).toBe(false)
    expect(allowNavigation('http://127.0.0.1:51234/api/v1/health')).toBe(false)
    const previousRenderer = process.env.ELECTRON_RENDERER_URL
    process.env.ELECTRON_RENDERER_URL = 'http://127.0.0.1:5173/'
    expect(allowNavigation('http://127.0.0.1:5173/')).toBe(true)
    expect(allowNavigation('http://127.0.0.1:5173/#/capture')).toBe(true)
    expect(allowNavigation('https://example.com')).toBe(false)
    if (previousRenderer === undefined) {
      delete process.env.ELECTRON_RENDERER_URL
    } else {
      process.env.ELECTRON_RENDERER_URL = previousRenderer
    }
  })
})
