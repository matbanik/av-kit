---
date: "2026-11-12"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-11-download-failure-visibility/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s65-execution-2026-11-11-download-failure-visibility"
round: 2
---

# Critical Review: 2026-11-11-download-failure-visibility

> **Review Mode:** execution. **Verdict:** approved. **Intent achieved:** yes. F1 fixed; zero open findings and no new High or Critical findings.

The round 1 observations and receipts below are retained as historical evidence. The Findings status and frontmatter reflect round 2; the appended Recheck gives the current observations and verdict.

## Intent Anchor

Session 65 makes a failed download, a SABR check and yt-dlp's own messages visible. A failed download's card says why in one short av-kit sentence per cause, and the Console has a matching `download.failed` line with yt-dlp's first line, redacted, in `detail`. Check SABR matches yt-dlp 2026.10.26's own SABR words, the page always states the last result with its time, and Check, Force and Clear each log one line. yt-dlp's warnings and errors always reach the Console with their text in a kept field; the existing Settings switch adds its debug and info lines, and a change applies on the next call without a restart.

## Scope

Reviewed Session 65 / MEU-137, MEU-138 and MEU-139's working-tree delta on `main`, HEAD `003e5b1466c4b7accadc6b3267c7d4b1315f2991`: product changes, four new test files, changed tests/pins, scoped record changes, the three handoffs and authoritative plan/task. Baseline-dirty hashes confirm only `task.md` changed among the nine pre-existing untracked plan/review paths. Applied execution-critical-review, IR-1 through IR-7 and AV-1 through AV-6. Author: Claude Code / Anthropic; reviewer: Codex / OpenAI, independently.

Repository files remained read-only. All reviewer scripts, databases, health logs and receipts are under `C:/Temp/av-kit`. No product suite, app/API launch, MCP call, network request, package/model download, git mutation or process termination ran. Every adapter probe patched `YoutubeDL` for the entire call. Prohibited files were not opened. The documented `.claude/settings.local.json` path was excluded before identity enumeration could read it. H2 and commit/push remain the coordinator's post-review work.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F1 | High | yes | behavior | Cleaning inside `classify_download_error` destroys split/boundary information before `SCRUB_LINE`. A real failed download with `ERROR: co\tokie=SECRET` stores and logs `co okie=SECRET`; a tab-split link also survives, and removing a NUL before a home path joins it to the preceding word so the home marker survives. This violates AC-137.7/.9's privacy behavior, D-627/D-638 and the goal's redacted failure line. | `packages/infrastructure/src/avkit_infra/youtube/adapter.py:365`; downstream `packages/core/src/avkit_core/services/download.py:651`; coverage gap `tests/e2e/test_api_download_visibility.py:99` | Preserve the raw split/boundary information until it has passed through `scrub_line`, while retaining the planned first-line and coloured-prefix behavior. Add a patched-`YoutubeDL` → adapter → service → SQLite/Console regression covering the split cookie/link and home cases. Keep existing assertions. | fixed |

## Probe Detail — F1, Round 1

`scrub_line('ERROR: co\tokie=SECRET')` correctly returns `ERROR: [REDACTED]`. But `classify_download_error` turns the tab into an ordinary space, returns `other, 'co okie=SECRET'`, and the service can no longer distinguish that space from the deliberately accepted plain-space case.

The independent patched-adapter/real-SQLite/real-HealthService probe observed:

| yt-dlp `DownloadError` text | Stored `error_message` and matching Console fields |
|---|---|
| `ERROR: co\tokie=SECRET` | `Download failed: co okie=SECRET.`; `detail=co okie=SECRET` |
| `ERROR: https:\t//e.example/private` | `Download failed: https: //e.example/private.`; same unredacted link in `detail` |
| `ERROR: at\x00<HOME-marker>\v.mp4 cookie=SECRET` | `Download failed: at<HOME-marker>\v.mp4 [REDACTED].`; same home marker in `detail` |
| Home marker with a tab inside its user-name component | The component survives with a space inserted, in both stored message and `detail`. |

The probe confirmed `SECRET`, the synthetic home marker and `e.example` in captured stdout as well. `download.failed` is an ERROR event, so HealthService also persists its displayed fields. The database mapper, route `_job_out` at `routes/downloads.py:56` and new card mapping at `DownloaderPage.tsx:485` forward the stored text unchanged: the user and API clients see the leaked value. No real credential/home path was used.

The current AC-137.7 and AC-137.9 tests inject `DownloadFailedError` directly (`test_download_failure_visibility.py:356`, `test_api_download_visibility.py:99`). Their assertions are meaningful for the service, but skip the classifier that destroys the information. This is one product defect with several examples, not separate findings about each delimiter or about paperwork.

## Review Questions (Round 1)

### Q1 — Failed download goal

Accepted ordinary traces. Independent calls through the patched adapter, service, SQLite and real Console produced the exact named messages for page reload, missing format after a SABR warning, cookie database copy failure and an output `OSError`. Each logged `download.started` before one `download.failed`, with stored text in `error`, safe first-line `detail`, and no `download.done`. The `OSError` detail was exactly `PermissionError: Permission denied`, without its planted filename. An ordinary multiline unknown error stored `Download failed: at ~\v.mp4 [link].`; its second line was absent.

`DownloadFailedError.__str__` contains only the cause. The actual age-gate adapter branch creates the fixed age-restricted text; service tests retain that status/message and one failure line. Cancellation retains only the started line, as D-634 requires. SQLite mappers, `GET /downloads`, the queue item type and card binding preserve the message. The redaction sentence of the goal is **not fully achieved**, for F1. Other goal sentences have implementation and substantive tests.

### Q2 — Cleaning and redaction

Accepted the scrubber in isolation: 32 cookie/link/home/mixed cases across whole, tab, NUL, ANSI, U+0085, U+2028, Cf and surrogate forms passed; another 40 cases covered all five `REDACT_NEEDLES`. Empty/control/surrogate inputs and a 100000-character line did not raise or produce invalid UTF-8. Source inspection confirms marked-home matching precedes joining, retains the original boundary, honors case/separator rules and preserves the readable form when no scrub changes the joined form. Ordinary home-only inputs agree with `scrub_home`; a plain space continues to split a word by design.

Rejected the end-to-end privacy claim: F1 shows that the actual writer reaches `scrub_line` only after lossy classification. `safe_reason` merely cuts/replaces links in the text it receives; it cannot restore the lost boundary or split marker. Stored text and card text therefore share the same leak. Warnings/debug lines call `scrub_line` directly and passed the same split-input checks.

### Q3 — Classification and yt-dlp source

Accepted needle contents/order, case folding, both bot-check apostrophes, first non-empty cleaned line and coloured `ERROR: ` removal. `no_format` becomes `refused` only when that call's logger matched SABR; a SABR phrase alone falls back to `refused`. The offline `s65-ytdlp-cause-strings`, `-sabr-source`, `-sabr-strings` and `-logger-routing` receipts corroborate the installed 2026.10.26 strings and routing. Classification matches its local algorithm; its cleaning step must be composed safely with `SCRUB_LINE` to fix F1.

### Q4 — SABR

Accepted. Whole-word and ordering probes distinguished Sabrina/sabre/sabrs from SABR-only/forcing SABR, rejected a PO Token line alone, and honored phrase priority. All four logger methods scan and retain the first match. Invalid phrase/status pairs raise `ValidationError`; omitted phrase remains valid. The adapter carries the detected phrase, the service stores it, and `_sabr_out`/`SABRStatusOut` keep it off the wire.

Independent probes confirmed one action event for each Check/Force/Clear, scrubbed failed-check ERROR, unchanged stored status and identical re-raised exception. MEU-138 Departure 2 is sound: an allowed Active status without a phrase logs `Active, no phrase recorded` rather than inventing a match. Renderer assertions exercise the user-opened Advanced panel, visible Inactive/Active text and local `09:05:07`; the page's existing error path handles rejected checks. No separate SABR finding.

### Q5 — yt-dlp text and live switch

Accepted. Independent capture found exactly WARNING/ERROR events with debug off, including a coloured `ERROR:` and split cookie/link redaction; debug/info/bare traceback emitted nothing. With debug on these latter methods emitted DEBUG with `detail`, and empty lines emitted nothing. No `message` field is used. Reading the prefix after cleaning is sound: scrubbers retain a leading literal `ERROR:` while removing its ANSI coloring; prefix-less text remains subject to D-632.

Five patched public yt-dlp calls read the source exactly five times and alternated `(quiet, verbose, debug_enabled)` between `(True, False, False)` and `(False, True, True)`. Source inspection and tests cover missing/raising sources as off. The real settings PUT test verifies the captured wiring lambda returns False → True → False, and the settings renderer test checks both PUT payloads. No restart is needed. The accepted early-return cookie checks do not start a yt-dlp operation. No separate logger/switch finding.

### Q6 — Pins and callers

Accepted. The ordered error census, constructor walk with class-specific `ERROR_ARGS`, status-field census, AC-6.10/AC-76.6 exact error types/causes/details, expanded `SABR_LINE_PHRASES` and stricter AC-122.16 debug-off absence assertions preserve their purposes. The old adapter constant is absent and no runtime consumer reads it. Row 1's 135-line and row 4's 55-line greps cover the existing production/test callers; later newly written tests are included in their Green commands and the matching full Python/UI gate. Appending the defaulted status field preserves three-positional-argument callers.

### Q7 — Tests and Red/Green

All 28 AC rows appear in their handoffs and have tests that assert their stated local behavior. The real boundary missing from the privacy evidence is F1. No new skip/xfail/only/todo, assertion neutralization or product stub was found in the changed tests/code.

Grades apply to every new test and changed assertion in the following groups:

| Test file / changed group | IR-5 grade | Basis |
|---|---|---|
| `test_download_failure_visibility.py`: AC-137.1–.5/.8, AC-138.1–.4, AC-139.1–.3/.9 | Strong | Exact signatures, enum/message values, negative invariants, recorded log/commit order, first-match behavior and field limits. |
| Same file: AC-137.7 | Adequate | Exact real-SQLite stored values and redaction negatives; direct domain-error injection omits the actual classifier boundary (F1). |
| `test_youtube_adapter_visibility.py` | Strong | Exact adapter exceptions/causes/details, planted filename absence, real logger/options, recording source and warning-to-Console trace. Its failure cases omit split-text composition (F1). |
| `test_api_download_visibility.py`: AC-137.9/.11 | Adequate | Real wiring, SQLite, authenticated routes, exact displayed values and stdout/marker positive controls; the fake port bypasses classification (F1). |
| Same file: AC-138.5–.7, AC-139.5 | Strong | Exact wire keys/action lines/levels, unchanged status, real Console and positive controls. |
| `test_domain.py`, moved `test_youtube_adapter.py` pins | Strong | Preserved ordered censuses, exact classes, causes/details, exception chaining and positive/negative SABR guards. |
| `test_api_wiring.py`, `test_transcript_metadata.py` | Strong | Real settings PUT/source values, empty off-switch capture and exact redacted on-switch Console text. |
| `downloader-page.behavior.test.ts`, `sabr-panel.test.ts`, `settings-page.test.ts` | Strong | Exact card reason/null/missing fallback, visible result/time, rejected-check banner, all snapshot variants and both switch payloads. |

Independent `red-check.py` runs used precisely task rows 2a/2b/2c's requirements: **12, 8 and 8 required tests, zero problems**, with child-failure sidecars checked. Its selftest passed **44 fixtures (13 positive, 31 negative), zero wrong**. Existing-behavior characterizations were correctly excluded from required Red failures. Green receipts confirm **286/296/306 Python** and **104/108/134 UI** passes. Full receipts confirm **2151 Python; 1285 UI in 120 files; 520 MCP in 35 files; 26 Electron**.

MEU-137 Departure 1 is an honest fixture correction. The preserved row-2a source and `row3_fix_ac10.py` show only four fixture ids and their matching lookups changed to dl-71…dl-74; assertion operators and expected text remain unchanged. The original fixture explicitly names dl-2 as current/in-flight at `downloader-page.behavior.test.ts:548`, explaining the `0% complete` observation. Other disclosed helper/consolidation/line-ending departures are consistent with the actual diff.

### Q8 — Evidence, freshness and records

Accepted execution evidence as real and current; a green suite does not disprove F1. With `ELECTRON_RUN_AS_NODE` unset and a temporary process-local Git ignore containing only `.claude/settings.local.json`, independent `identity.py --state-only` returned exactly:

`003e5b1466c4b7accadc6b3267c7d4b1315f2991+02916a61145051d9ce6a921eeb0b1340f52609efe4a06f5bf407733e7a2e5aec`

This matches every handoff's full evidence and gate before/after. The final gate receipt is byte-identical to run 2. Run 1 genuinely failed at py-tests on AC-130.10, marked subsequent steps not_run, and its isolated rerun passed before the full rerun; no finding is raised about that accepted flake. Recorded stage exits, Green/full counts, Red proofs and baseline/type/record observations agree with the corresponding receipts inspected.

Pre-status comparisons show only MEU-137–139's five status fields each, their registry rows and the derived BUILD_PLAN total, the three issues' resolution/verification fields, and grouping row 65/§9 heading. Generated issue outputs reflect those resolutions. Delivered notes in 01/02/06 match the implementation; 03 and MEU-137's broad privacy claim need the F1 correction. Measured CRLF/LF forms match the handoffs, including the two already-mixed UI files (750 CRLF/221 LF and 2096 CRLF/399 LF). Only `task.md` changed among baseline-dirty files. Independent OpenAPI `--check openapi.committed.json` and MEU render `--check` passed. No wire/schema change was found.

## Checklist Results (Round 1)

### Implementation review

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| IR-1 Live runtime evidence | pass | Codex inspected real-stack API tests, gate/per-step receipts and bound input identity; ran patched adapter/SQLite/HealthService probe | — | Real Console and persistence observed; existing matching API/Electron receipts accepted, not rerun. |
| IR-2 Stub behavior | pass | Codex traced recording ports, SQLite UoW and renderer fixture writes/refetches | — | Actual saved values and exact outputs asserted; no fake persistence inconsistency found. |
| IR-3 Error mapping | pass | Codex read unchanged download routes and checked new API error tests | — | Failed SABR check remains 422, with status preservation; no new write route. |
| IR-4 Fix generalization | n/a | First execution review round | — | No prior execution finding to recheck. |
| IR-5 Test rigor | partial | Codex audited every new/changed test group listed in Q7 | — | Substantive assertions; missing classifier-to-service privacy composition is F1. |
| IR-6 Boundary validation | pass | Codex traced new enum/status validation and unchanged REST schemas | — | Invalid phrase/status tests and off-wire phrase behavior hold. |
| IR-7 Deferrals and AC integrity | pass | Codex compared all 28 numbered plan ACs with tests/handoffs and accepted scope/deferred MEUs | — | No silent AC omission or disguised implementation deferral found. |
| AV-1–AV-6 | partial | Codex checked Red/Green, bypasses, assertions, skips, implementations and sources | — | Red evidence is genuine; F1 prevents the privacy completion claim. |

Manual rows above were observed by **codex-independent-reviewer**, with **null command exit**, not an inferred successful process exit. Paperwork-only checks are outside Mat's requested review substance.

### Independent executable evidence

All Python commands used `PYTHONDONTWRITEBYTECODE=1`, UTF-8 output, `UV_OFFLINE=true`, scratch `UV_CACHE_DIR`, TMP/TEMP under `C:/Temp/av-kit/s65/exec-review-tmp`, and `uv run --no-sync python -B`. Output was redirected under `C:/Temp/av-kit`, child exits captured immediately, then receipts read. The default uv cache was inaccessible; redirecting its cache to scratch resolved that before successful probes. The OpenAPI CLI requires a path after `--check`; the corrected invocation below passed.

```json
{"schema_version":"evidence.v1","check_id":"review-r1-privacy-regression","command":"rtk proxy uv run --no-sync python -B C:/Temp/av-kit/s65-review-regression.py","cwd":"P:/av-kit","scope":"real classifier output composed with the service scrubber","phase":"targeted","exit_code":1,"result":"fail","tested_state":"003e5b1466c4b7accadc6b3267c7d4b1315f2991+02916a61145051d9ce6a921eeb0b1340f52609efe4a06f5bf407733e7a2e5aec","output":"direct scrub: 'ERROR: [REDACTED]'; classifier -> service scrub: 'co okie=SECRET'; AssertionError: Classifier destroys the split marker before SCRUB_LINE can redact the cookie value"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-r1-patched-pipeline","command":"rtk proxy uv run --no-sync python -B C:/Temp/av-kit/s65-review-probe.py","cwd":"P:/av-kit","scope":"nine patched adapter/service/real-SQLite/real-Console failure cases, 32 direct scrub inputs and logger routing","phase":"targeted","exit_code":0,"result":"fail","tested_state":"003e5b1466c4b7accadc6b3267c7d4b1315f2991+02916a61145051d9ce6a921eeb0b1340f52609efe4a06f5bf407733e7a2e5aec","output":"Probe completed. Five ordinary cases had correct stored reasons and started/failed Console events. split-cookie stored 'Download failed: co okie=SECRET.' with detail=co okie=SECRET; split-link and two home-marker cases also survived. Captured stdout: has_SECRET=true, has_home=true, has_link=true. Direct scrub matrix: 32 cases, no failures. Logger routing: scrubbed ERROR/WARNING off, DEBUG additions on."}
```

```json
{"schema_version":"evidence.v1","check_id":"review-r1-sabr-live","command":"rtk proxy uv run --no-sync python -B C:/Temp/av-kit/s65-review-sabr-live.py","cwd":"P:/av-kit","scope":"SABR phrase priority/word negatives, all logger scans, action events/rethrow/status preservation, invalid statuses, five patched public source reads, all redaction needles","phase":"targeted","exit_code":0,"result":"pass","tested_state":"003e5b1466c4b7accadc6b3267c7d4b1315f2991+02916a61145051d9ce6a921eeb0b1340f52609efe4a06f5bf407733e7a2e5aec","output":"40 redact-needle cases: no failures; 8 SABR word/order cases passed; 4 logger methods kept first phrase; Check/Force/Clear each emitted one action event; missing phrase reported truthfully; failed check error=[REDACTED], same exception re-raised, status preserved; 4 invalid status pairs rejected; 5 source reads for 5 patched operations, quiet/verbose/debug toggled together."}
```

```json
{"schema_version":"evidence.v1","check_id":"review-r1-identity","command":"rtk proxy uv run --no-sync python -B docs/execution/plans/2026-11-11-download-failure-visibility/identity.py --state-only","cwd":"P:/av-kit","scope":"current full D6 input identity; ELECTRON_RUN_AS_NODE unset; process-local core.excludesFile=C:/Temp/av-kit/s65-review-ignore.txt, containing only .claude/settings.local.json; existing Git config preserved","phase":"static","exit_code":0,"result":"pass","tested_state":"003e5b1466c4b7accadc6b3267c7d4b1315f2991+02916a61145051d9ce6a921eeb0b1340f52609efe4a06f5bf407733e7a2e5aec","output":"003e5b1466c4b7accadc6b3267c7d4b1315f2991+02916a61145051d9ce6a921eeb0b1340f52609efe4a06f5bf407733e7a2e5aec; exact handoff/gate match"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-r1-red137","command":"rtk proxy uv run --no-sync python -B docs/execution/plans/2026-11-11-download-failure-visibility/red-check.py --require test_ac_137_2 --require test_ac_137_3 --require test_ac_137_4 --require test_ac_137_5 --require test_ac_137_6 --require test_ac_137_7 --require test_ac_137_8 --require test_ac_137_9 --require test_ac_137_11 --require test_ac_6_10_age_gate_and_unmapped_download_error --require test_ac_76_6_age_gate_and_media_download_keep_their_types_neg --require AC-137.10 C:/Temp/av-kit/s65-py-red-137.txt C:/Temp/av-kit/s65-ui-red-137.txt","cwd":"P:/av-kit","scope":"task row 2a exact required Red ids and child exits","phase":"static","exit_code":0,"result":"pass","tested_state":"reviewed historical row-2a receipts","output":"red-check: 2 receipt(s), 12 required test(s), 0 problem(s)"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-r1-red138","command":"rtk proxy uv run --no-sync python -B docs/execution/plans/2026-11-11-download-failure-visibility/red-check.py --require test_ac_138_1 --require test_ac_138_2 --require test_ac_138_3 --require test_ac_138_4 --require test_ac_138_5 --require test_ac_138_6 --require test_ac_138_7 --require AC-138.8 C:/Temp/av-kit/s65-py-red-138.txt C:/Temp/av-kit/s65-ui-red-138.txt","cwd":"P:/av-kit","scope":"task row 2b exact required Red ids and child exits","phase":"static","exit_code":0,"result":"pass","tested_state":"reviewed historical row-2b receipts","output":"red-check: 2 receipt(s), 8 required test(s), 0 problem(s)"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-r1-red139","command":"rtk proxy uv run --no-sync python -B docs/execution/plans/2026-11-11-download-failure-visibility/red-check.py --require test_ac_139_1 --require test_ac_139_2 --require test_ac_139_3 --require test_ac_139_4 --require test_ac_139_5 --require test_ac_139_6 --require test_ac_139_7 --require test_ac_139_9 C:/Temp/av-kit/s65-py-red-139.txt","cwd":"P:/av-kit","scope":"task row 2c exact required Red ids and child exits","phase":"static","exit_code":0,"result":"pass","tested_state":"reviewed historical row-2c receipts","output":"red-check: 1 receipt(s), 8 required test(s), 0 problem(s)"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-r1-red-selftest","command":"rtk proxy uv run --no-sync python -B docs/execution/plans/2026-11-11-download-failure-visibility/red-check.py --selftest","cwd":"P:/av-kit","scope":"offline Red checker positive and negative fixtures","phase":"static","exit_code":0,"result":"pass","tested_state":"current plan-local checker","output":"red-check selftest: 44 fixture(s) (13 positive, 31 negative), 0 wrong: []"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-r1-openapi","command":"rtk proxy uv run --no-sync python -B tools/export_openapi.py --check openapi.committed.json","cwd":"P:/av-kit","scope":"unchanged committed OpenAPI snapshot","phase":"static","exit_code":0,"result":"pass","tested_state":"003e5b1466c4b7accadc6b3267c7d4b1315f2991+02916a61145051d9ce6a921eeb0b1340f52609efe4a06f5bf407733e7a2e5aec","output":"No stdout/stderr; exit 0. Source inspection confirms matched_phrase omitted from SABRStatusOut and route projection."}
```

```json
{"schema_version":"evidence.v1","check_id":"review-r1-render","command":"rtk proxy uv run --no-sync python -B tools/meu_status.py render --check","cwd":"P:/av-kit","scope":"MEU status/render drift","phase":"static","exit_code":0,"result":"pass","tested_state":"003e5b1466c4b7accadc6b3267c7d4b1315f2991+02916a61145051d9ce6a921eeb0b1340f52609efe4a06f5bf407733e7a2e5aec","output":"Drift check passed — SSOT loaded (142 MEUs, 12 phases), rendered regions match on-disk content"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-r1-evidence-record-audit","command":"rtk proxy uv run --no-sync python -B C:/Temp/av-kit/s65-review-audit.py","cwd":"P:/av-kit","scope":"handoff evidence extraction, baseline-dirty byte hashes, pre-status diffs, changed-file line endings, task Red requirements, gate receipts/copy","phase":"static","exit_code":0,"result":"pass","tested_state":"003e5b1466c4b7accadc6b3267c7d4b1315f2991+02916a61145051d9ce6a921eeb0b1340f52609efe4a06f5bf407733e7a2e5aec","output":"Only task.md changed among baseline-dirty paths. Five pre-status comparisons show only scoped records/derived total/grouping edits. Current line endings match the handoffs. Red requirements match 12/8/8 invocations. Gate run 1: exit 1 at py-tests, 1 failed/2150 passed; run 2 all step exits 0, 2151 Python/1285 UI/520 MCP/26 Electron, identity equal. Final gate copy equals run 2 byte-for-byte."}
```

## Verdict (Round 1)

**changes_required** — the work achieves the ordinary failure, SABR and logger behavior, but the actual failed-download path can persist and display sensitive material that `scrub_line` would remove from the original text. F1 is an independently reproduced High behavioral/privacy defect under **AC-137**. Fix that boundary and add an adapter-through-storage/Console regression, then rerun affected checks and submit the complete rolling report for recheck. No approval, implementation correction, commit or push was performed by this reviewer.


## Recheck (Round 2)

**Date:** 2026-11-12. **Reviewer:** codex-independent-reviewer (OpenAI); author Claude Code (Anthropic). Scope is F1, D-639, AC-137.12 and affected callers/evidence only. D-639's delegated ruling is accepted as instructed. Round 1's other accepted behavior remains accepted.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| F1 | open | fixed |

### Corrections Applied

- `first_line` splits only CR, LF and CRLF, skips lines whose cleaned form is empty and returns the selected line unchanged (`packages/core/src/avkit_core/services/download.py:133-146`). The generic exception branch now uses it (`:660`).
- The classifier passes that raw line through an anchored, single leading `ERROR:` strip; only surrounding ANSI codes/whitespace are consumed (`packages/infrastructure/src/avkit_infra/youtube/adapter.py:119`, `:367`). It no longer imports `clean_line`. The original split/boundary information now reaches the service scrub at `packages/core/src/avkit_core/services/download.py:666`.
- AC-137.12 drives eight failures through patched yt-dlp, the real adapter/service and real SQLite, asserting exact stored messages, one matching failure log, exact details and absence of secret/link/home parts (`tests/integration/test_youtube_adapter_visibility.py:129-213`). The recorded Red fails an assertion on the pre-fix code; the recorded Green passes 149 tests.
- The plan adds AC-137.12 and D-639 (`implementation-plan.md:202`, `:659-674`); MEU-137 adds coverage, Red/Green and Departure 6. All three handoffs carry run 3's full gate. Inspected moved citations point to the intended current code/tests.

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

### R1 — F1 and preserved behavior

**Fixed.** Reran the exact round 1 regression and nine-case patched-adapter → real SQLite → real HealthService probe. The tab-split cookie stores `Download failed: [REDACTED].` with `detail=[REDACTED]`; the split link stores `Download failed: [link].` with `detail=[link]`; NUL-before-home plus cookie stores `Download failed: at~\v.mp4 [REDACTED].`; the tab-split home stores `Download failed: at ~\v.mp4.`. Their Console fields match. Captured stdout reports `has_SECRET=false`, `has_home=false`, `has_link=false`. The original 32 direct-scrub cases still have zero failures; logger routing still produces scrubbed ERROR/WARNING with debug off and DEBUG additions with it on.

An additional independent probe passed eight line-selection cases, seven prefix cases, five Unicode/long-input cases and 22 needle/case combinations. CR/LF/CRLF select the first non-empty line; U+0085/U+2028 remain within it. Coloured `ERROR:` is dropped, mid-line `ERROR:` is retained, and `ERROR: ERROR: rest` loses only the first prefix. A line containing only `ERROR:` yields empty detail without reading the next line or raising; its stored fallback is `Download failed: DownloadFailedError.`. The generic empty exception remains `Download failed: RuntimeError.`. A generic blank first line now selects the next non-empty line, deliberately per D-639. Classification order/SABR override is unchanged, and `OSError` remains `PermissionError: Permission denied` with no filename. No raise was observed for any tested string; inspection finds no non-total operation for the declared string inputs beyond ordinary resource limits.

### R2 — AC-137.12 and IR-5

**Strong.** The real adapter is the bound port, only `YoutubeDL` is replaced, jobs run through the actual processing path and SQLite, and final assertions compare all eight exact messages/details. Secret absence is checked after positive failure-count/status/error checks; there is no skip, bypass or catch that neutralizes an assertion.

The independent eight-case value probe matches every expected pair. In-memory replacement with the old classifier makes cases 0–5 disagree with those same expectations; replacing only the generic line selection with Unicode `splitlines()` makes case 6 disagree. Neither mutation touches repository files. Thus each defect would fail AC-137.12's exact list assertions independently. The historical Red receipt is an assertion failure at test line 207: `At index 0 diff: 'Download failed: co okie=SECRET.' != 'Download failed: [REDACTED].'`, followed by `1 failed in 39.21s`, exit sidecar `1`. The Red helper restores both modified files in `finally` and checks SHA-256; the current sources equal those fixed backups byte for byte. Independently rerun `red-check`: `1 receipt(s), 1 required test(s), 0 problem(s)`.

### R3 — Collateral and citations

**Pass.** Current caller search finds only the adapter download path and existing tests calling the classifier; no other production consumer relied on the adapter's removed `clean_line` import. The pre-fix/current source delta leaves cause matching, `scrub_line`, `_YtDlpLogger.error` and the `OSError` branch unchanged. AC-137.5's needle/prefix/multiline cases retain their expected values. AC-137.7, .9 and .11 pass raw `DownloadFailedError.detail` directly to the unchanged scrubber; their Unicode, redaction and fallback expectations are preserved. The generic branch changes only as D-639 specifies. AC-139's `ERROR:` test still examines scrubbed text, independently of the new classifier regex, and the rerun logger probe confirms it. The affected Green/full receipts corroborate these claims; no product runner was rerun by this reviewer.

The citation audit printed and inspected 99 current citations into the three moved files across the handoffs (46/22/31). Representative anchors are classifier `:358`/`:367`, service selection/scrub/store `:660`/`:666`/`:670`, new integration test `:170`, SABR test `:216` and live-switch test `:277`; the cited lines/ranges support their claims. Historical baseline citations were retained as historical.

### R4 — Freshness

**Exact match.** Independently ran `identity.py --state-only` with `ELECTRON_RUN_AS_NODE` unset. A process-local Git `core.excludesFile` containing only `.claude/settings.local.json` excludes that path before enumeration; existing Git configuration was preserved and the prohibited file was never opened. Result:

`003e5b1466c4b7accadc6b3267c7d4b1315f2991+a12677f6bd755b550577edac1f737db236bb558858f1de93dbe75f71d986b4ba`

It equals run 3's before/after identity and all three handoffs' full records. The final gate receipt is byte-identical to run 3. Its per-step receipts confirm `2152 passed, 37 warnings` Python, `1285 passed` UI in 120 files, `520 passed` MCP in 35 files and `26 passed (27.9s)` Electron; registered executed stages all exit 0 and `changed paths: 44 outside scope: []`. Existing declared skips remain accepted. Matching full evidence was inspected, not rerun.

### Current Checklist

| Check | Result | Observation |
|---|---|---|
| IR-1 / IR-4 runtime and fix generalization | pass | Original real-Console pipeline rerun; classifier and generic branches separately probed. |
| IR-5 / AV-1 to AV-6 rigor | pass | Exact eight-case assertions, independent old-behavior counterexamples, genuine Red and recorded Green/full success; D-639 supplies the source. |
| IR-2 / IR-3 / IR-6 | pass | Affected persistence, raw error flow and unchanged boundaries inspected; round 1's unaffected conclusions retained. |
| IR-7 AC integrity | pass | New AC-137.12 is in the plan/handoff and has integration evidence; the session now has 29 ACs. |
| Full-gate freshness | pass | Independent identity equals the current run 3 record and all three handoffs. |

### Independent executable evidence (Round 2)

All probes used `uv run --no-sync python -B`, `PYTHONDONTWRITEBYTECODE=1`, UTF-8 output, offline uv with scratch cache, and TMP/TEMP under `C:/Temp/av-kit/s65/exec-review-tmp`; all outputs and writes stayed under `C:/Temp/av-kit`. All yt-dlp instances were patched for the entire call. In-memory mutants were confined to the independent probe process. No product test runner, network call, app/API launch or repository mutation ran.

```json
{"schema_version": "evidence.v1", "check_id": "review-r2-1", "command": "rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s65-r2-python.ps1 C:/Temp/av-kit/s65-review-regression.py", "cwd": "P:/av-kit", "scope": "R1 original F1 regression", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "003e5b1466c4b7accadc6b3267c7d4b1315f2991+a12677f6bd755b550577edac1f737db236bb558858f1de93dbe75f71d986b4ba", "output": "Direct scrub ERROR: [REDACTED]; classifier then scrub [REDACTED]; assertion passes."}
```

```json
{"schema_version": "evidence.v1", "check_id": "review-r2-2", "command": "rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s65-r2-python.ps1 C:/Temp/av-kit/s65-review-probe.py", "cwd": "P:/av-kit", "scope": "R1 original SQLite/HealthService pipeline", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "003e5b1466c4b7accadc6b3267c7d4b1315f2991+a12677f6bd755b550577edac1f737db236bb558858f1de93dbe75f71d986b4ba", "output": "Nine real-adapter/SQLite/Console cases; all four original split failures scrubbed in stored message and detail; stdout has_SECRET=false, has_home=false, has_link=false; 32 direct cases have no failures; logger routing preserved."}
```

```json
{"schema_version": "evidence.v1", "check_id": "review-r2-3", "command": "rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s65-r2-python.ps1 C:/Temp/av-kit/s65-r2-edge-probe.py", "cwd": "P:/av-kit", "scope": "R1/R2 edges and regression sensitivity", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "003e5b1466c4b7accadc6b3267c7d4b1315f2991+a12677f6bd755b550577edac1f737db236bb558858f1de93dbe75f71d986b4ba", "output": "8 line, 7 prefix, 5 stress, 22 needle cases passed. All 8 AC-137.12 value pairs match. Old classifier mismatches cases [0,1,2,3,4,5]; old generic Unicode split mismatches [6]. Four empty/prefix/generic fallback cases passed."}
```

```json
{"schema_version": "evidence.v1", "check_id": "review-r2-4", "command": "rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s65-r2-python.ps1 docs/execution/plans/2026-11-11-download-failure-visibility/red-check.py --require test_ac_137_12 C:/Temp/av-kit/s65-f1-red-137-12.txt", "cwd": "P:/av-kit", "scope": "R2 Red receipt", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "003e5b1466c4b7accadc6b3267c7d4b1315f2991+a12677f6bd755b550577edac1f737db236bb558858f1de93dbe75f71d986b4ba", "output": "red-check: 1 receipt(s), 1 required test(s), 0 problem(s). Inspected Red: test line 207 AssertionError on leaked cookie, exit sidecar 1."}
```

```json
{"schema_version": "evidence.v1", "check_id": "review-r2-5", "command": "rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s65-r2-python.ps1 C:/Temp/av-kit/s65-r2-audit.py", "cwd": "P:/av-kit", "scope": "R3 affected callers/citations and gate records", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "003e5b1466c4b7accadc6b3267c7d4b1315f2991+a12677f6bd755b550577edac1f737db236bb558858f1de93dbe75f71d986b4ba", "output": "Inspected source delta and 99 current handoff citations (46/22/31); all 3 full records match current state/counts. Gate run 3 all executed steps exit 0; Python 2152, UI 1285, MCP 520, Electron 26. Final gate copy byte-identical to run 3; both Red-restored sources equal their fixed backups."}
```

```json
{"schema_version": "evidence.v1", "check_id": "review-r2-6", "command": "rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s65-r2-identity.ps1", "cwd": "P:/av-kit", "scope": "R4 current input identity", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "003e5b1466c4b7accadc6b3267c7d4b1315f2991+a12677f6bd755b550577edac1f737db236bb558858f1de93dbe75f71d986b4ba", "output": "003e5b1466c4b7accadc6b3267c7d4b1315f2991+a12677f6bd755b550577edac1f737db236bb558858f1de93dbe75f71d986b4ba; exact gate run 3 before/after and handoff match. ELECTRON_RUN_AS_NODE unset; excluded only .claude/settings.local.json before enumeration."}
```


### Verdict

**approved** — the implementation achieves the registered intent. F1 is fixed with an end-to-end regression that detects both pre-fix behaviors, and the fresh full-gate state matches. No new findings or unresolved material risk were found within this recheck's scope. D-639's declared line/prefix boundary and round 1's accepted limits remain the review boundary.

Completion-preflight was consulted and the canonical task reread. H1-7 acceptance/ledger collection and H2 remain the coordinator's subsequent work as explicitly assigned; this is implementation review approval, not a claim that session closeout, commit or push has occurred. The coordinator copies this complete report to the canonical path. No repository file was edited by this reviewer.
