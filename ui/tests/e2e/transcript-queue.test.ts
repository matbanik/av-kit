import { _electron, expect, test, type Page } from '@playwright/test'
import { mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))

type SeamJob = {
  id: string
  channel_url: string
  channel_name: string
  status: string
  output_dir: string
  video_count: number
  transcripts_done: number
  word_count: number
  zip_path: string | null
  last_title: string | null
  last_item_status: string | null
  queue_position: number
  compiled_path?: string | null
  error_message: string | null
  created_at: string
  updated_at: string
}

const e2eJob: SeamJob = {
  id: 'e2e-1',
  channel_url: 'https://www.youtube.com/@e2e-invalid',
  channel_name: 'E2E',
  status: 'Pending',
  output_dir: 'C:/out/e2e',
  video_count: 10,
  transcripts_done: 4,
  word_count: 100,
  zip_path: 'C:/out/e2e/e2e_raw.zip',
  last_title: 'E2E last',
  last_item_status: 'Done',
  queue_position: 1,
  compiled_path: 'C:/out/e2e/compiled/e2e_vol1.md',
  error_message: null,
  created_at: '2026-08-20T00:00:00Z',
  updated_at: '2026-08-20T00:00:00Z',
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

async function installTranscriptSeam(page: Page): Promise<void> {
  await page.addInitScript(() => {
    const state = window as unknown as {
      __e2eSeamInstalled?: boolean
      __e2eCalls?: Array<{ url: string; method: string; bodyKeys?: string[] }>
      __e2eIpc?: Array<{ channel: string; target: string }>
      __e2eItems?: Array<Record<string, unknown>>
      __e2eProcessor?: { state: string; current_job_id: string | null }
    }
    state.__e2eSeamInstalled = true
    state.__e2eCalls = []
    state.__e2eIpc = []
    state.__e2eItems = state.__e2eItems ?? []
    state.__e2eProcessor = state.__e2eProcessor ?? { state: 'Idle', current_job_id: null }
    const original = window.fetch.bind(window)
    window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
      const method = (init?.method ?? 'GET').toUpperCase()
      let bodyKeys: string[] = []
      if (typeof init?.body === 'string' && init.body.length > 0) {
        bodyKeys = Object.keys(JSON.parse(init.body) as Record<string, unknown>).sort()
      }
      state.__e2eCalls?.push({ url, method, bodyKeys })
      const json = (body: unknown, status = 200) =>
        new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
      const settingsTranscript = url.includes('/settings/transcript')
      const transcripts = url.includes('/transcripts')
      if (settingsTranscript && method === 'GET') {
        return json({ delay_between_requests: 6 })
      }
      if (/\/transcripts\/?$/.test(new URL(url).pathname) && method === 'POST') {
        const body = JSON.parse(String(init?.body ?? '{}')) as Record<string, unknown>
        const keys = Object.keys(body).sort()
        if (JSON.stringify(keys) !== JSON.stringify(['channel_url'])) {
          return json({ error: { code: 'VALIDATION', message: 'CREATE_BODY' } }, 422)
        }
        const created = {
          id: 'e2e-1',
          channel_url: String(body.channel_url),
          channel_name: 'E2E',
          status: 'Pending',
          output_dir: 'C:/out/e2e',
          video_count: 10,
          transcripts_done: 4,
          word_count: 100,
          zip_path: 'C:/out/e2e/e2e_raw.zip',
          last_title: 'E2E last',
          last_item_status: 'Done',
          queue_position: 1,
          compiled_path: 'C:/out/e2e/compiled/e2e_vol1.md',
          error_message: null,
          created_at: '2026-08-20T00:00:00Z',
          updated_at: '2026-08-20T00:00:00Z',
        }
        state.__e2eItems = [created]
        return json(created, 201)
      }
      if (/\/transcripts\/?$/.test(new URL(url).pathname) && method === 'GET') {
        return json({
          items: state.__e2eItems ?? [],
          processor: state.__e2eProcessor ?? { state: 'Idle', current_job_id: null },
        })
      }
      if (url.includes('/transcripts/start') && method === 'POST') {
        state.__e2eProcessor = { state: 'Processing', current_job_id: 'e2e-1' }
        return new Response('', { status: 202 })
      }
      if (url.includes('/transcripts/pause') && method === 'POST') {
        state.__e2eProcessor = { state: 'Paused', current_job_id: 'e2e-1' }
        return new Response('', { status: 202 })
      }
      if (url.includes('/transcripts/resume') && method === 'POST') {
        state.__e2eProcessor = { state: 'Processing', current_job_id: 'e2e-1' }
        return new Response('', { status: 202 })
      }
      if (url.includes('/transcripts/stop') && method === 'POST') {
        state.__e2eProcessor = { state: 'Idle', current_job_id: null }
        return new Response('', { status: 202 })
      }
      if (url.includes('/transcripts/reorder') && method === 'PUT') {
        const body = JSON.parse(String(init?.body ?? '{}')) as { job_ids?: string[] }
        if (Array.isArray(body.job_ids)) {
          const byId = new Map((state.__e2eItems ?? []).map((item) => [String(item.id), item]))
          state.__e2eItems = body.job_ids
            .map((id) => byId.get(id))
            .filter((item): item is Record<string, unknown> => item !== undefined)
        }
        return new Response('', { status: 202 })
      }
      if (url.includes('/compile') && method === 'POST') {
        return json({ compiled_paths: ['C:/out/e2e/compiled/e2e_vol1.md'] })
      }
      if (url.includes('/requeue') && method === 'POST') {
        return new Response('', { status: 202 })
      }
      if (url.includes('/retry') && method === 'POST') {
        return new Response('', { status: 202 })
      }
      if (transcripts && method === 'DELETE') {
        state.__e2eItems = []
        return new Response(null, { status: 204 })
      }
      if (transcripts || settingsTranscript) {
        return new Response('E2E_SEAM_UNHANDLED', { status: 599 })
      }
      if (url.includes('/downloads/sabr')) {
        return json({ mode: 'inactive', source: null, checked_at: null })
      }
      if (url.includes('/settings/downloader')) {
        return json({ cookie_mode: 'none' })
      }
      if (url.includes('/downloads')) {
        return json({ items: [], processor: { state: 'Idle', current_job_id: null } })
      }
      return original(input, init)
    }
  })
  await page.reload()
  await page.getByTestId('downloader-page').waitFor()
  await page.evaluate(() => {
    const state = window as unknown as {
      __e2eIpc?: Array<{ channel: string; target: string }>
    }
    state.__e2eIpc = state.__e2eIpc ?? []
    const api = window.api
    if (api) {
      api.openPath = async (target: string) => {
        state.__e2eIpc?.push({ channel: 'openPath', target })
      }
    }
  })
}

async function openTranscript(page: Page): Promise<void> {
  await page.getByTestId('nav-transcript').click()
  await page.getByTestId('transcript-page').waitFor()
}

async function setQueue(
  page: Page,
  items: SeamJob[],
  processor: { state: string; current_job_id: string | null },
): Promise<void> {
  await page.evaluate(
    ({ nextItems, nextProcessor }) => {
      const state = window as unknown as {
        __e2eItems?: unknown[]
        __e2eProcessor?: { state: string; current_job_id: string | null }
      }
      state.__e2eItems = nextItems
      state.__e2eProcessor = nextProcessor
    },
    { nextItems: items, nextProcessor: processor },
  )
  await page.getByTestId('nav-downloader').click()
  await page.getByTestId('nav-transcript').click()
  await page.getByTestId('transcript-page').waitFor()
  if (items.length > 0) {
    await page.getByTestId('channel-card').first().waitFor()
  }
}

test('W2-1 TRANSCRIPT_HOME shows the page and channel field', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installTranscriptSeam(page)
  await openTranscript(page)
  await expect(page.getByTestId('transcript-page')).toBeVisible()
  await expect(page.getByTestId('channel-input')).toBeVisible()
  await app.close()
})

test('W2-2 nav from home via nav-transcript', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installTranscriptSeam(page)
  await page.getByTestId('nav-transcript').click()
  await expect(page.getByTestId('transcript-page')).toBeVisible()
  await app.close()
})

test('W2-3 page chrome EXTRA presence', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installTranscriptSeam(page)
  await openTranscript(page)
  await expect(page.getByTestId('channel-input')).toBeVisible()
  await expect(page.getByTestId('channel-url-hint')).toBeVisible()
  await expect(page.getByTestId('add-btn')).toBeVisible()
  // TA-3 (class A setup): per-card controls need a card; seed one Done channel.
  await setQueue(page, [{ ...e2eJob, status: 'Done' }], { state: 'Idle', current_job_id: null })
  await expect(page.getByTestId('start-btn')).toBeVisible()
  // TA-3 (class B, TR2): one Pause/Resume node whose id follows processor state.
  await expect(page.getByTestId('pause-btn')).toBeVisible()
  await expect(page.getByTestId('resume-btn')).toHaveCount(0)
  await expect(page.getByTestId('stop-btn')).toBeVisible()
  // TA-3 (class A): ▲ ▼ live on each card; per-card actions live in its kebab.
  const seeded = page.getByTestId('channel-card').first()
  await expect(seeded.getByTestId('up-btn')).toBeVisible()
  await expect(seeded.getByTestId('down-btn')).toBeVisible()
  await seeded.getByTestId('queue-card-kebab').click()
  await expect(seeded.getByTestId('remove-btn')).toBeVisible()
  await expect(seeded.getByTestId('compile-btn')).toBeVisible()
  await expect(seeded.getByTestId('view-compiled-btn')).toBeVisible()
  await expect(seeded.getByTestId('open-zip-btn')).toBeVisible()
  await expect(seeded.getByTestId('open-folder-btn')).toBeVisible()
  await expect(page.getByTestId('processor-indicator')).toBeAttached()
  await app.close()
})

test('W2-4 E2E_HAPPY_PATH via E2E_SEAM', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  const seamSrc = installTranscriptSeam.toString()
  expect(seamSrc).toContain('addInitScript')
  expect(seamSrc).toContain('__e2eSeamInstalled')
  expect(seamSrc).toContain('__e2eCalls')
  expect(seamSrc).toContain('E2E_SEAM_UNHANDLED')
  expect(seamSrc).toContain('channel_url')
  expect(seamSrc).toContain('reload')
  await installTranscriptSeam(page)
  await openTranscript(page)
  await page.getByTestId('channel-input').fill('https://www.youtube.com/@e2e-invalid')
  await expect(page.getByTestId('add-btn')).toBeEnabled()
  await page.getByTestId('add-btn').click()
  await expect(page.getByTestId('channel-card')).toBeVisible({ timeout: 15_000 })
  await expect(page.getByTestId('channel-card')).toContainText('E2E')
  await expect(page.getByTestId('channel-progress')).toBeVisible()
  // TA-4 (class B, TR5 / mockup §05 row 9): line 3 is the output tree on a
  // non-Processing card and the last title on the Processing card; rate/ETA are
  // Processing-only.
  await expect(page.getByTestId('output-tree')).toBeVisible()
  await setQueue(page, [{ ...e2eJob, status: 'Processing' }], { state: 'Processing', current_job_id: 'e2e-1' })
  await expect(page.getByTestId('last-title')).toBeVisible()
  await expect(page.getByTestId('rate-display')).toBeVisible()
  await expect(page.getByTestId('eta-display')).toBeVisible()
  await app.close()
})

test('W2-5 E2E_ACTUATE ENABLED_WHEN confirm and opens', async () => {
  // TA-5 (setup): reaching per-card actions through the kebab adds ~20 clicks;
  // under the transcript seam each click settles in ~2s, so the budget scales.
  test.setTimeout(180_000)
  const app = await launchApp()
  const page = await app.firstWindow()
  await installTranscriptSeam(page)
  await openTranscript(page)
  const second: SeamJob = { ...e2eJob, id: 'e2e-2', channel_name: 'E2E-2', queue_position: 2 }
  await setQueue(page, [e2eJob, second], { state: 'Idle', current_job_id: null })
  await page.getByTestId('channel-card').first().click()
  await expect(page.getByTestId('start-btn')).toBeEnabled()
  await page.getByTestId('start-btn').click()
  await expect
    .poll(async () =>
      page.evaluate(() =>
        (window as unknown as { __e2eCalls?: Array<{ url: string }> }).__e2eCalls?.some((row) =>
          row.url.includes('/transcripts/start'),
        ),
      ),
    )
    .toBe(true)
  await setQueue(page, [{ ...e2eJob, status: 'Processing' }], {
    state: 'Processing',
    current_job_id: 'e2e-1',
  })
  await expect(page.getByTestId('processor-indicator')).toBeVisible()
  await page.getByTestId('channel-card').click()
  await expect(page.getByTestId('pause-btn')).toBeEnabled()
  await page.getByTestId('pause-btn').click()
  await expect
    .poll(async () =>
      page.evaluate(() =>
        (window as unknown as { __e2eCalls?: Array<{ url: string }> }).__e2eCalls?.some((row) =>
          row.url.includes('/transcripts/pause'),
        ),
      ),
    )
    .toBe(true)
  await setQueue(page, [{ ...e2eJob, status: 'Paused' }], { state: 'Paused', current_job_id: 'e2e-1' })
  await page.getByTestId('channel-card').click()
  await expect(page.getByTestId('resume-btn')).toBeEnabled()
  await page.getByTestId('resume-btn').click()
  await expect
    .poll(async () =>
      page.evaluate(() =>
        (window as unknown as { __e2eCalls?: Array<{ url: string }> }).__e2eCalls?.some((row) =>
          row.url.includes('/transcripts/resume'),
        ),
      ),
    )
    .toBe(true)
  await setQueue(page, [{ ...e2eJob, status: 'Processing' }], {
    state: 'Processing',
    current_job_id: 'e2e-1',
  })
  await page.getByTestId('channel-card').click()
  await expect(page.getByTestId('stop-btn')).toBeEnabled()
  await page.getByTestId('stop-btn').click()
  await expect
    .poll(async () =>
      page.evaluate(() =>
        (window as unknown as { __e2eCalls?: Array<{ url: string }> }).__e2eCalls?.some((row) =>
          row.url.includes('/transcripts/stop'),
        ),
      ),
    )
    .toBe(true)
  await setQueue(page, [e2eJob, second], { state: 'Idle', current_job_id: null })
  await page.getByTestId('channel-card').nth(1).click()
  // TA-5 (class A): ▲ ▼ are scoped to the card they move; Remove is in its kebab.
  const movable = page.getByTestId('channel-card').nth(1)
  await expect(movable.getByTestId('up-btn')).toBeEnabled()
  await movable.getByTestId('up-btn').click()
  const moved = page.locator('[data-testid="channel-card"][data-job-id="e2e-2"]')
  await expect(page.getByTestId('channel-card').first()).toHaveAttribute('data-job-id', 'e2e-2')
  await moved.getByTestId('queue-card-kebab').click()
  await expect(moved.getByTestId('remove-btn')).toBeEnabled()
  await page.keyboard.press('Escape')
  await expect(moved.getByTestId('down-btn')).toBeEnabled()
  await moved.getByTestId('down-btn').click()
  await expect
    .poll(async () =>
      page.evaluate(() =>
        (window as unknown as { __e2eCalls?: Array<{ url: string }> }).__e2eCalls?.some((row) =>
          row.url.includes('/transcripts/reorder'),
        ),
      ),
    )
    .toBe(true)
  await setQueue(page, [{ ...e2eJob, status: 'Done', transcripts_done: 4 }], {
    state: 'Idle',
    current_job_id: null,
  })
  await page.getByTestId('channel-card').click()
  // TA-5 (class A): per-card actions are reached through the card kebab.
  await page.getByTestId('queue-card-kebab').click()
  await expect(page.getByTestId('compile-btn')).toBeEnabled()
  await page.getByTestId('compile-btn').click()
  await expect
    .poll(async () =>
      page.evaluate(() =>
        (window as unknown as { __e2eCalls?: Array<{ url: string }> }).__e2eCalls?.some((row) =>
          row.url.includes('/compile'),
        ),
      ),
    )
    .toBe(true)
  await page.getByTestId('queue-card-kebab').click()
  await expect(page.getByTestId('remove-btn')).toBeEnabled()
  await expect(page.getByTestId('view-compiled-btn')).toBeEnabled()
  await page.getByTestId('view-compiled-btn').click()
  await page.getByTestId('queue-card-kebab').click()
  await expect(page.getByTestId('open-zip-btn')).toBeEnabled()
  await page.getByTestId('open-zip-btn').click()
  await page.getByTestId('queue-card-kebab').click()
  await expect(page.getByTestId('open-folder-btn')).toBeEnabled()
  await page.getByTestId('open-folder-btn').click()
  await expect
    .poll(async () =>
      page.evaluate(
        () => (window as unknown as { __e2eIpc?: Array<{ channel: string }> }).__e2eIpc?.length ?? 0,
      ),
    )
    .toBeGreaterThan(0)
  await setQueue(page, [{ ...e2eJob, status: 'Cancelled' }], { state: 'Idle', current_job_id: null })
  await page.getByTestId('channel-card').click()
  await page.getByTestId('queue-card-kebab').click()
  await expect(page.getByTestId('requeue-btn')).toBeVisible()
  await page.getByTestId('requeue-btn').click()
  await expect
    .poll(async () =>
      page.evaluate(() =>
        (window as unknown as { __e2eCalls?: Array<{ url: string }> }).__e2eCalls?.some((row) =>
          row.url.includes('/requeue'),
        ),
      ),
    )
    .toBe(true)
  await setQueue(page, [{ ...e2eJob, status: 'Failed' }], { state: 'Idle', current_job_id: null })
  await page.getByTestId('channel-card').click()
  await page.getByTestId('queue-card-kebab').click()
  await expect(page.getByTestId('retry-btn')).toBeVisible()
  await page.getByTestId('retry-btn').click()
  await expect
    .poll(async () =>
      page.evaluate(() =>
        (window as unknown as { __e2eCalls?: Array<{ url: string }> }).__e2eCalls?.some((row) =>
          row.url.includes('/retry'),
        ),
      ),
    )
    .toBe(true)
  await setQueue(page, [e2eJob], { state: 'Idle', current_job_id: null })
  await page.getByTestId('channel-card').click()
  await page.getByTestId('queue-card-kebab').click()
  await page.getByTestId('remove-btn').click()
  await expect(page.getByTestId('remove-confirm-btn')).toBeVisible()
  await expect(page.getByTestId('remove-confirm-cancel')).toBeVisible()
  await page.keyboard.press('Escape')
  await page.getByTestId('queue-card-kebab').click()
  await page.getByTestId('remove-btn').click()
  await page.getByTestId('remove-confirm-cancel').click()
  const deletesBeforeConfirm = await page.evaluate(
    () =>
      (window as unknown as { __e2eCalls?: Array<{ method: string }> }).__e2eCalls?.filter(
        (row) => row.method === 'DELETE',
      ).length ?? 0,
  )
  await page.getByTestId('queue-card-kebab').click()
  await page.getByTestId('remove-btn').click()
  await page.getByTestId('remove-confirm-btn').click()
  await expect
    .poll(async () =>
      page.evaluate(
        () =>
          (window as unknown as { __e2eCalls?: Array<{ method: string }> }).__e2eCalls?.filter(
            (row) => row.method === 'DELETE',
          ).length ?? 0,
      ),
    )
    .toBe(deletesBeforeConfirm + 1)
  await app.close()
})

test('W2-6 PALETTE_DELIVER transcript:add focuses channel-input on its page', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installTranscriptSeam(page)
  await page.getByTestId('header-palette-btn').click()
  await page.getByTestId('command-palette-input').fill('transcript:add')
  await expect(page.getByRole('dialog').getByRole('button', { name: 'Enter transcript channel URL' })).toHaveCount(0)
  await page.getByTestId('command-palette-input').fill('Transcript')
  await page.getByRole('dialog').getByRole('button', { name: /^Transcript( ?Ctrl\+2)?$/ }).click()
  await expect(page).toHaveURL(/#\/transcript/)
  await page.getByTestId('header-palette-btn').click()
  await page.getByTestId('command-palette-input').fill('transcript:add')
  await page.getByRole('dialog').getByRole('button', { name: 'Enter transcript channel URL' }).click()
  await expect(page.getByTestId('channel-input')).toBeFocused()
  await app.close()
})

async function ledger(page: Page): Promise<Array<{ url: string; method: string; bodyKeys?: string[] }>> {
  return page.evaluate(
    () => (window as unknown as { __e2eCalls?: Array<{ url: string; method: string; bodyKeys?: string[] }> }).__e2eCalls ?? [],
  )
}

async function ipcTargets(page: Page): Promise<string[]> {
  return page.evaluate(() =>
    ((window as unknown as { __e2eIpc?: Array<{ target: string }> }).__e2eIpc ?? []).map((row) => row.target),
  )
}

function channel(page: Page, name: string) {
  return page.getByTestId('channel-card').filter({ has: page.getByText(name, { exact: true }) })
}

const doneJob: SeamJob = { ...e2eJob, id: 'e2e-a', channel_name: 'Alpha', status: 'Done', queue_position: 1 }
const processingJob: SeamJob = {
  ...e2eJob,
  id: 'e2e-b',
  channel_name: 'Bravo',
  status: 'Processing',
  transcripts_done: 2,
  zip_path: null,
  compiled_path: null,
  last_title: 'Episode 3',
  queue_position: 2,
}
const failedJob: SeamJob = { ...e2eJob, id: 'e2e-c', channel_name: 'Charlie', status: 'Failed', queue_position: 3 }
const cancelledJob: SeamJob = { ...e2eJob, id: 'e2e-d', channel_name: 'Delta', status: 'Cancelled', queue_position: 4 }

test('AC-55.7 header chips, More, processor chip, rate chip and the three-action toolbar', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installTranscriptSeam(page)
  await openTranscript(page)
  await setQueue(page, [doneJob, processingJob, failedJob], { state: 'Processing', current_job_id: 'e2e-b' })
  const header = page.getByTestId('queue-header-row')
  await expect(header.getByRole('heading', { name: 'Channels' })).toBeVisible()
  const summary = header.getByTestId('transcript-queue-summary')
  await expect(summary).toContainText('Processing')
  await expect(summary).toContainText('Done')
  await expect(summary).toContainText('Failed')
  await expect(summary).not.toContainText('Pending')
  await header.getByTestId('queue-status-more').click()
  await expect(header.getByTestId('queue-status-details')).toContainText('Pending: 0')
  await expect(header.getByTestId('processor-indicator')).toBeVisible()
  await expect(header.getByTestId('transcript-rate-chip')).toContainText('ETA')
  const group = header.getByRole('group', { name: 'Transcript queue actions' })
  await expect(group.getByRole('button')).toHaveCount(3)
  await expect(group.getByTestId('resume-btn')).toHaveCount(0)
  await group.getByTestId('pause-btn').click()
  await expect.poll(async () => (await ledger(page)).some((row) => row.url.includes('/transcripts/pause'))).toBe(true)
  await setQueue(page, [doneJob, { ...processingJob, status: 'Paused' }], { state: 'Paused', current_job_id: 'e2e-b' })
  await expect(page.getByTestId('pause-btn')).toHaveCount(0)
  await page.getByTestId('resume-btn').click()
  await expect.poll(async () => (await ledger(page)).some((row) => row.url.includes('/transcripts/resume'))).toBe(true)
  await setQueue(page, [doneJob], { state: 'Idle', current_job_id: null })
  await expect(page.getByTestId('processor-indicator')).toBeHidden()
  await expect(page.getByTestId('processor-indicator')).toBeAttached()
  await expect(page.getByTestId('transcript-rate-chip')).toHaveCount(0)
  await app.close()
})

test('AC-55.7 card select, kebab and status links reach the existing commands', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installTranscriptSeam(page)
  await openTranscript(page)
  await setQueue(page, [doneJob, failedJob, cancelledJob], { state: 'Idle', current_job_id: null })
  await channel(page, 'Charlie').getByRole('button', { name: 'Select channel Charlie' }).click()
  await expect(channel(page, 'Charlie')).toHaveClass(/border-accent\/50/)
  await channel(page, 'Alpha').getByTestId('queue-card-kebab').click()
  await expect(channel(page, 'Alpha')).toHaveClass(/border-accent\/50/)
  await expect(channel(page, 'Charlie')).not.toHaveClass(/border-accent\/50/)
  const menu = channel(page, 'Alpha').getByTestId('queue-card-menu')
  await expect(menu.getByRole('menuitem')).toHaveCount(5)
  await menu.getByTestId('view-compiled-btn').click()
  await expect.poll(async () => ipcTargets(page)).toContain('C:/out/e2e/compiled/e2e_vol1.md')
  await channel(page, 'Alpha').getByTestId('open-zip-link').click()
  await expect.poll(async () => ipcTargets(page)).toContain('C:/out/e2e/e2e_raw.zip')
  await channel(page, 'Charlie').getByTestId('retry-link').click()
  await expect.poll(async () => (await ledger(page)).some((row) => row.url.includes('/e2e-c/retry'))).toBe(true)
  await channel(page, 'Delta').getByTestId('requeue-link').click()
  await expect.poll(async () => (await ledger(page)).some((row) => row.url.includes('/e2e-d/requeue'))).toBe(true)
  await expect(channel(page, 'Alpha').getByTestId('retry-link')).toHaveCount(0)
  await app.close()
})

test('AC-55.7 card-scoped ▲ ▼ reorder with disabled ends, and the queue keeps its height', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installTranscriptSeam(page)
  await openTranscript(page)
  await setQueue(page, [doneJob, failedJob, cancelledJob], { state: 'Idle', current_job_id: null })
  await expect(channel(page, 'Alpha').getByTestId('up-btn')).toBeDisabled()
  await expect(channel(page, 'Delta').getByTestId('down-btn')).toBeDisabled()
  await channel(page, 'Delta').getByTestId('up-btn').click()
  await expect
    .poll(async () => page.getByTestId('channel-card').evaluateAll((nodes) => nodes.map((node) => node.getAttribute('data-job-id'))))
    .toEqual(['e2e-a', 'e2e-d', 'e2e-c'])
  await expect(channel(page, 'Delta')).toHaveClass(/border-accent\/50/)
  const region = page.getByTestId('queue-list').locator('xpath=ancestor::*[contains(@class,"min-h-[20rem]")][1]')
  const box = await region.boundingBox()
  expect(box?.height ?? 0).toBeGreaterThanOrEqual(320)
  const scroller = page.getByTestId('queue-list').locator('xpath=..')
  await expect(scroller).toHaveClass(/overflow-auto/)
  await expect(page.getByTestId('queue-list')).not.toHaveClass(/overflow-auto/)
  await app.close()
})

test('AC-55.7 empty state focuses the field and the header wraps at a narrow window', async () => {
  const app = await launchApp()
  const page = await app.firstWindow()
  await installTranscriptSeam(page)
  await openTranscript(page)
  await setQueue(page, [], { state: 'Idle', current_job_id: null })
  const invite = page.getByTestId('transcript-empty-invite')
  await expect(invite).toBeVisible()
  const before = (await ledger(page)).filter((row) => row.method !== 'GET').length
  await invite.getByTestId('transcript-empty-invite-action').click()
  await expect(page.getByTestId('channel-input')).toBeFocused()
  expect((await ledger(page)).filter((row) => row.method !== 'GET')).toHaveLength(before)
  await app.evaluate(({ BrowserWindow }) => {
    BrowserWindow.getAllWindows()[0]?.setSize(760, 760)
  })
  const header = page.getByTestId('queue-header-row')
  const group = header.getByRole('group', { name: 'Transcript queue actions' })
  await expect(group.getByTestId('stop-btn')).toBeInViewport()
  const headerBox = await header.boundingBox()
  const groupBox = await group.boundingBox()
  expect(groupBox && headerBox ? groupBox.x + groupBox.width <= headerBox.x + headerBox.width + 1 : false).toBe(true)
  await app.close()
})
