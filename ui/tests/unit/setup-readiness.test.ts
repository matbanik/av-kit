import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { DatabaseSync } from 'node:sqlite'

import { describe, expect, it } from 'vitest'

import {
  defaultModelsDirectory,
  isDescriptorPresent,
  probeModelsDirWritable,
  probeSetupReadiness,
} from '../../src/main/setup-readiness'

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

  it('defaults models directory to app-data models', () => {
    expect(defaultModelsDirectory('C:/app-data').replace(/\\/g, '/')).toBe('C:/app-data/models')
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
