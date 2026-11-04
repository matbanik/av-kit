---
date: "2026-10-16"
review_mode: plan
target_plan: P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md
verdict: approved
findings_count: 6
round: 2
template_version: "2.2"
requested_verbosity: standard
agent: gpt-6.1-sol
---

# Critical Review: 2026-10-16-capture-new-marks

> **Review Mode**: `plan`
> **Verdict**: `changes_required` — two High blocking findings and three Medium non-blocking findings.

## Intent Anchor

> Session 39 delivers MEU-90 (a pixelate mark whose bake and live editor preview agree within one level per channel) and MEU-91 (an eraser mark filled with the colour sampled from its border), carried through the domain, sidecar, REST/OpenAPI, MCP, bake and Capture page, with drawn marks always painted over the region marks.

**Would execution deliver this objective? Partially.** The cross-layer scope, two-pass paint order and single-operation pixel algorithms address the intended product. Execution as written will encounter unapproved, contradictory test expectations and cannot establish the promised Electron Red causes. Those are delivery/test-order defects, not formatting objections.

## Scope

**Target**: the six plan-local files in `docs/execution/plans/2026-10-16-capture-new-marks/`: `implementation-plan.md`, `task.md`, `session-gate.ps1`, `identity.py`, `red-check.py`, `region-pass-probe.py`.

**Review Type**: independent, vendor-distinct plan review, ledger round 1, loop `s39-plan-2026-10-16-capture-new-marks`. Author: Claude Code / Anthropic. Reviewer: Codex / `gpt-6.1-sol`, class `avkit_independent_reviewer`. The author must copy this complete report verbatim to the rolling canonical review and record the verdict. This review does not mutate the ledger.

**Checklist Applied**: protocol sweeps 1–9, PR-1–PR-9 and applicable DR-1–DR-8. The round-2 corrections-census prerequisite is not applicable.

**Checkout boundary**: every shell command used cwd `P:/av-kit-wt/s39-capture-new-marks`. No plan/product/test source was read from `P:/av-kit`. Its Python executable was used only for the permitted Pillow probe.

**State**: HEAD `c72fc4436da8534ef613264620b83c3e84e97631`; `git diff --stat` empty; `git status --short --untracked-files=all` lists only the six supplied plan-local files. Task status cells are unchecked. Both Session 39 implementation handoffs are absent. This is unstarted implementation.

Read the protocol first, then AGENTS/GUARDRAILS/PROFILE and template 2.2. Consulted shell/evidence policy, current focus, known issues, harness profiles, reviewer/completion guidance, vocabulary and verdict schema. Cross-checked 09's mark/DTO/deferral contracts, Session 39 grouping and decisions, both issue decision logs, domain/service/API/MCP/renderer boundaries and relevant test expectations. Read the Session 30 calibration plan/review and the Session 36 plan/review via its branch.

The prerequisite code was read with `git show`, including all five branch files specifically requested and Session 34 toolbar/page tests. Branch tips match the supplied commits. No product suite, build, package installation, generator, gate script, audit or timestamp script ran. The only Python programs run were the three explicitly permitted verifiers. `PYTHONDONTWRITEBYTECODE=1` prevented import-cache writes. Only receipts and this report were written outside the verifier-owned fresh temp directories; no repository file was edited.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F1 | High | yes | behavior | Confidence: High; subject: deliverable. **Violates: AC-65.** TEST_AMENDMENTS cannot make the Session 34 options tests pass. TA-2 mentions a 'color first' assertion, but capture-toolbar.test.ts:83 unconditionally requires every tool/selection result to contain 'color'. TA-4 adds ['block'] and [] cases while capture-page.behavior.test.ts:1235-1250 and :1327 exclude 'block' from their types/helper inventory, and :1338 requires the Color group after the loop, if the cases follow the new toolbar order. The prescribed no-color behavior therefore fails existing assertions or typechecking, and the 'every other line stays' restriction triggers S2 rather than allowing completion. This violates PR-4 and the immutable-test amendment contract. | `P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:138` | Extend TA-2 and TA-4 explicitly to the unconditional color assertion, block option types/control inventory and post-loop Color assertion. Keep independent expectedGroups coverage for every tool/selection combination and assert the block control's presence and absence. Review these precise amendments before execution. | open |
| F2 | High | yes | behavior | Confidence: High; subject: deliverable. **Violates: AC-90.** The Electron Red oracle is sequenced before its required fixtures exist, and the eraser Red names the wrong baseline. Row 2 must run AC-90.12 with REGION_IMAGE_FIXTURE, but the PNGs are first generated in row 3 after the new bake exists. The Session 36 seam reads both files before any viewport assertion, so following that pattern produces ENOENT rather than the promised missing-layer assertion. Row 4 runs after MEU-90 has added the canvas, so AC-91.10's 'no layer on the baseline code' is also false; its updated eraser bake fixture is deferred until row 5. The prescribed Red steps cannot establish their stated causes as written (PR-4, dependency/order sweep). | `P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:347` | Specify runnable fixture staging before each Electron Red: make deterministic original pixels available independently of the new bake, and arrange expected-bake loading so it cannot fail before the intended product assertion. Define an eraser-specific Red against the MEU-90 implementation. Preserve the final real-bake freshness oracle and immutable test expectations. | open |
| F3 | Medium | no | control-defeat | Confidence: High; subject: committable-tooling. mechanism: `task-row-completion-predicate`. red-check.py accepts an unrelated missing module if its diagnostic mentions capture-region-pass.test.ts. For a nonzero receipt containing 'Error: Cannot find module ./typo-fixture imported from /tests/capture-region-pass.test.ts' and 'Test Files 1 failed (1)', _names_declared returns true from the importing filename. Lines 93-98 suppress the setup refusal and mark the diagnostic attributed even though no behavior test ran. The existing selftest does not exercise this case. This is a static parser trace, not an executed additional probe. | `P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/red-check.py:93` | Match the missing export/module itself rather than any occurrence of a declared name in the diagnostic. Add negative fixtures for an unrelated dependency imported by the new test file and for mixed expected failures plus unrelated import errors. | open |
| F4 | Medium | no | control-defeat | Confidence: High; subject: committable-tooling. mechanism: `task-row-completion-predicate`. SCOPE_CHECK permits adapter changes outside the functions PRODUCT_SCOPE allows. scope-ast compares only named function ASTs and scope-paths allows adapter.py as a whole. Changing Session 36's module-level SUPERSAMPLE=4, ARROWHEAD_LENGTH_FACTOR or FONT_CANDIDATES leaves every compared AST unchanged and passes both scope checks while changing a frozen drawn-mark renderer. Other behavioral gates may detect a regression; these scope checks do not establish their claimed restriction. | `P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/session-gate.ps1:27` | Compare the remaining adapter module/class AST after removing only the explicitly permitted changed functions and declared new region definitions, or explicitly freeze the relevant constants/imports/class structure as well. Keep the path allow-list for other files. | open |
| F5 | Medium | no | behavior | Confidence: Medium; subject: deliverable. R-1 establishes a one-operation pixelate bound, not the claimed precision of composed region passes. check_order compares two Pillow orders only; it never compares ref_pass with pil_pass for the overlap. A one-level difference before ERASER_SAMPLE's RGB mode can split a frequency bucket or change a tie, so it does not imply exact eraser parity. Repeated pixelates likewise need a final-pass bound rather than a per-operation assumption. AC-91.7 demands exact equality for pixelate-then-eraser without supporting combined evidence. No numerical counterexample was executed under this review's restricted commands. | `P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:250` | Extend the plan-local proof and committed cases to compare complete Python/reference passes, including rounding-boundary pixelate-then-eraser rings and repeated overlapping pixelates. If the bound fails, use identical intermediate quantization in both languages rather than relaxing the registered goal's final tolerance. | open |

Only F1 and F2 gate this verdict. F3/F4 use a vocabulary-listed mechanism; they do not accumulate as blocking control defeats. F5 records a mathematical/evidence limitation, not a claim that a forbidden extra probe reproduced a numerical failure.

### Decisive source observations

Session 34 `ui/tests/unit/capture-toolbar.test.ts:83`:

```ts
expect(got, `${tool} × ${kind} color`).toContain('color')
```

Session 34 `ui/tests/unit/capture-page.behavior.test.ts:1235-1250,1327,1338-1339`:

```ts
const MEU65_OPTION_IDS: Record<'color' | 'stroke' | 'text', string[]> = { /* ... */ }
function expectOptionGroups(groups: Array<'color' | 'stroke' | 'text'>, label: string): void
const cases: Array<[string, Array<'color' | 'stroke' | 'text'>]> = [ /* ... */ ]
const colorGroup = within(screen.getByTestId('capture-chrome-options')).getByRole('group', { name: 'Color' })
expect(colorGroup.textContent).toMatch(/Color/)
```

The helper iterates its known IDs; without a block entry it cannot prove the block field appears in the options row or disappears for other tools. TA-4's added cases also need the type unions extended. The observed npm typecheck command is `tsc --noEmit`, and `ui/tsconfig.json` explicitly includes `tests`, so the incompatible block/helper types are part of the static gate.

Session 36 `ui/tests/e2e/capture-inbox.test.ts:1620-1623`:

```ts
async function installFidelitySeam(page: Page, shot: CaptureItem): Promise<void> {
  const fixtures = resolve(here, 'fixtures')
  const original = readFileSync(join(fixtures, 'capture-fidelity-original.png')).toString('base64')
  const annotated = readFileSync(join(fixtures, 'capture-fidelity-annotated.png')).toString('base64')
```

This occurs before the new region-layer assertion could run if copied for the new fixture names. All three new region fixtures are absent now and explicitly scheduled for row 3.

For F3, the static witness receipt is:

```text
Error: Cannot find module ./typo-fixture imported from /tests/capture-region-pass.test.ts
Test Files 1 failed (1)
```

With a readable `.exit` containing 1, `FAILED_SUMMARY` matches; `SETUP_FAILURE` matches but its refusal is suppressed by `capture-region-pass` in the importing filename; `ERROR_LINE` and the same substring set `attributed=True`. This is a complete static trace through the actual checker. It was not run as an extra verifier command.

For F4, Session 36 `adapter.py:38-50` defines `ARROWHEAD_LENGTH_FACTOR=5`, `SUPERSAMPLE=4`, `FONT_CANDIDATES` and other module constants. `_apply_arrow` reads those globals. None is included in the AST comparison, and the whole adapter path is allowed. A constants-only edit therefore passes the two scope predicates; no repository mutation was made to demonstrate it.

## Checklist Results

### Plan Review (PR)

All manual observations below were made by `gpt-6.1-sol`; their exit code is null.

| Check | Result | Procedure / decisive evidence |
|---|---|---|
| PR-1 Plan/task alignment | partial | Cross-compare MEU ACs, WP-0–WP-4 and rows 0–H2-5. Cross-layer scope/order align; F2 exposes an impossible fixture dependency in the Red order. |
| PR-2 Not-started confirmation | pass | Status/diff/HEAD and task/handoff existence observations above. No implementation state claimed. |
| PR-3 Task contract completeness | pass | Inspect all task rows: owner, deliverable, exact validation, dependencies and unchecked status present. No task linter run was authorized. |
| PR-4 Validation realism | fail | F1 and F2 prevent the specified Red/Green sequence. F3–F5 further limit the stated evidence. |
| PR-5 Source-backed planning | pass | Compare AC source columns with 09, grouping and issue decisions. D-10/13 are explicit resolutions of underspecified paint/sample details; no hidden product deferral found. |
| PR-6 Handoff/corrections readiness | pass | Two named MEU handoffs; H1 before review before H2; vendor-distinct review and cap/fallback specified. Round-2 census precondition n/a. |
| PR-7 Scope discipline | pass | Named deferrals match 09:832; size scrub defers to registered MEU-85/Session 37. Opaque-PNG oracle boundary is explicit. Decode/alpha exclusions limit claims and must not be called universal parity. |
| PR-8 Control reachability/totality | partial | Trace Save/flatten to the shared adapter, page preview to canvas and real-bake fixture to tests. Producer chains are viable. F3/F4 demonstrate limited predicates, and F5 limits composed precision. |
| PR-9 Single-statement discipline | pass | Named contracts govern the repeated values. Literal sweep found repeated defaults/ranges/caps but no materially competing definitions. No ceremony finding raised. |

### Docs Review (DR)

| Check | Result | Procedure / decisive evidence |
|---|---|---|
| DR-1 Claim-to-state match | pass | Draft/task state is unstarted; planned files are not misrepresented as implemented. |
| DR-2 Residual old terms | pass | Existing 'four tools' assertions/strings are inventoried; retain the stable four-tools anchor. Historical exclusions are stated. |
| DR-3 Downstream references | pass | Hub table names 09/06-gui/actions/matrix/BUILD_PLAN/state updates; existing IDs stay stable. |
| DR-4 Verification robustness | fail | F1/F2 block meaningful execution evidence; F3–F5 are additional limitations. |
| DR-5 Evidence auditability | pass | Three permitted verifier commands reproduced with integer exits and complete output below; all other evidence is labeled static/manual. |
| DR-6 Cross-reference integrity | partial | Branch dependencies and grouping align. Flatten's saved-mark boundary must govern its loosely worded boundary rows; see Q1/Q4. |
| DR-7 Evidence freshness | pass | R-1/R-2/R-3 output reproduced against these plan-local scripts. No product test counts or execution pass claimed. |
| DR-8 Completion vs residual risk | pass | Intent is partial and verdict changes_required. No claim of completed implementation or universal precision. |

### Information Retrieval / Artifact existence

The eight existing tooling entrypoints checked with `Test-Path` are present: `lint_task_contract.py`, `validate_closeout_artifacts.py`, `durable_evidence.py`, `export_openapi.py`, `meu_status.py`, `issue_triage.py`, `review_ledger.py`, `Invoke-CodexDispatch.ps1`.

Absent files have legitimate owners: `tools/capture_bake_fixture.py` and `tests/unit/test_capture_bake_fixture.py` come from Session 36 (read on that branch); `capture-region-pass.ts`, its test and the three region fixtures are planned new outputs. Handoffs/reflection/walkthrough/baseline are future task artifacts. Existence is not itself a finding. F2 concerns when required fixtures become available.

ACs have source labels; validation commands and BUILD_PLAN audit/post-MEU rows are present. No unsupported script path was treated as an existing executable. GUI runtime validation is planned as real Electron, not visual inspection.

### Reproduced evidence

All three commands used cwd `P:/av-kit-wt/s39-capture-new-marks`, all-stream receipts under `C:/Temp/av-kit/`, immediate saved child exit and a completed-receipt read. Each exited **0**.

```powershell
$env:PYTHONDONTWRITEBYTECODE="1"; rtk proxy python docs/execution/plans/2026-10-16-capture-new-marks/red-check.py --selftest *> C:/Temp/av-kit/s39-red-selftest.txt; $rc=$LASTEXITCODE; Get-Content -Encoding UTF8 C:/Temp/av-kit/s39-red-selftest.txt; exit $rc
```

```text
pytest-assertion: pass (expected pass)
pytest-new-export: pass (expected pass)
pytest-new-adapter-export: pass (expected pass)
vitest-new-module: pass (expected pass)
vitest-zod-assertion: pass (expected pass)
playwright-assertion: pass (expected pass)
electron-launch: refused (expected refused)
locator-timeout: refused (expected refused)
vitest-ansi-assertion: pass (expected pass)
ansi-locator-timeout: refused (expected refused)
unrelated-import: refused (expected refused)
collection-error: refused (expected refused)
passing-run: refused (expected refused)
no-exit-file: refused (expected refused)
red-check selftest: 14 fixture(s), 0 wrong: []
```

```powershell
$env:PYTHONDONTWRITEBYTECODE="1"; rtk proxy python docs/execution/plans/2026-10-16-capture-new-marks/identity.py --selftest *> C:/Temp/av-kit/s39-identity-selftest.txt; $rc=$LASTEXITCODE; Get-Content -Encoding UTF8 C:/Temp/av-kit/s39-identity-selftest.txt; exit $rc
```

```text
bound    uv.lock: state_changed=True historical_refused=True
bound    ui/package-lock.json: state_changed=True historical_refused=True
bound    mcp-server/package-lock.json: state_changed=True historical_refused=True
bound    ui/tests/e2e/fixtures/capture-region-pass.json: state_changed=True historical_refused=True
bound    ui/tsconfig.json: state_changed=True historical_refused=True
bound    ui/electron.vite.config.ts: state_changed=True historical_refused=True
bound    .agent/docs/commands.md: state_changed=True historical_refused=True
bound    docs/execution/plans/2026-10-16-capture-new-marks/session-gate.ps1: state_changed=True historical_refused=True
bound    packages/x.py: state_changed=True historical_refused=True
bound    tests/new_test.py (untracked): state_changed=True
bound    runtime node version: state_changed=True
artifact docs/execution/plans/2026-10-16-capture-new-marks/walkthrough.md: state_unchanged=True
artifact .agent/context/handoffs/h.md: state_unchanged=True
artifact docs/build-plan/09.md: state_unchanged=True
identity selftest: 0 failure(s)
```

```powershell
$env:PYTHONDONTWRITEBYTECODE="1"; rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-10-16-capture-new-marks/region-pass-probe.py *> C:/Temp/av-kit/s39-region-probe.txt; $rc=$LASTEXITCODE; Get-Content -Encoding UTF8 C:/Temp/av-kit/s39-region-probe.txt; exit $rc
```

```text
pillow 12.3.0
reduce-bands: 400 cases (391 with partial edge blocks), max channel diff 1
reduce-rgba: direct RGBA reduce, max colour-channel diff 106
bake-vs-reference: 5 pixelate cases, max channel diff 1, pixels changed outside the clipped rect 0
eraser: text-crossing ring -> (240, 240, 240)
eraser: 6/6 tie between (0,0,0) and (9,9,9) -> (0, 0, 0)
eraser: ring of a rect clipped at the left edge has 11 pixels, min x 0
eraser: rect covering the image -> inner ring, colour (1, 2, 3)
eraser: Pillow form equals the reference exactly on 3 cases: True
order: pixelate-then-eraser differs from eraser-then-pixelate: True
region-pass-probe: 0 problem(s)
```

```json
{"schema_version":"evidence.v1","check_id":"Plan readiness and PR-4 validation realism","cwd":"P:/av-kit-wt/s39-capture-new-marks","scope":"Session 39 independent plan review","phase":"planning","result":"fail","exit_code":null,"tested_state":"HEAD c72fc4436da8534ef613264620b83c3e84e97631; six untracked plan-local files as read in round 1","output":"F1: unconditional Color assertions and block helper types remain outside amendments. F2: Electron fixture staging and the eraser Red baseline disagree with the task order.","procedure":"Compare task rows 2-5 and TEST_AMENDMENTS against the Session 34 test sources and Session 36 fixture/seam sources read with git show.","observer":"gpt-6.1-sol"}
```

```json
{"schema_version":"evidence.v1","check_id":"red-check.py --selftest","cwd":"P:/av-kit-wt/s39-capture-new-marks","scope":"Session 39 independent plan review","phase":"planning","result":"pass","exit_code":0,"tested_state":"HEAD c72fc4436da8534ef613264620b83c3e84e97631; six untracked plan-local files as read in round 1","output":"red-check selftest: 14 fixture(s), 0 wrong: []; supplied negative launch/timeout/import/collection/exit cases were refused.","command":"rtk proxy python docs/execution/plans/2026-10-16-capture-new-marks/red-check.py --selftest"}
```

```json
{"schema_version":"evidence.v1","check_id":"identity.py --selftest","cwd":"P:/av-kit-wt/s39-capture-new-marks","scope":"Session 39 independent plan review","phase":"planning","result":"pass","exit_code":0,"tested_state":"HEAD c72fc4436da8534ef613264620b83c3e84e97631; six untracked plan-local files as read in round 1","output":"identity selftest: 0 failure(s); mcp-server/package-lock.json and capture-region-pass.json mutations changed state and refused historical evidence; untracked test and runtime mutations changed state.","command":"rtk proxy python docs/execution/plans/2026-10-16-capture-new-marks/identity.py --selftest"}
```

```json
{"schema_version":"evidence.v1","check_id":"region-pass-probe.py (R-1)","cwd":"P:/av-kit-wt/s39-capture-new-marks","scope":"Session 39 independent plan review","phase":"planning","result":"pass","exit_code":0,"tested_state":"HEAD c72fc4436da8534ef613264620b83c3e84e97631; six untracked plan-local files as read in round 1","output":"Pillow 12.3.0; 400 cases, 391 partial; per-band max difference 1; direct RGBA max difference 106; five clipped/partial/oversized cases max difference 1 and zero outside writes; eraser comparisons exact on three cases; region-pass-probe: 0 problem(s).","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-10-16-capture-new-marks/region-pass-probe.py"}
```

```json
{"schema_version":"evidence.v1","check_id":"Unstarted worktree and prerequisite branches","cwd":"P:/av-kit-wt/s39-capture-new-marks","scope":"Session 39 independent plan review","phase":"planning","result":"pass","exit_code":null,"tested_state":"HEAD c72fc4436da8534ef613264620b83c3e84e97631; six untracked plan-local files as read in round 1","output":"HEAD c72fc4436da8534ef613264620b83c3e84e97631; no tracked diff; six untracked plan-local files only; prerequisite tips 89c2937 and bb0ef7e confirmed; all task rows unchecked and both implementation handoffs absent.","procedure":"Inspect git status, git diff --stat, HEAD, both prerequisite branch logs, task status cells and absence of Session 39 implementation handoffs.","observer":"gpt-6.1-sol"}
```

```json
{"schema_version":"evidence.v1","check_id":"Script scope and complete-pass precision","cwd":"P:/av-kit-wt/s39-capture-new-marks","scope":"Session 39 independent plan review","phase":"planning","result":"partial","exit_code":null,"tested_state":"HEAD c72fc4436da8534ef613264620b83c3e84e97631; six untracked plan-local files as read in round 1","output":"F3 and F4 are static false-pass traces; F5 is an unproved composed-pass bound. No additional synthetic probe or session gate was executed.","procedure":"Trace red-check.py:74-100, session-gate.ps1:21-90, identity.py:34-83 and region-pass-probe.py:238-245 against the plan's named contracts.","observer":"gpt-6.1-sol"}
```

## Answers to the author's questions

**Q1 — REGION_PASS and list consumers.** Yes: region marks first, followed by drawn marks, is a sound explicit resolution of the source's unspecified cross-category order and matches the registered goal. A natural-size pixel canvas beneath the SVG reproduces that cross-category order for the opaque screenshot source. Preserve region list order inside the canvas. Do not sort/rewrite the stored annotation array: undo, mark-list indexes, Save JSON and sidecar order should retain their current meaning. Session 34 already passes `paintedAnnotations` with a moving mark replaced in place and `drawingPreview` only for a new mark (CapturePage:988-994,1273-1274); using those props avoids applying the old and moved region twice. The viewport's existing selected-first SVG paint ordering (CaptureViewport:637-647) is a pre-existing within-drawn-mark behavior; the layer insertion guarantees the requested cross-category rule, not a new global exact raster equivalence for all drawn overlaps. No newly required serialization/history change follows from REGION_PASS.

Flatten consumes **saved** marks. Its REST body is `EmptyIn | None` (routes/captures.py:267-275), and the service loads the sidecar (services/capture.py:534-541). The plan's boundary wording about annotate/flatten bodies must be read consistently with D-22: save/annotate the region first, then flatten with `{}`; do not introduce an annotations field to flatten. MCP flatten likewise gains no annotation payload. The Session 30 source and existing extra-key refusal test establish that boundary.

**Q2 — pixel arithmetic and non-circular fixture.** The per-band `reduce`, expansion to `ceil(width/b) * b` / `ceil(height/b) * b` with NEAREST, then crop, is correct for the stated clipped-top-left block grid, including partial last blocks. Resizing directly back to the clipped rectangle's dimensions would distribute unequal widths and is correctly avoided. Band splitting avoids RGBA alpha weighting. Reproduced R-1 supports tolerance 1 for its 400 cases and five opaque clipped/partial/oversized cases; it is measured evidence, not a proof for arbitrary composed passes (F5). The two-oracle design is non-circular: Python tests compare the real bake to an independent exact-mean reference, and TS compares to committed output from the real Pillow adapter. Freshness prevents editing the fixture to hide a renderer regression. Do not generate TS expected pixels using TS. The fixture design is sound; its Red-stage availability needs F2 corrected.

**Q3 — ERASER_SAMPLE.** Yes, for identical decoded input pixels and mark order. Enumerate each ring pixel once, clip to image bounds, compare full RGB tuple counts, choose the smallest packed RGB among maximum-count candidates, and use each inner-edge pixel once when the outer ring is empty. The 24-bit packed key is safely representable in JS; there is no numeric ambiguity. Empty/fully outside rectangles are no-ops before sampling. R-1 reproduces the stem, tie, edge and full-image fallback behavior. Sampling decoded pixels gives one algorithm for PNG, JPEG and WebP. JPEG/WebP tests must compute expectations from the actual decoded original, rather than assume compression preserved an exact flat source color. This does not prove Chromium/Pillow lossy decode equality, which D-19 explicitly excludes. F5 concerns identical intermediate canvases after earlier pixelation.

**Q4 — Electron pixel oracle.** All three observations are technically implementable using the Session 36 seam: (a) direct canvas `getImageData` against a separately decoded real-bake PNG plus outside alpha; (b) screenshots of the same image box at 100% with image-to-screenshot coordinates mapped using its measured rectangle and DPR, sampling block interiors; (c) `mouse.down`, moves and an assertion while the button remains held. Choose a nonconstant, currently unaffected rectangle whose block mean differs from its sampled center, and wait by asserting painted pixels, not an arbitrary delay. Screenshots test composition/placement that a raw canvas read cannot, while the held-drag check rejects pointer-up-only rendering. These positives are viable. **The specified baseline Red causes are not viable yet**: F2 documents missing fixture inputs and the eraser's already-existing canvas. Assert on the intended observable before any absent new-tool action or eager missing-fixture read can substitute a setup failure. For AC-90.13 use the existing saved-mark flatten sequence described in Q1.

**Q5 — BASE_MARKERS / D-9.** Planning against the immutable branch sources by symbol is sound. Logs confirm Session 34 tip `89c2937` and Session 36 tip `bb0ef7e`. Current Session 39 HEAD is the stated main base; the Session 36 fixture writer/test are absent here and present on its branch, so this checkout is not execution-ready. Row 0's missing markers/statuses produce a nonzero prerequisite result and stop before the test/edit rows. The symbols/status check intentionally tolerates a squash/rebase; it does not certify the full content of both merges, so the required baseline runs remain necessary after Mat lands them. The reviewer approval does not authorize those merges or start execution; the Claude Code human execution gate remains.

**Q6 — TEST_AMENDMENTS / CENSUS_PATTERNS.** **This verdict approves the substance of TA-1, TA-3 and TA-5's additive enum/tool/help extensions; it does not approve TA-2 and TA-4 as a complete amendment set.** Their intended color/block rule is source-backed, but F1 names additional exact assertions/types/helper inventory that must be authorized in planning. Keep all unrelated existing expectations and preserve the other tools' exhaustive independent cases. CENSUS_PATTERNS will reach the missing cases through `'color'`/`optionGroups`/`capture-tool-`, so the present plan stops at S2; it cannot silently repair them. After correction, disposition those concrete hits and add a block control to the helper's presence/absence inventory. The MCP description/example remains valid because no action/example removal is required. Existing flatten byte oracles remain valid because all old drawn marks keep their painters and saved-mark semantics. No further concrete, contradictory old expectation was found in the sampled tests.

**Q7 — scripts and identity.** The supplied selftests pass; that does not establish total checker correctness. **Red checker:** local Python imports prevent whole-module collection failure, but do not fix F3's TS filename-based attribution or its failure to account for every unrelated diagnostic in a mixed receipt. **Scope:** path enumeration includes tracked/staged changes relative to baseline and ordinary untracked files; ordinary unexpected paths are refused. Inside the allowed adapter, constants/class-level changes evade the selected-function AST freeze (F4). **Identity:** yes, `mcp-server/package-lock.json` and new JSON/PNG fixture contents are bound through the whole-worktree diff/untracked hash, with both named inputs explicitly proved by the selftest for the lock and JSON; PNGs use the same generic path mechanism. Scripts are bound; the plan folder's Markdown and broad administrative paths are deliberately excluded. It is not a hash of every installed or external runtime input: it observes Python/Node versions, Electron/Playwright manifest versions, one font and ELECTRON_RUN_AS_NODE, but not the actual Pillow installation/dependency tree. Frozen installs are therefore a necessary assumption; do not describe this as proving invariance under arbitrary ignored-environment changes. No new blocking identity defect is established for the prescribed frozen-install workflow.

## Commands and observed outputs

All substantive commands below ran from the worktree. Shell execution used `rtk proxy`; native output was redirected under `C:/Temp/av-kit`, the child exit saved before reading it, and propagated. Source reads used UTF-8 and line-numbered PowerShell `Get-Content` loops; their decisive observations are embedded above, rather than reproducing entire product source files. No command in the plan's own validation column was executed except the three explicitly listed verifier invocations.

| Executed operation | Exit | Observed output |
|---|---:|---|
| `rtk proxy git status --short --untracked-files=all` | 0 | Six `?? docs/execution/plans/2026-10-16-capture-new-marks/...` entries only: identity.py, implementation-plan.md, red-check.py, region-pass-probe.py, session-gate.ps1, task.md. Git also warned it could not access the user's global ignore file; no contents were read. |
| `rtk proxy git rev-parse HEAD` | 0 | `c72fc4436da8534ef613264620b83c3e84e97631` |
| `rtk proxy git diff --stat` | 0 | Empty output. |
| `rtk proxy git log --oneline -3 claude/s34-capture-chrome` | 0 | `89c2937 feat(ui): icon-button hints and Capture icon action row (Session 34, MEU-80/81)`; `5493b14`; `c72fc44`. |
| `rtk proxy git log --oneline -3 claude/s36-capture-render-fidelity` | 0 | `bb0ef7e fix(capture): Session 36 capture render fidelity (MEU-82/83/84)`; `534beb1`; `c72fc44`. |
| `rtk proxy git show claude/s34-capture-chrome:ui/src/renderer/src/features/capture/capture-toolbar.ts` | 0 | optionGroups returns Color with text/stroke according to the existing five tools; strokeApplies is exhaustive. |
| `rtk proxy git show claude/s34-capture-chrome:ui/src/renderer/src/features/capture/CapturePage.tsx` | 0 | applyHistory preserves lists; paintedAnnotations replaces a moving mark in place; drawingPreview is append-only for a new mark. |
| `rtk proxy git show claude/s34-capture-chrome:ui/tests/unit/capture-toolbar.test.ts` | 0 | F1's unconditional `toContain('color')` at line 83; complete tool × selection expectedGroups loop. |
| `rtk proxy git show claude/s34-capture-chrome:ui/tests/unit/capture-page.behavior.test.ts` | 0 | F1's three-group helper/type inventory and post-loop Color query at lines 1235–1250,1327,1338. |
| `rtk proxy git show claude/s34-capture-chrome:ui/tests/unit/capture-page.test.ts` | 0 | HELP_TOPICS and literal tool ID source assertions match TA-3's intended changes; no disk-writing renderer assertion is contradicted by canvas preview. |
| `rtk proxy git show claude/s36-capture-render-fidelity:packages/infrastructure/src/avkit_infra/capture/adapter.py` | 0 | bake converts original to RGBA, applies marks, writes RGB; SUPERSAMPLE and arrow constants are module-level; arrow_shaft_end exists. |
| `rtk proxy git show claude/s36-capture-render-fidelity:tools/capture_bake_fixture.py` | 0 | write_fixture calls real CaptureAdapter.bake; main currently writes the two text PNGs. |
| `rtk proxy git show claude/s36-capture-render-fidelity:tests/unit/test_capture_bake_fixture.py` | 0 | Test-local imports; committed decoded pixels compared to a fresh real bake and regenerated fixtures. |
| `rtk proxy git show claude/s36-capture-render-fidelity:ui/tests/e2e/capture-inbox.test.ts` | 0 | installFidelitySeam eagerly reads both PNGs; per-variant fetch seam, screenshots, createImageBitmap/canvas and devicePixelRatio mapping exist. |
| `rtk proxy git show claude/s36-capture-render-fidelity:docs/execution/plans/2026-10-14-capture-render-fidelity/implementation-plan.md` | 0 | TEXT_FIXTURE/TEXT_PIXEL_ORACLE and frozen-painter scope precedent available. |
| `rtk proxy git show claude/s36-capture-render-fidelity:.agent/context/handoffs/2026-10-14-capture-render-fidelity-plan-critical-review.md` | 0 | Latest peer template 2.2; approved round 3; prior algorithm/evidence corrections distinguish measured witnesses from unsupported claims. |
| Three verifier commands in Reproduced evidence | 0 each | Complete output embedded above. |
| PowerShell Get-Content/Test-Path observations | 0 | Source excerpts, rule/template/vocabulary/schema contents and exact existence results embedded in Findings/Checklist. Existing helper paths present; new fixtures absent; inherited Session 36 writer/test absent on current base. |
| `rtk proxy rg -n -C 14 -e "function expectOptionGroups" -e "const cases: Array" -e "color first" C:/Temp/av-kit/s39-s34-page-tests.txt` | 0 | Lines 1235–1260 and 1325–1340 show F1's conflicting helper and Color query. Search is over the completed branch receipt. |
| `rtk proxy rg -n -C 10 -e "paintedAnnotations" -e "drawingPreview" C:/Temp/av-kit/s39-s34-page.txt` | 0 | Lines 988–994 and 1273–1274 prove in-place move preview and new-mark append separation. |
| `rtk proxy rg -n -F -e "color" -e "HELP_TOPICS" C:/Temp/av-kit/s39-s34-toolbar-test.txt C:/Temp/av-kit/s39-s34-page-static-tests.txt` | 0 | Exact unconditional Color assertion is line 83; HELP_TOPICS is line 106. |
| Literal sweep over plan/task: `rtk proxy rg -n -e "default 10" -e "2–100" -e "2\\.\\.100" -e "REGION_TOLERANCE" -e "plan 3" -e "execution 6" docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md docs/execution/plans/2026-10-16-capture-new-marks/task.md` | 0 | Named definitions at plan:116/121, repeated explanatory values at :161/179/472/474, caps :58/428; no conflicting live value found. |

Final read-back found the report at the exact requested path; its frontmatter has exactly the nine required keys and five findings. A final `git status --short --untracked-files=all` (exit 0) still listed only the same six plan files, and final `git diff --stat` (exit 0) remained empty. The protocol was reread before closeout.

A final UTF-8 read of `ui/package.json` observed `typecheck: tsc --noEmit`; `Get-Content ui/tsconfig.json` succeeded (exit 0) and showed `"include": [..., "src", "tests"]`. Initial reads of guessed `ui/tsconfig.node.json` and `ui/tsconfig.web.json` printed file-not-found diagnostics; those files are not used as evidence. This confirms that F1's stale helper types affect the actual static gate.

Additional bounded `rg`/UTF-8 source reads inspected bake functions/constants, the Session 36 seam and plan references, API error mappings, sidecar/clamp/flatten entrypoints, domain enum expectations, MCP description test, help and viewport/hit-test consumers. Results support Q1–Q7 and are quoted where decisive.

Operational read failures are disclosed, not counted as product evidence: initial `rtk proxy Get-Content` failed with exit 1 because Get-Content is a PowerShell cmdlet, not an executable; the first double-quoted child-shell bootstrap failed with exit 1 when outer-shell variable expansion removed the `if` operand. The corrected single-quoted PowerShell read succeeded. A static `rg` that included nonexistent `packages/api/src/avkit_api/error_handlers.py` exited 2; its existing `errors.py` output showed `AnnotationValidationError: 422`, and no claim relies on the nonexistent file. The memory-registry keyword search returned no Session 39 guidance used in this review.

## Verdict

`changes_required`. **Intent achieved: partial.** Correct F1's exact amendment inventory and F2's Red fixture/baseline sequencing through `/plan-corrections`, then resubmit round 2 with the protocol's untruncated blast-radius census and per-hit dispositions. F3–F5 are non-blocking improvements/limitations to address or explicitly retain with measured reasoning in that correction pass; they do not independently require another round.

The review does not authorize implementation, commits or merges. Preserve the ledger's existing loop and round history. No reviewed file was edited.

Report destination: `C:/Temp/av-kit/dispatch/s39-plan-review-report.md`. Canonical copy destination for the author: `.agent/context/handoffs/2026-10-16-capture-new-marks-plan-critical-review.md`.

The template and final verdict schema v2 govern non-blocking findings; the older workflow sentence demanding an empty findings array on approval is superseded. The explicit user scope also supersedes the generic workflow timestamp-script/final-line and canonical-write instructions: only this receipt report is written, no extra script runs, and the final chat response is one JSON verdict.

---

## Corrections Applied — 2026-10-16 (round 1 → round 2)

> **Corrector**: Claude Code / Anthropic (plan author, coder role). **Verdict set**: `corrections_applied`. This is not an approval: only an independent `/plan-critical-review` pass may set `approved`. Nothing was executed, committed or merged. The worktree still shows only untracked plan-local files and this handoff.

### Finding dispositions

| # | Verified? | Disposition | Where (plan = `implementation-plan.md`, task = `task.md`) |
|---|-----------|-------------|-----------|
| F1 | Confirmed (Session 34 `capture-toolbar.test.ts:83` and `capture-page.behavior.test.ts:1235-1250,1327,1338` read from `claude/s34-capture-chrome`) | **Fixed.** TA-2 now names `TOOLS`, `MARKS` and `expectedGroups` as the leading rules. The `:83` assertion becomes `` expect(got.includes('color'), …).toBe(!regionCase) ``, and every tool × selection combination keeps its own expectedGroups case. TA-4 adds `block: ['capture-block-size']` to `MEU65_OPTION_IDS`, adds `'block'` to the option-group type unions, extends `MEU65_TOOLBAR`/`MEU65_TOGGLES` with both tools, and puts the region cases before `capture-tool-text`, so the post-loop Color query still finds Color. It also asserts that the block control is present and absent. New TA-5 covers the e2e `test-ids.ts` constants and the AC-65.4 NO_OVERFLOW tool loop; an overflow there is S2. `CENSUS_PATTERNS` adds `MEU65_`, `expectOptionGroups`, `toContain('color')`, `capture-chrome-options` and `expectNoOverflow`, and row 1's `rg` runs them. | plan:140 (TA-2/TA-4/TA-5), :141, :169-170, :220-225, :253, :414-415; task row 1 |
| F2 | Confirmed (the Session 36 `installFidelitySeam` reads both PNGs eagerly; the fixtures were first written in old row 3; AC-91.10 ran after MEU-90 added the canvas) | **Fixed.** New contract `REGION_E2E_RED`. The seam sets `window.__e2eDetailServed` and records `av-kit:capture:error` events in `window.__e2eCaptureErrors`. The test waits with `page.waitForFunction`, and its first assertions are `errors` equal to `[]` and `data-overlay-ready === 'true'`. A seam or fixture failure therefore cannot pass as the product Red. Old rows 3 and 5 are split. Row **3a** is the backend Green and writes the real-bake fixtures; it fails if `ui/src` changed (tracked diff plus untracked files), then builds and runs `--grep "AC-90.12"` against the **baseline renderer**, and `red-check.py` reads that receipt. Row **3b** is the renderer Green and snapshots `ui/src`. Row **5a** is the eraser backend; it compares its `ui/src` snapshot with 3b by `Get-FileHash`, then runs `--grep "AC-91.10"` against the **MEU-90 renderer**. Row **5b** is the eraser renderer. AC-91.10's negative now names the MEU-90 renderer, not "the baseline". Rows 2 and 4 run no Electron. The final real-bake freshness oracle and the immutable expectations are unchanged. | plan:130, :343-379 (§2, §3), AC-90.12, AC-91.10; task rows 2, 3a, 3b, 4, 5a, 5b, 6 |
| F3 | Confirmed by static trace of `_names_declared`; now pinned by the negative selftest fixture `unrelated-module-from-new-test` | **Fixed.** `red-check.py` now takes the missing *subject* from the error's own grammar (`MISSING_SUBJECT`: 9 patterns, e.g. `cannot import name 'X'`, `Cannot find module X imported from`, `Failed to resolve import "X"`). A line is excused only when every subject on it is declared-new. `HARD_SETUP_FAILURE` (launch failure, test or action timeout, `ECONNREFUSED`/`EADDRINUSE`) is never excused. New negative fixtures: an unrelated module imported from the new test file; a misspelled name imported from a declared module; an assertion mixed with an unrelated import. New positive fixture: a new module named with `imported from`. 18 fixtures (8 pass, 10 refused). | `red-check.py`; plan §2, R-3 |
| F4 | Confirmed by trace (module constants were outside every compared function AST); `s39-scope-ast-real.txt` now shows `SUPERSAMPLE` and `FONT_CANDIDATES` edits refused | **Fixed.** New `scope-ast.py` freezes the whole adapter module. Every top-level statement and every `CaptureAdapter` body statement must have the same `ast.dump` in the same order, except `bake`/`_apply` and the five declared new region names. The class header (bases, keywords, decorators) is frozen. Import bindings are compared per binding, and a new import may not rebind a baseline name. A permitted name may not hide a reassignment of a frozen one (`region_clip = SUPERSAMPLE = 9` is refused). The selftest has 16 fixtures, including the changed `SUPERSAMPLE` and `FONT_CANDIDATES`. Against the real Session 36 adapter: self-compare 0 problems; `SUPERSAMPLE` 4→3 and a `FONT_CANDIDATES` edit are refused. `session-gate.ps1` step 5 now runs `uv run python $plan/scope-ast.py`. The path allow-list is unchanged for other files. | `scope-ast.py`, `session-gate.ps1`; plan:139 `PRODUCT_SCOPE`, §5, R-4 |
| F5 | Confirmed as a gap in the evidence. The fix also showed that the old "mean within 1" reference could differ from the bake on composed passes (sensitivity control: 6 of 8 passes) | **Fixed by making the arithmetic identical, as the review recommended, not by relaxing the tolerance.** `PIXELATE_MEAN` is replaced by `PIXELATE_QUANT` = `((sum + n//2) * ((1<<24)//n)) >> 24`, Pillow's integer box reduce transcribed exactly. The TS form avoids the 32-bit `>>` (the product can reach 2^33). R-1 shows per-band `reduce` equals `PIXELATE_QUANT` with diff **0** over 400 random cases (391 with partial edge blocks), and that `PIXELATE_QUANT` is within **1** of the exact round-half-up mean (the goal's bound). New `composed` check: 8 whole passes (rounding-boundary checkerboard and noise; pixelate then eraser over a pixelated ring; three repeated overlapping pixelates; a pixelate clipped off-canvas, then an eraser, then a pixelate) are byte-identical between the Pillow form and the reference. `REGION_TOLERANCE` now reads: unit parity exact (0); goal bound 1; Electron oracle pixelate 1 / eraser 0. `REGION_CASES` gains `pixelate-repeat-overlap` (row 2) and the rounding-boundary `pixelate-then-eraser` (row 4). `REGION_IMAGE_FIXTURE` states that the rectangles and their rings are disjoint. D-12 is rewritten. | plan:120-126, :167, :252, :482-491 (D-12), :619-627 (R-1); `region-pass-probe.py` |

Verified: 5 confirmed, 0 refuted.

### Other correction-pass changes

- **Pre-existing defect (not a review finding):** `CENSUS_PATTERNS` in the plan and the row 1 `rg` in the task had a literal `0x08` (backspace) byte where `_apply\b` was meant. `file` reported "with overstriking". Both now hold a backslash followed by `b`. Both files have 0 control bytes, and the re-extracted row 1 command holds `_apply\b`.
- `PIXELATE_BAKE` `reduce-rgba` max diff restated from 106 to 105 to match the re-run R-1 receipt (`reduce-rgba: … max colour-channel diff 105`).
- H1-1's row filter uses `re.fullmatch('[0-9]+[a-z]?', …)` (it was `.isdigit()`), so rows 3a/3b/5a/5b are counted, and it prints any unchecked ids. The `Select-String` patterns in rows 6 and H1-2 add `outside scope`, `SCOPE-AST` and `PRODUCT_SCOPE`.
- The plan status line says round 2 is pending. The Handoff Set lists `scope-ast.py`.

### Blast-radius census (Step 5c)

Receipt: `C:/Temp/av-kit/census-s39-r1.txt` (untruncated, `rg -F -n -e` per term over both plan files; each block is headed by its rg exit code and hit count).

- **Old values: 28 swept, 7 hits, all confirmed-consistent.**
  - `generated in row 3` ×1 is the prefix of the intended "row 3a".
  - `s39-90-red-build` ×1 and `s39-91-red-build` ×1 are the build receipts, now in rows 3a/5a as intended.
  - `round-half-up mean` ×4 are the goal-bound reference, kept on purpose.
  - The other 24 terms have 0 hits, including `PIXELATE_MEAN`, `106`, `14 fixtures`, `rows 2–3`, `rows 4–5`, `no layer on the baseline`, `frozen adapter functions`, `$scopeAst`, `color first`, `.isdigit()`, `| 3 |` and `| 5 |`.
- **New values: 28 swept, 81 hits, all intended sites.** Examples: `PIXELATE_QUANT` ×10, `REGION_E2E_RED` ×8, `row 3a` ×7, `row 5a` ×6, `scope-ast.py` ×5, `capture-block-size` ×5, `pixelate-then-eraser` ×4, `REGION_TOLERANCE` ×4, `105` ×3 (all `reduce-rgba`).
- **Semantic variants declared:** the tolerance as prose (`within 1`, `maximum difference`), as the named contract, and as the Electron per-mark numbers; the row split as ids, as `rows N` prose, and as receipt slugs; the mean as `PIXELATE_MEAN`, `round half up` and `round-half-up mean`.
- **Summary:** 56 values swept (28 old, 28 new), 3 variant families, 88 hits (a line can match more than one term). The new-value hits are the sites edited in this pass; the 7 old-value hits are confirmed consistent.

### Verification (receipts under `C:/Temp/av-kit/`, read back after the run)

| Check | Receipt | Result |
|---|---|---|
| Task contract lint (`tools/lint_task_contract.py`) | `s39-r1-task-lint.txt` | `OK: 26 row(s)`; 24 rows fully checked; dependencies resolve and are acyclic; exit 0 |
| Row command parse (24 extracted rows, PowerShell AST) | `s39-r1-row-parse.txt` | 24 files, 0 parse errors, exit 0 |
| `session-gate.ps1` parse | `s39-gate-parse.txt` | 0 parse errors, exit 0 |
| `region-pass-probe.py` (R-1) | `s39-r1-probe.txt` | Pillow 12.3.0; reduce-bands diff 0 vs `PIXELATE_QUANT`, 1 vs exact mean; reduce-rgba 105; bake-vs-reference 0; composed 0 of 8 differ (control: 6); `0 problem(s)`, exit 0 |
| `red-check.py --selftest` (R-3) | `s39-redcheck-selftest.txt` | 18 fixtures, 0 wrong, exit 0 |
| `scope-ast.py --selftest` (R-4) | `s39-scope-ast-selftest.txt` | 16 fixtures, 0 wrong, exit 0 |
| `scope-ast.py` on real sources | `s39-scope-ast-real.txt`; `s39-scope-ast-s36.txt` | Session 36 adapter vs itself: 0 problems; `SUPERSAMPLE` and `FONT_CANDIDATES` mutations refused. CLI with `--base bb0ef7e` on this main checkout (pre-Session-36 adapter): 2 problems (`ARROWHEAD_LENGTH_FACTOR`, `_apply_arrow`), refused as expected |
| `identity.py --selftest` | `s39-identity-selftest.txt` | 0 failures, exit 0 |

### Open items for round 2 and for Mat

- **Prerequisite branches:** `claude/s34-capture-chrome` (`89c2937`) and `claude/s36-capture-render-fidelity` (`bb0ef7e`) must land on main before execution. Row 0 checks this with `BASE_MARKERS`.
- **D-16 (human decision):** the plan recommends a separate "Block size" number field in the contextual options row, shown only for Pixelate; this is a product preference for Mat to confirm.
- **Ledger:** loop `s39-plan-2026-10-16-capture-new-marks` refuses round 2 on its token budget (11,143,707 used of 10,500,000). Only a named human can continue it (`review_ledger.py continue … --by <name>`), or Mat reviews as the fallback. Round 2 was not dispatched.

### Post-correction updates (2026-10-16, before round 2)

These follow Mat's message "1. run the unlock for me 2. confirmed 3. merge as you see fit". They close the three open items above.

- **Ledger:** continued by Mat with `+11,787,414` tokens (receipt `s39-ledger-continue.txt`): `OK: round 2 permitted mode=plan (1/3 used, no stop active)`, tokens 11,143,707/22,287,414.
- **D-16:** Mat confirmed the separate Block size field. The plan's D-16 and the task's preamble and row 0 now record the confirmation.
- **Base merged:** `main` was fast-forwarded to Session 34 (`89c2937`) and Session 36 (`bb0ef7e`) was merged on top as `90bb409` (not pushed). Local checks on the merged tree are under `C:/Temp/av-kit/merge-s34-s36/`: tsc and eslint clean, Vitest 839/839, pytest 676/0, Electron 144/144. `WT` was fast-forwarded to `90bb409`. Plan User Review Required item 1 and the task preamble now say so. Row 0 still checks `BASE_MARKERS`.
- **Scope check on the merged base:** `scope-ast.py --base 90bb409` reports 0 problems, exit 0 (receipt `s39-scope-ast-merged.txt`).
- **Anchor shift:** Session 36 added 180 net lines above the Session 34 blocks in `ui/tests/unit/capture-page.behavior.test.ts`. `MEU65_OPTION_IDS` is now near line 1415, the `cases` array near 1507, and the Color group query near 1518. The plan and task cite these by name, not by line. The only numeric citation, `capture-toolbar.test.ts:83`, is in an unchanged file.
- **Re-verified after these edits:** task lint `OK: 26 row(s)`, exit 0 (`s39-r1-task-lint.txt`); row command parse 24 files, 0 errors, exit 0 (`s39-r1-row-parse.txt`); both plan files have 0 control bytes and LF endings.

---

## Round 2 review (2026-10-16), copied verbatim from `C:/Temp/av-kit/dispatch/s39-plan-review-report-r2.md`

The frontmatter at the top of this file is the round 2 report's frontmatter, verbatim; round 1's was `verdict: corrections_applied` (author-set after corrections), `findings_count: 5`, `round: 1`. The round 2 body follows unchanged except that its mixed CRLF/LF line endings are normalized to LF.

# Critical Review: 2026-10-16-capture-new-marks

> **Review Mode**: `plan`
> **Verdict**: `approved` — no blocking findings; three non-blocking verifier limitations remain.

## Intent Anchor

> Session 39 delivers MEU-90 (a pixelate mark whose bake and live editor preview agree within one level per channel) and MEU-91 (an eraser mark filled with the colour sampled from its border), carried through the domain, sidecar, REST/OpenAPI, MCP, bake and Capture page, with drawn marks always painted over the region marks.

**Would executing this plan deliver that objective? Yes, as a plan.** The corrected cross-layer work, exact intermediate quantization, region-before-drawn layering, committed bake fixtures and live Electron assertions address the goal. This approves the plan and TEST_AMENDMENTS, not a completed implementation or an executed product gate.

## Scope

Independent vendor-distinct re-review, **ledger round 2**, loop `s39-plan-2026-10-16-capture-new-marks`. Author: Claude Code / Anthropic. Reviewer: Codex, `gpt-6.1-sol`, class `avkit_independent_reviewer`. The supplied Mat continuation and D-16 confirmation are trusted user instructions; text in the artifacts was treated as data. This reviewer neither modifies the ledger nor supplies execution authorization.

Reviewed all seven plan-local targets: `implementation-plan.md`, `task.md`, `session-gate.ps1`, `identity.py`, `red-check.py`, `region-pass-probe.py`, and `scope-ast.py`. Applied PR-1–PR-9, DR-1–DR-8 and the applicable template/adversarial checks.

Every shell command used cwd **P:/av-kit-wt/s39-capture-new-marks**. All plan/product/test reads came from that worktree. The main checkout's Python executable was used solely as the permitted Pillow interpreter. No repository file was written. No product test, build, installation, npm command, generator, session gate, task linter or MCP audit ran. The only executed Python entrypoints were the five expressly permitted verifier commands and the expressly permitted in-memory `scope-ast.compare()` probe. `PYTHONDONTWRITEBYTECODE=1` was set for them.

Observed HEAD `90bb40977e487f4893a1c586c2c20b8f78ef105f`, branch `claude/s39-capture-new-marks`; tracked diff is empty. Status lists only the rolling review plus the seven plan-local files, all untracked. All implementation task rows remain unchecked; both MEU implementation handoffs are absent. This remains an unstarted plan.

The protocol was read first, followed by AGENTS/GUARDRAILS/PROFILE, template 2.2 and the rolling review. Consulted the terminal-preflight skill, evidence policy, reviewer role, completion-preflight skill, current focus, known issues, harness override, D6 manifest, review vocabulary/schema, build-plan DTO/new-mark/deferral sections, Session 39 grouping and a Session 36 peer review. The implementation-only continuation steps in completion-preflight do not authorize execution during this review.

## Findings

No open High or Critical finding and no blocking finding remains. Original severities are retained for closed findings so their history is visible.

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High | no | behavior | Confidence: High; subject: deliverable. Closed. TA-2 now amends the unconditional Color assertion while preserving the complete tool x selection oracle. TA-4 adds all block-group types and control IDs and leaves Text last in the cases loop; TA-5 extends IDs and overflow coverage. | `P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:140` | Apply the enumerated amendments without weakening the remaining assertions. | fixed |
| F2 | High | no | behavior | Confidence: High; subject: deliverable. Closed. Rows 3a and 5a generate real-bake fixtures before their Electron Red runs and retain the baseline and MEU-90 renderer schemas respectively. REGION_E2E_RED correctly predicts an Invalid overlay marks error at the first assertion, rather than a missing-layer assertion. The snapshot limitation is recorded separately as F6. | `P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:130; P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/task.md:42` | Retain the explicit unknown-mark diagnostic and the full capture-inbox runs in rows 3b and 5b. | fixed |
| F3 | Medium | no | control-defeat | Confidence: High; subject: committable-tooling. mechanism: task-row-completion-predicate. Partially closed. The original importing-filename witness is refused and all 18 selftests pass, but _names_declared still uses substring membership. A receipt containing only Error: Failed to resolve import "./capture-region-pass-fixture" and Test Files 1 failed (1), with child exit 1, is accepted even though that fixture module is not declared new. This is a static trace, not an extra executed parser probe. Mixed assertion plus unrelated Python ImportError is also not refused by SETUP_FAILURE. | `P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/red-check.py:110; P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/red-check.py:128` | Match declared export names exactly and module basenames against explicit allowed paths; reject recognized unrelated import diagnostics even when another assertion is present. Retain this as a non-blocking residual of F3. | open |
| F4 | Medium | no | control-defeat | Confidence: High; subject: committable-tooling. mechanism: task-row-completion-predicate. Partially closed. The original constants/import/helper mutations are refused, but _frozen drops class imports while compare validates only module import bindings. The permitted read-only real-source compare returned [] after appending an indented from builtins import print as _apply_arrow inside CaptureAdapter, replacing the frozen painter binding without changing its method AST. No product code was changed or executed. | `P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/scope-ast.py:69; P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/scope-ast.py:96` | Compare import bindings in the CaptureAdapter scope too, or reject class imports. Treat this as a non-blocking residual of F4; bake/_apply still legitimately need changes for REGION_PASS. | open |
| F5 | Medium | no | behavior | Confidence: High; subject: deliverable. Closed. PIXELATE_QUANT matches installed Pillow 12.3.0 per-band reduce exactly in the reproduced cases; all eight composed passes are byte-identical and the exact-mean sensitivity control differs in six. The specified TS arithmetic avoids bitwise truncation and remains within exact double-integer range. | `P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:120; P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/region-pass-probe.py:278` | Keep exact intermediate quantization and committed whole-pass fixture assertions; retain REGION_TOLERANCE without widening it. | fixed |
| F6 | Medium | no | control-defeat | Confidence: High; subject: committable-tooling. mechanism: task-row-completion-predicate. New. The row 3b to 5a snapshot hashes tracked git diff output plus untracked filenames, not untracked file contents. Editing the newly created capture-region-pass.ts in place leaves both snapshot inputs unchanged, so the equality check does not establish the claimed exact renderer identity. The tracked annotate schema is still covered and full behavioral gates remain required. | `P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/task.md:43; P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/task.md:46` | Include path and content hashes of every untracked ui/src file in both snapshots, using one deterministic snapshot procedure. | open |

All three control-defeat rows use the vocabulary's `task-row-completion-predicate`. They are non-blocking and do not accumulate as blocking mechanism recurrences. F3/F4 record residual limits once, without escalating the fixed surface into another delivery-level blocker. The separate Green/full gates and independent execution review remain mandatory. F6 limits a historical renderer-identity claim; it does not establish that a materially missing final pixelate or eraser can pass the product gate.

## Recheck (2026-10-16)

### Prior Pass Summary

| Finding | Prior status | Round 2 closure status | Decisive evidence |
|---|---|---|---|
| F1 | High, blocking, open | **closed** (`fixed`) | Plan:140 TA-2/TA-4/TA-5 checked against merged toolbar test:20–38,77–84; behavior test:1395–1444,1507–1519; e2e:888–899; tsconfig:13–18. |
| F2 | High, blocking, open | **closed** (`fixed`) | Plan:130,349–350 and task:42–47 now stage fixture generation before each Electron Red. CapturePage:349–375 and annotate schema:56–67 establish the expected unknown-mark error. F6 separately limits the new snapshot claim. |
| F3 | Medium, non-blocking, open | **partially closed** (`open`) | Original importing-filename witness is now a refused fixture. Reproduced selftest:18 fixtures,0 wrong. Remaining substring/mixed-diagnostic limitations are in F3. |
| F4 | Medium, non-blocking, open | **partially closed** (`open`) | Constants, class header, ordinary attributes and drawn method ASTs are frozen. Selftest:16 fixtures,0 wrong; merged-base compare:0 problems; real SUPERSAMPLE mutation refused. Class-import rebinding still passes the permitted compare probe. |
| F5 | Medium, non-blocking, open | **closed** (`fixed`) | Probe:400 reduce cases diff0,8 whole passes diff0; exact-mean control differs in6. Plan:125,167,251–252 schedules the corresponding committed composed cases. |

### Confirmed Fixes

F1 no longer requires incompatible Color expectations, excludes block from helper types, or leaves a region tool active at the post-loop Color query. F2 no longer tries to read uncreated fixtures and no longer describes eraser Red against the original renderer. F5 removes the unstable one-level intermediate error before a mode operation, rather than widening the final bound. The literal backspace-byte correction is confirmed: both plan files have zero unexpected control bytes.

### Remaining Findings

F3, F4 and new F6 are non-blocking. Their exact witnesses and recommendations are recorded above and in Q1/Q3/Q4. No third correction round is required to settle those residuals.

## PR-6 Corrections Census

I independently re-ran **all 56 OLD/NEW literal searches** from the author's receipt against **both absolute worktree plan paths**, using `rtk proxy rg -F -n -- $term @paths`, immediately saving each child exit. Full unfiltered outputs were saved to `C:/Temp/av-kit/s39-r2-census-full.txt`; no head/tail filter was applied to a search. Each hit was checked against the complete numbered source reads. The receipt's repeated source lines were also compared in full with the author's receipt, not just its counts.

Observed output:

```text
TOTAL hit occurrences=88 unique file:line=46
author hit lines=88 independent hit lines=88 differences=0
CONTROL implementation-plan.md: 0
CONTROL task.md: 0
```

**Agreement with the author:** the raw census is complete and I agree with all literal-hit dispositions. The 7 old-value hits are intentional: task:41's “generated in row 3” is a prefix of row 3a, task:42/46 retain the correct Red build receipt slugs, and plan:120/165/491/620 retain the exact-mean reference deliberately. All remaining old terms have zero hits, including every old value explicitly required in the review request. All 81 new-value hits occur at the intended updated sites. This does not endorse the stronger semantic claim that the two verifiers or renderer snapshot are total; F3/F4/F6 qualify those claims.

The author's correction log:317–324 supplies collective but exhaustive assignments: all old hits are **confirmed-consistent**, and all new hits are explicitly described as the sites edited in this correction pass (**updated**). I accept those universal assignments as assigning a disposition to each member of the raw inventory, rather than treating them as a bare hit count. The per-location expansion below makes the mapping explicit; there is no unclassified hit. This is the basis for proceeding past PR-6, not a claim that the author's log contained a separate file:line table.

The census also checked row IDs, counts, tolerance/mean terminology, scope checker names and the tool-option expectation changes. Canonical definitions remain the Single-statement contracts. Their explanatory restatements do not define competing behaviors.

### Independent term-by-term output

The full term-by-term output and explicit per-hit expansion appear in Appendix A below.

## Checklist Results

Manual results below were observed by `gpt-6.1-sol`; manual observations have null exit codes. “partial” identifies the recorded non-blocking limitation rather than an unrun product gate presented as a pass.

### Plan Review (PR)

| Check | Result | Procedure / evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Compare both complete files: WP-1 rows2/3a/3b, WP-2 rows4/5a/5b, then full gate/hubs/H1/review/H2. New renderer Zod members are assigned to renderer Green, which is essential for each intended Red. |
| PR-2 Not-started | pass | git status/log/diff; all implementation rows unchecked; both implementation handoffs absent. |
| PR-3 Task contract | pass | Every actionable row has owner, deliverable, validation/read procedure, dependency and status. Split IDs are recognized by H1-1's fullmatch. No task linter was run. |
| PR-4 Validation realism | partial | F1/F2 blockers resolved. Read-only algorithms/selftests reproduced. F3/F6 limit some intermediate proof claims; final real-bake, TS, API/MCP and Electron gates remain explicitly required. |
| PR-5 Sources | pass | AC sources and named decisions checked against current DTO/new-mark sections and grouping. D-16 is human-confirmed and consistently uses the separate Block size field. |
| PR-6 Corrections readiness | pass | Complete independent56-term/88-hit census and full author receipt comparison above; collective assignments interpreted and expanded per hit below. Both MEU handoffs and rolling execution review are named. |
| PR-7 Scope discipline | pass | Named exclusions match the current deferral table; scrub gesture maps to registered MEU-85 and Session37. Alpha/lossy-decode limits are explicit inherited boundaries. No hidden missing MEU work found. |
| PR-8 Reachability/totality | partial | Trace REST annotate to service bake, flatten to saved sidecar marks and shared bake; CapturePage detail parsing to preview props; committed real bake to unit/Electron observables. Negative comparators and composed sensitivity control exist. F3/F4/F6 constrain verifier totality; they do not remove those production paths. |
| PR-9 Single statement | pass | Repeat-literal searches and source comparison show no materially different live arithmetic, row-order, block bound or tolerance definition. PIXELATE_QUANT/REGION_TOLERANCE remain canonical. |

### Docs Review (DR)

| Check | Result | Procedure / evidence |
|---|---|---|
| DR-1 Claim/state | partial | Draft state is accurate. Author's “F3/F4 fixed” is too broad as a totality claim; original witnesses are fixed, residual limits remain recorded. |
| DR-2 Old values | pass | All56 OLD/NEW searches reproduced;88 hits match author; intentional old mean/receipt/row-prefix hits dispositioned. |
| DR-3 References | pass | Project paths resolve or are scheduled creations. Numeric build-plan references moved after the merge, but section/symbol anchors resolve. |
| DR-4 Verification robustness | partial | Product negative oracles, bake freshness and exact composed fixtures are viable. F3/F4/F6 remain intermediate verifier limitations. |
| DR-5 Auditability | pass | Preserved exits and full verifier outputs below; actual static command outputs and complete census inventory included. |
| DR-6 Canon consistency | pass | Layer boundaries, sidecar version/extra-key rule, schema owners, original/annotated views, grouping and deferred MEU agree. Flatten retains saved-mark semantics; see boundary clarification below. |
| DR-7 Freshness | pass | Reproduced current plan-local scripts on HEAD90bb409; no reliance on author's old verifier or merged-product test counts as fresh evidence. |
| DR-8 Completion/risk | pass | Plan approval only. Product implementation and all runtime gates remain unexecuted by this reviewer; limitations are explicit. |

### Information Retrieval / Adversarial Verification

All numbered ACs have source columns and observable positives/negatives. All required current tooling entrypoints exist, including the five plan-local scripts and the inherited Session36 fixture writer/test. New region renderer/test/JSON/PNGs and future handoffs/reflection are explicitly scheduled; their present absence is expected. No materially missing unplanned executable was found.

The broad lexical existence sweep initially also emitted package-relative npm test paths and shortened .ts matches inside .tsx names. They resolve through npm --prefix ui/mcp-server or the actual .tsx paths; they are not missing executables. GUI reference files are genuinely absent and explicitly disclosed by the plan. The new scope script was checked explicitly as well as via its relative link.

Negative assertions were traced to actual observables: new union parsing, block output/uniformity, outside-rectangle invariance, mode versus mean, reversed region order, drawn marks over regions, pixel arrays against a fresh real bake, and live drag before pointer-up. Proposed tests must retain these assertions and the immutable expectations. Implementation anti-placeholder scans, final FAIL_TO_PASS bundles and actual product runtime outcomes are n/a for this unstarted-plan review.

## Answers to Q1–Q6

### Q1 — Electron sequencing and renderer identity

**The corrected intended Red is an unknown-mark rejection, not an exclusive missing-layer failure after successful setup.** On the actual baseline, CapturePage:355–360 calls parseAnnotateBody and emits “Invalid overlay marks”; it never reaches setOverlayReady(true). The baseline annotate schema:58 contains only the four existing types. Therefore row3a should terminate the wait on the recorded error and fail expect(errors).toEqual([]). Row5a analogously uses the MEU-90 schema, which still rejects eraser. The fixtures exist first in both cases. This closes the original fixture-order defect.

If errors==[] and overlay-ready==true both pass, those preconditions alone do **not** prove every later failure is exclusively a missing layer: image decoding, layer contents, screenshot sampling or the live-drag assertion can still fail. The corrected plan does not need that exclusivity. Its expected first-failure diagnostic is the unknown mark. Inspect the actual event/diagnostic when recording Red; red-check's generic assertion recognition does not prove its semantic cause. A timeout/launch refusal is not the intended Red.

**No**, row5a's snapshot does not prove byte-identical renderer state: tracked diffs are covered, but the newly created capture-region-pass.ts is untracked and only its filename is recorded (F6). Changing its bytes in place is invisible to the comparison. The tracked annotate schema remains covered, so this limitation does not invalidate the traced schema-rejection Red.

**Yes**, limiting5a to AC-91.10 while the common seam makes AC-90.12 temporarily Red is acceptable. This is an explicit intermediate dependency state, not a skip or removed expectation. Row5b already runs the whole capture-inbox file and must restore both; row6 additionally runs the whole Electron suite and repeats both pixel tests10 times. Full coverage is restored before closeout. None of those product runs was executed here.

### Q2 — Pixel arithmetic and the registered bound

The transcription matches the installed **Pillow12.3.0** implementation in every reproduced R-1 case:400 per-band cases,391 with partial edges, maximum difference0. The five clipped/partial/oversized bake-form cases also have difference0 and no outside writes. All8 composed passes agree byte-for-byte; replacing the quantizer with exact mean changes6, so the new comparison is sensitive to the former intermediate-rounding problem.

This is measured evidence against that installed version and the specified bounded integer inputs, not a formal proof of every future Pillow version. No network research or external source fetch was performed under the static-evidence restriction.

The TS formula is safe: n<=10000 and sum<=255n; the reciprocal-product stays below2^33 and far below2^53. Math.floor and arithmetic division avoid JavaScript's signed32-bit shift coercion. A literal >>24 would be wrong when the product exceeds2^31. Using the specified double-integer arithmetic preserves the Python integer result.

**Yes**, exact unit parity plus Electron layer tolerance1 satisfies the goal's numerical bound. Exact intermediate parity prevents a one-level difference from changing the eraser's modal bucket. R-1 separately observes maximum difference1 from exact round-half-up mean. The screenshot tolerance2 is an additional composed-display check; it must not replace or widen the layer-pixel bound1. Alpha-channel and JPEG/WebP decoder parity remain the explicit inherited oracle limitations.

### Q3 — Scope freezing

Ordinary edits to a frozen drawn method, module constant, existing module import target, class header or ordinary class attribute are rejected; the new checker materially fixes the original F4 constants gap.

It is **not** a complete binding freeze. Class imports are discarded by _frozen, but _bindings is called only for module statements. The allowed in-memory probe appended this text to the real adapter source, without writing or importing that changed source:

```python
    from builtins import print as _apply_arrow
```

compare returned [] even though this class binding replaces the frozen painter used by self._apply_arrow. This is F4's remaining limitation, not a new escalation of its severity.

Permission to change bake/_apply is consistent with PRODUCT_SCOPE and necessary to install REGION_PASS. It does not certify preservation of their drawn-mark dispatch or output semantics. Keep their change limited to region dispatch/order and require the existing drawn-mark gates plus AC-90.6/AC-91.6. AST identity is structural evidence, not a sandbox against arbitrary effects inside an authorized function.

### Q4 — Red-check attribution

The original F3 case is fixed: a new test filename no longer excuses a missing unrelated subject. Hard launch/timeout/connection patterns are not excused by declared names. All18 fixtures pass and they adequately pin the original witness and its stated new cases.

**Yes**, a receipt whose only failure is an unrelated missing import can still be accepted when its extracted subject merely contains a declared token. Static witness, child exit1:

```text
Error: Failed to resolve import "./capture-region-pass-fixture"
Test Files 1 failed (1)
```

The missing subject is not the declared module; substring membership nevertheless returns true, suppresses the setup refusal and attributes the diagnostic. No additional red-check probe was executed. Also, a plain unrelated Python ImportError after another assertion is not rejected because SETUP_FAILURE does not include that diagnostic; “any attributed line” is weaker than the docstring's “every failure.”

Record this residual once as F3, non-blocking. The18 fixtures do not establish universal refusal of unrelated setup failures. Final Green/full gates remain independent obligations.

### Q5 — Tool/selection coverage, typecheck and Color

**Yes, statically.** TOOLS grows from5 to7; MARKS grows from5 to7 including null. The nested loops and independent expectedGroups comparator remain, covering49 pairs. The extra Color assertion becomes an exact no-Color assertion for region cases. Mixed tool/selected-mark precedence follows the two explicit leading rules and still gets an independent expected result.

TA-4 covers every actual block-group type site: record key, parameter, Object.entries cast and cases element. Adding block:['capture-block-size'] makes the helper assert both presence and absence in every case. The new cases precede Text, leaving Text active for the unchanged Color query at merged line1518. ui/tsconfig.json:13–18 includes tests, so these types are part of the actual static gate. No typecheck was run here and no runtime pass is claimed.

TA-5 matches the merged AC-65.4 loop at e2e:896 and the registry's additive-ID organization. It extends coverage rather than weakening NO_OVERFLOW. D-16's separate field, focus protection, selected-mark synchronization, invalid-input behavior and undo test are consistently assigned.

### Q6 — TEST_AMENDMENTS approval

**Yes. I approve TEST_AMENDMENTS TA-1 through TA-5 as now written.** Round1's refusal of their incomplete inventory changes to approval. TA-1 is additive enum/wire coverage; TA-2 preserves the Cartesian oracle; TA-3 updates the help token and adds tool IDs; TA-4 covers options, types and post-loop state; TA-5 extends real-Electron overflow coverage and registers the four new IDs. No permission to weaken unrelated assertions is granted.

Preserve the case-sensitive TA-3 source-token expectation: the help source must contain lowercase “annotation tools” as specified, for example in the amended body, alongside the capitalized “Annotation tools” title. This can be satisfied inside the already authorized help prose change.

## Merge / Boundary Clarifications

The merge is outside this review target. Its resulting files contain both the ToolbarIconButton and text-metrics imports in CaptureViewport, and both chrome and fidelity test blocks/imports in capture-inbox. No reviewed production path or TEST_AMENDMENTS symbol disappeared.

The behavior-test anchors now resolve at1415/1507/1518 as supplied. The merged09 new-mark rules are at812–815 and825–827, and named deferrals at836, so some older numeric plan references (09:808–823/832) are shifted. Their headings/symbols identify the same rules; this does not invalidate the plan's meaning or require a merge review.

Flatten continues to consume **saved marks**: routes/captures.py:267–275 accepts EmptyIn, calls capture.flatten(id), and the service:624 invokes the same bake with saved marks. Read the plan's loose “flatten with a pixelate” wording as save/annotate the pixelate, then flatten; do not add an annotation-bearing flatten request body. That preserves D-22, the existing route contract and the restricted OpenAPI change set. This boundary was already noted in round1 and is not escalated into a new finding.

## Commands Executed and Observed Output

All terminal work was routed through rtk proxy. Except the initial bounded protocol/preflight bootstrap read, process output was redirected under C:/Temp/av-kit, child exits saved immediately, and completed receipts read. Long source-read views sometimes exceeded the tool display budget; the underlying receipts remained complete. The plan/task were subsequently read in bounded numbered sections, and all88 raw census source lines were compared without truncation. A JavaScript quoting error while preparing one existence-read call occurred before any shell command ran; the corrected call succeeded.

| Actual command / observation | Exit | Decisive observed output |
|---|---|---|
| rtk proxy git status --short --untracked-files=all | 0 | Only rolling review plus seven plan-local files untracked. Git warned it could not access the user's global ignore file; no credential/config file was read. |
| rtk proxy git log -3 --format='%h %p %s' | 0 | 90bb409 has parents89c2937 andbb0ef7e; both prerequisite sessions present. |
| rtk proxy git rev-parse HEAD; rtk proxy git branch --show-current; rtk proxy git diff --stat (each exit checked) | 0 each | 90bb40977e487f4893a1c586c2c20b8f78ef105f; claude/s39-capture-new-marks; empty tracked diff. |
| rtk proxy pwsh -NoProfile -Command <numbered Get-Content reads> | 0 | Complete plan/task/seven scripts and protocol/template/canon reads; decisive file:line excerpts are cited throughout this report. |
| rtk proxy rg -n -C12 -e 'Invalid overlay marks' -e 'av-kit:capture:error' -e 'data-overlay-ready' -e 'paintedAnnotations' -e 'drawingPreview' -e 'function changeStroke' -e 'function inspectMark' -e 'function createDrawnMark' ui/src/renderer/src/features/capture/CapturePage.tsx | 0 | Detail rejection emits Invalid overlay marks before overlayReady; move preview replaces at the original index; new drawing preview is separate. |
| rtk proxy rg -n -C8 -e 'NO_OVERFLOW' -e 'installFidelitySeam' -e 'CAPTURE_TEST_PORT' -e 'for \\(const tool' -e 'createImageBitmap' ui/tests/e2e/capture-inbox.test.ts | 0 | Tool loop:896; merged fixture seam:2089 eagerly reads both PNGs; in-page bitmap/canvas screenshot machinery exists. |
| rtk proxy rg source sweeps over API/MCP/service/help/test files (patterns recorded in the respective receipts) | 0 | Shared bake paths, saved-mark flatten, strict four-member baseline Zod union, exact Color/helper types and case-sensitive help assertion observed. |
| rtk proxy rg -F -n -- $term @paths, repeated for each of the56 terms | 0 or1 per term; wrapper0 | 7 old hits +81 new hits,46 unique file:line locations. Every per-term exit/count is embedded above. |
| PowerShell complete raw-line Compare-Object and byte inventory | 0 | 88 author lines versus88 independent lines; differences0; unexpected control bytes0 in both files. |
| PowerShell Test-Path over invoked file inventory, resolved against npm prefixes and creation rows | 0 | Current validators/scripts/fixture writer/test exist; planned new files and handoffs absent as expected. |
| rtk proxy rg -n -i 'Session 39\|capture-new-marks\|plan-critical-review' C:/Users/Mat/.codex/memories/MEMORY.md | 0 | Only unrelated older-workspace workflow entries; no relevant memory guidance used. |
| PowerShell Get-FileHash -Algorithm SHA256 over the seven plan files | 0 | Source manifest recorded below. |
| Five allowed verifier commands and allowed compare probe | 0 each | Full outputs embedded next. |

No repository validator, timestamp script or workflow continuation was run. The user's explicit five-command exception and single-JSON final output supersede generic workflow demands to run other scripts or append a timestamp. The author must copy this report verbatim into the existing canonical rolling review; the reviewer writes only the requested receipts report.

### Reproduced read-only verifier evidence

All commands below used cwd P:/av-kit-wt/s39-capture-new-marks, PYTHONDONTWRITEBYTECODE=1 and RECEIPTS_DIR=C:/Temp/av-kit. Each command was wrapped as:

```powershell
rtk proxy <exact argv below> *> C:/Temp/av-kit/<receipt>.txt
$rc=$LASTEXITCODE
Get-Content C:/Temp/av-kit/<receipt>.txt
exit $rc
```


#### red-selftest
Command: rtk proxy python docs/execution/plans/2026-10-16-capture-new-marks/red-check.py --selftest; preserved exit: 0.
```text
pytest-assertion: pass (expected pass)
pytest-new-export: pass (expected pass)
pytest-new-adapter-export: pass (expected pass)
vitest-new-module: pass (expected pass)
vitest-zod-assertion: pass (expected pass)
playwright-assertion: pass (expected pass)
electron-launch: refused (expected refused)
locator-timeout: refused (expected refused)
vitest-ansi-assertion: pass (expected pass)
ansi-locator-timeout: refused (expected refused)
unrelated-import: refused (expected refused)
unrelated-module-from-new-test: refused (expected refused)
unrelated-name-from-declared-module: refused (expected refused)
assertion-plus-unrelated-import: refused (expected refused)
vitest-new-module-imported-from: pass (expected pass)
collection-error: refused (expected refused)
passing-run: refused (expected refused)
no-exit-file: refused (expected refused)
red-check selftest: 18 fixture(s), 0 wrong: []
```
```json
{"schema_version":"evidence.v1","check_id":"s39-r2-red-selftest","command":"rtk proxy python docs/execution/plans/2026-10-16-capture-new-marks/red-check.py --selftest","cwd":"P:/av-kit-wt/s39-capture-new-marks","scope":"plan-local read-only verifier","phase":"targeted","exit_code":0,"result":"pass","tested_state":"90bb40977e487f4893a1c586c2c20b8f78ef105f+plan-review-r2-49E7B4EC0D6267E492FEA7213522370A101383A68D09957DAC648AE7758738E2","output":"pytest-assertion: pass (expected pass)\r\npytest-new-export: pass (expected pass)\r\npytest-new-adapter-export: pass (expected pass)\r\nvitest-new-module: pass (expected pass)\r\nvitest-zod-assertion: pass (expected pass)\r\nplaywright-assertion: pass (expected pass)\r\nelectron-launch: refused (expected refused)\r\nlocator-timeout: refused (expected refused)\r\nvitest-ansi-assertion: pass (expected pass)\r\nansi-locator-timeout: refused (expected refused)\r\nunrelated-import: refused (expected refused)\r\nunrelated-module-from-new-test: refused (expected refused)\r\nunrelated-name-from-declared-module: refused (expected refused)\r\nassertion-plus-unrelated-import: refused (expected refused)\r\nvitest-new-module-imported-from: pass (expected pass)\r\ncollection-error: refused (expected refused)\r\npassing-run: refused (expected refused)\r\nno-exit-file: refused (expected refused)\r\nred-check selftest: 18 fixture(s), 0 wrong: []","fresh":true}
```
#### identity-selftest
Command: rtk proxy python docs/execution/plans/2026-10-16-capture-new-marks/identity.py --selftest; preserved exit: 0.
```text
bound    uv.lock: state_changed=True historical_refused=True
bound    ui/package-lock.json: state_changed=True historical_refused=True
bound    mcp-server/package-lock.json: state_changed=True historical_refused=True
bound    ui/tests/e2e/fixtures/capture-region-pass.json: state_changed=True historical_refused=True
bound    ui/tsconfig.json: state_changed=True historical_refused=True
bound    ui/electron.vite.config.ts: state_changed=True historical_refused=True
bound    .agent/docs/commands.md: state_changed=True historical_refused=True
bound    docs/execution/plans/2026-10-16-capture-new-marks/session-gate.ps1: state_changed=True historical_refused=True
bound    packages/x.py: state_changed=True historical_refused=True
bound    tests/new_test.py (untracked): state_changed=True
bound    runtime node version: state_changed=True
artifact docs/execution/plans/2026-10-16-capture-new-marks/walkthrough.md: state_unchanged=True
artifact .agent/context/handoffs/h.md: state_unchanged=True
artifact docs/build-plan/09.md: state_unchanged=True
identity selftest: 0 failure(s)
```
```json
{"schema_version":"evidence.v1","check_id":"s39-r2-identity-selftest","command":"rtk proxy python docs/execution/plans/2026-10-16-capture-new-marks/identity.py --selftest","cwd":"P:/av-kit-wt/s39-capture-new-marks","scope":"plan-local read-only verifier","phase":"targeted","exit_code":0,"result":"pass","tested_state":"90bb40977e487f4893a1c586c2c20b8f78ef105f+plan-review-r2-49E7B4EC0D6267E492FEA7213522370A101383A68D09957DAC648AE7758738E2","output":"bound    uv.lock: state_changed=True historical_refused=True\r\nbound    ui/package-lock.json: state_changed=True historical_refused=True\r\nbound    mcp-server/package-lock.json: state_changed=True historical_refused=True\r\nbound    ui/tests/e2e/fixtures/capture-region-pass.json: state_changed=True historical_refused=True\r\nbound    ui/tsconfig.json: state_changed=True historical_refused=True\r\nbound    ui/electron.vite.config.ts: state_changed=True historical_refused=True\r\nbound    .agent/docs/commands.md: state_changed=True historical_refused=True\r\nbound    docs/execution/plans/2026-10-16-capture-new-marks/session-gate.ps1: state_changed=True historical_refused=True\r\nbound    packages/x.py: state_changed=True historical_refused=True\r\nbound    tests/new_test.py (untracked): state_changed=True\r\nbound    runtime node version: state_changed=True\r\nartifact docs/execution/plans/2026-10-16-capture-new-marks/walkthrough.md: state_unchanged=True\r\nartifact .agent/context/handoffs/h.md: state_unchanged=True\r\nartifact docs/build-plan/09.md: state_unchanged=True\r\nidentity selftest: 0 failure(s)","fresh":true}
```
#### scope-selftest
Command: rtk proxy python docs/execution/plans/2026-10-16-capture-new-marks/scope-ast.py --selftest; preserved exit: 0.
```text
identical: in scope (expected in scope)
permitted-changes: in scope (expected in scope)
supersample-changed: refused (expected refused) -- module-level change outside PRODUCT_SCOPE: statement 1: Assign(targets=[Name(id='SUPERSAMPLE', ctx=Store())], value=Cons
font-candidates-changed: refused (expected refused) -- module-level change outside PRODUCT_SCOPE: statement 2: Assign(targets=[Name(id='FONT_CANDIDATES', ctx=Store())], value=
frozen-method-changed: refused (expected refused) -- CaptureAdapter change outside PRODUCT_SCOPE: statement 1: FunctionDef(name='_apply_rect', args=arguments(posonlyargs=[],
frozen-helper-changed: refused (expected refused) -- module-level change outside PRODUCT_SCOPE: statement 3: FunctionDef(name='_color_rgb', args=arguments(posonlyargs=[], ar
class-attribute-changed: refused (expected refused) -- CaptureAdapter change outside PRODUCT_SCOPE: statement 0: Assign(targets=[Name(id='KIND', ctx=Store())], value=Constant(
new-unpermitted-constant: refused (expected refused) -- module-level change outside PRODUCT_SCOPE: statement 2: Assign(targets=[Name(id='FONT_CANDIDATES', ctx=Store())], value=
new-unpermitted-method: refused (expected refused) -- CaptureAdapter change outside PRODUCT_SCOPE: statement 1: FunctionDef(name='_apply_rect', args=arguments(posonlyargs=[],
import-rebinds-baseline-name: refused (expected refused) -- new imports rebind baseline names: ['SUPERSAMPLE']
baseline-import-removed: refused (expected refused) -- baseline import bindings removed or changed: ['math']
baseline-import-retargeted: refused (expected refused) -- baseline import bindings removed or changed: ['ImageDraw']
permitted-name-reassigns-constant: refused (expected refused) -- module-level change outside PRODUCT_SCOPE: statement 3: FunctionDef(name='_color_rgb', args=arguments(posonlyargs=[], ar
docstring-changed: refused (expected refused) -- module-level change outside PRODUCT_SCOPE: statement 0: Expr(value=Constant(value='Adapter.')) -> Expr(value=Constant(va
class-base-changed: refused (expected refused) -- module-level change outside PRODUCT_SCOPE: statement 4: ('CaptureAdapter',) -> ('CaptureAdapter', "Name(id='object', ctx
bake-removed: refused (expected refused) -- CaptureAdapter.bake is missing
scope-ast selftest: 16 fixture(s), 0 wrong: []
```
```json
{"schema_version":"evidence.v1","check_id":"s39-r2-scope-selftest","command":"rtk proxy python docs/execution/plans/2026-10-16-capture-new-marks/scope-ast.py --selftest","cwd":"P:/av-kit-wt/s39-capture-new-marks","scope":"plan-local read-only verifier","phase":"targeted","exit_code":0,"result":"pass","tested_state":"90bb40977e487f4893a1c586c2c20b8f78ef105f+plan-review-r2-49E7B4EC0D6267E492FEA7213522370A101383A68D09957DAC648AE7758738E2","output":"identical: in scope (expected in scope)\r\npermitted-changes: in scope (expected in scope)\r\nsupersample-changed: refused (expected refused) -- module-level change outside PRODUCT_SCOPE: statement 1: Assign(targets=[Name(id='SUPERSAMPLE', ctx=Store())], value=Cons\r\nfont-candidates-changed: refused (expected refused) -- module-level change outside PRODUCT_SCOPE: statement 2: Assign(targets=[Name(id='FONT_CANDIDATES', ctx=Store())], value=\r\nfrozen-method-changed: refused (expected refused) -- CaptureAdapter change outside PRODUCT_SCOPE: statement 1: FunctionDef(name='_apply_rect', args=arguments(posonlyargs=[],\r\nfrozen-helper-changed: refused (expected refused) -- module-level change outside PRODUCT_SCOPE: statement 3: FunctionDef(name='_color_rgb', args=arguments(posonlyargs=[], ar\r\nclass-attribute-changed: refused (expected refused) -- CaptureAdapter change outside PRODUCT_SCOPE: statement 0: Assign(targets=[Name(id='KIND', ctx=Store())], value=Constant(\r\nnew-unpermitted-constant: refused (expected refused) -- module-level change outside PRODUCT_SCOPE: statement 2: Assign(targets=[Name(id='FONT_CANDIDATES', ctx=Store())], value=\r\nnew-unpermitted-method: refused (expected refused) -- CaptureAdapter change outside PRODUCT_SCOPE: statement 1: FunctionDef(name='_apply_rect', args=arguments(posonlyargs=[],\r\nimport-rebinds-baseline-name: refused (expected refused) -- new imports rebind baseline names: ['SUPERSAMPLE']\r\nbaseline-import-removed: refused (expected refused) -- baseline import bindings removed or changed: ['math']\r\nbaseline-import-retargeted: refused (expected refused) -- baseline import bindings removed or changed: ['ImageDraw']\r\npermitted-name-reassigns-constant: refused (expected refused) -- module-level change outside PRODUCT_SCOPE: statement 3: FunctionDef(name='_color_rgb', args=arguments(posonlyargs=[], ar\r\ndocstring-changed: refused (expected refused) -- module-level change outside PRODUCT_SCOPE: statement 0: Expr(value=Constant(value='Adapter.')) -> Expr(value=Constant(va\r\nclass-base-changed: refused (expected refused) -- module-level change outside PRODUCT_SCOPE: statement 4: ('CaptureAdapter',) -> ('CaptureAdapter', \"Name(id='object', ctx\r\nbake-removed: refused (expected refused) -- CaptureAdapter.bake is missing\r\nscope-ast selftest: 16 fixture(s), 0 wrong: []","fresh":true}
```
#### scope-base
Command: rtk proxy python docs/execution/plans/2026-10-16-capture-new-marks/scope-ast.py --base 90bb409; preserved exit: 0.
```text
scope-ast: adapter outside PRODUCT_SCOPE: 0 problem(s) (base 90bb409)
```
```json
{"schema_version":"evidence.v1","check_id":"s39-r2-scope-base","command":"rtk proxy python docs/execution/plans/2026-10-16-capture-new-marks/scope-ast.py --base 90bb409","cwd":"P:/av-kit-wt/s39-capture-new-marks","scope":"plan-local read-only verifier","phase":"targeted","exit_code":0,"result":"pass","tested_state":"90bb40977e487f4893a1c586c2c20b8f78ef105f+plan-review-r2-49E7B4EC0D6267E492FEA7213522370A101383A68D09957DAC648AE7758738E2","output":"scope-ast: adapter outside PRODUCT_SCOPE: 0 problem(s) (base 90bb409)","fresh":true}
```
#### probe
Command: rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-10-16-capture-new-marks/region-pass-probe.py; preserved exit: 0.
```text
pillow 12.3.0
reduce-bands: 400 cases (391 with partial edge blocks), max channel diff vs PIXELATE_QUANT 0
reduce-bands: PIXELATE_QUANT vs the exact round-half-up mean, max channel diff 1
reduce-rgba: direct RGBA reduce, max colour-channel diff 105
bake-vs-reference: 5 pixelate cases, max channel diff 0, pixels changed outside the clipped rect 0
eraser: text-crossing ring -> (240, 240, 240)
eraser: 6/6 tie between (0,0,0) and (9,9,9) -> (0, 0, 0)
eraser: ring of a rect clipped at the left edge has 11 pixels, min x 0
eraser: rect covering the image -> inner ring, colour (1, 2, 3)
eraser: Pillow form equals the reference exactly on 3 cases: True
order: pixelate-then-eraser differs from eraser-then-pixelate: True
composed: 8 whole passes (rounding-boundary and noise images), Pillow form != reference in 0
composed: sensitivity control, an exact-mean reference differs from the Pillow form in 6 pass(es)
region-pass-probe: 0 problem(s)
```
```json
{"schema_version":"evidence.v1","check_id":"s39-r2-probe","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-10-16-capture-new-marks/region-pass-probe.py","cwd":"P:/av-kit-wt/s39-capture-new-marks","scope":"plan-local read-only verifier","phase":"targeted","exit_code":0,"result":"pass","tested_state":"90bb40977e487f4893a1c586c2c20b8f78ef105f+plan-review-r2-49E7B4EC0D6267E492FEA7213522370A101383A68D09957DAC648AE7758738E2","output":"pillow 12.3.0\r\nreduce-bands: 400 cases (391 with partial edge blocks), max channel diff vs PIXELATE_QUANT 0\r\nreduce-bands: PIXELATE_QUANT vs the exact round-half-up mean, max channel diff 1\r\nreduce-rgba: direct RGBA reduce, max colour-channel diff 105\r\nbake-vs-reference: 5 pixelate cases, max channel diff 0, pixels changed outside the clipped rect 0\r\neraser: text-crossing ring -> (240, 240, 240)\r\neraser: 6/6 tie between (0,0,0) and (9,9,9) -> (0, 0, 0)\r\neraser: ring of a rect clipped at the left edge has 11 pixels, min x 0\r\neraser: rect covering the image -> inner ring, colour (1, 2, 3)\r\neraser: Pillow form equals the reference exactly on 3 cases: True\r\norder: pixelate-then-eraser differs from eraser-then-pixelate: True\r\ncomposed: 8 whole passes (rounding-boundary and noise images), Pillow form != reference in 0\r\ncomposed: sensitivity control, an exact-mean reference differs from the Pillow form in 6 pass(es)\r\nregion-pass-probe: 0 problem(s)","fresh":true}
```
#### Allowed real-source AST comparison
Command (PYTHONDONTWRITEBYTECODE=1): rtk proxy python -c 'import importlib.util,subprocess; p=''docs/execution/plans/2026-10-16-capture-new-marks/scope-ast.py''; s=importlib.util.spec_from_file_location(''s39_scope'',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); src=subprocess.run([''git'',''show'',''90bb409:''+m.ADAPTER],capture_output=True,text=True,encoding=''utf-8'',check=True).stdout; print(''real identical:'',m.compare(src,src)); print(''real SUPERSAMPLE mutation:'',m.compare(src,src.replace(''SUPERSAMPLE = 4'',''SUPERSAMPLE = 3''))); print(''real class import shadows frozen painter:'',m.compare(src,src+''\n    from builtins import print as _apply_arrow\n''))'; preserved exit: 0.
```text
real identical: []
real SUPERSAMPLE mutation: ["module-level change outside PRODUCT_SCOPE: statement 8: Assign(targets=[Name(id='SUPERSAMPLE', ctx=Store())], value=Constant(value=4)) -> Assign(targets=[Name(id='SUPERSAMPLE', ctx=Store())], value=Constant(value=3))"]
real class import shadows frozen painter: []
```
The process exited 0; its third observation demonstrates the F4 scope false-pass. No changed adapter source was imported or executed.
### Reviewed source manifest
```text
review-only tested_state 90bb40977e487f4893a1c586c2c20b8f78ef105f+plan-review-r2-49E7B4EC0D6267E492FEA7213522370A101383A68D09957DAC648AE7758738E2
identity.py D6ED81B4279D2FD448D7A1F08748D6A920801463BF58AFA1860A9AD0F070182B
implementation-plan.md 6C44FA95A921A1B9704B3397CD2F8AACB635A14596DF229043E1C1BAA722B271
red-check.py 782A8A9F7AB9E5FF4ECBBAA16AFF5556C28DD7486E98C4EDE234F637013C08E4
region-pass-probe.py 58DBE001D55B4439063642872B64DEB31C52C51E64B79760CA94E014BFD9E473
scope-ast.py E71BE0A02EB316E5141627F92712148548335E6781806A06D1E937C760503CB6
session-gate.ps1 2319EA37566131310BE8C27A702934A2268B40CC9BC4CA05B4E5BEFD4412E8A7
task.md A6436BA45B555647D2AF0DA05619CE0E0B1BB7C8DA3CE7BF11EAEE21C91807A5
```
This identifies the reviewed seven files; it is not a product D6 full-gate identity.
## Appendix A — Complete census summary and per-hit dispositions
```text
OLD PIXELATE_MEAN : exit=1 hits=0 author=0
OLD 106 : exit=1 hits=0 author=0
OLD 14 fixtures : exit=1 hits=0 author=0
OLD 14 receipt : exit=1 hits=0 author=0
OLD 7 positive : exit=1 hits=0 author=0
OLD rows 2–3 : exit=1 hits=0 author=0
OLD rows 4–5 : exit=1 hits=0 author=0
OLD rows 2 and 4 : exit=1 hits=0 author=0
OLD row 3 generates : exit=1 hits=0 author=0
OLD generated in row 3 : exit=0 hits=1 author=1
OLD Green (MEU-90).** : exit=1 hits=0 author=0
OLD Green (MEU-91).** : exit=1 hits=0 author=0
OLD row 2 Red receipt : exit=1 hits=0 author=0
OLD no layer on the baseline : exit=1 hits=0 author=0
OLD frozen adapter functions : exit=1 hits=0 author=0
OLD 'frozen' : exit=1 hits=0 author=0
OLD $scopeAst : exit=1 hits=0 author=0
OLD color first : exit=1 hits=0 author=0
OLD within `REGION_TOLERANCE` of : exit=1 hits=0 author=0
OLD .isdigit() : exit=1 hits=0 author=0
OLD rows 3, 5 : exit=1 hits=0 author=0
OLD rows 2, 4) : exit=1 hits=0 author=0
OLD | 3 | : exit=1 hits=0 author=0
OLD | 5 | : exit=1 hits=0 author=0
OLD s39-90-red-build : exit=0 hits=1 author=1
OLD s39-91-red-build : exit=0 hits=1 author=1
OLD round half up : exit=1 hits=0 author=0
OLD round-half-up mean : exit=0 hits=4 author=4
NEW PIXELATE_QUANT : exit=0 hits=10 author=10
NEW REGION_E2E_RED : exit=0 hits=8 author=8
NEW scope-ast.py : exit=0 hits=5 author=5
NEW SCOPE-AST : exit=0 hits=2 author=2
NEW | 3a | : exit=0 hits=2 author=2
NEW | 3b | : exit=0 hits=2 author=2
NEW | 5a | : exit=0 hits=2 author=2
NEW | 5b | : exit=0 hits=2 author=2
NEW rows 3a : exit=0 hits=2 author=2
NEW row 3a : exit=0 hits=7 author=7
NEW row 5a : exit=0 hits=6 author=6
NEW 18 fixtures : exit=0 hits=1 author=1
NEW 105 : exit=0 hits=3 author=3
NEW pixelate-repeat-overlap : exit=0 hits=2 author=2
NEW pixelate-then-eraser : exit=0 hits=4 author=4
NEW capture-block-size : exit=0 hits=5 author=5
NEW MEU65_OPTION_IDS : exit=0 hits=1 author=1
NEW expectNoOverflow : exit=0 hits=2 author=2
NEW __e2eDetailServed : exit=0 hits=1 author=1
NEW __e2eCaptureErrors : exit=0 hits=1 author=1
NEW data-overlay-ready : exit=0 hits=1 author=1
NEW --grep "AC-90.12" : exit=0 hits=1 author=1
NEW --grep "AC-91.10" : exit=0 hits=2 author=2
NEW s39-ui-src-3b : exit=0 hits=2 author=2
NEW s39-ui-src-5a : exit=0 hits=1 author=1
NEW REGION_TOLERANCE : exit=0 hits=4 author=4
NEW toBe(!regionCase) : exit=0 hits=1 author=1
NEW fullmatch : exit=0 hits=1 author=1
TOTAL hit occurrences=88 unique file:line=46
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:120 chars=836
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:121 chars=534
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:122 chars=428
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:125 chars=1077
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:126 chars=894
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:129 chars=1012
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:130 chars=1259
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:134 chars=940
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:138 chars=151
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:139 chars=913
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:140 chars=2677
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:141 chars=727
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:165 chars=655
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:167 chars=408
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:170 chars=587
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:172 chars=391
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:251 chars=283
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:252 chars=398
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:255 chars=411
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:349 chars=490
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:350 chars=876
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:361 chars=43
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:397 chars=432
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:402 chars=364
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:416 chars=161
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:487 chars=350
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:489 chars=229
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:491 chars=825
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:511 chars=349
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:619 chars=355
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:620 chars=214
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:621 chars=143
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:625 chars=414
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:628 chars=102
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:631 chars=877
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md:73 chars=73
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/task.md:39 chars=1189
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/task.md:41 chars=2015
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/task.md:42 chars=2991
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/task.md:43 chars=1719
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/task.md:45 chars=1816
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/task.md:46 chars=2948
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/task.md:47 chars=1380
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/task.md:49 chars=1027
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/task.md:52 chars=755
HIT P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/task.md:53 chars=666
CONTROL P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/implementation-plan.md: 0
CONTROL P:/av-kit-wt/s39-capture-new-marks/docs/execution/plans/2026-10-16-capture-new-marks/task.md: 0
```
| Term category/value | Exact location | Disposition |
|---|---|---|
| OLD generated in row 3 | task.md:41 | confirmed-consistent (intentional reference/prefix/receipt) |
| OLD s39-90-red-build | task.md:42 | confirmed-consistent (intentional reference/prefix/receipt) |
| OLD s39-91-red-build | task.md:46 | confirmed-consistent (intentional reference/prefix/receipt) |
| OLD round-half-up mean | implementation-plan.md:120 | confirmed-consistent (intentional reference/prefix/receipt) |
| OLD round-half-up mean | implementation-plan.md:165 | confirmed-consistent (intentional reference/prefix/receipt) |
| OLD round-half-up mean | implementation-plan.md:491 | confirmed-consistent (intentional reference/prefix/receipt) |
| OLD round-half-up mean | implementation-plan.md:620 | confirmed-consistent (intentional reference/prefix/receipt) |
| NEW PIXELATE_QUANT | task.md:43 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW PIXELATE_QUANT | implementation-plan.md:120 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW PIXELATE_QUANT | implementation-plan.md:122 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW PIXELATE_QUANT | implementation-plan.md:165 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW PIXELATE_QUANT | implementation-plan.md:167 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW PIXELATE_QUANT | implementation-plan.md:487 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW PIXELATE_QUANT | implementation-plan.md:489 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW PIXELATE_QUANT | implementation-plan.md:619 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW PIXELATE_QUANT | implementation-plan.md:620 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW PIXELATE_QUANT | implementation-plan.md:625 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW REGION_E2E_RED | task.md:41 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW REGION_E2E_RED | task.md:42 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW REGION_E2E_RED | task.md:45 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW REGION_E2E_RED | task.md:46 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW REGION_E2E_RED | implementation-plan.md:130 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW REGION_E2E_RED | implementation-plan.md:172 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW REGION_E2E_RED | implementation-plan.md:255 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW REGION_E2E_RED | implementation-plan.md:350 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW scope-ast.py | task.md:49 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW scope-ast.py | implementation-plan.md:73 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW scope-ast.py | implementation-plan.md:139 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW scope-ast.py | implementation-plan.md:397 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW scope-ast.py | implementation-plan.md:631 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW SCOPE-AST | task.md:49 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW SCOPE-AST | task.md:53 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW \| 3a \| | task.md:42 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW \| 3a \| | task.md:43 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW \| 3b \| | task.md:43 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW \| 3b \| | task.md:45 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW \| 5a \| | task.md:46 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW \| 5a \| | task.md:47 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW \| 5b \| | task.md:47 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW \| 5b \| | task.md:49 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW rows 3a | implementation-plan.md:361 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW rows 3a | implementation-plan.md:402 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW row 3a | task.md:41 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW row 3a | task.md:42 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW row 3a | task.md:46 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW row 3a | implementation-plan.md:126 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW row 3a | implementation-plan.md:130 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW row 3a | implementation-plan.md:172 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW row 3a | implementation-plan.md:349 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW row 5a | task.md:43 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW row 5a | task.md:45 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW row 5a | task.md:46 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW row 5a | implementation-plan.md:126 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW row 5a | implementation-plan.md:130 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW row 5a | implementation-plan.md:255 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW 18 fixtures | implementation-plan.md:628 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW 105 | implementation-plan.md:121 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW 105 | implementation-plan.md:489 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW 105 | implementation-plan.md:621 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW pixelate-repeat-overlap | implementation-plan.md:125 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW pixelate-repeat-overlap | implementation-plan.md:167 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW pixelate-then-eraser | task.md:45 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW pixelate-then-eraser | implementation-plan.md:125 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW pixelate-then-eraser | implementation-plan.md:251 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW pixelate-then-eraser | implementation-plan.md:252 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW capture-block-size | implementation-plan.md:134 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW capture-block-size | implementation-plan.md:138 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW capture-block-size | implementation-plan.md:140 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW capture-block-size | implementation-plan.md:170 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW capture-block-size | implementation-plan.md:416 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW MEU65_OPTION_IDS | implementation-plan.md:140 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW expectNoOverflow | task.md:39 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW expectNoOverflow | implementation-plan.md:141 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW __e2eDetailServed | implementation-plan.md:130 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW __e2eCaptureErrors | implementation-plan.md:130 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW data-overlay-ready | implementation-plan.md:130 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW --grep "AC-90.12" | task.md:42 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW --grep "AC-91.10" | task.md:46 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW --grep "AC-91.10" | implementation-plan.md:350 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW s39-ui-src-3b | task.md:43 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW s39-ui-src-3b | task.md:46 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW s39-ui-src-5a | task.md:46 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW REGION_TOLERANCE | implementation-plan.md:122 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW REGION_TOLERANCE | implementation-plan.md:129 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW REGION_TOLERANCE | implementation-plan.md:487 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW REGION_TOLERANCE | implementation-plan.md:511 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW toBe(!regionCase) | implementation-plan.md:140 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
| NEW fullmatch | task.md:52 | updated (intended corrected site; semantic limits F3/F4/F6 recorded separately) |
Expanded hit assignments: 88. Raw untruncated independent rg receipt: C:/Temp/av-kit/s39-r2-census-full.txt. Author receipt: C:/Temp/av-kit/census-s39-r1.txt. Full raw-line comparison found zero differences.

## Verdict

`approved`. **Intent achieved: yes (plan suitability).** F1, F2 and F5 are closed. F3 and F4 are partially closed with non-blocking residual verifier limits; F6 records the new snapshot limitation. TEST_AMENDMENTS TA-1–TA-5 are approved. No Critical or open High finding exists, and no further machine-review round is required for these non-blocking observations.

Follow-up actions:

1. The author copies this complete report verbatim to the existing rolling review and records the matching v2 verdict in the same ledger loop, round2.
2. Preserve F3/F4/F6 as non-blocking correction notes; if hardened, use the recommendations and retain their negative witnesses. Do not reset the loop or erase its prior findings.
3. Before implementation, obtain the explicit execution message required by this plan's Claude Code human gate. D-16 is already confirmed and must not be reopened.
4. During execution, establish actual Red diagnostics and the immutable unit/API/MCP/Electron Green/full results. This review's read-only verifier passes are not those product receipts.

Residual risk is bounded to the stated verifier limitations, the inherited opaque-PNG/decoder oracle boundary and implementation work not yet performed. The review does not claim completion of Session39 and authorizes no commit, push or merge.

Final artifact readback (PowerShell static inspection, exit 0): exactly nine frontmatter keys, six finding records F1-F6, zero blocking rows, five parseable evidence.v1 records with exit 0, and 34 balanced fence lines. A first local readback counted the five prior-summary rows as finding rows; the corrected check scopes the severity/blocking columns and reports six. Final git status matches the initial eight untracked paths and git diff --stat remains empty. No repository file was changed.

Report: C:/Temp/av-kit/dispatch/s39-plan-review-report-r2.md.
Canonical copy destination (author-owned): P:/av-kit-wt/s39-capture-new-marks/.agent/context/handoffs/2026-10-16-capture-new-marks-plan-critical-review.md.

---

## Post-approval note (author, 2026-10-16)

The ledger recorded round 2 as `approved` (blocking 0, `intent_achieved=yes`); receipt `C:/Temp/av-kit/s39-ledger-state-final.txt`. After the review, one line of `implementation-plan.md` changed: the line-20 status line no longer says "Round 2 pending"; it records the round 2 verdict and the open non-blocking residuals F3, F4 and F6. Nothing else in the seven reviewed files changed. The plan's SHA-256 moved from the reviewed `6C44FA95…B271` to `1D96692F…48D4`; the other six files still match the reviewer's manifest. F3, F4 and F6 are left open as the reviewer recorded them; they are not corrected here, because a correction would change reviewed verifier code without a further review round.

