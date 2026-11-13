---
date: "2026-11-12"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-12-download-audio-extract/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s67-plan-canonical-2026-11-12-download-audio-extract"
round: 2
---

# Critical Review: 2026-11-12-download-audio-extract

> **Review Mode:** plan. **Verdict:** changes_required. **Intent achieved:** partial, assessed as a plan.

## Intent Anchor

Session 67 makes an MP3 audio download give an MP3. `DownloadService` takes the app's `MediaPort` and, after a good download of an audio-only `StandardMp3` job, converts the file to MP3 with `MediaPort.convert`, stores the MP3 as the job's file and removes the source, in every cookie mode and with no `ConversionJob` row. Without ffmpeg the job fails with the `FFmpegNotFoundError` message on its card through Session 65's failure path, and the downloaded file stays.

## Scope

Reviewed the working-tree implementation plan, task and all six plan-local scripts; the named service/domain/port/adapter/wiring contracts; construction sites and source pins; API/MCP/UI input and card plumbing; the residual spec, grouping, issue and MEU by id. Applied PR-1 through PR-9, the Materiality Gate and Verdict Rule. HEAD observed: `3435b7e516edd86a3d6ce3df497593907684012b`. Implementation remains unstarted: rows unchecked, new product tests absent, service still has no media parameter or conversion step. Claude Code/Anthropic authored the plan; this Codex reviewer did not.

Accepted the grouping and approved Sessions 50–66 as supplied. D-664 through D-670 were judged on their substance; D-671 remains Mat's decision. Other sessions' dirty paths are outside this review. No repository file was edited. No forbidden file was opened, network request made, product suite/build/package manager run, or backend/MCP server started. No baseline/session gate was executed. Review probes and the two authorized selftests wrote only under `C:/Temp/av-kit`. Probe results below are plan-contract observations, not implementation passes.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High | yes | behavior | `FAIL_DETAIL` cannot meet AC-142.13's safety promise. With convert error text ending `Authorization: Bearer` followed by LF or CRLF and a synthetic secret, `LAST_LINE` discards the redaction needle before `scrub_line` sees the secret. The literal planned formatter, passed through the real `HealthService._process`, put `S67_SYNTHETIC_SECRET` in the Console and persisted error log. U+2028 is safe, so testing only that split would miss the regression. Exact path/name replacement also leaves directory paths visible for forward-slash paths and the doubled backslashes produced by `str(OSError(..., filename))`; removing the basename alone leaves the private directory. This affects users whose conversion/filesystem failure text contains these supported safety inputs. Violates AC-142, specifically AC-142.13, `FAIL_DETAIL` and the Where values go contract. Confidence: High. | `docs/execution/plans/2026-11-12-download-audio-extract/implementation-plan.md:114`; `:115`; `:134`; `:182`; `task.md:46` | Specify a convert-error formatter that redacts sensitive spans using the complete text before selecting its diagnostic line, and removes equivalent path representations (including slash variants and escaped filesystem-error filenames). Preserve useful safe final-line diagnostics. Strengthen AC-142.13 with LF, CR and CRLF secret-tail cases, split-home tails and forward-slash/escaped-path cases, asserting the real Console, stdout and persisted log; keep the fixed card text. Do not change the approved Session 65 helpers merely to accommodate this new caller. | fixed |

## Q1 — Goal and three jobs

Accepted the ordinary browser-cookie trace: download returns `.m4a` → SABR handling → `EXTRACT_TRIGGER` → `MP3_RESERVE` → `MediaPort.convert` → stat → Done transaction storing MP3 path/size, progress 1.0, no received height and archive entry → `download.done` → source unlink. AC-142.4–.8 and .17 cover this, including all cookie modes and no conversion row. The Downloader maps `error_message` to the card (`DownloaderPage.tsx:485`).

With no ffmpeg, the real adapter raises its fixed `FFmpegNotFoundError`; the proposed catch maps it through `download_failure_message(other, reason)` to `Download failed: ffmpeg binary was not found.`, calls `_finish(Failed)`, retains the source, removes its reservation and logs failure without an archive entry. AC-142.9, .11 and .18 cover that chain.

For multiline encode failure, `FilesystemError` maps to the fixed `Download failed: MP3 convert failed.` card and retains the source; AC-142.10–.13/.15 cover failure and cleanup. The Console's proposed formatting fails F1. Each 03 residual rule has a row and AC; the missing work is a sound safety transformation for the new error caller, not a missing conversion feature.

## Q2 — Trigger and suffix skip

Accepted D-665. API and MCP permit `standard_mp3` independently of `audio_only`; the UI also sends both values. A video job therefore can carry that format, but the adapter reads it only inside `if options.audio_only` (`youtube/adapter.py:752`). Such a job keeps its selected video, which is consistent with the goal's audio-only qualification. AC-142.4 covers the 18 cells. Skipping a case-insensitive `.mp3` suffix is sound for the adapter-produced file boundary; this session introduces no arbitrary imported-file boundary or request to recode existing MP3s.

## Q3 — Reservation and actual FFmpeg

Accepted D-666. An independent Windows probe closed an `open(path, "xb")` reservation, called the real pinned adapter with the proposed options, and obtained a 26,474-byte MP3 with one `mp3` audio stream. FFmpeg's `-y` works with that closed reservation. Existing candidates produce `FileExistsError` and are never the chosen output; AC-142.5/.11 check their bytes. Numbering is intentionally open-ended, advances on each collision and terminates for a finite unchanged collision set; other filesystem failures must enter row 3's error mapping. No arbitrary numbering cap is required by this contract.

## Q4 — Done ordering, transaction and removal

Accepted D-667: persist the MP3 before deleting the source. The new stat/reservation/filesystem operations are explicitly inside error mapping (`task.md:62`); post-Done unlink failures retain Done and log only the exception type. Progress, received height and archive handling match today's Done transaction (`download.py:696–719`).

If the Done unit of work itself raises after conversion, today's exception propagation remains: no `download.done`, no later source unlink, and both files remain. The plan does not promise database-outage recovery; this is not a reason to expand this session. Removal/clear during conversion deletes the row; the fresh transaction reads None and returns before commit or deletion, so `ROW_GONE` keeps both files. AC-142.14 covers both commands. No proposed queue path resurrects a removed row.

## Q5 — Failure strings, exception partition and Console

Accepted the cause vocabulary and fixed card strings in D-668. `FilesystemError` and `FFmpegEncodeError` derive from `DomainError`, not `OSError`; real nonzero `convert` raises `FilesystemError` (`adapter.py:449`). It reaches the fixed MP3-convert reason. Python filesystem/spawn `OSError` reaches `write_failed`, whose exact existing card is `Couldn't write the file. Check the output folder, then requeue.` Missing ffmpeg uses its fixed adapter message. Cleanup warning fields are safe type names.

Did not accept `FAIL_DETAIL`: the offline contract model used the unchanged real `_LINE_BREAKS`/`scrub_line` and the real Console processor/store. LF and CRLF secret tails survived; U+2028 was redacted. A forward-slash source left `C:/Temp/av-kit/s67/review/[file]`; an escaped `PermissionError` filename left its directory too. Quoting alone does not fix or defeat an exact inner-path match, but separator/escape differences do. F1 requires stronger AC-142.13 cases and a formatter that preserves redaction context before line selection. The existing Session 65 contract is accepted; the defect is the new last-line caller.

## Q6 — Cancel and no conversion row

Accepted D-669. `cancel_processing` sets `_cancel` only (`download.py:367`); `_cancel_inflight` runs from the same worker between jobs. A download cancellation raised by the adapter still takes the existing Cancelled branch with no convert. A cancel during conversion leaves the row Downloading until Done, clears current-job identity, and stops the next worker iteration, so there is no intervening Cancelled → Done conflict. AC-142.16 tests this distinction. Direct use of `MediaPort.convert` adds no conversion-service call or row; AC-142.7 also checks SQLite.

## Q7 — Media port, constructors and source pins

Accepted D-664. The census found exactly the production wiring construction plus the eight test constructions in §Pins that move. The shared adapter is built before the download service. No signature-equality or call-order pin requiring another edit was found in the test sweep. The two AC-30.8 forbidden-source-string pins remain compatible with the proposed code.

There are also existing source readers at `tests/unit/test_domain.py:1559` (no redefined requeue status constant) and `tests/e2e/test_api_downloads.py:622` (no service-side `normalize_blocker_reason`). Neither constrains this change. The plan's row-1 census and existing full gate cover them without a source-pin update. `FakeMedia.convert` already raises; `StubMedia`'s scheduled addition is sufficient for its existing use.

## Q8 — Type-only row and meaningful Reds

Accepted rows 1–3. Row 1 supplies the required constructor/store/wiring and both new imported names (`AUDIO_EXTRACT`, `last_line`) with wrong behavior before Red. All other imported domain/port names already exist. `DECLARED_NEW` also includes inherited selftest-only names, which the script labels explicitly. Its 47 fixtures passed independently (14 positive, 33 negative, 0 wrong).

The required set is AC-142.1 and .4–.18; .2/.3 correctly remain passing type/wiring checks, and .19 is row 4's CI check. Required tests demand assertion-only failure blocks and reject import/fixture/setup failures. The guards let AC-142.17 assert the baseline `.m4a` result before probing an MP3 that does not yet exist; clip generation is valid offline setup with the present pinned pair. No impossible Red was identified. F1's stronger safety test needs the corresponding contract amendment before execution.

## Q9 — Real FFmpeg and CI

Accepted D-670. AC-142.17 explicitly requires the pinned pair and failure rather than skip; the runtime gate uses `-rfEs` and turns a reported `SKIPPED` into failure. `ci-collect.py` parses the actual Python Tests step and requires exactly one deselect, no collected module ids with it, and collected ids without it. I inspected this path; I did not run collection or pytest.

AC-142.18 uses the real resolver with no configured/bundled binary and `shutil.which` patched to None, so it needs neither installed ffmpeg nor the pinned pair on CI. Pair checks must remain runtime assertions/fixture checks, as the cited precedent does, so deselected-module collection needs no binary. The real reservation probe confirms the chosen encode command works locally.

## Q10 — Endings, identity, scope and records

Accepted the measured CRLF/LF inventory and byte-preserving write instructions, with LF for new files. The Files Modified/project inventories and gate allowed paths cover the work, including row 6's register/renders/grouping and closeout artifacts. `identity.py` binds code/tests/config, plan scripts, status/spec inputs, runtime/distribution identity and the pinned pair, excluding the named post-gate artifacts. Its scratch-repository selftest independently reported 0 failures. I did not run its whole-worktree hashing mode, which could read reviewer-visible private untracked files.

Row 6 takes pre-status copies, limits issue changes to the named issue's three fields, requires parsed-difference checks, and calls for entry-level status/grouping diffs and both renders. Queue, ruling, shapes and anchors blocks read their named actual sources; the unresolved D-671 properly prevents execution. The baseline version loop (`baseline.ps1:261–264`) does print success without checking the native `-version` exit: that preliminary claim should be corrected, but the mandatory real conversion and skip rejection still prevent a broken pair certifying delivery, so it is not an additional blocker. No demonstrated material scope/identity false-pass was found.

## Q11 — Offline and protected boundaries

Accepted the test design's fake YouTube/MediaPort collaborators, generated local clip, temporary SQLite/files, offline dependency sync and CI collection environment. These planned probes need no network or MCP server. The comparison report is only a hash input; no task requires reading its contents. No adapter/port/UI-format change, upload, installer build, picker fetch or live audit is scheduled.

D-671's A/B/D paths are executable as described: A records an open manual check, B presents the named public cookies-off download to Mat before it runs after the gate, and D records the ruling without that manual check. I did not choose an option. Cookie values are unnecessary in all three. F1 is the exception to accepting the no-raw-value Console claim; synthetic inputs already demonstrate the unsafe text path.

## Checklist Results

### Plan review

All manual observations below were performed by `codex-independent-reviewer` against the current working tree; exit code is null for manual checks.

| Check | Result | Procedure | Exit | Evidence |
|---|---|---|---|---|
| PR-1 Plan/task alignment | pass | Cross-read contracts, ACs and task rows 0–6/H1/H2 | null | Same MEU, sequencing, files and behavior; F1 is a shared contract defect. |
| PR-2 Not started | pass | Read current service, plan/task, MEU and target test inventory | null | No media/convert implementation; task unchecked; MEU-142 pending. |
| PR-3 Task deliverables and validation | pass | Read every task row and six script bodies | null | Concrete outputs, ownership, dependencies and commands present. |
| PR-4 Validation realism | fail | Evaluate AC-142.13 against literal planned formatter and real Console | null | Required safety result contradicts the formatter; F1. Other Reds/gates are executable. |
| PR-5 Source-backed planning | pass | Trace AC sources to 02/03, grouping and decisions | null | D-664–D-670 have local sources; D-671 remains explicitly pending. |
| PR-6 Correction/handoff readiness | pass | Inspect named handoff/review routes | null | One MEU, canonical target and bounded review loop; round-2 census not applicable. |
| PR-7 Scope discipline | pass | Compare exclusions to goal, residual section and supplied boundaries | null | No residual conversion rule silently deferred. |
| PR-8 Reachable observable behavior | fail | Trace production caller, transaction, card and Console consumers | null | Conversion/card chains exist; new error formatting computes unsafe Console output (F1). |
| PR-9 Named contracts | pass | Read single-statement mechanism table and row references | null | No unresolved competing behavior definition beyond F1's explicit contradiction. |

### Independent offline evidence

Commands ran from `P:/av-kit` through `rtk proxy`, with all-stream receipts and immediate exit capture. `PYTHONDONTWRITEBYTECODE=1` was set for importing probes/selftests; selftest TMP/TEMP were `C:/Temp/av-kit/s67/review`. The contract probe reports observations and exits 0 even when an observation demonstrates a safety failure.

```json
{"schema_version":"evidence.v1","check_id":"s67-review-contract-probe","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s67/review/probe.py","cwd":"P:/av-kit","scope":"Literal FAIL_DETAIL/LAST_LINE model, real existing Console store, pinned local convert","phase":"targeted","exit_code":0,"result":"fail","tested_state":"plan-review at 3435b7e516edd86a3d6ce3df497593907684012b; proposed formatter modeled, not implemented","output":"lf_secret_tail: detail=S67_SYNTHETIC_SECRET, secret_survived=true; crlf_secret_tail: secret_survived=true; u2028_secret: detail=[REDACTED], secret_survived=false. path_forward_slashes: Could not open C:/Temp/av-kit/s67/review/[file]. path_oserror_repr retains escaped directory. Closed xb reservation converted by the pinned real adapter: 26474 bytes, streams=[[audio,mp3]], source_kept=true."}
```

```json
{"schema_version":"evidence.v1","check_id":"s67-review-red-selftest","command":"rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-12-download-audio-extract/red-check.py --selftest","cwd":"P:/av-kit","scope":"Plan-local receipt parser fixtures only","phase":"targeted","exit_code":0,"result":"pass","tested_state":"plan-review at 3435b7e516edd86a3d6ce3df497593907684012b","output":"red-check selftest: 47 fixture(s) (14 positive, 33 negative), 0 wrong: []"}
```

```json
{"schema_version":"evidence.v1","check_id":"s67-review-identity-selftest","command":"rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-12-download-audio-extract/identity.py --selftest","cwd":"P:/av-kit","scope":"Scratch git fixture under C:/Temp/av-kit/s67/review; no worktree identity traversal","phase":"targeted","exit_code":0,"result":"pass","tested_state":"plan-review at 3435b7e516edd86a3d6ce3df497593907684012b","output":"Bound code/config/status/script and runtime mutations changed identity and refused historical evidence; named post-gate artifact edits left it unchanged. identity selftest: 0 failure(s)"}
```

```json
{"schema_version":"evidence.v1","check_id":"s67-review-construction-census","command":"rtk proxy rg -n 'DownloadService\\(' packages tests tools ui mcp-server","cwd":"P:/av-kit","scope":"Production/test/tool/UI/MCP construction sites","phase":"static","exit_code":0,"result":"pass","tested_state":"plan-review at 3435b7e516edd86a3d6ce3df497593907684012b","output":"Nine sites: packages/api/src/avkit_api/wiring.py:175; tests/unit/test_services.py:743,971,1514; tests/unit/test_extract_options.py:91; tests/unit/test_download_failure_visibility.py:273; tests/integration/test_download_received_quality.py:150; tests/e2e/real_stack.py:97; tests/e2e/test_api_error_surface.py:202. All scheduled."}
```

Persisted-log confirmation: `rtk proxy rg -n 'S67_SYNTHETIC_SECRET|source.m4a|source.mp3' C:/Temp/av-kit/s67/review/app/logs/console.log` exited 0. Its lines 2 and 3 both contain `error=Download failed: MP3 convert failed. detail=S67_SYNTHETIC_SECRET`. These are synthetic probe data, never real credentials.

Report validation: `rtk proxy .venv/Scripts/python.exe tools/validate_closeout_artifacts.py --review C:/Temp/av-kit/s67-plan-review-round-1.md --review-state-only --expected-review-mode plan --expected-target-plan docs/execution/plans/2026-11-12-download-audio-extract/implementation-plan.md --max-review-rounds 3 --output C:/Temp/av-kit/s67/review/review-state.json` exited 0: `OK: review_mode=plan; round 1 of 3; verdict=changes_required; open findings=1`. The verdict JSON also passed the repository's Draft 2020-12 schema using `jsonschema.Draft202012Validator`.

Product tests, collection, baseline and session gate: not run, as required for this read-only plan review. Given planning receipts were used as background evidence, never represented as new reviewer runs. Report/probe artifacts are under `C:/Temp/av-kit`; the coordinator owns canonical copying and ledger recording.

## Verdict

`changes_required` — one evidence-backed High behavioral finding. The MP3 conversion design and coverage otherwise address the registered goal, but the new failure-detail contract would expose supported sensitive error inputs to users' Console and persisted logs. Correct F1 in the plan and AC-142.13 before execution. D-671 remains open for Mat at the execution gate; it is not a finding.

Residual limits: implementation and product suites have not run, and no live download was performed. The preliminary baseline version-exit observation does not defeat the final required real-FFmpeg behavior gate. No handoff/template/style finding is raised.

## Corrections Applied — 2026-11-12

Written by the coordinator (Claude Code), not the reviewer. Every edit is an exact, counted byte replacement in `C:/Temp/av-kit/s67/fix-f1.py`, which holds each old and new string; the files kept their LF endings (0 CRLF before and after). No production code or test was written.

| Finding | Correction |
|---|---|
| F1 | `FAIL_DETAIL` (implementation-plan.md:114) now uses a private `_convert_detail`. It masks every form of each path: the full path with any run of `\` or `/` between its parts, in any case on Windows, becomes `[file]`; the parent folder becomes `[folder]`; the file name becomes `[file]`. It returns the scrubbed last line only when that line is a suffix of `scrub_line` over the whole masked text, and `[REDACTED]` otherwise. The same rule is in §Where values go (:132), the function chain (:137), D-668's chosen, precedents and reasoning (:360 on) and §Planning receipts (:450). AC-142.13 (:182) now has twelve parametrize ids: ten leak cases (LF, CR and CR LF secret tails, a needle split across an LF, a home folder split across an LF, forward-slash, mixed-separator, escaped `str(PermissionError)`, folder-only and upper-case paths) and two keep cases that fail if the detail falls back to `[REDACTED]`. Each case asserts the Console row, captured stdout and the persisted `console.log`, and the card text: `write_failed`'s for the `PermissionError`, `MP3 convert failed` otherwise. task.md rows 2 (:61) and 3 (:62) say the same. Evidence: `C:/Temp/av-kit/s67/fmt-probe.py` models the rule over the unchanged Session 65 helpers and the real `HealthService` store; `C:/Temp/av-kit/s67/fmt-probe.txt` reports 18 cases, 0 failures and no leak in the persisted log. |
| Q10 note | baseline.ps1:261-267 now takes each pinned binary's `-version` output into a variable, reads its exit code before trimming to the first line, and exits 1 on a nonzero exit (`C:/Temp/av-kit/s67/version-exit-probe.txt`: both exit 0). |

Rechecked after the edits: `C:/Temp/av-kit/s67-plan-task-lint.txt` (`OK: 25 row(s)`), `C:/Temp/av-kit/s67-plan-red-check-selftest.txt` (47 fixtures, 0 wrong) and a PowerShell parse of baseline.ps1 (0 errors).

## Recheck (Round 2)

**Date:** 2026-11-12. **Agent:** codex-independent-reviewer (Codex; independent of Claude Code/Anthropic). **Verdict:** approved. **Intent achieved:** yes, assessed as a plan. The round 1 prose and its verdict above are retained as history; this recheck and the frontmatter state the current verdict.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| F1 | fixed | fixed |

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| None | — | no | — | None. | — | — | fixed |

### R1 — FAIL_DETAIL

F1 is fixed at `implementation-plan.md:114–115`. By construction the returned detail is either a suffix of `scrub_line(masked)` or the fixed `[REDACTED]`. Line selection cannot disclose characters removed by that whole-text scrub. This comparison is to the **masked** whole text, as the rule states; it is not a general proof that arbitrary preprocessing preserves every possible redaction cue. The LF/CR/CRLF tails, LF-split needle and home, needle within the tail, mixed/slash/upper-case paths, escaped OSError, and folder plus another filename all pass. Both ordinary FFmpeg cases retain their expected diagnostic text.

Quotes do not interfere with matching. Given UNC paths and extended-prefix drive/UNC forms lose their identifying path components; only a prefix such as `\\?\` may remain. A supplied relative or 8.3 path is masked in its supplied spelling. A **different alias** of an absolute path is not resolved: a manufactured relative alias retains directory fragments and an 8.3 alias retains its alias spelling. The concrete rule defines separator/case variants, not filesystem alias discovery; the unchanged adapter passes `str(input_path)`/`str(output_path)` to FFmpeg (`media/adapter.py:436–449`). No new producer of those different aliases was demonstrated, so this is a stated limit, not a new delivery defect.

For a drive-root parent the model's folder pattern reduces to the drive token and can replace unrelated occurrences of `C:`. This is harmless over-redaction of Console detail. A tabbed tail following an earlier link also falls back to `[REDACTED]`. These losses are acceptable for diagnostic detail: `CONVERT_FAIL` keeps the independently fixed card text, and the two keep cases prohibit blanket loss of ordinary diagnostics.

### R2 — AC-142.13 and Red

`implementation-plan.md:182` now covers the demonstrated F1 failures and preserves useful diagnostics. **Ten** leak cases fail the round 1 formatter; the two keep cases already pass it and reject an always-`[REDACTED]` formatter. Twelve cases need not all distinguish round 1. The assertions are feasible: `HealthService._process` appends the Console row, prints stdout, and persists ERROR events regardless of `app.log_to_file` (`health.py:204–244`). A fresh app directory, the positive control and sequence filtering isolate the failure row. The independent probe additionally exercised real structlog dispatch and asserted all three surfaces. This is formatter/Console evidence, not execution of the unimplemented service change.

`escaped_oserror` must have the fake convert raise the actual `PermissionError`, whose `str()` supplies the escaped filename. It is an `OSError`, so `CONVERT_FAIL` selects the existing `write_failed` card. Wrapping its text in `FilesystemError` would instead select the other fixed card and would not implement that AC. Rows 1–3 remain viable: without a conversion step the baseline job ends Done and emits no expected `download.failed`, so AC-142.13 fails an assertion before row 3. `_convert_detail` is private and called through the service; the test need not import or patch it. Neither row 1 nor `DECLARED_NEW` needs another name.

### R3 — Native version exit

`baseline.ps1:261–269` captures the native output completely, saves `$LASTEXITCODE` immediately, and only then selects its first line. Successful binaries still print `{name} {size} B: {version banner}`, followed by `baseline step ffmpeg-pair exit=0`. An extracted copy of this block passed with both real pinned binaries. A scratch negative changed only the native argument to an invalid option: the native exit was `-1414549496`, the copied block exited 1 and never printed the success marker. The complete baseline was not run.

### R4 — Correction consistency

The eight implementation-plan replacements and two task replacements from `fix-f1.py` are present once each, with no stale old clauses outside their replacement. D-668's YAML (`implementation-plan.md:360–376`), `FAIL_DETAIL`, `CONVERT_FAIL`, the value flow and private call chain agree. Task rows 2/3 (`task.md:61–62`) retain Red then Green and immutable tests; the baseline edit leaves its success output usable by its neighbours. The FIC table still has exactly AC-142.1 through AC-142.19. No corrected clause breaks a round 1 accepted behavior or changes its scope.

### Recheck evidence

All Python runs used `PYTHONDONTWRITEBYTECODE=1` and `RECEIPTS_DIR=C:/Temp/av-kit`; every generated app/log/script is under `C:/Temp/av-kit/s67/review`. Commands ran from `P:/av-kit`, with all streams redirected and native exit captured before receipt reads. No product tests, collection, baseline, session gate, package manager, backend, MCP server or network operation ran. No repository file was edited. The initial scratch census assertion mistakenly counted an old literal intentionally embedded in its replacement; the scratch assertion was corrected and the final probe reran successfully.

```json
{"schema_version":"evidence.v1","check_id":"s67-r2-formatter","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s67/review/recheck-round2.py","cwd":"P:/av-kit","scope":"Corrected FAIL_DETAIL model over unchanged helpers, real Console/stdout/log, old/new cases, path variants and correction census","phase":"targeted","exit_code":0,"result":"pass","tested_state":"Session 67 corrected working-tree plan at supplied HEAD 3435b7e; formatter modeled, product conversion unimplemented","output":"fmt-probe: 18 case(s), 0 failure(s); persisted_lines=18, persisted_leaks=[]; ten old leak cases differ and two ordinary keep cases remain exact; real-dispatch: Console row + captured stdout + persisted console.log asserted; replacement census: plan 8, task 2; AC census: exactly AC-142.1 through AC-142.19. Different 8.3/relative aliases remain a stated model limit, not an asserted pass."}
```

```json
{"schema_version":"evidence.v1","check_id":"s67-r2-red-selftest","command":"rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-12-download-audio-extract/red-check.py --selftest","cwd":"P:/av-kit","scope":"Plan-local receipt parser fixtures only","phase":"targeted","exit_code":0,"result":"pass","tested_state":"Session 67 corrected plan, round 2","output":"red-check selftest: 47 fixture(s) (14 positive, 33 negative), 0 wrong: []"}
```

```json
{"schema_version":"evidence.v1","check_id":"s67-r2-version-positive","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s67/review/version-positive.ps1","cwd":"P:/av-kit","scope":"Only the extracted pinned-binary block; no baseline invocation","phase":"targeted","exit_code":0,"result":"pass","tested_state":"Current baseline.ps1 pinned-binary block and pinned packaging/ffmpeg-win64 pair","output":"ffmpeg.exe 165577728 B: ffmpeg version n8.1.3-27-g8dca1586f4-20261031; ffprobe.exe 165371904 B: ffprobe version n8.1.3-27-g8dca1586f4-20261031; baseline step ffmpeg-pair exit=0"}
```

```json
{"schema_version":"evidence.v1","check_id":"s67-r2-version-negative","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s67/review/version-negative.ps1","cwd":"P:/av-kit","scope":"Extracted block, only native -version argument mutated to an invalid option in scratch","phase":"targeted","exit_code":1,"result":"pass","tested_state":"Scratch negative of current pinned-binary block","output":"Unrecognized option 's67_invalid_version_probe'. Error splitting the argument list: Option not found. baseline step ffmpeg-pair exit=1 (ffmpeg.exe -version exit=-1414549496; S4). Expected rejection observed; no success marker."}
```

### Current checklist and verdict

| Check | Result | Procedure or command | Exit | Evidence |
|---|---|---|---|---|
| R1 corrected safety and diagnostic retention | pass | `recheck-round2.py` | 0 | 18 original model cases pass; real logger dispatch asserts all three outputs; aliases and root overmask are stated above. |
| R2 coverage, card and Red feasibility | pass | codex-independent-reviewer cross-read AC-142.13, rows 1–3, DECLARED_NEW and the real HealthService/failure tests | null | Ten leak cases distinguish round 1, two keep cases reject blanket redaction; PermissionError uses write_failed; no private helper import required. |
| R3 native exit and output | pass | `version-positive.ps1`; `version-negative.ps1` | 0 / 1 | Preserved success banners; expected native failure rejected before success marker. |
| R4 correction blast radius | pass | `recheck-round2.py` and manual neighbour/D-668/task comparison by codex-independent-reviewer | 0 / null | Eight plan clauses and two task clauses verified; 19 ACs unchanged. |
| Product implementation validation | n/a | Not run in this read-only plan recheck | null | Implementation remains future work; this approval assesses the plan. |

`approved` — F1 is fixed, the Q10 note is addressed, and there are no new High/Critical or other actionable findings. Executing this corrected plan would deliver the registered MP3 conversion intent. D-671 and explicit execution authorization remain Mat's existing gate; approval does not rule that question or start implementation. The coordinator owns canonical copying and ledger recording. Residual limits: no implementation/product suite or live download has run; path alias discovery is not established by the defined textual mask.
