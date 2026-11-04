---
date: "2026-10-16"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-10-14-capture-render-fidelity/implementation-plan.md"
loop_id: "s36-execution-2026-10-14-capture-render-fidelity"
round: 1
verdict: "approved"
findings_count: 0
blocking_findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-gpt-6.1-sol"
intent_anchor: "Session 36 makes capture rendering faithful: MEU-82 aligns the text preview baseline with the baked PNG, MEU-83 fixes arrow shaft/head geometry and anti-aliases the baked head, MEU-84 reconciles the annotated path and makes Open file/folder target the viewed file, all within PRODUCT_SCOPE."
intent_achieved: "yes"
---

# Critical Review: 2026-10-14-capture-render-fidelity

> **Review Mode:** execution, ledger round 1 of 6
> **Verdict:** approved

## Intent Anchor

Session 36 makes capture rendering faithful: MEU-82 aligns the text preview baseline with the baked PNG, MEU-83 fixes arrow shaft/head geometry and anti-aliases the baked head, MEU-84 reconciles the annotated path and makes Open file/folder target the viewed file, all within PRODUCT_SCOPE.

**Intent achieved: yes.** The delivered implementation and meaningful regression tests satisfy the 21 acceptance criteria. No evidence-backed material defect survived verification.

## Scope

**Worktree:** `P:/av-kit/.claude/worktrees/s36-capture-render-fidelity`, branch `claude/s36-capture-render-fidelity`. Baseline: `534beb174e2be1a97fc0cd248f53b4b8cdc83e49`. Scope is its baseline diff plus the untracked files, not the other checkout at `P:/av-kit`.

**Handoff set, reviewed in dependency order:**

1. `.agent/context/handoffs/2026-10-14-capture-render-fidelity-MEU-82-handoff.md`
2. `.agent/context/handoffs/2026-10-14-capture-render-fidelity-MEU-83-handoff.md`
3. `.agent/context/handoffs/2026-10-14-capture-render-fidelity-MEU-84-handoff.md`

**Plan folder:** `docs/execution/plans/2026-10-14-capture-render-fidelity/`, including implementation-plan, task, walkthrough, human-gate-decision, session-gate, identity, red-check, aa-oracle-probe, census-r1 and baseline.sha. Reviewed actual product/test/fixture changes, hub edits, SSOT state and named receipts. The multi-MEU handoff expansion applies to all three MEUs. Reflection and metrics belong to the explicitly pending H2 phase.

**Independence:** Claude Code / Anthropic authored the work; Codex `gpt-6.1-sol` / OpenAI performed this review. No reviewed files were edited. The report is written only here; the orchestrator owns its complete canonical copy to `.agent/context/handoffs/2026-10-14-capture-render-fidelity-implementation-critical-review.md`.

**Method:** execution IR-1–IR-7, docs DR-1–DR-8, AC tracing and E1–E5. Static review and the expressly permitted read-only probes only. No project test suite, build, install, session gate or generator was executed by the reviewer. The terminal-preflight/output-evidence procedures and completion-preflight were consulted; the user's review-only write and command limits govern their application.

## Findings

| # | Severity | Blocking | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|

None. No formatting or ceremony findings are raised.

## Acceptance Criteria Trace

Paths below are relative to the reviewed worktree. Product filenames beginning `capture-` and `Capture` resolve under `ui/src/renderer/src/features/capture/`, except the explicitly qualified main-process files. `adapter.py` resolves to `packages/infrastructure/src/avkit_infra/capture/adapter.py`; service references are fully qualified. Each test reference identifies a test that detects loss of the stated behavior; characterization/freshness checks intentionally already passed at baseline.

### MEU-82

| AC | Product file:line / delivering artifact | Test file:line that detects loss | Status |
|---|---|---|---|
| AC-82.1 | `capture-segoe-metrics.ts:2`; `capture-text-metrics.ts:12` | `ui/tests/unit/capture-text-metrics.test.ts:22`, `:34` — constants, 17 sizes, naive-rounding negatives | pass |
| AC-82.2 | `adapter.py:121`, `:391`, `:401`; `capture-segoe-metrics.ts:2` — same Segoe font/ascender basis | `tests/unit/test_capture_text_metrics.py:38`, `:49`, `:57` — live Pillow metrics, corrupted fixture, la/ls offset | pass |
| AC-82.3 | `capture-text-metrics.ts:2`, `:20` | `ui/tests/unit/capture-text-metrics.test.ts:43` — exact baseline and clamp | pass |
| AC-82.4 | `CaptureViewport.tsx:188`, `:206`; unchanged `textBackgroundBox` at `capture-text-metrics.ts:40` | `ui/tests/unit/capture-page.behavior.test.ts:889` — detail-loaded mark, y=38, exact plate, outside/inside selection | pass |
| AC-82.5 | `adapter.py:388`; `tools/capture_bake_fixture.py:26`; both `ui/tests/e2e/fixtures/capture-fidelity-*.png` | `tests/unit/test_capture_bake_fixture.py:26`, `:40`, `:52` — full decoded bytes, moved-mark negative and writer round trip | pass |
| AC-82.6 | `CaptureViewport.tsx:206`; `capture-text-metrics.ts:12` | `ui/tests/e2e/capture-inbox.test.ts:1747` (measurement at `:1671`) — actual Electron preview/bake ink and plate bounds | pass |

### MEU-83

| AC | Product file:line | Test file:line that detects loss | Status |
|---|---|---|---|
| AC-83.1 | `capture-arrow-head.ts:2`, `:14`, `:31`; drawing's zero-length guard `CaptureViewport.tsx:148` | `ui/tests/unit/capture-arrow-head.test.ts:56`, `:85`; no-head rendering also at page behavior `:932` | pass |
| AC-83.2 | `adapter.py:38`, `:63`, `:84`; bake zero-length guard `:345` | `tests/unit/test_capture_adapter.py:665` — constants, five shared cases, short/zero shaft results | pass |
| AC-83.3 | `capture-arrow-head.ts:40`; `adapter.py:100` | `ui/tests/unit/capture-arrow-head.test.ts:91`; `tests/unit/test_capture_adapter.py:701` — four fixture directions × strokes 1–64 × both corners, including tip-ended negatives | pass |
| AC-83.4 | `CaptureViewport.tsx:124` — model endpoints on group, shortened/absent line, conditional head | `ui/tests/unit/capture-page.behavior.test.ts:932`; amended zoom tests `:1903` and `ui/tests/e2e/capture-inbox.test.ts:1123` | pass |
| AC-83.5 | `adapter.py:343`, `:367`, `:369` | `tests/unit/test_capture_adapter.py:728` — real bake and module-level shaft-to-tip monkeypatch negative | pass |
| AC-83.6 | `adapter.py:355`, `:358`, `:370`, `:374` | `tests/unit/test_capture_adapter.py:755` — blends, solid interior and all outside-tile bytes | pass |
| AC-83.7 | `adapter.py:349`, `:353`, `:374` | `tests/unit/test_capture_adapter.py:790` — clipped head, color at (111,60), outside-tile preservation, wholly outside no-op | pass |
| AC-83.8 | `adapter.py:355`, `:356`, `:367`, `:369`, `:370` | `tests/unit/test_capture_adapter.py:809` — source requirements plus positive tile-mask size and negative full-canvas size spy | pass |
| AC-83.9 | `CaptureViewport.tsx:136`, `:152` — group stroke retained, polygon stroke none | `ui/tests/unit/capture-page.behavior.test.ts:978` | pass |

### MEU-84

| AC | Product file:line | Test file:line that detects loss | Status |
|---|---|---|---|
| AC-84.1 | `packages/core/src/avkit_core/services/capture.py:278`, `:317`, `:329` | `tests/unit/test_capture_service.py:1039`, `:1052`, `:1065`, `:1078`, `:1098` — independent clears, timestamp, no save and original deletion | pass |
| AC-84.2 | `packages/core/src/avkit_core/services/capture.py:340`, `:323` — list invokes scan/reconcile | `tests/e2e/test_api_captures.py:1009` — real services, SQLite, PNG, annotate/list/detail/image lifecycle | pass |
| AC-84.3 | `capture-viewed-file.ts:10` | `ui/tests/unit/capture-viewed-file.test.ts:8`, `:13` — both variants, null/empty fallback and no shot | pass |
| AC-84.4 | `CapturePage.tsx:296`; `capture-commands.ts:118`, `:126`, `:145` | `ui/tests/unit/capture-page.behavior.test.ts:989` — button/palette targets and catalog refetch | pass |
| AC-84.5 | Same selection/commands; `ui/src/main/index.ts:379`, `:386` | `ui/tests/e2e/capture-inbox.test.ts:1802` — ordered actual main-process log for both variants | pass |
| AC-84.6 | `ui/src/main/e2e-shell.ts:6`, `:13`; `ui/src/main/index.ts:379`, `:386` | `ui/tests/unit/capture-main.behavior.test.ts:273`, `:284`, `:296` — order, env isolation, early return and retained production shell calls | pass |

## Commands Executed and Decisive Output

All shell reads/probes used `rtk proxy`, the specified worktree cwd, all-stream receipts under `C:/Temp/av-kit/`, immediate exit capture and completed-receipt reads. Probe processes used `PYTHONDONTWRITEBYTECODE=1`; selftests used `TEMP`/`TMP=C:/Temp/av-kit`, so scratch writes stayed outside the repository. `ELECTRON_RUN_AS_NODE` was cleared for identity derivation.

| Executed command / observation | Exit | Decisive output |
|---|---|---|
| `rtk proxy git status --short` | 0 | 42 changed/untracked paths; product, listed tests/fixtures/tools, plan-local and administrative artifacts only |
| `rtk proxy git diff 534beb1 -- packages ui/src tools/capture_bake_fixture.py` | 0 | Only listed capture rendering/reconciliation/selection and E2E-log product hunks |
| `rtk proxy git diff 534beb1 -- tests ui/tests` | 0 | Existing expectation changes limited to TA-1–TA-7; added contract tests and oracles |
| `rtk proxy git diff 534beb1 -- docs/build-plan/09-screenshot-capture.md docs/build-plan/build-priority-matrix.md docs/BUILD_PLAN.md .agent/context/meu-status.yaml docs/execution/plans/2026-10-14-capture-render-fidelity/session-gate.ps1 docs/execution/plans/2026-10-14-capture-render-fidelity/red-check.py docs/execution/plans/2026-10-14-capture-render-fidelity/implementation-plan.md` | 0 | Actual D-20/D-21 amendments, ANSI fix, G-1/G-2, truthful hub/ready-for-review state |
| `rtk proxy git diff --quiet 534beb174e2be1a97fc0cd248f53b4b8cdc83e49 -- packages/api openapi.committed.json` | 0 | No diff in frozen API/OpenAPI paths |
| `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-10-14-capture-render-fidelity/red-check.py --selftest` | 0 | `red-check selftest: 11 fixture(s), 0 wrong: []`; colored assertion accepted, colored timeout refused |
| `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-10-14-capture-render-fidelity/identity.py --selftest` | 0 | `identity selftest: 0 failure(s)`; bound mutations changed identity and refused historical evidence; project artifacts did not |
| `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-10-14-capture-render-fidelity/identity.py --state-only` | 0 | Exact state below, equal to all handoffs and both H1 identity receipts |
| `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-10-14-capture-render-fidelity/aa-oracle-probe.py --pad 4` | 0 | Positive: 0 leak, halo 0, 641 edge pixels, blend 0.5117, interior deviation 4, outside changed 0. Full-shaft negative: 58 leaks. Baseline: 53 leaks, blend 0.0. Clipped probe red; wholly outside unchanged. All seven verdict booleans true |
| `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s36-review-font-probe.py` | 0 | `Segoe ascent sweep: 8195 sizes; mismatches=[]; font_errors=[]` — all integers 1–8192 plus 16384, 32767, 65535 |
| `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s36-review-static-probe.py` | 0 | Nine parser scenarios matched expectations; all 8 frozen adapter ASTs unchanged; Pillow primitive reconstruction exactly matched annotated RGB pixels |
| `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s36-review-report-probe.py` | 0 | Required report metadata valid; 21 unique AC rows; 0 findings; approved/yes; all 42 current changed paths exactly match the initial status observation |

The reviewer probes are short stdlib/Pillow programs in the receipts directory. The font probe transcribes the TS formula and compares `getmetrics()[0]`; it does not run a test suite. The static probe transcribes G-1's predicate, compares ASTs using `git show <baseline>:<adapter>`, and reconstructs the frozen text drawing with Pillow primitives; it imports no project test or product module. The report probe checks the report's metadata/AC set and compares the final static Git path list with the initial observation.

Supporting shell reads were `rtk proxy pwsh -NoProfile -Command ...` with `Get-Content` over the workflow/context, plan folder, three handoffs/template, relevant source/config/test sections and receipts; `rg -n` over AC declarations, font/view selection wiring and harness prerequisites; and `Get-ChildItem`/`Get-FileHash -Algorithm SHA256` over the named receipt sets. Their decisive observations appear throughout this report. Reviewer read receipts are `s36-review-{protocol,context,plan,contract,walkthrough,scripts1,scripts2,handoffs,product,newfiles,wiring,receipts,rowreceipts,docdiff,trace,final-contract,closeout-read}.txt`. Product/test diffs are also retained as `s36-review-{diff,testdiff,pytests,e2e-tests}.txt`.

Two initial read-command setup attempts failed before obtaining evidence: trying to pass PowerShell's `Get-Content` directly through RTK, and an expanded double-quoted child script. Both were corrected with explicit `pwsh`/literal quoting; neither changed repository state or supplied a passing verification claim. The memory registry search found no Session 36 material and was not used as evidence.

### Current identity and reused gate evidence

```text
534beb174e2be1a97fc0cd248f53b4b8cdc83e49+53752bff3673103ed7b022f1acc53376c3170362093ec3896b34747ff49615d4
```

```json
{"schema_version":"evidence.v1","check_id":"s36-review-current-state","command":"rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-10-14-capture-render-fidelity/identity.py --state-only","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"current D6 inputs with ELECTRON_RUN_AS_NODE unset","phase":"targeted","exit_code":0,"result":"pass","tested_state":"534beb174e2be1a97fc0cd248f53b4b8cdc83e49+53752bff3673103ed7b022f1acc53376c3170362093ec3896b34747ff49615d4","output":"534beb174e2be1a97fc0cd248f53b4b8cdc83e49+53752bff3673103ed7b022f1acc53376c3170362093ec3896b34747ff49615d4","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s36-review-gate-receipt-audit","procedure":"Read s36-gate-h1.txt and per-stage receipts; compare complete identity before/after with reviewer-derived state and all three handoffs; read Red/Green child exits, diagnostics and summaries.","observer":"codex-gpt-6.1-sol","cwd":"P:/av-kit/.claude/worktrees/s36-capture-render-fidelity","scope":"H1-2 gate and per-MEU evidence","phase":"targeted","exit_code":null,"result":"pass","tested_state":"534beb174e2be1a97fc0cd248f53b4b8cdc83e49+53752bff3673103ed7b022f1acc53376c3170362093ec3896b34747ff49615d4","output":"H1-2: static exits 0; pytest raw exit 1, 2 baseline failures and 674 passed, no errors, baseline predicate accepts; Vitest 85 files/815 passed; Electron 139 passed; repeat 20 passed; frozen AST []; outside scope []; identical before/after state. Red child .exit files all 1 and failures attributable to planned behavior/new exports. No project suite rerun by reviewer."}
```

The H1 gate is a **baseline-adjusted pass**, not an assertion that pytest returned zero. Its packaging failures are exactly AC-24.10 (absent PyInstaller tree) and AC-25.10 (absent ffmpeg/ffprobe), as at baseline. No other Python test failed. The full Vitest and Electron summaries contain no skips/retries/flaky result category. The Red MEU-84 `102 skipped` count comes from the declared `-t AC-84` selection, not added skip annotations; the final unfiltered unit suite passed all 815 tests.

Observed per-MEU records agree: MEU-82 pin 9 / Green Python 26, UI 130, Electron 29; MEU-83 Green Python 63, UI 132, Electron 29; MEU-84 Green Python 56, UI 146, Electron 30, extra repeat 10. The initial MEU-83 Electron run's two failures remain disclosed; its focused rerun passed 6 cases and stress passed 40. Both later full gates passed. Attempt archives 1–5 preserve prerequisite/status/environment failures and subsequent successful runs. H1 structural/AC/evidence receipts report OK for all three handoffs, and hub/render/audit observations match actual files.

Receipt SHA-256 values observed with `Get-FileHash`:

| Receipt | SHA-256 |
|---|---|
| `s36-gate-h1.txt` | `45acda58d90f29617088855c98a4a6e92408c1c5cc4fd3ce2a6c33a97fc95655` |
| `s36-D6-py-tests.txt` | `f84821e7a93fefe6e47b8f8c3d09a7072726b0d26590f247f5f4ef028a02a717` |
| `s36-D6-ui-tests.txt` | `866a7ccbf8d59361f2319116926d9760981098c6951ed9b65267359371ca30a8` |
| `s36-D6-ui-electron.txt` | `96b5f7deea1502a0254ecf1d23dae8292df18e4dc12c3056eeacc074f8a2bdf5` |
| `s36-D6-e2e-repeat.txt` | `1475ef67f92c490f091048eac56bf7bededb0d316eaa3b061da5f5e012f6bc9c` |
| `s36-D6-identity-before.txt`, `s36-D6-identity-after.txt` | `28fb904ea107aa74683f28a23aeb9c648ce15a8a1934607c5c4d3951981dd0b0` |

## Substantive Review: E1–E5

### E1 — Delivery

**MEU-82:** `segoeAscentPx` implements the approved 26.6 rounding, rather than selecting fixture values or using the wrong plain ceil. No JS bitwise coercion limits it to signed 32-bit intermediate values. The UI accepts positive integers with no explicit upper size limit; the algebra is size-independent, and the additional sweep covers thousands of non-fixture sizes and large values without disagreement. That finite probe is supporting evidence, not a claim of exhaustive testing of arbitrarily large input. The plate function and hit-test files have no changed behavior; the page test checks their observable dimensions and selection. Only text y/baseline and the metric constants changed.

**MEU-83:** TS/Python constants, angle signs and shaft formulas agree. Short arrows return no shaft; zero-length arrows retain the legacy endpoint while both renderers explicitly omit the head. The SVG head now has no inherited outline. The bake makes a clipped tile, creates its 4× L coverage mask, applies the 1.5 supersample coordinate offset, draws shaft/head, LANCZOS-downscales and composites the solid opaque mark color through coverage. It converts input to RGBA before cropping/compositing, so RGB, RGBA and palette input do not produce palette-index or channel-count errors. Opaque RGB-equivalent inputs therefore follow the same coverage arithmetic in all three modes. Outside the tile stays unchanged in the working RGBA image; empty clipped tiles return unchanged. The existing bake converts final output to RGB for PNG/JPEG/WebP; transparency export semantics were not changed or claimed. This mode assessment is source-based; the persisted real-adapter raster tests use RGB fixtures.

**MEU-84:** Reconciliation remains under the same lock and unit of work. The original-missing branch alone deletes a row; surviving originals reach independent nullable-path checks and a save guarded by actual tuple inequality. No new unlink/delete of files exists. Selection wiring uses the current selected catalog object and `viewVariant`, so refetched paths update commands. Both buttons and the palette call the same viewed-path functions. E2E recording is called from the exact `AVKIT_E2E === '1'` early-return branches; the production branches still call Electron shell. The exported recorder itself is callable as a module function, but no production caller reaches it, and the global log is published only under the E2E flag, as contracted.

### E2 — Fidelity oracles

The Electron text oracle screenshots the image element's visible rectangle, including the sibling SVG overlay within that clip; it does not merely decode the original file. It checks 100% zoom, loaded variant images, removal of vectors for Annotated, non-null ink/plate boxes, all four sides within one pixel, and ink containment. D-24 excludes only a 2-CSS-pixel perimeter caused by fractional screenshot bounds; the fixture's mark lies far inside that ring. Red still measures the actual 8-pixel baseline defect. Green records identical ink `(23,42)-(48,65)` and plates differing by at most one pixel. Tolerance was not padded.

The PNG freshness test compares every decoded RGB byte with a real adapter bake; a y+1 negative must differ. The reviewer independently reconstructed the frozen Pillow text primitives and matched decoded pixel SHA-256 `e7bca9e5a088b0ea707fc0e2dc7fe59abe5ba1b6d9d71af1a847c88d53d36b12`.

The arrow tip oracle derives expected geometry independently of production helpers and has an effective negative control patched at the actual module-level shaft function. The edge oracle simultaneously requires substantial blending, correct solid interior and unchanged outside-tile bytes, so blank output, an aliased baseline or generic blur does not satisfy the combined checks. Geometry fixtures/property tests and source/mask-size tests complement those raster probes; the oracles are not claimed to prove arbitrary raster equivalence for every possible image. The permitted calibration independently reproduced the positive/negative metrics.

### E3 — Test integrity and execution decisions

All removed/replaced existing assertions fit TA-1–TA-7. TA-5/TA-6 retain exact stored endpoints while moving observation to the group, and AC-83.4 separately pins the actual shortened line. TA-7 is an honest adaptation to a head-only arrow: it measures rendered tip-to-left length 35 at stroke 7, versus 15 if the stroke edit is lost under the new constants. The old design produced length 28 in Red. The remaining font-edit assertions stay intact. D-20 and D-21 are recorded as human decisions, not autonomous waivers; the user explicitly placed them in this review's scope.

D-23 strips formatting escapes without changing the Red conditions; the new colored positive/negative fixtures both behave correctly. D-24 was a setup correction before formal Red and leaves the actual mark region and one-pixel contract intact. D-27 places the observable no-head assertion in AC-83.4 instead of changing a vertex helper's return signature; the bake's no-head condition is explicit in source. D-28 adds a positive expected tile-mask allocation to the size spy, preventing a no-supersampling implementation from passing the negative allocation test alone. No added `.skip`, `.only`, retry configuration or timeout padding appears in the diff.

### E4 — Evidence honesty

The current independent identity matches all three handoffs and H1-2 exactly. Scope ASTs were also independently compared. Counts, failure diagnostics, baseline adjustments and shell-target evidence agree with the receipts. D-12 is consistently described as the approved plan's silent-message default (factor 5 / angle 0.45), not as an explicit size choice made by Mat. The walkthrough preserves the earlier unrecorded plan-round ledger problem, the VENV repair and failed gate attempts instead of presenting them as successful runs. This review does not rewrite that history or count it as this execution loop's round.

### E5 — Scope

Every current changed/untracked path is in the plan's Files tables, its plan-local artifacts or the enumerated administrative/handoff outputs. The current status contains 42 paths versus H1 gate's 37 because the three handoffs and later registry/focus updates are post-gate project artifacts; this does not change the bound input state. No diff exists under `packages/api` or `openapi.committed.json`. All eight scope-AST functions remain identical to baseline. The hub Arrow/Text/Head rows accurately state the delivered geometry, baseline and AA; matrix 9.15–9.17 has the correct MEUs, anchors and dependencies. Existing GUI action ids/IPC remain accurate. SSOT remains `ready_for_review`, with H2 approval/issue/reflection/metrics work pending as designed.

## Gate Changes

### G-1 — Accepted: faithful application of the approved Baseline rule

Removing `-x` is necessary to inspect all regressions rather than stop at the first known packaging failure. The allow-list includes the **complete parametrized nodeids** for precisely the two baseline failures. Raw pytest exit 1 is accepted only with a nonempty FAILED set entirely within that list and no ERROR lines; other nonzero exit codes propagate. The actual receipt contains exactly those two failures and 674 passes.

Collection errors normally return 2 and fail before the exception applies; if combined execution returns 1, `-rE` emits `ERROR ...` and the error check refuses it. Other FAILED ids, including parametrization suffixes, remain outside the exact allow-list. Strict XPASS is a FAILED nodeid and cannot hide an unrelated regression. Expected XFAIL and non-strict XPASS keep pytest's existing successful-test semantics; G-1 does not introduce xfail marks, alter strictness, or turn an ordinary failure into one. The nine-case stdlib transcription verified these distinctions, including an added suffix on an allowlisted id and a receipt lacking FAILED ids.

The rule deliberately cannot distinguish a new failure reason inside an already excluded packaging test. That is the approved test-identity baseline boundary, not evidence that a capture regression passed. No new capture failure can use either exact packaging nodeid, and no false-pass of a material product defect was demonstrated. No blocking finding is warranted.

### G-2 — Accepted: build the suite's existing prerequisites

The added isolated harness build writes `ui/out-e2e/`; `dotnet publish` writes the stub's `publish/` plus conventional `bin/`/`obj/` intermediates. All are covered by the actual `.gitignore` (`ui/out-e2e/`, `native/**/publish/`, `[Bb]in/`, `[Oo]bj/`), so they are not hashed as tracked/untracked input by identity.py. The tracked source/config/build scripts remain hashed.

The harness flag is confined to a child PowerShell build. The normal `ui-build` still runs, capture E2Es still launch `ui/out/main/index.js`, and only the primitive test launches `out-e2e`. The picker tests already explicitly choose the deterministic stub through `AVKIT_REGION_PICKER_PATH`; G-2 builds that existing stub rather than substituting it into production. It does not alter a test, assertion or product source. Actual missing-artifact failures and subsequent passes support the change; no masking of a Session 36 product defect was found.

## Checklist Results

Results below are manual observations by `codex-gpt-6.1-sol` with null exit codes unless an executed command is named above. They describe this review and inspected execution evidence, not a reviewer rerun of the product suites.

| Check | Result | Procedure / decisive evidence |
|---|---|---|
| IR-1 Live runtime evidence | pass | Trace real `build_services` API test and real Electron launch paths; inspect Green/H1 receipts, 139 Electron passes and 20 repeat passes |
| IR-2 Stub behavioral compliance | pass | Inspect fixture seam variant bytes/detail marks and existing picker stub selection; backend lifecycle uses real services/files |
| IR-3 Error mapping completeness | n/a | No new/changed write route or exception mapping; unchanged annotated-image 404 is asserted by AC-84.2 |
| IR-4 Fix generalization | pass | Compare TS/Python formulas, both open actions/palette, and independent annotated/sidecar reconciliation |
| IR-5 Test rigor | pass | Audit every new/amended test across all 11 changed/new test files; grading below; no weak changed test |
| IR-6 Boundary validation coverage | pass | Inspect unchanged strict annotation schemas and the added path/log boundaries; no input schema weakened |
| IR-7 Deferral and AC coverage | pass | Trace all 21 ACs above; integration ACs invoke real renderer/API/adapter/Electron behavior; no required behavior silently deferred |
| DR-1 Claim-to-state match | pass | Compare handoff claims to actual diff, code and preserved receipts |
| DR-2 Residual old terms | pass | Old hanging/head values remain only as baseline history or explicit alternatives; active rendering and hub rows carry the delivered values |
| DR-3 Downstream references updated | pass | Inspect sibling handoff references and new matrix/build-plan anchors |
| DR-4 Verification robustness | pass | Oracles reject baseline geometry/raster; reviewed fresh full evidence has no additional failure |
| DR-5 Evidence auditability | pass | Exact commands, current identity, raw decisive diagnostics and receipt hashes are recorded |
| DR-6 Cross-reference integrity | pass | Renderer/adapter contracts and actual 09:366, :367, :723 plus matrix 9.15–9.17 agree |
| DR-7 Evidence freshness | pass | Current input identity equals the recorded full gate; counts independently read from its preserved receipts, without a suite rerun |
| DR-8 Completion vs residual risk | pass | Baseline packaging exclusions and earlier failures are explicit; H2 remains pending; no required AC gap is concealed |
| AV-1 Failing-then-passing proof | pass | Read preserved Red child exits/attributed failures and subsequent Green/full receipts; baseline-characterization cases identified separately |
| AV-2 No bypass hacks | pass | The shaft monkeypatch deliberately makes the negative-control bake fail its oracle; no assertion mock or early successful exit added |
| AV-3 Changed paths asserted | pass | All 21 ACs trace to observable exact-value, raster, persistence or shell-target assertions |
| AV-4 No skipped/xfail masking | pass | Diff adds no skip/only/xfail/retry; selected Red tests explain filtered counts |
| AV-5 No unresolved placeholders | pass | Inspect complete changed product functions; no required unfinished branch or placeholder found |
| AV-6 Source-backed criteria | pass | FIC sources and D-8–D-21 map behavior to Spec, Local Canon, Research-backed or Human-approved decisions |
| Template/source/closeout checks | pass | Read REVIEW-TEMPLATE 2.2 and peer for structure; current plan/task/handoffs carry sources and evidence; pending H2 is explicit |
| Reused full gate identity | pass | Executed `identity.py --state-only` exit 0; exact equality to H1-2 and all three handoffs |
| Review write scope | pass | Repository untouched; report/probes/receipts only under `C:/Temp/av-kit` |

### IR-5 grading of changed tests

| Test file | New/amended tests audited | Grade |
|---|---|---|
| `ui/tests/unit/capture-text-metrics.test.ts` | AC-59.19, AC-82.1 (2), AC-82.3 | Strong: exact constants/values and incorrect-rounding negative |
| `tests/unit/test_capture_text_metrics.py` | Three functions including four corrupted-size parametrizations | Strong: live font comparison and la/ls relation |
| `tests/unit/test_capture_bake_fixture.py` | All three tests | Strong: complete byte comparator plus moved-mark and writer controls |
| `ui/tests/unit/capture-arrow-head.test.ts` | AC-59.2, AC-83.1 (2), AC-83.3 | Strong collectively: pinned fixture and geometric property; fixture-only negative supports the runtime checks |
| `tests/unit/test_capture_adapter.py` | AC-59.2, AC-83.2/.3/.5/.6/.7/.8 | Strong: independent geometry, real raster, negative control and allocation spy |
| `ui/tests/unit/capture-page.behavior.test.ts` | AC-82.4, AC-83.4/.9, AC-84.4, amended AC-59.19/65.3/66.11 | Strong: rendered exact geometry and user-driven state/target changes |
| `tests/unit/test_capture_service.py` | AC-84.1 a–e | Strong: real files, field independence, ticking timestamp and save spy |
| `tests/e2e/test_api_captures.py` | AC-84.2 | Strong: real API/DB/files and positive-to-negative lifecycle |
| `ui/tests/unit/capture-viewed-file.test.ts` | Both AC-84.3 tests | Strong: complete specified path truth table |
| `ui/tests/unit/capture-main.behavior.test.ts` | Three AC-84.6 tests | Strong module behavior; Adequate source-structure guard for branches, corroborated by Electron and inspected production calls |
| `ui/tests/e2e/capture-inbox.test.ts` | AC-82.6, AC-84.5, amended AC-66.14 | Strong: rendered pixel bounds, actual main-process targets and retained endpoint values |

## Verdict

**approved** — zero findings, zero blocking findings; intent achieved **yes**. G-1 and G-2 are substantively acceptable. The reviewed tree is bound to a fresh recorded baseline-adjusted full gate; the additional permitted probes passed.

**Follow-up actions:** the orchestrator should validate and record this round-1 verdict, copy this complete report to the canonical rolling review file, then perform the already planned H1-7a/H1-7b and H2 closeout. This report neither completes those pending tasks nor authorizes commit/push. No correction round is required by this review.

**Limits:** product suite/runtime results were inspected from preserved receipts, not rerun. Segoe-only metrics, the existing RGB export policy and the two baseline packaging exclusions remain the approved boundaries. No unresolved product-contract question was identified.
