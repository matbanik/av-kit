---
date: "2026-11-09"
project: "release-rc2"
meus: ["MEU-125"]
plan_source: "docs/execution/plans/2026-11-08-release-rc2/implementation-plan.md"
template_version: "2.0"
---

# 2026-11-09 Meta-Reflection

> **Date**: 2026-11-09
> **MEU(s) Completed**: MEU-125 `dist-release-candidate-2` (grouping D-243). Session 57 moved every version surface to 0.1.0-rc.2, added the libdvdcss line to the notices (D-275), built the installer from a clean tree with the pinned FFmpeg, checked it as RC1 was checked plus MEU-114's round trip and MEU-117's and MEU-121's smokes on the installed copy, ran a fresh gate, and wrote the notes and the publish checklist. Nothing is tagged, uploaded or published, and no product issue closes
> **Plan Source**: `docs/execution/plans/2026-11-08-release-rc2/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   - **The gate ran six times.** Run 1 stopped at `task-contract`: row 6's corrected cell held three bare `|` and split into 13 cells. Run 2 stopped at AC-81.11 because a screenshot tool Mat had running held F2 system-wide; Mat stopped it ("ShareX stopped"). Run 3 passed, and writing its line into the notes, a gated input, moved the tested_state, so run 4 reran on the finished notes. Run 5 followed D-475's rewording and run 6 followed execution review F1's checklist fix. Every run's receipts are kept under `C:/Temp/av-kit/s57/`. Only runs 3 to 6 made D-464's audit requests.
   - **The plan review cost 23,146,595 over three recorded rounds.** Round 1 (13,056,333) found four High blocking findings and a Medium. Round 2 (9,151,966) approved with all five closed, but its Prior Pass Summary wrote `✅ Fixed`, which the closeout parser reads as still open. Round 3 (938,296) only rewrote the cells as bare `fixed` (RULE-5).
   - **Row 3 stopped twice before the build.** `clean-tree.py` refused 9 untracked paths of the capture-crop-copy session (D-471 B, `--leave-out`). The first build then stopped at the offline guard, because `@electron/get` fetches `SHASUMS256.txt` even with the zip cached (D-472 A, seeded from the lock-pinned `checksums.json`; RULE-3).

2. **What instructions were ambiguous?**
   - **The commit trailer, again.** The harness asks for a Co-Authored-By trailer. Task H2-5, citing `development-lifecycle.md:454`, says there is none. The draft follows H2-5.
   - **Whether the notes' gate line reruns the gate.** H1-2 writes the gate's last line into a gated input. H1-6b's "if inputs changed, re-run H1-2" settled it, at the cost of run 4.

3. **What instructions were unnecessary?**
   - H2-1's `view_file` row. H2-2's check validates the reflection against the same template and schema.

4. **What was missing?**
   - **A check of the notes' live-service claims against the gate's own receipts.** The notes said YouTube *is* blocking the test network. Runs 3 and 4 fetched and compiled captions on that network. The coordinator caught it only when reading run 4's audit before the review (D-475, RULE-1).
   - **For each checklist outcome, every line it makes false.** Step 6 changed one part of the notes per outcome and left the Known problems item or the other-network line false. That was execution review F1 (RULE-2).
   - **The Electron checksum fetch in `offline-probe.ps1`** (RULE-3).
   - **A precheck that AC-81.11's global hotkey is free.** Its `DllImport` lacks `SetLastError`, so the fixture printed `0` where the probe found 1409, `ERROR_HOTKEY_ALREADY_REGISTERED` (RULE-4).
   - **The capability smoke's real post-state in the plan.** The plan said the models folder stays absent. The tool always creates it with a stub and `config.json` (D-473).

5. **What did you do that wasn't in the prompt?**
   - **Four plan-local changes, each on Mat's ruling:**
     - `clean-tree.py --leave-out` with four selftest cases (D-471);
     - the seeded `SHASUMS256.txt-42.11.18` (D-472);
     - `ruled-commits.txt` and the gate's ruled-commit acceptance in `scope-paths` (D-474);
     - the Transcript rewording of the notes and checklist (D-475).
   - **The F2 probe** (`f2-probe.ps1`). It registered F2 with `SetLastError` to name the holder's error. It ended no process.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **Row 1's Red:** the seven AC-110.9 tests and AC-72.7 failed by assertion on the rc.1 surfaces, and `red-check.py` found 0 problems.
   - **The gate's own audit receipts caught the notes' stale claim** (D-475). No test did.
   - **`clean-tree.py` refused another session's paths before anything was deleted** (S10). The offline guard stopped a fetch the probe had missed (S13).
   - **The execution reviewer's in-memory replay of checklist step 6 against the notes** found F1. Round 2's replay of all four outcomes passed.

7. **Which tests were trivially obvious?**
   - AC-110.20 and AC-110.21 pass in the Red by design. They guard a later surface slip, not this move.

8. **Did pyright/ruff catch anything meaningful?**
   - No. No product file changed apart from version strings.

### Workflow Signal Log

9. **Was the FIC useful as written?**
   - Yes. The 17 mechanism ids named the same contract in the plan, the handoff and both review prompts, and Codex cited `PUBLISH_CHECKLIST` for F1.

10. **Was the handoff template right-sized?**
    - It was heavy for a release. Six gate runs each needed their own Execution note, and the AC table's cited families (AC-72, AC-81, AC-110, AC-114, AC-117 and AC-121) exist mainly for the AC check (`slim_candidate`).

11. **How many tool calls did this session take?**
    - About 1,030 in this conversation's transcript at H2-2, across planning, three plan review rounds, rows 0 to 10, six gate runs, two execution review rounds and closeout.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    - None. The coordinator ran every row. Codex reviewed the plan and the execution as the independent reviewer, which isn't delegation.

### Decisions Log

| ID | Stage | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|-------|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-214 | triage | Which FFmpeg build replaces the pinned BtbN GPL build so libdvdcss leaves the package? | human | Superseded by D-266, not built | Human-approved | Mat first accepted this route through a brief with no do-nothing option, then chose to keep FFmpeg as it is (D-266). This session built with the unchanged pin. | USER_EXPLICIT 2026-11-04 'All ohter recommendations are accepted' |
| D-215 | triage | Does v0.1.0-rc.1 stay publicly downloadable until a build without libdvdcss replaces it? | human | RC1 stays up; its fate when rc.2 replaces it is Mat's in MEU-125's checklist | Human-approved | Each download can't be recalled, but the audience is very small and rc.2 supersedes it. This session's checklist carries D-467's note step. One-way. | USER_EXPLICIT 2026-11-04 'FFmpeg, keeping libdvdcss in rc.2: yes' |
| D-216 | triage | When are the public RC1 notes corrected, and what waits for the other-network check? | human | Follow D-215; the 'your network' wording waits for the other-network check | Human-approved | No other-network result arrived by row 8, so rc.2's notes use D-466's alternative and drop the cause claim. The check stays in the checklist's step 6. | USER_EXPLICIT 2026-11-04 'All ohter recommendations are accepted' |
| D-222 | triage | Which models folder is right, and what changes? | autonomous | The backend default `~/.avkit/models` stands; the readiness probe uses the same default | Local Canon | Moving the default would strand users' files. rc.2's notes describe that one default. Two-way. | — |
| D-240 | grouping | Where does session numbering start? | autonomous | 49 | Local Canon | Starting at 49 reuses no number. Two-way. | — |
| D-241 | grouping | Are the transcript title and channel name two MEUs? | autonomous | One, MEU-122 | Local Canon | Same enumeration, change and test fake. Two-way. | — |
| D-242 | grouping | Where do the riders go? | autonomous | By shared file | Local Canon | A rider needs a session already working in that file. The light accent first sat in MEU-118 as a rider; D-249 replaced that. Two-way. | — |
| D-243 | grouping | Does rc.2 get its own MEU? | autonomous | Yes, MEU-125 | Local Canon | MEU-110 is approved and closed, and reopening it would hide the new gate. This session is MEU-125 and closes it. Two-way. | — |
| D-244 | grouping | Which session runs first? | autonomous | Fetch and uninstall, Session 49 | Local Canon | It was the smallest, and MEU-125 reused its round-trip script, which this session ran on the full build. Two-way. | — |
| D-245 | grouping | Is TTS one session or two? | autonomous | Two, Sessions 51 and 52 | Local Canon | The FP16 cause hunt has no upper bound and shouldn't hold the download refusal. Two-way. | — |
| D-246 | grouping | Where does the FFmpeg build run, and where does the rebuilt archive live? | human | Withdrawn: no build runs | Human-approved | Mat kept FFmpeg as it is (D-266). This session's gate bound the pinned pair, unchanged. | USER_EXPLICIT 2026-11-04 "FFmpeg, keeping libdvdcss in rc.2: yes" |
| D-247 | grouping | Do errors always go to a file? | human | Yes: errors always go to a file. Session 50's plan carried it out | Human-approved | It changes a default the user sees, so it was Mat's to rule. D-296 carried it out. | USER_EXPLICIT 2026-11-05 "D-247: yes they should go to file" |
| D-248 | grouping | Does Mat's "Proceed" confirm the grouping for the D-234 scoping review? | autonomous | Yes, with the §3 changes listed for Mat to check | Local Canon | Waiting would stop work Mat asked to go ahead, and the grouping stays reversible. Two-way. | USER_EXPLICIT 2026-11-04 "All ohter recommendations are accepted. Proceed" |
| D-249 | grouping | Does the light accent stay in MEU-118? | autonomous | No: its own MEU-126 in Session 56, optional for rc.2 | Local Canon | Scoping review F1: a separate cause, separate tests and a separate human check. Session 56 approved MEU-126 before this build, so rc.2 carries it. Two-way. | — |
| D-250 | grouping | Does Batch E stay one session? | autonomous | No: MEU-123 in Session 54 and MEU-124 in Session 55 | Local Canon | Scoping review F2: they share no file. Two-way. | — |
| D-266 | triage | Does FFmpeg stay the stock BtbN GPL build, with libdvdcss in it, in rc.2 and later? | human | Yes; no build and no new pin | Human-approved | A self-built FFmpeg would lose other builders' updates. This session's build used the unchanged pin, and the gate's build record binds it. One-way. | USER_EXPLICIT 2026-11-04 'FFmpeg, keeping libdvdcss in rc.2: yes' |
| D-267 | grouping | Do the two remaining fixes stay in one session now they share no file? | autonomous | Yes, Session 49 keeps MEU-113 and MEU-114 | Local Canon | Each is a few lines, and a second plan and review would cost more than they save. Two-way. | — |
| D-275 | triage | Do the third-party notices name libdvdcss? | human | Yes: one factual line in the FFmpeg section, in MEU-125 | Human-approved | The name is already public, so the line adds prominence, not new information. This session added it (`NOTICE_LINE`, AC-72.7's needles). Not legal advice. One-way. | USER_EXPLICIT 2026-11-05 'all recommendations are accpeted, proceed' |
| D-277 | grouping | Does Codex recheck the grouping after round 1's fixes? | human | No. The scoping loop stays `changes_required`, recorded as not rechecked | Human-approved | Both findings were session splits, and both were applied. Each session's plan review covers its own scope, as this one's did. | USER_EXPLICIT 2026-11-05 "all recommendations are accpeted, proceed" |
| D-280 | grouping | Does the tooling session get an MEU? | autonomous | No: Session 49b is tracked by its issue | Local Canon | MEUs are build-plan product work, and Session 49b ships nothing. Two-way. | — |
| D-362 | execution | What happens with the one-off E2E seam reload failure? | human | File it as MONITORING, P4, and watch it in Session 57's gate, with no code change now | Human-approved | One failure can't show that a fix works. W2-4 passed in every gate run that reached `ui-electron`, so D-470's rerun rule never fired and no fix landed. Two-way. | USER_EXPLICIT 2026-11-07 'all recommendations are accepted' |
| D-460 | planning | In what order do the rows run? | autonomous | Baseline; the Red; the Green; clean tree, build and record; the checks on win-unpacked; the round trip; the two smokes on the installed copy; the notes; the checklist; the records | Local Canon | Every check needs the one recorded installer, and the documents follow the checks so they report results (`implementation-plan.md:475`). Two-way. | — |
| D-461 | planning | How do the version surfaces and the notices move, and what proves it? | autonomous | VERSION_ONE and NOTICE_LINE: Red on AC-110.9 and AC-72.7, then `version-bump.py --apply` with exact counts and endings, and the offline lock checks | Local Canon | The tests already pin every surface, and the scripted bump can't miss an occurrence or change an ending (`implementation-plan.md:485`). Two-way. | — |
| D-462 | planning | How is the installer built and tied to the tree, and what is a clean tree? | autonomous | Session 44's build and record scripts; CLEAN_TREE by `clean-tree.py` before anything is deleted | Local Canon | RC1's scripts proved the order and the record. The check refused another session's paths, which led to D-471 (`implementation-plan.md:495`). Two-way. | — |
| D-463 | planning | What does the round trip add to Session 49's for the full build? | autonomous | The record check and root smoke back, INSTALLED_COPY for the smokes, both install folders, and ROUNDTRIP_SAFETY as AC-125.12 to AC-125.15 | Local Canon | The installer's own backend is what users get, so the smokes ran on a copy of it (`implementation-plan.md:505`). Two-way. | — |
| D-464 | planning | How does the session gate treat the live mcp-audit while YouTube blocks captions, and which live requests does it make? | human | A: the MEU-116-shaped AUDIT_RULE with exactly the listed requests | Human-approved | No run needed the tolerance: runs 3 to 6 each passed 99 of 99, and Transcript fetched and compiled captions. Doing nothing would have left the gate unable to finish while the block lasted. | USER_EXPLICIT 2026-11-09 'all recommendations accpeted proceed' |
| D-465 | planning | Where do the notices point for the FFmpeg source, and under what name? | human | A: the rc.2 tag, with the cached archive attached unchanged under its rc.1 name | Human-approved | Each release's source sits beside its own binaries and keeps the SHA-256 RC1 published. Two-way. | USER_EXPLICIT 2026-11-09 'all recommendations accpeted proceed' |
| D-466 | planning | What do the release notes say about Transcript while the other-network check is open (D-216)? | human | The alternative: the measured block and retry advice, a line that the check hasn't run, and no cause claim | Human-approved | No result arrived by row 8, so the alternative stands. D-475 later restated it as today's facts. | USER_EXPLICIT 2026-11-09 'all recommendations accpeted proceed' |
| D-467 | planning | What does the checklist do with RC1 after rc.2 is published? | human | A: keep RC1 with its assets, add a first line 'Replaced by v0.1.0-rc.2', and set it not latest | Human-approved | It is reversible and keeps RC1's links working. A draft or a delete can break links or can't be undone. One-way. | USER_EXPLICIT 2026-11-09 'all recommendations accpeted proceed' |
| D-468 | planning | Which checks does the session gate run, and where do values go? | autonomous | RC1's gate: every suite, the builds, OpenAPI, the renders, the build record, the whole Electron suite and mcp-audit under AUDIT_RULE | Local Canon | The release carries every page and tool, so the gate runs every suite (`implementation-plan.md:515`). Two-way. | — |
| D-469 | planning | How do row 10 and H2-2 write MEU-125's status? | autonomous | GUARDED_STATUS_WRITE through Session 56's `status-write.py` | Local Canon | The status tool saves whole files without a lock. The guard costs one script that already passed its selftest (`implementation-plan.md:525`). | — |
| D-470 | planning | How does the session handle the watch item E2E-TRANSCRIPT-SEAM-RELOAD-FLAKE? | autonomous | W2-4 runs in the gate; a failure reruns once, a second failure lands the fix | Human-approved | The brief and the register give the rule. W2-4 passed in every run that reached it (`implementation-plan.md:535`). Two-way. | — |
| D-471 | execution | Row 3's clean-tree check refused 9 untracked paths of the capture-crop-copy session; how does the build proceed? | human | B: leave the 9 paths out with a repeatable `--leave-out` that refuses any build input | Human-approved | None of the 9 is a build input, by `build-identity.py`'s own test. Doing nothing would have stopped the release until that session committed. Two-way. | USER_EXPLICIT 2026-11-09 'B' |
| D-472 | execution | The first build stopped at the offline guard because `@electron/get` fetches `SHASUMS256.txt` even with the zip cached; how does the build get it? | human | A: seed the cache file from the lock-pinned `checksums.json` after checking the zip against it | Human-approved | No new input enters the build and nothing is downloaded. Doing nothing would have stopped the build. Two-way. | USER_EXPLICIT 2026-11-09 'A' |
| D-473 | execution | Row 6 expected the capability models folder to stay absent, but the smoke tool always creates it; what changes? | human | A: correct row 6, AC-125.17 and the plan to match the tool | Human-approved | The smoke passed; the plan misread its post-state. Doing nothing would have left row 6 failing against a wrong expectation. Two-way. | USER_EXPLICIT 2026-11-09 'A' |
| D-474 | execution | HEAD moved through Mat's commits `cbc6e22` and `8ce8b95` after row 7; does the session go on? | human | Accept the commits: `ruled-commits.txt`, and `scope-paths` accepts only ruled, docs-only commits | Human-approved | Both commits are docs-only and the build record still matched the tree. Doing nothing would have stopped the session at S3. Two-way. | USER_EXPLICIT 2026-11-09 'Accept the commits (Recommended)' |
| D-475 | execution | The gate fetched and compiled captions on the test network, but the notes and checklist said YouTube is blocking it; what do they say? | human | Reword to today's facts, keeping YOUTUBE-CAPTIONS-IP-BLOCK and the open installed-path and other-network checks | Human-approved | The present-tense claim contradicted the gate's own receipts. The audit ran through a checkout's backend, so the installed-app gap stands. Doing nothing would have shipped a disproved claim. Two-way. | USER_EXPLICIT 2026-11-09 'Reword to today's facts (Recommended)' |

---

## Pattern Extraction

### Patterns to KEEP
1. **The build record binds the installer to the tree, and the gate re-verifies it.** It let D-474 accept two docs-only commits without rebuilding.
2. **The clean-tree check runs before anything is deleted.** It stopped on another session's files and left them untouched (D-471).
3. **Keep each failed gate run's receipts in its own folder.** Six runs stayed traceable, and the reviewer reconstructed round 1's state from them.
4. **The reviewer replays the checklist's outcomes against the notes in memory.** It found F1 and proved the fix.

### Patterns to DROP
1. **Writing a gate's result into a gated input after the gate.** It cost a full rerun (run 4). The notes' test line can cite the gate receipt in a non-gated file, or the gate can write it before the identity is computed.

### Patterns to ADD
1. **Before the review, check every live-service sentence in the release notes against the gate's audit receipts** (RULE-1).
2. **List every line each checklist outcome makes false** (RULE-2).
3. **Run a full warm-cache offline build in the plan's probe** (RULE-3).
4. **Precheck system-wide resources before an E2E suite** (RULE-4).
5. **Ask for bare closure words in recheck cells** (RULE-5).

### Calibration Adjustment
- **Estimated time:** a day (Session 56's Next Day Outline).
- **Actual time:** about 21 hours of transcript time, 2026-11-08T23:41Z to closeout after 2026-11-09T15:40Z, including Mat's answers and seven human rulings. Each full gate run took about an hour.
- **Codex cost:** the plan review 23,146,595 over three rounds, and the execution review 12,734,912 over two (10,020,084 and 2,714,828) against the 60M budget.
- **Adjusted estimate for a release candidate:** a day and a half, plus one gate run for each gated document edit. Budget about 13M for a first plan round and about 10M for a first execution round. A narrow recheck costs 1M to 3M.

---

## Next Session Design Rules

```
RULE-1: Before the execution review, every sentence in the release notes about a live service (YouTube, a CDN, a network block) is checked against the gate's own audit receipts, and a sentence the receipts contradict is raised to the human before the review.
SOURCE: The notes said YouTube is blocking the test network, while gate runs 3 and 4 fetched and compiled captions on that network (transcripts_done 1, 112,778 B); caught only when reading run 4's audit, it needed D-475 and a fifth gate run.
EXAMPLE: "row 8 writes RC1's measured block" → "row 8 writes RC1's measured block; H1-2 greps the notes' Transcript claims against s57-D6-mcp-audit and stops on a contradiction".
```

```
RULE-2: A checklist step that tells the maintainer to edit the notes for each outcome of a check lists, for each outcome, every line in the notes that the outcome makes false, by quoted anchor, the section and its Known problems item alike.
SOURCE: Execution review F1 (High): step 6's success row removed the section but left the Known problems item saying the path was unverified, and its blocked row left "Transcript hasn't been tried from another network."
EXAMPLE: "On success, remove the section" → "On success, remove the section `Transcript on this build` and replace the Known problems item that starts `The installed app's Transcript path isn't verified` with …".
```

```
RULE-3: A plan that builds offline runs a full warm-cache build behind the offline guard in its probe, rather than probing each cache separately, so a fetch the build tool makes despite a warm cache shows up at plan time.
SOURCE: Row 3's first build stopped at S13: @electron/get fetches SHASUMS256.txt on every build even with the zip cached (electronGet.js:627-634), which offline-probe.ps1's per-cache cases didn't cover (D-472).
EXAMPLE: "offline-probe.ps1: 7 cache cases" → "offline-probe.ps1: 7 cache cases plus one build-rc.ps1 -DryRun under the guard".
```

```
RULE-4: A gate that runs E2E tests registering system-wide resources (global hotkeys, ports) checks each is free before the suite and names the holder's error, so a third-party program is told apart from a product failure.
SOURCE: Gate run 2 failed AC-81.11 with "F2 held by another process", Received FAILED 0; a probe with SetLastError got 1409 (ERROR_HOTKEY_ALREADY_REGISTERED) from a screenshot tool, which the fixture's DllImport without SetLastError couldn't report.
EXAMPLE: "ui-electron: run the suite" → "ui-electron: f2-probe registers and releases F2 first, stops with 1409 and asks the human".
```

```
RULE-5: A recheck prompt asks for the Prior Pass Summary's Recheck Result cells as the bare words fixed or open, with no emoji or bold, and the coordinator runs the review-state parse on the report before recording it as the closing round.
SOURCE: Plan review round 2 approved with `✅ Fixed` cells, which the closeout parser reads as open, so round 3 (938,296 tokens) only rewrote them.
EXAMPLE: "| F1 | open | ✅ Fixed |" → "| F1 | open | fixed |".
```

---

## Next Day Outline

1. **Target:** done in the tree, not committed. MEU-125 is approved, and the commit waits on Mat's words. Tagging, the draft release, uploading, the clean-machine check, the Transcript recheck, publishing and RC1's note are Mat's, in order, in `docs/releases/publish-checklist-v0.1.0-rc.2.md`.
2. **Next session:** Session 58 `capture-region-import`, the first capture-crop session, from the committed Session 58 plan. Its prompt is `C:/Temp/av-kit/session-58-prompt.md`.
3. **Scaffold changes needed:**
   - REVIEW-TEMPLATE's `✅ Fixed` against the closeout parser (RULE-5).
   - The offline probe's build-level case (RULE-3).
   - AC-81.11's `SetLastError` (RULE-4).

   Each is proposed for the register, on Mat's ruling.
4. **Patterns to bake in from today:** RULE-1 to RULE-5 here, plus Sessions 50 to 56's rules, all of which carry.
5. **Codex validation scope:** Session 58's execution, its plan being committed.
6. **Time estimate:** Session 58 is a capture GUI session, so about a day.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | About 1,030 in this conversation's transcript at H2-2 |
| Time to first green test | Green at 2026-11-09T00:16:04-05:00 after the Red at 00:15:10-05:00 (`s57-red.txt`, `s57-green-tests.txt`) |
| Tests added | None. pytest 1357 → 1357, Vitest 1183 → 1183 (113 files), MCP 470 → 470, Electron 190. The Red moved constants and needles inside existing tests (AC-110.9, AC-72.7) |
| Codex findings | **Plan review:** round 1 had 4 High blocking findings and 1 Medium: the traffic inventory, CLEAN_TREE ignoring baseline-dirty paths, the offline build falling back to downloads, and D-466's fallback keeping D-216's claim; plus `NO_RAW_CONSOLE`'s home-path overstatement. It cost 13,056,333. Round 2 approved with all five fixed (9,151,966). Round 3 approved, rewriting the closure cells only (938,296). **Execution review:** round 1 had 1 High blocking finding, F1, step 6 leaving the notes partly false (10,020,084). Round 2 approved with F1 fixed (2,714,828), 12,734,912 of the 60,000,000 budget |
| Handoff Score (X/7) | 7/7. Every AC has evidence, every gate run's receipts are kept, and each stop and its ruling is disclosed |
| Rule Adherence (%) | 91 (20 of 22 triggered rules followed in full, 2 in part; 3 more were not triggered) |
| Prompt→commit time | Planned 2026-11-08 and executed 2026-11-09. Not committed; waiting on Mat |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Tests before production code; Red before Green | AGENTS.md §Testing & TDD | Yes. Eight Reds failed by assertion and `red-check.py` reported 0 problems before row 2 |
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Both canonical reviews are Codex's reports, validated under `C:/Temp/av-kit` and copied byte for byte |
| A raw value that can reach a log, stdout or the Console is fixed in the row or raised | Session 50 rule | Yes. No product log line changed. The round trip writes `<HOME>`, and the committed record holds relative paths |
| `test-ids.ts` additions go in an additive block | Session 50 rule | Not triggered. No test id was added |
| tested_state prompts name the user git ignore and `.claude/settings.local.json` | Session 51 RULE-4 | Yes. Every review prompt names them, and both reviewers reconciled without opening the file |
| Probe register keys | Session 51 RULE-2 | Yes. `s57-decision-issue-probe.txt` |
| Re-read lines and correct moved cites | Session 51 RULE-3 | Yes. The handoff lists 07's moved `---` |
| Every command through RTK | AGENTS.md §RTK | Partly. Test, build, gate and tool runs went through `rtk proxy`. Many reads did not, and the RTK hook isn't installed on this PC |
| The recheck prompt gives the literal Prior Pass Summary table | Session 52 RULE-1 | Partly. The plan's round 2 prompt allowed the template's `✅ Fixed`, which cost round 3. The execution recheck asked for bare words |
| A loop's budget is compared with the last comparable round | Session 52 RULE-3 | Yes. The ask fired after plan round 1, and Mat set 60M |
| Assert a new name exists before patching | Session 52 RULE-4 | Yes. Every focus and handoff script asserts each marker occurs once |
| Shared missing names go in a type-only row first | Session 53 RULE-2 | Not triggered. No row adds a name (D-461) |
| A gate step that fails in an untouched file is rerun once unchanged | Session 53 RULE-4 | Yes. AC-81.11's F2 failure was probed and raised to Mat, then rerun unchanged once the holder stopped |
| A real-stack test with a positive control | Session 54 RULE-2 | Yes. The capability smoke's refused download is checked against `files_unchanged` |
| Handoff checks before the review prompt | Session 54 RULE-3 | Yes. H1-6, H1-6a and H1-6b passed before each execution dispatch |
| A cited authorization is checked with grep | Session 54 RULE-4 | Yes. Each D-471 to D-475 quote is in the handoff's decision_log |
| The decision probe names the plan; decision_log slots are words | Session 54 RULE-5 | Yes. The probe read the plan, and the closeout passes one `--decision-issue` per issue |
| Name each caller and run its tests in the Green | Session 55 RULE-1 | Yes. Row 2 ran every reader of the version and notices |
| Save, diff and disclose before a tool rewrites another session's file | Session 55 RULE-2 | Yes. `status-write.py` kept the bytes and wrote the diff at row 10 |
| `PYTHONIOENCODING=utf-8` | Session 55 RULE-5 | Yes. Every wrapper sets it |
| Generated wrappers take raw-string paths and are checked for control characters | Session 56 RULE-1 | Yes. `s57-plan-line-endings.txt` |
| A human-check row stops its own launch | Session 56 RULE-2 | Not triggered. No row launched the app for a human look |
| Each tooling safety property is its own AC | Session 56 RULE-3 | Yes. ROUNDTRIP_SAFETY is AC-125.12 to AC-125.15, and GUARDED_STATUS_WRITE is AC-125.22 |
| No branches or worktrees; never commit or push without the human | AGENTS.md §Commits | Yes. The work is on `main`, and nothing is committed |
| Decision briefs keep a do-nothing option | HDP | Yes. Each of D-464 to D-467 and D-471 to D-475 listed doing nothing |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "c298dd10-9c50-4a71-8baf-ddc623238fad"
  task_class: other
  outcome: success
sections:
  - {id: priority_0_system_constraints_non_negotiable, cited: true, influence: 3}
  - {id: planning_contract, cited: true, influence: 3}
  - {id: testing_tdd_protocol, cited: true, influence: 2}
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
    - docs/build-plan/07-distribution.md
decisive_rules: [P0:never-commit-or-push-without-human-approval, P0:never-publish-tag-or-upload, P0:human-decisions-stay-human, P1:independent-review-no-self-approval, P1:fresh-gate-on-changed-inputs]
conflicts:
  - "The harness asks for a Co-Authored-By trailer on commits; task H2-5 and development-lifecycle.md:454 say no AI attribution trailer. The draft has none."
  - "Connected docs servers offered to publish deliverables; Mat's rule keeps them as local repo files."
  - "REVIEW-TEMPLATE.md shows the Recheck Result as an emoji closure, which the closeout parser reads as still open."
note: "rc.2's surfaces, notices, installer, packaged checks, round trip and smokes passed; six gate runs, as gated documents changed after each."
slim_candidate: ["The handoff's cross-reference AC rows for earlier MEUs exist only for the AC check.", "H2-1's view_file row duplicates H2-2's template and schema check."]
overthinking_observed: false
review_churn:
  rounds_to_approval: {plan: 3, execution: 2}
  findings_per_round:
    - {review: plan, round: 1, critical: 0, high: 4, medium: 1, low: 0}
    - {review: plan, round: 2, critical: 0, high: 0, medium: 0, low: 0}
    - {review: plan, round: 3, critical: 0, high: 0, medium: 0, low: 0}
    - {review: execution, round: 1, critical: 0, high: 1, medium: 0, low: 0}
    - {review: execution, round: 2, critical: 0, high: 0, medium: 0, low: 0}
  churned_findings: 0
  finding_categories: {boundary_validation: 2, claim_to_state_drift: 3, contract_drift: 1}
  verdicts: {changes_required: 2, approved: 3}
meu_work_classes: [mixed]
```
