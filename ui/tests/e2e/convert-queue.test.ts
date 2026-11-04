import { _electron, expect, test, type Page } from '@playwright/test'
import { mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import {
  addThemeProbe,
  expectInsertedOn,
  expectThemeColours,
  expectThemeHeld,
  isShown,
  releaseTheme,
  THEME_FLOORS,
  type ThemeProbeMode,
} from './theme-probe'

const here = dirname(fileURLToPath(import.meta.url))

/**
 * MEU-45 rewrite (E2E_REWRITE_RULE).
 *
 * The converter's 13 per-page toolbar ids are retired by the queue-card
 * migration. Every assertion that covered one of them is REPLACED here — never
 * deleted — by an assertion at the new home named in `RETIRED_TOOLBAR_CONTROLS`,
 * and each replacement satisfies `MOUNT_GATE_CLAUSE_4` (c)+(d): it locates the
 * home, PERFORMS the interaction, and asserts an observable outcome (the
 * intercepted request method+path+body, or the resulting DOM state). A control
 * that renders but is wired to nothing therefore fails this spec.
 *
 * Home coverage in this file (16 MEU-45 homes of 13 retired ids):
 *   convert-start       -> queue-toolbar-start                     (W8-7)
 *   convert-pause       -> queue-toolbar-pause                     (W8-7)
 *   convert-resume      -> queue-toolbar-resume                    (W8-7)
 *   convert-cancel      -> in-flight card primary action           (W8-8)
 *   convert-up          -> kebab move-up / Alt+ArrowUp             (W8-7)
 *   convert-down        -> kebab move-down / Alt+ArrowDown         (W8-7)
 *   convert-top         -> kebab move-top                          (W8-7)
 *   convert-bottom      -> kebab move-bottom                       (W8-7)
 *   convert-reset       -> card primary action Retry               (W8-8)
 *   convert-remove      -> kebab remove                            (W8-4)
 *   convert-clear-all   -> queue-toolbar-overflow > clear-all      (W8-4)
 *   convert-open-file   -> kebab open-file / Done primary action   (W8-8)
 *   convert-open-folder -> kebab open-folder                       (W8-8)
 */

type ConversionItem = {
  id: string
  kind: string
  input_path: string
  output_path: string | null
  display_name: string
  preset_id: string | null
  cq: number | null
  scale_height: number | null
  audio_mode: string | null
  gpu_encoder: string | null
  in_ms: number | null
  out_ms: number | null
  copy_mode: string | null
  stream_index: number | null
  status: string
  progress: number
  speed: string | null
  eta: string | null
  file_size: number | null
  queue_position: number
}

type SeamCall = { method: string; path: string; body: unknown }

/** What `addInitScript` carries into the renderer: the seed plus the sample row. */
type InitSeed = SeamSeed & { sample: ConversionItem }

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
 * `window.api` is a FROZEN contextBridge proxy whose `window` property is
 * non-writable and non-configurable - stubbing `window.api.openPath` from the
 * page is silently ignored, so the seam reads the renderer's own ledger instead.
 */
type ShellIpcEntry = { channel: string; target: string }

type SeamSeed = {
  items: ConversionItem[]
  processorState: ProcessorStateName
  currentJobId: string | null
  holdReorder: boolean
  reorderStatus: number
}

const sampleJob: ConversionItem = {
  id: 'e2e-convert-1',
  kind: 'compress',
  input_path: 'C:/e2e/sample.mp4',
  output_path: null,
  display_name: 'sample.mp4',
  preset_id: 'balanced',
  cq: 25,
  scale_height: 0,
  audio_mode: 'aac_128',
  gpu_encoder: null,
  in_ms: null,
  out_ms: null,
  copy_mode: null,
  stream_index: null,
  status: 'Pending',
  progress: 0,
  speed: null,
  eta: null,
  file_size: null,
  queue_position: 1,
}

function job(overrides: Partial<ConversionItem> & { id: string }): ConversionItem {
  return { ...sampleJob, display_name: overrides.id + '.mp4', ...overrides }
}

/** A four-row queue covering every status the card surface branches on. */
function seededQueue(): ConversionItem[] {
  return [
    job({ id: 'job-1', status: 'Pending', queue_position: 1 }),
    job({
      id: 'job-2',
      status: 'Processing',
      queue_position: 2,
      progress: 42,
      speed: '2.4x',
      eta: '00:31',
    }),
    job({
      id: 'job-3',
      status: 'Done',
      queue_position: 3,
      progress: 100,
      output_path: 'C:/e2e/out/job-3.mp4',
      file_size: 1048576,
    }),
    job({ id: 'job-4', status: 'Failed', queue_position: 4 }),
  ]
}

async function launchApp() {
  return _electron.launch({
    args: [resolve(here, '../../out/main/index.js')],
    env: {
      ...process.env,
      AVKIT_E2E: '1',
      AVKIT_APP_DATA: mkdtempSync(join(tmpdir(), 'avkit-e2e-convert-')),
    },
  })
}

function isConversionsCollection(pathname: string): boolean {
  return /\/conversions\/?$/.test(pathname)
}

type Seam = {
  posts: { count: () => number }
  converterPuts: { count: () => number }
  calls: () => Promise<SeamCall[]>
  callsTo: (path: string, method: string) => Promise<SeamCall[]>
  opened: () => Promise<string[]>
  revealed: () => Promise<string[]>
  rowOrder: () => Promise<string[]>
  releaseReorder: () => Promise<void>
}

async function installSeam(
  page: Page,
  seed?: Partial<SeamSeed>,
  options: { themeProbe?: ThemeProbeMode } = {},
): Promise<Seam> {
  const posts = { value: 0 }
  const converterPuts = { value: 0 }
  let converterSettings = {
    output_dir: '~/Videos/av-kit',
    default_preset: 'balanced',
    skip_existing: true,
    gpu_preference: 'auto',
  }
  await page.route((url) => url.pathname.includes('/health/dependencies'), async (route) => {
    await route.fulfill({
      json: { ffmpeg: { available: true, version: '7.1.2' }, yt_dlp: { available: true } },
    })
  })
  await page.route((url) => url.pathname.includes('/conversions/gpu'), async (route) => {
    await route.fulfill({
      json: {
        nvidia_nvenc: false,
        amd_amf: false,
        intel_qsv: false,
        vulkan: false,
        software_h265: true,
        software_h264: true,
        recommended_encoder: 'libx265',
        checked_at: '2026-08-26T00:00:00Z',
      },
    })
  })
  await page.route((url) => url.pathname.includes('/settings/converter'), async (route) => {
    const request = route.request()
    if (request.method() === 'PUT') {
      converterPuts.value += 1
      const body = request.postDataJSON() as typeof converterSettings
      converterSettings = { ...converterSettings, ...body }
      await route.fulfill({ json: converterSettings })
      return
    }
    await route.fulfill({ json: converterSettings })
  })
  const items: ConversionItem[] = []
  await page.route((url) => isConversionsCollection(url.pathname), async (route) => {
    const request = route.request()
    if (request.method() === 'POST') {
      posts.value += 1
      items.push({ ...sampleJob })
      await route.fulfill({ json: { items: [...items] } })
      return
    }
    if (request.method() === 'GET') {
      await route.fulfill({ json: { items: [...items], processor: { state: 'Idle', current_job_id: null } } })
      return
    }
    if (request.method() === 'DELETE') {
      items.splice(0, items.length)
      await route.fulfill({ status: 204, body: '' })
      return
    }
    await route.fulfill({ status: 202, body: '' })
  })
  await page.route((url) => url.pathname.includes('/conversions/'), async (route) => {
    const method = route.request().method()
    if (method === 'DELETE') {
      items.splice(0, items.length)
      await route.fulfill({ status: 204, body: '' })
      return
    }
    if (method === 'POST' || method === 'PUT') {
      await route.fulfill({ status: method === 'PUT' ? 200 : 202, json: { items: [...items] } })
      return
    }
    await route.fallback()
  })

  /*
    The renderer's fetch is stubbed in-page below, so requests never reach the
    Playwright route layer and its counters would read zero whatever the page
    did. This binding lets the in-page seam report the real POST count back to
    the test process, which is what `seam.posts` observes.
  */
  await page.exposeFunction('__e2eRecordConversionPost', () => {
    posts.value += 1
  })

  /*
    `addInitScript` serialises this function into the renderer, so it may close
    over NOTHING from this module - `sampleJob` and `isConversionsCollection`
    are not defined there. The sample row travels in the payload and the
    collection test is inlined; referencing them by name threw a ReferenceError
    inside window.fetch, which is why every seeded row silently failed to load.
  */
  const resolved: InitSeed = {
    items: seed?.items ?? [],
    processorState: seed?.processorState ?? 'Idle',
    currentJobId: seed?.currentJobId ?? null,
    holdReorder: seed?.holdReorder ?? false,
    reorderStatus: seed?.reorderStatus ?? 200,
    sample: { ...sampleJob },
  }

  if (options.themeProbe) {
    await addThemeProbe(page, options.themeProbe)
  }
  await page.addInitScript((initial: InitSeed) => {
    const state = window as unknown as {
      __e2eItems?: ConversionItem[]
      __e2eProcessor?: { state: string; current_job_id: string | null }
      __e2eCalls?: SeamCall[]
      __e2eIpc?: ShellIpcEntry[]
      __e2eConversionPosts?: number
      __e2eConverterPuts?: number
      __e2eReleaseReorder?: () => void
      __e2eConverterSettings?: {
        output_dir: string
        default_preset: string
        skip_existing: boolean
        gpu_preference: string
      }
    }
    state.__e2eItems = initial.items.map((row) => ({ ...row }))
    state.__e2eProcessor = { state: initial.processorState, current_job_id: initial.currentJobId }
    state.__e2eCalls = []
    state.__e2eIpc = []
    state.__e2eConversionPosts = 0
    state.__e2eConverterPuts = 0
    state.__e2eConverterSettings = {
      output_dir: '~/Videos/av-kit',
      default_preset: 'balanced',
      skip_existing: true,
      gpu_preference: 'auto',
    }

    const renumber = (): void => {
      ;(state.__e2eItems ?? []).forEach((row, index) => {
        row.queue_position = index + 1
      })
    }

    const original = window.fetch.bind(window)
    window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
      const method = (init?.method ?? 'GET').toUpperCase()
      // THEME_PROBE (MEU-94): looked up at request time, so the init-script order does not matter.
      const probed = (
        window as unknown as {
          __avkitThemeProbe?: { handle: (u: string, m: string, i?: RequestInit) => Promise<Response> | null }
        }
      ).__avkitThemeProbe?.handle(url, method, init)
      if (probed) return probed
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

      if (url.includes('/health/dependencies')) {
        return json({ ffmpeg: { available: true, version: '7.1.2' }, yt_dlp: { available: true } })
      }
      if (url.includes('/conversions/gpu')) {
        return json({
          nvidia_nvenc: false,
          amd_amf: false,
          intel_qsv: false,
          vulkan: false,
          software_h265: true,
          software_h264: true,
          recommended_encoder: 'libx265',
          checked_at: '2026-08-26T00:00:00Z',
        })
      }
      if (url.includes('/settings/converter')) {
        if (method === 'PUT') {
          state.__e2eConverterPuts = (state.__e2eConverterPuts ?? 0) + 1
          const body =
            typeof init?.body === 'string' && init.body.length > 0
              ? (JSON.parse(init.body) as Partial<NonNullable<typeof state.__e2eConverterSettings>>)
              : {}
          state.__e2eConverterSettings = {
            output_dir: body.output_dir ?? state.__e2eConverterSettings?.output_dir ?? '~/Videos/av-kit',
            default_preset: body.default_preset ?? state.__e2eConverterSettings?.default_preset ?? 'balanced',
            skip_existing: body.skip_existing ?? state.__e2eConverterSettings?.skip_existing ?? true,
            gpu_preference: body.gpu_preference ?? state.__e2eConverterSettings?.gpu_preference ?? 'auto',
          }
          return json(state.__e2eConverterSettings)
        }
        return json(state.__e2eConverterSettings)
      }

      // --- processor lifecycle (queue-toolbar start / pause-resume) ---------
      if (path.endsWith('/conversions/start') && method === 'POST') {
        const next = (state.__e2eItems ?? []).find((row) => row.status === 'Pending')
        state.__e2eProcessor = {
          state: 'Processing',
          current_job_id: next?.id ?? state.__e2eProcessor?.current_job_id ?? null,
        }
        if (next !== undefined) {
          next.status = 'Processing'
        }
        return new Response('', { status: 202 })
      }
      if (path.endsWith('/conversions/pause') && method === 'POST') {
        state.__e2eProcessor = {
          state: 'Paused',
          current_job_id: state.__e2eProcessor?.current_job_id ?? null,
        }
        return new Response('', { status: 202 })
      }
      if (path.endsWith('/conversions/resume') && method === 'POST') {
        state.__e2eProcessor = {
          state: 'Processing',
          current_job_id: state.__e2eProcessor?.current_job_id ?? null,
        }
        return new Response('', { status: 202 })
      }
      if (path.endsWith('/conversions/cancel') && method === 'POST') {
        const current = state.__e2eProcessor?.current_job_id ?? null
        const row = (state.__e2eItems ?? []).find((entry) => entry.id === current)
        if (row !== undefined) {
          row.status = 'Cancelled'
        }
        state.__e2eProcessor = { state: 'Idle', current_job_id: null }
        return new Response('', { status: 202 })
      }

      // --- reorder (REORDER_WIRE_CONTRACT) ----------------------------------
      if (path.endsWith('/conversions/reorder') && method === 'PUT') {
        if (initial.holdReorder) {
          await new Promise<void>((resolve) => {
            state.__e2eReleaseReorder = resolve
          })
          state.__e2eReleaseReorder = undefined
        }
        if (initial.reorderStatus >= 400) {
          return json({ detail: 'reorder rejected' }, initial.reorderStatus)
        }
        const order = (parsed as { job_ids?: string[] } | undefined)?.job_ids ?? []
        const current = state.__e2eItems ?? []
        const next: ConversionItem[] = []
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
        return json({ items: state.__e2eItems })
      }

      // --- per-row reset / delete -------------------------------------------
      const resetMatch = /\/conversions\/([^/]+)\/reset$/.exec(path)
      if (resetMatch !== null && method === 'POST') {
        const row = (state.__e2eItems ?? []).find((entry) => entry.id === resetMatch[1])
        if (row !== undefined) {
          row.status = 'Pending'
          row.progress = 0
        }
        return new Response('', { status: 202 })
      }

      const isCollection = /\/conversions\/?$/.test(path)
      if (isCollection && method === 'POST') {
        state.__e2eConversionPosts = (state.__e2eConversionPosts ?? 0) + 1
        void (
          window as unknown as { __e2eRecordConversionPost?: () => Promise<void> }
        ).__e2eRecordConversionPost?.()
        state.__e2eItems = [...(state.__e2eItems ?? []), { ...initial.sample }]
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
      const deleteMatch = /\/conversions\/([^/]+)$/.exec(path)
      if (deleteMatch !== null && method === 'DELETE') {
        state.__e2eItems = (state.__e2eItems ?? []).filter((row) => row.id !== deleteMatch[1])
        renumber()
        return new Response(null, { status: 204 })
      }
      if (url.includes('/conversions/') && (method === 'POST' || method === 'PUT')) {
        return new Response('', { status: 202 })
      }
      return original(input, init)
    }
  }, resolved)

  await page.reload()
  // THEME_GATE holds the route while a theme answer is held, so the shell is the ready signal then.
  const held = options.themeProbe !== undefined && 'hold' in options.themeProbe.theme
  await page.getByTestId(held ? 'app-shell' : 'downloader-page').waitFor()

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
    converterPuts: { count: () => converterPuts.value },
    calls,
    callsTo: async (path: string, method: string) => {
      const all = await calls()
      return all.filter((row) => row.path.endsWith(path) && row.method === method)
    },
    opened: async () => ipcTargets('openPath'),
    revealed: async () => ipcTargets('showItemInFolder'),
    rowOrder: async () =>
      page.$$eval('[data-testid="convert-queue-row"]', (nodes) =>
        nodes.map((node) => (node as HTMLElement).dataset.jobId ?? ''),
      ),
    releaseReorder: async () => {
      await page.evaluate(() => {
        ;(window as unknown as { __e2eReleaseReorder?: () => void }).__e2eReleaseReorder?.()
      })
    },
  }
}

/** Open one card's kebab and return the menu locator. */
async function openKebab(page: Page, id: string) {
  const row = page.locator(`[data-testid="convert-queue-row"][data-job-id="${id}"]`)
  await row.getByTestId('queue-card-kebab').click()
  const menu = page.getByTestId('queue-card-menu')
  await expect(menu).toBeVisible()
  return menu
}

test('W8-1 CONVERT_HOME shows convert-page and dropzone', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page)
  await page.getByTestId('nav-convert').click()
  await expect(page.getByTestId('convert-page')).toBeVisible()
  await expect(page.getByTestId('convert-dropzone')).toBeVisible()
  await app.close()
})

test('W8-2 nav-convert shows convert-page with zero POST /conversions', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page)
  await page.getByTestId('nav-convert').click()
  await expect(page.getByTestId('convert-page')).toBeVisible()
  const conversionPosts = await page.evaluate(() => {
    return (window as unknown as { __e2eConversionPosts?: number }).__e2eConversionPosts ?? 0
  })
  expect(conversionPosts).toBe(0)
  expect(seam.posts.count()).toBe(0)
  await app.close()
})

test('W8-3 convert controls visible interact presets fill toggles advanced and settings', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page)
  await page.getByTestId('nav-convert').click()
  await expect(page.getByTestId('convert-page')).toBeVisible()
  await expect(page.getByTestId('convert-task-compress')).toBeVisible()
  await expect(page.getByTestId('convert-task-cut')).toBeVisible()
  await expect(page.getByTestId('convert-task-extract')).toBeVisible()
  await expect(page.getByTestId('convert-dropzone')).toBeVisible()
  await expect(page.getByTestId('convert-browse')).toBeVisible()
  await expect(page.getByTestId('convert-add')).toBeVisible()
  await expect(page.getByTestId('convert-preset-archival')).toBeVisible()
  await expect(page.getByTestId('convert-preset-high_quality')).toBeVisible()
  await expect(page.getByTestId('convert-preset-balanced')).toBeVisible()
  await expect(page.getByTestId('convert-preset-sharing')).toBeVisible()
  await expect(page.getByTestId('convert-preset-mobile')).toBeVisible()
  await expect(page.getByTestId('convert-advanced')).toBeVisible()
  await expect(page.getByTestId('convert-gpu-chip')).toBeVisible()
  await expect(page.getByTestId('convert-output-dir')).toBeVisible()
  await expect(page.getByTestId('convert-skip-existing')).toBeVisible()
  await expect(page.getByTestId('convert-page-save')).toBeVisible()
  await expect(page.getByTestId('convert-queue')).toBeVisible()
  await expect(page.getByTestId('convert-queue-summary')).toBeVisible()
  await expect(page.getByTestId('convert-processor')).toBeAttached()

  // TOOLBAR_CONTROLS (DEC-2): the 13 retired per-page buttons collapse to a
  // four-control toolbar. Asserting the exact interactive census is what makes
  // a 5th control a failure rather than a silent regrowth.
  const toolbar = page.getByTestId('queue-toolbar')
  await expect(toolbar).toBeVisible()
  await expect(toolbar.getByTestId('queue-toolbar-start')).toBeVisible()
  await expect(toolbar.getByTestId('queue-toolbar-clear-finished')).toBeVisible()
  await expect(toolbar.getByTestId('queue-toolbar-overflow')).toBeVisible()
  const interactive = toolbar.locator(
    'button, [role="button"], [role="menuitem"], a[href], input, select, textarea',
  )
  await expect(interactive).toHaveCount(4)

  // EMPTY_STATE_CONTRACT (converter): an empty queue invites file intake, and
  // Browse routes to the page's EXISTING staging picker, not a new one.
  await expect(page.getByTestId('queue-empty-dropzone')).toBeVisible()
  await expect(page.getByTestId('queue-empty-browse')).toBeVisible()
  await expect(page.getByTestId('queue-drop-strip')).toHaveCount(0)
  await page.getByTestId('queue-empty-browse').click()
  await page.getByTestId('convert-add').click()
  await expect(page.getByTestId('convert-queue-row')).toHaveCount(1)
  await expect(page.getByTestId('queue-empty-dropzone')).toHaveCount(0)
  await expect(page.getByTestId('queue-drop-strip')).toBeVisible()

  await page.getByTestId('convert-preset-archival').click()
  await page.getByTestId('convert-preset-high_quality').click()
  await page.getByTestId('convert-preset-balanced').click()
  await page.getByTestId('convert-preset-sharing').click()
  await page.getByTestId('convert-preset-mobile').click()
  await page.getByTestId('convert-advanced').click()
  await expect(page.getByTestId('convert-gpu-refresh')).toBeVisible()
  await page.getByTestId('convert-gpu-refresh').click()
  await page.getByTestId('convert-task-cut').click()
  await expect(page.getByTestId('convert-cut-in')).toBeVisible()
  await expect(page.getByTestId('convert-cut-out')).toBeVisible()
  await page.getByTestId('convert-cut-in').fill('00:00:01.000')
  await page.getByTestId('convert-cut-out').fill('00:00:02.000')
  await page.getByTestId('convert-task-extract').click()
  await expect(page.getByTestId('convert-extract-first')).toBeVisible()
  await expect(page.getByTestId('convert-extract-all')).toBeVisible()
  await page.getByTestId('convert-extract-first').click()
  await page.getByTestId('convert-extract-all').click()
  await page.getByTestId('convert-task-compress').click()
  await page.getByTestId('convert-output-dir').fill('C:/e2e/outdir')
  await page.getByTestId('convert-skip-existing').click()
  await page.getByTestId('nav-settings').click()
  await expect(page.getByTestId('convert-settings')).toBeVisible()
  await expect(page.getByTestId('settings-leaf-converter-output_dir')).toBeVisible()
  await expect(page.getByTestId('settings-leaf-default_preset')).toBeVisible()
  await expect(page.getByTestId('settings-leaf-skip_existing')).toBeVisible()
  await expect(page.getByTestId('settings-leaf-gpu_preference')).toBeVisible()
  await expect(page.getByTestId('browse-convert-path-btn')).toBeVisible()
  await expect(page.getByTestId('convert-settings-save')).toBeVisible()
  await page.getByTestId('settings-leaf-converter-output_dir').fill('C:/e2e/convert-out')
  await page.getByTestId('settings-leaf-default_preset').click()
  await page.getByTestId('settings-leaf-skip_existing').click()
  await page.getByTestId('settings-leaf-gpu_preference').click()
  await page.getByTestId('browse-convert-path-btn').click()
  await expect(page.getByTestId('convert-settings-save')).toHaveClass(/btn-save-dirty/)
  const putsBeforeSave = await page.evaluate(() => {
    return (window as unknown as { __e2eConverterPuts?: number }).__e2eConverterPuts ?? 0
  })
  expect(putsBeforeSave).toBe(0)
  await page.getByTestId('convert-settings-save').click()
  await expect.poll(async () => {
    return page.evaluate(() => {
      return (window as unknown as { __e2eConverterPuts?: number }).__e2eConverterPuts ?? 0
    })
  }).toBe(1)
  await app.close()
})

test('W8-4 browse add row then kebab remove and overflow clear-all confirm flows', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page)
  expect(typeof page.route).toBe('function')
  await page.getByTestId('nav-convert').click()
  await page.getByTestId('convert-browse').click()
  await page.getByTestId('convert-add').click()
  await expect(page.getByTestId('convert-queue-row')).toBeVisible()

  // convert-remove -> kebab remove, confirmed through the shared ConfirmModal
  // (G20_RULE + RETIRED_TESTIDS). Cancelling must issue no DELETE at all.
  const menu = await openKebab(page, 'e2e-convert-1')
  await menu.locator('[data-menu-action="remove"]').click()
  await expect(page.getByTestId('confirm-modal')).toBeVisible()
  await expect(page.getByTestId('confirm-modal-confirm')).toHaveText('Remove')
  await page.getByTestId('confirm-modal-cancel').click()
  await expect(page.getByTestId('confirm-modal')).toHaveCount(0)
  expect(await seam.callsTo('/conversions/e2e-convert-1', 'DELETE')).toHaveLength(0)
  await expect(page.getByTestId('convert-queue-row')).toHaveCount(1)

  const reopened = await openKebab(page, 'e2e-convert-1')
  await reopened.locator('[data-menu-action="remove"]').click()
  await page.getByTestId('confirm-modal-confirm').click()
  await expect(page.getByTestId('convert-queue-row')).toHaveCount(0)
  const removals = await seam.callsTo('/conversions/e2e-convert-1', 'DELETE')
  expect(removals).toHaveLength(1)
  // CLEAR_FINISHED_SEMANTICS clause 5 - the queue record only, files stay.
  expect(removals[0].body).toBeUndefined()

  // convert-clear-all -> queue-toolbar-overflow > queue-toolbar-clear-all.
  await page.getByTestId('convert-browse').click()
  await page.getByTestId('convert-add').click()
  await expect(page.getByTestId('convert-queue-row')).toBeVisible()
  await page.getByTestId('queue-toolbar-overflow').click()
  await page.getByTestId('queue-toolbar-clear-all').click()
  await expect(page.getByTestId('confirm-modal')).toBeVisible()
  await page.getByTestId('confirm-modal-cancel').click()
  await expect(page.getByTestId('convert-queue-row')).toHaveCount(1)
  await page.getByTestId('queue-toolbar-overflow').click()
  await page.getByTestId('queue-toolbar-clear-all').click()
  await page.getByTestId('confirm-modal-confirm').click()
  await expect(page.getByTestId('convert-queue-row')).toHaveCount(0)
  const cleared = (await seam.calls()).filter(
    (row) => row.method === 'DELETE' && /\/conversions\/?$/.test(row.path),
  )
  expect(cleared).toHaveLength(1)
  await app.close()
})

test('W8-5 ENABLED_WHEN chrome on empty convert queue', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page)
  await page.getByTestId('nav-convert').click()

  // The retired per-page buttons were all disabled on an empty queue; the
  // surviving toolbar controls carry that same ENABLED_WHEN chrome, and the
  // per-row controls simply do not exist when there are no rows.
  await expect(page.getByTestId('queue-toolbar')).toBeVisible()
  await expect(page.getByTestId('queue-toolbar-start')).toBeDisabled()
  await expect(page.getByTestId('queue-toolbar-clear-finished')).toBeDisabled()
  // Red-phase correction (disclosed in the MEU-45 handoff): the original form
  // of this assertion demanded the pause control be ABSENT on an empty queue,
  // which contradicts TOOLBAR_CONTROLS ("exactly four interactive elements ...
  // in every state") and W8-3's own census. The capability it was checking —
  // that an unusable control carries the retired buttons' ENABLED_WHEN chrome —
  // is asserted here instead, together with PAUSE_SCOPE's one-button rule.
  await expect(page.getByTestId('queue-toolbar-pause')).toBeVisible()
  await expect(page.getByTestId('queue-toolbar-pause')).toBeDisabled()
  await expect(page.getByTestId('queue-toolbar-resume')).toHaveCount(0)
  await expect(page.getByTestId('convert-queue-row')).toHaveCount(0)
  await expect(page.getByTestId('queue-card-primary-action')).toHaveCount(0)
  await expect(page.getByTestId('queue-card-kebab')).toHaveCount(0)
  await page.getByTestId('queue-toolbar-overflow').click()
  await expect(page.getByTestId('queue-toolbar-clear-all')).toBeDisabled()
  await page.keyboard.press('Escape')
  await expect(page.getByTestId('queue-empty-dropzone')).toBeVisible()
  await expect(page.getByTestId('convert-page-save')).toBeEnabled()
  await app.close()
})

test('W8-6 convert:add empty staging focuses dropzone with POST /conversions 0', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page)
  await page.getByTestId('header-palette-btn').click()
  await page.getByTestId('command-palette-input').fill('convert:add')
  await expect(page.getByRole('dialog').getByRole('button', { name: 'Add conversion files' })).toHaveCount(0)
  await page.getByTestId('command-palette-input').fill('Convert')
  await page.getByRole('dialog').getByRole('button', { name: /^Convert( ?Ctrl\+4)?$/ }).click()
  await expect(page).toHaveURL(/#\/convert/)
  await page.getByTestId('header-palette-btn').click()
  await page.getByTestId('command-palette-input').fill('convert:add')
  await page.getByRole('dialog').getByRole('button', { name: 'Add conversion files' }).click()
  await expect(page.getByTestId('convert-dropzone')).toBeFocused()
  const conversionPosts = await page.evaluate(() => {
    return (window as unknown as { __e2eConversionPosts?: number }).__e2eConversionPosts ?? 0
  })
  expect(conversionPosts).toBe(0)
  expect(seam.posts.count()).toBe(0)
  await app.close()
})

test('W8-7 toolbar lifecycle and kebab/keyboard reorder replace the retired move buttons', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page, { items: seededQueue() })
  await page.getByTestId('nav-convert').click()
  await expect(page.getByTestId('convert-queue-row')).toHaveCount(4)
  expect(await seam.rowOrder()).toEqual(['job-1', 'job-2', 'job-3', 'job-4'])

  // convert-start / convert-pause / convert-resume -> the toolbar's start button
  // and the single pause-resume toggle. Each click asserts its request AND the
  // toolbar state it produces, so a button wired to nothing fails here.
  await page.getByTestId('queue-toolbar-start').click()
  expect(await seam.callsTo('/conversions/start', 'POST')).toHaveLength(1)
  await expect(page.getByTestId('queue-toolbar-pause')).toBeVisible()
  await page.getByTestId('queue-toolbar-pause').click()
  expect(await seam.callsTo('/conversions/pause', 'POST')).toHaveLength(1)
  await expect(page.getByTestId('queue-toolbar-resume')).toBeVisible()
  await expect(page.getByTestId('queue-toolbar-pause')).toHaveCount(0)
  await page.getByTestId('queue-toolbar-resume').click()
  expect(await seam.callsTo('/conversions/resume', 'POST')).toHaveLength(1)
  await expect(page.getByTestId('queue-toolbar-pause')).toBeVisible()

  // convert-up / convert-top -> kebab move-up / move-top. REORDER_WIRE_CONTRACT:
  // the body is the complete permutation, never {id, direction}.
  const menu = await openKebab(page, 'job-3')
  await menu.locator('[data-menu-action="move-up"]').click()
  const afterUp = await seam.callsTo('/conversions/reorder', 'PUT')
  expect(afterUp).toHaveLength(1)
  expect(afterUp[0].body).toEqual({ job_ids: ['job-1', 'job-3', 'job-2', 'job-4'] })
  expect(afterUp[0].body).not.toHaveProperty('direction')
  await expect.poll(async () => seam.rowOrder()).toEqual(['job-1', 'job-3', 'job-2', 'job-4'])

  const topMenu = await openKebab(page, 'job-4')
  await topMenu.locator('[data-menu-action="move-top"]').click()
  const afterTop = await seam.callsTo('/conversions/reorder', 'PUT')
  expect(afterTop).toHaveLength(2)
  expect(afterTop[1].body).toEqual({ job_ids: ['job-4', 'job-1', 'job-3', 'job-2'] })
  await expect.poll(async () => seam.rowOrder()).toEqual(['job-4', 'job-1', 'job-3', 'job-2'])

  // convert-down / convert-bottom -> kebab move-down / move-bottom.
  const downMenu = await openKebab(page, 'job-4')
  await downMenu.locator('[data-menu-action="move-down"]').click()
  const afterDown = await seam.callsTo('/conversions/reorder', 'PUT')
  expect(afterDown).toHaveLength(3)
  expect(afterDown[2].body).toEqual({ job_ids: ['job-1', 'job-4', 'job-3', 'job-2'] })
  await expect.poll(async () => seam.rowOrder()).toEqual(['job-1', 'job-4', 'job-3', 'job-2'])

  const bottomMenu = await openKebab(page, 'job-1')
  await bottomMenu.locator('[data-menu-action="move-bottom"]').click()
  const afterBottom = await seam.callsTo('/conversions/reorder', 'PUT')
  expect(afterBottom).toHaveLength(4)
  expect(afterBottom[3].body).toEqual({ job_ids: ['job-4', 'job-3', 'job-2', 'job-1'] })
  await expect.poll(async () => seam.rowOrder()).toEqual(['job-4', 'job-3', 'job-2', 'job-1'])

  // convert-up / convert-down also live on the keyboard: Alt+Arrow on a focused
  // card reorders, and a bare Arrow must not.
  const card = page.locator('[data-testid="convert-queue-row"][data-job-id="job-3"]')
  await card.getByTestId('queue-card-title').click()
  await card.press('Alt+ArrowUp')
  const afterAltUp = await seam.callsTo('/conversions/reorder', 'PUT')
  expect(afterAltUp).toHaveLength(5)
  expect(afterAltUp[4].body).toEqual({ job_ids: ['job-3', 'job-4', 'job-2', 'job-1'] })
  await expect.poll(async () => seam.rowOrder()).toEqual(['job-3', 'job-4', 'job-2', 'job-1'])

  await card.press('Alt+ArrowDown')
  const afterAltDown = await seam.callsTo('/conversions/reorder', 'PUT')
  expect(afterAltDown).toHaveLength(6)
  expect(afterAltDown[5].body).toEqual({ job_ids: ['job-4', 'job-3', 'job-2', 'job-1'] })

  await card.press('ArrowUp')
  expect(await seam.callsTo('/conversions/reorder', 'PUT')).toHaveLength(6)
  await app.close()
})

test('W8-8 card primary actions and kebab open items replace the retired row buttons', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page, {
    items: seededQueue(),
    processorState: 'Processing',
    currentJobId: 'job-2',
  })
  await page.getByTestId('nav-convert').click()
  await expect(page.getByTestId('convert-queue-row')).toHaveCount(4)

  const rowOf = (id: string) =>
    page.locator(`[data-testid="convert-queue-row"][data-job-id="${id}"]`)

  // PRIMARY_ACTION_MAP: a Pending row offers none at all.
  await expect(rowOf('job-1').getByTestId('queue-card-primary-action')).toHaveCount(0)

  // convert-open-file -> the Done row's primary action (IPC, not fetch).
  const done = rowOf('job-3').getByTestId('queue-card-primary-action')
  await expect(done).toHaveText('Open file')
  await done.click()
  await expect.poll(async () => seam.opened()).toEqual(['C:/e2e/out/job-3.mp4'])

  // convert-open-file / convert-open-folder -> the kebab's own items.
  const doneMenu = await openKebab(page, 'job-3')
  await expect(doneMenu.locator('[data-menu-action="open-file"]')).toBeVisible()
  await expect(doneMenu.locator('[data-menu-action="copy-location"]')).toHaveText('Copy path')
  await doneMenu.locator('[data-menu-action="open-file"]').click()
  await expect.poll(async () => seam.opened()).toHaveLength(2)

  const folderMenu = await openKebab(page, 'job-3')
  await folderMenu.locator('[data-menu-action="open-folder"]').click()
  await expect.poll(async () => seam.revealed()).toEqual(['C:/e2e/out/job-3.mp4'])

  // convert-reset -> the Failed row's Retry primary action.
  const retry = rowOf('job-4').getByTestId('queue-card-primary-action')
  await expect(retry).toHaveText('Retry')
  await retry.click()
  expect(await seam.callsTo('/conversions/job-4/reset', 'POST')).toHaveLength(1)
  await expect.poll(async () =>
    rowOf('job-4').getByTestId('queue-card-primary-action').count(),
  ).toBe(0)

  // convert-cancel -> the in-flight row's primary action. CANCEL_CONTROL_LABEL
  // is exact, and cancelling the queue from a card raises no confirm.
  const cancel = rowOf('job-2').getByTestId('queue-card-primary-action')
  await expect(cancel).toHaveAccessibleName('Cancel queue')
  await cancel.click()
  expect(await seam.callsTo('/conversions/cancel', 'POST')).toHaveLength(1)
  await expect(page.getByTestId('confirm-modal')).toHaveCount(0)
  await app.close()
})

/*
  MEU-47 — BULK_CONTROL_E2E_OBLIGATION on the converter.

  Every control this MEU introduces is clicked here and its OUTCOME asserted:
  the five BULK_BAR_ACTIONS, the queue-select-all header in all three
  SELECTION_HEADER_CONTRACT states, and the keyboard selection entry path.
  A control that renders but is wired to nothing fails this block —
  MOUNT_GATE_CLAUSE_4 (c)+(d) is satisfied by the assertion, not by the id.
*/

/** Six rows: two requeueable, two Done, and two that neither set admits. */
function bulkQueue(): ConversionItem[] {
  return [
    job({ id: 'job-1', status: 'Pending', queue_position: 1 }),
    job({ id: 'job-2', status: 'Failed', queue_position: 2 }),
    job({
      id: 'job-3',
      status: 'Done',
      queue_position: 3,
      progress: 100,
      output_path: 'C:/e2e/out/job-3.mp4',
      file_size: 1048576,
    }),
    job({ id: 'job-4', status: 'Cancelled', queue_position: 4 }),
    job({
      id: 'job-5',
      status: 'Done',
      queue_position: 5,
      progress: 100,
      output_path: 'C:/e2e/out/job-5.mp4',
      file_size: 2097152,
    }),
    job({ id: 'job-6', status: 'Skipped', queue_position: 6 }),
  ]
}

function convertRow(page: Page, id: string) {
  return page.locator(`[data-testid="convert-queue-row"][data-job-id="${id}"]`)
}

/** Tick one row's selection checkbox. */
async function selectRow(page: Page, id: string): Promise<void> {
  await convertRow(page, id).getByTestId('selection-checkbox').click()
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

test('W8-9 bulk retry re-queues the selected rows and clear-selection empties the bar', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page, { items: bulkQueue() })
  await page.getByTestId('nav-convert').click()
  await expect(page.getByTestId('convert-queue-row')).toHaveCount(6)

  // AC-47.4: with nothing selected the bar is ABSENT, not hidden.
  await expect(page.getByTestId('bulk-action-bar')).toHaveCount(0)

  // bulk-retry over CONVERT_REQUEUEABLE_STATUSES: Failed + Cancelled.
  await selectRow(page, 'job-2')
  await selectRow(page, 'job-4')
  const bar = page.getByTestId('bulk-action-bar')
  await expect(bar).toBeVisible()
  await expect(bar.getByTestId('bulk-selection-count')).toContainText('2')

  await bar.getByTestId('bulk-retry').click()
  await expect
    .poll(async () => (await seam.callsTo('/conversions/job-2/reset', 'POST')).length)
    .toBe(1)
  expect(await seam.callsTo('/conversions/job-4/reset', 'POST')).toHaveLength(1)

  // BULK_ENDPOINT_POLICY: a client-side fan-out of per-id endpoints, so the
  // untouched rows are never named and no /bulk path is ever requested.
  expect(await seam.callsTo('/conversions/job-1/reset', 'POST')).toHaveLength(0)
  expect(await seam.callsTo('/conversions/job-3/reset', 'POST')).toHaveLength(0)
  expect((await seam.calls()).filter((call) => call.path.includes('/bulk'))).toHaveLength(0)

  // SELECTION_MODEL: a completed bulk action clears the selection, so the bar
  // goes away on its own and the retried rows are Pending again.
  await expect(page.getByTestId('bulk-action-bar')).toHaveCount(0)
  await expect(convertRow(page, 'job-2').getByTestId('queue-card-primary-action')).toHaveCount(0)
  await dismissBulkToast(page)

  // bulk-clear-selection: the bar disappears and every checkbox is unticked.
  await selectRow(page, 'job-1')
  await selectRow(page, 'job-3')
  await expect(bar.getByTestId('bulk-selection-count')).toContainText('2')
  await bar.getByTestId('bulk-clear-selection').click()
  await expect(page.getByTestId('bulk-action-bar')).toHaveCount(0)
  const ticked = await page
    .locator('[data-testid="convert-queue-row"] [data-testid="selection-checkbox"]')
    .evaluateAll((nodes) => nodes.filter((node) => (node as HTMLInputElement).checked).length)
  expect(ticked, 'clear-selection unticks every row, not just the bar').toBe(0)

  // Clearing a selection touches nothing on the server.
  expect((await seam.calls()).filter((call) => call.method === 'DELETE')).toHaveLength(0)
  await app.close()
})

test('W8-10 bulk move-top and move-bottom send folded REORDER_WIRE_CONTRACT bodies', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page, { items: bulkQueue() })
  await page.getByTestId('nav-convert').click()
  await expect(page.getByTestId('convert-queue-row')).toHaveCount(6)
  expect(await seam.rowOrder()).toEqual(['job-1', 'job-2', 'job-3', 'job-4', 'job-5', 'job-6'])

  // BULK_REORDER_ALGORITHM: move-top walks the selection in REVERSED render
  // order and each body is the fold of the preceding accepted one.
  await selectRow(page, 'job-2')
  await selectRow(page, 'job-4')
  await page.getByTestId('bulk-move-top').click()

  await expect.poll(async () => (await seam.callsTo('/conversions/reorder', 'PUT')).length).toBe(2)
  const top = await seam.callsTo('/conversions/reorder', 'PUT')
  expect(top[0].body, 'step 1 lifts the LAST selected row').toEqual({
    job_ids: ['job-4', 'job-1', 'job-2', 'job-3', 'job-5', 'job-6'],
  })
  expect(top[1].body, 'step 2 folds from step 1, never from the initial order').toEqual({
    job_ids: ['job-2', 'job-4', 'job-1', 'job-3', 'job-5', 'job-6'],
  })
  for (const call of top) {
    expect(call.body).not.toHaveProperty('direction')
  }
  await expect
    .poll(async () => seam.rowOrder())
    .toEqual(['job-2', 'job-4', 'job-1', 'job-3', 'job-5', 'job-6'])
  await dismissBulkToast(page)

  // move-bottom walks the selection in render order, same fold.
  await selectRow(page, 'job-1')
  await selectRow(page, 'job-3')
  await page.getByTestId('bulk-move-bottom').click()

  await expect.poll(async () => (await seam.callsTo('/conversions/reorder', 'PUT')).length).toBe(4)
  const bottom = await seam.callsTo('/conversions/reorder', 'PUT')
  expect(bottom[2].body).toEqual({
    job_ids: ['job-2', 'job-4', 'job-3', 'job-5', 'job-6', 'job-1'],
  })
  expect(bottom[3].body).toEqual({
    job_ids: ['job-2', 'job-4', 'job-5', 'job-6', 'job-1', 'job-3'],
  })
  await expect
    .poll(async () => seam.rowOrder())
    .toEqual(['job-2', 'job-4', 'job-5', 'job-6', 'job-1', 'job-3'])

  expect((await seam.calls()).filter((call) => call.path.includes('/bulk'))).toHaveLength(0)
  await app.close()
})

test('W8-11 bulk remove confirms with the verb label and Clear finished sweeps only Done', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page, { items: bulkQueue() })
  await page.getByTestId('nav-convert').click()
  await expect(page.getByTestId('convert-queue-row')).toHaveCount(6)

  // AC-47.6 (USER_LOCKS): the confirm names the verb and the count, and
  // dismissing it issues nothing.
  await selectRow(page, 'job-1')
  await selectRow(page, 'job-6')
  await page.getByTestId('bulk-remove').click()
  await expect(page.getByTestId('confirm-modal')).toBeVisible()
  await expect(page.getByTestId('confirm-modal-confirm')).toHaveText('Remove 2 items')
  await page.getByTestId('confirm-modal-cancel').click()
  expect((await seam.calls()).filter((call) => call.method === 'DELETE')).toHaveLength(0)
  await expect(page.getByTestId('convert-queue-row')).toHaveCount(6)
  await expect(page.getByTestId('bulk-action-bar')).toBeVisible()

  await page.getByTestId('bulk-remove').click()
  await page.getByTestId('confirm-modal-confirm').click()
  await expect
    .poll(async () => seam.rowOrder())
    .toEqual(['job-2', 'job-3', 'job-4', 'job-5'])
  expect(await seam.callsTo('/conversions/job-1', 'DELETE')).toHaveLength(1)
  expect(await seam.callsTo('/conversions/job-6', 'DELETE')).toHaveLength(1)
  await dismissBulkToast(page)

  // AC-47.7 over a mixed queue: only CLEAR_FINISHED_SNAPSHOT_STATUSES rows go.
  // Failed and Cancelled rows are failure evidence the user has not seen yet.
  await page.getByTestId('queue-toolbar-clear-finished').click()
  await expect.poll(async () => seam.rowOrder()).toEqual(['job-2', 'job-4'])
  expect(await seam.callsTo('/conversions/job-3', 'DELETE')).toHaveLength(1)
  expect(await seam.callsTo('/conversions/job-5', 'DELETE')).toHaveLength(1)
  expect(await seam.callsTo('/conversions/job-2', 'DELETE')).toHaveLength(0)
  expect(await seam.callsTo('/conversions/job-4', 'DELETE')).toHaveLength(0)
  expect((await seam.calls()).filter((call) => call.path.includes('/bulk'))).toHaveLength(0)
  await app.close()
})

test('W8-12 queue-select-all cycles all three states and the keyboard starts a selection', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page, { items: bulkQueue() })
  await page.getByTestId('nav-convert').click()
  await expect(page.getByTestId('convert-queue-row')).toHaveCount(6)

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
  await selectRow(page, 'job-3')
  await expect(page.getByTestId('bulk-selection-count')).toContainText('1')
  expect(await selectAllState(page)).toEqual({ checked: false, indeterminate: true })
  await header.click()
  await expect(page.getByTestId('bulk-selection-count')).toContainText('6')
  expect(await selectAllState(page)).toEqual({ checked: true, indeterminate: false })

  await page.getByTestId('bulk-clear-selection').click()
  await expect(page.getByTestId('bulk-action-bar')).toHaveCount(0)

  // AC-47.10a keyboard entry path (G34_RULE): focus a row's own checkbox and
  // toggle it from the keyboard. A checkbox reachable only by mouse fails here.
  const box = convertRow(page, 'job-5').getByTestId('selection-checkbox')
  await box.focus()
  await expect(box).toBeFocused()
  await box.press('Space')
  await expect(page.getByTestId('bulk-action-bar')).toBeVisible()
  await expect(page.getByTestId('bulk-selection-count')).toContainText('1')
  expect(await selectAllState(page)).toEqual({ checked: false, indeterminate: true })
  await app.close()
})

// ---------------------------------------------------------------------------
// MEU-49 — pointer and keyboard drag reorder on the converter queue.
//
// The same gesture as the downloader's AC-49.25, on the other page, with the
// same exact-sequence assertion. It exists to prove the wiring is per-page:
// `DND_OPT_IN_RULE` puts drag behind an opt-in prop, so a QueueList that drags
// on the downloader can perfectly well be inert here.
// ---------------------------------------------------------------------------

/** The drag handle on one converter card. */
function convertHandleOf(page: Page, id: string) {
  return page
    .locator(`[data-testid="convert-queue-row"][data-job-id="${id}"]`)
    .getByTestId('queue-card-drag-handle')
}

/** Observe dnd-kit's deferred keyboard-sensor registration without a timing guess. */
async function watchConvertKeydownListeners(page: Page): Promise<void> {
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

function convertKeydownListenerCount(page: Page): Promise<number> {
  return page.evaluate(
    () => (window as unknown as { __keydownListeners?: number }).__keydownListeners ?? 0,
  )
}

/**
 * TA-28: a focused handle shows its hint at once, and a visible hint listens for Escape on the document. Wait
 * for that hint, then zero the count, so the wait after Space sees only the keyboard sensor's listener.
 */
async function settleConvertHandleHint(page: Page): Promise<void> {
  await expect(page.getByTestId('queue-card-drag-handle-hint')).toBeVisible()
  await page.evaluate(() => {
    const store = window as unknown as { __keydownListeners: number }
    store.__keydownListeners = 0
  })
}

test('AC-49.29 dragging a conversion onto the third row lands the exact order', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page, { items: seededQueue() })
  await page.getByTestId('nav-convert').click()
  await expect(page.getByTestId('convert-queue-row')).toHaveCount(4)
  expect(await seam.rowOrder()).toEqual(['job-1', 'job-2', 'job-3', 'job-4'])

  /*
    E2E_DRAG_DRIVER — page.mouse.down/move(steps)/up, never locator.dragTo().
    dnd-kit is pointer-events only and its PointerSensor needs intermediate
    pointermove events to cross DND_SENSOR_CONFIG's 5px activation distance;
    dragTo() emits too few, the drag never activates, and the assertion below
    would then be measuring nothing.
  */
  const handle = page
    .locator('[data-testid="convert-queue-row"][data-job-id="job-1"]')
    .getByTestId('queue-card-drag-handle')
  const from = await handle.boundingBox()
  if (from === null) {
    throw new Error('no drag handle rendered for job-1')
  }
  const target = page.locator('[data-testid="convert-queue-row"][data-job-id="job-3"]')
  const to = await target.boundingBox()
  if (to === null) {
    throw new Error('no card rendered for job-3')
  }

  await page.mouse.move(from.x + from.width / 2, from.y + from.height / 2)
  await page.mouse.down()
  await page.mouse.move(from.x + from.width / 2, from.y + from.height / 2 + 14, { steps: 5 })
  await page.mouse.move(to.x + to.width / 2, to.y + to.height / 2, { steps: 10 })
  await page.mouse.up()

  // MOVE_TO_INDEX_CONTRACT — the FINAL index against the PRE-MOVE array, so
  // [A,B,C,D] with A dropped on row 3 is [B,C,A,D]. The post-removal-index bug
  // ([B,A,C,D]) and an inert page ([A,B,C,D]) must both fail — never a weaker
  // "the order changed" check.
  const puts = await seam.callsTo('/conversions/reorder', 'PUT')
  expect(puts).toHaveLength(1)
  expect(puts[0].body).toEqual({ job_ids: ['job-2', 'job-3', 'job-1', 'job-4'] })
  expect(puts[0].body, 'REORDER_WIRE_CONTRACT — a permutation, never a direction').not.toHaveProperty(
    'direction',
  )
  await expect.poll(async () => seam.rowOrder()).toEqual(['job-2', 'job-3', 'job-1', 'job-4'])
  await app.close()
})

test('QUEUE_SCROLL_CONTAINER_RULE convert scroller clears the ArrowDown clamp', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page, { items: seededQueue() })
  await page.getByTestId('nav-convert').click()
  await expect(page.getByTestId('convert-queue-row')).toHaveCount(4)

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
    const pageRoot = document.querySelector('[data-testid="convert-page"]')
    const region = document.querySelector('[data-testid="convert-queue-region"]')
    const list = document.querySelector('[data-testid="convert-queue"]')
    const scroller = list?.parentElement
    const form = pageRoot?.querySelector('form')
    const rows = [...document.querySelectorAll('[data-testid="convert-queue-row"]')]
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
      summary: box(document.querySelector('[data-testid="convert-queue-summary"]')),
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

test('AC-52 custom-id keyboard drag returns focus to the moved converter handle [TA-28]', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page, { items: seededQueue(), holdReorder: true })
  await page.getByTestId('nav-convert').click()
  await expect(page.getByTestId('convert-queue-row')).toHaveCount(4)

  await watchConvertKeydownListeners(page)
  await convertHandleOf(page, 'job-1').focus()
  await settleConvertHandleHint(page)
  await page.keyboard.press('Space')
  await expect.poll(async () => convertKeydownListenerCount(page)).toBeGreaterThan(0)
  await page.keyboard.press('ArrowDown')
  await expect(page.locator('[id^="DndLiveRegion"]')).toContainText(/position 2 of 4/i)
  await page.keyboard.press('Space')

  await expect.poll(async () => (await seam.callsTo('/conversions/reorder', 'PUT')).length).toBe(1)
  await page.evaluate(
    () => new Promise<void>((resolve) => requestAnimationFrame(() => requestAnimationFrame(() => resolve()))),
  )
  await page.evaluate(() => (document.activeElement as HTMLElement | null)?.blur())
  await expect(page.locator('body')).toBeFocused()
  await seam.releaseReorder()

  const puts = await seam.callsTo('/conversions/reorder', 'PUT')
  expect(puts).toHaveLength(1)
  expect(puts[0].body).toEqual({ job_ids: ['job-2', 'job-1', 'job-3', 'job-4'] })
  await expect.poll(async () => seam.rowOrder()).toEqual(['job-2', 'job-1', 'job-3', 'job-4'])
  await expect
    .poll(async () =>
      page.evaluate(() => {
        const el = document.activeElement
        return {
          testId: el?.getAttribute('data-testid') ?? null,
          jobId: el?.closest('[data-testid="convert-queue-row"]')?.getAttribute('data-job-id') ?? null,
        }
      }),
    )
    .toEqual({ testId: 'queue-card-drag-handle', jobId: 'job-1' })
  await app.close()
})

test('AC-52 custom-id keyboard drag restores focus after a rejected reorder [TA-28]', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page, {
    items: seededQueue(),
    holdReorder: true,
    reorderStatus: 500,
  })
  await page.getByTestId('nav-convert').click()
  await expect(page.getByTestId('convert-queue-row')).toHaveCount(4)

  await watchConvertKeydownListeners(page)
  await convertHandleOf(page, 'job-1').focus()
  await settleConvertHandleHint(page)
  await page.keyboard.press('Space')
  await expect.poll(async () => convertKeydownListenerCount(page)).toBeGreaterThan(0)
  await page.keyboard.press('ArrowDown')
  await expect(page.locator('[id^="DndLiveRegion"]')).toContainText(/position 2 of 4/i)
  await page.keyboard.press('Space')

  await expect.poll(async () => (await seam.callsTo('/conversions/reorder', 'PUT')).length).toBe(1)
  await page.evaluate(
    () => new Promise<void>((resolve) => requestAnimationFrame(() => requestAnimationFrame(() => resolve()))),
  )
  await page.evaluate(() => (document.activeElement as HTMLElement | null)?.blur())
  await expect(page.locator('body')).toBeFocused()
  await seam.releaseReorder()

  await expect.poll(async () => seam.rowOrder()).toEqual(['job-1', 'job-2', 'job-3', 'job-4'])
  await expect
    .poll(async () =>
      page.evaluate(() => {
        const el = document.activeElement
        return {
          testId: el?.getAttribute('data-testid') ?? null,
          jobId: el?.closest('[data-testid="convert-queue-row"]')?.getAttribute('data-job-id') ?? null,
        }
      }),
    )
    .toEqual({ testId: 'queue-card-drag-handle', jobId: 'job-1' })
  await app.close()
})

test('AC-52.6 converter queue header is wired and preserves scroll geometry in real Electron', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page, { items: seededQueue(), processorState: 'Processing' })
  await page.getByTestId('nav-convert').click()
  const region = page.getByTestId('convert-queue-region')
  const header = region.getByTestId('queue-header-row')
  await expect(header).toHaveCount(1)
  await expect(header.getByTestId('queue-select-all')).toBeVisible()
  await expect(header.getByTestId('convert-queue-summary')).toBeVisible()
  await expect(header.getByTestId('convert-processor')).toContainText('Processing')
  await expect(header.getByTestId('queue-toolbar').locator('button')).toHaveCount(4)
  await expect(header.getByTestId('convert-queue-summary').locator('[data-tone]')).toHaveCount(4)
  const before = await seam.calls()
  await header.getByTestId('queue-status-more').click()
  await expect(header.getByTestId('queue-status-details')).toContainText('Cancelled: 0')
  expect(await seam.calls()).toEqual(before)
  await header.getByTestId('queue-select-all').click()
  await expect(region.getByTestId('bulk-selection-count')).toContainText('4')
  await header.getByTestId('queue-toolbar-pause').click()
  await expect.poll(async () => (await seam.callsTo('/conversions/pause', 'POST')).length).toBe(1)
  await expect(header.getByTestId('queue-toolbar-resume')).toBeVisible()
  const layout = await region.evaluate((node) => {
    const header = node.querySelector('[data-testid="queue-header-row"]')
    const bulk = node.querySelector('[data-testid="bulk-action-bar"]')
    const list = node.querySelector('[data-testid="convert-queue"]')
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

test('AC-52.6 converter header wraps at narrow width and updates its live processor chip', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page, { items: seededQueue(), processorState: 'Processing' })
  await page.getByTestId('nav-convert').click()
  await page.setViewportSize({ width: 700, height: 650 })
  const header = page.getByTestId('convert-queue-region').getByTestId('queue-header-row')
  const selection = await header.getByTestId('queue-selection-header').boundingBox()
  const toolbar = await header.getByTestId('queue-toolbar').boundingBox()
  expect(selection).not.toBeNull()
  expect(toolbar).not.toBeNull()
  expect(toolbar!.y).toBeGreaterThan(selection!.y)
  await expect(header.getByTestId('queue-toolbar-pause')).toBeVisible()
  await header.getByTestId('queue-toolbar-pause').click()
  await expect.poll(async () => (await seam.callsTo('/conversions/pause', 'POST')).length).toBe(1)
  await expect(header.getByTestId('convert-processor')).toContainText('Paused')
  await app.close()
})

test('AC-54.1/.2/.3/.7 Convert Zone 1 stages duplicate paths, removes one locally, and Adds one exact body', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seam = await installSeam(page, { items: seededQueue() })
  await page.getByTestId('nav-convert').click()
  await page.setViewportSize({ width: 1600, height: 900 })
  const panel = page.getByTestId('convert-add-panel')
  const bounds = await panel.boundingBox()
  expect(bounds).not.toBeNull()
  expect(bounds!.width).toBeLessThanOrEqual(1153)
  for (const [id, value] of [
    ['convert-task-compress', 'compress'],
    ['convert-task-cut', 'cut'],
    ['convert-task-extract', 'extract'],
  ] as const) {
    await expect(panel.getByTestId(id)).toHaveAttribute('type', 'radio')
    await expect(panel.getByTestId(id)).toHaveAttribute('value', value)
  }
  await expect(panel.getByTestId('convert-gpu-chip')).toContainText('Encoder: Software (libx265)')
  await expect(panel.getByTestId('convert-gpu-refresh')).toHaveCount(1)
  await expect(panel.getByTestId('convert-gpu-refresh')).toBeVisible()
  await panel.getByTestId('convert-gpu-refresh').click()
  await expect.poll(async () => (await seam.callsTo('/conversions/gpu/refresh', 'POST')).length).toBe(1)
  const browse = panel.getByTestId('convert-browse')
  const add = panel.getByTestId('convert-add')
  const browseBox = await browse.boundingBox()
  const addBox = await add.boundingBox()
  expect(browseBox).not.toBeNull()
  expect(addBox).not.toBeNull()
  expect(Math.abs(browseBox!.y - addBox!.y)).toBeLessThan(24)
  await browse.click()
  await browse.click()
  await expect(panel.getByTestId('convert-staged-remove')).toHaveCount(2)
  await expect(add).toContainText('Add (2)')
  const before = await seam.calls()
  await panel.getByTestId('convert-staged-remove').first().click()
  await expect(panel.getByTestId('convert-staged-remove')).toHaveCount(1)
  await expect(add).toContainText('Add (1)')
  expect(await seam.calls()).toEqual(before)
  await add.click()
  await expect.poll(async () => (await seam.callsTo('/conversions', 'POST')).length).toBe(1)
  expect((await seam.callsTo('/conversions', 'POST'))[0].body).toEqual({
    paths: ['C:/e2e/sample.mp4'], kind: 'compress', preset: 'balanced',
  })
  await expect(page.getByTestId('convert-queue-row')).toHaveCount(5)
  await app.close()
})

test('AC-54.4/.5/.6/.7 native choices, Advanced, explicit Save, carried metadata and queue scroll survive', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const items = [
    ...seededQueue().map((row) => row.id === 'job-3' ? { ...row, gpu_encoder: 'h264_nvenc' } : row),
    job({ id: 'job-5', status: 'Skipped', queue_position: 5, preset_id: null, gpu_encoder: null }),
  ]
  const seam = await installSeam(page, { items })
  await page.getByTestId('nav-convert').click()
  const panel = page.getByTestId('convert-add-panel')
  const preset = panel.getByTestId('convert-preset-mobile')
  await expect(preset).toHaveAttribute('type', 'radio')
  await expect(preset).toHaveAttribute('value', 'mobile')
  await preset.click()
  await expect(preset).toBeChecked()
  const advanced = panel.getByTestId('convert-advanced')
  await expect(advanced).toHaveAttribute('aria-expanded', 'false')
  await advanced.click()
  await expect(advanced).toHaveAttribute('aria-expanded', 'true')
  await expect(panel.getByLabel('CQ')).toBeVisible()
  await panel.getByTestId('convert-task-cut').click()
  await expect(panel.getByTestId('convert-advanced')).toHaveCount(0)
  await expect(panel.getByTestId('convert-copy-reencode')).toHaveAttribute('value', 'reencode')
  await panel.getByTestId('convert-copy-reencode').click()
  await expect(panel.getByTestId('convert-copy-reencode')).toBeChecked()
  await panel.getByTestId('convert-task-extract').click()
  await expect(panel.getByTestId('convert-extract-all')).toHaveAttribute('value', 'all')
  await panel.getByTestId('convert-extract-all').click()
  await expect(panel.getByTestId('convert-extract-all')).toBeChecked()
  const save = panel.getByTestId('convert-page-save')
  await expect(save).toHaveClass(/btn-ghost/)
  await panel.getByTestId('convert-output-dir').fill('C:/e2e/new-output')
  await expect(save).toHaveClass(/btn-primary/)
  await expect(save).toContainText('Save Changes')
  expect(await seam.callsTo('/settings/converter', 'PUT')).toHaveLength(0)
  await save.click()
  await expect.poll(async () => (await seam.callsTo('/settings/converter', 'PUT')).length).toBe(1)
  const doneMeta = page.locator('[data-testid="convert-queue-row"][data-job-id="job-3"]').getByTestId('queue-card-meta')
  await expect(doneMeta).toContainText('h264_nvenc')
  const fallbackMeta = page.locator('[data-testid="convert-queue-row"][data-job-id="job-5"]').getByTestId('queue-card-meta')
  await expect(fallbackMeta).toContainText('Compress')
  await expect(fallbackMeta).not.toContainText('undefined')
  const region = page.getByTestId('convert-queue-region')
  const geometry = await region.evaluate((node) => {
    const list = node.querySelector('[data-testid="convert-queue"]')
    return { height: (node as HTMLElement).getBoundingClientRect().height, overflow: list?.parentElement ? getComputedStyle(list.parentElement).overflowY : null }
  })
  expect(geometry.height).toBeGreaterThanOrEqual(320)
  expect(geometry.overflow).toBe('auto')
  await expect(region.getByTestId('queue-header-row')).toBeVisible()
  await app.close()
})

// MEU-94 (Session 40): THEME_PROBE, THEME_COLOURS and THEME_GATE on the Convert route.
test('AC-94.10 Convert cold boot with a stale dark mirror holds the route until the theme', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page, undefined, { themeProbe: { mirror: 'dark', theme: { hold: true } } })
  await page.getByTestId('nav-convert').click()
  await expectThemeHeld(page)
  await releaseTheme(page, 'light')
  await expect.poll(() => isShown(page, 'convert-advanced')).toBe(true)
  await page.getByTestId('convert-advanced').click()
  await expectInsertedOn(page, 'light', THEME_FLOORS.convert)
  await expectThemeColours(page, 'light', THEME_FLOORS.convert)
  await app.close()
})

test('AC-93.7 Convert Output folder Browse sits beside the field and fills it from the dialog', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page)
  await page.getByTestId('nav-convert').click()
  await expect.poll(() => isShown(page, 'convert-output-dir')).toBe(true)
  await expect.poll(() => isShown(page, 'convert-output-dir-browse')).toBe(true)
  const field = page.getByTestId('convert-output-dir')
  const fieldBox = await field.boundingBox()
  const browseBox = await page.getByTestId('convert-output-dir-browse').boundingBox()
  expect(fieldBox).not.toBeNull()
  expect(browseBox).not.toBeNull()
  if (fieldBox === null || browseBox === null) {
    return
  }
  // Beside: Browse is to the right of the field, on the same line.
  expect(browseBox.x).toBeGreaterThanOrEqual(fieldBox.x + fieldBox.width)
  expect(Math.abs(browseBox.y + browseBox.height / 2 - (fieldBox.y + fieldBox.height / 2))).toBeLessThan(fieldBox.height)
  await expect.poll(() => field.inputValue()).toBe('~/Videos/av-kit')
  await page.getByTestId('convert-output-dir-browse').click()
  await expect.poll(() => field.inputValue()).toBe('C:/e2e/outdir')
  await app.close()
})

test('AC-97.7 Ctrl+O browses on Convert and is inert on Downloader', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installSeam(page)
  await page.getByTestId('nav-downloader').click()
  await expect(page).toHaveURL(/#\/$/)
  await page.keyboard.press('Control+O')
  await expect(page).toHaveURL(/#\/$/)
  await page.getByTestId('nav-convert').click()
  await expect(page.getByTestId('convert-staged-remove')).toHaveCount(0)
  await page.keyboard.press('Control+O')
  await expect(page.getByTestId('convert-staged-remove')).toHaveCount(1)
  await expect(page.getByTestId('convert-add')).toContainText('Add (1)')
  await page.getByTestId('convert-add').click()
  await expect(page.getByTestId('convert-queue-row')).toHaveCount(1)
  await app.close()
})
