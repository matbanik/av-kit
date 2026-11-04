# Human gate decision: gate location (plan time)

This file records plan-time decisions, as `.agent/docs/cloud-local-collaboration.md` §1 requires. It does **not** authorize execution. Claude Code resolves to `plan_to_exec_gate: human`, so execution starts only on a later direct user message. That message is recorded under §Execution authorization below when it arrives.

## A-1: where execution and the authoritative gate run

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code web session), 2026-10-01. The planner asked, "Where should Session 29 execution and the authoritative gate run?" The user chose:

> Split like Sessions 25–27 (Recommended)

The option text shown to the user:

> I write code and tests here and run a container pre-gate that tolerates only the declared env-bound failures. You then run one authoritative WINDOWS_GATE (validate-task.ps1) on your machine and push the result JSON, plus a short manual toolbar/zoom look at the default window.

What this decides, once execution is authorized:

- **Container (cloud):** task rows 0–9 and H1-1 to H1-5. The container pre-gate (`validate-task.sh pregate`) is non-authoritative. It tolerates only the `ENV_BOUND_*` census in `implementation-plan.md` §Environment-bound census, each with a proven signature.
- **Local (Mat, Windows, `P:/av-kit`):**
  - `WINDOWS_GATE` (`validate-task.ps1 -Check windows-gate`) with zero tolerance. The local side commits and pushes the result JSON.
  - Then the `CAPTURE_LOOK` checklist L1–L6 on the same commit ([local-requests.md](local-requests.md) §GATE), returned one line per item. This is "the short manual toolbar/zoom look".
  - Row H1-6 is the planned turn boundary.
- **No LOCAL_REPRO request.** CAPTURE-TOOLBAR-ICONS was already reproduced on the target (Session 27 `LOCAL_REPRO` R3, `known-issues.yaml` verification block). CAPTURE-SETTINGS-BUTTON-LABEL and CAPTURE-VIEWPORT-ZOOM are source facts: the `Disclosure title='Settings'` at `CapturePage.tsx:1133-1139`, and no zoom code in `features/capture`. AC-65.4 must go Red in the container, otherwise Stop condition S4 applies.

This decision does not authorize merge, release or deploy. It approves no test-expectation change (`TEST_AMENDMENTS` is empty). Changes to shared machine state (`P:/.agent`, sibling repos, `model-registry.local.json`) stay one-way-door decisions (cloud-local §3.5).

## Execution authorization

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code web session), 2026-10-02, after the Round 2 plan approval. The user wrote:

> /execution-session Session 29
> Try again

The slash command is not installed in this session, so the request was read as a plain instruction to run `.agent/workflows/execution-session.md` for Session 29, whose plan is this folder. "Try again" refers to an earlier attempt that did not start.

What this authorizes:

- **Execution** of `task.md` rows 0–9 and H1-1 to H2-3, under A-1's split (container, then `WINDOWS_GATE` + `CAPTURE_LOOK` on Mat's machine).
- **Autonomous decisions D-8 to D-21**: accepted. None were vetoed.
- **`TEST_AMENDMENTS`** stays empty. No existing expectation changes.
- **Commit and push** to the session's designated branch, `claude/hopeful-rubin-y3qkgn`, which the host session instructions name. `local-requests.md` names `claude/bold-edison-b91w56`, which was the planning branch; the GATE request uses the designated branch instead.
- Merge, release and deploy are **not** authorized.

## A-2: container `electron-setup` uses the Electron package's own installer

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code web session), 2026-10-02. The first `electron-setup` run fetches the release zip with `curl` from GitHub, and the host's permission classifier blocked it. After that block, the user wrote:

> Revise the Electron approach by looking at what was completed in the previous plans leading up to this one. 3 or 2 plans back should be sufficient.

**Precedents.**
- Session 26 (`2026-09-28-p11-capture-settings/walkthrough.md:13`) and Session 27 (`2026-09-30-tts-repair/walkthrough.md:36`) both ran `electron-setup` in the container.
- Session 27 A-5 (`2026-09-30-tts-repair/human-gate-decision.md`, A-5 §Implementation) settled on `node ui/node_modules/electron/install.js`. That is the same script `require('electron')` spawns on first use. It downloads through `@electron/get`, which honours `ELECTRON_GET_USE_PROXY`, checks the result against the package's `checksums.json`, and exits 0 as a no-op when the binary is already there.
- This plan's `validate-task.ps1` `npm-ci` stage already uses that method.

**Incident (recorded).** The baseline Vitest run happened before this decision, and it imported `electron` (through `g36-csp.test.ts` → `src/main/index`). That import ran `install.js` as a side effect, which materialized the binary and failed AC-19.20 in that run. The binary was then deleted, because the curl route had just been blocked. The baseline Vitest run is repeated after A-2.

**Change.** `validate-task.sh electron-setup` now runs `node ui/node_modules/electron/install.js` once, serially, before any test, and then requires `dist/electron` and `path.txt`. The xvfb `--version` smoke is unchanged. No test, stage id or `GATED_PATHS` entry changes (`validate-task.sh` is not in `GATED_PATHS`).

**Result.** `PASS electron-setup`: Electron 42.9.3, `v42.9.3` under `xvfb-run` (`s29-electron-setup.txt`).

## A-3: `TEST_AMENDMENTS` TA-1 and TA-2 (Electron AC-66.12 and AC-66.13)

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code web session), 2026-10-02 (AskUserQuestion), during row 7. `green66` failed two of the four new MEU-66 Electron specs. Product code was not the cause.

- **AC-66.12.** The approved oracle required the cursor's image pixel to move ≤ 1 px on both axes after one wheel step from Fit. With the 2400×1600 `ZOOM_SHOT` at the container's default window, Fit ≈ 0.24 and the first step is 25 %. The image is then 600 px wide in a frame about 810 px wide, so `VIEW_TRANSFORM` (09:636) centres the x axis. The cursor pixel moved 669 px on x (`Expected: <= 1, Received: 668.8`), while y stayed anchored. AC-66.4 already limits the ≤ 1 px claim to axes where no clamp or centring applies.
- **AC-66.13.** The test's oracle helper threw `no ladder level below 0.25`. The first step up from Fit is already 25 %, the bottom of the ladder, so Ctrl+- there is a correct no-op (`ZOOM_STEP` returns null).

The question offered three options for AC-66.12: a per-axis oracle (recommended), taking the wheel step from 100 %, or anchoring a fitting axis to the cursor (a spec change). It offered two for AC-66.13: fix the key sequence (recommended), or assert the no-op. The user chose:

> AC-66.12: Per-axis oracle (Recommended) — "TA-1: on an axis whose content overflows after the step, the cursor pixel moves ≤ 1 px; on an axis that fits, the content is centred ((Cw − W·s)/2). This matches VIEW_TRANSFORM and AC-66.4's 'where no clamp applies'. Product code unchanged."
>
> AC-66.13: Yes, fix the sequence (Recommended) — "TA-2: the key sequence becomes Ctrl+=, Ctrl+=, Ctrl+-, Ctrl+0 in both focus states, with the readout predicted by ZOOM_STEP and getZoomFactor() == 1 after every key."

**What changes.** These are the only `TEST_AMENDMENTS` in this plan. Both touch only new Session 29 specs in `ui/tests/e2e/capture-inbox.test.ts`.
- **TA-1:** an `expectAboutCursor` helper asserts ≤ 1 px on each overflowing axis and a centred offset on each fitting axis, and requires at least one overflowing axis. It applies to the wheel step and the Ctrl+wheel step.
- **TA-2:** the AC-66.13 key loop adds a second Ctrl+= before Ctrl+-.

No existing test, page-zoom check or product file changes.

**Applying TA-1 (two test-side details, recorded).**
- `expectAboutCursor` checks a fitting axis's centred offset to sub-pixel tolerance (`toBeCloseTo(…, 0)`). The observables carry the scale to 4 decimals, so 1/3 reads back as 0.3333. Over the 2400 px shot that rounding moves the expected centred offset by 0.04 px (observed `Expected 18.04, Received 18`). The ≤ 1 px cursor check on overflowing axes is unchanged.
- `readZoom` waits two animation frames before reading the observables. This is setup only and changes no assertion.

After both, `capture-inbox.test.ts -g "AC-66" --repeat-each=3` gives 12 passed.

## A-4: CAPTURE_LOOK L5 — a mouse click on a toolbar button hands focus to the draw surface

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code web session), 2026-10-02 (AskUserQuestion), after `WINDOWS_GATE` attempt 1 passed and `CAPTURE_LOOK` returned L5 fail.
- **The failure:** a real click on the Arrow tool, then a real Space+drag, drew a mark instead of panning. The click leaves focus on the tool button, and `spaceArmable()` (`CaptureViewport.tsx:531`) deliberately refuses to arm Space on a focused button, so that keyboard users' Space still activates the button.
- **The options offered:** focus hand-off on mouse click (recommended); buttons that never take mouse focus; or accept and document. The user chose:

> Mouse click hands focus to the image (Recommended) — "A-4: when a toolbar button is clicked with the mouse (event.detail > 0), focus moves to the draw surface, so Space then pans. Keyboard activation (Enter/Space) keeps focus on the button, so AC-66.10's keyboard negative and accessibility are unchanged. Adds one jsdom and one Electron test (mouse click on Arrow, then Space+drag pans with no mark). Changes 1 product file."

New AC: **AC-66.18** (`implementation-plan.md`). The change touches `GATED_PATHS`, so `WINDOWS_GATE` attempt 2 and an L5 re-look follow.

## A-5: Mat's out-of-checklist observations — fix the easy ones here, file the rest

Source: `USER_EXPLICIT`, same exchange. The question asked which of the four observations to file as known issues. The user answered:

> first classify the effort and if they are easy fixes, apply the fixes and add them to this plan. If they are to complex file them for later.

Classification:

| # | Observation | Effort | Disposition |
|---|---|---|---|
| 1 | Opening Options moves the button from the header row onto its own line | Easy. The Disclosure section is a content-sized flex item (`ml-auto`), so the open panel widens it and it wraps. As `flex-1 basis-0 min-w-0 items-end` it never wraps; the panel opens under the button and wraps inside the remaining width. | Fixed in this plan: **AC-65.8** |
| 2 | At 1280×800 the image frame is about 823×200 px, with empty space below | Easy. `main` has a definite height (`AppShell.tsx` `flex-1 min-h-0 overflow-auto`) and the Downloader, Convert and Transcript pages fill it with `h-full`, but the Capture page column does not, so the surface stops at `min-h-[200px]`. The page gets `min-h-full` and the content row `flex-1`. | Fixed in this plan: **AC-66.19** |
| 3 | The baked arrow looks thinner and stair-stepped next to the live overlay | Not easy. The bake is the Python/Pillow renderer in `packages/infrastructure`, which this plan's `PRODUCT_SCOPE` freezes, and matching the SVG stroke and anti-aliasing is a design question. | Filed: `CAPTURE-BAKE-ARROW-THIN` |
| 4 | After one arrow is drawn, the tool switches back to Select | Not a defect. It is the Human-approved MEU-60 auto-Select rule (AC-60.4; 09 §Annotation edit until Save), and changing it reverses that decision. | Filed as a decision item: `CAPTURE-AUTO-SELECT-AFTER-DRAW` |

Fixes 1 and 2 touch `CapturePage.tsx` (already in both Files Modified tables) and add Electron and jsdom tests. Both ride `WINDOWS_GATE` attempt 2 with A-4, and the re-look covers L2 (Options) as well as L5.

## A-6: WINDOWS_GATE attempt 2 — harden W1-8 (TA-3), then attempt 3

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code web session), 2026-10-02 (AskUserQuestion), after Mat's attempt-2 report.
- **Mat's report:** result `2c2b34b` on `c13a005`. Stages 1–15 exit 0; pytest 629/0; Vitest 748/748. `ui-electron` exit 1: Playwright 126 expected / 1 unexpected / 0 flaky. `download-queue.test.ts:675` "W1-8 card primary actions and kebab open items replace the retired row buttons" hit its 60 s timeout, then a worker hit its teardown timeout. The Electron stage took 13.2 min against 2.8 min in attempt 1. `source-audit` did not run.
- **Machine:** not quiet. `P:/zorivest-gt7`'s `validate_codebase.py` pytest runs (48 workers) overlapped the whole Electron stage at about 96 % CPU. Preflight matched attempt 1. The evidence is preserved at `C:/Temp/av-kit/keep/c13a0056c1f27aaca6e1a7ce9a77ec7c78d9a57f-attempt2/`.
- **Not caused by Session 29's diff:** W1-8 is a Downloader spec, and Session 29 changed no Downloader code; the shared `Disclosure` renders unchanged with default props (AC-65.6). W1-8 passed in attempt 1 and in the container pre-gate on the same code (1.3 s).
- **The options offered:** attempt 3 unchanged on a quiet machine (recommended); accept attempt 2 as-is; or harden W1-8 first. The user chose:

> Harden W1-8 first — "Treat it as a flaky test: raise its timeout or add a settle wait, then run attempt 3. Widens Session 29 into Downloader tests without evidence that the test, not the load, is at fault."

**TA-3** (the only change; `ui/tests/e2e/download-queue.test.ts`, W1-8 only):
1. `test.slow()` triples this test's budget, from 60 s to 180 s.
2. The two one-shot `expect(await seam.callsTo(…)).toHaveLength(1)` reads after the Retry and Cancel clicks become `expect.poll(…).toBe(1)`, with the same expected counts. A single read can run before the click's fetch is logged.

No assertion, expected value or product file changes.

**Container evidence:** W1-8 `--repeat-each=10` with 8 CPU-bound processes on 4 cores.
- **Before TA-3:** 10/10 passed, but one run took 32.3 s against a median of 2.4 s (`s29-a6-before.json`). That long tail is consistent with the Windows timeout under load.
- **After TA-3:** 10/10 passed, slowest 2.9 s, now against a 180 s budget (`s29-a6-after.json`).
- This shows the margin; it cannot prove the Windows host's behaviour. Attempt 3 does that.

**CAPTURE_LOOK carry-over (logged decision D-29, MEU-66 handoff).** TA-3 changes only an Electron test file. `ui/src` is byte-identical to `c2452aa`, the code Mat's attempt-2 look ran on (all six items pass), so that look is reused for attempt 3 rather than repeated.
