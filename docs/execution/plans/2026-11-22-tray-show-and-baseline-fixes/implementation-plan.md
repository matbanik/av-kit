---
project: "2026-11-22-tray-show-and-baseline-fixes"
date: "2026-11-22"
source: "Mat's request, 2026-11-22 (USER_EXPLICIT): 'add an issue where if icon in system tray is double clicked the \"Show window\" action needs to be executed. Than proceed with you recommendations'; registered as TRAY-DOUBLE-CLICK-NO-SHOW (triage D-1363) and MEU-164 in docs/build-plan/09-screenshot-capture.md §Tray double-click; the session also carries TEST-CAPTURE-SRGB-ICC-TIMESTAMP-FLAKE (D-1361) and TOOLING-PLAN-SLUG-ANCESTOR-MATCH (D-1362) (grouping D-1364)"
meus: ["MEU-164"]
status: "draft"
template_version: "2.3"
---

# Implementation Plan: a tray double-click runs Show window, and the two baseline pytest failures fixed

> **Project**: `2026-11-22-tray-show-and-baseline-fixes`
> **Build Plan Section(s)**: 09 §Tray double-click (`docs/build-plan/09-screenshot-capture.md`, anchor `tray-double-click`), matrix 9.47, registered at triage. Parent canon: 09 §Electron OS surface (main process), tray row. The two TECH-DEBT rows have no build-plan home, as for other register debt.
> **Status**: `draft`. `plan_to_exec_gate: human`. Mat's 2026-11-22 request ("Than proceed with you recommendations"), read with his 2026-11-18 hand-over ('make the decisions always the recommenations') and the grouping's D-1364 ("Run now through plan, execution and both Codex reviews"), is the execution approval once the Codex plan review approves and no stop item is open (precedent D-1351). The plan review approved at round 2 of loop `tsb-plan-2026-11-22-tray-show-and-baseline-fixes` with no findings open (2026-11-22; F1 to F3 fixed), and no stop item is open, so execution is approved. Its one wording note is applied as D-1369. Nothing commits or pushes without Mat's words.

---

## Goal

**Goal anchor:** a double-click on the av-kit tray icon brings the main window back, exactly as the tray menu's **Show window** item does: one show function, shared by the menu item and a new `double-click` listener, restores the window if it is minimized, shows it and focuses it. The tray menu keeps its four items in order, and a single click and a right-click behave as today. Vitest and an Electron E2E on the dev PC prove it, with no manual check. The same session fixes the two pytest failures that Session 101's gate had to deselect by name: AC-130.10 compares the two ICC profiles with the header's creation date and time masked, and `plan_slug` in `tools/validate_closeout_artifacts.py` reads the slug from the plan's own folder only, so a dated TEMP folder can no longer supply one. After this session, the full pytest run passes with nothing deselected.

**Why.**

- **Mat, 2026-11-22:** "add an issue where if icon in system tray is double clicked the "Show window" action needs to be executed. Than proceed with you recommendations".
- After close-to-tray, the window comes back only through the right-click menu. Double-click to reopen is the usual Windows tray behaviour.
- **The two debt rows.** Session 101's gate passed only with two `--deselect` arguments (D-1360). The triage of 2026-11-22 registered both failures with a reproduction (`C:/Temp/av-kit/2026-11-22-triage/repro.txt`) and recommended fixing them before the next gate.
- **Mat, 2026-11-16:** "This should be done with framework and scripts!" So the proof is tests in the gate.

**What the code shows (plan-time reads at `HEAD` `7f34348`, one worktree):**

- **The tray.** `ui/src/main/capture-tray.ts` (LF, 49 lines) `startCaptureTray(opts: { window, onRegion, inboxDir }): Tray` builds `new Tray(trayIconImage())`, sets the tooltip, builds a four-item menu (Show window: `opts.window.show(); opts.window.focus()`; Capture region; Open inbox folder; Quit), calls `tray.setContextMenu(menu)` and `registerNotifyTray(tray)`, and returns the tray. It registers no tray event. A grep of `ui/src` finds no `double-click` listener anywhere.
- **Where it starts.** `ui/src/main/index.ts:594` calls `startCaptureTray({ window, … })` in `boot()`, after the first renderer load, in every launch, an E2E launch included.
- **The restore precedent.** The `second-instance` handler (`index.ts:104-113`) restores a minimized window before it focuses it. Today's Show window item does not restore, so on a minimized window it focuses the taskbar entry but leaves the window minimized.
- **The Vitest stub.** `ui/vitest.config.ts` aliases `electron` to `ui/tests/unit/helpers/electron-stub.ts`, which exports no `Tray` and no `Menu`, and `trayIconImage` calls `image.resize`, which the stub's image lacks. A plan-time probe (`plan-vitest-probe.txt`) mocked `electron` (the stub plus fake `Tray` and `Menu`) and `../../src/main/app-icon` in one scratch test file, called `startCaptureTray` and passed: one tray, the four labels in order, the built menu set as the context menu, no `double-click` listener, and the menu item calling `show` then `focus` on a minimized window, with no `restore`. The scratch file was deleted.
- **The E2E hook precedent.** `ui/src/main/e2e-shell.ts` exposes `globalThis.__AVKIT_E2E_SHELL_LOG__` only when `process.env.AVKIT_E2E === '1'`, and Playwright reads it through `app.evaluate`. `ui/tests/e2e/electron-env.ts:40` sets `AVKIT_E2E = '1'` for every E2E launch. No E2E spec can reach the tray today, because Electron has no API that lists trays.
- **The source-text pins on `capture-tray.ts`** (all keep passing unchanged): `app-icon.test.ts:41` (`new Tray(trayIconImage())`, no `nativeImage.createEmpty()`), `capture-main.behavior.test.ts:128` (`showItemInFolder`, no `openPath`, "Open inbox folder"), `capture-page.test.ts:385` and `:557` (the `TRAY_MENU` labels, `/Tray/`, `/isQuitting|QUIT_INTENT/`, `/app\.quit/`, no `desktopCapturer`) and `login-item-ipc.test.ts:97` (`/opts\.window\.show\(\)/` in the tray source; `index.ts` must not match `/window\.show\(/`).
- **The ICC failure.** `tests/unit/test_capture_adapter.py` (CRLF) `test_ac_130_10_cmyk_icc_to_srgb` builds `srgb = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB"))` and later asserts `cropped.info.get("icc_profile") == srgb.tobytes()`. LittleCMS stamps the creation time into the header when a profile is built, and the adapter builds its own sRGB profile. When the two builds fall in different seconds, the bytes differ. The triage reproduction built two sRGB profiles 1.1 s apart: only byte 35 differed, inside header bytes 24 to 35, the creation date and time (ICC.1 §7.2.1). No profile ID is computed, so nothing else in the header follows the time.
- **The slug failure.** `tools/validate_closeout_artifacts.py` (CRLF) `plan_slug` (`:290-303`) walks every folder of the path from the leaf up and returns the first that matches `PLAN_SLUG` (`:94`). The selftest arm `unslugged-plan-path-is-usage` (`:2847`) writes `loose-plan.md` into `tempfile.mkdtemp(prefix="closeout-selftest-")` (`:2581`) and expects USAGE. Under a dated TEMP such as `C:/Temp/av-kit/2026-11-21-…/tmp`, the walk finds the dated folder, so the arm gets REFUSE and the selftest exits 1 (triage `repro.txt`: exit 1 under a dated TEMP, exit 0 under a plain one). `plan_slug` has one caller, `check_handoff_binding` (`:309`). Every real plan path ends `docs/execution/plans/<slug>/implementation-plan.md`, and every selftest plan sits directly in a slug folder (`:2823-2827`). `tests/tooling/test_framework_adoption.py:242` runs the selftest.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and ui/graphify-out/ are absent (2026-11-22). The change is one 49-line main-process module, one test helper, one tooling function, new test files and docs, all read at plan time; a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host. See `.agent/docs/harness-profiles.md` and the Claude Code block of `.agent/context/harness.local.md`.
  - Validation goes through `rtk proxy` with the receipt pattern. Task-cell commands run in pwsh.
  - Receipts go to `C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes/`. Execution receipts start `tsb-`; planning receipts start `tsb99-` or `plan-`.
  - Every row sets `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`, and clears `ELECTRON_RUN_AS_NODE`.
  - Vitest runs from pwsh after `Set-Location 'P:\av-kit\ui'`, never from the Bash tool, and returns to `P:\av-kit`.
  - `TMP` and `TEMP` are set to the undated `C:/Temp/av-kit/s102-tmp` for every Electron and pytest step, so no step depends on the slug fix it is proving. AC-164.9 builds its own dated TEMP. Each Electron launch uses a scratch `AVKIT_APP_DATA` under that folder. No row stops a process by image name.
  - Before each Electron step, the host-load probe must read 50 % or less. A receipt that holds `unhandled rejection:` is a failure.
- **Working directory:** `P:/av-kit` on `main`. Use no branch and no worktree. Leave `.agent/fleet/hub` alone.
- **Cloud-local contract:** local, because the work runs Electron. The new E2E spec uses no clipboard, so it runs on the dev PC.
- **Reviewer:** Codex runs through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `tsb-plan-2026-11-22-tray-show-and-baseline-fixes` and `tsb-execution-2026-11-22-tray-show-and-baseline-fixes`.
  - Caps come from `.agent/review-limits.json`: 3 plan rounds and 6 execution rounds. This plan carries no `review_limits` block.
  - Claude wrote the plan, so the reviewer is from a different vendor. The fallback is Mat.
  - The dispatch console goes to its own console file, never into the run log.
- **Never in these rows without Mat's words:** commit, push, or writing an `approved` verdict. Mat pushes himself.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-164 Tray double-click, and the two debt rows | `.agent/context/handoffs/2026-11-22-tray-show-and-baseline-fixes-MEU-164-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-22-tray-show-and-baseline-fixes-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-22-tray-show-and-baseline-fixes-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline and plan-local scripts (row 0) | — | shared | `baseline.sha`, `baseline-scope.json`, `baseline-eol.json`, `baseline-pins.json`, `red-check.py`, `identity.py`, `eol-check.py`, `host-wait.py`, `row-check.py` |
| WP-2 | Debt Red (row 1) | WP-1 | shared | The AC-164.8 tests and helper in its Red form; AC-130.10's one comparison; `test_closeout_plan_slug.py`; the Red hashes |
| WP-3 | Debt Green (row 2) | WP-2 | shared | The helper's Green body; `plan_slug` |
| WP-4 | Tray Reds (rows 3 and 4) | WP-3 | shared | `capture-tray.test.ts`, `tray-double-click.test.ts`, the Red hashes |
| WP-5 | Tray Green (row 5) | WP-4 | shared | `capture-tray.ts` per `TRAY_SHOW_SHARED` and `TRAY_E2E_HOOK` |
| WP-6 | Electron proof (row 6) | WP-5 | shared | The run receipts |
| WP-7 | Canon, register and status (row 7) | WP-6 | shared | The 09 tray row and Delivered note, the three issues resolved, MEU-164 `ready_for_review` |
| WP-8 | Closeout (H1, H2) | WP-7 | `compact_continue` | The handoff, the review, the reflection, the commit draft |

## User Review Required

> [!IMPORTANT]
> **No question is open for Mat.** D-1365 to D-1368 are reversible agent choices made under Mat's 2026-11-18 hand-over, each with its do-nothing option in §Decision Log. D-1367 changes one existing assertion (AC-130.10's profile comparison), an M-7 item decided under the hand-over and disclosed here.
>
> **What changes for you:**
>
> - A double-click on the av-kit tray icon brings the window back, the same as right-click → Show window.
> - If the window is minimized, both the double-click and the Show window item now restore it. Today the menu item leaves a minimized window minimized. This matches what a second launch of av-kit already does.
> - The tray menu, a single click and a right-click are unchanged.
> - The full pytest run no longer needs the two tests deselected. AC-130.10 no longer fails when a second boundary falls between two profile builds, and the closeout validator's selftest passes under any TEMP folder.

## Proposed Changes

### Single-statement contracts

- **`TRAY_SHOW_SHARED`.** Inside `startCaptureTray`, before the menu is built, `const showWindow = (): void => { if (opts.window.isMinimized()) { opts.window.restore() } opts.window.show(); opts.window.focus() }`. The Show window item's template entry is `{ label: 'Show window', click: showWindow }`. After `tray.setContextMenu(menu)`, `tray.on('double-click', showWindow)` is the only tray event listener the module registers. The other three items, their order, the tooltip, `registerNotifyTray(tray)` and the return value do not change. The literal `opts.window.show()` stays in the file once (`login-item-ipc.test.ts:97`).
- **`TRAY_E2E_HOOK`.** Right after the `tray.on('double-click', showWindow)` line, `if (process.env.AVKIT_E2E === '1') { (globalThis as { __AVKIT_E2E_TRAY__?: { tray: Tray; menu: Menu } }).__AVKIT_E2E_TRAY__ = { tray, menu } }`, with a one-line comment in the shape of `e2e-shell.ts` ("Playwright drives the tray through app.evaluate. Only a launch with AVKIT_E2E=1 exposes it."). Without `AVKIT_E2E=1` nothing is exposed. The flag is read at run time, as `e2e-shell.ts` does; the hook is a main-process global, not a renderer, preload or IPC surface. `Menu` joins the existing `import { … } from 'electron'` as a type.
- **`ICC_HEADER_MASK`.** `tests/unit/test_capture_adapter.py` gains, just before AC-130.10's first decorator (the line `@pytest.mark.parametrize("ac_id", ["AC-130.10"], ids=["AC-130.10"])`, so both of AC-130.10's decorators stay on it), the module helper `_same_icc_ignoring_creation(a: bytes | None, b: bytes | None) -> bool`, documented as "the ICC header's creation date and time, bytes 24 to 35 (ICC.1 §7.2.1), are ignored". Both forms first return False when either is None, when the lengths differ or when either is shorter than the 128-byte header. Then the Green form returns `a[:24] + a[36:] == b[:24] + b[36:]`, and the Red form (row 1) returns `a == b`, which is today's comparison. So the guard passes at Red and at Green. AC-130.10's one line `assert cropped.info.get("icc_profile") == srgb.tobytes()` becomes `assert _same_icc_ignoring_creation(cropped.info.get("icc_profile"), srgb.tobytes())`; every other line of AC-130.10 stays.
- **`PLAN_SLUG_PARENT_ONLY`.** In `plan_slug`, the walk over every folder becomes one check: `folder = parts[-2] if parts[-1].endswith(".md") and len(parts) > 1 else parts[-1]`, and `PLAN_SLUG.fullmatch(folder)` gives the slug or the existing `Usage` message, word for word. The docstring gains one sentence: "Only the plan's own folder counts, so a dated ancestor (a dated TEMP, say) names no plan." Nothing else in the file changes, and it stays CRLF.

### MEU-164: Tray double-click

1. **Tray.** Apply `TRAY_SHOW_SHARED` and `TRAY_E2E_HOOK` to `ui/src/main/capture-tray.ts` (LF).
2. **Canon.** In 09 §Electron OS surface, the tray row's rule becomes "Always created while the app runs. Menu: Show window, Capture region, Open inbox folder, Quit. A double-click on the icon runs Show window (MEU-164)". §Tray double-click gains a `> **Delivered (Session 102).**` note naming the shared function, the restore, the hook, the tests and D-1365 to D-1368 (row 7, `canon-edit.py`, CRLF).

### Debt rows

1. **ICC.** Apply `ICC_HEADER_MASK` (row 1 the Red form and AC-130.10's line; row 2 the Green body).
2. **Slug.** Apply `PLAN_SLUG_PARENT_ONLY` (row 2).

### Test pins

Row 0 records each pin file's SHA-256 in `baseline-pins.json`, and the gate checks that each one is unchanged.

| Pin | What it checks | After this change |
|---|---|---|
| `ui/tests/unit/app-icon.test.ts` | `new Tray(trayIconImage())`; no empty image | Unchanged; passes |
| `ui/tests/unit/capture-main.behavior.test.ts` | Open inbox folder uses `showItemInFolder` | Unchanged; passes |
| `ui/tests/unit/capture-page.test.ts` | The four tray labels; Tray; quit intent; `app.quit` | Unchanged; passes |
| `ui/tests/unit/login-item-ipc.test.ts` | `opts.window.show()` in the tray; `index.ts` never shows the window itself | Unchanged; passes. `index.ts` is not edited |
| `ui/tests/e2e/startup-reveal.test.ts` | The window is revealed at launch | Unchanged; runs once in row 6 and in the gate (the launch watch of `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG`) |
| `tests/unit/test_capture_adapter.py`, every top-level node except AC-130.10 | The capture adapter | Row 0 records the source text of every top-level node, read with `ast`. Only AC-130.10 changes (its one line), and only `_same_icc_ignoring_creation` and the two `test_ac_164_8_` tests are new (`row-check.py named-edits`) |
| `tools/validate_closeout_artifacts.py`, every top-level node except `plan_slug` | The closeout validator and its selftest | Row 0 records each node's source; only `plan_slug` changes (`row-check.py slug-edit`) |
| `tests/tooling/test_framework_adoption.py` | `test_evidence_contract_real_cli_selftests`, the selftest run | Unchanged; passes in the gate with no deselect |

Any other existing test that fails after a Green is S5: an M-7 question, not a fix.

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| Tray icon events | `capture-tray.ts` | `double-click` → `showWindow`; no other listener | — |
| `globalThis.__AVKIT_E2E_TRAY__` | `TRAY_E2E_HOOK` | Set only when `AVKIT_E2E === '1'`; `{ tray, menu }` | — |
| `validate_closeout_artifacts.py --plan` | `plan_slug` | The plan's own folder must match `PLAN_SLUG` | Unchanged: any other path is USAGE |

No API route, IPC channel, preload surface, OpenAPI document, MCP tool, setting or database schema changes. No user data is read or written.

### Acceptance Criteria

- **Family.** The session uses AC-164.1 to AC-164.9: the MEU's ACs and the two debt rows' ACs (AC-164.8 and AC-164.9) in one family, so the closeout coverage check binds all of them to the one handoff (D-1368). Vitest and Playwright titles start `AC-164.<n> ` with a space after. The pytest names start `test_ac_164_8_` and `test_ac_164_9_`.
- **New names fail by assertion at Red.** The Vitest file asserts `typeof listener === 'function'` before it calls the double-click listener. The E2E spec polls `app.evaluate` for the hook and asserts `toBe(true)` with the message `expect(tray hook)` (Playwright prints it as `Error: expect(tray hook)`, which `red-check.py` reads as an assertion line), so a missing hook is an assertion, never a TypeError. The slug test's `pytest.raises(v.Usage)` gives "DID NOT RAISE" at Red, which counts as an assertion.
- **Guards** pass at Red: `test_ac_164_8_icc_compare_sees_other_bytes` and `test_ac_164_9_plan_path_gives_its_slug`.

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-164.1 | unit | `ui/tests/unit/capture-tray.test.ts` mocks `electron` (the stub plus fake `Tray` and `Menu` that record listeners and the template) and `../../src/main/app-icon`. After `startCaptureTray`: one tray; the template's labels equal `['Show window', 'Capture region', 'Open inbox folder', 'Quit']`; the built menu is the context menu; exactly one `double-click` listener, and no other event; that listener is the same function object as the Show window item's `click` (`toBe`). | Human-approved (Mat 2026-11-22, D-1363); `TRAY_SHOW_SHARED` | At Red there is no listener: the count assertion fails |
| AC-164.2 | unit | Calling the shared function on a minimized window records `['restore', 'show', 'focus']`; on a window that is not minimized, `['show', 'focus']`. Neither call reaches `onRegion` or `shell.showItemInFolder`. | D-1365 | The not-minimized case is the negative: no `restore` |
| AC-164.3 | unit | With `AVKIT_E2E` unset, `startCaptureTray` leaves `globalThis.__AVKIT_E2E_TRAY__` undefined. With it `'1'`, the hook holds the created tray and the built menu. The test restores the variable and deletes the hook after each case. | `TRAY_E2E_HOOK`; D-1366 | The unset case |
| AC-164.4 | integration | `ui/tests/e2e/tray-double-click.test.ts` `AC-164.4 hidden`: launch with a scratch `AVKIT_APP_DATA`; wait for `app-shell`; poll (bounded, 10 s) until the hook exists, asserted with the message `expect(tray hook)`; hide the window and assert it is not visible; emit `double-click` on the hooked tray; poll until visible and focused. Hide it again; call the Show window menu item's `click()` through the hooked menu; poll until visible. | Human-approved (D-1363); D-1366 | The hidden state before each action |
| AC-164.5 | integration | `AC-164.5 minimized`: the same launch; minimize the window and poll until `isMinimized()`; emit `double-click`; poll until it is not minimized and is visible. | D-1365; D-1366 | The minimized state before the emit |
| AC-164.6 | check | The §Test pins pass with their row-0 hashes and node sources: the unit pins in row 5 and the gate, `startup-reveal.test.ts` in row 6 and the gate. | Local Canon | A failure is S5 |
| AC-164.7 | check | 09's tray row holds the text of Proposed Changes MEU-164 step 2, §Tray double-click holds the Delivered note, no other line of 09 changed, and it stays CRLF (`row-check.py canon`). | Local Canon (09 §Electron OS surface) | A missing or doubled line fails row 7 |
| AC-164.8 | unit (pytest) | `test_ac_164_8_icc_compare_ignores_creation_time`: with `base` the bytes of a fresh sRGB profile, `_same_icc_ignoring_creation(base, base)` is True, and so is each copy of `base` with one byte of 24 to 35 changed, and a copy with all twelve changed. `test_ac_164_8_icc_compare_sees_other_bytes` (guard): False for a copy with byte 23, byte 36 or byte 100 changed, for `base[:-1]`, for `None` on either side and for two equal 100-byte strings (shorter than a header). AC-130.10 passes through the helper. | TEST-CAPTURE-SRGB-ICC-TIMESTAMP-FLAKE (D-1361); D-1367 | The guard test; at Red the first test fails on its first changed-time copy |
| AC-164.9 | unit (pytest) | `tests/tooling/test_closeout_plan_slug.py`, importing the tool as `test_closeout_record_once.py` does. `test_ac_164_9_loose_plan_under_dated_ancestor_is_usage`: `v.plan_slug` of `C:/Temp/av-kit/2026-11-22-x/tmp/closeout-selftest-ab/loose-plan.md` raises `v.Usage` with "cannot derive a plan slug". `test_ac_164_9_plan_path_gives_its_slug` (guard): `docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes/implementation-plan.md` and the same folder without the file name both give `2026-11-22-tray-show-and-baseline-fixes`, and `loose-plan.md` alone raises `v.Usage`. `test_ac_164_9_selftest_under_dated_temp`: `tools/validate_closeout_artifacts.py --selftest`, run by `subprocess` with `sys.executable`, `TEMP` and `TMP` set to `tmp_path / "2026-11-22-dated-temp"` (created) and a 300 s timeout, exits 0. | TOOLING-PLAN-SLUG-ANCESTOR-MATCH (D-1362); D-1368 | The loose-plan cases; at Red the first and third tests fail (DID NOT RAISE; exit 1) |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| A tray double-click runs Show window | Human-approved | Mat 2026-11-22; D-1363 |
| One shared function | Local Canon | 09 §Tray double-click, One function row (D-1363) |
| Show window restores a minimized window | Agent decision | D-1365; precedent `index.ts:104-113` |
| How the tray is driven in Electron | Agent decision | D-1366 |
| AC-130.10's comparison | Agent decision (M-7) | D-1367 |
| `plan_slug` reads the plan's own folder | Agent decision | D-1368 |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/main/capture-tray.ts` | modify (LF) | `TRAY_SHOW_SHARED`, `TRAY_E2E_HOOK` |
| `ui/tests/unit/capture-tray.test.ts` | create (LF) | AC-164.1 to AC-164.3 |
| `ui/tests/e2e/tray-double-click.test.ts` | create (LF) | AC-164.4 and AC-164.5 |
| `tests/unit/test_capture_adapter.py` | modify (CRLF) | `ICC_HEADER_MASK`: the helper, the two AC-164.8 tests (right after AC-130.10), AC-130.10's one line |
| `tools/validate_closeout_artifacts.py` | modify (CRLF) | `PLAN_SLUG_PARENT_ONLY` |
| `tests/tooling/test_closeout_plan_slug.py` | create (LF) | AC-164.9 |
| `docs/build-plan/09-screenshot-capture.md` | modify (CRLF) | The tray row; the Delivered note |
| `.agent/context/known-issues.yaml`, `.agent/context/known-issues.md` | modify (CRLF) | The three issues resolved; the `.md` re-rendered |
| `.agent/context/meu-status.yaml`, `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md` | modify (LF) | MEU-164 status through `meu_status.py` |
| `.agent/context/grouping/2026-11-22-tray-show-and-baseline-fixes-session-grouping.md` | modify (LF) | §6 row 102 `executed (Session 102)` |
| `.agent/context/current-focus.md`, `docs/execution/metrics.md` | modify (CRLF) | Closeout |

The registration edits made before this plan (the grouping file, the three issues, MEU-164 in `meu-status.yaml`, `meu-registry.md`, `BUILD_PLAN.md`, 09's residual section and MEU row, matrix row 9.47 in `build-priority-matrix.md`, `triage-output.yaml`) are this session's own work. Row 0 lists them in `baseline-dirty.txt`, and they are committed with it.

### Project files

- **Plan-local scripts** live in this plan folder. Row 0 copies `baseline.ps1`, `red-check.py`, `identity.py`, `eol-check.py`, `host-wait.py`, `load-run.py` and `issue-resolve.py` from `2026-11-21-transcript-job-resume/`, and writes `row-check.py`. Row 7 writes `canon-edit.py`, which edits by bytes and refuses when a target line is not found exactly once. H1-2 writes `session-gate.ps1` from the Session 101 copy. `register-meu.py` and `link-issue.py` are the registration scripts already run.
- **Row 0 data:** `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-eol.json` and `baseline-pins.json`.
- **Read, never changed:** `ui/src/main/index.ts`, `ui/src/main/e2e-shell.ts`, `ui/src/main/app-icon.ts`, `ui/src/main/notify-user.ts`, `ui/tests/unit/helpers/electron-stub.ts`, `ui/vitest.config.ts`, `ui/tests/e2e/electron-app.ts`, `ui/tests/e2e/electron-env.ts`, `ui/tests/e2e/test-ids.ts`, `packages/infrastructure/src/avkit_infra/capture/adapter.py`, `tests/tooling/test_closeout_record_once.py` and the §Test pins files.
- **State:** `docs/execution/metrics.md` (CRLF), `.agent/context/current-focus.md` (CRLF), the handoff, the rolling reviews and the reflection.
- **New names (`DECLARED_NEW`):** `showWindow`, `__AVKIT_E2E_TRAY__`, `capture-tray.test`, `tray-double-click.test`, `_same_icc_ignoring_creation`, `test_closeout_plan_slug`.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| A single left click on the tray icon showing the window | out-of-scope | — | Mat asked for the double-click; 09 §Tray double-click Menu row keeps a single click as today |
| A Hide window item or a toggle on double-click | out-of-scope | — | Mat asked for Show window's action |
| Adding `Tray` and `Menu` to the shared Vitest stub | out-of-scope | — | D-1366: the new test mocks them itself; the stub serves about twenty files |
| Moving the `second-instance` handler onto the shared show function | out-of-scope | — | It lives in `index.ts`, whose pin forbids `window.show(` there (`login-item-ipc.test.ts:97`) |
| `TOOLING-RUFF-TOOLS-UNCLEAN` | out-of-scope | — | Grouping §1: its files are `issue_triage*` and `meu_status*` |
| Other tools that walk a path for a dated folder | out-of-scope | — | No failure reported; `plan_slug` is the one the selftest exercises |

## BUILD_PLAN.md Audit

MEU-164 (`gui-tray-double-click-show`, phase 9, matrix 9.47) was registered as `pending` at triage. Row 7 sets it to `ready_for_review` with this plan's `execution_plan`, and H2-2 sets it to `approved`, both through `tools/meu_status.py update`. `meu-registry.md` and `docs/BUILD_PLAN.md` are regenerated by `tools/meu_status.py render`, never by hand:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes/tsb-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes/tsb-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. Use `rtk proxy` for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` has the shape of `2026-11-21-transcript-job-resume/baseline.ps1`:

1. **Tree and host.** It prints `HEAD`, `git status --porcelain --untracked-files=all`, `git worktree list` and one host-load sample, and records `baseline.sha`, `baseline-dirty.txt` and `baseline-dirty-hashes.json`.
2. **Scope binding.** It records `baseline-scope.json`: the SHA-256 of each §Files Modified path and each "Read, never changed" path, or `absent`. Every new path must be `absent`. `current-focus.md`, `metrics.md` and `known-issues.yaml` and `.md` are recorded as `shared` with their hash, because another session may write them; the row that writes one re-reads it just before the edit. It also records `baseline-eol.json` and byte copies of the scope files under `C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes/baseline-copies/`.
3. **Pins.** `baseline-pins.json` holds the SHA-256 of each §Test pins file except `test_capture_adapter.py` and `validate_closeout_artifacts.py`. For those two it holds the source text, read with `ast`, of every top-level node, keyed by name.
4. **Citations.** It finds by text, once each, and records the current line of: `label: 'Show window',`, `opts.window.show()`, `tray.setContextMenu(menu)` and `registerNotifyTray(tray)` (`capture-tray.ts`); `startCaptureTray({` and `target.on('second-instance'` (`index.ts`); `shellGlobal.__AVKIT_E2E_SHELL_LOG__ = e2eShellLog` (`e2e-shell.ts`); `env.AVKIT_E2E = '1'` (`electron-env.ts`); `def test_ac_130_10_cmyk_icc_to_srgb` and `assert cropped.info.get("icc_profile") == srgb.tobytes()` (`test_capture_adapter.py`); `def plan_slug(`, `for part in reversed(parts[:-1] if parts[-1].endswith(".md") else parts):` and `"unslugged-plan-path-is-usage",` (`validate_closeout_artifacts.py`); and the 09 tray row `| Tray icon | Electron main | Always created while the app runs. Menu: Show window, Capture region, Open inbox folder, Quit |`. A missing or doubled anchor is S2; a moved line is recorded.
5. **Free ids.** Every `DECLARED_NEW` name and `AC-164.` occur nowhere in the tree outside this plan folder. D-1365 to D-1399 occur only in this plan folder and the grouping file.
6. **Base receipts.** The full Vitest suite (`tsb-base-ui.txt`) and the full pytest suite (`tsb-base-py.txt`, with `PYTHONIOENCODING=utf-8` and the undated TEMP). Their failures are recorded, not fatal. Under the undated TEMP the selftest arm passes, and AC-130.10 fails only when a second boundary falls between the two builds, so the expected base is 0 failed or AC-130.10 alone.
7. **Plan-local scripts.** It copies the scripts of §Project files with this plan's `PLAN`, receipts folder, artifacts and `DECLARED_NEW`. `red-check.py`'s fixtures use AC-164 (it must refuse `AC-164.1` matching `AC-164.10`). `row-check.py` has the subcommands `red-record --row N FILE…`, `red-unchanged` (every recorded file except `test_capture_adapter.py`, which `named-edits` checks by node), `pins-unchanged`, `red-reason RECEIPT --id ID --needle TEXT`, `e2e-count RECEIPT N [--plain RECEIPT…]`, `named-edits --stage red|green` (`ICC_HEADER_MASK`, by top-level `ast` node against `baseline-pins.json`: the changed or new nodes are exactly `_same_icc_ignoring_creation`, AC-130.10 and the two `test_ac_164_8_` tests; AC-130.10 differs from row 0 in its one comparison line only; the helper's source equals the Red or the Green form the script holds; the two new tests equal their row-1 source; the file stays CRLF), `slug-edit` (`PLAN_SLUG_PARENT_ONLY`: against `baseline-pins.json`, only `plan_slug` changed, its source equals the form the script holds, and the file stays CRLF), `canon` (AC-164.7) and `register` (by key with `yaml.safe_load`: every other issue in `known-issues.yaml` equals its row-0 copy, and the three issues differ only in `status`, `verification` and `resolution_path`; in the grouping file only §6 row 102 changed), each with a `--selftest`. It runs every selftest and `ruff format --check` and `ruff check` on the plan folder's Python.
8. **Secrets and the fleet hub.** The scope walk drops `.mcp.json`, `mcp-token.txt`, `.claude.json`, `.env`, `.claude/settings.local.json` and `.agent/fleet/hub` before any stat or read.

If any step except the base receipts fails, the row fails and nothing else runs.

### 2. Red, then Green

- **Debt first.** Row 1 is the debt Red and row 2 its Green, so the tray rows and the gate run a pytest suite that needs no deselect.
- **Every tray Red comes before the tray change.** Rows 3 and 4 change no product file. Row 4 builds the unchanged app.
- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py --require` names `test_ac_164_8_icc_compare_ignores_creation_time`, `test_ac_164_9_loose_plan_under_dated_ancestor_is_usage` and `test_ac_164_9_selftest_under_dated_temp` (row 1, pytest; "DID NOT RAISE" counts), AC-164.1 to AC-164.3 (row 3, Vitest), and AC-164.4 and AC-164.5 (row 4, Playwright). `row-check.py red-reason` requires `tray hook` in each failing E2E test's error block, so a launch failure is never a Red.
- **Expectations stay the same in Green** (S3). Rows 1, 3 and 4 record the hashes of the test-side files they write. Row 2 changes only the helper's body in `test_capture_adapter.py`, which `named-edits --stage green` checks node by node.
- **Line endings** are checked by `eol-check.py` after each Green.

### 3. Electron proof (row 6)

- `tray-double-click.test.ts` runs 3 times (`--repeat-each 3`): 6 `AC-164.` ok lines.
- `startup-reveal.test.ts` runs once (AC-164.6).
- `row-check.py e2e-count` requires the ok count and the `N passed` lines, and no `failed`, `flaky` or `unhandled rejection:` line.

### Session gate (H1-2)

`session-gate.ps1` has the shape of `2026-11-21-transcript-job-resume/session-gate.ps1`: one receipt per step, `tsb-D6-<step>`, fail-fast, later steps printed `not_run`, last line `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `ui-types`, `ui-lint` (pwsh in `ui/`); `py-types` (`uv run pyright packages/`); `py-lint` (`uv run ruff check packages/ tests/ tools/validate_closeout_artifacts.py`); `py-format` (`ruff format --check` on `tests/tooling/test_closeout_plan_slug.py` and this plan folder's Python); `task-contract`; `scope-paths`; `line-endings`; `home-path` (`tools/check_home_path.py`); `pins-unchanged`; `named-edits --stage green`; `slug-edit`; `canon`; `red-unchanged`; the selftests |
| Targeted | `py-debt` (`uv run pytest tests/tooling/test_closeout_plan_slug.py tests/unit/test_capture_adapter.py -k "ac_130_10 or ac_164"`); `closeout-selftest` (`tools/validate_closeout_artifacts.py --selftest` with `TEMP` and `TMP` set to `C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes/tmp-dated`, a dated path, on purpose); `ui-tray` (`capture-tray.test.ts` and the four unit pins) |
| Host load | `host-load` before every Electron step (limit 50 %) |
| Fresh full | `ui-tests` (full Vitest); `py-tests` (`uv run pytest tests/ -x --tb=short -q`, with `PYTHONIOENCODING=utf-8`, the undated TEMP and **no `--deselect`**); `ui-build`; `e2e-tray-double-click`; `e2e-startup-reveal`; `state-render` (`meu_status.py render --check`); `issues-render` (`issue_triage.py render --check`) |
| Skipped, with reason | The rest of `test:e2e`: only the tray module changed, and `startup-reveal` covers the launch and reveal. `mcp-server` tests and `openapi`: no MCP or API file changed |

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A `graphify-out` graph appears | Re-decide the context tool |
| S2 | Row 0 finds a citation anchor missing or doubled, or a free id taken | Stop and bring the receipt to Mat. A moved line is corrected, not a stop |
| S3 | A Red receipt fails `red-check.py` or `red-reason`, or a Green row needs a changed expectation | Fix the test setup; never edit an expectation in Green |
| S4 | A path outside this plan's scope and `baseline-dirty.txt` changes, or a scope path changes by another hand | Stop and re-baseline with Mat. Never commit, stash or revert another session's work |
| S5 | An existing test fails after a Green | Rerun it alone once. If it fails again, stop: an M-7 question, not a fix |
| S6 | Codex is unavailable or the ledger refuses | Mat |
| S7 | An Electron test fails in any of row 6's runs, or a receipt holds `unhandled rejection:`, or a launch or close hangs (`CAPTURE-E2E-LAUNCH-TEARDOWN-HANG`) | Stop and bring the receipts to Mat. Never raise a timeout or add a retry |
| S8 | The hook is set but `double-click` emitted from the main process does not run the listener | Stop and route back to the plan (D-1366) |

## Decision Log

> [!NOTE]
> D-1365 to D-1368 are autonomous, with `mandatory: none` except D-1367, made under Mat's hand-over (USER_EXPLICIT 2026-11-18: 'make the decisions always the recommenations'). Each passed the §4a list and the §4 test. D-1361 to D-1363 (triage) and D-1364 (grouping) are read from `known-issues.yaml` and the grouping file. The M items:
>
> - **M-4 clear.** No API route, body, OpenAPI document, IPC channel or MCP tool changes. The E2E hook exists only in a launch with `AVKIT_E2E=1`; it is a main-process global, not an IPC surface (D-1369).
> - **M-2 clear.** No user data is read or written. Every Electron launch uses scratch app data.
> - **M-7.** One existing assertion changes: AC-130.10's profile comparison (D-1367). No other assertion changes.
>
> Execution decisions take D-1369 to D-1399.

```yaml
decision_log:
  - id: D-1365
    stage: planning
    question: "What does the shared show function do with a minimized window?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: restore it if minimized, then show and focus (TRAY_SHOW_SHARED); the Show window menu item uses the same function, so it restores too."
    source_tag: Local Canon
    precedents:
      - "ui/src/main/index.ts:104-113 — the second-instance handler restores a minimized window before it focuses it"
      - "docs/build-plan/09-screenshot-capture.md §Tray double-click — One function row: the menu item and the listener share one function (D-1363)"
      - "C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes/plan-vitest-probe.txt — today's menu item calls show and focus on a minimized window, with no restore"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) restore, show, focus; (B) do nothing beyond sharing today's show and focus. On Windows, show() and focus() on a minimized window leave it minimized, so with B a double-click on the icon of a minimized av-kit would do nothing visible, which is the complaint Mat raised. A matches what a second launch already does. Weakness of A: the menu item's behaviour changes for a minimized window; it now restores it, which is disclosed in User Review Required. Two-way: one if statement."
  - id: D-1366
    stage: planning
    question: "How are the shared function and the double-click proved?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: a Vitest file that mocks electron itself (the stub plus fake Tray and Menu) for the listener, the shared function and the hook; and an Electron E2E spec that reaches the real tray through an E2E-only globalThis hook (TRAY_E2E_HOOK) and emits double-click from the main process, for a hidden and a minimized window, plus the menu item's click."
    source_tag: Local Canon
    precedents:
      - "ui/src/main/e2e-shell.ts — the E2E-only globalThis hook read through app.evaluate"
      - "C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes/plan-vitest-probe.txt — the per-file electron mock drives startCaptureTray"
      - "Mat 2026-11-16: 'This should be done with framework and scripts!'"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) unit plus E2E through a hook; (B) add Tray and Menu to the shared Vitest stub; (C) drive a real OS double-click on the notification area by screen automation; (D) unit tests only; (E) do nothing beyond a manual check by Mat. A proves the wiring on the real Electron Tray and the real window states, and keeps the shared stub that about twenty files use unchanged. B widens a shared file for one test. C depends on where Windows places the icon, which the host decides, and is flaky by nature. D never runs a real window. E is the manual check Mat ruled out. Weakness of A: the emit stands in for the OS's own double-click, so Electron's native event wiring is trusted, not tested."
  - id: D-1367
    stage: planning
    question: "How does AC-130.10 stop failing when the two sRGB profiles are built in different seconds?"
    resolution: autonomous
    class: two-way
    mandatory: [M-7]
    chosen: "A: compare the two profiles with the header's creation date and time (bytes 24 to 35) masked, through a helper that requires equal lengths, a full header and every other byte equal (ICC_HEADER_MASK); the helper's own tests prove both halves."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/2026-11-22-triage/repro.txt — two sRGB builds 1.1 s apart differ only in byte 35, inside header bytes 24 to 35"
      - "TEST-CAPTURE-SRGB-ICC-TIMESTAMP-FLAKE (triage D-1361) — the comparison with the time masked"
      - "ICC.1 §7.2.1 — header bytes 24 to 35 are the profile's creation date and time"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) mask the 12 time bytes; (B) compare parsed profile fields such as the description and colour space; (C) freeze LittleCMS's clock; (D) do nothing, so every gate deselects AC-130.10 by name. A keeps the strongest check, every other byte equal, and the helper's guard proves a change outside the time still fails. B is weaker: two different RGB profiles can share a description. C is not possible from Python: LittleCMS reads the system clock. D hides a real check. M-7: one assertion line changes, and its strength is kept apart from the 12 time bytes. Two-way."
  - id: D-1368
    stage: planning
    question: "How does plan_slug stop taking a slug from a dated ancestor, and how is the session's AC family named?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: plan_slug checks only the plan's own folder (PLAN_SLUG_PARENT_ONLY), proved by a pytest file that runs the selftest under a dated TEMP; the two debt rows' ACs are AC-164.8 and AC-164.9 in the MEU's family."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/2026-11-22-triage/repro.txt — the selftest exits 1 under a dated TEMP and 0 under a plain one"
      - "tools/validate_closeout_artifacts.py:2823-2827 — every selftest plan sits directly in a slug folder"
      - "tools/validate_closeout_artifacts.py:76 — AC_ID binds plan and handoff ACs by their number before the dot"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options for the fix: (A) the parent folder only; (B) require the slug folder to sit under docs/execution/plans/; (C) make the selftest create its own undated temp root; (D) do nothing, so every gate run under a dated TEMP deselects the selftest. A is the rule the docstring already states (the plan's own folder identifies it) and every real and selftest plan path meets it. B refuses plan copies a reviewer or a test makes outside the tree. C fixes the selftest, but the validator would still bind a loose plan to a dated folder in real use. D hides a real defect. For the AC family: one family lets --ac-coverage-only bind every AC to the one handoff, where a separate family would need a second handoff. Two-way."
  - id: D-1369
    stage: execution
    question: "How does the M-4 note describe where the E2E hook exists?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: the M-4 note and the tray-start fact say the hook exists only in a launch with AVKIT_E2E=1, as the plan review's round 2 note asked; there is no separate E2E build."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/tsb-plan-review-round-2.md — the M-4 introduction still said 'only in the E2E build'"
      - "ui/src/main/e2e-shell.ts — the E2E surface reads AVKIT_E2E at run time"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) apply the reviewer's wording; (B) do nothing and keep 'only in the E2E build'. B leaves a sentence that contradicts TRAY_E2E_HOOK. The reviewer approved with no further round, and no contract changes."
  - id: D-1370
    stage: execution
    question: "Does a D-1365..D-1399 match that only closes another session's claimed range count as a use in the row-0 free-id check?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: a match preceded by 'to ' or '..' is the upper end of another session's claimed range and is printed as a range end, not a use; every other match outside this session's files stays S2."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-21-transcript-job-resume-session-grouping.md:12 and :85 — 'claims D-1350 to D-1399', 'D-1352 to D-1399'"
      - "docs/execution/plans/2026-11-21-transcript-job-resume/ (baseline.ps1, implementation-plan.md, task.md) — 'D-1358 to D-1399', Session 101's range statement"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) skip only range-end matches; (B) list each Session 101 line as an exception; (C) count every match, so row 0 fails on text that uses no id. B breaks on the next session that states a range; C blocks a sound baseline. A still catches any real use, including one on the same line as a range end, since a line counts as a use whenever it holds more matches than range ends."
open_decisions: []
```

## Research References

- None outside the repository, except the ICC header layout (ICC.1 §7.2.1), already cited by the triage entry D-1361.

## Planning receipts

All under `C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes/`, read-only against the repository, unless named otherwise:

| Receipt | What it shows |
|---|---|
| `plan-vitest-probe.txt` | A scratch Vitest file (deleted afterwards) with `electron` and `app-icon` mocked: one tray, the four labels in order, the menu set, no `double-click` listener, the menu item calling `show` and `focus` with no `restore`; 1 passed |
| `C:/Temp/av-kit/2026-11-22-triage/repro.txt` | Two sRGB builds 1.1 s apart differ only in byte 35; the closeout selftest exits 1 under a dated TEMP (`unslugged-plan-path-is-usage` got REFUSE) and 0 under a plain one |
| `register-meu.txt`, `link-issue.txt` | MEU-164 registered (164 MEUs, LF), 09 and the matrix kept CRLF; the issue linked to MEU-164 |
| `tsb99-task-lint.txt` | `tools/lint_task_contract.py` on `task.md` |

## Validation stage contract

| Stage | Checks | Where |
|---|---|---|
| Plan review | This plan and `task.md`, against Mat's request, 09 §Tray double-click, 09 §Electron OS surface, the two debt issues and the code reads above | `tsb-plan-2026-11-22-tray-show-and-baseline-fixes` |
| Row checks | Each row's validation command | `task.md` |
| Session gate | §Session gate | H1-2 |
| Execution review | The delta from `baseline.sha` in the §Files Modified paths, against AC-164.1 to AC-164.9 | `tsb-execution-2026-11-22-tray-show-and-baseline-fixes` |
