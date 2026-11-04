import { existsSync } from 'node:fs'
import { join } from 'node:path'

import { app, nativeImage, type NativeImage } from 'electron'

/**
 * Resolve a bundled app-icon asset (the rottiboo mascot).
 *
 * Dev/unpacked: `ui/build/<name>` relative to the compiled `out/main/` entry.
 * Packaged: `resources/<name>`, which `electron-builder.yml` populates via
 * `extraResources` — `build/` is not inside the asar, so the dev path does not
 * survive packaging.
 */
export function appIconPath(name: 'icon.ico' | 'icon.png'): string {
  if (app.isPackaged) {
    const packaged = join(process.resourcesPath, name)
    if (existsSync(packaged)) {
      return packaged
    }
  }
  return join(__dirname, '..', '..', 'build', name)
}

/**
 * Load the tray-sized mascot image. Returns an empty image when the asset is
 * missing so a packaging miss degrades to a blank tray slot instead of throwing
 * during startup.
 */
export function trayIconImage(size = 16): NativeImage {
  const path = appIconPath('icon.png')
  if (!existsSync(path)) {
    return nativeImage.createEmpty()
  }
  const image = nativeImage.createFromPath(path)
  if (image.isEmpty()) {
    return image
  }
  return image.resize({ width: size, height: size })
}
