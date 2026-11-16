---
date: "2026-11-15"
project: "2026-11-15-capture-inbox-probe"
meu: "MEU-145"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-15-capture-inbox-probe/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "none"
---

# Handoff: 2026-11-15-capture-inbox-probe-MEU-145-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-145 `capture-scan-skips-unreadable` (issue `CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST`, triage D-802, filed by D-507). An inbox file that is not an image, is damaged or is half-written no longer breaks `GET /captures` or MCP `list`: the scan skips it, keeps its row as it was and tries it again on the next scan, and no message, log line or body names a path.
**Build Plan Section**: [09 §Scan skips unreadable files](../../../docs/build-plan/09-screenshot-capture.md#scan-skips-unreadable-files) (matrix 9.43), with the Delivered (Session 75) note above the `exif-orientation-on-scan` anchor.
**Predecessor**: none. The sibling MEU-146 handoff is `2026-11-15-capture-inbox-probe-MEU-146-handoff.md`.

- **SCAN_SKIP (D-900).** `CaptureService.scan_inbox` (`services/capture.py:651`; `:597` at row 0) wraps each file's `resolve()` and `probe` in one `try`/`except (InboxPathError, OSError)` (`:664-672`), so a file it cannot read is skipped and every readable shot still lists, through the API and MCP. No flag field is added to the list (M-4).
- **KEEP_ROW (D-901).** A skipped file's row, if any, is left exactly as it was (`id`, size, `file_size`, `updated_at`); the next scan tries the file again, and the loop that drops rows whose original is gone still sees the file, so the row stays.
- **PROBE_FIXED (D-902).** `probe` (`capture/adapter.py:534`; `:461` at row 0) raises `InboxPathError("no file at that path")` (`:542`) or `InboxPathError("the image could not be opened")` (`:550`) whatever Pillow raised, including the damaged-IDAT `SyntaxError`; `bake` (`:704`) and `render` (`:725`) give the same fixed text and write nothing. `UnidentifiedImageError` is no longer imported (`s75-145-eol.txt`).
- **SKIP_LOG (D-902).** `capture.scan_skipped` (`SCAN_SKIPPED_EVENT`, `services/capture.py:96`) is logged once with only `count` when the skipped set changes; a clean scan resets it (`_log_scan_skipped`, `:748-752`). The set lives on the service instance (`_scan_skipped`).
- **Spec text (row 5).** The Delivered note in 09 cites the row-0 and the current line numbers.
- **Records (row 6).** The issue is resolved through the plan's `issue-resolve.py` (`s75-issue-resolve.txt`), and MEU-145 is `ready_for_review` (`s75-status-145.txt`).

**Where values go (D-421, `NO_RAW_CONSOLE`).** A skipped file's path goes only into the in-memory skipped set, which is compared and counted, never logged or returned. AC-145.1 to AC-145.6, AC-145.10 and AC-145.12 use an inbox folder whose name holds the marker `s75mark`, and none of the messages, the log event or the list body holds it.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-15-capture-inbox-probe/implementation-plan.md) §MEU-145. **Execution authorization:** `USER_EXPLICIT`, 2026-11-15, "proceed with planning and execution for P:\av-kit\.agent\context\grouping\2026-11-15-post-rc3-triage-residuals-session-grouping.md like we did here. But use the new HDP process. Continue orchestrating the sessions." The plan review approved at round 3 ([plan-critical-review.md](2026-11-15-capture-inbox-probe-plan-critical-review.md)); `plan_to_exec_gate: human`. The coordinator wrote these words into the plan's Status line (line 15) before row 0; that is a plan-text edit made after the plan was approved, disclosed here.

**Receipts.** A receipt named by its file name alone is in the session's receipts folder (`RECEIPTS_DIR`, the plan's `capture-inbox-probe` folder under it). Full paths appear only in the evidence records' `command` fields.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-145.1 | unit | `probe` on a non-image file named `.png` raises `InboxPathError` whose message is exactly `the image could not be opened`. | Local Canon (09 §Scan skips: No path; D-421; D-902) | `tests/unit/test_capture_scan_unreadable.py:108` | ✅ |
| AC-145.2 | unit | The same for a PNG whose IDAT is damaged in place (same length). | Local Canon (09 Tests; D-902) | `tests/unit/test_capture_scan_unreadable.py:123` | ✅ |
| AC-145.3 | unit | The same for a PNG cut to half its length. | Local Canon (09 Retry: a half-written screenshot; D-902) | `tests/unit/test_capture_scan_unreadable.py:135` | ✅ |
| AC-145.4 | unit | `probe` on a missing path raises `InboxPathError` with exactly `no file at that path`. | Local Canon (`services/capture.py:727`; D-902) | `tests/unit/test_capture_scan_unreadable.py:146` | ✅ |
| AC-145.5 | unit | `bake` on the non-image, damaged and truncated files raises `InboxPathError` with the fixed message and writes no output file. | Local Canon (09 No path; D-902) | `tests/unit/test_capture_scan_unreadable.py:157` | ✅ |
| AC-145.6 | unit | `render` on the same three files raises `InboxPathError` with the fixed message. | Local Canon (D-902) | `tests/unit/test_capture_scan_unreadable.py:180` | ✅ |
| AC-145.7 | unit | A service scan whose fake probe raises `InboxPathError` for one file and `OSError` for another, and where `Path.resolve` is patched to raise `OSError` for a third, lists exactly the readable shots and adds no row for any of the three. | Local Canon (09 List; D-507; D-900) | `tests/unit/test_capture_scan_unreadable.py:246` | ✅ |
| AC-145.8 | unit | A file listed once, then made unreadable, keeps its row: same `id`, `width`, `height`, `file_size` and `updated_at`. | Local Canon (09 Retry; D-901) | `tests/unit/test_capture_scan_unreadable.py:276` | ✅ |
| AC-145.9 | unit | After the file is readable again, the next scan lists it (new file: a new row; kept row: updated as today). | Local Canon (09 Retry) | `tests/unit/test_capture_scan_unreadable.py:299` | ✅ |
| AC-145.10 | unit | Two unreadable files give one `capture.scan_skipped` warning whose keys are exactly `event`, `log_level`, `module` and `count`, with `count` 2 and no path, name, marker or exception text in any value. | Local Canon (09 No path; Session 50 rule; D-902) | `tests/unit/test_capture_scan_unreadable.py:346` | ✅ |
| AC-145.11 | unit | A second scan with the same set logs nothing; a third bad file logs `count` 3; a scan with all files readable logs nothing; a later bad file logs `count` 1. | Local Canon (D-902) | `tests/unit/test_capture_scan_unreadable.py:375` | ✅ |
| AC-145.12 | e2e | API: an inbox with `a.png`, `b.png`, a non-image `fake.png` and a damaged `broken.png` answers `GET /captures` 200 with exactly the names `a.png` and `b.png`; no bad name, marker or path is in the body. | Local Canon (09 List and Tests; D-900) | `tests/e2e/test_api_capture_scan_unreadable.py:91` | ✅ |
| AC-145.13 | e2e | API retry: a non-image `late.png` is not listed; after it is overwritten with a valid PNG, the next list includes it. | Local Canon (09 Retry) | `tests/e2e/test_api_capture_scan_unreadable.py:113` | ✅ |
| AC-145.14 | unit | MCP `list` is `GET /captures` through the same service: the pin at `mcp-server/tests/capture.test.ts:24` passes unchanged in the gate's `mcp-tests`. | Local Canon (09 List: "through the API and MCP") | `mcp-server/tests/capture.test.ts:24` (the `list` pin, unchanged; gate `mcp-tests`) | ✅ |
| AC-145.15 | e2e | AC-130.21 with its restore removed: the follow-up list answers 200 with the same ids while the damaged file stays in the inbox (Green only). | Local Canon (09 Tests: "AC-130.21 no longer needs to restore") | `tests/e2e/test_api_capture_crop.py:763` (`test_ac_130_21_damaged_source_is_422`) | ✅ |
| AC-130.21 (cross-ref) | pin that moves | `test_ac_130_21_damaged_source_is_422` no longer restores its source before the follow-up list; it is AC-145.15. Its other cases (`:613`, `:689`) are unchanged | MEU-130 | `tests/e2e/test_api_capture_crop.py:763` | ✅ |
| AC-128 (cross-ref) | guard | The view's fixed refusals (D-421) are unchanged: `view` still gives `the image could not be opened` and the 409 size check | MEU-128 | gate `py-tests` (2939 passed) | ✅ |
| AC-129 (cross-ref) | guard | D-421's fixed import refusals are unchanged; AC-129.5 (a tagged region import) still passes | MEU-129 | `tests/e2e/test_api_capture_region_import.py:384`; gate `py-tests` | ✅ |
| AC-104.3 (cross-ref) | guard | The bare-error adapter test already expects the fixed message, so PROBE_FIXED changes no assertion there | MEU-104 | `tests/unit/test_capture_adapter.py:465-470` | ✅ |
| AC-36.9, AC-36.10 (cross-ref) | guard | The fake port gains `shown_tag` and `read_shown` (returning 1 and the file's bytes), so the sidecar-key and `read_image` assertions hold | MEU-36 | `tests/unit/test_capture_service.py:356`, `:389` | ✅ |
| AC-136.7 (cross-ref) | pin that moves | Owned by MEU-146 (AC-146.11); named here because the same Green run swept the capture suites | MEU-136 | `tests/unit/test_capture_export_adapter.py:672` | ✅ |
| AC-146 (sibling) | sibling MEU | AC-146.1, AC-146.2, AC-146.3, AC-146.4, AC-146.5, AC-146.6, AC-146.7, AC-146.8, AC-146.9, AC-146.10, AC-146.11, AC-146.12, AC-146.13, AC-146.14, AC-146.15, AC-146.16, AC-146.17, AC-146.18, AC-146.19, AC-146.20, AC-146.21, AC-146.22, AC-146.23, AC-146.24, AC-146.25, AC-146.26, AC-146.27, AC-146.28: the orientation work, evidenced in the MEU-146 handoff | MEU-146 | `2026-11-15-capture-inbox-probe-MEU-146-handoff.md` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-145.1, AC-145.3, AC-145.5 | `message is not the fixed one` (the message held the inbox path) | Row 3: pass | `test_capture_scan_unreadable.py:108`, `:135`, `:157` |
| AC-145.2, AC-145.6 | `damaged: raised SyntaxError` | Row 3: pass | `test_capture_scan_unreadable.py:123`, `:180` |
| AC-145.4 | `message is not the fixed one`, against `no file at that path` | Row 3: pass | `test_capture_scan_unreadable.py:146` |
| AC-145.7, AC-145.8, AC-145.11 | `the scan raised InboxPathError` | Row 3: pass | `test_capture_scan_unreadable.py:246`, `:276`, `:375` |
| AC-145.9 | `the first scan raised InboxPathError` | Row 3: pass | `test_capture_scan_unreadable.py:299` |
| AC-145.10 | `the scan raised OSError` | Row 3: pass | `test_capture_scan_unreadable.py:346` |
| AC-145.12 | `list answered 500` | Row 3: pass | `test_api_capture_scan_unreadable.py:91` |
| AC-145.13 | `list answered 422` | Row 3: pass | `test_api_capture_scan_unreadable.py:113` |

- **Green only, not in FAIL_TO_PASS:** AC-145.14 (the MCP `list` pin, unchanged; it passes in the gate's `mcp-tests`) and AC-145.15 (AC-130.21 without its restore; before Green its `TestClient(app)` would raise on the 500, a setup failure, not a Red reason).
- **Row 2 Red** (`s75-red-py.txt`): `36 failed, 3 passed in 19.97s` across both MEUs; MEU-145's 13 cases all failed by assertion (catch-then-assert). `s75-red-check.txt`: `red-check: 1 receipt(s), 36 required test(s), 0 problem(s)`.
- **Row 3 Green** (`s75-145-green.txt`): `120 passed in 10.50s`.
- **AC-145.12's body check.** The test removes each listed shot's own `original_path` string from the body, then asserts that `s75mark`, `fake.png`, `broken.png`, `not an image` and `BAD!` are absent; a positive control asserts the marker does appear in the full body, so the check can see a path.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s75-0-baseline", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-15-capture-inbox-probe/baseline.ps1 *> C:/Temp/av-kit/capture-inbox-probe/s75-baseline.txt (task.md row 0's Validation cell)", "scope": "Row 0: the rulings (S9) and queue (S8) checks, the shapes check (S7), the row-0 copies and their SHA-256 and line endings (s75-anchors.txt), baseline.sha and baseline-dirty.txt, the base Python, UI, MCP and Electron runs, ruff, the UI build and the red-check, identity and id-length selftests", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3397e78 (baseline.sha), before row 1", "output": "s75-baseline.txt: execute words found; MEU-35, MEU-36, MEU-84, MEU-128, MEU-129, MEU-130 and MEU-136 approved, MEU-145 and MEU-146 pending; 6aaf9b0 is an ancestor of HEAD: True; shapes wrong (S7): []; the row-0 copies differ from HEAD: []; baseline-dirty.txt 61 paths; base py 2900 passed, 37 warnings in 250.26s; base ui Test Files 130 passed (130), Tests 1532 passed (1532); base mcp Tests 535 passed (535) in 36 files; base e2e 53 passed (1.5m); ruff All checks passed!; the base UI and MCP builds exit 0; red-check selftest 71 fixture(s) (21 positive, 50 negative), 0 wrong; identity selftest 0 failure(s); id-length selftest 4 case(s), 0 wrong; baseline: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s75-1-stubs", "command": "pwsh -NoProfile -File C:/Temp/av-kit/capture-inbox-probe/cmd-1.ps1 (task.md row 1's Validation cell, extracted to a .ps1 and run from P:/av-kit with ELECTRON_RUN_AS_NODE unset); receipts s75-stub-types.txt, s75-stub-lint.txt, s75-stub-sweep.txt, s75-stub-check.txt, s75-stub-fixtures.txt", "scope": "Row 1 type-only names: SHOWN_ORIENTATION_FORMATS, shown_orientation and _open_shown stubs, the port's shown_tag and read_shown, FakeCapturePort and FakeAnnotate shown_tag and read_shown, the STALE_BAKE_FAILED_EVENT and scan-state names, and tests/orientation_fixtures.py, with no behaviour", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3397e78 plus rows 0 and 1", "output": "s75-stub-types.txt: 0 errors, 0 warnings, 0 informations; s75-stub-lint.txt: All checks passed!; s75-stub-sweep.txt: 222 passed, 5 warnings in 17.70s; s75-stub-check.txt: stubs present: True line-ending drift: []; s75-stub-fixtures.txt: eight fixtures, each 40x30 with getexif_tag 6; exif_block_tag 6 for o6.jpg, o6.mpo.jpg, o6.png, o6-prefixed.png and o6.webp (EXIF chunk, vp8x_flags 8), and null for o6-xmp.jpg, o6-raw-profile.png and o6-after-idat.png"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s75-2-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/capture-inbox-probe/cmd-2.ps1 (task.md row 2's Validation cell, extracted to a .ps1 and run from P:/av-kit with ELECTRON_RUN_AS_NODE unset); receipts s75-red-idlen.txt, s75-red-py.txt, s75-red-check.txt (red-check.py with the 36 --require ids) and s75-red-e2e.txt (AC-146.19 through pwsh in P:/av-kit/ui)", "scope": "Red for both MEUs: AC-145.1 to AC-145.13 and AC-146.1 to AC-146.28 (less AC-146.11 and AC-146.19) against the row-1 stubs, with Pillow images under tmp_path and no network; the Electron pin AC-146.19", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3397e78 plus rows 0 to 2", "output": "s75-red-idlen.txt: id-length: 39 test(s), 0 too long. s75-red-py.txt: 36 failed, 3 passed in 19.97s; the 3 passing are the guards AC-146.5, AC-146.21 and AC-146.28. Decisive: message is not the fixed one; damaged: raised SyntaxError; the scan raised InboxPathError; the scan raised OSError; list answered 500; list answered 422; probe sizes off the shown frame; whole views not upright; jpg: the region raised ConflictError; the bake is (400, 300); the scan kept the old size; assert (160, 160) == (40, 40); the original was not read through read_shown; the tag-6 sidecar has no key; no key, tag 6: 0 bake calls; the copy is still (400, 300). s75-red-check.txt: red-check: 1 receipt(s), 36 required test(s), 0 problem(s). s75-red-e2e.txt: AC-146.19 1 passed (1.9s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s75-3-green-145", "command": "pwsh -NoProfile -File C:/Temp/av-kit/capture-inbox-probe/cmd-3.ps1 (task.md row 3's Validation cell, extracted to a .ps1 and run from P:/av-kit with ELECTRON_RUN_AS_NODE unset); receipts s75-145-green.txt, s75-145-types.txt, s75-145-eol.txt", "scope": "MEU-145 Green: SCAN_SKIP, KEEP_ROW, PROBE_FIXED and SKIP_LOG, and the AC-130.21 move (AC-145.15)", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3397e78 plus rows 0 to 3", "output": "s75-145-green.txt: 120 passed in 10.50s (test_capture_scan_unreadable.py, test_api_capture_scan_unreadable.py, test_api_capture_crop.py, test_capture_adapter.py, test_capture_service.py); s75-145-types.txt: 0 errors, 0 warnings, 0 informations; s75-145-eol.txt: line-ending drift: [] UnidentifiedImageError removed: True"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s75-5-notes", "command": "pwsh -NoProfile -File C:/Temp/av-kit/capture-inbox-probe/cmd-5.ps1 (task.md row 5's Validation cell, extracted to a .ps1 and run from P:/av-kit with ELECTRON_RUN_AS_NODE unset); receipt s75-notes-check.txt", "scope": "Row 5: one Delivered (Session 75) note under each of the two 09 anchors, CRLF kept, insert-only against row 0", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3397e78 plus rows 0 to 5", "output": "s75-notes-check.txt: CRLF: True notes: 1 1 opcodes against row 0: ['equal', 'insert']"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s75-6-records", "command": "pwsh -NoProfile -File C:/Temp/av-kit/capture-inbox-probe/cmd-6.ps1 (task.md row 6's Validation cell, extracted to a .ps1 and run from P:/av-kit with ELECTRON_RUN_AS_NODE unset); receipts s75-issue-resolve.txt, s75-issues-render.txt, s75-issues-render-check.txt, s75-status-145.txt, s75-status-146.txt, s75-status-render.txt, s75-row6-check.txt", "scope": "Row 6: both issues resolved through issue-resolve.py, known-issues.md rendered, MEU-145 and MEU-146 ready_for_review, the status render, and grouping row 75 executed", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3397e78 plus rows 0 to 6", "output": "s75-issue-resolve.txt: decision logs read: 95 of 95; parsed fields changed: 10 (issues[123] and issues[125]); issue-resolve: 0 problem(s). s75-issues-render.txt: Rendered known-issues.md: 64 lines; s75-issues-render-check.txt: OK: known-issues.md is up-to-date. s75-status-145.txt and s75-status-146.txt: Updated MEU-145 / MEU-146 → ready_for_review (updated: 2026-11-15). s75-status-render.txt: Loaded 153 MEUs across 12 phases; All regions rendered successfully. s75-row6-check.txt: other MEU rows changed: []; grouping LF: True"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s75-h1-1-rows", "command": "pwsh -NoProfile -File C:/Temp/av-kit/capture-inbox-probe/cmd-H1-1.ps1 (task.md row H1-1's Validation cell) ; receipt task-unchecked.txt", "scope": "H1-1: every implementation row of task.md is checked", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3397e78 plus rows 0 to 6", "output": "task-unchecked.txt: unchecked implementation rows: []"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s75-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-15-capture-inbox-probe/session-gate.ps1 *> C:/Temp/av-kit/capture-inbox-probe/s75-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/capture-inbox-probe/s75-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','mismatch','session-gate:'; exit $code", "scope": "H1-2, re-run after the F1 correction (D-1002): the registered D6 gate on the whole tree: identity, every static check, the full Python, UI and MCP suites, the UI build, OpenAPI, the MCP types, build and tests, both renders and the Electron capture-inbox spec, then the identity again", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "3397e78d7342d73e99dde3b43244a55cd6be7e87+38feee5f5521beeed6e8d96fadfb544a70cf5c2444a10d08be5553bcb4679fb8", "output": "identity-before exit=0; py-types exit=0 (0 errors, 0 warnings, 0 informations); py-lint exit=0 (All checks passed!); ui-types exit=0; ui-lint exit=0 (eslint --max-warnings 0); mcp-types exit=0; task-contract exit=0 (24 rows, 22 fully checked, 2 view_file exempt: H1-5, H2-1); scope-paths exit=0 (changed paths since 3397e78d7342: 86, outside scope (S3): [], head moved since row 0: False, baseline-dirty paths changed since row 0: []); route-comment-only exit=0 (route lines changed against row 0: 5, non-comment lines among them: []); red-check-selftest exit=0 (71 fixtures, 21 positive, 50 negative, 0 wrong); id-length exit=0 (40 tests, 0 too long); py-tests exit=0 (2940 passed, 37 warnings in 278.97s); openapi exit=0; ui-tests exit=0 (Test Files 130 passed (130), Tests 1532 passed (1532)); ui-build exit=0 (built in 5.53s); mcp-build exit=0; mcp-tests exit=0 (Test Files 36 passed (36), Tests 535 passed (535)); state-render exit=0 (153 MEUs, 12 phases, regions match); issues-render exit=0 (known-issues.md is up-to-date); ui-electron exit=0 (capture-inbox.test.ts, 54 passed (1.6m)); identity-after exit=0 (tested_state before = after); mcp-audit and build-record skipped with reasons; baseline failures excused: py [], ui [], mcp [], e2e []; session-gate: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s75-h1-3-ssot", "command": "pwsh -NoProfile -File C:/Temp/av-kit/capture-inbox-probe/cmd-H1-3.ps1 (task.md row H1-3's Validation cell); receipts s75-render-check.txt, s75-h13-status-145.txt, s75-h13-status-146.txt, s75-h13-check.txt", "scope": "H1-3: MEU-145 and MEU-146 are ready_for_review and the status render matches, after the current-focus update (not a gated input)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "3397e78d7342d73e99dde3b43244a55cd6be7e87+38feee5f5521beeed6e8d96fadfb544a70cf5c2444a10d08be5553bcb4679fb8", "output": "s75-render-check.txt: Drift check passed, SSOT loaded (153 MEUs, 12 phases), rendered regions match on-disk content; s75-h13-check.txt: MEU-145 and MEU-146 ready_for_review: True"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s75-h1-4-shape", "command": "pwsh -NoProfile -File C:/Temp/av-kit/capture-inbox-probe/cmd-H1-4.ps1 (task.md row H1-4's Validation cell); receipts s75-openapi-check.txt, s75-api-hash-check.txt", "scope": "H1-4 (S6): the app matches openapi.committed.json; the OpenAPI document, capture.ts, registry.ts and capture.test.ts keep their row-0 SHA-256; routes/captures.py differs from row 0 only in blank or comment lines", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "3397e78d7342d73e99dde3b43244a55cd6be7e87+38feee5f5521beeed6e8d96fadfb544a70cf5c2444a10d08be5553bcb4679fb8", "output": "export_openapi --check exit 0, no output; s75-api-hash-check.txt: API and MCP files changed since row 0: [] route code lines changed: []"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s75-eol-final", "command": "uv run python C:/Temp/av-kit/capture-inbox-probe/eol-final.py > C:/Temp/av-kit/capture-inbox-probe/s75-eol-final.txt 2>&1", "scope": "Supplementary: the line endings of the 30 files measured at row 0, the five new test files, the plan and task.md, measured in bytes after H1-4", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "3397e78d7342d73e99dde3b43244a55cd6be7e87+38feee5f5521beeed6e8d96fadfb544a70cf5c2444a10d08be5553bcb4679fb8", "output": "s75-eol-final.txt: files checked: 37 line-ending drift: []"}
```

### Quality Gate Results

`s75-gate-h1-2` (H1-2) is the fresh full record for both MEUs. It is the gate re-run after the F1 correction (D-1002); round 1's gate (`3397e78…+7597a302…`, also `session-gate: all steps exit 0`) is kept in the receipts folder's `gate-round1` folder. Its last line is:

> session-gate: all steps exit 0

- **Identity:** the tested_state was the same before and after the gate (`s75-D6-identity-before.txt`, `s75-D6-identity-after.txt`): `3397e78d7342d73e99dde3b43244a55cd6be7e87+38feee5f5521beeed6e8d96fadfb544a70cf5c2444a10d08be5553bcb4679fb8`. It is derived with `ELECTRON_RUN_AS_NODE` unset, as H1-6b's cell does. The plan's `*.md` files, this session's handoffs, the reflections, `metrics.md` and `current-focus.md` are artifacts the identity leaves out, so H1-3's current-focus edit and these handoffs do not change it.
- **Static:** pyright 0 errors; ruff passed; the UI typecheck and ESLint (`--max-warnings 0`) passed; the MCP typecheck passed; lint_task_contract passed on 24 rows (22 fully checked, 2 `view_file` exempt); scope-paths found 86 changed paths since `3397e78d7342`, none outside scope, HEAD did not move and no baseline-dirty path changed since row 0 (S3); route-comment-only found 5 changed route lines, none of them code; the red-check selftest read 71 fixtures with 0 wrong; id-length read 40 tests, none too long.
- **Suites:** pytest 2940 passed (`s75-D6-py-tests.txt`; the baseline's 2900 in `s75-baseline.txt` plus the 39 new cases that `s75-red-py.txt` ran at Red and F1's palette-alpha case, `s75-f1-red.txt`); Vitest Test Files 130 passed (130), Tests 1532 passed (1532), the baseline's counts, since no Vitest file changed; MCP Test Files 36 passed (36), Tests 535 passed (535), the baseline's counts, with the AC-145.14 `list` pin among them.
- **Build and state:** the UI build, the OpenAPI check and the MCP build exited 0; the state render (153 MEUs) and the issue render match the files on disk.
- **Runtime:** the Electron spec `ui/tests/e2e/capture-inbox.test.ts` passed 54 (`s75-D6-ui-electron.txt`; the baseline's 53 plus AC-146.19).
- **Skipped:** `mcp-audit` (live network, YouTube and the installed avkit servers, which the brief forbids) and `build-record` (no release and no package build in this session).
- **Baseline failures excused:** py [], ui [], mcp [], e2e []. Each gate run passed at its first attempt; the re-run is for F1's new tested_state, not a flake.
- **After the gate (both re-run after F1):** H1-3 (`s75-h13-check.txt`: `MEU-145 and MEU-146 ready_for_review: True`), H1-4 (`s75-api-hash-check.txt`: `API and MCP files changed since row 0: [] route code lines changed: []`) and the supplementary line-ending check (`s75-eol-final.txt`: `files checked: 37 line-ending drift: []`).

---

## Changed Files

Against `3397e78`, outside this plan folder and the handoffs, `git diff --numstat` reads 17 tracked files, 516 insertions and 105 deletions (it counts H1-3's `current-focus.md` paragraph too), plus five new test files.

| File | Line endings | Change |
|------|--------------|--------|
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` | CRLF, kept | +152 −48: `PROBE_FIXED`, `SHOWN_FORMATS`, `SHOWN_OPEN`, `PROBE_SWAP`, `SHOWN_TAG`, `READ_SHOWN`, `VIEW_SHOWN`, `ICC_KEEP`, `CROP_EXPORT_FRAME`, and F1's palette alpha in `_encode_view` (D-1002) |
| `packages/core/src/avkit_core/services/capture.py` | CRLF, kept | +223 −16: `SCAN_SKIP`, `KEEP_ROW`, `SKIP_LOG`, `DIMS_REFRESH`, `READ_SHOWN`, `BAKE_MARKER`, `STALE_BAKE`, `STAGED_REBAKE` |
| `packages/core/src/avkit_core/ports/capture.py` | CRLF, kept | +8: `shown_tag`, `read_shown` |
| `packages/api/src/avkit_api/routes/captures.py` | CRLF, kept | +3 −2, comment lines only (`:425-427`) |
| `tests/unit/test_capture_service.py` | CRLF, kept | +8: `FakeCapturePort.shown_tag` and `read_shown` |
| `tests/unit/test_capture_export_service.py` | LF, kept | +8: `FakeAnnotate.shown_tag` and `read_shown` |
| `tests/unit/test_capture_export_adapter.py` | LF, kept | +8 −9: AC-136.7 renamed and flipped (AC-146.11) |
| `tests/e2e/test_api_capture_crop.py` | LF, kept | −4: AC-130.21's restore removed (AC-145.15) |
| `ui/tests/e2e/capture-inbox.test.ts` | LF, kept | +56 −1: AC-146.19 |
| `tests/orientation_fixtures.py` | LF, new | 202 lines: the Pillow fixture builder |
| `tests/unit/test_capture_scan_unreadable.py` | LF, new | 398 lines: AC-145.1 to AC-145.11 |
| `tests/e2e/test_api_capture_scan_unreadable.py` | LF, new | 122 lines: AC-145.12, AC-145.13 |
| `tests/unit/test_capture_orientation.py` | LF, new | 943 lines: AC-146.1 to AC-146.10, AC-146.12 to AC-146.14, AC-146.20 to AC-146.26, with F1's palette-alpha case under AC-146.20 (`:478`) |
| `tests/e2e/test_api_capture_orientation.py` | LF, new | 243 lines: AC-146.15 to AC-146.18, AC-146.27, AC-146.28 |
| `docs/build-plan/09-screenshot-capture.md` | CRLF, kept | +22: the two Delivered (Session 75) notes |
| `.agent/context/known-issues.yaml`, `known-issues.md` | LF, kept | the two issues resolved (tool) and the render |
| `.agent/context/meu-status.yaml`, `meu-registry.md`, `docs/BUILD_PLAN.md` | LF, kept | MEU-145 and MEU-146 `ready_for_review` (tool) and the render |
| `.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md` | LF, kept | row 75 executed |
| `.agent/context/current-focus.md` | CRLF, kept | +3: the Session 75 paragraph (H1-3) |
| `docs/execution/plans/2026-11-15-capture-inbox-probe/implementation-plan.md`, `task.md` | LF, kept | Status line (coordinator), lines 220 and 230 (D-1001), the row marks |

Line endings were measured in bytes against row 0's `s75-anchors.txt` at rows 1, 3, 4 and 5, at F1's Green (`s75-f1-eol.txt`) and again after H1-4 (`s75-eol-final.txt`: 37 files, no drift). No file outside the plan's §Files Modified, this plan folder and the closeout artifacts it names was edited. Nothing was staged or committed.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Blocking | Finding | Fix | Status |
|---|----------|----------|---------|-----|--------|
| F1 | Medium | no | Round 1: `read_shown` turned a palette PNG with a `tRNS` chunk, and `_encode_view`'s PNG branch converted it to RGB, so the plain download made its transparent pixels opaque. | D-1002: `_encode_view` converts a palette PNG with `transparency` to RGBA (`packages/infrastructure/src/avkit_infra/capture/adapter.py:384-389`); regression `test_ac_146_20_read_shown_keeps_palette_alpha` at `tests/unit/test_capture_orientation.py:478`. | fixed |

Round 1 approved with F1 open and non-blocking. Round 2 rechecked the fix and recorded F1 `fixed`, with no new finding; its report wrote "None." under `### New Findings`, which the closeout parser reads as one open finding, so round 3 was a format-only recheck that rewrote that section as an empty table and confirmed the tested_state unchanged (`3397e78d7342d73e99dde3b43244a55cd6be7e87+38feee5f5521beeed6e8d96fadfb544a70cf5c2444a10d08be5553bcb4679fb8`). The canonical rolling report is `.agent/context/handoffs/2026-11-15-capture-inbox-probe-implementation-critical-review.md`.

### Verdict

`approved` at round 3 of 6 (ledger loop `s75-execution-2026-11-15-capture-inbox-probe`), with 0 open blocking findings. The review grants no commit or push authorization.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| The inbox resolver's `InboxPathError(f"{resolved} is not a file")` names a path; it is at `services/capture.py:2294` now (`:2089` when the plan was written) | residual for triage | none | Not the scan path, and neither issue names it (plan §Out of Scope) |
| A flag field for skipped files in the list | out-of-scope | none | M-4 (D-900) |
| Commit and push | out-of-scope | — | Only on Mat's explicit words (H2-5) |

### Departures and their basis

- **The Status line (plan line 15).** The coordinator wrote Mat's execute words into it before row 0. It is a plan-text edit made after the plan review approved, and it changes no AC or contract.
- **Decision ids.** Execution decisions use D-1000 to D-1009, not "the next free id after D-910" as H1-6's row says; the coordinator assigned the range so the parallel sessions of the grouping cannot collide. D-1000 to D-1002 are used.
- **Where the decisions are recorded.** H1-6's row says an execution decision goes in the plan's YAML and each handoff's Decision Log is `None.`. Under HDP v2 §6 and the coordinator's direction, D-1000 to D-1002 are recorded in the MEU-146 handoff's Decision Log, which the closeout reads; the plan's YAML is unchanged. The MEU-145 handoff's Decision Log is `None.` because no MEU-145 decision was made in execution.
- **Row commands.** Every row ran through a `.ps1` written from its task cell, because the cells' `*>` needs PowerShell; Vitest and Electron ran through pwsh in `P:/av-kit/ui`, and every pytest run set TMP and TEMP to the plan's `tmp` folder under the receipts folder.
- **The F1 correction came after round 1 approved.** The Codex execution review's round 1 approved Session 75 with one Medium, non-blocking finding, F1: `read_shown` turned a palette PNG with a `tRNS` chunk and `_encode_view`'s PNG branch converted it to RGB, so the plain download made its transparent pixels opaque. On the coordinator's call it was corrected in this session (D-1002): a Red case first (`s75-f1-red.txt`), a one-condition fix in `_encode_view`, Green, then H1-2, H1-3, H1-4, the line-ending check, H1-6, H1-6a and H1-6b again against the new tested_state.
- **No network, no real inbox.** No row and no gate step made a network request, and every test writes into its own `tmp_path` (S5).
- **Moved cites (Session 51 RULE-3).** Against the plan's row-0 anchors: `scan_inbox` is `services/capture.py:651` (was `:597`), `probe` `adapter.py:534` (was `:461`); the 09 note cites both.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-15 | claude-code-local (Claude Opus 5.5) | Initial MEU-145 handoff after the H1-2 gate, H1-3 and H1-4 |
| Updated | 2026-11-15 | claude-code-local (Claude Opus 5.5) | After the round 1 execution review: F1 corrected (D-1002, in the MEU-146 handoff); the gate re-run, so the full record's tested_state and pytest count changed |
