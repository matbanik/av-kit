import {
  accessSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readdirSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from 'node:fs'
import { homedir, tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { DatabaseSync } from 'node:sqlite'
import { fileURLToPath } from 'node:url'

import { describe, expect, it, vi } from 'vitest'

import * as readiness from '../../src/main/setup-readiness'
import {
  isDescriptorPresent,
  probeModelsDirWritable,
  probeSetupReadiness,
  readTtsModelsDirectory,
} from '../../src/main/setup-readiness'

// The fault cases below replace one call; every other call runs the real function.
vi.mock('node:fs', async (importOriginal) => {
  const actual = await importOriginal<typeof import('node:fs')>()
  return { ...actual, accessSync: vi.fn(actual.accessSync), writeFileSync: vi.fn(actual.writeFileSync) }
})

const actualFs = await vi.importActual<typeof import('node:fs')>('node:fs')

function restoreFs(): void {
  vi.mocked(writeFileSync).mockReset().mockImplementation(actualFs.writeFileSync)
  vi.mocked(accessSync).mockReset().mockImplementation(actualFs.accessSync)
}

const REPO_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '../../..')
const BACKEND_DEFAULT = join(homedir(), '.avkit', 'models')

function createSettingsTable(db: DatabaseSync): void {
  db.exec(`
    CREATE TABLE settings (
      namespace TEXT NOT NULL,
      key TEXT NOT NULL,
      value TEXT NOT NULL,
      value_type TEXT NOT NULL,
      updated_at TEXT NOT NULL,
      PRIMARY KEY (namespace, key)
    );
  `)
}

describe('setup readiness producers', () => {
  it('rejects invalid JSON and tombstone descriptors', () => {
    const dir = mkdtempSync(join(tmpdir(), 'avkit-readiness-'))
    const desc = join(dir, 'backend.json')
    writeFileSync(desc, 'not-json', 'utf8')
    expect(isDescriptorPresent(desc)).toBe(false)

    writeFileSync(desc, '{"tombstone":true}\n', 'utf8')
    expect(isDescriptorPresent(desc)).toBe(false)

    writeFileSync(desc, '{"pid":1234}\n', 'utf8')
    expect(isDescriptorPresent(desc)).toBe(true)
    rmSync(dir, { recursive: true, force: true })
  })

  // Amended in Session 52 (MEU-120, D-326): the default is the backend's folder, not app data.
  it("AC-120.2 the default models folder is the backend's", () => {
    expect(readiness).toHaveProperty('DEFAULT_MODELS_DIRECTORY')
    expect(readiness.defaultModelsDirectory()).toBe(BACKEND_DEFAULT)
  })

  it('returns false when models path is a regular file', () => {
    const dir = mkdtempSync(join(tmpdir(), 'avkit-models-file-'))
    const filePath = join(dir, 'models')
    writeFileSync(filePath, 'not-a-directory', 'utf8')
    expect(probeModelsDirWritable(filePath)).toBe(false)
    rmSync(dir, { recursive: true, force: true })
  })

  it('probes writable directories', () => {
    const dir = mkdtempSync(join(tmpdir(), 'avkit-models-dir-'))
    expect(probeModelsDirWritable(dir)).toBe(true)
    rmSync(dir, { recursive: true, force: true })
  })

  it('reads models_directory from sqlite settings when present', () => {
    const appData = mkdtempSync(join(tmpdir(), 'avkit-readiness-db-'))
    mkdirSync(join(appData, 'models'), { recursive: true })
    writeFileSync(join(appData, 'backend.json'), '{"pid":1}\n', 'utf8')

    const db = new DatabaseSync(join(appData, 'avkit.db'))
    db.exec(`
      CREATE TABLE settings (
        namespace TEXT NOT NULL,
        key TEXT NOT NULL,
        value TEXT NOT NULL,
        value_type TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        PRIMARY KEY (namespace, key)
      );
    `)
    db.prepare(
      'INSERT INTO settings (namespace, key, value, value_type, updated_at) VALUES (?, ?, ?, ?, ?)',
    ).run('tts', 'models_directory', join(appData, 'models'), 'string', new Date().toISOString())
    db.close()

    const result = probeSetupReadiness({
      appData,
      getPublishedBackendReady: () => ({ apiBase: 'http://127.0.0.1:51234/api/v1' }),
    })
    expect(result.descriptorPresent).toBe(true)
    expect(result.portOk).toBe(true)
    expect(result.modelsDirWritable).toBe(true)
    expect(result.logFilePath.replace(/\\/g, '/')).toBe(`${appData.replace(/\\/g, '/')}/logs/console.log`)
    rmSync(appData, { recursive: true, force: true })
  })
})

// MEU-120 `gui-models-dir-probe` (Session 52, D-326 to D-328).
describe('setup readiness models folder', () => {
  it('AC-120.1 the default models folder is the backend setting default', () => {
    const settings = readFileSync(
      join(REPO_ROOT, 'packages/core/src/avkit_core/services/settings.py'),
      'utf8',
    )
    const match = /\("tts", "models_directory"\): SettingSpec\("string", "([^"]+)"\)/.exec(settings)
    expect(match?.[1]).toBe('~/.avkit/models')
    expect(readiness).toHaveProperty('DEFAULT_MODELS_DIRECTORY')
    expect(readiness.DEFAULT_MODELS_DIRECTORY).toBe(match?.[1])
  })

  it('AC-120.3 with no stored setting the models folder is the default', () => {
    const appData = mkdtempSync(join(tmpdir(), 'avkit-models-default-'))
    try {
      const noDatabase = readTtsModelsDirectory(appData)
      const db = new DatabaseSync(join(appData, 'avkit.db'))
      createSettingsTable(db)
      db.close()
      expect([noDatabase, readTtsModelsDirectory(appData)]).toEqual([BACKEND_DEFAULT, BACKEND_DEFAULT])
    } finally {
      rmSync(appData, { recursive: true, force: true })
    }
  })

  it('AC-120.4 a missing folder under a writable folder reads true and creates nothing', () => {
    const dir = mkdtempSync(join(tmpdir(), 'avkit-models-missing-'))
    try {
      const writable = probeModelsDirWritable(join(dir, 'a', 'models'))
      expect({ writable, intermediate: existsSync(join(dir, 'a')), entries: readdirSync(dir) }).toEqual({
        writable: true,
        intermediate: false,
        entries: [],
      })
    } finally {
      rmSync(dir, { recursive: true, force: true })
    }
  })

  it('AC-120.5 a missing folder under a regular file reads false and creates nothing', () => {
    const dir = mkdtempSync(join(tmpdir(), 'avkit-models-under-file-'))
    try {
      const file = join(dir, 'f')
      writeFileSync(file, 'not-a-directory', 'utf8')
      const writable = probeModelsDirWritable(join(file, 'models'))
      expect({ writable, entries: readdirSync(dir) }).toEqual({ writable: false, entries: ['f'] })
    } finally {
      rmSync(dir, { recursive: true, force: true })
    }
  })

  it('AC-120.6 an existing folder reads true and keeps no probe file', () => {
    const dir = mkdtempSync(join(tmpdir(), 'avkit-models-existing-'))
    try {
      const writable = probeModelsDirWritable(dir)
      expect({ writable, entries: readdirSync(dir) }).toEqual({ writable: true, entries: [] })
    } finally {
      rmSync(dir, { recursive: true, force: true })
    }
  })

  // Execution review round 1 F1 (D-340): a probe that fails after its write removes its file.
  it('AC-120.4 fault: a write that throws after creating the probe leaves no file', () => {
    const dir = mkdtempSync(join(tmpdir(), 'avkit-models-write-fault-'))
    try {
      vi.mocked(writeFileSync).mockImplementationOnce((file, data, options) => {
        actualFs.writeFileSync(file, data, options)
        throw Object.assign(new Error('ENOSPC: no space left on device, write'), { code: 'ENOSPC' })
      })
      const writable = probeModelsDirWritable(join(dir, 'a', 'models'))
      expect({ writable, entries: readdirSync(dir) }).toEqual({ writable: false, entries: [] })
    } finally {
      restoreFs()
      rmSync(dir, { recursive: true, force: true })
    }
  })

  it('AC-120.6 fault: a failed access check after the write keeps no probe file', () => {
    const dir = mkdtempSync(join(tmpdir(), 'avkit-models-access-fault-'))
    try {
      vi.mocked(accessSync).mockImplementationOnce(() => {
        throw Object.assign(new Error('EACCES: permission denied, access'), { code: 'EACCES' })
      })
      const writable = probeModelsDirWritable(dir)
      expect({ writable, entries: readdirSync(dir) }).toEqual({ writable: false, entries: [] })
    } finally {
      restoreFs()
      rmSync(dir, { recursive: true, force: true })
    }
  })
})
