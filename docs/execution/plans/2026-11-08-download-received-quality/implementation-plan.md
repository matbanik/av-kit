---
project: "2026-11-08-download-received-quality"
date: "2026-11-08"
source: ".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md#session-55--download-received-quality-meu-124--p2"
grouping_source: ".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md"
meus: ["MEU-124"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: A download row shows the quality it received (Session 55)

> **Project:** `2026-11-08-download-received-quality`
> **Build plan:** `docs/build-plan/06-gui.md` §Downloader received quality (residual) (`:1582-1595`, anchor `download-received-quality-residual`, MEU-124).
>
> **Source request,** Mat's Session 55 brief, 2026-11-08. One MEU closes `DOWNLOAD-ROW-SHOWS-REQUESTED-QUALITY` (P3, triage D-225) and carries two riders: `DOWNLOAD-BARE-CHANNEL-LISTS-TABS` (P3, Mat's D-361) and `CONSOLE-STARTUP-DB-PATH` (P3, D-379). This plan's review round 1 found a third, `DOWNLOAD-PLAYLIST-ITEM-DOWNLOADS-PLAYLIST` (P2), which Mat filed into this session and whose fix he chose on 2026-11-08 (D-392). Done means "A row shows the file's quality, next to the request when they differ, and an old row shows what it shows today. An existing database gains the column without losing a row. A bare channel URL queues the channel's videos. The startup line shows no raw database path in the Console."
> **Known issues:** `DOWNLOAD-ROW-SHOWS-REQUESTED-QUALITY` (D-225), `DOWNLOAD-BARE-CHANNEL-LISTS-TABS` (D-361), `CONSOLE-STARTUP-DB-PATH` (D-377, D-379), `DOWNLOAD-PLAYLIST-ITEM-DOWNLOADS-PLAYLIST` (D-392).
> **Status:** `draft`. `plan_to_exec_gate: human`, so nothing runs until Mat says so after the plan review.
>
> Line anchors are from `main` `2963efe`, read 2026-11-08. The tree was clean and `P:/av-kit` was the only worktree when planning began (`git status --porcelain` empty, `git worktree list` one line).

## Goal

**Goal anchor:** Session 55 stores the height of the file each download actually received, in a new nullable `received_height` column that an existing database gains through `COLUMN_MIGRATIONS`. The row shows it next to the request only when they differ, and a null shows the request as today. The download add path flattens a bare channel's tabs one level, so it queues the channel's videos. The backend's `engine.created` line stops logging the database path.

The goal anchor above is the text the plan ledger registered, so it stays as written. D-392 adds a fourth fix, `VIDEO_TARGET`, which the anchor's bare-channel sentence depends on: without it the channel's videos are queued but each one downloads the channel.

Four things are wrong today:

1. **No field holds the received quality.** The row's meta line prints `row.quality` (`ui/src/renderer/src/features/downloader/DownloaderPage.tsx:497-498`), the preset stored at add (`packages/core/src/avkit_core/services/download.py:213`, `:235`). Under SABR, or when a video has no format at the asked height, the file is smaller than the row says.
2. **A bare channel URL queues tabs.** `add_to_queue` queues one item per id in `PlaylistInfo.video_ids` (`services/download.py:183-185`). `_playlist_from_info` takes those ids from the top-level entries (`packages/infrastructure/src/avkit_infra/youtube/adapter.py:257-268`), and a bare channel's top-level entries are its tabs, each a nested playlist whose `id` is the channel's (`C:/Temp/av-kit/s53-shapes.txt:24-28`; AC-122.18's shape, `tests/integration/test_youtube_adapter.py:966-1015`). Transcripts flatten them (`FLAT_TABS`, `adapter.py:158-177`); downloads don't.
3. **The first log line holds the user's profile path.** `create_sqlite_engine` logs `engine.created path=<db path>` (`packages/infrastructure/src/avkit_infra/database/engine.py:85`). `build_services` creates the engine (`packages/api/src/avkit_api/wiring.py:135`) before HealthService installs the Console processor (`:205`), so the line prints unchanged to stdout and the desktop host shows it in the Console. The plan-time probe found that line, and only that line, holding the folder (`C:/Temp/av-kit/s55-plan-startup-probe.txt`).
4. **Each video of a list downloads the whole list.** `add_to_queue` gives every item of a `PlaylistInfo` the URL that was typed (`services/download.py:186-187`), and `_run_one` hands `job.url` to `YouTubePort.download` (`:534`), which calls `extract_info(url, download=True)` (`adapter.py:497-498`). So every row of a playlist, tab or channel add asks yt-dlp for the whole list. A single-video add isn't affected. The plan review's offline probe recorded three download calls with the channel URL and none with a video URL (`.agent/context/handoffs/2026-11-08-download-received-quality-plan-critical-review.md`, F1).

The session ends when the contract's tests and Done's four lines hold, the session gate passes, and all four issues are resolved in the register.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls: No such file or directory, 2026-11-08). No payload is oversized: each layer's change is a few lines in files read directly."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host. Validation goes through `rtk proxy`:
  - receipts go under `C:/Temp/av-kit`, named `s55-*`;
  - `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`;
  - `ELECTRON_RUN_AS_NODE` is cleared;
  - `TMP` and `TEMP` point at `C:\Temp\av-kit\s55\tmp` for the Python suite, because `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` is still open.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub` and any other worktree are left alone.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `s55-plan-2026-11-08-download-received-quality` and `s55-execution-2026-11-08-download-received-quality`.
  - Claude wrote the plan, so the reviewer is a different vendor.
  - Caps: plan 3 rounds, execution 6.
  - If Codex is unavailable or the ledger refuses a round, the fallback is Mat.
  - Each round is metered, and the coordinator warns before dispatching.
  - Each rolling report is validated under `C:/Temp/av-kit` and then copied byte for byte to its canonical path (Session 49b D-290).
  - Reviewer prompts name the ledger vocabulary up front: D-381 to D-392, AC-124.1 to AC-124.16, and the mechanism ids in §Single-statement contracts. They forbid opening `P:/av-kit/.mcp.json`, any `mcp-token.txt`, `~/.claude.json`, any `.env` and `.claude/settings.local.json`. When they ask for `tested_state`, they name `~/.config/git/ignore` and the path it hides, `.claude/settings.local.json` (Session 51 RULE-4).
- **Never in these rows without Mat's words:** commit, push, a network request of any kind, a model, runtime, FFmpeg or Python package download, or an `approved` verdict authored by the implementer. Downloads are read-only from YouTube: no test or row makes a live request, and nothing uploads, publishes or writes to YouTube. Tests use fakes and the recorded shape.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-124 `download-received-quality` | `.agent/context/handoffs/2026-11-08-download-received-quality-MEU-124-handoff.md` |

Rolling reviews: `.agent/context/handoffs/2026-11-08-download-received-quality-plan-critical-review.md` and `.agent/context/handoffs/2026-11-08-download-received-quality-implementation-critical-review.md`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, base suite receipts, pre-change DDL |
| WP-2 | Type-only fields (row 1) | WP-1 | shared | The new names, with no behaviour |
| WP-3 | Red (rows 2, 3) | WP-2 | shared | Failing tests |
| WP-4 | Green (rows 4, 5) | WP-3 | shared | `RECEIVED_HEIGHT`, `STORED_ON_DONE`, `COLUMN_UPGRADE`, `WIRE_FIELD`, `SHOWN_WHEN_DIFFERENT`, `BARE_CHANNEL_FLAT`, `VIDEO_TARGET`, `STARTUP_NO_PATH` |
| WP-5 | Records (row 6) | WP-4 | shared | Spec notes, MEU status, register, renders, grouping tracker |
| WP-6 | Closeout (H1, H2) | WP-5 | `compact_continue` | Handoff, review, reflection, Session 56's prompt |

## User Review Required

> [!IMPORTANT]
> **No decision is open.** Every choice below is recorded as autonomous and two-way in §Decision Log (D-381 to D-391), with its alternatives. One more was Mat's: D-392, below. The gate asks Mat only to accept the plan, or to override one of them.
>
> **Mat's ruling on the review's F1 (D-392, 2026-11-08).** The plan review found that each row of a list add downloads the list (wrong-today item 4). The brief offered three options:
> - **Per-video URL at add (Recommended, chosen):** `add_to_queue` stores each item's watch URL (`VIDEO_TARGET`).
> - **Per-video URL at dispatch:** `_run_one` builds the watch URL from `job.video_id` for every job. This also mends rows already queued, but it ignores every URL typed, including a single video's.
> - **Do nothing:** leave the bug and drop or defer the bare-channel rider, whose rows would download the channel.
>
> Mat answered "Per-video URL at add (Recommended)". `DOWNLOAD-PLAYLIST-ITEM-DOWNLOADS-PLAYLIST` is filed under MEU-124 and closes here.
>
> **The limit it leaves.** Rows queued before the fix keep the list URL, so retrying one still downloads the list. Remove and re-add them. The card's copy action copies `item.url` for a row with no output (`ui/src/renderer/src/features/downloader/DownloaderPage.tsx:484`, `ui/src/renderer/src/components/queue/QueueCardMenu.tsx:141`). After the fix it copies the video's own URL for a new list row, and an old row copies the list URL as today.
>
> **Budgets (Mat, 2026-11-08).** Round 1 cost 9,117,395 tokens, more than the 5.25M threshold below, so Mat set both budgets. The plan loop gains 18,000,000, for 28,500,000 in total. The execution loop opens with `--token-budget 30000000`.
>
> **What the words in Done mean here, and the limits they leave.**
> - **"The file's quality" is the pixel height of the video format yt-dlp chose,** read from the info it returns after the download (D-381). The request is a height too: `bestvideo[height<=N]` (`adapter.py:102-110`). So the two compare like for like. A video that isn't 16:9 shows its real height: a 1920×800 film asked at 1080p reads `800p (asked 1080p)`, and a vertical Short asked at Best reads `1920p (asked best)`. That is what the selector measured, not YouTube's own label. Showing YouTube's label instead would need a field yt-dlp doesn't fill for a merged format.
> - **Audio-only rows store no height** (D-382), so they show the request as today. Their audio selectors can fall back to a muxed `best[height<=480]` (`AUDIO_WIRE`, `adapter.py`), and a height there would describe a picture the user didn't ask for.
> - **Only a Done row gets a value.** Old rows, and every row that never finished, stay null and show what they show today (`STORED_ON_DONE`, `COLUMN_UPGRADE`).
> - **`best` and `lowest` read as different** from any height: `1080p (asked best)`. The row then tells the user what Best turned out to be.
> - **The wire gains one field.** `DownloadJobOut.received_height` is `int | null`, so `openapi.committed.json` changes by that property. MCP passes it through unchanged (`WIRE_FIELD`, D-384).
> - **A bare channel URL now queues every video its tabs list,** deduplicated across tabs, as transcripts do. How many is still bounded by `playlist_end` (`adapter.py:465-466`). A URL that names a tab (`/videos`) is unchanged.
> - **Each row of a playlist, tab or channel add stores its own video's watch URL** (`VIDEO_TARGET`, D-392), so its download fetches that video. A single-video add stores the URL typed, as today.
> - **`engine.created` keeps its name and loses its `path` field** (D-387). Nothing reads the field: the host's ready probe reads `AVKIT_READY` (`ui/src/main/python-manager.ts:90`), and the two UI tests that quote the line quote it without a path (`ui/tests/unit/dev-spawn.test.ts:73`, `ui/tests/unit/ready-probe-guard.test.ts:34`).
>
> **The token estimate,** calibrated against Session 44's MEU-112 part (the same column pattern; execution 20.8M of 21M, with rounds 2 and 3 refused for citing ACs added after the loop opened), Session 53 (plan 8.8M over 2 rounds, execution 10.3M plus 2.6M) and Session 54 (plan 8.5M in 1 round, execution 7.9M). This session touches every layer from the domain to the renderer, plus two small riders: expect 1 to 2 plan rounds (about 8M to 12M) and 1 to 2 execution rounds (about 8M to 14M). The plan loop opened with the default 10.5M. If round 1 cost more than 5.25M, the gate would ask Mat for the execution loop's budget (Session 52 RULE-3). It did, and Mat set both budgets (above). The citable AC families were fixed when the plan loop opened, and AC-124.16 is in the AC-124 family. The execution loop opens after the gate, with AC-124.1 to AC-124.16.

## Proposed Changes

### Single-statement contracts

| Term | Meaning |
|---|---|
| `RECEIVED_HEIGHT` | `YouTubeAdapter.download` reads the top-level `height` of the info dict yt-dlp returns after the download, which is the chosen format's (yt-dlp 2026.10.26, `YoutubeDL.py:3152` `info_dict.update(best_format)`; a merge takes the video format's height). It is passed as `DownloadResult.height` when it is an `int`, not a `bool`, and greater than 0; anything else is `None`. |
| `STORED_ON_DONE` | `_run_one`'s Done save writes `received_height = None if latest.audio_only else result.height`. No other status writes it, and `add_to_queue` creates every job with `None`. |
| `COLUMN_UPGRADE` | `download_jobs.received_height` is a nullable `INTEGER`, declared last on `DownloadJobRow`, and `COLUMN_MIGRATIONS` adds it to an existing table. The mappers carry it both ways. No row is backfilled. |
| `WIRE_FIELD` | `DownloadJobOut.received_height: int \| None`, set by `_job_out` from the job. `openapi.committed.json` is regenerated. MCP and the queue hook pass it through unchanged. |
| `SHOWN_WHEN_DIFFERENT` | `downloadMetaSegments`' first segment is `row.quality` when `received_height` isn't a positive number or `` `${h}p` `` equals `row.quality`; otherwise it is `` `${h}p (asked ${row.quality})` ``. Speed and ETA follow, unchanged. |
| `BARE_CHANNEL_FLAT` | One adapter function, `_flat_entries(entries)`, returns the entries with each `_type: playlist` entry replaced by its own entries, one level deep, nested playlists dropped. `_listed_videos` (transcripts) and `_playlist_from_info` (downloads) both use it. An entry list with no playlist entry comes back unchanged. |
| `VIDEO_TARGET` | `add_to_queue`'s `PlaylistInfo` branch stores `WATCH_URL_PREFIX + video_id` as each item's URL, with `WATCH_URL_PREFIX = "https://www.youtube.com/watch?v="` a module constant in `services/download.py`. The `VideoInfo` branch stores `url.strip()` as today. `_run_one` is unchanged, so each job's download receives its stored URL. |
| `STARTUP_NO_PATH` | `create_sqlite_engine` logs `engine.created` with no field. No log line in `avkit_infra/database/` names the database path. |
| `NO_RAW_CONSOLE` | No new log line is added. `received_height` is an int and is never logged. The add path's `url` line is unchanged and, with a HealthService built, dropped from the Console (§Where values go). |

### Domain and adapter: `RECEIVED_HEIGHT` (D-381)

- **`packages/core/src/avkit_core/domain/download.py` (CRLF).** `DownloadJob` (`:116-176`) gains `received_height: int | None = None` as its last field, and `__post_init__` adds `require_optional_non_negative_int(self.received_height, "received_height")` (`domain/errors.py:161`). `DownloadResult` (`:322-337`) gains `height: int | None = None`, last, with the same check. The defaults keep every existing constructor call valid. `transition` and `reset_failed` need no change: Done is terminal, and only Done sets the value.
- **`packages/infrastructure/src/avkit_infra/youtube/adapter.py` (CRLF).** In `download` (`:486-533`), after the title check:

  ```python
  raw_height = info.get("height")
  height = (
      raw_height
      if isinstance(raw_height, int) and not isinstance(raw_height, bool) and raw_height > 0
      else None
  )
  ```

  and `DownloadResult(..., height=height)`. The `youtube.download` log line (`:532`) is unchanged.

### Service: `STORED_ON_DONE` (D-382)

`packages/core/src/avkit_core/services/download.py` (CRLF), the Done save in `_run_one` (`:559-567`): the dict gains `"received_height": None if latest.audio_only else result.height`. `add_to_queue` (`:167-253`) doesn't set it; the field defaults to `None`.

### Service: `VIDEO_TARGET` (D-392)

The same file. A module constant after the imports, `WATCH_URL_PREFIX = "https://www.youtube.com/watch?v="`, with a comment naming `VIDEO_TARGET`. Core can't import infrastructure, and `services/transcript.py:755` already builds the same URL inline. In `add_to_queue`, the `PlaylistInfo` branch (`:185-187`) becomes:

```python
elif isinstance(info, PlaylistInfo):
    for video_id in info.video_ids:
        items.append((f"{WATCH_URL_PREFIX}{video_id}", video_id, video_id))
```

The `VideoInfo` branch (`:183-184`) and `_run_one` (`:518-534`) are unchanged. Both `DownloadJob` constructions read `item_url` (`:210`, `:232`), so the SABR check and the stored job see the same URL. The ids are yt-dlp's, already filtered by `_unique_preserve_ids`. The URL is stored and returned by the API, as `url` is today, and it isn't logged.

### Database: `COLUMN_UPGRADE` (D-383)

- **`packages/infrastructure/src/avkit_infra/database/models.py` (LF).** `DownloadJobRow` (`:25-51`) gains, after `updated_at`, the same comment MEU-112 wrote at `:182`, then `received_height: Mapped[int | None] = mapped_column(Integer, nullable=True)`.
- **`migrations.py` (CRLF).** `COLUMN_MIGRATIONS` (`:102-104`) gains `("download_jobs", "received_height", "INTEGER")`. `apply_migrations` (`:115-146`) already adds a missing column and skips a present one.
- **`mappers.py` (LF).** `download_job_from_row` (`:99-119`), `download_job_to_row` (`:122-142`) and `apply_download_job` (`:145-162`) each carry `received_height`, as `gpu_preference` is carried at `:415`, `:448` and `:479`.

### API, MCP and renderer: `WIRE_FIELD`, `SHOWN_WHEN_DIFFERENT` (D-384, D-385)

- **`packages/api/src/avkit_api/schemas/downloads.py` (LF).** `DownloadJobOut` (`:45-63`) gains `received_height: int | None`, last, with no default, as `file_size` is declared.
- **`packages/api/src/avkit_api/routes/downloads.py` (CRLF).** `_job_out` (`:40-60`) passes `received_height=job.received_height`.
- **`openapi.committed.json` (CRLF)** is regenerated with `tools/export_openapi.py -o openapi.committed.json`, whose `write_text` keeps CRLF on Windows. The diff must be the one new property and its `required` entry (S6).
- **MCP:** no change. The download tool returns the API's rows, filtered by the `FORBIDDEN_KEYS` denylist in `mcp-server/src/toolsets/registry.ts`, which names no height. The MCP suite runs in the gate as a guard.
- **`ui/src/renderer/src/features/downloader/useDownloadQueue.ts` (LF).** `DownloadListItem` (`:8-20`) gains `received_height: number | null`.
- **`download-controls.ts` (CRLF).** `DownloadMetaRow` (`:146-151`) gains `received_height: number | null`. `downloadMetaSegments` (`:167-172`) becomes:

  ```ts
  export function downloadMetaSegments(row: DownloadMetaRow): string[] {
    const height = row.received_height
    const received = typeof height === 'number' && height > 0 ? `${height}p` : null
    const quality =
      received === null || received === row.quality ? row.quality : `${received} (asked ${row.quality})`
    const segments: (string | null)[] = [quality, row.speed, row.eta]
    return segments.filter(
      (segment): segment is string => segment !== null && segment.length > 0,
    )
  }
  ```

  The `typeof` test also covers a row from an older backend that has no field. Its doc comment gains one sentence naming `SHOWN_WHEN_DIFFERENT`. No export is added, and the segment count stays three (`DOWNLOAD_META_SEGMENTS`).
- **`DownloaderPage.tsx` (MIXED: 748 CRLF, 221 LF).** `metaSegmentsFor` (`:492-502`) passes `received_height: row.received_height`. The row edits by byte replacement that keeps each line's own ending, and checks both counts afterwards.

### Rider: `BARE_CHANNEL_FLAT` (D-386)

In `adapter.py`, the flatten loop in `_listed_videos` (`:165-177`) moves into a module function before it:

```python
def _flat_entries(entries: object) -> list[object]:
    """`FLAT_TABS` (D-358): each channel tab's entries in place of the tab, one level deep."""
    if not isinstance(entries, list):
        return []
    flat: list[object] = []
    for entry in entries:
        if not (isinstance(entry, dict) and entry.get("_type") == "playlist"):
            flat.append(entry)
            continue
        inner = entry.get("entries")
        if isinstance(inner, list):
            flat.extend(
                item
                for item in inner
                if not (isinstance(item, dict) and item.get("_type") == "playlist")
            )
    return flat
```

`_listed_videos` keeps its `isinstance` guard and loops over `_flat_entries(entries)`. `_playlist_from_info` (`:257-268`) becomes `video_ids=_unique_preserve_ids(_flat_entries(info.get("entries")))`. `extract_info` (`:461-470`), which the download add calls with `flat=False` (`services/download.py:177`), reaches it through `_is_playlist` (`:230-233`). With `extract_flat` off, yt-dlp still returns each resolved tab as a nested `_type: playlist` dict (`YoutubeDL.py:2078-2180`, `__process_playlist`), so the flatten applies in both modes. The transcript path's other `PlaylistInfo` reader takes only `title` and `playlist_id` (`services/transcript.py:151-162`), so it is unaffected, and AC-122.18 guards the refactor.

### Rider: `STARTUP_NO_PATH` (D-387)

`packages/infrastructure/src/avkit_infra/database/engine.py` (LF) `:85`: `log.info("engine.created", path=str(db_path))` becomes `log.info("engine.created")`.

### Where values go (Session 50 RULE-1, Session 53 RULE-1; D-388)

- **`received_height`** is an int from yt-dlp's format table. It is stored, returned by the API and MCP, and shown in the row. It is never logged.
- **A list item's stored URL (`VIDEO_TARGET`)** is the watch prefix and an id from yt-dlp. It goes where `url` already goes: the job row, the API's `url` field and the card's copy action. No log line names it: the job constructions at `:210` and `:232` don't log, and `youtube.download` logs only `video_id` and `sabr_detected`.
- **`youtube.download`** logs `video_id` and `sabr_detected` (`adapter.py:532`). Unchanged.
- **`add_to_queue_extract_start`** logs `url=` (`services/download.py:176`), and `add_to_queue_extract_done` logs `info_type=` (`:178`). Neither field is in `CONSOLE_FIELDS` (`packages/core/src/avkit_core/services/health.py:47-56`: job_id, video_id, variant_id, device, error, detail, request_id, route), so once a HealthService is built `_process` drops them before any renderer, the ring or `console.log` see them (`:233-235`). Production builds it at `wiring.py:205`, before any request can reach `add_to_queue`. This session doesn't change these lines.
- **`engine.created`** printed the raw database path to stdout before HealthService existed, and the host forwarded it to the Console (`ui/src/main/index.ts:267-274`, `ui/src/main/python-manager.ts:133-145`, `ui/src/renderer/src/hooks/useBackendLogs.ts:69-80`). After `STARTUP_NO_PATH` it holds no field. AC-124.13 proves it through `build_services`, in production's order, and reads stdout, the ring and `console.log`.
- **Session 53 RULE-1 has no target.** No new field carries outside text: `received_height` is an int, and the bare-channel ids go through the existing `_unique_preserve_ids`, unchanged. `VIDEO_TARGET` adds no field: it fills the existing `url` from the same ids that already fill `video_id`.

### Spec text (D3)

| File | Lines | Change |
|---|---|---|
| `docs/build-plan/06-gui.md` | after `:1595` | A Delivered note naming the mechanism ids (`VIDEO_TARGET` among them, with the limit that rows queued before it keep the list URL), the ACs and this plan folder |
| `docs/build-plan/02-infrastructure.md` | `:347` | One sentence: `_playlist_from_info` uses the same flatten, so the download add queues a bare channel's videos (`BARE_CHANNEL_FLAT`) |

Row 6 re-reads each anchor before it writes (Session 51 RULE-3) and cites the lines as they read after rows 1 to 5. `06-gui.md` is CRLF; `02-infrastructure.md` is measured in row 6 before it writes.

### MEU-124 `download-received-quality`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| yt-dlp info → `DownloadResult.height` | `adapter.py` `download` | positive `int`, not `bool`; else `None` | Every other key ignored |
| `DownloadJob.received_height` | `domain/download.py` | `int ≥ 0` or `None` (`require_optional_non_negative_int`) | Frozen dataclass |
| `download_jobs.received_height` | `models.py`, `migrations.py` | nullable `INTEGER`, last | Added by `COLUMN_MIGRATIONS` |
| `GET /api/v1/downloads` row | `schemas/downloads.py` `DownloadJobOut` | `received_height: int \| null` | Response model (unchanged policy) |
| MCP `avkit_download` list | `mcp-server/src/toolsets/registry.ts` (unchanged) | Passed through | `FORBIDDEN_KEYS` denylist |
| Renderer row | `useDownloadQueue.ts` `DownloadListItem` | `number \| null` | — |
| yt-dlp info → `PlaylistInfo.video_ids` | `adapter.py` `_playlist_from_info` | ids of entries after `_flat_entries` | Non-dict and id-less entries skipped (unchanged) |
| `PlaylistInfo` item → `DownloadJob.url` | `services/download.py` `add_to_queue` | `WATCH_URL_PREFIX` + the item's id; a `VideoInfo` keeps the URL typed | `DownloadJob`'s existing `url` check (unchanged) |

#### Acceptance Criteria

Pytest names are `test_ac_124_<n>_…`, and each module's own conventions hold. Vitest titles start `AC-124.<n>`. AC-124.1 goes in `tests/unit/test_domain.py`; .2 to .4 and .16 in `tests/unit/test_services.py`; .5, .6, .10 and .11 in `tests/integration/test_youtube_adapter.py`; .9 in `tests/e2e/test_api_downloads.py`; .7, .8, .12 and .13 in the new `tests/integration/test_download_received_quality.py`; .14 in `ui/tests/unit/download-controls.test.ts`; .15 in `ui/tests/unit/downloader-page.behavior.test.ts`.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-124.1 | unit | `DownloadJob` and `DownloadResult` default their new field to `None` and accept `360`. Each raises `ValidationError` for `-1` and for `True` | Local Canon: `domain/errors.py:161`; Boundary Inventory | Yes: Red, `DID NOT RAISE` after row 1 |
| AC-124.2 | unit | `STORED_ON_DONE`: a job added at `P1080` whose fake result has `height=360` ends `Done` with `received_height == 360`, read back through the unit of work | Local Canon: 06 `:1592`; triage D-225 | Yes: Red, `None` |
| AC-124.3 | unit | A fake result with `height=None` ends `Done` with `received_height is None` | Local Canon: 06 `:1592` ("for null") | Guard: passes in Red |
| AC-124.4 | unit | An audio-only job whose fake result has `height=480` ends `Done` with `received_height is None` | Local Canon: D-382 | Guard: passes in Red |
| AC-124.5 | integration | `RECEIVED_HEIGHT`: `YouTubeAdapter().download` on a patched `YoutubeDL` whose info has `height: 720` returns `DownloadResult.height == 720` | Local Canon: D-381; `YoutubeDL.py:3152` | Yes: Red, `None` |
| AC-124.6 | integration | Parametrized over `True`, `1.5`, `0`, `-1`, `"720"` and a missing key (ids `bool`, `float`, `zero`, `negative`, `string`, `missing`): `height is None`, and none raises | Local Canon: Boundary Inventory | Guard: passes in Red |
| AC-124.7 | integration | `COLUMN_UPGRADE`: a database whose `download_jobs` was created with the pre-change DDL and holds one Done row is opened with `create_sqlite_engine` and `init_schema`. The table's columns are then the fresh schema's, in its order, ending in `received_height`; the row survives with every value and reads back with `received_height is None`; a second `apply_migrations` changes nothing | Local Canon: 06 `:1593`; AC-112.5 (`tests/unit/test_ffmpeg_conversion.py:1040-1125`) | Yes: Red, no column |
| AC-124.8 | integration | A real-SQLite `DownloadService` (AC-10.14's shape, `tests/unit/test_services.py:948-975`) runs one job whose fake result has `height=360` to `Done`; a fresh unit of work reads `received_height == 360` | Local Canon: 06 `:1592` | Yes: Red, `None` |
| AC-124.9 | e2e | `WIRE_FIELD`: with AC-15.2's `_app()` (`tests/e2e/test_api_downloads.py:176-191`), two jobs, one replaced with `received_height=360`: `GET /api/v1/downloads` gives `item.get("received_height") == 360` for it and `"received_height" in item` with `None` for the other | Local Canon: D-384 | Yes: Red, the key is absent |
| AC-124.10 | integration | `BARE_CHANNEL_FLAT` on the measured shape: a top-level playlist whose three tab entries (`_type: playlist`, `id` the channel's) each hold three `url` entries, one id repeated across two tabs, plus a playlist nested in a tab. `YouTubeAdapter().extract_info(url)` returns `PlaylistInfo.video_ids` equal to the videos' ids in tab order, each once, with neither the channel id nor the nested playlist's | Human-approved: D-361; `s53-shapes.txt:24-28` | Yes: Red, the channel id |
| AC-124.11 | integration | A tab URL's shape (`/videos`: three `url` entries) gives those three ids, unchanged | Human-approved: D-361 ("a URL that names a tab is unchanged") | Guard: passes in Red |
| AC-124.12 | integration | Through the real stack: `DownloadService` on real SQLite with `ExtractCoordinator(YouTubeAdapter())`, `YoutubeDL` patched to AC-124.10's shape. `add_to_queue(<bare channel URL>, P1080, False, Default)` creates one `Pending` job per video, and no job's `video_id` is the channel id. Then through dispatch: the service's `youtube=` port is a recording fake whose `download(url, options)` appends `url` and returns a `DownloadResult` for the id after `watch?v=`. After `start_processing` and the worker's join, the recorded URLs equal `"https://www.youtube.com/watch?v=" + video_id` for the queued jobs in queue order, none is the channel URL, and every job is `Done` | Human-approved: D-361, D-392; Done ("a bare channel URL queues the channel's videos") | Yes: Red, one job for the channel id |
| AC-124.13 | integration | `STARTUP_NO_PATH`: with `HealthService._active` set to `None` (D-391), `build_services(app_data=<tmp folder whose name holds a marker>)` runs in production's order. No line of `capfd`'s stdout or stderr holds the marker, case-folded. A stdout line holds `engine.created`, the positive control. Neither the ring's messages nor `console.log`, when it exists, holds the marker | Local Canon: D-379; Session 54 RULE-2 | Yes: Red, the `engine.created` line |
| AC-124.14 | unit (UI) | `SHOWN_WHEN_DIFFERENT`: quality `1080p` with `received_height` `1080` gives `['1080p']`; with `360`, `['360p (asked 1080p)']`; with `null`, `['1080p']`; quality `best` with `1080`, `['1080p (asked best)']`. Each case keeps `speed` and `eta` after it | Local Canon: 06 `:1591`; D-385 | Yes: Red on the two different cases |
| AC-124.15 | unit (UI) | On the page, with AC-46.9's harness (`renderQueue`, `card(id)`, `ui/tests/unit/downloader-page.behavior.test.ts:560-585`, `:834-857`): a Done row at `1080p` with `received_height: 360` shows `360p (asked 1080p)` in its card meta, and a row with `null` shows `720p`, its request. The test waits one macrotask inside `act` before it reads the render (Session 51 RULE-1) | Local Canon: 06 `:1591` | Yes: Red on the first row |
| AC-124.16 | unit | `VIDEO_TARGET`: with `_download_stack`, `add_to_queue("https://youtu.be/vid1", …)` stores `https://youtu.be/vid1`. Then `youtube.playlist = PlaylistInfo(playlist_id="pl", title="P", video_ids=["a", "b"])` and `add_to_queue("https://youtube.com/pl", …)` store `https://www.youtube.com/watch?v=a` and `…=b`. After `start_processing` and the join, `DownloadYouTube.download_urls`, a list the fake's `download` appends to, equals the three jobs' stored URLs in queue order, and every job is `Done`. The test writes the watch prefix as a literal and doesn't import `WATCH_URL_PREFIX` | Human-approved: D-392 | Yes: Red, the list URL |

No existing test pins a list row's stored URL: AC-10.1 (`tests/unit/test_services.py:750-763`) checks the count and titles only.

Guards that run unchanged in rows 4 and 5: AC-122.18 (`tests/integration/test_youtube_adapter.py:966-1015`), AC-10.1 to AC-10.14, AC-6.x, AC-112.5, AC-15.x, AC-42.x (AC-42.9 counts routes and checks the OpenAPI file), `tests/integration/test_sqlite_uow.py`, `tests/integration/test_api_wiring.py`, AC-46.3 and AC-46.9. The MCP suite runs in the session gate.

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| A nullable field for the received quality | Local Canon | 06 `:1590`; triage D-225 |
| What "quality" is, and where it is measured | Inferred, flagged | D-381: the chosen format's height, because the request is a height selector |
| Audio-only stores nothing | Inferred, flagged | D-382 |
| Shown only when different; null shows the request | Local Canon | 06 `:1591`; D-225 |
| The display text `360p (asked 1080p)` | Inferred, flagged | D-385 |
| Upgrade through `COLUMN_MIGRATIONS` | Local Canon | 06 `:1592`; MEU-112 |
| Bare channel flattened, tab URL unchanged | Human-approved | D-361; 06 `:1594` |
| Each list row downloads its own video; a single-video add keeps the URL typed | Human-approved | D-392 |
| Startup line drops the field | Local Canon | D-379 offers drop or `~`; D-387 picks drop |

### Files Modified

| File | Action | Summary |
|---|---|---|
| `packages/core/src/avkit_core/domain/download.py` | Modify | `DownloadJob.received_height`, `DownloadResult.height` |
| `packages/core/src/avkit_core/services/download.py` | Modify | `STORED_ON_DONE`; `VIDEO_TARGET` and `WATCH_URL_PREFIX` |
| `packages/infrastructure/src/avkit_infra/youtube/adapter.py` | Modify | `RECEIVED_HEIGHT`, `_flat_entries`, `_playlist_from_info` |
| `packages/infrastructure/src/avkit_infra/database/models.py` | Modify | The column, last |
| `packages/infrastructure/src/avkit_infra/database/migrations.py` | Modify | `COLUMN_MIGRATIONS` entry |
| `packages/infrastructure/src/avkit_infra/database/mappers.py` | Modify | The three download mappers |
| `packages/infrastructure/src/avkit_infra/database/engine.py` | Modify | `STARTUP_NO_PATH` |
| `packages/api/src/avkit_api/schemas/downloads.py` | Modify | `DownloadJobOut.received_height` |
| `packages/api/src/avkit_api/routes/downloads.py` | Modify | `_job_out` |
| `openapi.committed.json` | Regenerate | One property |
| `ui/src/renderer/src/features/downloader/useDownloadQueue.ts` | Modify | `DownloadListItem.received_height` |
| `ui/src/renderer/src/features/downloader/download-controls.ts` | Modify | `DownloadMetaRow`, `downloadMetaSegments` |
| `ui/src/renderer/src/features/downloader/DownloaderPage.tsx` | Modify | `metaSegmentsFor` passes the field |
| `tests/unit/test_domain.py` | Modify | `SPEC_DOWNLOAD_JOB_FIELDS` (`:624`) gains the field; AC-124.1 |
| `tests/unit/test_services.py` | Modify | AC-124.2 to .4 and .16; `DownloadYouTube.download_urls` |
| `tests/integration/test_youtube_adapter.py` | Modify | AC-124.5, .6, .10, .11 |
| `tests/e2e/test_api_downloads.py` | Modify | AC-124.9 |
| `tests/integration/test_download_received_quality.py` | New | AC-124.7, .8, .12 (with its recording port), .13 |
| `ui/tests/unit/download-controls.test.ts` | Modify | The local `DownloadRow` type and `row()` (`:74-89`); AC-124.14 |
| `ui/tests/unit/downloader-page.behavior.test.ts` | Modify | `received_height: null` in the row literals (`:24`, `:38`, and the `queueItem` helpers at `:420`, `:1215`, `:1651`); AC-124.15 |
| `docs/build-plan/06-gui.md`, `docs/build-plan/02-infrastructure.md` | Modify | §Spec text |

No test id is added, so `ui/tests/e2e/test-ids.ts` and its byte-hash tests aren't touched (S9). Line endings (`C:/Temp/av-kit/s55-plan-probes.txt`): CRLF are `domain/download.py`, `services/download.py`, `adapter.py`, `migrations.py`, `routes/downloads.py`, `openapi.committed.json`, `download-controls.ts`, the five Python test files above, `download-controls.test.ts`, `06-gui.md` and the grouping file. LF are `models.py`, `mappers.py`, `engine.py`, `schemas/downloads.py`, `useDownloadQueue.ts`, the register and `meu-status.yaml`. `DownloaderPage.tsx` and `downloader-page.behavior.test.ts` are MIXED (748/221 and 2091/262 CRLF/LF), so their rows replace bytes in place, keep each line's own ending, and print both counts before and after. Every other row measures with Python bytes first and writes with `newline=""`. New files are LF.

### Project files

- `docs/execution/plans/2026-11-08-download-received-quality/`: `implementation-plan.md`, `task.md`, `baseline.ps1`, `baseline.sha`, `baseline-dirty.txt`, `pre-change-download-jobs.sql`, `red-check.py`, `identity.py`, `issue-resolve.py`, `session-gate.ps1`.
- `.agent/context/meu-status.yaml`, `docs/BUILD_PLAN.md`, `.agent/context/meu-registry.md`, `.agent/context/known-issues.yaml` and its renders, `.agent/context/triage-output.yaml`, and the grouping tracker row (`:258`). The plan review's F1 already wrote the register, its renders, `triage-output.yaml` and the grouping (§Planning receipts), so those paths are dirty when row 0 runs and `baseline-dirty.txt` records them.
- `.agent/context/handoffs/2026-11-08-download-received-quality-*.md`, `docs/execution/reflections/2026-11-08-download-received-quality-reflection.md`, `docs/execution/metrics.md`, `.agent/context/current-focus.md`.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Backfilling old rows' height from their files | Migration | None | Done: "an old row shows what it shows today" |
| Showing YouTube's own quality label | Display | None | D-381: yt-dlp fills no label for a merged format |
| A received bitrate or codec for audio-only rows | Feature | None | D-382: the issue names the video quality |
| The download add's `extract_flat=False`, which resolves each video during add | Behaviour | None | It predates this session; the rider changes only which ids are queued |
| Rewriting the URL of list rows queued before `VIDEO_TARGET` | Migration | None | D-392 chose the add-time fix; such rows are removed and re-added (§User Review Required) |
| Scrubbing every pre-HealthService line generically | Hardening | None | `engine.created` is the only one holding a path (`s55-plan-startup-probe.txt`); D-387 |
| `CONSOLE-HOME-SCRUB-SHORT-FORM` | Neighbouring issue | Its own placement | Not named in this brief |

## BUILD_PLAN.md Audit

MEU-124 is at `.agent/context/meu-status.yaml:3239`, phase 6, band P2, matrix item 6.16, anchor `download-received-quality-residual`, status `pending`. Plan time: 127 MEUs, 117 completed (116 approved, 1 closed), 10 pending (`C:/Temp/av-kit/s55-plan-meu-stats.txt`). Row 6 sets `ready_for_review` with `tools/meu_status.py update`, and H2-2 sets `approved`. The render check runs at rows 6 and H1-3:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/s55-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s55-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` does the following:

1. Creates `C:\Temp\av-kit\s55\tmp`. Records `HEAD` in `baseline.sha`, and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt` with each dirty path's SHA-256.
2. Runs `uv sync --frozen --offline --all-packages`, so this step can't fetch a package (plan-time dry run: `s55-uv-offline-dry-run.txt`, exit 0, "Would make no changes"), and proves `ui/` and `mcp-server/node_modules` match their locks. `npm ci` isn't run, for Session 50's reason. It asserts the pinned FFmpeg pair under `packaging/ffmpeg-win64/` exists and is over 1024 B, because the full Python suite runs Session 54's real-FFmpeg module; a missing pair is S4, not a fetch. It records `yt_dlp.version.__version__`, which must be `2026.10.26` (S4).
3. Writes `pre-change-download-jobs.sql`: the `sql` of `download_jobs` from `sqlite_master` in a database that `create_sqlite_engine` and `init_schema` build at `baseline.sha`, in `C:\Temp\av-kit\s55\tmp`. AC-124.7 copies it as a module constant, so its old table is the shipped one, not a hand-typed guess.
4. Captures the base Python suite to `s55-base-py.txt`, the base UI suite to `s55-base-ui.txt` and the base MCP suite to `s55-base-mcp.txt`, with `TMP` and `TEMP` at `C:\Temp\av-kit\s55\tmp`.
5. Runs `red-check.py --selftest` and `identity.py --selftest`.

`red-check.py` and `identity.py` are copies of Session 54's, with this plan's values:

- **`red-check.py`.** `DECLARED_NEW` holds `_flat_entries` and `WATCH_URL_PREFIX` and keeps the selftest fixtures' names. No test references either name: every AC goes through `extract_info`, `extract_video_ids` or the service, and AC-124.12 and .16 write the watch prefix as a literal. `received_height` and `height` exist after row 1, so no Red fails on a missing name.
- **`identity.py`.** `PLAN` is this folder, and `NAMED_DISTRIBUTIONS` stays empty: no Python dependency changes. It still binds the pinned FFmpeg pair by SHA-256, because `py-tests` runs Session 54's real-FFmpeg module. Its selftest binds this plan's `pre-change-download-jobs.sql`, the new integration module and `02-infrastructure.md` in place of Session 54's session-specific paths (`C:/Temp/av-kit/s55-plan-identity-selftest.txt`, 0 failures).
- **`PROJECT_ARTIFACTS`.** This plan's `*.md`, the handoff, the review and reflection files, `docs/execution/metrics.md` and `.agent/context/current-focus.md`, which are written after the gate. The registers and renders stay bound, because row 6 writes them before H1-2.

### 2. Type-only first, then Red, then Green (rows 1 to 5)

- **Row 1 adds the shared names with no behaviour (Session 53 RULE-2, D-389).** `DownloadJob.received_height` and `DownloadResult.height`, both defaulting to `None` with no check yet; `SPEC_DOWNLOAD_JOB_FIELDS`; the two TypeScript row types; `metaSegmentsFor` passing the field; and `received_height: null` in every test literal that `ui/tsconfig.json` type-checks. Its check proves nothing else moved: the Python suites that name these types, the UI typecheck and the two UI test files pass.
- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py` refuses a collection error and a required test that fails on a missing name. Row 2 holds the Python Reds and row 3 the UI Reds, one runner summary per receipt.
- **`--require` matches a test name up to a non-digit boundary** (`test_ac_124_1` never matches `test_ac_124_10`). A parametrized test is required case by case, by its full title.
- **Guards pass in Red by design.** AC-124.3, .4, .6 and .11 are in row 2's selection, and no Red row requires them.
- **AC-124.13 runs in production's order (D-391).** HealthService keeps class-level `_active` and installs its processor once (`health.py:132-133`, `:163-183`); `_dispatch` passes events through only when `_active is None`. A HealthService left by an earlier test in the same process would scrub the line and pass the Red falsely, so the test sets `monkeypatch.setattr(HealthService, "_active", None)` first and asserts the positive control. It reads `capfd`, so a write to the inherited descriptors is seen too, and it calls the returned dispose at the end. Its marker folder is under `tmp_path`, which pytest puts in `C:\Temp\av-kit\s55\tmp`.
- **AC-124.12 and AC-124.5's patched `YoutubeDL` returns a recorded shape.** No test reaches the network: `YoutubeDL` is replaced before the adapter is built, as `_patch_ydl` does (`tests/integration/test_youtube_adapter.py:153-207`). The new module carries its own small fake, because `_patch_ydl` is private to that test module. AC-124.12's download side never reaches yt-dlp: the service's `youtube=` port is the module's recording fake, and only the add goes through `ExtractCoordinator(YouTubeAdapter())`.
- **`VIDEO_TARGET` has two Reds.** AC-124.16 isolates it with the unit fake, so its Red fails on the stored list URL whatever the flatten does. AC-124.12 fails first on the channel id in Red, and after row 4 it proves the flatten and the per-video URL together through the real adapter and real SQLite. Row 2 adds `download_urls` to `DownloadYouTube` with AC-124.16; nothing in production changes for it.
- **Expectations stay immutable in Green.** No test file changes in rows 4 and 5.
- **Session 54 RULE-1:** rows 1 and 4 edit `packages/core/src`, so their checks run `tests/unit/test_domain.py`.

### Plan-local scripts

- `baseline.ps1`, `red-check.py`, `identity.py`: §1.
- `issue-resolve.py` (row 6): Session 54's copy with `SCRATCH` at `C:/Temp/av-kit/s55`. `RESOLVE_KEYS` stay `status`, `verification` and `resolution_path`. `DOWNLOAD-ROW-SHOWS-REQUESTED-QUALITY` lacks `resolution_path`, so the script adds it before `category`. The other three issues hold all three keys (Session 51 RULE-2; `s55-plan-probes.txt` for the two riders, `s55-plan-register-file.txt` for the issue F1 filed).
- `session-gate.ps1` (H1-2): below.

### Session gate (H1-2)

`session-gate.ps1` is Session 54's shape. It writes one receipt per step in `C:/Temp/av-kit`, named `s55-D6-<step>`. It is fail-fast, and it prints later steps as `not_run`. It sets `TMP` and `TEMP` as in §1 and clears `ELECTRON_RUN_AS_NODE`. Its last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `py-types`, `py-lint`, `ui-types`, `ui-lint`, `task-contract`, `scope-paths` (this plan's Files Modified and project files, plus `baseline-dirty.txt`; `ui/tests/e2e/test-ids.ts` refused), `red-check-selftest` |
| Fresh full | `py-tests`, `ui-tests`, `ui-build`, `openapi`, `mcp-types`, `mcp-tests`, `mcp-build`, `state-render`, `issues-render` |
| Runtime | `received-quality` (the new module on its own, so its receipt stands alone), then `ui-electron`, targeted to `ui/tests/e2e/download-queue.test.ts` |
| Skipped with reason | `mcp-audit` (live network), `build-record` (no installer build), the package build and its smokes (no packaged surface changes; MEU-125 runs them) |

`py-tests`, `ui-tests` and `mcp-tests` excuse only ids that row 0's receipts show failing. A step that fails in a file this session didn't touch is rerun once unchanged, and both attempts' receipts are kept (Session 53 RULE-4).

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | `graphify-out/` or `graphify-out-research/` appears | Re-decide the context tool |
| S2 | A Red receipt fails `red-check.py` | Fix the test setup; don't move to Green |
| S3 | `HEAD` moves from `baseline.sha`; a path outside `baseline-dirty.txt` and this plan appears; or, before rows 6 and H1-2, a `baseline-dirty.txt` path differs from its recorded SHA-256 | Stop and tell Mat; never commit, stash or revert another session's work |
| S4 | The pinned FFmpeg pair is missing or under 1024 B, or yt-dlp isn't `2026.10.26` | Stop: a fetch is a download and needs Mat's words, and D-381 rests on that version's source |
| S5 | Any network request, download or upload, or any write to YouTube | Stop and tell Mat |
| S6 | `export_openapi.py` changes anything in `openapi.committed.json` besides `received_height` | Stop and find out why |
| S7 | Codex is unavailable or the ledger refuses a round | Mat is the fallback |
| S8 | `pre-change-download-jobs.sql` holds a column the model doesn't, or the upgraded table's column order differs from a fresh one | Stop before Green; AC-124.7 would prove nothing |
| S9 | A row finds it must edit `ui/tests/e2e/test-ids.ts` | Stop, add ids in an additive block at the end, and run AC-51.6 and AC-81.13 in that row's own check |
| S10 | A path, URL or the AC-124.13 marker reaches a Console surface in any receipt | Fix it in the row or raise it with Mat; never record it as a residual (Session 50 RULE-1) |

## Decision Log

> [!WARNING]
> Mat's brief and triage D-225 settle the scope, and the riders come from Mat's D-361, from D-379 and from Mat's D-392. D-381 to D-391 didn't need Mat: each is autonomous and two-way, with its alternatives in `reasoning`. D-392 is Mat's answer to the plan review's F1, recorded here and, with the same stage and text, in the new issue's `decision_log`.
>
> Carried and not relisted in the block: every grouping §8 row, D-240 to D-250, D-267, D-277 and D-280, with stage `grouping`. Of those, D-250 keeps this MEU apart from MEU-123. The register holds D-225 (stage `triage`, under `DOWNLOAD-ROW-SHOWS-REQUESTED-QUALITY`), D-361 (stage `execution`, Session 53's closeout, under `DOWNLOAD-BARE-CHANNEL-LISTS-TABS`), and D-377 and D-379 (stage `planning`, Session 54's plan, under `CONSOLE-STARTUP-DB-PATH`). This plan cites them in prose only, so no id carries a second stage. The probe (`C:/Temp/av-kit/s55-decision-issue-probe.txt`), run with this plan as a source (Session 54 RULE-5), shows what the four `--decision-issue` flags pull in. H2-2 passes all four.

```yaml
decision_log:
  - id: D-381
    stage: planning
    question: "What is the received quality, and where is it measured?"
    resolution: autonomous
    class: two-way
    chosen: "RECEIVED_HEIGHT: the top-level height of the info yt-dlp returns from the download, which is the chosen format's; a positive int, else None; carried as DownloadResult.height"
    source_tag: Local Canon
    precedents: ["known issue DOWNLOAD-ROW-SHOWS-REQUESTED-QUALITY, triage D-225: store the file's real quality in a new nullable field", "packages/infrastructure/src/avkit_infra/youtube/adapter.py:102-110: the request is a height selector", "yt-dlp 2026.10.26 YoutubeDL.py:3152: info_dict.update(best_format)"]
    research: { engine: none, sources: [] }
    reasoning: "The request is bestvideo[height<=N], so the height of the chosen format is the same measure and compares like for like. yt-dlp already has it in memory, so it costs no probe. Probing the file with ffprobe afterwards would add an FFmpeg dependency to the download path for the same number. YouTube's quality label is not filled for a merged format. A 16:9 assumption would misreport non-16:9 videos either way; the plan states that limit at the gate."
  - id: D-382
    stage: planning
    question: "Which jobs store a value, and when?"
    resolution: autonomous
    class: two-way
    chosen: "STORED_ON_DONE: only the Done save writes it; an audio-only job stores None; add_to_queue creates every job with None"
    source_tag: Local Canon
    precedents: ["packages/core/src/avkit_core/services/download.py:559-567: the Done save", "docs/build-plan/06-gui.md:1592: existing rows stay null and show the request", "AUDIO_WIRE in adapter.py: audio selectors fall back to a muxed best[height<=480]"]
    research: { engine: none, sources: [] }
    reasoning: "Only a finished download has a file whose quality is known. An audio-only row asked for audio, and a height from the muxed fallback would describe a picture the user didn't ask for. Writing it for audio-only rows too would make the row read 480p (asked 1080p) for a file the user treats as audio."
  - id: D-383
    stage: planning
    question: "How does an existing database gain the column?"
    resolution: autonomous
    class: two-way
    chosen: "COLUMN_UPGRADE: nullable INTEGER declared last on DownloadJobRow, one COLUMN_MIGRATIONS entry, the three mappers carry it; no backfill"
    source_tag: Local Canon
    precedents: ["docs/build-plan/06-gui.md:1592: COLUMN_MIGRATIONS as MEU-112 did", "packages/infrastructure/src/avkit_infra/database/models.py:182-183: the column-order note", "tests/unit/test_ffmpeg_conversion.py:1040-1125: AC-112.5"]
    research: { engine: none, sources: [] }
    reasoning: "The contract names the mechanism. Declaring the column last keeps a fresh and an upgraded table in the same order, which AC-124.7 compares. A backfill would have to probe every old file, and Done wants old rows to show what they show today."
  - id: D-384
    stage: planning
    question: "How does the field reach the API, MCP and the renderer?"
    resolution: autonomous
    class: two-way
    chosen: "WIRE_FIELD: DownloadJobOut.received_height int or null with no default, set by _job_out; openapi.committed.json regenerated; MCP unchanged and guarded by its suite"
    source_tag: Local Canon
    precedents: ["packages/api/src/avkit_api/schemas/downloads.py:45-63: file_size is declared the same way", "mcp-server/src/toolsets/registry.ts: FORBIDDEN_KEYS names no height", "tests/e2e/test_api_downloads.py:413: AC-42.9 checks the committed OpenAPI file"]
    research: { engine: none, sources: [] }
    reasoning: "The renderer needs the raw height to compare it with the request, and every other nullable row field is declared without a default. Sending a preformatted string would fix the display in the backend and stop the renderer comparing. MCP forwards the API's rows, so an agent sees the field with no MCP change."
  - id: D-385
    stage: planning
    question: "What does the row show when the received quality differs from the request?"
    resolution: autonomous
    class: two-way
    chosen: "SHOWN_WHEN_DIFFERENT: the first meta segment reads HEIGHTp (asked REQUEST), for example 360p (asked 1080p), and is the request alone when they match or the height is null; best and lowest count as different"
    source_tag: Local Canon
    precedents: ["docs/build-plan/06-gui.md:1591: requested and received together only when they differ", "ui/src/renderer/src/features/downloader/download-controls.ts:167-172: DOWNLOAD_META_SEGMENTS", "ui/tests/unit/download-controls.test.ts:131: AC-46.3"]
    research: { engine: none, sources: [] }
    reasoning: "Keeping one segment leaves the card's three-segment layout and AC-46.3 intact. The received value comes first because it is what the file holds. A second segment would read as a separate column. For best and lowest, showing what was received is the information the user lacks today."
  - id: D-386
    stage: planning
    question: "How does the download add path flatten a bare channel's tabs?"
    resolution: autonomous
    class: two-way
    chosen: "BARE_CHANNEL_FLAT: move FLAT_TABS's loop into _flat_entries, used by _listed_videos and _playlist_from_info; a tab URL's entries pass through unchanged"
    source_tag: Human-approved
    precedents: ["known issue DOWNLOAD-BARE-CHANNEL-LISTS-TABS, Mat's D-361: apply D-354's rule to the download add path", "packages/infrastructure/src/avkit_infra/youtube/adapter.py:158-177: FLAT_TABS, D-358", "tests/integration/test_youtube_adapter.py:966-1015: AC-122.18"]
    research: { engine: none, sources: [] }
    reasoning: "One function keeps the transcript and download paths from drifting apart again, and AC-122.18 guards the move. The grouping placed the fix in services/download.py:177-186, but the ids come from the adapter, so flattening in the service would need the nested tabs in PlaylistInfo, a domain change for the same result. Doing nothing keeps the channel id as the queued item."
  - id: D-387
    stage: planning
    question: "Does engine.created drop the path field or show the home folder as ~?"
    resolution: autonomous
    class: two-way
    chosen: "STARTUP_NO_PATH: drop the field; the event keeps its name"
    source_tag: Local Canon
    precedents: ["known issue CONSOLE-STARTUP-DB-PATH, D-379: drop the field or show the home folder as ~", "packages/infrastructure/src/avkit_infra/database/engine.py:85", "ui/src/main/python-manager.ts:90: the ready probe reads AVKIT_READY, not this line", "known issue CONSOLE-HOME-SCRUB-SHORT-FORM: a home scrub misses a short-form path"]
    research: { engine: none, sources: [] }
    reasoning: "No reader uses the field, and the database location is fixed by engine.py:36-51. A ~ form would need its own home-folder rewrite before HealthService exists, and the open short-form issue shows that rewrite can miss. Dropping leaves nothing to scrub."
  - id: D-388
    stage: planning
    question: "Where are the new and nearby values written, and does console_field see them (Session 50 RULE-1)?"
    resolution: autonomous
    class: governance-value
    chosen: "Where values go: received_height is never logged; add_to_queue's url and info_type lines are dropped from the Console once HealthService is built, which production does before any request; engine.created holds no field; Session 53 RULE-1 has no target"
    source_tag: Local Canon
    precedents: ["docs/execution/reflections/2026-11-05-transcript-failure-reason-reflection.md:137: Session 50 RULE-1", "packages/core/src/avkit_core/services/health.py:47-56: CONSOLE_FIELDS", "packages/api/src/avkit_api/wiring.py:205"]
    research: { engine: none, sources: [] }
    reasoning: "The brief asks for this statement. The only raw values near this code are the add path's URL, already dropped by the Console processor, and the startup path, which STARTUP_NO_PATH removes."
  - id: D-389
    stage: planning
    question: "In what order do the rows add the shared names?"
    resolution: autonomous
    class: two-way
    chosen: "Row 1 adds received_height and DownloadResult.height with None defaults and no checks, the TypeScript row types, the page's pass-through and the test literals; rows 2 and 3 then fail by assertion"
    source_tag: Local Canon
    precedents: ["Session 53 RULE-2: a shared missing name gets a type-only row first", "Session 52 RULE-4", "docs/execution/plans/2026-11-07-convert-extract-index/red-check.py: a missing name is a setup failure"]
    research: { engine: none, sources: [] }
    reasoning: "Without row 1 the Reds would fail on a missing attribute or a type error, which red-check refuses, and ui/tsconfig.json type-checks the test literals. The defaults keep every caller valid, so row 1 changes no behaviour."
  - id: D-390
    stage: planning
    question: "Which checks does the session gate run?"
    resolution: autonomous
    class: two-way
    chosen: "Session 54's shape without ci-collect and extract-real-ffmpeg; the runtime stage is the new module on its own, then the download queue E2E; no package build or smokes; mcp-audit and build-record skipped with reasons"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-11-07-convert-extract-index/implementation-plan.md:329-341: Session 54 session gate"]
    research: { engine: none, sources: [] }
    reasoning: "The new module holds the real-SQLite, real-adapter and startup proofs. The download queue E2E runs the built app's renderer against the changed wire. No packaged surface changes, and MEU-125 builds the installer."
  - id: D-391
    stage: planning
    question: "How does the startup test avoid passing falsely because of an earlier test's HealthService?"
    resolution: autonomous
    class: governance-value
    chosen: "AC-124.13 sets HealthService._active to None with monkeypatch before build_services, reads capfd, asserts an engine.created stdout line as the positive control, and checks the ring and console.log"
    source_tag: Local Canon
    precedents: ["packages/core/src/avkit_core/services/health.py:132-133, :163-183: class-level _active and a processor installed once", "Session 54 RULE-2", "C:/Temp/av-kit/s55-plan-startup-probe.txt"]
    research: { engine: none, sources: [] }
    reasoning: "Session 54 RULE-2 builds HealthService first, but this test proves production's order, where the engine logs before HealthService exists. Without the reset, a HealthService left from an earlier test would scrub the line in the full suite and hide the defect, and the positive control shows the line was seen."
  - id: D-392
    stage: planning
    question: "Session 55's plan review found that each playlist item's row downloads the list's URL, so the bare-channel rider would queue rows that fail. How should the plan fix it?"
    resolution: human
    class: product-preference
    chosen: "Per-video URL at add: add_to_queue stores the watch URL of each playlist item's id, a single-video add keeps the URL typed, AC-124.12 is extended through dispatch with a fake that records each download URL, and this issue is opened and closed in MEU-124"
    source_tag: Human-approved
    precedents: [".agent/context/handoffs/2026-11-08-download-received-quality-plan-critical-review.md — F1", "packages/core/src/avkit_core/services/download.py:186-187,534 — the stored URL and the download call", "packages/core/src/avkit_core/services/transcript.py:755 — transcripts already build the watch URL from the id", "docs/execution/plans/2026-11-08-download-received-quality/implementation-plan.md — the brief and the options"]
    research: { engine: none, sources: [] }
    reasoning: "The add path already holds each item's id, and transcripts build the watch URL the same way. Fixing at add leaves a single-video add's URL and the dispatch code unchanged; fixing at dispatch would also mend rows already queued but would ignore every URL typed. Doing nothing would ship a rider whose rows fail. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-08 'Per-video URL at add (Recommended)' (answer to the F1 brief; options in implementation-plan.md §User Review Required)"
```

## Research References

- `docs/build-plan/06-gui.md:1582-1595` (the residual contract), `docs/build-plan/02-infrastructure.md:347` (`FLAT_TABS`).
- `.agent/context/known-issues.yaml` (the four issues), the grouping file §1 `:27`, §2 `:52`, §3 `:198-203`, §6 `:258` and §8 `:289`, `:303`.
- The plan review, round 1: `.agent/context/handoffs/2026-11-08-download-received-quality-plan-critical-review.md` (F1).
- yt-dlp 2026.10.26 source: `YoutubeDL.py:2078-2180` (nested playlists) and `:2833`, `:3152` (the chosen format's fields).
- Session 54's plan, task and scripts (`docs/execution/plans/2026-11-07-convert-extract-index/`), Session 44's MEU-112 work (AC-112.5), and Session 50's reflection.

## Planning receipts

- `C:/Temp/av-kit/s55-plan-probes.txt`: line endings of every target file, the register's SHA-256 (`d86be1bf…`, 380,921 B) and the three issues' keys (Session 51 RULE-2). F1's filing has changed the register since then (below), so row 6 reads the SHA-256 again for `--expect-sha256`. The fourth issue holds `status`, `verification` and `resolution_path`.
- `C:/Temp/av-kit/s55-plan-startup-probe.txt`: `build_services` into a marker-named folder printed 4 stdout lines, of which only `engine.created` held the marker.
- `C:/Temp/av-kit/s55-decision-issue-probe.txt`: the four flags, with this plan as a source, pull in D-225, D-361, D-377, D-379, D-392 and the grouping rows.
- Plan review round 1, after F1:
  - `C:/Temp/av-kit/s55-plan-review-validate.txt`: the report validated, `changes_required`, 1 open finding. It was copied byte for byte to the canonical path. `s55-plan-review-state.json` and `s55-plan-review-state-canonical.json` hold the review-state receipts.
  - `C:/Temp/av-kit/s55-plan-register-file.txt`: `DOWNLOAD-PLAYLIST-ITEM-DOWNLOADS-PLAYLIST` filed through `model.add_issue` and `model.save`, with 40 lines added, 0 removed and 122 issues. The pre-edit copy is `C:/Temp/av-kit/s55/s55-ki-before-f1.yaml`.
  - `C:/Temp/av-kit/s55-plan-register-cites.txt`: the register's grouping cites moved to the grouping's new lines.
  - `C:/Temp/av-kit/s55-plan-grouping-f1.txt`: four inserts in the grouping file, which stays CRLF with 0 bare LF.
  - `C:/Temp/av-kit/s55-plan-issues-render.txt`: `issue_triage.py render` and `render --check` pass.
  - `C:/Temp/av-kit/s55-plan-triage-regen.txt`: `triage-output.yaml` regenerated. Its only diff is the new issue and the moved cites.
  - `C:/Temp/av-kit/s55-plan-cite-fix.txt`: `download.py:186` corrected to `:186-187` in the register and grouping text.
  - The ledger's `continue` for the +18M was recorded with `--at 2026-11-08T02:00:00-08:00`. The real time was about 2026-11-08T08:09-05:00 (05:09 Pacific). The slip is in the timestamp only, and the ruling and its amount are as Mat gave them.
- `C:/Temp/av-kit/s55-plan-meu-stats.txt`.
- `C:/Temp/av-kit/s55-uv-offline-dry-run.txt` (Session 52 RULE-2): `uv sync --frozen --offline --all-packages --dry-run` exits 0, 122 packages, "Would make no changes". This plan relies on no cached wheel, model or file except the pinned FFmpeg pair, already on disk.
- `C:/Temp/av-kit/s55-plan-task-lint.txt`: `lint_task_contract.py` on `task.md`.
- Step 4A GUI check (`gui-refs-not-shipped`, items 3 and 5): the only visible change is the first meta segment's text on a Done row whose height differs from the request. No control, layout, colour or icon changes.
- Not run at plan time: any suite, build or smoke. Row 0 runs them.

## Validation stage contract

- **Static:** `pyright packages/`, `ruff`, the UI typecheck and lint, `lint_task_contract.py`, the scope-paths check and the `red-check.py` selftest.
- **Targeted:** each row's own files, with `red-check.py` reading every Red receipt.
- **Fresh full:** the whole Python, UI and MCP suites, the UI and MCP builds, the OpenAPI guard and the two render checks, in the session gate.
- **Runtime:** the new integration module on its own, and the download queue E2E spec on the built app.
- **Identity:** `identity.py` binds `HEAD`, the work tree minus `PROJECT_ARTIFACTS`, and the runtime. The gate records it before and after, and H1-6b checks the handoff's evidence against it.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
