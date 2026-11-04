import { describe, expect, it, vi } from 'vitest'

import {
  COPY_IMAGE_ENCODE_ERROR,
  COPY_IMAGE_FETCH_ERROR,
  toClipboardPng,
} from '../../src/renderer/src/features/capture/capture-clipboard'

const SIGNATURE = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]
const PNG = Uint8Array.from([...SIGNATURE, 0, 0, 0, 13, 0x49, 0x48, 0x44, 0x52])
// "RIFF....WEBP": a WebP header, which Electron's nativeImage cannot decode.
const WEBP = Uint8Array.from([0x52, 0x49, 0x46, 0x46, 4, 0, 0, 0, 0x57, 0x45, 0x42, 0x50])

describe('MEU-88 toClipboardPng (RENDERER_PNG)', () => {
  it('AC-88.4 PNG bytes come back unchanged without calling encode', async () => {
    const encode = vi.fn(async (_blob: Blob) => PNG)
    const out = await toClipboardPng(new Blob([PNG], { type: 'image/png' }), encode)
    expect(Array.from(out)).toEqual(Array.from(PNG))
    expect(encode).not.toHaveBeenCalled()
  })

  it('AC-88.4 a non-PNG blob goes to encode once and its PNG result is returned', async () => {
    const encoded = Uint8Array.from([...SIGNATURE, 1, 2, 3])
    const encode = vi.fn(async (_blob: Blob) => encoded)
    const blob = new Blob([WEBP], { type: 'image/webp' })
    const out = await toClipboardPng(blob, encode)
    expect(encode).toHaveBeenCalledTimes(1)
    expect(encode).toHaveBeenCalledWith(blob)
    expect(Array.from(out)).toEqual(Array.from(encoded))
  })

  it('AC-88.4 a null blob throws COPY_IMAGE_FETCH_ERROR', async () => {
    expect(COPY_IMAGE_FETCH_ERROR).toBe('the image could not be loaded')
    const encode = vi.fn(async (_blob: Blob) => PNG)
    await expect(toClipboardPng(null, encode)).rejects.toThrow('the image could not be loaded')
    expect(encode).not.toHaveBeenCalled()
  })

  it('AC-88.4 an encode result without PNG_SIGNATURE throws COPY_IMAGE_ENCODE_ERROR', async () => {
    expect(COPY_IMAGE_ENCODE_ERROR).toBe('the image could not be converted to PNG')
    const encode = vi.fn(async (_blob: Blob) => WEBP)
    await expect(toClipboardPng(new Blob([WEBP], { type: 'image/webp' }), encode)).rejects.toThrow(
      'the image could not be converted to PNG',
    )
  })
})
