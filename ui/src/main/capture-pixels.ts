export const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a])

export function isPngContainer(bytes: Buffer): boolean {
  return bytes.length >= 8 && bytes.subarray(0, 8).equals(PNG_SIGNATURE)
}

export function isBlackOrEmptyBitmap(bitmap: Buffer, width: number, height: number): boolean {
  if (isPngContainer(bitmap)) {
    throw new Error('PNG container passed; use toBitmap() raw pixels')
  }
  if (bitmap.length === 0 || width < 1 || height < 1) {
    return true
  }
  let nonzero = 0
  const step = Math.max(4, Math.floor(bitmap.length / 400) * 4)
  for (let i = 0; i < bitmap.length; i += step) {
    const r = bitmap[i] ?? 0
    const g = bitmap[i + 1] ?? 0
    const b = bitmap[i + 2] ?? 0
    if (r > 8 || g > 8 || b > 8) {
      nonzero += 1
    }
  }
  return nonzero === 0
}

export type NativeImageLike = {
  isEmpty: () => boolean
  getSize: () => { width: number; height: number }
  toBitmap: () => Buffer
}

export function inspectNativeImagePixels(image: NativeImageLike): {
  blocked: boolean
  width: number
  height: number
} {
  if (image.isEmpty()) {
    return { blocked: true, width: 0, height: 0 }
  }
  const size = image.getSize()
  const pixels = image.toBitmap()
  return {
    blocked: isBlackOrEmptyBitmap(pixels, size.width, size.height),
    width: size.width,
    height: size.height,
  }
}
