---
date: "2026-11-17"
project: "2026-11-15-docs-path-hygiene"
meu: "none"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-15-docs-path-hygiene/implementation-plan.md"
build_plan_section: "none (tooling and doc text; no MEU)"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-15-ready-handshake-MEU-154-handoff.md"
---

# Handoff: 2026-11-15-docs-path-hygiene-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: none. This is Session 83, the ninth session of the post-rc.3 triage residuals grouping (`.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md` §3). It closes two register issues: `INSTALL-FOLDER-NAME-MISMATCH` (triage D-811) and `TRACKED-FILES-HOLD-HOME-PATH` (grouping D-817, ruled A by Mat).

**Goal anchor:** av-kit's tracked text names the install folder the installer really uses (`Programs/av-kit-ui`), and a gate check, `tools/check_home_path.py`, fails when a file outside today's allow-listed evidence holds the home folder's full path; the six live files that hold it today are fixed, and every evidence file keeps its bytes.

**Execution gate.** `plan_to_exec_gate: human`. The plan review approved at round 3 (`.agent/context/handoffs/2026-11-15-docs-path-hygiene-plan-critical-review.md`). Mat's words, quoted on the plan's Status line: "proceed with planning and execution for P:\av-kit\.agent\context\grouping\2026-11-15-post-rc3-triage-residuals-session-grouping.md like we did here. But use the new HDP process. Continue orchestrating the sessions." The session ran on `main` from `86ee8e3` (`baseline.sha` `86ee8e31c4e3db29c45d1f316f350b9080b09d9f`); HEAD did not move. This handoff does not commit; the commit is Mat's call.

- **Part 1, the install folder (row 5).** `docs/build-plan/07-distribution.md:40` now reads `Programs/av-kit-ui`, and the install layout's seven lines from `├── extra/` through `└── mcp-server/` are replaced by the plan's six-line block, so the backend, ffmpeg and the MCP server sit directly under `resources/` as the installer puts them (D-996). `README.md:174-175`, the hand-written MCP config, now names `Programs\\av-kit-ui\\` (D-991); `av-kit.exe` stays. The package is not renamed (D-811); the round-trip scripts are not touched (D-990).
- **Part 2, the home folder (rows 1 to 4 and 6 to 10).**
  - `tools/check_home_path.py` (`CHECK`, new, LF, standard library): it scans tracked and untracked (not ignored) files outside `.agent/fleet/hub/`, reads each as UTF-8, UTF-16 or UTF-32 by its byte-order mark and a file with a NUL and no mark in five views, matches the home folder in its usual spellings only where the user name ends, and prints `path:line` only (D-988). An allow-listed file is exempt only while its content digest matches (D-997). Exit 0 `ok files= allowlisted= nul=`, exit 1 `refused found= changed= stale=`, exit 2 a usage or allow-list error.
  - `tools/home_path_allowlist.txt` (`ALLOW`, new, LF): a 7-line header and 60 entries, one per evidence file (16 handoffs, 14 session digests, 30 plan-folder files), each with its digest.
  - `tests/tooling/test_check_home_path.py` (new, LF): AC-1 to AC-7, AC-22 and AC-23, 47 cases, fake home `C:\Users\fixture`.
  - The six live files now write `~`, `C:/Users/YOU` or the fixture user `C:/Users/avkit` instead of the home folder (D-992): `.agent/skills/git-workflow/SKILL.md:153`, `_inspiration/capture-crop/design.md:205`, `docs/build-plan/06-gui.md:960` and `:975`, `ui/tests/unit/capture-interactive.test.ts:14`, `ui/tests/unit/dev-spawn.test.ts:8`, `:76`, `:77`, `:88`, `:89`, and `.agent/context/known-issues.yaml` (`CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` `root_cause` and `notes`).
  - `.agent/docs/commands.md` gains the `home-path` D6 row directly after `task-contract` (CRLF, add-only), so every session's gate runs `CHECK`. It is not in CI or `agent-commit.ps1`, because another machine's home folder differs.
  - The register: `INSTALL-FOLDER-NAME-MISMATCH` (row 7) and `TRACKED-FILES-HOLD-HOME-PATH` (row 10) are `resolved`; `known-issues.md` is rendered.

Not in scope: `tools/validate_closeout_artifacts.py`, the package name, the two older install round-trip scripts, CI, `agent-commit.ps1`, `P:/agentic-framework`, `P:/zorivest`, `P:/.agent`, any git configuration, and the commit itself.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-1 | integration | Each of the 12 home forms (back and forward slashes, doubled backslashes, other case, `file:///`, Git Bash, WSL, the bare home, and the home before `.`, `, `, `)` and a closing quote) is `found`, in every encoding `CHECK` reads | Human-approved (D-817); Local Canon (D-988) | `tests/tooling/test_check_home_path.py:208` (12 parametrized cases, CLI by subprocess; 10 encodings each) | ✅ |
| AC-2 | integration | None of the near misses is reported (`fixtures`, `fixture.other`, `fixture-other`, `fixture_x`, `fixtureé`, `YOU`, another drive, `fixture` alone, `~/a`, `%USERPROFILE%\a`) | Local Canon (D-988) | `test_check_home_path.py:234` | ✅ |
| AC-3 | integration | One `found path:line` per instance, sorted, right line numbers in LF and CRLF files, then `refused found=n changed=0 stale=0`, exit 1; no `Users` or `fixture` in the output | Human-approved (D-817) | `test_check_home_path.py:246` | ✅ |
| AC-4 | integration | A listed file with its digest is exempt; a missing listed file is `stale` (exit 1); nine malformed allow-list lines and a missing allow-list exit 2 without echo | Human-approved (D-817) | `test_check_home_path.py:279`, `:291`, `:317` (9 cases), `:328` | ✅ |
| AC-5 | integration | Untracked files are scanned, ignored ones are not, a deleted tracked file is skipped; a hub file is never opened (patched reader); the secret file names are never opened (D-1081) | Local Canon (D-988; the hub rule) | `test_check_home_path.py:340`, `:357`, `:380` | ✅ |
| AC-6 | integration | An unknown flag, a `--repo` that is not a repository (plain folder and absent) and a short `--home` (`C:\`, `/home`) exit 2 with no traceback and no echo | Local Canon (`check_commit_identity.py` convention) | `test_check_home_path.py:394`, `:403` (2 cases), `:416` (2 cases) | ✅ |
| AC-7 | integration | With `--home /home/fixture` the POSIX forms are found case-sensitively; the five negatives are not | Research-backed (POSIX paths are case-sensitive) | `test_check_home_path.py:427` | ✅ |
| AC-8 | unit | `inventory.py --check-allowlist --cross-check`: `ALLOW` lists exactly `EVIDENCE_SET` with the row-0 digests, and `CHECK` with an empty allow-list finds exactly `inventory.py`'s pairs | Human-approved (D-817); Local Canon (D-989) | Row 3 (`dph-allowlist-check.txt`); gate `inventory-check`; `inventory.py --selftest` (row 0, 0 failures) | ✅ |
| AC-9 | integration | Repo Red: `CHECK` with `ALLOW` exits 1 and its `found` set equals `LIVE_SET` (12 pairs), with no `stale` or `changed` line | Human-approved (D-817) | Row 4 (`dph-repo-red.txt`, `dph-repo-red-check.txt`) | ✅ |
| AC-10 | unit | `SKILL.md`: only the transcript line changes, to `~`; CRLF kept | Local Canon (D-992) | Row 5 `edit-check.py --group docs`; gate `edit-check-docs`; `edit-check.py --selftest` (row 0) | ✅ |
| AC-11 | unit | `design.md`: only line 205 changes, to `C:/Users/YOU/Desktop/…`; LF kept | Local Canon (D-992) | as AC-10 | ✅ |
| AC-12 | unit | `06-gui.md`: only lines 960 and 975 change, to `~/…` padded to the old width; CRLF kept | Local Canon (D-992) | as AC-10 | ✅ |
| AC-13 | unit | `07-distribution.md`: line 40 reads `Programs/av-kit-ui`; the seven `extra/` lines become the plan's six; CRLF kept | Local Canon (D-811, applied; D-996) | as AC-10 | ✅ |
| AC-14 | unit | `README.md`: only lines 174 and 175 change, to `Programs\\av-kit-ui\\`; the JSON block parses; LF kept | Local Canon (D-991) | as AC-10 | ✅ |
| AC-15 | integration | `capture-interactive.test.ts`: only line 14 changes; the file's tests pass, none skipped, among them the MEU-40 suite `MEU-40 AC-40.33 interactive request lifecycle`, whose `:82` and `:83` compare against `INBOX_PATH` (AC-40.33 is MEU-40's criterion, which the plan cites by its test title; it is not an AC of this plan) | Local Canon (D-992) | Row 6 (`dph-tests-check.txt`, `dph-ui-targeted.txt`); gate `edit-check-tests`, `ui-targeted` | ✅ |
| AC-16 | integration | `dev-spawn.test.ts`: only lines 8, 76, 77, 88 and 89 change; the file's tests pass, none skipped | Local Canon (D-992) | as AC-15 | ✅ |
| AC-17 | unit | Register scrub: in `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` only `root_cause` and `notes` change, to `~`; LF kept | Human-approved (D-817) | Row 7 (`dph-issue-resolve-7.txt`, `dph-register-check-7.txt`); gate `edit-check-register` | ✅ |
| AC-18 | integration | Both issues `resolved` with `verification` and `resolution_path`, each call bound to the hash before it; `render` and `render --check` exit 0 after each | Local Canon (D-994) | Rows 7 and 10 (`dph-issue-resolve-7.txt`, `dph-issues-render-check-7.txt`, `dph-issue-resolve-10.txt`, `dph-issues-render-check-10.txt`, `dph-register-check-10.txt`); gate `issues-render` | ✅ |
| AC-19 | unit | `commands.md`: exactly the `home-path` row is added after `task-contract`; CRLF kept; `test_framework_adoption.py` and `test_hdp_expert_pass.py` pass | Local Canon (D-988) | Row 8 (`dph-commands-check.txt`, `dph-adoption.txt`); gate `edit-check-commands`, `adoption-tests` | ✅ |
| AC-20 | integration | Repo Green: `CHECK` exits 0 with `allowlisted=60`; with an empty allow-list it exits 1 and its found files equal `EVIDENCE_SET` | Human-approved (D-817) | Row 9 (`dph-repo-green.txt`, `dph-repo-empty.txt`, `dph-repo-empty-check.txt`); row 10 (`dph-repo-green-2.txt`) | ✅ |
| AC-21 | integration | Gate: `home-path` exits 0 and `inventory-check` finds `ALLOW`'s SHA-256 equal to `allowlist.sha256`; H2-4 repeats both | Human-approved (D-817) | Gate steps `home-path` and `inventory-check` (H1-2); H2-4 after the review | ✅ (H1-2); H2-4 pending |
| AC-22 | integration | Encodings: six marked or unmarked UTF-16 and UTF-32 kinds in LF and CRLF found at `:3`; round 2's CJK fixture in unmarked UTF-16LE and BE found at `:3`; a PNG with NULs and no path passes with `nul=1`; the PNG with the path is found at `:4`; broken UTF-16 gives no traceback | Human-approved (D-817); Local Canon (D-988) | `test_check_home_path.py:450`, `:463`, `:478`, `:486`, `:497` | ✅ |
| AC-23 | integration | Digest binding: unchanged exempt; appended, byte-edited give `changed`; CRLF to LF still exempt; removed gives `stale`; `--prune` removes only a stale entry and leaves a `changed` entry byte-identical | Human-approved (D-817); Local Canon (D-997) | `test_check_home_path.py:553` (5 cases), `:565`, `:574` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-1 (12 cases) | FAILED: `assert False` where `is_file()` of `P:/av-kit/tools/check_home_path.py` | passed | `tests/tooling/test_check_home_path.py:208` |
| AC-2, AC-3 | FAILED, as above | passed | `test_check_home_path.py:234`, `:246` |
| AC-4 (12 cases) | FAILED, as above | passed | `test_check_home_path.py:279-328` |
| AC-5 (3 tests) | FAILED, as above | passed | `test_check_home_path.py:340-380` |
| AC-6 (5 cases), AC-7 | FAILED, as above | passed | `test_check_home_path.py:394-427` |
| AC-22 (5 tests) | FAILED, as above | passed | `test_check_home_path.py:450-497` |
| AC-23 (7 cases) | FAILED, as above | passed | `test_check_home_path.py:553-574` |

Red (row 1): `47 failed in 0.41s` (child exit 1, `dph-check-red.txt.exit`), and `red-check: 1 receipt(s), 9 required test(s), 0 problem(s)` with `--require test_ac_1` to `test_ac_7`, `test_ac_22` and `test_ac_23`. Every Red failure is the `CHECK.is_file()` assertion. Green (row 2): `47 passed in 6.64s`, no skip; `ruff check` on both files: `All checks passed!`.

The repository has its own Red and Green: row 4 ran `CHECK` with `ALLOW` before the fixes (`refused found=12 changed=0 stale=0`, equal to the 12 live pairs of row 0), and rows 9 and 10 ran it after them (`ok files=2484 allowlisted=60 nul=31`).

Receipts, all under `C:/Temp/av-kit/dph/`:
- row 0: `dph-baseline.txt` (`baseline: all steps exit 0`), `dph-base-py.txt`, `dph-base-ui.txt`, `dph-base-ui-full.txt`, `inventory-0.json`; the row-0 file copies in `base/`;
- rows 1 and 2: `dph-check-red.txt`, `dph-check-red.txt.exit`, `dph-check-red-check.txt`, `dph-check-green.txt`, `dph-check-lint.txt`;
- rows 3 and 4: `dph-allowlist-write.txt`, `dph-allowlist-check.txt`, `dph-repo-red.txt`, `dph-repo-red-check.txt`;
- rows 5 and 6: `dph-docs-check.txt`, `dph-tests-check.txt`, `dph-ui-targeted.txt`;
- row 7: `dph-issue-resolve-7.txt`, `dph-issues-render-check-7.txt`, `dph-register-check-7.txt`;
- row 8: `dph-commands-check.txt`, `dph-adoption.txt`;
- row 9: `dph-repo-green.txt`, `dph-repo-empty.txt`, `dph-repo-empty-check.txt`;
- row 10: `dph-issue-resolve-10.txt`, `dph-issues-render-check-10.txt`, `dph-register-check-10.txt`, `dph-repo-green-2.txt`;
- H1: `task-unchecked.txt` (H1-1); `dph-gate-h1.txt` and `dph-D6-*.txt`, one per gate step (H1-2); `dph-h13-focus.txt` and `dph-render-check.txt` (H1-3); `openapi-check.txt` (H1-4); `dph-h15-sources.txt` (H1-5); `handoff-check.txt` (H1-6), `handoff-ac-check.txt` (H1-6a) and `full-evidence-check.txt` (H1-6b).

Each row ran its task.md Validation cell verbatim, written into `C:/Temp/av-kit/dph/run-row` plus the row id plus `.ps1` after the row environment (`Set-Location P:/av-kit`, `ELECTRON_RUN_AS_NODE` cleared, `PYTHONIOENCODING=utf-8`, `PYTHONDONTWRITEBYTECODE=1`, `RECEIPTS_DIR=C:/Temp/av-kit`), and run as `pwsh -NoProfile -File`.

**The evidence set (D-989).** `EVIDENCE_SET` is 60 files: 16 handoffs (53 lines), 14 session digests (14 lines) and 30 plan-folder files (51 lines), 118 lines in all; no NUL file holds the path. D-989 added **no** file: no evidence file of Sessions 75 to 82 holds the path (the newest files that do are dated 2026-11-14), so every entry is from the plan's 2026-11-15 count. `allowlist.sha256` (row 3) is `7391b734e1dfe841d104f2b34a6923e6016f2890b1654d419cb1f75fbc9f3770`.

**Execution notes.** Each is a deviation from the plan, or a fact the plan did not foresee.

- **The plan's hash after its review.** The plan review approved the plan at SHA-256 `9b73511c…f41ff2b5`. After that, the plan's Status line was changed to quote Mat's execution words, so the plan executed is SHA-256 `f9b02aac8371d63dedd1f39b153d156ed308614e77fe288b63959c84aa61b71d` (LF, 687 lines), confirmed at row 0. Only the Status line differs. The `P:\av-kit\…` path it quotes is not the home folder, so it is not an S7 hit.
- **The dates.** The plan is dated 2026-11-15; it ran on 2026-11-17. The register's `last_checked` and `resolution_path` say 2026-11-17, the day the fix was made, not the plan's template date (D-1085).
- **Red-check's header pattern (D-1080).** The copied `red-check.py` takes the D-919 pytest header form, as Sessions 81 and 82 did (D-974, D-985), so a long parametrized title is one failure block.
- **Secret files are excluded (D-1081).** `CHECK`, `inventory.py` and the baseline's dirty-file walk never stat, open, hash or copy `.mcp.json`, `mcp-token.txt`, `.claude.json`, `.env`, `.env.*` or `.claude/settings.local.json`, as they never open `.agent/fleet/hub/`. AC-5's third test proves it.
- **The PNG fixture is found at `:4` (D-1082).** The PNG signature holds two LF bytes and the fixture's head ends with a third, so the path after them is on line 4, as AC-22 says.
- **Plan scripts are formatted (D-1083).** The plan-local scripts were run through `ruff format`; `ruff check --fix` removed one unused import from the copied `scope-check.py`. E501 is accepted in plan-local scripts, which no CI step lints. No logic changed.
- **One extra baseline receipt (D-1084).** Row 0 also ran the full Vitest suite into `dph-base-ui-full.txt` (`137 passed` files, `1578 passed` tests), so the gate's `ui-tests` step has a baseline to excuse against; it excused nothing.
- **The tests run `CHECK` by `sys.executable` (D-1086).** The test file starts `CHECK` with `sys.executable`, the interpreter `uv run pytest` already runs, as `test_check_commit_identity.py` does, not a nested `uv run`.
- **`CHECK` refuses an unreadable allow-list.** After the draft was placed, a `try`/`except` was added around the allow-list read, so an allow-list that exists but cannot be read exits 2 (`the allowlist cannot be read`) instead of a traceback. AC-4 and AC-6's no-traceback rule is the reason.
- **The gate's temp folders.** The gate's Python steps run with `TMP` and `TEMP` in the plan's temp folder, which keeps pytest's temp dirs away from the home folder; its `ui-*` steps run with the caller's `TMP` and `TEMP`, as row 0's baseline ran Vitest. The gate's `edit-check-register` step runs at stage 10, the register's final state.
- **Git's line-ending notice.** `git diff` prints "LF will be replaced by CRLF" for the LF files. That is git's existing `core.autocrlf` notice about the work tree; the bytes on disk are LF, as at base, measured with Python.
- **Scratch overwrite.** Row 10's run of `issue-resolve.py` overwrote the scratch copy `register-before-resolve.yaml` that row 7 had written; this is expected, and each call is bound to the hash before it (`register-row7.sha256` for row 10).
- **Receipts and the home folder.** No receipt, no new tracked file and nothing in this handoff holds the home folder's path. `CHECK` prints `path:line` only, and the edit scripts never print a line's text.

### Commands Executed

```json
{"schema_version": "evidence.v1", "check_id": "dph-row0-baseline", "command": "pwsh -NoProfile -File C:/Temp/av-kit/dph/run-row0.ps1 (task.md row 0 Validation cell, verbatim: rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-15-docs-path-hygiene/baseline.ps1 *> C:/Temp/av-kit/dph/dph-baseline.txt)", "cwd": "P:/av-kit", "scope": "Row 0: baseline.sha, baseline-dirty.txt and its hashes, baseline-scope.json, the row-0 copies, line endings, the inventory, the anchors, uv sync, the base Python and Vitest suites and the plan-local selftests", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 86ee8e3 (baseline.sha) plus the plan folder", "output": "baseline.sha 86ee8e31c4e3db29c45d1f316f350b9080b09d9f; kind live: files=6 lines=12; live pairs at row 0: 12 (the plan counted 12); base suite py 3035 passed, 37 warnings; base ui two files 22 passed; base suite ui 137 files, 1578 passed; red-check selftest: 39 fixture(s) (13 positive, 26 negative), 0 wrong; inventory selftest: 0 failure(s); edit-check selftest 0 failures; identity selftest: 0 failure(s); baseline: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "check_id": "dph-row1-check-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/dph/run-row1.ps1 (task.md row 1 Validation cell, verbatim: pytest tests/tooling/test_check_home_path.py into dph-check-red.txt, then red-check.py with --require for test_ac_1 to test_ac_7, test_ac_22 and test_ac_23)", "cwd": "P:/av-kit", "scope": "Red for AC-1 to AC-7, AC-22 and AC-23, before CHECK exists", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 86ee8e3 plus row 1", "output": "47 failed in 0.41s (child exit 1); last block: assert False where False = is_file() of P:/av-kit/tools/check_home_path.py. red-check: 1 receipt(s), 9 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "dph-row2-check-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/dph/run-row2.ps1 (task.md row 2 Validation cell, verbatim: pytest tests/tooling/test_check_home_path.py -rs into dph-check-green.txt, then ruff check on CHECK and the test into dph-check-lint.txt)", "cwd": "P:/av-kit", "scope": "Green for AC-1 to AC-7, AC-22 and AC-23 after CHECK was placed", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 86ee8e3 plus rows 1 and 2", "output": "47 passed in 6.64s, no SKIPPED; ruff: All checks passed!"}
```

```json
{"schema_version": "evidence.v1", "check_id": "dph-row3-allowlist", "command": "pwsh -NoProfile -File C:/Temp/av-kit/dph/run-row3.ps1 (task.md row 3 Validation cell, verbatim: inventory.py --write-allowlist into dph-allowlist-write.txt, then inventory.py --check-allowlist --cross-check into dph-allowlist-check.txt)", "cwd": "P:/av-kit", "scope": "AC-8: ALLOW written from EVIDENCE_SET with the row-0 digests, and the empty-list cross-check", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 86ee8e3 plus rows 1 to 3", "output": "entries of kind digest: 14; handoff: 16; plan-folder: 30; allow-list entries: 60; EVIDENCE_SET now: 60; CHECK with an empty allow-list: exit=1 found=130; inventory pairs=130; allowlist.sha256 matches; inventory: ok"}
```

```json
{"schema_version": "evidence.v1", "check_id": "dph-row4-repo-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/dph/run-row4.ps1 (task.md row 4 Validation cell, verbatim: CHECK into dph-repo-red.txt, then inventory.py --expect-live into dph-repo-red-check.txt)", "cwd": "P:/av-kit", "scope": "AC-9: the repository's Red, with ALLOW in place and the live files not yet fixed", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 86ee8e3 plus rows 1 to 4", "output": "check_home_path: found ui/tests/unit/dev-spawn.test.ts:89 (last of 12); check_home_path: refused found=12 changed=0 stale=0; repo Red found=12 LIVE_SET=12; inventory: ok"}
```

```json
{"schema_version": "evidence.v1", "check_id": "dph-row5-docs", "command": "pwsh -NoProfile -File C:/Temp/av-kit/dph/run-row5.ps1 (task.md row 5 Validation cell, verbatim: edit-check.py --group docs into dph-docs-check.txt)", "cwd": "P:/av-kit", "scope": "AC-10 to AC-14 after the five doc edits", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 86ee8e3 plus rows 1 to 5", "output": "docs/build-plan/06-gui.md: ok (CRLF; changed lines 960,975); docs/build-plan/07-distribution.md: ok (CRLF; lines 493 -> 492); README.md: ok (LF; changed lines 174,175); edit-check docs: ok files=5"}
```

```json
{"schema_version": "evidence.v1", "check_id": "dph-row6-tests", "command": "pwsh -NoProfile -File C:/Temp/av-kit/dph/run-row6.ps1 (task.md row 6 Validation cell, verbatim: edit-check.py --group tests into dph-tests-check.txt, then npm --prefix ui run test -- tests/unit/dev-spawn.test.ts tests/unit/capture-interactive.test.ts into dph-ui-targeted.txt)", "cwd": "P:/av-kit", "scope": "AC-15 and AC-16 after the two fixture edits", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "HEAD 86ee8e3 plus rows 1 to 6", "output": "ui/tests/unit/capture-interactive.test.ts: ok (LF; changed lines 14); ui/tests/unit/dev-spawn.test.ts: ok (LF; changed lines 8,76,77,88,89); edit-check tests: ok files=2; Test Files 2 passed (2); Tests 22 passed (22); no skip"}
```

```json
{"schema_version": "evidence.v1", "check_id": "dph-row7-register", "command": "pwsh -NoProfile -File C:/Temp/av-kit/dph/run-row7.ps1 (task.md row 7 Validation cell, verbatim: issue-resolve.py --issue INSTALL-FOLDER-NAME-MISMATCH with the two --scrub fields, issue_triage.py render, render --check, the register hash into register-row7.sha256, edit-check.py --group register --stage 7)", "cwd": "P:/av-kit", "scope": "AC-17 and AC-18, first call", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 86ee8e3 plus rows 1 to 7", "output": "issue-resolve: 0 problem(s); changed .issues[89].root_cause, .issues[89].notes and the resolved issue's status, verification and resolution_path; OK: known-issues.md is up-to-date; .agent/context/known-issues.yaml: ok (LF; stage 7); edit-check register --stage 7: ok files=1"}
```

```json
{"schema_version": "evidence.v1", "check_id": "dph-row8-commands", "command": "pwsh -NoProfile -File C:/Temp/av-kit/dph/run-row8.ps1 (task.md row 8 Validation cell, verbatim: edit-check.py --group commands into dph-commands-check.txt, then pytest tests/tooling/test_framework_adoption.py tests/tooling/test_hdp_expert_pass.py into dph-adoption.txt)", "cwd": "P:/av-kit", "scope": "AC-19 after the D6 row was inserted", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 86ee8e3 plus rows 1 to 8", "output": ".agent/docs/commands.md: ok (CRLF; lines 224 -> 225); edit-check commands: ok files=1; 106 passed in 74.63s"}
```

```json
{"schema_version": "evidence.v1", "check_id": "dph-row9-repo-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/dph/run-row9.ps1 (task.md row 9 Validation cell, verbatim: CHECK into dph-repo-green.txt, CHECK --allowlist with an empty file into dph-repo-empty.txt, inventory.py --expect-evidence into dph-repo-empty-check.txt)", "cwd": "P:/av-kit", "scope": "AC-20: the repository's Green, and the empty-list negative", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 86ee8e3 plus rows 1 to 9", "output": "check_home_path: ok files=2484 allowlisted=60 nul=31. Empty list: check_home_path: refused found=118 changed=0 stale=0; kind digest: files=14 lines=14; kind handoff: files=16 lines=53; kind plan-folder: files=30 lines=51; total: files=60 lines=118 nul_files=0; empty-list run found files=60 pairs=118 EVIDENCE_SET=60; inventory: ok"}
```

```json
{"schema_version": "evidence.v1", "check_id": "dph-row10-register", "command": "pwsh -NoProfile -File C:/Temp/av-kit/dph/run-row10.ps1 (task.md row 10 Validation cell, verbatim: issue-resolve.py --issue TRACKED-FILES-HOLD-HOME-PATH bound to register-row7.sha256, issue_triage.py render, render --check, edit-check.py --group register --stage 10, CHECK into dph-repo-green-2.txt)", "cwd": "P:/av-kit", "scope": "AC-18, second call, and CHECK once more", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 86ee8e3 plus rows 1 to 10", "output": "issue-resolve: 0 problem(s); OK: known-issues.md is up-to-date; .agent/context/known-issues.yaml: ok (LF; stage 10); edit-check register --stage 10: ok files=1; check_home_path: ok files=2484 allowlisted=60 nul=31"}
```

```json
{"schema_version": "evidence.v1", "check_id": "dph-h1-1-unchecked", "command": "pwsh -NoProfile -File C:/Temp/av-kit/dph/run-rowH1-1.ps1 (task.md row H1-1 Validation cell, verbatim)", "cwd": "P:/av-kit", "scope": "H1-1: no implementation row of task.md is unchecked", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 86ee8e3 plus rows 1 to 10", "output": "unchecked implementation rows: []"}
```

```json
{"schema_version": "evidence.v1", "check_id": "dph-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-15-docs-path-hygiene/session-gate.ps1 *> C:/Temp/av-kit/dph/dph-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/dph/dph-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','mismatch','session-gate:'; exit $code", "cwd": "P:/av-kit", "scope": "H1-2, the registered D6 gate on the whole tree after rows 0 to 10: identity, every static check (lint, task contract, scope, home-path, inventory-check, the four edit-checks, the red-check selftest, ui typecheck and lint), the targeted CHECK, Vitest and adoption tests, the full Python and Vitest suites, the state and issue renders, the closeout validator's selftest, then the identity again", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "86ee8e31c4e3db29c45d1f316f350b9080b09d9f+5f22c37d3ec1423901bd81e096bfefb4865c2cc961195253bea74208bd8af099", "output": "tools-lint All checks passed!; py-lint All checks passed!; task-contract OK: 27 row(s), 25 fully checked, 2 exempt (view_file): H1-5, H2-1; scope-paths HEAD 86ee8e3 = baseline.sha, files-modified 13, plan-or-closeout 17, scope-check: ok; home-path check_home_path: ok files=2485 allowlisted=60 nul=31; inventory-check CHECK with an empty allow-list: exit=1 found=118; inventory pairs=118; allowlist.sha256 matches; edit-check docs ok files=5, tests ok files=2, commands ok files=1, register --stage 10 ok files=1; red-check selftest: 39 fixture(s), 0 wrong; ui-types and ui-lint exit 0; home-path-tests 47 passed, no skip; ui-targeted 2 files, 22 passed; adoption-tests 106 passed; py-tests 3082 passed, 37 warnings in 248.21s (the base suite's 3035 plus this session's 47), baseline failures excused: 0; ui-tests 137 files, 1578 passed, excused: 0; state-render drift check passed (153 MEUs); issues-render OK; closeout-selftest 231 arm(s), 0 failure(s); tested_state before equals after; session-gate: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "check_id": "dph-h1-3-render", "command": "uv run python C:/Temp/av-kit/dph/apply-focus.py (the focus entry, CRLF kept), then pwsh -NoProfile -File C:/Temp/av-kit/dph/run-rowH1-3.ps1 (task.md row H1-3 Validation cell, verbatim: tools/meu_status.py render --check)", "cwd": "P:/av-kit", "scope": "H1-3: the current-focus entry on top, and the MEU SSOT render check (no MEU status changes)", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "86ee8e31c4e3db29c45d1f316f350b9080b09d9f+5f22c37d3ec1423901bd81e096bfefb4865c2cc961195253bea74208bd8af099", "output": "current-focus.md: bytes 76271 -> 77683, crlf 194 -> 197, bare_lf=0, tail unchanged: True; one wording fix after it: bytes 77683 -> 77713, crlf 197 -> 197, bare_lf 0; render --check: Drift check passed, SSOT loaded (153 MEUs, 12 phases), rendered regions match on-disk content"}
```

```json
{"schema_version": "evidence.v1", "check_id": "dph-h1-4-openapi-skip", "command": "pwsh -NoProfile -File C:/Temp/av-kit/dph/run-rowH1-4.ps1 (task.md row H1-4 Validation cell, verbatim)", "cwd": "P:/av-kit", "scope": "H1-4: nothing under packages/api changed, so the OpenAPI check is skipped on that basis", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "86ee8e31c4e3db29c45d1f316f350b9080b09d9f+5f22c37d3ec1423901bd81e096bfefb4865c2cc961195253bea74208bd8af099", "output": "packages/api paths that differ from baseline.sha: 0 still at their row-0 content: 0 changed in this session: []"}
```

### Quality Gate Results

`dph-gate-h1-2` is the fresh full record, and its last line is:

> session-gate: all steps exit 0

| Step | Stage | Result |
|------|-------|--------|
| identity-before / identity-after | identity | `tested_state` `86ee8e31c4e3db29c45d1f316f350b9080b09d9f+5f22c37d3ec1423901bd81e096bfefb4865c2cc961195253bea74208bd8af099` both times |
| tools-lint | static | `All checks passed!` (`ruff check` on `CHECK` and its test) |
| py-lint | static | `All checks passed!` (`ruff check packages/ tests/`) |
| task-contract | static | `OK: 27 row(s)`; 25 fully checked; 2 exempt (`view_file`): H1-5, H2-1 |
| scope-paths | static | HEAD `86ee8e3` equals `baseline.sha`; 13 Files Modified paths, 17 plan or closeout files; `scope-check: ok` |
| home-path | static | `check_home_path: ok files=2485 allowlisted=60 nul=31` (AC-21) |
| inventory-check | static | empty allow-list `exit=1 found=118`, inventory pairs 118; `allowlist.sha256 matches`; `inventory: ok` (AC-8, AC-21) |
| edit-check-docs, -tests, -commands, -register | static | `ok files=5`, `ok files=2`, `ok files=1` (224 to 225 lines), `--stage 10 ok files=1` |
| red-check-selftest | static | 39 fixtures (13 positive, 26 negative), 0 wrong |
| ui-types, ui-lint | static | `tsc --noEmit` and `eslint --max-warnings 0` exit 0 |
| home-path-tests | targeted | `47 passed`, no skip |
| ui-targeted | targeted | 2 files, `22 passed` |
| adoption-tests | targeted | `106 passed` |
| py-tests | full | `3082 passed, 37 warnings` (the base suite's 3035 plus this session's 47); baseline failures excused: 0 |
| ui-tests | full | 137 files, `1578 passed`, as at base; excused: 0 |
| state-render | full | drift check passed (153 MEUs, 12 phases) |
| issues-render | full | `OK: known-issues.md is up-to-date` |
| closeout-selftest | full | `RESULT: 231 arm(s), 0 failure(s)` |

Skipped by design, as the plan's §Session gate says: `py-types`, `ui-build` and `ui-electron` (no source change), the MCP steps, `openapi` (H1-4) and `build-record`.
`files=2485` here against `2484` in rows 9 and 10: the gate script `session-gate.ps1` was written after row 10.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `tools/check_home_path.py` | new | `CHECK`; LF, standard library |
| `tools/home_path_allowlist.txt` | new | `ALLOW`: 7-line header, 60 entries; LF |
| `tests/tooling/test_check_home_path.py` | new | AC-1 to AC-7, AC-22, AC-23; 47 cases; LF, 580 lines |
| `.agent/skills/git-workflow/SKILL.md` | modified | Line 153: the home folder becomes `~`; CRLF |
| `_inspiration/capture-crop/design.md` | modified | Line 205: the home folder becomes `C:/Users/YOU`; LF |
| `docs/build-plan/06-gui.md` | modified | Lines 960 and 975: `~/Downloads/av-kit…` and `~/Documents/Transcripts…`, padded to the old width; CRLF |
| `docs/build-plan/07-distribution.md` | modified | Line 40 `Programs/av-kit-ui`; the seven `extra/` lines become six (D-996); CRLF |
| `README.md` | modified | Lines 174 and 175: `Programs\\av-kit-ui\\`; LF |
| `ui/tests/unit/capture-interactive.test.ts` | modified | `INBOX_PATH` (line 14) uses `C:/Users/avkit`; LF |
| `ui/tests/unit/dev-spawn.test.ts` | modified | Lines 8, 76, 77, 88, 89 use `C:/Users/avkit`; LF |
| `.agent/docs/commands.md` | modified | The `home-path` D6 row after `task-contract` (+1); CRLF |
| `.agent/context/known-issues.yaml` | modified | The scrub (`CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR`) and the two resolutions; LF |
| `.agent/context/known-issues.md` | modified | Rendered by `issue_triage.py render`; LF |
| `.agent/context/current-focus.md` | modified | This session's entry on top (H1-3); CRLF kept, the rest unchanged |
| Plan folder: `baseline.ps1`, `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `allowlist.sha256`, `register-row7.sha256`, `red-check.py`, `identity.py`, `scope-check.py`, `inventory.py`, `edit-check.py`, `issue-resolve.py`, `session-gate.ps1`, `task.md` (rows marked) | new or modified | The plan's records, oracles and gate |

Each modified file keeps its row-0 line endings on every line, measured as bytes; every new file is LF.

```diff
-# e.g. %LOCALAPPDATA%/Programs/av-kit
+# e.g. %LOCALAPPDATA%/Programs/av-kit-ui
```

```diff
-        "command": "C:\\Users\\...\\AppData\\Local\\Programs\\av-kit\\resources\\...",
+        "command": "C:\\Users\\...\\AppData\\Local\\Programs\\av-kit-ui\\resources\\...",
```

```diff
+| home-path | static | `uv run python tools/check_home_path.py` | Every session: tracked and untracked (not ignored) files outside .agent/fleet/hub; allow-list tools/home_path_allowlist.txt (D-817); exit 0 ok, 1 an instance or a stale entry, 2 usage; maintainer host only, CI's home differs |
```

---

## Codex Validation Report

Transcribed from the canonical review, `.agent/context/handoffs/2026-11-15-docs-path-hygiene-implementation-critical-review.md` (Codex, `codex-independent-reviewer`, loop `dph-execution-2026-11-15-docs-path-hygiene`, opened with `tokens=off`). The reviewer wrote the verdict; this section only records it.

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|

None. Round 1 of 6 reported 0 findings and 0 blocking; intent achieved: yes.

Reviewer notes:
- **Install folder (Q1):** the reviewer traced electron-builder's own folder choice (`NsisTarget.js:270`, `targetUtil.js:40-41`) to the package name, so `Programs/av-kit-ui` is right and `av-kit.exe` stays. The new layout matches `ui/electron-builder.yml:32-35,52-53`. A scan of the README and the Markdown under `docs/build-plan/`, `.agent/docs/` and `_inspiration/` found no wrong-folder reference left.
- **CHECK (Q2):** independent probes found all 12 forms in ten encodings (120 cases) and rejected five near misses. Scratch runs gave unchanged 0, edited 1, stale 1, malformed 2 and missing entry 1. An unreadable allow-list exits 2 with no traceback. The hub and secret exclusion runs before any stat or read. The reviewer notes the approved limits: the check is a maintainer-host gate, not a general identity detector.
- **Evidence (Q3):** every one of the 60 digests was recomputed and agrees with `ALLOW` and `inventory-0.json`. Each evidence file matches its HEAD blob after git's line-ending normalization. The empty-list run equals row 0's 118 pairs in 60 files exactly.
- **Live fixes (Q4):** the repo Red equals the 12-pair `LIVE_SET`. All four edit-check groups pass, and the ten row-0 copies match their pinned hashes and HEAD. No test expectation was weakened, and `capture-interactive.test.ts:82-83` still compares `INBOX_PATH`.
- **Red, Green and gate (Q5):** Red is the intended missing-`CHECK` assertion (47 failures, child exit 1). IR-5 grades are Strong for every AC test group. The 23 gate steps and their counts were confirmed from the receipts. D-1080 to D-1086 are sound, and the disclosed deviations do not weaken the evidence. Suites, builds and Electron were not rerun by the reviewer.
- **Register (Q6):** the hash chain base `66f97171…` to row 7 `768a4b61…` to the current `ca80ae7e…` holds, and `render --check` passes.
- **Safety and state (Q7):** with one process-local `core.excludesFile` holding the `.claude/settings.local.json` rule, the unchanged `identity.py --state-only` returns the gate's `tested_state` exactly. The plan folder and the handoff and review files are LF, with no home-folder path and no email address. HEAD is the baseline and the index is clean.

Ledger: `OK: recorded round 1 verdict=approved agent='codex-independent-reviewer' blocking=0 intent_achieved=yes`. H1-7a: `OK: review_mode=execution; round 1 of 6; verdict=approved; open findings=0`. H1-7b: `OK: approved at round 1 of 6, 0 open blocking findings`. Review rounds: plan 3, execution 1.

### Verdict

`approved` (round 1 of 6, 0 findings). The approval does not authorize a commit or a push; the commit is Mat's call.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| CI coverage of `CHECK` and its test | out-of-scope | — | D-988: another machine's home folder differs, so the check runs in the local gate only; `.github/workflows/ci.yml` ignores `tests/tooling` |
| AC-21's H2-4 repeat | sequenced | — | H2-4 runs after the review, the reflection and the metrics exist |
| Commit and push | out-of-scope | — | Mat's call; H2-5 only prepares the message |

**Flags for Mat.** The plan's Status line changed after the plan review approved (hash above). D-989 added no file. `current-focus.md` is shared: Session 83's entry sits above Session 82's.

---

## Decision Log

```yaml
decision_log:
  - id: D-1080
    stage: execution
    question: "Which pytest failure-header pattern does the copied red-check.py use?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "The D-919 form: one or more underscores on each side of the title, so a long parametrized title is one failure block"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-11-15-docs-path-hygiene/red-check.py:82-85 — the pattern and its history", "D-974 and D-985 — Sessions 81 and 82 took the same form"]
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. AC-1's parametrized titles are wider than the terminal, and pytest then frames them with one underscore; the older pattern split them, so red-check would miss a required test. Two sessions already took this form. Keeping the older pattern lost because it splits this session's titles."
  - id: D-1081
    stage: execution
    question: "Do CHECK, inventory.py and the baseline's dirty-file walk read the secret files?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "No: .mcp.json, mcp-token.txt, .claude.json, .env, .env.* and .claude/settings.local.json are dropped by name before any stat or read, as .agent/fleet/hub/ is"
    source_tag: Local Canon
    precedents: ["AGENTS.md and the session brief — the secret files are never opened", "tools/check_home_path.py:123-132 — the hub and secret-name exclusion", "tests/tooling/test_check_home_path.py:380 — the reader is patched to fail on any secret path"]
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The check opens every tracked and untracked file, and some of these may be untracked and not ignored on a host, so without the rule the gate would read a token file. A secret file holds no home path that ships, because none is tracked. Scanning them lost because opening them breaks the standing rule."
  - id: D-1082
    stage: execution
    question: "On which line is the path in AC-22's PNG fixture found?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Line 4: the PNG signature holds two LF bytes and the fixture's head ends with a third, so the path after them is on line 4"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-11-15-docs-path-hygiene/implementation-plan.md:296 — AC-22, the path after the fourth newline is found at :4", "tests/tooling/test_check_home_path.py:486"]
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The test counts lines the way CHECK does, by LF bytes, and the fixture is built to match AC-22's wording. Moving the path to another line lost because AC-22 names :4."
  - id: D-1083
    stage: execution
    question: "Are the plan-local scripts formatted and linted like repository code?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "They are run through ruff format and ruff check --fix (which removed one unused import from the copied scope-check.py); E501 is accepted in them"
    source_tag: Local Canon
    precedents: ["pyproject.toml — line-length 100", ".github/workflows/ci.yml — CI lints packages/, tests/ and one tool, not plan folders"]
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. Formatting keeps the copies readable and the unused import was dead. Long lines in the plan scripts hold embedded commands and paths that read worse when split, and no gate lints the folder. Rewrapping every long line lost on that cost; no logic changed."
  - id: D-1084
    stage: execution
    question: "What baseline does the gate's ui-tests step excuse against?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Row 0 also runs the full Vitest suite into dph-base-ui-full.txt; ui-tests excuses only ids failing there (none did)"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-11-15-docs-path-hygiene/implementation-plan.md:458 — py-tests and ui-tests excuse only ids that row 0's receipts show failing", "docs/execution/plans/2026-11-15-docs-path-hygiene/baseline.ps1:193-199"]
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The plan names a row-0 receipt for ui-tests but row 0's listed steps ran only the two files, so without this receipt the excuse rule had nothing to read. A missing receipt excuses nothing, so the gate stays strict either way."
  - id: D-1085
    stage: execution
    question: "Which date do the register's last_checked and resolution_path carry?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "2026-11-17, the day the rows ran, not the plan's 2026-11-15 template date"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-11-15-docs-path-hygiene/task.md:56 — row 7 asks for today's last_checked", ".agent/context/known-issues.yaml — every resolved issue records the day it was checked"]
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The row asks for today's date, and a register that records a check two days before it ran would be false. Copying the template's date lost for that reason."
  - id: D-1086
    stage: execution
    question: "How does the test file start CHECK?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "With sys.executable, the interpreter uv run pytest already runs, not a nested uv run"
    source_tag: Local Canon
    precedents: ["tests/tooling/test_check_commit_identity.py — the peer starts its tool with sys.executable"]
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-15 'like we did here. But use the new HDP process.'. The peer test does it this way, it runs the same environment, and it is faster across 47 cases. A nested uv run lost because it adds a second resolve per case and can pick a different interpreter."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-17 | claude-code-local (Claude Opus 5.5) | Initial handoff after H1-2, H1-3 and H1-4; for the H1-7 execution review |
| Reviewed | 2026-11-17 | codex (H1-7 execution review) | Approved at round 1 of 6 with 0 findings; Codex Validation Report transcribed by claude-code-local |
