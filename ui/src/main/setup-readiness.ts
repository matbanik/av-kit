import { randomUUID } from 'node:crypto'
import {
  accessSync,
  constants,
  existsSync,
  readFileSync,
  rmSync,
  statSync,
  unlinkSync,
  writeFileSync,
} from 'node:fs'
import { homedir } from 'node:os'
import { dirname, join } from 'node:path'
import { DatabaseSync } from 'node:sqlite'

import { descriptorPath } from './backend-descriptor'

export type SetupReadinessResult = {
  descriptorPresent: boolean
  portOk: boolean
  modelsDirWritable: boolean
  logFilePath: string
}

export function isDescriptorPresent(descFile: string): boolean {
  try {
    if (!existsSync(descFile)) {
      return false
    }
    const raw = readFileSync(descFile, 'utf8').trim()
    if (raw.length === 0) {
      return false
    }
    const parsed = JSON.parse(raw) as { tombstone?: boolean }
    return parsed.tombstone !== true
  } catch {
    return false
  }
}

export function expandUserPath(raw: string): string {
  if (raw.startsWith('~/')) {
    return join(homedir(), raw.slice(2))
  }
  if (raw === '~') {
    return homedir()
  }
  return raw
}

/** The backend's `tts.models_directory` default in `settings.py` (D-326, D-328). */
export const DEFAULT_MODELS_DIRECTORY = '~/.avkit/models'

export function defaultModelsDirectory(): string {
  return expandUserPath(DEFAULT_MODELS_DIRECTORY)
}

export function consoleLogFilePath(appData: string): string {
  return join(appData, 'logs', 'console.log')
}

export function readTtsModelsDirectory(appData: string): string {
  const dbPath = join(appData, 'avkit.db')
  if (!existsSync(dbPath)) {
    return defaultModelsDirectory()
  }
  try {
    const db = new DatabaseSync(dbPath, { readOnly: true })
    try {
      const row = db
        .prepare('SELECT value FROM settings WHERE namespace = ? AND key = ?')
        .get('tts', 'models_directory') as { value?: string } | undefined
      if (row?.value !== undefined && row.value.trim().length > 0) {
        return expandUserPath(row.value.trim())
      }
    } finally {
      db.close()
    }
  } catch {
    // fall through to the backend's default
  }
  return defaultModelsDirectory()
}

/** `path` or its nearest existing ancestor, or null when none exists or one can't be read. */
function nearestExistingEntry(path: string): { path: string; isDirectory: boolean } | null {
  let current = path
  for (;;) {
    try {
      return { path: current, isDirectory: statSync(current).isDirectory() }
    } catch (error) {
      const code = (error as NodeJS.ErrnoException).code
      const parent = dirname(current)
      if ((code !== 'ENOENT' && code !== 'ENOTDIR') || parent === current) {
        return null
      }
      current = parent
    }
  }
}

export function probeModelsDirWritable(modelsDir: string): boolean {
  // A missing folder is not created (D-327): the backend makes it on its first write, so the
  // nearest existing folder above it is the one that must be writable.
  const existing = nearestExistingEntry(modelsDir)
  if (existing === null || !existing.isDirectory) {
    return false
  }
  const probe = join(existing.path, `.write-probe-${randomUUID()}`)
  try {
    writeFileSync(probe, 'ok', 'utf8')
    accessSync(existing.path, constants.W_OK)
    unlinkSync(probe)
    return true
  } catch {
    // A write can create the file and then fail, so a failed probe still removes it (D-342).
    try {
      rmSync(probe, { force: true })
    } catch {
      // The answer is already false.
    }
    return false
  }
}

export function probePortOk(getPublishedBackendReady: () => { apiBase: string } | null): boolean {
  const published = getPublishedBackendReady()
  if (published === null) {
    return false
  }
  try {
    const url = new URL(published.apiBase)
    const port = url.port === '' ? (url.protocol === 'https:' ? 443 : 80) : Number(url.port)
    return Number.isFinite(port) && port > 0
  } catch {
    return false
  }
}

export function probeSetupReadiness(input: {
  appData: string
  getPublishedBackendReady: () => { apiBase: string } | null
}): SetupReadinessResult {
  const descFile = descriptorPath(input.appData)
  const descriptorPresent = isDescriptorPresent(descFile)
  const portOk = probePortOk(input.getPublishedBackendReady)
  const modelsDir = readTtsModelsDirectory(input.appData)
  const modelsDirWritable = probeModelsDirWritable(modelsDir)
  return {
    descriptorPresent,
    portOk,
    modelsDirWritable,
    logFilePath: consoleLogFilePath(input.appData),
  }
}
