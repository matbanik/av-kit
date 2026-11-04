---
date: "2026-11-04"
project: "release-rc1"
meu: "MEU-109"
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

# Handoff: 2026-11-03-release-rc1-MEU-109-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-109, `convert-output-folder`. Convert creates a missing output folder before FFmpeg starts.
**Build Plan Section**: [08 §Output folder (residual)](../../../docs/build-plan/08-video-conversion.md#output-folder-residual).
**Predecessor**: none. The [MEU-108 handoff](2026-11-03-release-rc1-MEU-108-handoff.md), the [MEU-110 handoff](2026-11-03-release-rc1-MEU-110-handoff.md), the [MEU-111 handoff](2026-11-03-release-rc1-MEU-111-handoff.md) and the [MEU-112 handoff](2026-11-03-release-rc1-MEU-112-handoff.md) are the same plan's other MEUs.

Before this MEU, a job pointed at a folder that didn't exist ended with an FFmpeg exit code and no explanation (`CONVERT-OUTPUT-DIR-MISSING`).

- **`OUTPUT_PARENT`.** `_ensure_output_parent` in `packages/infrastructure/src/avkit_infra/media/adapter.py` creates the parent folders. `encode`, `cut` and `extract_stream` call it after `_require_ffmpeg` and before anything else spawns.
- A failed `mkdir` raises `OSError`, which the service's existing `except` around `_dispatch` reports through `_finish(job.id, ConversionStatus.Failed, error=str(exc))` (`packages/core/src/avkit_core/services/conversion.py:479`), so the user reads the path problem.
- **Fix generalization.** Checked 4 locations in `packages/infrastructure/src/avkit_infra/media/adapter.py` (every method that writes an FFmpeg output). Fixed 3 instances (`encode`, `cut`, `extract_stream`). Skipped 1 (`convert` at `:388`, spec-divergent: 08 `OUTPUT_PARENT` names only the three; its one product caller, `services/tts.py:337`, has `write_audio_wav` create the same folder first at `filesystem/writer.py:84`). Verified 0 remaining unaddressed instances.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-03-release-rc1/implementation-plan.md) §MEU-109. **Execution authorization:** `USER_EXPLICIT`, 2026-11-03, "create MIT license file / prepare whatever we need to build and publish the release rc1 candidate", and 2026-11-04, "approve tripple of the token budget and add MEU-111". Plan review approved at round 3. Mat's 2026-11-04 rulings (ECN-6) don't change this MEU's code, so only the gate record moved.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-109.1 | unit | `encode` to a path whose parent folders do not exist creates them before FFmpeg starts. | Spec (08 §Output folder) | `tests/unit/test_ffmpeg_conversion.py:897`; real FFmpeg in AC-110.12 | ✅ |
| AC-109.2 | unit | `cut` does the same. | Spec | `tests/unit/test_ffmpeg_conversion.py:916` | ✅ |
| AC-109.3 | unit | `extract_stream` does the same. | Spec | `tests/unit/test_ffmpeg_conversion.py:941` | ✅ |
| AC-109.4 | unit | An existing folder is left alone and its contents survive. | Spec | `tests/unit/test_ffmpeg_conversion.py:965` | ✅ |
| AC-109.5 | unit | When the folder cannot be created, the job ends `Failed` with an error naming the path, and FFmpeg never starts. | Spec; `conversion.py:473-479` | `tests/unit/test_ffmpeg_conversion.py:989`; `tests/unit/test_conversion_service.py:758` | ✅ |
| AC-108 (cross-ref) | — | Owned by the MEU-108 handoff (the READY guard in the output handler) | plan §MEU-108 | [MEU-108 handoff](2026-11-03-release-rc1-MEU-108-handoff.md) | see MEU-108 |
| AC-110 (cross-ref) | — | Owned by the MEU-110 handoff (licence, version, build, packaged checks and release materials) | plan §MEU-110 | [MEU-110 handoff](2026-11-03-release-rc1-MEU-110-handoff.md) | see MEU-110 |
| AC-111 (cross-ref) | — | Owned by the MEU-111 handoff (the MCP image cap and the audit's two image steps) | plan §MEU-111 | [MEU-111 handoff](2026-11-03-release-rc1-MEU-111-handoff.md) | see MEU-111 |
| AC-112 (cross-ref) | — | Owned by the MEU-112 handoff (the encoder chosen for one job) | plan §MEU-112 | [MEU-112 handoff](2026-11-03-release-rc1-MEU-112-handoff.md) | see MEU-112 |
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
| AC-109.1 | `assert [False] == [True]` | pass | `test_ffmpeg_conversion.py:897` |
| AC-109.2 | `assert [False] == [True]` | pass | `test_ffmpeg_conversion.py:916` |
| AC-109.3 | `assert [False] == [True]` | pass | `test_ffmpeg_conversion.py:941` |
| AC-109.5 | `Failed: DID NOT RAISE OSError`: nothing refused the blocked folder | pass | `test_ffmpeg_conversion.py:989` |
| AC-109.5 (service) | `assert [['C:\\Users\...ibx265', ...]] == []`: the recording `Popen` held a spawn where none was expected, so FFmpeg started | pass | `test_conversion_service.py:758` |

AC-109.4 isn't required Red: an existing folder survives before and after. Row 4's first Red was refused by `red-check.py` because a long test name broke its failure-header match; the test name was shortened and the Red rerun, with no change to what the test asserts. Real FFmpeg against a missing folder is proved by AC-110.12 in rows 11 and 12.

Receipts: Red `C:/Temp/av-kit/s44-109-red.txt`; Green `C:/Temp/av-kit/s44-109-green.txt`; `C:/Temp/av-kit/rc1/rows/row5-ruff.txt`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "check_id": "s44-109-red", "command": "pwsh -NoProfile -File row-4.ps1 (task.md row 4 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-109 Red: a recording Popen captures output.parent.is_dir() at spawn, with red-check.py", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 (baseline.sha) plus rows 1 to 4", "output": "5 failed, 1 passed, 34 deselected. assert [False] == [True] for encode, cut and extract_stream. AC-109.5 at the adapter: Failed: DID NOT RAISE OSError. AC-109.5 through the service: the recording Popen list holds a spawn where == [] was expected (ibx265', ...]] == []). red-check: 1 receipt(s), 1 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s44-109-green", "command": "pwsh -NoProfile -File row-5.ps1 (task.md row 5 Validation cell, verbatim, from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-109 Green: the shared parent-folder step, the two conversion test files and ruff", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 24e2735 plus rows 1 to 5", "output": "40 passed in 33.61s. Ruff exit 0. Expectations unchanged from Red."}
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
| `packages/infrastructure/src/avkit_infra/media/adapter.py` | modified | `_ensure_output_parent`, called by `encode`, `cut`, `extract_stream` |
| `tests/unit/test_ffmpeg_conversion.py` | modified | AC-109.1 to AC-109.5 |
| `tests/unit/test_conversion_service.py` | modified | AC-109.5 through the service |
| `docs/build-plan/08-video-conversion.md` | modified | §Output folder (residual) |

```diff
+def _ensure_output_parent(output_path: Path) -> None:
+    # FFmpeg reports a missing folder only as an exit code; a failed mkdir names the path.
+    output_path.parent.mkdir(parents=True, exist_ok=True)
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

None.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-04 | claude-code-local (Claude Opus 5.5) | Initial MEU-109 handoff after H1-2 |
| Amended | 2026-11-04 | claude-code-local (Claude Opus 5.5) | Gate rebound to H1-2 attempt 3 after Mat's rulings (ECN-6); this MEU's code didn't change |
| Amended | 2026-11-04 | claude-code-local (Claude Opus 5.5) | Gate rebound to H1-2 attempt 5 after round 2's findings and Mat's crash report (ECN-8, ECN-9); this MEU's code didn't change |
| Amended | 2026-11-04 | claude-code-local (Claude Opus 5.5) | Gate rebound to H1-2 attempt 6 after round 3's finding (ECN-10); this MEU's code didn't change |
