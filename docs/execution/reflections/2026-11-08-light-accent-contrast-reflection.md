---
date: "2026-11-08"
project: "light-accent-contrast"
meus: ["MEU-126"]
plan_source: "docs/execution/plans/2026-11-08-light-accent-contrast/implementation-plan.md"
template_version: "2.0"
---

# 2026-11-08 Meta-Reflection

> **Date**: 2026-11-08
> **MEU(s) Completed**: MEU-126 `gui-light-accent-contrast`. Session 56 closes LIGHT-ACCENT-BELOW-AA-CONTRAST (Mat's D-235, grouping D-249): the light `--color-accent` is `#155e75` and `--color-accent-hover` is `#164e63`, and the dark theme is unchanged. Planning found the TTS status pill below 4.5:1 in both themes; Mat chose to keep the scope and file it (D-455, `TTS-STATUS-PILL-BELOW-AA-CONTRAST`, open P3)
> **Plan Source**: `docs/execution/plans/2026-11-08-light-accent-contrast/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   - **The plan review cost about 11.5M tokens for one recorded round.** The first dispatch, `s56-plan-r1`, found three High blocking findings, all in row 4's and row 5's inline cells: the leftover-process check matched its own command line (F1), its diagnostic printed a slice of each command line, which carries the backend's `--token` and `--mcp-token` (F2), and the save-and-diff around `tools/meu_status.py` could not see a capture-crop write lost between the tool's load and its save (F3). The ledger refused to record that round, about 6.14M, because F3 cited PR-8, which isn't a registered family, and no AC stated F2's or F3's property. Mat accepted the routing (D-459): two new ACs, AC-126.9 (LAUNCH_OWNERSHIP, NO_RAW_CONSOLE) and AC-126.10 (GUARDED_STATUS_WRITE), the plan-local `dev-app-procs.py` and `status-write.py` with selftests, and a re-dispatch, `s56-plan-r1b`, which the ledger recorded as round 1 and approved with F1 to F3 closed at 5,348,587 (RULE-3).
   - **Row 3's first validation failed at the settings E2E.** Playwright's `mkdir` got `ENOENT` on a TMP path in which my Python-written `.ps1` wrapper had turned `\a` and `\t` into control characters. The tokens, the re-baseline, the twelve unit files, typecheck, lint and build had passed. I rewrote the header as a raw string, checked every wrapper for control characters and reran the whole cell: 24 of 24. Both receipts are kept (RULE-1).

2. **What instructions were ambiguous?**
   - **The commit trailer, again.** The harness asks for a Co-Authored-By trailer, and task H2-5, citing `development-lifecycle.md:454`, says the commit has none. The draft follows H2-5 and Mat's brief.
   - **Where D-458 is recorded.** It opened at row 4, after the plan was approved, so it isn't in the plan's `decision_log` block. The plan says it goes into `human-check.md`, the handoff and this reflection with stage `execution`, and that is where it is.

3. **What instructions were unnecessary?**
   - H2-1's `view_file` row. H2-2's check validates the reflection against the same template and schema.

4. **What was missing?**
   - **ACs for the plan's own tooling.** The plan stated the product's properties as ACs, but not the properties of the scripts that inspect processes and write another session's files, so the reviewer's findings against them had nothing to cite and the ledger refused the round (RULE-3).
   - **A control-character check on generated wrappers.** The TMP path was right in the Python source and wrong in the `.ps1` it wrote (RULE-1).
   - **A stop step for the human check.** Mat answered in chat and left the app open, as a person looking at a window would. Row 4's `check` then listed 14 of this launch's processes and exited 1; `check --stop` ended them by id and listed 0, as the row allows (RULE-2).
   - **A selftest that doesn't depend on the row it guards.** `status-write.py --selftest` copies the live status files, so its stale-save case only bites while MEU-126 reads something other than the `ready_for_review` it writes. Between row 5 and H2-2 it read `ready_for_review`, and the case failed on the live tree. The execution reviewer replayed the selftest on the saved pre-row-5 copies, where it passed 9 of 9; after H2-2 set `approved` it passes on the live tree again (RULE-4).

5. **What did you do that wasn't in the prompt?**
   - **Filed `TTS-STATUS-PILL-BELOW-AA-CONTRAST`** at row 5 on Mat's D-455, with the probe of both themes' ratios.
   - **Wrote seven plan-local scripts with selftests:** `identity.py`, `red-check.py`, `matrix-rebaseline.py`, `dev-app-procs.py`, `status-write.py`, `issue-file.py` and `issue-resolve.py`. `dev-app-procs.py` and `status-write.py` came from plan review F1 to F3.
   - **Recorded the capture-crop session's three changed paths** with their SHA-256 at H1-2 and in the handoff. They changed at 13:30:57 local, before the gate, and this session didn't write them.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **Row 1's five Reds failed by assertion on the shipped `#0891b2`:** white on the accent 3.68:1, the 12% tint 2.82 to 3.20:1, the 20% tint 2.59 to 2.90:1, the 15% segmented tint 2.87 and 3.09:1, accent text 3.41 and 3.68:1. `red-check.py` required all five and found 0 problems.
   - **AC-126.8 failed on `rgb(8, 145, 178)` after its dark steps passed,** so the positive control held and the failure was the light token, not the toggle.
   - **AC-43.3, an earlier MEU's contrast matrix,** pinned 40 light values the ruled accent moves. `matrix-rebaseline.py` replaced exactly those under Mat's D-456 authorization, every label still at 4.5:1 or more.
   - **The plan review's own probe** found the lowest live pair, the 20% hover on a selected queue card's 5% wash, at 4.62:1. D-451 added that backdrop to the test.

7. **Which tests were trivially obvious?**
   - AC-126.2 (white on the hover) passed in the Red at 5.36:1 and AC-126.7 (the dark tokens) passes by construction. Both guard a slip in a later token change rather than prove this one.

8. **Did pyright/ruff catch anything meaningful?**
   - No defect. No Python product file changed; the UI typecheck and ESLint stayed clean.

### Workflow Signal Log

9. **Was the FIC useful as written?**
   - Yes. LIGHT_ACCENT_TOKENS to GUARDED_STATUS_WRITE named the same contract in the plan, the Reds, the handoff and both review prompts, and Codex's execution report headed its Q2 to Q5 with them.

10. **Was the handoff template right-sized?**
    - Yes for one MEU of two tokens. The cross-reference rows for AC-43, AC-51, AC-81 and AC-94 were filler except AC-43's, which records the re-baseline (`slim_candidate`).

11. **How many tool calls did this session take?**
    - About 810 in this conversation's transcript at H2-2, across planning, two plan review dispatches, execution, the human check, the gate, the execution review and closeout.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    - None. The coordinator ran every row. Codex reviewed the plan and the execution as the independent reviewer, which isn't delegation.

### Decisions Log

| ID | Stage | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|-------|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-235 | triage | Does the light theme's `--color-accent` (`#0891b2`) change? | human | `--color-accent` `#155e75` and `--color-accent-hover` `#164e63`, with a look at the light theme before it ships | Human-approved | White labels go from 3.68:1 to 7.27:1. It changes how the whole light theme looks, so it was Mat's to rule. MEU-126 carried it out (LIGHT_ACCENT_TOKENS) and Mat's look is D-458. Two-way. | USER_EXPLICIT 2026-11-04 'All ohter recommendations are accepted' |
| D-240 | grouping | Where does session numbering start? | autonomous | 49 | Local Canon | Starting at 49 reuses no number. Two-way. | — |
| D-241 | grouping | Are the transcript title and channel name two MEUs? | autonomous | One, MEU-122 | Local Canon | Same enumeration, change and test fake. Two-way. | — |
| D-242 | grouping | Where do the riders go? | autonomous | By shared file | Local Canon | A rider needs a session already working in that file. The light accent first sat in MEU-118 as a rider; D-249 replaced that. Two-way. | — |
| D-243 | grouping | Does rc.2 get its own MEU? | autonomous | Yes, MEU-125 | Local Canon | MEU-110 is approved and closed. Reopening it would hide the new gate. Session 57 runs it. Two-way. | — |
| D-244 | grouping | Which session runs first? | autonomous | Fetch and uninstall, Session 49 | Local Canon | It's the smallest, and MEU-125 reuses its round-trip script. Two-way. | — |
| D-245 | grouping | Is TTS one session or two? | autonomous | Two, Sessions 51 and 52 | Local Canon | The FP16 cause hunt has no upper bound and shouldn't hold the download refusal. Two-way. | — |
| D-246 | grouping | Where does the FFmpeg build run, and where does the rebuilt archive live? | human | Withdrawn: no build runs | Human-approved | Mat kept FFmpeg as it is (D-266). This session's gate bound the pinned pair, unchanged. | USER_EXPLICIT 2026-11-04 "FFmpeg, keeping libdvdcss in rc.2: yes" |
| D-247 | grouping | Do errors always go to a file? | human | Yes: errors always go to a file. Session 50's plan carried it out | Human-approved | It changes a default the user sees, so it was Mat's to rule. D-296 carried it out. | USER_EXPLICIT 2026-11-05 "D-247: yes they should go to file" |
| D-248 | grouping | Does Mat's "Proceed" confirm the grouping for the D-234 scoping review? | autonomous | Yes, with the §3 changes listed for Mat to check | Local Canon | Waiting would stop work Mat asked to go ahead, and the grouping stays reversible. Two-way. | USER_EXPLICIT 2026-11-04 "All ohter recommendations are accepted. Proceed" |
| D-249 | grouping | Does the light accent stay in MEU-118? | autonomous | No: its own MEU-126 in Session 56, optional for rc.2 | Local Canon | Scoping review F1: a separate cause, separate tests and a separate human check. This session is MEU-126, and rc.2 didn't wait for it. Two-way. | — |
| D-250 | grouping | Does Batch E stay one session? | autonomous | No: MEU-123 in Session 54 and MEU-124 in Session 55 | Local Canon | Scoping review F2: they share no file. Two-way. | — |
| D-267 | grouping | Do the two remaining fixes stay in one session now they share no file? | autonomous | Yes, Session 49 keeps MEU-113 and MEU-114 | Local Canon | Each is a few lines, and a second plan and review would cost more than they save. Two-way. | — |
| D-277 | grouping | Does Codex recheck the grouping after round 1's fixes? | human | No. The scoping loop stays `changes_required`, recorded as not rechecked | Human-approved | Both findings were session splits, and both were applied. Each session's plan review covers its own scope, as this one's did. | USER_EXPLICIT 2026-11-05 "all recommendations are accpeted, proceed" |
| D-280 | grouping | Does the tooling session get an MEU? | autonomous | No: Session 49b is tracked by its issue | Local Canon | MEUs are build-plan product work, and Session 49b ships nothing. Two-way. | — |
| D-450 | planning | How does the contrast test read the tokens and compute each ratio? | autonomous | A new `light-accent-contrast.test.ts` reads both theme blocks of `styles.css`, holds its own helpers with the 0.04045 threshold and unrounded ratios, throws on a missing token, and copies neither ruled value | Local Canon | The contract asks for values read from the file, so a later token change is measured, not trusted. AC-43.3's helpers round to 2 dp, which would pass 4.496 as 4.50 (`implementation-plan.md:402`). Two-way. | — |
| D-451 | planning | Which tints does the test check, over which backdrops, and how is a tint composited? | autonomous | TINT_MODEL: the 12%, 20% and 15% tints over the page bg and the white surface, the 12% and 20% also over a selected queue card's wash; the accent at alpha N composited per channel in sRGB and rounded half up | Local Canon | The code draws three tints behind labels, so all three are checked. The selected card's 5% wash gives the lowest live pair, 4.62:1 on hover, which the plan review found (`implementation-plan.md:412`). Two-way. | — |
| D-452 | planning | How does the plan prove the running app paints the ruled colours? | autonomous | RUNTIME_COLOURS: AC-126.8 after AC-94.7 asserts the solid accent, hover and label colours in dark, light, then dark, with dark first as the positive control, pinned as rgb literals | Local Canon | The unit test reads the tokens, so a build that dropped them would still pass it; the E2E closes that gap. A screenshot diff breaks on any layout change (`implementation-plan.md:422`). Two-way. | — |
| D-453 | planning | Which checks does the session gate run? | autonomous | Session 55's shape: identity, static, the full Python, UI and MCP suites, the builds, the OpenAPI and render checks, the new test alone and the settings E2E; no package build or smokes | Local Canon | Row 5 writes registers that Python tests read, and the gate is the fresh full proof of the tree it binds. MEU-125 builds the installer (`implementation-plan.md:432`). Two-way. | — |
| D-454 | planning | How do this session's record writes share files with the capture-crop session's uncommitted edits? | autonomous | GUARDED_STATUS_WRITE: the three status files are written only through `status-write.py`, which holds them from first read to last write, refuses changes outside MEU-126 and the generated regions, keeps the bytes it read and writes the diff; H2-5 asks Mat before committing | Local Canon | The status tool saves whole files without a lock, so a peer save between its load and save would be lost (plan review F3). Holding the files makes that write fail loudly instead (`implementation-plan.md:442`). | — |
| D-455 | planning | The ruled light accent moves the TTS Generating pill's label from 3.97:1 to 2.01:1, and the pill already fails 4.5:1 for most statuses in both themes. Widen the session or keep its scope? | human | B: keep MEU-126 to the two ruled light tokens and file the whole TTS status pill as an open TECH-DEBT issue | Human-approved | Fixing Generating alone leaves the pill failing in dark, and fixing it whole changes the TTS page in both themes, outside D-235's two tokens. Filed as `TTS-STATUS-PILL-BELOW-AA-CONTRAST`, P3. Two-way. | USER_EXPLICIT 2026-11-08 'all recommendations accpeted, proceed' |
| D-456 | planning | AC-43.3 pins a contrast matrix that the ruled accent moves. How is it re-baselined? | autonomous | MATRIX_REBASELINE: `matrix-rebaseline.py` recomputes the matrix with AC-43.3's own algorithm and replaces exactly the 40 light values that move, every label at 4.5 or more and `_meta` unchanged; TEST_AMENDMENTS authorized by Mat at the plan gate | Local Canon | The matrix is data computed from the tokens. A script that refuses any other move keeps every other byte; editing 40 numbers by hand risks a typo AC-43.3 would pin (`implementation-plan.md:452`). | USER_EXPLICIT 2026-11-08 'all recommendations accpeted, proceed' |
| D-457 | planning | In what order do the rows run? | autonomous | Row 0 baseline; row 1 the unit Red; row 2 the build and the E2E Red; row 3 the tokens, the matrix and every caller's tests; row 4 Mat's look; row 5 records. No type-only row | Local Canon | No row adds a name, so a type-only row would hold nothing. Mat's look follows the Green so Mat sees the shipped tokens, and the records follow Mat's yes (`implementation-plan.md:462`). Two-way. | — |
| D-458 | execution | After the Green, does the light theme ship with `--color-accent` `#155e75` and `--color-accent-hover` `#164e63`? | human | Approve: the ruled light accent and hover ship, and the session goes on to the records and the execution review | Human-approved | D-235 asked for a look before the values ship. Mat saw the shipped tokens on the Downloader, Convert and Settings pages after the contrast test and the E2E passed. A no would have sent the hexes back as a new decision. Two-way. | USER_EXPLICIT 2026-11-08 'yes, approved  - everything looks good' |
| D-459 | plan-review | The ledger refused plan review round 1 because F3 cited PR-8, which isn't a registered family, and no AC stated F2's or F3's property. How are the findings routed? | human | F1 under AC-126, F2 under the new AC-126.9 and F3 under the new AC-126.10, and the revised plan re-dispatched as `s56-plan-r1b`, recorded as round 1; round 1's cost of about 6.14M stays disclosed outside the ledger | Human-approved | The ledger registers only the plan's AC ids and the closed mechanism catalogue, and neither the verdict nor the catalogue may be edited. Accepting the fixes unreviewed would leave the two new scripts unreviewed until after rows 4 and 5 used them (`implementation-plan.md:483`). Two-way. | USER_EXPLICIT 2026-11-08 'all recommendations accpeted, proceed' |

---

## Pattern Extraction

### Patterns to KEEP
1. **The token test reads the shipped file and keeps ratios unrounded** (D-450). It measured a later token change, the ruled one, without trusting it, and AC-43.3's rounding couldn't pass a 4.496.
2. **Dark first as the E2E's positive control** (Session 54 RULE-2, D-452). AC-126.8's Red failed on the light token after the dark steps passed, so the toggle was proven to work.
3. **A plan-local script with a selftest for every inline diagnostic that touches processes or another session's files.** `dev-app-procs.py` and `status-write.py` closed F1 to F3, and the reviewer re-ran both selftests.
4. **Mat's look after the Green and before the records** (D-457), so the answer was about the shipped tokens and a no would have left nothing to undo.

### Patterns to DROP
1. **Inline one-line process or file checks in a task cell.** All three plan review findings were in them.

### Patterns to ADD
1. **Write generated wrappers' Windows paths from raw strings and check the wrapper for control characters** (RULE-1).
2. **A human-check row stops its own launch before it checks for leftovers** (RULE-2).
3. **State the plan's tooling properties as ACs** (RULE-3).
4. **A plan-local selftest sets its fixture's starting state itself** rather than inheriting the live row it guards (RULE-4).

### Calibration Adjustment
- **Estimated time:** half a day (Session 55's Next Day Outline). The brief set the execution budget at 15M against Session 55's 11.6M round.
- **Actual time:** about 5 hours of transcript time, 2026-11-08T15:12Z to closeout after 20:07Z, Mat's answers included. The plan review cost about 11.5M (5,348,587 recorded), the execution review 9,980,641 in one round of 14 minutes.
- **Adjusted estimate for a token-only MEU with a human look:** half a day of agent time plus the look. Budget 6M per plan round once the tooling has ACs and selftests, and about 10M to 12M for an execution round whose reviewer re-runs selftests and recomputes values (this one 9,980,641).

---

## Next Session Design Rules

```
RULE-1: A wrapper that one language writes for another (Python writing .ps1 or .sh) takes every Windows path from a raw string, and is checked for control characters before it runs.
SOURCE: Row 3's first validation failed at the settings E2E: Playwright's mkdir got ENOENT because the Python-written .ps1 held C:\Temp\av-kit\s56\tmp with \a and \t turned into control characters.
EXAMPLE: header = "$env:TMP = 'C:\Temp\av-kit\s56\tmp'" → header = r"$env:TMP = 'C:\Temp\av-kit\s56\tmp'"; assert not re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", text).
```

```
RULE-2: A human-check row that launches the app ends the launch it recorded, by process id, before it checks that nothing of it is left; it doesn't expect the human to close the app.
SOURCE: Mat answered in chat with the app still open; row 4's check listed 14 of this launch's processes and exited 1, and check --stop ended them and listed 0.
EXAMPLE: "dev-app-procs.py check" after the answer → "dev-app-procs.py check --stop" after the answer, with the plain check as the row's later re-check.
```

```
RULE-3: A plan that adds a script which inspects processes, prints process data or writes another session's files states each safety property as its own AC, so a reviewer's finding against it has an AC to cite.
SOURCE: Plan review s56-plan-r1 found F1 to F3 in row 4's and row 5's inline cells; the ledger refused the round (about 6.14M) because F3 cited PR-8 and no AC stated F2's or F3's property; D-459 added AC-126.9 and AC-126.10.
EXAMPLE: "row 4: check no dev-app process is left" → "AC-126.9 LAUNCH_OWNERSHIP and NO_RAW_CONSOLE: the check counts only the recorded launch, never itself, and prints no command line".
```

```
RULE-4: A plan-local selftest sets the starting state of the row it guards in its own fixture copy, instead of inheriting whatever the live file holds, so it proves the same thing before and after the row runs.
SOURCE: status-write.py --selftest copies the live status files, and its stale-save case writes ready_for_review and expects a stale save to revert it. Between row 5 and H2-2 MEU-126 already read ready_for_review, so the stale save reverted nothing and the case failed on the live tree (execution review Q7); it passed on the saved pre-row-5 copies, and on the live tree again once H2-2 set approved (s56-h2-selftest-after-approve.txt).
EXAMPLE: "files = copies of the live status files" → "files = copies of the live status files, then MEU-126 set to pending in the copy before each case".
```

---

## Next Day Outline

1. **Target:** done in the tree, not committed. LIGHT-ACCENT-BELOW-AA-CONTRAST is resolved, MEU-126 is approved, and the commit waits on Mat's words. The tree also holds the capture-crop session's planning files, named to Mat before any commit.
2. **Next session:** Session 57 `release-rc2` (MEU-125), the rc.2 release candidate. Its prompt is `C:/Temp/av-kit/session-57-prompt.md`. Watch item: E2E-TRANSCRIPT-SEAM-RELOAD-FLAKE.
3. **Scaffold changes needed:** none.
4. **Patterns to bake in from today:** RULE-1 to RULE-4 here, plus Sessions 50 to 55's rules, all of which carry.
5. **Codex validation scope:** Session 57's plan.
6. **Time estimate:** Session 57 builds and smokes an installer, so a day.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | About 810 in this conversation's transcript at H2-2 |
| Time to first green test | Unit Green at 2026-11-08T13:36:43-05:00 after the Red at 13:34:50-05:00; E2E Green at 13:37:42-05:00 after its Red at 13:35:29-05:00 (`s56-unit-red.txt`, `s56-green-unit.txt`, `s56-e2e-red.txt`, `s56-green-e2e.txt`) |
| Tests added | Vitest 1176 → 1183 (+7, 112 → 113 files); settings E2E 24 of 24 with AC-126.8 new; pytest 1357 → 1357; MCP 470 → 470; AC-43.3's matrix moved 40 values |
| Codex findings | Plan review: `s56-plan-r1` refused by the ledger, 3 High blocking (self-matching check, token-bearing argv in the receipt, a lost peer write), about 6.14M outside the ledger; `s56-plan-r1b` recorded as round 1, approved, F1 to F3 closed, 5,348,587. Execution review: `s56-exec-r1` approved in round 1, no findings, intent achieved, 9,980,641 of the 15,000,000 budget; its Q7 noted the state-dependent stale-save case in `status-write.py --selftest` as an observation, not a finding (RULE-4) |
| Handoff Score (X/7) | 7/7. Every AC has evidence, the gate passed every step on its first run, and row 3's bad-TMP run and row 4's stop are disclosed |
| Rule Adherence (%) | 95 (20 of 21 triggered rules followed in full, 1 in part; 3 more were not triggered) |
| Prompt→commit time | Planned and executed 2026-11-08; not committed, waiting on Mat |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Tests before production code; Red before Green | AGENTS.md §Testing & TDD | Yes. Five unit Reds and the E2E Red failed by assertion, and `red-check.py` reported 0 problems before row 3 |
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Both canonical reviews are Codex's reports, validated under `C:/Temp/av-kit` and copied byte for byte |
| A raw value that can reach a log, stdout or the Console is fixed in the row or raised | Session 50 rule; the brief | Yes. F2 was the case; `dev-app-procs.py` prints ids, roles and owners only, and its selftest feeds a token-bearing argv |
| `test-ids.ts` additions go in an additive block | Session 50 rule | Not triggered. AC-126.8 uses existing test ids, and scope-paths confirmed `test-ids.ts` unchanged |
| tested_state prompts name the user git ignore and `.claude/settings.local.json` | Session 51 RULE-4 | Yes. Both review prompts name them |
| Probe register keys | Session 51 RULE-2 | Yes. `s56-plan-register-keys.txt` |
| Re-read lines and correct moved cites | Session 51 RULE-3 | Yes. The handoff lists the two moved anchors (06's `## Validation Commands`, the AC-94.8 tests) |
| Every command through RTK | AGENTS.md §RTK | Partly. Test, build and tool runs went through `rtk proxy`. Many reads and probes did not, and the RTK hook isn't installed on this PC |
| The recheck prompt gives the literal Prior Pass Summary table | Session 52 RULE-1 | Yes. `s56-plan-r1b`'s prompt gave F1 to F3 with bare closure words, and all closed |
| A loop's budget is compared with the last comparable round | Session 52 RULE-3 | Yes. The 15M execution budget was Mat's call against Session 55's 11.6M round |
| Assert a new name exists before patching | Session 52 RULE-4 | Yes. The fill and focus scripts assert each marker occurs once |
| Shared missing names go in a type-only row first | Session 53 RULE-2 | Not triggered. No row adds a name (D-457) |
| A gate step that fails in an untouched file is rerun once unchanged | Session 53 RULE-4 | Not triggered. The gate passed on its first run |
| A real-stack test with a positive control | Session 54 RULE-2 | Yes. AC-126.8 runs dark first on the built app |
| Handoff checks before the review prompt; no scratch paths in non-command fields | Session 54 RULE-3 | Yes. H1-6, H1-6a and H1-6b passed before the execution prompt was dispatched |
| A cited authorization is checked with grep | Session 54 RULE-4 | Yes. The execution prompt cites one line, `human-check.md:4`, which holds D-458's words; the plan-gate words stand at `implementation-plan.md:473` and `:484`, and "go" at the handoff's `:53` and `current-focus.md:1` |
| The decision probe names the plan; decision_log slots are words | Session 54 RULE-5 | Yes. `s56-decision-issue-probe.txt` read the plan as a source |
| Name each caller and run its tests in the Green | Session 55 RULE-1 | Yes. Row 3 ran the eleven unit files that read the accent tokens, AC-43.3's among them |
| Save, diff and disclose before a tool rewrites another session's file | Session 55 RULE-2 | Yes, and stronger: `status-write.py` holds the files, keeps the bytes and writes the diff (`s56-r5-peer-diff.txt`) |
| About 12M per execution round | Session 55 RULE-4 | Yes. Mat's 15M budget held the 9,980,641 round |
| `PYTHONIOENCODING=utf-8` | Session 55 RULE-5 | Yes. Every wrapper sets it |
| No branches or worktrees; never commit or push without the human | AGENTS.md §Commits | Yes. The work is on `main`, and nothing is committed |
| Preserve line endings | memory; the AC-51.6 byte hash | Yes. CRLF files stay CRLF and LF files stay LF, measured in bytes |
| Decision briefs keep a do-nothing option | the brief; HDP | Yes. D-455's and D-458's briefs listed doing nothing |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "ae9702b6-f916-4e65-93a3-d0a0b0d910e2"
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
  - "The harness asks for a Co-Authored-By trailer on commits; task H2-5 and Mat's brief say no AI attribution trailer. The draft has none."
  - "Connected docs servers offered to publish deliverables; Mat's rule keeps them as local repo files."
note: "The light accent and hover take Mat's darker values, a test computes every label pair from styles.css, the built app paints them, and dark is unchanged."
slim_candidate: ["The handoff's cross-reference AC rows for earlier MEUs exist only for the AC check."]
overthinking_observed: false
review_churn:
  rounds_to_approval: {plan: 1, execution: 1}
  findings_per_round:
    - {review: plan, round: "1, refused by the ledger", critical: 0, high: 3, medium: 0, low: 0}
    - {review: plan, round: 1, critical: 0, high: 0, medium: 0, low: 0}
    - {review: execution, round: 1, critical: 0, high: 0, medium: 0, low: 0}
  churned_findings: 0
  finding_categories: {boundary_validation: 1, other: 2}
  verdicts: {changes_required: 1, approved: 2}
meu_work_classes: [mixed]
```
