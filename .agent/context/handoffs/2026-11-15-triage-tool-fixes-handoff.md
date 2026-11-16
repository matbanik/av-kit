---
date: "2026-11-15"
project: "2026-11-15-triage-tool-fixes"
meu: "none"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-15-triage-tool-fixes/implementation-plan.md"
build_plan_section: "none (tooling debt in tools/issue_triage*; no MEU, D-815)"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-15-text-scrub-residuals-MEU-148-handoff.md"
---

# Handoff: 2026-11-15-triage-tool-fixes-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: none. This is Session 79 of the post-rc.3 triage residuals grouping (`.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md` §3). It works two tooling issues: `TOOLING-TRIAGE-CLI-CP1252` and `TOOLING-TRIAGE-SCANNER-FALSE-FINDINGS`.

**Goal anchor:** `tools/issue_triage.py` writes UTF-8 to a redirected receipt and never crashes on a Windows console code page; `verify --deep` reports only a missing file that a path-shaped `resolution_path` names and never writes the register; and `discover` reports no candidate from a vendored or bundled tree, a binary file or its own source.

**Execution gate.** `plan_to_exec_gate: human`. The plan review approved at round 2 (`.agent/context/handoffs/2026-11-15-triage-tool-fixes-plan-critical-review.md`). Mat, 2026-11-15: "proceed with planning and execution for P:\av-kit\.agent\context\grouping\2026-11-15-post-rc3-triage-residuals-session-grouping.md like we did here. But use the new HDP process. Continue orchestrating the sessions." After the plan review approved, the coordinator wrote those words into the plan's Status line (`implementation-plan.md:15`). That line is the only change made to the plan after its approval.

**Order and starting tree.** `main` at `263f635` (Session 77, committed and not pushed; `origin/main` is `ab761dd`). Session 78 (`e2e-harness-hardening`) is blocked at its row 0, waiting on Mat for the NuGet runtime packs, and changed no tracked file, so the coordinator ran Session 79 ahead of it (the executor brief's "Order and repository state" paragraph). The untracked plans and plan reviews of Sessions 78 and 80 to 83 sit in the same tree; this session left them alone. Every scope check binds to row 0's bytes (`baseline-scope.json`, `baseline-dirty-hashes.json`), not to `HEAD`, and `HEAD` did not move during the session.

- **UTF-8 output (rows 1 and 2, `TOOLING-TRIAGE-CLI-CP1252`, D-944).** `main` (`tools/issue_triage.py:338`) reconfigures `sys.stdout` and `sys.stderr` to UTF-8 with `errors="replace"`, each inside `contextlib.suppress(AttributeError, ValueError, OSError)`, before it builds the parser (`UTF8_STREAMS`). A redirected `--help` or `bucket` under cp1252 now exits 0 and writes `→` and `⚠` as UTF-8.
- **`verify --deep` (rows 3 and 4, D-945 to D-947).** `_is_path_like` (`tools/issue_triage/verify.py:23`) accepts one token with no whitespace and no `://` that holds a `/` or `\` or has a suffix (`PATH_LIKE`). `_strip_location` (`:32`) drops a trailing `:line` or `:line:col` and keeps a drive colon (`PATH_LOCATION`). `verify_deep` (`:180`) checks only a path-shaped `resolution_path`, under the project root, without its location (`PATH_CHECK`); it no longer reads `tests/` or emits `no_test_coverage` (`NO_COVERAGE_CHECK`); it lost `update_last_checked` and never changes its data, and `_cmd_verify` no longer saves the register (`DEEP_READ_ONLY`). The `--deep` help says "Check that path-shaped resolution_path values exist (read-only)" (`DEEP_HELP`).
- **`discover` (rows 5 and 6, D-948, D-953).** `EXCLUDED_DIRS` gains `.gitignore`'s slash-free generated trees and `EXCLUDED_PATHS` gains the vendored, bundled, built and fetched trees as `fnmatch` patterns (`tools/issue_triage/discover.py:52`, `:68`; `DISCOVER_ROOTS`). Exclusions match the path from the repository root that `_repo_root` finds, whatever `--root` is given, and a root inside an excluded tree scans nothing (`DISCOVER_ANCHOR`). A file with a NUL byte in its first 8,000 bytes is skipped (`DISCOVER_BINARY`), and so is the scanner's own module (`DISCOVER_SELF`).
- **`triage` (rows 7 and 8, D-949).** `generate_triage_output` archives `dismissed` issues beside `resolved` ones (`tools/issue_triage/triage.py:43`; `ARCHIVE_DISMISSED`).
- **The docs (row 9, D-950).** The ten line edits of `doc-check.py`'s `TABLE`, applied to the five docs from their row-0 bytes with their own line endings (`DOC_LINES`).
- **Live smoke and registers (rows 10 and 11).** `live-smoke.py` ran the changed tools on the real register and the real tree (AC-13). Both issues were resolved through `issue-resolve.py --expect-sha256` bound to row 0's register hash, then `issue_triage.py render` (AC-14); grouping §6 row 79 says `executed (Session 79)`.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-1 | unit (subprocess) | `--help` with `PYTHONIOENCODING=cp1252` and `PYTHONUTF8=0` exits 0 and its stdout holds `b"\xe2\x86\x92"`; the control shows the child's stdout encoding is `cp1252` | Local Canon (D-944) | `tests/unit/test_issue_triage.py:107` `test_ac_1_help_under_cp1252_exits_0_with_utf8_bytes` | ✅ |
| AC-2 | unit (subprocess) | `bucket` on a two-issue overlap fixture under cp1252 exits 0 and stdout holds `⚠ HAS RELATED OVERLAP` | Local Canon (D-944) | `test_issue_triage.py:121` `test_ac_2_bucket_overlap_under_cp1252_exits_0` | ✅ |
| AC-3 | unit | The `_is_path_like` truth table and the `_strip_location` rows | Local Canon (D-945) | `test_issue_triage.py:136` `test_ac_3_path_like_and_strip_location` | ✅ |
| AC-4 | unit | `verify_deep` on five open issues gives exactly the two `file_missing` findings for `missing/file.py` and `gone/other.py:9:2`, each `evidence_path` without its location | Local Canon (D-945) | `test_issue_triage.py:173` `test_ac_4_deep_checks_only_path_shaped_values` | ✅ |
| AC-5 | unit | No `no_test_coverage` with a `tests/` folder that never names the ids; finding types a subset of `{"file_missing"}` | Local Canon (D-946) | `test_issue_triage.py:194` `test_ac_5_deep_emits_no_test_coverage_finding` | ✅ |
| AC-6 | unit + subprocess | No `update_last_checked` parameter; the data equals its deep copy after the call; the CLI `--yaml f verify --deep` leaves `f`'s bytes unchanged, exits 1 for a missing path and 0 for prose | Local Canon (D-947) | `test_issue_triage.py:208` `test_ac_6_deep_is_read_only` | ✅ |
| AC-7 | unit | `scan_todos` skips the ten noise files and reports exactly the five controls; `_repo_root` of a subroot is the repository; `mcp-server` reports only `src/a.ts`; `mcp-server/bundle` and `ui/out` give `[]` | Local Canon (D-948, D-953) | `test_issue_triage.py:232` `test_ac_7_discover_skips_generated_trees_from_any_root` | ✅ |
| AC-8 | unit | A `lib/x.jar` with a NUL byte and a marker is skipped; the `notes.txt` control is reported | Local Canon (D-948) | `test_issue_triage.py:244` `test_ac_8_discover_skips_a_file_with_a_nul_byte` | ✅ |
| AC-9 | unit | `scan_todos(ROOT / "tools/issue_triage")` reports nothing from `discover.py`; a `tmp` file named `discover.py` with a marker is reported | Local Canon (D-948) | `test_issue_triage.py:253` `test_ac_9_discover_skips_its_own_module_only` | ✅ |
| AC-10 | subprocess | The CLI `discover --dry-run` prints `New candidates: 5` with only the controls, `1` from `mcp-server`, `0` from `mcp-server/bundle`; the register bytes unchanged | Local Canon (D-948, D-953) | `test_issue_triage.py:274` `test_ac_10_discover_cli_counts_only_source` | ✅ |
| AC-11 | unit | `generate_triage_output` archives the resolved and the dismissed issue, keeps TECH-DEBT actionable and `DEFER` deferred | Local Canon (D-949) | `test_issue_triage.py:290` `test_ac_11_triage_archives_resolved_and_dismissed` | ✅ |
| AC-12 | doc check | `doc-check.py --check` exits 0: each of the five docs equals its row-0 copy with `TABLE` applied, endings kept, no removed claim left; `--selftest` exits 0 | Local Canon (D-950, D-947) | `doc-check.py --check` (row 9, gate `doc-check`); `--selftest` 9/9 ok (row 0) | ✅ |
| AC-13 | live smoke | `live-smoke.py` exits 0 on the real register and tree: no `no_test_coverage`, no noise candidate from `.`, `mcp-server`, `ui` and `packaging`, 0 from inside `mcp-server/bundle` and `ui/out`, CLI counts equal, cp1252 `--help` exits 0, the register's SHA-256 unchanged | Local Canon (D-812; D-944 to D-948; D-953) | `live-smoke.py` (row 10, gate `live-smoke`) | ✅ |
| AC-14 | register | Both issues `resolved` through `issue-resolve.py` bound to row 0's register hash; `render` and `render --check` exit 0; the register stays LF; grouping §6 row 79 `executed (Session 79)` with this plan folder | Local Canon (`issue-triage.md` §Closing) | `issue-resolve.py` (row 11: 10 fields, 2 issues, 0 problems); `issue_triage.py render --check` (row 11, gate `issues-render-check`); the row-11 check | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-1 | FAILED: `assert 1 == 0`, the child's `UnicodeEncodeError: 'charmap' codec can't encode character '\u2192'` | passed (row 2) | `tests/unit/test_issue_triage.py:107` |
| AC-2 | FAILED: `assert 1 == 0`, the child's `UnicodeEncodeError: ... '\u26a0'` | passed (row 2) | `test_issue_triage.py:121` |
| AC-3 | FAILED: `assert False` where `False = hasattr(verify, '_is_path_like')` | passed (row 4) | `test_issue_triage.py:136` |
| AC-4 | FAILED: a prose value and `present.py:3` gave `file_missing` (four findings, two expected) | passed (row 4) | `test_issue_triage.py:173` |
| AC-5 | FAILED: `assert 'no_test_coverage' not in {'file_missing', 'no_test_coverage'}` | passed (row 4) | `test_issue_triage.py:194` |
| AC-6 | FAILED: the signature was `['data', 'project_root', 'update_last_checked']` | passed (row 4) | `test_issue_triage.py:208` |
| AC-7 | FAILED: the scan listed `.serena/cache/a.txt`, `_inspiration/external_code/x/a.properties`, `mcp-server/bundle/index.mjs` and the other noise files beside the controls | passed (row 6) | `test_issue_triage.py:232` |
| AC-8 | FAILED: `['lib/x.jar', 'notes.txt'] == ['notes.txt']` | passed (row 6) | `test_issue_triage.py:244` |
| AC-9, AC-10 | FAILED by assertion (`_SELF` absent; the CLI listed the noise files) | passed (row 6) | `test_issue_triage.py:253`, `:274` |
| AC-11 | FAILED: `{'archived': ['AR-1']} != {'archived': ['AR-1', 'AR-2']}` | passed (row 8) | `test_issue_triage.py:290` |

Red, encoding (row 1): `2 failed, 9 deselected` (child exit 1) and `red-check: 1 receipt(s), 2 required test(s), 0 problem(s)`. Green (row 2): `2 passed, 9 deselected`.

Red, verify (row 3): `4 failed, 7 deselected` (child exit 1), red-check `4 required test(s), 0 problem(s)`. Green (row 4): `6 passed, 5 deselected`; `verify.py CRLF kept: True`; the register callers `101 passed`.

Red, discover (row 5): `4 failed, 7 deselected` (child exit 1), red-check `4 required test(s), 0 problem(s)`. Green (row 6): `10 passed, 1 deselected`.

Red, triage (row 7): `1 failed, 10 deselected` (child exit 1), red-check `1 required test(s), 0 problem(s)`. Green (row 8): `11 passed`; `ruff check` on the test file `All checks passed!`; `ruff format --check` `1 file already formatted`.

Each Red ran the base code of the function under test, and each Green the changed code; every later row and the gate run the changed `tools/issue_triage*` of the working tree.

Receipts, all under `C:/Temp/av-kit/triage-tool-fixes/`:
- row 0: `ttf-baseline.txt` (`baseline: all steps exit 0`), `ttf-base-py.txt` (`2982 passed`), `ttf-ruff-base.txt`, `ttf-row0-eol.txt`, `ttf-d1040-apply.txt`, `ttf-d919-apply.txt`; the row-0 copies in `base/`;
- rows 1 and 2: `ttf-enc-red.txt` and its `.exit`, `ttf-enc-red-check.txt`, `ttf-enc-green.txt`;
- rows 3 and 4: `ttf-verify-red.txt` and its `.exit`, `ttf-verify-red-check.txt`, `ttf-verify-green.txt`, `ttf-verify-eol.txt`, `ttf-register-callers.txt`;
- rows 5 and 6: `ttf-discover-red.txt` and its `.exit`, `ttf-discover-red-check.txt`, `ttf-discover-green.txt`;
- rows 7 and 8: `ttf-triage-red.txt` and its `.exit`, `ttf-triage-red-check.txt`, `ttf-triage-green.txt`, `ttf-test-ruff.txt`, `ttf-test-format.txt`;
- row 9: `ttf-doc-apply.txt`, `ttf-doc-check.txt`; row 10: `ttf-live-smoke.txt`, `ttf-deep-readonly.txt`;
- row 11: `issue-resolve-set.json`, `ttf-issue-resolve.txt`, `ttf-issues-render.txt`, `ttf-issues-render-check.txt`, `ttf-row11-grouping.txt`, `ttf-row11-check.txt`;
- H1: `task-unchecked.txt` (H1-1); `ttf-gate-h1.txt` with `ttf-D6-<step>.txt` and `.exit` (H1-2); `ttf-render-check.txt` (H1-3); `openapi-check.txt` (H1-4); `ttf-h15-sources.txt` (H1-5); `handoff-check.txt` (H1-6), `handoff-ac-check.txt` (H1-6a) and `full-evidence-check.txt` (H1-6b).

Each row ran its task.md Validation cell verbatim from `C:/Temp/av-kit/triage-tool-fixes/run-row<n>.ps1`, after the row environment (`Set-Location P:/av-kit`, `PYTHONIOENCODING=utf-8`, `RECEIPTS_DIR=C:/Temp/av-kit`, `PYTHONDONTWRITEBYTECODE=1`, `ELECTRON_RUN_AS_NODE` cleared, `TMP` and `TEMP` at `C:\Temp\av-kit\triage-tool-fixes\tmp`) and the S4 check (`s4: pass` before every row), run as `pwsh -NoProfile -File`. The cp1252 tests (AC-1, AC-2) set `PYTHONIOENCODING=cp1252` and `PYTHONUTF8=0` in their own child's explicit environment; the row environment stays `utf-8`.

**The live smoke printed no `real:` line.** Its decisive lines: `verify_deep findings 0 types []`; `cli verify --deep exit 0`; `copy unchanged after verify --deep`; `ignored trees from git 69 noise trees 69`; `walk --root . files 839`; `scan_todos` new candidates 0 and the CLI count 0 from `.`, `mcp-server` (78 files), `ui` (369) and `packaging` (12); 0 from `mcp-server/bundle` and `ui/out`; `cp1252 --help exit 0 arrow bytes True`; the register's SHA-256 `458913892e2dc644e602518f4af45ee0ea9d08982673f32bb55f5d5b7952f050` before and after; `live-smoke: pass`.

**`DEEP_READ_ONLY` on the real register.** Beside the smoke, `deep-readonly.py` hashed the real register, ran the changed CLI `verify --deep` with its default `--yaml` (the real register) and hashed it again: `register sha256 before 458913…f050`, `cli verify --deep exit 0 | [DEEP VERIFY] No findings. All issues verified.`, `register sha256 after 458913…f050`, `register mtime unchanged: True`, `deep-readonly: pass`. The gate's `live-smoke` step proves the same hash again.

**Execution notes.** Each is a deviation from the plan, or a fact the plan did not foresee.

- **The Status line.** After the plan review approved, the coordinator wrote Mat's execute words into `implementation-plan.md:15`. It is the only change made to the plan after its approval; no row, AC or decision changed.
- **The session order.** Session 79 ran before Session 78, which is blocked at row 0 waiting on Mat (NuGet runtime packs) and changed no tracked file (the executor brief's "Order and repository state" paragraph).
- **`baseline.ps1`'s S2 code check (D-1040).** Row 0's first run reported S2 for the three LF code files although `git status` showed them clean and their working bytes equal the raw `HEAD` blobs: the system `core.autocrlf=true` makes `git cat-file --filters` emit CRLF for an LF blob. The check now accepts the working bytes when they equal the raw blob or the filtered one and `git diff --quiet HEAD -- PATH` exits 0 (`baseline.ps1`, SHA-256 `b1b08f65…` to `37fa5eb2…`, LF kept). The rerun ended `baseline: all steps exit 0`. S2 stays enforced: a changed file still fails both arms.
- **`red-check.py` carries D-919.** The plan copies `red-check.py` unchanged from `2026-11-15-framework-small-syncs`; this session applied Session 76's D-919 fix to it before any Red ran: `PYTEST_HEADER = ^_+ (.+?) _+\s*$` and the long-id fixture (`7db85aae…`; selftest `37 fixture(s) (12 positive, 25 negative), 0 wrong`).
- **The test file was written while row 0 was still running.** `tests/unit/test_issue_triage.py` was created after row 0's record step, during its base suite. `baseline-scope.json` records it `absent` correctly, and the base suite did not collect it (`ttf-base-py.txt` never names it).
- **Sizes since `6aaf9b0`.** Row 0 measured the same line endings as the plan everywhere; three sizes differ from the plan's `6aaf9b0` figures because Sessions 75 to 77 changed those files and are committed: `known-issues.yaml` 460,449 bytes (plan 455,210), `known-issues.md` 6,213 (plan 7,182), the grouping 31,580 (plan 31,451). They are bound by their row-0 hashes.
- **The `resolution_path` date.** Row 11's template begins `Fixed in Session 79 on 2026-11-15`. Every row ran after midnight on 2026-11-16 (row 0's receipt at 00:07), so both entries say `on 2026-11-16`, and `verification.last_checked` is `2026-11-16`.
- **The execution decision id.** The plan leaves D-954 free for execution; the executor brief assigns this session's execution ids from D-1040 to D-1049, so D-1040 is used.
- **The ruff base lines moved.** `tools-lint` compares `(path, code)` pairs only: row 0's `I001` in `issue_triage.py` and `E501` and `I001` in `verify.py` are the same three pairs after the fix, now at `verify.py:72` and `:166`.
- **Git's CRLF warnings.** `git diff` prints `LF will be replaced by CRLF` for the LF files. That comes from the system `core.autocrlf=true`, predates this session and changes no byte.
- **This handoff quotes no home-folder path.**

### Commands Executed

```json
{"schema_version": "evidence.v1", "check_id": "ttf-row0-baseline", "command": "pwsh -NoProfile -File C:/Temp/av-kit/triage-tool-fixes/run-row0.ps1 (task.md row 0 Validation cell, verbatim: baseline.ps1 into C:/Temp/av-kit/triage-tool-fixes/ttf-baseline.txt), run again after D-1040", "cwd": "P:/av-kit", "scope": "Row 0: baseline.sha, the dirty-path records, baseline-scope.json, the row-0 copies, the base Python suite, the base ruff pairs, the line endings of every Files Modified path, the S2 code check and the plan-local selftests", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 263f635 plus the row-0 dirty tree", "output": "baseline.sha 263f63568bce03028d544c0ab972db5c8e28d91b; baseline-dirty.txt 55 paths; baseline-scope.json 13 paths, tests/unit/test_issue_triage.py absent, known-issues.yaml 458913892e2dc644e602518f4af45ee0ea9d08982673f32bb55f5d5b7952f050; base suite 2982 passed, 37 warnings in 314.66s; base ruff pairs (tools/issue_triage.py, I001), (tools/issue_triage/verify.py, E501), (tools/issue_triage/verify.py, I001); doc-check selftest 9/9 ok; red-check selftest 37 fixture(s), 0 wrong; baseline: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ttf-row1-enc-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/triage-tool-fixes/run-row1.ps1 (task.md row 1 Validation cell, verbatim: -k ac_1 or ac_2 into ttf-enc-red.txt with its .exit, then red-check.py --require for both)", "cwd": "P:/av-kit", "scope": "Red for AC-1 and AC-2: the new tests against the base tools/issue_triage.py; the children run with PYTHONIOENCODING=cp1252 and PYTHONUTF8=0 in their own environment", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 263f635 plus row 1", "output": "2 failed, 9 deselected in 0.28s (child exit 1): UnicodeEncodeError 'charmap' codec can't encode character '\\u2192' (AC-1) and '\\u26a0' (AC-2). red-check: 1 receipt(s), 2 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ttf-row2-enc-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/triage-tool-fixes/run-row2.ps1 (task.md row 2 Validation cell, verbatim)", "cwd": "P:/av-kit", "scope": "Green for AC-1 and AC-2: UTF8_STREAMS in main", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 263f635 plus rows 1 and 2", "output": "2 passed, 9 deselected in 0.21s"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ttf-row3-verify-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/triage-tool-fixes/run-row3.ps1 (task.md row 3 Validation cell, verbatim: -k ac_3 to ac_6 into ttf-verify-red.txt with its .exit, then red-check.py --require for the four)", "cwd": "P:/av-kit", "scope": "Red for AC-3 to AC-6 against the base verify.py and the base _cmd_verify", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 263f635 plus rows 1 to 3", "output": "4 failed, 7 deselected in 17.73s (child exit 1): hasattr(verify, '_is_path_like') False; a prose value and present.py:3 gave file_missing; no_test_coverage emitted; signature ['data', 'project_root', 'update_last_checked']. red-check: 1 receipt(s), 4 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ttf-row4-verify-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/triage-tool-fixes/run-row4.ps1 (task.md row 4 Validation cell, verbatim: the selection into ttf-verify-green.txt, the CRLF check into ttf-verify-eol.txt, the register callers into ttf-register-callers.txt)", "cwd": "P:/av-kit", "scope": "Green for AC-3 to AC-6: PATH_LIKE, PATH_LOCATION, PATH_CHECK, NO_COVERAGE_CHECK, DEEP_READ_ONLY, DEEP_HELP", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 263f635 plus rows 1 to 4", "output": "6 passed, 5 deselected in 0.33s; verify.py CRLF kept: True; register callers 101 passed in 6.82s"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ttf-row5-discover-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/triage-tool-fixes/run-row5.ps1 (task.md row 5 Validation cell, verbatim: -k ac_7 to ac_10 into ttf-discover-red.txt with its .exit, then red-check.py --require for the four)", "cwd": "P:/av-kit", "scope": "Red for AC-7 to AC-10 against the base discover.py", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 263f635 plus rows 1 to 5", "output": "4 failed, 7 deselected in 0.41s (child exit 1): the AC-7 noise files listed beside the controls; lib/x.jar listed; the module's own markers and _SELF absent; the CLI counted the noise files. red-check: 1 receipt(s), 4 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ttf-row6-discover-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/triage-tool-fixes/run-row6.ps1 (task.md row 6 Validation cell, verbatim)", "cwd": "P:/av-kit", "scope": "Green for AC-7 to AC-10: DISCOVER_ROOTS, DISCOVER_ANCHOR, DISCOVER_BINARY, DISCOVER_SELF", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 263f635 plus rows 1 to 6", "output": "10 passed, 1 deselected in 0.60s"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ttf-row7-triage-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/triage-tool-fixes/run-row7.ps1 (task.md row 7 Validation cell, verbatim: -k ac_11 into ttf-triage-red.txt with its .exit, then red-check.py --require)", "cwd": "P:/av-kit", "scope": "Red for AC-11 against the base triage.py", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 263f635 plus rows 1 to 7", "output": "1 failed, 10 deselected in 0.25s (child exit 1): {'archived': ['AR-1']} != {'archived': ['AR-1', 'AR-2']}. red-check: 1 receipt(s), 1 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ttf-row8-triage-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/triage-tool-fixes/run-row8.ps1 (task.md row 8 Validation cell, verbatim: the whole test file, ruff check and ruff format --check on it)", "cwd": "P:/av-kit", "scope": "Green for AC-11 (ARCHIVE_DISMISSED) and the whole test file", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 263f635 plus rows 1 to 8", "output": "11 passed in 1.35s; ruff check All checks passed!; ruff format --check 1 file already formatted"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ttf-row9-doc-check", "command": "pwsh -NoProfile -File C:/Temp/av-kit/triage-tool-fixes/run-row9.ps1 (task.md row 9 Validation cell, verbatim: doc-check.py --apply, then --check into ttf-doc-check.txt)", "cwd": "P:/av-kit", "scope": "AC-12: DOC_LINES in the five docs from their row-0 bytes", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 263f635 plus rows 1 to 9", "output": "ok .agent/workflows/issue-triage.md 15012 bytes CRLF kept; ok .agent/skills/issue-triage/SKILL.md 4809 bytes LF kept; ok .agent/docs/issue-lifecycle-guide.md 25278 bytes CRLF kept; ok .agent/docs/commands.md 18365 bytes CRLF kept; ok .agent/docs/cloud-local-collaboration.md 26319 bytes CRLF kept; doc-check: exit 0"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ttf-row10-live-smoke", "command": "pwsh -NoProfile -File C:/Temp/av-kit/triage-tool-fixes/run-row10.ps1 (task.md row 10 Validation cell, verbatim: live-smoke.py into ttf-live-smoke.txt); then deep-readonly.py into ttf-deep-readonly.txt", "cwd": "P:/av-kit", "scope": "AC-13: the changed tools on the real register and the real tree; DEEP_READ_ONLY through the CLI on the real register", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 263f635 plus rows 1 to 9", "output": "verify_deep findings 0 types []; cli verify --deep exit 0; copy unchanged after verify --deep; ignored trees from git 69 noise trees 69; files walked . 839, mcp-server 78, ui 369, packaging 12; new candidates 0 and CLI count 0 from each; 0 from mcp-server/bundle and ui/out; cp1252 --help exit 0 arrow bytes True; register sha256 458913892e2dc644e602518f4af45ee0ea9d08982673f32bb55f5d5b7952f050 before and after; no real: line; live-smoke: pass. deep-readonly: register sha256 before and after equal, mtime unchanged, cli exit 0 [DEEP VERIFY] No findings. All issues verified.; deep-readonly: pass"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ttf-row11-registers", "command": "pwsh -NoProfile -File C:/Temp/av-kit/triage-tool-fixes/run-row11.ps1 (task.md row 11 Validation cell, verbatim: issue-resolve.py with issue-resolve-set.json and --expect-sha256 from baseline-scope.json, issue_triage.py render, render --check; then the grouping row 79 edit and the row-11 check)", "cwd": "P:/av-kit", "scope": "AC-14: both issues through the repo tools, and grouping section 6 row 79", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 263f635 plus rows 1 to 11", "output": "decision logs read: 95 of 95; register sha256 before=458913892e2dc644e602518f4af45ee0ea9d08982673f32bb55f5d5b7952f050 after=3b345682f255f3fe30f7311c06bf6a73a6c3c49c16b5aca5b267bc7619bda253 CRLF=0; 10 parsed fields changed, all under status, verification and resolution_path of TOOLING-TRIAGE-CLI-CP1252 and TOOLING-TRIAGE-SCANNER-FALSE-FINDINGS; issue-resolve: 0 problem(s); Rendered known-issues.md: 58 lines; OK: known-issues.md is up-to-date; grouping changed lines [260], 0 CR; row 79 executed (Session 79) with the plan folder, grouping LF True, register LF True"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ttf-h1-1-unchecked", "command": "pwsh -NoProfile -File C:/Temp/av-kit/triage-tool-fixes/run-h1-1.ps1 (task.md row H1-1 Validation cell, verbatim)", "cwd": "P:/av-kit", "scope": "H1-1: no implementation row of task.md is unchecked", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 263f635 plus rows 1 to 11", "output": "unchecked implementation rows: []"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ttf-gate-h1-2", "command": "pwsh -NoProfile -File C:/Temp/av-kit/triage-tool-fixes/run-h1-2.ps1 (task.md row H1-2 Validation cell, verbatim: $env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-15-triage-tool-fixes/session-gate.ps1 *> C:/Temp/av-kit/triage-tool-fixes/ttf-gate-h1.txt)", "cwd": "P:/av-kit", "scope": "H1-2, the registered D6 gate on the whole tree after rows 0 to 11: identity, ruff and the tools-lint base pairs, ruff format, the task contract, the scope paths, the line endings, doc-check, the red-check selftest, the test file, the register callers, the adoption suite, the live smoke, the full Python suite, the state and issue renders, then the identity again", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "263f63568bce03028d544c0ab972db5c8e28d91b+4a8b2b766f652e20156aedb7c6cd3f58b108755cf8ae007ba63d1317ce35f2b8", "output": "baseline py failures excused: 0 id(s); identity-before exit=0 tested_state 263f63568bce03028d544c0ab972db5c8e28d91b+4a8b2b766f652e20156aedb7c6cd3f58b108755cf8ae007ba63d1317ce35f2b8, ELECTRON_RUN_AS_NODE <unset>; py-lint exit=0 All checks passed!; tools-lint exit=0 new pairs (not in ttf-ruff-base.txt): []; py-format exit=0 1 file already formatted; task-contract exit=0 OK: 29 row(s), 27 fully checked, 2 exempt (view_file): H1-5, H2-1; scope-paths exit=0 changed paths: 69 outside scope: [] baseline-dirty content moved: [] head moved (S4): False; line-endings exit=0 line-ending problems: []; doc-check exit=0 doc-check: exit 0; red-check-selftest exit=0 37 fixture(s) (12 positive, 25 negative), 0 wrong; triage-tests exit=0 11 passed in 2.16s; register-callers exit=0 101 passed in 18.98s; adoption exit=0 96 passed in 184.65s; live-smoke exit=0 live-smoke: pass; py-tests exit=0 2993 passed, 37 warnings in 572.07s; state-render exit=0 Drift check passed, SSOT loaded (153 MEUs, 12 phases), rendered regions match on-disk content; issues-render-check exit=0 OK: known-issues.md is up-to-date; identity-after exit=0 tested_state before=263f63568bce03028d544c0ab972db5c8e28d91b+4a8b2b766f652e20156aedb7c6cd3f58b108755cf8ae007ba63d1317ce35f2b8 after=263f63568bce03028d544c0ab972db5c8e28d91b+4a8b2b766f652e20156aedb7c6cd3f58b108755cf8ae007ba63d1317ce35f2b8; session-gate: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ttf-h1-3-render", "command": "pwsh -NoProfile -File C:/Temp/av-kit/triage-tool-fixes/run-h1-3.ps1 (task.md row H1-3 Validation cell, verbatim: rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/triage-tool-fixes/ttf-render-check.txt)", "cwd": "P:/av-kit", "scope": "H1-3: rendered state regions after this session's current-focus entry. No MEU status changes in this session", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "263f63568bce03028d544c0ab972db5c8e28d91b+4a8b2b766f652e20156aedb7c6cd3f58b108755cf8ae007ba63d1317ce35f2b8", "output": "Drift check passed, SSOT loaded (153 MEUs, 12 phases), rendered regions match on-disk content"}
```

```json
{"schema_version": "evidence.v1", "check_id": "ttf-h1-4-openapi", "command": "pwsh -NoProfile -File C:/Temp/av-kit/triage-tool-fixes/run-h1-4.ps1 (task.md row H1-4 Validation cell, verbatim, into openapi-check.txt)", "cwd": "P:/av-kit", "scope": "H1-4: the basis for skipping the OpenAPI check (git diff from baseline.sha and untracked files under packages/api)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "263f63568bce03028d544c0ab972db5c8e28d91b+4a8b2b766f652e20156aedb7c6cd3f58b108755cf8ae007ba63d1317ce35f2b8", "output": "packages/api changes: []"}
```

### Quality Gate Results

`ttf-gate-h1-2` is the fresh full record (`ttf-gate-h1.txt`). Its last line is:

> session-gate: all steps exit 0

| Step | Stage | Exit | Result |
|------|-------|------|--------|
| identity-before | identity | 0 | `tested_state` recorded; `ELECTRON_RUN_AS_NODE <unset>` |
| py-lint | static | 0 | `All checks passed!` |
| tools-lint | static | 0 | `new pairs (not in ttf-ruff-base.txt): []` (the three row-0 pairs only) |
| py-format | static | 0 | `1 file already formatted` |
| task-contract | static | 0 | 29 rows, 27 fully checked, 2 exempt (`view_file`: H1-5, H2-1) |
| scope-paths | static | 0 | 69 changed paths, none outside scope; baseline-dirty content unmoved; `HEAD` not moved |
| line-endings | static | 0 | `line-ending problems: []` over the 13 Files Modified paths |
| doc-check | static | 0 | `doc-check: exit 0` |
| red-check-selftest | static | 0 | 37 fixtures (12 positive, 25 negative), 0 wrong |
| triage-tests | targeted | 0 | `11 passed in 2.16s` |
| register-callers | targeted | 0 | `101 passed in 18.98s` |
| adoption | targeted | 0 | `96 passed in 184.65s` |
| live-smoke | targeted | 0 | `live-smoke: pass` (after row 11: register `3b345682…a253` before and after) |
| py-tests | full | 0 | `2993 passed, 37 warnings in 572.07s` (row 0: 2982; +11 new tests); 0 baseline failures excused |
| state-render | full | 0 | Drift check passed (153 MEUs, 12 phases) |
| issues-render-check | full | 0 | `OK: known-issues.md is up-to-date` |
| identity-after | identity | 0 | `tested_state` equal before and after |

Skipped with their reasons in the receipt: `py-types` (pyright covers `packages/` only, and nothing there changes), the `ui-*` steps, the `mcp-*` steps, `e2e`, `openapi` (H1-4) and `build-record`.

`tested_state` `263f63568bce03028d544c0ab972db5c8e28d91b+4a8b2b766f652e20156aedb7c6cd3f58b108755cf8ae007ba63d1317ce35f2b8`, the same before and after the gate. H1-3's current-focus entry, `task.md`'s row marks and this handoff are `PROJECT_ARTIFACTS` that `identity.py` excludes; H1-6b re-derives the state after them.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `tools/issue_triage.py` | modified | `UTF8_STREAMS` (`import contextlib`), `DEEP_READ_ONLY` in `_cmd_verify`, `DEEP_HELP`; LF kept, 15,643 to 15,907 bytes |
| `tools/issue_triage/verify.py` | modified | `_is_path_like`, `_strip_location`, `PATH_CHECK`, `NO_COVERAGE_CHECK`, `DEEP_READ_ONLY`, the docstring; CRLF kept, 8,784 to 8,004 bytes |
| `tools/issue_triage/discover.py` | modified | `DISCOVER_ROOTS`, `DISCOVER_ANCHOR`, `DISCOVER_BINARY`, `DISCOVER_SELF`; LF kept, 9,427 to 11,626 bytes |
| `tools/issue_triage/triage.py` | modified | `ARCHIVE_DISMISSED`, the docstring; LF kept, 2,529 to 2,558 bytes |
| `tests/unit/test_issue_triage.py` | new | AC-1 to AC-11, 11 tests; LF, 305 lines, 11,893 bytes; markers built as `"TO" + "DO"` |
| `.agent/workflows/issue-triage.md`, `.agent/skills/issue-triage/SKILL.md`, `.agent/docs/issue-lifecycle-guide.md`, `.agent/docs/commands.md`, `.agent/docs/cloud-local-collaboration.md` | modified | `DOC_LINES` through `doc-check.py`'s `TABLE`; endings kept (CRLF, LF, CRLF, CRLF, CRLF) |
| `.agent/context/known-issues.yaml` | modified, by `issue-resolve.py` only | The two issues' `status`, `verification` and `resolution_path` (10 parsed fields); LF kept |
| `.agent/context/known-issues.md` | regenerated, by `issue_triage.py render` only | LF |
| `.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md` | modified | §6 row 79 only (line 260); LF kept |
| `.agent/context/current-focus.md` | modified | This session's entry on top (H1-3); CRLF kept |
| Plan folder: `baseline.ps1` (D-1040), `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `red-check.py` (D-919), `session-gate.ps1` (new in H1-2), `task.md` (rows marked) | new or modified | The plan's records, oracles and gate |

```diff
 def main(argv: list[str] | None = None) -> int:
     """CLI entrypoint."""
+    # A redirected Windows console is cp1252; write UTF-8 so → and ⚠ never raise (D-944).
+    for stream in (sys.stdout, sys.stderr):
+        with contextlib.suppress(AttributeError, ValueError, OSError):
+            stream.reconfigure(encoding="utf-8", errors="replace")
```

```diff
+        # Read-only: the register is never written (D-947).
         data = load(args.yaml)
-        findings = verify_deep(data, update_last_checked=True)
+        findings = verify_deep(data)
 ...
-            save(data, args.yaml)
             return 1
 ...
-            save(data, args.yaml)
             return 0
```

```diff
+def _is_path_like(value: object) -> bool:
+    """Whether VALUE is one path-shaped token, not prose, a URL or an id (D-945)."""
+    if not isinstance(value, str):
+        return False
+    s = value.strip()
+    if not s or any(c.isspace() for c in s) or "://" in s:
+        return False
+    return "/" in s or "\\" in s or bool(PurePosixPath(s).suffix)
 ...
-        if resolution_path and isinstance(resolution_path, str):
-            full_path = root / resolution_path
+        if not _is_path_like(resolution_path):
+            continue
+        full_path = root / _strip_location(resolution_path.strip())
 ...
-        # AC-3: Check test coverage (issue ID in tests/)
-        tests_dir = root / "tests"
 ...
-        # AC-6: Update verification.last_checked
-        if update_last_checked:
```

```diff
-    for file_path in _walk_source_files(root, root):
+    # Exclusions are matched against the repository path, whatever root is given (D-953).
+    anchor = _repo_root(root)
+    if _in_excluded_tree(root, anchor):
+        return findings
+
+    for file_path in _walk_source_files(root, anchor):
+        if file_path.resolve() == _SELF:
+            continue
 ...
-            text = file_path.read_text(encoding="utf-8", errors="ignore")
+            raw = file_path.read_bytes()
         except OSError:
             continue
+        if b"\x00" in raw[:_BINARY_SNIFF_BYTES]:
+            continue
+        text = raw.decode("utf-8", errors="ignore")
```

```diff
-        if issue.get("status") == "resolved":
+        if issue.get("status") in ("resolved", "dismissed"):
             archived.append(entry)
```

Line endings, measured as Python bytes after the last edit (the gate's `line-endings` step): `verify.py` and the four CRLF docs CRLF on every line; `issue_triage.py`, `discover.py`, `triage.py`, the test file, `SKILL.md`, `known-issues.yaml`, `known-issues.md` and the grouping 0 CR; `task.md`, `baseline.ps1`, `red-check.py` and `session-gate.ps1` LF.

---

## Codex Validation Report

Left for the reviewer. The H1-7 execution review writes the verdict to `.agent/context/handoffs/2026-11-15-triage-tool-fixes-implementation-critical-review.md`; this section only records it.

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

The H1-7 review, round 1 of loop `ttf-execution-2026-11-15-triage-tool-fixes` (cap 6), raised no finding.

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

### Verdict

**approved** at round 1 of 6: 0 findings, 0 blocking, intent achieved: yes. Usage 4,247,841 tokens (dispatch `ttf-exec-r1`).

- The review accepted Q1 to Q6 (encoding, deep verification, discovery, triage and documents, tests and evidence, safety and fidelity). Its IR-5 audit rated AC-1 to AC-4 and AC-6 to AC-11 Strong, and AC-5 Adequate alone and Strong together with AC-4. It marked IR-1, IR-4, IR-5, IR-7, DR, the Red rigor, the adversarial probes and the gate's freshness `pass`, with IR-2, IR-3 and IR-6 `n/a`.
- It held D-944 to D-953 fixed and found D-1040 sound (`baseline.ps1:129`): its probes showed the four delivered code changes and appended-byte controls fail the byte check, so S2 stays effective. It found D-919 in `red-check.py:83` does not weaken the Red proof.
- Its own runs: the test file `11 passed in 0.58s`; `doc-check.py --check` and `--selftest` 9/9; the red-check selftest 37 fixtures, 0 wrong, and the four Red receipts replayed with 0 problems; a probe over all 39 exclusion patterns and seven controls.
- The reviewer's `tested_state` was `263f63568bce03028d544c0ab972db5c8e28d91b+4a8b2b766f652e20156aedb7c6cd3f58b108755cf8ae007ba63d1317ce35f2b8`, equal to the gate's.
- Residual limits it named: the approved path-shape rules, the fixed exclusion inventory and the first-8,000-byte NUL heuristic.
- H1-7a, the review-state check: `OK: review_mode=execution; round 1 of 6; verdict=approved; open findings=0`.
- H1-7b, the execution-review check: `OK: approved at round 1 of 6, 0 open blocking findings`.
- The canonical review is `.agent/context/handoffs/2026-11-15-triage-tool-fixes-implementation-critical-review.md`, a byte copy of the reviewer's output that the coordinator collected.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| The three existing ruff findings in the tool files (`I001` in `issue_triage.py`, `E501` and `I001` in `verify.py`) | out-of-scope | — | Plan §Out of Scope: neither issue names them; the gate allows no new pair |
| Commit | out-of-scope | Mat | The coordinator commits after the execution review clears, without a push (Mat: "I give you permissions to commit as you need to. Leave off the push.") |

---

## Decision Log

```yaml
decision_log:
  - id: D-1040
    stage: execution
    question: "Row 0's S2 code check reported the three LF code files as changed since HEAD although git status showed them clean: the system core.autocrlf=true makes git cat-file --filters emit CRLF for an LF blob. How does baseline.ps1 decide that a code file is unchanged?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A file is unchanged when its working bytes equal the raw HEAD blob or the filtered one and git diff --quiet HEAD on that path exits 0; the S2 stop is kept for every other case"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-11-15-triage-tool-fixes/baseline.ps1 — the S2 code check, now two arms", "docs/execution/plans/2026-11-15-triage-tool-fixes/implementation-plan.md §Stop Conditions S2 — stop when a code file of Files Modified changed since HEAD", "docs/execution/plans/2026-11-15-tooling-test-hermeticity/baseline-dirty-blobs.json — Session 76 met the same autocrlf effect and compared blobs instead of filtered bytes"]
    research: { engine: none, sources: [] }
    reasoning: "The working bytes equal the raw HEAD blob byte for byte and git diff reports no change, so the stop was a false positive of the comparison, not a changed file. Comparing with both the raw and the filtered blob, and requiring git diff to agree, still stops for any real change, so S2 keeps its meaning. Stopping for Mat lost, because nothing in the tree had changed. Turning off core.autocrlf lost, because the brief forbids changing git config. Dropping the byte check lost, because git diff alone trusts the index stat cache. Two-way: one plan-local script."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-16 | claude-code-local (Claude Opus 5.5) | Initial handoff after H1-1 to H1-5; for the H1-7 execution review |
| Updated | 2026-11-16 | claude-code-local (Claude Opus 5.5) | The H1-7 Codex report (approved at round 1 of 6, 0 findings) |
