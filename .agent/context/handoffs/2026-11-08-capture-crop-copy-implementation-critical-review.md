---
date: "2026-11-09"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-08-capture-crop-copy/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s59-execution-2026-11-08-capture-crop-copy"
round: 2
---

# Critical Review: 2026-11-08-capture-crop-copy

> **Review Mode:** execution · **Verdict:** changes_required · **Intent achieved:** partial

## Scope

Independent Codex review of Claude Code/Anthropic's Session 59, MEU-130. Scope: the working-tree delta against `f15626c25af428e33c0274cb280eef6579455320`, including the new crop integration module, handoff and baseline records. The reviewer did not author the work. Applied IR-1 through IR-7, relevant DR checks, AC-130.1–29, the listed cross-reference families, D-481–499/D-476 and the grouping's D-400–406.

**Intent anchor:** Session 59 lets an agent cut a region of any capture into a new shot. `POST /captures/{id}/crop` and MCP `crop` take `x`, `y`, `width` and `height` in original pixels, or in fractions with `unit: "fraction"`, and an optional `name`. The box goes through Session 58's `resolve_region`, so a crop and a region view of the same box cut the same pixels (grouping D-401). The original's pixels are saved exactly, with no resampling, as a PNG in the inbox root with metadata stripped and the ICC profile kept. The new shot has source `Crop`. The source's saved marks are carried over, moved by the crop's origin and clipped to it, and the crop gets its own sidecar and bake. The response is 201 with the new shot, the source id, the requested and applied boxes, whether the box was clamped, and how many marks were kept, clipped and dropped. The source's file, sidecar, bake and row are never changed, so no `confirm` is asked.

All reviewer writes stayed under `C:/Temp/av-kit`. No product suite, application, gate, live audit, network request or Git mutation was run. Independent image probes used only scratch images. Repository files, forbidden configuration/secrets and the real inbox were not written; forbidden configuration/secrets were not opened. Accepted scope decisions, documented limits and subsequent H2 work are not findings.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F1 | High | yes | behavior | **CROP_PIXELS silently discards the ICC profile of a CMYK JPEG.** The adapter deliberately sets `icc = None` when converting CMYK to RGB. A scratch JPEG carrying the valid U.S. Web Coated (SWOP) v2 CMYK profile had 557168 ICC bytes before crop and zero afterward. The crop succeeds, so an API/MCP caller receives a new PNG without the promised retained profile; color-managed consumers lose the source's color-profile information. RGB conversion is an accepted limit; dropping the profile is not. This violates D-482/CROP_PIXELS and AC-130.10's ICC-preservation requirement, also stated in the goal and the handoff. The current metadata test covers only RGB PNG. | `packages/infrastructure/src/avkit_infra/capture/adapter.py:409-410`; test gap `tests/unit/test_capture_adapter.py:1549-1575` | Honor the approved ICC-preservation contract for converted input modes and add a profiled CMYK-JPEG regression alongside the RGB-PNG control. If color-space compatibility requires changing that contract, obtain an explicit amendment instead of silently introducing an exception. | fixed |
| F2 | Medium | no | behavior | **MARK_CLIP_ARROW rounds an exact half-pixel intersection down for some integer arrows.** For a 300×300 source, crop `(89,125,8,44)` and saved arrow `(119,223) → (79,53)`, the exact entry is `(8,4.5)`, so half-up requires `(8,5)`. The implementation returns `(8,4)` because floating-point interpolation falls below the tie. Reversing that same segment returns the boundary point `(8,5)`. An agent's carried arrow can therefore move by one pixel depending on direction. This violates the half-up rule in D-487 and AC-130.3; the eleven existing cases miss this tie. The one-pixel discrepancy is non-blocking under the materiality gate. | `packages/core/src/avkit_core/domain/capture.py:517`; `packages/core/src/avkit_core/domain/capture.py:526-527` | Make integer-segment intersection rounding robust at exact halves, for example with exact rational arithmetic, and add this case and its reverse to AC-130.3. | fixed |

Both findings have **High confidence**, subject **deliverable**, kind **behavior**, and contract family **AC-130**. Neither is a control-defeat finding. No Critical finding was established.

## Checklist Results

### Q1 — Mark carry and clipping

**Accepted:** exhaustive `Annotation` matching with `assert_never`; half-open region marks, inclusive rect outlines, zero-size mark rules and text-anchor behavior. Source marks are immutable. Counts and the clamp fixed-point assertions are meaningful. Scratch checks included negative crop origins, exact edges and a 1 px crop. A zero-length arrow already wholly inside is kept by the explicit both-ends-inside contract; a clipped arrow rounded to zero is dropped. No reversal was observed. **Not accepted: F2.** An independent exact-rational oracle found 2 rounding mismatches among 20000 seeded arrow cases; the all-positive, API-valid reproducer above confirms the issue on reachable coordinates.

### Q2 — Pixels, modes, metadata and adapter errors

**Accepted:** direct `Image.crop`, no resize, EXIF transpose or empty bake; PNG-storable modes and palette transparency are preserved; other modes convert to RGB/RGBA. RGB PNG retained its 588-byte ICC profile and exact cropped pixels. Save/probe failures are wrapped; decode and size refusals have the fixed path-free messages. **Not accepted: F1.** A valid profiled CMYK JPEG becomes an RGB PNG with no ICC profile. The source hash stays unchanged in both probes.

### Q3 — Naming and source enum

**Accepted:** sanitization, fixed refusals, reserved Windows names including `CON.txt`, PNG extension, bounded derived stems and collision numbering. `_crop_dest` considers case-folded root entries, every temporary entry without its suffix, all listed sidecar/bake/image suffixes and row paths. Exclusive temporary creation protects a competing temporary file. Sanitized names cannot traverse the inbox; derived names remain comfortably below the component limit. `Crop` is last, has no register wire entry, and name-based persistence needs no migration. **Not accepted:** no additional material issue.

### Q4 — Read, bake, rollback and source safety

**Accepted:** one lock hold and one unit of work; the mapped `try` encloses sidecar reads, name enumeration, directory creation, exclusive temporary creation, adapter/probe/writes and commit. `tmp` is assigned only after `open("xb")` succeeds. Ownership flags gate cleanup, and pre-cut refusals pass through while other failures become fixed 503s. Carried marks create both sidecar and configured bake, with both paths saved; no carried marks creates neither. Source paths are read only. The four fault tests and competing-temporary-file cases have meaningful row/file assertions. The disclosed `_discard` and semantic-sidecar-message departures do not establish an additional material product failure within the declared boundary. **Not accepted:** none beyond Q2's output metadata.

### Q5 — API and OpenAPI

**Accepted:** inherited `ApiModel` extra-field prohibition; finite-number guard and Session 58 resolver; 201 with the six specified response fields and no image bytes. AC-130.13 compares applied coordinates and exact pixels within the accepted view-scale bounds. Independent recursive OpenAPI comparison found only the crop path and five crop schemas; after removing them, the documents are equal. **Not accepted:** no API-shape defect.

### Q6 — MCP, audit baseline and parity fixture

**Accepted:** strict crop union member, POST body, add timeout, description markers, non-destructive/no-confirm behavior, 71 rows and 11 capture actions. `capture.crop` is immediately after revert, depends on flatten, registers cleanup ownership and compares the source SHA before/after. A dedicated `StepSpec.execute` correctly implements the required extra observation. D-499 A's pending set is exactly `avkit_capture.crop`; equality and membership/absence checks still reject unrelated drift. Four fixture cases use real `clip_mark` with their own seed. Independent comparison found every old fixture case unchanged and exactly the four named additions. **Not accepted:** no additional material issue. No live audit is claimed.

### Q7 — Console and private values

**Accepted:** no added log calls; name refusals do not echo input; the existing registered event carries id/source, and HealthService removes the bake's path field before rendering or ring storage. The crop's protected file-error paths prevent raw probe/OS diagnostics from reaching responses. AC-130.22 builds the real services with the D-391 reset and checks stdout/stderr, ring, refusal messages and an existing console file. Its stdout/ring/Crop positive controls are substantive. **Limit:** the file check is conditional and the supplied name is not marker-bearing, so the test alone does not prove every hypothetical logging mutation; source tracing supports the current behavior. No new home-folder literal was found in added tracked lines or the inspected new module. **Not accepted:** no concrete new leak established.

### Q8 — Tests and Red/Green evidence

**Accepted:** independent `red-check.py` runs confirmed all 7 carry, 15 crop and 7 MCP/UI required AC titles, with zero problems; its 36-fixture selftest had zero wrong results. Red runs contain assertion failures, not setup failures. Baseline/Green/full receipts agree: Python 1448 → 1559 (final run has no warnings), UI 1192 → 1193 in 114 files, MCP 479 → 485 in 35 files, and standalone crop 23. Cross-reference enum/action/route pins and AC-16.9's valid-body oracle move correctly; AC-67.19's order pin now includes crop. The unchanged resolver/import/scan and fixture-reproduction guards are in the recorded full scope, and `test-ids.ts` is unchanged. The disclosed row-5 and getdata changes preserve their behavior assertions. **Limit:** the receipts do not contain complete Red-time snapshots of every test file, so byte-for-byte historical immutability cannot be independently certified; no additional assertion weakening was identified. **Not accepted:** AC-130.10 omits the F1 conversion branch; AC-130.3 omits the F2 exact tie.

**IR-5 ratings for changed assertions:** Strong — AC-130.1–9, .11–21, .23–26, .28–29 and the changed enum/route/action/order regression pins; Adequate — .10 (strong RGB metadata oracle, missing converted input), .22 (conditional file surface), .27 (checks call/registration, while source-unchanged behavior is established by code inspection). AC-130.3's reference cases are strong for those cases but incomplete at the reproduced tie. No trivially passing test was identified. Existing tests outside the changed assertions were not exhaustively re-audited.

### Q9 — Evidence freshness and records

**Accepted:** current state recomputed exactly as `f15626c25af428e33c0274cb280eef6579455320+fd97e8484a122e30240b8aeb29933ec764ba893f4937436f2cfc2b59998c9587`. `ELECTRON_RUN_AS_NODE` was unset. A process-local scratch ignore file excluded only `.claude/settings.local.json`; it was never opened. A process-local `safe.directory` value addressed sandbox ownership, without changing Git config on disk. The initial attempt replaced the harness's safety override and failed before hashing; the corrected attempt exited 0 with the exact expected hash.

The seven handoff `evidence.v1` summaries agree with their named receipts, including the initial 21 warnings and subsequent clean full rerun. The full gate records each step's exit, both matching identities and `session-gate: all steps exit 0`. Structured comparisons found only MEU-130 changed in the MEU register, no existing issue changed/removed and exactly the new pending-crop issue added. Grouping changes only row 59. All 34 baseline anchor files retain their measured line endings; the new module is LF. Git's LF-normalized blobs were not mistaken for working-copy endings. **Not accepted:** 09's and the handoff's unqualified ICC-retention claims do not hold for F1. Other delivered notes match the implementation.

### IR/DR outcome summary

| Check | Result | Procedure / observation |
|---|---|---|
| IR-1 integration evidence | pass | Real `build_services` integration module inspected; matching full/runtime receipts show 1559 Python and 23 crop passes. Reviewer did not rerun suites. |
| IR-2 stub compliance | n/a | No new production stub remains; new integration tests use real collaborators. |
| IR-3 error mapping | pass | Traced service, adapter and API handlers; inspected 404/422/409/503 assertions and ownership/failure cases. |
| IR-4 correction generalization | n/a | Initial execution-review round; no prior findings to close. |
| IR-5 assertion strength | partial | Per-AC grades above; conversion metadata and exact-half arrow cases are missing. |
| IR-6 boundary validation | pass | Strict API/Zod schemas and negative request assertions inspected. |
| IR-7 scope and AC integrity | pass | All 29 owned ACs and named cross-reference families are represented; GUI/baseline/evaluation deferrals follow accepted decisions. |
| DR claim-to-state | partial | F1 contradicts ICC-retention claims; remaining changed spec/record notes agree. |
| DR evidence freshness | pass | Independent current identity equals the recorded full-gate state; individual receipts match counts. |

Manual observations above were performed by `codex-independent-reviewer`; their process exit is not applicable.

### Commands executed and durable observations

All shell processes used RTK with all-stream scratch receipts and preserved exits. The reviewer used `git status --short`, scoped `git diff`, `git show HEAD:<path>`, targeted numbered reads, and the following independent checks. Python probes used `-B`; uv probes used `--no-sync`; `TMP`/`TEMP` were `C:/Temp/av-kit/s59/review-tmp`, `PYTHONDONTWRITEBYTECODE=1`, and uv cache output was confined to scratch. A successful probe exit means the probe ran; defect observations below remain failures of the product contract.

```json
{"schema_version":"evidence.v1","check_id":"s59-review-current-state","command":"rtk proxy uv run --no-sync python -B docs/execution/plans/2026-11-08-capture-crop-copy/identity.py --state-only (ELECTRON_RUN_AS_NODE unset; process-local core.excludesFile=C:/Temp/av-kit/s59-review-ignore.txt excludes only .claude/settings.local.json; process-local safe.directory=P:/av-kit)","cwd":"P:/av-kit","scope":"Current D6 input identity, documented ignore reconciliation","phase":"full","exit_code":0,"result":"pass","tested_state":"f15626c25af428e33c0274cb280eef6579455320+fd97e8484a122e30240b8aeb29933ec764ba893f4937436f2cfc2b59998c9587","output":"Recomputed state exactly equals the handoff's H1-2 full-gate state. No secret file read. This checks identity, not a fresh reviewer suite run."}
```

```json
{"schema_version":"evidence.v1","check_id":"s59-review-product-reproducers","command":"rtk proxy uv run --no-sync python -B C:/Temp/av-kit/s59-review-repros.py","cwd":"P:/av-kit","scope":"Scratch CaptureAdapter.crop with valid CMYK ICC; API-valid exact-half arrow intersection","phase":"targeted","exit_code":0,"result":"fail","tested_state":"f15626c25af428e33c0274cb280eef6579455320+fd97e8484a122e30240b8aeb29933ec764ba893f4937436f2cfc2b59998c9587","output":"VALID_PROFILE U.S. Web Coated (SWOP) v2 color_space CMYK bytes 557168. CMYK_REPRO source_mode CMYK source_icc_bytes 557168 crop_mode RGB crop_icc_bytes 0 source_unchanged True. BOX_ACCEPTED (89,125,8,44,False). ARROW_HALF_REPRO exact_entry (8,9/2), expected_half_up (8,5), actual_from (8,4), actual_to (7,0), carry clipped. Reversed segment gives (7,0)->(8,5)."}
```

```json
{"schema_version":"evidence.v1","check_id":"s59-review-independent-oracle","command":"rtk proxy uv run --no-sync python -B C:/Temp/av-kit/s59-review-probes.py","cwd":"P:/av-kit","scope":"RGB metadata/pixel control; 20000 seeded arrows against exact-rational clipping; 1 px and naming edge cases","phase":"targeted","exit_code":0,"result":"partial","tested_state":"f15626c25af428e33c0274cb280eef6579455320+fd97e8484a122e30240b8aeb29933ec764ba893f4937436f2cfc2b59998c9587","output":"RGB ICC: 588 bytes before/after, profile_equal True, pixels_equal True, source_unchanged True. Arrow oracle: dropped 15270, kept 39, clipped 4691, 2 endpoint-rounding mismatches. 1 px region marks/rect/text match the stated edge rules. CON.txt -> crop_CON.txt; ../foo -> foo; invalid names receive fixed refusals; 240-character source gives a 105-character derived stem."}
```

```json
{"schema_version":"evidence.v1","check_id":"s59-review-red-proof","procedure":"Ran red-check.py through rtk proxy uv run --no-sync python -B with --require test_ac_130_1 through test_ac_130_7 against s59-py-red-carry.txt; test_ac_130_8 through test_ac_130_22 against s59-py-red-crop.txt; AC-130.23 through AC-130.29 against s59-mcp-red.txt and s59-ui-red.txt. Ran red-check.py --selftest separately. All four commands preserved exit 0.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"All 29 required AC Red titles and checker negative controls","phase":"red","exit_code":null,"result":"pass","tested_state":"Current checker; historical Red receipts","output":"Carry: 1 receipt, 7 required tests, 0 problems. Crop: 1 receipt, 15 required tests, 0 problems. MCP/UI: 2 receipts, 7 required tests, 0 problems. Selftest: 36 fixtures, 11 positive, 25 negative, 0 wrong."}
```

```json
{"schema_version":"evidence.v1","check_id":"s59-review-receipt-and-schema-audit","command":"rtk proxy python -B C:/Temp/av-kit/s59-review-receipts.py","cwd":"P:/av-kit","scope":"Baseline/row/full-gate receipts, OpenAPI structure and test-id diff","phase":"targeted","exit_code":0,"result":"pass","tested_state":"f15626c25af428e33c0274cb280eef6579455320+fd97e8484a122e30240b8aeb29933ec764ba893f4937436f2cfc2b59998c9587","output":"Full receipts: Python 1559 passed with no warning summary; UI 114 files/1193 passed; MCP 35 files/485 passed; crop 23 passed. Green rows: 221 carry, 497 crop with the disclosed initial 21 warnings. OpenAPI adds only /api/v1/captures/{id}/crop and CaptureCropAppliedOut, CaptureCropIn, CaptureCropMarksOut, CaptureCropOut, CaptureCropRequestedOut; remainder_equal True. TEST_IDS_UNCHANGED True. An exploratory tests-only tsc receipt contains prior test-type errors; the claimed registered MCP typecheck/build steps are separately recorded clean."}
```

```json
{"schema_version":"evidence.v1","check_id":"s59-review-records-and-endings","command":"rtk proxy uv run --no-sync python -B C:/Temp/av-kit/s59-review-records.py","cwd":"P:/av-kit","scope":"Structured MEU/issue diffs, old parity cases, baseline working-copy endings and added home-path literals","phase":"targeted","exit_code":0,"result":"pass","tested_state":"f15626c25af428e33c0274cb280eef6579455320+fd97e8484a122e30240b8aeb29933ec764ba893f4937436f2cfc2b59998c9587","output":"MEU_OTHER_TOP_LEVEL_CHANGED []; MEU_ROWS_CHANGED ['MEU-130']; ISSUES_CHANGED_OR_REMOVED []; ISSUES_ADDED ['MCP-AUDIT-BASELINE-PENDING-CROP']; PARITY_OLD_CASES_UNCHANGED True; four expected crop cases added; ANCHOR_LINE_ENDINGS_CHECKED 34 MISMATCHES []; NEW_MODULE_ENDING LF; ADDED_HOME_PATH_LINES 0."}
```

## Verdict

`changes_required` — the agent-facing crop workflow is substantially implemented and its recorded full-gate evidence is genuine and current. F1 prevents the stated ICC-preservation intent from being achieved for a supported source format. F2 is a separate non-blocking one-pixel clipping error. No additional blocking defect was established.

**Follow-up:** correct F1 and add its regression; address F2's exact-half case. Rerun affected checks and obtain a fresh full gate after input changes, then return the complete rolling report for round 2. Corrections and H2 remain coordinator work; this reviewer made no repository edits and supplies no execution approval.

**Residual limits:** no fresh reviewer API/service or suite execution was permitted; integration conclusions use inspected real-stack tests and the matching receipts. No claim is made that historical test files were byte-identical without Red-time snapshots. Accepted EXIF-frame, saved-marks, bake-difference, scale and live-baseline limits remain as approved.

🕐 Completed: 2026-11-09 22:33 (EST)

## Corrections Applied (2026-11-09)

**Workflow**: `/execution-corrections`, called by the execution loop `s59-execution-2026-11-08-capture-crop-copy` after round 1
**Agent**: claude-code-local (Claude Opus 5.5), the implementer. This section is the author's account, not a review, and it sets no approval.

### Verified

- **F1 confirmed.** Row 5 added `_CROP_ICC_DROP_MODES` (`CMYK`, `YCbCr`, `LAB`) and set `icc = None` for them. That departed from D-482 and the `CROP_PIXELS` row, and row 5 did not record it as a deviation. The literal rule can't hold for these modes: PNG has no CMYK colour type, and a CMYK profile is not valid on RGB pixels.
- **D-506 (Mat's ruling).** The fix needed an amendment to an approved AC, so it went to Mat through the Human Decision Protocol with three options: convert through the profile (recommended), drop the profile and amend the contract, or do nothing. Mat's words (2026-11-09): "A: convert via profile (Recommended)". D-506 is recorded in the plan's decision log after D-476, and it amends D-482's `CROP_PIXELS` and AC-130.10.
- **F2 confirmed.** With floats, the reproducer's entry at `x=8` came out just under `y=9/2`, so `floor(y + 0.5)` gave 4. The reversed segment hit the tie from the other side and gave 5.
- **Category:** F1 is an approved contract that the code departed from without disclosure. F2 is floating-point error at an exact rounding tie.

### Siblings searched

- **The other conversions in the adapter.** The region `view` (`adapter.py:348`), the upright import (`:392`) and the bake (`_write_png`, `_write_lossy`) convert without carrying a profile. Those are Session 58 and earlier paths with no ICC contract, outside this delta, and unchanged.
- **The modes the crop keeps** (`_CROP_KEPT_MODES`) keep their profile as before. A png, jpg, jpeg or webp file decodes to one of them, or to `CMYK` for a CMYK JPEG.
- **Every arrow clip goes through `_clip_arrow`.** `CaptureService.crop_shot` (`services/capture.py:927`) and `tools/capture_bake_fixture.py:28` call `clip_mark`. `_round_half_up` has no other caller. The box and text clips use only integers.
- **The parity fixture.** Its four crop cases come from the real `clip_mark` and have no arrow, so the exact arithmetic doesn't change them. `tests/unit/test_capture_bake_fixture.py` reproduces the fixture and passed in the F2 Green.

### Red (tests first)

- **F2** (`s59-py-red-f2.txt`): `pytest tests/unit/test_domain_capture.py -k half_tie` gave 1 failed, 1 passed and 106 deselected.
  - `test_ac_130_3_arrow_half_tie_rounds_up[fwd]` (`tests/unit/test_domain_capture.py:803`) failed with `from_xy: (8, 4) != (8, 5)`.
  - `[rev]`, the reversed segment, passed. It is the control.
  - `red-check.py --require test_ac_130_3_arrow_half_tie_rounds_up` found 0 problems.
- **F1** (`s59-py-red-f1.txt`): `pytest tests/unit/test_capture_adapter.py -k cmyk -W error::DeprecationWarning` gave 1 failed, 2 passed and 46 deselected.
  - `test_ac_130_10_cmyk_icc_to_srgb` (`tests/unit/test_capture_adapter.py:1657`) failed at `assert None == <sRGB profile bytes>`: the crop had no `icc_profile`.
  - The two `test_ac_130_10_cmyk_plain_fallback` cases (`:1691`) (`none`, `junk`) passed. They are the controls for the fallback that D-506 keeps.
  - `red-check.py --require test_ac_130_10_cmyk_icc_to_srgb` found 0 problems.
  - The profile is a 320-byte ICC v2 CMYK profile that the test builds in bytes (`_cmyk_icc`, `:1584`): Lab PCS and a 2-point lut16 `A2B0`. No system profile is read.
  - The test checks that the profile's conversion differs from Pillow's plain one. It then checks that the crop's pixels equal `ImageCms.profileToProfile` of the decoded source's box, and that its `icc_profile` equals sRGB's bytes.

### Changes

- **`packages/core/src/avkit_core/domain/capture.py`** (CRLF kept). `_clip_arrow` (`:503`) computes `t0`, `t1` and each ratio as `fractions.Fraction`, so an exact half rounds up from either direction. `_round_half_up` (`:499`) now takes a `Fraction`. Nothing else changed.
- **`packages/infrastructure/src/avkit_infra/capture/adapter.py`** (CRLF kept).
  - `_CROP_ICC_DROP_MODES` became `_CROP_ICC_CONVERT_MODES` (`:74`).
  - The new `_to_srgb` (`:256`) builds an `ImageCms` transform from the source's profile to sRGB. It returns the converted RGB image and sRGB's profile bytes. With no profile, or one that raises `OSError`, `ValueError` or `PyCMSError`, it returns the plain RGB conversion and no profile.
  - In `crop` (`:395`), the converted-mode branch calls `_to_srgb` for those three modes. Every other mode is unchanged.
  - The import of `ImageCms` is the only other change.
- **Tests** (CRLF kept): `tests/unit/test_domain_capture.py` (the F2 test) and `tests/unit/test_capture_adapter.py` (`_cmyk_icc`, `_cmyk_jpeg` and the two F1 tests).
- **Records** (endings kept):
  - The plan (LF) amends the goal anchor's ICC clause, the user-facing behaviour, the `CROP_PIXELS` row and AC-130.10, and adds D-506.
  - 09 (CRLF) amends §Crop's delivered note at `:1053`.
  - The handoff carries the new tests, receipts and gate.
- No route, schema, MCP or OpenAPI file changed.

### Green and gate

- **F2 Green** (`s59-py-green-f2.txt`): 225 passed. The selection was `test_domain_capture.py`, `test_domain.py` (Session 54 RULE-1), `test_capture_service.py`, the crop module and the fixture reproduction.
- **Your oracle.** I reran `C:/Temp/av-kit/s59-review-probes.py` on the fix (`s59-f2-oracle.txt`): 0 mismatches in 20000 arrows, down from 2. Its CMYK line still shows 0 profile bytes, because that probe's CMYK source carries sRGB's RGB profile, which builds no CMYK transform. D-506 gives that case a plain conversion and no profile.
- **Your reproducer.** I reran `C:/Temp/av-kit/s59-review-repros.py` (`s59-f12-repros.txt`). The SWOP-profiled CMYK JPEG's crop is RGB and carries 588 bytes, sRGB's profile, where it carried 0 before. The source is unchanged. The arrow's entry is `(8, 5)` in both directions.
- **F1 Green** (`s59-py-green-f1.txt`): `test_capture_adapter.py -k ac_130` passed 15 under `-W error::DeprecationWarning`.
- **Static checks:** `pyright packages/` 0 errors (`s59-f12-pyright.txt`). `ruff check packages/ tests/ tools/capture_bake_fixture.py` passed after one E501 in the new test was wrapped (`s59-f12-ruff.txt`).
- **Gate** (`s59-gate-r2.txt`, H1-2 rerun on the whole tree; round 1's receipts are kept in `C:/Temp/av-kit/s59/gate-r1/`): the last line is "session-gate: all steps exit 0".
  - Suites: pytest 1564 passed with no warnings (1559 plus the 5 new cases); Vitest 1193 in 114 files and MCP 485 in 35 files, unchanged; the crop module 23 of 23.
  - Static and build: pyright 0 errors, ruff, the UI types and ESLint, the task contract (25 rows), scope-paths (48 changed paths, none outside scope, HEAD unmoved), the red-check selftest, the UI build, the OpenAPI check, the MCP types and build, and both renders passed. The same four steps were skipped as in round 1.
  - tested_state, the same before and after the gate and when recomputed afterwards: `f15626c25af428e33c0274cb280eef6579455320+431a6b2db44b53eb217c171bbdfbbc504431a9fe41dcd4cb79991ad72be8ab90`. Round 1 reviewed `f15626c25af428e33c0274cb280eef6579455320+fd97e8484a122e30240b8aeb29933ec764ba893f4937436f2cfc2b59998c9587`.

### Status

`corrections_applied`. This awaits the independent round-2 recheck. The implementer does not set `approved`.

## Recheck (Round 2)

**Workflow**: `/execution-critical-review` recheck
**Agent**: codex-independent-reviewer

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---------|-------------|----------------|
| F1 | open | fixed |
| F2 | open | fixed |

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

### Confirmed Fixes

- **F1 / CROP_PIXELS — fixed under D-506 (R1).** `packages/infrastructure/src/avkit_infra/capture/adapter.py:256` converts a usable source profile through ImageCms to RGB/sRGB and returns the destination profile; `:434` applies it to CMYK, YCbCr and LAB. Independent scratch crops verified managed CMYK and LAB pixels against `ImageCms.profileToProfile`, and plain RGB with no ICC for absent, junk and wrong-colour-space profiles. The system SWOP reproducer again read the 557168-byte CMYK profile: its crop now carries 588-byte sRGB, its pixels equal the managed conversion and differ from plain conversion, and the source hash is unchanged. Pillow could not build the tested YCbCr transform, so that case correctly exercised the fallback; no successful YCbCr transform is claimed. The synthetic 320-byte CMYK profile also produced a non-vacuous managed/plain difference. `_CROP_KEPT_MODES` (`:73`), kept-mode transparency (`:428`) and other RGB/RGBA conversions (`:437`) are unchanged. The independent RGB control preserved ICC and exact pixels; a second control retained ICC while stripping EXIF and Comment text.

  **Error boundary:** malformed/incompatible profile errors are caught at `adapter.py:264`; none escaped the scratch cases. Destination-profile creation/serialization and plain conversion are outside that local catch, and `crop` does not wrap the entire conversion block. Thus I do not claim that every hypothetical library failure is mapped by the adapter. Unexpected exceptions still reach the unchanged service cleanup and fixed, path-free 503 (`packages/core/src/avkit_core/services/capture.py:977`). The helper operates on image/profile bytes, not a profile pathname. No new input-triggered error or path disclosure was established.

- **F2 / MARK_CLIP_ARROW — fixed (R2).** `packages/core/src/avkit_core/domain/capture.py:516` and `:522` now derive the clipping parameters and intersections with Fraction from integer coordinates. The original arrow returns `(8,5) -> (7,0)`; its reverse returns `(7,0) -> (8,5)`. The rerun exact-rational oracle found **0 mismatches in 20000** cases: 15270 dropped, 39 kept and 4691 clipped. Closed-rectangle Liang–Barsky rejection, endpoint clamping, rounded-zero dropping and direction are preserved (`:513-535`). `_round_half_up` (`:499`) still adds floating `0.5` at the final rounding operation; exact halves in the reproduced image-coordinate range remain exactly representable. This is a verified repair of the reported half-tie defect, not a claim that the last operation is rational arithmetic. Reconstructed round-1 source confirms the box/text helpers are unchanged (`:455`, `:474`, `:489`). The parity fixture and its four crop cases are unchanged.

**R3 — correction scope and siblings accepted.** I reconstructed both round-1 source files in memory from their saved Git diffs and checked their recorded blob hashes. Only `_clip_arrow`/`_round_half_up` changed in the domain; only `_to_srgb`/`crop`, their imports/constants and explanatory text changed in the adapter. Current Git blob hashes match the prior receipts for the API route/schema, service, enum/port, MCP toolset/registry/audit step, OpenAPI, fixture generator, parity JSON and inspected regression pins. There is no route, schema, MCP or OpenAPI correction. The region view (`adapter.py:319`), upright import (`:385`), bake (`:449`) and PNG/lossy writers are semantically identical to HEAD; the author's Session 58 sibling notes hold. No additional sibling in this session's implementation needs the ICC or arrow fix. The existing accepted source-safety, naming, cleanup, baseline-pending and scope conclusions stand.

**R4 — regression strength and Red/Green accepted, with a historical limit.** Both new regressions are **Strong**: `tests/unit/test_domain_capture.py:795-816` fixes both directional endpoint tuples and checks the carried mark; `tests/unit/test_capture_adapter.py:1657-1685` establishes source mode/profile, asserts managed pixels differ from plain pixels (`:1678`), then checks output mode/size, sRGB profile and exact managed bytes. The fallback cases (`:1688-1711`) assert both exact plain pixels and no ICC. No skip, setup bypass or weakened expectation was found.

The actual Red receipts show F2's forward assertion `(8,4) != (8,5)` with its reverse passing (**1 failed, 1 passed**) and F1's missing-profile assertion with both fallback controls passing (**1 failed, 2 passed**); both saved child exits are 1. Independent `red-check.py --require` reruns each returned **0 problems, exit 0**. Its selftest returned **36 fixtures, 0 wrong**. The Green receipts report **225 passed** for F2 and **15 passed** for F1. Every assertion exposed by the Red traceback still matches the current test AST (2/2 for F2, 6 exposed of 7 current assertions for F1); parameter values match. The Green summaries contain no complete test-file snapshot, so byte-for-byte immutability across the historical Red and Green runs cannot be independently certified. No evidence of assertion weakening was found. `s59-f12-ruff.txt` contains the initial E501, not a clean run; the fresh `s59-D6-py-lint.txt` establishes the later clean result after wrapping.

**R5 — evidence freshness and amended records accepted.** With `ELECTRON_RUN_AS_NODE` unset, the independently executed `identity.py --state-only` returned exactly:

```text
f15626c25af428e33c0274cb280eef6579455320+431a6b2db44b53eb217c171bbdfbbc504431a9fe41dcd4cb79991ad72be8ab90
```

This matches `s59-gate-r2`, its before/after identities and the handoff's full record (`.agent/context/handoffs/2026-11-08-capture-crop-copy-MEU-130-handoff.md:179`). Process-local Git settings preserved the harness settings, added `safe.directory=P:/av-kit`, and used a scratch ignore file containing only `.claude/settings.local.json`. That path was never opened. Direct receipt reads confirm **pytest 1564 passed with no warning summary; Vitest 1193 in 114 files; MCP 485 in 35 files; crop 23; scope-paths 48, outside scope [], HEAD unmoved**. The gate ends `session-gate: all steps exit 0`; its four disclosed skips remain as approved. The post-handoff drift/OpenAPI/handoff/AC/evidence receipts agree with the updated records. I did not rerun suites, the gate, exporter, renderer or live audit.

D-506's actual ruling is present at `implementation-plan.md:772`; its amended CROP_PIXELS (`:118`) and AC-130.10 (`:287`), the delivered note (`docs/build-plan/09-screenshot-capture.md:1053`) and handoff AC/correction records (`:70`, `:77`, `:125-133`, `:163-179`) describe the fixed behavior and observed counts. Byte inspection confirms **CRLF only** for domain/capture.py, adapter.py, test_domain_capture.py, test_capture_adapter.py and 09; the plan remains **LF only**. H2 and the pending reviewer/status fields remain coordinator work as specified.

Independent commands and durable observations (all preserved exit 0):

```json
{"schema_version":"evidence.v1","check_id":"s59-r2-review-color","command":"rtk proxy uv run --no-sync python -B C:/Temp/av-kit/s59-r2-mode-probes.py","cwd":"P:/av-kit","scope":"Scratch CMYK/LAB/YCbCr conversion matrix, synthetic ICC, system SWOP pixels, RGB metadata","phase":"targeted","exit_code":0,"result":"pass","tested_state":"f15626c25af428e33c0274cb280eef6579455320+431a6b2db44b53eb217c171bbdfbbc504431a9fe41dcd4cb79991ad72be8ab90","output":"12 mode/profile cases: exact managed or plain pixels, correct ICC presence, unchanged source hashes. Synthetic profile and SWOP differ from plain RGB. SWOP pixels equal managed RGB. RGB ICC retained; EXIF/text stripped. No successful YCbCr transform claimed."}
```

```json
{"schema_version":"evidence.v1","check_id":"s59-r2-review-arrow","command":"rtk proxy uv run --no-sync python -B C:/Temp/av-kit/s59-review-probes.py","cwd":"P:/av-kit","scope":"Independent exact-rational 20000-arrow oracle, RGB pixel/profile and edge controls","phase":"targeted","exit_code":0,"result":"pass","tested_state":"f15626c25af428e33c0274cb280eef6579455320+431a6b2db44b53eb217c171bbdfbbc504431a9fe41dcd4cb79991ad72be8ab90","output":"ARROW_ORACLE dropped 15270, kept 39, clipped 4691; mismatches 0. RGB 588 ICC bytes retained, exact pixels, source unchanged. CMYK carrying an incompatible RGB profile correctly falls back with no ICC under D-506."}
```

```json
{"schema_version":"evidence.v1","check_id":"s59-r2-review-state","command":"rtk proxy uv run --no-sync python -B docs/execution/plans/2026-11-08-capture-crop-copy/identity.py --state-only","cwd":"P:/av-kit","scope":"Current D6 identity, ELECTRON_RUN_AS_NODE unset, only the documented local-settings path ignored","phase":"full","exit_code":0,"result":"pass","tested_state":"f15626c25af428e33c0274cb280eef6579455320+431a6b2db44b53eb217c171bbdfbbc504431a9fe41dcd4cb79991ad72be8ab90","output":"Recomputed identity exactly matches the fresh handoff gate record and both gate identities. Identity check, not a reviewer suite run."}
```

Supplementary scratch checks: `s59-review-repros.py` verified SWOP profile retention and the original half-tie in both directions; `s59-r2-compare.py` reconstructed and compared round-1 source; `s59-r2-audit.py` checked historical blob hashes, source siblings, receipts, exposed Red assertions and file endings. Each ran through `rtk proxy uv run --no-sync python -B` with exit 0. All reviewer image/probe/checker output stayed under `C:/Temp/av-kit`; no repository file, real inbox, secret, application state or Git ref was written. No network was used.

### Remaining Findings

None.

### Verdict

`approved` — F1 is fixed against Mat's amended D-506 contract, F2's directional half-tie is fixed, and the fresh full-gate evidence matches the independently recomputed current inputs. No new material defect was established. The registered intent is achieved as amended by D-506. Historical snapshot and direct reviewer suite-execution limits remain stated above; H2 closeout remains with the coordinator.
