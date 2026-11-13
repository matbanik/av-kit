/** @vitest-environment node */

import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

const UI = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const MODULE = '../../src/renderer/src/features/capture/capture-flatten'

type FlattenModule = {
  applyState: (input: {
    selected: boolean
    savedCount: number
    currentCount: number
    dirty: boolean
    canSave: boolean
    confirmOpen: boolean
    originalPath: string
  }) => { enabled: boolean; title: string | undefined }
  revertState: (input: { dirty: boolean; confirmOpen: boolean }) => { enabled: boolean; title: string | undefined }
  flattenConfirmText: (input: {
    displayName: string
    originalPath: string
    backupEnabled: boolean
    backupDir: string
  }) => string
  revertConfirmText: (displayName: string, backupPath: string) => string
  flattenStatus: (
    outcome:
      | { kind: 'flatten'; backupBefore: string | null; backupAfter: string | null }
      | { kind: 'convert'; displayName: string }
      | { kind: 'revert'; backupPath: string },
  ) => string
}

/** Loads the pure module; a missing module fails as an assertion, not a collection error. */
async function load(): Promise<FlattenModule> {
  const mod = (await import(/* @vite-ignore */ MODULE).catch(() => null)) as FlattenModule | null
  expect(mod, 'capture-flatten.ts exports the APPLY_ENABLED rules').not.toBeNull()
  return mod as FlattenModule
}

const READY = {
  selected: true,
  savedCount: 2,
  currentCount: 2,
  dirty: false,
  canSave: true,
  confirmOpen: false,
  originalPath: 'C:/inbox/a.png',
}

describe('MEU-67 APPLY_ENABLED and REVERT_VISIBLE rules', () => {
  it('AC-67.20 Apply is enabled for PNG, JPEG and WebP shots with saved marks and a clean overlay', async () => {
    const { applyState } = await load()
    for (const originalPath of ['C:/inbox/a.png', 'C:/inbox/b.PNG', 'C:/inbox/c.jpg', 'C:/inbox/d.JPEG', 'C:/inbox/e.webp']) {
      expect(applyState({ ...READY, originalPath }), originalPath).toEqual({ enabled: true, title: undefined })
    }
  })

  it('AC-67.20 each disabled reason names the first unmet rule in order', async () => {
    const { applyState } = await load()
    expect(applyState({ ...READY, savedCount: 0 })).toEqual({ enabled: false, title: 'Save marks first' })
    // SAVE_AND_FLATTEN (MEU-104): a dirty overlay counts its current marks and needs canSave.
    expect(applyState({ ...READY, savedCount: 0, currentCount: 0, dirty: true })).toEqual({ enabled: false, title: 'Save marks first' })
    expect(applyState({ ...READY, dirty: true, canSave: false })).toEqual({ enabled: false, title: 'Save annotations first' })
    expect(applyState({ ...READY, dirty: true, canSave: false, originalPath: 'C:/inbox/a.bmp' })).toEqual({
      enabled: false,
      title: 'Save annotations first',
    })
    expect(applyState({ ...READY, dirty: true, originalPath: 'C:/inbox/a.bmp' })).toEqual({
      enabled: false,
      title: 'This file type cannot be flattened',
    })
    expect(applyState({ ...READY, savedCount: 0, dirty: true })).toEqual({ enabled: true, title: undefined })
    expect(applyState({ ...READY, originalPath: 'C:/inbox/a.bmp' })).toEqual({
      enabled: false,
      title: 'This file type cannot be flattened',
    })
    expect(applyState({ ...READY, confirmOpen: true }).enabled).toBe(false)
    expect(applyState({ ...READY, selected: false }).enabled).toBe(false)
  })

  it('AC-67.23 Revert is disabled while dirty or while a confirm strip is open', async () => {
    const { revertState } = await load()
    expect(revertState({ dirty: false, confirmOpen: false })).toEqual({ enabled: true, title: undefined })
    expect(revertState({ dirty: true, confirmOpen: false })).toEqual({
      enabled: false,
      title: 'Save or discard unsaved marks first',
    })
    expect(revertState({ dirty: false, confirmOpen: true }).enabled).toBe(false)
  })
})

describe('MEU-67 confirm and status texts', () => {
  it('AC-67.21 FLATTEN_CONFIRM_TEXT: PNG with backups on, default and custom folder', async () => {
    const { flattenConfirmText } = await load()
    const base = { displayName: 'a.png', originalPath: 'C:/inbox/a.png', backupEnabled: true }
    expect(flattenConfirmText({ ...base, backupDir: '' })).toBe(
      'Bake the saved marks into a.png? The original is copied to the backup folder in the inbox first.',
    )
    expect(flattenConfirmText({ ...base, backupDir: '  ' })).toBe(
      'Bake the saved marks into a.png? The original is copied to the backup folder in the inbox first.',
    )
    expect(flattenConfirmText({ ...base, backupDir: 'D:/backups' })).toBe(
      'Bake the saved marks into a.png? The original is copied to D:/backups first.',
    )
  })

  it('AC-67.21 FLATTEN_CONFIRM_TEXT: PNG with backups off, and a JPEG/WebP shot', async () => {
    const { flattenConfirmText } = await load()
    expect(
      flattenConfirmText({ displayName: 'a.png', originalPath: 'C:/inbox/a.png', backupEnabled: false, backupDir: '' }),
    ).toBe('Bake the saved marks into a.png? Backups are off, so this cannot be undone.')
    for (const name of ['photo.jpg', 'photo.JPEG', 'photo.webp']) {
      expect(
        flattenConfirmText({ displayName: name, originalPath: `C:/inbox/${name}`, backupEnabled: false, backupDir: '' }),
      ).toBe(`Bake the saved marks into a new PNG copy of ${name}? ${name} itself stays unchanged.`)
    }
  })

  it('AC-67.23 REVERT_CONFIRM_TEXT names the backup by its basename', async () => {
    const { revertConfirmText } = await load()
    expect(revertConfirmText('a.png', 'C:\\inbox\\.avkit-backup\\a.20261003-120000.png')).toBe(
      'Replace a.png with its newest backup (a.20261003-120000.png)? The current image is overwritten.',
    )
    expect(revertConfirmText('a.png', '/home/u/inbox/.avkit-backup/a.20261003-120000_1.png')).toBe(
      'Replace a.png with its newest backup (a.20261003-120000_1.png)? The current image is overwritten.',
    )
  })

  it('AC-67.22 AC-67.33 FLATTEN_STATUS for each outcome', async () => {
    const { flattenStatus } = await load()
    expect(flattenStatus({ kind: 'flatten', backupBefore: null, backupAfter: 'C:/b/a.1.png' })).toBe(
      'Flattened into image. Backup: C:/b/a.1.png',
    )
    expect(flattenStatus({ kind: 'flatten', backupBefore: 'C:/b/a.1.png', backupAfter: 'C:/b/a.2.png' })).toBe(
      'Flattened into image. Backup: C:/b/a.2.png',
    )
    // Backups off: no new backup, even when an older one is still the newest.
    expect(flattenStatus({ kind: 'flatten', backupBefore: 'C:/b/a.1.png', backupAfter: 'C:/b/a.1.png' })).toBe(
      'Flattened into image (no backup).',
    )
    expect(flattenStatus({ kind: 'flatten', backupBefore: null, backupAfter: null })).toBe('Flattened into image (no backup).')
    expect(flattenStatus({ kind: 'convert', displayName: 'photo-converted.png' })).toBe(
      'Flattened into a new PNG copy: photo-converted.png.',
    )
    expect(flattenStatus({ kind: 'revert', backupPath: 'C:\\b\\a.20261003-120000.png' })).toBe(
      'Restored from a.20261003-120000.png.',
    )
  })
})

describe('MEU-67 test ids (AC-67.26)', () => {
  const IDS = [
    'capture-apply-image',
    'capture-revert-image',
    'capture-flatten-confirm',
    'capture-flatten-confirm-cancel',
    'capture-revert-confirm',
    'capture-revert-confirm-cancel',
    'settings-leaf-flatten_backup',
    'settings-leaf-capture-backup_dir',
    'settings-capture-backup-browse',
    'settings-leaf-annotated_format',
  ]

  it('AC-67.26 NEW_TESTIDS sit after the MEU-66 block, once each, and the MEU-51 prefix holds', () => {
    const registry = readFileSync(resolve(UI, 'tests/e2e/test-ids.ts'), 'utf8')
    const [prefix, tail] = registry.split('// MEU-51 primitive harness IDs.')
    expect(tail, 'MEU-51 marker present').toBeDefined()
    const afterMeu66 = (tail ?? '').split('// MEU-66 Capture viewport zoom (additive IDs).')[1] ?? ''
    const block = afterMeu66.split('// MEU-67 Capture flatten and revert (additive IDs).')[1] ?? ''
    expect(block.length, 'MEU-67 block after the MEU-66 block').toBeGreaterThan(0)
    const page = readFileSync(resolve(UI, 'src/renderer/src/features/capture/CapturePage.tsx'), 'utf8')
    const settings = readFileSync(resolve(UI, 'src/renderer/src/features/settings/SettingsPage.tsx'), 'utf8')
    for (const id of IDS) {
      expect(block, id).toContain(`= '${id}'`)
      expect(prefix, id).not.toContain(`'${id}'`)
      expect(registry.split(`'${id}'`).length - 1, `${id} registered once`).toBe(1)
      expect(page + settings, id).toContain(id)
    }
  })
})
