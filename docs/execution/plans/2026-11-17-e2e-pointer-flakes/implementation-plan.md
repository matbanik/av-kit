---
project: "2026-11-17-e2e-pointer-flakes"
date: "2026-11-17"
source: "grouping .agent/context/grouping/2026-11-17-value-triage-session-grouping.md §3 Session 91; issues DOWNLOAD-QUEUE-DRAG-OVER-MISS, CAPTURE-ZOOM-PAN-ORIGIN-FLAKE and CAPTURE-E2E-LAUNCH-TEARDOWN-HANG, with Session 90's failing specs folded in (D-1126, D-1132)"
meus: []
status: "draft"
template_version: "2.3"
grouping_source: ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md"
---

# Implementation Plan: settle the pointer specs and trace the launch hang under load

> **Project**: `2026-11-17-e2e-pointer-flakes`
> **Build Plan Section(s)**: none. This is test-harness debt with no MEU (grouping D-1132), in the style of Session 78 `2026-11-15-e2e-harness-hardening` and Session 90 `2026-11-17-test-run-reliability`. The FIC below numbers its criteria `AC-1` to `AC-15`, with no MEU prefix. If row 7 finds a race in the product, that race is registered as an MEU (grouping `:94`) and fixed in its own session.
> **Status**: said to execute (USER_EXPLICIT 2026-11-17 "orchestrate the plan creation for all sessions and proceed with execution for each", and USER_EXPLICIT 2026-11-18 "Why do you keep stopping for each of the decisions even after I expelictly told you to make the decisions always the recommenations. If you do not believe you can make the decisions run HDP and take recommenations from that!"). Written at `HEAD` `ecfa3f3` (`epf91-probe.txt`). `plan_to_exec_gate: human`: the 2026-11-17 message is the execution approval once the plan review approves; the plan review was approved at round 3 (.agent/context/handoffs/2026-11-17-e2e-pointer-flakes-plan-critical-review.md), after Mat relieved the task-row-completion-predicate mechanism stop on 2026-11-18 ("yes run it from me"). Nothing in this plan waits for Mat: every decision is taken on its recommendation. A stop is held only for a destructive or irreversible step, a push, or user data. By D-1142 the queue runs Sessions 74, 92, 93 and 94 first; this session runs last, after Session 94 is committed.

## Goal

**Goal anchor.** The three Electron load flakes and the specs folded into them pass on a busy host. That means full Electron runs on a host held at a median load of at least 60 %, with zero failures in the watched specs, zero test-timeout hangs except those excused by a signature this session registered, zero unhandled rejections and zero diagnostics errors. If row 3's isolated watched runs showed zero failures, the proof is five full runs; otherwise it is three full runs plus ten repeats of the eleven watched tests under the same load, all passing.

Every fix waits on a real condition:

- a layout read that holds still,
- a hit-test that lands on the target,
- the app's own announcement,
- or an attribute the drag changes.

No retry, no raised timeout and no new fixed sleep is added. No existing assertion line changes. No file under `ui/src/`, `packages/`, `mcp-server/` or `tools/` changes.

The launch hang gets launch and close phase lines and a main-process event log, so each hang names the phase it stopped in. If a hang has a cause outside the specs, it is registered with a signature and split out, and acceptance excuses only a hang that matches that signature (D-1150). Scripts and tests prove all of this. There is no manual check.

**Why.**

- **`DOWNLOAD-QUEUE-DRAG-OVER-MISS`** (`known-issues.yaml:971`).
  - The drag specs miss their drop target under full-suite load: either the press misses the handle, or the drop lands one row short.
  - The root cause records "A-4 diagnostics show human input on the window, A-7": a real cursor over the window moves the drag.
  - The blast radius names transcript-queue W2-5 too. At `ecfa3f3` that spec has no mouse drag, so it stays out of scope and is only read.
  - Session 90's folded specs `download-queue.test.ts:1319` (AC-49.25) and `convert-queue.test.ts:1182` (AC-49.29) belong here (D-1126).
- **`CAPTURE-ZOOM-PAN-ORIGIN-FLAKE`** (`:1010`). Under load, the zoom origin read after a pan was 92 px off. The read came one frame before the pan's layout settled. The folded specs are:
  - `capture-inbox.test.ts:1601` (AC-67.20 A-6)
  - `:1658` (AC-80.10)
  - `:2001` (AC-81.14)
  - `:3496` (AC-143.29)
- **`CAPTURE-E2E-LAUNCH-TEARDOWN-HANG`** (`:2904`).
  - Under host load ("other agent sessions starting their MCP servers") a capture spec hits `Test timeout of 60000ms exceeded`, then `Worker teardown timeout`.
  - The issue's notes give the next step: "log host process starts during the Electron stage and time launch and close in the capture-inbox fixture".
  - AC-67.24 (`capture-inbox.test.ts:1572`) and AC-67.35 (`:1623`) were seen earlier.
  - `:1948` (AC-81.11, two launches and a PowerShell hotkey holder) is folded in.

**Grouping §3 Session 91** (grouping `:88-97`):

- **Order** (`:93`): reproduce under load first, then the drag overshoot, then the pointer origin, then the launch hang.
- **Gate** (`:94`): "no retries and no raised timeouts; a fix waits on a real condition. Any assertion change is named in the plan (M-7). If a race is in the product, the plan registers an MEU for it."
- **Split flag** (`:97`): "yes, if reproduction shows the launch hang has a separate cause; it then becomes its own session".
- **Calibration:** Session 90 and Session 78.

Mat, 2026-11-16: "This should be done with framework and scripts!", so nothing in this plan is a manual check.

**What the code shows** (plan-time reads at `HEAD` `ecfa3f3`, `epf91-probe.txt`):

- **The download drag helpers** (`download-queue.test.ts`, LF, 1695 lines):
  - `handleOf` `:1082`
  - `settledCenter` `:1098-1125`: a 60-frame loop that returns a transform-corrected centre once two frames agree, and throws `layout never settled for the drag target` otherwise.
  - `rowTransitionsIdle` `:1128`: a `waitForFunction` over `getAnimations()` on `[data-testid="queue-card"]`.
  - `windowSettled` `:1149`:
    - waits for visibility;
    - waits for full-rate frames, with a `15_000` deadline;
    - waits for a 500 ms resize quiet, using two `window.setTimeout(` calls.
  - `grabRow` `:1204`:
    - waits for `windowSettled`, then `settledCenter`;
    - moves, presses, then moves +14 px in 5 steps;
    - waits for `aria-pressed="true"` on the handle.
  - `dragOver` `:1224`:
    - reads the order from `data-job-id`;
    - moves in 10 steps, then waits for `rowTransitionsIdle`;
    - re-aims;
    - waits for the live region to hold `moved to position ${position} of ${order.length}.`, with the A-4 diagnostics in its catch (`:1264`).
  - `liveRegion` `:1269`.
- **The convert drag** (`convert-queue.test.ts`, LF, 1584 lines). AC-49.29 at `:1182-1228` does not use those helpers:
  - It reads a raw `handle.boundingBox()` (`:1200`) and `target.boundingBox()` (`:1205`), each followed by an `if (... === null) throw`.
  - It moves, presses, moves +14 px in 5 steps, moves to the target in 10 steps, and releases at `:1214`.
  - It never waits for the press to register or for the drop to commit.
  - Its expectations are `:1221` (`expect(puts).toHaveLength(1)`), `:1222`, `:1223-1225` and `:1226` (`expect.poll`).
  - The convert list is the same `QueueList` with `rowTestId="convert-queue-row"` (`ConvertPage.tsx:938`; `QueueList.tsx:75`, default `'queue-card'` at `:162`). Its rows carry `data-job-id` (`:325`), and its announcements come from the same `createQueueAnnouncements(` (`:367`). So the download helpers fit it with the row test id as a parameter.
- **The capture pointer sites** (`capture-inbox.test.ts`, LF, 3739 lines):
  - `windowSettled` `:787-828` is the same code as the download copy, without comments.
  - `readZoom` `:943` waits for `twoFrames` (`:830`) and then reads the surface's `data-zoom-*` attributes and rect once.
  - AC-66.14 (`:1159`) reads at `:1169` and `:1174` and asserts `expect(view.ox).toBeCloseTo(centred.ox - 40, 3)` at `:1175`. AC-81.14 has the same pair at `:2010`, `:2015` and `:2016`.
  - AC-81.14 then grabs the arrow head with `toHandle.boundingBox()`: mouse down, move +20, mouse up at `:2067`. It reads `ends()` at once (`:2068`) and asserts x2 at `:2069`, with nothing between the release and the read.
  - AC-67.20 A-6 (`:1601`) reads `applyButton.boundingBox()` at `:1613` and moves to it at `:1615`.
  - AC-80.10 (`:1658`) hovers `capture-tool-arrow` at `:1678`, waits `HINT_DELAY_MS` (400, `:13`), and later reads the Undo box (`:1693`).
  - `dragImage` (`:2552`) reads `surface.boundingBox()` once at `:2554`. AC-87.6 (`:2566`) and AC-143.29 (`:3496`, at `:3515` and `:3517`) reach it.
  - No one of these sites checks that the pointer's point hits the target before it presses.
- **The launch path** (`electron-app.ts`, LF, 97 lines):
  - `launchElectron` `:70` is the one `_electron.launch` site (`:76`).
  - The wrapped close `:88` runs `close()`, then waits `EXIT_WAIT_MS` (5 000 ms, `:26`), then runs `checkMainErrors` (`:46`), which is Session 90's rejection watch.
  - Nothing records when a launch or a close starts or ends. When a test times out, the receipt cannot tell a slow launch from a stuck body or a stuck close.
- **The harness pins** (`ui/tests/unit/e2e-harness.test.ts`):
  - `:60`: only `electron-app.ts` under `ui/tests/e2e/` may hold the text `_electron`, and it names `_electron.launch(` once.
  - `:66`: `electron-env.ts` spreads `...process.env` at most once.
  - `:121-130`: `requireScratchAppData(env` appears once.
  - The new files therefore never hold `_electron`.
- **No E2E spec drives real OS input.** There is no `SendInput`, `mouse_event`, `SetCursorPos` or `keybd_event` under `ui/tests/`, and no `setIgnoreMouseEvents` or `browser-window-created` anywhere under `ui/`. Playwright's mouse goes through CDP `Input.dispatchMouseEvent`, which the renderer takes directly, without OS hit-testing. A window that ignores OS mouse input therefore still takes the spec's pointer, and Mat's real cursor passes through it (D-1149, AC-9).
- **Versions:** `electron ^42.5.0`, `@playwright/test ^1.58.2`, `@dnd-kit/core ^6.3.1`, `vitest ^5.0.5`. `ui/playwright.config.ts` sets `timeout: 60_000` and `workers: 1`, and is not changed.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls, 2026-11-17). The change touches three E2E spec files and the E2E launch file, all read at the cited lines at plan time, plus four new test-side files; that is a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`.agent/docs/harness-profiles.md`, the Claude Code block of `.agent/context/harness.local.md`).
  - **Commands and receipts:**
    - Validation goes through `rtk proxy` with the receipt pattern `> receipt 2>&1`. Task-cell commands run in pwsh.
    - Receipts go under `C:/Temp/av-kit/e2e-pointer-flakes/` and are named `epf-*`. Planning receipts are named `epf91-*`.
  - **Environment:**
    - Every row sets `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`, and clears `ELECTRON_RUN_AS_NODE` (Session 88 RULE-3).
    - Vitest runs from pwsh after `Set-Location 'P:\av-kit\ui'`, never from the Bash tool, and returns to `P:\av-kit`.
  - **Host load:**
    - Before any gate or Electron run, the host load is at most 50 % (`flake-run.py`'s host-load wait; Session 81 RULE-2). A load still above 50 % after the 10-minute wait is exit 2 (S8).
    - The busy children that `flake-run.py` starts on purpose, and the one process-churn child at row 3, are the only load this session adds.
    - Eighteen busy children give about 75 % load on their own, so the 60 % median floor proves only that the children ran, not that the load came from elsewhere.
  - **Processes:**
    - Each Electron test stops only the app it launched, through the harness close.
    - `flake-run.py` stops only its own busy children, through their handles, and a timed-out Playwright tree only by the node pid it recorded.
    - No row stops a process by image name. Other worktrees run their own apps, and ShareX or any other program is never stopped.
- **Working directory:** `P:/av-kit` on `main`. There are no branches or worktrees. `.agent/fleet/hub` and every other worktree are left alone.
- **Cloud-local contract:** local (Electron E2E on a loaded host; grouping §3 "Cloud/local: local").
- **Reviewer:** Codex `avkit_independent_reviewer` through `tools/Invoke-CodexDispatch.ps1`, run by the coordinator with `AGENT_MODEL_REGISTRY_HOME='P:/.agent'`.
  - **Ledger loops:** `epf-plan-2026-11-17-e2e-pointer-flakes` and `epf-execution-2026-11-17-e2e-pointer-flakes`.
  - **Caps:** from `.agent/review-limits.json`: plan 3 rounds, execution 6, token budgets off. This plan carries no `review_limits` block.
  - **Vendor:** Claude wrote the plan, so the reviewer comes from a different vendor. If a dispatch fails, it is retried once; after that the review stays pending and the coordinator re-dispatches it (S6).
  - **Logs:** each dispatch writes its own run log, and the console output goes to a separate console file (Session 88 RULE-2).
- **Queue:** Session 74 runs before this session. It should not touch `ui/tests/e2e/`, and row 0 checks that it did not. Sessions 92, 93 and 94 follow; Session 94 adds E2E specs after this session's commit (grouping `:68-72`). The baselines are bound to content at row 0 (§Verification Plan 1).
- **Never in these rows without Mat's words:** commit, push, or writing an `approved` verdict. Mat pushes himself.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| The three issues and the folded specs (no MEU) | `.agent/context/handoffs/2026-11-17-e2e-pointer-flakes-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-17-e2e-pointer-flakes-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-17-e2e-pointer-flakes-implementation-critical-review.md`

The session has one handoff, following the no-MEU precedent `2026-11-15-e2e-harness-hardening-handoff.md`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline, copied checkers, assertion snapshot, list total (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-eol.json`, `baseline-skip-hashes.json`, `red-check.py`, `identity.py`, `issue-resolve.py`, `eol-check.py`, `epf-base-total.txt` |
| WP-2 | Red, then Green, for the helpers and the diagnostics (rows 1 and 2) | WP-1 | shared | `pointer-settle.ts`, `e2e-diag.ts`, `electron-app.ts`, `e2e-pointer.test.ts`, `e2e-diag.test.ts` |
| WP-3 | Reproduction under load on the unfixed specs (row 3) | WP-2 | shared | `epf-repro-*`, `epf-base-full-*`, `epf-burn-level.txt` (with `accept-runs:`) |
| WP-4 | The drag fix, then the capture origin fix, each with a measurement (rows 4 and 5) | WP-3 | shared | The three spec files; the `epf-drag-*` and `epf-origin-*` receipts |
| WP-5 | The shield on by default, then the launch-hang verdict (rows 6 and 7) | WP-4 | shared | `electron-app.ts`; `epf-shield-*`; `epf-hang-verdict.txt`; `epf-hang-signatures.json`; a registered MEU and issue only if D-1150 calls for them |
| WP-6 | Acceptance under load (row 8), then registers and the grouping row (row 9) | WP-5 | shared | `epf-accept-*`; `epf-watch10-*` only when `accept-runs` is 3; the issues; grouping row 91 |
| WP-7 | Closeout (H1, H2) | WP-6 | `compact_continue` | The handoff, the review, the reflection |

## User Review Required

> [!NOTE]
> **Nothing here needs your ruling, and nothing waits for you.**
>
> Four decisions are briefs (§Decision Log):
>
> - D-1145: what proves the flakes are gone
> - D-1146: how they are reproduced first
> - D-1149: shielding the test windows from your real mouse
> - D-1150: what happens if the launch hang has a cause outside the specs
>
> Your words of 2026-11-18 ('Why do you keep stopping for each of the decisions even after I expelictly told you to make the decisions always the recommenations. If you do not believe you can make the decisions run HDP and take recommenations from that!'), continuing the hand-over of 2026-11-17 ('orchestrate the plan creation for all sessions and proceed with execution for each') and 2026-11-15 ('like we did here. But use the new HDP process.'), settle every brief on its recommendation, and they are recorded that way. A fresh-context expert pass changed all four briefs, and its changes are adopted (§Decision Log). Read them if you want to overrule one before execution.
>
> **One conflict to know about.** D-1150 hits M-11, the run-scope gate, because `--split-hang` lets acceptance excuse a hang. HDP §6 (`human-decision-protocol.md:328-329`) keeps an M-11 item with you even under a hand-over. The coordinator directed, under your 2026-11-18 words, that it be decided on its recommendation too, and the plan records it that way. One line from you overturns it.
>
> There is no human check row: tests and scripts prove each change, and so does the gate.
>
> There is no stop that waits for you. Where the plan used to stop for you (an unhandled rejection, a shield that cannot be verified, an assertion that would have to change, a hang in acceptance), it now records the evidence, registers an issue where one is due, and takes an execution decision (D-1152 to D-1154) on the HDP recommendation. The holds that stay with you are a destructive or irreversible step, a push, and any read or write of your data.
>
> **What changes for you:**
>
> - The Electron suite stops failing on the drag and capture specs when the machine is busy. Session 90 saw them fail 3 of its 7 full runs, so every later gate needed a rerun.
> - While an E2E run is going, its app windows ignore your real mouse: the pointer passes through to whatever is under them. The tests' own pointer still works. A spec can opt out with `pointerShield: false`. The keyboard is not blocked. A click that passes through can raise the window beneath the test window; the visibility log shows when that happens.
> - When a spec hangs, the receipt now says where. Each launch writes when it started, when it was up, when its close began and when the process exited. The main process logs its window moves, resizes, focus changes, minimize and visibility changes, and cursor entries. The host's process starts during the run are listed beside them.
> - If the launch hang turns out to have its own cause (a slow launch or close, or a race in the app), it is registered with a signature (file, line, test title and phase) and gets its own session instead of a workaround here. Acceptance excuses only a hang that matches a registered signature, and the handoff lists every one it excused.

## Proposed Changes

### Single-statement contracts

- **`SETTLE` (D-1148).**
  - `ui/tests/e2e/pointer-settle.ts` exports `settle<T>(read: () => Promise<T>, nextFrame: () => Promise<void>, maxFrames = 60): Promise<T>`.
  - It calls `read`, then `nextFrame`, then `read` again. It returns the second value as soon as two reads in a row are equal by `JSON.stringify`.
  - It throws `Error('layout never settled: ' + <last value as JSON>)` after `maxFrames` reads that never repeat.
  - The 60-frame bound is the one `settledCenter` (`download-queue.test.ts:1098-1125`) already uses. No wall-clock timeout is added.
- **`POINTER_SETTLE_TYPES_ONLY`:** `pointer-settle.ts` imports only types from `@playwright/test` (`import type`), so the unit test can load it in Vitest.
- **`SETTLED_BOX`:** `settledBox(page, locator)` returns `settle(() => locator.boundingBox(), <one rAF in the page>)`: a `Box` or `null`, read once the box has held still for one frame.
- **`POINTER_ON`:** `pointerOn(page, locator)` returns the centre of `settledBox`. Before it returns, a `page.waitForFunction` checks frame by frame that `document.elementFromPoint` at that point is the target, an ancestor of it, or a descendant of it. If the box is `null`, it throws `Error('no box for the pointer target')`. Nothing is clicked or moved.
- **`POINTER_HELPERS_SHARED` (D-1147).**
  - `settledCenter`, `rowTransitionsIdle`, `windowSettled`, `grabRow` and `dragOver` move once, unchanged in logic, from `download-queue.test.ts` into `pointer-settle.ts`.
  - Each queue helper takes an options object `{ rowTestId = 'queue-card' }`. It builds its row selector from that, and its row-handle and live-region locators locally.
  - `download-queue.test.ts` imports them and keeps its own `handleOf` and `liveRegion` for its other tests.
  - `capture-inbox.test.ts` deletes its identical `windowSettled` (`:787-828`) and imports the shared one.
- **`DRAG_DRIVER_SHARED`.**
  - Convert AC-49.29 (`convert-queue.test.ts:1182`) drives its drag with `grabRow` and `dragOver` and `{ rowTestId: 'convert-queue-row' }`, then `page.mouse.up()`.
  - This replaces `:1199-1214`. The raw `boundingBox()` reads, their two `throw` lines and the manual moves go away.
  - The drag now waits for the press to register and for the committed-over announcement before it releases, as the download drags do.
  - The test's expectations at `:1221-1226` are kept, byte for byte.
- **`SETTLED_ZOOM`.**
  - `capture-inbox.test.ts` adds `settledZoom(page)`, which returns `settle(() => readZoom(page), async () => undefined)`. `readZoom` waits two frames itself.
  - AC-66.14 (`:1169`, `:1174`) and AC-81.14 (`:2010`, `:2015`) read through it.
- **`GRAB_COMMITTED`:** in AC-81.14, after `page.mouse.up()` (`:2067`) and before `const grabbed = await ends()` (`:2068`), a `page.waitForFunction` waits until the arrow line's `x2` attribute differs from `before.x2`. A grab that never moves the head now ends as a test timeout instead of a wrong x2. This is named in §Test pins.
- **`POINTER_SITES`:**
  - AC-67.20 A-6 (`:1613`) reads `settledBox` and then waits for `pointerOn` on the Apply button before the move at `:1615`. The line `expect(box).toBeTruthy()` (`:1614`) is kept.
  - AC-80.10 waits for `pointerOn` before the arrow hover (`:1678`) and before the Undo move. Its `waitForTimeout(HINT_DELAY_MS)` calls stay as they are: they are the product's hint delay, not a settle.
  - `dragImage` (`:2552`) reads `settledBox` at `:2554` and keeps `:2555`.
- **`DIAG_DIR`:** `ui/tests/e2e/e2e-diag.ts` exports:
  - `DIAG_DIR_ENV = 'AVKIT_E2E_DIAG_DIR'`;
  - `diagDir(env = process.env): string | null`, which gives the folder or `null` when the variable is unset or empty;
  - `RUN_ID_ENV = 'AVKIT_E2E_RUN_ID'` and `runId(env = process.env): string`, which gives the run id `flake-run.py` set for this run, or `''` when the variable is unset.

  With `null`, no diag line is written anywhere. `e2e-diag.ts` imports nothing from `@playwright/test`.
- **`PHASE_LINES`.**
  - `e2e-diag.ts` exports `phaseLine(dir, row)`, which appends one JSON line `{ t, phase, run_id, file, line, title, repeat, test_status, test_errors, launch, main_log }` to `<dir>/phases.jsonl`.
  - `launchElectron` writes the phases `launch-start`, `launch-end`, then `evaluate-end` or `evaluate-error`. The wrapped close writes `close-start`, `close-end` (after `close()`) and `exit` (after the exit wait, before `checkMainErrors`).
  - The fields:
    - `t` is `Date.now()`;
    - `run_id` is `runId()`. `flake-run.py` sets `AVKIT_E2E_RUN_ID` to `<inv>-<i>` for run `i` of invocation `<inv>`, so each line names the one run that wrote it, and `flake-run.py` reads only lines that carry its own run id (plan review round 2, F3);
    - `file` is the bare file name of `test.info().file` (`path.basename`), and `line` is `test.info().line`: the spec file and the line the failure header prints for the test;
    - `title` and `repeat` come from `test.info()`. `file`, `line`, `title` and `repeat` are read in one `try`, or are `''`, `0`, `''` and `0` outside a test;
    - `test_status` is `test.info().status` and `test_errors` is `test.info().errors.length`, read in the same `try` when the line is written, or `''` and `0` outside a test. Playwright 1.64.1 sets the status to `'timedOut'` and pushes the error the moment the test timeout fires, while the body still runs (`workerProcessEntry.js` `_failWithError`, called from `_runWithTimeout`). So a `close-start` written by a `finally` after a body timeout reads `'timedOut'`. This is the test's own timeout state at close entry, which row 7 and `flake-run.py` read instead of a clock inferred from the first launch;
    - `launch` is the integer `process.pid * 1000 + n`, where `n` is the worker's launch counter;
    - `main_log` is `main-<launch>.jsonl`.
  - `electron-app.ts` imports `test` beside `_electron`, in the same import line.
- **`MAIN_DIAG`.**
  - `e2e-diag.ts` exports `installMainDiag(electron, { file, shield })`. The function is self-contained: it takes `fs` from `process.getBuiltinModule('node:fs')` and closes over nothing.
  - `launchElectron` runs it with `app.evaluate(installMainDiag, { file: <dir>/<main_log>, shield })`.
  - It appends one JSON line `{ t, event, ... }` per event to `file`:
    - `install`, with every window's bounds;
    - per window: `show`, `hide`, `resize`, `move`, `focus`, `blur`, `minimize`, `restore`;
    - `display` (added, removed or metrics changed);
    - `cursor-inside` and `cursor-outside`, on a change of whether `screen.getCursorScreenPoint()` lies inside any window's bounds. A 250 ms `setInterval` checks this; it is `unref`'d and cleared on `will-quit`;
    - `visibility`, with `state`, on a change of a window's `document.visibilityState`. The same 250 ms interval reads it through `webContents.executeJavaScript('document.visibilityState')`; a rejected read is skipped, not logged as a change;
    - `before-quit`, `will-quit` and `quit`.
  - Windows created later are hooked through `app.on('browser-window-created')`.
  - It never calls `setBackgroundThrottling(false)`. That call would change how the app renders under test, and the point of the log is to see the app as it runs.
- **`DIAG_DEFAULT_MAIN_ONLY`:** the evaluate runs only when `main` is undefined (the built app), so `electron-harness.test.ts:100`'s `STARTUP_MAIN` launch is unchanged.
- **`EVALUATE_ERROR_KEPT_GOING`:** if the evaluate throws, `launchElectron` writes `evaluate-error` with the message and returns the app as before. A run counts any `evaluate-error` against AC-13.
- **`POINTER_SHIELD` (D-1149):** with `shield: true`, `installMainDiag` calls `setIgnoreMouseEvents(true)` on every window in `BrowserWindow.getAllWindows()`, and on each window that `browser-window-created` delivers. Real OS mouse input passes through the app's windows; Playwright's CDP input still reaches the page. The keyboard is not blocked. A click that passes through can raise the window beneath; the `visibility`, `blur` and `minimize` lines name it when it happens. `launchElectron`'s default is `false` from row 2 to row 5 and `true` from row 6 on.
- **`SHIELD_OPT_OUT`:** `LaunchOptions` gains `pointerShield?: false`. With `false`, `installMainDiag` gets `shield: false` and the diagnostics still run.
- **`ASSERTIONS_KEPT` (D-1151):**
  - In each of the three spec files, the multiset of stripped lines that hold `expect(` or `expect.` equals its row-0 copy.
  - The `test(` title lines are unchanged and in order.
  - `assert-check.py` checks both. An added wait is a `waitForFunction` or `waitFor`, never a new `expect(`.
- **`NO_NEW_WAIT_KNOBS`:**
  - Across the spec files, the three harness files and the four new files, no `BANNED` token (`assert-check.py`) is counted more often than across the row-0 copies of the spec and harness files. The tokens are `retries`, `waitForTimeout(`, `setTimeout(`, `test.slow`, `repeatEach`, `timeout:`, `Timeout =` and `sleep(`.
  - Moving the duplicated `windowSettled` into one shared copy lowers the count.
  - The new files pass no `timeout:` option, with one named exception: AC-9's `spawnSync` in `e2e-diag.test.ts` takes `timeout: AC9_SPAWN_TIMEOUT_MS`, from `const AC9_SPAWN_TIMEOUT_MS = 30_000`, so a stuck child cannot hold the test. `assert-check.py`'s `ALLOWED_TIMEOUT` allows that one text once, in that file only.
- **`CONFIG_KEPT`:** `ui/playwright.config.ts` is byte-identical to row 0.
- **`EXIT_WAIT_KEPT`:** `electron-app.ts` still holds `const EXIT_WAIT_MS = 5_000`.
- **`REJECTION_WATCH_KEPT`:** `main-error-watch.cjs` and `electron-env.ts` are byte-identical to row 0, and `checkMainErrors` is unchanged. Session 90's rejection watch stays on.
- **`PRODUCT_UNCHANGED`:** no file under `ui/src/`, `packages/`, `mcp-server/` or `tools/` changes. A product race goes through D-1150.
- **`NO_LAUNCHER_NAME`:** none of `pointer-settle.ts`, `e2e-diag.ts` or `e2e-diag.test.ts` holds the text `_electron` (`e2e-harness.test.ts:60`). `e2e-diag.test.ts` loads `electron-app.ts`, `pointer-settle.ts` and `e2e-diag.ts` through dynamic imports after an `existsSync` assertion, as `electron-harness.test.ts:16-21` does.

### Helpers and diagnostics (rows 1 and 2)

- **Row 1** writes the two test files and changes nothing else.
- **Row 2** writes `pointer-settle.ts` (only `settle`, `settledBox` and `pointerOn` at this point) and `e2e-diag.ts`. It adds `PHASE_LINES`, `MAIN_DIAG`, `DIAG_DEFAULT_MAIN_ONLY`, `EVALUATE_ERROR_KEPT_GOING` and `SHIELD_OPT_OUT` to `electron-app.ts`, with the shield default `false`.
- **At row 2's end:**
  - AC-1, AC-2, AC-3, AC-4, AC-8 and AC-10 pass.
  - AC-6 and AC-7 still fail. Their static reads wait for rows 4 and 5.
  - AC-9 still fails until row 6.

### Reproduction (row 3)

`flake-run.py` is written and selftested at plan time (122 checks, `epf91-selftest-flake-run.txt`), and its busy-child stop was checked live, with and without the churn child (`epf91-killcheck.txt`, `epf91-killcheck-churn.txt`).

On the tree at row 2's end, with the spec files still unfixed, row 3 runs two things:

- the eleven `WATCHED` tests ×10 (`--mode watched --repeat 10 --runs 1 --churn --label repro`);
- one full run (`--mode full --runs 1 --churn --label base-full`).

Both run with the default 18 busy children and one process-churn child (`--churn`: short `node -e 0` and `pwsh -NoProfile -Command exit` starts in a loop). The churn child stands in for the hang hypothesis on record: other sessions starting their MCP servers (`known-issues.yaml:2910` root cause, `:2923` notes). Exit 0 and exit 1 are both measurements. Exit 2 is S8; it also covers a host load still above the ceiling after the wait and a churn child that died during the run. If both show zero watched failures and no hang, the two runs are repeated once with `--children 24` (`repro24`, `base-full24`; D-1146). If 3 or more failures outside the watched set then occur (uncovered specs, plus hangs in specs that are not watched), the level goes back to 18 and that is recorded. `epf-burn-level.txt` records the level that rows 4, 5, 6 and 8 use, and `accept-runs: 5` when the watched receipts show zero failures, else `accept-runs: 3` (AC-5, D-1145).

### The drag fix (row 4)

Row 4 applies `POINTER_HELPERS_SHARED` and `DRAG_DRIVER_SHARED`, then measures with the watched specs ×10 at the burn level (`--label drag`). The measurement records the counts. It is not the acceptance.

### The capture origin (row 5)

Row 5 applies `SETTLED_ZOOM`, `GRAB_COMMITTED` and `POINTER_SITES`, and imports the shared `windowSettled`. It then measures the same way (`--label origin`).

### The shield (row 6)

Row 6 sets the shield default to `true`. AC-9 now passes and AC-10 still passes. It then runs the watched tests ×10 at the burn level with the shield on (`--label shield10`), as a measurement. If AC-9 fails, that is S11.

### The launch hang (row 7)

Row 7 reads every hang that rows 3 to 6 recorded:

- the failure blocks marked `hang` in the `epf-repro-*`, `epf-base-full-*`, `epf-drag-*`, `epf-origin-*` and `epf-shield10-*` receipts;
- the `diag:` summary of each block: the last phase per launch, the event counts and the host process starts.

It writes `epf-hang-verdict.txt`. That file holds one block per hang: the title, the receipt, the last phase of each launch with its `test_status` and `test_errors`, a `signature: <file>:<line> <phase> <title>` line (the file and the title exactly as the failure header prints them), a `cause:` line and a `register:` line. The register change is decided per block, not once for the session. A final line `outcome: <one of in-spec, product-race, split, not-reproduced>` gives the session's outcome, which is the worst outcome of any block, in that order; row 9 reads it. It also writes `epf-hang-signatures.json`: one entry per `product-race` or `split` block, in the format `flake-run.py --split-hang` reads (its docstring point 4), and `[]` when there is none. Then D-1150 applies, block by block:

- **`in-spec`:** the hang stopped in a test body, and the cause is in the spec. An example is AC-81.11's hotkey holder (two launches, a PowerShell `Add-Type` compile and its `expect.poll` 5 s waits, all inside one 60 s test).
  - The fix is made here, within the contracts above: wait on the real condition the diag names.
  - If no fix fits the contracts (it would need a timeout, a hook, a new test structure or an assertion change), that is an execution decision taken through HDP (the next free id of D-1152 to D-1154). Its default registers the block as a `split` block with its signature, and no contract is broken.
- **`product-race`:** the diag shows a race in `ui/src`. Examples: a window that reports `show` before it can take input, or a close that waits on a renderer that never answers.
  - Row 7 registers the next free MEU (MEU-160 at plan time, `epf91-probe.txt`) with `meu-register.py`, written at row 7 in the shape of the 2026-11-17 Stage A registration: one anchored edit per file, endings kept. The files are:
    - `.agent/context/meu-status.yaml` (LF);
    - the owning `docs/build-plan/<area>.md` (CRLF);
    - `docs/build-plan/build-priority-matrix.md` (CRLF).
  - It then runs `meu_status.py render` and `render --check`.
  - It also adds one issue with `tools/issue_triage.py add`, then runs `render` and `render --check`.
  - It writes a `product-race` entry with that issue id and that MEU id to `epf-hang-signatures.json`. Grouping `:94` asks for the MEU, so the drag and zoom fixes are not held by a race this session has registered: acceptance excuses a hang with that exact signature, even in a watched spec.
  - The fix itself is split out to its own session.
- **`split`:** the hang stopped inside a launch or a close with nothing in the specs to fix, for example a launch that took the whole 60 s on a loaded host. The test's final launch in that run (the launch whose last line is the latest; every earlier launch of the test reached `exit`) has the last phase `launch-start` or `close-start`, and that phase line reads `test_status` `'passed'` with `test_errors` `0`: the test had not timed out or failed when the launch or the close began. A last phase of `launch-end` is not split: the app was up and the test body ran, so the hang is in the spec or the app. A `close-start` that reads `'timedOut'`, or any error, is not split either: the body hung or failed and the `finally` close came after it. The `finally` close at `capture-inbox.test.ts:1953` (AC-81.11's second launch) is split only under that rule. The rule reads the test's own state, not a clock from the first launch, so setup before the launch cannot move a body timeout inside the window (plan review round 1, F2). A missing or mistyped `test_status` or `test_errors` is never split.
  - Row 7 adds one issue for it, and `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` is narrowed in its `notes`.
  - It writes a `split` entry with that issue id, the block's spec file name and its exact test title, and the phase, to `epf-hang-signatures.json`.
  - Row 8 runs with `--split-hang`, so a hang that matches the signature is printed, counted and listed but does not fail acceptance. A split entry excuses only a hang in that same file with that same title (plan review round 1, F1): a hang in another file, or in another test of the same file, is never excused by it. A split entry never excuses a hang in a watched spec (grouping `:97`).
  - **The evidence binding (plan review round 2, F3).** An excuse rests only on the failing test's own final launch, in this run, of this invocation of `flake-run.py`. Nothing else in a folder can excuse a hang:
    - Each invocation takes a new id `<inv>` (time, pid and six random hex digits) and prints `invocation: <inv>`.
    - Run `i` writes `epf-<label>-<i>-<inv>.txt` and the diag folder `epf-<label>-<i>-diag-<inv>`, and sets `AVKIT_E2E_RUN_ID` to `<inv>-<i>`. It prints `run <i> files: receipt R diag D run_id ID` before Playwright starts.
    - The folder is created with no `exist_ok` and the receipt is opened exclusive. A folder or receipt already there is a setup failure (exit 2) before Playwright starts, so no line is ever appended across invocations.
    - The solo rerun of RULE-3 and the host-process file `epf-<label>-procs-<inv>.txt` are named and created fresh in the same way.
    - `diag_summary` counts a phase line for the test only when it carries this run's id and names this test: the bare file name, the line, and the title (equal to the header's title, or its last ` › ` part).
    - It counts three kinds of line: foreign lines (another run id or none, anywhere in the folder), unreadable lines (not JSON), and malformed lines of this test (a launch, repeat or `t` that is not a number, or an unknown phase).
    - An excuse needs all of these: zero foreign, unreadable and malformed lines; exactly one repeat; a final launch (the latest last line, where a tie leaves none); and every other launch of the test ended at `exit`. The final launch's last phase must equal the signature's phase, and that phase line must read `'passed'` and `0`.
    - So a registered close signature for a test cannot excuse a later body hang in that test, nor can any line from an earlier attempt, another run, another test or an earlier launch.
    - `--split-hang` with `--repeat` other than 1 is refused (exit 2), because the failure header names no repeat.
  - Known limit: an assertion thrown inside a `try` reaches Playwright only after its `finally` ends, so a `finally` close that then hangs still reads `'passed'` at `close-start`. The file, line and title identity, the run id and the watched rule bound that case to the one registered test in this run, and the hang is still printed and listed in the handoff.
- **`not-reproduced`:** no hang was seen. The instrumentation stays, `epf-hang-signatures.json` is `[]`, and `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` stays `open` with a note that names the receipts and the next step.

### Acceptance (row 8)

Row 8 reads `accept-runs:` from `epf-burn-level.txt` and runs:

- that many full runs at the burn level (`--mode full --runs <5 or 3> --label accept --expect-total <row-0 total + 4>`), with `--split-hang C:/Temp/av-kit/e2e-pointer-flakes/epf-hang-signatures.json` when that file holds entries;
- only when `accept-runs` is 3: the watched tests ×10 (`--mode watched --repeat 10 --runs 1 --label watch10`).

They run on the fixed tree with the shield on (AC-13, AC-14). Every `excused:` line in the receipts is copied into the handoff.

Row 8's check reads the `invocation:` line and the `run <i> files:` lines of `epf-accept.txt` (and of `epf-watch10.txt` when it runs). It wants:

- exactly one invocation per receipt;
- runs numbered 1 to the expected count;
- each name equal to `epf-<label>-<i>-<inv>.txt` or `epf-<label>-<i>-diag-<inv>`, and each run id equal to `<inv>-<i>`;
- every receipt, folder and invocation distinct.

It then counts `unhandled rejection:` lines and `evaluate-error` phases only in those bound files. A rerun of row 8 (S9) is a new invocation with new files, so a stale receipt or folder from an earlier attempt is never read.

### Registers and the grouping (row 9)

- **`issue-resolve.py`:**
  - It resolves `DOWNLOAD-QUEUE-DRAG-OVER-MISS` and `CAPTURE-ZOOM-PAN-ORIGIN-FLAKE` with `status: resolved`, `verification` and `resolution_path`. Each `verification` block carries `last_checked`, a `method` that names the receipts, and a `result` whose counts are copied from those receipts.
  - It resolves `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` only under the `in-spec` outcome. Under the other outcomes it updates only that issue's `notes`, and the status stays `open`.
- **Renders:** `issue_triage.py render` and `render --check`.
- **Grouping `:163`:** becomes `` | 91 | `e2e-pointer-flakes` | — | P3 | executed (Session 91) | `docs/execution/plans/2026-11-17-e2e-pointer-flakes/` | ``. No other grouping line changes.

### Test pins

Each pin is cited by its file, line and description. Session 83 RULE-1: no other family's AC ids are copied here as this plan's.

| Pin | What it checks | After this change |
|---|---|---|
| `download-queue.test.ts:1319` ("dragging a row onto the third row lands the exact order, and it survives a reload"), `:1348` ("the drag announces position-based progress"), `:1427` ("a row drag never puts the list into its file-drop state") | Drag order, the announcement, no file-drop state | Unchanged lines. The helpers they call come from `pointer-settle.ts`, with the same logic and the default `rowTestId` |
| `convert-queue.test.ts:1182` ("dragging a conversion onto the third row lands the exact order"), expectations `:1221-1226` | One PUT with the new order, then the rows in that order | Expectation lines unchanged. **The drive changes (`DRAG_DRIVER_SHARED`).** Old: raw boxes, a fixed move sequence, a release with no wait, and two `throw` lines on a `null` box. New: `grabRow` and `dragOver`, which wait for `aria-pressed="true"` and for the `moved to position 3 of 4.` announcement before the release. A press that misses, or a drop that would land short, now ends as a test timeout in the helper (A-4 diagnostics printed) instead of a `toHaveLength(1)` failure |
| `capture-inbox.test.ts:1175`, `:2016` (`expect(view.ox).toBeCloseTo(centred.ox - 40, 3)`) | The pan moved the origin by 40 px | Unchanged lines. Both reads come from `settledZoom` |
| `capture-inbox.test.ts:2069` (x2 grows by 20) | The grab moved the head | Unchanged line. **A wait is added before `:2068` (`GRAB_COMMITTED`).** Old: read at once. New: wait until x2 changes, then read. A grab that never moves the head ends as a test timeout instead of the `:2069` failure |
| `capture-inbox.test.ts:1614` (`expect(box).toBeTruthy()`), `:1618` (the hint is visible) | The disabled Apply shows its reason where the pointer lands | Unchanged lines. The move at `:1615` aims at a settled box that `pointerOn` has hit-tested |
| `capture-inbox.test.ts:1680` and the Undo hint lines in the same test | The real hover shows the hints inside the window | Unchanged lines. `pointerOn` runs before each hover. `HINT_DELAY_MS` waits stay |
| `capture-inbox.test.ts:2555` (`expect(box).toBeTruthy()`), `:3517` (`toHaveCount(1)`), and the AC-87.6 drag expectations at `:2566` onward | The surface box exists, and the drags draw boxes | Unchanged lines. `dragImage` reads `settledBox` |
| `capture-inbox.test.ts:403` (W9-7, stderr holds no `UnhandledPromiseRejectionWarning: Error: backend not ready`) | Session 90's warning line | Unchanged. `main-error-watch.cjs` is byte-identical (`REJECTION_WATCH_KEPT`) |
| `capture-inbox.test.ts:1948` (the hotkey-in-use fixture with two launches) | The banner sits in the header | Unchanged unless row 7's `in-spec` fix lands there. Such a fix is named in the handoff with its file and line and stays within the contracts (no assertion line changes, `assert-check.py`) |
| `ui/tests/unit/e2e-harness.test.ts:60` (only `electron-app.ts` names the launcher, once), `:66` (one `...process.env` spread), `:121-130` (`requireScratchAppData(env` once) | The single launch site | Unchanged and passing. The new files never hold `_electron` (`NO_LAUNCHER_NAME`), and `electron-env.ts` is not edited |
| `ui/tests/e2e/electron-harness.test.ts:50`, `:69`, `:97`, `:117`; `ui/tests/unit/rejection-watch.test.ts`; `ui/tests/e2e/main-rejection-watch.test.ts` | Session 78's exception watch and Session 90's rejection watch | Unchanged and passing in row 2 and the gate. `:100` launches `STARTUP_MAIN`, so it gets no diag evaluate (`DIAG_DEFAULT_MAIN_ONLY`) |
| **Every E2E launch of the built app** (`electron-app.ts` `launchElectron`, `:70`) | Old: the app takes OS mouse input | **New harness default (`POINTER_SHIELD`, D-1149).** New: the app's windows ignore OS mouse input, and CDP input still arrives. No spec in the suite drives OS input (plan-time grep). Proved by AC-9 and AC-10 and by the full runs of rows 8 and the gate |

A wait added in front of an unchanged expectation can turn an assertion failure into a test timeout. The three places where that happens are named above: the convert drag, the AC-81.14 grab, and the hit-test before the capture hovers. Each waits on the condition the expectation then checks, so a real fault still fails the test.

Any other existing test that fails after Green is S5. A failure that holds `unhandled rejection:` is S10.

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `<AVKIT_E2E_DIAG_DIR>/phases.jsonl`, one JSON object per line | `e2e-diag.ts` `phaseLine`, read by `flake-run.py` `diag_summary` | `t` (ms), `phase` (one of `launch-start`, `launch-end`, `evaluate-end`, `evaluate-error`, `close-start`, `close-end`, `exit`), `run_id` (`AVKIT_E2E_RUN_ID`, `''` when unset), `file` (the spec's bare file name, `''` outside a test), `line` (integer, the test's line, `0` outside a test), `title`, `repeat`, `test_status` (`test.info().status`, `''` outside a test), `test_errors` (integer, `test.info().errors.length`, `0` outside a test), `launch` (integer), `main_log`; `evaluate-error` adds `message` | Test-only; no other field |
| `<AVKIT_E2E_DIAG_DIR>/main-<launch>.jsonl` | `e2e-diag.ts` `installMainDiag` | `t`, `event` (from `MAIN_DIAG`'s list), with `bounds` or `point` where they apply | Test-only; the packaged app never runs it |
| `LaunchOptions` | `electron-app.ts` | `main?`, `env?` (unchanged), and the new `pointerShield?: false` | Test-only |

No API route, OpenAPI document, MCP tool shape, backend service, persisted setting or database schema changes, so M-4 stays clear. Nothing reads user data: the specs use a scratch `AVKIT_APP_DATA` and the fake E2E backend.

### Acceptance Criteria

- **Titles.** Vitest and Playwright titles start `AC-<n> `, the number followed by a space, so `red-check.py --require AC-1` never matches `AC-10`.
- **New names fail by assertion at Red.**
  - `e2e-pointer.test.ts` asserts `existsSync` on `pointer-settle.ts` or `e2e-diag.ts` first, and then loads it through `import(pathToFileURL(...).href)`.
  - `e2e-diag.test.ts` does the same for `pointer-settle.ts`, `e2e-diag.ts` and `electron-app.ts`.
  - So no Red fails on a missing module or export (Session 52 RULE-4).
- **The guard AC-10 passes at Red.**
- **The checks AC-5 and AC-11 to AC-15 are not test titles.** Rows 3 and 7 to 9 and the gate run them.
- **The unit file** `ui/tests/unit/e2e-pointer.test.ts` (`// @vitest-environment node`) holds AC-1, AC-2, AC-3, AC-6 and AC-7. **The E2E file** `ui/tests/e2e/e2e-diag.test.ts` holds AC-4, AC-8, AC-9 and AC-10.

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-1 | unit | `settle` with a fake `read` that yields `1, 2, 2` returns `2` after exactly three reads and two `nextFrame` calls. With `{a:1}` then `{a:1}` it returns after two reads. With a read that never repeats and `maxFrames = 5` it rejects with `layout never settled:` after five reads. | Local Canon (`SETTLE`; grouping §3 Gate "a fix waits on a real condition") | In Red `pointer-settle.ts` does not exist |
| AC-2 | unit | `DIAG_DIR_ENV` is `'AVKIT_E2E_DIAG_DIR'`. `diagDir({})` and `diagDir({ AVKIT_E2E_DIAG_DIR: '' })` are `null`, and `diagDir({ AVKIT_E2E_DIAG_DIR: d })` is `d`. `RUN_ID_ENV` is `'AVKIT_E2E_RUN_ID'`; `runId({})` is `''` and `runId({ AVKIT_E2E_RUN_ID: 'x-1' })` is `'x-1'`. `phaseLine(d, row)` twice appends two lines that parse back to the rows, with every `PHASE_LINES` field, `run_id`, `file`, `line`, `test_status` and `test_errors` among them (one row `'passed'` and `0`, one `'timedOut'` and `1`). `e2e-diag.ts`'s text holds no `@playwright/test`. | Local Canon (`DIAG_DIR`, `PHASE_LINES`; the issue's next step) | In Red `e2e-diag.ts` does not exist |
| AC-3 | unit | `installMainDiag` called directly with a fake electron module: two windows (each an event emitter with `getBounds` and a `setIgnoreMouseEvents` spy), a `browser-window-created` emitter, and a fake `screen` whose cursor point is set by the test. The file is a temporary path, and fake timers are used. **With `shield: true`:** `setIgnoreMouseEvents(true)` is called once on each window, and once on a window emitted later. The log holds `install`, then `resize` with bounds after a window emits `resize`, then `cursor-inside` after the point moves inside and 250 ms pass, then `cursor-outside` after it leaves, then `minimize` after a window emits `minimize`. Each window's fake `webContents.executeJavaScript` resolves the visibility state the test set: a change of that state adds one `visibility` line with `state` after 250 ms, and an unchanged state adds none. After `will-quit`, a further 1 s adds no cursor or visibility line. **With `shield: false`:** the spy is never called and the events are still written. The function's source text holds no `require(`, no `import` and no `setBackgroundThrottling`. | Local Canon (`MAIN_DIAG`, `POINTER_SHIELD`, `SHIELD_OPT_OUT`) | In Red the module does not exist |
| AC-4 | E2E | A launch of the built app with a scratch `AVKIT_APP_DATA`, and `AVKIT_E2E_DIAG_DIR` set to a fresh temporary folder when the worker has none. **Before the close:** `phases.jsonl` holds, for this launch and with this test's title, its bare file name `e2e-diag.test.ts`, its `test.info().line` and a `run_id` equal to `process.env.AVKIT_E2E_RUN_ID ?? ''`, `launch-start`, `launch-end` and `evaluate-end`, in that order, each with `test_status` `'passed'` and `test_errors` `0`. Its `main-<launch>.jsonl` holds `install`. After `app.evaluate` calls `setSize` on the first window, a `resize` line appears; the test waits for it frame by frame with `expect.poll` and its default bound. **After `close()` resolves:** the file adds `close-start`, `close-end` and `exit`, in that order, again `'passed'` and `0`, and no `evaluate-error`. | Local Canon (`PHASE_LINES`, `MAIN_DIAG`, `DIAG_DEFAULT_MAIN_ONLY`; the issue's next step) | In Red no `phases.jsonl` is written |
| AC-5 | check | `flake-run.py` at row 3 exits 0 or 1, never 2, in both runs. Exit 2 means a setup failure, a host load still above the ceiling after the wait, or a churn child that died. Its receipts print `host-load:`, `churn child: started`, the per-run lines, `churn child alive at the stop: yes`, `busy children left: 0` and `busy interpreters left: 0`. `epf-burn-level.txt` names the children count, the watched failure count, the count of failures outside the watched set, the median load and `accept-runs:`. The watched count and the full run's covered count are copied into the handoff as the reproduction rate. | Local Canon (D-1146; grouping §3 Order "reproduce under load first") | A setup failure (exit 2), or a busy process left behind, fails it |
| AC-6 | unit (static) | Read as text: `pointer-settle.ts` defines each of `settledCenter`, `rowTransitionsIdle`, `windowSettled`, `grabRow` and `dragOver` once, and holds `rowTestId`. Neither queue spec defines any of the five, and both import from `./pointer-settle`. The AC-49.29 body in `convert-queue.test.ts` calls `grabRow(` and `dragOver(` with `'convert-queue-row'` and holds no `boundingBox()`. | Local Canon (`POINTER_HELPERS_SHARED`, `DRAG_DRIVER_SHARED`; `DOWNLOAD-QUEUE-DRAG-OVER-MISS`) | In Red the helpers live in `download-queue.test.ts` and convert reads raw boxes |
| AC-7 | unit (static) | Read as text from `capture-inbox.test.ts`: <br>• it holds no `async function windowSettled(` and imports `windowSettled` from `./pointer-settle`; <br>• the AC-66.14 and AC-81.14 bodies read through `settledZoom(` and never call `readZoom(` directly; <br>• the AC-81.14 body has a `waitForFunction` between its last `mouse.up()` and `const grabbed = await ends()`; <br>• the AC-67.20 A-6 and AC-80.10 bodies call `pointerOn(`; <br>• `dragImage` calls `settledBox(`. | Local Canon (`SETTLED_ZOOM`, `GRAB_COMMITTED`, `POINTER_SITES`; `CAPTURE-ZOOM-PAN-ORIGIN-FLAKE`) | In Red the sites read once |
| AC-8 | E2E | In the built app, the test adds a fixed, full-window `div` over a nav button. `pointerOn(page, button)` is started and has not resolved after 10 animation frames, which the test counts in the page. After the overlay is removed, it resolves to a point whose `elementFromPoint` is the button or inside it. `settledBox(page, button)` equals `button.boundingBox()` once both are read after `pointerOn`. | Local Canon (`POINTER_ON`, `SETTLED_BOX`) | In Red `pointer-settle.ts` does not exist |
| AC-9 | E2E | A default launch. The first window's handle comes from `getNativeWindowHandle().readBigUInt64LE(0)` through `app.evaluate`. A `spawnSync('pwsh', ['-NoProfile', '-Command', <GetWindowLongPtrW(hwnd, -20) through Add-Type>], { timeout: AC9_SPAWN_TIMEOUT_MS })` call reads the extended style; the test asserts `result.error` is undefined and `result.status` is 0. Both `0x20` (`WS_EX_TRANSPARENT`) and `0x80000` (`WS_EX_LAYERED`) are set. After that, a Playwright `click()` on a nav button changes the route, and a `hover()` on a titled control shows its `title` hint, so CDP input still works. | Local Canon (`POINTER_SHIELD`; D-1149; `DOWNLOAD-QUEUE-DRAG-OVER-MISS` "human input on the window") | In Red, and from row 2 to row 5, the bits are clear |
| AC-10 | E2E (guard) | A launch with `pointerShield: false`: the same read shows `0x20` clear. Passes at Red and at every later row. | Local Canon (`SHIELD_OPT_OUT`) | A shield that ignores the opt-out fails it |
| AC-11 | check | `assert-check.py` passes (`ASSERTIONS_KEPT`, `TESTS_KEPT`, `NO_NEW_WAIT_KNOBS`, `CONFIG_KEPT`, `LF_ONLY`, `EXIT_WAIT_KEPT`) at rows 4, 5, 6, 7 and 8 and in the gate. `main-error-watch.cjs` and `electron-env.ts` keep their row-0 hashes (`REJECTION_WATCH_KEPT`). | Local Canon (D-1151; grouping §3 Gate; D-1145 "no retries, no raised timeouts") | A changed assertion line, a new `timeout:`, a retry or a changed config fails it |
| AC-12 | check | `epf-hang-verdict.txt` lists every failure that rows 3 to 6 marked `hang`, each with its title, its receipt, the last phase of each of its launches, a `signature:`, a `cause:` and a `register:` line. Its last line is `outcome: <in-spec, product-race, split or not-reproduced>`. The registers match the blocks: <br>• `in-spec`: the fix is named with file and line; <br>• `product-race`: one MEU `planned` and one issue `open` naming it, both rendered; <br>• `split`: one new issue `open`; <br>• `not-reproduced`: no register change in row 7. <br>`epf-hang-signatures.json` holds one entry per `product-race` or `split` block and passes `flake-run.py`'s signature check; a `split` entry carries its block's spec file name and exact test title. | Local Canon (D-1150; grouping `:94`, `:97`; the issue's next step) | A hang with no phase named, or an outcome without its register change, fails it |
| AC-13 | check (acceptance) | `flake-run.py --mode full --runs <accept-runs> --label accept --expect-total <row-0 total + 4>` (with `--split-hang <scratch>/epf-hang-signatures.json` when that file holds entries) exits 0 at the burn level. That means: <br>• the median load during the runs is at least 60 %; <br>• each run lists exactly the expected total; <br>• there is no covered failure, no `unhandled rejection:` line and no `evaluate-error` phase; <br>• the busy counts left are 0. <br>**RULE-3 (Session 90).** A failure that is not covered and holds no rejection is rerun alone once under the same load. If the rerun passes, it is recorded and, if new, registered at row 9 with `issue_triage.py add`. If the rerun fails, that is S5. A covered failure fails the AC. A rejection is S10. A test-timeout hang is excused only when it matches a registered signature (a `split` entry: the same spec file and exact title, not watched; a `product-race` entry: the same file and line), with the test's own final launch in this run of this invocation (phase lines bound by run id, file, line and title; no foreign, unreadable or malformed line; one repeat; every earlier launch at `exit`) whose last phase is the signature's and whose phase line reads `test_status` `'passed'` and `test_errors` `0`. Every per-run receipt and diag folder is named by the invocation and created fresh, and row 8 reads only the files that its invocation printed. Every excused hang is listed in the handoff. A hang that matches no signature fails the AC, and an assertion failure is never excused. | Local Canon (D-1145, D-1150; Session 90 RULE-3) | Any watched failure, or a hang that matches no signature, in any run fails it |
| AC-14 | check (acceptance) | Only when `accept-runs` is 3: `flake-run.py --mode watched --repeat 10 --runs 1 --label watch10` exits 0 at the burn level: 110 of 110 tests pass, with the same load, rejection and busy conditions as AC-13. When `accept-runs` is 5 it is recorded `not_run (accept-runs 5)`. | Local Canon (D-1145) | One watched failure in 110 fails it |
| AC-15 | check | Row 9's check passes. `DOWNLOAD-QUEUE-DRAG-OVER-MISS` and `CAPTURE-ZOOM-PAN-ORIGIN-FLAKE` are `resolved`, each with `verification` and `resolution_path`. `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` is `resolved` only under `in-spec`; otherwise it is `open` with the new note. `issue_triage.py render --check` and `meu_status.py render --check` pass. Grouping `:163` reads `executed (Session 91)` with this plan folder, and no other grouping line differs from row 0. | Local Canon (D-1132; grouping §6) | A missing field, or another changed line, fails it |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| What counts as "the flake is gone" | Local Canon | Five full runs under load, or three full runs and 110 watched runs when row 3's watched runs failed, all clean (D-1145) |
| How the flake is reproduced | Local Canon | The watched specs and one full run at the burn level, plus the process-churn child, on the unfixed specs (D-1146) |
| How a pointer target is read | Local Canon | Two equal reads one frame apart, then a hit-test (D-1148) |
| Where the shared helpers live | Local Canon | One `pointer-settle.ts` (D-1147) |
| Real mouse input during a run | Local Canon | The shield is on by default, with an opt-out (D-1149) |
| A hang with a cause outside the specs | Local Canon | It is registered with a signature and split, and acceptance excuses only a hang that matches a registered signature (D-1150; grouping `:94`, `:97`) |
| Which assertions may change | Local Canon | None (D-1151; grouping §3 Gate) |
| How the behaviour is proved | Human-approved | Scripts and tests in the gate (Mat 2026-11-16) |

#### Files Modified

| File | Action | Line endings | Summary |
|------|--------|--------------|---------|
| `ui/tests/e2e/download-queue.test.ts` | modify | LF, kept | The five helpers move out to `pointer-settle.ts`, and the file imports them |
| `ui/tests/e2e/convert-queue.test.ts` | modify | LF, kept | AC-49.29's drive (`DRAG_DRIVER_SHARED`) and the import |
| `ui/tests/e2e/capture-inbox.test.ts` | modify | LF, kept | `windowSettled` imported; `settledZoom`, `GRAB_COMMITTED`, `POINTER_SITES`; row 7's `in-spec` fix, if any |
| `ui/tests/e2e/electron-app.ts` | modify | LF, kept | `PHASE_LINES`, `MAIN_DIAG` call, `DIAG_DEFAULT_MAIN_ONLY`, `EVALUATE_ERROR_KEPT_GOING`, `pointerShield` |
| `ui/tests/e2e/pointer-settle.ts` | new | LF | `SETTLE`, `SETTLED_BOX`, `POINTER_ON`, the shared helpers |
| `ui/tests/e2e/e2e-diag.ts` | new | LF | `DIAG_DIR`, `PHASE_LINES`, `MAIN_DIAG`, `POINTER_SHIELD` |
| `ui/tests/e2e/e2e-diag.test.ts` | new | LF | AC-4, AC-8, AC-9, AC-10 |
| `ui/tests/unit/e2e-pointer.test.ts` | new | LF | AC-1, AC-2, AC-3, AC-6, AC-7 |
| `.agent/context/known-issues.yaml` | modify (script, tool) | LF, kept | Row 9; and row 7 under `product-race` or `split` |
| `.agent/context/known-issues.md` | regenerate | LF | `issue_triage.py render` |
| `.agent/context/grouping/2026-11-17-value-triage-session-grouping.md` | modify | LF, kept | Row 91 (`:163`) only |
| `.agent/context/meu-status.yaml` | modify, only under `product-race` | LF, kept | One MEU, `planned` |
| `docs/build-plan/<area>.md`, `docs/build-plan/build-priority-matrix.md` | modify, only under `product-race` | CRLF, kept | The MEU's row, anchored once |
| `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md` | regenerate, only under `product-race` | as rendered | `meu_status.py render` |

**Line endings** were measured with Python bytes (`epf91-probe.txt`, at `HEAD` `ecfa3f3`).

- **LF:**
  - every spec and harness file in scope;
  - `electron-harness.test.ts`, `e2e-harness.test.ts`, `rejection-watch.test.ts` and `playwright.config.ts`;
  - the registers, the generated issue file, `meu-registry.md` and the grouping;
  - the four new files, which are written as bytes with their CR count checked (Session 83 RULE-3).
- **CRLF:**
  - `ui/package.json`, which is not changed;
  - the state files `docs/execution/metrics.md` and `.agent/context/current-focus.md`;
  - the conditional `docs/build-plan/*.md` files.

  A CRLF file is read and written with `newline=""` from CRLF text. `eol-check.py` checks every scope path in rows 2, 4, 5, 6, 7 and 9 and in the gate, and `assert-check.py` checks `LF_ONLY` on the spec, harness and new files.

### Project files

- **Plan-local scripts, all in this plan folder.**
  - **Written at plan time:**
    - `flake-run.py` (AC-5, AC-13, AC-14, the gate's `ui-electron`), adapted from Session 90's `load-run.py` with its ownership rule and stop unchanged;
    - `assert-check.py` (AC-11).

    Each has a `--selftest` (`epf91-selftest-flake-run.txt`: 122 checks; `epf91-selftest-assert-check.txt`: 17 checks; 0 failures each).
  - **Written in row 0:** `baseline.ps1`, plus `red-check.py`, `identity.py`, `issue-resolve.py` and `eol-check.py`, copied in shape from `2026-11-17-test-run-reliability/`.
  - **Written in row 7,** only under `product-race`: `meu-register.py`.
  - **Written in H1-2:** `session-gate.ps1`.
- **Row 0 data:** `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-eol.json`, `baseline-skip-hashes.json`.
- **Read, never changed** (bound in `baseline-scope.json`):
  - `ui/tests/e2e/electron-env.ts`
  - `ui/tests/e2e/main-error-watch.cjs`
  - `ui/tests/e2e/electron-harness.test.ts`
  - `ui/tests/e2e/main-rejection-watch.test.ts`
  - `ui/tests/e2e/transcript-queue.test.ts`
  - `ui/tests/unit/e2e-harness.test.ts`
  - `ui/tests/unit/rejection-watch.test.ts`
  - `ui/playwright.config.ts`
  - `ui/package.json` (CRLF)
  - `ui/src/renderer/src/components/queue/QueueList.tsx`
  - `ui/src/renderer/src/components/queue/queue-dnd.ts`
- **Never run:** `capture-filmstrip-actions.test.ts` and `capture-import.test.ts`. They touch the real clipboard. `flake-run.py`'s `EXCLUDED` keeps them out of every run, and `--list-check` proves it.
- **State:** `docs/execution/metrics.md` (CRLF), `.agent/context/current-focus.md` (CRLF), the handoff, the rolling reviews and the reflection.

### Sibling overlap

The plan binds each shared file to its content at row 0 (`baseline-scope.json`), not to `HEAD`, and changes only its own entries or lines in it.

| File | Siblings | Rule |
|---|---|---|
| `ui/tests/e2e/` | Session 74 before (it should not touch the folder; row 0 runs `git log ecfa3f3..HEAD -- ui/tests/e2e ui/src`); Session 94 after, which adds F1 and layout specs after this session's commit (grouping `:68-72`) | A commit by Session 74 into a scope file is S2. A moved citation is corrected in the handoff (Session 51 RULE-3). Session 94's new specs launch through `launchElectron`, so they get the shield and the diagnostics by default |
| `known-issues.yaml`, `known-issues.md` | Any triage session; Sessions 92 to 94 | `issue-resolve.py` changes only the three named issues and binds to a hash (S4). Additions go through `issue_triage.py add` |
| Grouping §6 table | Sessions 74 and 92 to 94 | Only `:163` changes |
| `meu-status.yaml`, `docs/build-plan/*.md` | Session 74 (MEU-144), Session 94 (MEU-158, MEU-159) | Touched only under `product-race`, one anchored entry, next free id read at row 7 |
| `current-focus.md`, `metrics.md` | Every session | Read first; change only this session's lines |

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| `transcript-queue.test.ts` W2-5 (named in the drag issue's blast radius) | out-of-scope | — | It has no mouse drag at `ecfa3f3`; it is read only |
| Fixing a race found in `ui/src` | out-of-scope (registered) | the MEU row 7 registers | D-1150: register and split; `PRODUCT_UNCHANGED` |
| A slow launch or close on a loaded host with no spec cause | out-of-scope (registered) | — | D-1150 `split` |
| Retries, raised timeouts, `test.slow`, a changed Playwright config | out-of-scope | — | Grouping §3 Gate; `NO_NEW_WAIT_KNOBS`, `CONFIG_KEPT` |
| Any change to an existing assertion line | out-of-scope | — | D-1151; M-7; S7 undoes the edit |
| The clipboard specs | out-of-scope | — | Never run in this session |

## BUILD_PLAN.md Audit

This session has no MEU of its own. `meu-status.yaml`, `meu-registry.md` and `docs/BUILD_PLAN.md` change only if row 7 registers a product race. H1-3 confirms the render either way:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/e2e-pointer-flakes/epf-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/e2e-pointer-flakes/epf-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` follows `2026-11-17-test-run-reliability/baseline.ps1`.

1. **Tree state and siblings.**
   - It records `baseline.sha` (`HEAD`) and `baseline-dirty.txt` (`git status --porcelain --untracked-files=all`).
   - It records the worktree list and the host load.
   - It runs `git log --oneline ecfa3f3..HEAD -- ui/tests/e2e ui/src`, which names the earlier sessions that touched these paths (Session 74 is expected to touch none).
2. **Path-scoped baseline, bound to content.**
   - `baseline-scope.json` maps each §Files Modified path and each "Read, never changed" path to its SHA-256, or to `absent`. The four new files and `meu-register.py` must be `absent`.
   - `baseline-dirty-hashes.json`, `baseline-eol.json` and `baseline-skip-hashes.json` follow Session 90's rules. The skip hashes now cover `packages/`, `mcp-server/`, `tools/` and `ui/src/` (`PRODUCT_UNCHANGED`).
   - It copies each scope file's bytes to `C:/Temp/av-kit/e2e-pointer-flakes/baseline-copies/<path>`. `assert-check.py --snapshot` writes its own copies under `baseline-copies/assert`, and refuses to overwrite them.
   - **The S2 binding:**
     - every `epf91-probe.txt` anchor is found once at its line, or at a moved line with the same text (a moved line is recorded and corrected in the handoff, Session 51 RULE-3);
     - the three issues are `open`;
     - grouping `:163` is `proposed`;
     - the highest MEU is MEU-159 or a later id that another session registered (recorded);
     - D-1145 to D-1154 are unused outside this plan.
3. **Base receipts.**
   - The host-load wait runs first.
   - `flake-run.py --list-check --label base-list` writes `epf-base-list.txt`. It checks that the clipboard specs are not listed, that each watched fragment names one test, and that the watched list holds 11. Its full total goes to `epf-base-total.txt`.
   - The full Vitest run goes to `epf-base-ui.txt`. Failures are recorded, not fatal, and the gate excuses only those ids.
   - `epf-red-source.txt` records `git rev-parse HEAD:<spec>` for the three spec files, so row 3 can show that it ran on unfixed specs.
4. **Plan-local scripts.**
   - `red-check.py`, `identity.py`, `issue-resolve.py` and `eol-check.py` are copied from `2026-11-17-test-run-reliability/` with this plan's `PLAN`, `PROJECT_ARTIFACTS` and scope.
   - `DECLARED_NEW` is `settle`, `settledBox`, `settledZoom`, `pointerOn`, `grabRow`, `dragOver`, `phaseLine`, `diagDir`, `installMainDiag`, `DIAG_DIR_ENV`, `runId` and `RUN_ID_ENV`.
   - `red-check.py`'s boundary fixtures check `AC-1` against `AC-10` to `AC-15`.
   - `identity.py` clears `ELECTRON_RUN_AS_NODE`, and its other-plan skip covers the untracked `docs/execution/plans/2026-11-1[5-7]-<slug>/` folders other than this one.
   - `issue-resolve.py` uses `SCRATCH` at `C:/Temp/av-kit/e2e-pointer-flakes/issue-resolve`, with `RESOLVE_KEYS` `status`, `verification`, `resolution_path` and `notes`. An entry with no `status` leaves the issue's status as it is.
   - Then `assert-check.py --snapshot` runs.
   - Then the selftests of `red-check.py`, `identity.py`, `eol-check.py`, `flake-run.py` and `assert-check.py` run, along with `flake-run.py --kill-check --children 2 --churn`, and `ruff format --check` and `ruff check` on the plan folder's Python (Session 82 RULE-1).
5. **Secrets and the fleet hub.** The scope walk drops `.mcp.json`, `mcp-token.txt`, `.claude.json`, `.env`, `.claude/settings.local.json` and `.agent/fleet/hub` before any stat or read (Session 83 RULE-2).

If any step fails, except the full Vitest receipt, the row fails and nothing else runs.

### 2. Red, then Green

- **Each Red receipt holds an assertion failure, never a setup failure.**
  - `red-check.py --require` names AC-1, AC-2, AC-3, AC-6 and AC-7 in the Vitest receipt, which reads `5 failed`.
  - It names AC-4, AC-8 and AC-9 in the Playwright receipt. That receipt also has one `ok` line for AC-10 (count pattern `^ +ok +[0-9]+ `, Session 89 RULE-1).
- **Expectations stay immutable in Green** (S3). Row 1 records the hashes of the two test files, and every later row checks them.
- **Partial Green.**
  - Row 2's Vitest receipt reads `2 failed | 3 passed`, and `red-check.py --require AC-6 --require AC-7` still passes on it.
  - Its Playwright receipt has `ok` lines for AC-4, AC-8 and AC-10, while AC-9 still fails by assertion.
  - AC-6 passes from row 4, AC-7 from row 5 and AC-9 from row 6.
- **No typecheck at Red.** Typecheck and lint run from row 2 on.

### 3. Load runs (rows 3, 4, 5, 6 and 8)

`flake-run.py`'s docstring is the contract:

- the host-load wait, with exit 2 when the load is still above the ceiling after 10 minutes;
- the busy children, each one owned through its handle, and at row 3 the `--churn` child, whose death during a run is exit 2;
- the 60 % signal, which proves only that the children ran;
- Playwright through `node ui/node_modules/@playwright/test/cli.js` with `--retries=0`;
- a new invocation id per invocation, and per run a receipt, a diag folder and a run id named by it, each created fresh and refused if already there (exit 2);
- the process-start sampler, into its own fresh `procs-<inv>` file;
- the failure classes and the solo rerun;
- the `finally` stop;
- at row 8, `--split-hang` with the signatures row 7 registered: only a test-timeout hang that matches one is excused, and each is printed as an `excused:` line.

Exit 2 is S8. Every run is preceded by `npm --prefix ui run build`, because the stale-build check in `global-setup.ts` would otherwise refuse it.

### Session gate (H1-2)

`session-gate.ps1` follows `2026-11-17-test-run-reliability/session-gate.ps1`:

- one receipt per step in `C:/Temp/av-kit/e2e-pointer-flakes/`, named `epf-D6-<step>`;
- fail-fast, with later steps printed as `not_run`;
- the last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `ui-types`, `ui-lint` (pwsh in `ui/`); `task-contract`; `scope-paths`; `line-endings` (`eol-check.py`); `home-path` (`tools/check_home_path.py`) |
| Selftests | `flake-run-selftest`, `assert-check-selftest`, `red-check-selftest`, `eol-check-selftest`, `identity-selftest` |
| Python | `py-format` (`ruff format --check` on the plan folder's Python); `py-lint` (`ruff check` on the same) |
| Targeted | `assert-check`; `ui-unit` (`e2e-pointer.test.ts`, `e2e-harness.test.ts`, `rejection-watch.test.ts`) |
| Host load | `host-load`: at most 50 % before the Electron stage, waited for, and recorded (Session 81 RULE-2) |
| Fresh full | `ui-tests` (full Vitest); `ui-build`; `ui-electron`: `flake-run.py --mode full --runs 1 --no-burn --label gate --expect-total <row-0 total + 4>`, which runs every E2E file except the two clipboard specs, with no busy children; `issues-render-check` (`issue_triage.py render --check`); `state-render` (`meu_status.py render --check`) |
| Skipped, with reason | `py-tests`, `py-types`, `openapi`, `mcp-*`: every file under `packages/`, `mcp-server/`, `tools/` and `ui/src/` keeps its `baseline-skip-hashes.json` hash, and none was added or removed (H1-4). Under `product-race` the MEU files are docs and registers only |

`ui-tests` excuses only the ids that `epf-base-ui.txt` shows failing.

## Stop Conditions

No stop waits for Mat. Mat, 2026-11-18: 'Why do you keep stopping for each of the decisions even after I expelictly told you to make the decisions always the recommenations. If you do not believe you can make the decisions run HDP and take recommenations from that!'. Where a stop below calls for a decision, it is an execution decision (D-1152, D-1153, D-1154 in that order), run through HDP and taken on its recommendation under those words, with the evidence and the recommendation recorded in the handoff.

| ID | Condition | Action |
|---|---|---|
| S1 | A `graphify-out` graph appears | Re-decide the context tool |
| S2 | Row 0 finds an anchor missing, or its text changed; an issue not `open`; `:163` not `proposed`; a new file present; or a commit since `ecfa3f3` that changed a scope file | Another session moved this ground. Re-probe, correct the plan's anchors and baseline in the handoff, and go on. A line that only moved is corrected in the handoff. Never revert another session's work |
| S3 | A Red receipt fails `red-check.py` (a setup failure, or a Red that passes); AC-10 fails at Red; or a Green row needs a changed expectation in a new test | Fix the test setup. Never edit an expectation in Green |
| S4 | A path outside this plan's scope and `baseline-dirty.txt` changes; a `baseline-dirty.txt` path changes content; or `known-issues.yaml` lacks its expected hash when `issue-resolve.py` runs | Re-baseline in exact-scope mode: record the other session's paths and hashes, bind this session's checks to its own paths, and go on. Never commit, stash or revert another session's work |
| S5 | An existing test, not covered, fails twice: once in a run and once in its solo rerun (Session 90 RULE-3) | Register an issue with its receipts (`issue_triage.py add`), then take an execution decision through HDP. It is an M-7 question, not a fix |
| S6 | Codex is unavailable or the ledger refuses | Retry the dispatch once. If it fails again, the review stays pending and the coordinator re-dispatches it |
| S7 | `assert-check.py` fails | Undo the edit that broke it. If an assertion change seems needed, that is an execution decision through HDP whose default keeps the assertion and registers an issue. Never edit the checker to pass |
| S8 | `flake-run.py` exits 2 (the load is not reached, the host load stays above the ceiling after the wait, the churn child died, a reused id is refused, or a busy process is left) | Rerun once after the host-load wait. If it fails again, record the receipts and take an execution decision through HDP. Never lower `--threshold` |
| S9 | AC-13 or AC-14 shows a covered failure | Read its diag. Make one more fix within the contracts at the row whose mechanism it names, then rerun row 8 in full. The rerun is a new invocation: its receipts, diag folders and run ids are new, and neither `flake-run.py` nor row 8's check reads the earlier attempt's files. A second covered failure is an execution decision through HDP, with the receipts |
| S10 | Any `unhandled rejection:` line in any run | Stop the run at the first record and register it as an issue with the record. Never rerun it away. Then take an execution decision through HDP |
| S11 | AC-9 fails at row 6 (the shield bits are not set, or CDP input stops working) | Set the default back to `false`, record it, then take an execution decision through HDP (D-1149's C would change AC-9) |
| S12 | AC-13 shows a test-timeout hang | A hang that matches a signature in `epf-hang-signatures.json` (its file and title or line, its phase, and the test's own final launch in this run of this invocation, which stood `'passed'` with no error at that phase, with no foreign, unreadable or malformed line, one repeat, and every earlier launch at `exit`) is excused, printed as `excused:` and listed in the handoff; the drag and zoom fixes are not held. A hang that matches no signature fails AC-13, and S9 applies |
| S13 | A file under `packages/`, `mcp-server/`, `tools/` or `ui/src/` changes | Undo this session's own edit. A change by another session is S4. This session changes no product, API or tool file |

The holds that stay with Mat are a destructive or irreversible step, a push, and any read or write of user data. No row takes one: nothing is deleted outside the scratch folder, nothing is pushed, and the specs use a scratch `AVKIT_APP_DATA`.

## Decision Log

> [!NOTE]
> **Briefs and autonomous decisions.**
>
> - D-1147, D-1148 and D-1151 are autonomous with `mandatory: none`. Each passed the §4a list and the §4 test.
> - Four decisions hit an M item, so they are briefs (below):
>   - D-1145: M-3 and M-8
>   - D-1146: M-8
>   - D-1149: M-3
>   - D-1150: M-8 and M-11 (`--split-hang` lets acceptance excuse a hang, which narrows the run's scope)
> - Mat's hand-over covers M-3, M-5, M-6 and M-8 briefs (HDP §6). The four are recorded `autonomous`, with their `mandatory:` lists kept. `open_decisions` is empty and there is no STOP item.
> - **Conflict, recorded as directed.** HDP §6 (`human-decision-protocol.md:328-329`) keeps an M-11 item with Mat even under a hand-over. The coordinator directed that M-11 for `--split-hang` be decided on its recommendation under Mat's 2026-11-18 words ('Why do you keep stopping for each of the decisions even after I expelictly told you to make the decisions always the recommenations. If you do not believe you can make the decisions run HDP and take recommenations from that!'). D-1150 is recorded `autonomous` on that direction, and its reasoning states the conflict. One line from Mat overturns it.
>
> **No other M item is hit.**
>
> - No API, OpenAPI or MCP change, so M-4 is clear.
> - No user data is read or written, so M-2 is clear.
> - No existing assertion line changes (`ASSERTIONS_KEPT`, enforced by `assert-check.py`). The three waits added in front of unchanged expectations are named with their files and lines in §Test pins, so M-7 is clear.
> - Registering a product race as an MEU is pre-approved by grouping `:94`, and splitting a separate launch-hang cause by grouping `:97`. D-1150 follows those two lines rather than making a new scope call.
>
> **Free ids.** D-1152 to D-1154 are free for execution decisions, taken through HDP in that order: S5, S7, S8, S9, S10, S11, an in-spec hang with no fix inside the contracts, or a split or rename of this session. None waits for Mat.
>
> **Why Session 91 is inside the hand-over.**
>
> - Mat's 2026-11-18 message: 'Why do you keep stopping for each of the decisions even after I expelictly told you to make the decisions always the recommenations. If you do not believe you can make the decisions run HDP and take recommenations from that!'
> - Mat's 2026-11-17 message asked to "orchestrate the plan creation for all sessions and proceed with execution for each", continuing his 2026-11-15 hand-over ('like we did here. But use the new HDP process.').
> - Session 91 is §3 of the grouping that message acts on (this plan's `grouping_source`).
> - The 2026-11-17 message is dated the day this brief set was written, and the 2026-11-18 message the day the expert pass revised it, so the hand-over is not carried over from an earlier brief set. `plan_to_exec_gate: human` is kept as the plan's gate field. Under the 2026-11-18 words, execution opens on the coordinator's dispatch, and no brief waits for Mat.
>
> **Earlier rows are not copied here.**
>
> - The grouping rows D-1131 to D-1133 live in the grouping file's §8 (grouping `:196`: "Sessions 91 to 94 carry D-1131, D-1132 and D-1133"). The three issues carry D-1126 in their enrichment.
> - H2-2 reads them through `--decision-source` on the grouping and on `.agent/context/known-issues.yaml`, with `--decision-issue` for each of the three issues.
> - `decision_sources` was probed at plan time against this plan itself, once it existed (`epf91-probe-run.txt`):
>   - the grouping alone gives D-1131 to D-1134;
>   - with the register and the three issues it gives D-1126 and D-1131 to D-1134;
>   - with this plan it also gives D-1145 to D-1151 at stage `planning`.

```yaml
decision_log:
  - id: D-1145
    stage: planning
    question: "What proves the three load flakes are gone?"
    resolution: autonomous
    class: product-preference
    mandatory: [M-3, M-8]
    chosen: "A: full Electron runs (every E2E file but the two clipboard specs) at the burn level, each run listing the row-0 total plus 4 tests, with zero covered failures (a watched title, or a test-timeout hang that matches no registered signature), zero unhandled-rejection lines and zero evaluate-error phases (AC-13). The count follows row 3: if the watched receipts show zero failures, five full runs (accept-runs 5) and no watched repeat; otherwise three full runs plus the eleven watched tests ten times at the same load, 110 of 110 (AC-14). The host-load wait before each run has a ceiling: a load still above 50 % after 10 minutes is exit 2 (S8). The 60 % median floor proves only that the busy children ran. No retry, no raised timeout, no changed config (AC-11). An uncovered failure with no rejection is rerun alone once: a pass is recorded and registered if new, a second failure is S5 (Session 90 RULE-3)."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md:88-97 — Session 91 order, gate and split flag"
      - ".agent/context/handoffs/2026-11-17-test-run-reliability-handoff.md:101-108 — Session 90's seven full runs: 3 failed, each run 6.9 to 17.3 min"
      - ".agent/context/known-issues.yaml:971, :1010, :2904 — the three issues, each seen only under full-suite load"
      - ".agent/context/known-issues.yaml:986, :1025 — every isolated rerun on record passed"
      - "docs/execution/plans/2026-11-17-test-run-reliability/load-run.py — Session 90's busy-child load run, the source of flake-run.py"
      - "ui/playwright.config.ts — timeout 60_000, workers 1, kept byte-identical"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'Why do you keep stopping for each of the decisions even after I expelictly told you to make the decisions always the recommenations. If you do not believe you can make the decisions run HDP and take recommenations from that!', continuing USER_EXPLICIT 2026-11-17 'orchestrate the plan creation for all sessions and proceed with execution for each', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. M-3 because the load floor, the ceiling, the run counts and the repeats are thresholds; M-8 because the acceptance defines when the issues close. The flakes failed 3 of Session 90's 7 full runs (Session 90 handoff :101-108), so with no fix a clean full run still comes up about 57 % of the time (4/7): one clean run (B) passes by chance more often than not, three in a row about 19 % of the time (0.57^3) and five about 6 % (0.57^5). Those runs took 6.9 to 17.3 min each, so C's two extra full runs cost about 14 to 35 min, not hours. Every isolated rerun on record passed (known-issues.yaml:986, :1025), so ten watched repeats tell the fix apart from luck only when row 3's watched runs fail; with zero watched failures there, acceptance is five full runs, and otherwise three full runs plus the ten watched repeats. Eighteen busy children give about 75 % on 24 logical CPUs on their own, so the 60 % floor proves only that the children ran; the ceiling keeps a run from starting on a host already loaded from elsewhere. known-issues.yaml:982, :2913-2914 and grouping :92 still copy 4 of 7; they are outside this plan's scope and are not edited here. Two-way: the counts are flags on flake-run.py."
  - id: D-1146
    stage: planning
    question: "How are the flakes reproduced before any fix, and what if they do not show?"
    resolution: autonomous
    class: product-preference
    mandatory: [M-8]
    chosen: "A: at row 3, on the unfixed specs (epf-red-source.txt), run the watched tests ten times and one full run with 18 busy children (about 75 % on 24 logical CPUs) and one process-churn child (--churn: short node -e 0 and pwsh -NoProfile -Command exit starts in a loop). Exit 0 or 1 is a measurement and the counts go into the handoff as the reproduction rate; exit 2 is S8, and covers a churn child that died. If both show no watched failure and no hang, repeat once with 24 children; if 3 or more failures outside the watched set then occur (uncovered specs, plus hangs in specs that are not watched), go back to 18 and record it. epf-burn-level.txt fixes the level rows 4, 5, 6 and 8 use, and the accept-runs count that D-1145 reads. A reproduction with no failure does not stop the session: the fixes are judged by their mechanism tests (AC-1 to AC-10) and by acceptance at that level."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md:93 — reproduce under load first"
      - "docs/execution/plans/2026-11-17-e2e-pointer-flakes/flake-run.py — the watched list, the classes, the churn child and the diag summary"
      - ".agent/context/known-issues.yaml:2904 — the issue's next step: log host process starts and time launch and close"
      - ".agent/context/known-issues.yaml:2910, :2923 — the hang's root cause and notes: other sessions starting their MCP servers"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'Why do you keep stopping for each of the decisions even after I expelictly told you to make the decisions always the recommenations. If you do not believe you can make the decisions run HDP and take recommenations from that!', continuing USER_EXPLICIT 2026-11-17 'orchestrate the plan creation for all sessions and proceed with execution for each', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. M-8 because a statistical reproduction stands in for a deterministic Red on the flakes themselves. The hang hypothesis on record is bursts of process starts from other sessions starting their MCP servers (known-issues.yaml:2910, :2923), which busy loops alone do not make, so one churn child adds that kind of load. At 24 children every timeout is classed a covered hang, so a back-off that counted only uncovered specs would never fire; counting hangs outside the watched set lets starvation at 24 bring the level back down instead of feeding D-1150. Requiring a failure before any fix (B) could stop the session on a lucky quiet hour although the code shows the races (one-shot reads, a release with no wait). Fixing from the code alone (C) gives no before-and-after rate and no hang diagnostics to decide D-1150 on. Two-way: one receipt and two flags."
  - id: D-1147
    stage: planning
    question: "Where do the drag and window-settle helpers live once convert and capture use them?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "One new ui/tests/e2e/pointer-settle.ts: the five download helpers move there once with a rowTestId option (default queue-card), with settle, settledBox and pointerOn beside them; capture-inbox's identical windowSettled copy is deleted and imported."
    source_tag: Local Canon
    precedents:
      - "ui/tests/e2e/download-queue.test.ts:1098-1269 — the helpers and their Session 26 settle rule"
      - "ui/tests/e2e/capture-inbox.test.ts:787-828 — the same windowSettled, copied"
      - "ui/src/renderer/src/components/queue/QueueList.tsx:75, :162, :325, :367 — rowTestId, data-job-id and the shared announcements"
    research: { engine: none, sources: [] }
    reasoning: "A second copy of the drag helpers in convert-queue.test.ts would leave three copies of the same settle code to drift; the convert spec raced exactly because it never got them. A shared file under ui/tests/e2e is test-only and adds no launcher name (e2e-harness.test.ts:60). Two-way: a move and an import."
  - id: D-1148
    stage: planning
    question: "What does a settled pointer target mean?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Two equal reads one animation frame apart, bounded at 60 frames as settledCenter already is, then a hit-test that elementFromPoint lands on the target; the AC-81.14 grab waits until x2 changes. No wall-clock wait is added."
    source_tag: Local Canon
    precedents:
      - "ui/tests/e2e/download-queue.test.ts:1098-1125 — settledCenter's two-frame rule and 60-frame bound"
      - ".agent/context/known-issues.yaml:1010 — the origin read 92 px off, one frame early"
      - ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md:94 — a fix waits on a real condition"
    research: { engine: none, sources: [] }
    reasoning: "Each fault in the issues is a read taken while layout or a drag was still moving, or a press aimed at a point another element covered. Waiting for the read to repeat and the point to hit removes both without guessing a delay; a fixed sleep or a longer timeout would hide the race on a quiet host and lose it on a busy one. Two-way: helper code."
  - id: D-1149
    stage: planning
    question: "Should the E2E app windows ignore real mouse input while a run is going?"
    resolution: autonomous
    class: product-preference
    mandatory: [M-3]
    chosen: "A, widened: on by default for every launch of the built app, through setIgnoreMouseEvents(true) on each window from the main-process diagnostics, with LaunchOptions.pointerShield: false as an opt-out. The keyboard is not blocked. MAIN_DIAG also logs hide, minimize, restore and visibility changes, so a pass-through click that raises the window beneath shows in the log; setBackgroundThrottling(false) is not used. AC-9 proves the window style bits and that Playwright clicks and hovers still work, with its spawnSync bounded by AC9_SPAWN_TIMEOUT_MS; AC-10 proves the opt-out. Row 6 runs the watched tests ten times at the burn level with the shield on. If AC-9 fails, the default goes back to false and an execution decision is taken through HDP (S11). Rejected: enabling the shield only if rows 3 to 5 show cursor-inside at a failure."
    source_tag: Local Canon
    precedents:
      - ".agent/context/known-issues.yaml:971 — A-4 diagnostics show human input on the window (A-7)"
      - "ui/tests — no spec drives OS input (no SendInput, mouse_event, SetCursorPos or keybd_event), and ui/ has no setIgnoreMouseEvents"
      - "ui/tests/e2e/electron-app.ts:70 — the one launch path"
      - "ui/tests/e2e/download-queue.test.ts:1150-1177 — the suite waits for a visible window with full-rate frames"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'Why do you keep stopping for each of the decisions even after I expelictly told you to make the decisions always the recommenations. If you do not believe you can make the decisions run HDP and take recommenations from that!', continuing USER_EXPLICIT 2026-11-17 'orchestrate the plan creation for all sessions and proceed with execution for each', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. M-3 because it is a new default for every E2E launch. Mat works on the same desktop while suites run, and the drag issue records his cursor moving a drag; the settle fixes cannot stop a real pointer from arriving mid-drag. Opt-in for the watched specs (B) leaves every other pointer spec open to the same input. Diagnostics only (C) would show the input but not stop it. The conditional enable (D) is rejected: it depends on Mat happening to move the mouse during rows 3 to 5, an absence of cursor-inside proves nothing about the runs after, and the shield is cheap and has an opt-out. A pass-through click can raise the window beneath, and the suite needs a visible window with full-rate frames within 15 s (download-queue.test.ts:1150-1177), so row 6 measures the watched set with the shield on and the visibility log names any cover; setBackgroundThrottling(false) would hide real visibility faults. AC-9's pwsh Add-Type has the shape of the AC-81.11 hang suspect, so its spawnSync gets a timeout, the one named exception to NO_NEW_WAIT_KNOBS. Playwright's input goes through CDP, which the shield does not block. Two-way: one default."
  - id: D-1150
    stage: planning
    question: "What happens if the launch hang has a cause outside the specs?"
    resolution: autonomous
    class: product-preference
    mandatory: [M-8, M-11]
    chosen: "A, per block: row 7 classifies every hang from the phase lines and decides the register change per block, writing a signature (file:line, phase and the exact test title), a cause and a register line for each. In-spec: fix it here within the contracts; if no fix fits, an execution decision through HDP whose default registers it as split. Product race: register the next free MEU in the Stage A shape and one issue, write a product-race signature with both ids, and split the fix to its own session; acceptance excuses a hang with that exact signature, so the drag and zoom fixes are not held. A separate launch or close cause (last phase launch-start or close-start, written while test.info() still read status passed with no error; never launch-end): register one issue, write a split signature keyed on the spec file, the exact test title and the phase, and split it. Row 8 runs --split-hang with the signature file when it holds entries: only a test-timeout hang that matches a signature is excused, a split signature excuses only its own file and title and never a watched spec, every excuse rests only on the failing test's own final launch in this run of this invocation (each invocation names its receipts and diag folders by a new id and creates them fresh, refusing any already there; a phase line counts only when it carries the run's id, file, line and title; any foreign, unreadable or malformed line, a second repeat, a tie or an earlier launch that did not reach exit excuses nothing), that launch's last phase line must have stood passed with no error (missing state excuses nothing), and every excused hang is listed in the handoff. Not reproduced: keep the instrumentation, write [] and leave CAPTURE-E2E-LAUNCH-TEARDOWN-HANG open with a note naming the receipts."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md:94 — if a race is in the product, the plan registers an MEU for it"
      - ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md:97 — split flag: a separate cause becomes its own session"
      - ".agent/context/known-issues.yaml:2904 — the hang's shape and next step"
      - "ui/tests/e2e/capture-inbox.test.ts:1953 — the finally close of AC-81.11's second launch"
      - ".agent/docs/human-decision-protocol.md:328-329 — the hand-over does not cover M-11"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'Why do you keep stopping for each of the decisions even after I expelictly told you to make the decisions always the recommenations. If you do not believe you can make the decisions run HDP and take recommenations from that!', continuing USER_EXPLICIT 2026-11-17 'orchestrate the plan creation for all sessions and proceed with execution for each', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. M-8 because a split narrows what this session closes and what AC-13 counts; M-11 because --split-hang lets an existing test's timeout pass acceptance. HDP §6 (human-decision-protocol.md:328-329) keeps an M-11 item with Mat even under a hand-over. The coordinator directed on 2026-11-18, under Mat's words above, that it be decided on its recommendation, and it is recorded that way; the conflict is stated here and in the plan, and one line from Mat overturns it. launch-end is not split because by then the app is up and this session's own installMainDiag evaluate runs, so excusing it could hide a hang the session made. A close-start counts as split only when its phase line still reads test.info() status passed with no error, because a body hang that ends in the finally close (capture-inbox.test.ts:1953) would otherwise read as a close hang; Playwright 1.64.1 sets the status to timedOut when the timeout fires, while the body still runs, so this is the test's own timeout state, not a clock inferred from the first launch that setup before the launch could shift (plan review round 1, F2). The same clean-state rule holds for a product-race entry, so a registered close signature cannot excuse a later body hang in that test. A split entry names its spec file and exact title, so it cannot excuse a hang in another test (round 1, F1). Plan review round 2 (F3) found that a rerun of row 8 appended to the earlier attempt's diag folder, so a stale clean close could excuse a current body timeout; the ledger's V30 stop named the mechanism, so the binding was redesigned rather than the instance patched: each invocation takes a new id and names every receipt, diag folder and host-process file by it, created fresh and refused when already there; each phase line carries its run id, file and line, and diag_summary counts a line for the test only on all four of run id, file, line and title; any foreign, unreadable or malformed line, a second repeat, a tie between launches or an earlier launch that did not reach exit excuses nothing; --split-hang with repeats is refused; row 8's check reads only the files its invocation printed. The selftest holds the two-invocation regression and the other negative cases, and ten weakened copies of flake-run.py each fail it (epf91-f3-mutants.txt). Keeping the excuse path against counting every timeout as a failure was weighed under HDP: counting every timeout would make a registered product race or split cause fail AC-13 and hold the drag and zoom fixes, the same end as C, and would undo what grouping :94 and :97 already decided; the path is now bound to this test's own final launch in this run of this invocation and fails closed on any doubt, every excuse is printed, counted and listed in the handoff, and one line from Mat removes it. So the recommendation is to keep it, and it is taken. Known limits: an assertion thrown inside a try reaches Playwright only after its finally ends, so a finally close that hangs after it still reads passed; an excuse needs the phase lines to have been written; the run id is an environment value the test side copies; a launch id could repeat if a worker pid is reused. The file, line and title identity, the run id and the watched rule bound each to the one registered test in this run. Per-block registers stop one session-wide outcome from deciding for blocks of another kind. Without an excuse for a registered product race, AC-13 would count it and hold the drag and zoom fixes, the same end as C. Fixing a product race here (B) would put ui/src changes into a test-harness session without their own plan and review. Stopping on every outcome (C) would hold the drag and origin fixes, which do not depend on the hang. The grouping already decided both the registration and the split, so A follows it and keeps the acceptance honest: an excused hang is printed, counted and listed, only not failed. Two-way: registers and a flag."
  - id: D-1151
    stage: planning
    question: "May any existing assertion line change to make a spec steady?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "No. In the three spec files the multiset of expect lines and the test( lines equal row 0 (assert-check.py, AC-11); added waits are waitForFunction or waitFor; an edit that breaks the check is undone (S7), and a needed assertion change is an execution decision through HDP whose default keeps the assertion and registers an issue."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md:94 — any assertion change is named in the plan (M-7)"
      - "docs/execution/plans/2026-11-17-e2e-pointer-flakes/assert-check.py — the check and its 17 selftest cases"
    research: { engine: none, sources: [] }
    reasoning: "The flakes are in how the specs aim and when they read, not in what they assert; keeping every assertion makes that claim checkable. Naming a change in advance is impossible because none is planned, so any change is undone and goes through S7, never a quiet edit. Two-way: a checker."
  - id: D-1152
    stage: execution
    question: "F2 is held by a process outside this session (RegisterHotKey last error 1409, ERROR_HOTKEY_ALREADY_REGISTERED), so AC-81.11's HOTKEY_IN_USE_FIXTURE cannot hold it and fails on every launch: all 10 of row 3's watched failures and the one covered failure in its full run are AC-81.11 at capture-inbox.test.ts:1958. It distorts row 3's burn level (without it the watched and hang counts are 0, so escalate would be yes and accept-runs 5) and would fail every row 8 run. What happens?"
    resolution: autonomous
    class: externally-blocked
    mandatory: [M-10, M-11]
    chosen: "A: rows 4 to 7 go on at the recorded level (18 children) as measurements, with AC-81.11 named F2-held in each receipt read and an F2 probe receipt beside each run. Row 5's plain capture-inbox run counts as passing when its only failure is AC-81.11 at :1958 and an F2 probe just after reads held; that is recorded as a deviation, not a pass of AC-81.11. Before row 8 F2 is probed again. If it is still held, the session goes back to the coordinator as a hold before row 8, recommending that Mat release F2 (close the holder), then row 3 rerun as a new invocation for an honest burn level and accept-runs, then row 8. No process outside this session is stopped, and AC-81.11 is never excused in acceptance."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-pointer-flakes/epf-f2-probe-1.txt, epf-f2-probe-2.txt — F2 held, last error 1409, with no av-kit launch of this session running"
      - "C:/Temp/av-kit/e2e-pointer-flakes/epf-burn-level.txt — watched failures 11, all AC-81.11; escalate no; accept-runs 3"
      - ".agent/context/handoffs/2026-10-24-gui-theme-path-fields-MEU-93-handoff.md:74 — AC-81.11 failed once with F2 held by ShareX; accepted by Mat (D-120)"
      - "docs/execution/plans/2026-10-14-capture-chrome/implementation-plan.md:495 — S4: F2 already held; Mat closes the holder, or a seam"
      - "ui/tests/e2e/capture-inbox.test.ts:1948-1958 — the fixture asserts the helper prints HELD"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-17 'orchestrate the plan creation for all sessions and proceed with execution for each', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.', and USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. M-10 because only Mat can release the F2 hotkey: the brief forbids stopping a process this session did not start, and ShareX and Mat's own apps run on this host. M-11 because row 5's plain-run check is read with one environment failure set aside. The fixture fails before its launch (each failing diag line shows launches 0), so the failures say nothing about the hang or the pointer fixes, and rows 4 to 7 still measure the drag, zoom, origin and shield tests. Holding now (B) would leave those measurements undone while waiting for one hotkey. Excusing AC-81.11 in acceptance (C) would change AC-13 and hide a watched test, so it is rejected. Do nothing (run row 8 with F2 held) fails AC-81.11 in every run and ends in S9 with no fix in the contracts. Two-way: Mat releases F2 and the two runs repeat as new invocations."
  - id: D-1153
    stage: execution
    question: "F2 was held through rows 3 to 7 (D-1152), so row 3's burn level and accept-runs rest on AC-81.11 failing its F2 hold. Now that F2 is free, how are the burn level and acceptance set?"
    resolution: autonomous
    class: externally-blocked
    mandatory: [M-10]
    chosen: "A, the hold's recommendation: rerun row 3 as a new invocation under fresh receipt names (labels repro-b, base-full-b and, when D-1146 escalates, repro24-b and base-full24-b; epf-burn-level-b.txt), take the burn level and accept-runs from it under D-1145 and D-1146, probe F2 again just before row 8, and run row 8 at that level. Row 3 runs on the unfixed specs with the shield off, so for the rerun the three spec files are put back from the row-0 copies (baseline-copies, hashes checked against baseline-scope.json) and the shield default is set back to false; the fixed files are saved first with their hashes and restored after, each hash checked. The first run's receipts stay as they are, as the skewed evidence, and the handoff shows both runs. Row 8 reads epf-burn-level-b.txt in place of epf-burn-level.txt; any hang in the rerun receipts goes through row 7 again."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/e2e-pointer-flakes/epf-f2-probe-7.txt — F2 free (registered and released)"
      - "C:/Temp/av-kit/e2e-pointer-flakes/epf-burn-level.txt — the skewed level: watched failures 11, all AC-81.11; escalate no; accept-runs 3"
      - "docs/execution/plans/2026-11-17-e2e-pointer-flakes/implementation-plan.md D-1145, D-1146 — how the level and the run count follow row 3"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-17 'orchestrate the plan creation for all sessions and proceed with execution for each', continuing USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.', and USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Mat released F2 on 2026-11-18 by closing the ShareX hotkey: 'closed the sharex app hotkey should be free now'. The coordinator took the hold's recommendation and approved the extra row-3 load, which is local CPU only. M-10 because the release was Mat's action. Keeping the skewed level (B) would set acceptance from a measurement in which every watched failure was the F2 hold, not the flakes, and would depart from D-1145 and D-1146. Doing nothing leaves AC-81.11 failing nowhere now, but the level unjustified. The temporary restore of the unfixed specs is reversible: every file is saved with its hash and checked on the way back. Two-way: receipts under new names."
open_decisions: []
```

Expert pass (fresh context): 4 briefs. Holds: none. Changed: D-1145, D-1146, D-1149, D-1150. Not adopted: none (the pass's conditional-enable option for D-1149 is added to that brief as a rejected option). Receipt: `C:/Temp/av-kit/e2e-pointer-flakes/s91-expert-pass.txt`.

### D-1145: What proves the three load flakes are gone?

**I recommend A: full Electron runs on a machine kept busy on purpose, all clean. Five runs if the flaky tests passed on their own at row 3; otherwise three runs plus ten runs of the eleven flaky tests.** The flakes only show when the machine is busy, so the proof runs that way. The script keeps about three quarters of the processor busy and checks it stays above 60 %. That floor only proves its own load ran, so the script also refuses to start while the machine is still more than half busy from elsewhere. A clean run means none of the flaky tests fails, no test hangs except one with a cause this session registered, and the app logs no unhandled error. A test outside this set that fails once is rerun on its own. If it then passes, it is noted and registered. If it fails again, it is registered and decided through HDP. Nothing is retried, and no time limit is raised.

The flakes failed 3 of Session 90's 7 full runs. If the fixes did nothing, three clean runs in a row would still happen about one time in five, and five clean runs about one time in seventeen.

- B: one full run under load. With no fix, a clean run still comes up more than half the time.
- C: always five full runs and ten runs of the flaky tests. The two extra full runs cost about 14 to 35 minutes, and the ten runs add little when the flaky tests pass on their own.
- Do nothing: keep rerunning the suite in every session's gate when a flake fails.

Expert pass: changed from three full runs plus ten watched runs, always: Session 90 failed 3 of 7 full runs, not 4 of 7, so three runs pass by chance about 19 % of the time; a run takes 6.9 to 17.3 minutes, not hours; and the 60 % floor needed a ceiling beside it.

Refs: `known-issues.yaml:971`, `:986`, `:1010`, `:1025`, `:2904`, grouping `:88-97`, Session 90 handoff `:101-108`, `flake-run.py`, Session 90 RULE-3, M-3, M-8.

### D-1146: How are the flakes reproduced first, and what if they do not show?

**I recommend A: run the flaky tests ten times, and the whole suite once, on the unfixed tests with the machine busy, and record how often they fail.** This gives a before-and-after number. It also gives the hang's timing lines, which decide D-1150. Beside the busy load, one extra process keeps starting short programs, the way other sessions starting their tools did when the hang was seen. If nothing fails, the load is raised once to the whole processor. If too many unrelated tests then fail or hang, it goes back down. A quiet reproduction does not stop the work: each fix also has its own test, which fails before the fix and passes after it.

- B: insist on a reproduction before fixing anything. A quiet hour could stop the session although the code shows the races.
- C: skip the reproduction and fix from the code. This gives no before-and-after rate and no hang timings.
- Do nothing: leave the flakes as they are.

Expert pass: changed from busy loops alone, with a back-off on unrelated failures only: the hang's recorded cause is bursts of process starts, and at the top level every timeout counts as a hang, so that back-off would never have fired.

Refs: grouping `:93`, `known-issues.yaml:2904`, `:2910`, `:2923`, `flake-run.py`, M-8.

### D-1149: Should the test app's windows ignore your real mouse during a run?

**I recommend A: yes, for every test launch, with a switch to turn it off in a single test.** The drag issue records your real cursor moving a drag while a test ran. With A, your mouse passes through the test windows to whatever is under them, and the tests' own pointer still works. A test checks both of those, and another test checks the switch. The keyboard is not blocked. A click that passes through can bring the window under it to the front, so the log now records when a test window is hidden, minimised or covered, and the flaky tests run ten more times with the shield on. If the first check fails, the session turns the shield off again and decides the next step through HDP.

- B: only for the flaky tests. Every other pointer test can still be moved by your mouse.
- C: only record when your mouse enters a test window, and do not block it. The cause would be visible but still there.
- D: turn the shield on only if rows 3 to 5 catch your cursor inside a test window at a failure. Rejected: it depends on you happening to move the mouse during those runs, a quiet run proves nothing about later ones, and the shield is cheap to keep with its switch.
- Do nothing: avoid the mouse while a run is going.

Expert pass: changed from A as first written: widened with a ten-run measurement at row 6, hide, minimise and visibility lines in the log, no change to background throttling, a time limit on AC-9's PowerShell call, and a note that the keyboard is not blocked.

Refs: `known-issues.yaml:971` (A-4, A-7), `electron-app.ts:70`, `download-queue.test.ts:1150-1177`, AC-9, AC-10, M-3.

### D-1150: What happens if the launch hang has a cause outside the tests?

**I recommend A: name each hang's cause from the new timing lines, and act on that cause, hang by hang.**

- **A test problem:** fix it here. If no fix fits the plan's rules, it is registered as a slow launch or close instead.
- **A problem in the app:** register it as an MEU and an issue, with its file, line and phase, and fix it in its own session.
- **Launches or closes that are just too slow on a busy machine:** register an issue with its file, test name and phase, and give it its own session. A hang after the app is up is never put in this class, and neither is a close that began after the test had already timed out or failed.
- **Not seen at all:** keep the timing lines, and leave the issue open with what was learned.

The grouping already says that an app problem gets an MEU and that a separate hang cause gets its own session. The final runs then excuse only a hang in the same test (same file and same test name, or file and line for an app problem) at the recorded phase, and only when the test had not already timed out or failed at that point. The handoff lists each one. One gap is left: if a test's check fails inside a `try` and its `finally` close then hangs, the hang still looks like a close hang. That can only happen in the one test that was registered. An excuse reads only that test's own last launch in the current run: every run writes its timing lines to a new folder named for that run, never to one an earlier attempt left behind, and any line that is not that test's, or any doubt about which launch failed, excuses nothing. That way the drag and zoom fixes are not held by a problem this session has registered. Counting every timeout as a failure was weighed instead and set aside: it would hold those fixes behind a registered problem, which is the same end as C. Excusing a hang lets an existing test's timeout pass, which is an M-11 call. HDP keeps M-11 with you even under a hand-over; under your 2026-11-18 words it is decided on the recommendation, and one line from you overturns it.

- B: fix an app problem here too. This puts app changes into a test session without their own plan and review.
- C: stop and ask you whatever the cause. This holds the drag and zoom fixes, which do not depend on it.
- Do nothing: leave the hang as it is.

Expert pass: changed from one session-wide outcome with a finished launch counted as split: that could excuse a hang in this session's own diagnostics, a close after a stuck test body would read as split, a registered app race would still have held the fixes, and the grouping cites were one line off. Plan review round 1 then narrowed it: a slow-close entry now names its test, and the close check reads whether the test had already timed out instead of timing from the first launch. Plan review round 2 then rebuilt how an excuse finds its evidence: a rerun had added its lines to the earlier attempt's folder, so an old clean close could excuse a new hang. Each run now writes to its own new folder and tags every line with its run, and only that test's own last launch in that run counts.

Refs: grouping `:94`, `:97`, `known-issues.yaml:2904`, `capture-inbox.test.ts:1953`, `human-decision-protocol.md:328-329`, AC-12, AC-13, M-8, M-11.

## Research References

- **Electron `BrowserWindow.setIgnoreMouseEvents(ignore)`:** on Windows it sets `WS_EX_TRANSPARENT` (0x20) and `WS_EX_LAYERED` (0x80000) in the window's extended style (`GWL_EXSTYLE`, -20). OS mouse events go to the window below. There is no getter, so AC-9 reads the style with `GetWindowLongPtrW` on the handle from `getNativeWindowHandle()` (a little-endian 64-bit buffer).
- **Playwright mouse input in Electron:** `page.mouse` and `locator.click()` send CDP `Input.dispatchMouseEvent`, which the renderer handles without OS hit-testing. So a window that ignores OS mouse input still takes it (AC-9).
- **`electronApplication.evaluate(fn, arg)`:** `fn` runs in the main process with the `electron` module as its first argument and must be self-contained. `process.getBuiltinModule('node:fs')` gives `fs` without `require` (Node 22.3 and later; Electron 42).
- **dnd-kit:** the pointer sensor activates after the press moves past its distance; `aria-pressed` on the handle shows the drag is active. The live region (`[id^="DndLiveRegion"]`) carries the announcement that `createQueueAnnouncements` builds, so `moved to position N of M.` means the over target is committed.
- **Playwright list reporter:** failure headers use the separator U+203A. Hangs read `Test timeout of 60000ms exceeded.` and, after them, `Worker teardown timeout`. `ok` lines are counted with `^ +ok +[0-9]+ ` (Session 89 RULE-1).

## Planning receipts

All under `C:/Temp/av-kit/e2e-pointer-flakes/`, read-only against the repository:

| Receipt | What it shows |
|---|---|
| `epf91-probe.py`, `epf91-probe.txt`, `epf91-probe-run.txt` | `HEAD` `ecfa3f3`, a clean tree, one worktree, 24 logical CPUs; line endings, sizes and hashes of the scope; the new files and the handoff absent; 0 anchor misses; the three issues `open`; grouping `:163` `proposed`; highest D-id D-1134, D-1145 to D-1154 free; highest MEU-159; `decision_sources` without and with this plan |
| `epf91-assert-counts.txt` | The base `BANNED` token counts and assertion-line counts per spec file |
| `epf91-selftest-flake-run.txt`, `epf91-selftest-assert-check.txt` | The plan-time scripts' selftests: 122 and 17 checks, 0 failures each |
| `epf91-f3-mutants.txt` | Ten weakened copies of `flake-run.py` (no run-id filter, foreign lines ignored, `exist_ok` folder, appended receipt, any clean launch, repeats ignored, earlier launches ignored, substring title, no line check, `--split-hang` with repeats); each fails the selftest |
| `epf91-sim-checks.txt` | Row 3's, row 7's and row 8's checks run on fake receipts, with row 8's against a stale earlier invocation, a missing `run files` line, names and run ids of another invocation, a doubled invocation line and missing bound files |
| `epf91-killcheck.txt` | `flake-run.py --kill-check --children 2`: 2 interpreters accepted, 0 left, `PASS` |
| `epf91-killcheck-churn.txt` | `flake-run.py --kill-check --children 2 --churn`: 2 interpreters accepted, the churn child alive at the stop, 0 left, `PASS` |
| `s91-expert-pass.txt` | The fresh-context expert pass on D-1145, D-1146, D-1149 and D-1150, with the coordinator's checks (HDP §5a) |
| `C:/Temp/av-kit/epf-plan-review-round-1.md` | Plan review round 1, `changes_required`: F1 (a split entry had no test identity, so any unwatched hang in that phase was excused) and F2 (the close guard measured from the first launch, so a body timeout after setup read as a close hang); both answered in rows 7 and 8, `PHASE_LINES`, D-1150 and `flake-run.py` |
| `C:/Temp/av-kit/epf-plan-review-round-2.md` | Plan review round 2: F1 and F2 fixed; F3 (a rerun of row 8 appended to the earlier attempt's diag folder, so stale clean-close evidence could excuse a current body timeout), with the ledger's V30 mechanism-class stop. Answered by the evidence binding in rows 7 and 8, `PHASE_LINES`, AC-2, AC-4, AC-13, S9, S12, D-1150 and `flake-run.py` |
| `epf91-ruff-fmt.txt`, `epf91-ruff-check.txt` | `ruff format --check` and `ruff check` on the plan folder's Python |
| `epf91-peer-task-full.txt`, `epf91-peer-task-rows.txt` | Session 90's task rows, read as the shape for this plan's rows |

## Validation stage contract

| Stage | Checks | Where |
|---|---|---|
| Plan review | This plan and `task.md`, against the three issues, grouping §3 Session 91 and D-1132, Session 90's harness, and the code reads above | `epf-plan-2026-11-17-e2e-pointer-flakes` |
| Row checks | Each row's validation command | `task.md` |
| Session gate | §Session gate | H1-2 |
| Execution review | The delta from `baseline.sha` in the §Files Modified paths, against AC-1 to AC-15 | `epf-execution-2026-11-17-e2e-pointer-flakes` |
