---
project: "2026-11-11-download-failure-visibility"
date: "2026-11-11"
source: ".agent/context/grouping/2026-11-10-download-reliability-session-grouping.md#session-65--download-failure-visibility-meu-137-to-meu-139--p2"
grouping_source: ".agent/context/grouping/2026-11-10-download-reliability-session-grouping.md"
meus: ["MEU-137", "MEU-138", "MEU-139"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: Download failure visibility (Session 65)

> **Project:** `2026-11-11-download-failure-visibility`
> **Build plan:** `docs/build-plan/03-service-layer.md` §Download failure reason (`:700-716`, anchor `download-failure-reason-residual`, MEU-137); `docs/build-plan/02-infrastructure.md` §SABR check result (`:534-549`, anchor `sabr-check-result-residual`, MEU-138) and §yt-dlp log detail (`:551-564`, anchor `ytdlp-log-detail-residual`, MEU-139).
>
> **Source request.** On 2026-11-10 Mat asked for the download comparison report's findings to be filed and grouped ("follow the process, file them and add to session grouping"; triage D-531 to D-534, grouping D-535). This is the first of the grouping's three sessions (Sessions 65 to 67, MEU-137 to MEU-142). Done comes from the three spec sections, not from Mat's words: each rule holds with a behaviour test, and the three issues close with that evidence.
> **Known issues:** this session closes `DOWNLOAD-FAILED-NO-REASON` (D-531), `SABR-CHECK-MISSES-CURRENT-MESSAGES` (D-532) and `YTDLP-LOG-TEXT-DROPPED` (D-533). `DOWNLOAD-CLIENT-PIN-MISSES-WORKING-CLIENT` and `DOWNLOAD-MP3-NOT-CONVERTED` are Sessions 66 and 67's and are not touched. The comparison report `docs/proposals/2026-11-10-download-logic-divergence-report.md` is another session's untracked file: it is hashed only and never opened.
> **Status:** `draft`. `plan_to_exec_gate: human`. Mat ruled D-622 to D-624 in planning (§User Review Required). D-625 (the split point) is ruled B by the Fable subagent under Mat's delegation of 2026-11-12 (§Decision Log). The gate was held on 2026-11-12, with the execution budget at 40M (Mat's words in §User Review Required, "The gate").

## Goal

**Goal anchor:** Session 65 makes a failed download, a SABR check and yt-dlp's own messages visible. A failed download's card says why in one short av-kit sentence per cause, and the Console has a matching `download.failed` line with yt-dlp's first line, redacted, in `detail`. Check SABR matches yt-dlp 2026.10.26's own SABR words, the page always states the last result with its time, and Check, Force and Clear each log one line. yt-dlp's warnings and errors always reach the Console with their text in a kept field; the existing Settings switch adds its debug and info lines, and a change applies on the next call without a restart.

Six things are missing today (`003e5b1`):

1. **The card drops the reason.** `DownloadService._finish` stores `error=str(exc)` (`packages/core/src/avkit_core/services/download.py:587-600`, called at `:538` and `:545-548`) and the API serves it, but `DownloaderPage.tsx:476-485` builds each `QueueCardJob` without `errorMessage`, and `DownloadListItem` (`useDownloadQueue.ts:8-21`) has no `error_message`, so `QueueCard.tsx:277` shows the placeholder.
2. **The stored reason is yt-dlp's whole text.** The adapter raises `DomainError(str(exc))` for every yt-dlp `DownloadError` (`packages/infrastructure/src/avkit_infra/youtube/adapter.py:513-517`) and `DomainError("yt-dlp IO failed")` for an `OSError` (`:518-521`); there is no cause and no short message.
3. **The download path logs nothing per job.** The service's only log calls are at `:178`, `:180` and `:199`, all at add time.
4. **The SABR phrases are stale.** `SABR_LOG_NEEDLES` (`adapter.py:81-85`) holds three phrases yt-dlp 2026.10.26 doesn't print; `check_sabr_status` (`:555-561`) and the passive `_YtDlpLogger._scan` (`:321-328`) both use it.
5. **An Inactive result is hidden and SABR actions are silent.** `DownloaderPage.tsx:664` hides the panel unless Active; `check_sabr`, `force_sabr` and `clear_sabr` (`services/download.py:345-380`) log nothing.
6. **yt-dlp's text is dropped.** `_YtDlpLogger._scan` logs only when debug is on, in a `message` field that `CONSOLE_FIELDS` doesn't keep, and `wiring.py:149` reads the setting once at startup.

The session ends when the three sections hold with a behaviour test per rule, the three issues are closed with their evidence, the session gate's last line is `session-gate: all steps exit 0`, and MEU-137 to MEU-139 are `approved` after Codex approves.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (2026-11-11). No payload is oversized: adapter.py, services/download.py, DownloaderPage.tsx and the spec files were read by section."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`plan_to_exec_gate: human`). Validation goes through `rtk proxy`:
  - receipts go under `C:/Temp/av-kit`, named `s65-*`;
  - `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`;
  - `TMP` and `TEMP` point at `C:\Temp\av-kit\s65\tmp` for the Python suite, because `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` is still open;
  - `ELECTRON_RUN_AS_NODE` is cleared before every UI and Electron run (the scripts clear it too).
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub` and any other worktree are left alone.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `s65-plan-canonical-2026-11-11-download-failure-visibility` and `s65-execution-2026-11-11-download-failure-visibility`.
  - Claude wrote the plan, so the reviewer is a different vendor.
  - Caps: plan 3 rounds, execution 6.
  - If Codex is unavailable or the ledger refuses a round, the fallback is Mat.
  - Each round is metered, and the coordinator tells Mat before dispatching.
  - Each rolling report is validated under `C:/Temp/av-kit` and then copied byte for byte to its canonical path (Session 49b D-290), and the `--review-state-only` receipt is rebuilt there.
  - Reviewer prompts name the ledger vocabulary up front: D-622 to D-639, AC-137.1 to AC-137.12, AC-138.1 to AC-138.8, AC-139.1 to AC-139.9, and the mechanism ids in §Single-statement contracts. They forbid opening `P:/av-kit/.mcp.json`, any `mcp-token.txt`, `~/.claude.json`, any `.env`, `.claude/settings.local.json`, anything under `.agent/fleet/hub` and `docs/proposals/2026-11-10-download-logic-divergence-report.md`, and write `<HOME>` for the home folder. When they ask for `tested_state`, they name `~/.config/git/ignore` and the path it hides, `.claude/settings.local.json` (Session 51 RULE-4). Each recheck carries a literal Prior Pass Summary with bare closure words (Session 52 RULE-1), names each prior finding by the review's own id (Session 53 RULE-3), and asks for a `### New Findings` table and bare words in its Recheck cells (`fixed`, `open`).
- **Never in these rows without Mat's words:** commit, push, a network request of any kind (YouTube included), a model, runtime or package download, the live MCP audit, `--update-baseline`, a tag, release or upload, or an `approved` verdict authored by the implementer. Nothing touches the installed avkit MCP servers (no `mcp__avkit__*` tool is called). Every yt-dlp test runs against a mocked `YoutubeDL`; no row reaches YouTube.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-137 `svc-download-failure-reason` | `.agent/context/handoffs/2026-11-11-download-failure-visibility-MEU-137-handoff.md` |
| MEU-138 `infra-sabr-check-result` | `.agent/context/handoffs/2026-11-11-download-failure-visibility-MEU-138-handoff.md` |
| MEU-139 `infra-ytdlp-log-detail` | `.agent/context/handoffs/2026-11-11-download-failure-visibility-MEU-139-handoff.md` |

Rolling reviews: `.agent/context/handoffs/2026-11-11-download-failure-visibility-plan-critical-review.md` and `.agent/context/handoffs/2026-11-11-download-failure-visibility-implementation-critical-review.md`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, base suite receipts, `s65-anchors.txt` |
| WP-2 | Type-only names (row 1) | WP-1 | shared | `DownloadFailureCause`, `DownloadFailedError`, the stubs, `SABRStatus.matched_phrase`, `sabrResultText`, the adapter's debug source; the pins moved |
| WP-3 | MEU-137 Red, then Green (rows 2a, 3) | WP-2 | shared | `FAILURE_MESSAGE`, `FAILURE_CAUSE`, `FAILURE_LOG`, `CARD_REASON` |
| WP-4 | MEU-138 Red, then Green (rows 2b, 4) | WP-3 | shared | `SABR_MATCH`, `SABR_RESULT`, `SABR_LOG`, `SABR_SHOWN` |
| WP-5 | MEU-139 Red, then Green (rows 2c, 5) | WP-4 | shared | `YTDLP_LINE`, `YTDLP_LIVE` |
| WP-6 | Records (row 6) | WP-5 | shared | Spec notes, register resolve, MEU status, renders, grouping tracker |
| WP-7 | Closeout (H1, H2) | WP-6 | `compact_continue` | Three handoffs, the review, the reflection, Session 66's prompt |

**No split point (D-625 B).** MEU-137 is the largest MEU and the other two share its `clean_line`, `scrub_line` and log shape. D-625 is ruled B: all three MEUs run in this session with no context-measured split. When MEU-137's Green (row 3) passes, the context state is recorded in the MEU-137 handoff and the session goes straight on to rows 2b, 4, 2c, 5, 6 and closeout, with one commit and one push. If MEU-139 genuinely fails to land, it can still be deferred on its own merits, not on a context reading.

## User Review Required

> [!IMPORTANT]
> **Four questions were Mat's, and all four are ruled.** D-622 to D-624 were asked through the Human Decision Protocol and Mat chose the recommended option each time (the quotes are in §Decision Log). D-625 was ruled B by the Fable subagent, under Mat's delegation of 2026-11-12: "If you need decisions answerd have Fable subagent do rulling and accept it as if it was coming from human". Every other choice is recorded as autonomous in §Decision Log (D-626 to D-638), with its alternatives. The gate asks Mat to accept the plan, set the execution budget, and override any autonomous choice. Only Mat's words start execution.
>
> **D-622 (ruled A): what the debug switch shows.** Debug off: yt-dlp's warnings and its `ERROR:` lines reach the Console, and nothing else; AC-122.16's rule that a debug line never shows a title stays true with debug off. Debug on: debug and info lines also reach the Console, redacted, which can show a video title.
> **D-623 (ruled A): how a SABR phrase matches.** Whole words, case-insensitive: `sabr` matches "SABR-only" and "forcing SABR" but not "Sabrina" or "the sabre".
> **D-624 (ruled A): the `po token` phrase.** Narrowed to `require a gvs po token`, the old phrase, so a line about PO Tokens alone doesn't turn SABR on.
>
> **D-625 (ruled B, by the Fable subagent under Mat's delegation): the split point.**
> - **A (the planning recommendation, not chosen): keep all three MEUs and name the split point.** If, after MEU-137's Green, the context is past about half, MEU-139 moves to Session 65b (§Work Packages). MEU-139 is the least coupled: it needs only `clean_line` from MEU-137.
> - **B, do nothing: run all three with no split.** Auto-compaction carries the session; the risk is a late compaction inside MEU-139's rows. **Chosen.** Fable's reason: Mat's standing instruction is not to let context decide scope, and Mat's "Full session" answer names one execution loop and one commit; the late-compaction risk is bounded by the Red and Green receipts and the gate.
>
> **What the words in the contracts mean here, and the limits they leave.**
> - **"One short av-kit message per cause."** Five causes (`FAILURE_MESSAGE`). Only `other` carries yt-dlp's text, as its first line, redacted, links as `[link]`, home as `~`, cut to 200 characters. The four named causes carry no yt-dlp text at all.
> - **"Refused."** The page-reload, bot-check and SABR-only messages, and a missing-format error raised in a call whose logger saw a SABR phrase (D-636): yt-dlp says "Requested format is not available" when SABR has hidden every format, and the fix is to wait, not to change quality.
> - **"yt-dlp's raw line, redacted."** The first line of the error text as written (`first_line`: only CR, LF or CRLF ends a line), with only a leading `ERROR:` and the ANSI codes and whitespace around it dropped (D-639), then cleaned by `clean_line` (D-627: ANSI codes dropped, whitespace made spaces, other control, format and lone-surrogate code points dropped) and scrubbed, both inside `scrub_line` (home as `~`, links as `[link]`, then `redact_message`). `scrub_line` first matches the home folder with those characters allowed inside it and its boundary read from the line as written, then also scrubs a joined form with every whitespace character but U+0020 removed, so a control or format character, U+0085, U+2028, a tab or a line break inside a cookie needle, a link or the home path can't hide it, and one before the home path can't join it to the word before (F1, rounds 2 and 3); a plain space still splits a word, as it does today. The Console then applies `console_field` (300 characters).
> - **"Whole words."** `\b` boundaries on the case-folded line. A phrase inside a longer word doesn't match; a phrase next to `-`, `.` or `(` does.
> - **"Every check's result with its time."** The panel shows the last result the backend holds (§`SABR_SHOWN`), with the time in the app's local clock as `HH:MM:SS`. The page doesn't keep a history.
> - **"Applies without a restart."** The adapter reads the setting once at the start of each public call. A change made during a call applies to the next one.
> - **Limits.** No passive-scan log line and no passive matched phrase on the status (§Out of Scope). A traceback that yt-dlp passes to `error()` without the `ERROR:` prefix is a debug line (D-632). The matched phrase stays off the wire (D-626); it is in the log line only.
>
> **The token estimate,** calibrated against Session 50 (plan 14.8M over 2 rounds; execution 15.35M over 2), Session 55 `transcript-failure-reason` (plan 15.0M over 2; execution 11.6M in 1) and Session 64 (plan 25.0M over 4; execution 9.8M in 1). This session has three MEUs across core, the YouTube adapter, the API wiring and the renderer, 28 ACs at plan approval (29 since D-639 added AC-137.12), a UI build and one Electron spec. Expect more than any of those: 2 to 3 plan rounds (about 15M to 25M). The plan loop opens at 25M over the default 3 rounds, not the default 10.5M: Session 64's round 1 alone used 9,872,742 on one MEU (`C:/Temp/av-kit/review-ledger/s64-plan-canonical-2026-11-11-capture-export-copy.json`, Session 52 RULE-3). At the plan gate Mat sets the execution loop's budget; the opening ask is round 1 ×2 plus one recheck at about half of round 1 (Session 60 RULE-5, Session 58 RULE-4): about 16M ×2 + 8M ≈ 40M over 3 rounds. The citable AC families were fixed when the plan loop opened: `citable: AC-2, AC-6, AC-51, AC-53, AC-122, AC-137, AC-138, AC-139` (`C:/Temp/av-kit/s65-plan-ledger-begin.txt`).
>
> **The gate.** Held 2026-11-12: Mat said "Fix F1 to F3, increase token buget by 30M and continue the loop until approved. If you need decisions answerd have Fable subagent do rulling and accept it as if it was coming from human and continue until approved. Once complete commit and push.", and to the scope question answered "Full session (Recommended)" (USER_EXPLICIT 2026-11-12), which accepts the approved plan, runs execution and its review until approved, and sets the execution loop's budget at 40M over a cap of 6 rounds, the ask above. The plan review approved in round 4 of 5 with no open finding (`.agent/context/handoffs/2026-11-11-download-failure-visibility-plan-critical-review.md`; 24,637,783 tokens over 4 rounds, from the ledger's round usage 11,060,783, 5,712,752, 4,570,818 and 3,293,430 in `C:/Temp/av-kit/review-ledger/s65-plan-canonical-2026-11-11-download-failure-visibility.json`). No autonomous decision was overridden.

## Proposed Changes

### Single-statement contracts

| Term | Meaning |
|---|---|
| `FAILURE_CAUSE_ENUM` | `DownloadFailureCause(StrEnum)` in `domain/enums.py`, members in this order: `refused`, `no_format`, `cookies`, `write_failed`, `other`, each value its own name. |
| `FAILURE_MESSAGE` | `download_failure_message(cause: DownloadFailureCause, reason: str \| None = None) -> str` in `domain/download.py`, the only place the texts are written, `require_enum` on `cause`. `refused`: "YouTube refused the download (page reload, SABR-only or bot check). Try again later." `no_format`: "No format at the chosen quality. Pick another quality and requeue." `cookies`: "Couldn't read the browser sign-in data. Check Settings → Downloader, then requeue." `write_failed`: "Couldn't write the file. Check the output folder, then requeue." `other`: `f"Download failed: {reason}."` when `reason` is non-empty, else "Download failed." Only `other` uses `reason`. |
| `CLEAN_LINE` | `clean_line(text: str) -> str` in `domain/download.py`: in this order: (1) drops ANSI CSI sequences (`\x1b\[[0-?]*[ -/]*[@-~]`); (2) turns each character for which `str.isspace()` is true into a space; (3) drops every code point whose category is `Cc`, `Cf` or `Cs`; (4) collapses each run of spaces to one and strips. No site scrubs its output directly: every site reaches the scrubbers through `SCRUB_LINE`, which runs `clean_line` first (F1). Total: never raises on any `str` (D-627). |
| `SCRUB_LINE` | `scrub_line(text: str) -> str` in `services/download.py`, pure: the text a site keeps. In this order: (1) `marked` is `text` with each ANSI CSI sequence (`CLEAN_LINE`'s pattern) replaced by `\x00`, then each character for which `str.isspace()` is true, other than U+0020, replaced by `\t`, and each other `Cc`, `Cf` or `Cs` code point replaced by `\x00`; (2) `homed` is `marked` with the home folder as `~` (private `_scrub_split_home`): it matches as `scrub_home` matches, with the parts of `health.home_folder()` (called through the module at each call, so a test's patch of `health.home_folder` reaches it), the separators `\\`, `/` or a doubled `\\`, the same left boundary (no word character, separator, `.`, `~` or `-` just before) and the same case rule, but with any run of `\t` and `\x00` allowed between any two of its characters, and a right boundary of a run of `\t` and `\x00` then a separator or a quote, or a run of `\t`, `\x00` and U+0020 then the end; (3) `readable` is `clean_line(homed)` and `joined` is `clean_line(homed.replace("\t", ""))`; (4) with `scrub(x)` = `redact_message(replace_links(scrub_home(x)))`, `console_field`'s order without its cut, it returns `scrub(joined)` when that differs from `joined`, and `scrub(readable)` otherwise. The home step runs before any character is removed, so its left boundary is the character the line really has there: a tab, a NUL or an ANSI code before the home path is a boundary, as it is for `scrub_home` on the raw line, and choosing `joined` can't undo the match (round 3 F1). It removes every home path that `scrub_home` removes from `readable` or from `joined`, and on a text with no `\t`, no `\x00` and no trailing space it gives exactly `scrub_home`'s result. A `REDACT_NEEDLES` entry and a URL hold no whitespace, so every needle and link that `text` holds, whole or split by any whitespace character but U+0020 (U+0085, U+2028, a tab, a line break) or by a code point `clean_line` drops, is whole in `joined` (round 2 F1); a needle or link whole in `readable` is whole in `joined` too, so the readable branch is taken only when neither form holds one. A plain space is a split that stays, as it is today: `co okie` is two words, and a home path joined straight onto a word character, `.`, `/`, `~` or `-`, or followed by a space and then more than spaces, is kept as `scrub_home` keeps it. When nothing is scrubbed, the readable form with its spaces is kept, so AC-137.4's outputs hold; when something is, the kept text loses only the other whitespace characters. Total: never raises on any `str` (D-627). |
| `FAILED_ERROR` | `DownloadFailedError(DomainError)` in `domain/errors.py`, built `DownloadFailedError(cause, detail)`; `.cause` is the `DownloadFailureCause` and `.detail` the raw first line; `str(err)` is `f"download failed: {cause.value}"`, so no yt-dlp text reaches a generic error path. Appended last to `DOMAIN_ERROR_TYPES` (D-631). |
| `FAILURE_CAUSE` | `classify_download_error(text: str, sabr_matched: bool) -> tuple[DownloadFailureCause, str]` in `youtube/adapter.py`, pure. `detail` is `first_line(text)` (in `services/download.py`, pure and total: the first line, split only at CR, LF and CRLF, that `clean_line` leaves non-empty, returned as written, else `""`) with only a leading `ERROR:` and the ANSI codes and whitespace before and after it dropped (`_ERROR_PREFIX`), so yt-dlp's coloured prefix goes too and every other character stays for `scrub_line` (D-639; execution round 1 F1: cleaning here removed the split marks `scrub_line` reads, and `splitlines` cut a home path at U+2028 or U+0085). The cause is the first `FAILURE_CAUSE_NEEDLES` entry whose case-folded needle is a substring of the case-folded `text`, in this order: `refused` ("the page needs to be reloaded", "confirm you're not a bot", "confirm you’re not a bot"), `no_format` ("requested format is not available", "no video formats found", "only images are available"), `cookies` ("could not copy chrome cookie database", "failed to decrypt with dpapi", "cookies database"), `write_failed` ("unable to open for writing", "unable to write data"); a text in which `sabr_phrase` finds a phrase is `refused` (row 3 calls the row 1 stub, which finds none, so this branch starts working in row 4 and is tested by AC-138.2, F3); otherwise `other`. A `no_format` result becomes `refused` when `sabr_matched` (D-636). The age gate is checked before this, as today. |
| `FAILURE_RAISE` | In `YouTubeAdapter.download`: a `DownloadError` that isn't the age gate raises `DownloadFailedError(*classify_download_error(str(exc), logger.sabr_detected))` from it; an `OSError` outside cookie file mode raises `DownloadFailedError(write_failed, f"{type(exc).__name__}: {exc.strerror or ''}".rstrip(": "))` from it, never the filename (D-637); file mode still raises `CookieTestError`. "download completed without an output file" stays a `DomainError`. |
| `FAILURE_LOG` | In `DownloadService._run_one`: `download.started` INFO with `job_id` and `video_id`, before the port call; `download.done` INFO with the same fields, after the Done commit; on each failure branch except Cancelled, `download.failed` ERROR with `job_id`, `video_id`, `error` = the stored message and `detail` = `scrub_line(raw)`, where `raw` is `.detail` for a `DownloadFailedError` and `first_line(str(exc))` otherwise (D-639). The stored message is `download_failure_message(cause, reason)`: the error's own cause for `DownloadFailedError`, `cookies` for `CookieTestError`, `other` for any other `DomainError` or `Exception`; `reason` (for `other` only) is `safe_reason(scrub_line(raw)) or type(exc).__name__` (D-638). AgeRestricted keeps its stored text and logs `download.failed` with it (D-633). Cancelled logs nothing new (D-634). |
| `CARD_REASON` | `DownloadListItem` gains `error_message?: string \| null`; `DownloaderPage` maps it to `QueueCardJob.errorMessage`. `QueueCard` is unchanged. |
| `SABR_MATCH` | `SABR_PHRASES = ("forcing sabr", "missing a url", "require a gvs po token", "sabr")` and `sabr_phrase(text: str) -> str \| None` in `youtube/adapter.py`: the first phrase in that order with `re.search(rf"\b{re.escape(p)}\b", text.casefold())`, else `None`. Replaces `SABR_LOG_NEEDLES`, which is removed (D-623, D-624). |
| `SABR_SCAN` | `_YtDlpLogger.matched_phrase: str \| None`, set from the first line that has a phrase and never changed after; `sabr_detected` becomes a read-only property, `matched_phrase is not None`. Every logger method scans. |
| `SABR_STATUS_PHRASE` | `SABRStatus.matched_phrase: str \| None = None`, the last field; `SABR_STATUS_FIELDS` gains it last. A non-`None` value must be a non-empty `str` on `mode` Active with `source` Detected; any other combination raises `ValidationError`. |
| `SABR_RESULT` | `check_sabr_status` returns `matched_phrase=logger.matched_phrase` on Active; `DownloadService.check_sabr` carries it into the status it stores. Not on the wire (D-626). |
| `SABR_LOG` | `download.sabr_check` INFO with `detail` `"Active, matched '<phrase>'"` or `"Inactive, no phrase matched"`; on failure `download.sabr_check` ERROR with `error` = `scrub_line(str(exc))`, then the error is re-raised unchanged. `download.sabr_force` INFO with `detail` `"Active, forced"`; `download.sabr_clear` INFO with `detail` `"Inactive, cleared"`. One line per call. |
| `SABR_SHOWN` | `sabrResultText(snapshot: SabrSnapshot \| undefined): string` in `sabr-panel.ts`: `checking` → "Checking…"; `active` → "SABR active — quality limited to 360p", plus " · forced HH:MM:SS" when `source` is `forced` or " · checked HH:MM:SS" otherwise, when `checked_at` parses; `inactive` with a time → "SABR inactive · checked HH:MM:SS" when `source` is `detected`, "SABR inactive · cleared HH:MM:SS" when it is `null`; no snapshot or no parseable time on inactive → "SABR not checked". `HH:MM:SS` is the local time, zero-padded. The `sabr-status` panel loses its `hidden` attribute and holds this text; it stays in the Advanced disclosure beside the Check, Force and Clear buttons, so it is shown whenever those buttons are, and the disclosure's open rule is unchanged (review Q7); the separate `Checking…` line goes (D-635). A failed check shows through the page's existing `run`/`setError` path. |
| `YTDLP_LINE` | `_YtDlpLogger` (`module="yt-dlp"`, event `"yt-dlp"`): `warning(text)` logs WARNING; `error(text)` logs ERROR when `text` starts with `ERROR:`; both always, with `detail=scrub_line(str(text))`. `debug`, `info`, and an `error` without the prefix (D-632) log DEBUG with the same `detail` only when `debug_enabled`. A line whose `detail` is empty logs nothing. No `message` field. |
| `YTDLP_LIVE` | `YouTubeAdapter(yt_dlp_debug: Callable[[], bool] \| None = None)`; each public call reads `yt_dlp_debug()` once (`None` reads as `False`, a raising source as `False`) and builds `_YtDlpLogger(debug)`; `_base_opts` reads `logger.debug_enabled` for `quiet` and sets `verbose` to the same value. `wiring.py` passes `lambda: settings.get("downloader", "yt_dlp_debug") is True` with a `# LIVE_SOURCE` comment, and the startup read goes. |

### Pins that move

| Pin | Where | From → to | Row |
|---|---|---|---|
| `DOMAIN_ERROR_TYPE_NAMES` | `tests/unit/test_domain.py:181-207` | gains `"DownloadFailedError"` last, after `"ExtractError"` | 1 |
| `SPEC_SABR_STATUS_FIELDS` | `tests/unit/test_domain.py:326` | gains `"matched_phrase"` last | 1 |
| `DOMAIN_ERROR_TYPES` constructor walk | `tests/unit/test_domain.py:221` | `cls("domain failure")` becomes `cls(*ERROR_ARGS.get(cls.__name__, ("domain failure",)))`, with `ERROR_ARGS = {"DownloadFailedError": (DownloadFailureCause.other, "domain failure")}` beside the walk; the `isinstance` and `type(err) is cls` asserts are unchanged; passes in row 1 (F2) | 1 |
| Unmapped download error type | `tests/integration/test_youtube_adapter.py:472`, in `test_ac_6_10_age_gate_and_unmapped_download_error` | `type(domain_err.value) is DomainError` becomes `is DownloadFailedError`, plus `.cause is DownloadFailureCause.other` and `.detail == "boom"`; `pytest.raises(DomainError)`, the `__cause__` assert and the not-AgeRestricted assert stay; fails by assertion in row 2a's receipt and passes in row 3 (F2) | 2a |
| Media download error type | `tests/integration/test_youtube_adapter.py:736`, in `test_ac_76_6_age_gate_and_media_download_keep_their_types_neg` | `type(failed.value) is DomainError` becomes `is DownloadFailedError`, plus `.cause is DownloadFailureCause.other` and `.detail == "boom"`; the rest stays; fails in row 2a and passes in row 3 (F2) | 2a |
| Test-local `SABR_LOG_NEEDLES` | `tests/integration/test_youtube_adapter.py:87`, used by AC-6.11 at `:487-493` | the tuple each needle of which must set `sabr_detected` becomes the four `SABR_PHRASES` plus the two old android and ios phrases, renamed `SABR_LINE_PHRASES`; it fails in row 2b's receipt (the scan still reads the old needles) and passes in row 4 | 2b |
| AC-122.16 | `tests/unit/test_transcript_metadata.py:324-353` | the debug line is logged with `_YtDlpLogger(False)`; it expects no `yt-dlp` event at all (an empty capture, not only no title) and nothing in the Console (review Q8); the debug-on half moves to AC-139.6 | 2c |
| `"SABRDetectedError" not in source` | `tests/integration/test_youtube_adapter.py:495` | unchanged; still holds | — |

### Where values go (Session 50 RULE-1, Session 53 RULE-1, Session 61 RULE-1)

- **yt-dlp's error text** comes from `DownloadError` and reaches `classify_download_error`, then `DownloadFailedError.detail`, as written but for its `ERROR:` prefix (D-639). From there: the `download.failed` line's `detail` after `scrub_line` (the home folder matched across split characters first, then `clean_line`, then `scrub_home`, `replace_links` and `redact_message`, on the joined form when that finds something), then the Console after `console_field`; and, for `other` only, the stored `error_message` after `scrub_line`, then `safe_reason`, which reaches SQLite, `GET /downloads`, the MCP `avkit_download` list and the card. Its writers: yt-dlp, and the extractors it runs. A cookie value, a home path, a URL, a lone surrogate and a NUL are each traced (AC-137.9, AC-137.11), and the first three again with a NUL, an ANSI code, U+0085 or U+2028 inside them (AC-137.7, AC-137.9; F1), and a home path after a tab or a NUL in a line where a cookie is also scrubbed (AC-137.4, AC-137.7, AC-137.9; round 3 F1). The whole path, from a mocked `YoutubeDL` through the real adapter, the service and SQLite to the Console line, is traced with split forms by AC-137.12 (execution round 1 F1).
- **An `OSError`'s text** never leaves the adapter: only its type name and `strerror` reach `detail` (D-637).
- **The stored message** for the four named causes comes from `FAILURE_MESSAGE` only.
- **The matched SABR phrase** comes from `SABR_PHRASES`, never from yt-dlp's text, so the `detail` line holds only a constant.
- **A failed SABR check's text** reaches the `download.sabr_check` ERROR line after `scrub_line`, and the 422 body as the route maps it today.
- **yt-dlp's logger lines** reach the Console through `YTDLP_LINE` only, each `detail` after `scrub_line`, split forms included (AC-139.5); with debug off a debug or info line reaches nothing (AC-139.3, AC-122.16).
- **The debug setting** comes from `SettingsService` at each public call (`YTDLP_LIVE`); its writer is `PUT /settings`, from the Settings switch.

### Spec text (D3)

| File | Lines at `003e5b1` | Change |
|---|---|---|
| `docs/build-plan/01-domain-layer.md` | the `SABRStatus` row (`:133-141`) and the errors table (`:534-555`) | A `matched_phrase` row; a `DownloadFailedError` row |
| `docs/build-plan/02-infrastructure.md` | §SABR Passive row (`:378`), §download Debug row (`:362`), §SABR check result Phrases row (`:540`), §yt-dlp log detail Control row (`:558`) | Passive and Debug name the new sections; Phrases says whole words and `require a gvs po token` (D-623, D-624, D-629); Control names the existing "yt-dlp debug" switch (D-630); a Delivered note after each residual section |
| `docs/build-plan/03-service-layer.md` | after §Download failure reason's Tests row (`:716`) | A Delivered note |
| `docs/build-plan/06-gui.md` | §SABR detection sources (`:462-466`), the yt-dlp debug toggle row (`:345`) | Detection names 02 §SABR check result; the toggle row names the Settings → Downloader switch (D-630) |
| The grouping file | before the D-539 brief (`:179`) | A `## 9. Decision Briefs` heading, so §8 parses (D-628); row 65 of the tracker (`:149`) marked executed |

Row 6 re-reads each anchor before it writes (Session 51 RULE-3) and cites the lines as they read then. Each Delivered note names the mechanism ids, the ACs and this plan folder, in the format of Session 64's note in 09.

### MEU-137 `svc-download-failure-reason`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `DownloadJob.error_message` | `domain/download.py` | `FAILURE_MESSAGE` output or AgeRestricted's text | — |
| `GET /downloads` item `error_message` | `schemas/downloads.py` (unchanged) | `str \| None` | unchanged |
| `DownloadListItem` | `useDownloadQueue.ts` | `error_message?: string \| null` | — |
| `download.failed` log line | `services/download.py` | `job_id`, `video_id`, `error`, `detail` | Console keeps `CONSOLE_FIELDS` only |

#### Acceptance Criteria

Test names start `test_ac_137_<n>_` (Python) and `AC-137.<n>` (Vitest). New Python files are LF.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-137.1 | Unit | Type characterisation of row 1's names: `DownloadFailureCause` has exactly the five members in order with equal values; `DownloadFailedError` is a `DomainError` with `.cause` and `.detail` and `str` `download failed: other`, and is last in `DOMAIN_ERROR_TYPES`; `download_failure_message` has positional `cause` and `reason=None`; `clean_line` takes one `str`; `classify_download_error` takes `text` and `sabr_matched`; `SABRStatus` ends with `matched_phrase` defaulting to `None`. Passes from row 1 and runs as a guard. In `tests/unit/test_download_failure_visibility.py`. | 03 Message | Signature drift fails |
| AC-137.2 | Unit | `FAILURE_MESSAGE`: each named cause gives its exact text with and without a `reason`; `other` with `"x"` gives `Download failed: x.`, with `None` and `""` gives `Download failed.`; a non-member cause raises `ValidationError`. | 03 Message | `reason` ignored by the named causes |
| AC-137.3 | Unit | Each cause's message, with and without a `reason`, is non-empty, ends with `.`, and holds no `REDACT_NEEDLES` entry, URL or path separator. | 03 Message; D-247 | Needle sweep |
| AC-137.4 | Unit | `CLEAN_LINE`: `"\x1b[0;31mERROR:\x1b[0m bad"` → `"ERROR: bad"`; a lone `\ud800`, `\x00`, `\x07`, `\x7f` and `\x9b` are dropped; `"a\r\n\tb"` → `"a b"`; `"a\u2028b"` → `"a b"`; `"co\x00okie"` → `"cookie"`; `"a\u200bb"` → `"ab"`; `"\u202e"` → `""`; `"C:\\Us\x1b[0mers"` → `"C:\\Users"`; `""` → `""`; a string of only controls → `""`; `"Łódź ✓"` is unchanged (Session 53 RULE-1). `SCRUB_LINE`, with the home folder set to a marker path: `"co\x85okie=SECRET"` and `"co\u2028okie=SECRET"` → `"[REDACTED]"`; `"https:\u2028//e.example/private"` → `"[link]"`; the marker path with `\x85` inside its user name, then `\\v.mp4`, → `"~\\v.mp4"`; `"a\tb cookie=X"` → `"ab [REDACTED]"`; `"a\u2028b"` → `"a b"` (nothing is scrubbed, so the readable form is kept); `"co okie=x"` is unchanged; `""` and a lone `\ud800` → `""` (round 2 F1); and in a mixed line (round 3 F1): `"at\t<marker>\\v.mp4 cookie=SECRET"`, the same with `\x85` inside the marker's user name, and `"at\x00<marker>\\v.mp4 cookie=SECRET"` each → `"at~\\v.mp4 [REDACTED]"`; `"at\t<marker>\\v.mp4"` → `"at ~\\v.mp4"`; `"x<marker>\\v.mp4"` and `"<marker>2\\v.mp4"` are unchanged, as `scrub_home` keeps them. | D-627 | Surrogate, control and empty |
| AC-137.5 | Unit | `FAILURE_CAUSE`: each needle of each cause, in upper and mixed case, inside a captured-shape `ERROR: [youtube] gKcOjnDJfzk: …` line, gives that cause and the line without `ERROR: `; both apostrophes of the bot check; a coloured `\x1b[0;31mERROR:\x1b[0m [youtube] x: The page needs to be reloaded.` gives `refused` and the line without the prefix; a multi-line text gives its first non-empty line; "Requested format is not available" gives `no_format` with `sabr_matched=False` and `refused` with `True`; an unknown text gives `other`; `""` gives `other` and `""`. | 03 Message; D-636 | The SABR override, the unknown text |
| AC-137.6 | Integration | `FAILURE_RAISE` with a mocked `YoutubeDL`: a `DownloadError("ERROR: [youtube] x: The page needs to be reloaded.")` raises `DownloadFailedError` `refused` with that detail; the warning `WARNING: [youtube] x: Some formats require a GVS PO Token which was not provided` logged before a `Requested format is not available` error makes it `refused` (both the old `SABR_LOG_NEEDLES` and `SABR_PHRASES` hold that phrase, so it passes on row 3's scanner; the captured missing-a-URL line is AC-138.5's, F3); an `OSError(13, "Permission denied", "<marker>/x.mp4")` in browser mode raises `write_failed` with detail `PermissionError: Permission denied` and no marker; the same in file mode raises `CookieTestError`; the age gate still raises `AgeRestrictedError`. In `tests/integration/test_youtube_adapter_visibility.py`. | 03 Message; D-637 | The filename is absent |
| AC-137.7 | Unit | `FAILURE_LOG` storage with a fake port and the real SQLite UoW: each `DownloadFailedError` cause stores its message; `CookieTestError` stores the `cookies` message; `DomainError("download completed without an output file")` stores `Download failed: download completed without an output file.`; `RuntimeError("")` stores `Download failed: RuntimeError.`; a reason with a cookie needle stores ` [REDACTED]` in place of the rest, a home path stores `~`, a URL stores `[link]`, a 500-character reason is cut to 200 before the `.`; and the split forms (F1): `co\x00okie=SECRET` stores ` [REDACTED]` with no `SECRET`, `https\x00://e.example/private` stores `[link]` with no `e.example`, and a home path with `\x1b[0m` inside its user name stores `~` with no home marker; and the whitespace splits (round 2 F1): `co\x85okie=SECRET` and `co\u2028okie=SECRET` each store ` [REDACTED]` with no `SECRET`, `https:\u2028//e.example/private` stores `[link]` with no `e.example`, and a home path with `\x85` inside its user name stores `~` with no home marker; and the mixed line (round 3 F1): `at\t<home split by \x85>\\v.mp4 cookie=SECRET` stores `Download failed: at~\\v.mp4 [REDACTED].` with no home marker and no `SECRET`. | 03 Message | Each branch, the redaction |
| AC-137.8 | Unit | `FAILURE_LOG` lines with `structlog.testing.capture_logs`: a success logs `download.started` then `download.done`, once each, with `job_id` and `video_id`, `started` before the port is called (a recording fake) and `done` after the row is Done; each failure branch logs `download.started` then exactly one `download.failed` at error level with `error` equal to the stored message and `detail` equal to `scrub_line(raw)`; AgeRestricted logs `download.failed` with `video is age-restricted`; Cancelled logs no `download.failed` and no `download.done`. | 03 Log | Cancelled logs nothing |
| AC-137.9 | API | The Console trace on the real stack (Session 54 RULE-2): `HealthService` is built first; a fake port raises `DownloadFailedError(other, "ERROR: x at <HOME-marker>\\v.mp4 https://e.example/p cookie=SECRET")`; `/health/console` holds one `download.failed` line whose `error` and `detail` show `~`, `[link]` and ` [REDACTED]`, and neither the home marker nor `SECRET` appears in the ring, captured stdout or the card's served `error_message`; a second job whose fake raises the split forms, `DownloadFailedError(other, "ERROR: x at <HOME-marker split by \x1b[0m>\\v.mp4 https\x00://e.example/q co\x00okie=SECRET")`, shows `~`, `[link]` and ` [REDACTED]` the same way, with no home marker, `e.example` or `SECRET` in the ring, stdout or the served `error_message` (F1); a third job raises `DownloadFailedError(other, "ERROR: x at <HOME-marker split by \x85>\\v.mp4 https:\u2028//e.example/r co\x85okie=SECRET")`, a fourth `DownloadFailedError(other, "ERROR: x co\u2028okie=SECRET")` and a fifth `DownloadFailedError(other, "ERROR: x at\t<HOME-marker split by \x85>\\v.mp4 cookie=SECRET")`, each checked the same way (rounds 2 and 3 F1); the positive control logs the home marker once and finds it as `~`. In `tests/e2e/test_api_download_visibility.py`. | 03 Log, Done; D-247 | Marker absence with a positive control |
| AC-137.10 | Renderer | `CARD_REASON`: a Failed item with `error_message` shows that text on its card's meta line; a Failed item with `null` and one with the key missing show the placeholder; an AgeRestricted item shows its text. In `ui/tests/unit/downloader-page.behavior.test.ts`. | 03 Card | Missing and null keys |
| AC-137.11 | API | A fake port raising `DownloadFailedError(other, "bad\ud800 x\x00y")`, stores and serves: `GET /downloads` returns 200 with valid JSON whose `error_message` is exactly `Download failed: bad xy.`, and the `download.failed` Console line's `detail` is `bad xy`. In `test_api_download_visibility.py`. | D-627; Session 53 RULE-1 | Surrogate and NUL |
| AC-137.12 | Integration | `FAILURE_CAUSE`, `FAILURE_RAISE` and `FAILURE_LOG` end to end (D-639): a mocked `YoutubeDL` behind the real `YouTubeAdapter.download`, run by `DownloadService` with the real SQLite UoW under `capture_logs`, raises in turn the `DownloadError`s `ERROR: co\tokie=SECRET`, `ERROR: https:\t//e.example/private`, `ERROR: at\x00<marker>\v.mp4 cookie=SECRET`, `ERROR: at <marker>\v.mp4` with a tab inside the marker's user name, the same with U+2028, and a coloured `ERROR:` with U+0085 inside the user name and a second line; then a `RuntimeError` with U+2028 inside the user name and a tab-split cookie (the service's own branch); then `OSError(13, "Permission denied", "<marker>/x.mp4")`. Each job is Failed with one `download.failed` line whose `error` is the stored message. The stored messages are exactly `Download failed: [REDACTED].`, `Download failed: [link].`, `Download failed: at~\v.mp4 [REDACTED].`, `Download failed: at ~\v.mp4.` three times, `Download failed: at ~\v.mp4 [REDACTED].` and the `write_failed` message; the `detail`s are the same text without the frame, and `PermissionError: Permission denied` for the `OSError`. No `secret`, `e.example` or part of the marker's user name appears in any of them. In `tests/integration/test_youtube_adapter_visibility.py`. | D-639; execution round 1 F1 | Split forms through the real adapter |

Guards (Session 54 RULE-1, Session 55 RULE-1): `tests/unit/test_domain.py` (core changes), `tests/unit/test_services.py` (the `DownloadService` tests), `tests/e2e/test_api_downloads.py`, `tests/e2e/test_api_error_surface.py`, `tests/integration/test_youtube_adapter.py`, `tests/integration/test_download_received_quality.py`, `tests/integration/test_api_wiring.py` and `tests/unit/test_transcript_metadata.py`, run in rows 1, 3, 4 and 5 (the files `grep -lE "DownloadService|_run_one|check_sabr|force_sabr|clear_sabr|YouTubeAdapter" tests -r` lists at `003e5b1`). Every caller of what is extended: `_finish` is called from `_run_one` only; `DOMAIN_ERROR_TYPES` is read by `tests/unit/test_domain.py:216` only (`C:/Temp/av-kit/s65/corr-domain-error-types.txt`), and the download path's exact-type pins are `test_youtube_adapter.py:472` and `:736` (§Pins that move, rows 1 and 2a; F2); `DownloadListItem` is read by `useDownloadQueue.ts` and `DownloaderPage.tsx` only (row 1 greps each again into `s65-anchors.txt`).

#### Spec Sufficiency

| Behavior | Classification | Resolution |
|---|---|---|
| Card | Local Canon | 03 Card; `CARD_REASON` |
| Messages and causes | Local Canon | 03 Message; D-636, D-637, D-638 |
| Log lines | Local Canon | 03 Log; D-633, D-634 |
| Cleaning | Local Canon | D-627 |

### MEU-138 `infra-sabr-check-result`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `SABRStatus.matched_phrase` | `domain/download.py` | `SABR_STATUS_PHRASE` | — |
| `GET/POST /downloads/sabr*` | `schemas/downloads.py` `SABRStatusOut` | unchanged: `mode`, `source`, `checked_at` | `matched_phrase` not serialised (D-626); OpenAPI `--check` unchanged |
| `sabr-status` panel | `DownloaderPage.tsx`, `sabr-panel.ts` | `SABR_SHOWN` | — |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-138.1 | Unit | Type characterisation: `SABR_PHRASES` equals the four phrases in order; `SABR_LOG_NEEDLES` is absent from the adapter module; `sabr_phrase` takes one `str`; `SABR_STATUS_FIELDS` ends `"matched_phrase"`; `_YtDlpLogger.sabr_detected` is a property. In `test_download_failure_visibility.py`. | 02 Phrases | Absence pin |
| AC-138.2 | Unit | `SABR_MATCH`: the captured 2026.10.26 line "WARNING: [youtube] x: Some android client https formats have been skipped as they are missing a URL. YouTube may have enabled the SABR-only streaming experiment …" gives `missing a url`; "forcing SABR" in any case gives `forcing sabr`; the three old phrases are matched (`require a gvs po token` itself; `android client sabr formats require` and `ios client sabr formats require` through `sabr`); "SABR-only" gives `sabr`; "Sabrina", "the sabre", "sabrs" and "PO Token required for GVS" give `None`; a line with none gives `None`; `""` gives `None`; `classify_download_error("ERROR: [youtube] x: YouTube is forcing SABR streaming for this client", False)` gives `refused`, the phrase branch of `FAILURE_CAUSE`, moved here from AC-137.5 because it needs `SABR_MATCH` (F3). | 02 Phrases; D-623, D-624 | The near-words |
| AC-138.3 | Unit | `SABR_SCAN`: a logger fed a plain line, then the captured line, then a "forcing SABR" line has `matched_phrase` `missing a url` and `sabr_detected` True; each of `debug`, `info`, `warning` and `error` scans; a fresh logger has `None` and False; `sabr_detected` can't be assigned. | 02 Passive | First match kept |
| AC-138.4 | Unit | `SABR_STATUS_PHRASE`: Active, Detected, `"sabr"` builds; Active Forced with a phrase, Inactive with a phrase, Active Detected with `""` and with `1` each raise `ValidationError`; `matched_phrase` omitted is `None`; AC-2.6's `TypeError` for a missing field still holds. | 01 SABRStatus | Each invalid pair |
| AC-138.5 | Integration | `SABR_RESULT`: `check_sabr_status` with a mocked `YoutubeDL` whose extract logs the captured line returns Active, Detected, `missing a url`; with no phrase, Inactive and `None`; `download` with a mocked `YoutubeDL` that logs the captured line as a warning and then raises `DownloadError("ERROR: [youtube] gKcOjnDJfzk: Requested format is not available")` raises `DownloadFailedError` `refused`, the goal's first trace (F3; it fails in row 2b because the old needles miss the line); `DownloadService.check_sabr` stores the phrase it got; `GET /downloads/sabr` still returns exactly `{mode, source, checked_at}`. In `test_youtube_adapter_visibility.py` and `test_api_download_visibility.py`. | 02 Log; D-626 | Off the wire |
| AC-138.6 | API | `SABR_LOG` on the real stack: `POST /downloads/sabr/check` with a fake port returning Active and `sabr` logs exactly one `download.sabr_check` line with `detail` `Active, matched 'sabr'`; Inactive logs `Inactive, no phrase matched`; `force` logs one `download.sabr_force` `Active, forced`; `clear` one `download.sabr_clear` `Inactive, cleared`; each shows in `/health/console`. In `test_api_download_visibility.py`. | 02 Log, Tests | Exactly one line each |
| AC-138.7 | API | A failed check: a fake port raising `ExtractError("x cookie=SECRET")` gives the route's 422, one `download.sabr_check` ERROR line whose `error` shows ` [REDACTED]` and not `SECRET`, and the stored SABR status is unchanged. Renderer: a rejected check shows its error through `setError`; this half characterises today's page and passes from row 2b. In `test_api_download_visibility.py` and `downloader-page.behavior.test.ts`. | 02 Shown | Status unchanged on failure |
| AC-138.8 | Renderer | `SABR_SHOWN`: `sabrResultText` for each row of the contract with a local time built from parts (`09:05:07`), an unparseable `checked_at`, and `undefined`; after opening the Advanced disclosure the way a user does before clicking Check SABR, the panel is visible (`toBeVisible`, which also checks the disclosure around it) with "SABR inactive · checked 09:05:07" after an Inactive check and with "SABR active — quality limited to 360p · checked 09:05:07" after an Active one; the AC-53.2 and AC-53.4 pins still hold. In the new `ui/tests/unit/sabr-panel.test.ts` and `downloader-page.behavior.test.ts`. | 02 Shown, Tests | Inactive is shown |

Guards: AC-53.2 (`ui/tests/e2e/download-queue.test.ts:1640-1653`) in the gate's `ui-electron` step; `downloader-page.behavior.test.ts` `:1070-1074` and `:1158-1167`; `test_youtube_adapter.py` SABR tests. Every caller of `SABRStatus(...)`: grepped in row 1 into `s65-anchors.txt`; the production callers use keywords, and the fakes at `tests/e2e/test_api_downloads.py:56`, `:149`, `:153` and `:157` build `SABRStatus` positionally with three values, which stays valid because the new last field defaults to `None` (review Q6).

#### Spec Sufficiency

| Behavior | Classification | Resolution |
|---|---|---|
| Phrases and matching | Human-approved | 02 Phrases; D-623, D-624, D-629 |
| Result shown | Local Canon | 02 Shown; D-635 |
| Log lines | Local Canon | 02 Log; D-626 |
| Passive phrase carry | Out of Scope | §Out of Scope |

### MEU-139 `infra-ytdlp-log-detail`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| yt-dlp log line | `youtube/adapter.py` `_YtDlpLogger` | `YTDLP_LINE` | `detail` only |
| `downloader.yt_dlp_debug` | `services/settings.py` (unchanged) | boolean, default False | unchanged |
| Settings switch | `SettingsPage.tsx` (unchanged) | `settings-leaf-yt_dlp_debug` | — |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-139.1 | Unit | Type characterisation: `YouTubeAdapter`'s `yt_dlp_debug` parameter is keyword, `Callable[[], bool] \| None`, default `None`; `_YtDlpLogger(debug_enabled)` exposes `debug_enabled`; `_base_opts` takes the logger only. In `test_download_failure_visibility.py`. | 02 Live | Signature drift |
| AC-139.2 | Unit | `YTDLP_LINE` with debug off: `warning("x")` logs one WARNING `yt-dlp` line with `detail` `x`; `error("ERROR: y")` one ERROR line with `detail` `ERROR: y`; neither has a `message` key. | 02 Warnings and errors | Debug off still logs |
| AC-139.3 | Unit | With debug off, `debug`, `info` and `error("Traceback …")` log nothing; with it on, each logs one DEBUG line with its `detail`; `warning("")`, `warning("\x1b[0m")` and `debug("\x00")` with debug on log nothing. | 02 Debug lines; D-622, D-632 | Off logs nothing |
| AC-139.4 | Integration | `YTDLP_LIVE`: a recording source returning False then True gives `quiet` True and `verbose` False on the first `download` and the reverse on the second, and is read exactly once per public call (`download`, `extract_info`, `check_sabr_status`, the cookie test); a source that raises reads as False; `None` reads as False. `wiring.py` builds the adapter with a source that follows a `PUT /settings` change between two calls on the real stack. In `test_youtube_adapter_visibility.py` and `tests/integration/test_api_wiring.py`. | 02 Live | Read once, live |
| AC-139.5 | API | Redaction on the real stack (Session 54 RULE-2): with `HealthService` built first, a warning holding the home marker, a URL and `cookie=SECRET` reaches `/health/console` with `~`, `[link]` and ` [REDACTED]`, and neither the marker nor `SECRET` is in the ring or captured stdout; so do the whitespace splits (round 2 F1): `WARNING: x at <HOME-marker split by \u2028>\\v.mp4 co\x85okie=SECRET` shows `~` and ` [REDACTED]`, and `WARNING: https:\x85//e.example/s co\u2028okie=SECRET` shows `[link]` and ` [REDACTED]`, with no marker, `e.example` or `SECRET` in the ring or stdout; and the mixed line `WARNING: at\u2028<HOME-marker>\\v.mp4 cookie=SECRET` shows `at~` and ` [REDACTED]` with no marker or `SECRET` in the ring or stdout (round 3 F1); positive control as AC-137.9. In `test_api_download_visibility.py`. | 02 Redaction | Marker absence |
| AC-139.6 | Unit | With debug on, a debug line holding a title marker reaches the Console redacted (D-622); AC-122.16's debug-off half still finds no marker. In `test_transcript_metadata.py`. | D-622 | Debug-off half |
| AC-139.7 | Integration | The Session 55 RULE-3 trace: a mocked `YoutubeDL` whose `extract_info` calls `params["logger"].warning(...)` with a marker reaches the Console row through a real `HealthService` and a recording fake, with debug off. In `test_youtube_adapter_visibility.py`. | 02 Warnings and errors | The whole path |
| AC-139.8 | Renderer | The existing switch saves: toggling `settings-leaf-yt_dlp_debug` sends `PUT` with `{downloader: {yt_dlp_debug: true}}` and then `false`. A characterisation of the existing switch (D-630): it passes from row 2c and runs as a guard. In `ui/tests/unit/settings-page.test.ts`. | 02 Control, Tests | Both directions |
| AC-139.9 | Unit | A warning holding a lone surrogate, a NUL, `\x1b[31m` and a 400-character tail logs a `detail` with no surrogate, NUL or escape; the Console line is at most `FIELD_LIMIT` per field; an empty warning logs nothing (Session 53 RULE-1). In `test_download_failure_visibility.py`. | D-627 | Surrogate, control and empty |

Guards: every `_YtDlpLogger(...)` site (`adapter.py:446`, `:469`, `:480`, `:495`, `:556`, `:588`) and every `YouTubeAdapter(...)` construction (`wiring.py:156-162` and the tests, grepped in row 1); `tests/unit/test_transcript_metadata.py`; `tests/integration/test_api_wiring.py`.

#### Spec Sufficiency

| Behavior | Classification | Resolution |
|---|---|---|
| Warning and error lines | Local Canon | 02 Warnings and errors; D-632 |
| Debug lines | Human-approved | 02 Debug lines; D-622 |
| Redaction | Local Canon | 02 Redaction |
| Live setting | Local Canon | 02 Live |
| Control | Local Canon | D-630: the switch exists |

### Files Modified

| File | Action | Summary |
|---|---|---|
| `packages/core/src/avkit_core/domain/enums.py` | Modify | `DownloadFailureCause` (`FAILURE_CAUSE_ENUM`) |
| `packages/core/src/avkit_core/domain/errors.py` | Modify | `DownloadFailedError`, appended to `DOMAIN_ERROR_TYPES` (`FAILED_ERROR`) |
| `packages/core/src/avkit_core/domain/download.py` | Modify | `download_failure_message`, `clean_line`, `SABRStatus.matched_phrase`, `SABR_STATUS_FIELDS` (`FAILURE_MESSAGE`, `CLEAN_LINE`, `SABR_STATUS_PHRASE`) |
| `packages/core/src/avkit_core/services/download.py` | Modify | `scrub_line` and its private `_scrub_split_home`, `first_line`, `_run_one`, `_finish`, `check_sabr`, `force_sabr`, `clear_sabr` (`SCRUB_LINE`, `FAILURE_CAUSE`'s `first_line`, `FAILURE_LOG`, `SABR_RESULT`, `SABR_LOG`) |
| `packages/infrastructure/src/avkit_infra/youtube/adapter.py` | Modify | `SABR_PHRASES`, `sabr_phrase`, `FAILURE_CAUSE_NEEDLES`, `classify_download_error` and its `_ERROR_PREFIX`, `_YtDlpLogger`, `YouTubeAdapter.__init__`, `_base_opts`, `download`, `check_sabr_status` and every public call that builds a logger (`FAILURE_CAUSE`, `FAILURE_RAISE`, `SABR_MATCH`, `SABR_SCAN`, `YTDLP_LINE`, `YTDLP_LIVE`) |
| `packages/api/src/avkit_api/wiring.py` | Modify | The live debug source (`YTDLP_LIVE`) |
| `ui/src/renderer/src/features/downloader/useDownloadQueue.ts`, `DownloaderPage.tsx`, `sabr-panel.ts` | Modify | `CARD_REASON`, `SABR_SHOWN` |
| `tests/unit/test_download_failure_visibility.py`, `tests/integration/test_youtube_adapter_visibility.py`, `tests/e2e/test_api_download_visibility.py`, `ui/tests/unit/sabr-panel.test.ts` | New | The ACs above |
| `tests/unit/test_domain.py`, `tests/unit/test_transcript_metadata.py`, `tests/integration/test_youtube_adapter.py`, `tests/integration/test_api_wiring.py`, `ui/tests/unit/downloader-page.behavior.test.ts`, `ui/tests/unit/settings-page.test.ts` | Modify | §Pins that move; AC-137.10, AC-138.7, AC-138.8, AC-139.4, AC-139.6, AC-139.8 |
| `docs/build-plan/01-domain-layer.md`, `02-infrastructure.md`, `03-service-layer.md`, `06-gui.md` | Modify | §Spec text |

Every function a mechanism names is in this table and in the gate's scope (Session 61 RULE-4). `services/health.py`, `api/routes/downloads.py` and `services/settings.py`, which the grouping names as possible files, don't change: `CONSOLE_FIELDS` already keeps `error` and `detail`, the routes need nothing new (D-626), and the setting and its switch exist (D-630). `openapi.committed.json` doesn't change. `ui/tests/e2e/test-ids.ts` is not touched (the AC-51.6 prefix hash). Line endings at `003e5b1` (`C:/Temp/av-kit/s65-plan-probes.txt`): `domain/download.py`, `errors.py`, `services/download.py`, `adapter.py`, `wiring.py`, `test_domain.py`, `test_youtube_adapter.py`, `test_api_wiring.py`, `settings-page.test.ts`, `02`, `03`, `06`, `current-focus.md` and `metrics.md` are CRLF; `useDownloadQueue.ts`, `sabr-panel.ts`, `test_transcript_metadata.py`, `01`, `known-issues.yaml`, `meu-status.yaml`, `meu-registry.md`, `BUILD_PLAN.md` and the grouping are LF; `DownloaderPage.tsx` (749 CRLF, 221 LF) and `downloader-page.behavior.test.ts` (2096 CRLF, 286 LF) are mixed, and an edit there writes each new line in the ending of the line it follows. Row 0 measures every file again with Python bytes into `s65-anchors.txt`, `enums.py` included, and every row writes with `newline=""` or by byte replacement; a scratch script that edits a tracked file records its ending, writes in it, and fails on mixed endings unless the file was mixed at baseline with the same counts plus its own lines (Session 63 RULE-3). New files are LF.

### Project files

- `docs/execution/plans/2026-11-11-download-failure-visibility/`: `implementation-plan.md`, `task.md`, `baseline.ps1`, `baseline.sha`, `baseline-dirty.txt`, `red-check.py`, `identity.py`, `issue-resolve.py`, `session-gate.ps1`.
- `.agent/context/known-issues.yaml` and its render `.agent/context/known-issues.md`, `.agent/context/triage-output.yaml` (row 6's resolve).
- `.agent/context/meu-status.yaml`, `docs/BUILD_PLAN.md`, `.agent/context/meu-registry.md`, and the grouping file (§9 heading and tracker row 65). If another session holds any of them dirty when row 6 runs, row 6 byte-edits only this session's fields and proves them with `render --check` (Session 61 RULE-5).
- `.agent/context/handoffs/2026-11-11-download-failure-visibility-*.md`, `docs/execution/reflections/2026-11-11-download-failure-visibility-reflection.md`, `docs/execution/metrics.md`, `.agent/context/current-focus.md`.

Not this session's, and never opened: `docs/proposals/2026-11-10-download-logic-divergence-report.md` (hashed only, sha256 `bbaf04eb4a20460affb5b4d87b13ba5b62efd120f3d2fefa8a1a56729fd1c0ec`). Anything another session leaves dirty is named to Mat before any commit.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| A passive SABR detection log line, and the passive phrase on the status | Feature | None | 02 Log names Check, Force and Clear; a download that sees a phrase already turns SABR on |
| The client pin and fallback | Bug | MEU-140, MEU-141 (Session 66) | Their own sections |
| The MP3 convert | Bug | MEU-142 (Session 67) | Its own section |
| A Cancelled log line | Feature | None | D-634 |
| `app.log_level`, stored and unread | Bug | None; raised in the MEU-139 handoff for Mat | Named in `YTDLP-LOG-TEXT-DROPPED`'s root cause; not in 02's rules |
| `add_to_queue_extract_start` logs `url=` (`services/download.py:178`) | Privacy | None; raised in the MEU-137 handoff for Mat | `url` is not a `CONSOLE_FIELD`, so the Console drops it and `HealthService` prints only the safe message; it is a raw value in the event dict before the processor (Session 50 RULE-1: raised, not fixed, since no surface shows it) |
| Session 64's items: 16-bit gray in `_encode_view` and `bake`, the other strict MCP actions echoing unknown keys, PNG transparency keys in crop and the view, `avkit_capture.export` in `BASELINE_PENDING`, the validator counting ACs by family only | Mixed | None | Named for Mat in Session 64's handoff; not this session's |

## BUILD_PLAN.md Audit

MEU-137 (phase 3, P2, matrix 3.19, anchor `download-failure-reason-residual`), MEU-138 (phase 2, P2, matrix 2.6, anchor `sabr-check-result-residual`) and MEU-139 (phase 2, P2, matrix 2.7, anchor `ytdlp-log-detail-residual`) are in `.agent/context/meu-status.yaml`, all `pending`. Row 6 sets each `ready_for_review` with `tools/meu_status.py update`, and H2-2 sets `approved`. The render check runs at row 6 and H1-3:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/s65-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s65-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` does the following:

1. Checks that D-622 to D-625 carry Mat's rulings in §Decision Log (S14). **The ruling format:** an entry's `chosen` starts with the option letter, as `"A: …"`, and its `human_message_reference` is `"USER_EXPLICIT <date> '<Mat's words>'"`. A `chosen` that starts `Pending Mat's ruling`, or a `null` reference, is unruled. D-622 to D-624 take A, B or C; D-625 takes A or B. Checks the queue (S8): MEU-136 is `approved`, MEU-137 to MEU-139 are `pending`, and `003e5b1` is an ancestor of `HEAD`.
2. Checks the shapes this plan relies on, by name (S11): `SABR_LOG_NEEDLES`, `AGE_GATE_NEEDLES`, `_YtDlpLogger` and `_scan`, the `yt_dlp_debug: bool` keyword, `_base_opts`, `check_sabr_status`, the download logger, `check_sabr`, `force_sabr`, `clear_sabr`, `_run_one`, `_finish`, `SABR_STATUS_FIELDS`, `SABRStatus`, `ExtractError`, `DOMAIN_ERROR_TYPES`, `SABRMode`, `TranscriptFailureCause`, the wiring read, `QueueCard`'s `errorMessage`, the hidden `sabr-status` panel, `SabrSnapshot`, `DownloadListItem`, the Settings switch, the test-local needles, AC-122.16's debug-on line, the SPEC SABR pin and the last error-name pin; and that `DownloadFailureCause`, `DownloadFailedError`, the domain and adapter names, the `download.*` log events and `sabrResultText` are absent.
3. Creates `C:\Temp\av-kit\s65\tmp`. Records `HEAD` in `baseline.sha`, and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt` with each dirty path's SHA-256; the comparison report, if dirty, is hashed and never opened.
4. Records the line endings and SHA-256 of every file in §Files Modified and §Project files to `s65-anchors.txt`, which row 1 reads before it writes, and stops when a new file already exists.
5. Runs `uv sync --frozen --offline --all-packages`, and proves `ui/` and `mcp-server/node_modules` match their locks. `npm ci` isn't run, for Session 50's reason.
6. Captures the base Python suite to `s65-base-py.txt`, the base UI suite to `s65-base-ui.txt`, builds and tests the MCP server, and runs `ruff check packages/ tests/` to `s65-base-ruff.txt`. The suites' own failures are recorded, not fatal.
7. Runs the `red-check.py` and `identity.py` selftests, each on its own fixture copy (Session 56 RULE-4).

The scripts are copies of Session 64's, with this plan's values:

- **`red-check.py`.** `DECLARED_NEW` holds this plan's names and the selftest fixtures' names; these excuse a non-required block only. A red-check failure names the failing test (Session 50). Planning selftest: 44 fixtures (13 positive, 31 negative), 0 wrong (`C:/Temp/av-kit/s65-plan-redcheck-selftest.txt`).
- **`identity.py`.** `PLAN` is this folder. Its selftest binds `session-gate.ps1`, the target sources and tests, the four spec files, the register and its renders, `meu-status.yaml` and the grouping. Planning selftest: 0 failures (`C:/Temp/av-kit/s65-plan-identity-selftest.txt`).
- **`issue-resolve.py`.** Row 6's register resolve: reads `C:/Temp/av-kit/s65-resolve.json`, refuses a register whose SHA-256 differs from `--expect-sha256`, and sets each named issue `resolved` with its evidence, byte-editing only those entries.
- **`PROJECT_ARTIFACTS`.** This plan's `*.md`, the handoff, review and reflection files, `docs/execution/metrics.md` and `.agent/context/current-focus.md`.

### 2. Type-only first, then Red, then Green (rows 1 to 5)

- **Row 1 adds the shared names with no behaviour (Session 53 RULE-2).** `DownloadFailureCause`; `DownloadFailedError` in `DOMAIN_ERROR_TYPES`; `download_failure_message` returning `""`, `clean_line` returning its input, `scrub_line` (in `services/download.py`) returning its input, `classify_download_error` returning `(other, "")`, `sabr_phrase` returning `None`; `SABR_PHRASES` beside `SABR_LOG_NEEDLES` (the scan still reads the old constant); `FAILURE_CAUSE_NEEDLES = ()`; `SABRStatus.matched_phrase` with its default and no check; `_YtDlpLogger.debug_enabled` and `matched_phrase` with `sabr_detected` kept as an attribute; `sabrResultText` returning `""` and `DownloadListItem.error_message`. The adapter's `yt_dlp_debug` stays a `bool` in row 1, so wiring doesn't change until row 5. The pins in §Pins that move marked row 1 move. Its check runs `test_domain.py`, `test_download_failure_visibility.py`'s AC-137.1 (written in row 1), the download unit tests, `test_youtube_adapter.py`, `test_transcript_metadata.py`, `npm --prefix ui run typecheck`, `ruff` and `pyright` on the touched packages.
- **AC-137.1 is written in row 1 and passes from there**, running as a guard in each later row. AC-138.1 (the `SABR_LOG_NEEDLES` absence and the property) and AC-139.1 (the callable keyword) are written in rows 2b and 2c and fail by assertion there.
- **Red and Green alternate by MEU:** 2a, 3, 2b, 4, 2c, 5. Each Red row writes its MEU's Python and Vitest tests and checks both receipts.
- **Row 3 doesn't need MEU-138 (F3).** `classify_download_error` calls `sabr_phrase`, the row 1 stub, until row 4, and `FAILURE_RAISE` reads `logger.sabr_detected` from the scanner as it stands. AC-137.6's warning holds a phrase both scanners match; the phrase-only case is AC-138.2 and the captured missing-a-URL trace is AC-138.5, both Red in row 2b.
- **Each Red receipt holds an assertion failure, never a setup failure (Session 62 RULE-3).** `red-check.py` refuses a collection error, an import error, a fixture error and a required test that fails on a missing name. The Reds import new names inside the test body. A test that patches a new name asserts the name exists first (Session 52 RULE-4).
- **`--require` matches a test name up to a non-digit boundary**, and each required prefix needs at least one block that failed by assertion alone. Row 2a: `test_ac_137_2` to `_9` and `_11`, the two moved pins by full name (`test_ac_6_10_age_gate_and_unmapped_download_error` and `test_ac_76_6_age_gate_and_media_download_keep_their_types_neg`, F2), and `AC-137.10`. Row 2b: `test_ac_138_1` to `_7`, and `AC-138.8`. Row 2c: `test_ac_139_1` to `_7` and `_9`. Three tests characterise behaviour that exists, so they must pass where they are written: AC-137.1 (row 1), AC-138.7's renderer half (row 2b) and AC-139.8 (row 2c). AC-122.16's moved debug-off half also passes in row 2c.
- **Expectations stay immutable in Green.** No test file changes in rows 3 to 5.

### Plan-local scripts

- `baseline.ps1`, `red-check.py`, `identity.py`, `issue-resolve.py`: §1.
- `session-gate.ps1` (H1-2): below.

### Session gate (H1-2)

`session-gate.ps1` is Session 64's shape with Session 62's UI steps. It writes one receipt per step in `C:/Temp/av-kit`, named `s65-D6-<step>`. It is fail-fast, and it prints later steps as `not_run`. It sets `TMP` and `TEMP` as in §1 and clears `ELECTRON_RUN_AS_NODE`. Its last line is `session-gate: all steps exit 0`. Before it runs, the coordinator lists every changed path against the gate's scope (Session 60 RULE-4).

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match, and `tested_state` is compared |
| Static | `py-types` (`pyright`), `py-lint` (`ruff check packages/ tests/`), `ui-types` (`npm --prefix ui run typecheck`), `ui-lint`, `task-contract`, `scope-paths` (this plan's Files Modified and project files, plus `baseline-dirty.txt`; `ui/tests/e2e/test-ids.ts` refused), `red-check-selftest` |
| Fresh full | `py-tests`, `openapi` (`export_openapi.py --check openapi.committed.json`, unchanged under D-626), `ui-tests`, `ui-build`, `mcp-types`, `mcp-build`, `mcp-tests`, `state-render`, `issues-render`, `ui-electron` (`npm --prefix ui run test:e2e -- tests/e2e/download-queue.test.ts`, the AC-53.2 guard) |
| Skipped with reason | `mcp-audit` (live network), `build-record` (no installer build), the package build and its smokes (no packaged surface changes), `real-ffmpeg` (no FFmpeg path changes) |

`py-tests` excuses only ids that row 0's receipt shows failing; the UI, MCP and Electron steps excuse nothing. A step that fails in a file this session didn't touch is rerun once unchanged, and both attempts' receipts are kept (Session 53 RULE-4).

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | `graphify-out/` or `graphify-out-research/` appears | Re-decide the context tool |
| S2 | A Red receipt fails `red-check.py` | Fix the test setup; don't move to Green |
| S3 | `HEAD` moves from `baseline.sha`; a path outside `baseline-dirty.txt` and this plan appears; or, before rows 6 and H1-2, a `baseline-dirty.txt` path differs from its recorded SHA-256 | Stop and tell Mat; never commit, stash or revert another session's work |
| S4 | `uv sync --frozen --offline` fails, or `ui/` or `mcp-server/node_modules` doesn't match its lock | Stop: a fetch is a download and needs Mat's words |
| S5 | Any network request, download or upload, YouTube included, or the live audit | Stop and tell Mat |
| S6 | A test would need the real `YoutubeDL` to reach a URL | Stop; mock it, or raise it with Mat |
| S7 | Codex is unavailable or the ledger refuses a round | Mat is the fallback |
| S8 | At row 0, MEU-136 isn't `approved`, one of MEU-137 to MEU-139 isn't `pending`, or `003e5b1` isn't an ancestor of `HEAD` | Stop; the queue is wrong |
| S9 | A pin outside §Pins that move fails because of a new name, field or log line | Add it to the row with its AC, grep its neighbours for order and adjacency (Session 59 RULE-1, Session 62 RULE-4), and name it in the handoff |
| S10 | yt-dlp text, a path, a URL or a cookie value reaches a log line, stdout, the Console, the card or an error body in a way it didn't before | Fix it in the row or raise it with Mat; never record it as a residual (Session 50 RULE-1) |
| S11 | A row 0 shape check fails, or a new name already exists | Stop; amend this plan through the plan review before row 1 |
| S12 | A row would change a spec rule's meaning beyond §Spec text, an AC, or an existing route's wire shape | Stop; brief Mat with a recommendation and a do-nothing option (record a departure and keep the approved text; Session 59 RULE-3) |
| S13 | Retired: D-625 is B, so no context reading moves scope | When row 3 passes, record the context state in the MEU-137 handoff and go on |
| S14 | At row 0, any of D-622 to D-625 has no ruling from Mat in §Decision Log | Stop; ask Mat through the Human Decision Protocol |
| S15 | At row 6, `meu-status.yaml`, `meu-registry.md`, `BUILD_PLAN.md`, `known-issues.yaml` or the grouping changes any line outside this session's entries and rows | Stop and tell Mat |

## Decision Log

> [!WARNING]
> Mat's request settles the scope, and the grouping (D-535 to D-543) placed these MEUs. D-622 to D-624 are Mat's, asked through the Human Decision Protocol in planning; D-625 was ruled B by the Fable subagent under Mat's delegation of 2026-11-12, and D-639 was ruled A by it in execution review round 1 under the same delegation. D-626 to D-638 didn't need Mat: each is autonomous, with its alternatives in `reasoning`. D-622 to D-639 are free (`C:/Temp/av-kit/s65-plan-dids.txt`; D-625 showed once only because Session 64's plan text names it in a free range), so this block starts at D-622.
>
> Carried and not relisted in the block: every grouping §8 row, D-535 to D-543, with stage `grouping`. The reflection carries all nine: D-535 as human (`USER_EXPLICIT 2026-11-10 'follow the process, file them and add to session grouping'`), D-539 and D-540 as human (`USER_EXPLICIT 2026-11-10 'A'`, Mat's reply to the two briefs, which both recommended A), and the others as autonomous, because the closeout validator reads every §8 row of the declared grouping. Triage D-531 to D-533 ride in the register. The probe (`C:/Temp/av-kit/s65-plan-decision-probe.txt`), run with the grouping copy that has the §9 heading (D-628), the register and the three issue ids, returns 12 decisions: D-531 to D-533 and D-535 to D-543 (Session 54 RULE-5).

```yaml
decision_log:
  - id: D-622
    stage: planning
    question: "With the yt-dlp debug switch off and on, which yt-dlp lines reach the Console?"
    resolution: human
    class: two-way
    chosen: "A: opt-in shows text; warnings and ERROR lines always, debug and info lines redacted only when the switch is on"
    source_tag: Human-approved
    precedents:
      - "02 §yt-dlp log detail — Warnings and errors, Debug lines rows"
      - "AC-122.16 (tests/unit/test_transcript_metadata.py:324-353) — a debug line never shows a title"
    research:
      engine: none
      sources: []
    reasoning: "02 says debug lines show when the switch is on, and AC-122.16 says a debug line never shows a title; they conflict once the text is kept. A keeps AC-122.16 with the switch off and lets Mat opt in to the titles. B (never show debug text) makes the switch do nothing. C (always show) breaks AC-122.16. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-11 'Opt-in shows text (Recommended)'"
  - id: D-623
    stage: planning
    question: "How does a SABR phrase match a yt-dlp line?"
    resolution: human
    class: two-way
    chosen: "A: whole words, case-insensitive"
    source_tag: Human-approved
    precedents:
      - "02 §SABR check result Phrases row — case-insensitive on sabr, missing a url, forcing sabr and po token"
      - "C:/Temp/av-kit/s65-plan-matrix-probe.txt — the phrase matrix"
    research:
      engine: none
      sources: []
    reasoning: "A bare substring 'sabr' matches 'Sabrina' in a title or channel line. Whole words keep SABR-only and forcing SABR and drop the near-words. B (substring, as P:/yt-dlp_GUI does) would turn SABR on from a title. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-11 'Whole words (Recommended)'"
  - id: D-624
    stage: planning
    question: "Does the phrase set keep 02's bare 'po token'?"
    resolution: human
    class: two-way
    chosen: "A: narrow it to 'require a gvs po token'"
    source_tag: Human-approved
    precedents:
      - "C:/Temp/av-kit/s65-plan-potoken-probe.txt — yt-dlp 2026.10.26's PO Token lines"
    research:
      engine: none
      sources: []
    reasoning: "yt-dlp prints PO Token lines that are not about SABR, so a bare 'po token' would turn SABR on and lock quality at 360p without cause. The old phrase is kept. B (keep 'po token') follows 02's text as written. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-11 'Narrow it (Recommended)'"
  - id: D-625
    stage: planning
    question: "Does the session name a split point that moves MEU-139 to Session 65b?"
    resolution: human
    class: two-way
    chosen: "B: run all three MEUs with no context-measured split; at row 3 the context state is recorded in the MEU-137 handoff and the session goes on"
    source_tag: Human-approved
    precedents:
      - "the session prompt — raise the split with HDP at the plan gate"
      - "grouping :82-97 — the Session 65 entry"
    research:
      engine: none
      sources: []
    reasoning: "Three MEUs across core, infra and the renderer is the most this grouping puts in one session. A names a point where MEU-139, the least coupled, can move without rework. B, do nothing, runs all three and relies on compaction. Ruled B by the Fable subagent under Mat's delegation: Mat's standing instruction of 2026-11-06 is not to let context decide scope, and Mat's 'Full session' answer of 2026-11-12 names one execution loop and one commit of plan and code, which B keeps; the late-compaction risk is bounded by the Red and Green receipts and the gate, and if MEU-139 genuinely fails to land it can still be deferred on its own merits. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-12 'If you need decisions answerd have Fable subagent do rulling and accept it as if it was coming from human' — ruled by the Fable subagent: B"
  - id: D-626
    stage: planning
    question: "Does matched_phrase go on the SABR wire?"
    resolution: autonomous
    class: two-way
    chosen: "A: no; it is kept on the domain status and in the download.sabr_check log line only, and the OpenAPI snapshot doesn't change"
    source_tag: Local Canon
    precedents:
      - "02 §SABR check result Log row — the matched phrase in a kept field of the log line"
      - "02 Shown row — the page states the result and its time, not the phrase"
    research:
      engine: none
      sources: []
    reasoning: "The spec puts the phrase in the log. Adding it to SABRStatusOut would change the OpenAPI snapshot, the MCP surface and its audit for a field no rule asks to show. Two-way: a later MEU can add it."
    human_message_reference: null
  - id: D-627
    stage: planning
    question: "How is yt-dlp text cleaned before it is stored or logged?"
    resolution: autonomous
    class: two-way
    chosen: "A: clean_line drops ANSI CSI sequences, turns whitespace into spaces, drops Cc, Cf and Cs code points, collapses spaces, and runs before every scrubber, through scrub_line, which first matches the home folder across split characters with its boundary read from the line as written, then also scrubs a joined form with every whitespace character but U+0020 removed"
    source_tag: Local Canon
    precedents:
      - "Session 53 RULE-1 — surrogate, control-character and empty regressions"
      - "C:/Temp/av-kit/s65-plan-matrix-probe.txt — yt-dlp's coloured ERROR prefix"
    research:
      engine: none
      sources: []
    reasoning: "yt-dlp colours its ERROR prefix, and a title can hold a lone surrogate that SQLite's UTF-8 encode and the JSON response refuse. Dropping them keeps one readable line. Replacing them with U+FFFD lost because it adds noise to the card. Round 1 (F1) showed that cleaning after redact_message lets a NUL inside 'cookie' or 'https://', or an ANSI code inside the home path, pass the scrubbers and then be joined back up; cleaning first closes that, and Cf joins Cc because zero-width and bidi marks split a word the same way. Round 2 (F1) showed that turning U+0085 or U+2028 into a space still splits 'cookie' after cleaning; scrub_line closes that by also scrubbing the joined form, and keeps the readable form when nothing is scrubbed, so AC-137.4's readable outputs hold. Round 3 (F1) showed that removing a tab before the home path joins it to the word before, so scrub_home's left boundary fails whenever the joined form is chosen; scrub_line therefore matches the home folder first, on the line with its split characters marked and its boundary as written, and the joined form can no longer undo it. Fixing the joined form's boundary afterwards lost, because a split inside the home name and one before it are the same character, and only the home folder's own text tells them apart. Treating those characters as line ends lost, because a tab or a no-break space splits a needle the same way and a line end would cut the Console detail. Two-way."
    human_message_reference: null
  - id: D-628
    stage: planning
    question: "How is the grouping's §8 table made readable to the closeout validator?"
    resolution: autonomous
    class: two-way
    chosen: "A: insert a '## 9. Decision Briefs' heading before the D-539 brief"
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/s65-plan-decision-probe.txt — without the heading the validator refuses with '§8 row 10 is ragged'; with it, 12 decisions"
    research:
      engine: none
      sources: []
    reasoning: "The briefs follow §8 with no heading, so the validator reads their tables as §8 rows. A heading ends §8 and changes no decision text. Editing the validator lost because it is outside this session's scope. Two-way."
    human_message_reference: null
  - id: D-629
    stage: planning
    question: "Does 02's Phrases row change to match D-623 and D-624?"
    resolution: autonomous
    class: two-way
    chosen: "A: yes; the row says whole words, case-insensitive, and require a gvs po token, and names D-623 and D-624"
    source_tag: Local Canon
    precedents:
      - "02 :540 — the Phrases row"
    research:
      engine: none
      sources: []
    reasoning: "Mat ruled both; a spec that says otherwise would contradict the tested behaviour. Recording a departure instead lost because the rows are this MEU's own residual text. Two-way."
    human_message_reference: null
  - id: D-630
    stage: planning
    question: "02's Control row asks for a 'yt-dlp debug log' switch; one called 'yt-dlp debug' exists. What does the row say?"
    resolution: autonomous
    class: two-way
    chosen: "A: name the existing 'yt-dlp debug' switch (SettingsPage.tsx:724-733, leaf yt_dlp_debug) and test that it saves; 06's toggle row names it too"
    source_tag: Local Canon
    precedents:
      - "YTDLP-LOG-TEXT-DROPPED root cause — 'has no control in Settings' (true at 55d1289, not at 003e5b1)"
      - "ui/src/renderer/src/features/settings/settings-sections.ts — CHECKBOX_COPY_SOURCES yt_dlp_debug"
    research:
      engine: none
      sources: []
    reasoning: "The switch landed after the issue was written. Renaming it lost because the label is pinned by the settings copy sources. Two-way."
    human_message_reference: null
  - id: D-631
    stage: planning
    question: "Where do DownloadFailedError and the classifier live?"
    resolution: autonomous
    class: two-way
    chosen: "A: DownloadFailedError in domain/errors.py, last in DOMAIN_ERROR_TYPES; classify_download_error, FAILURE_CAUSE_NEEDLES, SABR_PHRASES and sabr_phrase in the YouTube adapter"
    source_tag: Local Canon
    precedents:
      - "domain/errors.py — every DomainError subclass and DOMAIN_ERROR_TYPES"
      - "adapter.py AGE_GATE_NEEDLES — yt-dlp's words live in the adapter"
    research:
      engine: none
      sources: []
    reasoning: "The service needs the cause, not yt-dlp's words; the adapter already holds the age-gate needles. errors.py can import enums.py with no cycle. Appending keeps the existing order pin. Two-way."
    human_message_reference: null
  - id: D-632
    stage: planning
    question: "Is an error() call without the 'ERROR:' prefix logged at ERROR?"
    resolution: autonomous
    class: two-way
    chosen: "A: no; it is a debug line, logged only when the switch is on"
    source_tag: Research-backed
    precedents:
      - "C:/Temp/av-kit/s65-plan-matrix-probe.txt — 'error lines: 14 start ERROR: , 14 are tracebacks'"
    research:
      engine: none
      sources: []
    reasoning: "With verbose on, yt-dlp passes each traceback to error() with no prefix; logging those at ERROR would double every failure and persist the traceback. The real error line always has the prefix. Two-way."
    human_message_reference: null
  - id: D-633
    stage: planning
    question: "Does an AgeRestricted job log download.failed?"
    resolution: autonomous
    class: two-way
    chosen: "A: yes, at ERROR with its stored text 'video is age-restricted'"
    source_tag: Local Canon
    precedents:
      - "03 Card row — the card shows the reason on a Failed or AgeRestricted row"
    research:
      engine: none
      sources: []
    reasoning: "The spec treats AgeRestricted as a failure on the card; the Console should match it. A separate event name lost because no rule names one. Two-way."
    human_message_reference: null
  - id: D-634
    stage: planning
    question: "Does a Cancelled job log a line?"
    resolution: autonomous
    class: two-way
    chosen: "A: no new line"
    source_tag: Local Canon
    precedents:
      - "03 Log row — started, done and failed"
    research:
      engine: none
      sources: []
    reasoning: "The user cancels, so the cause is known. Adding download.cancelled lost because no rule names it. Two-way."
    human_message_reference: null
  - id: D-635
    stage: planning
    question: "How does the page state an Inactive result?"
    resolution: autonomous
    class: two-way
    chosen: "A: the sabr-status panel is always shown and holds sabrResultText; the separate Checking line goes"
    source_tag: Local Canon
    precedents:
      - "02 Shown row"
      - "C:/Temp/av-kit/s65-plan-ui.txt — no test asserts the panel hidden while Inactive; AC-53.2 and AC-53.4 assert it visible while Active"
    research:
      engine: none
      sources: []
    reasoning: "One place for the result keeps the pins and the layout. A toast lost because it disappears and the spec wants the result stated. Two-way."
    human_message_reference: null
  - id: D-636
    stage: planning
    question: "Is a missing-format error during SABR a no_format or a refused failure?"
    resolution: autonomous
    class: two-way
    chosen: "A: refused, when the same call's logger matched a SABR phrase"
    source_tag: Research-backed
    precedents:
      - "C:/Temp/av-kit/s65-plan-matrix-probe.txt — the cause matrix"
    research:
      engine: none
      sources: []
    reasoning: "With SABR on, yt-dlp hides every format and then says the requested format is not available. Telling the user to pick another quality would be wrong; waiting is the fix. Two-way."
    human_message_reference: null
  - id: D-637
    stage: planning
    question: "What does an OSError outside cookie file mode become?"
    resolution: autonomous
    class: two-way
    chosen: "A: DownloadFailedError(write_failed) with detail 'the exception type name, a colon, then its strerror', never the filename"
    source_tag: Local Canon
    precedents:
      - "adapter.py :518-521 — today 'yt-dlp IO failed'"
      - "Session 50 RULE-1 — no raw path in a log"
    research:
      engine: none
      sources: []
    reasoning: "An OSError during a download is the output folder or disk in almost every case. str(exc) holds the path, so only the type and strerror are kept. Two-way."
    human_message_reference: null
  - id: D-638
    stage: planning
    question: "How is the 'other' reason on the card made safe?"
    resolution: autonomous
    class: two-way
    chosen: "A: safe_reason(scrub_line(raw)) or the error's type name"
    source_tag: Local Canon
    precedents:
      - "services/transcript.py :596 — safe_reason(redact_message(str(exc))) or type(exc).__name__"
    research:
      engine: none
      sources: []
    reasoning: "MEU-115's pattern, plus scrub_home, because the stored message is also served to agents through the API and MCP. Leaving out scrub_home lost because yt-dlp's text can hold the output path. scrub_line cleans first (F1), matches the home folder before anything is joined (round 3 F1) and also scrubs the joined form (round 2 F1), so no control or format character and no whitespace character other than U+0020 can split a needle, a link or the home path; a plain space still splits a word, as it does today. Two-way."
    human_message_reference: null
  - id: D-639
    stage: execution
    question: "How does yt-dlp's error line keep its split characters until scrub_line (execution review round 1, F1)?"
    resolution: human
    class: two-way
    chosen: "A: first_line(text) splits only at CR, LF and CRLF and returns the first line clean_line leaves non-empty, as written; classify_download_error drops only a leading ERROR: with the ANSI codes and whitespace around it; the service's generic branch uses first_line(str(exc)); all cleaning happens once, in scrub_line"
    source_tag: Human-approved
    precedents:
      - "this plan's CLEAN_LINE row — no site scrubs its output directly; every site reaches the scrubbers through SCRUB_LINE"
      - "this plan's FAILED_ERROR row — .detail is the raw first line"
    research:
      engine: none
      sources: []
    reasoning: "Round 1 F1 showed that classify_download_error ran clean_line before scrub_line, so a tab became a space and a NUL vanished before scrub_line could mark them: a real DownloadError('ERROR: co\\tokie=SECRET') stored 'Download failed: co okie=SECRET.'. str.splitlines also ends a line at U+2028, U+0085 and other separators, which cut a home path inside its user name. A hands scrub_line the line as yt-dlp wrote it and agrees with the CLEAN_LINE and FAILED_ERROR rows. B, scrubbing inside the classifier, contradicts FAILED_ERROR, scrubs twice and keeps the splitlines cut. C, doing nothing, leaves an evidence-backed High privacy finding open. Conditions: first_line is total and returns the original text; the prefix strip is anchored and touches nothing else; AC-137.12 drives the real adapter, service and SQLite and asserts the stored message and the log detail, with a non-DownloadFailedError case and an OSError case. Ruled A by the Fable subagent under Mat's delegation. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-12 'If you need decisions answerd have Fable subagent do rulling and accept it as if it was coming from human' — ruled by the Fable subagent: A"
```

## Research References

- `docs/build-plan/03-service-layer.md:700-716`, `docs/build-plan/02-infrastructure.md:534-564`, `:360-378`, `docs/build-plan/06-gui.md:343-347`, `:460-466`, `docs/build-plan/01-domain-layer.md:133-141`, `:534-555`.
- The grouping file: the Session 65 entry (`:82-97`), §5 (`:131-144`), §6 tracker (`:149`), §8 (`:165-177`), the D-539 and D-540 briefs (`:179`, `:206`).
- The register entries for D-531 to D-533 (`C:/Temp/av-kit/s65-plan-issues.txt`).
- Session 55's plan and scripts (`docs/execution/plans/` for `transcript-failure-reason`) and Session 64's (`2026-11-11-capture-export-copy/`).

## Planning receipts

- `C:/Temp/av-kit/s65-plan-probes.txt` (`C:/Temp/av-kit/s65/plan_probes.py`): `HEAD` `003e5b1466c4b7accadc6b3267c7d4b1315f2991`, line endings and SHA-256 of the target files, `plan-probes: 0 problem(s)`.
- `C:/Temp/av-kit/s65-plan-matrix-probe.txt` (`C:/Temp/av-kit/s65/plan_probe_matrix.py`): the phrase and cause matrix against yt-dlp 2026.10.26's own strings, `plan-probe-matrix: 0 problem(s)`.
- `C:/Temp/av-kit/s65-plan-potoken-probe.txt`: yt-dlp's PO Token lines (D-624).
- `C:/Temp/av-kit/s65-ytdlp-*.txt`, `C:/Temp/av-kit/s65-captured-line-grep.txt`: yt-dlp's logger routing and the captured SABR-only line.
- `C:/Temp/av-kit/s65-plan-dids.txt`: D-622 to D-639 and AC-137 to AC-139 are free; the only worktree is `main`.
- `C:/Temp/av-kit/s65-plan-decision-probe.txt`: the decision probe (D-628).
- `C:/Temp/av-kit/s65-plan-issues.txt`, `s65-plan-specrows.txt`, `s65-plan-errors*.txt`, `s65-plan-callers.txt`, `s65-plan-ui*.txt`, `s65-plan-sabr-api.txt`, `s65-plan-layout.txt`: the reads this plan cites.
- `C:/Temp/av-kit/s65-rulings.txt`: Mat's D-622 to D-624 selections.
- `C:/Temp/av-kit/s65-plan-redcheck-selftest.txt`, `s65-plan-identity-selftest.txt`: the scripts' selftests, each 0 wrong.
- `baseline.ps1`'s rulings, shapes and anchors blocks run alone, unchanged, at plan time (`C:/Temp/av-kit/s65/plan_probe_baseline_steps.py` extracts each block from the file):
  - `C:/Temp/av-kit/s65-plan-shapes-probe.txt`: `shapes wrong (S11): []`, `probe shapes exit=0`.
  - `C:/Temp/av-kit/s65-plan-anchors-probe.txt`: `missing targets: [] new files already present: []`, `probe anchors exit=0`.
  - `C:/Temp/av-kit/s65-plan-rulings-probe.txt`: D-622 to D-625 `ruled=True` (`D-625: chosen starts 'B:', reference starts 'USER_EXPLICIT 2026-11-12'`), `probe ruled exit=0`, rerun on 2026-11-12 after D-625 was recorded.
- `C:/Temp/av-kit/s65-plan-ac-probe.txt`: H1-6a's plan-side regex finds `28` ACs, AC-137.1 to .11, AC-138.1 to .8 and AC-139.1 to .9.
- `C:/Temp/av-kit/s65-plan-task-lint.txt`: `lint_task_contract.py` on `task.md`, `OK: 26 row(s); 10-column table (with builder_model); 24 row(s) fully checked`, with H1-5 and H2-1 exempt as `view_file` rows.
- Not run at plan time: any suite or build.

## Validation stage contract

- **Static:** `pyright`, `ruff check packages/ tests/`, `npm --prefix ui run typecheck`, `ui-lint`, `lint_task_contract.py`, the scope-paths check and the `red-check.py` selftest.
- **Targeted:** each row's own files, with `red-check.py` reading every Red receipt.
- **Fresh full:** the whole Python, UI and MCP suites, the OpenAPI check, the UI and MCP builds, the two render checks and the download-queue Electron spec, in the session gate.
- **Identity:** `identity.py` binds `HEAD`, the work tree minus `PROJECT_ARTIFACTS`, and the runtime. The gate records it before and after, and H1-6b checks each handoff's evidence against it.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
