---
date: "2026-11-12"
project: "download-audio-extract"
meu: "MEU-142"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-12-download-audio-extract/implementation-plan.md"
build_plan_section: "bp03"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-12-youtube-client-runtime-MEU-140-handoff.md"
---

# Handoff: 2026-11-12-download-audio-extract-MEU-142-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-142 `svc-download-audio-extract`. It closes `DOWNLOAD-MP3-NOT-CONVERTED`.

- **The port.** `DownloadService` takes `media: MediaPort`, a required keyword after `youtube`. `build_services` passes it the one `FFmpegAdapter` that the conversion, TTS and Health services already hold (`MEDIA_PORT`, D-664).
- **What converts.** An audio-only `StandardMp3` job whose downloaded file is not already `.mp3` is converted to MP3 with `libmp3lame` at 192 kbps after the download, in any cookie mode (`AUDIO_EXTRACT`, `EXTRACT_TRIGGER`, D-665). No other format and no video job converts.
- **The name.** The MP3 takes a new name beside the source, with `-2`, `-3` and so on when a name is taken, so no existing file is opened or overwritten (`MP3_RESERVE`, D-666).
- **Done.** The Done row with the MP3's path and size is committed before the source is removed. A row removed during the convert keeps both files. A file that cannot be removed logs `download.source_kept` or `download.partial_kept` (`CONVERT_DONE`, `ROW_GONE`, `KEPT_LOGS`, D-667).
- **Failed.** A failed convert keeps the source, removes only the MP3 it reserved and fails the job with the ffmpeg not-found card (MEU-137's path), the `write_failed` card or `Download failed: MP3 convert failed.`. The Console detail is FFmpeg's last line with every path masked, or `[REDACTED]` (`CONVERT_FAIL`, `SOURCE_KEPT`, `FAIL_DETAIL`, `LAST_LINE`, D-668).
- **Cancel and rows.** A cancel during the convert lets the job finish Done, and the convert writes no `ConversionJob` row (`CONVERT_CANCEL`, `NO_CONVERSION_ROW`, D-669). CI deselects the real-FFmpeg module (`CI_DESELECT`, D-670).

No API route, schema, MCP tool or UI file changes. The OpenAPI snapshot does not move (H1-4).

**Build Plan Section**: bp03, `docs/build-plan/03-service-layer.md` §Construction and the MP3 residual section.

**Predecessor**: [MEU-140 handoff](2026-11-12-youtube-client-runtime-MEU-140-handoff.md), Session 66. This is the third and last session of the grouping `.agent/context/grouping/2026-11-10-download-reliability-session-grouping.md` (Sessions 65 to 67, MEU-137 to MEU-142). The grouping's decisions D-535, D-537 and D-542 carry.

**Execution authorization:** `USER_EXPLICIT`, 2026-11-12. Codex approved the plan at round 2. Mat ruled D-671 ("B: one live public download"), set the execution review budget ("30M") and authorized the run ("Yes, execute now").

**Receipts.** A receipt named by its file name alone (`s67-*.txt`) is in the session's receipts folder (`RECEIPTS_DIR`). A name starting `s67/` is in that folder's session subfolder. Full paths appear only in the evidence records' `command` fields.

### Where values go, as built (Session 50 RULE-1, Session 53 RULE-1, Session 61 RULE-1)

- **The port to the service.** `wiring.py:159` builds `media = FFmpegAdapter(...)`. The `DownloadService(` construction (`wiring.py:175`) passes `media=media` (`:178`), the same object as `ConversionService` (`:228`) and the TTS and Health services. `DownloadService.__init__` takes `media: MediaPort` (`services/download.py:257`) and stores `self._media` (`:265`). AC-142.3 checks the identity.
- **The trigger.** `_run_one` (`services/download.py:717`) reads `AUDIO_EXTRACT` (`:70`) with the job's `audio_format`, only when `audio_only` is set, and converts when the source's case-folded suffix differs from the map's (`:784-794`). The cookie settings are read by `_options_from` as before and play no part.
- **The source and MP3 paths.** The adapter's `DownloadResult.file_path` is the source. `_reserve` (`:213`) creates the MP3 with `open(path, "xb")`, and appends each name to the caller's `tried` list before it opens it (`:225`, the F1 correction). `_convert` (`:831`) calls `self._media.convert(source, mp3, options)` (`:843`) and returns the MP3 and its `stat().st_size`. `file_path` and `file_size` then go into the Done commit in place of the source's. No log field carries a path: `download.source_kept`, `download.partial_kept` and `download.failed` have none. The adapter's existing `media.convert` INFO line passes `input` and `output`, which are not in `CONSOLE_FIELDS`, so the Console shows `media.convert` alone. Live run 2's Console row reads `"message": "media.convert"` (`s67-live.txt`).
- **Done.** The Done unit of work re-reads the row. A missing row returns with no commit and no removal (`ROW_GONE`, `:798`). Otherwise it commits Done, logs `download.done` (`:821`), and only then `_remove`s the source (`:824`, `CONVERT_DONE`).
- **The convert's error text.** `FFmpegAdapter.convert` raises `FilesystemError(stderr)`; `_require_ffmpeg` raises `FFmpegNotFoundError`; the filesystem raises `OSError`. `_convert`'s one `except` maps them (`CONVERT_FAIL`):
  - `FFmpegNotFoundError` gives cause `other` with `safe_reason(scrub_line(str(exc)))`, so the card is `Download failed: ffmpeg binary was not found.`;
  - `OSError` gives `write_failed` and its card;
  - anything else gives cause `other` with `CONVERT_FAILED_REASON` (`:78`), `MP3 convert failed`.

  The card text comes from `download_failure_message` and goes to `_finish(Failed)`, the row's `error_message` and `download.failed`'s `error` (`:862`). The raw text goes only to `detail = _convert_detail(str(exc), (source, *tried))` (`:863`, the helper at `:200`), where `tried` holds every MP3 name `_reserve` tried, so a reservation that fails masks the name it failed on: `_mask_paths` (`:185`, with `_path_pattern` at `:180` and `_SEPARATOR_RUN` at `:177`) masks each path, each parent folder and each file name, then `last_line` (`:163`) and `scrub_line` take the tail, kept only when it is a suffix of the whole text's scrub. The detail is never stored on the row. From there structlog and `HealthService._process` (unchanged) write the Console row, stdout and `console.log`. AC-142.13 runs that chain through the real `HealthService`.
- **A removal error.** `_remove` (`:867`) logs `kept_event` with `error=type(exc).__name__` and leaves the job's status as it is (`KEPT_LOGS`).

### Row 1's caller grep (S55 RULE-1, S59 RULE-1, S62 RULE-4, S63 RULE-1)

Before its edits, row 1 grepped `packages/`, `tests/`, `tools/`, `ui/src` and `mcp-server/src` at `3435b7e`. The receipt is `s67-anchors.txt` (28 lines), which also holds each target's SHA-256 and line endings.

- **`DownloadService(` constructions:** `wiring.py:175`, `tests/e2e/real_stack.py:97`, `tests/e2e/test_api_error_surface.py:202`, `tests/integration/test_download_received_quality.py:150`, `tests/unit/test_download_failure_visibility.py:273`, `tests/unit/test_extract_options.py:91`, and `tests/unit/test_services.py:743`, `:971` and `:1514`.
- **`_run_one(` callers:** `services/download.py:589` only. `ConversionService` has its own `_run_one`.
- **`build_services(` callers:** `cli.py:204`, `main.py:75` and 29 test sites. None constructs `DownloadService` itself.
- **Fakes passed as `media`.** Each raises `AssertionError` from `convert`, and none of these tests runs a `StandardMp3` audio job:
  - `FakeMedia()` (`tests/unit/test_services.py:315`) in `test_services.py`, `test_extract_options.py`, `test_download_failure_visibility.py` and `test_download_received_quality.py`;
  - `StubMedia()` in `real_stack.py` (`:71`), which gained that `convert`;
  - `_Unreached()` (`test_api_error_surface.py:183`), the file's existing fake for unreached ports.
- **Source pins that read `services/download.py`**, all unchanged and passing: `test_conversion_service.py:459` and `:461` (AC-30.8: no `ConversionService`, no `conversion_jobs`), `test_capture_service.py:468-472`, `test_domain.py:1528` and `:1559`, and `test_api_downloads.py:622`.
- **Order and neighbour pins:** none.

### Row 2's Red tests (S50 RULE-2, S61 RULE-3)

Row 2 wrote two new files, both LF, and one test in an existing file:

- `tests/unit/test_download_audio_extract.py` covers AC-142.1, .2, .4 to .16 and .18, with a recording `MediaPort` fake, a trace unit of work and the real `HealthService` for AC-142.13.
- `tests/integration/test_download_audio_extract_real_ffmpeg.py` covers AC-142.17 with the pinned FFmpeg.
- `tests/integration/test_api_wiring.py:162` covers AC-142.3 (CRLF kept).

**Test names.** pytest pads a failure header to 80 columns, and red-check's header pattern needs three underscores on each side, so `s67/row2-rename.py` shortened thirteen functions and one set of parametrize ids before the accepted Red run. The `test_ac_142_N_` prefixes, the assertions and the fixtures are unchanged. Examples: `test_ac_142_4_only_audio_mp3_converts`, `test_ac_142_13_detail_never_leaks`, `test_ac_142_17_pinned_ffmpeg_makes_an_mp3`; AC-142.11's ids are `not-found`, `fs-partial` and `os-partial`.

**AC-142.6's trace.** Row 2 corrected the test's expected trace order before the accepted Red run. The trace as asserted (`test_download_audio_extract.py:392-399`) is: the Downloading commit, `download.started`, `download`, `convert` with the row reading Downloading, the Done commit with the MP3, its size, progress 1.0, `received_height` None and the archive entry, `download.done` with the source still present, and then the source gone.

### Row 3's Green changes (S55 RULE-1)

`services/download.py` (CRLF kept, 911 lines, by counted byte replacement in `s67/row3-edit.py`; 915 lines after the F1 correction below):

- `AUDIO_EXTRACT` holds the D-665 value, and `CONVERT_FAILED_REASON` is `MP3 convert failed`.
- `last_line`, `_SEPARATOR_RUN`, `_path_pattern`, `_mask_paths`, `_convert_detail` and `_reserve` are module helpers.
- `_run_one` converts after the SABR block and before the Done unit of work, commits the MP3's path and size, and removes the source after `download.done`.
- `_convert` and `_remove` are private methods before `_finish`.
- `FFmpegNotFoundError` joined the error imports.

Rows 4 and 5 added the CI deselect and the 03 spec text (§Changed Files).

### Execution review F1's correction

Codex's round 1 found that a failure inside `_reserve` leaked the MP3 name it tried. `mp3` was still `None`, so the detail masked only the source, and a denied create or a folder of that name put the tried name and its folder into the Console row, stdout and `console.log` (F1, High, AC-142.13 `FAIL_DETAIL`).

- **Red.** `s67/f1-red.py` added `test_ac_142_13_reserve_failure_never_leaks` (LF kept, 840 to 907 lines). It patches `Path.open` so that the `"xb"` create of the first name, or of `-2` beside an existing MP3, raises `PermissionError(13, ...)` with that path. Both ids failed on the leak alone (§FAIL_TO_PASS).
- **Green.** `s67/f1-green.py` made 3 counted replacements (CRLF kept, 911 to 915 lines). `_reserve` takes `tried: list[Path]` and appends each name before it opens it. `_convert` passes a new list and masks `(source, *tried)`. Row 3's command, rerun as `s67/f1-green.ps1`, gave `338 passed in 26.76s` (`s67-f1-green.txt`), pyright 0 errors, 0 warnings, 0 informations (`s67-f1-pyright.txt`) and ruff `All checks passed!` (`s67-f1-ruff.txt`); outer receipt `s67-f1-green-outer.txt`.
- No D-id and no AC changed. The fix is how `FAIL_DETAIL` (D-668) and AC-142.13 already read.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-142.1 | behaviour | `AUDIO_EXTRACT` equals the D-665 value exactly, and its keys over all 9 `AudioFormat` values are `StandardMp3` alone. `HighM4a` and `StandardM4a` are not keys | Local Canon: 02 `convert` row; D-665 | `tests/unit/test_download_audio_extract.py:219` | ✅ |
| AC-142.2 | type | `DownloadService.__init__`'s `media` is keyword-only, required, right after `youtube`, annotated `MediaPort`. Constructing without it raises `TypeError`. Row 1 added it, so it passed where row 2 wrote it | Local Canon: 03 §Construction; D-664 | `test_download_audio_extract.py:234` | ✅ |
| AC-142.3 | type | `build_services` gives `download._media`, `conversion._media`, `tts._media` and `health._media` one object, the `FFmpegAdapter`. It passed where row 2 wrote it | Local Canon: D-664 | `tests/integration/test_api_wiring.py:162` | ✅ |
| AC-142.4 | behaviour | `EXTRACT_TRIGGER`: over 9 formats × `audio_only` True and False, `convert` is called once exactly for audio-only `StandardMp3`, with the source, the reserved `.mp3` and the map's options. The 17 other cells call nothing, and a `.mp3` or `.MP3` source is not converted | Local Canon: 03 Convert and Tests rows | `test_download_audio_extract.py:267`, `:284` | ✅ |
| AC-142.5 | behaviour | `MP3_RESERVE`: `a.mp3`, then `a-2.mp3`, then `a-3.mp3`; each existing file keeps its bytes and is never passed to `convert` | Local Canon: D-666 | `test_download_audio_extract.py:302` | ✅ |
| AC-142.6 | behaviour | `CONVERT_DONE`: one job traced from the download to the source's removal (Session 55 RULE-3), with the row Downloading inside `convert` and the source still present at the Done commit | Local Canon: 03 Convert row; D-667 | `test_download_audio_extract.py:368` | ✅ |
| AC-142.7 | behaviour | `NO_CONVERSION_ROW`: on the SQLite stack a `StandardMp3` job ends Done with the MP3, and `conversion_jobs` holds no row | Local Canon: 03 No row; 08 §ConversionJob | `test_download_audio_extract.py:410` | ✅ |
| AC-142.8 | behaviour | The convert runs the same way with cookie mode none, browser and file | Local Canon: 03 Convert row; grouping D-542 | `test_download_audio_extract.py:453` | ✅ |
| AC-142.9 | behaviour | `FFmpegNotFoundError` gives Failed, `Download failed: ffmpeg binary was not found.`, one `download.failed` line with that `error`, and the source kept; no `download.done` line and no archive entry | Local Canon: 03 No ffmpeg; Session 65 CARD_REASON | `test_download_audio_extract.py:471` | ✅ |
| AC-142.10 | behaviour | `CONVERT_FAIL`: a `FilesystemError` gives `Download failed: MP3 convert failed.`, and an `OSError` gives the `write_failed` card, each its own parametrize id | Local Canon: D-668 | `test_download_audio_extract.py:499` | ✅ |
| AC-142.11 | safety | `SOURCE_KEPT`: after each failing convert the source's bytes are unchanged, the reserved or partial MP3 is gone, and a pre-existing `a.mp3` keeps its bytes | Local Canon: 03 Tests row; Session 56 RULE-3 | `test_download_audio_extract.py:527` | ✅ |
| AC-142.12 | behaviour | `LAST_LINE`: CR LF, CR and LF split; U+2028, U+0085 and form feed do not; trailing blank or control-only lines are skipped; a lone surrogate, control characters only and `""` never raise | Local Canon: D-668; Session 53 RULE-1 | `test_download_audio_extract.py:560` | ✅ |
| AC-142.13 | safety | `FAIL_DETAIL`: twelve cases through the real service to the real `HealthService` Console row, stdout and `console.log`. The ten leak cases find no secret, no part of the home folder past `~`, no file name and no folder path in any of the three. The two keep cases find FFmpeg's exact last line, and that line with `[file]`. The stored card holds none of them. Execution review F1 added two cases: `_reserve` failing on the first name and on a numbered name (`first-name`, `numbered-name`) keeps the source and any existing MP3, and the detail reads `[Errno 13] Permission denied: '[file]'` with neither the tried name nor its folder on any surface | Local Canon: Session 50 RULE-1, Session 65 RULE-1; execution review F1 | `test_download_audio_extract.py:648`, `:701` | ✅ |
| AC-142.14 | behaviour | `ROW_GONE`: a row removed, or the queue cleared, during the convert leaves both files and no row | Local Canon: D-667 | `test_download_audio_extract.py:771` | ✅ |
| AC-142.15 | behaviour | `KEPT_LOGS`: a failing source unlink after Done gives Done and one `download.source_kept`; a failing MP3 removal after a failed convert gives Failed and one `download.partial_kept`; neither holds a path, and a removal that succeeds logs no warning | Local Canon: D-667, D-668 | `test_download_audio_extract.py:813`, `:829`, `:851` | ✅ |
| AC-142.16 | behaviour | `CONVERT_CANCEL`: a cancel during the download gives Cancelled with no `convert` call; a cancel inside `convert` gives Done with the MP3 and the processor Idle with no next job started | Local Canon: D-669 | `test_download_audio_extract.py:865` | ✅ |
| AC-142.17 | behaviour | The pinned `packaging/ffmpeg-win64/` FFmpeg converts a generated 1 s `.m4a` through the real `FFmpegAdapter` and `DownloadService`: Done with an `.mp3` that `ffprobe` reads as one `mp3` audio stream, and the source gone. The module fails, never skips, when the pair is missing | Local Canon: 03 Tests row | `tests/integration/test_download_audio_extract_real_ffmpeg.py:76`; gate `real-ffmpeg` | ✅ |
| AC-142.18 | behaviour | The real `FFmpegAdapter` with no configured path, a missing bundle path and `shutil.which` patched to None gives `Download failed: ffmpeg binary was not found.` and keeps the source. It runs on CI | Local Canon: 03 No ffmpeg; MEU-78 resolver | `test_download_audio_extract.py:893` | ✅ |
| AC-142.19 | check | `CI_DESELECT`: `ci-collect.py` reads the Tests step's argv from `ci.yml` and finds the new module deselected exactly once | Local Canon: 03 Tests row | `docs/execution/plans/2026-11-12-download-audio-extract/ci-collect.py` (row 4, `s67-r4-ci-collect.txt`); gate `ci-collect` | ✅ |
| AC-30.8 (cross-ref) | regression | MEU-30's AC is owned by its handoff. Its source pins read `services/download.py` for `ConversionService` and `conversion_jobs`, and the new code names neither. Unchanged and passing | plan §Pins that move | `tests/unit/test_conversion_service.py:452`; gate `py-tests` | ✅ |
| AC-137 (cross-ref) | regression | MEU-137's failure path is reused, not changed: `download_failure_message`, `safe_reason`, `scrub_line`, the `write_failed` and `other` causes and the not-found card. Its tests are unchanged and passing | plan §Single-statement contracts (`CONVERT_FAIL`) | `tests/unit/test_download_failure_visibility.py`, `tests/integration/test_youtube_adapter_visibility.py`, `tests/e2e/test_api_download_visibility.py`; gate `py-tests` | ✅ |
| AC-78 (cross-ref) | regression | MEU-78's FFmpeg resolver is unchanged. AC-142.18 drives it with no path, no bundle and no `PATH` binary | plan AC-142.18 Source | `tests/integration/test_api_wiring.py:91`, `:110`; `tests/e2e/test_api_ffmpeg_resolution.py:65`, `:85`; gate `py-tests` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-142.1, AC-142.4 to AC-142.18 | Row 2, against the baseline service: `37 failed, 25 passed in 3.01s`, exit 1 (`s67-py-red.txt`). Decisive lines: `assert 0 == 1` ×23 and `AssertionError: assert 0 == 1` ×8 (no `convert` call); `where 0 = len([])` ×31; `RecordingMedia.calls == []`; `assert {} == {AudioFormat...}` (the empty map); the trace mismatch; `last_line` returning `''`; `a.m4a` or `clip.m4a` where the MP3 was expected; `(Done, None) == (... not found.)` | Row 3: `336 passed in 15.59s` (`s67-py-green.txt`); gate `py-tests` and `real-ffmpeg` | `test_download_audio_extract.py:219-893`, `test_download_audio_extract_real_ffmpeg.py:76` |
| AC-142.13, execution review F1 (`test_ac_142_13_reserve_failure_never_leaks`, ids `first-name` and `numbered-name`) | Against row 3's service: `2 failed in 0.43s`, exit 1 (`s67-f1-red.txt`). Decisive line in both: `AssertionError: assert [('console', ...', 's67clip')] == []`: the leak list is not empty, starting on the Console row. red-check: `1 receipt(s), 1 required test(s), 0 problem(s)` (`s67-f1-red-check.txt`) | After the fix: `338 passed in 26.76s` (`s67-f1-green.txt`); gate `py-tests` | `test_download_audio_extract.py:701` |
| AC-142.2, AC-142.3 | Type checks that row 1 met. Row 2's guard run: `2 passed, 59 deselected in 1.67s` (`s67-r2-guard.txt`) | Row 3 and gate `py-tests` | `test_download_audio_extract.py:234`, `test_api_wiring.py:162` |
| AC-142.19 | Before row 4, `ci-collect.py` exited 1 (`s67-plan-ci-collect-pre.txt`) | Row 4: `ci-collect: 0 problem(s)` (`s67-r4-ci-collect.txt`); gate `ci-collect` | `ci.yml:67` |

- **red-check.** Row 2's check (`s67-red-check.txt`) reads `red-check: 1 receipt(s), 16 required test(s), 0 problem(s)`. Every failing block failed by assertion alone.
- **The passes in the Red run** are AC-142.2 and AC-142.3, the other `test_api_wiring.py` tests, and the parametrize cells that need no convert (the 17 non-converting AC-142.4 cells and the `.mp3` sources).

### Live MP3 download (D-671 B; task row H1-2m)

Mat ruled D-671 B ("B: one live public download") at the plan gate. `s67/live-run.py` builds the real stack with `build_services` on a throwaway database and output folder in the session subfolder. It sets `cookie_mode` none and `archive_tracking` False, queues `https://www.youtube.com/watch?v=jNQXAC9IVRw` (public, 19 s) as an audio-only `StandardMp3` job, runs the worker and prints only the status, the error, the suffixes, the size match and the ffprobe streams. No cookie is read or stored.

| Run | Mat's words | Setting | Outcome |
|---|---|---|---|
| 1 | "Run it now" | `downloader.deno_path` empty (a fresh database) | Failed, `YouTube refused the download (page reload, SABR-only or bot check). Try again later.` yt-dlp logged `No supported JavaScript runtime could be found` and then `Sign in to confirm you're not a bot`. No file was written, so the convert step was not reached |
| 2 | "Retry once with Deno set" | `downloader.deno_path` set to `packaging/deno-win64/deno.exe` (`s67/live-run2.py`) | `status: Done`, `error_message: None`, `file suffix: .mp3`, `file exists: True`, `file_size matches disk: True`, `output folder suffixes: ['.mp3']`, `source removed (only the mp3 left): True`, `ffprobe streams: [('audio', 'mp3')]` |

- **Run 2's events, in order:** `download.started`, `youtube.download`, `media.convert` (its Console row holds the event alone), `download.done`.
- **Why run 1 failed.** `JsRuntimeLocator` (MEU-141) reads `downloader.deno_path`, then the bundled Deno in a frozen build only, then `deno` on `PATH`. The script ran from source on a fresh database, and this host has no `deno` on `PATH`, so yt-dlp had no JS runtime. That is MEU-141's approved lookup, not a MEU-142 change. The packaged app finds its bundled Deno.
- **Receipts.** `s67-live.txt` holds both runs under `===== H1-2m run 1` and `===== H1-2m run 2` headers, run 2 last. `s67-live2.txt` is run 2 alone. The H1-2m check (`s67-live-check.txt`, outer receipt `s67-H1-2m-outer.txt`) exits 0.
- **Its tested_state.** Both runs ran at gate run 1's tested_state, before the F1 correction, and were not repeated. F1 changed only how `_reserve` reports a name it failed to create; run 2's reservation succeeded, so its path through the code is the same after the fix.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s67-0-baseline", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-12-download-audio-extract/baseline.ps1 *> C:/Temp/av-kit/s67-baseline.txt (task.md row 0's Validation cell; base suites in C:/Temp/av-kit/s67-base-py.txt, s67-base-ui.txt, s67-base-mcp.txt, s67-base-mcp-build.txt and s67-base-ruff.txt; outer receipt C:/Temp/av-kit/s67-row0-outer.txt)", "scope": "Row 0: D-671 ruled, the queue, the shapes and absent names (S7), baseline.sha, the anchors and line endings, the lock sync, the FFmpeg pair, the base suites, and the red-check and identity selftests", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3435b7e before any row", "output": "D-671: chosen starts 'B:', reference starts 'USER_EXPLICIT 2026-11-12', ruled=True; queue: {'MEU-141': 'approved', 'MEU-142': 'pending'}; 3435b7e is an ancestor of HEAD: True; shapes wrong (S7): []; missing targets: [] new files already present: []; ui lock sync: 651 locked packages, 0 differ, 0 missing; mcp-server lock sync: 133 locked packages, 0 differ, 0 missing; ffmpeg.exe 165577728 B: ffmpeg version n8.1.3-27-g8dca1586f4-20261031; base pytest 2309 passed, 37 warnings in 170.41s (0:02:50); base UI Test Files 121 passed (121), Tests 1293 passed (1293); base MCP Test Files 36 passed (36), Tests 525 passed (525); ruff All checks passed!; red-check selftest: 47 fixture(s) (14 positive, 33 negative), 0 wrong; identity selftest: 0 failure(s); baseline: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s67-1-types", "command": "rtk proxy uv run pytest (row 1's guard files: test_services.py, test_download_failure_visibility.py, test_extract_options.py, test_conversion_service.py, test_download_received_quality.py, test_api_wiring.py, test_api_error_surface.py, test_api_downloads.py, test_api_conversions.py, test_api_client_fallback.py, test_api_download_visibility.py) --tb=short -q -rfE *> C:/Temp/av-kit/s67-types-py.txt; export_openapi.py --check *> C:/Temp/av-kit/s67-types-openapi.txt; pyright packages/ *> C:/Temp/av-kit/s67-types-pyright.txt; ruff check packages/ tests/ *> C:/Temp/av-kit/s67-types-ruff.txt (task.md row 1's Validation cell; outer receipt C:/Temp/av-kit/s67-row1-outer.txt; caller grep C:/Temp/av-kit/s67-anchors.txt)", "scope": "Row 1: MEDIA_PORT's signature and wiring, AUDIO_EXTRACT as an empty map, last_line as a stub, the fakes passed as media, and the caller grep", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3435b7e plus rows 0 to 1", "output": "278 passed in 25.30s; export_openapi --check exit 0; pyright 0 errors, 0 warnings, 0 informations; ruff All checks passed!; anchors: 28 lines"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s67-2-red", "command": "rtk proxy uv run pytest tests/unit/test_download_audio_extract.py tests/integration/test_download_audio_extract_real_ffmpeg.py tests/integration/test_api_wiring.py --tb=short -q *> C:/Temp/av-kit/s67-py-red.txt; red-check.py with the 16 --require ids *> C:/Temp/av-kit/s67-red-check.txt; pytest -k 'test_ac_142_2_ or test_ac_142_3_' *> C:/Temp/av-kit/s67-r2-guard.txt (task.md row 2's Validation cell; outer receipt C:/Temp/av-kit/s67-row2-outer.txt)", "scope": "MEU-142 Red: AC-142.1 and AC-142.4 to AC-142.18 against the baseline service, and AC-142.2 and AC-142.3 as passing type checks", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3435b7e plus rows 0 to 2", "output": "37 failed, 25 passed in 3.01s (child exit 1). Decisive: assert 0 == 1 x23; AssertionError: assert 0 == 1 x8; where 0 = len([]) x31; RecordingMedia.calls == []; assert {} == {AudioFormat...}; the trace mismatch; last_line returning ''; a.m4a or clip.m4a where the MP3 was expected; (Done, None) == (... not found.). red-check: 1 receipt(s), 16 required test(s), 0 problem(s). Guard: 2 passed, 59 deselected in 1.67s"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s67-3-green", "command": "rtk proxy uv run pytest (row 3's files: the MEU-142 tests, test_api_wiring.py and the row 1 guard files) --tb=short -q -rfE *> C:/Temp/av-kit/s67-py-green.txt; pyright *> C:/Temp/av-kit/s67-r3-pyright.txt; ruff check *> C:/Temp/av-kit/s67-r3-ruff.txt (task.md row 3's Validation cell; outer receipt C:/Temp/av-kit/s67-row3-outer.txt)", "scope": "MEU-142 Green: AUDIO_EXTRACT, EXTRACT_TRIGGER, MP3_RESERVE, CONVERT_DONE, ROW_GONE, KEPT_LOGS, CONVERT_FAIL, SOURCE_KEPT, FAIL_DETAIL, LAST_LINE, CONVERT_CANCEL, NO_CONVERSION_ROW, and the plan's guards", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3435b7e plus rows 0 to 3", "output": "336 passed in 15.59s; pyright 0 errors, 0 warnings, 0 informations; ruff All checks passed!"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s67-f1-red", "command": "uv run python C:/Temp/av-kit/s67/f1-red.py; TMP and TEMP C:/Temp/av-kit/s67/tmp; rtk proxy uv run pytest tests/unit/test_download_audio_extract.py::test_ac_142_13_reserve_failure_never_leaks --tb=short -q > C:/Temp/av-kit/s67-f1-red.txt 2>&1 (exit in C:/Temp/av-kit/s67-f1-red.txt.exit); red-check.py --require test_ac_142_13_reserve_failure_never_leaks C:/Temp/av-kit/s67-f1-red.txt > C:/Temp/av-kit/s67-f1-red-check.txt 2>&1", "scope": "Execution review F1, Red: a failure inside _reserve leaks the tried MP3 name and its folder (AC-142.13 FAIL_DETAIL), on the first name and on a numbered name", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3435b7e plus rows 0 to 6 and the F1 test", "output": "2 failed in 0.43s (child exit 1): test_ac_142_13_reserve_failure_never_leaks[first-name] and [numbered-name], each AssertionError: assert [('console', ...', 's67clip')] == []. red-check: 1 receipt(s), 1 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s67-f1-green", "command": "uv run python C:/Temp/av-kit/s67/f1-green.py; pwsh -NoProfile -File C:/Temp/av-kit/s67/f1-green.ps1 > C:/Temp/av-kit/s67-f1-green-outer.txt 2>&1 (row 3's Validation cell with receipts C:/Temp/av-kit/s67-f1-green.txt, s67-f1-pyright.txt and s67-f1-ruff.txt)", "scope": "Execution review F1, Green: _reserve records each tried name and _convert masks the source and every tried name", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3435b7e plus rows 0 to 6 and the F1 correction", "output": "3 replacements; CRLF 911->915. 338 passed in 26.76s; pyright 0 errors, 0 warnings, 0 informations; ruff All checks passed!"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s67-4-ci-deselect", "command": "rtk proxy uv run python docs/execution/plans/2026-11-12-download-audio-extract/ci-collect.py *> C:/Temp/av-kit/s67-r4-ci-collect.txt (task.md row 4's Validation cell)", "scope": "Row 4: CI_DESELECT, the Tests step's argv collected as CI holds it and without the new deselect", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3435b7e plus rows 0 to 4", "output": "--deselect tests/integration/test_download_audio_extract_real_ffmpeg.py: 1 occurrence(s); as CI holds it: exit=0 collected=2206 in the module=0; control without it: exit=0 collected=2207 in the module=1; control collects tests/integration/test_download_audio_extract_real_ffmpeg.py::test_ac_142_17_pinned_ffmpeg_makes_an_mp3; ci-collect: 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s67-5-spec", "command": "rtk proxy uv run python -c (row 5's four checks over docs/build-plan/03-service-layer.md) *> C:/Temp/av-kit/s67-r5-spec.txt (task.md row 5's Validation cell)", "scope": "Row 5 (D3): the 03 Construction row, the moved wiring citation and the Delivered (Session 67) note", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3435b7e plus rows 0 to 5", "output": "{'crlf_only': True, 'construction_row': True, 'delivered_note': True, 'stale_wiring_cite': True}"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s67-6-status", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s67/row6-run.ps1 > C:/Temp/av-kit/s67-row6-outer.txt (task.md row 6's Validation cell: the resolve receipt C:/Temp/av-kit/s67-resolve.txt, meu_status.py render --check *> C:/Temp/av-kit/s67-r6-render.txt, issue_triage.py render --check *> C:/Temp/av-kit/s67-r6-issues.txt and the status read *> C:/Temp/av-kit/s67-r6-status.txt; value checks C:/Temp/av-kit/s67-r6-semantic.txt and C:/Temp/av-kit/s67-r6-triage-diff.txt)", "scope": "Row 6: MEU-142 ready_for_review, DOWNLOAD-MP3-NOT-CONVERTED resolved with its verification, the triage move, the registry, BUILD_PLAN and known-issues renders, and grouping row 67 executed", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 3435b7e plus rows 0 to 6", "output": "issue-resolve: 0 problem(s); Drift check passed - SSOT loaded (142 MEUs, 12 phases), rendered regions match on-disk content; OK: known-issues.md is up-to-date; MEU-142: ready_for_review row 67: ['| 67 | `download-audio-extract` | MEU-142 | P2 | executed | `docs/execution/plans/2026-11-12-download-audio-extract/` |']"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s67-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-12-download-audio-extract/session-gate.ps1 *> C:/Temp/av-kit/s67-gate-h1.txt; then Select-String for ' exit=', 'not_run', 'skipped', 'tested_state', '_sha256 ', 'outside scope', 'mismatch', 'session-gate:' and exit $code (task.md row H1-2's Validation cell, run from P:/av-kit; outer receipt C:/Temp/av-kit/s67-h12-outer.txt; per-step receipts C:/Temp/av-kit/s67-D6-*.txt; rerun after execution review F1, run 1 saved in C:/Temp/av-kit/s67/gate-r1/)", "scope": "H1-2: the registered full gate. Static: py-types, py-lint, ui-types, ui-lint, task-contract, scope-paths, red-check-selftest, ci-collect. Full: py-tests, openapi, ui-tests, ui-build, mcp-types, mcp-build, mcp-tests, state-render, issues-render. Runtime: real-ffmpeg, ui-electron. Identity before and after. Skipped with reasons: mcp-audit, build-record, live-mp3-download", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "3435b7e516edd86a3d6ce3df497593907684012b+82610d5fa3ea22bb1029ccafb035c5e9c212971b68bc70f413ff5a9933101a90", "output": "py-types 0 errors, 0 warnings, 0 informations; py-lint All checks passed!; ui-types exit 0; ui-lint exit 0; task-contract OK: 25 row(s), 23 fully checked, 2 exempt (view_file): H1-5, H2-1; scope-paths changed paths: 34 outside scope: [] head: 3435b7e516edd86a3d6ce3df497593907684012b head moved (S3): False; red-check selftest: 47 fixture(s) (14 positive, 33 negative), 0 wrong: []; ci-collect as CI holds it: exit=0 collected=2208 in the module=0, control without it: exit=0 collected=2209 in the module=1; py-tests 2369 passed, 37 warnings in 157.31s (0:02:37); openapi exit 0; ui-tests Test Files 121 passed (121), Tests 1293 passed (1293); ui-build exit 0; mcp-types exit 0; mcp-build exit 0; mcp-tests Test Files 36 passed (36), Tests 525 passed (525); state-render Drift check passed (142 MEUs, 12 phases); issues-render OK: known-issues.md is up-to-date; real-ffmpeg 1 passed in 0.24s; ui-electron 26 passed (37.9s); tested_state before = after; session-gate: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s67-h1-2m-live", "command": "uv run python C:/Temp/av-kit/s67/live-run.py, then uv run python C:/Temp/av-kit/s67/live-run2.py, each once on Mat's words, recorded in C:/Temp/av-kit/s67-live.txt (run 2 alone in C:/Temp/av-kit/s67-live2.txt); then task.md row H1-2m's Validation cell *> C:/Temp/av-kit/s67-live-check.txt (outer receipt C:/Temp/av-kit/s67-H1-2m-outer.txt)", "scope": "H1-2m, D-671 B: one live public audio-only StandardMp3 download of jNQXAC9IVRw through the real wiring with cookies off, retried once with downloader.deno_path set", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "3435b7e516edd86a3d6ce3df497593907684012b+ccfabb992cab1d6ee498ab32db5ad604ee2050d378d115461b943047df5464f9", "output": "Run 1 (deno_path empty): status: Failed; error_message: YouTube refused the download (page reload, SABR-only or bot check). Try again later.; yt-dlp: No supported JavaScript runtime could be found, then Sign in to confirm you're not a bot; output folder suffixes: []. Run 2 (deno_path set): download.started, youtube.download, media.convert, download.done; status: Done; error_message: None; file suffix: .mp3; file exists: True; file_size matches disk: True; output folder suffixes: ['.mp3']; source removed (only the mp3 left): True; ffprobe streams: [('audio', 'mp3')]; exit 0"}
```

### Quality Gate Results

`s67-gate-h1-2` (H1-2) is the fresh full record. Its last line is:

> session-gate: all steps exit 0

- **Two runs.** The gate passed every step on its first run, at tested_state `3435b7e516edd86a3d6ce3df497593907684012b+ccfabb992cab1d6ee498ab32db5ad604ee2050d378d115461b943047df5464f9`. Execution review round 1 found F1, so the gate ran again after the correction and passed every step (`s67-gate-h1.txt`, outer receipt `s67-h12-outer.txt`). Run 1's receipts are kept in `s67/gate-r1/`. The counts below are run 2's. Its own `scope-paths` step lists the changed paths against `$scopePaths` (below).
- **Static checks.**
  - pyright: 0 errors, 0 warnings, 0 informations. ruff check: all checks passed. The UI typecheck and eslint exited 0.
  - lint_task_contract passed on 25 rows: 23 fully checked, with H1-5 and H2-1 exempt as `view_file`.
  - scope-paths found 34 changed paths, none outside scope. HEAD `3435b7e` did not move (S3).
  - The red-check selftest read 47 fixtures (14 positive, 33 negative), with 0 wrong.
  - ci-collect collected 2208 with the deselect and 0 from the module, and 2209 with 1 without it.
- **Suites.**
  - pytest: 2369 passed (`s67-D6-py-tests.txt`), the baseline's 2309 (`s67-base-py.txt`) plus 60: row 2's 58 and F1's 2. No skip or deselect line.
  - UI: 1293 passed in 121 files, the same as the baseline. MCP: 525 passed in 36 files, the same as the baseline.
  - Real FFmpeg: 1 passed in 0.24s (`s67-D6-real-ffmpeg.txt`). Electron E2E: 26 passed (`s67-D6-ui-electron.txt`).
- **Build and state.** `export_openapi.py --check`, the UI build, the MCP typecheck and the MCP build exited 0. The state render and the issue render match the files on disk.
- **After the gate.**
  - H1-1 (`s67-h11-outer.txt`) read `unchecked implementation rows: []`.
  - H1-3 (`s67-H1-3-outer.txt`) read `MEU-142 ready_for_review: True`, and `current-focus.md` gained the Session 67 paragraph.
  - H1-4 (`s67-H1-4-outer.txt`) read `openapi unchanged from baseline: True`.
- **Skipped.** Each skip has a reason in the gate:
  - `mcp-audit`: it needs the live network and YouTube, which the brief forbids;
  - `build-record`: no release and no package build in this session;
  - `live-mp3-download`: a recorded manual check after the gate, only on Mat's words (H1-2m, above).
- **Identity.**
  - The tested_state was the same before and after: `3435b7e516edd86a3d6ce3df497593907684012b+82610d5fa3ea22bb1029ccafb035c5e9c212971b68bc70f413ff5a9933101a90`.
  - The identity leaves out this plan's `*.md` files, this session's handoffs and reflection, `docs/execution/metrics.md` and `current-focus.md`, so writing them doesn't change it.
- **Warnings.** The gate's `py-tests` has 37 warnings, the same as the baseline. None is from this session's code.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/services/download.py` | modified | `media: MediaPort`, `AUDIO_EXTRACT`, `CONVERT_FAILED_REASON`, `last_line`, the path masking and `_convert_detail`, `_reserve`, the convert step in `_run_one`, `_convert` and `_remove` |
| `packages/api/src/avkit_api/wiring.py` | modified | `media=media` in the `DownloadService(` construction (row 1) |
| `tests/unit/test_download_audio_extract.py` | new | AC-142.1, .2, .4 to .16, .18, and F1's AC-142.13 test. LF, 907 lines |
| `tests/integration/test_download_audio_extract_real_ffmpeg.py` | new | AC-142.17. LF, 118 lines |
| `tests/integration/test_api_wiring.py` | modified | AC-142.3 |
| `tests/unit/test_services.py`, `tests/unit/test_download_failure_visibility.py`, `tests/unit/test_extract_options.py`, `tests/integration/test_download_received_quality.py`, `tests/e2e/real_stack.py`, `tests/e2e/test_api_error_surface.py` | modified | `media=` a fake whose `convert` raises (row 1); `StubMedia` gained `convert` |
| `.github/workflows/ci.yml` | modified | `CI_DESELECT` (row 4) |
| `docs/build-plan/03-service-layer.md` | modified | The Construction row, the moved wiring citation and a `Delivered (Session 67)` note (row 5) |
| `.agent/context/meu-status.yaml`, `meu-registry.md`, `docs/BUILD_PLAN.md`, `known-issues.yaml`, `known-issues.md`, `triage-output.yaml`, the grouping file | modified | Only MEU-142's fields and row, the one issue, and grouping row 67 (row 6) |
| `.agent/context/current-focus.md` | modified | Session 67's priority paragraph (H1-3) |

`git diff --stat 3435b7e` on the tracked files reads `19 files changed, 275 insertions(+), 71 deletions(-)` after the F1 correction (`s67-h16-diffstat.txt`). The untracked paths are this plan's folder, this handoff, the plan review and the two new test files.

- **`meu-status.yaml`'s reflow.** `meu_status.py update` re-serialized the quoting and line wrapping of MEU-137 to MEU-141 and the phase-3 note. Their values didn't change: `s67-r6-semantic.txt` compares the parsed files and finds only MEU-142's `execution_plan`, `status`, `labels` and `updated` changed. That is most of the file's 43-line diff.
- **`triage-output.yaml`.** `s67-r6-triage-diff.txt` finds the issue moved from actionable (38 to 37) to archived (88 to 89), and `core-download-mp3-not-converted` dropped from `proposed_batches` (2 to 1).

Line endings were measured with Python bytes before each edit and kept:

- **CRLF.** `services/download.py`, `wiring.py`, `real_stack.py`, `test_api_error_surface.py`, `test_services.py`, `test_api_wiring.py`, 03 and `current-focus.md`.
- **LF.** `test_download_received_quality.py`, `test_download_failure_visibility.py`, `test_extract_options.py`, `ci.yml`, `meu-status.yaml`, `meu-registry.md`, `BUILD_PLAN.md`, the issue files, `triage-output.yaml` and the grouping file.
- **New files** are LF.

```diff
 # services/download.py, _run_one (abridged)
+        file_path, file_size = result.file_path, result.file_size
+        extract = AUDIO_EXTRACT.get(job.audio_format) if job.audio_only else None
+        if extract is not None and result.file_path.suffix.casefold() != extract[0].casefold():
+            converted = self._convert(job, result.file_path, *extract)
+            if converted is None:
+                return
+            file_path, file_size = converted
         with self._uow_factory() as uow:
             latest = uow.downloads.get(job.id)
             if latest is None:
+                # ROW_GONE (D-667): removed or cleared during the download or the convert;
+                # no commit, and neither file is removed.
                 return
 ...
-                    "file_path": result.file_path,
-                    "file_size": result.file_size,
+                    "file_path": file_path,
+                    "file_size": file_size,
 ...
         log.info("download.done", job_id=job.id, video_id=job.video_id)
+        if file_path != result.file_path:
+            # CONVERT_DONE (D-667): the source goes only after the MP3's Done row is committed.
+            self._remove(job, result.file_path, "download.source_kept")
 # services/download.py, _convert (abridged)
+        mp3: Path | None = None
+        tried: list[Path] = []
+        try:
+            mp3 = _reserve(source, suffix, tried)
+            self._media.convert(source, mp3, options)
+            return mp3, mp3.stat().st_size
+        except Exception as exc:
+            if isinstance(exc, FFmpegNotFoundError):
+                cause = DownloadFailureCause.other
+                reason: str | None = safe_reason(scrub_line(str(exc)))
+            elif isinstance(exc, OSError):
+                cause, reason = DownloadFailureCause.write_failed, None
+            else:
+                cause, reason = DownloadFailureCause.other, CONVERT_FAILED_REASON
+            if mp3 is not None:
+                self._remove(job, mp3, "download.partial_kept")
+            stored = download_failure_message(cause, reason)
+            self._finish(job.id, DownloadStatus.Failed, error=stored)
+            log.error("download.failed", job_id=job.id, video_id=job.video_id, error=stored,
+                      detail=_convert_detail(str(exc), (source, *tried)))
+            return None
 # api/wiring.py, the DownloadService construction
+        media=media,
 # .github/workflows/ci.yml, the Tests step
+          --deselect tests/integration/test_download_audio_extract_real_ffmpeg.py
```

The excerpt is abridged. The source is `services/download.py:784-824` and `:831-865`; `_reserve` is at `:213-232`.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

Codex reviews the execution in one rolling report, `2026-11-12-download-audio-extract-implementation-critical-review.md`, on the ledger loop `s67-execution-2026-11-12-download-audio-extract`. The table is filled in as the rounds return.

| Round | Verdict | Findings | Tested state |
|-------|---------|----------|--------------|
| 1 | changes_required | F1 (High, blocking, AC-142.13 `FAIL_DETAIL`): a failure inside `_reserve` left `mp3` as `None`, so the Console detail leaked the tried MP3 name and its folder. Corrected and gate rerun (§Execution review F1's correction) | `3435b7e516edd86a3d6ce3df497593907684012b+ccfabb992cab1d6ee498ab32db5ad604ee2050d378d115461b943047df5464f9` |
| 2 | approved | F1 fixed; no new finding. Codex reran its round 1 repro and probes against the corrected code and recomputed the tested_state, which matched | `3435b7e516edd86a3d6ce3df497593907684012b+82610d5fa3ea22bb1029ccafb035c5e9c212971b68bc70f413ff5a9933101a90` |

### Verdict

**approved** at round 2 of 6, with 0 open blocking findings (`review-state-check.txt`, `exec-review.txt`; outer receipts `s67-H1-7a-outer.txt` and `s67-H1-7b-outer.txt`). The ledger recorded round 1 at 9,449,629 tokens and round 2 at 3,799,263 (`dispatch/s67-exec-outer-r2.txt`).

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| A script that calls `build_services` from source on a fresh database has no JS runtime on this host, because `deno` is not on `PATH` and the bundled Deno is read only in a frozen build. Live run 1 failed at YouTube's bot check for that reason | observation | None | MEU-141's approved lookup (`JsRuntimeLocator`, `youtube/js_runtime.py:63`). The packaged app and a dev setup with `downloader.deno_path` set or `deno` on `PATH` are not affected. Not a MEU-142 change |
| Commit and push | out-of-scope | — | Only on Mat's words, after Codex approves (H2-5) |

### Departures and their basis

1. **Test names (row 2).** Thirteen MEU-142 test functions and AC-142.11's parametrize ids were shortened so that red-check reads every failure header (§Row 2's Red tests). The AC ids, assertions and fixtures are unchanged.
2. **AC-142.6's trace.** Row 2 corrected the expected trace order before the accepted Red run. The trace asserts the plan's order: the Done commit, then `download.done`, then the source's removal.
3. **`_Unreached()` as `media`.** The plan's pin table names `FakeMedia` or `StubMedia` for each construction. `test_api_error_surface.py` already has `_Unreached()` for ports its tests never reach, so row 1 passed that instead. It raises on any call, as the plan requires.
4. **A second live run.** D-671 B is one live public download. Run 1 failed before the convert step for want of a JS runtime, and Mat chose to retry once with `downloader.deno_path` set ("Retry once with Deno set"). Run 2 is the recorded result.
5. **`meu-status.yaml`'s reflow.** The status tool re-serialized MEU-137 to MEU-141's quoting and wrapping. `s67-r6-semantic.txt` shows that no value but MEU-142's changed.

No execution-stage decision was added. D-664 to D-671 are the plan's, with stage `planning`.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-12 | claude-code-local (Claude Opus 5.5) | The AC table, where values go, row 1's caller grep, the Red and Green receipts, the H1-2 gate, the live MP3 download and the evidence records (H1-6) |
| Corrected | 2026-11-12 | claude-code-local (Claude Opus 5.5) | Execution review round 1's F1: the Red test, the `_reserve` fix, the Green run, the gate's second run and the moved line numbers; H1-6 to H1-6b rerun |
