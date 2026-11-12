---
date: "2026-11-12"
project: "download-failure-visibility"
meu: "MEU-137"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-11-download-failure-visibility/implementation-plan.md"
build_plan_section: "bp03"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-11-capture-export-copy-MEU-136-handoff.md"
---

# Handoff: 2026-11-11-download-failure-visibility-MEU-137-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-137 `svc-download-failure-reason`. It closes `DOWNLOAD-FAILED-NO-REASON`. A failed download's card now says why it failed, and the Console has a matching `download.failed` line. A download also logs `download.started`, and a finished one logs `download.done`. yt-dlp's text is cleaned before it reaches a log or the database, so a coloured `ERROR:` prefix, a lone surrogate or a NUL never reaches SQLite or JSON. A cookie value, a home path or a link is scrubbed even when a control character, an ANSI code, U+0085 or U+2028 splits it.

**Build Plan Section**: [03 §Download failure reason (residual)](../../../docs/build-plan/03-service-layer.md) (the Delivered note at `:714`).
**Predecessor**: [MEU-136 handoff](2026-11-11-capture-export-copy-MEU-136-handoff.md), Session 64. This is the first session of the grouping `.agent/context/grouping/2026-11-10-download-reliability-session-grouping.md` (Sessions 65 to 67, MEU-137 to MEU-142). MEU-138 and MEU-139 follow in this session: [MEU-138 handoff](2026-11-11-download-failure-visibility-MEU-138-handoff.md), [MEU-139 handoff](2026-11-11-download-failure-visibility-MEU-139-handoff.md).

- **Core (rows 1 and 3).**
  - `DownloadFailureCause` (`packages/core/src/avkit_core/domain/enums.py:145`), `FAILURE_CAUSE_ENUM`: `refused`, `no_format`, `cookies`, `write_failed`, `other`.
  - `DownloadFailedError` (`packages/core/src/avkit_core/domain/errors.py:47`), `FAILED_ERROR`, with `.cause` and `.detail`. It is last in `DOMAIN_ERROR_TYPES` (`:280`).
  - `download_failure_message` (`packages/core/src/avkit_core/domain/download.py:109`), `FAILURE_MESSAGE`, and `clean_line` (`:121`), `CLEAN_LINE` (D-627).
- **Service (rows 1 and 3).** In `packages/core/src/avkit_core/services/download.py`:
  - `scrub_line` (`:118`), `SCRUB_LINE`, with its private helpers `_SPLIT_GAP` (`:76`), `_HOME_SEPARATORS` (`:77`), `_mark_splits` (`:80`), `_scrub_split_home` (`:93`) and `_scrub` (`:114`) (Departure 2);
  - `first_line` (`:136`), which `FAILURE_CAUSE` and `FAILURE_LOG` both use (D-639, Departure 6);
  - `FAILURE_LOG` in `_run_one` (`:620`): `download.started` (`:637`), `download.failed` for AgeRestricted (`:645`) and for every other failure (`:673`), and `download.done` (`:711`) (D-633, D-634, D-638).
- **Adapter (rows 1 and 3).** In `packages/infrastructure/src/avkit_infra/youtube/adapter.py`: `FAILURE_CAUSE_NEEDLES` (`:95`) and `classify_download_error` (`:358`) with `_ERROR_PREFIX` (`:119`), `FAILURE_CAUSE` (D-636, D-639); and `FAILURE_RAISE` in `download` (`:594`), with its raises at `:620` and `:626` (D-637).
- **UI (rows 1 and 3).** `DownloadListItem.error_message` (`ui/src/renderer/src/features/downloader/useDownloadQueue.ts:21`) and `CARD_REASON`, the card's `errorMessage` (`DownloaderPage.tsx:485`).
- **Tests.**
  - `tests/unit/test_download_failure_visibility.py` (new, LF): AC-137.1 to .5, .7 and .8.
  - `tests/integration/test_youtube_adapter_visibility.py` (new, LF): AC-137.6 and AC-137.12.
  - `tests/e2e/test_api_download_visibility.py` (new, LF): AC-137.9 and .11.
  - `ui/tests/unit/downloader-page.behavior.test.ts`: AC-137.10.
  - The pins in the plan's §Pins that move: `test_domain.py`'s `DOMAIN_ERROR_TYPE_NAMES` and the constructor walk's `ERROR_ARGS` (row 1), and the two download-error pins in `test_youtube_adapter.py` (AC-6.10 at `:469`, AC-76.6 at `:739`; row 2a).
- **Spec text and records (row 6).** 03's Delivered note (`docs/build-plan/03-service-layer.md:714`) and the `DownloadFailedError` row in 01's errors table (`docs/build-plan/01-domain-layer.md:547`). MEU-137 is `ready_for_review` with this plan (`.agent/context/meu-status.yaml`, `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md`). `DOWNLOAD-FAILED-NO-REASON` is `resolved` (`.agent/context/known-issues.yaml`).

**Execution authorization:** `USER_EXPLICIT`, 2026-11-11 and 2026-11-12. Mat ruled D-622 to D-624 (each "Recommended" option) and approved the plan (`implementation-plan.md:113`). On 2026-11-12, after round 3 of the plan review, Mat said "Fix F1 to F3, increase token buget by 30M and continue the loop until approved. If you need decisions answerd have Fable subagent do rulling and accept it as if it was coming from human and continue until approved. Once complete commit and push." Mat then chose "Full session (Recommended)": the plan loop until approved (approved in round 4), then execution and its review until approved on a 40M budget over at most 6 rounds, then one commit on `main` and a push. D-625 B was ruled by a Fable subagent under that delegation. The review's approval is Codex's.

### Context state after row 3 (D-625 B)

Recorded when row 3 (MEU-137 Green) passed, before row 2b. HEAD is `003e5b1466c4b7accadc6b3267c7d4b1315f2991`. The session runs on `main` with no split (D-625 B).

- **Rows done.** Rows 0, 1, 2a and 3 were `[x]`.
  - Row 2a Red: `s65-red-137-check.txt` holds `red-check: 2 receipt(s), 12 required test(s), 0 problem(s)`. The AC-137.1 guard holds `1 passed, 16 deselected in 0.19s` (`s65-r2a-guard.txt`).
  - Row 3 Green: `s65-py-green-137.txt` holds `286 passed in 10.75s`, and `s65-ui-green-137.txt` holds `Tests  104 passed (104)`. tsc, pyright (`0 errors, 0 warnings, 0 informations`) and ruff (`All checks passed!`) are clean (`s65-r3-*.txt`).
- **Next, as it then stood.** Row 2b (MEU-138 Red), then rows 4, 2c, 5 and 6, then H1 and H2. All of them ran in this session.

### Where values go, as built (Session 50 RULE-1, Session 53 RULE-1, Session 61 RULE-1)

- **yt-dlp's error text** comes from `DownloadError`. `download` (`adapter.py:594`) passes `str(exc)` and the scanner's `sabr_detected` to `classify_download_error` (`:358`), and raises `DownloadFailedError(cause, detail)` (`:620`). In `_run_one`'s one `except Exception` branch (`services/download.py:656`), `detail = scrub_line(raw)` (`:666`) reaches the `download.failed` line's `detail` (`:677`), then the Console after `console_field`. For `other` only, `safe_reason(detail)` (`:669`) becomes the reason inside the stored message (`:670`). That message reaches SQLite through `_finish`, then `GET /downloads`, the MCP `avkit_download` list and the card. Its writers are yt-dlp and the extractors it runs. AC-137.9 and AC-137.11 trace a cookie value, a home path, a URL, a lone surrogate and a NUL. AC-137.7 and AC-137.9 trace the first three again with a NUL, an ANSI code, U+0085 or U+2028 inside them, and a home path after a tab or a NUL in a line where a cookie is also scrubbed (AC-137.4, AC-137.7, AC-137.9).
- **Any other exception** gives `first_line(str(exc))` as `raw` (`:660`, D-639): `CookieTestError` is `cookies`, and anything else is `other`. An empty text falls back to the type name (`:669`), so `RuntimeError("")` stores `Download failed: RuntimeError.` (AC-137.7).
- **`first_line` and the classifier (D-639).** `first_line` (`services/download.py:136`) splits only at CR, LF and CRLF, and returns the first line that `clean_line` leaves non-empty, as written. `classify_download_error` (`adapter.py:358`) takes that line and drops only a leading `ERROR:` with the ANSI codes and whitespace around it (`_ERROR_PREFIX`, `adapter.py:119`). So a tab, a NUL, U+0085 or U+2028 inside a cookie value, a home path or a link is still in `raw` when `scrub_line` runs, and all cleaning happens once, there. AC-137.12 drives this through the real adapter, service and SQLite.
- **An `OSError`'s text** never leaves the adapter. Only its type name and `strerror` reach `detail` (`adapter.py:626`, D-637), so the filename is absent (AC-137.6, AC-137.12).
- **The stored message** for the four named causes comes from `FAILURE_MESSAGE` only (`domain/download.py:109`). No yt-dlp text reaches it.
- **AgeRestricted** stores its own message as before. Its `download.failed` line's `detail` is the first line of that message after `scrub_line` (`services/download.py:649`).
- **Cancelled** logs neither `download.failed` nor `download.done` (D-634; AC-137.8).

### Row 1's caller grep (S55 RULE-1, S59 RULE-1, S62 RULE-4)

Row 1 grepped `packages/`, `tests/` and `ui/` for every caller of `_finish(`, `SABRStatus(`, `_YtDlpLogger(`, `YouTubeAdapter(`, `DOMAIN_ERROR_TYPES` and `DownloadListItem`, and for every test that walks `DOMAIN_ERROR_TYPES` or `SABR_STATUS_FIELDS`. The receipt `s65-row1-callers.txt` holds 135 lines, which are also recorded in `s65-anchors.txt`:

| File | Hits |
|---|---|
| `tests/integration/test_youtube_adapter.py` | 57 |
| `ui/tests/unit/downloader-page.behavior.test.ts` | 15 |
| `packages/infrastructure/src/avkit_infra/youtube/adapter.py` | 14 |
| `tests/unit/test_domain.py` | 13 |
| `packages/core/src/avkit_core/services/download.py` | 11 |
| `tests/e2e/test_api_downloads.py` | 4 |
| `ui/src/renderer/src/features/downloader/useDownloadQueue.ts` | 3 |
| `packages/core/src/avkit_core/services/tts.py`, `services/conversion.py`, `domain/download.py` | 3 each |
| `tests/unit/test_services.py`, `tests/integration/test_download_received_quality.py` | 2 each |
| `tests/unit/test_transcript_metadata.py`, `tests/integration/test_api_wiring.py`, `tests/e2e/real_stack.py`, `domain/errors.py`, `packages/api/src/avkit_api/wiring.py` | 1 each |

- The `tts.py` and `conversion.py` hits are their own `_finish` methods, not callers of the download one.
- The two walkers of `DOMAIN_ERROR_TYPES` in `test_domain.py`, `DOMAIN_ERROR_TYPE_NAMES` (`:208`) and the constructor walk's `ERROR_ARGS` (`:223`, `:225`), moved in row 1. The walker of `SABR_STATUS_FIELDS`, `SPEC_SABR_STATUS_FIELDS` (`:330`), is MEU-138's.
- Rows 3, 4 and 5 ran the tests of every listed caller in their check (row 4's own grep is `s65-r4-callers.txt`, 55 lines).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-137.1 | unit | Type characterisation of row 1's names: the five `DownloadFailureCause` members in order; `DownloadFailedError` is a `DomainError` with `.cause`, `.detail` and `str` `download failed: other`, last in `DOMAIN_ERROR_TYPES`; the signatures of `download_failure_message`, `clean_line` and `classify_download_error`; `SABRStatus` ends with `matched_phrase` defaulting to `None`. It passed from row 1 and ran as a guard in each later row | 03 Message | `tests/unit/test_download_failure_visibility.py:115` | ✅ |
| AC-137.2 | unit | `FAILURE_MESSAGE`: each named cause gives its exact text with and without a `reason`; `other` gives `Download failed: x.` and, with `None` or `""`, `Download failed.`; a non-member raises `ValidationError` | 03 Message | `test_download_failure_visibility.py:151` | ✅ |
| AC-137.3 | unit | Each message is non-empty, ends with `.`, and holds no `REDACT_NEEDLES` entry, URL or path separator | 03 Message; D-247 | `test_download_failure_visibility.py:163` | ✅ |
| AC-137.4 | unit | `CLEAN_LINE`'s cases, and `SCRUB_LINE`'s split needles, links and home paths, the readable form kept when nothing is scrubbed, and the mixed lines of round 3 F1 | D-627 | `test_download_failure_visibility.py:175`, `:196` | ✅ |
| AC-137.5 | unit | `FAILURE_CAUSE`: each needle of each cause in upper and mixed case; both apostrophes; the coloured prefix; the first non-empty line; the SABR override; an unknown and an empty text give `other` | 03 Message; D-636 | `test_download_failure_visibility.py:220`, `:229` | ✅ |
| AC-137.6 | integration | `FAILURE_RAISE` with a mocked `YoutubeDL`: page reload gives `refused`; a SABR warning turns `no_format` into `refused`; an `OSError` in browser mode gives `write_failed` without the filename; file mode raises `CookieTestError`; the age gate still raises `AgeRestrictedError` | 03 Message; D-637 | `tests/integration/test_youtube_adapter_visibility.py:62`, `:76`, `:91`, `:107` | ✅ |
| AC-137.7 | unit | `FAILURE_LOG` storage with the real SQLite UoW: each cause's message; `CookieTestError`; a `DomainError`; `RuntimeError("")`; the cookie, home and link scrubbing and the 200 cut; the NUL, ANSI, U+0085 and U+2028 splits; the mixed line | 03 Message | `test_download_failure_visibility.py:306`, `:339` | ✅ |
| AC-137.8 | unit | `FAILURE_LOG` lines: a success logs `download.started` then `download.done`, with `started` before the port call and `done` after the Done row; each failure logs `started` then one `download.failed` at error with `error` and `detail`; AgeRestricted logs its text; Cancelled logs neither | 03 Log | `test_download_failure_visibility.py:404`, `:457`, `:473` | ✅ |
| AC-137.9 | API | The Console trace on the real stack, `HealthService` built first: five failing jobs, plain and split, each show `~`, `[link]` and ` [REDACTED]`, with no home marker, `e.example` or `SECRET` in the ring, stdout or the served `error_message`; the positive control finds the marker as `~` | 03 Log, Done; D-247 | `tests/e2e/test_api_download_visibility.py:125` | ✅ |
| AC-137.10 | renderer | `CARD_REASON`: a Failed card shows its `error_message`; `null` and a missing key show the placeholder; an AgeRestricted card shows its text | 03 Card | `ui/tests/unit/downloader-page.behavior.test.ts:1219` | ✅ |
| AC-137.11 | API | `DownloadFailedError(other, "bad\ud800 x\x00y")` is served as valid JSON with `error_message` exactly `Download failed: bad xy.`, and the Console line's `detail` is `bad xy` | D-627; Session 53 RULE-1 | `test_api_download_visibility.py:160` | ✅ |
| AC-137.12 | integration | Split text from yt-dlp, end to end: the real `YouTubeAdapter().download` with a mocked `YoutubeDL`, the real service and the real SQLite UoW. Eight cases (`SPLIT_FAILURES`, `:129`): a tab-split cookie, a tab-split link, a NUL before a home path with a cookie, a tab in the user name, U+2028, a coloured `ERROR:` with U+0085 and a second line, a `RuntimeError` with U+2028 and a tab-split cookie, and an `OSError`. It asserts each stored message, each `download.failed` line's `detail`, and that no secret, `e.example` or home folder part is stored or logged. Added for execution round 1 F1 | D-639 | `tests/integration/test_youtube_adapter_visibility.py:170` | ✅ |
| AC-6 (cross-ref) | regression | MEU-6's ACs are owned by its handoff. Moved pin: AC-6.10 (`test_youtube_adapter.py:469`) expected `DomainError` for an unmapped `DownloadError`, and now expects `DownloadFailedError` `other` with the text as `detail`. It failed in row 2a and passes from row 3. AC-6.11 is MEU-138's moved pin | plan §Pins that move | `tests/integration/test_youtube_adapter.py:469`; gate `py-tests` | ✅ |
| AC-76 (cross-ref) | regression | Moved pin: AC-76.6's media-download half (`test_youtube_adapter.py:739`) now expects `DownloadFailedError`. It failed in row 2a and passes from row 3 | plan §Pins that move | `test_youtube_adapter.py:739`; gate `py-tests` | ✅ |
| AC-2 (cross-ref) | regression | AC-2.6 (`test_domain.py:461`), the `SABRStatus` field check, is unchanged and passes. Its `TypeError` for a missing field still holds (AC-138.4) | plan §Pins that move | `tests/unit/test_domain.py:461`; gate `py-tests` | ✅ |
| AC-51 (cross-ref) | regression | The AC-51.6 byte-hash guards were not touched: no file they hash changed (Session 50 RULE-2) | plan §Guards | gate `py-tests` | ✅ |
| AC-53 (cross-ref) | regression | AC-53.2 and AC-53.4 (`downloader-page.behavior.test.ts:1058`, `:1159`) are unchanged guards and pass after `CARD_REASON` | plan §Guards | `downloader-page.behavior.test.ts:1058`, `:1080`, `:1159`; gate `ui-tests` | ✅ |
| AC-122 (cross-ref) | regression | AC-122.16 is MEU-139's moved pin (`test_transcript_metadata.py:324`) | plan §Pins that move | [MEU-139 handoff](2026-11-11-download-failure-visibility-MEU-139-handoff.md) | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-137.2 to AC-137.9, AC-137.11 (Python), and the AC-6.10 and AC-76.6 pins | Row 2a: `23 failed, 91 passed in 2.49s` against row 1's stubs (`s65-py-red-137.txt`). `AssertionError: assert [] == ['download.st...nload.failed']` ×6; `At index 0 diff: <class '…DomainError'> != <class '…DownloadFailedError'>` ×3; `At index 0 diff: <DownloadFailureCause.other: 'other'> != <DownloadFailureCause.refused: 'refused'>` ×2; `assert 'download failed: other' == 'Download failed: bad xy.'`; `At index 0 diff: 'download failed: refused' != 'YouTube refused the download (page reload, SABR-only or bot check). Try again later.'` | Row 3: `286 passed in 10.75s` (`s65-py-green-137.txt`); gate `py-tests` | `test_download_failure_visibility.py:151-473`, `test_youtube_adapter_visibility.py:62-107`, `test_api_download_visibility.py:125`, `:160`, `test_youtube_adapter.py:469`, `:739` |
| AC-137.10 (renderer) | Row 2a: `Tests  1 failed \| 49 passed (50)` (`s65-ui-red-137.txt`). `AssertionError: expected '—' to contain 'No format at the chosen quality. Pick…'` | Row 3: `Tests  104 passed (104)` (`s65-ui-green-137.txt`); gate `ui-tests` | `downloader-page.behavior.test.ts:1219` |
| AC-137.1 | A characterisation of row 1. Row 2a's guard: `1 passed, 16 deselected in 0.19s` (`s65-r2a-guard.txt`) | Gate `py-tests` | `test_download_failure_visibility.py:115` |
| AC-137.12 (execution round 1 F1, D-639) | Run against the pre-fix classifier and generic branch, restored by byte replacement with SHA-256 checks (`f1_red_receipt.py`): exit 1 (`s65-f1-red-137-12.txt`). `At index 0 diff: 'Download failed: co okie=SECRET.' != 'Download failed: [REDACTED].'` | `149 passed in 5.54s` over the visibility unit, integration and e2e files, `test_youtube_adapter.py`, `test_domain.py` and `test_transcript_metadata.py` (`s65-f1-green.txt`); gate `py-tests` | `test_youtube_adapter_visibility.py:170` |

- **red-check.** Row 2a's check (`s65-red-137-check.txt`) reads `red-check: 2 receipt(s), 12 required test(s), 0 problem(s)`. Every failing block failed by assertion alone. AC-137.12's check (`s65-f1-red-check.txt`, `--require test_ac_137_12`) reads `red-check: 1 receipt(s), 1 required test(s), 0 problem(s)`.
- **The failures in the Red run that aren't AC-137 tests** are the two moved pins, named in full: `test_ac_6_10_age_gate_and_unmapped_download_error` and `test_ac_76_6_age_gate_and_media_download_keep_their_types_neg` (F2).
- **AC-137.6's file-mode and age-gate test** (`:97`) passed in Red. It characterises types that already held, beside the three AC-137.6 tests that failed.
- **The passes in the Red run** are AC-137.1, the other adapter and domain tests in the same files, and the cases that row 1's stubs already met.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s65-0-baseline", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-11-download-failure-visibility/baseline.ps1 *> C:/Temp/av-kit/s65-baseline.txt (task.md row 0's Validation cell, run from P:/av-kit; base suites in C:/Temp/av-kit/s65-base-py.txt, s65-base-ui.txt, s65-base-mcp.txt, s65-base-mcp-build.txt and s65-base-ruff.txt)", "scope": "Row 0: D-622 to D-625 ruled (S14), the queue (S8), the shapes and absent names (S11), baseline.sha and baseline-dirty.txt, the anchors and line endings, the lock sync (S4), the base suites, and the red-check and identity selftests", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 003e5b1 before any row", "output": "D-622 to D-625 ruled=True; queue: MEU-136 approved, MEU-137 to MEU-139 pending; 003e5b1 is an ancestor of HEAD: True; shapes wrong (S11): []; missing targets: [] new files already present: []; ui lock sync: 651 locked packages, 0 differ, 0 missing; mcp-server lock sync: 133 locked packages, 0 differ, 0 missing; base pytest 2108 passed, 37 warnings in 152.45s; base UI Test Files 119 passed (119), Tests 1279 passed (1279); base MCP Test Files 35 passed (35), Tests 520 passed (520); ruff All checks passed!; red-check selftest: 44 fixture(s) (13 positive, 31 negative), 0 wrong; identity selftest: 0 failure(s); baseline: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s65-1-types", "command": "rtk proxy uv run pytest tests/unit/test_domain.py tests/unit/test_download_failure_visibility.py (the download unit tests) tests/integration/test_youtube_adapter.py tests/unit/test_transcript_metadata.py -q *> C:/Temp/av-kit/s65-types-py.txt; rtk proxy uv run pyright packages/ *> C:/Temp/av-kit/s65-types-pyright.txt; rtk proxy uv run ruff check packages/ tests/ *> C:/Temp/av-kit/s65-types-ruff.txt; npm --prefix ui run typecheck *> C:/Temp/av-kit/s65-types-ui.txt; the caller grep *> C:/Temp/av-kit/s65-row1-callers.txt (task.md row 1's Validation cell)", "scope": "Row 1: the shared names as wrong stubs (DownloadFailureCause, DownloadFailedError, download_failure_message, clean_line, scrub_line, classify_download_error, sabr_phrase, SABR_PHRASES, FAILURE_CAUSE_NEEDLES, SABRStatus.matched_phrase, _YtDlpLogger.debug_enabled and matched_phrase, sabrResultText, DownloadListItem.error_message), the row 1 pins, AC-137.1, and the caller grep", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 003e5b1 plus rows 0 to 1", "output": "264 passed in 10.33s; pyright 0 errors, 0 warnings, 0 informations; ruff All checks passed!; typecheck exit 0; callers: 135 lines"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s65-2a-red-137", "command": "rtk proxy uv run pytest (row 2a's files: test_download_failure_visibility.py, test_youtube_adapter_visibility.py, test_api_download_visibility.py, test_youtube_adapter.py) --tb=short -q *> C:/Temp/av-kit/s65-py-red-137.txt; npm --prefix ui run test -- tests/unit/downloader-page.behavior.test.ts *> C:/Temp/av-kit/s65-ui-red-137.txt; red-check.py with the 12 --require ids *> C:/Temp/av-kit/s65-red-137-check.txt; pytest -k test_ac_137_1_ *> C:/Temp/av-kit/s65-r2a-guard.txt (task.md row 2a's Validation cell)", "scope": "MEU-137 Red: AC-137.2 to AC-137.11 against row 1's stubs, the AC-6.10 and AC-76.6 pins, and AC-137.1 as a passing guard", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 003e5b1 plus rows 0 to 2a", "output": "Python 23 failed, 91 passed in 2.49s. Decisive: assert [] == ['download.started', 'download.failed'] x6; DomainError != DownloadFailedError x3; other != refused x2; 'download failed: other' == 'Download failed: bad xy.'. UI Tests 1 failed | 49 passed (50): expected '—' to contain 'No format at the chosen quality. Pick…'. red-check: 2 receipt(s), 12 required test(s), 0 problem(s). AC-137.1 guard: 1 passed, 16 deselected in 0.19s"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s65-3-green-137", "command": "rtk proxy uv run pytest (row 3's files: the MEU-137 tests, every caller of _finish, DOMAIN_ERROR_TYPES and DownloadListItem, test_domain.py) --tb=short -q -rfE *> C:/Temp/av-kit/s65-py-green-137.txt; npm --prefix ui run test -- (the downloader tests) *> C:/Temp/av-kit/s65-ui-green-137.txt; pyright, ruff and the UI typecheck *> C:/Temp/av-kit/s65-r3-*.txt (task.md row 3's Validation cell)", "scope": "MEU-137 Green: FAILURE_CAUSE_ENUM, FAILURE_MESSAGE, CLEAN_LINE, SCRUB_LINE, FAILED_ERROR, FAILURE_CAUSE, FAILURE_RAISE, FAILURE_LOG, CARD_REASON", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 003e5b1 plus rows 0 to 3", "output": "286 passed in 10.75s; UI Test Files 4 passed (4), Tests 104 passed (104); pyright 0 errors, 0 warnings, 0 informations; ruff All checks passed!; typecheck exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s65-6-records", "command": "task.md row 6, run from P:/av-kit: the S3 check, the pre-status copies, the spec text in 01, 02, 03 and 06, MEU-137 to MEU-139's fields byte-edited in meu-status.yaml (S15), the registry and BUILD_PLAN rows, the grouping heading and row 65, issue-resolve.py on s65-resolve.json; its checks into C:/Temp/av-kit/s65-r6-render.txt, s65-r6-issues.txt, s65-r6-issue-render.txt and s65-r6-status.txt", "scope": "Row 6: the D3 spec text, MEU-137 to MEU-139 ready_for_review with this plan, the three issues resolved, the render, and grouping row 65 executed", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 003e5b1 plus rows 0 to 6", "output": "Drift check passed - SSOT loaded (142 MEUs, 12 phases), rendered regions match on-disk content; OK: known-issues.md is up-to-date; meus: ['ready_for_review', 'ready_for_review', 'ready_for_review'] issues: ['resolved', 'resolved', 'resolved']; tracker row 65 executed; heading 9: True; 02 and 03 notes: [True, True]; 01 error row: True"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s65-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-11-download-failure-visibility/session-gate.ps1 *> C:/Temp/av-kit/s65-gate-h1.txt; then Select-String for ' exit=', 'not_run', 'skipped', 'tested_state', '_sha256 ', 'outside scope', 'mismatch', 'session-gate:' and exit $code (task.md row H1-2's Validation cell, run from P:/av-kit; per-step receipts C:/Temp/av-kit/s65-D6-*.txt; run 3, after D-639 (execution round 1 F1), copied to C:/Temp/av-kit/s65-gate-h1-run3.txt; run 2 is s65-gate-h1-run2.txt)", "scope": "H1-2: the registered full gate. Static: py-types, py-lint, ui-types, ui-lint, task-contract, scope-paths, red-check-selftest. Full: py-tests, openapi, ui-tests, ui-build, mcp-types, mcp-build, mcp-tests, state-render, issues-render. Runtime: ui-electron. Identity before and after. Skipped with reasons: mcp-audit, build-record, package-build, real-ffmpeg", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "003e5b1466c4b7accadc6b3267c7d4b1315f2991+a12677f6bd755b550577edac1f737db236bb558858f1de93dbe75f71d986b4ba", "output": "py-types 0 errors, 0 warnings, 0 informations; py-lint All checks passed!; task-contract OK: 26 row(s), 24 fully checked, 2 exempt (view_file): H1-5, H2-1; scope-paths changed paths: 44 outside scope: [] head moved (S3): False; baseline-dirty paths changed since row 0 (S3): []; red-check selftest: 44 fixture(s) (13 positive, 31 negative), 0 wrong; py-tests 2152 passed, 37 warnings in 307.22s (0:05:07); ui-tests Test Files 120 passed (120), Tests 1285 passed (1285); mcp-tests Test Files 35 passed (35), Tests 520 passed (520); state-render Drift check passed (142 MEUs, 12 phases); issues-render OK: known-issues.md is up-to-date; ui-electron 26 passed (27.9s); tested_state before = after; session-gate: all steps exit 0"}
```

### Quality Gate Results

`s65-gate-h1-2` (H1-2) is the fresh full record. Its last line is:

> session-gate: all steps exit 0

- **Two runs.** Run 1 (`s65-gate-h1-run1.txt`) stopped at `py-tests`, exit 1 (`s65-D6-py-tests-run1.txt`): `1 failed, 2150 passed, 37 warnings in 167.72s (0:02:47)`. The one failure is `tests/unit/test_capture_adapter.py::test_ac_130_10_cmyk_icc_to_srgb[AC-130.10]`, `assert cropped.info.get("icc_profile") == srgb.tobytes()`, `At index 35 diff: b';' != b':'`. Byte 35 lies in the ICC header's creation-time field, so the two sRGB profiles the test builds were stamped a second apart. That file and the capture adapter are untouched by this session (MEU-130). Under Session 53 RULE-4 it was rerun once alone: `1 passed in 0.17s` (`s65-h1-2-rerun-ac130-10.txt`). Run 2 (`s65-gate-h1-run2.txt`) passed every step. Both runs' receipts are kept. The flake is raised for Mat in §Deferred Items.
- **Run 3, after D-639.** Execution round 1's F1 changed `services/download.py`, `adapter.py` and `test_youtube_adapter_visibility.py`, so the whole gate ran again (`s65-gate-h1.txt`, the same bytes as `s65-gate-h1-run3.txt`) and passed every step. The record `s65-gate-h1-2` above and the counts below are run 3's.
- **Static checks.**
  - pyright: 0 errors, 0 warnings, 0 informations. ruff check: all checks passed. The UI typecheck and eslint (`--max-warnings 0`) exited 0.
  - lint_task_contract passed on 26 rows (24 fully checked; H1-5 and H2-1 are exempt as `view_file`).
  - scope-paths found 44 changed paths, none outside scope (run 2's 41 plus the three handoffs, which H1-6 wrote after it). HEAD `003e5b1` did not move, and no path in `baseline-dirty.txt` changed since row 0 (S3). Before the gate, the tree's changed paths were listed against the gate's scope paths (Session 60 RULE-4).
  - The red-check selftest read 44 fixtures (13 positive, 31 negative), with 0 wrong.
- **Suites.**
  - pytest: 2152 passed (the baseline's 2108 plus 44 new cases, AC-137.12 among them).
  - UI: 1285 passed in 120 files (the baseline's 1279 in 119, plus 6 cases and `sabr-panel.test.ts`).
  - MCP: 520 passed in 35 files, the same as the baseline.
  - Electron E2E: 26 passed.
- **Build and state.**
  - `export_openapi.py --check`, the UI build, the MCP typecheck and the MCP build exited 0. No route or response model changed, and `DownloadListItem.error_message` already existed in the API.
  - The state render and the issue render match the files on disk.
  - After the gate, H1-3's `render --check` (`drift-check.txt`) and H1-4's `export_openapi.py --check` with `git diff --quiet` (`openapi-check.txt`, `openapi.committed.json unchanged: True`) passed, both exit 0. H1-1 found no unchecked implementation row (`task-unchecked.txt`: `unchecked implementation rows: []`).
- **Skipped.** Each skip has a reason in the gate:
  - `mcp-audit`: it needs the live network, which the brief forbids;
  - `build-record`: no installer build;
  - `package-build`: no packaged surface change (MEU-125 ran the package build and its smokes);
  - `real-ffmpeg`: no FFmpeg path changed, and `py-tests` still runs the module.
- **Identity.**
  - The tested_state was the same before and after: `003e5b1466c4b7accadc6b3267c7d4b1315f2991+a12677f6bd755b550577edac1f737db236bb558858f1de93dbe75f71d986b4ba` (run 2's was `…+02916a61…`, before the F1 fix).
  - The closeout records, this plan's `*.md`, `task.md` and this session's handoffs are left out of the identity, so writing them doesn't change it.
- **Warnings.** The gate's `py-tests` has 37 warnings. Each is Pillow's `getdata` deprecation from a capture test helper, none from this session's code: 16 from `test_capture_sheet_adapter.py`, 16 from `test_video_real_ffmpeg.py`, and 5 from `test_capture_export_adapter.py`'s two AC-136.4 tests. The baseline had the same 37.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/domain/enums.py` | modified | `DownloadFailureCause` |
| `packages/core/src/avkit_core/domain/errors.py` | modified | `DownloadFailedError`, last in `DOMAIN_ERROR_TYPES` |
| `packages/core/src/avkit_core/domain/download.py` | modified | `download_failure_message`, `clean_line` (and MEU-138's `matched_phrase`) |
| `packages/core/src/avkit_core/services/download.py` | modified | `scrub_line` and its private helpers; `FAILURE_LOG` in `_run_one` (and MEU-138's `SABR_LOG`) |
| `packages/infrastructure/src/avkit_infra/youtube/adapter.py` | modified | `FAILURE_CAUSE_NEEDLES`, `classify_download_error`, `FAILURE_RAISE` (and MEU-138's and MEU-139's mechanisms) |
| `ui/src/renderer/src/features/downloader/useDownloadQueue.ts` | modified | `DownloadListItem.error_message` |
| `ui/src/renderer/src/features/downloader/DownloaderPage.tsx` | modified | `CARD_REASON` (and MEU-138's panel) |
| `tests/unit/test_download_failure_visibility.py` | new | AC-137.1 to .5, .7, .8 (and MEU-138's and MEU-139's unit ACs). LF, 679 lines |
| `tests/integration/test_youtube_adapter_visibility.py` | new | AC-137.6, AC-137.12 (D-639) (and AC-138.5, AC-139.4, AC-139.7). LF, 367 lines |
| `tests/e2e/test_api_download_visibility.py` | new | AC-137.9, .11 (and AC-138.5 to .7, AC-139.5). LF, 340 lines |
| `tests/unit/test_domain.py` | modified | `DOMAIN_ERROR_TYPE_NAMES`, `ERROR_ARGS` (and MEU-138's `SPEC_SABR_STATUS_FIELDS`) |
| `tests/integration/test_youtube_adapter.py` | modified | The AC-6.10 and AC-76.6 pins (and MEU-138's AC-6.11 pin) |
| `ui/tests/unit/downloader-page.behavior.test.ts` | modified | AC-137.10 (and AC-138.7, AC-138.8) |
| `docs/build-plan/01-domain-layer.md`, `03-service-layer.md` | modified | The `DownloadFailedError` row (`01:547`); the Delivered note (`03:714`) |
| `.agent/context/meu-status.yaml`, `meu-registry.md`, `docs/BUILD_PLAN.md`, `known-issues.yaml`, `known-issues.md`, `triage-output.yaml`, the grouping file | modified | Only MEU-137 to MEU-139's fields and rows, the three issues, the grouping's §9 heading and row 65 (row 6) |

The MEU-138 and MEU-139 handoffs list their own files: `sabr-panel.ts`, `sabr-panel.test.ts`, `wiring.py`, `test_api_wiring.py`, `test_transcript_metadata.py`, `settings-page.test.ts`, `02-infrastructure.md` and `06-gui.md`.

`git diff --stat 003e5b1` on the tracked files: 27 files changed, 799 insertions(+), 191 deletions(-). That is after D-639 and H1-3; the 27th file is `current-focus.md` (5 lines, H1-3). The four new test files hold 679, 367, 340 and 53 lines.

Line endings were measured with Python bytes before each edit and kept:
- These files stayed CRLF: `enums.py`, `errors.py`, `domain/download.py`, `services/download.py`, `adapter.py`, `wiring.py`, `test_domain.py`, `test_youtube_adapter.py`, `test_api_wiring.py`, `settings-page.test.ts`, 02, 03 and 06.
- These files stayed LF: `useDownloadQueue.ts`, `sabr-panel.ts`, `test_transcript_metadata.py`, 01, `meu-status.yaml`, `meu-registry.md`, `BUILD_PLAN.md`, the issue files and the grouping file.
- `DownloaderPage.tsx` and `downloader-page.behavior.test.ts` were already mixed in the working tree at row 0 (`s65-anchors.txt`: 749 CRLF and 221 LF; 2096 CRLF and 286 LF). The edits kept each region's ending: the page is 750 CRLF and 221 LF, and the test file 2096 CRLF and 399 LF, its new blocks LF.
- New files are LF.

```diff
 # services/download.py, _run_one (abridged)
+        log.info("download.started", job_id=job.id, video_id=job.video_id)
-        except DomainError as exc:
-            ...
-        except Exception as exc:
-            ...
+        except Exception as exc:
+            if isinstance(exc, DownloadFailedError):
+                cause, raw = exc.cause, exc.detail
+            else:
+                ...
+            detail = scrub_line(raw)
+            reason = None
+            if cause is DownloadFailureCause.other:
+                reason = safe_reason(detail) or type(exc).__name__
+            stored = download_failure_message(cause, reason)
+            self._finish(job.id, DownloadStatus.Failed, error=stored)
+            log.error("download.failed", job_id=job.id, video_id=job.video_id, error=stored, detail=detail)
 # DownloaderPage.tsx
+    errorMessage: item.error_message ?? null,
```

The excerpt is abridged. The source is `services/download.py:620-711` and `DownloaderPage.tsx:485`.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

Codex reviews the execution in one rolling report, `2026-11-11-download-failure-visibility-implementation-critical-review.md`, on the ledger loop `s65-execution-2026-11-11-download-failure-visibility`.

| Round | Verdict | Findings | Tested state |
|-------|---------|----------|--------------|
| 1 | changes_required | 1 finding, F1 High (AC-137): cleaning inside `classify_download_error` lost the split before `SCRUB_LINE`; blocking 1; intent achieved partial; 13,389,317 tokens (`C:/Temp/av-kit/dispatch/s65-exec-run-r1.txt`) | `003e5b1466c4b7accadc6b3267c7d4b1315f2991+02916a61145051d9ce6a921eeb0b1340f52609efe4a06f5bf407733e7a2e5aec` |
| 2 | approved | F1 fixed (D-639, AC-137.12); 0 new findings; blocking 0; intent achieved yes; 3,259,894 tokens, 16,649,211 of 40,000,000 in all (`C:/Temp/av-kit/dispatch/s65-exec-run-r2.txt`) | `003e5b1466c4b7accadc6b3267c7d4b1315f2991+a12677f6bd755b550577edac1f737db236bb558858f1de93dbe75f71d986b4ba` |

### Verdict

Approved by Codex in round 2 of 6. Round 1's F1 is `fixed` in the round 2 Prior Pass Summary, and round 2 has no new finding. H1-7a (`C:/Temp/av-kit/review-state-check.txt`) reads `OK: review_mode=execution; round 2 of 6; verdict=approved; open findings=0`, and H1-7b (`C:/Temp/av-kit/exec-review.txt`) reads `OK: approved at round 2 of 6, 0 open blocking findings`. MEU-137 moves to `approved` in H2-2.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| `add_to_queue_extract_start` logs `url=` (`services/download.py:262`; `:178` at `003e5b1`) | privacy, raised for Mat | None | Plan §Out of Scope. `url` is not a `CONSOLE_FIELD`, so the Console drops it and `HealthService` prints only the safe message. It is a raw value in the event dict before the processor (Session 50 RULE-1: raised, not fixed, since no surface shows it) |
| A Cancelled log line | feature | None | D-634; AC-137.8 checks that Cancelled logs nothing new |
| Session 64's items: 16-bit gray in `_encode_view` and `bake`; the other strict MCP actions echoing unknown keys; PNG transparency keys in crop and the view; `avkit_capture.export` in `BASELINE_PENDING`; the validator counting ACs by family only | mixed, raised for Mat | None | Plan §Out of Scope; named for Mat in Session 64's handoff, not this session's |
| The client pin and fallback | bug | MEU-140, MEU-141 (Session 66) | Their own grouping sessions |
| The MP3 convert | bug | MEU-142 (Session 67) | Its own grouping session |
| AC-130.10's sRGB profile comparison fails when the two profiles are built in different seconds (gate run 1) | test flake, raised for Mat | None | Session 53 RULE-4: an untouched file (MEU-130), rerun once, passed; not this session's scope |
| Commit and push | out-of-scope | — | Mat's "Once complete commit and push" (H2), after Codex approves |

**Execution notes.**
- **One branch for every non-age, non-cancel failure.** `DownloadFailedError` gives its own cause and detail; any other exception gives its first line, with `CookieTestError` as `cookies`. One code path then computes the detail, the reason and the stored message, so each failure logs exactly one `download.failed` line (Departure 3).
- **The status write.** `meu_status.py update` re-wrapped other MEUs' YAML (MEU-140 to MEU-142), so row 6 kept the pre-row copy and byte-edited only MEU-137 to MEU-139's five fields each, checking that the result parses equal to the tool's output (S15, Session 61 RULE-5). `render --check` passes (`s65-r6-render.txt`).

### Departures and their basis

1. **AC-137.10 test ids (row 3, a test file edit in Green).** Row 3 says "No test file changes". In Green, the AC-137.10 `it` block failed with `0% complete` on its `dl-2` card, because the MEU-46 fixture's processor names `current_job_id: 'dl-2'` (`downloader-page.behavior.test.ts`, the fixture near `:548`), so that card renders as in flight. The session script `row3_fix_ac10.py` moved the block's four ids to `dl-71` to `dl-74`. It touched only that LF block and asserted that the file's endings stay 2096 CRLF and 322 LF. The AC text and every assertion are unchanged; only the fixture ids moved. Disclosed for review under Session 59 RULE-1.
2. **Private helpers not named in the plan.** `services/download.py` gains `_SPLIT_GAP`, `_HOME_SEPARATORS`, `_mark_splits` and `_scrub` beside the planned `_scrub_split_home` and `scrub_line`. Each matches the reference probe (`ref_check.py`, `FAILS 0`). They are in Changed Files, and they sit in the gate scope through `services/download.py`.
3. **One `except Exception` branch.** `_run_one`'s former `except DomainError` and `except Exception` branches are merged into one branch that computes the cause, raw text, detail, reason and stored message, then calls `_finish` and logs `download.failed`. The `DomainError` import, used only by the old branch, is removed.
4. **The edit tool fix.** The session's byte-edit helper, `edit.py`, took a replacement's line ending from the next line, so in row 2a it wrote 5 CRLF lines into the behaviour test's LF region. `row2a_fix.py` restored them to LF (asserting 2096 CRLF and 322 LF), and `edit.py` now keeps LF when the matched old text is LF.
5. **Gate run 1** stopped at `py-tests` on an untouched file (§Quality Gate Results).
6. **Execution round 1 F1, fixed through D-639.** Codex found that cleaning inside `classify_download_error` lost the split before `SCRUB_LINE` ran: a real failed download with `ERROR: co\tokie=SECRET` stored and logged `co okie=SECRET`, a tab-split link survived, and removing a NUL before a home path joined it to the word before, so the home marker survived. The ruling also covered the service's generic branch, which had used `str.splitlines()` and so split at U+0085 and U+2028 too. A Fable subagent ruled D-639 A under Mat's delegation: `first_line` splits only at CR, LF and CRLF and returns the line as written; the classifier drops only an anchored leading `ERROR:`; the generic branch uses `first_line(str(exc))`; and AC-137.12 drives the real adapter, service and SQLite. Red first (`s65-f1-red-137-12.txt`, exit 1), then the fix (`services/download.py:136`, `:660`; `adapter.py:119`, `:367`). The plan gained AC-137.12 and the D-639 block (29 ACs), and task.md's H1-6a check now expects 29. The citations in all three handoffs were moved by a line map built from the pre-fix copies (`f1_line_map.py`, `f1_cite_sweep.py`) and checked line by line (`s65-f1-cite-check.txt`).

The other departures recorded before the gate belong to MEU-138 (the Console's `request_id` field; an Active result without a phrase) and MEU-139 (`_emit` and `_debug_now`; the `ERROR:` prefix read after cleaning; `extract_video_ids` in AC-139.4). Each is in its own handoff.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-12 | claude-code-local (Claude Opus 5.5) | The context state after row 3 (D-625 B) and the departures recorded before the gate |
| Completed | 2026-11-12 | claude-code-local (Claude Opus 5.5) | The MEU-137 handoff after the H1-2 gate |
