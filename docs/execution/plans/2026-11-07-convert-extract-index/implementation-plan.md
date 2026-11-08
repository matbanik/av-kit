---
project: "2026-11-07-convert-extract-index"
date: "2026-11-07"
source: ".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md#session-54--convert-extract-index-meu-123--p2"
grouping_source: ".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md"
meus: ["MEU-123"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: Extract counts audio tracks the way FFmpeg does (Session 54)

> **Project:** `2026-11-07-convert-extract-index`
> **Build plan:** `docs/build-plan/08-video-conversion.md` §Extract stream index (residual) (`:593-605`, MEU-123).
>
> **Source requests,** Mat, 2026-11-07. The Session 54 brief scopes one MEU that closes `CONVERT-EXTRACT-STREAM-INDEX-MISMATCH` and carries the rider `CONVERT-EXTRACT-ENCODER-LABEL` (grouping D-242). Done means "First audio stream writes `.m4a` for AAC. All audio streams extracts every track, the first included, and no job asks for a track that doesn't exist. `stream_index` has one meaning in the API, MCP, GUI, service and adapter. An Extract job shows no encoder".
> **Known issues:** `CONVERT-EXTRACT-STREAM-INDEX-MISMATCH` (P3; triage D-227) and `CONVERT-EXTRACT-ENCODER-LABEL` (P4; grouping D-242).
> **Status:** `draft`. `plan_to_exec_gate: human`, so nothing runs until Mat says so after the plan review.
> **Plan review:** round 1 approved with no blocking finding, for 8,541,302 tokens (`.agent/context/handoffs/2026-11-07-convert-extract-index-plan-critical-review.md`). Its one finding, F1, is folded in as AC-123.13 (D-376). Answering it turned up D-377.
> **Mat's rulings, 2026-11-07:** "All recommendations accepted. But also file, and assign into session groupings So next sessions, can handle the new issues." That settles D-373, D-377 and D-378 at their recommendations. The two new issues were filed at plan time and placed by D-379 and D-380. Execution still waits for Mat's explicit go-ahead.
>
> Line anchors are from `main` `39ac742`, read 2026-11-07. At plan time the tree holds nine uncommitted files from another session, which filed and placed Session 53's three new issues (D-361 to D-363): `current-focus.md`, the grouping file, `known-issues.md`, `known-issues.yaml`, `meu-status.yaml`, `docs/build-plan/06-gui.md`, `docs/execution/metrics.md`, and Session 53's `closeout-decisions.md` and reflection (last written 18:42). Mat ruled that planning continues on top of them and that Session 54's commit carries them (D-375). The only untracked path is this plan folder. Six of those nine paths now also hold this plan's filing and placement of its two new issues (D-379, D-380): the register and its render, the grouping file, `06-gui.md`, `current-focus.md` and `meu-status.yaml`. Row 0's `baseline-dirty.txt` records them as they stand, so a diff from the baseline doesn't show those edits, and H1-7's review prompt names them.

## Goal

**Goal anchor:** Session 54 gives `stream_index` one meaning, the Nth audio stream in ffprobe order, which is the N that FFmpeg's `-map a:N` selects. The service then picks an Extract's extension from that audio stream, plans All audio streams as positions 0 to k-1, and creates no job that asks for a track the file doesn't have. An Extract job saves no encoder. Proof is a real `.mp4` with one audio track and with two, through the real FFmpeg adapter.

Two things are wrong today:

1. **The service and the adapter count streams differently.** The adapter passes `-map a:{stream_index}` (`packages/infrastructure/src/avkit_infra/media/adapter.py:634-635`), which counts audio streams only. The service reads the same number as ffprobe's index across all streams: `_output_ext` compares it with `StreamInfo.index` (`packages/core/src/avkit_core/services/conversion.py:384-388`), and the All audio streams plan sends `stream.index` (`:328`). On a normal video the picture is stream 0, so:
   - First audio stream looks up the picture's codec, misses the container map and writes `.mka` (`:390-391`);
   - All audio streams on a one-track video plans `a:1`, and FFmpeg fails ("Error opening output files: Invalid argument", measured in `C:/Temp/av-kit/s54-plan-ffmpeg-fixture-probe.txt`);
   - on a two-track video it plans `a:1` and `a:2`, so the first track is never extracted and the second job fails.
   The tests missed it because every fixture lists audio first (`tests/unit/test_conversion_service.py:570-651`).
2. **An Extract job is labelled with a video encoder.** `_dispatch` resolves an encoder and saves it for every kind (`:487-495`), although an Extract is a stream copy (`-c:a copy`, `adapter.py:632-633`).

The session ends when the contract's tests and Done's four lines hold through the real FFmpeg binary, the session gate passes, and both issues are resolved in the register.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls: No such file or directory, 2026-11-07). No payload here is oversized: the scope is one service file, two test files, the CI workflow and one spec file, read directly."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host. Validation goes through `rtk proxy`:
  - receipts go under `C:/Temp/av-kit`, named `s54-*`;
  - `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`;
  - `ELECTRON_RUN_AS_NODE` is cleared;
  - `TMP` and `TEMP` point at `C:\Temp\av-kit\s54\tmp` for the Python suite, because `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` is still open.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub` and any other worktree are left alone.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `s54-plan-2026-11-07-convert-extract-index` and `s54-execution-2026-11-07-convert-extract-index`.
  - Claude wrote the plan, so the reviewer is a different vendor.
  - Caps: plan 3 rounds, execution 6.
  - If Codex is unavailable or the ledger refuses a round, the fallback is Mat.
  - Each round is metered, and the coordinator warns before dispatching.
  - Each rolling report is validated under `C:/Temp/av-kit` and then copied byte for byte to its canonical path (Session 49b D-290).
  - Reviewer prompts name the ledger vocabulary up front, forbid opening `P:/av-kit/.mcp.json`, any `mcp-token.txt`, `~/.claude.json`, any `.env` and `.claude/settings.local.json`, and, when they ask for `tested_state`, name `~/.config/git/ignore` and the path it hides (`.claude/settings.local.json`; Session 51 RULE-4).
- **Never in these rows without Mat's words:** commit, push, a network request of any kind, a model, runtime, FFmpeg or Python package download, or an `approved` verdict authored by the implementer. Convert is local files only: nothing here uploads, publishes or writes to YouTube.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-123 `convert-extract-stream-index` | `.agent/context/handoffs/2026-11-07-convert-extract-index-MEU-123-handoff.md` |

Rolling reviews: `.agent/context/handoffs/2026-11-07-convert-extract-index-plan-critical-review.md` and `.agent/context/handoffs/2026-11-07-convert-extract-index-implementation-critical-review.md`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, base suite receipts |
| WP-2 | Audio positions, plans, extension, missing tracks, no encoder (rows 1, 2) | WP-1 | shared | `AUDIO_POSITION`, `AUDIO_PLAN`, `EXTRACT_EXT`, `MISSING_TRACK`, `EXTRACT_NO_ENCODER`; the real-FFmpeg module |
| WP-3 | CI keeps running without the fetched binaries (row 3) | WP-2 | shared | `CI_DESELECT` |
| WP-4 | Records (row 4) | WP-3 | shared | Spec notes, MEU status, register, renders, grouping tracker |
| WP-5 | Closeout (H1, H2) | WP-4 | `compact_continue` | Handoff, review, reflection, Session 55's prompt |

## User Review Required

> [!IMPORTANT]
> **Three questions had Decision Briefs in `human-gate-decision.md`, and Mat ruled all three on 2026-11-07:** "All recommendations accepted. But also file, and assign into session groupings So next sessions, can handle the new issues."
> - **D-373: a Cut job saves an encoder it never uses.** `_dispatch` saves the resolved encoder for Cut too (`conversion.py:487-495`), but Cut's re-encode is fixed at `libx265` (`adapter.py:592-604`) and Fast Copy is `-c copy` (`:590-591`). On an NVIDIA machine with the GPU setting at Auto or NVIDIA, a Cut row reads `hevc_nvenc` either way. Neither issue names Cut. **Ruled:** file `CONVERT-CUT-ENCODER-LABEL`, with no Cut change here. It is filed at P4 and placed last in current-focus's debt queue, since no remaining session works in its files (D-380).
> - **D-377: the backend's first log line puts the database path, user name included, in the Console.** `build_services` creates the engine (`packages/api/src/avkit_api/wiring.py:135`) before HealthService installs the Console processor (`:205`). So `engine.created path=…` (`packages/infrastructure/src/avkit_infra/database/engine.py:85`) prints unchanged to stdout, and the desktop host forwards it to the Console (`ui/src/main/python-manager.ts:133-145`). The probe found this one line (`C:/Temp/av-kit/s54-plan-startup-stdout-probe.txt`). It predates this session, and neither issue names it. **Ruled:** file `CONSOLE-STARTUP-DB-PATH`, with no change here. It is filed at P3 and placed as a rider in Session 55 (MEU-124), the last code session before rc.2 and the only one left in the database package (D-379).
> - **D-378: the execution loop's token budget.** Round 1 cost more than 5.25M, so the gate asked (Session 52 RULE-3). **Ruled:** open it at the execution default, 21,000,000.
>
> **Round 1 and what changed after it (D-376).** Round 1 approved the plan. Its F1 found that the real-FFmpeg tests, as first described, built no HealthService, so the fixture paths and the scratch database path printed to stdout. Row 1 now builds one before the engine, as production builds it before ConversionService. AC-123.13 asserts that no fixture path reaches stdout, the ring or `console.log`. The other changes are its two non-blocking notes: D-373's wording, and the persistence and ConvertPage rows in §Where `stream_index` goes. These changes apply the reviewer's own recommendations, so no recheck runs for them. Mat took neither widen option, so no recheck runs for D-373 or D-377. The filing and placement change records only, not this plan's code scope, and H1-7's review reads them. The plan loop has 1,958,698 of its 10,500,000 tokens left.
>
> **Already ruled, not asked again:** D-361, D-362 and D-363, Mat's placements of Session 53's three new issues (2026-11-07, recorded in that session's reflection and in each issue's `decision_log`). None of them touches this session's files.
>
> **Your instruction on the other session's files (D-375).** You wrote: "other session updated session grouping for planning of issue filed from session 53, you can continue this will not impact your planning, once you are done you will commit these files". So row 0 records those nine paths in `baseline-dirty.txt` as allowed, row 4 writes on top of the register, MEU status and grouping changes they hold, and H2-5's commit list includes them. The commit itself still waits for your explicit words.
>
> **What the words in Done mean here, and the limits they leave.**
> - **"One meaning" changes no wire field.** The API, MCP and GUI already pass the number through untouched (§Where `stream_index` goes). The meaning is written in contract 08, not in a new schema `description`, so `openapi.committed.json` doesn't change.
> - **All audio streams' file names change for new jobs.** A two-track file now gives `clip_a0.m4a` and `clip_a1.ac3`, where today's plan named `clip_a1` and `clip_a2`.
> - **A file without the asked-for track gets one Failed row at add.** It reads "the file has no audio track", or "no audio track a:2; the file has 1 audio track(s)" for an index past the end. FFmpeg never runs for it. Retry runs FFmpeg, which then fails with "ffmpeg exited …", as a retried probe failure does today (AC-30.1's path).
> - **Existing jobs need nothing (D-369).** The adapter always read an audio position, so a stored row runs as before. Rows already planned with the old numbers keep their names and positions, and the user re-adds the file for the right tracks. A Done Extract row keeps its old encoder label; a retried one loses it.
> - **Extract no longer needs a software encoder.** An Extract row stores no encoder preference (AC-112.4), so the setting decides. Today, with the setting at Software and an FFmpeg that has neither `libx265` nor `libx264`, an Extract fails with "software encoder unavailable" (`conversion.py:411-415`). After the fix it doesn't ask for an encoder.
>
> **The token estimate,** calibrated against Session 42 (plan 12.8M over 2 rounds, execution 4.1M over 1), Session 52 (plan 22.9M over 4 rounds, execution 15.0M plus 4.7M) and Session 53 (plan 8.8M over 2 rounds, execution 10.3M plus 2.6M). This is one service file and a real-binary test, closest to Session 42: expect 1 to 2 plan rounds (about 5M to 11M) and 1 to 2 execution rounds (about 4M to 10M). The plan loop opens with the default 10.5M. If round 1 costs more than 5.25M, the gate asks Mat for the execution loop's budget (Session 52 RULE-3). Round 1 cost 8,541,302, so the gate asked, and Mat ruled the default 21,000,000 (D-378).

## Proposed Changes

### Single-statement contracts

| Term | Meaning |
|---|---|
| `AUDIO_POSITION` | `stream_index` is the Nth audio stream (0-based) in ffprobe's stream order, the N in FFmpeg's `-map a:N`. `_audio_streams(info)` returns the probe's `StreamInfo` entries whose `codec_type` is `audio`, sorted by `index`, or `None` when the positions are unknown (no probe, or `info.streams is None`). An empty list means the file has no audio. |
| `AUDIO_PLAN` | All audio streams plans positions `0..k-1` for a file with `k` audio streams. The naming token is the position: `_a0`, `_a1`, and so on. With unknown positions or no audio it plans one job at `spec.stream_index`, or 0. |
| `EXTRACT_EXT` | `_output_ext` takes the codec of the audio stream at the planned position. With unknown positions, `info.audio_codec` (the first audio stream's codec, `adapter.py:468-471`) applies to position 0 only. Anything else is `.mka`. |
| `MISSING_TRACK` | When the positions are known and the planned one has no audio stream, the job is created `Failed` at add with an `error_message` that names the position and the count, and FFmpeg never runs for it. |
| `EXTRACT_NO_ENCODER` | `_dispatch` neither calls `detect_gpu` nor resolves an encoder for an Extract job, and saves `gpu_encoder=None`. Compress is unchanged, and so is Cut (D-373). |
| `LEGACY_JOBS` | No migration. A stored row's `stream_index` reaches `ExtractOptions` unchanged. |
| `PASS_THROUGH` | The API schema, the route, the MCP tool and the GUI carry `stream_index` without changing it, and none of them changes here. |
| `REAL_FFMPEG` | `tests/integration/test_extract_real_ffmpeg.py` runs the real service on a real SQLite unit of work with `FFmpegAdapter(configured_path=<pinned ffmpeg.exe>)`, on `.mp4` files it generates with that binary. Each test builds a HealthService before it creates the SQLite engine, as production does. It never skips: a missing binary fails with the fetch command in its message. |
| `CI_DESELECT` | CI's Tests step deselects the real-FFmpeg module, because the runner has no fetched binaries (`.gitignore:35`), as it does AC-24.10 and AC-25.10. |
| `NO_RAW_CONSOLE` | No new log line is added, `MISSING_TRACK`'s message holds no path or codec, and it goes to `error_message` only. With a HealthService built, its processor drops every field outside `CONSOLE_FIELDS`. Production builds one before ConversionService (`wiring.py:205`), and the real-FFmpeg module builds one before the engine. AC-123.13 asserts it. The startup line logged before production builds one is D-377. |

### Service: `AUDIO_POSITION`, `AUDIO_PLAN`, `EXTRACT_EXT`, `MISSING_TRACK` (D-364 to D-367)

All in `packages/core/src/avkit_core/services/conversion.py` (CRLF, 602 lines). Row 2 re-reads each anchor first.

- **`_audio_streams`**, a module-level function after `EXTRACT_UNKNOWN_EXT` (`:64`):

  ```python
  def _audio_streams(info: MediaInfo | None) -> list[StreamInfo] | None:
      """AUDIO_POSITION: the audio streams in ffprobe order, so list position N is FFmpeg's a:N.

      None means the positions are unknown: there was no probe, or it listed no streams.
      """
      if info is None or info.streams is None:
          return None
      audio = [s for s in info.streams if isinstance(s, StreamInfo) and s.codec_type == "audio"]
      return sorted(audio, key=lambda stream: stream.index)
  ```

- **`_expand_plans`** (`:314-330`): the Extract branch becomes

  ```python
  audio = _audio_streams(info)
  if spec.stream_mode == "all" and audio:
      return [{"stream_index": position} for position in range(len(audio))]
  index = spec.stream_index if spec.stream_index is not None else 0
  return [{"stream_index": index}]
  ```

  The naming token (`:359-361`) already prints the planned number, so it now prints the position. Its condition, All mode with more than one plan (`:265-269`), doesn't change.
- **`_output_ext`** (`:371-391`): the lookup at `:382-389` becomes a lookup at the position in `_audio_streams(info)`. With unknown positions the `info.audio_codec` fallback applies at position 0 only. A position past the end gives `"unknown"`, so `.mka`.
- **`_jobs_for_path`** (`:240-312`): for an Extract, `audio = _audio_streams(info)` once per file. Each plan's error is `probe_error or _missing_track(plan, audio)`, and a non-`None` error sets `Failed` (today `:272-273`) and `error_message` (today `:302`). `_missing_track` returns `None` when `audio is None` or the position is in range. Otherwise it returns `"the file has no audio track"` when `audio` is empty, else `f"no audio track a:{position}; the file has {len(audio)} audio track(s)"`. The output path is still resolved and reserved, as for a probe failure.

### Rider: `EXTRACT_NO_ENCODER` (D-368)

`_dispatch` (`:486-495`): `caps` and `encoder` are read only at `:487-488`, the save at `:493` and Compress's `codec=encoder` at `:517`. Row 2 sets `encoder = None` for `ConversionKind.Extract` and runs `:487-488` only for the other kinds. The save stays, so a retried legacy Extract row's label is cleared to `None`. Because `detect_gpu` isn't called, an Extract can't fail with `GpuUnavailableError` (`:415`).

### Where `stream_index` goes (`PASS_THROUGH`, D-370)

| Surface | Line | What it sends or shows | Change |
|---|---|---|---|
| API request | `packages/api/src/avkit_api/schemas/conversions.py:52` | `stream_index: int \| None = Field(default=None, ge=0)` | None |
| API route | `packages/api/src/avkit_api/routes/conversions.py:145` | `stream_index=body.stream_index` into `ConversionAddSpec` | None |
| API response | `schemas/conversions.py:83`, `routes/conversions.py:81` | The stored `stream_index` | None. New rows hold positions |
| MCP tool | `mcp-server/src/toolsets/convert.ts:76` | `z.number().int().nonnegative().optional()`, forwarded unchanged | None |
| GUI request | `ui/src/renderer/src/features/converter/convert-body.ts:42`, `:114-119` | Validates and forwards `stream_index`. ConvertPage sends only `stream_mode` | None |
| Persistence | `packages/infrastructure/src/avkit_infra/database/models.py:169`; `mappers.py:402`, `:435`, `:466`; `migrations.py:32` | The column, its two-way mapping and the column's migration entry. The stored int is unchanged | None |
| GUI queue | `ui/src/renderer/src/features/converter/useConversionQueue.ts:22`; `ConvertPage.tsx:544-552` | The row type's `stream_index`, which ConvertPage passes into `convertMetaSegments` | None |
| GUI row | `ui/src/renderer/src/features/converter/convert-controls.ts:208-210` | `a:{n}` from the stored number, now matching FFmpeg's `a:N` | None |
| GUI encoder | `convert-controls.ts:225-236` | `convertMetaSegments` drops a null `gpu_encoder` (AC-45.17, `ui/tests/unit/convert-controls.test.ts:218-231`) | None |
| Service | `services/conversion.py` | `AUDIO_POSITION` everywhere | Rows 1, 2 |
| Adapter | `adapter.py:634-635` | `-map a:{stream_index}`: already a position | None |

Pass-through is already proved by AC-31.21 (`tests/e2e/test_api_conversions.py:744-762`) and MCP `mcp-server/tests/convert.test.ts:254-264`. Both run in the session gate's full suites.

### Where values go (Session 50 RULE-1, Session 53 RULE-1; D-372)

- **`convert.extract`** logs `stream_index`, an int (`adapter.py:638`).
- **`convert.finished` and `convert.cancelled`** log `argv=command[1:4]` (`adapter.py:370`, `:374`). For an extract this is `["-y", "-i", <input path>]`, so it holds a raw path. `argv` isn't in `CONSOLE_FIELDS` (`packages/core/src/avkit_core/services/health.py:47-56`), and `_process` replaces the whole event with the Console's safe message before any renderer runs (`:233-235`, configured at `:176`). So once a HealthService is built, the path reaches no log file, stdout, ring or Console. Production builds it before ConversionService (`packages/api/src/avkit_api/wiring.py:205`). Without one, structlog's default renderer prints every field, so the real-FFmpeg module builds one first (D-376, AC-123.13). This session doesn't change these lines.
- **`engine.created`** logs `path=str(db_path)` (`packages/infrastructure/src/avkit_infra/database/engine.py:85`). `build_services` creates the engine (`wiring.py:135`) before HealthService (`:205`), so in production this line prints unchanged to stdout. The host forwards it to the Console (`ui/src/main/index.ts:267-274`, `ui/src/main/python-manager.ts:133-145`, `ui/src/renderer/src/hooks/useBackendLogs.ts:69-80`). It predates this session. Under Mat's D-377 ruling it is filed as `CONSOLE-STARTUP-DB-PATH` and placed in Session 55 (D-379). In the real-FFmpeg module the HealthService comes first, so the line is dropped there.
- **FFmpeg's own output** never reaches the backend's stdout. The encode runner sends FFmpeg's stdout to `DEVNULL` and reads its stderr for progress only (`adapter.py:282-286`), and `_run` captures both (`:262-269`).
- **`MISSING_TRACK`'s message** holds a position and a count, no path, codec or title. It is stored in `error_message`, returned by the API and shown in the GUI row, and it is never logged.
- **FFmpeg's stderr** isn't stored: a failure keeps `ffmpeg exited N` (`adapter.py:373`).
- **Session 53 RULE-1 doesn't apply.** No stream title, language or other outside text is stored or named from. Only the codec name picks an extension, through a fixed map.

### Spec text (D3)

| File | Lines | Change |
|---|---|---|
| `docs/build-plan/08-video-conversion.md` | `:176-177` | First audio stream is position 0. All audio streams is one job per audio stream at positions 0 to k-1, named `_a0`…, and a file with no audio track gives one Failed row |
| `docs/build-plan/08-video-conversion.md` | `:468` | `stream_index` is the Nth audio stream (0-based), the N in `-map a:N` |
| `docs/build-plan/08-video-conversion.md` | `:476` | `gpu_encoder` is `null` for an Extract |
| `docs/build-plan/08-video-conversion.md` | after `:605` | A Delivered note naming the mechanism ids, the ACs, the real-FFmpeg module and its CI deselect |

Row 4 re-reads each anchor before it writes (Session 51 RULE-3), and it cites the lines as they read after rows 1 to 3. The registered text above the residual's table is history and isn't rewritten. The file is LF.

### MEU-123 `convert-extract-stream-index`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `POST /api/v1/conversions` extract body | `schemas/conversions.py:52` (unchanged) | `stream_mode` `first` \| `all`; `stream_index` `int ≥ 0` or absent; now an audio position | Extra forbid (unchanged) |
| MCP `avkit_convert` add | `convert.ts:76` (unchanged) | `stream_index` non-negative int, optional | Strict (unchanged) |
| ffprobe → `MediaInfo.streams` | `adapter.py:403-486` (unchanged) | `StreamInfo.index` is ffprobe's index; `codec_type`, `codec_name` | Read by `_audio_streams` only |
| `ConversionJob.stream_index`, `gpu_encoder` | `domain/conversion.py` (unchanged) | `int \| None`; `str \| None`, now `None` for Extract | Unchanged, no schema change |

#### Acceptance Criteria

Pytest names are `test_ac_123_<n>_…`. AC-123.1 to .8 go in `tests/unit/test_conversion_service.py` with the module's fakes; AC-123.9 to .13 go in the new `tests/integration/test_extract_real_ffmpeg.py`.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-123.1 | unit | First mode on a picture-first probe (`[0 video h264, 1 audio aac]`) gives one job at `stream_index` 0, named `clip_a.m4a`, and after processing the fake's `encode_options` hold one `ExtractOptions(stream_index=0, output_container="m4a")` (`RecordingMedia.extract_stream` records through `encode`, `tests/unit/test_conversion_service.py:266-274`) | Local Canon: 08 `:602`; triage D-227 | Yes: Red, today `.mka` |
| AC-123.2 | unit | All mode on `[0 video, 1 audio aac, 2 audio ac3]` gives jobs at 0 and 1, named `clip_a0.m4a` and `clip_a1.ac3`, and the fake's `encode_options` hold `stream_index` 0 and 1 | Local Canon: 08 `:603`; triage D-227 | Yes: Red, today 1 and 2 |
| AC-123.3 | unit | All mode on `[0 video, 1 audio aac]` gives one job at 0, named `clip_a.m4a` | Local Canon: 08 `:603` | Yes: Red, today 1 |
| AC-123.4 | unit | `MISSING_TRACK`: a video-only probe gives one `Failed` job in First mode and in All mode, each with "the file has no audio track". First mode with `stream_index=2` on `[0 video, 1 audio aac]` gives `Failed` with "no audio track a:2; the file has 1 audio track(s)". After `start_processing`, the jobs are still `Failed` and `media.encode_calls` is 0 | Local Canon: brief ("no job asks for a track that doesn't exist"); AC-30.1's path | Yes: Red, today `Pending` |
| AC-123.5 | unit | Unknown positions (`streams=None`, `audio_codec="aac"`, the fake's default): position 0 gives `.m4a`, position 1 gives `.mka`, both `Pending` | Local Canon: `EXTRACT_EXT`; `adapter.py:468-471` | Yes: Red on position 1, today `.m4a` |
| AC-123.6 | unit | `EXTRACT_NO_ENCODER`: with NVIDIA caps an Extract job ends `Done` with `gpu_encoder is None`, and a subclass of `RecordingMedia` that counts `detect_gpu` calls saw none. With the `software` setting and caps that have neither software encoder (AC-30.11's shape, `:681-710`), an Extract job ends `Done` | Local Canon: `CONVERT-EXTRACT-ENCODER-LABEL` | Yes: Red, today `hevc_nvenc`, and the second fails with "software encoder unavailable" |
| AC-123.7 | unit | `LEGACY_JOBS`: an Extract row stored `Failed` with `stream_index=1` and `gpu_encoder="hevc_nvenc"`, retried through `reset_failed`, reaches the fake as `ExtractOptions(stream_index=1, …)` and ends with `gpu_encoder is None` | Local Canon: brief ("whether existing jobs need anything") | Yes: Red on the label |
| AC-123.8 | unit | Compress still saves its encoder: `libx265` on default caps, `hevc_nvenc` with NVIDIA caps and Auto | Local Canon: brief ("a Compress job still saves one"); AC-112.1 | Guard: passes in Red |
| AC-123.9 | integration | The pinned `packaging/ffmpeg-win64/ffmpeg.exe` and `ffprobe.exe` exist and are over 1024 B, and the message names `tools/fetch_ffmpeg_windows.ps1`. `FFmpegAdapter(configured_path=<pinned>).ffmpeg_binaries()` resolves to both. The generated fixtures probe as: `one_track` `[video, audio aac]`, `two_track` `[video, audio aac, audio ac3]`, `no_audio` `[video]` | Local Canon: AC-25.10 (`tests/unit/test_packaging_installer.py:94-116`) | Guard: passes in Red; it proves the fixtures |
| AC-123.10 | integration | First mode, parametrized over `one_track` and `two_track`, through the real stack: one job, `Done`, `<stem>_a.m4a`, which the real adapter probes as one `aac` audio stream and no video; `gpu_encoder is None` | Local Canon: 08 `:605`; triage D-227 | Yes: Red, today `.mka` |
| AC-123.11 | integration | All mode, parametrized: `one_track` gives one job at 0, `Done`, `<stem>_a.m4a` (`aac`). `two_track` gives jobs at 0 and 1, both `Done`, `<stem>_a0.m4a` (`aac`) and `<stem>_a1.ac3` (`ac3`). Every job's `gpu_encoder is None` | Local Canon: 08 `:603`, `:605` | Yes: Red, today `a:1` fails on `one_track` and `a:2` on `two_track` |
| AC-123.12 | integration | `no_audio` through the real stack, First mode and All mode: one `Failed` job at add with "the file has no audio track"; after the worker drains it is still `Failed`, no output file exists, and a counting subclass of `FFmpegAdapter` saw no `extract_stream` call | Local Canon: brief; `MISSING_TRACK` | Yes: Red, today `Pending` |
| AC-123.13 | integration | `NO_RAW_CONSOLE` through the real stack. The module's media folder is made with a marker in its name. The test's HealthService (`app.log_to_file` on) is built before the engine, and a First-mode Extract of `one_track` runs to `Done`. Neither the marker nor pytest's base temp folder appears in `capfd`'s stdout and stderr, the ring's messages or `console.log`. The ring holds `engine.created` and `convert.finished`, the positive controls | Local Canon: Session 50 RULE-1; plan review F1; AC-115.19 (`tests/integration/test_transcript_failure_delivery.py:33-66`) | Guard: passes in Red, since the Red's `.mka` changes nothing that is logged |

Guards that run unchanged in row 2: AC-30.13 (`tests/unit/test_conversion_service.py:570-651`, audio-first probes, where index and position agree), AC-112.1 to AC-112.4, AC-30.1, AC-30.11, AC-30.12, `tests/unit/test_ffmpeg_conversion.py`, `tests/integration/test_filesystem_media.py`, `tests/integration/test_api_wiring.py`, `tests/e2e/test_api_conversions.py` (AC-31.21 among them) and `tests/e2e/test_api_bodies.py`: every Python test file that names the conversion service or route outside the two this plan edits. The MCP and UI suites run in the session gate.

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| One meaning, audio position | Local Canon | 08 `:601`; triage D-227; the adapter's `a:N` |
| Extension from the audio position | Local Canon | 08 `:602`; Extract table `:178` |
| All audio streams sends positions | Local Canon | 08 `:603` |
| A missing track fails at add | Inferred, flagged | D-367: the brief's "no job asks for a track that doesn't exist"; AC-30.1 fails a probe the same way |
| No encoder for Extract | Local Canon | 08 `:604`; the rider issue |
| Existing jobs | Local Canon | D-369: the adapter always read a position |
| Tests on a real `.mp4` | Local Canon | 08 `:605`; D-371 |
| Cut's label | Human-approved | D-373: filed, placed by D-380 |
| No fixture path reaches the Console | Local Canon | Session 50 RULE-1; plan review F1; D-376 |
| The startup line's database path | Human-approved | D-377: filed, placed by D-379 |

### Files Modified

| File | Action | Summary |
|---|---|---|
| `packages/core/src/avkit_core/services/conversion.py` | Modify | `_audio_streams`, `_missing_track`, `_expand_plans`, `_output_ext`, `_jobs_for_path`, `_dispatch` |
| `tests/unit/test_conversion_service.py` | Modify | AC-123.1 to .8, appended; imports stay inside tests, as its docstring says |
| `tests/integration/test_extract_real_ffmpeg.py` | New | AC-123.9 to .13 |
| `.github/workflows/ci.yml` | Modify | `CI_DESELECT` and its comment (`:56-63`) |
| `docs/build-plan/08-video-conversion.md` | Modify | §Spec text |

No test id is added, so `ui/tests/e2e/test-ids.ts` and its byte-hash tests aren't touched. No API schema changes, so `openapi.committed.json` doesn't. Line endings (`C:/Temp/av-kit/s54-plan-probes.txt`): the service, the unit test file and the grouping file are CRLF. `ci.yml`, contract 08 and the register are LF. Each row measures the endings with Python bytes first and writes with `newline=""`, so they don't change. New files in this plan folder and the new test module are LF.

### Project files

- `docs/execution/plans/2026-11-07-convert-extract-index/`: `implementation-plan.md`, `task.md`, `human-gate-decision.md`, `baseline.ps1`, `baseline.sha`, `baseline-dirty.txt`, `red-check.py`, `identity.py`, `ci-collect.py`, `issue-resolve.py`, `session-gate.ps1`.
- `.agent/context/meu-status.yaml`, `docs/BUILD_PLAN.md`, `.agent/context/meu-registry.md`, `.agent/context/known-issues.yaml` and its renders, `.agent/context/triage-output.yaml`, and the grouping tracker row (`:254`).
- `.agent/context/handoffs/2026-11-07-convert-extract-index-*.md`, `docs/execution/reflections/2026-11-07-convert-extract-index-reflection.md`, `docs/execution/metrics.md`, `.agent/context/current-focus.md`.
- The other session's uncommitted paths in `baseline-dirty.txt`, which the commit carries (D-375).

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Cut's encoder label | Neighbouring defect | None: `CONVERT-CUT-ENCODER-LABEL`, P4, current-focus's debt queue (D-373, D-380) | Neither issue names Cut |
| The startup `engine.created` line's database path | Neighbouring defect | MEU-124, rider `CONSOLE-STARTUP-DB-PATH`, P3 (D-377, D-379) | It predates this session, and neither issue names it |
| Renaming or re-planning stored Extract rows | Migration | None | D-369: they run as before; the user re-adds the file |
| A schema `description` for `stream_index` | Wire text | None | D-370: it would change `openapi.committed.json`; contract 08 carries the meaning |
| Picking a track by language or title in the GUI | Feature | None | The GUI offers First and All only (08 `:176-177`) |
| Video-only and subtitle extract | Feature | None | Deferred in 08 `:179` |
| Re-checking positions when a Failed `MISSING_TRACK` row is retried | Limit | None | Stated at the gate: retry runs FFmpeg, as a retried probe failure does |
| Running the real-FFmpeg module in CI | CI | None | `CI_DESELECT`: the runner has no fetched binaries, as for AC-25.10 |

## BUILD_PLAN.md Audit

MEU-123 is at `.agent/context/meu-status.yaml:3214`, band P2, matrix item 8.9, anchor `extract-stream-index-residual`. Plan time: 127 MEUs, 116 completed, 11 pending (`C:/Temp/av-kit/s54-plan-meu-stats.txt`). Row 4 sets `ready_for_review` with `tools/meu_status.py update`, and H2-2 sets `approved`. The render check runs at rows 4 and H1-3:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/s54-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s54-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` does the following:

1. Creates `C:\Temp\av-kit\s54\tmp`. Records `HEAD` in `baseline.sha`, and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt` with each dirty path's SHA-256.
2. Runs `uv sync --frozen --offline --all-packages`, so this step can't fetch a package (plan-time dry run: `s54-uv-offline-dry-run.txt`, "Would make no changes"), and proves `ui/` and `mcp-server/node_modules` match their locks. `npm ci` isn't run, for Session 50's reason. It asserts the pinned FFmpeg pair exists and is over 1024 B, and records its `-version` first line. It then captures the base Python suite to `s54-base-py.txt`, the base UI suite to `s54-base-ui.txt` and the base MCP suite to `s54-base-mcp.txt`, with `TMP` and `TEMP` at `C:\Temp\av-kit\s54\tmp`.
3. Runs `red-check.py --selftest` and `identity.py --selftest`.

`baseline.ps1`, `red-check.py` and `identity.py` are copies of Session 53's, with this plan's values:

- **`red-check.py`.** `DECLARED_NEW` holds `_audio_streams` and `_missing_track` and keeps the selftest fixtures' names. No test references either, because every AC goes through the service's public calls or `FFmpegAdapter`, both existing.
- **`identity.py`.** `PLAN` is this folder, and `NAMED_DISTRIBUTIONS` stays empty: no Python dependency changes. It also binds the pinned `ffmpeg.exe` and `ffprobe.exe` by SHA-256, because the runtime stage depends on them.
- **`PROJECT_ARTIFACTS`.** It holds this plan's `*.md`, the handoff, the review and reflection files, `docs/execution/metrics.md` and `.agent/context/current-focus.md`, which are written after the gate. The registers and renders stay bound, because row 4 writes them before H1-2.

### 2. Red then Green (rows 1 and 2)

- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py` refuses a collection error and a required test that fails on a missing name. No AC needs a new name, so Session 52 RULE-4 has no target.
- **`--require` matches a test name up to a non-digit boundary** (`test_ac_123_1` never matches `test_ac_123_10`).
- **One runner summary per receipt.**
- **Guards pass in Red by design.** AC-123.8, AC-123.9 and AC-123.13 are in row 1's selection, and no Red row requires them.
- **The fixtures are generated, never committed (D-371).** A module-scoped fixture in `test_extract_real_ffmpeg.py` makes one folder with `tmp_path_factory.mktemp`, its name holding AC-123.13's marker. It runs the pinned `ffmpeg.exe` there with `-f lavfi`: `testsrc=size=64x64:rate=10:duration=1` as `mpeg4` video first, then one `sine` input per track (`aac`, or `aac` and `ac3`), mapped in that order, with `-shortest`, into `tmp_path`. The plan-time probe built `one_track.mp4` (16,602 B, streams `[0 mpeg4, 1 aac]`) and `two_track.mp4` (29,706 B, `[0 mpeg4, 1 aac, 2 ac3]`) in about 0.13 s each with FFmpeg n8.1.3, and showed `a:0` and `a:1` extract while `a:1` on one track and `a:2` on two tracks fail (`s54-plan-ffmpeg-fixture-probe.txt`). `no_audio.mp4` is the same command with no `sine` input.
- **Each test's stack builds a HealthService first (D-376).** It follows AC-115.19 (`tests/integration/test_transcript_failure_delivery.py:33-49`): `HealthService(SharedFakeFactory(FakeUnitOfWork()), app_data=tmp_path / "app", settings=…, media=FakeMedia(), youtube=FakeYouTube(), assets=FakeAssets(), download_runtime=idle_runtime)`. Its own fake-backed `SettingsService` has `app.log_to_file` on, so `console.log` sees every line. Its constructor installs the Console processor, so a Red failure's captured stdout holds no path. A Red assertion message can still name a fixture path, which pytest puts under `C:\Temp\av-kit\s54\tmp\pytest-of-<user>` (§1). That is the test runner's report in a receipt, not a Console surface, and no tracked file quotes it.
- **The real stack then follows AC-30.12** (`tests/unit/test_conversion_service.py:537-567`): `create_sqlite_engine`, `init_schema`, `SqlAlchemyUnitOfWork`, `SettingsService` with `converter.output_dir` in `tmp_path` and `skip_existing` off. The queue runs through `start_processing()` and a `_thread.join(timeout=60)`, and the test asserts the thread has stopped. Outputs are read back with the real adapter's `probe`.
- **Expectations stay immutable in Green.** No test file changes in row 2.
- **Session 51 RULE-1 has no target here.** No UI test is written.
- **No network.** FFmpeg reads only files in `tmp_path`.

### Plan-local scripts

- `red-check.py`, `identity.py`, `baseline.ps1`: §1.
- `ci-collect.py` (row 3), LF. It reads `.github/workflows/ci.yml` with `yaml.safe_load`, takes the `Tests` step's `run` string, splits it with `shlex.split`, appends `--collect-only` (the step's own `-q` makes pytest list one node id per line; a second `-q` would list file counts instead), and runs it with `TMP` and `TEMP` as in §1 and `UV_OFFLINE=1`, so the step's `uv run --locked --no-sync` can't fetch (`s54-plan-uv-locked-offline.txt`). It exits 0 only when the run exits 0, no collected id starts with `tests/integration/test_extract_real_ffmpeg.py`, and the run without that one `--deselect` collects the module's ids. So the check proves the argv as CI holds it, not a copy.
- `issue-resolve.py` (row 4): Session 53's copy with `SCRATCH` at `C:/Temp/av-kit/s54`. `RESOLVE_KEYS` stay `status`, `verification` and `resolution_path`. `CONVERT-EXTRACT-ENCODER-LABEL` lacks `resolution_path`, so the script adds it before `category`; `CONVERT-EXTRACT-STREAM-INDEX-MISMATCH` holds all three (Session 51 RULE-2; `s54-plan-probes.txt`).
- `session-gate.ps1` (H1-2): below.

### Session gate (H1-2)

`session-gate.ps1` is Session 53's shape. It writes one receipt per step in `C:/Temp/av-kit`, named `s54-D6-<step>`. It is fail-fast, and it prints later steps as `not_run`. It sets `TMP` and `TEMP` as in §1 and clears `ELECTRON_RUN_AS_NODE`. Its last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `py-types`, `py-lint`, `ui-types`, `ui-lint`, `task-contract`, `scope-paths` (this plan's Files Modified and project files, plus `baseline-dirty.txt`; `ui/tests/e2e/test-ids.ts` refused), `red-check-selftest` |
| Fresh full | `py-tests`, `ui-tests`, `ui-build`, `openapi`, `mcp-types`, `mcp-tests`, `mcp-build`, `state-render`, `issues-render`, `ci-collect` |
| Runtime | `extract-real-ffmpeg` (the new module on its own, so its receipt stands alone), then `ui-electron`, targeted to `ui/tests/e2e/convert-queue.test.ts` |
| Skipped with reason | `mcp-audit` (live network), `build-record` (no installer build), the package build and its smokes (no packaged surface changes; MEU-125 runs them) |

`py-tests`, `ui-tests` and `mcp-tests` excuse only ids that row 0's receipts show failing, as Session 53 did. A step that fails in a file this session didn't touch is rerun once unchanged, and both attempts' receipts are kept (Session 53 RULE-4).

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | `graphify-out/` or `graphify-out-research/` appears | Re-decide the context tool |
| S2 | A Red receipt fails `red-check.py` | Fix the test setup; don't move to Green |
| S3 | `HEAD` moves from `baseline.sha`; a path outside `baseline-dirty.txt` and this plan appears; or, before rows 4 and H1-2, a `baseline-dirty.txt` path that no row of this plan has written yet differs from its recorded SHA-256 | Stop and tell Mat; never commit, stash or revert another session's work |
| S4 | The pinned FFmpeg pair is missing or under 1024 B | Stop: fetching it is a download and needs Mat's words |
| S5 | Any network request, download or upload | Stop and tell Mat |
| S6 | `export_openapi.py --check` reports drift | Stop: this plan changes no schema, so find out why |
| S7 | Codex is unavailable or the ledger refuses a round | Mat is the fallback |
| S8 | The generated fixtures probe in a different stream order than AC-123.9 states | Stop before Green; the Red would prove nothing |
| S9 | A row finds it must edit `ui/tests/e2e/test-ids.ts` | Stop, add ids in an additive block at the end, and run AC-51.6 and AC-81.13 in that row's own check |
| S10 | A path, codec or `MISSING_TRACK` message reaches a Console surface in any receipt, other than the `engine.created` line, which is filed as `CONSOLE-STARTUP-DB-PATH` and placed in Session 55 (D-377, D-379) | Fix it in the row or raise it with Mat; never record it as a residual (Session 50 RULE-1) |

## Decision Log

> [!WARNING]
> Mat's brief and triage D-227 settle the scope. D-373, D-377 and D-378 have Decision Briefs in `human-gate-decision.md`, each with a recommendation and a do-nothing option, and Mat accepted all three recommendations on 2026-11-07. D-375 records Mat's instruction on the other session's files. D-376 folds in plan review round 1's F1. D-379 and D-380 place the two filed issues in the grouping, as Mat asked in the same message; they are copied from each issue's `decision_log`.
>
> Carried from the grouping and not relisted in the block, because the grouping's rows hold them: every §8 row, D-240 to D-250, D-267, D-277 and D-280, with stage `grouping`. Of those, D-242 puts the encoder-label rider here and D-250 keeps this MEU apart from MEU-124. The closeout check reads all of them, and D-246 stays as a withdrawn row. D-361 to D-363 are Mat's rulings on Session 53's issues, recorded outside §8.
>
> The triage decision D-227 is in `.agent/context/known-issues.yaml` under `CONVERT-EXTRACT-STREAM-INDEX-MISMATCH`. The rider's issue holds no decision log. The probe (`C:/Temp/av-kit/s54-decision-issue-probe.txt`) confirms that the two flags pull in D-227 and the grouping rows, and nothing else. H2-2 passes `--decision-issue` for both.

```yaml
decision_log:
  - id: D-364
    stage: planning
    question: "What does stream_index mean, and where is that meaning computed?"
    resolution: autonomous
    class: two-way
    chosen: "AUDIO_POSITION: the Nth audio stream in ffprobe order, the N in -map a:N; one module function _audio_streams returns the ordered audio StreamInfo list, or None when positions are unknown"
    source_tag: Local Canon
    precedents: ["docs/build-plan/08-video-conversion.md:601 — 'stream_index is audio-relative everywhere'", "packages/infrastructure/src/avkit_infra/media/adapter.py:634-635 — -map a: followed by the stream index", "docs/build-plan/08-video-conversion.md:176 — First audio stream is map a:0", "known issue CONVERT-EXTRACT-STREAM-INDEX-MISMATCH — triage D-227"]
    research: { engine: none, sources: [] }
    reasoning: "The adapter, the Extract table and D-227 already use the audio position; only the service disagrees, so the service moves. One function keeps _expand_plans, _output_ext and the missing-track check from drifting apart again. Making the adapter take ffprobe's index instead would change the wire meaning the API and MCP already document as a:N and every stored row."
  - id: D-365
    stage: planning
    question: "What does All audio streams plan, and what are its files called?"
    resolution: autonomous
    class: two-way
    chosen: "AUDIO_PLAN: positions 0..k-1; the existing token prints the position, so _a0, _a1; one plan when positions are unknown or the file has no audio"
    source_tag: Local Canon
    precedents: ["docs/build-plan/08-video-conversion.md:177 — one ConversionJob per stream", "docs/build-plan/08-video-conversion.md:603 — 'The plan sends audio positions'", "packages/core/src/avkit_core/services/conversion.py:359-361 — the token"]
    research: { engine: none, sources: [] }
    reasoning: "Positions are what FFmpeg selects, so the names say which track a file holds. Keeping ffprobe's index in the name while sending the position would print a number the GUI's a:N row contradicts. New names differ from today's for the same file, stated at the gate."
  - id: D-366
    stage: planning
    question: "Which codec picks an Extract's extension when the positions are unknown or out of range?"
    resolution: autonomous
    class: two-way
    chosen: "EXTRACT_EXT: the codec at the position; with unknown positions, info.audio_codec at position 0 only; anything else .mka"
    source_tag: Local Canon
    precedents: ["packages/infrastructure/src/avkit_infra/media/adapter.py:468-471 — audio_codec is the first audio stream's", "docs/build-plan/08-video-conversion.md:178 — unknown gives .mka"]
    research: { engine: none, sources: [] }
    reasoning: "audio_codec describes position 0, so using it for another position is the same mismatch in another place. The real adapter always lists streams, so this fallback serves fakes and a probe that lists none."
  - id: D-367
    stage: planning
    question: "What happens when a file lacks the asked-for audio track?"
    resolution: autonomous
    class: two-way
    chosen: "MISSING_TRACK: when positions are known and the planned one is absent, the job is created Failed at add with 'the file has no audio track' or 'no audio track a:N; the file has K audio track(s)', with N the asked-for position and K the file's audio count; FFmpeg never runs; a retry runs FFmpeg and fails as a retried probe failure does"
    source_tag: Local Canon
    precedents: ["brief — 'no job asks for a track that doesn't exist'", "packages/core/src/avkit_core/services/conversion.py:252-273 — a probe failure creates a Failed job at add", "tests/unit/test_conversion_service.py:299-318 — AC-30.1"]
    research: { engine: none, sources: [] }
    reasoning: "AUDIO_PLAN removes the wrong positions, but a video-only file in either mode and an explicit index past the end can still ask for a missing track. Failing at add keeps a batch add going, as AC-30.1 does for a bad probe, and shows the reason in the row. Refusing the whole request with a 4xx would drop the other files in the batch. Doing nothing leaves FFmpeg's 'Invalid argument' as the only reason."
  - id: D-368
    stage: planning
    question: "How does an Extract job save no encoder?"
    resolution: autonomous
    class: two-way
    chosen: "EXTRACT_NO_ENCODER: _dispatch skips detect_gpu and _resolve_encoder for Extract and saves gpu_encoder=None; Compress and Cut unchanged"
    source_tag: Local Canon
    precedents: ["known issue CONVERT-EXTRACT-ENCODER-LABEL — 'an extract is a stream copy that uses no encoder'", "docs/build-plan/08-video-conversion.md:604", "packages/core/src/avkit_core/services/conversion.py:486-495 — _dispatch"]
    research: { engine: none, sources: [] }
    reasoning: "An Extract never reads the encoder, so not resolving it is the smallest change and also stops an Extract failing for want of a software encoder. Saving None rather than skipping the save clears a legacy label on retry. Clearing the label in the API or GUI instead would leave the stored row wrong."
  - id: D-369
    stage: planning
    question: "Do existing jobs need anything?"
    resolution: autonomous
    class: two-way
    chosen: "LEGACY_JOBS: no migration; a stored row's stream_index reaches ExtractOptions unchanged; old names stay; a Done row keeps its old label and a retried one loses it"
    source_tag: Local Canon
    precedents: ["packages/infrastructure/src/avkit_infra/media/adapter.py:634-635 — the adapter always read a position", "packages/core/src/avkit_core/services/conversion.py:549-558 — Extract dispatch reads the stored row", "brief — 'The plan says whether existing jobs need anything'"]
    research: { engine: none, sources: [] }
    reasoning: "_expand_plans and _output_ext run only at add, so a stored row's meaning never changed. A migration would have to re-probe every input and rename planned outputs, which the user gets by re-adding the file."
  - id: D-370
    stage: planning
    question: "Do the API, MCP and GUI change to carry the one meaning?"
    resolution: autonomous
    class: two-way
    chosen: "PASS_THROUGH: no change; contract 08 :468 states the meaning; no schema description, so openapi.committed.json is unchanged"
    source_tag: Local Canon
    precedents: ["packages/api/src/avkit_api/schemas/conversions.py:52", "mcp-server/src/toolsets/convert.ts:76", "ui/src/renderer/src/features/converter/convert-controls.ts:208-210", "tests/e2e/test_api_conversions.py:744-762 — AC-31.21 pass-through"]
    research: { engine: none, sources: [] }
    reasoning: "Every surface forwards the number untouched, and the GUI's a:N label already reads it as a position, so only the service was wrong. A schema description would force an OpenAPI regeneration for a text change; the contract is where av-kit records wire meaning."
  - id: D-371
    stage: planning
    question: "How do the tests run a real .mp4 through the real FFmpeg adapter, and where do the fixtures live?"
    resolution: autonomous
    class: two-way
    chosen: "REAL_FFMPEG and CI_DESELECT: a new integration module generates one_track, two_track and no_audio .mp4 files in tmp_path with the pinned ffmpeg.exe and lavfi, runs the real service on real SQLite with FFmpegAdapter(configured_path=pinned), never skips, and is deselected in CI"
    source_tag: Local Canon
    precedents: ["docs/build-plan/08-video-conversion.md:605 — 'Both modes against a real .mp4'", "tests/unit/test_packaging_installer.py:94-116 — AC-25.10 asserts the pinned binaries", ".github/workflows/ci.yml:56-63 — AC-24.10 and AC-25.10 deselected", "C:/Temp/av-kit/s54-plan-ffmpeg-fixture-probe.txt — generation in ~0.13 s, offline"]
    research: { engine: none, sources: [] }
    reasoning: "Generating keeps media bytes out of the repository and pins the stream order the bug needs (picture first). The pinned binary is what users run, and configured_path makes PATH irrelevant. A skip would hide a missing binary, and the suite has none. CI has no fetched binaries, so the AC-25.10 precedent applies; fetching FFmpeg in CI would be a new download step."
  - id: D-372
    stage: planning
    question: "Where are paths, codecs and the new message written, and does console_field see them (Session 50 RULE-1)?"
    resolution: autonomous
    class: governance-value
    chosen: "§Where values go: no new log line; once a HealthService is built, the argv path in convert.finished and convert.cancelled is dropped by _process before any renderer; MISSING_TRACK's message holds no path and is never logged; Session 53 RULE-1 has no target"
    source_tag: Local Canon
    precedents: ["docs/execution/reflections/2026-11-05-transcript-failure-reason-reflection.md:137 — Session 50 RULE-1", "packages/core/src/avkit_core/services/health.py:47-56 — CONSOLE_FIELDS", "packages/core/src/avkit_core/services/health.py:233-235 — _process clears the event", "packages/api/src/avkit_api/wiring.py:205 — production builds HealthService before ConversionService"]
    research: { engine: none, sources: [] }
    reasoning: "The brief asks for this statement. The only raw value near this code is the input path in argv. The Console processor removes it before stdout, the ring or the file see it, but only once a HealthService is built. Production builds one before ConversionService, and the real-FFmpeg module builds one first (D-376). The startup line logged before that is D-377."
  - id: D-373
    stage: planning
    question: "A Cut job also saves an encoder it never uses. Register it, fix it here, or leave it?"
    resolution: human
    class: product-preference
    chosen: "File CONVERT-CUT-ENCODER-LABEL, with no Cut change in MEU-123; filed at plan time through model.add_issue (C:/Temp/av-kit/s54-plan-register-file.txt) and placed by D-380"
    source_tag: Human-approved
    precedents: ["human-gate-decision.md — D-373 brief and Mat's ruling", "packages/infrastructure/src/avkit_infra/media/adapter.py:590-604 — Cut uses copy or libx265", "Session 52 D-337, D-344 — neighbours filed; Session 53 D-354 — a neighbour fixed in place"]
    research: { engine: pomera_web_search (tavily), sources: ["https://www.ffmpeg.org/doxygen/2.4/ffmpeg_8h_source.html", "https://ossrs.io/lts/en-us/docs/v7/doc/ffmpeg"] }
    reasoning: "The two precedents point different ways, and widening changes a behaviour neither issue names, so the call was Mat's. Filing keeps MEU-123 to the two issues it closes, and the plan needs no recheck."
    human_message_reference: "USER_EXPLICIT 2026-11-07 'All recommendations accepted. But also file, and assign into session groupings So next sessions, can handle the new issues.'"
  - id: D-374
    stage: planning
    question: "Which checks does the session gate run?"
    resolution: autonomous
    class: two-way
    chosen: "Session 53's shape plus ci-collect; the runtime stage is the real-FFmpeg module on its own, then the convert queue E2E; no package build or smokes; mcp-audit and build-record skipped with reasons"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-11-07-transcript-metadata/implementation-plan.md:368-380 — Session 53 §Session gate"]
    research: { engine: none, sources: [] }
    reasoning: "The real binary is this change's runtime proof. The convert queue E2E guards the unchanged GUI that shows these rows. No packaged surface changes, and MEU-125 builds the installer."
  - id: D-375
    stage: planning
    question: "The tree holds another session's uncommitted files. Plan on top of them, and what does the commit carry?"
    resolution: human
    class: product-preference
    chosen: "Continue planning; row 0 records the nine paths as allowed; Session 54's commit carries them, on Mat's explicit words at H2-5"
    source_tag: Human-approved
    precedents: ["brief — 'If the tree holds uncommitted files from another session, stop and tell me'"]
    research: { engine: none, sources: [] }
    reasoning: "The brief made it Mat's call, and Mat answered."
    human_message_reference: "USER_EXPLICIT 2026-11-07 'other session updated session grouping for planning of issue filed from session 53, you can continue this will not impact your planning, once you are done you will commit these files'"
  - id: D-376
    stage: planning
    question: "Plan review F1: the real-FFmpeg tests built no HealthService, so the fixture and database paths printed to stdout. How does the plan answer it, and does the amended plan need a recheck?"
    resolution: autonomous
    class: governance-value
    chosen: "Each real-FFmpeg test builds a HealthService before the engine, in AC-115.19's shape with app.log_to_file on; new guard AC-123.13 asserts that neither the fixture folder's marker nor pytest's base temp folder reaches capfd's stdout and stderr, the ring or console.log, with engine.created and convert.finished in the ring as positive controls; NO_RAW_CONSOLE and D-372 are qualified; no recheck, because the amendments apply round 1's own recommendations and wording notes; a recheck runs only if Mat widens D-373 or D-377"
    source_tag: Local Canon
    precedents: [".agent/context/handoffs/2026-11-07-convert-extract-index-plan-critical-review.md — F1 and its recommendation; its wording notes are 'not grounds for another review cycle by themselves'", "tests/integration/test_transcript_failure_delivery.py:33-66 — AC-115.19 builds HealthService with fakes and reads stdout, the ring and console.log", "packages/core/src/avkit_core/services/health.py:163-183 — the constructor installs the processor", "packages/api/src/avkit_api/wiring.py:205 — production's order"]
    research: { engine: none, sources: [] }
    reasoning: "F1 asked the row-1 setup to handle its own logging and to assert the marker is absent, and this does both in the production order. capfd rather than capsys also catches a child process writing to the inherited descriptors. Building HealthService after the engine would still print the scratch database path. Doing nothing breaks Session 50 RULE-1."
  - id: D-377
    stage: planning
    question: "The backend's startup engine.created line prints the database path, user name included, before HealthService is built, and the host shows it in the Console. File it, fix it here, or leave it?"
    resolution: human
    class: product-preference
    chosen: "File CONSOLE-STARTUP-DB-PATH, with no change in MEU-123; filed at plan time through model.add_issue (C:/Temp/av-kit/s54-plan-register-file.txt) and placed by D-379"
    source_tag: Human-approved
    precedents: ["human-gate-decision.md — D-377 brief and Mat's ruling", "packages/infrastructure/src/avkit_infra/database/engine.py:85 — the line", "packages/api/src/avkit_api/wiring.py:135, :205 — engine before HealthService", "C:/Temp/av-kit/s54-plan-startup-stdout-probe.txt — one line holds the folder", "Session 52 D-337 — CONSOLE-HOME-SCRUB-SHORT-FORM filed; Session 53 D-354 — a neighbour fixed in place"]
    research: { engine: pomera_web_search (tavily), sources: ["https://www.structlog.org/en/stable/console-output.html", "https://www.structlog.org/en/stable/api.html"] }
    reasoning: "Session 50 RULE-1 says a raw value reaching the Console is fixed in the row or raised. It is outside both issues, and the precedents point both ways, so the call was Mat's. Filing raises it, as RULE-1 requires, and the plan needs no recheck."
    human_message_reference: "USER_EXPLICIT 2026-11-07 'All recommendations accepted. But also file, and assign into session groupings So next sessions, can handle the new issues.'"
  - id: D-378
    stage: planning
    question: "Plan round 1 cost 8,541,302, more than 5.25M. What token budget does the execution loop open with?"
    resolution: human
    class: product-preference
    chosen: "The execution default, 21,000,000; H1-7 runs begin with no --token-budget"
    source_tag: Human-approved
    precedents: ["tools/review_ledger.py:100-106 — TOKEN_BUDGETS execution 21,000,000", "Session 53 — execution 10.3M plus 2.6M", "Session 52 — execution 15.0M plus 4.7M", "Session 52 RULE-3 — compare with the last comparable round"]
    research: { engine: none, sources: [] }
    reasoning: "Mat's brief makes the budget Mat's call once round 1 passes 5.25M, and Mat took the recommendation."
    human_message_reference: "USER_EXPLICIT 2026-11-07 'All recommendations accepted. But also file, and assign into session groupings So next sessions, can handle the new issues.'"
  - id: D-379
    stage: planning
    question: "Where does CONSOLE-STARTUP-DB-PATH go in the session grouping?"
    resolution: autonomous
    class: two-way
    chosen: "P3, a rider in MEU-124 (Session 55 download-received-quality): engine.created logs no raw path, with a Red that build_services into a folder with a marker name prints no stdout line holding it"
    source_tag: Local Canon
    precedents: [".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md:278 — D-242, a rider needs a session already in the file", ".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md:199 — D-361, Session 55's first rider", "docs/build-plan/06-gui.md:1592 — MEU-124 adds its column through COLUMN_MIGRATIONS, in the package that holds engine.py", "tests/integration/test_sqlite_uow.py:165-172 — the real-SQLite tests build through create_sqlite_engine and init_schema"]
    research: { engine: none, sources: [] }
    reasoning: "Session 55 is the last code session before rc.2 and the only one left in avkit_infra/database/, and its column tests run create_sqlite_engine, the function that logs the line. That stretches D-242 from the file to its package, which is why it is stated here. The debt queue would ship the user name in rc.2's Console at every start. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-07 'All recommendations accepted. But also file, and assign into session groupings So next sessions, can handle the new issues.'"
  - id: D-380
    stage: planning
    question: "Where does CONVERT-CUT-ENCODER-LABEL go in the session grouping?"
    resolution: autonomous
    class: two-way
    chosen: "P4, last in current-focus's debt queue, not a rider; it needs a build, so it lands before Session 57 if wanted"
    source_tag: Local Canon
    precedents: [".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md:278 — D-242, a rider needs a session already in the file", ".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md:81 — D-363, a fix whose files no remaining session works in goes to the debt queue", "CONVERT-EXTRACT-ENCODER-LABEL — the Extract half of the same label defect, filed P4"]
    research: { engine: none, sources: [] }
    reasoning: "Sessions 55 to 57 work in downloads, the light theme and the release; none edits services/conversion.py or the media adapter, so a rider would chain unrelated work into a session (D-250's test). The debt queue keeps it visible for a build before rc.2. It is P4, as the Extract half was. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-07 'All recommendations accepted. But also file, and assign into session groupings So next sessions, can handle the new issues.'"
```

## Research References

- `docs/build-plan/08-video-conversion.md:172-181`, `:462-478`, `:593-605` (the Extract table, the wire schemas and the residual contract).
- `.agent/context/known-issues.yaml` (`CONVERT-EXTRACT-STREAM-INDEX-MISMATCH`, `CONVERT-EXTRACT-ENCODER-LABEL`), and the grouping file §1 `:26`, §3 `:192-194`, §6 `:254` and §8 `:278`, `:286`, `:299`, as they read after this plan's placements (D-379, D-380).
- FFmpeg's stream specifiers: `a:N` selects the Nth audio stream, measured on the pinned build (`s54-plan-ffmpeg-fixture-probe.txt`).
- Session 53's plan, task and scripts (`docs/execution/plans/2026-11-07-transcript-metadata/`), and Session 50's reflection.

## Planning receipts

- `C:/Temp/av-kit/s54-plan-ffmpeg-fixture-probe.txt`: FFmpeg n8.1.3-27-g8dca1586f4-20261031 builds both fixtures offline, picture first; `a:0` on one track gives `aac`; `a:1` on one track exits 4294967274 ("Error opening output files: Invalid argument"); on two tracks `a:0` is `aac`, `a:1` is `ac3` and `a:2` fails.
- `C:/Temp/av-kit/s54-decision-issue-probe.txt`: both flags give the grouping's rows and D-227; `CONVERT-EXTRACT-ENCODER-LABEL` adds nothing.
- `C:/Temp/av-kit/s54-plan-probes.txt`: Session 51 RULE-2 register keys and the line endings above. The register's SHA-256 was `c8089183…` (367,022 B, written 18:40 by the other session); row 4 reads it again for `--expect-sha256`.
- `C:/Temp/av-kit/s54-plan-meu-stats.txt`.
- `C:/Temp/av-kit/s54-uv-offline-dry-run.txt` (Session 52 RULE-2): `uv sync --frozen --offline --all-packages --dry-run` exits 0, 122 packages, "Would make no changes". This plan relies on no cached wheel, model or file except the pinned FFmpeg pair, which is already on disk.
- `C:/Temp/av-kit/s54-plan-uv-locked-offline.txt`: CI's `uv run --locked --no-sync` form runs with `UV_OFFLINE=1` and exits 0.
- `C:/Temp/av-kit/s54-plan-deselect-module-probe.txt`: `--deselect` with a module path deselects all 20 of that module's tests, so `CI_DESELECT` can name the module.
- `C:/Temp/av-kit/s54-plan-task-lint.txt`: `lint_task_contract.py` on `task.md`, rerun after round 1's amendments.
- `C:/Temp/av-kit/s54-plan-ledger-begin.txt`: the plan loop opened with 3 rounds and 10,500,000 tokens, and the citable ACs.
- `C:/Temp/av-kit/s54-plan-review-validate.txt` and `s54-plan-review-state.json`: round 1's report validated under `C:/Temp/av-kit` before the byte-for-byte copy.
- `C:/Temp/av-kit/s54-plan-startup-stdout-probe.txt`: `build_services` into a marker-named folder prints one line holding it, `engine.created` (D-377).
- `C:/Temp/av-kit/s54-plan-triage-add-help.txt`: `issue_triage.py add` takes no related list or priority, so the filing under Mat's ruling ran through `model.add_issue` and `model.save` instead.
- `C:/Temp/av-kit/s54-plan-register-file.txt`: `CONVERT-CUT-ENCODER-LABEL` (P4) and `CONSOLE-STARTUP-DB-PATH` (P3) filed `open`, with `related`, `meu_links`, `resolution_path` and the D-373/D-380 and D-377/D-379 `decision_log` entries. The register then held 121 issues, 378,072 B. A diff against the pre-edit copy (`s54-ki-roundtrip.yaml`) shows only the appended entries and four of D-361 to D-363's grouping cites, moved by the inserted lines (Session 51 RULE-3).
- `C:/Temp/av-kit/s54-plan-pin-cut-cite.txt`: `CONVERT-CUT-ENCODER-LABEL`'s `conversion.py:486-495` cite now names `39ac742`, because row 2 edits `_dispatch` and row 4's `issue-resolve.py` may not change `root_cause`. The diff against `s54-ki-before-pin.yaml` is that line and the issue's `notes`; the register is 378,187 B, and `s54-plan-issues-render-2.txt` renders and checks it. Row 4 reads the SHA-256 again for `--expect-sha256`.
- `C:/Temp/av-kit/s54-plan-issues-render.txt` and `s54-plan-meu-render.txt`: `issue_triage.py render --check` and `meu_status.py render --check` exit 0 after the filing and placement.
- Step 4A GUI check (`gui-refs-not-shipped`, items 3 and 5): no control, label, layout, colour or icon changes. The `a:N` label shows a different number for new rows, and the encoder segment is absent for Extract rows, both through unchanged code.
- Not run at plan time: any suite, build or smoke. Row 0 runs them.

## Validation stage contract

- **Static:** `pyright packages/`, `ruff`, the UI typecheck and lint, `lint_task_contract.py`, the scope-paths check and the `red-check.py` selftest.
- **Targeted:** each Red and Green row's own files, with `red-check.py` reading every Red receipt.
- **Fresh full:** the whole Python, UI and MCP suites, the UI and MCP builds, the OpenAPI guard, the two render checks and `ci-collect`, in the session gate.
- **Runtime:** the real-FFmpeg module on the pinned binary, and the convert queue E2E spec on the built app.
- **Identity:** `identity.py` binds `HEAD`, the work tree minus `PROJECT_ARTIFACTS`, the runtime and the pinned FFmpeg pair. The gate records it before and after, and H1-6b checks each handoff's evidence against it.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
