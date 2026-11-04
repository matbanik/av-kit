# Row 9 — drag E2E failures: measured root cause

Status: **row 9 in progress**. Pointer path fixed and verified; keyboard path
diagnosed, fix not yet applied. Written at a session pause so the diagnosis does
not have to be re-derived.

## What failed

Full Playwright run before any fix: **73 passed / 6 failed**.

| Case | Symptom |
|---|---|
| AC-49.25 | order came out `[dl-2,dl-3,dl-4,dl-1]`, expected `[dl-2,dl-3,dl-1,dl-4]` |
| AC-49.26 | live region read `position 4 of 4`, expected `position 3 of 4` |
| AC-49.29 | same as AC-49.25, converter queue |
| AC-49.27 | **0** reorder PUTs — the row never moved |
| `command-palette-nav.spec.ts:22` | non-MEU, green at the session-21 baseline — still untriaged |
| `download-queue.test.ts:723` (W1-9) | non-MEU, green at the session-21 baseline — still untriaged |

## One shared cause

The queue is **not its own scroll container**. Its nearest scrollable ancestor is
the page shell's `<main>`, and the list sits at the bottom of it. Measured in
Electron (window 739px tall):

```
MAIN.flex-1 min-h-0 overflow-auto  rect=40-739  client=699  scrollH=848  maxScroll=148.5
rows                               dl-1:548-602  dl-2:610-664  dl-3:672-726  dl-4:734-788
```

`<main>`'s vertical midpoint is 389.5. **Every row is below it**, and dl-4 is
almost entirely below `<main>`'s visible bottom (739). dnd-kit measures both of
its scroll behaviours against that container:

1. **Pointer — auto-scroll.** Default `threshold {x:0.2,y:0.2}` + `acceleration:10`
   puts the trigger band over the rows themselves. Telemetry, two 10px steps
   after grabbing dl-1:
   ```
   STEP y=599 live="…position 1 of 4." scroll[MAIN=0]
   STEP y=609 live="…position 3 of 4." scroll[MAIN=100]
   STEP y=619 live="…position 4 of 4." scroll[MAIN=149]   <- maximum
   ```
   The shell hit its maximum scroll before the pointer reached the next row, so
   `over` skipped dl-3 and resolved to dl-4.

2. **Keyboard — the scroll clamp.** `KeyboardSensor.handleKeyDown` clamps the
   target coordinate to `[container.top, container.bottom - height/2]` and, when
   the clamp bites and the container can still scroll, **scrolls instead of
   moving and returns**. Instrumented `coordinateGetter` + patched
   `Element.prototype.scrollTo`:
   ```
   PROBEGETTER code=ArrowDown collisionRect={"top":547.5,…} rects=4 enabled=4 result={"x":216,"y":609.5}
   KEYS ["win Space dp=true",
         "scrollTo MAIN.flex-1 min-h-0 ove {\"top\":62,\"behavior\":\"smooth\"}",
         "win ArrowDown dp=true", "win Space dp=true"]
   puts=[]
   ```
   The getter resolved dl-2 correctly (`y=609.5`); dnd-kit discarded it and
   issued a scroll. 609.5 > 389.5, so this fires on **every** ArrowDown here —
   the row can never move. (`<main>` is genuinely scrollable: setting
   `scrollTop` directly gives `after=62`, `max=148.5`.)

An earlier probe also showed `dp=false` on an ArrowDown pressed immediately after
`Space`: `KeyboardSensor.attach()` adds its document listener inside a
`setTimeout`, and Chromium prioritises the input task over the pending timer, so
a fast synthetic ArrowDown can arrive before the sensor is listening. Not the
root cause — with a settle wait the sensor handles the key and still refuses to
move — but any keyboard-drag spec needs a settle after activation.

## Fix applied so far (pointer only)

`QueueList.tsx` — `DND_AUTOSCROLL_CONFIG` on `DndContext`:

```tsx
autoScroll={{ threshold: { x: 0, y: 0.05 }, acceleration: 5 }}
```

Verified by probe: `scroll=0` for the whole drag, PUT body
`{"job_ids":["dl-2","dl-3","dl-1","dl-4"]}`, resulting order
`["dl-2","dl-3","dl-1","dl-4"]` — exactly AC-49.25. Typecheck and build both
`EXIT=0` after the probe was removed.

Source: dnd-kit auto-scroller options (`threshold`, `acceleration`) are the
documented control surface; issue #1414 records that the relative default is too
aggressive on large containers.

Caveat to close before this is durable: dl-3's centre (699) clears the 5% band
(704–739) by only **5px**. The drag specs should reveal the queue (scroll it into
view) before grabbing, so the assertion does not sit on a 5px cliff.

## Fix still owed (keyboard, AC-49.27)

Configuration cannot reach the keyboard clamp — it is unconditional in
`KeyboardSensor` (identical on `master`, so not a version issue). The three
candidates, with the plan contracts they touch:

1. **Give the queue list its own bounded scroll container** so the rows sit at
   the *top* of the container dnd-kit measures, and `<main>` stops overflowing.
   Fixes both paths at the source, keeps `DND_SENSOR_CONFIG`,
   `DND_HANDLE_CONTRACT` and the announcements untouched. Cost: a layout change
   to `DownloaderPage` / `ConvertPage` (fixed chrome, scrolling queue — the
   pattern every production queue UI uses). **Recommended.**
2. A hand-written keyboard sensor that always moves. Violates
   `DND_SENSOR_CONFIG` (which names `KeyboardSensor` +
   `sortableKeyboardCoordinates`) and re-implements library internals whose
   fields are `private`.
3. Our own keyboard reorder mode on the handle, dropping `KeyboardSensor`. Also
   violates `DND_SENSOR_CONFIG`, and needs its own live region.

Either 2 or 3 requires a plan amendment and reviewer sign-off; 1 does not.
