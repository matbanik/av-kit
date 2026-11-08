---
date: "2026-11-08"
project: "convert-extract-index"
meu: "MEU-123"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-07-convert-extract-index/implementation-plan.md"
build_plan_section: "bp08"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "none"
---

# Handoff: 2026-11-07-convert-extract-index-MEU-123-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-123 `convert-extract-stream-index` (`CONVERT-EXTRACT-STREAM-INDEX-MISMATCH`, triage D-227; rider `CONVERT-EXTRACT-ENCODER-LABEL`, grouping D-242). First audio stream now writes `.m4a` for AAC. All audio streams extracts every track, the first included, and no job asks for a track the file doesn't have. `stream_index` has one meaning in the API, MCP, GUI, service and adapter: the Nth audio stream, the N in `-map a:N`. An Extract job saves no encoder.
**Build Plan Section**: [08 §Extract stream index (residual)](../../../docs/build-plan/08-video-conversion.md), Delivered note after the residual's table (`:607-612`), with the Extract table (`:176-177`) and the DTO notes (`:468`, `:476`).
**Predecessor**: none.

- **Audio positions (rows 1, 2; D-364 to D-367).**
  - `_audio_streams` (`services/conversion.py:93`) returns the probe's audio `StreamInfo` entries sorted by ffprobe `index`, so list position N is the N in the adapter's `-map a:N` (`media/adapter.py:635`), or `None` when the positions are unknown (`AUDIO_POSITION`). An empty list means no audio.
  - `_expand_plans` (`:338`) plans positions `0..k-1` in All mode (`AUDIO_PLAN`). The naming token is the position, so two tracks give `_a0`, `_a1`, and one track stays `_a`.
  - `_output_ext` (`:390`) takes the codec at the position; with unknown positions the probe's first audio codec applies at position 0 only (`EXTRACT_EXT`). AAC gives `.m4a`.
  - `_missing_track` (`:105`) names why a plan has no audio track: "the file has no audio track", or "no audio track a:N; the file has K audio track(s)". `_jobs_for_path` combines it with the probe error (`:282`), so the job is created `Failed` and FFmpeg never runs for it (`MISSING_TRACK`). The message holds a position and a count only.
- **Encoder label (row 2; D-368).** `_dispatch` (`:504`) neither calls `detect_gpu` nor resolves an encoder for an Extract and saves `gpu_encoder=None`, which also clears a label an older build stored (`EXTRACT_NO_ENCODER`). An Extract no longer fails for want of a software encoder. Compress resolves and saves its encoder as before; its branch now narrows `encoder` with a `ValidationError` guard (`:535-536`), see Quality Gate Results. Cut is unchanged and filed (D-373).
- **Unchanged (D-369, D-370).** No migration: a stored row's `stream_index` reaches `ExtractOptions` as before (`LEGACY_JOBS`). The API schema and route, the MCP tool, the GUI and the adapter carry `stream_index` unchanged (`PASS_THROUGH`); the adapter always read a position, so the GUI row's `a:{n}` now matches FFmpeg's.
- **Real FFmpeg (rows 1, 3; D-371).** `tests/integration/test_extract_real_ffmpeg.py` runs the real service, a real SQLite unit of work and `FFmpegAdapter(configured_path=<pinned ffmpeg.exe>)` on `.mp4` files it generates with that binary: one track (`aac`), two tracks (`aac`, `ac3`) and none (`REAL_FFMPEG`). It never skips; a missing binary fails with `tools/fetch_ffmpeg_windows.ps1` in its message. CI's Tests step deselects the module (`.github/workflows/ci.yml:65`, `CI_DESELECT`), because the runner has no fetched binaries; `ci-collect.py` proves the deselect from the workflow file itself.
- **Where values go (D-372, `NO_RAW_CONSOLE`).** No log line is added. `convert.extract` logs an int; `convert.finished` and `convert.cancelled` log `argv`, which holds the input path, but `argv` isn't a Console field and the HealthService processor replaces the event before any renderer runs, and production builds the HealthService before ConversionService (`wiring.py:205`). FFmpeg's own stdout goes to `DEVNULL` and its stderr is read for progress only. `MISSING_TRACK`'s message goes to `error_message` only and holds no path, codec or title. The module builds its HealthService before the engine, and AC-123.13 asserts that no clip path or pytest temp folder reaches stdout, stderr, the ring or `console.log`. The startup `engine.created` line, which prints the database path before production builds a HealthService, predates this session and is filed as `CONSOLE-STARTUP-DB-PATH` (D-377, placed in Session 55 by D-379).
- **Spec text (row 4).** 08's Extract table (`:176-177`), `ConversionCreateIn` (`:468`), `ConversionJobOut` (`:476`) and the Delivered note after the residual's table (`:607-612`).

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-07-convert-extract-index/implementation-plan.md) §MEU-123. **Execution authorization:** `USER_EXPLICIT`, 2026-11-07, "proceed with execution", given after the Codex plan review approved ([plan-critical-review.md](2026-11-07-convert-extract-index-plan-critical-review.md)); recorded in [human-gate-decision.md](../../../docs/execution/plans/2026-11-07-convert-extract-index/human-gate-decision.md) (`plan_to_exec_gate: human`).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-123.1 | unit | First mode on a picture-first probe (`[0 video h264, 1 audio aac]`) gives one job at `stream_index` 0, named `clip_a.m4a`, and the fake records `ExtractOptions(stream_index=0, output_container="m4a")` | Local Canon: 08 `:602`; triage D-227 | `tests/unit/test_conversion_service.py:977` | ✅ |
| AC-123.2 | unit | All mode on `[0 video, 1 audio aac, 2 audio ac3]` gives jobs at 0 and 1, named `clip_a0.m4a` and `clip_a1.ac3`, and the fake records `stream_index` 0 and 1 | Local Canon: 08 `:603`; triage D-227 | `tests/unit/test_conversion_service.py:995` | ✅ |
| AC-123.3 | unit | All mode on `[0 video, 1 audio aac]` gives one job at 0, named `clip_a.m4a` | Local Canon: 08 `:603` | `tests/unit/test_conversion_service.py:1016` | ✅ |
| AC-123.4 | unit | `MISSING_TRACK`: a video-only probe gives one `Failed` job in First and in All mode, "the file has no audio track"; First mode at `stream_index=2` on one audio track gives "no audio track a:2; the file has 1 audio track(s)"; after `start_processing` they stay `Failed` and `encode_calls` is 0 | Local Canon: brief; AC-30.1's path | `tests/unit/test_conversion_service.py:1041` (3 cases) | ✅ |
| AC-123.5 | unit | Unknown positions (`streams=None`, `audio_codec="aac"`): position 0 gives `.m4a`, position 1 gives `.mka`, both `Pending` | Local Canon: `EXTRACT_EXT`; `adapter.py:468-471` | `tests/unit/test_conversion_service.py:1071` | ✅ |
| AC-123.6 | unit | `EXTRACT_NO_ENCODER`: with NVIDIA caps an Extract ends `Done` with `gpu_encoder is None` and no `detect_gpu` call; with the `software` setting and caps without either software encoder, an Extract ends `Done` | Local Canon: `CONVERT-EXTRACT-ENCODER-LABEL` | `tests/unit/test_conversion_service.py:1094`, `:1113` | ✅ |
| AC-123.7 | unit | `LEGACY_JOBS`: an Extract row stored `Failed` with `stream_index=1` and `gpu_encoder="hevc_nvenc"`, retried through `reset_failed`, reaches the fake as `ExtractOptions(stream_index=1, …)` and ends with `gpu_encoder is None` | Local Canon: brief | `tests/unit/test_conversion_service.py:1139` | ✅ |
| AC-123.8 | unit | Compress still saves its encoder: `libx265` on default caps, `hevc_nvenc` with NVIDIA caps on Auto (guard) | Local Canon: brief; AC-112.1 | `tests/unit/test_conversion_service.py:1172` (2 cases) | ✅ |
| AC-123.9 | integration | The pinned `ffmpeg.exe` and `ffprobe.exe` exist and are over 1024 B, the message names `tools/fetch_ffmpeg_windows.ps1`, `FFmpegAdapter(configured_path=<pinned>)` resolves both, and the generated fixtures probe as `[video, aac]`, `[video, aac, ac3]` and `[video]` (guard) | Local Canon: AC-25.10 | `tests/integration/test_extract_real_ffmpeg.py:127` | ✅ |
| AC-123.10 | integration | First mode on `one_track` and `two_track` through the real stack: one job, `Done`, `<stem>_a.m4a`, which the real adapter probes as one `aac` stream and no video; `gpu_encoder is None` | Local Canon: 08 `:605`; triage D-227 | `tests/integration/test_extract_real_ffmpeg.py:141` (2 cases) | ✅ |
| AC-123.11 | integration | All mode: `one_track` gives one job at 0, `Done`, `<stem>_a.m4a`; `two_track` gives jobs at 0 and 1, both `Done`, `<stem>_a0.m4a` (`aac`) and `<stem>_a1.ac3` (`ac3`); every `gpu_encoder is None` | Local Canon: 08 `:603`, `:605` | `tests/integration/test_extract_real_ffmpeg.py:157` (2 cases) | ✅ |
| AC-123.12 | integration | `no_audio` through the real stack, First and All mode: one `Failed` job at add, "the file has no audio track"; after the worker drains it is still `Failed`, no output file exists, and a counting `FFmpegAdapter` saw no `extract_stream` call | Local Canon: brief; `MISSING_TRACK` | `tests/integration/test_extract_real_ffmpeg.py:181` (2 cases) | ✅ |
| AC-123.13 | integration | `NO_RAW_CONSOLE`: with the media folder named with a marker and the HealthService built before the engine, a First-mode Extract runs to `Done`, and neither the marker nor pytest's base temp folder reaches stdout, stderr, the ring or `console.log`; the ring holds `engine.created` and `convert.finished` (guard) | Local Canon: Session 50 RULE-1; plan review F1; AC-115.19 | `tests/integration/test_extract_real_ffmpeg.py:197` | ✅ |
| AC-30, AC-112 (cross-ref) | regression | AC-30.1, AC-30.11 to AC-30.13 and AC-112.1 to AC-112.4 pass unchanged; AC-30.13's audio-first probes are where index and position agree | plan §Acceptance Criteria (guards) | row 2; gate `py-tests` | ✅ |
| AC-31.21, MCP convert (cross-ref) | regression | `stream_index` passes through the API and MCP unchanged (`PASS_THROUGH`) | plan §Where `stream_index` goes | `tests/e2e/test_api_conversions.py:744-762` (row 2), `mcp-server/tests/convert.test.ts:254-264` (gate `mcp-tests`) | ✅ |
| AC-4.12 (cross-ref) | regression | No `assert` statement in `packages/core/src` | `tests/unit/test_domain.py` | gate `py-tests` (run 2) | ✅ |
| AC-24, AC-25 (cross-ref) | regression | CI's Tests step deselects the real-FFmpeg module, as it already does AC-24.10 and AC-25.10, because the runner has no fetched binaries (`CI_DESELECT`) | plan §Single-statement contracts | `.github/workflows/ci.yml:65`; gate `ci-collect` | ✅ |
| AC-45 (cross-ref) | regression | `convertMetaSegments` drops a null `gpu_encoder`, so an Extract row shows no encoder; AC-45.17 passes unchanged | plan §Where `stream_index` goes | `ui/tests/unit/convert-controls.test.ts:218-231`; gate `ui-tests` | ✅ |
| AC-51, AC-81 (cross-ref) | regression | `ui/tests/e2e/test-ids.ts` is unchanged (scope-paths refuses it), so the byte-hash tests pass | plan §Files Modified | gate `scope-paths`, `ui-tests` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-123.1, AC-123.10 | `assert [(0, 'clip_a.mka')] == [(0, 'clip_a.m4a')]`; `(0, 'one_track_a.mka') != (0, 'one_track_a.m4a')`, and the same for `two_track` | Row 2: pass | `test_conversion_service.py:977`, `test_extract_real_ffmpeg.py:141` |
| AC-123.2, AC-123.3, AC-123.11 | `(1, 'clip_a1.m4a') != (0, 'clip_a0.m4a')`; `(1, 'clip_a.m4a') != (0, 'clip_a.m4a')`; real: `(1, 'one_track_a.m4a') != (0, …)`, `(1, 'two_track_a1.m4a') != (0, 'two_track_a0.m4a')` | Row 2: pass | `test_conversion_service.py:995`, `:1016`, `test_extract_real_ffmpeg.py:157` |
| AC-123.4, AC-123.12 | `(Pending, None) != (Failed, 'the file has no audio track')`, and `!= (Failed, 'no audio track a:2; the file has 1 audio track(s)')` | Row 2: pass | `test_conversion_service.py:1041`, `test_extract_real_ffmpeg.py:181` |
| AC-123.5 | `At index 1 diff: [('.m4a', Pending)] != [('.mka', Pending)]` | Row 2: pass | `test_conversion_service.py:1071` |
| AC-123.6, AC-123.7 | `'hevc_nvenc' != None` (and a `detect_gpu` count of 1); `Failed != Done` with "software encoder unavailable"; `'hevc_nvenc' != None` on the legacy row | Row 2: pass | `test_conversion_service.py:1094`, `:1113`, `:1139` |
| AC-123.8, AC-123.9, AC-123.13 | Guards: pass in Red by design | Row 2: pass | `test_conversion_service.py:1172`, `test_extract_real_ffmpeg.py:127`, `:197` |

- **Row 1 Red:** 16 failed and 4 passed (the guards, AC-123.8 counting two cases) with 24 deselected in 3.33s, each failure by assertion. `red-check.py` required the 16 tests and found 0 problems. No collection or import error.
- **Row 2 Green:** 150 passed over the conversion service, real-FFmpeg, FFmpeg conversion, filesystem media, API wiring, conversion API and API body suites, with pyright 0 errors and ruff clean. No test file changed in row 2. The receipts were rerun after the gate-found fix (see Quality Gate Results); the first run's copies are in `C:/Temp/av-kit/s54-row2-r1/` and read the same counts.
- **Row 3:** CI's Tests step, read from `ci.yml` itself, collects 1199 tests and none of the module; the control without the deselect collects 1207, the module's 8 among them.

Receipts: `C:/Temp/av-kit/s54-baseline.txt`, `s54-base-py.txt`, `s54-base-ui.txt`, `s54-base-mcp.txt`, `s54-extract-red.txt` (with `.exit`), `s54-extract-red-check.txt`, `s54-extract-green.txt`, `s54-extract-types.txt`, `s54-extract-lint.txt` (run 1's copies in `s54-row2-r1/`), `s54-ci-collect.txt`, `s54-resolve.txt`, `s54-r4-*.txt`, gate run 2's `s54-gate-h1.txt` and `s54-D6-<id>.txt` (run 1's copies in `s54-gate-r1/`), `drift-check.txt` and `openapi-check.txt`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s54-0-baseline", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-07-convert-extract-index/baseline.ps1 *> C:/Temp/av-kit/s54-baseline.txt (task.md row 0's Validation cell, run from P:/av-kit)", "scope": "Row 0: baseline.sha, baseline-dirty.txt with each dirty path's SHA-256, the offline locked installs, the pinned FFmpeg pair, the base Python, UI and MCP suites with TMP and TEMP outside the home folder, and the red-check and identity selftests", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 39ac742 (baseline.sha), before row 0", "output": "baseline-dirty.txt 18 paths; baseline.sha 39ac742d123aa12bcad849f60008818ede359a61; uv sync checked 122 packages; ui lock sync 651 locked, 0 differ; mcp-server lock sync 133 locked, 0 differ; ffmpeg.exe 165577728 B: ffmpeg version n8.1.3-27-g8dca1586f4-20261031; ffprobe.exe 165371904 B: ffprobe version n8.1.3-27-g8dca1586f4-20261031; base py 1318 passed; base ui 1174 passed; base mcp 470 passed; identity selftest: 0 failure(s); baseline: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s54-123-red", "command": "$env:TMP='C:\\Temp\\av-kit\\s54\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest tests/unit/test_conversion_service.py tests/integration/test_extract_real_ffmpeg.py -k ac_123 --tb=short -q *> C:/Temp/av-kit/s54-extract-red.txt; then red-check.py with the 16 --require ids *> C:/Temp/av-kit/s54-extract-red-check.txt (abridged from task.md row 1's Validation cell, run from P:/av-kit through an extracted .ps1)", "scope": "MEU-123 Red: AC-123.1 to AC-123.13 against the unchanged service, with the unit fakes and the real FFmpegAdapter on the generated one-track, two-track and no-audio .mp4 fixtures", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 39ac742 plus rows 0 and 1", "output": "16 failed, 4 passed, 24 deselected in 3.33s. Decisive: assert [(0, 'clip_a.mka')] == [(0, 'clip_a.m4a')]; (1, 'clip_a1.m4a') != (0, 'clip_a0.m4a'); (Pending, None) != (Failed, 'the file has no audio track'); (Pending, None) != (Failed, 'no audio track a:2; the file has 1 audio track(s)'); [('.m4a', Pending)] != [('.mka', Pending)]; 'hevc_nvenc' != None; Failed != Done (software encoder unavailable); real: (0, 'one_track_a.mka') != (0, 'one_track_a.m4a'), (1, 'two_track_a1.m4a') != (0, 'two_track_a0.m4a'). red-check: 1 receipt(s), 16 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s54-123-green", "command": "$env:TMP='C:\\Temp\\av-kit\\s54\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest tests/unit/test_conversion_service.py tests/integration/test_extract_real_ffmpeg.py tests/unit/test_ffmpeg_conversion.py tests/integration/test_filesystem_media.py tests/integration/test_api_wiring.py tests/e2e/test_api_conversions.py tests/e2e/test_api_bodies.py --tb=short -q *> C:/Temp/av-kit/s54-extract-green.txt; then rtk proxy uv run pyright packages/ *> C:/Temp/av-kit/s54-extract-types.txt; then rtk proxy uv run ruff check packages/ tests/unit/test_conversion_service.py tests/integration/test_extract_real_ffmpeg.py *> C:/Temp/av-kit/s54-extract-lint.txt (task.md row 2's Validation cell, run from P:/av-kit through an extracted .ps1, after the AC-4.12 fix)", "scope": "MEU-123 Green: _audio_streams, _missing_track, _expand_plans, _output_ext, _jobs_for_path and _dispatch, with every Python suite that names the conversion service or route", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "39ac742d123aa12bcad849f60008818ede359a61+f67b517a559fc07414ffec531ac782498aec7e81a91130308978619ed40a22ae", "output": "150 passed in 7.33s. pyright: 0 errors, 0 warnings, 0 informations. ruff check: All checks passed!"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s54-3-ci-collect", "command": "rtk proxy uv run python docs/execution/plans/2026-11-07-convert-extract-index/ci-collect.py *> C:/Temp/av-kit/s54-ci-collect.txt (task.md row 3's Validation cell, run from P:/av-kit)", "scope": "Row 3 CI_DESELECT: the python job's Tests step read from .github/workflows/ci.yml with yaml.safe_load, collected offline as CI holds it and without the new deselect", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 39ac742 plus rows 0 to 3", "output": "--deselect tests/integration/test_extract_real_ffmpeg.py: 1 occurrence(s); as CI holds it: exit=0 collected=1199 in the module=0; control without it: exit=0 collected=1207 in the module=8; ci-collect: 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s54-4-records", "command": "task.md row 4 (abridged), run from P:/av-kit: the 08 notes; tools/meu_status.py update MEU-123 ready_for_review and render; issue-resolve.py --issue CONVERT-EXTRACT-STREAM-INDEX-MISMATCH --issue CONVERT-EXTRACT-ENCODER-LABEL --set-file C:/Temp/av-kit/s54-resolve.json --expect-sha256 $sha *> C:/Temp/av-kit/s54-resolve.txt; issue_triage.py render and triage; grouping row 54; then its Validation cell through an extracted .ps1 into s54-r4-render.txt, s54-r4-issues.txt and s54-r4-status.txt", "scope": "Row 4: the 08 spec text, MEU-123 ready_for_review, both issues resolved, the renders, and grouping row 54 naming the plan", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 39ac742 plus rows 0 to 4", "output": "register sha256 before 9c181ea36fe8 (the plan-time hash), after d86be1bf202e984a, CRLF=0 LF=4426; parsed fields changed: 10 (issues[104] and issues[87]); issue-resolve: 0 problem(s). Drift check passed (127 MEUs); OK: known-issues.md is up-to-date. ['resolved', 'resolved'] [True, True]; filed: [('open', 'P4', True), ('open', 'P3', True)]; grouping tracker names the plan: True, grouping places the filings: True"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s54-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-07-convert-extract-index/session-gate.ps1 *> C:/Temp/av-kit/s54-gate-h1.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s54-gate-h1.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','mismatch','session-gate:'; exit $code", "scope": "H1-2, gate run 2: the registered D6 gate on the whole tree after the AC-4.12 fix: identity, every static check, both full suites, the UI build, OpenAPI, the MCP types, tests and build, both renders, ci-collect, the real-FFmpeg module and the targeted Electron spec, then the identity again", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "39ac742d123aa12bcad849f60008818ede359a61+f67b517a559fc07414ffec531ac782498aec7e81a91130308978619ed40a22ae", "output": "identity-before exit=0; py-types exit=0 (0 errors, 0 warnings, 0 informations); py-lint exit=0 (All checks passed!); ui-types exit=0; ui-lint exit=0 (eslint --max-warnings 0); task-contract exit=0 (22 rows, 20 fully checked, 2 view_file exempt); scope-paths exit=0 (changed paths: 29, outside scope: [], head moved: False); red-check-selftest exit=0 (36 fixtures, 11 positive, 25 negative, 0 wrong); py-tests exit=0 (1338 passed); ui-tests exit=0 (112 files, 1174 passed); ui-build exit=0; openapi exit=0; mcp-types exit=0; mcp-tests exit=0 (35 files, 470 passed); mcp-build exit=0; state-render exit=0 (127 MEUs, 12 phases, regions match); issues-render exit=0 (known-issues.md is up-to-date); ci-collect exit=0 (0 problem(s)); extract-real-ffmpeg exit=0 (8 passed); ui-electron exit=0 (convert-queue.test.ts, 23 passed); identity-after exit=0 (tested_state before = after); mcp-audit, build-record and package-build skipped; baseline failures excused: py [], ui [], mcp []; session-gate: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s54-h1-3-render", "command": "rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/drift-check.txt (H1-3's cell, run through an extracted .ps1 from P:/av-kit)", "scope": "H1-3: rendered state regions against meu-status.yaml, after the current focus was updated. No status was written here; row 4 set MEU-123 ready_for_review", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "39ac742d123aa12bcad849f60008818ede359a61+f67b517a559fc07414ffec531ac782498aec7e81a91130308978619ed40a22ae", "output": "Drift check passed: SSOT loaded (127 MEUs, 12 phases), rendered regions match on-disk content"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s54-h1-4-openapi", "command": "rtk proxy uv run python tools/export_openapi.py --check openapi.committed.json *> C:/Temp/av-kit/openapi-check.txt (H1-4's cell, run through the same .ps1 from P:/av-kit)", "scope": "H1-4: packages/api doesn't change, so the OpenAPI check runs as a guard, and any drift would be S6", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "39ac742d123aa12bcad849f60008818ede359a61+f67b517a559fc07414ffec531ac782498aec7e81a91130308978619ed40a22ae", "output": "exit 0; check_openapi prints nothing when openapi.committed.json matches the live schema"}
```

### Quality Gate Results

`s54-gate-h1-2` (H1-2, gate run 2) is the fresh full record, and its last line is:

> session-gate: all steps exit 0

- **Static:** pyright 0 errors, 0 warnings; ruff check passed; the UI typecheck and ESLint (`--max-warnings 0`) passed; lint_task_contract passed on 22 rows (20 fully checked, 2 `view_file` exempt); scope-paths found 29 changed paths, none outside scope, `ui/tests/e2e/test-ids.ts` unchanged, and HEAD 39ac742 did not move; the red-check selftest read 36 fixtures with 0 wrong.
- **Suites:** pytest 1338 passed (the baseline's 1318 plus the 20 new AC-123 tests); Vitest 1174 passed in 112 files (baseline 1174); MCP tests 470 passed in 35 files (baseline 470). No baseline failure was excused.
- **Build and state:** the UI build, the OpenAPI check, the MCP typecheck and the MCP build exited 0; the state render (127 MEUs) and the issue render match the files on disk; `ci-collect` found 0 problems.
- **Runtime:** the real-FFmpeg module passed 8 of 8 on its own, with the pinned FFmpeg `n8.1.3-27-g8dca1586f4-20261031` (`ffmpeg.exe` 165,577,728 B, SHA-256 `c46215f8889634396f0ac0acac738ef2145175e5b6caf28b3daa8ac9a9980c5f`; `ffprobe.exe` 165,371,904 B, SHA-256 `b77db2dfcbf08886d6a29bc1fabdceea3dd559751b03087205e3e13ec85c3e15`), which the identity binds. The targeted Electron spec `tests/e2e/convert-queue.test.ts` passed 23 of 23, so the Convert page still renders its queue, rows and controls.
- **Skipped:** `mcp-audit` (live network, which the brief forbids), `build-record` (no installer build) and `package-build` (no packaged surface changes; MEU-125 runs the package build and its smokes).
- **Identity:** the tested_state was the same before and after the gate: `39ac742d123aa12bcad849f60008818ede359a61+f67b517a559fc07414ffec531ac782498aec7e81a91130308978619ed40a22ae`. It is re-derived with `ELECTRON_RUN_AS_NODE` unset, as H1-6b's cell does; the runtime identity records that variable, so a shell that has it set derives another state.
- **Gate run 1 and its fix.** Run 1 (H1-2) passed identity and every static step on `39ac742d123aa12bcad849f60008818ede359a61+1b6283118721fc5f3006d026c75fe86ca0157ace974f46ad9e142df3bd80be23`, then failed `py-tests` with 1 failed and 1337 passed: `tests/unit/test_domain.py::test_ac_4_12_validation_error_is_domain_constructor_error`, "assert remains in core source: ['packages\\core\\src\\avkit_core\\services\\conversion.py:535']". Row 2 had narrowed `encoder` for pyright with an `assert` in Compress's branch, and AC-4.12 bans `assert` anywhere in `packages/core/src`. The gate is fail-fast, so the later steps did not run. The `assert` is now `if encoder is None: raise ValidationError("Compress jobs require an encoder")` (`services/conversion.py:535-536`), the same guard the Cut branch uses at `:558-559`; it can't fire, since every kind but Extract resolves an encoder above. The edit kept the file's CRLF endings and moved no cited line before it. Row 2's commands were rerun into the same receipt names (150 passed, pyright 0 errors, ruff clean), and `test_ac_4_12` passed on its own before the gate ran again. Run 1's receipts are in `C:/Temp/av-kit/s54-gate-r1/`. `durable_evidence.py --require-full` binds every passing full record to the tree, so run 1 is not kept as a record.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/services/conversion.py` | modified | `_audio_streams`, `_missing_track`, `_expand_plans`, `_output_ext`, `_jobs_for_path`, `_dispatch`. CRLF kept |
| `tests/unit/test_conversion_service.py` | modified | AC-123.1 to AC-123.8, appended. CRLF kept |
| `tests/integration/test_extract_real_ffmpeg.py` | new | AC-123.9 to AC-123.13 on generated `.mp4` fixtures and the pinned FFmpeg. LF |
| `.github/workflows/ci.yml` | modified | `CI_DESELECT` and its comment (`:56-65`). LF kept |
| `docs/build-plan/08-video-conversion.md` | modified | §Spec text (row 4). LF kept |
| `docs/BUILD_PLAN.md`, `.agent/context/meu-status.yaml`, `meu-registry.md` | modified | MEU-123 `ready_for_review` (row 4) |
| `.agent/context/known-issues.yaml`, `known-issues.md`, `triage-output.yaml` | modified | Both issues resolved through `issue-resolve.py` (row 4) |
| `.agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md` | modified | Row 54 `executed` with the plan folder (`:254`). CRLF kept |
| `.agent/context/current-focus.md` | modified | Session 54 entry (H1-3) |
| Plan folder: `baseline.ps1`, `baseline.sha`, `baseline-dirty.txt`, `red-check.py`, `identity.py`, `ci-collect.py`, `issue-resolve.py`, `session-gate.ps1`, `human-gate-decision.md`, `task.md` | new | The plan's scripts and records |

```diff
+def _audio_streams(info: MediaInfo | None) -> list[StreamInfo] | None:
+    if info is None or info.streams is None:
+        return None
+    audio = [s for s in info.streams if isinstance(s, StreamInfo) and s.codec_type == "audio"]
+    return sorted(audio, key=lambda stream: stream.index)
+
+def _missing_track(plan: dict[str, int | None], audio: list[StreamInfo] | None) -> str | None:
+    position = plan.get("stream_index") or 0
+    if audio is None or position < len(audio):
+        return None
+    if not audio:
+        return "the file has no audio track"
+    return f"no audio track a:{position}; the file has {len(audio)} audio track(s)"
     ...
+        audio = _audio_streams(info) if spec.kind is ConversionKind.Extract else None
         for offset, plan in enumerate(plans):
+            error = probe_error or _missing_track(plan, audio)
     ...
-        if spec.stream_mode == "all" and info is not None and info.streams:
-            audio = [stream for stream in info.streams if ... codec_type == "audio"]
-            if audio:
-                return [{"stream_index": stream.index} for stream in audio]
+        audio = _audio_streams(info)
+        if spec.stream_mode == "all" and audio:
+            return [{"stream_index": position} for position in range(len(audio))]
     ...
-        if info is not None and info.streams:
-            index = plan.get("stream_index")
-            for stream in info.streams:
-                if isinstance(stream, StreamInfo) and stream.index == index:
-                    codec = stream.codec_name
-                    break
-        elif info is not None and info.audio_codec:
+        audio = _audio_streams(info)
+        position = plan.get("stream_index") or 0
+        if audio is not None:
+            if position < len(audio):
+                codec = audio[position].codec_name
+        elif position == 0 and info is not None and info.audio_codec:
             codec = info.audio_codec
     ...
     def _dispatch(self, job) -> None:
-        caps = self._gpu or self.detect_gpu()
-        encoder = self._resolve_encoder(caps, job.gpu_preference)
+        encoder: str | None = None
+        if job.kind is not ConversionKind.Extract:
+            encoder = self._resolve_encoder(self._gpu or self.detect_gpu(), job.gpu_preference)
     ...
         if job.kind is ConversionKind.Compress:
+            if encoder is None:  # resolved above for every kind but Extract
+                raise ValidationError("Compress jobs require an encoder")
```

```diff
           --deselect "tests/unit/test_packaging_installer.py::test_nsis_pack_check_script[AC-25.10]"
+          --deselect tests/integration/test_extract_real_ffmpeg.py
```

The excerpts are abridged; docstrings and comments are left out. `services/conversion.py:93-112`, `:279-282`, `:338-349`, `:390-409`, `:504-536` and `.github/workflows/ci.yml:56-65` are the source.

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
| — | — | None. Round 1 raised no finding | — | — | — |

### Verdict

Round 1 of loop `s54-execution-2026-11-07-convert-extract-index` returned `approved`, intent achieved `yes`, with 0 findings, using 7,859,970 of the loop's 21,000,000 tokens ([implementation-critical-review.md](2026-11-07-convert-extract-index-implementation-critical-review.md)). It accepted Q1 to Q8 with nothing not accepted. Its own probes ran both modes through the real FFmpeg adapter and SQLite on one- and two-track files, a mixed batch, a retry, the collision and `skip_existing` paths and the Console surfaces with an injected-marker control, and an AST scan found no `assert` in `packages/core/src`. It recomputed the tested_state as the handoff's and found the register write limited to the two issues' 10 fields. H1-7a and H1-7b passed on the canonical copy (`review-state-check.txt`, `exec-review.txt`).

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| Cut saves an encoder label it doesn't use | out-of-scope | debt queue (`CONVERT-CUT-ENCODER-LABEL`, P4) | D-373; filed and placed at plan time (D-379, D-380) |
| The startup `engine.created` line prints the database path before a HealthService exists | out-of-scope | Session 55 rider (`CONSOLE-STARTUP-DB-PATH`, P3) | D-377; filed and placed at plan time (D-379) |
| Commit and push | out-of-scope | — | Only on Mat's explicit words (H2-5) |

**Execution notes.**
- **Row commands.** They ran through `.ps1` files written from the task cells, because the cells' `*>` needs PowerShell.
- **Helper placement.** `_audio_streams` and `_missing_track` sit after `_preset_by_id` (`:93`, `:105`), as module-level helpers beside the other one, rather than right after `EXTRACT_UNKNOWN_EXT` as row 2 says. Nothing reads them by position.
- **Row 1 fixes before the Red run.** The identity selftest's `tests/` folder creation uses `exist_ok=True`, because the copied selftest makes the folder twice. A docstring line in the new module was rewrapped for ruff's E501, and the new module was `ruff format`ted. No expectation changed.
- **Row 3.** `ci-collect.py` first counted four steps named Tests, because each CI job has one; it now reads the `python` job's only, with a comment saying so.
- **Gate run 1's regression and its fix.** See Quality Gate Results. Row 2's commands were rerun after the fix into the same receipt names.
- **H1-3 and H1-4.** They ran from Git Bash through `.ps1` files, with `ELECTRON_RUN_AS_NODE` unset.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-08 | claude-code-local (Claude Opus 5.5) | Initial MEU-123 handoff after H1-2 gate run 2 |
| Reviewed | 2026-11-08 | codex-independent-reviewer | Execution review round 1 `approved`, 0 findings |
