---
date: "2026-11-20"
project: "2026-11-20-e2e-devpc-clipboard"
meus: []
plan_source: "docs/execution/plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md"
template_version: "2.0"
---

# 2026-11-20 Meta-Reflection

> **Date**: 2026-11-20 to 2026-11-21. Planned and plan-reviewed on 2026-11-20; executed, reviewed and closed on 2026-11-21.
> **MEU(s) Completed**: none. Session 100 `e2e-devpc-clipboard` changes E2E test files, E2E tooling, the known list and the run book only, with no product change and no MEU (D-1302). It is the only session of the second 2026-11-20 grouping (`.agent/context/grouping/2026-11-20-e2e-devpc-clipboard-session-grouping.md` §3, row 100), run on `main` from `f1ba411`. Session 99 (`help-quick-start`) ran in the same tree; it is another session's work and is named here by path class only.
>
> - **The split** (`CLIPBOARD_SPLIT`; D-1305, D-1306, D-1309, D-1328). The clipboard steps of `C1-5` and `AC-71.15` (b) and (d) moved byte for byte into the new gated `ui/tests/e2e/copy-system-clipboard.test.ts`; `console-chrome.test.ts`, `mcp-setup-prompt.test.ts` and `settings.test.ts` keep the rest and run in every full run. `AC-71.15`'s token now comes from `launchApp(token)`'s seed (D-1307, D-1327); `W4-3` lost its two Pin MCP config clicks (D-1308).
> - **The dev PC never runs a clipboard test** (`CLIPBOARD_NEVER_DEVPC`; D-1305, D-1319). Both gated files skip unless `AVKIT_E2E_CLIPBOARD_GATED=1`, set only by the mini-air's gated stage; the plan-local `flake-run.py` excludes both and refuses while an old file still calls the clipboard.
> - **The guard** (`CLIPBOARD_GUARD`; D-1310, D-1311, D-1320 to D-1324, D-1331). `ui/tests/e2e/clipboard-guard.cjs` is preloaded into every non-gated launch, records every main, renderer and `webContents` clipboard call, copy, paste and chord instead of reaching the OS clipboard, and fails the launch at close with `CLIPBOARD_GUARD:`. A tracked Vitest scan fails a new clipboard call in `ui/tests/e2e` outside the gated files (D-1312, D-1326).
> - **The proof.** Dev-PC full run 238 of 238 in 30 files with the guard on (`edc-full-7.txt`). The mini-air run `r20261121T044121Z-3b7b4ac` on a no-ref snapshot (`SNAPSHOT_NO_REF`, D-1316): main 238 of 238 in 30 files, gated outcome `run`, reason `no-remote-session`, 5 of 5 expected; `primer=2/2 other=3/3` (`edc-gated-count-8.txt`). The final gate passed every step.
> - **The records.** `E2E-DEVPC-CLIPBOARD-SPECS` is `resolved`; `E2E-CLIPBOARD-PRIMER-EMPTY` stays `open` with the run's verification (D-1301 tally `3 of 5`); grouping row 100 is `executed (Session 100)`, so the grouping is done.
>
> **Plan Source**: `docs/execution/plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   - **Row 7, the dev-PC full run, ran three times** across about seven hours. The first attempt failed `AC-81.11` in `capture-inbox.test.ts` because another program on the dev PC held F2 (`F2: held, error=1409`, `edc-f2-probe-1.txt`; D-1341); Mat closed the program and the probes read `F2: free`. The second attempt never started a test: Playwright's global setup refused a `ui/out` built before Session 99's `ui/src` edits (D-1343). After Session 99 froze and one build (`edc-build-7.txt`), the third attempt passed 238 of 238.
   - **Session 99's class widened twice during execution** (D-1342, D-1343). Each widening changed plan-local scripts (`session-gate.ps1`, `baseline.ps1`, `identity.py`, `flake-run.py`, `guard-check.py`, `writer-scan.py`) on coordinator rulings, with their hashes and selftests recorded.
   - **Row 0's first attempt** waited 619 s for the dev PC's load and gave up at `89.6 %` (`edc-os-probe-0-attempt1.txt`); row 0 ran again in full.
   - **The executor's process exited after the H1-2 gate** and before the row was marked. The identity, `HEAD` and the own paths' times were checked against the gate, and the row was marked with no rerun (`edc-gate-recheck-h1-2.txt`).
   - **H1-6's first run refused** four plan "ACs" (`AC-33`, `AC-39`, `AC-61`, `AC-132`): the validator reads every `\bAC-(\d+)\b` in the plan, so the dotted spec ids in D-1343's ruling and the plan's foreign-id list counted (RULE-3).
   - The rows, from the receipts' modification times (local):

     | Step | Time |
     |---|---|
     | Plan review round 1, changes required | to 11-20 22:18 |
     | Plan review round 2, approved | to 11-20 22:47 |
     | Row 0 baseline, first attempt (load) | 11-20 23:02 |
     | Row 0 baseline | 11-20 23:15 |
     | Row 1 Red | 11-20 23:18 |
     | Rows 2 to 5 | 11-20 23:19 to 23:27 |
     | Row 7, first attempt (F2 held, D-1341) | 11-20 23:38 |
     | Row 8, the mini-air run | to 11-21 00:09 |
     | Row 7, second attempt (stale build, D-1343) | 11-21 06:35 |
     | Row 7, passed | 11-21 06:46 |
     | Row 9 records | 11-21 06:48 |
     | H1-2 gate, passed | 11-21 06:49 to 07:02 |
     | Execution review round 1, approved | 11-21 11:03 to 11:17 |

2. **What instructions were ambiguous?**
   - **What a shared tree's peer may do during a run.** The plan bound Session 99 by name and by its tracked digest, but said nothing about Session 99 building `ui/out` or editing `ui/src` while row 7 ran; D-1343 froze it (RULE-1).
   - **Which plan text the AC coverage check reads.** H1-6a counts table rows (`^| AC-n |`), but H1-6's validator counts every `AC-n` anywhere in the plan.

3. **What instructions were unnecessary?**
   - H2-1's `view_file` row, because H2-2's validator reads the same template and schema (as in Sessions 74 and 88 to 98).

4. **What was missing?**
   - **A host-input probe before the full run.** The suite registers F2; nothing checked that F2 was free before a seven-minute run (RULE-2).
   - **A build step in the row that runs the full E2E.** Row 7 relied on a `ui/out` that another session could leave stale.

5. **What did you do that wasn't in the prompt?**
   - **Kept every superseded receipt** with `-r1`, `-r2` or `attempt1`: row 0's first attempt, row 7's two failed attempts and H1-1's first run.
   - **Made every byte edit with a Python script** that keeps the file's line endings and checked the CR count afterwards.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **The plan review** (EDC-R1-1, EDC-R1-2), not a test: native paste bypassed both protection layers, and the gate read Session 99's handoff into `tested_state`. D-1331 and D-1330 fixed both before execution, and `S100 AC-8` and the scan's negatives pin the paste kinds.
   - **`AC-81.11`** caught a real host condition (F2 held by another program), not a code bug.
   - **Playwright's global setup** refused the stale build, which kept row 7 from testing the wrong renderer.

7. **Which tests were trivially obvious?**
   - `S100 AC-9`'s source-text checks of `electron-app.ts`; they pin the wiring rather than its behaviour, which `S100 AC-10` proves.

8. **Did pyright/ruff catch anything meaningful?**
   - Ruff found format and lint fixes in the plan-local Python this session wrote; no product finding. `py-types` was skipped with its H1-4 basis (no `packages/` change).

### Workflow Signal Log

9. **Was the FIC useful as written?**
   - Yes. The contract names (`CLIPBOARD_SPLIT`, `CLIPBOARD_NEVER_DEVPC`, `CLIPBOARD_GUARD`, `SNAPSHOT_NO_REF`) gave the tests, the handoff and both reviews one vocabulary; the execution review approved at round 1 with no findings.

10. **Was the handoff template right-sized?**
    - Mostly. The Departures and Execution notes carry the D-1342 and D-1343 hash chains at length; a single table of plan-local script hashes per ruling would be shorter (slim_candidate below).

11. **How many tool calls did this session take?**
    - Not counted exactly. The executor's transcript ran to a few hundred calls, rows 0 to H2-6, across context compactions and one process exit. Planning, the review dispatches and H1-7 to H1-7b ran in the coordinator's session.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    - The coordinator (Claude Code) delegated rows 0 to H1-6b and H2-1 to H2-6 to one executor subagent (Claude Code, Claude Opus 5.5). It ran the review dispatches and H1-7 to H1-7b itself.
    - No row went to `av-kit-builder`, `av-kit-verifier` or `av-kit-peer-reviewer`. No delegated result needed rework after review.

### Decisions Log

All are `autonomous`, decided on the HDP recommendation under Mat's hand-over (USER_EXPLICIT 2026-11-18 "make the decisions always the recommenations", continuing USER_EXPLICIT 2026-11-20 "continue with next prompt"). Planning decisions with an M hit (D-1310 M-3; D-1311, D-1312 and D-1322 M-8; D-1324 and D-1331 M-3 and M-8; D-1314, D-1316 and D-1330 M-6) were approved with the plan. The execution decisions D-1341 to D-1343 were ruled by the coordinator; D-1342 and D-1343 are M-6. D-1344 to D-1349 are unused.

- A second gated file, `copy-system-clipboard.test.ts`, for the three copy tests — [D-1305](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- `split-specs.py` builds the four files and checks them against the plan-time hashes — [D-1306](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- `AC-71.15`'s token from `launchApp(token)`'s seed instead of a clipboard read — [D-1307](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- `W4-3`'s two Pin MCP config clicks retired; the click stays a named residual — [D-1308](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- The moved tests keep their titles — [D-1309](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- A guard preloaded with `-r` into every non-gated launch, failing the launch at close (M-3) — [D-1310](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- The guard covers the clipboard readers too (M-8) — [D-1311](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- The static scan as a tracked Vitest test (M-8) — [D-1312](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- The AC-10 spec proves the guard on the dev PC — [D-1313](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- The gated outcome counted per file with `gated-count.py` (M-6) — [D-1314](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- Resolve `E2E-DEVPC-CLIPBOARD-SPECS`; `E2E-CLIPBOARD-PRIMER-EMPTY` gets verification only — [D-1315](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- The snapshot holds `HEAD` plus the eleven paths; the foreign class by name (M-6) — [D-1316](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- A guard hit in a run stops the session — [D-1317](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- The run book section and the commands line — [D-1318](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- `EXCLUDED` and `OLD_CLIPBOARD` in `flake-run.py` — [D-1319](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- A fixed list of twenty `NAMES`, tagged recorders, exit 70 on a failed install — [D-1320](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- A guard log per launch and `guard-logs.py` — [D-1321](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- `dom-ready` via `on`; the two clipboard permissions denied and recorded (M-8) — [D-1322](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- The AC-10 spec polls main's call list for 10 s — [D-1323](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- `wc.copy`, `cut` and the copy chords guarded (M-3, M-8) — [D-1324](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- The Edit menu's roles stay a named residual — [D-1325](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- The scan's patterns run over the whole file text — [D-1326](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- One added assertion that `mcp-token.txt` equals the seed plus a newline — [D-1327](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- `C1-5 log-to-file` keeps its route, with `try`/`finally` — [D-1328](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- The skip, only and todo literals check — [D-1329](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- `PEER_PREFIXES`; Session 99 by name only; a peer write after the gate reruns H1-2 (M-6) — [D-1330](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- The native paste kinds and `copyImageAt` guarded and scanned (M-3, M-8) — [D-1331](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- Treat the F2 failure as environmental; keep row 7's receipts as `-r1` and run row 7 once more after F2 was free — [D-1341](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- Widen Session 99's class by name, drop its untracked files before any read, exclude its new tests by name (M-6) — [D-1342](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)
- Freeze Session 99, build once, keep the `-r2` attempt off the rerun count, put three unit files in its class (M-6) — [D-1343](../plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md)

**Read from their own logs, not listed:**
- D-1262, D-1299 and D-1301 are on the issues.
- D-1200, D-1302, D-1303 and D-1304 are grouping §8.

**The `decision_sources` probe was re-run at H2-2** (`edc-decision-probe-h2.txt`), with the plan, the grouping and the register with both issues:
- it reads D-1200 and D-1302 to D-1304 (grouping), D-1262, D-1299 and D-1301 (triage), D-1305 to D-1331 (planning) and D-1341 to D-1343 (execution), 37 ids against 34 at the end of planning; the three new ids are this session's execution decisions;
- grouping §8 alone still reads the same 4 ids, and no other session added a row;
- the plan's YAML reads no pending entry, no slot and no open decision.

---

## Pattern Extraction

### Patterns to KEEP
1. **Guard the whole launch, not only the specs.** The preload records every clipboard path at the Electron and renderer level, so a future spec that copies fails by name on the dev PC instead of writing Mat's clipboard.
2. **No-ref snapshot commits for the host run.** The mini-air ran `HEAD` plus this session's eleven paths without Session 99's work and without a commit on `main`.
3. **Keep each superseded receipt with a suffix.** The reviewer read row 7's three attempts in order.

### Patterns to DROP
1. **Repeating the plan-local script hash chain in Departures and Execution notes.** One table per ruling would carry it.

### Patterns to ADD
1. **Freeze a peer session's build inputs and build in the run's own row** (RULE-1).
2. **Probe the host inputs the suite needs before a full run** (RULE-2).
3. **Name every `AC-n` the plan text holds in the handoff before H1-6** (RULE-3).

### Calibration Adjustment
- **Estimated:** no token budget. Round caps of 3 (plan) and 6 (execution).
- **Actual time:** about 1 hour of rows from row 0 to row 8, then about 6.5 hours waiting on F2 and Session 99 before row 7 passed; the gate took 13 minutes, and the mini-air main stage about 22 minutes (`duration_ms=1314303`).
- **Tokens:**

  | Item | Tokens |
  |---|---|
  | Plan review, round 1 | 15,265,446 |
  | Plan review, round 2 | 19,135,433 |
  | Execution review, round 1 | 12,427,048 |

- **Adjusted estimate** for an E2E tooling change proved on the second host: 15M to 19M tokens for a plan review round and about 12M for an execution round; about 2 hours of rows when the dev PC's inputs are free and no peer session shares the tree.

---

## Next Session Design Rules

```
RULE-1: When another session shares the tree, the row that runs the dev-PC full E2E builds the renderer itself just before the run, and the plan states which of the peer's paths are frozen (ui/src, the build config, package.json, tsconfig.json) for that row.
SOURCE: Session 100 D-1343: row 7's second attempt never started a test because Playwright's global setup refused a ui/out built before Session 99's ui/src edits.
EXAMPLE: before, row 7 runs flake-run.py on whatever ui/out exists; after, row 7 runs npm --prefix ui run build first and records the peer freeze in its receipt.
```

```
RULE-2: Each row that runs the full E2E on the dev PC first probes the global inputs the suite registers (F2 today) and stops before the run, naming the holder, when one is held.
SOURCE: Session 100 D-1341: AC-81.11 failed after a seven-minute run because another program on the dev PC held F2 (F2: held, error=1409).
EXAMPLE: before, the F2 probe ran only after the failure; after, row 7's script runs it first and exits nonzero on held.
```

```
RULE-3: Before H1-6, list every AC-n the plan text holds, dotted spec ids and rulings added in execution included, and name each one in the handoff's cross-ref row.
SOURCE: Session 100 H1-6: validate_closeout_artifacts.py reads \bAC-(\d+)\b, so AC-39.13, AC-33.18, AC-61.16 (D-1343) and AC-132.23 counted as plan ACs and the first run refused.
EXAMPLE: before, the handoff names the plan's AC-1 to AC-22 and the spec ids it moved; after, it also names each foreign id the plan quotes, marked not this session's.
```

---

## Next Day Outline

1. **Next:** the second 2026-11-20 grouping is done. The next step is issue triage (`.agent/skills/issue-triage/`) and a new session grouping for Mat. The prompt is at `C:/Temp/av-kit/next-session-prompt.md` (H2-6).
2. **Scaffold changes needed:** none.
3. **Patterns to bake in from today:** RULE-1 to RULE-3 here, plus the rules Sessions 74 and 82 to 98 carried, all in the start prompt.
4. **Codex validation scope:** the next session's own loops.
5. **Time estimate:** set by the triage and grouping pass.
6. **Still open for Mat:** D-1216's host items (Smart App Control, auto sign-in, a GitHub runner), which stay his and unchanged; D-1200 (the FFmpeg report); `E2E-CLIPBOARD-PRIMER-EMPTY` (repeated gated passes, `3 of 5`); `TOOLING-RUFF-TOOLS-UNCLEAN`; the guard's residuals (a native copy by Chromium, a renderer write before `dom-ready`, Pin MCP config not actuated); and the commit of Session 100 by the coordinator, with no push from the agent. H2-5 has the draft and the path list. Session 99 (`help-quick-start`) is another session's work, neither continued nor closed here.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | A few hundred in the executor's transcript, rows 0 to H2-6; not counted exactly |
| Time to first green test | Row 2's touched Vitest files at 23:19, 4 minutes after row 0; the Red at row 1 was 23:18 |
| Tests added | 5 Vitest tests in `ui/tests/unit/e2e-clipboard-guard.test.ts` (`S100 AC-5` to `AC-9`), 1 E2E spec in `ui/tests/e2e/clipboard-guard.test.ts` (`S100 AC-10`) and 4 `test_s100_` pytest functions in `tests/tooling/test_e2e_remote.py`; one changed existing test (`test_ac_11_known_tracked_list`). Three tests moved into `copy-system-clipboard.test.ts`. Final gate: Vitest 1,644 in 147 files, Python 3,335 passed, dev-PC E2E 238; the mini-air 238 main and 5 gated |
| Codex findings | Plan review: R1 changes required, 2 findings (EDC-R1-1 and EDC-R1-2, both High, fixed by D-1331 and D-1330); R2 approved, 0 findings. Execution review: R1 approved, 0 findings |
| Handoff Score (X/7) | 7/7. Every AC has evidence, the gate passed, and the execution review approved at round 1 |
| Rule Adherence (%) | 90 (9 of 10 sampled rules followed) |
| Prompt→commit time | Planned 2026-11-20, executed, approved and closed 2026-11-21; the coordinator commits without a push |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Codex reviewed the plan and the execution, and the executor never dispatched or wrote a verdict |
| The executor never commits, stages or pushes | The executor brief; AGENTS.md §Commits | Yes. The only git object is the no-ref snapshot `3b7b4ac`; H2-5 is a draft and a path list only |
| Red before Green, by assertion | AGENTS.md §Testing | Yes. Rows 1 and 3 failed by assertion before their Green (`edc-red-check-1.txt`, `edc-red-check-3.txt`) |
| Never run a clipboard test on the dev PC | The plan (`CLIPBOARD_NEVER_DEVPC`) | Yes. Every dev-PC full run went through `flake-run.py`, and `AVKIT_E2E_CLIPBOARD_GATED` was never set here |
| Never open Session 99's plan folder, handoffs or reflections | D-1316, D-1330 | Yes. Its paths were named only; no content hash or read |
| No host value in a tracked file | The plan (`LOCAL_HOST_DETAILS`) | Yes. The host-details scan reads `bad=0` |
| Keep line endings; measure in Python bytes | Session 70 RULE-5 | Yes. `current-focus.md`, `commands.md`, `metrics.md` and the three kept specs stay CRLF |
| An LF file is written as bytes and its CR count checked | Session 83 RULE-3 | Yes. The handoff, the commit draft, the reflection and the plan-local scripts read CR 0 |
| No model call or network use beyond the configured host | The brief | Yes. Only SSH and scp to the configured host through `tools/e2e_remote.py` |
| Run each Validation cell as written | The execution workflow | No. Row 0 and row 7 ran more than once, H1-1 and H1-6 ran twice, and six plan-local scripts changed on coordinator rulings (D-1342, D-1343); all disclosed |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "a3707a5b-24b9-4989-a528-bc4ea719a8a8"
  task_class: tdd
  outcome: success
sections:
  - id: priority_0_system_constraints_non_negotiable
    cited: true
    influence: 3
  - id: planning_contract
    cited: true
    influence: 2
  - id: testing_tdd_protocol
    cited: true
    influence: 3
  - id: execution_contract
    cited: true
    influence: 3
  - id: session_discipline
    cited: true
    influence: 2
  - id: dual_agent_workflow
    cited: true
    influence: 3
  - id: commits
    cited: true
    influence: 3
  - id: validation_pipeline
    cited: true
    influence: 3
  - id: rtk_token_optimized_commands
    cited: true
    influence: 1
  - id: instruction_coverage_reflection
    cited: true
    influence: 2
loaded:
  workflows: [execution_session]
  roles: [orchestrator, coder, tester]
  skills: []
  refs:
    - .agent/docs/human-decision-protocol.md
    - .agent/schemas/reflection.v1.yaml
    - docs/execution/reflections/TEMPLATE.md
    - .agent/context/handoffs/TEMPLATE.md
    - docs/execution/reflections/2026-11-20-e2e-clipboard-specs-reflection.md
    - .agent/context/handoffs/2026-11-20-e2e-clipboard-specs-handoff.md
    - .agent/docs/e2e-remote-host.md
decisive_rules: [P0:never-commit-or-push-without-human-approval, P0:never-run-clipboard-tests-on-the-dev-pc, P0:never-open-another-sessions-files, P0:keep-line-endings, P1:hdp-recommendation-under-hand-over]
conflicts:
  - "A peer session shared the tree; its class widened twice during execution, and six plan-local scripts changed on coordinator rulings (D-1342, D-1343)."
note: "Dev-PC clipboard steps moved to the gated stage and every other launch guarded; 238 main and 5 gated pass; plan review found two Highs."
slim_candidate: ["H2-1's view_file row repeats what H2-2's validator checks.", "Departures and Execution notes repeat the plan-local script hash chain."]
overthinking_observed: false
review_churn:
  rounds_to_approval:
    plan: 2
    execution: 1
  findings_per_round:
    - review: plan
      round: 1
      critical: 0
      high: 2
      medium: 0
      low: 0
    - review: plan
      round: 2
      critical: 0
      high: 0
      medium: 0
      low: 0
    - review: execution
      round: 1
      critical: 0
      high: 0
      medium: 0
      low: 0
  churned_findings: 0
  finding_categories: {boundary_validation: 1, contract_drift: 1}
  verdicts:
    changes_required: 1
    approved: 2
meu_work_classes: []
```

The review churn counts the ledger's recorded rounds in the session's two loops. The plan loop, `edc-plan-2026-11-20-e2e-devpc-clipboard`, used 2 of 3 rounds: round 1 found EDC-R1-1 (High, blocking, native paste bypassed both protection layers) and EDC-R1-2 (High, blocking, the gate read Session 99's handoff) with `intent_achieved=partial` (`usage` 15,265,446), and round 2 approved with both fixed and `intent_achieved=yes` (`usage` 19,135,433). The execution loop, `edc-execution-2026-11-20-e2e-devpc-clipboard`, used 1 of 6 rounds: round 1 approved with no findings and `intent_achieved=yes` (`usage` 12,427,048).
