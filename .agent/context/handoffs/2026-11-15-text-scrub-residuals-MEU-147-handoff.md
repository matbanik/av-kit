---
date: "2026-11-15"
project: "2026-11-15-text-scrub-residuals"
meu: "MEU-147"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-15-text-scrub-residuals/implementation-plan.md"
build_plan_section: "bp03"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "none (first MEU of Session 77)"
---

# Handoff: 2026-11-15-text-scrub-residuals-MEU-147-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-147 `svc-transcript-title-cleaning` (issue `TRANSCRIPT-UNCLEANED-TITLE-FALLBACKS`, triage D-804). A transcript channel named from its extract title, and a transcript title taken from the caption port, now go through D-360's cleaner, so a lone surrogate or a control character no longer fails job creation or the raw write. A value that cleans to nothing takes the playlist or video ID.
**Build Plan Section**: [03 §Transcript title cleaning (residual)](../../../docs/build-plan/03-service-layer.md#transcript-title-cleaning-residual) (matrix 3.22), with the Delivered (Session 77) note under it (`03-service-layer.md:757`).
**Successor**: MEU-148 (same session; `2026-11-15-text-scrub-residuals-MEU-148-handoff.md`).

- **TEXT_CLEAN_SHARED (D-922).** D-360's `_clean_text` moved unchanged into the domain as `clean_text` (`packages/core/src/avkit_core/domain/download.py:321`), with `_UNCLEAN_CATEGORIES` (`:318`) directly above `_require_text_clean` (`:338`), which is not changed. The YouTube adapter imports it (`packages/infrastructure/src/avkit_infra/youtube/adapter.py:28`) and keeps no copy: `_clean_text`, `_UNCLEAN_CATEGORIES` and `import unicodedata` are gone, and its three call sites (`:224`, `:718` twice, `:722`) call `clean_text`. AC-147.1 checks that the adapter's `clean_text` is the domain's object.
- **CHANNEL_FALLBACK_CLEAN (D-923).** `add_channel` names the job `listing.channel_name or clean_text(info.title) or channel_id` (`packages/core/src/avkit_core/services/transcript.py:173`), where `channel_id` is the playlist ID or the video ID. The output folder still uses `slugify(info.title)` (`SLUG_SOURCE`, AC-122.11); the comment now says the name is cleaned.
- **RESULT_TITLE_CLEAN.** A fetch keeps `current.title or clean_text(result.title) or result.video_id` (`transcript.py:639`), and that one value goes to the raw Markdown and the stored item. The listed title still wins (`TITLE_KEPT`, AC-122.13).
- **CLEAN_AT_ENTRY (D-924).** `TranscriptJob`, `TranscriptItem` and `TranscriptResult` gain no refusal guard. The service cleans at its two entry points, so the values it builds pass `_require_text_clean`.
- **Spec text and records (row 5).** The Delivered (Session 77) note in 03; the issue resolved through the plan's `issue-resolve.py` (`tsr-issue-resolve.txt`: `issue-resolve: 0 problem(s)`); MEU-147 `ready_for_review` (`tsr-status-147.txt`).

**Residual risk for triage (plan §Out of Scope).** A lone surrogate in a transcript's text (`result.text`) fails the same raw write. Neither issue names it, so this MEU leaves it; it is named here for the next triage.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-11-15-text-scrub-residuals/implementation-plan.md) §MEU-147. **Execution authorization:** `USER_EXPLICIT`, 2026-11-15, "proceed with planning and execution for P:\av-kit\.agent\context\grouping\2026-11-15-post-rc3-triage-residuals-session-grouping.md like we did here. But use the new HDP process. Continue orchestrating the sessions." The plan review approved at round 2 ([plan-critical-review.md](2026-11-15-text-scrub-residuals-plan-critical-review.md)); `plan_to_exec_gate: human`. The coordinator wrote these words into the plan's Status line (line 15) before row 0; that is a plan-text edit made after the plan was approved, disclosed here.

**Receipts.** A receipt named by its file name alone is in the session's receipts folder (`RECEIPTS_DIR`, the plan's `text-scrub-residuals` folder under it). Full paths appear only in the evidence records' `command` fields.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-147.1 | unit | `clean_text` exists in `avkit_core.domain.download`. Parametrized: a lone surrogate and a control character inside text are dropped; tabs, newlines and space runs collapse to one space and the ends are trimmed; U+200B (category `Cf`) is kept, as D-360 keeps it; text that holds only surrogates, controls or whitespace, `""`, `None` and `7` give `None`. Every non-`None` output passes `_require_text_clean`. The YouTube adapter module has no `_clean_text` or `_UNCLEAN_CATEGORIES`, and its `clean_text` is the domain's object. | Local Canon (D-360, MEU-122; D-922) | `tests/unit/test_transcript_title_cleaning.py:81`, `:91` | ✅ |
| AC-147.2 | unit | With no listed channel name, an extract title `Chan <U+D800> <U+0007>Name` gives a job whose `channel_name` is `Chan Name`, read back from the unit of work, and it passes `_require_text_clean`. The output folder name equals `slugify` of the raw extract title (`SLUG_SOURCE` unchanged). After a fetch, the raw Markdown's `channel:` front matter is `Chan Name`. The same holds for the `VideoInfo` branch. | Local Canon (03 §Transcript title cleaning: Clean; D-360) | `tests/unit/test_transcript_title_cleaning.py:100`, `:119` | ✅ |
| AC-147.3 | unit | An extract title that cleans to nothing (`<U+D800><U+0001>`) with no listed channel name gives `channel_name` equal to the playlist ID, and the video ID for the `VideoInfo` branch. The job is created. | Local Canon (03 §Transcript title cleaning: Fallback; D-923) | `tests/unit/test_transcript_title_cleaning.py:139`, `:152` | ✅ |
| AC-147.4 | unit | An item with no listed title, fetched with a port title `Talk <U+D800> <U+0007>title`, ends `Done` with the stored title `Talk title`; its raw Markdown decodes as UTF-8 and its front matter title is `Talk title`. A port title that cleans to nothing stores the video ID, in the file and in the item. | Local Canon (03 §Transcript title cleaning: Clean, Fallback; MEU-122's ID fallback) | `tests/unit/test_transcript_title_cleaning.py:166` | ✅ |
| AC-147.5 | integration | Real storage (SQLite under `tmp_path`, `SqlAlchemyUnitOfWork`, `FilesystemAdapter`, a fake extract and caption port): an extract title and a port title that each hold a lone surrogate and a control character; `add_channel` raises nothing, the job ends `Done`, the raw file decodes as UTF-8, and the job and item read back through a new unit of work hold the cleaned values. | Local Canon (issue `resolution_path`; Session 53 RULE-1) | `tests/unit/test_transcript_title_cleaning.py:188` | ✅ |
| AC-147.6 | integration | The MEU-122 tests pass unchanged: `tests/unit/test_transcript_metadata.py` and `pytest tests/integration/test_youtube_adapter.py -k ac_122`. | Local Canon (AC-122.2, AC-122.3, AC-122.8, AC-122.10, AC-122.11, AC-122.13) | `tests/unit/test_transcript_metadata.py` (`tsr-147-green.txt`); `tests/integration/test_youtube_adapter.py:812`, `:852`, `:881`, `:949`, `:973`, `:987` (`tsr-147-adapter.txt`) | ✅ |
| AC-122 (cross-ref) | guard | The MEU-122 regression: the adapter's cleaning (AC-122.2, AC-122.3, AC-122.8), the slug source (AC-122.11) and the listed title (AC-122.13) are unchanged, with no test edited; it is AC-147.6 | MEU-122 | `tests/integration/test_youtube_adapter.py:812`, `:852`, `:881`; `tests/unit/test_transcript_metadata.py` | ✅ |
| AC-148 (sibling) | sibling MEU | AC-148.1, AC-148.2, AC-148.3, AC-148.4, AC-148.5, AC-148.6, AC-148.7, AC-148.8, AC-148.9: the home folder's short form, evidenced in the MEU-148 handoff, which also carries the AC-119 (AC-119.10) cross-reference | MEU-148 | `2026-11-15-text-scrub-residuals-MEU-148-handoff.md` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-147.1 | `AssertionError: assert False` / `where False = hasattr(download_domain, 'clean_text')` (`tsr-147-red.txt`; 12 parametrized cases and the adapter case) | Row 2: pass (`tsr-147-green.txt`) | `test_transcript_title_cleaning.py:81`, `:91` |
| AC-147.2 | the same assertion, for the playlist and the video branch | Row 2: pass | `test_transcript_title_cleaning.py:100`, `:119` |
| AC-147.3 | the same assertion, for the playlist ID and the video ID | Row 2: pass | `test_transcript_title_cleaning.py:139`, `:152` |
| AC-147.4 | the same assertion | Row 2: pass | `test_transcript_title_cleaning.py:166` |
| AC-147.5 | the same assertion | Row 2: pass | `test_transcript_title_cleaning.py:188` |

- **Row 1 Red** (`tsr-147-red.txt`): `19 failed in 0.24s`; each case fails at its first line, `hasattr(download_domain, 'clean_text')`, so Red is by assertion and never by `AttributeError` in setup (Session 52 RULE-4). `tsr-147-red-check.txt`: `red-check: 1 receipt(s), 5 required test(s), 0 problem(s)`.
- **Not in FAIL_TO_PASS:** AC-147.6 runs existing tests unchanged; it is a regression check, not a Red case.
- **Row 2's first Green attempt** (`tsr-147-green-attempt1.txt`): `2 failed, 33 passed in 1.15s`. AC-147.4 and AC-147.5 failed with an `IndexError` in the test's own `_front` helper (`test_transcript_title_cleaning.py:50-57`), which split the raw Markdown on `\n` only; on Windows the file is read back with CRLF. The helper now normalises CRLF first (`:52`); no assertion and no product line changed. The kept Green is `tsr-147-green.txt`: `35 passed in 17.93s`.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsr-0-baseline", "command": "pwsh -NoProfile -File C:/Temp/av-kit/text-scrub-residuals/run-row0.ps1 (task.md row 0's Validation cell: rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-15-text-scrub-residuals/baseline.ps1 *> C:/Temp/av-kit/text-scrub-residuals/tsr-baseline.txt, with ELECTRON_RUN_AS_NODE unset); receipts tsr-baseline.txt, tsr-base-py.txt", "scope": "Row 0: baseline.sha, baseline-dirty.txt, baseline-scope.json, baseline-dirty-hashes.json and baseline-eol.json; the row-0 copies of red-check.py, identity.py and issue-resolve.py; the base Python suite; the red-check and identity selftests; the S4 scope check for row 1 and the line-ending check", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD ab761dd (baseline.sha), before row 1", "output": "tsr-baseline.txt: baseline-dirty.txt 51 paths; baseline-scope.json 14 paths; 2 absent; baseline-dirty-hashes.json 6 paths outside this scope; red-check selftest: 37 fixture(s) (12 positive, 25 negative), 0 wrong: []; identity selftest: 0 failure(s); scope-check: ok; baseline: all steps exit 0. tsr-base-py.txt: 2945 passed, 37 warnings in 297.28s (0:04:57)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsr-1-red-147", "command": "pwsh -NoProfile -File C:/Temp/av-kit/text-scrub-residuals/run-row1.ps1 (task.md row 1's Validation cell: uv run pytest tests/unit/test_transcript_title_cleaning.py --tb=short -q *> C:/Temp/av-kit/text-scrub-residuals/tsr-147-red.txt, its exit code to tsr-147-red.txt.exit, then red-check.py --require test_ac_147_1 to test_ac_147_5); receipts tsr-147-red.txt, tsr-147-red-check.txt, tsr-s4-row1.txt", "scope": "MEU-147 Red: AC-147.1 to AC-147.5 against the row-0 product code, after the S4 check", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD ab761dd plus rows 0 and 1", "output": "tsr-s4-row1.txt: scope-check: ok. tsr-147-red.txt: 19 failed in 0.24s, each AssertionError: assert False where False = hasattr(download_domain, 'clean_text'); tsr-147-red.txt.exit 1. tsr-147-red-check.txt: red-check: 1 receipt(s), 5 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsr-2-green-147", "command": "pwsh -NoProfile -File C:/Temp/av-kit/text-scrub-residuals/run-row2.ps1 (task.md row 2's Validation cell: uv run pytest tests/unit/test_transcript_title_cleaning.py tests/unit/test_transcript_metadata.py, then uv run pytest tests/integration/test_youtube_adapter.py -k ac_122, then the line-ending check of the four MEU-147 files); receipts tsr-147-green.txt, tsr-147-adapter.txt, tsr-147-eol.txt, tsr-s4-row2.txt", "scope": "MEU-147 Green: TEXT_CLEAN_SHARED, CHANNEL_FALLBACK_CLEAN, RESULT_TITLE_CLEAN and CLEAN_AT_ENTRY, with the MEU-122 tests unchanged", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD ab761dd plus rows 0 to 2", "output": "tsr-s4-row2.txt: scope-check: ok. tsr-147-green.txt: 35 passed in 17.93s; tsr-147-adapter.txt: 6 passed, 31 deselected in 1.28s; tsr-147-eol.txt: line-ending drift: []. The first attempt, tsr-147-green-attempt1.txt: 2 failed, 33 passed in 1.15s (the _front helper's CRLF IndexError, fixed in the helper only)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsr-5-close", "command": "pwsh -NoProfile -File C:/Temp/av-kit/text-scrub-residuals/run-row5.ps1 (task.md row 5's Validation cell: issue-resolve.py --issue TRANSCRIPT-UNCLEANED-TITLE-FALLBACKS --issue CONSOLE-HOME-SCRUB-SHORT-FORM --set-file C:/Temp/av-kit/text-scrub-residuals/issue-resolve-set.json --expect-sha256 <row-0 hash>, issue_triage.py render and render --check, meu_status.py update MEU-147 and MEU-148 ready_for_review, meu_status.py render, then the row-5 check); receipts tsr-issue-resolve.txt, tsr-issues-render.txt, tsr-issues-render-check.txt, tsr-status-147.txt, tsr-status-148.txt, tsr-status-render.txt, tsr-row5-check.txt, tsr-s4-row5.txt", "scope": "Row 5: the two Delivered (Session 77) notes in 03 (CRLF), both issues resolved, both MEUs ready_for_review, grouping row 77 executed", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD ab761dd plus rows 0 to 5", "output": "tsr-issue-resolve.txt: issue-resolve: 0 problem(s); tsr-issues-render.txt: Rendered known-issues.md: 60 lines; tsr-issues-render-check.txt: OK: known-issues.md is up-to-date; tsr-status-147.txt: Updated MEU-147 to ready_for_review (updated: 2026-11-15); tsr-status-render.txt: Loaded 153 MEUs across 12 phases; tsr-row5-check.txt: row 77 executed (Session 77), grouping LF: True 03 CRLF: True notes: 2"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsr-h1-1-unchecked", "command": "pwsh -NoProfile -File C:/Temp/av-kit/text-scrub-residuals/run-h1-1.ps1 (task.md H1-1's Validation cell) *> C:/Temp/av-kit/text-scrub-residuals/task-unchecked.txt", "scope": "H1-1: no implementation row of task.md is unchecked", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD ab761dd plus rows 0 to 5", "output": "task-unchecked.txt: unchecked implementation rows: []"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsr-gate-h1-2", "command": "pwsh -NoProfile -File C:/Temp/av-kit/text-scrub-residuals/run-h1-2.ps1 (task.md H1-2's Validation cell: rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-15-text-scrub-residuals/session-gate.ps1 *> C:/Temp/av-kit/text-scrub-residuals/tsr-gate-h1.txt, with ELECTRON_RUN_AS_NODE unset); receipts tsr-gate-h1.txt and the tsr-D6-*.txt step receipts", "scope": "H1-2 session gate for MEU-147 and MEU-148: identity before and after, ruff check and format, pyright, the task contract, scope paths, line endings, the red-check selftest, the MEU-147 tests and the MEU-122 adapter tests, the MEU-148 tests with no skip, AC-119.10, the empty-lookup mutant and its red-check, the scrub callers, the full Python suite, the state and issue renders and the UI canon", "phase": "full", "fresh": true, "snapshot": false, "exit_code": 0, "result": "pass", "tested_state": "ab761ddd5cc47cb014e80450be1e80c0825c984f+e7c60e3a25531c47ba7e950292591af393053446561e32e97d1731d07e2e0e4d", "output": "tsr-gate-h1.txt: session-gate: all steps exit 0; tested_state before = after (tsr-D6-identity-before.txt, tsr-D6-identity-after.txt). py-lint All checks passed!; py-format 7 files already formatted; py-types 0 errors, 0 warnings, 0 informations; task-contract OK: 23 row(s), 21 fully checked, 2 view_file exempt (H1-5, H2-1); scope-paths scope-check: ok (other-session-plan 39, plan-or-closeout 15, baseline-dirty-hashes checked 6); line-endings scope-check: ok; red-check-selftest 37 fixture(s) (12 positive, 25 negative), 0 wrong; meu-147-tests 35 passed in 2.64s; meu-147-adapter 6 passed, 31 deselected in 0.82s; meu-148-tests 18 passed in 1.12s; meu-148-ac119 10 passed, 108 deselected in 0.37s; meu-148-mutant must fail: pytest exit=1, 2 failed, 16 deselected in 0.07s; meu-148-mutant-check red-check: 1 receipt(s), 1 required test(s), 0 problem(s); scrub-callers 100 passed in 3.08s; py-tests (tsr-D6-py-tests.txt) 2982 passed, 37 warnings in 527.72s (0:08:47), the row-0 base 2945 plus 19 MEU-147 and 18 MEU-148 tests; state-render Drift check passed (153 MEUs, 12 phases); issues-render-check OK: known-issues.md is up-to-date; ui-canon Test Files 2 passed (2), Tests 14 passed (14). Attempt 1 (tsr-gate-h1-attempt1.txt) stopped at meu-148-mutant-check: no readable child exit code in tsr-D6-meu-148-mutant.txt.exit, a gate-script defect fixed in session-gate.ps1's MustFail block before the rerun"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsr-h1-3-status", "command": "pwsh -NoProfile -File C:/Temp/av-kit/text-scrub-residuals/run-h1-3.ps1 (task.md H1-3's Validation cell: meu_status.py render --check, meu_status.py get MEU-147 and MEU-148, then the ready_for_review check); receipts tsr-render-check.txt, tsr-h13-status-147.txt, tsr-h13-status-148.txt, tsr-h13-check.txt", "scope": "H1-3: row 5's status writes hold, with no new write after the gate; the current-focus paragraph", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "the gate's tested_state (current-focus.md is an identity artifact)", "output": "tsr-render-check.txt: Drift check passed (153 MEUs, 12 phases); tsr-h13-status-147.txt and tsr-h13-status-148.txt: status ready_for_review; tsr-h13-check.txt: MEU-147 and MEU-148 ready_for_review: True. The Session 77 paragraph heads current-focus.md, which stays CRLF (179 CRLF, 0 bare LF)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsr-h1-4-openapi", "command": "pwsh -NoProfile -File C:/Temp/av-kit/text-scrub-residuals/run-h1-4.ps1 (task.md H1-4's Validation cell) *> C:/Temp/av-kit/text-scrub-residuals/openapi-check.txt", "scope": "H1-4: packages/api has no change since baseline.sha, so the OpenAPI check is skipped on that basis", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "the gate's tested_state", "output": "openapi-check.txt: packages/api changes: []"}
```

### Quality Gate Results

- **Last line** (`tsr-gate-h1.txt`): `session-gate: all steps exit 0`.
- **Identity:** tested_state `ab761ddd5cc47cb014e80450be1e80c0825c984f+e7c60e3a25531c47ba7e950292591af393053446561e32e97d1731d07e2e0e4d` before and after the gate (`tsr-D6-identity-before.txt`, `tsr-D6-identity-after.txt`).
- **Static:** ruff check `All checks passed!`; ruff format `7 files already formatted`; pyright `0 errors, 0 warnings, 0 informations`; the task contract `OK: 23 row(s); 21 fully checked; 2 view_file exempt (H1-5, H2-1)`; scope paths and line endings `scope-check: ok`; the red-check selftest `37 fixture(s) (12 positive, 25 negative), 0 wrong`.
- **Suites:** MEU-147 `35 passed`; the MEU-122 adapter tests `6 passed, 31 deselected`; MEU-148 `18 passed` with no skip; AC-119.10 `10 passed, 108 deselected`; the empty-lookup mutant fails as it must (`2 failed, 16 deselected`, exit 1) and its red-check reports `0 problem(s)`; the scrub callers `100 passed` (84 callers and 16 metadata); the full Python suite `2982 passed, 37 warnings in 527.72s` (`tsr-D6-py-tests.txt`), which is the row-0 base of 2945 plus the 19 MEU-147 and 18 MEU-148 tests; the state render `Drift check passed`; the issue render `OK: known-issues.md is up-to-date`; the UI canon `Tests 14 passed (14)`.
- **Skipped, with basis:** ui-lint, ui-types and ui-tests (nothing under `ui/` changes); the MCP steps (no MCP change); E2E (no renderer change); OpenAPI (no `packages/api` change, H1-4 `openapi-check.txt`); build-record (no build).
- **Baseline failures excused:** 0.
- **First attempt:** `tsr-gate-h1-attempt1.txt` stopped at `meu-148-mutant-check` (`no readable child exit code in tsr-D6-meu-148-mutant.txt.exit`). The mutant itself had failed as required; the gate's MustFail block wrote no `.exit` file. That is a defect in the plan-local `session-gate.ps1`, not a flake, and the block now writes it (`Set-Content "$receipt.exit" $code`). The attempt's receipts are kept as `*-attempt1.txt`; the rerun above passed every step.
- **After the gate:** H1-3 added the current-focus paragraph, task.md rows were marked, and these handoffs were written. `identity.py` excludes all three, so no product, test or tracked record changed after the gate; H1-6b checks that the expected state still equals the gate's.

---

## Changed Files

All counts are `git diff ab761dd --numstat`; line endings were measured as bytes before and after (`tsr-eol-final.txt`: `line-ending drift: []` over 20 files).

| File | Change | Added / removed | Line endings |
|------|--------|-----------------|--------------|
| `packages/core/src/avkit_core/domain/download.py` | MEU-147: `_UNCLEAN_CATEGORIES` and `clean_text` (D-922) | +20 / -0 | CRLF kept |
| `packages/infrastructure/src/avkit_infra/youtube/adapter.py` | MEU-147: imports `clean_text`; the copy, its categories and `import unicodedata` removed; two D-930 layout hunks | +6 / -29 | CRLF kept |
| `packages/core/src/avkit_core/services/transcript.py` | MEU-147: the channel and result-title fallbacks (D-923) | +7 / -6 | LF kept |
| `packages/core/src/avkit_core/services/health.py` | MEU-148: `short_path_name`, `home_forms` and its cache and lock, the short form in `scrub_home` (D-926, D-927, D-337) | +87 / -10 | CRLF kept |
| `packages/core/src/avkit_core/services/download.py` | MEU-148: `_scrub_split_home` loops over `home_forms` (D-925); four D-930 layout hunks | +16 / -21 | CRLF kept |
| `tests/unit/test_transcript_title_cleaning.py` | new: AC-147.1 to AC-147.5 | +250 (new) | LF |
| `tests/unit/test_console_home_short_form.py` | new: AC-148.1 to AC-148.9 | +291 (new) | LF |
| `docs/build-plan/03-service-layer.md` | the two Delivered (Session 77) notes (`:757`, `:777`) | +14 / -0 | CRLF kept |
| `docs/BUILD_PLAN.md` | the rendered MEU status | +1 / -1 | LF kept |
| `.agent/context/meu-status.yaml` | MEU-147 and MEU-148 `ready_for_review` (through `tools/meu_status.py`) | +8 / -8 | LF kept |
| `.agent/context/meu-registry.md` | the rendered registry | +2 / -2 | LF kept |
| `.agent/context/known-issues.yaml` | both issues resolved (through the plan's `issue-resolve.py`) | +10 / -5 | LF kept |
| `.agent/context/known-issues.md` | the rendered issue list (`tools/issue_triage.py render`) | +3 / -5 | LF kept |
| `.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md` | row 77 `executed` | +1 / -1 | LF kept |
| `.agent/context/current-focus.md` | the Session 77 paragraph (H1-3) | +3 / -0 | CRLF kept |

Plan-local files (in the plan folder): `mutant_empty_lookup.py` (16 lines, the AC-148.6 mutant plugin), `scope-check.py` (D-929), the row-0 records (`baseline.sha`, `baseline-dirty.txt`, `baseline-scope.json`, `baseline-dirty-hashes.json`, `baseline-eol.json`) and the row-0 copies of `red-check.py`, `identity.py` and `issue-resolve.py`; `session-gate.ps1` gained the MustFail `.exit` line. These two handoffs are new. Nothing is committed or staged.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Blocking | Finding | Fix | Status |
|---|----------|----------|---------|-----|--------|

Round 1 (dispatch `tsr-exec-r1`) approved with no finding: `findings_count: 0`, intent achieved `yes`, and the ledger recorded `blocking=0`. The reviewer's tested_state is `ab761ddd5cc47cb014e80450be1e80c0825c984f+e7c60e3a25531c47ba7e950292591af393053446561e32e97d1731d07e2e0e4d`, the gate's exactly; it reproduced the host's ignore of `.claude/settings.local.json` with a temp-only exclude file and never opened that file. It accepted D-922 to D-927 as fixed, and D-928 to D-930 against their code and receipts (for D-930, a whole-module AST comparison shows the six extra hunks are layout only). Its IR-5 audit rates 17 of the 18 new test functions Strong and AC-148.1's native-volume smoke Adequate, with no Weak test. For this MEU the reviewer accepted Q1 (AC-147.1 to AC-147.6): an AST comparison found `clean_text`'s executable body identical to the adapter's old cleaner, both fallbacks are cleaned before any stored row or written file, and the real-storage test reads the cleaned values back. It restates the approved exclusions (transcript body text, stored rows written before the change) and infers no broader guarantee. The canonical rolling report is `.agent/context/handoffs/2026-11-15-text-scrub-residuals-implementation-critical-review.md`, byte-equal to the round-1 report.

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsr-h1-7a-review-state", "command": "rtk proxy uv run python tools/validate_closeout_artifacts.py --review .agent/context/handoffs/2026-11-15-text-scrub-residuals-implementation-critical-review.md --review-state-only --expected-review-mode execution --expected-target-plan docs/execution/plans/2026-11-15-text-scrub-residuals/implementation-plan.md --max-review-rounds 6 --output C:/Temp/av-kit/text-scrub-residuals/review-state.json *> C:/Temp/av-kit/text-scrub-residuals/review-state-check.txt", "scope": "H1-7a: the canonical execution review parsed to its target-bound state", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "ab761ddd5cc47cb014e80450be1e80c0825c984f+e7c60e3a25531c47ba7e950292591af393053446561e32e97d1731d07e2e0e4d", "output": "review-state-check.txt: OK: review_mode=execution; round 1 of 6; verdict=approved; open findings=0; state receipt written to review-state.json"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "tsr-h1-7b-approval", "command": "rtk proxy uv run python tools/validate_closeout_artifacts.py --review .agent/context/handoffs/2026-11-15-text-scrub-residuals-implementation-critical-review.md --approved-state-only --review-state-receipt C:/Temp/av-kit/text-scrub-residuals/review-state.json --expected-review-mode execution --expected-target-plan docs/execution/plans/2026-11-15-text-scrub-residuals/implementation-plan.md --max-review-rounds 6 *> C:/Temp/av-kit/text-scrub-residuals/exec-review.txt", "scope": "H1-7b: an approved current review state and a matching ledger verdict, cap 6", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "ab761ddd5cc47cb014e80450be1e80c0825c984f+e7c60e3a25531c47ba7e950292591af393053446561e32e97d1731d07e2e0e4d", "output": "exec-review.txt: OK: approved at round 1 of 6, 0 open blocking findings"}
```

### Verdict

`approved` at round 1 of 6 (ledger loop `tsr-execution-2026-11-15-text-scrub-residuals`), with 0 open blocking findings (`review-state-check.txt`, `exec-review.txt`). The review grants no commit or push authorization.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| A lone surrogate in a transcript's text (`result.text`) fails the same raw write | residual for triage | none | Plan §Out of Scope; neither issue names it (`TRANSCRIPT-UNCLEANED-TITLE-FALLBACKS`, triage D-804) |
| A refusal guard on `TranscriptJob`, `TranscriptItem` or `TranscriptResult` | out-of-scope | none | D-924 (CLEAN_AT_ENTRY) |
| Stored rows written before this change with an unclean name or title | out-of-scope | none | D-924: stored rows are read as before; only new values are cleaned |
| The renderer, the API, MCP and E2E | out-of-scope | none | No shape changes (plan §Boundary Inventory) |
| Commit and push | out-of-scope | — | Only on Mat's explicit words (H2-5) |

### Departures and their basis

- **Status line 15.** The coordinator wrote Mat's authorizing words into the plan's Status line after the plan review approved it. It is a plan-text edit made after approval; no AC, task row or contract changed.
- **Execution decisions D-928 to D-930** (HDP v2, `resolution: autonomous`, recorded in the plan's decision YAML; none hit an M item, each `mandatory: none`): D-928, the DECLARED_NEW list follows task row 0; D-929, the plan-local `scope-check.py`; D-930, `ruff format` on `adapter.py` and `services/download.py`, six layout-only hunks. Per H1-6 (Session 65 RULE-2) they live in the plan YAML, so the Decision Log below is `None.`.
- **Early test write.** The MEU-147 test file was written while row 0's base suite was still running; that suite had already collected, and `baseline-scope.json` records the file absent. The file was moved to the receipts folder's `staged` folder and restored at row 1 after the S4 check (`tsr-s4-row1.txt`: `scope-check: ok`). The base 2945 exclude it. The MEU-148 test was first written into `staged` and placed at row 3.
- **Row 2's first Green attempt** failed 2 of 35 in the test's own `_front` helper (CRLF on read-back); the fix is in the helper only (`test_transcript_title_cleaning.py:52`). Receipt `tsr-147-green-attempt1.txt`.
- **U+200B in the test source.** A literal zero-width space was replaced by the `\u200b` escape, so the file holds no invisible character; the case is unchanged.
- **`_SHORT_FORMS_LOCK`.** `health.py` guards the short-form cache with a lock beyond the plan text, so "looked up at most once per process" holds when logging threads scrub at the same time.
- **Scratch wrappers.** Each row ran through a `run-*.ps1` wrapper of its task cell in the receipts folder, with `ELECTRON_RUN_AS_NODE` unset; helper scripts there (`delivered-notes.py`, `green-147.py`, `green-148.py`, `focus-h13.py`, `mark-row.py`, `fill-handoffs.py`, `eol-final.py`) are not tracked. One wrapper's `Set-Location` line first carried a BEL where a backslash was meant and was corrected before it ran a row.
- **D-919 red-check regex** (`red-check.py:87`, `^_+ (.+?) _+\s*$`) was applied to the row-0 copy, as the plan directs; the row-0 copies carry 4 (red-check), 6 (identity) and 2 (issue-resolve) edits.
- **Gate attempt 1** stopped on a gate-script defect (the missing mutant `.exit` file), fixed in `session-gate.ps1`; the rerun passed. This is not the one flake rerun the brief allows.
- **`tsr-148-real-lookup.txt`** begins with a Python `SyntaxWarning` from the probe's `-c` string; the probe's results follow it and are unaffected.
- **AC-147.5** is an integration AC whose test sits in the `tests/unit` file under `@pytest.mark.integration` (`:187`), where the plan placed it.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-15 | claude-code-local (Claude Opus 5.5) | Initial MEU-147 handoff after the H1-2 gate, H1-3 and H1-4 |
| Reviewed | 2026-11-15 | codex-independent-reviewer | H1-7 execution review approved at round 1 of 6, 0 findings |
| Updated | 2026-11-15 | claude-code-local (Claude Opus 5.5) | Codex Validation Report filled from the canonical review (H2) |
