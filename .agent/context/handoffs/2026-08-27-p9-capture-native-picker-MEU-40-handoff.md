---
date: "2026-09-01"
project: "2026-08-27-p9-capture-native-picker"
meu: "MEU-40"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-08-27-p9-capture-native-picker/implementation-plan.md"
build_plan_section: "bp09s9.7"
agent: "claude-opus-5"
reviewer: "gpt-5.6-sol"
predecessor: "2026-08-27-p9-capture-gui-MEU-39-handoff.md"
---

# Handoff: 2026-08-27-p9-capture-native-picker-MEU-40-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-40 — a native C# WinForms (.NET 8) region-picker sidecar replaces the Chromium
region overlay. The sidecar owns the two jobs the overlay did badly: it freezes the display
under the cursor with GDI **before** any window exists, and it picks the rectangle in a real
Win32 window. Electron keeps everything it was already good at — tray, hotkey, inbox watch,
filmstrip, annotate, and the existing `POST /captures` register path. The Chromium overlay is
**deleted with no fallback** (USER_EXPLICIT, 2026-08-27), so there is no second code path that
can regress to the black click-through sheet.

**Build Plan Section**: `docs/build-plan/09-screenshot-capture.md` §Native region picker
(helper process) — matrix item 9.7. Reaching it required a **spec revision**, not a silent
refactor: the section previously mandated `overlay = BrowserWindow, grab = desktopCapturer`.

**Predecessor**: `.agent/context/handoffs/2026-08-27-p9-capture-gui-MEU-39-handoff.md`

**Design decisions taken by the human (USER_EXPLICIT, 2026-08-27):**

| Decision | Choice | Alternatives rejected |
|---|---|---|
| Sidecar toolchain | **C# WinForms (.NET 8)** | Rust / C++ helper |
| Old Chromium path | **Delete entirely, no fallback** | Keep behind a flag |
| Not taken | — | `electron-screenshots` (keeps the Chromium overlay), `node-screenshots` + Chromium overlay (same electron#40515 bug class), koffi to user32/gdi32 (a Win32 app written in JavaScript), `ms-screenclip:` (returns the image only to MSIX-packaged apps; av-kit ships unpackaged NSIS) |

---

## Acceptance Criteria

> All 29 live plan ACs appear below. Four MEU-40 ACs were **retired during plan review
> (round 11)** and are recorded under §Retired ACs rather than dropped.

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-40.1 | unit | `RectMath.Normalize(p1,p2)` returns the axis-aligned rect for either drag direction | Spec | `native/region-picker-tests/RectMathTests.cs` | ✅ |
| AC-40.2 | unit | `RectMath.MeetsMinEdge` true iff both edges meet `PICKER_MIN_EDGE_PX` | Spec | `native/region-picker-tests/RectMathTests.cs` | ✅ |
| AC-40.3 | unit | `RectMath.ClampToBounds` never exceeds the frozen bitmap | Spec | `native/region-picker-tests/RectMathTests.cs` | ✅ |
| AC-40.4 | unit | Helper static contract: PerMonitorV2 `app.manifest`, `net8.0-windows` WinForms csproj, `PICKER_EXIT_*` constants asserted against `named-sets.json` | Spec | `native/region-picker-tests/ProgramExitTests.cs` | ✅ |
| AC-40.5 | integration | `capture-picker.ts` resolves packaged/dev/env exe path, spawns `['--out', staging]`, maps every `PICKER_EXIT_*` to an outcome | Spec | `ui/tests/unit/capture-picker.test.ts`; structural: `ui/tests/unit/capture-page.test.ts` | ✅ |
| AC-40.6 | integration | Lossless publication: `inspectNativeImagePixels` on the staged PNG; blocked means log + unlink + **no inbox `.png`, no register** | Spec | `ui/tests/unit/capture-picker.test.ts` | ✅ |
| AC-40.7 | integration | Single in-flight picker: a second `captureRegionFromGui` returns null without spawning | Spec | `ui/tests/unit/capture-picker.test.ts` | ✅ |
| AC-40.8 | integration | Interactive MCP path uses the picker: confirm to `.../complete`, cancel to `.../cancel` | Spec | `ui/tests/unit/capture-picker.test.ts`, `ui/tests/unit/capture-main.behavior.test.ts` | ✅ |
| AC-40.9 | unit | Chromium overlay deleted **from source and from build output** — zero `OVERLAY_FORBIDDEN_TOKEN` occurrences under every scan root | Human-approved | `assert-overlay-deleted.ps1` (§5a); `ui/tests/unit/capture-page.test.ts` | ✅ |
| AC-40.10 | integration | The production `dist` chain cleans, builds the picker, and publishes a runnable runtime | Local Canon | `assert-packaging-clean.ps1` (§2) | ✅ |
| AC-40.11 | integration | **Conditional** `AVKIT_E2E=1` short-circuit — only while `AVKIT_REGION_PICKER_PATH` is unset | Spec | `ui/tests/unit/capture-picker.test.ts` | ✅ |
| AC-40.12 | integration | Spec revision landed: 0 normative `desktopCapturer` matches and at least 1 `avkit-region-picker` match in `09-screenshot-capture.md`; `07-distribution.md` carries the extraResources rows | Human-approved | task row 1 receipt (`Select-String` over both build-plan files) | ✅ |
| AC-40.13 | integration | MEU-40 registered in `meu-status.yaml`; `tools/meu_status.py render --check` clean | Local Canon | §6 registry-drift receipt | ✅ |
| AC-40.14 | unit | Renderer surface unchanged: preload `captureRegion` + `captures:inbox-changed` retained; vite preload inputs contain only `index` | Spec | `ui/tests/unit/capture-page.test.ts` | ✅ |
| AC-40.15 | integration | Full gates green after deletion (vitest, `tsc --noEmit`, eslint `--max-warnings 0`, `dotnet test`) **and** a recorded live-smoke latency | Local Canon | §1 / §4a / §4b receipts; task row 7b smoke record | ✅ |
| AC-40.16 | integration | `PickerController` is the production owner of drag state, driven end-to-end in xunit | Spec | `native/region-picker-tests/PickerControllerTests.cs`, `ProgramExitTests.cs`, `Fakes.cs` | ✅ |
| AC-40.18 | e2e | Real-Electron capture path **executed** under Playwright against the deterministic sidecar stub | Local Canon | `ui/tests/e2e/capture-picker.test.ts` (§9c / §9d) | ✅ |
| AC-40.19 | integration | The E2E is **wired** before it is judged: spec under `testDir`, matches `testMatch`, no `.skip(` / `.only(` | Local Canon | `assert-e2e-wired.ps1 -Mode Wired` (§9a) | ✅ |
| AC-40.21 | integration | The hub states the shipped architecture — no line of `HUB_FILE` still describes the deleted Chromium design | Local Canon | `assert-build-plan-hub.ps1` (§8a) | ✅ |
| AC-40.24 | unit | `PICKER_READY_MARKER` is declared beside the exit codes and emitted only after the frozen frame is on screen | Spec | `native/region-picker-tests/ProgramExitTests.cs` | ✅ |
| AC-40.25 | unit | Global-to-local mapping survives a hostile monitor layout (negative-origin, mixed-DPI synthetic bounds) | Research-backed | `native/region-picker-tests/CaptureGeometryTests.cs` | ✅ |
| AC-40.26 | unit | The frame is captured **before** the window exists and the crop is exact, through the `ICaptureSource` seam | Spec | `native/region-picker-tests/CaptureGeometryTests.cs` | ✅ |
| AC-40.27 | integration | Real-desktop proof: the real `ScreenCaptureSource` returns a painted fixture's pixels at the fixture's rect | Local Canon | `native/region-picker-tests/RealDesktopCaptureTests.cs` (trait `Category=RealDesktop`, §1b) | ✅ |
| AC-40.28 | integration | Helper lifecycle totality — every declared exit code, an off-contract code, `close` without exit, both timeouts | Spec | `ui/tests/unit/capture-lifecycle.test.ts` | ✅ |
| AC-40.29 | integration | Spawn hygiene: `shell:false`, `windowsHide:true`, `stdio:['ignore','pipe','pipe']`, argv **array** (paths containing spaces and quotes) | Research-backed | `ui/tests/unit/capture-lifecycle.test.ts` | ✅ |
| AC-40.30 | integration | Publication races and failures — `EEXIST` collision suffixes, null filename, delayed writes | Spec | `ui/tests/unit/capture-lifecycle.test.ts` | ✅ |
| AC-40.31 | unit | Idempotent registration **repairs** `source`: a row already inserted as `scan` is updated to the registering source | Spec | `tests/unit/test_capture_service.py:583` `test_ac_40_31_register_repairs_source_on_a_scanned_row` | ✅ |
| AC-40.32 | integration | The **installed** app resolves and runs the helper from its own prefix; bogus argv gives `PICKER_EXIT_ERROR`; zero overlay tokens in the payload | Local Canon | `assert-packaging-clean.ps1 -Installed` (§2b) | ✅ |
| AC-40.33 | integration | A published capture never cancels its request (round-12 finding R12-2) | Local Canon | `ui/tests/unit/capture-interactive.test.ts` | ✅ |

### Retired ACs

#### Retired MEU-39 ACs

These were MEU-39 acceptance criteria whose **surface** this MEU deletes. They were removed
*with* their surface, never neutralized in place — no assertion was edited to pass, no test was
skipped, no `.skip`/`.only`/`.todo` was introduced. Each asserted something about the Chromium
overlay that no longer exists:

| Retired AC | What it asserted | Why it is gone |
|---|---|---|
| AC-39.19 | Overlay `BrowserWindow` geometry / display selection | The overlay window is deleted; the sidecar owns display selection (AC-40.25) |
| AC-39.20 | Overlay drag / rubber-band behaviour in the renderer | Drag state moved into `PickerController` (AC-40.16) |
| AC-39.22 | Overlay freeze frame **and** the black-pixel guard | The overlay half is gone; **the pixel guard survives** as AC-40.6 |
| AC-39.25 | Overlay preload contract | The overlay preload entry is removed from `electron.vite.config.ts` (AC-40.14) |
| AC-39.29 | Overlay teardown / escape wiring | Escape is now a sidecar exit code, `PICKER_EXIT_CANCEL` (AC-40.28) |

#### Retired MEU-40 ACs (plan review, round 11)

| Retired AC | What it would have asserted | Why it was retired |
|---|---|---|
| AC-40.17, AC-40.20 | Roslyn semantic-model proofs that WinForms handlers bind to `PickerController` | A syntax walk is slower and weaker than the end-to-end controller drive in AC-40.16; a reviewer reads the binding faster than the analyzer proves it |
| AC-40.22 | A prose validator scoring the reflection's distinct-word ratio | Bureaucratic load; judgement belongs to the reviewer, not to a word-ratio metric |
| AC-40.23 | A minted run-nonce proving which app instance produced the smoke | Replaced by the human smoke record plus the objective corroboration in row 7b |

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

Tests were written first in both toolchains and observed failing before any implementation.

| Test | Red Output (snippet) | Green Output | File:Line |
|------|---------------------|--------------|-----------|
| `RectMathTests` / `PickerControllerTests` / `ProgramExitTests` / `CaptureGeometryTests` / `RealDesktopCaptureTests` (xunit) | `Failed!  - Failed: 56, Passed: 13, Skipped: 0, Total: 69` — e.g. `RealDesktopCaptureTests.PrimaryDisplay_CaptureReturnsTheFixturesPixelsAtTheFixturesRect`: `Assert.Equal() Failure: Values differ / Expected: {Width=1920, Height=1080} / Actual: {Width=1, Height=1}` | `67 passed` (`Category!=RealDesktop`) plus `2 passed` (`Category=RealDesktop`) | receipt `C:/Temp/av-kit/dotnet-test-red.txt`; `native/region-picker-tests/RealDesktopCaptureTests.cs:49` |
| `capture-picker` / `capture-lifecycle` / `capture-interactive` (vitest) | `Test Files 5 failed \| 34 passed (39)`, `Tests 8 failed \| 242 passed (250)` — `FAIL tests/unit/capture-picker.test.ts`, `FAIL ... AC-40.5 the picker sidecar seam exists in the main process` | `323 passed` across `40` files | receipt `C:/Temp/av-kit/ui-test-red.txt`; `ui/tests/unit/capture-picker.test.ts` |
| `AC-40.9 the Chromium overlay is gone from ui/src` | `FAIL tests/unit/capture-page.test.ts > AC-40.9` — deliberate: the overlay still existed at Red | passes after `capture-overlay.ts` is deleted | receipt `C:/Temp/av-kit/ui-test-red.txt`; `ui/tests/unit/capture-page.test.ts` |
| `test_ac_40_31_register_repairs_source_on_a_scanned_row` | assertion on `shot.source` — the pre-change `_upsert_shot` returned the existing `scan` row unchanged | `PY_CORE_TESTS` green | `tests/unit/test_capture_service.py:583` |

### Commands Executed

Every command ran under the P0 redirect-to-file pattern with receipts under `C:/Temp/av-kit/`.
`ELECTRON_RUN_AS_NODE` is unset for every Electron/Playwright receipt (deviation D8).

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| `run-verification-plan.ps1` (§1 through §9d, the full J-gate) | 0 | `PASS: VERIFICATION_PLAN 18 sections` — no section deferred, so no disposition file was consulted |
| `dotnet test native/region-picker-tests --filter Category!=RealDesktop` | 0 | `67 passed` |
| `dotnet test native/region-picker-tests --filter Category=RealDesktop` | 0 | `2 passed` (real desktop, painted fixture) |
| `npm --prefix ui run test:unit` (vitest) | 0 | `323 passed`, 40 files |
| `npm --prefix ui run typecheck` / `lint` | 0 | 0 errors, 0 warnings (`--max-warnings 0`) |
| `npx playwright test` (full suite) | 0 | `59 passed` |
| `npx playwright test tests/e2e/capture-picker.test.ts` | 0 | `4 expected, 0 unexpected, 0 flaky, 0 skipped` |
| `assert-overlay-deleted.ps1` | 0 | `PASS: OVERLAY_DELETION` |
| `assert-packaging-clean.ps1` | 0 | `PASS: PACKAGING_CLEAN_PATH` — clean rebuild; `avkit-region-picker.exe` 152,576 bytes |
| `assert-packaging-clean.ps1 -Installed` | 0 | `PASS: PACKAGING_INSTALLED` — `bogusArgvExit 1`, `overlayTokens 0`, `staleArtifacts []`; installed picker resolved at `resources/region-picker/avkit-region-picker.exe` inside its own prefix |
| `assert-e2e-wired.ps1 -Mode Wired` | 0 | `PASS: E2E_WIRED` |
| `assert-build-plan-hub.ps1` | 0 | `PASS: BUILD_PLAN_HUB` |
| `assert-task-rows.ps1` (through H1-1) | 0 | `PASS: TASK_ROW_GATE 18 of 31 rows closed; 4 producer binding(s) statically named` |
| `tools/meu_status.py render` then `render --check` | 0 | `Drift check passed - SSOT loaded (40 MEUs, 10 phases)` |
| OpenAPI `--check` | 0 | empty output (no drift) |
| `npm --prefix ui run dev` (live smoke, row 7b) | 0 by design | see §Live smoke below |

### Quality Gate Results

```
dotnet test (Category!=RealDesktop):  67 passed, 0 failed
dotnet test (Category=RealDesktop):    2 passed, 0 failed
vitest:                              323 passed, 0 failed (40 files)
tsc --noEmit:                          0 errors
eslint --max-warnings 0:               0 warnings
playwright (full suite):              59 passed
playwright (capture spec):             4 expected, 0 unexpected, 0 flaky, 0 skipped
pytest (capture service):              PY_CORE_TESTS green
anti-placeholder:                      0 matches
registry drift / OpenAPI drift:        clean
verification plan:                    18 of 18 sections PASS
```

### Live smoke (AC-40.15, task row 7b — human-judged)

Human verdict, USER_EXPLICIT 2026-09-01: *"capture button works and after changing to F3 hot
key works as well"*; rubber band and freeze frame *"yes, felt fine"*; *"no flicker, no black
flash"*. Esc cancelled cleanly.

Objective corroboration: **5 rows in `capture_shots`** from the live run — 2 `Gui` (button) and
3 `Hotkey` — at 1268x531, 2800x1606, 876x694, 1935x1317, 880x580, 35-787 KB, all present in the
configured inbox. Widths above the 1920 *logical* width prove PerMonitorV2 native-resolution
capture; the file sizes rule out a black freeze.

**`picker_startup_ms` = 136 / 167 / 151 (median 151)**, spawn to `ready`. That is not
perceptibly worse than the deleted overlay, so the warm-process follow-up named in the plan's
§Out of Scope trigger was **not** filed.

Esc was also verified non-interactively: `EXIT_CODE=2`, no staging file left behind
(`RESULT=ESC_CANCELS_CLEANLY`).

Two environmental notes, neither a defect: **F2 was already held by another process on this
machine**, which the app surfaces through `capture-hotkey-banner` — F3 registered first try,
which is designed behaviour. And the `dev` process later exited 1 on
`EBUSY ... watch rottiboo.png`, a vite watcher racing an unrelated file written into
`ui/src/renderer/src/assets/` six minutes after the last capture; AGENTS.md §Windows Shell
already records that `dev` exiting 1 on teardown is not a build failure.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `native/region-picker/avkit-region-picker.csproj` | new | `net8.0-windows` WinForms, manifest wired, assembly name `avkit-region-picker.exe` |
| `native/region-picker/app.manifest` | new | PerMonitorV2 DPI awareness |
| `native/region-picker/Program.cs` | new | argv parse, `Run(args, ICaptureSource, IPickerDialog)` seam, capture-before-show ordering, `PICKER_READY_MARKER`, `PICKER_EXIT_*` |
| `native/region-picker/RegionForm.cs` | new | Receives an **already-frozen** bitmap; draws shade and rubber band; every handler delegates to `PickerController` |
| `native/region-picker/PickerController.cs` | new | Tested owner of drag state; consumes `RectMath`; produces the confirm/cancel outcome |
| `native/region-picker/RectMath.cs` | new | Pure rect logic — normalize / min-edge / clamp |
| `native/region-picker/ScreenCaptureSource.cs` | new | The GDI `ICaptureSource`: `Format32bppArgb` bitmap, `BitBlt` with `SRCCOPY \| CAPTUREBLT` through P/Invoke, alpha forced opaque |
| `native/region-picker-tests/` (7 sources + csproj) | new | xunit: `RectMathTests`, `PickerControllerTests`, `ProgramExitTests`, `CaptureGeometryTests`, `RealDesktopCaptureTests`, `Fakes.cs`, `MultiMonitorFact.cs` |
| `native/region-picker-stub/` | new | Deterministic sidecar stub the Playwright E2E drives (confirm / cancel / all-black) |
| `ui/src/main/capture-picker.ts` | new | Path resolution, spawn hygiene, the total lifecycle state machine with startup and interaction timeouts, publication and register. **Round 2:** publication committed at the link (finding 1), blocked outcomes notified with the helper's stderr tail (finding 2), bounded readiness parser (finding 3) |
| `ui/src/main/capture-overlay.ts` | **deleted** | The Chromium overlay. No fallback, no flag |
| `ui/src/main/notify-user.ts` | new | The one OS-level notice for the capture path; branches on `app.isPackaged` for the AUMID. **Round 2:** `path` is optional, for failures that produced no file |
| `ui/src/main/index.ts` | modified | Imports from `capture-picker`; the interactive call site's single `try` split at the publication boundary |
| `ui/src/main/capture-register.ts` | modified | Completion journal (`Map<requestId, {path, attempts, nextAttemptAt}>`) consulted before the pending row reaches the picker |
| `ui/src/main/capture-pixels.ts` | modified | `createFromPath` entry point for the helper-PNG black-frame guard |
| `ui/src/main/capture-inbox-watch.ts` | modified | Notification decision exported as a pure function over inbox listings, not over event names |
| `ui/electron.vite.config.ts` | modified | Overlay preload and renderer inputs removed |
| `ui/package.json` | modified | `clean:out`, `build:picker`, `build:picker-stub`, `dist:prep` (clean, then build, then build:picker — in that order) |
| `ui/electron-builder.yml` | modified | `region-picker` extraResources |
| `ui/tests/unit/capture-picker.test.ts` | new | AC-40.5 through AC-40.8, AC-40.11 |
| `ui/tests/unit/capture-lifecycle.test.ts` | new | AC-40.28 through AC-40.30. **Round 2:** six cases for review findings 1-3, written red first |
| `ui/tests/unit/capture-interactive.test.ts` | new | AC-40.33. **Round 2:** local `Notice` alias widened (fixture only) |
| `ui/tests/e2e/capture-picker.test.ts` | new | AC-40.18 — real Electron driven against the sidecar stub |
| `ui/tests/e2e/global-setup.ts` | modified | **Round 3:** fails closed when any `ui/src` file is newer than `out/main/index.js`, so a fresh report can no longer be produced by a stale bundle (review R2-1) |
| `packages/core/src/avkit_core/services/capture.py` | modified | AC-40.31 — registration repairs `source`. The only Python change in the project |
| `tests/unit/test_capture_service.py` | modified | AC-40.31 regression test, written first |
| `global.json` | new | Pins the .NET SDK band with `rollForward: latestFeature` |
| `docs/build-plan/09-screenshot-capture.md` | modified | **Spec revision** — the Chromium overlay design is replaced by the native helper contract |
| `docs/build-plan/07-distribution.md` | modified | extraResources and build-step rows |
| `.agent/context/meu-status.yaml`, `.agent/context/meu-registry.md` | modified | MEU-40 row (registry rendered from the SSOT) |
| `.agent/context/known-issues.md` | modified | Registers `CAPTURE-JOURNAL-VOLATILE` |
| `.agent/context/current-focus.md` | modified | Session outcome |

**The one Python change (AC-40.31)** — registration now repairs a row the inbox scanner won the
race to insert:

```diff
         existing = uow.capture_shots.get_by_path(resolved)
         if existing is not None:
-            return existing
+            # The registering source wins over whatever the row already carries. The
+            # region picker writes its PNG into the inbox and registers it a moment
+            # later, so the inbox scanner can reach the file first and insert the row
+            # as CaptureSource.Scan; returning that row unchanged would leave every
+            # captured shot indistinguishable from a file the user dropped in by hand.
+            if existing.file_size == probe.file_size and existing.source == source:
+                return existing
+            updated = replace(existing, width=probe.width, height=probe.height,
+                              file_size=probe.file_size, source=source, updated_at=now)
+            uow.capture_shots.save(updated)
+            return updated
```

**The interactive call site (AC-40.33, round-12 finding R12-2)** — capture and completion are no
longer inside one `try`, so a failing completion retries instead of cancelling a request whose
PNG is already in the inbox:

```diff
+  // The lifecycle itself lives in `runInteractiveTick`; this only supplies the picker. Capture and
+  // completion are deliberately no longer inside one try: a completion that fails must retry, not
+  // cancel a request whose PNG is already in the inbox.
   startInteractiveRequestLoop({
     ready: () => !capturing,
     capture: async () => {
       capturing = true
       try {
-        return await captureRegionFromOverlay({ ... })
+        return await captureRegionFromGui({
+          inboxDir: captureInboxDir,
+          copyToClipboard: captureCopyToClipboard,
+          source: 'gui',
+          window,
+          register: false,
+        })
       } finally {
         capturing = false
       }
     },
   })
```

---

## Deviations from the approved plan

Surfaced for the reviewer rather than buried. None changes an AC's meaning; several
**strengthen** a gate that could otherwise have passed vacuously.

| # | Deviation | Why |
|---|---|---|
| D1 | `RegionForm` forces the foreground with `TopMost` **plus** `ForceToForeground` - `SetWindowPos(HWND_TOPMOST)`, `BringWindowToTop`, then a best-effort `SetForegroundWindow` (`native/region-picker/RegionForm.cs:29`, `:88-96`) | Root cause of the sidecar window losing focus. `TopMost` and `Form.Activate` alone are not enough: the picker is launched by Electron, so the process has never held the foreground, and Windows lets a background process show a window without raising it. Corrected in round 2 - the original wording claimed no `SetForegroundWindow` call, which the code contradicts; the shipped behaviour is stronger than the wording described, and the review confirmed it is not a defect |
| D2 | Patch scripts made CRLF-aware (`nl = '\r\n' if '\r\n' in t else '\n'`) | Anchors matched zero times against CRLF files, silently |
| D3 | `packages/core/tests/services/test_capture_service.py` corrected to **`tests/unit/test_capture_service.py`** in `named-sets.json`, the plan, and `task.md` (1 + 3 + 3 occurrences) | The planned path never existed in this repo. Flagged for the reviewer: row 6a's RED receipt would have been satisfied by that usage error alone, which is why the **path** was corrected rather than the receipt re-pointed at whatever passed |
| D4 | The vite overlay-input strip moved from row 7c to row 7 | Row 7's own gate reads that config; leaving the strip in 7c left row 7 red for a reason unrelated to its deliverable |
| D5 | `AVKIT_E2E_API_BASE` added to `index.ts` only | Narrowest surface that makes the E2E deterministic |
| D6 | AC-40.5 additionally asserted structurally in `capture-page.test.ts` | A behavioural test alone could pass with the seam inlined; the structural assertion pins the seam's existence |
| D7 | Row 7 carried exactly one expected AC-40.9 failure | The overlay still existed at that point — Red by construction, not a regression |
| D8 | `ELECTRON_RUN_AS_NODE` must be unset for every Electron/Playwright receipt | It is exported in this shell; with it set, Electron silently runs as plain Node and the E2E proves nothing |
| D9 | `CaptureFilmstrip` keeps the timestamped caption in the DOM whether or not the thumbnail loads | Screenshots of the same app are indistinguishable as thumbnails; the name is the only discriminator |
| D10 | Packaging gate: the NSIS install now runs under `Start-Process -Wait -PassThru` plus a bounded 300 s poll for the installed exe; the `finally` polls for `Uninstall*.exe`, runs it, then retries `Remove-Item` up to 10 times and warns if the prefix survives | The one-click stub hands off to a child and returns **before** the tree is written — the gate was racing the installer, not detecting a defect. Fixed by waiting, not by weakening the assertion; the cleanup can no longer orphan a temp install |
| D11 | Installed-picker exit code read via `Start-Process -Wait -PassThru -NoNewWindow` | The picker is a GUI-subsystem (`WinExe`) process: `&` does not wait for it and `$LASTEXITCODE` then reports the *previous* command. Empirically `directExit: null` versus `startProcessExit: 1` |
| D12 | Installed overlay-token scan scoped to `<prefix>\resources` with a fail-closed existence guard | All 9 `desktopCapturer` hits were inside Electron's own `av-kit.exe` launcher — that string is an Electron API name. A whole-prefix scan asserts something about Electron, not about av-kit |
| D13 | **Spec correction in `09-screenshot-capture.md`**: the blit goes to `gdi32!BitBlt` through P/Invoke, and `CAPTUREBLT` is documented as **required, not optional** | `Graphics.CopyFromScreen` validates its argument against the `CopyPixelOperation` enum and throws `InvalidEnumArgumentException` for `SourceCopy \| CaptureBlt`, since the OR of the two is not itself a declared member. The plan's §Proposed Changes table still says `CopyFromScreen`; the implementation and the spec now both say `BitBlt` |
| D14 | `named-sets.json`: `AC_IDS` gained the missing `AC-40.33` (28 entries to 29, now equal to `AC_COUNT`), and a new `RETIRED_ACS` set was declared. `assert-handoff-acs.ps1` subtracts `RETIRED_ACS` before the totality check **and additionally asserts** that `RETIRED_ACS` and `AC_IDS` are disjoint and that every retired ID still appears in the plan | `AC_COUNT` was bumped to 29 when AC-40.33 was added in round 12 but the ID list was not, so the gate could never pass. The plan also names the four round-11 retirements in prose, so a raw token sweep of the plan saw 33 IDs. The replacement is strictly stronger than the original: a resurrected AC **and** a lost retirement record now each fail the gate |

Also folded in during execution: the row-9 type/lint harness fixes, and the repair of row H2-2's
command, which still invoked a deleted `assert-reflection-quality.ps1` and its artifact.

---

## Round-2 Corrections (review round 1 — 3 findings)

Round 1 returned `changes_required` with three findings and accepted everything else
(pixel path, overlay deletion, tests, packaging, D1–D14). Each finding below was fixed
**tests-first**: the six new cases in `capture-lifecycle.test.ts` were written and run red
against the shipped code before any production line changed, and the round-1 failure output is
quoted rather than summarised.

### Red receipt (before the fixes) — `C:/Temp/av-kit/r2-red-vitest.txt`

```
Tests  6 failed | 30 passed (36)

× a renderer torn down mid-announcement still publishes and never cancels the request
  AssertionError: expected "spy" to not be called at all, but actually been called 1 times
× an error exit tells the user why and carries the helper stderr tail into the log
  AssertionError: expected [] to have a length of 1 but got +0
× a spawn error tells the user which executable could not start
  AssertionError: expected [] to have a length of 1 but got +0
× a cancel stays silent while a blocked black frame does not
  AssertionError: expected [] to have a length of 1 but got +0
× a helper that never writes a newline keeps the parser under PICKER_LINE_MAX_BYTES
  TypeError: (0 , getPickerParserState) is not a function
× a line whose head was discarded can never satisfy the readiness match
  Error: Test timed out in 5000ms
```

The first line is the finding-1 defect reproduced exactly: a PNG published into the inbox,
and its interactive request cancelled anyway.

### Finding 1 (Medium) — publication is now a committed state

`finalizeCapturedPng` calls its `notify()` callback **outside** the try that guards
registration (`ui/src/main/capture-register.ts:190`), so a `notifyInboxChanged` that throws —
the real Electron race where the renderer is torn down between `window.isDestroyed()` and
`webContents.send()` — rejected `publishStagedCapture` *after* the hard link had already
published the file. `runInteractiveTick` cannot tell a post-publication rejection from a
pre-publication one, so it took the `catch` branch and called `/cancel` on a request whose PNG
was on disk (AC-40.33 violated).

Fix (`ui/src/main/capture-picker.ts:483-508`): everything after a successful `claimInboxName`
— the reservation lift, the announcement, the register call — runs inside a try whose catch
logs and falls through to `return dest`. Publication is committed at the link; nothing after it
may reject.

Test: `a renderer torn down mid-announcement still publishes and never cancels the request`
drives the **production** path — a real `runInteractiveTick` over a real `captureRegionFromGui`
with the fake child process and a window whose `isDestroyed()` answers `false` and whose
`send()` throws. It asserts `cancel` is never called, `complete` is called once, and exactly one
PNG lands in the inbox. This is the boundary the previous AC-40.33 test could not reach: it
started from a `capture()` mock that had already returned a path.

### Finding 2 (Medium) — blocked helper outcomes are visible and diagnostic

Every non-cancel failure resolved `null` with no notification and a log line that omitted the
helper's own diagnosis, so a missing, denied, wedged or crashing helper was indistinguishable
from a user pressing Escape — "F2 does nothing".

Fix:
- `withStderrTail` (`capture-picker.ts:191-207`) folds a whitespace-collapsed, 400-byte tail of
  the helper's stderr into every `blocked` reason, so the log line and the user-visible notice
  both carry it. `PICKER_REASON_STDERR_BYTES` is the declared bound.
- `captureRegionFromGui` (`capture-picker.ts:565-571`) notifies on `blocked`. **Cancel stays
  silent** — it is the user's own decision — and so does the re-entrant-press guard.
- The black/empty-frame guard and a name that cannot be claimed also notify
  (`capture-picker.ts:470-478`, `capture-picker.ts:486-492`); both were previously silent.
- `Notice.path` became optional (`notify-user.ts:21-26`): a helper that never produced a file
  has no path to point at. The toast's click handler, the dialog detail and the log line all
  branch on its presence, so no branch renders `undefined`.

Tests: `an error exit tells the user why and carries the helper stderr tail into the log`
(asserts the notice title, the stderr text inside the body, and the same text in the `[Capture]
picker blocked:` line), `a spawn error tells the user which executable could not start`, and
`a cancel stays silent while a blocked black frame does not` — which pins both halves of the
rule in one case.

### Finding 3 (Low) — the readiness parser is bounded

`stdout` was tail-clamped but `lineBuffer` was not: a helper writing without newlines grew the
parser's partial line for the whole startup timeout plus kill grace.

Fix (`capture-picker.ts:60-70`, `capture-picker.ts:310-330`): `PICKER_LINE_MAX_BYTES` (4096)
bounds the unterminated line. An overlong partial is discarded and the line it belonged to is
**poisoned** via `lineDiscarded`, so a discard can never re-anchor mid-stream and turn
`yyy…ready` into a readiness match. `getPickerParserState()` exposes the live buffer size and
the discard flag.

Tests: `a helper that never writes a newline keeps the parser under PICKER_LINE_MAX_BYTES`
floods 256 KiB of newline-free stdout and asserts both the stored pipe tail and the parser's
pending line stay under their declared caps; `a line whose head was discarded can never satisfy
the readiness match` proves the poison rule by showing the run still dies on the startup
timeout.

### Round-2 quality gates

| Check | Result | Receipt |
|-------|--------|---------|
| Vitest, capture lifecycle (red, before fixes) | `6 failed \| 30 passed` | `C:/Temp/av-kit/r2-red-vitest.txt` |
| Vitest, capture lifecycle (green) | `36 passed` | `C:/Temp/av-kit/r2-green-vitest.txt` |
| Vitest, full `ui/tests/unit` | `329 passed` (40 files; was 323 — the six new cases) | `C:/Temp/av-kit/r2-vitest-all.txt` |
| `npm --prefix ui run typecheck` | exit 0 | `C:/Temp/av-kit/r2-typecheck.txt` |
| `npm --prefix ui run lint` | exit 0, `--max-warnings 0` | `C:/Temp/av-kit/r2-lint.txt` |
| Real-Electron capture E2E, re-armed and re-run | `PASS: E2E_EXECUTED 3 capture cases ran green … (report freshly produced by this run)`; `expected: 4, unexpected: 0, skipped: 0, flaky: 0` | `C:/Temp/av-kit/e2e-executed.txt`; `C:/Temp/av-kit/e2e-capture-results.json` |
| Full Playwright suite | `59 passed (5.3m)` | `C:/Temp/av-kit/ui-e2e.txt` |

`capture-picker.ts` changed, so row 7a's evidence was **re-armed and re-run** rather than
inherited: `arm-run.ps1` clears and stamps the JSON report first, so the green above cannot be a
stale report from before these fixes.

### Two test-fixture edits, and why they are not assertion edits

`Notice.path` becoming optional widened three collector arrays in `capture-lifecycle.test.ts`
(`const toasts: string[]` → `(string | undefined)[]`) and the local `Notice` alias in
`capture-interactive.test.ts`. Both are declarations of test scaffolding; no expected value,
matcher or assertion was touched. Under the Green-phase rule (AGENTS.md §FIC-Based TDD) setup
and fixtures may change, assertions may not.

---

## Round-3 Corrections (review round 2 — 1 finding)

Round 2 closed all three round-1 findings in source and unit tests, and opened one new one:
**R2-1 (High) — the re-armed real-Electron report was fresh, but the bundle it launched was not.**

### The defect

`arm-run.ps1` proves the *report* is new; nothing proved the *application* was. The Playwright
capture suite launches `ui/out/main/index.js`, and the round-2 rerun never rebuilt it: the
launched bundle was written at `2026-09-01T23:19:31-04:00`, before `capture-picker.ts`
(`2026-09-02T00:13:21-04:00`) and `notify-user.ts` (`00:13:12-04:00`) were corrected. The green
run therefore exercised the *pre-correction* main process — generic blocked log, unbounded
readiness buffer, `finalizeCapturedPng` outside the committed-state try, no blocked notification.
Reverting all three round-2 fixes would not have turned that run red. AC-40.18 / row 7a had not
been re-proven against the corrected application.

The reviewer named the root enabler precisely: `global-setup.ts` asserted only that the bundle
**exists**.

### Fix 1 — the harness fails closed on a stale bundle

`ui/tests/e2e/global-setup.ts` now walks `ui/src` for the newest modification time and refuses to
start Playwright when any source outruns `out/main/index.js`:

```ts
const newest = newestSource(resolve(here, '../../src'))
const built = statSync(main).mtimeMs
if (newest.mtimeMs > built) {
  throw new Error(
    `out/main/index.js is older than ${newest.path} — run npm run build before Playwright`,
  )
}
```

The tree is walked rather than stat'd at the root because a directory's own mtime does not move
when a nested file is edited. This is the structural half of the fix: the same mistake cannot be
made silently again, in this session or a later one.

**Negative oracle** — the guard is proven to reject, not merely to exist. `capture-picker.ts` was
touched to make it newer than the bundle and the capture suite re-run:

```
> 39 |     throw new Error(
     |           ^
    at globalSetup (P:\av-kit\ui\tests\e2e\global-setup.ts:39:11)

PASS: STALE_BUNDLE_REJECTED exit=1
```

Receipt: `C:/Temp/av-kit/r3-stale-bundle-oracle.txt`, driver
`C:/Temp/av-kit/r3-stale-oracle-driver.txt`.

### Fix 2 — rebuild, then re-arm, then re-run; and record the ordering

`C:/Temp/av-kit/r3-e2e.ps1` now runs `npm --prefix ui run build` **before** `arm-run.ps1`, and
writes a freshness receipt that makes the ordering self-evidencing rather than something a
reader has to reconstruct from file timestamps:

```
BUILT_UTC=2026-09-02T11:54:18.0661985Z
NEWEST_SRC=P:\av-kit\ui\src\main\capture-picker.ts 2026-09-02T11:45:04.6907879Z
CAPTURE_START_UTC=09/02/2026 11:54:22
PASS: BUNDLE_FRESHNESS build < capture run, sources < build
```

Receipt: `C:/Temp/av-kit/r3-bundle-freshness.txt`. The driver hard-fails on either inversion
(`FAIL: BUNDLE_STALE`, `FAIL: CAPTURE_RAN_BEFORE_BUILD`) instead of continuing into a suite whose
green would be meaningless.

The rebuilt bundle carries all three round-2 behaviors — one occurrence each of `helper said:`
(the stderr tail folded into a blocked reason), `post-publication step failed` (the committed-state
catch), and `pendingLineBytes` (the bounded parser state) in `ui/out/main/index.js`.

### Round-3 quality gates

| Check | Result | Receipt |
|-------|--------|---------|
| Stale-bundle negative oracle | `PASS: STALE_BUNDLE_REJECTED exit=1` — Playwright refused to start | `C:/Temp/av-kit/r3-stale-bundle-oracle.txt` |
| `npm --prefix ui run build` | exit 0, main + preload + renderer | `C:/Temp/av-kit/r3-ui-build.txt` |
| Bundle freshness ordering | `PASS: BUNDLE_FRESHNESS` (src `11:45:04` < build `11:54:18` < capture run `11:54:22`) | `C:/Temp/av-kit/r3-bundle-freshness.txt` |
| `assert-e2e-wired.ps1 -Mode Wired` | PASS | `C:/Temp/av-kit/e2e-wired.txt` |
| Capture E2E against the rebuilt bundle | `expected: 4, unexpected: 0, skipped: 0, flaky: 0` | `C:/Temp/av-kit/e2e-capture-results.json` |
| `assert-e2e-wired.ps1 -Mode Executed` | `PASS: E2E_EXECUTED 3 capture cases ran green … (report freshly produced by this run)` | `C:/Temp/av-kit/e2e-executed.txt` |
| Full Playwright suite | `59 passed (5.2m)` | `C:/Temp/av-kit/ui-e2e.txt` |
| `npm --prefix ui run typecheck` | exit 0 | `C:/Temp/av-kit/r3-typecheck.txt` |
| `npm --prefix ui run lint` | exit 0, `--max-warnings 0` | `C:/Temp/av-kit/r3-lint.txt` |

No production source changed in round 3 — the round-2 fixes stand as reviewed and their unit
evidence (`329 passed`, 40 files) is unaffected. The only edited file is the E2E harness's
`global-setup.ts`.

---

## Codex Validation Report

_Left blank for the reviewer agent (`gpt-5.6-sol`). The implementing agent does not author the
verdict — AGENTS.md §Execution Contract, self-review prohibition._

### Recheck Protocol

1. Read Scope and the AC table
2. Verify each AC against the Evidence section (file:line, not memory)
3. Run all Commands Executed and compare output
4. Run the quality gates independently
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| — | — | _pending review_ | — | — | — |

### Verdict

`pending`

---

## Deferred Items

| Item | Reason | Deferred-to MEU (scheduled) | Follow-up |
|------|--------|-----------------------------|-----------|
| The completion journal does not survive a main-process restart | out-of-scope (plan §Out of Scope, round-14) | none — tracked as a known issue, not as a deferred AC | `.agent/context/known-issues.md` entry `CAPTURE-JOURNAL-VOLATILE` |

No AC is deferred. The warm-process follow-up named in the plan's §Out of Scope trigger was
**not** filed: a median `picker_startup_ms` of 151 is not perceptibly worse than the deleted
overlay, so its trigger condition never fired.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-09-01 | claude-opus-5 | Initial handoff — 29 live ACs green, 18 of 18 verification sections PASS |
| Submitted for review | 2026-09-01 | claude-opus-5 | Dispatched to gpt-5.6-sol (`exec-review-p9-native-picker`) |
| Round 1 verdict | 2026-09-01 | gpt-5.6-sol | `changes_required`, 3 findings; pixel path, overlay deletion, tests, packaging and D1-D14 all accepted |
| Round 2 corrections | 2026-09-02 | claude-opus-5 | All 3 findings fixed tests-first (6 new cases, red receipt quoted); D1 wording corrected; E2E re-armed and re-run |
| Round 2 verdict | 2026-09-02 | gpt-5.6-sol | `changes_required`, 1 finding; all 3 round-1 findings closed, R2-1 stale launched bundle behind a fresh report |
| Round 3 corrections | 2026-09-02 | claude-opus-5 | `global-setup.ts` fails closed on a stale bundle (negative oracle proven); rebuild-then-arm driver with a recorded freshness ordering; E2E re-run against the corrected bundle |
