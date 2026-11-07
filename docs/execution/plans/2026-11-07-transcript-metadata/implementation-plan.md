---
project: "2026-11-07-transcript-metadata"
date: "2026-11-07"
source: ".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md#session-53--transcript-metadata-meu-122--p2"
grouping_source: ".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md"
meus: ["MEU-122"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: Transcripts carry the video's title and the channel's name (Session 53)

> **Project:** `2026-11-07-transcript-metadata`
> **Build plan:** `docs/build-plan/03-service-layer.md` §Transcript source metadata (residual) (`:663-675`, MEU-122).
>
> **Source requests,** Mat, 2026-11-07. The Session 53 brief scopes one MEU for both issues (grouping D-241). Done means "a transcript's files, compiled headings, contents and "Last:" label show the video's title; the job's channel name is the channel's, not the tab's or the playlist's title; the output folder and the compiled volume names are unchanged for an existing channel URL; no extra request per video".
> **Known issues:** `TRANSCRIPT-TITLE-IS-VIDEO-ID` (P3; triage D-223) and `TRANSCRIPT-CHANNEL-IS-PLAYLIST-NAME` (P4; D-224).
> **Status:** `draft`. `plan_to_exec_gate: human`, so nothing runs until Mat says so after the plan review.
>
> Line anchors are from `main` `9093d95`, read 2026-11-07. The only untracked path at plan time is this plan folder. Only one worktree is open (`git worktree list`: `P:/av-kit 9093d95 [main]`).
>
> **Amended 2026-11-07 after the plan gate.** Mat ruled both gate questions on 2026-11-07 ("proceed, D-353 yes, D-354 Flatten the tabs now"; briefs and rulings in `human-gate-decision.md`). D-353 yes makes row 0a `--live`, and its receipt also records the nested tab shape that D-354's ruling depends on. D-354 takes the brief's alternative: `_listed_videos` flattens a bare channel's nested tab playlists (`FLAT_TABS`, D-358, AC-122.18; AC-122.3's nested clause moves there), so no issue is filed. Row 0a runs before the recheck, so the reviewer sees the measured shapes, and the amendment goes to one recheck round of the plan review before row 0.

## Goal

**Goal anchor:** Session 53 makes a transcript's files, compiled headings, contents and "Last:" label show each video's title, stored per item from the flat enumeration `add_channel` already runs, with the video ID as the fallback only and no extra request per video. It makes the job's channel name the channel's, not the tab's or the playlist's title, falling back to today's title, and leaves the output folder and compiled volume names unchanged for an existing channel URL.

Three things are wrong today:

1. **Every transcript is titled with its video ID.** The transcript adapter reads `fetched.title`, which `FetchedTranscript` doesn't have, so its fallback to the ID always wins (`packages/infrastructure/src/avkit_infra/transcript/adapter.py:63-66`). The service stores that value at `services/transcript.py:611`. It reaches the front matter (`:754`), the compiled headings and contents (`:364-373`) and the API's `last_title` (`routes/transcripts.py:34`).
2. **The enumeration throws the titles away.** `add_channel` already runs a flat enumeration (`services/transcript.py:151`), and yt-dlp's flat entries carry `title` (`_tab.py:145-151`). But `extract_video_ids` returns IDs only (`ports/youtube.py:24`, `services/extract.py:49`, `youtube/adapter.py:418`).
3. **A channel's name is its tab's title.** `name = info.title` (`services/transcript.py:158`, `:161`) gives "Creative Commons - Videos" for a Videos tab (yt-dlp's recorded expectation, `_tab.py:1226-1240`) and the playlist's title for a playlist. The same value is the source of the folder and volume slugs (`:167`, `:343`, `:377`), so changing the name alone would move both.

The session ends when the contract's five tests and Done's four lines hold on fakes, the session gate passes, and both issues are resolved in the register. A live proof on a real channel's captions isn't part of it. Mat ruled yes on D-353, and that measurement reads listing shapes only (§User Review Required).

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls: No such file or directory, 2026-11-07). A headroom binary is on PATH but no payload here is oversized: the scope is a named list of about 15 files, read directly."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host. Validation goes through `rtk proxy`:
  - receipts go under `C:/Temp/av-kit`, named `s53-*`;
  - `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`;
  - `ELECTRON_RUN_AS_NODE` is cleared;
  - `TMP` and `TEMP` point at `C:\Temp\av-kit\s53\tmp` for the Python suite, because `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` is still open.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub` and any other worktree are left alone.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `s53-plan-2026-11-07-transcript-metadata` and `s53-execution-2026-11-07-transcript-metadata`.
  - Claude wrote the plan, so the reviewer is a different vendor.
  - Caps: plan 3 rounds, execution 6.
  - If Codex is unavailable or the ledger refuses a round, the fallback is Mat.
  - Each round is metered, and the coordinator warns before dispatching.
  - Each rolling report is validated under `C:/Temp/av-kit` and then copied byte for byte to its canonical path (Session 49b D-290).
  - Reviewer prompts name the ledger vocabulary up front, forbid opening `P:/av-kit/.mcp.json`, any `mcp-token.txt`, `~/.claude.json` and any `.env`, and, when they ask for `tested_state`, name `~/.config/git/ignore` and the path it hides (`.claude/settings.local.json`; Session 51 RULE-4).
- **Never in these rows without Mat's words:** commit, push, a YouTube request of any kind, a model, voice, runtime or Python package download, or an `approved` verdict authored by the implementer. Nothing here uploads, publishes or writes to YouTube.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-122 `svc-transcript-metadata` | `.agent/context/handoffs/2026-11-07-transcript-metadata-MEU-122-handoff.md` |

Rolling reviews: `.agent/context/handoffs/2026-11-07-transcript-metadata-plan-critical-review.md` and `.agent/context/handoffs/2026-11-07-transcript-metadata-implementation-critical-review.md`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, base suite receipts |
| WP-2 | URL shapes (row 0a, live, run before the recheck) | — | shared | `measure-shapes.py`, `s53-shapes.txt` |
| WP-3 | Listing, flattened tabs, stored titles, channel name, slug source, SQL parameters (rows 1, 2) | WP-1, WP-2 | shared | `LISTING`, `FLAT_TABS`, `STORED_TITLE`, `TITLE_KEPT`, `CHANNEL_SOURCE`, `SLUG_SOURCE`, `SQL_PARAMS_HIDDEN`; the amended 6.4 test |
| WP-4 | The API's `last_title` (rows 3, 4) | WP-3 | shared | `LAST_TITLE_PROCESSED` |
| WP-5 | Records (row 5) | WP-4 | shared | Spec notes, MEU status, register, renders, grouping tracker |
| WP-6 | Closeout (H1, H2) | WP-5 | `compact_continue` | Handoff, review, reflection, Session 54's prompt |

## User Review Required

> [!IMPORTANT]
> **Two questions have Decision Briefs in `human-gate-decision.md`.**
> - **D-353: a read-only measurement of URL shapes.** D-223 says "the plan must measure", and a live measurement is a YouTube request, so it is Mat's. Row 0a is written as the do-nothing option (`--recorded`, no network). On Mat's yes, the gate amendment replaces `--recorded` with `--live` in that row, and nothing else. No row can reach YouTube without that ruling. **Ruled yes** on 2026-11-07: row 0a is `--live`.
> - **D-354: a bare channel URL with Streams or Shorts tabs.** When more than one tab gives a result, yt-dlp's source returns nested tab playlists (`_tab.py:2416-2425`), so today's job gets one item whose "video ID" is the channel's ID. The recommendation was to file it for the next triage. **Ruled: flatten the tabs now** (2026-11-07), so `_listed_videos` lists each tab's videos (`FLAT_TABS`, D-358) and no issue is filed. A job from such a URL now holds the channel's videos, Shorts and live streams, in the order yt-dlp returns the tabs. Downloads of the same URL keep today's behaviour, because `_playlist_from_info` still lists the channel's ID (Out of Scope).
>
> **One departure from D-223's wording.** D-223 reasons that "PlaylistInfo carries only video_ids today, so it gains a field". This plan leaves `PlaylistInfo` alone and changes `extract_video_ids`'s return type instead (D-346). Only the transcript service calls `extract_video_ids`, and downloads never do, so nothing in downloads changes: not a field, not a call, not a test. The brief asks the plan to name what a new field changes there, and the answer is that there is no new field.
>
> **One raw-value fix that the brief didn't name (Session 50 RULE-1, D-357).** Titles and channel names are text from YouTube, and they become bound SQL parameters. If a database write fails, SQLAlchemy's error text holds those parameters, `log_unhandled_error` puts that text in the `error` field (`packages/api/src/avkit_api/errors.py:77-88`), and `console_field` lets it through (receipt `s53-sqlalchemy-hide-params.txt`). So row 2 adds one argument, `hide_parameters=True`, to `create_engine` in `create_sqlite_engine`. It hides every bound value from every SQL error's text, not only titles. Nothing in `packages`, `tests`, `ui/tests` or `mcp-server/tests` reads that text.
>
> **One existing path this session doesn't change, raised rather than recorded as a residual (D-356).** The folder name is a slug of the tab or playlist title, as it is today. A filesystem error on that folder can put the slug in the Console through the `error` field. `scrub_home` turns the home folder into `~`, and the slug stays. No raw title or channel name goes this way, only the slug, and Session 53 doesn't widen it. Say so if you want it handled.
>
> **What the words in Done mean here, and the limits they leave.**
> - **"Files" means front matter and headings.** Raw files stay `raw/{video_id}.md`. The ID remains the file name.
> - **Existing jobs stay as they are.** Their items hold `None` or the ID, and nothing migrates them. New jobs get titles. A job whose items hold `None` still gets the adapter's ID fallback when fetched.
> - **A single video's job takes its uploader as the channel name.** Its folder stays the slug of the video's title, as today.
> - **A curated playlist's channel name is its owner.** Each video's own channel isn't stored.
> - **Contents links are not fixed for every title.** Link anchors still come from `slugify(title)`. With real titles, that can differ from a Markdown renderer's anchor (em-dashes, "A - B"), and duplicate titles share an anchor. With IDs this rarely showed. This is out of scope, and a link that misses doesn't lose text.
> - **Flat titles can differ from a full page's.** yt-dlp issue 6006 reports this for a title with a mention that links to another channel. The source doesn't say whether it was fixed.
> - **YouTube's placeholder titles would be stored if it gives any** (for example "[Private video]"). The item then fails as it does today, under that title.
>
> **The token estimate,** calibrated against Session 42 (plan 12.8M over 2 rounds, execution 4.1M over 1), Session 51 (7.5M and 8.7M, one round each) and Session 52 (plan 22.9M over 4 rounds for three MEUs, execution 15.0M plus 4.7M). This is one MEU, smaller than Session 52: expect 1 to 2 plan rounds (about 6M to 11M) and 1 to 2 execution rounds (about 5M to 12M). The plan loop opens with the default 10.5M. Session 52's round 1 cost 11.4M and Session 51's 7.5M, so a second round could pass the budget and would need Mat's grant (Session 52 RULE-3). If round 1 costs more than 5.25M, the gate asks Mat for the execution loop's budget.

## Proposed Changes

### Single-statement contracts

| Term | Meaning |
|---|---|
| `LISTING` | `extract_video_ids` returns `VideoListing(videos: tuple[ListedVideo, ...], channel_name: str \| None)`, with `ListedVideo(video_id: str, title: str \| None)`. Both are frozen dataclasses in `domain/download.py`. |
| `TEXT_CLEAN` | A listed title or channel name is `None`, or non-empty with single spaces, no leading or trailing space and no control characters. The adapter's `_clean_text` produces it, and the domain types refuse anything else, in a message that doesn't hold the value. |
| `STORED_TITLE` | `add_channel` stores each listed title on its `TranscriptItem` when it creates the items. |
| `TITLE_KEPT` | A fetch writes `current.title or result.title` to the file and the item. The stored title wins, and the result's title, which is the ID, is the fallback only. |
| `CHANNEL_SOURCE` | `channel_name = listing.channel_name or info.title`. The adapter takes top-level `channel`, then `uploader`. |
| `SLUG_SOURCE` | The output folder stays `slugify(info.title)`. Volumes and the zip take their slug from `job.output_dir.name`, never from `channel_name`. |
| `NO_EXTRA_REQUEST` | `add_channel` calls `extract_info` once and `extract_video_ids` once, and adds no other enumeration, whatever the number of videos. |
| `QUOTED_FRONT_MATTER` | Front-matter `title` and `channel` values go through `json.dumps(value, ensure_ascii=False)`. |
| `ESCAPED_CONTENTS` | Contents link text escapes `\`, `[` and `]`. The anchor is unchanged. |
| `LAST_TITLE_PROCESSED` | The API's `last_title` comes only from an item with a `processed_at`, so a stored title never shows under "Last:" before that video has been processed. |
| `TITLES_NOT_IN_CONSOLE` | No Console field is set from a title or channel name, and yt-dlp's debug text is dropped by `_process`. |
| `SQL_PARAMS_HIDDEN` | `create_sqlite_engine` passes `hide_parameters=True`, so a SQL error's text holds no bound value. |
| `SHAPES_RECORD` | `s53-shapes.txt`: what each URL shape returns, marked `live: measured` or `live: not measured`. |
| `FLAT_TABS` | A top-level entry whose `_type` is `playlist` is a tab: it contributes its own `entries`' videos, one level deep, and never its own ID or title. Duplicates keep their first title, across tabs too. |

### Enumeration: `LISTING` (D-346, D-347)

`domain/download.py` gains, after `PlaylistInfo` (`:234-247`):

```python
@dataclass(frozen=True)
class ListedVideo:
    """One video from a flat enumeration: its ID and, when given, its title."""

    video_id: str
    title: str | None

    def __post_init__(self) -> None: ...  # video_id non-empty; title TEXT_CLEAN


@dataclass(frozen=True)
class VideoListing:
    """A flat enumeration's videos and, when given, the channel that owns them."""

    videos: tuple[ListedVideo, ...]
    channel_name: str | None

    def __post_init__(self) -> None: ...  # a tuple of ListedVideo; IDs unique; channel_name TEXT_CLEAN
```

- `ports/youtube.py:24` becomes `def extract_video_ids(self, channel_url: str) -> VideoListing: ...`.
- `services/extract.py`: `_ids_cache` holds `tuple[float, VideoListing]` (`:22`), and `extract_video_ids` (`:49-62`) returns the cached listing as is. It is immutable, so the `list(...)` copies go.
- `youtube/adapter.py` gains `_clean_text(value: object) -> str | None`: not a `str` gives `None`; non-whitespace control characters are dropped; `" ".join(value.split())`; empty gives `None`.
- `youtube/adapter.py` gains `_listed_videos(entries: object) -> tuple[ListedVideo, ...]`, deduplicated as `_unique_preserve_ids` is today (`:119-134`), first occurrence wins. An entry whose `_type` is `playlist` is a nested tab (D-354 ruling; `FLAT_TABS`, D-358): its own `entries` list gives its videos, in order, and its own ID, which is the channel's, and its title, which is a tab's, are never listed. A tab without an `entries` list, and a playlist nested inside a tab, contribute nothing. An entry of any other `_type`, `url` included, is a video, as today.
- yt-dlp applies `playlistend` at each level, so with a `playlist_end` of N each tab gives at most N videos, and `add_channel`'s slice caps the job at N in total, taken from the first tab first.
- `extract_video_ids` (`:418-428`): a playlist gives `VideoListing(_listed_videos(info.get("entries")), channel)`. A single video gives one `ListedVideo(video.video_id, _clean_text(info.get("title")))` and `channel`. `channel` is `_clean_text(info.get("channel")) or _clean_text(info.get("uploader"))`.
- `_unique_preserve_ids` stays for `_playlist_from_info`, which downloads use.

`PlaylistInfo` and `extract_info` don't change (AC-122.6). Callers of `extract_video_ids` at `9093d95`: `services/transcript.py:151` and `services/extract.py:58`, plus the port, the adapter and tests. Two fakes raise from it (`tests/unit/test_services.py:387-388`, `tests/e2e/test_api_error_surface.py:178`) and keep doing so. Pyright covers only `packages/*/src` (`pyproject.toml:36-40`), so their `-> list[str]` annotations can stay.

### What each URL shape returns (D-353)

From yt-dlp 2026.10.26's installed source (`.venv/Lib/site-packages/yt_dlp/extractor/youtube/_tab.py`; receipt `s53-ytdlp-shapes.txt`), not measured live unless Mat rules yes:

| URL shape | Top-level title | Top-level `channel` | Entries |
|---|---|---|---|
| Channel Videos tab | "Creative Commons - Videos" (`:1226-1240`) | "Creative Commons" (`:679-690`) | flat `url` entries with `id`, `title`, and `channel` when the renderer has a byline (`:76-160`, `:316-380`) |
| Playlist | The playlist's title (`:1322-1345`) | The owner (`:800-812`) | The same |
| Single video | The video's title | The uploader | None; the adapter takes the single-video path |
| Bare channel, more than one tab gives a result (Videos with Streams or Shorts) | The channel's | The channel | Nested tab playlists whose `id` is the channel's and whose `title` is a tab's, each holding its own `entries` (`:2354-2386`, `:2403-2425`); flattened by `FLAT_TABS` (D-354 ruling, D-358) |
| Bare channel, one tab gives a result | As that tab: with one result, it returns that tab directly (`:2416-2417`) | As that tab | As that tab |

**Measured live on 2026-11-07** (row 0a under D-353 yes; `C:/Temp/av-kit/s53-shapes.txt`, exit 0, 0 problems; `playlistend: 3`, no cookies, no retry). Every shape matches the table. The Videos tab and the playlist each gave three `url` entries, all with `id` and `title`, under a top-level `channel`. The Videos tab's entries carry no per-entry `channel` (0/3), which D-347 doesn't read. The bare channel gave three nested `playlist` entries, each holding its own `entries` list of three `url` entries, all with `id` and `title`, under a top-level `channel`: the shape `FLAT_TABS` reads. The single video gave a title and a channel.

Every field the code reads falls back: a missing title gives the ID, a missing channel gives today's `info.title`, and nothing raises. So a wrong shape costs what the display shows today, never a job.

### Service: `STORED_TITLE`, `CHANNEL_SOURCE`, `SLUG_SOURCE`, `TITLE_KEPT` (D-348, D-349, D-350)

`add_channel` (`services/transcript.py:142-207`):

- `listing = self._coordinator.extract_video_ids(url)`; `videos = listing.videos`; the `playlist_end` slice applies to `videos`.
- `if not videos and isinstance(info, VideoInfo): videos = (ListedVideo(info.video_id, None),)`. The adapter's single-video path always lists one video, so this fallback serves only an empty listing, as it does today.
- `folder = info.title` in both branches of `:158-162` (with `channel_id` as today), `name = listing.channel_name or info.title`.
- `output_dir = root / slugify(folder)` (`:167`); `channel_name=name` (`:172`); `video_count=len(videos)`; items take `video_id=video.video_id, title=video.title` (`:183-198`).

`_write_volumes` (`:343`) and `_zip_raw` (`:377`) use `slug = job.output_dir.name`. For every existing job, the folder was built as `root / slugify(channel_name)`, so `output_dir.name` equals today's value. For a new job, it equals the same folder slug as today. No database change, no migration. The stored path isn't changed by any setting, so an existing job's volume names can't move.

`_fetch_item`: `title = current.title or result.title` (before `:606`); `_raw_markdown(job, result, title)`; `title=title` at `:611`. `retry_failed_channel` (`:293-304`) uses `replace`, so it keeps the stored title. `transcript/adapter.py:63-66` doesn't change: `TranscriptResult.title` is required, and the ID is what `result.title` falls back to.

### Text safety: `QUOTED_FRONT_MATTER`, `ESCAPED_CONTENTS` (D-351)

A real title can hold `:` or `"`, which unquoted front matter would break, and `[` or `]`, which would break a Contents link. `_raw_markdown` (`:746-759`) writes `title` and `channel` through `json.dumps(value, ensure_ascii=False)`; `06-gui.md:722-723` already shows them quoted. A `_contents_label` helper escapes `\`, `[` and `]` in the link text at `:365`. Headings stay verbatim, because a `TEXT_CLEAN` title has no newline and so can't open a new block. `_markdown_body` (`:762-768`) splits on a line that is only `---`, so a quoted value doesn't touch it. Only this module reads the front matter.

### API: `LAST_TITLE_PROCESSED` (D-352)

`_aggregates` (`routes/transcripts.py:28-36`) falls back to `items[-1]` when nothing has been processed. Today that item's title is `None`. With `STORED_TITLE`, it would show a video nobody has processed yet under "Last:". The fix is `title = chosen.title if dated else None`. `last_item_status` and the message don't change. `TranscriptPage.tsx:128-129` shows the label only while Processing, and no UI code changes. No schema change, so OpenAPI doesn't drift. AC-16.2 still passes: its "Latest" item has a `processed_at` (`tests/e2e/api_fakes.py:127-140`).

### Where titles and channel names go (Session 50 RULE-1, D-356, D-357)

| Surface | Holds a title or channel name? | `console_field` sees it? |
|---|---|---|
| `transcript_items.title`, `transcript_jobs.channel_name` | Yes (existing columns) | No, unless a SQL error's text holds it: closed by `SQL_PARAMS_HIDDEN` |
| Raw files, compiled volumes | Yes | No |
| API JSON (`channel_name`, `last_title`), UI, MCP | Yes | No: the UI and MCP code holding these fields has no log call |
| `transcript.*` log lines (`:554`, `:574`, `:593`) | No: `job_id`, `video_id` and `error` | `error` is the failure's reason, unchanged |
| yt-dlp debug text (`_YtDlpLogger`, `adapter.py:254-279`) | Possibly, as `message=` | No: `message` isn't in `CONSOLE_FIELDS` (`health.py:47-56`), and `_process` (`:196-238`) clears everything else |
| Output folder's slug | A slug of `info.title`, unchanged | Only inside an `OSError`'s path text, as today; raised at the gate |

AC-122.16 and AC-122.17 prove the first and fifth rows with markers. `domain/errors.py` validators name the field, not the value.

### Spec text (D3)

| File | Lines | Change |
|---|---|---|
| `docs/build-plan/01-domain-layer.md` | `:207-208`, `:270`, `:433` | `ListedVideo` and `VideoListing` DTO rows; Resolve stores titles; the port returns `VideoListing` |
| `docs/build-plan/02-infrastructure.md` | `:343-345` | `extract_video_ids` returns `VideoListing`, with `_clean_text`, the top-level channel and `FLAT_TABS` |
| `docs/build-plan/03-service-layer.md` | `:210`, after `:675` | Step 4's slug comes from the extract title; a Delivered note after the residual's table, whose first line says the registered text cites the 2026-11-04 tree and what it reads at this plan's baseline |
| `docs/build-plan/06-gui.md` | `:709`, `:713-716` | The folder and volume comments name `SLUG_SOURCE` (Session 53 D-349) |

Row 5 re-reads each anchor before it writes (Session 51 RULE-3), and it cites the lines as they read after rows 1 to 4. The registered text above each table is history and isn't rewritten.

### MEU-122 `svc-transcript-metadata`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| yt-dlp flat info dict → `LISTING` | `_listed_videos`, `_clean_text` | `id` non-empty `str`; `title`, `channel`, `uploader` any type, cleaned to `TEXT_CLEAN` or `None` | Other keys ignored; a top-level `_type: playlist` entry is a tab whose own `entries` are listed and whose own ID and title never are (`FLAT_TABS`, D-358) |
| `ListedVideo`, `VideoListing` | `domain/download.py` | `video_id` non-empty and unique; `title`, `channel_name` `TEXT_CLEAN` | Frozen dataclasses; no extra fields |
| `TranscriptItem.title`, `TranscriptJob.channel_name` | `domain/transcript.py` (unchanged) | `str \| None`; non-empty `str` | Unchanged, no schema change |
| `GET /api/v1/transcripts` `last_title` | `schemas/transcripts.py:34` (unchanged) | `str \| None` | Unchanged, no schema change |

#### Acceptance Criteria

Pytest names are `test_ac_122_<n>_…`.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-122.1 | unit | `VideoListing` and `ListedVideo` exist and are frozen; empty IDs, duplicate IDs and non-`TEXT_CLEAN` text are refused, and no message holds the value; the port's `get_type_hints` return is `VideoListing` | Local Canon: triage D-223; D-346 | Yes: Red, the names are missing |
| AC-122.2 | integration | The adapter maps a Videos-tab dict and a playlist dict to their videos, titles and top-level `channel`; a title with inner newlines, double spaces and control characters comes back `TEXT_CLEAN`; a duplicate ID keeps its first title | Local Canon: triage D-223, D-224; yt-dlp source shapes | Yes: Red |
| AC-122.3 | integration | Fallbacks: a missing or non-`str` title gives `None`; a missing `channel` takes `uploader`; neither gives `None`. The nested-entry clause moved to AC-122.18 at the gate | Local Canon: 03 `:671`, `:673` | Yes: Red |
| AC-122.4 | integration | A single video gives one `ListedVideo` with its title and its `channel` | Local Canon: D-347 | Yes: Red |
| AC-122.5 | integration | The amended `test_ac_6_4_extract_video_ids_playlistend_ctor`: the IDs are `[v.video_id for v in listing.videos]`; `extract_flat` and `playlistend` assertions don't change | Local Canon: triage D-223 | Yes: Red, today a `list` |
| AC-122.6 | unit | `PlaylistInfo`'s fields are still `playlist_id`, `title`, `video_ids`, and the `extract_info` annotation is unchanged | Local Canon: brief ("shared with downloads") | Guard: passes in Red |
| AC-122.7 | unit | The coordinator caches the listing: two calls return the same object and the fake's `ids_calls` is 1 | Local Canon: 03 `:173-177` | Yes: Red |
| AC-122.8 | unit | After `add_channel`, before any fetch, items hold their listed titles. After processing, each raw file's front matter holds its title and the channel, and the compiled volume holds `# channel`, a Contents link and `## title` for each | Local Canon: 03 contract ("Tests") | Yes: Red |
| AC-122.9 | unit | A listed title of `None` gives the ID in the raw front matter, the Contents and the heading | Local Canon: 03 contract ("Tests") | Yes: Red |
| AC-122.10 | unit | A listed channel of `None` gives `channel_name == info.title`; a listed channel gives that channel, also in the front matter and the H1 | Local Canon: 03 contract ("Tests"); triage D-224 | Yes: Red |
| AC-122.11 | unit | With a channel name different from `info.title`, the folder is `my-channel`, the volume `my-channel_vol1.md` and the zip `my-channel_raw.zip`; a job built with `channel_name == info.title` gives the same names | Local Canon: triage D-224 | Yes: Red |
| AC-122.12 | unit | For a 2-video and a 50-video listing, after `add_channel` and again after processing: `extract_calls == 1`, `ids_calls == 1`, and no download ran (`last_options is None`) | Local Canon: 03 contract ("Tests"); triage D-223 | Yes: Red |
| AC-122.13 | unit | A fetch whose result's title differs keeps the stored title in the item and the file; a retried failed item keeps it too | Local Canon: 03 contract ("Stored title") | Yes: Red, today the result's title wins |
| AC-122.14 | unit | A title holding `:`, `"`, `[`, `]` and `\`: the front matter parses back to the title with `json.loads`, the Contents label is escaped, the heading is verbatim, and the body after `_markdown_body` is the transcript's | Local Canon: D-351; 06 `:722-723` | Yes: Red |
| AC-122.15 | e2e | A job whose items hold titles and no `processed_at` gives `last_title` `None`. An item with a `processed_at` gives its title | Local Canon: D-352; brief ("Last:") | Yes: Red, today the last item's title |
| AC-122.16 | unit | With a marker title and channel, including a failing item: the marker reaches the raw file. It is absent from the ring, stdout and `console.log`. A control Console line with a control marker reaches all three, so the capture works. `_YtDlpLogger(True).debug(marker)` adds nothing | Local Canon: Session 50 RULE-1; D-356 | Yes: Red, the setup needs the new names; afterwards a guard with a control |
| AC-122.17 | unit | A failed insert on a real engine from `create_sqlite_engine`: `str(exc)` doesn't hold the bound marker, and `console_field(str(exc))` doesn't either | Local Canon: Session 50 RULE-1; D-357 | Yes: Red, today it holds it |
| AC-122.18 | integration | `FLAT_TABS`: a bare-channel dict with a top-level `channel` and three nested `_type: playlist` entries, each with the channel's `id` and a tab's `title`: Videos (two videos), Shorts (a new video, a video already in Videos under another title, and a nested playlist) and Live without an `entries` list. The listing holds the Videos tab's two videos, then the Shorts tab's new one, each with its own title; the duplicate keeps its Videos title; the channel's ID, the tabs' titles and the inner playlist's ID appear nowhere; `channel_name` is the top-level `channel` | Human-approved: D-354 ruling, 2026-11-07; D-358 | Yes: Red |

Guards that run unchanged in row 2: AC-122.6, `test_ac_16_2_aggregates_without_video_ids_or_text`, `tests/integration/test_transcript_failure_delivery.py`, `tests/integration/test_transcript_block_done.py`, `tests/integration/test_sqlite_uow.py`, and every download test in `tests/unit/test_services.py`.

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Titles from the flat enumeration, stored at creation | Local Canon | 03 `:671-672`; D-223 |
| What changes in `PlaylistInfo` | Local Canon | Nothing: D-346 departs from "gains a field", stated at the gate |
| Channel name and fallback | Local Canon | 03 `:673`; D-224 |
| Slug source | Local Canon | D-224 sets the outcome; D-349 names the source |
| A processed-only `last_title` | Inferred, flagged | D-352: stored titles would otherwise mislabel "Last:" |
| Quoted front matter and escaped Contents | Inferred, flagged | D-351: 06 `:722-723` shows the quotes; real titles need them |
| URL shapes | Human-approved | D-353 ruled yes: row 0a measures live |
| A bare channel's nested tabs | Human-approved | D-354 ruled flatten (2026-11-07); D-358 names how |
| SQL error text | Local Canon | Session 50 RULE-1; D-357 |

### Files Modified

| File | Action | Summary |
|---|---|---|
| `packages/core/src/avkit_core/domain/download.py` | Modify | `ListedVideo`, `VideoListing` |
| `packages/core/src/avkit_core/ports/youtube.py` | Modify | `extract_video_ids` returns `VideoListing` |
| `packages/core/src/avkit_core/services/extract.py` | Modify | The cache holds the listing |
| `packages/core/src/avkit_core/services/transcript.py` | Modify | `STORED_TITLE`, `CHANNEL_SOURCE`, `SLUG_SOURCE`, `TITLE_KEPT`, `QUOTED_FRONT_MATTER`, `ESCAPED_CONTENTS` |
| `packages/infrastructure/src/avkit_infra/youtube/adapter.py` | Modify | `_clean_text`, `_listed_videos` with `FLAT_TABS`, `extract_video_ids` |
| `packages/infrastructure/src/avkit_infra/database/engine.py` | Modify | `SQL_PARAMS_HIDDEN` |
| `packages/api/src/avkit_api/routes/transcripts.py` | Modify | `LAST_TITLE_PROCESSED` |
| `tests/unit/test_transcript_metadata.py` | New | AC-122.1, .6 to .14, .16, .17 |
| `tests/unit/test_services.py` | Modify | `DownloadYouTube`: `titles`, `channel`, a `VideoListing` return; `ids` stays |
| `tests/integration/test_youtube_adapter.py` | Modify | AC-122.2 to .4 and .18; the amended 6.4 |
| `tests/e2e/test_api_transcripts.py` | Modify | AC-122.15 |
| `docs/build-plan/01-domain-layer.md`, `02-infrastructure.md`, `03-service-layer.md`, `06-gui.md` | Modify | §Spec text |

No test id is added, so `ui/tests/e2e/test-ids.ts` and its byte-hash tests aren't touched. `api/openapi` doesn't change. Most of these files are CRLF in the working tree (`C:/Temp/av-kit/s53-line-endings.txt`): `domain/download.py`, `youtube/adapter.py`, `test_services.py`, `test_youtube_adapter.py`, three of the four spec files and the grouping file. Each row measures the line endings with Python bytes first and writes with `newline=""`, so the endings don't change. New files in this plan folder are LF, and so is the new test file.

### Project files

- `docs/execution/plans/2026-11-07-transcript-metadata/`: `implementation-plan.md`, `task.md`, `human-gate-decision.md`, `baseline.ps1`, `baseline.sha`, `baseline-dirty.txt`, `measure-shapes.py`, `red-check.py`, `identity.py`, `issue-resolve.py`, `session-gate.ps1`.
- `.agent/context/meu-status.yaml`, `docs/BUILD_PLAN.md`, `.agent/context/meu-registry.md`, `.agent/context/known-issues.yaml` and its renders, `.agent/context/triage-output.yaml`, and the grouping tracker row (`:243`).
- `.agent/context/handoffs/2026-11-07-transcript-metadata-*.md`, `docs/execution/reflections/2026-11-07-transcript-metadata-reflection.md`, `docs/execution/metrics.md`, `.agent/context/current-focus.md`.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Each video's own channel in a curated playlist | Feature | None | D-224 names the job's channel only |
| Migrating existing jobs' titles or channel names | Feature | None | The fix is for new jobs; no request is added to backfill |
| Contents anchors matching a renderer's, and duplicate anchors | Limit | None | Stated at the gate; a link that misses doesn't lose text |
| Non-flat `extract_info` in `add_channel` | Existing cost | Issue `TRANSCRIPT-ADD-CHANNEL-422` | This session adds no request; that issue owns the 8-minute enumeration |
| Downloads of a bare channel URL with nested tabs | Existing bug | None | D-354's ruling names `_listed_videos`, which only transcripts use. `_playlist_from_info` still lists the channel's ID for downloads. Raised to Mat at the recheck, not filed without a ruling |
| A collaborative video's owner in a byline | Limit | None | The job's channel is the page's top-level channel |
| `transcript/adapter.py:63-66` | Unchanged | None | `TranscriptResult.title` stays required; the ID stays its fallback |
| 06's `date:` and `# Video Title` raw-file lines | Existing gap | None | Not in D-223 or D-224 |
| Placeholder titles for private or deleted videos | Limit | None | Stated at the gate; the item fails as it does today |
| Live proof on a real channel's captions | Runtime | MEU-125 or Mat's check from another network | `YOUTUBE-CAPTIONS-IP-BLOCK` is open |

## BUILD_PLAN.md Audit

MEU-122 is at `.agent/context/meu-status.yaml:3188`, band P2, matrix item 3.17, anchor `transcript-source-metadata-residual`. Plan time: 127 MEUs, 115 completed, 12 pending (`C:/Temp/av-kit/s53-plan-meu-stats.txt`). Row 5 sets `ready_for_review` with `tools/meu_status.py update`, and H2-2 sets `approved`. The render check runs at rows 5 and H1-3:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/s53-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s53-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` does the following:

1. Creates `C:\Temp\av-kit\s53\tmp`, and records `HEAD` in `baseline.sha` and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt`.
2. Runs `uv sync --frozen --offline --all-packages`, so this step can't fetch a package (plan-time dry run: `s53-uv-offline-dry-run.txt`, "Would make no changes"), and proves `ui/` and `mcp-server/node_modules` match their locks. `npm ci` isn't run, for Session 50's reason: the avkit MCP servers in use run from those trees. It then captures the base Python suite to `s53-base-py.txt`, the base UI suite to `s53-base-ui.txt` and the base MCP suite to `s53-base-mcp.txt`, with `TMP` and `TEMP` at `C:\Temp\av-kit\s53\tmp`.
3. Runs `red-check.py --selftest` and `identity.py --selftest`.

`baseline.ps1`, `red-check.py` and `identity.py` are copies of Session 52's, with this plan's values:

- **`baseline.ps1`.** The models snapshot, the dev check and the asset check leave it, because nothing here touches models.
- **`red-check.py`.** `DECLARED_NEW` holds `VideoListing`, `ListedVideo`, `_listed_videos` and `_clean_text`, and keeps the selftest fixtures' names.
- **`identity.py`.** `PLAN` is this folder, and `NAMED_DISTRIBUTIONS` stays empty: no Python dependency changes.
- **`PROJECT_ARTIFACTS`.** It holds this plan's `*.md`, the handoff, the review and reflection files, `docs/execution/metrics.md` and `.agent/context/current-focus.md`, which are written after the gate. The registers and renders stay bound, because row 5 writes them before H1-2.

### 2. Red then Green (rows 1 to 4)

- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py` refuses a collection error and a required test that fails on a missing name. So each test using the new types first asserts `hasattr(download_domain, "VideoListing")` and `hasattr(download_domain, "ListedVideo")` (Session 52 RULE-4). The test file's module-level imports use only names that exist today.
- **`--require` matches a test name up to a non-digit boundary (`test_ac_122_1` never matches `test_ac_122_10`), so the amended test is required by its full name,** `test_ac_6_4_extract_video_ids_playlistend_ctor`.
- **One runner summary per receipt.**
- **Guards pass in Red by design.** AC-122.6 is the only guard in row 1's selection. No Red row requires it.
- **The fake changes in row 1, so Green doesn't touch a test file.** `DownloadYouTube.extract_video_ids` (`tests/unit/test_services.py:682-691`) returns a `VideoListing` built from `ids`, `titles` and `channel`, with a lazy import. That import fails until row 2. Row 1's `-k` selects only `ac_122` and the amended 6.4, and each of those that uses the fake fails first at its `hasattr` assertion. No other suite runs between rows 1 and 2.
- **Row 2's Green re-runs the existing suites with the changed fake.**
- **AC-122.16's Red comes from its setup.** The marker never reaches the Console today either, so after Green it is a guard. Its control line proves the capture sees a Console field, and its marker in the raw file proves the marker flowed (PR-8).
- **Expectations stay immutable in Green.** The amended 6.4 changes in row 1. Its `extract_flat` and `playlistend` assertions stay.
- **Session 51 RULE-1 has no target here.** No UI test is written.
- **No real request.** Every test fakes yt-dlp (`_patch_ydl`) or the port (`DownloadYouTube`). `FakeCaptions` serves captions. Only row 0a's `measure-shapes.py --live` reaches the network, under Mat's yes to D-353 (S5).

### Plan-local scripts

- `measure-shapes.py` (row 0a), LF.
  - **`--recorded`** makes no network request. It checks that yt-dlp's installed version is `2026.10.26`, that the cited `_tab.py` strings still stand, and writes §What each URL shape returns to the receipt with `live: not measured`. It exits 0 on a match and 1 otherwise (S8).
  - **`--live`,** only on Mat's yes to D-353, runs yt-dlp flat with the adapter's `_base_opts(_YtDlpLogger(False))` plus `extract_flat` and `playlistend: 3`, with no cookies and `download=False`, on four URLs: `https://www.youtube.com/channel/UCTwECeGqMZee77BjdoYtI2Q/videos`, the same channel without `/videos`, playlist `PLav47HAVZMjnA3P7yQvneyQPiVxZ6erFS` (the transcript fixture in `docs/execution/plans/2026-10-01-mcp-live-audit/implementation-plan.md:552`) and watch `jNQXAC9IVRw`. It records which fields are present, never their values: top-level `_type`, `channel`, `uploader`, `title`; entries' `_type`, `id`, `title`, `channel`; and, for an entry whose `_type` is `playlist`, whether it holds an `entries` list, how many, and its inner entries' `_type`, `id` and `title`. A bot wall or 429 on a URL records it as `not run`, and that shape is treated as do-nothing. If a Videos tab or a playlist lacks entry titles or a top-level channel, or a single video lacks a title, it exits 1 (S8). For the bare channel, a nested tab with no `entries` list, or with inner entries lacking `id` or `title`, exits 1 (S8), because `FLAT_TABS` reads them. A bare channel that returns one tab directly records `nested: not seen live`, and AC-122.18 rests on the source shape.
- `red-check.py`, `identity.py`, `baseline.ps1`: §1.
- `issue-resolve.py` (row 5): Session 52's copy with `SCRATCH` at `C:/Temp/av-kit/s53`. `RESOLVE_KEYS` stay `status`, `verification` and `resolution_path`.
- `session-gate.ps1` (H1-2): below.

### Session gate (H1-2)

`session-gate.ps1` is Session 51's shape. It writes one receipt per step in `C:/Temp/av-kit`, named `s53-D6-<step>`. It is fail-fast, and it prints later steps as `not_run`. It sets `TMP` and `TEMP` as in §1 and clears `ELECTRON_RUN_AS_NODE`. Its last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `py-types`, `py-lint`, `ui-types`, `ui-lint`, `task-contract`, `scope-paths` (this plan's Files Modified and project files, plus `baseline-dirty.txt`; `ui/tests/e2e/test-ids.ts` refused), `red-check-selftest` |
| Fresh full | `py-tests`, `ui-tests`, `ui-build`, `openapi`, `mcp-types`, `mcp-tests`, `mcp-build`, `state-render`, `issues-render` |
| Runtime | `ui-electron`, targeted to `ui/tests/e2e/transcript-queue.test.ts` |
| Skipped with reason | `mcp-audit` (live network and YouTube), `build-record` (no installer build), the package build and its smokes (no packaged surface changes; MEU-125 runs them) |

`py-tests`, `ui-tests` and `mcp-tests` excuse only ids that row 0's receipts show failing, as Session 51 did.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | `graphify-out/` or `graphify-out-research/` appears | Re-decide the context tool |
| S2 | A Red receipt fails `red-check.py` | Fix the test setup; don't move to Green |
| S3 | `HEAD` moves from `baseline.sha`, or a path outside `baseline-dirty.txt` and this plan appears | Stop and re-baseline with Mat; never commit, stash or revert another session's work |
| S5 | Any YouTube request or any download, except row 0a's `--live` on Mat's yes to D-353 | Stop and tell Mat |
| S6 | `export_openapi.py --check` reports drift | Stop: this plan changes no schema, so find out why |
| S7 | Codex is unavailable or the ledger refuses a round | Mat is the fallback |
| S8 | `measure-shapes.py` reports a shape that contradicts §What each URL shape returns | Stop before row 1 and bring the shape to Mat; the design may change |
| S9 | A row finds it must edit `ui/tests/e2e/test-ids.ts` | Stop, add ids in an additive block at the end, and run AC-51.6 and AC-81.13 in that row's own check |
| S10 | A title or channel name reaches a Console surface in any receipt | Fix it in the row or raise it with Mat; never record it as a residual (Session 50 RULE-1) |

## Decision Log

> [!WARNING]
> Mat's brief and triage D-223 and D-224 settle the scope. D-353 and D-354 have Decision Briefs in `human-gate-decision.md`, each with a recommendation and a do-nothing option. Mat ruled both on 2026-11-07: D-353 yes, and D-354 the flatten alternative. D-358 records how the flatten works.
>
> Carried from the grouping and not relisted in the block, because the grouping's rows hold them: every §8 row, D-240 to D-250, D-267, D-277 and D-280, with stage `grouping`. Of those, D-241 makes this one MEU. The closeout check reads all of them, and D-246 stays as a withdrawn row.
>
> The triage decisions are in `.agent/context/known-issues.yaml`: D-223 under `TRANSCRIPT-TITLE-IS-VIDEO-ID` and D-224 under `TRANSCRIPT-CHANNEL-IS-PLAYLIST-NAME`. The probe (`C:/Temp/av-kit/s53-decision-issue-probe.txt`) confirms that the two flags pull in those and nothing else. H2-2 passes `--decision-issue` for both.

```yaml
decision_log:
  - id: D-346
    stage: planning
    question: "How does the enumeration carry titles and a channel name, given that PlaylistInfo is shared with downloads?"
    resolution: autonomous
    class: two-way
    chosen: "extract_video_ids keeps its name and returns a new frozen VideoListing of ListedVideo; PlaylistInfo and every download path stay as they are"
    source_tag: Local Canon
    precedents: ["packages/core/src/avkit_core/ports/youtube.py:24 — the port", "packages/core/src/avkit_core/domain/download.py:234-247 — PlaylistInfo", "known issue TRANSCRIPT-TITLE-IS-VIDEO-ID — triage D-223, 'it gains a field'"]
    research: { engine: none, sources: [] }
    reasoning: "Only the transcript service calls extract_video_ids, and extract_info's PlaylistInfo inserts download jobs, which need no titles or channel. A defaulted PlaylistInfo field, which D-223's reasoning suggests, would add an unused field to every download and leave extract_video_ids returning ids. A new method beside the old would leave a dead one. Doing nothing keeps the bug. The departure from D-223's wording is stated at the gate."
  - id: D-347
    stage: planning
    question: "Which info-dict fields does the adapter read, and how are they cleaned?"
    resolution: autonomous
    class: two-way
    chosen: "Entry title unless the entry is a nested playlist; top-level channel, then uploader; _clean_text gives single-line text or None; a single video reads its own title and channel"
    source_tag: Local Canon
    precedents: [".venv/Lib/site-packages/yt_dlp/extractor/youtube/_tab.py:76-160 — flat entries", ".venv/Lib/site-packages/yt_dlp/extractor/youtube/_tab.py:679-690 — top-level channel", "docs/build-plan/03-service-layer.md:673 — channel name"]
    research: { engine: native, sources: ["https://github.com/yt-dlp/yt-dlp/issues/6006 — a flat title can differ when it holds a mention; dropping flat makes large listings much slower", "https://www.mintlify.com/yt-dlp/yt-dlp/guides/playlists — channel tabs are separate pages"] }
    reasoning: "The page's top-level channel is the channel a job was added for. The per-entry channel can be missing or a collaborator's, so it isn't used. A nested playlist's title is a tab's, which would be the same bug one level down. Titles are stored and rendered, so a newline or control character is removed here, once."
  - id: D-348
    stage: planning
    question: "How does add_channel use the listing?"
    resolution: autonomous
    class: two-way
    chosen: "Items take the listed titles at creation; channel_name is the listed channel or info.title; playlist_end slices the videos; an empty listing with a VideoInfo gives its ID and no title"
    source_tag: Local Canon
    precedents: ["docs/build-plan/03-service-layer.md:671-673 — title and channel name", "packages/core/src/avkit_core/services/transcript.py:142-207 — add_channel"]
    research: { engine: none, sources: [] }
    reasoning: "This is the contract. The empty-listing branch exists today and the adapter's single-video path never reaches it, so it keeps its shape; using info.title there would need VideoInfo's title cleaned to TEXT_CLEAN for a branch only fakes reach."
  - id: D-349
    stage: planning
    question: "Where does the slug come from, so the folder and volumes don't move?"
    resolution: autonomous
    class: two-way
    chosen: "The folder stays slugify(info.title); _write_volumes and _zip_raw read job.output_dir.name; no column is added"
    source_tag: Local Canon
    precedents: ["known issue TRANSCRIPT-CHANNEL-IS-PLAYLIST-NAME — triage D-224, the slug stays unchanged", "packages/core/src/avkit_core/services/transcript.py:167 — the folder", "packages/core/src/avkit_core/services/transcript.py:343 — volumes", "packages/core/src/avkit_core/services/transcript.py:377 — the zip"]
    research: { engine: none, sources: [] }
    reasoning: "output_dir.name already holds the slug for every job, so an existing job's volume names can't change and no migration is needed. A folder_slug column would store the same text twice. slugify(channel_name) at those two lines, or doing nothing, would rename a new job's volumes and split a channel's output, which D-224 forbids."
  - id: D-350
    stage: planning
    question: "What does a fetch write as the title?"
    resolution: autonomous
    class: two-way
    chosen: "current.title or result.title, to the file and the item; the transcript adapter is unchanged"
    source_tag: Local Canon
    precedents: ["docs/build-plan/03-service-layer.md:672 — stored title", "packages/core/src/avkit_core/services/transcript.py:611 — title=result.title"]
    research: { engine: none, sources: [] }
    reasoning: "The result's title is the ID until the transcript library offers one, so it is the fallback. Older jobs with None titles still work through it."
  - id: D-351
    stage: planning
    question: "Real titles can hold characters that IDs never did. What changes?"
    resolution: autonomous
    class: two-way
    chosen: "Front-matter title and channel go through json.dumps(ensure_ascii=False); Contents link text escapes backslash and brackets; headings stay verbatim; anchors stay"
    source_tag: Local Canon
    precedents: ["docs/build-plan/06-gui.md:722-723 — the raw format shows both values quoted", "packages/core/src/avkit_core/services/transcript.py:746-759 — _raw_markdown", "packages/core/src/avkit_core/services/transcript.py:365 — the Contents line"]
    research: { engine: none, sources: [] }
    reasoning: "A title with a colon makes unquoted front matter invalid YAML, and a bracket breaks a link's text. A JSON string is valid YAML. Doing nothing leaves files that a YAML reader refuses, and only for videos with such titles. New files also quote an ID fallback; nothing reads the front matter back."
  - id: D-352
    stage: planning
    question: "Stored titles reach _aggregates' fallback to the last item. What does 'Last:' show before anything is processed?"
    resolution: autonomous
    class: two-way
    chosen: "last_title comes only from an item with a processed_at; otherwise None"
    source_tag: Local Canon
    precedents: ["packages/api/src/avkit_api/routes/transcripts.py:28-36 — _aggregates", "ui/src/renderer/src/features/transcript/TranscriptPage.tsx:128-129 — the label", "tests/e2e/test_api_transcripts.py:91-100 — AC-16.2"]
    research: { engine: none, sources: [] }
    reasoning: "Today the fallback's title is None, so the label is empty. With stored titles it would name the last video in the channel as if it had just run. A UI change couldn't tell the two apart. Doing nothing shows a wrong title for the first video's whole fetch."
  - id: D-353
    stage: planning
    question: "D-223 says the plan must measure which URL shapes return titles. Is a live, read-only YouTube measurement run?"
    resolution: human
    class: externally-blocked
    chosen: "Yes (Mat, 2026-11-07): row 0a runs --live once on the four URLs, field presence only, with the nested tab fields D-354's ruling reads. It was the recommendation; the do-nothing option was --recorded, no network, 'live: not measured'"
    source_tag: Human-approved
    precedents: ["known issue TRANSCRIPT-TITLE-IS-VIDEO-ID — triage D-223, the plan must measure", "known issue YOUTUBE-CAPTIONS-IP-BLOCK — 429 on api/timedtext; listing captions succeeds", ".venv/Lib/site-packages/yt_dlp/extractor/youtube/_tab.py:1226-1240 — recorded expectation"]
    research: { engine: native, sources: ["https://agentfactory.panaversity.org/docs/TypeScript-Language-Realtime-Interaction/testing-typescript-ai/integration-testing-patterns — recorded fixtures in CI, occasional live calls to check them", "https://bdfinst.github.io/ai-patterns/contract-testing-strategies — recorded fixtures as the CI default", "https://github.com/yt-dlp/yt-dlp/issues/6006 — flat titles can differ"] }
    reasoning: "The recorded shapes are yt-dlp's own test expectations, read from the installed source, and they haven't been seen on this network. The code falls back on every field, so a wrong shape costs today's display, never a job. The tests run on fakes in both cases. Brief in human-gate-decision.md."
    human_message_reference: "USER_EXPLICIT 2026-11-07 'proceed, D-353 yes, D-354 Flatten the tabs now'"
  - id: D-354
    stage: planning
    question: "A bare channel URL with Streams or Shorts tabs returns nested tab playlists, and today's job gets the channel's ID as one 'video'. What does this session do?"
    resolution: human
    class: product-preference
    chosen: "Flatten the tabs now (Mat, 2026-11-07), the brief's alternative: _listed_videos lists each nested tab's videos and never the tab's ID or title (FLAT_TABS, D-358); no issue is filed. The recommendation was to file TRANSCRIPT-CHANNEL-HOME-NESTED-TABS with no code change"
    source_tag: Human-approved
    precedents: [".venv/Lib/site-packages/yt_dlp/extractor/youtube/_tab.py:2354-2386 — extra tabs", ".venv/Lib/site-packages/yt_dlp/extractor/youtube/_tab.py:2403-2425 — nested playlist result", "packages/infrastructure/src/avkit_infra/youtube/adapter.py:119-134 — _unique_preserve_ids"]
    research: { engine: none, sources: [] }
    reasoning: "It is an existing bug in which videos a job gets, not in what they are called, and neither issue names it. Flattening here would change a job's video set, and it hasn't been measured. Doing nothing leaves it unrecorded. Brief in human-gate-decision.md. The ruling takes the alternative: a bare URL gets real videos and titles in this session, with Streams and Shorts in the job."
    human_message_reference: "USER_EXPLICIT 2026-11-07 'proceed, D-353 yes, D-354 Flatten the tabs now'"
  - id: D-355
    stage: planning
    question: "Which checks does the session gate run?"
    resolution: autonomous
    class: two-way
    chosen: "Session 51's shape, with the transcript queue E2E as the runtime stage; no package build or smokes; mcp-audit and build-record skipped with reasons"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-11-06-tts-build-capability/implementation-plan.md — Session 51 §Session gate", "docs/execution/plans/2026-11-06-tts-load-fp16/session-gate.ps1 — Session 52's gate"]
    research: { engine: none, sources: [] }
    reasoning: "No packaged surface changes, and MEU-125 builds the installer. The MCP suites are cheap and catch an API change nobody planned. mcp-audit would call YouTube."
  - id: D-356
    stage: planning
    question: "Where are titles and channel names written, and does console_field see them (Session 50 RULE-1)?"
    resolution: autonomous
    class: governance-value
    chosen: "§Where titles and channel names go; AC-122.16 proves it with markers and a control; the folder slug in an OSError's text is unchanged and raised at the gate"
    source_tag: Local Canon
    precedents: ["docs/execution/reflections/2026-11-05-transcript-failure-reason-reflection.md:137 — Session 50 RULE-1", "packages/core/src/avkit_core/services/health.py:47-56 — CONSOLE_FIELDS", "packages/core/src/avkit_core/services/health.py:196-238 — _process"]
    research: { engine: none, sources: [] }
    reasoning: "The brief asks for this statement. No new log line carries a title, and the one path a raw value could take is D-357."
  - id: D-357
    stage: planning
    question: "A failed SQL write's error text holds its bound parameters, which now include titles, and log_unhandled_error sends it to console_field. Fix it or raise it?"
    resolution: autonomous
    class: two-way
    chosen: "Fix it in row 2: hide_parameters=True on create_engine in create_sqlite_engine; AC-122.17 on a real engine; stated at the gate"
    source_tag: Local Canon
    precedents: ["docs/execution/reflections/2026-11-05-transcript-failure-reason-reflection.md:137 — Session 50 RULE-1", "packages/api/src/avkit_api/errors.py:77-88 — log_unhandled_error", "packages/infrastructure/src/avkit_infra/database/engine.py:75-85 — create_sqlite_engine"]
    research: { engine: none, sources: [] }
    reasoning: "The receipt s53-sqlalchemy-hide-params.txt shows the marker in console_field without the argument and absent with it. One argument closes the path for every bound value, and nothing reads that text. Raising it instead would only delay the same line. Doing nothing leaves YouTube's text in a pasted Console log."
  - id: D-358
    stage: planning
    question: "Mat ruled to flatten a bare channel's nested tabs now (D-354). What exactly does the adapter list?"
    resolution: autonomous
    class: two-way
    chosen: "FLAT_TABS: _listed_videos takes each top-level entry whose _type is playlist as a tab and lists that tab's own entries, one level deep, in the order yt-dlp returns the tabs; the tab's own ID and title are never listed; a tab without an entries list, and a playlist inside a tab, give nothing; duplicates keep their first title across tabs; playlist_end caps each tab in yt-dlp and the job's total in add_channel; downloads are unchanged"
    source_tag: Human-approved
    precedents: ["D-354 ruling — USER_EXPLICIT 2026-11-07 'proceed, D-353 yes, D-354 Flatten the tabs now'", ".venv/Lib/site-packages/yt_dlp/extractor/youtube/_tab.py:2403-2425 — each tab is a full playlist result, nested one level", ".venv/Lib/site-packages/yt_dlp/extractor/youtube/_tab.py:2348 — tab names may be translated", "packages/infrastructure/src/avkit_infra/youtube/adapter.py:119-134 — first occurrence wins"]
    research: { engine: none, sources: [] }
    reasoning: "The ruling says flatten; this names the rule. yt-dlp nests tabs exactly one level, and its message calls them separate playlists, so one level covers the shape and anything deeper isn't a tab. Listing the tab's own ID is today's bug, so it is dropped even when the tab holds no entries. Keeping yt-dlp's order needs no tab names, which may be translated. _playlist_from_info is left alone because the ruling named _listed_videos and downloads are outside this MEU; the same shape there is raised to Mat."
    human_message_reference: "USER_EXPLICIT 2026-11-07 'proceed, D-353 yes, D-354 Flatten the tabs now'"
```

## Research References

- `docs/build-plan/03-service-layer.md:663-675` (the residual contract).
- `.agent/context/known-issues.yaml` (`TRANSCRIPT-TITLE-IS-VIDEO-ID`, `TRANSCRIPT-CHANNEL-IS-PLAYLIST-NAME`, `TRANSCRIPT-ADD-CHANNEL-422`, `YOUTUBE-CAPTIONS-IP-BLOCK`), and the grouping file §3 `:181-183` and §6 `:243`.
- yt-dlp 2026.10.26's installed source, `.venv/Lib/site-packages/yt_dlp/extractor/youtube/_tab.py` (the anchors in §What each URL shape returns).
- Session 52's plan, task and reflection (`docs/execution/plans/2026-11-06-tts-load-fp16/`), and Session 50's reflection.

## Planning receipts

- `C:/Temp/av-kit/s53-decision-issue-probe.txt`: the decisions the closeout check reads for each issue and for the grouping.
- `C:/Temp/av-kit/s53-register-keys.txt`: Session 51 RULE-2. Both issues hold `status` and `verification` and lack `resolution_path`, so the resolve script adds that key before `category`. The register's SHA-256 was `0bcd5af73a865097f2353d1f9ad9bb51c503c6924f94629c6f6f8e0ed34285fa` at plan time; row 5 reads it again for `--expect-sha256`.
- `C:/Temp/av-kit/s53-plan-meu-stats.txt`, `C:/Temp/av-kit/s53-line-endings.txt`.
- `C:/Temp/av-kit/s53-ytdlp-shapes.txt`: read from installed source, no network.
- `C:/Temp/av-kit/s53-sqlalchemy-hide-params.txt` (SQLAlchemy 2.1.6): `hide_parameters=False` puts the marker in `str(exc)` and in `console_field`; `True` puts it in neither.
- `C:/Temp/av-kit/s53-shapes.txt` (row 0a, run at the gate under D-353 yes, before the recheck): `live: measured`, `measure-shapes: 0 problem(s)`, exit 0. `C:/Temp/av-kit/s53-shapes-recorded.txt` is the same script's `--recorded` run, also 0 problems.
- `C:/Temp/av-kit/s53-uv-offline-dry-run.txt` (Session 52 RULE-2): `uv sync --frozen --offline --all-packages --dry-run` exits 0, 122 packages, "Would make no changes". This plan relies on no other cached wheel, model or file. yt-dlp and SQLAlchemy are the locked versions.
- Plan review round 1 approved with two wording clarifications, applied without a new round, as the verdict allows: the bare-channel nesting depends on more than one tab giving a result, and row 0's sync is `--offline`.
- Step 4A GUI check (`gui-refs-not-shipped`, items 3 and 5): no control, label, layout, colour or icon changes. The "Last:" label's code is unchanged and shows different text. No test id is added, so `test-ids.ts` and its byte-hash tests aren't touched.
- Not run at plan time: any suite, build or smoke. Row 0 runs them.

## Validation stage contract

- **Static:** `pyright packages/`, `ruff`, the UI typecheck and lint, `lint_task_contract.py`, the scope-paths check and the `red-check.py` selftest.
- **Targeted:** each Red and Green row's own files, with `red-check.py` reading every Red receipt.
- **Fresh full:** the whole Python, UI and MCP suites, the UI and MCP builds, the OpenAPI guard and the two render checks, in the session gate.
- **Runtime:** the transcript queue E2E spec on the built app.
- **Identity:** `identity.py` binds `HEAD`, the work tree minus `PROJECT_ARTIFACTS`, and the runtime. The gate records it before and after, and H1-6b checks each handoff's evidence against it.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
