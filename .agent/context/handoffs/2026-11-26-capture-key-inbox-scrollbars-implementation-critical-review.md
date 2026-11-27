---
date: "2026-11-27"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "cki-execution-2026-11-26-capture-key-inbox-scrollbars"
round: 1
---

# Critical Review: capture-key-inbox-scrollbars

> **Review Mode**: execution
> **Verdict**: approved

## Scope

**Intent anchor:** "after this session the Capture page does three things it does not do today." The implementation must name the saved capture key, keep the catalog and selection within the saved inbox, and provide draggable viewport scroll bars while preserving existing gestures.

Independent read-only review by Codex of Claude Code/Anthropic's Session 103 implementation, MEU-165, MEU-166 and MEU-167. Scope is the delta from baseline `e5028a3ad45fa033c388dea46658ff282fbd7364` in the plan's Files Modified paths, against the 26 dotted ACs. The three handoffs, approved plan corrections, relevant 09 homes, product/test diffs and supporting receipts were consulted. Other sessions' files and process-paperwork quality are outside this verdict.

**tested_state:** `e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78`.

The reviewer obtained this value twice with `identity.py --state-only`, with ELECTRON_RUN_AS_NODE unset. It exactly equals gate run 2 and H1-6b. There is no differing value to attribute to the sandbox's global-ignore permissions. No secret file or global-ignore file was opened.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

## Q1 — Goal

**Achieved.** All three observable outcomes have implementation, assertion Red, passing targeted evidence and passing real Electron evidence.

| Outcome | Criteria and implementation | Decisive evidence |
|---|---|---|
| Saved key, without restart; original default readings | AC-165.1–AC-165.10; `capture-key.ts:12`, `useCaptureSettings.ts:150`, `CapturePage.tsx:945`, help readers and HelpCard | Row 7: 13 passing tests; Electron AC-165.10 expected in Green. Red expected F9 and received F2. Green logged main reporting F9 registered and checked its cap. |
| Current inbox only; other rows preserved; immediate refresh and cleared selection | AC-166.1–AC-166.8; `capture.py:651`, `:755`, `:760`, `useCaptureSettings.ts:142`, `CapturePage.tsx:688` | Reviewer: 109 Python tests passed, including real API isolation and unknown-id 404 equivalence. Row 5: 6 passing UI tests. Electron AC-166.7 expected in Green; Red expected one B item and received three mixed items. |
| Scroll position and thumb drag, existing gestures preserved | AC-167.1–AC-167.8; `capture-scroll-bars.ts:21`, `CaptureViewport.tsx:597`, `:977` | Row 9: 13 passing tests. Both Electron scrollbar tests expected in Green; Red failed on absent bars/thumb. Existing gesture tests remain unchanged and passed in the complete Electron run. |

Accepted the approved scope boundaries and decisions as supplied. This approves the delivered behavior; H2 and any commit remain the coordinator's subsequent work.

## Q2 — Capture key

**Pass.** CAPTURE_KEY_TOKEN resolves all eight specified texts through one formatter. The three allowed renderer F2 holders remain the formatter default, settings defaults and shortcut registry. The default constants preserve the original text, topic ids/order and quick-start hash inputs. The raw-JSON E2E and help-shot readers now resolve the same default reading.

CAPTURE_KEY_SAVED reads the saved baseline, including the Settings help; draft changes do not drive the text, banner or cap. CAPTURE_KEY_FOLLOW performs an initial read and at most ten additional reads at 500 ms while the accelerator differs, stops on a match, and cancels timers/late callbacks on cleanup. CAPTURE_KEY_UNCONFIRMED handles exhausted following and rejected reads without claiming registration. The tests assert both notice text and absent cap, not merely read counts.

AC-165.3, AC-162 pins and the default hashes remain passing. Direct diffs and the independently rerun guards confirm that D-1422's four source-scan replacements are the only changed existing unit expectations. The two approved raw-reader adaptations preserve their expected rendered/default values. I found no remaining in-scope literal text or unsupported registration claim.

## Q3 — Inbox service

**Pass.** INBOX_SCOPE is direct Path-parent equality and makes no filesystem call. INBOX_SCOPE_SCAN checks a resolved child's parent before adapter probing or upserting, and skips out-of-scope rows before filesystem reconciliation, pruning, recovery or rebaking. Returning to a folder resumes the existing treatment of its rows.

INBOX_SCOPE_BY_ID uses `_scoped_shot` at each of the six former direct public entry lookups. The remaining public methods delegate through `get_shot`; the twelve-method census matches the class. The parameterized real-store tests verify identical unknown-id errors and unchanged files/rows for every method. The separate linked-file test verifies no probe of B through A and no B-row modification.

The reviewer reran the new service/API tests plus the four specified regression files: **109 passed in 52.60s**, exit 0. The API test uses the real wiring and asserts response key sets, equivalent unknown/outside 404 bodies for read and write, unchanged A files, and successful access after returning to A. The guards bind unchanged routes and OpenAPI bytes; the independent OpenAPI check also exited 0. No transport or reply-shape change is claimed.

## Q4 — Inbox page and asynchronous results

**Pass.** INBOX_SAVE_REFRESH invalidates the catalog only when the changed leaves contain `inbox_dir`, after the settings refetch. INBOX_SELECTION_LEFT tracks the inbox associated with the selection and clears a departed shot with the delete path's resets. A late old-folder detail 404 clears silently and holds the automatic newest-shot pick until the next list answer.

INBOX_RESULT_BOUND compares live inbox refs with the operation's starting inbox before crop selection, range anchoring and notice; the flatten PNG-copy continuation has the corresponding check. An unseen crop result is retained within its original inbox, without making it permanently exempt after a switch.

The held-response UI test checks both B-list-before-old-crop and old-detail-404-before-B-list orders, including selected name, old-id detail requests, notices and error events. Its same-inbox guards preserve existing crop behavior. The flatten-copy guard was also inspected in source; the held-response test specifically exercises crop and detail rather than every flatten interleaving.

D-1436's preserved/current harness diff changes request counting to begin at the PUT, releases the list hold, and reinstates it for the second save. Expected product outcomes are unchanged. The replacement row 4 Red passes its Red validator; row 5 then passes, and current Red hashes match. D-1437's initial/current key-behavior diff adds only localStorage cleanup. Neither departure hides a changed product expectation.

## Q5 — Scroll bars

**Pass.** SCROLL_BAR_GEOMETRY implements the specified visible share, minimum 24 px thumb, track cap, clamped position/value and inverse drag ratio. Equal content/frame lengths and Fit hide the bar; both overflowing axes shorten each track by 10 px. A thumb filling its track returns zero movement rather than dividing by zero. The table-driven tests cover endpoints, midpoint, one/two axes, minimum thumb and clamped overshoot.

SCROLL_BAR_OVERLAY keeps the existing frame and coordinate map. SCROLL_BAR_DRAG captures the pointer, stops pointer/mouse propagation, and pans through the existing clamp. The rendered test checks movement, unchanged other axis/scale, no annotation, no undo entry and no color change. The Electron test additionally checks real thumb dimensions, a 40 px drag, overshoot to value 100 and Fit removal.

SCROLL_BAR_LOOK uses theme tokens, no geometry transition, scrollbar role/orientation/range/current value, surface controls and accessible names, without a tab stop. Green Electron stdout records fill/edge contrast **10.73 dark** and **7.02 light**, with opaque colors. This proves the specified theme-pair oracle; it is not a claim of contrast against every possible image.

Both `capture-fit-map.ts` and `capture-zoom.ts` are unchanged. Existing wheel, Space+drag and middle-button tests are preserved and included in the 260-test Electron Green run. The four new Red failures are assertion failures on the intended product behavior, not launch or whole-test timeouts.

## Q6 — D-1438, gate and pins

**Accepted on its merits.** Run 1 has nine identical 5000 ms whole-test timeouts across six unchanged main-process test files. Their imports concern main-process modules, their helpers and Node; the session changes renderer/service code. The isolated six-file diagnostic reports **99 passed in 551 ms**. This satisfies S5's requirement to rerun the failing existing tests alone once.

The retained run 1 is a failure, not a pass. The subsequent complete unchanged gate is separate evidence: **1716 Vitest tests passed**, **3379 pytest tests passed**, build passed, and **all 28 steps exited 0**, with equal identities before and after. The gate source has no deselection or per-test timeout relaxation. The load explanation is a supported inference from the observed pattern, isolation and unchanged successful rerun; I did not retrospectively measure the other repository's workers. Nothing indicates a hidden defect in this session's code.

Gate run 2 covers the plan's registered static, targeted and full stages. D-1430's Electron reuse is sound: the saved remote-fresh receipt establishes both subtrees equal to row 10, current input identity still equals that gate, and an independent read-only Git blob comparison matches **all 24 snapshot paths**. I did not execute remote-fresh itself because its implementation can write Git objects or dispatch a fresh run.

The independently rerun guards report **18 pinned files unchanged**, exactly the named expectation replacements, E2E additions preserving prior lines, and five test-id lines added. The test-id diff is precisely one new block at the end; no previous byte changes.

## Q7 — Safety, scope and evidence fidelity

**Pass within the observed scope.** The fresh line-ending check reports 42 scope paths and zero problems, including the disclosed CRLF document handling. Fresh guards/scope checks bind 122 read-only paths and report no out-of-scope session change. Other sessions' declared state was left alone.

HEAD remains the baseline; worktree inspection shows one worktree on main, the index is empty, and the HEAD reflog has no later commit/movement. The plan's detached Electron snapshot objects are expected test inputs; no Session 103 commit on main or push is represented. No evidence of stashing or reverting other work was found; inspection cannot reconstruct every historical filesystem operation.

A read-only scan found no home-folder path or non-noreply/non-example email match in scoped additions/new files or the session's top-level cki text receipts. Fixture names in tests are synthetic. I did not inspect real settings, inbox/Pictures contents, databases, models, browser profiles or secret files, and cannot identify real inbox names by consulting those private sources.

Handoff counts and outcomes match the examined receipts and current input identity. No network, installation, build, Electron launch or repository write was performed by this reviewer. The first reviewer uv invocation stopped on its inaccessible default cache (exit 2); setting an offline scratch cache resolved the tooling access issue without changing project inputs.

## Checklist Results

| Check | Result | Observation / decisive evidence |
|---|---|---|
| IR-1 runtime/integration | pass | Real-stack API test rerun; four new Electron tests inspected in both raw reports; Green 260 expected, zero unexpected/flaky/skipped. |
| IR-2 product stubs | n/a | No delivered product stub; mocked UI collaborators have held-response assertions and same-inbox negative guards. |
| IR-3 error mapping | pass | Unknown/outside-id read and annotate responses both 404 with equal normalized bodies; no A-file changes. |
| IR-4 generalization | pass | Twelve public shot-id methods enumerated and exercised; eight texts and both scan loops covered. |
| IR-5 test rigor | pass | Assertion audit below; no weak test masking an observed product defect. |
| IR-6 new input schemas | n/a | Existing settings/route boundaries unchanged; no new external payload. |
| IR-7 AC/deferral integrity | pass | All 10 + 8 + 8 criteria delivered; no missing required feature or invented deferral. |
| Fresh evidence/state | pass | Current identity exactly equals the complete gate; 24 snapshot paths match. |

### Test rigor audit

| Test surface | Grade | Basis |
|---|---|---|
| capture-key.test.ts and capture-key.behavior.test.ts | Strong | Exact substitutions/defaults, source-holder set, saved/draft distinction, bounded follow, cancellation and rejected reads. |
| test_capture_inbox_scope.py and test_api_capture_inbox_scope.py | Strong | Real SQLite/Pillow/API, preserved row/file values, return-to-folder, linked-file spy, complete id census, concrete 404 body equivalence. |
| capture-inbox-scope.behavior.test.ts | Strong | Recorded requests, controlled response ordering, selected-shot and negative event/notice assertions. |
| capture-scroll-bars.test.ts and capture-scroll-bars.behavior.test.ts | Strong | Independent numeric expectations, edge cases, rendered movement, semantics and no editing side effects. |
| Added capture-settings-draft E2E tests | Strong | Real backend/temp inboxes, persistence, no reload, actual key status, folder switch/back and unchanged original files. |
| Added capture-inbox E2E tests | Strong | Real dimensions/drag/clamp/Fit plus opaque computed colors and numeric theme contrast. |
| Four existing source-scan expectations | Adequate | Static token ownership checks complemented by rendered default/saved-key tests. |
| Existing quick-start/help-shot reader adaptations | Adequate | Default normalization retains the rendered comparison and hash oracle; unchanged manifest pin remains covered. |

### Durable reviewer evidence

All commands ran from P:/av-kit with PYTHONDONTWRITEBYTECODE=1, TMP/TEMP under the assigned exec-review/tmp folder, an offline scratch uv cache, and ELECTRON_RUN_AS_NODE unset. Shell output used unfiltered RTK receipts; exit codes were preserved immediately.

```json
{"schema_version":"evidence.v1","check_id":"reviewer-current-state","command":"rtk proxy uv run --no-sync python docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars/identity.py --state-only","cwd":"P:/av-kit","scope":"current D6 input identity, before and after independent checks","phase":"static","exit_code":0,"result":"pass","tested_state":"e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78","output":"Both observations exactly match the supplied full gate identity."}
```

```json
{"schema_version":"evidence.v1","check_id":"reviewer-python-regressions","command":"rtk proxy uv run --no-sync pytest -q --tb=short -p no:cacheprovider tests/unit/test_capture_inbox_scope.py tests/e2e/test_api_capture_inbox_scope.py tests/unit/test_capture_service.py tests/e2e/test_api_captures.py tests/e2e/test_api_capture_crop.py tests/tooling/test_help_guide_ste.py","cwd":"P:/av-kit","scope":"new inbox service/API contracts and specified regression suites","phase":"targeted","exit_code":0,"result":"pass","tested_state":"e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78","output":"109 passed in 52.60s"}
```

```json
{"schema_version":"evidence.v1","check_id":"reviewer-pins-scope","command":"rtk proxy uv run --no-sync python docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars/row-check.py guards --row 11","cwd":"P:/av-kit","scope":"Red hashes, named expectations, preserved tests, scope/read-only files and line endings","phase":"static","exit_code":0,"result":"pass","tested_state":"e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78","output":"pins: 18 file(s), 0 problem(s); named expectations: named lines; added-only test-ids.ts: 5 lines; 122 read-only; row-check guards: 0 problem(s)"}
```

```json
{"schema_version":"evidence.v1","check_id":"reviewer-gate-and-runtime","procedure":"Read gate run 2 and run 1 failure receipts, six-file diagnostic, gate source, both raw Electron report.json files, their summaries and snapshot record. Compare all 24 snapshot paths to current Git blob hashes without writing objects. Inspect scoped production and test diffs against the ACs.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"independent evidence audit; existing full and runtime runs, not a reviewer full rerun","phase":"review","exit_code":null,"result":"pass","tested_state":"e5028a3ad45fa033c388dea46658ff282fbd7364+937ef42b857984acb234116d46866c6f400165b024ddc6e8e943398619c92a78","output":"Gate: 1716 UI / 3379 Python passed, all steps exit 0, identity unchanged. Electron Red: four intended expectation failures; Green: all four expected, 260/260 expected, no flaky/skipped/unexpected. Snapshot comparison: 24 paths, zero mismatches. Theme contrast: dark 10.73, light 7.02."}
```

Additional independent commands, each exit 0: plan `row-check.py canon` (nine 09 edits and one grouping edit, zero problems); `eol-check.py` (42 paths, zero problems); `tools/help_guide_ste.py` (zero problems); `tools/export_openapi.py --check openapi.committed.json` (no drift output).

## Verdict

**approved** — intent achieved; no evidence-backed material defect found. The review report is complete at C:/Temp/av-kit/cki-exec-review-round-1.md. The coordinator can validate and copy it unchanged to the canonical review path, then continue H2. This verdict gives no commit or push authorization.

