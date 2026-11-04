---
date: "2026-08-26"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-08-26-p8-conversion-api-mcp/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.1"
requested_verbosity: "standard"
agent: "gpt-5.6-sol"
round: 4
---

# Critical Review: p8-conversion-api-mcp

> **Review Mode**: `plan`
> **Verdict**: `approved`

## Intent Anchor

Executing this plan is supposed to deliver Session 14 only: MEU-31's complete `/api/v1/conversions*` REST/settings/OpenAPI contract followed by MEU-32's REST-parity `avkit_convert` MCP tool, using the approved MEU-28–30 engine and excluding MEU-33, Session 15, and Session 8c. The current plan would not reliably deliver that objective because one API response contract is an unsupported planner choice and the FIC can false-pass implementations that omit Spec-required kind-specific conversion options.

---

## Scope

**Targets reviewed:**

- `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/implementation-plan.md`
- `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/task.md`
- `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/named-sets.json`
- `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/assert-red-oracle.ps1`
- `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/assert-handoff-markers.ps1`
- `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/assert-handoff-acs.ps1`

**Authority checked:** `docs/build-plan/08-video-conversion.md` §REST + §MCP; Phase 4 downloads/settings/wiring/error/formatter canon; Phase 5 `mcp-server/src/toolsets/`, registry, destructive gate, and settings canon; Session 14/15 grouping; MEU SSOT; approved MEU-28–30 engine surfaces; harness override; quality-gate contract.

**Scope lock applied:** MEU-31 then MEU-32 only. MEU-33 / Session 15 / Session 8c were treated as out of scope. The create-plan §4A skip and `fresh_worker: none`/no-`isolated` rows are correct. The absent `tools/validate_closeout_artifacts.py` is intentional; the existing named scripts plus `tools/check_exec_review.py` were reviewed as the selected closeout surface.

**Checklist applied:** IR + DR + PR, including C2, PR-8, and PR-9.

---

## Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|
| P8AM-001 | High | High | **The unprobed GPU response is an unsourced contract that conflicts with the Spec-owned VO.** The Spec defines `GPUCapabilities.recommended_encoder` as non-null `str`, has no `probed` field, and says the session is empty until first detection, with page mount or `GET /conversions/gpu` named as a trigger. The plan instead freezes a sentinel object with `probed:false` and `recommended_encoder:null`, requires GET never to call `detect_gpu`, and asserts `probed=true` after refresh. The cited FastAPI issue is a report about nullable OpenAPI schema generation; it does not recommend a sentinel object. This leaves materially different response/OpenAPI behaviors unresolved while the plan says no human review is required, violating PR-5 and the Spec Sufficiency Gate. | `docs/build-plan/08-video-conversion.md:235-250,447`; `implementation-plan.md:69-78,110-111,168-169,192,379-386`; `named-sets.json:45-54` | Resolve the contract from canonical authority or a human decision: define the exact unprobed body and whether GET performs first-use detection, then make `GPUCapabilitiesOut`, named sets, AC-31.3/31.4, and control bindings consistent. Do not use FastAPI #5120 as normative support for the sentinel choice. | open |
| P8AM-002 | High | High | **The REST/MCP FIC can false-pass materially incomplete kind-specific create wiring.** Spec requires compress overrides `cq`, `scale_height`, `audio_mode`, and `gpu_preference`; cut `copy_mode`; and extract `stream_index`. The REST Boundary Inventory and AC-31.1/31.13 prove kind/preset and shape rejection but never assert that those optional fields are accepted, mapped to the domain enums, and forwarded in the exact `ConversionAddSpec`. The MCP Boundary Inventory says “add fields match REST wires,” but AC-32.1–32.3 prove census/path/strictness, not acceptance and forwarding of each kind-specific field. An implementation that supports only `{paths, kind, preset}` at REST and a minimal add body at MCP can satisfy every stated AC while violating Spec and M2 parity. This is a demonstrated PR-4/PR-8 false-pass of required behavior. | `docs/build-plan/08-video-conversion.md:461-469,494-513`; `implementation-plan.md:90,152-160,164-183,236-257`; `named-sets.json:26-43,87-100` | Expand the Boundary Inventories and FIC with positive and negative assertions for every kind-specific field. At REST, spy on the exact `ConversionAddSpec` for non-default compress, cut, and extract requests. At MCP, prove the same fields survive strict Zod parsing and are forwarded unchanged to the REST body, including wrong-kind rejection. Bind those assertions to the Red oracle titles. | open |
| P8AM-003 | Medium | High | **The planned MEU/H1 gates omit blocking quality checks.** MEU-32 runs `tsc`, Vitest, and build but never ESLint. The plan lists anti-placeholder/G36 `rg` commands, and task row 3 claims that check, but no task validation cell actually executes the anti-placeholder or anti-deferral scans for the API/MCP changes. The quality-gate skill classifies TypeScript lint and both placeholder scans as blocking. | `task.md:46,49,54,66`; `implementation-plan.md:364-373`; `.agent/skills/quality-gate/SKILL.md:44-55` | Add redirected, exit-propagating ESLint plus anti-placeholder/anti-deferral receipts to the applicable MEU gates and H1 closeout. Handle `rg` exit 1 as a clean zero-hit result and >1 as an error. | open |
| P8AM-007 | Medium | High | **Several validation failure branches violate the P0 exit-preservation contract.** Task row 3 checks `$LASTEXITCODE`, reads the receipt, and only then exits with `$LASTEXITCODE`; the Red-oracle branches repeat that shape after invoking the helper. P0 requires saving the native exit code immediately before any `Get-Content` or other command. This is a verification/portability defect, not an additional delivery-level blocker. | `task.md:44,46-47`; `implementation-plan.md:331-334,358-362`; `AGENTS.md` §Windows Shell — Mandatory Redirect-to-File Pattern | After every native process/helper invocation, assign `$code=$LASTEXITCODE` immediately; use `$code` for the branch and final `exit`, including after `assert-red-oracle.ps1`. | open |
| P8AM-004 | Low | High | **The exact `confirm_required` oracle is not reachable through the stated Local Canon schema shape.** The plan says destructive branches use required `confirm: z.literal(true)` and also requires missing `confirm` to reach `confirmMissing` and return code `confirm_required`. In the live toolsets, required literal validation runs before `confirmMissing`, so missing confirm returns `validation_error`; M3 only requires `confirm:true` and no fetch. This is clerical/internal predicate drift, not a product-safety gap. | `implementation-plan.md:242,251,257,272-275`; `mcp-server/src/toolsets/registry.ts:202-213`; `mcp-server/src/toolsets/download.ts:86-87`; `docs/build-plan/05-mcp-server.md:84-95` | Choose one contract and state it once: either make the literal optional so runtime `confirmMissing` owns the exact code, or retain required `z.literal(true)` and assert generic TOOL_ERROR plus fetch count 0. | open |
| P8AM-005 | Low | High | **PR-9 named thresholds/state sets are restated outside `named-sets.json`.** The plan repeats `48 + 13 = 61`, `46 + 13 = 59`, and “59 / 7 tools”; task row 4 restates KEEP 46; the stream-mode lock repeats `first/all`. These are clerical stale-clause risks because the executable owner is otherwise clear. | `named-sets.json:43,56-58,75-85`; `implementation-plan.md:88-89,108,291`; `task.md:47` | Replace repeated numeric/state literals with `ROUTE_COUNT_*`, `ACTION_INDEX_*`, `COMPOUND_TOOLS_AFTER`, and `STREAM_MODES` references. | open |
| P8AM-006 | Low | High | **C2's Downloader→Convert deferral has the wrong destination label.** The Spec calls it a named integration deferral “not this phase's GUI,” and registered MEU-33 covers the Convert GUI rather than reopening MEU-20. The row is substantively excluded from Session 14, so this is clerical under PR-7 rather than disguised skipped work. | `implementation-plan.md:296-307`; `docs/build-plan/08-video-conversion.md:535-543`; `.agent/context/meu-status.yaml:886-908` | Mark it `out-of-scope` with no deferred-to MEU, or cite a new Human-approved/SSOT assignment before naming MEU-33. | open |

### Severity Summary

| Critical | High | Medium | Low |
|---:|---:|---:|---:|
| 0 | 2 | 2 | 3 |

---

## Checklist Results

### Information Retrieval (IR)

| Check | Result | Evidence |
|---|---|---|
| All AC have supported source labels | fail | Labels exist, but AC-31.3/31.4's sentinel `probed` contract is not supported by the cited FastAPI issue and conflicts with the Spec VO shape (P8AM-001). |
| Validation cells are exact and complete | fail | Existing commands are concrete and referenced executables exist or are scheduled, but blocking ESLint and placeholder/deferral scans are not bound to task gates, and several failure branches do not preserve native exit status before receipt reads (P8AM-003/007). |
| BUILD_PLAN audit row present | pass | Task row 7 binds MEU-31/32 and phase 8 to `PLAN_FOLDER`, preserves the engine slash, and sets `HUB_NEXT_AFTER`. |
| Post-MEU rows present | pass | H1 handoff/review barrier and H2 reflection/metrics/commit-draft rows are explicit and sequential. |

### Design Review (DR)

| Check | Result | Evidence |
|---|---|---|
| Naming convention followed | pass | Plan folder, MEU handoffs, rolling implementation review, reflection, and metrics slug are consistent. |
| Template version present | pass | Plan `2.0`; task and review `2.1`. |
| YAML frontmatter well-formed | pass | Required fields are present. `task.md` says `in_progress`, but every task remains unchecked and all planned new implementation artifacts are absent; review mode is still unstarted plan. |
| Spec/local-canon cross-references | fail | REST/MCP field-forwarding obligations are not converted into complete FIC assertions, and GPU sentinel behavior is not supported by its cited authority. |

### Plan Review (PR)

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Both preserve MEU-31 Red→Green→gate, then MEU-32 Red→Green→gate, H1 review, and H2 closeout. |
| PR-2 Not-started confirmation | pass | All 20 actionable rows are `[ ]`; both planned source modules, both new test files, both MEU handoffs, implementation review, and reflection are absent. MEU-31/32 remain `pending` in SSOT. |
| PR-3 Task contract completeness | pass | Every actionable row supplies task, owner, deliverable, exact validation, dependency, context strategy, durable output, builder model, and status. |
| PR-4 Validation realism | fail | Required kind-specific input forwarding can false-pass; mandatory quality checks are not all scheduled; several failure branches violate P0 exit preservation (P8AM-002/003/007). |
| PR-5 Source-backed planning | fail | The GPU sentinel object/`probed` contract is an unsupported product decision (P8AM-001). Official Pydantic documentation does support discriminated unions; that choice is sound. |
| PR-6 Handoff/corrections readiness | pass | Two named MEU handoffs and one rolling implementation review are explicit; helper scripts and `tools/check_exec_review.py` exist. Round-2 census rules are not applicable to this Round 1 review. |
| PR-7 Scope discipline / C2 | pass with Low correction | MEU-33, Session 15, and Session 8c remain excluded. One named integration deferral is mislabeled as MEU-33 but does not hide current-session work (P8AM-006). |
| PR-8 Control reachability/totality | fail | Positive field-forwarding observables are missing for required create options; the exact confirm-error chain is internally inconsistent (P8AM-002/004). Other named chains—GPU counter, path precheck, start conflict, settings 422, list envelope—are reachable. |
| PR-9 Single-statement discipline | fail (Low) | Executable ownership is centralized in `named-sets.json`, but several thresholds and `STREAM_MODES` are restated in prose/task rows (P8AM-005). |

---

## Referenced-Artifact Existence

The selected pre-existing executables and templates all exist: `.agent/context/handoffs/TEMPLATE.md`, `.agent/schemas/reflection.v1.yaml`, `tools/export_openapi.py`, `tools/check_exec_review.py`, `tools/Invoke-CodexDispatch.ps1`, `tools/meu_status.py`, the three plan helper scripts, OpenAPI, existing API tests, and existing MCP census/confirm tests. `tools/validate_closeout_artifacts.py` is absent exactly as the plan states. Planned new routes, schemas, tests, MEU handoffs, implementation review, and reflection are absent, confirming unstarted execution.

---

## Commands Executed

Static review only. All shell work used RTK or `rtk proxy pwsh`, redirected every process stream to `C:/Temp/av-kit/`, captured exit status before receipt reads, and ran no project tests or project scripts.

- Full line-numbered reads of the six target-folder artifacts.
- Full/targeted reads of the Phase 8 REST/MCP SSOT, Phase 4 API canon, Phase 5 MCP canon, engine enum/service surfaces, grouping/MEU SSOT, harness controls, quality-gate skill, workflow, review template, and peer exemplar.
- `Test-Path` inventories recorded in `C:/Temp/av-kit/review-artifact-existence.txt` and `C:/Temp/av-kit/review-unstarted-existence.txt`.
- Exact `AppServices(` census in `C:/Temp/av-kit/review-appservices-census.txt`; all six live constructors are named by `APPSERVICES_SITES`.
- PR-9 censuses in `C:/Temp/av-kit/review-pr9-48.txt`, `review-pr9-61.txt`, `review-pr9-46.txt`, `review-pr9-59.txt`, and `review-pr9-stream-modes.txt`.
- Control/source censuses in `review-kind-options-census.txt`, `review-confirm-chain-census.txt`, `review-grouping-census.txt`, and `review-meu-status-numbered.txt`.
- Primary-source web check of [Pydantic discriminated unions](https://docs.pydantic.dev/latest/concepts/unions/), [Pydantic configuration](https://docs.pydantic.dev/latest/api/config/), and [FastAPI issue #5120](https://github.com/fastapi/fastapi/issues/5120).

Attempted scoped `git status` could not run because `P:/av-kit` is not a Git worktree (`fatal: not a git repository`); this did not affect read-only file-state verification.

No pytest, Vitest, OpenAPI export, repository tool under `tools/`, plan helper script, lint, type check, build, product code, test, plan, or unrelated handoff was run or modified.

---

## Open Questions / Assumptions

1. Which source-backed unprobed GPU behavior governs: a nullable 200 body, a sentinel object, or first-use detection on GET? The current Spec/citation set does not resolve the exact response schema.
2. Is the exact missing-confirm code part of the desired MCP contract, or is M3's generic TOOL_ERROR/no-fetch behavior sufficient? This is nonblocking once stated consistently.

No question remains about scope: Session 14 is MEU-31 then MEU-32 only.

---

## Required Follow-up

Use `/plan-corrections` to resolve P8AM-001 through P8AM-007. At minimum, the correction pass must resolve the GPU contract and add source-backed REST/MCP acceptance criteria that prove every Spec-required kind-specific create option is accepted and forwarded. It should also bind the blocking quality checks, repair P0 exit preservation, and consolidate the Low named-set/C2/confirm drift. Round 2 must include the PR-6 blast-radius census receipt and a per-hit disposition log.

---

## Verdict

`changes_required` — P8AM-001 and P8AM-002 are evidence-backed High findings: the plan freezes an unsupported GPU response contract and can false-pass REST/MCP implementations that omit required kind-specific conversion inputs. The Session 14 scope/order, no-GUI skip, harness strategy, helper-script existence, and named closeout approach are otherwise coherent.

---

## Residual Risk

This was a static unstarted-plan review under the user's no-execution constraint. Runtime correctness, OpenAPI generation, Red-oracle behavior, API/MCP test results, lint/type checks, and closeout scripts remain unverified until execution. No product or plan files were changed.

---

## Corrections Applied — 2026-08-26 (create-plan Step 5b / plan-corrections)

**Corrector:** coordinator (not the reviewer). Verdict set to `corrections_applied` only. Independent Round 2 must re-score. Product code, tests, and `docs/build-plan/` were not modified.

**Instruction conflict (flagged, not silently picked):** `plan-corrections.md` HARD STOP says timestamp-and-stop and do not auto-chain into `/plan-critical-review`. Driving workflow is `/create-plan` Step 5b (`plan_to_exec_gate: reviewer-auto` in `.agent/context/harness.local.md`), which requires re-dispatch after the census. Re-dispatch proceeds under create-plan. `named-sets.json` is not listed in `plan-corrections.md` Write Scope; it is a create-plan Step 4 plan-folder artifact and was updated as such.

**Second conflict:** `.agent/skills/quality-gate/SKILL.md` lists ESLint as blocking; `mcp-server` has no eslint script/config and p5 shipped on `npx tsc --noEmit`. Plan lock: `MCP_ESLINT: null`, gate is `MCP_TS_GATE`. Anti-placeholder/G36 `rg` is bound to MEU-31/32 gates and H1-2.

### Finding dispositions (corrector claims; not an `approved` verdict)

| # | Change | Files |
|---|--------|-------|
| P8AM-001 | Withdrew unprobed sentinel. Lock `GPU_LAZY_GET`: empty session first GET → `detect_gpu()` once; later GET → `get_gpu()` only; always 200 `GPUCapabilitiesOut` matching domain VO (non-empty `recommended_encoder: str`, no `probed`). POST `/gpu/refresh` always re-probes. Spec 250+447. FastAPI #5120 withdrawn as GPU authority. AC-31.3/31.4 rewritten. | named-sets.json; implementation-plan.md |
| P8AM-002 | Added AC-31.19–21 (spy `ConversionAddSpec` for `COMPRESS_OVERRIDE_FIELDS` / `CUT_OVERRIDE_FIELDS` / `EXTRACT_OVERRIDE_FIELDS`) and AC-32.11 (Zod + `httpBody` forwards). `RED_COUNT_31`=21, `RED_COUNT_32`=11. Boundary inventories cite the named sets. | named-sets.json; implementation-plan.md; task.md rows 1–2, 4–5 |
| P8AM-003 | Did **not** add ESLint (`MCP_ESLINT: null`, p5 Local Canon). Bound anti-placeholder/G36 `rg` to task rows 3, 6, and H1-2 with `rg` exit 1 = clean, `>1` = error. | named-sets.json; task.md; implementation-plan.md §Verification |
| P8AM-007 | After every native/helper process, capture `$code`/`$c`/`$ocode=$LASTEXITCODE` immediately before `Get-Content`. Red-oracle helpers use `$ocode`. | task.md rows 1,3,4,5,6,H1-2; implementation-plan.md verification snippets |
| P8AM-004 | Keep download Local Canon required `confirm: z.literal(true)`. Missing confirm → Zod `validation_error` (not `confirm_required`) + fetch count 0. AC-32.10 states the negative. | implementation-plan.md AC-32.10 |
| P8AM-005 | Cite `ROUTE_COUNT_*`, `ACTION_INDEX_*`, `COMPOUND_TOOLS_AFTER`, `STREAM_MODES` instead of restating `48+13`, `46+13`, `59/7`, `KEEP 46`, `first/all`. | implementation-plan.md; task.md |
| P8AM-006 | Downloader→Convert is `out-of-scope`, Deferred-to MEU `—`, basis 08 535–541. GUI Convert remains `deferred` MEU-33 (Session 15). | implementation-plan.md C2 / Out of Scope |

### Blast-radius census (Step 5c / PR-6)

Index: `C:/Temp/av-kit/census-p8am-index.txt`. Runner: `C:/Temp/av-kit/census-p8am-runner.txt`. Unfiltered concat: `C:/Temp/av-kit/census-p8am-ledger.txt`. Per-query receipts: `C:/Temp/av-kit/census-p8am-01-old.txt` … `census-p8am-25-new.txt`. Duplicate disposition copy: `C:/Temp/av-kit/census-p8am-per-hit-dispositions.md`.

Queries: 42. `rg -F -n` over `implementation-plan.md`, `task.md`, `named-sets.json`. Zero-hit old/vacuous: 18 (`GPU_GET_UNPROBED`, `probed: false`, `recommended_encoder:null`, `recommended_encoder: null`, `AC-31.1–31.18`, `AC-31.1-31.18`, `AC-32.1–32.10`, `AC-32.1-32.10`, `KEEP 46`, `48 + 13`, `46 + 13`, `59 / 7`, `first/all`, backtick `first/all`, `npx eslint`, `if ($LASTEXITCODE`, `Deferred-to MEU-33`, junk `GPUCapabilitiesOut probed`). Remaining hits dispositioned below.

| Receipt | File:Line | Disposition |
|---|---|---|
| census-p8am-01-old.txt | (no hit) | updated-gone |
| census-p8am-01-new.txt | named-sets.json:45 | updated |
| census-p8am-01-new.txt | task.md:45 | updated |
| census-p8am-01-new.txt | implementation-plan.md:93 | updated |
| census-p8am-01-new.txt | implementation-plan.md:112 | updated |
| census-p8am-01-new.txt | implementation-plan.md:170 | updated |
| census-p8am-01-new.txt | implementation-plan.md:391 | updated |
| census-p8am-02-old.txt | implementation-plan.md:392 | confirmed-consistent (withdrawn Option B) |
| census-p8am-02b-old.txt | (no hit) | updated-gone |
| census-p8am-03-old.txt | (no hit) | updated-gone |
| census-p8am-03b-old.txt | (no hit) | updated-gone |
| census-p8am-04-old.txt | (no hit) | updated-gone |
| census-p8am-04b-old.txt | (no hit) | updated-gone |
| census-p8am-04-new.txt | named-sets.json:6 | updated |
| census-p8am-04-new.txt | task.md:44 | updated |
| census-p8am-04-new.txt | implementation-plan.md:59 | updated |
| census-p8am-05-old.txt | (no hit) | updated-gone |
| census-p8am-05b-old.txt | (no hit) | updated-gone |
| census-p8am-05-new.txt | named-sets.json:8 | updated |
| census-p8am-05-new.txt | task.md:47 | updated |
| census-p8am-05-new.txt | implementation-plan.md:62 | updated |
| census-p8am-06-old.txt | (no hit) | updated-gone |
| census-p8am-06-new.txt | named-sets.json:70 | confirmed-consistent (owner numeric lives only here) |
| census-p8am-06-new.txt | implementation-plan.md:89 | updated |
| census-p8am-06-new.txt | implementation-plan.md:254 | updated |
| census-p8am-06-new.txt | task.md:47 | updated |
| census-p8am-07-old.txt | (no hit) | updated-gone |
| census-p8am-07-new.txt | named-sets.json:53 | confirmed-consistent (owner) |
| census-p8am-07-new.txt | task.md:45 | updated |
| census-p8am-07-new.txt | implementation-plan.md:88 | updated |
| census-p8am-07-new.txt | implementation-plan.md:184 | updated |
| census-p8am-07-new.txt | implementation-plan.md:234 | updated |
| census-p8am-08-old.txt | (no hit) | updated-gone |
| census-p8am-08-new.txt | named-sets.json:72 | confirmed-consistent (owner) |
| census-p8am-08-new.txt | task.md:48 | updated |
| census-p8am-08-new.txt | implementation-plan.md:89 | updated |
| census-p8am-08-new.txt | implementation-plan.md:254 | updated |
| census-p8am-08-new.txt | implementation-plan.md:284 | updated |
| census-p8am-08-new.txt | implementation-plan.md:299 | updated |
| census-p8am-09-old.txt | (no hit) | updated-gone |
| census-p8am-09-new.txt | named-sets.json:73 | confirmed-consistent (owner) |
| census-p8am-09-new.txt | implementation-plan.md:254 | updated |
| census-p8am-09-new.txt | implementation-plan.md:299 | updated |
| census-p8am-10-old.txt | (no hit) | updated-gone |
| census-p8am-10b-old.txt | (no hit) | updated-gone |
| census-p8am-10-new.txt | named-sets.json:43 | confirmed-consistent (owner) |
| census-p8am-10-new.txt | implementation-plan.md:90 | updated |
| census-p8am-10-new.txt | implementation-plan.md:110 | updated |
| census-p8am-10-new.txt | implementation-plan.md:158 | updated |
| census-p8am-11-old.txt | implementation-plan.md:263 | confirmed-consistent (negative: code is not `confirm_required`) |
| census-p8am-12-old.txt | (no hit) | updated-gone |
| census-p8am-12-new.txt | named-sets.json:50 | updated |
| census-p8am-12-new.txt | task.md:40 | updated |
| census-p8am-12-new.txt | implementation-plan.md:95 | updated |
| census-p8am-13-new.txt | named-sets.json:49 | updated |
| census-p8am-13-new.txt | implementation-plan.md:95 | updated |
| census-p8am-13-new.txt | task.md:40 | updated |
| census-p8am-13-new.txt | task.md:48 | updated |
| census-p8am-13-new.txt | task.md:49 | updated |
| census-p8am-13-new.txt | task.md:54 | updated |
| census-p8am-14-old.txt | (no hit) | updated-gone |
| census-p8am-14-new.txt | task.md:44 | updated |
| census-p8am-14-new.txt | task.md:47 | updated |
| census-p8am-14-new.txt | implementation-plan.md:341 | updated |
| census-p8am-14-new.txt | implementation-plan.md:368 | updated |
| census-p8am-15-old.txt | (no hit) | updated-gone |
| census-p8am-15b-old.txt | implementation-plan.md:146 | confirmed-consistent (GUI Convert is the real MEU-33 deferral) |
| census-p8am-15-new.txt | implementation-plan.md:309 | updated |
| census-p8am-15-new.txt | implementation-plan.md:310 | confirmed-consistent |
| census-p8am-15-new.txt | implementation-plan.md:311 | confirmed-consistent |
| census-p8am-15-new.txt | implementation-plan.md:312 | confirmed-consistent |
| census-p8am-15-new.txt | implementation-plan.md:313 | confirmed-consistent |
| census-p8am-15-new.txt | implementation-plan.md:314 | confirmed-consistent |
| census-p8am-15-new.txt | implementation-plan.md:315 | confirmed-consistent |
| census-p8am-15-new.txt | implementation-plan.md:316 | confirmed-consistent |
| census-p8am-15-new.txt | implementation-plan.md:317 | confirmed-consistent |
| census-p8am-16-new.txt | named-sets.json:46 | updated |
| census-p8am-16-new.txt | task.md:45 | updated |
| census-p8am-16-new.txt | implementation-plan.md:94 | updated |
| census-p8am-16-new.txt | implementation-plan.md:158 | updated |
| census-p8am-16-new.txt | implementation-plan.md:186 | updated |
| census-p8am-16-new.txt | implementation-plan.md:246 | updated |
| census-p8am-16-new.txt | implementation-plan.md:264 | updated |
| census-p8am-17-new.txt | named-sets.json:47 | updated |
| census-p8am-17-new.txt | task.md:45 | updated |
| census-p8am-17-new.txt | implementation-plan.md:94 | updated |
| census-p8am-17-new.txt | implementation-plan.md:158 | updated |
| census-p8am-17-new.txt | implementation-plan.md:187 | updated |
| census-p8am-17-new.txt | implementation-plan.md:246 | updated |
| census-p8am-17-new.txt | implementation-plan.md:264 | updated |
| census-p8am-18-new.txt | named-sets.json:48 | updated |
| census-p8am-18-new.txt | task.md:45 | updated |
| census-p8am-18-new.txt | implementation-plan.md:94 | updated |
| census-p8am-18-new.txt | implementation-plan.md:158 | updated |
| census-p8am-18-new.txt | implementation-plan.md:188 | updated |
| census-p8am-18-new.txt | implementation-plan.md:246 | updated |
| census-p8am-18-new.txt | implementation-plan.md:264 | updated |
| census-p8am-19-new.txt | implementation-plan.md:186 | updated |
| census-p8am-19-new.txt | implementation-plan.md:213 | updated |
| census-p8am-20-new.txt | implementation-plan.md:187 | updated |
| census-p8am-21-new.txt | implementation-plan.md:188 | updated |
| census-p8am-22-new.txt | implementation-plan.md:264 | updated |
| census-p8am-22-new.txt | implementation-plan.md:283 | updated |
| census-p8am-23-old.txt | implementation-plan.md:409 | confirmed-consistent (withdrawn as GPU authority) |
| census-p8am-24-old.txt | (no hit) | updated-gone |
| census-p8am-25-new.txt | named-sets.json:45 | confirmed-consistent (`GPU_LAZY_GET` owner text) |
| census-p8am-25-new.txt | implementation-plan.md:112 | confirmed-consistent |
| census-p8am-25-new.txt | implementation-plan.md:113 | confirmed-consistent |
| census-p8am-25-new.txt | implementation-plan.md:170 | confirmed-consistent |
| census-p8am-25-new.txt | implementation-plan.md:171 | confirmed-consistent |
| census-p8am-25-new.txt | implementation-plan.md:197 | confirmed-consistent |
| census-p8am-25-new.txt | implementation-plan.md:207 | confirmed-consistent |

Blast-radius census: 24 values/variants with hits or explicit gone, 42 queries, all hits `updated` or `confirmed-consistent`, 18 `updated-gone`.

---

## Round 2 Recheck — 2026-08-26

### Intent Anchor

Executing this plan is supposed to deliver Session 14 only: MEU-31's complete `/api/v1/conversions*` REST/settings/OpenAPI contract followed by MEU-32's REST-parity `avkit_convert` MCP tool, reusing the approved MEU-28–30 engine and leaving MEU-33, Session 15, and Session 8c untouched. The Round 1 response-shape and field-forwarding blockers are corrected, but the current plan can still deliver a race-prone first-use GPU control that violates its own exactly-once observable while all planned tests pass.

### Scope

**Targets re-read from current disk:**

- `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/implementation-plan.md`
- `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/task.md`
- `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/named-sets.json`
- `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/assert-red-oracle.ps1`
- `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/assert-handoff-markers.ps1`
- `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/assert-handoff-acs.ps1`

**Authority rechecked:** `docs/build-plan/08-video-conversion.md` §REST + §MCP and GPU VO; current `ConversionService` GPU surface; Phase 4 API canon; Phase 5 MCP toolset/registry/destructive/settings canon; Session 14/15 grouping; MEU SSOT; harness override; review workflow and template.

**Checklist applied:** IR + DR + PR, including C2, PR-6, PR-8, and PR-9. Static review only; no tests, linters, type checks, builds, OpenAPI export, or repository Python tools were run.

### Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|
| P8AM-008 | High | High | **`GPU_LAZY_GET` is an unlocked read-then-write control, and its sequential oracle can false-pass duplicate cold probes.** The plan requires the first cold GET to call `detect_gpu` exactly once, but the production chain it names is `get_gpu()` followed by `detect_gpu()`. Those existing service methods read/write `_gpu` without a lock; the service's `_lock` is used by `start_processing`, not by either GPU method. Two concurrent cold GETs can therefore both observe `None` and each run the 1-frame probe. AC-31.3 only sends a first GET and then a second cached GET, so that race-prone implementation satisfies the planned oracle. This is a new, materially different PR-8 failure from Round 1's now-fixed response/authority issue: the observable and producer exist, but the read-then-write pair has no named atomicity mechanism and no adversarial concurrent oracle. | `implementation-plan.md:112,170,203-215`; `task.md:45`; `packages/core/src/avkit_core/services/conversion.py:139,159-164,185-190` | Keep the corrected 200 VO contract, but specify one in-scope atomic mechanism for cold initialization (for example, a router-owned lock with a second cache check, or a source-backed atomic service surface) and add a concurrent cold-GET test proving N simultaneous requests produce one `detect_gpu` call and the same non-null response. Preserve refresh as an explicit re-probe outside the lazy-cache rule. | open |
| P8AM-009 | Low | High | **H2-4's prose overstates the checks its command re-runs.** The row says it re-runs handoff AC sets plus reflection/metrics checks, but its validation invokes only handoff markers, `check_exec_review.py`, and `meu_status.py render --check`. Earlier H1-6a/H2-2/H2-3 rows separately cover the omitted artifacts, so this is clerical predicate drift and does not block. | `task.md:59,64-66` | Either add the already-named AC/reflection/metrics checks to H2-4 or narrow the row text to the three checks it actually runs. | open |

### Severity Summary

| Critical | High | Medium | Low |
|---:|---:|---:|---:|
| 0 | 1 | 0 | 1 |

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| P8AM-001 GPU response authority/shape | open | ✅ Fixed — `GPU_LAZY_GET` now returns the non-null domain VO shape, omits `probed`, and uses Spec 250 + 447 rather than FastAPI #5120 as authority. P8AM-008 is a distinct atomicity failure, not a continuation of the response-shape finding. |
| P8AM-002 kind-specific REST/MCP forwarding | open | ✅ Fixed — AC-31.19–21 bind exact `ConversionAddSpec` fields and AC-32.11 binds Zod input through `httpBody` to fetch JSON. |
| P8AM-003 runnable quality gates | open | ✅ Fixed — the live MCP package has typecheck/test/build scripts but no ESLint dependency or config; the plan names `MCP_TS_GATE`, records `MCP_ESLINT: null`, and binds anti-placeholder/G36 scans to MEU and H1 gates. |
| P8AM-007 exit preservation | open | ✅ Fixed — native/helper exit codes are captured before receipt reads in the corrected Red and gate commands. |
| P8AM-004 missing-confirm oracle | open | ✅ Fixed — AC-32.10 expects Zod `validation_error` plus fetch count zero. |
| P8AM-005 repeated named literals | open | ✅ Fixed — corrected plan/task sites reference the named-set owners; the Round 1 literal variants have zero-hit receipts. |
| P8AM-006 Downloader→Convert scope label | open | ✅ Fixed — current Session 14 exclusion cites the named Spec deferral without assigning it to MEU-33; GUI Convert remains the registered MEU-33 deferral. |

### Confirmed Fixes

- `GPUCapabilitiesOut` is now aligned with the approved domain VO: non-empty `recommended_encoder`, no planner-invented `probed`, and refresh remains an explicit re-probe.
- REST acceptance criteria now cover compress, cut, and extract override forwarding into `ConversionAddSpec`; MCP AC-32.11 covers strict Zod acceptance and fetch-body forwarding.
- Named Red counts are `RED_COUNT_31` and `RED_COUNT_32`; the helpers consume those owners and reject missing AC failure titles.
- Required plan helper scripts and pre-existing validation executables/templates exist; planned API/MCP source, tests, handoffs, review, and reflection remain absent, confirming plan-review mode.

### Checklist Results

#### Information Retrieval (IR)

| Check | Result | Evidence |
|---|---|---|
| All AC have supported source labels | pass | AC-31.1–21 and AC-32.1–11 cite Spec, Local Canon, Research-backed, G29/M2–M7, or combinations. |
| Validation cells are exact commands | pass with Low note | Commands are concrete and receipt-bound. H2-4's label lists checks absent from that row's command (P8AM-009), but the omitted artifacts have separate prerequisite rows. |
| BUILD_PLAN audit row present | pass | Row 7 and WP-HUB bind MEU-31/32, phase 8 execution plans, and `HUB_NEXT_AFTER`. |
| Post-MEU rows present | pass | H1 handoff/review and H2 reflection/metrics/commit-draft rows are explicit and ordered. |

#### Design / Docs Review (DR)

| Check | Result | Evidence |
|---|---|---|
| Naming convention / template version / YAML | pass | Plan folder and rolling artifacts are consistently named; plan template 2.0, task/review 2.1; frontmatter is well formed. |
| DR-1 Claim-to-state match | pass | Corrector claims were checked against current target lines, not Round 1 line numbers. |
| DR-2 Residual old terms | pass | Static old-literal sweep returned zero hits for the withdrawn sentinel/count/scope variants. |
| DR-3 Downstream references | pass | Plan, task, and `named-sets.json` agree on counts, handoffs, override sets, and Session 14 scope. |
| DR-4 Verification robustness | fail | Sequential AC-31.3 cannot catch concurrent duplicate cold probes (P8AM-008). H2-4 also has a Low prose/command mismatch (P8AM-009). |
| DR-5 Evidence auditability | pass | Raw census index, ledger, runner, and per-query receipts are named and readable; static receipts are reproducible. |
| DR-6 Cross-reference integrity | pass | Corrected response VO, REST/MCP fields, settings, destructive set, grouping, and approved engine surfaces otherwise align. |
| DR-7 Evidence freshness | pass | Round 2 independently re-read current targets and reproduced the old-term, existence, unstarted-state, AppServices, and atomicity sweeps. |
| DR-8 Completion vs residual risk | pass | No implementation-complete claim is made; all execution rows remain unchecked and planned implementation artifacts are absent. |

#### Plan Review (PR)

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Both preserve MEU-31 Red→Green→gate, MEU-32 Red→Green→gate, H1 independent review, then H2 closeout. |
| PR-2 Not-started confirmation | pass | All task rows are `[ ]`; planned routes/schemas/tests/handoffs/review/reflection are absent; MEU-31–33 remain `pending`. |
| PR-3 Task contract completeness | pass | Every actionable row has task, owner, deliverable, exact validation, dependency, context strategy, durable output, builder model, and status. |
| PR-4 Validation realism | fail | AC-31.3 can pass an implementation that violates the plan's exactly-once cold-probe control under concurrency (P8AM-008). |
| PR-5 Source-backed planning | pass | The corrected GPU contract uses Spec 250 + 447; field wires and scope exclusions are source-tagged. |
| PR-6 Handoff/corrections readiness | pass | Two MEU handoffs and one rolling implementation review are explicit. Census gate: 42/42 indexed receipts exist, no truncation marker, and 94 ledger hits reconcile exactly to 94 allowed dispositions (`DELTA=0`). |
| PR-7 Scope discipline / C2 | pass | GUI Convert is deferred to registered MEU-33; other exclusions cite actual Spec/grouping/governance bases and do not hide Session 14 REST/MCP work. |
| PR-8 Control reachability / totality / atomicity | fail | GPU observable and call chain are named, but the cold-cache read-then-write has no lock/CAS/atomic statement and no concurrent negative oracle (P8AM-008). Other corrected forwarding/confirm/list/error controls have reachable producers and negative observables. |
| PR-9 Single-statement discipline | pass | Round 1 repeated thresholds/state-set variants are gone; live plan/task references use the named owners. Concrete example values inside one AC do not create competing governing definitions. |

### Commands Executed

Static review only. Every process was redirected under `C:/Temp/av-kit/`, and exit status was captured before receipt reads. No pytest, Vitest, OpenAPI export, ruff, pyright, npm, product build, plan helper, or `tools/*.py` command was run.

- Full current reads of the six targets, the rolling review, review workflow/template, harness/profile/guardrails, Phase 8 authority, MEU/grouping SSOT, current conversion service/domain VO, and Phase 4/5 local canon.
- PR-6 receipts: `review-r2-census-existence.txt` (`42`, missing `0`), `review-r2-census-truncation.txt` (zero hits), and `review-r2-census-reconcile.txt` (`LEDGER_HITS=94`, `DISPOSITIONED_HITS=94`, `DELTA=0`).
- Static inventories: `review-r2-artifact-existence.txt`, `review-r2-unstarted.txt`, `review-r2-appservices.txt`, `review-r2-old-terms.txt`, and `review-r2-atomicity-census.txt`.
- Scoped `rg -F -n` reads/censuses only; no git-worktree assumption was made.

### Open Questions / Assumptions

No human product decision is required. The remaining blocker is a control-design omission: the plan must name how cold GPU initialization becomes atomic while preserving the already-corrected first-use and refresh behavior.

### Verdict

`changes_required` — P8AM-008 is an evidence-backed High PR-8 finding. The plan's sequential test can approve an unlocked implementation that runs the expensive GPU probe more than once under simultaneous cold GETs, contrary to its own exactly-once lazy-init contract. P8AM-009 is clerical and does not affect the verdict.

### Residual Risk

This remains a static unstarted-plan review. Runtime behavior, generated OpenAPI, Red-oracle execution, API/MCP suites, lint/type/build receipts, and closeout artifacts remain unverified until execution. No product code, tests, or plan files were modified.

---

## Corrections Applied — 2026-08-26 after Round 2 (P8AM-008 / P8AM-009)

**Corrector:** coordinator (not the reviewer). Verdict set to `corrections_applied` only. Independent Round 3 must re-score. Product code, tests, and `docs/build-plan/` were not modified. Plan-review cap is 3; this is the last planned resubmission.

**Instruction conflict (flagged):** `plan-corrections.md` HARD STOP vs `/create-plan` Step 5b auto-dispatch — create-plan + `harness.local.md` `reviewer-auto` win.

### Finding dispositions (corrector claims; not an `approved` verdict)

| # | Change | Files |
|---|--------|-------|
| P8AM-008 | Named `GPU_COLD_INIT` on `GPU_ENSURE_FN` (`ensure_conversion_gpu`): `threading.Lock` + double-check `get_gpu` before `detect_gpu`. Do not reuse `ConversionService._lock` (start_processing only; Session 13). AC-31.22: `GPU_COLD_GET_N` threads + Barrier overlap on the helper (not serialized HTTP); GET handler must spy-call `GPU_ENSURE_FN`. Sequential lazy remains AC-31.3. `RED_COUNT_31`=22. Refresh still calls `detect_gpu` directly. | named-sets.json; implementation-plan.md; task.md row 2 |
| P8AM-009 | H2-4 prose now matches its command: handoff markers + `check_exec_review` + `render --check`. AC-set / reflection / metrics stay on H1-6a / H2-2 / H2-3. | task.md H2-4 |

### Blast-radius census (Step 5c / PR-6) — Round 3 resubmission

Index: `C:/Temp/av-kit/census-p8am-r3-index.txt`. Runner: `C:/Temp/av-kit/census-p8am-r3-runner.txt`. Ledger: `C:/Temp/av-kit/census-p8am-r3-ledger.txt`. Extra lock-name receipt: `C:/Temp/av-kit/census-p8am-r3-10-new.txt`. Per-query: `C:/Temp/av-kit/census-p8am-r3-01-old.txt` … `census-p8am-r3-09-new.txt`.

Queries: 12 scripted + 1 extra (`ConversionService._lock`). Zero-hit old: 5 (`"RED_COUNT_31": 21`, `AC-31.1–31.21`, `detect_gpu exactly once`, H2-4 old prose, unbackticked `reuse ConversionService._lock`).

| Receipt | File:Line | Disposition |
|---|---|---|
| census-p8am-r3-01-old.txt | (no hit) | updated-gone |
| census-p8am-r3-01-new.txt | named-sets.json:6 | updated |
| census-p8am-r3-02-old.txt | (no hit) | updated-gone |
| census-p8am-r3-02b-old.txt | (no hit) | updated-gone |
| census-p8am-r3-03-new.txt | named-sets.json:46 | updated |
| census-p8am-r3-03-new.txt | named-sets.json:48 | confirmed-consistent (owner text cites `GPU_ENSURE_FN`) |
| census-p8am-r3-03-new.txt | task.md:45 | updated |
| census-p8am-r3-03-new.txt | implementation-plan.md:93 | updated |
| census-p8am-r3-03-new.txt | implementation-plan.md:112 | updated |
| census-p8am-r3-03-new.txt | implementation-plan.md:189 | updated |
| census-p8am-r3-03-new.txt | implementation-plan.md:199 | updated |
| census-p8am-r3-03-new.txt | implementation-plan.md:209 | updated |
| census-p8am-r3-03-new.txt | implementation-plan.md:210 | updated |
| census-p8am-r3-03-new.txt | implementation-plan.md:218 | updated |
| census-p8am-r3-03-new.txt | implementation-plan.md:229 | updated |
| census-p8am-r3-03-new.txt | implementation-plan.md:397 | updated |
| census-p8am-r3-04-new.txt | named-sets.json:48 | updated |
| census-p8am-r3-04-new.txt | task.md:45 | updated |
| census-p8am-r3-04-new.txt | implementation-plan.md:93 | updated |
| census-p8am-r3-04-new.txt | implementation-plan.md:112 | updated |
| census-p8am-r3-04-new.txt | implementation-plan.md:189 | updated |
| census-p8am-r3-04-new.txt | implementation-plan.md:199 | updated |
| census-p8am-r3-04-new.txt | implementation-plan.md:210 | updated |
| census-p8am-r3-04-new.txt | implementation-plan.md:218 | updated |
| census-p8am-r3-04-new.txt | implementation-plan.md:229 | updated |
| census-p8am-r3-04-new.txt | implementation-plan.md:397 | updated |
| census-p8am-r3-05-new.txt | named-sets.json:47 | updated |
| census-p8am-r3-05-new.txt | implementation-plan.md:93 | updated |
| census-p8am-r3-05-new.txt | implementation-plan.md:189 | updated |
| census-p8am-r3-05-new.txt | implementation-plan.md:210 | updated |
| census-p8am-r3-06-new.txt | implementation-plan.md:170 | updated |
| census-p8am-r3-06-new.txt | implementation-plan.md:189 | updated |
| census-p8am-r3-06-new.txt | implementation-plan.md:210 | updated |
| census-p8am-r3-07-old.txt | (no hit) | updated-gone |
| census-p8am-r3-07-new.txt | task.md:66 | updated |
| census-p8am-r3-08-old.txt | (no hit) | updated-gone (literal without backticks; see r3-10) |
| census-p8am-r3-09-new.txt | named-sets.json:46 | confirmed-consistent (function name owned here; plan cites `GPU_ENSURE_FN`) |
| census-p8am-r3-10-new.txt | named-sets.json:48 | confirmed-consistent (negative: `_lock` stays start-only) |
| census-p8am-r3-10-new.txt | implementation-plan.md:112 | confirmed-consistent (do **not** reuse) |
| census-p8am-r3-10-new.txt | implementation-plan.md:218 | confirmed-consistent (not `_lock`) |
| census-p8am-r3-10-new.txt | implementation-plan.md:398 | confirmed-consistent (withdrawn Option B) |

Blast-radius census: 13 queries, all hits `updated` or `confirmed-consistent`, 5 `updated-gone`.

---

## Round 3 Recheck — 2026-08-26

### Intent Anchor

Executing this plan is supposed to deliver Session 14 only: MEU-31's complete `/api/v1/conversions*` REST/settings/OpenAPI contract followed by MEU-32's REST-parity `avkit_convert` MCP tool, using the approved MEU-28–30 engine and leaving MEU-33, Session 15, and Session 8c untouched. The named GPU cold-init mechanism is now explicit, but its planned concurrency oracle deadlocks that intended mechanism, so executing the current TDD plan cannot reliably complete MEU-31.

### Scope

**Targets re-read from current disk:**

- `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/implementation-plan.md`
- `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/task.md`
- `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/named-sets.json`
- `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/assert-red-oracle.ps1`
- `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/assert-handoff-markers.ps1`
- `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/assert-handoff-acs.ps1`

**Authority rechecked:** `docs/build-plan/08-video-conversion.md` §REST + §MCP and GPU VO; Phase 4 API boundary/status canon; Phase 5 MCP strict/confirm/build/description canon; current `ConversionService` GPU and lock surfaces; the existing Barrier contention pattern in `tests/unit/test_services.py`; Session 14/15 grouping; MEU SSOT; harness override; review workflow and template.

**Checklist applied:** IR + DR + PR, including C2, PR-6, PR-8, and PR-9. Static review only; no pytest, Vitest, OpenAPI export, ruff, pyright, npm, product build, plan helper, or repository Python tool was run.

### Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|
| P8AM-008 | High | High | **The atomic mechanism is named, but AC-31.22's overlap oracle deadlocks the intended locked implementation.** `GPU_COLD_INIT` requires `GPU_ENSURE_FN` to hold a `threading.Lock`, double-check `get_gpu`, and then call `detect_gpu` while still protected. With `GPU_COLD_GET_N == 2`, AC-31.22 instead puts `threading.Barrier(2)` inside fake `detect_gpu`: caller 1 acquires the lock and waits at the Barrier; caller 2 blocks acquiring that same lock and can never enter `detect_gpu` to release the Barrier. The post-join `detect_calls == 1` assertion is therefore unreachable for the correct implementation, while the unlocked implementation is the only one that releases the Barrier. This is a concrete PR-8 totality/negative-oracle failure and makes the MEU-31 Green/gate path hang rather than validate the intended control. | `implementation-plan.md:189,210`; `named-sets.json:47-48`; Local Canon contrast `tests/unit/test_services.py:2039-2045` | Keep the named lock/double-check mechanism, but synchronize the callers' initial empty-cache reads outside the protected `detect_gpu` call (for example, a one-shot Barrier in the first `get_gpu` reads). Add bounded joins plus an assertion that no worker remains alive, then assert `detect_calls == 1`, identical non-empty results, and the GET-handler spy call. | open |

### Severity Summary

| Critical | High | Medium | Low |
|---:|---:|---:|---:|
| 0 | 1 | 0 | 0 |

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| P8AM-008 GPU cold-init atomicity/oracle | open | ❌ Still open — the lock plus under-lock double-check is now named, but the Barrier inside the protected fake `detect_gpu` deadlocks the intended implementation; the overlapping negative oracle is not valid. |
| P8AM-009 H2-4 prose/command mismatch | open | ✅ Fixed — H2-4 now names exactly handoff markers, `check_exec_review`, and `render --check`; it explicitly leaves AC-set, reflection, and metrics checks on H1-6a, H2-2, and H2-3. |
| P8AM-001–007 | fixed in Round 2 | ✅ Remain fixed — current target reads and Round 3 censuses did not reopen their response authority, field forwarding, quality-gate, confirm, naming, scope, or exit-preservation surfaces. |

### Confirmed Fixes

- `GPU_COLD_INIT` now names `threading.Lock` plus an under-lock `get_gpu` double-check before `detect_gpu`; `ConversionService._lock` remains start-processing-only.
- `GPU_ENSURE_FN` is owned as `ensure_conversion_gpu`; sequential lazy GET remains AC-31.3 and POST refresh still re-probes directly.
- `RED_COUNT_31` is 22, and the helper script consumes the named count.
- H2-4's task prose now matches its three validation commands.

### Checklist Results

#### Information Retrieval (IR)

| Check | Result | Evidence |
|---|---|---|
| All AC have supported source labels | pass | AC-31.1–22 and AC-32.1–11 carry Spec, Local Canon, Research-backed, G29/M2–M7, or named-owner bases. |
| Validation cells are exact commands | fail | Commands are concrete and receipt-bound, but the AC-31.22 test contract cannot terminate on the specified correct implementation (P8AM-008). |
| BUILD_PLAN audit row present | pass | Row 7 and WP-HUB bind MEU-31/32, Phase 8 execution plans, and `HUB_NEXT_AFTER`. |
| Post-MEU rows present | pass | H1 handoff/review and H2 reflection/metrics/commit-draft rows remain explicit and ordered. |

#### Design / Docs Review (DR)

| Check | Result | Evidence |
|---|---|---|
| Naming convention / template version / YAML | pass | Folder and rolling artifacts use the canonical slug; plan template 2.0 and task/review template 2.1 frontmatter are well formed. |
| DR-1 Claim-to-state match | fail | The corrector's named lock claim matches disk, but the claim that AC-31.22 supplies a valid overlapping oracle does not: the prescribed Barrier placement deadlocks it. |
| DR-2 Residual old terms | pass | Round 3 old-query receipts are zero-hit for the withdrawn count, AC range, old H2 prose, and lock-reuse wording. |
| DR-3 Downstream references | pass | Plan, task, and `named-sets.json` agree on counts, helper owner, Session 14 scope, and H2 check ownership. |
| DR-4 Verification robustness | fail | AC-31.22 cannot reach its assertions with the intended lock (P8AM-008). |
| DR-5 Evidence auditability | pass | Index, ledger, runner, 12 per-query receipts, the extra lock census, and the correction-log disposition table are present and readable. |
| DR-6 Cross-reference integrity | fail | The cited Local Canon Barrier pattern synchronizes callers before the locked operation (`tests/unit/test_services.py:2039-2045`); it does not place a multi-party Barrier inside the serialized critical section. |
| DR-7 Evidence freshness | pass | Round 3 re-read the current targets and current census receipts; no prior line number was trusted without a fresh read/rg. |
| DR-8 Completion vs residual risk | pass | No implementation-complete claim is made; task rows and planned product/handoff/reflection artifacts remain unstarted/absent. |

#### Plan Review (PR)

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Both retain MEU-31 Red→Green→gate, MEU-32 Red→Green→gate, H1 independent review, then H2 closeout. |
| PR-2 Not-started confirmation | pass | Every task row is unchecked; planned routes/schemas/tests/handoffs/review/reflection are absent; MEU-31–33 remain pending. |
| PR-3 Task contract completeness | pass | Each actionable row has task, owner, deliverable, exact validation, dependency, context strategy, durable output, builder model, and status. |
| PR-4 Validation realism | fail | AC-31.22 hangs the intended locked helper before its assertions (P8AM-008). |
| PR-5 Source-backed planning | fail | The Barrier is source-labeled, but its specified placement is contrary to the cited Local Canon contention shape and incompatible with the named lock. |
| PR-6 Handoff/corrections readiness | pass | Two MEU handoffs and one rolling implementation review are explicit. Round 3 census gate passed: all named receipts exist and are readable; every hit/zero-hit has an allowed disposition. |
| PR-7 Scope discipline / C2 | pass | GUI Convert is deferred to registered MEU-33; the remaining exclusions cite the Phase 8 spec, grouping/MEU state, or governance and do not hide Session 14 REST/MCP work. |
| PR-8 Control reachability / totality / atomicity | fail | The named lock/double-check mechanism is sufficient, but its only concurrent oracle is not total: the correct path cannot release the Barrier or reach the observable assertions (P8AM-008). |
| PR-9 Single-statement discipline | pass | Governing counts, route/action sets, helper name, lock contract, field sets, handoffs, and hub next value remain owned by `named-sets.json`; no materially conflicting live spelling was found. |

### Referenced-Artifact Existence

All required pre-existing executables/templates referenced by the plan are present: `tools/export_openapi.py`, `tools/check_exec_review.py`, `tools/meu_status.py`, `tools/Invoke-CodexDispatch.ps1`, the handoff/reflection templates, the reflection schema, the three plan helper scripts, and `openapi.committed.json`. `tools/validate_closeout_artifacts.py` is absent as explicitly documented. Planned API/MCP source, tests, MEU handoffs, rolling implementation review, and reflection remain absent and are inventoried as execution deliverables.

### Commands Executed

Static review only. Every process was redirected under `C:/Temp/av-kit/`, and exit status was captured before receipt reads.

- Full reads of the six current targets, rolling review, review workflow/template, harness/profile/guardrails, architecture/testing/evidence docs, role specs, and relevant Phase 4/5/8 authorities.
- PR-6 full reads of the Round 3 index, ledger, runner, 12 per-query receipts, extra `ConversionService._lock` receipt, and correction-log dispositions.
- `Test-Path` inventories for required existing and planned-new artifacts.
- Scoped `rg -n` reads for C2 grouping/MEU evidence, current GPU/lock/Barrier source, source authority, and PR-9 named-literal census.
- No pytest, Vitest, OpenAPI export, ruff, pyright, npm, product build, plan helper, `tools/*.py`, or git command was run.

### Open Questions / Assumptions

No human product decision is required. The required change is limited to making AC-31.22 a terminating, deterministic concurrent oracle for the already-selected `GPU_COLD_INIT` mechanism.

### Required Follow-up

This is Round 3, the plan-review cap. The coordinator must not auto-loop into a fourth review round. Human direction is required after the corrector revises the AC-31.22 synchronization contract and records a new blast-radius census.

### Verdict

`changes_required` — P8AM-008 remains an evidence-backed High PR-8 blocker. The atomic mechanism is now named, but the prescribed Barrier sits inside the critical section and deadlocks the intended implementation, so the plan still lacks a usable overlapping negative oracle and cannot reliably complete MEU-31's Green/gate path.

### Residual Risk

This remains a static unstarted-plan review. Runtime behavior, generated OpenAPI, Red-oracle execution, API/MCP suites, lint/type/build receipts, and closeout artifacts remain unverified until execution. No plan file, product code, or test was modified. The plan-review cap is reached, so no further automatic correction/review loop is authorized.

---

## Corrections Applied — 2026-08-26 after Round 3 (human: continue review loop)

**Corrector:** coordinator (not the reviewer). Verdict set to `corrections_applied` only. Human message `continue review loop` authorizes Round 4 beyond the default cap of 3. Product code, tests, and `docs/build-plan/` were not modified.

**Instruction conflict (flagged):** `plan-corrections.md` HARD STOP vs `/create-plan` Step 5d option (a) after explicit USER_EXPLICIT continue — create-plan continuation wins.

### Finding dispositions (corrector claims; not an `approved` verdict)

| # | Change | Files |
|---|--------|-------|
| P8AM-008 | Withdrew N-party Barrier inside fake `detect_gpu`. Live oracle is `GPU_COLD_ORACLE`: caller-side `threading.Barrier(GPU_COLD_GET_N)` then `GPU_ENSURE_FN`; fake `detect_gpu` uses `entered`/`release` Events (Local Canon `test_services.py`); bounded join `GPU_COLD_JOIN_TIMEOUT_S`; assert `detect_calls==1` **before** release; threads not alive after join. `GPU_COLD_INIT` lock/double-check unchanged. | named-sets.json; implementation-plan.md AC-31.22/control/Open Questions; task.md row 2 |

### Blast-radius census (Step 5c / PR-6) — Round 4 resubmission

Index: `C:/Temp/av-kit/census-p8am-r4-index.txt`. Runner: `C:/Temp/av-kit/census-p8am-r4-runner.txt`. Ledger: `C:/Temp/av-kit/census-p8am-r4-ledger.txt`. Extra: `C:/Temp/av-kit/census-p8am-r4-07-new.txt`. Per-query: `C:/Temp/av-kit/census-p8am-r4-01-old.txt` … `census-p8am-r4-06-new.txt`.

Queries: 7 scripted + 1 extra. Zero-hit old: 3 (Barrier-inside-detect AC text; `waits on Barrier(GPU_COLD_GET_N)` as detect wait; `Barrier overlap + unlocked helper`).

| Receipt | File:Line | Disposition |
|---|---|---|
| census-p8am-r4-01-old.txt | (no hit) | updated-gone |
| census-p8am-r4-01b-old.txt | (no hit) | updated-gone |
| census-p8am-r4-02-new.txt | named-sets.json:50 | updated |
| census-p8am-r4-02-new.txt | task.md:45 | updated |
| census-p8am-r4-02-new.txt | implementation-plan.md:93 | updated |
| census-p8am-r4-02-new.txt | implementation-plan.md:112 | updated |
| census-p8am-r4-02-new.txt | implementation-plan.md:189 | updated |
| census-p8am-r4-02-new.txt | implementation-plan.md:199 | updated |
| census-p8am-r4-02-new.txt | implementation-plan.md:210 | updated |
| census-p8am-r4-02-new.txt | implementation-plan.md:229 | updated |
| census-p8am-r4-02-new.txt | implementation-plan.md:397 | updated |
| census-p8am-r4-03-new.txt | named-sets.json:48 | updated |
| census-p8am-r4-03-new.txt | named-sets.json:50 | confirmed-consistent (oracle owner cites timeout name) |
| census-p8am-r4-03-new.txt | implementation-plan.md:93 | updated |
| census-p8am-r4-04-old.txt | (no hit) | updated-gone |
| census-p8am-r4-05-new.txt | named-sets.json:50 | confirmed-consistent (owner protocol text) |
| census-p8am-r4-06-new.txt | implementation-plan.md:399 | confirmed-consistent (withdrawn Option C) |
| census-p8am-r4-07-new.txt | named-sets.json:50 | confirmed-consistent (caller Barrier lives only in `GPU_COLD_ORACLE` owner) |

Blast-radius census: 8 queries, all hits `updated` or `confirmed-consistent`, 3 `updated-gone`.

---

## Round 4 — 2026-08-26

### Intent Anchor

Executing this plan is supposed to deliver Session 14 only: MEU-31's complete `/api/v1/conversions*` REST/settings/OpenAPI contract followed by MEU-32's REST-parity `avkit_convert` MCP tool, using the approved MEU-28–30 engine and excluding MEU-33, Session 15, and Session 8c. The current plan is ready to deliver that objective: the Round 3 deadlock is removed, the cold-GPU control now has a terminating concurrent oracle for its selected lock/double-check mechanism, and no new delivery-level blocker remains.

### Scope

**Targets re-read from current disk:**

- `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/implementation-plan.md`
- `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/task.md`
- `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/named-sets.json`
- `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/assert-red-oracle.ps1`
- `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/assert-handoff-markers.ps1`
- `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/assert-handoff-acs.ps1`

**Authority rechecked:** `docs/build-plan/08-video-conversion.md` REST/MCP and named-deferral sections; current `ConversionService` GPU/lock surfaces; Local Canon contention pattern in `tests/unit/test_services.py`; Session 14/15 grouping; MEU SSOT; harness override; review workflow/template; output-evidence policy.

**Checklist applied:** IR + DR + PR, including C2, PR-6, PR-8, and PR-9. Static review only under the user's execution prohibition.

### Findings

| # | Severity | Confidence | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|

No open findings.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| P8AM-008 GPU cold-init oracle deadlocked the intended lock | open | ✅ Fixed — callers now synchronize before `GPU_ENSURE_FN`; fake `detect_gpu` uses `entered`/`release` Events instead of an N-party Barrier; release precedes bounded joins; the correct locked implementation reaches all assertions and terminates. |
| P8AM-001–007 and P8AM-009 | fixed in prior rounds | ✅ Remain fixed — current target reads and the Round 4 census did not reopen their response authority, field forwarding, quality-gate, confirm, naming, scope, exit-preservation, or H2-4 surfaces. |

### Confirmed Fix

- `GPU_COLD_ORACLE` is owned once in `named-sets.json:50`: `GPU_COLD_GET_N` callers wait on a caller-side Barrier and then invoke `GPU_ENSURE_FN`; fake `detect_gpu` increments the counter, sets `entered`, and waits on `release` with `GPU_COLD_JOIN_TIMEOUT_S`.
- On the intended `GPU_COLD_INIT` path, one caller holds the dedicated lock, double-checks `get_gpu`, and enters `detect_gpu`; other callers wait on the lock rather than inside the fake. The main test can therefore observe `detect_calls == 1`, set `release`, join every thread with the named timeout, assert no thread remains alive, assert the final counter remains one, and compare identical encoders (`implementation-plan.md:93,112,189,210`; `task.md:45`).
- GET production reachability remains explicit: handler → `GPU_ENSURE_FN` → dedicated lock → under-lock `get_gpu` double-check → `detect_gpu`; a GET spy proves the handler uses the helper (`implementation-plan.md:189,210`). Refresh continues to call `detect_gpu` directly.
- Withdrawn Option C remains documented only as rejected: no N-party Barrier is placed inside fake `detect_gpu` (`implementation-plan.md:399`).

### Checklist Results

#### Information Retrieval (IR)

| Check | Result | Evidence |
|---|---|---|
| All AC have supported source labels | pass | AC-31.1–22 and AC-32.1–11 retain Spec, Local Canon, Research-backed, G29/M2–M7, or named-owner sources. |
| Validation cells are exact commands | pass | Task rows retain concrete redirected commands, immediate exit capture, Red-oracle helpers, scoped gates, and named closeout checks. AC-31.22 now terminates on the selected implementation. |
| BUILD_PLAN audit row present | pass | WP-HUB/task row 7 bind MEU-31/32, phase 8 execution plans, and `HUB_NEXT_AFTER`. |
| Post-MEU rows present | pass | H1 handoff/independent-review and H2 reflection/metrics/commit-draft rows remain explicit and sequential. |

#### Design / Docs Review (DR)

| Check | Result | Evidence |
|---|---|---|
| Naming convention / template version / YAML | pass | Canonical slug and rolling paths are consistent; plan template 2.0 and task/review template 2.1 frontmatter are well formed. |
| DR-1 Claim-to-state match | pass | The corrector's caller-Barrier/Event protocol is present in `named-sets.json:50` and referenced consistently by the plan/task. |
| DR-2 Residual old terms | pass | Round 4 old-query receipts are zero-hit for Barrier-inside-detect wording and the prior unlocked-helper label. |
| DR-3 Downstream references | pass | Plan, task, and named sets agree on `GPU_COLD_ORACLE`, timeout ownership, AC count, Session 14 scope, and H2 ownership. |
| DR-4 Verification robustness | pass | The intended lock no longer blocks the test harness; counter, liveness, identical-result, and GET-spy observables are reachable. |
| DR-5 Evidence auditability | pass | Round 4 index, ledger, runner, seven indexed per-query receipts, extra receipt, and per-hit/zero-hit disposition table are present and readable. |
| DR-6 Cross-reference integrity | pass | The new pattern matches Local Canon's caller-side Barrier plus entered/release Event shape (`tests/unit/test_services.py:2039-2056`) without moving the Barrier into the serialized operation. |
| DR-7 Evidence freshness | pass | All six targets and cited current canon were re-read from disk; current line references were regenerated. |
| DR-8 Completion vs residual risk | pass | This is an unstarted plan approval, not an implementation-complete claim. |

#### Plan Review (PR)

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Both preserve MEU-31 Red→Green→gate, MEU-32 Red→Green→gate, H1 independent review, then H2 closeout. |
| PR-2 Not-started confirmation | pass | Every task row is unchecked; planned routes/schemas/tests/MEU handoffs/implementation review/reflection are absent; MEU-31–33 remain pending. |
| PR-3 Task contract completeness | pass | Every actionable row includes task, owner, deliverable, exact validation, dependency/context, durable output, builder model, and status. |
| PR-4 Validation realism | pass | AC-31.22 can run to completion on `GPU_COLD_INIT`; the remaining API/MCP validations are concrete and scoped to their deliverables. |
| PR-5 Source-backed planning | pass | The lock/double-check and concurrent oracle cite Research-backed atomicity plus the live Local Canon contention shape; other AC sources remain supported. |
| PR-6 Handoff/corrections readiness | pass | Index, ledger, runner, all seven indexed per-query receipts, and the extra receipt exist. The correction log dispositions cover every raw hit and all three zero-hit old queries. Two MEU handoffs and one rolling implementation review remain explicit. |
| PR-7 Scope discipline / C2 | pass | Session 14 is MEU-31 then MEU-32; GUI Convert is deferred to registered MEU-33/Session 15; the remaining exclusions cite the Phase 8 spec, grouping/MEU state, or governance and hide no Session 14 work. |
| PR-8 Control reachability / totality / atomicity | pass | AC-31.22 names its counter/liveness/result observables, traces GET to the producer, supplies an unlocked-helper adversary oracle, and binds the read-then-write pair to a dedicated lock with under-lock double-check. The intended path terminates. |
| PR-9 Single-statement discipline | pass | Counts, route/action sets, helper/lock/oracle names, timeout, field sets, handoffs, and hub-next remain owned by `named-sets.json`; the current census found no materially conflicting live spelling. |

### Referenced-Artifact Existence

Required pre-existing tools/templates remain present: `tools/export_openapi.py`, `tools/check_exec_review.py`, `tools/meu_status.py`, `tools/Invoke-CodexDispatch.ps1`, handoff/review/reflection templates, reflection schema, all three plan helper scripts, and `openapi.committed.json`. `tools/validate_closeout_artifacts.py` is absent exactly as documented. Planned API/MCP source, tests, MEU handoffs, rolling implementation review, and reflection remain absent and scheduled, confirming unstarted execution.

### Commands Executed

Static evidence only. Every process wrote all streams under `C:/Temp/av-kit/` and preserved exit status before receipt reads.

- Full/current line-numbered reads of the six target artifacts, rolling review, workflow/template, harness/profile/guardrails, role/evidence docs, Phase 8 authority, current conversion service, and Local Canon concurrency test.
- PR-6 exact indexed-file reads and existence checks; raw evidence is captured in `C:/Temp/av-kit/r4-pr6-census-audit.txt` and `r4-pr6-exact-files.txt`.
- C2/grouping/MEU evidence in `C:/Temp/av-kit/r4-c2-scope-evidence.txt`; referenced-artifact/unstarted inventory in `r4-artifact-existence.txt`; PR-9 census in `r4-pr9-census.txt`; canonical-target guard in `r4-pre-edit-guard.txt`.
- Two grouped display attempts and one initial PR-9 regex form failed before collecting evidence because of outer-PowerShell variable/quote expansion; corrected variable-free/single-quoted forms produced the cited canonical receipts. No target state was changed by those failures.
- No pytest, Vitest, OpenAPI export, ruff, pyright, npm, product build, plan helper, `tools/*.py`, or git command was run.

### Open Questions / Assumptions

None. No remaining product decision or review blocker is required for Session 14 execution.

### Required Follow-up

No `/plan-corrections` follow-up is required. This review workflow stops after recording the Round 4 verdict; implementation is outside the independent review request.

### Verdict

`approved` — P8AM-008 is fixed. AC-31.22 is now a terminating concurrent oracle for the named `GPU_COLD_INIT` lock/double-check mechanism, the PR-6 correction evidence is complete and dispositioned, prior fixes remain intact, and no new High or Critical finding remains.

### Residual Risk

This is static plan approval, not runtime evidence. Red-oracle execution, generated OpenAPI, API/MCP tests, type/lint/build gates, concurrent scheduling behavior, and closeout artifacts still require execution receipts under `task.md`. No plan file, product code, or test was modified during this review.
