---
date: "2026-11-08"
project: "convert-extract-index"
meus: ["MEU-123"]
plan_source: "docs/execution/plans/2026-11-07-convert-extract-index/implementation-plan.md"
template_version: "2.0"
---

# 2026-11-08 Meta-Reflection

> **Date**: 2026-11-08
> **MEU(s) Completed**: MEU-123 `convert-extract-stream-index`. Session 54 closes CONVERT-EXTRACT-STREAM-INDEX-MISMATCH (D-227) and its rider CONVERT-EXTRACT-ENCODER-LABEL (D-242). Mat ruled the Cut label filed (D-373), the startup database path filed (D-377) and the default execution budget (D-378), and asked that both filings be placed in the grouping (D-379, D-380)
> **Plan Source**: `docs/execution/plans/2026-11-07-convert-extract-index/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   - **Gate run 1 failed on a line row 2 added.** Row 2 narrowed `encoder` for pyright with an `assert` in Compress's branch. AC-4.12 bans `assert` in `packages/core/src`, and row 2's Green ran only the suites that name the conversion service, so the ban first ran in the gate's `py-tests` (1 failed, 1337 passed). The `assert` became the `ValidationError` guard the Cut branch already uses (`services/conversion.py:535-536`), row 2's commands were rerun, and run 2 passed every step. Run 1's receipts are kept in `C:/Temp/av-kit/s54-gate-r1/`.
   - **The plan review cost 8,541,302 tokens in one round,** more than the 5.25M that makes the execution budget Mat's call. Mat took the recommendation, the default 21M (D-378).
   - **H2-2's first run refused the plan's decision log.** The closeout check's placeholder pattern read `{stream_index}` in D-364's adapter precedent, and `{n}` and `{k}` in D-367's message, as unfilled template slots. Both YAML lines were reworded with the same meaning, "a: followed by the stream index", as D-227 already words it, and "a:N … K" with N and K defined. The plan-time probe (`s54-decision-issue-probe.txt`) read the grouping and the register but not the plan's own decision log, so the refusal first surfaced at closeout (RULE-5).
   - **Two refusals at H1-6.** The evidence check refused a record whose `scope` named the scratch TMP folder under the receipts root, and the AC check refused a handoff whose table never named AC-24 or AC-45, which the plan cites. Both were fixed in the handoff: the scope now says "outside the home folder", and the cross-reference rows were added.

2. **What instructions were ambiguous?**
   - **The commit trailer.** The harness asks for a Co-Authored-By trailer, and task H2-5 says the commit has none (`development-lifecycle.md:452`). The draft follows H2-5, as Sessions 52 and 53 did.
   - **Row 2's helper placement.** The row says "right after `EXTRACT_UNKNOWN_EXT`". `_audio_streams` and `_missing_track` sit after `_preset_by_id`, beside the other module helper. Nothing reads them by position, and the handoff states the departure.

3. **What instructions were unnecessary?**
   - H2-1's `view_file` row, again. H2-2's check validates the reflection against the same template and schema.

4. **What was missing?**
   - **The repository's static bans in a row's Green.** Row 2's Validation cell listed the conversion suites but not `tests/unit/test_domain.py`, which holds the AC-4.12 ban that any core edit can break (RULE-1).
   - **The evidence and AC checks' rules in the handoff template.** That non-command fields may not name the receipts root, and that every AC the plan cites needs a row, are known only from the validators' refusals (RULE-3).

5. **What did you do that wasn't in the prompt?**
   - **A HealthService first in the real-FFmpeg tests (D-376).** Plan review F1 measured the fixture and database paths printing to stdout without one; AC-123.13 now guards it with positive controls.
   - **Filed two issues at plan time on Mat's rulings.** `CONVERT-CUT-ENCODER-LABEL` (debt queue, D-380) and `CONSOLE-STARTUP-DB-PATH` (Session 55 rider, D-379), with `decision_log` entries in the register.
   - **Read only the `python` job in `ci-collect.py`.** Each CI job has a step named Tests, so the first draft counted four.
   - **`exist_ok=True` in the identity selftest's folder creation,** because the copied selftest creates `tests/` twice.
   - **Kept gate run 1's receipts** and recorded the failure and its fix in the Quality Gate Results, not only the passing run.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **All 16 Reds in `s54-extract-red.txt` failed on their own behaviour,** each by assertion, as Session 53 RULE-2 asked. First audio stream named an AAC track `clip_a.mka`, not `.m4a` (AC-123.1). All audio streams planned `_a1`, `_a2` from ffprobe's index, not `_a0`, `_a1` (AC-123.2), and a single-track file asked for position 1 (AC-123.3). A video-only file and an index past the end were queued `Pending` rather than failed at add (AC-123.4). An Extract saved `hevc_nvenc` (AC-123.6), and with no software encoder it failed outright. Six real-FFmpeg cases failed the same ways on generated `.mp4` files (AC-123.10 to AC-123.12).
   - **AC-4.12's ban in gate run 1.** It caught the `assert` row 2 added, which pyright had asked for and no conversion test exercised.

7. **Which tests were trivially obvious?**
   - AC-123.7, a legacy Extract row runs unchanged. It guards LEGACY_JOBS (D-369), so a later migration can't change a stored row's meaning without failing it.

8. **Did pyright/ruff catch anything meaningful?**
   - Pyright's narrowing request led to the `assert` that AC-4.12 then refused, so it pointed at a real missing guard. Ruff caught one E501 docstring line in the new module. No defect otherwise.

### Workflow Signal Log

9. **Was the FIC useful as written?**
   - Yes. The mechanism ids (AUDIO_POSITION to NO_RAW_CONSOLE) let the Reds, the handoff and the review prompt name the same contract, and the review approved in one round.

10. **Was the handoff template right-sized?**
    - Yes for one MEU. The cross-reference AC rows for earlier MEUs are filler that only the AC check needs (`slim_candidate`).

11. **How many tool calls did this session take?**
    - About 600 in this conversation's transcript at H2-2, across planning, the plan review, execution, the gate, the execution review and closeout.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    - None. The coordinator ran every row. Codex reviewed the plan and the execution as the independent reviewer, which isn't delegation.

### Decisions Log

| ID | Stage | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|-------|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-227 | triage | What does stream_index mean? | autonomous | Audio-relative everywhere. _output_ext looks the codec up by audio position and the All audio streams plan sends audio positions. Both modes are tested against a real .mp4 | Local Canon | The adapter maps `a:N` and the 08 contract picks the container from the codec at that position; only the service used ffprobe's index (`known-issues.yaml:3817`). Two-way. | — |
| D-240 | grouping | Where does session numbering start? | autonomous | 49 | Local Canon | Starting at 49 reuses no number. Two-way. | — |
| D-241 | grouping | Are the transcript title and channel name two MEUs? | autonomous | One, MEU-122 | Local Canon | Same enumeration, change and test fake. Two-way. | — |
| D-242 | grouping | Where do the riders go? | autonomous | By shared file | Local Canon | A rider needs a session already working in that file. Session 54 carried CONVERT-EXTRACT-ENCODER-LABEL, which lives in `services/conversion.py`. Two-way. | — |
| D-243 | grouping | Does rc.2 get its own MEU? | autonomous | Yes, MEU-125 | Local Canon | MEU-110 is approved and closed. Reopening it would hide the new gate. Two-way. | — |
| D-244 | grouping | Which session runs first? | autonomous | Fetch and uninstall, Session 49 | Local Canon | It's the smallest, and MEU-125 reuses its round-trip script. Two-way. | — |
| D-245 | grouping | Is TTS one session or two? | autonomous | Two, Sessions 51 and 52 | Local Canon | The FP16 cause hunt has no upper bound and shouldn't hold the download refusal. Two-way. | — |
| D-246 | grouping | Where does the FFmpeg build run, and where does the rebuilt archive live? | human | Withdrawn: no build runs | Human-approved | Mat kept FFmpeg as it is (D-266). This session's real-FFmpeg tests run the pinned binary as shipped. | USER_EXPLICIT 2026-11-04 "FFmpeg, keeping libdvdcss in rc.2: yes" |
| D-247 | grouping | Do errors always go to a file? | human | Yes: errors always go to a file. Session 50's plan carried it out | Human-approved | It changes a default the user sees, so it was Mat's to rule. D-296 carried it out. | USER_EXPLICIT 2026-11-05 "D-247: yes they should go to file" |
| D-248 | grouping | Does Mat's "Proceed" confirm the grouping for the D-234 scoping review? | autonomous | Yes, with the §3 changes listed for Mat to check | Local Canon | Waiting would stop work Mat asked to go ahead, and the grouping stays reversible. Two-way. | USER_EXPLICIT 2026-11-04 "All ohter recommendations are accepted. Proceed" |
| D-249 | grouping | Does the light accent stay in MEU-118? | autonomous | No: its own MEU-126 in Session 56, optional for rc.2 | Local Canon | Scoping review F1: a separate cause, separate tests and a separate human check. Two-way. | — |
| D-250 | grouping | Does Batch E stay one session? | autonomous | No: MEU-123 in Session 54 and MEU-124 in Session 55 | Local Canon | Scoping review F2: they share no file. Session 54 ran MEU-123 alone, and its Cut finding went to the debt queue on the same test (D-380). Two-way. | — |
| D-267 | grouping | Do the two remaining fixes stay in one session now they share no file? | autonomous | Yes, Session 49 keeps MEU-113 and MEU-114 | Local Canon | Each is a few lines, and a second plan and review would cost more than they save. Two-way. | — |
| D-277 | grouping | Does Codex recheck the grouping after round 1's fixes? | human | No. The scoping loop stays `changes_required`, recorded as not rechecked | Human-approved | Both findings were session splits, and both were applied. Each session's plan review covers its own scope, as this one's did. | USER_EXPLICIT 2026-11-05 "all recommendations are accpeted, proceed" |
| D-280 | grouping | Does the tooling session get an MEU? | autonomous | No: Session 49b is tracked by its issue | Local Canon | MEUs are build-plan product work, and Session 49b ships nothing. Two-way. | — |
| D-364 | planning | What does stream_index mean, and where is that meaning computed? | autonomous | AUDIO_POSITION: the Nth audio stream in ffprobe order, the N in -map a:N; one module function _audio_streams returns the ordered audio list, or None when positions are unknown | Local Canon | The adapter, the Extract table and D-227 already use the position, so the service moves. One function keeps the plan, the extension and the missing-track check from drifting apart again (`implementation-plan.md:369`). | — |
| D-365 | planning | What does All audio streams plan, and what are its files called? | autonomous | AUDIO_PLAN: positions 0..k-1; the token prints the position, so _a0, _a1; one plan when positions are unknown or the file has no audio | Local Canon | Positions are what FFmpeg selects, so the names say which track a file holds. New names differ from today's for the same file, stated at the gate (`implementation-plan.md:379`). | — |
| D-366 | planning | Which codec picks an Extract's extension when the positions are unknown or out of range? | autonomous | EXTRACT_EXT: the codec at the position; with unknown positions, info.audio_codec at position 0 only; anything else .mka | Local Canon | audio_codec describes position 0, so using it for another position repeats the mismatch (`implementation-plan.md:389`). | — |
| D-367 | planning | What happens when a file lacks the asked-for audio track? | autonomous | MISSING_TRACK: the job is created Failed at add with a fixed reason; FFmpeg never runs | Local Canon | Failing at add keeps a batch add going, as AC-30.1 does for a bad probe. A 4xx would drop the other files; doing nothing leaves FFmpeg's 'Invalid argument' (`implementation-plan.md:399`). | — |
| D-368 | planning | How does an Extract job save no encoder? | autonomous | EXTRACT_NO_ENCODER: _dispatch skips detect_gpu and _resolve_encoder for Extract and saves gpu_encoder=None; Compress and Cut unchanged | Local Canon | An Extract never reads the encoder, so this also stops one failing for want of a software encoder. Saving None clears a legacy label on retry (`implementation-plan.md:409`). | — |
| D-369 | planning | Do existing jobs need anything? | autonomous | LEGACY_JOBS: no migration; a stored row runs unchanged | Local Canon | The plan and the extension are computed only at add, so a stored row's meaning never changed. A migration would re-probe every input (`implementation-plan.md:419`). | — |
| D-370 | planning | Do the API, MCP and GUI change to carry the one meaning? | autonomous | PASS_THROUGH: no change; contract 08 states the meaning; openapi.committed.json is unchanged | Local Canon | Every surface forwards the number untouched, and the GUI's a:N label already reads it as a position (`implementation-plan.md:429`). | — |
| D-371 | planning | How do the tests run a real .mp4 through the real FFmpeg adapter? | autonomous | REAL_FFMPEG and CI_DESELECT: a new module generates the files in tmp_path with the pinned ffmpeg.exe, runs the real service on real SQLite, never skips, and is deselected in CI | Local Canon | Generating keeps media out of the repository and pins the stream order the bug needs. CI has no fetched binaries, so the AC-25.10 precedent applies (`implementation-plan.md:439`). | — |
| D-372 | planning | Where are paths, codecs and the new message written, and does console_field see them? | autonomous | §Where values go: no new log line; the argv path is dropped by _process once a HealthService is built; MISSING_TRACK's message holds no path | Local Canon | The brief asks for this statement under Session 50 RULE-1. The startup line logged before a HealthService exists is D-377 (`implementation-plan.md:449`). | — |
| D-373 | planning | A Cut job also saves an encoder it never uses. Register it, fix it here, or leave it? | human | File CONVERT-CUT-ENCODER-LABEL, with no Cut change in MEU-123; placed by D-380 | Human-approved | The precedents point both ways and widening changes a behaviour neither issue names. Filing keeps MEU-123 to its two issues (`implementation-plan.md:459`). | USER_EXPLICIT 2026-11-07 'All recommendations accepted. But also file, and assign into session groupings So next sessions, can handle the new issues.' |
| D-374 | planning | Which checks does the session gate run? | autonomous | Session 53's shape plus ci-collect; the real-FFmpeg module, then the convert queue E2E; no package build or smokes | Local Canon | The real binary is this change's runtime proof, and no packaged surface changes (`implementation-plan.md:470`). | — |
| D-375 | planning | The tree holds another session's uncommitted files. Plan on top of them, and what does the commit carry? | human | Continue planning; row 0 records the paths as allowed; Session 54's commit carries them, on Mat's explicit words | Human-approved | The brief made it Mat's call, and Mat answered (`implementation-plan.md:480`). | USER_EXPLICIT 2026-11-07 'other session updated session grouping for planning of issue filed from session 53, you can continue this will not impact your planning, once you are done you will commit these files' |
| D-376 | planning | Plan review F1: the real-FFmpeg tests built no HealthService. How does the plan answer it? | autonomous | Each real-FFmpeg test builds a HealthService before the engine; AC-123.13 asserts no fixture or temp path reaches stdout, the ring or console.log, with positive controls; no recheck | Local Canon | It applies round 1's own recommendation in the production order. Doing nothing breaks Session 50 RULE-1 (`implementation-plan.md:491`). | — |
| D-377 | planning | The startup engine.created line prints the database path before HealthService is built. File it, fix it here, or leave it? | human | File CONSOLE-STARTUP-DB-PATH, with no change in MEU-123; placed by D-379 | Human-approved | It is outside both issues and the precedents point both ways. Filing raises it, as Session 50 RULE-1 requires (`implementation-plan.md:501`). | USER_EXPLICIT 2026-11-07 'All recommendations accepted. But also file, and assign into session groupings So next sessions, can handle the new issues.' |
| D-378 | planning | Plan round 1 cost 8,541,302, more than 5.25M. What budget does the execution loop open with? | human | The execution default, 21,000,000 | Human-approved | Mat's brief makes it Mat's call past 5.25M. Round 1 used 7,859,970 of it (`implementation-plan.md:512`). | USER_EXPLICIT 2026-11-07 'All recommendations accepted. But also file, and assign into session groupings So next sessions, can handle the new issues.' |
| D-379 | planning | Where does CONSOLE-STARTUP-DB-PATH go in the session grouping? | autonomous | P3, a rider in MEU-124 (Session 55 download-received-quality) | Local Canon | Session 55 is the only one left in avkit_infra/database/, and its column tests run create_sqlite_engine, which logs the line. That stretches D-242 from the file to its package, stated here (`implementation-plan.md:523`). Two-way. | USER_EXPLICIT 2026-11-07 'All recommendations accepted. But also file, and assign into session groupings So next sessions, can handle the new issues.' |
| D-380 | planning | Where does CONVERT-CUT-ENCODER-LABEL go in the session grouping? | autonomous | P4, last in current-focus's debt queue, not a rider | Local Canon | No remaining session edits services/conversion.py or the media adapter, so a rider would chain unrelated work (D-250's test) (`implementation-plan.md:534`). Two-way. | — |

---

## Pattern Extraction

### Patterns to KEEP
1. **Mechanism ids across the plan, the Reds, the handoff and the review prompt.** The review approved in one round, below Session 53's round 1 cost.
2. **A read-only real-stack probe in the plan review.** Codex ran the defects through the real service, SQLite and adapter before any row was written, and found the logging precondition (F1) that the fakes couldn't show.
3. **Reds that each fail on their own behaviour** (Session 53 RULE-2). All 16 named a wrong extension, position, status or label.

### Patterns to DROP
1. **A row's Green that runs only the suites naming the changed service.** It missed a repository-wide ban that the gate then caught (RULE-1).

### Patterns to ADD
1. **The static bans in every core row's Green** (RULE-1).
2. **A HealthService first in any test that builds the real stack outside wiring** (RULE-2).
3. **Run the evidence and AC checks on the handoff draft before the review prompt** (RULE-3).
4. **Check a review prompt's authorization cite against the file** (RULE-4).
5. **Run the closeout check on the plan's decision log at plan time** (RULE-5).

### Calibration Adjustment
- **Estimated time:** half a day for one MEU (Session 53's Next Day Outline). Session 53 budgeted 5M to 6M per plan round and 10M for the execution round.
- **Actual time:** about 6 hours of transcript time, 2026-11-07T23:25Z to 2026-11-08T05:40Z. The plan review cost 8,541,302 in one round, the execution review 7,859,970 in one round.
- **Adjusted estimate for a one-MEU service session with a real-binary test module:** half a day. Budget 9M for the plan round when the reviewer runs a real-stack probe, and 8M to 10M for the execution round.

---

## Next Session Design Rules

```
RULE-1: A row that edits packages/core/src runs tests/unit/test_domain.py in its Green, so the AC-4.12 assert ban and the other source scans run before the gate.
SOURCE: Row 2 narrowed encoder for pyright with an assert; its Green ran only the conversion suites and passed, and gate run 1 failed py-tests on test_ac_4_12 (conversion.py:535), so the gate ran twice.
EXAMPLE: "uv run pytest tests/unit/test_conversion_service.py ..." → "uv run pytest tests/unit/test_conversion_service.py tests/unit/test_domain.py ...".
```

```
RULE-2: A test that builds the real stack outside wiring.py builds a HealthService before the engine, and asserts a marker path is absent from stdout, the ring and console.log, with a positive control.
SOURCE: Plan review F1: a real-stack probe without one printed the fixture path in convert.finished argv and the SQLite path at engine creation; D-376 and AC-123.13 fixed it in row 1.
EXAMPLE: "engine = create_sqlite_engine(tmp_path / 'db')" → "HealthService(...) first, then the engine, then assert the marker folder is absent from capfd, the ring and console.log".
```

```
RULE-3: The handoff draft goes through the evidence and AC checks before the review prompt is written, and its non-command fields name no path under RECEIPTS_DIR's scratch folders; every AC the plan cites, an earlier MEU's included, gets a row.
SOURCE: H1-6 refused record 1's scope for naming the scratch TMP folder, and H1-6a refused the handoff because AC-24 and AC-45 never appeared; both were fixed before dispatch.
EXAMPLE: "scope: ... with TMP under C:/Temp/av-kit/s54/tmp" → "scope: ... with TMP outside the home folder", plus "| AC-24 (cross-ref) | ... |".
```

```
RULE-4: A review prompt that quotes Mat's authorization cites the file and line that hold the quote, checked with grep before dispatch.
SOURCE: The execution prompt first cited human-gate-decision.md for "proceed with execution"; the words are at current-focus.md:1, and the cite was corrected before round 1.
EXAMPLE: "Mat said 'proceed with execution' (human-gate-decision.md)" → "grep -n 'proceed with execution' first, then cite current-focus.md:1".
```

```
RULE-5: The plan-time decision probe names the plan itself as a --decision-source, and a decision_log item writes a format string's slots as words or capitals, never in braces or angle brackets.
SOURCE: H2-2's first run refused implementation-plan.md decision_log item 1, because PLACEHOLDER matched '-map a:{stream_index}'; D-367's 'a:{n} ... {k}' would have been refused next. The plan-time probe read only the grouping and the register.
EXAMPLE: "-map a:{stream_index}" → "-map a: followed by the stream index"; "a:{n}" → "a:N, with N the asked-for position".
```

---

## Next Day Outline

1. **Target:** done in the tree, not committed. Both issues are resolved, MEU-123 is approved, and the commit waits on Mat's words. It also carries the other session's files (D-375).
2. **Next session:** Session 55 `download-received-quality` (MEU-124), with the riders DOWNLOAD-BARE-CHANNEL-LISTS-TABS (D-361) and CONSOLE-STARTUP-DB-PATH (D-379). Its prompt is `C:/Temp/av-kit/session-55-prompt.md`.
3. **Scaffold changes needed:** none.
4. **Patterns to bake in from today:** RULE-1 to RULE-5 here, plus Session 53's, Session 52's, Session 51's and Session 50's rules, all of which carry.
5. **Codex validation scope:** Session 55's plan.
6. **Time estimate:** Session 55 is one MEU with two riders, so half a day to a day.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | About 600 in this conversation's transcript at H2-2 |
| Time to first green test | Before gate run 1 at 2026-11-08T05:08Z, after the Red at 04:52:39Z; the Green receipt on disk is the rerun after the AC-4.12 fix, 05:12:48Z (`s54-extract-green.txt`) |
| Tests added | pytest 1318 → 1338 (+20: 12 unit, 8 real FFmpeg); Vitest 1174 → 1174 (112 files); MCP 470 → 470; Electron convert queue 23 of 23 |
| Codex findings | Plan review: R1 approved, F1 Medium non-blocking (no HealthService in the real-stack tests), 8,541,302 tokens, folded in by D-376. Execution review: R1 approved, 0 findings, `intent_achieved: yes`, 7,859,970 of 21,000,000 |
| Handoff Score (X/7) | 6/7. Every AC has evidence and gate run 2 passed every step; run 1 failed on a line row 2 added, disclosed with its fix |
| Rule Adherence (%) | 80 (8 of 10 triggered rules followed in full, 2 in part; 6 more were not triggered) |
| Prompt→commit time | Planned and executed 2026-11-07 to 2026-11-08; not committed, waiting on Mat |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Tests before production code; Red before Green | AGENTS.md §Testing & TDD | Yes. All 16 Reds failed by assertion, and `red-check.py` reported 0 problems before row 2 |
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Both canonical reviews are Codex's reports, validated under `C:/Temp/av-kit` and copied byte for byte |
| A raw value that can reach a log, stdout or the Console is fixed in the row or raised | Session 50 rule; the brief | Yes. D-372 states where values go, D-376 and AC-123.13 close the test path, and the startup line is filed (D-377) |
| A row that edits a byte-hashed file runs its hash test | Session 50 rule | Not triggered. No row edited `ui/tests/e2e/test-ids.ts` |
| tested_state prompts name the user git ignore and `.claude/settings.local.json` | Session 51 RULE-4 | Yes. The execution prompt names both |
| Every command through RTK | AGENTS.md §RTK | Partly. Test, build and tool runs went through `rtk proxy`. Many reads and probes did not, and the RTK hook isn't installed on this PC |
| The recheck prompt gives the literal closure table | Session 52 RULE-1 | Not triggered. Both reviews approved in round 1 |
| A loop's budget is compared with the last comparable round | Session 52 RULE-3 | Yes. D-378's brief compared plan round 1 with 5.25M, and the execution budget with Session 53's 12.9M and Session 52's 19.7M executions |
| A new field carrying outside text gets a real-storage regression with invalid text | Session 53 RULE-1 | Not triggered. No new field carries outside text; MISSING_TRACK's message is av-kit's own |
| Shared missing names go in a type-only row first | Session 53 RULE-2 | Not triggered. No new name was shared by the Reds; each failed on its own behaviour |
| A recheck prompt names prior findings by the validator's id | Session 53 RULE-3 | Not triggered. No recheck ran |
| A gate step that fails in an untouched file is rerun once unchanged | Session 53 RULE-4 | Not triggered. Run 1 failed on a line row 2 added, so it was fixed, not rerun unchanged |
| No `assert` in `packages/core/src` | AC-4.12 | Partly. Row 2 added one, and gate run 1 caught it before the review |
| No branches or worktrees; never commit or push without the human | AGENTS.md §Commits | Yes. The work is on `main`, and nothing is committed |
| Preserve line endings | memory; the AC-51.6 byte hash | Yes. CRLF files stay CRLF and LF files stay LF, measured in bytes |
| Decision briefs keep a do-nothing option | the brief; HDP | Yes. D-373, D-377 and D-378 each list one |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "4bb56210-be84-4b47-98dc-d861ec32948b"
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
decisive_rules: [P0:never-commit-or-push-without-human-approval, P0:human-decisions-stay-human, P0:raw-values-fixed-or-raised, P1:independent-review-no-self-approval, P1:tests-before-production-code]
conflicts:
  - "The harness asks for a Co-Authored-By trailer on commits; task H2-5 says no AI attribution trailer. The draft has none."
  - "Connected docs servers offered to publish deliverables; the user's rule keeps them as local repo files."
note: "stream_index is the Nth audio stream everywhere; Extract picks the extension at that position, plans positions 0..k-1, fails a missing track at add and saves no encoder."
slim_candidate: ["The handoff's cross-reference AC rows for earlier MEUs exist only for the AC check."]
overthinking_observed: false
review_churn:
  rounds_to_approval: {plan: 1, execution: 1}
  findings_per_round:
    - {review: plan, round: 1, critical: 0, high: 0, medium: 1, low: 0}
    - {review: execution, round: 1, critical: 0, high: 0, medium: 0, low: 0}
  churned_findings: 0
  finding_categories: {boundary_validation: 1}
  verdicts: {approved: 2}
meu_work_classes: [correctness]
```
