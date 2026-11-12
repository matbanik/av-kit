---
date: "2026-11-12"
project: "download-failure-visibility"
meu: "MEU-139"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-11-download-failure-visibility/implementation-plan.md"
build_plan_section: "bp02"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-11-download-failure-visibility-MEU-138-handoff.md"
---

# Handoff: 2026-11-11-download-failure-visibility-MEU-139-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-139 `infra-ytdlp-log-detail`. It closes `YTDLP-LOG-TEXT-DROPPED`. yt-dlp's warnings and `ERROR:` lines now reach the Console with their text in a scrubbed `detail` field, whether or not debug is on. With Settings → Downloader's existing "yt-dlp debug" switch on, its debug and info lines reach the Console at DEBUG too (D-622, D-630, D-632). The switch is read at each public adapter call, so a change applies to the next call without a restart.

**Build Plan Section**: [02 §yt-dlp log detail (residual)](../../../docs/build-plan/02-infrastructure.md) (the Delivered note at `:568`).
**Predecessor**: [MEU-138 handoff](2026-11-11-download-failure-visibility-MEU-138-handoff.md), this session. It is the last MEU of Session 65; Session 66 (`youtube-client-runtime`, MEU-140 and MEU-141) is next in the grouping.

- **Adapter (rows 1 and 5).** In `packages/infrastructure/src/avkit_infra/youtube/adapter.py`:
  - `YTDLP_LINE` in `_YtDlpLogger` (`:385`): `__init__(debug_enabled)` (`:386`) and the methods `debug` (`:408`), `info` (`:413`), `warning` (`:418`) and `error` (`:421`), with the private `_emit` (`:403`). A warning always logs at WARNING; an `ERROR:` line always logs at ERROR; a debug line, an info line and an error line without the prefix log at DEBUG only when debug is on. Each `detail` is `scrub_line`'s output, and a line that scrubs to nothing logs nothing;
  - `YTDLP_LIVE`: `YouTubeAdapter.__init__` (`:434`) takes `yt_dlp_debug: Callable[[], bool] | None = None`, and `_debug_now` (`:452`) reads it once per public call. No source, a source that raises, and any answer but `True` read as off. Each call builds its logger from that one read: `extract_info` (`:570`, which `get_formats` calls), `extract_video_ids` (`:581`), `download` (`:596`), `check_sabr_status` (`:661`) and `test_cookies` (`:699`). `_run_extract` (`:547`) reads it only when its caller passed no logger, which none of the callers at `:575`, `:586` and `:664` does. `_base_opts` (`:499`) takes the logger and sets `quiet` and `verbose` from `logger.debug_enabled`.
- **Wiring (row 5).** `packages/api/src/avkit_api/wiring.py:159-160`, `LIVE_SOURCE`: the adapter gets `lambda: settings.get("downloader", "yt_dlp_debug") is True` in place of the value read once at startup.
- **Tests.**
  - `tests/unit/test_download_failure_visibility.py`: AC-139.1 to .3 and .9.
  - `tests/integration/test_youtube_adapter_visibility.py`: AC-139.4's adapter half and AC-139.7.
  - `tests/integration/test_api_wiring.py`: AC-139.4's wiring half.
  - `tests/e2e/test_api_download_visibility.py`: AC-139.5.
  - `tests/unit/test_transcript_metadata.py`: AC-139.6, and the AC-122.16 pin that moves (row 1).
  - `ui/tests/unit/settings-page.test.ts`: AC-139.8.
- **Spec text and records (row 6).** 02's Debug row (`:361`), Control row (`:565`) and Delivered note (`:568`); 06's yt-dlp debug toggle row (`docs/build-plan/06-gui.md:345`). MEU-139 is `ready_for_review` with this plan, and `YTDLP-LOG-TEXT-DROPPED` is `resolved`.

**Execution authorization:** `USER_EXPLICIT`, 2026-11-11 and 2026-11-12, as recorded in the [MEU-137 handoff](2026-11-11-download-failure-visibility-MEU-137-handoff.md) §Scope. Mat ruled D-622 "Opt-in shows text (Recommended)", which this MEU builds.

### Where values go, as built (Session 50 RULE-1, Session 53 RULE-1, Session 61 RULE-1)

- **yt-dlp's logger lines** reach the Console only through `_YtDlpLogger._emit` (`adapter.py:403`), as `yt-dlp detail=<text>`, each `detail` after `scrub_line`: the home folder, links and cookie-looking values are scrubbed, split forms included (AC-139.5), and a lone surrogate, a NUL and an ANSI code are removed (AC-139.9). Their writers are yt-dlp and the extractors it runs. There is no `message` key (AC-139.2).
- **With debug off** a debug or info line reaches nothing (AC-139.3; AC-122.16's moved pin). With it on, a title in a debug line can reach the Console, scrubbed (AC-139.6; D-622).
- **The debug setting** comes from `SettingsService` at each public call (`wiring.py:160`, `adapter.py:452`). Its writer is `PUT /settings`, from the Settings switch (AC-139.8). AC-139.4 traces a `PUT` between two calls on the real stack.
- **`app.log_level`** is stored and never read. Raised for Mat (§Deferred Items).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-139.1 | unit | Type characterisation: `yt_dlp_debug` is keyword, `Callable[[], bool] \| None`, default `None`; `_YtDlpLogger(debug_enabled)` exposes `debug_enabled`; `_base_opts` takes the logger only | 02 Live | `tests/unit/test_download_failure_visibility.py:601` | ✅ |
| AC-139.2 | unit | `YTDLP_LINE` with debug off: `warning("x")` logs one WARNING `yt-dlp` line with `detail` `x`; `error("ERROR: y")` one ERROR line with `detail` `ERROR: y`; neither has a `message` key | 02 Warnings and errors | `test_download_failure_visibility.py:618` | ✅ |
| AC-139.3 | unit | With debug off, `debug`, `info` and `error("Traceback …")` log nothing; with it on, each logs one DEBUG line; `warning("")`, `warning("\x1b[0m")` and `debug("\x00")` log nothing | 02 Debug lines; D-622, D-632 | `test_download_failure_visibility.py:629` | ✅ |
| AC-139.4 | integration | `YTDLP_LIVE`: a recording source returning False then True gives `quiet` True and `verbose` False on the first `download` and the reverse on the second, read exactly once per public call; a raising source and `None` read as False; `wiring.py`'s source follows a `PUT /settings` between two calls on the real stack | 02 Live | `tests/integration/test_youtube_adapter_visibility.py:277`, `:312`; `tests/integration/test_api_wiring.py:131` | ✅ |
| AC-139.5 | API | Redaction on the real stack, `HealthService` built first: a warning with the home marker, a URL and `cookie=SECRET` shows `~`, `[link]` and ` [REDACTED]`; so do the U+2028 and U+0085 splits and the mixed line; no marker, `e.example` or `SECRET` in the ring or stdout | 02 Warnings and errors; D-247 | `tests/e2e/test_api_download_visibility.py:315` | ✅ |
| AC-139.6 | unit | With debug on, a debug line holding a title marker reaches the Console redacted (D-622); AC-122.16's debug-off half still finds no marker | D-622 | `tests/unit/test_transcript_metadata.py:374` | ✅ |
| AC-139.7 | integration | The Session 55 RULE-3 trace: a mocked `YoutubeDL` whose `extract_info` calls `params["logger"].warning(...)` with a marker reaches the Console row through a real `HealthService` and a recording fake, with debug off | 02 Warnings and errors | `test_youtube_adapter_visibility.py:331` | ✅ |
| AC-139.8 | renderer | The existing switch saves: toggling `settings-leaf-yt_dlp_debug` sends `PUT` with `{downloader: {yt_dlp_debug: true}}` and then `false`. A characterisation (D-630) that passed from row 2c | 02 Control | `ui/tests/unit/settings-page.test.ts:502` | ✅ |
| AC-139.9 | unit | A warning with a lone surrogate, a NUL, `\x1b[31m` and a 400-character tail logs a `detail` with none of them, each Console field at most `FIELD_LIMIT`; an empty warning logs nothing | D-627; Session 53 RULE-1 | `test_download_failure_visibility.py:656` | ✅ |
| AC-122 (cross-ref) | regression | Moved pin: AC-122.16 (`test_transcript_metadata.py:324`) built `_YtDlpLogger(True)` and expected one `yt-dlp` line with no title. With D-622, a debug line logs only when debug is on, so the pin now builds `_YtDlpLogger(False)` and expects no line at all; the debug-on half is AC-139.6. It passed in row 2c's guard and in the gate | plan §Pins that move | `tests/unit/test_transcript_metadata.py:324`; gate `py-tests` | ✅ |
| AC-137 (cross-ref) | regression | MEU-137's ACs are owned by its handoff. `scrub_line` (`SCRUB_LINE`) is the one cleaner for both the failure line and every yt-dlp line | [MEU-137 handoff](2026-11-11-download-failure-visibility-MEU-137-handoff.md) | gate `py-tests` | ✅ |
| AC-138 (cross-ref) | regression | MEU-138's ACs are owned by its handoff. Each logger method calls `_scan` before deciding whether to log, so `SABR_SCAN` sees every line with debug off | [MEU-138 handoff](2026-11-11-download-failure-visibility-MEU-138-handoff.md) | gate `py-tests` | ✅ |
| AC-6 (cross-ref) | regression | MEU-6's adapter tests (`tests/integration/test_youtube_adapter.py`) pass with the per-call source; their adapters are built without one, which reads as off | plan §Guards | gate `py-tests` | ✅ |
| AC-2 (cross-ref) | regression | AC-2.6 (`test_domain.py:461`) is unchanged and passes | plan §Guards | gate `py-tests` | ✅ |
| AC-51 (cross-ref) | regression | The AC-51.6 byte-hash guards were not touched: no file they hash changed | plan §Guards | gate `py-tests` | ✅ |
| AC-53 (cross-ref) | regression | AC-53.2 and AC-53.4 are MEU-137's and MEU-138's guards; they pass in the gate's `ui-tests` | plan §Guards | gate `ui-tests` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-139.1 to AC-139.7 and AC-139.9 | Row 2c: `10 failed, 51 passed in 3.07s` against row 4's tree (`s65-py-red-139.txt`). The ten are `test_ac_139_1_debug_source_and_logger_have_their_planned_shape`, `test_ac_139_2_warnings_and_error_lines_log_with_debug_off`, `test_ac_139_3_debug_lines_log_only_with_debug_on`, `test_ac_139_9_surrogate_control_and_long_lines_are_cleaned`, `test_ac_139_4_each_public_call_reads_the_source_once`, `test_ac_139_4_a_raising_or_missing_source_reads_as_off`, `test_ac_139_7_a_warning_inside_extract_reaches_the_console`, `test_ac_139_5_ytdlp_warnings_reach_the_console_redacted`, `test_ac_139_6_debug_on_shows_a_title_redacted` and `test_api_wiring.py::test_ac_139_4_debug_source_follows_a_settings_put`. Decisive: `assert (<_ParameterK...'bool', False) == (<_ParameterK...\| None', None)`; `assert [] == [('warning', ...R: y', False)]`; `assert ['yt-dlp'] == ['yt-dlp deta...] [REDACTED]']`; `where False = callable(False)` | Row 5: `306 passed in 11.27s` (`s65-py-green-139.txt`); gate `py-tests` | `test_download_failure_visibility.py:601-656`, `test_youtube_adapter_visibility.py:277-331`, `test_api_download_visibility.py:315`, `test_transcript_metadata.py:374`, `test_api_wiring.py:131` |
| AC-139.8 | A characterisation of the existing switch (D-630). Row 2c's guard: `Tests  26 passed (26)` (`s65-r2c-guard-ui.txt`) | Row 5: 6 files, `Tests  134 passed (134)` (`s65-ui-green-139.txt`); gate `ui-tests` | `settings-page.test.ts:502` |

- **red-check.** Row 2c's check (`s65-red-139-check.txt`) reads `red-check: 1 receipt(s), 8 required test(s), 0 problem(s)`. Every failing block failed by assertion alone.
- **Every failure in the Red run is an AC-139 test.** AC-122.16's pin moved in row 1, beside the stub, and passed throughout.
- **Row 2c's guard** of the MEU-137, MEU-138 and AC-122.16 tests held: `34 passed, 23 deselected in 2.49s` (`s65-r2c-guard-py.txt`).

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s65-2c-red-139", "command": "rtk proxy uv run pytest tests/unit/test_download_failure_visibility.py tests/integration/test_youtube_adapter_visibility.py tests/e2e/test_api_download_visibility.py tests/unit/test_transcript_metadata.py tests/integration/test_api_wiring.py --tb=short -q *> C:/Temp/av-kit/s65-py-red-139.txt; red-check.py with the 8 --require ids *> C:/Temp/av-kit/s65-red-139-check.txt; pytest -k 'test_ac_137_ or test_ac_138_ or test_ac_122_16_' *> C:/Temp/av-kit/s65-r2c-guard-py.txt; npm --prefix ui run test -- tests/unit/settings-page.test.ts *> C:/Temp/av-kit/s65-r2c-guard-ui.txt (task.md row 2c's Validation cell)", "scope": "MEU-139 Red: AC-139.1 to AC-139.7 and AC-139.9 against row 4's tree; the MEU-137, MEU-138 and AC-122.16 tests and AC-139.8 as passing guards", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 003e5b1 plus rows 0 to 4 and 2c", "output": "10 failed, 51 passed in 3.07s. Decisive: assert (<_ParameterK...'bool', False) == (<_ParameterK...| None', None); assert [] == [('warning', ...R: y', False)]; assert ['yt-dlp'] == ['yt-dlp deta...] [REDACTED]']; where False = callable(False). red-check: 1 receipt(s), 8 required test(s), 0 problem(s). Guards: 34 passed, 23 deselected in 2.49s; Tests 26 passed (26)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s65-5-green-139", "command": "rtk proxy uv run pytest (row 5's files: the session's tests, test_domain.py, test_services.py, test_transcript_metadata.py, test_youtube_adapter.py, test_download_received_quality.py, test_api_wiring.py, test_api_downloads.py, test_api_error_surface.py) --tb=short -q -rfE *> C:/Temp/av-kit/s65-py-green-139.txt; npm --prefix ui run test -- (the downloader, sabr-panel and settings tests) *> C:/Temp/av-kit/s65-ui-green-139.txt; pyright, ruff and the UI typecheck *> C:/Temp/av-kit/s65-r5-*.txt (task.md row 5's Validation cell)", "scope": "MEU-139 Green: YTDLP_LINE and YTDLP_LIVE, with LIVE_SOURCE in wiring.py", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 003e5b1 plus rows 0 to 5", "output": "306 passed in 11.27s; UI Test Files 6 passed (6), Tests 134 passed (134); pyright 0 errors, 0 warnings, 0 informations; ruff All checks passed!; typecheck exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s65-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-11-download-failure-visibility/session-gate.ps1 *> C:/Temp/av-kit/s65-gate-h1.txt; then Select-String for ' exit=', 'not_run', 'skipped', 'tested_state', '_sha256 ', 'outside scope', 'mismatch', 'session-gate:' and exit $code (task.md row H1-2's Validation cell, run from P:/av-kit; per-step receipts C:/Temp/av-kit/s65-D6-*.txt; run 3, after D-639 (execution round 1 F1), copied to C:/Temp/av-kit/s65-gate-h1-run3.txt; run 2 is s65-gate-h1-run2.txt)", "scope": "H1-2: the registered full gate. Static: py-types, py-lint, ui-types, ui-lint, task-contract, scope-paths, red-check-selftest. Full: py-tests, openapi, ui-tests, ui-build, mcp-types, mcp-build, mcp-tests, state-render, issues-render. Runtime: ui-electron. Identity before and after. Skipped with reasons: mcp-audit, build-record, package-build, real-ffmpeg", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "003e5b1466c4b7accadc6b3267c7d4b1315f2991+a12677f6bd755b550577edac1f737db236bb558858f1de93dbe75f71d986b4ba", "output": "py-types 0 errors, 0 warnings, 0 informations; py-lint All checks passed!; task-contract OK: 26 row(s), 24 fully checked, 2 exempt (view_file): H1-5, H2-1; scope-paths changed paths: 44 outside scope: [] head moved (S3): False; baseline-dirty paths changed since row 0 (S3): []; red-check selftest: 44 fixture(s) (13 positive, 31 negative), 0 wrong; py-tests 2152 passed, 37 warnings in 307.22s (0:05:07); ui-tests Test Files 120 passed (120), Tests 1285 passed (1285); mcp-tests Test Files 35 passed (35), Tests 520 passed (520); state-render Drift check passed (142 MEUs, 12 phases); issues-render OK: known-issues.md is up-to-date; ui-electron 26 passed (27.9s); tested_state before = after; session-gate: all steps exit 0"}
```

### Quality Gate Results

The session has one gate, recorded in full in the [MEU-137 handoff](2026-11-11-download-failure-visibility-MEU-137-handoff.md) §Quality Gate Results. Its last line is:

> session-gate: all steps exit 0

Run 1 stopped at `py-tests` on the AC-130.10 ICC timestamp flake in an untouched capture test; the rerun alone passed (`s65-h1-2-rerun-ac130-10.txt`), and run 2 passed every step. After execution round 1's F1 fix (D-639), run 3 passed every step, with `py-tests` at 2152. Its tested_state was `003e5b1466c4b7accadc6b3267c7d4b1315f2991+a12677f6bd755b550577edac1f737db236bb558858f1de93dbe75f71d986b4ba` before and after.

### Caller grep (S55 RULE-1)

Every caller of `YouTubeAdapter(` and `_YtDlpLogger(` is in row 1's grep (`s65-row1-callers.txt`; the table is in the [MEU-137 handoff](2026-11-11-download-failure-visibility-MEU-137-handoff.md)). The one production builder is `wiring.py:155`. Row 5's pytest ran each listed test file.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `packages/infrastructure/src/avkit_infra/youtube/adapter.py` | modified | `_YtDlpLogger`'s methods and `_emit`; `yt_dlp_debug` as a source; `_debug_now`; each public call builds its logger from one read; `_base_opts` reads the logger |
| `packages/api/src/avkit_api/wiring.py` | modified | `LIVE_SOURCE`: a lambda over the setting (`:159-160`) |
| `tests/unit/test_download_failure_visibility.py`, `tests/integration/test_youtube_adapter_visibility.py`, `tests/e2e/test_api_download_visibility.py` | new | AC-139.1 to .5, .7 and .9 (with MEU-137's and MEU-138's ACs) |
| `tests/integration/test_api_wiring.py` | modified | AC-139.4's wiring half (+31 lines) |
| `tests/unit/test_transcript_metadata.py` | modified | AC-122.16's moved pin and AC-139.6 |
| `ui/tests/unit/settings-page.test.ts` | modified | AC-139.8 (+36 lines) |
| `docs/build-plan/02-infrastructure.md`, `06-gui.md` | modified | 02's Debug and Control rows and Delivered note (`:361`, `:565`, `:568`); 06's toggle row (`:345`) |

Line endings are listed in the [MEU-137 handoff](2026-11-11-download-failure-visibility-MEU-137-handoff.md) §Changed Files. `wiring.py`, `test_api_wiring.py` and `settings-page.test.ts` stayed CRLF; `test_transcript_metadata.py` stayed LF.

```diff
 # wiring.py
-    yt_dlp_debug = settings.get("downloader", "yt_dlp_debug") is True
-        yt_dlp_debug=yt_dlp_debug,
+        # LIVE_SOURCE: the yt-dlp debug switch is read at each public call (YTDLP_LIVE).
+        yt_dlp_debug=lambda: settings.get("downloader", "yt_dlp_debug") is True,
 # adapter.py (abridged)
-        yt_dlp_debug: bool = False,
+        yt_dlp_debug: Callable[[], bool] | None = None,
-            "quiet": not self._yt_dlp_debug,
+            "quiet": not logger.debug_enabled,
+            "verbose": logger.debug_enabled,
-        logger = _YtDlpLogger(self._yt_dlp_debug)
+        logger = _YtDlpLogger(self._debug_now())
-            logger = _YtDlpLogger(False)
+            logger = _YtDlpLogger(self._debug_now())
```

The last pair is `test_cookies` (`adapter.py:699`), which built its logger with debug off before.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

Codex reviews the execution in one rolling report, `2026-11-11-download-failure-visibility-implementation-critical-review.md`, on the ledger loop `s65-execution-2026-11-11-download-failure-visibility`.

| Round | Verdict | Findings | Tested state |
|-------|---------|----------|--------------|
| 1 | changes_required | 1 finding, F1 High (AC-137): cleaning inside `classify_download_error` lost the split before `SCRUB_LINE`; blocking 1; intent achieved partial; 13,389,317 tokens (`C:/Temp/av-kit/dispatch/s65-exec-run-r1.txt`) | `003e5b1466c4b7accadc6b3267c7d4b1315f2991+02916a61145051d9ce6a921eeb0b1340f52609efe4a06f5bf407733e7a2e5aec` |
| 2 | approved | F1 fixed (D-639, AC-137.12); 0 new findings; blocking 0; intent achieved yes; 3,259,894 tokens, 16,649,211 of 40,000,000 in all (`C:/Temp/av-kit/dispatch/s65-exec-run-r2.txt`) | `003e5b1466c4b7accadc6b3267c7d4b1315f2991+a12677f6bd755b550577edac1f737db236bb558858f1de93dbe75f71d986b4ba` |

### Verdict

Approved by Codex in round 2 of 6. Round 1's F1 is `fixed` in the round 2 Prior Pass Summary, and round 2 has no new finding. H1-7a (`C:/Temp/av-kit/review-state-check.txt`) reads `OK: review_mode=execution; round 2 of 6; verdict=approved; open findings=0`, and H1-7b (`C:/Temp/av-kit/exec-review.txt`) reads `OK: approved at round 2 of 6, 0 open blocking findings`. MEU-139 moves to `approved` in H2-2.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| `app.log_level` is stored and never read, so the Console shows DEBUG lines whenever the yt-dlp switch is on | design, raised for Mat | None | Plan §Out of Scope; the switch, not a log level, is this MEU's control (D-630) |
| The client pin and fallback | bug | MEU-140, MEU-141 (Session 66) | Their own grouping session |
| The MP3 convert | bug | MEU-142 (Session 67) | Its own grouping session |

### Departures and their basis

1. **Private helpers not named in the plan (row 5).** `_YtDlpLogger._emit` (`adapter.py:403`) is the one place that logs a line and drops an empty `detail`, and `YouTubeAdapter._debug_now` (`:452`) is the one read of the source. Both are in Changed Files and in the gate scope through `adapter.py`.
2. **The `ERROR:` prefix is read after cleaning (row 5).** D-632 says only an `ERROR:` line is an error. yt-dlp colours the prefix when its output is a terminal, so `error` reads the prefix from `scrub_line`'s output, after the ANSI code is gone (`adapter.py:424-425`). A raw `startswith` would log a coloured `ERROR:` line at DEBUG.
3. **`extract_video_ids` is a fifth call that reads the source (row 2c).** AC-139.4's text names four public calls: `download`, `extract_info`, `check_sabr_status` and the cookie test. `extract_video_ids` (`:581`) builds a logger too, so it reads the source once per call in the same way, and AC-139.4's test (`test_youtube_adapter_visibility.py:277`) checks all five. The AC text is unchanged; the test checks one more call than it names.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Completed | 2026-11-12 | claude-code-local (Claude Opus 5.5) | The MEU-139 handoff after the H1-2 gate |
