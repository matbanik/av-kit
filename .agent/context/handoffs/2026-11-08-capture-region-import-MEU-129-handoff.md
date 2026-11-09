---
date: "2026-11-09"
project: "capture-region-import"
meu: "MEU-129"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-08-capture-region-import/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-08-capture-region-import-MEU-128-handoff.md"
---

# Handoff: 2026-11-08-capture-region-import-MEU-129-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-129 `capture-image-import`. `POST /captures` takes `{"mode": "import", "path": …}` and MCP `capture` takes `mode: "import"` with `path`. An outside PNG, JPEG or WebP is checked, then copied into the inbox root and registered with source `Import`. EXIF orientations 2 to 8 are written upright as PNG. A file already in the inbox root registers in place, and the source file is never changed.
**Build Plan Section**: [09 §Image import](../../../docs/build-plan/09-screenshot-capture.md) (anchor `image-import`; the Delivered note at `:1026-1031`), 09 `:282` and its body and `capture` rows, and [00 §Enums](../../../docs/build-plan/00-overview.md) (`:68`).
**Predecessor**: [MEU-128 handoff](2026-11-08-capture-region-import-MEU-128-handoff.md), which shares this session's gate.

- **Domain and schema (row 5; D-414, D-415).** `CaptureSource.Import` is the last member (`enums.py:219`, `IMPORT_SOURCE`), reported as `Import` with no register wire value. `CaptureImportIn` (`schemas/captures.py:50`) is `{mode: Literal["import"], path: str}` with `extra="forbid"`, and joins the `CaptureCreateIn` discriminated union (`:57`, `IMPORT_MODE`).
- **Adapter (row 5; D-417).** `inspect_import` (`adapter.py:328`) refuses more than `Image.MAX_IMAGE_PIXELS` pixels by name, turns Pillow's bomb warning into an error, runs `verify()`, then reopens and `load()`s every pixel, and returns EXIF tag `0x0112` (`EXIF_ORIENTATION_TAG`, `:60`). `write_upright_png` (`:357`) applies `ImageOps.exif_transpose` and writes through `_write_png` (`:460`). The fixed messages are `IMPORT_OPEN_MESSAGE` and `IMPORT_PIXEL_MESSAGE` (`:58-59`). The port gains both (`ports/capture.py:39`, `:43`).
- **Service (row 5; D-416 to D-420, D-425).** `CaptureService.import_image` (`services/capture.py:449`) checks in order: absolute path, exists, is a file, `.png`/`.jpg`/`.jpeg`/`.webp`, at most `IMPORT_MAX_BYTES` (`:61`, 50,000,000, D-425), not an inbox-root annotated copy, readable, and decodes through `inspect_import` (`IMPORT_ACCEPT`). Each refusal is an `InboxPathError` or `ValidationError` (422) with a fixed message that names no path. A file in the inbox root registers in place through `_import_in_place` (`:489`, `IMPORT_IN_PLACE`): it probes the file, looks it up with `get_by_path`, and keeps an existing row's id and source (D-419). Any other file goes through `_import_copy` (`:512`). Under `CAPTURE_FILE_LOCK` (`:94`) it:
  - writes `<name>.avkit-tmp`;
  - `os.replace`s it into the name `_import_dest` (`:549`) chose;
  - probes and inserts it.

  On any failure it removes what it wrote and raises `CaptureFailedError("the import could not be written")`, a 503 (`IMPORT_COPY`, D-418). `import_stem` (`:111`, `IMPORT_NAME`, D-420) keeps `\w`, space and `-`, maps a reserved or empty stem to `import`, and makes the name unique with `casefold()`. Orientations 2 to 8 go through `write_upright_png` as `.png` (`IMPORT_UPRIGHT`). The register's scan (`scan_inbox`, `:343`) already held the same lock, so a scan and an import don't race (D-419).
- **Route and MCP (row 5; D-415).** `create_capture` (`routes/captures.py:245`) sends `CaptureImportIn` to `import_image` (`:258`) and answers 201. MCP `capture`'s `mode` enum gains `import` and its member gains `path` (`capture.ts:171`), and the description holds `IMPORT_TEXT` (`:43`, `:57`).
- **Spec text and records (row 6).** 09 `:282`, the body table's `import` row, the `capture` row, the Request, Source and Planning check rows (D-414, D-415, D-419, D-424) and the Delivered note (`:1026-1031`); 00 `:68`. `CAPTURE-EXIF-SCANNED-ORIENTATION` was filed (D-424), and grouping row 58 is `executed`.

**Where values go (D-421, `NO_RAW_CONSOLE`), for both MEUs.** The source path is outside text. Its stem reaches the copy's name and `display_name` only through `import_stem`. No refusal names the path: each is a fixed message (`ValidationError`, `InboxPathError`, or a 503 `internal_error` with a fixed detail). No log line was added. The copy's `capture.wrote` event already holds a path, which the Console processor drops, and `capture.registered` (`services/capture.py:1059`) logs only the id and source. AC-129.11 proves the whole list under `build_services` with a marker in every folder name, for the import and for MEU-128's region view: no `capfd` stdout or stderr line, ring message, `console.log` line or error message holds the marker, and the positive controls (a stdout `engine.created` line, at least two `capture.registered` ring lines) show the surfaces were read.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-08-capture-region-import/implementation-plan.md) §MEU-129. **Execution authorization:** `USER_EXPLICIT`, 2026-11-08, "proceed with execution", then "After S57 lands (Recommended)", given after the Codex plan review approved in round 3 ([plan-critical-review.md](2026-11-08-capture-region-import-plan-critical-review.md)) (`plan_to_exec_gate: human`). **D-425:** Mat accepted the recommendations ("all recommendations accepted"), so `IMPORT_MAX_BYTES` is 50,000,000.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-129.1 | unit | `"Import" in CaptureSource.__members__` and it is the last member, asserted before `.value == "Import"` is read | Local Canon: 09 `:1012`; D-414 | `tests/unit/test_domain_capture.py:604` | ✅ |
| AC-129.2 | e2e | `mode: import` with an extra key, and with no `path`, each return 422 `validation_error` | Local Canon: 09 `:1007` | `tests/e2e/test_api_capture_region_import.py:308` | ✅ |
| AC-129.3 | e2e | `IMPORT_COPY`: an outside PNG gives 201, source `Import`, a byte-equal copy in the inbox root; the source's bytes and `st_mtime_ns` unchanged; a following list shows the shot once, still `Import` | Local Canon: 09 `:1008`, `:1012`; design D-9 | `tests/e2e/test_api_capture_region_import.py:325` | ✅ |
| AC-129.4 | e2e | `IMPORT_NAME`: `shot.png`, `shot_2.png`, then `Shot_3.png` (casefold); `..` gives `import.png`; `a.b c#!.jpg` gives `a_b c.jpg`; `CON!.png` gives `import_CON.png` | Local Canon: 09 `:1011`; D-420 | `tests/e2e/test_api_capture_region_import.py:347` | ✅ |
| AC-129.5 | e2e | `IMPORT_UPRIGHT` over orientations 1 to 8 and no tag: 1 and none give a `.jpg` byte copy; 2 to 8 give a `.png` pixel-equal to `ImageOps.exif_transpose`, with the row's size matching | Research-backed: 09 `:1010`; design D-9 (R-7) | `tests/e2e/test_api_capture_region_import.py:384` (9 cases) | ✅ |
| AC-129.6 | e2e | `IMPORT_IN_PLACE`: a listed inbox-root file (source `Scan`) imports to the same id, still `Scan`, twice; an unlisted inbox-root file imports as `Import` with no new file | Local Canon: 09 `:1008`; D-419 | `tests/e2e/test_api_capture_region_import.py:419` | ✅ |
| AC-129.7 | e2e | An inbox-root `x.annotated.png` gives 422 with the annotated-copy message; a file in an inbox subfolder is copied to the root | Local Canon: D-416 | `tests/e2e/test_api_capture_region_import.py:442` | ✅ |
| AC-129.8 | e2e | Eleven refusals, each a 422 with its fixed text and no part of the path (relative, missing, folder, `.gif`, text as `.png`, over the patched 1 MB cap, both bomb PNGs, a damaged `IDAT`, a half JPEG); after the half JPEG the inbox has no new file and no `.avkit-tmp`, and a list returns 200 | Local Canon: 09 `:1009`, `:1013`; D-416, D-417 | `tests/e2e/test_api_capture_region_import.py:524` (11 cases) | ✅ |
| AC-129.9 | e2e | Three faults after the checks (`os.replace`, `probe` on the copy, `commit`): each gives a path-free 503 `internal_error`, leaves no temporary file, copy or row, and a following list returns 200 without the shot | Local Canon: D-418 | `tests/e2e/test_api_capture_region_import.py:545` (3 cases); `:627` (4 cases: a temporary file another writer left is never written over or removed, review round 1, F1) | ✅ |
| AC-129.10 | e2e | With `Path.read_bytes` raising `OSError` for the source, the import gives 422 `the file could not be read`; so do `exists`, `is_file`, `stat` and `resolve` raising, with no path in the response or the console, and an in-place `probe` fault gives 422 `the image could not be opened` (review round 1, F2) | Local Canon: D-416 | `tests/e2e/test_api_capture_region_import.py:600`, `:682` (4 cases), `:716` | ✅ |
| AC-129.11 | e2e | `NO_RAW_CONSOLE` for both MEUs under `build_services` with a marker in every folder name (registered file, import, region view, one import refusal, one view 422): no surface holds the marker; controls `engine.created` and two `capture.registered` lines | Local Canon: Session 50 RULE-1; Session 54 RULE-2; D-421 | `tests/e2e/test_api_capture_region_import.py:744` | ✅ |
| AC-129.12 | unit (MCP) | `capture` `mode: "import"` with `path` sends `{"mode": "import", "path": …}` as the POST body with `ADD_TIMEOUT_MS`; an extra key and a missing `path` are refused | Local Canon: 09 `:1007`; D-415 | `mcp-server/tests/capture.test.ts:723` | ✅ |
| AC-129.13 | unit (MCP) | The `capture` description holds `mode=import` and `never changed`; the advertised `mode` takes `import`, and `path` is listed | Research-backed: design §6.7 (R-8) | `mcp-server/tests/capture.test.ts:764` | ✅ |
| AC-128 (cross-ref) | cross-reference | MEU-128's ACs, AC-128.1 to AC-128.24, are owned and evidenced by the MEU-128 handoff | plan §MEU-128 | [MEU-128 handoff](2026-11-08-capture-region-import-MEU-128-handoff.md) | ✅ |
| AC-37 (cross-ref) | regression | The `CaptureSource` tuples that pin the enum gain `Import`: `CAPTURE_SOURCE_MEMBERS` (`tests/unit/test_domain_capture.py:18-26`), the `test_domain.py` entry (`:298-306`) and `SOURCE_OUT` (`tests/e2e/test_api_captures.py:93-101`); every other AC-37 test passes unchanged | plan §Test Plan (row 4a) | gate `py-tests` | ✅ |
| AC-38 (cross-ref) | regression | AC-38.2's 10 actions stand, because import is a `capture` mode (D-415); AC-38.3 and .11 to .13 and the capture suite's other members pass unchanged | plan §MEU-129 guards | gate `mcp-tests` | ✅ |
| AC-67, AC-111 (cross-ref) | regression | AC-67.17 and AC-111.1 to .4 are MEU-128's guards; the MEU-128 handoff carries them, and they passed in the shared gate | plan §MEU-128 guards | [MEU-128 handoff](2026-11-08-capture-region-import-MEU-128-handoff.md); gate `mcp-tests` | ✅ |
| AC-51, AC-81 (cross-ref) | regression | `ui/tests/e2e/test-ids.ts` is unchanged (scope-paths refuses it, and S9 never fired), so AC-51.6 and AC-81.13 pass | plan §Files Modified; S9 | gate `scope-paths`, `ui-tests` | ✅ |
| AC-84 (cross-ref) | regression | AC-84.2 and the scan and register tests pass unchanged; the scan holds `CAPTURE_FILE_LOCK`, which the import shares (D-419) | plan §MEU-129 guards | `tests/e2e/test_api_captures.py`; gate `py-tests` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-129.1 | `AssertionError: assert 'Import' in mappingproxy({'Hotkey': …, 'Scan': <CaptureSource.Scan: 'Scan'>})` | Row 5: pass | `test_domain_capture.py:604` |
| AC-129.3 to AC-129.6 | `assert 422 == 201` (12 cases; the discriminator refused `import`) | Row 5: pass | `test_api_capture_region_import.py:325`, `:347`, `:384`, `:419` |
| AC-129.7, AC-129.8 | `AssertionError: {"error":{"code":"validation_error","message":"Request validation failed",…}}` and `('validation_...ation failed') == ('ValidationE... jpeg, webp)')` (11 cases) | Row 5: pass | `test_api_capture_region_import.py:442`, `:524` |
| AC-129.9, AC-129.10 | `AssertionError: assert False` where `False = callable(None)` (4 cases; `import_image` is missing) | Row 5: pass | `test_api_capture_region_import.py:545`, `:600` |
| AC-129.11 | `assert 1 >= 2` (fewer than two `capture.registered` ring lines) | Row 5: pass | `test_api_capture_region_import.py:744` |
| AC-129.9 (review F1) | `assert 'shot.png' == 'shot_2.png'`; the race returned 201; `assert [] == ['shot.png.avkit-tmp']` | Corrections: pass | `test_api_capture_region_import.py:627` |
| AC-129.10 (review F2) | `assert 500 == 422` (`exists`, `is_file`, `stat`, `resolve`, the in-place probe) | Corrections: pass | `test_api_capture_region_import.py:682`, `:716` |
| AC-129.12 | `expected false to be true` (zod refused `mode: "import"`) | Row 5: pass | `capture.test.ts:723` |
| AC-129.13 | `expected 'Workflow: call avkit_capture capture …' to contain 'mode=import'` | Row 5: pass | `capture.test.ts:764` |
| AC-129.2 | Guard: passes in Red by design | Row 5: pass | `test_api_capture_region_import.py:308` |

- **Row 4a Python Red:** 29 failed and 1 passed (AC-129.2, the guard), every failure by assertion. The three `CaptureSource` tuples were amended in the same row and failed by assertion too. `red-check.py` required 10 tests and found 0 problems.
- **Row 4b MCP Red:** 2 failed and 28 skipped in 1 file, each by assertion. `red-check.py` required 2 tests and found 0 problems.
- **Review round 1 corrections (F1, F2):** the nine new AC-129.9 and AC-129.10 cases failed on the round-1 code by assertion (`s58-fix-r1-red`) and passed after the corrections (`s58-fix-r1-green`).
- **Row 5 Green:** the named Python suites passed 274; the OpenAPI check exited 0 after regeneration; since row 3 the file gained the `CaptureImportIn` schema, the discriminator's `"import"` mapping and its `oneOf` `$ref`; pyright 0 errors and ruff clean; the MCP suite passed 479 in 35 files and its typecheck was clean. No test file changed in row 5.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s58-129-red-py", "command": "$env:TMP='C:\\Temp\\av-kit\\s58\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest tests/unit/test_domain_capture.py tests/e2e/test_api_capture_region_import.py -k ac_129 --tb=short -q *> C:/Temp/av-kit/s58-py-red-129.txt; then red-check.py with the 10 --require ids *> C:/Temp/av-kit/s58-py-red-129-check.txt (abridged from task.md row 4a's Validation cell, run from P:/av-kit through an extracted .ps1)", "scope": "MEU-129 Python Red: AC-129.1 to AC-129.11 against the unchanged import path, with Pillow images under tmp_path and no network", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD e0c1d0b plus rows 0 to 4a", "output": "29 failed, 1 passed, 39 deselected in 4.82s. Decisive: assert 'Import' in mappingproxy({... 'Scan': <CaptureSource.Scan: 'Scan'>}); assert 422 == 201 (12); the validation_error envelope (11); ('validation_...ation failed') == ('ValidationE... jpeg, webp)') (3) and == ('ValidationE...-pixel limit') (2); assert False where False = callable(None) (4); assert 1 >= 2. red-check: 1 receipt(s), 10 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s58-129-red-mcp", "command": "rtk proxy npm --prefix mcp-server run test -- tests/capture.test.ts -t \"AC-129\" *> C:/Temp/av-kit/s58-mcp-red-129.txt; then red-check.py with the 2 --require ids *> C:/Temp/av-kit/s58-mcp-red-129-check.txt (abridged from task.md row 4b's Validation cell, run from P:/av-kit through an extracted .ps1)", "scope": "MEU-129 MCP Red: AC-129.12 and AC-129.13 against the unchanged capture.ts", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD e0c1d0b plus rows 0 to 4b", "output": "Test Files 1 failed (1); Tests 2 failed | 28 skipped (30). AssertionError: expected false to be true; AssertionError: expected 'Workflow: call avkit_capture capture …' to contain 'mode=import'. red-check: 1 receipt(s), 2 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s58-129-green", "command": "$env:TMP='C:\\Temp\\av-kit\\s58\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest tests/unit/test_domain.py tests/unit/test_domain_capture.py tests/unit/test_capture_adapter.py tests/unit/test_capture_service.py tests/e2e/test_api_captures.py tests/e2e/test_api_capture_flatten.py tests/e2e/test_api_capture_region_import.py tests/e2e/test_api_bodies.py --tb=short -q *> C:/Temp/av-kit/s58-py-green-129.txt; then export_openapi.py --check *> C:/Temp/av-kit/s58-r5-openapi.txt, git diff -- openapi.committed.json *> C:/Temp/av-kit/s58-r5-openapi-diff.txt, pyright *> C:/Temp/av-kit/s58-r5-pyright.txt, ruff *> C:/Temp/av-kit/s58-r5-ruff.txt, npm --prefix mcp-server run test *> C:/Temp/av-kit/s58-mcp-green-129.txt and typecheck *> C:/Temp/av-kit/s58-r5-mcp-types.txt (task.md row 5's Validation cell, run from P:/av-kit through an extracted .ps1)", "scope": "MEU-129 Green: IMPORT_MODE, IMPORT_ACCEPT, IMPORT_COPY, IMPORT_UPRIGHT, IMPORT_IN_PLACE, IMPORT_NAME, IMPORT_SOURCE and NO_RAW_CONSOLE", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD e0c1d0b plus rows 0 to 5", "output": "274 passed in 12.15s. export_openapi --check: exit 0, no output. openapi.committed.json since row 3: the CaptureImportIn schema, the discriminator mapping \"import\" and its oneOf $ref (the whole diff against HEAD is 158 lines added, 1 removed, both MEUs). pyright: 0 errors, 0 warnings, 0 informations. ruff: All checks passed! MCP: Tests 479 passed (479). tsc --noEmit && tsc -p tsconfig.scripts.json clean."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s58-6-records", "command": "task.md row 6 (abridged), run from P:/av-kit: the 09, 00 and 05 notes; tools/meu_status.py update MEU-128 and MEU-129 ready_for_review --plan and render; issue-file.py *> C:/Temp/av-kit/s58-issue-file.txt; issue_triage.py render and triage; grouping row 58; then its Validation cell through an extracted .ps1 into s58-r6-render.txt, s58-r6-issues.txt and s58-r6-status.txt", "scope": "Row 6: the D3 spec text, both MEUs ready_for_review with this plan, CAPTURE-EXIF-SCANNED-ORIENTATION filed (D-424), the renders, and grouping row 58 executed", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD e0c1d0b plus rows 0 to 6", "output": "issue-file: before 5d9084c29298beba 394190; after 523fa184e7a34e74 397272 CRLF 0; added lines 38 removed lines 0; CAPTURE-EXIF-SCANNED-ORIENTATION open P3 ['D-424']. meu_status render: Loaded 132 MEUs across 12 phases; All regions rendered successfully. Validation: ['ready_for_review', 'ready_for_review'] open ['| 58 | `capture-region-import` | MEU-128, MEU-129 | P2 | executed | `docs/execution/plans/2026-11-08-capture-region-import/` |']; exit 0"}
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
| `packages/core/src/avkit_core/domain/enums.py` | modified | `CaptureSource.Import`, last. CRLF kept |
| `packages/core/src/avkit_core/ports/capture.py` | modified | `inspect_import`, `write_upright_png`. CRLF kept |
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` | modified | `inspect_import`, `write_upright_png` and their constants. CRLF kept |
| `packages/core/src/avkit_core/services/capture.py` | modified | `IMPORT_MAX_BYTES`, the stem constants, `import_stem`, `import_image`, `_read_import`, `_import_in_place`, `_import_copy`, `_import_dest`; both import paths take the existing `CAPTURE_FILE_LOCK`, which `scan_inbox` already held. After review round 1: the file checks map `OSError` to the fixed 422, the in-place probe maps `OSError`, the copy creates its temporary file exclusively and removes only that, and a name whose temporary file exists is taken. CRLF kept |
| `packages/api/src/avkit_api/schemas/captures.py` | modified | `CaptureImportIn` and its union entry. CRLF kept |
| `packages/api/src/avkit_api/routes/captures.py` | modified | The import branch of `create_capture`. CRLF kept |
| `openapi.committed.json` | modified | Regenerated in row 5 (`CaptureImportIn`, the mapping, the `$ref`). CRLF kept |
| `mcp-server/src/toolsets/capture.ts` | modified | `mode: "import"`, `path`, `IMPORT_TEXT`. CRLF kept |
| `tests/unit/test_domain_capture.py`, `tests/unit/test_domain.py`, `tests/e2e/test_api_captures.py` | modified | AC-129.1 and the three `CaptureSource` tuples. CRLF kept |
| `tests/e2e/test_api_capture_region_import.py` | new | AC-129.2 to AC-129.11 (and MEU-128's AC-128.11 to .17), with the nine AC-129.9 and AC-129.10 fault cases from review round 1. LF |
| `mcp-server/tests/capture.test.ts` | modified | AC-129.12, AC-129.13. CRLF kept |
| `docs/build-plan/09-screenshot-capture.md`, `00-overview.md` | modified | §Spec text (row 6). CRLF kept |
| `.agent/context/known-issues.yaml`, `known-issues.md`, `triage-output.yaml` | modified | `CAPTURE-EXIF-SCANNED-ORIENTATION` filed and the renders (row 6) |
| `docs/BUILD_PLAN.md`, `.agent/context/meu-status.yaml`, `meu-registry.md`, the grouping file | modified | MEU-129 `ready_for_review`; grouping row 58 `executed` (row 6) |

```diff
 # services/capture.py
+    def import_image(self, path: Path) -> CaptureShot:
+        if not path.is_absolute():
+            raise InboxPathError("path must be absolute")
+        inbox = self._inbox()
+        try:
+            # exists, is a file, suffix, size, annotated copy in the root, then the read
+            resolved, data = self._read_import(path, inbox)
+        except OSError as exc:
+            raise InboxPathError("the file could not be read") from exc
+        orientation = self._annotate.inspect_import(data)
+        if in_root:
+            return self._import_in_place(resolved)
+        return self._import_copy(resolved, inbox, data, orientation)
 # routes/captures.py
+    elif isinstance(body, CaptureImportIn):
+        shot = capture.import_image(Path(body.path))
```

The excerpt is abridged; `services/capture.py:449-575` and `routes/captures.py:258-260` are the source.

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
| A scanned JPEG or WebP with EXIF orientation 5 to 8 is sized and annotated sideways; only an import turns it upright | out-of-scope | `CAPTURE-EXIF-SCANNED-ORIENTATION` (filed in row 6) | D-424 |
| Commit and push | out-of-scope | — | Only on Mat's explicit words (H2-5) |

**Execution notes.**
- **Row 4a.** AC-129.5, .8 and .9's cases are `pytest.param` ids (`AC-129.8-half-jpeg` and so on), so each case prints its own id. The red-check `--require` ids follow the final test names.
- **Row 4b.** AC-129.12 checks `ADD_TIMEOUT_MS` with a spy on `AbortSignal.timeout`, because the timeout isn't otherwise visible to the fake fetch.
- **Row 5, helper names.** `_import_in_place`, `_import_copy` and `_import_dest` split `import_image`, which the plan described as one method.
- **Row 5, `IMPORT_NAME`.** Python's `\w` keeps Unicode letters, so a stem such as `résumé` stays as written; the plan's examples are ASCII and pass.
- **Row 5, `IMPORT_IN_PLACE`.** After the probe, an inbox-root file is looked up by path, so a listed file keeps its id and source. A size that changed since the list updates the row's size.
- **Row 5, `inspect_import`.** A file with no orientation tag, or with a value outside 2 to 8, returns 1, which gives a byte copy.
- **Row 5, the refusal order.** The size cap is checked before the annotated-copy check and the read, so an oversize file is refused without being read.
- **Row 5, ruff.** Two `I001` import-order fixes in the new test file after the first validation run; the whole command reran green.
- **Moved cite (Session 51 RULE-3).** `capture.registered` is `services/capture.py:1085` (the plan cited `:894` at `2963efe`).
- **No network.** No row and no gate step made a network request.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-09 | claude-code-local (Claude Opus 5.5) | Initial MEU-129 handoff after the H1-2 gate |
| Corrected | 2026-11-09 | claude-code-local (Claude Opus 5.5) | Review round 1's F1 and F2 fixed in the import path; the H1-2 gate rerun and its record replaced |
| Approved | 2026-11-09 | codex-independent-reviewer | Execution review round 2: `approved`, F1 and F2 `fixed`, no new finding |
