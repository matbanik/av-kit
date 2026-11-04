---
date: "2026-10-03"
project: "capture-flatten-backup"
meu: "MEU-67"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-02-capture-flatten-backup/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code-web"
reviewer: "claude-fable-5-1-subagent (user-authorized, human-review-decision.md)"
predecessor: ".agent/context/handoffs/2026-10-01-capture-viewport-chrome-MEU-66-handoff.md"
---

# Handoff: 2026-10-02-capture-flatten-backup-MEU-67-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-67 — `capture-flatten-backup`. Saved overlay marks can be baked into the capture image, with a backup to revert from, across the API, MCP and GUI.
- **API (cycle 1):**
  - `POST /captures/{id}/flatten` bakes the saved marks into a PNG in place (`FLATTEN_SEQUENCE`). It writes a backup first when `capture.flatten_backup` is on (`BACKUP_DIR_RULE`, `BACKUP_NAME`) and rolls back on failure (`FLATTEN_ROLLBACK`).
  - A JPEG or WebP shot gets a new `{stem}-converted.png` shot instead, and the original stays untouched (`CONVERT_ON_APPLY`).
  - `POST /captures/{id}/revert` restores the newest backup (`LATEST_BACKUP`, `REVERT_SEQUENCE`) and re-bakes the annotated copy if saved marks remain (`ANNOTATED_CONSISTENCY`).
  - The detail gains `backup_path`.
  - Save overlay can write PNG, JPEG or WebP (`ANNOTATED_FORMATS`, `LOSSY_QUALITY` 90).
  - All capture file work is serialized by `CAPTURE_FILE_LOCK`.
- **Settings:** `capture.flatten_backup` (true), `capture.backup_dir` ("") and `capture.annotated_format` ("png"), in the API, MCP and renderer schemas.
- **MCP (cycle 1):**
  - The registry gains `avkit_capture.flatten` and `avkit_capture.revert` (destructive, `confirm: true`).
  - Capture `remove`, `flatten` and `revert` also ask the person, and are refused unless they accept (`USER_CONFIRM`, fail closed). The question goes through MCP elicitation (120 s timeout). When the client has no elicitation, or declines or cancels faster than `USER_CONFIRM_AUTODECLINE_MS` (an IDE that auto-declines), the server asks with a topmost Windows Yes/No dialog instead (`DIALOG_FALLBACK`, A-11). Only an explicit accept runs.
  - Capture ids are opaque server tokens, validated at the boundary, and every path parameter is percent-encoded, so agent text never reaches the prompt or another route (review round 1, F1).
  - The server instructions say what each capture action does to files (`INSTRUCTION_TEXT`).
  - The live audit gains the flatten/revert steps, a declined-prompt refusal and `capture.backup_dir` isolation.
- **GUI (cycle 2):**
  - **Apply to image** (`APPLY_ENABLED`) and **Revert** (`REVERT_VISIBLE`) sit in the per-shot actions, with inline confirm strips (`CONFIRM_KINDS`).
  - The status line reports each outcome (`FLATTEN_STATUS`), and the viewport and thumbnail refetch (`IMAGE_REVISION`).
  - A converted shot becomes the selection.
  - The Settings Capture card shows the three leaves, and the help card explains the feature.

**Build Plan Section**: `docs/build-plan/09-screenshot-capture.md` §Flatten with backup (09:652-659), §MCP (09:487, 09:526), Settings (09:603, 09:655).
**Predecessor**: MEU-66 (the Capture viewport and per-shot actions this builds on).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-67.1 | integration | PNG flatten with backups on: detail with no marks, backup with the original's bytes, original baked | Spec 09:657 | `tests/e2e/test_api_capture_flatten.py::test_ac_67_1_flatten_png_with_backup` | ✅ |
| AC-67.2 | unit | `FLATTEN_SEQUENCE`: the backup exists before `bake` | Spec 09:657 | `tests/unit/test_capture_service.py::test_ac_67_2_backup_exists_before_bake` | ✅ |
| AC-67.3 | unit | `FLATTEN_ROLLBACK` on a bake failure (503) and a replace failure (409) | D-8 | `test_capture_service.py::test_ac_67_3_rollback_on_bake_and_replace_failure` (2) | ✅ |
| AC-67.4 | integration | `FLATTEN_CONFLICTS` (a)–(d) → 409 with no change | D-9 | `test_api_capture_flatten.py::test_ac_67_4_flatten_conflicts_change_nothing` | ✅ |
| AC-67.5 | integration | Missing body and `{}` accepted; extra key 422; no bearer 401 | Local Canon | `::test_ac_67_5_boundary_bodies_and_auth` | ✅ |
| AC-67.6 | integration | Backups off: baked, no backup written | Spec 09:655 | `::test_ac_67_6_flatten_with_backups_off` | ✅ |
| AC-67.7 | integration | Revert restores the backup bytes, keeps the backup, re-bakes | Spec 09:659 | `::test_ac_67_7_revert_restores_and_rebakes` | ✅ |
| AC-67.8 | integration | Revert without a matching backup → 404, no change | Spec 09:659 | `::test_ac_67_8_revert_without_backup_is_404` | ✅ |
| AC-67.9 | unit | `BACKUP_NAME` collision suffix; `LATEST_BACKUP` by name | D-13 | `test_capture_service.py::test_ac_67_9_backup_names_and_latest` | ✅ |
| AC-67.10 | integration | Detail carries `backup_path`; list keys unchanged | Spec 09:654 | `::test_ac_67_10_detail_backup_path_list_unchanged` | ✅ |
| AC-67.11 | integration | Settings defaults and validation (StrictBool, enum) | Spec 09:655; A-2 Q2 | `::test_ac_67_11_capture_settings_leaves` | ✅ |
| AC-67.12 | unit | `BACKUP_DIR_RULE` | D-11 | `test_capture_service.py::test_ac_67_12_resolve_backup_dir` (parametrized) | ✅ |
| AC-67.13 | integration | Inbox invariant (API) and watcher filter (Vitest) | Spec 09:658 | `::test_ac_67_13_backups_and_temps_never_become_shots`; `ui/tests/unit/capture-main.behavior.test.ts` `AC-67.13 …` | ✅ |
| AC-67.14 | unit | `CAPTURE_FILE_LOCK` serializes flatten and scan | D-14 | `test_capture_service.py::test_ac_67_14_file_lock_serializes_flatten_and_scan` | ✅ |
| AC-67.15 | integration | OpenAPI: exactly two new paths; schema changes limited | Local Canon G8 | `::test_ac_67_15_openapi_routes_and_detail_schema`; `validate-task.sh gate-cycle1` openapi diff | ✅ |
| AC-67.16 | integration | MCP flatten/revert refuse missing/false/extra confirm with zero fetches; accept POSTs `{}` once | Spec 09:656 | `mcp-server/tests/capture.test.ts` `AC-67.16 …` (4) | ✅ |
| AC-67.17 | unit | Registry order, destructive keys, M7 markers, settings keys and Zod | Spec 09:656 | `capture.test.ts` `AC-67.17 …` | ✅ |
| AC-67.18 | unit | `INSTRUCTION_TEXT` | D-19; A-2 Q3 | `capture.test.ts` `AC-67.18 …` | ✅ |
| AC-67.19 | integration | Audit steps, isolation, a test-local userConfirm step over the fake backend; container live audit | Spec 05:300 | `mcp-server/tests/audit/runner-fake-backend.test.ts` `AC-67.19 …` (2); `audit-container` | ✅ container; authoritative run at `LOCAL_SEQUENCE` step 1 |
| AC-67.20 | integration | GUI Apply placement and `APPLY_ENABLED` titles | Spec 09:657; A-2 Q1 | `ui/tests/unit/capture-flatten.test.ts` (2); `capture-page.behavior.test.ts` `AC-67.20 …` (2); `capture-inbox.test.ts` `AC-67.20 AC-67.21 AC-67.22 …` | ✅ |
| AC-67.21 | integration | Flatten confirm texts; Cancel sends nothing; Confirm POSTs `{}` once; strip locks the page | Spec 09:657 | `capture-flatten.test.ts` (2); `capture-page.behavior.test.ts` `AC-67.21 …` (2); Electron (same spec as AC-67.20) | ✅ |
| AC-67.22 | integration | Success status, marks cleared, Original view, image refetch; 409 changes nothing | Spec 09:657-658 | `capture-flatten.test.ts` `AC-67.22 AC-67.33 …`; `capture-page.behavior.test.ts` `AC-67.22 …` (2); Electron (same spec as AC-67.20) | ✅ |
| AC-67.23 | integration | Revert visibility, strip, POST, status, refetch; disabled while dirty | Spec 09:659 | `capture-flatten.test.ts` (2); `capture-page.behavior.test.ts` `AC-67.23 …` (2); `capture-inbox.test.ts` `AC-67.23 …` | ✅ |
| AC-67.24 | integration | Settings card leaves and PUT; renderer schema rejections | Spec 09:603, 09:655 | `capture-page.test.ts` `AC-67.24 …` (3); `capture-inbox.test.ts` `AC-67.24 …` | ✅ |
| AC-67.25 | unit | `FLATTEN_HELP_SENTENCE` appended; old sentence verbatim | 09:155-157 | `capture-help-content.test.ts` `AC-67.25 …` | ✅ |
| AC-67.26 | unit | `NEW_TESTIDS` after the MEU-66 block, unique, used | Local Canon AC-51.6 | `capture-flatten.test.ts` `AC-67.26 …` | ✅ |
| AC-67.27 | integration | `CONVERT_ON_APPLY` for JPEG and WebP; failure leaves nothing | A-2 Q1; D-22 | `::test_ac_67_27_convert_on_apply` (2); `::test_ac_67_27_convert_failure_leaves_nothing` | ✅ |
| AC-67.28 | integration | `ANNOTATED_FORMATS` Save output | A-2 Q2; D-23 | `::test_ac_67_28_annotated_formats` | ✅ |
| AC-67.29 | unit | `BAKE_PORT` lossy formats at `LOSSY_QUALITY` | D-23 | `tests/unit/test_capture_adapter.py::test_ac_67_29_bake_output_formats` | ✅ |
| AC-67.30 | unit | `USER_CONFIRM` in `handleTool` for every outcome; never asked for refused parses or non-members | A-2 Q3; D-24 | `mcp-server/tests/user-confirm.test.ts` `AC-67.30 …` (17) | ✅ |
| AC-67.31 | integration | `USER_CONFIRM` through the SDK: accept, decline, throw, no capability; timeout option | A-2 Q3 | `user-confirm.test.ts` `AC-67.31 …` (4) | ✅ |
| AC-67.32 | integration | `AUDIT_ELICITATION`: client capability, default decline, `refusalVerdict` | D-24 | `mcp-server/tests/audit/classify.test.ts` `AC-67.32 …` (6); `audit-container` `refusal_declined` | ✅ |
| AC-67.33 | integration | GUI convert selection and status; the JPEG stays | A-2 Q1 | `capture-page.behavior.test.ts` `AC-67.33 …`; `capture-inbox.test.ts` `AC-67.33 …` | ✅ |
| AC-67.34 | integration | `ADVERTISED_SCHEMA`: `tools/list` advertises `action` as an enum plus typed fields for every tool, so discovery is clean. The server still refuses a string `confirm` or an extra key, with no API call and no prompt. | Human-approved A-9 | `mcp-server/tests/user-confirm.test.ts` `AC-67.34 …` (3) | ✅ |
| AC-67.35 | integration | `DISABLED_REASON_TIP`: hovering a disabled Apply/Revert shows a rendered `role="tooltip"` reason | Human-approved A-10 | `capture-page.behavior.test.ts` `AC-67.35 …`; `capture-inbox.test.ts` `AC-67.35 …` | ✅ |
| AC-67.36 | integration | `DIALOG_FALLBACK`: with no elicitation, a throwing handler, or a decline faster than `USER_CONFIRM_AUTODECLINE_MS`, the Windows dialog is asked with `USER_CONFIRM_MESSAGE`. Only its accept runs; every other outcome, including dialog errors, is refused with zero API calls. | Human-approved A-11 | `mcp-server/tests/user-confirm.test.ts` `AC-67.36 …` (including the 98e5551 `runDialog` cases) | ✅ |

### Other plan AC references (not owned by MEU-67)

| AC | Owner | Status in MEU-67 |
|----|-------|------------------|
| AC-12.8 | MEU-12 service layering guard (`tests/unit/test_services.py`) | unchanged; it passes since A-5 (backup folder created through `ImageAnnotatePort.ensure_dir`) |
| AC-34.10 | existing domain suite | unchanged |
| AC-38.2 | MEU-38 capture MCP suite | TA-2 (10 rows) |
| AC-41.3, AC-51.6 | existing suites | declared env-bound Vitest members; AC-51.6 also proves the `NEW_TESTIDS` prefix |
| AC-50.1 | layout-canon suite | re-run at row 10 |
| AC-68.5, AC-68.8 | MEU-68 audit suites | TA-1, TA-3 (AC-68.5) and TA-5 (AC-68.8); the committed-baseline clause of AC-68.5 is `BASELINE_PENDING` until `LOCAL_SEQUENCE` step 1 |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| pytest AC-67.1, 67.4–67.8, 67.10, 67.11, 67.13, 67.15, 67.27, 67.28 (14) | `AssertionError: BAKE_PORT output_format missing` (the `_require_meu67` precondition) | pass | `tests/e2e/test_api_capture_flatten.py` |
| pytest AC-67.2, 67.3, 67.9, 67.12, 67.14, 67.29 (6) | missing symbol (`flatten`, `resolve_backup_dir`, `LOSSY_QUALITY`, …), declared new | pass | `tests/unit/test_capture_service.py`, `test_capture_adapter.py` |
| MCP Vitest AC-67.16–67.19, 67.30–67.32 (31) | `USER_CONFIRM_ACTIONS export: expected undefined to be an instance of Set` (21); `expected { verdict: 'pass', … } to deeply equal { verdict: 'fail', … }` (3); `expected true not to be true` (flatten/revert refused before fetch, 2); `expected 'av-kit is a local YouTube read/consum…' not to contain 'Files on disk are not deleted'` | pass | `mcp-server/tests/user-confirm.test.ts`, `capture.test.ts`, `audit/*.test.ts` |
| UI Vitest AC-67.20–67.26, 67.33 (20) | `capture-flatten.ts exports the APPLY_ENABLED rules: expected null not to be null`; `capture-apply-image rendered: expected null not to be null` | pass | `ui/tests/unit/capture-flatten.test.ts`, `capture-page.behavior.test.ts`, … |
| Electron AC-67.20–67.24, 67.33 (4 specs) | `expect(locator).toBeEnabled() failed … capture-apply-image … element(s) not found`; `locator.click: Timeout 30000ms exceeded … waiting for getByTestId('capture-apply-image')` (2); `expect(locator).toBeVisible() failed … settings-leaf-flatten_backup` | pass | `ui/tests/e2e/capture-inbox.test.ts` |

Every Red and Green receipt is in [walkthrough.md](../../../docs/execution/plans/2026-10-02-capture-flatten-backup/walkthrough.md) (§Rows 2–3, §Rows 4–5, §Row 6, §Rows 7–8, §Row 9).

**Test amendments (human-approved):**
- TA-1: the registry count is 70.
- TA-2: 10 capture rows plus 2 destructive keys.
- TA-3: the destructive audit list.
- TA-4: 7 capture setting keys.
- TA-5: 7 isolation keys.
- TA-6: `ROUTE_COUNT_AFTER` is 73.
- TA-7: `CaptureFlattenConflictError`.
- TA-8: the OpenAPI route index, `ACTION_INDEX_AFTER`, and `backup_path` in the detail fields. A-3 approved it.
- TA-9: the port `bake` signature. A-4 approved it.

The fixture repairs are (a)–(h). Repair (h) is from A-5: the container pre-gate found that the flatten backup folder was created with `mkdir` inside the service, which breaks the MEU-12 guard `test_ac_12_8_no_direct_mkdir_in_services`. The user chose a port method, so `ImageAnnotatePort.ensure_dir` creates the folder and no test expectation changed. The execution reviewer should check every TA row against its test file and line.

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s30-red-py","command":"bash docs/execution/plans/2026-10-02-capture-flatten-backup/validate-task.sh red-py","cwd":"/home/user/av-kit","scope":"AC-67 pytest (new + appended)","phase":"targeted","exit_code":0,"result":"pass","tested_state":"baseline product tree + row 2 tests","output":"PASS ac_67 pytest RED: 14 decisive, 6 missing-symbol","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s30-green-py","command":"bash docs/execution/plans/2026-10-02-capture-flatten-backup/validate-task.sh green-py","cwd":"/home/user/av-kit","scope":"PYT + REGPY","phase":"targeted","exit_code":0,"result":"pass","tested_state":"e00df09","output":"PASS s30-green-py: 214 passed; env-bound baseline failures tolerated (all in s30-baseline-pytest.txt)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s30-red-mcp","command":"bash docs/execution/plans/2026-10-02-capture-flatten-backup/validate-task.sh red-mcp","cwd":"/home/user/av-kit","scope":"MCPT","phase":"targeted","exit_code":0,"result":"pass","tested_state":"bdd73b4","output":"PASS AC-67 RED: 31 failing AC-67 assertions, 235 passing","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s30-green-mcp","command":"bash docs/execution/plans/2026-10-02-capture-flatten-backup/validate-task.sh green-mcp","cwd":"/home/user/av-kit","scope":"MCPT","phase":"targeted","exit_code":0,"result":"pass","tested_state":"e00df09","output":"PASS s30-green-mcp: 280 passed of 281, BASELINE_PENDING tolerated: 1","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s30-gate-cycle1","command":"bash docs/execution/plans/2026-10-02-capture-flatten-backup/validate-task.sh gate-cycle1","cwd":"/home/user/av-kit","scope":"pyright, ruff, pytest, MCP typecheck/build/full suite, OpenAPI two-step + diff, container audit","phase":"targeted","exit_code":0,"result":"pass","tested_state":"e00df09","output":"PASS s30-c1-mcp-tests: 376 passed of 377, BASELINE_PENDING tolerated: 1 | PASS openapi diff: +['/api/v1/captures/{id}/flatten', '/api/v1/captures/{id}/revert'] | PASS audit-container: capture.flatten, capture.revert and capture.remove pass with declined refusals","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s30-red-ui","command":"bash docs/execution/plans/2026-10-02-capture-flatten-backup/validate-task.sh red-ui","cwd":"/home/user/av-kit","scope":"UNIT67 Vitest, fresh build, Electron capture-inbox -g AC-67","phase":"targeted","exit_code":0,"result":"pass","tested_state":"1e6c931","output":"PASS AC-67 RED: 20 failing AC-67 assertions, 122 passing | PASS AC-67 E2E RED: 4 failing AC-67 specs","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s30-green-ui","command":"bash docs/execution/plans/2026-10-02-capture-flatten-backup/validate-task.sh green-ui","cwd":"/home/user/av-kit","scope":"UNIT67 + REGCAP Vitest, ui build, Electron -g AC-67","phase":"targeted","exit_code":0,"result":"pass","tested_state":"23d37ca","output":"PASS s30-green-ui: 227 passed of 228, env-bound tolerated: ['MEU-51 shared layout primitives AC-51.6 '] | PASS s30-green-ui-build | PASS s30-green-ui-e2e: 4 passed","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s30-gate67","command":"bash docs/execution/plans/2026-10-02-capture-flatten-backup/validate-task.sh gate67","cwd":"/home/user/av-kit","scope":"ui typecheck, lint, UNIT67 + REGCAP Vitest, ui build, harness build, Electron capture-inbox + settings (whole files), repeat-each=20 over AC-67|AC-57.10","phase":"targeted","exit_code":0,"result":"pass","tested_state":"5045d2e","output":"PASS s30-67-typecheck | PASS s30-67-lint | PASS s30-67-vitest: 227 passed of 228, env-bound tolerated: ['MEU-51 shared layout primitives AC-51.6 '] | PASS s30-67-build | PASS s30-67-harness-build | PASS s30-67-e2e: 35 passed, env-bound tolerated: [] | PASS repeat-each=20 67-capture (stats expected 160, unexpected 0, flaky 0)","fresh":true}
```

The authoritative full gate is `WINDOWS_GATE`, and the authoritative audit is `LOCAL_SEQUENCE` step 1 (H1-6).

### Quality Gate Results

```
pyright: 0 errors; ruff: all checks passed
pytest PYT + REGPY: 214 passed (env-bound baseline failures only)
MCP full suite: 376/377 (BASELINE_PENDING: committed audit baseline until LOCAL_SEQUENCE step 1)
container live audit: capture.flatten / capture.revert / capture.remove pass with declined refusals; cleanup ok
ui typecheck: 0 errors; ui lint: 0
Vitest UNIT67 + REGCAP: 227/228 (AC-51.6 env-bound)
Electron capture-inbox + settings: 35 passed
repeat-each=20 (AC-67|AC-57.10): 160 expected, 0 unexpected, 0 flaky
api-scope: 54 changed product files, all listed; adapter drawing unchanged
```

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/domain/capture.py` | modified | `AnnotatedFormat`, `ANNOTATED_FORMATS`, `ANNOTATED_EXT`, `ANNOTATED_SUFFIXES` |
| `packages/core/src/avkit_core/domain/errors.py` | modified | `CaptureFlattenConflictError` (+ `DOMAIN_ERROR_TYPES`) |
| `packages/core/src/avkit_core/ports/capture.py` | modified | `bake(..., output_format="png")`; `ensure_dir(path)` (A-5) |
| `packages/core/src/avkit_core/services/capture.py` | modified | flatten/convert/revert, backup naming and dir rule, `CAPTURE_FILE_LOCK`, annotated format siblings |
| `packages/core/src/avkit_core/services/settings.py` | modified | three capture leaves |
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` | modified | `LOSSY_QUALITY`, JPEG/WebP writer |
| `packages/api/src/avkit_api/routes/captures.py`, `schemas/captures.py`, `schemas/settings.py` | modified | two routes, `backup_path`, settings leaves (StrictBool) |
| `openapi.committed.json` | regenerated | two paths; `CaptureShotDetailOut`, `SettingsPutIn` |
| `mcp-server/src/toolsets/registry.ts` | modified | two rows; `USER_CONFIRM` in `handleTool`; elicitation wiring and the dialog fallback in `registerMcpSurface` (A-11); `tools/list` rewritten with `ADVERTISED_SCHEMA` (A-9); path parameters percent-encoded (review F1) |
| `mcp-server/src/destructive.ts` | modified | two destructive keys; `USER_CONFIRM_ACTIONS`, timeout, messages |
| `mcp-server/src/toolsets/capture.ts`, `settings.ts`, `src/index.ts` | modified | schemas/descriptions, settings leaves, `INSTRUCTION_TEXT` |
| `mcp-server/scripts/audit/{plan,client,classify,run,types}.ts` | modified | `AUDIT_STEPS`, `AUDIT_ELICITATION`, `AUDIT_ISOLATION` |
| `ui/src/renderer/src/features/capture/capture-flatten.ts` | new | `applyState`, `revertState`, confirm texts, `flattenStatus` |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modified | Apply/Revert, `CONFIRM_KINDS` switch, notice, `IMAGE_REVISION`, convert selection |
| `ui/src/renderer/src/features/capture/{capture-commands,CaptureFilmstrip,useCaptureSettings,capture-help-content}.ts(x)` | modified | commands, thumbnail key, leaves, help sentence |
| `ui/src/renderer/src/features/settings/{settings-schemas,SettingsPage}.ts(x)` | modified | schema leaves; Capture card rows (the backup folder is an inline `FormRow` + input + Browse, so `PathRow` stays unchanged) |
| `mcp-server/src/native-confirm.ts` | new (A-11) | Windows Yes/No dialog runner for `DIALOG_FALLBACK`; injectable runner, monotonic timing, dialog errors are `cancel` (98e5551) |
| `.agent/model-registry.local.json` | modified (A-12) | `validated_against` pin revalidated against the current shared registry |
| Tests | new/appended | see the AC table; TA-1..TA-9; fixture repairs (a)–(h) |

---

## Codex Validation Report

_Left blank for reviewer agent. Reviewer fills this section during `/validation-review`._

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|

### Verdict

_pending_

---

## Corrections Applied (2026-10-03, after LOCAL_SEQUENCE attempt 1)

**Findings resolved:** F1 (A-6, A-10), F8 (A-7, A-9) and the attempt 2 gate drift (A-8).

| # | Finding | Fix Applied | Verification |
|---|---------|-------------|--------------|
| 1 | F1: a disabled Apply/Revert never shows its reason. The shared `Button` primitive sets `disabled:pointer-events-none`, so the native `title` cannot appear. | `CapturePage.tsx` wraps Apply and Revert in `capture-apply-image-tip` / `capture-revert-image-tip` spans that carry the reason while the button is disabled. In the AC-67.20 jsdom test, the "same row as Delete" assertion now reads the wrapper's parent. | jsdom A-6 test (Red, then Green); Electron `AC-67.20 A-6 …` (Red on the pre-fix renderer: `Received: null`; Green after); gate67 36/36 Electron, repeat 180/0/0 |
| 2 | F8: av-kit never loaded in the VS Code extension. The local scope is keyed by a case-sensitive project path, and Settings has no viewable setup prompt. | Out of Session 30 by A-7. `MCP-SETUP-PROMPT` is filed for its own plan session. F8 is re-run with a researched project `.mcp.json` recipe. | `LOCAL_SEQUENCE` attempt 2 |
| 3 | Attempt 2, F1: no native tooltip shows on any Capture button (`CAPTURE-TOOLTIPS-NOT-SHOWN`, app-wide, not caused by this diff) | A-10: the wrapper renders a fixed-position `role="tooltip"` reason while the action is disabled | AC-67.35 jsdom and Electron (Red on the A-6 page: element not found; Green after) |
| 4 | Attempt 2, F8e: Claude Code refused `confirm: true` with "Invalid input" before any prompt, because `tools/list` advertised an empty schema (`MCP-TOOLS-LIST-EMPTY-INPUT-SCHEMA`) | A-9: `registerMcpSurface` rewrites `tools/list` with `ADVERTISED_SCHEMA` (action enum + typed fields, `additionalProperties: false`); the registered strict union is unchanged | AC-67.34 (Red: no action enum; Green after); full MCP suite 380/380 |
| 6 | Attempt 3, F8: Claude Code (VS Code) declares elicitation but declines every prompt itself, so no capture action could be accepted | A-11: `DIALOG_FALLBACK` (Windows dialog after an auto-decline); local Codex review findings fixed in 98e5551 | AC-67.36; `LOCAL_SEQUENCE` attempt 4 F8 passes both paths |
| 7 | Attempt 3 `WINDOWS_GATE`: two framework-adoption tests failed with `overlay_not_validated` after the shared registry changed | A-12: the overlay's `validated_against` pin is revalidated | Attempt 4 `WINDOWS_GATE` 17/17 stages, pytest 653/0 |
| 5 | Attempt 2: `WINDOWS_GATE` preflight drift (`P:/.agent/model-registry.json` changed outside av-kit) | A-8: `validate-task.ps1 -AcceptDrift A-8` records the accepted drift with the previous hashes; `windows-gate-check` accepts drift only with a recorded A-decision | windows-gate-check exercised on synthetic results: raw drift and an unrecorded A-99 are refused, A-8 is accepted |

## Corrections Applied (2026-10-08, execution review round 1)

The review is `.agent/context/handoffs/2026-10-02-capture-flatten-backup-implementation-critical-review.md`.

| # | Finding | Fix Applied | Verification |
|---|---------|-------------|--------------|
| F1 (High) | An agent-supplied capture `id` reached the `USER_CONFIRM` prompt and, unencoded, the request path (`/../` traversal) | `CAPTURE_ID_PATTERN` (an opaque id) on every capture `id`; `interpolatePath` percent-encodes each path parameter | 5 tests, Red then Green; MCP suite 411/411 |
| F2 (Medium) | This handoff predated A-11 and A-12 | AC-67.36 row, `native-confirm.ts` and overlay rows, the scope sentence, (a)–(h), corrections 6–7 | `validate-task.sh handoff-ac` |
| F4 (Low) | Convert rollback could orphan the target's backup; revert without marks left a stale sidecar | Convert rollback deletes the target-stem backups this call created; the empty-marks revert unlinks the sidecar | 2 unit negatives, Red then Green |
| F5 (Low) | Revert was `ghost`, while the plan says `secondary` | `variant="secondary"` | jsdom variant test, Red then Green |

F3 (the framework-HEAD drift record) needs Mat's decision, and F6 (stale plan wording) goes to plan corrections. Both are tracked in the review file.

## Deferred Items

None. The authoritative audit, `WINDOWS_GATE` and `FLATTEN_LOOK` F1–F8 run on Mat's machine at H1-6, as planned.

---

## Decision Log

```yaml
decision_log:
  - id: D-25
    stage: execution
    question: "Where do USER_CONFIRM_ACTIONS, the timeout and the prompt messages live, and what does a throwing confirmWithUser mean?"
    resolution: autonomous
    class: two-way
    chosen: "src/destructive.ts beside DESTRUCTIVE_ACTIONS; a thrown error is the outcome cancel (refused)"
    source_tag: Local Canon
    precedents: ["implementation-plan.md Files table — destructive.ts gains USER_CONFIRM_ACTIONS", "USER_CONFIRM — anything else or a thrown error/timeout → cancel (fail closed)"]
    research: { engine: none, sources: [] }
    reasoning: "Keeping the membership, timeout and messages beside the destructive set gives one module for every confirmation rule. Treating a throw as cancel matches the plan's fail-closed rule for the SDK path in handleTool too."
  - id: D-26
    stage: execution
    question: "How does the audit require all three flatten probe fields to change, and revert to restore the pre-flatten bytes?"
    resolution: autonomous
    class: two-way
    chosen: "destructiveStep gains an optional confirmedEffect(ctx, before, after); flatten checks sha changed, annotated gone, backup_count + 1; revert checks the sha recorded by flatten's precondition"
    source_tag: Local Canon
    precedents: ["implementation-plan.md AUDIT_STEPS", "scripts/audit/plan.ts destructiveStep (default effect: any probe change)"]
    research: { engine: none, sources: [] }
    reasoning: "The default 'any change' oracle would pass a flatten that wrote no backup. An explicit effect predicate keeps the refusal checks unchanged and makes the confirmed check exactly the plan's."
  - id: D-27
    stage: execution
    question: "How does FLATTEN_STATUS tell a flatten with a backup from one without, when an older backup can still be the newest?"
    resolution: autonomous
    class: two-way
    chosen: "Compare the detail's backup_path before and after: a new non-null value means a backup was written"
    source_tag: Local Canon
    precedents: ["implementation-plan.md FLATTEN_STATUS", "LATEST_BACKUP — the newest backup by name"]
    research: { engine: none, sources: [] }
    reasoning: "Reading the backups setting at call time could disagree with what the server did if the setting changed in between. The before/after detail values come from the server."
  - id: D-28
    stage: execution
    question: "The ruff rewrap of the GET detail docstring changed an existing OpenAPI path; what is the fix?"
    resolution: autonomous
    class: two-way
    chosen: "Restore the baseline docstring verbatim and regenerate openapi.committed.json"
    source_tag: Local Canon
    precedents: ["validate-task.sh gate-cycle1 — existing openapi paths must not change", "AC-67.15"]
    research: { engine: none, sources: [] }
    reasoning: "The docstring is the OpenAPI description; the plan allows only the two new paths and two schema changes. The baseline text already met the line limit."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-03 | claude-code-web | Initial handoff after gate67 |
