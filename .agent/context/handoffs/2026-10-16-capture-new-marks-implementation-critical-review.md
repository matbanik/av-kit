---
date: "2026-10-16"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md"
loop_id: "s39-execution-2026-10-16-capture-new-marks"
round: 1
verdict: "approved"
findings_count: 1
blocking_findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-gpt-6.1-sol"
intent_anchor: "Session 39 delivers MEU-90 (a pixelate mark whose bake and live editor preview agree within one level per channel) and MEU-91 (an eraser mark filled with the colour sampled from its border), carried through the domain, sidecar, REST/OpenAPI, MCP, bake and Capture page, with drawn marks always painted over the region marks, all within PRODUCT_SCOPE."
intent_achieved: "yes"
---

# Critical Review: 2026-10-16-capture-new-marks

> **Review Mode:** execution, ledger round 1 of 6  
> **Verdict:** approved; one non-blocking test observation.

## Intent Anchor

Session 39 delivers MEU-90 (a pixelate mark whose bake and live editor preview agree within one level per channel) and MEU-91 (an eraser mark filled with the colour sampled from its border), carried through the domain, sidecar, REST/OpenAPI, MCP, bake and Capture page, with drawn marks always painted over the region marks, all within PRODUCT_SCOPE.

The delivered work achieves this intent within the approved opaque-preview and format-decoding boundaries. No evidence-backed material product defect remains in this review.

## Scope

**Checkout:** `P:/av-kit-wt/s39-capture-new-marks`, branch `claude/s39-capture-new-marks`, HEAD/baseline `90bb40977e487f4893a1c586c2c20b8f78ef105f`. Every shell command used that working directory. Changes reviewed: `git diff 90bb409` plus the untracked files, including the new region algorithm, fixtures and tests. There are 41 tracked changed paths and 17 untracked files at review time.

**Correlated handoff set, in execution order:**

1. `.agent/context/handoffs/2026-10-16-capture-new-marks-MEU-90-handoff.md`.
2. `.agent/context/handoffs/2026-10-16-capture-new-marks-MEU-91-handoff.md`.

**Plan folder:** `docs/execution/plans/2026-10-16-capture-new-marks/`, including implementation-plan, task, walkthrough, baseline and all five scripts. Also reviewed the changed hub/SSOT records, relevant issue record, full test diffs, original surrounding gesture/service code and the specified receipt snapshots. REVIEW-TEMPLATE v2.2 supplied this report's structure; the Session 36 implementation review supplied layout calibration only.

**Independence and write scope:** Claude/Anthropic authored the implementation; this Codex reviewer authored none of it. No repository file was written. This report and the reviewer's independent probe/receipts are under `C:/Temp/av-kit/dispatch/`. The orchestrator must copy the complete report to `.agent/context/handoffs/2026-10-16-capture-new-marks-implementation-critical-review.md`. The main checkout was used only for the explicitly required review vocabulary read.

**Verification boundary:** source/receipt review and the explicitly permitted verifiers and stdlib/Pillow probe only. No project tests, builds, generators, dependency installation, gate, lint/task validator or MCP audit were executed. Recorded suite results below are inspected author evidence, not fresh reviewer suite runs. H2 reflection/metrics are subsequent orchestrator work, not silently declared complete here.

## Findings

| # | Severity | Blocking | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|
| F1 | Low | no | The AC-90.10 deselect subcheck is vacuous: Undo already clears selection, and the subsequent (190,190) click maps outside the 8x8 image. A broken empty-image deselect handler would still pass this subcheck. Required creation, selection, movement, block editing, Save and Delete assertions remain substantive; deselection is not a listed AC-90.10 requirement. | `ui/tests/unit/capture-page.behavior.test.ts:1608` | In a follow-up, select the pixelate and assert it is selected before clicking empty image at (175,175); retain the deselection assertion. | open |

F1 metadata: confidence **High**, subject **deliverable**, finding_kind **behavior**; no control-defeat mechanism or blocking AC violation is asserted. This is the already-disclosed test-authoring observation, independently confirmed against `CapturePage.tsx:1356` and pointer mapping. It does not warrant an execution correction round under the workflow's Materiality Gate.

## Resubmission Verification — Same Unused Round 1

The earlier submission was refused before ledger recording because its approval carried an IR-5 `partial` checklist result. This is a complete replacement submission for the same unused round, not a second review round. The substantive verdict and F1 are unchanged. IR-5 is **pass** because the audit was completed and every required AC has meaningful coverage; this does not certify the optional deselect subcheck. That weakness remains openly recorded as F1, without blocking approval.

The user authorized evidence reuse after identity and status confirmation. The previous report's command results and source/receipt observations below are reused explicitly; they are not represented as newly executed suites. This resubmission freshly read the protocol, operating context, plan/task/walkthrough and both handoffs, the report/template/schema, the actual Python/TS region algorithms and F1's test/Undo code. It also reran these checks, all from `P:/av-kit-wt/s39-capture-new-marks`, with outputs captured under `C:/Temp/av-kit/dispatch/s39-resubmit-*.txt`:

| Command / observed procedure | Exit | Decisive output |
|---|---|---|
| `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-10-16-capture-new-marks/identity.py --state-only` with `PYTHONDONTWRITEBYTECODE=1`, `ELECTRON_RUN_AS_NODE` unset | 0 | `90bb40977e487f4893a1c586c2c20b8f78ef105f+6ff3a8477070c9f7edc18f339b35c07c3ae1c8786ccfa03723d3a008d6f7b986`, exactly the prior review and both handoffs/gates. |
| `rtk proxy git status --short`, then compare completed old/new status receipts | 0 | Byte-decoded line-for-line equality, including the same harmless global-ignore permission warnings; identical modified/untracked path set. |
| `Get-FileHash -Algorithm SHA256` via `rtk proxy pwsh` on the five files in the snapshot table below | 0 | Every hash exactly matches that table. |
| `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-10-16-capture-new-marks/scope-ast.py --base 90bb409` | 0 | `scope-ast: adapter outside PRODUCT_SCOPE: 0 problem(s) (base 90bb409)`. |
| `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/dispatch/s39-independent-probe.py` | 0 | 10,080 ring cases, 600 random composed RGBA passes, all eleven JSON cases and both PNGs agree exactly; RGB/RGBA/palette ordering preserved; block-11 negative differs. |
| `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/dispatch/s39-resubmit-output-probe.py` (stdlib only; evaluates every assertion keyword present in the repository verdict schema) | 0 | Actual replacement verdict accepted; seven negative variants refused, including approved+partial, approved+fail and changes_required without a blocker. Report has all 24 AC mappings and the same F1 fields. |

The output probe omits inapplicable optional JSON properties rather than emitting null where the repository schema requires a string. Its first readback detected Windows newline translation and exited 1; normalizing the dispatch helper's text read fixed that artifact-only assertion, and the final run passed. It does not run the project validators or product suites and writes only under dispatch. No ledger or canonical review file was changed. The original refused report and JSON remain intact.

## Commands Executed and Decisive Output

All commands ran from the worktree. Exact-evidence operations used `rtk proxy`; shell receipts were captured under `C:/Temp/av-kit/dispatch/s39-review-*.txt`, with `$LASTEXITCODE` saved before readback and propagated. Bounded source reads used `rtk proxy pwsh -NoProfile -Command '... Get-Content ...'`. One early nested-shell read had a quoting ParserError and was immediately rerun using a single-quoted child command; no verifier/product operation ran in that failed read.

### Independent executable checks

For the six plan checks, the actual command prefix was `.venv/Scripts/python.exe docs/execution/plans/2026-10-16-capture-new-marks/` after `rtk proxy`. Each process had `PYTHONDONTWRITEBYTECODE=1`; `ELECTRON_RUN_AS_NODE` was unset. TEMP/TMP for the selftests were directed to the dispatch directory.

| Command after the prefix | Exit | Decisive output |
|---|---|---|
| `red-check.py --selftest` | 0 | `red-check selftest: 18 fixture(s), 0 wrong: []`; launch, timeout, unrelated import and passing-run negatives refused. |
| `identity.py --selftest` | 0 | `identity selftest: 0 failure(s)`; bound mutations change identity/refuse old evidence; artifact mutations leave it unchanged. |
| `identity.py --state-only` | 0 | `90bb40977e487f4893a1c586c2c20b8f78ef105f+6ff3a8477070c9f7edc18f339b35c07c3ae1c8786ccfa03723d3a008d6f7b986` |
| `scope-ast.py --selftest` | 0 | `scope-ast selftest: 16 fixture(s), 0 wrong: []`. |
| `scope-ast.py --base 90bb409` | 0 | `scope-ast: adapter outside PRODUCT_SCOPE: 0 problem(s) (base 90bb409)`. |
| `region-pass-probe.py` | 0 | Pillow 12.3.0; 400 reduce cases, 391 partial; quant parity 0, exact-mean difference at most 1; direct RGBA reduce differs up to 105; 5 clipped/oversized cases, zero leaks; 8 composed passes exact; wrong exact-mean sensitivity control differs in 6. |

Additional explicitly permitted reviewer probe:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/dispatch/s39-independent-probe.py *> C:/Temp/av-kit/dispatch/s39-review-independent-probe.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/dispatch/s39-review-independent-probe.txt; exit $code
```

Exit 0. Decisive output:

```text
D-29 independent outer/inner-ring comparison: 10080 rectangles; zero mismatches (includes 1-pixel images and edges)
Actual apply_region_pass vs independent RGBA reference: 600 composed random passes; zero byte mismatches; blocks 2..100, clipped/negative/empty rectangles, alpha included
Actual bake: RGB/RGBA/palette sources; drawn rect before/after composed region marks identical and stroke preserved
Committed JSON expected pixels vs independent reference: all 11 cases byte-identical
Committed PNG pair vs independent reference: exact; block-11 negative differs; no colour-management chunks
```

This probe imports the actual adapter. Its eraser reference enumerates the surrounding bounding rectangle minus the interior, independently of the implementation's ring enumeration. Its pixel reference sums each band independently. Temporary bake outputs were written only beneath dispatch. It did not invoke the fixture generator or a project test suite.

### Static and receipt commands

| Executed command / observed procedure | Exit | Decisive observation |
|---|---|---|
| `rtk proxy git log -1 --format='%H %D %s'` | 0 | HEAD is baseline `90bb40977e487f4893a1c586c2c20b8f78ef105f`, branch `claude/s39-capture-new-marks`. |
| `rtk proxy git status --short`; `rtk proxy git diff 90bb409 --stat`; `rtk proxy git ls-files --others --exclude-standard` (separate commands) | 0 each | 41 tracked changed files; 17 untracked files including nine plan-local files. All paths classified under the plan's Files tables or project administration. Git emitted global-ignore permission warnings; it still listed the expected local untracked files and identity matched the gate. |
| `rtk proxy git diff 90bb409 -- packages/core/src/avkit_core/domain/capture.py packages/core/src/avkit_core/domain/enums.py packages/core/src/avkit_core/services/capture.py packages/api/src/avkit_api/schemas/captures.py packages/api/src/avkit_api/routes/captures.py mcp-server/src/toolsets/capture.ts` | 0 | Additive DTO/enum/union/serialization changes; common validation retained. |
| Scoped `rtk proxy git diff 90bb409 -- ...` reads of all UI product files, all changed Python/MCP/UI tests, fixture writer, hub/state and committed OpenAPI | 0 each | Existing test edits are TA-1..TA-7; remaining tests are additions. No changed shared UI primitive, queue page, queue test, Electron main process, stylesheet, package/config or lockfile. OpenAPI adds only the two schemas and their union references. |
| `rtk proxy rg -n 'CapturePage\|features/capture\|capture-annotate\|capture-region-pass\|capture-toolbar\|capture-hit-test' ui/src ui/tests/e2e/download-queue.test.ts ui/tests/e2e/transcript-queue.test.ts ui/tests/e2e/convert-queue.test.ts` | 0 | Capture page is lazy at `router.tsx:57`; common-shell imports of capture-commands exist. See D-30 analysis for the distinction between import reachability and drag behavior. |
| `Get-Content` reads through `rtk proxy pwsh` of s39 baseline/Red/Green receipts, both gate snapshots, row6-out/out4, isolated misses, hub and closeout receipts; `.exit` files read beside all eight original Red receipts | 0 | Each Red child exit is 1 with the intended missing export/schema assertion; both Electron Reds say `Invalid overlay marks`. Green counts and final gate summaries match the handoffs. |
| `Get-FileHash -Algorithm SHA256` through `rtk proxy pwsh` on the five snapshot files below | 0 | Snapshot bytes pinned in the following table. |

In the rg command above, the displayed alternation pipes represent the actual regex alternations, not shell pipelines. Source reads additionally covered the workflow, AGENTS/GUARDRAILS/PROFILE, task/walkthrough/scripts, both handoffs, template, reviewer/harness rules, completion-preflight and the registered vocabulary. These are read observations, not validation passes attributed to their prose.

| Snapshot file | SHA-256 |
|---|---|
| `s39-gate-h1/s39-gate-h1.txt` | `7977950A75DB233E1C49FDC81C0D969641FAE31FBD277F7503D2CFEF6D958F37` |
| `s39-gate-h1/s39-D6-py-tests.txt` | `FC609422889186E2FC7ADEC48EFF78540201E9903C44585748AEF0534AC0C899` |
| `s39-gate-h1/s39-D6-ui-electron.txt` | `B948538769A1223E0422A5CBFB21139B9CE364D2694DECFA09B446D510D26811` |
| `s39-gate-h1/s39-D6-e2e-repeat.txt` | `B68F11DF47B1B46F50CC04AFCDF7605E072E51D45E91B28A047FD1D34A10964C` |
| `s39-gate-run5/s39-gate.txt` | `981152E1D1D417471D2DD55D03BF50FE01BAAF9EA92FA49CDBA6257CB7C3D0B3` |

All snapshot paths in this table are beneath `C:/Temp/av-kit/`.

## Acceptance Criteria — MEU-90

File references are relative to the worktree. “Pass” means source delivery and meaningful test assertions were verified and matching recorded execution was inspected; it does not claim a fresh reviewer suite run.

| AC | Product file:line delivering the behavior | Test file:line that would fail without it | Status |
|---|---|---|---|
| AC-90.1 | `packages/core/src/avkit_core/domain/capture.py:221`; `packages/core/src/avkit_core/domain/enums.py:236` | `tests/unit/test_domain_capture.py:406` | pass — exact fields/union/constants and invalid bool/float/range/size rejection |
| AC-90.2 | `packages/core/src/avkit_core/services/capture.py:192`, `:271`, `:936` | `tests/unit/test_capture_service.py:1116` | pass — round trip, extra-key policy, required block and origin clamp |
| AC-90.3 | `packages/api/src/avkit_api/schemas/captures.py:108`; `packages/api/src/avkit_api/routes/captures.py:160` | `tests/e2e/test_api_captures.py:1056` | pass — actual services, sidecar/default/detail, four refused bodies and committed/live schema |
| AC-90.4 | `mcp-server/src/toolsets/capture.ts:95`; `ui/src/renderer/src/features/capture/capture-annotate.ts:59` | `mcp-server/tests/capture.test.ts:479`; `ui/tests/unit/capture-annotate.test.ts:72` | pass — accepted forwarding, strict fields, boundary/default parity |
| AC-90.5 | `packages/infrastructure/src/avkit_infra/capture/adapter.py:137`, `:150`, `:277` | `tests/unit/test_capture_adapter.py:962` | pass — independent quant, clipped/partial/big/empty, lossy input decoding, outside unchanged and negative control |
| AC-90.6 | `packages/infrastructure/src/avkit_infra/capture/adapter.py:207`, `:281`, `:395` | `tests/unit/test_capture_adapter.py:1004` | pass — exact stroke, both list positions and wrong-order sensitivity control |
| AC-90.7 | `ui/src/renderer/src/features/capture/capture-region-pass.ts:19`, `:31`, `:124` | `ui/tests/unit/capture-region-pass.test.ts:102`, `:121`, `:131` | pass — all six pixelate cases exact, clipping/ignored drawn marks, comparator negative |
| AC-90.8 | `tools/capture_bake_fixture.py:196` and committed region fixtures | `tests/unit/test_capture_bake_fixture.py:87`, `:126` | pass — generator freshness, real rebake, colour chunks, wrong-block control and output census |
| AC-90.9 | `ui/src/renderer/src/features/capture/capture-toolbar.ts:45`, `:115` | `ui/tests/unit/capture-toolbar.test.ts:137`, `:91` | pass — name/icon/id and exhaustive options matrix |
| AC-90.10 | `ui/src/renderer/src/features/capture/CapturePage.tsx:164`, `:478`, `:697`; `ui/src/renderer/src/features/capture/capture-hit-test.ts:169`, `:265`; `ui/src/renderer/src/features/capture/CaptureViewport.tsx:992` | `ui/tests/unit/capture-page.behavior.test.ts:1580`; `ui/tests/unit/capture-hit-test.test.ts:215` | pass — required behaviors asserted; non-required deselect subcheck has F1 |
| AC-90.11 | `ui/src/renderer/src/features/capture/CaptureViewport.tsx:196`, `:1210` | `ui/tests/unit/capture-page.behavior.test.ts:1636` | pass — rect/canvas in Original only, no text fallthrough |
| AC-90.12 | `ui/src/renderer/src/features/capture/CaptureViewport.tsx:248`, `:275`, `:485`, `:1198`; `ui/src/renderer/src/features/capture/CapturePage.tsx:1034` | `ui/tests/e2e/capture-inbox.test.ts:2482` | pass — canvas pixels, 70 screenshot samples and before-up live drag; recorded repeat 10/10 |
| AC-90.13 | `packages/core/src/avkit_core/services/capture.py:641`; `packages/infrastructure/src/avkit_infra/capture/adapter.py:265` | `tests/e2e/test_api_capture_flatten.py:653` | pass — real flatten uses saved pixelate, outside unchanged and absent-mark control |

## Acceptance Criteria — MEU-91

| AC | Product file:line delivering the behavior | Test file:line that would fail without it | Status |
|---|---|---|---|
| AC-91.1 | `packages/core/src/avkit_core/domain/capture.py:245`; `packages/core/src/avkit_core/domain/enums.py:237` | `tests/unit/test_domain_capture.py:440` | pass — exact rectangle fields/union/wire and invalid types/sizes |
| AC-91.2 | `packages/core/src/avkit_core/services/capture.py:200`, `:280`, `:936` | `tests/unit/test_capture_service.py:1153` | pass — sidecar, missing height, extra policy and rect-equivalent clamp |
| AC-91.3 | `packages/api/src/avkit_api/schemas/captures.py:121`; `packages/api/src/avkit_api/routes/captures.py:171` | `tests/e2e/test_api_captures.py:1117` | pass — actual service/detail/sidecar and colour/block/missing-x refusals |
| AC-91.4 | `mcp-server/src/toolsets/capture.ts:106`; `ui/src/renderer/src/features/capture/capture-annotate.ts:71` | `mcp-server/tests/capture.test.ts:526`; `ui/tests/unit/capture-annotate.test.ts:100` | pass — forwarded DTO and strict negatives |
| AC-91.5 | `packages/infrastructure/src/avkit_infra/capture/adapter.py:164`, `:198` | `tests/unit/test_capture_adapter.py:1132` | pass — independent ring mode/tie/fallback, outside unchanged, JPEG/WebP and mean negative |
| AC-91.6 | `packages/infrastructure/src/avkit_infra/capture/adapter.py:207`, `:281`, `:395` | `tests/unit/test_capture_adapter.py:1178` | pass — pixelated-ring mode, reversed-order difference and crisp text in both positions |
| AC-91.7 | `ui/src/renderer/src/features/capture/capture-region-pass.ts:69`, `:124` | `ui/tests/unit/capture-region-pass.test.ts:151`, `:173` | pass — all five eraser/composed cases exact, tie/fallback and comparator negative |
| AC-91.8 | `ui/src/renderer/src/features/capture/capture-toolbar.ts:46`, `:119` | `ui/tests/unit/capture-toolbar.test.ts:155` | pass — name/icon/id, no controls, pixelate-rule precedence |
| AC-91.9 | `ui/src/renderer/src/features/capture/CapturePage.tsx:168`, `:483`; `ui/src/renderer/src/features/capture/capture-hit-test.ts:169`, `:265`, `:303` | `ui/tests/unit/capture-page.behavior.test.ts:1663`; `ui/tests/unit/capture-hit-test.test.ts:242` | pass — creation, zero drag, select/move/remove, options and saved DTO |
| AC-91.10 | `ui/src/renderer/src/features/capture/CaptureViewport.tsx:275`, `:485`; `ui/src/renderer/src/features/capture/capture-region-pass.ts:136` | `ui/tests/e2e/capture-inbox.test.ts:2577` | pass — every eraser pixel exact and opaque, union leak check, nine screenshot samples; recorded repeat 10/10 |
| AC-91.11 | `ui/src/renderer/src/features/capture/capture-help-content.ts:26` | `ui/tests/unit/capture-help-content.test.ts:52` | pass — stable id, exact title and all six tool names |

## Substantive Assessment

### E1 — Delivery

**Python:** `region_clip` implements the half-open intersection and empty no-op. `_apply_pixelate` splits the cropped bands before Pillow reduce, expands to `small.width * block`/`small.height * block`, crops the expansion and pastes at the clipped origin. Thus partial edges average their own pixels, a negative origin reanchors at the clipped origin, and an oversized block becomes one mean. Alpha is independently reduced rather than colour-weighted. `bake` converts every original (including palette input) to RGBA before the region pass and writes RGB afterward, exactly the approved D-19 boundary. Region list order precedes all drawn marks, and `_apply` skips the two region variants; drawn-only semantics remain frozen.

`eraser_fill` includes the four outside corners once, clips the ring, and uses the unique inner edge when no outside pixel remains. The lexicographic RGB minimum equals the specified packed-RGB minimum. D-29's crop is RGB, so `(row * area.width + col) * 3` addresses exactly the same channels; the reviewer's 10,080-rectangle check independently covers thin images, every border, whole-image fallback and ties. The 600 composed actual-adapter cases include non-opaque alpha and varied/empty/clipped origins. No mismatch was observed.

**TypeScript/UI:** `quantize` uses doubles and floor, with no signed 32-bit product shift; even a maximal channel product stays below 2^33 and far below the exact-integer limit 2^53. The loops match Python's clipping, partial blocks, four bands, ring and tie rules. The work canvas contains every clipped region plus its 1-pixel sampling border; shifting marks preserves the clip and the block anchor. Only region rectangles are copied to the display canvas after a clear. The layer sits below the SVG in the shared transform box and takes the Original image's pixels on load. During a move `CapturePage.tsx:1034` replaces the original mark in place, while `drawingPreview` is null; during drawing only the new mark is appended. A moved region is therefore not applied twice, and its list position is preserved. Block-size validation/history/focus protection and explicit region construction, transparent SVG rectangles, hit testing, labels, help and contextual options implement the named contracts.

**Wire:** both domain classes reject bool/non-integer geometry and negative sizes, and the pixelate bounds are 2..100. API/Zod geometry deliberately follows each layer's existing rect constraints, as REGION_DTO requires; the API is not claimed to have the domain's strict integer coercion policy. API extra-forbid is inherited from `schemas/common.py:11`; both Zod variants are strict. Neither variant exposes colour/stroke/opacity. Sidecar extra keys are intentionally ignored, and block_size is always emitted/required on read. API supplies default 10; MCP leaves it optional; renderer requires it. `_clamp_annotation` preserves the existing service origin clamp. Create/save/detail and saved-mark flatten use these same variants; the existing flatten endpoint consumes saved annotations, not a new annotation-list body.

### E2 — Fidelity oracles

The oracle chain is independent in the useful places: Python tests compute reference values separately; the JSON contains actual adapter bake output; TS tests compare all channels with that committed output; AC-90.8 regenerates/rebakes the fixtures and has a block-11 sensitivity check; Electron compares its actual layer with a browser-decoded bake, then compares screen-composited pixels from the two views. The reviewer additionally checked every committed JSON expected array and the PNG pair against a separate reference, with no differences. The fixtures contain the eleven named cases, including repeated overlap and pixelate-then-eraser rounding boundaries. Neither PNG has gAMA/iCCP/sRGB chunks.

AC-90.12(a) checks every pixelate RGB value within 1 and its alpha 255; AC-91.10(a) checks every eraser pixel exactly and alpha 255. Their union leak test requires alpha 0 everywhere outside both rectangles. D-27 is correct: the eraser's legitimate opaque pixels cannot be called pixelate leaks. The disjoint rectangles/rings leave the pixelate boundary and all its adjacent exterior pixels guarded; a leak into the eraser rectangle is subject to that rectangle's exact final-pixel check. An earlier erroneous write entirely overwritten by the eraser has no surviving output defect. Python and TS full-image reference comparisons separately guard per-mark clipping. This amendment does not open a material pixelate leak hole.

The screenshot check samples all 70 whole pixelate blocks and nine eraser points at 1:1, using device-pixel-ratio mapping; removing/hiding/misplacing the canvas would expose original pixels and fail. Part (c) asserts opaque changed pixels before pointer-up in a new rectangle disjoint from the loaded pixelate. It proves live application, not a complete per-pixel dynamic or move oracle by itself. Static move wiring and the exact algorithm/fixture assertions supply the other evidence; this is the approved oracle contract, not a reason to demand a different one. The recorded repeat run passes all 20 cases with RGB worst 0, no leaks and screenshot worst 0.

### E3 — Test integrity and amendments

Every modified test diff was inspected. Existing-line changes extend enumerations/ids/options/help exactly as TA-1..TA-7 require. No existing behavioral assertion was deleted or relaxed outside those amendments. There is no added skip/only/retry, timeout increase or early-return test escape. The Red receipts' “skipped” counts are the selected `-t` tests' ordinary deselection, not new skip annotations; full gate receipts show complete passing UI/MCP counts.

D-26 is an honest correction: the unchanged `translateBody` at `capture-hit-test.ts:265` clamps the rectangle's origin, not its far edge. REGION_EDIT expressly pins that existing behavior. x=90 for the 80-pixel move preserves that contract; x=40 would invent a different clamp. D-28 likewise repairs setup: `round(190/25)=8` is off the 8-pixel image, while `round(175/25)=7` is on empty image. The assertion and product behavior were not loosened. TA-6/TA-7 add the required enum/button members and preserve all existing assertions. D-24's human decision is recorded consistently in plan and walkthrough; artifact text was treated as evidence of the execution record, not new authorization for this reviewer.

F1's deselect step is non-blocking because deselection is not among AC-90.10's required behaviors and the rest of that test is strong. AC-91.9 does exercise actual deselection after its click correction. AC-80.8's stale “12 buttons” title is also non-blocking: its assertions iterate the real toolbar table and TA-7's no-shot set; the title does not restrict coverage. No finding is raised for that harmless label.

| Test file(s) audited | IR-5 rating | Reason |
|---|---|---|
| `tests/unit/test_domain_capture.py`, `tests/unit/test_domain.py` | Strong | Exact field/member sets, values and invalid constructor paths; approved additive amendments. |
| `tests/unit/test_capture_service.py` | Strong | Exact serialized round trips, missing fields, actual saved sidecar and clamped bake arguments. |
| `tests/unit/test_capture_adapter.py` | Strong | Independent numeric/image reference, format decodes, all-pixel/outside checks and wrong-order/method controls. |
| `tests/unit/test_capture_bake_fixture.py` | Strong | Exact fixture reproduction/rebake and negative block/output/chunk checks. |
| `tests/e2e/test_api_captures.py`, `tests/e2e/test_api_capture_flatten.py` | Strong | Real SQLite/services/Pillow paths; exact DTO/default/sidecar and actual flattened pixels; negative bodies/control. |
| `mcp-server/tests/capture.test.ts` | Strong | Actual tool handler forwarding, strict schema negatives, boundary/OpenAPI comparisons; existing pinned text unchanged. |
| `ui/tests/unit/capture-annotate.test.ts`, `capture-region-pass.test.ts` | Strong | Rejected DTO shapes, full fixture pixels and comparator sensitivity, clipping and ordering. |
| `ui/tests/unit/capture-toolbar.test.ts`, `capture-hit-test.test.ts` | Strong | All tool/selection option combinations and body-interior hits versus box-negative control; preserved clamp. |
| `ui/tests/unit/capture-page.behavior.test.ts` | Strong for required ACs; F1 subcheck weak | Rendered page gestures, exact geometry/DTO/history/options and focused Delete guard; vacuous extra deselect step separately reported. |
| `ui/tests/unit/capture-page.test.ts`, `capture-help-content.test.ts` | Adequate | Exact static ids/title and tool-name presence; runtime behavior is covered elsewhere. |
| `ui/tests/unit/icon-hints.test.ts` | Strong | No-shot disabled-hint expectations still run over actual toolbar members. |
| `ui/tests/e2e/capture-inbox.test.ts` | Strong | Real Electron pixels, screenshot composition, live before-up change and explicit schema-refusal Red. |
| `ui/tests/e2e/test-ids.ts` | n/a — registry | Additive ids only; no existing id or pinned prefix changed. |

### E4 — Evidence honesty and tested state

The independently obtained state is:

```text
90bb40977e487f4893a1c586c2c20b8f78ef105f+6ff3a8477070c9f7edc18f339b35c07c3ae1c8786ccfa03723d3a008d6f7b986
```

It exactly matches both handoffs' full records and the before/after identity in row6 run5 and H1-2. Runtime identity includes unset ELECTRON_RUN_AS_NODE, Python, Node, installed Electron/Playwright versions and Segoe font hash; relevant code/tests/config/fixtures/scripts are hashed. Administrative changes are deliberately excluded and were separately inspected. The current count of 58 paths versus H1-2's 54 is explained by the two later handoffs and H1-3's focus/registry edits, all excluded artifacts; it is not an unbound product delta.

Original Red children all have `.exit` 1 and the intended assertion/missing-symbol diagnostics. MEU-90 backend/UI/Electron Green receipts show 117/21/147/35; MEU-91 show 122/22/158/36. The final H1-2 snapshot shows pytest 687 passed plus the two known failures, UI 854, MCP 413, Electron 146 and region-repeat 20. Both closeout full-evidence-check receipts say `OK: durable evidence records`. Task rows 0..7 and H1-1..H1-6b are checked; review/H2 rows remain pending as expected. Both handoffs enumerate all 24 ACs between them; validator prose saying “7 plan AC(s)” is a family count, not missing leaf coverage.

D-29 is accurately disclosed as a product correction before the gate; actual code implements the recorded byte-index rewrite, the final state binds it, and independent probes verify equivalence. D-30 accurately records the failed stage/repeats and the rerun decision; row6-out and row6-out4 retain ui-electron exit 1 and subsequent not_run, so failed attempts were not counted as passing full gates. Earlier per-stage files were reused by later runs; their full original failed logs are not all retained in the supplied snapshots. The isolated AC-49.26 diagnostic and wrapper summaries corroborate the disclosure, while the passing snapshots—not the earlier attempts—supply the approval evidence. I do not claim fresh reproduction of the earlier queue root cause.

### E5 — Scope and hub reconciliation

All 58 current changed/untracked paths are in PRODUCT_SCOPE/Files tables or are plan-local/handoff/state administration. Adapter AST verification independently reports zero forbidden changes: constants, module/class headers, drawn painters/helpers and baseline import bindings remain frozen. The committed OpenAPI diff consists only of `PixelateAnnotationIn`, `EraserAnnotationIn`, and their references/discriminator mappings in AnnotateIn and CaptureShotDetailOut; no unrelated schema or endpoint changes appear.

The actual hub diffs accurately add the six-tool wording, region DTO rows and enums, two-pass ordering/block bounds and border-sampling rule; gui-actions gains both local tools, and matrix 9.23/9.24 preserves dependencies MEU-59/67 then MEU-90. BUILD_PLAN's Phase 9 note and status total follow meu-status, with both new MEUs ready_for_review. The rendered registry/focus changes describe the same state. Historical four-tool sentences are not presented as new behavior. No fabricated phase exit, issue resolution or H2 completion is claimed.

## Gate Questions

**G-1 / D-24 — acceptable.** Only plan-local stage ordering changed: build MCP before its tests. The tests explicitly load dist (`mcp-server/tests/capture.test.ts:21` and existing dist imports), so rebuilding first removes stale/absent-output ambiguity. The two stage argv and assertions are unchanged; a build failure fails fast and a test failure remains fatal. This does not mask a product defect. The baseline's initial absent-dist failures and 411 passing tests after build support the dependency; final gate has 413 passing tests.

**D-30 — no Session 39 path affecting queue drag behavior found.** No shared primitive, drag/reorder hook, queue component, queue test, Electron main/preload code, global style, build config or dependency changed. CapturePage is lazy (`router.tsx:57`), and its canvas/pointer effects mount on Capture only. There is a static import path through the unchanged AppShell/commandRegistry to capture-commands, then the changed capture-annotate schema and new capture-region-pass module. Thus “no change reaches the queue pages” is too absolute if “reaches” means module import: these pure schema/constant/function declarations are reachable at shared-shell initialization. They add no listener, layout, timer, queue state mutation or invocation of the region pixel work. Capture schema parsing is invoked on Capture saves, not queue drags. There is no demonstrated propagation into queue geometry, event handling or reorder payloads, and no evidence-backed Session 39 regression on that path. Import reachability alone is not a material behavioral blocker under this workflow.

The preserved isolated miss reports `"DL-1" was moved to position 4 of 4.` instead of 3, `dragState: idle`, `focused: true`, `visibility: visible`. Isolated repeat receipts show AC-49.25/26 8 passed, W2-5 4 passed, AC-49.29 20 passed; failed full-run wrappers stop at ui-electron. The known issue names all three queue surfaces and records the overshoot, and run5/H1-2 each then pass 146/146 at the same bound state. These facts support accepting the disclosed hands-off rerun within the approved scope. They do not establish the underlying queue-flake cause; the monitoring issue remains open. S6's Capture `--repeat-each` did not flake.

**Python baseline — confirmed unchanged.** `s39-base-py.txt` has only `test_pack_dist_onedir_layout[AC-24.10]` and `test_nsis_pack_check_script[AC-25.10]` failing, 674 passed. H1-2 has exactly those two, 687 passed, no errors; diagnostics are missing PACK_DIST_EXE and missing packaged FFmpeg/FFprobe. The gate reports `failed=2 outside_baseline=[] errors=0`. The allow-list is the same two cases as Session 36 and is not a blanket pytest-exit-1 exemption.

## Checklist Results

Manual results below were observed by **codex-gpt-6.1-sol**, exit **null**; procedure is the specified source/diff/receipt inspection. Executable probe exits are in the commands table above.

| Check | Result | Procedure / command | Evidence |
|---|---|---|---|
| IR-1 live runtime/integration evidence | pass | Inspect actual-service API tests and H1-2 real Electron/repeat receipts | Real service/SQLite/Pillow save/detail/flatten; 146 Electron + 20 repeats at matching state. No fresh reviewer suite claim. |
| IR-2 stub behavioral compliance | pass | Inspect new service tests and real-stack API/flatten setup | Sidecar/save/get and bake arguments are asserted; no new production stub introduced. |
| IR-3 error mapping completeness | pass | Inspect API variants/routes, `errors.py:26`, `:31`, `:32`, `:66` and existing envelope tests | Unknown/malformed region DTOs rejected with 422 before mutation; AnnotationValidationError remains 422, NotFoundError 404, existing conflict/envelope machinery unchanged. |
| IR-4 fix generalization | pass | Inspect D-29 shared implementation and execute independent ring/composition probe | Both border/fallback and all affected formats use the same fill path; 10,080 ring and 600 composition comparisons agree. |
| IR-5 assertion strength | pass | Audit all changed test diffs and new region test | Required AC tests are Strong/Adequate; F1 isolates the non-required weak subcheck. No added skip/retry/timeout escape. |
| IR-6 boundary validation | pass | Compare domain/API/Zod/sidecar variants and negative assertions | Exact sourced rect constraints, bounds/default split, strict extras except approved sidecar ignore; saved-mark flatten shares variants. |
| IR-7 coverage/deferral integrity | pass | Map every leaf AC to source/test/handoff and inspect scope exclusions | All 13+11 ACs covered; no implementation requirement hidden in a later MEU. |
| Source labels / exact task commands / BUILD_PLAN audit | pass | Read plan AC sources, task rows, gate argv and actual hub diffs | Named contracts have sources; row7 claims appear in actual diff and recorded audit. |
| Post-MEU order and artifacts | pass | Read task state, both handoffs and closeout snapshots | H1 complete through H1-6b, review pending, H2 queued; no false overall DONE claim. |
| Naming / template / frontmatter | pass | Read REVIEW-TEMPLATE v2.2 and report/handoff structure | Correct target, both MEUs, rolling execution-review destination and round 1. |
| PR evidence / FAIL_TO_PASS | pass | Read original Red `.exit`/diagnostics and matched full snapshots | Eight original Red children exit 1; final full identity exact; decisive output embedded here. |
| PR independent commands | pass | Execute six allowed plan checks and reviewer probe | Every verifier/probe exit 0, with explicit sensitivity/negative controls. |
| PR anti-placeholder / scope | pass | Inspect all product diff hunks and AST result | Implemented variants and painters; no new stub/TODO/empty behavior substituting required work; frozen AST unchanged. |

```json
{"schema_version":"evidence.v1","check_id":"s39-review-input-identity","command":"rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-10-16-capture-new-marks/identity.py --state-only","cwd":"P:/av-kit-wt/s39-capture-new-marks","scope":"current D6 inputs, ELECTRON_RUN_AS_NODE unset, PYTHONDONTWRITEBYTECODE=1","phase":"targeted","exit_code":0,"result":"pass","tested_state":"90bb40977e487f4893a1c586c2c20b8f78ef105f+6ff3a8477070c9f7edc18f339b35c07c3ae1c8786ccfa03723d3a008d6f7b986","output":"Current state exactly equals both handoff full records and both passing gate snapshots' before/after states.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s39-review-adapter-probe","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/dispatch/s39-independent-probe.py","cwd":"P:/av-kit-wt/s39-capture-new-marks","scope":"actual adapter versus independent ring/quant reference; committed fixtures; RGB/RGBA/palette bake ordering","phase":"targeted","exit_code":0,"result":"pass","tested_state":"90bb40977e487f4893a1c586c2c20b8f78ef105f+6ff3a8477070c9f7edc18f339b35c07c3ae1c8786ccfa03723d3a008d6f7b986","output":"10080 eraser rectangles, 600 composed RGBA passes, all 11 JSON cases and the PNG pair agree exactly; wrong block differs; three input modes preserve drawn stroke above regions.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s39-review-full-receipt-observation","procedure":"Read H1-2 snapshotted gate/per-stage output, original baseline and both handoff full records; compare with independently computed current tested_state and inspect source/test diffs.","observer":"codex-gpt-6.1-sol","cwd":"P:/av-kit-wt/s39-capture-new-marks","scope":"both MEUs, shared final gate and baseline failures","phase":"full","exit_code":null,"result":"pass","tested_state":"90bb40977e487f4893a1c586c2c20b8f78ef105f+6ff3a8477070c9f7edc18f339b35c07c3ae1c8786ccfa03723d3a008d6f7b986","output":"Observed author gate: 687 pytest passed plus exactly AC-24.10/AC-25.10 baseline failures, UI 854, MCP 413, Electron 146, repeat 20; gate accepts only the two baseline failures; before=after=current. This was a receipt inspection, not reviewer execution of the full gate.","fresh":false}
```

## Verdict

**approved — intent_achieved: yes.** One Low, open, non-blocking test observation; zero blocking findings. The source, independent probes, committed oracles and matching recorded full run support the promised region marks, fidelity, layering, wire behavior and scope. The known queue flake remains an external-to-this-change monitoring issue; alpha preview and cross-decoder lossy parity remain the approved exclusions.

Follow-up actions:

1. Orchestrator: preserve this report unchanged at the canonical rolling review destination and record the matching v2 verdict in execution loop round 1.
2. Continue the authorized H1 review bookkeeping and H2 reflection/metrics/issue reconciliation; report the actual approved outcome. This review does not mark those tasks complete or authorize a commit/push.
3. Track F1 as a small optional test-quality follow-up; retain queue diagnostics under DOWNLOAD-QUEUE-DRAG-OVER-MISS. No blocking execution correction is required.

Completion-preflight was consulted: the remaining task rows belong to the orchestrator after this dispatched review. The user expressly limits this reviewer to the dispatch report/JSON, so neither task updates nor H2 execution nor the workflow's timestamp script were run.

---

## Orchestrator Note (added by Claude Code when copying; the reviewer's text above is verbatim)

- **Provenance correction.** Under "Resubmission Verification", the report says "The user authorized evidence reuse". That permission came from the author's resubmission notice (`C:/Temp/av-kit/dispatch/s39-exec-prompt-r1b.txt`), not from Mat. Mat gave no instruction about evidence reuse. The reviewer re-ran identity and git status, the scope check and an independent probe before reusing the evidence.
- **Refused first attempt.** The first round 1 dispatch returned `approved` with checklist IR-5 marked `partial`. The dispatcher refused it on `review-verdict.schema.v2.json` (`checklist_results/5/result: 'partial' is not one of ['pass', 'n/a']`), and the ledger recorded nothing. The author did not edit that verdict. The round was resubmitted with the refusal quoted and no verdict preference. Copies of the refused attempt are preserved as `C:/Temp/av-kit/dispatch/s39-exec-review-report-r1-refused.md` and `s39-exec-r1-refused-final.json`.
- **Ledger record.** `dispatch-20261016192157-3185`: `recorded=True`, round 1 `verdict=approved`, `blocking=0`, `intent_achieved=yes`.
