---
date: "2026-11-12"
project: "youtube-client-runtime"
meu: "MEU-140"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-12-youtube-client-runtime/implementation-plan.md"
build_plan_section: "bp03"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-11-download-failure-visibility-MEU-139-handoff.md"
---

# Handoff: 2026-11-12-youtube-client-runtime-MEU-140-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-140 `infra-youtube-client-fallback`. It closes `DOWNLOAD-CLIENT-PIN-MISSES-WORKING-CLIENT`.

- **Attempt 1 lets yt-dlp choose its client.** It sets no `extractor_args` in any cookie mode (`ATTEMPT_OPTS`).
- **One pinned retry.** A client-side error (`CLIENT_SIDE`) gets one attempt 2 with `COOKIE_EXTRACTOR_ARGS` and the same cookie opts (`RETRY_ONCE`, D-643, D-654).
- **Logging.** A failed attempt that retries logs `youtube.attempt_failed`, and a SABR phrase in either attempt sets `sabr_detected` (`ATTEMPT_LOG`, `SABR_ACROSS`).
- **Catch-all.** Each height selector ends with `/best` (`CATCH_ALL`).
- **The add-time extract.** It gets the download's cookie options and the same attempt sequence (`ADD_OPTS`). Its cache key includes the cookie fields (`ADD_CACHE_KEY`, D-646).

MEU-141 (`infra-ytdlp-js-runtime`) ran in this session too. Its ACs (AC-141.1 to AC-141.16) and its packaging cross-references (AC-25, AC-51, AC-68, AC-72, AC-78, AC-81, AC-110, AC-113) are in the [MEU-141 handoff](2026-11-12-youtube-client-runtime-MEU-141-handoff.md).

**Predecessor**: [MEU-139 handoff](2026-11-11-download-failure-visibility-MEU-139-handoff.md), Session 65. This is the second session of the grouping `.agent/context/grouping/2026-11-10-download-reliability-session-grouping.md` (Sessions 65 to 67, MEU-137 to MEU-142).

**Execution authorization:** `USER_EXPLICIT`, 2026-11-12. Mat ruled the gate decisions ("all recommendations are accepted"): D-640 A, D-641 D and D-642 A. The execution review budget is 37.5M tokens.

**Receipts.** A receipt named by its file name alone (`s66-*.txt`) is in the session's receipts folder (`RECEIPTS_DIR`). A name starting `s66/` is in that folder's session subfolder. Full paths appear only in the evidence records' `command` fields.

### Where values go, as built (Session 50 RULE-1, Session 53 RULE-1, Session 61 RULE-1)

- **Cookie settings to the download.** `_download_options` (`services/download.py:546`) reads the downloader path, `cookie_mode`, `cookie_browser`, `cookie_browser_profile` and `cookie_file_path` fresh at each call. Both callers use it:
  - `_options_from` (`:543`) for a queued job;
  - `add_to_queue` (`:265`) for the add-time extract.

  The resulting `DownloadOptions` reaches `YouTubeAdapter.download` (`adapter.py:748`) or `extract_info` (`:707`).
- **Options to yt-dlp.** `_attempt_sequence` (`adapter.py:621`) builds each attempt's options in three steps:
  - `opts_for(logger)`, which is `_base_opts` (`:553`) plus the format and output template, or `_extract_opts` for an extract;
  - `_attempt_opts(options, attempt)` (`:606`) overlaid on them. It drops `_cookie_opts`' `extractor_args` for attempt 1 and sets `COOKIE_EXTRACTOR_ARGS` (`:79`) for attempt 2. `cookiesfrombrowser` and `cookiefile` are kept in both attempts;
  - a fresh `_YtDlpLogger` per attempt.

  `_cookie_opts` itself is unchanged, so `check_sabr_status` (`:821`) still runs once with `SABR_EXTRACTOR_ARGS` (`:84`), and `test_cookies` is unchanged (AC-140.12).
- **yt-dlp's error text.** A `DownloadError` from attempt 1 is tested by `client_side_error(text, logger.sabr_detected)` (`:401`):
  - a `NO_RETRY_NEEDLES` needle (`:128`) anywhere in the case-folded text refuses the retry;
  - otherwise a `RETRY_NEEDLES` needle (`:134`), a SABR phrase in the text, or a SABR match in attempt 1's log retries.

  Only on a retry does attempt 1's text leave the adapter, as `youtube.attempt_failed`'s `detail = scrub_line(detail)` (`:666`), where `detail` is `classify_download_error`'s first line (D-655). With it go `attempt`, `clients` (`ATTEMPT_CLIENTS[1]`, `"default"`, `:136`) and `cause`. The Console keeps only the event and `detail`, because `CONSOLE_FIELDS` is unchanged (AC-140.6, AC-140.7).
- **The final failure.** A non-retrying error, or attempt 2's, is raised through `fail(exc, logger)` with that attempt's own logger (D-657):
  - `_download_failure` (`:428`) for a download, which gives `DownloadFailedError(cause, detail)`;
  - `_extract_failure` (`:421`) for an extract, which gives `AgeRestrictedError` or `ExtractError`, as before.

  In the service, `_run_one`'s one branch (`services/download.py:675`) runs `scrub_line` over it and logs `download.failed` (`:682`), as in Session 65.
- **A stop between attempts.** `download` passes `stoppable=True`. When `should_stop()` is true after a failed attempt 1, it raises `DownloadCancelledError` and runs no attempt 2 (`:657`, AC-140.5). The add-time extract passes `stoppable=False`, because it has no job to stop (D-656).
- **`sabr_detected`.** `sabr_seen` ORs each attempt's logger (`:653`, `:670`) into `DownloadResult.sabr_detected` (`:804`). `youtube.download` logs it with `attempt` (`:807-812`, AC-140.8).
- **The add-time extract's cache.** `ExtractCoordinator.extract_info` (`services/extract.py:37`) keys a call that has options by `(url, flat, mode, browser, profile, cookie_file)` (`:47`), and a call without options by `(url, flat)` as before. It forwards `options=` only when it is given (`:58-61`), so the transcript path's port call is unchanged (AC-140.9, AC-140.10).
- **A missing cookie file at add time.** `_cookie_opts` raises `CookieTestError` before any run, and `avkit_api/errors.py:31` maps it to 422. No job row is written (AC-140.11).

### Row 1's caller grep (S55 RULE-1, S59 RULE-1, S62 RULE-4)

Before its edits, row 1 grepped `packages/`, `tests/`, `tools/`, `ui/` and `mcp-server/` for every caller and fake of these names:

- `extract_info(`, `_cookie_opts(`, `_quality_selector(` and `_base_opts(`;
- `YouTubeAdapter(`, `ExtractCoordinator(`, `DependencyHealth(`, `DependenciesOut(` and `HealthService(`;
- `SETTINGS_KEY_TABLE`, `bundled_ffmpeg(` and `ISOLATION_INPUT_KEYS`.

The receipt is `s66-callers.txt` (193 lines). It is also recorded in `s66-anchors.txt`.

| Name | Sites |
|---|---|
| `extract_info(` | 40 |
| `YouTubeAdapter(` | 68 |
| `SETTINGS_KEY_TABLE` | 25 |
| `ExtractCoordinator(` | 13 |
| `HealthService(` | 13 |
| `_base_opts(` | 6 |
| `ISOLATION_INPUT_KEYS` | 5 |
| `_cookie_opts(` | 3 |
| `bundled_ffmpeg(` | 3 |
| `_quality_selector(` | 2 |
| `DependenciesOut(` | 2 |
| `DependencyHealth(` | 1 |

| File | Hits |
|---|---|
| `tests/integration/test_youtube_adapter.py` | 69 |
| `packages/infrastructure/src/avkit_infra/youtube/adapter.py` | 16 |
| `tests/unit/test_services.py` | 14 |
| `tests/integration/test_youtube_adapter_visibility.py` | 13 |
| `tests/unit/test_capture_service.py` | 9 |
| `packages/core/src/avkit_core/services/settings.py` | 8 |
| `tests/unit/test_transcript_flat_extract.py` | 7 |
| `tests/unit/test_conversion_service.py` | 6 |
| `packages/api/src/avkit_api/wiring.py` | 5 |
| `tests/integration/test_download_received_quality.py` | 4 |
| `mcp-server/scripts/audit/classify.ts` | 3 |
| `mcp-server/scripts/audit/run.ts`, `mcp-server/tests/audit/isolation.test.ts`, `services/extract.py`, `tests/integration/test_transcript_failure_delivery.py`, `tests/e2e/test_api_capture_flatten.py` | 2 each |
| `ports/youtube.py`, `services/download.py`, `services/transcript.py`, `services/health.py`, `schemas/health.py`, `routes/health.py`, `tests/e2e/real_stack.py`, `tests/e2e/test_api_error_surface.py`, `tests/e2e/test_api_download_visibility.py`, `tests/e2e/test_api_tts_runtime.py`, `tests/unit/test_transcript_metadata.py`, `tests/unit/test_download_failure_visibility.py`, `tests/unit/test_console_level.py`, `tests/unit/test_ffmpeg_bundle_wire.py`, `tests/unit/test_uow_commit_log.py`, `tests/integration/test_extract_real_ffmpeg.py`, `tests/integration/test_api_wiring.py` | 1 each |

- **Callers of `extract_info`.**
  - `services/download.py:266` calls `coordinator.extract_info(url.strip(), options=options)` (the add path).
  - `services/transcript.py:155` calls `coordinator.extract_info(url, flat=True)`.
  - The adapter's `get_formats` calls `self.extract_info(..., flat=False)`.
  - The two `mcp-server/scripts/audit/run.ts` hits are yt-dlp's own `YoutubeDL.extract_info` in an audit script, not the port.
- **Fakes that took `options` in row 1.** Each takes `options: object = None` and ignores it. The transcript fake in `tests/unit/test_transcript_flat_extract.py` is unchanged. The fakes are:
  - two in `tests/unit/test_services.py`;
  - the StubCoordinator in `tests/e2e/real_stack.py`;
  - one each in `tests/e2e/test_api_error_surface.py` and `tests/integration/test_download_received_quality.py`.
- **Pins moved in row 1.** `test_ac_4_7_port_method_sets_and_signatures` (`tests/unit/test_domain.py:1336`) and `test_ac_122_6_playlist_info_and_extract_info_unchanged` (`tests/unit/test_transcript_metadata.py:129`). Both now end with `"options"`, with a default of None.
- **`_cookie_opts`.** `test_cookies` calls it, and it stays unchanged. `_attempt_opts` is the new per-attempt wrapper.

### Row 1's MEU-141 pin sweep (S59 RULE-1, S62 RULE-4, S63 RULE-1)

The receipt is `s66/row1-pin-sweep.txt` (92 lines), grouped by name, neighbour and count. It is also recorded in `s66-anchors.txt`. It has no `deno_path` hit yet. Rows 1b and 2b moved these pins. The [MEU-141 handoff](2026-11-12-youtube-client-runtime-MEU-141-handoff.md) records each move.

- **`yt_dlp_debug`, the last downloader leaf and the new leaf's neighbour**, in:
  - `ui/tests/unit/settings-page.test.ts` (9);
  - `tests/integration/test_youtube_adapter_visibility.py` (5);
  - `ui/tests/unit/downloader-page.behavior.test.ts` and `tests/integration/test_api_wiring.py` (3 each);
  - `ui/tests/unit/settings-rail.test.tsx` (2);
  - `ui/tests/unit/settings-mcp-prompt.test.ts`, `ui/tests/unit/convert-page.behavior.test.ts` and `tests/unit/test_download_failure_visibility.py` (1 each).
- **Order.** Neither of these pins fixes the downloader leaves in order, so a `deno_path` path leaf moves neither:
  - `settings-page.test.ts:228-237` only checks that each listed leaf is present;
  - `settings-rail.test.tsx:175` pins `CHECKBOX_COPY_SOURCES`, which lists checkboxes only.
- **Health rows and fields.**
  - `DEPS_.*_ROW`: `ui/tests/e2e/settings.test.ts` (2).
  - `tts_espeak`: `ui/tests/unit/settings-tts-runtime.test.ts` (3), `tests/e2e/test_api_tts_runtime.py` (2), and `ui/tests/unit/settings-page.test.ts`, `tests/e2e/test_api_health_settings.py`, `tests/e2e/test_api_auth.py` and `tests/e2e/api_fakes.py` (1 each).
  - `ffprobe_available`: `tests/e2e/test_api_ffmpeg_resolution.py` (3), and `ui/tests/e2e/settings.test.ts`, `ui/tests/e2e/mcp-setup-prompt.test.ts`, `tests/e2e/test_api_health_settings.py`, `tests/e2e/test_api_auth.py` and `tests/e2e/api_fakes.py` (1 each).
- **Packaging.** `hiddenimports` and `collect_data_files`: `tests/unit/test_packaging_backend.py` (3).
- **Audit isolation.** `ISOLATION_INPUT_KEYS` and `cookie_file_path`: `mcp-server/tests/audit/isolation.test.ts` (2 each).

### Row 2a's Red tests (S50 RULE-2, S61 RULE-3)

Row 2a wrote three new files, all LF:

- `tests/integration/test_youtube_client_fallback.py` covers AC-140.1 to .5, .8 and .12, with a scripted `YoutubeDL` (`_script`) that records each run's options.
- `tests/unit/test_extract_options.py` covers AC-140.9 and AC-140.10.
- `tests/e2e/test_api_client_fallback.py` covers AC-140.6, .7 and .11 on the real stack (`build_services`), where only `YoutubeDL` is scripted.

Two pins in `tests/integration/test_youtube_adapter.py` moved. CRLF was kept, by byte replacement.

- `test_ac_6_6_quality_selectors_exhaustive` (`:346`) now expects the `/best` catch-all at the end of each height selector.
- `test_ac_6_16_extractor_args_cookie_vs_sabr` (`:604`) now expects attempt 1 to have no `extractor_args`, in mode none and in mode file.

**ATTEMPT_LOG's detail and the Console row (D-655, plan YAML).**

- The `youtube.attempt_failed` detail is `scrub_line` of the classifier's detail.
- The Console row shows only the event and that detail, because `CONSOLE_FIELDS` is unchanged. AC-140.6 therefore checks `attempt`, `clients` and `cause` through `capture_logs`, and the Console row through the API.

**Test names.** The first run's red-check refused the receipt with 31 blocks for 59 failures.

- **Why.** pytest pads a failure header with underscores to 80 columns. A title longer than 72 characters gets fewer than three underscores on each side, and red-check's header pattern needs three.
- **The fix.** Five functions were shortened, keeping their `test_ac_140_N_` prefixes, and every collected title is now 72 characters or less:
  - `test_ac_140_3_retries_once_on_cookie_pin`;
  - `test_ac_140_3_attempt_two_fails_with_its_cause`;
  - `test_ac_140_4_no_retry_runs_once`;
  - `test_ac_140_5_stop_between_attempts`;
  - `test_ac_140_7_console_scrubbed`.

  `test_ac_140_9_no_options_no_cookies_one_run` was shortened for the same reason.

### Row 3's Green changes (S55 RULE-1)

- **`youtube/adapter.py` (CRLF kept).**
  - `client_side_error` holds `CLIENT_SIDE` (D-643). It reads `NO_RETRY_NEEDLES` first across the whole text: the age gate, both bot checks, the cookie needles and the write needles. Then it reads `RETRY_NEEDLES` (the format needles and the reload page), then a SABR phrase in the text or the log.
  - `_attempt_opts` drops `_cookie_opts`' `extractor_args` for attempt 1 and sets `COOKIE_EXTRACTOR_ARGS` for attempt 2. `_cookie_opts` is unchanged, so `test_cookies` and `check_sabr_status` are unchanged.
  - `_attempt_sequence` is the one private method that `download`, and `extract_info` with options, call. It holds `ATTEMPT_OPTS`, `RETRY_ONCE`, `ATTEMPT_LOG` and `SABR_ACROSS`.
  - `download` passes `stoppable=True`. `extract_info` with options passes False (D-656).
  - A failed attempt 2 is classified with its own logger (D-657).
  - `_quality_selector` ends each height selector with `/best` (`CATCH_ALL`).
  - `youtube.download` gains `attempt`.
  - `_extract_failure` is the one DownloadError mapping for both extract paths, so `_run_extract` keeps its errors.
- **`services/download.py` (CRLF kept).** `_download_options(quality, audio_only, audio_format)` reads the cookie settings fresh. `_options_from` and `add_to_queue` both call it (`ADD_OPTS`).
- **`services/extract.py` (LF).** `ADD_CACHE_KEY`. The coordinator forwards `options=` only when it is given.
- **`ports/youtube.py` (LF).** `extract_info` gains `options: DownloadOptions | None = None`, last.

### Row 3s: the split point and the context state (D-641)

- **S3.** HEAD is `0553779` (`baseline.sha`), and `git status --porcelain` lists only this plan's paths.
- **Context state.** The session's context was compacted once before row 2a finished. After that, the window was about a third used.
- **Active set.** D-641 is ruled D, so neither a ruling nor the context share calls for a split. `active-meus.txt` reads `MEU-140 MEU-141` (LF), and rows 4, 1b, 2b and 5 ran in this session.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-140.1 | behaviour | Attempt 1 sets no `extractor_args` in modes none, browser and file. Browser mode keeps `cookiesfrombrowser`, and file mode keeps `cookiefile`. `_attempt_opts` pins `COOKIE_EXTRACTOR_ARGS` only for attempt 2 | Human-approved: D-539 | `tests/integration/test_youtube_client_fallback.py:155`, `:176` | ✅ |
| AC-140.2 | behaviour | `CATCH_ALL`: each height preset ends `/best`, and the download passes that format. `Best`, `Lowest` and every audio selector are unchanged, compared whole | Local Canon: 02 Catch-all row | `test_youtube_client_fallback.py:194`, `:210` | ✅ |
| AC-140.3 | behaviour | `RETRY_ONCE` on each client-side error in each cookie mode: exactly two `YoutubeDL` runs, the second with `COOKIE_EXTRACTOR_ARGS` and the same cookie opts. A passing attempt 2 returns its `DownloadResult`. A failing attempt 2 raises with its own cause, and no third run happens | Human-approved: D-539; Local Canon: 02 Tests row | `test_youtube_client_fallback.py:240`, `:260` | ✅ |
| AC-140.4 | guard | Exactly one run, and the same error as at `0553779`, on each of these: a bot check, a cookie cause, a write failure, other text, `DownloadCancelledError`, `CookieTestError`, an age gate and an `OSError`. Each case is its own parametrize id. `CLIENT_SIDE`'s precedence cases also run once: a SABR phrase in attempt 1's log followed by a bot, cookie or write error, and a multiline text that holds a format error and a cookie error. It passed where row 2a wrote it, and it ran again after row 3 | Local Canon: 02 Tests row; D-643 | `test_youtube_client_fallback.py:422` | ✅ |
| AC-140.5 | behaviour | A stop requested after a failed attempt 1 raises `DownloadCancelledError` and runs no attempt 2. When `should_stop` is False, attempt 2 runs | Local Canon: 02 Tests row | `test_youtube_client_fallback.py:446` | ✅ |
| AC-140.6 | behaviour | `ATTEMPT_LOG`: a failed attempt 1 logs one `youtube.attempt_failed` warning with `attempt=1`, `clients="default"`, the cause and the scrubbed first line. When attempt 2 also fails, the service's `download.failed` line follows with attempt 2's cause. The test traces this from the port call to the Console rows. No `attempt_failed` line is logged when attempt 1 passes | Human-approved: D-539; grouping :65; D-655 | `tests/e2e/test_api_client_fallback.py:89`, `:123`, `:157` | ✅ |
| AC-140.7 | behaviour | Attempt 1's text reaches the Console only through `scrub_line`. Split secret and home-folder text is driven through the real adapter, service and Console store. A lone surrogate, control characters and empty text give a clean or empty `detail` and never raise. The raw secret and the raw home folder are absent from every row | Local Canon: D-639, Session 65 RULE-1, Session 53 RULE-1 | `test_api_client_fallback.py:227` | ✅ |
| AC-140.8 | behaviour | `SABR_ACROSS`: a SABR phrase in attempt 1's log and a passing attempt 2 give `sabr_detected=True`, and no phrase in either attempt gives False. `youtube.download` carries `attempt` | Local Canon: D-645; D-657 | `test_youtube_client_fallback.py:476`, `:494`, `:509` | ✅ |
| AC-140.9 | behaviour | `ADD_OPTS`: `add_to_queue` passes `DownloadOptions`, built from its arguments and the cookie settings read fresh, to the coordinator and the port. The adapter's `extract_info` with options applies the cookies and the same attempt sequence. The negative tests check three cases: a bot check doesn't retry, a missing cookie file runs nothing, and `extract_info` without options (the transcript path) sets no cookie opts and runs once | Local Canon: 02 Add-time check row; D-656 | `tests/unit/test_extract_options.py:112`, `:129`, `:152`, `:180`, `:197`, `:211`, `:221`, `:232`, `:245` | ✅ |
| AC-140.10 | behaviour | `ADD_CACHE_KEY`: a cookie mode change within the TTL misses the cache, each cookie field is in the key, and the same options hit it. The no-options key is unchanged for the transcript path | Local Canon: D-646 | `test_extract_options.py:286`, `:309`, `:339`, `:353`, `:363` | ✅ |
| AC-140.11 | behaviour | `POST /downloads` with cookie mode file and a missing file answers 422 with the cookie message and creates no job row. The same add with mode none creates the row | Local Canon: D-646; `avkit_api/errors.py:31` | `test_api_client_fallback.py:271`, `:296` | ✅ |
| AC-140.12 | guard | `check_sabr_status` still uses `SABR_EXTRACTOR_ARGS` and runs once, and an error in it does not retry. It passed where row 2a wrote it | Local Canon: 02 §SABR check result | `test_youtube_client_fallback.py:527`, `:542` | ✅ |
| AC-6 (cross-ref) | regression | MEU-6's ACs are owned by its handoff. These are moved pins. AC-6.6 (`test_youtube_adapter.py:346`) now expects each height selector to end `/best`. AC-6.16 (`:604`) now expects attempt 1 to have no `extractor_args` in modes none and file. Both failed in row 2a and pass from row 3 | plan §Pins that move | `tests/integration/test_youtube_adapter.py:346`, `:604`; gate `py-tests` | ✅ |
| AC-4 (cross-ref) | regression | Moved pin: AC-4.7 (`test_domain.py:1336`) now expects `YouTubePort.extract_info`'s parameters `["self", "url", "flat", "options"]`, with `options` defaulting to None. The test's other checks are unchanged. Moved in row 1 | plan §Pins that move | `tests/unit/test_domain.py:1336`; gate `py-tests` | ✅ |
| AC-122 (cross-ref) | regression | Moved pin: AC-122.6 (`test_transcript_metadata.py:129`) now expects the port's hints to also hold `"options": DownloadOptions \| None`, with `options` defaulting to None. `PlaylistInfo`'s fields, the return type and `flat`'s default False stay pinned as written, so the guard still stops a wider download type (D-346). Moved in row 1 | plan §Pins that move | `tests/unit/test_transcript_metadata.py:129`; gate `py-tests` | ✅ |
| AC-141 (cross-ref) | regression | MEU-141's sixteen ACs are owned by the [MEU-141 handoff](2026-11-12-youtube-client-runtime-MEU-141-handoff.md). Its `js_runtimes` key reaches both of this MEU's attempts and the add-time extract (AC-141.5) | plan §MEU-141 | MEU-141 handoff | ✅ |
| AC-25, AC-51, AC-68, AC-72, AC-78, AC-81, AC-110, AC-113 (cross-ref) | regression | MEU-141's packaging, test-id, audit and settings guards and pins. The MEU-141 handoff records them. No MEU-140 file touches them | plan §Guards | MEU-141 handoff; gate `py-tests`, `ui-tests`, `mcp-tests` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-140.1 to AC-140.3, AC-140.5 to AC-140.11, and the AC-6.6 and AC-6.16 pins | Row 2a, against the baseline adapter: `59 failed, 61 passed in 3.49s`, exit 1 (`s66-py-red-140.txt`). Decisive lines: `assert DownloadFailedError('download failed: no_format') is None` ×9 and `AssertionError: DownloadFailedError('download failed: no_format')` ×9 (no attempt 2 ran); `AssertionError: assert 1 == 2` ×7 (one run where two were expected); `AssertionError: {'youtube': {'player_client': ['tv', 'web_safari', 'web']}}` ×4 (attempt 1 still pinned); `assert 'extractor_args' not in {...}` ×3 | Row 3: `392 passed in 14.08s` (`s66-py-green-140.txt`); gate `py-tests` | `test_youtube_client_fallback.py:155-509`, `test_extract_options.py:112-363`, `test_api_client_fallback.py:89-296`, `test_youtube_adapter.py:346`, `:604` |
| AC-140.4, AC-140.12 | Guards that characterise behaviour that already existed. Row 2a's guard run: `20 passed, 34 deselected in 0.48s` (`s66-r2a-guard.txt`) | Row 3 and gate `py-tests` | `test_youtube_client_fallback.py:422`, `:527`, `:542` |

- **red-check.** Row 2a's check (`s66-red-140-check.txt`) reads `red-check: 1 receipt(s), 12 required test(s), 0 problem(s)`. Every failing block failed by assertion alone.
- **The passes in the Red run** are AC-140.4 and AC-140.12, the other adapter tests in `test_youtube_adapter.py`, and the AC-140.9 cases that row 1's port signature already met.

### Live probes (D-642 A, D-663; task row H1-2m)

Mat approved every probe ("all probes approved"). `s66/live-probe.py` builds the real `YouTubeAdapter`:

- with the pinned FFmpeg;
- with the runtime that `JsRuntimeLocator` finds (the pinned `packaging/deno-win64/deno.exe` as the bundle).

It downloads at 360p into the session subfolder `s66/probe/` and appends one JSON line per probe to `s66-probes.txt`. It prints and stores no cookie value, no cookie file path and no browser profile.

- **Cookies.** The app's `cookie_mode` was none, so Mat named Firefox ("I have singed into youtube in firefox, so the cookie should be from the firefox browser"), D-663. The cookies-on probes use Firefox's default profile, and the receipt stores only the mode `browser`.
- **What is stored.** The video id is stored only for public cookies-off probes. The two members-only videos' URLs and ids are stored nowhere, and the `--private` flag keeps them out of the receipt.

The H1-2m check reads the receipt and exits 0 (`s66-h12m-row.txt`). The receipt holds six lines. Each one reads `runtime_source` `bundled`, `runtime_version` `2.9.8` and `solver` true.

| Probe | Cookies | Outcome | Attempt passed | File size (bytes) | Height | sabr_detected | Events |
|---|---|---|---|---|---|---|---|
| public-1 (`gKcOjnDJfzk`) | none | passed | 1 | 214,953,128 | 262 | False | `youtube.download` attempt 1 |
| public-2 (`jNQXAC9IVRw`) | none | passed | 1 | 474,462 | 240 | False | `youtube.download` attempt 1 |
| logged-in (`gKcOjnDJfzk`) | browser | passed | 1 | 214,953,128 | 262 | False | `youtube.download` attempt 1 |
| members (a channel the account doesn't belong to) | browser | failed, `final_cause` `other` | — | — | — | — | none |
| members2-in (a channel the account belongs to) | browser | passed | 1 | 1,113,831,498 | 360 | False | `youtube.download` attempt 1 |
| members2-out (the same video) | none | failed, `final_cause` `other` | — | — | — | — | none |

- **The contract, live.** In each passing probe, attempt 1 passed with yt-dlp choosing its client and no `extractor_args`. That includes the logged-in and members probes, which the cookie pin used to miss. So no probe ran attempt 2. `RETRY_ONCE` is shown by AC-140.3 and AC-140.4 only.
- **The members refusals.** Mat said that the first members video is from a channel the account doesn't belong to ("I'm not a member"). For the second, Mat said it "should work when signed in and should not work when signed out", and both probes matched that. Both refusals logged no `youtube.attempt_failed`, so `CLIENT_SIDE` treated them as not client-side and ran no retry. Each was classified `other`, because no cause names a members-only refusal (raised for Mat in §Deferred Items).

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s66-0-baseline", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-12-youtube-client-runtime/baseline.ps1 *> C:/Temp/av-kit/s66-baseline.txt (task.md row 0's Validation cell, run from P:/av-kit; base suites in C:/Temp/av-kit/s66-base-py.txt, s66-base-ui.txt, s66-base-mcp.txt, s66-base-mcp-build.txt and s66-base-ruff.txt)", "scope": "Row 0: D-640 to D-642 ruled (S14), the queue (S8), the shapes and absent names (S11), baseline.sha and baseline-dirty.txt, the anchors and line endings, the lock sync (S4), the base suites, and the red-check and identity selftests", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 0553779 before any row", "output": "D-640: chosen starts 'A:', ruled=True; D-641: chosen starts 'D:', ruled=True; D-642: chosen starts 'A:', ruled=True; queue: MEU-139 approved, MEU-140 pending, MEU-141 pending; 0553779 is an ancestor of HEAD: True; shapes wrong (S11): []; missing targets: [] new files already present: []; ui lock sync: 651 locked packages, 0 differ, 0 missing; mcp-server lock sync: 133 locked packages, 0 differ, 0 missing; base pytest 2152 passed, 37 warnings in 176.99s (0:02:56); base UI Test Files 120 passed (120), Tests 1285 passed (1285); base MCP Test Files 35 passed (35), Tests 520 passed (520); ruff All checks passed!; red-check selftest: 49 fixture(s) (15 positive, 34 negative), 0 wrong; identity selftest: 0 failure(s); baseline: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s66-1-types-140", "command": "env -u ELECTRON_RUN_AS_NODE python C:/Temp/av-kit/s66/run_row.py 1 > C:/Temp/av-kit/s66-row1-run.txt (task.md row 1's Validation cell: pytest over the port, adapter, service, extract and transcript-metadata tests *> C:/Temp/av-kit/s66-types-py.txt; pyright *> s66-types-pyright.txt; ruff *> s66-types-ruff.txt; export_openapi.py --check *> s66-types-openapi.txt; the caller grep *> s66-callers.txt; the MEU-141 pin sweep *> C:/Temp/av-kit/s66/row1-pin-sweep.txt)", "scope": "Row 1: MEU-140's shared names as stubs (the port's options keyword, ATTEMPT_CLIENTS, client_side_error, _attempt_opts, _download_options), the fakes that take options, the AC-4.7 and AC-122.6 pins, the caller grep and the MEU-141 pin sweep", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 0553779 plus rows 0 to 1", "output": "323 passed in 12.40s; pyright 0 errors, 0 warnings, 0 informations; ruff All checks passed!; export_openapi --check exit 0; callers: 193 lines; pin sweep: 92 lines; row 1 exit=0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s66-2a-red-140", "command": "rtk proxy uv run pytest tests/integration/test_youtube_client_fallback.py tests/unit/test_extract_options.py tests/e2e/test_api_client_fallback.py tests/integration/test_youtube_adapter.py --tb=short -q *> C:/Temp/av-kit/s66-py-red-140.txt; red-check.py with the 12 --require ids *> C:/Temp/av-kit/s66-red-140-check.txt; pytest -k 'test_ac_140_4_ or test_ac_140_12_' *> C:/Temp/av-kit/s66-r2a-guard.txt (task.md row 2a's Validation cell)", "scope": "MEU-140 Red: AC-140.1 to .3 and .5 to .11 against the baseline adapter, the AC-6.6 and AC-6.16 pins, and AC-140.4 and AC-140.12 as passing guards", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 0553779 plus rows 0 to 2a", "output": "59 failed, 61 passed in 3.49s (child exit 1). Decisive: assert DownloadFailedError('download failed: no_format') is None x9; AssertionError: DownloadFailedError('download failed: no_format') x9; AssertionError: assert 1 == 2 x7; AssertionError: {'youtube': {'player_client': ['tv', 'web_safari', 'web']}} x4; assert 'extractor_args' not in attempt 1's opts x3. red-check: 1 receipt(s), 12 required test(s), 0 problem(s). Guard: 20 passed, 34 deselected in 0.48s"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s66-3-green-140", "command": "rtk proxy uv run pytest (row 3's files: the MEU-140 tests, test_youtube_adapter.py, test_youtube_adapter_visibility.py, test_download_failure_visibility.py, test_api_download_visibility.py, test_services.py, test_transcript_flat_extract.py, test_transcript_metadata.py, test_download_received_quality.py, test_api_downloads.py, test_api_error_surface.py) --tb=short -q *> C:/Temp/av-kit/s66-py-green-140.txt; pyright *> C:/Temp/av-kit/s66-r3-pyright.txt; ruff check *> C:/Temp/av-kit/s66-r3-ruff.txt (task.md row 3's Validation cell); the full suite after row 3 *> C:/Temp/av-kit/s66/r3-full.txt", "scope": "MEU-140 Green: CLIENT_SIDE, ATTEMPT_OPTS, RETRY_ONCE, ATTEMPT_LOG, SABR_ACROSS, CATCH_ALL, ADD_OPTS, ADD_CACHE_KEY, and the plan's guards", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 0553779 plus rows 0 to 3", "output": "392 passed in 14.08s; pyright 0 errors, 0 warnings, 0 informations; ruff All checks passed!; full suite 2235 passed, 37 warnings in 170.82s (0:02:50)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s66-3s-split", "command": "env -u ELECTRON_RUN_AS_NODE python C:/Temp/av-kit/s66/run_row.py 3s (task.md row 3s's Validation cell: active-set.py check and lint_task_contract.py *> C:/Temp/av-kit/s66-r3s-lint.txt)", "scope": "Row 3s: the split point under D-641 D, the context state, and active-meus.txt", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 0553779 plus rows 0 to 3s", "output": "active-meus.txt: MEU-140 MEU-141; OK: 28 row(s); 10-column table (with builder_model); 26 row(s) fully checked: backticked, exit-code re-raised, receipt under RECEIPTS_DIR; dependencies resolve and are acyclic; 2 row(s) exempt (view_file): H1-5, H2-1"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s66-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-12-youtube-client-runtime/session-gate.ps1 *> C:/Temp/av-kit/s66-gate-h1.txt; then Select-String for ' exit=', 'not_run', 'skipped', 'tested_state', 'outside scope', 'mismatch', 'session-gate:' and exit $code (task.md row H1-2's Validation cell, run from P:/av-kit, row receipt C:/Temp/av-kit/s66-h12-row.txt; per-step receipts C:/Temp/av-kit/s66-D6-*.txt)", "scope": "H1-2: the registered full gate. Static: py-types, py-lint, ui-types, ui-lint, task-contract, scope-paths, red-check-selftest, active-set. Full: py-tests, openapi, ui-tests, ui-build, mcp-types, mcp-build, mcp-tests, state-render, issues-render. Runtime: ui-electron, package-build, deno-copy, runtime-smoke, licences. Identity before and after. Skipped with reasons: mcp-audit, build-record, live-probes, real-ffmpeg", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "055377999828ea759315fcdd8d6c7b488110b67c+4fd745a936fbc9857749819533559d04f37a8de662c832365be61a1232e08c30", "output": "py-types 0 errors, 0 warnings, 0 informations; py-lint All checks passed!; ui-types exit 0; ui-lint exit 0; task-contract OK: 28 row(s), 26 fully checked, 2 exempt (view_file): H1-5, H2-1; scope-paths changed paths: 72 outside scope: [] head moved (S3): False; red-check selftest: 49 fixture(s) (15 positive, 34 negative), 0 wrong; active-set exit 0; py-tests 2309 passed, 37 warnings in 186.14s (0:03:06); openapi exit 0; ui-tests Test Files 121 passed (121), Tests 1293 passed (1293); ui-build exit 0; mcp-types exit 0; mcp-build exit 0; mcp-tests Test Files 36 passed (36), Tests 525 passed (525); state-render Drift check passed (142 MEUs, 12 phases); issues-render OK: known-issues.md is up-to-date; ui-electron 24 passed (38.2s); package-build exit 0; deno-copy: ['LICENSE.md', 'deno.exe']; runtime-smoke PASS: smoke-runtime source=bundled version=2.9.8 solver=True; licences THIRD_PARTY_LICENSES.txt: 1103368 bytes; tested_state before = after; session-gate: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s66-h1-2m-probes", "command": "uv run --no-sync python C:/Temp/av-kit/s66/live-probe.py --label L --url U --cookies off|browser [--browser firefox] [--private], once per probe on Mat's words; then task.md row H1-2m's Validation cell *> C:/Temp/av-kit/s66-probes-check.txt (row receipt C:/Temp/av-kit/s66-h12m-row.txt; probe records C:/Temp/av-kit/s66-probes.txt)", "scope": "H1-2m, D-642 A and D-663: two public videos with cookies off, a logged-in probe and three members-only probes with Firefox's cookies or none, through the real adapter at 360p", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "055377999828ea759315fcdd8d6c7b488110b67c+4fd745a936fbc9857749819533559d04f37a8de662c832365be61a1232e08c30", "output": "6 probe lines, each runtime_source bundled, runtime_version 2.9.8, solver true. public-1 none passed attempt 1, 214953128 bytes, height 262, sabr False; public-2 none passed attempt 1, 474462 bytes, height 240, sabr False; logged-in browser passed attempt 1, 214953128 bytes, height 262, sabr False; members browser (not a member) failed, final_cause other, no youtube events; members2-in browser passed attempt 1, 1113831498 bytes, height 360, sabr False; members2-out none failed, final_cause other, no youtube events. row H1-2m exit=0"}
```

### Quality Gate Results

`s66-gate-h1-2` (H1-2) is the fresh full record. Its last line is:

> session-gate: all steps exit 0

- **One run.** The gate passed every step on its first run (`s66-gate-h1.txt`, row receipt `s66-h12-row.txt`).
  - Before it, Session 60 RULE-4's listing found `tests/e2e/api_fakes.py` changed but outside the gate's allowed set. It is D-658's third fixture repair, so D-662 added it to `$scopePaths` with a comment naming D-658.
- **Static checks.**
  - pyright: 0 errors, 0 warnings, 0 informations. ruff check: all checks passed. The UI typecheck and eslint exited 0.
  - lint_task_contract passed on 28 rows: 26 fully checked, with H1-5 and H2-1 exempt as `view_file`.
  - scope-paths found 72 changed paths, none outside scope. HEAD `0553779` did not move (S3).
  - The red-check selftest read 49 fixtures (15 positive, 34 negative), with 0 wrong. `active-set.py check` exited 0.
- **Suites.**
  - pytest: 2309 passed, the baseline's 2152 plus 157 new cases.
  - UI: 1293 passed in 121 files, the baseline's 1285 in 120 plus `settings-runtime.test.ts`'s 8.
  - MCP: 525 passed in 36 files, the baseline's 520 in 35 plus 5: three in `settings-runtime.test.ts` and two AC-141.16 tests.
  - Electron E2E: 24 passed (`s66-D6-ui-electron.txt`).
- **Build, package and state.**
  - `export_openapi.py --check`, the UI build, the MCP typecheck and the MCP build exited 0.
  - The package build exited 0. The Deno copy placed `deno.exe` and `LICENSE.md`.
  - The packaged smoke read `PASS: smoke-runtime source=bundled version=2.9.8 solver=True`, and the licence generator wrote `THIRD_PARTY_LICENSES.txt: 1103368 bytes`.
  - The state render and the issue render match the files on disk.
- **After the gate.**
  - H1-3 (`s66-h13-row.txt`) read `active-set records: MEU-140 MEU-141; 0 problem(s): []`, and its render check passed.
  - H1-4 (`s66-h14-row.txt`) read `schemas added or removed: ['JsRuntimeOut']` and `active-set openapi: MEU-140 MEU-141; 0 problem(s): []`. MEU-140 changes no route or schema.
- **Skipped.** Each skip has a reason in the gate:
  - `mcp-audit`: it needs the live network and YouTube, which the brief forbids;
  - `build-record`: no release (row 5 built the NSIS installer, D-650);
  - `live-probes`: a recorded manual check after the gate (H1-2m, above);
  - `real-ffmpeg`: no FFmpeg change, and `py-tests` still runs the module.
- **Identity.**
  - The tested_state was the same before and after: `055377999828ea759315fcdd8d6c7b488110b67c+4fd745a936fbc9857749819533559d04f37a8de662c832365be61a1232e08c30`.
  - The identity leaves out this plan's `*.md` files, this session's handoffs and reflection, `docs/execution/metrics.md` and `current-focus.md`, so writing them doesn't change it.
- **Warnings.** The gate's `py-tests` has 37 warnings, the same as the baseline. None is from this session's code.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `packages/infrastructure/src/avkit_infra/youtube/adapter.py` | modified | `NO_RETRY_NEEDLES`, `RETRY_NEEDLES`, `ATTEMPT_CLIENTS`, `client_side_error`, `_attempt_opts`, `_attempt_sequence`, `_download_failure`, `CATCH_ALL` in `_quality_selector`, `extract_info` with options, `youtube.download`'s `attempt` (and MEU-141's `js_runtime` and `JS_RUNTIME_OPTS`) |
| `packages/core/src/avkit_core/ports/youtube.py` | modified | `extract_info(..., options: DownloadOptions \| None = None)` |
| `packages/core/src/avkit_core/services/download.py` | modified | `_download_options`, read fresh by `_options_from` and `add_to_queue` (`ADD_OPTS`) |
| `packages/core/src/avkit_core/services/extract.py` | modified | `ADD_CACHE_KEY` and the forwarded `options=` |
| `tests/integration/test_youtube_client_fallback.py` | new | AC-140.1 to .5, .8, .12. LF, 554 lines |
| `tests/unit/test_extract_options.py` | new | AC-140.9, AC-140.10. LF, 369 lines |
| `tests/e2e/test_api_client_fallback.py` | new | AC-140.6, .7, .11. LF, 308 lines |
| `tests/integration/test_youtube_adapter.py` | modified | The AC-6.6 and AC-6.16 pins |
| `tests/unit/test_domain.py`, `tests/unit/test_transcript_metadata.py` | modified | The AC-4.7 and AC-122.6 pins |
| `tests/unit/test_services.py`, `tests/e2e/real_stack.py`, `tests/e2e/test_api_error_surface.py`, `tests/integration/test_download_received_quality.py` | modified | The add-path fakes take `options` (row 1) |
| `docs/build-plan/02-infrastructure.md` | modified | The client fallback line names `ATTEMPT_OPTS` and `RETRY_ONCE`, and a `Delivered (Session 66)` note (row 6) |
| `.agent/context/meu-status.yaml`, `meu-registry.md`, `docs/BUILD_PLAN.md`, `known-issues.yaml`, `known-issues.md`, `triage-output.yaml`, the grouping file | modified | Only MEU-140 and MEU-141's fields and rows, the two issues, and grouping row 66 (row 6, D-661) |
| `.agent/context/current-focus.md` | modified | Session 66's priority paragraph (H1-3) |

The MEU-141 handoff lists its own files: the runtime, Health, settings, packaging and UI files, and its tests.

`git diff --stat 0553779` on the tracked files reads `47 files changed, 692 insertions(+), 148 deletions(-)`. The 16 untracked paths are this plan's folder, the three handoffs (this one, MEU-141's and the plan review) and the twelve new code and test files.

Line endings were measured with Python bytes before each edit and kept:

- **CRLF.** `adapter.py`, `services/download.py`, `test_youtube_adapter.py`, `test_domain.py`, `test_services.py`, `real_stack.py`, `test_api_error_surface.py`, 02 and `current-focus.md`.
- **LF.** `ports/youtube.py`, `services/extract.py`, `test_transcript_metadata.py`, `test_download_received_quality.py`, `meu-status.yaml`, `meu-registry.md`, `BUILD_PLAN.md`, the issue files and the grouping file.
- **New files** are LF.

```diff
 # adapter.py, _attempt_sequence (abridged)
+            extra = self._attempt_opts(options, attempt)
+            ...
+            except DownloadError as exc:
+                sabr_seen = sabr_seen or logger.sabr_detected
+                text = str(exc)
+                if attempt == 2 or not client_side_error(text, logger.sabr_detected):
+                    raise fail(exc, logger) from exc
+                if stoppable and self._should_stop is not None and self._should_stop():
+                    raise DownloadCancelledError("download cancelled") from exc
+                cause, detail = classify_download_error(text, logger.sabr_detected)
+                log.warning("youtube.attempt_failed", attempt=attempt,
+                            clients=ATTEMPT_CLIENTS[attempt], cause=cause, detail=scrub_line(detail))
+                attempt = 2
+                continue
+            return value, attempt, sabr_seen or logger.sabr_detected
 # adapter.py, _quality_selector
-    return f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"
+    return f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"
```

The excerpt is abridged. The source is `adapter.py:621-670` and `:160`.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

Codex reviews the execution in one rolling report, `2026-11-12-youtube-client-runtime-implementation-critical-review.md`, on the ledger loop `s66-execution-2026-11-12-youtube-client-runtime`. The table is filled in as the rounds return.

| Round | Verdict | Findings | Tested state |
|-------|---------|----------|--------------|
| 1 | approved | 0 findings; intent achieved: yes; IR-1 to IR-7 pass | `055377999828ea759315fcdd8d6c7b488110b67c+4fd745a936fbc9857749819533559d04f37a8de662c832365be61a1232e08c30` |

### Verdict

`approved` at round 1 of 6 (dispatch `s66-exec-r1`), with no findings. The review-state check (H1-7a) and the approved-state check (H1-7b) both exit 0. MEU-140 moves to `approved` in H2-2.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| A members-only refusal is classified `other`, since no cause names it. Both live members failures had no `youtube.attempt_failed` line and `final_cause` `other` | message quality, raised for Mat | None | Out of this plan's scope. `CLIENT_SIDE` already treats it as not client-side, so it doesn't retry. A named cause would change Session 65's `FAILURE_CAUSE` contract and needs its own issue if Mat wants one |
| `RETRY_ONCE` was not seen live: attempt 1 passed in every passing probe | coverage note | None | AC-140.3 and AC-140.4 drive both attempts with a scripted `YoutubeDL`. A live retry needs a video that fails on yt-dlp's own client choice and passes on the cookie pin |
| The MP3 convert | bug | MEU-142 (Session 67) | Its own grouping session |
| Commit and push | out-of-scope | — | Only on Mat's words, after Codex approves (H2-5) |

### Departures and their basis

1. **Test names (row 2a).** Six MEU-140 test functions were shortened so that red-check reads every failure header (§Row 2a's Red tests). The AC ids, assertions and fixtures are unchanged.
2. **D-655.** `ATTEMPT_LOG`'s `detail` is `scrub_line` of `classify_download_error`'s first line, and the Console row shows only the event and `detail`. AC-140.6 checks `attempt`, `clients` and `cause` through `capture_logs`.
3. **D-656.** The add-time extract's attempt sequence doesn't check `should_stop`, because an add has no job to stop.
4. **D-657.** A failed attempt 2 is classified with attempt 2's own logger. `SABR_ACROSS` sets only `DownloadResult.sabr_detected`.
5. **D-662.** `tests/e2e/api_fakes.py`, D-658's third fixture repair, was added to the gate's allowed set before H1-2.
6. **D-663.** The cookies-on probes used Firefox's cookies, because the app's cookie mode was none.
7. **A sixth probe pair.** On 2026-11-12, after the four planned probes, Mat sent a second members-only video with the expected results. Both probes ran under "all probes approved", with `--private` so that neither stores the video's URL or id.

The departures recorded for MEU-141 (D-658 to D-661) are in its handoff.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-12 | claude-code-local (Claude Opus 5.5) | Row 1's caller grep and MEU-141 pin sweep |
| Updated | 2026-11-12 | claude-code-local (Claude Opus 5.5) | Row 2a's Red tests and receipts |
| Updated | 2026-11-12 | claude-code-local (Claude Opus 5.5) | Row 3's Green changes and receipts |
| Updated | 2026-11-12 | claude-code-local (Claude Opus 5.5) | Row 3s: no split, active set MEU-140 MEU-141 |
| Completed | 2026-11-12 | claude-code-local (Claude Opus 5.5) | The AC table, where values go, the live probes, the evidence records and the H1-2 gate (H1-6) |
