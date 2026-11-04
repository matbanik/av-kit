---
date: "2026-11-04"
project: "release-rc1"
meu: "MEU-112"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-03-release-rc1/implementation-plan.md"
build_plan_section: "bp08"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "none"
---

# Handoff: 2026-11-03-release-rc1-MEU-112-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-112, `convert-job-gpu-preference`. The encoder chosen for one Convert job now decides that job's encoder.
**Build Plan Section**: [08 §Encoder choice per job (residual)](../../../docs/build-plan/08-video-conversion.md#job-encoder-choice-residual).
**Predecessor**: none. The [MEU-108 handoff](2026-11-03-release-rc1-MEU-108-handoff.md), the [MEU-109 handoff](2026-11-03-release-rc1-MEU-109-handoff.md), the [MEU-110 handoff](2026-11-03-release-rc1-MEU-110-handoff.md) and the [MEU-111 handoff](2026-11-03-release-rc1-MEU-111-handoff.md) are the same plan's other MEUs.

Before this MEU, `POST /conversions` accepted `gpu_preference` and the page had an Encoder dropdown, but nothing read the value, so only the saved setting chose the encoder (`CONVERT-JOB-GPU-PREFERENCE-IGNORED`). The RC smoke found it, D-191 disclosed it, and Mat overruled that with "2: fix it".

- **The job.** `ConversionJob` gains a nullable `gpu_preference` (`packages/core/src/avkit_core/domain/conversion.py:275`, validated at `:290-291`). Only a Compress job stores what the request sent (`packages/core/src/avkit_core/services/conversion.py:306-307`). Cut and Extract store null.
- **The encoder.** `_dispatch` passes the job's value to `_resolve_encoder` (`services/conversion.py:488`). An explicit value wins, including Auto. Null means the setting, read when the job runs (`:402`, through `_preference` at `:393-394`).
- **The column.** `conversion_jobs` gains a nullable last column (`packages/infrastructure/src/avkit_infra/database/migrations.py:45`, `models.py:183`, `mappers.py:415`, `:448`, `:479`). An old database upgrades through the new `COLUMN_MIGRATIONS` (`migrations.py:102`), which reads `PRAGMA table_info` first (`:134-139`). It can't join `MIGRATIONS`, because `tests/integration/test_sqlite_uow.py:254` requires `IF NOT EXISTS` there.
- **The page.** `ui/src/renderer/src/features/converter/ConvertPage.tsx:195` keeps only what the user picked, null until they pick, and the dropdown shows that pick or else the setting (`:727`). `perJobGpuPreference` (`convert-commands.ts:170`) decides what Add (`ConvertPage.tsx:342`) and the command snapshot (`convert-commands.ts:198`) send: a pick goes out unless it equals a known saved setting, including Auto over a saved non-auto value. A dropdown nobody touched sends nothing.
- **Unchanged.** `packages/api/src/avkit_api/routes/conversions.py:126`, `:133` and `mcp-server/src/toolsets/convert.ts:49` already carried the value. The API response and the OpenAPI paths stay as they were, because `gpu_encoder` already shows what ran.
- **Fix generalization.** Checked 2 locations in `packages/core/src/avkit_core/services/conversion.py` (every use of `_resolve_encoder` and `_preference`, `:488` and `:402`). Fixed 1 instance (`_dispatch`, `:488`). Skipped 1 (`:402`, the fallback for a job with no choice, which 08 keeps: null means the setting read at Start). Verified 0 remaining unaddressed instances.
- **Round 2's F1.** The page used to copy the setting into its own state, and its settings effect overwrote that copy whenever settings arrived or changed. So a Software choice made before settings loaded, or before the setting changed, was lost, and the job could run on hardware. The reviewer reproduced it on the real page. D-207 takes the encoder out of that effect, so no settings timing can overwrite a pick and Add and the palette can't disagree. It also closes a third case the review didn't list: a preset clicked before settings load left the dropdown at Auto and sent an Auto nobody chose.
- **Second fix generalization (F1).** Checked the 4 values the settings effect sets on `ConvertPage.tsx`: encoder, CQ, Scale and Audio. Fixed 1 (the encoder, under Mat's "2: fix it"). Skipped 3 under D-208, which files `CONVERT-ADVANCED-EDIT-REPLACED` as low and lists it in the release notes. CQ was measured on the real page: 31 went back to 25 when settings arrived late, and became 30 when the saved default preset changed to mobile. Scale and Audio weren't measured.
- **Round 3's F1.** `useConverterSettings` copied the whole form into its draft on the first edit. With an Output folder or Skip existing edit open, a refetch that changed the saved encoder left the page comparing against the copy, so an explicit pick equal to the old setting was left out of Add and the command snapshot, and the backend followed the new setting. The reviewer reproduced it and so did I. D-212 makes the draft hold only the fields the user edited (`useConverterSettings.ts:63`), and the form is the saved values with those edits on top (`:66`). `ConvertPage.tsx` didn't change, because it never edits `gpu_preference`, so its form value is the saved one. This differs in shape from the reviewer's recommendation of a separate saved baseline: the same comparison now reads a value that follows the saved settings. It also stops Save writing a frozen encoder back over a newer one, and stops an edit made before settings load holding the defaults. The Settings page has its own instance of the hook and gets the same behaviour. The app's own Settings page can't trigger this defect, because leaving Convert unmounts the page and drops the draft. It takes an MCP client or API call changing the saved encoder, then a refetch.
- **Third fix generalization (F1 in round 3).** Checked the 2 places in `ui/src/renderer/src` where a draft falls back with `?? baseline`. Fixed 1 (`useConverterSettings.ts`). Skipped 1 (`ui/src/renderer/src/features/capture/useCaptureSettings.ts:78-83`, which has no encoder), filed low as `SETTINGS-DRAFT-STALE-BASELINE`. That one is read from the code and wasn't reproduced. Verified 0 remaining unaddressed instances.

The design decisions are D-203, D-207, D-208 and D-212, in the plan's decision block.

### What these checks don't prove

- The page's dropdown is covered by behaviour tests, not by a run of the installed window. AC-112.8's timing cases hold the settings response in jsdom, AC-112.9's open-edit cases run in jsdom as well, and the rebuilt app wasn't driven by hand. AC-112.7 sends the value to the packaged backend's API.
- Other Advanced values can still snap back when settings arrive late (`CONVERT-ADVANCED-EDIT-REPLACED`, D-208). AC-112.8 covers the encoder only.
- AC-112.7 ran on this PC, which has an NVIDIA GPU: `hevc_nvenc` for the default job and `libx265` for Software. A machine without NVENC is a question for Mat's check from the published release (D-204).

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-03-release-rc1/implementation-plan.md) §MEU-112. **Execution authorization:** `USER_EXPLICIT`, 2026-11-04, "2: fix it".

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-112.1 | unit | A Compress job added with per-job Software on an NVIDIA PC with the setting at auto runs `libx265`, in both `gpu_encoder` and the encode options' `codec`. | Spec (08 §Encoder choice per job); Local Canon `CONVERT-JOB-GPU-PREFERENCE-IGNORED` | `tests/unit/test_conversion_service.py:842` | ✅ |
| AC-112.2 | unit | A job with no per-job value uses the setting, read when the job runs. | Spec | `tests/unit/test_conversion_service.py:853` | ✅ |
| AC-112.3 | unit | A per-job Auto beats a non-auto setting and runs the recommended encoder. | Spec | `tests/unit/test_conversion_service.py:875` | ✅ |
| AC-112.4 | unit | The choice survives re-queue (`reset_failed`) and a SQLite round trip. A Cut or Extract job stores null even if the spec carries a value. | Spec | `tests/unit/test_conversion_service.py:886`, `:914`; `tests/unit/test_ffmpeg_conversion.py:1016` | ✅ |
| AC-112.5 | unit | A database with the old `conversion_jobs` table upgrades with its rows intact, the rows load with `gpu_preference` null, and a second pass changes nothing. A fresh database and an upgraded one have the same columns in the same order. | Spec; precedent `tests/e2e/test_api_downloads.py:629` | `tests/unit/test_ffmpeg_conversion.py:1074` | ✅ |
| AC-112.6 | unit | The Convert page and the command snapshot send `gpu_preference` when the dropdown differs from the saved setting, including Auto over a saved non-auto value, and omit it when they match. | Spec | `ui/tests/unit/convert-page.behavior.test.ts:260`, `:267`, `:274`, `:280` | ✅ |
| AC-112.7 | runtime | On the packaged backend, a job sent with `gpu_preference: software` runs `libx265` or `libx264`. | Spec; the observation that filed the issue | `tools/smoke_packaged_rc.py:256-266`, `:280-282`; rows 11, 12 | ✅ |
| AC-112.8 | unit | A choice made in the dropdown stays the choice when settings arrive late or change afterwards, on Add and on the palette command, and is sent when settings aren't known yet. A dropdown nobody touched follows the setting and sends nothing. | Spec; execution round 2 F1 | `ui/tests/unit/convert-page.behavior.test.ts:345`, `:354`, `:361`, `:370`, `:377`, `:387`, `:395`, `:404`, `:414` | ✅ |
| AC-112.9 | unit | An unsaved edit to the Output folder or Skip existing holds only what was edited. A dropdown nobody touched, the comparison behind what Add and the palette command send, and a Save all use the current saved values for every other field. The edit itself survives a refetch, and the Settings page's form behaves the same way. | Spec; execution round 3 F1 | `ui/tests/unit/convert-page.behavior.test.ts:443`, `:452`, `:459`, `:467`, `:478`, `:490`, `:500`, `:519`, `:526` | ✅ |
| AC-108 (cross-ref) | — | Owned by the MEU-108 handoff (the READY guard in the output handler) | plan §MEU-108 | [MEU-108 handoff](2026-11-03-release-rc1-MEU-108-handoff.md) | see MEU-108 |
| AC-109 (cross-ref) | — | Owned by the MEU-109 handoff (the output folder before FFmpeg starts) | plan §MEU-109 | [MEU-109 handoff](2026-11-03-release-rc1-MEU-109-handoff.md) | see MEU-109 |
| AC-110 (cross-ref) | — | Owned by the MEU-110 handoff (licence, version, build, packaged checks and release materials) | plan §MEU-110 | [MEU-110 handoff](2026-11-03-release-rc1-MEU-110-handoff.md) | see MEU-110 |
| AC-111 (cross-ref) | — | Owned by the MEU-111 handoff (the MCP image cap and the audit's two image steps) | plan §MEU-111 | [MEU-111 handoff](2026-11-03-release-rc1-MEU-111-handoff.md) | see MEU-111 |
| AC-24 (cross-ref) | regression | AC-24.10: the packaged backend folder holds its exe and support tree. It passed at row 0, not failed as the plan predicted, because this tree holds the gitignored outputs; it fails only in a clean clone, and CI deselects it (plan ECN-2) | plan ECN-2 | `tests/unit/test_packaging_backend.py:212` (gate `py-tests`) | ✅ |
| AC-25 (cross-ref) | regression | AC-25.7: the MCP snippet names the app-data folder, with no token or API base, fixed in `0eb59ab` before this baseline. AC-25.10: the NSIS check script exists and fails closed; same clean-clone note as AC-24.10 | plan ECN-2 | `tests/unit/test_packaging_installer.py:64`, `:94` (gate `py-tests`) | ✅ |
| AC-68 (cross-ref) | regression | AC-68.2: the audit runner imports nothing from the server's tree. H1-2 attempt 1 failed this test on row 5b's import; the [MEU-111 handoff](2026-11-03-release-rc1-MEU-111-handoff.md) holds the correction (D-189, ECN-3). The forbidden-pattern list is unchanged | plan ECN-3 | `mcp-server/tests/audit/run-cli.test.ts` (gate `mcp-tests`) | ✅ |
| AC-71 (cross-ref) | regression | AC-71.10: Electron with `ELECTRON_RUN_AS_NODE` on the dev server entry answers `initialize` as av-kit, and the fuse pin holds in `electron-builder.yml`, which row 7 edited | plan §Verification 1 | `ui/tests/unit/mcp-spawn-electron.test.ts:76` (gate `ui-tests`) | ✅ |
| AC-72 (cross-ref) | regression | AC-72.7: `THIRD_PARTY_NOTICES.md` stays hand-curated with its LGPL appendix and FFmpeg source section; it gains one pointer line to the generated list, and its `## FFmpeg` section names the re-pinned build | plan §MEU-110 | `tests/unit/test_packaging_installer.py:207` (gate `py-tests`) | ✅ |
| AC-92 (cross-ref) | regression | AC-92.4: the MCP entry runs through the app's own exe with `ELECTRON_RUN_AS_NODE`. It is the Local Canon behind AC-110.13, which row 11 proved on the RC build | plan AC-110.13 | row 11 MCP probe, in the [MEU-110 handoff](2026-11-03-release-rc1-MEU-110-handoff.md) | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-112.1 | `AssertionError: assert 'hevc_nvenc' == 'libx265'` | pass | `test_conversion_service.py:842` |
| AC-112.3 | `AssertionError: assert 'libx265' == 'hevc_nvenc'` | pass | `test_conversion_service.py:875` |
| AC-112.4 re-queue | `AttributeError: 'ConversionJob' object has no attribute 'gpu_preference'` | pass | `test_conversion_service.py:886` |
| AC-112.4 Cut, Extract | `AttributeError: 'ConversionJob' object has no attribute 'gpu_preference'` | pass | `test_conversion_service.py:914` |
| AC-112.4 SQLite | `TypeError: ConversionJob.__init__() got an unexpected keyword argument 'gpu_preference'` | pass | `test_ffmpeg_conversion.py:1016` |
| AC-112.5 | `assert ['id', 'kind'...eset_id', ...] == ['id', 'kind'...eset_id', ...]` | pass | `test_ffmpeg_conversion.py:1074` |
| AC-112.6 Auto over a saved non-auto setting | `expected { Object (paths, kind, ...) } to match object { gpu_preference: 'auto' }` | pass | `convert-page.behavior.test.ts:260` |
| AC-112.6 a choice that matches the saved setting | `expected { Object (paths, kind, ...) } to not have property "gpu_preference"` | pass | `convert-page.behavior.test.ts:274` |
| AC-112.6 the command snapshot | `expected { Object (paths, kind, ...) } to match object { gpu_preference: 'auto' }` | pass | `convert-page.behavior.test.ts:280` |
| AC-112.8 choice before settings load, on Add | `AssertionError: expected 'auto' to be 'software'` | pass | `convert-page.behavior.test.ts:345` |
| AC-112.8 choice before settings load, on the snapshot | `to match object { gpu_preference: 'software' }` | pass | `convert-page.behavior.test.ts:354` |
| AC-112.8 later change to the setting, on Add | `AssertionError: expected 'nvidia' to be 'software'` | pass | `convert-page.behavior.test.ts:361` |
| AC-112.8 later change to the setting, on the snapshot | `to match object { gpu_preference: 'software' }` | pass | `convert-page.behavior.test.ts:370` |
| AC-112.8 Auto before settings load | `AssertionError: expected 'software' to be 'auto'` | pass | `convert-page.behavior.test.ts:377` |
| AC-112.8 Add while settings load | `to match object { gpu_preference: 'auto' }` | pass | `convert-page.behavior.test.ts:387` |
| AC-112.8 preset before settings load | `AssertionError: expected 'auto' to be 'software'` | pass | `convert-page.behavior.test.ts:395` |
| AC-112.8 `perJobGpuPreference` table | `AssertionError: expected undefined to be type of 'function'` | pass | `convert-page.behavior.test.ts:414` |
| AC-112.9 Output folder edit, on Add | `expected { Object (paths, kind, ...) } to match object { gpu_preference: 'software' }` | pass | `convert-page.behavior.test.ts:443` |
| AC-112.9 Output folder edit, on the snapshot | `expected { paths: [], kind: 'compress', …(1) } to match object { gpu_preference: 'software' }` | pass | `convert-page.behavior.test.ts:452` |
| AC-112.9 Skip existing edit | `expected { Object (paths, kind, ...) } to match object { gpu_preference: 'software' }` | pass | `convert-page.behavior.test.ts:459` |
| AC-112.9 untouched dropdown | `AssertionError: expected 'software' to be 'nvidia'` | pass | `convert-page.behavior.test.ts:467` |
| AC-112.9 Save | `to match object { output_dir, gpu_preference }`: expected nvidia, received software | pass | `convert-page.behavior.test.ts:478` |
| AC-112.9 edit before settings load | `AssertionError: expected 'auto' to be 'software'` | pass | `convert-page.behavior.test.ts:490` |
| AC-112.9 Settings page | `AssertionError: expected true to be false` | pass | `convert-page.behavior.test.ts:500` |

Two tests passed at Red, and both were already true before the fix. AC-112.2 (`test_conversion_service.py:853`) holds because every job followed the setting. AC-112.6's `:262`, a choice that differs from a saved `auto`, holds because the page already sent any non-auto choice. AC-112.7 is a runtime proof with no Red. The filed issue is its failing observation. AC-112.8's Red ended with 8 failed and 1 passed, and the pass is the untouched-dropdown guard (`:404`), which holds before and after by design. A first Red run had 6 failed and 3 passed: two cases passed falsely, because assertions ran before query updates reached the page and one click hit a preset already selected. Both were corrected before the fix went in, and `red-check` had accepted both runs, so the counts were read too. AC-112.9's Red ended with 7 failed and 2 passed. The two passes are the guards (`:519`, `:526`), which hold before and after by design.

Receipts: Red `C:/Temp/av-kit/s44-112-red.txt`, `s44-112-red-ui.txt`, `s44-112-red-check.txt`; Green `s44-112-green.txt`, `s44-112-green-ui.txt`; registration `s44-112-render.txt`; under `C:/Temp/av-kit/rc1/`: `smoke-unpacked.json`, `smoke-installed.json`. AC-112.8: `s44-112-8-red.txt`, `s44-112-8-red-check.txt`, `s44-112-8-green-ui.txt`, `s44-112-8-types.txt`, `s44-112-8-lint.txt`. The reviewer's own reproduction, rerun after the fix: `C:/Temp/av-kit/rc1/r2-probe-after-fix.txt`. The CQ measurement: `C:/Temp/av-kit/rc1/sibling/result.txt`. AC-112.9: `C:/Temp/av-kit/rc1/s44-112-9-red-kept.txt`, `C:/Temp/av-kit/s44-112-9-red-check.txt`, `s44-112-9-green-ui.txt`, `s44-112-9-types.txt`, `s44-112-9-lint.txt`. Round 3's reproduction: `C:/Temp/av-kit/rc1/r3-probe-before-fix.txt` (exit 1), `r3-probe-after-fix.txt` (exit 0).

### Commands Executed

```json
{"schema_version": "evidence.v1", "check_id": "s44-112-register", "command": "pwsh -NoProfile -File row-9a.ps1 (task.md row 9a Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-112 registered in meu-status.yaml, matrix item 8.8, 08 and BUILD_PLAN, then rendered", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 9a", "output": "Drift check passed — SSOT loaded (112 MEUs, 12 phases), rendered regions match on-disk content"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-112-red", "command": "pwsh -NoProfile -File row-9b.ps1 (task.md row 9b Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-112 Red: AC-112.1 to AC-112.6 in the two Python test files and the Convert page's behaviour test, with red-check.py", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 9b", "output": "Python 7 failed, 1 passed, 40 deselected in 79.45s (0:01:19). assert 'hevc_nvenc' == 'libx265' for AC-112.1. assert 'libx265' == 'hevc_nvenc' for AC-112.3. AttributeError: 'ConversionJob' object has no attribute 'gpu_preference' for AC-112.4. TypeError: ConversionJob.__init__() got an unexpected keyword argument 'gpu_preference' for the SQLite round trip. UI 3 failed, 1 passed, 40 skipped (44). red-check: 2 receipt(s), 4 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-112-green", "command": "pwsh -NoProfile -File row-9c.ps1 (task.md row 9c Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-112 Green: the field, the column, the upgrade step, the service path and the page, with the conversion, domain, unit-of-work and API suites", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 9c", "output": "pytest 105 passed in 10.79s. Vitest Tests 44 passed (44)."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-112-8-red", "command": "pwsh -NoProfile -File row-9g.ps1 (task.md row 9g Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "AC-112.8 Red: delayed and changed settings on Add and the command snapshot, the preset case, the guard and the perJobGpuPreference table", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 9g", "output": "Tests 8 failed | 1 passed | 44 skipped (53). expected 'auto' to be 'software' for a choice before settings load. expected 'nvidia' to be 'software' for a later change. expected undefined to be type of 'function' for the table. red-check: 1 receipt(s), 1 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-112-8-green", "command": "pwsh -NoProfile -File row-9h.ps1 (task.md row 9h Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "AC-112.8 Green per D-207, with the whole UI suite (RULE-1)", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 9h", "output": "Test Files 108 passed (108). Tests 1124 passed (1124)."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-112-8-reviewer-probe", "command": null, "exit_code": null, "procedure": "Reran round 2 F1's own reproduction on the real page after the fix: hold the settings response, make the choice, read the POST body.", "observer": "claude-code-local (Claude Opus 5.5)", "cwd": "P:/av-kit", "scope": "Round 2 F1's own reproduction on the real page, rerun after the fix, from the reviewer's report", "phase": "manual", "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 9h", "output": "choice preserved true true true. All three cases POST gpu_preference software: settings arrive after the choice, the saved setting changes after the choice, and the control."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-112-9-red", "command": "pwsh -NoProfile -File row-9l.ps1 (task.md row 9l Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "AC-112.9 Red: open Output folder and Skip existing edits on Add and the command snapshot, an untouched dropdown, Save, an edit begun before settings load, the Settings page and the two guards", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 9l", "output": "Tests 7 failed | 2 passed | 53 skipped (62). expected 'software' to be 'nvidia' for the untouched dropdown. expected 'auto' to be 'software' for an edit before settings load. expected true to be false on the Settings page. red-check: 1 receipt(s), 1 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-112-9-green", "command": "pwsh -NoProfile -File row-9m.ps1 (task.md row 9m Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "AC-112.9 Green per D-212, with the whole UI suite (RULE-1), the typecheck and the lint", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 9m", "output": "Test Files 108 passed (108). Tests 1138 passed (1138). Typecheck and lint exit 0."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-112-9-reviewer-probe", "command": null, "exit_code": null, "procedure": "Ran round 3 F1's own reproduction on the real page before and after the fix: load saved Software, choose Auto then Software, edit Output folder without saving, refetch with saved Nvidia, read the POST body and the command snapshot.", "observer": "claude-code-local (Claude Opus 5.5)", "cwd": "P:/av-kit", "scope": "Round 3 F1's own reproduction on the real page, before and after the fix, from the reviewer's report", "phase": "manual", "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 9m", "output": "Before the fix the reproduction exits 1. After it, exit 0 and the last line reads: 10 actual-page cases pass; snapshot equals Add in every case. The case with an explicit Software, an open Output folder edit and a saved Nvidia refetch now sends gpu_preference software."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-112-packaged", "command": "pwsh -NoProfile -File row-11.ps1 (task.md row 11 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "AC-112.7 on the packaged win-unpacked backend, inside the MEU-110 smoke", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 9m, ECN-3, ECN-6, ECN-8, ECN-9 and ECN-10, build_inputs 08ade695aadca286cd671168389227671ec1b163d81132344d38269ab2cde573", "output": "Default job: Done, hevc_nvenc, 109239 B. Job sent with gpu_preference software: status Done, error null, encoder libx265."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-112-installed", "command": "pwsh -NoProfile -File row-12.ps1 (task.md row 12 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "AC-112.7 on the installed backend, inside the MEU-110 round trip's install-root smoke", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 9m, ECN-3, ECN-6, ECN-8, ECN-9 and ECN-10, build_inputs 08ade695aadca286cd671168389227671ec1b163d81132344d38269ab2cde573", "output": "Default job: Done, hevc_nvenc, 109239 B. Job sent with gpu_preference software: status Done, error null, encoder libx265."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-gate-h1-2-attempt1", "command": "$env:TMP='C:\\Temp\\av-kit\\rc1\\tmp'; $env:TEMP='C:\\Temp\\av-kit\\rc1\\tmp'; $env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-03-release-rc1/session-gate.ps1 *> C:/Temp/av-kit/s44-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s44-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','PRODUCT_SCOPE','build_inputs','mismatch','audit rule','session-gate:'; exit $code", "cwd": "P:/av-kit", "scope": "H1-2 attempt 1, the registered D6 gate, on the tree before the ECN-3 correction", "phase": "full", "exit_code": 1, "result": "fail", "tested_state": "24e27354e35eccc0cfa7d7e76357e673a6e38c23+ab9c5df667b9ca5ae9139129a9e0075c6b774bf96f173e13d8d9fae746342ea2", "output": "mcp-tests exit=1: 1 failed, 464 passed, tests/audit/run-cli.test.ts AC-68.2, the runner tree contains none of the forbidden imports, hit mcp-server/scripts/audit/plan.ts: src/toolsets. Every earlier step exit 0, including py-tests 1100 passed. ui-build through identity-after not_run (fail-fast).", "fresh": false}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-gate-h1-2", "command": "$env:TMP='C:\\Temp\\av-kit\\rc1\\tmp'; $env:TEMP='C:\\Temp\\av-kit\\rc1\\tmp'; $env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-03-release-rc1/session-gate.ps1 *> C:/Temp/av-kit/s44-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s44-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','PRODUCT_SCOPE','build_inputs','mismatch','audit rule','session-gate:'; exit $code", "cwd": "P:/av-kit", "scope": "H1-2 attempt 6, the registered D6 gate, whole tree after ECN-6, ECN-7, ECN-8, ECN-9, ECN-10 and the rebuild", "phase": "full", "exit_code": 0, "result": "pass", "tested_state": "24e27354e35eccc0cfa7d7e76357e673a6e38c23+025862f4f8e1a5c5b6d9023835d17014eabdac94e0785551cb7cc778a4bbd382", "output": "Every step exit 0 except mcp-audit exit 1, which audit-rule.py tolerated (rule exit 0). py-tests 1186 passed in 123.98s (0:02:03). ui-tests 108 files, 1138 passed. mcp-tests 34 files, 466 passed. ui-electron 182 passed (3.7m). mcp-audit authoritative: 98/99 pass, 0 discovery finding(s), cleanup ok, exit 1; the one failure is transcript.compile: no transcript fetched (transcripts_done 0, last_item_status Pending); live-rigging-snow_vol1.md 37 B. build_inputs 08ade695aadca286cd671168389227671ec1b163d81132344d38269ab2cde573, build record matches. task-contract 45 row(s). changed paths: 93 outside scope: [] head: 24e27354e35eccc0cfa7d7e76357e673a6e38c23 head moved (S4): False. baseline excused py [] ui []. tested_state before and after equal. session-gate: INCOMPLETE VERIFICATION: every other step exits 0, but the authoritative audit stays non-pass. Transcript is not verified end to end while YouTube blocks captions (YOUTUBE-CAPTIONS-IP-BLOCK).", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-h1-3-render", "command": "rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/drift-check.txt", "cwd": "P:/av-kit", "scope": "H1-3: rendered state regions against meu-status.yaml, after the current focus and the audit report were updated", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "24e27354e35eccc0cfa7d7e76357e673a6e38c23+025862f4f8e1a5c5b6d9023835d17014eabdac94e0785551cb7cc778a4bbd382", "output": "Drift check passed — SSOT loaded (112 MEUs, 12 phases), rendered regions match on-disk content The copied audit report holds no gmail-form address."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-h1-4-openapi", "command": "rtk proxy uv run python -c '<task.md row H1-4 compare of baseline.sha and the working file>' *> C:/Temp/av-kit/openapi-check.txt", "cwd": "P:/av-kit", "scope": "H1-4: the committed OpenAPI file against baseline.sha", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "24e27354e35eccc0cfa7d7e76357e673a6e38c23+025862f4f8e1a5c5b6d9023835d17014eabdac94e0785551cb7cc778a4bbd382", "output": "info.version: 0.1.0 -> 0.1.0rc1 components and paths unchanged: True The gate's openapi step exit 0."}
```

### Quality Gate Results

`s44-gate-h1-2` is the fresh full record, and it isn't a clean pass. Its last line is:

> session-gate: INCOMPLETE VERIFICATION: every other step exits 0, but the authoritative audit stays non-pass. Transcript is not verified end to end while YouTube blocks captions (YOUTUBE-CAPTIONS-IP-BLOCK).

The gate exits 0 because D-186 tolerates exactly one state: `transcript.compile` is the only failure, it wrote a real output file, and a direct caption fetch from this machine is blocked right now. `audit-rule.py` checked all three (rule exit 0). The audit's own verdict stays non-pass (`mcp-audit authoritative: 98/99 pass, 0 discovery finding(s), cleanup ok, exit 1`), the audit report says so, and the baseline wasn't refreshed. Transcript isn't verified end to end from this machine. That run doesn't check the content of compiled output either (plan F7).

- **Static:** `py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types`, `task-contract` (45 row(s)), `scope-paths` (93 changed paths, none outside scope, head not moved), `build-identity-selftest`, `audit-rule-selftest`, `audit-clear-selftest`: all exit 0.
- **Suites:** `py-tests` 1186 passed in 123.98s (0:02:03); `ui-tests` 108 files, 1138 passed; `mcp-tests` 34 files, 466 passed. Baseline failures excused: none.
- **Builds and state:** `mcp-build`, `ui-build`, `ui-harness-build`, `ui-picker-stub`, `openapi`, `state-render`, `build-record` (`build_inputs 08ade695aadca286cd671168389227671ec1b163d81132344d38269ab2cde573`): all exit 0.
- **Runtime:** `ui-electron` 182 passed (3.7m); `mcp-audit-clear` exit 0; `mcp-audit` 98 of 99, 0 discovery findings, cleanup ok.
- **Identity:** `tested_state` `24e27354e35eccc0cfa7d7e76357e673a6e38c23+025862f4f8e1a5c5b6d9023835d17014eabdac94e0785551cb7cc778a4bbd382`, the same before and after. Row H1-2 set `TMP` and `TEMP` under ECN-2 (D-190).
- **Attempts:** attempt 1 (`s44-gate-h1-2-attempt1`, state `…+ab9c5df6…`) failed `mcp-tests` on AC-68.2, a defect in row 5b, with 1 failed and 464 passed. Later steps didn't run. Its receipts are archived. Attempt 2 (state `…+7eba916b…`) passed on the build from before Mat's rulings (`py-tests` 1100 passed, `ui-tests` 1111 passed, `mcp-tests` 466 passed, `ui-electron` 181 passed), and ECN-6 superseded it. Attempt 3 (state `…+f52fc9d6…`) passed on the build from before round 2's findings (`py-tests` 1186 passed, `ui-tests` 1115 passed, `mcp-tests` 466 passed, `ui-electron` 181 passed), and ECN-8 superseded it. Neither has a record here, because `durable_evidence.py --require-full` accepts a passing full record only for the state under review. Attempt 4 failed `ui-electron` with 2 failed and 179 passed, AC-88.12's clipboard primer and AC-66.14's test timeout, while Mat dismissed the main-process error dialogs that ECN-9 fixes. Later steps didn't run. Its receipts are in `C:/Temp/av-kit/rc1/attempt-4/`. Attempt 5 (state `…+08022c05…`) passed on the build from before round 3's finding (`py-tests` 1186 passed, `ui-tests` 1129 passed, `mcp-tests` 466 passed, `ui-electron` 182 passed), and ECN-10 superseded it, so it has no record here for the same reason. Its receipts are in `C:/Temp/av-kit/rc1/attempt-5/`. Attempt 6 is this run, after the fix for round 3's finding and rows 10 to 13 again.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/domain/conversion.py` | modified | `ConversionJob.gpu_preference`, validated |
| `packages/core/src/avkit_core/services/conversion.py` | modified | Compress stores the choice; `_dispatch` passes it to `_resolve_encoder` |
| `packages/infrastructure/src/avkit_infra/database/models.py`, `mappers.py` | modified | The column and its round trip |
| `packages/infrastructure/src/avkit_infra/database/migrations.py` | modified | The fresh table's column and `COLUMN_MIGRATIONS` |
| `ui/src/renderer/src/features/converter/ConvertPage.tsx`, `convert-commands.ts` | modified | Keep only the user's pick; `perJobGpuPreference` decides what Add and the snapshot send. Round 3's fix didn't change these two |
| `ui/src/renderer/src/features/converter/useConverterSettings.ts` | modified | The draft holds only what was edited, and the form is the saved values with those edits on top (D-212) |
| `tools/smoke_packaged_rc.py` | new in MEU-110 | `SOFTWARE_ENCODERS`, `_run_one_job`, the second job for AC-112.7 |
| `tests/unit/test_conversion_service.py`, `tests/unit/test_ffmpeg_conversion.py`, `ui/tests/unit/convert-page.behavior.test.ts` | modified | AC-112.1 to AC-112.6, AC-112.8 and AC-112.9 |
| `docs/execution/plans/2026-11-03-release-rc1/red-check.py` | modified | `DECLARED_NEW` gains `gpu_preference` |
| `docs/build-plan/08-video-conversion.md`, `build-priority-matrix.md`, `docs/BUILD_PLAN.md`, `.agent/context/meu-status.yaml`, `meu-registry.md`, `known-issues.yaml`, `known-issues.md` | modified | §Encoder choice per job, registration and the closed issue, shared with the other four MEUs |

```diff
-        encoder = self._resolve_encoder(caps)
+        encoder = self._resolve_encoder(caps, job.gpu_preference)
```

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
| — | — | None open at approval. Findings by round are in the rolling review. | — | — | — |

### Verdict

Codex approved with no findings open and `intent_achieved: yes`, at report round 4 and ledger round 2 of 6 (dispatch `s44-exec-r4b`). The reviewer's verdict and its stated limits are in `2026-11-03-release-rc1-implementation-critical-review.md`. This line only points there.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| A real run on a machine without NVENC | out-of-scope | — | D-204: Mat waived the clean-machine step for now and runs it from the published release (checklist step 6) |
| `CONVERT-ADVANCED-EDIT-REPLACED`: CQ, Scale and Audio edits can snap back when settings arrive late | known-issue | `known-issues.yaml` | D-208: pre-dates this work, and the replaced value shows in the field; filed low, listed in the release notes |
| `SETTINGS-DRAFT-STALE-BASELINE`: an unsaved capture settings edit freezes the other capture settings | known-issue | `known-issues.yaml` | D-212: no encoder there and no job runs differently; read from the code, filed low |

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-04 | claude-code-local (Claude Opus 5.5) | Initial MEU-112 handoff after H1-2 attempt 3 |
| Amended | 2026-11-04 | claude-code-local (Claude Opus 5.5) | AC-112.8 and the fix for round 2's F1 (D-207, D-208, ECN-8); packaged proofs and gate rebound to H1-2 attempt 5 |
| Amended | 2026-11-04 | claude-code-local (Claude Opus 5.5) | AC-112.9 and the fix for round 3's F1 (D-211, D-212, ECN-10); packaged proofs and gate rebound to H1-2 attempt 6 |
