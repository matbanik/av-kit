---
date: "2026-09-02"
review_mode: "implementation"
target_plan: "docs/execution/plans/2026-08-27-p9-capture-native-picker/implementation-plan.md"
verdict: "approved"
findings_count: 0
round: 3
template_version: "2.1"
requested_verbosity: "standard"
agent: "gpt-5.6-sol"
dispatch_id: "exec-review-p9-native-picker"
---

# Critical Review: p9-capture-native-picker implementation

> **Review Mode**: `implementation`
> **Verdict**: `approved`

---

## Scope

**Target**: MEU-40 native region-picker sidecar, Electron lifecycle/publication integration,
capture registration repair, tests, deletion oracle, and installed-package proof.

**Review Type**: Independent execution/implementation review.

**Review emphasis**: Shipped behavior and failure modes. Process/template ceremony was not
treated as a source of findings.

---

## Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| 1 | Medium | **A PNG can be published and its interactive request then cancelled.** Failure scenario: the hard link succeeds and `settleInboxPath(dest)` records the final name, but the renderer is being torn down between `window.isDestroyed()` and `webContents.send()`, so `notifyInboxChanged` throws. `publishStagedCapture` never returns `dest`; `runInteractiveTick` classifies the rejected capture promise as a pre-publication failure and calls `/cancel`. The PNG remains in the inbox while the request is cancelled, violating AC-40.33. The AC-40.33 test begins with a mocked `capture()` that has already returned a path, so it cannot exercise this boundary. | `ui/src/main/capture-picker.ts:406`; `ui/src/main/capture-picker.ts:414`; `ui/src/main/capture-picker.ts:415`; `ui/src/main/capture-inbox-watch.ts:169`; `ui/src/main/capture-register.ts:346`; `ui/src/main/capture-register.ts:349` | Make publication a committed state that cannot reject after the link succeeds. At minimum, contain/log notification failures after `dest` exists and still return `dest`; preferably represent the result as a discriminated published/not-published outcome. Add an integration-style unit test in which the real publication path links the PNG, `webContents.send` throws, and the interactive request completes or journals completion but never calls cancel. | open |
| 2 | Medium | **Helper failures collapse into silent, generic cancellation-like behavior.** Failure scenario: GDI reports a useful reason on stderr and the helper exits `PICKER_EXIT_ERROR`. `runRegionPicker` stores the tail only in the test-facing `lastOutput`, logs merely `exited with code 1`, and `captureRegionFromGui` returns `null` without calling `notifyUser`. A user invoking F2 from the tray sees no picker and no visible error, and the application log omits the diagnostic that explains the failure. Missing-executable, timeout, missing-file, and black-frame paths have the same no-notification outcome. This contradicts the plan's user-visible blocked-state behavior and makes a broken installed helper look like an ordinary cancel. | `ui/src/main/capture-picker.ts:226`; `ui/src/main/capture-picker.ts:236`; `ui/src/main/capture-picker.ts:305`; `ui/src/main/capture-picker.ts:338`; `ui/src/main/capture-picker.ts:349`; `ui/src/main/capture-picker.ts:467` | Preserve cancel as silent, but surface every genuine blocked outcome through `notifyUser` and include the bounded stderr tail (when present) in the `[Capture]` log/reason. Add tests that an error exit and spawn error notify with actionable diagnostics, while exit 2 does not notify. | open |
| 3 | Low | **The readiness parser has an uncapped buffer despite the bounded-pipe contract.** Failure scenario: a wedged or mismatched helper continuously writes stdout without a newline. `stdout` is tail-clamped, but `lineBuffer += text` grows for every chunk until termination; a fast writer can consume substantial Electron-main memory during the startup timeout and kill grace. The existing log-bound test floods newline-terminated stderr and therefore misses this path. | `ui/src/main/capture-picker.ts:283`; `ui/src/main/capture-picker.ts:289`; `ui/src/main/capture-picker.ts:290`; `ui/tests/unit/capture-lifecycle.test.ts:328` | Bound the partial-line buffer independently (or use an incremental line parser that discards an overlong non-matching line) while retaining exact whole-line readiness matching. Add a no-newline stdout flood test and assert both stored output and parser state stay within the declared cap. | open |

---

## Substantive Results

### Pixels, geometry, and native window ordering

- Pass: `Program.Run` captures before `IPickerDialog.Show`; the real form's HWND is created by
  `ShowDialog`, after the BitBlt. `RegionForm` is instantiated earlier as a managed object, but
  its constructor does not force handle creation, so the substantive freeze-before-window rule
  holds.
- Pass: the direct `gdi32!BitBlt` uses the target display's signed `bounds.X/Y`, writes into a
  bitmap sized to that display, and uses `SRCCOPY | CAPTUREBLT`. Alpha is normalized before the
  frame is shown and before the crop is saved.
- Pass: a direct .NET 8 runtime probe reproduced D13: `Graphics.CopyFromScreen` rejects
  `SourceCopy | CaptureBlt` as an invalid `CopyPixelOperation`. The P/Invoke is justified.
- Pass: crop tests assert dimensions and a coordinate-derived pixel pattern at four corners and
  center. The recorded real-desktop run passed both primary and secondary-display fixtures with
  production `ScreenCaptureSource` (`2 passed`, no skips).
- Limitation accepted by the spec: HDR/scRGB color fidelity is not solved by GDI BitBlt.

### Deleted overlay

- Pass: the independent deletion gate found zero `desktopCapturer` tokens under `ui/src` and
  `ui/out`, zero stale overlay artifacts, zero deleted files still present, and zero overlay Vite
  inputs.
- Pass: a broader scan found old overlay literals only in deletion assertions. No source branch,
  preload entry, renderer input, or packaged fallback remains.
- Pass: the installed-package receipt reports zero payload tokens and zero stale overlay-named
  artifacts.

### Tests

- Pass: focused reruns produced `67 passed` native tests, `68 passed` relevant Vitest tests, and
  `18 passed` capture-service tests.
- Pass: no `.skip`, `.only`, `.todo`, or `.fixme` neutralization exists in the reviewed test
  surfaces. The dynamic secondary-monitor skip is an explicit hardware predicate; the recorded
  real-desktop receipt ran both cases without skipping.
- Pass: the fake capture source is supplemented by `RealDesktopCaptureTests`, which paints a
  fixture and reads its pixels through the production BitBlt path. The deterministic sidecar E2E
  runs real Electron spawn/publication/register boundaries, not a mocked main process.
- The red receipts support tests-first execution. Because the directory is not a git work tree,
  byte-for-byte assertion immutability cannot be reconstructed independently; no current-tree or
  receipt evidence contradicts the handoff's claim.
- Gap: findings 1 and 3 identify failure boundaries the current tests do not exercise.

### Lifecycle and publication

- Pass: declared/off-contract exit mapping, spawn-error handling, close-without-code behavior,
  startup and interaction timeouts, graceful-then-forceful kill, `will-quit`, single in-flight
  enforcement, argv array use, `shell:false`, `windowsHide:true`, and piped stdio are covered and
  passed.
- Pass: black/empty pixels are rejected before publication; collision naming uses hard-link
  claims and advances `_2`, `_3`, and so on without overwriting.
- Pass: registration failures retain the published PNG, and the in-memory completion journal
  prevents ordinary completion failures from becoming cancellation.
- Fail: post-publication notification exceptions can still cross the boundary and cancel the
  request (finding 1).
- Fail: blocked helper outcomes are not user-visible and discard useful stderr from normal logs
  (finding 2).
- Fail: the readiness partial-line buffer is not bounded (finding 3).

### Packaging

- Pass: `dist -> dist:prep -> clean:out + build + build:picker` is exact-segment checked;
  `build:picker` is a self-contained `win-x64` publish and `extraResources` maps it to
  `resources/region-picker`.
- Pass: the current installed-package receipt comes from a fresh NSIS artifact, installs into a
  temporary prefix, runs the installed helper with bogus argv and observes exit 1, and probes the
  installed Electron resolver for an existing helper path under that same prefix.
- Pass: packaging mutation tests reject hollow/echoed scripts, missing clean, late clean,
  framework-dependent publish, stale installer, wrong output directory, and dev-tree resolver
  answers.

---

## Deviations D1-D14

| Deviation | Result | Substance |
|-----------|--------|-----------|
| D1 | Accepted behavior; handoff wording stale | `RegionForm` now uses `TopMost` plus `SetWindowPos`, `BringWindowToTop`, and best-effort `SetForegroundWindow`. The handoff's claim that it uses no `SetForegroundWindow` is false, but the implemented focus behavior is stronger and does not create an open defect. |
| D2 | Accepted | CRLF-aware patch anchoring fixes a zero-match execution defect; it does not weaken a product assertion. |
| D3 | Accepted | The corrected Python test path exists and executes; the former path did not. |
| D4 | Accepted | Moving Vite-input deletion to the row that deletes the overlay keeps the gate causally aligned. |
| D5 | Accepted | `AVKIT_E2E_API_BASE` is confined to the E2E path and makes the real-Electron backend deterministic. |
| D6 | Accepted | The added structural check supplements behavioral coverage; it does not replace it. |
| D7 | Accepted | The lone expected red failure represented the still-present overlay before deletion. |
| D8 | Accepted | Unsetting `ELECTRON_RUN_AS_NODE` is necessary for Electron/Playwright evidence to exercise Electron. |
| D9 | Accepted | Keeping the filename caption is a real usability improvement and does not weaken a capture gate. |
| D10 | Accepted | `Start-Process -Wait`, bounded artifact polling, and cleanup strengthen the installed proof against the NSIS handoff race. |
| D11 | Accepted | `Start-Process -Wait -PassThru` is the correct way to observe the WinExe helper's exit code here. |
| D12 | Accepted | Scanning `resources` excludes Electron's own launcher API strings while still covering av-kit's app payload and extra resources; overlay-named files are scanned across the full prefix. |
| D13 | Accepted | Direct BitBlt is required to express `SRCCOPY | CAPTUREBLT`; independently reproduced on the installed .NET runtime. |
| D14 | Accepted | Adding AC-40.33 closes the live-ID count mismatch. The gate also requires disjoint live/retired sets and retention of every retirement record, so the change is not a weakened subtraction-only check. |

---

## Verification Evidence

| Check | Result | Receipt |
|-------|--------|---------|
| Native tests excluding real desktop | `67 passed` | `C:/Temp/av-kit/review-dotnet-2.txt` |
| Recorded real-desktop tests | `2 passed`, `0 skipped` | `C:/Temp/av-kit/dotnet-realdesktop.txt` |
| Focused picker/lifecycle/interactive Vitest | `68 passed` | `C:/Temp/av-kit/review-vitest-2.txt` |
| Capture-service pytest | `18 passed` | `C:/Temp/av-kit/review-pytest.txt` |
| Gate mutation/self-tests | `9 gates proven non-vacuous` | `C:/Temp/av-kit/review-oracle-selftests-2.txt` |
| Overlay deletion | `PASS: OVERLAY_DELETION` | `C:/Temp/av-kit/review-overlay.txt` |
| `CopyFromScreen` flag probe | Invalid `CopyPixelOperation` exception reproduced | `C:/Temp/av-kit/review-copyfromscreen-probe.txt` |
| Recorded capture Playwright | `4 passed`, no skipped/unexpected/flaky | `C:/Temp/av-kit/e2e-capture-results.json` |
| Recorded installed package | `PASS: PACKAGING_INSTALLED` | `C:/Temp/av-kit/packaging-installed.txt` |

---

## Verdict

`changes_required` — the native pixel path, overlay deletion, test foundations, gate changes,
and installed packaging proof are sound, but the shipped Electron boundary can still cancel an
already-published interactive capture, genuine helper failures are not visibly surfaced, and the
readiness parser violates its own memory bound. Correct the three findings and recheck in round 2.

---

## Round 2 Recheck (2026-09-02)

**Intent anchor**: This recheck determines whether the three round-1 failure boundaries are fixed
in the real Electron-main source and pinned by meaningful tests, without reopening the already
accepted native picker, overlay-deletion, packaging, or D1-D14 work.

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| R2-1 | High | **The re-armed real-Electron report is fresh, but it exercised a pre-correction main bundle.** Failure scenario: `arm-run.ps1` stamped at `2026-09-02T04:14:31.9280160Z` and the JSON report was written at `04:14:44.4550210Z`, so the report itself is fresh. However, the E2E launches `ui/out/main/index.js`; that file was last written at `2026-09-01T23:19:31-04:00`, before `capture-picker.ts` (`2026-09-02T00:13:21-04:00`) and `notify-user.ts` (`00:13:12-04:00`) changed. The launched bundle still has the generic blocked log, unbounded readiness buffer, post-link `finalizeCapturedPng` call outside a catch, and no blocked notification. `global-setup.ts` checks only that the bundle exists, and the round-2 runner builds only the picker stub. Thus removing all three round-2 source fixes would not make this fresh E2E run fail; AC-40.18/row 7a has not been re-proven against the corrected application. | `ui/tests/e2e/capture-picker.test.ts:169-170`; `ui/tests/e2e/global-setup.ts:7-10`; `ui/out/main/index.js:1203-1206`; `ui/out/main/index.js:1251-1259`; `ui/out/main/index.js:1343-1365`; `ui/out/main/index.js:1380-1384`; `C:/Temp/av-kit/r2-e2e.ps1:5-17` | Run `npm --prefix ui run build` after the corrections and before arming/running Playwright. Verify the rebuilt `ui/out/main/index.js` contains the round-2 behaviors, then re-arm and rerun the targeted capture E2E, the full Electron suite, and `assert-e2e-wired.ps1 -Mode Executed`. | open |

### Round-1 Finding Disposition

| Round-1 finding | Status | Recheck evidence |
|-----------------|--------|------------------|
| 1. Published PNG could still lead to request cancellation | **closed** | `publishStagedCapture` now contains every normal post-link step in the committed-state `try/catch` and returns `dest` after renderer IPC failure (`ui/src/main/capture-picker.ts:486-528`). The new test traverses `runInteractiveTick -> captureRegionFromGui -> linkSync -> notifyInboxChanged`, makes `webContents.send()` throw, and asserts no cancel, one completion, and one PNG (`ui/tests/unit/capture-lifecycle.test.ts:672-719`). The pre-fix receipt fails specifically because `cancel("req-hostile")` was called. |
| 2. Blocked helper outcomes were silent and undiagnosed | **closed** | All `runRegionPicker` blocked outcomes are enriched through the bounded stderr-tail helper before logging/resolution (`ui/src/main/capture-picker.ts:191-210`, `:265-288`); `captureRegionFromGui` notifies only `blocked`, while cancel and re-entry remain silent (`:555-573`). Black/empty and unclaimable-name paths notify separately (`:466-493`). Tests pin error stderr in both notice and terminal log, spawn error visibility, silent cancel, and visible black-frame rejection (`ui/tests/unit/capture-lifecycle.test.ts:721-782`). Exit-code classification at `:382-420` is unchanged. |
| 3. Readiness parser partial line was unbounded | **closed** | The parser discards a partial line over 4096 units, poisons that line until its newline, and exposes its retained state (`ui/src/main/capture-picker.ts:61-71`, `:127-133`, `:333-360`). The flood test would exceed the bound if the clamp were removed, and the poison test times out on the pre-fix parser because the surviving `ready` tail incorrectly starts the interaction timer (`ui/tests/unit/capture-lifecycle.test.ts:784-815`). |

### Regression and Test-Rigor Checks

- **No swallowed required failure / no changed exit classification**: post-publication announcement
  and bookkeeping errors are intentionally contained only after the hard link; pre-publication
  failures still return `null` or reject into the existing cancellation path. Exit 2 remains the
  sole helper cancel classification.
- **No ordinary-cancel notification**: the cancel test asserts an empty notice collection before
  exercising the black-frame branch. The re-entrant guard returns before notification.
- **Bounded diagnostics**: stderr storage remains capped and the whitespace-collapsed user tail is
  capped at `PICKER_REASON_STDERR_BYTES`; no new unbounded retained string was introduced.
- **Existing-test immutability**: exact comparison against the round-1 snapshots
  `C:/Temp/av-kit/review-capture-lifecycle-tests.txt` and
  `C:/Temp/av-kit/review-capture-interactive-tests.txt` found only new-test imports, formatter-only
  layout, path-collector type widening, and the local optional `Notice.path` alias. No existing
  assertion, expected value, or matcher changed.
- **D1 wording corrected**: the handoff now matches `RegionForm`'s `TopMost`, `SetWindowPos`,
  `BringWindowToTop`, and best-effort `SetForegroundWindow` implementation
  (`native/region-picker/RegionForm.cs:24-29`, `:59-95`).
- **IR-5**: `capture-lifecycle.test.ts` is **Strong** for the three corrections; the assertions bind
  lifecycle calls, disk state, diagnostic content, and parser state. The unchanged
  `capture-interactive.test.ts` remains **Strong** for request lifecycle behavior.

### Verification Evidence

| Check | Result | Receipt |
|-------|--------|---------|
| Round-1 snapshot comparison | Fixture/type and formatter changes only in existing test bodies; no assertion/matcher change | `C:/Temp/av-kit/r2-review-lifecycle-fc.txt`; `C:/Temp/av-kit/r2-review-interactive-fc.txt` |
| Pre-fix mutation evidence | `6 failed, 30 passed`; each new correction test red | `C:/Temp/av-kit/r2-red-vitest.txt` |
| Independent focused rerun | `36 passed` | `C:/Temp/av-kit/r2-review-vitest-rerun-registered.txt` |
| Independent full UI unit rerun | `329 passed` in 40 files | `C:/Temp/av-kit/r2-review-vitest-all-rerun.txt` |
| Independent typecheck and lint | exit 0 for both | `C:/Temp/av-kit/r2-review-typecheck-rerun.txt`; `C:/Temp/av-kit/r2-review-lint-rerun.txt` |
| E2E report freshness | Report is newer than arm stamp; gate reports 4 expected, 0 skipped/unexpected/flaky | `C:/Temp/av-kit/r2-review-e2e-freshness.txt`; `C:/Temp/av-kit/e2e-capture-results.json` |
| E2E launched-bundle freshness | **Fail**: bundle predates corrections and contains the old implementations | `C:/Temp/av-kit/r2-review-e2e-build-freshness.txt`; `C:/Temp/av-kit/r2-review-e2e-stale-bundle-lines.txt` |

One initial direct `npm exec vitest` attempt bypassed the package's configured Electron test stub
and failed during setup (`C:/Temp/av-kit/r2-review-vitest-rerun.txt`); it is excluded from product
evidence. The registered `npm --prefix ui run test -- ...` command then passed.

### Open Questions / Assumptions

None. The stale launched bundle is directly observable; no inference from repository history is
required.

### Verdict

`changes_required` — all three round-1 findings are closed in source and unit tests, but the
claimed round-2 real-Electron rerun used a bundle that still contains those three defects. Rebuild
the Electron output and rerun the armed evidence before approval.

**Residual risk**: no new source-level regression was found in the corrections. The remaining risk
is that the corrected main-process code has not yet been exercised by the recorded real-Electron
run.

---

## Round 3 Recheck (2026-09-02)

**Intent anchor**: This recheck is limited to R2-1 and the round-3 freshness change. The native
pixel path, overlay deletion, unit-test foundations, packaging proof, D1-D14, and the three
round-1 source corrections remain closed.

### Findings

None.

### R2-1 Disposition

| Finding | Status | Recheck evidence |
|---------|--------|------------------|
| R2-1 — fresh report launched a stale Electron-main bundle | **closed** | The current bundle is newer than every file under `ui/src` and contains all three round-2 behaviors: the bounded parser state (`pendingLineBytes`), stderr-enriched blocked reason (`helper said:`) plus user notification, and the committed post-publication catch (`post-publication step failed`) (`ui/out/main/index.js:1163-1168`, `:1281-1288`, `:1373-1419`, `:1431-1437`). The captured run started after that bundle was built: source `2026-09-02T11:45:04.6907879Z` < bundle `11:54:18.0661985Z` < report start `11:54:22.853Z`; its JSON reports 4 expected, 0 unexpected, 0 skipped, and 0 flaky. |

### Guard and Failure-Mode Review

- **Fail-closed behavior is real**: `global-setup.ts` recursively stats files, not the source
  directory, and throws before Playwright when the newest source outruns the bundle
  (`ui/tests/e2e/global-setup.ts:13-24`, `:27-42`). The negative oracle reached that exact throw
  after `capture-picker.ts` was touched and returned `PASS: STALE_BUNDLE_REJECTED exit=1`.
- **Paths resolve correctly**: the oracle names
  `P:\av-kit\ui\src\main\capture-picker.ts` and the E2E launches
  `P:\av-kit\ui\out\main\index.js`; this matches the source-relative resolutions and the launch
  argument (`ui/tests/e2e/capture-picker.test.ts:169-176`).
- **Current source boundary is sufficient for R2-1**: the Electron-main local import graph has no
  runtime source outside `ui/src`; package imports are externalized. Build configuration and
  dependency metadata live outside that tree, but the canonical round-3 driver unconditionally
  runs `npm --prefix ui run build` before arming, so those inputs and an intentionally
  mtime-preserved source edit are rebuilt rather than trusted by the timestamp guard.
- **Reversion behavior**: an ordinary revert of any round-2 source correction advances its mtime
  and makes global setup reject the stale bundle. Rebuilding such a revert updates the bundle,
  while the already-accepted round-2 unit tests remain the branch-specific red oracles. The
  real-Electron cases establish that the corrected bundle launches and completes the production
  chain; they are not substitutes for those failure-branch unit tests.
- **No legitimate-run wedge found**: a normal full build rewrites `out/main/index.js` after all
  current sources. A deliberately future-dated source could conservatively block until its mtime
  is normalized, but that is clock/metadata corruption rather than a false green or a product
  regression, and the error identifies the exact file to repair.

### Verification Evidence

| Check | Result | Receipt |
|-------|--------|---------|
| Stale-bundle negative oracle | Rejected before Playwright; exit 1 | `C:/Temp/av-kit/r3-stale-bundle-oracle.txt`; `C:/Temp/av-kit/r3-stale-oracle-driver.txt` |
| Current source/bundle/report ordering | source < bundle < capture start; JSON 4 expected, 0 unexpected/skipped/flaky | `C:/Temp/av-kit/reviewer-r3-ordering.txt`; `C:/Temp/av-kit/e2e-capture-results.json` |
| Bundle behavior inspection | All three round-2 behavior markers present in executable main bundle | `C:/Temp/av-kit/review-r3-bundle-behaviors.txt` |
| Independent targeted real-Electron rerun | `4 passed` | `C:/Temp/av-kit/reviewer-r3-capture-e2e.txt` |
| Full recorded Playwright suite | `59 passed` | `C:/Temp/av-kit/ui-e2e.txt` |
| Independent typecheck | exit 0 | `C:/Temp/av-kit/reviewer-r3-typecheck.txt` |
| Independent lint | exit 0, no warnings | `C:/Temp/av-kit/reviewer-r3-lint.txt` |

### Open Questions / Assumptions

None.

### Verdict

`approved` — R2-1 is closed. The rebuilt bundle contains the three accepted round-2 corrections,
the re-armed real-Electron evidence was produced against that bundle, the freshness guard rejects
the stale-source case it was added to prevent, and the round-3 harness change is clean under the
targeted Electron rerun, the recorded 59-test full suite, typecheck, and lint.

**Residual risk**: the structural check is timestamp-based rather than content-addressed. The
canonical runner's unconditional rebuild closes that gap for the reviewed workflow; deliberate
mtime preservation combined with bypassing that runner is outside the ordinary evidence path.
