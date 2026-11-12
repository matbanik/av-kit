---
date: "2026-11-12"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-11-download-failure-visibility/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s65-plan-canonical-2026-11-11-download-failure-visibility"
round: 4
---

# Critical Review: 2026-11-11-download-failure-visibility

> **Review Mode:** plan. **Verdict:** changes_required. **Intent achieved:** partial, judged as a plan.

## Intent Anchor

Session 65 makes a failed download, a SABR check and yt-dlp's own messages visible. A failed download's card says why in one short av-kit sentence per cause, and the Console has a matching `download.failed` line with yt-dlp's first line, redacted, in `detail`. Check SABR matches yt-dlp 2026.10.26's own SABR words, the page always states the last result with its time, and Check, Force and Clear each log one line. yt-dlp's warnings and errors always reach the Console with their text in a kept field; the existing Settings switch adds its debug and info lines, and a change applies on the next call without a restart.

## Scope

Reviewed the working-tree implementation plan, task and five plan-local scripts; cited spec sections, grouping, the three issue entries and MEUs by id; relevant domain/service/adapter/API/renderer code; existing test pins; installed yt-dlp source; and supplied planning scripts/receipts. Applied PR-1 to PR-9, the Materiality Gate and Verdict Rule. Observed HEAD `003e5b1466c4b7accadc6b3267c7d4b1315f2991`. The implementation task rows are unchecked and no MEU-137 to MEU-139 implementation handoff exists. Claude Code/Anthropic authored this plan; Codex did not.

Accepted Mat's D-622 to D-624, grouping D-535 to D-543, prior approvals through Session 64 and the stated exclusions. D-625 remains Mat's decision. No repository file was edited. No network request, product test suite, baseline/session gate, backend, MCP server, npm, npx or tsx was run. New probes, scratch copies and this report were written only under `C:/Temp/av-kit`. Forbidden files were not opened. Proposed behavior is assessed below; this report does not certify an implementation pass.

## Findings

All three findings have High confidence and concern delivery. No Critical finding was established.

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High | yes | behavior | `FAILURE_LOG`/D-638 cleans **after** redaction, home scrubbing and URL replacement. Literal execution with `co\x00okie=SECRET` stores `Download failed: cookie=SECRET.`; `https\x00://e.example/private` stores the restored URL; an ANSI sequence inside a synthetic home name restores the full home path. `CLEAN_LINE` reconstructs text the earlier scrubbers could not recognize. These values go straight to SQLite, `GET /downloads`, MCP list and the card. The Console's second scrub masks them, so its absence checks cannot certify storage safety. Violates AC-137, specifically AC-137.7/.9 and the promised safe stored reason. | `docs/execution/plans/2026-11-11-download-failure-visibility/implementation-plan.md:127`; `:150`; `:644`; `packages/core/src/avkit_core/domain/transcript.py:236`; `packages/core/src/avkit_core/services/health.py:76` | Extract the intended first line, normalize it before sensitive-text recognition, then redact, scrub home, replace links and truncate. Add storage/API regressions for split needles, split URLs and ANSI inside the home path, alongside the existing Console positive control. Keep the established Session 50 helpers. | fixed |
| F2 | High | yes | behavior | The moved pins omit incompatible existing callers. Appending `DownloadFailedError(cause, detail)` makes `test_domain.py:221` call it as `cls("domain failure")`, which raises TypeError; moving only the names tuple cannot make row 1 pass. After `FAILURE_RAISE`, two existing adapter tests still require the **exact** base `DomainError` for `DownloadError("boom")` (`:472`, `:736`), although the new contract requires `DownloadFailedError(other, "boom")`. Both run in row 3. Neither pin moves in row 2a, and Green forbids test edits. The proposed sequence therefore cannot reach its required Green checks. Violates AC-137's AC-137.1/FAILURE_RAISE delivery and its declared regression guards. | `docs/execution/plans/2026-11-11-download-failure-visibility/implementation-plan.md:142`; `:357`; `docs/execution/plans/2026-11-11-download-failure-visibility/task.md:65`; `:68`; `tests/unit/test_domain.py:221`; `tests/integration/test_youtube_adapter.py:472`; `:736` | Explicitly adapt the inventory's constructor case in row 1, preserving coverage of every error type. Move both exact-type pins in row 2a to the new, source-backed failure contract, retaining the age/extract distinction and exception chaining. Name these moves and keep Green expectations immutable. | fixed |
| F3 | High | yes | behavior | MEU-137's Green depends on MEU-138's later implementation. AC-137.6 requires the captured `missing a URL`/SABR-only warning followed by a format error to raise `refused`. Through row 3 the logger still scans only `SABR_LOG_NEEDLES`, so that warning leaves `sabr_detected=False` and `FAILURE_CAUSE` produces `no_format`. The offline probe reproduced this. Row 1 also leaves `sabr_phrase` returning None, while AC-137.5 already requires SABR text classification. `SABR_MATCH`/`SABR_SCAN` are implemented only in row 4, which depends on row 3 passing. Violates AC-137.5/.6, cited as family AC-137. | `docs/execution/plans/2026-11-11-download-failure-visibility/implementation-plan.md:191`; `:192`; `:352`; `docs/execution/plans/2026-11-11-download-failure-visibility/task.md:68`; `:71`; `packages/infrastructure/src/avkit_infra/youtube/adapter.py:321` | Schedule the shared matching/scanning prerequisites and their behavioral Reds before the first Green that needs them, or explicitly restructure the dependent tests/work packages. Keep one matcher and update the old-needle pin's Red/Green placement consistently. Do not waive AC-137.6 to get past row 3. | fixed |

## Q1 — Goal and three calls

The final intended trace is coherent: warning scanned → format error classified `refused` → `DownloadFailedError` → stored av-kit sentence and one `download.failed` → unchanged list route → `error_message` mapping → card. The failure line uses kept `error`/`detail`. F2/F3 prevent reaching this state in the written sequence; F1 defeats its safe unknown-cause path.

Check → adapter phrase → Active/Detected status → service status/log → unchanged three-field response → `sabrResultText` is covered by AC-138.2/.3/.5/.6/.8. Force/Clear have distinct log/text outcomes and a time. Settings PUT → live callable → next call's logger/options → kept text is covered by AC-139.4/.5/.7/.8. Every rule of the three residual sections has a named producer and AC; this is not a missing-feature-scope finding.

## Q2 — Causes and messages

Accepted the five-cause policy and exact named messages. The installed yt-dlp source and supplied matrix support the ordinary reload, bot-check, format, cookie and write needles. First-match ordering is explicit, including mixed-cause text; the age check remains before classification. Unknown, empty and multiline cases have tests. D-636 correctly uses the same call's `sabr_detected`, rather than a stale forced service status, for the format override. D-637 removes the OSError filename; its type/strerror are still sanitized at the service boundary. The timing of that SABR signal is F3.

## Q3 — Cleaning and lifecycle logs

Category-based removal is total over Python strings, including lone surrogates, NUL and C1 controls; the CSI regex handles the specified escapes. F1 is the material ordering defect. A small non-blocking wording correction is also needed: literal `CLEAN_LINE` at plan:123 removes CR/LF/tab before collapsing whitespace, producing `ab` for `a\r\n\tb`, whereas AC-137.4 expects `a b`. Make that ordering agree; this is not an additional High finding.

`FAILURE_LOG` covers DownloadFailedError, CookieTestError, AgeRestricted, other DomainError, other Exception and Cancelled. Its stored-text policy is explicit, with only AgeRestricted retaining its established text. Started-before-port, Done-after-commit and exactly-one failure event are observable in AC-137.8. Cancelled's lack of a new terminal event follows D-634.

## Q4 — Writers and redaction

For ordinary unmodified markers the chain is correct: named causes store constants; `other` is scrubbed and capped at REASON_LIMIT=200; Console fields scrub again and cap at FIELD_LIMIT=300; the Health processor prints/persists the same safe assembled message. API and MCP list consume the stored reason directly. F1 shows why the additional normalization must precede that first storage boundary. AC-137.9 and AC-139.5 explicitly require a positive home-marker control, which is sound.

AC-137.11's exact short expected values are compatible with both limits: `bad\ud800 x\x00y` becomes `bad xy`, and the message is `Download failed: bad xy.`. No truncation cuts a surviving cookie value when the original needle was recognized; a cut may shorten `[REDACTED]` without recovering the removed value. The problem demonstrated in F1 is recognition after normalization, not truncation of a correctly redacted secret.

## Q5 — SABR phrases and scan

Accepted D-623/D-624. Installed `_video.py:3538-3548` contains both the missing-URL template and the forcing/SABR-only wording; `:3197` contains `require a GVS PO Token`. Whole-word case-folded regexes match these and refuse Sabrina/sabre/sabrs. A generic PO Token line without a selected phrase stays off. Tuple-order precedence and first-matching-line retention are deterministic and tested. Every method scans, including both error forms. The only current assignments to the logger's `sabr_detected` are its initializer and scanner, both changed by `SABR_SCAN`; result DTO fields are separate. The final property is safe. Its late scheduling is F3.

## Q6 — SABR domain and wire

Accepted. The optional final phrase field leaves existing constructors valid; some test fakes use positional construction, contrary to one incidental sentence in plan:233, but appending a default preserves them. Active/Detected is the only permitted non-None combination; initial, forced, cleared and passive statuses keep None. SABRStatus is session state, not persisted. `_sabr_out` at routes/downloads.py:63-69 explicitly selects mode/source/time; neither it nor the wire schema walks `SABR_STATUS_FIELDS`. D-626 can leave OpenAPI and the wire unchanged, and AC-138.5 checks the exact response keys.

## Q7 — SABR actions and display

Accepted the one-event-per-action contract, unchanged re-raise, unchanged status on failed check, and existing `run`/`setError` error banner. Formatting distinguishes checked/forced/cleared, uses local zero-padded time and handles undefined/unparseable snapshots. The existing AC-53 assertions require the Active text/id to remain visible, rather than require Inactive to remain hidden. No test-id registry edit is needed. Effective visibility must implement the contract's “always shown” through the containing Advanced disclosure as well; renderer verification remains required, not observed here.

## Q8 — yt-dlp text and live switch

Accepted D-622/D-632 and the final routing. Installed YoutubeDL routes screen/info output to logger.debug, warnings to warning, prefixed failures to error, and verbose traceback text to a separate unprefixed error call. The supplied receipt observes 14 prefixed failures with debug off and an additional 14 traceback calls with verbose on. The policy preserves warnings/errors while allowing the chosen debug opt-in. AC-122.16's debug-off move needs its empty-event expectation as well as the constructor change; §Pins describes “nothing reaches the Console,” so that intended adjustment is clear.

All six logger construction sites are inventoried, including `_run_extract`'s fallback and the cookie probe. `_base_opts(logger)` following that snapshot avoids callable truthiness. None/raising sources fail closed. `extract_video_ids` uses the same path and must retain the per-call read rule. The `_live_location` spy records arbitrary kwargs and forwards them, so it does not require a bool `yt_dlp_debug`. AC-139.4's PUT between calls is the right live-setting proof.

## Q9 — Pins

F2 identifies the material missed constructor/exact-type pins. The other inventoried moves are appropriate: the optional SABR field updates both shared field inventories through `SPEC_SABR_STATUS_FIELDS`; the method signature-equality test is unaffected because no public port signature changes; the wiring spy is compatible. Moving test-local phrases in row 2b will fail against the old scanner and pass after row 4 **under the current schedule**. Correcting F3 must revise that assertion about timing too. AC-51.6's original test-id bytes remain outside the permitted edits.

## Q10 — Reds

The wrong stubs and DECLARED_NEW inventory cover the imported new names. Assertion-first helpers avoid collection/import/exception-class failures being mislabeled Red. The --require sets match the declared Python/Vitest ownership and omit the intended passing characterizations; the guard runs cover those characterizations separately. Independent `red-check.py --selftest` returned `44 fixture(s) (13 positive, 31 negative), 0 wrong: []`. Actual product Reds were not run. F2's TypeError and F3's impossible Green must be corrected before the planned Red/Green evidence can be obtained.

## Q11 — Endings, identity, scope and records

Accepted the byte-preserving edit rule, mixed-ending baselines and LF for new files. Files Modified, project files and gate scope cover the stated producers and test paths. Independent `identity.py --selftest` returned zero failures and exercised code/tests/config/docs/runtime mutations plus artifact exclusions. This verifies its fixture behavior, not the live full gate.

The copy-only resolver completed with `decision logs read: 84 of 84`, 15 parsed changes confined to status/verification/resolution_path of issue indexes 129–131, and `issue-resolve: 0 problem(s)`. The byte diff contained only those three entries; the repository register remained unchanged. Row 6's pre-status copies/diffs and render checks remain appropriate safeguards for actual closeout. D-628 only terminates §8 before the briefs; the supplied copy probe reads the intended 12 decisions without changing their text.

Baseline's rulings, queue, shapes and anchors read the named sources. The expected D-625 refusal is real (`ruled=False`, exit 1); it is not a finding. B runs the complete three-MEU sequence after the substantive fixes. Under A's triggered split, task:52-56 explicitly requires rewriting the active closeout rows for two handoffs/issues and a 65b prompt; MEU-139 remains unimplemented/pending and its issue open. These promised rewrites, including the H1-6a handoff iteration and H2-2 status writes, must precede the two-MEU closeout. Neither choice cures F1–F3, which occur by row 3. No decision for Mat is made here.

## Q12 — Safety

The review's commands were offline reads/probes, the two explicitly permitted selftests and a resolver invocation with a scratch --target. PYTHONDONTWRITEBYTECODE=1 was set for imports/selftests; temporary roots were under `C:/Temp/av-kit/s65/review`. No YoutubeDL download/extraction or network function was called by the reviewer. The plan requires mocked YoutubeDL, fake network-facing ports, tmp_path data, offline sync and no live MCP audit. The session gate includes normal repository build outputs as authorized execution work; it was only read here. No safety finding was established from the permitted inspection.

## Checklist Results

### Plan Review (PR)

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| PR-1 plan/task alignment and PR-4 runnable order | fail | Manual trace of rows 1–5 against required guards and staged implementations; observer codex-independent-reviewer | null | F2 prevents row 1/3 Green; F3 makes row 3 depend on row 4. |
| PR-2 unstarted | pass | Manual read of task statuses, MEU records and matching handoff existence; observer codex-independent-reviewer | null | Product rows unchecked; three MEUs pending; no matching implementation handoffs. |
| PR-3 task contracts and PR-6 correction readiness | pass | Manual task table and handoff-set inspection; observer codex-independent-reviewer | null | Owners, deliverables, exact commands, statuses and per-MEU handoffs present. |
| PR-5 source backing and PR-7 scope discipline | pass | Manual comparison of spec/grouping/issues and decision log; observer codex-independent-reviewer | null | Human choices preserved; later client/runtime/MP3 MEUs exist; no hidden feature deferral established. |
| PR-8 behavior/control reachability | fail | Offline review_probes.py and production writer trace | 0 | Stored cookie/path/URL reconstructed after scrub; direct API/card consumers do not scrub it again (F1). |
| PR-9 single-statement consistency | partial | Manual read of contracts and AC-137.4; observer codex-independent-reviewer | null | Shared mechanisms named once; control-removal/whitespace order needs the one-line clarification recorded in Q3. |

### Information Retrieval / Design Review

| Check | Result | Procedure | Exit | Evidence |
|---|---|---|---|---|
| Source labels, validation cells, build audit and post-MEU rows | pass | Manual plan/task inspection; observer codex-independent-reviewer | null | Three AC families, explicit spec/decision sources, audit and H1/H2 rows present. |
| Review template/frontmatter and report scope | pass | Manual comparison against REVIEW-TEMPLATE.md and supplied output contract; observer codex-independent-reviewer | null | Round-1 report in assigned Temp path; findings refer to delivery, not paperwork. |
| Implementation FAIL_TO_PASS/full gate | n/a | Not run: read-only planning review | null | Planned checks are not execution evidence. |

### Durable observations

```json
{"schema_version":"evidence.v1","check_id":"s65-review-contract-counterexamples","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s65/review/review_probes.py","cwd":"P:/av-kit","scope":"literal proposed text pipeline; unchanged logger; constructor and exact-type pins","phase":"targeted","exit_code":0,"result":"fail","tested_state":"plan-review at HEAD 003e5b1466c4b7accadc6b3267c7d4b1315f2991; proposed contracts, not implemented product","fresh":true,"output":"cookie-control stored_message='Download failed: cookie=SECRET.'; url-control stored_message='Download failed: https://e.example/private.'; home-ansi stored_message='Download failed: C:/Users/ReviewMarker/video.mp4.'; Console masks each; sabr_detected=False FAILURE_CAUSE=no_format while AC-137.6 expects refused; cls('domain failure') requires missing detail; exact DomainError predicates at test_youtube_adapter.py:472 and :736 are false for the required subclass. Exit 0 means the diagnostic probe completed, not that the contracts passed."}
```

```json
{"schema_version":"evidence.v1","check_id":"s65-review-red-check-selftest","command":"rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-11-download-failure-visibility/red-check.py --selftest","cwd":"P:/av-kit","scope":"scratch receipt-parser fixtures","phase":"targeted","exit_code":0,"result":"pass","tested_state":"plan-local red-check.py read at HEAD 003e5b1466c4b7accadc6b3267c7d4b1315f2991","fresh":true,"output":"red-check selftest: 44 fixture(s) (13 positive, 31 negative), 0 wrong: []"}
```

```json
{"schema_version":"evidence.v1","check_id":"s65-review-identity-selftest","command":"rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-11-download-failure-visibility/identity.py --selftest","cwd":"P:/av-kit","scope":"scratch identity-binding fixture","phase":"targeted","exit_code":0,"result":"pass","tested_state":"plan-local identity.py read at HEAD 003e5b1466c4b7accadc6b3267c7d4b1315f2991","fresh":true,"output":"Bound code/tests/config/spec/register/runtime mutations changed identity and refused historical evidence; designated project artifacts left identity unchanged. identity selftest: 0 failure(s)"}
```

```json
{"schema_version":"evidence.v1","check_id":"s65-review-resolver-copy","command":"rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-11-download-failure-visibility/issue-resolve.py --issue DOWNLOAD-FAILED-NO-REASON --issue SABR-CHECK-MISSES-CURRENT-MESSAGES --issue YTDLP-LOG-TEXT-DROPPED --set-file C:/Temp/av-kit/s65/review/resolve.json --expect-sha256 1b95db39781e22478c4e3cb21fc6fb6f5844cdf5ed2c53ae3feb557d77a64f36 --target C:/Temp/av-kit/s65/review/known-issues.yaml","cwd":"P:/av-kit","scope":"synthetic resolve to scratch copy only","phase":"targeted","exit_code":0,"result":"pass","tested_state":"register SHA-256 1b95db39781e22478c4e3cb21fc6fb6f5844cdf5ed2c53ae3feb557d77a64f36","fresh":true,"output":"decision logs read: 84 of 84; parsed fields changed: 15, confined to .issues[129], .issues[130], .issues[131] status/verification/resolution_path; issue-resolve: 0 problem(s). Independent byte diff contains only these entries. The original register was not written."}
```

## Verdict

`changes_required` — F1 is a reproduced stored-text safety defect. F2/F3 are concrete incompatible guards and a forward implementation dependency that prevent the written plan from reaching Green. Correct these through `/plan-corrections`, then independently recheck the revised plan. D-625 and execution authorization remain Mat's at the gate. No product execution is authorized by this report.

Residual risk: actual runtime behavior, full suites, Electron visibility and the final session gate remain unrun, as required for this review. This report is saved at `C:/Temp/av-kit/s65-plan-review-round-1.md`; the coordinator owns the canonical copy.

## Corrections Applied — 2026-11-12

Plan summary: the three MEUs, their 28 ACs and the row order are unchanged. Round 1's three findings and its Q3, Q6, Q7 and Q8 notes are corrected in `implementation-plan.md` and `task.md` only; no production code or test was written. Authority: Mat, USER_EXPLICIT 2026-11-12 "Fix F1 to F3, increase token buget by 30M and continue the loop until approved" (ledger `continue`, `C:/Temp/av-kit/s65-plan-ledger-continue-1.txt`).

Changes made, by file:

- `implementation-plan.md`, F1 (clean first, then scrub):
  - `CLEAN_LINE` now runs in four steps: drop ANSI CSI; turn every `str.isspace()` character into a space; drop `Cc`, `Cf` and `Cs` code points; collapse spaces and strip. Every site runs it before `redact_message`, `scrub_home` and `safe_reason`.
  - `FAILURE_LOG`: `detail` is `redact_message(clean_line(raw))`, and the `other` reason is `safe_reason(scrub_home(redact_message(clean_line(raw)))) or type(exc).__name__`.
  - `SABR_LOG`'s `error` and `YTDLP_LINE`'s `detail` are `redact_message(clean_line(...))`.
  - `FAILURE_CAUSE`'s `detail` is the first line whose `clean_line` is non-empty, cleaned, with `ERROR: ` dropped, so the coloured prefix goes too.
  - The meaning bullet, §Where values go, D-627 (chosen and reasoning) and D-638 (chosen and reasoning) say the same.
  - AC-137.4 gains `"a\u2028b"` → `"a b"`, `"co\x00okie"` → `"cookie"`, `"a\u200bb"` → `"ab"`, `"\u202e"` → `""` and an ANSI code inside a home path. Its `"a\r\n\tb"` → `"a b"` case now holds (the Q3 note).
  - AC-137.5 gains the coloured `ERROR:` prefix case.
  - AC-137.7 gains the three split forms in storage: `co\x00okie=SECRET`, `https\x00://e.example/private`, and a home path with `\x1b[0m` inside it.
  - AC-137.9 gains a second job that raises the split forms, checked in the ring, stdout and the served `error_message`.
- `implementation-plan.md`, F2 (pins that would break):
  - §Pins that move gains the `test_domain.py:221` constructor walk (row 1, with an `ERROR_ARGS` map for `DownloadFailedError`) and the two exact-type pins `test_youtube_adapter.py:472` and `:736` (row 2a: `is DownloadFailedError`, cause `other`, detail `boom`).
  - Verification Plan §2 requires both moved pins in row 2a by full name. `red-check.py`'s `_title_matches` accepts a full name, since it matches up to a non-digit boundary.
  - The Guards paragraph's false "read by the API error mapping" becomes `test_domain.py:216` only (`C:/Temp/av-kit/s65/corr-domain-error-types.txt`).
  - MEU-138's Guards name the positional `SABRStatus` fakes at `tests/e2e/test_api_downloads.py:56`, `:149`, `:153` and `:157` (the Q6 note; the review cited `:148`, and the grep finds four sites).
- `implementation-plan.md`, F3 (row 3 reached forward into MEU-138):
  - AC-137.6's warning is now `Some formats require a GVS PO Token which was not provided`. Both the old `SABR_LOG_NEEDLES` and `SABR_PHRASES` hold that phrase, so it passes on row 3's scanner. Every `_YtDlpLogger` method already calls `_scan` at `adapter.py:320-338`.
  - AC-137.5's phrase-only case moves to AC-138.2 as `classify_download_error("… forcing SABR streaming …", False)` → `refused`.
  - AC-138.5 gains the goal's first trace: `download` logs the captured missing-a-URL line, then raises `Requested format is not available`, and the result is `DownloadFailedError` `refused`.
  - `FAILURE_CAUSE` and a new Verification Plan §2 bullet say that row 3 calls the row 1 `sabr_phrase` stub and reads the scanner as it stands.
- `implementation-plan.md`, the notes:
  - Q7: `SABR_SHOWN` says that the panel loses `hidden` and stays in the Advanced disclosure beside the SABR buttons, and AC-138.8 checks it with `toBeVisible` after opening the disclosure.
  - Q8: the AC-122.16 pin row expects no `yt-dlp` event at all when debug is off.
- `task.md`:
  - The header says that a moved pin is required by its full name.
  - Row 1 moves three `test_domain.py` pins.
  - Row 2a re-reads `test_youtube_adapter.py:455-475` and `:722-740`, moves the two pins, adds `tests/integration/test_youtube_adapter.py` to its pytest run, and adds the two pins' `--require`.
  - Row 3 notes the clean-first order and the stubbed phrase branch.
  - Row 4 says that `classify_download_error` needs no change.

Verification results:

- The edits ran from `C:/Temp/av-kit/s65/corr/apply_r1_corrections.py`, which replaces each old text exactly once after a dry run of both files (`C:/Temp/av-kit/s65/corr/apply-r1.txt`). The plan took 32 edits and the task 9. Both files are still LF only.
- `tools/lint_task_contract.py --task … --allowed-builder-classes avkit_coordinator`: `OK: 26 row(s); … 24 row(s) fully checked …` (`C:/Temp/av-kit/s65/corr/lint-task-r1corr.txt`).
- The AC probe still lists 28 ACs, AC-137.1 to AC-139.9 (`C:/Temp/av-kit/s65/corr/ac-probe-r1corr.txt`).
- Blast-radius census: 12 values changed, 13 variants swept, 12 sites found, 11 updated, 1 confirmed consistent. The one left is D-635's chosen text, "always shown", which `SABR_SHOWN` now defines (`C:/Temp/av-kit/s65/corr/census-r1.txt`).

Status: corrections_applied. An independent recheck (round 2) follows; this section does not approve.


## Recheck (Round 2)

Date: 2026-11-12. Reviewer: codex-independent-reviewer (Codex/OpenAI); author: Claude Code/Anthropic. Review mode: plan. **Verdict: changes_required. Intent achieved: partial.** One High blocking behavior finding remains, carried as F1; F2 and F3 are fixed. The historical round-1 prose above is retained, with only its Findings Status cells updated. This section is the current assessment.

### Recheck Result

| Finding | Status | Evidence |
|---|---|---|
| F1 | partial | Plan:123/.127/.133/.135 now clean before scrubbing, and the original three counterexamples pass. However, whitespace controls become spaces: `co\x85okie=SECRET` and `co\u2028okie=SECRET` become `co okie=SECRET`. The literal `YTDLP_LINE` detail passed to the real `HealthService._process` retains `SECRET` in both ring and stdout. AC-137.7/.9 add the three original forms but do not cover these surviving splits. |
| F2 | fixed | Plan:144-146/.202/.360 and task:65/.67 explicitly adapt the constructor walk and both exact-type pins. The modeled extended inventory passes 27/27 constructor cases. The moved assertions fail by AssertionError on the old base error and pass on the required subclass; the actual red-check parser accepts both full names and refuses a missing required test. |
| F3 | fixed | Plan:194-195/.228/.231/.358 and task:68/.70-71 separate the staged dependencies. The real old scanner matches the revised GVS warning (row 3), misses the captured warning (row 2b), and the literal final matcher recognizes it (row 4). AC-138.2 and AC-138.5 retain the moved phrase/classification and captured-download proofs. |

### New Findings

| Finding | Severity | Blocking | Kind | Finding details | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| none | — | no | — | No new finding id. The surviving cleaning/scrubbing defect remains F1. | — | — | fixed |

### Remaining F1 — whitespace controls still hide sensitive text

**High, High confidence; blocking; subject: deliverable; kind: behavior.** Mechanisms: `CLEAN_LINE`, `FAILURE_LOG`, `YTDLP_LINE`, `redact_message`, `console_field`. Violates **AC-139**, specifically AC-139.5's redaction contract on the real Console stack; the same expression also remains unsafe for a port-supplied `DownloadFailedError.detail` (AC-137.7/.9).

At `implementation-plan.md:123`, step 2 turns both U+0085 (Cc, whitespace) and U+2028 (Zl, whitespace) into a space. Step 3 cannot remove them afterward. With either separator inside `cookie`, `redact_message(clean_line(raw))` at `:135` returns `co okie=SECRET`; the real `console_field` and `HealthService._process` keep it. The independent probe passed two such warning events through the actual processor, using an in-memory instance, captured stdout and no log-file writes: both ring messages and stdout contain `detail=co okie=SECRET`. This is the production logger-to-Console path specified by `YTDLP_LINE`, not just a storage fake or a grep claim. Splitting `https://` or the synthetic home name the same way likewise leaves `e.example/private` or the home marker visible in the literal scrubber pipeline. Relevant current source: `packages/core/src/avkit_core/services/health.py:76` (`redact_message`) and `:125` (`console_field`).

The original NUL/ANSI ordering defect is corrected; this is the unfinished safety boundary explicitly requested by R1. Moving whitespace normalization ahead of `safe_reason` also converts an original line boundary into an ordinary space. The proposed classifier at plan:125 does select a line with `splitlines()` before cleaning, so **that adapter-detail route does not carry the suffix after U+0085/U+2028 into storage**. That protection does not apply to `YTDLP_LINE`, which cleans the whole logger text, or to another port's supplied detail. D-638 at plan:655 and the meaning bullet at :105 therefore overclaim that no control can hide a needle after the correction.

Recommendation: define scrubbing/recognition for these whitespace-split inputs before retaining the joined text, while preserving AC-137.4's readable whitespace outputs and the original first-line contract. Add U+0085/U+2028 negatives for the affected storage/API and warning-to-Console paths, with the existing positive controls; then align D-627/D-638 and the meaning bullets with that policy. Do not close F1 based only on the three now-passing original forms.

### R1 — cleaning and redaction

The corrected stored-reason expression produces `[REDACTED]`, `[link]` and `~/v.mp4` for the three requested synthetic examples. `redact_message` returns `[REDACTED]` without a leading space when the needle starts the string; a retained prefix supplies the separating space. `detail` intentionally retains URLs/home paths until `console_field` replaces them. Zero-width and bidi marks (Cf) now disappear before recognition. U+0085/U+2028 survive as spaces and defeat recognition, as F1 explains. All 11 AC-137.4 example groups follow from the four steps; a sweep containing all 1,114,112 Python code points cleaned and UTF-8 encoded without error. This is bounded supporting evidence for the total function, not an implementation pass.

`FAILURE_LOG`, `SABR_LOG` and `YTDLP_LINE` consistently use clean-then-redact; that consistency also shares the remaining whitespace weakness. AC-137.7 now specifies storage checks for the NUL-cookie, NUL-URL and ANSI-home forms; AC-137.9 specifies the served error, ring and stdout checks for those forms. Neither AC currently specifies the two whitespace-split cases.

### R2 — constructors, pins and Red matching

`ERROR_ARGS` supplies both arguments to the new class while leaving all 26 existing error constructors covered. The two moved download pins keep `pytest.raises(DomainError)`, so the old base class reaches an assertion failure; after `FAILURE_RAISE`, exact subtype, cause and `boom` detail agree. Row 2a includes the entire adapter pin file and both full-name `--require` arguments. The actual `_title_matches` and receipt parser accept those names, including parameterized titles; a missing required name is refused. These are modeled assertions/receipt probes, not executions of the unmodified product tests.

The fresh grep found no additional all-domain constructor walk or download exact-type/string pin. `test_domain_capture.py:357` walks only `CAPTURE_ERRORS`; the exact DomainError pins in `test_transcript_adapter.py:272/:406` concern transcripts; `test_youtube_adapter.py:709/:715/:720` pin `extract_info` failures, which this plan preserves. The two affected download pins remain exactly `:472` and `:736`.

### R3 — independent MEU Green stages

Row 3 can satisfy the revised AC-137.5 without `SABR_MATCH`, and the real old scanner sets `sabr_detected=True` on AC-137.6's GVS warning, permitting the `no_format` → `refused` override. Its phrase-only branch deliberately calls the None-returning stub until row 4. In row 2b the moved AC-138.2 phrase-only assertion sees `other`, and AC-138.5's captured-warning/download assertion sees `no_format`; both can fail by assertion. The final matcher then enables both in row 4 without changing the classifier's expectations. Q1's first goal trace is explicitly retained by AC-138.5 and continues through AC-137.7/.9/.10 to stored text, Console and card.

### R4 — correction compatibility and census

Apart from F1's remaining whitespace exposure, no additional delivery regression was established. D-627 and D-638 agree with the four-step order, though D-638's safety claim needs the F1 correction. Positional SABR fakes remain valid; the panel is checked after opening Advanced with `toBeVisible`; AC-122.16 now requires an empty debug-off event capture. The current plan/task SHA-256 hashes match the correction receipt's prefixes, and the edit script's data inventories 32 plan replacements and 9 task replacements. Its mutating entrypoint was never invoked. The named census and correction bullets were read; accepted prior scope and decisions were not reopened.

The supplied task lint receipt says `OK: 26 row(s); ... 24 row(s) fully checked ...`; a fresh read-only audit confirms 26 unchecked rows, dependency order and immediate native exit captures for rows 1/2a/3/4. Row 2a's file list and full-name requirements match its deliverables. The plan still declares exactly 28 distinct AC rows: 11 for MEU-137, 8 for MEU-138 and 9 for MEU-139. No task validation command was executed.

### Round 2 Checklist Results

| Check | Result | Command / procedure | Exit | Evidence |
|---|---|---|---|---|
| PR-1/PR-4 staged pins and dependencies | pass | `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s65/review/recheck_r2.py` | 0 | 27/27 modeled constructor entries; moved assertions and full-name matcher verified; old/new SABR observations agree with staged rows. |
| PR-8 retained-text safety | fail | Same bounded probe; actual Console processor with in-memory collaborators | 0 | Both U+0085/U+2028 warning details expose `SECRET` in ring/stdout. Exit 0 means the counterexample probe completed. |
| PR-3/PR-6/PR-9 corrections and adjacent clauses | pass | Manual comparison of contracts, pins, Guards, D-627/D-638, correction bullets/receipts and task rows; observer codex-independent-reviewer | null | Corrected order and dependencies are explicit; F1 is a behavioral failure, not a conflicting spelling. |
| R4 counts/command audit | pass | `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s65/review/audit_r2.py` | 0 | 32/9 edit-pair inventory, matching current hashes, 26 unchecked task rows; 28 ACs counted by recheck_r2.py. |
| Red-check parser selftest | pass | `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-11-download-failure-visibility/red-check.py --selftest` | 0 | 44 fixtures (13 positive, 31 negative), 0 wrong. |
| Identity selftest | pass | `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-11-download-failure-visibility/identity.py --selftest` | 0 | 0 failures. |
| Product Reds/Greens, Electron, baseline/full session gate | n/a | Not run under the read-only review instruction | null | No product-suite pass claimed. |

### Round 2 Durable Evidence

```json
{"schema_version": "evidence.v1", "check_id": "s65-r2-literal-contract-recheck", "command": "rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s65/review/recheck_r2.py", "cwd": "P:/av-kit", "scope": "R1-R4 offline proposed-contract probes; real scrubbers/Console; staged scanner and pin assertions", "phase": "targeted", "exit_code": 0, "result": "fail", "tested_state": "plan SHA-256 4a17f4f3db754667e9bf08742511ec8f43895cbf249bec516b19a41005e56ec1; task SHA-256 7da502e0274ccf579b7d530ecebfb1d1f5939b60c08289b9b86e2437052eb412; proposed contracts plus current imported scrubbers/Console processor, not product implementation", "fresh": true, "output": "Original forms: [REDACTED], [link], ~/v.mp4. Cf split forms redact. U+0085/U+2028 produce co okie=SECRET in reason/detail/Console; actual HealthService._process retains both in ring/stdout. All 11 CLEAN_LINE example groups pass; all 1114112 code points clean and UTF-8 encode. ERROR_ARGS 27/27; full-name synthetic Red receipt accepted; missing-required negative refused. Old scanner GVS=True, captured=False; final matcher missing a url. 28 ACs (11/8/9). Exit 0 certifies probe completion, not redaction safety."}
```

Probe receipts: `C:/Temp/av-kit/s65/review/recheck-r2.txt`, `audit-r2-final.txt`, `red-selftest-r2.txt` and `identity-selftest-r2.txt`. Python ran with `PYTHONDONTWRITEBYTECODE=1`; final selftests also set TMP/TEMP to the review scratch directory. Imports/probes started no backend or server and made no network call. No repository write or product test was performed. Scratch helper-development failures were corrected before the successful audit; they are not product failures.

### Verdict

`changes_required` — F1 remains partially fixed with a reproduced High retained-text exposure; F2/F3 are fixed. Correct the remaining whitespace-split recognition and recheck within the existing ledger. D-625 and execution authorization remain Mat's at the gate. Actual runtime behavior and product validation remain unobserved.

Complete rolling report: `C:/Temp/av-kit/s65-plan-review-round-2.md`. The coordinator owns validation and the canonical copy; this reviewer did not edit that path.

## Corrections Applied — 2026-11-12 (round 2)

Plan summary: the three MEUs, their 28 ACs and the row order are unchanged. Round 2's remaining F1 (a whitespace character other than U+0020 inside a needle, a link or the home path) is corrected in `implementation-plan.md` and `task.md`, with the matching new name in `red-check.py`'s `DECLARED_NEW` and `baseline.ps1`'s absence list. No production code or test was written. D-625 is recorded as ruled. Authority: Mat, USER_EXPLICIT 2026-11-12 "Fix F1 to F3, increase token buget by 30M and continue the loop until approved. If you need decisions answerd have Fable subagent do rulling and accept it as if it was coming from human".

Changes made, by file:

- `implementation-plan.md`, F1 (round 2):
  - A new contract, `SCRUB_LINE`: `scrub_line(text)` in `services/download.py`. It takes `readable = clean_line(text)` and `joined`, which is `clean_line` of `text` after every whitespace character other than U+0020 is removed. With `scrub(x) = redact_message(replace_links(scrub_home(x)))` (`console_field`'s order without its cut), it returns `scrub(joined)` when that differs from `joined`, and `scrub(readable)` otherwise.
  - A needle and a URL hold no whitespace, and the home folder is matched as written. So every needle, link and home folder that is whole, or split by U+0085, U+2028, a tab, a line break or another non-U+0020 whitespace character, or by a code point `clean_line` drops, is whole in `joined`.
  - A plain space still splits a word, as it does today. When nothing is scrubbed, the readable form is kept, so AC-137.4's readable outputs hold.
  - `CLEAN_LINE` now says that no site scrubs its output directly, and that every site goes through `SCRUB_LINE`.
  - The sites now read as follows:
    - `FAILURE_LOG`: `detail` is `scrub_line(raw)`, and the `other` reason is `safe_reason(scrub_line(raw)) or type(exc).__name__`.
    - `SABR_LOG`: `error` is `scrub_line(str(exc))`.
    - `YTDLP_LINE`: `detail` is `scrub_line(str(text))`.
  - The meaning bullet, §Where values go (the yt-dlp error, the SABR check and the logger lines), D-627 (chosen and reasoning) and D-638 (chosen and reasoning) say the same. D-638 no longer claims that cleaning alone closes every split.
  - New cases in the ACs:
    - AC-137.4 gains `SCRUB_LINE` cases: `"co\x85okie=SECRET"` and `"co\u2028okie=SECRET"` → `"[REDACTED]"`; `"https:\u2028//e.example/private"` → `"[link]"`; the marker home with `\x85` inside its user name → `"~\\v.mp4"`; `"a\tb cookie=X"` → `"ab [REDACTED]"`; `"a\u2028b"` → `"a b"`; `"co okie=x"` unchanged; `""` and a lone `\ud800` → `""`.
    - AC-137.7 gains the storage negatives for `co\x85okie=SECRET`, `co\u2028okie=SECRET`, `https:\u2028//e.example/private` and a home path split by `\x85`.
    - AC-137.8's `detail` is `scrub_line(raw)`.
    - AC-137.9 gains a third job (home split by `\x85`, URL split by `\u2028`, cookie split by `\x85`) and a fourth (`co\u2028okie=SECRET`), each checked in the ring, stdout and the served `error_message`.
    - AC-139.5 gains two warnings through the real Console stack: home split by `\u2028` with `co\x85okie=SECRET`, and `https:\x85//…` with `co\u2028okie=SECRET`. They keep AC-137.9's positive control.
  - §Files Modified names `scrub_line` (`SCRUB_LINE`) in `services/download.py`, which is already in the gate's scope. The row 1 stub list adds `scrub_line` returning its input, so AC-137.4's new cases fail by assertion in row 2a.
- `implementation-plan.md`, D-625 recorded as B:
  - The decision entry: `chosen` "B: run all three MEUs with no context-measured split; …", with the Fable subagent's reasons in `reasoning`. Its `human_message_reference` is `USER_EXPLICIT 2026-11-12 'If you need decisions answerd have Fable subagent do rulling and accept it as if it was coming from human' — ruled by the Fable subagent: B`.
  - The Status line, the split paragraph (now "No split point (D-625 B)"), §User Review Required, the WP-5 and WP-7 rows, the S13 stop condition (retired) and the decision intro all say the same.
- `task.md`:
  - The header says that `scrub_line` is stubbed.
  - The D-625 note says B: no split and no Session 65b.
  - Row 1 adds the `scrub_line` stub.
  - Row 3 writes `SCRUB_LINE`, and its D-625 clause becomes "record the context state … and go on".
  - Row 3's deliverables name `SCRUB_LINE`.
  - The MEU-139 header loses "skipped under the D-625 split".
  - H1-6 says "D-625's ruling (B)", H2-2 says D-625 was ruled by Fable under Mat's delegation, and H2-6 loses the 65b branch.
- `red-check.py`: `scrub_line` is added to `DECLARED_NEW`.
- `baseline.ps1`: `scrub_line` is added to the S11 absence list for `services/download.py`.

Verification results:

- `C:/Temp/av-kit/s65/corr/apply_r2_corrections.py` made the edits. It replaces each old text exactly once, after a dry run over all four files (`apply-r2-dry.txt`, `apply-r2.txt`): 36 plan edits, 10 task edits, 1 red-check edit and 1 baseline edit. All four files are still LF only.
- `C:/Temp/av-kit/s65/corr/probe_scrub_line.py` ran the contract as written on the real `redact_message`, `scrub_home`, `replace_links`, `safe_reason` and `console_field`, with the home patched to a marker and no repository write (`probe-scrub-line.txt`, exit 0):
  - all 49 listed cases pass, which covers every AC-137.4, AC-137.9 and AC-139.5 output above and the round 1 forms;
  - `co<ch>okie=SECRET` is redacted for each of 22 whitespace and format characters;
  - a sweep over all 1,114,112 code points, each one put inside `cookie`, ends `failures=0`. U+0020 stays a split by contract.
- `tools/lint_task_contract.py --task … --allowed-builder-classes avkit_coordinator` printed `OK: 26 row(s); … 24 row(s) fully checked …` (`lint-task-r2corr.txt`).
- `red-check.py --selftest`: `44 fixture(s) (13 positive, 31 negative), 0 wrong` (`red-selftest-r2corr.txt`).
- The rulings, shapes and anchors blocks of `baseline.ps1` ran alone (`C:/Temp/av-kit/s65/plan_probe_baseline_steps.py`):
  - The rulings block printed `D-625: chosen starts 'B:', reference starts 'USER_EXPLICIT 2026-11-12', ruled=True` and `probe ruled exit=0`.
  - The shapes block printed `absent scrub_line: … lines []` and `shapes wrong (S11): []` (`C:/Temp/av-kit/s65-plan-rulings-probe.txt`, `s65-plan-shapes-probe.txt`).
- The census (`census_r2.py`, `census-r2.txt`, exit 0) found:
  - 15 old values, 0 hits;
  - 12 new values, each present;
  - the decision log YAML parses with 17 entries, D-622 to D-638;
  - 28 ACs.
  - The remaining "65b" and "split" lines are each read and are either intended or code: option A's historical text, D-625's question and the task note's "no Session 65b".

Status: corrections_applied. An independent recheck (round 3) follows; this section does not approve.

## Recheck (Round 3)

Date: 2026-11-12. Agent: codex-independent-reviewer (Codex/OpenAI), independent of Claude Code/Anthropic, the plan's author. Review mode: plan. **Verdict: changes_required. Intent achieved: partial.** One High blocking behavior finding remains as F1; no Critical finding or new finding id. This section is the current assessment; rounds 1 and 2 and both Corrections Applied sections above are preserved.

### Recheck Result

| Finding | Status | Evidence |
|---|---|---|
| F1 | partial | The four requested split examples pass, as do 207,180 isolated interior-split probes. However, `SCRUB_LINE` at plan:124 can remove the left boundary required by `scrub_home`. `at\tC:\Users\ReviewMarker\v.mp4 cookie=SECRET` keeps `atC:\Users\ReviewMarker\v.mp4 [REDACTED]`; the real Console ring/stdout retain the home marker. A home additionally split by U+0085 has the same result. |
| F2 | fixed | Plan:145-147 retains the constructor argument map and both exact-subtype pin moves; task:59/:61 schedules them before their Green checks. The round-2 edit inventory does not modify these accepted corrections. |
| F3 | fixed | Plan:125/:195-196/:231/:358 retains the staged classifier/scanner arrangement and the later captured-warning proof; task:62/:64-65 preserves the order. Adding `scrub_line` creates no new dependency on MEU-138. |

### New Findings

| Finding | Severity | Blocking | Kind | Finding details | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| none | — | no | — | No new finding id; the remaining retained-text exposure is F1. | — | — | fixed |

### Remaining F1 — joined-form selection can bypass home scrubbing

**High severity, High confidence; blocking; subject: deliverable; kind: behavior; violates AC-139** (AC-139.5's retained-text redaction). The same stored-reason expression also violates AC-137.7/.9. Mechanisms: `SCRUB_LINE`, `scrub_home`, `FAILURE_LOG`, `YTDLP_LINE`.

At `implementation-plan.md:124`, `joined` removes every non-U+0020 whitespace character throughout the line. But `scrub_home` requires a left boundary: `packages/core/src/avkit_core/services/health.py:108-120` refuses a home prefix immediately following a word character. For a marker home `C:\Users\ReviewMarker`, run the literal contract on:

```text
at\tC:\Users\ReviewMarker\v.mp4 cookie=SECRET
```

Here `\t` denotes an actual tab. Joining changes `at<TAB>C:` into `atC:`, so home recognition fails. The later cookie is redacted, making `scrub(joined) != joined`; that unrelated change selects the unsafe joined result even though scrubbing the readable form would remove the home. Observed outputs:

```text
scrub_line:       atC:\Users\ReviewMarker\v.mp4 [REDACTED]
stored formula:  Download failed: atC:\Users\ReviewMarker\v.mp4 [REDACTED].
Console ring:    yt-dlp detail=atC:\Users\ReviewMarker\v.mp4 [REDACTED]
captured stdout: contains ReviewMarker
```

Replacing the tab with U+0085 or U+2028 gives the same exposure. Each also fails with U+0085 inserted inside `ReviewMarker`: the joining reconstructs the sensitive home text while destroying its boundary. All six counterexamples were asserted. The real `HealthService._process` was exercised with an in-memory ring, disabled file logging and captured stdout. Neither its second `console_field` scrub nor its final `redact_message` removes the marker. The proposed storage expression was evaluated directly; no SQLite write or HTTP request was performed.

This is a demonstrated regression in the correction's new selection rule: Session 50's unchanged `console_field` on the original tab/unbroken-home input returns `at<TAB>~\v.mp4 [REDACTED]`. It is not a request to change Session 50's accepted home-matching semantics. Relevant plan sites: `:124` (`SCRUB_LINE`), `:128` (`FAILURE_LOG`), `:136` (`YTDLP_LINE`), `:197`/`:199` (storage/API negatives), `:266` (Console negatives), `:655-656` (D-638).

Recommendation: preserve the home scrubber's boundary recognition when removing split characters, and ensure choosing a joined result cannot undo a readable-form redaction. Add this mixed-context case, including a split home, to AC-137.4/.7/.9 and AC-139.5. Verify the kept value and real ring/stdout, with the positive control. Retain the agreed readable outputs and U+0020 policy.

### R1 — scrub contract and observables

The requested inputs produce `[REDACTED]`, `[REDACTED]`, `[link]` and `~\v.mp4`. `"a\u2028b"` produces `"a b"`; `"a\tb cookie=X"` produces `"ab [REDACTED]"`. All 207,180 isolated interior-split probes across all five current needles, a URL and the marker home passed, using every non-U+0020 whitespace and Cc/Cf/Cs code point plus an ANSI CSI sequence. Those successes do not close the mixed-context counterexample above. Inspection finds total string operations; all 1,114,112 code points singly inside a needle and the concatenated alphabet cleaned, scrubbed and UTF-8 encoded without exception. This is bounded supporting evidence, not a proof by enumerating every possible string or a product implementation pass.

The plain U+0020 exception is stated plainly at plan:105/:124/:656 and tested at :194. Keeping `co okie=x` is acceptable against the goal and Session 50's existing literal-needle behavior. `FAILURE_LOG`, `SABR_LOG` and `YTDLP_LINE` consistently use `SCRUB_LINE` (:128/:134/:136), so they share its remaining defect. AC-137.7 now checks split storage; AC-137.9 checks served `error_message`, ring and stdout; AC-139.5 checks warnings through `/health/console` and captured ring/stdout. Their prescribed ordinary-space prefixes miss the boundary-destruction case.

### R2 — compatibility, rows and correction records

Apart from F1's new joined-form selection defect, no regression in an accepted contract was established. Row 1 declares `scrub_line` as an identity stub; seven of AC-137.4's nine new examples fail that stub by assertion, while unchanged-space/empty characterizations pass. Row 2a requires `test_ac_137_4`; row 3 implements `SCRUB_LINE` before its use. The prescribed new examples pass the literal final algorithm. Actual product Red/Green tests were not run. `DECLARED_NEW` contains `scrub_line` once (`red-check.py:66`); S11 has the service absence entry (`baseline.ps1:138`), and the name is currently absent from production. A fresh permitted Red-check selftest returned **44 fixtures (13 positive, 31 negative), 0 wrong**.

The audit loaded only the correction script's literal edit data, never its mutating entrypoint: all 36 plan, 10 task, one Red-check and one baseline changes are present; all four current hashes match the supplied `apply-r2.txt` prefixes and all remain LF. D-625 B is consistent in plan status, work packages, chosen option/reference, retired S13 and task header/note/rows; historical unchosen A text is explicit. The task lint receipt reports **26 rows; 24 fully checked; two view_file exemptions; dependencies acyclic**. A fresh census confirms **26 unchecked rows and 28 unique ACs (11/8/9)**. The supplied census and correction dispositions were read. No task validation command, baseline block, product suite or session gate was executed.

### Round 3 Checklist Results

| Check | Result | Command / procedure | Exit | Evidence |
|---|---|---|---|---|
| R1 / PR-8 retained-text safety | fail | `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s65/review/recheck_r3.py` | 0 | Requested isolated cases pass; six mixed-context inputs retain ReviewMarker in kept value, modeled stored reason and actual Console ring/stdout. Exit 0 means the counterexample diagnostic completed. |
| R2 / PR-1, PR-3, PR-4, PR-6, PR-9 compatibility | pass | `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s65/review/audit_r3.py`; manual comparison of edited contracts, neighboring clauses and correction census; observer codex-independent-reviewer | 0 | All 36/10/1/1 edits present; hashes match apply receipt prefixes; row/stub/absence/DECLARED_NEW alignment; D-625 B consistent; lint receipt inspected. |
| Red-check selftest | pass | `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-11-download-failure-visibility/red-check.py --selftest` | 0 | 44 fixtures, 13 positive, 31 negative, 0 wrong. |
| AV-1 to AV-5 implementation proofs | n/a | Planning-only recheck; no implementation exists | null | Modeled assertions are identified as probes, not product test results. |
| AV-6 and accepted plan scope | pass | Manual inspection of D-627/D-638, source labels and unchanged accepted rulings; observer codex-independent-reviewer | null | No new source or scope dispute; D-625 delegation accepted as instructed. |
| Product suites, baseline, gate, network and runtime launch | n/a | Forbidden by the read-only review instruction | null | None run. No repository file written. |

### Round 3 Durable Evidence

```json
{"schema_version":"evidence.v1","check_id":"s65-r3-scrub-contract","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s65/review/recheck_r3.py","cwd":"P:/av-kit","scope":"literal CLEAN_LINE/SCRUB_LINE; real Session 50 helpers and in-memory HealthService processor; current plan AC/task census","phase":"targeted","exit_code":0,"result":"fail","tested_state":"plan sha256 b8e9f1ebb92d03b65c1d1d5b5b96a4c8949340d1fe71805bcf4f420bcecbb04f; task sha256 b8e4d4c8bdf045066f979942c05aca3bf3bfd3aa25b0d9874e56f81f8d0cd791; proposed contract, unchanged real scrubbers/Console; not implemented product","fresh":true,"output":"Requested four forms pass; readable outputs pass; 207180 isolated splits pass across 2301 whitespace/drop code points plus ANSI. 1114112 code points plus concatenated alphabet encode without exception. Six mixed-context probes retain ReviewMarker in kept text, modeled stored reason and actual ring/stdout. Example: at<TAB>C:\\Users\\ReviewMarker\\v.mp4 cookie=SECRET -> atC:\\Users\\ReviewMarker\\v.mp4 [REDACTED]. Session50 original-input positive control scrubs the unbroken home. 28 ACs=11/8/9; 26 unchecked rows. Diagnostic exit 0 does not mean safety passes."}
```

```json
{"schema_version":"evidence.v1","check_id":"s65-r3-correction-audit","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s65/review/audit_r3.py","cwd":"P:/av-kit","scope":"current plan/task/red-check/baseline text and supplied correction/lint data","phase":"static","exit_code":0,"result":"pass","tested_state":"plan b8e9f1ebb92d; task b8e4d4c8bdf0; red-check 88945fcaebdd; baseline b87e6fca34d9","fresh":true,"output":"36/10/1/1 edit data present, LF only, hashes match apply receipt prefixes; scrub_line declared once and S11 absence entry exists; production name absent; rows 1/2a/3 aligned; seven identity-stub assertion failures and two passing characterizations. Inspected lint receipt: 26 rows, 24 fully checked, two exemptions, dependencies acyclic. D-625 B consistent; F2/F3 correction data untouched."}
```

```json
{"schema_version":"evidence.v1","check_id":"s65-r3-red-check-selftest","command":"rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-11-download-failure-visibility/red-check.py --selftest","cwd":"P:/av-kit","scope":"plan-local receipt-parser fixtures","phase":"targeted","exit_code":0,"result":"pass","tested_state":"red-check sha256 88945fcaebdd5cc489edfaa82378d0cdf959f97fa1bee933a6fabe3d16217dd7","fresh":true,"output":"red-check selftest: 44 fixture(s) (13 positive, 31 negative), 0 wrong: []"}
```

Fresh receipts: `C:/Temp/av-kit/s65/review/recheck-r3.txt`, `audit-r3.txt`, `red-selftest-r3.txt`. Python ran with `PYTHONDONTWRITEBYTECODE=1`; the selftest's TMP/TEMP were under the review scratch directory. No network call, actual HTTP request, production test, backend/MCP server or repository mutation occurred. Forbidden paths were not opened. No memory-derived project fact was used.

### Verdict

`changes_required` — F1 remains partial with a reproduced High home-marker exposure caused by the new joined-form selection; F2/F3 remain fixed. The goal is only partially secured by this plan. This is ledger round 3, the configured initial plan cap: preserve the finding and ask the coordinator to apply the existing ledger's continuation rules; this reviewer does not start a new loop or make corrections. Runtime implementation and product validation remain unobserved.

Complete rolling report: `C:/Temp/av-kit/s65-plan-review-round-3.md`. The coordinator validates and copies this report to the canonical path. This reviewer wrote only under `C:/Temp/av-kit`.


## Corrections Applied — 2026-11-12 (round 3)

Plan summary: the three MEUs, their 28 ACs and the row order are unchanged. Round 3's F1 is corrected in `implementation-plan.md` and `task.md`. Removing a tab, U+0085 or U+2028 just before a home path joined it to the word before, so `scrub_home`'s left boundary failed, and the joined form was chosen whenever a cookie or a link was also scrubbed. No production code or test was written. `red-check.py` and `baseline.ps1` are unchanged, because the new helper is private to `scrub_line`. Authority: Mat, USER_EXPLICIT 2026-11-12 "Fix F1 to F3, increase token buget by 30M and continue the loop until approved". The ledger loop was continued by 2 rounds (`C:/Temp/av-kit/s65/corr/ledger-continue-r3.txt`: "+2 round(s) … rounds 3/5").

Changes made, by file:

- `implementation-plan.md`, the `SCRUB_LINE` row (F1, round 3). The contract now runs in four steps:
  1. `marked`: each ANSI CSI sequence becomes `\x00`; each `str.isspace()` character other than U+0020 becomes `\t`; each other `Cc`, `Cf` or `Cs` code point becomes `\x00`.
  2. `homed`: the private `_scrub_split_home` replaces the home folder with `~`. It matches as `scrub_home` does, with the same parts, separators, left boundary and case rule, but allows any run of `\t` and `\x00` between any two characters. Its right boundary is a gap run then a separator or a quote, or a run of gaps and spaces then the end. It reads `health.home_folder()` through the module at each call, because tests patch `health_module.home_folder` (`tests/unit/test_services.py:3313`).
  3. `readable = clean_line(homed)` and `joined = clean_line(homed.replace("\t", ""))`.
  4. It returns `scrub(joined)` when that differs from `joined`, else `scrub(readable)`, as in round 2.
  - The home step runs before anything is removed. Its left boundary is therefore the character the line really has, and choosing `joined` can't undo the match.
  - On a text with no `\t`, no `\x00` and no trailing space, the step gives exactly `scrub_home`'s result. Session 50's kept cases stay kept: a home joined straight onto a word character, `.`, `/`, `~` or `-`, or followed by a space and then more text.
- `implementation-plan.md`, the other sites:
  - The meaning bullet and §Where values go state the new order, and the traced forms add a home path after a tab or a NUL in a line where a cookie is also scrubbed.
  - §Files Modified names `_scrub_split_home` beside `scrub_line`, in `services/download.py`, which is already in the gate's scope.
  - D-627 `chosen` names the first step. Its `reasoning` adds round 3: fixing the joined form's boundary afterwards lost, because a split inside the home name and one before it are the same character, and only the home folder's own text tells them apart.
  - D-638 `reasoning` adds "matches the home folder before anything is joined (round 3 F1)".
- `implementation-plan.md`, the ACs (Codex's recommendation: the mixed case, including a split home, in AC-137.4, .7, .9 and AC-139.5):
  - AC-137.4: `"at\t<marker>\\v.mp4 cookie=SECRET"`, the same with `\x85` inside the marker's user name, and `"at\x00<marker>\\v.mp4 cookie=SECRET"` each → `"at~\\v.mp4 [REDACTED]"`. `"at\t<marker>\\v.mp4"` → `"at ~\\v.mp4"`. `"x<marker>\\v.mp4"` and `"<marker>2\\v.mp4"` are unchanged, as `scrub_home` keeps them.
  - AC-137.7: `at\t<home split by \x85>\\v.mp4 cookie=SECRET` stores `Download failed: at~\\v.mp4 [REDACTED].` with no home marker and no `SECRET`.
  - AC-137.9: a fifth job, `DownloadFailedError(other, "ERROR: x at\t<HOME-marker split by \x85>\\v.mp4 cookie=SECRET")`, checked in the ring, stdout and the served `error_message`, with the existing positive control.
  - AC-139.5: `WARNING: at\u2028<HOME-marker>\\v.mp4 cookie=SECRET` shows `at~` and ` [REDACTED]`, with no marker or `SECRET` in the ring or stdout.
  - Every round 2 output (`"a\u2028b"` → `"a b"`, `"a\tb cookie=X"` → `"ab [REDACTED]"`, `"co okie=x"` unchanged, the split needles, links and homes) is kept, and so is the U+0020 policy.
- `task.md`: row 3 writes `SCRUB_LINE` with its private `_scrub_split_home`, in the order: mark the split characters, match the home folder, clean, then scrub.

Verification results:

- `C:/Temp/av-kit/s65/corr/apply_r3_corrections.py` made the edits: a dry run first, then each old text replaced exactly once (`apply-r3.txt`: "implementation-plan.md: 12 edit(s)", "task.md: 1 edit(s)", both "LF only"). One follow-up Edit restored the comma before "a fourth" in AC-137.9.
- `C:/Temp/av-kit/s65/corr/probe_scrub_line_r3.py` ran the contract as written on the real `redact_message`, `scrub_home`, `replace_links`, `safe_reason`, `console_field` and `HealthService._process`, with the home patched to a marker and no repository write (`probe-scrub-line-r3.txt`, exit 0). It reports 48 `ok` lines and these lines:
  - "sweep1: 414360 probes over 2302 gap forms";
  - "sweep2: 60000 random mixed probes";
  - "parity: 20000 gap-free strings, scrub_split_home == scrub_home";
  - "totality: 1114112 code points plus the concatenated alphabet, no exception";
  - "failures=0".
  - Codex's six mixed-context inputs (a tab, `\x85` or `\u2028` before the home, with and without a split home, then `cookie=SECRET`) each leak nothing to the kept value, the stored reason, the ring or stdout (lines 44 to 49: `leaks: []`).
  - A probe hit is excused only when Session 50's `console_field` keeps the marker on the same text with no split.
- `lint-task-r3corr.txt`: "OK: 26 row(s); … 24 row(s) fully checked …".
- `red-selftest-r3corr.txt`: "red-check selftest: 44 fixture(s) (13 positive, 31 negative), 0 wrong: []".
- `census-r3.txt` (`census_r3.py`): no old wording, every new value present, the decision YAML parses ("17 entries, D-622 to D-638"), "ACs: 28 unique 28 split [11, 8, 9]", no mixed line endings, "census problems: 0".


## Recheck (Round 4)

Date: 2026-11-12. Agent: codex-independent-reviewer (Codex/OpenAI), independent of Claude Code/Anthropic, the author. Review mode: plan. **Verdict: approved. Intent achieved: yes, judged as a plan.** F1, F2 and F3 are fixed; no new High or Critical finding was established. This section is the current assessment. Earlier assessments and all three Corrections Applied sections remain historical, unchanged; only frontmatter and the top Findings table's Status cells were refreshed.

### Recheck Result

| Finding | Status | Evidence |
|---|---|---|
| F1 | fixed | `implementation-plan.md:124` matches the home on the marked text before either cleaned form is selected. All six round-3 mixed inputs now yield `at~\v.mp4 [REDACTED]`; the modeled stored message, real Console ring, captured stdout and in-memory persistence contain neither marker nor secret. AC-137.4/.7/.9 and AC-139.5 agree (`:194`, `:197`, `:199`, `:266`). Deterministic split sweeps and the multi-gap probe pass. |
| F2 | fixed | The constructor argument map and exact-subtype pin moves remain at plan `:145-147`, with row-1/row-2a placement at task `:59`/`:61`. The correction inventory leaves these accepted clauses unchanged. |
| F3 | fixed | Plan `:126`, `:195-196`, `:356-361` and task `:62`, `:64-65` retain the stub/scanner staging. The new helper needs only the existing Session 50 functions and `health.home_folder`; it adds no MEU-138 dependency to row 3. |

### New Findings

| Finding | Severity | Blocking | Kind | Finding details | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| none | — | no | — | None. | — | — | fixed |

### R1 — home recognition, observables and compatibility

Implemented the literal `SCRUB_LINE`/`CLEAN_LINE` rules independently in a scratch Python probe, including `_scrub_split_home`, using the real `redact_message`, `scrub_home`, `replace_links`, `safe_reason`, `console_field` and `HealthService._process`. Patched `health.home_folder` through the module to `C:\Users\ReviewMarker`; no real home path was read. The six requested tab/U+0085/U+2028 cases, with and without the interior U+0085, expose nothing in the kept value, stored-message formula, real ring or stdout. Error-level persistence was redirected into memory and also retains no marker. No SQLite write, HTTP call or production constructor was used.

No qualifying split bypass was found: **202,752** before/interior/after-home probes across **2,304** gap forms, **147,456** needle/link interior-split probes, and **50,000** seeded multi-gap mixed inputs pass. Gap forms include every non-U+0020 whitespace and Cc/Cf/Cs code point, complete ANSI CSI and mixed runs. The randomized check compares with Session 50 on the corresponding unsplit text. Literal fragments left by an incomplete/broken ANSI CSI are ordinary text, outside CLEAN_LINE's specified CSI removal; the multi-gap generator inserts complete sequences at original character boundaries.

On the home step's marked input with no tab, NUL or trailing space, its pattern reduces to Session 50's pattern: zero gaps, the same home parts/separators, boundaries and case flag. **40,000** gap-free comparisons across both case rules pass. The eight kept controls also pass with and without an unrelated cookie: a home directly after a word character, `.`, `/`, `~` or `-`, a longer user name, and a home followed by a space and further text (including a separator) remain kept. Positive controls confirm Session 50 scrubs an ordinary home and the original tab-before-home input.

The new AC outputs follow the contract: the mixed line gives `at~\v.mp4 [REDACTED]`; AC-137.7's stored formula is `Download failed: at~\v.mp4 [REDACTED].`; AC-137.9's fifth input keeps `ERROR: x at~\v.mp4 [REDACTED]`; AC-139.5 keeps `WARNING: at~\v.mp4 [REDACTED]`. With no further scrub trigger, `at<TAB><marker>\v.mp4` keeps the readable `at ~\v.mp4`. All earlier round-2 readable outputs and the agreed plain-space policy pass. Totality inspection found no partial string operation; all **1,114,112** individual code points plus their concatenated alphabet clean, scrub and UTF-8 encode without exception. These are contract probes and bounded adversarial evidence, not an implemented-product certification or enumeration of every possible string.

### R2 — correction inventory and execution order

The correction script was parsed as literal edit data only; its mutating entrypoint was never run. All **12 plan edits** (one contract row and 11 literal replacements) and **one task edit** are present, with old fragments absent; AC-137.9's comma follow-up is present. The affected sites and neighbors agree: plan `:105`, `:124`, `:154`, `:194`, `:197`, `:199`, `:266`, `:291`, `:490`, `:498`, `:656`; task `:62`. D-627/D-638 describe the revised ordering, the private helper is in Files Modified, and no accepted F2/F3 clause or unrelated mechanism was changed. `red-check.py` and `baseline.ps1` still match round 3's hashes.

Row 1 still makes `scrub_line` an identity stub; every newly added transforming AC-137.4 example fails that stub by assertion in row 2a, while kept/empty characterizations can pass. Nine transforming examples in the independent probe explicitly assert this negative control. Row 3 builds the private helper and SCRUB_LINE before use and forbids test edits. There remain **28 unique ACs (11/8/9)** and **26 unchecked task rows**, with no MEU-137/138/139 implementation handoff. The decision YAML parses as **17 entries, D-622 to D-638**. Inspected the supplied census, lint and Red-check receipts: census zero problems; lint 26 rows, 24 checked plus two read exemptions; selftest 44 fixtures, zero wrong. Those supplied checks were not represented as fresh executions. No regression in the previously accepted contracts was established.

### Round 4 Checklist Results

| Check | Result | Command / procedure | Exit | Evidence |
|---|---|---|---|---|
| R1 / PR-8 retained-text safety | pass | `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s65/review/recheck_r4.py` | 0 | Six original counterexamples safe through kept/stored-formula/ring/stdout; 202,752 home splits, 147,456 needle/link splits; 40,000 home-step parity cases; complete single-code-point totality sweep. |
| R2 / PR-1, PR-2, PR-3, PR-4, PR-6, PR-9 compatibility | pass | `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s65/review/audit_r4.py` | 0 | All 12/1 edits verified, unchanged F2/F3 staging and script hashes, 28 ACs, 26 pending rows, 17 decisions; 50,000 multi-gap mixed probes pass. |
| AV-2/AV-3/AV-6 contract verification | pass | Manual comparison of revised contract/ACs/task neighbors and the scratch probe's actual assertions; observer codex-independent-reviewer | null | Real Session 50 functions exercised; only home source patched. No assertion bypass, no scope reduction or new unsupported requirement found. |
| AV-1/AV-4/AV-5 implementation proofs | n/a | Unstarted-plan recheck; no product implementation or tests exist | null | Identity-stub negative control is a scratch assertion probe, not a product Red run. |
| Product suites, baseline/session gate, network, backend/MCP/GUI launch | n/a | Forbidden by this review's scope | null | None run. No repository file written; no forbidden path opened. |

### Round 4 Durable Evidence

```json
{"schema_version": "evidence.v1", "check_id": "s65-r4-scrub-contract", "command": "rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s65/review/recheck_r4.py", "cwd": "P:/av-kit", "scope": "literal proposed CLEAN_LINE/SCRUB_LINE; real Session50 functions and in-memory HealthService processor", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "docs/execution/plans/2026-11-11-download-failure-visibility/implementation-plan.md sha256 2c155f005bf8b5a654708538b1d7e7082bfb5d14fdeafa33f559de69f9eaac88; docs/execution/plans/2026-11-11-download-failure-visibility/task.md sha256 df79f34d3f606c88a30e369d3218e2ce93425544934cbd8c414902ee96ba6a95; docs/execution/plans/2026-11-11-download-failure-visibility/red-check.py sha256 88945fcaebdd5cc489edfaa82378d0cdf959f97fa1bee933a6fabe3d16217dd7; docs/execution/plans/2026-11-11-download-failure-visibility/baseline.ps1 sha256 b87e6fca34d9069663d591e628cb57890ac57e6c41d42d977f5a7df219b99c77", "fresh": true, "output": "Six mixed counterexamples safe in kept value, modeled stored message, actual ring/stdout and in-memory persistence. 202752 home-gap and 147456 needle/link-gap probes PASS across 2304 gap forms; 40000 home-step parity cases across both case rules PASS. Eight kept controls x plain/cookie PASS. 1114112 individual code points plus concatenated alphabet clean/scrub/UTF8 PASS. Nine identity-stub assertions fail as intended. No product implementation or API/SQLite execution."}
```

```json
{"schema_version": "evidence.v1", "check_id": "s65-r4-correction-audit", "command": "rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s65/review/audit_r4.py", "cwd": "P:/av-kit", "scope": "current plan/task, literal correction inventory, supplied receipts and seeded multi-gap contract probe", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "docs/execution/plans/2026-11-11-download-failure-visibility/implementation-plan.md sha256 2c155f005bf8b5a654708538b1d7e7082bfb5d14fdeafa33f559de69f9eaac88; docs/execution/plans/2026-11-11-download-failure-visibility/task.md sha256 df79f34d3f606c88a30e369d3218e2ce93425544934cbd8c414902ee96ba6a95; docs/execution/plans/2026-11-11-download-failure-visibility/red-check.py sha256 88945fcaebdd5cc489edfaa82378d0cdf959f97fa1bee933a6fabe3d16217dd7; docs/execution/plans/2026-11-11-download-failure-visibility/baseline.ps1 sha256 b87e6fca34d9069663d591e628cb57890ac57e6c41d42d977f5a7df219b99c77", "fresh": true, "output": "12 plan edits (contract row + 11 replacements), one task edit present, old fragments absent, comma follow-up present; F2/F3 pins and staging retained. 28 unique ACs=11/8/9; 26 unchecked rows; no implementation handoffs; decision YAML 17 entries D-622..D-638. 50000 randomized multi-gap mixed cases PASS against Session50 unsplit control. Supplied lint/red-check/census receipts inspected, not rerun."}
```

### Verdict

`approved` — F1 is fixed, F2/F3 remain fixed, and no new blocking delivery defect was established. Executing the revised plan would deliver the registered intent. Implementation Red/Green, real API/SQLite and UI behavior remain for execution; plan approval does not start execution under the authoring harness's human gate.

Complete rolling report: `C:/Temp/av-kit/s65-plan-review-round-4.md`. The coordinator validates and saves it to the canonical path; this reviewer does not. Fresh receipts: `C:/Temp/av-kit/s65/review/recheck-r4.txt` and `audit-r4.txt`. Python ran with `PYTHONDONTWRITEBYTECODE=1`; all writes were under `C:/Temp/av-kit`. No memory-derived project fact was used.

### Report validation

`rtk proxy .venv/Scripts/python.exe tools/validate_closeout_artifacts.py --review C:/Temp/av-kit/s65-plan-review-round-4.md --review-state-only --expected-review-mode plan --expected-target-plan docs/execution/plans/2026-11-11-download-failure-visibility/implementation-plan.md --max-review-rounds 5 --output C:/Temp/av-kit/s65/review/review-state-r4.json` exited 0: `OK: review_mode=plan; round 4 of 5; verdict=approved; open findings=0`. This is report structure/target binding; the coordinator owns ledger acceptance and the canonical copy. The continued cap of 5 is recorded in the supplied Mat continuation receipt.

The scratch `verdict-r4.json` validated against `.agent/schemas/review-verdict.schema.v2.json` with `jsonschema.validate` (exit 0); removing `round` was rejected as the negative control. Every current checklist result is pass or n/a. Preservation assertions confirmed all historical sections from Q1 onward and all three Corrections Applied blocks are unchanged; the target hashes remained unchanged after probing.

🕐 Completed: 2026-11-12 01:39 (EST)
