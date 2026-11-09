// Session 57 (a copy of Session 44's AC-110.15 smoke, version rc.2): the installed app launches,
// reaches its backend and renders a page.
// Usage: node packaged-app-smoke.mjs <install-root> <result.json> <screenshot.png>
// Launches the real av-kit.exe through Playwright, with no AVKIT_E2E, so main runs as a user's does.
// AVKIT_APP_DATA must name an empty folder: this keeps the run away from the real app data.
// Exit 0 means every check passed, 1 that one failed, 2 that the script refused to launch.
import { mkdirSync, readdirSync, writeFileSync } from 'node:fs'
import { createRequire } from 'node:module'
import { dirname, join, resolve, sep } from 'node:path'
import { fileURLToPath } from 'node:url'

const LAUNCH_TIMEOUT_MS = 120_000
const CLOSE_TIMEOUT_MS = 60_000
const RETRY_MS = 1_000
const RC_VERSION = '0.1.0-rc.2'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../../../..')
const require = createRequire(join(repoRoot, 'ui', 'package.json'))
const { _electron } = require('@playwright/test')

const [installRoot, resultPath, screenshotPath] = process.argv.slice(2)
const appData = process.env.AVKIT_APP_DATA
if (!installRoot || !resultPath || !screenshotPath) {
  console.error('usage: packaged-app-smoke.mjs <install-root> <result.json> <screenshot.png>')
  process.exit(2)
}
if (!appData) {
  console.error('refused: AVKIT_APP_DATA is not set')
  process.exit(2)
}
mkdirSync(appData, { recursive: true })
if (readdirSync(appData).length > 0) {
  console.error(`refused: AVKIT_APP_DATA is not empty: ${appData}`)
  process.exit(2)
}

const sameOrInside = (path, folder) => {
  const a = resolve(path).toLowerCase()
  const b = resolve(folder).toLowerCase()
  return a === b || a.startsWith(b + sep)
}

// The renderer's own route: the preload bridge for the address and token, then fetch. The token
// stays in the page, and only the status and a few fields come back.
const askBackend = async (page) =>
  page.evaluate(async () => {
    const [base, token] = await Promise.all([window.api.getBackendUrl(), window.api.getToken()])
    const response = await fetch(`${base}/health/dependencies`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    const body = await response.json()
    return {
      base,
      status: response.status,
      ffmpegPath: body.ffmpeg?.path ?? null,
      ffmpegAvailable: body.ffmpeg?.available ?? false,
    }
  })

const reachBackend = async (page) => {
  const deadline = Date.now() + LAUNCH_TIMEOUT_MS
  for (;;) {
    try {
      return await askBackend(page)
    } catch (error) {
      if (Date.now() >= deadline) {
        throw error
      }
      await new Promise((done) => setTimeout(done, RETRY_MS))
    }
  }
}

const exe = join(installRoot, 'av-kit.exe')
const env = { ...process.env }
for (const name of Object.keys(env)) {
  if (name === 'ELECTRON_RUN_AS_NODE' || name.startsWith('AVKIT_E2E')) {
    delete env[name]
  }
}

const result = { exe, appData, passed: false, errors: [], pageErrors: [] }
const check = (ok, message) => {
  if (!ok) {
    result.errors.push(message)
  }
}

let app
try {
  app = await _electron.launch({ executablePath: exe, args: [], env, timeout: LAUNCH_TIMEOUT_MS })
  const page = await app.firstWindow({ timeout: LAUNCH_TIMEOUT_MS })
  page.on('pageerror', (error) => result.pageErrors.push(String(error)))
  const responses = []
  page.on('response', (response) => {
    const url = new URL(response.url())
    if (url.hostname === '127.0.0.1' && url.pathname.startsWith('/api/v1/')) {
      responses.push({ path: url.pathname, status: response.status() })
    }
  })

  result.main = await app.evaluate(({ app: electronApp }) => ({
    isPackaged: electronApp.isPackaged,
    version: electronApp.getVersion(),
    userData: electronApp.getPath('userData'),
    execPath: process.execPath,
  }))
  check(result.main.isPackaged, 'the app does not report itself as packaged')
  check(result.main.version === RC_VERSION, `app version is ${result.main.version}`)
  check(sameOrInside(result.main.userData, appData), `userData is ${result.main.userData}`)
  check(sameOrInside(result.main.execPath, installRoot), `running ${result.main.execPath}`)

  result.backend = await reachBackend(page)
  check(result.backend.status === 200, `backend answered ${result.backend.status}`)
  check(result.backend.ffmpegAvailable, 'backend reports FFmpeg unavailable')
  check(
    result.backend.ffmpegPath !== null && sameOrInside(result.backend.ffmpegPath, installRoot),
    `backend uses FFmpeg at ${result.backend.ffmpegPath}`,
  )

  // From here on, only the app's own requests count: the probe above must not stand in for them.
  responses.length = 0
  await page.getByTestId('nav-settings').click({ timeout: LAUNCH_TIMEOUT_MS })
  await page.waitForURL(/#\/settings/, { timeout: LAUNCH_TIMEOUT_MS })
  await page.getByTestId('settings-page').waitFor({ state: 'visible', timeout: LAUNCH_TIMEOUT_MS })
  const ownRequest = (entry) => entry.path === '/api/v1/health/dependencies' && entry.status === 200
  const deadline = Date.now() + LAUNCH_TIMEOUT_MS
  while (!responses.some(ownRequest) && Date.now() < deadline) {
    await new Promise((done) => setTimeout(done, RETRY_MS))
  }
  check(responses.some(ownRequest), 'the Settings page got no 200 from /health/dependencies')
  // The link also shows while the query loads, so it only proves something after the response.
  await page.getByTestId('readiness-ffmpeg-link').waitFor({ state: 'detached', timeout: 10_000 })
  await page.getByTestId('deps-ffprobe-row').waitFor({ state: 'visible', timeout: 10_000 })
  result.page = await page.evaluate(() => ({
    hash: window.location.hash,
    textLength: document.body.innerText.length,
    mentionsFfmpeg: document.body.innerText.includes('FFmpeg available'),
  }))
  result.appResponses = responses.length
  result.appResponseErrors = responses.filter((entry) => entry.status >= 400)
  check(result.page.textLength > 200, `the page rendered ${result.page.textLength} characters`)
  check(result.page.mentionsFfmpeg, 'the Settings page does not show its FFmpeg readiness row')
  check(result.appResponseErrors.length === 0, 'the Settings page got an API error')
  await page.screenshot({ path: screenshotPath })
  check(result.pageErrors.length === 0, `page errors: ${result.pageErrors.join(' | ')}`)
} catch (error) {
  result.errors.push(`${error.name}: ${error.message}`)
} finally {
  if (app) {
    const closed = app.close().then(
      () => true,
      (error) => {
        result.errors.push(`close: ${error.name}: ${error.message}`)
        return false
      },
    )
    const timedOut = new Promise((done) => setTimeout(() => done(false), CLOSE_TIMEOUT_MS))
    result.closed = await Promise.race([closed, timedOut])
    check(result.closed, `the app did not close within ${CLOSE_TIMEOUT_MS} ms`)
  }
}

result.appDataEntries = readdirSync(appData).sort()
check(result.appDataEntries.length > 0, 'the app wrote nothing into AVKIT_APP_DATA')
result.passed = result.errors.length === 0
writeFileSync(resultPath, JSON.stringify(result, null, 2))
console.log(JSON.stringify(result, null, 2))
console.log(`${result.passed ? 'PASS' : 'FAIL'}: packaged-app-smoke`)
process.exit(result.passed ? 0 : 1)
