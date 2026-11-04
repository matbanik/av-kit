---
project: "2026-08-27-p9-capture-native-picker"
date: "2026-08-27"
source: "docs/build-plan/09-screenshot-capture.md"
meus: ["MEU-40"]
status: "draft"
template_version: "2.0"
---

# Implementation Plan: Native Region Picker (Capture overlay replacement)

> **Project**: `2026-08-27-p9-capture-native-picker`
> **Build Plan Section(s)**: `docs/build-plan/09-screenshot-capture.md` §Electron OS surface, §ShareX source map; `docs/build-plan/07-distribution.md` §extraResources
> **Status**: `draft`

---

## Goal

Replace the Chromium-based F2 region picker with a native Windows helper, and make the
spec say so.

MEU-39 shipped region capture as a **transparent Electron `BrowserWindow` overlay** fed by a
**`desktopCapturer` freeze-frame** (`ui/src/main/capture-overlay.ts`). That architecture is the
root cause of the observed failure: on a non-trivial slice of Windows GPU configurations,
Electron transparent windows render as an opaque **black click-through sheet**
([electron/electron#40515](https://github.com/electron/electron/issues/40515) — transparency
not respected, black background, with hardware acceleration enabled), and `desktopCapturer`
thumbnails are slow (all monitors captured to produce one) and have their own black-frame
class of bugs. ShareX — the spec's own intent source — never puts a compositor in this slot:
`RegionCaptureLightForm` is a plain opaque WinForms window painting a frozen GDI bitmap.

**The fix (Human-approved 2026-08-27, USER_EXPLICIT via AskUserQuestion):**

1. **Sidecar toolchain: C# WinForms on .NET 8** (SDK 8.0.424 verified installed —
   `C:/Temp/av-kit/toolchain.txt`). A ~200-line helper: freeze the display under the cursor
   via GDI (`Graphics.CopyFromScreen` ≙ `BitBlt`), show an **opaque** borderless topmost
   fullscreen Form painting that frozen bitmap, rubber-band drag, Enter/release confirm,
   Esc cancel, crop, write PNG, exit. No transparency, no compositor, no Chromium.
2. **The Chromium overlay path is deleted entirely** — no fallback. Overlay
   `BrowserWindow`, `desktopCapturer` freeze, overlay preload/renderer/vite entries all go.

Electron keeps everything it is good at and already ships approved: tray, global F2,
single-instance, inbox watch, settings poll, interactive-MCP poll, filmstrip page,
annotation, and the `POST /captures` register flow. Only the "pick a rectangle + grab
pixels" slot moves to the native helper. The Python `mss` adapter (MCP fullscreen/region
bbox path) is untouched.

This is a **spec revision + implementation** project: `09-screenshot-capture.md` currently
mandates the `BrowserWindow`/`desktopCapturer` design at lines 168, 183, 544 and 576, so the
build plan is rewritten first, then implemented as **MEU-40 `native-region-picker`**.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/graph.json and graphify-out-research/graph.json do not exist (verified 2026-08-27, ls receipt); Headroom anticipates no large eligible payloads — scope is direct source reads of ~15 known files plus exact-evidence test receipts, all bypass classes"
  human_message_reference: null
```

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| `MEU-40` | `.agent/context/handoffs/2026-08-27-p9-capture-native-picker-MEU-40-handoff.md` |

Rolling project review: `.agent/context/handoffs/2026-08-27-p9-capture-native-picker-implementation-critical-review.md`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Spec revision: 09-screenshot-capture.md + 07-distribution.md | — | `shared` | Revised build-plan files |
| WP-2 | Register MEU-40 in `meu-status.yaml`, render registry | WP-1 | `shared` | `.agent/context/meu-registry.md` render receipt |
| WP-3 | C# helper: xunit RED → WinForms implementation GREEN → publish wiring | WP-1 | `shared` | `native/region-picker/**`, `C:/Temp/av-kit/dotnet-test.txt` |
| WP-4 | Electron integration: vitest RED → `capture-picker.ts` GREEN → overlay deletion | WP-3 | `compact_continue` | `ui/src/main/capture-picker.ts`, `C:/Temp/av-kit/ui-test.txt`; compact then re-read `task.md` + this plan |
| WP-5 | BUILD_PLAN.md audit + closeout (H1/review/H2 per task.md) | WP-4 | `compact_continue` | Handoff + review + reflection artifacts; compact then re-read `task.md` |

**Harness note (conflict flagged per AGENTS.md §Communication Policy).** The driving harness
for this session is **Claude Code**, whose `harness-profiles.md` default is
`plan_to_exec_gate: human`. `.agent/context/harness.local.md` names `driver: Cursor IDE`
with `plan_to_exec_gate: reviewer-auto` and `fresh_worker: none`. AGENTS.md §Session
Discipline is explicit that the local file's flags win, so `reviewer-auto` governs and an
`approved` plan verdict auto-continues to execution. This is recorded rather than silently
resolved because the two sources disagree on the *driver name*. The disagreement has no
operational effect on row scheduling: `fresh_worker: none` means every row is
`shared`/`compact_continue` and no work is delegated to a builder subagent, so the
`builder_model` column is `—` throughout and the Cursor-vs-Claude-Code builder catalogs
never come into play.

### Executable gates owned by this plan folder

Every gate below is an on-disk script in this plan folder, and every one carries a
`-SelfTest` negative oracle proving it is not vacuous (`assert-oracle-selftests.ps1` runs
all of them in one receipt). No task row may cite a validator that does not exist.

| Gate | Script | Negative oracle |
|---|---|---|
| `TASK_ROW_GATE` | `assert-task-rows.ps1` | status is parsed positively from the row's last cell and fails closed: `[/]`, an unknown marker, a missing or unterminated marker, and two markers in one cell are each rejected (round-4 finding R4-1); a synthetic table with 2 open rows must be detected; a predicate matching 0 rows is itself a failure |
| `RED_ORACLE` | `assert-red-oracle.ps1 -Suite {dotnet\|vitest}` | green suite, unrelated compile failure, and absent receipt all rejected — a Red phase that never went red is not a Red phase |
| `OVERLAY_DELETION` | `assert-overlay-deleted.ps1` | round-11 finding R11-4: scanning `ui/src` alone let a stale `ui/out` bundle ship the deleted overlay inside the installer. Every root in `OVERLAY_SCAN_ROOTS` is now scanned for `OVERLAY_FORBIDDEN_TOKEN` **and** for `overlay*` build artifacts by name, because a minified bundle need not contain the source token verbatim (oracle O3 is exactly that case: a token-free `preload/overlay.js`). O1 clean tree, O2 token present, O4 an absent root reads as empty rather than erroring |
| `PACKAGING_CLEAN_PATH` | `assert-packaging-clean.ps1 [-Installed]` | the default mode proves the picker is **built** by the production `dist` chain: exact `&&`-segment composition, every `PICKER_PREP_REQUIRED_SEGMENTS` entry present **and in order** so the clean cannot be dropped (P5) or moved behind the builds it must precede (P6), every `PICKER_PUBLISH_REQUIRED_SEGMENTS` fragment present so a framework-dependent publish that dies on a machine with no .NET runtime is refused (P7), and a clean rebuild from an emptied publish dir. `-Installed` proves the package is **clean and resolvable**: silent-install the NSIS output to a temp prefix, find the helper at `INSTALLED_PICKER_REL`, run it with bogus argv expecting `PICKER_EXIT_ERROR`, and scan the installed tree for overlay leftovers. Dev-tree path resolution proves nothing about the shipped app |
| `E2E_WIRED` | `assert-e2e-wired.ps1 -Mode {Wired\|Executed}` | comment-only markers, a spec that never declares the required case titles, and an unran / failed / skipped / flaky / short / wrong-file / stale Playwright JSON report are all rejected; an `echo`-fronted or `&&`-split npm script is reported as printing the command rather than running it, and a segment that merely *starts with* the head's characters no longer counts as the head (S6e). A `[B]` on this row must carry an objective class, a reproduced `ERROR_SIGNATURE` in its own receipt, and a registered follow-up (Y1–Y4) |
| `VERIFICATION_ADJUDICATION` | `run-verification-plan.ps1 -SelfTest` | the runner decides whether a red step is a failure or a `[B]`, so it is a gate. One rule, six oracles: J1 a genuinely blocked step with its error reproduced in **its own** receipt is excused; J2 a signature that appears only in some other step's receipt is not; J3 `BLOCKED=no` keeps a red run a failure; J4 a subjective class is never a valid `[B]`; J5 an unregistered follow-up id is a well-formed string, not a linked task; J6 no disposition on disk means the failure stands. The inventory check additionally fails if any section names a gate script that is not on disk, or if a deferrable section declares no disposition file |
| `RUN_ARM` | `arm-run.ps1 -Name e2e-capture` | a deleted artifact, and an artifact predating its arming stamp, are both rejected; only an artifact written after arming is accepted (round-5 finding R4-3-R5 — a stale green report from an earlier run used to satisfy the executed-E2E gate) |
| `BUILD_PLAN_HUB` | `assert-build-plan-hub.ps1` | today's hub text is pinned as oracle H0 and **must fail**, so the predicate is provably non-vacuous; a bare `desktopCapturer` line, a capitalised `Overlay`, and a hub that never names the replacement are each rejected; a line that frames the old word against the `region picker` replacement is accepted (round-5 finding R5-1) |
| `HANDOFF_MARKER_CHECK` / `HANDOFF_AC_SET` | `assert-handoff-markers.ps1`, `assert-handoff-acs.ps1` | plan must expose exactly `AC_COUNT` ACs or the extraction is treated as drifted |
| `EXEC_REVIEW_DISPATCH` / `CHECK_EXEC_REVIEW` | `assert-exec-review-dispatch.ps1`, `tools/check_exec_review.py` (exists) | self-authored or stale `approved` file rejected |
| `CLOSEOUT_GATE` | `assert-closeout.ps1` | aggregates all of the above |

**Round-11 scaffolding retirement (non-blocking reviewer note, adopted).** Four gates and
about 3,700 lines of PowerShell are **deleted**, not disabled: `PICKER_BINDING`
(`assert-picker-binding.ps1`, 1,256 lines of Roslyn source-shape policing),
`SMOKE_DISPOSITION` + `SMOKE_PRODUCER` (`assert-smoke-disposition.ps1`,
`run-live-smoke.ps1`, and the run-nonce/arming identity protocol they needed),
`REFLECTION_QUALITY` (`assert-reflection-quality.ps1`, a prose validator scoring
distinct-sentence ratios), and the eight `census-round*-corrections.ps1` scripts.
`lib-disposition.ps1` drops from 628 to 112 lines and now owns exactly the three rules two
gates genuinely share. The reason is the human's standing direction that intent outranks
procedure: those gates policed the *shape of av-kit's own source and prose*, which the
implementing agent and the independent reviewer judge better than a regex, and they cost
more attention than the 200-line C# helper they were guarding. What replaces them is
product evidence — `PickerControllerTests`, `CaptureGeometryTests`, `RealDesktopCaptureTests`,
the installed-app packaging proof. Nothing that guards a **fact about the shipped artifact**
was removed.

Names, thresholds, and file sets live once in `named-sets.json`; the scripts are their sole
executable owners.

---

## User Review Required

> [!IMPORTANT]
> - **Spec revision of an approved phase:** MEU-39 is `✅ approved`; this project deletes part
>   of its shipped surface (overlay BrowserWindow + desktopCapturer freeze, 8 of its 30 ACs
>   retired) and revises the Phase 9 SSOT. Both decisions are already **Human-approved
>   2026-08-27 USER_EXPLICIT** (AskUserQuestion: "C# WinForms (.NET 8)" and "Delete it
>   entirely"), recorded in the spec-revision task.
> - **Installer size:** self-contained .NET 8 WinForms publish adds roughly 60–100 MB
>   unpacked to `extraResources` (WinForms does not support trimming). The installer already
>   carries a PyInstaller backend + ffmpeg; accepted as part of the toolchain decision.
> - **No fallback:** if the helper exe is missing or crashes, F2 logs `[Capture]` and fails
>   visibly — it does not fall back to a Chromium overlay (that path no longer exists).

---

## Proposed Changes

### Spec revision — `docs/build-plan/09-screenshot-capture.md` (+ 07, WP-1)

The Phase 9 SSOT changes from "overlay = BrowserWindow, grab = desktopCapturer" to
"region select + freeze + grab = native Windows helper; Electron orchestrates".

| Location (current) | Revision |
|---|---|
| §Electron OS surface, "Region overlay" row (line 168) | Owner becomes **Native region-picker helper** (`avkit-region-picker.exe`, C# WinForms .NET 8, spawned by Electron main). Opaque frozen-bitmap fullscreen topmost window on the display under the cursor; drag rect; Enter/release confirm; Esc cancel; minimum edge `PICKER_MIN_EDGE_PX`; PerMonitorV2 DPI |
| §Electron OS surface, "Write PNG" row + overlay-preload paragraph (line 183) | Helper writes the PNG to the **staging path Electron gives it** (inside the inbox directory, see §Result publication); Electron main runs the black/empty pixel guard, then atomically publishes it as `{inbox_dir}/{yyyy-MM-dd_HH-mm-ss}.png` and `POST /captures`. The overlay-preload paragraph is replaced by the **helper process contract** (below) |
| §Interactive MCP row (line 171) | "Show overlay" becomes "spawn the region-picker helper" (same poll/complete/cancel flow) |
| Preload allowlist table (line 177) | `capture-region` invoke stays (GUI button → main spawns helper); overlay-window channels (`overlay-submit`, `overlay-cancel`, `overlay-freeze-frame`) are deleted |
| §ShareX source map intro (line 544) and grab row (line 576) | "the overlay is a `BrowserWindow`, the grab is `desktopCapturer` / crop" becomes "the overlay+grab are `avkit-region-picker.exe` (WinForms + GDI `CopyFromScreen`), Electron registers the result". `RegionCaptureLightForm` mapping now points at the helper's `RegionForm` |
| §Sources table + Human-approved row (line 19) | Append: **Human-approved 2026-08-27 USER_EXPLICIT** — native C# WinForms sidecar replaces the Chromium overlay; Chromium overlay path deleted with no fallback. Research-backed: [electron#40515](https://github.com/electron/electron/issues/40515) |
| New subsection **§Native region picker (helper process)** | The full helper contract below, plus build/publish command and packaged path |
| `07-distribution.md` line 151 + §extraResources table (line 180) + checklist (line 300) | Add `region-picker/` to `extraResources`; note the `dotnet publish` build step |

**Helper process contract — THE normative definition (single-statement rule).**
The constants below are declared here once and in `named-sets.json`; every AC, task row, and
spec sentence refers to them **by name only** and never restates their values.

| Name | Value | Meaning |
|---|---|---|
| `PICKER_MIN_EDGE_PX` | `8` | Minimum width **and** height, in physical pixels, of a confirmable region (same lock as the deleted `OVERLAY_MIN_EDGE_PX`) |
| `PICKER_EXIT_CONFIRM` | `0` | User confirmed a region meeting `PICKER_MIN_EDGE_PX`; cropped PNG written to `--out` |
| `PICKER_EXIT_ERROR` | `1` | Error (bad argv, unwritable `--out` parent, GDI failure); reason on stderr; no file written |
| `PICKER_EXIT_CANCEL` | `2` | User cancelled (Esc, or released below `PICKER_MIN_EDGE_PX`); no file written |
| *any other code* | — | Not part of the contract; Electron **fails closed** and classifies it `blocked` (open-world input) |

| Item | Value |
|---|---|
| Binary | `avkit-region-picker.exe` — .NET 8 self-contained win-x64 WinForms publish from `native/region-picker/` |
| Invocation | `avkit-region-picker.exe --out <staging-path>` — Electron chooses the path; see §Result publication |
| Outcome | The `PICKER_EXIT_*` table above; the helper never names or timestamps the final file |
| Readiness | From the handler for the form's **first `Shown` event** — raised once, after the freeze-frame window is on screen and before any input is accepted — the helper writes `PICKER_READY_MARKER` on its own line to stdout and flushes. This is the only start-of-picker event Electron can observe, and without it `picker_startup_ms` is a guess rather than a measurement (round-7 finding R7-2). Round-8 finding R8-1 reconciled the wording: this row said "first painted frame" while the test, the gate and the task rows said `Shown`. WinForms has no first-paint event to bind to — `Paint` is raised again on every invalidation — so "first painted frame" describes a moment rather than naming an observable. `Shown` is raised exactly once, is what the production code registers, and is now the single event named everywhere. It is a one-way notification: the helper never reads stdin, so the `PICKER_EXIT_*` codes remain the whole *result* contract |
| Display | The display under the cursor at launch (`Screen.FromPoint(Cursor.Position)`), physical pixels — PerMonitorV2 via `app.manifest` |
| UX | Freeze-frame (opaque), dimmed shade outside the drag rect, crosshair cursor, drag → live rubber band, mouse-release or Enter confirms, Esc cancels. No annotation tools |
| Packaged path | `{process.resourcesPath}/region-picker/avkit-region-picker.exe`; dev path `native/region-picker/publish/avkit-region-picker.exe`; env override `AVKIT_REGION_PICKER_PATH` (dev/test only) |
| Concurrency | Electron main enforces a single in-flight picker; further `capture-region` triggers are ignored until exit |
| Internal structure | `RegionForm` (WinForms shell) delegates every input event to `PickerController`, which is the xunit-tested owner of drag state; `PickerController` calls `RectMath` for all geometry. Neither `RegionForm` nor `Program` may reimplement that math — proven by the controller and geometry unit tests (AC-40.16, AC-40.25), which drive the production types directly rather than inspecting their source text |

**§Capture pipeline (pixels and coordinates — normative).** Round-11 finding R11-1:
the plan named `CopyFromScreen` and PerMonitorV2 but never said what the bytes are, so two
implementers would ship two different pictures. Every rule below is in **physical device
pixels**; there are no logical/DIP coordinates anywhere in the helper.

1. **DPI awareness precedes everything.** `app.manifest` declares PerMonitorV2. No `Screen`
   query, no bitmap allocation and no window creation may happen before the process is
   DPI-aware, because a process that becomes aware late has already been handed virtualized
   coordinates. `Program.Main` therefore does argv parsing and nothing else before the
   capture step below.
2. **Target display.** `target = Screen.FromPoint(Cursor.Position)` at launch;
   `bounds = target.Bounds`. `bounds.X` and `bounds.Y` **may be negative** (a monitor left of
   or above the primary), neighbouring monitors may run at different scale factors, and the
   primary origin is the only `(0,0)` in the virtual screen. No code may assume the target's
   origin is `(0,0)` or that `bounds.Size` equals any other monitor's.
3. **Freeze before the window exists.** The order is fixed and is the whole reason the picker
   is native: allocate `new Bitmap(bounds.Width, bounds.Height, PixelFormat.Format32bppArgb)`,
   then `Graphics.FromImage(bmp).CopyFromScreen(bounds.X, bounds.Y, 0, 0, bounds.Size,
   CopyPixelOperation.SourceCopy | CopyPixelOperation.CaptureBlt)`, and only then construct and
   `Show` the `RegionForm` with that bitmap as its background. `CaptureBlt` is required, not
   optional: without it layered windows (Spotify's overlays, tooltips, most Electron menus)
   appear as holes in the frozen frame. Showing the window first and grabbing after is the
   defect this whole project exists to remove.
4. **Alpha is undefined after a GDI blit.** `CopyFromScreen` writes no meaningful alpha
   channel, so the captured bitmap's alpha is forced to `255` for every pixel before it is
   used or saved. A PNG whose alpha came out of a BitBlt is what produces "the screenshot is
   invisible in some viewers".
5. **Global → local mapping.** The form is positioned at `bounds`, so a mouse point in form
   client coordinates is `local = physical - bounds.Location`. The crop is
   `bitmap.Clone(localRect, PixelFormat.Format32bppArgb)` where `localRect` is the drag rect
   after `RectMath.ClampToBounds(rect, new Rectangle(Point.Empty, bounds.Size))`. Clamping is
   in **local** space: clamping in global space and cloning in local space is the subtraction
   bug that a negative-origin monitor turns into an exception or a wrong picture.
6. **The cursor is not drawn.** ShareX draws it optionally; av-kit's spec does not ask for it
   and a frozen frame with a stale pointer in it is worse than none.
7. **Output.** 32-bpp opaque PNG at `--out`. No resampling, no scaling, no colour conversion:
   the saved image's `Width`/`Height` equal the clamped selection's exactly, and pixel
   `(x, y)` of the PNG is the desktop pixel at `bounds.Location + localRect.Location + (x, y)`.
8. **Known limitation — HDR/scRGB.** `BitBlt` performs no colour management. On an HDR or
   wide-gamut display the SDR-referred bytes GDI returns can differ from what the eye saw.
   This is stated rather than solved: matching it needs Windows.Graphics.Capture plus a
   tone-map, which is Out of Scope here. Follow-up `CAPTURE-HDR-COLOR`.

**§Helper lifecycle (Electron side — normative).** Round-11 finding R11-2: the contract
described the happy path and left "the helper never exits" undefined, which is the failure
mode that costs a user the feature for the rest of the session. `capture-picker.ts` runs one
**total** state machine — every path ends in exactly one of `confirm`, `cancel`, or `blocked`,
exactly once.

| Situation | Terminal state | User-visible behaviour |
|---|---|---|
| exit `PICKER_EXIT_CONFIRM`, staged file present and non-empty | `confirm` | publish per §Result publication |
| exit `PICKER_EXIT_CONFIRM`, staged file missing or zero bytes | `blocked` | `[Capture]` log + error notification; the helper lied about its own success |
| exit `PICKER_EXIT_CANCEL` | `cancel` | **nothing** — no notification, no register, no error. Cancel is a normal outcome, not a failure |
| exit `PICKER_EXIT_ERROR` | `blocked` | `[Capture]` log carrying the captured stderr tail + error notification |
| any other exit code | `blocked` | fails closed (open-world input) |
| `close` with `code === null` and a signal | `blocked` | the process was killed; the signal is logged |
| `spawn` `error` event (missing exe, `EACCES`, `ENOENT`) | `blocked` | no throw escapes into the F2 handler |
| no `PICKER_READY_MARKER` within `PICKER_STARTUP_TIMEOUT_MS` | `blocked` | kill, then log "picker failed to start" |
| no exit within `PICKER_INTERACTION_TIMEOUT_MS` of readiness | `blocked` | kill, then log "picker timed out" |
| Electron quits while a picker is in flight (`app.will-quit`) | `blocked` | kill; no orphan process outlives the app |

Mechanics that make that table true:

- **Spawn**: `spawn(exePath, ['--out', stagingPath], { shell: false, windowsHide: true,
  stdio: ['ignore', 'pipe', 'pipe'] })`. `shell: false` is what makes a path containing spaces,
  `&`, a quote or non-ASCII characters safe — argv is passed as an array and never
  re-parsed by `cmd.exe`. The helper's stdin is never written to.
- **Both pipes are drained**, always, and each is bounded to `PICKER_LOG_MAX_BYTES` with the
  **tail** kept. An undrained stderr pipe is a deadlock waiting for a verbose GDI failure; an
  unbounded one is a memory leak on a helper that decides to loop.
- **Readiness** is the **first** line matching `^PICKER_READY_MARKER$` on stdout. Subsequent
  matches are ignored. This is where `picker_startup_ms` is measured and where the
  interaction timeout starts.
- **Kill is graceful then not**: `kill()`, and if the process has not emitted `close` within
  `PICKER_KILL_GRACE_MS`, `kill('SIGKILL')`.
- **One settle**: a single `settled` flag guards the terminal transition. `error`, `close`,
  `exit` and both timeouts all route through it, and the **first** one wins. To be precise
  about the two process events: `exit` is **observed and recorded** — its code and signal are
  stashed — but it does not itself classify the outcome. Classification waits for `close`, so
  the stderr tail is complete when the result is logged. Node guarantees `close` follows
  `exit` or a spawn `error`, so this is not a state the machine can be stranded in; and if
  `close` somehow never arrived, the interaction timeout is still armed and settles it.
- **The in-flight guard is released in `finally`**, together with listener removal, timer
  clearing, and unlinking the staged file on **every** non-confirm path. A guard leaked by a
  crashed helper disables F2 until the app restarts — which is exactly the class of bug this
  project is replacing, so it does not get to reappear on the Electron side.

**§Result publication (normative).** Electron passes `--out` as a *staging path inside the
inbox directory itself*: `{inbox_dir}/{PICKER_STAGING_PREFIX}{uuid}.tmp`. The staging name is
deliberately dot-prefixed and non-`.png` so that neither the inbox watcher nor the filmstrip's
PNG listing can surface it — `capture-inbox-watch.ts` exports the ignore decision as a pure
predicate so this is directly testable (AC-40.6). On `PICKER_EXIT_CONFIRM`, main runs the
black/empty pixel guard on the staged file and then publishes it. Round-11 finding R11-3
found three ways the old one-line `renameSync` publication lost a capture; all three are
closed here.

1. **Never clobber.** `registerFileName()` resolves to the second, so two captures inside one
   second produce the same name, and `fs.renameSync` would silently destroy the first PNG.
   Publication instead **claims a name**: for candidate `{base}.png`, `{base}_2.png`,
   `{base}_3.png`, … (starting at `PICKER_COLLISION_SUFFIX_START`), try
   `fs.linkSync(staged, candidate)` and treat `EEXIST` as "taken, try the next". `link` fails
   rather than overwrites, which is the property `rename` does not have. On success,
   `fs.unlinkSync(staged)`. The suffix form matches the SSOT's existing `_2`/`_3` convention,
   so nothing downstream has to learn a new shape.
2. **Ordered against the watcher — and independent of watcher timing.** The final path is
   recorded as Electron-owned **before** the link is attempted, and `shouldNotifyInboxChange()`
   suppresses that exact path until registration settles; exactly one `captures:inbox-changed`
   is emitted afterwards. Without this the watcher can fire on the new `.png` and race the
   register call, which is how the filmstrip ends up showing a capture the API has never heard
   of.

   Path suppression alone is **not** sufficient, and round-12 finding R12-1 is why. Node
   documents that an `fs.watch` callback may deliver `filename === null` (the platform did not
   report which file changed), and a delayed event for an Electron-owned path can arrive
   *after* suppression has been lifted. Neither can be matched against an owned path, so
   neither is suppressed. The watcher therefore does not decide whether to notify by matching
   a path at all: it recomputes the inbox's PNG set and emits `captures:inbox-changed` **only
   when that set differs from the last emitted set**. An Electron-owned path is inserted into
   the known set at publication time — before the link — so its later arrival, by any route and
   at any time, is never a difference and never a second event. `filename === null` degrades to
   a rescan that finds nothing new. This makes the notification idempotent rather than merely
   well-timed, which is the only shape that survives a watcher whose event content and delivery
   time are both unguaranteed.

   Three details make that comparison total rather than approximately total, and round 13
   asked for each by name.

   - **The baseline is seeded, not empty.** The watcher lists the inbox once at start and
     adopts that listing as the last-emitted set **without notifying**. Starting from an empty
     set would make every pre-existing capture a difference and fire a refresh at every app
     start.
   - **A reservation that never becomes a file is released — from its own set.** Reservations
     live in a **separate** set from the last-emitted set, and the decision is
     `current \ (lastEmitted ∪ reserved)`. The owned-path entry is inserted immediately before
     *each* `linkSync` candidate is attempted and removed from the **reservation** set the
     moment that candidate fails — `EEXIST` or any other throw — in the same `finally` that
     disposes of staging; only the candidate the link actually created stays reserved, released
     at settlement. Releasing a reservation **never removes a name from the last-emitted set**,
     and a completed pass advances the last-emitted set to the full current listing. Round-14
     finding: one set doing both jobs is not equivalent. Two captures inside the same second
     make the second one reserve `{base}.png`, hit `EEXIST`, and release — and if that release
     deleted the name outright, the *first* capture's already-announced PNG would look new on
     the next listing and fire a spurious refresh. Keeping the sets separate makes the release
     a no-op against history, which is the property that was actually wanted. Without the
     release itself, an abandoned `_2` reservation would swallow the notification for a
     genuinely new file that later takes that name.
   - **Rescans are serialized.** An event arriving while a rescan is in flight does not start a
     second one; it sets a run-once-more flag the in-flight pass honours on completion. The
     listing, the comparison, and the advance of the last-emitted set therefore all happen
     inside one pass, so two events cannot compare against a set a third has already moved.

   What keeps this proportionate: the watcher is an **accelerator, not the only route**. The
   filmstrip already re-queries `GET /captures` every 5 s, and every 1 s while an interactive
   request is pending (`ui/src/renderer/src/features/capture/useCaptureCatalog.ts:46-48`,
   `:75`), and that endpoint runs `scan_inbox()` on the way through
   (`packages/core/src/avkit_core/services/capture.py:178-182`). A missed notification costs a
   few seconds of latency; a spurious one costs one extra GET. Correctness never rides on the
   watcher. That same poll is also why a refresh landing mid-registration can enter an
   Electron-owned PNG as `source = scan` before the register call settles — which is not a
   watcher problem to solve but exactly what rule 4's `source` repair (AC-40.31) exists for.
3. **A failed registration never destroys pixels.** If `POST /captures` fails (backend down,
   4xx, timeout), the PNG **stays in the inbox** under its claimed name, the error is logged
   with that path, and the user is notified per §User-visible notification that the capture was
   saved but not registered. The recovery path is the existing `scan_inbox` — not a re-capture,
   and never an unlink.

   **§User-visible notification (normative).** Round-14 finding: "the user is notified" appears
   in this section three times and today has nothing behind it. The only `notify` callback in
   the capture path is `notifyInboxChanged(window)` (`ui/src/main/capture-register.ts:100-114`,
   `capture-overlay.ts:180-182`), which is a renderer IPC refresh — invisible to a user whose
   window is closed to tray, which is precisely the state a hotkey capture is taken from. Main
   therefore gains one `notifyUser({ title, body, path })` helper
   (`ui/src/main/notify-user.ts`) and every "the user is notified" in this plan means that
   helper:
   The surface is chosen by **`app.isPackaged`, not by `Notification.isSupported()`**. Round-15
   finding, and it is the difference between a notice and the appearance of one: a Windows
   toast is delivered against a *shortcut identity* — a Start Menu shortcut carrying an
   AppUserModelID and a ToastActivatorCLSID — and `isSupported()` reports OS capability, not
   whether that identity exists. An unpackaged dev run has no such shortcut, so calling
   `setAppUserModelId('com.avkit.app')` and taking the toast branch produces a call that
   succeeds and a notification Windows silently discards, with the tray fallback never reached.
   The two configurations are therefore branched explicitly:
   - **Packaged (`app.isPackaged === true`) — the shipped app.** `app.setAppUserModelId()` with
     the `appId` from `ui/electron-builder.yml:1`, which is the AUMID electron-builder writes
     into the NSIS Start Menu shortcut, so the identity matches. Then
     `new Notification({ title, body }).show()` when `Notification.isSupported()`, its `click`
     running `shell.showItemInFolder(path)` so the notice is **actionable** rather than merely
     informative; tray balloon if `isSupported()` is false.
   - **Unpackaged (dev, and the Playwright run).** The AUMID is **not** set to the packaged
     `appId` — claiming an identity no shortcut backs is what makes the toast vanish — and the
     toast branch is not taken at all. The notice goes to the tray balloon
     (`tray.displayBalloon`), which needs no shortcut identity, and to the log. If the tray is
     not yet constructed when a notice fires, the helper falls back to `dialog.showMessageBox`
     with no parent window.
   - `appendStdoutLog` **always**, on every branch. This matters more than it looks: Windows can
     drop a notification for reasons no API reports (Focus Assist, notification centre policy,
     and on Win10+ a tray balloon may itself be routed through the notification centre), so the
     log line is the one receipt the plan can actually promise. The plan claims a *visible*
     notice only for the packaged app, which is the configuration a user has.
   The helper is injected (a module-level seam) so vitest counts calls and asserts the branch
   without spawning real toasts, and delivery is suppressed under `AVKIT_E2E` so the Playwright
   run does not fire OS notifications while still recording the call.
4. **Idempotent register repairs `source`.** `packages/core/src/avkit_core/services/capture.py`
   currently returns an existing row unchanged when a path is re-registered, so a capture first
   seen by the inbox scanner keeps `source = scan` forever even when the picker registers it a
   moment later. Registration now repairs `source` on the idempotent path, with its own
   regression test (AC-40.31). This is the one Python change in the project.
5. **A confirm never reports cancel — including to the MCP requester.** The publication step
   has no path that swallows a confirmed capture silently: every branch above either produces
   an inbox file or logs and notifies.

   Round-12 finding R12-2 found the one place this rule was still violated, and it is a
   *caller*, not the publication step. `ui/src/main/index.ts` wraps the whole interactive
   request in a single `try`, and its `catch` calls `cancelCaptureRequest(row.id)`. Once
   publication has succeeded, `completeCaptureRequest` can still fail — backend down, timeout,
   4xx — and control lands in that `catch`. The user then confirmed a region, the PNG is on
   disk in the inbox, and the request the agent is waiting on reports `Canceled`. That is a lie
   about what happened, and it is exactly the failure this section exists to eliminate.

   The call site is therefore **in scope for this MEU** (superseding the "call sites unchanged
   in shape" note that previously stood in Files Modified). The `try` is split at the
   publication boundary: the pre-publication phase (`listPendingRequests`,
   `captureRegionFromGui`) may cancel on failure, because nothing has been produced yet. Once
   `dest !== null` the request has pixels behind it and **no failure path may cancel it**: a
   failing `completeCaptureRequest` is logged with the inbox path and the request is
   **retried**, never flipped to `Canceled`. Cancel remains reachable only for a genuine
   `PICKER_EXIT_CANCEL` (`dest === null`).

   Round-13 finding: "leave it pending" is not a recovery path, and the code says so.
   `startInteractivePoll` (`ui/src/main/capture-register.ts:119-133`) re-reads the first Pending
   row every `POLL_REQUEST_MS` and hands it to the same handler, so a request that stays
   Pending **reopens the picker on the next tick**. The user confirms a region, keeps the PNG,
   and is then asked to select a region again, and again, until `expire_stale_requests()` flips
   the row to `Expired` after `REQUEST_TTL_S` = 120 s
   (`packages/core/src/avkit_core/services/capture.py:271-292`). `Expired` is terminal
   (`CAPTURE_REQUEST_TRANSITIONS[Expired]` is the empty set,
   `packages/core/src/avkit_core/domain/capture.py:41-43`), so the agent that asked for the
   capture never receives it even though the pixels are sitting in the inbox. Worse for the
   user: `request_interactive` refuses a second request while one is Pending
   (`capture.py:221-235`), so the agent cannot even retry until the TTL burns down. The plan
   therefore owns the recovery rather than gesturing at one.

   - **A completion journal, consulted before the picker.** Main keeps a session-scoped
     `Map<requestId, { path, attempts, nextAttemptAt }>`, written the moment publication
     succeeds and before `completeCaptureRequest` is first attempted. The poll handler consults
     it **first**: if the Pending row it was handed is already journalled, it retries
     `completeCaptureRequest(id, entry.path)` and **does not invoke the picker**. This is what
     ends the re-prompt loop, and it is rule 5 restated: a user who confirmed once is asked
     once.
   - **The retry cannot duplicate a shot, and a rejected replay is a *signal*.** Precisely
     (round-15 note — "idempotent" was too loose): `complete_request` resolves the shot by path
     through `_upsert_shot` (`capture.py:237-260`, `:410-430`), so replaying the same
     `{requestId, path}` can never create a second shot. But the *request* transition is not
     idempotent — completing an already-`Completed` row raises `ConflictError`
     (`capture.py:245-252`, and `CAPTURE_REQUEST_TRANSITIONS[Completed]` is empty). The status
     read below is what normally prevents that replay. A 409 that does arrive is a **trigger to
     reconcile, never a verdict** — round-16 finding R16-1, and the round-15 rule it replaces
     ("409 means terminal-success, drop silently") was wrong in the way that costs a user their
     capture. The backend raises the same 409 for *every* non-Pending state, and
     `complete_request` calls `expire_stale_requests()` **before** it validates the transition
     (`capture.py:237-252`), so a user who confirms near the 120 s TTL can have that very call
     expire the row and answer 409. Under the round-15 rule Electron would then discard the
     journal silently while the calling agent sees `Expired` — a false success, and no notice to
     the user whose PNG is sitting in the inbox. A concurrent cancel does the same. So on 409
     the journal re-reads the row's **actual** status through the discriminated listing below
     and lets that decide: `Completed` ⇒ drop silently; `Cancelled`, `Expired`, or absent ⇒ drop
     **with** the terminal notice; `unavailable` ⇒ keep the entry until the status is knowable.
     What the 409 does buy is that the entry is never retried into a loop against a row that has
     already left Pending. No new backend endpoint, no schema change.
   - **The poll must be able to tell "gone" from "unreachable".** Round-14 finding, and the
     journal cannot work without it: `listPendingRequests()` today returns `[]` for a backend
     that is not ready, a non-OK status, a thrown fetch, and a genuinely empty pending list
     alike (`ui/src/main/capture-register.ts:83-97`). Treating `[]` as terminal would drop the
     journal during exactly the backend restart the retry exists for; ignoring `[]` would make
     expiry unreachable. The poll is therefore re-specified to preserve both facts, with no
     backend change — `GET /captures/requests` already takes an **optional** status filter and
     returns every row with its status (`packages/api/src/avkit_api/routes/captures.py:164-173`,
     `capture.py:283-292`):
     - it returns a discriminated result, `{ kind: 'ok', rows } | { kind: 'unavailable', reason }`.
       Backend-not-ready, non-OK, thrown, or unparseable ⇒ `unavailable`. The picker's trigger is
       the first `Pending` row in `rows`, so its behavior is unchanged.
     - it keeps the existing `?status=pending` filter for the **ordinary** tick, and drops the
       filter **only while the journal is non-empty** — a transient state measured in seconds.
       Round-15 note: the unfiltered listing walks the whole historical request table
       (`packages/infrastructure/src/avkit_infra/database/repositories.py:474-478`), which is
       fine for the rare recovery case and wasteful twice a second forever. The discriminated
       result applies to both shapes; only the filter changes.
     - `unavailable` is **never terminal**: the journal entry stays and the backoff continues.
       This is the backend-restart case, and it is the whole reason the distinction matters.
     - on `ok`, the journalled id's **actual status** decides: `Pending` ⇒ retry when its
       backoff is due; `Completed` ⇒ drop the entry silently (an earlier call landed and only
       its response was lost); `Cancelled` or `Expired` ⇒ terminal; absent from a successful
       listing ⇒ terminal, because a listing that succeeded and does not contain the row means
       it is genuinely gone.
   - **Bounded, then terminal and visible.** Retries back off (1 s, 2 s, 4 s, 8 s, capped at
     15 s) instead of firing on every 500 ms tick, and stop on any terminal status above. On a
     terminal status that is not `Completed`, the entry is dropped and the user gets one
     **OS-level** notice naming the inbox path, per §User-visible notification — not a renderer
     refresh, which a user who is not looking at the app never sees (round-14 finding). The
     capture itself is never at risk: it is already in the inbox and `scan_inbox` puts it in the
     filmstrip regardless (rule 3).
   - **The honest bound.** The journal is in memory, so a main-process restart inside that
     120 s window loses the retry. The PNG still stands and still reaches the filmstrip; only
     the request expires. Persisting the journal, or letting the backend associate an already
     expired request with a shot after the fact, is deliberately out of scope — it would need a
     schema change in a project whose one Python change is AC-40.31.

   Proven by AC-40.33.

On any non-confirm outcome, or when the pixel guard blocks, the staged file is unlinked and no
inbox file or register call is produced.

**§Packaging and output cleanliness (normative).** Round-11 finding R11-4: deleting the
overlay from `ui/src` does not delete it from the installer. `electron-builder` packages
`ui/out` as it finds it, and `ui/out/preload/overlay.js` and `ui/out/renderer/overlay.html`
exist in this repo **today** (proof: `C:/Temp/av-kit/r11-stale-out-proof.txt`), left by the
last Chromium-overlay build.

- `dist:prep` = delete `DIST_CLEAN_DIRS` (`ui/out`, `native/region-picker/publish`) →
  `electron-vite build` → `dotnet publish native/region-picker -c Release -r win-x64
  --self-contained true -p:PublishSingleFile=false -o native/region-picker/publish`.
  `dist` = `npm run dist:prep && electron-builder --win nsis --x64`. The clean is a required
  segment **in order** (oracles P5/P6), so it cannot be dropped as "slow" or moved after the
  builds it exists to precede.
- `OVERLAY_DELETION` scans `OVERLAY_SCAN_ROOTS` — `ui/src` **and** `ui/out` — for the
  forbidden token, and additionally rejects any `overlay*` file by name, because a compiled
  bundle need not contain `desktopCapturer` verbatim.
- **Runtime shape**: self-contained win-x64, **not** single-file, **not** trimmed, **not** AOT
  (WinForms supports neither trimming nor AOT). Roughly 70–100 MB unpacked under
  `extraResources`. **x64 only**; an arm64 build is named Out of Scope rather than left silent.
- **SDK pinning**: `global.json` at the repo root pins the `DOTNET_SDK_BAND` (`8.0.4xx`) band
  with `rollForward: latestFeature`, so the sidecar is not built against whatever SDK a
  machine happens to have. The toolchain receipt records 8.0.424 present.
- **Path resolution is proven from an installed app**, not from the dev tree
  (`assert-packaging-clean.ps1 -Installed`, AC-40.32): silent-install the NSIS output to a temp
  prefix, assert `INSTALLED_PICKER_REL`, run the helper there and require `PICKER_EXIT_ERROR`
  for bogus argv — which also proves the self-contained publish brought its own runtime — and
  then run the installed **Electron** app through its own resolver (see R12-3 below), which is
  the part a user actually depends on.
- **The helper is unsigned**, like the rest of av-kit. First-run SmartScreen and AV behaviour
  for a freshly published unsigned .NET executable is documented in `07-distribution.md`;
  follow-up `DIST-CODE-SIGNING`. Naming it is the point — an unsigned sidecar that silently
  fails to start on a locked-down machine is indistinguishable from a broken picker.


Round-12 finding R12-3 corrected three things about how that installed proof is obtained,
because as written it could not have run at all:

- **The gate must look where electron-builder actually writes.** `ui/electron-builder.yml` sets
  `directories.output: dist`, so the installer lands in `ui/dist`. `NSIS_OUTPUT_DIR` said
  `ui/release`, a directory that does not exist on this tree — row 9a would have failed with
  "missing NSIS_OUTPUT_DIR" on every run, and had a stale `ui/release` ever been created it
  would have inspected the wrong installer. `NSIS_OUTPUT_DIR` is now `ui/dist`, and AC-40.10
  asserts it equals `directories.output` in `ui/electron-builder.yml` so the two cannot drift
  apart again.
- **The installer must be the one this run produced.** Picking the newest `.exe` in a directory
  proves nothing about the build that just finished. Row 9a arms the run first
  (`arm-run.ps1 -Name packaging-installed`) and the gate requires the installer's
  `LastWriteTime` to be **newer than the arm stamp** — the same staleness defence the E2E gate
  already carries (round-5 finding R4-3-R5).
- **Resolution must be proven through the shipped code path, not around it.** Launching the
  installed helper directly proves the binary runs and brought its own runtime; it does **not**
  prove that the installed *Electron main process* finds it, which is what
  `{process.resourcesPath}` makes fragile and what a user actually depends on. The installed
  app therefore answers a diagnostic flag, `PICKER_PATH_PROBE_FLAG` (`--avkit-picker-path`):
  main runs its real `resolvePickerExePath()`, prints `PICKER_PATH=<resolved>` plus whether
  that path exists, and quits without creating a window. The gate runs the **installed**
  `av-kit.exe` with that flag and requires the resolved path to exist and to sit under the
  install prefix. That is the production resolver running under the production layout. A full
  F2 GUI drive inside the installer sandbox stays a follow-up
  (`DIST-INSTALLER-SANDBOX`); the human live smoke (task row 7b) covers the GUI end on the dev
  tree.
### MEU-40 `native-region-picker` — helper + Electron integration (WP-3, WP-4)

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| Helper argv (`--out`) | `Program.cs` argv parser | exactly one `--out` with an absolute path whose parent directory exists; anything else → exit 1 + stderr | unknown flags → exit 1 (fail closed) |
| Helper → Electron readiness | a single `PICKER_READY_MARKER` line on stdout | Electron matches it **anchored** and acts on the FIRST occurrence only; any other stdout text is ignored, never parsed, and never surfaced to the renderer | n/a |
| Helper → Electron result | exit-code contract above + PNG file | `0`/`2`/`1`-or-other mapped exhaustively in `capture-picker.ts`; **unrecognized exit codes fail closed as `blocked`** | n/a |
| Returned PNG | `inspectNativeImagePixels` (existing `capture-pixels.ts`) | black/empty bitmap → blocked; no inbox write; no register | n/a |
| REST / MCP / renderer IPC | unchanged | `POST /captures` register body unchanged (`capture-register.ts` Zod `.strict()` untouched); renderer preload allowlist unchanged except overlay-channel removal | unchanged |

The old renderer-crossing boundary (overlay rect over IPC, `parseOverlayRect` +
`overlayRectBridgeSchema`) is **deleted with its surface** — rect math never leaves the
helper process; the trust boundary becomes the exit code + PNG file, validated as above.

#### Acceptance Criteria

> Control-binding note: each integration AC names its observable, its production call chain,
> and a negative oracle. The exit-code classification in AC-40.5 is over open-world input
> (a process exit code) and therefore **fails closed** on unrecognized values.
> Constants (`PICKER_MIN_EDGE_PX`, `PICKER_EXIT_*`) are referenced by name only — their
> values live once in §Helper process contract and `named-sets.json`.

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-40.1 | unit | `RectMath.Normalize(p1, p2)` returns the axis-aligned rect for any two drag points (either drag direction); observable: xunit assertions | Spec (drag rect) | inverted/equal points → non-negative width/height; zero-area rect flagged invalid |
| AC-40.2 | unit | `RectMath.MeetsMinEdge(rect)` true iff both edges meet `PICKER_MIN_EDGE_PX` | Spec (minimum region) | one-below-minimum in each axis → false ⇒ cancel path; exactly-minimum square → true |
| AC-40.3 | unit | `RectMath.ClampToBounds(rect, bounds)` never exceeds the frozen bitmap | Spec (display under cursor) | drag past screen edge → clamped, not out-of-range crop (GDI crop of an out-of-bounds rect would throw) |
| AC-40.4 | unit | Helper static contract: `app.manifest` declares PerMonitorV2; csproj is `net8.0-windows` WinForms with manifest wired; the `PICKER_EXIT_*` constants are asserted from the test project against the values in §Helper process contract | Research-backed (WinForms DPI) + Spec contract | missing/duplicate `--out`, or an `--out` whose parent does not exist → `PICKER_EXIT_ERROR`, no file written |
| AC-40.16 | integration | **Native control binding.** `PickerController` is the production owner of drag state and is driven end-to-end in xunit: begin/update/end drag → `Confirmed(rect)`; below-minimum release → `Cancelled`; Esc → `Cancelled`; Enter after a valid drag → `Confirmed`; drag past bounds → `Confirmed` with a **clamped** rect. `Program.Run(args, IPickerDialog)` — the real production entrypoint — is then driven with a fake dialog to prove each outcome maps to its `PICKER_EXIT_*` code. Chain: `RegionForm` event handler → `PickerController` → `RectMath`; `Program.Run` → dialog outcome → process exit code | Spec (helper contract) | a controller that ignores `MeetsMinEdge` returns `Confirmed` for a below-minimum drag ⇒ test fails; a `Program.Run` that maps cancel to `PICKER_EXIT_CONFIRM` ⇒ test fails |
| AC-40.5 | integration | `capture-picker.ts` (new): resolves packaged/dev/env-override exe path, spawns with `['--out', stagingPath]`, maps `PICKER_EXIT_CONFIRM`→`{kind:'confirm', path}`, `PICKER_EXIT_CANCEL`→`cancel`, **any other code**→`blocked` + `[Capture]` log; missing exe → `blocked` + log, no throw. Chain: F2 / `capture-region` IPC / interactive poll → `captureRegionFromGui` → `runRegionPicker` → spawn. Observable: mocked-spawn vitest assertions + log lines | Human-approved (sidecar) | `PICKER_EXIT_ERROR` and an off-contract code (e.g. 137) both → `blocked`; **no** `POST /captures` fetch occurs |
| AC-40.6 | integration | **Lossless publication.** On confirm, `captureRegionFromGui` runs `inspectNativeImagePixels` on the staged file; blocked ⇒ log, staged file unlinked, **no inbox `.png`, no register**; pass ⇒ publish per §Result publication. Publication **claims** a name rather than overwriting one: `fs.linkSync(staged, candidate)` over `{base}.png`, `{base}_2.png`, … treating `EEXIST` as taken, then `fs.unlinkSync(staged)`. `shouldNotifyInboxChange()` (exported from `capture-inbox-watch.ts` as a pure predicate) returns false for the staging name **and** for the claimed final path until registration settles, after which exactly one `captures:inbox-changed` is emitted. If `POST /captures` fails, the PNG stays put and the user is told it was saved but not registered. Observable: fs call spies + fetch calls in vitest | Spec (Write PNG row) + Research-backed (`link` fails on an existing name; `rename` silently replaces it) | all-black PNG fixture ⇒ inbox holds no `.png` and fetch not called; **two captures resolving to the same `registerFileName()` second ⇒ two files, `_2` suffixed, neither overwritten** (a `renameSync` implementation fails this); a register rejection ⇒ the file still exists and no unlink occurred; a spy asserting `writeFile`/`copyFile`/`renameSync` targeted the final path ⇒ fail; `shouldNotifyInboxChange(stagingName)` returning true ⇒ fail |
| AC-40.7 | integration | Single in-flight picker: while a spawn is unresolved, further `captureRegionFromGui` calls return null without spawning. Observable: spawn call count | Spec (helper contract, concurrency) | two rapid F2 fires → exactly one spawn |
| AC-40.8 | integration | Interactive MCP path uses the picker: pending request → picker confirm → `POST /captures/requests/{id}/complete` with path; `PICKER_EXIT_CANCEL` → `…/cancel`. Chain: `startInteractivePoll` → `index.ts` handler → `captureRegionFromGui`. Observable: mocked fetch endpoints | Spec (Interactive MCP row) | picker `blocked` → no `complete` is sent naming a nonexistent file (cancel only) |
| AC-40.9 | unit | Chromium overlay fully deleted **from source and from build output**, proven by `OVERLAY_DELETION` (`assert-overlay-deleted.ps1`): zero occurrences of `OVERLAY_FORBIDDEN_TOKEN` under every `OVERLAY_SCAN_ROOTS` entry (`ui/src` **and** `ui/out`), zero files matching `OVERLAY_FORBIDDEN_NAME_PATTERN` (`overlay*`) under those roots, none of `OVERLAY_DELETED_FILES` on disk, no overlay entries in `electron.vite.config.ts` | Human-approved (delete entirely) + round-11 finding R11-4 | token count ≠ 0 in either root, a compiled `out/preload/overlay.js` that no longer contains the token but still carries the name, any listed path present, or any vite overlay input ⇒ fail (script `-SelfTest` O1–O4 proves detection works, including the name-only case) |
| AC-40.10 | integration | **The production `dist` chain builds the picker, cleans before it, and publishes a runnable runtime**, proven by `PACKAGING_CLEAN_PATH` (`assert-packaging-clean.ps1`): `ui/package.json` gains `clean:out`, `build:picker` and `dist:prep`; splitting each script body on `&&` must yield the **exact** segments `npm run dist:prep` (in `dist`) and every `PICKER_PREP_REQUIRED_SEGMENTS` entry **in declared order** (in `dist:prep`) — a segment that merely mentions the name (`echo build:picker`) does not count, and a clean that runs *after* the builds is rejected as deleting what it just built; `build:picker`'s body must carry every `PICKER_PUBLISH_REQUIRED_SEGMENTS` fragment (`-r win-x64`, `--self-contained true`, …), so a framework-dependent publish that dies on a machine without the .NET Desktop Runtime cannot ship; `GLOBAL_JSON_FILE` pins the `DOTNET_SDK_BAND` band; `electron-builder.yml` `extraResources` gains `from: ../native/region-picker/publish, to: region-picker`; and `NSIS_OUTPUT_DIR` must equal `directories.output` in `ui/electron-builder.yml` resolved against `ui/` (round-12 finding R12-3 — they disagreed, `ui/release` vs `dist`, so the installed proof could never have run). Observable: exact-segment asserts + a **clean-path rebuild that runs the production `npm --prefix ui run dist:prep` segment verbatim** from an emptied publish dir | Local Canon (07 extraResources pattern) + round-11 finding R11-4 | `dist = "echo dist:prep && electron-builder …"` ⇒ fail (P1); a `dist:prep` that does not invoke `build:picker` ⇒ fail (P2/P4); no clean ⇒ fail (P5); clean after build ⇒ fail (P6); a publish without `--self-contained true` ⇒ fail (P7); emptied publish dir not reproduced by the production segment ⇒ fail; `NSIS_OUTPUT_DIR` pointing anywhere other than electron-builder's own output directory ⇒ fail (P8), which is the defect R12-3 found |
| AC-40.11 | integration | **Conditional** `AVKIT_E2E=1` short-circuit: `captureRegionFromGui` notifies and returns null **without spawning** the helper only while `AVKIT_REGION_PICKER_PATH` is unset (keeps the nine pre-existing Wave-9 specs hermetic). When a test supplies the override, the real spawn/publish/register chain runs — that is what AC-40.18 exercises. `assert-e2e-wired.ps1` proves every `AVKIT_E2E` line in `capture-picker.ts` also names the override | Local Canon (MEU-39 E2E guard) + Local Canon (AGENTS.md real-Electron rule) | E2E env set, override unset → spawn call count 0; **an unconditional `if (process.env.AVKIT_E2E === '1')` short-circuit ⇒ gate fails** (it would make the real chain permanently untestable) |
| AC-40.18 | e2e | **Real-Electron capture path, executed.** `ui/tests/e2e/capture-picker.test.ts` launches the packaged main process under Playwright with `AVKIT_REGION_PICKER_PATH` pointed at the deterministic sidecar stub and asserts the full production chain across the three declared `E2E_REQUIRED_CASES`: **confirm** → stub writes the staged PNG → pixel guard passes → the `linkSync` name-claim publishes `{inbox}/{registerFileName()}` (or its `_2`/`_3` collision form) → `POST /captures` register → `captures:inbox-changed` refresh reaches the renderer; **cancel** → inbox unchanged, no register; **all-black** (`AVKIT_STUB_PIXEL=black`) → staged file unlinked, no `.png`, no register. The run produces its own machine-readable receipt: `npm --prefix ui run test:e2e:capture` emits a Playwright JSON report to `E2E_EXECUTED_RECEIPT` via `PLAYWRIGHT_JSON_OUTPUT_NAME` (the console stream still redirects to `C:/Temp/av-kit/` per P0, so the JSON stays unpolluted), and `assert-e2e-wired.ps1 -Mode Executed` requires `stats.unexpected`/`skipped`/`flaky` all `0`, `stats.expected >=` the case count, and every required case present, `ok`, all statuses `expected`, and reported from the capture spec's own file (round-4 finding R4-3 — "the spec exists" is not "the spec ran"). The report must additionally be **fresh**: task row 7a and verification §9a1 call `arm-run.ps1 -Name e2e-capture`, which deletes the report and writes `RUN_STAMPS['e2e-capture'].stamp` before the run, and the gate rejects a report older than that stamp — a green report left behind by an earlier run is not this run's evidence (round-5 finding R4-3-R5) | Local Canon (AGENTS.md §Testing: runtime GUI behavior is verified by Playwright against real Electron, never by eyeballing) | a report in which the capture spec is absent, skipped, failed, flaky, short, or attributed to another spec file ⇒ gate fails (self-tests X1–X6); if Electron cannot launch in the sandbox the row is `[B]` with receipt + follow-up — the spec is still written, wired, and gated |
| AC-40.19 | integration | **The E2E is wired before it is judged.** `E2E_WIRED` (`assert-e2e-wired.ps1 -Mode Wired`) proves the spec exists under the configured `testDir`, matches `testMatch`, carries no `.skip(`/`.only(`/`.fixme(` (G36), declares each `E2E_REQUIRED_CASES` title as a real `test("…")` in **comment-stripped** source, names `AVKIT_REGION_PICKER_PATH` outside comments, that the `AVKIT_E2E` short-circuit is conditional on that override, and that `test:e2e:capture` carries every `E2E_CAPTURE_REQUIRED_SEGMENTS` segment, `build:picker-stub` runs `dotnet publish`, and `E2E_STUB_PROJECT_FILE` exists. `-Mode Executed` (after the run) checks the JSON report per AC-40.18. Round-11 trim: the manual live smoke is no longer wrapped in a launcher, bound to a minted run-nonce, and parsed by a gate. It is a **human-recorded step** (task row 9) whose evidence the independent reviewer judges — a person confirming a picker feels right is the one thing a PowerShell parser cannot check, and three gates plus a nonce protocol were spent pretending otherwise | Local Canon (G36; AGENTS.md `[B]` evidence rule) | a `.skip(`-ed spec, a spec whose required cases exist only in comments, an `echo`-fronted or `&&`-split capture script, or a segment that merely starts with the head's characters ⇒ fail (self-tests S1–S7 incl. S6e, G1–G3, X1–X7b, Y0–Y4) |
| AC-40.12 | integration | Spec revision landed: `Select-String` over `docs/build-plan/09-screenshot-capture.md` finds 0 normative `desktopCapturer` matches and ≥1 `avkit-region-picker` match; `07-distribution.md` extraResources lists `region-picker`; Human-approved 2026-08-27 recorded | Human-approved | leftover normative `BrowserWindow` overlay text in §Electron OS surface ⇒ fail |
| AC-40.13 | integration | MEU-40 registered: `meu-status.yaml` row (phase 9, matrix 9.7, depends MEU-39) + `tools/meu_status.py render --check` clean | Local Canon (registry SSOT) | `render --check` drift ⇒ fail |
| AC-40.14 | unit | Renderer surface unchanged: preload `captureRegion` invoke + `captures:inbox-changed` retained; `CapturePage`/filmstrip/annotate untouched; vite preload inputs contain only `index` | Spec (GUI notes) | overlay entry present in vite preload inputs ⇒ fail |
| AC-40.21 | integration | **The hub states the shipped architecture.** `BUILD_PLAN_HUB` (`assert-build-plan-hub.ps1`) fails if any line of `HUB_FILE` still states the deleted Chromium design — `HUB_FORBIDDEN_TOKENS` (`desktopCapturer`, `overlay`) matched case-insensitively — unless that same line **both** names a `HUB_REQUIRED_TOKENS` term **and** carries a `HUB_RETIREMENT_MARKERS` word (`replaced`, `retired`, `removed`, …), and fails if the hub never names the replacement at all. Round-6 finding R6-3 added the half that makes the gate a *specification* rather than a filter: each of the four `HUB_REQUIRED_LINES` — the exact replacement text for hub lines 32, 93, 111 and 143 — must appear **verbatim**, so appending " region picker" to a stale line (oracle H6) or dropping a retirement framing (H7) no longer passes. Round-5 finding R5-1: the previous treatment was a report-only match count that could close while changing nothing, which is exactly the AGENTS.md §Pre-Handoff Self-Review item-4 failure | Local Canon (AGENTS.md §Pre-Handoff Self-Review 4: "if you changed architecture, `rg` canonical docs for the old pattern") | today's hub — four bare `overlay` lines (32, 93, 111, 143), zero `region picker` — **fails** this predicate, and its exact line texts are pinned as self-test oracle H0 so the non-vacuity proof survives the fix; `Overlay` capitalised ⇒ fail; a hub scrubbed of the old words but never naming the picker ⇒ fail; a line reading "the region picker replaces the removed Chromium overlay" ⇒ pass |
| AC-40.24 | unit | **The readiness signal exists and is emitted after the frozen frame is on screen.** The helper declares `PICKER_READY_MARKER` beside the `PICKER_EXIT_*` codes (asserted from the test project as in AC-40.4), and it is written — flushed — from the handler for the form's first `Shown` event, never from `Main`'s prologue: a marker printed before the freeze frame is visible would make Electron's `picker_startup_ms` measure process creation rather than readiness. Round-11: the Roslyn syntax-and-control-flow gate that used to police this is deleted; the property is proven instead by `PickerControllerTests` driving `Program.Run` with a fake `IPickerDialog` whose `Show()` records call order, and asserting the marker write happens **after** the dialog reports the frame is displayed. `Shown` remains coarse readiness — it fires when the window is shown, not when the compositor has presented a frame — which is accepted rather than papered over: the measurement is a lower bound | Spec (helper contract §Readiness — the observable Electron times against) | a marker written before `Show()` ⇒ the recorded order inverts and the test fails; a missing flush on a redirected stdout ⇒ the line can be lost in the pipe, so the constants test also asserts the flush call is present; a typo'd marker ⇒ diverges from `named-sets.json`, which the constants test reads |
| AC-40.15 | integration | Full UI gates green after deletion: `vitest run` all pass (retired overlay tests removed, new picker tests in), `tsc --noEmit` clean, `eslint --max-warnings 0` clean; xunit `dotnet test` green | Local Canon (AGENTS.md §Validation Pipeline P1 gates; registered UI receipts in `.agent/docs/commands.md`) | any gate nonzero ⇒ not done |
| AC-40.25 | unit | **Global→local coordinate mapping survives a hostile monitor layout.** `CaptureGeometryTests` drives `RectMath` with synthetic `Rectangle` bounds standing in for real displays: a **negative-origin** monitor (`bounds = (-1920, -300, 1920, 1080)`, a screen left of and above the primary), a monitor whose origin is positive but non-zero, and a mixed-DPI pair whose sizes differ. For each: a drag expressed in global coordinates maps to `local = global - bounds.Location`, `ClampToBounds` is applied in **local** space against `new Rectangle(Point.Empty, bounds.Size)`, and the resulting rect is inside the bitmap for every drag including ones that leave the monitor on each of the four edges | Research-backed (Win32 virtual-screen coordinates are signed; `Screen.Bounds` of a non-primary display may have a negative origin) + round-11 finding R11-1 | clamping in global space then cloning in local space ⇒ an out-of-range rect on the negative-origin monitor ⇒ test fails (and would throw in GDI at runtime); assuming `bounds.Location == Point.Empty` ⇒ every non-primary case fails |
| AC-40.26 | unit | **The frame is captured before the window exists, and the crop is exact.** The helper takes its pixels through an `ICaptureSource` seam (`ScreenCaptureSource.cs` is the GDI implementation; `Program.Run` receives the interface). A fake source returning a known synthetic pattern is driven through the real `Program.Run` + `PickerController` path and asserts: (a) `Capture(bounds)` is called **before** `IPickerDialog.Show()` — recorded call order, which is the whole ordering defect the Chromium overlay had; (b) the produced bitmap is `Format32bppArgb` with **every** alpha byte `255`; (c) the saved PNG's `Width`/`Height` equal the clamped selection exactly, with no resampling; (d) pixel `(x, y)` of the output equals pattern pixel `localRect.Location + (x, y)` for the four corners and the centre | Spec (§Capture pipeline) + round-11 finding R11-1 | a `Program.Run` that shows the dialog first ⇒ the order assertion fails; a capture path that leaves alpha at 0 ⇒ (b) fails; an off-by-one crop origin ⇒ (d) fails at the corners |
| AC-40.27 | integration | **Real-desktop proof.** `native/region-picker-tests/RealDesktopCaptureTests.cs`, trait `Category=RealDesktop`, runs the **real** `ScreenCaptureSource` against the actual desktop: it paints a known fixture form (solid colour, known screen rect), captures the containing display, and asserts the captured pixels at that rect are the fixture's colour and that a sub-rect crop lands exactly where the geometry says. A second case repeats it on a **secondary** display with a non-zero (ideally negative) origin, and calls `Skip` when `Screen.AllScreens.Length < 2`. Run under its own receipt (verification §1b) | Research-backed (a fake `ICaptureSource` can prove the plumbing but never that `CopyFromScreen` + `CaptureBlt` returns the right pixels on a real DWM-composited desktop) + round-11 finding R11-1 | **the primary-display case is not `[B]`-able** — the agent machine has a desktop, so a failure there is a real failure; the multi-monitor case may take an evidence-gated `[B]` (`missing-dependency`, follow-up `CAPTURE-MULTIMON-HW`) only with a receipt showing the skip reason, since single-monitor hardware is a genuine external constraint |
| AC-40.28 | integration | **Helper lifecycle totality.** Every row of the §Helper lifecycle table is a vitest case over a fake child process: each of the four declared exit codes, an off-contract code, `close` with `code === null` plus a signal, a `spawn` `error` event, a confirm whose staged file is missing or zero bytes, no readiness within `PICKER_STARTUP_TIMEOUT_MS`, no exit within `PICKER_INTERACTION_TIMEOUT_MS`, and `app.will-quit` mid-flight. Each asserts exactly one terminal state, exactly once, that the in-flight guard is released, that timers and listeners are cleared, and that the staged file is unlinked on every non-confirm path. Cancel asserts **no** error notification and **no** register | Spec (§Helper lifecycle) + round-11 finding R11-2 | a hung helper with no timeout ⇒ the timeout cases never settle and the guard stays held ⇒ F2 is dead for the rest of the session, which is exactly the bug being replaced; an implementation settling on both `exit` and `close` ⇒ the exactly-once assertion fails; a cancel that notifies an error ⇒ fails |
| AC-40.29 | integration | **Spawn hygiene.** `runRegionPicker` spawns with `shell: false`, `windowsHide: true`, `stdio: ['ignore','pipe','pipe']` and an **argv array**. Cases: an exe path and an `--out` path each containing a space, an `&`, a single quote, and non-ASCII characters are passed through unmangled (asserted on the spy's argv, not on a command string); both pipes are drained and each is capped at `PICKER_LOG_MAX_BYTES` keeping the **tail**; readiness matches only an anchored, whole-line `PICKER_READY_MARKER` and only the **first** occurrence; the child is killed on `app.will-quit`, with `SIGKILL` after `PICKER_KILL_GRACE_MS` | Research-backed (Node `child_process`: with `shell: false` argv is passed to `CreateProcess` without a shell re-parse; an undrained pipe can deadlock a chatty child) + round-11 finding R11-2 | any `shell: true` or string-concatenated command line ⇒ the `&`-in-path case fails; an undrained stderr ⇒ the verbose-stderr case hangs; an unanchored `includes(marker)` ⇒ a stderr line mentioning the marker falsely signals readiness |
| AC-40.30 | integration | **Publication races and failures.** Five vitest cases beyond AC-40.6's happy path: (a) `linkSync` throwing `EEXIST` for `{base}.png` and `{base}_2.png` ⇒ the capture lands at `{base}_3.png`, and a non-`EEXIST` error is **not** swallowed as a collision; (b) the inbox watcher firing for the claimed path **before** registration returns ⇒ no duplicate `captures:inbox-changed`, and exactly one afterwards; (c) `POST /captures` rejecting ⇒ the file remains, the error is logged **with the final path**, `notifyUser` is called exactly once with that path (the **OS** surface, not `notifyInboxChanged` — round-14 finding), and no unlink is attempted; with `app.isPackaged === false` the same case must take the **tray-balloon** branch and never construct a `Notification`, and with `app.isPackaged === true` it must take the toast branch (round-15 finding: `Notification.isSupported()` is true in a dev run whose toast Windows will silently discard, so branching on it shows the user nothing); (d) **round-12 finding R12-1 — a watcher event with `filename === null`** (which Node permits and which cannot be matched against an owned path) delivered both before and after registration settles ⇒ still exactly one `captures:inbox-changed` for that capture, because the handler compares inbox PNG **sets** rather than paths; (e) a **delayed** event naming the claimed path arriving after suppression has been lifted ⇒ no second event. Cases (d) and (e) drive the notification decision function directly with a synthetic inbox listing, so they do not depend on real `fs.watch` timing; (f) **round-13** — the watcher's first listing over a **non-empty** inbox ⇒ the set is adopted as the baseline and **no** `captures:inbox-changed` is emitted; (g) **round-13** — a candidate reserved before a `linkSync` that throws `EEXIST` ⇒ the reservation is released, so a later listing containing that name **does** notify; (h) **round-14** — two captures inside one second: A settles at `{base}.png` and is announced, then B reserves `{base}.png`, takes `EEXIST`, releases, and settles at `{base}_2.png` ⇒ **exactly one** further `captures:inbox-changed` (for B), and `{base}.png` is never re-announced | Spec (§Result publication) + round-11 finding R11-3 + round-12 finding R12-1 + round-13 | an implementation that treats every `linkSync` throw as a collision ⇒ an `EACCES` becomes an infinite suffix walk (a); a watcher notification that is not suppressed ⇒ the filmstrip shows a capture the API has not registered (b); an unlink-on-register-failure ⇒ the user loses the pixels (c); a path-matching-only suppression ⇒ (d) and (e) both emit a spurious second refresh, which is the bug the set comparison exists to make impossible; an empty initial baseline ⇒ (f) fires a refresh at every app start; a reservation never released on a failed link ⇒ (g) is silent, and a real capture that later takes that name never reaches the filmstrip until the next poll; a single set doing both reservation and history ⇒ (h) re-announces the first capture, because releasing B's failed `{base}.png` candidate deletes A's settled name from history |
| AC-40.31 | unit | **Idempotent registration repairs `source`.** `packages/core/src/avkit_core/services/capture.py`: registering a path already present with `source = scan` updates the row's `source` to the registering source and persists it, while remaining idempotent in every other respect (no duplicate row, id preserved). Regression test in `tests/unit/test_capture_service.py` | Spec (§Result publication 4) + round-11 finding R11-3 | today's early-return ⇒ a capture the inbox scanner saw first is attributed to `scan` forever even after the picker registers it, so the UI can never tell a scanned file from a captured one ⇒ test fails against the unfixed service |
| AC-40.32 | integration | **The installed app resolves and runs the helper.** `assert-packaging-clean.ps1 -Installed` silently installs the NSIS output to a temp prefix (`/S /D=`) and then proves three separate things. **(1) The installer is this run's**: row 9a arms `packaging-installed` first and the chosen `.exe` in `NSIS_OUTPUT_DIR` must be newer than the arm stamp, so a leftover installer from an earlier build cannot satisfy the gate (round-12 finding R12-3; same staleness defence as R4-3-R5). **(2) The helper is present and runnable from the installed layout**: `INSTALLED_PICKER_REL` exists, and running it with a bogus flag returns `PICKER_EXIT_ERROR` — which also proves the self-contained publish brought its own runtime. **(3) The shipped resolver finds it**: the installed `av-kit.exe` is run with `PICKER_PATH_PROBE_FLAG` (`--avkit-picker-path`), which makes main call its real `resolvePickerExePath()`, print `PICKER_PATH=<resolved>`, and quit without a window; the gate requires that path to exist and to be under the install prefix. (2) alone would leave `{process.resourcesPath}` resolution unproved — the reviewer's round-12 point — so (3) is the one that speaks to what a user experiences. Finally the installed tree is scanned for `OVERLAY_FORBIDDEN_TOKEN` and `overlay*` names, and the app is uninstalled in `finally` | Local Canon (07 distribution) + round-11 finding R11-4 + round-12 finding R12-3 | a dev-tree-only path check passes while the packaged app cannot find its helper — the failure a user sees and no other gate catches; a stale `ui/out` packaged into the installer ⇒ the installed-tree overlay scan fails; a framework-dependent publish ⇒ the exe fails to start and the exit-code assertion fails; a resolver that hardcodes a dev-tree path ⇒ (3) fails even though (2) passes (P9); an installer older than the arm stamp ⇒ fail (P10). Evidence-gated `[B]` only if `electron-builder` cannot produce an installer in the sandbox (`external-error`, follow-up `DIST-INSTALLER-SANDBOX`); the **GUI** F2 drive from inside the installed app stays that follow-up's scope, with the human live smoke (row 7b) covering it on the dev tree |
| AC-40.33 | integration | **A published capture never cancels its request.** Round-12 finding R12-2: `ui/src/main/index.ts` currently cancels from a `catch` that also covers the post-publication phase. Three vitest cases over the interactive poll handler with a mocked API: (a) `captureRegionFromGui` resolves a path and `completeCaptureRequest` **rejects** ⇒ `cancelCaptureRequest` is **never called**, the error is logged with the inbox path, and the request is left pending; (b) `captureRegionFromGui` resolves `null` (a real `PICKER_EXIT_CANCEL`) ⇒ `cancelCaptureRequest` **is** called exactly once; (c) `captureRegionFromGui` itself throws before producing a file ⇒ cancel is still allowed, because nothing was produced. Round-13 adds the recovery the first three only implied: (d) after (a), the poll hands the **same** Pending row back ⇒ the picker is **not** invoked and `completeCaptureRequest` is retried with the same `{requestId, path}` from the journal, succeeding on the retry ⇒ the request completes and the journal entry is dropped; (e) the row is observed `Expired` ⇒ the entry is dropped, no further retries are attempted, and `notifyUser` is called exactly once with the inbox path. Round-14 adds the states the poll must tell apart, which is what makes (d) and (e) reachable in production rather than only under mocks: (f) the poll returns `{ kind: 'unavailable' }` for a backend restart across several ticks ⇒ the journal entry **survives**, no notification fires, and the retry succeeds once the backend answers again; (g) the poll returns `{ kind: 'ok' }` and the journalled id reads `Completed` ⇒ the entry is dropped **silently**, with no notification and no further complete call; (h) `{ kind: 'ok' }` whose listing does not contain the id at all ⇒ terminal, treated as (e); (i) **round-15, corrected in round-16** — `complete` rejecting with **409** ⇒ the journal re-reads the row's actual status and that decides: `Completed` ⇒ dropped silently; `Expired` (the near-TTL confirm, where the completion call itself expired the row) or `Cancelled` ⇒ dropped **with** the terminal notice naming the inbox path; `unavailable` on the reconciling read ⇒ the entry survives. In no case is the 409 retried into a loop. Observable: mocked `complete`/`cancel` call counts, picker-invocation count, `notifyUser` call count | Spec (§Result publication rule 5) + round-12 finding R12-2 | the shipped shape — one `try` around the whole body — fails (a): the user confirms a region, the PNG is in the inbox, and the waiting agent is told the request was `Canceled`. A fix that stops cancelling altogether fails (b) and (c). Leaving the request pending with no journal fails (d) — the poll reopens the picker and the user is asked to select a region a second time for a capture already taken, every 500 ms until the TTL expires; retrying forever with no terminal notification fails (e) — the pixels exist and nobody is told; today's `listPendingRequests`, which collapses a dead backend and an empty list to the same `[]` (`capture-register.ts:83-97`), fails (f) by dropping the journal during the restart the retry exists for, and fails (g) by re-completing a request that already completed; a terminal notice routed through `notifyInboxChanged` fails (e) for a user whose window is closed to tray; treating a 409 as a retryable failure fails (i) by retrying against a row that has already left Pending; treating it as terminal-**success** fails (i) the other way and is the round-16 bug: a confirm near the 120 s TTL is expired by its own completion call, so the agent sees `Expired`, the journal is discarded silently, and the user is never told the PNG in the inbox never reached the requester |

Retired MEU-39 ACs (superseded by this spec revision, recorded in the handoff):
AC-39.19, AC-39.20, AC-39.22 (overlay half — the pixel guard itself survives in AC-40.6),
AC-39.25 (overlay-preload half), AC-39.29. Their vitest assertions are **removed with
their surface**, not neutralized in place — G36 does not apply to tests whose subject is
deleted by an approved spec revision; the review verifies none of the surviving ACs lost
coverage.

Retired in round 11, with the gates they existed to describe (recorded here so the numbering
gap is deliberate rather than lost): **AC-40.17** and **AC-40.20** (Roslyn static and
control-flow proofs that each WinForms handler bound its mapped controller method — they
policed the shape of av-kit's own C# source, which `PickerControllerTests` proves behaviourally
and a reviewer reads faster than a syntax walk), **AC-40.22** (a prose validator scoring the
reflection's distinct-word ratio), and **AC-40.23** (a minted run-nonce proving the app under
test was the app that ran). None of them asserted a fact about the shipped capture feature.

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Overlay host technology | Human-approved | 2026-08-27 USER_EXPLICIT: C# WinForms .NET 8 sidecar; Chromium path deleted, no fallback |
| Why not Chromium (evidence) | Research-backed | [electron#40515](https://github.com/electron/electron/issues/40515): transparent `BrowserWindow`s render opaque black/gray on affected Windows systems with hardware acceleration enabled. The issue establishes the **defect class**, not an incidence rate — no percentage is claimed here. `desktopCapturer` additionally captures all monitors to produce one thumbnail |
| Grab primitive | Research-backed | `Graphics.CopyFromScreen` (GDI BitBlt) — ShareX `Screenshot.cs` shape; spec's ShareX map already pins this intent |
| DPI handling | Research-backed | PerMonitorV2 via `app.manifest`; with it, `Screen.FromPoint` bounds are physical pixels, so freeze/crop/rubber-band share one coordinate space (no `scaleFactor` math — that lived in the deleted overlay) |
| Cold-start latency (spawn per F2, no warm process) | Research-backed | A self-contained .NET 8 WinForms process starts in the low hundreds of milliseconds; ShareX — the spec's own intent source — likewise builds its picker form per invocation. **The human decision covered the toolchain, not a latency budget**, so no acceptance figure is attributed to the user. Spawn-per-invocation is adopted as the simplest correct design; if the row-9 live smoke measures a startup that is perceptibly worse than the deleted overlay, a warm-process follow-up is filed rather than assumed away |
| Self-contained publish (no trimming) | Research-backed | WinForms does not support IL trimming (MS docs); self-contained required — user machines don't carry the .NET Desktop Runtime |
| Staging handoff (helper writes to a path main chose, main publishes) | Local Canon | Timestamp naming (`registerFileName`) and the register flow stay in tested TS (`capture-register.ts`); the helper stays name-agnostic |
| Losslessness of staging→inbox publication | Research-backed | Staging lives **inside** the inbox directory, so publication is a same-directory operation with no cross-volume copy. Round-11 finding R11-3 replaced `rename` with `link`+`unlink`: `rename` silently **replaces** an existing name, and `registerFileName()` resolves to the second, so two captures in one second lost one. `link` fails with `EEXIST` instead, which turns the collision into a name-claim loop (`_2`, `_3`, … matching the SSOT's existing convention) rather than data loss. The staging name is dot-prefixed and non-`.png` so the watcher and the PNG listing both ignore it (AC-40.6) |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `docs/build-plan/09-screenshot-capture.md` | modify | Spec revision per WP-1 table + new §Native region picker |
| `docs/build-plan/07-distribution.md` | modify | extraResources + build step rows |
| `.agent/context/meu-status.yaml` | modify | MEU-40 row; phase 9 note/plan refs |
| `.agent/context/meu-registry.md` | modify | Rendered by `tools/meu_status.py render` |
| `native/region-picker/avkit-region-picker.csproj` | new | net8.0-windows WinForms, manifest, publish props; assembly name matches `PICKER_EXE_REL` (`avkit-region-picker.exe`) |
| `native/region-picker/app.manifest` | new | PerMonitorV2 |
| `native/region-picker/Program.cs` | new | argv parse, `Run(args, ICaptureSource, IPickerDialog)` seam, capture-before-show ordering, `PICKER_READY_MARKER` from the first `Shown`, `PICKER_EXIT_*` mapping — no geometry |
| `native/region-picker/RegionForm.cs` | new | Receives an **already-frozen** bitmap; draws shade and rubber band; every handler delegates to `PickerController` — no geometry, and no capture |
| `native/region-picker/PickerController.cs` | new | tested owner of drag state; consumes `RectMath`; produces the confirm/cancel outcome |
| `native/region-picker/RectMath.cs` | new | pure rect logic (normalize/min-edge/clamp) |
| `native/region-picker-tests/avkit-region-picker-tests.csproj` | new | xunit; no Roslyn dependency (round-11 trim). Declares the `Category=RealDesktop` trait so §1b can filter it |
| `native/region-picker-tests/RectMathTests.cs` | new | AC-40.1–40.3 |
| `native/region-picker-tests/PickerControllerTests.cs` | new | AC-40.16 controller state machine (drag/min-edge/clamp/Enter/Esc) |
| `native/region-picker-tests/ProgramExitTests.cs` | new | AC-40.4, AC-40.16 — `Program.Run` outcome → `PICKER_EXIT_*` with a fake dialog |
| `native/region-picker/ScreenCaptureSource.cs` | new | The `ICaptureSource` GDI implementation: `Format32bppArgb` bitmap, `CopyFromScreen` with `SourceCopy | CaptureBlt`, alpha forced opaque (AC-40.26) |
| `native/region-picker-tests/CaptureGeometryTests.cs` | new | AC-40.25, AC-40.26 — negative-origin and mixed-DPI mapping; capture-before-show ordering and exact crop against a fake `ICaptureSource` |
| `native/region-picker-tests/RealDesktopCaptureTests.cs` | new | AC-40.27 — trait `Category=RealDesktop`; real `CopyFromScreen` against a painted fixture, primary display required, secondary display skipped when absent |
| `ui/src/main/capture-picker.ts` | new | Path resolution, spawn hygiene (`shell:false`, argv array, bounded pipe draining), the total lifecycle state machine with startup/interaction timeouts and kill-on-quit, the in-flight guard, and collision-safe publication (AC-40.5, 40.6, 40.28–40.30) |
| `ui/src/main/capture-overlay.ts` | delete | replaced by `capture-picker.ts` + rewritten `captureRegionFromGui` (new home: `capture-picker.ts`) |
| `ui/src/main/overlay-preload.ts`, `overlay-freeze-buffer.ts`, `overlay-page-target.ts`, `overlay-rect.ts` | delete | overlay surface gone |
| `ui/src/renderer/overlay.html`, `src/overlay.ts`, `src/overlay-interaction.ts` | delete | overlay surface gone |
| `ui/src/main/index.ts` | modify | import from `capture-picker`; GUI/hotkey call sites unchanged in shape. **The interactive call site changes** (round-12 finding R12-2): its single `try` is split at the publication boundary so the `catch` can no longer cancel a request whose PNG is already in the inbox — pre-publication failures may cancel; post-publication failures log, journal the `{requestId, path}` and retry rather than cancel (AC-40.33). Also answers `PICKER_PATH_PROBE_FLAG` by printing `PICKER_PATH=<resolvePickerExePath()>` and quitting without a window, which is what lets the installed proof exercise the shipped resolver (R12-3, AC-40.32) |
| `ui/src/main/capture-register.ts` | modify | Owns the **completion journal** (round-13, R12-2): `Map<requestId, { path, attempts, nextAttemptAt }>` written at publication, consulted by `startInteractivePoll` **before** the pending row reaches the picker, retried with capped backoff while the row is Pending, dropped with a single `notifyUser` when it is observed terminal. Also re-specifies the poll itself (round-14): it returns `{ kind: 'ok', rows } \| { kind: 'unavailable', reason }` so a dead backend is no longer indistinguishable from an empty pending list — today both are `[]` (`capture-register.ts:83-97`), which would drop the journal during a backend restart. It keeps `?status=pending` for the ordinary tick and drops the filter **only while the journal is non-empty** (round-15), and reconciles a 409 from `complete` against that listing rather than assuming success (round-16, R16-1). The `POST /captures` Zod `.strict()` body and the register flow itself are untouched (AC-40.33 d/e) |
| `ui/src/main/notify-user.ts` | new | The one OS-level user notice for the capture path (round-14): branch on **`app.isPackaged`** (round-15) — packaged sets the AUMID from `electron-builder.yml`'s `appId` and shows a `Notification` whose click opens the file in Explorer; unpackaged sets no AUMID and goes straight to the tray balloon, with a parentless `dialog.showMessageBox` if the tray does not exist yet. `appendStdoutLog` on every branch, injectable for vitest and suppressed under `AVKIT_E2E`. Every "the user is notified" in §Result publication resolves to this (AC-40.30 c, AC-40.33 e) |
| `ui/src/main/capture-pixels.ts` | modify | keep; add `createFromPath` entry point for helper PNG guard |
| `ui/src/main/capture-inbox-watch.ts` | modify | Export the notification decision as a **pure function over inbox listings, not over event names** (round-12 finding R12-1): it compares the current PNG set against the last emitted set and returns whether to notify, so a `filename === null` event or one delayed past suppression cannot produce a spurious refresh (AC-40.30 d/e). Still ignore `PICKER_STAGING_PREFIX` names and suppress the claimed final path until registration settles (AC-40.6, AC-40.30) |
| `ui/electron.vite.config.ts` | modify | remove overlay preload + renderer inputs |
| `ui/package.json` | modify | `clean:out`, `build:picker`, `build:picker-stub`, `dist:prep` scripts; `dist:prep` = clean → build → build:picker **in that order**; `dist` = `npm run dist:prep && electron-builder --win nsis --x64`; `test:e2e` = `playwright test`; `test:e2e:capture` = `playwright test tests/e2e/capture-picker.test.ts --reporter=json` (AC-40.18 receipt) |
| `ui/electron-builder.yml` | modify | `region-picker` extraResources |
| `ui/tests/unit/capture-page.test.ts`, `capture-main.behavior.test.ts` | modify | retire overlay ACs; add AC-40.5–40.14 asserts |
| `ui/tests/unit/capture-picker.test.ts` | new | AC-40.5–40.8, 40.11 |
| `ui/tests/unit/overlay-freeze-buffer.test.ts`, `overlay-hit-test.test.ts`, `overlay-interaction.behavior.test.ts`, `overlay-page-target.test.ts` | delete | The four vitest files that exist only to test the deleted Chromium overlay. Named explicitly (round-11 reviewer note) so "`vitest run` is green" cannot be reached by leaving dead specs that import removed modules |
| `ui/tests/unit/capture-lifecycle.test.ts` | new | AC-40.28–40.30 — the lifecycle totality matrix, spawn hygiene, and the publication race/failure cases including the round-12 null-filename and delayed-event cases |
| `ui/tests/unit/capture-interactive.test.ts` | new | AC-40.33 — a published capture never cancels its request (round-12 finding R12-2) |
| `packages/core/src/avkit_core/services/capture.py` | modify | AC-40.31 — idempotent registration repairs `source` instead of returning the existing row unchanged. The only Python change in the project |
| `tests/unit/test_capture_service.py` | modify | AC-40.31 regression test (written first, Red before Green) |
| `global.json` | new | Pins the .NET SDK to the `DOTNET_SDK_BAND` band with `rollForward: latestFeature`, so the sidecar is not built against whatever SDK a machine happens to carry (AC-40.10) |
| `ui/tests/e2e/capture-picker.test.ts` | new | AC-40.18 — real-Electron capture path via the sidecar stub (confirm / cancel / all-black) |
| `native/region-picker-stub/avkit-region-picker-stub.csproj`, `Program.cs` | new | Deterministic console sidecar for E2E (`E2E_STUB_PROJECT_FILE`): parses `--out`, writes a non-black (or `AVKIT_STUB_PIXEL=black`) PNG, exits with `AVKIT_STUB_EXIT` — no UI, no display needed |
| `docs/BUILD_PLAN.md` | modify (**required edit**, AC-40.21) | Every hub line that states the deleted Chromium design is rewritten to name the region picker; today's hub fails `assert-build-plan-hub.ps1`, so this is a failing predicate, not an audit |
| `.agent/context/known-issues.md` | modify | Registers `CAPTURE-JOURNAL-VOLATILE` (round-14: the completion journal does not survive a main-process restart — see Out of Scope), and conditionally registers `E2E-SANDBOX-NODISPLAY` when task row 7a takes its evidence-gated `[B]`; the id is referenced across the build plan today but registered in no `FOLLOWUP_SOURCES` file, so an unregistered follow-up would fail the gate |
| `{plan folder}/named-sets.json` | new (**exists**) | Single owner of every threshold, exit code, file set, and marker list used by the gates |
| `{plan folder}/assert-task-rows.ps1`, `assert-red-oracle.ps1`, `assert-overlay-deleted.ps1`, `assert-packaging-clean.ps1`, `assert-e2e-wired.ps1`, `assert-build-plan-hub.ps1`, `assert-oracle-selftests.ps1`, `assert-closeout.ps1`, `assert-handoff-markers.ps1`, `assert-handoff-acs.ps1`, `assert-exec-review-dispatch.ps1` | new (**exist**) | The executable gates, each with a `-SelfTest` negative oracle where its predicate could otherwise be vacuous. Round 11 **deleted** `assert-picker-binding.ps1`, `assert-smoke-disposition.ps1`, `run-live-smoke.ps1` and `assert-reflection-quality.ps1` — about 3,700 lines that policed av-kit's own source shape and prose rather than any fact about the shipped app |
| `{plan folder}/lib-disposition.ps1` | new (**exists**) | Single owner (PR-9) of the rules two gates still share, 628 → 112 lines after the round-11 trim: `KEY=VALUE` disposition parsing, the `[B]` evidence contract (`Test-BlockedEvidence`: objective class, reproduced `ERROR_SIGNATURE`, follow-up that resolves against `FOLLOWUP_SOURCES`, receipt pinned to the row), and artifact freshness (`Test-ArtifactFresh`). The run-identity nonce protocol went with the smoke gates |
| `{plan folder}/arm-run.ps1` | new (**exists**) | Single owner of run arming: deletes a `RUN_STAMPS` artifact and writes its stamp, so a gate can require an artifact produced **after** arming. `-SelfTest` proves the freshness predicate rejects a deleted (A1) and a stale (A3) artifact while accepting a fresh one (A2), and that the stamp is written before the run (A4). Round-11: the minted-nonce identity protocol is deleted with the smoke gates it existed for; only `e2e-capture` is armed now |
| `{plan folder}/run-verification-plan.ps1` | new (**exists**) | Single executable owner of the Verification Plan section list (task row H1-2); `-SelfTest` proves every scheduled section names a gate script that exists |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| Chromium overlay as fallback when helper fails | out-of-scope | — | Human-approved 2026-08-27 USER_EXPLICIT: "Delete it entirely"; fallback would keep electron#40515 reachable exactly where it fires |
| Warm/daemon picker process for latency | out-of-scope | — | Research-backed: spawn-per-invocation is ShareX's own shape and a self-contained .NET 8 process starts in the low hundreds of ms, so no warm process is scheduled here. Not attributed to the human decision, which covered the toolchain only. **No MEU is pre-registered** (round-3 finding N7: `deferred` requires a registered target MEU-ID, and none exists). The human live smoke (row 7b) instead records how the picker *feels* against the deleted overlay, in the handoff; if it is perceptibly worse, a *new* MEU is proposed then — from evidence, not in advance. (The former `LATENCY_MS` smoke-disposition field went with the smoke gates deleted in round 11; this row is corrected rather than resurrecting them.) |
| Durable completion journal across a main-process restart | out-of-scope | — | Round-14 reviewer note, accepted as an explicit shipping bound: the journal is in memory, so an Electron restart inside a request's 120 s TTL loses the retry — the PNG still stands in the inbox and still reaches the filmstrip via `scan_inbox`, and only the request expires. Making it durable needs persistence the backend does not have (`CaptureRequest` has no shot association after `Expired`, `packages/core/src/avkit_core/domain/capture.py:41-43`), which is a schema change in a project whose one Python change is AC-40.31. Registered as follow-up `CAPTURE-JOURNAL-VOLATILE` in `.agent/context/known-issues.md` so the limitation is not lost |
| macOS / Linux picker + hotkey | out-of-scope | — | `09-screenshot-capture.md` §Named deferrals ("macOS / Linux overlay + hotkey — Windows-first") |
| In-picker annotation toolbar | out-of-scope | — | `09-screenshot-capture.md` §Named deferrals ("In-overlay arrows — annotation is the Capture page / MCP") |
| Python `mss` adapter / MCP bbox-grab changes | out-of-scope | — | `09-screenshot-capture.md` §MCP: bbox path is FastAPI+mss by spec; unaffected surface |
| REST / MCP route or schema changes | out-of-scope | — | MEU-37/38 approved; register/complete/cancel bodies unchanged (`ROUTE_COUNT_AFTER=71`, `ACTION_INDEX_AFTER=67` hold) |
| Windows.Graphics.Capture instead of GDI | out-of-scope | — | Spec's ShareX map pins the GDI `Screenshot.cs` shape; WGC needs WinRT interop + HDR tone-map complexity with no MVP gain (Research-backed, recorded here) |
| ms-screenclip: / Snipping Tool protocol | out-of-scope | — | Returns the image only to MSIX-packaged apps; av-kit ships unpackaged NSIS (`07-distribution.md` §NSIS) |

---

## BUILD_PLAN.md Hub Reconciliation

This project revises Phase 9's OS-surface architecture, so `docs/BUILD_PLAN.md` — the hub
every agent reads first — must stop stating the deleted Chromium design. Round-5 finding
R5-1: the previous treatment here was a report-only `Select-String` that printed a match
count and let task row 8 close while changing nothing. It is replaced by a **failing
predicate** owned by one script (PR-9), scheduled as Verification Plan §8a and re-run by
`assert-closeout.ps1`. Concrete task row: task.md #8. Rule (AC-40.21):

- No line of `HUB_FILE` may match a `HUB_FORBIDDEN_TOKENS` term (`desktopCapturer`,
  `overlay`; OrdinalIgnoreCase, so `Overlay` is caught) **unless that same line also names
  a `HUB_REQUIRED_TOKENS` term** — a line may reference the old design only while naming
  the replacement that supersedes it.
- The hub must name every `HUB_REQUIRED_TOKENS` term at least once, so scrubbing the old
  words without stating the new architecture also fails.

Today's hub — four bare `overlay` lines (32, 93, 111, 143) and zero `region picker` —
**fails** this gate, and those exact line texts are pinned as self-test oracle H0. The gate
is therefore provably non-vacuous before the edit, and stays non-vacuous after it: this row
cannot close as a no-op.

```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-27-p9-capture-native-picker/assert-build-plan-hub.ps1 *> C:/Temp/av-kit/build-plan-hub.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/build-plan-hub.txt; exit $code
```

---

## Verification Plan

The section list has exactly **one executable owner** —
`{plan folder}/run-verification-plan.ps1` (task row H1-2). The table below names each
section's gate and receipt; it does not restate the commands, so the two cannot drift
(round-3 finding N6/PR-9). `-SelfTest` prints this inventory and fails if any section
names a gate script that is not on disk (task row 0a).

```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-27-p9-capture-native-picker/run-verification-plan.ps1 *> C:/Temp/av-kit/verification-plan.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/verification-plan.txt | Select-Object -Last 40; exit $code
```

| § | Gate | What it proves | Receipt |
|---|------|----------------|---------|
| 0 | `assert-oracle-selftests.ps1` | All nine surviving negative oracles reject their false-pass input — run FIRST, so no gate below is trusted unproven | `C:/Temp/av-kit/oracle-selftests.txt` |
| 1 | `dotnet test native/region-picker-tests -c Release` | AC-40.1–40.4, 40.16, 40.24–40.26 green (the RED counterpart is gated by `assert-red-oracle.ps1`) | `C:/Temp/av-kit/dotnet-test.txt` |
| 1b | `dotnet test … --filter Category=RealDesktop` | AC-40.27 — the **real** `CopyFromScreen` returns the fixture's pixels at the geometry's rect. Deferrable: the multi-monitor case only, with an evidence-gated disposition at `REALDESKTOP_DISPOSITION_FILE`; the primary-display case is not `[B]`-able | `C:/Temp/av-kit/dotnet-realdesktop.txt` |
| 2 | `assert-packaging-clean.ps1` | AC-40.10 — ordered `&&`-segment composition, RID/self-contained fragments, `global.json` band, and a clean rebuild through the production `dist:prep` segment | `C:/Temp/av-kit/packaging-clean.txt` |
| 2b | `assert-packaging-clean.ps1 -Installed` | AC-40.32 — arm the run, silent-install **this build's** NSIS output from electron-builder's own `directories.output`, resolve `INSTALLED_PICKER_REL` and run it, probe the installed `av-kit.exe` with `--avkit-picker-path` so the **shipped resolver** is what answers, and prove no overlay leftovers shipped. Deferrable with a disposition at `PACKAGING_DISPOSITION_FILE` | `C:/Temp/av-kit/packaging-installed.txt` |
| 3 | `npm --prefix ui test` | AC-40.5–40.9, 40.11, 40.14, 40.28–40.30 vitest green | `C:/Temp/av-kit/ui-test.txt` |
| 4a | `npm --prefix ui run typecheck` | AC-40.15 — `tsc --noEmit` clean | `C:/Temp/av-kit/ui-typecheck.txt` |
| 4b | `npm --prefix ui run lint` | AC-40.15 — `eslint --max-warnings 0` clean | `C:/Temp/av-kit/ui-lint.txt` |
| 5a | `assert-overlay-deleted.ps1` | AC-40.9 — exact-count deletion across `ui/src` **and** `ui/out`, by token and by name (exact evidence) | `C:/Temp/av-kit/overlay-deletion.txt` |
| 6 | `uv run python tools/meu_status.py render --check` | AC-40.13 — registry SSOT drift-free | `C:/Temp/av-kit/drift-check.txt` |
| 7 | `uv run pytest tests/unit/test_capture_service.py` | AC-40.31 — idempotent register repairs `source` | `C:/Temp/av-kit/py-core-tests.txt` |
| 8 | `uv run python tools/export_openapi.py --check openapi.committed.json` | OpenAPI drift **proved, not asserted** — `packages/api/` is outside this project's boundary table, so the skip basis is the passing check itself | `C:/Temp/av-kit/openapi-check.txt` |
| 8a | `assert-build-plan-hub.ps1` | AC-40.21 — the hub every agent reads first no longer states the deleted Chromium design and names the replacement (a **failing predicate**, not a report) | `C:/Temp/av-kit/build-plan-hub.txt` |
| 9a | `assert-e2e-wired.ps1 -Mode Wired` | AC-40.19 — the real-Electron spec is discoverable, un-neutralized, declares each required case, is override-driven; the capture script and stub project exist | `C:/Temp/av-kit/e2e-wired.txt` |
| 9a1 | `arm-run.ps1 -Name e2e-capture` | Clears `E2E_EXECUTED_RECEIPT` and stamps the run, so §9d can prove the report it reads was produced by **this** run (round-5 finding R4-3-R5) | `C:/Temp/av-kit/arm-e2e-capture.txt` |
| 9b | `npm --prefix ui run test:e2e` | The full Wave-9 E2E suite stays green after the overlay deletion. **`dispositionedBy = 9d`**: a nonzero exit here is excused only when §9d passed and the disposition it validated says `BLOCKED=yes` with an objective class, a registered follow-up, and the `ERROR_SIGNATURE` reproduced in **this section's own** receipt (J1/J2). With `BLOCKED=no`, a red run still fails the runner | `C:/Temp/av-kit/ui-e2e.txt` |
| 9c | `npm --prefix ui run test:e2e:capture` (with `PLAYWRIGHT_JSON_OUTPUT_NAME`) | AC-40.18 — **runs** the real Electron → spawn → publish → register → refresh chain and emits the machine-readable JSON report §9d consumes. Also `dispositionedBy = 9d`, under the same excuse rule | `C:/Temp/av-kit/ui-e2e-capture.txt` + `C:/Temp/av-kit/e2e-capture-results.json` |
| 9d | `assert-e2e-wired.ps1 -Mode Executed` | AC-40.18 — the **single disposition point** for the capture E2E (round-5 finding R5-2). With `BLOCKED=no` the JSON report must be fresher than §9a1's stamp and show every required case present, `ok`, `expected`, from the capture spec file, with zero unexpected/skipped/flaky; with `BLOCKED=yes` the `[B]` must satisfy the shared evidence contract | `C:/Temp/av-kit/e2e-executed.txt` |

**The live smoke is a human step, not a section.** Task row 7b is `npm --prefix ui run dev`, F2,
drag, confirm — a PNG in the inbox and a filmstrip that refreshes, recorded in the handoff with
the observed `picker_startup_ms` and whatever the operator noticed about how it *felt*. Round 11
deleted the launcher, the minted run-nonce, and the disposition gate that surrounded it
(§10 and three scripts). The reason is the one thing the machinery could never do: a gate can
prove a process ran, but only a person can say the rubber band tracked the cursor and the freeze
frame did not flicker — and that judgement is the independent reviewer's to weigh, not a
PowerShell parser's.

**Sequencing — prove the native slice before deleting the Chromium path.** §1, §1b and §3 must be
green, and the human smoke recorded, **before** the overlay deletion lands (§5a, AC-40.9). The
task table orders it that way for a reason: deletion with no fallback was the human's explicit
choice, so the rollback position is "the sidecar is proven working on this machine", not "git
still has the old files". Deleting first would leave the app with no region capture at all if the
sidecar turned out to be wrong on real hardware.


## Open Questions

None. Both material decisions (toolchain; no-fallback deletion) were resolved
Human-approved 2026-08-27 before planning. Latency, DPI, and packaging behaviors are
resolved in the Spec Sufficiency Table.

---

## Research References

- [electron/electron#40515](https://github.com/electron/electron/issues/40515) — transparent `BrowserWindow` renders opaque black/gray with hardware acceleration on affected Windows systems (primary defect driver; the issue establishes the defect class, not an incidence rate)
- Node.js `fs` documentation — `fs.copyFile`/`fs.cp` carry **no atomicity guarantee**, which is why publication uses a same-directory `fs.renameSync` instead of a byte copy
- ShareX source map already pinned in `docs/build-plan/09-screenshot-capture.md` §ShareX source map (`RegionCaptureLightForm.cs`, `Screenshot.cs`, `CaptureHelpers.GetActiveScreenBounds`) — read for control flow only, GPL-3.0, no code translation (Golden Rule 5)
- Microsoft: WinForms high-DPI PerMonitorV2 (`app.manifest` `dpiAwareness`), `Graphics.CopyFromScreen`, WinForms trimming unsupported
- Toolchain receipt: `C:/Temp/av-kit/toolchain.txt` (dotnet SDK 8.0.424 present; rustc/cargo absent)
