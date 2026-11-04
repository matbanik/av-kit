# Walkthrough — 2026-10-14-capture-render-fidelity (Session 36)

Durable evidence for `task.md`. Receipts are working data under `C:/Temp/av-kit/`; the decisive lines are copied here as `evidence.v1`.

## Execution message

- **Execution authorization:** `USER_EXPLICIT` 2026-10-16, Mat, in the Claude Code chat, verbatim: "proceed". It followed the round-3 plan review (Codex `gpt-6.1-sol`, `approved`, review file §Recheck — Round 3) and my presentation of that verdict under `plan_to_exec_gate: human`.
- **D-12 (arrow head size):** the message is silent on it, so the default applies: `ARROW_HEAD` (plan §Single-statement contracts). TA-1 and TA-2 stay in `TEST_AMENDMENTS`.
- **Plan-review ledger note:** the ledger loop `s36-plan-2026-10-14-capture-render-fidelity` records round 1 only. Round 2 (`changes_required`, PR-6 procedural gate) and round 3 (`approved`) were refused by the wrapper's ledger step: round 2 because the verdict schema needs a non-empty `findings` array for `changes_required`, round 3 because its `round: 3` did not match the ledger's expected round 2. Neither verdict was edited. The review file holds all three rounds. Reported to Mat 2026-10-14; execution authorization came after that report.
- **Baseline move:** planning started from `7861020` (origin/main). Before execution Mat merged Session 31 into main (`c72fc44`) and committed the plan folder and plan review as `534beb1` on this branch. `git diff --name-only 7861020 c72fc44` touches, in this plan's scope, only `.agent/context/current-focus.md`, `known-issues.md`, `known-issues.yaml`, `meu-status.yaml` and `docs/BUILD_PLAN.md`; no capture product, test or fixture file. Per the plan §Goal, the live HEAD at execution start is the baseline (`baseline.sha`).
- **Worktree venv:** the first row-0 run failed at `uv sync --frozen --all-packages` (exit 2): the worktree `.venv` was CPython 3.14 and `spacy` has no cp314 wheel. I recreated it with `uv venv --clear --python 3.12.12 .venv` (the interpreter the lockfile resolves for) and re-ran row 0 unchanged. No lockfile or pyproject edit.

## Baseline

`baseline.sha` = `534beb174e2be1a97fc0cd248f53b4b8cdc83e49` (HEAD at execution start). Row 0 exit 0.

```json
{"schema_version":"evidence.v1","check_id":"s36-row0-prereq","command":"task.md row 0 (prereq step)","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"graphify-out absent; MEU-39/59/67 approved; MEU-82/83/84 pending","phase":"targeted","exit_code":0,"result":"pass","tested_state":"HEAD 534beb1, clean tree, .venv CPython 3.12.12","output":"prereq problems: []","fresh":true}
{"schema_version":"evidence.v1","check_id":"s36-base-py","command":"rtk proxy uv run pytest tests/ -q --tb=no","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"Python baseline","phase":"full","exit_code":1,"result":"fail","tested_state":"HEAD 534beb1, clean tree","output":"2 failed, 653 passed, 1 warning in 188.67s. FAILED tests/unit/test_packaging_backend.py::test_pack_dist_onedir_layout[AC-24.10]; FAILED tests/unit/test_packaging_installer.py::test_nsis_pack_check_script[AC-25.10]","fresh":true}
{"schema_version":"evidence.v1","check_id":"s36-base-ui","command":"rtk proxy npm --prefix ui run test","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"UI unit baseline","phase":"full","exit_code":0,"result":"pass","tested_state":"HEAD 534beb1, clean tree","output":"Test Files 84 passed (84); Tests 800 passed (800)","fresh":true}
{"schema_version":"evidence.v1","check_id":"s36-base-build","command":"rtk proxy npm --prefix ui run build","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"UI build baseline","phase":"full","exit_code":0,"result":"pass","tested_state":"HEAD 534beb1, clean tree","output":"built in 8.61s","fresh":true}
{"schema_version":"evidence.v1","check_id":"s36-base-e2e","command":"rtk proxy npm --prefix ui run test:e2e -- tests/e2e/capture-inbox.test.ts","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"Electron capture-inbox baseline","phase":"targeted","exit_code":0,"result":"pass","tested_state":"HEAD 534beb1, clean tree","output":"28 passed (1.3m)","fresh":true}
```

**Baseline failing set:** Python `AC-24.10` and `AC-25.10` only. Both are packaging tests that need the pack script's dist tree (`PACK_DIST_EXE missing — pack script has not produced an onedir tree`), which a fresh worktree does not have. They are environmental, outside capture, and excluded from this session's regressions. UI unit, build and capture-inbox Electron have no failures.

## Census

Row 1 receipt `C:/Temp/av-kit/s36-census.txt`: exit 0, `census hits: 166` (165 hits plus the rtk banner line). Every hit was dispositioned by a rules script that exits 1 on any unclassified hit (receipt `C:/Temp/av-kit/s36-census-dispo.txt`: `census hits: 165; supplementary: 5; unclassified: 0`). The pattern cannot see `<line>` reads that have no `x2`/`y2` on the same line, so a grep for `arrow"] line` adds five supplementary hits.

Counts over the 165 census hits: unaffected 155, TA-1 2, TA-2 3, TA-3 2, TA-4 2, TA-5 1. Supplementary: TA-5 1, TA-6 1, unaffected 2, **new-contradiction 1**.

Required confirmations:
- **AC-35.13** (`test_capture_adapter.py:387-404`) is unaffected. It asserts that the adapter source contains `polygon` and `.line(`/`draw.line` and the font names. `BAKE_AA` keeps `draw.line` and `draw.polygon` (AC-83.8 pins this).
- **AC-67.1** (flatten byte oracle, `test_api_capture_flatten.py:388`) is unaffected. Its `expected` bytes come from the same adapter `bake` inside the test, so the new `_apply_arrow` changes both sides equally.
- **`capture-hit-test.test.ts`** is unaffected. It has no census hit. `hitArrowBody` tests the model's from→to segment, and `SHAFT_END` changes only the rendered `<line>`, not the model.

| File | Lines | Disposition | Reason |
|---|---|---|---|
| `ui/tests/e2e/capture-picker.test.ts` | 30, 31, 102, 103 | unaffected | `CaptureShot` field types/fixture values; no shape change |
| `ui/tests/e2e/capture-inbox.test.ts` | 12, 13, 38, 39, 284, 285 | unaffected | `CaptureShot` field types/fixture values; no shape change |
| `ui/tests/e2e/capture-inbox.test.ts` | 226, 227, 331, 332 | unaffected | Open file/folder visibility and disabled states; MEU-84 keeps both testids and the no-selection states (folder falls back to inboxDir) |
| `ui/tests/e2e/capture-inbox.test.ts` | 500, 1388 | unaffected | seam writes `annotated_path` on annotate/revert; RECONCILE is server-side and the seam is a fake |
| `tests/unit/test_capture_adapter.py` | 21, 22, 177, 178, 205, 206 | unaffected | repository round-trip of the two path fields; no schema change |
| `tests/unit/test_capture_adapter.py` | 438, 444, 445 | TA-2 | AC-59.2 Python head values → `ARROW_HEAD` |
| `ui/tests/e2e/download-queue.test.ts` | 77, 451, 452 | unaffected | other feature surface: MEU-84 changes only the capture commands and appends to a log inside the main-process `AVKIT_E2E` branch; renderer bridge stubs, source regexes and per-feature IPC ledgers are untouched |
| `ui/tests/e2e/convert-queue.test.ts` | 79, 486, 487 | unaffected | other feature surface: MEU-84 changes only the capture commands and appends to a log inside the main-process `AVKIT_E2E` branch; renderer bridge stubs, source regexes and per-feature IPC ledgers are untouched |
| `tests/unit/test_domain_capture.py` | 42, 43, 79, 80 | unaffected | domain field list/defaults; no shape change |
| `ui/tests/unit/capture-arrow-head.test.ts` | 6, 8 | TA-1 | AC-59.2 preview head values (12 / 0.4) → `ARROW_HEAD` (factor 5, angle 0.45, min 10) |
| `ui/tests/unit/app-shell-wiring.test.ts` | 24, 25 | unaffected | other feature surface: MEU-84 changes only the capture commands and appends to a log inside the main-process `AVKIT_E2E` branch; renderer bridge stubs, source regexes and per-feature IPC ledgers are untouched |
| `ui/tests/e2e/tts-generate.test.ts` | 391, 392, 532 | unaffected | other feature surface: MEU-84 changes only the capture commands and appends to a log inside the main-process `AVKIT_E2E` branch; renderer bridge stubs, source regexes and per-feature IPC ledgers are untouched |
| `tests/unit/test_capture_service.py` | 150, 185, 516, 629 | unaffected | scan_inbox import/list semantics; RECONCILE only clears paths whose file is missing and these shots keep their files |
| `tests/unit/test_capture_service.py` | 166, 169 | unaffected | AC-36.2 vanished original → row deleted; RECONCILE runs over survivors only (AC-84.1(e) characterises this) |
| `tests/unit/test_capture_service.py` | 334, 335, 336, 337, 339, 345, 346, 390, 391, 1007, 1009 | unaffected | annotate/revert/clear path semantics; RECONCILE does not touch annotate or revert |
| `tests/unit/test_capture_service.py` | 955 | unaffected | concurrency test asserts no deletes; RECONCILE saves, never deletes, under the same CAPTURE_FILE_LOCK |
| `ui/tests/e2e/transcript-queue.test.ts` | 184, 185 | unaffected | other feature surface: MEU-84 changes only the capture commands and appends to a log inside the main-process `AVKIT_E2E` branch; renderer bridge stubs, source regexes and per-feature IPC ledgers are untouched |
| `ui/tests/e2e/test-ids.ts` | 194, 195 | unaffected | testid constants unchanged |
| `ui/tests/unit/capture-page.test.ts` | 80, 81, 301, 302 | unaffected | testid inventory unchanged |
| `ui/tests/unit/capture-page.test.ts` | 248 | unaffected | filmstrip must not open paths; MEU-84 adds no filmstrip open |
| `ui/tests/unit/capture-page.test.ts` | 304, 305 | unaffected | AC-39.12 source regex: capture sources still call openPath and showItemInFolder |
| `ui/tests/unit/capture-text-metrics.test.ts` | 6, 9 | TA-3 | `hanging` → `alphabetic` |
| `ui/tests/unit/capture-page.behavior.test.ts` | 62, 63, 480, 1390, 1399, 1405, 1408, 2116 | unaffected | fixture `annotated_path` values; no test asserts an openPath/showItemInFolder target, so retargeting to the viewed file breaks nothing |
| `ui/tests/unit/capture-page.behavior.test.ts` | 98, 99 | unaffected | no-op bridge stubs; no call-argument assertions in this file |
| `ui/tests/unit/capture-page.behavior.test.ts` | 1062, 1079, 1080 | unaffected | Open file/folder/delete testids and disabled states unchanged |
| `ui/tests/unit/capture-page.behavior.test.ts` | 1744 | TA-5 | AC-66.11 x2/y2 read moves to the `<g>` ('750'/'400') |
| `ui/tests/unit/capture-page.behavior.test.ts` | 1772, 1775 | unaffected | AC-66.11 negative: before/after equality on the `<line>` of an L = 50 arrow; the `<line>` exists |
| `ui/tests/unit/capture-page.behavior.test.ts` | 1834, 1869 | TA-4 | AC-59.19 viewport: dominant-baseline → alphabetic, text y → ann.y + ascent; plate asserts stay |
| `ui/tests/unit/capture-main.behavior.test.ts` | 128, 130, 131 | unaffected | AC-39.16 tray Open inbox folder still uses showItemInFolder; the tray is not in MEU-84 scope |
| `ui/tests/unit/chrome-zorivest.test.ts` | 121, 122 | unaffected | other feature surface: MEU-84 changes only the capture commands and appends to a log inside the main-process `AVKIT_E2E` branch; renderer bridge stubs, source regexes and per-feature IPC ledgers are untouched |
| `ui/tests/unit/console-polish.test.ts` | 32, 33 | unaffected | other feature surface: MEU-84 changes only the capture commands and appends to a log inside the main-process `AVKIT_E2E` branch; renderer bridge stubs, source regexes and per-feature IPC ledgers are untouched |
| `ui/tests/unit/convert-page.test.ts` | 598, 599 | unaffected | other feature surface: MEU-84 changes only the capture commands and appends to a log inside the main-process `AVKIT_E2E` branch; renderer bridge stubs, source regexes and per-feature IPC ledgers are untouched |
| `ui/tests/unit/convert-page.behavior.test.ts` | 37, 38, 375 | unaffected | other feature surface: MEU-84 changes only the capture commands and appends to a log inside the main-process `AVKIT_E2E` branch; renderer bridge stubs, source regexes and per-feature IPC ledgers are untouched |
| `ui/tests/unit/convert-page.behavior.test.ts` | 1551 | unaffected | comment containing `hanging` (an HTTP request), not a text baseline |
| `tests/e2e/test_api_capture_flatten.py` | 191, 192, 431, 432 | unaffected | response field lists; no shape change |
| `tests/e2e/test_api_capture_flatten.py` | 237, 238, 358 | unaffected | null paths after revert/clear; unchanged |
| `tests/e2e/test_api_capture_flatten.py` | 388 | unaffected | AC-67.1 byte oracle: `expected` is produced by the same adapter `bake` in-test, so the new `_apply_arrow` changes both sides equally |
| `tests/e2e/test_api_capture_flatten.py` | 602 | unaffected | lossy annotated path naming unchanged |
| `ui/tests/unit/downloader-page.test.ts` | 398, 399 | unaffected | other feature surface: MEU-84 changes only the capture commands and appends to a log inside the main-process `AVKIT_E2E` branch; renderer bridge stubs, source regexes and per-feature IPC ledgers are untouched |
| `ui/tests/unit/gui-actions-audit.test.ts` | 63 | unaffected | `capture:open_folder` still maps to the `capture-open-folder` testid |
| `ui/tests/unit/gui-actions-audit.test.ts` | 71 | unaffected | audit cell classifier; other feature surface: MEU-84 changes only the capture commands and appends to a log inside the main-process `AVKIT_E2E` branch; renderer bridge stubs, source regexes and per-feature IPC ledgers are untouched |
| `tests/e2e/test_api_captures.py` | 78, 79, 201, 202, 354 | unaffected | router tests over `FakeCapture`; the real-service RECONCILE is not exercised (AC-84.2 adds its own real-file test) |
| `ui/tests/unit/downloader-page.behavior.test.ts` | 60, 61, 478, 481 | unaffected | other feature surface: MEU-84 changes only the capture commands and appends to a log inside the main-process `AVKIT_E2E` branch; renderer bridge stubs, source regexes and per-feature IPC ledgers are untouched |
| `ui/tests/unit/downloader-page.behavior.test.ts` | 1668 | unaffected | comment containing `hanging` (an HTTP request), not a text baseline |
| `ui/tests/unit/header-toggles.test.ts` | 84, 85 | unaffected | other feature surface: MEU-84 changes only the capture commands and appends to a log inside the main-process `AVKIT_E2E` branch; renderer bridge stubs, source regexes and per-feature IPC ledgers are untouched |
| `ui/tests/unit/helpers/electron-stub.ts` | 86, 87 | unaffected | main-process electron `shell` stub; `recordE2eShell` only runs in the AVKIT_E2E branch and does not change the shell calls |
| `ui/tests/unit/settings-emphasis.test.tsx` | 36, 37 | unaffected | other feature surface: MEU-84 changes only the capture commands and appends to a log inside the main-process `AVKIT_E2E` branch; renderer bridge stubs, source regexes and per-feature IPC ledgers are untouched |
| `ui/tests/unit/settings-rail.test.tsx` | 36, 37 | unaffected | other feature surface: MEU-84 changes only the capture commands and appends to a log inside the main-process `AVKIT_E2E` branch; renderer bridge stubs, source regexes and per-feature IPC ledgers are untouched |
| `ui/tests/unit/shell-ipc-ledger.test.ts` | 28, 29, 31, 32, 37, 44 | unaffected | renderer `__e2eIpc` ledger; D-17 adds a separate main-process log and leaves this one unchanged |
| `ui/tests/unit/secret-paths.test.ts` | 15, 16, 34, 38, 51, 52, 57, 62 | unaffected | other feature surface: MEU-84 changes only the capture commands and appends to a log inside the main-process `AVKIT_E2E` branch; renderer bridge stubs, source regexes and per-feature IPC ledgers are untouched |
| `ui/tests/unit/settings-page.test.ts` | 61, 62 | unaffected | other feature surface: MEU-84 changes only the capture commands and appends to a log inside the main-process `AVKIT_E2E` branch; renderer bridge stubs, source regexes and per-feature IPC ledgers are untouched |
| `ui/tests/unit/transcript-page.test.ts` | 223, 294 | unaffected | other feature surface: MEU-84 changes only the capture commands and appends to a log inside the main-process `AVKIT_E2E` branch; renderer bridge stubs, source regexes and per-feature IPC ledgers are untouched |
| `ui/tests/unit/tts-page.test.ts` | 369, 373, 374 | unaffected | other feature surface: MEU-84 changes only the capture commands and appends to a log inside the main-process `AVKIT_E2E` branch; renderer bridge stubs, source regexes and per-feature IPC ledgers are untouched |
| `ui/tests/unit/transcript-page.behavior.test.ts` | 60, 69, 70 | unaffected | other feature surface: MEU-84 changes only the capture commands and appends to a log inside the main-process `AVKIT_E2E` branch; renderer bridge stubs, source regexes and per-feature IPC ledgers are untouched |
| `ui/tests/unit/tts-page.behavior.test.ts` | 62, 63, 65, 66, 413, 440 | unaffected | other feature surface: MEU-84 changes only the capture commands and appends to a log inside the main-process `AVKIT_E2E` branch; renderer bridge stubs, source regexes and per-feature IPC ledgers are untouched |
| `ui/tests/e2e/capture-inbox.test.ts` | 1165 (supplementary) | TA-6 | AC-66.14 reads x1..y2 from the `<line>`; under `SHAFT_END` x2/y2 move to the shaft end, so TA-6 moves the x2/y2 reads (:1168-1169) to the `<g>`; x1/y1 stay `from` on both elements |
| `ui/tests/unit/capture-page.behavior.test.ts` | 1331 (supplementary) | new-contradiction | AC-65.3 reads `stroke-width` from `[data-annotation-type="arrow"] line` after a drag (25,25)→(150,150) on the 200×200 bound surface over the 8×8 `SHOT`: fit s = 25, offset 0, so the arrow is (1,1)→(6,6), L = 7.07. At stroke 7 head = 35 and back = 35·cos 0.45 − 1 = 30.45 ≥ L, so `SHAFT_END` renders no `<line>` and `line` is null. No drag on an 8×8 image can exceed back (max diagonal 9.9 < 30.45). Outside `TEST_AMENDMENTS` → S2 |
| `ui/tests/unit/capture-page.behavior.test.ts` | 1742 (supplementary) | TA-5 | AC-66.11 x1/y1 still `from` on the `<line>`; TA-5 moves the x2/y2 read (:1744) to the `<g>` |
| `ui/tests/unit/capture-page.behavior.test.ts` | 1771 (supplementary) | unaffected | AC-66.11 negative: arrow is a 100 CSS px drag at zoom s = 2, so L = 50 image px at default stroke 3 > back 12.5, so the `<line>` exists; the test only compares before/after for equality |
| `ui/tests/unit/capture-page.behavior.test.ts` | 1774 (supplementary) | unaffected | same test as :1771; equality of before/after holds under any deterministic shaft end |


**Result: one `new-contradiction` → S2.** Row 1 was `[B]` (c) on D-20 below (D-21 is a related scope question). Both were resolved on 2026-10-16: TA-7 approved (A-1), and the head outline added to MEU-83 as AC-83.9 (A-2). See [human-gate-decision.md](human-gate-decision.md). Row 1 is `[x]`. Per plan §Stop Conditions S2, there is no test edit and execution holds at row 1.

## Decision — S2 (row 1)

These briefs follow `.agent/docs/human-decision-protocol.md` in order: a precedent sweep (receipts `C:/Temp/av-kit/s36-d66-precedent.txt` exit 0, `s36-d67-precedent.txt`, `s36-d67-precedent2.txt`), web research, the obviousness test, then the brief. The ids continue the plan's Decision Log (D-1..D-19). An earlier draft called D-20 "D-66", which collides with triage D-66 in `.agent/context/known-issues.yaml:2036`.

### D-20: How should AC-65.3 check the stroke edit once short arrows have no `<line>`?   [two-way, hard gate: test amendment (S2)] [execution, row 1]

**Recommendation:** approve **TA-7**, a test-only amendment to `capture-page.behavior.test.ts:1331-1332`. The test would read the arrow's `<polygon>` and assert that the head length (tip→left) is 35, which is `ARROW_HEAD` factor 5 × stroke 7. That keeps the test's intent (editing stroke on a selected arrow changes the rendered arrow) through an element that exists for every non-zero arrow. At the default stroke 3 the head is 15, so a stroke edit that never reaches the render still fails. There is no product change and no contract change, and the file is already on MEU-83's Files Modified list.

Proposed replacement for lines 1331–1332 (nothing else in the test changes):

```ts
const head = document.querySelector('[data-annotation-type="arrow"] polygon') as SVGPolygonElement
const [tip = [], left = []] = (head.getAttribute('points') ?? '').split(' ').map((p) => p.split(',').map(Number))
expect(Math.hypot(Number(tip[0]) - Number(left[0]), Number(tip[1]) - Number(left[1]))).toBeCloseTo(35, 9)
```

**Why it breaks:** AC-65.3 (`capture-page.behavior.test.ts:1323-1345`) drags (25,25)→(150,150) on the 200×200 bound surface over the 8×8 `SHOT`. Fit scale is 25 with zero offset, so the arrow is (1,1)→(6,6) in image px, L = 7.07. After the stroke edit to 7, head = 35 and back = 35·cos 0.45 − 1 = 30.52 ≥ L. `SHAFT_END` then renders the head only, with no `<line>`. `document.querySelector('[data-annotation-type="arrow"] line')` returns null and `.getAttribute` throws. The existing assertion is outside `TEST_AMENDMENTS` (TA-1..TA-6), so this is S2.

**Why not the others**
| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ TA-7: assert head length from the `<polygon>` | — | — | plan §TEST_AMENDMENTS TA-5/TA-6; https://testing-library.com/docs/react-testing-library/intro |
| ⚠️ Add `data-stroke-width` to the arrow `<g>`; the test reads it | Reads the stored value directly, from the same element TA-5/TA-6 read | Adds a test-only attribute to the product. It reads the model value, not the render, so it would pass even if the render ignored stroke. A plain `stroke-width` on the `<g>` instead would be inherited by the head polygon and thicken its outline | `CaptureViewport.tsx:122-130`; https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/stroke-width |
| ❌ Lengthen the drag | No new oracle | Impossible on the 8×8 `SHOT`: the longest diagonal is 9.9 < back 30.52 at stroke 7. It would need a larger fixture for this one test, a wider edit than TA-7 | `capture-page.behavior.test.ts:59-66`, `capture-fit-map.ts:17-28` |
| ❌ Change `SHAFT_END` to always emit a (degenerate) `<line>` | No test edit | Changes an approved contract, which sends the plan back to planning. The preview gains an element the bake does not draw, against this session's fidelity goal | plan §SHAFT_END; https://github.com/excalidraw/excalidraw/issues/6712 |

**Precedent:**
| Where | What it decided | Who | Applies |
|---|---|---|---|
| `AGENTS.md:57` | A proven wrong expectation needs a sourced amendment plus explicit human authorization or independent review | rule | directly |
| `implementation-plan.md:96`, `:406` (S2) | This plan listed TA-1..TA-6 in advance and sends any other census contradiction to the human with a brief, with no test edit. This is why D-20 stops for you rather than going to independent review | plan, approved by Codex round 3 and by you ("proceed") | directly |
| `2026-10-02-capture-flatten-backup/human-gate-decision.md:73-85` (A-3) | The row-1 census found pins outside TA-1..TA-7, an S2 stop; added as TA-8 | `USER_EXPLICIT` "Approve TA-8 (Recommended)" | directly (same class, same stop) |
| `2026-09-28-p11-capture-settings/human-gate-decision.md:47-54` (TM-11/TM-12) | Census follow-up in this same test file: the setup moved and the assertions' intent was kept | `USER_EXPLICIT` "Approve TM-11 + TM-12 (Recommended)" | directly |
| `2026-10-10-gui-polish-residuals/human-gate-decision.md:95-102` (A-6) | Knock-on test data re-baselined after an approved change, with no assertion code changed | `USER_EXPLICIT` "Re-baseline 16 rows (Recommended)" | by analogy |
| this plan, TA-5 / TA-6 | A `<line>` read invalidated by `SHAFT_END` moves to an element that keeps the asserted value | planner; plan approved | directly (same mechanism) |

**Research:** Pomera MCP web search (`pomera_web_search`, tavily and exa).
- *Authority:* https://testing-library.com/docs/react-testing-library/intro. Tests should assert what the user sees, and `data-testid`-style hooks are an escape hatch. This favours reading the rendered polygon (TA-7) over a test-only data attribute.
- *Authority:* https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/stroke-width (SVG2: initial value 1, inherited). A `stroke-width` on the `<g>` reaches the polygon, which is the con of the ⚠️ option.
- *Practice:* https://github.com/excalidraw/excalidraw/issues/6712. Head size on short arrows is a real rendering case in production editors, so a head-only short arrow is legitimate output and the test should not depend on a shaft existing.
- *AI-era:* https://github.com/TDM-Technologies/strictlock/tree/main/test-protection-guard, https://juliapottinger.com/working-with-coding-agents-as-qa-engineer/, https://www.fundesk.io/test-driven-development-ai-agents-guide and https://www.linkedin.com/posts/yevhen-vorkov_ai-agent-guardrails-activity-7485276654576041984-OkNa. All four keep assertion changes by coding agents behind a human or a guard. They support keeping this gate human; they do not argue for a different option.

**Obviousness test:** (1) convergence holds: TA-5/TA-6 and the Testing Library guidance agree on TA-7. (2) It is two-way, but a test-assertion change outside `TEST_AMENDMENTS` is on the hard-gate list (plan S2, `AGENTS.md:57`), so this test fails. (3) No product fork, since the change is test-only. (4) It sets no governance number. The option is settled (`Research-backed`), but authorizing it is yours, and the protocol never loosens a hard gate.
**Reversibility / risk:** two-way. It is one assertion in one test. If it is wrong, AC-65.3 under-checks or over-checks the stroke edit; no product behaviour depends on it.
**If you do not answer:** row 1 stays `[B]` and rows 2–9 do not start. MEU-82 (text) does not depend on this, but the plan's S2 rule stops the whole run.

### D-21: Should MEU-83 also remove the 1 px outline the preview head inherits?   [product-preference: scope addition to an approved plan] [execution, row 1]

**Recommendation:** add it to MEU-83 as a plan amendment. Set `stroke="none"` on the head `<polygon>` in `CaptureViewport.tsx` and add one AC with a Red-first test that the arrow polygon carries `stroke="none"`. Leave the `<g>`'s `stroke={ann.color}` in place, because the colour tests read it (`capture-page.behavior.test.ts:637-666`, `:832-841`, `:921-932`). MEU-83 exists to make the preview head match the bake, and this is the one remaining difference in the head: one attribute in a file MEU-83 already edits.

**What it is:** the arrow `<g>` sets `stroke={ann.color}` and the `<polygon>` sets only `fill`. The polygon inherits the stroke at the SVG default width of 1, so the preview head is drawn with a 1 px outline the bake does not draw, making it about 0.5 px larger on every side. No plan contract or AC covers it (AC-83.4, `implementation-plan.md:202`, checks only the points).

**Why not the others**
| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ Add to MEU-83: polygon `stroke="none"` plus a new AC | — | — | `CaptureViewport.tsx:118-144`; https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/stroke-width |
| ⚠️ Log it in `known-issues.yaml` and fix it in a later session | The approved scope stays as reviewed | MEU-83 ships "preview head matches bake" with a known 0.5 px difference, and a later session has to reopen the same file for one attribute | `.agent/docs/issue-lifecycle-guide.md:52-57` |
| ❌ Move `stroke` from the `<g>` to the `<line>` only | Also removes the outline | Breaks the colour tests that read the `<g>` stroke (`:637-666`, `:832-841`, `:921-932`), so it needs more test amendments and another S2 | `capture-page.behavior.test.ts` |
| ❌ Do nothing and do not log it | No work | Leaves a known fidelity gap with no record, which the protocol treats as silence | protocol §6 |

**Precedent:**
| Where | What it decided | Who | Applies |
|---|---|---|---|
| `.agent/workflows/tdd-implementation.md:23` | Authorized user scope changes are folded into plan, task and review scope | rule | directly |
| `.agent/docs/issue-lifecycle-guide.md:52-57` | Out-of-scope findings go to `known-issues.yaml` (the SSOT) | rule | directly (the fallback) |
| `docs/execution/reflections/2026-10-01-capture-viewport-chrome-reflection.md:39` | A fidelity gap the FIC never measured was noticed by you outside the checklist | lesson | by analogy: fidelity gaps outside the FIC tend to slip |

**Research:** Pomera MCP web search. *Authority:* https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/stroke-width (SVG2 `stroke-width` initial 1, inherited). This confirms the outline exists in every SVG renderer and that `stroke="none"` on the polygon removes it without touching the `<g>`.
**Obviousness test:** (1) convergence holds. (2) It is two-way. (3) It fails: adding scope to a plan that was approved after review is a change to what this session ships, and only you can authorize it (`tdd-implementation.md:23`). (4) It sets no governance number.
**Reversibility / risk:** two-way. If it is wrong, the head loses an outline the bake never had; nothing else reads the polygon stroke.
**If you do not answer:** I log it in `known-issues.yaml` at closeout and do not change MEU-83's scope.

**Decision Log drafts** (copied into the MEU-83 handoff `## Decision Log` once resolved):

```yaml
decision_log:
  - id: D-20
    stage: execution
    question: "How should AC-65.3 check the stroke edit once short arrows render no <line>?"
    resolution: human
    class: two-way
    chosen: "TA-7: assert the rendered head polygon length"
    source_tag: Human-approved
    precedents:
      - "AGENTS.md:57 — wrong expectation needs sourced amendment plus human authorization or independent review"
      - "implementation-plan.md:406 — S2: an unlisted census contradiction stops for the human"
      - "2026-10-02-capture-flatten-backup/human-gate-decision.md:73-85 — A-3/TA-8 user-approved at the same stop"
      - "2026-09-28-p11-capture-settings/human-gate-decision.md:47-54 — TM-11/TM-12 user-approved in the same file"
      - "implementation-plan.md §TEST_AMENDMENTS TA-5/TA-6 — <line> reads moved to elements that keep the value"
    research:
      engine: tavily+exa
      sources:
        - "https://testing-library.com/docs/react-testing-library/intro — assert rendered output; test ids are an escape hatch"
        - "https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/stroke-width — initial 1, inherited"
        - "https://github.com/excalidraw/excalidraw/issues/6712 — short-arrow head sizing is a real production case"
        - "https://github.com/TDM-Technologies/strictlock/tree/main/test-protection-guard — agent test edits stay guarded"
    reasoning: "TA-7 keeps the test's intent through an element every non-zero arrow renders; data-stroke-width reads the model not the render; a longer drag is impossible on 8x8; an always-present <line> reopens an approved contract. Hard gate (S2) keeps authorization human."
    human_message_reference: "USER_EXPLICIT 2026-10-16 'Approve TA-7 (Recommended)'"
  - id: D-21
    stage: execution
    question: "Should MEU-83 also remove the 1 px outline the preview head inherits from the <g> stroke?"
    resolution: human
    class: product-preference
    chosen: "Add to MEU-83: polygon stroke=none, AC-83.9"
    source_tag: Human-approved
    precedents:
      - ".agent/workflows/tdd-implementation.md:23 — authorized scope changes fold into plan/task/review"
      - ".agent/docs/issue-lifecycle-guide.md:52-57 — out-of-scope findings go to known-issues.yaml"
      - "2026-10-01-capture-viewport-chrome-reflection.md:39 — a fidelity gap outside the FIC was caught by the user"
    research:
      engine: tavily+exa
      sources:
        - "https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/stroke-width — initial 1, inherited"
    reasoning: "One attribute closes the last preview/bake head difference in a file MEU-83 already edits; moving stroke off the <g> breaks colour tests; deferring leaves a known gap in the MEU meant to close it."
    human_message_reference: "USER_EXPLICIT 2026-10-16 'Add to MEU-83 (Recommended)'"
```

## MEU-82 Red (row 2)

Row 2 command (task.md row 2, verbatim) exit **0** on 2026-10-16.

| Receipt | Child exit | Result |
|---|---|---|
| `C:/Temp/av-kit/s36-82-pin.txt` | 0 | `9 passed`: AC-82.2 (Pillow ascent = fixture for all 17 sizes; four off-by-one comparator self-checks; `la`−`ls` bottom = ascent) and AC-82.5 (committed PNGs = fresh bake; bake at `y+1` differs; writer reproduces both PNGs). Green by design: they pin the existing bake. |
| `C:/Temp/av-kit/s36-82-red-ui.txt` (`.exit` = 1) | 1 | `Tests 6 failed \| 84 passed (90)`. |
| `C:/Temp/av-kit/s36-82-red-build.txt` | 0 | build OK |
| `C:/Temp/av-kit/s36-82-red-e2e.txt` (`.exit` = 1) | 1 | `1 failed` (AC-82.6) |
| `C:/Temp/av-kit/s36-82-red-check.txt` | 0 | `red-check: 2 receipt(s), 0 problem(s)` |

Red reasons (diagnostic lines from the receipts):

| Test | Diagnostic |
|---|---|
| AC-59.19 TEXT_MODULE (TA-3) | `AssertionError: expected 'hanging' to be 'alphabetic'` |
| AC-82.1 fixture + `SEGOE_UNITS` | `AssertionError: expected undefined to be 2048` (`SEGOE_UI_UNITS_PER_EM` is declared-new) |
| AC-82.1 naive-formula negative | `TypeError: mod.segoeAscentPx is not a function` (declared-new) |
| AC-82.3 | `AssertionError: expected 'hanging' to be 'alphabetic'` |
| AC-59.19 viewport (TA-4) | `AssertionError: expected 'hanging' to be 'alphabetic'` |
| AC-82.4 page | `AssertionError: expected '20' to be '38'` |
| AC-82.6 Electron | `Error: expect(received).toBeLessThanOrEqual(expected)`, `Received: 8` (ink top) |

AC-82.6 boxes on the baseline code (image px; the image box sits at CSS `(719.5, 456.5)`):

| View | Ink (l, t, r, b) | Plate (l, t, r, b) |
|---|---|---|
| Original + SVG preview | 23, **34**, 48, **57** | 20, 42, 50, 66 |
| Annotated (bake) | 23, **42**, 48, **65** | 21, 43, 51, 65 |

The preview ink sits 8 px above the bake (the `hanging` baseline), which is the defect MEU-82 fixes. The plates already agree within 1 px.

Files written in row 2:
- `tools/capture_bake_fixture.py` (new, `TEXT_FIXTURE` writer, `--out DIR`).
- `ui/tests/e2e/fixtures/capture-geometry.json` (new; `segoe_ascent` only; sha256 `65242554…d049`).
- `ui/tests/e2e/fixtures/capture-fidelity-original.png` (sha256 `180cd88d…93d2`) and `capture-fidelity-annotated.png` (sha256 `3eb0a910…0db8`), written by the tool. In the bake, the plate covers `(20, 42)–(51, 65)` and the ink `(23, 42)–(48, 64)`.
- `tests/unit/test_capture_text_metrics.py` (new, AC-82.2) and `tests/unit/test_capture_bake_fixture.py` (new, AC-82.5).
- `ui/tests/unit/capture-text-metrics.test.ts`: TA-3 (title and line 9 `'hanging'` → `'alphabetic'`), AC-82.1 ×2, AC-82.3.
- `ui/tests/unit/capture-page.behavior.test.ts`: TA-4 (title, `'hanging'` → `'alphabetic'`, and a new `y` = `'38'` assertion; the plate assertions are unchanged) and AC-82.4. AC-82.4 uses a 40×40 catalog shot, so the fit scale is 5 on the 200 px surface. A click outside the plate leaves no handle, and a click at CSS `(85, 160)` inside the plate shows `capture-handle-body`.
- `ui/tests/e2e/capture-inbox.test.ts`: `installFidelitySeam`, `fidelityBoxes`, AC-82.6 (`readFileSync` import added).

Test-setup corrections before the formal Red run, so no test assertion changed:
1. **Inset ring (AC-82.6).** The image box sits at a fractional CSS origin, so Playwright's element screenshot rounds outward to 241×121 and its edge pixels carry the dark surface. On the first dry run the "ink" box covered the whole frame. The scan now skips a `ceil(2·DPR)` px ring. The mark is at least 20 px from every edge.
2. **No custom `expect` messages (AC-82.6).** With a message, Playwright prints `Error: <message>` instead of `Error: expect(`, and `red-check.py` would not attribute the failure. The logged boxes name the side.
3. **S3: `red-check.py` ANSI fix.** The first formal run of row 2 exited 1 with `RED-CHECK: s36-82-red-ui.txt: no failing-run summary`. The Vitest receipt is coloured (`ESC[1mESC[31m6 failed`). The digit follows `m`, so `\b\d+ failed` has no word boundary, and the coloured `AssertionError:` lines miss the `^\s*` anchor. Per S3 ("fix the test setup only, then re-prove Red"), `red-check.py` now strips CSI escapes before matching (`ANSI_ESCAPE`). Two selftest fixtures were added:
   - `vitest-ansi-assertion` (positive). Without the strip it fails both the summary and the assertion regex.
   - `ansi-locator-timeout` (negative, still refused).

   `--selftest` gives 11 fixtures, 0 wrong. No rule was loosened. The row was then re-run and is the receipt above.

## MEU-82 Green (row 3)

Row 3 command (task.md row 3, verbatim) exit **0** on 2026-10-16.

| Receipt | Result |
|---|---|
| `C:/Temp/av-kit/s36-82-green-ui.txt` | `Test Files 4 passed (4)`, `Tests 130 passed (130)` (capture-text-metrics, capture-page.behavior, capture-page, capture-hit-test) |
| `C:/Temp/av-kit/s36-82-green-py.txt` | `26 passed` (test_capture_text_metrics, test_capture_bake_fixture, test_capture_adapter) |
| `C:/Temp/av-kit/s36-82-green-build.txt` | build OK |
| `C:/Temp/av-kit/s36-82-green-e2e.txt` | `29 passed` (the whole `capture-inbox.test.ts`, AC-82.6 included) |

AC-82.6 boxes after the fix (image px, the image box at CSS `(719.5, 456.5)`):

| View | Ink (l, t, r, b) | Plate (l, t, r, b) |
|---|---|---|
| Original + SVG preview | 23, 42, 48, 65 | 20, 42, 50, 66 |
| Annotated (bake) | 23, 42, 48, 65 | 21, 43, 51, 65 |

Ink differs by 0 px on every side (it was 8 px at the top in Red). The plates differ by at most 1 px, and each ink box lies inside its plate expanded by 1 px. S4 was not reached.

Product changes:
- `capture-segoe-metrics.ts`: `SEGOE_UI_UNITS_PER_EM = 2048`, `SEGOE_UI_ASCENDER = 2210` (`SEGOE_UNITS`).
- `capture-text-metrics.ts`:
  - `SVG_DOMINANT_BASELINE = 'alphabetic'`.
  - `segoeAscentPx(size)` implements `SEGOE_ASCENT`. The y scale is written as `size·64·65536 / UNITS_PER_EM`; the plan's literal `2048` is that value, not a second use of `UNITS_PER_EM`.
  - `svgTextBaselineY({y, font_size}) = y + segoeAscentPx(font_size)`.
- `CaptureViewport.tsx`: the `<text>` `y` is `svgTextBaselineY(ann)`. `textBackgroundBox`, the hit test, the body handle and the bake are unchanged.

## MEU-83 Red (row 4)

Row 4 command (task.md row 4, verbatim) exit **0** on 2026-10-16. D-12 stands at `ARROW_HEAD`, so TA-1 and TA-2 apply.

| Receipt | Child exit | Result |
|---|---|---|
| `C:/Temp/av-kit/s36-83-red-py.txt` | 1 | `6 failed, 1 passed, 16 deselected` |
| `C:/Temp/av-kit/s36-83-red-ui.txt` | 1 | `Test Files 2 failed (2)`, `Tests 6 failed \| 86 passed (92)` |
| `C:/Temp/av-kit/s36-83-red-check.txt` | 0 | `red-check: 2 receipt(s), 0 problem(s)` |

Red reasons (diagnostic lines from the receipts):

| Test | Diagnostic |
|---|---|
| AC-59.2 pytest (TA-2) | `assert (88.947…, 4.673…) == approx((86.49…, 6.52…))` (the 4 / 0.40 head) |
| AC-83.2 | `assert (4, 0.4, 10) == (5, 0.45, 10)` |
| AC-83.3 pytest | `AttributeError: module 'avkit_infra.capture.adapter' has no attribute 'arrow_shaft_end'` (declared-new) |
| AC-83.5 | `assert 53 == 0`: 53 leak pixels, as R-3 predicted for the baseline |
| AC-83.6 | `assert (0 / 641) >= 0.4`: blend fraction 0.0 over 641 edge pixels, as in R-3 |
| AC-83.8 | `assert 'Image.Resampling.LANCZOS' in '…'` |
| AC-59.2 Vitest (TA-1) | `expected 88.94726807196538 to be close to 86.49329346470985` |
| AC-83.1 | `expected 4 to be 5` (`ARROWHEAD_LENGTH_FACTOR`) |
| AC-83.3 Vitest | `TypeError: mod.arrowShaftEnd is not a function` (declared-new) |
| AC-83.4 | `0,0 -> 100,0 s3 line x2: expected 12.50670653529015 to be less than or equal to 1e-9`: the baseline `<line>` ends at the tip |
| AC-83.9 | `expected null to be 'none'`: the baseline head `<polygon>` has no `stroke` |
| AC-65.3 (TA-7) | `expected 27.999999999999996 to be close to 35`: the head length is 4 × 7, not 5 × 7 |

**AC-83.7 passes on the baseline code.** The current adapter already clips its drawing at the image edge, and `(111, 60)` is red. The test guards the Green tile code: an unclipped tile must neither raise nor write outside the tile. TA-5 (AC-66.11) also passes, because the `<g>` already carries `x2/y2`.

`ARROW_CASES` (`GEOMETRY_FIXTURE.arrows`, sha256 `2078b80c…2aa0`) was computed by this scratch script from the plan formulas, independent of the product code (which still has the 4 / 0.40 head):

```python
"""Session 36 row 4: compute ARROW_CASES from the plan formulas and pin them in GEOMETRY_FIXTURE.

ARROW_HEAD: factor 5, angle 0.45, min 10. ARROW_SHAFT_OVERLAP_PX = 1. SHAFT_END as in the plan.
Independent of the product code (which still has the baseline 4 / 0.40 head at row 4).
"""

from __future__ import annotations

import json
import math
import pathlib
import sys

FACTOR, ANGLE, MINIMUM, OVERLAP = 5, 0.45, 10, 1
CASES = (((0, 0), (100, 0), 3), ((700, 375), (750, 400), 4), ((50, 10), (50, 90), 1), ((0, 0), (8, 0), 4), ((5, 5), (5, 5), 3))


def case(frm, to, stroke):
    dx, dy = to[0] - frm[0], to[1] - frm[1]
    length = math.hypot(dx, dy)
    if length == 0:
        return {"from": list(frm), "to": list(to), "stroke": stroke, "head": None, "left": None, "right": None, "shaft_end": list(to)}
    theta = math.atan2(dy, dx)
    head = max(MINIMUM, FACTOR * stroke)
    left = [to[0] - head * math.cos(theta - ANGLE), to[1] - head * math.sin(theta - ANGLE)]
    right = [to[0] - head * math.cos(theta + ANGLE), to[1] - head * math.sin(theta + ANGLE)]
    back = head * math.cos(ANGLE) - OVERLAP
    end = None if length <= back else [to[0] - dx / length * back, to[1] - dy / length * back]
    return {"from": list(frm), "to": list(to), "stroke": stroke, "head": head, "left": left, "right": right, "shaft_end": end}


def main(path: str) -> int:
    cases = [case(*c) for c in CASES]
    h = cases[0]
    assert h["head"] == 15, h
    assert h["left"] == [86.49329346470985, 6.524483011668454], h["left"]
    assert h["right"] == [86.49329346470985, -6.524483011668454], h["right"]
    assert h["shaft_end"] == [87.49329346470985, 0], h["shaft_end"]
    assert cases[3]["shaft_end"] is None and cases[4]["head"] is None
    target = pathlib.Path(path)
    with open(target, encoding="utf-8", newline="") as f:
        data = json.loads(f.read())
    data["arrows"] = cases
    seg = json.dumps({"segoe_ascent": data["segoe_ascent"]}, indent=2)[:-2]  # drop "\n}"
    lines = ",\n".join("    " + json.dumps(c) for c in cases)
    text = seg + ',\n  "arrows": [\n' + lines + "\n  ]\n}\n"
    assert json.loads(text) == data
    with open(target, "w", encoding="utf-8", newline="") as f:
        f.write(text.replace("\n", "\r\n"))
    for c in cases:
        print(json.dumps(c))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
```

The script asserts the horizontal case equals the pinned values exactly. The result: horizontal `head 15`, `left (86.49329346470985, 6.524483011668454)`, `right (86.49329346470985, -6.524483011668454)`, `shaft_end (87.49329346470985, 0.0)`; diagonal `head 20`, `shaft_end (734.7867397429735, 392.39336987148675)`; vertical `head 10`, `shaft_end (50.0, 81.99552897647322)`; short `head 20`, `shaft_end null`; zero-length `head/left/right null`, `shaft_end (5, 5)`.

Files written in row 4:
- `ui/tests/e2e/fixtures/capture-geometry.json`: `arrows` added; `segoe_ascent` unchanged.
- `ui/tests/unit/capture-arrow-head.test.ts`:
  - TA-1: in AC-59.2, `4 * 3` → `5 * 3`, `0.4` → `0.45`, `12` → `15`, plus the `ARROW_CASES` horizontal comparison.
  - AC-83.1 and its negative; AC-83.3 with the at-tip negative.
- `ui/tests/unit/capture-page.behavior.test.ts`:
  - TA-5: AC-66.11 reads `x2/y2` from the arrow `<g>`; the values stay `'750'`, `'400'`.
  - TA-7: AC-65.3 asserts that the head `<polygon>` length from the tip to the left vertex is 35 to `1e-9`, instead of the `<line>` `stroke-width`.
  - AC-83.4: all five `ARROW_CASES` are loaded through the detail fetch on an 800×450 shot.
  - AC-83.9.
- `ui/tests/e2e/capture-inbox.test.ts`: TA-6. AC-66.14 reads `x2/y2` from the arrow `<g>`; the values stay `'1260'`, `'830'`. It runs in row 5's E2E.
- `tests/unit/test_capture_adapter.py`:
  - TA-2: in `test_ac_59_2_shared_arrowhead_vertices`, the same value changes plus the `ARROW_CASES` comparison.
  - AC-83.2, AC-83.3, AC-83.5–83.8.
  - The helpers restate `ARROW_HEAD`, `SHAFT_END`, the `BAKE_AA` tile and `AA_LIMITS` from the plan (`PLAN_HEAD`, `_plan_shaft_end`, `_plan_tile`), so the oracles never take their geometry from the adapter under test. The bakes go through `tools/capture_bake_fixture.py` (`write_original`, `bake`), as the plan's Files table says.

Readings of the contract:
1. **Zero-length "no head" (AC-83.1/83.2).** `arrowheadVertices` / `arrowhead_vertices` keep their signatures. The unit tests assert the legacy from→to shaft (`arrowShaftEnd` returns `to`). The missing head is asserted where it is drawn: no `<polygon>` (AC-83.4). The bake already skips the head at zero length (`_apply_arrow`).
2. **AC-83.8 size spy.** It asserts that no created image is at least `SUPERSAMPLE ×` the canvas in both axes. It also asserts that a mask of `SUPERSAMPLE ×` the `BAKE_AA` tile is created (step 2), so the spy cannot pass on a bake that skips supersampling.
3. **AC-83.4 polygon.** The points equal `arrowHeadPoints(...)` and also the fixture vertices to `1e-9`. The second check is what makes the test Red on the baseline, which computes `arrowHeadPoints` with the old head.

Lint, no assertion change: `ruff check` flagged E501 in the row 2 files `test_capture_bake_fixture.py` and `test_capture_text_metrics.py` (the module docstrings and the sizes list). These were wrapped without changing behaviour. The new MEU-83 code was wrapped the same way, and its tile-difference scan was shared as `_changed_outside`.

## MEU-83 Green (row 5)

The row 5 command (task.md row 5, verbatim) exited **0** on its final run on 2026-10-16. It took four runs; see "Runs" below.

| Receipt | Result |
|---|---|
| `C:/Temp/av-kit/s36-83-green-py.txt` | `63 passed, 1 warning` (adapter, bake fixture, `test_api_capture_flatten`, `test_api_captures`) |
| `C:/Temp/av-kit/s36-83-green-ui.txt` | `Test Files 4 passed (4)`, `Tests 132 passed (132)` |
| `C:/Temp/av-kit/s36-83-green-build.txt` | 3 × `built in`, exit 0 |
| `C:/Temp/av-kit/s36-83-green-e2e.txt` | `29 passed`: `capture-inbox.test.ts`, including TA-6 (AC-66.14) and AC-82.6 |

Product changes (`PRODUCT_SCOPE`: arrow drawing only):
- `ui/src/renderer/src/features/capture/capture-arrow-head.ts`:
  - `ARROWHEAD_LENGTH_FACTOR` 4 → 5 and `ARROWHEAD_ANGLE_RAD` 0.4 → 0.45 (`ARROW_HEAD`, D-12). `ARROWHEAD_MIN_PX` stays 10.
  - New `ARROW_SHAFT_OVERLAP_PX = 1`.
  - New `arrowShaftEnd(from, to, strokeWidth)` (`SHAFT_END`): zero length returns `to`, `length <= back` returns `null`, otherwise it returns `to − u·back` with `back = head·cos(angle) − overlap`.
  - `arrowheadVertices` and `arrowHeadPoints` are unchanged apart from the constants.
- `CaptureViewport.tsx` `AnnotationMark`:
  - The `<line>` ends at `arrowShaftEnd(...)` and is not rendered when that is `null`.
  - The head `<polygon>` gets `stroke="none"` (AC-83.9, D-21).
  - The `<g>` keeps `x1/y1/x2/y2 = from/to` and its `stroke`.
- `packages/infrastructure/src/avkit_infra/capture/adapter.py`:
  - The same `ARROW_HEAD` constants, plus `ARROW_SHAFT_OVERLAP_PX = 1`, `SUPERSAMPLE = 4` and `ARROW_TILE_PAD_PX = 4`.
  - New module-level `arrow_shaft_end(from_xy, to_xy, stroke_width)`, the same logic as the TS function.
  - `_apply_arrow` now follows `BAKE_AA`:
    1. The tile is the bbox of from, the shaft end and the head vertices, padded by `stroke/2 + 4`. Bounds are `floor` of the min and `ceil` of the max + 1, end-exclusive, clipped to the image. An empty tile returns unchanged.
    2. An `L` mask is created at `SUPERSAMPLE ×` the tile size.
    3. `draw.line` (width `SUPERSAMPLE·max(1, stroke)`) and `draw.polygon` draw at 255, each point mapped as `SUPERSAMPLE·(p − origin) + 1.5`.
    4. The mask is resized with `Image.Resampling.LANCZOS`.
    5. `Image.composite(solid, tile, coverage)` is pasted back at the tile origin.
  - The shaft end is read from the module global `arrow_shaft_end`, so AC-83.5's negative control (which patches it) reaches the bake.
  - `_apply_text`, `text_plate_box`, `_apply_rect`, `_apply_highlight` and the bake format handling are unchanged.

Runs:
1. **Run 1 exited 1.** Pytest, Vitest and the build passed, but the E2E reported `2 failed, 27 passed`:
   - AC-60.12 (`arrow.to` still `[6, 6]` after the `to` handle drag).
   - AC-67.35 (`capture-apply-image-reason` not found).

   The receipt is kept at `C:/Temp/av-kit/s36-83-green-e2e-attempt1.txt`. Neither test reads the rendered shaft:
   - The SVG overlay is `pointer-events-none`.
   - Handle and mark hits are geometric (`capture-hit-test.ts`, from/to distances).
   - AC-67.35 concerns the Apply reason tooltip.

   Run alone, both passed 3/3. `--repeat-each 20` on both gave `40 passed` (`C:/Temp/av-kit/s36-83-green-e2e-repeat20.txt`).
2. **Run 2 exited 0** (`29 passed`).
3. **Run 3 was not a valid exit check.** After run 2, `ruff format --check` wanted to rejoin the new `arrowhead_vertices(...)` call in `_apply_arrow`, so I joined it (layout only), then reran row 5. That rerun's exit was hidden by a pipe.
4. **Run 4 is the receipt above** (exit 0).

`ruff format --check adapter.py` still reports one hunk, the `ValidationError` call at line 156. That code predates this session: `git show HEAD:…/adapter.py` reports the same hunk, so it stays untouched under `PRODUCT_SCOPE`. `ruff check` and `eslint` on the changed files are clean.

S6 (plan `:411`) covers a flake under `--repeat-each`, and the stress run above had none. Run 1 is recorded here so H1 can watch for a repeat: the full Electron suite runs again in row 8 (`ui-electron`).

No test assertion changed in row 5. `GEOMETRY_FIXTURE` sha256 is still `2078b80c…`.

## MEU-84 Red (row 6)

The row 6 command (task.md row 6, verbatim) ran on 2026-10-16. Each test receipt's `.exit` is `1`, the build exited 0, and `red-check: 3 receipt(s), 0 problem(s)`.

| Receipt | Result | Diagnostic |
|---|---|---|
| `C:/Temp/av-kit/s36-84-red-py.txt` | `4 failed, 2 passed, 50 deselected` | `E AssertionError` on the stale `annotated_path` / `sidecar_path` (AC-84.1 a, b, c; AC-84.2) |
| `C:/Temp/av-kit/s36-84-red-ui.txt` | `Test Files 3 failed (3)`, `Tests 4 failed \| 102 skipped` | see below |
| `C:/Temp/av-kit/s36-84-red-e2e.txt` | `1 failed` (AC-84.5) | `Error: expect(received).toEqual(expected)`: `Expected: []`, `Received: null` (`__AVKIT_E2E_SHELL_LOG__` is not defined) |

Tests written:
- **AC-84.1** (`tests/unit/test_capture_service.py`). Each case uses `_marked_shot` with a one-second ticking clock.
  - (a) The annotated copy is deleted: `annotated_path` becomes `None`, the sidecar stays, and `updated_at` advances.
  - (b) The sidecar is deleted: the reverse of (a).
  - (c) Both are deleted: both become `None`.
  - (d) A complete row is not saved: a spy on `capture_shots.save` records nothing and the row equals the one before the scan. This is the negative guard, so it **passes on baseline**, as intended.
  - (e) **Characterisation.** A row whose original is gone is still deleted. This pins existing `scan_inbox` behaviour, so it **passes on baseline** and must keep passing after RECONCILE.
- **AC-84.2** (`tests/e2e/test_api_captures.py`): the real API with a 32×32 PNG.
  1. Annotate a rect.
  2. Delete the annotated file.
  3. The list then shows `annotated_path: null` with the sidecar kept.
  4. Detail still returns the `rect`, and `image?variant=annotated` returns 404.
- **AC-84.3** (new `ui/tests/unit/capture-viewed-file.test.ts`): `viewedFilePath`.
  - The annotated variant gives the annotated path, and the original variant gives the original.
  - A `null` or `''` annotated path falls back to the original, and no shot gives `null`.
  - Red: `Failed to load url ../../src/renderer/src/features/capture/capture-viewed-file`. The line names the declared-new `capture-viewed-file`.
- **AC-84.4** (`capture-page.behavior.test.ts`): the page's Open file and Open folder buttons, plus the palette `open_folder` (hash `#/capture`, `requestAnimationFrame` stubbed to run at once).
  1. Original view: both name the original.
  2. Annotated view: all three name the annotated copy.
  3. The list refetches with `annotated_path: null`: all three fall back to the original.

  Red: `AssertionError: expected last "spy" call to have been called with [ 'C:/shots/a.annotated.png' ]`, received `C:/shots/a.png`.
- **AC-84.5** (`ui/tests/e2e/capture-inbox.test.ts`): a seam shot with `annotated_path`.
  - The log is `[]` right after the shot opens.
  - View Annotated, then Open file and Open folder, each polled to the next length: the last two entries are `openPath` and `showItemInFolder` of the annotated path.
  - View Original, then repeat: entries 3 and 4 name the original.

  The first assertion gives an immediate Red, not a timeout.
- **AC-84.6** (`capture-main.behavior.test.ts`). Its three cases:
  1. `recordE2eShell` appends in order.
  2. The global is undefined with `AVKIT_E2E` unset and equals `e2eShellLog` when it is `1` (`vi.resetModules` between imports).
  3. A source check of each `index.ts` handler's `AVKIT_E2E === '1'` branch: it must contain `recordE2eShell('<op>', target)` and `return`, contain no `shell.`, and the real `shell.<op>(target)` must stay after it.

  Red: cases 1 and 2 fail with `Cannot find module '../../src/main/e2e-shell'`, which names the declared-new `e2e-shell`. Case 3 fails with `AssertionError: openPath: expected '\r\n        return\r' to contain 'recordE2eShell('openPath', target)'`.

No product code changed in row 6.

## MEU-84 Green (row 7)

The row 7 command (task.md row 7, verbatim) exited **0** on its first run on 2026-10-16.

| Receipt | Result |
|---|---|
| `C:/Temp/av-kit/s36-84-green-py.txt` | `56 passed, 1 warning` (`test_capture_service.py`, `test_api_captures.py`, all cases) |
| `C:/Temp/av-kit/s36-84-green-ui.txt` | `Test Files 5 passed (5)`, `Tests 146 passed (146)` |
| `C:/Temp/av-kit/s36-84-green-build.txt` | exit 0 |
| `C:/Temp/av-kit/s36-84-green-e2e.txt` | `30 passed`: all of `capture-inbox.test.ts`, including AC-84.5 |
| `C:/Temp/av-kit/s36-84-green-e2e-repeat10.txt` | extra S6 check: `--grep "AC-84.5" --repeat-each 10` → `10 passed` |

Product changes:
- `packages/core/src/avkit_core/services/capture.py` `scan_inbox` (`RECONCILE`, D-15). In the final loop, still under `CAPTURE_FILE_LOCK` and the same unit of work:
  - A row whose original is gone is still deleted, then the loop moves on (`continue`).
  - Otherwise `annotated_path` and `sidecar_path` are each set to `None` when set but not `is_file()`, independently.
  - The row is saved (`replace(..., updated_at=self._now())`) only when one of them changed.
- New `ui/src/renderer/src/features/capture/capture-viewed-file.ts`: `viewedFilePath(variant, shot)` (`VIEWED_FILE`, D-16).
- `capture-commands.ts`: the selection's `originalPath` becomes `viewedPath`. `openCaptureFile` opens it, `openCaptureFolder` reveals it (falling back to `inboxDir` only with no selection), and the palette `open_folder` reaches the same function.
- `CapturePage.tsx`: the selection effect passes `viewedPath: viewedFilePath(viewVariant, selected)`. Its dependencies are now `[annotations, selected, selectedId, viewVariant]`, so a refetch that drops `annotated_path` updates the target.
- New `ui/src/main/e2e-shell.ts` (`E2E_SHELL_LOG`, D-17):
  - It exports `e2eShellLog` and `recordE2eShell(op, target)`.
  - It assigns `globalThis.__AVKIT_E2E_SHELL_LOG__` at module load only when `AVKIT_E2E === '1'`.
- `ui/src/main/index.ts`: the `openPath` and `showItemInFolder` E2E branches call `recordE2eShell(...)` and return. The real `shell.*` calls after them are unchanged.

Checks:
- `npx tsc --noEmit` (ui) exits 0.
- `eslint` on the changed source and test files and `ruff check` on the changed Python files are clean.
- `ruff format --check` lists hunks in `capture.py` (lines 423, 445, 448, 865, 901) and `test_capture_service.py` (278, 284, 457, 587). All of them are in code that predates this session: `git show HEAD:…/capture.py` fails the same check. None touches the lines rows 6 and 7 added, so they stay untouched under `PRODUCT_SCOPE`.

No test assertion changed in row 7.

## Gate (row 8)

The row 8 command (task.md row 8, verbatim, with `RECEIPTS_DIR=C:/Temp/av-kit` as in planning) exited **0** on attempt 5, 2026-10-16. `session-gate: all steps exit 0`.

### Decisive lines (attempt 5)

| Step | Stage | Exit | Decisive line |
|---|---|---|---|
| identity-before | identity | 0 | `tested_state 534beb1…+53752bff…15d4` |
| py-types, py-lint, py-lint-tools, ui-types, ui-lint | static | 0 | — |
| task-contract | static | 0 | — |
| scope-ast | static | 0 | `frozen adapter functions changed: []` |
| scope-paths | static | 0 | `changed paths: 33 outside scope: []` |
| py-tests | full | 1 → 0 | `2 failed, 674 passed, 1 warning`; `py-tests baseline rule: failed=2 outside_baseline=[] errors=0` |
| ui-tests | full | 0 | `Test Files 85 passed (85)`, `Tests 815 passed (815)` |
| ui-build | full | 0 | — |
| ui-harness-build | full | 0 | — |
| ui-picker-stub | full | 0 | — |
| openapi | full | 0 | — |
| state-render | full | 0 | — |
| ui-electron | runtime | 0 | `139 passed (2.8m)` |
| e2e-repeat | runtime | 0 | `20 passed (34.3s)` (AC-82.6 and AC-84.5, `--repeat-each=10`; no flake, S6 clear) |
| identity-npm | identity | 0 | `@playwright/test@1.62.1`, `electron@42.9.3` |
| identity-after | identity | 0 | `tested_state before == after` |

The two `py-tests` failures are exactly the §Baseline failed set and are not regressions:
- `tests/unit/test_packaging_backend.py::test_pack_dist_onedir_layout[AC-24.10]`
- `tests/unit/test_packaging_installer.py::test_nsis_pack_check_script[AC-25.10]`

### Input identity (attempt 5, `s36-D6-identity-after.txt`)

```text
python 3.12.12
node v24.19.0
electron 42.9.3
playwright_test 1.62.1
segoeui_sha256 704eada12961a27fd271f7d3b09e2066520e758390c1776744eff430fee30f6e
ELECTRON_RUN_AS_NODE <unset>
uv_lock_sha256 b4aeccb195d4d0b9db101d73a0241165b26eb4a0998a574812e8d8fdef584352
ui_package_lock_sha256 a86d9a42c6cbd98705e1720edbd7666fed573581c07e21ea0f56379dc7332980
tested_state 534beb174e2be1a97fc0cd248f53b4b8cdc83e49+53752bff3673103ed7b022f1acc53376c3170362093ec3896b34747ff49615d4
```

### Attempts

| # | Result | Cause | Fix | Receipts |
|---|---|---|---|---|
| 1 | `task-contract` exit 3 | `RECEIPTS_DIR is unset` | Run with `RECEIPTS_DIR=C:/Temp/av-kit`, the repo convention planning used | `C:/Temp/av-kit/s36-gate-attempt1/` |
| 2 | `task-contract` exit 1 | Status cells carried notes after `` `[x]` `` | Status cells reduced to the bare legend token; evidence stays in this file | `C:/Temp/av-kit/s36-gate-attempt2/` |
| 3 | `py-tests` exit 1 | `-x` stopped at `AC-24.10`, a §Baseline failure (`1 failed, 598 passed`) | **Gate change G-1** (below) | `C:/Temp/av-kit/s36-gate-attempt3/` |
| 4 | `ui-electron` exit 1 | `5 failed, 134 passed`: four `capture-picker.test.ts` tests (`the deterministic sidecar stub is missing: run "npm --prefix ui run build:picker-stub"`) and AC-51.7 `layout-primitives.test.ts` (`fresh isolated main build`) | **Gate change G-2** (below) | `C:/Temp/av-kit/s36-gate-attempt4/` |
| 5 | exit 0 | — | — | `C:/Temp/av-kit/s36-gate.txt`, `s36-D6-*.txt` |

### Gate changes after plan approval (flagged for the execution review)

Both change only the plan-local `session-gate.ps1`. Neither changes a test, an assertion or product code, and both are named in the H1-7 review prompt.

- **G-1: `py-tests` applies the plan's baseline rule.**
  - The approved script ran `pytest tests/ -x`. It could never pass in this worktree, because the two §Baseline tests need the gitignored PyInstaller tree (`packaging/dist/avkit-backend`, 341 MB) and the fetched ffmpeg binaries.
  - That contradicts the plan's own rule (implementation-plan.md §Baseline): "A test failing at baseline is never counted as a regression, and a test passing at baseline that fails later is."
  - The step now runs without `-x` and with `-rfE`. Pytest exit 1 passes only when there is at least one `FAILED` id, every one is in `$baselinePyFailed` (the two ids above), and no line starts with `ERROR `. Any other failure, any error, or any other exit code fails the step.
  - Session 31 (`2026-10-10-gui-polish-residuals`) used the same subset rule (`pytest_env_ok`).
  - Rejected alternatives: building the pack tree and fetching ffmpeg is out of scope. Copying the main checkout's stale build would make the test pass without proving anything.
- **G-2: the Electron suite's gitignored prerequisites become stages before `ui-electron`.**
  - `ui-harness-build`: `AVKIT_PRIMITIVE_HARNESS_BUILD=1 npm --prefix ui run build -- --outDir <root>/ui/out-e2e`, the same argv as Session 31's `validate-task.ps1` stage.
  - `ui-picker-stub`: `npm --prefix ui run build:picker-stub`, the command the failing test's own error names.
  - Session 31's gate ran in the main checkout, where the stub was already published. `.agent/docs/cloud-local-collaboration.md` §3.1 item 3 requires every build artifact the E2E suite needs to be a stage.
  - Both write only gitignored paths (`ui/out-e2e/`, `native/**/publish/`), which `identity.py` does not hash.
  - Before attempt 5, the five failed tests passed alone after these builds: `5 passed (11.3s)` (`C:/Temp/av-kit/s36-prereq-e2e.txt`).

## Hub (row 9)

The row 9 command (task.md row 9, verbatim) exited **0** on 2026-10-16: the hub `rg` found every edit (`C:/Temp/av-kit/s36-hub-rg.txt`), and `render --check` printed `Drift check passed — SSOT loaded (91 MEUs, 12 phases), rendered regions match on-disk content` (`C:/Temp/av-kit/s36-state-render.txt`).

Edits (all CRLF, as before):
- `docs/build-plan/09-screenshot-capture.md`:
  - **`:366` Arrow row:** the head is now `max(10, 5 * stroke_width)` at `0.45` rad, with no outline. The shaft ends at the back of the head plus `ARROW_SHAFT_OVERLAP_PX = 1`; an arrow shorter than that draws only the head. The bake draws at 4× on its own tile and downscales with LANCZOS. Cites Session 36 plan D-12, D-13, D-14.
  - **`:367` Text row:** `dominant-baseline="alphabetic"` at `y + ascent` (the Segoe `la` ascent). Cites D-11.
  - **`:723` Head row:** the chosen head values. Cites D-12.
- `docs/build-plan/build-priority-matrix.md`: rows 9.15 MEU-82, 9.16 MEU-83 and 9.17 MEU-84 after 9.12, in the 9.12 row format. The 09 anchors and dependencies match the 09 MEU table (`:861-863`).
- `.agent/context/meu-status.yaml` Phase 9:
  - `last_updated: '2026-10-16'`.
  - The note gains "MEU-82–84 bound to capture-render-fidelity."
  - `tools/meu_status.py render` regenerated the `docs/BUILD_PLAN.md` Phase 9 line (`:53`) inside AUTOGEN. Render writes LF, so the file was restored to its CRLF working copy before `render --check`. The index is LF either way (`text=auto`), and the diff stays one line.
- `docs/build-plan/gui-actions-index.md:71-72` needs **no change**. `capture:open_file` → IPC `openPath` and `capture:open_folder` → IPC `showItemInFolder` keep their ids and IPC. Only the path they receive follows `VIEWED_FILE`. `gui-actions-audit.test.ts`: `Test Files 1 passed (1)`, `Tests 4 passed (4)` (`C:/Temp/av-kit/s36-gui-actions-audit.txt`).

Every file row 9 changes is in `identity.py`'s `PROJECT_ARTIFACTS` (`docs/build-plan`, `docs/BUILD_PLAN.md`, `.agent/context`), so the row 8 `tested_state` still holds. H1-6b re-derives it.

Checked after row 9: `identity.py --state-only` with `ELECTRON_RUN_AS_NODE` cleared (as the gate runs) re-derives `534beb1…+53752bff…15d4`, the attempt 5 value. In a shell that still has `ELECTRON_RUN_AS_NODE=1` it gives `…+e6d0168b…`, because that value is a bound runtime input. H1-6b must run with it cleared.

## Closeout H1 (H1-1 to H1-6b)

All on 2026-10-16, from the worktree, with each task.md command run verbatim:
- **H1-1:** exit **0**. No numeric row is still `[ ]` (`C:/Temp/av-kit/task-unchecked.txt`).
- **H1-2:** the gate re-run exited **0** (`C:/Temp/av-kit/s36-gate-h1.txt`, `session-gate: all steps exit 0`).
  - Static stages all exit 0. `scope-ast`: `frozen adapter functions changed: []`. `scope-paths`: `changed paths: 37 outside scope: []`. The rise from 33 at row 8 is the row 9 hub edits, which are all inside scope.
  - `py-tests`: `2 failed, 674 passed, 1 warning`, then `py-tests baseline rule: failed=2 outside_baseline=[] errors=0` → exit 0 (G-1).
  - `ui-tests`: `Test Files 85 passed (85)`, `Tests 815 passed (815)`. `ui-build`, `ui-harness-build`, `ui-picker-stub` (G-2), `openapi` and `state-render` all exit 0.
  - `ui-electron`: `139 passed (2.5m)`. `e2e-repeat`: `20 passed (37.7s)`.
  - `identity-npm`: `@playwright/test@1.62.1`, `electron@42.9.3`. `tested_state` before == after == row 8's (`534beb1…+53752bff…15d4`).
- **H1-3:** `tools/meu_status.py update` set MEU-82/83/84 to `ready_for_review` with `execution_plan: docs/execution/plans/2026-10-14-capture-render-fidelity`. `render` regenerated `docs/BUILD_PLAN.md` and `.agent/context/meu-registry.md` (`69 + 3🟡 + 1🚫`). Both tools write LF, so the three files were restored to CRLF; the content is unchanged. `current-focus.md` now names Session 36 as the current priority. `render --check`: `Drift check passed — SSOT loaded (91 MEUs, 12 phases)`, exit **0** (`C:/Temp/av-kit/drift-check.txt`).
- **H1-4:** exit **0**. There is no diff under `packages/api` or `openapi.committed.json` against `baseline.sha`, and the H1-2 `openapi` receipt exited 0 (`C:/Temp/av-kit/openapi-check.txt`).
- **H1-5:** read `.agent/context/handoffs/TEMPLATE.md` and the MEU-67 exemplar. The handoffs follow its sections and its `Codex Validation Report` placeholder.
- **H1-6:** the three handoffs `.agent/context/handoffs/2026-10-14-capture-render-fidelity-MEU-{82,83,84}-handoff.md` were written (CRLF). The validator reported `OK` for each: 9, 16 and 9 AC rows; 5, 5 and 2 decisions logged; `all 9 plan AC(s) present`; no `[B]` rows. Exit **0**.
  - Each handoff carries its own Red and Green `evidence.v1` records plus the two shared full gate records (`s36-gate-row8`, `s36-gate-h1-2`).
  - Execution decisions: MEU-82 has D-22 to D-26, where D-25 is G-1 and D-26 is G-2. MEU-83 has D-20, D-21 and D-27 to D-29. MEU-84 has D-30 and D-31.
  - D-12 is recorded as the plan default (`ARROW_HEAD` 5 / 0.45), because the execution message was silent on it. The reflection resolves the plan's pending `human_message_reference`.
- **H1-6a:** `OK: all 9 plan AC(s) present in the handoff` ×3, exit **0**.
- **H1-6b:** `identity.py --state-only` re-derived the state with `ELECTRON_RUN_AS_NODE` cleared. `durable_evidence.py --require-full --expected-state` returned `OK: durable evidence records` ×3, exit **0**. The handoffs and hub edits are project artifacts, so the gate's `tested_state` still holds.

## Closeout H1-7 (execution review) and H2-1

- **H1-7:** the ledger loop `s36-execution-2026-10-14-capture-render-fidelity` was opened with `review_ledger.py begin --review-mode execution`. The prompt `C:/Temp/av-kit/dispatch/s36-exec-prompt.txt` covers the three handoffs, the plan, E1–E5, and gate changes G-1/G-2.
  - The first dispatch stopped before reaching Codex with `registry_not_found: no ModelRegistry.psm1 at any S2 location`. The ledger recorded nothing. The row command was re-run unchanged with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`, which is the same registry location the plan rounds used.
  - Round 1 (Codex CLI `gpt-6.1-sol`, high): **approved**, 0 findings, 0 blocking, `intent_achieved: yes`. G-1 and G-2 were accepted on substance. The reviewer ran its own probes: a Segoe ascent sweep with no mismatches, a positive AA-oracle blend, the red-check and identity selftests, and an identity state match.
  - `review_ledger.py record`: `recorded round 1 verdict=approved … blocking=0 intent_achieved=yes usage=9,183,735; loop may close`.
  - The canonical copy is `.agent/context/handoffs/2026-10-14-capture-render-fidelity-implementation-critical-review.md` (CRLF).
- **H1-7a:** `OK: review_mode=execution; round 1 of 6; verdict=approved; open findings=0` (`C:/Temp/av-kit/review-state.json`).
- **H1-7b:** `OK: approved at round 1 of 6, 0 open blocking findings`.
- **H2-1:** read `docs/execution/reflections/TEMPLATE.md`, `.agent/schemas/reflection.v1.yaml` and the peer `2026-10-02-capture-flatten-backup-reflection.md`.

## Closeout H2-2 (reflection, issues, SSOT)

- **Reflection:** `docs/execution/reflections/2026-10-14-capture-render-fidelity-reflection.md` (CRLF). It records review churn of plan 3 rounds and execution 1 round, and has three sourced design rules. Its Decisions Log carries:
  - grouping D-1 to D-7;
  - triage D-52 to D-55 and D-65;
  - plan D-8 to D-21;
  - handoff D-22 to D-31.

  D-12 is resolved as the plan default: `ARROW_HEAD`, because the execution message was silent on it.
- **Known issues:** `CAPTURE-TEXT-BG-PREVIEW-OFFSET`, `CAPTURE-BAKE-ARROW-THIN`, `CAPTURE-STALE-ANNOTATED-PATH` and `CAPTURE-OPEN-FILE-VARIANT` are `resolved`. Each has `evidence_file` set to its MEU handoff, `last_checked: '2026-10-16'`, and a method and result. `issue_triage.py render` regenerated `known-issues.md`: Active 34 → 30, Resolved 15 → 19.
- **SSOT:** `tools/meu_status.py update MEU-82/83/84 approved`, then `render`. `meu_status.py` and `issue_triage.py render` write LF, so `meu-status.yaml`, `meu-registry.md`, `docs/BUILD_PLAN.md` and `known-issues.md` were restored to CRLF; the content is unchanged. `current-focus.md` now says Session 36 is `approved`.
- **The row command took four runs.** Each refusal needed a format-only edit, with no change of meaning:
  1. `implementation-plan.md decision_log item 12 still carries a template placeholder`. The plan's D-19, D-20 and D-21 YAML used literal SVG tag names, which match `PLACEHOLDER`'s `<[a-z-]+>`. Seven strings were reworded, for example from the bracketed `line` tag to "SVG line element". No decision, AC or contract changed. The review state is bound to the review file's digest, not the plan.
  2. `issue CAPTURE-OPEN-FILE-VARIANT decision_log item 1 is not valid YAML`. The triage-time D-65 entry used an indentless `precedents:` sequence and a single-quoted `reasoning` that wrapped onto a second line, both outside the validator's bounded grammar. Its `chosen` also spelt the stem in braces, which `PLACEHOLDER` refuses. The edit indents the sequence, joins the scalar and writes the stem as `[stem]`. A `yaml.safe_load` comparison proved every other issue identical, and D-65 different only in that spelling.
  3. `Decisions Log is missing decision D-2`. The check reconciles every grouping §8 row, not only the four the plan names, so D-2, D-5 and D-7 were added.
  4. Exit **0**: `OK: all 15 template section(s) present; all 7 required schema field(s) emitted; 3 design rule(s), all sourced; 32 recorded decision(s) reconciled against 36 Decisions Log row(s)`, `OK: known-issues.md is up-to-date`, and `Drift check passed`.
- **Limit of the check:** `--decision-issue` is a single-value option, so of the four flags the row passes only the last, `CAPTURE-OPEN-FILE-VARIANT`, is reconciled. The other three issues' decisions (D-52 to D-55) were carried into the reflection by hand.

## Closeout H2-3 (metrics)

`docs/execution/metrics.md` gained the `2026-10-16 | 2026-10-14-capture-render-fidelity` row (CRLF). The `row-H2-3` check (the file contains `capture-render-fidelity`) exited 0.

## Closeout H2-4 (task contract lint)

`lint_task_contract.py` exited 0: `OK: 26 row(s); 10-column table (with builder_model); 24 row(s) fully checked: backticked, exit-code re-raised, receipt under RECEIPTS_DIR; dependencies resolve and are acyclic; 2 row(s) exempt (view_file): H1-5, H2-1`.

## Closeout H2-5 (commit message draft)

The row exited 0 and wrote `C:/Temp/av-kit/commit-draft.txt`. **Defect in the row:** the command's `\\n` inside `python -c` is an escaped backslash in Python source, so the file holds one line with literal `\n` separators instead of three lines. The three subjects are right; the row command was left verbatim. Nothing was committed, and committing waits for Mat.
