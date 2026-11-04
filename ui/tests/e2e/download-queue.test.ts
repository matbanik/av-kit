import { _electron, expect, test, type Locator, type Page } from '@playwright/test'
import { mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))

/**
 * MEU-46 rewrite (E2E_REWRITE_RULE).
 *
 * The downloader's 13 per-page toolbar ids are retired by the queue-card
 * migration. Every assertion that covered one of them is REPLACED here - never
 * deleted - by an assertion at the new home named in `RETIRED_TOOLBAR_CONTROLS`,
 * and each replacement satisfies `MOUNT_GATE_CLAUSE_4` (c)+(d): it locates the
 * home, PERFORMS the interaction, and asserts an observable outcome (the
 * intercepted request method+path+body, the renderer's IPC ledger, or the
 * resulting DOM state). A control that renders but is wired to nothing
 * therefore fails this spec.
 *
 * Home coverage in this file (16 MEU-46 homes of 13 retired ids):
 *   start-btn       -> queue-toolbar-start                     (W1-7)
 *   pause-btn       -> queue-toolbar-pause                     (W1-7)
 *   resume-btn      -> queue-toolbar-resume                    (W1-7)
 *   cancel-btn      -> in-flight card primary action           (W1-8)
 *   up-btn          -> kebab move-up / Alt+ArrowUp             (W1-7)
 *   down-btn        -> kebab move-down / Alt+ArrowDown         (W1-7)
 *   top-btn         -> kebab move-top                          (W1-7)
 *   bottom-btn      -> kebab move-bottom                       (W1-7)
 *   reset-btn       -> card primary action Retry               (W1-8)
 *   remove-btn      -> kebab remove                            (W1-9)
 *   clear-all-btn   -> queue-toolbar-overflow > clear-all      (W1-9)
 *   open-file-btn   -> kebab open-file / Done primary action   (W1-8)
 *   open-folder-btn -> kebab open-folder                       (W1-8)
 *
 * The ENABLED_WHEN chrome the retired buttons carried is rewritten onto the
 * surviving toolbar controls in W1-5, and AC-46.14's URL-intake empty state
 * (EMPTY_STATE_CONTRACT, downloader half) is exercised end to end in W1-10.
 */

type DownloadItem = {
  id: string
  url: string
  video_id: string
  title: string
  quality: string
  audio_only: boolean
  audio_format: string
  status: string
  progress: number
  speed: string | null
  eta: string | null
  file_size: number | null
  file_path: string | null
  error_message: string | null
  queue_position: number
  created_at: string
}

type SeamCall = { method: string; path: string; body: unknown }

/**
 * The processor states the queue envelope actually admits.
 *
 * `PROCESSOR_STATES` in `src/renderer/src/lib/queue/envelope.ts` is the source
 * of truth and `parseListEnvelope` THROWS on anything else, which surfaces as
 * an empty queue rather than an error - so the seam is typed against the enum
 * instead of `string`, and a stray name fails the type-check, not a run.
 */
type ProcessorStateName = 'Idle' | 'Processing' | 'Paused'

/**
 * One shell request the renderer recorded, mirroring `lib/queue/shell-actions`.
 *
 * Open file / Show in folder cross the IPC boundary rather than fetch, and
 * `window.api` is a FROZEN contextBridge proxy whose properties are
 * non-writable and non-configurable - stubbing `window.api.openPath` from the
 * page is silently ignored, so the seam reads the renderer's own ledger instead.
 */
type ShellIpcEntry = { channel: string; target: string }

type SeamSeed = {
  items: DownloadItem[]
  processorState: ProcessorStateName
  currentJobId: string | null
  cookieMode: 'none' | 'browser' | 'file'
  sabrMode: 'inactive' | 'active'
  /**
   * Keep the seam's row order across a `page.reload()`.
   *
   * `addInitScript` re-runs on every navigation and would otherwise reset the
   * queue to the seed, which would make a durability assertion (AC-49.25) pass
   * for a page that never persisted anything. The order is parked in the TEST
   * process over an exposed binding rather than in web storage, because the
   * renderer is loaded from a `file://` origin whose storage Chromium treats as
   * opaque.
   */
  persist: boolean
}

/** What `addInitScript` carries into the renderer: the seed plus the sample row. */
type InitSeed = SeamSeed & { sample: DownloadItem }

const sampleJob: DownloadItem = {
  id: 'e2e-1',
  url: 'https://example.invalid/watch?v=e2e0001',
  video_id: 'e2e0001',
  title: 'E2E',
  quality: '1080p',
  audio_only: false,
  audio_format: 'default',
  status: 'Pending',
  progress: 0,
  speed: null,
  eta: null,
  file_size: null,
  file_path: null,
  error_message: null,
  queue_position: 1,
  created_at: '2026-08-20T00:00:00Z',
}

function job(overrides: Partial<DownloadItem> & { id: string }): DownloadItem {
  return { ...sampleJob, title: overrides.id.toUpperCase(), ...overrides }
}

/** A four-row queue covering every status the card surface branches on. */
function seededQueue(): DownloadItem[] {
  return [
    job({ id: 'dl-1', status: 'Pending', quality: '720p', queue_position: 1 }),
    job({
      id: 'dl-2',
      status: 'Downloading',
      quality: '1080p',
      queue_position: 2,
      progress: 42,
      speed: '1.1MiB/s',
      eta: '02:13',
    }),
    job({
      id: 'dl-3',
      status: 'Done',
      quality: '4k',
      queue_position: 3,
      progress: 100,
      speed: '4.2MiB/s',
      eta: '00:00',
      file_size: 163_577_856,
      file_path: 'C:/e2e/out/dl-3.mp4',
    }),
    job({ id: 'dl-4', status: 'Failed', quality: '480p', queue_position: 4 }),
  ]
}

async function launchApp() {
  return _electron.launch({
    args: [resolve(here, '../../out/main/index.js')],
    env: {
      ...process.env,
      AVKIT_E2E: '1',
      AVKIT_APP_DATA: mkdtempSync(join(tmpdir(), 'avkit-e2e-')),
    },
  })
}

type Seam = {
  posts: { count: () => number }
  calls: () => Promise<SeamCall[]>
  callsTo: (path: string, method: string) => Promise<SeamCall[]>
  opened: () => Promise<string[]>
  revealed: () => Promise<string[]>
  rowOrder: () => Promise<string[]>
}

async function installSeam(page: Page, seed?: Partial<SeamSeed>): Promise<Seam> {
  const posts = { value: 0 }
  const context = page.context()
  await context.route((url) => url.pathname.includes('/downloads/sabr'), async (route) => {
    await route.fulfill({ json: { mode: seed?.sabrMode ?? 'inactive', source: null, checked_at: null } })
  })
  await context.route((url) => url.pathname.includes('/settings/downloader'), async (route) => {
    await route.fulfill({ json: { cookie_mode: seed?.cookieMode ?? 'none', cookie_browser: 'chrome', cookie_browser_profile: 'Default', cookie_file_path: '' } })
  })

  /*
    The renderer's fetch is stubbed in-page below, so requests never reach the
    Playwright route layer and its counters would read zero whatever the page
    did. This binding lets the in-page seam report the real POST count back to
    the test process, which is what `seam.posts` observes.
  */
  await page.exposeFunction('__e2eRecordDownloadPost', () => {
    posts.value += 1
  })

  // See SeamSeed.persist. Registered unconditionally so the binding names are
  // always defined in the page; the init script only calls them when asked to.
  const savedOrder: { value: string[] | null } = { value: null }
  await page.exposeFunction('__e2eSaveOrder', (ids: string[]) => {
    savedOrder.value = [...ids]
  })
  await page.exposeFunction('__e2eLoadOrder', () => savedOrder.value)

  /*
    `addInitScript` serialises this function into the renderer, so it may close
    over NOTHING from this module - `sampleJob` is not defined there. The sample
    row travels in the payload; referencing it by name would throw a
    ReferenceError inside window.fetch and silently empty the seeded queue.
  */
  const resolved: InitSeed = {
    items: seed?.items ?? [],
    processorState: seed?.processorState ?? 'Idle',
    currentJobId: seed?.currentJobId ?? null,
    cookieMode: seed?.cookieMode ?? 'none',
    sabrMode: seed?.sabrMode ?? 'inactive',
    persist: seed?.persist ?? false,
    sample: { ...sampleJob },
  }

  await page.addInitScript((initial: InitSeed) => {
    const state = window as unknown as {
      __e2eItems?: DownloadItem[]
      __e2eProcessor?: { state: string; current_job_id: string | null }
      __e2eCalls?: SeamCall[]
      __e2eIpc?: ShellIpcEntry[]
      __e2eDownloadPosts?: number
      __e2eSeamInstalled?: boolean
    }
    state.__e2eItems = initial.items.map((row) => ({ ...row }))
    state.__e2eProcessor = { state: initial.processorState, current_job_id: initial.currentJobId }
    state.__e2eCalls = []
    state.__e2eIpc = []
    state.__e2eDownloadPosts = 0
    state.__e2eSeamInstalled = true

    const renumber = (): void => {
      ;(state.__e2eItems ?? []).forEach((row, index) => {
        row.queue_position = index + 1
      })
    }

    const bridge = window as unknown as {
      __e2eSaveOrder?: (ids: string[]) => Promise<void>
      __e2eLoadOrder?: () => Promise<string[] | null>
    }

    /** Park the current order with the test process, so a reload can restore it. */
    const remember = (): void => {
      if (initial.persist) {
        void bridge.__e2eSaveOrder?.((state.__e2eItems ?? []).map((row) => row.id))
      }
    }

    /**
     * Restore the parked order on the first request after a navigation. The
     * seeded rows are the source of the row DATA either way; only their
     * sequence is restored.
     */
    let hydrated = !initial.persist
    const hydrate = async (): Promise<void> => {
      if (hydrated) {
        return
      }
      hydrated = true
      const saved = await bridge.__e2eLoadOrder?.()
      if (!Array.isArray(saved) || saved.length === 0) {
        return
      }
      const current = state.__e2eItems ?? []
      const next: DownloadItem[] = []
      for (const id of saved) {
        const found = current.find((row) => row.id === id)
        if (found !== undefined) {
          next.push(found)
        }
      }
      for (const row of current) {
        if (!next.includes(row)) {
          next.push(row)
        }
      }
      state.__e2eItems = next
      renumber()
    }

    const original = window.fetch.bind(window)
    window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      await hydrate()
      const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
      const method = (init?.method ?? 'GET').toUpperCase()
      const path = new URL(url).pathname
      const json = (body: unknown, status = 200) =>
        new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
      let parsed: unknown
      if (typeof init?.body === 'string' && init.body.length > 0) {
        try {
          parsed = JSON.parse(init.body)
        } catch {
          parsed = init.body
        }
      }
      if (method !== 'GET') {
        state.__e2eCalls?.push({ method, path, body: parsed })
      }

      if (url.includes('/downloads/sabr')) {
        return json({ mode: initial.sabrMode, source: null, checked_at: null })
      }
      if (url.includes('/settings/downloader')) {
        return json({ cookie_mode: initial.cookieMode, cookie_browser: 'chrome', cookie_browser_profile: 'Default', cookie_file_path: '' })
      }

      // --- processor lifecycle (queue-toolbar start / pause-resume) ---------
      if (path.endsWith('/downloads/start') && method === 'POST') {
        const next = (state.__e2eItems ?? []).find((row) => row.status === 'Pending')
        state.__e2eProcessor = {
          state: 'Processing',
          current_job_id: next?.id ?? state.__e2eProcessor?.current_job_id ?? null,
        }
        if (next !== undefined) {
          next.status = 'Downloading'
        }
        return new Response('', { status: 202 })
      }
      if (path.endsWith('/downloads/pause') && method === 'POST') {
        state.__e2eProcessor = {
          state: 'Paused',
          current_job_id: state.__e2eProcessor?.current_job_id ?? null,
        }
        return new Response('', { status: 202 })
      }
      if (path.endsWith('/downloads/resume') && method === 'POST') {
        state.__e2eProcessor = {
          state: 'Processing',
          current_job_id: state.__e2eProcessor?.current_job_id ?? null,
        }
        return new Response('', { status: 202 })
      }
      if (path.endsWith('/downloads/cancel') && method === 'POST') {
        const current = state.__e2eProcessor?.current_job_id ?? null
        const row = (state.__e2eItems ?? []).find((entry) => entry.id === current)
        if (row !== undefined) {
          row.status = 'Cancelled'
        }
        state.__e2eProcessor = { state: 'Idle', current_job_id: null }
        return new Response('', { status: 202 })
      }

      // --- reorder (REORDER_WIRE_CONTRACT) ----------------------------------
      if (path.endsWith('/downloads/reorder') && method === 'PUT') {
        const order = (parsed as { job_ids?: string[] } | undefined)?.job_ids ?? []
        const current = state.__e2eItems ?? []
        const next: DownloadItem[] = []
        for (const id of order) {
          const found = current.find((row) => row.id === id)
          if (found !== undefined) {
            next.push(found)
          }
        }
        for (const row of current) {
          if (!next.includes(row)) {
            next.push(row)
          }
        }
        state.__e2eItems = next
        renumber()
        remember()
        return json({ items: state.__e2eItems })
      }

      // --- per-row reset ----------------------------------------------------
      const resetMatch = /\/downloads\/([^/]+)\/reset$/.exec(path)
      if (resetMatch !== null && method === 'POST') {
        const row = (state.__e2eItems ?? []).find((entry) => entry.id === resetMatch[1])
        if (row !== undefined) {
          row.status = 'Pending'
          row.progress = 0
        }
        return new Response('', { status: 202 })
      }

      const isCollection = /\/downloads\/?$/.test(path)
      if (isCollection && method === 'POST') {
        const body = (parsed ?? {}) as Record<string, unknown>
        const keys = Object.keys(body).sort()
        if (
          JSON.stringify(keys) !== JSON.stringify(['audio_format', 'audio_only', 'quality', 'url']) ||
          typeof body.url !== 'string' ||
          typeof body.quality !== 'string' ||
          typeof body.audio_only !== 'boolean' ||
          typeof body.audio_format !== 'string'
        ) {
          return json({ error: { code: 'VALIDATION', message: 'CREATE_BODY' } }, 422)
        }
        state.__e2eDownloadPosts = (state.__e2eDownloadPosts ?? 0) + 1
        void (
          window as unknown as { __e2eRecordDownloadPost?: () => Promise<void> }
        ).__e2eRecordDownloadPost?.()
        state.__e2eItems = [
          ...(state.__e2eItems ?? []),
          { ...initial.sample, url: String(body.url), quality: String(body.quality) },
        ]
        renumber()
        return json({ items: state.__e2eItems }, 201)
      }
      if (isCollection && method === 'GET') {
        return json({
          items: state.__e2eItems ?? [],
          processor: state.__e2eProcessor ?? { state: 'Idle', current_job_id: null },
        })
      }
      if (isCollection && method === 'DELETE') {
        state.__e2eItems = []
        return new Response(null, { status: 204 })
      }
      const deleteMatch = /\/downloads\/([^/]+)$/.exec(path)
      if (deleteMatch !== null && method === 'DELETE') {
        state.__e2eItems = (state.__e2eItems ?? []).filter((row) => row.id !== deleteMatch[1])
        renumber()
        return new Response(null, { status: 204 })
      }
      if (url.includes('/downloads/') && (method === 'POST' || method === 'PUT')) {
        return new Response('', { status: 202 })
      }
      if (method === 'DELETE') {
        return new Response(null, { status: 204 })
      }
      return original(input, init)
    }
  }, resolved)

  await page.reload()
  await page.getByTestId('downloader-page').waitFor()

  const calls = async (): Promise<SeamCall[]> =>
    page.evaluate(() => (window as unknown as { __e2eCalls?: SeamCall[] }).__e2eCalls ?? [])

  const ipcTargets = async (channel: string): Promise<string[]> =>
    page.evaluate((wanted: string) => {
      const ledger = (window as unknown as { __e2eIpc?: { channel: string; target: string }[] })
        .__e2eIpc
      return (ledger ?? []).filter((row) => row.channel === wanted).map((row) => row.target)
    }, channel)

  return {
    posts: { count: () => posts.value },
    calls,
    callsTo: async (path: string, method: string) => {
      const all = await calls()
      return all.filter((row) => row.path.includes(path) && row.method === method)
    },
    opened: async () => ipcTargets('openPath'),
    revealed: async () => ipcTargets('showItemInFolder'),
    rowOrder: async () =>
      page.$$eval('[data-testid="queue-card"]', (nodes) =>
        nodes.map((node) => (node as HTMLElement).dataset.jobId ?? ''),
      ),
  }
}

/** Open one card's kebab and return the menu locator. */
async function openKebab(page: Page, id: string) {
  const row = page.locator(`[data-testid="queue-card"][data-job-id="${id}"]`)
  await row.getByTestId('queue-card-kebab').click()
  const menu = page.getByTestId('queue-card-menu')
  await expect(menu).toBeVisible()
  return menu
}

test('W1-1 DOWNLOADER_HOME shows the page and url field', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page)
  await expect(page.getByTestId('downloader-page')).toBeVisible()
  await expect(page.getByTestId('url-input')).toBeVisible()
  await app.close()
})

test('W1-2 nav from transcript returns to downloader', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page)
  await page.getByTestId('nav-transcript').click()
  await page.getByTestId('nav-downloader').click()
  await expect(page.getByTestId('downloader-page')).toBeVisible()
  await app.close()
})

test('W1-3 WAVE1 extra controls are present', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page, { items: seededQueue() })
  // MEU-53 keeps these controls in Advanced; open the real disclosure first.
  await page.getByTestId('add-advanced-toggle').click()
  await expect(page.getByTestId('quality-select')).toBeVisible()
  await expect(page.getByTestId('audio-only')).toBeVisible()
  await expect(page.getByTestId('audio-format')).toBeAttached()
  await expect(page.getByTestId('cookie-mode-none')).toBeVisible()
  await expect(page.getByTestId('cookie-mode-browser')).toBeVisible()
  await expect(page.getByTestId('cookie-mode-file')).toBeVisible()
  await expect(page.getByTestId('cookie-browser')).toBeAttached()
  await expect(page.getByTestId('cookie-profile')).toBeAttached()
  await expect(page.getByTestId('cookie-file')).toBeAttached()
  await expect(page.getByTestId('cookie-test-btn')).toBeVisible()
  await expect(page.getByTestId('sabr-check-btn')).toBeVisible()
  await expect(page.getByTestId('sabr-force-btn')).toBeVisible()
  await expect(page.getByTestId('sabr-clear-btn')).toBeVisible()

  /*
    MEU-46 rewrite. The seven reorder/lifecycle ids this census used to list
    (up/down/top/bottom/reset/remove/clear-all-btn) and `queue-table` are
    retired; the census now names the surfaces that carry those capabilities.
    Presence alone is not the contract - W1-7..W1-9 perform each one.
  */
  await expect(page.getByTestId('queue-list')).toBeVisible()
  await expect(page.getByTestId('queue-toolbar')).toBeVisible()
  await expect(page.getByTestId('queue-toolbar-start')).toBeVisible()
  await expect(page.getByTestId('queue-toolbar-clear-finished')).toBeVisible()
  await expect(page.getByTestId('queue-toolbar-overflow')).toBeVisible()
  await expect(page.getByTestId('queue-card')).toHaveCount(4)
  await expect(page.locator('[data-testid="queue-card"][data-job-id="dl-3"]').getByTestId('queue-card-kebab')).toBeVisible()
  await expect(
    page.locator('[data-testid="queue-card"][data-job-id="dl-3"]').getByTestId('queue-card-primary-action'),
  ).toBeVisible()

  // PRESERVED_TESTIDS: these three survive the migration untouched.
  await expect(page.getByTestId('queue-summary')).toBeVisible()
  await expect(page.getByTestId('processor-indicator')).toBeAttached()
  await expect(page.getByTestId('add-btn')).toBeVisible()
  await expect(page.getByTestId('sabr-status')).toBeAttached()
  await app.close()
})

test('W1-4 E2E_HAPPY_PATH add via E2E_SEAM', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page)
  await page.getByTestId('url-input').fill('https://example.invalid/watch?v=e2e0001')
  await page.getByTestId('add-btn').click()
  await expect(page.getByTestId('queue-card')).toBeVisible({ timeout: 15_000 })
  await expect(page.getByTestId('queue-card')).toContainText('E2E')
  expect(seam.posts.count()).toBe(1)
  await app.close()
})

test('W1-5 ENABLED_WHEN chrome on an empty download queue', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page)

  /*
    The retired per-page buttons were all disabled on an empty queue; the
    surviving toolbar controls carry that same ENABLED_WHEN chrome, and the
    per-card controls simply do not exist when there are no cards.
  */
  await expect(page.getByTestId('queue-toolbar')).toBeVisible()
  await expect(page.getByTestId('queue-toolbar-start')).toBeDisabled()
  await expect(page.getByTestId('queue-toolbar-clear-finished')).toBeDisabled()
  // PAUSE_SCOPE: one pause-resume toggle, so exactly one of the two exists.
  await expect(page.getByTestId('queue-toolbar-pause')).toBeVisible()
  await expect(page.getByTestId('queue-toolbar-pause')).toBeDisabled()
  await expect(page.getByTestId('queue-toolbar-resume')).toHaveCount(0)
  await expect(page.getByTestId('queue-card')).toHaveCount(0)
  await expect(page.getByTestId('queue-card-primary-action')).toHaveCount(0)
  await expect(page.getByTestId('queue-card-kebab')).toHaveCount(0)
  await page.getByTestId('queue-toolbar-overflow').click()
  await expect(page.getByTestId('queue-toolbar-clear-all')).toBeDisabled()
  await page.keyboard.press('Escape')

  // AC-46.6: none of the 13 retired ids survives anywhere on the page.
  for (const retired of [
    'start-btn',
    'pause-btn',
    'resume-btn',
    'cancel-btn',
    'up-btn',
    'down-btn',
    'top-btn',
    'bottom-btn',
    'reset-btn',
    'remove-btn',
    'clear-all-btn',
    'open-file-btn',
    'open-folder-btn',
  ]) {
    await expect(page.locator(`[data-testid="${retired}"]`), `${retired} is retired`).toHaveCount(0)
  }
  await app.close()
})

test('W1-6 PALETTE_DELIVER download:add focuses url-input on its page', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page)
  await page.getByTestId('nav-transcript').click()
  await page.getByTestId('header-palette-btn').click()
  await page.getByTestId('command-palette-input').fill('download:add')
  await expect(page.getByRole('dialog').getByRole('button', { name: 'Enter download URL' })).toHaveCount(0)
  await page.getByTestId('command-palette-input').fill('Downloader')
  await page.getByRole('dialog').getByRole('button', { name: /^Downloader( ?Ctrl\+1)?$/ }).click()
  await expect(page).toHaveURL(/#\/$/)
  await page.getByTestId('header-palette-btn').click()
  await page.getByTestId('command-palette-input').fill('download:add')
  await page.getByRole('dialog').getByRole('button', { name: 'Enter download URL' }).click()
  await expect(page.getByTestId('url-input')).toBeFocused()
  await app.close()
})

test('W1-7 toolbar lifecycle and kebab/keyboard reorder replace the retired move buttons', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page, { items: seededQueue() })
  await expect(page.getByTestId('queue-card')).toHaveCount(4)
  expect(await seam.rowOrder()).toEqual(['dl-1', 'dl-2', 'dl-3', 'dl-4'])

  // start-btn / pause-btn / resume-btn -> the toolbar's start button and the
  // single pause-resume toggle. Each click asserts its request AND the toolbar
  // state it produces, so a button wired to nothing fails here.
  await page.getByTestId('queue-toolbar-start').click()
  expect(await seam.callsTo('/downloads/start', 'POST')).toHaveLength(1)
  await expect(page.getByTestId('queue-toolbar-pause')).toBeVisible()
  await page.getByTestId('queue-toolbar-pause').click()
  expect(await seam.callsTo('/downloads/pause', 'POST')).toHaveLength(1)
  await expect(page.getByTestId('queue-toolbar-resume')).toBeVisible()
  await expect(page.getByTestId('queue-toolbar-pause')).toHaveCount(0)
  await page.getByTestId('queue-toolbar-resume').click()
  expect(await seam.callsTo('/downloads/resume', 'POST')).toHaveLength(1)
  await expect(page.getByTestId('queue-toolbar-pause')).toBeVisible()

  // up-btn / top-btn -> kebab move-up / move-top. REORDER_WIRE_CONTRACT: the
  // body is the complete permutation, never {id, direction}.
  const menu = await openKebab(page, 'dl-3')
  await menu.locator('[data-menu-action="move-up"]').click()
  const afterUp = await seam.callsTo('/downloads/reorder', 'PUT')
  expect(afterUp).toHaveLength(1)
  expect(afterUp[0].body).toEqual({ job_ids: ['dl-1', 'dl-3', 'dl-2', 'dl-4'] })
  expect(afterUp[0].body).not.toHaveProperty('direction')
  await expect.poll(async () => seam.rowOrder()).toEqual(['dl-1', 'dl-3', 'dl-2', 'dl-4'])

  const topMenu = await openKebab(page, 'dl-4')
  await topMenu.locator('[data-menu-action="move-top"]').click()
  const afterTop = await seam.callsTo('/downloads/reorder', 'PUT')
  expect(afterTop).toHaveLength(2)
  expect(afterTop[1].body).toEqual({ job_ids: ['dl-4', 'dl-1', 'dl-3', 'dl-2'] })
  await expect.poll(async () => seam.rowOrder()).toEqual(['dl-4', 'dl-1', 'dl-3', 'dl-2'])

  // down-btn / bottom-btn -> kebab move-down / move-bottom.
  const downMenu = await openKebab(page, 'dl-4')
  await downMenu.locator('[data-menu-action="move-down"]').click()
  const afterDown = await seam.callsTo('/downloads/reorder', 'PUT')
  expect(afterDown).toHaveLength(3)
  expect(afterDown[2].body).toEqual({ job_ids: ['dl-1', 'dl-4', 'dl-3', 'dl-2'] })
  await expect.poll(async () => seam.rowOrder()).toEqual(['dl-1', 'dl-4', 'dl-3', 'dl-2'])

  const bottomMenu = await openKebab(page, 'dl-1')
  await bottomMenu.locator('[data-menu-action="move-bottom"]').click()
  const afterBottom = await seam.callsTo('/downloads/reorder', 'PUT')
  expect(afterBottom).toHaveLength(4)
  expect(afterBottom[3].body).toEqual({ job_ids: ['dl-4', 'dl-3', 'dl-2', 'dl-1'] })
  await expect.poll(async () => seam.rowOrder()).toEqual(['dl-4', 'dl-3', 'dl-2', 'dl-1'])

  // up-btn / down-btn also lived on the keyboard: Alt+Arrow on a focused card
  // reorders, and a bare Arrow must not.
  const card = page.locator('[data-testid="queue-card"][data-job-id="dl-3"]')
  await card.getByTestId('queue-card-title').click()
  await card.press('Alt+ArrowUp')
  const afterAltUp = await seam.callsTo('/downloads/reorder', 'PUT')
  expect(afterAltUp).toHaveLength(5)
  expect(afterAltUp[4].body).toEqual({ job_ids: ['dl-3', 'dl-4', 'dl-2', 'dl-1'] })
  await expect.poll(async () => seam.rowOrder()).toEqual(['dl-3', 'dl-4', 'dl-2', 'dl-1'])

  await card.press('Alt+ArrowDown')
  const afterAltDown = await seam.callsTo('/downloads/reorder', 'PUT')
  expect(afterAltDown).toHaveLength(6)
  expect(afterAltDown[5].body).toEqual({ job_ids: ['dl-4', 'dl-3', 'dl-2', 'dl-1'] })

  await card.press('ArrowUp')
  expect(await seam.callsTo('/downloads/reorder', 'PUT')).toHaveLength(6)
  await app.close()
})

test('W1-8 card primary actions and kebab open items replace the retired row buttons', async () => {
  // TA-3 (Session 29 A-6): a long multi-step flow; under heavy host load (WINDOWS_GATE attempt 2) it overran
  // the 60 s default. test.slow() triples the budget for this test only; no assertion changes.
  test.slow()
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page, {
    items: seededQueue(),
    processorState: 'Processing',
    currentJobId: 'dl-2',
  })
  await expect(page.getByTestId('queue-card')).toHaveCount(4)

  const rowOf = (id: string) => page.locator(`[data-testid="queue-card"][data-job-id="${id}"]`)

  // PRIMARY_ACTION_MAP: a Pending row offers none at all.
  await expect(rowOf('dl-1').getByTestId('queue-card-primary-action')).toHaveCount(0)

  // open-file-btn -> the Done row's primary action (IPC, not fetch).
  const done = rowOf('dl-3').getByTestId('queue-card-primary-action')
  await expect(done).toHaveText('Open file')
  await done.click()
  await expect.poll(async () => seam.opened()).toEqual(['C:/e2e/out/dl-3.mp4'])

  // open-file-btn / open-folder-btn -> the kebab's own items. KEBAB_ACTION_LABELS
  // makes copy-location state-dependent: this row HAS an output path, so the
  // label must name the path it copies (the URL variant is covered on the
  // pathless first row by the unit suite's AC-46.10).
  const doneMenu = await openKebab(page, 'dl-3')
  await expect(doneMenu.locator('[data-menu-action="open-file"]')).toBeVisible()
  await expect(doneMenu.locator('[data-menu-action="copy-location"]')).toHaveText('Copy path')
  await doneMenu.locator('[data-menu-action="open-file"]').click()
  await expect.poll(async () => seam.opened()).toHaveLength(2)

  const folderMenu = await openKebab(page, 'dl-3')
  await folderMenu.locator('[data-menu-action="open-folder"]').click()
  await expect.poll(async () => seam.revealed()).toEqual(['C:/e2e/out/dl-3.mp4'])

  // reset-btn -> the Failed row's Retry primary action.
  const retry = rowOf('dl-4').getByTestId('queue-card-primary-action')
  await expect(retry).toHaveText('Retry')
  await retry.click()
  // TA-3: poll the seam log (same expected count); one read can run before the click's fetch is logged.
  await expect.poll(async () => (await seam.callsTo('/downloads/dl-4/reset', 'POST')).length).toBe(1)
  await expect
    .poll(async () => rowOf('dl-4').getByTestId('queue-card-primary-action').count())
    .toBe(0)

  // cancel-btn -> the in-flight row's primary action. CANCEL_CONTROL_LABEL is
  // exact, and cancelling the queue from a card raises no confirm.
  const cancel = rowOf('dl-2').getByTestId('queue-card-primary-action')
  await expect(cancel).toHaveAccessibleName('Cancel queue')
  await cancel.click()
  // TA-3: poll the seam log (same expected count); one read can run before the click's fetch is logged.
  await expect.poll(async () => (await seam.callsTo('/downloads/cancel', 'POST')).length).toBe(1)
  await expect(page.getByTestId('confirm-modal')).toHaveCount(0)
  await app.close()
})

test('W1-9 kebab remove and toolbar clear-all replace the retired destructive buttons', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page, { items: seededQueue() })
  await expect(page.getByTestId('queue-card')).toHaveCount(4)

  // remove-btn -> kebab remove, behind the shared confirm modal. Dismissing it
  // must issue nothing: the outcome, not the click, is the contract.
  const menu = await openKebab(page, 'dl-2')
  await menu.locator('[data-menu-action="remove"]').click()
  await expect(page.getByTestId('confirm-modal')).toBeVisible()
  await page.getByTestId('confirm-modal-cancel').click()
  expect(await seam.callsTo('/downloads/dl-2', 'DELETE')).toHaveLength(0)
  await expect(page.getByTestId('queue-card')).toHaveCount(4)

  const again = await openKebab(page, 'dl-2')
  await again.locator('[data-menu-action="remove"]').click()
  await page.getByTestId('confirm-modal-confirm').click()
  expect(await seam.callsTo('/downloads/dl-2', 'DELETE')).toHaveLength(1)
  await expect.poll(async () => seam.rowOrder()).toEqual(['dl-1', 'dl-3', 'dl-4'])

  // clear-all-btn -> queue-toolbar-overflow > queue-toolbar-clear-all, also
  // behind the shared confirm modal rather than window.confirm.
  await page.getByTestId('queue-toolbar-overflow').click()
  await page.getByTestId('queue-toolbar-clear-all').click()
  await expect(page.getByTestId('confirm-modal')).toBeVisible()
  await expect(page.getByTestId('confirm-modal-confirm')).toHaveText('Clear all')
  await page.getByTestId('confirm-modal-confirm').click()
  const cleared = (await seam.calls()).filter(
    (call) => call.method === 'DELETE' && /\/downloads\/?$/.test(call.path),
  )
  expect(cleared).toHaveLength(1)
  await expect(page.getByTestId('queue-card')).toHaveCount(0)
  await app.close()
})

test('AC-96.12 CONFIRM_ROUTE palette Clear opens the confirm and Cancel keeps the queue', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page, { items: seededQueue() })
  await expect(page.getByTestId('queue-card')).toHaveCount(4)

  await page.getByTestId('header-palette-btn').click()
  await page.getByTestId('command-palette-input').fill('Clear')
  await page.getByRole('dialog').getByRole('button', { name: 'Clear download queue' }).click()
  await expect(page.getByTestId('confirm-modal')).toHaveCount(1)
  await expect(page.getByTestId('confirm-modal')).toBeVisible()
  await expect(page.getByTestId('confirm-modal-confirm')).toHaveText('Clear all')
  await page.getByTestId('confirm-modal-cancel').click()
  await expect(page.getByTestId('confirm-modal')).toHaveCount(0)
  await expect(page.getByTestId('queue-card')).toHaveCount(4)
  expect(await seam.callsTo('/downloads', 'DELETE')).toHaveLength(0)

  await page.getByTestId('header-palette-btn').click()
  await page.getByTestId('command-palette-input').fill('Clear')
  await page.getByRole('dialog').getByRole('button', { name: 'Clear download queue' }).click()
  await page.getByTestId('confirm-modal-confirm').click()
  await expect.poll(async () => (await seam.callsTo('/downloads', 'DELETE')).length).toBe(1)
  await app.close()
})

test('W1-10 EMPTY_STATE_CONTRACT url intake invite focuses url-input and adds', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page)

  // The downloader has no local-file intake, so the converter's drop/Browse
  // invitation must NOT appear here.
  await expect(page.getByTestId('queue-empty-invite')).toBeVisible()
  await expect(page.getByTestId('queue-empty-invite')).toContainText(
    'Paste a video link above to queue a download',
  )
  await expect(page.getByTestId('queue-empty-dropzone')).toHaveCount(0)
  await expect(page.getByTestId('queue-drop-strip')).toHaveCount(0)

  // The invite's button is real: it focuses the existing url-input, and the
  // normal intake then produces exactly one POST /downloads.
  await page.getByTestId('queue-empty-invite-action').click()
  await expect(page.getByTestId('url-input')).toBeFocused()
  await page.keyboard.type('https://example.invalid/watch?v=e2e0001')
  await page.getByTestId('add-btn').click()
  await expect(page.getByTestId('queue-card')).toHaveCount(1, { timeout: 15_000 })
  expect(seam.posts.count()).toBe(1)
  await expect(page.getByTestId('queue-empty-invite')).toHaveCount(0)
  await app.close()
})

/*
  MEU-47 — BULK_CONTROL_E2E_OBLIGATION on the downloader.

  The obligation is explicit that no control may rely on a sibling home: the
  converter's identical block does not cover these. Every one of the five
  BULK_BAR_ACTIONS is clicked here, the queue-select-all header is exercised in
  all three SELECTION_HEADER_CONTRACT states, and the keyboard entry path is
  driven end to end — each with an outcome assertion, per MOUNT_GATE_CLAUSE_4.
*/

/**
 * Six rows: two requeueable, two Done, and two neither set admits.
 *
 * `dl-4` is `QualityBlocked` on purpose — it is in
 * DOWNLOAD_REQUEUEABLE_STATUSES but NOT in CONVERT_REQUEUEABLE_STATUSES, so a
 * bulk Retry that quietly reused the converter's set would leave it behind.
 */
function bulkQueue(): DownloadItem[] {
  return [
    job({ id: 'dl-1', status: 'Pending', quality: '720p', queue_position: 1 }),
    job({ id: 'dl-2', status: 'Failed', quality: '1080p', queue_position: 2 }),
    job({
      id: 'dl-3',
      status: 'Done',
      quality: '4k',
      queue_position: 3,
      progress: 100,
      file_size: 163_577_856,
      file_path: 'C:/e2e/out/dl-3.mp4',
    }),
    job({ id: 'dl-4', status: 'QualityBlocked', quality: '4k', queue_position: 4 }),
    job({
      id: 'dl-5',
      status: 'Done',
      quality: '1080p',
      queue_position: 5,
      progress: 100,
      file_size: 52_428_800,
      file_path: 'C:/e2e/out/dl-5.mp4',
    }),
    job({ id: 'dl-6', status: 'Skipped', quality: '480p', queue_position: 6 }),
  ]
}

function downloadRow(page: Page, id: string) {
  return page.locator(`[data-testid="queue-card"][data-job-id="${id}"]`)
}

/** Tick one row's selection checkbox. */
async function selectRow(page: Page, id: string): Promise<void> {
  await downloadRow(page, id).getByTestId('selection-checkbox').click()
}

/** Clear the G35 partial-result toast if one is up, so it cannot eat a click. */
async function dismissBulkToast(page: Page): Promise<void> {
  const dismiss = page.getByTestId('bulk-toast-dismiss')
  if ((await dismiss.count()) > 0) {
    await dismiss.first().click()
  }
}

/** Read the header checkbox's tri-state, which lives in DOM properties only. */
async function selectAllState(page: Page): Promise<{ checked: boolean; indeterminate: boolean }> {
  return page.getByTestId('queue-select-all').evaluate((node) => ({
    checked: (node as HTMLInputElement).checked,
    indeterminate: (node as HTMLInputElement).indeterminate,
  }))
}

test('W1-11 bulk retry re-queues the selected rows and clear-selection empties the bar', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page, { items: bulkQueue() })
  await expect(page.getByTestId('queue-card')).toHaveCount(6)

  // AC-47.4: with nothing selected the bar is ABSENT, not hidden.
  await expect(page.getByTestId('bulk-action-bar')).toHaveCount(0)

  // bulk-retry over DOWNLOAD_REQUEUEABLE_STATUSES: Failed + QualityBlocked.
  await selectRow(page, 'dl-2')
  await selectRow(page, 'dl-4')
  const bar = page.getByTestId('bulk-action-bar')
  await expect(bar).toBeVisible()
  await expect(bar.getByTestId('bulk-selection-count')).toContainText('2')

  await bar.getByTestId('bulk-retry').click()
  await expect
    .poll(async () => (await seam.callsTo('/downloads/dl-2/reset', 'POST')).length)
    .toBe(1)
  expect(
    await seam.callsTo('/downloads/dl-4/reset', 'POST'),
    'QualityBlocked is requeueable on the downloader',
  ).toHaveLength(1)

  // BULK_ENDPOINT_POLICY: per-id endpoints only, and never for a row the user
  // did not select.
  expect(await seam.callsTo('/downloads/dl-1/reset', 'POST')).toHaveLength(0)
  expect(await seam.callsTo('/downloads/dl-3/reset', 'POST')).toHaveLength(0)
  expect((await seam.calls()).filter((call) => call.path.includes('/bulk'))).toHaveLength(0)

  // SELECTION_MODEL: a completed bulk action clears the selection.
  await expect(page.getByTestId('bulk-action-bar')).toHaveCount(0)
  await expect(downloadRow(page, 'dl-2').getByTestId('queue-card-primary-action')).toHaveCount(0)
  await dismissBulkToast(page)

  // bulk-clear-selection: the bar disappears and every checkbox is unticked.
  await selectRow(page, 'dl-1')
  await selectRow(page, 'dl-3')
  await expect(bar.getByTestId('bulk-selection-count')).toContainText('2')
  await bar.getByTestId('bulk-clear-selection').click()
  await expect(page.getByTestId('bulk-action-bar')).toHaveCount(0)
  const ticked = await page
    .locator('[data-testid="queue-card"] [data-testid="selection-checkbox"]')
    .evaluateAll((nodes) => nodes.filter((node) => (node as HTMLInputElement).checked).length)
  expect(ticked, 'clear-selection unticks every row, not just the bar').toBe(0)

  expect((await seam.calls()).filter((call) => call.method === 'DELETE')).toHaveLength(0)
  await app.close()
})

test('W1-12 bulk move-top and move-bottom send folded REORDER_WIRE_CONTRACT bodies', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page, { items: bulkQueue() })
  await expect(page.getByTestId('queue-card')).toHaveCount(6)
  expect(await seam.rowOrder()).toEqual(['dl-1', 'dl-2', 'dl-3', 'dl-4', 'dl-5', 'dl-6'])

  // BULK_REORDER_ALGORITHM: move-top walks the selection in REVERSED render
  // order and each body is the fold of the preceding accepted one.
  await selectRow(page, 'dl-2')
  await selectRow(page, 'dl-4')
  await page.getByTestId('bulk-move-top').click()

  await expect.poll(async () => (await seam.callsTo('/downloads/reorder', 'PUT')).length).toBe(2)
  const top = await seam.callsTo('/downloads/reorder', 'PUT')
  expect(top[0].body, 'step 1 lifts the LAST selected row').toEqual({
    job_ids: ['dl-4', 'dl-1', 'dl-2', 'dl-3', 'dl-5', 'dl-6'],
  })
  expect(top[1].body, 'step 2 folds from step 1, never from the initial order').toEqual({
    job_ids: ['dl-2', 'dl-4', 'dl-1', 'dl-3', 'dl-5', 'dl-6'],
  })
  for (const call of top) {
    expect(call.body).not.toHaveProperty('direction')
  }
  await expect
    .poll(async () => seam.rowOrder())
    .toEqual(['dl-2', 'dl-4', 'dl-1', 'dl-3', 'dl-5', 'dl-6'])
  await dismissBulkToast(page)

  // move-bottom walks the selection in render order, same fold.
  await selectRow(page, 'dl-1')
  await selectRow(page, 'dl-3')
  await page.getByTestId('bulk-move-bottom').click()

  await expect.poll(async () => (await seam.callsTo('/downloads/reorder', 'PUT')).length).toBe(4)
  const bottom = await seam.callsTo('/downloads/reorder', 'PUT')
  expect(bottom[2].body).toEqual({ job_ids: ['dl-2', 'dl-4', 'dl-3', 'dl-5', 'dl-6', 'dl-1'] })
  expect(bottom[3].body).toEqual({ job_ids: ['dl-2', 'dl-4', 'dl-5', 'dl-6', 'dl-1', 'dl-3'] })
  await expect
    .poll(async () => seam.rowOrder())
    .toEqual(['dl-2', 'dl-4', 'dl-5', 'dl-6', 'dl-1', 'dl-3'])

  expect((await seam.calls()).filter((call) => call.path.includes('/bulk'))).toHaveLength(0)
  await app.close()
})

test('W1-13 bulk remove confirms with the verb label and Clear finished sweeps only Done', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page, { items: bulkQueue() })
  await expect(page.getByTestId('queue-card')).toHaveCount(6)

  // AC-47.6 (USER_LOCKS): the confirm names the verb and the count, and
  // dismissing it issues nothing.
  await selectRow(page, 'dl-1')
  await selectRow(page, 'dl-6')
  await page.getByTestId('bulk-remove').click()
  await expect(page.getByTestId('confirm-modal')).toBeVisible()
  await expect(page.getByTestId('confirm-modal-confirm')).toHaveText('Remove 2 items')
  await page.getByTestId('confirm-modal-cancel').click()
  expect((await seam.calls()).filter((call) => call.method === 'DELETE')).toHaveLength(0)
  await expect(page.getByTestId('queue-card')).toHaveCount(6)
  await expect(page.getByTestId('bulk-action-bar')).toBeVisible()

  await page.getByTestId('bulk-remove').click()
  await page.getByTestId('confirm-modal-confirm').click()
  await expect.poll(async () => seam.rowOrder()).toEqual(['dl-2', 'dl-3', 'dl-4', 'dl-5'])
  expect(await seam.callsTo('/downloads/dl-1', 'DELETE')).toHaveLength(1)
  expect(await seam.callsTo('/downloads/dl-6', 'DELETE')).toHaveLength(1)
  await dismissBulkToast(page)

  // AC-47.7 over a mixed queue: only CLEAR_FINISHED_SNAPSHOT_STATUSES rows go.
  // Failed and QualityBlocked rows are failure evidence the user has not seen.
  await page.getByTestId('queue-toolbar-clear-finished').click()
  await expect.poll(async () => seam.rowOrder()).toEqual(['dl-2', 'dl-4'])
  expect(await seam.callsTo('/downloads/dl-3', 'DELETE')).toHaveLength(1)
  expect(await seam.callsTo('/downloads/dl-5', 'DELETE')).toHaveLength(1)
  expect(await seam.callsTo('/downloads/dl-2', 'DELETE')).toHaveLength(0)
  expect(await seam.callsTo('/downloads/dl-4', 'DELETE')).toHaveLength(0)
  expect((await seam.calls()).filter((call) => call.path.includes('/bulk'))).toHaveLength(0)
  await app.close()
})

test('W1-14 queue-select-all cycles all three states and the keyboard starts a selection', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page, { items: bulkQueue() })
  await expect(page.getByTestId('queue-card')).toHaveCount(6)

  // SELECTION_HEADER_CONTRACT: mounted before anything is selected — it is the
  // control that STARTS a selection, so it cannot depend on one.
  const header = page.getByTestId('queue-select-all')
  await expect(header).toBeVisible()
  expect(await selectAllState(page)).toEqual({ checked: false, indeterminate: false })

  // none -> all
  await header.click()
  await expect(page.getByTestId('bulk-selection-count')).toContainText('6')
  expect(await selectAllState(page)).toEqual({ checked: true, indeterminate: false })

  // all -> none
  await header.click()
  await expect(page.getByTestId('bulk-action-bar')).toHaveCount(0)
  expect(await selectAllState(page)).toEqual({ checked: false, indeterminate: false })

  // indeterminate -> all
  await selectRow(page, 'dl-3')
  await expect(page.getByTestId('bulk-selection-count')).toContainText('1')
  expect(await selectAllState(page)).toEqual({ checked: false, indeterminate: true })
  await header.click()
  await expect(page.getByTestId('bulk-selection-count')).toContainText('6')
  expect(await selectAllState(page)).toEqual({ checked: true, indeterminate: false })

  await page.getByTestId('bulk-clear-selection').click()
  await expect(page.getByTestId('bulk-action-bar')).toHaveCount(0)

  // AC-47.10a keyboard entry path (G34_RULE): focus a row's own checkbox and
  // toggle it from the keyboard. A checkbox reachable only by mouse fails here.
  const box = downloadRow(page, 'dl-5').getByTestId('selection-checkbox')
  await box.focus()
  await expect(box).toBeFocused()
  await box.press('Space')
  await expect(page.getByTestId('bulk-action-bar')).toBeVisible()
  await expect(page.getByTestId('bulk-selection-count')).toContainText('1')
  expect(await selectAllState(page)).toEqual({ checked: false, indeterminate: true })
  await app.close()
})

// ---------------------------------------------------------------------------
// MEU-49 — pointer and keyboard drag reorder on the downloader queue.
//
// AC-49.25, AC-49.26, AC-49.27, AC-49.28 and AC-49.36. These are the only
// assertions in the MEU that exercise a real drag: jsdom reports every rect as
// all-zero (`JSDOM_RECT_RULE`), so dnd-kit's collision detection can never
// resolve a drop in a unit test and the unit suite mocks it away. Here it runs
// for real, against real Electron.
// ---------------------------------------------------------------------------

/** The drag handle on one card. */
function handleOf(page: Page, id: string) {
  return page
    .locator(`[data-testid="queue-card"][data-job-id="${id}"]`)
    .getByTestId('queue-card-drag-handle')
}

/**
 * `E2E_DRAG_SETTLE` (Session 26 amendment A12). On Windows the drag specs raced
 * layout about one run in five: the pointer was aimed from a box read while the
 * page or a sortable transform was still moving, so either the press missed the
 * handle (no drag, an empty live region) or the pointer settled one row short
 * (`closestCenter` resolved the neighbour). Aim only at layout that has held
 * still for two animation frames, measured with every ancestor transform
 * removed — the same transform-agnostic rect dnd-kit measures droppables with —
 * so a row mid-shift is aimed at where it sits, not where it is sliding.
 */
async function settledCenter(page: Page, locator: Locator): Promise<{ x: number; y: number }> {
  let previous = ''
  for (let frame = 0; frame < 60; frame += 1) {
    const center = await locator.evaluate((element) => {
      const rect = element.getBoundingClientRect()
      let dx = 0
      let dy = 0
      for (let node: Element | null = element; node !== null; node = node.parentElement) {
        const transform = getComputedStyle(node).transform
        if (transform !== 'none') {
          const matrix = new DOMMatrixReadOnly(transform)
          dx += matrix.m41
          dy += matrix.m42
        }
      }
      return { x: rect.left - dx + rect.width / 2, y: rect.top - dy + rect.height / 2 }
    })
    const key = `${center.x},${center.y}`
    if (key === previous) {
      return center
    }
    previous = key
    await page.evaluate(
      () => new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve))),
    )
  }
  throw new Error('layout never settled for the drag target')
}

/** Wait until no CSS transition is running on a queue row or its sortable wrapper. */
async function rowTransitionsIdle(page: Page): Promise<void> {
  await page.waitForFunction(() =>
    document.getAnimations().every((animation) => {
      const target = (animation.effect as KeyframeEffect | null)?.target
      const onRow =
        target instanceof Element &&
        (target.closest('[data-testid="queue-card"]') !== null ||
          target.querySelector('[data-testid="queue-card"]') !== null)
      return !onRow || animation.playState !== 'running'
    }),
  )
}

/**
 * `E2E_WINDOW_SETTLE` (Session 26 amendment A13). dnd-kit cancels an active
 * pointer or keyboard drag on any window `resize` or `visibilitychange`, and the
 * app window resizes once just after launch (probed: 1280x800 -> 1280x773 as
 * the window is shown). On a loaded Windows host that resize can land after the
 * pickup and cancel the drag ("… was cancelled"). Start a drag only once the
 * window is visible and has not resized for 500ms.
 */
async function windowSettled(page: Page): Promise<void> {
  await page.waitForFunction(() => document.visibilityState === 'visible')
  // `E2E_WINDOW_SHOWN` (Session 27 A-4). The renderer reports `visible` even before the main
  // process shows the window, and a not-yet-shown window is frame-throttled. Showing it resizes
  // it, which cancels a held drag. Wait for full-rate frames (a shown window) first, so the
  // reveal's resize falls before the quiet period below and not inside the drag.
  const shown = await page.evaluate(
    () =>
      new Promise<boolean>((resolve) => {
        const deadline = performance.now() + 15_000
        let last = performance.now()
        let fast = 0
        const tick = (now: number): void => {
          fast = now - last < 50 ? fast + 1 : 0
          last = now
          if (fast >= 6) {
            resolve(true)
          } else if (now > deadline) {
            resolve(false)
          } else {
            requestAnimationFrame(tick)
          }
        }
        requestAnimationFrame(tick)
      }),
  )
  if (!shown) {
    throw new Error('E2E_WINDOW_SHOWN: the window never reached full-rate frames within 15 s')
  }
  await page.evaluate(
    () =>
      new Promise<void>((resolve) => {
        const quiet = 500
        let timer = window.setTimeout(done, quiet)
        function onResize(): void {
          window.clearTimeout(timer)
          timer = window.setTimeout(done, quiet)
        }
        function done(): void {
          window.removeEventListener('resize', onResize)
          resolve()
        }
        window.addEventListener('resize', onResize)
      }),
  )
}

/**
 * Press the pointer on a row's handle and cross dnd-kit's activation distance.
 *
 * `E2E_DRAG_DRIVER`: `locator.dragTo()` is NOT used. dnd-kit is pointer-events
 * only and its PointerSensor needs intermediate `pointermove` events to cross
 * `DND_SENSOR_CONFIG`'s 5px `activationConstraint`; `dragTo()` emits too few,
 * so the drag never activates and the test silently asserts nothing.
 */
async function grabRow(page: Page, id: string): Promise<void> {
  const handle = handleOf(page, id)
  await handle.waitFor()
  await windowSettled(page)
  const { x, y } = await settledCenter(page, handle)
  await page.mouse.move(x, y)
  await page.mouse.down()
  // The activation nudge: more than 5px, in steps, BEFORE the pointer reaches
  // the target row.
  await page.mouse.move(x, y + 14, { steps: 5 })
  // dnd-kit marks the active handle `aria-pressed="true"` once the sensor has
  // activated; only then is there a drag for the pointer to carry.
  await page
    .locator(
      `[data-testid="queue-card"][data-job-id="${id}"] [data-testid="queue-card-drag-handle"][aria-pressed="true"]`,
    )
    .waitFor()
}

/** Move the held pointer onto the vertical centre of another row. */
async function dragOver(page: Page, id: string): Promise<void> {
  const target = page.locator(`[data-testid="queue-card"][data-job-id="${id}"]`)
  await target.waitFor()
  // Sortable rows move by transform only, so DOM order is still the pre-drag order.
  const order = await page
    .locator('[data-testid="queue-card"]')
    .evaluateAll((cards) => cards.map((card) => card.getAttribute('data-job-id')))
  const position = order.indexOf(id) + 1
  const aim = await settledCenter(page, target)
  await page.mouse.move(aim.x, aim.y, { steps: 10 })
  // Let the sortable shift finish, then re-aim if the layout moved under the
  // pointer while it travelled (a transform alone never changes the aim).
  await rowTransitionsIdle(page)
  const settled = await settledCenter(page, target)
  if (settled.x !== aim.x || settled.y !== aim.y) {
    await page.mouse.move(settled.x, settled.y, { steps: 2 })
    await rowTransitionsIdle(page)
  }
  // `E2E_DRAG_COMMITTED_OVER` (Session 26 amendment A16). dnd-kit commits the
  // row under the pointer two React renders after the last pointermove, and the
  // drop reads whatever is committed at pointerup; a release that beats those
  // renders (a loaded Windows host) drops on the previous row. The over
  // announcement is emitted only once `over` is committed, so wait for it.
  try {
    await liveRegion(page)
      .filter({ hasText: `moved to position ${position} of ${order.length}.` })
      .waitFor({ state: 'attached' })
  } catch (error) {
    // Session 27 A-4: a timeout here used to leave no trace of the drag state (Playwright keeps
    // no page snapshot for `_electron` windows), so the failure carries it.
    const state = await page
      .evaluate(() => ({
        liveRegion: Array.from(document.querySelectorAll('[id^="DndLiveRegion"]')).map((node) => node.textContent),
        dragState: document.querySelector('[data-testid="queue-list"]')?.getAttribute('data-drag-state'),
        window: { width: window.innerWidth, height: window.innerHeight },
        focused: document.hasFocus(),
        visibility: document.visibilityState,
      }))
      .catch((probe: unknown) => ({ probeFailed: String(probe) }))
    const message = error instanceof Error ? error.message : String(error)
    throw new Error(`${message}\nA-4 drag diagnostics: ${JSON.stringify(state)}`)
  }
}

/** The dnd-kit live region. `DND_LIVE_REGION_LOCATOR` — never role=status. */
function liveRegion(page: Page) {
  return page.locator('[id^="DndLiveRegion"]')
}

/**
 * Count `document` keydown registrations, so a keyboard drag can wait for
 * dnd-kit's sensor to actually be listening.
 *
 * `KeyboardSensor.attach()` registers its document keydown listener from a
 * `setTimeout`, and the sensor is constructed in an effect that runs after the
 * pickup announcement has already been committed. Measured on this page: Space
 * at t=134ms, announcement at t=140ms, listener at t=153ms. So the announcement
 * is not a usable settle — neither is one macrotask after it, because the 13ms
 * gap is real work rather than queue ordering, and a spec that races it drops
 * the ArrowDown and moves nothing. The registration is the only honest signal.
 * No human typing speed can reproduce the race, which is why it is a test
 * concern and not a product defect.
 */
async function watchKeydownListeners(page: Page): Promise<void> {
  await page.evaluate(() => {
    const store = window as unknown as { __keydownListeners: number }
    store.__keydownListeners = 0
    const original = document.addEventListener.bind(document)
    document.addEventListener = ((type: string, ...rest: unknown[]) => {
      if (type === 'keydown') {
        store.__keydownListeners += 1
      }
      return (original as (...args: unknown[]) => void)(type, ...rest)
    }) as typeof document.addEventListener
  })
}

function keydownListenerCount(page: Page): Promise<number> {
  return page.evaluate(
    () => (window as unknown as { __keydownListeners?: number }).__keydownListeners ?? 0,
  )
}

/**
 * TA-27: a focused handle shows its hint at once, and a visible hint listens for Escape on the document. Wait
 * for that hint, then zero the count, so the wait after Space sees only the keyboard sensor's listener.
 */
async function settleHandleHint(page: Page): Promise<void> {
  await expect(page.getByTestId('queue-card-drag-handle-hint')).toBeVisible()
  await page.evaluate(() => {
    const store = window as unknown as { __keydownListeners: number }
    store.__keydownListeners = 0
  })
}

test('AC-49.25 dragging a row onto the third row lands the exact order, and it survives a reload', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page, { items: seededQueue(), persist: true })
  await expect(page.getByTestId('queue-card')).toHaveCount(4)
  expect(await seam.rowOrder()).toEqual(['dl-1', 'dl-2', 'dl-3', 'dl-4'])

  await grabRow(page, 'dl-1')
  await dragOver(page, 'dl-3')
  await page.mouse.up()

  // MOVE_TO_INDEX_CONTRACT — targetIndex is the FINAL index resolved against
  // the PRE-MOVE array, so [A,B,C,D] with A dropped on row 3 is [B,C,A,D].
  // [B,A,C,D] is the post-removal-index bug and [A,B,C,D] means the drag never
  // activated; both must fail here.
  const puts = await seam.callsTo('/downloads/reorder', 'PUT')
  expect(puts).toHaveLength(1)
  expect(puts[0].body).toEqual({ job_ids: ['dl-2', 'dl-3', 'dl-1', 'dl-4'] })
  await expect.poll(async () => seam.rowOrder()).toEqual(['dl-2', 'dl-3', 'dl-1', 'dl-4'])

  // Durability: the order the page shows after a full reload is the order the
  // server holds, not an optimistic local shuffle.
  await page.reload()
  await page.getByTestId('downloader-page').waitFor()
  await expect(page.getByTestId('queue-card')).toHaveCount(4)
  await expect.poll(async () => seam.rowOrder()).toEqual(['dl-2', 'dl-3', 'dl-1', 'dl-4'])
  await app.close()
})

test('AC-49.26 the drag announces position-based progress naming the dragged title', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page, { items: seededQueue() })
  await expect(page.getByTestId('queue-card')).toHaveCount(4)

  // The dragged row's title, read off the card rather than assumed.
  const title = (
    await page
      .locator('[data-testid="queue-card"][data-job-id="dl-1"]')
      .getByTestId('queue-card-title')
      .textContent()
  )?.trim()
  expect(title, 'the seeded row has a title to announce').toBeTruthy()

  await grabRow(page, 'dl-1')
  await dragOver(page, 'dl-3')

  // DND_ANNOUNCEMENT_CONTRACT — during the drag, position-based and 1-indexed.
  await expect(liveRegion(page)).toContainText(String(title))
  await expect(liveRegion(page)).toContainText(/position 3 of 4/i)

  await page.mouse.up()

  // And after it: the drop is confirmed, still by title and still by position.
  await expect(liveRegion(page)).toContainText(String(title))
  await expect(liveRegion(page)).toContainText(/position 3 of 4/i)
  await app.close()
})

test('AC-49.27 a keyboard drag reorders and returns focus to the moved row handle [TA-27]', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page, { items: seededQueue() })
  await expect(page.getByTestId('queue-card')).toHaveCount(4)

  await watchKeydownListeners(page)
  await windowSettled(page)

  // DND_HANDLE_CONTRACT — the handle is a real button, so it takes focus. A div
  // with listeners could not be reached this way at all.
  await handleOf(page, 'dl-1').focus()
  await settleHandleHint(page)
  await page.keyboard.press('Space')
  // The sensor registers its keydown listener well after it announces the
  // pickup; an ArrowDown sent before that is silently dropped. See
  // watchKeydownListeners.
  await expect.poll(async () => keydownListenerCount(page)).toBeGreaterThan(0)
  await page.keyboard.press('ArrowDown')
  // The drop resolves against dnd-kit's committed `over`. A Space sent before
  // the ArrowDown has been announced ends the drag on the row it started on,
  // which is an identity permutation and issues no PUT at all.
  await expect(liveRegion(page)).toContainText(/position 2 of 4/i)
  await page.keyboard.press('Space')

  const puts = await seam.callsTo('/downloads/reorder', 'PUT')
  expect(puts).toHaveLength(1)
  expect(puts[0].body).toEqual({ job_ids: ['dl-2', 'dl-1', 'dl-3', 'dl-4'] })
  await expect.poll(async () => seam.rowOrder()).toEqual(['dl-2', 'dl-1', 'dl-3', 'dl-4'])

  // setActivatorNodeRef is what gives dnd-kit its focus restoration; without it
  // focus lands on the body and the keyboard user is lost mid-list.
  // Polled, not read once: the drop reconciles the list from the PUT response,
  // and dnd-kit restores the activator focus after that re-render rather than
  // during it. The asserted end state is unchanged.
  await expect
    .poll(async () =>
      page.evaluate(() => {
        const el = document.activeElement
        return {
          testId: el?.getAttribute('data-testid') ?? null,
          jobId: el?.closest('[data-testid="queue-card"]')?.getAttribute('data-job-id') ?? null,
        }
      }),
    )
    .toEqual({ testId: 'queue-card-drag-handle', jobId: 'dl-1' })
  await app.close()
})

test('AC-49.28 a row drag never puts the list into its file-drop state', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page, { items: seededQueue() })
  await expect(page.getByTestId('queue-card')).toHaveCount(4)

  const list = page.getByTestId('queue-list')
  await expect(list).toHaveAttribute('data-drag-state', 'idle')

  // DRAG_STATE_ISOLATION_RULE — dnd-kit is pointer-events only and the drop
  // zone is HTML5 dragenter/dragover, so the two must not bleed into each
  // other. Checked at every stage of the gesture, since a merged context shows
  // the overlay mid-drag and then hides it again on drop.
  await grabRow(page, 'dl-1')
  await expect(list).toHaveAttribute('data-drag-state', 'idle')
  await expect(page.getByTestId('queue-drop-overlay')).toHaveCount(0)

  await dragOver(page, 'dl-3')
  await expect(list).toHaveAttribute('data-drag-state', 'idle')
  await expect(page.getByTestId('queue-drop-overlay')).toHaveCount(0)

  await page.mouse.up()
  await expect(list).toHaveAttribute('data-drag-state', 'idle')
  await expect(page.getByTestId('queue-drop-overlay')).toHaveCount(0)
  await app.close()
})

test('AC-49.36 every drag handle resolves to touch-action none on the rendered page', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page, { items: seededQueue() })
  await expect(page.getByTestId('queue-card')).toHaveCount(4)

  /*
    DND_TOUCH_ACTION_RULE. The computed value is asserted rather than the class
    name because a utility that is purged, overridden by a later rule, or lost
    to a specificity conflict still leaves `touch-none` in the source while the
    browser resolves `auto` — and under Pointer Events that hands every touch
    drag to the native scroll gesture instead of to dnd-kit. The mouse driver
    above cannot expose that.
  */
  const resolved = await page.$$eval('[data-testid="queue-card-drag-handle"]', (nodes) =>
    nodes.map((node) => window.getComputedStyle(node).touchAction),
  )
  expect(resolved, 'one handle per seeded row').toHaveLength(4)
  for (const value of resolved) {
    expect(value).toBe('none')
  }
  await app.close()
})

test('QUEUE_SCROLL_CONTAINER_RULE downloader scroller clears the ArrowDown clamp', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page, { items: seededQueue() })
  await expect(page.getByTestId('queue-card')).toHaveCount(4)

  const geo = await page.evaluate(() => {
    const box = (el: Element | null | undefined) =>
      el
        ? {
            h: (el as HTMLElement).clientHeight,
            tag: el.tagName,
            testid: el.getAttribute('data-testid'),
            className: (el as HTMLElement).className,
          }
        : null
    const main = document.querySelector('main')
    const pageRoot = document.querySelector('[data-testid="downloader-page"]')
    const region = document.querySelector('[data-testid="download-queue-region"]')
    const list = document.querySelector('[data-testid="queue-list"]')
    const scroller = list?.parentElement
    const form = pageRoot?.querySelector('form')
    const rows = [...document.querySelectorAll('[data-testid="queue-card"]')]
    const pitch =
      rows.length >= 2
        ? rows[1].getBoundingClientRect().top - rows[0].getBoundingClientRect().top
        : 0
    return {
      main: box(main),
      mainScroll: main?.scrollHeight ?? -1,
      mainOverflowY: main ? getComputedStyle(main).overflowY : null,
      page: box(pageRoot),
      form: box(form),
      region: box(region),
      header: box(document.querySelector('[data-testid="queue-selection-header"]')),
      bulk: box(document.querySelector('[data-testid="bulk-action-bar"]')),
      scroller: box(scroller),
      scrollerScroll: scroller?.scrollHeight ?? -1,
      scrollerOverflowY: scroller ? getComputedStyle(scroller).overflowY : null,
      summary: box(document.querySelector('[data-testid="queue-summary"]')),
      toolbar: box(document.querySelector('[data-testid="queue-toolbar"]')),
      pitch,
    }
  })

  expect(geo.pitch, JSON.stringify(geo)).toBeGreaterThan(50)
  expect(geo.scrollerOverflowY, JSON.stringify(geo)).toBe('auto')
  expect(geo.scroller?.h, JSON.stringify(geo)).toBeGreaterThanOrEqual(2 * geo.pitch)
  expect(geo.mainScroll, JSON.stringify(geo)).toBeLessThanOrEqual((geo.main?.h ?? -1) + 1)
  await app.close()
})

test('AC-52.6 downloader queue header is wired and preserves scroll geometry in real Electron', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page, { items: seededQueue(), processorState: 'Processing' })
  const region = page.getByTestId('download-queue-region')
  const header = region.getByTestId('queue-header-row')
  await expect(header).toHaveCount(1)
  await expect(header.getByTestId('queue-select-all')).toBeVisible()
  await expect(header.getByTestId('queue-summary')).toBeVisible()
  await expect(header.getByTestId('processor-indicator')).toContainText('Processing')
  await expect(header.getByTestId('queue-toolbar').locator('button')).toHaveCount(4)
  await expect(header.getByTestId('queue-summary').locator('[data-tone]')).toHaveCount(4)
  const before = await seam.calls()
  await header.getByTestId('queue-status-more').click()
  await expect(header.getByTestId('queue-status-details')).toContainText('AgeRestricted: 0')
  expect(await seam.calls()).toEqual(before)
  await header.getByTestId('queue-select-all').click()
  await expect(region.getByTestId('bulk-selection-count')).toContainText('4')
  await header.getByTestId('queue-toolbar-pause').click()
  await expect.poll(async () => (await seam.callsTo('/downloads/pause', 'POST')).length).toBe(1)
  await expect(header.getByTestId('queue-toolbar-resume')).toBeVisible()
  const layout = await region.evaluate((node) => {
    const header = node.querySelector('[data-testid="queue-header-row"]')
    const bulk = node.querySelector('[data-testid="bulk-action-bar"]')
    const list = node.querySelector('[data-testid="queue-list"]')
    const scroller = list?.parentElement
    return {
      height: (node as HTMLElement).getBoundingClientRect().height,
      order: Boolean(header && bulk && list &&
        (header.compareDocumentPosition(bulk) & Node.DOCUMENT_POSITION_FOLLOWING) &&
        (bulk.compareDocumentPosition(list) & Node.DOCUMENT_POSITION_FOLLOWING)),
      overflow: scroller ? getComputedStyle(scroller).overflowY : null,
    }
  })
  expect(layout.order).toBe(true)
  expect(layout.height).toBeGreaterThanOrEqual(320)
  expect(layout.overflow).toBe('auto')
  await app.close()
})

test('AC-52.6 downloader header wraps at narrow width and updates its live processor chip', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page, { items: seededQueue(), processorState: 'Processing' })
  await page.setViewportSize({ width: 700, height: 650 })
  const header = page.getByTestId('download-queue-region').getByTestId('queue-header-row')
  const selection = await header.getByTestId('queue-selection-header').boundingBox()
  const toolbar = await header.getByTestId('queue-toolbar').boundingBox()
  expect(selection).not.toBeNull()
  expect(toolbar).not.toBeNull()
  expect(toolbar!.y).toBeGreaterThan(selection!.y)
  await expect(header.getByTestId('queue-toolbar-pause')).toBeVisible()
  await header.getByTestId('queue-toolbar-pause').click()
  await expect.poll(async () => (await seam.callsTo('/downloads/pause', 'POST')).length).toBe(1)
  await expect(header.getByTestId('processor-indicator')).toContainText('Paused')
  await app.close()
})

test('AC-53.1/.2/.5 Downloader Add panel keeps one Enter POST, local Advanced state, and queue scroll', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page, { items: seededQueue() })
  await page.setViewportSize({ width: 1600, height: 900 })
  const url = page.getByTestId('url-input')
  const add = page.getByTestId('add-btn')
  const toggle = page.getByTestId('add-advanced-toggle')
  const form = page.getByTestId('downloader-page').locator('form')
  const formBox = await form.boundingBox()
  const urlBox = await url.boundingBox()
  const addBox = await add.boundingBox()
  expect(formBox).not.toBeNull()
  expect(urlBox).not.toBeNull()
  expect(addBox).not.toBeNull()
  expect(formBox!.width).toBeLessThanOrEqual(1153)
  expect(Math.abs(urlBox!.y - addBox!.y)).toBeLessThan(24)
  await expect(toggle).toHaveAttribute('aria-expanded', 'false')
  await expect(page.getByTestId('cookie-mode-none')).toBeHidden()
  await add.click()
  expect(seam.posts.count()).toBe(0)
  await url.fill('https://example.invalid/watch?v=layout53a')
  await url.press('Enter')
  await expect.poll(() => seam.posts.count()).toBe(1)
  await expect(page.getByTestId('queue-card')).toHaveCount(5)
  await expect(page.getByTestId('add-status')).toContainText('Queued')
  await url.fill('https://example.invalid/watch?v=layout53b')
  await add.click()
  await expect.poll(() => seam.posts.count()).toBe(2)
  const calls = await seam.callsTo('/downloads', 'POST')
  expect(calls).toHaveLength(2)
  expect(calls[0].body).toEqual({ url: 'https://example.invalid/watch?v=layout53a', quality: '1080p', audio_only: false, audio_format: 'default' })
  expect(calls[1].body).toEqual({ url: 'https://example.invalid/watch?v=layout53b', quality: '1080p', audio_only: false, audio_format: 'default' })
  await toggle.click()
  await expect(toggle).toHaveAttribute('aria-expanded', 'true')
  await expect(page.getByTestId('cookie-mode-none')).toBeVisible()
  expect(await seam.callsTo('/settings/downloader', 'PUT')).toHaveLength(0)
  const region = page.getByTestId('download-queue-region')
  const geometry = await region.evaluate((node) => {
    const list = node.querySelector('[data-testid="queue-list"]')
    return { height: (node as HTMLElement).getBoundingClientRect().height, overflow: list?.parentElement ? getComputedStyle(list.parentElement).overflowY : null }
  })
  expect(geometry.height).toBeGreaterThanOrEqual(320)
  expect(geometry.overflow).toBe('auto')
  await expect(region.getByTestId('queue-header-row')).toBeVisible()
  await app.close()
})

test('AC-53.2/.3/.4 configured cookies and SABR open Advanced with live radios and commands', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page, { items: seededQueue(), cookieMode: 'browser', sabrMode: 'active' })
  const toggle = page.getByTestId('add-advanced-toggle')
  await expect(toggle).toHaveAttribute('aria-expanded', 'true')
  for (const id of ['cookie-mode-none', 'cookie-mode-browser', 'cookie-mode-file']) {
    await expect(page.getByTestId(id)).toHaveAttribute('type', 'radio')
  }
  await expect(page.getByTestId('cookie-mode-browser')).toBeChecked()
  const warning = page.getByTestId('sabr-quality-chip')
  await expect(warning).toHaveAttribute('data-tone', 'warning')
  await expect(warning).toContainText('SABR')
  await expect(page.getByTestId('sabr-status')).toBeVisible()
  await page.getByTestId('cookie-mode-file').click()
  await expect.poll(async () => (await seam.callsTo('/settings/downloader', 'PUT')).length).toBe(1)
  expect((await seam.callsTo('/settings/downloader', 'PUT'))[0].body).toEqual({
    cookie_mode: 'file', cookie_browser: 'chrome', cookie_browser_profile: 'Default', cookie_file_path: '',
  })
  await expect(page.getByTestId('cookie-file')).toBeVisible()
  await expect(page.getByTestId('cookie-browser')).toBeHidden()
  for (const [id, path] of [
    ['sabr-check-btn', '/downloads/sabr/check'],
    ['sabr-force-btn', '/downloads/sabr/force'],
    ['sabr-clear-btn', '/downloads/sabr/clear'],
  ] as const) {
    await page.getByTestId(id).click()
    await expect.poll(async () => (await seam.callsTo(path, 'POST')).length).toBe(1)
  }
  await toggle.click()
  await expect(toggle).toHaveAttribute('aria-expanded', 'false')
  await expect(page.getByTestId('cookie-mode-file')).toBeHidden()
  expect(await seam.callsTo('/settings/downloader', 'PUT')).toHaveLength(1)
  await app.close()
})

test('AC-97.9 Ctrl+Enter adds as add-btn does and passes through the open palette', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page)
  // url-input empty: Ctrl+Enter must not post (add-btn has no disabled rule; the empty add returns early).
  await page.getByTestId('url-input').click()
  await page.keyboard.press('Control+Enter')
  await page.getByTestId('url-input').fill('https://example.invalid/watch?v=e2e0001')
  await page.keyboard.press('Control+Enter')
  await expect.poll(() => seam.posts.count()).toBe(1)
  await expect(page.getByTestId('queue-card')).toBeVisible({ timeout: 15_000 })
  expect(seam.posts.count(), 'the empty Ctrl+Enter posted nothing').toBe(1)

  await page.getByTestId('url-input').fill('https://example.invalid/watch?v=e2e0002')
  await page.getByTestId('header-palette-btn').click()
  await page.getByTestId('command-palette-input').fill('console')
  await page.keyboard.press('ArrowDown')
  await expect(page.getByTestId('command-palette').locator('[data-selected="true"]')).toContainText('Toggle console')
  await page.keyboard.press('Control+Enter')
  await expect.poll(() => seam.posts.count()).toBe(2)
  await expect(page.getByTestId('command-palette')).toHaveCount(0)
  await expect(page.getByTestId('console-panel')).toHaveCount(0)
  await app.close()
})
