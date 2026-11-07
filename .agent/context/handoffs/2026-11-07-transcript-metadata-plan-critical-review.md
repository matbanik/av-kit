---
date: "2026-11-07"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-07-transcript-metadata/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s53-plan-2026-11-07-transcript-metadata"
round: 2
---

# Critical Review: 2026-11-07-transcript-metadata

> **Review Mode:** `plan` · **Verdict:** `approved` · **Ledger round:** 1

## Scope

Reviewed the working-tree implementation plan, task and human-gate decision brief for Session 53 / MEU-122 against the registered intent, the four named issue records, the service-layer contract, current production callers, affected fakes/tests, installed yt-dlp source, and the Session 52 scripts designated for copying. HEAD is `9093d957f1fd3225cec42712137acf021d6605bf`.

Claude Code/Anthropic authored the plan. This review is by Codex/OpenAI and is independent. No repository files were edited. No product test runner, app, session gate, network request or YouTube request was run. All reviewer-created files are under `C:/Temp/av-kit`. The coordinator owns saving the report to the canonical repository path.

**Intent anchor:** Session 53 makes a transcript's files, compiled headings, contents and "Last:" label show each video's title, stored per item from the flat enumeration `add_channel` already runs, with the video ID as the fallback only and no extra request per video. It makes the job's channel name the channel's, not the tab's or the playlist's title, falling back to today's title, and leaves the output folder and compiled volume names unchanged for an existing channel URL.

**Intent achieved:** yes, as a plan. This does not certify an implementation or live YouTube behavior.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

No High or Critical delivery finding, missing required deliverable, impossible dependency, or demonstrated materially false-passing guard was found. The two clarifications below do not block the metadata objective.

## Review questions

Paths below are relative to `P:/av-kit`; `plan` means this target's `implementation-plan.md`.

| Question | Assessment |
|---|---|
| **Q1 — Done** | Accepted. `LISTING` carries entry titles; `STORED_TITLE` persists them before fetching; `TITLE_KEPT` supplies the same chosen title to the item and raw front matter. Compilation already reads `item.title or item.video_id` for both Contents and `##` headings (`services/transcript.py:364`, `:368`). `_aggregates` then exposes the stored title after processing. The plan explicitly keeps ID filenames and does not backfill old jobs (`plan:97-103`). Real-title punctuation is addressed by `QUOTED_FRONT_MATTER` and `ESCAPED_CONTENTS`; renderer-specific anchors remain a stated limitation, not a lost title. |
| **Q2 — LISTING** | Accepted. The complete `extract_video_ids` census in `packages` and `tests` finds the transcript service, coordinator, protocol, adapter, one returning fake, two raising fakes and the adapter test. Downloads use `extract_info`/`PlaylistInfo`; they do not call this method. Row 1 changes the returning `DownloadYouTube` fake and amended 6.4 expectation; the raising fakes can keep raising. `PlaylistInfo` and its download mapper stay unchanged (`plan:152-159`, `task.md:49-50`). |
| **Q3 — adapter and shapes** | Accepted for the design. `_tab.py:145`, `:377`, `:687`, `:806` substantiate flat entry titles and page-level channel/owner. `_video.py:4488`, `:4532` substantiate the single-video channel/uploader mapping. Cleaning followed by the same `TEXT_CLEAN` invariant prevents new title/channel validation rejection; missing or non-string fields become `None`. First-ID deduplication and nested-playlist title suppression preserve the existing video selection. Source expectations are honestly distinguished from live measurements. The bare-channel generalization needs the non-blocking qualification below. |
| **Q4 — service and slug** | Accepted for supported production-created jobs. Today `add_channel` stores `root / slugify(info.title)` and the same title as `channel_name` (`services/transcript.py:157-174`). The proposed folder expression preserves that exact source; volume/zip naming from `output_dir.name` then preserves both old and new filenames while the displayed channel changes. Settings changes do not rewrite persisted job paths. This equality is not a guarantee for arbitrary hand-edited database paths; there is no supported production path-update operation in the inspected call chain. Tuple slicing preserves `playlist_end`; duplicate-URL `ConflictError` still occurs before either extraction call (`:146-154`). AC-122.11 exercises the differing display-name case and old-name case. |
| **Q5 — TITLE_KEPT** | Accepted. `current.title or result.title` fixes the overwrite at `services/transcript.py:611` and supplies the same value to the raw writer. Retry uses `replace` without changing `title` (`:293-304`); requeue retains items. An old item with `None` still uses the transcript adapter's ID fallback. Existing already-stored IDs are intentionally retained rather than migrated (`plan:98`, `:186`). |
| **Q6 — text and Last** | Accepted. JSON string quoting is suitable for the front-matter values; the existing `_markdown_body` delimiter split still extracts the transcript body. Backslash-first escaping of backslashes/brackets protects Contents link syntax. Volumes and the zip consume the same files; the UI consumes API text, and no other front-matter parser was found. `LAST_TITLE_PROCESSED` changes only the title aggregate. AC-16.2's `Latest` fixture has `processed_at`, even though its status is Pending (`api_fakes.py:129-140`), so it remains selected. The only UI label consumer still gates on Processing (`TranscriptPage.tsx:128-129`). |
| **Q7 — raw values** | Accepted. The named storage/file/API surfaces account for the new values. Transcript failure logging uses IDs and sanitized reasons; `_YtDlpLogger` uses a `message` field that `HealthService._process` removes before downstream rendering (`health.py:208-235`). SQL parameter text is a real additional path through `log_unhandled_error`; the proposed `SQL_PARAMS_HIDDEN` change closes it. An independent failing-insert probe confirmed the marker is visible today and absent with `hide_parameters=True`, both before and after `console_field`. The exact-string census found no dependency on the removed SQL parameter text. The existing slug-in-filesystem-error path is raised to Mat, not hidden as a residual. |
| **Q8 — briefs** | Accepted as decision briefs, without ruling on Mat's preferences. Both recommendations have genuine do-nothing options. Row 0a defaults to source-only recorded evidence and cannot invoke its described live branch without the D-353 amendment. Live absence checks guard the essential title/channel assumptions; missing fallback fields remain supported behavior. A bare-channel observation informs the separately reserved video-selection question rather than silently flattening it. D-354 describes a real multi-tab defect, with the single-tab qualification below. No claim of fresh external research or live measurement is made by this review. |
| **Q9 — Red and guards** | Accepted as executable test designs. New-name `hasattr` assertions precede construction/use, so missing types produce assertions rather than import failures. The copied checker rejects required missing-name failures; its boundary-aware matching distinguishes `_1` from `_10` (`red-check.py:211-212`). Row 1 selects only the new ACs and amended 6.4; the fake's lazy import therefore does not break unrelated tests before Green. AC-122.6 is correctly not required to fail. AC-122.12 reads counters actually incremented by the fake port; extra uncached per-video extracts change them, and download sets `last_options`. AC-122.16 includes a Console-field control reaching all three captures and a marker-positive raw file. AC-122.11 checks exact folder, volume and zip names with unequal source/display names. No vacuous guard was demonstrated. Future Red/Green receipts remain implementation work. |
| **Q10 — order and safety** | Accepted with the package-sync clarification below. Execution remains human-gated, with a distinct D-353 amendment for live YouTube measurement. Tests use fake enumeration/captions; live audit is omitted. The identity copy binds product code, tests, dependencies, relevant canon, scripts and pre-gate register changes; excluding rolling plan/status/closeout prose does not remove the independently bound gate script or product inputs. The Files Modified plus project-file inventory includes the planned edits and renders needed by `scope-paths`. No instruction requires a wholesale newline conversion; the per-row byte measurement and newline-preserving edit contract must be honored. Script absence before their creation rows is not a defect. |

## Non-blocking clarifications

- **Bare-channel nesting is conditional on multiple results.** Qualify `plan:170` and `human-gate-decision.md:42`: `_tab.py:2416-2417` returns a sole tab directly. A channel with only one available Shorts/Streams result need not yield a nested playlist. This narrows D-354's affected population; it does not invalidate the multi-tab bug or require changing this session's video-selection policy.
- **Frozen sync is not offline sync.** `plan:329` / `task.md:46` prescribe `uv sync --frozen --all-packages`; installed CLI help says `--frozen` prevents lock updates, while `--offline` disables network access. State whether package fetching is included in Mat's execution authorization, or use offline sync/run settings to honor the no-download wording at `task.md:15`. No package sync was run here. This is not a demonstrated bypass of the human execution gate or a metadata-delivery failure.

## Checklist Results

The checklist rates plan readiness, not unrun implementation tests.

| Check | Result | Procedure / evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Compared scope, row dependencies, AC ownership and Green changes in both working-tree documents. |
| PR-2 Not started | pass | Implementation rows remain unchecked; tracked diff is empty. New types, tests and plan-local scripts are scheduled execution deliverables. |
| PR-3 Task contract | pass | Read task rows and their named deliverables, owners, validation commands and statuses. |
| PR-4 Validation realism | pass | Traced each targeted selection to existing runners/fakes and each future script to its creation row/source copy. No material unrunnable gate found. |
| PR-5 Source-backed planning | pass | Compared D-223/D-224 and the service-layer residual with D-346 through D-357 and the FIC. |
| PR-6 Review readiness | pass | One MEU, explicit handoff and rolling-review targets. Round-2 correction census is inapplicable in round 1. |
| PR-7 Scope discipline | pass | No required metadata behavior is silently deferred. Migration, per-video channels, anchor fidelity and adjacent video-selection behavior are explicitly bounded. Live choice remains Mat's. |
| PR-8 Control reachability | pass | Inspected actual counter producers, title writers, Console processing/control, Red parser and filename outputs as described in Q9. |
| PR-9 Single-statement contracts | pass | Named contracts govern their AC/row references; no competing operative spelling with materially different behavior found. |
| Product suites / live shapes | n/a | Deliberately not run in this read-only plan review; not implementation evidence. |

### Decisive evidence

```json
{"schema_version":"evidence.v1","check_id":"review-plan-source-trace","procedure":"Read the target plan, task and decision briefs; trace the title/channel/slug/API/Console call chains and inspect the installed yt-dlp branches and designated Session 52 checker sources; compare the four issue records by id and build-plan/03-service-layer.md:663-675.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"Session 53 MEU-122 plan, Q1-Q10 and PR-1 through PR-9","phase":"review","exit_code":null,"result":"pass","tested_state":"9093d957f1fd3225cec42712137acf021d6605bf plus the working-tree 2026-11-07-transcript-metadata plan folder read in round 1","output":"Title survives creation/fetch/retry/compilation/API; download callers remain unchanged; source/display slug separation preserves supported job names; meaningful Red and counter/Console/slug guards are specified. No material delivery defect found. Two non-blocking qualifications are recorded above."}
```

```json
{"schema_version":"evidence.v1","check_id":"review-offline-probes","command":"$env:RECEIPTS_DIR='C:/Temp/av-kit'; $env:HF_HUB_OFFLINE='1'; $env:PYTHONDONTWRITEBYTECODE='1'; rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s53-review-probe.py","cwd":"P:/av-kit","scope":"Current markdown-body parser, proposed JSON quoting, service-created slug invariant and SQL parameter hiding; scratch database only","phase":"review","exit_code":0,"result":"pass","tested_state":"9093d957f1fd3225cec42712137acf021d6605bf; local installed packages; no product edits","output":"PASS: proposed JSON front matter round-trips; current _markdown_body preserves the body; folder-name slug equals previous slug for ordinary service-created paths at either root. PASS: current project engine: marker in exception=True, marker in console_field=True. PASS: proposed hide_parameters=True: marker in exception=False, marker in console_field=False. UV_OFFLINE explicitly true: False. Repository uv.toml exists: False. No network requests or product test runners invoked."}
```

```json
{"schema_version":"evidence.v1","check_id":"review-uv-command-semantics","command":"rtk proxy uv sync --help","cwd":"P:/av-kit","scope":"Meaning of baseline sync flags; help only","phase":"review","exit_code":0,"result":"pass","tested_state":"Installed uv CLI during round 1","output":"--frozen: Sync without updating the uv.lock file. --offline: Disable network access [env: UV_OFFLINE=]. --no-python-downloads: Disable automatic downloads of Python [env: UV_PYTHON_DOWNLOADS=never]."}
```

```json
{"schema_version":"evidence.v1","check_id":"review-head","command":"rtk proxy git rev-parse HEAD","cwd":"P:/av-kit","scope":"Review baseline","phase":"review","exit_code":0,"result":"pass","tested_state":"9093d957f1fd3225cec42712137acf021d6605bf","output":"9093d957f1fd3225cec42712137acf021d6605bf"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-tracked-diff","command":"rtk proxy git diff --name-only","cwd":"P:/av-kit","scope":"Tracked working-tree changes at review closeout","phase":"review","exit_code":0,"result":"pass","tested_state":"9093d957f1fd3225cec42712137acf021d6605bf","output":"No output: no tracked working-tree differences. The uncommitted plan folder was read directly, not inferred from git diff."}
```

The SQL text-dependency census was `rtk proxy rg -n -F -e '[parameters:' -e 'hide_parameters' -e 'SQL parameters hidden' packages tests ui/tests mcp-server/tests`; exit **1**, no matches. This is an observed empty search, not a product-test pass. Additional numbered reads and the full method/consumer census are retained in `C:/Temp/av-kit/s53-review-*.txt`; decisive observations are embedded above.

## Verdict

`approved` — the plan delivers the registered metadata intent. No blocking findings. Apply the two brief clarifications without a new review cycle solely for wording. D-353 and D-354 remain Mat's decisions; approval does not authorize execution, live requests, commits or pushes.

Live title/channel availability is unmeasured, the caption IP-block issue remains open, and planned implementation tests have not run. These are accurately disclosed limits, not fabricated passes.

🕐 Completed: 2026-11-07 13:44 (EST)


## Recheck (Round 2)

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|

Round 1 had no findings.

### Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

No evidence-backed High or Critical finding. This recheck covers only the D-353/D-354 amendment, D-358 and their affected contracts; round 1's accepted work stays accepted. Claude Code/Anthropic authored the plan; Codex/OpenAI reviewed it independently. No repository file was edited, and no network request, YouTube call, product test runner, app or session gate was run.

### R1 — FLAT_TABS and yt-dlp

Accepted. Installed `_tab.py:2355-2384` chooses Videos plus available Streams/Shorts, and `:2403-2426` returns the full tab playlists, or the sole tab directly. `_extract_from_tabs` supplies each tab's video enumeration (`:665-677`). One-level flattening therefore removes the wrapper introduced for multiple tabs. A playlist inside that enumeration is not another automatically selected upload tab; recursively resolving it would widen the selected set and could add requests. Under `extract_flat=True`, playlist links can also remain `url` entries (`:412-417`); treating those as today is an explicit boundary, not a promise to recursively traverse arbitrary playlists.

The adapter calls `extract_info` with default processing (`adapter.py:388-405`). `YoutubeDL.py:2088-2098`, `:2166-2180` processes nested playlists and returns ordinary lists even from generators/lazy extractor inputs. The adapter does not enable lazy/discard options. Thus requiring a tab's `entries` to be a list is valid on this path. `PlaylistEntries.get_requested_items` reads `playlistend` on every playlist (`utils/_utils.py:2464-2478`), including the outer tab list. Offline probes through actual yt-dlp processing confirmed list materialization and limits 1, 2 and 3 at both levels; the service's post-flattening slice caps the job total (`plan:185`, service `:152-154`). D-358 promises an upper bound, not that every tab is visited when the outer limit excludes it. The supplied live receipt independently shows three tab lists, each with three video entries.

### R2 — The resulting job and downloads

Accepted. `FLAT_TABS` excludes a tab's own ID/title even when it has no list, skips inner playlists and retains the first valid occurrence of each video across tabs (`plan:128`, `:158-161`). Titles belong to the video entries; missing/non-string titles remain the accepted `None`/ID fallback. First occurrence wins even if a later duplicate has a title that the first lacks; this does not invent a stronger title-recovery contract. Direct Videos-tab, playlist and single-video mappings retain round 1's accepted behavior. The outer dict's cleaned `channel`, then `uploader`, supplies `CHANNEL_SOURCE`; `info.title` still supplies `SLUG_SOURCE` (`plan:160`, `:185-190`). Duplicate URL rejection precedes both extractions (`transcript.py:146-151`).

The download-side description is true: `_playlist_from_info` delegates to unchanged `_unique_preserve_ids` (`adapter.py:119-134`, `:203-214`). The AC-122.18-shaped synthetic dict still maps to `[CHANNEL]` there. `extract_info` and `PlaylistInfo` stay unchanged, and `DownloadYouTube`'s changed enumeration return serves transcript callers only. The flattening cannot reach a download through this call chain. The existing download bug is raised to Mat by the Out of Scope row (`plan:311`), as instructed; it is not a blocker or a newly authorized issue filing.

### R3 — AC-122.18 and AC-122.3

Accepted as test designs. AC-122.18 (`plan:260`) specifies exact order and per-video titles, the duplicate retaining its Videos title, exclusion of channel/tab/inner-playlist identifiers or titles, the tab without entries contributing nothing, and the top-level channel. The offline model produced exactly `a/Title A, b/Title B, c/Title C`; today's mapper instead produced the channel ID. Row 1 requires initial `hasattr` assertions for the new types, so the absent type fails by assertion before access/import, as the checker demands (`task:49`; designated checker `red-check.py:261-269`). The observed initial assertion fails today as designed. This is plan-readiness evidence, not a claimed pytest Red/Green run.

Row 1's `-k "ac_122 or ac_6_4_extract_video_ids_playlistend_ctor"` selects `test_ac_122_18_...`, and its new `--require test_ac_122_18` is compatible with the checker's boundary matcher (`:211-212`). Row 2 runs the entire integration file after implementing `FLAT_TABS`. AC-122.3 still independently requires the missing/non-string title and channel/uploader fallbacks (`plan:245`); moving nesting to .18 does not remove those cases.

### R4 — Measurement and later requests

Accepted for this amendment and the actual receipt. The script declares the four authorized URLs (`measure-shapes.py:39-45`), uses the adapter's `_base_opts`/`_run_extract` with flat extraction, `playlistend=3`, no cookie configuration and `download=False` (`:94-102`), and records field presence/counts rather than title/channel/ID values. A raised block is recorded as `not run` and has no application retry (`:103-111`). A synthetic blocked call confirmed one invocation and that result. The installed YouTube retry paths specifically do not retry HTTP 403/429 (`_base.py:1001-1011`, `:1342-1346`); the script does not disable every yt-dlp retry for other transient errors. It is not a universal no-retry transport configuration.

The new nested-tab checks detect missing entry lists or missing inner IDs/titles, and a synthetic missing-list case was rejected (`measure-shapes.py:137-149`). The checker is not an exhaustive assertion of every table cell: its direct-single-tab bare-channel branch (`:134-136`) can return zero problems with a missing entry title. The offline probe demonstrated that limitation. The accepted ID fallback handles that absence, and this run actually measured the nested shape with all nine IDs/titles present. It supplies no evidence of a materially missing deliverable or a contradiction in the observed receipt. `s53-shapes.txt:20-35` supports the factual presence/count claims at `plan:177`; it cannot establish semantic title accuracy from presence alone. The independent `--recorded` run exited 0 with seven source checks found and `live: not measured`. Only completed row 0a contains `--live`; later tests use fakes, the live audit is excluded, and no later row authorizes another YouTube request (`plan:357`, `:378`; `task:38`, `:47`).

### R5 — Rulings, records and carry-through

Accepted. Both Decision blocks reproduce Mat's supplied words exactly (`human-gate-decision.md:40-44`, `:76-80`). D-353 records human/external permission and taking the recommendation; D-354 records human/product preference and taking the alternative, with `Human-approved` tags and the actual message (`plan:477-498`). D-358 properly records an autonomous, reversible implementation choice derived from that human-approved direction (`:529-539`), without claiming Mat dictated each filtering detail.

WP-3, row 1 after both 0 and 0a, row 2, the infrastructure spec update, row 5's no-filing instruction, H1 AC coverage, the execution ledger prompt through AC-122.18/D-358 and H2's decision range carry the amendment forward (`plan:80`, `:220`; `task:49-54`, `:61-65`, `:70`). The changed adapter and existing integration-test file are inventoried. Two minor stale descriptions are clear from their operative successors: the boundary inventory at `plan:232` still says a nested playlist keeps its ID, and the integration-file inventory at `plan:291` omits .18 from its summary. `FLAT_TABS`, AC-122.18 and rows 1/2 unambiguously require the new behavior; these are correction notes only, not findings or reasons for another round.

### Observed evidence

```json
{"schema_version":"evidence.v1","check_id":"s53-r2-offline-probes","command":"$env:RECEIPTS_DIR='C:/Temp/av-kit'; $env:PYTHONDONTWRITEBYTECODE='1'; $env:HF_HUB_OFFLINE='1'; $env:PYTHONIOENCODING='utf-8'; rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s53-r2-probe.py","cwd":"P:/av-kit","scope":"Amended FLAT_TABS design, real installed yt-dlp playlist processing, unchanged download mapper, assertion-first Red design, measurement block and nested-negative branches","phase":"review","exit_code":0,"result":"pass","tested_state":"9093d95 and the working-tree Session 53 amendment read for ledger round 2; installed yt-dlp 2026.10.26; synthetic input only","output":"PASS: AC-122.18 synthetic contract yields a,b,c with own titles; first duplicate wins; missing tab entries and inner playlist contribute nothing; current download mapper still yields CHANNEL. PASS: proposed initial hasattr assertion fails today by AssertionError. PASS: row 1 selection and --require include .18. Actual yt-dlp generator processing returned ordinary lists; playlistend 0/1/2/3 gave outer tabs 3/1/2/3 and sliced job totals 15/1/2/3. Blocked measurement: one synthetic call, not run, no retry, flat, playlistend 3, no cookies, download=False. Missing nested entries list was detected. LIMIT: direct-tab missing title is not rejected by the measurement checker; accepted ID fallback remains. Network sockets denied; no test runner or repository write used."}
```

```json
{"schema_version":"evidence.v1","check_id":"s53-r2-recorded-shapes","command":"$env:RECEIPTS_DIR='C:/Temp/av-kit'; $env:PYTHONDONTWRITEBYTECODE='1'; $env:HF_HUB_OFFLINE='1'; $env:PYTHONIOENCODING='utf-8'; rtk proxy .venv/Scripts/python.exe -B docs/execution/plans/2026-11-07-transcript-metadata/measure-shapes.py --recorded","cwd":"P:/av-kit","scope":"Installed yt-dlp version and the script's seven cited source strings; no request","phase":"review","exit_code":0,"result":"pass","tested_state":"Working-tree measure-shapes.py; installed yt-dlp 2026.10.26","output":"yt-dlp version: 2026.10.26 (expected 2026.10.26); all seven cited source checks found; live: not measured; measure-shapes: 0 problem(s)."}
```

The earlier live receipt was inspected, not rerun. Implementation Red/Green, full suites and runtime behavior remain unrun by this reviewer. Completion-preflight was consulted for scope: this is a completed independent plan recheck, not a claim that the still-unchecked implementation task is done. Only scratch review artifacts were written.

### Verdict

`approved` — the amendment implements the authorized tab flattening and preserves the registered metadata intent. **Intent achieved: yes, as a plan.** No blocking findings. The measurement limits and two stale inventory descriptions above do not require another review round. Complete rolling report: `C:/Temp/av-kit/s53-plan-review-round-2.md`; the coordinator owns canonical saving and ledger recording.
