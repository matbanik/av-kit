import { existsSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../..')
const captureDir = resolve(repoRoot, 'ui/src/renderer/src/features/capture')
const pagePath = resolve(captureDir, 'CapturePage.tsx')
const filmstripPath = resolve(captureDir, 'CaptureFilmstrip.tsx')
const viewportPath = resolve(captureDir, 'CaptureViewport.tsx')
const catalogPath = resolve(captureDir, 'useCaptureCatalog.ts')
const commandsPath = resolve(captureDir, 'capture-commands.ts')
const helpPath = resolve(captureDir, 'capture-help-content.ts')
const annotatePath = resolve(captureDir, 'capture-annotate.ts')
const settingsHookPath = resolve(captureDir, 'useCaptureSettings.ts')
const routerPath = resolve(repoRoot, 'ui/src/renderer/src/router.tsx')
const appShellPath = resolve(repoRoot, 'ui/src/renderer/src/components/layout/AppShell.tsx')
const navPath = resolve(repoRoot, 'ui/src/renderer/src/components/layout/NavRail.tsx')
const headerPath = resolve(repoRoot, 'ui/src/renderer/src/components/layout/Header.tsx')
const registryPath = resolve(repoRoot, 'ui/src/renderer/src/registry/commandRegistry.ts')
const helpCardPath = resolve(repoRoot, 'ui/src/renderer/src/components/help/HelpCard.tsx')
const settingsPagePath = resolve(repoRoot, 'ui/src/renderer/src/features/settings/SettingsPage.tsx')
const settingsSchemasPath = resolve(repoRoot, 'ui/src/renderer/src/features/settings/settings-schemas.ts')
const settingsPathsPath = resolve(repoRoot, 'ui/src/renderer/src/features/settings/settings-paths.ts')
const formGuardPath = resolve(repoRoot, 'ui/src/renderer/src/styles/form-guard.css')
const ipcPath = resolve(repoRoot, 'ui/src/main/ipc.ts')
const preloadPath = resolve(repoRoot, 'ui/src/main/preload.ts')
const indexMainPath = resolve(repoRoot, 'ui/src/main/index.ts')
const pickerMainPath = resolve(repoRoot, 'ui/src/main/capture-picker.ts')
const notifyMainPath = resolve(repoRoot, 'ui/src/main/notify-user.ts')
const hotkeyMainPath = resolve(repoRoot, 'ui/src/main/capture-hotkey.ts')
const trayMainPath = resolve(repoRoot, 'ui/src/main/capture-tray.ts')
const watchMainPath = resolve(repoRoot, 'ui/src/main/capture-inbox-watch.ts')
const registerMainPath = resolve(repoRoot, 'ui/src/main/capture-register.ts')
/** Mirrors OVERLAY_DELETED_FILES in named-sets.json (AC-40.9). */
const OVERLAY_DELETED_FILES = [
  'ui/src/main/capture-overlay.ts',
  'ui/src/main/overlay-preload.ts',
  'ui/src/main/overlay-rect.ts',
  'ui/src/main/overlay-page-target.ts',
  'ui/src/main/overlay-freeze-buffer.ts',
  'ui/src/renderer/overlay.html',
  'ui/src/renderer/src/overlay.ts',
  'ui/src/renderer/src/overlay-interaction.ts',
].map((rel) => resolve(repoRoot, rel))
const viteConfigPath = resolve(repoRoot, 'ui/electron.vite.config.ts')
const envDtsPath = resolve(repoRoot, 'ui/src/renderer/src/env.d.ts')
const guiAuditPath = resolve(here, 'gui-actions-audit.test.ts')
const ipcChannelsPath = resolve(here, 'ipc-channels.ts')
const testIdsPath = resolve(repoRoot, 'ui/tests/e2e/test-ids.ts')
const launchPath = resolve(repoRoot, 'ui/tests/e2e/launch.test.ts')
const e2ePath = resolve(repoRoot, 'ui/tests/e2e/capture-inbox.test.ts')
const e2eWiringPath = resolve(here, 'e2e-wiring.test.ts')
const shellHomePath = resolve(here, 'shell-home.test.ts')
const guiDocPath = resolve(repoRoot, 'docs/build-plan/06-gui.md')
const guiIndexPath = resolve(repoRoot, 'docs/build-plan/gui-actions-index.md')
const apiCapturesPath = resolve(repoRoot, 'packages/api/src/avkit_api/routes/captures.py')
const mcpDir = resolve(repoRoot, 'mcp-server')
const openapiPath = resolve(repoRoot, 'openapi.committed.json')

const WAVE9_TESTIDS = [
  'nav-capture',
  'capture-page',
  'capture-region',
  'capture-filmstrip',
  'capture-viewport',
  'capture-tool-arrow',
  'capture-save',
] as const

const WAVE9_EXTRA_TESTIDS = [
  'capture-tool-box',
  'capture-tool-highlight',
  'capture-tool-text',
  'capture-undo',
  'capture-redo',
  'capture-delete',
  'capture-open-file',
  'capture-open-folder',
  'capture-inbox-path',
  'capture-inbox-browse',
  'capture-hotkey',
  'capture-hotkey-change',
  'capture-status',
  'capture-empty',
  'capture-delete-confirm',
  'capture-delete-confirm-cancel',
  'capture-dirty-confirm',
  'capture-dirty-confirm-cancel',
  'capture-hotkey-banner',
  'capture-settings',
  'capture-settings-save',
  'settings-leaf-capture-inbox_dir',
  'settings-leaf-hotkey',
  'settings-leaf-copy_to_clipboard',
  'settings-leaf-close_to_tray',
  'browse-capture-path-btn',
  'capture-filmstrip-item',
  'capture-color',
  'capture-stroke',
] as const

const CAPTURE_PALETTE_IDS = ['nav:capture', 'capture:region', 'capture:save', 'capture:open_folder'] as const
const HELP_TOPICS = [
  'What Capture does',
  'F2 vs ShareX conflict',
  'inbox folder',
  'original vs .annotated.png',
  'annotation tools',
  'MCP can see the PNG',
  'close-to-tray keeps the hotkey',
  'never uploads',
] as const
const TRAY_MENU = ['Show window', 'Capture region', 'Open inbox folder', 'Quit'] as const
const PAGE_FILES = [
  pagePath,
  filmstripPath,
  viewportPath,
  catalogPath,
  commandsPath,
  helpPath,
  annotatePath,
  settingsHookPath,
] as const
const MAIN_FILES = [
  pickerMainPath,
  notifyMainPath,
  hotkeyMainPath,
  trayMainPath,
  watchMainPath,
  registerMainPath,
] as const

function readRequired(path: string): string {
  expect(existsSync(path), path).toBe(true)
  return readFileSync(path, 'utf8')
}

function captureSources(): string[] {
  return PAGE_FILES.map((path) => readRequired(path))
}

function mainCaptureSources(): string[] {
  return MAIN_FILES.map((path) => readRequired(path))
}

describe('MEU-39 capture gui', () => {
  it('AC-39.1 CAPTURE_HOME uses lazyRouteComponent without a static CapturePage import', () => {
    const src = readRequired(routerPath)
    expect(src).toMatch(/lazyRouteComponent/)
    expect(src).toMatch(/features\/capture\/CapturePage/)
    expect(src).toMatch(/pendingComponent:\s*ModuleSkeleton|ModuleSkeleton/)
    expect(src).not.toMatch(
      /import\s*\{\s*CapturePage\s*\}\s*from\s*['"]\.\/features\/capture\/CapturePage['"]/,
    )
    expect(src).toMatch(/import\s*\{\s*DownloaderPage\s*\}/)
    expect(src).toMatch(/lazyRouteComponent\(\(\) => import\('\.\/features\/converter\/ConvertPage'/)
    const page = readRequired(pagePath)
    expect(page).toContain('capture-page')
    expect(page).toMatch(/export function CapturePage/)
  })

  it('AC-39.2 NAV_CAPTURE is 5th primary after Convert and never POSTs on rail or Ctrl+5', () => {
    const nav = readRequired(navPath)
    expect(nav).toContain('nav-capture')
    expect(nav).toContain('nav:capture')
    expect(nav).toMatch(/Camera/)
    expect(nav).toMatch(/Ctrl\+5/)
    const primary = nav.match(/SHELL_PRIMARY_NAV[\s\S]+?\] as const/)
    expect(primary?.[0]).toMatch(/nav:convert[\s\S]+nav:capture/)
    expect(primary?.[0]).not.toMatch(/nav:capture[\s\S]+nav:convert/)
    expect(primary?.[0]).toMatch(/nav:convert/)
    expect(nav).toMatch(/onNavigate\?\.\(item\.path\)/)
    expect(nav).not.toMatch(/apiFetch|\/captures/)
    const shell = readRequired(appShellPath)
    expect(shell).toMatch(/createShortcutHandler/)
    expect(readRequired(registryPath)).toMatch(/navigateShell\(['"]\/capture['"]\)/)
    expect(shell).not.toMatch(/Ctrl\+5[\s\S]{0,200}capture:region/)
    const header = readRequired(headerPath)
    expect(header).toMatch(/PAGE_LABELS[\s\S]*'\/capture':\s*'Capture'/)
    const registry = readRequired(registryPath)
    expect(registry).toContain('nav:capture')
    expect(registry).toMatch(/shortcut:\s*'Ctrl\+5'/)
    expect(registry).toContain('nav:convert')
  })

  it('AC-39.3 CATALOG_ENVELOPE QUERY_KEY and poll skip processor', () => {
    const catalog = readRequired(catalogPath)
    expect(catalog).toMatch(/queryKey:\s*\[[\s\S]*captures/)
    expect(catalog).toMatch(/refetchInterval/)
    expect(catalog).toMatch(/1000/)
    expect(catalog).toMatch(/5000/)
    expect(catalog).toMatch(/items/)
    expect(catalog).not.toMatch(/processor/)
    expect(catalog).not.toMatch(/EventSource|text\/event-stream/)
    expect(catalog).toMatch(/captures:inbox-changed|inbox-changed/)
    expect(catalog).toMatch(/GET|\/captures/)
    const page = readRequired(pagePath)
    expect(page).not.toMatch(/data\.map\(/)
  })

  it('AC-39.4 inbox header Browse uses show-directory-dialog and G23 Save', () => {
    const page = readRequired(pagePath)
    expect(page).toContain('capture-inbox-path')
    expect(page).toContain('capture-inbox-browse')
    const sources = captureSources().join('\n')
    expect(sources).toMatch(/showDirectoryDialog|show-directory-dialog/)
    expect(sources).toMatch(/\/settings\/capture/)
    // Browse picks a folder. MEU-132's Import image… button is the one files dialog (09 §GUI image import).
    const inboxRow = page.slice(
      page.indexOf('id="capture-inbox-path-field"'),
      page.indexOf('browseTestId="capture-inbox-browse"'),
    )
    expect(inboxRow).toMatch(/showDirectoryDialog/)
    expect(inboxRow).not.toMatch(/showFilesDialog/)
    expect(sources.match(/showFilesDialog/g) ?? []).toHaveLength(1)
    expect(sources).toMatch(/showFilesDialog\(\[\{ name: 'Images'/)
    expect(readRequired(settingsHookPath)).toMatch(/\.strict\(\)|parseSettingsPut/)
  })

  it('AC-39.5 hotkey display recorder and in-use banner', () => {
    const page = readRequired(pagePath)
    expect(page).toContain('capture-hotkey')
    expect(page).toContain('capture-hotkey-change')
    expect(page).toContain('capture-hotkey-banner')
    expect(page).toMatch(/is in use — quit ShareX or pick another key/)
    const sources = captureSources().join('\n')
    expect(sources).toMatch(/get-hotkey-status|getHotkeyStatus/)
    expect(readRequired(hotkeyMainPath)).toMatch(/globalShortcut/)
    expect(readRequired(hotkeyMainPath)).not.toMatch(/from ['"]keyboard['"]/)
  })

  it('AC-39.6 Capture region invokes IPC_CAPTURE_REGION not FastAPI bbox', () => {
    const page = readRequired(pagePath)
    expect(page).toContain('capture-region')
    const commands = readRequired(commandsPath)
    expect(commands).toMatch(/capture-region/)
    expect(commands).not.toMatch(/mode:\s*['"]region['"]/)
    expect(commands).not.toMatch(/mss/)
    const sources = captureSources().join('\n')
    expect(sources).not.toMatch(/desktopCapturer/)
  })

  it('AC-39.7 filmstrip newest first blob thumbs never file protocol', () => {
    const film = readRequired(filmstripPath)
    expect(film).toContain('capture-filmstrip')
    expect(film).toContain('capture-filmstrip-item')
    expect(film).toMatch(/createObjectURL/)
    expect(film).toMatch(/revokeObjectURL/)
    expect(film).not.toMatch(/file:\/\//)
    expect(film).toMatch(/\/captures\/.+\/image|\/image/)
    expect(film).toMatch(/created_at|sort/)
    expect(film).toMatch(/bg-accent/)
    expect(film).not.toMatch(/openPath|open-path/)
  })

  it('AC-59.4 viewport SVG is image-space viewBox and never multiplies devicePixelRatio', () => {
    const viewport = readRequired(viewportPath)
    expect(viewport).toMatch(/viewBox/)
    expect(viewport).toMatch(/preserveAspectRatio/)
    expect(viewport).toMatch(/xMidYMid/)
    expect(viewport).not.toMatch(/devicePixelRatio/)
  })

  it('AC-39.8 viewport four tools undo redo stay off the picker', () => {
    const viewport = readRequired(viewportPath)
    expect(viewport).toContain('capture-viewport')
    expect(viewport).toContain('capture-tool-arrow')
    expect(viewport).toContain('capture-tool-box')
    expect(viewport).toContain('capture-tool-highlight')
    expect(viewport).toContain('capture-tool-text')
    expect(viewport).toContain('capture-tool-pixelate')
    expect(viewport).toContain('capture-tool-eraser')
    expect(viewport).toContain('capture-undo')
    expect(viewport).toContain('capture-redo')
    // The annotation tools live on the capture page only. The picker is a separate
    // process with no renderer at all, so the old 'not on the overlay window' half of
    // this assertion is proven by AC-40.9 instead.
    expect(readRequired(pickerMainPath)).not.toMatch(/capture-tool-arrow|ShapeManager/)
  })

  it('AC-39.9 Save annotate POSTs strict list and never bakes in renderer', () => {
    const annotate = readRequired(annotatePath)
    expect(annotate).toMatch(/\.strict\(\)/)
    expect(annotate).toMatch(/\/captures\/.+\/annotate|\/annotate/)
    expect(readRequired(pagePath)).toContain('capture-save')
    const sources = captureSources().join('\n')
    expect(sources).not.toMatch(/writeFileSync|createWriteStream/)
  })

  it('AC-39.10 dirty-thumb G20 portal confirm without window.confirm', () => {
    const sources = captureSources().join('\n')
    expect(sources).toContain('capture-dirty-confirm')
    expect(sources).toContain('capture-dirty-confirm-cancel')
    expect(sources).not.toMatch(/window\.confirm/)
  })

  it('AC-39.11 Delete G20 confirm then DELETE files', () => {
    const sources = captureSources().join('\n')
    expect(sources).toContain('capture-delete-confirm')
    expect(sources).toContain('capture-delete-confirm-cancel')
    expect(sources).toMatch(/method:\s*['"]DELETE['"]|apiFetch\([^)]*DELETE/)
    expect(sources).not.toMatch(/window\.confirm/)
    expect(readRequired(pagePath)).toContain('capture-delete')
  })

  it('AC-39.12 open file and folder use existing IPC and stay disabled without selection', () => {
    const page = readRequired(pagePath)
    expect(page).toContain('capture-open-file')
    expect(page).toContain('capture-open-folder')
    const sources = captureSources().join('\n')
    expect(sources).toMatch(/openPath|open-path/)
    expect(sources).toMatch(/showItemInFolder|show-item-in-folder/)
    expect(sources).toMatch(/disabled|toBeDisabled/)
  })

  it('AC-39.13 empty state HelpCard G26 topics and collapse key', () => {
    const page = readRequired(pagePath)
    expect(page).toContain('capture-empty')
    expect(page).toMatch(/Press F2 or Capture region/)
    // No drop zone as the primary path; MEU-132's page-wide drop handler shows none (09 :115, :1099).
    expect(page).not.toMatch(/drop-?zone/i)
    expect(page).toMatch(/feature=["']capture["']|feature=\{?'capture'\}?/)
    const help = readRequired(helpPath)
    for (const topic of HELP_TOPICS) {
      expect(help).toContain(topic)
    }
    const shell = readRequired(appShellPath)
    expect(shell).toMatch(/'\/capture'/)
    const helpCard = readRequired(helpCardPath)
    expect(helpCard).toMatch(/aria-expanded/)
    expect(helpCard).toMatch(/aria-controls/)
    expect(helpCard).toMatch(/av-kit:capture-help:|av-kit:\$\{?feature\}?-help:/)
  })

  it('AC-39.14 CAPTURE_PALETTE_IDS AppShell listener and RULE-3 navigate then deliver', () => {
    const registry = readRequired(registryPath)
    for (const id of CAPTURE_PALETTE_IDS) {
      expect(registry).toContain(id)
    }
    expect(registry).toMatch(/category:\s*'capture'/)
    const shell = readRequired(appShellPath)
    expect(shell).toMatch(/CAPTURE_COMMANDS|av-kit:capture:region/)
    expect(shell).toMatch(/requestAnimationFrame/)
    expect(shell).not.toMatch(/apiFetch\([^)]*\/captures/)
    const commands = readRequired(commandsPath)
    expect(commands).toMatch(/CAPTURE_EVENTS/)
    expect(commands).toMatch(/av-kit:capture:region/)
    expect(readRequired(guiIndexPath)).toMatch(/capture:open_folder[\s\S]{0,80}\| yes \|/)
  })

  it('AC-39.15 Settings Capture card G23 explicit Save not schedulePut', async () => {
    const settings = readRequired(settingsPagePath)
    expect(settings).toContain('capture-settings')
    expect(settings).toContain('capture-settings-save')
    expect(settings).toContain('settings-leaf-capture-inbox_dir')
    expect(settings).toContain('settings-leaf-hotkey')
    expect(settings).toContain('settings-leaf-copy_to_clipboard')
    expect(settings).toContain('settings-leaf-close_to_tray')
    expect(settings).toContain('browse-capture-path-btn')
    expect(settings).toMatch(/btn-save-dirty/)
    expect(settings).toMatch(/Save Changes •/)
    const hook = readRequired(settingsHookPath)
    expect(hook).not.toMatch(/schedulePut/)
    expect(hook).toMatch(/\/settings\/capture/)
    const schemas = readRequired(settingsSchemasPath)
    expect(schemas).toMatch(/capturePutSchema/)
    expect(schemas).toMatch(/inbox_dir/)
    const paths = readRequired(settingsPathsPath)
    expect(paths).toMatch(/capture:\s*'\/settings\/capture'/)
    expect(readRequired(formGuardPath)).toMatch(/btn-save-dirty/)
    const { parseSettingsPut } = await import('../../src/renderer/src/features/settings/settings-schemas')
    expect(() => parseSettingsPut('capture', { extra: true })).toThrow()
  })

  it('AC-39.16 tray menu labels and Quit sets QUIT_INTENT', () => {
    const tray = readRequired(trayMainPath)
    for (const label of TRAY_MENU) {
      expect(tray).toContain(label)
    }
    expect(tray).toMatch(/Tray/)
    expect(tray).toMatch(/isQuitting|QUIT_INTENT/)
    expect(tray).toMatch(/app\.quit/)
    expect(tray).not.toMatch(/window\.close\(\)/)
    expect(readRequired(indexMainPath)).toMatch(/capture-tray/)
  })

  it('AC-39.17 close-to-tray hide only when QUIT_INTENT is false', () => {
    const main = readRequired(indexMainPath)
    expect(main).toMatch(/isQuitting/)
    expect(main).toMatch(/close_to_tray|closeToTray/)
    expect(main).toMatch(/preventDefault/)
    expect(main).toMatch(/before-quit/)
    expect(main).toMatch(/hide\(/)
  })

  it('AC-39.18 globalShortcut register unregister lifetime without Python hook', () => {
    const hotkey = readRequired(hotkeyMainPath)
    expect(hotkey).toMatch(/globalShortcut\.register/)
    expect(hotkey).toMatch(/unregister/)
    expect(hotkey).not.toMatch(/keyboard/)
    expect(hotkey).not.toMatch(/python/)
    expect(readRequired(indexMainPath)).toMatch(/capture-hotkey/)
  })

  it('AC-39.21 write local timestamp PNG then register POST', () => {
    const register = readRequired(registerMainPath)
    expect(register).toMatch(/yyyy-MM-dd_HH-mm-ss/)
    expect(register).toMatch(/mode:\s*['"]register['"]/)
    expect(register).toMatch(/hotkey/)
    expect(register).toMatch(/gui/)
    expect(register).not.toMatch(/source:\s*['"]scan['"]/)
    expect(register).toMatch(/\/captures/)
    expect(register).toMatch(/guiNonce|Authorization|Bearer/)
  })

  it('AC-39.22 black-frame policy skips publication and register (picker path)', () => {
    const sources = readRequired(pickerMainPath) + readRequired(registerMainPath)
    expect(sources).toMatch(/Screen capture blocked/)
    expect(sources).toMatch(/\[Capture\]/)
    expect(sources).toMatch(/black|empty/)
    expect(readRequired(pickerMainPath)).toMatch(/inspectNativeImagePixels|isBlackOrEmptyBitmap/)
  })

  it('AC-39.23 inbox watcher skips annotated png and is not SSE', () => {
    const watch = readRequired(watchMainPath)
    expect(watch).toMatch(/fs\.watch|watch\(/)
    expect(watch).toMatch(/captures:inbox-changed/)
    expect(watch).toMatch(/annotated\.png/)
    expect(watch).not.toMatch(/EventSource|text\/event-stream/)
  })

  it('AC-39.24 interactive poll complete and cancel bodies', () => {
    const register = readRequired(registerMainPath)
    expect(register).toMatch(/500/)
    expect(register).toMatch(/\/captures\/requests\/.+\/complete|\/complete/)
    expect(register).toMatch(/\/cancel/)
    expect(register).not.toMatch(/from ['"].*features\/capture/)
  })

  it('AC-39.25 preload allowlist PRELOAD_LOCK stays minimal', () => {
    const preload = readRequired(preloadPath)
    expect(preload).toMatch(/capture-region/)
    expect(preload).toMatch(/get-hotkey-status/)
    expect(preload).toMatch(/captures:inbox-changed/)
    const main = readRequired(indexMainPath)
    expect(main).toMatch(/nodeIntegration:\s*false|createWebPreferences/)
    expect(main).toMatch(/contextIsolation:\s*true|sandbox:\s*true/)
    const ipc = readRequired(ipcPath)
    expect(ipc).toContain('capture-region')
    expect(ipc).toContain('get-hotkey-status')
    expect(readRequired(ipcChannelsPath)).toContain('capture-region')
    expect(readRequired(envDtsPath)).toMatch(/captureRegion|getHotkeyStatus|onInboxChanged/)
  })

  it('AC-39.26 Wave 9 capture-inbox E2E is written and wired with W9 cases', () => {
    expect(existsSync(pagePath), pagePath).toBe(true)
    const e2e = readRequired(e2ePath)
    for (const caseId of ['W9-1', 'W9-2', 'W9-3', 'W9-4', 'W9-5', 'W9-6']) {
      expect(e2e).toContain(caseId)
    }
    expect(e2e).toMatch(/page\.route/)
    expect(e2e).toMatch(/page\.on\('request'/)
    expect(e2e).toMatch(/capturePostCount/)
    expect(e2e).toMatch(/AVKIT_APP_DATA/)
    expect(e2e).toMatch(/getByTestId\('nav-capture'\)/)
    expect(e2e).toMatch(/capture:region/)
    const ids = readRequired(testIdsPath)
    for (const id of [...WAVE9_TESTIDS, ...WAVE9_EXTRA_TESTIDS]) {
      expect(ids).toContain(id)
    }
    const gui = readRequired(guiDocPath)
    expect(gui).toMatch(/\*\*42\*\*/)
  })

  it('AC-39.27 Wave0 shell and e2e-wiring include nav-capture and keep nav-convert', () => {
    expect(readRequired(launchPath)).toContain('nav-capture')
    expect(readRequired(launchPath)).toContain('nav-convert')
    expect(readRequired(e2eWiringPath)).toContain('capture-inbox.test.ts')
    expect(readRequired(e2eWiringPath)).toContain('nav-capture')
    expect(readRequired(shellHomePath)).toContain('nav:capture')
    expect(readRequired(shellHomePath)).toContain('nav-capture')
    expect(readRequired(navPath)).toContain('nav-capture')
    expect(readRequired(navPath)).toContain('nav-convert')
    expect(readRequired(registryPath)).toContain('nav:capture')
    expect(readRequired(guiAuditPath)).toMatch(/capture-/)
  })

  it('AC-39.28 G30-G35 G36 hold on capture sources with no skip or raw hex className', () => {
    const sources = captureSources().join('\n') + mainCaptureSources().join('\n')
    expect(sources).not.toMatch(/TODO|FIXME|NotImplementedError/)
    expect(sources).not.toMatch(/className=\{?[`'"][^`'"]*#[0-9a-fA-F]{3,8}/)
    expect(sources).not.toMatch(/duration-200|transition-all/)
    expect(sources).not.toMatch(/bg-blue-600/)
    expect(readRequired(pagePath)).toMatch(
      /variant=["']primary["'][\s\S]*capture-region|capture-region[\s\S]*variant=["']primary["']/,
    )
    expect(readRequired(pagePath)).toMatch(
      /variant=["']destructive["'][\s\S]*capture-delete|capture-delete[\s\S]*variant=["']destructive["']/,
    )
    const unit = readFileSync(resolve(here, 'capture-page.test.ts'), 'utf8')
    expect(unit).not.toMatch(/it\.skip|describe\.skip|test\.skip|it\.only|describe\.only|test\.only/)
    const vite = readRequired(viteConfigPath)
    expect(vite).toMatch(/\[name\]\.js/)
  })

  it('AC-39.30 complete and cancel extra keys never succeed and unknown id is 404', () => {
    const register = readRequired(registerMainPath)
    expect(register).toMatch(/\.strict\(\)|CaptureCompleteIn|empty/)
    expect(register).toMatch(/404/)
    expect(register).not.toMatch(/shot_id/)
    expect(existsSync(apiCapturesPath)).toBe(true)
    expect(existsSync(mcpDir)).toBe(true)
    expect(existsSync(openapiPath)).toBe(true)
    const api = readFileSync(apiCapturesPath, 'utf8')
    expect(api).toMatch(/complete|CaptureCompleteIn/)
  })

  // The behavioural AC-40.5 suite (tests/unit/capture-picker.test.ts) cannot report per-test
  // failures while the module is absent: vitest fails that file at collection, which prints the
  // importer path but no describe titles. This structural row carries the same criterion at a
  // level that survives a missing module, so a RED receipt still names AC-40.5.
  it('AC-40.5 the picker sidecar seam exists in the main process', () => {
    const picker = readRequired(pickerMainPath)
    expect(picker).toMatch(/PICKER_EXIT_CONFIRM/)
    expect(picker).toMatch(/PICKER_EXIT_CANCEL/)
    expect(picker).toMatch(/PICKER_EXIT_ERROR/)
    expect(picker).toMatch(/AVKIT_REGION_PICKER_PATH/)
    expect(picker).toMatch(/spawn\(/)
    expect(readRequired(notifyMainPath)).toMatch(/isPackaged/)
  })

  it('AC-40.9 the Chromium overlay is gone from ui/src', () => {
    for (const path of OVERLAY_DELETED_FILES) {
      expect(existsSync(path), path).toBe(false)
    }
    const survivors = [
      indexMainPath,
      preloadPath,
      ipcPath,
      pickerMainPath,
      notifyMainPath,
      hotkeyMainPath,
      trayMainPath,
      watchMainPath,
      registerMainPath,
    ]
    for (const path of survivors) {
      expect(readRequired(path)).not.toMatch(/desktopCapturer/)
    }
  })

  it('AC-40.14 the renderer surface is unchanged and vite carries no overlay input', () => {
    const preload = readRequired(preloadPath)
    expect(preload).toMatch(/capture-region/)
    expect(preload).toMatch(/captures:inbox-changed/)
    expect(readRequired(envDtsPath)).toMatch(/captureRegion/)
    expect(readRequired(pagePath)).toContain('capture-region')

    const vite = readRequired(viteConfigPath)
    expect(vite).not.toMatch(/overlay/)
    // The preload and renderer input maps must name `index` and nothing else.
    for (const block of vite.split(/input:/).slice(1)) {
      const map = block.slice(0, block.indexOf('}') + 1)
      expect(map).toMatch(/index/)
      expect(map).not.toMatch(/overlay/)
    }
  })
})

describe('MEU-67 capture settings schema (AC-67.24)', () => {
  const VALID = {
    inbox_dir: 'C:/Pictures/av-kit',
    hotkey: 'F2',
    copy_to_clipboard: false,
    close_to_tray: true,
    flatten_backup: true,
    backup_dir: '',
    annotated_format: 'png',
  }

  it('AC-67.24 capturePutSchema accepts the three new leaves with every format wire', async () => {
    const { parseSettingsPut } = await import('../../src/renderer/src/features/settings/settings-schemas')
    for (const annotated_format of ['png', 'jpeg', 'webp']) {
      expect(() => parseSettingsPut('capture', { ...VALID, annotated_format }), annotated_format).not.toThrow()
    }
    expect(parseSettingsPut('capture', { ...VALID, flatten_backup: false, backup_dir: 'D:/backups' })).toEqual({
      ...VALID,
      flatten_backup: false,
      backup_dir: 'D:/backups',
    })
  })

  it('AC-67.24 capturePutSchema rejects a non-boolean flatten_backup, a non-string backup_dir and a format outside the enum', async () => {
    const { parseSettingsPut } = await import('../../src/renderer/src/features/settings/settings-schemas')
    expect(() => parseSettingsPut('capture', { ...VALID, flatten_backup: 'yes' })).toThrow()
    expect(() => parseSettingsPut('capture', { ...VALID, backup_dir: 3 })).toThrow()
    expect(() => parseSettingsPut('capture', { ...VALID, annotated_format: 'gif' })).toThrow()
    expect(() => parseSettingsPut('capture', { ...VALID, annotated_format: 'jpg' })).toThrow()
  })

  it('AC-67.24 the Settings page Capture card and hook carry the three leaves', () => {
    const settings = readRequired(settingsPagePath)
    for (const id of [
      'settings-leaf-flatten_backup',
      'settings-leaf-capture-backup_dir',
      'settings-capture-backup-browse',
      'settings-leaf-annotated_format',
      'Back up the original before Apply to image',
      'Save overlay format',
    ]) {
      expect(settings, id).toContain(id)
    }
    const hook = readRequired(settingsHookPath)
    for (const leaf of ['flatten_backup', 'backup_dir', 'annotated_format']) {
      expect(hook, leaf).toContain(leaf)
    }
  })
})

describe('MEU-97 capture hints (AC-97.4)', () => {
  it('AC-97.4 HINTS capture-save passes its chord to ToolbarIconButton and capture-region carries its own', () => {
    const page = readRequired(pagePath)
    const saveAt = page.indexOf("spec={ACTION_BUTTONS['capture-save']}")
    expect(saveAt, 'capture-save button').toBeGreaterThan(-1)
    const save = page.slice(saveAt, page.indexOf('/>', saveAt))
    expect(save, 'capture-save shortcut prop').toContain('shortcut=')
    const regionAt = page.indexOf('data-testid="capture-region"')
    expect(regionAt, 'capture-region button').toBeGreaterThan(-1)
    const region = page.slice(regionAt, page.indexOf('Capture region', regionAt))
    expect(region, 'capture-region aria-keyshortcuts').toContain('aria-keyshortcuts=')
    expect(region, 'capture-region title').toContain('title=')
  })
})
