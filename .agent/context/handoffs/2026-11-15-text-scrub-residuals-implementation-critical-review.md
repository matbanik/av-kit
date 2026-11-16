---
date: "2026-11-15"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-15-text-scrub-residuals/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "tsr-execution-2026-11-15-text-scrub-residuals"
round: 1
---

# Critical Review: 2026-11-15-text-scrub-residuals

> **Review Mode:** `execution`  
> **Verdict:** `approved` — the delivered changes achieve the registered intent; no findings.

## Intent Anchor

a lone surrogate or a control character in a transcript channel's extract title or in a caption port's title never fails job creation or a fetch and never reaches a stored row or a written file, and on Windows the Console and the download log lines show the home folder's 8.3 short form as `~`, just as they show the long form.

**Intent achieved: yes.**

## Scope

Independent Codex review of Anthropic/Claude Code's Session 77 implementation, MEU-147 and MEU-148, on `main`, baseline/HEAD `ab761ddd5cc47cb014e80450be1e80c0825c984f`. Read the execution-review workflow, implementation plan, task and both handoffs, inspected the five product-file diffs and all scoped record diffs, and read both new test files completely. Applied IR and AV checks to behavior, tests and evidence. Approved decisions D-922 through D-927 and Mat's D-337 were held fixed. D-928 through D-930 were assessed against their code and receipts.

Sessions 78–83 plans and other sessions' baseline-dirty artifacts are outside this review. The coordinator's H1 review collection and subsequent H2 work remain pending as expected. This approval covers the delivered implementation, not a claim that the coordinator has completed closeout or received commit authorization.

The reviewer wrote only under `C:/Temp/av-kit`; no repository file was edited. No stage, commit, stash, revert, branch, worktree, push or network operation was performed. The coordinator copies this report to its canonical destination.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

## Q1 — Transcript title cleaning (AC-147.1 to AC-147.6)

Accepted. `packages/core/src/avkit_core/domain/download.py:318` and `:321` contain D-360's category set and cleaner. Independent AST comparison confirms that its executable body is identical to the old adapter implementation; the docstring adds the shared-use explanation. `packages/infrastructure/src/avkit_infra/youtube/adapter.py:28`, `:224`, `:718` and `:722` use that one object, with no local cleaner or category-set copy (`TEXT_CLEAN_SHARED`).

`packages/core/src/avkit_core/services/transcript.py:173` cleans the extract-title fallback before creating the job and saving its name, and supplies the extract ID when cleaning produces nothing (`CHANNEL_FALLBACK_CLEAN`). The folder still comes from the raw extract title's `slugify` result (`SLUG_SOURCE`). At `:639`, the listed title wins; otherwise the cleaned port title or video ID is selected once, then supplied to both `_raw_markdown` and the stored Done item (`RESULT_TITLE_CLEAN`, `TITLE_KEPT`). Raw front matter at `:793` and compiled headings at `:369` consume these stored clean values; no additional path from either named fallback bypasses cleaning. Listed fields retain their existing domain guard. The service does not add refusal guards to old transcript rows (`CLEAN_AT_ENTRY`).

The real SQLite/filesystem test passes, including a fresh unit-of-work readback and UTF-8 file decoding. All 16 metadata tests and six selected AC-122 adapter tests also pass unchanged. No missing behavior was found within the two entry points. Cleaning transcript body text and migrating historical stored values remain the approved exclusions.

## Q2 — Windows lookup (AC-148.1, AC-148.8, AC-148.9)

Accepted. `packages/core/src/avkit_core/services/health.py:118` loads `GetShortPathNameW` inside the Windows branch with `[LPCWSTR, LPWSTR, DWORD]` and return type `DWORD`, matching the ctypes pattern in `packages/api/src/avkit_api/cli.py:28`. Off Windows it returns `None`; the two specified load failures are caught (`SHORT_PATH_API`). The reviewer independently checked the real callable's signature and injected both load exceptions, without looking up the actual home folder.

At `health.py:137`, `short_path_name` queries the size, allocates that size, fills the buffer and returns its value only for `0 < written < size` (`SHORT_PATH_NAME`). The supplied tests verify success and the principal failure cases; reviewer probes additionally verify ValueError during either call, a fill larger than the buffer and a negative fill length. All return `""` as required. The real native test uses only a folder under the review temp directory and checks same-file identity when the call succeeds.

The independently run empty-lookup mutant produced exactly two assertion failures, at `tests/unit/test_console_home_short_form.py:232` and `:243`, with zero passes and 16 deselections. The real helper's successful producer and its downstream consumer are therefore both checked. No lookup defect was found; a real volume returning no distinct alias is intentionally not proof of a successful alias lookup.

## Q3 — Cache, scrubbing and lock (AC-148.2 to AC-148.7)

Accepted within the approved contract. `health.py:161` keys `_SHORT_FORMS` by the trailing-separator-trimmed home value, caches empty results, deduplicates case-equivalent aliases and bypasses lookup entirely when `SHORT_FORM_LOOKUP` is false (`SHORT_FORM_LOOKUP`, `SHORT_FORM_CACHE`). The added lock makes the at-most-once rule hold for concurrent callers. Independent 16-thread probes, for both a distinct alias and an empty lookup, each recorded exactly one lookup and exact outputs from every Console/download caller.

The lock's scope deserves precision: `health.py:175` holds it while making the first synchronous native lookup. Thus a claim that lookup occurs outside the lock, or that arbitrary native I/O cannot delay logging, would be false. The implementation has no logging callback or Console ring/file-lock acquisition beneath that lock; `HealthService._process` constructs fields before acquiring its ring lock (`:294`, `:303`). No concrete recursive deadlock or indefinite lookup was demonstrated. The bounded concurrency probe establishes cache correctness and completion with a returning lookup, not an OS-call time bound. This latency limitation is recorded below rather than asserted away or promoted into an unsupported High finding.

`health.py:183` and `packages/core/src/avkit_core/services/download.py:107` retain the D-335 patterns and case flag, applying them to each form (`SHORT_FORM_SCRUB`, `SHORT_FORM_SPLIT`). The download path retains D-627's marks before cleaning. Short-form boundary negatives, slash/doubled-backslash/case cases, tab/control/ANSI splits, failure behavior, long-form regression and disabled lookup pass. A reviewer probe also sent a synthetic short path through the actual HealthService and verified exact scrubbed messages in the ring, JSON stdout and `console.log`. No short-form-only bypass was found on a surface that scrubs the long form.

## Q4 — Red/Green evidence and test rigor

Accepted. Original Red receipts report 19 MEU-147 failures and 18 MEU-148 failures, all attributed by the plan's checker to assertions on the absent names; independently rerunning that checker with every required AC family returned zero problems for both. These Reds establish the declared entry-point absence, rather than independently reproducing every downstream storage failure. The current tests then exercise specific output values, fallbacks and storage behavior; none passes vacuously.

Independent Green: 37 new tests, 16 metadata tests, six AC-122 tests and ten AC-119.10 tests passed: **69 passed** across four invocations. The mutant failed as intended. The new home tests use synthetic home values; the real native case creates only a temp folder. The new storage test uses function-scoped SQLite and FilesystemAdapter, with real writes/readback under temp. Its integration marker remains effective despite its unit-folder location. Existing regression test files are byte-unchanged in the HEAD diff.

The first Green's two `_front` IndexErrors match the retained receipt; the helper's CRLF normalization fixes parsing without weakening any assertion. The escaped U+200B case retains its original value. The gate's first attempt genuinely stopped at its missing mutant exit sidecar. `session-gate.ps1:120` now saves the original child status before converting the expected failure into a gate success; failure count, zero passes, red-check attribution and fail-fast behavior remain required. This repair does not weaken the mutant check.

### IR-5 test audit

Every parametrized case shares its function's rating. Strong means exact behavioral values or state assertions; Adequate identifies the intentionally permissive native-volume smoke test. No Weak test was found.

| Test function (prefix `test_` omitted) | Source | Rating |
|---|---|---|
| ac_147_1_clean_text_drops_controls_and_surrogates | test_transcript_title_cleaning.py:81 | Strong |
| ac_147_1_adapter_uses_the_domain_cleaner | test_transcript_title_cleaning.py:91 | Strong |
| ac_147_2_channel_fallback_cleaned_for_a_playlist | test_transcript_title_cleaning.py:100 | Strong |
| ac_147_2_channel_fallback_cleaned_for_a_video | test_transcript_title_cleaning.py:119 | Strong |
| ac_147_3_title_that_cleans_to_nothing_takes_the_playlist_id | test_transcript_title_cleaning.py:139 | Strong |
| ac_147_3_title_that_cleans_to_nothing_takes_the_video_id | test_transcript_title_cleaning.py:152 | Strong |
| ac_147_4_result_title_cleaned_and_falls_back_to_the_id | test_transcript_title_cleaning.py:166 | Strong |
| ac_147_5_unclean_fallbacks_survive_real_storage | test_transcript_title_cleaning.py:188 | Strong |
| ac_148_1_real_native_lookup_does_not_break | test_console_home_short_form.py:102 | Adequate |
| ac_148_2_short_form_becomes_tilde | test_console_home_short_form.py:133 | Strong |
| ac_148_3_lookup_runs_once_per_home | test_console_home_short_form.py:141 | Strong |
| ac_148_4_no_short_form_matches_only_the_long_form | test_console_home_short_form.py:183 | Strong |
| ac_148_5_no_lookup_when_the_flag_is_false | test_console_home_short_form.py:192 | Strong |
| ac_148_6_one_line_with_both_forms | test_console_home_short_form.py:200 | Strong |
| ac_148_7_scrub_line_matches_a_split_short_form | test_console_home_short_form.py:220 | Strong |
| ac_148_8_real_helper_returns_the_filled_alias | test_console_home_short_form.py:229 | Strong |
| ac_148_8_real_helper_feeds_the_scrub | test_console_home_short_form.py:239 | Strong |
| ac_148_9_failed_native_lookup_gives_nothing | test_console_home_short_form.py:281 | Strong |

## Q5 — Delivery boundaries

Accepted. The API, OpenAPI, MCP and renderer trees have no delta. The shared-record row-0 hashes match HEAD (accounting for stored versus physical CRLF), so the reviewed record diffs isolate this session's changes. Parsed YAML comparison identifies exactly MEU-147 and MEU-148, both `ready_for_review`, and exactly their two issues; issue edits affect only `status`, `verification` and `resolution_path`. Row 5's wrapper and successful receipts show `issue-resolve.py`, `issue_triage.py render` and `meu_status.py update/render` performing these changes. Generated totals and rendered rows agree with the gate receipts.

The grouping changes only section 6 row 77. `03-service-layer.md` changes only the two Delivered (Session 77) notes. D-928 strengthens declared-name setup-failure detection; D-929 implements the planned scope and line-ending checks, and passes against all six untouched baseline-dirty hashes. For D-930, whole-module AST comparison after removing only the intended functional changes proves both modules otherwise identical; the six extra hunks are layout only. No unrelated product work or silently deferred acceptance criterion was found.

## Q6 — Safety, fidelity and tested state

Accepted. The independent scope check passes; HEAD equals baseline and the index is empty. All 14 Files Modified entries retain their declared line endings, including CRLF product files and the 03 document; both new tests are LF. Added text across 28 scoped source/plan files contains no real home long-form prefix or personal email, and the home short forms in added examples are synthetic. The existing tracked-home-path cleanup issue remains outside this delta. No claim is made that all historical tracked documents were sanitized by this session.

**tested_state:** `ab761ddd5cc47cb014e80450be1e80c0825c984f+e7c60e3a25531c47ba7e950292591af393053446561e32e97d1731d07e2e0e4d`.

This is the actual output of the plan's `identity.py --state-only`, with `ELECTRON_RUN_AS_NODE` unset. It exactly matches the gate. Before executing it, the reviewer supplied a temp-only `core.excludesFile` containing solely `/.claude/settings.local.json`, reproducing the stated host ignore while preserving inherited Git safety configuration. Comparing filename enumerations with an empty temp ignore proves that **only** `.claude/settings.local.json` differs between those views; its contents were never opened or hashed. Consequently there is no tested-state difference after that explicit normalization. An unnormalized identity, which would read that forbidden file, was deliberately not computed. The schema has no top-level `tested_state` property, so the machine verdict records the value in its summary and identity checklist evidence.

The handoffs' full-gate claim matches the retained receipts: identity before equals after, all static checks pass, targeted checks and the mutant predicate pass, the full Python suite reports **2982 passed, 37 warnings**, the issue/status renders pass and UI canon reports **14 passed**. The previous gate attempt and initial Green failures are accurately disclosed. The fresh full gate was accepted at its matching identity; the reviewer did not rerun the whole suite.

## Checklist Results

All execution commands below ran from `P:/av-kit`. The temp wrapper invokes `rtk proxy uv run --no-sync --offline --frozen`, propagates the child's exit immediately, disables bytecode and pytest cache, sets TMP/TEMP and every pytest basetemp beneath the assigned review tmp directory, and uses a temp UV cache. No environment synchronization or network lookup runs. Initial reviewer command/setup failures were repaired only in temp; they are not product failures or passing evidence.

| Check | Result | Observation |
|---|---|---|
| IR-1 runtime/storage evidence | pass | Real SQLite/FilesystemAdapter test and native Windows temp-folder smoke passed. |
| IR-2 collaborator fidelity | pass | Concrete job/item state and raw Markdown readback assertions; real-storage counterpart. |
| IR-3 route error mapping | n/a | No API route or MCP shape change. |
| IR-4 fix generalization | pass | Both title fallbacks and both home scrubbers traced through callers. |
| IR-5 assertion rigor | pass | All 18 new test functions audited above; no Weak test. |
| IR-6 boundary validation | pass | Cleaning at approved entry points; existing listing guards and public shapes retained. |
| IR-7 AC/deferral integrity | pass | All 15 ACs evidenced, real-storage integration retained, no silent deferral. |
| AV-1 to AV-6 | pass | Red/Green, exact assertions, no skip/xfail or bypass, no delivered placeholders, source-backed criteria. |
| State/fresh full evidence | pass | Exact normalized identity match; 2982 Python and 14 UI canon passes in retained gate. |
| Scope/EOL/privacy | pass | Independent scope/EOL checks and source-delta audit passed; no repo mutation. |

```json
{"schema_version":"evidence.v1","check_id":"review-new-tests","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/text-scrub-residuals/exec-review/run-review.ps1 -Step new-tests","cwd":"P:/av-kit","scope":"Both new test files, AC-147.1 to AC-147.5 and AC-148.1 to AC-148.9","phase":"targeted","exit_code":0,"result":"pass","tested_state":"ab761ddd5cc47cb014e80450be1e80c0825c984f+e7c60e3a25531c47ba7e950292591af393053446561e32e97d1731d07e2e0e4d","output":"37 passed in 0.49s; no skipped cases"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-regressions","procedure":"Ran run-review.ps1 separately with -Step metadata, adapter and ac119; each wrapper preserved its pytest child exit.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"Unchanged metadata, AC-122 and AC-119.10 regression tests","phase":"targeted","exit_code":null,"result":"pass","tested_state":"ab761ddd5cc47cb014e80450be1e80c0825c984f+e7c60e3a25531c47ba7e950292591af393053446561e32e97d1731d07e2e0e4d","output":"metadata exit 0: 16 passed in 0.52s; adapter exit 0: 6 passed, 31 deselected in 0.49s; ac119 exit 0: 10 passed, 108 deselected in 0.15s"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-empty-lookup-mutant","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/text-scrub-residuals/exec-review/run-review.ps1 -Step mutant","cwd":"P:/av-kit","scope":"AC-148.8 with -p mutant_empty_lookup and PYTHONPATH at the plan folder","phase":"red","exit_code":1,"result":"pass","tested_state":"ab761ddd5cc47cb014e80450be1e80c0825c984f+e7c60e3a25531c47ba7e950292591af393053446561e32e97d1731d07e2e0e4d","output":"Expected failure: 2 failed, 16 deselected in 0.09s; both failures are AssertionError at test_console_home_short_form.py:232 and :243; no passed test"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-adversarial-probes","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/text-scrub-residuals/exec-review/run-review.ps1 -Step probe","cwd":"P:/av-kit","scope":"Synthetic concurrent cache, native load/signature/failure handling, cleaner AST, unchanged public/test surfaces and actual Console sinks","phase":"targeted","exit_code":0,"result":"pass","tested_state":"ab761ddd5cc47cb014e80450be1e80c0825c984f+e7c60e3a25531c47ba7e950292591af393053446561e32e97d1731d07e2e0e4d","output":"16 threads: alias lookup once, empty lookup once, all outputs exact. Native signatures/load exceptions/ValueError/invalid fill lengths pass. Cleaner executable AST identical. Existing tests/API/MCP/UI/OpenAPI unchanged; main/HEAD/index checks pass. Synthetic alias scrubbed exactly in ring, JSON stdout and console.log. review probes: all assertions passed"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-source-and-red-audit","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/text-scrub-residuals/exec-review/run-review.ps1 -Step audit","cwd":"P:/av-kit","scope":"D-930, record YAML deltas and baseline binding, filename-only ignore comparison, original Red checker runs and scoped source privacy","phase":"static","exit_code":0,"result":"pass","tested_state":"ab761ddd5cc47cb014e80450be1e80c0825c984f+e7c60e3a25531c47ba7e950292591af393053446561e32e97d1731d07e2e0e4d","output":"Both module AST comparisons pass after removing planned behavior changes. Exactly two MEUs and two issues changed. Shared-record baseline hashes match HEAD. Untracked enumeration differs only for the forbidden settings filename, never opened. Original Red checks: 5 and 9 required AC families, 0 problems, 19 and 18 failures. Privacy additions audit over 28 scoped files passes. audit: all assertions passed"}
```

```json
{"schema_version":"evidence.v1","check_id":"review-scope-and-state","procedure":"Executed run-review.ps1 with -Step identity, scope and eol; compared the identity output with both original gate identity receipts and read the gate and decisive full-suite summaries.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"Current input identity, row-0 scope and line endings, retained fresh full gate","phase":"full","exit_code":null,"result":"pass","tested_state":"ab761ddd5cc47cb014e80450be1e80c0825c984f+e7c60e3a25531c47ba7e950292591af393053446561e32e97d1731d07e2e0e4d","output":"All three reviewer commands exit 0. Identity exactly matches gate after temp-only ignore normalization; scope-check: ok, six baseline-dirty hashes unchanged; all 14 EOL entries match. Observed original gate: session-gate: all steps exit 0; full Python 2982 passed, 37 warnings in 527.72s; UI canon 14 passed. This is observation of the author's full gate, not a reviewer full-suite rerun."}
```

## Residual Risks and Assumptions

- The first short-path lookup is synchronous and occurs under the cache lock. No timeout is implemented; concurrent scrubbing waits for that lookup. No actual indefinite native lookup or lock cycle was reproduced.
- A volume may expose no distinct 8.3 alias; success is proven over a fake native callable, with a real temp-folder smoke alongside it. The real home folder was never looked up by a reviewer probe.
- The approved exclusions remain: malformed transcript body text, historical unclean stored values, `Path.home()` already supplied in short form and a new alias appearing after an empty result was cached. No broader guarantee is inferred.

## Verdict

`approved` — the scoped implementation achieves the registered goal. No evidence-backed High or Critical defect, blocking finding or new required correction was found. Continue the coordinator's review collection and H2 closeout; commit and push still await Mat's direction.
