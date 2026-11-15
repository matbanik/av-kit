---
date: "2026-11-14"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-14-capture-shapes-steps/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s72-execution-2026-11-14-capture-shapes-steps"
round: 1
---

# Critical Review: 2026-11-14-capture-shapes-steps

> **Review Mode:** execution
> **Verdict:** approved

## Scope

**Intent anchor:** “Session 72 adds the last three marks of the capture annotation synthesis.” The delivered work supplies Line and double-headed Arrow, Ellipse, numbered Step placement, and clamped Ctrl+D duplication while preserving the accepted capture contracts.

**Intent achieved:** yes.

**Target:** the uncommitted Session 72 delta on `main`, HEAD `5db36236dbdff78bc846bd4586206897c7e9be94`; both MEU-106 and MEU-107 handoffs and their shared plan/task. Claude Code, vendor Anthropic, authored the work; this reviewer did not. Applied execution-critical-review's Materiality Gate, IR-1 through IR-7, AV-1 through AV-6, and the supplied Q1–Q10. Accepted prior-session contracts and human decisions were not reopened.

**Write boundary:** only `C:/Temp/av-kit`. No repository files were edited. No test runner, build, session gate, live server, network call, system clipboard operation, package installation, or git mutation was performed by this review. H2, approval-state updates, commits, and pushes remain the coordinator's later work.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

## Q1 — Goal and end-to-end paths

**Accepted.** MCP's strict arrow/rect/step schemas join `captureSchema` (`mcp-server/src/toolsets/capture.ts:113`, `:200`, `:258`); the existing annotate route forwards the annotations as its POST body. `AnnotationIn` and `StepAnnotationIn` (`packages/api/src/avkit_api/schemas/captures.py:173`, `:187`) lead to `_annotations_from_in` (`routes/captures.py:160`, `:236`), validated domain marks, the clamp, wire serialization and sidecar. Read-back restores the new fields, `clip_mark` dispatches all three crop rules, and adapter dispatch reaches `_apply_arrow`, `_apply_rect`, and `_apply_step`. D-783's two trace halves pin equal literal bodies and real downstream behavior. The independent API probe additionally sent Both, Ellipse, and Step together and verified GET, sidecar, and decode/encode equality.

The UI follows the planned controls into pick-aware `createDrawnMark` (`CapturePage.tsx:361`), previews and history. Step placement runs after ARMED_EDIT and Text (`:1483`), selects under Lock, and derives its number from current marks. Ctrl+D follows the registry event to `duplicateSelected` (`:1278`), `duplicateMark`, history, and selection. AC-106.18–.25/.28 and AC-107.11/.13/.14/.18/.21/.24 cover this composition. Every goal bullet and both specification sections have implementation and behavioral evidence. **Not accepted:** no contrary delivery claim or missing goal rule was found.

## Q2 — HEAD_FIELD, SHAPE_FIELD and DEFAULT_OMIT

**Accepted.** The last-field additions retain positional compatibility. Domain checks reject unsupported values with constant field-level messages (`domain/capture.py:311`, `:338`); wire readers validate explicit values and default missing ones, while writers conditionally append only non-default keys (`services/capture.py:364`, `:374`, `:467`, `:480`). API per-field `exclude_if` preserves unrelated output fields. The old sidecar fixture pins byte equality; the independent probe verified default round trips, all allowed choices, and empty/control/surrogate/wrong-case/integer/null rejection. HTTP probes received the exact sanitized 422 envelope and retained the prior marks after rejected writes. HEAD_CLIP preserves all three head choices through `replace`.

**Not accepted:** raw Pydantic diagnostics are not treated as the public response contract; the tested HTTP error envelope is the applicable boundary. No default leakage or public refused-value echo was found.

## Q3 — Heads, ellipse, preview, hit testing and crop

**Accepted.** HEAD_BAKE and HEAD_PREVIEW mirror the same span and head geometry, including no shaft when Both's pullbacks overlap. The fixture is checked independently in Python and TypeScript; rendered tests check head counts and shaft coordinates. HEAD_HIT uses only the chosen triangles. The reviewer independently reproduced both baseline RGB-byte hashes: End arrow `af685c76ffcd76beed861e6cd79175d1222b97fa0fb9ebcd27064518661ba3fe`; Rect `9ce84cf453ac76c5407e9a1a3d40e368ee42e8e1a9de784f473bed70c02a89fd`.

ELLIPSE_BAKE uses the approved Pillow box/width, and ELLIPSE_PREVIEW uses its box geometry. ELLIPSE_HIT measures CSS distance to the sampled outline, including thin and degenerate cases, instead of normalized-radius error. Existing spread-based resize preserves `shape`; the rendered resize test checks it through Save. `_clip_ellipse` (`domain/capture.py:595`) uses exactly D-676's closed-crop inequalities. Reviewer probes included touching, one-past, and negative-side cases. **Not accepted:** no regression in End/Rect bytes, head carry, ellipse resize, or keep/drop semantics was found. Pixel-level SVG/Pillow antialiasing equality is not claimed by the approved contracts.

## Q4 — Step at the boundaries

**Accepted.** STEP_TYPE, STEP_WIRE, STEP_API, STEP_MCP and STEP_ZOD align on nonnegative integer coordinates, number 1–999, size 12–200, and the named/hex annotation colors. Python explicitly rejects bool and non-int values; HTTP uses StrictInt/StrictStr; Zod rejects noninteger numbers and other types. Wire/API/MCP/UI schemas refuse extra keys. Independent wire/API probes checked bool, float, string and null across every numeric field; HTTP probes also checked extra keys and range failures without exposing their values.

STEP_CLAMP uses the existing text-anchor clamp. STEP_CLIP uses half-open centre membership, distinct from the ellipse's closed box rule. The stored `s72-D6-never-probe.txt` shows unchanged scratch copies passing and each removed Step branch producing exactly the expected Step-to-Never error. Its seven-case detector selftest passed independently. `openapi-delta.py` and its eight-case selftest passed, and `export_openapi.py --check` exited 0. **Not accepted:** no silently dropped type or unplanned OpenAPI change was found.

## Q5 — STEP_BAKE, STEP_CENTRE and STEP_PREVIEW

**Accepted.** Python and TS use the same radius, digit-dependent font size, integer baseline rounding, sRGB conversion, and strict `luminance > 0.179` comparison (`adapter.py:192`, `:206`; `capture-step.ts:16`, `:31`). Both fixture tests pin all 12 size/number pairs. The reviewer independently rendered all 12, measured horizontal/vertical ink-box centring, and checked every detected ink pixel lay inside the disc; all passed. The rendered preview tests check circle, number, anchor, baseline and contrast; the recorded real Electron test measures browser horizontal centring. Annotated export, copy-image bake and flatten each have a service-to-real-adapter assertion and a disc pixel assertion (AC-107.23).

**Not accepted:** no missing export path or layout/contrast mismatch was found. A fresh browser run was not performed; browser evidence is the matching-state recorded Electron run. The approved preview vertical contract is shared baseline geometry, not an additional browser ink measurement.

## Q6 — STEP_STYLE and preserved style contracts

**Accepted.** The service, API, MCP, and UI leaves carry the approved defaults and types. API/service validation enforces the size range; the named 401-digit/4301-digit outcomes were independently verified as 422/400. Step commits use the existing `saveCaptureToolStyle` → `commitLeaves` queue and `latest` merge; the held/failing GET tests exercise real page/store behavior. `readToolStyles` supplies fallback defaults for each bad stored Step leaf in AC-107.17. Partial PUT probes confirmed Step changes preserve the other style and Lock leaves.

`styleToolFor`, `styleToolOfMark`, and option precedence extend Step without changing the existing tool rules. Selected-mark changes remain local history operations. **Not accepted:** no claim that the unchanged settings service repairs every corrupt database string was needed; AC-107.17 proves UI read-back fallback for its specified leaves. No stale-GET overwrite, lost style, or lost Lock defect was found.

## Q7 — Controls, placement, labels and Lock

**Accepted.** SHAPE_OPTIONS shows selected-mark values or the mount-local pick, changes a selected mark as one undo step, and sends no settings PUT. `createDrawnMark` omits the default fields. `LetterTool` narrows the mapping to the same eight lettered tools; Step has the specified position, icon and hint, and no letter. ARMED_EDIT precedes STEP_PLACE, so the selected badge moves under Lock. Placement rounds/clamps its centre, a drag adds no extra badge, and max-plus-one handles gaps and Undo. Placement stops at 999 without applying history. STEP_HIT scales the image radius and adds fixed CSS padding; labels distinguish per-kind Line/Ellipse counts and Step's own number.

**Not accepted:** no failed placement/selection/numbering rule was found. D-784's optional list argument preserves existing two-argument labels for existing mark kinds; the viewport opts into the new per-kind counts.

## Q8 — DUPLICATE

**Accepted.** The registry entry is page-scoped, stateful, chord-only and absent from RESERVED_CHORDS. Published state, the page focus/modal checks, and `gestureRef` prevent duplicate actions from disabled contexts. The actual shortcut-handler tests verify the hex-field chord is consumed without copying. Scrub pointer-down focuses its input, which the same focus guard excludes. The copy uses extent-aware nonnegative displacement, with the closed Rect bound and half-open filled-box bound distinguished (`capture-shapes.ts:35`). It preserves fields, clamps the offset, selects the copy, sends no PUT, and adds one undo step.

Step copying uses the current list's next number and refuses 1000 while preserving list/selection/history; non-Step copies still work beside 999. The edge matrix and exhaustion cases address plan-review F1/F2, and HEAD_HIT/ELLIPSE_HIT tests address F3/F4. Chord-table/audit migrations reflect the actual registry. **Not accepted:** no off-image offset, duplicated number, focus bypass or extra duplicate undo step was found.

## Q9 — Test rigor and moved pins

**Accepted.** All 34 AC-106 rows and all 30 AC-107 rows have handoff coverage and corresponding code/test/check evidence. The reviewer read all six new test files, both appended Electron tests, the MCP additions, and every changed existing-test hunk. All 45 required Red IDs pass `red-check.py` against the four original nonzero-exit receipts: `4 receipt(s), 45 required test(s), 0 problem(s)`. Detector selftests also pass; no runner was re-executed.

IR-5 grading below applies to every new case within each named group. Existing test edits preserve exact assertions and extend their expected sets/tables; no removed behavioral assertion or skip/xfail masking was found.

| Test file or group | Grade | Reason |
|---|---|---|
| `tests/unit/test_capture_shapes.py` behavioral cases | Strong | Exact round trips, baseline hashes, head pixels/vertices/spans, crop outcomes and preserved fields; signature cases Adequate. |
| `tests/unit/test_capture_step.py` behavioral cases | Strong | Explicit invalid values, key order, crop boundaries, ink geometry and service export pixels; signature cases Adequate. |
| `tests/e2e/test_api_capture_shapes.py` | Strong | Real SQLite/API stack, exact response/sidecar contents, immutable prior marks on refusal, domain recording and bake pixels. |
| `tests/e2e/test_api_capture_step.py` | Strong | Real stack, strict refusals, persistence, settings bounds, trace and crop sidecars. |
| `ui/tests/unit/capture-shapes.test.ts` | Strong | Exact schema outcomes, fixture parity, outline/head hit cases, registry semantics and labels; declaration-only checks Adequate. |
| `ui/tests/unit/capture-shapes.behavior.test.ts` main cases | Strong | Real page/store/registry over a recording transport; saved payloads, history, selections, edge copies, 999, stale/failing GET and focus guards. |
| Same file: AC-106.31, AC-107.27, AC-107.29 | Adequate | Preservation guards intentionally tolerate pre-feature controls; complementary .19/.20 and .16 tests require those controls and real commits. No sole feature proof relies on the conditional branches. |
| `mcp-server/tests/capture.test.ts` additions | Strong | Strict schema outcomes, actual tool handler with recording transport, exact POST bodies and key order. |
| `ui/tests/e2e/capture-inbox.test.ts` additions | Adequate | Real compiled Electron interactions and saved values, plus measured horizontal badge centring; detailed bounds/history are asserted by the page tests. |
| Existing Python enum/clamp/settings pins; UI toolbar/style/lock/redact/hint/help pins; chord fixture | Strong for changed assertions | Expected sets, defaults, ordering and behavior matrices remain explicit and gain the planned entries. |
| `tests/e2e/test_api_capture_tool_lock.py` historical delta pin | Strong | Still pins MEU-143's exact historical delta; current snapshot equality and Session 72 delta are independently pinned elsewhere. |

D-785 inserts the required Duplicate sentence between the same two ordered help sentences. D-788 changes the historical snapshot endpoint and retains the exact `tool_lock` delta assertion; the current snapshot remains checked. D-786's pure/rendered split preserves both proofs. D-787's Python union position has no additional order-dependent production reader. **Not accepted:** no weak test that substitutes for required behavior proof, unreported test weakening, or dropped AC was found.

## Q10 — Freshness, records and safety

**Accepted.** The independently recomputed state is exactly:

`5db36236dbdff78bc846bd4586206897c7e9be94+af02bc49a48e1af1202e8293cf57440dbc19d948d2d9b5a4f8f9f2c2b4a9691c`

The review cleared ELECTRON_RUN_AS_NODE and supplied a scratch git exclude for `.claude/settings.local.json`, without opening it. The first attempts encountered sandbox cache/ownership restrictions; redirecting uv's cache to scratch and supplying process-local `safe.directory=P:/av-kit` enabled the unmodified identity script. Neither adjustment changes its hashed runtime inputs. The resulting value matches both handoffs and both gate identities.

The gate source preserves each exit and stops on failure. All 23 recorded steps report exit 0, no baseline failures are excused, and the gate ends `session-gate: all steps exit 0`. Its step receipts corroborate the handoffs' full-gate records:

| Suite | Baseline | H1 gate |
|---|---|---|
| Python | 2630 | 2781, 37 warnings |
| UI | 1423 in 128 files | 1532 in 130 files |
| MCP | 530 in 36 files | 535 in 36 files |
| Capture Electron | 51 | 53 |

The nine evidence.v1 records in each handoff are internally consistent with the described staged work and inspected Red/Green/gate/closeout receipts. Intermediate row-2 and Red failures are explicitly disclosed; they are not represented as product-suite passes. The reviewer recomputed AC-51.6 as `6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454` and independently checked original test-id lines are preserved. All 52 measured anchor files retain their recorded line-ending kind. The pre-status comparisons contain only MEU-106/107 lifecycle/plan/date fields, their rendered records, and row 48's band/status/plan plus its section band. The two Delivered notes and actions-index additions describe actual code.

New tests use generated images and temporary databases or recording/fake transports. Reviewed error responses are sanitized; marks are not added to new logs. Export/copy-image bake tests render bytes without writing the system clipboard. The explicitly excluded clipboard specs and live MCP audit were not run. **Not accepted:** no freshness mismatch, unrelated status change, unsafe new test path or false success claim was found. H2 omissions and pending reviewer-status fields are deliberate and do not block this review.

## Checklist Results

| Check | Result | Observation |
|---|---|---|
| IR-1 live integration evidence | pass | Real API/SQLite integration tests and matching-state Electron receipts; independent in-process API probe also passed. |
| IR-2 fake behavioral compliance | pass | Recording transports maintain saved marks/settings; held GET uses its original snapshot, enabling the stale-read check. |
| IR-3 error mapping | pass | New malformed mark bodies return the exact 422 envelope; known huge-integer settings parser boundary remains 400. |
| IR-4 fix generalization | pass | Plan-review bounds, exhaustion, ellipse-distance and head-hit corrections appear in code and decisive tests. |
| IR-5 assertion strength | pass | Per-group grading above; no Weak sole acceptance proof. |
| IR-6 boundary validation | pass | Strict domain/API/wire/Zod paths with positive, negative, extra-key and preservation checks. |
| IR-7 AC and deferral integrity | pass | 34 + 30 AC rows covered; disclosed exclusions match accepted scope; H2 is after this review. |
| AV-1 through AV-6 | pass | Required Red assertion evidence, behavioral Green evidence, preserved assertions, no masking/stubs, and sourced criteria. |
| Fresh full-gate evidence | pass | Exact current-state match, original step receipts and declared counts; no full-suite rerun. |
| Repository write boundary | pass | Only reviewer artifacts/probes under C:/Temp/av-kit; identity remains unchanged. |

### Independent evidence

Commands below ran from `P:/av-kit` through `rtk proxy`, with all streams captured, the child exit preserved, PYTHONDONTWRITEBYTECODE=1, and TMP/TEMP and uv cache under `C:/Temp/av-kit/s72/exec-review-tmp`. The probe scripts are retained there for reproduction. Commands/procedures and decisive outputs are embedded here, rather than relying on receipt paths alone.

```json
{"schema_version":"evidence.v1","check_id":"review-current-identity","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s72-review-state.ps1 (runs uv run --no-sync python -B docs/execution/plans/2026-11-14-capture-shapes-steps/identity.py --state-only with ELECTRON_RUN_AS_NODE unset and the documented local-settings exclude)","cwd":"P:/av-kit","scope":"complete D6 input identity","phase":"static","exit_code":0,"result":"pass","tested_state":"5db36236dbdff78bc846bd4586206897c7e9be94+af02bc49a48e1af1202e8293cf57440dbc19d948d2d9b5a4f8f9f2c2b4a9691c","output":"5db36236dbdff78bc846bd4586206897c7e9be94+af02bc49a48e1af1202e8293cf57440dbc19d948d2d9b5a4f8f9f2c2b4a9691c"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-independent-behavior","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s72-review-probe.ps1 (runs uv run --no-sync python -B C:/Temp/av-kit/s72/exec-review-tmp/reviewer_probe.py)","cwd":"P:/av-kit","scope":"domain/wire/API/crop/bake/settings; generated scratch images and isolated SQLite TestClient","phase":"targeted","exit_code":0,"result":"pass","tested_state":"5db36236dbdff78bc846bd4586206897c7e9be94+af02bc49a48e1af1202e8293cf57440dbc19d948d2d9b5a4f8f9f2c2b4a9691c","output":"reviewer-probe: 188 assertions passed; domain/wire/API/crop/bake/settings; isolated scratch only"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-red-schema-record-controls","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s72-review-controls.ps1 (runs reviewer_controls.py; extracts the exact 45 --require IDs from task row 3; runs red-check, four allowed selftests, openapi-delta, export_openapi --check and meu_status render --check; compares the four pre-status copies)","cwd":"P:/av-kit","scope":"original Red evidence, exact schema additions and lifecycle records","phase":"static","exit_code":0,"result":"pass","tested_state":"5db36236dbdff78bc846bd4586206897c7e9be94+af02bc49a48e1af1202e8293cf57440dbc19d948d2d9b5a4f8f9f2c2b4a9691c","output":"red-check: 4 receipt(s), 45 required test(s), 0 problem(s); selftests: red-check 71/0 wrong, id-length 4/0, assert-never-probe 7/0, openapi-delta 8/0; openapi-delta: pass; export_openapi --check exit 0; Drift check passed; test-id original lines preserved True; pre-status diff confined to the two MEUs and grouping row 48; reviewer-controls: pass"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-bytes-gate-ac-audit","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s72-review-audit.ps1 (runs uv run --no-sync python -B C:/Temp/av-kit/s72/exec-review-tmp/reviewer_audit.py)","cwd":"P:/av-kit","scope":"baseline bake bytes, hash boundary, anchor endings, AC coverage and original gate receipts","phase":"targeted","exit_code":0,"result":"pass","tested_state":"5db36236dbdff78bc846bd4586206897c7e9be94+af02bc49a48e1af1202e8293cf57440dbc19d948d2d9b5a4f8f9f2c2b4a9691c","output":"anchor line endings preserved: 52; AC-51.6 hash 6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454; baseline End/Rect bake hashes match; handoffs: 34 and 30 AC rows, 9 evidence records each, gate matches current state True; all 23 gate steps exit 0; reviewer-audit: pass"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-manual-code-and-tests","procedure":"Read the supplied execution review contract, both work handoffs, plan contracts/ACs/decisions and task; inspect all modified source/test hunks and six new test files; trace the MCP/API/persistence/crop/bake and UI/tool/history/style paths; compare published claims with the named original receipts and grade the acceptance assertions as recorded in Q1-Q10.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"Session 72 uncommitted delta and preserved capture contracts","phase":"targeted","exit_code":null,"result":"pass","tested_state":"5db36236dbdff78bc846bd4586206897c7e9be94+af02bc49a48e1af1202e8293cf57440dbc19d948d2d9b5a4f8f9f2c2b4a9691c","output":"All four goal bullets are implemented with behavioral evidence; 64 ACs accounted for; D-783 through D-788 preserve intent; no evidence-backed material product defect found."}
```

## Verdict

**approved** — the delivered work achieves the registered intent. There are no findings requiring correction and no Critical or High defects identified. Recorded full-suite/Electron evidence is accepted only for the exactly matching tested state; this review's fresh execution was limited to the permitted independent probes and read-only checks. No new human decision is required by this verdict.
