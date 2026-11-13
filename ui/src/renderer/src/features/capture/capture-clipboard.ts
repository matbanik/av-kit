import { parseAnnotateBody, type Annotation } from './capture-annotate'
import { fetchAuthorizedBlob, postAuthorizedBlob } from './capture-image'

/** The 8-byte PNG file signature (W3C PNG §5.2). */
export const PNG_SIGNATURE = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a] as const

export const COPY_IMAGE_FETCH_ERROR = 'the image could not be loaded'
export const COPY_IMAGE_ENCODE_ERROR = 'the image could not be converted to PNG'
export const COPY_IMAGE_UNAVAILABLE = 'copying images is not available in this window'
export const COPY_IMAGE_MARKS_ERROR = 'the current marks could not be read'

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

/**
 * COPY_IMAGE_SOURCE plus RENDERER_PNG: the shot's file as PNG bytes. FILMSTRIP_AS_SHOWN
 * (MEU-104, D-677 A): the caller asks for `annotated` when the shot has an annotated file.
 */
export async function loadClipboardPng(
  id: string,
  variant: 'original' | 'annotated' = 'original',
): Promise<Uint8Array> {
  const blob = await fetchAuthorizedBlob(`/captures/${encodeURIComponent(id)}/image?variant=${variant}`)
  return toClipboardPng(blob, encodePng)
}

/** RENDER_CLIENT (MEU-104): the shot baked with `annotations` by the render route, as PNG bytes. */
export async function renderClipboardPng(id: string, annotations: readonly Annotation[]): Promise<Uint8Array> {
  const body = parseAnnotateBody({ annotations })
  if (body === null) {
    throw new Error(COPY_IMAGE_MARKS_ERROR)
  }
  const blob = await postAuthorizedBlob(`/captures/${encodeURIComponent(id)}/render`, body)
  return toClipboardPng(blob, encodePng)
}

/** A rejected `ipcRenderer.invoke` prefixes the main-process message; keep only that message. */
export function copyErrorMessage(caught: unknown): string {
  const raw = caught instanceof Error ? caught.message : String(caught)
  return raw.replace(/^Error invoking remote method '[^']+': (?:Error: )?/, '')
}
