---
date: "2026-11-09"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-08-capture-region-import/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s58-execution-2026-11-08-capture-region-import"
round: 2
---

# Critical Review: 2026-11-08-capture-region-import

> **Review Mode:** execution · **Verdict:** changes_required · **Intent achieved:** partial

## Scope

Independent Codex review of Claude Code/Anthropic's Session 58, MEU-128 and MEU-129, against HEAD/baseline `e0c1d0bce56dc2501f5fba785c4d1a1ded62fe52`. The scope is the uncommitted delta, including the new integration module and both correlated handoffs. Applied IR-1 through IR-7, relevant DR checks and the approved contracts D-407 through D-427. The reviewer did not author the implementation.

**Intent anchor:** Session 58 lets an agent look at any part of a capture at full resolution and bring any local image into the capture inbox. `GET /captures/{id}/image` and MCP `image` take an optional region in original pixels or in fractions rounded outward. The region is clamped to the image and fitted inside `max_edge` (default 1568, at most 4× up) with Lanczos resampling. No file is written. The frame is reported in five response headers and, through MCP, in a text item before the image. `POST /captures` with `mode: import`, and MCP `capture` with `mode: import`, copy a local png, jpg, jpeg or webp into the inbox root as a new shot with source `Import`. An EXIF-rotated image is written as an upright PNG. A file already in the inbox root registers in place, and the source file is never changed.

All writes stayed under `C:/Temp/av-kit`. No product test runner, gate, application, import against an inbox, network request or Git mutation was run. Image probes used scratch images; import failure probes executed the current methods extracted from their AST against an in-memory filesystem/unit of work. They did not instantiate production services or touch an inbox. The supplied full-stack/Electron receipts provide the integration evidence. H2 remains subsequent coordinator work; accepted limitations and future MEU-130/131/132 work are not findings.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F1 | High | yes | behavior | **IMPORT_COPY can overwrite or delete a pre-existing temporary file.** With `shot.png.avkit-tmp` already in the inbox and `shot.png` absent, `_import_dest` selects `shot.png`. The first write opens the existing temporary path destructively; if that write fails before changing any bytes, the exception handler still deletes the pre-existing file. A user retrying an import after an interrupted operation can lose existing inbox content. The independent in-memory probe preserved the real method bodies, injected a first-write failure and observed the pre-existing file disappear. This violates AC-129.9's rollback contract and D-418's explicit restriction that cleanup remove only files this import wrote. | `packages/core/src/avkit_core/services/capture.py:514-525`; `packages/core/src/avkit_core/services/capture.py:540-544` | Reserve both destination and temporary names, create the temporary file exclusively and track ownership before cleanup. A failed attempt to acquire an existing temporary path must preserve it. Add successful-write and first-write-failure cases with a pre-existing temporary file. | fixed |
| F2 | High | yes | behavior | **File-error mapping is incomplete, allowing private paths into the Console and returning 500 for file refusals.** Import calls `exists`, `is_file`, `stat` and `resolve` outside its protected read. An unreadable parent or failed metadata lookup raises a raw `PermissionError`; the current API logger includes its path in the `error` field, which survives `console_field`. The probe observed `api.unhandled_error PermissionError: [Errno 13] Permission denied: 'C:/private/s58PARENTMARKER/photo.png'`. The new view path also leaves its second `read_bytes` outside its handler; a read failure leaks the same way. Separately, a scratch PNG with an incomplete IDAT followed by an invalid chunk raises an uncaught `SyntaxError` during `view`, giving 500 instead of the fixed decode refusal. AC-129.8/.10/.11 and NO_RAW_CONSOLE/D-421 are not satisfied across these file failures; the view gap also affects AC-128.10/D-410. | `packages/core/src/avkit_core/services/capture.py:449-469`; `packages/infrastructure/src/avkit_infra/capture/adapter.py:297-311`; logging sink `packages/api/src/avkit_api/errors.py:77-87` | Map filesystem failures throughout the new import checks and view reads to the specified path-free domain errors. Include Pillow decode failures such as `SyntaxError`, and cover the in-place probe's metadata read. Add fault tests for denied parent/stat/read and malformed PNG decoding; verify masked errors under the real HealthService logging setup. | fixed |

Both findings have **High confidence**, subject **deliverable**, kind **behavior**, and ledger contract family **AC-129**. F2 also cites affected AC-128 behavior in its prose. Neither is a control-defeat finding. No Critical finding was established.

## Checklist Results

### Q1 — REGION_RESOLVE, REGION_ERRORS and VIEW_SCALE

**Accepted.** Integer conversion precedes px addition; fractions use the approved 9-place guard before outward rounding. The thirteen error cases and ordering match the plan. Probes returned horizontal bounds 100–300, 29–79, 100–601 and 79–480 for the four guard cases; `1e308` gave the fixed outside-image error, and NaN/infinity gave the finite-number error. Clamp reporting and the 4×/shrink-only paths are correct. A 10000×8 region at 64 returns 64×1. **Not accepted:** none.

### Q2 — VIEW_FORMAT and RETURN_UNCHANGED

**Accepted.** Size mismatch maps to 409; crop/Lanczos, palette conversion, JPEG RGB and in-memory format encoding match the contract. The independent pixel comparison returned `lanczos (80, 64) True`; the whole-frame comparison returned `unchanged True`. No view invokes EXIF transposition or writes a file. **Not accepted: F2.** Actual malformed PNG decoding raises `SyntaxError`; a fault at the second file read escapes with its path. Existing tests exercise text masquerading as PNG, which does not cover these cases.

### Q3 — Route, FRAME_HEADERS and OVERSIZE_HINT

**Accepted.** All successful route branches attach the five formatted headers, including both variants and the legacy no-field branch. Without fields, the existing read path and bytes are preserved. Variant/missing-file checks and the 15 MiB cap remain; the 413 text changes as specified. Recursive OpenAPI comparison found only the six new query parameters, 200 header documentation, `CaptureImportIn`, its discriminator mapping and union member. **Not accepted:** the new view's error escapes are F2; no independent route-shape defect was found.

### Q4 — MCP query, frame item and image cap

**Accepted.** Query forwarding is gated on GET, and region/import POST bodies retain their fields without a query. Zod applies the specified numeric bounds and unit enum. The parser checks tuple shape, numeric text, positive finite scale and the boolean spelling; a missing or syntactically malformed required header returns the image alone. Frame JSON and mapping precede the image. `apiBinary` collects only lowercased `x-capture-*` headers. The hint names `max_edge (64 to 2576)` and a region; the 7,800,000 B cap and existing cap/stdio guards remain. The parser trusts server-generated image dimensions; no additional upstream threat model is imposed. **Not accepted:** none material to the delivered API/MCP path.

### Q5 — Import acceptance, copy, orientation, naming and persistence

**Accepted.** Strict schemas, 50,000,000-byte cap, refusal ordering, full verify/reopen/load and decompression-bomb refusal match the plan. Orientations 2–8 use upright PNG; 1/none use byte copies. Root imports preserve an existing id/source and refresh changed size, while new root rows use `Import`. Normal final-name collisions include case-folded inbox entries and stale rows. Source data is only read. Import and scan share `CAPTURE_FILE_LOCK`; copy/probe/register/commit are inside the rollback boundary. The enum is appended without a wire-map or migration change, preserving existing rows. **Not accepted: F1** for temporary-file ownership and **F2** for unguarded file checks. Normal copy/replace/probe/commit fault tests start with an empty inbox and therefore miss F1.

### Q6 — NO_RAW_CONSOLE and outside text

**Accepted for tested paths.** No logging statement was added. Sanitized stems alone reach copy names; normal registration logs only id/source, and the upright writer's `path` key is omitted by the Console allowlist. AC-129.11 resets HealthService and calls `build_services`, checks stdout/stderr, the ring, errors and an existing console log, with `engine.created` and two registration events as its positive controls. Its marker checks meaningfully test the exercised paths. **Not accepted: F2.** That test does not trigger a failed metadata lookup or the view's second read. An actual call to `log_unhandled_error` with the propagated source error, captured through a temporary fake logger, followed by the real `console_field`, retained the marker/path. No changed tracked file was found to acquire the user's home folder; reports use `<HOME>` if needed.

### Q7 — AC tests, Red/Green and regression evidence

**Accepted.** All 24 AC-128 and 13 AC-129 sub-IDs appear in their handoffs and current tests. Independently rerunning `red-check.py` against the four original receipts required **16 / 6 / 10 / 2** test ids and found **0 problems** each. Red summaries are **28 failed/1 passed**, **6 failed/1 passed**, **29 failed/1 passed**, and **2 failed**; guards pass as designed. Failures are assertions rather than setup errors. Green receipts show Python **200**, then **274**, and MCP **477**, then **479**. Current assertions agree with the decisive Red diagnostics. The supplied material contains no per-phase test-file hash snapshots, so byte-for-byte immutability between Red and Green cannot be independently reconstructed; the disclosed row-5 ruff repairs concern import ordering, and no weakened expectation was identified.

IR-5 grades for the changed test coverage:

| Test file / ACs | Grade | Observation |
|---|---|---|
| `tests/unit/test_domain_capture.py`: AC-128.1, .2, .3, .4, .5; AC-129.1 and source tuple | Strong | Exact region, scale, error, enum-order and value assertions. |
| `tests/unit/test_capture_adapter.py`: AC-128.6, .7, .8, .9, .10 | Strong for stated cases | Pixel/format/size comparisons, filesystem metadata guard and exact mapped errors. Decode-error coverage needs F2. |
| `tests/e2e/test_api_capture_region_import.py`: AC-128.11, .12, .13, .14, .15, .16, .17 | Strong | Real service/API/database stack; exact bytes, frames, pixels, errors and list-based recovery. |
| Same integration file: AC-129.2, .3, .4, .5, .6, .7, .8, .10 | Strong for stated cases | Strict input, copy/source integrity, naming, all orientations, identity/source and fixed refusal assertions. Metadata-failure cases need F2. |
| Same integration file: AC-129.9, .11 | Adequate | Meaningful rollback/log controls, but existing temporary ownership and additional file-error paths are untested (F1/F2). |
| `mcp-server/tests/capture.test.ts`: AC-128.18, .19, .20, .22, .23, .24; AC-129.12, .13 | Strong | Exact query/body, frame ordering/JSON, size refusal, schema bounds, advertised fields and timeout spy. |
| `mcp-server/tests/client.test.ts`: AC-128.21 | Strong | Exact header equality excludes unrelated headers. |
| `tests/unit/test_domain.py`, `tests/e2e/test_api_captures.py`: changed source tuples | Strong | Enum/API source contract updated; existing regression tests preserved. |

No introduced skip/xfail, assertion bypass or placeholder was identified. AC-37/38 source/action contracts, AC-67/111 image limits and AC-84 scan locking remain. `ui/tests/e2e/test-ids.ts` has no diff, preserving AC-51/81. The original gate receipts independently corroborate **1416 Python**, **1183 UI / 113 files**, **479 MCP / 35 files**, **36 region-import**, and **43 Electron capture-inbox** passes. **Not accepted:** green coverage does not disprove F1/F2.

### Q8 — Evidence, freshness and records

**Accepted.** With `ELECTRON_RUN_AS_NODE` unset, the independently recomputed identity is exactly:

`e0c1d0bce56dc2501f5fba785c4d1a1ded62fe52+d70b2324f4c6058ac99194a6a09a97dd9dc2bb9d0dcf1ba1f49db4f712b5bd19`

The scratch-only Git excludes file ignores just `.claude/settings.local.json`; that file was never opened. Existing sandbox `safe.directory` entries were preserved. UV's cache was redirected into scratch after its default cache access was denied. These environment accommodations changed no repository file or gated input.

Both evidence.v1 sets agree with the baseline, type, Red/Green, records and full-gate receipts, including the reported skips. HEAD is unchanged; no baseline failure was excused. The before-issue snapshot equals HEAD's register, and the current register appends only the filed D-424 issue. SSOT diffs touch only MEU-128/129 and their render; grouping changes only row 58. 00/05/09 describe the normal delivered behavior accurately, but their universal safe-error/cleanup claims need the F1/F2 corrections. Observed worktree CRLF/LF styles match the plan's list, including LF `00`, client files, state/register files and the new integration module. Git blobs are normalized LF by `.gitattributes`; that does not establish an ending change. The UI test-id file and lockfiles are unchanged after Git's normal EOL normalization.

**Not accepted:** no freshness or fabricated-count finding; the gate is real and current, but misses the two reproduced defects.

### IR/DR and adversarial summary

| Check | Result | Observed basis |
|---|---|---|
| IR-1 live integration | pass | Real-stack integration source and recorded 36-case runtime run; recorded 43-case Electron run. |
| IR-2 stub compliance | n/a | Product behavior uses real adapter/repositories; no new product stub. |
| IR-3 error mapping | fail | F2: uncaught metadata/read/decode errors. |
| IR-4 generalization | n/a | First execution-review round; no prior execution findings. |
| IR-5 test rigor | partial | Grades above; specific F1/F2 blind spots, no trivial pass identified. |
| IR-6 write boundary | pass | Strict import schemas and malformed/extra/missing input tests; no new update surface. |
| IR-7 AC/defer integrity | pass | All sub-IDs accounted for; future GUI/crop work is explicitly grouped and outside this session. |
| DR claim/evidence/freshness | partial | Receipts/counts/state verified; overbroad cleanup/error claims fail only as detailed in F1/F2. |
| AV-1/2/4/5/6 | pass | Real assertion-based Red/Green, no introduced masking/placeholder, sourced criteria. |
| AV-3 changed behavior asserted | partial | Normal paths asserted; F1/F2 lack the required negative cases. |

### Commands and durable reviewer observations

Commands ran from `P:/av-kit`, through `rtk proxy`, with all streams redirected under `C:/Temp/av-kit` and child exits captured before receipt reads. For the Python commands below, the process set `PYTHONDONTWRITEBYTECODE=1`, `TMP=TEMP=C:/Temp/av-kit/s58/review-tmp` and `UV_CACHE_DIR=C:/Temp/av-kit/s58/review-uv-cache`. The identity command additionally cleared `ELECTRON_RUN_AS_NODE` and added the single scratch ignore entry through process-local Git config, retaining both pre-existing safe-directory entries. The scratch scripts named here are retained beside the report to reproduce the observations; decisive output is embedded below.

```json
{"schema_version":"evidence.v1","check_id":"s58-review-contract-probes","command":"rtk proxy uv run --no-sync python -B C:/Temp/av-kit/s58-review-probe.py","cwd":"P:/av-kit","scope":"Domain functions; CaptureAdapter against scratch images; actual import method AST against in-memory filesystem/UoW; API error logger captured with fake logger and real console_field","phase":"targeted","exit_code":0,"result":"fail","tested_state":"e0c1d0bce56dc2501f5fba785c4d1a1ded62fe52+d70b2324f4c6058ac99194a6a09a97dd9dc2bb9d0dcf1ba1f49db4f712b5bd19","output":"fraction bounds 100-300,29-79,100-601,79-480; huge/NaN/Inf produce specified ValidationError; thin region 64x1; unchanged True; lanczos (80,64) True. import-first-write-denied CaptureFailedError the import could not be written remaining= {} (pre-existing temporary file lost). import-exists PermissionError [Errno 13] Permission denied: 'C:/private/s58PARENTMARKER/photo.png'; api-error-console-field api.unhandled_error PermissionError: [Errno 13] Permission denied: 'C:/private/s58PARENTMARKER/photo.png'. view-broken-idat 1 SyntaxError broken PNG file (chunk b'BAD!'); same for 2,4,8,16. view-second-read PermissionError carries scratch image path. Exit 0 means the probe completed and observed the failures, not that the product passed."}
```

```json
{"schema_version":"evidence.v1","check_id":"s58-review-red-and-record-audit","command":"rtk proxy uv run --no-sync python -B C:/Temp/av-kit/s58-review-audit.py","cwd":"P:/av-kit","scope":"Original Red receipts, required selectors extracted from task rows 2a/2b/4a/4b, OpenAPI JSON comparison, EOL styles, immutable cross-reference files, baseline/Green/record/validator receipt reads and handoff AC inventories","phase":"targeted","exit_code":0,"result":"pass","tested_state":"e0c1d0bce56dc2501f5fba785c4d1a1ded62fe52+d70b2324f4c6058ac99194a6a09a97dd9dc2bb9d0dcf1ba1f49db4f712b5bd19","output":"red-check independently rerun: 16/6/10/2 required ids, every exit 0 and 0 problems. OpenAPI changes only CaptureImportIn, import discriminator/oneOf, image GET parameters and 200 headers. Baseline suites 1357/1183/470; Green 200 then 274 Python, 477 then 479 MCP. Original issue snapshot equals HEAD; only append in current issue register. All 24 AC-128 and 13 AC-129 sub-IDs found. test-ids.ts and three lockfiles unchanged after Git EOL normalization; EOL styles match declared worktree styles."}
```

```json
{"schema_version":"evidence.v1","check_id":"s58-review-current-state","command":"rtk proxy uv run --no-sync python -B docs/execution/plans/2026-11-08-capture-region-import/identity.py --state-only","cwd":"P:/av-kit","scope":"Current D6 inputs and runtime, ELECTRON_RUN_AS_NODE unset; only forbidden local settings path excluded using scratch Git excludes file","phase":"static","exit_code":0,"result":"pass","tested_state":"e0c1d0bce56dc2501f5fba785c4d1a1ded62fe52+d70b2324f4c6058ac99194a6a09a97dd9dc2bb9d0dcf1ba1f49db4f712b5bd19","output":"e0c1d0bce56dc2501f5fba785c4d1a1ded62fe52+d70b2324f4c6058ac99194a6a09a97dd9dc2bb9d0dcf1ba1f49db4f712b5bd19; exact match to both handoffs and original gate identity-before/after."}
```

```json
{"schema_version":"evidence.v1","check_id":"s58-review-recorded-runtime","procedure":"Read s58-gate-h1.txt and the separate s58-D6-py-tests, ui-tests, mcp-tests, region-import and ui-electron receipts; compare their decisive summaries and before/after identity with both handoffs. Inspect the current integration fixtures for real build_services/create_app wiring.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"Recorded full-gate and real runtime evidence, independently inspected without rerunning prohibited suites","phase":"full","exit_code":null,"result":"pass","tested_state":"e0c1d0bce56dc2501f5fba785c4d1a1ded62fe52+d70b2324f4c6058ac99194a6a09a97dd9dc2bb9d0dcf1ba1f49db4f712b5bd19","output":"1416 passed; UI Test Files 113 passed, Tests 1183 passed; MCP Test Files 35 passed, Tests 479 passed; region-import 36 passed; Electron capture-inbox 43 passed. Every gate step exit=0; tested_state before=after; session-gate: all steps exit 0. This is acceptance of matching recorded execution, not a newly run reviewer product gate."}
```

## Verdict

**changes_required** — the intended region/import capability is implemented and supported by genuine, matching gate evidence. F1 permits loss of pre-existing inbox content during rollback; F2 permits path-bearing file errors to reach the Console and misclassifies file failures as 500. Correct those behaviors and add focused negative cases, then rerun the affected checks and the full gate for the changed inputs before re-review. No repository correction was made by this reviewer.

**Open questions:** none requiring a new product decision. **Residual limits:** the approved stale-header, lossy-view and scanned-EXIF limitations remain accepted; no fresh reviewer product-suite or Electron run is claimed. This report is the complete round-1 report for coordinator copying to the canonical review path.

## Corrections Applied (2026-11-09)

**Workflow**: `/execution-corrections`, called by the execution loop `s58-execution-2026-11-08-capture-region-import` after round 1
**Agent**: claude-code-local (Claude Opus 5.5), the implementer. This section is the author's account, not a review, and it sets no approval.

### Verified

- **F1 confirmed.** `_import_dest` listed the inbox names but not the temporary names, so with `shot.png.avkit-tmp` present it chose `shot.png`. The copy then opened `shot.png.avkit-tmp` with `write_bytes`, which truncates, and the `except` branch unlinked `tmp` whether or not this call had created it.
- **F2 confirmed, in four places.** In `import_image`, `exists`, `is_file`, `stat` and `resolve` ran outside the `try` that guarded `read_bytes`. In `_import_in_place`, the `probe` catch took only `InboxPathError`, so the `OSError` from `probe`'s own `is_file`/`stat` escaped. In `CaptureAdapter.view`, the decode catch took `(UnidentifiedImageError, OSError)`, so Pillow's `SyntaxError("broken PNG file (chunk b'BAD!')")` escaped (reproduced for an `IDAT` cut to 1, 2, 4, 8 and 16 bytes and followed by an invalid chunk). The RETURN_UNCHANGED `path.read_bytes()` was unguarded.
- **Category:** an error-mapping gap on a file path, plus a cleanup that does not track ownership.

### Siblings searched

- `CaptureService._variant_path` (MEU-128's shared variant check) called `Path.is_file`, which raises `PermissionError` on a denied lookup in Python 3.12. It now goes through `_is_file`, which reads that as missing and gives the existing 404 text.
- `CaptureAdapter.probe` keeps its own `is_file` and `stat` outside its `try`, as before this session. Its two callers in this delta now map whatever it raises: the copy's call is inside the `except Exception` that gives the fixed 503, and the in-place call maps `InboxPathError` and `OSError` to the fixed 422.
- `CaptureAdapter.inspect_import` already catches `Exception`.
- **Left unchanged:** `CaptureService.read_image`, the no-field whole-image read, still calls `read_bytes()` unguarded. It predates this session; MEU-128 only moved its variant checks into `_variant_path`, and RETURN_UNCHANGED requires that a request without the new fields behaves as today. The same holds for the annotate, flatten and revert paths. A denied read there is today's behaviour and outside this session's delta. The fault tests could not reach any of them.

### Red (tests first)

`s58-fix-r1-red.txt`: `pytest tests/unit/test_capture_adapter.py tests/e2e/test_api_capture_region_import.py -k "test_ac_128_10 or test_ac_129_9 or test_ac_129_10"` gave 11 failed, 5 passed, 63 deselected. The 11 failures are the new cases and the 5 passes are the existing AC-128.10, AC-129.9 and AC-129.10 cases.

- `test_ac_128_10_view_maps_decode_and_read_faults` (`tests/unit/test_capture_adapter.py:1420`), 2 cases. `broken-chunk` raised `SyntaxError: broken PNG file`; `second-read` raised the path-bearing `PermissionError`.
- `test_ac_129_9_keeps_a_temporary_file_it_did_not_write` (`tests/e2e/test_api_capture_region_import.py:627`), 4 cases. `none` gave `'shot.png' == 'shot_2.png'`; `race` returned 201 over the other writer's file; `replace` and `commit` gave `[] == ['shot.png.avkit-tmp']`, so the other writer's file had been deleted.
- `test_ac_129_10_metadata_fault_is_422` (`:682`), 4 cases (`exists`, `is_file`, `stat`, `resolve`). Each gave `500 == 422`.
- `test_ac_129_10_in_place_probe_fault_is_422` (`:716`), 1 case. It gave `500 == 422`.

Each new case also asserts that no path reaches the response. The metadata case also asserts that its marker reaches neither stdout nor stderr. The AC-129.9 cases assert that the other writer's bytes are unchanged.

### Changes

- `packages/core/src/avkit_core/services/capture.py` (CRLF kept):
  - `_is_file` (`:81`): `Path.is_file` with an `OSError` read as missing. `_variant_path` (`:749`) uses it.
  - `import_image` (`:449`) resolves `self._inbox()` and then calls the new `_read_import` (`:470`) inside one `try`. `_read_import` runs IMPORT_ACCEPT's file checks in the same order with the same messages: missing, not a file, extension, size cap, annotated copy in the root, read. An `OSError` from any of them becomes `InboxPathError("the file could not be read")`.
  - `_import_in_place` (`:489`) maps `InboxPathError` or `OSError` from `probe` to `InboxPathError("the image could not be opened")`.
  - `_import_copy` (`:512`) creates `NAME.avkit-tmp` with `open("xb")`. `tmp` is set only once that open succeeds, so the cleanup unlinks only a temporary file this call created. A name that already exists raises `FileExistsError` into the fixed 503. An orientation 1 copy writes through the open handle; for 2 to 8, `write_upright_png` writes the exclusively created file after the handle closes.
  - `_import_dest` (`:549`) counts a name as taken when its `.avkit-tmp` is in the inbox root.
- `packages/infrastructure/src/avkit_infra/capture/adapter.py` (CRLF kept): `view` (`:291`) maps any exception from open, load or copy to `InboxPathError("the image could not be opened")`, and the same for an `OSError` from the RETURN_UNCHANGED read.
- No route, schema, MCP or OpenAPI file changed. `export_openapi.py --check` exits 0.

### Green and gate

- `s58-fix-r1-green.txt`: the same selection gave 16 passed, 63 deselected. pyright gave 0 errors (`s58-fix-r1-pyright.txt`) and `ruff check` passed (`s58-fix-r1-ruff.txt`).
- `ruff format --check` lists 23 files. These include files this session never touched, such as `domain/tts.py`. The plan's gate runs `ruff check`, not the formatter, so this is not a new failure.
- H1-2 was rerun on the whole tree. `C:/Temp/av-kit/s58-gate-h1.txt` ends `session-gate: all steps exit 0`. Every step exited 0: pytest 1427 passed, the region-import module 45 passed, UI 1183 passed in 113 files, MCP 479 passed in 35 files, Electron `capture-inbox.test.ts` 43 passed, pyright 0 errors, `ruff check` and eslint clean, scope-paths 35 changed paths with none outside scope. The tested_state was `e0c1d0bce56dc2501f5fba785c4d1a1ded62fe52+73cc442629ca09d3d38777f0f7638d8df51681653e330cc5dafe47d64dc2e599` before and after.
- The handoffs carry the new gate record, the counts, the moved AC-129.11 cite, the new tests in their AC rows, and the Red and Green records.

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

- **R1 / F1 — fixed: IMPORT_COPY, IMPORT_NAME and IMPORT_UPRIGHT.** `packages/core/src/avkit_core/services/capture.py:555` includes temporary names in the case-folded occupied-name set. At `:531`, `open("xb")` refuses an occupied temporary name without opening it destructively; `tmp` acquires a value only after that succeeds (`:532`). The exception boundary includes writing, upright conversion, replace, probe, registration and UoW exit/commit (`:527-545`). Cleanup therefore has no temporary path to unlink after an exclusive-open refusal. With a pre-existing temporary file, the import chooses `_2`; with one appearing after listing, it returns the fixed 503 and preserves the other writer's bytes. Independent scratch probes also preserved those bytes through denied open, failed handle write, upright-write failure, replace failure, probe failure and commit failure, leaving no new copy or row on failure. Orientations 2–8 still write the reserved file as upright PNG through `write_upright_png` (`:536`; `packages/infrastructure/src/avkit_infra/capture/adapter.py:357`). All eight EXIF orientation probes matched transposed pixels, preserved source bytes/mtime and left no owned temporary file after success. Orientation 1 remained a byte copy.

- **R2 / F2 — fixed: IMPORT_ACCEPT, IMPORT_IN_PLACE, VIEW_FORMAT, RETURN_UNCHANGED and NO_RAW_CONSOLE.** `packages/core/src/avkit_core/services/capture.py:458-461` maps `OSError` from the complete source-file check/read sequence (`:470-487`) to `InboxPathError("the file could not be read")`. Independent faults at `exists`, `is_file`, `stat`, `resolve` and `read_bytes` all produced that fixed refusal. The in-place probe now maps both `InboxPathError` and `OSError` at `:494`, preserving the user's file. `packages/infrastructure/src/avkit_infra/capture/adapter.py:301-304` maps all open/load/copy decode exceptions; actual broken-IDAT decoding and injected SyntaxError, ValueError and RuntimeError each gave `InboxPathError("the image could not be opened")`. Its RETURN_UNCHANGED read now maps `OSError` at `:315-316`. These are mapped 422 domain errors; the API's domain handler returns the fixed text without calling `api.unhandled_error` (`packages/api/src/avkit_api/errors.py:131-152`), so their path-bearing causes do not enter the ring/stdout/stderr logging path. The new metadata integration cases additionally assert absence of their marker in captured stdout/stderr (`tests/e2e/test_api_capture_region_import.py:707-711`); the existing full-stack Console test remains at `:744` and passes in the recorded gate.

- **R2 sibling check — accepted.** `_is_file` (`packages/core/src/avkit_core/services/capture.py:81`) catches filesystem lookup errors only; `_variant_path` (`:749`) retains the original and annotated 404 messages and the invalid-variant validation error. Both denied-lookup probes returned the existing 404 text; unrelated programming exceptions are not swallowed by this helper. The no-field `read_image` read (`:716`) is the same operation as HEAD's pre-existing read. Leaving that read, annotate, flatten and revert unchanged is accepted within this session's scope and the approved no-field compatibility contract; it is not evidence that those older paths have universal file-error mapping.

**R3 — preserved behavior accepted.** The absolute-path refusal remains first (`packages/core/src/avkit_core/services/capture.py:456`). For the configured inbox, resolving `self._inbox()` before `_read_import` supplies the same resolved-root comparison; it neither creates a directory nor writes a file. `_read_import` preserves the missing → regular file → extension → size cap → annotated-root copy → read order and every specified message (`:473-487`). In-root files still register in place without rotating/copying (`:489-510`), and root annotated copies still refuse. Independent scratch probes confirmed in-place identity/source retention and annotated-copy refusal. The actual OpenAPI diff exactly matches the retained pre-corrections row-5 diff: no correction changed the route/schema contract. No additional product regression was established.

**R4 — regression evidence accepted, with an explicit limit.** The new tests are **Strong** for the reported defects: four foreign-temporary cases (`tests/e2e/test_api_capture_region_import.py:627`), four metadata cases (`:682`), one in-place-probe case (`:716`) and two view cases (`tests/unit/test_capture_adapter.py:1420`). They assert exact status/message, preservation or rollback, and path exclusion; the race case deliberately bypasses only name selection to exercise exclusive acquisition. The Red receipt identifies all 11 new cases and records the actual defects: escaping SyntaxError and PermissionError; `shot.png` instead of `shot_2.png`; 201 instead of 503 in the race; deletion of the foreign temporary file after replace/commit failure; and 500 instead of 422 for all five import error cases. The five existing cases passed. There is no collection/setup failure. Green records the same selection, **16 passed / 63 deselected**, with pyright 0 errors and ruff check clean. Current fault and assertion statements at `:671`, `:673`, `:676`, `:707`, `:737` and unit `:1441` agree with the Red diagnostics; no weakened expectation or bypass was identified. Historical per-test-file hash snapshots were not supplied, so byte-for-byte immutability between Red and Green cannot be independently proved. The evidence supports unchanged expectations, not an invented historical hash check.

**R5 — freshness and recorded execution accepted.** With `ELECTRON_RUN_AS_NODE` unset, the independently recomputed tested state is:

`e0c1d0bce56dc2501f5fba785c4d1a1ded62fe52+73cc442629ca09d3d38777f0f7638d8df51681653e330cc5dafe47d64dc2e599`

It exactly matches both handoffs' new full-gate records and the before/after gate identities. Process-local Git config used a scratch excludes file containing only `/.claude/settings.local.json`, preserving existing config entries; that forbidden file was never opened. The gate has **20 executed steps, all exit 0**, and its separate receipts corroborate **1427 Python**, **1183 UI / 113 files**, **479 MCP / 35 files**, **45 region-import** and **43 Electron capture-inbox** passes. Network audit, installer record and package build remain the declared skips. The recorded drift/OpenAPI/handoff/AC/full-evidence checks agree. All 24 AC-128 and 13 AC-129 sub-IDs remain accounted for, and the added test cites and correction descriptions match the files. A few introductory source anchors and the prose scope count are stale (the full record correctly says 35 paths); these do not change the behavior or execution evidence and are not findings.

Byte inspection confirms retained endings: service **1149 CRLF / 0 bare LF**, adapter **591 / 0**, adapter test **1447 / 0**; the new integration test has **0 CRLF / 801 LF**. No repository file was edited. H1-7 onward and H2 remain coordinator work after this verdict; this approval does not claim session closeout or authorize a commit.

Reviewer commands below ran from `P:/av-kit`, with all streams redirected under `C:/Temp/av-kit` and exits captured immediately. Python used `-B`, `PYTHONDONTWRITEBYTECODE=1`, `TMP=TEMP=C:/Temp/av-kit/s58/review-tmp`, and a scratch UV cache. No product test runner, gate, dev app, real inbox, network request or Git mutation was run. Service probes used the real current methods with a scratch filesystem and a fake repository/UoW; they are not claimed as fresh database/API/Electron integration runs.

```json
{"schema_version":"evidence.v1","check_id":"s58-r2-correction-probes","command":"rtk proxy uv run --no-sync python -B C:/Temp/av-kit/s58-r2-probe.py","cwd":"P:/av-kit","scope":"Current CaptureService methods with scratch images and fake UoW; current CaptureAdapter decoding and upright writes","phase":"targeted","exit_code":0,"result":"pass","tested_state":"e0c1d0bce56dc2501f5fba785c4d1a1ded62fe52+73cc442629ca09d3d38777f0f7638d8df51681653e330cc5dafe47d64dc2e599","output":"32 passed: foreign temporary ownership across none/race/open/write/upright/replace/probe/commit; EXIF orientations 1-8 correct, source unchanged, no owned temp; exists/is_file/stat/resolve/read_bytes faults mapped; in-place probe preserves source; root identity/source retained; annotated root refused; both denied variants give existing 404; RETURN_UNCHANGED read and SyntaxError/ValueError/RuntimeError plus actual broken IDAT map to fixed path-free errors."}
```

```json
{"schema_version":"evidence.v1","check_id":"s58-r2-current-state","command":"rtk proxy uv run --no-sync python -B docs/execution/plans/2026-11-08-capture-region-import/identity.py --state-only","cwd":"P:/av-kit","scope":"Current D6 inputs/runtime; ELECTRON_RUN_AS_NODE unset; only the forbidden local-settings path excluded through process-local Git config","phase":"static","exit_code":0,"result":"pass","tested_state":"e0c1d0bce56dc2501f5fba785c4d1a1ded62fe52+73cc442629ca09d3d38777f0f7638d8df51681653e330cc5dafe47d64dc2e599","output":"Exact match with both new handoff full-gate records and gate identity-before/after: e0c1d0bce56dc2501f5fba785c4d1a1ded62fe52+73cc442629ca09d3d38777f0f7638d8df51681653e330cc5dafe47d64dc2e599."}
```

```json
{"schema_version":"evidence.v1","check_id":"s58-r2-evidence-audit","command":"rtk proxy uv run --no-sync python -B C:/Temp/av-kit/s58-r2-audit.py","cwd":"P:/av-kit","scope":"Both handoffs' evidence/AC inventories; Red/Green receipts and current assertions; full-gate/step receipts; pre-corrections OpenAPI diff; raw file endings; remaining task rows","phase":"targeted","exit_code":0,"result":"pass","tested_state":"e0c1d0bce56dc2501f5fba785c4d1a1ded62fe52+73cc442629ca09d3d38777f0f7638d8df51681653e330cc5dafe47d64dc2e599","output":"24/24 and 13/13 AC sub-ids accounted for; both full records fresh/pass/exit 0 with exact matching state; 20 gate steps all exit 0; receipts 1427/1183/479/45/43; 11 new Red defect failures and 5 existing passes, Green 16 passes; current assertions agree with Red failure cites; OpenAPI diff unchanged since row 5; CRLF/bareLF counts service 1149/0, adapter 591/0, unit test 1447/0, integration test 0/801. Historical per-test-file byte immutability is not independently established."}
```

### Remaining Findings

None.

### Verdict

`approved` — F1 and F2 are fixed, the work achieves the registered intent, and no new material defect was established. Independent targeted probes and the matching recorded full gate support approval. The accepted plan limitations remain; no fresh reviewer product-suite or Electron pass is claimed.
