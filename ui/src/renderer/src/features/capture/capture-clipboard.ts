import { fetchAuthorizedBlob } from './capture-image'

/** The 8-byte PNG file signature (W3C PNG §5.2). */
export const PNG_SIGNATURE = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a] as const

export const COPY_IMAGE_FETCH_ERROR = 'the image could not be loaded'
export const COPY_IMAGE_ENCODE_ERROR = 'the image could not be converted to PNG'
export const COPY_IMAGE_UNAVAILABLE = 'copying images is not available in this window'

function startsWithPng(bytes: Uint8Array): boolean {
  return PNG_SIGNATURE.every((byte, index) => bytes[index] === byte)
}

// Not every Blob implementation has arrayBuffer() (jsdom's does not); FileReader covers those.
async function blobBytes(blob: Blob): Promise<Uint8Array> {
  if (typeof blob.arrayBuffer === 'function') {
    return new Uint8Array(await blob.arrayBuffer())
  }
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      resolve(new Uint8Array(reader.result as ArrayBuffer))
    }
    reader.onerror = () => {
      reject(new Error(COPY_IMAGE_FETCH_ERROR))
    }
    reader.readAsArrayBuffer(blob)
  })
}

/**
 * RENDERER_PNG: the clipboard only takes PNG from the renderer, so PNG bytes pass through
 * unchanged and any other format goes through `encode`.
 */
export async function toClipboardPng(
  blob: Blob | null,
  encode: (blob: Blob) => Promise<Uint8Array>,
): Promise<Uint8Array> {
  if (blob === null) {
    throw new Error(COPY_IMAGE_FETCH_ERROR)
  }
  const bytes = await blobBytes(blob)
  if (startsWithPng(bytes)) {
    return bytes
  }
  const encoded = await encode(blob)
  if (!startsWithPng(encoded)) {
    throw new Error(COPY_IMAGE_ENCODE_ERROR)
  }
  return encoded
}

/** Production `encode`: decode the image and redraw it onto a PNG canvas. */
export async function encodePng(blob: Blob): Promise<Uint8Array> {
  let bitmap: ImageBitmap
  try {
    bitmap = await createImageBitmap(blob)
  } catch {
    throw new Error(COPY_IMAGE_ENCODE_ERROR)
  }
  try {
    const canvas = new OffscreenCanvas(bitmap.width, bitmap.height)
    const context = canvas.getContext('2d')
    if (context === null) {
      throw new Error(COPY_IMAGE_ENCODE_ERROR)
    }
    context.drawImage(bitmap, 0, 0)
    const png = await canvas.convertToBlob({ type: 'image/png' })
    return blobBytes(png)
  } finally {
    bitmap.close()
  }
}

/** COPY_IMAGE_SOURCE plus RENDERER_PNG: the shot's original file as PNG bytes. */
export async function loadClipboardPng(id: string): Promise<Uint8Array> {
  const blob = await fetchAuthorizedBlob(`/captures/${encodeURIComponent(id)}/image?variant=original`)
  return toClipboardPng(blob, encodePng)
}

/** A rejected `ipcRenderer.invoke` prefixes the main-process message; keep only that message. */
export function copyErrorMessage(caught: unknown): string {
  const raw = caught instanceof Error ? caught.message : String(caught)
  return raw.replace(/^Error invoking remote method '[^']+': (?:Error: )?/, '')
}
