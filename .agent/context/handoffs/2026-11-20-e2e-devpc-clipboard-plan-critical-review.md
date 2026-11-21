---
date: "2026-11-20"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-20-e2e-devpc-clipboard/implementation-plan.md"
verdict: "approved"
findings_count: 2
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "edc-plan-2026-11-20-e2e-devpc-clipboard"
round: 2
---

# Critical Review: 2026-11-20-e2e-devpc-clipboard

> **Review Mode:** plan
> **Verdict:** approved
> Round 2: both historical findings fixed; no new findings. The original Findings table is preserved unchanged; current statuses are in the recheck table.

## Scope

Session 100's complete current plan and task table, plan-local scripts, Session 100 grouping and issue decisions, affected specs and launch helpers, product clipboard entrypoints, unchanged remote gated-stage code and its pins, and named planning receipts. `PLAN` means `docs/execution/plans/2026-11-20-e2e-devpc-clipboard`. Applied PR-1 through PR-9, the Materiality Gate and the supplied intent-focused scope. Rechecked D-1330/D-1331 and their effects on previously accepted behavior.

Claude Code (Anthropic) authored the plan; Codex is the independent reviewer. Repository content stayed read-only. Reviewer scripts, synthetic fixtures, scratch Git repositories and outputs were confined to `C:/Temp/av-kit`. No product suite, npm command, Electron launch, clipboard operation, network request or mini-air command ran. Session 99's actual plan, handoffs and reflection were never opened, hashed or bound. Identity regression fixtures were synthetic.

## Intent Anchor

The plan must ensure that no dev-PC E2E run reads or writes Mat's system clipboard, preserve the three moved clipboard assertions in the mini-air's second gated file, retire W4-3's two copy clicks, and record and fail clipboard calls in non-gated launches by name. With the round-1 corrections, the plan delivers that intent within the supplied scope and disclosed runtime limits. This is approval of an unstarted plan, not a claim that execution acceptance has already passed.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| EDC-R1-1 | High | yes | behavior | **Native paste bypasses both protection layers.** High confidence. The proposed hooks wrap only `webContents.copy/cut` and copy/cut chords, while the scanner explicitly accepts `Control+V` and `Shift+Insert` and also misses `webContents.paste()` and `pasteAndMatchStyle()`. A non-gated spec can focus a text field and paste Mat's clipboard through Chromium without invoking either patched JS clipboard object, recording a call or failing its test. The reviewer reproduced zero scanner hits for all four forms; no real paste was executed. This defeats the no-read intent and AC-5's clipboard-call exclusion, rather than being one of the explicitly named mouse-menu or pre-dom-ready residuals. | `PLAN/implementation-plan.md:212`, `:213`, `:215`, `:385`; `PLAN/writer-scan.py:82`, `:199`, `:200`; local Electron API declarations `ui/node_modules/electron/electron.d.ts:18269`, `:18273` | Extend `CLIPBOARD_GUARD` to record and block native paste methods and paste chords, and teach both scans to reject them outside gated files. Name their tests and negative oracles in the ACs. Verify refusal with fakes/tag-checked recorders; never exercise a real read on the dev PC. Violates **AC-5**. | open |
| EDC-R1-2 | High | yes | behavior | **The gate reads and binds Session 99's excluded handoff.** High confidence. `identity.py` excludes other plan folders only; its untracked-file loop still reads `.agent/context/handoffs/2026-11-20-help-quick-start-*`. H1-2 invokes it before and after the full gate. On the supplied tree, the parallel session's untracked review handoff therefore enters `tested_state`, contrary to the explicit never-read/hash/bind boundary; subsequent peer edits also invalidate this session's gate. A scratch fixture reproduced both a changed identity when only that synthetic handoff changed and a read error when it was removed. | `PLAN/identity.py:62`, `:99`, `:171`, `:174`; `PLAN/session-gate.ps1:261`, `:300`; `PLAN/task.md:44`; `PLAN/implementation-plan.md:400` | Exclude the peer plan, handoff and reflection prefixes before any content read in identity generation, consistently with baseline and gate scope handling. Add a synthetic regression proving peer artifact contents are neither read nor included in `tested_state`, while own code/test inputs remain bound. Violates **AC-20**. | open |

## Recheck (round 2)

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| EDC-R1-1 | open | fixed |
| EDC-R1-2 | open | fixed |

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

No new delivery defect established. No open High or Critical finding remains.

### Corrections verified

- **EDC-R1-1 / D-1331:** `PLAN/implementation-plan.md:214` specifies tagged, non-forwarding `webContents.paste`, `pasteAndMatchStyle` and `copyImageAt` recorders; `:215` blocks paste chords; `:217` records `execCommand('paste')`. AC-5 and AC-8 at `:388` and `:391` explicitly name the positive and negative oracles, and task row 5 (`PLAN/task.md:60`) carries the added hooks into Green. `PLAN/writer-scan.py:88` and `:93`–`:106` implement the matching scan kinds. Fresh independent fixtures now reject all seven native-read/copy forms; plain V, Shift+V, Insert, replace and replaceMisspelling remain accepted. The full 56-case scanner selftest passes. The real guard's new paste routes are to be proven on fakes and tag-checked recorders, as the plan states; no real paste was tested on the dev PC.
- **Menu correction:** D-1325 (`PLAN/implementation-plan.md:881`) now cites D-1331's narrower, supported claim. `edc-plan-electron-roles.txt:3`, `:5` and `:30` show Windows copy/cut/paste roles dispatching through the focused webContents object. That supports the proposed interception; it is not evidence of a live mouse-menu test or of macOS interception.
- **EDC-R1-2 / D-1330:** `PLAN/identity.py:84` defines the three peer prefixes; `:140` excludes them from Git diff/enumeration, and `:196` excludes their names before `:200` reads untracked bytes. Its fresh selftest proves both tracked and untracked peer exclusion, with own inputs still bound. An additional probe listed three nonexistent synthetic peer artifacts beside an own source file: no peer read occurred, and changing the own file changed the identity. `PLAN/baseline.ps1:177`, `:325` and `:347` keep peer artifacts outside content hashing and mark dirty shared/product paths by name; `PLAN/session-gate.ps1:101`, `:112`, `:139` and `:151` retain that scope handling. D-1316 (`PLAN/implementation-plan.md:759`) is amended, and D-1330 (`:949`) explicitly distinguishes unread peer artifacts from tracked suite inputs included only in the aggregate diff digest. No real Session 99 artifact was used to verify this.

## Q1. Goal and acceptance coverage

Accepted: AC-1–4 and row 2 preserve the three clipboard moves, retire W4-3's clicks and seed (e); AC-5–10/21 cover scan, guard and named failures; rows 7–9 supply dev-PC evidence, final snapshot acceptance and issue updates. D-1331 closes the concrete no-read hole found in round 1. D-1330 restores the excluded-peer boundary.

The counts still reconcile: baseline 239 plus three moved tests and one guard test gives 243 in 32 files; five gated tests in two files leave 238 in 30 files. No remaining goal clause lacks an AC and proving row. No new rejection under Q1.

## Q2. Moves, assertions and token seed

Accepted: `split-specs.py:248` constructs the copy file from the pinned base blocks and helpers; `:265` retains C1-5's route/setup; `:375` checks invariants; `:430` compares actual output bytes. Fresh reconstruction matches all four plan-time SHA-256 values, including `0b75576e...` for the new file, and the 13-case selftest passes. Existing moved assertion lines and (e)'s assertion loop remain unchanged. `ui/src/main/index.ts:162` reads the scratch token file before creating a token; the specifically named added token-file assertion checks the seed remains in use.

W4-3's two clicks carry no independent value assertion. Gated (d) still proves the shared Copy MCP config write. Pin's no-page-error actuation is deliberately retired and disclosed by D-1308. No additional setup loss or assertion weakening established.

## Q3. Guard installation, routes and logs

Accepted: the test-only `-r` preload precedes app main, installs the fixed twenty-name main guard or exits 70, hooks later windows, patches the renderer on every load, denies clipboard permissions, and now intercepts the named native paste/copy routes. Each AC-10 call requires the exact function's tag before invocation and waits for all three records before close. D-1331 does not weaken that safety check or change AC-10's three-call log contract.

`guard-logs.py:76` ties call-time logs to launch phases independently of swallowed/raced close. Its fresh 19-case selftest passes, including missing/invalid observations and unexpected calls. The plan-local audit is wired into rows 5/7/8 and the final gate; it is not an automatically invoked audit of every future plain npm run.

Limits remain accurately separated from proof: the supplied Electron probe patches the ten writers and renderer write/execCommand methods and verifies shared main-process identity; it does not prove all twenty replacements or the preload-registered window hook. Row 5 must prove those. Pre-dom-ready legacy execCommand, later replacement of permission handlers, mouse-menu behavior and macOS native roles remain disclosed limits; no current non-gated spec exercising an uncovered route was established. No new Q3 blocker.

## Q4. Static scan

Accepted: the scanner covers whole-file matches, multiline chains, locator variables, CSS/role/text copy locators, native paste/copy methods and the specified chords. Launch helpers are exempt only from direct-launch matching. The two gated files and the guard's own files remain the only file exclusions. The tracked Vitest twin is explicitly required to carry the same patterns and positive/negative fixtures.

Fresh independent counts remain **10 before the moves, 8 after the split, 0 with both gated files excluded**. The widened 56-case selftest passes, and all four original round-1 bypass fixtures now produce hits. Dynamically assembled selectors remain the runtime guard's responsibility, as disclosed. No new Q4 rejection.

## Q5. Dev PC and gated stage

Accepted: both gated files skip at file level unless the gate variable is `1`; `flake-run.py:163` excludes both by name, and `:544` removes the variable from every child. The current source-writer precheck refuses before execution. The file guards also protect default npm/Playwright and Session 98's older runner when the variable is unset. No planned dev-PC command sets it.

`tools/e2e_host/run-e2e.ps1:255` removes the variable before main; only `AvStage -Gated` sets it for its child (`:59`), and it is cleared immediately afterward. Existing list handling supports both files without tool/host-script edits. The 238/30 main and 5/2 gated partition holds. Empty `known` still leaves unexpected main failures on `_summary_refusal`'s exit-40 path (`tools/e2e_remote.py:1070`). Source and supplied receipts support this; no fresh host execution is claimed.

## Q6. Acceptance run, snapshot and registers

Accepted: row 8 names exactly eleven code/test paths. `snapshot-commit.py:118` starts a temporary index from HEAD; `:167` verifies the complete changed-path set and working blobs. None names Session 99's artifacts. The no-ref snapshot preserves the working index/refs and is followed by one mini-air acceptance run at those final files, with S13 invalidating an affected result. Green sweeps precede the snapshot, and the run precedes resolution.

D-1330's identity exclusion is now effective without excluding this session's inputs. Session 99's tracked suite-input changes still invalidate aggregate gate identity, as explicitly decided; peer artifacts remain unread. `gated-count.py:83` counts only the capture file's 2/2 under `run`; copy failures remain failures, while skipped/voided stages do not count. The fresh 17-case selftest passes. With prior=2, PRIMER stays open. DEVPC resolves through the named resolver only after dev-PC and mini-air main-stage evidence; register tools preserve other entries. No remaining Q6 rejection.

## Q7. Pins and full gate

Accepted: fresh searches of `tests/` and `ui/tests/` again identifies `test_ac_11_known_tracked_list` as the changed tracked-list pin. Other one-file expectations belong to isolated fixtures. The plan names the exact new value, added tests, retitles, seed and added assertion; `pins-check.py`'s 14-case selftest passes.

The gate includes typecheck, ESLint, full Vitest/pytest, D-1287-scoped ruff, build and Electron through pwsh with `ELECTRON_RUN_AS_NODE` cleared, EOL/home/host checks, scan and guard-log audits, final snapshot binding and generated-register checks. Issue mutations use `issue-resolve.py` and `issue_triage.py`; grouping edits are restricted to Session 100's row. D-1330 does not remove any own code/test/config input from gate binding. No new substantive Q7 rejection.

## Non-blocking correction notes

`PLAN/task.md:75` still pins the AC-table count to 20; the actual declared set is AC-1–22. Change that literal to 22 when executing the closeout check. At `PLAN/task.md:74`, stale hash wording must follow the explicit D-1330/name-only rule at `:44`; several closeout decision-range references also still stop at D-1329. These are inferable clerical carryovers, not missing product behavior or reasons for another review round. No formatting/template finding is raised.

## Checklist Results

Manual procedure: read the complete current plan/task; inspect the corrected scripts, Decision Log, source call chains, grouping/issue rulings and supplied receipts; cross-check each Q against its AC/task row and re-evaluate the original findings. Observer: codex-independent-reviewer; exit_code: null.

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Moves, guard, runs, snapshot scope and register ordering agree; stale closeout literals are clerical notes above. |
| PR-2 Not started | pass | Draft rows remain unchecked and all four planned new implementation/test paths are absent. |
| PR-3 Task contracts | pass | Owners, outputs, dependencies and commands remain specified. |
| PR-4 Validation realism | pass | Corrected native routes have rejecting oracles; peer artifacts are excluded before reads; own inputs remain bound. |
| PR-5 Source-backed planning | pass | Grouping, issue decisions, supplied hand-over and current local code support the choices, including D-1330/D-1331. |
| PR-6 Correction readiness | pass | Both original findings rechecked against current scripts, decision records, negative receipts and fresh probes; no unresolved substantive correction. |
| PR-7 Scope discipline | pass | Test/run-book scope remains; product/tool/host-script changes and excluded peer work remain outside this session. |
| PR-8 Reachability and negative oracle | pass | Launch/helper/log chain, fake native-route oracles, scanner refusals and real-Git synthetic identity regression checks remain connected. |
| PR-9 Single-statement contracts | pass | No materially ambiguous competing behavior established; known stale literals have an evident canonical value. |
| AV-1 to AV-6, plan applicability | pass | Named Red/Green paths, immutable assertions, expected file guards, source-backed scope and fresh negative checker probes; no implementation pass asserted. |
| Live dev-PC/mini-air acceptance | n/a | Execution is unstarted. Reviewer ran neither. |

### Fresh reviewer evidence

Commands ran with `PYTHONDONTWRITEBYTECODE=1`; Python scratch temp directories were under the review folder. The identity selftest's Git fixture was confined there and used the required noreply author/committer environment. No production repository mutation was performed.

| Command | Exit | Decisive result |
|---|---|---|
| `rtk proxy python C:/Temp/av-kit/edc_r2_probes.py` | 0 | writer-scan 56/56; guard-logs 19/19; guard-check 13/0 wrong; gated-count 17/0 wrong; pins-check 14/0 wrong; split-specs 13/ok; eol-check 24/0 wrong; red-check 39/0 wrong; identity 0 failures. Seven native-route fixtures rejected, five negatives accepted; nonexistent listed peer artifacts unread, own change detected. |
| `rtk proxy python C:/Temp/av-kit/edc_r2_counts.py` | 0 | Scan counts 10,8,0; split invariants pass; four output SHA-256 values match the plan; all four new implementation/test paths absent. |
| `rtk proxy python C:/Temp/av-kit/edc_r2_receipts.py` | 0 | 45 explicitly named planning receipts read, none missing; no broad receipt-folder search. |
| `rtk proxy rg -n 'known-failures\.json|capture-system-clipboard\.test\.ts|gated.*==|239|237|e2e-remote-host.md' tests ui/tests/unit` | 0 | Changed tracked-list pin remains test_ac_11_known_tracked_list; other one-file assertions are fixture-specific. |

```json
{"schema_version":"evidence.v1","check_id":"edc-r2-corrections","command":"rtk proxy python C:/Temp/av-kit/edc_r2_probes.py","cwd":"P:/av-kit","scope":"nine plan-local checker selftests and synthetic native-route/peer-identity fixtures","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"unstarted Session 100 round-2 plan; targeted corrections review, not a product D6 identity","output":"writer-scan 56/56; guard-logs 19/19; guard-check 13 zero wrong; gated-count 17 zero wrong; pins-check 14 zero wrong; split-specs 13 ok; eol-check 24 zero wrong; red-check 39 zero wrong; identity zero failures; seven native-route scan fixtures rejected and five negatives accepted; missing synthetic peer artifacts not read; own mutation detected","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"edc-r2-split-and-scan","command":"rtk proxy python C:/Temp/av-kit/edc_r2_counts.py","cwd":"P:/av-kit","scope":"read-only E2E sources and in-memory reconstruction from f1ba411","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"unstarted Session 100 round-2 plan; no E2E execution","output":"scan counts 10,8,0; split invariants pass; SHA-256 console ca33af993d389512adfcd8fa362a901e97b762c853fae5b80133feb796048e90, mcp 525c4705ea3bce9add794697dccc968cbe5845f56ca6333e2643ced994df4485, settings a71bf7ca57160b3a84beecac4d53f8df751df40786e505d9a336a876194409ce, new copy 0b75576ecc0a79be0b6d37b8b26706110d944f3f975f5c33b3c5a52cb785e7f9; four implementation/test paths absent","fresh":true}
```

The initial product-caller search included the nonexistent `ui/src/preload/` directory and exited 2. It was corrected to the actual `ui/src/main/preload.ts` layout and rerun over `ui/src/main` and `ui/src/renderer`, exit 0; the incomplete first search is not used as absence evidence. An initial tooling filename-glob search also exited 2 and was rerun with rg's `-g` filters, exit 0. No product-suite pass is inferred from either source search.

The final report was also parsed with the repository's `check_review_state` through `rtk proxy python C:/Temp/av-kit/edc_r2_validate.py`, exit 0: `review_mode=plan`, `round 2 of 3`, `verdict=approved`, `open findings=0`. The original Findings table is byte-identical, and all seven Q sections and round-2 tables are present. The first reviewer wrapper incorrectly treated informational return lines as errors; after checking the parser API, that wrapper assertion was corrected and the final validation passed.

Completion-preflight was consulted for the review artifact's required fields and rolling status. Unchecked execution rows are expected for an unstarted plan and were not executed by this reviewer.

## Verdict

**approved** — EDC-R1-1 and EDC-R1-2 are fixed; no new evidence-backed High or Critical delivery finding remains. Proceed with the authorized execution and its planned verification. Runtime acceptance, including the single final-tree mini-air run, remains to be demonstrated during execution. The complete rolling report is `C:/Temp/av-kit/edc-plan-review-round-2.md`; the coordinator owns copying it to the canonical review path.
