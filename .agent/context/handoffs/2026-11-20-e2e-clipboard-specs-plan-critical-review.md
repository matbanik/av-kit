---
date: "2026-11-20"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-20-e2e-clipboard-specs/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "ecs-plan-2026-11-20-e2e-clipboard-specs"
round: 1
---

# Critical Review: 2026-11-20-e2e-clipboard-specs

> **Review Mode:** plan
> **Verdict:** approved

## Scope

Session 98, the complete working plan and task table, plan-local scripts, the two source specs, Playwright entrypoints, Session 96's remote tool/host scripts/tests/run book, grouping, issue records, and the named planning receipts and RustDesk source copies. Applied the Materiality Gate and PR-1 through PR-9. `PLAN` below denotes `docs/execution/plans/2026-11-20-e2e-clipboard-specs`.

Claude Code (Anthropic) authored this plan. Codex is the independent reviewer. The repository was read only; all writes were under `C:/Temp/av-kit`. No pytest, Vitest, npm, uv, Electron, network request or remote command ran. The disclosed sandbox-only untracked settings file was not opened. Completion-preflight was consulted for review-artifact checks; implementation remains unstarted and its unchecked rows are expected in this review mode.

## Intent Anchor

the five capture E2E tests that only share a file with a clipboard test run again in every full run on both hosts, and the two tests that use the system clipboard run on the second Windows host (the mini-air) only when a probe before and after them reads no remote-desktop session; otherwise the run reports them skipped or voided with a named reason. The tests never run on the dev PC. Six parts: 1. **The split** (D-1268, `CLIPBOARD_SPLIT`). `AC-88.12 (a)(b)(f)` (Copy full path and Copy image) leaves `ui/tests/e2e/capture-filmstrip-actions.test.ts` and `AC-132.23` (Ctrl+V paste) leaves `ui/tests/e2e/capture-import.test.ts`; both move, with the helpers only they use, into the new `ui/tests/e2e/capture-system-clipboard.test.ts`. Their bodies keep every byte (only the line ending of the filmstrip lines moves from CRLF to LF). The five others, `AC-88.12 (c)`, `AC-88.12 (d)(e)`, `AC-89.9`, `AC-89.15` and `AC-132.22`, stay where they are, byte for byte. `split-specs.py` builds all three files from the `b59207b` bytes, with a file-level guard after the new file's imports that skips it unless `AVKIT_E2E_CLIPBOARD_GATED=1` (D-1282), and `--check` proves the result. 2. **The dev PC** (D-1276, `CLIPBOARD_NEVER_DEVPC`). The plan-local `flake-run.py` excludes only the new file, and refuses before any run while either old file still calls the clipboard. Its full run has 237 tests in 29 files, the five rejoined ones among them. The new file also guards itself in tracked code: it skips unless `AVKIT_E2E_CLIPBOARD_GATED=1`, which only the mini-air's gated stage sets, so a plain `npm run test:e2e` lists its two tests as skipped and never runs them (D-1282, `guard-check.py`). 3. **The probe** (D-1269 to D-1271, D-1273, `SESSION_PROBE`). One PowerShell block, the same bytes in `host-facts.ps1`, `host-status.ps1` and `run-e2e.ps1`, reads the RustDesk processes' command-line switches, `rdpclip.exe` and `qwinsta`, and returns `none`, `connected` or `undecided` with a named reason. `tools/e2e_remote.py check` prints it as a `session-probe:` line, and each run poll records it. 4. **The gated stage** (D-1271, D-1272, `GATED_STAGE`). `run-e2e.ps1` runs the main specs first, then probes. Only when the probe reads `none` does it run the gated file in `results\<run-id>\gated\`, and it probes again after. The tool reports a `gated` object with one of five outcomes. A gated failure exits 40, apart from the main stage's `new` list. A session that connects during the stage (seen by the after-probe or a poll) voids the result. 5. **The known list and its pin** (D-1272, D-1275). `tools/e2e_host/known-failures.json` drops its two `skip` entries and gains one `gated` entry for the new file. `tests/tooling/test_e2e_remote.py::test_ac_11_known_tracked_list` changes in row 3, which names it. `pins-check.py` proves that no other existing statement of that file changes. 6. **The acceptance run and the registers** (D-1277 to D-1280). One mini-air run (and a second, row 8b, only when the gating probe cannot read the host; D-1280) through `tools/e2e_remote.py run` at the final tree, as a snapshot commit on no ref (`SNAPSHOT_NO_REF`). The main stage has 237 tests, all expected. The gated outcome is a receipt, not a pass condition. Then `E2E-CLIPBOARD-SPECS-UNGATED` is resolved when row 8's `probe-check.py --judge-gate` says resolve (D-1280), `E2E-CLIPBOARD-PRIMER-EMPTY` gets that run's verification and stays open, a new low issue records the two dev-PC specs that also write the clipboard, and grouping row 98 is set.

Executing the plan would deliver the stated intent, including the explicitly authorized split-only fallback. This approves planning readiness; it does not certify an executed dev-PC gate or a live mini-air probe.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

## Q1. Goal and acceptance coverage

Accepted: AC-1–4 and AC-20 cover the split, the five restored tests, 237 dev-PC tests and the tracked skip guard; AC-5–12 cover probe/stage behavior; AC-13–14 bind the mini-air run to the snapshot and require 237 expected main tests in 29 files; AC-15/18 control issue disposition and fallback; AC-19 records the other writers. Rows 2, 7b, 8/8b and 9 put those proofs in dependency order (`PLAN/implementation-plan.md:468`; `PLAN/task.md:53`, `:62`, `:64`, `:67`).

No missing goal clause established. A fallback deliberately leaves UNGATED open; it cannot be reported as a demonstrated working clipboard stage. PRIMER-EMPTY remains open in either form.

## Q2. Split bytes, helpers and isolation

Accepted: the only clipboard users in the two source files are AC-88.12 (a)(b)(f), AC-132.23 and their private helpers. Each test creates its own app/profile/backend; there is no shared beforeAll or fixture state that the split loses (`capture-filmstrip-actions.test.ts:53`, `:222`, `:242`; `capture-import.test.ts:160`, `:337`, under `ui/tests/e2e/`). The copied shared helpers preserve the two tests' setup; deleteLedger and mainPng/importBodies remain with their users.

`split-specs.py:314` builds from b59207b, and `:414` compares the actual files with those built bytes. The independent scratch probe compared all five retained test blocks, reproduced all three hashes, and demonstrated refusal of both a changed retained assertion and an inverted guard. No assertion/wait/timeout change is authorized. The filmstrip file keeps CRLF; the moved lines normalize to LF as specified.

## Q3. Dev-PC exclusion and tracked guard

Accepted: `flake-run.py:161` excludes only the new file; `:486` inspects the old files, and `:1841` refuses before run(). A fresh invocation on the current tree exited 2 with “refused before any run”. `child_env` removes the gate variable as well as ELECTRON_RUN_AS_NODE (`:530`).

The new file's top-level guard covers npm, default Playwright and older runner copies that do not know its name (`split-specs.py:147`). `guard-check.py:107` removes the variable and uses --list, so it exercises discovery without launching tests. The named unset/set receipts show respectively two skipped tests and four guard problems; its eight-case selftest passed. The planned launcher tests check that only AvStage -Gated sets the variable (`implementation-plan.md:268`, `:377`, `:388`). This is the stated opt-in boundary, not protection against someone deliberately setting the variable on the dev PC. The two other clipboard writers remain issue-only under the supplied scope decision.

## Q4. Probe signals and fail-closed behavior

Accepted within the documented RustDesk/RDP and English-host scope: RustDesk start_ipc connects to or starts the --cm endpoint (`rustdesk-src/src_server_connection.rs:4724`, `:4729`, `:4763` in the named receipt folder); a positive cm/RDP signal withholds the tests. The rule order makes read failures undecided and exempts only the identified service and direct child from unreadable-command-line refusal (`implementation-plan.md:232`, `:240`). AC-6 requires PS 5.1 fixture coverage of every reason and those exemptions.

The host receipt proves only the elevated idle view. It does not establish the Limited-token connected case; the plan now says so and judges the actual launcher's probes in row 8. Stale cm and rdpclip processes can conservatively starve the stage, and other remote-control programs are outside this detector. Start times/detail and the run-book risks expose those limits. None is presented as a proven live connection lifecycle or a guarantee that voiding restores a clipboard (`implementation-plan.md:255`). No new false-none path was established from the available source and plan.

## Q5. Gated stage and Session 96 contracts

Accepted: one scheduled task and lock remain; AvStage retains the single Start-Process site, records its stage-specific pid before waiting, and main results remain separate. The tool excludes gated specs from the main expected set and reports five gated outcomes; connected dominates undecided, and any non-none gated poll/after reading voids the result (`implementation-plan.md:261`, `:297`). Missing expected probe/report artifacts remain report refusals. Gated failures under run exit 40 through gated.new; voided failures remain visible separately.

The existing main-summary implementation treats every non-expected test as new when known is empty (`tools/e2e_remote.py:731`, `:812`). Its report consistency/spec-membership, pinned SSH, refusal, locking and no-stop tests remain unchanged. The proposed fake-host and real-PS launcher cases exercise the new call chain, including exact main exit, connected skip, undecided skip and after/poll voids (`implementation-plan.md:370`). No weakening of PINNED_SSH, NAMED_REFUSAL, NEVER_STOP, ONE_LOCK, COMMIT_BOUND, REPORT_ONLY, KNOWN_NAMED or NO_PARTIAL was identified. This assesses the planned implementation and tests, not code that has already been written.

## Q6. Split flag and evidence-led issue outcome

Accepted: row 7a is provisional; row 8's --judge-gate reads gated.probe_before/after from the task context. Unreadable/failed gating reads trigger exit 3, row 8b records limited-unreadable, restores the baseline tool/host scripts and reruns once in fallback form. The independent 28-case probe-check selftest passed, including limited-before, failed-before and limited-after (`probe-check.py:148`, `:258`).

Only run, skipped-connected and voided-connected-during permit “ungated: resolve”; undecided outcomes preserve the issue as open. Row 9 checks that decision before resolving through the register helper. S13 separately permits one final-state rerun after a runtime-scope change; neither path authorizes retrying until the clipboard tests pass (`task.md:64`, `:65`, `:67`; `implementation-plan.md:660`). The host run precedes resolution, preserving Session 97 RULE-3. A stale cm can still cause a conservative skip; its detail is recorded rather than asserted to prove an active human connection.

## Q7. Pins, snapshot, gates and register tools

Accepted: an independent search of tests/ and ui/tests/ found the existing tracked-list pin only in test_ac_11_known_tracked_list; host-script/run-book pins remain compatible. The plan names the new assertion and docstring, keeps known == [] and KNOWN_FILE, and freezes all other existing statements (`implementation-plan.md:399`; `pins-check.py:63`). Its 13-case selftest passed.

SNAPSHOT_NO_REF uses a temporary index, commit-tree and GIT_OPTIONAL_LOCKS=0, then compares index/status/refs/HEAD. The scratch selftest passed preservation, scoped additions/deletion, no-ref, post-build drift, existing-output and identity-refusal cases (`snapshot-commit.py:116`, `:165`). No object was created in the real repository by this review.

`session-gate.ps1:239` schedules typecheck, ESLint, full Vitest/pytest, ruff, real built Electron E2E through the guarded runner, EOL/home/host scans, snapshot/test hashes and register renders, with fail-fast exit propagation and before/after identity. Row 7b brings full Vitest and ruff before the host snapshot. Issue updates use issue-resolve.py and issue_triage.model; rendering uses the register CLI. No product code or MEU changes are planned. These are validated gate definitions, not live product-suite results.

## Checklist Results

Manual procedure: read the complete plan/task; inspect split/probe/guard/pin/snapshot and gate implementations; trace the remote producer/summary paths and existing tests; compare grouping, issue rules and the named receipts; map each AC to its task row. Observer: codex-independent-reviewer. Exit: null.

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Split, gated implementation, provisional flag, bounded fallback run and issue changes agree. |
| PR-2 Not started | pass | HEAD b59207b on main; one worktree; tracked diff empty; no implementation handoff; task rows unchecked. |
| PR-3 Task contracts | pass | Named owner, deliverable, dependencies and validations for implementation rows. |
| PR-4 Validation realism | pass | Byte reconstruction, negative split mutations, pre-run refusal, fixture Reds, frozen tests and final-tree host acceptance. |
| PR-5 Source-backed planning | pass | Grouping/issue rulings, supplied hand-over, local scripts and RustDesk source support the behavior. No uncovered reserved human act found. |
| PR-6 Review/corrections readiness | pass | Independent execution review follows the evidence handoff; round-1 review needs no prior-finding census. |
| PR-7 Scope discipline | pass | Product changes, host settings, other writers and PRIMER closure follow the explicit boundaries. |
| PR-8 Reachability/negative oracle | pass | Tracked guard, launcher probes, polls/summary and final-host acceptance have named producers and negative tests. |
| PR-9 Single-statement contracts | pass | Named contracts govern the ACs and task rows; no unresolved materially different live predicate found. |
| AV-1–AV-6 applicable planning checks | pass | Assertion Reds/Greens, byte pins, explicit conditional skip, no completed stub claims and source-backed limits. |
| Live final product/mini-air gate | n/a | Execution has not begun; prohibited in this read-only review. |

### Fresh reviewer evidence

Python ran with PYTHONDONTWRITEBYTECODE=1. Git preservation probes used GIT_OPTIONAL_LOCKS=0. Receipts are under C:/Temp/av-kit; decisive output is embedded here.

| Probe | Actual command or observed procedure | Exit | Decisive output |
|---|---|---|---|
| Independent split/selection probe | `rtk proxy python -B C:/Temp/av-kit/e2e-clipboard-specs/review/split-proof.py` | 0 | Five retained blocks equal; intended bytes accepted; changed retained assertion and inverted guard each refused; dev-PC child removes gate variable. |
| Snapshot scratch selftest | `rtk proxy python -B docs/execution/plans/2026-11-20-e2e-clipboard-specs/snapshot-commit.py --selftest C:/Temp/av-kit/e2e-clipboard-specs/review/snapshot-proof-r1` | 0 | `snapshot-commit selftest: 0 failure(s)`; refs/index/status preserved and later mutation refused. |
| Unsplit runner refusal | `rtk proxy python -B docs/execution/plans/2026-11-20-e2e-clipboard-specs/flake-run.py --mode full --runs 1 --no-burn --expect-total 237 --label review-refusal` | 2 | `flake-run: refused before any run: capture-filmstrip-actions.test.ts still calls the system clipboard (Session 57 RULE-4)`; expected refusal, no tests run. |
| Independent pin census | `rtk proxy rg -n 'known-failures|capture-filmstrip-actions|capture-import|run-e2e.ps1|host-facts.ps1|host-status.ps1|capture-system-clipboard' tests/ ui/tests/` | 0 | Direct changed-list assertion at test_e2e_remote.py:1561; host and run-book contracts remain unchanged. |
| Checker selftests | Python runpy invocation of probe-check.main, guard-check.main, pins-check.main and split-specs.main with --selftest; output in ecs-selftests-review.txt; observer codex-independent-reviewer | 0 | Probe 28 cases/0 wrong; guard 8/0; pins 13/0; split 6 cases/ok. |

Reconstructed file identities:

| File | Bytes | SHA-256 |
|---|---|---|
| capture-system-clipboard.test.ts | 23156 | f848f6b48826ed128e197f49753cf09513bfa2a3e0fde7d763a5d4d48635d069 |
| capture-filmstrip-actions.test.ts | 13709 | 026997846ea516bf1e05c03d3beaf2300dd0ce0b101663ba5ae0cb94323f282a |
| capture-import.test.ts | 9166 | e6a28e77c3c2bd617d7a0477e3b776d2a24634830b38432eb420701e8c9d8edb |

```json
{"schema_version": "evidence.v1", "check_id": "ecs-review-split-proof", "command": "rtk proxy python -B C:/Temp/av-kit/e2e-clipboard-specs/review/split-proof.py", "cwd": "P:/av-kit", "scope": "plan-generated split and dev-PC selection", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "b59207b084cfe18e54acdec0799541762f3a67a0;plan=f9a7430f8432765eba801f14001d01db76db4151330fa50a4cb071306bcbc245;task=5175510a4b860bff9e1b71906b500decd491ff37517c2db35dd5f38812852e52", "output": "Five retained test blocks equal; generated files match planned SHA-256 values; changed retained assertion and inverted clipboard guard each refused; split-proof: all independent checks passed", "fresh": true}
```

## Nonblocking correction note

Nonblocking correction: implementation-plan.md:441 says split-specs.py --out refuses existing scratch files, but split-specs.py:503-507 overwrites them. Row 0 already requires a fresh output directory, so this does not defeat acceptance.

## Verdict

`approved` — no evidence-backed High or Critical delivery defect. No blocking correction is required before authorized execution. Preserve the documented probe limits, issue-open fallback and final-tree run requirement. Execution and its independent review remain outstanding.

Reviewed state: `b59207b084cfe18e54acdec0799541762f3a67a0;plan=f9a7430f8432765eba801f14001d01db76db4151330fa50a4cb071306bcbc245;task=5175510a4b860bff9e1b71906b500decd491ff37517c2db35dd5f38812852e52`.
