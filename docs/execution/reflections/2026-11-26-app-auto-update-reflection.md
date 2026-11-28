---
date: "2026-11-26"
project: "2026-11-26-app-auto-update"
meus: ["MEU-173", "MEU-174"]
plan_source: "docs/execution/plans/2026-11-26-app-auto-update/implementation-plan.md"
template_version: "2.0"
---

# 2026-11-26 Meta-Reflection

> **Date**: 2026-11-26. Planned and plan-reviewed on 2026-11-26 and 2026-11-27; executed on 2026-11-27 and 2026-11-28; execution-reviewed and closed on 2026-11-28.
> **MEU(s) Completed**: MEU-173 Update feed and MEU-174 In-app update (phase 7; 07 §Update feed and §In-app update, 06 §Settings, Updates), from Mat's request of 2026-11-26 (`APP-NO-IN-APP-UPDATE`). Session 106 `app-auto-update` was the third of the four sessions of the 2026-11-26 grouping (D-1410). It ran on `main` from `5e4ec2f`, and `HEAD` did not move.
>
> - **A release build writes the feed files and checks them before upload** (MEU-173). `tools/check_update_feed.py` refuses a `latest.yml` whose version, file name, size or SHA-512 does not match the installer, and `docs/releases/publish-checklist-update-feed.md` is the standing step list from the first feed release on.
> - **The app checks for a newer release on a schedule and installs it from Settings** (MEU-174). The App group has an Updates section with the interval (weekly by default, monthly or never), the version, a status line, Check now and Restart and update. A found release downloads in the background and installs only on the user's click (D-1540 to D-1542, D-1547 to D-1550).
> - **The installer stops only av-kit's own processes and an update keeps Start at sign-in** (D-1553, D-1554). The installed round trip on mini-air (`0.0.901` to `0.0.902`) passed in run `r20261128T062757Z-ac98b72`.
> - **The proof of the whole.** Gate run r11 passed all 33 steps: Vitest 1,803, pytest 3,412, MCP 560 and the tool audit 104 of 104, with the identity unchanged from start to end.
> - **Still Mat's:** D-1543 (trust for an unsigned update) and D-1544 (the new request to GitHub), for release only. Nothing is published, and no feed is uploaded.
>
> **Plan Source**: `docs/execution/plans/2026-11-26-app-auto-update/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**
   - **Row 17, the installed round trip, ran four times on mini-air.** The first two runs failed on faults in the spec's own steps: a missing load-state wait (D-1578) and a click on a controlled checkbox (D-1579). The third run failed the same way: in installed `0.0.901` the Start at sign-in box stayed unchecked 30 s after the click. That was the coordinator's bound of three runs, so row 17 became `[B]` (B-17, D-1580).
   - **B-17 was a product bug, not test mechanics (D-1583).** Electron 42's `getLoginItemSettings` reads the `Run` value named after the AppUserModelId. av-kit set that id only inside `defaultToast`, so the box never read as checked after a sign-in change in a packaged app. `boot()` now calls `applyAppUserModelId(app)` on win32. The new test `app-user-model-id.test.ts` went Red, then Green, and run `r20261128T024018Z-d7983df` passed (D-1584).
   - **The gate ran 11 times.** Four stops were on this plan's own files, each fixed at its source: py-lint, task-contract, the OpenAPI delta (D-1582) and py-format (D-1586). Two stops were host faults on the shared PC: load timeouts (D-1587, D-1588) and the system commit limit exhausted by another repository's pytest run (D-1589). One stop was the tool audit's bare form (D-1590). After the round-1 corrections, r9 stopped on the CRLF review copy (D-1593) and r10 on a powered-off display (D-1594). No timeout was raised and no test was excused.
   - **Row 16's pair build** ran five times: PowerShell 5.1 quoting, a licence override (D-1577) and the pair config (D-1576).
   - The rows, from the receipts' modification times (local):

     | Step | Time |
     |---|---|
     | Plan review rounds 1 to 3, approved at round 3 | 2026-11-26 to 2026-11-27 00:13 |
     | Rows 0 to 3 (MEU-173 Red and Green) | 2026-11-27 17:15 to 17:40 |
     | Row 7 host canary, rows 8 to 15 | to 18:45 |
     | Row 16 pair build r1 to r5, row 17 runs 1 to 3 (B-17) | 18:43 to 21:39 |
     | Gate runs r1 to r8, with the 90-minute load wait | 20:57 to 2026-11-28 00:33 |
     | D-1583 fix, row 16 r6, row 17 run 4 | 01:08 to 02:02 |
     | Execution review round 1, corrections, gate r9 and r10 | to 02:27 |
     | Display back on, gate r11, execution review round 2, approved | 07:25 to 07:49 |

2. **What instructions were ambiguous?**
   - **The bound on host reruns** did not say whether a run that fails on a spec defect counts against it. D-1578 and D-1579 counted both, and the bound stopped the third run.
   - **"A failure in a touched file is not rerun"** read at first as any test in a touched file. The coordinator's ruling in D-1588 narrowed it to a failure the session's change could cause.

3. **What instructions were unnecessary?**
   - H2-1's `view_file` row: H2-2's validator reads the same template and schema.

4. **What was missing?**
   - **A real packaged-app sign-in check before the round trip.** The unit tests mocked `app.getLoginItemSettings`, so the AppUserModelId dependency had no test until B-17 (RULE-1).
   - **A privacy read of each new dependency's network behaviour at plan time.** electron-updater sends a persistent `x-user-staging-id` header and keeps a `.updaterId` file, and it logs raw error stacks to the console. The plan's privacy ACs covered av-kit's own log line only (RULE-2).
   - **A display check before a gate whose tool audit takes screen captures** (D-1594, RULE-3).
   - **The execution decisions were not yet in the plan's decision log at H2-2.** The header of `decisions.yaml` said they would go there at H1-3, and no row did it. H2-2 appended D-1555 to D-1594 before the probe could read them.

5. **What did you do that wasn't in the prompt?**
   - **Appended D-1555 to D-1594 to the plan's `decision_log`** and reworded seven tokens that the validator reads as template placeholders (angle-bracket names, braces) with the same meaning, so the probe reads 53 ids (`aau-decision-probe.txt`).
   - **Made every hand edit with a script** that writes bytes, asserts each anchor once and keeps the file's line endings.

### Quality Signal Log

6. **Which tests caught real bugs?**
   - **`update-roundtrip.test.ts` (AC-174.19)** caught B-17: the start-at-sign-in box never read as checked in a packaged app. No unit test could find it, because each one mocks Electron's login-item API.
   - **The execution review's real-library probe** caught F1 and F2. `app-updater.test.ts` now runs the real `electron-updater` against a local feed and asserts that no staging header, no `.updaterId` file and no library console line appear (D-1591, D-1592).
   - **`app-running-nsh.test.ts` (AC-174.21)** pins the bounded path match that the plan review's F4 asked for. A sibling decoy outside the install folder lives through the update.
   - **The OpenAPI delta test (AC-106.5)** caught the new `update_interval` field, which got a narrow exemption (D-1582).

7. **Which tests were trivially obvious?**
   - The guard tests that keep the other Settings sections and the IPC channel order unchanged passed at Red, as guards should.

8. **Did pyright/ruff catch anything meaningful?**
   - ruff stopped two gate runs on format and line length in `canon-edit.py`, which is format, not behaviour. pyright and tsc found nothing.

### Workflow Signal Log

9. **Was the FIC useful as written?**
   - Yes. The mechanism ids (`UPDATE_TICK`, `UPDATER_CONFIG`, `UPDATE_QUIET_FAILURE`, `ROUND_TRIP`, `APP_RUNNING_CHECK` and the others) gave both reviews one vocabulary. Each finding named its id and AC.

10. **Was the handoff template right-sized?**
    - Large for MEU-174 (21 ACs, 34 KB). The departures section carries most of the session's history, and a reader needs it to follow B-17.

11. **How many tool calls did this session take?**
    - Not counted exactly. Several hundred in the coordinator's and the executor's transcripts, across several context compactions.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**
    - No task row was delegated to a subagent. One Claude Code executor fork ran rows 0 to H2-6 under the coordinator. The coordinator dispatched the Codex reviews.

### Decisions Log

All are `autonomous`, decided on the HDP recommendation under Mat's hand-over (USER_EXPLICIT 2026-11-18, "make the decisions always the recommenations"), with `mandatory: none` unless named. The grouping decisions are read from the grouping file and the triage decision from `known-issues.yaml`, all through `--decision-source`.

- Open, Mat's: trust for an unsigned update, SHA-512 over HTTPS with no publisher signature (M-4); recommendation A, ship it and say so — D-1543
- Open, Mat's: the new request to GitHub and the works-offline and privacy statements (M-4, M-12); recommendation A, name the request, with Never as the switch — D-1544
- Offer only the release GitHub marks Latest, with no prerelease and no downgrade — [D-1540](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- Weekly by default, with monthly and a third value, never — [D-1541](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- Download at once in the background and install only on the Restart and update click — [D-1542](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- One session, MEU-173 first with its own handoff — [D-1545](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- MCP gets the setting only, as a leaf of avkit_settings — [D-1546](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- A new Updates section in the App group, after Startup — [D-1547](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- A Check now button that works with every interval — [D-1548](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- A fixed sentence beside the button says which running jobs stop — [D-1549](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- The schedule state lives in update-state.json; 7 and 30 days, first tick 60 s after the backend, a 24 h retry floor — [D-1550](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- A test seam read only under AVKIT_E2E=1 — [D-1551](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- The real update runs on mini-air as a third stage of e2e_remote.py — [D-1552](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- The uninstaller removes the updater cache, and an update keeps Start at sign-in — [D-1553](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- The installer stops only processes whose file is inside the install folder — [D-1554](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- The host payload tests go in tests/tooling/test_e2e_remote.py — [D-1555](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- Row 0 starts from Session 103's script copies — [D-1556](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- Only a definition counts as a use of a reserved decision id — [D-1557](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- Three scripts with no selftest leave row 0's selftest list; four get line-length fixes — [D-1558](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- What pins-scan counts as an enumerating file and which growth it allows — [D-1559](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- What baseline-pins.json holds — [D-1560](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- build-update.ps1 builds in a shared scratch clone at the snapshot commit — [D-1561](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- The process-selection macro wraps each call in an array for PowerShell 5.1 — [D-1562](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- build-update.ps1 creates the ffmpeg folder before the copy — [D-1563](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- A fifth install precondition folder, the packaged userData — [D-1564](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- The main and install stages share run-e2e.ps1's one ungated stage call — [D-1565](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- Row 5's cell uses an in-process script block, not a nested pwsh — [D-1566](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- Row 11's MCP run is repeated unchanged after one load timeout in an untouched file — [D-1567](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- Row 11's audit takes the authoritative form against the baseline — [D-1568](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- clipboard-image-main.test.ts is set by hand as a pins file — [D-1569](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- The three update channels go just before the last pinned channel — [D-1570](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- One shared shutdownForQuit for quit and install — [D-1571](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- test-ids.ts is set by hand as a pins file — [D-1572](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- SettingsPage.tsx exports GridSelect for UpdatesCard.tsx — [D-1573](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- run-check.py is fixed, and row 7's run is not repeated — [D-1574](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- The updater's log lines also go to the main process's stdout — [D-1575](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- Each pair pack uses a generated full copy of electron-builder.yml — [D-1576](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- A reviewed licence override for lazy-val — [D-1577](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- Row 17's spec waits for the load state — [D-1578](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- Row 17's spec waits for the controlled checkbox to answer — [D-1579](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- Row 17 is blocked after three runs (B-17) — [D-1580](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- The canon line is fixed in its generator — [D-1581](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- A narrow OpenAPI delta exemption for update_interval — [D-1582](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- B-17's root cause is fixed in this session: boot() sets the AppUserModelId — [D-1583](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- Row 17 is done after its fourth run passed — [D-1584](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- remote-run-2 accepts the reason ok with exit 0 — [D-1585](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- canon-edit.py is formatted, its edits unchanged — [D-1586](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- Gate r5's load failures stop the gate — [D-1587](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- Gate r5's failures are host load, so the gate reruns unchanged — [D-1588](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- Gate r6's failures are the system commit limit, a host fault — [D-1589](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- The gate's audit step takes row 11's authoritative form — [D-1590](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- F1: the updater sends no staging id header and keeps no id file — [D-1591](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- F2: the updater's library logger is off — [D-1592](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- The canonical review copy is LF — [D-1593](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- Gate r10 stops as blocked by the environment (display off) — [D-1594](../plans/2026-11-26-app-auto-update/implementation-plan.md)
- One commit for both MEUs, the plan's two messages kept as the alternative — [D-1595](../plans/2026-11-26-app-auto-update/implementation-plan.md)

---

## Pattern Extraction

### Patterns to KEEP
1. **Stop at the run bound and find the root cause.** B-17 stopped at three runs. The fourth run passed only after a product fix that a new unit test pins, not after another try.
2. **Prove a host fault before a rerun.** Each load or memory failure was run alone first, and the gate then ran again unchanged, with nothing excused.
3. **Probe the real library in the review.** The reviewer's `probe.cjs` against the real `electron-updater` found what the mocked tests could not, and the fix kept that probe as a test.
4. **Bind each host run to a snapshot commit** so a run's result belongs to one tree.

### Patterns to DROP
1. **Mocking the Electron API that a packaged-app proof depends on, with no packaged-app check.** It hid B-17 until the most expensive row.
2. **Decision text with angle-bracket or brace names** (`<v>`, `{state.enabled}`). The validator reads them as unfilled templates; Session 104 and Session 103 found this too.

### Patterns to ADD
1. **A packaged-app check of each OS integration the change reads back** (RULE-1).
2. **A network and logging read of each new runtime dependency at plan time** (RULE-2).
3. **A display check before a gate that takes screen captures** (RULE-3).
4. **Append the execution decisions to the plan's decision log in the H1 row that says so**, and probe them before H2.

### Calibration Adjustment
- **Estimated:** no token budget. Round caps of 3 (plan) and 6 (execution).
- **Actual time:** about 9 hours of rows and gate on 2026-11-27 and 2026-11-28, of which about 3 hours were host waits and gate reruns, plus a 5-hour stop with the display off.
- **Tokens:**

  | Item | Tokens |
  |---|---|
  | Plan review, round 1 | 17,549,036 |
  | Plan review, round 2 | 5,944,338 |
  | Plan review, round 3 | 7,671,091 |
  | Execution review, round 1 | 14,309,119 |
  | Execution review, round 2 | 4,932,857 |
  | Total | 50,406,441 |

- **Adjusted estimate** for a two-MEU change with an installed-app round trip on the host: about 30M tokens for a three-round plan review and 20M for a two-round execution review. Allow two host runs per round-trip row. Allow two hours more than the rows need when the PC is shared.

---

## Next Session Design Rules

```
RULE-1: A change that reads back an OS integration (sign-in, notifications, file types) proves the read-back in a packaged app before the row that depends on it, not only with the Electron API mocked.
SOURCE: Session 106 B-17 (D-1580, D-1583): three host runs failed with "Received: unchecked" because getLoginItemSettings reads the Run value named after the AppUserModelId, which only defaultToast set.
EXAMPLE: before, login-item tests mock app.getLoginItemSettings; after, the plan names a packaged-app check of the read-back and a unit test that boot() sets the id.
```

```
RULE-2: The plan reads each new runtime dependency for what it sends over the network, what it stores on disk and what it logs, and writes an AC for each one the privacy statements cover.
SOURCE: Session 106 execution review round 1: F1 (High), electron-updater sends x-user-staging-id and keeps .updaterId; F2 (Medium), its default logger prints raw error stacks.
EXAMPLE: before, the privacy AC covers av-kit's own log line; after, an AC pins no staging header, no id file and no library console line against the real library.
```

```
RULE-3: A gate whose tool audit takes screen captures first checks that the display is on and a capture is not black, and stops before the audit if it is.
SOURCE: Session 106 D-1594: gate r10, "mcp-audit authoritative: 93/104", "captured frame is black", with the monitor off.
EXAMPLE: before, the gate runs mcp-audit straight away; after, it runs a one-capture probe with an isolated inbox and records the result in its receipt.
```

---

## Next Day Outline

1. **Next:** Session 105 (`entry-emphasis-and-advanced`, MEU-171 and MEU-172), the last session of the 2026-11-26 grouping, with D-1500 = A applied at row 0. The prompt is at `C:/Temp/av-kit/2026-11-26-app-auto-update/aau-next-session-prompt.md` (H2-6).
2. **Scaffold changes needed:** none.
3. **Patterns to bake in from today:** RULE-1 to RULE-3 here, and Session 103's and Session 104's rules. A Settings section uses `GridSelect`, which SettingsPage.tsx now exports. The App group now has an Updates section after Startup.
4. **Codex validation scope:** the next session's own loops.
5. **Time estimate:** set by the next plan.
6. **Still open for Mat:** the commit of Session 106 (H2-5 has the draft; no push from the agent); D-1543 and D-1544 before the first release with feed files; that release's steps in `docs/releases/publish-checklist-update-feed.md`; the one-time manual install for rc.5 users.

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | Not counted exactly; several hundred across context compactions |
| Time to first green test | Row 2 at 17:27 on 2026-11-27, 4 minutes after row 1's Red at 17:23 |
| Tests added | 14 new test files: 9 Vitest files under `ui/tests/unit/`, 1 MCP Vitest file, 2 Electron files (`app-update.test.ts` in the main stage, `update-roundtrip.test.ts` in the install stage) and 3 pytest files. Final gate: Vitest 1,803 (Session 103's 1,716), pytest 3,412 (3,379), MCP 560, the tool audit 104 of 104 |
| Codex findings | Plan review: R1 changes_required, 6 (4 High, 2 Medium); R2 changes_required, 1 (F4 partial, High); R3 approved. Execution review: R1 changes_required, 2 (F1 High, F2 Medium); R2 approved, 0 |
| Handoff Score (X/7) | 5/7. Every AC has evidence and both reviews approved; row 17 needed a product fix after its run bound, and the gate needed 11 runs |
| Rule Adherence (%) | 100 (10 of 10 sampled rules followed) |
| Prompt→commit time | Requested 2026-11-26; planned and reviewed 2026-11-26 and 2026-11-27; executed 2026-11-27 and 2026-11-28; the commit waits for Mat |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Codex reviewed the plan and the execution; no verdict was written locally |
| Never commit, stage or push without Mat | AGENTS.md §Commits | Yes. H2-5 is a draft only |
| Red before Green, by assertion | AGENTS.md §Testing | Yes. Each Red row failed by assertion, and D-1583's test failed before its fix |
| Never raise a timeout or retry to green | AGENTS.md §Testing | Yes. The host faults were proved first and the gate reran unchanged (D-1588, D-1589) |
| Stop at the host run bound | The coordinator's bound; the plan (S10) | Yes. Row 17 became `[B]` at three runs (D-1580) |
| Keep line endings; measure in bytes | Session 70 RULE-5 | Yes. `eol-check` 0 problems over the scope paths |
| No home path in a tracked file | AGENTS.md | Yes. `check_home_path` ok |
| No Electron on the dev PC | Grouping D-1411 | Yes. Every Electron run was on mini-air through `e2e_remote.py` |
| Never publish a release or upload a feed | The plan; D-1543, D-1544 | Yes. Both stay Mat's; the feed was tested only from a local folder |
| Change no file outside the plan's paths | The plan §Files Modified | Yes. `scope-paths` 0 problems |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "b1d467ba-37b7-49d9-84d8-77aaa1f34169"
  task_class: tdd
  outcome: success
sections:
  - id: priority_0_system_constraints_non_negotiable
    cited: true
    influence: 3
  - id: planning_contract
    cited: true
    influence: 3
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
  skills: [mcp-tool-audit]
  refs:
    - .agent/docs/human-decision-protocol.md
    - .agent/docs/e2e-remote-host.md
    - .agent/schemas/reflection.v1.yaml
    - docs/execution/reflections/TEMPLATE.md
    - .agent/context/handoffs/TEMPLATE.md
    - docs/execution/reflections/2026-11-26-capture-key-inbox-scrollbars-reflection.md
decisive_rules: [P0:never-commit-or-push-without-human-approval, P0:keep-line-endings, P1:red-before-green-by-assertion, P1:never-raise-a-timeout-or-retry-to-green, P1:independent-review-no-self-approval]
conflicts:
  - "The coordinator's rule 'a failure in a touched file is not rerun' fought the D-1438 path for host load: gate r5's 105 load timeouts included one unchanged test in settings-rail.test.tsx, a touched file. The coordinator ruled in D-1588 that the rule means a failure the session's change could cause."
  - "The host run bound of three counted runs that failed on the spec's own defects (D-1578, D-1579), so B-17 stopped the row before the product bug was found; the coordinator found the root cause (D-1583)."
note: "A release build writes the update feed files and checks them; the app checks for a newer release on a schedule and installs it from Settings on the user's click."
slim_candidate: ["H2-1's view_file row repeats what H2-2's validator checks.", "The MEU-174 handoff's departures section, 34 KB in all, repeats the decision log at length."]
overthinking_observed: false
review_churn:
  rounds_to_approval:
    plan: 3
    execution: 2
  findings_per_round:
    - review: plan
      round: 1
      critical: 0
      high: 4
      medium: 2
      low: 0
    - review: plan
      round: 2
      critical: 0
      high: 1
      medium: 0
      low: 0
    - review: plan
      round: 3
      critical: 0
      high: 0
      medium: 0
      low: 0
    - review: execution
      round: 1
      critical: 0
      high: 1
      medium: 1
      low: 0
    - review: execution
      round: 2
      critical: 0
      high: 0
      medium: 0
      low: 0
  churned_findings: 1
  finding_categories: {boundary_validation: 3, contract_drift: 3, other: 2}
  verdicts:
    changes_required: 3
    approved: 2
meu_work_classes: [correctness, correctness]
```

The review churn counts the ledger's recorded rounds in the session's two loops. The plan loop, `aau-plan-2026-11-26-app-auto-update`, asked for changes at round 1 (4 blocking, `usage` 17,549,036) and at round 2 (1 blocking, F4 partial, `usage` 5,944,338), and approved at round 3 of 3 (`usage` 7,671,091). The execution loop, `aau-execution-2026-11-26-app-auto-update`, asked for changes at round 1 (1 blocking, F1; F2 non-blocking; `usage` 14,309,119) and approved at round 2 of 6 with F1 and F2 fixed and no new findings (`usage` 4,932,857). The two privacy findings are this session's main lesson: the mocked tests proved av-kit's own code, but only a probe of the real library showed what it sends and logs.
