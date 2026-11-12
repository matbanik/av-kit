---
project: "2026-11-12-youtube-client-runtime"
date: "2026-11-12"
source: ".agent/context/grouping/2026-11-10-download-reliability-session-grouping.md#session-66--youtube-client-runtime-meu-140-meu-141--p2"
grouping_source: ".agent/context/grouping/2026-11-10-download-reliability-session-grouping.md"
meus: ["MEU-140", "MEU-141"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: YouTube client choice and JS runtime (Session 66)

> **Project:** `2026-11-12-youtube-client-runtime`
> **Build plan:** `docs/build-plan/02-infrastructure.md` §YouTube client fallback (residual) (`:576-585`, anchor `youtube-client-fallback-residual`, MEU-140) and §yt-dlp JS runtime (residual) (`:589-598`, anchor `ytdlp-js-runtime-residual`, MEU-141). Distribution rules: `docs/build-plan/07-distribution.md:33` (500 MB disk target) and `:159-164` (ffmpeg probe order), `:444` (installer size check).
>
> **Source request.** On 2026-11-10 Mat asked for the download comparison report's findings to be filed and grouped ("follow the process, file them and add to session grouping"; triage D-529 and D-530, grouping D-535), and ruled D-539 A and D-540 A ("A"). This is the grouping's second session (Sessions 65 to 67, MEU-137 to MEU-142). Done comes from the two spec sections: each rule holds with a behaviour test, and the two issues close with that evidence.
> **Known issues:** this session closes `DOWNLOAD-CLIENT-PIN-MISSES-WORKING-CLIENT` (`known-issues.yaml:4683`, D-529) and `YTDLP-NO-JS-RUNTIME` (`:4724`, D-530). `DOWNLOAD-MP3-NOT-CONVERTED` is Session 67's and is not touched. The comparison report `docs/proposals/2026-11-10-download-logic-divergence-report.md` is never opened; the plan needs no fact that only it holds (D-653).
> **Status:** `draft`, with the gate held on 2026-11-12. `plan_to_exec_gate: human`. Mat ruled the three gate decisions on 2026-11-12 ("all recommendations are accepted"): D-640 A (yt-dlp plus `yt-dlp-ejs==0.8.0` with a pin-match test), D-641 D (one session, no context-measured split) and D-642 A (the named fetches, each recorded with its SHA-256, and the live probes as a manual check, each brought to Mat first). The execution review budget is 37.5M tokens. Plan review round 1 (Codex) asked for changes, F1 to F5; they are corrected here and in `task.md`, and the correction log is in the rolling review. Round 2 found F1 to F5 fixed and one more port pin, F6 (`tests/unit/test_transcript_metadata.py:142-145`, AC-122.6); row 1 now moves it too. Round 3 approved the plan; rounds 4 and 5 re-issued that approval in the table shapes the closeout validator reads, and the canonical review passes `--approved-state-only` at round 5 of 5.

## Goal

**Goal anchor:** Session 66 lets yt-dlp choose its own YouTube clients, with one retry on today's cookie pin, and gives yt-dlp a JavaScript runtime and its challenge solver in dev and in the installed app. A download's first attempt sets no `player_client` in any cookie mode; a client-side failure retries once with `tv`, `web_safari`, `web`, and the Console shows each failed attempt. A video selector at a fixed height falls back to `/best`. The add-time extract uses the download's cookie and client options. Deno ships in the Windows installer and is found the way ffmpeg is (the setting, the bundled file, PATH); yt-dlp gets it through `js_runtimes`, the solver scripts ship in the backend, and Health names the runtime or says none was found and what that costs.

Seven things are missing today (`0553779`):

1. **The pin replaces yt-dlp's own client choice.** `_cookie_opts` (`packages/infrastructure/src/avkit_infra/youtube/adapter.py:513-536`) sets `COOKIE_EXTRACTOR_ARGS` (`:77-81`, `tv`, `web_safari`, `web`) with cookies and `SABR_EXTRACTOR_ARGS` (`:82-90`, `android`, `tv`, `ios`, hls and dash skipped) without them. gKcOjnDJfzk failed on both pins on 2026-11-10 and downloaded with yt-dlp's choice (register `:4683`).
2. **There is no retry.** `download` (`:594-652`) runs one `extract_info` and raises on the first `DownloadError`.
3. **The height selectors have no catch-all.** `_quality_selector` (`:136-144`) returns `bestvideo[height<=N]+bestaudio/best[height<=N]`, so a video with formats but none at or under the height fails.
4. **The add-time extract ignores the download's options.** `DownloadService.add_to_queue` (`packages/core/src/avkit_core/services/download.py:253-263`) calls `ExtractCoordinator.extract_info(url)` (`services/extract.py:34-50`), and the adapter's `extract_info` (`adapter.py:569-578`) uses `_base_opts` only: no cookies, no client options.
5. **No JS runtime is given.** No opts builder sets `js_runtimes`; yt-dlp's default (`{'deno': {}}`, `yt_dlp/YoutubeDL.py:740` in 2026.10.26) looks for `deno` on PATH, and Deno sits in `~/.deno/bin`, off PATH (`C:/Temp/av-kit/s66-plan-probes.txt`).
6. **No solver ships.** `packages/infrastructure/pyproject.toml:12` depends on plain `yt-dlp`; `yt_dlp_ejs` is not installed (`s66-plan-probes.txt`), and `packaging/avkit-backend.spec:23` collects `yt_dlp` only.
7. **Health is silent about it.** `DependencyHealth` (`packages/core/src/avkit_core/domain/health.py:40-51`) and `DependenciesOut` (`packages/api/src/avkit_api/schemas/health.py:46-54`) have no runtime row.

The session ends when the two sections hold with a behaviour test per rule, the two issues are closed with their evidence, the session gate's last line is `session-gate: all steps exit 0`, and MEU-140 and MEU-141 are `approved` after Codex approves (MEU-140 alone when the active set defers MEU-141 to Session 66b: under D-640 D, D-641 B or D-642 D, or under D-641 A past about half the context; §Plan-local scripts, `active-set.py`).

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (C:/Temp/av-kit/s66-plan-probes.txt, 2026-11-12). No payload is oversized: adapter.py, services/download.py, the health and settings layers and the packaging files were read by section."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`plan_to_exec_gate: human`, `.agent/context/harness.local.md` Claude Code block). Validation goes through `rtk proxy`:
  - receipts go under `C:/Temp/av-kit`, named `s66-*`;
  - `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`;
  - `TMP` and `TEMP` point at `C:\Temp\av-kit\s66\tmp` for the Python suite, because `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` is still open;
  - `ELECTRON_RUN_AS_NODE` is cleared before every UI and Electron run (the scripts clear it too).
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub` and any other worktree are left alone.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `s66-plan-canonical-2026-11-12-youtube-client-runtime` and `s66-execution-2026-11-12-youtube-client-runtime`.
  - Claude wrote the plan, so the reviewer is a different vendor. Caps: plan 3 rounds, execution 6. If Codex is unavailable or the ledger refuses a round, the fallback is Mat.
  - Each round is metered, and the coordinator tells Mat before dispatching.
  - Each rolling report is validated under `C:/Temp/av-kit` and then copied byte for byte to its canonical path, and the `--review-state-only` receipt is rebuilt there.
  - Reviewer prompts name the ledger vocabulary up front: D-640 to D-654, AC-140.1 to AC-140.12, AC-141.1 to AC-141.16, and the mechanism ids in §Single-statement contracts, with MEU-141's ACs and ids in scope only when `active-set.py meus` names it. They forbid opening `P:/av-kit/.mcp.json`, any `mcp-token.txt`, `~/.claude.json`, any `.env`, `.claude/settings.local.json`, anything under `.agent/fleet/hub` and `docs/proposals/2026-11-10-download-logic-divergence-report.md`, and write `<HOME>` for the home folder. When they ask for `tested_state`, they name `~/.config/git/ignore` and the path it hides, `.claude/settings.local.json` (Session 51 RULE-4). `## Findings` holds only the Findings table; probe tables go under another heading (Session 65 RULE-3). Each recheck carries the literal Prior Pass Summary with bare closure words (Session 52 RULE-1), names each prior finding by the review's own id (Session 53 RULE-3), and asks for a `### New Findings` table and bare words in its Recheck cells (`fixed`, `open`).
- **Never in these rows without Mat's words:** commit, push, a tag, release or upload, the live MCP audit, `--update-baseline`, or an `approved` verdict authored by the implementer. A network request runs only as D-642 names it, after Mat's words: no test and no suite row reaches YouTube or the network, and every yt-dlp test runs against a mocked `YoutubeDL`. A live probe never prints or stores a cookie value. Nothing touches the installed avkit MCP servers (no `mcp__avkit__*` tool is called), and no other program is stopped.

## Handoff Set

| MEU | Handoff | Chain |
|---|---|---|
| MEU-140 | `.agent/context/handoffs/2026-11-12-youtube-client-runtime-MEU-140-handoff.md` | first |
| MEU-141 | `.agent/context/handoffs/2026-11-12-youtube-client-runtime-MEU-141-handoff.md` | after MEU-140 |

Rolling reviews: `.agent/context/handoffs/2026-11-12-youtube-client-runtime-plan-critical-review.md` and `.agent/context/handoffs/2026-11-12-youtube-client-runtime-implementation-critical-review.md`.

## Work Packages and Context Lifecycle

| WP | Rows | Content | Context |
|---|---|---|---|
| WP-1 | 0 | Baseline: rulings, queue, shapes, dirty paths, anchors, base suites, selftests | shared |
| WP-2 | 1 | MEU-140's type-only names, every caller swept, and the two port signature pins moved (Session 53 RULE-2) | shared |
| WP-3 | 2a, 3 | MEU-140 Red and Green | shared |
| — | 3s | The split point. The coordinator records the context state in the MEU-140 handoff and writes `active-meus.txt` from D-640 to D-642 (`task.md` §Order and row 3s). Under a split, rows 4, 1b, 2b and 5 are `[B]` and the session goes to row 6 with MEU-140 alone; otherwise it goes on to row 4. The coordinator decides this from the rulings and never stops to ask. | — |
| WP-4 | 4, 1b | MEU-141 fetches under D-642 (the lock, Deno and its licence), then MEU-141's type-only names and the regenerated OpenAPI snapshot | shared |
| WP-5 | 2b, 5 | MEU-141 Red and Green, with the package build and the onedir smoke | shared |
| WP-6 | 6 | Spec text, register, status, grouping | shared |
| WP-7 | H1, H2 | Gate, handoffs, review, reflection, next prompt | compact_continue |

**MEU-142 does not ride with this session (D-651).** The grouping lets it ride if this plan comes out small (`:117`); it doesn't. Session 66 already carries a split flag, a package build and three network fetches.

## User Review Required

**Ruled before this plan (carried):** D-539 A and D-540 A (Mat, 2026-11-10, "A"). The plan carries both as written, with one exception D-640 asks Mat about.

**Open for Mat at the plan gate.** Each brief is in §Decision Log in full; the short form:

1. **D-640 — the solver dependency** `[one-way-door] [source-conflict]`. *Recommendation A:* depend on `yt-dlp` and `yt-dlp-ejs==0.8.0`, the version yt-dlp 2026.10.26 pins in its `default` extra, with a test that fails when the two disagree. *Why it is yours:* D-540's text says `yt-dlp[default]`, and that extra also brings `mutagen` (GPL-2.0-or-later), which `tools/generate_third_party_licenses.py:44` refuses (`GPL_ALLOWED = {"num2words"}`), plus `brotli`, `pycryptodomex` and `websockets`. *Do nothing:* keep plain `yt-dlp`, so no solver ships and MEU-141 can't close `YTDLP-NO-JS-RUNTIME`.
2. **D-641 — the split point** `[process]`. *Recommendation D, do nothing:* run both MEUs in one session with no context-measured split. Row 3s records the context state in the MEU-140 handoff and the session goes straight on, as your standing instruction of 2026-11-06 asks and as Session 65 ruled D-625. MEU-141 still moves to Session 66b if D-640 or D-642 is ruled D, because it can't ship then. *A:* split after row 3 if the session has passed about 50% of its context. *B:* split now; MEU-141 goes to Session 66b.
3. **D-642 — network** `[outward-facing]`. *Recommendation A:* allow, at execution, the fetches named in D-642's brief (the `yt-dlp-ejs` wheel through `uv lock` and `uv sync`, plus the `default` extra's other new packages if D-640 is ruled B or C, the Deno 2.9.8 Windows zip and its licence text from GitHub, and the installer build if electron-builder fetches), each recorded; and run the four live probes (gKcOjnDJfzk, one other public video, a members-only video and a logged-in account) as a recorded manual check after the gate, each brought to Mat before it runs. *Do nothing:* the plan runs offline, MEU-141's rows 4, 1b, 2b and 5 can't run (the solver and Deno aren't on the machine in a form the build can ship), MEU-141 moves to Session 66b, and the live measurements stay open as named manual checks.

**The gate.** Execution waits for Mat's explicit message. At the gate Mat sets the execution review budget (Session 60 RULE-5: the round 1 estimate twice plus one recheck).

**Token estimate.** Calibrated against Session 55 (plan 15,022,770 over 2 rounds; execution 11,637,446 in 1), Session 51 (plan 7,450,042 in 1; execution 8,724,472 in 1, with a package build and an onedir smoke) and Session 65 (plan 24,637,783 over 4 rounds; execution 16,649,211 over 2, at 13,389,317 and 3,259,894). This session is wider than Session 55 and carries Session 51's packaging, so:

- plan review: about 9M for round 1 and about 5M per recheck, so about 20M over 3 rounds;
- execution review: about 15M for round 1, so the loop opens at 37.5M (15M × 2 plus one recheck at about 7.5M, Session 58 RULE-4), unless Mat sets another figure.

**Word meanings.** *Attempt 1* is the first `YoutubeDL` run of a download or an add-time extract, with no `extractor_args`. *Attempt 2* is the one retry, with `COOKIE_EXTRACTOR_ARGS`. A *client-side error* is one the D-643 rule selects. *The runtime* is the Deno executable that `JS_RUNTIME_LOOKUP` returns. *The solver* is the `yt_dlp_ejs` package.

## Proposed Changes

### Single-statement contracts

Each mechanism id below is one statement. A row cites the id; a test names the AC.

| Id | Statement | MEU | File |
|---|---|---|---|
| `ATTEMPT_OPTS` | `_attempt_opts(options, attempt)` returns the cookie opts of `_cookie_opts` with no `extractor_args` for attempt 1, and with `extractor_args = COOKIE_EXTRACTOR_ARGS` for attempt 2, in every cookie mode. | 140 | `youtube/adapter.py` |
| `CLIENT_SIDE` | `client_side_error(text, sabr_matched)` decides in two steps over the whole case-folded text, every line of it. It is False when the text holds an `AGE_GATE_NEEDLES` needle, either bot-check needle of `FAILURE_CAUSE_NEEDLES` (`confirm you're not a bot` with a straight or a curly apostrophe), a `cookies` needle or a `write_failed` needle, whatever else the text or the log holds. Otherwise it is True when the text holds a `no_format` needle or `the page needs to be reloaded`, when `sabr_phrase(text)` matches, or when `sabr_matched` is True. Nothing else is client-side (D-643). | 140 | `youtube/adapter.py` |
| `RETRY_ONCE` | `download` runs attempt 1, and on a `DownloadError` that is not an age gate and is `CLIENT_SIDE`, checks `should_stop` (a stop raises `DownloadCancelledError`) and runs attempt 2 once; every other error is raised as today. | 140 | `youtube/adapter.py` |
| `ATTEMPT_LOG` | Each failed attempt that is followed by a retry logs one `youtube.attempt_failed` warning with `attempt`, `clients` (`default` or `tv,web_safari,web`), `cause` and `detail = scrub_line(first line)`; the final failure keeps Session 65's `download.failed` path, and the success line `youtube.download` gains `attempt` (D-644). | 140 | `youtube/adapter.py` |
| `SABR_ACROSS` | `DownloadResult.sabr_detected` is True when either attempt's logger matched a SABR phrase (D-645). | 140 | `youtube/adapter.py` |
| `CATCH_ALL` | `_quality_selector` for a height preset returns `bestvideo[height<=N]+bestaudio/best[height<=N]/best`; `Best`, `Lowest` and the audio selectors are unchanged. | 140 | `youtube/adapter.py` |
| `ADD_OPTS` | `add_to_queue` builds `DownloadOptions` from its own arguments and the cookie settings with the helper `_options_from` uses, and passes them to `ExtractCoordinator.extract_info(url, options=...)`; the port's `extract_info` gains `options: DownloadOptions \| None = None`; the coordinator forwards `options=` only when it is given, so the transcript path's call and its fakes (`tests/unit/test_transcript_flat_extract.py:24`) stay as written; with options the adapter runs the same `ATTEMPT_OPTS` and `RETRY_ONCE` sequence (D-646). | 140 | `services/download.py`, `services/extract.py`, `ports/youtube.py`, `youtube/adapter.py` |
| `ADD_CACHE_KEY` | `ExtractCoordinator`'s info cache key is `(url, flat)` without options and `(url, flat, mode, browser, profile, cookie_file)` with them. | 140 | `services/extract.py` |
| `DENO_SETTING` | `("downloader", "deno_path")` is a `string` setting with default `""`, last in the downloader namespace, mirrored in `SettingsPutIn`, the MCP settings schema and leaves, and the UI settings schema (D-647). | 141 | `services/settings.py`, `schemas/settings.py`, `mcp-server/src/toolsets/settings.ts`, `settings-schemas.ts` |
| `AUDIT_INPUT` | The MCP audit's `ISOLATION_INPUT_KEYS` names `downloader.deno_path` beside `ffmpeg_path` and `cookie_file_path`, so `isolationKeys` treats it as an input and never redirects it to an output folder (`PATH_LIKE` at `classify.ts:274` matches `deno_path`). | 141 | `mcp-server/scripts/audit/classify.ts` |
| `JS_RUNTIME_LOOKUP` | `JsRuntimeLocator.resolve()` returns the first of: the setting's file, the bundled file, `shutil.which("deno")`, as `JsRuntime(name="deno", path, source)` with `source` in `setting`, `bundled`, `path`, else None; the setting is read at every call, and every filesystem call on it sits inside the error mapping, so an unusable value falls through to the next source. | 141 | `youtube/js_runtime.py` (new) |
| `JS_RUNTIME_OPTS` | `_base_opts` sets `js_runtimes = {"deno": {"path": str(path)}}` when the lookup finds a runtime, and leaves the key out when it finds none. | 141 | `youtube/adapter.py` |
| `RUNTIME_HEALTH` | `HealthService.dependencies()` carries `js_runtime: JsRuntimeStatus(available, name, path, version, source, solver)`; `version` comes from one bounded `deno --version` run (5 s, first line, `deno X.Y.Z` parsed, else None) and `solver` is True when `yt_dlp_ejs` imports. | 141 | `domain/health.py`, `services/health.py`, `youtube/js_runtime.py` |
| `RUNTIME_WIRE` | `GET /health/dependencies` serves `js_runtime` as `JsRuntimeOut`, and `openapi.committed.json` is regenerated. Against `baseline.sha` the snapshot adds `JsRuntimeOut`, removes nothing, and changes `DependenciesOut` (gaining `js_runtime`) and `SettingsPutIn` (gaining `deno_path`, from `DENO_SETTING`), each equal to its base without that property, with the paths unchanged (`active-set.py openapi`, H1-4). | 141 | `schemas/health.py`, `routes/health.py`, `openapi.committed.json` |
| `RUNTIME_ROW` | Settings → Dependencies shows a JS runtime row naming the runtime, its version, its source and its path, or, when none is found, says yt-dlp runs without a runtime, that some formats may be missing, and how to fix it (D-648). | 141 | `SettingsPage.tsx` |
| `DENO_FIELD` | Settings → Downloader shows `deno_path` read-only with a Browse button, as `ffmpeg_path` is, and a `deno_path` PUT refetches the dependencies query. | 141 | `SettingsPage.tsx`, `useSettingsPage.ts` |
| `SOLVER_DEP` | The infrastructure package depends on the solver per D-640's ruling, and the lock holds it. | 141 | `pyproject.toml`, `uv.lock` |
| `SOLVER_SPEC` | `avkit-backend.spec` adds `yt_dlp_ejs` and its submodules to `hiddenimports` and `collect_data_files("yt_dlp_ejs")` to `datas`. | 141 | `packaging/avkit-backend.spec` |
| `DENO_BUNDLE` | `tools/fetch_deno_windows.ps1` fetches a pinned Deno zip and licence by URL and SHA-256 into `packaging/deno-win64/`, which is git-ignored; `electron-builder.yml` copies it to `resources/deno` without the zip; `bundled_deno()` in `wiring.py` returns `resources/deno/deno.exe` when frozen (D-649). | 141 | `tools/fetch_deno_windows.ps1` (new), `ui/electron-builder.yml`, `.gitignore`, `wiring.py` |
| `DENO_LICENCE` | `OTHER_LISTS` names `resources/deno/LICENSE.md: Deno`, and `THIRD_PARTY_NOTICES.md` has a Deno row (MIT, version, source URL). | 141 | `tools/generate_third_party_licenses.py`, `packaging/THIRD_PARTY_NOTICES.md` |
| `RUNTIME_SMOKE` | `tools/smoke_packaged_runtime.py --backend-dir D --out F` starts the onedir backend in `D` through `Backend` from `tools/smoke_packaged_tts.py`, with a fresh app-data folder and a `PATH` from which every folder holding a `deno.exe` is removed, and exits 0 only when `/health/dependencies` reports `js_runtime.available`, `source == "bundled"`, a parsed `version` and `solver` True; otherwise it exits 1 naming the first missing field. It ends the backend by its recorded process (Session 56). | 141 | `tools/smoke_packaged_runtime.py` (new) |

### Pins that move

| Row | Test | Today | After |
|---|---|---|---|
| 2a | `tests/integration/test_youtube_adapter.py:346` `test_ac_6_6_quality_selectors_exhaustive` | height selectors end `best[height<=N]` | they end `/best` (`CATCH_ALL`) |
| 2a | `tests/integration/test_youtube_adapter.py:611` and `:621` (AC-6.16) | no cookies select `SABR_EXTRACTOR_ARGS`, cookies select `COOKIE_EXTRACTOR_ARGS` | attempt 1 has no `extractor_args` in either mode (`ATTEMPT_OPTS`) |
| 1 | add-path fakes: `tests/unit/test_services.py:384`, `:671`; `tests/e2e/real_stack.py:66`; `tests/e2e/test_api_error_surface.py:174`; `tests/integration/test_download_received_quality.py:98` | `extract_info(url, flat)` or `extract_info(url)` | accept `options` (`ADD_OPTS`) |
| 1 | `tests/unit/test_domain.py:1355` `test_ac_4_7_port_method_sets_and_signatures` (CRLF) | `YouTubePort.extract_info`'s parameters are `["self", "url", "flat"]` | `["self", "url", "flat", "options"]`, with `options` defaulting to None and the test's other checks unchanged (`ADD_OPTS`) |
| 1 | `tests/unit/test_transcript_metadata.py:142-145` `test_ac_122_6_playlist_info_and_extract_info_unchanged` (AC-122.6, LF) | the port's type hints equal `{"url": str, "flat": bool, "return": VideoInfo \| PlaylistInfo}` and its parameters are `["self", "url", "flat"]` | the hints also hold `"options": DownloadOptions \| None` and the parameters are `["self", "url", "flat", "options"]` with `options` defaulting to None; `PlaylistInfo`'s fields, the return type and `flat`'s default False stay pinned as written, so the guard still stops a wider download type (D-346, its purpose) (`ADD_OPTS`, round 2 F6) |
| 2b | `mcp-server/tests/audit/isolation.test.ts:35` (AC-68.8) | `ISOLATION_INPUT_KEYS` sorted equals `cookie_file_path`, `ffmpeg_path` | it also holds `deno_path` (`AUDIT_INPUT`); `:31` and `:36` stay as written |
| 1b | `DependencyHealth(` constructions: `tests/e2e/api_fakes.py:76`, `tests/e2e/test_api_auth.py:69`, `tests/e2e/test_api_health_settings.py:55` | no runtime field | `js_runtime` has a default, so they build unchanged; row 1b proves it |

Row 1 greps every pin on the settings registry order, the Health dependency fields, the `DependenciesOut` fields, the downloader settings leaves in UI and MCP tests, and the spec's `hiddenimports` and `datas`, by neighbour as well as count (Session 59 RULE-1, Session 62 RULE-4, Session 63 RULE-1), and records each in `s66-anchors.txt`. A pin found there is added to this table in the MEU-140 or MEU-141 handoff as a departure.

### Where values go (Session 50 RULE-1, Session 53 RULE-1, Session 61 RULE-1)

| Value | Writers | Readers | Rule |
|---|---|---|---|
| Attempt 1's error text | yt-dlp `DownloadError` | `ATTEMPT_LOG` `detail` | only through `scrub_line` (D-639); a test drives split text (a secret and the home folder broken across the line) through the real adapter, service and Console store (Session 65 RULE-1), plus lone-surrogate, control-character and empty cases |
| Attempt 2's error text | yt-dlp `DownloadError` | Session 65's `DownloadFailedError` → `download.failed` | unchanged path |
| `clients` | the constant names `default` or `tv,web_safari,web` | `ATTEMPT_LOG` | never yt-dlp text |
| Cookie values, cookie file contents | yt-dlp | none | never logged; `cookiefile` path and browser name are not logged either |
| `deno_path` setting | the user, through PUT | `JS_RUNTIME_LOOKUP` at each call, Health `path` | read fresh at each use (Session 61 RULE-2); a NUL, control character or lone surrogate makes the source unusable and falls through, never raises, never logs the value |
| Runtime path | `JS_RUNTIME_LOOKUP` | `js_runtimes` opts, Health `path` | the user's own path on the user's own machine is shown in Health as `ffmpeg_path` is; it is not logged |
| `deno --version` output | the runtime | Health `version` | only the parsed `X.Y.Z`; anything else is None |

### Spec text (D3)

| File | Change |
|---|---|
| `docs/build-plan/02-infrastructure.md` | `Delivered (Session 66)` notes under both residual sections, with the mechanism ids, the ACs and the plan folder; the `:381` SABR client fallback line names `ATTEMPT_OPTS`; the Solver row records D-640's ruling |
| `docs/build-plan/06-gui.md` | the key table gains `downloader.deno_path` after `downloader.yt_dlp_debug`; the dependencies list gains the JS runtime row |
| `docs/build-plan/07-distribution.md` | a `## Deno (locked)` section after `## FFmpeg (locked)` with the probe order and the bundled path, and the installer size measured by row 5 |

### MEU-140 `infra-youtube-client-fallback`

**Boundary inventory.** Inputs: `DownloadOptions` (cookie mode, browser, profile, cookie file, quality, audio flags), yt-dlp's `DownloadError` text, the yt-dlp logger's SABR match, `should_stop`. Outputs: `YoutubeDL` options per attempt, `DownloadResult`, `DownloadFailedError`, `youtube.attempt_failed` and `youtube.download` lines. Port change: `YouTubePort.extract_info(url, flat=False, options=None)`. No API route, schema or UI change.

**Input matrix (Session 64 RULE-1).** Probed by reading `_cookie_opts`, `download`, `classify_download_error` and `FAILURE_CAUSE_NEEDLES` at `0553779`:

| Cookie mode | Attempt 1 | Error class | Expected |
|---|---|---|---|
| none, browser, file | passes | — | one run, no `extractor_args`, cookies as today, `attempt=1` |
| each | fails | reload page, requested format not available, no video formats, only images, SABR phrase in text, SABR phrase only in attempt 1's log | `attempt_failed` line; attempt 2 with `COOKIE_EXTRACTOR_ARGS` and the same cookies; its pass gives `attempt=2`, its failure raises Session 65's error for attempt 2 |
| each | fails | bot check, cookie database, DPAPI, write failed, other text; and each of the first four after a SABR line in attempt 1's log or beside a format line in the same text (`CLIENT_SIDE`'s first step) | one run, raised as today, no retry |
| each | raises | `DownloadCancelledError`, `CookieTestError`, age gate, `OSError` | one run, raised as today |
| each | fails, then `should_stop` is True | client-side | `DownloadCancelledError`, no attempt 2 |
| file, missing file | — | — | `CookieTestError` before any run, at download and at add |

| AC | Type | Description | Source | Negative test |
|---|---|---|---|---|
| AC-140.1 | behaviour | Attempt 1 sets no `extractor_args` in modes none, browser and file; browser keeps `cookiesfrombrowser`, file keeps `cookiefile` | Human-approved: D-539 | AC-6.16 moved: no `player_client` reaches attempt 1 in any mode |
| AC-140.2 | behaviour | `CATCH_ALL`: each height preset ends `/best`; `Best`, `Lowest` and every audio selector unchanged | Local Canon: 02 Catch-all row | `Best` and `Lowest` strings compared whole |
| AC-140.3 | behaviour | `RETRY_ONCE` on each client-side error in each cookie mode: exactly two `YoutubeDL` runs, the second with `COOKIE_EXTRACTOR_ARGS` and the same cookie opts; a passing attempt 2 returns its `DownloadResult` | Human-approved: D-539; Local Canon: 02 Tests row | a third run never happens when attempt 2 fails |
| AC-140.4 | guard | No retry on a bot check, a cookie cause, a write failure, other text, `DownloadCancelledError`, `CookieTestError`, an age gate or an `OSError`: exactly one run, the same error as at `0553779`. `CLIENT_SIDE`'s precedence cases are here too, each one run: a SABR phrase in attempt 1's log followed by a bot, cookie or write error, and a multiline text holding a format error and a cookie error. It holds at baseline, so it passes where row 2a writes it, and row 3 runs it again once the retry exists | Local Canon: 02 Tests row (a cancel or cookie error never retries); D-643 | each case is its own parametrize id; AC-140.3's SABR-only case still retries |
| AC-140.5 | behaviour | A stop requested after a failed attempt 1 raises `DownloadCancelledError` and runs no attempt 2 | Local Canon: 02 Tests row | `should_stop` False runs attempt 2 |
| AC-140.6 | behaviour | `ATTEMPT_LOG`: a failed attempt 1 logs one `youtube.attempt_failed` warning with `attempt=1`, `clients="default"`, the cause and the scrubbed first line; when attempt 2 fails too the service's `download.failed` line follows with attempt 2's cause; traced from the port call to the Console rows with a recording fake (Session 55 RULE-3) | Human-approved: D-539 (both attempts log); grouping :65 | no `attempt_failed` line when attempt 1 passes |
| AC-140.7 | behaviour | Attempt 1's text reaches the Console only through `scrub_line`: split secret and home-folder text driven through the real adapter, service and Console store; lone surrogate, control characters and empty text give a clean or empty `detail` and never raise | Local Canon: D-639, Session 65 RULE-1, Session 53 RULE-1 | the raw secret and the raw home folder are absent from every row |
| AC-140.8 | behaviour | `SABR_ACROSS`: a SABR phrase in attempt 1's log and a passing attempt 2 give `sabr_detected=True`; `youtube.download` carries `attempt` | Local Canon: D-645 | no phrase in either gives False |
| AC-140.9 | behaviour | `ADD_OPTS`: `add_to_queue` passes `DownloadOptions` built from its arguments and the cookie settings to the coordinator and the port; the adapter's `extract_info` with options applies the cookies and the same attempt sequence | Local Canon: 02 Add-time check row | `extract_info` without options (the transcript path) sets no cookie opts and runs once |
| AC-140.10 | behaviour | `ADD_CACHE_KEY`: a cookie mode change within the TTL misses the cache; the same options hit it | Local Canon: D-646 | the no-options key is unchanged for the transcript path |
| AC-140.11 | behaviour | `POST /downloads` with cookie mode file and a missing file answers 422 with the cookie message and creates no job row | Local Canon: D-646; `avkit_api/errors.py:31` | the same add with mode none creates the row |
| AC-140.12 | guard | `check_sabr_status` still uses `SABR_EXTRACTOR_ARGS` and runs once | Local Canon: 02 §SABR check result | must pass where written (characterises behaviour that exists) |

**Guards.** `tests/integration/test_youtube_adapter.py`, `tests/integration/test_youtube_adapter_visibility.py`, `tests/unit/test_download_failure_visibility.py`, `tests/e2e/test_api_download_visibility.py`, `tests/unit/test_services.py`, `tests/unit/test_transcript_flat_extract.py`, `tests/unit/test_transcript_metadata.py`, `tests/integration/test_download_received_quality.py`, `tests/e2e/test_api_downloads.py` and `tests/e2e/test_api_error_surface.py` pass after row 3.

**Spec sufficiency.** Every 02 rule has an AC: Client choice (AC-140.1, .3 to .6), Catch-all (AC-140.2), Add-time check (AC-140.9 to .11), Tests (AC-140.3 to .5). The live probe is D-642's manual check, not an AC.

### MEU-141 `infra-ytdlp-js-runtime`

**Boundary inventory.** Inputs: the `deno_path` setting, the frozen layout (`sys.executable`), PATH, the `deno --version` output, the `yt_dlp_ejs` import. Outputs: `js_runtimes` in every opts builder, `JsRuntimeStatus` in Health, `JsRuntimeOut` on the wire, a Settings row and field, the onedir's collected solver, the installer's `resources/deno`. New files: `youtube/js_runtime.py`, `tools/fetch_deno_windows.ps1`, tests.

**Input matrix (Session 64 RULE-1).**

| Setting | Bundled file | PATH | Expected `source` |
|---|---|---|---|
| a file | any | any | `setting` |
| empty, missing file, a folder, NUL, control character, lone surrogate, `is_file` raising `OSError` | present | any | `bundled` |
| unusable as above | absent or not frozen | `deno` found | `path` |
| unusable | absent | not found | None: Health `available=False`, no `js_runtimes` key |

| AC | Type | Description | Source | Negative test |
|---|---|---|---|---|
| AC-141.1 | behaviour | `DENO_SETTING`: the key exists with default `""`, last in the downloader namespace, and the API, MCP and UI schemas take it | Human-approved: D-540 (the setting) | an unknown leaf is still refused |
| AC-141.2 | behaviour | `JS_RUNTIME_LOOKUP` order over the input matrix, one parametrize id per row | Human-approved: D-540; Local Canon: 07:159-164 | a setting that names a missing file never wins |
| AC-141.3 | behaviour | Every unusable setting value falls through without raising and without logging the value (Session 58 RULE-2, Session 53 RULE-1) | Local Canon | each value is its own id |
| AC-141.4 | behaviour | A `deno_path` PUT reaches the next adapter call and the next Health read without a restart (`LIVE_SOURCE` in `wiring.py`) | Local Canon: Session 61 RULE-2, ffmpeg's `LIVE_SOURCE` | clearing it falls back to the bundled or PATH runtime |
| AC-141.5 | behaviour | `JS_RUNTIME_OPTS` in every opts builder (both download attempts, `extract_info` with and without options, `extract_video_ids`, `check_sabr_status`, `test_cookies`) | Human-approved: D-540 (`js_runtimes`) | with no runtime the key is absent |
| AC-141.6 | behaviour | `RUNTIME_HEALTH`: found through each source gives `available`, `name="deno"`, the path and the source | Human-approved: D-540 (Health names the runtime) | none found gives `available=False`, `path=None`, `source=None` |
| AC-141.7 | behaviour | The version probe parses `deno 2.9.8 (...)` to `2.9.8`; a timeout, an `OSError`, garbage and empty output give `None` and keep `available` | Local Canon | no output text but the parsed version leaves the probe |
| AC-141.8 | behaviour | `GET /health/dependencies` serves `js_runtime` with all six fields, the OpenAPI check passes on the regenerated snapshot, and its delta from `baseline.sha` is the one `RUNTIME_WIRE` names | Local Canon: 02 Health row | the route still needs the bearer token |
| AC-141.9 | behaviour | `RUNTIME_ROW` in Settings → Dependencies, found and none found | Human-approved: D-540; Local Canon: 02 Health row | the none-found text names the cost and the fix |
| AC-141.10 | behaviour | `DENO_FIELD`: the read-only field and Browse render, and a `deno_path` PUT refetches dependencies | Local Canon: AC-78.8, AC-78.9 | a quality PUT doesn't refetch |
| AC-141.11 | guard | `SOLVER_DEP`: `yt_dlp_ejs` imports in the dev environment, and its installed version equals the one yt-dlp's `default` extra pins in its metadata (offline read of `importlib.metadata`); row 4 installs the solver, so this passes where row 2b writes it | Research-backed: EJS wiki; D-640 | the test's pin reader refuses a fixture requirement list whose `yt-dlp-ejs` pin differs from the installed version |
| AC-141.12 | behaviour | `SOLVER_SPEC` and `RUNTIME_SMOKE`: the spec names the solver, and the onedir smoke reports `source == "bundled"` and `solver` True on a fresh build (Red on the pre-session build in `packaging/dist`, Session 51 D-315) | Research-backed: EJS wiki; Local Canon: 02 Tests row | the pre-session onedir has no `js_runtime` field |
| AC-141.13 | behaviour | `DENO_LICENCE` and `DENO_BUNDLE`: `OTHER_LISTS` names `resources/deno/LICENSE.md`, `THIRD_PARTY_NOTICES.md` has the Deno row, `electron-builder.yml` copies `packaging/deno-win64` to `deno` without `*.zip`, and the licence generator passes on the fresh build | Human-approved: D-540 (MIT notice) | the generator still refuses a GPL-class package off the allow list |
| AC-141.14 | behaviour | `fetch_deno_windows.ps1` refuses an empty URL (exit 2), a non-hex SHA (exit 2) and a mismatched SHA (exit 3), and extracts a matching archive (run offline with `-ExtractOnly` on a fixture zip) | Local Canon: `tools/fetch_ffmpeg_windows.ps1` | a SHA mismatch leaves no `deno.exe` |
| AC-141.15 | measurement | The NSIS installer built with Deno is under 500 MB (07:444); the number and the rc.2 reference (340,362,828 bytes, `ui/dist/av-kit-Setup-0.1.0-rc.2.exe`) go in the handoff | Human-approved: D-540 (size check); Local Canon: 07:33, :444 | over 500 MB stops the row (S13) |
| AC-141.16 | behaviour | `AUDIT_INPUT`: `ISOLATION_INPUT_KEYS` holds `downloader.deno_path`, and `isolationKeys(SETTINGS_SCHEMA)` still equals the seven output keys (AC-68.8 unchanged) | Local Canon: AC-68.8 | `isolationKeys` never contains `downloader.deno_path` |

**Test ids.** The Settings row and field need `deps-js-runtime-row` and `browse-deno-btn`. They go in one additive block at the end of `ui/tests/e2e/test-ids.ts` (CRLF), headed `// MEU-141 YouTube JS runtime (additive IDs).`, and row 2b runs the AC-51.6 and AC-81.13 byte-hash tests (`ui/tests/unit/layout-primitives.test.ts`, `ui/tests/unit/capture-action-row.test.ts`) in its own check (S9).

**Guards.** `tests/integration/test_api_wiring.py` (the ffmpeg `LIVE_SOURCE` tests), `tests/e2e/test_api_health_settings.py`, `tests/e2e/test_api_auth.py`, `tests/e2e/test_api_ffmpeg_resolution.py`, `ui/tests/unit/settings-page.test.ts`, `ui/tests/unit/settings-deps-refresh.test.ts`, `ui/tests/unit/settings-rail.test.tsx`, `ui/tests/unit/settings-mcp-prompt.test.ts`, `ui/tests/unit/settings-path-fields.test.tsx`, `ui/tests/e2e/settings.test.ts` (in the gate), the MCP audit fake backend and isolation tests (`mcp-server/tests/audit/`), `mcp-server/tests/capture.test.ts` and `convert.test.ts` (they read `SETTINGS_SCHEMA`), `tests/unit/test_generate_third_party_licenses.py`, and the packaging pins, which check subsets and so don't move: `tests/unit/test_packaging_backend.py` (AC-72.6 spec), `tests/unit/test_packaging_installer.py` (AC-25.2, AC-72.7 notices, AC-113 fetch exits) and `tests/unit/test_release_packaging.py` (AC-110 resources and notices), all pass after row 5.

**Spec sufficiency.** Runtime (AC-141.1 to .6, .13 to .16), Solver (AC-141.11, .12), Health (AC-141.6 to .9), Tests (AC-141.2, .3, .12).

### Files Modified

Endings and SHA-256 prefixes from `C:/Temp/av-kit/s66-plan-endings.txt`; row 0 records them again in full.

| File | Endings | MEU |
|---|---|---|
| `packages/infrastructure/src/avkit_infra/youtube/adapter.py` | CRLF | 140, 141 |
| `packages/infrastructure/src/avkit_infra/youtube/js_runtime.py` (new) | LF | 141 |
| `packages/core/src/avkit_core/ports/youtube.py` | LF | 140 |
| `packages/core/src/avkit_core/services/extract.py` | LF | 140 |
| `packages/core/src/avkit_core/services/download.py` | CRLF | 140 |
| `packages/core/src/avkit_core/services/settings.py` | CRLF | 141 |
| `packages/core/src/avkit_core/services/health.py` | CRLF | 141 |
| `packages/core/src/avkit_core/domain/health.py` | CRLF | 141 |
| `packages/api/src/avkit_api/wiring.py` | CRLF | 141 |
| `packages/api/src/avkit_api/schemas/health.py`, `schemas/settings.py`, `routes/health.py` | CRLF | 141 |
| `openapi.committed.json` | CRLF | 141 |
| `packages/infrastructure/pyproject.toml` | CRLF | 141 |
| `uv.lock` | LF | 141 |
| `packaging/avkit-backend.spec`, `packaging/THIRD_PARTY_NOTICES.md` | CRLF | 141 |
| `ui/electron-builder.yml`, `.gitignore` | CRLF | 141 |
| `tools/generate_third_party_licenses.py` | LF | 141 |
| `tools/smoke_packaged_runtime.py` (new) | LF | 141 |
| `mcp-server/tests/settings-runtime.test.ts` (new) | LF | 141 |
| `tools/fetch_deno_windows.ps1` (new) | CRLF, as `fetch_ffmpeg_windows.ps1` | 141 |
| `mcp-server/src/toolsets/settings.ts`, `mcp-server/scripts/audit/classify.ts`, `mcp-server/tests/audit/isolation.test.ts` | CRLF | 141 |
| `ui/tests/e2e/test-ids.ts` (byte-hash guarded, additive block only, S9) | CRLF | 141 |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx`, `settings-schemas.ts`, `useSettingsPage.ts` | CRLF | 141 |
| `tests/integration/test_youtube_adapter.py`, `tests/unit/test_services.py`, `tests/e2e/real_stack.py`, `tests/e2e/test_api_error_surface.py` | CRLF | 140 |
| `tests/integration/test_download_received_quality.py` | LF | 140 |
| `tests/unit/test_domain.py` (the port signature pin, row 1) | CRLF | 140 |
| `tests/unit/test_transcript_metadata.py` (the AC-122.6 port pin, row 1) | LF | 140 |
| `tests/integration/test_youtube_client_fallback.py` (new), `tests/unit/test_extract_options.py` (new), `tests/e2e/test_api_client_fallback.py` (new) | LF | 140 |
| `tests/unit/test_js_runtime.py` (new), `tests/integration/test_js_runtime_wiring.py` (new), `tests/e2e/test_api_js_runtime.py` (new), `tests/unit/test_fetch_deno.py` (new) | LF | 141 |
| `tests/integration/test_api_wiring.py`, `tests/e2e/test_api_health_settings.py`, `tests/e2e/test_api_auth.py` | CRLF | 141 |
| `ui/tests/unit/settings-runtime.test.ts` (new) | LF | 141 |
| `docs/build-plan/02-infrastructure.md`, `06-gui.md`, `07-distribution.md` | CRLF | both |

Each row measures a file's endings with Python bytes before it writes and writes in that ending; a scratch script that edits a tracked file fails on mixed endings (Session 63 RULE-3).

### Project files

`.agent/context/known-issues.yaml` (LF), `.agent/context/meu-status.yaml`, `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md`, the grouping file (LF; tracker row 66 at `:150`), the two handoffs, the two rolling reviews, the reflection, `docs/execution/metrics.md`, `.agent/context/current-focus.md`, `.agent/context/triage-output.yaml`, and this folder's plan, task and scripts, with `active-set.py` and the `active-meus.txt` that row 3s writes (one LF line).

## Out of Scope

| Item | Basis |
|---|---|
| MEU-142 (MP3 conversion) | Session 67 (D-651) |
| Node, Bun or Electron's Node as the runtime | D-540 ruled A over B and C |
| Any other `player_client` list, `visionos` in the pin, the `default,web_safari` mix | D-539 ruled A over B and C |
| Changing `SABR_EXTRACTOR_ARGS` or Check SABR | MEU-138 owns it; AC-140.12 guards it |
| The transcript path's extract options | not in the issue; `extract_info` without options is unchanged (AC-140.9 negative) |
| A runtime for macOS or Linux installers | 07 ships Windows only |
| Fetching Deno at app runtime or updating it in place | D-540 bundles it; a Deno bump moves with a yt-dlp bump, as ffmpeg's pin does |
| The card showing both attempts | D-644: the card keeps the final cause; the Console carries attempt 1 |

## BUILD_PLAN.md Audit

`uv run python tools/meu_status.py render --check` passes at baseline and after rows 6 and H2-2. MEU-140 and MEU-141 are `pending` with dependencies MEU-6, MEU-124 and MEU-137 (MEU-140) and MEU-6, MEU-13 and MEU-140 (MEU-141), all approved except MEU-140 itself (`C:/Temp/av-kit/s66-plan-probes.txt`).

## Verification Plan

### 1. Baseline (row 0)

`baseline.ps1`:
1. checks that D-640 to D-642 are ruled in this plan's decision log (`chosen` starts `A: `, `B: ` or another letter, with a `human_message_reference`), and stops if not (S14);
2. checks the queue (S8): MEU-139 `approved`, MEU-140 and MEU-141 `pending`, `0553779` an ancestor of `HEAD`;
3. checks by name the shapes this plan relies on (`_cookie_opts`, `_quality_selector`, `classify_download_error`, `FAILURE_CAUSE_NEEDLES`, `ExtractCoordinator.extract_info`, `FFmpegAdapter._resolve_ffmpeg`, `bundled_ffmpeg`, `DependencyHealth`, `DependenciesOut`, `SETTINGS_KEY_TABLE`, `OTHER_LISTS`, `GPL_ALLOWED`) that the port signature pins at `tests/unit/test_domain.py:1355` and `tests/unit/test_transcript_metadata.py:143-144` still read `["self", "url", "flat"]` and the old type hints, and that every new name and file, `active-meus.txt` among them, is absent (S11, Session 61 RULE-3);
4. creates `C:\Temp\av-kit\s66\tmp` and records `baseline.sha`, `baseline-dirty.txt` with each dirty path's SHA-256, and `s66-anchors.txt` with every target's endings and SHA-256; `docs/proposals/2026-11-10-download-logic-divergence-report.md`, if present, is hashed, never opened;
5. installs from the lock with `uv sync --frozen --offline --all-packages` and proves both `node_modules` trees match their locks (S4);
6. records the installed yt-dlp version, whether `yt_dlp_ejs` imports, and `~/.deno/bin/deno.exe --version` (Session 52 RULE-2);
7. captures the base Python, UI and MCP suites and `ruff check packages/ tests/`;
8. runs the `red-check.py` and `identity.py` selftests on their own fixture copies (Session 56 RULE-4).

### 2. Type-only first, then Red, then Green

Row 1 adds MEU-140's names as wrong stubs or unread fields (Session 53 RULE-2): `_attempt_opts` returning `_cookie_opts`'s result unchanged, `client_side_error` returning False, the port and coordinator `options` keyword unread; it also moves the port signature pins `test_domain.py:1355` and `test_transcript_metadata.py:142-145` (§Pins that move). Row 1b, after row 4 and only when MEU-141 is active, adds MEU-141's the same way: `JsRuntime` and `JsRuntimeLocator` with `resolve()` returning None, `JsRuntimeStatus` and `DependencyHealth.js_runtime` defaulting to unavailable, `JsRuntimeOut` and `DependenciesOut.js_runtime`, `probe_deno_version` returning None, an unread `js_runtime` keyword on `YouTubeAdapter`, `bundled_deno()` returning None. The `deno_path` setting and its schema leaves are not added in row 1: they are behaviour, so AC-141.1 stays Red until row 5. Row 1b regenerates the OpenAPI snapshot for `JsRuntimeOut` and `DependenciesOut.js_runtime`; row 5 adds `SettingsPutIn.deno_path`. Red rows pass only when `red-check.py` reads each receipt and names each failing required test as an assertion failure (Session 50); every Red test asserts a name exists before it patches or calls it (Session 52 RULE-4) and asserts membership before indexing (Session 62 RULE-3). Green rows change no test file.

### Plan-local scripts

`baseline.ps1`, `red-check.py`, `identity.py`, `issue-resolve.py` and `session-gate.ps1` in this folder, adapted from Session 65's with the `s66` names and this plan's paths. `red-check.py` and `identity.py` keep their selftests.

`active-set.py` (added after round 1, F5) holds the one active-MEU set every later step reads. `active-meus.txt`, written at row 3s, holds `MEU-140 MEU-141` or `MEU-140`. D-640 D, D-641 B or D-642 D allow only `MEU-140`; otherwise D-641 D allows only both, and D-641 A allows either, by the context reading at row 3s. Its subcommands:
- `check`: the set against the rulings, and rows 4, 1b, 2b and 5 against the set (`[B]` exactly when MEU-141 is deferred, one row each);
- `meus`, `issues` and `deferred`: the active MEUs, their issues, and the deferred MEU;
- `records`: the statuses (active `ready_for_review`, deferred `pending`), each issue resolved exactly when its MEU is active, one grouping row 66 marked executed with this plan folder, a 66b row (MEU-141, `pending`) exactly under a split, and one `Delivered (Session 66)` note per active MEU;
- `openapi BASE`: H1-4's delta, the one `RUNTIME_WIRE` names with MEU-141 and none without it.

Its `--selftest` runs 57 fixtures over both paths.

### Session gate (H1-2)

`session-gate.ps1` runs, each step with its own receipt and exit code:

| Step | Command |
|---|---|
| Active set | `active-set.py meus` and MEU-141's status in `meu-status.yaml`; they must agree (`ready_for_review` with both MEUs, `pending` with MEU-140 alone), or the gate stops with exit 2 |
| Identity before | `identity.py` |
| Static | pyright, ruff (naming `tools/smoke_packaged_runtime.py` only when MEU-141 is active), UI typecheck and lint, `lint_task_contract.py`, the scope-paths check, `active-set.py check` |
| Fresh full | the whole Python suite (TMP and TEMP at `C:\Temp\av-kit\s66\tmp`), the whole UI suite, the MCP suite, `export_openapi.py --check`, the UI and MCP builds, `meu_status.py render --check`, `issue_triage.py render --check`, the settings Electron spec |
| Package build (MEU-141 active) | `tools/package_backend.py`, which always writes the git-ignored `packaging/dist/avkit-backend` (`package_backend.py:12`) |
| Runtime smoke (MEU-141 active) | `smoke_packaged_runtime.py` on that build, with `packaging/deno-win64` copied to the git-ignored `packaging/dist/deno` as its sibling (`bundled_deno()` reads `Path(sys.executable).resolve().parent.parent / "deno" / "deno.exe"`) |
| Licences (MEU-141 active) | `generate_third_party_licenses.py` on that build |
| Identity after | `identity.py`, equal to before |
| Skipped with reason | `mcp-audit` (network and YouTube), `build-record` (no release), the live probes (D-642's manual check), `real-ffmpeg` (no ffmpeg change); under a split, the package build, the Deno copy, the runtime smoke and the licences (MEU-141 moved to Session 66b) |

The NSIS build for AC-141.15 runs in row 5, not in the gate, because it may fetch (D-642).

## Stop Conditions

| Id | Condition | Action |
|---|---|---|
| S1 | A Red test passes before its Green | fix the test; never weaken the Green |
| S2 | A Green row needs a test file change | stop; a moved pin goes to Mat as a departure |
| S3 | `HEAD` moves or a path outside this plan and `baseline-dirty.txt` changes | stop and ask Mat; never commit, stash or revert another session's work |
| S4 | `uv sync --frozen --offline` or a `node_modules` check fails at baseline | stop and ask Mat |
| S5 | A test or row reaches YouTube or the network outside D-642's named fetches | stop |
| S6 | A raw value reaches a log, stdout or the Console | fix it in the row or ask Mat (Session 50 RULE-1) |
| S7 | Codex unavailable or the ledger refuses a round | Mat reviews |
| S8 | The queue isn't as row 0 expects | stop and ask Mat |
| S9 | A row must edit a byte-hash-guarded file (`ui/tests/e2e/test-ids.ts`) | additive block at the end, and run AC-51.6 and AC-81.13 in that row's own check |
| S10 | A cookie value or cookie file content appears anywhere | stop |
| S11 | A new name exists at baseline | stop and re-plan |
| S12 | The OpenAPI snapshot drifts from the code after row 5 | stop |
| S13 | The installer is 500 MB or more | stop and bring Mat a Decision Brief |
| S14 | D-640 to D-642 are not ruled | stop at row 0 |
| S15 | A status file another session holds dirty | copy to `C:/Temp/av-kit/s66/pre-status/`, byte-edit only this session's fields, prove with `render --check` and a diff (Session 61 RULE-5) |
| S16 | A fetched file's SHA-256 differs from the value Mat approved | stop; never re-fetch from another URL |
| S17 | The licence generator refuses the fresh build | stop and bring Mat a Decision Brief |
| S18 | A contract or AC in this plan needs to change | record a departure; one that changes an AC goes to Mat as a Decision Brief (Session 59 RULE-3) |

## Decision Log

> [!WARNING]
> D-539 and D-540 are Mat's rulings, carried. D-640 to D-642 wait for Mat at the plan gate. D-643 to D-654 are autonomous, each with its alternatives in `reasoning`. D-640 to D-655 are free (`C:/Temp/av-kit/s66-plan-probes.txt`, a `git grep` count of 0 for each).
>
> Carried and not relisted in the block: every grouping §8 row, D-535 to D-543, with stage `grouping`. The reflection carries all nine: D-535 as human (`USER_EXPLICIT 2026-11-10 'follow the process, file them and add to session grouping'`), D-539 and D-540 as human (`USER_EXPLICIT 2026-11-10 'A'`, Mat's reply to the two briefs, which both recommended A), and the others as autonomous. Triage D-529 and D-530 ride in the register. The decision probe (`C:/Temp/av-kit/s66-plan-decision-probe.txt`) names this plan, the grouping and the register as sources (Session 54 RULE-5). With the plan, the grouping, the register and the two issue ids it returns 26 decisions: D-529 and D-530 (triage), D-535 to D-543 (grouping) and D-640 to D-654 (planning). Without the grouping it refuses (HDP-18), so H2-2 passes the grouping file.

```yaml
decision_log:
  - id: D-640
    stage: planning
    question: "How does the solver reach the build, given that yt-dlp[default] brings mutagen, a GPL-2.0-or-later package the licence gate refuses?"
    resolution: human
    class: one-way
    chosen: "A: depend on yt-dlp and yt-dlp-ejs==0.8.0, the version yt-dlp 2026.10.26 pins in its default extra, with a test that fails when the two disagree"
    recommendation: "A: depend on yt-dlp and yt-dlp-ejs==0.8.0, the version yt-dlp 2026.10.26 pins in its default extra, with a test that fails when the two disagree"
    source_tag: Human-approved
    precedents:
      - "grouping D-540 (ruled A): yt-dlp[default] so the matching yt-dlp-ejs comes with yt-dlp"
      - "tools/generate_third_party_licenses.py:44 GPL_ALLOWED = num2words only"
      - "grouping D-61: espeak-ng not bundled because of its GPL licence"
    research:
      engine: none
      sources:
        - "yt_dlp-2026.10.26.dist-info/METADATA lines 31-40, read offline: the default extra is brotli, certifi, mutagen, pycryptodomex, requests, urllib3, websockets and yt-dlp-ejs==0.8.0 (C:/Temp/av-kit/s66-plan-ytdlp-src.txt)"
    reasoning: "D-540 chose yt-dlp[default] for one reason, the matching solver version. A keeps that reason with a test and adds one package. B (yt-dlp[default] with mutagen excluded in the spec) keeps the ruled text but ships three more packages and an exclusion to maintain. C (yt-dlp[default] with mutagen allow-listed) puts a GPL library in-process in the MIT backend, which D-61 and the licence gate avoid. D (do nothing) ships no solver."
    human_message_reference: "USER_EXPLICIT 2026-11-12 'all recommendations are accepted'"
  - id: D-641
    stage: planning
    question: "Where may the session split?"
    resolution: human
    class: two-way
    chosen: "D: do nothing; both MEUs in one session with no context-measured split; row 3s records the context state and the session goes straight on"
    recommendation: "D: do nothing; both MEUs in one session with no context-measured split; row 3s records the context state and the session goes straight on, unless D-640 or D-642 is ruled D"
    source_tag: Human-approved
    precedents:
      - "grouping :106 split flag"
      - "Session 65 D-625 (ruled B: no context-measured split)"
      - "Mat, 2026-11-06 (Session 50 row 7): do not worry about context just continue, we have auto compaction"
    research:
      engine: none
      sources: []
    reasoning: "Mat's standing instruction of 2026-11-06 is not to let context stop or shape a session, and Session 65 ruled its split point the same way (D-625 B). Auto compaction carries the session, and the Red and Green receipts and the gate bound the risk of a compaction inside the packaging rows. A (split after row 3 past about half the context) keeps MEU-140 shippable if the packaging runs long, but lets a context reading set the scope. B (split now) is the smallest session, but separates two MEUs D-537 measures together and makes MEU-141 wait. Under every option D-640 D or D-642 D defers MEU-141, because no solver or runtime could ship; active-set.py holds that one fact for every later step (round 1 F5)."
    human_message_reference: "USER_EXPLICIT 2026-11-12 'all recommendations are accepted'"
  - id: D-642
    stage: planning
    question: "Which network requests may execution make, and do the live probes run?"
    resolution: human
    class: one-way
    chosen: "A: allow the yt-dlp-ejs wheel through uv lock and uv sync, the Deno 2.9.8 Windows zip with the release's published sha256sum file and its LICENSE.md at tag v2.9.8 from GitHub (the zip pinned only when its SHA-256 equals the published one; a missing or different sum stops the row and comes to Mat), and the installer build; run the four live probes as a recorded manual check after the gate, each brought to Mat first"
    recommendation: "A: allow the yt-dlp-ejs wheel through uv lock and uv sync, the Deno 2.9.8 Windows zip with the release's published sha256sum file and its LICENSE.md at tag v2.9.8 from GitHub (the zip pinned only when its SHA-256 equals the published one; a missing or different sum stops the row and comes to Mat), and the installer build; run the four live probes as a recorded manual check after the gate, each brought to Mat first"
    source_tag: Human-approved
    precedents:
      - "tools/fetch_ffmpeg_windows.ps1 (pinned URL and SHA)"
      - "grouping :103 and :107 (live probe and the two unmeasured D-539 cases)"
    research:
      engine: none
      sources:
        - "yt_dlp-2026.10.26.dist-info/METADATA line 62: pin-deno is deno==2.9.8"
    reasoning: "MEU-141 can't ship a solver or a runtime that isn't on the machine: yt-dlp-ejs is not in the uv cache and the only Deno here is 2.5.2 in the user folder (s66-plan-probes.txt). The live probes measure D-539's two unmeasured cases. Do nothing keeps the session offline and moves MEU-141 to Session 66b."
    human_message_reference: "USER_EXPLICIT 2026-11-12 'all recommendations are accepted'"
  - id: D-643
    stage: planning
    question: "Which errors are client-side and retry?"
    resolution: autonomous
    class: two-way
    chosen: "Two steps over the whole case-folded text: an age-gate, bot-check, cookies or write_failed needle anywhere refuses the retry; otherwise the no_format needles, the reload-page needle, or a SABR phrase in the error or in the attempt's log retry"
    source_tag: Local Canon
    precedents:
      - "02 Client choice row lists reload page, no formats, SABR-only, requested format not available"
      - "adapter FAILURE_CAUSE_NEEDLES and sabr_phrase (Session 65)"
    research:
      engine: none
      sources: []
    reasoning: "These are the four the ruling lists, matched with the needles Session 65 already proved. The bot check sits in the refused cause too, but a different client doesn't answer it, so it doesn't retry. The refusing needles are read first across every line, so a SABR line logged earlier, or a format line beside a cookie error, never retries a failure another client can't fix (round 1 F1). A wider rule (any refused cause) would retry bot checks; a narrower one would miss the SABR-only case."
    human_message_reference: null
  - id: D-644
    stage: planning
    question: "How do both attempts log, and what does the card show?"
    resolution: autonomous
    class: two-way
    chosen: "A youtube.attempt_failed warning for a failed attempt that retries; download.failed for the final failure; youtube.download carries the attempt number; the card keeps the final cause"
    source_tag: Local Canon
    precedents:
      - "grouping :65 (the retry reports through MEU-137's path)"
      - "Session 65 FAILURE_LOG and scrub_line (D-639)"
    research:
      engine: none
      sources: []
    reasoning: "The Console already holds Session 65's started, done and failed lines, so one more line per failed attempt says which attempt failed and why. Putting both causes on the card would change Session 65's card contract for a case the Console covers."
    human_message_reference: null
  - id: D-645
    stage: planning
    question: "Which attempt sets sabr_detected?"
    resolution: autonomous
    class: two-way
    chosen: "Either attempt"
    source_tag: Local Canon
    precedents:
      - "services/download.py _run_one sets SABR Active from result.sabr_detected"
    research:
      engine: none
      sources: []
    reasoning: "A SABR phrase on attempt 1 is a fact about the video and yt-dlp's clients, and a passing attempt 2 doesn't undo it. Only the passing attempt would hide it from the SABR lock."
    human_message_reference: null
  - id: D-646
    stage: planning
    question: "How does the add-time extract get the download's options?"
    resolution: autonomous
    class: two-way
    chosen: "An options keyword on the port, the coordinator and the adapter's extract_info, built in add_to_queue from its own arguments and the cookie settings; the cache key includes the cookie fields; a missing cookie file fails the add with 422"
    source_tag: Local Canon
    precedents:
      - "02 Add-time check row"
      - "avkit_api/errors.py:31 CookieTestError 422"
    research:
      engine: none
      sources: []
    reasoning: "A keyword keeps the transcript path unchanged. A new port method would need its own coordinator path and cache. Failing the add on a missing cookie file matches what the download would do anyway; adding it without cookies would queue a job that fails."
    human_message_reference: null
  - id: D-647
    stage: planning
    question: "What is the runtime setting called, and where does it sit?"
    resolution: autonomous
    class: two-way
    chosen: "downloader.deno_path, a string with default empty, last in the downloader namespace, shown read-only with Browse like ffmpeg_path"
    source_tag: Local Canon
    precedents:
      - "downloader.ffmpeg_path (06 key table :1043, AC-78.8, AC-78.9)"
    research:
      engine: none
      sources: []
    reasoning: "Deno is the only runtime yt-dlp enables by default and the only one shipped, so the name says what the file must be. Appending it last moves no order pin; placing it beside ffmpeg_path would. A generic js_runtime_path would invite a Node path that js_runtimes would pass as deno."
    human_message_reference: null
  - id: D-648
    stage: planning
    question: "What does Health say when no runtime is found?"
    resolution: autonomous
    class: two-way
    chosen: "No JavaScript runtime found: yt-dlp runs without one, and some YouTube formats may be missing. Set a Deno path, or install Deno 2.3 or later."
    source_tag: Local Canon
    precedents:
      - "02 Health row"
      - "yt-dlp _jsruntime.py DenoJsRuntime MIN_SUPPORTED_VERSION 2.3.0"
    research:
      engine: none
      sources: []
    reasoning: "It names the cost the register records and the two fixes the user has. A bare unavailable flag says nothing about the cost."
    human_message_reference: null
  - id: D-649
    stage: planning
    question: "Where does the bundled Deno live, and how is it fetched?"
    resolution: autonomous
    class: two-way
    chosen: "resources/deno/deno.exe with resources/deno/LICENSE.md, fetched by tools/fetch_deno_windows.ps1 with a pinned URL and SHA-256 into the git-ignored packaging/deno-win64"
    source_tag: Local Canon
    precedents:
      - "tools/fetch_ffmpeg_windows.ps1; electron-builder.yml ffmpeg entry; wiring.bundled_ffmpeg"
    research:
      engine: none
      sources: []
    reasoning: "It is ffmpeg's layout, which D-540 names as the precedent. Committing the binary would put 118 MB in the repository."
    human_message_reference: null
  - id: D-650
    stage: planning
    question: "How is the installer size measured?"
    resolution: autonomous
    class: two-way
    chosen: "Row 5 builds the NSIS installer with npm --prefix ui run dist, its output sent to C:/Temp/av-kit/s66/nsis so ui/dist and its rc.2 installer stay untouched, and records its size beside rc.2's 340,362,828 bytes"
    source_tag: Local Canon
    precedents:
      - "07-distribution.md:444 measure the NSIS, not the installed folder"
    research:
      engine: none
      sources: []
    reasoning: "07 says to measure the NSIS. An estimate from the uncompressed exe would overstate it."
    human_message_reference: null
  - id: D-651
    stage: planning
    question: "Does MEU-142 ride with Session 66?"
    resolution: autonomous
    class: two-way
    chosen: "No; Session 67"
    source_tag: Local Canon
    precedents:
      - "grouping :117"
    research:
      engine: none
      sources: []
    reasoning: "The grouping lets it ride only if this plan is small, and it carries a split flag, a package build and network fetches."
    human_message_reference: null
  - id: D-652
    stage: planning
    question: "What does the session gate cover?"
    resolution: autonomous
    class: two-way
    chosen: "Identity, the static checks, the full Python, UI and MCP suites, OpenAPI, the builds, the renders, the settings Electron spec, the package build, the runtime smoke and the licence generator; mcp-audit, build-record, real-ffmpeg and the live probes skipped with reasons"
    source_tag: Local Canon
    precedents:
      - "Session 51 D-321"
    research:
      engine: none
      sources: []
    reasoning: "The session changes the adapter, core, the API contract, MCP, the renderer and the packaged build, so each has its check. The skipped steps would touch the network or have nothing to check."
    human_message_reference: null
  - id: D-653
    stage: planning
    question: "Does the plan need the comparison report?"
    resolution: autonomous
    class: two-way
    chosen: "No; the live probe scripts are written fresh"
    source_tag: Local Canon
    precedents:
      - "session prompt: never open the report"
    research:
      engine: none
      sources: []
    reasoning: "Every fact the plan uses is in the register, the grouping, 02 and the code. The grouping names the report's probe scripts as a starting point, but a probe of four URLs needs none of them."
    human_message_reference: null
  - id: D-654
    stage: planning
    question: "Which pin does the no-cookie retry use?"
    resolution: autonomous
    class: two-way
    chosen: "COOKIE_EXTRACTOR_ARGS in every mode; SABR_EXTRACTOR_ARGS stays for Check SABR only"
    source_tag: Human-approved
    precedents:
      - "grouping D-539: retries once with today's cookie pin"
    research:
      engine: none
      sources: []
    reasoning: "D-539 names the cookie pin for the retry and makes no exception for the no-cookie mode. The no-cookie pin asks for android and ios, which the brief says need PO tokens."
    human_message_reference: null
  - id: D-655
    stage: execution
    question: "Which first line does ATTEMPT_LOG's detail scrub, and what does the Console row show (row 2a)?"
    resolution: autonomous
    class: two-way
    chosen: "detail is scrub_line of classify_download_error's detail, the first line as written with only a leading ERROR: dropped (D-639), so attempt 1's line reads as download.failed's would; the Console row shows the event and detail only, because CONSOLE_FIELDS is unchanged, and attempt, clients and cause are structured fields of the log event"
    source_tag: Local Canon
    precedents:
      - "D-639: classify_download_error's detail is first_line(text) with only a leading ERROR: dropped, and scrub_line does all cleaning"
      - "Session 65 FAILURE_LOG: download.failed's detail is scrub_line of the classifier's detail"
      - "services/health.py CONSOLE_FIELDS: only job_id, video_id, variant_id, device, error, detail, request_id and route reach a Console row"
    research:
      engine: none
      sources: []
    reasoning: "ATTEMPT_LOG says detail = scrub_line(first line) without naming which first line. The classifier's detail is the first line D-639 defines for a failed download, so both attempts' lines read alike and the scrub still sees the text as written. The plan does not extend CONSOLE_FIELDS, and doing so would widen every Console row's contract, so AC-140.6 asserts attempt, clients and cause on the log event and the Console row as it is served. Only attempt 1 is ever followed by a retry (RETRY_ONCE), so an attempt_failed row before a download.failed row names attempt 1. Two-way."
    human_message_reference: null
  - id: D-656
    stage: execution
    question: "Does the add-time extract check should_stop between its attempts, as download does (row 3)?"
    resolution: autonomous
    class: two-way
    chosen: "No. The one attempt sequence takes a stoppable flag; download passes True and extract_info with options passes False, so an add never raises DownloadCancelledError"
    source_tag: Local Canon
    precedents:
      - "RETRY_ONCE names download as the call that checks should_stop"
      - "services/download.py should_stop returns the queue's cancel flag, which cancel_processing sets and only start_processing or the worker's exit clears"
    research:
      engine: none
      sources: []
    reasoning: "should_stop is the download queue's stop flag. A cancel sent while the queue is idle leaves it set until the next start, so an add whose attempt 1 failed client-side would fail as cancelled although nothing was cancelled. An add has no job to stop, and its extract writes nothing. ADD_OPTS keeps ATTEMPT_OPTS, CLIENT_SIDE, ATTEMPT_LOG and the single retry. Two-way."
    human_message_reference: null
  - id: D-657
    stage: execution
    question: "Which log's SABR match classifies a failed attempt 2 (row 3)?"
    resolution: autonomous
    class: two-way
    chosen: "Attempt 2's own logger, as Session 65 classifies a single run; SABR_ACROSS sets only DownloadResult.sabr_detected"
    source_tag: Local Canon
    precedents:
      - "Error-class table: attempt 2's failure raises Session 65's error for attempt 2"
      - "D-645 and SABR_ACROSS name DownloadResult.sabr_detected only"
    research:
      engine: none
      sources: []
    reasoning: "The plan says attempt 2's failure raises Session 65's error for attempt 2, and Session 65 reads the run's own log. Carrying attempt 1's SABR match into attempt 2's cause would turn a no_format on the pinned clients into refused, which the plan doesn't state. Attempt 1's line in the Console still carries attempt 1's cause. Two-way."
    human_message_reference: null
  - id: D-658
    stage: execution
    question: "Do the e2e dependency fakes build unchanged once the route reads js_runtime (row 2b)?"
    resolution: autonomous
    class: two-way
    chosen: "No. The three e2e fakes are SimpleNamespace objects, not DependencyHealth, so each gains a js_runtime SimpleNamespace under a FIXTURE_REPAIRS comment in row 2b; the pin row that says they build unchanged is corrected here"
    source_tag: Local Canon
    precedents:
      - "Session 33 FIXTURE_REPAIRS (d): the DEPS_FFMPEG fields were added to the same fakes"
      - "Row 1's caller records: DependencyHealth( has one site, services/health.py:266"
    research:
      engine: none
      sources: []
    reasoning: "tests/e2e/api_fakes.py:67, test_api_auth.py:60 and test_api_health_settings.py:46 return SimpleNamespace fakes from dependencies(). A dataclass default cannot reach them, so row 5's route read of deps.js_runtime would raise AttributeError in every e2e health test. The repair adds the RUNTIME_HEALTH field with the unavailable values, matching JS_RUNTIME_UNAVAILABLE, and changes no assertion. Two-way."
    human_message_reference: null
  - id: D-659
    stage: execution
    question: "Row 5 found an unused counter in ui/tests/unit/settings-runtime.test.ts that fails the UI lint; may row 5, whose cell says no test file changes, remove it?"
    resolution: autonomous
    class: two-way
    chosen: "Yes. The three depsGets lines (the declaration, the increment in the fetch mock and the reset in beforeEach) are removed; no assertion, query or fixture value changes"
    source_tag: Local Canon
    precedents:
      - "D-658: a test repair recorded as a departure, with no assertion changed"
      - "ui package.json lint: eslint src/ tests/ --max-warnings 0, so a test file must pass it"
    research:
      engine: none
      sources: []
    reasoning: "Row 2b wrote depsGets as a dependencies GET counter and then asserted the refetch through the invalidation order instead, so the counter is written and never read. eslint's no-unused-vars refuses it, and the session gate's ui-lint step runs npm --prefix ui run lint. Removing it leaves every AC-141.9 and AC-141.10 check as written; the file still passes 8 of 8. Two-way."
    human_message_reference: null
  - id: D-660
    stage: execution
    question: "D-650's npm run dist stops at build:picker: NuGet has no package source on this machine, SDK 8.0.428 asks for the 8.0.34 runtime packs, and the cache stops at 8.0.33. clean:out had already deleted native/region-picker/publish. How is the AC-141.15 installer built?"
    resolution: human
    class: two-way
    chosen: "A: copy the 2026-11-09 picker from ui/dist/win-unpacked/resources/region-picker into native/region-picker/publish (243 files, tree sha256 1db5f034dcca0644368c107c3a7cb828058375320ebc2eb6165c7570eddab971 on both sides), then run dist's other steps unchanged: npm --prefix ui run build, npm --prefix mcp-server run bundle, and electron-builder --win nsis --x64 with -c.directories.output=C:/Temp/av-kit/s66/nsis"
    recommendation: "A: copy the 2026-11-09 picker from ui/dist/win-unpacked/resources/region-picker into native/region-picker/publish, then run dist's other steps unchanged"
    source_tag: Human-approved
    precedents:
      - "D-650: the NSIS build command for AC-141.15"
      - "D-642 A: the only fetches this session allows, which do not include a NuGet restore"
      - "ui package.json dist:prep: clean:out, build, build:picker, then the mcp-server bundle"
    research:
      engine: none
      sources:
        - "C:/Temp/av-kit/s66-r5-nsis.txt: NU1100 for the three win-x64 runtime packs at 8.0.34"
        - "C:/Temp/av-kit/s66-r5-nsis-d660.txt: exit_build=0, exit_bundle=0, exit_builder=0"
    reasoning: "The picker source in native/region-picker last changed on 2026-11-03, before the 2026-11-09 build, so the copied picker is what build:picker would produce from the same source. This session changes no picker file. AC-141.15 measures Deno's cost in the installer, and the picker is the same in both builds. B, one nuget.org restore, is a fetch outside D-642 A. C defers AC-141.15. D leaves row 5 open. Two-way: the next real dist rebuilds the picker from source."
    human_message_reference: "USER_EXPLICIT 2026-11-12 'Reuse Nov 9 picker (Recommended)'"
  - id: D-661
    stage: execution
    question: "Row 6's meu_status.py update re-dumped all of meu-status.yaml, re-wrapping and re-quoting the entries of MEU-137, MEU-138, MEU-139 and MEU-142 and the header note, which S15 allows only for this session's entries. Which bytes does the file keep?"
    resolution: autonomous
    class: two-way
    chosen: "The pre-status copy's bytes, with only the MEU-140 and MEU-141 writes applied by byte replacement (status, both progress cells, execution_plan, updated). The parsed data equals the tool's dump, which is kept at C:/Temp/av-kit/s66/meu-status.tool-dump.yaml"
    source_tag: Local Canon
    precedents:
      - "plan S15: only this session's entries and rows may change in the shared records"
      - "the carried rule that a byte-hash or shared file keeps its other bytes"
    research:
      engine: none
      sources:
        - "C:/Temp/av-kit/s66-r6-prestatus-diff.txt: the tool's dump against the pre-status copy"
    reasoning: "The re-wrap changes no value, since yaml.safe_load of both files is equal, but it puts other sessions' entries in this session's diff and could collide with another session's write. The rebuilt file differs from the pre-status copy only in the ten lines of the two entries, and render --check and active-set.py records pass on it. Two-way: the tool's dump is kept."
    human_message_reference: null
  - id: D-662
    stage: execution
    question: "H1-2's RULE-4 listing found tests/e2e/api_fakes.py changed but absent from session-gate.ps1's allowed set, so the scope-paths step would fail. D-658 wrote that file's fixture repair, and the set already named the other two fakes. Does the gate allow it?"
    resolution: autonomous
    class: two-way
    chosen: "Add tests/e2e/api_fakes.py to the gate's allowed set, beside test_api_auth.py, with a comment naming D-658. No other path is added"
    source_tag: Local Canon
    precedents:
      - "D-658: the three e2e fixture repairs, one of them in tests/e2e/api_fakes.py"
      - "plan S3: only Files Modified, the new files and the record files may change"
    research:
      engine: none
      sources:
        - "git status --porcelain=v1 -uall at H1-2, kept at C:/Temp/av-kit/s66/h12-status.txt: 72 paths, one outside the set"
        - "git diff tests/e2e/api_fakes.py: 4 added lines, the js_runtime SimpleNamespace under FIXTURE_REPAIRS (Session 66, MEU-141)"
    reasoning: "The change is the one D-658 recorded and the MEU-141 handoff reports, so it is in the session's scope; only the gate's list missed it. Every other changed path is already in the set, the plan prefixes or baseline-dirty.txt. Two-way: one line in the gate."
    human_message_reference: null
  - id: D-663
    stage: execution
    question: "H1-2m's two cookies-on probes were to run with Mat's cookie mode, read from the app's settings, but the app's downloader.cookie_mode is none, so both stopped before any fetch. Which cookies do they use?"
    resolution: human
    class: two-way
    chosen: "Firefox's cookies, default profile: live-probe.py takes --cookies browser --browser firefox for the logged-in and members probes. The receipt stores the mode browser only, never the browser name, a profile, a cookie path or a cookie value"
    source_tag: Human-approved
    precedents:
      - "D-642 A: the four live probes as a recorded manual check, each brought to Mat first"
      - "task row H1-2m: the receipt stores no cookie value, cookie file path or browser profile"
    research:
      engine: none
      sources:
        - "C:/Temp/av-kit/s66/probe-logged-in.txt: the first run, which read cookie mode none from the app and exited before any fetch"
    reasoning: "The app had no cookie mode to read, and Mat named the browser signed in to YouTube. Mat approved all probes and gave the members-only URL in this session, and stated the account is not a member of that channel, so the members probe's failure is expected. Two-way: a probe-script option outside the repository."
    human_message_reference: "USER_EXPLICIT 2026-11-12 'I have singed into youtube in firefox, so the cookie should be from the firefox browser'"
```

### D-640 brief: How does the solver reach the build?   [one-way-door] [source-conflict]

**Recommendation:** A. Depend on `yt-dlp` and `yt-dlp-ejs==0.8.0`, the version yt-dlp 2026.10.26 pins in its `default` extra. One test reads yt-dlp's installed metadata and fails if the pin and the installed solver disagree, so a yt-dlp bump that moves the pin fails the suite until the solver moves with it. That keeps the reason D-540 gave for `[default]` and adds one package to the build.

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ A: `yt-dlp` plus `yt-dlp-ejs==0.8.0`, with a pin-match test | — | — | METADATA :40; licence gate :44 |
| ⚠️ B: `yt-dlp[default]` with `mutagen` excluded from the spec | Matches the ruled text; ships `brotli` and `websockets`, which yt-dlp uses when present | Three more packages and licence entries; an exclusion to keep in step with yt-dlp | METADATA :31-40 |
| ⚠️ C: `yt-dlp[default]` with `mutagen` allow-listed | Matches the ruled text with no exclusion | A GPL-2.0-or-later library in-process in the MIT backend, which D-61 and the gate avoid | `generate_third_party_licenses.py:6`, `:44` |
| ❌ D: do nothing (plain `yt-dlp`) | No change | No solver ships; `YTDLP-NO-JS-RUNTIME` stays open | register `:4724` |

**Reversibility:** one-way for each installer that ships the choice. **If you do not answer:** the plan carries A as a guarded row, and row 0 stops (S14).

### D-641 brief: Where may the session split?   [process]

**Recommendation:** D, do nothing: one session, with no context-measured split. At row 3s the coordinator records the context state in the MEU-140 handoff and goes straight on to row 4. This follows your standing instruction of 2026-11-06 ("do not worry about context just continue, we have auto compaction. And do not stop for this reason again.") and Session 65's D-625 B. Under any option, if D-640 or D-642 is ruled D, MEU-141 moves to Session 66b, because no solver or runtime could ship. One file, `active-meus.txt`, holds the result, and `active-set.py` refuses a value the rulings don't allow (round 1 F5).

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) |
|---|---|---|
| ✅ D: do nothing (one session, no context-measured split) | — | — |
| ⚠️ A: split after row 3 if past about 50% of the context | MEU-140 ships even if the packaging runs long | a context reading sets the scope, which your 2026-11-06 instruction argues against; a second session if it fires |
| ⚠️ B: split now; MEU-141 to Session 66b | smallest session | D-537 measures the two together; MEU-141 waits |

**Reversibility:** two-way; a later session can take MEU-141 up under any option. **If you do not answer:** row 0 stops (S14).

### D-642 brief: Network fetches and live probes   [outward-facing]

**Recommendation:** A. Allow at execution, each recorded with its URL, its destination and its SHA-256:
- `uv lock` and `uv sync` resolving `yt-dlp-ejs==0.8.0` from PyPI (row 4); if D-640 is ruled B or C, also the `default` extra's packages not already in the lock;
- the Deno 2.9.8 Windows zip (`deno-x86_64-pc-windows-msvc.zip` from `github.com/denoland/deno/releases/tag/v2.9.8`), the release's published `.sha256sum` file for it, and `LICENSE.md` at that tag, into the new, git-ignored `packaging/deno-win64/`. The zip is pinned in the fetch script only when its SHA-256 equals the published one; a missing or different sum stops the row and comes to you (row 4, S16). Nothing from the zip runs before that check, and the extracted `deno.exe` first runs as `deno --version` in row 5;
- the NSIS build, if electron-builder needs a download (row 5). Its output goes to `C:/Temp/av-kit/s66/nsis`, so `ui/dist` and its rc.2 installer stay as they are.

After the gate, the four live probes run as a recorded manual check, each brought to Mat with what it fetches and where it writes before it runs: gKcOjnDJfzk and one other public video, a members-only video, and a logged-in account. Each runs `yt-dlp` through the adapter with Mat's cookie setting, writes to `C:/Temp/av-kit/s66/probe/`, and prints and stores no cookie value.

| Option | Pros | Cons |
|---|---|---|
| ✅ A: the named fetches, the probes as a manual check | MEU-141 completes; D-539's unmeasured cases get measured | three fetches to review |
| ⚠️ B: the fetches only, no live probes | no YouTube traffic from the session | the two D-539 cases stay unmeasured |
| ❌ D: do nothing (offline) | no network at all | MEU-141 moves to Session 66b; the measurements stay open |

## Research References

- yt-dlp 2026.10.26, read offline from `.venv`: `YoutubeDL.py:544`, `:740` (`js_runtimes` default), `utils/_jsruntime.py:89-101` (Deno minimum 2.3.0), `dependencies/__init__.py:27` (mutagen imported when present), METADATA :31-62 (`C:/Temp/av-kit/s66-plan-ytdlp-src.txt`).
- yt-dlp EJS wiki, as cited in 02 and grouping D-540: https://github.com/yt-dlp/yt-dlp/wiki/EJS
- The D-539 and D-540 briefs in the grouping file §9 for the rest.

## Planning receipts

- `C:/Temp/av-kit/s66-plan-probes.txt`: HEAD, worktrees, MEU status and dependencies, D-640 to D-655 free, AC-140 and AC-141 free, yt-dlp version, `yt_dlp_ejs` absent, Deno 2.5.2 in the user folder, graphify absent.
- `C:/Temp/av-kit/s66-plan-packaging.txt`, `s66-plan-packaging2.txt`, `s66-plan-lock.txt`: pyproject, lock, spec, electron-builder, licence generator, 07 rules, the rc.2 installer size, the uv cache.
- `C:/Temp/av-kit/s66-plan-ytdlp-src.txt`: yt-dlp's `js_runtimes` and extras.
- `C:/Temp/av-kit/s66-plan-pins.txt`: the pins that move and the port fakes.
- `C:/Temp/av-kit/s66-plan-endings.txt`: endings and SHA-256 prefixes.
- `C:/Temp/av-kit/s66-plan-decision-probe.txt`: the decision probe.
- `C:/Temp/av-kit/s66-plan-redcheck-selftest.txt` and `s66-plan-identity-selftest.txt`: the two selftests (49 fixtures, 0 wrong; 0 failures).
- `C:/Temp/av-kit/s66-plan-task-lint.txt`: `lint_task_contract.py` on task.md after the round 1 corrections (`OK: 28 row(s)`), and `s66-plan-task-lint-split.txt`: the same on a scratch copy with the split applied (rows 4, 1b, 2b and 5 `[B]` with their blocks; `OK: 28 row(s)`), with `active-set.py`'s row check passing on the copy under the split set and on the real task under the full set, and refusing the real task under the split set.
- `C:/Temp/av-kit/s66-plan-activeset-selftest.txt`: `active-set.py --selftest` (57 fixtures, 0 wrong).
- `C:/Temp/av-kit/s66-plan-baseline-dry-shapes.txt` and `s66-plan-baseline-dry-anchors.txt`: `baseline.ps1`'s shapes and anchors blocks run alone at `0553779` (exit 0 each; the shapes block rerun after round 1 finds the port signature pin at `test_domain.py:1355` and no `active-meus.txt`; after round 2 it also finds the AC-122.6 pins at `test_transcript_metadata.py:143-144`, `C:/Temp/av-kit/s66-plan-baseline-dry-shapes-r2fix.txt`). Its rulings block exits 1 until Mat rules D-640 to D-642, as S14 intends.
- Not run at plan time: any suite or build.

## Validation stage contract

- **Static:** `pyright`, `ruff check packages/ tests/`, `npm --prefix ui run typecheck`, `ui-lint`, `lint_task_contract.py`, the scope-paths check and the `red-check.py` selftest.
- **Targeted:** each row's own files, with `red-check.py` reading every Red receipt.
- **Fresh full:** the whole Python, UI and MCP suites, the OpenAPI check, the UI and MCP builds, the two render checks, the settings Electron spec, the package build, the runtime smoke and the licence generator, in the session gate.
- **Identity:** `identity.py` binds `HEAD`, the work tree minus `PROJECT_ARTIFACTS`, and the runtime. The gate records it before and after, and H1-6b checks each handoff's evidence against it.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
