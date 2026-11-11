import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it, vi } from 'vitest'

import { writePngToClipboard } from '../../src/main/clipboard-image'
import { handleIpc, listRegisteredChannels } from '../../src/main/ipc'
import { getPreloadApiKeys } from '../../src/main/preload'
import { RENDERER_TO_MAIN_CHANNELS } from './ipc-channels'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')

const SIGNATURE = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]
const PNG = Uint8Array.from([...SIGNATURE, 0, 0, 0, 13, 0x49, 0x48, 0x44, 0x52])

function freshEffects() {
  return { dialog: 0, fs: 0, clipboard: 0, spawn: 0 }
}

describe('MEU-88 write-clipboard-image IPC (IMAGE_HANDLER)', () => {
  it('AC-88.6 valid PNG bytes reach writeClipboardImage once and count one clipboard effect', async () => {
    const effects = freshEffects()
    const writeClipboardImage = vi.fn(async (_png: Uint8Array) => true)
    const result = await handleIpc('write-clipboard-image', { png: PNG }, { sideEffects: effects, writeClipboardImage })
    expect(result.ok).toBe(true)
    expect(writeClipboardImage).toHaveBeenCalledTimes(1)
    expect(Array.from(writeClipboardImage.mock.calls[0]?.[0] ?? [])).toEqual(Array.from(PNG))
    expect(effects.clipboard).toBe(1)
  })

  const oversized = new Uint8Array(64 * 1024 * 1024 + 1)
  oversized.set(SIGNATURE)
  const rejected: Array<[string, unknown]> = [
    ['a string', { png: 'x' }],
    ['a number array', { png: [137, 80] }],
    ['an ArrayBuffer', { png: new ArrayBuffer(8) }],
    ['empty bytes', { png: new Uint8Array(0) }],
    ['bytes over COPY_IMAGE_MAX_BYTES', { png: oversized }],
    ['bytes without PNG_SIGNATURE', { png: Uint8Array.from([0x52, 0x49, 0x46, 0x46, 0, 0, 0, 0, 0x57]) }],
    ['an extra key', { png: PNG, path: 'C:/x' }],
  ]
  it.each(rejected)('AC-88.6 %s is rejected before the dependency or any effect', async (_label, payload) => {
    const effects = freshEffects()
    const writeClipboardImage = vi.fn(async (_png: Uint8Array) => true)
    const result = await handleIpc('write-clipboard-image', payload, { sideEffects: effects, writeClipboardImage })
    expect(result.ok).toBe(false)
    expect(writeClipboardImage).not.toHaveBeenCalled()
    expect(effects).toEqual(freshEffects())
  })

  it('AC-88.6 an image the main process cannot decode, or no dependency, returns IMAGE_DECODE_ERROR', async () => {
    const declined = await handleIpc(
      'write-clipboard-image',
      { png: PNG },
      { sideEffects: freshEffects(), writeClipboardImage: async () => false },
    )
    expect(declined).toEqual({ ok: false, error: 'image could not be decoded' })
    const missing = await handleIpc('write-clipboard-image', { png: PNG }, { sideEffects: freshEffects() })
    expect(missing).toEqual({ ok: false, error: 'image could not be decoded' })
  })
})

describe('MEU-88 writePngToClipboard (MAIN_IMAGE_WRITE)', () => {
  it('AC-88.7 decodes exactly the given bytes and writes the decoded image once', () => {
    // A view into a larger buffer: only the viewed bytes may reach createFromBuffer.
    const backing = new Uint8Array(PNG.length + 8).fill(0xee)
    backing.set(PNG, 4)
    const view = backing.subarray(4, 4 + PNG.length)
    const image = { isEmpty: () => false }
    const createFromBuffer = vi.fn((_buffer: Buffer) => image)
    const writeImage = vi.fn()
    const ok = writePngToClipboard(view, {
      nativeImage: { createFromBuffer },
      clipboard: { writeImage },
    } as unknown as Parameters<typeof writePngToClipboard>[1])
    expect(ok).toBe(true)
    expect(createFromBuffer).toHaveBeenCalledTimes(1)
    const passed = createFromBuffer.mock.calls[0]?.[0] as Buffer
    expect(Buffer.isBuffer(passed)).toBe(true)
    expect(Array.from(passed)).toEqual(Array.from(PNG))
    expect(writeImage).toHaveBeenCalledTimes(1)
    expect(writeImage).toHaveBeenCalledWith(image)
  })

  it('AC-88.7 an empty decoded image returns false and never writes the clipboard', () => {
    const writeImage = vi.fn()
    const ok = writePngToClipboard(PNG, {
      nativeImage: { createFromBuffer: () => ({ isEmpty: () => true }) },
      clipboard: { writeImage },
    } as unknown as Parameters<typeof writePngToClipboard>[1])
    expect(ok).toBe(false)
    expect(writeImage).not.toHaveBeenCalled()
  })
})

describe('MEU-88 IMAGE_CHANNEL registration (PRELOAD_KEY)', () => {
  it('AC-88.8 the channel is registered, the census list has 20 entries, and preload invokes it with { png }', () => {
    const registered = listRegisteredChannels()
    expect(RENDERER_TO_MAIN_CHANNELS).toHaveLength(22)
    expect(registered).toEqual([...RENDERER_TO_MAIN_CHANNELS])
    expect(registered).toContain('write-clipboard-image')
    expect(getPreloadApiKeys()).toContain('writeClipboardImage')
    const preload = readFileSync(resolve(repoRoot, 'ui/src/main/preload.ts'), 'utf8')
    expect(preload).toMatch(
      /writeClipboardImage: \(png: Uint8Array\) => ipcRenderer\.invoke\('write-clipboard-image', \{ png \}\)/,
    )
  })
})
