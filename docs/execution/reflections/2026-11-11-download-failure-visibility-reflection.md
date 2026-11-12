---
date: "2026-11-12"
project: "download-failure-visibility"
meus: ["MEU-137", "MEU-138", "MEU-139"]
plan_source: "docs/execution/plans/2026-11-11-download-failure-visibility/implementation-plan.md"
template_version: "2.0"
---

# 2026-11-12 Meta-Reflection

> **Date**: 2026-11-12 (planned on the evening of 2026-11-11; reviewed, executed and closed in the early hours of 2026-11-12)
> **MEU(s) Completed**: MEU-137 `download-failure-reason`, MEU-138 `sabr-check-current-messages` and MEU-139 `ytdlp-log-text`, Session 65, the first session of the download reliability grouping (grouping D-535 to D-543, Sessions 65 to 67). A failed or age-restricted download card states its reason in one short av-kit sentence per cause (refused, no format, cookies, write failed), or gives yt-dlp's first line, redacted, for any other failure. The Console gains `download.started`, `download.done` and `download.failed` lines. Check SABR matches yt-dlp 2026.10.26's own SABR words as whole words. The page always states the last result and its time, and Check, Force and Clear each log one line. yt-dlp's warnings and errors always reach the Console, with their text in the kept, redacted `detail` field. The existing yt-dlp debug switch adds debug and info lines, and a change applies on the next call. The session resolves DOWNLOAD-FAILED-NO-REASON, SABR-CHECK-MISSES-CURRENT-MESSAGES and YTDLP-LOG-TEXT-DROPPED.
> **Plan Source**: `docs/execution/plans/2026-11-11-download-failure-visibility/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   - **The plan review: four rounds, three of them about one contract.** Round 1 raised F1 to F3 (all High). F1 said `FAILURE_LOG` cleaned yt-dlp's text after the redactors, so a NUL or a tab inside a secret, a link or the home folder got through. F2 and F3 were about pins and staging, and round 2 closed them. F1 came back in rounds 2 and 3 as `partial`. A whitespace split, then an interior split of the home folder, each beat the latest cleaning order. Round 4 approved. The rounds used 11,060,783, 5,712,752, 4,570,818 and 3,293,430 tokens: 24,637,783 in all. That total needed Mat's "increase token buget by 30M" after round 1 (ledger grant, 2026-11-12 00:29) and his scope answer, which allowed two more rounds (ledger grant, 01:28). RULE-1 adds the missing step.
   - **The execution review found the same class of fault in the code (F1, High, AC-137).** The plan's contract held, but `classify_download_error` ran `clean_line` before `scrub_line` in the adapter. A real `DownloadError('ERROR: co\tokie=SECRET')` stored `co okie=SECRET`, and a tab-split link and a NUL before the home path also got through. The unit tests checked `scrub_line` by itself and the classifier by itself, and no test drove split text through both. D-639, ruled A by the Fable subagent under Mat's delegation, moved all cleaning into `scrub_line`. AC-137.12 now drives the real adapter, service and SQLite (RULE-1).
   - **Gate run 1** stopped at `py-tests` on `test_ac_130_10_cmyk_icc_to_srgb`, a capture test this session didn't touch: `1 failed, 2150 passed` (`s65-D6-py-tests-run1.txt`). The test passed alone (`s65-h1-2-rerun-ac130-10.txt`, `1 passed in 0.17s`), and run 2 passed every step. Both receipts are kept (Session 53 RULE-4).
   - **Two closeout checks refused artifacts the session wrote.** H1-7a refused round 1's report, because Codex put a two-column probe table inside `## Findings`, and the review parser reads every table row there as a finding (`s65-h1-7a-r1.txt`). The report wasn't edited, and the round 2 prompt asked Codex to move the table. H1-6 refused the MEU-137 handoff after the F1 fix, because its Decision Log held a bullet for D-639. It accepts only `None.` or one fenced `decision_log` YAML block. D-639 stays in the plan's Decision Log, as D-622 to D-638 do, and Departure 6 points to it. RULE-2 and RULE-3 add the missing steps.
   - **H2-2 refused the approved plan.** D-637's `chosen` text read `'<Type>: <strerror>'`, and the closeout check reads `<strerror>` as an unfilled template placeholder (`decision_log item 16 still carries a template placeholder`). The text now spells out the same thing in words: "the exception type name, a colon, then its strerror". The meaning is unchanged. H2-2 passed after the edit, and so did the H1-6 family and H1-7a/b when rerun (`s65-h2-2-run.txt`, `s65-h1-6-recheck.txt`, `s65-h1-7ab-recheck.txt`). The plan rounds didn't run this check, so the problem went unnoticed through four approved rounds.

2. **What instructions were ambiguous?**
   - **Where an execution-stage decision is logged.** The plan carries the session's YAML Decision Log, and the handoff's Decision Log section accepts the same YAML. Nothing says which of the two holds a decision made during execution. The session chose the plan (RULE-2).
   - **The commit trailer.** The harness asks for a Co-Authored-By trailer. Task H2-5, `.agent/docs/development-lifecycle.md:452` and Mat's standing rule say there is none. The commit has none.

3. **What instructions were unnecessary?**
   - H2-1's `view_file` row, as in Sessions 59 to 64. H2-2's check validates the reflection against the same template and schema.

4. **What was missing?**
   - **An end-to-end split-text test as part of any redaction contract** (RULE-1).
   - **A rule for where an execution decision goes** (RULE-2).
   - **A Findings-section rule in the execution review prompt** (RULE-3).

5. **What did you do that wasn't in the prompt?**
   - **Had a Fable subagent rule D-625 and D-639** under Mat's delegation ("If you need decisions answerd have Fable subagent do rulling and accept it as if it was coming from human", USER_EXPLICIT 2026-11-12). Each ruling was accepted as a human ruling and recorded with that quote.
   - **Wrote `f1_red_receipt.py`.** It ran AC-137.12 against the pre-fix classifier and generic branch, then restored both files and checked their SHA-256.
   - **Remapped the handoffs' line citations into the three files that moved** (`f1_line_map.py`, `f1_cite_sweep.py`). Then I checked each changed citation against the line it named (`f1_cite_check.py`). That check found two wrong citations, and both were corrected (adapter `:626`, service `:649`).

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **Every Red failed by assertion** (Session 62 RULE-3), and red-check found 0 problems on each:
     - MEU-137: pytest `23 failed, 91 passed`, Vitest `1 failed | 49 passed`; `red-check: 2 receipt(s), 12 required test(s), 0 problem(s)`;
     - MEU-138: pytest `11 failed, 113 passed`, Vitest `3 failed | 51 passed`; `red-check: 2 receipt(s), 8 required test(s), 0 problem(s)`;
     - MEU-139: pytest `10 failed, 51 passed`; `red-check: 1 receipt(s), 8 required test(s), 0 problem(s)`;
     - AC-137.12 (after D-639): `1 failed in 39.21s`; `red-check: 1 receipt(s), 1 required test(s), 0 problem(s)`.
   - **The reference scrubber (`ref_check.py`, `FAILS 0`)** checked `scrub_line` against an independent implementation, case by case.
   - **AC-137.12 caught what the unit tests could not.** It is the only test that sends split text through the classifier and the service together. It failed on the pre-fix code and passes on the fix.

7. **Which tests were trivially obvious?**
   - AC-137.1's enum member check and AC-138.1's phrase constant check. They are characterisation guards, which is their purpose.

8. **Did pyright/ruff catch anything meaningful?**
   - No. pyright had 0 errors and ruff was clean on every gate receipt (`s65-D6-py-types.txt`, `s65-D6-py-lint.txt`).

### Workflow Signal Log

9. **Was the FIC useful as written?**
   - Mostly. Eighteen mechanism ids, `FAILURE_CAUSE_ENUM` to `LIVE_SOURCE`, gave the plan, the Reds, the handoffs and both reviews one contract. But `SCRUB_LINE`'s contract named only `scrub_line`. It didn't name the cleaning that ran before it in the adapter, so the plan review and the unit tests both checked the scrubber alone (RULE-1).

10. **Was the handoff template right-sized?**
    - For three MEUs, the shared gate record repeated in all three handoffs was the costliest part to keep current. The F1 fix changed it in three places (`f1_gate_record.py`). The cross-reference AC rows exist only for the AC check (`slim_candidate`).

11. **How many tool calls did this session take?**
    - About 1,169 unique tool calls in this conversation's transcript at H2-2. They cover the planning probes, the four-round plan review, execution, the two-round execution review and closeout.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    - **No task row was delegated** to `av-kit-builder` or `av-kit-verifier`.
    - **D-625 and D-639** were each ruled by one Claude Code `general-purpose` subagent on Fable, under Mat's delegation. Neither ruling needed rework.
    - **Codex** reviewed the plan and the execution as the independent reviewer, which isn't delegation.

### Decisions Log

| ID | Stage | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|-------|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-531 | triage | File DOWNLOAD-FAILED-NO-REASON from the 2026-11-10 download comparison report, or leave it in the report? | human | File it: MEU-NEW, P2, open, linked to MEU-137 | Human-approved | Mat asked for the report's findings to be filed and grouped. Leaving them in an untracked proposal hides them from the register and from /session-grouping. MEU-137 resolves it. Two-way. | USER_EXPLICIT 2026-11-10 'follow the process, file them and add to session grouping' |
| D-532 | triage | File SABR-CHECK-MISSES-CURRENT-MESSAGES from the 2026-11-10 download comparison report, or leave it in the report? | human | File it: MEU-NEW, P3, open, linked to MEU-138 | Human-approved | As D-531. MEU-138 resolves it. Two-way. | USER_EXPLICIT 2026-11-10 'follow the process, file them and add to session grouping' |
| D-533 | triage | File YTDLP-LOG-TEXT-DROPPED from the 2026-11-10 download comparison report, or leave it in the report? | human | File it: MEU-NEW, P3, open, linked to MEU-139 | Human-approved | As D-531. MEU-139 resolves it. Two-way. | USER_EXPLICIT 2026-11-10 'follow the process, file them and add to session grouping' |
| D-535 | grouping | File the comparison report's findings and group them? | human | Yes: six issues filed and MEU-137 to MEU-142 grouped into Sessions 65 to 67 | Human-approved | Mat asked for exactly this. Leaving the findings in an untracked proposal lost: the failures are measured and silent. This session ran the first of the three sessions. | USER_EXPLICIT 2026-11-10 'follow the process, file them and add to session grouping' |
| D-536 | grouping | Slicing, homes and phases | autonomous | One MEU per issue; adapter MEUs in 02 as phase 2, service MEUs in 03 as phase 3, band P2 | Local Canon | Each issue is one logical change with its own TDD cycle; MEU-115 set the precedent. Two-way. | — |
| D-537 | grouping | Which MEUs share a session? | autonomous | 137, 138 and 139 in Session 65; 140 and 141 in Session 66; 142 alone in Session 67 | Local Canon | Session 65 shares the logger, the Downloader page and the redaction path. It ran all three MEUs with no split (D-625 B). Two-way. | — |
| D-538 | grouping | Queue position | autonomous | Session 65 after Session 61 and before Sessions 62 to 64; 66 after 65; 67 after 65 in any slot | Local Canon | Fixes to a silent failure in the released rc.3 go ahead of new capability. Sessions 62 to 64 ran first, and this session followed them. Two-way. | — |
| D-539 | grouping | How should a download choose YouTube clients? | human | A: no player_client on the first attempt, one retry with today's cookie pin, both attempts logged | Human-approved | Brief in the grouping (HDP run 2026-11-10). Session 66 carries it; this session didn't touch the client choice. | USER_EXPLICIT 2026-11-10 'A' |
| D-540 | grouping | How does yt-dlp get a JS runtime in dev and in the installed app? | human | A: ship deno.exe in the Windows installer, resolved like ffmpeg; yt-dlp[default]; Health names the runtime | Human-approved | Brief in the grouping (HDP run 2026-11-10). Session 66 carries it. | USER_EXPLICIT 2026-11-10 'A' |
| D-541 | grouping | SABR phrases and the check's visibility | autonomous | One phrase constant matched case-insensitively; show every result with its time; log each SABR action | Local Canon | The GUI's own probe uses the phrases. At plan time Mat narrowed the match to whole words (D-623) and 'po token' to 'require a gvs po token' (D-624), and MEU-138 implements those rulings. Two-way. | — |
| D-542 | grouping | MP3: yt-dlp postprocessor or MediaPort.convert? | autonomous | MediaPort.convert after the download, in any cookie mode | Local Canon | The spec already names this path. Session 67 carries it. Two-way. | — |
| D-543 | grouping | yt-dlp log lines: what and when | autonomous | Warnings and errors always log with the text in the kept, redacted detail; debug lines only with the setting on; the setting read per call | Local Canon | Session 50 (D-247) made detail a kept, redacted field; the ffmpeg setting is already read live. MEU-139 implements it, with D-622 A for the debug text. Two-way. | — |
| D-622 | planning | With the yt-dlp debug switch off and on, which yt-dlp lines reach the Console? | human | A: warnings and ERROR lines always; debug and info lines, redacted, only with the switch on | Human-approved | 02 and AC-122.16 conflict once the text is kept. A keeps AC-122.16 with the switch off; B makes the switch do nothing; C breaks AC-122.16. Two-way. | USER_EXPLICIT 2026-11-11 'Opt-in shows text (Recommended)' |
| D-623 | planning | How does a SABR phrase match a yt-dlp line? | human | A: whole words, case-insensitive | Human-approved | A bare substring 'sabr' matches 'Sabrina' in a title. B (substring) would turn SABR on from a title. Two-way. | USER_EXPLICIT 2026-11-11 'Whole words (Recommended)' |
| D-624 | planning | Does the phrase set keep 02's bare 'po token'? | human | A: narrow it to 'require a gvs po token' | Human-approved | yt-dlp prints PO Token lines that are not about SABR, and a bare phrase would lock quality at 360p without cause. B follows 02's text as written. Two-way. | USER_EXPLICIT 2026-11-11 'Narrow it (Recommended)' |
| D-625 | planning | Does the session name a split point that moves MEU-139 to Session 65b? | human | B: run all three MEUs with no context-measured split | Human-approved | B, the do-nothing option, relies on compaction, which held: all three MEUs landed in one session. A named a split point for the least coupled MEU. Ruled by the Fable subagent under Mat's delegation. Two-way. | USER_EXPLICIT 2026-11-12 'If you need decisions answerd have Fable subagent do rulling and accept it as if it was coming from human' (Fable subagent: B) |
| D-626 | planning | Does matched_phrase go on the SABR wire? | autonomous | A: no; domain status and the download.sabr_check line only; the OpenAPI snapshot doesn't change | Local Canon | The spec puts the phrase in the log; adding it to the wire changes the snapshot, MCP and its audit for a field no rule shows. H1-4 confirms the snapshot is unchanged. Two-way. | — |
| D-627 | planning | How is yt-dlp text cleaned before it is stored or logged? | autonomous | A: clean_line drops ANSI, controls, format and surrogate code points and runs inside scrub_line, which matches the home folder across split characters first | Local Canon | Three plan rounds shaped it (F1). Execution round 1 found the adapter also cleaned before the scrub, which D-639 removed. Two-way. | — |
| D-628 | planning | How is the grouping's §8 table made readable to the closeout validator? | autonomous | A: insert a '## 9. Decision Briefs' heading before the D-539 brief | Local Canon | A heading ends §8 and changes no decision text; editing the validator is out of scope. Two-way. | — |
| D-629 | planning | Does 02's Phrases row change to match D-623 and D-624? | autonomous | A: yes; it says whole words, case-insensitive, and require a gvs po token | Local Canon | Mat ruled both; a spec that says otherwise would contradict the tested behaviour. Two-way. | — |
| D-630 | planning | 02's Control row asks for a 'yt-dlp debug log' switch; one called 'yt-dlp debug' exists. What does the row say? | autonomous | A: name the existing 'yt-dlp debug' switch and test that it saves | Local Canon | The switch landed after the issue was written; its label is pinned by the settings copy sources. Two-way. | — |
| D-631 | planning | Where do DownloadFailedError and the classifier live? | autonomous | A: DownloadFailedError last in domain/errors.py; the classifier, needles and SABR phrases in the YouTube adapter | Local Canon | The service needs the cause, not yt-dlp's words; appending keeps the existing order pin. Two-way. | — |
| D-632 | planning | Is an error() call without the 'ERROR:' prefix logged at ERROR? | autonomous | A: no; it is a debug line, logged only with the switch on | Research-backed | With verbose on, yt-dlp passes each traceback to error() with no prefix; logging those at ERROR doubles every failure. Two-way. | — |
| D-633 | planning | Does an AgeRestricted job log download.failed? | autonomous | A: yes, at ERROR with its stored text | Local Canon | The card treats AgeRestricted as a failure; the Console matches it. Two-way. | — |
| D-634 | planning | Does a Cancelled job log a line? | autonomous | A: no new line | Local Canon | The user cancels, so the cause is known; no rule names a cancel event. Two-way. | — |
| D-635 | planning | How does the page state an Inactive result? | autonomous | A: the sabr-status panel is always shown and holds the result text | Local Canon | One place for the result keeps the pins and layout; a toast disappears. Two-way. | — |
| D-636 | planning | Is a missing-format error during SABR a no_format or a refused failure? | autonomous | A: refused, when the same call's logger matched a SABR phrase | Research-backed | With SABR on, yt-dlp hides every format and then says the format is not available; waiting is the fix, not another quality. Two-way. | — |
| D-637 | planning | What does an OSError outside cookie file mode become? | autonomous | A: write_failed with detail Type: strerror, never the filename | Local Canon | str(exc) holds the path, so only the type and strerror are kept. Two-way. | — |
| D-638 | planning | How is the 'other' reason on the card made safe? | autonomous | A: safe_reason(scrub_line(raw)) or the error's type name | Local Canon | MEU-115's pattern plus scrub_home, because the stored message also reaches agents through the API and MCP. Two-way. | — |
| D-639 | execution | How does yt-dlp's error line keep its split characters until scrub_line (execution review round 1, F1)? | human | A: first_line splits only at CR, LF and CRLF; the classifier drops only a leading ERROR:; the generic branch uses first_line; all cleaning in scrub_line; AC-137.12 end to end | Human-approved | Round 1 F1 showed the classifier cleaned before scrub_line, so a split secret was stored. Cleaning once, in scrub_line, keeps the plan's approved order. str.splitlines also ends a line at U+2028, which would hide a split. Ruled by the Fable subagent under Mat's delegation. Two-way. | USER_EXPLICIT 2026-11-12 'If you need decisions answerd have Fable subagent do rulling and accept it as if it was coming from human' (Fable subagent: A) |

---

## Pattern Extraction

### Patterns to KEEP
1. **A reference implementation beside a security-relevant helper.** `ref_check.py` compared `scrub_line` with an independent version over the plan's cases (`FAILS 0`), and the reviewer's probes found no gap in `scrub_line` itself.
2. **A Red receipt for a review fix, taken on the restored pre-fix code with a hash check** (`f1_red_receipt.py`). It proves the new test fails for the reason the finding gives.
3. **A citation check after a line remap.** `f1_cite_check.py` printed the source line under each changed citation, and that found the two the sweep got wrong.

### Patterns to DROP
1. **Testing a scrubber only in isolation.** Each step's unit tests passed while the path through them leaked (RULE-1).

### Patterns to ADD
1. **An end-to-end split-text test in any redaction contract** (RULE-1).
2. **Execution decisions logged in the plan's YAML Decision Log, with the handoff pointing to them from a Departure** (RULE-2).
3. **A Findings-section rule in every review prompt** (RULE-3).

### Calibration Adjustment
- **Estimated:** the plan review opened at 3 rounds and 25M. Mat added 30M, then 2 rounds. Execution opened at 6 rounds and 40M.
- **Actual time (local time, UTC-5):**
  - The plan review returned round 1 at 23:56 on 2026-11-11 and approved in round 4 at 01:39 on 2026-11-12.
  - The baseline ran at 01:45. MEU-137's Red ran at 02:00 and its Green at 02:04. MEU-138's ran at 02:11 and 02:13, and MEU-139's at 02:20 and 02:21.
  - Gate run 1 stopped at 02:30, and run 2 passed at 02:37. Execution round 1 returned at 03:00.
  - The F1 Red ran at 03:11, and gate run 3 passed at 03:19. Round 2 returned approved at 03:29.
- **Tokens:**
  - plan review: 24,637,783 over four rounds;
  - execution review: 16,649,211 over two rounds (13,389,317 and 3,259,894) of 40,000,000.
- **Adjusted estimate for a three-MEU redaction and logging session:** budget 4 plan rounds (about 25M), unless a split-text matrix probe runs through every function between the source and the store before round 1. Then budget about 12M. Budget two execution rounds (about 20M).

---

## Next Session Design Rules

```
RULE-1: A redaction contract names every function that touches the raw text between its source and the scrubber, in order. Its tests include one end-to-end case that drives text with split characters (tab, NUL, CR, U+2028, ANSI) inside a secret, a link and the home folder through the real adapter, service and store. Unit tests of the scrubber alone don't prove the path.
SOURCE: Plan review rounds 1 to 3 (F1 partial twice) and execution round 1 F1. classify_download_error cleaned before scrub_line, so 'ERROR: co\tokie=SECRET' stored 'co okie=SECRET' while every unit test passed.
EXAMPLE: "SCRUB_LINE: scrub_line cleans, then scrubs" becomes "path: YoutubeDL error -> classify_download_error (first_line, prefix strip only) -> _run_one -> scrub_line (the only cleaner) -> store and log; AC-137.12 drives eight split cases end to end".
```

```
RULE-2: A decision made during execution goes into the plan's YAML Decision Log beside the planning decisions. The handoff's Decision Log stays `None.` and a Departure names the decision id. If a handoff does log it, the entry must be the fenced decision_log YAML block.
SOURCE: H1-6 refused the MEU-137 handoff because its Decision Log held a bullet for D-639 (human-decision-protocol.md §6).
EXAMPLE: "## Decision Log\n\n- **D-639 ... ruled A**" becomes "## Decision Log\n\nNone." with Departure 6 citing D-639 and the plan's block.
```

```
RULE-3: Every review prompt states that the `## Findings` section holds exactly one table, the Findings table, and that probe or evidence tables go under another heading.
SOURCE: H1-7a refused execution round 1's report: 'Findings row 2 has 2 cell(s) but the header has 8', from a probe table under a ### heading inside ## Findings.
EXAMPLE: the prompt's Output section gains "## Findings holds only the Findings table; put probe tables in ## Probe Detail".
```

---

## Next Day Outline

1. **Target:** done and committed. MEU-137 to MEU-139 are approved.
2. **Next session:** Session 66 `youtube-client-runtime` (MEU-140, MEU-141), the second session of the download reliability grouping. It carries D-539 A and D-540 A. Its prompt is `C:/Temp/av-kit/session-66-prompt.md`.
3. **Scaffold changes needed:** none. Where an execution decision is logged (RULE-2) is worth raising with Mat as a protocol item.
4. **Patterns to bake in from today:** RULE-1 to RULE-3 here, plus the rules carried from Sessions 50 to 64.
5. **Codex validation scope:** Session 66's plan, then its execution.
6. **Time estimate:** set by the Session 66 plan. It measures the client and runtime change against YouTube, which this session didn't do.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | About 1,169 unique tool calls in this conversation's transcript at H2-2, from planning on |
| Time to first green test | MEU-137's Green at 2026-11-12 02:04 (UTC-5), 4 minutes after its Red (`s65-py-red-137.txt`, `s65-py-green-137.txt`) |
| Tests added | pytest 2108 to 2152 (+44; `s65-base-py.txt`, `s65-D6-py-tests.txt`); Vitest 1279 to 1285 (+6; `s65-base-ui.txt`, `s65-D6-ui-tests.txt`); MCP 520 unchanged |
| Codex findings | Plan review: R1 changes_required (F1 to F3, 3 High); R2 F1 partial; R3 F1 partial; R4 approved (24,637,783). Execution review: R1 changes_required (F1 High, AC-137); R2 approved, F1 fixed, 0 new findings (16,649,211 of 40,000,000) |
| Handoff Score (X/7) | 5/7. Every AC has evidence. The execution review found a High leak that the handoffs' evidence didn't cover. H1-6 refused the MEU-137 handoff once, on the Decision Log format |
| Rule Adherence (%) | 89 (17 of 19 sampled rules followed in full, 2 in part) |
| Prompt→commit time | Planned 2026-11-11, committed 2026-11-12 |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Tests before production code; Red before Green | AGENTS.md §Testing & TDD | Yes. Each MEU's Red failed by assertion before its Green, and so did AC-137.12 before D-639's fix |
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Both canonical reviews are Codex's reports, validated under `C:/Temp/av-kit` and copied byte for byte |
| Human decisions stay human, with a brief and a do-nothing option | `.agent/docs/human-decision-protocol.md` | Yes. D-622 to D-624 went to Mat. D-625 and D-639 went to the Fable subagent under Mat's quoted delegation, and D-625's options included the do-nothing B |
| A raw value that can reach a log, stdout or the Console is fixed or raised | Session 50 rule | Partly. The plan fixed it in its rows, but the adapter's pre-clean leaked split secrets until execution round 1's F1 |
| Outside text gets lone-surrogate, control-character and empty regressions | Session 53 RULE-1 | Yes. `clean_line`, `scrub_line` and `first_line` |
| Shared missing names go in a type-only row first | Session 53 RULE-2 | Yes. Row 1 |
| A failure in an untouched file is rerun once, with both receipts kept | Session 53 RULE-4 | Yes. AC-130.10 in gate run 1 |
| Handoff checks before the review prompt; every cited AC has a row | Session 54 RULE-3 | Yes. H1-6 to H1-6b and the dotted check passed before each dispatch |
| List and run the callers of anything extended | Session 55 RULE-1 | Yes. `DownloadFailedError`'s constructor walk and both exact-type pins |
| Temps opened with xb | Session 58 rule | n/a. This session writes no temp file in production code |
| A departure from an approved contract is recorded before the gate | Session 59 rule | Yes. Departures 1 to 5 before H1-2; Departure 6 before gate run 3 |
| Check the path list before an identity run | Session 60 RULE-4 | Yes. The gate's scope-paths step |
| Byte-edit a status file another session may hold dirty | Session 61 RULE-5 | Yes. H2-2 byte-edited MEU-137 to MEU-139's fields and proved them with render |
| Each Red fails by assertion | Session 62 RULE-3 | Yes. red-check found 0 problems on all four Red sets |
| Sweep adjacency pins in every test file | Session 63 RULE-1 | Yes. The constructor and exact-type pins moved in row 1 and row 2a |
| Counts in handoff prose copied from the receipt | Session 63 RULE-2 | Yes. Each count names its receipt |
| Edit scripts record CRLF or LF and fail on mixed endings | Session 63 RULE-3 | Partly. `edit.py` wrote 5 CRLF lines into an LF region in row 2a; `row2a_fix.py` restored them (Departure 4) |
| An AC that relies on a checker quotes its exact output line | Session 64 RULE-2 | Yes. The red-check and AC check lines are quoted from their receipts |
| Every command through RTK | AGENTS.md §RTK | Partly. Tests, gates, tools and dispatches went through `rtk proxy`; many reads and scratch scripts did not |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "7be03f27-971f-464c-b32b-2b44f64a3a0f"
  task_class: tdd
  outcome: success
sections:
  - {id: priority_0_system_constraints_non_negotiable, cited: true, influence: 3}
  - {id: planning_contract, cited: true, influence: 3}
  - {id: testing_tdd_protocol, cited: true, influence: 3}
  - {id: execution_contract, cited: true, influence: 3}
  - {id: session_discipline, cited: true, influence: 2}
  - {id: dual_agent_workflow, cited: true, influence: 3}
  - {id: commits, cited: true, influence: 3}
  - {id: validation_pipeline, cited: true, influence: 3}
  - {id: rtk_token_optimized_commands, cited: true, influence: 1}
  - {id: instruction_coverage_reflection, cited: true, influence: 2}
loaded:
  workflows: [create_plan, plan_critical_review, execution_session, execution_critical_review]
  roles: [orchestrator, coder, tester]
  skills: []
  refs:
    - .agent/docs/human-decision-protocol.md
    - .agent/docs/harness-profiles.md
    - .agent/schemas/review-verdict.schema.v2.json
    - .agent/schemas/reflection.v1.yaml
    - .agent/templates/REVIEW-TEMPLATE.md
    - docs/execution/reflections/TEMPLATE.md
decisive_rules: [P0:human-decisions-stay-human, P0:raw-values-fixed-or-raised, P1:independent-review-no-self-approval, P1:tests-before-production-code, P0:never-commit-or-push-without-human-approval]
conflicts:
  - "The harness asks for a Co-Authored-By trailer on commits; task H2-5, development-lifecycle.md:452 and Mat's rule say no AI attribution trailer. The commit has none."
  - "Connected docs and artifact tools offered to publish deliverables; the user's rule keeps them as local repo files."
  - "The handoff template's Decision Log accepts an execution decision, while this plan logs every decision in its own YAML block; H1-6 refused a bullet entry."
note: "A failed download says why, Check SABR matches current yt-dlp words, and yt-dlp's own lines reach the Console; the download reliability grouping's first session."
slim_candidate: ["The shared gate record repeated in three handoffs had to be updated three times after one fix.", "H2-1's view_file row repeats what H2-2's validator checks."]
overthinking_observed: false
review_churn:
  rounds_to_approval: {plan: 4, execution: 2}
  findings_per_round:
    - {review: plan, round: 1, critical: 0, high: 3, medium: 0, low: 0}
    - {review: plan, round: 2, critical: 0, high: 1, medium: 0, low: 0}
    - {review: plan, round: 3, critical: 0, high: 1, medium: 0, low: 0}
    - {review: plan, round: 4, critical: 0, high: 0, medium: 0, low: 0}
    - {review: execution, round: 1, critical: 0, high: 1, medium: 0, low: 0}
    - {review: execution, round: 2, critical: 0, high: 0, medium: 0, low: 0}
  churned_findings: 2
  finding_categories: {boundary_validation: 1, back_compat_break: 1, contract_drift: 1, fix_generalization_miss: 1}
  verdicts: {changes_required: 4, approved: 2}
meu_work_classes: [correctness, correctness, mixed]
```
