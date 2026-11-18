// Session 91 (2026-11-17-e2e-pointer-flakes, D-1147, D-1148): one place for the pointer settle the
// E2E specs aim with. A target is read until two reads one frame apart agree (SETTLE), and a
// pointer point is used only once the page hit-tests it to the target (POINTER_ON). This file
// imports only types from the Playwright package, so the unit suite can load it. The queue drag
// helpers below moved here from download-queue.test.ts (POINTER_HELPERS_SHARED, D-1147), so the
// download and convert queue drags run the same driver; each takes the row's test id.
import type { Locator, Page } from '@playwright/test'

export type Box = { x: number; y: number; width: number; height: number }

/**
 * `SETTLE`: read, wait one frame, read again, and return the read as soon as two reads in a row
 * are equal by `JSON.stringify`. After `maxFrames` reads that never repeat it throws. The bound is
 * the 60 frames `settledCenter` has always used; no wall-clock bound is added.
 */
export async function settle<T>(read: () => Promise<T>, nextFrame: () => Promise<void>, maxFrames = 60): Promise<T> {
  let last = JSON.stringify(await read())
  for (let reads = 1; reads < maxFrames; reads += 1) {
    await nextFrame()
    const value = await read()
    const key = JSON.stringify(value)
    if (key === last) {
      return value
    }
    last = key
  }
  throw new Error('layout never settled: ' + last)
}

/** One animation frame in the page. */
function nextFrame(page: Page): () => Promise<void> {
  return () => page.evaluate(() => new Promise<void>((done) => requestAnimationFrame(() => done())))
}

/** `SETTLED_BOX`: the locator's box (or `null`) once it has held still for one frame. */
export function settledBox(page: Page, locator: Locator): Promise<Box | null> {
  return settle(() => locator.boundingBox(), nextFrame(page))
}

/**
 * `POINTER_ON`: the centre of the settled box, returned only once `document.elementFromPoint` at
 * that point is the target, an ancestor of it or a descendant of it, checked frame by frame. It
 * clicks and moves nothing.
 */
export async function pointerOn(page: Page, locator: Locator): Promise<{ x: number; y: number }> {
  const box = await settledBox(page, locator)
  if (box === null) {
    throw new Error('no box for the pointer target')
  }
  const point = { x: box.x + box.width / 2, y: box.y + box.height / 2 }
  const target = await locator.elementHandle()
  try {
    await page.waitForFunction(
      ({ element, x, y }) => {
        const hit = document.elementFromPoint(x, y)
        return hit !== null && (hit === element || element.contains(hit) || hit.contains(element))
      },
      { element: target, x: point.x, y: point.y },
      { polling: 'raf' },
    )
  } finally {
    await target.dispose()
  }
  return point
}

/** POINTER_HELPERS_SHARED: the queue row a helper reads; `queue-card` is the downloader's. */
export interface RowOptions {
  rowTestId?: string
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
export async function settledCenter(page: Page, locator: Locator): Promise<{ x: number; y: number }> {
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
export async function rowTransitionsIdle(page: Page, { rowTestId = 'queue-card' }: RowOptions = {}): Promise<void> {
  await page.waitForFunction(
    (row) =>
      document.getAnimations().every((animation) => {
        const target = (animation.effect as KeyframeEffect | null)?.target
        const onRow = target instanceof Element && (target.closest(row) !== null || target.querySelector(row) !== null)
        return !onRow || animation.playState !== 'running'
      }),
    `[data-testid="${rowTestId}"]`,
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
export async function windowSettled(page: Page): Promise<void> {
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
export async function grabRow(page: Page, id: string, { rowTestId = 'queue-card' }: RowOptions = {}): Promise<void> {
  const row = `[data-testid="${rowTestId}"][data-job-id="${id}"]`
  const handle = page.locator(row).getByTestId('queue-card-drag-handle')
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
    .locator(`${row} [data-testid="queue-card-drag-handle"][aria-pressed="true"]`)
    .waitFor()
}

/** Move the held pointer onto the vertical centre of another row. */
export async function dragOver(page: Page, id: string, { rowTestId = 'queue-card' }: RowOptions = {}): Promise<void> {
  const target = page.locator(`[data-testid="${rowTestId}"][data-job-id="${id}"]`)
  await target.waitFor()
  // Sortable rows move by transform only, so DOM order is still the pre-drag order.
  const order = await page
    .locator(`[data-testid="${rowTestId}"]`)
    .evaluateAll((cards) => cards.map((card) => card.getAttribute('data-job-id')))
  const position = order.indexOf(id) + 1
  const aim = await settledCenter(page, target)
  await page.mouse.move(aim.x, aim.y, { steps: 10 })
  // Let the sortable shift finish, then re-aim if the layout moved under the
  // pointer while it travelled (a transform alone never changes the aim).
  await rowTransitionsIdle(page, { rowTestId })
  const settled = await settledCenter(page, target)
  if (settled.x !== aim.x || settled.y !== aim.y) {
    await page.mouse.move(settled.x, settled.y, { steps: 2 })
    await rowTransitionsIdle(page, { rowTestId })
  }
  // `E2E_DRAG_COMMITTED_OVER` (Session 26 amendment A16). dnd-kit commits the
  // row under the pointer two React renders after the last pointermove, and the
  // drop reads whatever is committed at pointerup; a release that beats those
  // renders (a loaded Windows host) drops on the previous row. The over
  // announcement is emitted only once `over` is committed, so wait for it.
  try {
    await page
      .locator('[id^="DndLiveRegion"]')
      .filter({ hasText: `moved to position ${position} of ${order.length}.` })
      .waitFor({ state: 'attached' })
  } catch (error) {
    // Session 27 A-4: a timeout here used to leave no trace of the drag state (Playwright keeps
    // no page snapshot for Electron windows), so the failure carries it.
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
