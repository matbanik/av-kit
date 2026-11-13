---
project: "2026-11-12-download-audio-extract"
date: "2026-11-12"
source: ".agent/context/grouping/2026-11-10-download-reliability-session-grouping.md#session-67--download-audio-extract-meu-142--p2"
grouping_source: ".agent/context/grouping/2026-11-10-download-reliability-session-grouping.md"
meus: ["MEU-142"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: Download audio extract (Session 67)

> **Project:** `2026-11-12-download-audio-extract`
> **Build plan:** `docs/build-plan/03-service-layer.md` §Download audio extract (residual) (`:722-733`, anchor `download-audio-extract-residual`, MEU-142), with the §Construction `MediaPort` row (`:56`) and 02 §Media adapter's `convert` row (`docs/build-plan/02-infrastructure.md:432`).
>
> **Source request.** On 2026-11-10 Mat asked for the download comparison report's findings to be filed and grouped ("follow the process, file them and add to session grouping"; triage D-534, grouping D-535). This is the grouping's third and last session (Sessions 65 to 67, MEU-137 to MEU-142). Grouping D-542 set the path: `MediaPort.convert` after the download, not yt-dlp's postprocessor. Done comes from the residual section: each rule holds with a behaviour test, and the issue closes with that evidence.
> **Known issue:** this session closes `DOWNLOAD-MP3-NOT-CONVERTED` (`known-issues.yaml:4889`, D-534). The comparison report `docs/proposals/2026-11-10-download-logic-divergence-report.md` is never opened; the plan needs no fact that only it holds.
> **Status:** `draft`. `plan_to_exec_gate: human`. The plan review approved at round 2 (`.agent/context/handoffs/2026-11-12-download-audio-extract-plan-critical-review.md`). At the plan gate Mat ruled D-671 B (USER_EXPLICIT 2026-11-12 'B: one live public download'), set the execution review budget to 30M (USER_EXPLICIT 2026-11-12 '30M') and said to execute (USER_EXPLICIT 2026-11-12 'Yes, execute now').

## Goal

**Goal anchor:** Session 67 makes an MP3 audio download give an MP3. `DownloadService` takes the app's `MediaPort` and, after a good download of an audio-only `StandardMp3` job, converts the file to MP3 with `MediaPort.convert`, stores the MP3 as the job's file and removes the source, in every cookie mode and with no `ConversionJob` row. Without ffmpeg the job fails with the `FFmpegNotFoundError` message on its card through Session 65's failure path, and the downloaded file stays.

Four things are missing today (`3435b7e`):

1. **The service has no media port.** `DownloadService.__init__` (`packages/core/src/avkit_core/services/download.py:166-192`) takes `youtube`, `coordinator` and `settings` only, and `build_services` (`packages/api/src/avkit_api/wiring.py:175-180`) passes no `media`, although the same `FFmpegAdapter` (`:159`) is already given to TTS, Health, Conversion and Capture.
2. **There is no convert step.** `_run_one` (`download.py:629`) saves the downloaded file as the job's file on success (`:695-718`). `StandardMp3` selects plain `bestaudio` (`packages/infrastructure/src/avkit_infra/youtube/adapter.py:752`, the audio branch), so the job's file is an `.m4a` or `.webm`.
3. **Cookie mode ignores the audio format.** With cookies the adapter selects `COOKIE_AUDIO_SELECTOR` for every audio format (register `:4889`), so the format's only remaining effect has to come after the download.
4. **The 03 Construction row says "optional".** `03-service-layer.md:56` calls the download convert optional, and 02's `convert` row (`:432`) says download audio extract uses `ConvertOptions` from the chosen `AudioFormat`; no code does.

The session ends when the residual section holds with a behaviour test per rule, `DOWNLOAD-MP3-NOT-CONVERTED` is closed with that evidence, the session gate's last line is `session-gate: all steps exit 0`, and MEU-142 is `approved` after Codex approves.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (2026-11-12). No payload is oversized: services/download.py, the media adapter, wiring.py and the eight construction sites were read by section."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`plan_to_exec_gate: human`, `.agent/context/harness.local.md` Claude Code block). Validation goes through `rtk proxy`:
  - receipts go under `C:/Temp/av-kit`, named `s67-*`;
  - `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`;
  - `TMP` and `TEMP` point at `C:\Temp\av-kit\s67\tmp` for the Python suite, because `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` is still open;
  - `ELECTRON_RUN_AS_NODE` is cleared before every UI and Electron run (the scripts clear it too).
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub` and any other worktree are left alone.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `s67-plan-canonical-2026-11-12-download-audio-extract` and `s67-execution-2026-11-12-download-audio-extract`.
  - Claude wrote the plan, so the reviewer is a different vendor. Caps: plan 3 rounds, execution 6. If Codex is unavailable or the ledger refuses a round, the fallback is Mat.
  - Each round is metered, and the coordinator tells Mat before dispatching.
  - Each rolling report is validated under `C:/Temp/av-kit` and then copied byte for byte to its canonical path, and the `--review-state-only` receipt is rebuilt there.
  - Reviewer prompts name the ledger vocabulary up front: D-664 to D-671, AC-142.1 to AC-142.19, and the mechanism ids in §Single-statement contracts. They forbid opening `P:/av-kit/.mcp.json`, any `mcp-token.txt`, `~/.claude.json`, any `.env`, `.claude/settings.local.json`, anything under `.agent/fleet/hub` and `docs/proposals/2026-11-10-download-logic-divergence-report.md`, and write `<HOME>` for the home folder. When they ask for `tested_state`, they name `~/.config/git/ignore` and the path it hides, `.claude/settings.local.json` (Session 51 RULE-4). `## Findings` holds only the Findings table; probe tables go under another heading (Session 65 RULE-3). Every prompt carries the literal `### New Findings` header and the Prior Pass Summary table with the columns Finding, Prior Status and Recheck Result (Session 66 RULE-4); a recheck names each prior finding by the review's own id (Session 53 RULE-3) and asks for bare words in its Recheck cells (`fixed`, `open`; Session 52 RULE-1, Session 57 RULE-5).
- **Never in these rows without Mat's words:** commit, push, a tag, release or upload, the live MCP audit, `--update-baseline`, or an `approved` verdict authored by the implementer. A network request runs only as D-671 is ruled: no test and no suite row reaches YouTube or the network, and the convert tests use a fake `MediaPort` or the pinned local FFmpeg on a generated clip. Nothing touches the installed avkit MCP servers (no `mcp__avkit__*` tool is called), and no other program is stopped.

## Handoff Set

| MEU | Handoff | Chain |
|---|---|---|
| MEU-142 | `.agent/context/handoffs/2026-11-12-download-audio-extract-MEU-142-handoff.md` | only |

Rolling reviews: `.agent/context/handoffs/2026-11-12-download-audio-extract-plan-critical-review.md` and `.agent/context/handoffs/2026-11-12-download-audio-extract-implementation-critical-review.md`.

## Work Packages and Context Lifecycle

| WP | Rows | Content | Context |
|---|---|---|---|
| WP-1 | 0 | Baseline: ruling, queue, shapes, dirty paths, anchors, base suites, the FFmpeg pair, selftests | shared |
| WP-2 | 1 | Type-only names: the `media` keyword, the wiring, the eight construction sites, an empty `AUDIO_EXTRACT` and a `last_line` stub | shared |
| WP-3 | 2, 3 | Red, then Green | shared |
| WP-4 | 4, 5 | The CI deselect, and the 03 spec text | shared |
| WP-5 | 6 | Register, status, grouping | shared |
| WP-6 | H1, H2 | Gate, handoff, review, reflection, next prompt | compact_continue |

## User Review Required

**Carried rulings:** none open from the grouping for this session. D-535 is Mat's (2026-11-10); D-537 and D-542 are autonomous grouping decisions, and this plan follows D-542's path.

**Open for Mat at the plan gate.** The brief is in §Decision Log in full; the short form:

1. **D-671 — network** `[outward-facing]`. *Recommendation A:* no network in the session. The suites stay offline, and a live MP3 download in the app stays a named open manual check in the handoff and the register's verification. *B:* after the gate, one live `StandardMp3` download of a public video with cookies off, on Mat's words, as a recorded manual check. *Do nothing (D):* the session runs offline and no manual check is recorded; the issue closes on the test evidence alone.

**The gate.** Execution waits for Mat's explicit message. At the gate Mat sets the execution review budget (Session 60 RULE-5: the round 1 estimate twice plus one recheck).

**Token estimate.** Calibrated against Session 54 (plan round 1 8.5M; execution round 1 7,859,970 of a 21M budget, a `MediaPort` service change with real-ffmpeg tests), Session 65 (plan 24.6M over 4 rounds; execution 16.6M over 2) and Session 66 (plan 24.85M over 5 rounds; execution round 1 10.8M of 37.5M). This session is one MEU, with a narrower delta than Session 54's:

- plan review: about 9M for round 1 and about 5M for one recheck, so about 14M over 2 rounds;
- execution review: about 9M for round 1, so the loop opens at 22.5M (9M × 2 plus one recheck at about 4.5M, Session 58 RULE-4), unless Mat sets another figure. Mat set 30M at the gate (USER_EXPLICIT 2026-11-12 '30M').

**Word meanings.** *The source* is the file `YouTubePort.download` returns (`DownloadResult.file_path`). *The MP3* is the file `MP3_RESERVE` reserves and `MediaPort.convert` writes. *A good convert* is a `convert` call that returns without raising, followed by a successful `stat` of the MP3.

## Proposed Changes

### Single-statement contracts

Each mechanism id below is one statement. A row cites the id; a test names the AC.

| Id | Statement | File |
|---|---|---|
| `MEDIA_PORT` | `DownloadService.__init__` takes `media: MediaPort` as a required keyword-only parameter right after `youtube`, stored as `self._media`; `build_services` passes the one `media` it already builds, so `download._media is conversion._media is tts._media is health._media` (D-664). | `services/download.py`, `api/wiring.py` |
| `AUDIO_EXTRACT` | A module constant `AUDIO_EXTRACT: dict[AudioFormat, tuple[str, ConvertOptions]]` equals `{AudioFormat.StandardMp3: (".mp3", ConvertOptions(codec="libmp3lame", bitrate_kbps=192, sample_rate=None, channels=None))}` (D-665). | `services/download.py` |
| `EXTRACT_TRIGGER` | `_run_one` converts exactly when the job is `audio_only`, its `audio_format` is a key of `AUDIO_EXTRACT`, and the source's suffix, case-folded, is not that key's suffix; the cookie mode plays no part (D-665). | `services/download.py` |
| `MP3_RESERVE` | The MP3 path is the source's folder, the source's stem and the map's suffix; it is reserved by `open(path, "xb")`, and on `FileExistsError` the stem gains `-2`, `-3` and so on until one is free, so an existing file is never opened, truncated or overwritten (D-666). | `services/download.py` |
| `CONVERT_DONE` | On a good convert, `_run_one` stats the MP3, commits Done with `file_path` the MP3 and `file_size` its size (progress 1.0, `received_height` None, the archive entry added) in one unit of work, logs `download.done`, and only then unlinks the source (D-667). | `services/download.py` |
| `ROW_GONE` | If the job row is gone when the Done commit reads it (removed or cleared during the convert), no commit happens and neither file is removed (D-667). | `services/download.py` |
| `KEPT_LOGS` | A failed unlink of the source after Done logs one `download.source_kept` warning, and a failed removal of a reserved MP3 after a failed convert logs one `download.partial_kept` warning; each carries `job_id`, `video_id` and `error` set to the exception's type name, never a path; the job's status is not changed by either (D-667, D-668). | `services/download.py` |
| `CONVERT_FAIL` | A convert that raises fails the job through `_finish(Failed)` with `download_failure_message(cause, reason)`: `FFmpegNotFoundError` gives cause `other` with `reason = safe_reason(scrub_line(str(exc)))`, so the card reads `Download failed: ffmpeg binary was not found.`; `OSError` gives cause `write_failed`; any other exception gives cause `other` with the fixed reason `MP3 convert failed`. No new cause is added; the archive entry is not added (D-668). | `services/download.py` |
| `SOURCE_KEPT` | After a failed convert the source stays byte for byte, and only the MP3 this job reserved is removed (D-668). | `services/download.py` |
| `FAIL_DETAIL` | A failed convert logs one `download.failed` error with `error` the stored card text and `detail = _convert_detail(str(exc), (source, mp3))`, a private helper. It first masks every form of each path: the full path, matched with any run of `\` or `/` between its parts (so forward slashes, mixed separators and the doubled backslashes of `str(OSError)` all match) and in any case when `health.HOME_IGNORES_CASE` is set, becomes `[file]`; then each parent folder in the same forms becomes `[folder]`; then each file name becomes `[file]`. It then takes `tail = scrub_line(last_line(masked))` and returns `tail` only when `scrub_line(masked)`, the whole text scrubbed as one line, ends with `tail`; otherwise it returns `[REDACTED]`. The detail is therefore always a suffix of the whole-text scrub or the fixed `[REDACTED]`, so a needle, a split needle or a split home folder on an earlier line can never leave a secret or part of the home folder in it. A tail that holds a tab or another in-line split after an earlier link can fall back to `[REDACTED]`; that loses only the Console detail. Session 65's helpers are unchanged (D-668; `C:/Temp/av-kit/s67/fmt-probe.txt`). | `services/download.py` |
| `LAST_LINE` | `last_line(text)` splits only on CR LF, CR and LF (`_LINE_BREAKS`) and returns the last part that `scrub_line` leaves non-empty, else `""`; it never raises, so a lone surrogate, control characters or empty text give a clean or empty value (D-668). | `services/download.py` |
| `CONVERT_CANCEL` | A cancel requested during the download still ends Cancelled with no convert; the convert itself has no stop hook, so a cancel requested during it lets the job finish Done and the worker stops at its next loop. The status stays `Downloading` while the convert runs (D-669). | `services/download.py` |
| `NO_CONVERSION_ROW` | The convert writes no `ConversionJob` row and calls nothing in `ConversionService` (D-669). | `services/download.py` |
| `CI_DESELECT` | `.github/workflows/ci.yml`'s Tests step deselects `tests/integration/test_download_audio_extract_real_ffmpeg.py` once, after the existing real-FFmpeg deselects (D-670). | `.github/workflows/ci.yml` |

### Pins that move

| Row | Test | Today | After |
|---|---|---|---|
| 1 | `DownloadService(` constructions: `tests/e2e/real_stack.py:97`, `tests/e2e/test_api_error_surface.py:202`, `tests/integration/test_download_received_quality.py:150`, `tests/unit/test_download_failure_visibility.py:273`, `tests/unit/test_extract_options.py:91`, `tests/unit/test_services.py:743`, `:971` and `:1514` | no `media` | `media=` a fake whose `convert` raises `AssertionError` (`FakeMedia`, `tests/unit/test_services.py:315`, or `real_stack.py`'s `StubMedia` at `:71`, which gains that `convert`); none of these runs a `StandardMp3` audio job (`C:/Temp/av-kit/s67-plan-matrix-probe.txt`), so none reaches it |

No test pins `DownloadService`'s signature (`C:/Temp/av-kit/s67/sig-sweep.txt`). Two source pins read `services/download.py` and must keep passing: `tests/unit/test_conversion_service.py:459` and `:461` (no `ConversionService`, no `conversion_jobs` in the file); the new code names neither. Row 1 greps every caller of `DownloadService(` and `_run_one` and every pin that reads `download.py` by name, order or neighbour (Session 55 RULE-1, Session 59 RULE-1, Session 62 RULE-4, Session 63 RULE-1), and records them in `s67-anchors.txt`. A pin found there is added to this table in the handoff as a departure.

### Where values go (Session 50 RULE-1, Session 53 RULE-1, Session 61 RULE-1)

| Value | Writers | Readers | Rule |
|---|---|---|---|
| The convert's error text | `FFmpegAdapter.convert` (`FilesystemError(stderr)`, `adapter.py:449`; the first line is FFmpeg's banner and the last holds the error, `C:/Temp/av-kit/s67/convert-probe.txt`), `FFmpegNotFoundError`, `OSError` | `FAIL_DETAIL`'s `detail` | `_convert_detail` (`FAIL_DETAIL`): every path form masked as `[file]` or `[folder]`, then the scrubbed last line only when it is a suffix of the whole text's scrub, else `[REDACTED]`; never stored on the row. AC-142.13 drives secret tails after LF, CR and CR LF, a needle split across a line, a home folder split across a line, and slash, mixed, escaped, folder-only and upper-case paths through the real service to the real `HealthService` Console row, stdout and the persisted `console.log` (Session 65 RULE-1); AC-142.12 covers lone-surrogate, control-character and empty text (Session 53 RULE-1) |
| The card text | `download_failure_message` | `error_message`, the Downloader card, `download.failed`'s `error` | built from fixed text and `safe_reason` only (`CONVERT_FAIL`) |
| The source and MP3 paths | the adapter's `DownloadResult`, `MP3_RESERVE` | the job's `file_path` (the MP3 on Done, as `file_path` holds the source today) | never in a log field: `download.source_kept`, `download.partial_kept` and `download.failed` carry no path; the adapter's existing `media.convert` INFO line passes `input` and `output`, which are not in `CONSOLE_FIELDS` (`services/health.py:53-62`), so the Console shows `media.convert` alone (`s67-plan-matrix-probe.txt`) |
| An unlink or removal error | `Path.unlink` | `KEPT_LOGS`'s `error` | the type name only |

Every function between the convert's raise and the Console row is named here: `_run_one`'s convert step, `_convert_detail`, `last_line`, `scrub_line`, `safe_reason`, `download_failure_message`, `_finish`, structlog, `HealthService._process` (`console_field`, `redact_message`). AC-142.13 runs that whole chain (Session 65 RULE-1).

### Spec text (D3)

| File | Change |
|---|---|
| `docs/build-plan/03-service-layer.md` | the §Construction `MediaPort` row (`:56`) reads `DownloadService (audio extract)` in place of `DownloadService (optional audio convert)` (D-664); the residual section's `api/wiring.py:164-169` citation moves to where the wiring reads after row 1; a `Delivered (Session 67)` note under the residual section with the mechanism ids, AC-142.1 to AC-142.19 and the plan folder, and a sentence that the Convert rule applies to audio-only jobs, the only jobs whose audio format the adapter reads (`youtube/adapter.py:752`; D-665) |

### MEU-142 `svc-download-audio-extract`

**Boundary inventory.** Inputs: the job (`audio_only`, `audio_format`), the `DownloadResult` (`file_path`, `file_size`, `video_id`, `title`, `sabr_detected`), the cookie settings (read by `_options_from`, unchanged), `MediaPort.convert`'s return or exception, the filesystem's answers to `open("xb")`, `stat` and `unlink`. Outputs: the job row, the archive entry, `download.done`, `download.failed`, `download.source_kept` and `download.partial_kept` lines, the MP3 file, the source's removal. Port change: none (`MediaPort.convert`, `ports/media.py:28`, unchanged). No API route, schema, MCP or UI change; the OpenAPI snapshot does not move.

**Input matrix (Session 64 RULE-1).** Probed by reading `_run_one`, `_finish`, `_worker`, `_cancel_inflight`, the adapter's `convert` and `_run`, and by running the pinned FFmpeg on generated clips at `3435b7e` (`C:/Temp/av-kit/s67/convert-probe.txt`, `C:/Temp/av-kit/s67-plan-matrix-probe.txt`):

| Job | Source | Convert | Expected |
|---|---|---|---|
| audio-only `StandardMp3`, any cookie mode | `.m4a`, `.webm`, `.mp4` (audio and video) | passes (the probe: each gives an `mp3` stream, about 72 KiB for 3 s) | Done with the MP3, source removed |
| audio-only `StandardMp3` | `.mp3` (any case) | not called | Done with the source, as today |
| audio-only, any other format (8) | any | not called | Done with the source, as today |
| not audio-only, each of the 9 formats | any | not called | Done with the source, as today |
| audio-only `StandardMp3` | any | `FFmpegNotFoundError` (no binary; the real adapter's `_require_ffmpeg`, `adapter.py:282-288`) | Failed, card `Download failed: ffmpeg binary was not found.`, source kept, reserved MP3 removed |
| audio-only `StandardMp3` | a video-only or empty file | `FilesystemError` (the probe: `Error opening output files: Invalid argument`, `Error opening input files: Invalid data found when processing input` as the last line) | Failed, card `Download failed: MP3 convert failed.`, source kept, partial removed |
| audio-only `StandardMp3` | any | `OSError` | Failed, the `write_failed` card, source kept |
| audio-only `StandardMp3` | any | passes, then the row is removed or the queue cleared | no commit; both files stay |
| audio-only `StandardMp3` | any | passes, then the source unlink raises | Done with the MP3; `download.source_kept` |
| audio-only `StandardMp3` | any | raises, then the MP3 removal raises | Failed; `download.partial_kept` |
| any | — | cancel during the download | Cancelled, convert not called |
| audio-only `StandardMp3` | any | cancel during the convert | Done with the MP3; the worker stops at its next loop |

No existing test runs a `StandardMp3` audio job to Done, so no current test meets the new step (`s67-plan-matrix-probe.txt`: `StandardMp3` appears only in `test_youtube_adapter.py:74` and `test_domain.py:293`).

| AC | Type | Description | Source | Negative test |
|---|---|---|---|---|
| AC-142.1 | behaviour | `AUDIO_EXTRACT` equals the D-665 value exactly, and its keys over all 9 `AudioFormat` values are `StandardMp3` alone | Local Canon: 02 `convert` row (`:432`); D-665 | `HighM4a` and `StandardM4a` are not keys |
| AC-142.2 | type | `DownloadService.__init__`'s `media` is keyword-only, required (no default), right after `youtube`, annotated `MediaPort` | Local Canon: 03 §Construction (`:56`); D-664 | constructing without `media` raises `TypeError`. Row 1 adds it, so it passes where row 2 writes it |
| AC-142.3 | type | `build_services` gives `download._media`, `conversion._media`, `tts._media` and `health._media` one object, the `FFmpegAdapter` | Local Canon: D-664 | passes where row 2 writes it (row 1 adds the wiring) |
| AC-142.4 | behaviour | `EXTRACT_TRIGGER`: over 9 formats × `audio_only` True and False, `convert` is called once exactly for audio-only `StandardMp3`, with the source, the reserved `.mp3` and `AUDIO_EXTRACT`'s options; a `.mp3` or `.MP3` source is not converted | Local Canon: 03 Convert row (`:730`); 03 Tests row (`:733`, other formats do not) | the 17 other cells call nothing |
| AC-142.5 | behaviour | `MP3_RESERVE`: with `a.mp3` free the MP3 is `a.mp3`; with `a.mp3` present it is `a-2.mp3`, and with both present `a-3.mp3`; each existing file keeps its bytes | Local Canon: D-666 | an existing `a.mp3` is never passed to `convert` |
| AC-142.6 | behaviour | `CONVERT_DONE`: a recording fake traces one job end to end (Session 55 RULE-3): `download`, then `convert` (the row reads `Downloading` inside it), then the Done row with the MP3's path and size, progress 1.0 and `received_height` None, the archive entry, `download.done`, then the source gone | Local Canon: 03 Convert row; D-667 | the source still exists when the Done row is committed |
| AC-142.7 | behaviour | `NO_CONVERSION_ROW`: on the SQLite stack a `StandardMp3` job ends Done with the MP3 and `conversion_jobs` holds no row | Local Canon: 03 No row (`:731`); 08 §ConversionJob | — |
| AC-142.8 | behaviour | The convert runs the same way with cookie mode none, browser and file | Local Canon: 03 Convert row (any cookie mode); grouping D-542 | — |
| AC-142.9 | behaviour | A fake `convert` raising `FFmpegNotFoundError("ffmpeg binary was not found")` gives Failed, `error_message` `Download failed: ffmpeg binary was not found.`, one `download.failed` line with that `error`, and the source kept | Local Canon: 03 No ffmpeg (`:732`); Session 65 CARD_REASON | no `download.done` line, no archive entry |
| AC-142.10 | behaviour | `CONVERT_FAIL`: a `FilesystemError` gives `Download failed: MP3 convert failed.`; an `OSError` gives the `write_failed` card | Local Canon: D-668 | each case is its own parametrize id |
| AC-142.11 | safety | `SOURCE_KEPT`: after each failing convert (not found, `FilesystemError` with a partial MP3 written, `OSError`) the source's bytes equal their pre-run bytes, the reserved or partial MP3 is gone, and a pre-existing `a.mp3` keeps its bytes | Local Canon: 03 Tests row (a failed convert keeps the source); Session 56 RULE-3 | — |
| AC-142.12 | behaviour | `LAST_LINE`: CR LF, CR and LF split; U+2028, U+0085 and form feed do not split; trailing blank or control-only lines are skipped; a lone surrogate, control characters only and `""` give a clean value or `""` and never raise | Local Canon: D-668; Session 53 RULE-1 | U+2028 stays inside its line |
| AC-142.13 | safety | `FAIL_DETAIL`: a convert failure goes through the real service to the real `HealthService` Console row, captured stdout and the persisted `console.log`, one parametrize id per case. Leak cases: `lf_secret_tail`, `cr_secret_tail` and `crlf_secret_tail` (`Authorization: Bearer`, the break, then a synthetic secret), `needle_split_across_lf`, `home_split_lf` (the patched home folder broken by an LF so the last line holds its rest), `forward_slash_path`, `mixed_separators`, `escaped_oserror` (the text of `str(PermissionError(13, "Permission denied", str(mp3)))`), `folder_only` (the source's folder with another file name) and `upper_case_path`; each asserts no secret, no part of the home folder past `~`, no source or MP3 name and no folder path in any of the three. Keep cases: `ordinary` asserts the detail is FFmpeg's exact last error line, and `ordinary_path_tail` that it is that line with `[file]`. The stored card is the case's fixed card (`Download failed: MP3 convert failed.` for a `FilesystemError`, `write_failed`'s for the `PermissionError`) and holds none of them | Local Canon: Session 50 RULE-1, Session 65 RULE-1; `C:/Temp/av-kit/s67/fmt-probe.txt` | the two keep cases fail if the detail falls back to `[REDACTED]` |
| AC-142.14 | behaviour | `ROW_GONE`: a fake `convert` that removes the row (and, as a second case, clears the queue) leaves both the source and the MP3, and no row | Local Canon: D-667 | — |
| AC-142.15 | behaviour | `KEPT_LOGS`: a failing source unlink after Done gives Done and one `download.source_kept` warning; a failing MP3 removal after a failed convert gives Failed and one `download.partial_kept` warning; neither line holds a path | Local Canon: D-667, D-668 | no warning when the unlink succeeds |
| AC-142.16 | behaviour | `CONVERT_CANCEL`: a cancel during the download gives Cancelled with no `convert` call; a cancel set inside the fake `convert` gives Done with the MP3 and the processor Idle with no next job started | Local Canon: D-669 | the first case holds at baseline (a guard inside the required test) |
| AC-142.17 | behaviour | The pinned `packaging/ffmpeg-win64/` FFmpeg converts a generated 1 s `.m4a` through the real `FFmpegAdapter` and `DownloadService`: the job is Done with an `.mp3` that `ffprobe` reports as one `mp3` audio stream, and the source is gone | Local Canon: 03 Tests row (one real-ffmpeg integration test on a generated clip) | the module fails, never skips, when the pair is missing |
| AC-142.18 | behaviour | The real `FFmpegAdapter` with no configured path, a bundle path that does not exist and `shutil.which` patched to None gives the card `Download failed: ffmpeg binary was not found.` and keeps the source; it runs on CI | Local Canon: 03 No ffmpeg; MEU-78 resolver | — |
| AC-142.19 | check | `CI_DESELECT`: `ci-collect.py` collects the Tests step's argv from `ci.yml` and finds the new module deselected exactly once | Local Canon: 03 Tests row (deselected on CI) | exits 1 before row 4 |

**Guards.** `tests/unit/test_services.py`, `tests/unit/test_download_failure_visibility.py`, `tests/unit/test_extract_options.py`, `tests/unit/test_conversion_service.py`, `tests/integration/test_download_received_quality.py`, `tests/integration/test_api_wiring.py`, `tests/e2e/test_api_error_surface.py`, `tests/e2e/test_api_downloads.py`, `tests/e2e/test_api_conversions.py`, `tests/e2e/test_api_client_fallback.py` (the last two build `real_stack.py`) and `tests/e2e/test_api_download_visibility.py` pass after rows 1 and 3.

**Spec sufficiency.** Every 03 residual rule has an AC: Convert (AC-142.1, .4 to .6, .8), No row (AC-142.7), No ffmpeg (AC-142.9, .18), Tests (AC-142.4, .11, .17, .19). The live MP3 download is D-671's subject, not an AC.

### Files Modified

Endings from `C:/Temp/av-kit/s67/endings-baseline.txt` and `C:/Temp/av-kit/s67-plan-id-probe2.txt`; row 0 records them again with SHA-256 in `s67-anchors.txt`.

| File | Endings | Rows |
|---|---|---|
| `packages/core/src/avkit_core/services/download.py` (`MEDIA_PORT` to `NO_CONVERSION_ROW`, `last_line`) | CRLF | 1, 3 |
| `packages/api/src/avkit_api/wiring.py` (`MEDIA_PORT`) | CRLF | 1 |
| `tests/e2e/real_stack.py`, `tests/e2e/test_api_error_surface.py`, `tests/unit/test_services.py` | CRLF | 1 |
| `tests/integration/test_download_received_quality.py`, `tests/unit/test_download_failure_visibility.py`, `tests/unit/test_extract_options.py` | LF | 1 |
| `tests/integration/test_api_wiring.py` (AC-142.3) | CRLF | 2 |
| `tests/unit/test_download_audio_extract.py` (new) | LF | 2 |
| `tests/integration/test_download_audio_extract_real_ffmpeg.py` (new) | LF | 2 |
| `.github/workflows/ci.yml` (`CI_DESELECT`) | LF | 4 |
| `docs/build-plan/03-service-layer.md` | CRLF | 5 |

Each row measures a file's endings with Python bytes before it writes and writes in that ending; a scratch script that edits a tracked file fails on mixed endings (Session 63 RULE-3). No row edits a byte-hash-guarded file; `ui/tests/e2e/test-ids.ts` is refused by the gate's scope check.

### Project files

`.agent/context/known-issues.yaml` (LF), `.agent/context/known-issues.md` (LF), `.agent/context/triage-output.yaml` (LF), `.agent/context/meu-status.yaml` (LF), `.agent/context/meu-registry.md` (LF), `docs/BUILD_PLAN.md` (LF), the grouping file (LF; tracker row 67 at `:151`), the handoff, the two rolling reviews, the reflection, `docs/execution/metrics.md` (CRLF), `.agent/context/current-focus.md` (CRLF), and this folder's plan, task and scripts.

## Out of Scope

| Item | Basis |
|---|---|
| yt-dlp's `FFmpegExtractAudio` postprocessor | grouping D-542: a second FFmpeg path |
| Changing the cookie-mode audio selector (`COOKIE_AUDIO_SELECTOR`) | the convert makes the format's result independent of the selector; the selector is Session 66's area and not in the issue's Convert rule |
| Other formats converting (`HighM4a`, the WebM formats) | the downloaded container already matches them; 02 `:432` ties the convert to the chosen format, and only MP3 is a codec yt-dlp can't select |
| Converting a video job's audio | the adapter reads `audio_format` only for audio-only jobs (`youtube/adapter.py:752`) |
| A progress or status for the convert, or a stop hook inside it | D-669; the convert of an audio file takes well under a second on the probe clips |
| Changes to `FFmpegAdapter`, `MediaPort` or the TTS convert | the port already does what the service needs (`ports/media.py:28`) |
| The UI's audio format choices | `02-infrastructure.md:324` and the Downloader page are unchanged; `standard_mp3` is already offered |
| A live MP3 download | D-671 |
| Members-only URLs or ids; the `RETRY_ONCE` live probe; .NET 8.0.34 picker packs; `npm run dist`; RC1 "Transcript from another network" | Session 67 prompt, not in scope |

## BUILD_PLAN.md Audit

`uv run python tools/meu_status.py render --check` passes at baseline and after rows 6 and H2-2. MEU-142 is `pending` with dependencies MEU-8, MEU-10, MEU-78 and MEU-137, all `approved` (`C:/Temp/av-kit/s67/dep-probe.txt`).

## Verification Plan

### 1. Baseline (row 0)

`baseline.ps1`:
1. checks that D-671 is ruled in this plan's decision log (`chosen` starts `A: `, `B: ` or `D: `, with a `USER_EXPLICIT` reference), and stops if not (S9);
2. checks the queue (S8): MEU-141 `approved`, MEU-142 `pending`, `3435b7e` an ancestor of `HEAD`;
3. checks by name the shapes this plan relies on (`_run_one`, `_finish`, `scrub_line`, `first_line`, `_LINE_BREAKS`, `MediaPort.convert`, `ConvertOptions`, `download_failure_message`, `FFmpegNotFoundError`, `TTS_MP3_CONVERT`, the adapter's not-found text, the wiring's `media` and `DownloadService(` call, the last CI deselect line and the two AC-30.8 source pins), and that this plan's names and files are absent (`AUDIO_EXTRACT`, `last_line`, `MediaPort` and `ConvertOptions` in `download.py`, `_media`, `source_kept`, `partial_kept`, `FFmpegNotFoundError` in `download.py`, the new deselect, `download._media` in `test_api_wiring.py`, `media=` in the wiring's `DownloadService(` call, and the two new test files) (S7, Session 61 RULE-3);
4. creates `C:\Temp\av-kit\s67\tmp` and records `baseline.sha`, `baseline-dirty.txt` with each dirty path's SHA-256, and `s67-anchors.txt` with every target's endings and SHA-256; `docs/proposals/2026-11-10-download-logic-divergence-report.md`, if present, is hashed, never opened;
5. installs from the lock with `uv sync --frozen --offline --all-packages` and proves both `node_modules` trees match their locks;
6. checks the pinned FFmpeg pair: both files present, over 1 KiB, and `ffmpeg -version` exits 0 (S4; Session 52 RULE-2);
7. captures the base Python, UI and MCP suites and `ruff check packages/ tests/`;
8. runs the `red-check.py` and `identity.py` selftests on their own fixture copies (Session 56 RULE-4).

The shapes block alone ran at `3435b7e` with exit 0 (`C:/Temp/av-kit/s67-plan-shapes-dry-run.txt`). The rulings block exits 1 until Mat rules D-671, as S9 intends.

### 2. Type-only first, then Red, then Green

Row 1 adds the names with no behaviour (Session 53 RULE-2): the `media` keyword stored and unread, the wiring's `media=media`, the eight construction sites' fakes, `AUDIO_EXTRACT` as an empty dict with its annotation, and `last_line(text: str) -> str` returning `""`. Row 2's Red requires only new-behaviour tests (Session 66 RULE-2): AC-142.1 and AC-142.4 to AC-142.18. AC-142.2 and AC-142.3 test what row 1 adds and must pass where they are written; AC-142.19 is `ci-collect.py`'s check in row 4. Red rows pass only when `red-check.py` reads each receipt and names each failing required test as an assertion failure (Session 50); a required test that fails on a missing name is refused (the `pytest-required-ac-142-12-stub-name` fixture). Every Red test asserts a name exists before it patches or calls it (Session 52 RULE-4) and asserts length or membership before indexing (Session 62 RULE-3). Green rows change no test file.

### Plan-local scripts

`baseline.ps1`, `red-check.py`, `identity.py`, `issue-resolve.py` and `session-gate.ps1` in this folder are adapted from Session 66's with the `s67` names and this plan's paths; `ci-collect.py` is Session 54's with this plan's module. `red-check.py --selftest` runs 47 fixtures (14 positive, 33 negative; 0 wrong, `C:/Temp/av-kit/s67-plan-red-check-selftest.txt`), including the AC-142.1 boundary against AC-142.10 to AC-142.19 and the stub-name refusal. `identity.py --selftest` reports 0 failures (`C:/Temp/av-kit/s67-plan-identity-selftest.txt`).

### Session gate (H1-2)

`session-gate.ps1` runs, each step with its own receipt `s67-D6-<id>.txt` and exit code:

| Step | Command |
|---|---|
| Identity before | `identity.py` |
| Static | pyright, `ruff check packages/ tests/`, UI typecheck and lint, `lint_task_contract.py`, the scope-paths check (S3; `test-ids.ts` refused), the `red-check.py` selftest, `ci-collect.py` (AC-142.19) |
| Fresh full | the whole Python suite (TMP and TEMP at `C:\Temp\av-kit\s67\tmp`; only the Python ids the base receipt shows failing are excused), `export_openapi.py --check`, the whole UI suite and build, the MCP typecheck, build and suite, `meu_status.py render --check`, `issue_triage.py render --check` |
| Runtime | the real-FFmpeg module with `-rfEs` (AC-142.17; any `SKIPPED` fails the step), the Downloader Electron spec `ui/tests/e2e/download-queue.test.ts` |
| Identity after | `identity.py`, equal to before |
| Skipped with reason | `mcp-audit` (network and YouTube), `build-record` (no release, no package build), `live-mp3-download` (D-671's manual check, after the gate, only on Mat's words) |

## Stop Conditions

| Id | Condition | Action |
|---|---|---|
| S1 | A required Red test passes before its Green | fix the test; never weaken the Green |
| S2 | A Green row needs a test file change | stop; a moved pin goes to Mat as a departure |
| S3 | `HEAD` moves, or a path outside this plan and `baseline-dirty.txt` changes, or a `baseline-dirty.txt` path this plan doesn't write changes its SHA-256 | stop and ask Mat; never commit, stash or revert another session's work |
| S4 | `uv sync --frozen --offline`, a `node_modules` check or the FFmpeg pair check fails at baseline | stop and ask Mat |
| S5 | A test or row reaches YouTube or the network | stop |
| S6 | A raw value (convert text, a path, a secret) reaches a log, stdout or the Console | fix it in the row or ask Mat (Session 50 RULE-1) |
| S7 | A shape this plan relies on is missing, or a new name exists at baseline | stop and re-plan |
| S8 | The queue isn't as row 0 expects | stop and ask Mat |
| S9 | D-671 is not ruled | stop at row 0 |
| S10 | Codex unavailable or the ledger refuses a round | Mat reviews |
| S11 | A status file another session holds dirty | copy to `C:/Temp/av-kit/s67/pre-status/`, byte-edit only this session's fields, prove with `render --check` and a diff (Session 61 RULE-5) |
| S12 | A contract or AC in this plan needs to change | record a departure before the gate; one that changes an AC goes to Mat as a Decision Brief with a do-nothing option (Session 59 RULE-3) |

## Decision Log

> [!WARNING]
> D-671 waits for Mat at the plan gate. D-664 to D-670 are autonomous, each with its alternatives in `reasoning`. D-664 to D-673 are free (`C:/Temp/av-kit/s67/id-probe.txt` and `C:/Temp/av-kit/s67-plan-id-probe2.txt`, a `git grep` count of 0 for each).
>
> Carried and not relisted in the block: every grouping §8 row, D-535 to D-543, with stage `grouping`. The reflection carries all nine: D-535 as human (`USER_EXPLICIT 2026-11-10 'follow the process, file them and add to session grouping'`), D-539 and D-540 as human (`USER_EXPLICIT 2026-11-10 'A'`, Session 66's record), and the others, D-537 and D-542 among them, as autonomous. Triage D-534 rides in the register. The decision probe (`C:/Temp/av-kit/s67-plan-decision-probe.txt`) names this plan, the grouping and the register as sources (Session 54 RULE-5); its counts are in §Planning receipts.

```yaml
decision_log:
  - id: D-664
    stage: planning
    question: "How does DownloadService get the media port?"
    resolution: autonomous
    class: two-way
    chosen: "A required keyword-only media parameter right after youtube, stored as _media; build_services passes the one FFmpegAdapter it already builds; the 03 Construction row drops the word optional; the eight test construction sites pass a fake whose convert raises"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/03-service-layer.md:56 - MediaPort is used by DownloadService"
      - "packages/api/src/avkit_api/wiring.py:159 - one FFmpegAdapter shared by TTS, Health, Conversion and Capture"
      - "packages/core/src/avkit_core/services/tts.py - TTSService takes media as a keyword"
    research:
      engine: none
      sources: []
    reasoning: "One adapter means one ffmpeg resolver (MEU-78), so the setting, the bundled file and PATH apply to the download convert as they do to TTS. A required keyword makes a missing port a construction error rather than a silent no-convert. An optional media defaulting to None lost: it would keep the 03 word optional and let a wiring slip ship the bug again. A media factory lost: no other service takes one. Two-way."
    human_message_reference: null
  - id: D-665
    stage: planning
    question: "Which jobs convert, and with which options?"
    resolution: autonomous
    class: two-way
    chosen: "AUDIO_EXTRACT maps StandardMp3 alone to the suffix .mp3 and ConvertOptions(codec libmp3lame, bitrate_kbps 192, sample_rate None, channels None); the convert runs for audio-only jobs whose format is a key, and not when the source already has the key's suffix"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/02-infrastructure.md:432 - download audio extract uses ConvertOptions from the chosen AudioFormat"
      - "packages/core/src/avkit_core/services/tts.py:47 - TTS_MP3_CONVERT uses libmp3lame at 192 kbps"
      - "packages/infrastructure/src/avkit_infra/youtube/adapter.py:752 - the audio format is read only for audio-only jobs"
      - "C:/Temp/av-kit/s67/ffmpeg-pin-probe.txt - the pinned FFmpeg has the libmp3lame encoder"
    research:
      engine: none
      sources: []
    reasoning: "A map keyed by format gives 02's per-format options one home and makes the trigger a membership test. 192 kbps matches the app's other MP3 and keeps quality close to YouTube's audio; the sample rate and channels follow the source. Converting every audio format lost: m4a and webm already arrive in their container. Converting video jobs lost: the adapter ignores the audio format for them, and an MP3 would replace the video. A fixed 128 kbps lost to the in-app precedent. Two-way: one constant."
    human_message_reference: null
  - id: D-666
    stage: planning
    question: "Where does the MP3 go, and what if a file of that name exists?"
    resolution: autonomous
    class: two-way
    chosen: "The source's folder and stem with .mp3, reserved with open xb; on FileExistsError the stem gains -2, -3 and so on; an existing file is never opened for writing"
    source_tag: Local Canon
    precedents:
      - "packages/core/src/avkit_core/services/tts.py - _free_paths numbers -2 and -3"
      - "Session 58 RULE-1 - temps opened with xb; an existing one counts as taken"
    research:
      engine: none
      sources: []
    reasoning: "The adapter runs ffmpeg with -y, so the service must hand it a path it owns. Reserving with xb closes the race between a check and the write, and the numbering matches TTS. Overwriting an existing a.mp3 lost: it could destroy a user's file. Writing to a temp folder and moving lost: a cross-volume move adds a failure mode for nothing. Two-way."
    human_message_reference: null
  - id: D-667
    stage: planning
    question: "In what order does a good convert finish the job, and what if the row or the source can't be handled?"
    resolution: autonomous
    class: two-way
    chosen: "Convert after the SABR block, stat the MP3, commit Done with the MP3 path and size and the archive entry, log download.done, then unlink the source; a failed unlink logs download.source_kept with job_id, video_id and the error type and leaves Done; a row gone at the commit keeps both files and commits nothing"
    source_tag: Local Canon
    precedents:
      - "grouping D-542 - the source file is removed after a good convert"
      - "packages/core/src/avkit_core/services/download.py:695-718 - the Done commit returns when the row is gone"
    research:
      engine: none
      sources: []
    reasoning: "Committing before the unlink means a crash between the two leaves a Done job pointing at a real MP3 plus a stray source, never a Done job pointing at a deleted file. Keeping both files when the row is gone matches today's behaviour, where a removed job's file stays on disk (the MCP note: remove keeps files). Unlinking first lost: a failed commit would lose the only good file's record. Two-way."
    human_message_reference: null
  - id: D-668
    stage: planning
    question: "How does a failed convert reach the card and the Console, and what happens to the files?"
    resolution: autonomous
    class: two-way
    chosen: "FFmpegNotFoundError gives cause other with its scrubbed message as the reason; OSError gives write_failed; anything else gives cause other with the fixed reason MP3 convert failed; the source stays, the reserved or partial MP3 is removed (download.partial_kept on a failed removal); download.failed carries the stored text and a detail from _convert_detail: every form of the two paths masked as [file] and their folders as [folder], then the scrubbed last line only when it is a suffix of the whole text scrubbed as one line, else [REDACTED]"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/03-service-layer.md:732 - the job fails with the FFmpegNotFoundError message on its card"
      - "packages/core/src/avkit_core/services/download.py:665-688 - Session 65's cause, reason and failed-log path"
      - "C:/Temp/av-kit/s67/convert-probe.txt - FFmpeg's first stderr line is the banner and its last holds the error"
      - "C:/Temp/av-kit/s67/fmt-probe.txt - the revised detail against the real Console store and console.log, 18 cases, 0 failures"
    research:
      engine: none
      sources: []
    reasoning: "Reusing Session 65's causes keeps one card vocabulary; the not-found text is fixed adapter text, so it can be the reason. FFmpeg's stderr holds paths and is multi-line, so the card gets a fixed reason and the Console gets the last line with paths replaced, which is where FFmpeg puts the error. A new convert_failed cause lost: it would move the domain enum, the UI and the OpenAPI snapshot for no new user action. The first line lost: it is always the version banner. Plan review round 1 showed that taking the last line before redaction let a secret on the line after its needle reach the Console, and that exact path replacement missed slash and escaped forms; the suffix rule keeps the detail inside the whole-text scrub. Two-way."
    human_message_reference: null
  - id: D-669
    stage: planning
    question: "How do cancel, status and the conversion queue relate to the convert?"
    resolution: autonomous
    class: two-way
    chosen: "No stop hook and no new status: the job stays Downloading during the convert; a cancel during the download gives Cancelled with no convert; a cancel during the convert lets the job finish Done and the worker stops at its next loop; no ConversionJob row and no ConversionService call"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/03-service-layer.md:731 - the convert creates no ConversionJob row"
      - "packages/core/src/avkit_core/services/download.py:566-598 - _cancel_inflight runs only on the worker thread between jobs"
      - "C:/Temp/av-kit/s67/convert-probe.txt - each 3 s clip converts in about 0.04 s"
    research:
      engine: none
      sources: []
    reasoning: "An audio convert is short next to the download, and a stop hook would need a port change the residual section doesn't ask for. Finishing Done on a late cancel gives the user the file they waited for. A Converting status lost: it moves the enum, the UI and the snapshot. Routing through ConversionService lost: 08 forbids the row. Two-way."
    human_message_reference: null
  - id: D-670
    stage: planning
    question: "Where do the tests live and what runs on CI?"
    resolution: autonomous
    class: two-way
    chosen: "Unit tests with a recording fake MediaPort in tests/unit/test_download_audio_extract.py, on the fake unit of work and a SQLite stack, including the real FFmpegAdapter with no binary; one real-FFmpeg module in tests/integration/test_download_audio_extract_real_ffmpeg.py on a generated clip and the pinned pair, deselected on CI by ci.yml; the wiring identity test in tests/integration/test_api_wiring.py"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/03-service-layer.md:733 - unit with a fake MediaPort; one real-ffmpeg integration test on a generated clip, deselected on CI"
      - "tests/integration/test_extract_real_ffmpeg.py - Session 54's real-FFmpeg module, deselected at ci.yml:65"
    research:
      engine: none
      sources: []
    reasoning: "The 03 Tests row names this layout. The no-binary case uses the real adapter with which patched, so the card text is proven against the real raise on CI too. Running the real-FFmpeg module on CI lost: the pinned pair is fetched, not tracked. Two-way."
    human_message_reference: null
  - id: D-671
    stage: planning
    question: "Does the session make any network request, such as a live MP3 download?"
    resolution: human
    class: two-way
    chosen: "B: one live StandardMp3 download of a public video with cookies off, after the gate and on Mat's words, as a recorded manual check written under C:/Temp/av-kit/s67/live/; it prints and stores no cookie value, and no test or suite row reaches the network"
    recommendation: "A: no network; the suites stay offline and a live MP3 download in the app stays a named open manual check in the handoff and the register's verification"
    source_tag: Human-approved
    precedents:
      - "Session 67 prompt: Network: recommendation none. A live MP3 download stays a named manual check"
      - "Session 66 D-642 - each live probe brought to Mat first, recorded as a manual check"
    research:
      engine: none
      sources: []
    reasoning: "The convert runs on a local file, so a live download proves nothing the real-FFmpeg test on a generated clip doesn't, beyond yt-dlp's own behaviour, which Session 66 measured. B measures one real StandardMp3 job end to end at the cost of a YouTube request. D records nothing, so a later reader can't tell the live path was never run."
    human_message_reference: "USER_EXPLICIT 2026-11-12 'B: one live public download'"
```

### D-671 brief: Network and a live MP3 download   [outward-facing]

**Recommendation:** A. No network in the session. Every test runs offline: the unit tests use a fake `MediaPort`, and the real-FFmpeg test converts a clip it generates with the pinned FFmpeg. A live MP3 download in the app stays a named open manual check, written in the MEU-142 handoff and in the issue's verification, for you to run when you choose.

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ A: offline; the live download is a named open manual check | — | — | Session 67 prompt; 03 Tests row `:733` |
| ⚠️ B: one live `StandardMp3` download of a public video with cookies off, after the gate and on your words, written to `C:/Temp/av-kit/s67/live/` and recorded; it prints and stores no cookie value | proves one real job end to end in the session | one YouTube request; adds a manual step before closeout | Session 66 D-642 |
| ❌ D: do nothing (offline, no manual check recorded) | no extra record | the handoff and the register don't say the live path was never run | — |

**Reversibility:** two-way; a live check can run in any later session. **If you do not answer:** row 0 stops (S9).

## Research References

- FFmpeg n8.1.3 (`packaging/ffmpeg-win64/`), read and run offline: `libmp3lame` present; each of `audio.m4a`, `audio.webm`, `av.mp4` and `av.webm` converts with the adapter's command shape to one `mp3` stream, and a video-only or empty input fails with the error on stderr's last line (`C:/Temp/av-kit/s67/convert-probe.txt`, `C:/Temp/av-kit/s67/ffmpeg-pin-probe.txt`).
- No web research: every rule comes from 02, 03, 08 and the grouping.

## Planning receipts

- `C:/Temp/av-kit/s67/id-probe.txt` and `C:/Temp/av-kit/s67-plan-id-probe2.txt`: D-664 to D-673 and AC-142 free; the project files' endings.
- `C:/Temp/av-kit/s67/dep-probe.txt`: MEU-142 `pending`, its dependencies `approved`.
- `C:/Temp/av-kit/s67/sig-sweep.txt`: signature and source pins over `tests/`.
- `C:/Temp/av-kit/s67/endings-baseline.txt`: endings and SHA-256 of the targets.
- `C:/Temp/av-kit/s67/convert-probe.txt` and `C:/Temp/av-kit/s67/ffmpeg-pin-probe.txt`: the convert probe and the pinned pair.
- `C:/Temp/av-kit/s67/fmt-probe.txt`: the revised `FAIL_DETAIL` model (`C:/Temp/av-kit/s67/fmt-probe.py`) through the real `HealthService` Console store and `console.log`, 18 cases, 0 failures, no leak in the persisted log.
- `C:/Temp/av-kit/s67-plan-matrix-probe.txt`: the input matrix's grep evidence (no test runs a `StandardMp3` job; the eight construction sites; `CONSOLE_FIELDS`; the adapter's `media.convert` line).
- `C:/Temp/av-kit/s67-plan-decision-probe.txt`: the decision probe. With this plan, the grouping and the register (`DOWNLOAD-MP3-NOT-CONVERTED`) it returns 18 decisions: D-664 to D-671 `planning`, D-535 to D-543 `grouping`, D-534 `triage`. Without the grouping it refuses (HDP-18). Each source's SHA-256 is unchanged by the run.
- `C:/Temp/av-kit/s67-plan-red-check-selftest.txt` and `C:/Temp/av-kit/s67-plan-identity-selftest.txt`: the two selftests (47 fixtures, 0 wrong; 0 failures).
- `C:/Temp/av-kit/s67-plan-shapes-dry-run.txt`: `baseline.ps1`'s shapes block run alone at `3435b7e` (exit 0).
- `C:/Temp/av-kit/s67-plan-task-lint.txt`: `lint_task_contract.py` on `task.md`.
- `C:/Temp/av-kit/s67-plan-ci-collect-pre.txt`: `ci-collect.py` before row 4 (exit 1, the module not deselected), as AC-142.19's negative.
- Not run at plan time: any suite or build.

## Validation stage contract

- **Static:** `pyright`, `ruff check packages/ tests/`, `npm --prefix ui run typecheck`, `ui-lint`, `lint_task_contract.py`, the scope-paths check, the `red-check.py` selftest and `ci-collect.py`.
- **Targeted:** each row's own files, with `red-check.py` reading the Red receipt.
- **Fresh full:** the whole Python, UI and MCP suites, the OpenAPI check, the UI and MCP builds, the two render checks, the real-FFmpeg module and the Downloader Electron spec, in the session gate.
- **Identity:** `identity.py` binds `HEAD`, the work tree minus `PROJECT_ARTIFACTS`, the pinned FFmpeg pair and the runtime. The gate records it before and after, and H1-6b checks the handoff's evidence against it.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
