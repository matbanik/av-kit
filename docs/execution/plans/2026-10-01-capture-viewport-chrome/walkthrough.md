# Walkthrough — 2026-10-01-capture-viewport-chrome (Session 29)

**Receipts.** `$RECEIPTS_DIR` is `/tmp/av-kit` in the container. Receipt names follow `validate-task.sh` (`s29-*`).

## Execution authorization and prerequisites (row 0)

- **Authorization:** `USER_EXPLICIT 2026-10-02 "/execution-session Session 29 / Try again"`, recorded in [human-gate-decision.md](human-gate-decision.md) §Execution authorization. The context-tool gate was re-checked for execution: `graphify-out/` and `graphify-out-research/` are absent and there is no `headroom`, so `not_applicable` (execution phase).
- **Dependencies:** `npm --prefix ui ci`, `npm --prefix mcp-server ci` and `uv sync` exit 0. As in Session 27, plain `uv sync` installs only the root dev group, so 18 test modules failed to collect (`ModuleNotFoundError: No module named 'structlog'`). `uv sync --all-packages` (exit 0) installs the workspace packages.
- **`electron-setup`:** the first run, using `curl` from GitHub releases, was blocked by the host permission classifier. The user then directed a revision based on the previous plans. **A-2** ([human-gate-decision.md](human-gate-decision.md)) switches the container step to the package's own `install.js`, the Session 27 A-5 method this plan's `.ps1` already uses. `PASS electron-setup`: Electron 42.9.3, `v42.9.3` under `xvfb-run` (`s29-electron-setup.txt`). The incident record (an earlier Vitest run's `require('electron')` ran the installer as a side effect, and the binary was then deleted) is in A-2.
- **`prereq`:** `PASS MEU state {'MEU-57': 'approved', 'MEU-59': 'approved', 'MEU-60': 'approved', 'MEU-65': 'pending', 'MEU-66': 'pending'}` and `PASS prereq`: gate record, execution message, dependency trees, the 15 lucide icons and Electron launchability.

## Baseline

`validate-task.sh baseline` ran on the untouched product tree. `baseline.sha` = `c1694531fe29920104496318020dbbd5c1682349`.

| Stage | Result (container) |
|---|---|
| pytest (`s29-baseline-pytest.txt`) | `63 failed, 566 passed` in 82 s. The failed set is the container's env-bound `ENV_BOUND_PY` reference for `pytest_env_ok`. It is the same Windows-bound tooling/packaging set as Session 27 (63 failed then too). |
| Vitest (`s29-baseline-vitest`) | `PASS s29-baseline-vitest: 700 passed of 702`; env-bound tolerated: AC-51.6 (CRLF hash) and AC-41.3 (`P:/zorivest`). Total 702 = `COUNT_FLOORS`. |
| UI build / harness build | `PASS s29-baseline-build`, `PASS s29-baseline-harness-build` |
| Electron (`s29-baseline-e2e`) | `PASS s29-baseline-e2e: 114 passed`; env-bound tolerated: the 4 capture-picker stub specs, so 118 specs in total = `COUNT_FLOORS`. |

## Census (row 1)

`validate-task.sh census` (exit 0) wrote 333 hit lines (`s29-census.txt`). `TEST_AMENDMENTS` is empty, so every hit must be `unaffected`. Dispositions, grouped by file:

| File (hits) | Disposition |
|---|---|
| `ui/tests/unit/capture-page.behavior.test.ts` (125) | unaffected. Every tool, history, view and option id is kept (`ICON_BUTTON_RULE`, test-ID migration), and the tests locate them by test id. `:347-355`, `:1047-1054` (`h-7`, `aria-pressed`) → kept: `size="sm"` (D-9). `:1055-1056` (visible "Color" in the `role=group`, "Stroke" in the label) → kept: label text moves with its group into the options row. `:490` (`capture-stroke` after open) → kept: the default tool is Arrow, and `OPTIONS_BY_TOOL` gives `stroke` for Arrow. `:488-494`, `:497-525`, `:854-857` (text options for the Text tool or a selected text mark) → kept: the `text` group. `:941-944` (`flex-nowrap` on the tools and marks rows) → kept: both rows stay `flex-nowrap`, and the new options row is too. `:962-977` (AC-57.1 Settings disclosure by test id, `aria-expanded`, `[hidden]`) → kept: `OPTIONS_TOGGLE` keeps the test id, `aria-*` and panel. `:358-363` (viewBox, `xMidYMid meet`), `:755-761`, `:1246-1322` (handle radius × fit `s`; the surface rect stub) → kept: at Fit, `VIEW_TRANSFORM` equals `fitScaleOrigin`, and the surface stays the measured container (`SURFACE_POINTER`, `CONTENT_BOX`). `:1064-1076` (no shot: disabled, `title` matches /shot/) → kept: `NO_SHOT_HINT`. |
| `ui/tests/e2e/capture-inbox.test.ts` (71) | unaffected. Test ids are kept. `:28` `sampleShot` gains only an optional size argument (`ZOOM_SHOT`). `:44-52`, `:290-303`, `:414-425`, `:662-670` re-derive FIT_MAP from the surface box → kept at Fit (the default zoom state). `:223`, `:691-700` (the header toggle by test id; `aria-expanded`; inbox hidden/visible) → kept. `:240-241` (W9-3 fills `capture-color` and `capture-stroke` with no shot) → kept: the chrome still renders without a shot, and the default tool (Arrow) has the `stroke` group. `:466-467` (Arrow tool → `capture-text-bg` hidden) → kept (absent counts as hidden). `:732-737` (AC-57.10 no-shot tools disabled) → kept. |
| `ui/tests/e2e/test-ids.ts` (29) | registry constants; the MEU-65/66 blocks are appended after the MEU-51 marker (`NEW_TESTIDS`) → unaffected. |
| `ui/tests/unit/capture-page.test.ts` (22) | `:63-102` (`WAVE9_TESTIDS` must be in the registry) → kept. `:251-256` (AC-59.4: `viewBox`, `preserveAspectRatio`, `xMidYMid`, no `devicePixelRatio` in `CaptureViewport.tsx`) → kept (`SURFACE_POINTER`, `CONTENT_BOX`). **`:260-267` (AC-39.8: the literal tool, undo and redo ids must appear in `CaptureViewport.tsx`)** → kept **by design constraint**: `TOOLBAR_BUTTONS` is keyed by test id, and `CaptureViewport.tsx` renders each icon button with its literal id. Moving the ids only into `capture-toolbar.ts` would break this test. `:345-346` (Settings page `capture-settings` ids) → unaffected (another page). |
| `ui/tests/unit/layout-primitives.test.ts` (20) | AC-51.1 (`Disclosure` named "Advanced", ghost, hidden panel), AC-51.5 (no `features/`, no hex, no `TODO`), AC-51.6 (prefix hash), AC-51.7 (adoption) → kept: `DISCLOSURE_PROPS` are optional, and with none passed the DOM is unchanged (AC-65.6). `Disclosure.tsx` gains no hex and no feature import. |
| `ui/tests/unit/tts-page.behavior.test.ts:245,253`, `ui/tests/e2e/tts-generate.test.ts:464,469` | exact `Cleanup · N of 11 steps` toggle text → kept: TTS passes none of the new props. |
| `ui/tests/unit/capture-fit-map.test.ts` (4), `capture-hit-test.test.ts` (7) | existing exports keep their signatures and outputs (`VIEW_MAP` is additive; S6) → unaffected. |
| `ui/tests/unit/capture-help-content.test.ts` (5) | existing sentences stay verbatim; `ZOOM_HELP_SENTENCE` is appended → unaffected. |
| `ui/tests/unit/capture-color.test.ts:7` | module import only → unaffected. |
| `'Settings'` hits: `command-palette-nav.spec.ts:45`, `settings.test.ts:244,297`, `console-chrome.test.ts:104`, `chrome-zorivest.test.ts:183`, `app-shell-wiring.test.ts:86`, `settings-rail.test.tsx:146,198`, `settings-page.test.ts:501` | the app Settings page, nav and palette, not the Capture header → unaffected. |
| `h-7` / `Disclosure` / `Controls` / `wheel` substring hits in Settings, Convert, Downloader and queue suites (`settings-rail.test.tsx:411,437,503`, `convert-page.behavior.test.ts:828`, `convert-page.test.ts:204,213,262`, `download-controls.test.ts`, `convert-controls.test.ts`, `reorder-body.test.ts`, `queue-card-slots.test.tsx`, `queue-canon.test.ts:149-152`, `fixtures/queue-slot-baseline.json`) | other pages; the Convert/Downloader `Disclosure` usages pass no new prop → unaffected. |
| `capture-picker.test.ts:68` | `Access-Control-Allow-Origin` header (substring) → unaffected. |

**New contradictions outside `TEST_AMENDMENTS`: none.** Stop condition S2 does not fire. One structural pin is handled by design, not by amendment: AC-39.8 needs the literal ids in `CaptureViewport.tsx`, so `TOOLBAR_BUTTONS` is keyed by test id.

## MEU-65 Red (row 2)

`validate-task.sh red65` exit 0 (`s29-65-red.txt`):

- `PASS AC-65 RED: 4 failing AC-65 assertions, 63 passing`
- `PASS AC-65 E2E RED: 2 failing AC-65 specs`
- `PASS AC-65.4 RED on toBeLessThanOrEqual`. The measured geometry: `tool select at innerWidth 1280: capture-chrome-tools scrollWidth`, expected `<= 836`, received `1300`. The tools row overflows at `DEFAULT_WINDOW` in the container too, so Stop condition S4 does not fire.

Each failure from `s29-65-red-vitest.json` / `s29-65-red-e2e.json`:

| Test | Failure | Disposition |
|---|---|---|
| AC-65.2 icon-only toolbar | `capture-tool-select: expected null to be 'Select'` (no `aria-label`) | decisive Red |
| AC-65.2 negative, no shot | `capture-tool-select: expected 'Select' to be ''` (text node present) | decisive Red |
| AC-65.3 negative, Highlight | `expected <input …> to be null` (`capture-stroke` shown for Highlight) | decisive Red |
| AC-65.6 variant/icon/chevron | `expected '…' to contain 'btn-secondary'` | decisive Red |
| AC-65.3 options row (×2) | `Unable to find an element by: [data-testid="capture-chrome-options"]` | Red on the missing new row. This is a missing-element query error, not a setup error, so the helper lists it as "other". |
| AC-65.5 Options toggle | `Unable to find an accessible element with the role "button" and name "Options"` | Red on the missing name (same "other" class) |
| `capture-toolbar.test.ts` (AC-65.1, AC-65.7) | suite load: `Cannot find module '…/capture-toolbar'` | the declared new-module Red (`vitest_red` allows it for this file only) |
| AC-51.6 prefix hash | `expected 'DCABD0F9…' to be '819760B9…'` | env-bound (`ENV_BOUND_*` CRLF proof; LF checkout) |
| AC-65.6 default Disclosure | passed | regression lock, expected green at Red: the default render must not change |
| E2E AC-65.4 | `toBeLessThanOrEqual`, 1300 > 836 | decisive Red (geometry) |
| E2E AC-65.5 | `getByRole('button', { name: 'Options', exact: true })` count 0 | decisive Red |

No existing test failed. `TEST_AMENDMENTS` stays empty.

## MEU-66 Red (row 5)

`validate-task.sh red66` exit 0 (`s29-66-red.txt`): `PASS AC-66 RED: 7 failing AC-66 assertions, 69 passing` and `PASS AC-66 E2E RED: 4 failing AC-66 specs`.

| Test | Failure | Disposition |
|---|---|---|
| AC-66.2, AC-66.3 (`capture-fit-map.test.ts`, 6 tests) | `expected 'undefined' to be 'function'` (each test of a new export starts with a `typeof` assertion) | decisive Red |
| AC-66.16 help sentence | `expected 'Arrow, Box, Highlight, and Text draw …' to contain 'Zoom with the mouse wheel, …'` | decisive Red |
| AC-66.7 – AC-66.11 (`capture-page.behavior.test.ts`, 11 tests including the viewport-level `SURFACE_POINTER` test) | `Unable to find an element by: [data-testid="capture-zoom-in"]` / `"capture-zoom-level"`, or no button named "Zoom out" | Red on the missing zoom controls (missing-element class, listed by the helper as "other") |
| `capture-zoom.test.ts` (AC-66.1, AC-66.4, AC-66.6, AC-66.17) | suite load: `Cannot find module '…/capture-zoom'` | the declared new-module Red |
| AC-66.5 (`capture-hit-test.test.ts`, 2 tests) | passed | `green-at-baseline (lock)`, as the plan states: `hitTestMarks` is already generic in `scale/ox/oy`; AC-66.11 is the Red-capable chain |
| E2E AC-66.12 | `Expected: "fit" Received: null` (no `data-zoom-kind`) | decisive Red |
| E2E AC-66.13 / 66.14 / 66.15 | timeout waiting for `capture-zoom-in` / `capture-zoom-level` | Red on the missing controls |

No existing test failed. `TEST_AMENDMENTS` stays empty.

## MEU-66 Green and gate (rows 6–8)

- `green66-unit`: `PASS s29-66-green-unit: 24 passed of 24`. AC-66.17 was moved, unchanged, from `capture-zoom.test.ts` to `capture-page.behavior.test.ts` before Green, because it reads `CaptureViewport.tsx`, which gains the ids only in row 7 (MEU-66 handoff D-26).
- `green66` first run: Vitest 188/189 and 2 of the 4 new Electron specs failed. AC-66.12's oracle assumed the cursor pixel stays fixed on both axes, but a fitting axis is centred by `VIEW_TRANSFORM`. AC-66.13's helper assumed a ladder level below 25 %. **A-3** ([human-gate-decision.md](human-gate-decision.md)) records the user's TA-1 (per-axis oracle) and TA-2 (Ctrl+= twice before Ctrl+-). Product code was unchanged.
- `green66` after A-3: `PASS s29-66-green: 188 passed of 189` (AC-51.6 env-bound), `PASS s29-66-green-build`, `PASS s29-66-green-e2e: 4 passed`. **Stop condition S5 did not fire:** `getZoomFactor()` stayed 1 after every key and wheel step.
- `gate66`: typecheck, lint, Vitest 188/189, builds, Electron capture-inbox 19 passed, Disclosure neighbours 15 passed, `repeat-each=20` 240 expected / 0 unexpected / 0 flaky.

## Hub reconciliation (row 9)

`validate-task.sh hub` exit 0: `PASS hub reconciliation`, `PASS s29-hub-render-check`, `PASS s29-hub-doc-tests: 17 passed of 18` (AC-41.3 env-bound).
- `09-screenshot-capture.md`:
  - The §Viewport tools zoom sentence now points to §Viewport zoom (MEU-66).
  - The Levels row names `ZOOM_LADDER` with its `page_zoom.cc` citation (Session 29 plan D-14).
  - New rows: Pan gestures (D-15), Wheel step (D-18) and Key scope (D-17) in §Viewport zoom; Icon size (D-9) and Options per tool (D-12) in §Viewport toolbar icons and Options.
  - §MEUs gains the MEU-65, MEU-66 and MEU-67 rows (matrix 9.10–9.12).
- `11-page-layout.md` §Capture page layout: one prose sentence about the Options toggle (MEU-65). The CP decision rows and mockup-inventory rows are untouched (AC-50.1/50.4 lock).
- `gui-actions-index.md`: `capture:zoom_in`, `capture:zoom_out` and `capture:zoom_fit` added after `capture:redo` (Palette `no`, local view).

## Container pre-gate (H1-2), non-authoritative

`validate-task.sh pregate` exit 0 (`s29-pregate.txt`). Input identity: HEAD `05b5b86a1d4fb40bfb3408027b9ab6516949bca4`; `git status --porcelain` sha256 `e0d19be1…` (the H1-1 `task.md` mark only); `ui/package-lock.json` `d26fb2de…`, `mcp-server/package-lock.json` `62147de5…`, `uv.lock` `da452c34…`; Node v22.22.0; electron 42.9.3.

| Stage | Result |
|---|---|
| py-types, py-lint, ui-types, ui-lint, mcp-types | PASS (pyright 0 errors) |
| plan-static | `PASS static: 20 task rows; scripts and plan cross-references agree` |
| task-contract | PASS |
| py-tests (`pytest_env_ok`) | `PASS pytest: no new failures (baseline env-bound 63, head 63, passed 566)` |
| ui-tests (`vitest_env_ok`) | `744 passed of 746`; env-bound tolerated: AC-51.6, AC-41.3. Total 746 ≥ 702 floor. |
| ui-build, ui-harness-build, mcp-build | PASS |
| mcp-tests | 334 passed (22 files) |
| openapi, state-render | PASS |
| ui-electron (`electron_env_ok`) | `120 passed`; env-bound tolerated: the 4 capture-picker stub specs. Playwright `expected` 120 ≥ 118 floor; `unexpected` 4 (the stub specs, Windows-only), flaky 0. |
| source-audit | 0 hits over `AUDIT_SRC` |

`PASS container pre-gate (authoritative: windows-gate + CAPTURE_LOOK)`.

## WINDOWS_GATE attempt 1 (PASS)

Source: Mat's report (`USER_EXPLICIT`, relayed in the Claude Code web session, 2026-10-02); result committed in `a12ecea`.
- Tree clean at `f69a9d0`, 2026-10-01 22:10:57–22:16:18 -04:00. Electron 42.9.3, Node v24.19.0, no preflight drift.
- All 17 stages exit 0. Vitest 746 total / 0 failed; Playwright 124 expected / 0 unexpected / 0 flaky / 0 skipped; pytest 629 passed / 0 failed.
- **Quiet machine: not fully quiet.** No Electron, Playwright or Remote Control process was running, and `ELECTRON_RUN_AS_NODE` and `AVKIT_E2E_OUT_DIR` were cleared. Two other agent sessions (zorivest-cb, zorivest-e9) were running zorivest pytest and a backend during the gate. The user directed the run to go ahead and be recorded; the result commit body says so. The gate still passed with zero tolerance.
- `validate-task.sh windows-gate-check` exit 0: `PASS windows gate @ f69a9d06dc019e1575efda971f58717ad93ca4c5: vitest {'passed': 746, 'failed': 0, 'total': 746} e2e {'expected': 124, 'unexpected': 0, 'skipped': 0, 'flaky': 0} pytest {'passed': 629, 'failed': 0}`.

## CAPTURE_LOOK attempt 1 (on f69a9d0; L5 fail, superseded)

Source: Mat's report (`USER_EXPLICIT`, relayed 2026-10-02), on the gate's tested commit `f69a9d0`.
- **Setup:** the app ran in dev mode (`npm run dev`) with fresh app data, at the default 1280×800 window with Windows display scaling 200 %. The test shot is 2194×1234.
- **Input:** Mat drove the app through Playwright, and used real Windows mouse, wheel and keyboard input wherever the result depends on it.
- **Evidence:** `C:/Temp/av-kit/s29-look*` on Mat's host.

| Item | Result |
|---|---|
| L1 pass | Each of the five tools: the tools and options rows are 823/823 px (no scroll, nothing clipped); all 12 icon tooltips appear on a real hover |
| L2 pass | "Options" reads as a button (fill, sliders icon, chevron); it opens and closes the Inbox/Hotkey panel, and the chevron flips |
| L3 pass | Each real wheel notch is exactly one step (33→50→67→75 and back); the cursor pixel stays within about 1 image px on overflowing axes, and a fitting axis is centred |
| L4 pass | Ctrl+= Fit→25→33→50, Ctrl+- →33, Ctrl+0 →Fit with real keys; page scale, window width, nav button size and body font unchanged |
| L5 fail | At 200 %, a real click on the Arrow tool and then a real Space+drag created "Arrow 1", and the image did not move. The click leaves focus on the tool button, and `spaceArmable()` refuses to arm Space while a button has focus. Space+drag with focus off the buttons panned exactly (+150,+100); middle-drag always panned exactly (±120,±80); neither made a mark. Screenshot `L5-real-A-arrowfocus-space-drag.png`. |
| L6 pass | At 200 % an arrow on the eye catchlight (image px 250,599); after Save and switching to Annotated, the baked arrowhead sits on the same spot (`L6-compare.png`) |

**Observations outside the checklist (Mat):**
1. Opening Options moves the Options button from the header row onto its own line.
2. At 1280×800 with 200 % scaling, the image frame is about 823×200 px, with a large empty area below it.
3. The baked arrow looks thinner and stair-stepped next to the live overlay.
4. After one arrow is drawn, the tool switches back to Select. This is the Human-approved MEU-60 auto-Select (AC-60.4).

## Corrections after CAPTURE_LOOK (A-4, A-5)

TDD for each fix: the new tests were written first and proven Red, then the fix went in.

| AC | Red (container, `f69a9d0` product code + new tests) | Fix | Green |
|---|---|---|---|
| AC-66.18 (L5, A-4) | jsdom: `expected <button …> to be <div …>` (focus stayed on the Arrow button). Electron: `toBeFocused()` failed, Received `inactive`. The keyboard negative passed at baseline (a lock). | `CaptureViewport.tsx`: the tools row focuses the surface after a mouse click (`event.detail > 0`) on a button | pass |
| AC-65.8 (observation 1, A-5) | `toggle top` Expected `<= 1` Received `48` | `CapturePage.tsx`: the Disclosure section is `flex min-w-0 flex-1 flex-col items-end gap-2` | pass |
| AC-66.19 (observation 2, A-5) | `{"mainBottom":773,"pageBottom":574,…,"surfaceHeight":200}`: the page ended 199 px above `main`'s bottom | `CapturePage.tsx`: the page is `min-h-full` and the content row `flex-1` | pass |

Targeted run after the fixes: `capture-inbox.test.ts -g "AC-66.18|AC-65.8|AC-66.19|AC-65.4|AC-57"` 8 passed.

Filed (A-5): `CAPTURE-BAKE-ARROW-THIN` and `CAPTURE-AUTO-SELECT-AFTER-DRAW` (`known-issues.yaml`, rendered and checked).

These corrections touch `GATED_PATHS` (`ui/`), so `WINDOWS_GATE` attempt 2 plus a re-look of L2 and L5 follow (cloud-local §3.4).

`gate66` after the corrections: `PASS s29-66-vitest: 190 passed of 191` (AC-51.6 env-bound), builds PASS, `PASS s29-66-e2e: 22 passed`, `PASS s29-66-e2e-disclosure: 15 passed`, `repeat-each=20` 300 expected / 0 unexpected / 0 flaky.

## Container pre-gate before WINDOWS_GATE attempt 2

`validate-task.sh pregate` exit 0 on HEAD `c2452aa` (`s29-pregate-2.txt`):
- static stages PASS;
- pytest: no new failures (env-bound 63, passed 566);
- Vitest `746 passed of 748`, env-bound tolerated: AC-51.6 and AC-41.3;
- builds, MCP 334 passed, OpenAPI and state-render PASS;
- Electron `123 passed`, plus the 4 env-bound capture-picker specs (127 total);
- source audit: 0 hits.

## WINDOWS_GATE attempt 2 (FAIL at ui-electron; load) and CAPTURE_LOOK 2 (all pass)

Source: Mat's report (`USER_EXPLICIT`, relayed 2026-10-02); result `2c2b34b` on `c13a005` (tested code `c2452aa`).
- **Gate:** stages 1–15 exit 0; pytest 629/0; Vitest 748/748. `ui-electron` exit 1: Playwright 126 expected / 1 unexpected / 0 flaky / 0 skipped (127 total, as predicted). W1-8 (`download-queue.test.ts:675`) hit its 60 s timeout, then a worker hit its teardown timeout. The Electron stage took 13.2 min (2.8 min in attempt 1). `source-audit` did not run.
- **Machine:** not quiet. `P:/zorivest-gt7` ran 48-worker pytest at about 96 % CPU across the Electron stage. Preflight matched attempt 1 (agentic-framework `4033418f…`, registry `B06D7CDA…`). Evidence: `C:/Temp/av-kit/keep/c13a0056c1f27aaca6e1a7ce9a77ec7c78d9a57f-attempt2/`.
- **`windows-gate-check`:** FAIL (stage list stops at `ui-electron`, so no `source-audit`). This is expected for a failed attempt. → **A-6** (TA-3, W1-8 hardening), then attempt 3.

**CAPTURE_LOOK 2.** Mat ran it in dev mode at 1280×800 (display scaling 2), driving the app through the debugging port with real mouse and keyboard input. It ran on `2c2b34b`, whose code is identical to `c13a005` / `c2452aa`; screenshots are in `C:/Temp/av-kit/s29-look2/`.

| Item | Result |
|---|---|
| L1 pass | All 5 tools fit (no overflow or clipping); all 12 real-hover tooltips appear |
| L2 pass | Options opens and closes the panel. The button stays at x 1120.7, y 138 when closed, open and closed again (moved 0, 0) — A-5 / AC-65.8 confirmed |
| L3 pass | Each real notch is one step (33→50→67→75→67→50 %); the cursor point drifts ≤ 0.5 image px |
| L4 pass | Real keys 50→67→75→80→75 %, then Fit; no layout change |
| L5 pass | At 200 %, after a real mouse click on Arrow, focus is on the image and Arrow stays active. Space+drag panned exactly (−150, −100), no mark, nothing to undo; middle-drag panned (+120, +80); Box, Highlight and Text each panned exactly (+60, +40), no mark — A-4 / AC-66.18 confirmed |
| L6 pass | An arrow on the eye catchlight at 200 % sits on the catchlight after Save; Annotated keeps the 200 % view |
| Frame | 823×365 px, from just below the toolbar to 699 of the 739 px window, no scrolling (attempt 1: 823×200) — A-5 / AC-66.19 confirmed |

**Non-blocking notes (Mat):**
1. About 37 px of empty space above the toolbar where the Options panel goes.
2. The image area shows a focus ring after a tool click. This is the A-4 hand-off: the surface has `tabIndex=0` and keeps the app's focus-visible ring.
3. A ShareX-held F2 shows the hotkey banner, which takes about 4 px off the frame (existing MEU-57 behaviour).
4. The baked arrow is thinner, and auto-Select applies after a draw; both are already filed.

## Container pre-gate before WINDOWS_GATE attempt 3

`validate-task.sh pregate` exit 0 on HEAD `66c7bfd` (`s29-pregate-3.txt`):
- static stages PASS;
- pytest: no new failures (passed 566);
- Vitest `746 passed of 748` (AC-51.6, AC-41.3 env-bound);
- builds, MCP, OpenAPI and state-render PASS;
- Electron `123 passed` + 4 env-bound capture-picker specs;
- source audit: 0 hits.

## WINDOWS_GATE attempts 3 and 4 (PASS); attempt 4 is the gate of record

Source: Mat's report (`USER_EXPLICIT`, relayed 2026-10-02).

**Attempt 4 (gate of record).**
- **Result:** commit `f7a3c44`, tested `bde58a4` (clean tree; docs-only over `383c49e`; tested code `66c7bfd`).
- **Preflight:** agentic-framework `4033418f…`, registry `B06D7CDA…1C2C78`; equal to attempts 1–3, drift false.
- **Stages and counts:** 17/17 exit 0, including `source-audit` (no hits). pytest 629/0; Vitest 748/748/0; Playwright 127 expected / 0 unexpected / 0 flaky / 0 skipped. Ran 16:50:43–16:55:29 -04:00; `ui-electron` took 2.3 min.
- **Machine: quiet.** No foreign pytest, validate_codebase, Vitest or Playwright processes ran during the gate (sampled every 20 s). The peer session SP-11 held its test runs. `ELECTRON_RUN_AS_NODE` and `AVKIT_E2E_OUT_DIR` were cleared. Receipt: `C:/Temp/av-kit/s29-gate4-quiet.txt`.
- **`validate-task.sh windows-gate-check`** exit 0: `PASS windows gate @ bde58a4a14b2a9187b6937770ce7386240e274f6: vitest {'passed': 748, 'failed': 0, 'total': 748} e2e {'expected': 127, 'unexpected': 0, 'skipped': 0, 'flaky': 0} pytest {'passed': 629, 'failed': 0}`.

**Attempt 3** (`bde58a4` on `383c49e`) also passed, 17/17 with the same counts, but on a loaded machine: untraced zorivest pytest runs, CPU peaks near 100 %, `ui-electron` 3.6 min.

**TA-3:** W1-8 passed in both attempts, with no timeout or teardown error.

**`ui-electron` duration by attempt:** 2.8 min (1), 13.2 min (2, failed under load), 3.6 min (3), 2.3 min (4).

## CAPTURE_LOOK

The look of record is Mat's second look (`USER_EXPLICIT`, relayed 2026-10-02; full table above in §WINDOWS_GATE attempt 2 … and CAPTURE_LOOK 2).
- **Where it ran:** on `2c2b34b`, whose renderer code is identical to `c2452aa`.
- **Why it binds to the gate:** the gate of record tested `bde58a4`, whose tested code is `66c7bfd`, and `66c7bfd` differs from `c2452aa` only by TA-3 in `ui/tests/e2e/download-queue.test.ts`. `ui/src` is byte-identical (D-29). The look therefore applies to the code gated at `bde58a4`.

| Item | Result |
|---|---|
| L1 | pass: all 5 tools fit with no overflow or clipping; all 12 real-hover tooltips appear |
| L2 | pass: Options opens and closes the panel, and the button does not move (0, 0) |
| L3 | pass: one real wheel notch is one step; the cursor point drifts ≤ 0.5 image px |
| L4 | pass: Ctrl+= / Ctrl+- / Ctrl+0 step the image only; no layout change |
| L5 | pass: after a real mouse click on Arrow, Space+drag pans exactly with no mark; middle-drag pans |
| L6 | pass: the baked arrow sits on the aimed detail at 200 % |

Frame height: 823×365 at 1280×800, with no scrolling.

## Execution review (H1-7): approved, round 1

The reviewer was the user-authorized Fable 5.1 subagent, in a separate context (`human-review-decision.md`). It wrote `.agent/context/handoffs/2026-10-01-capture-viewport-chrome-implementation-critical-review.md` and modified no other file. `validate-task.sh review-check … execution 6` exit 0: `PASS execution review approved round 1 by claude-fable-5-1-subagent`.

Findings: 3 Low, none blocking. Handling:
- **F1** (`api-scope` failed at HEAD because the TA-3 file was in no Files Modified table): fixed by adding the row to the plan's MEU-66 Files Modified table and the MEU-66 handoff's Changed Files. `api-scope` exit 0.
- **F2** (`plan-static` failed because D-29 had no definition site the checker reads): fixed with a `### D-29` section in the plan pointing to the handoff's `decision_log`. `PASS static: 20 task rows`.
- **F3** (AC-66.7's "same object" clause is proven by proxies): accepted as is. The reviewer rates it 🟡 Adequate and notes that the AC-66.14 and AC-66.15 Electron ledgers close the stored half. Tightening it would change a `GATED_PATHS` test file and reopen the Windows gate for an adequate assertion.

F1 and F2 are docs-only, outside `GATED_PATHS`, so the gate of record stays bound to the code.
