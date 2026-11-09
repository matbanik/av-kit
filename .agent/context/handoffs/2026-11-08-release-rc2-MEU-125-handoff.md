---
date: "2026-11-08"
project: "release-rc2"
meu: "MEU-125"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-08-release-rc2/implementation-plan.md"
build_plan_section: "bp07"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "none"
---

# Handoff: 2026-11-08-release-rc2-MEU-125-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-125 `dist-release-candidate-2` (P2; grouping D-243 makes it the last session of the RC2 triage batch). It closes no product issue. Its watch item is `E2E-TRANSCRIPT-SEAM-RELOAD-FLAKE` (MONITORING, P4, D-362).
**Build Plan Section**: [07 §Second release candidate (residual)](../../../docs/build-plan/07-distribution.md#second-release-candidate-residual) (`:371-386`). The Delivered note is at `:388-397`.
**Predecessor**: none.

Every version surface reads `0.1.0-rc.2`. The notices say the FFmpeg build carries libdvdcss and that av-kit never uses DVD input. Session 57 built the installer from a clean tree, offline and with the pinned FFmpeg, and checked it the way RC1 was checked. It also ran MEU-114's round trip on the full build and MEU-117's and MEU-121's packaged smokes on the installer's own backend. It ran a fresh gate and wrote the notes and the publish checklist. Nothing was tagged, uploaded or published.

- **Version and notices (rows 1, 2; D-461, `VERSION_ONE`, `NOTICE_LINE`).** `version-bump.py` wrote 13 files with exact counts and kept their endings:
  - `ui/package.json`, `ui/package-lock.json`, `mcp-server/package.json`, `mcp-server/package-lock.json` and `mcp-server/src/index.ts:20`;
  - the four `pyproject.toml` files and `packages/api/src/avkit_api/__init__.py`;
  - `uv.lock` (3,361 LF), `openapi.committed.json` (`info.version` only, 6,516 CRLF) and `packaging/THIRD_PARTY_NOTICES.md` (226 CRLF).

  AC-110.9's constants (`tests/unit/test_release_packaging.py:27-28`) and AC-72.7's needles (`tests/unit/test_packaging_installer.py`) moved in row 1, before the bump. The FFmpeg source archive keeps its rc.1 name, and the notices link the rc.2 tag (D-465 A).
- **Build (row 3; D-462, `CLEAN_TREE`, `FRESH_BUILD`, `BUILD_RECORD`).**
  - `build-rc.ps1` built `ui/dist/av-kit-Setup-0.1.0-rc.2.exe` offline from deleted outputs: 340,362,828 B, SHA-256 `547b1f5019e79f2b2a44fbc79aedc16c45bf26c753c1ada9845dcdd8037f74c8`.
  - The pinned FFmpeg pair is `ffmpeg.exe` `c46215f8889634396f0ac0acac738ef2145175e5b6caf28b3daa8ac9a9980c5f` and `ffprobe.exe` `b77db2dfcbf08886d6a29bc1fabdceea3dd559751b03087205e3e13ec85c3e15`, build `n8.1.3-27-g8dca1586f4-20261031`. Its archive's SHA-256 is `401dffcf14c301082e1fc03b0bc876b92ea676bfc521fc56e80a1537d137034f`.
  - The record `docs/releases/v0.1.0-rc.2-build-record.json` (`s44.build-record.v1`) binds `build_inputs` `df8c41a9079c6a8bd431e8cb5e8315b3b1d3171a7df327b1e88400ebb9c7f4d3`.
  - Its toolchain: node v26.13.0, npm 11.20.0, uv 0.12.5, Python 3.12.12, dotnet 8.0.427, Electron 42.11.18, electron-builder 26.18.0 and PyInstaller 6.22.3.
- **Packaged checks (row 4; `PACKAGED_CHECKS`).** All three ran on `win-unpacked`:
  - the release smoke passed with its negative control (`phonemizer`);
  - the MCP probe through `av-kit.exe` reported `av-kit` `0.1.0-rc.2`;
  - offline TTS from a backend copy behind dead proxies wrote 41,400 samples at 24,000 Hz.
- **Round trip (row 5; D-463, `ROUNDTRIP`, `ROUNDTRIP_SAFETY`, `INSTALLED_COPY`).** Phases A to D passed with RC1 as the old installer, and the install-root smoke and the app smoke passed at each new install.
  - After every uninstall nothing was left behind, and `%APPDATA%\av-kit-ui` and `%LOCALAPPDATA%\av-kit` kept the same entries.
  - Phase B's backend copy matched the install: 1,160 of 1,160 files and 288,682,325 of 288,682,325 B.
- **Smokes on the installed copy (rows 6, 7; `CAPABILITY_SMOKE`, `SENTENCE_SMOKE`).**
  - PyTorch FP32 was listed unavailable, and its download (409) and load (422) were refused with `files_unchanged` true.
  - ONNX INT8 generated all 149 jobs with 0 failures.
- **Documents (rows 8, 9; `RELEASE_NOTES`, `PUBLISH_CHECKLIST`).** Both are LF and hold no home path:
  - `docs/releases/v0.1.0-rc.2.md`, the notes, uses D-466's alternative, with the Transcript section reworded to the gate's facts (D-475);
  - `docs/releases/publish-checklist-v0.1.0-rc.2.md`, Mat's steps in order, keeps RC1 and marks it replaced (D-467 A).
- **Records (row 10; D-469, `GUARDED_STATUS_WRITE`).**
  - The build record was copied byte for byte.
  - The 07 Delivered note (`07-distribution.md:388-397`) was added.
  - MEU-125 was set to `ready_for_review` through `status-write.py`.
  - Grouping row 57 (`:260`) became `executed` with the plan folder.

**Where values go (Session 50 RULE-1; D-468, `NO_RAW_CONSOLE`).** No product log line, stdout line or Console field changes.
- The only product source change is the version string at `mcp-server/src/index.ts:20`. The gate's `scope-paths` step refuses any other path under `packages/`, `ui/src/` or `mcp-server/src/`.
- The plan-local scripts print names, counts, sizes and SHA-256s. The round trip's log writes `<HOME>` for the home folder in all three spellings.
- The committed build record holds relative paths only. The two documents and the record hold no `Users\` path (rows 8 to 10 check it).
- The live MCP audit's report goes to `.agent/context/MCP/mcp-tool-audit-report.md` only after a check for a personal address (H1-3).
- Session 53 RULE-1, Session 54 RULE-1 and RULE-2, and Session 55 RULE-3 have no target. No field carries outside text, no `packages/core/src` file changes, and nothing fans out.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-08-release-rc2/implementation-plan.md) §MEU-125.
**Plan gate:** `USER_EXPLICIT`, 2026-11-09, "all recommendations accpeted proceed". This answered the Decision Briefs for D-464 to D-467, after the Codex plan review approved in round 3 of the ledger loop `s57-plan-2026-11-08-release-rc2` ([plan-critical-review.md](2026-11-08-release-rc2-plan-critical-review.md)).
**Execution budget:** 60,000,000 tokens, Mat's "Add 60M to the plan loop so round 2 can run, and set execution to 60M." (`plan_to_exec_gate: human`).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-125.1 | unit | AC-110.9's seven version tests pass with `RC_NPM = "0.1.0-rc.2"` and `RC_PY = "0.1.0rc2"`, and `tests/e2e/test_api_openapi.py:110` passes | Human-approved: triage batching, 07 `:379`; Local Canon: AC-110.9 | `tests/unit/test_release_packaging.py:159`, `:169`, `:176`, `:186`, `:194`, `:206`, `:212`; row 1 Red (7 fail), row 2 Green; gate `py-tests` | ✅ |
| AC-125.2 | unit | AC-72.7's FFmpeg needles hold the rc.2 tag URL, `"libdvdcss"` and `"av-kit never uses DVD input"`, and still the rc.1 archive name | Human-approved: D-275, 07 `:384`; D-465 | `tests/unit/test_packaging_installer.py::test_ac_72_7_third_party_notices`; row 1 Red, row 2 Green | ✅ |
| AC-125.3 | unit, guard | AC-110.20 and AC-110.21 pass unchanged: the notice states the pin as one fact, and the fetch tool's pinned URL and SHA-256 are unchanged | Human-approved: D-266, 07 `:381` | row 1 guard run (76 passed), row 2 Green; H1-4 pin tools unchanged | ✅ |
| AC-125.4 | static | `version-bump.py --check`, `uv lock --check --offline` and `export_openapi.py --check openapi.committed.json` exit 0 | Local Canon: AC-110.9; Session 52 RULE-2 | row 2 (`--check` 0 problems; 146 packages resolved; OpenAPI check exit 0); gate `openapi`; H1-4 | ✅ |
| AC-125.5 | plan-local script | `CLEAN_TREE`: `clean-tree.py` exits 0 at row 3 before the build deletes anything; its selftest passes | Human-approved: Mat's brief; 07 `:382`; S10 B (D-471) | row 3: selftest 19 of 19 (15 planned plus 4 for `--leave-out`), the ruled check exit 0 | ✅ |
| AC-125.6 | build | `FRESH_BUILD`: `build-rc.ps1` exits 0 with the real backend, from deleted outputs, and the installer is under 500,000,000 B (AC-110.10) | Local Canon: 07 §Release candidate packaging, AC-110.10 | row 3: exit 0, 340,362,828 B | ✅ |
| AC-125.7 | build | `BUILD_RECORD`: the record is written with `--expect-inputs`, `--verify-record` passes at row 3 and in the gate, and the `build-identity.py` selftest passes (AC-110.19) | Local Canon: AC-110.19; S8 | row 3 "build record: matches"; row 10 committed copy matches; gate `build-record`, `build-identity-selftest` | ✅ |
| AC-125.8 | packaged | `smoke_packaged_rc.py` passes on `win-unpacked` with the negative control, and AC-110.1 to AC-110.8 and AC-110.18 pass in the gate's Python suite | Local Canon: `LICENCE_LIST`, AC-110.1 to AC-110.18 | row 4 PASS, negative control `phonemizer`; gate `py-tests` | ✅ |
| AC-125.9 | packaged | The MCP probe through `av-kit.exe` reports `"name":"av-kit","version":"0.1.0-rc.2"` (AC-110.13) | Local Canon: AC-110.13 | row 4 `mcp-probe.json` passed | ✅ |
| AC-125.10 | packaged | The offline TTS phase passes on a copy of `win-unpacked`'s backend behind dead proxies (AC-110.14) | Local Canon: AC-110.14; D-88 | row 4 `tts-offline.json` PASS | ✅ |
| AC-125.11 | packaged | `ROUNDTRIP`: `install-roundtrip.ps1` exits 0 through phases A to D (AC-114.5 to AC-114.9), with the install-root smoke and the app smoke passing at each new install (AC-110.15) | Human-approved: 07 `:382`; Local Canon: D-268, AC-114.5 to AC-114.9 | row 5 exit 0 | ✅ |
| AC-125.12 | plan-local script | `ROUNDTRIP_SAFETY` preconditions: exit 40 for an `-OutDir` outside the session's scratch folder, a missing input, a running `av-kit` or files in either default install folder; exit 41 when the installer isn't the record's; `-PreconditionsOnly` installs nothing | Human-approved: Mat's brief; Session 56 RULE-3 | plan-time refusals; row 5 `-PreconditionsOnly` clear | ✅ |
| AC-125.13 | plan-local script | `ROUNDTRIP_SAFETY` process stops: only processes under the install location are stopped, none by name | Human-approved: Mat's brief; memory rule on worktree-scoped kills | `install-roundtrip.ps1` `Stop-InstalledProcesses` filters by `.Path`; row 5: 0 processes under the install folder at each uninstall | ✅ |
| AC-125.14 | plan-local script | `ROUNDTRIP_SAFETY` app data: no `--delete-app-data`; `%APPDATA%\av-kit-ui` and `%LOCALAPPDATA%\av-kit` keep the same entry names across every phase; launches use throwaway `AVKIT_APP_DATA` | Local Canon: AC-114.7; D-268 | row 5 S6 lines for A, B, C and D | ✅ |
| AC-125.15 | plan-local script | `ROUNDTRIP_SAFETY` updater cache: `%LOCALAPPDATA%\av-kit-ui-updater` is deleted only when it was absent or held only RC1's copy | Local Canon: Session 49's round trip | row 5: absent before; B's install overwrote RC1's leftover copy and B's uninstall removed it; the script deleted nothing itself; absent after | ✅ |
| AC-125.16 | packaged | `INSTALLED_COPY`: the copy equals the install in file count, total bytes and `avkit-backend.exe`'s SHA-256 | Local Canon: D-315, D-332 | row 5: 1,160 of 1,160 files, 288,682,325 of 288,682,325 B | ✅ |
| AC-125.17 | packaged | `CAPABILITY_SMOKE` passes on `INSTALLED_COPY` from an absent models folder, which afterwards holds only the smoke's stub and `config.json`, with `files_unchanged` true (AC-117.15) | Human-approved: 07 `:382`; S16 A (D-473); Local Canon: AC-117.15 | row 6 PASS; post-check `config.json, kokoro-v1_0.pth` | ✅ |
| AC-125.18 | packaged | `SENTENCE_SMOKE` passes all 149 jobs on `INSTALLED_COPY` (AC-121.8) | Human-approved: 07 `:382`; Local Canon: AC-121.8 | row 7 PASS, 149 jobs, 0 failures | ✅ |
| AC-125.19 | gate | The gate's last line is `session-gate: all steps exit 0`, or `session-gate: INCOMPLETE VERIFICATION` only by `AUDIT_RULE`; the `audit-rule.py` (46 of 46) and `audit-clear.ps1` (8 of 8) selftests pass | Human-approved: D-464; Local Canon: 07 `:382` | `s57-gate-h1-2`: `session-gate: all steps exit 0`; audit-rule 46 of 46, audit-clear 8 of 8 | ✅ |
| AC-125.20 | document | `RELEASE_NOTES` holds each part of §The documents, the archive's size and SHA-256 (AC-110.22) and the caption block (AC-110.16), and no home path | Human-approved: D-216, D-466, 07 `:383` | row 8 check (missing [], forbidden [], CR 0), rerun after the gate's line | ✅ |
| AC-125.21 | document | `PUBLISH_CHECKLIST` holds the steps in order with exact commands, attaches the source archive, checks `%USERPROFILE%\.avkit\models` and writes D-467's choice for RC1 | Human-approved: D-266, D-101, D-467, 07 `:385` | row 9 check (missing [], forbidden [], CR 0) | ✅ |
| AC-125.22 | plan-local script | `GUARDED_STATUS_WRITE` for row 10 and H2-2 | Local Canon: Session 56 AC-126.10; Session 55 RULE-2 | row 0 selftest 0 failures; row 10 0 problems; H1-3 `--verify MEU-125=ready_for_review` | ✅ |
| AC-125.23 | static | `NO_RAW_CONSOLE`: no file under `packages/`, `ui/src/` or `mcp-server/src/` changes except `mcp-server/src/index.ts:20`'s version, and no new committed file holds the home folder | Local Canon: Session 50 RULE-1 | gate `scope-paths` (outside scope []); rows 8 to 10 `Users\` checks | ✅ |
| AC-125.24 | static | `NOTHING_PUBLISHED`: `git tag --list v0.1.0-rc.2` prints nothing at H1-3 and H2-5, and no row tags, pushes or runs `gh release` | Local Canon: PROFILE E5; 07 `:386` | H1-3 (0 tags); review | ✅ |
| AC-72.7 (cited) | unit | The third-party notices name each bundled component's licence and the FFmpeg source; now with the rc.2 tag link and the libdvdcss line | Local Canon: MEU-72; D-275 | `tests/unit/test_packaging_installer.py::test_ac_72_7_third_party_notices`; row 1 Red, row 2 Green | ✅ |
| AC-110.1 to AC-110.22 (cited) | unit, packaged | MEU-110's release-candidate contract on this build: the licence list and smoke (AC-110.1 to AC-110.8, AC-110.11, AC-110.12, AC-110.17, AC-110.18), the version (AC-110.9), the size limit (AC-110.10), the MCP probe (AC-110.13), offline TTS (AC-110.14), the app smoke (AC-110.15), the caption block (AC-110.16), the build record (AC-110.19), the pin (AC-110.20, AC-110.21) and the archive line (AC-110.22) | Local Canon: 07 §Release candidate packaging | gate `py-tests` (1357 passed); rows 3, 4, 5, 8 | ✅ |
| AC-114.5 to AC-114.9 (cited) | packaged | MEU-114's installer-copy round trip on a full build: RC1's uninstall leaves its copy (A), this build's removes it on its own (B), over RC1 (C) and over itself (D), and the app data stays | Local Canon: D-268 | row 5: AC-114.5 A, AC-114.6 B, AC-114.8 C and AC-114.9 D lines; S6 for each phase (AC-114.7) | ✅ |
| AC-117.15 (cited) | packaged | The capability smoke refuses a PyTorch download and load on the packaged backend and leaves the models folder unchanged | Local Canon: MEU-117 | row 6 | ✅ |
| AC-121.8 (cited) | packaged | The 149-job sentence smoke passes on the packaged backend with real audio | Local Canon: MEU-121 | row 7 | ✅ |
| AC-51.6, AC-81.13 (cross-ref) | regression | `ui/tests/e2e/test-ids.ts` is unchanged (scope-paths refuses it), so the byte-hash tests pass | plan §Files Modified | gate `scope-paths`, `ui-tests` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-125.1 (seven AC-110.9 tests) | `{'mcp-server/package.json': '0.1.0-rc.1'} != {'mcp-server/package.json': '0.1.0-rc.2'}`; `assert '0.1.0rc1' == '0.1.0rc2'`; the MCP entry lacks `{ name: "av-kit", version: "0.1.0-rc.2" }` | Row 2: 256 passed | `test_release_packaging.py:159-212` |
| AC-125.2, AC-72.7 | `AssertionError: https://github.com/matbanik/av-kit/releases/tag/v0.1.0-rc.2` not in the FFmpeg section | Row 2: pass | `test_packaging_installer.py::test_ac_72_7_third_party_notices` |
| AC-125.3 | Guard: AC-110.20 and AC-110.21 pass in Red by design | Row 2: pass | row 1's guard run, 76 passed |

- **Row 1 Red:** 8 failed and 12 passed (20). The seven AC-110.9 tests and AC-72.7 failed by assertion. `red-check.py` required all 8 and found 0 problems, and the guard run passed 76 with 2 deselected.
- **Row 2 Green:** `version-bump.py` wrote 13 files with 0 problems. `uv lock` resolved 146 packages; `uv sync --frozen --offline` moved the four avkit packages to `0.1.0rc2`; `version-bump.py --check` found 0 problems; every reader of the version and the notices passed 256 tests; the OpenAPI check exited 0.
- **Rows 3 to 10:** see the records below.

Receipts are named `s57-*` under the session's receipts folder. The ones that back the records are:
- row 0: `s57-baseline.txt`;
- row 1: `s57-red.txt`, `s57-red-check.txt` and `s57-red-guard.txt`;
- row 2: `s57-bump.txt` and `s57-green-*.txt`;
- row 3: `s57-clean-tree-selftest.txt`, `s57-clean-tree-b.txt`, `s57/offline-probe.txt`, `s57/build-attempt1-s13.txt`, `s57-electron-sums-check.txt`, `s57-electron-sums-seed.txt` and `s57/row3-run.txt`;
- row 4: `s57/row4-run.txt`, `s57/smoke-unpacked.json`, `s57/mcp-probe.json` and `s57/tts-offline.json`;
- row 5: `s57/roundtrip-preconditions.txt`, `s57/roundtrip.txt` and `s57/row5-run.txt`;
- row 6: `s57/capability.json`, `s57/capability-postcheck.txt`, `s57-r6-postcheck-r2.txt` and `s57-r6-task-lint.txt`;
- row 7: `s57/sentences.json` and `s57/row7-run.txt`;
- rows 8 and 9: `s57-notes-check.txt` and `s57-checklist-check.txt`;
- row 10: `s57-r10-*.txt`;
- the gate: `s57-gate-h1.txt` and `s57-D6-step.txt` for each step, with the earlier runs in `s57/gate-run-0-task-contract/`, `s57/gate-run-1-f2-held/`, `s57/gate-run-2-pre-notes/`, `s57/gate-run-3-pre-d475/` and `s57/gate-run-4-pre-f1/`;
- H1-3 and H1-4: `s57-h1-status-verify.txt`, `drift-check.txt` and `s57-scope-check.txt`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s57-0-baseline", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-08-release-rc2/baseline.ps1 *> C:/Temp/av-kit/s57-baseline.txt (task.md row 0's Validation cell, run from P:/av-kit)", "scope": "Row 0: baseline.sha, baseline-dirty.txt, the offline locked installs, the pinned FFmpeg pair, the base Python, UI and MCP suites, and the red-check, identity, build-identity, audit-rule, audit-clear and status-write selftests", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 8bcb4a6 (baseline.sha), before row 0", "output": "baseline-dirty.txt 27 paths; baseline.sha 8bcb4a68e796f5b340b20eae41b7ad8c71e1fab9; uv sync checked 122 packages; ui lock sync 651 locked, 0 differ; mcp-server lock sync 133 locked, 0 differ; ffmpeg.exe 165577728 B: n8.1.3-27-g8dca1586f4-20261031; red-check selftest 38 fixtures (12 positive, 26 negative), 0 wrong; identity selftest 0 failures; build-identity selftest passed; audit-rule selftest 46 of 46; audit-clear selftest 8 of 8; status-write selftest 0 failures; base py 1357 passed; base ui 1183 passed in 113 files; base mcp 470 passed in 35 files; baseline: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s57-125-red", "command": "rtk proxy uv run pytest tests/unit/test_release_packaging.py tests/unit/test_packaging_installer.py *> C:/Temp/av-kit/s57-red.txt; red-check.py with the eight required tests *> C:/Temp/av-kit/s57-red-check.txt; the guard run *> C:/Temp/av-kit/s57-red-guard.txt (task.md row 1's Validation cell, abridged, run from P:/av-kit through an extracted .ps1)", "scope": "MEU-125 Red: AC-110.9's seven version tests with RC_NPM 0.1.0-rc.2 and RC_PY 0.1.0rc2, and AC-72.7's new needles, against the rc.1 tree; AC-110.20 and AC-110.21 as guards", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 8bcb4a6 plus rows 0 and 1", "output": "8 failed, 12 passed. FAILED test_npm_manifests_carry_version, test_npm_locks_carry_version, test_mcp_server_reports_version, test_python_manifests_carry_version, test_api_package_carries_version, test_uv_lock_carries_version, test_openapi_carries_version [AC-110.9], test_ac_72_7_third_party_notices. Decisive: {'mcp-server/package.json': '0.1.0-rc.1'} != {'mcp-server/package.json': '0.1.0-rc.2'}; assert '0.1.0rc1' == '0.1.0rc2'; AssertionError: https://github.com/matbanik/av-kit/releases/tag/v0.1.0-rc.2. red-check: 1 receipt(s), 8 required test(s), 0 problem(s). Guard run: 76 passed, 2 deselected. The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s57-125-green", "command": "rtk proxy uv run python docs/execution/plans/2026-11-08-release-rc2/version-bump.py --apply *> C:/Temp/av-kit/s57-bump.txt; then task.md row 2's Validation cell: uv lock --check --offline, uv sync --frozen --offline, version-bump.py --check, the version and notices readers, and export_openapi.py --check into C:/Temp/av-kit/s57-green-*.txt (abridged, run from P:/av-kit through an extracted .ps1)", "scope": "MEU-125 Green: VERSION_ONE and NOTICE_LINE on 13 files with exact counts and endings, the lock, the sync, the check that allows only the archive's rc.1 name, every reader of the version and notices (Session 55 RULE-1) and the OpenAPI guard", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 8bcb4a6 plus rows 0 to 2", "output": "version-bump: 13 files written, 0 problems after; uv.lock CRLF=0 LF=3361 sha256=4e704a1bd7bf717906e7d601b14d900e8ac2a2866ae45877be21b8891ed01e69; openapi.committed.json CRLF=6516; THIRD_PARTY_NOTICES.md CRLF=226 sha256=1c1b6b246b570b1748a3b32ff98614019b7f2bb4b22fc431dd7e0dbfadaa0f3e. Resolved 146 packages. avkit-infra==0.1.0rc1 -> 0.1.0rc2 (and core, api, root). version-bump --check: 0 problems. 256 passed. OpenAPI check exit 0."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s57-3-build", "command": "task.md row 3's Validation cell, run from P:/av-kit through an extracted .ps1: clean-tree.py --selftest; clean-tree.py with the nine --leave-out paths of Mat's S10 B *> C:/Temp/av-kit/s57-clean-tree-b.txt; offline-probe.ps1; build-rc.ps1; build-identity.py --verify-record C:/Temp/av-kit/s57/build-record.json *> C:/Temp/av-kit/s57/row3-run.txt", "scope": "Row 3: CLEAN_TREE before anything is deleted, the offline guard, FRESH_BUILD with the real backend from deleted outputs, and BUILD_RECORD written with --expect-inputs and verified", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 8bcb4a6 plus rows 0 to 3", "output": "clean-tree selftest 19 of 19; clean-tree: clean with 9 paths left out by ruling; offline-probe 7 of 7; electron-builder exit 0; installer av-kit-Setup-0.1.0-rc.2.exe 340362828 B (limit 500000000), sha256 547b1f5019e79f2b2a44fbc79aedc16c45bf26c753c1ada9845dcdd8037f74c8; ffmpeg archive_sha256 401dffcf14c301082e1fc03b0bc876b92ea676bfc521fc56e80a1537d137034f; ffmpeg_sha256 c46215f8889634396f0ac0acac738ef2145175e5b6caf28b3daa8ac9a9980c5f; ffprobe_sha256 b77db2dfcbf08886d6a29bc1fabdceea3dd559751b03087205e3e13ec85c3e15; build_inputs df8c41a9079c6a8bd431e8cb5e8315b3b1d3171a7df327b1e88400ebb9c7f4d3; build record: matches; row3 exit 0. The first attempt stopped at S13 before electron-builder ran; see Execution notes."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s57-4-packaged", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-08-release-rc2/packaged-probes.ps1 (task.md row 4's Validation cell, run from P:/av-kit through an extracted .ps1) *> C:/Temp/av-kit/s57/row4-run.txt", "scope": "Row 4: PACKAGED_CHECKS on win-unpacked: smoke_packaged_rc.py with the negative control, the MCP probe through av-kit.exe, and offline TTS on a backend copy behind dead proxies", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 8bcb4a6 plus rows 0 to 4", "output": "PASS: smoke_packaged_rc; negative_control [\"phonemizer\"]; conversion Done (default hevc_nvenc; Software libx265). mcp-probe: serverInfo name av-kit, version 0.1.0-rc.2, passed true. tts-offline: PASS offline, wav 41400 samples at 24000 Hz. row4 exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s57-5-roundtrip", "command": "$env:ELECTRON_RUN_AS_NODE=$null; install-roundtrip.ps1 -PreconditionsOnly *> C:/Temp/av-kit/s57/roundtrip-preconditions.txt; then install-roundtrip.ps1 with RC1's and this build's installers and records *> C:/Temp/av-kit/s57/roundtrip.txt (task.md row 5's Validation cell, abridged, run from P:/av-kit through an extracted .ps1)", "scope": "Row 5: ROUNDTRIP phases A to D (AC-114.5 to AC-114.9) on the full build, ROUNDTRIP_SAFETY's preconditions, process stops, app data and updater cache, and INSTALLED_COPY for rows 6 and 7", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 8bcb4a6 plus rows 0 to 5", "output": "Preconditions: S5 clear, record match, nothing installed. pre-state: <HOME>\\AppData\\Local\\av-kit-ui-updater is absent. A: RC1 install exit 0, copy present sha256 beabc509...; uninstall exit 0; S6 (A) nothing left behind, app data same entries; AC-114.5 A: RC1's uninstall left the copy. B: install exit 0, copy sha256 547b1f50...; install-root smoke PASS; backend copy 1160 of 1160 files, 288682325 of 288682325 B; app smoke PASS; uninstall exit 0; S6 (B); AC-114.6 B: the copy and its folder are gone. C: RC1 then this build, app smoke PASS, S6 (C), AC-114.8 C gone. D: this build twice, app smoke PASS, S6 (D), AC-114.9 D gone. Processes under the install folder at each uninstall: 0. install-roundtrip: exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s57-6-capability", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy uv run --frozen python tools/smoke_packaged_tts.py --phase capability --backend-dir C:/Temp/av-kit/s57/installed-backend/avkit-backend --models-dir C:/Temp/av-kit/s57/capability-models --out C:/Temp/av-kit/s57/capability.json, then the post-run folder check (task.md row 6's Validation cell as corrected under S16 A, run from P:/av-kit through an extracted .ps1)", "scope": "Row 6: CAPABILITY_SMOKE on INSTALLED_COPY from an absent models folder (AC-117.15)", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 8bcb4a6 plus rows 0 to 6", "output": "PASS. kokoro-pt-fp32 available false. download_refused: 409 ConflictError 'This build can't run PyTorch models. Choose an ONNX model.', files_unchanged true. load_refused: 422 ModelLoadError, stub_bytes 16. Both refusals logged. capability-models after: config.json, kokoro-v1_0.pth; files_unchanged: True; exit=0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s57-7-sentences", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy uv run --frozen python tools/smoke_packaged_tts.py --phase sentences on the installed copy with a fresh copy of the smoke models --out C:/Temp/av-kit/s57/sentences.json (task.md row 7's Validation cell, abridged, run from P:/av-kit through an extracted .ps1) *> C:/Temp/av-kit/s57/row7-run.txt", "scope": "Row 7: SENTENCE_SMOKE on INSTALLED_COPY (AC-121.8)", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 8bcb4a6 plus rows 0 to 7", "output": "PASS: 149 jobs on kokoro-onnx-int8, 0 failures, each WAV's payload checked"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s57-9-checklist", "command": "task.md row 9's Validation cell, run from P:/av-kit through an extracted .ps1 *> C:/Temp/av-kit/s57-checklist-check.txt, rerun after D-475's rewording and again after the execution review's F1", "scope": "Row 9: PUBLISH_CHECKLIST: the needed commands and names (the record check, the draft prerelease, the installer, the source archive, %USERPROFILE%\\.avkit\\models, v0.1.0-rc.1, D-467, D-101, YOUTUBE-CAPTIONS-IP-BLOCK), no home path, no %LOCALAPPDATA%\\av-kit\\models, LF only", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 8ce8b95 plus rows 0 to 10, the notes' gate line, D-475's rewording and F1's step 6", "output": "missing: [] forbidden: [] CR: 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s57-10-records", "command": "rtk proxy uv run python docs/execution/plans/2026-11-08-release-rc2/status-write.py --row MEU-125 --status ready_for_review --plan docs/execution/plans/2026-11-08-release-rc2/ --keep C:/Temp/av-kit/s57/before-r10 --diff-out C:/Temp/av-kit/s57-r10-peer-diff.txt *> C:/Temp/av-kit/s57-r10-status-write.txt; then task.md row 10's Validation cell into C:/Temp/av-kit/s57-r10-records.txt, s57-r10-record-check.txt and s57-r10-render.txt (run from P:/av-kit through an extracted .ps1)", "scope": "Row 10: the committed build record, the 07 Delivered note, MEU-125 ready_for_review under GUARDED_STATUS_WRITE (AC-125.22), the render, and grouping row 57", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 8ce8b95 plus rows 0 to 10", "output": "status-write: 0 problem(s); MEU-125 -> ready_for_review; render line disclosed: BUILD_PLAN.md Total 118 + 1🚫 -> 118 + 1🟡 + 1🚫. record equal: True; grouping row 57: | 57 | `release-rc2` | MEU-125 | P2 | executed | `docs/execution/plans/2026-11-08-release-rc2/` |; 07 note: True. build_inputs df8c41a9079c6a8bd431e8cb5e8315b3b1d3171a7df327b1e88400ebb9c7f4d3; build record: matches docs/releases/v0.1.0-rc.2-build-record.json. Drift check passed (132 MEUs, 12 phases)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s57-8-notes", "command": "task.md row 8's Validation cell with D-466's alternative, run from P:/av-kit through an extracted .ps1 *> C:/Temp/av-kit/s57-notes-check.txt, rerun after the notes took the gate's line and again after D-475's rewording", "scope": "Row 8: RELEASE_NOTES holds the version, YOUTUBE-CAPTIONS-IP-BLOCK, libdvdcss, the source archive's name, size and SHA-256, %USERPROFILE%\\.avkit\\models, unsigned, another network and the installer's SHA-256 from the build record; no home path, no %LOCALAPPDATA%\\av-kit\\models and, under D-466's alternative, no 'not your copy of av-kit'; LF only", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 8ce8b95 plus rows 0 to 10, the notes' gate line and D-475's rewording", "output": "D-466: alternative missing: [] forbidden: [] CR: 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s57-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-08-release-rc2/session-gate.ps1 *> C:/Temp/av-kit/s57-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s57-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','mismatch','audit-rule','session-gate:'; exit $code", "scope": "H1-2: the registered D6 gate on the whole tree after the notes took the gate's line, D-475's rewording and F1's step 6: identity, every static check, the task contract, scope-paths with the ruled commits, the red-check, build-identity, audit-rule and audit-clear selftests, the three full suites, the MCP, UI, harness and picker-stub builds, OpenAPI, both renders, the build record, the full Electron E2E (W2-4 among them), the live MCP audit under AUDIT_RULE, then the identity again", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "8ce8b956067b7edc034818d081bbf678460f1ef6+b62b8a982c40295c45173b435cac4401caeea0b0ca9f7bf345e31aba7358dadc", "output": "identity-before exit=0; py-types exit=0 (0 errors, 0 warnings); py-lint exit=0 (All checks passed!); ui-types exit=0; ui-lint exit=0 (eslint --max-warnings 0); mcp-types exit=0; task-contract exit=0 (28 rows, 26 fully checked, 2 view_file exempt: H1-5, H2-1); scope-paths exit=0 (ruled commit 8ce8b95 10 paths and cbc6e22 1 path, none outside docs/.agent or in this plan; commits since baseline 2, all ruled, baseline is ancestor; changed paths 48, outside scope [], head moved (S3) False); red-check-selftest exit=0 (38 fixtures, 0 wrong); build-identity-selftest exit=0 (passed); audit-rule-selftest exit=0 (46 of 46); audit-clear-selftest exit=0 (8 of 8); py-tests exit=0 (1357 passed); ui-tests exit=0 (113 files, 1183 passed); mcp-build exit=0; mcp-tests exit=0 (35 files, 470 passed); ui-build exit=0; ui-harness-build exit=0; ui-picker-stub exit=0; openapi exit=0; state-render exit=0 (132 MEUs, 12 phases); issues-render exit=0 (known-issues.md up to date); build-record exit=0 (build_inputs df8c41a9079c6a8bd431e8cb5e8315b3b1d3171a7df327b1e88400ebb9c7f4d3, build record: matches); ui-electron exit=0 (190 passed, W2-4 transcript-queue.test.ts:270 ok); mcp-audit-clear exit=0 (clear); mcp-audit exit=0 (authoritative: 99/99 pass, 0 discovery findings, cleanup ok); identity-npm exit=0 (@playwright/test 1.64.1, electron 42.11.18); identity-after exit=0; ffmpeg_sha256 c46215f8889634396f0ac0acac738ef2145175e5b6caf28b3daa8ac9a9980c5f; ffprobe_sha256 b77db2dfcbf08886d6a29bc1fabdceea3dd559751b03087205e3e13ec85c3e15; uv_lock_sha256 4e704a1bd7bf717906e7d601b14d900e8ac2a2866ae45877be21b8891ed01e69; ui_package_lock_sha256 144a6bfc93707197afc77bffd27a7f283c875d1be0f9038cc5ad16a8ee59ea48; tested_state before and after equal; session-gate: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s57-h1-3-ssot", "command": "task.md H1-3's Validation cell, run from P:/av-kit through an extracted .ps1: Copy-Item C:/Temp/av-kit/s57-D6-mcp-audit/mcp-tool-audit-report.md .agent/context/MCP/mcp-tool-audit-report.md; the @gmail refusal; status-write.py --verify MEU-125=ready_for_review *> C:/Temp/av-kit/s57-h1-status-verify.txt; meu_status.py render --check *> C:/Temp/av-kit/drift-check.txt; git tag --list v0.1.0-rc.2", "scope": "H1-3: the gate's audit report copied with no personal address, MEU-125 still ready_for_review (S15), the render, and NOTHING_PUBLISHED's tag check", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "8ce8b956067b7edc034818d081bbf678460f1ef6+b62b8a982c40295c45173b435cac4401caeea0b0ca9f7bf345e31aba7358dadc (the report and the current focus are not gated inputs)", "output": "MEU-125 status ready_for_review; expected ready_for_review; renders in step: True; status-write --verify: ok; Drift check passed (132 MEUs, 12 phases); tags named v0.1.0-rc.2: 0. The copied report reads Backend version 0.1.0rc2, Commit 8ce8b95, Exit code 0, Totals 99 pass of 99, LF as committed, 0 home-path or @gmail matches"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s57-h1-4-scope", "command": "task.md H1-4's Validation cell, run from P:/av-kit through an extracted .ps1 *> C:/Temp/av-kit/s57-scope-check.txt", "scope": "H1-4: openapi.committed.json changed only info.version since baseline.sha, and the FFmpeg pin tools are unchanged (S2)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "8ce8b956067b7edc034818d081bbf678460f1ef6+b62b8a982c40295c45173b435cac4401caeea0b0ca9f7bf345e31aba7358dadc", "output": "info.version: 0.1.0rc1 -> 0.1.0rc2 components and paths unchanged: True pin tools unchanged: True"}
```

### Quality Gate Results

`s57-gate-h1-2` (H1-2) is the fresh full record, and its last line is:

> session-gate: all steps exit 0

- **Static:** pyright 0 errors; ruff check passed; the UI and MCP typechecks and ESLint (`--max-warnings 0`) passed; lint_task_contract passed on 28 rows (26 fully checked, 2 `view_file` exempt); scope-paths found 48 changed paths, none outside scope and `ui/tests/e2e/test-ids.ts` unchanged, and accepted HEAD `8ce8b95` because both commits since `baseline.sha` are ruled (D-474) and touch only `docs/` or `.agent/` paths outside this plan.
- **Selftests:** red-check 38 fixtures with 0 wrong; build-identity passed; `audit-rule.py` 46 of 46; `audit-clear.ps1` 8 of 8.
- **Suites:** pytest 1357 passed, Vitest 1183 passed in 113 files and the MCP tests 470 passed in 35 files, each equal to row 0's baseline: no test was added, and the moved constants and needles are inside existing tests.
- **Build and state:** the MCP, UI, harness and picker-stub builds and the OpenAPI check exited 0; the state render (132 MEUs, 12 phases) and the issue render match the files on disk; the build record still matches the tree (`build_inputs df8c41a9…`), so rows 3 to 7 stand (S8).
- **Runtime:** the full Electron E2E passed 190 of 190. The watch item W2-4 (`ui/tests/e2e/transcript-queue.test.ts:270`, whose seam reload is the plan's `:177`) passed on every run that reached it, so D-470's rerun and S11 never applied. The live audit passed 99 of 99 with no discovery finding and cleanup ok, so `AUDIT_RULE` excused nothing.
- **Identity:** the tested_state was the same before and after the gate: `8ce8b956067b7edc034818d081bbf678460f1ef6+b62b8a982c40295c45173b435cac4401caeea0b0ca9f7bf345e31aba7358dadc`. The FFmpeg pair, `uv.lock` and `ui/package-lock.json` hashes match row 0's and row 3's.
- **Six runs.** Run 1 stopped at `task-contract`, run 2 at AC-81.11 while another program held F2, run 3 passed every step on the notes before their gate line, run 4 passed every step on the finished notes, run 5 passed every step after D-475's rewording, and run 6, this record, passed every step after F1's step 6 fix, each with the same counts. The changed-path count rose from 45 to 47 at run 5 (H1-3 wrote `.agent/context/MCP/mcp-tool-audit-report.md` and `.agent/context/current-focus.md` after run 4) and to 48 at run 6 (the canonical execution review), and none of the three is a gated input. See Execution notes.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `ui/package.json`, `ui/package-lock.json`, `mcp-server/package.json`, `mcp-server/package-lock.json` | modified | `0.1.0-rc.2` (row 2). CRLF kept |
| `mcp-server/src/index.ts` | modified | `:20` version only. CRLF kept (35) |
| `pyproject.toml`, `packages/api/pyproject.toml`, `packages/core/pyproject.toml`, `packages/infrastructure/pyproject.toml`, `packages/api/src/avkit_api/__init__.py` | modified | `0.1.0rc2` (row 2). Endings kept |
| `uv.lock` | modified | The four avkit packages at `0.1.0rc2`. LF kept (3,361) |
| `openapi.committed.json` | modified | `info.version` only (H1-4). CRLF kept (6,516) |
| `packaging/THIRD_PARTY_NOTICES.md` | modified | `NOTICE_LINE`: the libdvdread, libdvdnav and libdvdcss line, and the rc.2 tag link. CRLF kept (226) |
| `tests/unit/test_release_packaging.py`, `tests/unit/test_packaging_installer.py` | modified | AC-110.9's constants and AC-72.7's needles (row 1). Endings kept |
| `docs/releases/v0.1.0-rc.2-build-record.json` | new | The row 3 record, byte for byte |
| `docs/releases/v0.1.0-rc.2.md`, `docs/releases/publish-checklist-v0.1.0-rc.2.md` | new | The notes and the checklist (rows 8, 9), with the Transcript wording reset to the gate's facts (D-475). LF |
| `docs/build-plan/07-distribution.md` | modified | The Delivered note (`:388-397`). CRLF kept |
| `docs/BUILD_PLAN.md`, `.agent/context/meu-status.yaml`, `.agent/context/meu-registry.md` | modified | MEU-125 `ready_for_review` through `status-write.py` (row 10); see Execution notes on the render line |
| `.agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md` | modified | Row 57 `executed` with the plan folder (`:260`), by byte replacement. CRLF kept (322) |
| `.agent/context/MCP/mcp-tool-audit-report.md` | modified | The gate's audit report (H1-3) |
| `.agent/context/current-focus.md` | modified | Session 57 entry (H1-3) |
| Plan folder: `baseline.ps1`, `baseline.sha`, `baseline-dirty.txt`, `ruled-commits.txt`, `red-check.py`, `identity.py`, `version-bump.py`, `clean-tree.py`, `offline-probe.ps1`, `build-rc.ps1`, `build-identity.py`, `packaged-probes.ps1`, `packaged-app-smoke.mjs`, `install-roundtrip.ps1`, `audit-rule.py`, `audit-clear.ps1`, `status-write.py`, `session-gate.ps1`, `task.md` | new | The plan's scripts and records |

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
| F1 | High | Checklist step 6 left the notes partly false after either outcome of the Transcript recheck: on success the Known problems item still said the installed path was unverified, and on a block from another network the section still said Transcript hadn't been tried from another network and described the recheck as future work. | `docs/releases/publish-checklist-v0.1.0-rc.2.md:154-157`; `docs/releases/v0.1.0-rc.2.md:109-117,168-169` | Give each outcome its own updates to the section and its Known problems item. | fixed (round 2) |

### Verdict

`approved` in round 2 of loop `s57-execution-2026-11-08-release-rc2` (Codex, 2026-11-09), with no open findings and intent achieved. Round 1 (10,020,084 tokens) accepted the build and its evidence and returned `changes_required` for F1 (AC-125.21, `PUBLISH_CHECKLIST`). Step 6's success and blocked rows were rewritten (see Execution notes), row 9's check and the gate (run 6) were rerun, and round 2 (2,714,828 tokens; 12,734,912 of the 60,000,000 budget in all) closed F1 as `fixed`. Round 2 applied each of step 6's four outcomes to an in-memory copy of the notes and found each result true, found every quoted anchor in the notes, and confirmed that only checklist lines 154 and 155 changed since round 1. It recomputed the tested_state independently as `8ce8b956067b7edc034818d081bbf678460f1ef6+b62b8a982c40295c45173b435cac4401caeea0b0ca9f7bf345e31aba7358dadc`, which equals run 6's, leaving out the untracked `.claude/settings.local.json` that its sandbox counts, without opening that file. Report: [implementation-critical-review.md](2026-11-08-release-rc2-implementation-critical-review.md). H1-7a: `OK: review_mode=execution; round 2 of 6; verdict=approved; open findings=0` (`C:/Temp/av-kit/review-state-check.txt`). H1-7b: `OK: approved at round 2 of 6, 0 open blocking findings` (`C:/Temp/av-kit/exec-review.txt`).

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| Tag, draft release, upload, the clean-machine check, the Transcript recheck, publishing and RC1's note | out-of-scope | Mat, through `docs/releases/publish-checklist-v0.1.0-rc.2.md` | `NOTHING_PUBLISHED`; PROFILE E5; D-467 |
| The other-network Transcript run (D-216) | human | Mat, checklist step "Transcript recheck" | D-466: no result by row 8, so the notes use the alternative |
| `offline-probe.ps1` didn't cover the Electron `SHASUMS256.txt` fetch that `@electron/get` makes even with the zip cached | process gap | proposed for the register at closeout | S13 at row 3's first attempt; D-472 |
| Commit and push | out-of-scope | — | Only on Mat's explicit words (H2-5) |

**Execution notes.**
- **Row commands.** They ran through `.ps1` files written from the task cells, because the cells' `*>` needs PowerShell. Each file sets `RECEIPTS_DIR` and `PYTHONIOENCODING=utf-8`. The Python suite runs with `TMP` and `TEMP` in the session's scratch folder (`CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR`).
- **Row 3, S10 (D-471).** The clean-tree check refused 9 untracked paths of the capture-crop-copy session (MEU-130). All of them are under `docs/` or `.agent/`. Mat ruled B ("B"): leave them out.
  - `clean-tree.py` gained a repeatable `--leave-out PATH`. It refuses any path that `build-identity.py`'s `in_identity` counts as a build input.
  - The selftest gained four cases and passed 19 of 19.
  - The ruled check passed with the 9 paths named. Nothing was deleted before it passed.
- **Row 3, S13 (D-472).** The first build stopped at `offline-guard` before electron-builder ran. With the Electron 42.11.18 zip cached, `@electron/get` still fetches `SHASUMS256.txt` on every build (`ui/node_modules/app-builder-lib/out/util/electronGet.js:627-634`), a case the plan's offline probe didn't cover.
  - The cached zip's SHA-256 matched `ui/node_modules/electron/checksums.json`.
  - Mat ruled A ("A"): the coordinator wrote `%LOCALAPPDATA%\electron\Cache\SHASUMS256.txt-42.11.18` from that file and reran row 3 with the guard unchanged. No download happened.
- **Row 6, S16 (D-473).** The plan and row 6 said the capability models folder stays absent after the smoke. The tool always creates it, with a 16-byte stub `kokoro-v1_0.pth` and a `config.json` (`tools/smoke_packaged_tts.py:596-600`), and checks `files_unchanged` across the refused download.
  - Mat ruled A ("A"): row 6's cell, AC-125.17 and the plan's text were corrected to match the tool. The smoke itself was not changed or rerun.
  - The corrected post-check reads `config.json, kokoro-v1_0.pth; files_unchanged: True`.
- **S3 after row 7 (D-474).** HEAD moved from `8bcb4a6` to `8ce8b95` through Mat's two docs-only commits: `cbc6e22` (`.agent/context/current-focus.md`) and `8ce8b95` (the capture-crop-copy plan, including the 9 paths S10 left out).
  - The build record still matched the tree, so rows 3 to 7 stand.
  - Mat ruled "Accept the commits (Recommended)". `baseline.sha` stays row 0's, and `ruled-commits.txt` names the two commits.
  - The gate's `scope-paths` step accepts the move only when `baseline.sha` is an ancestor, every commit since it is ruled, and each ruled commit touches only `docs/` or `.agent/` paths outside this plan.
- **H1-2's first gate run (not a product failure).** The `task-contract` step refused `task.md:57`: row 6's S16-corrected Validation cell held three unescaped `|` pipes, so the row split into 13 cells.
  - Every step before it passed. Every step after it was `not_run`, so no audit request went out.
  - The cell was rewritten without pipes (the linter also refuses `\|`). The rewritten post-check gave the same result, and the lint passed 28 rows.
  - Then the gate ran again. That run's receipts are kept in `s57/gate-run-0-task-contract/`.
- **H1-2's second gate run (environment, not a product failure).** Every step through `build-record` passed. `ui-electron` passed 189 of 190: W2-4 passed, and AC-81.11 (`ui/tests/e2e/capture-inbox.test.ts:1930`) failed at `:1940` with `F2 held by another process`, Received `FAILED 0`.
  - That fixture registers F2 system-wide. A probe with `SetLastError` got error 1409 (`ERROR_HOTKEY_ALREADY_REGISTERED`) at 08:51 and 08:53. A desktop screenshot tool Mat had running held F2. The fixture's `DllImport` lacks `SetLastError`, so it printed `0` instead of 1409.
  - It isn't W2-4, so D-470's rerun rule didn't apply. The coordinator stopped and asked Mat, and stopped no process. Mat stopped the program ("ShareX stopped"). The probe then registered and released F2 at 09:26, S3 was rechecked clean, and the gate ran again unchanged.
  - The audit steps were `not_run`, so no audit request went out. That run's receipts are kept in `s57/gate-run-1-f2-held/`.
- **The notes' gate line and the final gate run.** H1-2 puts the gate's last line into the notes' "How this build was tested" section after the gate. The notes are a gated input (`identity.py:145`), so that edit moves the tested_state.
  - Following H1-6b ("If inputs changed … re-run H1-2"), the line was written after the third run, row 8's check was rerun, and the gate ran a fourth time on the finished notes.
  - The third run passed every step (`session-gate: all steps exit 0`, tested_state `8ce8b95…+d9c7c4aa…`) and its receipts are kept in `s57/gate-run-2-pre-notes/`. The fourth run (tested_state `8ce8b95…+fde2b6b5…`) gave the same counts, so the notes' sentence stood as written.
- **The Transcript wording (D-475).** Reading run 4's audit before the review, the coordinator found `transcript.resume` reached `transcripts_done 1` and `transcript.compile` wrote a combined file, while the notes and checklist said YouTube *is* blocking the test network.
  - Mat ruled "Reword to today's facts (Recommended)". The notes' section is now `Transcript on this build` (RC1 hit the block; the 2026-11-09 audit fetched and compiled captions on the same network through a checkout's backend; the installed app's path isn't verified; no other network was tried), with the Known problems line, checklist `:21-26` and step 6's table to match.
  - Rows 8 and 9's checks were rerun and passed. Run 4's receipts are kept in `s57/gate-run-3-pre-d475/`, and the gate ran a fifth time, which repeated D-464's audit requests. Run 5 passed every step with the same counts and again fetched and compiled captions, so the reworded section and the notes' test sentence stand. H1-3 and H1-4 were rerun on it.
- **Execution review round 1, F1.** Codex accepted the build and its evidence, and found that checklist step 6 left the notes partly false after either outcome: on success the Known problems item still said the installed path was unverified, and on a block from another network the section still said no other network was tried.
  - Step 6's success row now replaces that Known problems item with the date and network of the check, and its blocked row replaces the other-network line and the last paragraph with what the check showed. Each anchor it quotes is in the notes.
  - Row 9's check was rerun and passed. The checklist is a gated input, so run 5's receipts are kept in `s57/gate-run-4-pre-f1/` and the gate ran a sixth time, which repeated D-464's audit requests. Run 6 (`s57-gate-h1-2`) passed every step with the same counts and again fetched and compiled captions. H1-3 and H1-4 were rerun on it.
- **Row 10's render line (D-454).** `status-write.py` changed:
  - MEU-125's entry in `meu-status.yaml` (`:3276-3279`, status and labels; `:3294-3295`, `execution_plan` and `updated`);
  - MEU-125's row in `meu-registry.md` (`:124`);
  - one render line that doesn't name MEU-125: `BUILD_PLAN.md:68`, the Total, from `**118 + 1🚫**` to `**118 + 1🟡 + 1🚫**`.

  No capture-crop line changed, and the bytes before the write are kept.
- **Moved cites (Session 51 RULE-3).** Against the plan's anchors, 07's `---` moved from `:388` to `:398` under the new note (`:388-397`). The plan's other anchors hold: MEU-125 at `meu-status.yaml:3266`, grouping row 57 at `:260`, and 07 `:371-386`.
- **Live requests.** No row made a network request. The build ran behind `offline-guard`, and the packaged smokes ran behind dead proxies. The gate's `mcp-audit` step made the requests D-464 A authorizes, in runs 3 to 6 only; runs 1 and 2 stopped before it. All four audits passed 99 of 99, `transcript.resume` (`transcripts_done 1`) and `transcript.compile` among them: at RC1 that check failed while YouTube blocked captions from this machine (`YOUTUBE-CAPTIONS-IP-BLOCK`, D-186), so today's run reached captions. This is not D-216's other-network check, which stays with Mat (D-466).

---

## Decision Log

```yaml
decision_log:
  - id: D-471
    stage: execution
    question: "Row 3's clean-tree check refused 9 untracked paths of the capture-crop-copy session; how does the build proceed?"
    resolution: human
    class: two-way
    chosen: "B: leave the 9 paths out of the clean-tree check with a repeatable --leave-out that refuses any build input, and build"
    source_tag: Human-approved
    precedents: ["docs/execution/plans/2026-11-08-release-rc2/implementation-plan.md: S10 and its brief (User Review Required item 6)", "docs/execution/plans/2026-11-08-release-rc2/clean-tree.py: --leave-out and its four selftest cases"]
    research: { engine: none, sources: [] }
    reasoning: "The 9 paths are another session's plan documents under docs/ and .agent/, none of which the build reads; build-identity.py's in_identity confirms no build input is left out. Doing nothing would have stopped the release until that session committed. Two-way: the flag is plan-local."
    human_message_reference: "USER_EXPLICIT 2026-11-09 'B'"
  - id: D-472
    stage: execution
    question: "The first build stopped at the offline guard because @electron/get fetches SHASUMS256.txt even with the zip cached; how does the build get it?"
    resolution: human
    class: two-way
    chosen: "A: seed %LOCALAPPDATA%\\electron\\Cache\\SHASUMS256.txt-42.11.18 from the local ui/node_modules/electron/checksums.json, after checking the cached zip against it, and rerun row 3 with the guard unchanged"
    source_tag: Human-approved
    precedents: ["ui/node_modules/app-builder-lib/out/util/electronGet.js:627-634", "docs/execution/plans/2026-11-08-release-rc2/implementation-plan.md: S13"]
    research: { engine: none, sources: [] }
    reasoning: "The checksum list comes from the installed Electron package, whose hash the lock pins, and the zip matched it, so no new input enters the build and nothing is downloaded. Doing nothing would have stopped the build at S13; a download needs Mat's words. Two-way: one cache file."
    human_message_reference: "USER_EXPLICIT 2026-11-09 'A'"
  - id: D-473
    stage: execution
    question: "Row 6's check expected the capability models folder to stay absent, but the smoke tool always creates it with its stub and config; what changes?"
    resolution: human
    class: two-way
    chosen: "A: correct row 6's cell, AC-125.17 and the plan's text to match the tool: afterwards the folder holds only config.json and the stub kokoro-v1_0.pth, and files_unchanged is true"
    source_tag: Human-approved
    precedents: ["tools/smoke_packaged_tts.py:596-600 and :490-515", "docs/execution/plans/2026-11-08-release-rc2/implementation-plan.md: S16 and AC-125.17"]
    research: { engine: none, sources: [] }
    reasoning: "The smoke passed; the plan misread what the tool leaves behind. Doing nothing would have left row 6 failing against a wrong expectation. Two-way: a document correction, no product change."
    human_message_reference: "USER_EXPLICIT 2026-11-09 'A'"
  - id: D-474
    stage: execution
    question: "HEAD moved from baseline.sha through Mat's commits cbc6e22 and 8ce8b95 after row 7; does the session go on?"
    resolution: human
    class: two-way
    chosen: "Accept the commits: baseline.sha stays row 0's record, ruled-commits.txt names the two commits, and scope-paths accepts a moved HEAD only when every commit since the baseline is ruled and docs-only outside this plan"
    source_tag: Human-approved
    precedents: ["docs/execution/plans/2026-11-08-release-rc2/ruled-commits.txt", "docs/execution/plans/2026-11-08-release-rc2/implementation-plan.md: S3 and Planning receipts"]
    research: { engine: none, sources: [] }
    reasoning: "Both commits are docs-only and the build record still matched the tree, so rows 3 to 7 stand. Doing nothing would have stopped the session at S3. Two-way: the list is plan-local."
    human_message_reference: "USER_EXPLICIT 2026-11-09 'Accept the commits (Recommended)'"
  - id: D-475
    stage: execution
    question: "Gate runs 3 and 4 fetched and compiled captions on the test network, but the notes and checklist said YouTube is blocking it; what do they say?"
    resolution: human
    class: two-way
    chosen: "Reword to today's facts: keep YOUTUBE-CAPTIONS-IP-BLOCK, and say RC1 hit the block, the 2026-11-09 audit on the same network fetched and compiled captions, the installed app's Transcript path isn't verified, and another network wasn't tried; the same for the checklist; then rerun row 8 and the gate"
    source_tag: Human-approved
    precedents: ["C:/Temp/av-kit/s57/gate-run-3-pre-d475/s57-D6-mcp-audit/ (transcript.resume transcripts_done 1; transcript.compile wrote the combined file)", "docs/execution/plans/2026-11-08-release-rc2/implementation-plan.md: D-466 and AC-125.20", ".agent/context/known-issues.yaml: YOUTUBE-CAPTIONS-IP-BLOCK"]
    research: { engine: none, sources: [] }
    reasoning: "The notes' present-tense claim contradicted the gate's own receipts. The audit ran through a checkout's backend, not the installed app, so the Transcript gap and D-466's other-network check both stand. Doing nothing would have shipped a claim the receipts disprove. Two-way: two release documents."
    human_message_reference: "USER_EXPLICIT 2026-11-09 'Reword to today's facts (Recommended)'"
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-09 | claude-code-local (Claude Opus 5.5) | Initial MEU-125 handoff after the H1-2 gate |
