---
date: "2026-11-27"
project: "2026-11-26-ytdlp-challenge-and-cookie-test"
meu: "MEU-168"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/implementation-plan.md"
build_plan_section: "docs/build-plan/02-infrastructure.md §yt-dlp challenge solver (residual) (MEU-168, matrix 2.10)"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-22-tray-show-and-baseline-fixes-MEU-164-handoff.md"
---

# Handoff: 2026-11-26-ytdlp-challenge-and-cookie-test-MEU-168-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-168 yt-dlp challenge solver (phase 2, matrix 2.10), from `YTDLP-CHALLENGE-SOLVE-FAILS`, grouped as Session 104 with MEU-169 and MEU-170 (grouping D-1410 to D-1412). This handoff is the first of three: MEU-168 → [MEU-169](2026-11-26-ytdlp-challenge-and-cookie-test-MEU-169-handoff.md) → [MEU-170](2026-11-26-ytdlp-challenge-and-cookie-test-MEU-170-handoff.md).
**Build Plan Section**: `docs/build-plan/02-infrastructure.md` §yt-dlp challenge solver (residual), with its `Delivered (Session 104)` note (row 18).
**Predecessor**: [2026-11-22-tray-show-and-baseline-fixes-MEU-164-handoff.md](2026-11-22-tray-show-and-baseline-fixes-MEU-164-handoff.md). Session 104 ran from `c0acc89` (`baseline.sha`), and `HEAD` did not move.

- **The lock (`YTDLP_LOCK`, D-1460).** `uv.lock` moves yt-dlp from 2026.10.26 to 2026.11.23, and `packages/infrastructure/pyproject.toml` sets the floor `yt-dlp>=2026.11.23`. yt-dlp-ejs stays 0.8.0, the version the release pins (`lock: versions {'yt-dlp': '2026.11.23', 'yt-dlp-ejs': '0.8.0'}; hold-override: yes`, `ycc-row3-lock-diff.txt`). `tests/unit/test_ytdlp_lock.py` holds the lock to it.
- **The hold (`HOLD_OVERRIDE`, D-1468, D-1490).** uv's 7-day `exclude-newer` refused 2026.11.23 at row 3, so the root `[tool.uv]` gained `exclude-newer-package = { yt-dlp = false }` (`ycc-hold.txt`: `hold-override: yes`). It must be removed, and `uv lock` run again, after 2026-11-30.
- **Which of the two was needed: the version.** The `player_js_variant` fallback was not needed (D-1461): yt-dlp 2026.11.23's own default player variant is `tv`, which is why the after-run prints `variant=tv` although av-kit sets no `player_js_variant` (guard `test_ac_168_6_adapter_sets_no_player_js_variant`). Rows 5a and 5b were skipped as `fallback not needed`.
- **The proof (`PROOF_PAIR`, D-1462).** The same video, run with `proof-extract.py` and no cookie source, ended `verdict=challenge-errors` with 0 formats on 2026.10.26 and `verdict=clean` with 11 formats on 2026.11.23. Row 5c: `proved`.
- **Records.** MEU-168 is `ready_for_review`; `YTDLP-CHALLENGE-SOLVE-FAILS` is resolved, with the hold-line follow-up in its resolution text; 02 §yt-dlp challenge solver carries the Delivered note.

**What Mat sees.** Downloads that stopped with YouTube's challenge errors work again: the app ships yt-dlp 2026.11.23, which solves the current n and signature challenges, and the packaged backend lists it. Nothing in the app's screens changes. One line in `pyproject.toml` is to be removed after 2026-11-30.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/implementation-plan.md) §Single-statement contracts. **Execution authorization:** `USER_EXPLICIT`, 2026-11-26 ("drafts stand, go for 104 after the reviews finish and then execute rest as you see fit. Use HDP for decisions and pick recommendations as expect and do not stop for human decisions on techincal metters that are settled as primary recommendation for any of the 4 executions."); the same words approve the six moved assertions of rows 7 and 11 (M-7). The plan review approved at round 1 of loop `ycc-plan-2026-11-26-ytdlp-challenge-and-cookie-test` with no findings (`.agent/context/handoffs/2026-11-26-ytdlp-challenge-and-cookie-test-plan-critical-review.md`). Receipts named by file name alone are in the session's receipts folder (the `2026-11-26-ytdlp-challenge-and-cookie-test` folder under `RECEIPTS_DIR`); the mini-air run folders are under its `e2e-remote` folder.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-168.1 | unit | `YTDLP_LOCK`: the lock holds yt-dlp 2026.11.23 or later, yt-dlp-ejs 0.8.0 and the floor `yt-dlp>=2026.11.23`; `row-check.py lock` finds only the yt-dlp package, its requirement and the hold option changed | Research-backed (yt-dlp issue 18123, PyPI 2026.11.23); D-1460, D-1468 | `tests/unit/test_ytdlp_lock.py:70`; negative `:74`; `ycc-row3-lock-diff.txt`, `ycc-row3-installed.txt` | ✅ |
| AC-168.2 | unit | The yt-dlp/yt-dlp-ejs pin test still runs and passes, at its baseline hash | Human-approved D-640 | `tests/unit/test_fetch_deno.py` (`ycc-row4-pins.txt`: `ok`) | ✅ |
| AC-168.3 | integration | The adapter, client fallback, extract option and JS runtime suites pass on 2026.11.23 at their baseline hashes | Local Canon (home Tests row) | `ycc-row4-suites.txt`: `139 passed in 26.20s`; `ycc-row4-pins.txt` | ✅ |
| AC-168.4 | script | `proof-extract.py` holds no cookie option, prints only the named lines, and `--selftest` proves each verdict | Local Canon; D-464 A; D-1462 | `docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/proof-extract.py --selftest` (`ycc-proof-selftest.txt`: `proof-extract selftest: 11 classify cases, 4 emit cases, 0 failure(s)`) | ✅ |
| AC-168.5 | script | The pair: 2026.10.26 ends `verdict=challenge-errors`, 2026.11.23 ends `verdict=clean` | Local Canon; D-1462 | `ycc-proof-before.txt`, `ycc-proof-after.txt`, `ycc-row5c-verdict.txt` (`proved`) | ✅ |
| AC-168.6 | unit | `VARIANT_FALLBACK`: the adapter builds no `player_js_variant`; the handoff records that the version, not the fallback, was needed | Research-backed (pull request 18124, `_video.py` at 2026.11.23); D-1461 | `tests/unit/test_ytdlp_lock.py:131`; `ycc-row5-classify.txt` | ✅ (passed at Red: guard) |
| AC-168.7 | packaged | The packaged backend passes `smoke_packaged_runtime.py` (bundled Deno, solver imports) and the licence list names yt-dlp 2026.11.23 | Local Canon; 02 `RUNTIME_SMOKE`; 07 `LICENCE_LIST` | `ycc-row6-smoke.txt`: `PASS: smoke-runtime source=bundled version=2.9.8 solver=True`; `ycc-licences.txt:15576` `yt-dlp 2026.11.23`; `ycc-row6-licence-check.txt` | ✅ |
| AC-168.8 | check | Reach: no version file, release note or tag changed; nothing uploaded or published | Local Canon; D-1407; E5 | gate `scope-paths` (`ycc-D6-scope-paths.txt`) | ✅ |
| AC-159.3 to AC-159.5, AC-51.6, AC-81.13 (cross-ref) | guard | Unchanged guards that this session's plan cites; not criteria of MEU-168 | Local Canon | gate `pins-unchanged`, `ui-tests`, `py-tests`; row 17 `AC-159 4` | ✅ |
| AC-53.2 (cross-ref) | guard | A precedent that D-1499 cites: a click right after a cookie setting persists must still act, so Test Cookies has its own busy state and not the page's shared one; unchanged, not a criterion of this plan | Local Canon; D-1499 | `ui/tests/unit/downloader-page.behavior.test.ts:1282`, `:1304`, `:1331`; gate `ui-tests` | ✅ |
| AC-169 (cross-ref) | sibling | This plan's AC-169 criteria belong to MEU-169; that handoff carries their Red and Green evidence, and this handoff claims none of them | the plan | see the MEU-169 handoff | cross-ref |
| AC-170 (cross-ref) | sibling | This plan's AC-170 criteria belong to MEU-170; that handoff carries their Red and Green evidence, and this handoff claims none of them | the plan | see the MEU-170 handoff | cross-ref |
| AC-138 (cross-ref) | sibling | This plan's AC-138 criteria belong to MEU-169 and MEU-170 (the moved AC-138.8 pins); that handoff carries their Red and Green evidence, and this handoff claims none of them | the plan | see the MEU-169 handoff | cross-ref |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-168.1 `test_ac_168_1_lock_holds_the_fixed_release` | `Left contains 2 more items, first extra item: 'the lock holds yt-dlp 2026.10.26, before 2026.11.23'` (`ycc-row2-red.txt`, `1 failed, 2 passed in 0.31s`) | Row 3: `3 passed in 0.56s` (`ycc-row3-green.txt`) | `tests/unit/test_ytdlp_lock.py:70` |

`test_ac_168_1_helper_refuses_an_old_lock` and `test_ac_168_6_adapter_sets_no_player_js_variant` passed at Red and are guards. AC-168.4, AC-168.5 and AC-168.7 are script and packaged checks, AC-168.8 a scope check.

- **Row 1, the before-run** (`ycc-proof-before.txt`), as printed:

```text
yt-dlp=2026.10.26
yt-dlp-ejs=0.8.0
deno=2.9.8 (bundled)
clients=tv,web_safari,web
player=b485e332
variant=main
challenge=n-challenge:1 signature:1 dispose-callback:1 page-reload:2
formats=0
verdict=challenge-errors
```

- **Row 5, the after-run** (`ycc-proof-after.txt`), as printed:

```text
yt-dlp=2026.11.23
yt-dlp-ejs=0.8.0
deno=2.9.8 (bundled)
clients=tv,web_safari,web
player=b485e332
variant=tv
challenge=n-challenge:0 signature:0 dispose-callback:0 page-reload:0
formats=11
verdict=clean
```

- **The pair**: `proof-pair: before challenge-errors, after clean (variant tv): proved` (`ycc-row5-classify.txt`); row 5c `proof-pair: before challenge-errors, last run (after) clean: proved` (`ycc-row5c-verdict.txt`). Rows 5a and 5b: `skipped: fallback not needed`.
- **Row 3, the lock** (`ycc-row3-lock.txt`): uv printed `Updated yt-dlp v2026.10.26 -> v2026.11.23` and `Resolving despite existing lockfile due to addition of exclude newer exclusion for package \`yt-dlp\``. The lock diff (`git diff --ignore-cr-at-eol uv.lock`):

```diff
+[options.exclude-newer-package]
+yt-dlp = false
-    { name = "yt-dlp" },
+    { name = "yt-dlp", specifier = ">=2026.11.23" },
-version = "2026.10.26"
+version = "2026.11.23"
```

  plus the sdist and wheel URLs and hashes of 2026.11.23 in place of 2026.10.26.
- **Row 6, packaged**: `tools/package_backend.py` built `packaging/dist/avkit-backend` (`ycc-row6-package.txt`); `PASS: smoke-runtime source=bundled version=2.9.8 solver=True` (`ycc-row6-smoke.txt`); the licence list holds `yt-dlp 2026.11.23` and `yt-dlp-ejs 0.8.0` (`ycc-licences.txt`), `licence: 0 title(s) missing` (`ycc-row6-licence-check.txt`); licence tests `64 passed in 5.26s` (`ycc-row6-licence-tests.txt`).

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "ycc-0-baseline", "command": "pwsh -NoProfile -File docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-run.ps1 -Row 0 (task.md row 0's Validation cell); receipts C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-row0*.txt, ycc-base-*.txt", "scope": "Row 0: the baseline at c0acc89, the scope and line-ending records, the free-id check, the plan-local selftests and the base suites", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD c0acc89 (baseline.sha) plus rows 0 to 0", "output": "row 0: all steps exit 0. ycc-base-py.txt: 3348 passed, 37 warnings in 310.90s (0:05:10). ycc-base-mcp.txt: Tests  554 passed (554)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "ycc-1-2-3-lock", "command": "pwsh -NoProfile -File docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-run.ps1 -Row 1, -Row 2, -Row 3; receipts C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-row1*.txt, ycc-row2*.txt, ycc-row3*.txt, ycc-proof-before.txt", "scope": "AC-168.1 Red then Green; the before-run on 2026.10.26", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD c0acc89 (baseline.sha) plus rows 0 to 3", "output": "ycc-proof-before.txt: verdict=challenge-errors. ycc-row2-red.txt: 1 failed, 2 passed in 0.31s. ycc-row3-green.txt: 3 passed in 0.56s. ycc-row3-lock-diff.txt: lock: versions {'yt-dlp': '2026.11.23', 'yt-dlp-ejs': '0.8.0'}; hold-override: yes; row-check lock: 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "ycc-4-5-6-proof", "command": "pwsh -NoProfile -File docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-run.ps1 -Row 4, -Row 5, -Row 5a, -Row 5b, -Row 5c, -Row 6; receipts C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-row4*.txt to ycc-row6*.txt, ycc-proof-*.txt, ycc-licences.txt", "scope": "AC-168.2 to AC-168.7", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD c0acc89 (baseline.sha) plus rows 0 to 6", "output": "ycc-row4-suites.txt: 139 passed in 26.20s. ycc-proof-after.txt: variant=tv; formats=11; verdict=clean. ycc-row5c-verdict.txt: proof-pair: before challenge-errors, last run (after) clean: proved. ycc-row6-smoke.txt: PASS: smoke-runtime source=bundled version=2.9.8 solver=True. ycc-row6-licence-check.txt: licence: 0 title(s) missing"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "ycc-18-19-canon-register", "command": "pwsh -NoProfile -File docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/row-run.ps1 -Row 18, then -Row 19; receipts C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-row18*.txt, ycc-row19*.txt", "scope": "Rows 18 and 19: the §Spec text in 01, 02, 04 and 06; the three issues resolved; MEU-168 to MEU-170 ready_for_review; the grouping row", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD c0acc89 (baseline.sha) plus rows 0 to 19", "output": "ycc-row18-check.txt: row-check canon: 0 problem(s). ycc-row18-eol.txt: eol-check: 45 scope path(s), 0 problem(s). ycc-row19-register.txt: row-check register: 0 problem(s). ycc-row19-render-check.txt: ✅ Drift check passed — SSOT loaded (174 MEUs, 12 phases), rendered regions match on-disk content. ycc-row19-grouping.txt: grouping: row 104 now reads executed (Session 104)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "ycc-h1-2-gate", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/session-gate.ps1 *> C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-gate-h1.txt (task.md row H1-2's Validation cell); step receipts C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-D6-*.txt", "scope": "H1-2: the registered verification plan: identity before and after; static; openapi; fresh full with nothing deselected (py-tests, ui-tests, mcp-tests, ui-build, state-render, issues-render); e2e-remote bound to row 16's run", "phase": "full", "exit_code": 0, "result": "pass", "tested_state": "c0acc89e8b0eda65dd9dcaa2c008e03af35e33b4+c567b60166cced52337673de4040a0ec1fa705509e6dfdb24da13d8668083a10", "fresh": true, "snapshot": false, "output": "ycc-gate-h1.txt: tested_state before=c0acc89e8b0eda65dd9dcaa2c008e03af35e33b4+c567b60166cced52337673de4040a0ec1fa705509e6dfdb24da13d8668083a10 after=c0acc89e8b0eda65dd9dcaa2c008e03af35e33b4+c567b60166cced52337673de4040a0ec1fa705509e6dfdb24da13d8668083a10; session-gate: all steps exit 0. ycc-D6-py-tests.txt: 3358 passed, 37 warnings in 691.20s (0:11:31). ycc-D6-ui-tests.txt: Tests  1684 passed (1684). ycc-D6-mcp-tests.txt: Tests  557 passed (557). ycc-D6-e2e-remote.txt: row-check e2e-result: 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "ycc-h1-2-recheck", "command": "uv run --no-sync python docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/identity.py --state-only with ELECTRON_RUN_AS_NODE unset; receipt C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-identity-recheck-h1-2.txt", "scope": "H1-2: the gate's tested_state re-derived after the gate process exited", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "c0acc89e8b0eda65dd9dcaa2c008e03af35e33b4+c567b60166cced52337673de4040a0ec1fa705509e6dfdb24da13d8668083a10", "output": "ycc-identity-recheck-h1-2.txt: c0acc89e8b0eda65dd9dcaa2c008e03af35e33b4+c567b60166cced52337673de4040a0ec1fa705509e6dfdb24da13d8668083a10, equal to the gate's tested_state"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "ycc-h1-3-focus", "command": "uv run --no-sync python of the H1-3 focus script (a byte write that keeps CRLF), then pwsh -NoProfile -File of task.md row H1-3's Validation cell; receipts C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-h13-*.txt", "scope": "H1-3: MEU-168, MEU-169 and MEU-170 ready_for_review from row 19 with no new status write; the Session 104 entry on top of current-focus.md", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "c0acc89e8b0eda65dd9dcaa2c008e03af35e33b4+c567b60166cced52337673de4040a0ec1fa705509e6dfdb24da13d8668083a10", "output": "ycc-h13-render.txt: ✅ Drift check passed — SSOT loaded (174 MEUs, 12 phases), rendered regions match on-disk content. ycc-h13-status.txt: row-check status: 0 problem(s). ycc-rowH1-3.txt: row H1-3: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "ycc-h1-4-no-deselect", "command": "pwsh -NoProfile -File of task.md row H1-4's Validation cell; receipts C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-h14-*.txt", "scope": "H1-4: the OpenAPI drift gate on the final tree; the gate's py-tests step holds no --deselect and its receipt ends passed", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "c0acc89e8b0eda65dd9dcaa2c008e03af35e33b4+c567b60166cced52337673de4040a0ec1fa705509e6dfdb24da13d8668083a10", "output": "ycc-h14-openapi.txt: no output, exit 0 (ycc-h14-openapi.txt.exit: 0). ycc-h14-no-deselect.txt: row-check no-deselect: 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "ycc-h1-5-sources", "command": "view_file of .agent/context/handoffs/TEMPLATE.md and 2026-11-22-tray-show-and-baseline-fixes-MEU-164-handoff.md (also the newest handoff by mtime), with sha256 into C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/ycc-h15-source-read.txt", "scope": "H1-5: the template and the precedent read before this handoff", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "c0acc89e8b0eda65dd9dcaa2c008e03af35e33b4+c567b60166cced52337673de4040a0ec1fa705509e6dfdb24da13d8668083a10", "output": "ycc-h15-source-read.txt: 1e013a15c3cecfc3c290b051a6e1e6c0ed07ad661f14a936fe786a92d06702be TEMPLATE.md; ec11fe17b971033306a114929d00288c3b1840e1d930a97be6a84ded40e8fa0c 2026-11-22-tray-show-and-baseline-fixes-MEU-164-handoff.md; newest *-handoff.md by mtime: the MEU-164 handoff itself"}
```

### Quality Gate Results

On the final tree, from `identity-before` to `identity-after`, at `HEAD` `c0acc89`. The last line of `ycc-gate-h1.txt` is `session-gate: all steps exit 0`. The gate's `tested_state` is `c0acc89e8b0eda65dd9dcaa2c008e03af35e33b4+c567b60166cced52337673de4040a0ec1fa705509e6dfdb24da13d8668083a10`, and the identity re-derived after the gate exited is the same (`ycc-identity-recheck-h1-2.txt`). The gate ran three times. The first run (`ycc-gate-h1-r1.txt`, `ycc-D6-*-r1.txt`) stopped at `py-lint` on 25 `E501` lines, all in the `EDITS` block of `canon-edit.py` written at row 18 (Departures). The second run (`ycc-gate-h1-r2.txt`, `ycc-D6-*-r2.txt`) stopped at `py-tests`, `1 failed, 3357 passed`: Session 72's AC-106.5 delta refused the new cookie test schemas (D-1600, Departures). In both, every later step was `not_run`. The third run is the one below. No step excuses a test by name, reaches YouTube, or starts Electron on the dev PC.

| Step | Stage | Result | Decisive line | Receipt |
|------|-------|--------|---------------|---------|
| `identity-before` | identity | exit 0 | `tested_state c0acc89e8b0eda65dd9dcaa2c008e03af35e33b4+c567b60166cced52337673de4040a0ec1fa705509e6dfdb24da13d8668083a10` | `ycc-D6-identity-before.txt` |
| `py-types` | static | exit 0 | `0 errors, 0 warnings, 0 informations` | `ycc-D6-py-types.txt` |
| `py-lint` | static | exit 0 | `All checks passed!` | `ycc-D6-py-lint.txt` |
| `py-format` | static | exit 0 | `11 files already formatted` | `ycc-D6-py-format.txt` |
| `ui-types` | static | exit 0 | `> tsc --noEmit` | `ycc-D6-ui-types.txt` |
| `ui-lint` | static | exit 0 | `> eslint src/ tests/ --max-warnings 0` | `ycc-D6-ui-lint.txt` |
| `mcp-types` | static | exit 0 | `> tsc --noEmit && tsc -p tsconfig.scripts.json` | `ycc-D6-mcp-types.txt` |
| `task-contract` | static | exit 0 | `OK: 43 row(s); 10-column table (with builder_model); 41 row(s) fully checked: backticked, exit-code re-raised, receipt under RECEIPTS_DIR; dependencies resolve and are acyclic; 2 row(s) exempt (view_file): H1-5, H2-1` | `ycc-D6-task-contract.txt` |
| `scope-paths` | static | exit 0 | `row-check scope-paths: 0 problem(s)` | `ycc-D6-scope-paths.txt` |
| `line-endings` | static | exit 0 | `eol-check: 46 scope path(s), 0 problem(s)` | `ycc-D6-line-endings.txt` |
| `home-path` | static | exit 0 | `check_home_path: ok files=3027 allowlisted=60 nul=45` | `ycc-D6-home-path.txt` |
| `pins-unchanged` | static | exit 0 | `row-check pins-unchanged: 0 problem(s)` | `ycc-D6-pins-unchanged.txt` |
| `red-unchanged` | static | exit 0 | `row-check red-unchanged: 0 problem(s)` | `ycc-D6-red-unchanged.txt` |
| `kept` | static | exit 0 | `row-check kept: 0 problem(s)` | `ycc-D6-kept.txt` |
| `canon` | static | exit 0 | `row-check canon: 0 problem(s)` | `ycc-D6-canon.txt` |
| `row-steps` | static | exit 0 | `row-check steps: 0 problem(s)` | `ycc-D6-row-steps.txt` |
| `row-check-selftest` | static | exit 0 | `row-check selftest: 60 case(s), 0 wrong []` | `ycc-D6-row-check-selftest.txt` |
| `red-check-selftest` | static | exit 0 | `red-check selftest: 128 fixture(s) (37 positive, 91 negative), 0 wrong: []` | `ycc-D6-red-check-selftest.txt` |
| `eol-check-selftest` | static | exit 0 | `eol-check selftest: 24 case(s), 0 wrong: []` | `ycc-D6-eol-check-selftest.txt` |
| `proof-selftest` | static | exit 0 | `proof-extract selftest: 11 classify cases, 4 emit cases, 0 failure(s)` | `ycc-D6-proof-selftest.txt` |
| `identity-selftest` | static | exit 0 | `identity selftest: 0 failure(s)` | `ycc-D6-identity-selftest.txt` |
| `openapi` | openapi | exit 0 | `no output (exit 0 is the pass)` | `ycc-D6-openapi.txt` |
| `py-tests` | full | exit 0 | `3358 passed, 37 warnings in 691.20s (0:11:31)` | `ycc-D6-py-tests.txt` |
| `ui-tests` | full | exit 0 | `Tests  1684 passed (1684)` | `ycc-D6-ui-tests.txt` |
| `mcp-tests` | full | exit 0 | `Tests  557 passed (557)` | `ycc-D6-mcp-tests.txt` |
| `ui-build` | full | exit 0 | `✓ built in 5.34s` | `ycc-D6-ui-build.txt` |
| `state-render` | full | exit 0 | `✅ Drift check passed — SSOT loaded (174 MEUs, 12 phases), rendered regions match on-disk content` | `ycc-D6-state-render.txt` |
| `issues-render` | full | exit 0 | `OK: known-issues.md is up-to-date` | `ycc-D6-issues-render.txt` |
| `e2e-snapshot` | e2e-remote | exit 0 | `snapshot-commit verify: bound` | `ycc-D6-e2e-snapshot.txt` |
| `e2e-remote` | e2e-remote | exit 0 | `row-check e2e-result: 0 problem(s)` | `ycc-D6-e2e-remote.txt` |
| `identity-after` | identity | exit 0 | `tested_state c0acc89e8b0eda65dd9dcaa2c008e03af35e33b4+c567b60166cced52337673de4040a0ec1fa705509e6dfdb24da13d8668083a10` | `ycc-D6-identity-after.txt` |
| the gate | all | pass | `session-gate: all steps exit 0` | `ycc-gate-h1.txt` |

H1-4 (`ycc-h14-no-deselect.txt`): `row-check no-deselect: 0 problem(s)`.

---

## Changed Files

Counts are added / removed lines against `HEAD` `c0acc89` (`git diff --numstat --ignore-cr-at-eol HEAD`); a new file's count is its line count. Line endings were measured as bytes (the gate's `line-endings` step).

| File | Change | Added / removed | Line endings |
|------|--------|-----------------|--------------|
| `uv.lock` | yt-dlp 2026.11.23, its requirement and the hold option | +7 / -4 | LF kept |
| `packages/infrastructure/pyproject.toml` | `"yt-dlp"` → `"yt-dlp>=2026.11.23"` | +1 / -1 | CRLF kept |
| `pyproject.toml` | `exclude-newer-package = { yt-dlp = false }` (to remove after 2026-11-30) | +1 / -0 | LF kept |
| `tests/unit/test_ytdlp_lock.py` | AC-168.1 and the AC-168.6 guard | new, 146 | LF |
| `docs/build-plan/02-infrastructure.md` | the three Delivered notes and §Cookie test (row 18; MEU-168's note under §yt-dlp challenge solver) | +62 / -1 (with the triage's three homes) | CRLF kept |
| The shared records | see the MEU-169 handoff's Changed Files | | |

Nothing is committed or staged. `packaging/dist/` was rebuilt and is gitignored.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

### Verdict

`approved` at round 1 of loop `ycc-execution-2026-11-26-ytdlp-challenge-and-cookie-test`, `intent_achieved=yes`, 0 findings, 0 blocking (ledger `usage` 9,372,763; dispatch `ycc-exec-r1`, exit 0, receipts `C:/Temp/av-kit/dispatch/ycc-exec-r1/receipt.txt` and `ledger-record.txt`). The reviewer's `tested_state` matches the gate's. The report is `.agent/context/handoffs/2026-11-26-ytdlp-challenge-and-cookie-test-implementation-critical-review.md`. H1-7a: `OK: review_mode=execution; round 1 of 6; verdict=approved; open findings=0` (`review-state-check.txt`). H1-7b: `OK: approved at round 1 of 6, 0 open blocking findings` (`exec-review.txt`).

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| Removing the hold line and running `uv lock` again | follow-up | after 2026-11-30 | D-1468, D-1490 |
| Any `player_js_variant` other than `tv`, or another solver workaround | out-of-scope | — | Home Fallback row |
| Bumping `yt-dlp-ejs` or Deno | out-of-scope | — | Home Version row |
| The client lists, from which upstream took `web` (pull request 18131) | raised for Mat | triage | D-539, D-643 to D-646 |
| A release, a tag, an upload or a published build that ships the fix | out-of-scope | — | Home Reach row; M-1 is Mat's |
| Commit and push | out-of-scope | — | Only on Mat's direction (H2) |

### Departures and their basis

- **Execution decisions D-1470 to D-1499** (autonomous, in the plan's YAML; every reasoning starts with Mat's hand-over). D-1490: the 7-day hold refused 2026.11.23 at row 3, so the hold line was added. D-1491: the cookie test loads the jar with yt-dlp's public `load_cookies` into `ydl.cookiejar`, so a failure there is `unreadable` and a later one `check_failed`. D-1493: the browser-mode test never reads a real profile (`browser-probe: hits=[] pytest=0`). D-1494: the stale docstring above. D-1495: the schema uses the domain enum. D-1497: `cast(Any, ...)` types the `load_cookies` arguments. D-1498: the Electron spec routes with `page.route`. D-1499: the mini-air outage. D-1600: the AC-106.5 delta exemption (below). D-1600 follows D-1499 because Session 106 reserves D-1540 to D-1599. The other departures below are recorded here, not as decisions.
- **Reruns.** A rerun row kept its first receipts as `-r1`: rows 3, 8, 12 and 13 (each refused or failed before its fix and passed after), row 18 (`refused: EDITS not written`: D-1481 has the texts written at row 18, so its first run met the empty `EDITS` and wrote nothing), row 11a (the outage) and row 16 (the lost runner). No expectation was edited at Green (S3), and no existing test failed after a Green (S5).
- **Row 18's lint (gate run 1).** Row 18 wrote `canon-edit.py`'s `EDITS` with string lines up to 115 characters, which no row step lints; the gate's `py-lint` refused them (`ycc-D6-py-lint-r1.txt`: 25 `E501`, all in that block). The strings were re-wrapped to 100 columns and `ruff format` set their quotes; a check by `exec` showed the `EDITS` value equal before and after, and `row-check.py canon` still read `0 problem(s)`. No build-plan file changed, so row 18 was not re-run, and the whole gate was run again.
- **The AC-106.5 delta exemption (gate run 2, D-1600) — a departure for the execution reviewer.** Session 72's `docs/execution/plans/2026-11-14-capture-shapes-steps/openapi-delta.py` compares the whole OpenAPI document with `5db3623`, so the gate's `py-tests` failed at `tests/e2e/test_api_capture_shapes.py::test_ac_106_5_openapi_snapshot_and_delta` (`ycc-D6-py-tests-r2.txt`: `1 failed, 3357 passed`; `a change AC-106.5 doesn't name: /components/schemas/CookieTestOut/description`). The coordinator ruled option A under Mat's hand-over: `COOKIE_TEST_SHAPES` requires `CookieTestOut` and `CookieTestOutcome` to be both the base's or both exactly this session's committed shapes, and sets them back to the base's before the compare, as the rc4 row-7 `info.version` exemption does; two selftest cases were added (`openapi-delta selftest: 11 case(s), 0 wrong`). This changes another plan's check, which HDP §6 lists as M-7 outside a hand-over; the source relied on is Mat's explicit instruction, and Mat can overturn it with one line. The path was added to §Files Modified and to `eol-check.py` SCOPE (LF, now 46 paths) after the plan review, and its row-0 copy was taken after row 0 from the file unchanged since 2026-11-21 (equal to the `c0acc89` blob). It changes no snapshot path, so the mini-air runs stand. The whole gate was run again.
- **How the rows ran.** Each row ran through `row-run.ps1` (generated from `task.md`, D-1474) with `ELECTRON_RUN_AS_NODE` cleared. Edits to CRLF files were made by bytes and checked by `eol-check.py`. No Electron ran on the dev PC; the E2E ran on mini-air only, through `e2e_remote.py`.
- **Secrets.** No row read, printed, copied or dispatched a real cookie value, a cookie file or browser profile content; the cookie tests use made-up content written by the test, and the proof script's options hold no cookie source.

### Execution notes

- **Mini-air's address moved (environment, not a product finding).** At row 11a.4 mini-air did not answer (`exit 10 ssh-failed`, no ping reply). Its DHCP address had moved from 192.168.11.205 to 192.168.11.194; the coordinator changed only the `HostName` line of the `mini-air12` block in the fleet SSH config, with the host key still pinned and strict checking unchanged. D-1499 recorded how the session went on: the Red snapshot `88f00345` was already built and `--verify`-bound, rows 12, 13 and 14 ran out of their `depends_on` order on 11b, and the Red run was taken against that same commit when mini-air answered (row 11a's first-attempt receipts are kept as `-r1`).
- **Row 16's local runner was lost (environment, coordinator action, not a product finding).** The local `e2e_remote.py run` process stopped after poll 42 (`task=Running`) with no final `e2e-remote:` line (`ycc-row16-e2e-r1.txt`, kept as the runner-lost evidence). The run itself finished on mini-air. The coordinator ran the tool's own recovery, `e2e_remote.py collect r20261127T133531Z-b2f78f8` (`ycc-row16-collect.txt`, exit 0, `e2e-remote: ok exit=0`), which also released the lock. The run was not repeated, so this is not a retry to green; `ycc-row16-e2e.txt` is a byte copy of the collect receipt so that `row-check.py e2e-result` reads it. The two clipboard specs were gated `skipped-connected` (a RustDesk session was connected) by the tool's own gate, not by this session.
- **Raised for Mat (plan §Out of Scope; not fixed here).** (1) yt-dlp prints its own stderr line when it skips a cookie-file entry (`yt_dlp/cookies.py:1386`). It is not in the reply and not an av-kit log line, and it also happens on a download; it is for triage. (2) Upstream took `web` out of its default clients in 2026.11.23 (pull request 18131). av-kit's client lists (`COOKIE_EXTRACTOR_ARGS`, the retry pin) still name it; D-539 and D-643 to D-646 govern those lists, so no change was made.
- **Hold-line follow-up.** `exclude-newer-package = { yt-dlp = false }` in the root `[tool.uv]` (D-1468, `hold-override: yes`, D-1490) must be removed, and `uv lock` run again, once 2026.11.23 is 7 days old (after 2026-11-30). Nothing in the repository enforces this; it is also in the issue's resolution text.
- **The route docstring (D-1494).** `test_cookies` in `packages/api/src/avkit_api/routes/downloads.py` still says "Probe cookies and return `{ok}` only." Changing it would move the OpenAPI `paths` that row 9 freezes, so it is kept; its wording is stale and is an open item for the next OpenAPI change.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-27 | claude-code-local (Claude Opus 5.5) | Handoff after the H1-2 gate, H1-3 and H1-4 |
