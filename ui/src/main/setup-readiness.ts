import { randomUUID } from 'node:crypto'
import {
  accessSync,
  constants,
  existsSync,
  mkdirSync,
  readFileSync,
  statSync,
  unlinkSync,
  writeFileSync,
} from 'node:fs'
import { homedir } from 'node:os'
import { join } from 'node:path'
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

export function defaultModelsDirectory(appData: string): string {
  return join(appData, 'models')
}

export function consoleLogFilePath(appData: string): string {
  return join(appData, 'logs', 'console.log')
}

export function readTtsModelsDirectory(appData: string): string {
  const dbPath = join(appData, 'avkit.db')
  if (!existsSync(dbPath)) {
    return defaultModelsDirectory(appData)
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
    // fall through to app-data default
  }
  return defaultModelsDirectory(appData)
}

export function probeModelsDirWritable(modelsDir: string): boolean {
  try {
    const stat = statSync(modelsDir)
    if (!stat.isDirectory()) {
      return false
    }
  } catch {
    try {
      mkdirSync(modelsDir, { recursive: true })
    } catch {
      return false
    }
  }
  try {
    const probe = join(modelsDir, `.write-probe-${randomUUID()}`)
    writeFileSync(probe, 'ok', 'utf8')
    accessSync(modelsDir, constants.W_OK)
    unlinkSync(probe)
    return true
  } catch {
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
