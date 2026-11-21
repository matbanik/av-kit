---
date: "2026-11-20"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-20-e2e-clipboard-specs/implementation-plan.md"
verdict: "approved"
findings_count: 1
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "ecs-execution-2026-11-20-e2e-clipboard-specs"
round: 2
---

# Critical Review: 2026-11-20-e2e-clipboard-specs

> **Review Mode:** execution
> **Verdict:** approved

## Scope

Session 98, no MEU: the working-tree delta from `b59207b` in the plan's Files Modified scope, its plan-local tooling, records, handoff and specifically cited receipts, with particular attention to everything changed since round 1. Claude Code (Anthropic) authored the work; Codex is the independent reviewer. Applied the execution workflow, IR/PR and AV checks, the materiality rule and adversarial behavior checks. `PLAN` below means `docs/execution/plans/2026-11-20-e2e-clipboard-specs`.

Read the complete round 1 report first. This complete rolling report retains ECS-R1-1 and updates its status and Q answers. The repository remained read only. Reviewer scripts, fixtures, receipts and reports were written only under `C:/Temp/av-kit`. No real spec, Electron app, backend, network command, model or avkit MCP server ran. Launcher fixtures used fake node programs. No forbidden config or real application data was opened. H1 review collection and H2 remain the coordinator's work; this review approves the delivered work without claiming those later rows complete.

**tested_state:** `b59207b084cfe18e54acdec0799541762f3a67a0+ee8411a555a1de80e8f52c1a1c2a779ee0d643dbcb0b11ee7345df759954e839`. This exactly matches both identities of the second H1 gate and the supplied H1-6b identity. There is no identity difference to explain. The sandbox cannot read the global git ignore and additionally lists `.claude/settings.local.json`; `identity.py:93` excludes that path before reading, so it does not affect the result. That file was never opened.

## Intent Anchor

the five capture E2E tests that only share a file with a clipboard test run again in every full run on both hosts, and the two tests that use the system clipboard run on the second Windows host (the mini-air) only when a probe before and after them reads no remote-desktop session; otherwise the run reports them skipped or voided with a named reason. The tests never run on the dev PC. Six parts: 1. **The split** (D-1268, `CLIPBOARD_SPLIT`). `AC-88.12 (a)(b)(f)` (Copy full path and Copy image) leaves `ui/tests/e2e/capture-filmstrip-actions.test.ts` and `AC-132.23` (Ctrl+V paste) leaves `ui/tests/e2e/capture-import.test.ts`; both move, with the helpers only they use, into the new `ui/tests/e2e/capture-system-clipboard.test.ts`. Their bodies keep every byte (only the line ending of the filmstrip lines moves from CRLF to LF). The five others, `AC-88.12 (c)`, `AC-88.12 (d)(e)`, `AC-89.9`, `AC-89.15` and `AC-132.22`, stay where they are, byte for byte. `split-specs.py` builds all three files from the `b59207b` bytes, with a file-level guard after the new file's imports that skips it unless `AVKIT_E2E_CLIPBOARD_GATED=1` (D-1282), and `--check` proves the result. 2. **The dev PC** (D-1276, `CLIPBOARD_NEVER_DEVPC`). The plan-local `flake-run.py` excludes only the new file, and refuses before any run while either old file still calls the clipboard. Its full run has 237 tests in 29 files, the five rejoined ones among them. The new file also guards itself in tracked code: it skips unless `AVKIT_E2E_CLIPBOARD_GATED=1`, which only the mini-air's gated stage sets, so a plain `npm run test:e2e` lists its two tests as skipped and never runs them (D-1282, `guard-check.py`). 3. **The probe** (D-1269 to D-1271, D-1273, `SESSION_PROBE`). One PowerShell block, the same bytes in `host-facts.ps1`, `host-status.ps1` and `run-e2e.ps1`, reads the RustDesk processes' command-line switches, `rdpclip.exe` and `qwinsta`, and returns `none`, `connected` or `undecided` with a named reason. `tools/e2e_remote.py check` prints it as a `session-probe:` line, and each run poll records it. 4. **The gated stage** (D-1271, D-1272, `GATED_STAGE`). `run-e2e.ps1` runs the main specs first, then probes. Only when the probe reads `none` does it run the gated file in `results\<run-id>\gated\`, and it probes again after. The tool reports a `gated` object with one of five outcomes. A gated failure exits 40, apart from the main stage's `new` list. A session that connects during the stage (seen by the after-probe or a poll) voids the result. 5. **The known list and its pin** (D-1272, D-1275). `tools/e2e_host/known-failures.json` drops its two `skip` entries and gains one `gated` entry for the new file. `tests/tooling/test_e2e_remote.py::test_ac_11_known_tracked_list` changes in row 3, which names it. `pins-check.py` proves that no other existing statement of that file changes. 6. **The acceptance run and the registers** (D-1277 to D-1280). One mini-air run (and a second, row 8b, only when the gating probe cannot read the host; D-1280) through `tools/e2e_remote.py run` at the final tree, as a snapshot commit on no ref (`SNAPSHOT_NO_REF`). The main stage has 237 tests, all expected. The gated outcome is a receipt, not a pass condition. Then `E2E-CLIPBOARD-SPECS-UNGATED` is resolved when row 8's `probe-check.py --judge-gate` says resolve (D-1280), `E2E-CLIPBOARD-PRIMER-EMPTY` gets that run's verification and stays open, a new low issue records the two dev-PC specs that also write the clipboard, and grouping row 98 is set.

**Intent achieved: yes.** The six delivered parts achieve the approved goal. ECS-R1-1 is fixed; no new finding blocks approval.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| ECS-R1-1 | High | yes | behavior | A missing or malformed after-probe is accepted as a successful gated run. With a valid `none` before-probe and a passing report, both absent `probe-after.json` and `{}` produce `gated.outcome=run`, `reason=no-remote-session`, `result=ok`, exit 0. This is reachable after a probe-file write failure: the actual copied launcher continued to `DONE 0` when its after-probe destination could not be written. A connection after the last poll can therefore lack its required observation while the tool certifies the clipboard result. Violates AC-7 and GATED_STAGE (`PLAN/implementation-plan.md:186`: `run` requires before, after and every gated poll to read `none`). | `tools/e2e_remote.py:989`; `tools/e2e_remote.py:934`; contributing write handling: `tools/e2e_host/run-e2e.ps1:75` | Whenever the before-probe is `none`, require a present, valid after-probe before returning `run`. Refuse missing evidence with the existing `report-missing` exit 31 and invalid evidence with the existing invalid-report refusal, or otherwise fail closed with the named undecided outcome. Make probe-write failure explicit and add missing/invalid-after and launcher-write-error regressions. | fixed |

## Q1. Goal and acceptance coverage

Accepted: every goal clause has current implementation and matching evidence. The plan's decisions and D-1284 through D-1287 were accepted on the supplied authorization basis and checked for faithful execution. The fix closes the AC-7 gap found in round 1.

| Goal clause | ACs | Decisive observation |
|---|---|---|
| Exact split, helpers and five retained bodies | AC-1, AC-2 | Independent rebuild from `b59207b`: zero differences; three original plan-time hashes match |
| Static validity, five tests restored, dev-PC guard | AC-3, AC-4, AC-20 | Current full gate typecheck/lint pass; both raw full-run receipts contain 237 passes including all five titles; clipboard filename absent; saved Playwright list independently judged 239 listed / two skipped |
| Identical probe, named readings, check and polls | AC-6, AC-8, AC-9, AC-12 | Three identical blocks; PS 5.1 fixture classifier tests pass; real run has before/after `none` and 38 polls recording `none` |
| Five gated outcomes, independent failure accounting | AC-5, AC-7, AC-10 | 211 tooling tests pass; independent missing/invalid-after and launcher-write probes fail closed; connected polls retain precedence |
| Known list, named pin and documentation | AC-5, AC-11, AC-16 | `known=[]`, `skip=[]`, one exact gated entry; zero unauthorized changed statements; run book names both new reasons |
| Snapshot, real acceptance and registers | AC-13 through AC-19 | Nine current blobs match ef4842e; actual reports 237/237 main and 2/2 gated; judge says resolve; records cite rerun with required states |

Not accepted as evidence: the superseded snapshot/run and first H1 gate cannot certify the corrected tree. The rerun and second gate provide that certification. No current goal clause remains unaccepted.

## Q2. Split bytes, helpers and isolation

Accepted: `split-specs.py --check` independently rebuilds from the two baseline blobs and compares complete file bytes, rather than trusting hashes in the handoff (`split-specs.py:316`, `:416`). The moved blocks retain their assertions, waits, fixture state and helpers. Both tests create their own scratch profiles; there are no shared suite hooks lost by moving them. Only the new file of these three calls the system clipboard. The five retained test bodies remain exact.

| File under ui/tests/e2e | Bytes | SHA-256 |
|---|---|---|
| capture-system-clipboard.test.ts | 23156 | f848f6b48826ed128e197f49753cf09513bfa2a3e0fde7d763a5d4d48635d069 |
| capture-filmstrip-actions.test.ts | 13709 | 026997846ea516bf1e05c03d3beaf2300dd0ce0b101663ba5ae0cb94323f282a |
| capture-import.test.ts | 9166 | e6a28e77c3c2bd617d7a0477e3b776d2a24634830b38432eb420701e8c9d8edb |

D-1286's comparison remains exact (`split-specs.py:434`): only the filmstrip baseline is converted into its CRLF checkout representation. An independent scratch-only probe mutated one byte in each old file in turn; both writes refused with result 1, retained every scratch byte and left the new file absent. No repository write mode was invoked. The seven-case selftest passes, including assertion, block, EOL, clipboard-call, guard and existing-output refusals. No split exception or weakening accepted.

## Q3. Dev-PC exclusion and tracked guard

Accepted: `flake-run.py:161` excludes only the new file; `:486` checks both old files for clipboard calls; `:1841` refuses before running. The decisive Red is the clipboard refusal in `ecs-guard-red-1.txt`, not D-1285's earlier argument refusal. The child environment removes the gate variable. The file-level skip at `capture-system-clipboard.test.ts:18` covers npm, plain npx Playwright and older flake-run copies that do not exclude its new filename.

The saved row-2 list was independently judged: 239 tests in 30 files, exactly the two moved tests skipped with the prescribed reason, no execution results. Both raw dev-PC full-run receipts were independently read again: row 7b and the second gate each contain 237 passing lines, all five retained titles once each, and no clipboard filename. No Playwright/list invocation was necessary for this review.

Accepted boundary: the approved guard relies on never manually setting `AVKIT_E2E_CLIPBOARD_GATED` on the dev PC. It is not a host authenticator. The real launcher removes inherited values before main and sets it only for `AvStage -Gated` (`run-e2e.ps1:59`, `:61`, `:255`); the fake launcher tests prove that child-environment separation. No dev-PC gap within that boundary was established.

## Q4. Session probe

Accepted: the probe blocks remain byte-identical, ASCII and LF, and unchanged between the two acceptance snapshots. The independent block check and 28-case checker selftest pass. The 211-test suite includes the actual PS 5.1 classifier fixtures for CIM/read failure, connection-manager switches, RDP, unreadable processes, empty/unknown switches and the service exemption.

At `run-e2e.ps1:177`, the unreadable exemption is anchored to the Win32_Service PID whose own process is in session 0. It covers that PID and direct children only. Readable `--cm` takes precedence; an unreadable grandchild is undecided. This fits the approved RustDesk process model: its server launches the connection manager, rather than the connection manager being the service's direct child. The real before/after observations show exactly the disclosed unreadable service/server plus readable tray. No new false-none or permanently false-connected behavior was demonstrated within that model.

Accepted limits remain sampled observations, stale connection-manager or RDP processes causing conservative skips, English session labels, and RustDesk/RDP-only scope. Those approved decisions were not reopened. The version field can be unavailable without determining session state; process/service/session read failures produce undecided. ECS-R1-1 concerned missing evidence in the result reader, now fixed, rather than a classifier change.

## Q5. Gated stage, known list and preserved tool contracts

Accepted: main runs first and excludes only the skip/gated files. The gated stage runs only after a `none` before-probe, in its own folder, and then probes again. All five outcomes, connected/undecided skips, after/poll voids, connected precedence, gated failure exit 40, separate `gated.new`, main failure accounting and `voided_failures` remain covered by meaningful assertions. A connection before the stage skips it; a connection observed during it voids it.

The corrected reader at `e2e_remote.py:937` treats an absent after-probe as `after-probe-missing` and an invalid state as `after-probe-invalid`. Both give `voided-undecided-during`. `gated_summary` obtains non-JSON evidence through the existing empty-object reader, so it takes the invalid path. A connected gated poll still wins. `AvProbeWrite` now catches a terminating write error and records its filename (`run-e2e.ps1:78`, `:80`). The reviewer independently reproduced a connected after-probe whose destination could not be written: the launcher logged the failure, reached DONE, and the result reader voided the passing gated report. Full recheck observations are below.

Session 96's PINNED_SSH, NAMED_REFUSAL, NEVER_STOP, ONE_LOCK, COMMIT_BOUND, REPORT_ONLY, KNOWN_NAMED and NO_PARTIAL paths retain their existing tests. The change adds no transport bypass, process stop, task start outside the existing operation, or second lock. Main-stage failures remain independent of clipboard skip/void results.

KNOWN_EMPTY holds. `test_ac_11_known_tracked_list:1564` still asserts exact known/skip/gated content and the known-list path; reintroduced known entries or a wrong gated filename fail it. Its change is named in the plan's Test pins and row 3. The row-0 copy equals the HEAD blob; independent AST/source comparison finds no other existing statement changed. The test file's current hash equals D-1284's Red record; the original row-3 record is preserved. No weakened outcome or pin accepted.

## Q6. Acceptance run, snapshot, full gate and records

Accepted: all nine paths in `ecs-snapshot-8.json` match their current clean-filter blob hashes and ef4842e's blobs. The snapshot differs from its parent only at those nine paths. Its saved guards are equal; the current index hash and refs hash equal their saved values; the index is unstaged; HEAD remains `b59207b` on main. No ref contains ef4842e. Its author matches the required noreply identity. No snapshot-building operation ran in this review.

The run `r20261120T230628Z-ef4842e` binds that snapshot. Independently parsed host reports give:

| Stage | Tests | Expected | Unexpected / flaky / skipped | Files |
|---|---|---|---|---|
| Main | 237 | 237 | 0 / 0 / 0 | 29 |
| Gated | 2 | 2 | 0 / 0 / 0 | 1 |

Main `new` and `overlap` are empty; every restored title is expected. Gated outcome is `run`, reason `no-remote-session`. The actual probes read `none` at 23:31:00.8597267Z and 23:31:10.4312973Z. There are 38 polls: 37 main and one gated, all with state `none`. All ten recorded tool/host hashes still match current bytes. The independent judge prints `ungated: resolve (outcome run, reason no-remote-session)`; row 8b was unnecessary.

S13 was followed: the first acceptance receipts were preserved with `-r1`, and row 8 ran once more after the correction. Comparing the two snapshots shows the expected reader, launcher and new regression-test changes. The gate's only round-2 change against `session-gate.ps1.pre-r1fix` is the documented comment and Red-record selection. The original row-3 test hash remains unchanged; the new record equals the current test file. D-1285, D-1286 and D-1287 remain as accepted in round 1.

The original resolve and the verification rewrite receipts both postdate their respective host runs. The resolver reports four changed parsed fields for the rewrite: method and result of the two issues' verification only. Independent parsed comparison with the preserved pre-fix YAML confirms that restriction, no other issue changes, and the unchanged new issue. Both verifications name the rerun and the superseded run under S13. UNGATED remains resolved, PRIMER-EMPTY open, and DEVPC-CLIPBOARD-SPECS open/low. `render --check` passes. The grouping diff changes line 108, row 98 only.

The second H1 gate, stamp `20261120-183646`, contains all 36 completed steps at exit 0 and ends `session-gate: all steps exit 0`. Every step receipt is present and was read; the specified scope skips have their recorded basis. Counts are UI 146 files / 1639 tests, Python 3331 passes, canon 14 passes, plus a fresh 237-pass dev-PC E2E run. D-1287's actual lint argv is preserved. Its before/after identities match the independently calculated current identity exactly. No unchanged full gate was rerun merely to repeat its summary.

## Q7. Safety, scope and evidence fidelity

Accepted: the path inventory stays within the approved tooling/spec/register/docs/plan/closeout scope, apart from the disclosed sandbox-only secret filename, never opened. All 191 product/MCP/native baseline hashes remain unchanged; no changes under packages, mcp-server, ui/src or backend were found. The EOL check reports 19 scope paths and zero problems; the new spec and host scripts retain LF, the filmstrip and other designated files retain CRLF.

LOCAL_HOST_DETAILS is supported by the gate's scanner (`files=32`, `grown_pairs=3`, `bad=0`), the post-fix and handoff scans, the home-path checks and inspection of the changed source/docs. The reviewer did not reopen the forbidden local config to rerun the value-based scanner. No new leaked host value was established, and this report copies no host identity or address. Security conclusions are bounded by that evidence, not a claim to have inspected forbidden files.

The handoff's substantive test counts, named outcomes, hashes, snapshot, register verification and full-gate identity agree with current files and receipts. The actual fixture tests use fake transport and node programs; the moved bodies retain scratch profiles and local test collaborators. No reviewer action ran a spec or reached a network host. No commit, stash, revert, branch, worktree, push or application launch was performed by the reviewer. The current git state and saved snapshot guards support the executor's disclosed no-ref operation.

Not claimed: a live connected-session exercise on the mini-air, a reviewer GUI run, or inspection of secret/global-ignore data. These are the supplied review limits. No safety or fidelity finding remains open.

## Checklist Results

### Information Retrieval (IR) and Design Review (DR)

| Check | Result | Observed procedure | Exit | Evidence |
|---|---|---|---|---|
| Intent and AC mapping | pass | Codex compared plan AC-1 through AC-20, current delta, handoff and cited receipts | null | All six goal parts supported; AC-7 gap fixed |
| Source and decision fidelity | pass | Codex compared D-1284 implementation, preserved gate copy, Red records, snapshots and register copy; retained round-1 accepted D-1285 through D-1287 checks | null | No unauthorized assertion or required scope reduction found |
| Product API/schema/MEU checks | n/a | No product or MEU changes | null | Unchanged product hashes and scope |

### Post-Implementation Review (PR) and adversarial verification

`PY` below is the repository `.venv/Scripts/python.exe`. Reviewer commands used `-B`, `PYTHONDONTWRITEBYTECODE=1`, TMP/TEMP under `C:/Temp/av-kit/e2e-clipboard-specs/exec-review/tmp`, and cleared ELECTRON_RUN_AS_NODE. Process output went through the RTK receipt wrapper with captured exits.

| Check | Result | Observed command | Exit | Decisive output |
|---|---|---|---|---|
| Tooling suite | pass | `rtk proxy uv run --no-sync python -B -m pytest tests/tooling/test_e2e_remote.py -p no:cacheprovider` | 0 | 211 passed in 36.12s; UV_CACHE_DIR under review tmp after default-cache access refusal |
| ECS-R1-1 and controls | pass | `rtk proxy PY -B C:/Temp/av-kit/e2e-clipboard-specs/exec-review/r2-probes.py` | 0 | Four malformed-evidence cases voided; valid-after and skip controls pass; connected poll wins; launcher write failure logged and voided |
| Split, pins, probe, guard, EOL, records and identity | pass | `rtk proxy PY -B C:/Temp/av-kit/e2e-clipboard-specs/exec-review/r2-checks.py` | 0 | All 13 checks exit 0; split 0 problems; pins 0; probe 3 copies; guard 239/2 skipped; render clean; current identity exact |
| One-byte write refusal | pass | `rtk proxy PY -B C:/Temp/av-kit/e2e-clipboard-specs/exec-review/byte-guard.py` | 0 | Both baseline mutations refused with child result 1; scratch bytes unchanged |
| Raw dev-PC run receipts | pass | `rtk proxy PY -B C:/Temp/av-kit/e2e-clipboard-specs/exec-review/devpc-receipts.py` | 0 | Row 7b and second gate each 237 passes, all five titles once, clipboard filename absent |
| Snapshot, host reports and scoped receipts | pass | `rtk proxy PY -B C:/Temp/av-kit/e2e-clipboard-specs/exec-review/r2-audit.py` | 0 | Nine blobs / ten tool hashes match; 237/237 plus 2/2; 191 product hashes unchanged; 36 gate steps at exit 0 |
| S13, registers, refs and Red preservation | pass | `rtk proxy PY -B C:/Temp/av-kit/e2e-clipboard-specs/exec-review/r2-records.py` | 0 | Only the two verifications rewritten; row 98 only; current refs equal guard; original Red preserved, fix Red matches |

The first uv attempt exited 2 because the default cache was sandbox-denied; its successful retry used a temp-local cache. The reviewer records probe initially used Windows' default text decoding for a UTF-8 grouping file; specifying UTF-8 corrected that reviewer probe and confirmed the one-line delta. Neither observation is an implementation failure or omitted check.

Test rigor: the moved and retained E2E assertions remain **Strong** for their existing contracts. New fake-host integration and PS launcher tests are **Strong**: they exercise actual orchestration with fake transport/node and assert exact outcomes, counts, exits, cleanup and named errors. D-1284's three regression functions expand to six pytest cases. Their Red receipt has six assertion failures, not setup failures; Green has 211 passes; the test hash is unchanged since that Red. The reviewer separately used passing gated reports for the four missing/invalid-after cases, complementing the shipped failing-report regressions. AV-1 through AV-6 show no assertion bypass, untracked deferral, required placeholder or unsourced behavior.

```json
{"schema_version":"evidence.v1","check_id":"ecs-r2-after-probe","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/e2e-clipboard-specs/exec-review/r2-probes.py","cwd":"P:/av-kit","scope":"GATED_STAGE result reader and copied launcher, fake transport/node only","phase":"targeted","exit_code":0,"result":"pass","tested_state":"b59207b084cfe18e54acdec0799541762f3a67a0+ee8411a555a1de80e8f52c1a1c2a779ee0d643dbcb0b11ee7345df759954e839","output":"With none before and a passing two-test report: absent after -> voided-undecided-during/after-probe-missing; {}, non-JSON and unknown state -> voided-undecided-during/after-probe-invalid. Valid none after -> run/no-remote-session. Connected gated polls win for missing, invalid and none after. Connected/undecided before skips unchanged. Copied launcher failed to write a connected after-probe, logged probe-write-failed probe-after.json, reached DONE 0, and the reader voided its passing report.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"ecs-r2-tooling-suite","command":"rtk proxy uv run --no-sync python -B -m pytest tests/tooling/test_e2e_remote.py -p no:cacheprovider","cwd":"P:/av-kit","scope":"remote-run tooling suite with fake transport and Windows PowerShell fixture roots; UV_CACHE_DIR under reviewer tmp","phase":"targeted","exit_code":0,"result":"pass","tested_state":"b59207b084cfe18e54acdec0799541762f3a67a0+ee8411a555a1de80e8f52c1a1c2a779ee0d643dbcb0b11ee7345df759954e839","output":"211 collected; 211 passed in 36.12s; no skipped tests.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"ecs-r2-final-state-audit","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/e2e-clipboard-specs/exec-review/r2-audit.py","cwd":"P:/av-kit","scope":"snapshot blobs, current hashes, actual acceptance reports and each named full-gate receipt","phase":"targeted","exit_code":0,"result":"pass","tested_state":"b59207b084cfe18e54acdec0799541762f3a67a0+ee8411a555a1de80e8f52c1a1c2a779ee0d643dbcb0b11ee7345df759954e839","output":"Snapshot paths 9, mismatches []; guards equal and index equal now; no containing ref; HEAD b59207b on main, staged paths []. Actual main 237 expected, 29 files; all five retained titles expected. Actual gated 2 expected, outcome run/no-remote-session; both probes none. Ten tool hashes match; 38 none polls. 191 product hashes unchanged. Full gate stamp 20261120-183646: 36 completed steps, all exit 0; before/after identities equal current tested_state.","fresh":true}
```

## Verdict

`approved` — ECS-R1-1 is fixed and no new substantive finding remains. The implementation achieves the registered intent. The coordinator can collect this verdict, complete H2 and proceed with the already authorized commit; this review performs neither commit nor push.

## Recheck (round 2)

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| ECS-R1-1 | open | fixed |

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

### Confirmed Fixes

- `e2e_remote.py:937` through the new missing/invalid branches prevents `run` without a valid after state; gated connected polls still take precedence.
- `run-e2e.ps1:78` and `:80` catch and log the write failure; the independent copied-launcher failure reaches the reader's void path.
- The run book names both reasons; the additional tests were Red first and retain their recorded hash.
- S13 preserves the first run, binds the final nine files to ef4842e and supplies a fresh real-host rerun. The gate uses the new Red record without rewriting the old one. Both issue verifications now cite the rerun.

### Independent recheck probes

| Input with none before and two expected gated tests | Observed outcome | Named reason |
|---|---|---|
| Missing after file | voided-undecided-during | after-probe-missing |
| Empty object | voided-undecided-during | after-probe-invalid |
| Non-JSON after file | voided-undecided-during | after-probe-invalid |
| Unknown after state | voided-undecided-during | after-probe-invalid |
| Valid none after | run | no-remote-session |
| Connected gated poll plus missing/invalid/none after | voided-connected-during | connected-rdp |
| Launcher cannot write connected after-probe | voided-undecided-during | after-probe-missing |

Every row was observed with reviewer fixtures and assertions, command exit 0. No real clipboard test ran.

### Recheck Verdict

`approved` — prior finding fixed, zero new findings, intent achieved.

## Residual Risks and Limits

Sampled probes can miss a brief connection, stale connection processes can conservatively skip later stages, and a void cannot undo clipboard writes already made. Detection is limited to the approved RustDesk/RDP model. The real host was idle; connected, undecided and void cases are proved by fake-host fixtures. PRIMER-EMPTY remains open for repeated gated verification, and the other dev-PC clipboard writers remain recorded in their separate low issue. These approved limits were preserved, without treating the superseded run as final-state evidence.
