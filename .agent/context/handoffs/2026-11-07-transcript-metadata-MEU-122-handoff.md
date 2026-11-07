---
date: "2026-11-07"
project: "transcript-metadata"
meu: "MEU-122"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-07-transcript-metadata/implementation-plan.md"
build_plan_section: "bp03"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "none"
---

# Handoff: 2026-11-07-transcript-metadata-MEU-122-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-122 `svc-transcript-metadata` (`TRANSCRIPT-TITLE-IS-VIDEO-ID`, triage D-223; `TRANSCRIPT-CHANNEL-IS-PLAYLIST-NAME`, triage D-224; one MEU per grouping D-241). A transcript's files, compiled headings, Contents and "Last:" label now show the video's title, and its channel name is the channel's. The folder and volume names are unchanged, and no request is added per video.
**Build Plan Section**: [03 §Transcript source metadata (residual)](../../../docs/build-plan/03-service-layer.md), Delivered note after the residual's table (`:677-684`).
**Predecessor**: none.

- **Listing (rows 1, 2; D-346, D-347, `LISTING`, `TEXT_CLEAN`).**
  - `domain/download.py` gains `ListedVideo` (`:270`) and `VideoListing` (`:282`), frozen. `_require_text_clean` (`:251`) refuses a title or channel name that isn't single-spaced text without control characters or lone surrogates (D-360), and its message names the field, never the value. `VideoListing` refuses a repeated `video_id`. `PlaylistInfo` is unchanged (AC-122.6).
  - `YouTubePort.extract_video_ids` returns `VideoListing` (`ports/youtube.py:25`). The coordinator caches the listing object itself (`services/extract.py:22`, `:49-62`).
  - The adapter's `extract_video_ids` (`youtube/adapter.py:472-484`) reads the flat enumeration it already ran: each entry's ID and `_clean_text` title (`:143`, which drops control characters and lone surrogates, `_UNCLEAN_CATEGORIES` `:140`), and the top-level `channel`, falling back to `uploader`. `_listed_videos` (`:158`) keeps the first title of a repeated ID. A single video lists itself with its own title. `_unique_preserve_ids` stays for `extract_info`.
  - **`FLAT_TABS` (D-354 ruled flatten, D-358).** A bare channel URL returns one nested `playlist` entry per tab. `_listed_videos` lists each tab's own entries, one level deep, and never a tab's ID (the channel's) or title (the tab's); anything nested further is dropped.
- **Service (row 2; D-348 to D-351).**
  - `add_channel` (`services/transcript.py:143`) stores each listed title on its item (`STORED_TITLE`, `:192`). The channel name is `listing.channel_name or info.title` (`CHANNEL_SOURCE`, `:169`). The folder keeps the extract title's slug (`SLUG_SOURCE`, `:160-163`, `:172`), and `_write_volumes` and `_zip_raw` take the slug from the folder's name (`:347`, `:381`), so volume and zip names don't change.
  - `_fetch_item` keeps the stored title, with the result's title (the video ID) as the fallback (`TITLE_KEPT`, `:611`).
  - `_raw_markdown` quotes the title and channel with `json.dumps` (`QUOTED_FRONT_MATTER`, `:752-761`), and `_contents_label` escapes backslashes and square brackets in the Contents link text (`ESCAPED_CONTENTS`, `:768-770`).
- **API (rows 3, 4; D-352, `LAST_TITLE_PROCESSED`).** `_aggregates` (`routes/transcripts.py:35`) shows a title under "Last:" only from an item with a `processed_at`, because stored titles would otherwise label an unprocessed video. No schema change; the OpenAPI check is a guard (H1-4).
- **Raw values (D-356, D-357).** Titles reach no Console field (AC-122.16), and the SQL engine is built with `hide_parameters=True` (`database/engine.py:82`), so a SQL error's text holds no bound value (`SQL_PARAMS_HIDDEN`, AC-122.17).
- **Shapes (row 0a; D-353, `SHAPES_RECORD`).** Measured live once on Mat's yes (2026-11-07), on four URLs, recording which fields were present and never their values, with no retry: the Videos tab's and the playlist's flat entries each held an `id` and a `title` (3 of 3), every top level held a `channel`, and the bare channel returned three nested `playlist` tabs whose inner entries held an `id` and a `title` (3 of 3 each). `measure-shapes: 0 problem(s)` (`C:/Temp/av-kit/s53-shapes.txt`).
- **Review round 1 correction (rows C1 to C6; D-360).** Round 1 returned `changes_required` with one High finding, F1: a lone surrogate (a code point from U+D800 to U+DFFF standing alone) in a listed title or channel passed `TEXT_CLEAN`, then SQLite and the UTF-8 raw file refused it, so `add_channel` raised `UnicodeEncodeError` and the whole job failed to be created. `_clean_text` now drops Unicode category `Cs` as it drops `Cc`, so such a title becomes the rest of its text, or `None` and the ID fallback; `_require_text_clean` refuses `Cs`, so the domain guard agrees. Other Unicode, format characters such as U+200B included, is kept. No request is added. AC-122.1, AC-122.2 and AC-122.8 each gain a test (row C1), and AC-122.8's runs through the real adapter, a real SQLite engine and the real file system.
- **Spec text (row 5).** 01 gains the two DTO rows (`:209-210`; row C2 adds "or lone surrogates" to `:209`), the Resolve row (`:272`) and the port's return (`:435`). 02 gains the listing paragraph (`:347`). 03 step 4 names the slug source (`:211`) and gains the Delivered note (`:677-684`). 06's output tree names `SLUG_SOURCE` and `{folder}` (`:708`, `:713-716`).

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-07-transcript-metadata/implementation-plan.md) §MEU-122. **Execution authorization:** `USER_EXPLICIT`, 2026-11-07, "proceed, D-353 yes, D-354 Flatten the tabs now", given after the Codex plan review approved in round 2 ([plan-critical-review.md](2026-11-07-transcript-metadata-plan-critical-review.md)); recorded in [human-gate-decision.md](../../../docs/execution/plans/2026-11-07-transcript-metadata/human-gate-decision.md) (`plan_to_exec_gate: human`).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-122.1 | unit | `VideoListing` and `ListedVideo` exist and are frozen; empty IDs, duplicate IDs and non-`TEXT_CLEAN` text, lone surrogates included, are refused, and no message holds the value; other Unicode is accepted; the port's return hint is `VideoListing` | Local Canon: triage D-223; D-346; D-360 | `tests/unit/test_transcript_metadata.py:56`, `:110` | ✅ |
| AC-122.2 | integration | A Videos-tab dict and a playlist dict map to their videos, titles and top-level `channel`; a title with inner newlines, double spaces and control characters comes back `TEXT_CLEAN`; a duplicate ID keeps its first title; lone surrogates are dropped from a title and the channel, a title of only a surrogate gives `None`, and accented, CJK, emoji and zero-width text is kept | Local Canon: triage D-223, D-224; D-360 | `tests/integration/test_youtube_adapter.py:791`, `:831` | ✅ |
| AC-122.3 | integration | A missing or non-`str` title gives `None`; a missing `channel` takes `uploader`; neither gives `None` | Local Canon: 03 `:671`, `:673` | `tests/integration/test_youtube_adapter.py:928` | ✅ |
| AC-122.4 | integration | A single video gives one `ListedVideo` with its title and its `channel` | Local Canon: D-347 | `tests/integration/test_youtube_adapter.py:952` | ✅ |
| AC-122.5 | integration | The amended `test_ac_6_4_extract_video_ids_playlistend_ctor`: the IDs are `[v.video_id for v in listing.videos]`; its `extract_flat` and `playlistend` assertions are unchanged | Local Canon: triage D-223 | `tests/integration/test_youtube_adapter.py:277` | ✅ |
| AC-122.6 | unit | `PlaylistInfo`'s fields and the `extract_info` annotation are unchanged (guard, passes in Red) | Local Canon: brief | `tests/unit/test_transcript_metadata.py:129` | ✅ |
| AC-122.7 | unit | The coordinator caches the listing: two calls return the same object and `ids_calls` is 1 | Local Canon: 03 `:173-177` | `tests/unit/test_transcript_metadata.py:148` | ✅ |
| AC-122.8 | unit | Items hold their listed titles before any fetch; each raw file's front matter holds its title and the channel; the volume holds `# channel`, a Contents link and `## title` for each; through the real adapter, SQLite engine and file system, a title and channel holding lone surrogates are created without error, stored cleaned, processed to Done and written as UTF-8 | Local Canon: 03 contract ("Tests"); D-360 | `tests/unit/test_transcript_metadata.py:167`, `tests/integration/test_youtube_adapter.py:860` | ✅ |
| AC-122.9 | unit | A listed title of `None` gives the ID in the front matter, the Contents and the heading | Local Canon: 03 contract ("Tests") | `tests/unit/test_transcript_metadata.py:196` | ✅ |
| AC-122.10 | unit | A listed channel of `None` gives `info.title`; a listed channel gives that channel, in the front matter and the H1 | Local Canon: 03 contract; triage D-224 | `tests/unit/test_transcript_metadata.py:214` | ✅ |
| AC-122.11 | unit | The folder `my-channel`, the volume `my-channel_vol1.md` and the zip `my-channel_raw.zip`, whether the channel name differs from `info.title` or not | Local Canon: triage D-224 | `tests/unit/test_transcript_metadata.py:232` (2 cases) | ✅ |
| AC-122.12 | unit | At 2 and 50 videos, after `add_channel` and after processing: `extract_calls == 1`, `ids_calls == 1`, no download (`last_options is None`) | Local Canon: 03 contract; triage D-223 | `tests/unit/test_transcript_metadata.py:253` (2 cases) | ✅ |
| AC-122.13 | unit | A fetch whose result's title differs keeps the stored title in the item and the file; a retried failed item keeps it too | Local Canon: 03 contract ("Stored title") | `tests/unit/test_transcript_metadata.py:267` | ✅ |
| AC-122.14 | unit | A title holding `:`, `"`, `[`, `]` and `\`: the front matter parses back with `json.loads`, the Contents label is escaped, the heading is verbatim, and the body is the transcript's | Local Canon: D-351; 06 `:722-723` | `tests/unit/test_transcript_metadata.py:298` | ✅ |
| AC-122.15 | e2e | Items with titles and no `processed_at` give `last_title` `None` on both endpoints; a processed item gives its title | Local Canon: D-352; brief ("Last:") | `tests/e2e/test_api_transcripts.py:145` | ✅ |
| AC-122.16 | unit | A marker title and channel, with a failing item, reach the raw file and not the ring, stdout or `console.log`; a control marker reaches all three; `_YtDlpLogger(True).debug(marker)` adds only the bare `yt-dlp` event, with no field holding the marker (D-359) | Local Canon: Session 50 RULE-1; D-356; D-359 | `tests/unit/test_transcript_metadata.py:324` | ✅ |
| AC-122.17 | unit | A failed insert on a real `create_sqlite_engine` engine: neither `str(exc)` nor `console_field(str(exc))` holds the bound marker | Local Canon: Session 50 RULE-1; D-357 | `tests/unit/test_transcript_metadata.py:368` | ✅ |
| AC-122.18 | integration | `FLAT_TABS`: three nested tabs (Videos with two videos; Shorts with a new video, a duplicate under another title and a nested playlist; Live without `entries`) give the two Videos videos, then the new Shorts one; the duplicate keeps its Videos title; no channel ID, tab title or inner playlist ID appears; `channel_name` is the top-level `channel` | Human-approved: D-354, 2026-11-07; D-358 | `tests/integration/test_youtube_adapter.py:966` | ✅ |
| AC-16 (cross-ref) | regression | `test_ac_16_2_aggregates_without_video_ids_or_text` passes unchanged | plan §Acceptance Criteria (guards) | `tests/e2e/test_api_transcripts.py` (row 4; gate `py-tests`) | ✅ |
| AC-6 (cross-ref) | regression | Every other AC-6 adapter test and every download test in `tests/unit/test_services.py` passes unchanged with the `VideoListing` fake | plan §Acceptance Criteria (guards) | rows 2 and 4; gate `py-tests` | ✅ |
| AC-51, AC-81 (cross-ref) | regression | `ui/tests/e2e/test-ids.ts` is unchanged (scope-paths refuses it), so the byte-hash tests pass | plan §Files Modified | gate `scope-paths`, `ui-tests` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-122.1 to AC-122.5, AC-122.7 to AC-122.14, AC-122.16, AC-122.18 | Row 1: `AssertionError: assert False` where `False = hasattr(download_domain, 'VideoListing')` (17 failures); each test asserts the new names first (Session 52 RULE-4) | Row 2: pass | `test_transcript_metadata.py:56-324`, `test_youtube_adapter.py:277`, `:791-966` |
| AC-122.17 | Row 1: `assert 'SYNTHETIC_SQL_MARKER' not in '(sqlite3.In...'`: the error's text holds `parameters: ('SYNTHETIC_SQL_MARKER',)` | Row 2: pass | `test_transcript_metadata.py:368` |
| AC-122.15 | Row 3: `assert ('Latest', 'Latest') == (None, None)`: today the last item's stored title shows | Row 4: pass | `test_api_transcripts.py:145` |
| AC-122.6 | Guard: passes in Red by design | Row 2: pass | `test_transcript_metadata.py:129` |
| AC-122.1, AC-122.2, AC-122.8 lone surrogates (F1) | Row C1: `Failed: DID NOT RAISE ValidationError`; `assert VideoListing(...'Chan \udfff') == VideoListing(...l_name='Chan')`; `assert 'UnicodeEncodeError' is None`, the real `add_channel` failure | Row C2: pass | `test_transcript_metadata.py:110`, `test_youtube_adapter.py:831`, `:860` |

- **Row 1 Red:** 18 failed, 1 passed (the AC-122.6 guard) and 21 deselected in 1.72s. `red-check.py` required 16 tests and found 0 problems. No collection or import error.
- **Row 3 Red:** 1 failed and 3 deselected in 2.12s, by assertion. `red-check.py` found 0 problems.
- **Green:** row 2, 243 passed over the metadata, adapter, service, domain, failure-delivery, block-done, SQLite UoW, transcript API and error-surface suites, with pyright 0 errors. Row 4, 15 passed, with pyright 0 errors. No test file changed in a Green row.
- **Row C1 Red (F1):** 3 failed and 40 deselected in 2.89s, each by assertion; `red-check.py` required the 3 tests and found 0 problems. AC-122.8's Red reproduces the reviewer's failure on the real path: `add_channel` raised `UnicodeEncodeError`.
- **Row C2 Green (F1):** 247 passed over row 2's suites, pyright 0 errors, ruff check passed. No test file changed in row C2.

Receipts: `C:/Temp/av-kit/s53-shapes.txt`, `s53-baseline.txt`, `s53-base-py.txt`, `s53-base-ui.txt`, `s53-base-mcp.txt`, `s53-listing-red.txt`, `s53-listing-red-check.txt`, `s53-listing-green.txt`, `s53-listing-types.txt`, `s53-api-red.txt`, `s53-api-red-check.txt`, `s53-api-green.txt`, `s53-api-types.txt`, `s53-resolve.txt`, `s53-r5-*.txt`, `s53-c1-red.txt` (with `.exit`), `s53-c1-red-check.txt`, `s53-c2-green.txt`, `s53-c2-types.txt`, `s53-c2-lint.txt`, gate run 2's `s53-gate-h1-r2.txt` and `s53-D6-<id>.txt` (run 1's copies are in `s53-gate-r1/`), and `drift-check.txt` and `openapi-check.txt`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "check_id": "s53-0a-shapes", "command": "rtk proxy uv run python docs/execution/plans/2026-11-07-transcript-metadata/measure-shapes.py --live *> C:/Temp/av-kit/s53-shapes.txt (task.md row 0a, run from P:/av-kit on Mat's D-353 yes)", "cwd": "P:/av-kit", "scope": "Row 0a SHAPES_RECORD: yt-dlp's installed version and source strings, then one flat extract each of a channel Videos tab, the same channel bare, a playlist and a single video, with playlistend 3, no cookies and no retry, recording field presence only", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9093d95 (baseline.sha), before row 0", "output": "yt-dlp version: 2026.10.26 (expected 2026.10.26); every source string found. channel-videos-tab: top channel, uploader and title present; entries 3, _type {url: 3}, id 3/3, title 3/3. bare-channel: entries 3, _type {playlist: 3}; tab 0, 1 and 2 each: entries 3, _type {url: 3}, id 3/3, title 3/3. playlist: top channel present; entries 3, id 3/3, title 3/3. single-video: _type None; channel, uploader and title present; entries none. measure-shapes: 0 problem(s)."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s53-122-listing-red", "command": "$env:TMP='C:\\Temp\\av-kit\\s53\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest tests/unit/test_transcript_metadata.py tests/integration/test_youtube_adapter.py -k \"ac_122 or test_ac_6_4_extract_video_ids_playlistend_ctor\" --tb=short -q *> C:/Temp/av-kit/s53-listing-red.txt; then red-check.py --require on the 16 required tests *> C:/Temp/av-kit/s53-listing-red-check.txt (abridged from task.md row 1's Validation cell, run from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-122 Red, listing and service: AC-122.1 to AC-122.14, AC-122.16 to AC-122.18 and the amended 6.4 test against the unchanged code, with the fake's VideoListing return in place", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9093d95 plus rows 0, 0a and 1", "output": "18 failed, 1 passed, 21 deselected in 1.72s. Decisive: AssertionError: assert False where False = hasattr(download_domain, 'VideoListing') for 17 tests; assert 'SYNTHETIC_SQL_MARKER' not in '(sqlite3.In...' for AC-122.17. red-check: 1 receipt(s), 16 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s53-122-listing-green", "command": "$env:TMP='C:\\Temp\\av-kit\\s53\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest tests/unit/test_transcript_metadata.py tests/integration/test_youtube_adapter.py tests/unit/test_services.py tests/unit/test_domain.py tests/integration/test_transcript_failure_delivery.py tests/integration/test_transcript_block_done.py tests/integration/test_sqlite_uow.py tests/e2e/test_api_transcripts.py tests/e2e/test_api_error_surface.py --tb=short -q *> C:/Temp/av-kit/s53-listing-green.txt; then rtk proxy uv run pyright packages/ *> C:/Temp/av-kit/s53-listing-types.txt (task.md row 2's Validation cell, run from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-122 Green, listing, service and SQL, with the existing adapter, service, domain, transcript delivery, UoW and API suites", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9093d95 plus rows 0 to 2", "output": "243 passed. pyright: 0 errors, 0 warnings, 0 informations."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s53-122-api-red", "command": "$env:TMP='C:\\Temp\\av-kit\\s53\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest tests/e2e/test_api_transcripts.py -k ac_122_15 --tb=short -q *> C:/Temp/av-kit/s53-api-red.txt; then red-check.py --require test_ac_122_15 *> C:/Temp/av-kit/s53-api-red-check.txt (abridged from task.md row 3's Validation cell, run from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-122 Red, API: AC-122.15 against the unchanged _aggregates", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9093d95 plus rows 0 to 3", "output": "1 failed, 3 deselected in 2.12s. Decisive: AssertionError: assert ('Latest', 'Latest') == (None, None). red-check: 0 problem(s). The row exits 0 because red-check confirms the decisive failure."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s53-122-api-green", "command": "$env:TMP='C:\\Temp\\av-kit\\s53\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest tests/e2e/test_api_transcripts.py tests/e2e/test_api_error_surface.py --tb=short -q *> C:/Temp/av-kit/s53-api-green.txt; then rtk proxy uv run pyright packages/ *> C:/Temp/av-kit/s53-api-types.txt (abridged from task.md row 4's Validation cell, run from P:/av-kit)", "cwd": "P:/av-kit", "scope": "MEU-122 Green, API, with the transcript API and error-surface suites", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9093d95 plus rows 0 to 4", "output": "15 passed in 15.49s. pyright: 0 errors, 0 warnings, 0 informations."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s53-row5-hub", "command": "task.md row 5 (abridged), run from P:/av-kit: tools/meu_status.py update MEU-122 ready_for_review --plan docs/execution/plans/2026-11-07-transcript-metadata/ and render; rtk proxy uv run python docs/execution/plans/2026-11-07-transcript-metadata/issue-resolve.py --issue TRANSCRIPT-TITLE-IS-VIDEO-ID --issue TRANSCRIPT-CHANNEL-IS-PLAYLIST-NAME --set-file C:/Temp/av-kit/s53-resolve.json --expect-sha256 $sha *> C:/Temp/av-kit/s53-resolve.txt; issue_triage.py render and triage; grouping row 53; then its Validation cell, through an extracted .ps1: the resolve receipt's '^issue-resolve: 0 problem', meu_status.py render --check *> C:/Temp/av-kit/s53-r5-render.txt, issue_triage.py render --check *> C:/Temp/av-kit/s53-r5-issues.txt, and the two statuses and the grouping row *> C:/Temp/av-kit/s53-r5-status.txt", "cwd": "P:/av-kit", "scope": "Row 5 hub: the 01, 02, 03 and 06 spec text, MEU-122 ready_for_review, both issues resolved through issue-resolve.py, the renders and grouping row 53 naming the plan", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9093d95 plus rows 0 to 5", "output": "register sha256 before=0bcd5af73a865097f2353d1f9ad9bb51c503c6924f94629c6f6f8e0ed34285fa (the plan-time hash), after=6694ff336c3d5cbeb460525fe496ab4d35595bb10830bd189a618498de38d08e CRLF=0 LF=4182; parsed fields changed: 10 (issues[78] and issues[79] resolution_path, status, verification.last_checked, method and result); issue-resolve: 0 problem(s). ['resolved', 'resolved']. grouping tracker names the plan: True."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s53-122-c1-red", "command": "$env:TMP='C:\\Temp\\av-kit\\s53\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest tests/unit/test_transcript_metadata.py tests/integration/test_youtube_adapter.py -k surrogate --tb=short -q *> C:/Temp/av-kit/s53-c1-red.txt; then red-check.py --require test_ac_122_1_lone_surrogate_text_is_refused --require test_ac_122_2_lone_surrogate_is_dropped --require test_ac_122_8_surrogate_title_survives_real_storage *> C:/Temp/av-kit/s53-c1-red-check.txt (abridged from task.md row C1's Validation cell, run from P:/av-kit through an extracted .ps1)", "cwd": "P:/av-kit", "scope": "Review round 1 F1, Red (D-360): the three lone-surrogate tests against the unchanged _clean_text and _require_text_clean. AC-122.8's runs the real YouTubeAdapter over a patched YoutubeDL, a real SQLite engine with init_schema, SqlAlchemyUnitOfWork, SettingsService, FilesystemAdapter and FakeCaptions, and records add_channel's exception by class name so the Red fails by assertion", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 9093d95 plus rows 0 to 5, H1 and C1", "output": "3 failed, 40 deselected in 2.89s. Decisive: Failed: DID NOT RAISE ValidationError (AC-122.1); assert VideoListing(...'Chan \\udfff') == VideoListing(...l_name='Chan') with title 'Talk \\ud800 title' kept (AC-122.2); assert 'UnicodeEncodeError' is None (AC-122.8, the real add_channel). red-check: 1 receipt(s), 3 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s53-122-c2-green", "command": "$env:TMP='C:\\Temp\\av-kit\\s53\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest tests/unit/test_transcript_metadata.py tests/integration/test_youtube_adapter.py tests/unit/test_services.py tests/unit/test_domain.py tests/integration/test_transcript_failure_delivery.py tests/integration/test_transcript_block_done.py tests/integration/test_sqlite_uow.py tests/e2e/test_api_transcripts.py tests/e2e/test_api_error_surface.py --tb=short -q *> C:/Temp/av-kit/s53-c2-green.txt; then rtk proxy uv run pyright packages/ *> C:/Temp/av-kit/s53-c2-types.txt; then rtk proxy uv run ruff check packages/ tests/unit/test_transcript_metadata.py tests/integration/test_youtube_adapter.py *> C:/Temp/av-kit/s53-c2-lint.txt (task.md row C2's Validation cell, run from P:/av-kit through an extracted .ps1)", "cwd": "P:/av-kit", "scope": "Review round 1 F1, Green (D-360): _clean_text drops categories Cc and Cs (youtube/adapter.py:140-153), _require_text_clean refuses both (domain/download.py:251-266), and 01-domain-layer.md:209 says so; row 2's suites, pyright and ruff", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "9093d957f1fd3225cec42712137acf021d6605bf+65399a3bed6c6e9d76a68516f7f2b046f01788b5357c89f1e3566c27fc837c2a", "output": "247 passed in 16.38s. pyright: 0 errors, 0 warnings, 0 informations. ruff check: All checks passed!"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s53-gate-c3", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-07-transcript-metadata/session-gate.ps1 *> C:/Temp/av-kit/s53-gate-h1-r2.txt; $code=$LASTEXITCODE; Select-String -Path C:/Temp/av-kit/s53-gate-h1-r2.txt -Pattern ' exit=','not_run','tested_state','_sha256 ','outside scope','mismatch','session-gate:'; exit $code", "cwd": "P:/av-kit", "scope": "Row C3, gate run 2: the registered D6 gate on the whole tree after rows C1 and C2: identity, every static check, both full suites, the UI build, OpenAPI, the MCP types, tests and build, both renders and the targeted Electron spec, then the identity again", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "9093d957f1fd3225cec42712137acf021d6605bf+65399a3bed6c6e9d76a68516f7f2b046f01788b5357c89f1e3566c27fc837c2a", "output": "identity-before exit=0; py-types exit=0 (0 errors, 0 warnings, 0 informations); py-lint exit=0 (All checks passed!); ui-types exit=0; ui-lint exit=0 (eslint --max-warnings 0); task-contract exit=0 (30 rows, 28 fully checked, 2 view_file exempt: H1-5, H2-1); scope-paths exit=0 (changed paths: 37, outside scope: [], head moved: False); red-check-selftest exit=0 (36 fixtures, 11 positive, 25 negative, 0 wrong); py-tests exit=0 (1318 passed); ui-tests exit=0 (112 files, 1174 passed); ui-build exit=0; openapi exit=0; mcp-types exit=0; mcp-tests exit=0 (35 files, 470 passed); mcp-build exit=0; state-render exit=0 (127 MEUs, 12 phases, regions match); issues-render exit=0 (known-issues.md is up-to-date); ui-electron exit=0 (transcript-queue.test.ts, 11 passed); identity-after exit=0 (tested_state before = after); mcp-audit, build-record and package-build skipped; baseline failures excused: py [], ui [], mcp []; session-gate: all steps exit 0 (second attempt; the first stopped at ui-electron, see Quality Gate Results)"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s53-h1-3-render", "command": "rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/drift-check.txt (H1-3's cell, run through C:/Temp/av-kit/s53/tmp/h1-34.ps1 from P:/av-kit)", "cwd": "P:/av-kit", "scope": "H1-3: rendered state regions against meu-status.yaml, after the current focus was updated. No status was written here; row 5 set MEU-122 ready_for_review", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "9093d957f1fd3225cec42712137acf021d6605bf+21d9393a0d0e812c88f1b57abd4eeb5ec5b042d11ddba2762f3cf1b70cd36a20", "output": "Drift check passed: SSOT loaded (127 MEUs, 12 phases), rendered regions match on-disk content"}
```

```json
{"schema_version": "evidence.v1", "check_id": "s53-h1-4-openapi", "command": "rtk proxy uv run python tools/export_openapi.py --check openapi.committed.json *> C:/Temp/av-kit/openapi-check.txt (H1-4's cell, run through C:/Temp/av-kit/s53/tmp/h1-34.ps1 from P:/av-kit)", "cwd": "P:/av-kit", "scope": "H1-4: packages/api changes only inside _aggregates' body, with no schema change; the OpenAPI check runs as a guard, and any drift would be S6", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "9093d957f1fd3225cec42712137acf021d6605bf+21d9393a0d0e812c88f1b57abd4eeb5ec5b042d11ddba2762f3cf1b70cd36a20", "output": "exit 0; check_openapi prints nothing when openapi.committed.json matches the live schema"}
```

### Quality Gate Results

`s53-gate-c3` (row C3, gate run 2) is the fresh full record, and its last line is:

> session-gate: all steps exit 0

- **Static:** pyright 0 errors, 0 warnings; ruff check passed; the UI typecheck and ESLint (`--max-warnings 0`) passed; lint_task_contract passed on 30 rows (28 fully checked, 2 `view_file` exempt); scope-paths found 37 changed paths, none outside scope, `ui/tests/e2e/test-ids.ts` unchanged, and HEAD 9093d95 did not move (the 3 paths beyond run 1's 34 are this handoff, the implementation review and `current-focus.md`); the red-check selftest read 36 fixtures with 0 wrong.
- **Suites:** pytest 1318 passed (run 1's 1315 plus the three row C1 tests); Vitest 1174 passed in 112 files (baseline 1174); MCP tests 470 passed in 35 files (baseline 470). No baseline failure was excused.
- **Build and state:** the UI build, the OpenAPI check, the MCP typecheck and the MCP build exited 0; the state render (127 MEUs) and the issue render match the files on disk.
- **Runtime:** the targeted Electron spec `tests/e2e/transcript-queue.test.ts` passed 11 of 11, so the transcript page still renders its queue and job states. It asserts no "Last:" title; AC-122.15 covers the API side, and the renderer's label code is unchanged.
- **First attempt of run 2.** It passed every step up to `ui-electron`, where one test (W2-4, "E2E_HAPPY_PATH via E2E_SEAM") failed with `page.reload: net::ERR_ABORTED; maybe frame was detached?` in `installTranscriptSeam` (`ui/tests/e2e/transcript-queue.test.ts:177`); the other 10 passed. The gate is fail-fast, so `identity-after` did not run. Rows C1 and C2 change no file under `ui/` (`git diff --stat HEAD -- ui/` is empty), and the machine was loaded: that attempt's pytest took 305 s against 191 s on the rerun, and its Electron spec 2.6 min against 22 s. The whole gate was rerun unchanged and passed. The attempt's receipts are kept in `C:/Temp/av-kit/s53-gate-r2a/`. The reload flake is reported to Mat, not filed here.
- **Skipped:** `mcp-audit` (live network and YouTube, which the brief forbids), `build-record` (no installer build) and `package-build` (no packaged surface changes; MEU-125 runs the package build and its smokes).
- **Identity:** the tested_state was the same before and after the gate: `9093d957f1fd3225cec42712137acf021d6605bf+65399a3bed6c6e9d76a68516f7f2b046f01788b5357c89f1e3566c27fc837c2a`.
- **Earlier run.** Run 1 (H1-2) passed every step on `9093d957f1fd3225cec42712137acf021d6605bf+21d9393a0d0e812c88f1b57abd4eeb5ec5b042d11ddba2762f3cf1b70cd36a20`, the tree review round 1 read; its receipts are in `C:/Temp/av-kit/s53-gate-r1/`. Rows C1 and C2 changed bound files, so the gate ran again. `durable_evidence.py --require-full` binds every passing full record to the tree, so run 1 is not kept as a record.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/domain/download.py` | modified | `_require_text_clean` (refuses controls and lone surrogates, D-360), `ListedVideo`, `VideoListing`. CRLF kept |
| `packages/core/src/avkit_core/ports/youtube.py` | modified | `extract_video_ids -> VideoListing` |
| `packages/core/src/avkit_core/services/extract.py` | modified | The cache holds the listing |
| `packages/infrastructure/src/avkit_infra/youtube/adapter.py` | modified | `_clean_text` (drops controls and lone surrogates, D-360), `_listed_videos` with `FLAT_TABS`, `extract_video_ids`. CRLF kept |
| `packages/core/src/avkit_core/services/transcript.py` | modified | `add_channel`, `_write_volumes`, `_zip_raw`, `_fetch_item`, `_raw_markdown`, `_contents_label` |
| `packages/infrastructure/src/avkit_infra/database/engine.py` | modified | `hide_parameters=True` |
| `packages/api/src/avkit_api/routes/transcripts.py` | modified | `_aggregates`: "Last:" only from a processed item |
| `tests/unit/test_transcript_metadata.py` | new | AC-122.1 (two tests, one for lone surrogates), AC-122.6 to AC-122.14, AC-122.16, AC-122.17 |
| `tests/unit/test_services.py` | modified | `DownloadYouTube`: `titles`, `channel` and a `VideoListing` return; `ids` stays. CRLF kept |
| `tests/integration/test_youtube_adapter.py` | modified | AC-122.2 to AC-122.4, AC-122.18, the lone-surrogate tests of AC-122.2 and AC-122.8 (row C1); the amended 6.4 test. CRLF kept |
| `tests/e2e/test_api_transcripts.py` | modified | AC-122.15 |
| `docs/build-plan/01-domain-layer.md`, `02-infrastructure.md`, `03-service-layer.md`, `06-gui.md` | modified | §Spec text (row 5); row C2's "or lone surrogates" in 01 `:209`. 02, 03 and 06 CRLF kept |
| `docs/BUILD_PLAN.md`, `.agent/context/meu-status.yaml`, `meu-registry.md` | modified | MEU-122 `ready_for_review` (row 5) |
| `.agent/context/known-issues.yaml`, `known-issues.md`, `triage-output.yaml` | modified | Both issues resolved through `issue-resolve.py` (row 5) |
| `.agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md` | modified | Row 53 `executed` with the plan folder. CRLF kept |
| `.agent/context/current-focus.md` | modified | Session 53 entry (H1-3) |
| Plan folder: `baseline.ps1`, `baseline.sha`, `baseline-dirty.txt`, `measure-shapes.py`, `red-check.py`, `identity.py`, `issue-resolve.py`, `session-gate.ps1`, `human-gate-decision.md`, `task.md` | new | The plan's scripts and records |

```diff
     def add_channel(self, channel_url: str) -> TranscriptJob:
         info = self._coordinator.extract_info(url)
-        ids = self._coordinator.extract_video_ids(url)
+        listing = self._coordinator.extract_video_ids(url)
+        videos = listing.videos
         ...
         if isinstance(info, PlaylistInfo):
-            name = info.title
+            folder = info.title
         ...
+        # The folder keeps the extract title's slug (SLUG_SOURCE); the name is the channel's.
+        name = listing.channel_name or info.title
-        output_dir = root / slugify(name)
+        output_dir = root / slugify(folder)
         ...
-                video_id=video_id,
-                title=None,
+                video_id=video.video_id,
+                title=video.title,
     ...
-        slug = slugify(job.channel_name)
+        slug = job.output_dir.name
     ...
-        self._filesystem.write_text_atomic(path, _raw_markdown(job, result))
+        # The listed title wins; the result's title, the ID, is the fallback (TITLE_KEPT).
+        title = current.title or result.title
+        self._filesystem.write_text_atomic(path, _raw_markdown(job, result, title))
     ...
-        f"title: {title}\n"
-        f"channel: {job.channel_name}\n"
+        f"title: {json.dumps(title, ensure_ascii=False)}\n"
+        f"channel: {json.dumps(job.channel_name, ensure_ascii=False)}\n"
```

```diff
     chosen = max(dated, key=lambda item: item.processed_at) if dated else items[-1]
-    title = chosen.title
+    # A stored title shows under "Last:" only once that video was processed (D-352).
+    title = chosen.title if dated else None
```

The excerpts are abridged. `services/transcript.py:143-200`, `:347`, `:381`, `:609-618`, `:752-770`, `youtube/adapter.py:140-195`, `:472-484` and `routes/transcripts.py:33-36` are the source.

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
| F1 | High (blocking) | A lone surrogate in a listed title or channel passed `TEXT_CLEAN`, and SQLite and the UTF-8 raw file refused it, so `add_channel` raised and the job was not created | `youtube/adapter.py:144` and `domain/download.py:262` at round 1 | Drop lone surrogates before the listing is built, make the domain guard agree, and add a regression through the real SQLite path | fixed by rows C1 and C2 (D-360); round 2 `fixed` |

### Verdict

Round 1 of loop `s53-execution-2026-11-07-transcript-metadata` returned `changes_required`, intent achieved `yes` apart from F1, using 10,294,200 of the loop's 21,000,000 tokens ([implementation-critical-review.md](2026-11-07-transcript-metadata-implementation-critical-review.md)). It accepted every other question, graded every AC test Adequate or Strong, and reproduced the tested_state. Rows C1 to C4 fix F1 and refresh the evidence; round 2 (row C5) rechecks F1 only. Round 2 (row C5) returned `approved` with F1 `fixed`, no new finding and intent achieved `yes`, using 2,598,073 tokens (12,892,273 of 21,000,000 over both rounds). It reproduced the tested_state, checked the cleaner and the domain guard against every Unicode code point, and judged the gate rerun sound. Row C6's review state and approved-state checks passed.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| A bare channel URL in the download queue lists the tabs, not the videos | out-of-scope | — (raised to Mat at closeout) | Seen while measuring D-353: `_playlist_from_info` (`youtube/adapter.py`) reads a bare channel's top-level entries, which are its tabs (`s53-shapes.txt`: `_type {playlist: 3}`), so the download side would queue the channel's ID per tab. Downloads are outside this plan (brief: "shared with downloads", AC-122.6), and D-354's ruling covered the transcript listing only. Not filed: filing is Mat's call |
| Commit and push | out-of-scope | — | Only on Mat's explicit words (H2-5) |

**Execution notes.**
- **Row commands.** They ran through `.ps1` files written from the task cells, because the cells' `*>` needs PowerShell.
- **AC-122.16 (D-359).** A probe before the Red run showed that `HealthService` records every structlog event's name in the ring, debug included, so `_YtDlpLogger(True).debug(marker)` adds one bare `yt-dlp` event, because `message=` is not a Console field. The test asserts that the events it adds are exactly `["yt-dlp"]`, with no text, rather than an unchanged count. This was settled before the Red run; no expectation changed in Green.
- **`meu-status.yaml`.** `meu_status.py update` re-dumps the file, which re-wrapped MEU-121's note at a different column. Its value is unchanged.
- **Formatting.** `ruff format --check` flags pre-existing hunks in `youtube/adapter.py`, `test_services.py` and `test_youtube_adapter.py`, and 8 untouched package files; none is in this session's lines. Only the new test file was formatted. `ruff check` passes (gate `py-lint`).
- **H1-3 and H1-4.** They ran from Git Bash, so each cell's `*>` became `> 2>&1`, with `ELECTRON_RUN_AS_NODE` unset.

---

## Decision Log

```yaml
decision_log:
  - id: D-359
    stage: execution
    question: "AC-122.16 says _YtDlpLogger(True).debug(marker) adds nothing to the Console, but the ring records every structlog event's name, so the call adds a bare yt-dlp event. What does the test assert?"
    resolution: autonomous
    class: two-way
    chosen: "Assert the events added are exactly [\"yt-dlp\"], with no field holding the marker"
    source_tag: Local Canon
    precedents: ["packages/core/src/avkit_core/services/health.py — _process records each event's name plus CONSOLE_FIELDS only", "implementation-plan.md AC-122.16 — the intent is that no title reaches the Console"]
    research: { engine: none, sources: [] }
    reasoning: "The event name is a constant and carries no value, so the AC's intent, that no title reaches the Console, holds. Dropping debug events from the ring would change Console behaviour for every yt-dlp call, downloads included, which is outside this plan. Asserting the exact added list still fails if any text reaches a Console field."
  - id: D-360
    stage: execution
    question: "Review round 1 F1: a lone surrogate in a listed title or channel passes TEXT_CLEAN and then fails the SQLite insert and the UTF-8 file write, so add_channel raises. What does TEXT_CLEAN do with one?"
    resolution: autonomous
    class: two-way
    chosen: "_clean_text drops Unicode category Cs as it drops Cc, and _require_text_clean refuses both; a title left empty becomes None and takes the ID fallback"
    source_tag: Local Canon
    precedents: ["implementation-plan.md TEXT_CLEAN — the adapter cleans and the domain refuses what is not clean", "implementation-critical-review.md round 1 F1 — normalize to valid text or absence, make the guard consistent, add a real SQLite regression, add no requests", "task.md H1-7 — correct and re-dispatch within 6 rounds"]
    research: { engine: none, sources: [] }
    reasoning: "A lone surrogate is not text: it cannot be encoded as UTF-8, so no reader could show it. Dropping it matches how TEXT_CLEAN already treats control characters, and keeps the rest of the title. Replacing it with U+FFFD would store a character the user never saw. Leaving it keeps the job-creation failure. Format characters such as U+200B stay, as round 1 accepted. The change is two lines and is reversed by removing Cs from both sets."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-07 | claude-code-local (Claude Opus 5.5) | Initial MEU-122 handoff after H1-2 |
| Corrected | 2026-11-07 | claude-code-local (Claude Opus 5.5) | Review round 1 `changes_required` (F1, lone surrogates): rows C1 to C3, D-360, gate run 2 |
| Rechecked | 2026-11-07 | codex-independent-reviewer | Review round 2 `approved`: F1 fixed, no new finding |
