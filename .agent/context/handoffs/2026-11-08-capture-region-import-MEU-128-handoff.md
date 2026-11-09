---
date: "2026-11-09"
project: "capture-region-import"
meu: "MEU-128"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-08-capture-region-import/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "none"
---

# Handoff: 2026-11-08-capture-region-import-MEU-128-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-128 `capture-region-view`. `GET /captures/{id}/image` and MCP `image` take an optional region in original pixels or in fractions rounded outward. The region is clamped to the image and fitted inside `max_edge` (default 1568, 64 to 2576, at most 4× up) with Lanczos resampling, and no file is written. The frame is reported in five `X-Capture-*` headers and, through MCP, in a text item before the image. Without the new fields the bytes are today's. An oversize shot's error names `max_edge` and a region.
**Build Plan Section**: [09 §Region view](../../../docs/build-plan/09-screenshot-capture.md) (anchor `region-view`; the Delivered note at `:1000-1006`), 09's MCP `image` row (`:577`), and [05 §Capture](../../../docs/build-plan/05-mcp-server.md) (`:228-234`, `:323`, the Delivered note at `:337-342`).
**Predecessor**: none.

- **Domain (rows 1, 3; D-407, D-408, D-409).** `REGION_MAX_EDGE_DEFAULT`, `_MIN`, `_MAX` and `REGION_UPSCALE_MAX` (`domain/capture.py:28-31`), `ViewFrame` (`:126`), `RegionUnit` (`:141`), `resolve_region` (`:144`, `REGION_RESOLVE`), `view_scale` (`:197`, `VIEW_SCALE`) and `view_frame` (`:210`, `REGION_ERRORS`). Fractions round outward after a 9-place guard.
- **Adapter (rows 1, 3; D-410).** `CaptureAdapter.view` (`adapter.py:291`) checks the file's size against the frame's source size, crops, resizes with `Image.Resampling.LANCZOS` and encodes in memory in the path's format at `LOSSY_QUALITY` for JPEG and WebP (`VIEW_FORMAT`). A whole frame at scale 1 returns `path.read_bytes()` (`RETURN_UNCHANGED`). The port gains `view` (`ports/capture.py:35`).
- **Service and route (row 3; D-410, D-411).** `CaptureService.read_image_view` (`services/capture.py:718`) shares the variant checks with `read_image` through `_variant_path` (`:749`). `get_capture_image` (`routes/captures.py:315`) takes `x`, `y`, `width`, `height`, `unit` and `max_edge`, returns the file's bytes when none is given (`:331`), and sends the five headers on every 200 (`_frame_headers`, `:212-219`, `FRAME_HEADERS`), documented by `_FRAME_HEADER_DOCS` (`:63-84`) in the route's 200 `responses` (`:314`). The 413 detail `IMAGE_OVERSIZE_DETAIL` names `max_edge (64 to 2576)` and a region (`:59-61`, `OVERSIZE_HINT`).
- **MCP (row 3; D-412, D-413).** `GET_QUERY_KEYS` (`capture.ts:19`) gains the six fields, and the `image` member gains them with zod bounds (`:198`). `registry.ts:384` appends the query only for a GET row (`QUERY_GET_ONLY`). `parseCaptureFrame` (`registry.ts:225`) reads the five headers. The image branch (`:393-422`) returns the frame text item and then the image when all five parse (`:414`, `FRAME_ITEM`), and its oversize message names `max_edge (64 to 2576)` (`:404-405`). `ApiBinaryOk.captureHeaders` (`client.ts:161-162`) holds every `x-capture-*` header, lowercased (`:255-262`).
- **Spec text (row 6).** 09 `:282`, `:577`, `:578`, the Frame row's 9-place guard, the Frame report and Tests rows (D-412) and the Delivered note (`:1000-1006`); 05 `:228-234` and `:323` and the Delivered note (`:337-342`).

**Where values go (D-421, `NO_RAW_CONSOLE`).** The region fields and the frame are numbers. They go into the five response headers and the MCP text item and are never logged. A view's refusals are fixed messages that name no path: `REGION_ERRORS` (422), the changed-file `ConflictError` (409) and `InboxPathError("the image could not be opened")` (422). No log line was added. AC-129.11 views a region and triggers a view 422 under `build_services` with a marker in every folder name, and no stdout, stderr, ring or `console.log` line holds the marker; the MEU-129 handoff carries that receipt.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-08-capture-region-import/implementation-plan.md) §MEU-128. **Execution authorization:** `USER_EXPLICIT`, 2026-11-08, "proceed with execution", then "After S57 lands (Recommended)", given after the Codex plan review approved in round 3 ([plan-critical-review.md](2026-11-08-capture-region-import-plan-critical-review.md)) (`plan_to_exec_gate: human`).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-128.1 | unit | `REGION_RESOLVE`, px: `resolve_region(1000, 800, 100, 50, 200, 100, "px")` is `(100, 50, 200, 100, False)`, and `view_frame` gives the same region with `unit` defaulting to px | Local Canon: 09 `:990-991` | `tests/unit/test_domain_capture.py:511` | ✅ |
| AC-128.2 | unit | Fractions round outward, with the 9-place guard cases on W 1000, 100, 1001 and 799 | Research-backed: design D-4; D-408 | `tests/unit/test_domain_capture.py:524` | ✅ |
| AC-128.3 | unit | Clamp: px and fraction regions past the edge clamp with `clamped True`; a region inside is `clamped False` | Research-backed: design D-6 | `tests/unit/test_domain_capture.py:543` | ✅ |
| AC-128.4 | unit | Every `REGION_ERRORS` row (13 ids, `px-huge` included) raises `ValidationError` with its exact message | Local Canon: 09 `:991-992`; D-407 | `tests/unit/test_domain_capture.py:559` (13 cases) | ✅ |
| AC-128.5 | unit | `VIEW_SCALE`: 4× cap, `max_edge` fit, `max_edge` alone only shrinks, no fields give scale 1, a 10000×8 region at 64 gives 64×1; the four constants | Research-backed: design D-5; D-409 | `tests/unit/test_domain_capture.py:573` | ✅ |
| AC-128.6 | unit | At scale 1, `view` decodes to exactly `image.crop((10, 8, 30, 24))` | Local Canon: 09 `:993` | `tests/unit/test_capture_adapter.py:1277` | ✅ |
| AC-128.7 | unit | PNG resize is pixel-equal to Lanczos; a palette PNG with transparency goes through RGBA; RGBA stays RGBA | Research-backed: design D-5; D-410 | `tests/unit/test_capture_adapter.py:1292` | ✅ |
| AC-128.8 | unit | A `.jpg` view decodes as JPEG RGB and a `.webp` view as WEBP, at the returned size | Local Canon: D-410 | `tests/unit/test_capture_adapter.py:1332` | ✅ |
| AC-128.9 | unit | No file is written: names, sizes and `st_mtime_ns` unchanged after every kind of view | Local Canon: 09 `:993` | `tests/unit/test_capture_adapter.py:1350` | ✅ |
| AC-128.10 | unit | A source-size mismatch raises a path-free `ConflictError`; a `.png` holding text raises `InboxPathError("the image could not be opened")`, and so do a damaged PNG that makes Pillow raise `SyntaxError` and a failed RETURN_UNCHANGED read (review round 1, F2) | Local Canon: D-410 | `tests/unit/test_capture_adapter.py:1376`, `:1420` (2 cases) | ✅ |
| AC-128.11 | e2e | `RETURN_UNCHANGED` and `FRAME_HEADERS` with no field: exact bytes, today's media type, the five headers | Local Canon: 09 `:993-994` | `tests/e2e/test_api_capture_region_import.py:95` | ✅ |
| AC-128.12 | e2e | A px region at the default `max_edge` and at 2576; `variant=annotated` returns the annotated file's crop | Research-backed: design D-5 | `tests/e2e/test_api_capture_region_import.py:109` | ✅ |
| AC-128.13 | e2e | A fraction region past the edge reports the resolved px region and `X-Capture-Clamped: true` | Research-backed: design D-4, D-6 | `tests/e2e/test_api_capture_region_import.py:149` | ✅ |
| AC-128.14 | e2e | `max_edge=500` alone gives 500×250 at `0.250000`; `max_edge=2576` alone returns the exact bytes at `1.000000` | Local Canon: 09 `:993` | `tests/e2e/test_api_capture_region_import.py:165` | ✅ |
| AC-128.15 | e2e | 422 through the envelope for `partial`, `unit-alone`, `max-edge-low` and `outside`; `unit=inch` gives `validation_error` | Local Canon: D-407 | `tests/e2e/test_api_capture_region_import.py:182` | ✅ |
| AC-128.16 | e2e | With `IMAGE_MAX_BYTES` patched low, the 413 detail names `max_edge (64 to 2576)` on the whole-image and the region path | Local Canon: 05 `:318`; D-411 | `tests/e2e/test_api_capture_region_import.py:213` | ✅ |
| AC-128.17 | e2e | A replaced file: a region view gives a path-free 409 until `GET /captures`, then 200 with the new `X-Capture-Source` | Local Canon: D-410 | `tests/e2e/test_api_capture_region_import.py:231` | ✅ |
| AC-128.18 | unit (MCP) | `image` sends the six fields as query keys on the GET path | Local Canon: 09 `:990` | `mcp-server/tests/capture.test.ts:579` | ✅ |
| AC-128.19 | unit (MCP) | `capture` `mode: "region"` sends a POST body with the region and a path with no query string | Local Canon: D-413 | `mcp-server/tests/capture.test.ts:615` | ✅ |
| AC-128.20 | unit (MCP) | Five headers give the text item and then the image; without `X-Capture-Scale`, the image alone | Research-backed: design D-3; D-412 | `mcp-server/tests/capture.test.ts:640` | ✅ |
| AC-128.21 | unit (MCP) | `apiBinary` returns `captureHeaders` with the five `x-capture-*` headers, lowercased, and no other | Local Canon: D-412 | `mcp-server/tests/client.test.ts:201` | ✅ |
| AC-128.22 | unit (MCP) | An image over `IMAGE_MAX_BYTES` gives `payload_too_large` with today's text plus `max_edge (64 to 2576)` | Local Canon: 09 `:995`; MEU-111 | `mcp-server/tests/capture.test.ts:675` | ✅ |
| AC-128.23 | unit (MCP) | zod accepts a fraction region and refuses `x: -1`, `width: 0`, `unit: "inch"` and `max_edge` 63, 2577 and 100.5 | Local Canon: Boundary Inventory | `mcp-server/tests/capture.test.ts:690` | ✅ |
| AC-128.24 | unit (MCP) | The `image` description holds `max_edge`, `2576`, `fraction` and `region.x + x / scale` with at least three M7 markers; the advertised schema lists the six fields | Research-backed: design §6.7 | `mcp-server/tests/capture.test.ts:708` | ✅ |
| AC-129 (cross-ref) | cross-reference | MEU-129's ACs, AC-129.1 to AC-129.13, are owned and evidenced by the MEU-129 handoff; AC-129.11 also covers this MEU's view lines | plan §MEU-129 | [MEU-129 handoff](2026-11-08-capture-region-import-MEU-129-handoff.md) | ✅ |
| AC-37 (cross-ref) | regression | AC-37.10's 413 check reads only the status and passes unchanged; it takes the unchanged no-field path | plan §MEU-128 guards | `tests/e2e/test_api_captures.py:587` (the plan cited `:586`); gate `py-tests` | ✅ |
| AC-38 (cross-ref) | regression | AC-38.1, .2, .5, .11, .12 and .13 pass unchanged; `avkit_capture` keeps its 10 actions and `ACTION_INDEX` its 70 rows | plan §MEU-128 guards | `mcp-server/tests/capture.test.ts`; gate `mcp-tests` | ✅ |
| AC-67 (cross-ref) | regression | AC-67.17 (MCP actions, destructive flags, M7 descriptions) passes unchanged | plan §MEU-128 guards | `mcp-server/tests/capture.test.ts:435`; gate `mcp-tests` | ✅ |
| AC-111 (cross-ref) | regression | AC-111.1 to .4, the MCP image cap tests, pass unchanged; the image is found with `content.find` | plan §MEU-128 guards | gate `mcp-tests` | ✅ |
| AC-84 (cross-ref) | regression | AC-84.2 and the scan and register tests are MEU-129's guards; the MEU-129 handoff carries them, and they passed in the shared gate | plan §MEU-129 guards | [MEU-129 handoff](2026-11-08-capture-region-import-MEU-129-handoff.md); gate `py-tests` | ✅ |
| AC-51, AC-81 (cross-ref) | regression | `ui/tests/e2e/test-ids.ts` is unchanged (scope-paths refuses it, and S9 never fired), so AC-51.6 and AC-81.13 pass | plan §Files Modified; S9 | gate `scope-paths`, `ui-tests` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-128.1, AC-128.2, AC-128.3 | `assert (0, 0, 1000, 800, False) == (100, 50, 200, 100, False)` and the same stub tuple against each expected region | Row 3: pass | `test_domain_capture.py:511`, `:524`, `:543` |
| AC-128.4 | `Failed: DID NOT RAISE ValidationError` (13 cases) | Row 3: pass | `test_domain_capture.py:559` |
| AC-128.5 | `assert (0, 0, 1000, ...000, 800, ...) == (0, 0, 100, 50, 400, 200, ...)` | Row 3: pass | `test_domain_capture.py:573` |
| AC-128.6, AC-128.7, AC-128.8 | `assert (64, 48) == (20, 16)`; `assert (64, 48) == (80, 64)` (the stub returned the whole file) | Row 3: pass | `test_capture_adapter.py:1277`, `:1292`, `:1332` |
| AC-128.10 | `Failed: DID NOT RAISE ConflictError` | Row 3: pass | `test_capture_adapter.py:1376` |
| AC-128.10 (review F2) | `SyntaxError: broken PNG file (chunk b'BAD!')`; the second read's `PermissionError` escaped | Corrections: pass | `test_capture_adapter.py:1420` |
| AC-128.11, AC-128.13 | `assert (None, None, None, None, None) == ('40,30', '0,...000', 'false')`; `assert None == '200,150,200,150'` | Row 3: pass | `test_api_capture_region_import.py:95`, `:149` |
| AC-128.15 | `assert 200 == 422` | Row 3: pass | `test_api_capture_region_import.py:182` |
| AC-128.16 | `assert 'image exceed...AGE_MAX_BYTES' == 'image exceed...smaller image'` | Row 3: pass | `test_api_capture_region_import.py:213` |
| AC-128.17 | `assert 200 == 409` | Row 3: pass | `test_api_capture_region_import.py:231` |
| AC-128.18, AC-128.23 | `expected false to be true` (zod refused the fields) | Row 3: pass | `capture.test.ts:579`, `:690` |
| AC-128.20 | `expected [ 'image' ] to deeply equal [ 'text', 'image' ]` | Row 3: pass | `capture.test.ts:640` |
| AC-128.21 | `expected undefined to deeply equal { 'x-capture-source': '40,30', …(4) }` | Row 3: pass | `client.test.ts:201` |
| AC-128.22 | `expected 'payload_too_large: image exceeds the …' to contain 'max_edge (64 to 2576)'` | Row 3: pass | `capture.test.ts:675` |
| AC-128.24 | `max_edge: expected 'Workflow: call avkit_capture image to…' to contain 'max_edge'` | Row 3: pass | `capture.test.ts:708` |
| AC-128.9, AC-128.19 | Guards: pass in Red by design | Row 3: pass | `test_capture_adapter.py:1350`, `capture.test.ts:615` |

- **Row 1 (type-only):** the four constants, `ViewFrame`, `RegionUnit`, the region function stubs and the port's `view` stub, with no behavior. The domain and adapter suites passed 156, pyright 0 errors and ruff clean.
- **Row 2a Python Red:** 28 failed and 1 passed (AC-128.9, the guard), every failure by assertion. `red-check.py` required 16 tests and found 0 problems.
- **Row 2b MCP Red:** 6 failed and 1 passed (AC-128.19, the guard) in 2 files, each by assertion. `red-check.py` required 6 tests and found 0 problems.
- **Review round 1 corrections (F2):** the two AC-128.10 fault cases failed on the round-1 code with the escaping `SyntaxError` and `PermissionError` (`s58-fix-r1-red`), and passed after `view` mapped both (`s58-fix-r1-green`). `_variant_path` now reads a denied lookup as missing.
- **Row 3 Green:** the named Python suites passed 200; the OpenAPI check exited 0 after the file was regenerated (133 lines added, 1 removed: the six query parameters and the 200 response's five header docs); pyright 0 errors and ruff clean; the MCP suite passed 477 in 35 files and its typecheck was clean. No test file changed in row 3.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s58-0-baseline", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-08-capture-region-import/baseline.ps1 *> C:/Temp/av-kit/s58-baseline.txt (task.md row 0's Validation cell, run from P:/av-kit)", "scope": "Row 0: the S8 queue check, baseline.sha, baseline-dirty.txt with each dirty path's SHA-256, the offline locked installs, the pinned FFmpeg pair, the base Python, UI and MCP suites with TMP and TEMP outside the home folder, and the red-check and identity selftests", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD e0c1d0b (baseline.sha), before row 0", "output": "baseline-dirty.txt 1 paths; baseline.sha e0c1d0bce56dc2501f5fba785c4d1a1ded62fe52; ui lock sync: 651 locked packages, 0 differ, 0 missing; mcp-server lock sync: 133 locked packages, 0 differ, 0 missing; ffmpeg.exe 165577728 B: n8.1.3-27-g8dca1586f4-20261031; base py 1357 passed; base ui 1183 passed in 113 files; base mcp 470 passed in 35 files; identity selftest: 0 failure(s); baseline: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s58-128-types", "command": "$env:TMP='C:\\Temp\\av-kit\\s58\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest tests/unit/test_domain_capture.py tests/unit/test_capture_adapter.py --tb=short -q *> C:/Temp/av-kit/s58-types-py.txt; then pyright packages/ *> C:/Temp/av-kit/s58-types-pyright.txt and ruff check *> C:/Temp/av-kit/s58-types-ruff.txt (abridged from task.md row 1's Validation cell, run from P:/av-kit through an extracted .ps1)", "scope": "Row 1 type-only names: REGION_* constants, ViewFrame, RegionUnit, the resolve_region, view_scale and view_frame stubs, and the port's view stub, with no behavior", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD e0c1d0b plus rows 0 and 1", "output": "156 passed in 5.15s; pyright 0 errors, 0 warnings, 0 informations; ruff All checks passed!"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s58-128-red-py", "command": "$env:TMP='C:\\Temp\\av-kit\\s58\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest tests/unit/test_domain_capture.py tests/unit/test_capture_adapter.py tests/e2e/test_api_capture_region_import.py -k ac_128 --tb=short -q *> C:/Temp/av-kit/s58-py-red-128.txt; then red-check.py with the 16 --require ids *> C:/Temp/av-kit/s58-py-red-128-check.txt (abridged from task.md row 2a's Validation cell, run from P:/av-kit through an extracted .ps1)", "scope": "MEU-128 Python Red: AC-128.1 to AC-128.17 against the row 1 stubs, with Pillow images under tmp_path and no network", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD e0c1d0b plus rows 0 to 2a", "output": "28 failed, 1 passed, 42 deselected in 2.89s. Decisive: DID NOT RAISE ValidationError (13); assert (0, 0, 1000, 800, False) == (100, 50, 200, 100, False); assert (64, 48) == (20, 16); DID NOT RAISE ConflictError; assert (None, None, None, None, None) == ('40,30', '0,...000', 'false'); assert 200 == 422; assert 200 == 409. red-check: 1 receipt(s), 16 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s58-128-red-mcp", "command": "rtk proxy npm --prefix mcp-server run test -- tests/capture.test.ts tests/client.test.ts -t \"AC-128\" *> C:/Temp/av-kit/s58-mcp-red-128.txt; then red-check.py with the 6 --require ids *> C:/Temp/av-kit/s58-mcp-red-128-check.txt (abridged from task.md row 2b's Validation cell, run from P:/av-kit through an extracted .ps1)", "scope": "MEU-128 MCP Red: AC-128.18 to AC-128.24 against the unchanged capture.ts, registry.ts and client.ts", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD e0c1d0b plus rows 0 to 2b", "output": "Test Files 2 failed (2); Tests 6 failed | 1 passed | 30 skipped (37). expected [ 'image' ] to deeply equal [ 'text', 'image' ]; expected 'payload_too_large: image exceeds the …' to contain 'max_edge (64 to 2576)'; expected undefined to deeply equal { 'x-capture-source': '40,30', …(4) }; max_edge: expected 'Workflow: call avkit_capture image to…' to contain 'max_edge'. red-check: 1 receipt(s), 6 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s58-128-green", "command": "$env:TMP='C:\\Temp\\av-kit\\s58\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest (row 3's named suites) --tb=short -q *> C:/Temp/av-kit/s58-py-green-128.txt; then export_openapi.py --check *> C:/Temp/av-kit/s58-r3-openapi.txt, git diff -- openapi.committed.json *> C:/Temp/av-kit/s58-r3-openapi-diff.txt, pyright *> C:/Temp/av-kit/s58-r3-pyright.txt, ruff *> C:/Temp/av-kit/s58-r3-ruff.txt, npm --prefix mcp-server run test *> C:/Temp/av-kit/s58-mcp-green-128.txt and typecheck *> C:/Temp/av-kit/s58-r3-mcp-types.txt (abridged from task.md row 3's Validation cell, run from P:/av-kit through an extracted .ps1)", "scope": "MEU-128 Green: REGION_RESOLVE, REGION_ERRORS, VIEW_SCALE, VIEW_FORMAT, RETURN_UNCHANGED, FRAME_HEADERS, FRAME_ITEM, QUERY_GET_ONLY and OVERSIZE_HINT", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD e0c1d0b plus rows 0 to 3", "output": "200 passed in 11.03s. export_openapi --check: exit 0, no output. openapi.committed.json diff: 133 lines added, 1 removed (the x, y, width, height, unit and max_edge query parameters and the 200 response's X-Capture-Source, -Region, -Returned, -Scale and -Clamped header docs). pyright: 0 errors, 0 warnings, 0 informations. ruff: All checks passed! MCP: Test Files 35 passed (35); Tests 477 passed (477). tsc --noEmit clean."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s58-6-records", "command": "task.md row 6 (abridged), run from P:/av-kit: the 09, 00 and 05 notes; tools/meu_status.py update MEU-128 and MEU-129 ready_for_review --plan and render; issue-file.py *> C:/Temp/av-kit/s58-issue-file.txt; issue_triage.py render and triage; grouping row 58; then its Validation cell through an extracted .ps1 into s58-r6-render.txt, s58-r6-issues.txt and s58-r6-status.txt", "scope": "Row 6: the D3 spec text, both MEUs ready_for_review with this plan, CAPTURE-EXIF-SCANNED-ORIENTATION filed, the renders, and grouping row 58 executed", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD e0c1d0b plus rows 0 to 6", "output": "issue-file: before 5d9084c29298beba 394190; after 523fa184e7a34e74 397272 CRLF 0; added lines 38 removed lines 0; CAPTURE-EXIF-SCANNED-ORIENTATION open P3 ['D-424']. meu_status render: Loaded 132 MEUs across 12 phases; All regions rendered successfully. Validation: ['ready_for_review', 'ready_for_review'] open ['| 58 | `capture-region-import` | MEU-128, MEU-129 | P2 | executed | `docs/execution/plans/2026-11-08-capture-region-import/` |']; exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s58-fix-r1-red", "command": "$env:TMP='C:\\Temp\\av-kit\\s58\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run --no-sync pytest -q --tb=line -p no:cacheprovider tests/unit/test_capture_adapter.py tests/e2e/test_api_capture_region_import.py -k \"test_ac_128_10 or test_ac_129_9 or test_ac_129_10\" > C:/Temp/av-kit/s58-fix-r1-red.txt 2>&1", "scope": "Review round 1, F1 and F2: the 11 new fault cases against the round-1 code, with the 5 existing cases of the same ACs", "phase": "red", "exit_code": 1, "result": "fail", "tested_state": "HEAD e0c1d0b plus rows 0 to 6 and the new tests", "output": "11 failed, 5 passed, 63 deselected. Decisive: SyntaxError: broken PNG file (chunk b'BAD!'); PermissionError from the second read; assert 'shot.png' == 'shot_2.png'; the race returned 201; assert [] == ['shot.png.avkit-tmp'] (replace, commit); assert 500 == 422 (exists, is_file, stat, resolve, the in-place probe)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s58-fix-r1-green", "command": "the same pytest selection > C:/Temp/av-kit/s58-fix-r1-green.txt 2>&1; rtk proxy uv run --no-sync ruff check packages tests > C:/Temp/av-kit/s58-fix-r1-ruff.txt 2>&1; rtk proxy uv run --no-sync pyright packages > C:/Temp/av-kit/s58-fix-r1-pyright.txt 2>&1", "scope": "Review round 1 corrections: _import_copy's exclusive temporary file, _import_dest's temporary names, _read_import's mapped file checks, the in-place probe, _is_file in _variant_path, and view's decode and second-read mapping", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD e0c1d0b plus rows 0 to 6 and the corrections", "output": "16 passed, 63 deselected in 8.99s. ruff: All checks passed! pyright: 0 errors, 0 warnings, 0 informations"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s58-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-08-capture-region-import/session-gate.ps1 *> C:/Temp/av-kit/s58-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s58-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','mismatch','session-gate:'; exit $code", "scope": "H1-2: the registered D6 gate on the whole tree: identity, every static check, the three full suites, the UI build, OpenAPI, the MCP types, tests and build, both renders, the region-import module and the targeted Electron capture-inbox spec, then the identity again", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "e0c1d0bce56dc2501f5fba785c4d1a1ded62fe52+73cc442629ca09d3d38777f0f7638d8df51681653e330cc5dafe47d64dc2e599", "output": "identity-before exit=0; py-types exit=0 (0 errors); py-lint exit=0 (All checks passed!); ui-types exit=0; ui-lint exit=0 (eslint --max-warnings 0); task-contract exit=0 (26 rows, 24 fully checked, 2 view_file exempt: H1-5, H2-1); scope-paths exit=0 (changed paths: 35, outside scope: [], head moved (S3): False); red-check-selftest exit=0 (36 fixtures, 11 positive, 25 negative, 0 wrong); py-tests exit=0 (1427 passed); ui-tests exit=0 (113 files, 1183 passed); ui-build exit=0; openapi exit=0; mcp-types exit=0; mcp-tests exit=0 (35 files, 479 passed); mcp-build exit=0; state-render exit=0 (132 MEUs, 12 phases, regions match); issues-render exit=0 (known-issues.md is up-to-date); region-import exit=0 (45 passed); ui-electron exit=0 (capture-inbox.test.ts, 43 passed); identity-after exit=0 (tested_state before = after); mcp-audit, build-record and package-build skipped; baseline failures excused: py [], ui [], mcp []; session-gate: all steps exit 0"}
```

### Quality Gate Results

`s58-gate-h1-2` (H1-2) is the fresh full record for both MEUs, and its last line is:

> session-gate: all steps exit 0

- **Static:** pyright 0 errors; ruff check passed; the UI typecheck and ESLint (`--max-warnings 0`) passed; lint_task_contract passed on 26 rows (24 fully checked, 2 `view_file` exempt); scope-paths found 35 changed paths, none outside scope, `ui/tests/e2e/test-ids.ts` unchanged, and HEAD e0c1d0b did not move (S3); the red-check selftest read 36 fixtures with 0 wrong.
- **Suites:** pytest 1427 passed (the baseline's 1357 plus 70 new cases: 31 for AC-128.1 to .17 and 39 for AC-129.1 to .11, 11 of them added for review round 1's F1 and F2); Vitest 1183 passed in 113 files (the baseline's count, since no UI file changed); MCP tests 479 passed in 35 files (the baseline's 470 plus AC-128.18 to .24 and AC-129.12 and .13). No baseline failure was excused.
- **Build and state:** the UI build, the OpenAPI check, the MCP typecheck and the MCP build exited 0; the state render (132 MEUs) and the issue render match the files on disk.
- **Runtime:** the region-import module (`tests/e2e/test_api_capture_region_import.py`) passed 45 of 45 on its own, and the targeted Electron spec `tests/e2e/capture-inbox.test.ts` passed 43 of 43, so the Capture page still lists, opens and annotates shots in the built app. F2 was checked free before the gate. The pinned FFmpeg pair is unchanged from the baseline, and the identity binds the FFmpeg hashes and both lock files.
- **Skipped:** `mcp-audit` (live network, which the brief forbids), `build-record` (no installer build) and `package-build` (no packaged surface changes; MEU-125 ran the package build and its smokes).
- **Identity:** the tested_state was the same before and after the gate: `e0c1d0bce56dc2501f5fba785c4d1a1ded62fe52+73cc442629ca09d3d38777f0f7638d8df51681653e330cc5dafe47d64dc2e599`. It is re-derived with `ELECTRON_RUN_AS_NODE` unset, as H1-6b's cell does; the runtime identity records that variable, so a shell that has it set derives another state. The handoffs, reviews and other closeout records are artifacts the identity leaves out, so writing them doesn't change it.
- **Rerun after review round 1.** The first gate passed at tested_state `e0c1d0bce56dc2501f5fba785c4d1a1ded62fe52+d70b2324f4c6058ac99194a6a09a97dd9dc2bb9d0dcf1ba1f49db4f712b5bd19` (1416 Python tests, 36 in the region-import module). The round-1 corrections changed two product files and two test files, so H1-2 ran again on the whole tree; the record above is that run. It passed on its first try.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/domain/capture.py` | modified | The four `REGION_*` constants, `ViewFrame`, `RegionUnit`, `resolve_region`, `view_scale`, `view_frame`. CRLF kept |
| `packages/core/src/avkit_core/ports/capture.py` | modified | `view`. CRLF kept |
| `packages/core/src/avkit_core/services/capture.py` | modified | `read_image_view` and `_variant_path`, which `read_image` now shares; `_variant_path` checks through `_is_file`, which reads a denied lookup as missing (review F2). CRLF kept |
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` | modified | `view`, whose decode and RETURN_UNCHANGED read map every failure to the fixed refusal (review F2). CRLF kept |
| `packages/api/src/avkit_api/routes/captures.py` | modified | The six query parameters, the five headers and their 200 docs, the 413 text. CRLF kept |
| `openapi.committed.json` | modified | Regenerated in row 3 (the six parameters and the five header docs). CRLF kept |
| `mcp-server/src/toolsets/capture.ts` | modified | `GET_QUERY_KEYS`, the `image` fields and bounds (`REGION_MAX_EDGE_MIN`/`MAX`), the description. CRLF kept |
| `mcp-server/src/toolsets/registry.ts` | modified | `QUERY_GET_ONLY`, `parseCaptureFrame` and the frame item, the oversize text. CRLF kept |
| `mcp-server/src/client.ts` | modified | `captureHeaders`. LF kept |
| `tests/unit/test_domain_capture.py`, `tests/unit/test_capture_adapter.py` | modified | AC-128.1 to AC-128.10, appended, and the two AC-128.10 fault cases from review round 1. CRLF kept |
| `tests/e2e/test_api_capture_region_import.py` | new | AC-128.11 to AC-128.17 on the real stack (and MEU-129's tests). LF |
| `mcp-server/tests/capture.test.ts`, `mcp-server/tests/client.test.ts` | modified | AC-128.18 to AC-128.24. CRLF and LF kept |
| `docs/build-plan/09-screenshot-capture.md`, `05-mcp-server.md` | modified | §Spec text (row 6). CRLF kept |
| `docs/BUILD_PLAN.md`, `.agent/context/meu-status.yaml`, `meu-registry.md` | modified | MEU-128 `ready_for_review` (row 6) |
| `.agent/context/grouping/2026-11-08-capture-crop-session-grouping.md` | modified | Row 58 `executed` (`:108`), edited in place. CRLF kept |
| `.agent/context/current-focus.md` | modified | Session 58 entry (H1-3) |
| Plan folder: `baseline.sha`, `baseline-dirty.txt`, `task.md` | new or modified | Row 0's records and the row marks |

```diff
 # domain/capture.py
+def resolve_region(source_width, source_height, x, y, width, height, unit):
+    if unit == "px":
+        left, top = int(x), int(y)
+        right, bottom = left + int(width), top + int(height)
+    else:
+        left = math.floor(round(x * source_width, 9))
+        top = math.floor(round(y * source_height, 9))
+        right = math.ceil(round((x + width) * source_width, 9))
+        bottom = math.ceil(round((y + height) * source_height, 9))
+    clamped = right > source_width or bottom > source_height
+    right, bottom = min(right, source_width), min(bottom, source_height)
 # routes/captures.py
+    if all(value is None for value in (x, y, width, height, unit, max_edge)):
+        payload = capture.read_image(id, variant)
+        frame = _whole_frame(shot.width, shot.height)
+    else:
+        payload, frame = capture.read_image_view(id, variant, x=x, ...)
+    ...
+        "X-Capture-Scale": f"{frame.scale:.6f}",
```

```diff
 // registry.ts
-  const path = withQuery(interpolatePath(row.path, record), record);
+  const path = row.method === "GET"
+    ? withQuery(interpolatePath(row.path, record), record)
+    : interpolatePath(row.path, record);
     ...
+    const frame = parseCaptureFrame(binary.captureHeaders);
```

The excerpts are abridged and leave out the argument checks; `domain/capture.py:144-195`, `routes/captures.py:315-358`, `registry.ts:225-260` and `:384-422` are the source.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| F1 | High | Round 1: `IMPORT_COPY` could write over or delete a `NAME.avkit-tmp` it had not created | `services/capture.py:512`, `:549` | Create the temporary file exclusively; count a name whose temporary file exists as taken | fixed (round 2) |
| F2 | High | Round 1: import metadata lookups, the in-place probe, a broken-chunk PNG decode and the view's second read raised unmapped errors whose text held the path (500) | `services/capture.py:449`, `:489`; `adapter.py:291` | Map each to the fixed 422 refusal | fixed (round 2) |

### Verdict

`approved` in round 2 of loop `s58-execution-2026-11-08-capture-region-import` (Codex, 2026-11-09), with no open findings and intent achieved. Round 1 (7,847,133 tokens) returned `changes_required` with F1 and F2, both High and blocking; the corrections added 11 Red-first cases, and round 2 (3,872,291 tokens) closed both as `fixed` with no new finding. The loop used 11,719,424 of its 60,000,000-token budget and 2 of 6 rounds. The reviewer recomputed the tested_state independently and got `e0c1d0bce56dc2501f5fba785c4d1a1ded62fe52+73cc442629ca09d3d38777f0f7638d8df51681653e330cc5dafe47d64dc2e599`. Report: [implementation-critical-review.md](2026-11-08-capture-region-import-implementation-critical-review.md). H1-7a: `OK: review_mode=execution; round 2 of 6; verdict=approved; open findings=0` (`C:/Temp/av-kit/review-state-check.txt`). H1-7b: `OK: approved at round 2 of 6, 0 open blocking findings` (`C:/Temp/av-kit/exec-review.txt`).

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| A file replaced since the last list reports the old size in the five headers of a whole-image request until a list runs; a region view refuses the mismatch with 409 | out-of-scope | none; the plan states the limit (§User Review Required) | D-410, D-411 |
| A lossless WebP comes back lossy when it is cut or scaled, because JPEG and WebP views re-encode at `LOSSY_QUALITY` 90 | out-of-scope | none; the plan states the limit | D-410 |
| A scanned JPEG or WebP with EXIF orientation 5 to 8 is viewed and sized sideways, as before | out-of-scope | `CAPTURE-EXIF-SCANNED-ORIENTATION` (filed in row 6) | D-424 |
| Commit and push | out-of-scope | — | Only on Mat's explicit words (H2-5) |

**Execution notes.**
- **Row commands.** They ran through `.ps1` files written from the task cells, because the cells' `*>` needs PowerShell.
- **Row 1.** The adapter `view` stub's docstring was shortened for E501 after its receipt; ruff and pyright reran clean. `RegionUnit = Literal["px", "fraction"]` is an alias the plan doesn't name, used for the `unit` parameter.
- **Row 3, the frame item's text (D-412's inferred detail).** `{"frame": {"source": {"width", "height"}, "region": {"x", "y", "width", "height"}, "returned": {"width", "height"}, "scale", "clamped"}, "map": "source_x = region.x + x / scale; source_y = region.y + y / scale"}`. A header that is missing or malformed (non-digit parts, a wrong count, a scale that isn't a positive decimal, clamped not `true` or `false`) gives the image alone.
- **Row 3, shared variant checks.** `read_image`'s variant checks moved into `CaptureService._variant_path`, which `read_image_view` shares; the messages are unchanged.
- **Row 3, OpenAPI scope (S6).** The route's explanation sits in a comment, not the docstring, so the OpenAPI diff stays the six parameters and the 200 header docs.
- **Row 3, first validation run.** pyright refused `Image.LANCZOS`; it became `Image.Resampling.LANCZOS`, the file's existing spelling, and the whole command reran green.
- **Moved cites (Session 51 RULE-3).** Against the plan's `2963efe` anchors: `registry.ts`'s path line is now `:384` (was `:335`) and its image branch `:393-422` (was `:342-363`); `get_capture_image` is `routes/captures.py:315` (was `:257`); `GET_QUERY_KEYS` stays `capture.ts:19`; `client.ts`'s `ApiBinaryOk` field is `:161-162` and its fill `:255-262`.
- **No network.** No row and no gate step made a network request; every test builds its images with Pillow under `tmp_path` or in memory.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-09 | claude-code-local (Claude Opus 5.5) | Initial MEU-128 handoff after the H1-2 gate |
| Corrected | 2026-11-09 | claude-code-local (Claude Opus 5.5) | Review round 1's F2 fixed in `view` and `_variant_path`; the H1-2 gate rerun and its record replaced |
| Approved | 2026-11-09 | codex-independent-reviewer | Execution review round 2: `approved`, F1 and F2 `fixed`, no new finding |
