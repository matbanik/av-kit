import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const uiRoot = resolve(__dirname, '../..')

function read(relative: string): string {
  return readFileSync(resolve(uiRoot, relative), 'utf8')
}

describe('rottiboo app icon wiring', () => {
  it('ships the build assets the window, tray, and installer read', () => {
    expect(existsSync(resolve(uiRoot, 'build/icon.ico')), 'build/icon.ico').toBe(true)
    expect(existsSync(resolve(uiRoot, 'build/icon.png')), 'build/icon.png').toBe(true)
    expect(
      existsSync(resolve(uiRoot, 'src/renderer/src/assets/rottiboo.png')),
      'renderer brand mark',
    ).toBe(true)
  })

  it('icon.ico carries the six Windows shell sizes', () => {
    // ICONDIR header: reserved(2) type(2) count(2), then 16-byte ICONDIRENTRYs
    // whose first two bytes are width/height (0 meaning 256).
    const ico = readFileSync(resolve(uiRoot, 'build/icon.ico'))
    expect(ico.readUInt16LE(2), 'ICO resource type').toBe(1)
    const count = ico.readUInt16LE(4)
    const sizes = Array.from({ length: count }, (_, i) => {
      const width = ico.readUInt8(6 + i * 16)
      return width === 0 ? 256 : width
    })
    expect(sizes.sort((a, b) => a - b)).toEqual([16, 32, 48, 64, 128, 256])
  })

  it('the main window and tray resolve their icon through app-icon.ts', () => {
    const appIcon = read('src/main/app-icon.ts')
    expect(appIcon).toContain('process.resourcesPath')
    expect(appIcon).toContain("join(__dirname, '..', '..', 'build', name)")

    expect(read('src/main/index.ts')).toContain("icon: appIconPath('icon.ico')")

    const tray = read('src/main/capture-tray.ts')
    expect(tray).toContain('new Tray(trayIconImage())')
    expect(tray, 'tray no longer starts blank').not.toContain('nativeImage.createEmpty()')
  })

  it('electron-builder packages the icon for the exe and for resourcesPath', () => {
    const builder = read('electron-builder.yml')
    expect(builder).toContain('icon: build/icon.ico')
    expect(builder).toMatch(/- from: build\/icon\.png\s+to: icon\.png/)
    expect(builder).toMatch(/- from: build\/icon\.ico\s+to: icon\.ico/)
  })

  it('the header renders the mark in the upper-left breadcrumb', () => {
    const header = read('src/renderer/src/components/layout/Header.tsx')
    expect(header).toContain("import rottibooMark from '../../assets/rottiboo.png'")
    expect(header).toMatch(/header-breadcrumb__mark[\s\S]*src=\{rottibooMark\}/)
    // Decorative: the adjacent "av-kit" brand text already names the app.
    expect(header).toMatch(/header-breadcrumb__mark[\s\S]*aria-hidden="true"/)
    expect(read('src/renderer/src/styles.css')).toContain('.header-breadcrumb__mark {')
  })
})
