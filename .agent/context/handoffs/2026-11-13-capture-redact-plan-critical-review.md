---
date: "2026-11-13"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-13-capture-redact/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s68-plan-canonical-2026-11-13-capture-redact"
round: 2
---

# Critical Review: 2026-11-13-capture-redact

> **Review Mode:** plan. **Current verdict:** approved. **Intent achieved:** yes, assessed for plan sufficiency; implementation remains unstarted. Round 1 required changes; both findings are closed by the round-2 recheck below.

## Intent Anchor

Session 68 adds a solid `redact` mark across every layer: the Annotation union and sidecar, the region-pass bake and its TS preview, the crop, the API, OpenAPI and MCP schemas, and a GUI Redact tool. The tool is Solid by default and has a Pixelate toggle. The session also renames Eraser to "Smart eraser" in the GUI, keeping the JSON type `eraser`.

## Scope

Reviewed the working-tree implementation plan and task for Session 68, MEU-103. This is ledger round 2, rechecking F1/F2 from `C:/Temp/av-kit/s68-plan-review-round-1.md` and checking the described corrections for new delivery failures. Claude Code/Anthropic authored the plan; this Codex independent reviewer did not. Applied PR-1 through PR-9, the Materiality Gate and Verdict Rule, with Mat's instruction to judge delivery substance. The initial findings remain below as historical round-1 records; the recheck explicitly closes them.

Read the complete current plan/task, the prior report, review template, relevant spec/grouping/MEU entries, corrected contracts and affected source/test guards. Inspected plan-local script logic and planning receipts; ran only the permitted scratch Python probe and two script selftests. Retained settled round-1 conclusions on unchanged surfaces without reopening approved Sessions 38–67 or supplied rulings. No repository file was edited. No product suite, build, package manager, pyright, baseline/session gate, network request or server was run. No prohibited file was opened. The coordinator owns the canonical report copy and ledger recording.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High | yes | behavior | Round 1: REDACT_TYPE scheduled the enum member without its explicit `to_wire` dictionary entry. The all-member wire assertion would raise KeyError in row 1, and the wire discriminator would remain broken. Violates AC-103, including REDACT_TYPE/REDACT_WIRE and AC-103.4. Confidence: High. Historical round-1 condition, closed in Round 2 below. | Round-1 task.md:73; implementation-plan.md:148; packages/core/src/avkit_core/domain/enums.py:258; tests/unit/test_domain_capture.py:129 | Add the member's explicit wire mapping in row 1 and retain the all-member assertion. | open |
| F2 | High | yes | behavior | Round 1: the pin inventory omitted AC-130.6's exact samples/Annotation-union equality. Adding the union member in row 3 without the redact sample would fail Green, where test edits are forbidden. Violates AC-130, specifically AC-130.6, triggered by REDACT_CLIP and AC-103.3/.6. Confidence: High. Historical round-1 condition, closed in Round 2 below. | Round-1 implementation-plan.md:171; task.md:75-76; tests/unit/test_domain_capture.py:864; tests/unit/test_domain_capture.py:876 | Add the redact sample in row 2; retain exact equality and per-kind kept/shift assertions, allowing the expected moved-pin failure before Green. | open |

## Q1 — Goal and end-to-end trace

Accepted: Solid GUI draw → explicit black redact payload → REDACT_API/domain validation → annotate/clamp → sidecar write/read → REDACT_BAKE → REDACT_PREVIEW; AC-103.16/.11/.4/.10/.8/.9/.21 cover these joins. MCP without colour forwards omission to the API's black default (.13/.11). Crop reaches `clip_mark`, sidecar serialization and bake through `services/capture.py:1620-1666`; export uses the saved annotated sibling through `:1731-1744`. AC-103.25 checks clipped/dropped sidecars, pixels and export. All five 09 Redact rows have work and AC coverage. F1/F2 no longer interrupt the planned sequence. No remaining goal gap found.

## Q2 — Tool retirement and type/enum pins

Accepted D-679: one Redact tool replaces the Pixelate tool; Pixelate remains a mode and annotation type. Existing callers, button maps, drawing, options and Electron clicks are scheduled to follow that change; the tool has no letter yet and no persisted mode. F1 is corrected in REDACT_TYPE and task row 1 (`implementation-plan.md:148,243,371`; `task.md:73`). F2 is explicit in the row-2 pin inventory (`implementation-plan.md:172`; `task.md:75`). The toolbar pin now expressly includes its TOOLS list, expectedGroups helper, eight-tool keys and icon. Appending types preserves the existing order. No additional count/order regression from these corrections found.

## Q3 — Mode precedence and history

Accepted unchanged MODE_GROUPS/MODE_SWAP: crop wins, then selected redaction kind, then an unselected Redact tool's mode, then Eraser/existing options. A selected pixelate therefore shows its mode/block controls even with Eraser active. A selected non-redaction mark exposes no mode control. Replacement keeps the index/box; `applyHistory` records one previous list (`CapturePage.tsx:713-722`); the checked-mode guard avoids a new history entry. AC-103.17/.18 prove precedence, swap, Undo and no-op behavior. No new issue introduced.

## Q4 — Half-open crop and assert-never

Accepted REDACT_CLIP and the independent test-local intersection oracle, including right/bottom touching edges and zero-size origins at excluded edges. The current inherited AC-130.6 explicitly compares the class sets and then every sample's carry/shift (`test_domain_capture.py:864-884`). The scratch recheck executes those unchanged assertions: seven samples fail against row 1's six-member union and pass against the planned seven-member union and clip arm. F2 is fixed without weakening the crop guard.

The unchanged assert-never probe requires a clean copy first and then exit 1 with exactly one diagnostic naming RedactAnnotation, Never and assert_never after removing the unique case arm. Its supplied three-toy receipt shows the positive and two refusals. No pyright invocation was made in this recheck. Crop/export reachability remains as in Q1; no separate export discriminator branch is missing.

## Q5 — Bake, preview and colours

Accepted unchanged REDACT_BAKE/REDACT_PREVIEW: paste RGB at alpha 255 into the shared half-open clip, in region-list order before drawn marks. The existing named-colour tables and hex handling agree between Pillow and TS; empty/outside boxes use the existing None/null guard. AC-103.8/.9/.21 cover opacity, untouched outside pixels, ordering, parity and editor preview. The revised dataclass staging changes validation timing, not these pixel rules. No new bake/preview conflict found.

## Q6 — API, MCP, sidecar and schemas

Accepted D-682: domain/API default black, explicit required stored colour, optional MCP colour forwarded unchanged. REDACT_API now expressly uses StrictInt for all four numbers (`implementation-plan.md:155`), matching the matrix's refusal of numeric strings/fractions while leaving earlier DTO contracts alone. REDACT_TYPE now translates non-string/empty-colour ValidationError to AnnotationValidationError; the scratch model confirms all seven probed bad-colour cases reach that class without printing their values.

OpenAPI changes remain the new schema and annotation-union/discriminator references. MCP's listed annotate schema grows, but tool/action identity does not; `mcp-server/tests/audit/baseline.test.ts:33-69` classifies tool/action/status deltas, not annotation-schema hashes. Its offline suite remains in scope; the live audit and baseline rewrite remain excluded. No path is planned to store an omitted or invalid redact colour.

## Q7 — Rename, outline, hit test and help

Accepted SMART_ERASER: optional hint extends the tooltip after name/shortcut, while aria-label stays the short name. The correction explicitly adds the eraser HINT_OVERRIDE to capture-page.behavior as well as icon-hints (`implementation-plan.md:175,177`), matching the actual assertion at `capture-page.behavior.test.ts:1509`. Other buttons have no new hint. REDACT_HIT now explicitly names BoxMark, isBoxMark and hitBody (`implementation-plan.md:163`), covering the existing body/handle guards. Original-only dashed SVG outlines, no Annotated/baked outlines, chip labels and help remain covered by AC-103.15/.19/.20/.22. No new mismatch found.

## Q8 — Type-only staging, Reds and moved pins

Accepted corrected staging (`implementation-plan.md:369-397`; `task.md:73,75-76`): row 1 adds the frozen fields/default without __post_init__, outside the Annotation union. It deliberately accepts bad values, so AC-103.2 can fail by DID NOT RAISE; row 3 adds validation and union/clip behavior. The wire mapping is required enum wiring in row 1. AC-103.1 now correctly expects capitalised `.value` and lowercase `.to_wire()`.

The required Red set remains pytest .2-.6/.8/.10/.11/.25, MCP .13, UI .14-.22 and Electron .24. Excluding .1/.7/.9/.12/.23 is justified by their staged roles. Assertion-first handling avoids missing-name, unexpected exception and locator-setup failures; the moved pins have their separate diagnostic receipt and must pass in Green. Both fresh detector selftests passed: red-check 49 fixtures, 0 wrong; id-length 4 cases, 0 wrong. No new staging contradiction found.

## Q9 — Fixtures and byte hash

Accepted unchanged REDACT_FIXTURE: append redact cases after crop_cases and compare every prior case's name/order/pixels plus unchanged PNGs before replacement. The original round-1 byte probe established the prefix SHA-256 `6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454`; both planned test-id edits remain after its boundary. That prior observation is carried forward, not represented as a fresh runtime/hash test. The round-2 corrections do not move either edit or introduce a CAPTURE_TOOL_PIXELATE reader. The separate action-row check remains required during execution.

## Q10 — Endings, identity, scope and records

Accepted byte-preserving existing endings and LF for new tests. F2's test file was already in the allowed set; the new pin adds no path outside scope. One clerical note: Files Modified still labels test_domain_capture.py row 1 only (`implementation-plan.md:305`); the pin table and task explicitly put AC-130.6 in row 2, so the intended edit is unambiguous. This is not a finding or delivery blocker.

The unchanged identity script binds product/tests/config/scripts/spec/status/runtime inputs, excluding named closeout artifacts; its supplied selftest reports 0 failures. Whole-tree identity was not run, avoiding reviewer-visible private untracked content. S11 still requires pre-status copies/diffs, only MEU-103 and grouping row 44/§9.1 changes, then render --check. Baseline rulings/queue/shapes remain source-bound preconditions; the supplied expected planning-time ruling refusal does not constitute product evidence or a new blocker. D-688's authority comes from Mat's supplied words. No new false-pass demonstrated.

## Q11 — Safety

Accepted the unchanged offline plan: generated images and tmp_path, in-process API clients, mocked MCP backend, Electron seams, scratch regeneration and ignored build outputs. Corrections add no network/YouTube/server call, secret read or new output destination. The validation translation uses fixed text rather than a refused colour. This recheck wrote only under C:/Temp/av-kit and ran no forbidden product command. Future implementation/test bodies still need execution review; no runtime safety certification is claimed.

## Checklist Results

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| PR-1 plan/task alignment | pass | Manual comparison of current contracts and rows 0-H2; observer codex-independent-reviewer | null | Same scope/order; F1 mapping and F2 row-2 sample agree across plan/task. |
| PR-2 unstarted confirmation | pass | Manual current task and MEU-103 inspection; observer codex-independent-reviewer | null | Implementation rows remain unchecked; MEU-103 remains pending. |
| PR-3 task contract | pass | Manual row/dependency/validation inspection; observer codex-independent-reviewer | null | Owners, deliverables, validation and ordered dependencies remain present; supplied r2 task lint reports OK, 24 rows. |
| PR-4 validation realism | pass | rtk proxy python C:/Temp/av-kit/s68/review/recheck-r2.py | 0 | Corrected enum mappings pass; unchanged inherited crop assertions fail before Green and pass after the planned additions. |
| PR-5 source-backed planning | pass | Manual trace to 09 five rows and grouping §9; observer codex-independent-reviewer | null | All goal layers and accepted decisions remain covered. |
| PR-6 corrections readiness | pass | Manual comparison of supplied correction list, prior F1/F2 and current affected clauses/tests; observer codex-independent-reviewer | null | Both findings addressed; secondary strict-input/hint/toolbar/hit-test guidance is explicit. |
| PR-7 scope discipline | pass | Manual unchanged exclusions and Files Modified/scope-set comparison; observer codex-independent-reviewer | null | No required behavior silently deferred or new edit path omitted. |
| PR-8 controls/reachability | pass | Manual receipt-detector, negative-probe and production call-chain inspection; observer codex-independent-reviewer | null | Corrected requirements remain testable; no new materially false-passing gate found. |
| PR-9 single-statement contracts | pass | Manual revised-clause comparison; observer codex-independent-reviewer | null | No conflicting behavioral restatement introduced. |
| Red detector selftest | pass | rtk proxy python docs/execution/plans/2026-11-13-capture-redact/red-check.py --selftest | 0 | 49 fixtures: 15 positive, 34 negative, 0 wrong. |
| Pytest-title boundary selftest | pass | rtk proxy python docs/execution/plans/2026-11-13-capture-redact/id-length.py --selftest | 0 | 4 cases, 0 wrong. |
| Product tests/builds/runtime gate | n/a | Not run under the explicit read-only review restrictions | null | Plan approval only. |

```json
{"schema_version":"evidence.v1","check_id":"s68-round2-correction-probe","command":"rtk proxy python C:/Temp/av-kit/s68/review/recheck-r2.py","cwd":"P:/av-kit","scope":"corrected enum mapping, type-only/Green validation staging and inherited AC-130.6 assertions","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"implementation-plan.md sha256 abab2c747e8aea79c44f69357e1c26d9314570a1b08a617908cd8abedb619d8b; task.md sha256 346cb3c390b9ae4493ce47b7993d6cc6c52621e8d13c94dada28b92948d33c08; scratch source models only","output":"F1: 7 members, all wire mappings pass, Redact value=Redact wire=redact. Row-1 stub accepts negative size and empty colour. Green validation model: 7 invalid-colour cases raise AnnotationValidationError. F2: unchanged exact set equality and per-kind kept/shift checks fail with union=6/samples=7 and pass with union=7/samples=7. No repository writes.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s68-round2-red-check-selftest","command":"rtk proxy python docs/execution/plans/2026-11-13-capture-redact/red-check.py --selftest","cwd":"P:/av-kit","scope":"plan-local Red receipt detector","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"round-2 working-tree red-check.py","output":"red-check selftest: 49 fixture(s) (15 positive, 34 negative), 0 wrong: []","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s68-round2-id-length-selftest","command":"rtk proxy python docs/execution/plans/2026-11-13-capture-redact/id-length.py --selftest","cwd":"P:/av-kit","scope":"plan-local pytest title-width boundary","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"round-2 working-tree id-length.py","output":"id-length selftest: 4 case(s), 0 wrong","fresh":true}
```

## Verdict

approved — the revised plan would deliver the registered goal. Both original delivery blockers are fixed, and the corrections introduce no demonstrated High/Critical failure. This approves the plan; it does not claim the feature has been implemented or the future session gate has passed.

## Recheck (Round 2)

Date: 2026-11-13. Workflow: /plan-critical-review recheck. Agent: codex-independent-reviewer.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| F1 | open | fixed |
| F2 | open | fixed |

### Confirmed Fixes

- F1: REDACT_TYPE schedules `AnnotationType.Redact = "Redact"` and its explicit `"redact"` wire mapping in row 1; AC-103.1 matches the enum's actual convention (`implementation-plan.md:148,243,371`; `task.md:73`). Scratch all-member mapping checks pass.
- F2: row 2 adds a valid RedactAnnotation sample to AC-130.6 and retains exact equality and per-kind carry/shift checks (`implementation-plan.md:172`; `task.md:75`). The inherited assertions pass with the planned union/clip additions and still fail before Green.
- Ancillary corrections: validation-free row-1 stub plus Green exception translation, StrictInt coordinates/extents, both eraser hint overrides, the toolbar expectation helpers/keys/icon, and explicit body/handle guards now match the prior review guidance. No AC was weakened.

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

### Verdict

approved. No new findings. The sole clerical row-label note is recorded in Q10 and does not block.

## Follow-up and Residual Risk

The coordinator should validate and copy this complete rolling report byte for byte to `.agent/context/handoffs/2026-11-13-capture-redact-plan-critical-review.md`, record the round-2 verdict, and proceed under Mat's existing execution authorization. Preserve the corrected inherited assertions and staging. No further planning correction or human decision is required by this review.

Residual risk is the unexecuted implementation: actual GUI mode/history/outline behavior, pixel parity, strict API refusal paths and the fresh full session gate remain execution obligations. No repository file was changed by this reviewer.
