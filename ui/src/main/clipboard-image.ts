import type { clipboard, nativeImage } from 'electron'

export type ClipboardImageElectron = {
  nativeImage: Pick<typeof nativeImage, 'createFromBuffer'>
  clipboard: Pick<typeof clipboard, 'writeImage'>
}

// Decodes PNG bytes in main and puts the image on the system clipboard.
// Returns false, without touching the clipboard, when the bytes do not decode.
export function writePngToClipboard(png: Uint8Array, electron: ClipboardImageElectron): boolean {
  const image = electron.nativeImage.createFromBuffer(Buffer.from(png.buffer, png.byteOffset, png.byteLength))
  if (image.isEmpty()) {
    return false
  }
  electron.clipboard.writeImage(image)
  return true
}
