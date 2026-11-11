---
date: "2026-11-10"
project: "video-probe-frames"
meu: "MEU-133"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-10-video-probe-frames/implementation-plan.md"
build_plan_section: "bp08"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-10-gui-capture-image-import-MEU-132-handoff.md"
---

# Handoff: 2026-11-10-video-probe-frames-MEU-133-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-133 `convert-media-probe`. A caller reads a local video's duration, size, frame rate and codecs without changing the file or writing a job.
- **REST.** `POST /api/v1/conversions/probe {"path": …}` answers 200 with the eleven 08 fields: `path`, `duration_ms`, `timecode`, `container`, `video_codec`, `audio_codec`, `width`, `height`, `fps`, `has_video`, `has_audio`. It is synchronous and writes nothing.
- **MCP.** `avkit_convert` `probe` takes `{action, path}` and calls that route with the 30 s default timeout.
- **UTF-8 (D-573 A).** `FFmpegAdapter._run` now decodes FFmpeg's and ffprobe's output as UTF-8 with `errors="replace"`. A path or a title tag holding `Ł` used to probe as all-`None` under cp1252; it now probes with `duration_ms` 3000.

**Build Plan Section**: [08 §Media probe (residual)](../../../docs/build-plan/08-video-conversion.md) (anchor `media-probe-residual`, `:616`; the Delivered note at `:629`).
**Predecessor**: [MEU-132 handoff](2026-11-10-gui-capture-image-import-MEU-132-handoff.md). This is the first session of the video stills grouping (`.agent/context/grouping/2026-11-09-video-stills-session-grouping.md`, Sessions 62 to 64, D-500 to D-505). Its sibling MEU-134 has its own handoff: [MEU-134 handoff](2026-11-10-video-probe-frames-MEU-134-handoff.md).

- **Core module (rows 1 and 3; D-571, D-585).** `packages/core/src/avkit_core/services/video_input.py` (new, LF) is pure. For this MEU it holds:
  - `MAX_PATH_CHARS` (`:23`) and `VideoProbe` (`:42`), the frozen dataclass of the eleven fields;
  - `require_local_video` (`:93`), for `VIDEO_INPUT`, with `_non_local` (`:78`) and `_bad_char` (`:87`);
  - `format_timecode` (`:121`) and `duration_ms` (`:129`), for `TIMECODE`;
  - `video_probe(resolved, info)` (`:143`), the one writer of `PROBE_MAP`'s fields (see Departures).
- **Service (row 3; D-572).** `ConversionService.probe_file` (`packages/core/src/avkit_core/services/conversion.py:193`) runs `VIDEO_INPUT`, then `self._media.probe(resolved)`, and returns `video_probe(resolved, info)` (`:209`). A `MediaProbeError` becomes `ValidationError("the file could not be probed")`, raised after the `except` clause has ended. `FFmpegNotFoundError` passes through to the masked 503. No job row is written.
- **Adapter (rows 1 and 3; D-573 A, D-588).** In `packages/infrastructure/src/avkit_infra/media/adapter.py`:
  - `_run` (`:294`) passes `encoding="utf-8", errors="replace"` (`:308-309`, `:316-317`) and takes a new keyword `timeout`. It calls `subprocess.run` with `timeout=` only when `timeout` isn't `None`, so the existing callers make the call they made before (`RUN_UTF8`).
  - `probe` (`:452`) takes `timeout_s: float | None = None` and maps `subprocess.TimeoutExpired` to `MediaProbeError("ffprobe timed out")` (`:477`). `probe_file` passes no timeout. `MediaPort.probe` (`packages/core/src/avkit_core/ports/media.py:30`) gains the same keyword under D-588 (the plan's Decision Log, `implementation-plan.md:697-711`).
- **API (row 3).** `ConversionProbeIn` (`packages/api/src/avkit_api/schemas/conversions.py:123`, `path` 1 to 4096, `extra="forbid"`) and `ConversionProbeOut` (`:129`). The route `probe_conversion_input` (`packages/api/src/avkit_api/routes/conversions.py:189`) is declared before `/{id}` (`PROBE_ROUTE`). `openapi.committed.json` is regenerated.
- **MCP (row 3; D-583).**
  - `mcp-server/src/toolsets/convert.ts`: `PROBE_TEXT` (`:8`), the description (`:37`) and the strict schema (`:111-112`) after `gpu_refresh` (`PROBE_MCP`).
  - `mcp-server/src/toolsets/registry.ts:122`: the `ACTION_INDEX` row after `gpu_refresh`.
  - `mcp-server/scripts/audit/plan.ts`: the offline `convert.probe` step on a made 2 s clip (AC-134.16 owns its coverage).
- **Tests.**
  - `tests/unit/test_video_input.py` (new, LF): AC-133.1 and .2, and MEU-134's AC-134.2 to .4.
  - `tests/unit/test_conversion_probe.py` (new, LF): AC-133.3.
  - `tests/e2e/test_api_conversion_probe.py` (new, LF): AC-133.4 and .5.
  - `tests/unit/test_media_adapter_frames.py` (new, LF): AC-133.6, and MEU-134's AC-134.9.
  - `tests/integration/test_video_real_ffmpeg.py` (new, LF): AC-133.7, and MEU-134's AC-134.10 and .11. CI deselects it (`.github/workflows/ci.yml`, beside the extract module).
  - `mcp-server/tests/convert.test.ts`: AC-133.8.
  - `tests/e2e/test_api_openapi.py`: AC-133.9.
  - The pins in §Pins that move (rows 2a and 2b): `ROUTE_INDEX` 74 → 75, `ROUTE_COUNT_AFTER` and `ACTION_INDEX_AFTER`, `_valid_body`, `CONVERT_ROUTES` and `STATIC_BEFORE_ID`, the MCP action counts 71 → 72, convert 13 → 14, the M7 keys and `BASELINE_PENDING`.
- **Spec text and records (row 6).**
  - 08's Delivered note (`docs/build-plan/08-video-conversion.md:629`).
  - MEU-133 `ready_for_review` with this plan (`.agent/context/meu-registry.md:148`).
  - Grouping row 62 `executed` (`.agent/context/grouping/2026-11-09-video-stills-session-grouping.md:102`).

**Execution authorization:** `USER_EXPLICIT`, 2026-11-10. The Codex plan review approved at round 4 ([plan-critical-review.md](2026-11-10-video-probe-frames-plan-critical-review.md)). The plan's human rulings are quoted in its decision log: D-573, D-576 and D-577, each "A", on Mat's "all recommendations are accpeted, proceed". Then Mat said:
- "start execution" (2026-11-10T22:28:44-05:00);
- "for any questions ask fable subagent and accept ruling from it" (2026-11-10T22:29:50-05:00).

The receipt for both is `s62-exec-authorization.txt` (lines 2 and 3), with HEAD `7b9f34d`. Under the second, D-588 to D-592 were ruled by a Fable subagent. That delegation covers execution questions only. It doesn't cover a commit or a push, which wait on Mat's own words, or the review's approval, which is Codex's.

### Where values go (Session 50 RULE-1, Session 53 RULE-1, Session 61 RULE-1)

- **The video path** goes from the request body to `VIDEO_INPUT`, then to ffprobe's argv and to the 200 body's `path` (the resolved path). It is never logged and never put in an error message. Every refusal is a fixed message (AC-133.1, AC-133.5). Its only writer is the caller.
- **ffprobe's stdout** becomes `MediaInfo` fields through the unchanged parse. `container`, `video_codec` and `audio_codec` reach the 200 body. They come from the file's own header. `RUN_UTF8`'s `errors="replace"` turns undecodable bytes into U+FFFD (AC-133.6). They are never logged.
- **ffprobe's stderr**, which names the path, is dropped. `PROBE_MAP` raises its fixed error after the `except` clause has ended, so nothing is chained (AC-133.3 checks `__cause__` and `__context__`).
- **The duration** reaches the body as `duration_ms` and `timecode` (`TIMECODE`).
- **No new log line.** AC-133.5 drives a marker through the missing-file, symlink-loop, URL, probe-failure and FFmpeg-missing errors on the real stack, with `HealthService` built first (Session 54 RULE-2). The marker is absent from every body, the log ring, stdout and stderr. A positive control logs it once and finds it in the ring and in stdout (D-590).
- **No network.** Every video in every test and probe was made locally with the pinned FFmpeg. A URL is refused as input.

### Documented limits

- **`_run_with_progress` still decodes with the locale codec.** Its `Popen` (`adapter.py:323`) uses `text=True` with no `encoding`, and its reader thread catches only `OSError`. Its callers are encode (`:729`), cut (`:767`) and `extract_stream` (`:798`). The plan cited these as `:274`, `:570`, `:608` and `:639`; the lines moved with this session's additions. A conversion whose FFmpeg output holds a byte cp1252 can't decode would end that reader thread. This is named for Mat and not fixed (plan §Out of Scope, D-573). It is not filed as an issue, because no row has Mat's words to file one.
- **A raw stream has no duration.** `duration_ms` and `timecode` are `null` for a raw `.h264` stream (AC-133.7). The MCP description says so.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-133.1 | unit | `VIDEO_INPUT`: an absolute drive path and a `\\?\` UNC-shaped path to a file are accepted and resolved; empty, 4097 characters, relative, `http:`, `file:`, `ftp:`, a lone surrogate, `\x07`, NUL, a missing file, a directory and a self-loop symlink (or a patched `resolve` raising `RuntimeError`) each give the exact fixed message, with `__cause__` and `__context__` `None` and no marker in the formatted exception | 08 Input; D-571 | `tests/unit/test_video_input.py:39` (through `:156`) | ✅ |
| AC-133.2 | unit | `TIMECODE`: `format_timecode` of 0, 999, 1000, 3,599,999 and 359,999,999; `duration_ms` of 3.0, 7200.021, 3.0005 (3001, exact half up), 3.0004 (3000), and `None`, NaN, inf, 0 and −1 give `None` | 08 Response | `test_video_input.py:191`, `:228` | ✅ |
| AC-133.3 | unit | `PROBE_MAP` with a recording fake `MediaPort`: the eleven fields; `has_video` and `has_audio` from the codecs; a marker-bearing `MediaProbeError` becomes `the file could not be probed` with nothing chained; `FFmpegNotFoundError` passes through; no job row, the queue unchanged | 08 Request, Errors; D-572 | `tests/unit/test_conversion_probe.py:87` (through `:181`) | ✅ |
| AC-133.4 | API | Real stack with a fake `MediaPort`: 200 with exactly the eleven keys; `duration_ms` and `timecode` null with no duration; an extra key, a missing `path`, `""` and a non-string `path` give the fixed 422; no conversion row after any call | 08 Request, Response | `tests/e2e/test_api_conversion_probe.py:139`, `:164`, `:187` | ✅ |
| AC-133.5 | API | Errors: `video file not found` (missing file and self-loop symlink, no `probe` call), the URL message, `the file could not be probed`, the masked 503; the marker absent from every body, the log ring, stdout and stderr, with a positive control (D-590) | 08 Errors; S54 RULE-2 | `test_api_conversion_probe.py:196` | ✅ |
| AC-133.6 | unit | `RUN_UTF8` (D-573 A): a recording fake `subprocess.run` sees `encoding="utf-8"`, `errors="replace"`, `text=True` and `capture_output=True` on `probe` and on `version`'s `-version` call; invalid UTF-8 in stdout doesn't raise | D-573 | `tests/unit/test_media_adapter_frames.py:78`, `:91`, `:104`, `:116` | ✅ |
| AC-133.7 | integration | Real FFmpeg through `probe_file`: the counter clip with audio (3000 ms, 320×240, 25 fps, both streams), with no audio, a raw `.h264` (nulls, `has_video` true), `Łodz.mp4` and a `Ł` title tag (both 3000 ms); each source's SHA-256 unchanged | 08 Tests; D-573 | `tests/integration/test_video_real_ffmpeg.py:112`, `:130`, `:139`, `:151`, `:163` | ✅ |
| AC-133.8 | MCP | `PROBE_MCP`: `{action, path}` accepted; an extra key, an empty and a missing path refused before fetch; the row after `gpu_refresh`; `POST /conversions/probe` with body exactly `{path}` and the default timeout; the four M7 markers and `PROBE_TEXT`; transport parity of the eleven keys | 08 Request, Tests; D-583 | `mcp-server/tests/convert.test.ts:306`, `:332`, `:346`, `:382` | ✅ |
| AC-133.9 | API | OpenAPI: the route with `ConversionProbeIn` and `ConversionProbeOut` in `openapi.committed.json`; `export_openapi.py --check` passes; `/probe` declared before `/{id}` | 08 Tests | `tests/e2e/test_api_openapi.py:144`; H1-4 | ✅ |
| AC-134 (cross-ref) | cross-reference | MEU-134's ACs, AC-134.1 to AC-134.17, are owned and evidenced by the MEU-134 handoff. AC-134.9's last case covers this MEU's `probe(file_path)` and `-version` calls passing no `timeout` keyword | plan §MEU-134 | [MEU-134 handoff](2026-11-10-video-probe-frames-MEU-134-handoff.md) | ✅ |
| AC-8 (cross-ref) | regression | AC-8.12 (`tests/integration/test_filesystem_media.py:445-477`) pins `FFmpegAdapter`'s `MediaPort` signatures equal to the protocol's; it passes with `probe`'s new `timeout_s` on both sides (D-588) | plan `FRAME_PORT`; D-588 | gate `py-tests` | ✅ |
| AC-16 (cross-ref) | regression | AC-16.6 walks every `ROUTE_INDEX` row in the live OpenAPI; its lookup now asserts `path in paths` before indexing (D-589), and passes with the 76 rows | D-589 | `tests/e2e/test_api_openapi.py:121-122`; gate `py-tests` | ✅ |
| AC-31 (cross-ref) | regression | AC-31.17's static-before-id check asserts `path in paths` before indexing (D-589); `STATIC_BEFORE_ID` gains `/probe` | D-589; plan §Pins that move | `tests/e2e/test_api_conversions.py:637-639`; gate `py-tests` | ✅ |
| AC-68 (cross-ref) | regression | AC-68.5's `AUDIT_ACTION_SET` and AC-68.1/AC-68.4's built-server discovery count 73 actions; `BASELINE_PENDING` gains `avkit_convert.probe` | plan §Pins that move | `mcp-server/tests/audit/coverage.test.ts`, `runner-fake-backend.test.ts:77`; gate `mcp-tests` | ✅ |
| AC-38, AC-67, AC-130 (cross-ref) | regression | Capture-side pins, owned by the MEU-134 handoff: AC-38.5 and AC-67.17's shared markers (`capture.test.ts:168`, `:438-449`) and AC-130.7's member order (`test_domain_capture.py:884-892`) | plan §Pins that move | [MEU-134 handoff](2026-11-10-video-probe-frames-MEU-134-handoff.md); gate `py-tests`, `mcp-tests` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-133.1 to AC-133.7, AC-133.9 (Python) | Row 2a: 71 failed, 163 passed against the row 1 stubs. `DID NOT RAISE <class 'avkit_core.domain.errors.ValidationError'>` ×21; `assert 0 == None` ×7; `Method Not Allowed` ×6; `assert 405 == 422` ×5; `assert 405 == 200` ×2 | Row 3: 312 passed; gate `py-tests` 1792 passed | `test_video_input.py:39-228`, `test_conversion_probe.py:87`, `test_api_conversion_probe.py:139-196`, `test_media_adapter_frames.py:78-116`, `test_video_real_ffmpeg.py:112-163`, `test_api_openapi.py:144` |
| AC-133.8 (MCP) | Row 2b: Test Files 6 failed; Tests 17 failed, 126 passed (143). `expected [ …(71) ] to have a length of 72 but got 71`; `expected 'undefined' to be 'string'` | Row 3: 35 files, 491 passed; gate `mcp-tests` 498 passed | `convert.test.ts:306-382` |

- **red-check.** Row 2a's receipt: 1 receipt, 8 required tests, 0 problems. Row 2b's: 1 receipt, 1 required test, 0 problems. Every failing block is an assertion.
- **D-589, row 2a's first run.** red-check refused two blocks that failed with `KeyError: '/api/v1/conversions/probe'`: `test_ac_16_6_each_route_index_row[POST-/api/v1/conversions/probe]` and `test_ac_31_17_openapi_static_auth_console[AC-31.17]`. Their lookups indexed the OpenAPI paths before asserting. Under the Fable ruling, only `test_api_openapi.py:121-122` and `test_api_conversions.py:637-639` changed, to assert `path in paths` first. Both stayed CRLF. The rerun is the receipt above.
- **The passes in the Red runs.** Row 2a's 163 passes are the guard modules and the cases the row 1 stubs already met. Row 2b's 126 passes are the MCP tests that don't read the new action.
- **D-590, row 3's first run.** It had 311 passed and 1 failed: AC-133.5's stdout positive control expected exactly one line holding the marker and found two. `HealthService._process` prints the JSON payload (`packages/core/src/avkit_core/services/health.py:230`), and the structlog console renderer prints the line again, by design. Under the Fable ruling, only the stdout control (`test_api_conversion_probe.py:248`) became `>= 1`. The ring control (`:245`, `== 1`) and every absence check are unchanged. The rerun passed 312.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s62-0-baseline", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-10-video-probe-frames/baseline.ps1 *> C:/Temp/av-kit/s62-baseline.txt (task.md row 0's Validation cell, run from P:/av-kit; base suites in C:/Temp/av-kit/s62-base-py.txt, s62-base-mcp.txt, s62-base-ruff.txt and s62-base-mcp-build.txt)", "scope": "Row 0: rulings, anchors, baseline.sha and baseline-dirty.txt, line endings, the offline FFmpeg probe, base suites and the identity selftest", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 7b9f34d before any row", "output": "Base suites: pytest 1565 passed in 120.62s; MCP 35 files, 485 passed; ruff All checks passed!; MCP build exit 0. Identity selftest: 0 failures, every artifact state_unchanged=True. baseline: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s62-1-types", "command": "rtk proxy uv run pytest (test_domain.py, test_domain_capture.py, test_api_captures.py and the MediaPort pin files) *> C:/Temp/av-kit/s62-types-py.txt; rtk proxy uv run pyright *> C:/Temp/av-kit/s62-types-pyright.txt; rtk proxy uv run ruff check *> C:/Temp/av-kit/s62-types-ruff.txt; the caller grep *> C:/Temp/av-kit/s62-r1-callers.txt (task.md row 1's Validation cell)", "scope": "Row 1: the shared names as wrong stubs (video_input.py, FramePort, MediaPort.probe's timeout_s under D-588, CaptureSource.Video), the CaptureSource pins, and the caller and pin grep", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 7b9f34d plus rows 0 to 1", "output": "241 passed in 7.37s; pyright 0 errors; ruff All checks passed!; caller grep 121 lines (CaptureService(, ConversionService(, _run( callers, CaptureSource and MediaPort pins)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s62-2a-red-133-py", "command": "rtk proxy uv run pytest (the MEU-133 Python tests and the moved pins) *> C:/Temp/av-kit/s62-py-red-133.txt; then red-check.py with the 8 --require ids *> C:/Temp/av-kit/s62-py-red-133-check.txt (task.md row 2a's Validation cell, rerun after D-589)", "scope": "MEU-133 Python Red: AC-133.1 to AC-133.7 and AC-133.9 against the row 1 stubs", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 7b9f34d plus rows 0 to 2a", "output": "71 failed, 163 passed in 13.96s. Decisive: DID NOT RAISE ValidationError x21; assert 0 == None x7; Method Not Allowed x6; assert 405 == 422 x5; assert 405 == 200 x2. red-check: 1 receipt(s), 8 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s62-2b-red-133-mcp", "command": "rtk proxy npm --prefix mcp-server run build *> C:/Temp/av-kit/s62-r2b-mcp-build.txt; rtk proxy npm --prefix mcp-server test *> C:/Temp/av-kit/s62-mcp-red-133.txt; then red-check.py --require AC-133.8 (task.md row 2b's Validation cell)", "scope": "MEU-133 MCP Red: AC-133.8 and the moved MCP pins, on a fresh build", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 7b9f34d plus rows 0 to 2b", "output": "Test Files 6 failed; Tests 17 failed | 126 passed (143). Decisive: expected [ ...(71) ] to have a length of 72 but got 71; expected 'undefined' to be 'string'. red-check: 1 receipt(s), 1 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s62-3-green-133", "command": "rtk proxy uv run pytest (row 3's MEU-133 tests and guards) *> C:/Temp/av-kit/s62-py-green-133.txt; rtk proxy npm --prefix mcp-server test *> C:/Temp/av-kit/s62-mcp-green-133.txt; real FFmpeg *> C:/Temp/av-kit/s62-r3-real-ffmpeg.txt; callers *> C:/Temp/av-kit/s62-r3-callers.txt; export_openapi diff *> C:/Temp/av-kit/s62-r3-openapi-diff.txt; pyright and ruff *> C:/Temp/av-kit/s62-r3-pyright.txt, s62-r3-ruff.txt (task.md row 3's Validation cell; rerun after D-590)", "scope": "MEU-133 Green: VIDEO_INPUT, TIMECODE, PROBE_MAP, RUN_UTF8, PROBE_ROUTE, PROBE_MCP, and the guards test_ffmpeg_conversion, test_ffmpeg_resolver, test_conversion_service, test_api_conversions and test_extract_real_ffmpeg", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 7b9f34d plus rows 0 to 3", "output": "312 passed; MCP Test Files 35 passed (35), Tests 491 passed (491); real FFmpeg 14 passed; every _run, FFmpegAdapter and ConversionService caller plus test_domain and test_domain_capture: 408 passed; OpenAPI diff adds only /api/v1/conversions/probe, ConversionProbeIn (path minLength 1, additionalProperties false) and ConversionProbeOut; pyright 0 errors; ruff All checks passed!"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s62-6-records", "command": "task.md row 6 (abridged), run from P:/av-kit: the S3 check, the pre-status copies, the 08 and 09 Delivered notes, tools/meu_status.py update MEU-133 and MEU-134 ready_for_review --plan, the S15 byte-edit route and render; grouping row 62; then its Validation cell into C:/Temp/av-kit/s62-r6-render.txt and its status check into C:/Temp/av-kit/s62-r6-status.txt", "scope": "Row 6: the D3 spec text, MEU-133 and MEU-134 ready_for_review with this plan, the render, and grouping row 62 executed", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 7b9f34d plus rows 0 to 6", "output": "Drift check passed - SSOT loaded (142 MEUs, 12 phases), rendered regions match on-disk content. status ['ready_for_review', 'ready_for_review']; grouping row 62 executed; spec notes True True"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s62-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-10-video-probe-frames/session-gate.ps1 *> C:/Temp/av-kit/s62-gate-h1.txt; then Select-String for ' exit=', 'not_run', 'skipped', 'tested_state', '_sha256 ', 'outside scope', 'mismatch', 'session-gate:' and exit $code (task.md row H1-2's Validation cell, run from P:/av-kit; per-step receipts C:/Temp/av-kit/s62-D6-*.txt; rerun after D-592, the first run's receipt kept as C:/Temp/av-kit/s62-gate-h1-pre-d592.txt)", "scope": "H1-2: the registered D6 gate on the whole tree, shared by MEU-133 and MEU-134", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "7b9f34d4e93b9fc733277278859f2b9ec26abdb8+25fcaf6e1ae51b67694418476fe797d4e4d790721f5638b009089b4c19e76651", "output": "baseline failures excused: py [], mcp []; ui-types, ui-lint, ui-tests, ui-build, ui-electron, mcp-audit, build-record and package-build skipped with reasons; identity-before exit=0; py-types exit=0 (0 errors, 0 warnings, 0 informations); py-lint exit=0 (All checks passed!); task-contract exit=0 (26 rows, 24 fully checked, 2 view_file exempt: H1-5, H2-1); scope-paths exit=0 (changed paths: 57, outside scope: [], head moved (S3): False, baseline-dirty paths changed since row 0: []); red-check-selftest exit=0 (43 fixtures, 13 positive, 30 negative, 0 wrong); py-tests exit=0 (1800 passed in 142.05s); openapi exit=0; mcp-types exit=0; mcp-build exit=0; mcp-tests exit=0 (35 files, 498 passed); state-render exit=0 (142 MEUs, 12 phases); issues-render exit=0 (known-issues.md is up-to-date); status-canon exit=0 (2 files, 14 passed); real-ffmpeg exit=0 (23 passed in 4.24s); identity-after exit=0 (tested_state before = after); session-gate: all steps exit 0"}
```

### Quality Gate Results

`s62-gate-h1-2` (H1-2) is the fresh full record for both MEUs. Its last line is:

> session-gate: all steps exit 0

- **The rerun after D-592.** The first H1-2 run passed at `7b9f34d+eb0ad811…` (receipt `s62-gate-h1-pre-d592.txt`). Execution review round 1 approved with one finding, F1, and its fix under D-592 changed `video_input.py` and two test files. So the gate ran again on the whole tree, and this section and the `s62-gate-h1-2` record describe that run.
- **Static checks.**
  - pyright: 0 errors, 0 warnings, 0 informations. ruff check: all checks passed.
  - lint_task_contract passed on 26 rows (24 fully checked; H1-5 and H2-1 are exempt as `view_file`).
  - scope-paths found 57 changed paths, none outside scope. That is the first run's 54 plus the two handoffs and `current-focus.md`, written after it. HEAD `7b9f34d` did not move, and none of the paths in `baseline-dirty.txt` changed since row 0 (S3).
  - The red-check selftest read 43 fixtures (13 positive, 30 negative), with 0 wrong.
- **Suites.**
  - pytest: 1800 passed. That is the baseline's 1565 plus 235 new cases for MEU-133 and MEU-134, 8 of them D-592's. No baseline failure was excused.
  - MCP: 498 passed in 35 files. That is the baseline's 485 plus 6 for AC-133.8 and 7 for AC-134.15 and .16.
  - real-ffmpeg: 23 passed. That is 15 in `test_video_real_ffmpeg.py` (AC-133.7, AC-134.10 and .11) and the 8 of `test_extract_real_ffmpeg.py`, which runs again because `_run` changed (Session 55 RULE-1).
  - status-canon: the two UI tests that read `meu-status.yaml` and `BUILD_PLAN.md` (`layout-canon.test.ts`, `queue-canon.test.ts`) passed 14.
- **Build and state.**
  - `export_openapi.py --check`, the MCP typecheck and the MCP build exited 0.
  - The state render (142 MEUs) and the issue render match the files on disk.
  - H1-3's `render --check` and H1-4's `export_openapi.py --check` passed after the gate (receipts `drift-check.txt` and `openapi-check.txt`).
- **Skipped.** Each skip has a reason in the gate:
  - `ui-types`, `ui-lint`, `ui-tests`, `ui-build`, `ui-electron`: no `ui/` file changed. status-canon runs the only UI tests that read a file this session writes.
  - `mcp-audit`: it needs the live network, which the brief forbids. `AUDIT_PLAN`'s two new steps are covered offline by AC-134.16.
  - `build-record`: no installer build.
  - `package-build`: no packaged surface change. MEU-125 ran the package build and its smokes.
- **Identity.**
  - The tested_state was the same before and after the gate: `7b9f34d4e93b9fc733277278859f2b9ec26abdb8+25fcaf6e1ae51b67694418476fe797d4e4d790721f5638b009089b4c19e76651`.
  - The identity leaves out the closeout records, so writing them doesn't change it: the plan folder's `.md` files, the handoffs and reviews named `2026-11-10-video-probe-frames-*`, the reflection, `metrics.md` and `current-focus.md`.
  - Its inputs also hash the pinned `ffprobe.exe` (`ffprobe_sha256` `b77db2df…`), `uv.lock` and `ui/package-lock.json`.

### The row 3 OpenAPI diff

`export_openapi.py` regenerated `openapi.committed.json` (CRLF kept). Against `7b9f34d` the diff adds:
- the path `/api/v1/conversions/probe` (POST, 200 `ConversionProbeOut`, 422);
- the schema `ConversionProbeIn`: `path` string, `minLength` 1, `maxLength` 4096, `additionalProperties: false`;
- the schema `ConversionProbeOut` with the eleven fields.

Nothing else was changed or removed. Row 5 added MEU-134's route to the same file (see the MEU-134 handoff).

### D-573: the ruling and its result (D-504 receipt `probe5-receipt.txt`)

- **Before.** At plan time, `probe5-receipt.txt` ran the adapter's `probe` under the machine's `preferred_encoding=cp1252`. A plain path, a CJK path and an emoji path probed with duration 3.0. A path holding `Ł` and a title tag holding `Ł` both probed as all-`None`, because ffprobe's UTF-8 JSON held byte 0x81, which cp1252 can't decode (`UnicodeDecodeError: 'charmap' codec can't decode byte 0x81`). A missing file named with `Ł` raised `MediaProbeError` whose message didn't name the path.
- **Ruling.** D-573 A: `RUN_UTF8`, on Mat's "all recommendations are accpeted, proceed".
- **After.** AC-133.6 pins the keywords on the `probe` and `-version` calls. AC-133.7's `Łodz.mp4` copy and `Ł` title tag both probe with `duration_ms` 3000 through the real adapter (`test_video_real_ffmpeg.py:151`, `:163`), in row 3 and in the gate.

### Caller and pin grep (S55 RULE-1, S59 RULE-1)

- **`_run`'s callers** (row 1, re-read in row 3) were all run in row 3's caller set (408 passed): `version`, `probe`, the encoder and hwaccel lists and the GPU smoke. With `timeout` unset, each makes the call it made before, plus the two decoding keywords.
- **`ConversionService(`** is built at `wiring.py:215`, `real_stack.py:103`, `test_extract_real_ffmpeg.py:102` and `test_conversion_service.py:289`, `:562`. Its constructor didn't change.
- **`MediaPort.probe`** pins: `test_filesystem_media.py:448`, `:466` (AC-8.12), `test_domain.py:1331`, `:1340`, `test_domain_conversion.py:170-187` and `test_services.py:326`. All pass in the gate.
- **Count pins** next to `ROUTE_INDEX` and `ACTION_INDEX` were grepped again in row 2a and 2b (S59 RULE-1), and every hit is in §Pins that move. An absence grep for tests asserting `probe` is absent found none (Session 61 RULE-3).

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/services/video_input.py` | new | `VIDEO_INPUT`, `TIMECODE`, `VideoProbe`, `video_probe` (and MEU-134's names). LF |
| `packages/core/src/avkit_core/services/conversion.py` | modified | `probe_file` (`PROBE_MAP`) |
| `packages/core/src/avkit_core/ports/media.py` | modified | `MediaPort.probe`'s `timeout_s` (D-588) |
| `packages/infrastructure/src/avkit_infra/media/adapter.py` | modified | `RUN_UTF8`; `_run`'s `timeout`; `probe`'s `timeout_s` (and MEU-134's grab) |
| `packages/api/src/avkit_api/routes/conversions.py`, `schemas/conversions.py` | modified | `PROBE_ROUTE` |
| `openapi.committed.json` | regenerated | The probe route and its two schemas |
| `mcp-server/src/toolsets/convert.ts`, `registry.ts` | modified | `PROBE_MCP` and its `ACTION_INDEX` row |
| `mcp-server/scripts/audit/plan.ts` | modified | The offline `convert.probe` step |
| `tests/unit/test_video_input.py`, `test_conversion_probe.py`, `test_media_adapter_frames.py` | new | AC-133.1 to .3, .6 (and MEU-134's). LF |
| `tests/e2e/test_api_conversion_probe.py` | new | AC-133.4, .5. LF |
| `tests/integration/test_video_real_ffmpeg.py` | new | AC-133.7 (and MEU-134's). LF |
| `tests/e2e/test_api_openapi.py` | modified | AC-133.9; `ROUTE_INDEX`; the AC-16.6 lookup, row 2a Red made assertion-shaped (D-589) |
| `tests/e2e/test_api_conversions.py` | modified | `CONVERT_ROUTES`, `STATIC_BEFORE_ID`; the AC-31.17 lookup, row 2a Red made assertion-shaped (D-589) |
| `tests/e2e/test_api_downloads.py`, `test_api_bodies.py` | modified | The route and action counts; the probe's valid body |
| `mcp-server/tests/convert.test.ts`, `capture.test.ts`, `action-index.test.ts`, `m7-resource.test.ts`, `fixtures.ts`, `audit/coverage.test.ts`, `audit/runner-fake-backend.test.ts` | modified | AC-133.8; the counts 71 → 72; `BASELINE_PENDING` |
| `.github/workflows/ci.yml` | modified | `--deselect tests/integration/test_video_real_ffmpeg.py` |
| `docs/build-plan/08-video-conversion.md` | modified | The Delivered note (`:629`) |
| `.agent/context/meu-status.yaml`, `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md`, the grouping file | modified | Only MEU-133's and MEU-134's fields and rows, and grouping row 62 (row 6) |
| `.agent/context/current-focus.md` | modified | The Session 62 paragraph (H1-3) |

Line endings were measured with Python bytes before each edit and kept:
- These files stayed CRLF: `conversion.py`, `ports/media.py`, `adapter.py`, both conversion API files, `convert.ts`, `registry.ts`, `plan.ts`, the MCP test files, `test_api_openapi.py`, `test_api_conversions.py`, `test_api_downloads.py`, `openapi.committed.json`, the grouping and `current-focus.md`.
- These files stayed LF: `test_api_bodies.py`, `ci.yml`, 08, `meu-status.yaml`, `BUILD_PLAN.md` and `meu-registry.md`.
- New files are LF.

```diff
 # adapter.py, FFmpegAdapter._run (abridged)
+                    encoding="utf-8",
+                    errors="replace",
 # adapter.py, FFmpegAdapter.probe
-    def probe(self, file_path: Path) -> MediaInfo:
+    def probe(self, file_path: Path, *, timeout_s: float | None = None) -> MediaInfo:
+            raise MediaProbeError("ffprobe timed out")
 # routes/conversions.py
+@router.post("/probe", response_model=ConversionProbeOut)
+def probe_conversion_input(
+    probe = conversion.probe_file(body.path)
+    return ConversionProbeOut(**dataclasses.asdict(probe))
```

The excerpt is abridged. The source is `adapter.py:294-321`, `:452-477`, `conversion.py:193-209` and `routes/conversions.py:189-199`.

**S15's status diff** (row 6, against the pre-status copies):
- **`meu-status.yaml`.** Only MEU-133's and MEU-134's `status`, `status_labels`, `execution_plan` and `updated` changed (10 lines in the two entries). The tool's whole-file rewrite was set aside and the pre-status copy byte-edited (Session 61 RULE-5); `yaml.safe_load` of the result equals the tool's output.
- **`meu-registry.md`.** Only rows 148 (MEU-133) and 196 (MEU-134) changed.
- **`BUILD_PLAN.md`.** Only the total changed (`:68`), from `124 + 1🚫` to `124 + 2🟡 + 1🚫`.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

Codex reviews the execution in one rolling report, `2026-11-10-video-probe-frames-implementation-critical-review.md`, on the ledger loop `s62-execution-2026-11-10-video-probe-frames`.

| Round | Verdict | Findings | Tested state |
|-------|---------|----------|--------------|
| 1 | approved | F1 (Medium, non-blocking): a huge finite float time, such as `1e25`, passed `CaptureFramesIn`, and `_time_ms`'s Decimal quantize raised `InvalidOperation`, so `frames` answered the generic 500 instead of the fixed 422. Fixed under D-592 | `7b9f34d4e93b9fc733277278859f2b9ec26abdb8+eb0ad8111e0de603143b55d4bd3be55581f7f9dc158fc7372d4348aa504ea75b` |
| 2 | approved, `intent_achieved: yes` | F1 `fixed`; no new findings. Codex compared 9,325 non-negative floats up to 1e9 with the pre-fix parser and all matched. A guard on sign only, or one placed after the quantize, still raised `InvalidOperation` on 1e25, 1e100 and 1e308. 2,484,514 tokens | `7b9f34d4e93b9fc733277278859f2b9ec26abdb8+25fcaf6e1ae51b67694418476fe797d4e4d790721f5638b009089b4c19e76651` |

### Verdict

Approved at round 2 of 6, with 0 open findings (H1-7a and H1-7b, `C:/Temp/av-kit/review-state-check.txt` and `exec-review.txt`). The canonical review is a byte-for-byte copy of Codex's report, SHA-256 `6d866fbb5a20eede…`. MEU-133 and MEU-134 move to `approved` at H2-2.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| `_run_with_progress`'s decoding (`adapter.py:323`; callers `:729`, `:767`, `:798`) | observation for Mat | Mat's ruling | Plan §Out of Scope, D-573: named, not fixed |
| `MCP-AUDIT-BASELINE-PENDING-CROP`, with `avkit_convert.probe` now pending too | known issue | The next authoritative baseline update | D-499; `--update-baseline` needs Mat's words, and the live audit is forbidden here |
| `MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL` | known issue | Its own session | Not this session's |
| Contact sheet, export, the description eval | feature | MEU-135, MEU-136, Session 64 | Grouping §3, D-505 |
| Commit and push | out-of-scope | — | Only on Mat's explicit words (H2) |

**Execution notes.**
- **Shared rows.** Rows 0, 1 and 6 and the H1-2 gate serve both MEUs; their records are in both handoffs.
- **`video_probe` moved into `video_input.py` in row 5.** Row 3 built the eleven fields inside `probe_file`. Row 5 needed the same fields for `frames`' `video` object, so the mapping became `video_probe(resolved, info)` (`video_input.py:143`), and `probe_file` returns it (`conversion.py:209`). `PROBE_MAP` has one writer. `conversion.py` was touched again in row 5, and AC-133.3 and AC-133.4 passed in row 5 and in the gate.
- **`_run`'s two calls.** `_run` makes two explicit `subprocess.run` calls, with and without `timeout=`, because pyright rejects a `**dict` splat into `subprocess.run`.
- **Receipts re-encoded.** Row 3's script first ran under Windows PowerShell 5, which wrote UTF-16 receipts. Their content was re-encoded to UTF-8 unchanged, and every later command ran under PowerShell 7.
- **No network.** No row and no gate step made a network request beyond the local API. Every video was made locally with the pinned FFmpeg.
- **The other session's files.** The download-reliability session's files are its own. `docs/proposals/2026-11-10-download-logic-divergence-report.md` was hashed for S3 and never opened.

### Departures and their basis

- **D-588** (MEU-134's handoff): `MediaPort.probe` gains `timeout_s` so AC-8.12 holds.
- **D-589**: two test lookups made assertion-shaped so row 2a's Red fails by assertion. The same lookup shape exists at `tests/e2e/test_api_captures.py:765-766`; it isn't changed, because it fails on no route this session adds.
- **D-590**: the stdout positive control counts at least one line.
- **D-592** (MEU-134's handoff): after execution review round 1, `parse_time` refuses a float above 1e9 seconds before the Decimal step. It touches no MEU-133 code.
- **The 08 Delivered note** sits after the Tests row at `:627`. The plan's §Spec text cited `:629`; the line had moved before this session.

---

## Decision Log

```yaml
decision_log:
  - id: D-589
    stage: execution
    question: "Row 2a: red-check refused two Red blocks, test_ac_16_6_each_route_index_row[POST-/api/v1/conversions/probe] and test_ac_31_17_openapi_static_auth_console[AC-31.17], which failed with KeyError on the new route's OpenAPI lookup rather than by assertion. How does row 2a go on?"
    resolution: autonomous
    class: two-way
    chosen: "A: assert path in paths before each lookup, only at test_api_openapi.py:121-122 and test_api_conversions.py:637-639, CRLF kept, then rerun row 2a whole"
    source_tag: Local Canon
    precedents:
      - "implementation-plan.md:368 — every Red fails by assertion, which red-check enforces"
      - "implementation-plan.md:159, :163, :304 — both files are on row 2a's modify list"
    research:
      engine: none
      sources: []
    reasoning: "A keeps both tests at least as strict and keeps rows 2a and 2b's exact commands. Loosening red-check (B) or narrowing the receipt (C, D) would spend the rule to save the test. Doing nothing leaves row 2a refused. Ruled by the Fable subagent under Mat's standing delegation, USER_EXPLICIT 2026-11-10 'for any questions ask fable subagent and accept ruling from it'. Two-way: two test lines."
    human_message_reference: null
  - id: D-590
    stage: execution
    question: "Row 3: AC-133.5's stdout positive control expected exactly one stdout line holding the marker and found two, the JSON line HealthService._process prints and the structlog console renderer's line. How does row 3 go on?"
    resolution: autonomous
    class: two-way
    chosen: "A: the stdout control becomes at least one line (test_api_conversion_probe.py:248), with a comment naming health.py:230; the ring control stays exactly one and every absence check is unchanged; rerun row 3"
    source_tag: Local Canon
    precedents:
      - "packages/core/src/avkit_core/services/health.py:230 — the console ring prints its own JSON line"
      - "tests/e2e/test_api_conversion_probe.py:245 — the ring control, still exactly one"
    research:
      engine: none
      sources: []
    reasoning: "Two lines per event is the console ring's design, not a defect. The control's job is to prove the capture would see the marker, and at least one proves it without pinning a renderer format. Changing the renderer (C) alters out-of-scope behaviour; pinning two lines (B) pins that format; doing nothing (D) blocks a correct implementation. Ruled by the Fable subagent under Mat's standing delegation, USER_EXPLICIT 2026-11-10 'for any questions ask fable subagent and accept ruling from it'. Two-way: one test line."
    human_message_reference: null
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-10 | claude-code-local (Claude Opus 5.5) | Initial MEU-133 handoff after the H1-2 gate |
| Updated | 2026-11-11 | claude-code-local (Claude Opus 5.5) | Execution review round 1 approved with F1; D-592 fixed it (MEU-134's handoff); the H1-2 gate reran |
